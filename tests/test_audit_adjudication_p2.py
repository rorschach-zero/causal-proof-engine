"""Whole-codebase audit (issue #37): the P2 findings in ``cpe/adjudication``.

- Pass 3 A2: a ``record_id`` longer than 256 characters was admitted, and replay then refused the ledger.
- Pass 3 A3: an ``EventSpec`` with a negative latency window was admitted, and replay then refused the ledger.
- Pass 3 A4: an order comparator over a non-number was registered; it can never evaluate, every record is refused
  ``incomparable_values`` and the member resolves NO by absence.
- Pass 4 A5: the same class on other fields (flags given as 1, identifiers of 300 characters, an unknown comparator
  or predicate kind, a fractional latency window): the registry wrote values its own replay refuses.
- Pass 4 A6: the status identifier was formed from the instant as written, so one instant in two time zones landed
  two conflicting statuses, and the disposition depended on submission order.
- Pass 4 A7: a disposition corrected on a stale snapshot was returned, while the ledger held another.

Every test here failed on the pass-4 commit ``c3d6233dbaeb71eb71cb128394099b23cef285b5``; A2, A3 and A4 also on the
pass-3 commit ``b48c952c67c4d4358f82d3f811f744d47bdeb0b4``."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import timedelta, timezone
from pathlib import Path

import pytest

from cpe.adjudication import AbsenceObservation, AdjudicationRegistry, ResolutionRecord, SourceRule, SourceStatus
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.schemas import EventSpec
from tests.test_adjudication import archived, day, record, rule, spec, submit


def _registry(tmp_path: Path, source_rule: SourceRule | None = None) -> tuple[AdjudicationRegistry, ManualClock, Ledger]:
    clock = ManualClock(day(3))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(source_rule or rule())
    return registry, clock, ledger


# Pass 3 A2, A3, A4 -------------------------------------------------------------------------------------------------

def _overlong_record_id(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    reg.register_event(spec())
    clock.set(day(106))
    content = archived("occurred")
    reg.archive_content(content)
    reg.submit_record(ResolutionRecord("r" * 300, "E", "src", "occurred", first_observed_at=day(105),
                                       content_digest=content.sha256, occurrence_time=day(95),
                                       evidenced_publication_time=day(105)))


def _negative_window(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    reg.register_event(replace(spec(), latency_window_seconds=-86400))


@pytest.mark.parametrize("write", [_overlong_record_id, _negative_window])
def test_a2_a3_the_registry_never_writes_what_its_replay_refuses(
        tmp_path: Path, write: Callable[[AdjudicationRegistry, ManualClock], None]) -> None:
    reg, clock, _ = _registry(tmp_path)
    try:
        write(reg, clock)
    except Refusal:
        return  # refused at the write: the required behaviour
    reg.state()  # at c3d6233: invalid_identifier, invalid_integer, for this and every later reader


@pytest.mark.parametrize("comparator, value", [("gt", "high"), ("lt", True), ("ge", None), ("le", "1")])
def test_a4_an_order_comparator_over_a_non_number_is_refused_at_registration(comparator: str, value: object) -> None:
    payload = spec().to_payload()
    payload["predicate"] = dict(payload["predicate"], comparator=comparator, value=value)  # type: ignore[arg-type]
    with pytest.raises(Refusal) as refused:
        EventSpec.from_payload(payload)  # at c3d6233: registered, and no record can ever evaluate under it
    assert refused.value.reason == "invalid_predicate_value"


# Pass 4 A5 ---------------------------------------------------------------------------------------------------------

def _definitive_int(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    reg.register_event(spec())
    clock.set(day(101))
    r = record("r", claim="not-occurred", published=101)
    reg.archive_content(r.content)
    reg.submit_record(replace(r.record, definitive=1))  # type: ignore[arg-type]


def _status_int(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    clock.set(day(5))
    reg.declare_source_status(SourceStatus("src", 1, day(4)))  # type: ignore[arg-type]


def _observation_id_300(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    reg.register_event(spec())
    clock.set(day(111))
    reg.submit_observation(AbsenceObservation("o" * 300, "E", "src", day(110)))


def _unknown_comparator(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    s = spec()
    reg.register_event(replace(s, predicate=replace(s.predicate, comparator="foo")))  # type: ignore[arg-type]


def _unknown_kind(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    reg.register_event(replace(spec(), predicate_kind="other"))  # type: ignore[arg-type]


def _float_window(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    reg.register_event(replace(spec(), latency_window_seconds=864000.5))  # type: ignore[arg-type]


def _slot_300(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    reg.register_event(replace(spec(), scoring_slots=("x" * 300,), primary_slot="x" * 300))


@pytest.mark.parametrize("write", [_definitive_int, _status_int, _observation_id_300, _unknown_comparator,
                                   _unknown_kind, _float_window, _slot_300])
def test_a5_the_registry_never_writes_what_its_replay_refuses(tmp_path: Path,
                                                               write: Callable[[AdjudicationRegistry, ManualClock], None]) -> None:
    reg, clock, _ = _registry(tmp_path)
    try:
        write(reg, clock)
    except Refusal:
        return  # refused at the write: the required behaviour
    reg.state()  # admitted: replay must read it back (at c3d6233 it refuses, and so does every later call)


def test_a5_a_rule_with_a_non_boolean_flag_is_never_written(tmp_path: Path) -> None:
    clock = ManualClock(day(3))
    reg = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    try:
        reg.register_rule(SourceRule("src", 1, True, False))  # type: ignore[arg-type]
    except Refusal:
        return
    reg.state()


# Pass 4 A6 ---------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("first, second", [(False, True), (True, False)])
def test_a6_one_instant_carries_one_status_whatever_its_time_zone(tmp_path: Path, first: bool, second: bool) -> None:
    reg, clock, ledger = _registry(tmp_path)
    reg.register_event(spec())
    clock.set(day(101))
    reg.declare_source_status(SourceStatus("src", first, day(100)))
    with pytest.raises(Refusal) as refused:  # in UTC the second declaration is a duplicate; at c3d6233 it lands
        reg.declare_source_status(SourceStatus("src", second, day(100).astimezone(timezone(timedelta(hours=1)))))
    assert refused.value.reason == "duplicate_status"  # the registry's rule, not the ledger's identifier (pass 9)


# Pass 4 A7 ---------------------------------------------------------------------------------------------------------

def test_a7_the_returned_disposition_is_the_one_the_ledger_holds(tmp_path: Path) -> None:
    reg, clock, ledger = _registry(tmp_path)
    other = AdjudicationRegistry(ledger)
    reg.register_event(spec())
    clock.set(day(100))
    submit(reg, record("r-1", occurrence=90, published=100, observed=100))
    assert reg.adjudicate("E").knowable_at == day(100)
    clock.set(day(105))
    submit(reg, record("r-2", occurrence=80, published=85, observed=105))

    def other_writer() -> None:  # lands between this registry's snapshot and its write
        submit(other, record("r-3", occurrence=70, published=80, observed=105))
        assert other.adjudicate("E").knowable_at == day(80)

    reg.before_write = other_writer
    returned = reg.adjudicate("E")
    held = reg.state().event("E").disposition
    assert held is not None and held.knowable_at == day(80)
    assert returned == held  # at c3d6233: knowable_at 85, and a redundant knowable_correction row for r-2
