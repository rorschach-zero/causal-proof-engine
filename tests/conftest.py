"""Shared fixtures: a manual clock and ledger factories. Every test is offline and synthetic."""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from cpe.capability import CapabilityGate
from cpe.clock import ManualClock
from cpe.ledger import FaultInjector, HarnessAnchorStore, Ledger
from tests import invariants

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


@pytest.fixture(autouse=True)
def generic_invariants(monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory) -> Iterator[None]:
    """Invariants 1 and 2 of ``tests/invariants.py`` on every scenario the suite builds: each value a write returns
    is checked against a replay right after it, and every ledger the test opened is checked at its end against its
    replay, its reopen and its restored export."""
    tracked = invariants.Tracked()
    problems: list[str] = []
    ledger_init, gate_init = Ledger.__init__, CapabilityGate.__init__

    def track_ledger(self: Ledger, path: str | Path, *args: Any, **kwargs: Any) -> None:
        ledger_init(self, path, *args, **kwargs)
        tracked.ledgers.append((self, str(path)))

    def track_gate(self: CapabilityGate, *args: Any, **kwargs: Any) -> None:
        tracked.gates.append(self)  # before the start, which may refuse after writing its rotation
        gate_init(self, *args, **kwargs)

    monkeypatch.setattr(Ledger, "__init__", track_ledger)
    monkeypatch.setattr(CapabilityGate, "__init__", track_gate)
    for owner, name in invariants.AFTER:
        monkeypatch.setattr(owner, name, invariants.checked(owner, name, getattr(owner, name), problems))
    yield
    scratch = tmp_path_factory.mktemp("invariants")
    for ledger, path in list(tracked.ledgers):
        if hasattr(ledger, "_conn"):
            problems.extend(invariants.check_ledger(ledger, path, tracked.rules_on(ledger), scratch))
    assert not problems, "generic invariants (tests/invariants.py):\n" + "\n".join(problems)
