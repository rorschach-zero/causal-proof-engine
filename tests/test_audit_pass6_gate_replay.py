"""Whole-codebase audit, pass 6 (issue #37), at ``1dca8d75ab6f49a82397cd493714d8602131538b``: gate replay.

- E1 (P1): replay took a ``gate_epoch`` row's epoch identifier as written. A row repeating an epoch the ledger had
  already rotated away from, appended through ``Ledger.append`` and anchored, made a capability signed for that epoch,
  and never presented in it, promote the gate to ``SIM_READ_ONLY``: the rotation is what invalidates every
  outstanding capability (RC-73, RC-100, RC-123), and the identifier is drawn fresh so that no rotation repeats one
  (``EpochRecord``; RC-123 (ii)). Replay now admits an epoch row only under the identifier the gate gives it and only
  with an identifier no earlier rotation of the ledger carried (class W of pass 4).

``test_e1_*`` failed on the pass-6 commit; the last test checks that the epochs the gate writes still replay."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.canonical import digest_of
from cpe.capability.records import KIND_EPOCH, EpochRecord
from cpe.errors import Refusal
from tests.test_audit_pass4_replay import reading_of
from tests.test_capability import EVIDENCE, RELEASE, Rig, issue


@pytest.mark.parametrize("canonical", [False, True], ids=["chosen identifier", "canonical identifier"])
def test_e1_a_repeated_epoch_does_not_revive_its_capabilities(tmp_path: Path, canonical: bool) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    old = rig.epoch()
    signed = issue(old, "outstanding")  # signed for the epoch of this process, never presented in it
    rig.restart()  # the start rotates the epoch: every outstanding capability is invalid (RC-123)
    with pytest.raises(Refusal) as stale:
        rig.gate.promote(signed, EVIDENCE)
    assert stale.value.reason == "stale_epoch"
    rig.tick()
    forged = EpochRecord(old, rig.index() + 1, "start", reading_of(rig), RELEASE)
    record_id = f"gate-epoch:{digest_of([str(forged.index), str(forged.epoch)])}" if canonical else "gate-epoch:forged"
    rig.ledger.append(KIND_EPOCH, record_id, forged.to_payload())
    rig.ledger.anchor()
    rig.tick()
    with pytest.raises(Refusal) as refused:
        rig.gate.promote(signed, EVIDENCE)  # at 1dca8d7: acknowledged at SIM_READ_ONLY
    assert refused.value.reason == "invalid_gate_ledger"


def test_every_epoch_the_gate_writes_is_new(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    for _ in range(3):
        rig.tick()
        rig.gate.demote("test")
    rig.restart()
    epochs = [EpochRecord.from_payload(r.payload).epoch for r in rig.ledger.records() if r.kind == KIND_EPOCH]
    assert len(epochs) == len(set(epochs)) == 5
    rig.tick()
    assert rig.gate.anchor_epoch()
    rig.gate.promote(issue(rig.epoch(), "fresh"), EVIDENCE)
    rig.gate.perform("sim_read")
