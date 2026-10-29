"""Whole-codebase audit, pass 6 (issue #37), at ``1dca8d75ab6f49a82397cd493714d8602131538b``: the public snapshot of the
pre-registration registry.

- Codex 6-2 (PR #73 review comment 4415890506; decided as a P2 defect by the coordinator on 2026-10-29, reading P6-R2):
  ``RegistrationRegistry.state()`` returned every forecast, value included, before the event's issuance window closed,
  while ``forecasts_of`` refused the same read (RC-109). The public snapshot now leaves out the forecasts of every event
  whose window is still open at the ledger clock; the unredacted state is internal to the registry's decisions.

``test_6_2_*`` failed on the pass-6 commit."""
from __future__ import annotations

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.registration import RegistrationRegistry
from tests.test_registration import clock, day, forecast, ledger, registry  # noqa: F401


def test_6_2_the_public_snapshot_holds_no_sealed_forecast(registry: RegistrationRegistry, ledger: Ledger,  # noqa: F811
                                                          clock: ManualClock) -> None:  # noqa: F811
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1", point=0.8))
    with pytest.raises(Refusal) as sealed:
        registry.forecasts_of("E-1")
    assert sealed.value.reason == "read_before_close"
    state = registry.state()  # at 1dca8d7: forecasts[("E-1", "FULL", "primary")].forecast.point == 0.8
    assert not any(key[0] == "E-1" for key in state.forecasts)
    assert "E-1" not in state.forecasts_by_event and not any(key[0] == "E-1" for key in state.submissions)
    assert state.events["E-1"] is not None  # what is not sealed stays in the snapshot


def test_6_2_after_the_close_the_snapshot_shows_the_forecast(registry: RegistrationRegistry, ledger: Ledger,  # noqa: F811
                                                             clock: ManualClock) -> None:  # noqa: F811
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1", point=0.8))
    clock.set(day(41))  # the window of E-1 closes at day 40
    state = registry.state()
    assert state.forecasts[("E-1", "FULL", "primary")].forecast.point == 0.8
    assert [f.forecast.point for f in registry.forecasts_of("E-1")] == [0.8]
