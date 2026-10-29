"""Regression tests for Codex's review of PR #33 at 61a8dce (round 1), one per finding. Each fails at 61a8dce and
passes after the fix."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger, Record
from cpe.pointintime import FeatureRow, PointInTimeStore, detect_leak
from cpe.pointintime.store import KIND_ROW, replay_state
from tests.test_point_in_time import day, f25_row


def store_at(tmp_path: Path, at: float = 60) -> tuple[PointInTimeStore, Ledger]:
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(day(at)), HarnessAnchorStore())
    return PointInTimeStore(ledger), ledger


def test_4335189780_the_store_exposes_no_read_without_a_cutoff(tmp_path: Path) -> None:
    store, _ = store_at(tmp_path)
    store.ingest(f25_row(10, 50, "v6", 1.40))
    public = {name for name in dir(store) if not name.startswith("_")}
    assert public == {"ingest", "reader", "reader_for"}


def test_4335189809_a_non_integer_permutation_count_is_refused() -> None:
    for count in (200.0, "200", None):
        with pytest.raises(Refusal) as refused:
            detect_leak([0.5, 0.5], [0, 1], bound=0.05, permutations=count, seed=1)  # type: ignore[arg-type]
        assert refused.value.reason == "invalid_permutations"


def test_4335189761_replay_refuses_a_second_record_of_one_vintage(tmp_path: Path) -> None:
    store, ledger = store_at(tmp_path)
    store.ingest(f25_row(10, 12, "v1", 1.00))
    rewritten = f25_row(10, 12, "v1", 9.00).to_payload()
    ledger.append(KIND_ROW, "pit:another-id", rewritten)  # an authentic ledger row under a non-canonical id
    with pytest.raises(Refusal) as refused:
        replay_state(ledger.records())
    # The one record id of a vintage is its canonical id, so a second record of it is always under another id: the
    # identifier check is the rule that refuses it (issue #37, pass 6: the "either reason" accepted no specific one).
    assert refused.value.reason == "invalid_record_id"
    with pytest.raises(Refusal):
        store.reader(day(20)).series("E1", "f")


def test_4335189789_idempotence_compares_the_persisted_content(tmp_path: Path) -> None:
    store, _ = store_at(tmp_path)
    store.ingest(FeatureRow("E1", "flag", True, day(10), day(12), "v1"))
    with pytest.raises(Refusal) as refused:
        store.ingest(FeatureRow("E1", "flag", 1, day(10), day(12), "v1"))
    assert refused.value.reason == "vintage_immutable"
    store.ingest(FeatureRow("E1", "x", 1, day(10), day(12), "v1"))
    with pytest.raises(Refusal) as as_float:
        store.ingest(FeatureRow("E1", "x", 1.0, day(10), day(12), "v1"))
    assert as_float.value.reason == "vintage_immutable"


def test_4335189800_an_as_of_override_is_validated_and_normalised(tmp_path: Path) -> None:
    store, _ = store_at(tmp_path)
    store.ingest(f25_row(10, 12, "v1", 1.00))
    reader = store.reader(day(20))
    with pytest.raises(Refusal) as naive:
        reader.series("E1", "f", as_of=datetime(2026, 1, 15))
    assert naive.value.reason == "naive_timestamp"
    with pytest.raises(Refusal) as naive_row:
        reader.row("E1", "f", "v1", as_of=datetime(2026, 1, 15))
    assert naive_row.value.reason == "naive_timestamp"


def test_4335189771_two_stores_on_one_ledger_ingest_one_vintage_idempotently(tmp_path: Path) -> None:
    first, ledger = store_at(tmp_path)
    second = PointInTimeStore(ledger)
    append = ledger.append

    def competitor_lands_first(row: FeatureRow) -> None:
        def append_after_competitor(*args: object, **kwargs: object) -> Record:
            ledger.append = append  # type: ignore[method-assign]
            first.ingest(row)  # the other writer lands between this one's decision and its append
            return append(*args, **kwargs)  # type: ignore[arg-type]
        ledger.append = append_after_competitor  # type: ignore[method-assign]

    competitor_lands_first(f25_row(10, 12, "v1", 1.00))
    written = second.ingest(f25_row(10, 12, "v1", 1.00))
    assert written.kind == KIND_ROW and [r.kind for r in ledger.records()] == [KIND_ROW]
    competitor_lands_first(f25_row(10, 20, "v2", 1.50))
    with pytest.raises(Refusal) as conflict:
        second.ingest(f25_row(10, 20, "v2", 9.99))
    assert conflict.value.reason == "vintage_immutable"
