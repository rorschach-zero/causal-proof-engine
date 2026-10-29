"""Whole-codebase audit, pass 5 (issue #37), at ``b34c7212ca688d72611c3fd09b4eba170f94b44b``: the ledger.

- L1: an anchor attempt staged before its publish bounds the clock (``17`` item 2 "Clock": the persisted wall time
  is a high-water mark, a check below it fails closed). Reopening the ledger reconciled an attempt the store had
  never received by deleting its row, and the bound went with it: a record was admitted with a receipt below the
  wall time the ledger had persisted. ``anchor()`` itself kept the bound only because the attempt it stages next is
  later. A settled or disproved attempt now keeps its time as a bound.

The two ``test_l1_*`` tests failed on the pass-5 commit."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from tests.test_audit_pass4_r1_review import Switchable
from tests.test_registration import day


def staged_and_lost(tmp_path: Path) -> tuple[ManualClock, Switchable]:
    clock = ManualClock(day(1))
    store = Switchable()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    ledger.append("note", "n-1", {})
    clock.set(day(10))
    store.lose_next = True
    with pytest.raises(Refusal):
        ledger.anchor()  # staged at day 10, never reached the store
    clock.set(day(5))
    with pytest.raises(Refusal) as refused:
        ledger.now()
    assert refused.value.reason == "clock_rollback"
    ledger.close()
    return clock, store


def test_l1_a_disproved_attempt_bounds_the_clock_after_reopen(tmp_path: Path) -> None:
    clock, store = staged_and_lost(tmp_path)
    reopened = Ledger(tmp_path / "l.sqlite", clock, store)  # reconciliation clears the attempt
    assert reopened.pending_anchors() == ()
    with pytest.raises(Refusal) as refused:
        reopened.append("note", "n-2", {})
    assert refused.value.reason == "clock_rollback"
    clock.set(day(10))
    assert reopened.append("note", "n-2", {}).receipt_time.startswith("2026-01-11")


def test_l1_the_bound_survives_a_second_reopen(tmp_path: Path) -> None:
    clock, store = staged_and_lost(tmp_path)
    Ledger(tmp_path / "l.sqlite", clock, store).close()
    with pytest.raises(Refusal) as refused:
        Ledger(tmp_path / "l.sqlite", clock, store).now()
    assert refused.value.reason == "clock_rollback"


def test_a_settled_attempt_keeps_the_ledger_usable_at_and_after_its_time(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    store = Switchable()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    ledger.append("note", "n-1", {})
    clock.set(day(10))
    store.land_then_fail = True
    with pytest.raises(Refusal):
        ledger.anchor()  # landed, acknowledgement lost
    ledger.close()
    reopened = Ledger(tmp_path / "l.sqlite", clock, store)
    assert [a.prefix_length for a in reopened.local_anchors()] == [1] and reopened.pending_anchors() == ()
    reopened.append("note", "n-2", {})
