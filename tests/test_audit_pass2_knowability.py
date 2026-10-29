"""Whole-codebase audit, pass 2 (issue #37): the adjudication findings of the Codex auditor (issue #37 comment
``6346290601``, findings 2, 3, 4 and 8). ``knowable_at`` = min(publication time, public occurrence time, deadline +
latency window) (``17`` "Logical finality", RC-77, RC-146). Each test failed on the audit commit
``2998824d0330ef028a8cc2cb7682a40f6fc23763``."""
from __future__ import annotations

from pathlib import Path

from cpe.adjudication import AdjudicationRegistry, adjudicate, classify_forecast, cluster_knowable_time
from cpe.clock import ManualClock
from cpe.ledger import HarnessAnchorStore, Ledger
from tests.test_adjudication import day, observation, record, rule, spec, submit


# 2 (P1): an earlier evidenced publication corrects a stored disposition's knowable time --------------------------

def test_codex_2_an_earlier_publication_corrects_the_stored_knowable_time(tmp_path: Path) -> None:
    clock = ManualClock(day(3))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    registry.register_event(spec())
    clock.set(day(100))
    submit(registry, record("r-1", occurrence=90, published=100, observed=100))
    stored = registry.adjudicate("E")
    assert stored.disposition == "RESOLVED_YES" and stored.knowable_at == day(100)
    clock.set(day(105))
    submit(registry, record("r-2", occurrence=80, published=85, observed=105))  # timely, evidenced publication 85
    after = registry.adjudicate("E")
    assert after.disposition == "RESOLVED_YES" and after.deciding_record_id == "r-1"  # the disposition stays
    assert after.knowable_at == day(85)  # at 2998824: 100
    assert registry.state().event("E").disposition == after  # replayed from the knowable-time row
    assert registry.adjudicate("E") == after  # nothing is written twice
    assert sum(1 for r in ledger.records() if r.kind == "knowable_correction") == 1


# 3 (P1): an OPEN member with an evidenced public occurrence carries it as its knowable time ----------------------

def test_codex_3_an_open_member_keeps_its_evidenced_public_occurrence() -> None:
    late_report = record("r", occurrence=90, published=118, observed=118)  # the RC-146 fixture, with no observation
    result = adjudicate(spec(), rule(public_act=True), [late_report], [], [], day(120))
    assert result.disposition == "OPEN"  # no rule decides it yet; the disposition is not invented
    assert result.knowable_at == day(90)  # at 2998824: None
    sibling = spec(event_id="S", deadline=200, not_before=99, issuance=(60, 99))
    assert classify_forecast(day(95), sibling, day(10), cluster_knowable_time([result])) == "late"


def test_codex_3_an_open_member_without_a_public_occurrence_has_no_knowable_time() -> None:
    late_report = record("r", occurrence=90, published=118, observed=118)
    result = adjudicate(spec(), rule(), [late_report], [], [], day(120))  # not a public act
    assert result.disposition == "OPEN" and result.knowable_at is None


# 4 (P1): a late expiry's knowable time is at most logical finality -----------------------------------------------

def test_codex_4_a_late_expiry_is_knowable_at_logical_finality() -> None:
    late_expiry = record("r", occurrence=103, published=115, observed=115)
    result = adjudicate(spec(), rule(), [late_expiry], [], [], day(116))
    assert result.disposition == "EXPIRED_NO"
    assert result.knowable_at == day(110)  # at 2998824: 115
    sibling = spec(event_id="S", deadline=200, not_before=114, issuance=(60, 114))
    assert classify_forecast(day(113), sibling, day(10), cluster_knowable_time([result])) == "late"  # F-21b


def test_codex_4_an_absence_based_no_stays_at_finality() -> None:
    result = adjudicate(spec(), rule(), [], [observation(110)], [], day(111))
    assert result.disposition == "RESOLVED_NO" and result.knowable_at == day(110)


# 8 (P2): every timely record received after finality is a receipt-lag incident -----------------------------------

def test_codex_8_a_non_deciding_timely_record_received_late_is_a_receipt_lag() -> None:
    first = record("r-1", occurrence=90, published=95, observed=100)
    lagging = record("r-2", occurrence=90, published=96, observed=120)
    result = adjudicate(spec(), rule(), [first, lagging], [], [], day(121))
    assert result.disposition == "RESOLVED_YES" and result.deciding_record_id == "r-1"
    assert [(i.kind, i.reference_id) for i in result.incidents] == [("receipt_lag", "r-2")]  # at 2998824: none


def test_codex_8_the_lag_of_a_record_received_after_the_stored_disposition_is_logged(tmp_path: Path) -> None:
    clock = ManualClock(day(3))
    registry = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    registry.register_rule(rule())
    registry.register_event(spec())
    clock.set(day(100))
    submit(registry, record("r-1", occurrence=90, published=95, observed=100))
    assert registry.adjudicate("E").disposition == "RESOLVED_YES"
    clock.set(day(120))
    submit(registry, record("r-2", occurrence=90, published=96, observed=120))
    after = registry.adjudicate("E")
    assert [(i.kind, i.reference_id) for i in after.incidents] == [("receipt_lag", "r-2")]
