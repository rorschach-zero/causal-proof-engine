"""Whole-codebase audit, pass 2 (issue #37): the two findings of the Codex review of PR #44 (``4351249330``,
``4351249349``). Each test failed on the head of PR #44, ``0325f2116550d058e7e66f0731ea84c04461e2e2``, and on
``main`` after its merge, ``5020b0456900012bf56d8e34177d51b46e738614``."""
from __future__ import annotations

from pathlib import Path

from cpe.adjudication import AdjudicationRegistry, adjudicate
from cpe.clock import ManualClock
from cpe.ledger import HarnessAnchorStore, Ledger
from tests.test_adjudication import day, observation, record, rule, spec, submit


# 4351249330 (P1): an earlier evidenced publication corrects the knowable time of a stored disposition it contradicts

def test_4351249330_a_contradicting_timely_publication_corrects_the_stored_knowable_time(tmp_path: Path) -> None:
    clock = ManualClock(day(3))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    registry.register_event(spec())
    clock.set(day(110))
    registry.submit_observation(observation(110))
    stored = registry.adjudicate("E")
    assert stored.disposition == "RESOLVED_NO" and stored.knowable_at == day(110)
    clock.set(day(120))
    # a timely YES the read at finality missed: published at 105, before finality, received at 120
    submit(registry, record("r-timely", occurrence=95, published=105, observed=119))
    after = registry.adjudicate("E")
    assert after.disposition == "RESOLVED_NO"  # the disposition is immutable (RC-88)
    assert after.knowable_at == day(105)  # the outcome information was public at 105 (RC-146); at 0325f21: 110
    assert registry.state().event("E").disposition == after
    assert registry.adjudicate("E") == after


# 4351249349 (P2): an OPEN adjudication keeps its receipt-lag incidents -------------------------------------------

def test_4351249349_an_open_adjudication_keeps_its_receipt_lag() -> None:
    # a non-definitive NO published after the deadline and inside the window decides nothing; received after finality
    lagging = record("r", claim="not-occurred", published=105, observed=120)
    result = adjudicate(spec(), rule(), [lagging], [], [], day(121))
    assert result.disposition == "OPEN"
    assert [(i.kind, i.reference_id) for i in result.incidents] == [("receipt_lag", "r")]  # at 0325f21: none
