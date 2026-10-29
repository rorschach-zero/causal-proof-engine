"""Pre-registration registry: T-37 retained parts, T-17 and T-19 retained parts, T-06 slot case, F-24 G, F-27
registration refusals, RC-75, RC-78, RC-85, RC-87, RC-96, RC-109, RC-138, RC-150, and ``18`` M-1 (i), M-5, M-8."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
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
    VoidRequest,
    derive_seed,
)
from cpe.schemas import ArmVersion, ClusterRecord, EventSpec, Forecast
from tests.test_schemas import HEX

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def day(n: float) -> datetime:
    return BASE + timedelta(days=n)


def ts(n: float) -> str:
    return day(n).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def arm(version_id: str, cutoff: str, consumes: list[str] | None = None) -> ArmVersion:
    return ArmVersion.from_payload({
        "arm_version_id": version_id, "arm_id": version_id.rsplit("-", 1)[0], "forecaster_id": "f",
        "forecaster_version": version_id.rsplit("-", 1)[1], "declared_cutoff": cutoff, "cutoff_evidence_id": "ev",
        "cutoff_claim_label": "UNVERIFIED", "consumes": consumes or [],
    })


def spec(event_id: str, cluster_id: str = "C-1", not_before: float = 50, kind: str = "milestone-deadline",
         falsifier_from: float | None = None, slots: list[str] | None = None,
         issuance: tuple[float, float] = (20, 40)) -> EventSpec:
    payload: dict[str, Any] = {
        "event_id": event_id, "cluster_id": cluster_id, "predicate_kind": kind,
        "predicate": {"source": "src", "record_selector": "sel", "field": "f", "comparator": "eq", "value": True,
                      "not_before": ts(not_before), "not_after": ts(100)},
        "latency_window_seconds": 864000, "issuance_open": ts(issuance[0]), "issuance_close": ts(issuance[1]),
        "evidence_cutoff": ts(issuance[1] - 1), "reference_class_id": "RC-1",
    }
    if falsifier_from is not None:
        payload["falsifier_observable_from"] = ts(falsifier_from)
    if slots:
        payload["scoring_slots"], payload["primary_slot"] = slots, slots[0]
    return EventSpec.from_payload(payload)


def registration(events: list[EventSpec], cluster_id: str = "C-1", void: list[str] | None = None,
                 arms: dict[str, str] | None = None) -> ClusterRegistration:
    cluster = ClusterRecord(cluster_id, tuple(e.event_id for e in events), tuple(void or []))
    return ClusterRegistration(cluster, tuple(events), arms or {"FULL": "FULL-1", "A": "A-1", "DESIGN_C": "DESIGN_C-1"},
                               "DESIGN_C")


def forecast(event_id: str, arm_id: str = "FULL", version: str = "FULL-1", point: float = 0.3, slot: str = "primary") -> Forecast:
    return Forecast.from_payload({"event_id": event_id, "arm_id": arm_id, "slot_id": slot, "arm_version_id": version,
                                  "point": point, "low": point, "high": point, "prompt_hash": HEX, "model_hash": HEX,
                                  "evidence_ids": []})


@pytest.fixture
def clock() -> ManualClock:
    return ManualClock(day(1))


@pytest.fixture
def ledger(tmp_path: Path, clock: ManualClock) -> Ledger:
    return Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())


@pytest.fixture
def registry(ledger: Ledger, clock: ManualClock) -> RegistrationRegistry:
    r = RegistrationRegistry(ledger)
    r.register_arm_version(arm("A-1", "2026-01-05"))
    r.register_arm_version(arm("DESIGN_C-1", "2026-01-01"))
    r.register_arm_version(arm("FULL-1", "2026-01-03", ["A-1"]))
    r.commit_base_rate(BaseRate("RC-1", 0.2))
    for event_id in ("E-1", "E-2"):
        r.log_candidate(CandidateEntry(f"cand-{event_id}", event_id, "src", day(1), "registered", "predicate match"))
    clock.set(day(10))
    r.register_cluster(registration([spec("E-1"), spec("E-2")]))
    return r


def test_arm_versions_are_immutable_and_name_registered_inputs(ledger: Ledger) -> None:
    r = RegistrationRegistry(ledger)
    r.register_arm_version(arm("A-1", "2026-01-05"))
    with pytest.raises(Refusal) as immutable:
        r.register_arm_version(arm("A-1", "2026-01-06"))
    assert immutable.value.reason == "arm_version_immutable"
    with pytest.raises(Refusal):
        r.register_arm_version(arm("FULL-1", "2026-01-03", ["B-1"]))


def test_t37_registration_needs_a_prior_candidate_entry_and_an_entry_after_a_forecast_is_refused(
    registry: RegistrationRegistry, clock: ManualClock
) -> None:
    with pytest.raises(Refusal) as refusal:
        registry.register_cluster(registration([spec("E-9", cluster_id="C-9")], cluster_id="C-9"))
    assert refusal.value.reason == "no_candidate_entry"
    registry.log_candidate(CandidateEntry("cand-E-9", "E-9", "src", day(2), "sampled-out", "draw"))
    with pytest.raises(Refusal) as refusal:
        registry.register_cluster(registration([spec("E-9", cluster_id="C-9")], cluster_id="C-9"))
    assert refusal.value.reason == "candidate_not_registered"
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1"))
    with pytest.raises(Refusal) as refusal:
        registry.log_candidate(CandidateEntry("cand-E-1-b", "E-1", "src", day(21), "registered", "again"))
    assert refusal.value.reason == "candidate_after_forecast"
    assert registry.candidate_counts() == {"registered": {"predicate match": 2}, "sampled-out": {"draw": 1}}


def test_t17_t19_membership_and_void_set_are_fixed_at_registration(registry: RegistrationRegistry, clock: ManualClock) -> None:
    with pytest.raises(Refusal) as refusal:
        registry.register_cluster(registration([spec("E-1"), spec("E-2"), spec("E-3")]))
    assert refusal.value.reason == "cluster_immutable"
    before = registry.slot_states("E-1")
    registry.request_void(VoidRequest("vr-1", "E-1", "please"))
    assert registry.slot_states("E-1") == before and registry.event("E-1").event_id == "E-1"
    with pytest.raises(Refusal):
        registry.request_void(VoidRequest("vr-2", "E-9", "unknown"))
    kinds = [r.kind for r in registry._ledger.records()]
    assert kinds.count("void_request") == 1


def test_rc138_registration_refusals_against_e_i_cutoff_window_and_base_rate(registry: RegistrationRegistry, clock: ManualClock) -> None:
    registry.log_candidate(CandidateEntry("cand-F", "F-1", "src", day(2), "registered", "ok"))
    # RC-138: a registration record written after the falsifier became observable (e_i 15, record at 16)
    early_falsifier = spec("F-1", "C-F", not_before=20, kind="terminal-falsifier", falsifier_from=15, issuance=(12, 14))
    clock.set(day(16))
    with pytest.raises(Refusal) as refusal:
        registry.register_cluster(registration([early_falsifier], "C-F"))
    assert refusal.value.reason == "registration_after_e_i"
    clock.set(day(10))
    with pytest.raises(Refusal) as refusal:  # F-27: a cutoff at or after e_i
        registry.register_cluster(registration([spec("F-1", "C-F")], "C-F",
                                               arms={"FULL": "FULL-1", "LATE": "LATE-1", "DESIGN_C": "DESIGN_C-1"}))
    assert refusal.value.reason == "unknown_arm_version"
    registry.register_arm_version(arm("LATE-1", "2026-02-28"))
    with pytest.raises(Refusal) as refusal:
        registry.register_cluster(registration([spec("F-1", "C-F", not_before=50)], "C-F",
                                               arms={"FULL": "FULL-1", "LATE": "LATE-1", "DESIGN_C": "DESIGN_C-1"}))
    assert refusal.value.reason == "cutoff_after_e_i"
    clock.set(day(25))
    with pytest.raises(Refusal) as refusal:  # RC-87: the issuance window must open at or after the record
        registry.register_cluster(registration([spec("F-1", "C-F")], "C-F"))
    assert refusal.value.reason == "issuance_before_registration"
    clock.set(day(10))
    other = EventSpec.from_payload({**spec("F-1", "C-F").to_payload(), "reference_class_id": "RC-none"})
    with pytest.raises(Refusal) as refusal:  # F-24 G member 2
        registry.register_cluster(registration([other], "C-F"))
    assert refusal.value.reason == "no_base_rate"


def test_rc150_cutoff_correction_before_and_after_the_first_registration(registry: RegistrationRegistry, clock: ManualClock) -> None:
    registry.register_arm_version(arm("B-1", "2026-01-02"))
    _, registered_under = registry.correct_cutoff(CutoffCorrection("B-1", date(2026, 1, 4), "ev-2"))
    assert registered_under is False
    _, registered_under = registry.correct_cutoff(CutoffCorrection("FULL-1", date(2026, 1, 4), "ev-3"))
    assert registered_under is True
    with pytest.raises(Refusal):
        registry.correct_cutoff(CutoffCorrection("FULL-1", date(2026, 1, 5), "ev-4"))
    registry.log_candidate(CandidateEntry("cand-G", "G-1", "src", day(2), "registered", "ok"))
    with pytest.raises(Refusal) as refusal:
        registry.register_cluster(registration([spec("G-1", "C-G")], "C-G"))
    assert refusal.value.reason == "arm_version_withdrawn"


def test_forecast_submission_refusals_rc87_rc96_rc109_rc75(registry: RegistrationRegistry, clock: ManualClock) -> None:
    with pytest.raises(Refusal) as refusal:
        registry.submit_forecast(forecast("E-9"))
    assert refusal.value.reason == "before_registration"
    clock.set(day(21))
    for bad, reason in ((forecast("E-1", arm_id="DESIGN_C", version="DESIGN_C-1"), "baseline_not_submittable"),
                        (forecast("E-1", arm_id="Z"), "unknown_arm"),
                        (forecast("E-1", version="FULL-2"), "wrong_arm_version"),
                        (forecast("E-1", slot="revision-1"), "unknown_slot")):
        with pytest.raises(Refusal) as refusal:
            registry.submit_forecast(bad)
        assert refusal.value.reason == reason
    registry.submit_forecast(forecast("E-1", point=0.3))
    with pytest.raises(Refusal) as refusal:  # T-06 slot case: the second record for one slot is refused
        registry.submit_forecast(forecast("E-1", point=0.7))
    assert refusal.value.reason == "slot_occupied"
    clock.set(day(41))
    stored = registry.forecasts_of("E-1")
    assert len(stored) == 1 and stored[0].forecast.point == 0.3 and stored[0].receipt == day(21)


def test_f24_g_slot_states_abstention_at_close_and_baseline_from_base_rate(registry: RegistrationRegistry, clock: ManualClock) -> None:
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1", arm_id="A", version="A-1", point=0.4))
    open_states = {(s.arm_id, s.status) for s in registry.slot_states("E-1")}
    assert open_states == {("A", "filled"), ("FULL", "open"), ("DESIGN_C", "baseline")}
    with pytest.raises(Refusal) as refusal:
        registry.forecasts_for_baseline("E-1")
    assert refusal.value.reason == "read_before_close"
    clock.set(day(41))
    registry.submit_forecast(forecast("E-1", point=0.9))  # the late FULL submission is kept, labelled, never fills the slot
    states = {s.arm_id: s for s in registry.slot_states("E-1")}
    assert states["FULL"].status == "abstention" and states["A"].status == "filled"
    assert states["DESIGN_C"].status == "baseline" and states["DESIGN_C"].value == 0.2
    assert len(registry.forecasts_for_baseline("E-1")) == 2


def test_m8_a_source_listing_population_is_refused_and_claims_are_immutable(registry: RegistrationRegistry) -> None:
    claim = ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                 "period-balanced", ("DESIGN_C", "A"), ("L-1", "L-2"), "cal-1")
    registry.register_claim(claim)
    with pytest.raises(Refusal) as refusal:
        registry.register_claim(ClaimPreregistration("claim-2", "source_listing", "S-1", "holder", day(1), day(60), day(400),
                                                     "period-balanced", ("DESIGN_C",), ("L-1",), "cal-2"))
    assert refusal.value.reason == "non_confirmatory_population"
    with pytest.raises(Refusal) as immutable:
        registry.register_claim(claim)
    assert immutable.value.reason == "claim_immutable"  # not the reservation of its own record (pass 8)
    with pytest.raises(Refusal) as family:
        ClaimPreregistration("claim-3", "fixed_question_set", "Q", "h", day(1), day(60), day(400), "period-balanced",
                             ("DESIGN_C", "A"), ("L-1",), "cal-3")
    assert family.value.reason == "invalid_family"


def test_m1_binding_register_and_beacon_seed(registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    claim = ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                 "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1")
    registry.register_claim(claim)
    with pytest.raises(Refusal) as refusal:
        registry.record_calibration(CalibrationRecord("cal-X", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    assert refusal.value.reason == "binding_mismatch"
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    with pytest.raises(Refusal) as refusal:
        registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 2000, 0.01, "beacon", "round-7"))
    assert refusal.value.reason == "second_calibration_record"  # bound both ways, and the claim's second
    output = BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12))
    with pytest.raises(Refusal) as refusal:  # no anchor yet: the round cannot be after the record's anchor
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(9)))
    assert refusal.value.reason == "round_before_anchor"
    with pytest.raises(Refusal):
        registry.seed_of("cal-1")  # no draw before the round
    assert registry.claim_status("claim-1") == "exploratory"
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    assert registry.claim_status("claim-1") == "exploratory"  # listed, but the register is not anchored yet
    with pytest.raises(Refusal) as refusal:
        registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-2", 2, ("claim-1",)))
    assert refusal.value.reason == "register_immutable"
    clock.set(day(11))
    ledger.anchor()
    assert registry.claim_status("claim-1") == "confirmatory"
    # A round attested as published before both anchors is recorded and binds: issue #37, PR #48 reviews
    # 4352111655 and 4352111663 (tests/test_audit_pass3_followup.py).
    clock.set(day(12))
    with pytest.raises(Refusal) as refusal:
        registry.supply_beacon_output(BeaconOutput("cal-1", "other", "round-7", "ab" * 32, day(12)))
    assert refusal.value.reason == "wrong_beacon"
    _, seed = registry.supply_beacon_output(output)
    assert seed == derive_seed(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7").to_payload(), "ab" * 32)
    assert registry.seed_of("cal-1") == seed
    clock.set(day(13))
    with pytest.raises(Refusal) as refusal:
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "cd" * 32, day(13)))
    assert refusal.value.reason == "second_seed"
    registry.register_claim(ClaimPreregistration("claim-late", "fixed_question_set", "Q-1", "holder", day(1), day(60),
                                                 day(400), "period-balanced", ("DESIGN_C",), ("L-1",), "cal-late"))
    assert registry.claim_status("claim-late") == "exploratory"


def test_register_after_a_beacon_round_confers_nothing(registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    registry.register_claim(ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                                 "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1"))
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(12))
    registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))
    with pytest.raises(Refusal) as refusal:
        registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    assert refusal.value.reason == "register_after_beacon"
    assert registry.claim_status("claim-1") == "exploratory"


def test_a_register_anchored_after_the_round_is_refused_at_the_round(registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    registry.register_claim(ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                                 "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1"))
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    clock.set(day(11))
    ledger.anchor()
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(12))
    with pytest.raises(Refusal) as refusal:  # the register is written but not yet anchored before the round
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))
    assert refusal.value.reason == "register_not_anchored"
    clock.set(day(13))
    ledger.anchor()
    clock.set(day(14))
    with pytest.raises(Refusal):  # the named round was published before the register's anchor
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(12)))
    with pytest.raises(Refusal) as other_round:  # another round is not the one the record names
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-9", "ab" * 32, day(14)))
    assert other_round.value.reason == "wrong_round"


def test_state_is_replayed_byte_for_byte_from_the_ledger(tmp_path: Path, registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    clock.set(day(21))
    registry.submit_forecast(forecast("E-2", point=0.6))
    digest = ledger.state_digest()
    states = registry.slot_states("E-2")
    ledger.close()
    reopened = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    assert reopened.state_digest() == digest
    assert RegistrationRegistry(reopened).slot_states("E-2") == states
