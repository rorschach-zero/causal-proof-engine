"""Hardening pass H4: the three late findings the owner's delegate assigned on 2026-10-21 (``research/19`` section
9.9 and the reviews of PR #32 and PR #33). Each test fails at 44aa596 and passes after the fix."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cpe.adjudication.registry import KIND_CONTENT, replay_state
from cpe.capability import CapabilityGate
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.pointintime import detect_leak
from tests.test_capability import ENV, OWNER, RELEASE, TOLERANCE, FlakyStore, Rig, issue
from tests.test_resolution_content import content_of
from tests.test_review_round2_pr25 import PausingTimeSource


class RollbackClock(ManualClock):
    """A manual clock that, once armed, returns one more reading and then steps back by ``rollback``."""

    def __init__(self, start: datetime) -> None:
        super().__init__(start)
        self.rollback: timedelta | None = None

    def now(self) -> datetime:
        moment = super().now()
        if self.rollback is not None:
            step, self.rollback = self.rollback, None
            self.set(moment - step)
        return moment


class ArmingTimeSource(PausingTimeSource):
    """The slow monotonic read of ``PausingTimeSource``, which also arms the clock's rollback after the pause."""

    def __init__(self, clock: RollbackClock, rollback: timedelta) -> None:
        super().__init__(clock)
        self._rolling = clock
        self._step = rollback

    def monotonic(self) -> float:
        armed = self.pause is not None
        value = super().monotonic()
        if armed:
            self._rolling.rollback = self._step
        return value


def test_4334622032_a_capability_expired_at_receipt_is_refused_after_a_rollback(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    clock = RollbackClock(rig.clock.now())
    time = ArmingTimeSource(clock, timedelta(seconds=0.5))
    rig.clock, rig.time, rig.store = clock, time, FlakyStore()
    rig.ledger = Ledger(tmp_path / "rollback.sqlite", clock, rig.store, rig.faults)
    rig.gate = CapabilityGate(rig.ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    rig.tick()
    capability = issue(rig.epoch(), "a", expiry=clock.now() + timedelta(seconds=0.5))
    # The decision reads t, the monotonic read takes 0.75 s, the intent's receipt t + 0.75 is past the expiry; the
    # wall clock then steps back 0.5 s, inside the slew tolerance of 1 s.
    time.pause = timedelta(seconds=0.75)
    assert rig.refused(capability) == "expired"
    assert clock.now() < capability.expiry  # the rolled-back clock reads before the expiry again
    # The refusal was persisted at the receipt that showed the expiry, so the high-water mark refuses the
    # stepped-back clock; at 44aa596 it was persisted at the rolled-back time and this presentation was acknowledged.
    assert rig.refused(capability) == "clock_rollback"
    rig.tick()  # once the clock is past the high-water mark again, the capability is past its expiry
    assert rig.refused(capability) == "expired"
    state = rig.gate.state()
    assert state.level == "RESEARCH_ONLY" and not state.intents and not state.commits


def test_4335196673_replay_refuses_content_available_after_its_receipt(tmp_path: Path) -> None:
    clock = ManualClock(content_of({"r": {"v": 1}}).available_at)
    ledger = Ledger(tmp_path / "l.sqlite", clock)
    late = content_of({"r": {"v": 1}}, available=5)  # available at day 5, received at day 0
    ledger.append(KIND_CONTENT, f"content:{late.sha256}", late.to_payload())  # written past the registry's check
    with pytest.raises(Refusal) as refused:
        replay_state(ledger.records())
    assert refused.value.reason == "evidence_after_receipt"  # at 44aa596: admitted on replay


@pytest.mark.parametrize("seed", [None, True, 1.5, "1"])
def test_4335327806_the_leak_detector_refuses_a_seed_that_is_not_an_integer(seed: object) -> None:
    with pytest.raises(Refusal) as refused:
        detect_leak([0.9, 0.1], [1, 0], bound=0.05, permutations=10, seed=seed)  # type: ignore[arg-type]
    assert refused.value.reason == "invalid_seed"  # at 44aa596: None seeds from system entropy
