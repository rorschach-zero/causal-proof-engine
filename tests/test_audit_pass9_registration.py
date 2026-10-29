"""Whole-codebase audit, pass 9 (issue #37), at ``811ba9d6bd13996cec72da62c0179d1baf71c6f2``: a read that decides an
event's issuance close persists it, whether or not a forecast is sealed.

P9-1 (class C; found by invariant 7 of PR #100): ``forecasts_of``, ``forecasts_for_baseline`` and ``slot_states`` wrote
the event's disclosure row only when a forecast was sealed. For an event with none, a read after the close answered as
only a closed event can (an empty release; every slot an abstention, ``18`` M-5) and persisted nothing, so a clock
stepped back into the window, above every receipt, admitted a forecast that filled a slot the read had reported as an
abstention (RC-109; ``17`` item 2 "Clock": a clock-dependent check is persisted before its verdict; the 8-1
precedent). The first such read now writes the disclosure row (reading P8-R2), with or without a sealed forecast.

Each test named p9_1 fails at the pin."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from cpe.registration import RegistrationRegistry
from cpe.registration.registry import KIND_DISCLOSURE, _ledger_id
from tests.test_registration import clock as clock, ledger as ledger, registry as registry  # noqa: F401 (fixtures)
from tests.test_registration import day, forecast

READS: dict[str, Callable[[RegistrationRegistry], object]] = {
    "forecasts_of": lambda r: r.forecasts_of("E-2"),
    "forecasts_for_baseline": lambda r: r.forecasts_for_baseline("E-2"),
    "slot_states": lambda r: r.slot_states("E-2"),
}


@pytest.mark.parametrize("read", list(READS))
def test_p9_1_a_read_after_the_close_of_an_event_without_forecasts_bounds_every_later_submission(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock, read: str) -> None:
    clock.set(day(41))  # E-2 closed at day 40 with no forecast
    READS[read](registry)  # an empty release, or every slot an abstention
    assert [r.record_id for r in ledger.records() if r.kind == KIND_DISCLOSURE] == [_ledger_id("disclosure", "E-2")]
    clock.set(day(30))  # back inside the window, above every receipt
    with pytest.raises(Refusal) as refused:
        registry.submit_forecast(forecast("E-2"))  # at 811ba9d: admitted, filling the slot reported as an abstention
    assert refused.value.reason == "clock_rollback"


def test_p9_1_the_bound_survives_a_restore(registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock,
                                         tmp_path: Path) -> None:
    clock.set(day(41))
    assert {s.arm_id: s.status for s in registry.slot_states("E-2")}["FULL"] == "abstention"
    exported = records_from_jsonl(ledger.export_jsonl())
    restored, _ = Ledger.restore(tmp_path / "restored.sqlite", ManualClock(day(30)), exported,
                                 HarnessAnchorStore(ledger.local_anchors()))
    with pytest.raises(Refusal) as refused:
        RegistrationRegistry(restored).submit_forecast(forecast("E-2"))
    assert refused.value.reason == "clock_rollback"


def test_a_read_before_the_close_still_writes_nothing(registry: RegistrationRegistry, ledger: Ledger,
                                                     clock: ManualClock) -> None:
    clock.set(day(39))
    assert {s.arm_id: s.status for s in registry.slot_states("E-2")}["FULL"] == "open"
    with pytest.raises(Refusal):
        registry.forecasts_of("E-2")
    assert [r for r in ledger.records() if r.kind == KIND_DISCLOSURE] == []
