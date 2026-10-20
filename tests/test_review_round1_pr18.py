"""Regression tests for the Codex review of PR #18, one per finding (review comment ids in the test names).

Each test fails on the reviewed commit (31ef3a3, merged with PR #16's fix round as d4a4a33) and passes after the
fix; the test functions name the finding they cover.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from cpe.adjudication import AbsenceObservation, AdjudicationRegistry, SourceRule, SourceStatus, adjudicate
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.schemas import EventSpec
from tests.test_adjudication import day, observation, record, rule, spec


def registry(tmp_path: Path, at: float, source_rule: SourceRule | None = None,
             event: EventSpec | None = None) -> tuple[AdjudicationRegistry, ManualClock, Ledger]:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    reg = AdjudicationRegistry(ledger)
    reg.register_rule(source_rule if source_rule is not None else rule())
    reg.register_event(event if event is not None else spec())
    clock.set(day(at))
    return reg, clock, ledger


def test_4329192955_evidence_dated_after_the_receipt_is_refused(tmp_path: Path) -> None:
    reg, _, _ = registry(tmp_path, 100)
    with pytest.raises(Refusal) as refused:
        reg.submit_record(record("r", occurrence=95, published=105).record)
    assert refused.value.reason == "evidence_after_receipt"
    with pytest.raises(Refusal) as observed_late:
        reg.submit_record(record("r", occurrence=95, published=99, observed=101).record)
    assert observed_late.value.reason == "evidence_after_receipt"
    with pytest.raises(Refusal) as pure:
        adjudicate(spec(), rule(), [record("r", occurrence=95, published=105, received=100)], [], [], day(100))
    assert pure.value.reason == "evidence_after_receipt"


def test_4329192965_observations_after_now_or_after_receipt_do_not_count(tmp_path: Path) -> None:
    assert adjudicate(spec(), rule(), [], [observation(120)], [], day(111)).disposition == "OPEN"
    assert adjudicate(spec(), rule(), [], [observation(120)], [], day(120)).disposition == "RESOLVED_NO"
    reg, _, _ = registry(tmp_path, 111)
    with pytest.raises(Refusal) as refused:
        reg.submit_observation(observation(120))
    assert refused.value.reason == "evidence_after_receipt"


def test_4329192971_observations_from_another_source_are_refused(tmp_path: Path) -> None:
    foreign = AbsenceObservation("o", "E", "other", day(110))
    with pytest.raises(Refusal) as pure:
        adjudicate(spec(), rule(), [], [foreign], [], day(111))
    assert pure.value.reason == "wrong_source"
    reg, _, _ = registry(tmp_path, 111)
    reg.register_rule(SourceRule("other", False, True, False))
    with pytest.raises(Refusal) as refused:
        reg.submit_observation(foreign)
    assert refused.value.reason == "wrong_source"
    assert reg.adjudicate("E").disposition == "OPEN"


def test_4329192985_records_of_another_event_are_refused() -> None:
    with pytest.raises(Refusal) as refused:
        adjudicate(spec(), rule(), [record("r", occurrence=95, published=105, event_id="F")], [], [], day(106))
    assert refused.value.reason == "wrong_event"


def test_4329192993_a_late_falsifier_after_a_terminal_falsifier_yes_is_a_defect() -> None:
    out = adjudicate(spec("terminal-falsifier"), rule(), [record("late", occurrence=60, published=115)],
                     [observation(110)], [], day(116))
    assert out.disposition == "RESOLVED_YES" and [d.record_id for d in out.defects] == ["late"]
    # a late record that does not contradict the disposition is no defect
    agreeing = adjudicate(spec(), rule(), [record("late", occurrence=105, published=115)], [observation(110)], [],
                          day(116))
    assert agreeing.disposition == "RESOLVED_NO" and agreeing.defects == ()


def test_4329192997_an_occurrence_before_the_predicate_window_decides_nothing() -> None:
    assert adjudicate(spec(), rule(), [record("r", occurrence=40, published=41)], [], [], day(42)).disposition == "OPEN"
    assert adjudicate(spec("terminal-falsifier"), rule(), [record("r", occurrence=40, published=41)], [], [],
                      day(42)).disposition == "OPEN"
    inside = adjudicate(spec(), rule(), [record("r", occurrence=50, published=51)], [], [], day(52))
    assert inside.disposition == "RESOLVED_YES"


def test_4329193009_the_registry_adjudicates_at_the_ledger_clock(tmp_path: Path) -> None:
    reg, clock, _ = registry(tmp_path, 50, source_rule=rule(evidenced=False))
    assert reg.adjudicate("E").disposition == "OPEN"
    clock.set(day(111))
    out = reg.adjudicate("E")
    assert out.disposition == "VOID" and out.adjudicated_at == day(111)


def test_4329193020_the_registry_binds_adjudication_to_the_registered_specification(tmp_path: Path) -> None:
    reg, _, ledger = registry(tmp_path, 50)
    reg.register_event(spec())
    with pytest.raises(Refusal) as refused:
        reg.register_event(spec(deadline=90, window_days=10))
    assert refused.value.reason == "event_immutable"
    with pytest.raises(Refusal) as unknown:
        reg.adjudicate("other-event")
    assert unknown.value.reason == "unknown_event"
    assert [r.kind for r in ledger.records()].count("event_spec") == 1


def test_4329193031_defects_recorded_after_the_disposition_are_returned_and_replayed(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 111)
    reg.submit_observation(observation(110))
    first = reg.adjudicate("E")
    assert first.disposition == "RESOLVED_NO" and first.defects == ()
    clock.set(day(113))
    reg.submit_record(record("late", occurrence=95, published=112).record)
    again = reg.adjudicate("E")
    assert [d.record_id for d in again.defects] == ["late"] and replace(again, defects=()) == first
    ledger.close()
    reopened = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    assert reopened.adjudicate("E") == again


def test_4329193037_a_source_failure_declared_after_finality_does_not_void_the_disposition() -> None:
    late_failure = SourceStatus("src", failed=True, declared_at=day(120))
    out = adjudicate(spec(), rule(), [], [observation(110)], [late_failure], day(121))
    assert out.disposition == "RESOLVED_NO"
    at_finality = adjudicate(spec(), rule(), [], [observation(110)], [SourceStatus("src", True, day(110))], day(121))
    assert at_finality.disposition == "VOID"


def test_4329193050_a_record_admitted_between_snapshot_and_write_is_decided_on(tmp_path: Path) -> None:
    reg, _, ledger = registry(tmp_path, 111)
    reg.submit_observation(observation(110))

    def admit_timely_yes() -> None:
        reg.submit_record(record("r", occurrence=95, published=105).record)

    reg.before_write = admit_timely_yes
    out = reg.adjudicate("E")
    assert out.disposition == "RESOLVED_YES" and out.deciding_record_id == "r"
    kinds = [r.kind for r in ledger.records()]
    assert kinds.index("resolution_record") < kinds.index("disposition") and kinds.count("disposition") == 1
    with pytest.raises(Refusal) as stale:
        ledger.append("disposition", "disposition:E:again", {"x": 1}, expected_head="0" * 64)
    assert stale.value.reason == "stale_head"
