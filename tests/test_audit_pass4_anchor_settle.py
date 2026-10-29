"""Codex review of PR #63, finding ``4414429445`` (P2): an anchor attempt the external store held, but whose
acknowledgement was lost, stayed pending after a later, larger anchor succeeded, because ``anchor()`` settled a held
attempt only at the current head. A round published after the held anchor was refused with ``anchor_pending``, and
nothing could unblock it but reopening the ledger. ``anchor()`` now settles every held attempt with the time the store
holds, as reconciliation at open does. The R1 test set-up is reused. Every test here failed on ``main``
``bba974d``."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.clock import parse_timestamp
from cpe.registration import BeaconOutput, RegistrationRegistry
from tests.test_audit_registration_p2 import setup
from tests.test_registration import day
from tests.test_schemas import HEX


@pytest.mark.parametrize("calibration_settled", [True, False])
def test_4414429445_a_larger_anchor_settles_a_held_attempt_without_a_reopen(tmp_path: Path,
                                                                           calibration_settled: bool) -> None:
    ledger, clock, _ = setup(tmp_path, calibration_settled)  # the day-11 anchor is held by the store, pending locally
    ledger.append("note", "n-1", {"x": 1})  # another record before the retry
    ledger.anchor()  # day 13, a larger prefix
    assert ledger.pending_anchors() == ()  # at bba974d: the held day-11 attempt stayed pending
    held = [a for a in ledger.local_anchors() if parse_timestamp(a.published_at) == day(11)]
    assert len(held) == 1  # settled with the time the store holds, not the time of the later attempt
    registry = RegistrationRegistry(ledger)
    assert registry.claim_status("claim-1") == "confirmatory"
    clock.set(day(14))
    _, seed = registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(12)))
    assert seed == registry.seed_of("cal-1")  # at bba974d: refused with anchor_pending, or round_before_anchor


def test_a_held_attempt_settles_once_and_the_later_anchor_is_kept(tmp_path: Path) -> None:
    ledger, _, store = setup(tmp_path, True)
    ledger.append("note", "n-1", {"x": 1})
    later = ledger.anchor()
    assert [a.prefix_length for a in ledger.local_anchors()] == sorted(a.prefix_length for a in store.anchors())
    assert ledger.local_anchors()[-1] == later
    assert ledger.anchor() == later  # the head is anchored: the store's anchor is returned, nothing is published
    assert len(store.anchors()) == len(ledger.local_anchors())
