"""Mutation testing, ``cpe/adjudication`` registry, predicate, records, content, eligibility and breaches: tests
that kill mutants the suite let survive at ac4c640 (``research/19`` section "Mutation testing"). They pin the
identity of every registry record on the ledger (two of a kind never collide), the reason code of every refusal,
the boundaries of eligibility and breach classes, and JSON equality inside lists and objects."""
from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from cpe.adjudication import (
    AbsenceObservation,
    ArchivedContent,
    ResolutionRecord,
    SourceRule,
    SourceStatus,
    adjudicate,
    classify_breaches,
    classify_forecast,
    cluster_knowable_time,
    evaluate,
)
from cpe.adjudication.registry import KIND_CONTENT, replay_state
from cpe.adjudication.rules import Adjudication
from cpe.canonical import canonical_bytes
from cpe.errors import Refusal
from cpe.ledger import Record
from tests.test_adjudication import archived, day, observation, record, rule, spec, submit
from tests.test_resolution_content import content_of, predicate
from tests.test_review_round2_pr18 import registry


def refused(call: object, *args: object) -> str:
    assert callable(call)
    with pytest.raises(Refusal) as refusal:
        call(*args)
    return refusal.value.reason


# predicate evaluation ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize(("observed", "holds"), [
    ([1, 2], True), ([1, 3], False), ([1, 2, 3], False), ([2, 1], False), ([1], False),
    ({"a": 1}, True), ({"a": 2}, False), ({"a": 1, "b": 1}, False), ({"b": 1}, False), (1, False),
])
def test_membership_compares_lists_and_objects_element_by_element(observed: Any, holds: bool) -> None:
    content = content_of({"sel": {"f": observed}})
    claim = evaluate(predicate("in", [[1, 2], {"a": 1}]), content)
    assert claim == ("occurred" if holds else "not-occurred")


@pytest.mark.parametrize(("comparator", "observed", "holds"), [
    ("lt", 1, True), ("lt", 2, False), ("le", 2, True), ("le", 3, False),
    ("gt", 3, True), ("gt", 2, False), ("ge", 2, True), ("ge", 1, False),
])
def test_order_comparisons_put_the_observed_value_on_the_left(comparator: str, observed: int, holds: bool) -> None:
    claim = evaluate(predicate(comparator, 2), content_of({"sel": {"f": observed}}))
    assert claim == ("occurred" if holds else "not-occurred")


@pytest.mark.parametrize(("observed", "registered"), [("1", 2), (2, "1"), (True, 2)])
def test_an_order_comparison_with_one_number_is_refused_by_name(observed: Any, registered: Any) -> None:
    assert refused(evaluate, predicate("lt", registered), content_of({"sel": {"f": observed}})) == "incomparable_values"


def test_a_non_json_constant_in_the_content_is_non_canonical() -> None:
    data = b'{"sel":{"f":NaN}}'
    from cpe.canonical import sha256_hex
    content = ArchivedContent(data, sha256_hex(data), "application/json", "src", day(0))
    assert refused(evaluate, spec().predicate, content) == "non_canonical_content"


# records and content -------------------------------------------------------------------------------------------------

def test_record_schemas_refuse_by_name_and_default_their_flags() -> None:
    assert refused(SourceRule.from_payload, {**rule().to_payload(), "monotone_publication": "yes"}) == "invalid_flag"
    assert refused(SourceRule, "src", False, False, True) == "invalid_source_rule"
    base = record("r", occurrence=95, published=105).record.to_payload()
    assert refused(ResolutionRecord.from_payload, {**base, "claim": "maybe"}) == "invalid_choice"
    minimal = {k: v for k, v in base.items() if k not in ("lateness_evidence", "definitive")}
    parsed = ResolutionRecord.from_payload(minimal)
    assert (parsed.lateness_evidence, parsed.definitive, parsed.claim) == (False, False, "occurred")
    obs = observation(110)
    assert AbsenceObservation.from_payload(obs.to_payload()) == obs


def test_archived_content_refuses_by_name() -> None:
    assert refused(ArchivedContent, "text", "0" * 64, "application/json", "src", day(0)) == "invalid_content"
    payload = archived().to_payload()
    assert refused(ArchivedContent.from_payload, {**payload, "content_base64": 7}) == "invalid_content"
    assert refused(ArchivedContent.from_payload, {**payload, "content_base64": "@@@@"}) == "invalid_content"
    padded = str(payload["content_base64"]).rstrip("=")
    assert refused(ArchivedContent.from_payload, {**payload, "content_base64": padded + "\n"}) == "invalid_content"


# eligibility and breaches ---------------------------------------------------------------------------------------------

def test_t_star_counts_the_adjudication_time_of_a_void_member_only() -> None:
    void = Adjudication("V", "VOID", None, day(120), "b", None)
    yes = Adjudication("Y", "RESOLVED_YES", day(110), day(121), "b", None)
    assert cluster_knowable_time([void]) == day(120)
    assert cluster_knowable_time([yes]) == day(110)  # a YES's adjudication time is no outcome information
    assert cluster_knowable_time([Adjudication("O", "OPEN", None, None, "b", None)]) is None


def test_eligibility_is_inclusive_at_the_close_and_late_at_t_star() -> None:
    s = spec()
    assert classify_forecast(s.issuance_close, s, day(10), None) == "eligible"
    assert classify_forecast(day(30), s, day(10), day(30)) == "late"


def test_breach_classes_are_inclusive_at_their_bounds() -> None:
    at_registration = classify_breaches("E", day(10), day(10), {}, [])
    assert at_registration.registration_breach and at_registration.any_breach
    at_cutoff = classify_breaches("E", day(20), day(10), {"A": date(2026, 1, 21)}, [])
    assert at_cutoff.early_knowability_arms == ("A",)
    at_close = classify_breaches("E", day(40), day(10), {}, [day(40)])
    assert at_close.issuance_breach
    assert at_close.to_payload() == {"event_id": "E", "knowable_at": "2026-02-10T00:00:00.000000Z",
                                     "registration_breach": False, "early_knowability_arms": [],
                                     "issuance_breach": True}
    assert (at_close.event_id, at_close.knowable_at) == ("E", day(40))


# the registry: refusals and ledger identities ---------------------------------------------------------------------------

def test_registry_refusals_are_named(tmp_path: Path) -> None:
    reg, clock, _ = registry(tmp_path, 101)
    assert refused(reg.register_rule, replace(rule(), occurrence_is_public_act=True)) == "rule_immutable"
    other = replace(record("r", occurrence=95, published=100).record, source_id="unknown")
    reg.archive_content(archived())
    assert refused(reg.submit_record, other) == "unknown_source"
    assert refused(reg.submit_observation, AbsenceObservation("o", "E", "unknown", day(100))) in ("wrong_source",)
    assert refused(reg.declare_source_status, SourceStatus("unknown", True, day(100))) == "unknown_source"
    assert refused(reg.declare_source_status, SourceStatus("src", True, day(102))) == "evidence_after_receipt"
    bare = record("bare", occurrence=95, observed=100).record  # the source rule promises evidenced times
    assert refused(reg.submit_record, bare) == "missing_publication_time"


def test_two_records_of_each_kind_have_distinct_ledger_identities(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 1)
    reg.register_rule(SourceRule("src-2", False, True, False))
    reg.register_event(spec(event_id="E2"))
    clock.set(day(101))
    submit(reg, record("a", occurrence=95, published=100))
    submit(reg, record("b", occurrence=96, published=100))
    reg.submit_observation(observation(100))
    reg.submit_observation(observation(101))
    reg.declare_source_status(SourceStatus("src", False, day(100)))
    reg.declare_source_status(SourceStatus("src", False, day(101)))
    reg.declare_source_status(SourceStatus("src-2", False, day(101)))
    assert reg.adjudicate("E").disposition == "RESOLVED_YES"
    clock.set(day(120))
    reg.submit_observation(AbsenceObservation("o-E2", "E2", "src", day(119)))
    assert reg.adjudicate("E2").disposition == "RESOLVED_NO"
    kinds = [r.kind for r in ledger.records()]
    assert kinds.count("disposition") == 2 and kinds.count("source_status") == 3


def test_two_side_rows_of_each_kind_have_distinct_ledger_identities(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 1)
    reg.register_event(spec(event_id="E2"))
    clock.set(day(111))
    for event_id in ("E", "E2"):
        reg.submit_observation(AbsenceObservation(f"o-{event_id}", event_id, "src", day(111)))
        assert reg.adjudicate(event_id).disposition == "RESOLVED_NO"
    clock.set(day(120))
    for event_id in ("E", "E2"):
        for record_id, occurrence in (("late-1", 95), ("late-2", 96)):
            submit(reg, record(f"{record_id}-{event_id}", occurrence=occurrence, published=115, event_id=event_id))
        out = reg.adjudicate(event_id)
        assert sorted(d.record_id for d in out.defects) == [f"late-1-{event_id}", f"late-2-{event_id}"]
    kinds = [r.kind for r in ledger.records()]
    assert kinds.count("source_latency_defect") == 4


def test_knowable_corrections_and_incidents_of_two_events_do_not_collide(tmp_path: Path) -> None:
    clock_reg, clock, ledger = registry(tmp_path, 1)
    reg = clock_reg
    reg.register_rule(SourceRule("pub", True, True, False))
    for event_id in ("P1", "P2"):
        s = spec(event_id=event_id)
        reg.register_event(replace(s, predicate=replace(s.predicate, source="pub")))
    clock.set(day(111))
    for event_id in ("P1", "P2"):
        reg.submit_observation(AbsenceObservation(f"o-{event_id}", event_id, "pub", day(111)))
        assert reg.adjudicate(event_id).knowable_at == day(110)
    clock.set(day(120))
    for event_id in ("P1", "P2"):
        late = record(f"late-{event_id}", occurrence=90, published=118, event_id=event_id)
        late = replace(late, record=replace(late.record, source_id="pub"),
                       content=archived(source="pub"))
        submit(reg, late)
        assert reg.adjudicate(event_id).knowable_at == day(90)
    corrections = [r for r in ledger.records() if r.kind == "knowable_correction"]
    assert len(corrections) == 2
    assert sorted(str(r.payload["record_id"]) for r in corrections if isinstance(r.payload, dict)) == ["late-P1", "late-P2"]


def test_a_content_row_available_at_its_receipt_replays(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 5)
    reg.archive_content(archived(available=5))  # available exactly at its receipt
    assert len(replay_state(ledger.records()).contents) == 1


def test_a_registry_adjudication_on_a_ledger_that_never_stops_advancing_is_contended(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 111)
    reg.submit_observation(observation(111))

    def always_stale(*args: Any, **kwargs: Any) -> Record:
        raise Refusal("stale_head", "another writer")

    ledger.append = always_stale  # type: ignore[method-assign]
    assert refused(reg.adjudicate, "E") == "contended"


def test_adjudication_needs_the_rule_of_the_event_source(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 1)
    s = spec(event_id="E3")
    ledger.append("event_spec", "forged-event", replace(s, predicate=replace(s.predicate, source="none")).to_payload())
    assert refused(reg.adjudicate, "E3") == "unknown_source"


def test_replay_refuses_a_payload_that_is_not_a_mapping(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 1)
    ledger.append(KIND_CONTENT, "forged", [1, 2])
    assert refused(replay_state, ledger.records()) == "invalid_payload"
    _ = canonical_bytes, adjudicate


def test_t_star_takes_a_void_adjudication_time_even_before_knowable_times() -> None:
    early_void = Adjudication("V", "VOID", day(115), day(111), "b", None)
    yes = Adjudication("Y", "RESOLVED_YES", day(112), day(105), "b", None)  # a YES's adjudication time never counts
    assert cluster_knowable_time([early_void, yes]) == day(111)
    assert cluster_knowable_time([yes]) == day(112)


def test_registration_at_the_issuance_open_is_late(tmp_path: Path) -> None:
    reg, clock, _ = registry(tmp_path, 1)
    clock.set(spec(event_id="E5").issuance_open)
    assert refused(reg.register_event, spec(event_id="E5")) == "late_registration"


def test_a_status_received_at_finality_decides(tmp_path: Path) -> None:
    reg, clock, _ = registry(tmp_path, 110)  # finality of spec() is day 110
    reg.declare_source_status(SourceStatus("src", True, day(110)))
    clock.set(day(120))
    assert reg.adjudicate("E").disposition == "VOID"


def test_two_successive_knowable_corrections_of_one_event_are_both_kept(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 1)
    reg.register_rule(SourceRule("pub", True, True, False))
    s = spec(event_id="P")
    reg.register_event(replace(s, predicate=replace(s.predicate, source="pub")))
    clock.set(day(111))
    reg.submit_observation(AbsenceObservation("o-P", "P", "pub", day(111)))
    assert reg.adjudicate("P").knowable_at == day(110)
    for at, (record_id, occurrence) in ((120, ("late-90", 90)), (121, ("late-80", 80))):
        clock.set(day(at))
        late = record(record_id, occurrence=occurrence, published=at - 1, event_id="P")
        submit(reg, replace(late, record=replace(late.record, source_id="pub"), content=archived(source="pub")))
        assert reg.adjudicate("P").knowable_at == day(occurrence)
    assert [r.kind for r in ledger.records()].count("knowable_correction") == 2
