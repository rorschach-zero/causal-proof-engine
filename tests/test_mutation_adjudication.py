"""Mutation testing, ``cpe/adjudication`` rules: tests that kill mutants the suite let survive at ac4c640
(``research/19`` section "Mutation testing"). They pin the boundaries of RC-77, RC-105 and RC-146 (an occurrence at
the deadline, a publication at finality, an occurrence at the lower bound), the deciding record and receipt of every
route, and the round trip of a stored adjudication."""
from __future__ import annotations

from dataclasses import replace

import pytest

from cpe.adjudication import adjudicate
from cpe.adjudication.records import SourceStatus
from cpe.adjudication.rules import (
    Adjudication,
    Defect,
    Incident,
    ReceivedRecord,
    check_record_is_final_enough,
    earliest_public_occurrence,
)
from cpe.errors import Refusal
from tests.test_adjudication import day, observation, record, rule, spec


def refused(call: object, *args: object) -> str:
    assert callable(call)
    with pytest.raises(Refusal) as refusal:
        call(*args)
    return refusal.value.reason


# the deadline, finality and the lower bound are inclusive ---------------------------------------------------------

def test_an_occurrence_at_the_deadline_is_timely() -> None:
    yes = adjudicate(spec(), rule(), [record("r", occurrence=100, published=101)], [], [], day(102))
    assert (yes.disposition, yes.deciding_record_id) == ("RESOLVED_YES", "r")
    no = adjudicate(spec("terminal-falsifier"), rule(), [record("f", occurrence=100, published=101)], [], [], day(102))
    assert (no.disposition, no.deciding_record_id) == ("RESOLVED_NO", "f")


def test_a_publication_at_finality_is_timely_and_a_receipt_at_finality_is_no_lag() -> None:
    at_finality = record("r", occurrence=95, published=110, observed=110, received=110)
    out = adjudicate(spec(), rule(), [at_finality], [], [], day(111))
    assert (out.disposition, out.deciding_record_id, out.incidents) == ("RESOLVED_YES", "r", ())


def test_adjudication_at_finality_reads_an_observation_made_at_finality() -> None:
    out = adjudicate(spec(), rule(), [], [observation(110)], [], day(110))
    assert out.disposition == "RESOLVED_NO" and out.knowable_at == day(110)


def test_a_no_published_at_the_deadline_is_final_and_one_before_it_is_not() -> None:
    check_record_is_final_enough(record("n", "not-occurred", published=100).record, spec(), rule())
    assert refused(check_record_is_final_enough, record("n", "not-occurred", published=99).record, spec(), rule()) \
        == "not_final"


def test_finality_of_a_no_reads_the_time_the_source_rule_evidences() -> None:
    evidenced_early_seen_late = record("n", "not-occurred", published=99, observed=101).record
    assert refused(check_record_is_final_enough, evidenced_early_seen_late, spec(), rule()) == "not_final"
    seen_early = record("n", "not-occurred", observed=99).record
    assert refused(check_record_is_final_enough, seen_early, spec(), rule(evidenced=False)) == "not_final"
    check_record_is_final_enough(replace(seen_early, first_observed_at=day(100)), spec(), rule(evidenced=False))
    check_record_is_final_enough(record("n", "not-occurred", observed=99).record, spec(), rule())  # no time evidenced
    assert refused(check_record_is_final_enough, replace(seen_early, source_id="other"), spec(), rule()) == "wrong_source"


def test_a_terminal_falsifier_counts_from_falsifier_observable_from() -> None:
    early = replace(spec("terminal-falsifier", issuance=(10, 20)), falsifier_observable_from=day(30))
    falsifier = record("f", occurrence=40, published=41)  # before not_before (50), after falsifier_observable_from
    out = adjudicate(early, rule(), [falsifier], [], [], day(42))
    assert (out.disposition, out.deciding_record_id) == ("RESOLVED_NO", "f")


def test_public_occurrences_at_the_bounds_set_knowable_at() -> None:
    at_lower = record("r", occurrence=50, published=60)
    assert earliest_public_occurrence(spec(), rule(public_act=True), [at_lower]) == (day(50), "r")
    at_deadline = record("f", occurrence=100, published=101)
    assert earliest_public_occurrence(spec("terminal-falsifier"), rule(public_act=True), [at_deadline]) == (day(100), "f")


# defects: which late records contradict a final disposition -------------------------------------------------------

def test_late_reports_at_the_bounds_are_defects_and_a_late_no_is_not() -> None:
    absence = [observation(110)]
    for occurrence in (50, 100):  # at the lower bound and at the deadline: timely occurrences, published late
        out = adjudicate(spec(), rule(), [record("late", occurrence=occurrence, published=115)], absence, [], day(116))
        assert out.disposition == "RESOLVED_NO" and [d.record_id for d in out.defects] == ["late"]
    late_no = record("late-no", "not-occurred", published=115, definitive=True)
    assert adjudicate(spec(), rule(), [late_no], absence, [], day(116)).defects == ()
    yes = adjudicate(spec("terminal-falsifier"), rule(), [record("after", occurrence=105, published=115)], absence, [],
                     day(116))
    assert yes.disposition == "RESOLVED_YES" and yes.defects == ()  # a falsifier after the deadline contradicts nothing
    stated_late = record("lateness", published=115, lateness=True)  # no occurrence time, lateness evidenced
    assert adjudicate(spec(), rule(), [stated_late], absence, [], day(116)).defects == ()


# the deciding record and its receipt on every route ----------------------------------------------------------------

def test_among_timely_deciding_records_the_earliest_knowable_decides_whatever_its_disposition() -> None:
    yes = record("yes", occurrence=90, published=91)
    no = record("definitive-no", "not-occurred", published=95, definitive=True)
    out = adjudicate(spec(), rule(), [no, yes], [], [], day(96))
    assert (out.disposition, out.deciding_record_id) == ("RESOLVED_YES", "yes")
    assert out.timestamps is not None and out.timestamps.receipt == yes.receipt


def test_each_absence_route_records_the_receipt_of_its_evidence() -> None:
    void = adjudicate(spec(), rule(evidenced=False), [], [], [], day(120))
    assert void.disposition == "VOID" and void.timestamps is not None and void.timestamps.receipt == day(120)
    failed = SourceStatus("src", True, day(100))
    unreceipted = adjudicate(spec(), rule(), [], [], [failed], day(120))
    assert unreceipted.timestamps is not None and unreceipted.timestamps.receipt == day(120)
    monotone = record("first-late", published=115, observed=116, received=117)
    out = adjudicate(spec(), rule(monotone=True), [monotone], [], [], day(118))
    assert out.disposition == "RESOLVED_NO" and out.timestamps is not None and out.timestamps.receipt == day(117)


def test_an_observer_outage_names_the_event() -> None:
    out = adjudicate(spec(), rule(), [], [observation(112)], [], day(113))
    assert [(i.kind, i.reference_id) for i in out.incidents] == [("observer_outage", "E")]


def test_an_open_adjudication_names_its_event() -> None:
    out = adjudicate(spec(), rule(), [], [], [], day(105))
    assert (out.event_id, out.disposition, out.knowable_at, out.timestamps) == ("E", "OPEN", None, None)


def test_status_receipts_are_bounded_at_both_ends_inclusively() -> None:
    status = SourceStatus("src", True, day(100))
    at_bounds = adjudicate(spec(), rule(), [], [], [status], day(120), None, {status: day(120)})
    assert at_bounds.timestamps is not None and at_bounds.timestamps.receipt == day(120)
    assert adjudicate(spec(), rule(), [], [], [status], day(120), None, {status: day(100)}).disposition == "VOID"
    assert refused(adjudicate, spec(), rule(), [], [], [status], day(120), None, {status: day(99)}) \
        == "evidence_after_receipt"
    assert refused(adjudicate, spec(), rule(), [], [], [status], day(120), None, {status: day(121)}) \
        == "receipt_after_now"


def test_a_source_rule_that_promises_evidenced_times_refuses_a_record_without_one() -> None:
    bare: ReceivedRecord = record("r", occurrence=95, observed=105)
    assert refused(bare.publication, rule()) == "missing_publication_time"


# the stored adjudication -----------------------------------------------------------------------------------------

def test_a_stored_adjudication_round_trips_with_defects_incidents_and_without_timestamps() -> None:
    out = adjudicate(spec(), rule(), [record("late", occurrence=95, published=115)], [observation(112)], [], day(116))
    assert out.defects and out.incidents
    assert Adjudication.from_payload(out.to_payload()) == out
    opened = adjudicate(spec(), rule(), [], [], [], day(105))
    assert Adjudication.from_payload(opened.to_payload()) == opened
    assert Defect.from_payload(Defect("r", "why").to_payload()) == Defect("r", "why")
    assert Incident.from_payload(Incident("receipt_lag", "r", "why").to_payload()) == Incident("receipt_lag", "r", "why")
    payload = out.to_payload()
    assert refused(Adjudication.from_payload, {**payload, "disposition": "MAYBE"}) == "invalid_choice"
    assert refused(Adjudication.from_payload, {**payload, "incidents": {}}) == "invalid_list"
    assert refused(Adjudication.from_payload, {**payload, "defects": {}}) == "invalid_list"
    assert refused(Incident.from_payload, {"kind": "flood", "reference_id": "r", "detail": ""}) == "invalid_choice"


def test_a_late_report_of_occurrence_without_a_time_or_lateness_is_a_defect() -> None:
    out = adjudicate(spec(), rule(), [record("untimed", published=115)], [observation(110)], [], day(116))
    assert out.disposition == "RESOLVED_NO" and [d.record_id for d in out.defects] == ["untimed"]


def test_a_record_published_after_its_receipt_is_refused_by_name() -> None:
    published_late = record("r", occurrence=95, published=106, observed=105, received=105)
    assert refused(adjudicate, spec(), rule(), [published_late], [], [], day(107)) == "evidence_after_receipt"


def test_a_late_timely_report_after_a_yes_is_no_defect() -> None:
    timely = record("timely", occurrence=95, published=100)
    late = record("late", occurrence=96, published=115)
    out = adjudicate(spec(), rule(), [timely, late], [], [], day(116))
    assert out.disposition == "RESOLVED_YES" and out.defects == ()


def test_a_status_declared_and_received_after_now_is_received_after_now() -> None:
    status = SourceStatus("src", True, day(125))
    assert refused(adjudicate, spec(), rule(), [], [], [status], day(120), None, {status: day(125)}) \
        == "receipt_after_now"
