"""Shared fixtures: a manual clock and ledger factories. Every test is offline and synthetic."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.ledger import FaultInjector, HarnessAnchorStore, Ledger

START = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def clock() -> ManualClock:
    return ManualClock(START)


@pytest.fixture
def anchor_store() -> HarnessAnchorStore:
    return HarnessAnchorStore()


@pytest.fixture
def faults() -> FaultInjector:
    return FaultInjector()


@pytest.fixture
def ledger(tmp_path: Path, clock: ManualClock, anchor_store: HarnessAnchorStore, faults: FaultInjector) -> Ledger:
    return Ledger(tmp_path / "ledger.sqlite", clock, anchor_store, faults)
