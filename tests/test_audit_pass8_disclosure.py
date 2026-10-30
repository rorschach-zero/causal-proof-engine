"""Whole-codebase audit, pass 8 (issue #37), at ``c37d04899c3f0c821825f7aee09ff79c900eb02a``: the release of sealed
forecasts bounds the clock.

Codex 8-1 (PR #87 review comment 4417203533, P1, class C): a read that released an event's forecasts after its
issuance close persisted no time, so after a clock rollback into the window another arm submitted a forecast it had
already seen: ``forecasts_of`` at day 41, the clock stepped back to day 30, and a submission at day 30 was admitted
(RC-109; ``17`` item 2 "Clock": a clock-dependent check is persisted before its verdict).

Reading P8-R2 (coordinator, 2026-10-29): the first disclosure of an event's sealed forecasts after its close is a
ledger row (``forecast_disclosure``, one per event); its receipt bounds the clock across reopen and restore. The
alternative, a ledger-local mark, was rejected because a restore would lose it. The row is written by the first read
that releases a forecast (``forecasts_of``, ``forecasts_for_baseline``, ``slot_states``, the public ``state``), against
its own receipt, and admitted on replay by the same rule.

Every test named codex8_1 failed at the pass-8 pin (with the kind name inlined, which the pin does not define); the
last test is the gap PR #95's review found (4418096591), which this PR, its successor, closes."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from cpe.registration import CandidateEntry, RegistrationRegistry
from cpe.registration.registry import KIND_DISCLOSURE, _ledger_id
from tests.test_registration import clock as clock, ledger as ledger, registry as registry  # noqa: F401 (fixtures)
from tests.test_registration import day, forecast, registration, spec

READS: dict[str, Callable[[RegistrationRegistry], object]] = {
    "forecasts_of": lambda r: r.forecasts_of("E-1"),
    "forecasts_for_baseline": lambda r: r.forecasts_for_baseline("E-1"),
    "slot_states": lambda r: r.slot_states("E-1"),
    "state": lambda r: r.state(),
}


def disclosures(ledger: Ledger) -> list[str]:
    return [r.record_id for r in ledger.records() if r.kind == KIND_DISCLOSURE]


@pytest.mark.parametrize("read", list(READS))
def test_codex8_1_a_forecast_read_after_the_close_bounds_every_later_submission(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock, read: str) -> None:
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1"))
    clock.set(day(41))
    READS[read](registry)  # FULL's forecast is released
    clock.set(day(30))  # back inside the window, above every receipt
    with pytest.raises(Refusal) as refused:
        registry.submit_forecast(forecast("E-1", "A", "A-1", 0.3))  # at c37d048: admitted, filling A's slot
    assert refused.value.reason == "clock_rollback"


def test_codex8_1_the_bound_survives_a_restore(registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock,
                                              tmp_path: Path) -> None:
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1"))
    clock.set(day(41))
    registry.forecasts_of("E-1")
    exported = records_from_jsonl(ledger.export_jsonl())
    restored, _ = Ledger.restore(tmp_path / "restored.sqlite", ManualClock(day(30)), exported,
                                 HarnessAnchorStore(ledger.local_anchors()))
    with pytest.raises(Refusal) as refused:
        RegistrationRegistry(restored).submit_forecast(forecast("E-1", "A", "A-1", 0.3))
    assert refused.value.reason == "clock_rollback"


def test_codex8_1_a_rollback_before_the_release_refuses_the_read(registry: RegistrationRegistry, ledger: Ledger,
                                                                clock: ManualClock) -> None:
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1"))
    clock.set(day(41))
    registry.before_write = lambda: clock.set(day(39))  # stepped back into the window before the row is received
    with pytest.raises(Refusal) as refused:
        registry.forecasts_of("E-1")  # no forecast is returned without its release on the ledger
    assert refused.value.reason == "read_before_close"
    assert disclosures(ledger) == []


def test_one_release_per_event_and_none_before_the_close(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1"))
    with pytest.raises(Refusal):
        registry.forecasts_of("E-1")  # sealed
    clock.set(day(41))
    for read in READS.values():
        read(registry)
    assert disclosures(ledger) == [_ledger_id("disclosure", "E-1")]  # E-2 is not read
    assert registry.forecasts_of("E-2") == ()  # E-2 has no forecast: its empty release is written too (pass 9 P9-1)
    assert disclosures(ledger) == [_ledger_id("disclosure", "E-1"), _ledger_id("disclosure", "E-2")]


def test_a_release_row_before_the_close_refuses_replay(registry: RegistrationRegistry, ledger: Ledger,
                                                      clock: ManualClock) -> None:
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1"))
    ledger.append(KIND_DISCLOSURE, _ledger_id("disclosure", "E-1"), {"event_id": "E-1"})  # inside the window
    with pytest.raises(Refusal) as refused:
        registry.event("E-1")
    assert refused.value.reason == "invalid_record" and "read_before_close" in refused.value.detail


def test_a_snapshot_releases_only_what_its_disclosure_rows_cover(registry: RegistrationRegistry, ledger: Ledger,
                                                                clock: ManualClock) -> None:
    """PR #95 review 4418096591 (P1, a gap of #95): ``state`` chose the events to release on one clock sample and
    sealed on a second, so an event that closed between the two was returned without its disclosure row, and after a
    rollback below its close another arm copied its forecast. The snapshot now decides on one sample and keeps every
    event without a disclosure row sealed."""
    registry.log_candidate(CandidateEntry("cand-E-3", "E-3", "src", day(1), "registered", "match"))
    registry.register_cluster(registration([spec("E-3", cluster_id="C-3", not_before=70, issuance=(20, 60))],
                                           cluster_id="C-3"))
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1"))
    registry.submit_forecast(forecast("E-3"))  # E-3 closes at day 60
    clock.set(day(41))
    sampled = ledger.now
    samples = 0

    def stepping() -> datetime:  # the clock reaches day 61 while E-1's disclosure is decided, after the snapshot's
        nonlocal samples      # own sample (issue #37, pass 9: this step was armed at a third sample, which never came)
        samples += 1
        moment = sampled()
        if samples == 2:
            clock.set(day(61))
        return moment

    ledger.now = stepping  # type: ignore[method-assign]
    snapshot = registry.state()
    ledger.now = sampled  # type: ignore[method-assign]
    assert samples == 2  # the snapshot's sample and the disclosure's: the step was taken
    assert sorted(snapshot.forecasts_by_event) == ["E-1"]  # at d5406dd: E-1 and E-3, E-3 without its row
    assert disclosures(ledger) == [_ledger_id("disclosure", "E-1")]  # E-3, closed by then, released nothing
