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
5. Clock monotonicity (class C; pass 9). At the end of every test, on the ledger as written, reopened and restored:
   no persisted receipt or clock sample (a gate reading, a disposition's adjudication time) is below a bound persisted
   before it (an earlier receipt or sample, or the publication time of an anchor of a shorter prefix), no anchor is
   published below the bounds of the prefix it covers, and the ledger refuses its clock below every persisted bound.
6. Refusal symmetry (class W; pass 9). Every refusal a public write path returns, on any input of any test, about
   that input: the row the path would have written for it, appended raw at the time of the refusal, is refused by the
   module's replay. The capability gate is not wrapped: every refusal of a presentation or an action is persisted as
   its own check record, and an intent appended raw is invariant 3's.
7. Disclosure (class C; pass 9). Every public read whose result depends on an event's issuance close having passed
   (``forecasts_of``, ``forecasts_for_baseline``, ``slot_states`` with an abstention or a value, the snapshot of
   ``state`` with an event's forecasts) returns only after the ledger holds that event's disclosure row, received
   after the close, under every clock sequence the suite builds.

What the first two cannot see: a defect every replay shares (they compare replays with replays and with the writer),
a clock bound the export does not carry (the times of anchor attempts never confirmed, reading P5-R2), and a test
that ends before the defect's write. Invariant 5 sees what a ledger persists, not a clock sample a decision took and
never persisted (invariant 7 covers the reads that must persist one); invariant 6 sees the refusals the suite
provokes, and judges a time-dependent refusal at the ledger's latest clock sample, which is the decision's.

Problems that are open findings of issue #37 are listed in ``KNOWN_OPEN`` with their finding until the fix lands,
which removes the entry; ``tests/test_invariants.py`` holds a strict expected failure for each.
"""
from __future__ import annotations

import inspect
import itertools
import sqlite3
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cpe.adjudication import AdjudicationRegistry, ArchivedContent, ResolutionRecord, SourceRule
from cpe.adjudication.records import AbsenceObservation, SourceStatus
from cpe.canonical import ZERO_DIGEST
from cpe.adjudication import registry as adjudication_module
from cpe.capability import CapabilityGate, GateRules, replay_gate
from cpe.clock import ManualClock, format_timestamp, parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger, Record, replay
from cpe.ledger.kinds import GATE_KINDS, KIND_DISPOSITION, KIND_EPOCH
from cpe.ledger.store import records_from_jsonl
from cpe.pointintime import FeatureRow, PointInTimeStore
from cpe.pointintime import store as point_in_time_module
from cpe.registration import (
    BaseRate,
    BeaconOutput,
    CalibrationRecord,
    CandidateEntry,
    ClaimPreregistration,
    ClusterRegistration,
    ConfirmatoryRegister,
    CutoffCorrection,
    RegistrationRegistry,
    VoidRequest,
)
from cpe.registration import registry as registration_module
from cpe.registration.registry import KIND_BEACON, KIND_FORECAST
from cpe.registration.seeds import derive_seed
from cpe.schemas import ArmVersion, EventSpec, Forecast
from cpe.schemas.common import as_persisted, require_identifier

_SERIAL = itertools.count()

# Open findings of issue #37 that the invariants report on the existing suite, by the start of the problem text, each
# with its strict expected failure in ``tests/test_invariants.py``; the fix removes the entry.
KNOWN_OPEN: dict[str, str] = {
    **{f"clock: {where}: gate_": "pass 9 P9-2: gate replay reads a reading below a wall time persisted before it"
       for where in ("written", "reopened", "restored")},
}


def open_findings_removed(problems: list[str]) -> list[str]:
    return [p for p in problems if not any(p.startswith(prefix) for prefix in KNOWN_OPEN)]
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


# Invariant 5: clock monotonicity ---------------------------------------------------------------------------------

def _samples(record: Record) -> list[tuple[str, str]]:
    """The ledger clock samples a record persists besides its receipt, as (label, timestamp): the reading of a gate
    record (an epoch's baseline), and the adjudication time of a disposition. Each was read from the ledger clock at or
    above every bound the ledger held, and before its own append."""
    payload = record.payload
    if not isinstance(payload, dict):
        return []
    if record.kind in GATE_KINDS:
        reading = payload.get("baseline" if record.kind == KIND_EPOCH else "reading")
        wall = reading.get("wall") if isinstance(reading, dict) else None
        return [("reading", wall)] if isinstance(wall, str) else []
    adjudicated = payload.get("adjudicated_at")
    if record.kind == KIND_DISPOSITION and isinstance(adjudicated, str):
        return [("adjudicated_at", adjudicated)]
    return []


def clock_problems(records: tuple[Record, ...], anchors: tuple[Any, ...], floor: str, where: str) -> list[str]:
    """Invariant 5 on one ledger: no persisted receipt or clock sample is below a bound persisted before it, and the
    ledger refuses its clock below every persisted bound. A bound is an earlier receipt or sample, or the publication
    time of an anchor of a shorter prefix: an anchor covers the whole committed prefix when it is taken, so every
    record beyond it was appended after it. An anchor's own time is at or above every bound of the prefix it covers."""
    problems: list[str] = []
    ordered = sorted(anchors, key=lambda a: a.prefix_length)
    bound: datetime | None = None
    highest = bound
    for record in records:
        for anchor in ordered:
            if anchor.prefix_length < record.seq:
                published = parse_timestamp(anchor.published_at)
                bound = published if bound is None else max(bound, published)
        times = [("receipt", record.receipt_time), *_samples(record)]
        for label, stamp in times:
            moment = parse_timestamp(stamp)
            if bound is not None and moment < bound:
                problems.append(f"clock: {where}: {record.kind} {record.record_id} has {label} {stamp}, below the "
                                f"bound {format_timestamp(bound)} persisted before it")
        latest = max(parse_timestamp(stamp) for _, stamp in times)
        bound = latest if bound is None else max(bound, latest)
        for anchor in ordered:
            if anchor.prefix_length == record.seq and parse_timestamp(anchor.published_at) < bound:
                problems.append(f"clock: {where}: the anchor of prefix {anchor.prefix_length} is published at "
                                f"{anchor.published_at}, below {format_timestamp(bound)}")
        highest = bound
    for anchor in ordered:
        if anchor.prefix_length >= len(records):
            published = parse_timestamp(anchor.published_at)
            highest = published if highest is None else max(highest, published)
    if highest is not None and (not floor or parse_timestamp(floor) < highest):
        problems.append(f"clock: {where}: the ledger refuses its clock below {floor or 'nothing'}, under the persisted "
                        f"bound {format_timestamp(highest)}")
    return problems


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
    if readable:
        problems += clock_problems(records, anchors, _floor(ledger), "written")
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
            if readable:
                problems += clock_problems(reopened.records(), reopened.local_anchors(), _floor(reopened), "reopened")
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
        if readable:
            problems += clock_problems(restored.records(), restored.local_anchors(), _floor(restored), "restored")
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


# Invariant 7: disclosure ---------------------------------------------------------------------------------------

def _released(registry: RegistrationRegistry, event_id: str, read: str) -> list[str]:
    """A read whose result depends on the event's issuance close having passed (a forecast or a slot value released,
    an abstention reported, the event's forecasts returned at all) persisted that close as the receipt of the event's
    disclosure row, after the close (RC-109; ``17`` item 2 "Clock": a clock-dependent check is persisted before its
    verdict; reading P8-R2)."""
    spec = registry._state().events.get(event_id)
    if spec is None:
        return [f"disclosure: {read} answered for {event_id!r}, which is not registered"]
    rows = [r for r in registry._ledger.records()
            if r.kind == registration_module.KIND_DISCLOSURE and isinstance(r.payload, dict)
            and r.payload.get("event_id") == event_id]
    if not any(parse_timestamp(r.receipt_time) > spec.issuance_close for r in rows):
        return [f"disclosure: {read} returned what the close of {event_id} decides, and the ledger holds no "
                "disclosure row received after that close"]
    return []


def _after_forecasts_of(registry: RegistrationRegistry, result: Any, event_id: str) -> list[str]:
    return _released(registry, str(event_id), "forecasts_of")


def _after_slot_states(registry: RegistrationRegistry, result: Any, event_id: str) -> list[str]:
    decided = any(s.status == "abstention" or (s.status == "filled" and s.value is not None) for s in result)
    return _released(registry, str(event_id), "slot_states") if decided else []


def _after_state(registry: RegistrationRegistry, result: Any, *_: object) -> list[str]:
    released = {key[0] for key in result.forecasts} | set(result.forecasts_by_event) | {k[0] for k in result.submissions}
    return [problem for event_id in sorted(released) for problem in _released(registry, event_id, "state")]


AFTER: dict[tuple[type, str], Callable[..., list[str]]] = {
    (RegistrationRegistry, "forecasts_of"): _after_forecasts_of,
    (RegistrationRegistry, "forecasts_for_baseline"): _after_forecasts_of,
    (RegistrationRegistry, "slot_states"): _after_slot_states,
    (RegistrationRegistry, "state"): _after_state,
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
    signature = inspect.signature(method)

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        result = method(self, *args, **kwargs)
        if _alone() and getattr(self, "_invariants_quiet", 0) == 0:
            self._invariants_quiet = 1  # the check's own reads are not checked again
            try:
                # the call's arguments in the method's order, however they were passed (PR #88 review 4417450701)
                bound = signature.bind(self, *args, **kwargs)
                bound.apply_defaults()
                problems.extend(after(self, result, *list(bound.arguments.values())[1:]))
            except Refusal as refusal:  # a ledger that refuses its own replay right after a write
                problems.append(f"write-replay: {owner.__name__}.{name} left a ledger that refuses replay "
                                f"({refusal.reason}: {refusal.detail})")
            finally:
                self._invariants_quiet = 0
        return result

    return wrapper


# Invariant 6: refusal symmetry ----------------------------------------------------------------------------------

# Refusals that are no verdict on the input: contention, the clock or the anchor store at that moment, a duplicate the
# ledger itself refuses (a raw append is refused the same way), and the outcomes of a protected operation that are
# persisted as their own records.
NOT_ABOUT_THE_INPUT = frozenset({
    "stale_head", "contended", "clock_rollback", "clock_discontinuity", "duplicate_record_id", "anchor_failed",
    "anchor_store_unavailable", "anchor_pending", "commit_in_doubt", "superseded", "intent_aborted", "no_anchor_store",
})
Row = tuple[str, str, Any]


def _reg_id(prefix: str, *parts: str) -> str:
    return registration_module._ledger_id(prefix, *parts)


def _adj_id(prefix: str, *parts: str) -> str:
    return adjudication_module._ledger_id(prefix, *parts)


def _forecast_row(registry: RegistrationRegistry, forecast: Any) -> Row:
    key = (forecast.event_id, forecast.arm_id, forecast.slot_id)
    count = registry._state().submissions.get(key, 0) + 1
    return KIND_FORECAST, _reg_id("forecast", *key, str(count)), forecast.to_payload()


def _beacon_row(registry: RegistrationRegistry, output: Any) -> Row:
    calibration = registry._state().calibrations.get(output.calibration_record_id)
    seed = ZERO_DIGEST if calibration is None else derive_seed(calibration.to_payload(), output.value)
    return KIND_BEACON, _reg_id("beacon", output.calibration_record_id), {"output": output.to_payload(), "seed": seed}


def _persisted(schema: Callable[[object], Any]) -> Callable[[Any], Any]:
    return lambda value: as_persisted(value, schema)


# For every public write path: the schema its input is read back through, and the row the path writes for it.
SYMMETRY: dict[tuple[type, str], tuple[Callable[[Any], Any], Callable[[Any, Any], Row]]] = {
    (RegistrationRegistry, "register_arm_version"): (_persisted(ArmVersion.from_payload), lambda r, v: (
        registration_module.KIND_ARM_VERSION, _reg_id("arm-version", v.arm_version_id), v.to_payload())),
    (RegistrationRegistry, "correct_cutoff"): (_persisted(CutoffCorrection.from_payload), lambda r, c: (
        registration_module.KIND_CUTOFF_CORRECTION, _reg_id("cutoff-correction", c.arm_version_id, c.evidence_id),
        c.to_payload())),
    (RegistrationRegistry, "log_candidate"): (_persisted(CandidateEntry.from_payload), lambda r, e: (
        registration_module.KIND_CANDIDATE, _reg_id("candidate", e.candidate_id), e.to_payload())),
    (RegistrationRegistry, "commit_base_rate"): (_persisted(BaseRate.from_payload), lambda r, b: (
        registration_module.KIND_BASE_RATE, _reg_id("base-rate", b.reference_class_id), b.to_payload())),
    (RegistrationRegistry, "register_cluster"): (_persisted(ClusterRegistration.from_payload), lambda r, c: (
        registration_module.KIND_CLUSTER, _reg_id("cluster", c.cluster.cluster_id), c.to_payload())),
    (RegistrationRegistry, "request_void"): (_persisted(VoidRequest.from_payload), lambda r, v: (
        registration_module.KIND_VOID_REQUEST, _reg_id("void-request", v.request_id), v.to_payload())),
    (RegistrationRegistry, "submit_forecast"): (_persisted(Forecast.from_payload), _forecast_row),
    (RegistrationRegistry, "register_claim"): (_persisted(ClaimPreregistration.from_payload), lambda r, c: (
        registration_module.KIND_CLAIM, _reg_id("claim", c.claim_id), c.to_payload())),
    (RegistrationRegistry, "anchor_confirmatory_register"): (_persisted(ConfirmatoryRegister.from_payload),
                                                             lambda r, c: (registration_module.KIND_REGISTER,
                                                                           _reg_id("register"), c.to_payload())),
    (RegistrationRegistry, "record_calibration"): (_persisted(CalibrationRecord.from_payload), lambda r, c: (
        registration_module.KIND_CALIBRATION, _reg_id("calibration", c.calibration_record_id), c.to_payload())),
    (RegistrationRegistry, "supply_beacon_output"): (_persisted(BeaconOutput.from_payload), _beacon_row),
    (RegistrationRegistry, "forecasts_of"): (lambda e: require_identifier(e, "event_id"), lambda r, e: (
        registration_module.KIND_DISCLOSURE, _reg_id("disclosure", e), {"event_id": e})),
    (AdjudicationRegistry, "register_event"): (_persisted(EventSpec.from_payload), lambda r, s: (
        adjudication_module.KIND_EVENT, _adj_id("event", s.event_id), s.to_payload())),
    (AdjudicationRegistry, "register_rule"): (_persisted(SourceRule.from_payload), lambda r, s: (
        adjudication_module.KIND_RULE, _adj_id("rule", s.source_id), s.to_payload())),
    (AdjudicationRegistry, "archive_content"): (_persisted(ArchivedContent.from_payload), lambda r, c: (
        adjudication_module.KIND_CONTENT, _adj_id("content", c.sha256), c.to_payload())),
    (AdjudicationRegistry, "submit_record"): (_persisted(ResolutionRecord.from_payload), lambda r, x: (
        adjudication_module.KIND_RECORD, _adj_id("record", x.record_id), x.to_payload())),
    (AdjudicationRegistry, "submit_observation"): (_persisted(AbsenceObservation.from_payload), lambda r, o: (
        adjudication_module.KIND_OBSERVATION, _adj_id("observation", o.observation_id), o.to_payload())),
    (AdjudicationRegistry, "declare_source_status"): (_persisted(SourceStatus.from_payload), lambda r, s: (
        adjudication_module.KIND_STATUS, _adj_id("status", s.source_id, s.declared_at.isoformat()), s.to_payload())),
    (PointInTimeStore, "ingest"): (_persisted(FeatureRow.from_payload), lambda p, row: (
        point_in_time_module.KIND_ROW, point_in_time_module._row_id(row), row.to_payload())),
}


def _replay_of(owner: Any) -> Callable[[tuple[Record, ...], tuple[Any, ...]], object]:
    if isinstance(owner, RegistrationRegistry):
        return _registration
    if isinstance(owner, AdjudicationRegistry):
        return lambda records, anchors: adjudication_module.replay_state(records)
    return lambda records, anchors: point_in_time_module.replay_state(records)


def symmetry_problems(owner: Any, name: str, argument: Any, refusal: Refusal, scratch: Path) -> list[str]:
    """Invariant 6 on one refusal: the row the write path would have written for the refused input, appended to the
    ledger raw at the time of the refusal, is refused by the module's replay."""
    ledger: Ledger = owner._ledger
    stamp = getattr(ledger, "_invariants_moment", None)  # the latest clock sample of the ledger: the decision's
    if refusal.reason in NOT_ABOUT_THE_INPUT or stamp is None:
        return []
    moment = parse_timestamp(stamp)
    read, row_of = SYMMETRY[(type(owner), name)]
    try:
        value = read(argument)
        kind, record_id, payload = row_of(owner, value)
        copy, _ = Ledger.restore(scratch / f"symmetry-{next(_SERIAL)}.sqlite", ManualClock(moment), ledger.records(),
                                 HarnessAnchorStore(ledger.local_anchors()))
    except (Refusal, sqlite3.ProgrammingError):
        return []  # an input no row can carry, or a ledger the test has closed
    try:
        try:
            copy.append(kind, record_id, payload)
        except Refusal:
            return []  # the ledger itself refuses the row (a duplicate identifier, its own clock rule)
        try:
            _replay_of(owner)(copy.records(), copy.local_anchors())
        except Refusal:
            return []
        return [f"refusal symmetry: {type(owner).__name__}.{name} refused {refusal.reason} ({refusal.detail}); "
                f"the same {kind} row appended raw is read by replay"]
    finally:
        copy.close()


def symmetric(owner: type, name: str, method: Callable[..., Any], problems: list[str],
              scratch: Callable[[], Path]) -> Callable[..., Any]:
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        before = None
        try:
            before = len(self._ledger.records())
        except sqlite3.ProgrammingError:
            pass
        try:
            return method(self, *args, **kwargs)
        except Refusal as refusal:
            quiet = getattr(self, "_invariants_quiet", 0)
            grew = before is not None and len(self._ledger.records()) != before  # the refusal is a record itself
            if _alone() and quiet == 0 and not grew and (args or kwargs):
                self._invariants_quiet = 1
                try:
                    problems.extend(symmetry_problems(self, name, (args or tuple(kwargs.values()))[0], refusal,
                                                      scratch()))
                finally:
                    self._invariants_quiet = 0
            raise

    return wrapper
