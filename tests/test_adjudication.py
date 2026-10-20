"""Adjudication: T-02 (retained parts), T-03, T-04, F-02a to F-02e, F-03, F-21, F-21b, F-24 F, F-27 breach classes,
RC-146, RC-88 immutability, RC-105, RC-113, RC-139, RC-156, RC-163."""
from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from cpe.adjudication import (
    AbsenceObservation,
    AdjudicationRegistry,
    ResolutionRecord,
    SourceRule,
    SourceStatus,
    adjudicate,
    classify_breaches,
    classify_forecast,
    cluster_knowable_time,
)
from cpe.adjudication.rules import ReceivedRecord
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.schemas import EventSpec

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def day(n: float) -> datetime:
    return BASE + timedelta(days=n)


def rule(public_act: bool = False, evidenced: bool = True, monotone: bool = False) -> SourceRule:
    return SourceRule("src", occurrence_is_public_act=public_act, publishes_evidenced_times=evidenced,
                      monotone_publication=monotone)


def spec(kind: str = "milestone-deadline", event_id: str = "E", deadline: float = 100, window_days: float = 10,
         not_before: float = 50, issuance: tuple[float, float] = (20, 40)) -> EventSpec:
    payload = {
        "event_id": event_id, "cluster_id": "C", "predicate_kind": kind,
        "predicate": {"source": "src", "record_selector": "sel", "field": "f", "comparator": "eq", "value": True,
                      "not_before": day(not_before).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                      "not_after": day(deadline).strftime("%Y-%m-%dT%H:%M:%S.%fZ")},
        "latency_window_seconds": int(window_days * 86400),
        "issuance_open": day(issuance[0]).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "issuance_close": day(issuance[1]).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "evidence_cutoff": day(issuance[1] - 1).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "reference_class_id": "RC",
    }
    if kind == "terminal-falsifier":
        payload["falsifier_observable_from"] = day(not_before).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return EventSpec.from_payload(payload)


def record(record_id: str, claim: str = "occurred", occurrence: float | None = None, published: float | None = None,
           observed: float | None = None, received: float | None = None, lateness: bool = False,
           definitive: bool = False, event_id: str = "E") -> ReceivedRecord:
    seen = observed if observed is not None else (published if published is not None else 0.0)
    rec = ResolutionRecord(record_id, event_id, "src", claim,  # type: ignore[arg-type]
                           first_observed_at=day(seen),
                           occurrence_time=None if occurrence is None else day(occurrence),
                           evidenced_publication_time=None if published is None else day(published),
                           lateness_evidence=lateness, definitive=definitive)
    return ReceivedRecord(rec, day(received if received is not None else seen))


def observation(at: float, event_id: str = "E") -> AbsenceObservation:
    return AbsenceObservation(f"obs-{at}", event_id, "src", day(at))


def test_t03_timely_yes_observed_inside_the_window_and_the_public_act_route() -> None:
    yes = adjudicate(spec(), rule(), [record("r", occurrence=95, published=105)], [], [], day(106))
    assert yes.disposition == "RESOLVED_YES" and yes.knowable_at == day(105)
    assert yes.timestamps is not None and yes.timestamps.occurrence == day(95) and yes.timestamps.publication == day(105)
    public = adjudicate(spec(), rule(public_act=True), [record("r", occurrence=95, published=105)], [], [], day(106))
    assert public.knowable_at == day(95)


def test_f02b_timestamp_less_late_yes_is_void_never_expired_no() -> None:
    out = adjudicate(spec(), rule(), [record("r", published=105)], [], [], day(106))
    assert out.disposition == "VOID" and "RC-71" in out.basis and out.knowable_at == day(105)
    late_evidenced = adjudicate(spec(), rule(), [record("r", published=105, lateness=True)], [], [], day(106))
    assert late_evidenced.disposition == "EXPIRED_NO"


def test_f02a_occurrence_after_the_deadline_is_expired_no() -> None:
    out = adjudicate(spec(), rule(), [record("r", occurrence=105, published=108)], [], [], day(109))
    assert out.disposition == "EXPIRED_NO" and out.knowable_at == day(108)


def test_f03_no_before_the_deadline_is_not_final(tmp_path: Path) -> None:
    early_no = record("r", claim="not-occurred", published=2)
    with pytest.raises(Refusal) as refusal:
        adjudicate(spec(), rule(), [early_no], [], [], day(3))
    assert refusal.value.reason == "not_final"
    registry = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", ManualClock(day(3)), HarnessAnchorStore()))
    registry.register_rule(rule())
    registry.register_event(spec())
    with pytest.raises(Refusal) as refused:
        registry.submit_record(early_no.record)
    assert refused.value.reason == "not_final"
    definitive = adjudicate(spec(), rule(), [record("r", claim="not-occurred", published=101, definitive=True)], [], [], day(102))
    assert definitive.disposition == "EXPIRED_NO"


def test_t04_terminal_falsifier_is_no_when_published_and_yes_by_absence_at_finality() -> None:
    falsified = adjudicate(spec("terminal-falsifier"), rule(public_act=True), [record("r", occurrence=60, published=61)],
                           [], [], day(62))
    assert falsified.disposition == "RESOLVED_NO" and falsified.knowable_at == day(60)
    survived = adjudicate(spec("terminal-falsifier"), rule(), [], [observation(110)], [], day(111))
    assert survived.disposition == "RESOLVED_YES" and survived.knowable_at == day(110)


def test_t04_no_by_expiry_needs_an_observation_of_absence_and_is_immutable() -> None:
    before = adjudicate(spec(), rule(), [], [], [], day(115))
    assert before.disposition == "OPEN"
    at_finality = adjudicate(spec(), rule(), [], [observation(110)], [], day(115))
    assert (at_finality.disposition, at_finality.knowable_at) == ("RESOLVED_NO", day(110))
    assert at_finality.incidents == ()
    late_read = adjudicate(spec(), rule(), [], [observation(120)], [], day(121))
    assert late_read.disposition == "RESOLVED_NO" and late_read.knowable_at == day(110)
    assert [i.kind for i in late_read.incidents] == ["observer_outage"]
    # F-02c: a report of timely occurrence published after finality is a defect, never YES and never VOID
    with_late = adjudicate(spec(), rule(), [record("late", occurrence=95, published=112)], [observation(110)], [], day(113))
    assert with_late.disposition == "RESOLVED_NO" and [d.record_id for d in with_late.defects] == ["late"]


def test_f02e_monotone_publication_makes_the_late_record_the_observation_of_absence() -> None:
    late = record("late", occurrence=95, published=115, observed=130)
    out = adjudicate(spec(), rule(monotone=True), [late], [], [], day(131))
    assert (out.disposition, out.knowable_at) == ("RESOLVED_NO", day(110))
    assert [d.record_id for d in out.defects] == ["late"] and [i.kind for i in out.incidents] == ["observer_outage"]
    without_condition = adjudicate(spec(), rule(monotone=False), [late], [], [], day(131))
    assert without_condition.disposition == "OPEN"
    cannot_evidence = adjudicate(spec(), rule(evidenced=False), [], [], [], day(131))
    assert cannot_evidence.disposition == "VOID" and "RC-113" in cannot_evidence.basis


def test_f02d_record_published_inside_the_window_and_received_late_resolves_by_content() -> None:
    out = adjudicate(spec(), rule(), [record("r", occurrence=95, published=105, observed=118, received=118)], [], [], day(118))
    assert out.disposition == "RESOLVED_YES" and out.knowable_at == day(105)
    assert [i.kind for i in out.incidents] == ["receipt_lag"]


def test_source_failure_condition_gives_void_at_finality() -> None:
    failed = SourceStatus("src", failed=True, declared_at=day(100))
    out = adjudicate(spec(), rule(), [], [observation(110)], [failed], day(111))
    assert out.disposition == "VOID" and out.knowable_at == day(110)


def test_rc146_knowable_at_is_the_earliest_of_the_three_times() -> None:
    # occurrence public at 90 (inside the predicate window opening at 80), deadline + window 110 (deadline 101,
    # window 9), publication 105 inside the window: knowable_at is 90, the earliest of the three
    late_spec = spec(deadline=101, window_days=9, not_before=80, issuance=(20, 80))
    out = adjudicate(late_spec, rule(public_act=True), [record("r", occurrence=90, published=105)], [], [], day(119))
    assert (out.disposition, out.knowable_at) == ("RESOLVED_YES", day(90))
    t_star = cluster_knowable_time([out])
    assert t_star == day(90)
    assert classify_forecast(day(79), late_spec, day(10), t_star) == "eligible"
    # the issuance window closes at e_i = 80 (RC-163), so no forecast received at or after 90 is inside it
    assert classify_forecast(day(95), late_spec, day(10), t_star) == "out_of_window"


def test_f21_publication_gap_and_f21b_expiry_gap() -> None:
    # F-21: outcome (lateness evidenced, no occurrence time) published 10:00, forecast received 10:05, registry
    # receives the outcome 10:30
    ten = day(100) + timedelta(hours=10)
    gap_spec = spec(deadline=101, not_before=100.9, issuance=(20, 100.9))
    published_at_ten = record("r", published=100 + 10 / 24, received=100 + 10.5 / 24, lateness=True)
    out = adjudicate(gap_spec, rule(), [published_at_ten], [], [], day(101))
    assert (out.disposition, out.knowable_at) == ("EXPIRED_NO", ten)
    t_star = cluster_knowable_time([out])
    assert t_star == ten
    assert classify_forecast(ten + timedelta(minutes=5), gap_spec, day(10), t_star) == "late"
    assert classify_forecast(ten - timedelta(minutes=5), gap_spec, day(10), t_star) == "eligible"
    # F-21b: deadline 100, window 10, formal NO record at 118; knowable_at is 110 by logical finality, so a forecast
    # received at 113 is excluded (it is also outside any issuance window, which closes by e_i <= the deadline)
    expired = adjudicate(spec(), rule(), [], [observation(118)], [], day(118))
    t_star_b = cluster_knowable_time([expired])
    assert t_star_b == day(110)
    assert day(113) >= t_star_b
    assert classify_forecast(day(113), spec(), day(10), t_star_b) != "eligible"
    assert classify_forecast(day(30), spec(), day(10), t_star_b) == "eligible"


def test_f24_cluster_f_void_sibling_sets_t_star_for_the_whole_cluster() -> None:
    void_member = adjudicate(spec(event_id="m1", deadline=100), rule(), [record("r1", published=10, event_id="m1")], [], [], day(10))
    assert void_member.disposition == "VOID" and void_member.adjudicated_at == day(10)
    open_member = adjudicate(spec(event_id="m2"), rule(), [], [], [], day(15))
    assert cluster_knowable_time([void_member, open_member]) == day(10)
    assert classify_forecast(day(15), spec(event_id="m2", issuance=(1, 50)), day(0), day(10)) == "late"
    assert classify_forecast(day(5), spec(event_id="m2", issuance=(1, 50)), day(6), None) == "before_registration"
    assert classify_forecast(day(60), spec(event_id="m2", issuance=(1, 50)), day(0), None) == "out_of_window"


def test_f27_breach_classes_rc139_rc163_rc156() -> None:
    cutoffs = {"FULL": day(0).date()}
    registration = classify_breaches("E", day(5), day(10), cutoffs, [day(10)])
    assert registration.registration_breach and registration.early_knowability_arms == () and not registration.issuance_breach
    issuance = classify_breaches("E", day(5), day(1), cutoffs, [day(10)])
    assert (issuance.registration_breach, issuance.issuance_breach) == (False, True)
    composite = {"A": date(2026, 1, 21), "B": date(2026, 1, 11), "C": date(2026, 1, 9), "JEV": date(2026, 1, 6),
                 "FULL": date(2026, 1, 21), "COMMITTEE": date(2026, 1, 21), "A3": date(2026, 1, 21)}
    early = classify_breaches("E", day(15), day(1), composite, [day(10)])
    assert early.early_knowability_arms == ("A", "A3", "COMMITTEE", "FULL") and not early.issuance_breach
    clean = classify_breaches("E", day(60), day(1), composite, [day(10)])
    assert not clean.any_breach


def test_registry_writes_the_disposition_once_and_replays_it(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    with pytest.raises(Refusal) as unknown:
        registry.submit_observation(observation(110))
    assert unknown.value.reason == "unknown_event"
    with pytest.raises(Refusal) as no_rule:
        registry.register_event(spec())
    assert no_rule.value.reason == "unknown_source"
    registry.register_rule(rule())
    registry.register_rule(rule())
    with pytest.raises(Refusal):
        registry.register_rule(rule(public_act=True))
    registry.register_event(spec())
    clock.set(day(105))
    with pytest.raises(Refusal):
        registry.submit_record(record("missing-time").record)
    assert registry.adjudicate("E").disposition == "OPEN"
    clock.set(day(111))
    registry.submit_observation(observation(110))
    first = registry.adjudicate("E")
    assert first.disposition == "RESOLVED_NO" and first.adjudicated_at == day(111) and first.defects == ()
    clock.set(day(113))
    registry.submit_record(record("late", occurrence=95, published=112).record)
    again = registry.adjudicate("E")
    assert replace(again, defects=()) == first and [d.record_id for d in again.defects] == ["late"]
    kinds = [r.kind for r in ledger.records()]
    assert kinds.count("disposition") == 1 and kinds.count("source_latency_defect") == 1
    assert registry.adjudicate("E") == again
    assert [r.kind for r in ledger.records()].count("source_latency_defect") == 1
    ledger.close()
    clock.set(day(200))
    reopened = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    assert reopened.adjudicate("E") == again


def test_registry_refuses_the_wrong_source_and_event() -> None:
    other = EventSpec.from_payload({**spec().to_payload(), "predicate": {**spec().predicate.to_payload(), "source": "other"}})
    with pytest.raises(Refusal) as refusal:
        adjudicate(other, rule(), [], [], [], day(1))
    assert refusal.value.reason == "wrong_source"
    with pytest.raises(Refusal) as from_other:
        adjudicate(spec(), rule(), [ReceivedRecord(ResolutionRecord("x", "E", "other", "occurred", day(1)), day(1))], [],
                   [], day(1))
    assert from_other.value.reason == "wrong_source"
