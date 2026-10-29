"""Mutation testing, ``cpe/capability``: tests that kill mutants the suite let survive at ac4c640 (``research/19``
section "Mutation testing"). They pin the gate's audit records (verdict, subject, epoch reason), the reason code of
every refusal, the boundaries of expiry and slew, the replay of a malformed gate ledger and the time sources."""
from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from cpe.capability import CapabilityGate, HostTimeSource, ManualTimeSource, replay_gate
from cpe.capability.levels import permits, promotion_target, rank
from cpe.capability.records import (
    KIND_ABORT,
    KIND_CHECK,
    KIND_COMMIT,
    KIND_EPOCH,
    KIND_INTENT,
    AbortRecord,
    CheckRecord,
    CommitRecord,
    EpochRecord,
    IntentRecord,
    intent_ledger_id,
)
from cpe.capability.timesource import ClockReading
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger, Record
from cpe.ledger.anchor import UnavailableAnchorStore
from tests.test_capability import BASE, ENV, OWNER, RELEASE, RULES, TOLERANCE, Rig, issue
from tests.test_review_round2_pr25 import PausingTimeSource


@pytest.fixture
def rig(tmp_path: Path) -> Rig:
    return Rig(tmp_path)


def payloads(rig: Rig, kind: str) -> list[dict[str, Any]]:
    out = []
    for record in rig.ledger.records():
        if record.kind == kind:
            assert isinstance(record.payload, dict)
            out.append(record.payload)
    return out


def reason_of(call: Callable[[], object]) -> str:
    with pytest.raises(Refusal) as refused:
        call()
    return refused.value.reason


# records and levels ----------------------------------------------------------------------------------------------

def test_every_gate_record_round_trips_through_its_payload() -> None:
    reading = ClockReading(BASE, 12.5, "boot-1")
    capability = issue(7, "n-1")
    for record in (EpochRecord(7, 1, "start", reading), IntentRecord("i-1", capability, "SIM_READ_ONLY", reading),
                   AbortRecord("i-1", "aborted at process start", reading), CommitRecord("i-1", 3, "ab" * 32, reading),
                   CheckRecord("action:research", "refused", "level_insufficient", reading)):
        assert type(record).from_payload(record.to_payload()) == record
    assert CheckRecord("s", "admitted", "", reading).to_payload() == {
        "subject": "s", "verdict": "admitted", "reason": "", "reading": reading.to_payload()}
    assert reason_of(lambda: EpochRecord.from_payload({**EpochRecord(7, 1, "start", reading).to_payload(), "index": 0})) \
        == "invalid_epoch"


def test_level_refusals_are_named() -> None:
    assert reason_of(lambda: rank("ROOT")) == "unknown_level"
    assert reason_of(lambda: permits("RESEARCH_ONLY", "trade")) == "unknown_action"
    assert reason_of(lambda: promotion_target("demote:RESEARCH_ONLY")) == "unknown_action"


# time sources ----------------------------------------------------------------------------------------------------

def test_a_reboot_resets_the_monotonic_clock_to_zero_by_default() -> None:
    source = ManualTimeSource(ManualClock(BASE), monotonic=50.0)
    source.reboot("boot-2")
    assert (source.monotonic(), source.boot_id()) == (0.0, "boot-2")


def test_the_host_time_source_reads_the_kernel_boot_id_or_falls_back(monkeypatch: pytest.MonkeyPatch,
                                                                     tmp_path: Path) -> None:
    boot = tmp_path / "boot_id"
    boot.write_text("1234-abcd\n", encoding="ascii")
    monkeypatch.setattr(HostTimeSource, "_BOOT_ID_PATH", boot)
    host = HostTimeSource()
    assert host.boot_id() == "1234-abcd"
    first = host.monotonic()
    assert isinstance(first, float) and host.monotonic() >= first
    monkeypatch.setattr(HostTimeSource, "_BOOT_ID_PATH", tmp_path / "absent")
    fallback = HostTimeSource().boot_id()
    assert str(uuid.UUID(fallback)) == fallback  # a UUID stands in for the kernel's id
    boot.write_text("", encoding="ascii")
    monkeypatch.setattr(HostTimeSource, "_BOOT_ID_PATH", boot)
    assert len(HostTimeSource().boot_id()) == 36  # an empty kernel id falls back as well


# the gate's audit records -------------------------------------------------------------------------------------------

def test_the_audit_records_carry_verdict_subject_and_epoch_reason(rig: Rig) -> None:
    rig.tick()
    rig.gate.perform("research")
    with pytest.raises(Refusal):
        rig.gate.perform("sim_read")
    checks = payloads(rig, KIND_CHECK)
    assert [(c["subject"], c["verdict"], c["reason"]) for c in checks] == [
        ("action:research", "admitted", ""), ("action:sim_read", "refused", "level_insufficient")]
    rig.tick()
    outcome = rig.promote(issue(rig.epoch(), "p", level="SIM_READ_ONLY"))
    assert (outcome.status, outcome.level) == ("acknowledged", "SIM_READ_ONLY")
    assert outcome.commit_anchor == rig.ledger.local_anchors()[-1] and outcome.intent_id in rig.gate.state().effective
    assert [(c["subject"], c["verdict"], c["reason"]) for c in payloads(rig, KIND_CHECK)][-1] == ("acknowledgement:p", "admitted", "")
    rig.tick()
    rig.gate.demote("operator")
    rig.tick(5)
    rig.time.reboot("boot-2")
    with pytest.raises(Refusal):
        rig.gate.perform("research")
    reasons = [e["reason"] for e in payloads(rig, KIND_EPOCH)]
    assert reasons[0] == "start" and reasons[1] == "demotion:operator" and reasons[2].startswith("discontinuity:boot id")


def test_a_refused_presentation_is_recorded_as_refused(rig: Rig) -> None:
    rig.tick()
    assert rig.refused(issue(rig.epoch(), "bad", environment="env-2")) == "wrong_environment"
    last = payloads(rig, KIND_CHECK)[-1]
    assert (last["subject"], last["verdict"], last["reason"]) == ("presentation:bad", "refused", "wrong_environment")


def test_an_expiry_equal_to_the_decision_time_or_the_receipt_is_expired(rig: Rig) -> None:
    rig.tick()
    assert rig.refused(issue(rig.epoch(), "now", expiry=rig.clock.now())) == "expired"  # expiry == the decision clock
    last = payloads(rig, KIND_CHECK)[-1]
    assert (last["subject"], last["verdict"], last["reason"]) == ("presentation:now", "refused", "expired")


def test_a_drift_equal_to_the_tolerance_is_not_a_discontinuity(rig: Rig) -> None:
    rig.tick()
    rig.gate.perform("research")
    index = rig.index()
    rig.time.advance(timedelta(seconds=1), slew=timedelta(seconds=TOLERANCE))  # drift exactly the tolerance
    rig.gate.perform("research")
    assert rig.index() == index
    rig.time.advance(timedelta(seconds=1), slew=timedelta(microseconds=1))  # one microsecond beyond it
    assert reason_of(lambda: rig.gate.perform("research")) == "clock_discontinuity"


def test_anchor_epoch_reports_an_epoch_already_anchored(rig: Rig) -> None:
    assert rig.gate.state().epoch_anchored and rig.gate.anchor_epoch() is True


def test_a_gate_whose_store_never_answered_has_no_anchored_prefix(tmp_path: Path) -> None:
    clock = ManualClock(BASE)
    ledger = Ledger(tmp_path / "l.sqlite", clock, UnavailableAnchorStore())
    gate = CapabilityGate(ledger, OWNER, ManualTimeSource(clock), ENV, RELEASE, TOLERANCE)
    assert gate.state().epoch_unanchored
    assert reason_of(lambda: gate.perform("research")) == "epoch_unanchored"


def test_a_capability_of_a_new_epoch_may_reuse_a_nonce_of_an_old_one(rig: Rig) -> None:
    rig.tick()
    assert rig.promote(issue(rig.epoch(), "same", level="SHADOW_LIVE_QUOTES")).status == "acknowledged"
    rig.tick()
    rig.gate.demote("rotate")
    rig.tick()
    assert rig.promote(issue(rig.epoch(), "same", level="SHADOW_LIVE_QUOTES")).status == "acknowledged"


def test_every_abort_has_its_own_ledger_identity(rig: Rig) -> None:
    rig.tick()
    for nonce in ("a", "b"):  # two presentations whose intent anchor fails: two aborts on one ledger
        rig.store.mode = "lost"
        assert rig.refused(issue(rig.epoch(), nonce)) == "anchor_failed"
        rig.tick()
    state = rig.gate.state()
    assert sorted(state.aborted.values()) == ["anchor of the intent failed", "anchor of the intent failed"]


def test_a_same_level_promotion_overtaken_by_an_equal_one_is_superseded(rig: Rig) -> None:
    epoch = rig.epoch()
    rig.tick()

    def overtake() -> None:
        assert rig.promote(issue(epoch, "first", level="SIM_READ_ONLY")).status == "acknowledged"

    rig.gate.hooks["after_intent_anchor"] = overtake
    assert rig.refused(issue(epoch, "second", level="SIM_READ_ONLY")) == "superseded"
    (reason,) = rig.gate.state().aborted.values()
    assert reason == "the gate reached SIM_READ_ONLY since the intent; a commit never lowers it"


def test_the_highest_commit_of_the_epoch_is_compared_by_rank_not_by_name(rig: Rig) -> None:
    epoch = rig.epoch()
    rig.tick()
    assert rig.promote(issue(epoch, "read", level="SIM_READ_ONLY")).status == "acknowledged"
    rig.tick()

    def higher_commit_lands_unanchored() -> None:  # SIM_EXECUTION is written, its anchor fails: in doubt
        rig.gate.hooks["after_commit_record"] = lambda: setattr(rig.store, "mode", "lost")
        assert rig.refused(issue(epoch, "exec-1", level="SIM_EXECUTION")) == "commit_in_doubt"

    rig.gate.hooks["after_intent_anchor"] = higher_commit_lands_unanchored
    # "SIM_READ_ONLY" sorts after "SIM_EXECUTION" by name; by rank the written SIM_EXECUTION is the higher one
    assert rig.refused(issue(epoch, "exec-2", level="SIM_EXECUTION")) == "superseded"


def test_an_intent_aborted_by_another_gate_before_step_3_is_refused_by_name(rig: Rig) -> None:
    rig.tick()

    def another_process_starts() -> None:  # its start aborts every pending intent
        CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)

    rig.gate.hooks["after_intent_anchor"] = another_process_starts
    assert rig.refused(issue(rig.epoch(), "late")) == "intent_aborted"
    assert list(rig.gate.state().aborted.values()) == ["aborted at process start"]


def test_a_decision_overtaken_by_a_demotion_is_taken_again(rig: Rig) -> None:
    other = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)  # its start rotates: before the promotion
    rig.tick()
    assert rig.promote(issue(rig.epoch(), "r", level="SIM_READ_ONLY")).status == "acknowledged"
    rig.tick()
    original = rig.ledger.append
    fired = False

    def demotion_lands_first(*args: Any, **kwargs: Any) -> Record:
        nonlocal fired
        if not fired:
            fired = True
            other.demote("between the decision and the write")
        return original(*args, **kwargs)

    rig.ledger.append = demotion_lands_first  # type: ignore[method-assign]
    try:
        assert reason_of(lambda: rig.gate.perform("sim_read")) == "level_insufficient"  # decided again at the floor
    finally:
        rig.ledger.append = original  # type: ignore[method-assign]


def test_a_ledger_that_never_stops_advancing_is_contended(rig: Rig) -> None:
    def always_stale(*args: Any, **kwargs: Any) -> Record:
        raise Refusal("stale_head", "another writer")

    rig.ledger.append = always_stale  # type: ignore[method-assign]
    assert reason_of(lambda: rig.gate.perform("research")) == "contended"


# replay of a malformed gate ledger ---------------------------------------------------------------------------------

def malformed(rig: Rig, kind: str, payload: Any) -> str:
    rig.ledger.append(kind, f"forged:{len(rig.ledger.records())}", payload)
    return reason_of(lambda: replay_gate(rig.ledger.records(), 0, RULES, rig.ledger.local_anchors()))


def genuine_intent(rig: Rig, nonce: str, reading: ClockReading) -> str:
    """An intent as the protected operation writes it, under its nonce's identity, so that the structural checks
    after it are the ones exercised (replay re-validates the intent itself since issue #37, pass 4 W1)."""
    capability = issue(rig.epoch(), nonce)
    intent_id = intent_ledger_id(capability)
    rig.ledger.append(KIND_INTENT, intent_id, IntentRecord(intent_id, capability, "SIM_READ_ONLY", reading).to_payload())
    return intent_id


def test_replay_names_every_malformed_gate_ledger(tmp_path: Path) -> None:
    reading = ClockReading(BASE, 0.0, "boot-1")

    def fresh(name: str) -> Rig:
        sub = tmp_path / name
        sub.mkdir()
        return Rig(sub)

    r = fresh("index")
    assert malformed(r, KIND_EPOCH, EpochRecord(1, 9, "start", reading).to_payload()) == "invalid_gate_ledger"
    r = fresh("twice")
    capability = issue(r.epoch(), "x")
    intent = IntentRecord(intent_ledger_id(capability), capability, "SIM_READ_ONLY", reading)
    r.ledger.append(KIND_INTENT, intent.intent_id, intent.to_payload())
    assert malformed(r, KIND_INTENT, intent.to_payload()) == "invalid_gate_ledger"
    r = fresh("abort")
    assert malformed(r, KIND_ABORT, AbortRecord("i-unknown", "x", reading).to_payload()) == "invalid_gate_ledger"
    r = fresh("commit-after-abort")
    i2 = genuine_intent(r, "y", reading)
    r.ledger.append(KIND_ABORT, "forged-abort-2", AbortRecord(i2, "gone", reading).to_payload())
    assert replay_gate(r.ledger.records(), 0, RULES, r.ledger.local_anchors()).aborted == {i2: "gone"}
    assert malformed(r, KIND_COMMIT, CommitRecord(i2, 1, "ab" * 32, reading).to_payload()) == "invalid_gate_ledger"
    r = fresh("abort-after-commit")
    i3 = genuine_intent(r, "z", reading)
    anchor = r.ledger.anchor()
    r.ledger.append(KIND_COMMIT, "forged-commit-3",
                    CommitRecord(i3, anchor.prefix_length, anchor.digest, reading).to_payload())
    assert i3 in replay_gate(r.ledger.records(), 0, RULES, r.ledger.local_anchors()).commits
    assert malformed(r, KIND_ABORT, AbortRecord(i3, "late", reading).to_payload()) == "invalid_gate_ledger"
    r = fresh("old-epoch")
    i4 = genuine_intent(r, "w", reading)
    r.gate.demote("rotate")
    assert malformed(r, KIND_COMMIT, CommitRecord(i4, 1, "ab" * 32, reading).to_payload()) == "invalid_gate_ledger"


def test_a_receipt_equal_to_the_expiry_is_expired(rig: Rig) -> None:
    time = PausingTimeSource(rig.clock)
    rig.time = time
    rig.gate = CapabilityGate(rig.ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    rig.tick()
    capability = issue(rig.epoch(), "edge", expiry=rig.clock.now() + timedelta(seconds=0.5))
    time.pause = timedelta(seconds=0.5)  # the decision reads before the expiry, the receipt is exactly at it
    assert rig.refused(capability) == "expired"
    assert not rig.gate.state().intents
    last = payloads(rig, KIND_CHECK)[-1]
    assert (last["subject"], last["verdict"], last["reason"]) == ("presentation:edge", "refused", "expired")


def test_an_intent_overtaken_by_a_demotion_is_aborted_as_rotated(rig: Rig) -> None:
    rig.tick()
    def demote() -> None:
        rig.gate.demote("between steps 2 and 3")

    rig.gate.hooks["after_intent_anchor"] = demote
    assert rig.refused(issue(rig.epoch(), "rotated")) == "superseded"
    assert list(rig.gate.state().aborted.values()) == ["epoch rotated since the intent (RC-197)"]
