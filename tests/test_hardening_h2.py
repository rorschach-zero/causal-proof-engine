"""Hardening pass H2 (capability gate): the six findings of Codex's automatic review of PR #25 at 050ff07 that the
owner's delegate decided to fix on 2026-10-21. Each test fails at dd8af3f (H1) and passes after the fix."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cpe.capability.records import gate_ledger_id
from cpe.capability import ACTIONS, CapabilityGate, ManualTimeSource
from cpe.capability.timesource import ClockReading
from cpe.capability.records import KIND_COMMIT, CommitRecord
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from tests.test_capability import ENV, OWNER, RELEASE, TOLERANCE, Rig, issue


@pytest.fixture
def rig(tmp_path: Path) -> Rig:
    return Rig(tmp_path)


def test_4333626167_a_lower_commit_after_an_unanchored_higher_one_aborts(rig: Rig) -> None:
    other = CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)  # a second gate on the same ledger
    epoch = rig.epoch()
    rig.tick()
    outcomes: list[str] = []

    def first_gate_commits() -> None:  # lands after the second gate's intent anchor, before its step 3
        intent_id = next(i for i, x in rig.gate.state().intents.items() if x.capability.nonce == "high")
        anchor = rig.ledger.local_anchors()[-1]
        reading = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())  # the other gate's own
        rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent_id),
                          CommitRecord(intent_id, anchor.prefix_length, anchor.digest, reading).to_payload())

    def second_gate_presents_a_lower_capability() -> None:
        other.hooks["after_intent_anchor"] = first_gate_commits
        try:
            outcomes.append(other.promote(issue(epoch, "low", level="SHADOW_LIVE_QUOTES"),
                                          {"bundle": "gate-evidence-1", "tests": 182}).status)
        except Refusal as refusal:
            outcomes.append(refusal.reason)
        raise RuntimeError("the first gate stops after its commit")

    rig.gate.hooks["after_intent_anchor"] = second_gate_presents_a_lower_capability
    with pytest.raises(RuntimeError):
        rig.promote(issue(epoch, "high", level="SIM_EXECUTION"))
    assert outcomes == ["superseded"]  # never a commit below a commit already written in the epoch
    state = rig.gate.state()
    assert {state.intents[i].target_level for i in state.commits} == {"SIM_EXECUTION"}


def test_4333626175_a_discontinuity_before_the_acknowledgement_supersedes_the_promotion(rig: Rig) -> None:
    rig.tick()
    rig.gate.hooks["after_commit_anchor"] = lambda: rig.time.reboot("boot-2")
    outcome = rig.promote(issue(rig.epoch(), "a"))
    assert outcome.status == "superseded" and outcome.level == "RESEARCH_ONLY"
    assert rig.gate.state().level == "RESEARCH_ONLY"


class RollingBackTimeSource(ManualTimeSource):
    """Reading the monotonic clock rolls the wall clock back below the high-water mark once: the decision's clock
    sample passed, the append's own sample does not."""

    def __init__(self, clock: ManualClock) -> None:
        super().__init__(clock)
        self.roll_back_to: datetime | None = None

    def monotonic(self) -> float:
        if self.roll_back_to is not None:
            self._clock.set(self.roll_back_to)
            self.roll_back_to = None
        return super().monotonic()


def test_4333626183_a_rollback_at_the_append_sample_is_logged(rig: Rig, caplog: pytest.LogCaptureFixture) -> None:
    time = RollingBackTimeSource(rig.clock)
    rig.time = time
    rig.gate = CapabilityGate(rig.ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    rig.tick(10)
    rig.gate.perform("research")
    time.roll_back_to = rig.clock.now() - timedelta(seconds=5)
    with caplog.at_level(logging.WARNING, logger="cpe.capability"), pytest.raises(Refusal) as refused:
        rig.gate.perform("research")
    assert refused.value.reason == "clock_rollback"
    assert any("clock_rollback" in r.getMessage() for r in caplog.records if r.name == "cpe.capability")


def test_4333626186_the_action_table_is_read_only() -> None:
    with pytest.raises(TypeError):
        ACTIONS["sim_execution"] = "RESEARCH_ONLY"  # type: ignore[index]
    assert ACTIONS["sim_execution"] == "SIM_EXECUTION"


@pytest.mark.parametrize("monotonic, boot_id", [(-1.0, "boot-1"), (0.0, " ")])
def test_4333626188_a_faulty_time_source_never_poisons_the_ledger(tmp_path: Path, monotonic: float, boot_id: str) -> None:
    clock = ManualClock(datetime(2026, 1, 1, tzinfo=__import__("datetime").timezone.utc))
    ledger = Ledger(tmp_path / "l.sqlite", clock)
    with pytest.raises(Refusal):
        CapabilityGate(ledger, OWNER, ManualTimeSource(clock, monotonic, boot_id), ENV, RELEASE, TOLERANCE)
    assert ledger.state.count == 0


class SettlingGate(CapabilityGate):
    """A gate whose start-up abort is overtaken: between its snapshot of the pending intents and its abort, the
    first gate's step 3 lands (simulated by appending the commit record the first gate would write)."""

    overtake: object = None

    def _abort(self, intent_id: str, reason: str):  # type: ignore[no-untyped-def]
        overtake = type(self).overtake
        if callable(overtake):
            type(self).overtake = None
            overtake(intent_id)
        return super()._abort(intent_id, reason)


def test_4333626194_a_start_up_abort_skips_an_intent_another_gate_has_committed(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    rig.tick()

    def killed() -> None:
        raise RuntimeError("the first gate stops after its intent anchor")

    rig.gate.hooks["after_intent_anchor"] = killed
    with pytest.raises(RuntimeError):
        rig.promote(a)
    anchor = rig.ledger.local_anchors()[-1]

    def first_gate_commits(intent_id: str) -> None:
        reading = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())  # the other gate's own
        record = CommitRecord(intent_id, anchor.prefix_length, anchor.digest, reading)
        rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent_id), record.to_payload())

    SettlingGate.overtake = first_gate_commits
    rig.tick()
    late_starter = SettlingGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)
    state = late_starter.state()  # replays: no abort was written after the commit
    assert len(state.commits) == 1 and not state.aborted and state.level == "RESEARCH_ONLY"
