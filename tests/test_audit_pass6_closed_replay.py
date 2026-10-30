"""Whole-codebase audit, pass 6 (issue #37): replay is closed (reading P6-R1).

Passes 4 to 6 found, one row kind at a time, rows that replay read as authority without the rule the write path applies
(class W; X1, X2; Y1, E1). The structural reading: every module re-validates every row of its own kinds by its write
rule, skips another module's kinds, and refuses the ledger on a kind no module writes. The kinds are named once, in
``cpe.ledger.kinds``.

- Every kind constant of a module is in its table, and the tables are disjoint.
- A row of each kind a module writes, under an identifier of the writer's choosing and with an empty payload, refuses
  that module's replay with a typed reason: no kind is skipped or read without a rule, and none raises an untyped
  error (the raw beacon rows raised ``KeyError`` before).
- A row of a kind no module writes refuses every module's replay (``unknown_kind``).
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

import cpe.adjudication.registry as adjudication
import cpe.capability.records as gate_records
import cpe.pointintime.store as point_in_time
import cpe.registration.registry as registration
from cpe.capability.state import replay_gate
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger, Record
from cpe.ledger.kinds import ADJUDICATION_KINDS, GATE_KINDS, LEDGER_KINDS, POINT_IN_TIME_KINDS, REGISTRATION_KINDS
from tests.test_capability import RULES
from tests.test_registration import day

REPLAYS: dict[str, tuple[frozenset[str], ModuleType, Callable[[tuple[Record, ...]], object]]] = {
    "registration": (REGISTRATION_KINDS, registration, registration.replay_state),
    "adjudication": (ADJUDICATION_KINDS, adjudication, adjudication.replay_state),
    "gate": (GATE_KINDS, gate_records, lambda records: replay_gate(records, 0, RULES, ())),
    "point-in-time": (POINT_IN_TIME_KINDS, point_in_time, point_in_time.replay_state),
}


def _ledger(tmp_path: Path) -> Ledger:
    return Ledger(tmp_path / "l.sqlite", ManualClock(day(1)), HarnessAnchorStore())


@pytest.mark.parametrize("module", sorted(REPLAYS))
def test_every_kind_a_module_names_is_in_its_table(module: str) -> None:
    own, namespace, _ = REPLAYS[module]
    constants = {value for name, value in vars(namespace).items() if name.startswith("KIND_")}
    assert constants == own


def test_the_tables_are_disjoint_and_make_the_ledger_kinds() -> None:
    tables = [own for own, _, _ in REPLAYS.values()]
    assert sum(len(t) for t in tables) == len(LEDGER_KINDS) == len(frozenset().union(*tables))


@pytest.mark.parametrize("module, kind", sorted((m, k) for m, (own, _, _) in REPLAYS.items() for k in own))
def test_no_kind_is_skipped_by_its_module(tmp_path: Path, module: str, kind: str) -> None:
    """A malformed row of every kind refuses its module's replay, typed: no kind is skipped. The row is refused by
    its schema; that each kind is admitted by its write rule is invariant 3's (``tests/test_invariants.py``; issue #37,
    pass 9: this test was named for the rules, which it never reaches)."""
    _, _, replay = REPLAYS[module]
    ledger = _ledger(tmp_path)
    ledger.append(kind, "chosen:1", {})
    with pytest.raises(Refusal):  # typed: never skipped, never a KeyError
        replay(ledger.records())


@pytest.mark.parametrize("module", sorted(REPLAYS))
def test_a_kind_no_module_writes_refuses_every_replay(tmp_path: Path, module: str) -> None:
    _, _, replay = REPLAYS[module]
    ledger = _ledger(tmp_path)
    ledger.append("note", "n-1", {"x": 1})
    with pytest.raises(Refusal) as refused:
        replay(ledger.records())
    assert refused.value.reason == "unknown_kind"


@pytest.mark.parametrize("module", sorted(REPLAYS))
def test_another_modules_kind_is_skipped(tmp_path: Path, module: str) -> None:
    own, _, replay = REPLAYS[module]
    other = sorted(LEDGER_KINDS - own)[0]
    ledger = _ledger(tmp_path)
    ledger.append(other, "other:1", "any payload")
    replay(ledger.records())
