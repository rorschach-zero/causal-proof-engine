"""Whole-codebase audit, pass 2 (issue #37): a second adjudication registry on the same ledger. A record the other
writer landed first between this registry's snapshot and its append is read back, not refused as a duplicate
identifier, as the point-in-time store already does (4335189771). Each test failed on the audit commit
``2998824d0330ef028a8cc2cb7682a40f6fc23763`` with ``duplicate_record_id``."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from tests import test_adjudication as adj


@pytest.fixture
def clock() -> ManualClock:
    return ManualClock(adj.day(3))


@pytest.fixture
def ledger(tmp_path: Path, clock: ManualClock) -> Ledger:
    return Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())


def stale_once(registry: AdjudicationRegistry, monkeypatch: pytest.MonkeyPatch) -> None:
    """The registry's next snapshot is the one taken now: the other writer's record lands after it."""
    snapshot = registry.state()
    pending = [snapshot]
    monkeypatch.setattr(registry, "state",
                        lambda: pending.pop() if pending else AdjudicationRegistry.state(registry))


def test_a_rule_the_other_writer_registered_first_is_read_back(ledger: Ledger,
                                                               monkeypatch: pytest.MonkeyPatch) -> None:
    first, second = AdjudicationRegistry(ledger), AdjudicationRegistry(ledger)
    stale_once(second, monkeypatch)
    first.register_rule(adj.rule())
    second.register_rule(adj.rule())
    assert second.state().rules["src"] == adj.rule()


def test_an_event_the_other_writer_registered_first_is_read_back(ledger: Ledger,
                                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    first, second = AdjudicationRegistry(ledger), AdjudicationRegistry(ledger)
    first.register_rule(adj.rule())
    stale_once(second, monkeypatch)
    first.register_event(adj.spec())
    second.register_event(adj.spec())
    assert second.state().event("E").spec == adj.spec()


def test_other_criteria_the_other_writer_registered_first_are_refused(ledger: Ledger,
                                                                      monkeypatch: pytest.MonkeyPatch) -> None:
    first, second = AdjudicationRegistry(ledger), AdjudicationRegistry(ledger)
    first.register_rule(adj.rule())
    stale_once(second, monkeypatch)
    first.register_event(adj.spec())
    with pytest.raises(Refusal) as refused:
        second.register_event(adj.spec(deadline=101))
    assert refused.value.reason == "event_immutable"


def test_a_late_defect_the_other_writer_logged_first_is_read_back(ledger: Ledger, clock: ManualClock) -> None:
    first, second = AdjudicationRegistry(ledger), AdjudicationRegistry(ledger)
    first.register_rule(adj.rule())
    first.register_event(adj.spec())
    clock.set(adj.day(110))
    first.submit_observation(adj.observation(110))
    assert first.adjudicate("E").disposition == "RESOLVED_NO"
    clock.set(adj.day(120))
    adj.submit(first, adj.record("r-late", occurrence=96, published=118, observed=119))
    def other_writer() -> None:  # the other writer logs the defect after this registry's snapshot
        second.adjudicate("E")

    first.before_write = other_writer
    after = first.adjudicate("E")
    assert after.disposition == "RESOLVED_NO"
    assert [d.record_id for d in after.defects] == ["r-late"]
    assert sum(1 for r in ledger.records() if r.kind == "source_latency_defect") == 1
