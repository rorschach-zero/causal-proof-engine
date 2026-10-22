"""Whole-codebase audit, pass 4 (issue #37): finding C1 (P1). ``format_timestamp`` wrote a year below 1000 without
zero padding ("999-01-01T..."), and the ledger compared its high-water mark as text, so a clock rolled back below
year 1000 sorted above "2026-..." and was admitted: by ``append``, by ``now`` and by replay. 17 item 2 "Clock": "the
persisted wall time is a high-water mark: a check whose wall time is below it fails closed". Only an injected clock
reaches it (the host refuses a time before 1970); the gate compares instants and was unaffected. Every test here
failed on the pass-4 commit ``c3d6233dbaeb71eb71cb128394099b23cef285b5``."""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cpe.clock import ManualClock, format_timestamp, parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger, LedgerState, Record
from cpe.ledger.record import GENESIS_HASH, entry_digest
from cpe.ledger.store import records_from_jsonl

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
YEAR_999 = datetime(999, 1, 1, tzinfo=timezone.utc)


def rolled_back(tmp_path: Path) -> tuple[Ledger, ManualClock]:
    clock = ManualClock(NOW)
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    ledger.append("note", "n-1", {"x": 1})
    clock.set(YEAR_999)
    return ledger, clock


def test_c1_an_append_below_year_1000_is_a_rollback(tmp_path: Path) -> None:
    ledger, _ = rolled_back(tmp_path)
    with pytest.raises(Refusal) as refused:
        ledger.append("note", "n-2", {"x": 2})  # at c3d6233: admitted, and the export no longer restores
    assert refused.value.reason == "clock_rollback"
    assert len(records_from_jsonl(ledger.export_jsonl())) == 1


def test_c1_the_read_gate_below_year_1000_is_a_rollback(tmp_path: Path) -> None:
    ledger, _ = rolled_back(tmp_path)
    with pytest.raises(Refusal) as refused:
        ledger.now()  # at c3d6233: returned year 999
    assert refused.value.reason == "clock_rollback"


def test_c1_an_anchor_below_year_1000_is_a_rollback(tmp_path: Path) -> None:
    ledger, _ = rolled_back(tmp_path)
    with pytest.raises(Refusal) as refused:
        ledger.anchor()
    assert refused.value.reason == "clock_rollback"


def test_c1_replay_refuses_a_receipt_below_year_1000(tmp_path: Path) -> None:
    first = Record(1, "n-1", "note", format_timestamp(NOW), {"x": 1}, GENESIS_HASH,
                   entry_digest(1, "n-1", "note", format_timestamp(NOW), {"x": 1}, GENESIS_HASH))
    stamp = YEAR_999.strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # the text c3d6233 wrote: "999-01-01T00:00:00.000000Z"
    second = Record(2, "n-2", "note", stamp, {"x": 2}, first.entry_hash,
                    entry_digest(2, "n-2", "note", stamp, {"x": 2}, first.entry_hash))
    state = LedgerState()
    state.apply(first)
    with pytest.raises(Refusal):
        state.apply(second)  # at c3d6233: applied, the high-water mark moved back to year 999


def test_every_canonical_timestamp_has_four_year_digits_and_round_trips() -> None:
    for moment in (datetime(1, 1, 1, tzinfo=timezone.utc), YEAR_999, NOW,
                   datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)):
        text = format_timestamp(moment)
        assert len(text) == len("2026-01-01T00:00:00.000000Z")
        assert parse_timestamp(text) == moment
    assert format_timestamp(YEAR_999) == "0999-01-01T00:00:00.000000Z"
    with pytest.raises(Refusal):
        parse_timestamp("999-01-01T00:00:00.000000Z")  # not canonical


def test_the_order_of_canonical_timestamps_is_the_order_of_their_instants() -> None:
    rng = random.Random(37)
    base = datetime(1, 1, 1, tzinfo=timezone.utc)
    span = (datetime(9999, 12, 31, tzinfo=timezone.utc) - base).total_seconds()
    moments = [base + timedelta(seconds=rng.uniform(0, span), microseconds=rng.randrange(10**6)) for _ in range(500)]
    assert sorted(moments, key=format_timestamp) == sorted(moments)


def test_an_instant_outside_the_utc_range_is_a_typed_refusal() -> None:
    with pytest.raises(Refusal) as refused:
        format_timestamp(datetime(1, 1, 1, tzinfo=timezone(timedelta(hours=1))))
    assert refused.value.reason == "invalid_timestamp"
