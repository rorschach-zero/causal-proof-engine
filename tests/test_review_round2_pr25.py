"""Regression tests for the second review of PR #25 (Codex review at ce44f54), one per finding.

Each test fails at ce44f54 and passes after the fix.
"""
from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

import pytest

from cpe.capability import CapabilityGate, ManualTimeSource
from cpe.capability.records import KIND_CHECK
from cpe.clock import ManualClock
from cpe.errors import Refusal
from tests.test_capability import ENV, OWNER, RELEASE, TOLERANCE, Rig, issue


@pytest.fixture
def rig(tmp_path: Path) -> Rig:
    return Rig(tmp_path)


def test_4333434004_a_promotion_overtaken_by_a_higher_one_aborts_at_step_3(rig: Rig) -> None:
    epoch = rig.epoch()
    rig.tick()
    higher = issue(epoch, "high", level="SIM_EXECUTION")

    def overtake() -> None:  # another presentation completes all four steps between this one's steps 2 and 3
        assert rig.promote(higher).status == "acknowledged"

    rig.gate.hooks["after_intent_anchor"] = overtake
    assert rig.refused(issue(epoch, "low", level="SHADOW_LIVE_QUOTES")) == "superseded"
    state = rig.gate.state()
    assert state.level == "SIM_EXECUTION"  # never lowered without a rotating demotion
    assert len(state.aborted) == 1 and state.pending_intents == ()


def test_4333434009_a_clock_rollback_refusal_is_logged(rig: Rig, caplog: pytest.LogCaptureFixture) -> None:
    rig.tick(10)
    rig.gate.perform("research")
    rig.clock.set(rig.clock.now() - timedelta(seconds=5))
    with caplog.at_level(logging.WARNING, logger="cpe.capability"), pytest.raises(Refusal) as refused:
        rig.gate.perform("research")
    assert refused.value.reason == "clock_rollback"
    assert any("clock_rollback" in r.getMessage() for r in caplog.records if r.name == "cpe.capability")


class PausingTimeSource(ManualTimeSource):
    """Reading the monotonic clock takes ``pause`` once: real time and the wall clock move on during the read, and
    the read returns the value from before the pause (a slow read between the decision's sample and the append)."""

    def __init__(self, clock: ManualClock) -> None:
        super().__init__(clock)
        self.pause: timedelta | None = None

    def monotonic(self) -> float:
        value = super().monotonic()
        if self.pause is not None:
            pause, self.pause = self.pause, None
            self.advance(pause)
        return value


def test_4333434011_expiry_is_checked_against_the_appended_receipt_time(rig: Rig) -> None:
    time = PausingTimeSource(rig.clock)
    rig.time = time
    rig.gate = CapabilityGate(rig.ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    rig.tick()
    a = issue(rig.epoch(), "a", expiry=rig.clock.now() + timedelta(seconds=0.5))
    time.pause = timedelta(seconds=0.75)  # below the slew tolerance of 1 second
    assert rig.refused(a) == "expired"
    state = rig.gate.state()
    assert state.level == "RESEARCH_ONLY" and not state.commits and not state.intents  # refused at the receipt
    last = rig.ledger.records()[-1]  # since H1: the ledger refuses the intent at its receipt; the check is persisted
    assert last.kind == KIND_CHECK and isinstance(last.payload, dict) and last.payload["reason"] == "expired"
