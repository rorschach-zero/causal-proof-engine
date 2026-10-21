"""Mutation testing, ``cpe/schemas``, ``cpe/clock``, ``cpe/errors`` and ``cpe/validation``: tests that kill mutants
the suite let survive at ac4c640 (``research/19`` section "Mutation testing"). They pin the reason code of every
field refusal, the inclusive bounds of the event windows, the round trip of the optional fields, the canonical UTC
form of every accepted time and the identity of an issuance decision."""
from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Any

import pytest

from cpe.clock import ManualClock, format_timestamp, parse_timestamp
from cpe.errors import Refusal
from cpe.schemas import (
    ArmVersion,
    ClusterRecord,
    EventSpec,
    Forecast,
    JevRecord,
    ResearchOutput,
    ResolutionPredicate,
    ResolutionTimestamps,
)
from cpe.schemas.common import (
    require_date,
    require_identifier_tuple,
    require_non_negative_int,
    require_non_negative_number,
    require_probability,
)
from cpe.schemas.event import require_comparator, require_predicate_kind
from cpe.validation import check_issuance
from tests.test_input_validation import PROVIDERS, VERSIONS, jev, output
from tests.test_schemas import HEX, event_payload, forecast_payload

PLUS_TWO = timezone(timedelta(hours=2))


def refused(call: object, *args: object, **kwargs: object) -> str:
    assert callable(call)
    with pytest.raises(Refusal) as refusal:
        call(*args, **kwargs)
    return refusal.value.reason


class NoOffset(tzinfo):
    """A time zone object that names no offset: a time with it is naive in all but name."""

    def utcoffset(self, moment: datetime | None) -> timedelta | None:
        return None

    def dst(self, moment: datetime | None) -> timedelta | None:
        return None

    def tzname(self, moment: datetime | None) -> str | None:
        return None


# clock and errors ---------------------------------------------------------------------------------------------------

def test_times_are_stored_in_utc_and_a_zone_without_offset_is_naive() -> None:
    local = datetime(2026, 1, 1, 12, tzinfo=PLUS_TWO)
    assert format_timestamp(local) == "2026-01-01T10:00:00.000000Z"
    nameless = datetime(2026, 1, 1, tzinfo=NoOffset())
    assert refused(format_timestamp, nameless) == "naive_timestamp"
    clock = ManualClock(local)
    assert clock.now().tzinfo is timezone.utc and clock.now() == local
    clock.set(datetime(2026, 1, 2, 12, tzinfo=PLUS_TWO))
    assert clock.now().tzinfo is timezone.utc
    assert refused(clock.set, nameless) == "naive_timestamp"
    assert refused(ManualClock, datetime(2026, 1, 1)) == "naive_timestamp"
    assert refused(parse_timestamp, 7) == "invalid_timestamp"
    assert refused(parse_timestamp, "2026-13-01T00:00:00.000000Z") == "invalid_timestamp"


def test_a_refusal_reads_reason_and_detail() -> None:
    assert str(Refusal("reason", "detail")) == "reason: detail" and str(Refusal("reason")) == "reason"
    assert Refusal("reason").detail == ""


# common validators --------------------------------------------------------------------------------------------------

def test_field_validators_refuse_by_name_at_their_bounds() -> None:
    assert refused(require_identifier_tuple, "a", "f", allow_empty=True) == "invalid_list"
    assert refused(require_identifier_tuple, [], "f", allow_empty=False) == "empty_list"
    assert refused(require_identifier_tuple, ["a", "a"], "f", allow_empty=True) == "duplicate_identifier"
    assert refused(require_probability, "0.5", "p") == "invalid_probability"
    assert refused(require_non_negative_number, True, "n") == "invalid_number"
    assert refused(require_non_negative_number, "1", "n") == "invalid_number"
    assert require_non_negative_int(0, "i") == 0
    assert refused(require_non_negative_int, -1, "i") == "invalid_integer"
    assert refused(require_date, 20260101, "d") == "invalid_date"
    assert refused(require_date, "2026-02-30", "d") == "invalid_date"
    assert refused(require_predicate_kind, "other") == "invalid_choice"
    assert refused(require_comparator, "approx") == "invalid_choice"


# event schema ------------------------------------------------------------------------------------------------------

def spec_from(**changes: Any) -> EventSpec:
    return EventSpec.from_payload({**event_payload(), **changes})


def test_event_windows_are_inclusive_and_refusals_are_named() -> None:
    base = spec_from()
    predicate = base.predicate
    assert refused(replace, predicate, not_after=predicate.not_before) == "invalid_window"
    assert refused(replace, predicate, comparator="in", value=[]) == "invalid_predicate_value"
    assert refused(replace, predicate, comparator="in", value="x") == "invalid_predicate_value"
    assert refused(replace, predicate, comparator="eq", value=[1]) == "invalid_predicate_value"
    assert refused(ResolutionPredicate.from_payload, {**predicate.to_payload(), "value": {"a": 1}}) \
        == "invalid_predicate_value"
    at_open = replace(base, evidence_cutoff=base.issuance_open)
    at_close = replace(base, evidence_cutoff=base.issuance_close)
    assert at_open.evidence_cutoff == at_open.issuance_open and at_close.evidence_cutoff == at_close.issuance_close
    assert refused(replace, base, evidence_cutoff=base.issuance_close + timedelta(seconds=1)) == "invalid_window"
    assert refused(replace, base, scoring_slots=(), primary_slot="primary") == "invalid_slots"
    assert refused(replace, base, primary_slot="other") == "invalid_slots"
    assert refused(replace, base, predicate_kind="terminal-falsifier") == "missing_field"
    assert refused(EventSpec.from_payload, {**event_payload(), "scoring_slots": []}) == "empty_list"
    assert refused(EventSpec.from_payload, {**event_payload(), "scoring_slots": ["a", "b"]}) == "missing_field"


def test_finality_beyond_the_representable_range_is_refused() -> None:
    far = datetime(9999, 12, 31, tzinfo=timezone.utc)
    base = spec_from()
    late = replace(base.predicate, not_after=far)
    assert refused(replace, base, predicate=late, latency_window_seconds=2 * 86400) == "invalid_window"


def test_optional_event_fields_round_trip() -> None:
    falsifier = spec_from(predicate_kind="terminal-falsifier",
                          falsifier_observable_from=event_payload()["predicate"]["not_before"])
    assert EventSpec.from_payload(falsifier.to_payload()) == falsifier
    assert "falsifier_observable_from" not in spec_from().to_payload()
    receipt_only = ResolutionTimestamps.from_payload({"receipt": "2026-01-01T00:00:00.000000Z"})
    assert receipt_only.receipt == datetime(2026, 1, 1, tzinfo=timezone.utc) and receipt_only.occurrence is None
    assert refused(ResolutionTimestamps.from_payload, {}) == "missing_field"


def test_a_cluster_may_pre_declare_every_member_void() -> None:
    whole = ClusterRecord("C", ("E1", "E2"), ("E1", "E2"))
    assert ClusterRecord.from_payload(whole.to_payload()) == whole
    assert refused(ClusterRecord, "C", ("E1",), ("E2",)) == "invalid_cluster"
    assert refused(ClusterRecord.from_payload, {"cluster_id": "C", "member_event_ids": []}) == "empty_list"


# forecast schemas ---------------------------------------------------------------------------------------------------

def test_forecast_schemas_refuse_by_name_and_round_trip() -> None:
    assert refused(Forecast.from_payload, {**forecast_payload(), "knowledge_cutoff": "2026-01-01"}) \
        == "forecast_carries_cutoff"
    version = ArmVersion("A-1", "A", "f", "2", date(2026, 1, 1), "ev", ())
    assert ArmVersion.from_payload(version.to_payload()) == version
    assert refused(replace, version, cutoff_claim_label="VERIFIED") == "invalid_label"
    assert refused(replace, version, consumes=("A-1",)) == "invalid_arm_graph"
    record = JevRecord("j", "E", HEX, {"p": 1}, {"n": 0}, HEX, "route", 0.5)
    assert JevRecord.from_payload(record.to_payload()) == record


def test_a_research_output_keeps_its_claimed_production_time() -> None:
    payload = {**output("P-A"), "claimed_produced_at": "2026-01-01T00:00:00.000000Z"}
    parsed = ResearchOutput.from_payload(payload)
    assert parsed.claimed_produced_at == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert ResearchOutput.from_payload(parsed.to_payload()) == parsed
    assert refused(replace, parsed, event_id="other") == "inconsistent_output"


# issuance -----------------------------------------------------------------------------------------------------------

def test_every_issuance_decision_names_its_event_and_each_problem_its_subject() -> None:
    outputs = [output(p) for p in PROVIDERS]
    assert check_issuance("E-1", VERSIONS, outputs, jev(), slot_id="primary").event_id == "E-1"
    held = check_issuance("E-1", VERSIONS, outputs[:2], jev(), slot_id="primary")
    assert (held.event_id, held.status) == ("E-1", "held")
    wrong = check_issuance("E-1", VERSIONS, [*outputs[:2], output(PROVIDERS[2], "E-2")], jev(),
                           slot_id="primary")
    assert (wrong.event_id, wrong.status) == ("E-1", "rejected")
    assert [(p.reason, p.subject) for p in wrong.problems if p.reason == "wrong_event"] == [("wrong_event", "outputs[2]")]
    bad = check_issuance("E-1", VERSIONS, [{"arm_id": 1}], {"jev_record_id": 1}, slot_id="primary")
    assert all(p.detail for p in bad.problems if p.subject in ("outputs[0]", "jev"))
    assert refused(check_issuance, "E-1", {"P-A": "v"}, outputs, jev(), slot_id="primary") == "invalid_provider_set"


def test_duplicate_scoring_slots_are_refused_on_direct_construction() -> None:
    assert refused(replace, spec_from(), scoring_slots=("a", "a"), primary_slot="a") == "invalid_slots"


def test_times_are_converted_to_utc_whatever_the_host_zone(monkeypatch: pytest.MonkeyPatch) -> None:
    import time
    monkeypatch.setenv("TZ", "Asia/Tokyo")
    time.tzset()
    try:
        local = datetime(2026, 1, 1, 12, tzinfo=PLUS_TWO)
        assert format_timestamp(local) == "2026-01-01T10:00:00.000000Z"
        clock = ManualClock(local)
        assert clock.now().tzinfo is timezone.utc
        clock.set(local)
        assert clock.now().tzinfo is timezone.utc
    finally:
        monkeypatch.undo()
        time.tzset()
