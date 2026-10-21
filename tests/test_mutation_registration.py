"""Mutation testing, ``cpe/registration``: tests that kill mutants the suite let survive at ac4c640 (``research/19``
section "Mutation testing"). They pin the reason code of every refusal of the pre-registration registry, the ledger
identity of every record kind (two of a kind never collide), the round trip of every record, the boundaries of the
claim and calibration records, the consumption closure and the slot states."""
from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

import pytest

from cpe.canonical import canonical_bytes
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger, Record
from cpe.registration import (
    BaseRate,
    BeaconOutput,
    CalibrationRecord,
    CandidateEntry,
    ClaimPreregistration,
    ClusterRegistration,
    ConfirmatoryRegister,
    CutoffCorrection,
    RegistrationRegistry,
    SlotState,
    VoidRequest,
    derive_seed,
)
from cpe.schemas import ClusterRecord
from tests.test_registration import arm, clock, day, forecast, ledger, registration, registry, spec  # noqa: F401

__all__ = ["clock", "ledger", "registry"]  # the fixtures of test_registration, used here by name


def refused(call: object, *args: object, **kwargs: object) -> str:
    assert callable(call)
    with pytest.raises(Refusal) as refusal:
        call(*args, **kwargs)
    return refusal.value.reason


def claim(claim_id: str = "claim-1", calibration: str = "cal-1", **fields: Any) -> ClaimPreregistration:
    values: dict[str, Any] = {"claim_id": claim_id, "population_kind": "fixed_question_set", "question_set_id": "Q-1",
                              "holder_id": "holder", "question_set_fixed_at": day(1), "period_start": day(60),
                              "period_end": day(400), "weighting": "period-balanced", "family_order": ("DESIGN_C",),
                              "validity_class_ids": ("L-1",), "calibration_record_id": calibration}
    values.update(fields)
    return ClaimPreregistration(**values)


def calibration(record_id: str = "cal-1", claim_id: str = "claim-1", size: int = 1000,
                budget: float = 0.01) -> CalibrationRecord:
    return CalibrationRecord(record_id, claim_id, "block-t", size, budget, "beacon", "round-7")


# records ------------------------------------------------------------------------------------------------------------

def test_every_registration_record_round_trips_through_its_payload() -> None:
    events = [spec("E-1"), spec("E-2")]
    for record in (CandidateEntry("c", "E", "src", day(1), "rejected", "why"), VoidRequest("v", "E-1", "why"),
                   BaseRate("RC", 0.2), CutoffCorrection("A-1", date(2026, 1, 4), "ev"),
                   claim(weighting="event-weighted"), ConfirmatoryRegister("reg", 2, ()), calibration(),
                   BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)),
                   registration(events, void=["E-2"])):
        assert type(record).from_payload(record.to_payload()) == record
    assert VoidRequest("v", "E", "why").to_payload() == {"request_id": "v", "event_id": "E", "reason": "why"}


def test_record_refusals_are_named_and_bounds_are_exact() -> None:
    assert refused(CandidateEntry.from_payload, {**CandidateEntry("c", "E", "s", day(1), "registered", "r").to_payload(),
                                                 "decision": "maybe"}) == "invalid_choice"
    assert refused(CandidateEntry.from_payload, {**CandidateEntry("c", "E", "s", day(1), "registered", "r").to_payload(),
                                                 "decision": 1}) == "invalid_choice"
    assert refused(claim, period_start=day(400)) == "invalid_window"  # period_start == period_end
    assert refused(claim, question_set_fixed_at=day(60)) == "invalid_window"  # fixed at the period start
    assert refused(claim, family_order=()) == "invalid_family"
    assert refused(claim, validity_class_ids=("L-1", "L-2")) == "invalid_family"
    payload = claim().to_payload()
    assert refused(ClaimPreregistration.from_payload, {**payload, "family_order": []}) == "empty_list"
    assert refused(ClaimPreregistration.from_payload, {**payload, "validity_class_ids": []}) == "empty_list"
    assert refused(ConfirmatoryRegister, "reg", 0, ()) == "invalid_register"
    assert refused(ConfirmatoryRegister, "reg", 1, ("a", "b")) == "invalid_register"
    assert ConfirmatoryRegister.from_payload({"register_id": "r", "s_max": 1, "confirmatory_claim_ids": []}).s_max == 1
    assert calibration(size=1).calibration_size == 1
    assert refused(calibration, "cal-1", "claim-1", 0) == "invalid_calibration"
    for budget in (0.0, 1.0, 1.5):
        assert refused(calibration, "cal-1", "claim-1", 1000, budget) == "invalid_calibration"
    assert refused(CalibrationRecord.from_payload, {**calibration().to_payload(), "budget": True}) == "invalid_calibration"
    assert refused(CalibrationRecord.from_payload, {**calibration().to_payload(), "budget": "0.01"}) == "invalid_calibration"


def test_cluster_registration_refusals_are_named() -> None:
    e1, e2 = spec("E-1"), spec("E-2")
    assert refused(ClusterRegistration, ClusterRecord("C-1", ("E-1",)), (e1, e2), {"FULL": "F", "D": "D"}, "D") \
        == "invalid_cluster"
    assert refused(ClusterRegistration, ClusterRecord("C-2", ("E-1",)), (e1,), {"FULL": "F", "D": "D"}, "D") \
        == "invalid_cluster"
    assert refused(ClusterRegistration, ClusterRecord("C-1", ("E-1",)), (e1,), {"FULL": "F"}, "D") == "invalid_cluster"
    payload = registration([e1]).to_payload()
    assert refused(ClusterRegistration.from_payload, {**payload, "events": {}}) == "invalid_list"


def test_the_seed_is_sha256_of_the_record_bytes_and_the_beacon_value() -> None:
    record = calibration().to_payload()
    expected = hashlib.sha256(canonical_bytes(record) + ("ab" * 32).encode("ascii")).hexdigest()
    assert derive_seed(record, "ab" * 32) == expected


# the registry: refusals ---------------------------------------------------------------------------------------------

def test_arm_version_refusals_are_named(registry: RegistrationRegistry) -> None:
    assert refused(registry.register_arm_version, arm("A-1", "2026-01-05")) == "arm_version_immutable"
    assert refused(registry.register_arm_version, arm("B-1", "2026-01-05", ["Z-1"])) == "unknown_arm_version"
    assert refused(registry.arm_version, "Z-1") == "unknown_arm_version"
    assert refused(registry.correct_cutoff, CutoffCorrection("Z-1", date(2026, 1, 4), "ev")) == "unknown_arm_version"
    registry.correct_cutoff(CutoffCorrection("A-1", date(2026, 1, 4), "ev-1"))  # A-1 is consumed by FULL-1: withdrawn
    assert refused(registry.correct_cutoff, CutoffCorrection("A-1", date(2026, 1, 4), "ev-2")) == "arm_version_withdrawn"


def test_registry_lookups_and_submissions_refuse_by_name(registry: RegistrationRegistry, clock: ManualClock) -> None:
    assert refused(registry.log_candidate, CandidateEntry("cand-x", "E-1", "src", day(1), "registered", "again")) \
        == "candidate_exists"
    assert refused(registry.commit_base_rate, BaseRate("RC-1", 0.3)) == "base_rate_immutable"
    assert refused(registry.event, "E-9") == "unknown_event"
    assert refused(registry.request_void, VoidRequest("v", "E-9", "why")) == "unknown_event"
    assert refused(registry.forecasts_of, "E-9") == "unknown_event"
    assert refused(registry.slot_states, "E-9") == "unknown_event"
    registry.log_candidate(CandidateEntry("cand-3", "E-3", "src", day(1), "registered", "ok"))
    assert refused(registry.register_cluster, registration([spec("E-1", "C-2"), spec("E-3", "C-2")], "C-2")) \
        == "event_registered"
    assert refused(registry.register_cluster, registration([spec("E-1"), spec("E-2")])) == "cluster_immutable"


def test_claim_and_calibration_refusals_are_named(registry: RegistrationRegistry) -> None:
    registry.register_claim(claim())
    assert refused(registry.register_claim, claim()) == "claim_immutable"
    assert refused(registry.claim_status, "claim-9") == "unknown_claim"
    assert refused(registry.record_calibration, calibration("cal-9", "claim-9")) == "unknown_claim"
    registry.record_calibration(calibration())
    registry.register_claim(claim("claim-2", "cal-1b"))
    assert refused(registry.record_calibration, calibration("cal-1", "claim-2")) == "binding_mismatch"
    assert refused(registry.record_calibration, calibration()) == "second_calibration_record"
    assert refused(registry.supply_beacon_output, BeaconOutput("cal-9", "beacon", "round-7", "ab" * 32, day(1))) \
        == "unknown_calibration_record"
    assert refused(registry.seed_of, "cal-1") == "no_seed"
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg", 1, ("claim-1",)))
    assert refused(registry.anchor_confirmatory_register, ConfirmatoryRegister("reg", 1, ())) == "register_immutable"


def test_a_calibration_record_id_used_by_another_claim_is_refused(registry: RegistrationRegistry, ledger: Ledger) -> None:
    registry.register_claim(claim())
    registry.register_claim(claim("claim-2", "cal-2"))
    ledger.append("calibration_record", "forged-calibration", calibration("cal-2", "claim-1").to_payload())
    assert refused(registry.record_calibration, calibration("cal-2", "claim-2")) == "calibration_record_exists"


def test_a_registry_on_a_ledger_that_never_stops_advancing_is_contended(registry: RegistrationRegistry,
                                                                        ledger: Ledger) -> None:
    def always_stale(*args: Any, **kwargs: Any) -> Record:
        raise Refusal("stale_head", "another writer")

    ledger.append = always_stale  # type: ignore[method-assign]
    assert refused(registry.commit_base_rate, BaseRate("RC-2", 0.1)) == "contended"


# the registry: two of a kind ------------------------------------------------------------------------------------------

def test_two_records_of_each_kind_have_distinct_ledger_identities(registry: RegistrationRegistry, ledger: Ledger,
                                                                  clock: ManualClock) -> None:
    registry.commit_base_rate(BaseRate("RC-2", 0.1))
    registry.register_arm_version(arm("B-1", "2026-01-02"))
    registry.correct_cutoff(CutoffCorrection("B-1", date(2026, 1, 3), "ev-1"))
    registry.correct_cutoff(CutoffCorrection("B-1", date(2026, 1, 4), "ev-2"))
    assert registry.arm_version("B-1").declared_cutoff == date(2026, 1, 4)
    for event_id in ("E-3", "E-4"):
        registry.log_candidate(CandidateEntry(f"cand-{event_id}", event_id, "src", day(1), "registered", "ok"))
    registry.register_cluster(registration([spec("E-3", "C-2")], "C-2"))
    registry.register_cluster(registration([spec("E-4", "C-3")], "C-3"))
    registry.request_void(VoidRequest("v-1", "E-1", "why"))
    registry.request_void(VoidRequest("v-2", "E-1", "why"))
    registry.register_claim(claim())
    registry.register_claim(claim("claim-2", "cal-2"))
    registry.record_calibration(calibration())
    registry.record_calibration(calibration("cal-2", "claim-2"))
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(12))
    _, seed_1 = registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))
    _, seed_2 = registry.supply_beacon_output(BeaconOutput("cal-2", "beacon", "round-7", "ab" * 32, day(12)))
    assert (registry.seed_of("cal-1"), registry.seed_of("cal-2")) == (seed_1, seed_2) and seed_1 != seed_2
    clock.set(day(21))
    for event_id in ("E-1", "E-2"):
        for arm_id, version in (("FULL", "FULL-1"), ("A", "A-1")):
            registry.submit_forecast(forecast(event_id, arm_id=arm_id, version=version))
    kinds = [r.kind for r in ledger.records()]
    assert kinds.count("void_request") == 2 and kinds.count("forecast") == 4 and kinds.count("base_rate") == 2


def test_forecasts_in_two_slots_and_a_resubmission_after_the_window_are_distinct(ledger: Ledger,
                                                                                 clock: ManualClock) -> None:
    registry = RegistrationRegistry(ledger)
    registry.register_arm_version(arm("A-1", "2026-01-05"))
    registry.register_arm_version(arm("DESIGN_C-1", "2026-01-01"))
    registry.register_arm_version(arm("FULL-1", "2026-01-03"))
    registry.commit_base_rate(BaseRate("RC-1", 0.2))
    registry.log_candidate(CandidateEntry("cand", "S-1", "src", day(1), "registered", "ok"))
    clock.set(day(10))
    registry.register_cluster(registration([spec("S-1", slots=["primary", "revision"])]))
    clock.set(day(20))  # the window opens at day 20: a receipt at the open fills the slot
    registry.submit_forecast(forecast("S-1"))
    registry.submit_forecast(forecast("S-1", slot="revision"))
    clock.set(day(41))
    registry.submit_forecast(forecast("S-1", arm_id="A", version="A-1"))  # outside the window: kept, fills nothing
    registry.submit_forecast(forecast("S-1", arm_id="A", version="A-1", point=0.5))  # and again: another record
    states = registry.slot_states("S-1")
    assert states == (
        SlotState("S-1", "A", "primary", "abstention"), SlotState("S-1", "A", "revision", "abstention"),
        SlotState("S-1", "DESIGN_C", "primary", "baseline", None, 0.2),
        SlotState("S-1", "DESIGN_C", "revision", "baseline", None, 0.2),
        SlotState("S-1", "FULL", "primary", "filled", states[4].forecast_record_id, 0.3),
        SlotState("S-1", "FULL", "revision", "filled", states[5].forecast_record_id, 0.3),
    )
    records = {r.record_id for r in ledger.records() if r.kind == "forecast"}
    assert states[4].forecast_record_id in records and states[5].forecast_record_id in records
    assert states[4].forecast_record_id != states[5].forecast_record_id and len(records) == 4


# the consumption closure ----------------------------------------------------------------------------------------------

def test_a_correction_after_registration_withdraws_every_consumer_of_a_shared_input(ledger: Ledger,
                                                                                    clock: ManualClock) -> None:
    registry = RegistrationRegistry(ledger)
    registry.register_arm_version(arm("BASE-1", "2026-01-01"))
    registry.register_arm_version(arm("LEFT-1", "2026-01-01", ["BASE-1"]))
    registry.register_arm_version(arm("RIGHT-1", "2026-01-01", ["BASE-1"]))
    registry.register_arm_version(arm("FULL-1", "2026-01-01", ["LEFT-1", "RIGHT-1"]))  # a diamond over BASE-1
    registry.register_arm_version(arm("DESIGN_C-1", "2026-01-01"))
    registry.register_arm_version(arm("OTHER-1", "2026-01-01"))
    registry.commit_base_rate(BaseRate("RC-1", 0.2))
    registry.log_candidate(CandidateEntry("cand", "E-1", "src", day(1), "registered", "ok"))
    clock.set(day(10))
    registry.register_cluster(registration([spec("E-1")], arms={"FULL": "FULL-1", "DESIGN_C": "DESIGN_C-1",
                                                               "OTHER": "OTHER-1"}))
    _, registered = registry.correct_cutoff(CutoffCorrection("BASE-1", date(2026, 1, 2), "ev-1"))
    assert registered is True  # registered under through FULL-1, LEFT-1 and RIGHT-1
    _, other = registry.correct_cutoff(CutoffCorrection("OTHER-1", date(2026, 1, 2), "ev-2"))
    assert other is True
    for version in ("BASE-1", "LEFT-1", "RIGHT-1", "FULL-1", "OTHER-1"):  # both withdrawals hold
        assert refused(registry.register_arm_version, arm(f"NEW{version}", "2026-01-01", [version])) \
            == "arm_version_withdrawn"
