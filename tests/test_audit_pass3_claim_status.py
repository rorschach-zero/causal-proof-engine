"""Whole-codebase audit, pass 3 (issue #37): finding F4 (P1). A claim listed in a register anchored after the beacon
round of a calibration record bound to a Phase 1 claim is exploratory (RC-311, ``18`` M-1 (i)). The registry learns
the round's publication time when the round is supplied, and refuses it; it now writes that refusal at its receipt,
so ``claim_status`` reads it. The first test failed on the pass-3 audit commit
``b48c952c67c4d4358f82d3f811f744d47bdeb0b4``."""
from __future__ import annotations

import hashlib
import json

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.registration import BeaconOutput, CalibrationRecord, ClaimPreregistration, ConfirmatoryRegister
from cpe.registration import RegistrationRegistry
from cpe.registration.registry import KIND_BEACON, replay_state
from tests.test_registration import clock, day, ledger, registry  # noqa: F401
from tests.test_schemas import HEX

KIND_ROUND_REFUSED = "beacon_round_refused"  # the record kind of a refused round, as persisted


def claim() -> ClaimPreregistration:
    return ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1")


def calibrated(registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    """claim-1 and its calibration record cal-1, which names round-7, anchored at day 11."""
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    clock.set(day(11))
    ledger.anchor()


def test_f4_a_claim_whose_register_was_anchored_after_the_round_is_exploratory(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    calibrated(registry, ledger, clock)
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(13))
    ledger.anchor()  # the register is anchored at day 13
    assert registry.claim_status("claim-1") == "confirmatory"  # nothing shows a round before the anchor yet
    clock.set(day(14))
    round_7 = BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12))  # published at day 12, before the anchor
    with pytest.raises(Refusal) as refused:
        registry.supply_beacon_output(round_7)
    assert refused.value.reason == "register_not_anchored"
    assert registry.claim_status("claim-1") == "exploratory"  # at b48c952: "confirmatory"
    assert replay_state(ledger.records()).refused_rounds == {"cal-1": round_7}
    with pytest.raises(Refusal) as again:  # supplied again: refused again, written once
        registry.supply_beacon_output(round_7)
    assert again.value.reason == "register_not_anchored"
    assert [r.kind for r in ledger.records()].count(KIND_ROUND_REFUSED) == 1
    with pytest.raises(Refusal):
        registry.seed_of("cal-1")  # no seed is ever drawn from the refused round


def test_f4_a_round_published_before_any_anchor_of_the_register_is_recorded(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    calibrated(registry, ledger, clock)
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(14))
    with pytest.raises(Refusal) as refused:  # the register has no anchor yet
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    assert refused.value.reason == "register_not_anchored"
    ledger.anchor()  # the register is anchored at day 14, after the round
    assert registry.claim_status("claim-1") == "exploratory"


def test_f4_a_register_anchored_before_the_round_keeps_its_claim_confirmatory(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(11))
    ledger.anchor()  # the calibration record and the register are anchored at day 11
    clock.set(day(13))
    registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    assert registry.claim_status("claim-1") == "confirmatory"
    kinds = [r.kind for r in ledger.records()]
    assert KIND_BEACON in kinds and KIND_ROUND_REFUSED not in kinds


def test_f4_the_refusal_record_has_its_golden_identifier(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    calibrated(registry, ledger, clock)
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(13))
    ledger.anchor()
    clock.set(day(14))
    with pytest.raises(Refusal):
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    refusal = next(r for r in ledger.records() if r.kind == KIND_ROUND_REFUSED)
    canonical = json.dumps(["cal-1"], sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    assert refusal.record_id == "round-refused:" + hashlib.sha256(canonical.encode("ascii")).hexdigest()
