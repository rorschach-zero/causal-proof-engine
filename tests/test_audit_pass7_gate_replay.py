"""Whole-codebase audit, pass 7 (issue #37), at ``c55e4cee65656355850bde32b07059e37d8b523b``: gate replay.

- Codex 7-4 (PR #82 review comment 4416532472): replay admitted an intent received while its epoch was unanchored.
  ``CapabilityGate._validate`` refuses every presentation while the gate is demoted-unanchored (``epoch_unanchored``,
  ``17`` item 2 "Demotion without the anchor store", RC-123), but replay checked the epoch identifier only, so an
  intent appended through ``Ledger.append`` during that state, followed by an anchor covering both and the commit
  the gate writes, promoted the gate. Replay now admits an intent only when an anchor of a prefix covering its
  epoch's rotation was published at or before the intent's receipt; the anchors the gate replays with carry their
  publication times (PR #63), so this is the moment the online check saw.

The first test failed on the pass-7 pin; the second checks that the promotions the gate writes still replay."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.capability.records import KIND_COMMIT, KIND_INTENT, CommitRecord, IntentRecord, gate_ledger_id, intent_ledger_id
from cpe.errors import Refusal
from tests.test_audit_pass4_replay import reading_of
from tests.test_capability import EVIDENCE, Rig, issue


def test_codex7_4_an_intent_received_while_its_epoch_was_unanchored_confers_no_level(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    rig.store.available = False
    demoted = rig.gate.demote("operator")  # demoted-unanchored: every promotion is refused (RC-123)
    assert demoted.epoch_unanchored
    signed = issue(demoted.epoch, "during-outage")
    assert rig.refused(signed) == "epoch_unanchored"
    intent_id = intent_ledger_id(signed)
    rig.ledger.append(KIND_INTENT, intent_id, IntentRecord(intent_id, signed, "SIM_READ_ONLY",
                                                           reading_of(rig)).to_payload())
    rig.store.available = True
    rig.tick()
    anchor = rig.ledger.anchor()  # covers the rotation and the intent, published after the intent
    rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent_id),
                      CommitRecord(intent_id, anchor.prefix_length, anchor.digest, reading_of(rig)).to_payload())
    rig.ledger.anchor()
    rig.tick()
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("sim_read")  # at c55e4ce: admitted at SIM_READ_ONLY
    assert refused.value.reason == "invalid_gate_ledger"


def test_a_promotion_after_the_epoch_anchor_still_replays(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    rig.store.available = False
    demoted = rig.gate.demote("operator")
    rig.store.available = True
    rig.tick()
    assert rig.gate.anchor_epoch()
    rig.tick()
    assert rig.gate.promote(issue(demoted.epoch, "after-anchor"), EVIDENCE).status == "acknowledged"
    rig.tick()
    rig.gate.perform("sim_read")
    rig.restart()
    assert rig.gate.state().level == "RESEARCH_ONLY"
