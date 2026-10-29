"""T-15 (``17`` section 5; RC-09, RC-79, RC-86): the point-in-time store and its as-of read interface on fixture F-25,
cases (a) to (e), and the leak detector's positive control. Times are day offsets, as in F-25."""
from __future__ import annotations

import random
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from cpe.pointintime import AsOfReader, FeatureRow, PointInTimeStore, Vintage, detect_leak
from tests.test_adjudication import spec

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def day(n: float) -> datetime:
    return BASE + timedelta(days=n)


# Fixture F-25: one entity, one feature, rows (observed_at, available_at, vintage, value).
F25 = [(10, 12, "v1", 1.00), (10, 20, "v2", 1.50), (5, 25, "v3", 0.70), (30, 40, "v4", 2.00), (10, 50, "v6", 1.40)]

# The oracle of 17 section 5.1 (F-25) and T-15 (e): per observed_at, (vintage, value) at each cutoff.
ORACLE: dict[int, dict[int, tuple[str, float]]] = {
    11: {},
    12: {10: ("v1", 1.00)},
    19: {10: ("v1", 1.00)},
    20: {10: ("v2", 1.50)},
    24: {10: ("v2", 1.50)},
    25: {5: ("v3", 0.70), 10: ("v2", 1.50)},
    39: {5: ("v3", 0.70), 10: ("v2", 1.50)},
    40: {5: ("v3", 0.70), 10: ("v2", 1.50), 30: ("v4", 2.00)},
    49: {5: ("v3", 0.70), 10: ("v2", 1.50), 30: ("v4", 2.00)},
    50: {5: ("v3", 0.70), 10: ("v6", 1.40), 30: ("v4", 2.00)},
}


def f25_row(observed: int, available: int, vintage: str, value: float) -> FeatureRow:
    return FeatureRow("E1", "f", value, day(observed), day(available), vintage)


@pytest.fixture
def f25(tmp_path: Path) -> tuple[PointInTimeStore, Ledger]:
    clock = ManualClock(day(60))  # historical vintages ingested later, each with its attested available_at
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    store = PointInTimeStore(ledger)
    for row in F25:
        store.ingest(f25_row(*row))
    return store, ledger


def as_table(reader: AsOfReader) -> dict[int, tuple[str, float]]:
    series = reader.series("E1", "f")
    return {(observed - BASE).days: (v.vintage_id, float(str(v.value))) for observed, v in series.observations.items()}


# (e) positive oracles

@pytest.mark.parametrize("cutoff", sorted(ORACLE))
def test_t15_e_the_read_returns_exactly_the_oracle_series(f25: tuple[PointInTimeStore, Ledger], cutoff: int) -> None:
    store, _ = f25
    reader = store.reader(day(cutoff))
    assert as_table(reader) == ORACLE[cutoff]
    series = reader.series("E1", "f")
    assert series.empty == (ORACLE[cutoff] == {}) and series.as_of == day(cutoff)


def test_t15_e_an_empty_series_is_a_result_not_a_refusal(f25: tuple[PointInTimeStore, Ledger]) -> None:
    store, _ = f25
    empty = store.reader(day(11)).series("E1", "f")
    assert empty.empty and dict(empty.observations) == {}
    assert store.reader(day(50)).series("E1", "other-feature").empty


# (a) to (d): every read with available_at after the cutoff is refused

def refused(read: Callable[[], object]) -> str:
    with pytest.raises(Refusal) as refusal:
        read()
    return refusal.value.reason


def test_t15_a_a_later_vintage_of_a_revised_value_is_refused(f25: tuple[PointInTimeStore, Ledger]) -> None:
    store, _ = f25
    reader = store.reader(day(19))
    assert reader.row("E1", "f", "v1") == f25_row(*F25[0])
    assert refused(lambda: reader.row("E1", "f", "v2")) == "not_available"
    assert as_table(reader) == {10: ("v1", 1.00)}


def test_t15_b_a_publication_lagged_observation_is_refused(f25: tuple[PointInTimeStore, Ledger]) -> None:
    store, _ = f25
    reader = store.reader(day(39))  # observed at 30, before the cutoff; available at 40, after it
    assert refused(lambda: reader.row("E1", "f", "v4")) == "not_available"
    assert 30 not in as_table(reader)


def test_t15_c_a_backfilled_row_inserted_after_the_cutoff_is_refused(f25: tuple[PointInTimeStore, Ledger]) -> None:
    store, _ = f25
    reader = store.reader(day(24))  # period 5 backfilled at 25, after later periods exist
    assert refused(lambda: reader.row("E1", "f", "v3")) == "not_available"
    assert 5 not in as_table(reader)


def test_t15_d_a_post_cutoff_timestamp_is_refused(f25: tuple[PointInTimeStore, Ledger]) -> None:
    store, _ = f25
    reader = store.reader(day(24))
    assert refused(lambda: reader.series("E1", "f", as_of=day(25))) == "after_evidence_cutoff"
    assert refused(lambda: reader.row("E1", "f", "v1", as_of=day(50))) == "after_evidence_cutoff"
    assert as_table(store.reader(day(24))) == ORACLE[24]
    earlier = reader.series("E1", "f", as_of=day(19))  # an earlier as-of time inside the bound is a read
    assert dict(earlier.observations) == {day(10): Vintage("v1", 1.00)}


def test_t15_a_future_vintage_and_an_unknown_one_are_refused_alike(f25: tuple[PointInTimeStore, Ledger]) -> None:
    store, _ = f25
    reader = store.reader(day(19))
    with pytest.raises(Refusal) as future:
        reader.row("E1", "f", "v2")
    with pytest.raises(Refusal) as unknown:
        reader.row("E1", "f", "v9")
    # alike in reason and in detail, but for the vintage asked for: nothing says that v2 exists (issue #37, pass 7)
    assert future.value.reason == unknown.value.reason == "not_available"
    assert future.value.detail.replace("v2", "v9") == unknown.value.detail


def test_t15_the_reader_of_a_forecast_is_bound_to_the_event_evidence_cutoff(tmp_path: Path) -> None:
    event = spec()
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(event.evidence_cutoff + timedelta(days=1)), HarnessAnchorStore())
    store = PointInTimeStore(ledger)
    store.ingest(FeatureRow("E1", "f", 1, event.evidence_cutoff - timedelta(days=5), event.evidence_cutoff, "in"))
    store.ingest(FeatureRow("E1", "f", 2, event.evidence_cutoff - timedelta(days=5),
                            event.evidence_cutoff + timedelta(seconds=1), "out"))
    reader = store.reader_for(event)
    assert reader.evidence_cutoff == event.evidence_cutoff
    assert [v.vintage_id for v in reader.series("E1", "f").observations.values()] == ["in"]
    assert refused(lambda: reader.row("E1", "f", "out")) == "not_available"


# Readers that pass the refusal cases and fail the oracle, or fail both (16 Appendix I): the oracle discriminates

def refuse_all(rows: list[FeatureRow], cut: datetime) -> dict[int, tuple[str, float]]:
    raise Refusal("not_available", "every read refused")


def oldest_eligible(rows: list[FeatureRow], cut: datetime) -> dict[int, tuple[str, float]]:
    chosen: dict[datetime, FeatureRow] = {}
    for r in rows:
        if r.available_at <= cut and (r.observed_at not in chosen or r.available_at < chosen[r.observed_at].available_at):
            chosen[r.observed_at] = r
    return {(o - BASE).days: (r.vintage_id, float(str(r.value))) for o, r in sorted(chosen.items())}


def filters_on_observed_at(rows: list[FeatureRow], cut: datetime) -> dict[int, tuple[str, float]]:
    chosen: dict[datetime, FeatureRow] = {}
    for r in rows:
        if r.observed_at <= cut and (r.observed_at not in chosen or r.available_at > chosen[r.observed_at].available_at):
            chosen[r.observed_at] = r
    return {(o - BASE).days: (r.vintage_id, float(str(r.value))) for o, r in sorted(chosen.items())}


@pytest.mark.parametrize("reader, fails_refusals", [(refuse_all, False), (oldest_eligible, False),
                                                     (filters_on_observed_at, True)])
def test_t15_defective_readers_fail_the_oracle(reader: Callable[[list[FeatureRow], datetime],
                                                                dict[int, tuple[str, float]]],
                                               fails_refusals: bool) -> None:
    rows = [f25_row(*r) for r in F25]
    available = {r.vintage_id: r.available_at for r in rows}
    oracle_failures, refusal_failures = [], []
    for cutoff in sorted(ORACLE):
        try:
            got = reader(rows, day(cutoff))
        except Refusal:
            oracle_failures.append(cutoff)
            continue
        if got != ORACLE[cutoff]:
            oracle_failures.append(cutoff)
        if any(available[vintage] > day(cutoff) for vintage, _ in got.values()):
            refusal_failures.append(cutoff)
    assert oracle_failures
    assert bool(refusal_failures) == fails_refusals
    if reader is filters_on_observed_at:
        assert reader(rows, day(11))[10] == ("v6", 1.40)  # the classic leak: the second revision at cutoff 11


# Ingest

def test_ingest_refuses_a_row_available_after_its_receipt_and_a_rewritten_vintage(tmp_path: Path) -> None:
    clock = ManualClock(day(20))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    store = PointInTimeStore(ledger)
    assert refused(lambda: store.ingest(f25_row(10, 21, "v1", 1.0))) == "evidence_after_receipt"
    written = store.ingest(f25_row(10, 12, "v1", 1.0))
    assert store.ingest(f25_row(10, 12, "v1", 1.0)) == written
    assert refused(lambda: store.ingest(f25_row(10, 12, "v1", 9.0))) == "vintage_immutable"
    assert [r.kind for r in ledger.records()] == ["pit_row"]


def test_replay_of_the_export_gives_the_same_reads(f25: tuple[PointInTimeStore, Ledger], tmp_path: Path) -> None:
    store, ledger = f25
    restored, report = Ledger.restore(tmp_path / "restored.sqlite", ManualClock(day(60)),
                                      records_from_jsonl(ledger.export_jsonl()), HarnessAnchorStore())
    again = PointInTimeStore(restored)
    assert restored.state_digest() == ledger.state_digest()
    for cutoff in sorted(ORACLE):
        assert again.reader(day(cutoff)).series("E1", "f") == store.reader(day(cutoff)).series("E1", "f")


# The second line: the leak detector's positive control (an injected-outcome feature in a synthetic challenger)

BOUND, PERMUTATIONS, SEED = 0.05, 200, 20261021  # fixed for this fixture; the pre-registered values are OD fields


def challenger(tmp_path: Path, injected: bool) -> tuple[list[float], list[int]]:
    """A challenger that reads one feature per event through the as-of reader. With ``injected``, the feature is the
    outcome itself, attested as available before the cutoff (the leak the interface cannot see)."""
    generator = random.Random(7)
    outcomes = [1 if generator.random() < 0.3 else 0 for _ in range(120)]
    ledger = Ledger(tmp_path / f"challenger-{injected}.sqlite", ManualClock(day(30)), HarnessAnchorStore())
    store = PointInTimeStore(ledger)
    for i, outcome in enumerate(outcomes):
        value = outcome if injected else generator.randint(0, 1)
        store.ingest(FeatureRow(f"event-{i}", "signal", value, day(9), day(10), "v1"))
    reader = store.reader(day(11))
    forecasts = []
    for i in range(len(outcomes)):
        (vintage,) = reader.series(f"event-{i}", "signal").observations.values()
        forecasts.append(0.9 if vintage.value == 1 else 0.1)
    return forecasts, outcomes


def test_t15_leak_detector_flags_the_injected_outcome_feature(tmp_path: Path) -> None:
    forecasts, outcomes = challenger(tmp_path, injected=True)
    report = detect_leak(forecasts, outcomes, bound=BOUND, permutations=PERMUTATIONS, seed=SEED)
    assert report.flagged and report.inflation > BOUND
    assert len(report.null_briers) == PERMUTATIONS and report.brier < min(report.null_briers)
    assert detect_leak(forecasts, outcomes, bound=BOUND, permutations=PERMUTATIONS, seed=SEED) == report


def test_t15_leak_detector_on_an_unrelated_feature_of_this_fixture(tmp_path: Path) -> None:
    """A deterministic fixture beside the positive control, not a size claim: the detector does not flag
    everything."""
    forecasts, outcomes = challenger(tmp_path, injected=False)
    assert not detect_leak(forecasts, outcomes, bound=BOUND, permutations=PERMUTATIONS, seed=SEED).flagged
    constant = detect_leak([0.3] * len(outcomes), outcomes, bound=BOUND, permutations=PERMUTATIONS, seed=SEED)
    assert constant.inflation == pytest.approx(0.0) and not constant.flagged


@pytest.mark.parametrize("forecasts, outcomes, bound, permutations, reason", [
    ([], [], 0.05, 10, "invalid_sample"),
    ([0.5], [1, 0], 0.05, 10, "invalid_sample"),
    ([float("nan")], [1], 0.05, 10, "invalid_probability"),
    ([0.5], [2], 0.05, 10, "invalid_outcome"),
    ([0.5], [True], 0.05, 10, "invalid_outcome"),
    ([0.5], [1], -0.1, 10, "invalid_bound"),
    ([0.5], [1], float("inf"), 10, "invalid_bound"),
    ([0.5], [1], 0.05, 0, "invalid_permutations"),
])
def test_leak_detector_refuses_malformed_inputs(forecasts: list[float], outcomes: list[int], bound: float,
                                                permutations: int, reason: str) -> None:
    with pytest.raises(Refusal) as refusal:
        detect_leak(forecasts, outcomes, bound=bound, permutations=permutations, seed=1)
    assert refusal.value.reason == reason
