"""Regression tests for the second review of PR #19 (review 5590927716 at 7f7522d), one per finding applied.

Each test fails at 7f7522d and passes after the fix. Finding 4329659309 (authenticating the beacon value against
the public beacon) needs a network and is listed for the owner; it has no test.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.registration import (
    CalibrationRecord,
    ClaimPreregistration,
    ClusterRegistration,
    ConfirmatoryRegister,
    CutoffCorrection,
    RegistrationRegistry,
)
from cpe.schemas import ClusterRecord, Forecast
from tests.test_registration import arm, day, forecast, registration, spec
from tests.test_review_round1_pr19 import calibration, claim, make
from tests.test_schemas import HEX


def test_4329659300_a_calibration_record_after_the_claim_period_starts_is_refused(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)
    r.register_claim(claim())
    clock.set(day(60))
    with pytest.raises(Refusal) as refused:
        r.record_calibration(calibration())
    assert refused.value.reason == "late_calibration"
    clock.set(day(59))
    r.record_calibration(calibration())


def test_4329659316_forecasts_and_their_values_are_sealed_until_the_issuance_close(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)
    clock.set(day(21))
    r.submit_forecast(forecast("E-1", arm_id="A", version="A-1", point=0.4))
    with pytest.raises(Refusal) as refused:
        r.forecasts_of("E-1")
    assert refused.value.reason == "read_before_close"
    states = {s.arm_id: s for s in r.slot_states("E-1")}
    assert states["A"].status == "filled" and states["A"].value is None
    clock.set(day(40) + timedelta(microseconds=1))
    assert [f.forecast.point for f in r.forecasts_of("E-1")] == [0.4]
    assert {s.arm_id: s.value for s in r.slot_states("E-1")}["A"] == 0.4


def test_4329659278_the_question_set_is_fixed_before_the_period_and_before_the_claim_record(tmp_path: Path) -> None:
    with pytest.raises(Refusal) as refused:
        ClaimPreregistration("c", "fixed_question_set", "Q", "h", day(60), day(60), day(400), "period-balanced",
                             ("DESIGN_C",), ("L-1",), "cal")
    assert refused.value.reason == "invalid_window"
    r, clock, _ = make(tmp_path)
    future_fixing = ClaimPreregistration("c", "fixed_question_set", "Q", "h", day(30), day(60), day(400),
                                         "period-balanced", ("DESIGN_C",), ("L-1",), "cal")
    with pytest.raises(Refusal) as late:  # the clock is on day 10: the question set is not fixed yet
        r.register_claim(future_fixing)
    assert late.value.reason == "question_set_not_fixed"
    clock.set(day(30))
    r.register_claim(future_fixing)


def test_4329659340_a_claim_is_confirmatory_only_once_the_register_is_anchored(tmp_path: Path) -> None:
    r, clock, ledger = make(tmp_path)
    r.register_claim(claim())
    r.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    assert r.claim_status("claim-1") == "exploratory"
    clock.set(day(11))
    ledger.anchor()
    assert r.claim_status("claim-1") == "confirmatory"


def test_4329659334_a_forecast_object_is_validated_in_full_before_the_append(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)
    clock.set(day(21))
    bad = Forecast("E-1", "FULL", "primary", "FULL-1", 0.3, 0.3, 0.3, "not-hex", HEX, ())
    with pytest.raises(Refusal) as refused:
        r.submit_forecast(bad)
    assert refused.value.reason == "invalid_digest"
    assert r.slot_states("E-1")[0].event_id == "E-1"  # the state still replays


def test_4329659360_the_full_arm_is_mandatory_in_every_registration() -> None:
    cluster = ClusterRecord("C-1", ("E-1",), ())
    with pytest.raises(Refusal) as refused:
        ClusterRegistration(cluster, (spec("E-1"),), {"A": "A-1", "DESIGN_C": "DESIGN_C-1"}, "DESIGN_C")
    assert refused.value.reason == "invalid_cluster" and "FULL" in refused.value.detail
    ClusterRegistration(cluster, (spec("E-1"),), {"FULL": "FULL-1", "DESIGN_C": "DESIGN_C-1"}, "DESIGN_C")


def test_4329659348_two_registries_on_one_ledger_cannot_commit_a_decision_the_other_invalidated(tmp_path: Path) -> None:
    r, _, ledger = make(tmp_path)
    other = RegistrationRegistry(ledger)
    r.register_arm_version(arm("B-1", "2026-01-02"))

    def withdraw_b() -> None:  # lands between the first registry's validation and its append
        other.correct_cutoff(CutoffCorrection("B-1", date(2026, 3, 1), "ev-2"))

    r.before_write = withdraw_b
    with pytest.raises(Refusal) as refused:
        r.register_cluster(registration([spec("E-9", "C-9")], "C-9",
                                        arms={"FULL": "FULL-1", "B": "B-1", "DESIGN_C": "DESIGN_C-1"}))
    assert refused.value.reason == "cutoff_after_e_i"
    assert "C-9" not in r.state().clusters


def test_4329659293_the_register_precedes_the_evaluation_period_of_every_listed_claim(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)
    r.register_claim(claim())
    clock.set(day(60))
    with pytest.raises(Refusal) as refused:
        r.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    assert refused.value.reason == "register_after_period_start"
    assert r.state().register is None


def test_4329659325_a_forecast_at_the_close_is_eligible_and_the_read_opens_after_it(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)
    clock.set(day(40))
    r.submit_forecast(forecast("E-1", point=0.3))
    with pytest.raises(Refusal) as refused:
        r.forecasts_for_baseline("E-1")
    assert refused.value.reason == "read_before_close"
    assert {s.arm_id: s.status for s in r.slot_states("E-1")}["A"] == "open"
    clock.set(day(40) + timedelta(microseconds=1))
    assert len(r.forecasts_for_baseline("E-1")) == 1
    states = {s.arm_id: s for s in r.slot_states("E-1")}
    assert states["FULL"].status == "filled" and states["A"].status == "abstention"


def test_4329659355_the_ledger_clock_fails_closed_below_the_high_water_mark(tmp_path: Path) -> None:
    r, clock, ledger = make(tmp_path)
    clock.set(day(5))
    with pytest.raises(Refusal) as refused:
        ledger.now()
    assert refused.value.reason == "clock_rollback"
    with pytest.raises(Refusal) as gated:
        r.slot_states("E-1")
    assert gated.value.reason == "clock_rollback"
    clock.set(day(41))
    assert r.slot_states("E-1")[0].status in ("abstention", "baseline")
