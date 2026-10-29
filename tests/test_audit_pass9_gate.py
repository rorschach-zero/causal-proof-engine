"""Whole-codebase audit, pass 9 (issue #37), at ``811ba9d6bd13996cec72da62c0179d1baf71c6f2``: gate replay reads no
reading below a wall time the ledger persisted before it.

P9-2 (class W; found by invariant 5 of PR #100): replay judged an intent's and a commit's reading by its boot
identifier and its drift from the epoch baseline only (pass 8 Codex 8-2). The protected operation takes no step on a
reading below the latest wall time a persisted reading observed, nor below a receipt the ledger holds: it refuses
``clock_rollback`` (RC-37, RC-65; ``17`` item 2 "Clock"). A commit appended raw with the epoch's start reading, below its
own intent's reading, was read and conferred its level. Replay now refuses a gate record of any kind whose reading is
below the latest persisted reading or the latest receipt before it. A raw row with a fresh, plausible reading cannot be
told from the gate's own; this closes the reading that is provably not the gate's.

Each test named p9_2 or p9_3 fails at the pin; the test named 4418866225 fails at the head of PR #102 (55f9d9a), whose
replay rule a rotation carrying an earlier reading broke. PR #102 was closed unmerged and is superseded here."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cpe.capability import CapabilityGate, ManualTimeSource, replay_gate
from cpe.capability.records import KIND_CHECK, KIND_COMMIT, CheckRecord, CommitRecord, gate_ledger_id
from cpe.capability.timesource import ClockReading
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from tests.test_capability import BASE, ENV, OWNER, RELEASE, RULES, TOLERANCE, Rig, issue


def killed() -> None:
    raise RuntimeError("the gate stops after its intent anchor")


def intent_left_pending(rig: Rig) -> str:
    rig.tick()
    rig.gate.hooks["after_intent_anchor"] = killed
    with pytest.raises(RuntimeError):
        rig.promote(issue(rig.epoch(), "a"))
    (intent_id,) = rig.gate.state().intents
    return intent_id


def test_p9_2_a_commit_read_below_its_intent_confers_no_level(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    intent_id = intent_left_pending(rig)
    state = rig.gate.state()
    stale = state.baseline  # the epoch's start reading, a second before the intent's
    assert stale is not None and stale.wall < state.intents[intent_id].reading.wall
    anchor = rig.ledger.local_anchors()[-1]
    rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent_id),
                      CommitRecord(intent_id, anchor.prefix_length, anchor.digest, stale).to_payload())
    rig.ledger.anchor()
    rig.tick()
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("sim_read")  # at 811ba9d: admitted at SIM_READ_ONLY
    assert refused.value.reason == "invalid_gate_ledger" and "read below a wall time" in refused.value.detail


def test_p9_2_a_reading_below_an_earlier_receipt_is_refused_on_replay(tmp_path: Path) -> None:
    """A check whose reading is below the receipt of the record before it: the ledger clock was already past it."""
    rig = Rig(tmp_path)
    rig.tick()
    rig.gate.perform("research")
    records = rig.ledger.records()
    behind = ClockReading(rig.clock.now().replace(year=2025), 0.0, rig.time.boot_id())
    rig.ledger.append(KIND_CHECK, gate_ledger_id("gate-check", records[-1].entry_hash),
                      CheckRecord("action:research", "admitted", "", behind).to_payload())
    anchors = rig.ledger.local_anchors()
    with pytest.raises(Refusal) as refused:
        replay_gate(rig.ledger.records(), max(a.prefix_length for a in anchors), RULES, anchors)
    assert refused.value.reason == "invalid_gate_ledger"


def test_a_commit_with_its_own_fresh_reading_is_read_as_before(tmp_path: Path) -> None:
    """The reading another gate takes at its own commit is at or above every bound: replay reads it (the H2 cases)."""
    rig = Rig(tmp_path)
    intent_id = intent_left_pending(rig)
    anchor = rig.ledger.local_anchors()[-1]
    fresh = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())
    rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent_id),
                      CommitRecord(intent_id, anchor.prefix_length, anchor.digest, fresh).to_payload())
    rig.ledger.anchor()
    assert rig.gate.state().level == "SIM_READ_ONLY"


def test_4418866225_a_rotation_after_another_gates_write_leaves_a_readable_ledger(tmp_path: Path) -> None:
    """PR #102 review 4418866225 (P1, a regression of #102): a discontinuity rotation carried the reading that showed
    it as its baseline. When another gate wrote between that reading and the rotation's append, the epoch's baseline
    lay below the other gate's record, and replay under P9-2 refused the ledger every gate had written. The rotation
    now reads its own baseline against the chain head it is appended on."""
    rig = Rig(tmp_path)
    other = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)  # a second gate on the ledger
    rig.tick()
    read_boot = rig.time.boot_id
    reads = 0

    def boot_id() -> str:  # the first gate reads a new boot id; before its rotation lands, the other gate demotes
        nonlocal reads
        reads += 1
        if reads == 1:
            rig.tick()
            other.demote("operator")
            rig.time.reboot("boot-2", monotonic=rig.time.monotonic())
        return read_boot()

    rig.time.boot_id = boot_id  # type: ignore[method-assign]
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("research")
    assert refused.value.reason == "clock_discontinuity"
    assert rig.gate.state().baseline.boot_id == "boot-2"  # type: ignore[union-attr]  # at 55f9d9a: invalid_gate_ledger
    CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)  # a restart reads it too


class Scripted(ManualClock):
    """A manual clock whose next readings are taken from ``script``, then its own time again."""

    def __init__(self, start: datetime) -> None:
        super().__init__(start)
        self.script: list[datetime] = []

    def now(self) -> datetime:
        return self.script.pop(0) if self.script else super().now()


def test_p9_3_a_discontinuity_rotation_keeps_only_a_bound_its_record_carries(tmp_path: Path) -> None:
    """P9-3 (found by a line-by-line reviewer of pass 9): the rotation appended with ``observed = max(now,
    baseline.wall)`` while its record persisted the carried baseline only, so after a clock step back between the
    rotation's own sample (t0 + 10 s) and its append (received at t0 + 1 s) the writer refused t0 + 5 s and a restore of
    the complete export admitted it. The baseline is now the rotation's own sample, which the record carries."""
    clock = Scripted(BASE)
    time = ManualTimeSource(clock)
    store = HarnessAnchorStore()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    gate = CapabilityGate(ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    time.advance(timedelta(seconds=1))
    t0 = clock.now()
    time.reboot("boot-2")
    clock.script = [t0, t0 + timedelta(seconds=10), t0 + timedelta(seconds=1)]  # perform; the rotation; its append
    with pytest.raises(Refusal) as refused:
        gate.perform("research")
    assert refused.value.reason == "clock_discontinuity"
    clock.set(t0 + timedelta(seconds=5))
    restored, report = Ledger.restore(tmp_path / "restored.sqlite", clock, records_from_jsonl(ledger.export_jsonl()),
                                      store)
    assert report.intact
    for each in (ledger, restored):  # at 811ba9d the writer refused t0 + 5 s and the restore admitted it
        with pytest.raises(Refusal) as rolled_back:
            each.now()
        assert rolled_back.value.reason == "clock_rollback"
