"""Whole-codebase audit, pass 4 (issue #37): the findings of the Codex review of PR #56 (R1).

- ``4353231816`` (P1, a regression of PR #56): an anchor attempt that never reached the store stayed pending after a
  later, larger anchor succeeded and so proved it had not landed. ``supply_beacon_output`` took the disproved attempt
  as a possibly timely anchor of the register, refused the round without recording it, and ``claim_status`` stayed
  confirmatory although the register was anchored after the round (RC-311).
- ``4353231824`` (P2): the registry read the local anchors and the pending attempts in two calls; an attempt that
  settled between them was in neither set, and the round was recorded as refused for good (R1 again).

Both tests failed on the head of PR #56, ``d657ab7b7300e53d054e70a6a79f0e65a46d369e``."""
from __future__ import annotations

import threading
from pathlib import Path

import pytest

from cpe.pointintime import FeatureRow, PointInTimeStore
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger
from cpe.registration import BeaconOutput, CalibrationRecord, ConfirmatoryRegister, RegistrationRegistry
from tests.test_audit_pass3_claim_status import claim
from tests.test_registration import day
from tests.test_schemas import HEX

KIND_ROUND_REFUSED = "beacon_round_refused"


class Switchable(HarnessAnchorStore):
    """``lose_next``: the next publish never reaches the store. ``land_then_fail``: it lands, then the call fails."""

    def __init__(self) -> None:
        super().__init__()
        self.lose_next = False
        self.land_then_fail = False

    def publish(self, anchor: Anchor) -> None:
        if self.lose_next:
            self.lose_next = False
            raise Refusal("anchor_store_unavailable", "the call never reached the store")
        super().publish(anchor)
        if self.land_then_fail:
            self.land_then_fail = False
            raise Refusal("anchor_store_unavailable", "the acknowledgement was lost")


def registered(tmp_path: Path) -> tuple[Ledger, ManualClock, Switchable, RegistrationRegistry]:
    """claim-1 and cal-1, anchored and confirmed at day 10; the register written after it, not yet anchored."""
    clock = ManualClock(day(1))
    store = Switchable()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    registry = RegistrationRegistry(ledger)
    registry.register_claim(claim())
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    clock.set(day(10))
    ledger.anchor()
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    return ledger, clock, store, registry


def test_4353231816_a_disproved_attempt_is_no_possible_anchor(tmp_path: Path) -> None:
    ledger, clock, store, registry = registered(tmp_path)
    clock.set(day(11))
    store.lose_next = True
    with pytest.raises(Refusal):
        ledger.anchor()  # never landed; pending locally
    PointInTimeStore(ledger).ingest(FeatureRow("filler", "f", 1, day(0), day(0), "v1"))  # a kind replay knows (pass 6 P6-R1)
    clock.set(day(13))
    ledger.anchor()  # the register's real anchor, at day 13; the store holds no day-11 attempt
    clock.set(day(14))
    with pytest.raises(Refusal) as refused:
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    assert refused.value.reason == "register_not_anchored"  # at d657ab7: anchor_pending, nothing recorded
    assert registry.claim_status("claim-1") == "exploratory"  # at d657ab7: "confirmatory"


def test_4353231824_an_attempt_settling_during_the_snapshot_is_seen(tmp_path: Path) -> None:
    ledger, clock, store, registry = registered(tmp_path)
    clock.set(day(11))
    store.land_then_fail = True
    with pytest.raises(Refusal):
        ledger.anchor()  # landed at day 11, pending locally
    clock.set(day(13))
    original = ledger._local_anchors_locked

    def settle_concurrently() -> tuple[Anchor, ...]:
        anchors = original()
        ledger._local_anchors_locked = original  # type: ignore[method-assign]
        writer = threading.Thread(target=ledger.anchor)  # another writer settles the held attempt
        writer.start()
        writer.join(timeout=0.5)  # it waits for the ledger's lock while the snapshot holds it
        settle_concurrently.writer = writer  # type: ignore[attr-defined]
        return anchors

    ledger._local_anchors_locked = settle_concurrently  # type: ignore[method-assign]
    with pytest.raises(Refusal):
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    settle_concurrently.writer.join()  # type: ignore[attr-defined]
    assert KIND_ROUND_REFUSED not in [r.kind for r in ledger.records()]  # at d657ab7: recorded, for good
    _, seed = registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    assert seed == registry.seed_of("cal-1")
