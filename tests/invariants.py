"""Generic invariants of the ledger and every module on it (issue #37, pass 8).

Passes 4 to 7 found their P1s in three classes, each member a new instance of an old defect:
- class W: replay trusting a persisted row, or missing a prerequisite between rows;
- class C: a clock bound lost across restart, reopen or restore;
- class P: an input decided on the caller's object rather than as the ledger persists it.

This module states the invariants that cover each class once, for every scenario the suite builds rather than for the
scenario a finding named. ``tests/conftest.py`` applies the first two to every test; ``tests/test_invariants.py``
holds the other two and the tests of the machinery itself.

1. Write-replay equivalence (classes W and C). Every value a write returns is the value a replay of the ledger gives
   right after it, and at the end of every test the writer's in-memory state and clock marks equal a replay of its
   records and a reopen of its file.
2. Write-restore equivalence (class C). At the end of every test, the canonical export restored into an empty ledger
   gives the same records, anchors, receipt, anchor and observed-wall marks, and the same replayed state of every
   module, or the same refusal.
3. Raw-row refusal (class W): ``test_invariants``.
4. Persisted-input equivalence (class P): ``test_invariants``.

What the first two cannot see: a defect every replay shares (they compare replays with replays and with the writer),
a clock bound the export does not carry (the times of anchor attempts never confirmed, reading P5-R2), and a test
that ends before the defect's write.
"""
from __future__ import annotations

import itertools
import sqlite3
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cpe.adjudication import AdjudicationRegistry
from cpe.adjudication import registry as adjudication_module
from cpe.capability import CapabilityGate, GateRules, replay_gate
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger, Record, replay
from cpe.ledger.kinds import GATE_KINDS
from cpe.ledger.store import records_from_jsonl
from cpe.pointintime import PointInTimeStore
from cpe.pointintime import store as point_in_time_module
from cpe.registration import RegistrationRegistry
from cpe.registration import registry as registration_module

_SERIAL = itertools.count()
Outcome = tuple[str, object]  # ("state", value) or ("refused", reason)


def outcome(compute: Callable[[], object]) -> Outcome:
    try:
        return "state", compute()
    except Refusal as refusal:
        return "refused", refusal.reason


def _registration(records: tuple[Record, ...], anchors: tuple[Any, ...]) -> object:
    state = registration_module.replay_state(records)
    state.local_anchors = anchors
    registration_module.check_anchor_times(state)
    # the pending attempts are ledger-local and not in the export (reading P5-R2); the local anchors are compared
    # on their own
    return {f.name: getattr(state, f.name) for f in fields(state) if f.name not in ("local_anchors", "pending_anchors")}


def module_views(records: tuple[Record, ...], anchors: tuple[Any, ...],
                 gate_rules: tuple[GateRules, ...]) -> dict[str, Outcome]:
    """What every module replays from ``records`` and the local ``anchors``: its state, or the reason it refuses."""
    prefix = max((a.prefix_length for a in anchors), default=0)
    views = {
        "ledger": outcome(lambda: replay(records).to_payload()),
        "registration": outcome(lambda: _registration(records, anchors)),
        "adjudication": outcome(lambda: adjudication_module.replay_state(records)),
        "point_in_time": outcome(lambda: point_in_time_module.replay_state(records)),
    }
    for index, rules in enumerate(gate_rules):
        views[f"gate {index}"] = outcome(lambda rules=rules: replay_gate(records, prefix, rules, anchors))  # type: ignore[misc]
    return views


def _differences(left: object, right: object, path: str = "") -> Iterator[str]:
    """Field by field, so that a failure names the field that differs."""
    if is_dataclass(left) and is_dataclass(right) and type(left) is type(right):
        for f in fields(left):
            yield from _differences(getattr(left, f.name), getattr(right, f.name), f"{path}.{f.name}")
    elif isinstance(left, dict) and isinstance(right, dict) and left.keys() == right.keys():
        for key in left:
            yield from _differences(left[key], right[key], f"{path}[{key!r}]")
    elif left != right:
        yield f"{path or 'value'}: {left!r} != {right!r}"


def differences(left: object, right: object) -> list[str]:
    return list(_differences(left, right))[:5]


@dataclass
class Tracked:
    """The ledgers and gates a test opened, kept for the checks at its end."""

    ledgers: list[tuple[Ledger, str]] = field(default_factory=list)
    gates: list[CapabilityGate] = field(default_factory=list)

    def rules_on(self, ledger: Ledger) -> tuple[GateRules, ...]:
        return tuple(dict.fromkeys(gate._rules for gate in self.gates if getattr(gate, "_ledger", None) is ledger and hasattr(gate, "_rules")))


def _marks(ledger: Ledger) -> dict[str, str]:
    return {"receipt": ledger._state.high_water, "anchor": ledger._anchor_high_water,
            "observed": ledger._observed_high_water}


def _floor(ledger: Ledger, local_attempts: bool = True) -> str:
    """The time below which the ledger refuses its clock: the greatest of its marks. Without ``local_attempts``, the
    anchor mark counts published anchors only: the times of attempts never confirmed are not in the export (P5-R2)."""
    anchor = ledger._anchor_high_water if local_attempts else max(
        (a.published_at for a in ledger.local_anchors()), default="")
    return max(ledger._state.high_water, anchor, ledger._observed_high_water)


def check_ledger(ledger: Ledger, path: str, rules: tuple[GateRules, ...], scratch: Path) -> list[str]:
    """Invariants 1 and 2 on one ledger at the end of a test; the problems found, empty when both hold."""
    try:
        records = ledger.records()
        anchors = ledger.local_anchors()
    except sqlite3.ProgrammingError:  # closed by the test; its reopen is a ledger of its own
        return []
    try:
        replay(records)
    except Refusal:
        return []  # a history the test tampered with on disk; the chain checks (T-06, T-07) are its own
    problems: list[str] = []
    original = module_views(records, anchors, rules)
    # Whether every module reads the ledger; unknown when it holds gate rows and the test opened no gate on it.
    readable = all(view[0] == "state" for view in original.values()) and (
        bool(rules) or not any(record.kind in GATE_KINDS for record in records))

    # Invariant 1: the writer's memory against its records and its own disk.
    if ledger._state.to_payload() != replay(records).to_payload():
        problems.append(f"write-replay: in-memory ledger state {ledger._state.to_payload()} != replay")
    on_disk = {"anchor": ledger._load_anchor_high_water(), "observed": ledger._load_observed_high_water()}
    for name, value in on_disk.items():
        if _marks(ledger)[name] != value:
            problems.append(f"write-replay: in-memory {name} mark {_marks(ledger)[name]} != disk {value}")
    if path != ":memory:" and Path(path).exists():
        reopened = Ledger(path, ManualClock(datetime(2000, 1, 1, tzinfo=timezone.utc)))
        try:
            if _marks(reopened) != _marks(ledger):
                problems.append(f"write-reopen: marks {_marks(reopened)} != {_marks(ledger)}")
            if reopened.records() != records or reopened.local_anchors() != anchors:
                problems.append("write-reopen: records or anchors differ")
        finally:
            reopened.close()

    # Invariant 2: the canonical export, restored.
    exported = records_from_jsonl(ledger.export_jsonl())
    if exported != records:
        problems.append("write-restore: the export does not read back as the records")
    try:
        restored, _ = Ledger.restore(scratch / f"restored-{next(_SERIAL)}.sqlite",
                                     ManualClock(datetime(2000, 1, 1, tzinfo=timezone.utc)), exported,
                                     HarnessAnchorStore(anchors))
    except Refusal as refusal:
        if readable:
            problems.append(f"write-restore: restore refused ({refusal.reason}) a ledger every module reads")
        return problems
    try:
        # Compared when every module reads the ledger: a gate row appended raw, which replay refuses, may carry a
        # reading the writer never kept as a bound.
        if readable and _floor(restored) != _floor(ledger, local_attempts=False):
            problems.append(f"write-restore: the clock floor {_floor(restored)} != {_floor(ledger, False)} "
                            f"(marks {_marks(restored)}, written {_marks(ledger)})")
        if restored.local_anchors() != anchors:
            problems.append("write-restore: anchors differ")
        again = module_views(restored.records(), restored.local_anchors(), rules)
        for name, view in original.items():
            if view != again[name]:
                problems.append(f"write-restore: {name}: " + "; ".join(differences(view, again[name])))
    finally:
        restored.close()
    return problems


# Invariant 1 on the value a write returns: compared with a replay right after it ---------------------------------

def _alone() -> bool:
    """A concurrent writer may extend the ledger between a write and the replay after it; such tests are skipped."""
    return threading.active_count() == 1


def _after_adjudicate(registry: AdjudicationRegistry, result: Any, event_id: str) -> list[str]:
    stored = adjudication_module.replay_state(registry._ledger.records()).event(str(event_id)).disposition
    if result.final and stored != result:
        return [f"write-replay: adjudicate({event_id!r}) returned " + "; ".join(differences(result, stored))]
    if not result.final and stored is not None:
        return [f"write-replay: adjudicate({event_id!r}) returned an undecided member over a stored disposition"]
    return []


def _after_beacon(registry: RegistrationRegistry, result: Any, output: Any) -> list[str]:
    record, seed = result
    held = registry._state().seeds.get(record.payload["output"]["calibration_record_id"])
    return [] if held == seed else [f"write-replay: supply_beacon_output returned seed {seed}, the ledger holds {held}"]


def _after_promote(gate: CapabilityGate, result: Any, *_: object) -> list[str]:
    state = gate.state()
    problems = []
    if result.level != state.level:
        problems.append(f"write-replay: promote returned level {result.level}, replay gives {state.level}")
    if result.intent_id not in state.effective:
        problems.append(f"write-replay: promote acknowledged {result.intent_id}, which replay does not hold effective")
    return problems


def _after_record(owner: Any, result: Any, *_: object) -> list[str]:
    """An acknowledged write is durable: the record returned is the ledger's, byte for byte."""
    records = owner._ledger.records()
    record = result[0] if isinstance(result, tuple) else result
    if isinstance(record, Record) and record not in records:
        return [f"write-replay: {record.record_id} was acknowledged and is not in the ledger as returned"]
    return []


AFTER: dict[tuple[type, str], Callable[..., list[str]]] = {
    (AdjudicationRegistry, "adjudicate"): _after_adjudicate,
    (RegistrationRegistry, "supply_beacon_output"): _after_beacon,
    (CapabilityGate, "promote"): _after_promote,
    **{(RegistrationRegistry, name): _after_record for name in (
        "register_arm_version", "correct_cutoff", "log_candidate", "commit_base_rate", "register_cluster",
        "request_void", "submit_forecast", "register_claim", "anchor_confirmatory_register", "record_calibration")},
    **{(AdjudicationRegistry, name): _after_record for name in (
        "archive_content", "submit_record", "submit_observation", "declare_source_status")},
    (PointInTimeStore, "ingest"): _after_record,
    (CapabilityGate, "perform"): _after_record,
}


def checked(owner: type, name: str, method: Callable[..., Any], problems: list[str]) -> Callable[..., Any]:
    after = AFTER[(owner, name)]

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        result = method(self, *args, **kwargs)
        if _alone() and getattr(self, "_invariants_quiet", 0) == 0:
            self._invariants_quiet = 1  # the check's own reads are not checked again
            try:
                problems.extend(after(self, result, *args))
            except Refusal as refusal:  # a ledger that refuses its own replay right after a write
                problems.append(f"write-replay: {owner.__name__}.{name} left a ledger that refuses replay "
                                f"({refusal.reason}: {refusal.detail})")
            finally:
                self._invariants_quiet = 0
        return result

    return wrapper
