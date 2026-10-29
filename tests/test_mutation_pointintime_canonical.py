"""Mutation testing, ``cpe/pointintime`` and ``cpe/canonical``: tests that kill mutants the suite let survive at
ac4c640 (``research/19`` section "Mutation testing"). They pin the inclusive bounds of the as-of read (a row
available at its receipt, a read at the cutoff), the latest-vintage choice whatever the ingest order, the report of
the leak detector at its bounds, and the refusals of the canonical form."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.canonical import canonical_bytes, require_hex_digest
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger, Record
from cpe.pointintime import FeatureRow, PointInTimeStore, brier, detect_leak
from cpe.pointintime.store import _row_id, replay_state
from tests.test_point_in_time import day


def refused(call: object, *args: object, **kwargs: object) -> str:
    assert callable(call)
    with pytest.raises(Refusal) as refusal:
        call(*args, **kwargs)
    return refusal.value.reason


def store_at(tmp_path: Path, at: float) -> tuple[PointInTimeStore, Ledger, ManualClock]:
    clock = ManualClock(day(at))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    return PointInTimeStore(ledger), ledger, clock


# canonical ---------------------------------------------------------------------------------------------------------

def test_canonical_refusals_are_named() -> None:
    assert refused(canonical_bytes, {1: "a"}) == "non_string_key"
    assert refused(canonical_bytes, {"a": (1, 2)}) == "not_json"
    assert refused(canonical_bytes, [object()]) == "not_json"
    assert refused(require_hex_digest, "X" * 64, "d") == "invalid_digest"
    assert canonical_bytes({"é": "ü"}) == b'{"\\u00e9":"\\u00fc"}'


# the store ----------------------------------------------------------------------------------------------------------

def test_a_row_available_at_its_receipt_is_ingested_and_replayed(tmp_path: Path) -> None:
    store, ledger, _ = store_at(tmp_path, 12)
    store.ingest(FeatureRow("E", "f", 1, day(10), day(12), "v1"))
    assert len(replay_state(ledger.records()).rows) == 1


def test_replay_reads_past_records_of_other_registries(tmp_path: Path) -> None:
    store, ledger, _ = store_at(tmp_path, 12)
    ledger.append("event_spec", "other", {"x": 1})
    store.ingest(FeatureRow("E", "f", 1, day(10), day(12), "v1"))
    assert store.reader(day(12)).row("E", "f", "v1").value == 1
    ledger.append("pit_row", "pit:forged", FeatureRow("E", "f", 2, day(10), day(12), "v2").to_payload())
    # available at its receipt, so that its identifier alone refuses it (issue #37, pass 7)
    assert refused(replay_state, ledger.records()) == "invalid_record_id"


def test_replay_refuses_by_name(tmp_path: Path) -> None:
    _, ledger, _ = store_at(tmp_path, 12)
    late = FeatureRow("E", "f", 1, day(10), day(13), "v1")  # available after its receipt at 12
    ledger.append("pit_row", _row_id(late), late.to_payload())
    assert refused(replay_state, ledger.records()) == "evidence_after_receipt"


def test_replay_refuses_a_second_record_of_a_vintage_by_name() -> None:
    first, second = FeatureRow("E", "f", 1, day(10), day(11), "v1"), FeatureRow("E", "f", 2, day(10), day(11), "v1")
    receipt = "2026-01-12T00:00:00.000000Z"
    records = tuple(Record(seq, _row_id(row), "pit_row", receipt, row.to_payload(), "0" * 64, "0" * 64)
                    for seq, row in ((1, first), (2, second)))  # replay reads payloads; the chain is the ledger's
    assert refused(replay_state, records) == "vintage_immutable"


def test_the_latest_vintage_wins_whatever_the_ingest_order(tmp_path: Path) -> None:
    store, ledger, clock = store_at(tmp_path, 30)
    store.ingest(FeatureRow("E", "f", 2.0, day(10), day(20), "v2"))  # the later vintage first
    store.ingest(FeatureRow("E", "f", 1.0, day(10), day(15), "v1"))
    series = store.reader(day(30)).series("E", "f")
    assert (series.entity, series.feature, series.as_of) == ("E", "f", day(30))
    assert dict(series.observations) == {day(10): series.observations[day(10)]}
    assert series.observations[day(10)].vintage_id == "v2"


def test_a_read_at_the_cutoff_and_a_row_available_at_it_are_admitted(tmp_path: Path) -> None:
    store, _, _ = store_at(tmp_path, 30)
    store.ingest(FeatureRow("E", "f", 1, day(10), day(20), "v1"))
    reader = store.reader(day(20))
    assert reader.series("E", "f", as_of=day(20)).observations[day(10)].vintage_id == "v1"
    assert reader.row("E", "f", "v1").vintage_id == "v1"


# the leak detector --------------------------------------------------------------------------------------------------

def test_the_leak_detector_at_its_bounds() -> None:
    assert brier([0.25, 0.75], [0, 1]) == pytest.approx(0.0625)
    one = detect_leak([0.9, 0.1], [1, 0], bound=0, permutations=1, seed=1)  # a zero bound and one permutation are valid
    assert len(one.null_briers) == 1 and one.bound == 0
    tie = detect_leak([0.5, 0.5], [1, 0], bound=0.0, permutations=5, seed=1)
    assert tie.inflation == 0.0 and not tie.flagged  # an inflation equal to the bound is not a flag
