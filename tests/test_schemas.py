"""Structural schema checks of ``17`` section 3 item 1: T-29, T-22 (schema part), F-04, F-19, F-27 (e_i and effective
cutoff), RC-112, RC-98."""
from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cpe.errors import Refusal
from cpe.schemas import ArmVersion, Capability, ClusterRecord, EventSpec, Forecast, ResearchOutput, effective_cutoff
from cpe.schemas.forecast import JevRecord

HEX = "ab" * 32


def predicate_payload() -> dict[str, Any]:
    return {
        "source": "statutory-calendar", "record_selector": "release/2026-Q1", "field": "published", "comparator": "eq",
        "value": True, "not_before": "2026-03-01T00:00:00.000000Z", "not_after": "2026-03-31T00:00:00.000000Z",
    }


def event_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "event_id": "E-1", "cluster_id": "C-1", "predicate_kind": "milestone-deadline", "predicate": predicate_payload(),
        "latency_window_seconds": 864000, "issuance_open": "2026-02-01T00:00:00.000000Z",
        "issuance_close": "2026-02-10T00:00:00.000000Z", "evidence_cutoff": "2026-02-09T00:00:00.000000Z",
        "reference_class_id": "RC-releases",
    }
    payload.update(overrides)
    return payload


def forecast_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "event_id": "E-1", "arm_id": "FULL", "slot_id": "primary", "arm_version_id": "FULL-v1", "point": 0.4,
        "low": 0.3, "high": 0.5, "prompt_hash": HEX, "model_hash": HEX, "evidence_ids": ["ev-1"],
    }
    payload.update(overrides)
    return payload


def test_event_spec_round_trip_and_derived_times() -> None:
    spec = EventSpec.from_payload(event_payload())
    assert EventSpec.from_payload(spec.to_payload()) == spec
    assert spec.earliest_knowable_bound == spec.predicate.not_before
    assert spec.logical_finality.isoformat() == "2026-04-10T00:00:00+00:00"
    assert spec.scoring_slots == ("primary",) and spec.primary_slot == "primary"


@pytest.mark.parametrize("missing", ["predicate_kind", "cluster_id"])
def test_t29_event_spec_without_predicate_kind_or_cluster_id_is_refused(missing: str) -> None:
    payload = event_payload()
    del payload[missing]
    with pytest.raises(Refusal) as refusal:
        EventSpec.from_payload(payload)
    assert refusal.value.reason == "missing_field"


def test_f19_free_text_predicate_is_refused_by_the_typed_grammar() -> None:
    with pytest.raises(Refusal) as refusal:
        EventSpec.from_payload(event_payload(predicate="potentially excellent"))
    assert refusal.value.reason == "not_a_mapping"
    with pytest.raises(Refusal):
        EventSpec.from_payload(event_payload(predicate={**predicate_payload(), "comparator": "looks-like"}))


def test_unknown_event_field_is_refused() -> None:
    with pytest.raises(Refusal) as refusal:
        EventSpec.from_payload(event_payload(outcome="YES"))
    assert refusal.value.reason == "unknown_field"


def test_terminal_falsifier_declares_its_observable_time_and_sets_e_i(
) -> None:
    with pytest.raises(Refusal):
        EventSpec.from_payload(event_payload(predicate_kind="terminal-falsifier"))
    spec = EventSpec.from_payload(event_payload(
        predicate_kind="terminal-falsifier", falsifier_observable_from="2026-02-15T00:00:00.000000Z",
        issuance_close="2026-02-10T00:00:00.000000Z"))
    assert spec.earliest_knowable_bound.isoformat() == "2026-02-15T00:00:00+00:00"
    with pytest.raises(Refusal) as refusal:
        EventSpec.from_payload(event_payload(falsifier_observable_from="2026-02-15T00:00:00.000000Z"))
    assert refusal.value.reason == "unknown_field"


def test_issuance_window_must_close_before_the_earliest_knowable_bound() -> None:
    with pytest.raises(Refusal) as refusal:
        EventSpec.from_payload(event_payload(issuance_close="2026-03-02T00:00:00.000000Z",
                                             evidence_cutoff="2026-03-01T00:00:00.000000Z"))
    assert refusal.value.reason == "invalid_window"
    with pytest.raises(Refusal):
        EventSpec.from_payload(event_payload(evidence_cutoff="2026-02-11T00:00:00.000000Z"))


def test_several_slots_need_a_named_primary_slot() -> None:
    with pytest.raises(Refusal):
        EventSpec.from_payload(event_payload(scoring_slots=["primary", "revision-1"]))
    spec = EventSpec.from_payload(event_payload(scoring_slots=["primary", "revision-1"], primary_slot="primary"))
    assert spec.scoring_slots == ("primary", "revision-1")
    with pytest.raises(Refusal):
        EventSpec.from_payload(event_payload(scoring_slots=["a", "b"], primary_slot="c"))


def test_cluster_record_requires_members_and_void_declarations_inside_them() -> None:
    record = ClusterRecord.from_payload({"cluster_id": "C-1", "member_event_ids": ["E-1"]})
    assert record.pre_declared_void == ()
    with pytest.raises(Refusal):
        ClusterRecord.from_payload({"cluster_id": "C-1", "member_event_ids": []})
    with pytest.raises(Refusal):
        ClusterRecord.from_payload({"cluster_id": "C-1", "member_event_ids": ["E-1"], "pre_declared_void": ["E-9"]})


def test_t22_interval_only_and_point_outside_interval_are_refused() -> None:
    payload = forecast_payload()
    del payload["point"]
    with pytest.raises(Refusal) as refusal:
        Forecast.from_payload(payload)
    assert refusal.value.reason == "missing_field"
    with pytest.raises(Refusal) as refusal:
        Forecast.from_payload(forecast_payload(point=0.9))
    assert refusal.value.reason == "interval_disorder"


@pytest.mark.parametrize("bad", [{"point": float("nan")}, {"low": 0.8, "high": 0.2}, {"low": 1.2, "high": 1.3, "point": 1.25},
                                 {"point": True}, {"point": "0.4"}])
def test_f13_non_finite_reversed_and_out_of_range_forecasts_are_refused(bad: dict[str, Any]) -> None:
    with pytest.raises(Refusal):
        Forecast.from_payload(forecast_payload(**bad))


def test_rc112_a_forecast_carrying_a_cutoff_is_refused() -> None:
    with pytest.raises(Refusal) as refusal:
        Forecast.from_payload(forecast_payload(cutoff="2026-02-28"))
    assert refusal.value.reason == "forecast_carries_cutoff"


def test_forecast_round_trip_keeps_the_caller_claim_apart() -> None:
    forecast = Forecast.from_payload(forecast_payload(claimed_issued_at="2020-01-01T00:00:00.000000Z"))
    assert Forecast.from_payload(forecast.to_payload()) == forecast
    assert forecast.claimed_issued_at is not None and forecast.claimed_issued_at.year == 2020


@given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=3, max_size=3))
def test_any_ordered_triple_is_accepted_and_any_disordered_one_refused(values: list[float]) -> None:
    low, point, high = sorted(values)
    assert Forecast.from_payload(forecast_payload(low=low, point=point, high=high)).point == point
    if low < high:
        with pytest.raises(Refusal):
            Forecast.from_payload(forecast_payload(low=high, point=point, high=low))


def arm(version_id: str, cutoff: str, consumes: list[str]) -> ArmVersion:
    return ArmVersion.from_payload({
        "arm_version_id": version_id, "arm_id": version_id.split("-")[0], "forecaster_id": "f", "forecaster_version": "1",
        "declared_cutoff": cutoff, "cutoff_evidence_id": "ev-cutoff", "cutoff_claim_label": "UNVERIFIED",
        "consumes": consumes,
    })


def test_f27_composite_effective_cutoff_is_the_latest_over_every_input() -> None:
    versions = {v.arm_version_id: v for v in [
        arm("A-1", "2026-01-20", []), arm("B-1", "2026-01-10", []), arm("C-1", "2026-01-08", []),
        arm("JEV-1", "2026-01-05", []), arm("FULL-1", "2026-01-12", ["A-1", "B-1", "C-1", "JEV-1"]),
        arm("COMMITTEE-1", "2026-01-12", ["A-1", "B-1", "C-1"]), arm("A3-1", "2026-01-12", ["A-1"]),
    ]}
    for version_id in ("FULL-1", "COMMITTEE-1", "A3-1", "A-1"):
        assert effective_cutoff(version_id, versions) == date(2026, 1, 20)
    assert effective_cutoff("B-1", versions) == date(2026, 1, 10)


def test_effective_cutoff_refuses_unknown_inputs_and_cycles() -> None:
    versions = {"X-1": arm("X-1", "2026-01-01", ["Y-1"]), "Y-1": arm("Y-1", "2026-01-01", ["X-1"])}
    with pytest.raises(Refusal) as refusal:
        effective_cutoff("X-1", versions)
    assert refusal.value.reason == "invalid_arm_graph"
    with pytest.raises(Refusal) as refusal:
        effective_cutoff("Z-1", {"Z-1": arm("Z-1", "2026-01-01", ["missing"])})
    assert refusal.value.reason == "unknown_arm_version"


def test_rc98_cutoff_claim_label_is_fixed_to_unverified() -> None:
    payload = arm("A-1", "2026-01-20", []).to_payload()
    payload["cutoff_claim_label"] = "VERIFIED"
    with pytest.raises(Refusal) as refusal:
        ArmVersion.from_payload(payload)
    assert refusal.value.reason == "invalid_label"


def test_f04_research_output_with_non_hex_digest_is_refused() -> None:
    payload = {"arm_id": "FULL", "event_id": "E-1", "forecast": forecast_payload(), "reasoning_digest": "z" * 64,
               "evidence_ids": []}
    with pytest.raises(Refusal) as refusal:
        ResearchOutput.from_payload(payload)
    assert refusal.value.reason == "invalid_digest"
    payload["reasoning_digest"] = HEX
    assert ResearchOutput.from_payload(payload).reasoning_digest == HEX
    with pytest.raises(Refusal):
        ResearchOutput.from_payload({**payload, "arm_id": "OTHER"})


def capability_payload() -> dict[str, Any]:
    return {"capability": "GATE_PROMOTE", "environment": "offline-synthetic", "release_digest": HEX,
            "evidence_digest": HEX, "epoch": 3, "nonce": "n-1", "expiry": "2026-06-01T00:00:00.000000Z",
            "signature": "sig"}


def test_capability_signed_bytes_cover_the_whole_tuple_and_refuse_added_fields() -> None:
    capability = Capability.from_payload(capability_payload())
    reordered = Capability.from_payload(dict(reversed(list(capability_payload().items()))))
    assert capability.signed_bytes() == reordered.signed_bytes()
    assert b"signature" not in capability.signed_bytes()
    with pytest.raises(Refusal) as refusal:
        Capability.from_payload({**capability_payload(), "scope": "all"})
    assert refusal.value.reason == "unknown_field"
    with pytest.raises(Refusal):
        Capability.from_payload({**capability_payload(), "epoch": "3"})


def test_jev_record_round_trip() -> None:
    record = JevRecord.from_payload({"jev_record_id": "J-1", "event_id": "E-1", "inputs_digest": HEX,
                                     "result_positive": {"score": 0.7}, "result_negative": {"score": 0.2},
                                     "model_hash": HEX, "routing_result": "route-A", "cost": 0.01})
    assert JevRecord.from_payload(record.to_payload()) == record
    with pytest.raises(Refusal):
        JevRecord.from_payload({**record.to_payload(), "cost": -1})
