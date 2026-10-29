"""Whole-codebase audit, pass 8 (issue #37), at ``c37d04899c3f0c821825f7aee09ff79c900eb02a``: replay of an intent or a
commit checks its clock reading against the epoch's baseline.

Codex 8-2 (PR #87 review comment 4417203540, class W): the protected operation takes no step on a reading that breaks
continuity with the epoch's baseline (another boot identifier, or a wall-minus-monotonic offset drifted beyond the slew
tolerance): ``_reading`` rotates the epoch instead (RC-73, RC-100). Replay did not check it, so an intent appended
through the ledger under another boot, anchored with its otherwise valid commit, conferred its level. Each epoch now
records the tolerance it was judged by, and replay refuses an intent or a commit whose reading is not continuous with
its epoch's baseline; an epoch written before the tolerance was recorded is checked by boot identifier only.

The first three tests failed at the pass-8 pin; the fourth guards the epochs written before; the fifth is the regression
PR #92's review found (4417733808), which this PR, its successor, fixes: the live gate judges continuity by the epoch's
recorded tolerance, as replay does."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from cpe.capability.records import (
    KIND_COMMIT,
    KIND_EPOCH,
    KIND_INTENT,
    CommitRecord,
    EpochRecord,
    IntentRecord,
    epoch_ledger_id,
    gate_ledger_id,
    intent_ledger_id,
)
from cpe.capability import CapabilityGate
from cpe.capability.state import replay_gate
from cpe.capability.timesource import ClockReading
from cpe.errors import Refusal
from tests.test_capability import ENV, EVIDENCE, OWNER, RELEASE, RULES, Rig, issue


def reading(rig: Rig, boot_id: str | None = None, monotonic_shift: float = 0.0) -> ClockReading:
    return ClockReading(rig.clock.now(), rig.time.monotonic() + monotonic_shift, boot_id or rig.time.boot_id())


def raw_promotion(rig: Rig, intent_reading: ClockReading, commit_reading: ClockReading | None = None) -> None:
    """An intent and its commit as the protected operation writes them, but for their readings, each anchored."""
    capability = issue(rig.epoch(), "raw")
    intent_id = intent_ledger_id(capability)
    rig.ledger.append(KIND_INTENT, intent_id, IntentRecord(intent_id, capability, "SIM_READ_ONLY",
                                                           intent_reading).to_payload())
    anchor = rig.ledger.anchor()
    rig.tick()
    rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent_id),
                      CommitRecord(intent_id, anchor.prefix_length, anchor.digest,
                                   commit_reading or reading(rig)).to_payload())
    rig.ledger.anchor()


def refusal(rig: Rig) -> Refusal:
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("sim_read")  # at c37d048: admitted at SIM_READ_ONLY
    return refused.value


def test_codex8_2_an_intent_read_under_another_boot_confers_no_level(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    raw_promotion(rig, reading(rig, boot_id="another-boot"))
    refused = refusal(rig)
    assert refused.reason == "invalid_gate_ledger" and "boot id another-boot" in refused.detail


def test_codex8_2_an_intent_read_after_a_drift_beyond_the_tolerance_confers_no_level(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    raw_promotion(rig, reading(rig, monotonic_shift=5.0))  # the offset drifted by 5 s (tolerance 1 s)
    refused = refusal(rig)
    assert refused.reason == "invalid_gate_ledger" and "beyond the epoch's tolerance" in refused.detail


def test_codex8_2_a_commit_read_under_another_boot_confers_no_level(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    raw_promotion(rig, reading(rig), commit_reading=reading(rig, boot_id="another-boot"))
    refused = refusal(rig)
    assert refused.reason == "invalid_gate_ledger" and "commit of" in refused.detail


def test_an_epoch_written_before_the_tolerance_was_recorded_is_checked_by_boot_only(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    epochs = [EpochRecord.from_payload(r.payload) for r in rig.ledger.records() if r.kind == KIND_EPOCH]
    assert epochs[-1].tolerance == 1.0  # recorded with the rotation
    legacy = EpochRecord(77, epochs[-1].index + 1, "start", reading(rig), RELEASE)  # as written before pass 8
    rig.ledger.append(KIND_EPOCH, epoch_ledger_id(legacy.index, legacy.epoch), legacy.to_payload())
    rig.ledger.anchor()
    rig.tick()
    capability = issue(77, "legacy")
    intent_id = intent_ledger_id(capability)
    drifted = reading(rig, monotonic_shift=5.0)
    rig.ledger.append(KIND_INTENT, intent_id, IntentRecord(intent_id, capability, "SIM_READ_ONLY", drifted).to_payload())
    anchors = rig.ledger.local_anchors()
    assert intent_id in replay_gate(rig.ledger.records(), anchors[-1].prefix_length, RULES, anchors).intents
    other = IntentRecord(intent_ledger_id(issue(77, "other")), issue(77, "other"), "SIM_READ_ONLY",
                         reading(rig, boot_id="another-boot"))
    rig.ledger.append(KIND_INTENT, other.intent_id, other.to_payload())
    with pytest.raises(Refusal) as refused:
        replay_gate(rig.ledger.records(), anchors[-1].prefix_length, RULES, anchors)
    assert "boot id another-boot" in refused.value.detail


def test_a_gate_judges_continuity_by_the_tolerance_its_epoch_recorded(tmp_path: Path) -> None:
    """PR #92 review 4417733808 (P1, a regression of #92): with replay checking the epoch's recorded tolerance and the
    live gate its own, a lenient gate on a ledger whose epoch a strict gate opened wrote an intent that replay refused,
    and every gate on the ledger refused every step from then on, a restart included. The live gate now judges by the
    epoch's tolerance: the slewed promotion is refused as a discontinuity, and the ledger stays readable."""
    rig = Rig(tmp_path)  # tolerance 1 s
    lenient = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, 10.0)
    strict = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, 1.0)  # opens the current epoch
    rig.time.advance(timedelta(seconds=1), slew=timedelta(seconds=2))
    with pytest.raises(Refusal) as refused:
        lenient.promote(issue(strict.state().epoch, "slewed"), EVIDENCE)  # at ce902ba: invalid_gate_ledger
    assert refused.value.reason == "clock_discontinuity"
    assert strict.state().level == "RESEARCH_ONLY"  # the ledger reads
    lenient.demote("after the slew")
