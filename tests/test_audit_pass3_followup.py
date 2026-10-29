"""Whole-codebase audit, pass 3 (issue #37): the two findings of the Codex review of PR #48, ``4352111655`` and
``4352111663``. A beacon round attested as published before the confirmatory register's anchor is recorded whichever
timing check refuses it first, and a recorded round is never supplied again: the first attested time binds. The first
three tests failed on the head of PR #48, ``a109423ff5fb2a658fb844182af79808721bfd8b``, and on ``main``
after its merge, ``f77577a5c3f25b5be7c269478f548cef1848b653``."""
from __future__ import annotations

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.registration import BeaconOutput, CalibrationRecord, ConfirmatoryRegister, RegistrationRegistry
from tests.test_audit_pass3_claim_status import calibrated, claim
from tests.test_registration import clock, day, ledger, registry  # noqa: F401
from tests.test_schemas import HEX

KIND_ROUND_REFUSED = "beacon_round_refused"


def late_register(registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    """cal-1 anchored at day 11; the register listing claim-1 anchored at day 13."""
    calibrated(registry, ledger, clock)
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(13))
    ledger.anchor()
    clock.set(day(14))


def test_4352111655_a_recorded_round_is_never_supplied_again(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    late_register(registry, ledger, clock)
    with pytest.raises(Refusal):
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    with pytest.raises(Refusal) as again:  # the same round, now claimed after the anchor, with another value
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "cd" * 32, day(13.5)))
    assert again.value.reason == "register_not_anchored"  # at a109423: accepted, a seed drawn
    with pytest.raises(Refusal):
        registry.seed_of("cal-1")
    assert registry.claim_status("claim-1") == "exploratory"
    assert [r.kind for r in ledger.records()].count(KIND_ROUND_REFUSED) == 1


def test_4352111663_a_round_before_both_anchors_is_recorded(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(13))
    ledger.anchor()  # the calibration record and the register are first anchored at day 13
    clock.set(day(14))
    with pytest.raises(Refusal) as refused:
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    assert refused.value.reason == "round_before_anchor"  # the first check that refuses it
    assert registry.claim_status("claim-1") == "exploratory"  # at a109423: "confirmatory"
    assert [r.kind for r in ledger.records()].count(KIND_ROUND_REFUSED) == 1


def test_the_first_attested_time_binds_when_both_anchors_follow_it(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(11))
    ledger.anchor()
    with pytest.raises(Refusal) as early:  # attested as published at day 10.5, before both anchors
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(10.5)))
    assert early.value.reason == "round_before_anchor"
    clock.set(day(12))
    with pytest.raises(Refusal) as later:  # a later, contradictory attestation of the same round is not weighed
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    assert later.value.reason == "register_not_anchored"
    assert registry.claim_status("claim-1") == "exploratory"


def test_a_round_refused_only_for_the_calibration_anchor_can_be_corrected(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    with pytest.raises(Refusal) as early:  # no register yet: not recorded, the supplier's time can be corrected
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(9)))
    assert early.value.reason == "round_before_anchor"
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(12))
    registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    assert registry.seed_of("cal-1")
    assert KIND_ROUND_REFUSED not in [r.kind for r in ledger.records()]
