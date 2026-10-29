"""Regression tests for the review of PR #25 (Codex review at ef7b3a8), one per finding.

Each test fails at ef7b3a8 and passes after the fix.
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from cpe.capability import CapabilityGate
from cpe.capability.records import KIND_ABORT, KIND_CHECK
from cpe.errors import Refusal
from cpe.ledger import Anchor
from tests.test_capability import ENV, OWNER, RELEASE, Rig, issue


@pytest.fixture
def rig(tmp_path: Path) -> Rig:
    return Rig(tmp_path)


def test_4330333005_a_capability_naming_a_level_at_or_below_the_gate_is_refused(rig: Rig) -> None:
    epoch = rig.epoch()
    assert rig.promote(issue(epoch, "up", level="SIM_EXECUTION")).status == "acknowledged"
    for nonce, level in (("down", "RESEARCH_ONLY"), ("same", "SIM_EXECUTION")):
        assert rig.refused(issue(epoch, nonce, level=level)) == "not_a_promotion"
    assert rig.gate.state().level == "SIM_EXECUTION"  # a lowering never bypasses the rotating demotion path


@pytest.mark.parametrize("tolerance", [float("nan"), float("inf")])
def test_4330333012_a_non_finite_slew_tolerance_is_refused(rig: Rig, tolerance: float) -> None:
    with pytest.raises(Refusal) as refused:
        CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, tolerance)
    assert refused.value.reason == "invalid_tolerance"


def test_4330333020_a_transport_error_of_the_anchor_store_aborts_the_intent(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    publish = rig.store.publish

    def failing(anchor: Anchor) -> None:
        rig.store.publish = publish  # type: ignore[method-assign]
        raise OSError("connection reset by the anchor store")

    rig.store.publish = failing  # type: ignore[method-assign]
    assert rig.refused(a) == "anchor_failed"
    state = rig.gate.state()
    assert state.pending_intents == () and len(state.aborted) == 1 and state.level == "RESEARCH_ONLY"


def test_4330333029_a_clock_discontinuity_at_step_3_aborts_the_intent(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    rig.tick()
    rig.gate.hooks["after_intent_anchor"] = lambda: rig.time.reboot("boot-2")
    assert rig.refused(a) == "clock_discontinuity"
    state = rig.gate.state()
    assert state.pending_intents == () and len(state.aborted) == 1 and state.level == "RESEARCH_ONLY"


def test_4330333036_the_step_3_abort_persists_its_clock_reading(rig: Rig) -> None:
    a = issue(rig.epoch(), "a")
    rig.tick()

    def demote() -> None:
        rig.gate.demote("interleaved")
        rig.time.advance(timedelta(seconds=2))

    rig.gate.hooks["after_intent_anchor"] = demote
    assert rig.refused(a) == "superseded"
    abort = [r for r in rig.ledger.records() if r.kind == KIND_ABORT][-1]
    assert isinstance(abort.payload, dict)
    reading = abort.payload["reading"]
    assert isinstance(reading, dict) and reading["wall"] == abort.receipt_time and reading["boot_id"] == "boot-1"


def test_4330333047_an_unknown_action_is_refused_with_a_persisted_check(rig: Rig) -> None:
    rig.tick(3)
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("teleport")
    assert refused.value.reason == "unknown_action"
    last = rig.ledger.records()[-1]
    assert last.kind == KIND_CHECK and isinstance(last.payload, dict)
    reading = last.payload["reading"]
    assert last.payload["reason"] == "unknown_action" and isinstance(reading, dict) and reading["wall"] == last.receipt_time
