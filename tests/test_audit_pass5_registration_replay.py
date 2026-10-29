"""Whole-codebase audit, pass 5 (issue #37), at ``b34c7212ca688d72611c3fd09b4eba170f94b44b``: registration replay.

- X1 (P1): replay took forecast rows as written. A second forecast row for a filled slot, written through
  ``Ledger.append``, replaced the slot's value (RC-75: the second record is refused, the slot keeps the first), and a
  forecast row under another arm version filled the slot (RC-96). Replay now admits every row that sets what a
  forecast is judged against (arm versions, cutoff corrections, candidates, base rates, cluster registrations,
  forecasts) by the rule its write path applies, under the identifier the write path gives it; a row the registry
  would have refused refuses the ledger (class W of pass 4, extended: reading P5-R1).
- P3: a raw cutoff correction of an unknown arm version and a raw forecast on an unknown event raised ``KeyError``
  in replay; both are now the typed refusal of the class.

Every test but the last failed on the pass-5 commit; the last checks that the API's own ledger still replays."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.registration import BaseRate, CandidateEntry, RegistrationRegistry
from cpe.registration.registry import (
    KIND_CANDIDATE,
    KIND_CLUSTER,
    KIND_CUTOFF_CORRECTION,
    KIND_FORECAST,
    _ledger_id,
    replay_state,
)
from tests.test_registration import arm, clock, day, forecast, ledger, registration, registry, spec  # noqa: F401


def refuses(ledger: Ledger) -> None:  # noqa: F811
    with pytest.raises(Refusal) as refused:
        RegistrationRegistry(ledger).state()
    assert refused.value.reason == "invalid_record"


def test_x1_a_second_forecast_row_for_a_filled_slot_refuses_the_ledger(registry: RegistrationRegistry,  # noqa: F811
                                                                       ledger: Ledger, clock: ManualClock) -> None:
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1", point=0.3))
    ledger.append(KIND_FORECAST, _ledger_id("forecast", "E-1", "FULL", "primary", "2"),
                  forecast("E-1", point=0.9).to_payload())
    refuses(ledger)  # at b34c721: the FULL slot read 0.9


def test_x1_a_forecast_row_under_another_arm_version_refuses_the_ledger(registry: RegistrationRegistry,  # noqa: F811
                                                                        ledger: Ledger, clock: ManualClock) -> None:
    clock.set(day(21))
    ledger.append(KIND_FORECAST, _ledger_id("forecast", "E-1", "FULL", "primary", "1"),
                  forecast("E-1", version="FULL-2", point=0.9).to_payload())
    refuses(ledger)  # at b34c721: the FULL slot was filled


def test_x1_a_baseline_forecast_row_refuses_the_ledger(registry: RegistrationRegistry,  # noqa: F811
                                                       ledger: Ledger, clock: ManualClock) -> None:
    clock.set(day(21))
    ledger.append(KIND_FORECAST, _ledger_id("forecast", "E-1", "DESIGN_C", "primary", "1"),
                  forecast("E-1", arm_id="DESIGN_C", version="DESIGN_C-1").to_payload())
    refuses(ledger)  # RC-109: the baseline slot is computed, never submitted


def test_x1_a_cluster_row_after_e_i_refuses_the_ledger(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock)
    registry = RegistrationRegistry(ledger)
    registry.register_arm_version(arm("A-1", "2026-01-05"))
    registry.register_arm_version(arm("DESIGN_C-1", "2026-01-01"))
    registry.register_arm_version(arm("FULL-1", "2026-01-03", ["A-1"]))
    registry.commit_base_rate(BaseRate("RC-1", 0.2))
    registry.log_candidate(CandidateEntry("cand-E-1", "E-1", "src", day(1), "registered", "predicate match"))
    clock.set(day(60))  # after e_i (not_before, day 50): register_cluster refuses registration_after_e_i
    late = registration([spec("E-1")])
    ledger.append(KIND_CLUSTER, _ledger_id("cluster", "C-1"), late.to_payload())
    refuses(ledger)  # at b34c721: E-1 was registered, after its outcome could be known (RC-138)


def test_x1_a_candidate_row_listed_after_its_receipt_refuses_the_ledger(ledger: Ledger,  # noqa: F811
                                                                        clock: ManualClock) -> None:
    entry = CandidateEntry("cand-E-9", "E-9", "src", day(5), "registered", "predicate match")
    ledger.append(KIND_CANDIDATE, _ledger_id("candidate", "cand-E-9"), entry.to_payload())  # received at day 1
    refuses(ledger)  # RC-78: a listing time is at or before the entry's receipt


def test_p3_a_correction_row_of_an_unknown_version_is_a_typed_refusal(ledger: Ledger) -> None:  # noqa: F811
    ledger.append(KIND_CUTOFF_CORRECTION, _ledger_id("cutoff-correction", "X-1", "ev"),
                  {"arm_version_id": "X-1", "corrected_cutoff": "2026-01-01", "evidence_id": "ev"})
    refuses(ledger)  # at b34c721: KeyError


def test_p3_a_forecast_row_on_an_unknown_event_is_a_typed_refusal(ledger: Ledger) -> None:  # noqa: F811
    ledger.append(KIND_FORECAST, _ledger_id("forecast", "E-9", "FULL", "primary", "1"), forecast("E-9").to_payload())
    refuses(ledger)  # at b34c721: KeyError


def test_the_ledger_the_api_writes_still_replays(registry: RegistrationRegistry, ledger: Ledger,  # noqa: F811
                                                 clock: ManualClock) -> None:
    clock.set(day(15))
    registry.submit_forecast(forecast("E-1", point=0.3))  # before the window: kept, labelled, fills nothing
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1", point=0.4))
    registry.submit_forecast(forecast("E-2", arm_id="A", version="A-1", point=0.5))
    state = replay_state(ledger.records())
    assert state.forecasts[("E-1", "FULL", "primary")].forecast.point == 0.4
    assert state.submissions[("E-1", "FULL", "primary")] == 2
