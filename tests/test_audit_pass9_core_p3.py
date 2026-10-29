"""Whole-codebase audit, pass 9 (issue #37), at ``811ba9d6bd13996cec72da62c0179d1baf71c6f2``: typed refusals of the
ledger and the clock (P3, found by the line-by-line reviewers of pass 9). Each test fails at the pin.

- P9-4: ``Ledger.restore`` without an external store raised ``AttributeError``; its docstring says it refuses to run.
- P9-5: ``ManualClock`` accepted a start whose ``tzinfo`` gives no offset and read it as host local time, while ``set``
  refuses the same value as ``naive_timestamp``."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger

START = datetime(2026, 1, 1, tzinfo=timezone.utc)


class NoOffset(tzinfo):
    def utcoffset(self, moment: datetime | None) -> timedelta | None:
        return None

    def dst(self, moment: datetime | None) -> timedelta | None:
        return None

    def tzname(self, moment: datetime | None) -> str | None:
        return None


def test_p9_4_a_restore_without_an_external_store_is_a_typed_refusal(tmp_path: Path) -> None:
    clock = ManualClock(START)
    source = Ledger(tmp_path / "source.sqlite", clock, HarnessAnchorStore())
    clock.advance(timedelta(seconds=1))
    source.append("candidate", "n-1", {})
    with pytest.raises(Refusal) as refused:
        Ledger.restore(tmp_path / "restored.sqlite", clock, source.records(), None)  # type: ignore[arg-type]
    assert refused.value.reason == "no_anchor_store"
    assert not (tmp_path / "restored.sqlite").exists()  # refused before any file is written


def test_p9_5_a_manual_clock_start_without_an_offset_is_naive() -> None:
    with pytest.raises(Refusal) as refused:
        ManualClock(datetime(2026, 1, 1, tzinfo=NoOffset()))
    assert refused.value.reason == "naive_timestamp"
    clock = ManualClock(START)
    with pytest.raises(Refusal) as by_set:
        clock.set(datetime(2026, 1, 1, tzinfo=NoOffset()))
    assert by_set.value.reason == refused.value.reason
