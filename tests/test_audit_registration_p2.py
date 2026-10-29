"""Whole-codebase audit, pass 4 (issue #37): finding R1 (P2). When the anchor that covers the confirmatory register
had landed in the external store but its acknowledgement was lost, the anchor stayed pending locally. A round
published after it, supplied meanwhile, was recorded as refused (``register_not_anchored``) and bound for good:
once the anchor settled, the claim read confirmatory, yet its calibration could never draw a seed. An unconfirmed
attempt that may have anchored the register before the round now refuses the round without recording it. The first
two tests failed on the pass-4 commit ``c3d6233dbaeb71eb71cb128394099b23cef285b5``."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.clock import ManualClock, parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger
from cpe.registration import BeaconOutput, CalibrationRecord, ConfirmatoryRegister, RegistrationRegistry
from tests.test_audit_pass3_claim_status import claim
from tests.test_registration import day
from tests.test_schemas import HEX

KIND_ROUND_REFUSED = "beacon_round_refused"


class AcknowledgementLost(HarnessAnchorStore):
    """The store commits the anchor, then the call fails: the anchor stays pending locally."""

    def __init__(self) -> None:
        super().__init__()
        self.fail_next = False

    def publish(self, anchor: Anchor) -> None:
        super().publish(anchor)
        if self.fail_next:
            self.fail_next = False
            raise Refusal("anchor_store_unavailable", "acknowledgement lost")


def setup(tmp_path: Path, calibration_settled: bool) -> tuple[Ledger, ManualClock, AcknowledgementLost]:
    """claim-1, cal-1 and the register; the anchor covering the register is held by the store at day 11 and pending
    locally. With ``calibration_settled``, cal-1 was anchored and confirmed at day 10 first."""
    clock = ManualClock(day(1))
    store = AcknowledgementLost()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    registry = RegistrationRegistry(ledger)
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    if calibration_settled:
        clock.set(day(10))
        ledger.anchor()
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(11))
    store.fail_next = True
    with pytest.raises(Refusal):
        ledger.anchor()
    assert len(ledger.local_anchors()) == (1 if calibration_settled else 0)  # the day-11 anchor is pending
    clock.set(day(13))
    return ledger, clock, store


@pytest.mark.parametrize("calibration_settled, reason", [(True, "anchor_pending"), (False, "round_before_anchor")])
def test_r1_a_round_after_an_unconfirmed_register_anchor_is_not_bound(tmp_path: Path, calibration_settled: bool,
                                                                      reason: str) -> None:
    ledger, clock, store = setup(tmp_path, calibration_settled)
    round_7 = BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12))
    with pytest.raises(Refusal) as refused:
        RegistrationRegistry(ledger).supply_beacon_output(round_7)
    assert refused.value.reason == reason  # at c3d6233: recorded as refused, for good
    assert KIND_ROUND_REFUSED not in [r.kind for r in ledger.records()]
    clock.set(day(14))
    ledger.close()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)  # reopening settles the held anchor at day 11
    registry = RegistrationRegistry(ledger)
    assert parse_timestamp(ledger.local_anchors()[-1].published_at) == day(11)
    assert registry.claim_status("claim-1") == "confirmatory"
    _, seed = registry.supply_beacon_output(round_7)
    assert seed == registry.seed_of("cal-1")


def test_an_unconfirmed_anchor_after_the_round_still_records_it(tmp_path: Path) -> None:
    ledger, clock, _ = setup(tmp_path, True)
    with pytest.raises(Refusal) as refused:  # published at day 10.5, before even the pending attempt at day 11
        RegistrationRegistry(ledger).supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(10.5)))
    assert refused.value.reason == "register_not_anchored"
    assert [r.kind for r in ledger.records()].count(KIND_ROUND_REFUSED) == 1
