"""Regression tests for the review of PR #19 (review 5590566979 at 03685d3), one per finding applied.

Each test fails at 03685d3 and passes after the fix.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import FaultInjector, HarnessAnchorStore, Ledger
from cpe.registration import (
    BaseRate,
    BeaconOutput,
    CalibrationRecord,
    CandidateEntry,
    ClaimPreregistration,
    ConfirmatoryRegister,
    CutoffCorrection,
    RegistrationRegistry,
    derive_seed,
)
from tests.test_registration import arm, day, forecast, registration, spec
from tests.test_schemas import HEX


def make(tmp_path: Path, faults: FaultInjector | None = None) -> tuple[RegistrationRegistry, ManualClock, Ledger]:
    """A registry with three arm versions, one base rate and the cluster C-1 (E-1, E-2) registered on day 10."""
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore(), faults)
    r = RegistrationRegistry(ledger)
    r.register_arm_version(arm("A-1", "2026-01-05"))
    r.register_arm_version(arm("DESIGN_C-1", "2026-01-01"))
    r.register_arm_version(arm("FULL-1", "2026-01-03", ["A-1"]))
    r.commit_base_rate(BaseRate("RC-1", 0.2))
    for event_id in ("E-1", "E-2", "E-9"):
        r.log_candidate(CandidateEntry(f"cand-{event_id}", event_id, "src", day(1), "registered", "predicate match"))
    clock.set(day(10))
    r.register_cluster(registration([spec("E-1"), spec("E-2")]))
    return r, clock, ledger


def claim(claim_id: str = "claim-1", calibration_id: str = "cal-1") -> ClaimPreregistration:
    return ClaimPreregistration(claim_id, "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                "period-balanced", ("DESIGN_C",), ("L-1",), calibration_id)


def calibration(round_id: str = "round-7") -> CalibrationRecord:
    return CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", round_id)


def test_4329369299_the_one_register_is_written_once_under_contention(tmp_path: Path) -> None:
    r, _, ledger = make(tmp_path)
    r.register_claim(claim())

    def other_writer() -> None:
        r.anchor_confirmatory_register(ConfirmatoryRegister("reg-0", 1, ("claim-1",)))

    r.before_write = other_writer
    with pytest.raises(Refusal) as refused:
        r.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    assert refused.value.reason == "register_immutable"
    assert [rec.kind for rec in ledger.records()].count("confirmatory_register") == 1
    register = r.state().register
    assert register is not None and register.register_id == "reg-0"


def test_4329369309_a_claim_registered_at_or_after_its_period_start_is_refused(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)
    clock.set(day(60))
    with pytest.raises(Refusal) as refused:
        r.register_claim(claim())
    assert refused.value.reason == "late_claim"
    clock.set(day(59))
    r.register_claim(claim())


@pytest.mark.parametrize("rate", [2.0, -0.1, float("nan")])
def test_4329369272_a_base_rate_is_validated_at_construction(rate: float) -> None:
    with pytest.raises(Refusal) as refused:
        BaseRate("RC-1", rate)
    assert refused.value.reason == "invalid_probability"


def test_4329369210_registration_and_slot_times_come_from_the_ledger_clock(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)
    clock.set(day(25))
    with pytest.raises(Refusal) as refused:
        r.register_cluster(registration([spec("E-9", "C-9")], "C-9"))
    assert refused.value.reason == "issuance_before_registration"
    clock.set(day(41))
    assert {s.arm_id: s.status for s in r.slot_states("E-1")} == {"A": "abstention", "FULL": "abstention",
                                                                   "DESIGN_C": "baseline"}
    assert r.forecasts_for_baseline("E-1") == ()


def test_4329369221_a_version_registered_under_another_arm_is_refused(tmp_path: Path) -> None:
    r, _, _ = make(tmp_path)
    with pytest.raises(Refusal) as refused:
        r.register_cluster(registration([spec("E-9", "C-9")], "C-9",
                                        arms={"FULL": "A-1", "A": "FULL-1", "DESIGN_C": "DESIGN_C-1"}))
    assert refused.value.reason == "arm_mismatch"


def test_4329369232_a_register_naming_an_unknown_claim_is_refused(tmp_path: Path) -> None:
    r, _, _ = make(tmp_path)
    with pytest.raises(Refusal) as refused:
        r.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("ghost",)))
    assert refused.value.reason == "unknown_claim"
    assert r.state().register is None


def test_4329369265_a_correction_before_any_registration_amends_the_version(tmp_path: Path) -> None:
    r, _, _ = make(tmp_path)
    r.register_arm_version(arm("B-1", "2026-01-02"))
    _, registered_under = r.correct_cutoff(CutoffCorrection("B-1", date(2026, 3, 1), "ev-2"))
    assert registered_under is False
    version = r.arm_version("B-1")
    assert version.declared_cutoff == date(2026, 3, 1) and version.cutoff_evidence_id == "ev-2"
    with pytest.raises(Refusal) as refused:  # the corrected cutoff is the one in force: after e_i of E-9 (day 50)
        r.register_cluster(registration([spec("E-9", "C-9")], "C-9",
                                        arms={"FULL": "FULL-1", "B": "B-1", "DESIGN_C": "DESIGN_C-1"}))
    assert refused.value.reason == "cutoff_after_e_i"
    _, registered_under = r.correct_cutoff(CutoffCorrection("B-1", date(2026, 1, 4), "ev-3"))
    assert registered_under is False and r.arm_version("B-1").declared_cutoff == date(2026, 1, 4)
    r.register_cluster(registration([spec("E-9", "C-9")], "C-9",
                                    arms={"FULL": "FULL-1", "B": "B-1", "DESIGN_C": "DESIGN_C-1"}))


def test_4329369281_an_early_forecast_does_not_occupy_the_slot(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)
    clock.set(day(15))
    r.submit_forecast(forecast("E-1", point=0.1))
    clock.set(day(21))
    r.submit_forecast(forecast("E-1", point=0.3))
    assert {s.arm_id: s.status for s in r.slot_states("E-1")}["FULL"] == "filled"
    with pytest.raises(Refusal) as refused:
        r.submit_forecast(forecast("E-1", point=0.5))
    assert refused.value.reason == "slot_occupied"
    clock.set(day(41))
    states = {s.arm_id: s for s in r.slot_states("E-1")}
    assert states["FULL"].status == "filled" and states["FULL"].value == 0.3
    assert [f.forecast.point for f in r.forecasts_of("E-1")] == [0.1, 0.3]


def test_4329369319_colons_in_identifiers_do_not_collide(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    r = RegistrationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    for version, cutoff in (("A:B-1", "2026-01-05"), ("A-1", "2026-01-05"), ("DESIGN_C-1", "2026-01-01"),
                            ("FULL-1", "2026-01-03")):
        r.register_arm_version(arm(version, cutoff))
    r.commit_base_rate(BaseRate("RC-1", 0.2))
    r.log_candidate(CandidateEntry("cand-E-7", "E-7", "src", day(1), "registered", "ok"))
    clock.set(day(10))
    r.register_cluster(registration([spec("E-7", "C-7", slots=["C", "B:C"])], "C-7",
                                    arms={"A:B": "A:B-1", "A": "A-1", "DESIGN_C": "DESIGN_C-1", "FULL": "FULL-1"}))
    clock.set(day(21))
    r.submit_forecast(forecast("E-7", arm_id="A:B", version="A:B-1", slot="C"))
    r.submit_forecast(forecast("E-7", arm_id="A", version="A-1", slot="B:C"))
    clock.set(day(41))
    assert len(r.forecasts_of("E-7")) == 2


def test_4329369255_the_beacon_output_and_its_seed_are_one_durable_record(tmp_path: Path) -> None:
    faults = FaultInjector()
    r, clock, ledger = make(tmp_path, faults)
    r.register_claim(claim())
    r.record_calibration(calibration())
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(13))
    faults.arm("after_commit", OSError("process died after the commit"))
    with pytest.raises(OSError):
        r.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))
    assert r.seed_of("cal-1") == derive_seed(calibration().to_payload(), "ab" * 32)
    with pytest.raises(Refusal) as refused:
        r.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))
    assert refused.value.reason == "second_seed"


def test_4329369243_a_round_dated_after_the_ledger_clock_is_refused(tmp_path: Path) -> None:
    r, clock, ledger = make(tmp_path)
    r.register_claim(claim())
    r.record_calibration(calibration())
    clock.set(day(11))
    ledger.anchor()
    with pytest.raises(Refusal) as refused:
        r.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))
    assert refused.value.reason == "future_round"
    clock.set(day(12))
    r.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))


def test_4329369285_the_calibration_record_preselects_its_round(tmp_path: Path) -> None:
    with pytest.raises(Refusal) as missing:
        CalibrationRecord.from_payload({"calibration_record_id": "cal-1", "claim_id": "claim-1", "algorithm_id": "block-t",
                                        "calibration_size": 1000, "budget": 0.01, "beacon_id": "beacon"})
    assert missing.value.reason == "missing_field"
    r, clock, ledger = make(tmp_path)
    r.register_claim(claim())
    r.record_calibration(calibration("round-7"))
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(13))
    with pytest.raises(Refusal) as refused:
        r.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-8", "ab" * 32, day(12)))
    assert refused.value.reason == "wrong_round"
    r.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))
    assert r.seed_of("cal-1") == derive_seed(calibration("round-7").to_payload(), "ab" * 32)
    assert HEX  # the digest helper of the schema tests is the shape of a beacon value
