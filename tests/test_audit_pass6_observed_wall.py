"""Whole-codebase audit, pass 6 (issue #37), at ``1dca8d75ab6f49a82397cd493714d8602131538b``: wall times persisted from a
clock sample taken before their append.

- Codex 6-3 (P1, PR #73 review comment 4415890522): a gate check persists the wall time of the sample it was decided on;
  a clock stepped back between that sample and the append gives the record a lower receipt. The gate keeps that time
  as its own bound (pass 2, Codex 1), but the ledger's high-water mark held receipts and anchors only, so another
  registry on the ledger was admitted below it: with a check reading 100 ms after an event's issuance opened and a
  receipt 400 ms before, ``register_event`` recorded the criteria as received before the window (``17`` item 2
  "Clock", RC-37, RC-65). The ledger now keeps every such persisted wall time as a bound of later clock reads and
  receipts, across a reopen.
- A8 (P2): the same rollback before a disposition's append wrote ``adjudicated_at`` after the row's receipt, which
  replay refuses, so every later reader of the ledger failed. The append now refuses a receipt below the
  adjudication time (``clock_rollback``), and the next adjudication decides afresh.

Both tests failed on the pass-6 commit; the reopen test checks that the bound persists."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.capability import CapabilityGate, ManualTimeSource
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from tests.test_adjudication import day, observation, rule, spec
from tests.test_capability import ENV, OWNER, RELEASE, TOLERANCE


class RollbackAfterNextRead(ManualClock):
    """A wall clock that is stepped back by ``step`` right after the next read, as an NTP correction would."""

    def __init__(self, start: datetime) -> None:
        super().__init__(start)
        self.step: timedelta | None = None

    def now(self) -> datetime:
        moment = super().now()
        if self.step is not None:
            step, self.step = self.step, None
            self.set(moment - step)
        return moment


def test_codex6_3_a_persisted_check_time_bounds_every_later_receipt(tmp_path: Path) -> None:
    clock = RollbackAfterNextRead(day(1))
    time = ManualTimeSource(clock)
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    gate = CapabilityGate(ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    time.advance(day(20) + timedelta(milliseconds=100) - clock.now())  # 100 ms after spec()'s issuance opens
    clock.step = timedelta(milliseconds=500)  # rolled back between the check's decision and its append
    gate.perform("research")
    check = ledger.records()[-1]
    assert isinstance(check.payload, dict) and isinstance(check.payload["reading"], dict)
    assert check.kind == "gate_check" and str(check.payload["reading"]["wall"]) > check.receipt_time
    with pytest.raises(Refusal) as refused:
        registry.register_event(spec())  # at 1dca8d7: recorded 400 ms before the window opens
    assert refused.value.reason == "clock_rollback"


def test_a8_a_rollback_before_the_disposition_append_leaves_a_readable_ledger(tmp_path: Path) -> None:
    clock = RollbackAfterNextRead(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    registry.register_event(spec())
    clock.set(day(111))
    registry.submit_observation(observation(110))
    clock.advance(timedelta(seconds=1))  # the receipt high-water mark stays at day 111
    clock.step = timedelta(milliseconds=500)  # rolled back between the adjudication's clock read and its append
    try:
        registry.adjudicate("E")
    except Refusal as refusal:
        assert refusal.reason == "clock_rollback"
    AdjudicationRegistry(ledger).state()  # at 1dca8d7: invalid_record, for this and every later reader
    assert AdjudicationRegistry(ledger).state().event("E").disposition is None
    clock.advance(timedelta(seconds=1))
    assert registry.adjudicate("E").disposition == "RESOLVED_NO"  # decided afresh once the clock is past the sample


def test_the_persisted_bound_survives_a_reopen(tmp_path: Path) -> None:
    clock = RollbackAfterNextRead(day(1))
    time = ManualTimeSource(clock)
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    gate = CapabilityGate(ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    time.advance(timedelta(seconds=10))
    sampled = clock.now()
    clock.step = timedelta(milliseconds=500)
    gate.perform("research")
    ledger.close()
    reopened = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    with pytest.raises(Refusal) as refused:
        reopened.now()
    assert refused.value.reason == "clock_rollback"
    clock.set(sampled)
    assert reopened.now() == sampled
