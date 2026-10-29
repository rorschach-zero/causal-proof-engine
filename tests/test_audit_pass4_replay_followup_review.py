"""Whole-codebase audit, pass 4 (issue #37): the findings of the Codex review of PR #59, the first follow-up of #51,
which was superseded rather than merged.

- ``4353380374`` (P1, a regression of #59): a gate of an earlier release still running after a later release rotated
  the shared ledger replayed the later release's intent and acted at its level, holding no capability for its own
  release.
- ``4353380367`` (P1): an anchor of the intent's prefix published after the commit, then restored into the local
  anchors, was accepted as step 2.
- ``4353380358`` (P2): a refused-round row written under ``main``'s R1 behaviour made the ledger unreadable once the
  pending register anchor settled; with the corrected R1 the row is never written.
- ``4353380381`` (P2): gate state read the anchors and the records in two calls, so a concurrent promotion made
  replay refuse a valid ledger.

The tests failed on the head of PR #59, ``f2f447d57c86db9a8e55b1d73060c351a1a36012``."""
from __future__ import annotations

import threading
from dataclasses import replace
from pathlib import Path

import pytest

from cpe.capability import CapabilityGate
from cpe.capability.records import KIND_COMMIT, KIND_INTENT, CommitRecord, IntentRecord, intent_ledger_id
from cpe.capability.timesource import ClockReading
from cpe.clock import ManualClock, format_timestamp
from cpe.errors import Refusal
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger, Record
from cpe.ledger.store import records_from_jsonl
from cpe.registration import BeaconOutput, CalibrationRecord, ConfirmatoryRegister, RegistrationRegistry
from tests.test_audit_pass3_claim_status import claim
from tests.test_capability import ENV, EVIDENCE, OWNER, RELEASE, TOLERANCE, Rig, issue
from tests.test_registration import day
from tests.test_schemas import HEX

NEW_RELEASE = "cd" * 32


def test_4353380374_a_gate_of_an_earlier_release_acts_on_nothing(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    old = rig.gate
    new = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, NEW_RELEASE, TOLERANCE)
    new.anchor_epoch()
    rig.tick()
    capability = replace(issue(new.state().epoch, "new", level="SIM_EXECUTION"), release_digest=NEW_RELEASE)
    capability = replace(capability, signature=OWNER.sign(capability.signed_bytes()))
    assert new.promote(capability, EVIDENCE).status == "acknowledged"
    rig.tick()
    with pytest.raises(Refusal) as refused:
        old.perform("sim_execution")  # at f2f447d: admitted
    assert refused.value.reason == "stale_release"
    with pytest.raises(Refusal) as presented:  # nor may it consume a capability for its own release
        old.promote(issue(new.state().epoch, "old"), EVIDENCE)
    assert presented.value.reason == "stale_release"
    assert new.state().level == "SIM_EXECUTION"  # the ledger stays readable


def test_4353380367_an_intent_anchor_published_after_the_commit_is_not_step_2(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    capability = issue(rig.epoch(), "late-anchor", level="SIM_EXECUTION")
    reading = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())
    intent_id = intent_ledger_id(capability)
    intent = rig.ledger.append(KIND_INTENT, intent_id,
                               IntentRecord(intent_id, capability, "SIM_EXECUTION", reading).to_payload())
    rig.ledger.append(KIND_COMMIT, "commit", CommitRecord(intent_id, intent.seq, intent.entry_hash, reading).to_payload())
    rig.tick()  # an anchor of the intent's prefix, published after the commit was received
    rig.store.inner.publish(Anchor(intent.seq, intent.entry_hash, format_timestamp(rig.ledger.now())))
    rig.ledger.anchor()
    records = records_from_jsonl(rig.ledger.export_jsonl())
    rig.ledger.close()
    rig.tick()
    restored, report = Ledger.restore(tmp_path / "restored.sqlite", rig.clock, records, rig.store)
    assert report.intact
    with pytest.raises(Refusal) as refused:
        CapabilityGate(restored, OWNER, rig.time, ENV, RELEASE, TOLERANCE)  # at f2f447d: the commit is effective
    assert refused.value.reason == "invalid_gate_ledger"


class AcknowledgementLost(HarnessAnchorStore):
    def __init__(self) -> None:
        super().__init__()
        self.fail_next = False

    def publish(self, anchor: Anchor) -> None:
        super().publish(anchor)
        if self.fail_next:
            self.fail_next = False
            raise Refusal("anchor_store_unavailable", "the acknowledgement was lost")


def test_4353380358_a_settling_register_anchor_never_makes_the_ledger_unreadable(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    store = AcknowledgementLost()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    registry = RegistrationRegistry(ledger)
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    clock.set(day(10))
    ledger.anchor()
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(11))
    store.fail_next = True
    with pytest.raises(Refusal):
        ledger.anchor()  # held by the store at day 11, pending locally
    clock.set(day(13))
    with pytest.raises(Refusal):
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    ledger.close()
    clock.set(day(14))
    reopened = Ledger(tmp_path / "l.sqlite", clock, store)  # reconciliation settles the anchor at day 11
    assert RegistrationRegistry(reopened).claim_status("claim-1") == "confirmatory"  # at f2f447d: invalid_record


def test_4353380381_a_concurrent_promotion_never_makes_replay_refuse(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    other = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)
    other.anchor_epoch()
    rig.tick()
    epoch = other.state().epoch
    original = rig.ledger._local_anchors_locked
    original_records = rig.ledger.records
    promoted: list[object] = []
    writer = threading.Thread(target=lambda: promoted.append(other.promote(issue(epoch, "c"), EVIDENCE)))

    def promote_concurrently() -> tuple[Anchor, ...]:
        anchors = original()
        rig.ledger._local_anchors_locked = original  # type: ignore[method-assign]
        writer.start()  # another gate promotes; it needs the ledger's lock
        return anchors

    def records_after_the_promotion() -> tuple[Record, ...]:
        writer.join()  # a separate read of the records sees the promotion the anchors read did not
        rig.ledger.records = original_records  # type: ignore[method-assign]
        return original_records()

    rig.ledger._local_anchors_locked = promote_concurrently  # type: ignore[method-assign]
    rig.ledger.records = records_after_the_promotion  # type: ignore[method-assign]
    rig.gate.state()  # at f2f447d: invalid_gate_ledger, the commit seen without its anchor
    writer.join()
    rig.ledger.records = original_records  # type: ignore[method-assign]
    assert promoted and rig.gate.state().level == "SIM_READ_ONLY"
