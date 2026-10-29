"""Whole-codebase audit, pass 5 (issue #37), at ``b34c7212ca688d72611c3fd09b4eba170f94b44b``: the registration
registry.

- R2 (P2): a decision read the anchors with its snapshot, and the append was checked against the snapshot's chain
  head only; an anchor moves no chain head. When another writer anchored the register between the snapshot and the
  append, before the round was published, the round was still recorded as refused, and every later read of the
  registry refused the ledger (``check_anchor_times``: the register's anchor preceded the round). The append now
  expects the snapshot's anchors as well, and a decision that read stale anchors is recomputed.

The ``test_r2_*`` test failed on the pass-5 commit."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from cpe.clock import ManualClock
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger, Record
from cpe.registration import BeaconOutput, CalibrationRecord, ConfirmatoryRegister, RegistrationRegistry
from tests.test_audit_pass3_claim_status import claim
from tests.test_registration import day
from tests.test_schemas import HEX


def test_r2_an_anchor_landing_after_the_snapshot_recomputes_the_round(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = RegistrationRegistry(ledger)
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    clock.set(day(10))
    ledger.anchor()
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(11))
    original = ledger.snapshot
    landed: list[Anchor] = []

    def snapshot() -> tuple[tuple[Record, ...], tuple[Anchor, ...], tuple[Anchor, ...]]:
        taken = original()
        if not landed:  # another writer anchors the register right after this snapshot, at day 11.5
            clock.set(day(11) + timedelta(hours=12))
            landed.append(ledger.anchor())
            clock.set(day(12) + timedelta(hours=1))  # the decision's clock: after the round's publication
        return taken

    ledger.snapshot = snapshot  # type: ignore[method-assign]
    _, seed = registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    ledger.snapshot = original  # type: ignore[method-assign]
    # At b34c721 the round was recorded as refused against the stale anchors, and this read raised invalid_record.
    assert registry.claim_status("claim-1") == "confirmatory"
    assert registry.seed_of("cal-1") == seed
    assert "beacon_round_refused" not in [r.kind for r in ledger.records()]
