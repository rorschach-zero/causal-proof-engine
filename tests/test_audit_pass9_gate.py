"""Whole-codebase audit, pass 9 (issue #37), at ``811ba9d6bd13996cec72da62c0179d1baf71c6f2``: gate replay reads no
reading below a wall time the ledger persisted before it.

P9-2 (class W; found by invariant 5 of PR #100): replay judged an intent's and a commit's reading by its boot
identifier and its drift from the epoch baseline only (pass 8 Codex 8-2). The protected operation takes no step on a
reading below the latest wall time a persisted reading observed, nor below a receipt the ledger holds: it refuses
``clock_rollback`` (RC-37, RC-65; ``17`` item 2 "Clock"). A commit appended raw with the epoch's start reading, below its
own intent's reading, was read and conferred its level. Replay now refuses a gate record of any kind whose reading is
below the latest persisted reading or the latest receipt before it. A raw row with a fresh, plausible reading cannot be
told from the gate's own; this closes the reading that is provably not the gate's.

Each test named p9_2 fails at the pin."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.capability import replay_gate
from cpe.capability.records import KIND_CHECK, KIND_COMMIT, CheckRecord, CommitRecord, gate_ledger_id
from cpe.capability.timesource import ClockReading
from cpe.errors import Refusal
from tests.test_capability import RULES, Rig, issue


def killed() -> None:
    raise RuntimeError("the gate stops after its intent anchor")


def intent_left_pending(rig: Rig) -> str:
    rig.tick()
    rig.gate.hooks["after_intent_anchor"] = killed
    with pytest.raises(RuntimeError):
        rig.promote(issue(rig.epoch(), "a"))
    (intent_id,) = rig.gate.state().intents
    return intent_id


def test_p9_2_a_commit_read_below_its_intent_confers_no_level(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    intent_id = intent_left_pending(rig)
    state = rig.gate.state()
    stale = state.baseline  # the epoch's start reading, a second before the intent's
    assert stale is not None and stale.wall < state.intents[intent_id].reading.wall
    anchor = rig.ledger.local_anchors()[-1]
    rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent_id),
                      CommitRecord(intent_id, anchor.prefix_length, anchor.digest, stale).to_payload())
    rig.ledger.anchor()
    rig.tick()
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("sim_read")  # at 811ba9d: admitted at SIM_READ_ONLY
    assert refused.value.reason == "invalid_gate_ledger" and "read below a wall time" in refused.value.detail


def test_p9_2_a_reading_below_an_earlier_receipt_is_refused_on_replay(tmp_path: Path) -> None:
    """A check whose reading is below the receipt of the record before it: the ledger clock was already past it."""
    rig = Rig(tmp_path)
    rig.tick()
    rig.gate.perform("research")
    records = rig.ledger.records()
    behind = ClockReading(rig.clock.now().replace(year=2025), 0.0, rig.time.boot_id())
    rig.ledger.append(KIND_CHECK, gate_ledger_id("gate-check", records[-1].entry_hash),
                      CheckRecord("action:research", "admitted", "", behind).to_payload())
    anchors = rig.ledger.local_anchors()
    with pytest.raises(Refusal) as refused:
        replay_gate(rig.ledger.records(), max(a.prefix_length for a in anchors), RULES, anchors)
    assert refused.value.reason == "invalid_gate_ledger"


def test_a_commit_with_its_own_fresh_reading_is_read_as_before(tmp_path: Path) -> None:
    """The reading another gate takes at its own commit is at or above every bound: replay reads it (the H2 cases)."""
    rig = Rig(tmp_path)
    intent_id = intent_left_pending(rig)
    anchor = rig.ledger.local_anchors()[-1]
    fresh = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())
    rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent_id),
                      CommitRecord(intent_id, anchor.prefix_length, anchor.digest, fresh).to_payload())
    rig.ledger.anchor()
    assert rig.gate.state().level == "SIM_READ_ONLY"
