"""Whole-codebase audit, pass 1 (issue #37, findings C1 and C2): a "before" bound checked against a clock sample
taken before the append, not against the receipt the append assigns. Time that passes between the two let a
registration record be received at e_i, a claim at its period start and an event's criteria at its issuance open.
Each test failed on the audit commit 04fee70; the same class was fixed for the candidate log in H1 (PR #23
4330096714) and for observations and statuses in PR #32 (H1 review 4334622048)."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.registration import (
    BaseRate,
    BeaconOutput,
    CalibrationRecord,
    CandidateEntry,
    ClaimPreregistration,
    ConfirmatoryRegister,
    RegistrationRegistry,
)
from cpe.schemas import EventSpec
from tests import test_adjudication as adj
from tests.test_registration import arm, day, registration, spec, ts


class SteppingClock(ManualClock):
    """A manual clock that moves on to ``then`` right after its next reading: time passing between two samples."""

    def __init__(self, start: datetime) -> None:
        super().__init__(start)
        self.then: datetime | None = None

    def now(self) -> datetime:
        value = super().now()
        if self.then is not None:
            self.set(self.then)
            self.then = None
        return value


@pytest.fixture
def clock() -> ManualClock:
    return ManualClock(day(1))


@pytest.fixture
def registry(tmp_path: Path, clock: ManualClock) -> RegistrationRegistry:
    r = RegistrationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    r.register_arm_version(arm("A-1", "2026-01-05"))
    r.register_arm_version(arm("DESIGN_C-1", "2026-01-01"))
    r.register_arm_version(arm("FULL-1", "2026-01-03", ["A-1"]))
    r.commit_base_rate(BaseRate("RC-1", 0.2))
    return r


def refusal_of(call: object) -> str:
    assert callable(call)
    with pytest.raises(Refusal) as refused:
        call()
    return refused.value.reason


def just_before(moment: datetime) -> datetime:
    return moment - timedelta(microseconds=1)


def test_a_registration_record_received_at_e_i_is_refused(registry: RegistrationRegistry, clock: ManualClock) -> None:
    registry.log_candidate(CandidateEntry("cand-F", "F-1", "src", day(1), "registered", "ok"))
    base = spec("F-1", "C-F", not_before=20, kind="terminal-falsifier", falsifier_from=15, issuance=(14, 15)).to_payload()
    at_e_i = EventSpec.from_payload({**base, "issuance_open": ts(15), "evidence_cutoff": ts(15)})
    clock.set(just_before(day(15)))
    registry.before_write = lambda: clock.set(day(15))  # the receipt reaches e_i after the decision
    assert refusal_of(lambda: registry.register_cluster(registration([at_e_i], "C-F"))) == "registration_after_e_i"
    assert "F-1" not in registry.state().events


def test_a_registration_record_received_after_the_issuance_open_is_refused(registry: RegistrationRegistry,
                                                                           clock: ManualClock) -> None:
    registry.log_candidate(CandidateEntry("cand-E", "E-1", "src", day(1), "registered", "ok"))
    clock.set(just_before(day(20)))
    registry.before_write = lambda: clock.set(day(20) + timedelta(microseconds=1))
    assert refusal_of(lambda: registry.register_cluster(registration([spec("E-1")]))) == "issuance_before_registration"


def claim(claim_id: str = "claim-1", calibration_id: str = "cal-1") -> ClaimPreregistration:
    return ClaimPreregistration(claim_id, "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                "period-balanced", ("DESIGN_C",), ("L-1",), calibration_id)


def test_a_claim_received_at_its_period_start_is_refused(registry: RegistrationRegistry, clock: ManualClock) -> None:
    clock.set(just_before(day(60)))
    registry.before_write = lambda: clock.set(day(60))
    assert refusal_of(lambda: registry.register_claim(claim())) == "late_claim"


def test_a_calibration_record_received_at_the_period_start_is_refused(registry: RegistrationRegistry,
                                                                      clock: ManualClock) -> None:
    registry.register_claim(claim())
    clock.set(just_before(day(60)))
    registry.before_write = lambda: clock.set(day(60))
    record = CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7")
    assert refusal_of(lambda: registry.record_calibration(record)) == "late_calibration"


def test_a_register_received_at_a_listed_period_start_is_refused(registry: RegistrationRegistry,
                                                                  clock: ManualClock) -> None:
    registry.register_claim(claim())
    clock.set(just_before(day(60)))
    registry.before_write = lambda: clock.set(day(60))
    register = ConfirmatoryRegister("reg-1", 1, ("claim-1",))
    assert refusal_of(lambda: registry.anchor_confirmatory_register(register)) == "register_after_period_start"


def test_a_beacon_output_is_still_supplied_after_the_anchors_are_read(registry: RegistrationRegistry,
                                                                      clock: ManualClock) -> None:
    """The decision of a beacon output reads the local anchors with its snapshot, never under the ledger's lock."""
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    registry._ledger.anchor()
    clock.set(day(12))
    _, seed = registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(11)))
    assert registry.seed_of("cal-1") == seed


def test_event_criteria_received_at_the_issuance_open_are_refused(tmp_path: Path) -> None:
    clock = SteppingClock(adj.day(1))
    registry = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    registry.register_rule(adj.rule())
    event = adj.spec()
    clock.set(just_before(event.issuance_open))
    clock.then = event.issuance_open  # the append's receipt follows the registry's sample
    assert refusal_of(lambda: registry.register_event(event)) == "late_registration"
    assert registry.state().event(event.event_id).spec is None
