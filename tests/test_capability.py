"""Offline capability model: T-30, T-31, T-32, T-35 and the T-33 denial check (``17`` section 5, A5; hand-off
section 3.3 and 4.1). Every test is offline and synthetic; the signature double holds no key."""
from __future__ import annotations

import importlib
import threading
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from cpe.canonical import digest_of
from cpe.capability import (
    CapabilityGate,
    GateRules,
    GateState,
    HarnessVerifier,
    ManualTimeSource,
    PromotionOutcome,
    replay_gate,
)
from cpe.capability.records import KIND_CHECK, KIND_EPOCH, KIND_INTENT
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Anchor, FaultInjector, HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from cpe.schemas import Capability

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)
ENV = "env-1"
RELEASE = "ab" * 32
EVIDENCE: dict[str, Any] = {"bundle": "gate-evidence-1", "tests": 182}
TOLERANCE = 1.0
OWNER = HarnessVerifier("owner")
OTHER = HarnessVerifier("not-the-owner")
RULES = GateRules(OWNER, ENV, RELEASE)


def at(seconds: float) -> datetime:
    return BASE + timedelta(seconds=seconds)


def issue(epoch: int, nonce: str, level: str = "SIM_READ_ONLY", expiry: datetime | None = None,
          verifier: HarnessVerifier = OWNER, environment: str = ENV, release: str = RELEASE,
          evidence: Any = EVIDENCE) -> Capability:
    unsigned = Capability(f"promote:{level}", environment, release, digest_of(evidence), epoch, nonce,
                          expiry or at(100 * 86400), "unsigned")
    return replace(unsigned, signature=verifier.sign(unsigned.signed_bytes()))


class FlakyStore:
    """The harness anchor store behind a switch: ``available`` False refuses every call; ``mode`` ``lost`` makes
    the next publish fail before anything lands, ``landed`` makes it land and then fail (a crash around the
    external call, RC-153)."""

    def __init__(self) -> None:
        self.inner = HarnessAnchorStore()
        self.available = True
        self.mode: str | None = None

    def publish(self, anchor: Anchor) -> None:
        if not self.available:
            raise Refusal("anchor_store_unavailable", "the anchor store did not answer")
        mode, self.mode = self.mode, None
        if mode == "lost":
            raise Refusal("anchor_store_unavailable", "the call never reached the store")
        self.inner.publish(anchor)
        if mode == "landed":
            raise Refusal("anchor_store_unavailable", "the acknowledgement was lost after the anchor landed")

    def anchors(self) -> tuple[Anchor, ...]:
        if not self.available:
            raise Refusal("anchor_store_unavailable", "the anchor store did not answer")
        return self.inner.anchors()


class Rig:
    """A ledger file, the manual wall clock and time source, the switchable store, and a started gate."""

    def __init__(self, tmp_path: Path) -> None:
        self.dir = tmp_path
        self.path = tmp_path / "ledger.sqlite"
        self.clock = ManualClock(BASE)
        self.time = ManualTimeSource(self.clock)
        self.store = FlakyStore()
        self.faults = FaultInjector()
        self.ledger = Ledger(self.path, self.clock, self.store, self.faults)
        self.gate = CapabilityGate(self.ledger, OWNER, self.time, ENV, RELEASE, TOLERANCE)

    def tick(self, seconds: float = 1) -> None:
        self.time.advance(timedelta(seconds=seconds))

    def restart(self) -> None:
        """The process dies and starts again on the same ledger file (RC-74, RC-123)."""
        self.ledger.close()
        self.tick()
        self.ledger = Ledger(self.path, self.clock, self.store, self.faults)
        self.gate = CapabilityGate(self.ledger, OWNER, self.time, ENV, RELEASE, TOLERANCE)

    def restore_to_last_anchor(self) -> None:
        """Ledger and JSONL restored to exactly the last external anchor, then a process start (T-07, T-30)."""
        records = records_from_jsonl(self.ledger.export_jsonl())
        last = self.store.anchors()[-1].prefix_length
        self.ledger.close()
        self.tick()
        self.path = self.dir / f"restored-{last}-{len(records)}.sqlite"
        self.ledger, report = Ledger.restore(self.path, self.clock, records[:last], self.store, self.faults)
        assert report.intact and report.anchored_prefix == last
        self.gate = CapabilityGate(self.ledger, OWNER, self.time, ENV, RELEASE, TOLERANCE)

    def epoch(self) -> int:
        return self.gate.state().epoch

    def index(self) -> int:
        return self.gate.state().epoch_index

    def promote(self, capability: Capability) -> PromotionOutcome:
        return self.gate.promote(capability, EVIDENCE)

    def refused(self, capability: Capability) -> str:
        with pytest.raises(Refusal) as refusal:
            self.gate.promote(capability, EVIDENCE)
        return refusal.value.reason

    def invariants(self, nonce_capability: Capability) -> None:
        """After any crash, restart or restore: the capability acts at most once, no intent is pending, no anchor
        covers a prefix the local ledger never held, live state equals replay state (RC-153, RC-158)."""
        state = self.gate.state()
        assert len([i for i in state.effective if state.intents[i].capability.nonce == nonce_capability.nonce]) <= 1
        assert state.pending_intents == ()
        assert all(a.prefix_length <= self.ledger.state.count for a in self.store.anchors())
        exported = records_from_jsonl(self.ledger.export_jsonl())
        prefix = max((a.prefix_length for a in self.ledger.local_anchors()), default=0)
        assert replay_gate(exported, prefix, RULES) == state
        assert self.refused(nonce_capability) in ("stale_epoch", "nonce_consumed")


@pytest.fixture
def rig(tmp_path: Path) -> Rig:
    return Rig(tmp_path)


# T-31: whole-tuple signature under one canonical serialisation (RC-62) ----------------------------------------

def test_t31_a_capability_signed_with_a_non_owner_key_is_refused(rig: Rig) -> None:
    assert rig.refused(issue(rig.epoch(), "n-1", verifier=OTHER)) == "invalid_signature"
    assert rig.gate.state().level == "RESEARCH_ONLY"


@pytest.mark.parametrize("field, value", [
    ("capability", "promote:SIM_EXECUTION"), ("environment", "env-2"), ("release_digest", "cd" * 32),
    ("evidence_digest", "ef" * 32), ("epoch", 7), ("nonce", "n-other"), ("expiry", at(200 * 86400)),
])
def test_t31_each_signed_field_mutated_under_a_valid_signature_is_refused(rig: Rig, field: str, value: object) -> None:
    mutated = replace(issue(rig.epoch(), "n-1"), **{field: value})  # type: ignore[arg-type]
    assert rig.refused(mutated) == "invalid_signature"


def test_t31_the_same_tuple_serialised_in_another_key_order_verifies(rig: Rig) -> None:
    payload = issue(rig.epoch(), "n-1").to_payload()
    reordered = Capability.from_payload(dict(reversed(list(payload.items()))))
    assert rig.promote(reordered).status == "acknowledged"
    assert rig.gate.state().level == "SIM_READ_ONLY"


def test_t31_an_added_field_and_a_re_typed_numeric_field_are_refused(rig: Rig) -> None:
    payload = issue(rig.epoch(), "n-1").to_payload()
    with pytest.raises(Refusal) as added:
        Capability.from_payload({**payload, "scope": "all"})
    assert added.value.reason == "unknown_field"
    with pytest.raises(Refusal):
        Capability.from_payload({**payload, "epoch": str(payload["epoch"])})
    retyped = replace(issue(rig.epoch(), "n-2"), epoch="1")  # type: ignore[arg-type]
    with pytest.raises(Refusal):
        rig.promote(retyped)  # validated in full through its payload before anything is written


# T-30: the capability cases, sequential ------------------------------------------------------------------------

def test_t30_replayed_after_demotion_after_expiry_with_a_stale_epoch_and_with_a_consumed_nonce(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    assert rig.promote(a).status == "acknowledged"
    assert rig.refused(a) == "nonce_consumed"
    rig.gate.demote("test")
    assert rig.refused(a) == "stale_epoch"
    assert rig.refused(issue(rig.epoch() ^ 1, "b")) == "stale_epoch"
    expiring = issue(rig.epoch(), "c", expiry=at(30))
    rig.tick(60)
    assert rig.refused(expiring) == "expired"
    assert rig.gate.state().level == "RESEARCH_ONLY"


def test_t30_wrong_environment_wrong_release_and_other_evidence_are_refused(rig: Rig) -> None:
    assert rig.refused(issue(rig.epoch(), "e", environment="env-2")) == "wrong_environment"
    assert rig.refused(issue(rig.epoch(), "r", release="cd" * 32)) == "wrong_release"
    assert rig.refused(issue(rig.epoch(), "v", evidence={"bundle": "other"})) == "evidence_mismatch"


def test_t30_the_same_capability_presented_by_two_threads_at_once_acts_exactly_once(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def present() -> None:
        barrier.wait()
        try:
            outcomes.append(rig.gate.promote(a, EVIDENCE).status)
        except Refusal as refusal:
            outcomes.append(refusal.reason)

    threads = [threading.Thread(target=present) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(outcomes) == ["acknowledged", "nonce_consumed"]
    assert len(rig.gate.state().effective) == 1


def test_t30_restore_to_the_previous_anchor_after_an_acknowledged_action_refuses_the_capability(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    rig.tick()
    anchors_before = len(rig.store.anchors())
    assert rig.promote(a).status == "acknowledged"
    assert len(rig.store.anchors()) == anchors_before + 2  # the intent's anchor and the commit's
    records = records_from_jsonl(rig.ledger.export_jsonl())
    previous = rig.store.anchors()[anchors_before - 1].prefix_length
    rig.ledger.close()
    rig.tick()
    rig.ledger, report = Ledger.restore(rig.dir / "previous.sqlite", rig.clock, records[:previous], rig.store, rig.faults)
    assert report.status == "truncated" and not report.intact  # the external store still holds the later anchors (T-07)
    rig.gate = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)
    assert rig.gate.state().level == "RESEARCH_ONLY"
    assert rig.refused(a) == "stale_epoch"  # the start rotated the epoch; the restored prefix holds no nonce


def test_t30_anchor_store_unavailable_during_a_protected_action_fails_closed(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    rig.store.available = False
    assert rig.refused(a) == "anchor_failed"
    state = rig.gate.state()
    assert a.nonce in {i.capability.nonce for i in state.intents.values()}
    assert state.pending_intents == () and state.level == "RESEARCH_ONLY" and not state.effective
    rig.store.available = True
    assert rig.refused(a) == "nonce_consumed"  # consumed from step 1 on every branch


def test_t30_rc103_a_second_unused_capability_of_the_pre_demotion_epoch_is_stale(rig: Rig) -> None:
    epoch = rig.epoch()
    a, b = issue(epoch, "a"), issue(epoch, "b")
    assert rig.promote(a).status == "acknowledged"
    rig.gate.demote("operator")
    assert rig.refused(b) == "stale_epoch"
    assert rig.gate.state().level == "RESEARCH_ONLY"


def test_t30_rc123_demotion_with_the_anchor_store_unavailable_takes_effect_at_once(rig: Rig) -> None:
    epoch = rig.epoch()
    a, b = issue(epoch, "a"), issue(epoch, "b")
    assert rig.promote(a).status == "acknowledged"
    index = rig.index()
    rig.store.available = False
    state = rig.gate.demote("operator")
    assert state.level == "RESEARCH_ONLY" and state.epoch_unanchored and state.epoch_index == index + 1
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("research")
    assert refused.value.reason == "epoch_unanchored"  # every protected action refused while demoted-unanchored
    fresh = issue(state.epoch, "c")
    assert rig.refused(fresh) == "epoch_unanchored"  # every promotion too
    rig.store.available = True  # (i) the store returns and B is presented
    assert rig.refused(b) == "stale_epoch"
    assert rig.gate.state().level == "RESEARCH_ONLY"
    assert rig.gate.anchor_epoch() is True
    assert rig.promote(fresh).status == "acknowledged"


def test_t30_rc123_restart_while_the_store_is_down_begins_at_the_floor(rig: Rig) -> None:
    epoch = rig.epoch()
    a, b = issue(epoch, "a"), issue(epoch, "b")
    assert rig.promote(a).status == "acknowledged"
    index = rig.index()
    rig.store.available = False
    demoted = rig.gate.demote("operator").epoch
    rig.restart()  # (ii) the process restarts while the store is down
    state = rig.gate.state()
    assert state.level == "RESEARCH_ONLY" and state.epoch_unanchored and state.epoch_index == index + 2
    assert rig.refused(b) == "stale_epoch"
    assert rig.refused(issue(demoted, "c")) == "stale_epoch"  # the demotion's epoch is stale after the start
    fresh = issue(state.epoch, "d")
    assert rig.refused(fresh) == "epoch_unanchored"
    rig.store.available = True
    assert rig.gate.anchor_epoch() is True
    assert rig.promote(fresh).status == "acknowledged"


def test_t30_rc123_restore_to_the_last_anchor_after_an_unanchored_demotion(rig: Rig) -> None:
    epoch = rig.epoch()
    a, b = issue(epoch, "a"), issue(epoch, "b")
    assert rig.promote(a).status == "acknowledged"
    rig.store.available = False
    demoted = rig.gate.demote("operator").epoch
    records = records_from_jsonl(rig.ledger.export_jsonl())
    with pytest.raises(Refusal) as refused:  # a restore needs the external store (T-18): fails closed while it is down
        Ledger.restore(rig.dir / "down.sqlite", rig.clock, records, rig.store)
    assert refused.value.reason == "anchor_store_unavailable"
    rig.store.available = True
    rig.restore_to_last_anchor()  # the last anchor is the promotion's: the restored ledger holds no demotion
    state = rig.gate.state()
    assert state.level == "RESEARCH_ONLY"  # every start begins at the floor: the restore revives no level
    assert rig.refused(b) == "stale_epoch"
    assert rig.refused(issue(demoted, "c")) == "stale_epoch"  # the dropped epoch's capability never acts


# T-30: crash points of the four-step anchored commit (RC-153, RC-158) --------------------------------------------

CRASH_POINTS = ["before_intent", "after_intent", "after_intent_anchor", "after_commit_record", "after_commit_anchor"]


@pytest.mark.parametrize("point", CRASH_POINTS)
@pytest.mark.parametrize("recovery", ["restart", "restore"])
def test_t30_a_crash_at_each_step_leaves_the_capability_acting_at_most_once(rig: Rig, point: str, recovery: str) -> None:
    a = issue(rig.epoch(), "a")
    rig.tick()

    def crash() -> None:
        raise RuntimeError(f"process killed at {point}")

    rig.gate.hooks[point] = crash
    with pytest.raises(RuntimeError):
        rig.promote(a)
    before = rig.gate.state()
    if recovery == "restart":
        rig.restart()
    else:
        rig.restore_to_last_anchor()
    state = rig.gate.state()
    assert state.level == "RESEARCH_ONLY"
    if point == "after_commit_record":  # a commit outside every anchor is anchored at start and takes effect, unacknowledged
        if recovery == "restart":
            assert a.nonce in {state.intents[i].capability.nonce for i in state.effective} and state.superseded
        else:
            assert not state.commits  # the restore removed the never-acknowledged commit; its intent was aborted
    if point == "after_commit_anchor":
        if recovery == "restart":
            assert a.nonce in {state.intents[i].capability.nonce for i in state.effective}
        else:  # the change that took effect lies inside the last anchor and survives the restore
            assert a.nonce in {state.intents[i].capability.nonce for i in state.effective}
    if before.pending_intents and recovery == "restart":
        assert set(before.pending_intents) <= set(state.aborted)
    rig.invariants(a)


@pytest.mark.parametrize("mode", ["lost", "landed"])
@pytest.mark.parametrize("step", ["intent", "commit"])
@pytest.mark.parametrize("recovery", ["restart", "restore"])
def test_t30_an_anchor_call_that_fails_lost_or_landed_at_either_anchoring_step(rig: Rig, mode: str, step: str, recovery: str) -> None:
    a = issue(rig.epoch(), "a")
    rig.tick()
    if step == "intent":
        rig.store.mode = mode
    else:
        rig.gate.hooks["after_commit_record"] = lambda: setattr(rig.store, "mode", mode)
    reason = rig.refused(a)
    assert reason == ("anchor_failed" if step == "intent" else "commit_in_doubt")
    state = rig.gate.state()
    if step == "intent":
        assert state.pending_intents == () and not state.commits  # aborted; the nonce stays consumed
    else:
        assert state.unanchored_commits if mode == "lost" else True  # in doubt, never aborted
    if recovery == "restart":
        rig.restart()
    else:
        rig.restore_to_last_anchor()
    assert rig.gate.state().level == "RESEARCH_ONLY"
    rig.invariants(a)


def test_t30_a_local_commit_failure_after_the_intent_anchor_leaves_the_nonce_consumed_and_nothing_effective(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    rig.tick()
    rig.gate.hooks["after_intent_anchor"] = lambda: rig.faults.arm("before_commit", OSError("disk full"))
    with pytest.raises(OSError):
        rig.promote(a)
    state = rig.gate.state()
    assert state.pending_intents and not state.commits
    rig.restart()
    state = rig.gate.state()
    assert state.pending_intents == () and not state.commits and state.level == "RESEARCH_ONLY"
    rig.invariants(a)


# T-30: a demotion in every gap of the four steps (RC-197) ------------------------------------------------------

@pytest.mark.parametrize("point, expected", [
    ("before_intent", "stale_epoch"), ("after_intent", "superseded"), ("after_intent_anchor", "superseded"),
    ("after_commit_record", "superseded"), ("after_commit_anchor", "superseded"),
])
@pytest.mark.parametrize("recovery", ["none", "restart", "restore"])
def test_t30_rc197_a_demotion_in_every_gap_ends_at_the_floor_live_and_on_replay(rig: Rig, point: str, expected: str, recovery: str) -> None:
    a = issue(rig.epoch(), "a")
    rig.tick()
    def demote() -> None:
        rig.gate.demote("interleaved")

    rig.gate.hooks[point] = demote
    if point in ("after_commit_record", "after_commit_anchor"):
        outcome = rig.promote(a)
        assert outcome.status == "superseded" and outcome.level == "RESEARCH_ONLY"
        state = rig.gate.state()
        assert state.effective and state.superseded  # the change took effect at its position, then was superseded
    else:
        assert rig.refused(a) == expected
    assert rig.gate.state().level == "RESEARCH_ONLY"
    if recovery == "restart":
        rig.restart()
    elif recovery == "restore":
        rig.restore_to_last_anchor()
    assert rig.gate.state().level == "RESEARCH_ONLY"
    rig.invariants(a)


# T-32: no object is authority (RC-46) ---------------------------------------------------------------------------

def test_t32_a_fabricated_elevated_state_confers_nothing_on_a_protected_operation(rig: Rig) -> None:
    by_constructor = GateState(level="SIM_EXECUTION", epoch=rig.epoch(), epoch_anchored=True)
    by_reflection = object.__new__(GateState)
    object.__setattr__(by_reflection, "level", "SIM_EXECUTION")
    by_import = importlib.import_module("cpe.capability.state").GateState(level="SIM_EXECUTION")
    for fabricated in (by_constructor, by_reflection, by_import):
        rig.gate.__dict__["_fabricated"] = fabricated  # planted in the gate's own namespace
        with pytest.raises(Refusal) as refused:
            rig.gate.perform("sim_execution")
        assert refused.value.reason == "level_insufficient"
    unsigned = replace(issue(rig.epoch(), "x", level="SIM_EXECUTION"), signature="fabricated")
    assert rig.refused(unsigned) == "invalid_signature"
    assert rig.gate.state().level == "RESEARCH_ONLY"


# T-33: SHADOW_LIVE_QUOTES alone denies SIM execution; live stays blocked ---------------------------------------

def test_t33_shadow_live_quotes_alone_denies_sim_execution(rig: Rig) -> None:
    assert rig.promote(issue(rig.epoch(), "s", level="SHADOW_LIVE_QUOTES")).status == "acknowledged"
    rig.gate.perform("shadow_quotes")
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("sim_execution")
    assert refused.value.reason == "level_insufficient"


def test_live_promotion_is_blocked_in_code_whatever_the_signature(rig: Rig) -> None:
    assert rig.refused(issue(rig.epoch(), "l", level="LIVE_EXECUTION")) == "live_blocked"
    assert KIND_INTENT not in {r.kind for r in rig.ledger.records()}


# T-35: clock rules (RC-37, RC-65, RC-73, RC-100) -----------------------------------------------------------------

def test_t35_rc65_a_rollback_after_a_rejected_expired_check_is_refused_and_survives_restart(rig: Rig) -> None:
    a = issue(rig.epoch(), "a", expiry=at(20))
    rig.tick(10)
    rig.gate.perform("research")  # admission at t0 = 10, persisted
    rig.tick(20)
    assert rig.refused(a) == "expired"  # the rejected check at t2 = 30 persists its time too
    assert rig.ledger.records()[-1].kind == KIND_CHECK
    rig.clock.set(at(15))
    assert rig.refused(a) == "clock_rollback"  # the same capability, presented below the high-water mark
    with pytest.raises(Refusal) as during_admission:
        rig.gate.perform("research")
    assert during_admission.value.reason == "clock_rollback"
    rig.ledger.close()
    with pytest.raises(Refusal) as on_start:  # the high-water mark survives the restart: the start fails closed
        CapabilityGate(Ledger(rig.path, rig.clock, rig.store), OWNER, rig.time, ENV, RELEASE, TOLERANCE)
    assert on_start.value.reason == "clock_rollback"


def test_t35_rc73_an_idle_window_before_a_rollback_is_a_discontinuity_requiring_re_authorisation(rig: Rig) -> None:
    epoch, index = rig.epoch(), rig.index()
    a = issue(epoch, "a", expiry=at(20))
    rig.tick(10)
    rig.gate.perform("research")  # admission at 10
    rig.time.advance(timedelta(seconds=20))  # the machine is idle until real time 30
    rig.clock.set(at(15))  # the wall clock is rolled back to 15 before the next check
    assert rig.refused(a) == "clock_discontinuity"
    state = rig.gate.state()
    assert state.epoch != epoch and state.epoch_index == index + 1 and state.level == "RESEARCH_ONLY"
    assert rig.refused(a) == "stale_epoch"  # re-authorisation: only a capability of the new epoch can act
    assert rig.promote(issue(state.epoch, "b")).status == "acknowledged"


def test_t35_rc73_a_reboot_is_a_discontinuity(rig: Rig) -> None:
    index = rig.index()
    rig.tick(5)
    rig.time.reboot("boot-2", monotonic=0.0)
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("research")
    assert refused.value.reason == "clock_discontinuity"
    assert rig.gate.state().epoch_index == index + 1
    assert rig.ledger.records()[-1].kind == KIND_EPOCH and "boot-2" in str(rig.ledger.records()[-1].payload)


def test_t35_rc100_cumulative_slew_is_detected_against_the_epoch_baseline(rig: Rig) -> None:
    epoch, index = rig.epoch(), rig.index()
    a = issue(epoch, "a", expiry=at(60))
    rig.tick(1)
    rig.gate.perform("research")  # the first check, at the baseline offset
    reasons: list[str] = []
    for check in range(2, 101):  # each check slews the wall clock by 0.75 of the tolerance against the monotonic clock
        rig.time.advance(timedelta(seconds=0.25), slew=timedelta(seconds=0.75 * TOLERANCE))
        try:
            rig.gate.perform("research")
            reasons.append("admitted")
        except Refusal as refusal:
            reasons.append(refusal.reason)
            break
    assert reasons == ["admitted", "clock_discontinuity"]  # refused at the third check, long before the expiry at 60
    assert rig.clock.now() < at(60)
    assert rig.gate.state().epoch_index == index + 1
    assert rig.refused(a) == "stale_epoch"


# start-up, replay and persistence -------------------------------------------------------------------------------

def test_every_start_rotates_the_epoch_anchors_it_and_begins_at_the_floor(rig: Rig) -> None:
    first = rig.gate.state()
    assert first.epoch_index == 1 and first.epoch_anchored and first.level == "RESEARCH_ONLY"
    assert rig.promote(issue(first.epoch, "a")).status == "acknowledged"
    assert rig.gate.state().level == "SIM_READ_ONLY"
    rig.restart()
    state = rig.gate.state()
    assert state.epoch_index == 2 and state.epoch != first.epoch and state.level == "RESEARCH_ONLY" and state.epoch_anchored
    assert rig.refused(issue(first.epoch, "b")) == "stale_epoch"


def test_every_check_persists_its_reading_before_its_verdict(rig: Rig) -> None:
    rig.tick(3)
    record = rig.gate.perform("research")
    assert isinstance(record.payload, dict)
    reading = record.payload["reading"]
    assert isinstance(reading, dict) and reading["monotonic"] == 3.0 and reading["boot_id"] == "boot-1"
    assert record.receipt_time == reading["wall"]
    assert rig.refused(issue(rig.epoch(), "z", verifier=OTHER)) == "invalid_signature"
    refused = rig.ledger.records()[-1]
    assert refused.kind == KIND_CHECK and isinstance(refused.payload, dict) and refused.payload["reason"] == "invalid_signature"


def test_state_is_replayed_byte_for_byte_from_the_ledger(rig: Rig) -> None:
    rig.promote(issue(rig.epoch(), "a"))
    rig.gate.demote("x")
    rig.store.available = True
    rig.gate.anchor_epoch()
    state = rig.gate.state()
    digest = rig.ledger.state_digest()
    rig.ledger.close()
    reopened = Ledger(rig.path, rig.clock, rig.store)
    assert reopened.state_digest() == digest
    prefix = max(a.prefix_length for a in reopened.local_anchors())
    assert replay_gate(reopened.records(), prefix, RULES) == state


def test_the_slew_tolerance_is_a_named_owner_field(rig: Rig) -> None:
    with pytest.raises(Refusal) as refused:
        CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, 0.0)
    assert refused.value.reason == "invalid_tolerance"
