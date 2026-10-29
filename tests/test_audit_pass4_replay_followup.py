"""Whole-codebase audit, pass 4 (issue #37): the findings of the Codex review of PR #51.

- ``4353051497`` (P1): a commit citing its intent's own sequence and entry hash, with no intent anchor ever
  published, was accepted on replay as step 2; anchoring the completed prefix then made a validly signed promotion
  effective without the four-step protocol (RC-153, RC-158).
- ``4353051510`` (P2; duplicated as ``4353051516``): replay checked every historical intent against the running
  release, so a gate started under a new release could not replay a ledger an earlier release had promoted.
- ``4353051504`` (P2): a raw refused-round row for a round the register's anchor preceded was accepted on replay,
  and its calibration could never draw a seed.

The three ``test_49*`` tests failed on the head of PR #51, ``52acf5ae592c2dfca9c98cd18fa61ae31ff3d7a3``."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest

from cpe.capability import CapabilityGate
from cpe.capability.records import KIND_COMMIT, KIND_EPOCH, KIND_INTENT, CommitRecord, EpochRecord, IntentRecord
from cpe.capability.records import intent_ledger_id
from cpe.capability.timesource import ClockReading
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.registration import BeaconOutput, ConfirmatoryRegister, RegistrationRegistry
from cpe.registration.registry import KIND_ROUND_REFUSED, _ledger_id
from tests.test_audit_pass3_claim_status import calibrated
from tests.test_capability import ENV, EVIDENCE, OWNER, RELEASE, TOLERANCE, Rig, issue
from tests.test_registration import clock, day, ledger, registry  # noqa: F401
from tests.test_schemas import HEX

NEW_RELEASE = "cd" * 32


def reading_of(rig: Rig) -> ClockReading:
    return ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())


def test_4353051497_a_commit_must_cite_a_published_anchor(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    capability = issue(rig.epoch(), "unanchored", level="SIM_EXECUTION")  # validly signed by the owner
    intent_id = intent_ledger_id(capability)
    intent = rig.ledger.append(KIND_INTENT, intent_id,
                               IntentRecord(intent_id, capability, "SIM_EXECUTION", reading_of(rig)).to_payload())
    rig.ledger.append(KIND_COMMIT, "commit", CommitRecord(intent_id, intent.seq, intent.entry_hash,
                                                          reading_of(rig)).to_payload())
    rig.ledger.anchor()  # only the completed prefix is anchored; step 2 never happened
    rig.tick()
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("sim_execution")  # at 52acf5a: admitted
    assert refused.value.reason == "invalid_gate_ledger"


def test_4353051510_a_new_release_replays_what_an_earlier_one_promoted(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    assert rig.promote(issue(rig.epoch(), "before")).status == "acknowledged"
    rig.tick()
    upgraded = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, NEW_RELEASE, TOLERANCE)  # at 52acf5a: refused
    rig.gate = upgraded
    assert upgraded.state().level == "RESEARCH_ONLY"  # the start rotation puts the new release at the floor
    upgraded.anchor_epoch()
    rig.tick()
    with pytest.raises(Refusal) as refused:  # the running release applies to every new presentation
        rig.promote(issue(rig.epoch(), "old-release"))
    assert refused.value.reason == "wrong_release"
    rig.tick()
    current = issue(rig.epoch(), "new-release")
    unsigned = replace(current, release_digest=NEW_RELEASE, signature="unsigned")
    signed = replace(unsigned, signature=OWNER.sign(unsigned.signed_bytes()))
    assert rig.promote(signed).status == "acknowledged"
    assert rig.gate.state().level == "SIM_READ_ONLY"


def test_an_epoch_recorded_without_its_release_replays_under_the_running_one(tmp_path: Path) -> None:
    """Epochs written before the release was recorded carry none; their intents are checked as before."""
    rig = Rig(tmp_path)
    epoch = EpochRecord(7, rig.gate.state().epoch_index + 1, "start", reading_of(rig))
    assert "release_digest" not in epoch.to_payload()
    assert EpochRecord.from_payload(epoch.to_payload()) == epoch
    with pytest.raises(Refusal):
        EpochRecord.from_payload({**epoch.to_payload(), "release_digest": "not-a-digest"})
    rig.ledger.append(KIND_EPOCH, "legacy-epoch", epoch.to_payload())
    assert rig.gate.state().epoch == 7 and rig.gate.state().epoch_release is None


@pytest.mark.parametrize("reason, published", [("register_not_anchored", 12), ("chosen", 10.5)])
def test_4353051504_a_refused_round_row_must_be_one_the_registry_writes(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock, reason: str, published: float) -> None:
    calibrated(registry, ledger, clock)  # cal-1 anchored at day 11
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(11.5))
    ledger.anchor()  # the register is anchored at day 11.5
    clock.set(day(13))
    output = BeaconOutput("cal-1", "beacon", "round-7", HEX, day(published))
    ledger.append(KIND_ROUND_REFUSED, _ledger_id("round-refused", "cal-1"),
                  {"output": output.to_payload(), "reason": reason})
    with pytest.raises(Refusal) as refused:
        registry.claim_status("claim-1")  # at 52acf5a: "exploratory", and no seed ever
    assert refused.value.reason == "invalid_record"


def test_a_round_refused_by_the_registry_still_replays(registry: RegistrationRegistry, ledger: Ledger,
                                                       clock: ManualClock) -> None:
    calibrated(registry, ledger, clock)
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(13))
    ledger.anchor()
    clock.set(day(14) + timedelta(hours=1))
    with pytest.raises(Refusal):
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    clock.set(day(15))
    ledger.anchor()
    assert registry.claim_status("claim-1") == "exploratory"
