"""Whole-codebase audit, pass 7 (issue #37), at ``c55e4cee65656355850bde32b07059e37d8b523b``: reopening with an
unreachable anchor store.

- Codex 7-3 (PR #82 review comment 4416532460): an anchor attempt whose publish failed stays pending, and a ledger
  opened while the store is unreachable keeps every pending row pending (``Ledger._reconcile_pending_anchors``,
  PR #20 decision in ``research/19`` section 9.1). Only a typed ``Refusal`` from the store was read as unreachable: a
  transport error such as ``TimeoutError`` escaped the constructor, so the ledger could not be opened at all while
  the store was down, although the gate treats the same error as an unconfirmed anchor (``CapabilityGate._try_anchor``).
  Any ``Exception`` from the store now leaves the rows pending, the clock bound and the demoted-unanchored state with
  them.

The first test failed on the pass-7 pin."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.capability import CapabilityGate
from cpe.errors import Refusal
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger
from tests.test_capability import ENV, OWNER, RELEASE, TOLERANCE, Rig


class TimingOutStore:
    """The harness store behind a transport that times out: on publishing while ``publish_down``, on every call while
    ``down``."""

    def __init__(self) -> None:
        self.inner = HarnessAnchorStore()
        self.publish_down = False
        self.down = False

    def publish(self, anchor: Anchor) -> None:
        if self.down or self.publish_down:
            raise TimeoutError("anchor transport timed out")
        self.inner.publish(anchor)

    def anchors(self) -> tuple[Anchor, ...]:
        if self.down:
            raise TimeoutError("anchor transport timed out")
        return self.inner.anchors()


def test_codex7_3_a_ledger_opens_while_the_store_times_out(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    store = TimingOutStore()
    ledger = Ledger(tmp_path / "t.sqlite", rig.clock, store)
    rig.tick()
    store.publish_down = True
    gate = CapabilityGate(ledger, OWNER, rig.time, ENV, RELEASE, TOLERANCE)  # the start rotation is not anchored
    assert gate.state().epoch_unanchored
    pending = ledger.pending_anchors()
    assert len(pending) == 1
    ledger.close()
    store.down = True
    rig.tick()
    reopened = Ledger(tmp_path / "t.sqlite", rig.clock, store)  # at c55e4ce: TimeoutError
    assert reopened.pending_anchors() == pending
    restarted = CapabilityGate(reopened, OWNER, rig.time, ENV, RELEASE, TOLERANCE)
    with pytest.raises(Refusal) as refused:
        restarted.perform("research")
    assert refused.value.reason == "epoch_unanchored"
    store.down = store.publish_down = False
    rig.tick()
    assert restarted.anchor_epoch()
    restarted.perform("research")
