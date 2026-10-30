"""Generic invariants (issue #37, pass 8; ``tests/invariants.py`` states all four and what each cannot see).

Invariants 1 (write-replay) and 2 (write-restore) run on every test of the suite, through ``tests/conftest.py``; the
tests here only show that the machinery fails on the defects it is for.

Invariant 3, raw-row refusal (class W). For every module and every row of a reference ledger that holds every kind
the module writes: the module's replay of a prefix followed by a row accepts the row exactly when the module's write
path, run on that prefix at that row's receipt, writes that same row. The row is each original row and every
perturbation of one field of its payload, placed at its own position and at every earlier one, so that a row missing
a prerequisite between rows is tried too. A row the path refuses and replay reads is class W; a row the path writes
and replay refuses leaves a ledger no later read accepts. The gate's write paths decide on a time source and on the
anchor store, so its rows are checked against the fields the gate cannot choose instead (``GATE_FREE``).

Invariant 4, persisted-input equivalence (class P). For every public entry point, an argument that is a ``str`` whose
text is one value and which compares equal to, and hashes as, another decides exactly as its plain text: the same
result or refusal, and the same ledger bytes. ``test_every_public_entry_point_is_covered`` keeps the list complete.

Not covered: a defect shared by the write path and its replay (invariant 3 compares the two); perturbations that
change more than one field at a time; a write path whose outcome depends on more than the prefix and the receipt (the
gate's time source and anchor store, the pending anchor attempts of the registration registry, which are ledger-local);
numeric look-alikes (an ``int`` or ``float`` subclass), which every write path reads back through the canonical form
but no read interface takes.
"""
from __future__ import annotations

import copy
import itertools
import inspect
from collections.abc import Callable, Iterator
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from cpe.adjudication import AdjudicationRegistry, ArchivedContent, ResolutionRecord, SourceRule
from cpe.adjudication import registry as adjudication_module
from cpe.adjudication.records import AbsenceObservation, SourceStatus
from cpe.canonical import JsonValue
from cpe.capability import CapabilityGate, replay_gate
from cpe.capability import ManualTimeSource
from cpe.capability.records import CommitRecord, gate_ledger_id
from cpe.capability import gate as gate_module
from cpe.clock import ManualClock, format_timestamp, parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger, Record, replay
from cpe.ledger import kinds as K
from cpe.ledger import store as store_module
from cpe.ledger.record import GENESIS_HASH, entry_digest
from cpe.pointintime import AsOfReader, FeatureRow, PointInTimeStore
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
from cpe.schemas import ArmVersion, EventSpec, Forecast
from cpe.validation import check_issuance
from tests.test_adjudication import day as aday
from tests.test_adjudication import observation, record, rule, spec as aspec, submit
from tests.test_audit_pass7_plain_inputs import LooksLike
from tests import invariants
from tests.test_audit_pass6_observed_wall import RollbackAfterNextRead
from tests.test_capability import ENV, EVIDENCE, OWNER, RELEASE, RULES, TOLERANCE, Rig, issue
from tests.test_input_validation import VERSIONS, jev, output
from tests.test_registration import arm, day, forecast, registration, spec

# The reference ledgers -------------------------------------------------------------------------------------------


def registration_ledger(path: Path) -> tuple[Ledger, HarnessAnchorStore]:
    """Every registration kind: arm versions (one consuming another), a correction before and one after the first
    registration, candidates, a cluster, a VOID request, the base rate, forecasts inside and outside the window, two
    claims with their calibration records, the register, a seeded round, a round refused for the register, and the
    release of an event's forecasts by the first read after its close."""
    clock, store = ManualClock(day(1)), HarnessAnchorStore()
    ledger = Ledger(path, clock, store)
    r = RegistrationRegistry(ledger)
    r.register_arm_version(arm("A-1", "2026-01-05"))
    r.register_arm_version(arm("DESIGN_C-1", "2026-01-01"))
    r.register_arm_version(arm("FULL-1", "2026-01-03", ["A-1"]))
    r.register_arm_version(arm("B-1", "2026-01-04"))
    r.correct_cutoff(CutoffCorrection("B-1", date_of("2026-01-02"), "ev-b"))  # before any registration under it
    r.commit_base_rate(BaseRate("RC-1", 0.2))
    for event_id in ("E-1", "E-2"):
        r.log_candidate(CandidateEntry(f"cand-{event_id}", event_id, "src", day(1), "registered", "predicate match"))
    r.log_candidate(CandidateEntry("cand-E-9", "E-9", "src", day(1), "rejected", "out of scope"))
    clock.set(day(10))
    r.register_cluster(registration([spec("E-1"), spec("E-2")]))
    r.request_void(VoidRequest("vr-1", "E-1", "please"))
    r.correct_cutoff(CutoffCorrection("A-1", date_of("2026-01-06"), "ev-a"))  # after: A-1 and FULL-1 withdrawn
    for n, claim_id in enumerate(("claim-1", "claim-2"), start=1):
        r.register_claim(ClaimPreregistration(claim_id, "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                              "period-balanced", ("DESIGN_C",), ("L-1",), f"cal-{n}"))
        r.record_calibration(CalibrationRecord(f"cal-{n}", claim_id, "block-t", 1000, 0.01, "beacon", f"round-{n}"))
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(11.5))
    r.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 2, ("claim-1", "claim-2")))
    clock.set(day(12))
    ledger.anchor()
    clock.set(day(13))
    r.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-1", "ab" * 32, day(12.5)))
    with pytest.raises(Refusal):
        r.supply_beacon_output(BeaconOutput("cal-2", "beacon", "round-2", "cd" * 32, day(11.7)))  # recorded refused
    clock.set(day(21))
    r.submit_forecast(forecast("E-1"))
    r.submit_forecast(forecast("E-2", "A", "A-1", 0.6))
    clock.set(day(45))
    r.submit_forecast(forecast("E-2"))  # after the close: kept, fills nothing
    r.forecasts_of("E-1")  # the first read after the close releases E-1's forecasts: a disclosure row (P8-R2)
    return ledger, store


def date_of(text: str) -> Any:
    from datetime import date
    return date.fromisoformat(text)


def adjudication_ledger(path: Path) -> tuple[Ledger, HarnessAnchorStore]:
    """Every adjudication kind: two rules, three events, archived content, timely and late records, an observation,
    a status, dispositions, a source-latency defect, a knowable-time correction and a receipt-lag incident."""
    clock, store = ManualClock(aday(3)), HarnessAnchorStore()
    ledger = Ledger(path, clock, store)
    r = AdjudicationRegistry(ledger)
    r.register_rule(rule())
    r.register_rule(SourceRule("src-2", occurrence_is_public_act=False, publishes_evidenced_times=True,
                               monotone_publication=False))
    r.register_event(aspec())
    r.register_event(aspec(event_id="F"))
    r.register_event(aspec(event_id="G"))
    r.register_event(aspec(event_id="H"))  # left undecided
    clock.set(aday(100))
    submit(r, record("r-1", occurrence=90, published=100, observed=100, event_id="F"))
    r.adjudicate("F")  # RESOLVED_YES, knowable 100
    clock.set(aday(105))
    submit(r, record("r-2", occurrence=80, published=85, observed=105, event_id="F"))
    r.adjudicate("F")  # a knowable-time correction to 85
    r.declare_source_status(SourceStatus("src", False, aday(104)))
    clock.set(aday(111))
    r.submit_observation(observation(110))
    r.adjudicate("E")  # RESOLVED_NO by absence
    clock.set(aday(113))
    submit(r, record("late", occurrence=95, published=112, observed=113))
    submit(r, record("lagged", occurrence=96, published=108, observed=113))
    r.adjudicate("E")  # a defect of the late report and a receipt lag of the timely record received late
    r.submit_observation(observation(111, event_id="G"))
    r.adjudicate("G")
    return ledger, store


def point_in_time_ledger(path: Path) -> tuple[Ledger, HarnessAnchorStore]:
    clock, store = ManualClock(datetime(2026, 1, 10, tzinfo=timezone.utc)), HarnessAnchorStore()
    ledger = Ledger(path, clock, store)
    s = PointInTimeStore(ledger)
    def at(n: int) -> datetime:
        return datetime(2026, 1, n, tzinfo=timezone.utc)

    for entity, vintage, observed, available, value in (("X", "v1", 1, 2, 1.0), ("X", "v2", 1, 5, 1.5),
                                                        ("Y", "v1", 3, 4, True)):
        s.ingest(FeatureRow(entity, "f", value, at(observed), at(available), vintage))
    return ledger, store


# The machinery of invariant 3 ------------------------------------------------------------------------------------


def chain(rows: list[tuple[str, str, str, JsonValue]]) -> tuple[Record, ...]:
    """Rows (kind, record id, receipt, payload) as a consistent hash chain."""
    records: list[Record] = []
    head = GENESIS_HASH
    for seq, (kind, record_id, receipt, payload) in enumerate(rows, start=1):
        record = Record(seq, record_id, kind, receipt, payload, head,
                        entry_digest(seq, record_id, kind, receipt, payload, head))
        records.append(record)
        head = record.entry_hash
    return tuple(records)


def rows_of(records: tuple[Record, ...]) -> list[tuple[str, str, str, JsonValue]]:
    return [(r.kind, r.record_id, r.receipt_time, r.payload) for r in records]


def leaves(value: JsonValue, path: tuple[Any, ...] = ()) -> Iterator[tuple[tuple[Any, ...], JsonValue]]:
    if isinstance(value, dict):
        for key in sorted(value):
            yield from leaves(value[key], path + (key,))
    elif isinstance(value, list) and value:
        for index, item in enumerate(value):
            yield from leaves(item, path + (index,))
    else:
        yield path, value


def with_leaf(payload: JsonValue, path: tuple[Any, ...], value: JsonValue) -> JsonValue:
    changed = copy.deepcopy(payload)
    target: Any = changed
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return changed


def alternatives(value: JsonValue, strings: list[str]) -> list[JsonValue]:
    """The values one field is perturbed to: other times, flipped flags, other numbers, other identifiers."""
    if isinstance(value, bool):
        return [not value]
    if isinstance(value, int):
        return [value + 1, *([value - 1] if value > 0 else [])]
    if isinstance(value, float):
        return [v for v in (0.0, 0.5, 1.0, value / 2) if v != value]
    if isinstance(value, str):
        try:
            moment = parse_timestamp(value)
        except Refusal:
            return [*[s for s in strings if s != value][:6], "other"]
        return [format_timestamp(moment + delta) for delta in (timedelta(days=-30), timedelta(days=-1),
                                                               timedelta(microseconds=1), timedelta(days=1),
                                                               timedelta(days=30))]
    return []


def shifted(payload: JsonValue, paths: tuple[tuple[Any, ...], ...], to: str) -> JsonValue:
    """``payload`` with the leaves at ``paths``, which hold one time, set to ``to``: a time written in several fields (a
    disposition's ``adjudicated_at`` and its timestamps' ``adjudication``) moved together (issue #37, pass 9 P9-11)."""
    changed = copy.deepcopy(payload)
    for path in paths:
        changed = with_leaf(changed, path, to)
    return changed


def candidates(records: tuple[Record, ...], own: frozenset[str]) -> Iterator[tuple[int, Record, str]]:
    """For every row of the module: the row itself; every one-field perturbation; every payload time set to the
    row's own receipt; every time written in several fields moved together; and the receipt itself moved, the payload
    unchanged (pass 9 P9-11: a payload time was never set equal to the receipt, and two fields never moved
    together). As (index, row, label)."""
    strings = sorted({v for r in records for _, v in leaves(r.payload) if isinstance(v, str)
                      and not v.endswith("Z") and len(v) < 40})
    for index, original in enumerate(records):
        if original.kind not in own:
            continue
        yield index, original, "as written"
        times: dict[str, list[tuple[Any, ...]]] = {}
        for path, value in leaves(original.payload):
            for other in alternatives(value, strings):
                yield index, replace(original, payload=with_leaf(original.payload, path, other)), f"{path}={other!r}"
            if isinstance(value, str) and value.endswith("Z") and path:
                times.setdefault(value, []).append(path)
                if value != original.receipt_time:
                    yield (index, replace(original, payload=with_leaf(original.payload, path, original.receipt_time)),
                           f"{path}=the receipt")
        for stamp, paths in times.items():
            moment = parse_timestamp(stamp)
            for size in range(2, len(paths) + 1):
                for together in itertools.combinations(paths, size):
                    for delta in (timedelta(days=-1), timedelta(microseconds=1), timedelta(days=1)):
                        to = format_timestamp(moment + delta)
                        yield (index, replace(original, payload=shifted(original.payload, together, to)),
                               f"every {together}={to}")
        receipt = parse_timestamp(original.receipt_time)
        for delta in (timedelta(microseconds=-1), timedelta(microseconds=1), timedelta(days=1)):
            yield index, replace(original, receipt_time=format_timestamp(receipt + delta)), f"receipt {delta}"
        # the receipt at every later time an earlier row names (a period start, a close, an issuance open), and just
        # before it: a bound between rows is tried at its edge (pass 9 P9-11)
        named = sorted({v for r in records[:index] for _, v in leaves(r.payload)
                        if isinstance(v, str) and v.endswith("Z") and v > original.receipt_time})
        for stamp in named:
            moment = parse_timestamp(stamp)
            for at in (moment - timedelta(microseconds=1), moment):
                yield index, replace(original, receipt_time=format_timestamp(at)), f"receipt {format_timestamp(at)}"


def placements(index: int, label: str) -> list[int]:
    """A perturbed row at its own position; the row as written at its own position and at every earlier one, so that
    a row placed before a prerequisite is tried."""
    return list(range(0, index + 1)) if label == "as written" else [index]


Replay = Callable[[tuple[Record, ...], tuple[Anchor, ...]], object]
Write = Callable[[Ledger, Record], None]


def anchors_at(anchors: tuple[Anchor, ...], length: int, receipt: str) -> tuple[Anchor, ...]:
    """The anchors a write at ``receipt`` after ``length`` records could have seen."""
    moment = parse_timestamp(receipt)
    return tuple(a for a in anchors if a.prefix_length <= length and parse_timestamp(a.published_at) <= moment)


def replay_accepts(replay_module: Replay, prefix: tuple[Record, ...], row: Record, anchors: tuple[Anchor, ...]) -> bool:
    records = chain(rows_of(prefix) + [(row.kind, row.record_id, row.receipt_time, row.payload)])
    try:
        replay(records)  # the ledger's own rules first: receipts in order (a module replay leaves them to it)
        replay_module(records, anchors)
    except Refusal:
        return False
    return True


# A disposition carries the clock sample it was decided on, and its append may be received later than that sample:
# a row received after the time it names is one the write path writes, which an oracle run at the receipt cannot
# reproduce (pass 9 P9-11).
DECIDED_BEFORE_RECEIPT = frozenset({K.KIND_DISPOSITION})


# A status row is admitted by one status per source and instant, not by its identifier, because a ledger written
# before PR #54 holds identifiers formed from the declared offset (PR #54 review 4353163787; pass-6 reading (a)).
IDENTIFIER_NOT_ADMITTED = frozenset({K.KIND_STATUS})


def path_writes(write: Write, prefix: tuple[Record, ...], row: Record, anchors: tuple[Anchor, ...],
                scratch: Path) -> bool:
    """Whether the write path, run on ``prefix`` at the row's receipt, writes the row (kind, identifier, payload)."""
    clock = ManualClock(parse_timestamp(row.receipt_time))
    target = scratch / f"oracle-{len(list(scratch.iterdir()))}.sqlite"
    ledger, _ = Ledger.restore(target, clock, chain(rows_of(prefix)), HarnessAnchorStore(anchors))
    try:
        try:
            write(ledger, row)
        except Refusal:
            pass
        written = ledger.records()[len(prefix):]
        any_id = row.kind in IDENTIFIER_NOT_ADMITTED
        return any((w.kind, w.payload) == (row.kind, row.payload) and (any_id or w.record_id == row.record_id)
                   for w in written)
    finally:
        ledger.close()


def disagreements(records: tuple[Record, ...], anchors: tuple[Anchor, ...], own: frozenset[str], replay_module: Replay,
                  write: Write, scratch: Path, read_as_written: frozenset[str] = frozenset()) -> list[str]:
    found = []
    for index, row, label in candidates(records, own):
        for position in placements(index, label):
            prefix = records[:position]
            seen = anchors_at(anchors, position, row.receipt_time)
            replayed = replay_accepts(replay_module, prefix, row, seen)
            written = path_writes(write, prefix, row, seen, scratch)
            later = label.startswith("receipt ") and not label.startswith("receipt -") \
                and row.kind in DECIDED_BEFORE_RECEIPT
            if replayed != written and not (replayed and (row.kind in read_as_written or later)):
                found.append(f"{row.kind} {row.record_id} {label} at position {position + 1}: replay "
                             f"{'accepts' if replayed else 'refuses'}, the write path "
                             f"{'writes it' if written else 'refuses it'}")
    return found


# Registration --------------------------------------------------------------------------------------------------


def replay_registration(records: tuple[Record, ...], anchors: tuple[Anchor, ...]) -> object:
    state = registration_module.replay_state(records)
    state.local_anchors = anchors
    registration_module.check_anchor_times(state)
    return state


REGISTRATION_WRITES: dict[str, Callable[[RegistrationRegistry, JsonValue], object]] = {
    K.KIND_ARM_VERSION: lambda r, p: r.register_arm_version(ArmVersion.from_payload(p)),
    K.KIND_CUTOFF_CORRECTION: lambda r, p: r.correct_cutoff(CutoffCorrection.from_payload(p)),
    K.KIND_CANDIDATE: lambda r, p: r.log_candidate(CandidateEntry.from_payload(p)),
    K.KIND_CLUSTER: lambda r, p: r.register_cluster(ClusterRegistration.from_payload(p)),
    K.KIND_VOID_REQUEST: lambda r, p: r.request_void(VoidRequest.from_payload(p)),
    K.KIND_BASE_RATE: lambda r, p: r.commit_base_rate(BaseRate.from_payload(p)),
    K.KIND_FORECAST: lambda r, p: r.submit_forecast(Forecast.from_payload(p)),
    K.KIND_CLAIM: lambda r, p: r.register_claim(ClaimPreregistration.from_payload(p)),
    K.KIND_REGISTER: lambda r, p: r.anchor_confirmatory_register(ConfirmatoryRegister.from_payload(p)),
    K.KIND_CALIBRATION: lambda r, p: r.record_calibration(CalibrationRecord.from_payload(p)),
    K.KIND_BEACON: lambda r, p: r.supply_beacon_output(BeaconOutput.from_payload(p["output"])),  # type: ignore[index, call-overload]
    K.KIND_ROUND_REFUSED: lambda r, p: r.supply_beacon_output(BeaconOutput.from_payload(p["output"])),  # type: ignore[index, call-overload]
    K.KIND_DISCLOSURE: lambda r, p: r.forecasts_of(p["event_id"]),  # type: ignore[index, call-overload, arg-type]
}


def write_registration(ledger: Ledger, row: Record) -> None:
    REGISTRATION_WRITES[row.kind](RegistrationRegistry(ledger), row.payload)


# Disagreements known to be open, each a finding of issue #37 with its open fix: a module's test fails on any other
# disagreement, and the fix removes the entry. None is open: P8-6 and P8-7, found here at the pass-8 pin c37d048, were
# fixed by PR #90.
KNOWN: dict[str, Callable[[str], bool]] = {}


def unknown(found: list[str]) -> list[str]:
    return [line for line in found if not any(match(line) for match in KNOWN.values())]


def registration_disagreements(tmp_path: Path) -> list[str]:
    ledger, store = registration_ledger(tmp_path / "reference.sqlite")
    records = ledger.records()
    assert {r.kind for r in records} == K.REGISTRATION_KINDS  # every kind is tried
    scratch = tmp_path / "oracle"
    scratch.mkdir()
    return disagreements(records, store.anchors(), K.REGISTRATION_KINDS, replay_registration, write_registration,
                         scratch)


def test_invariant_3_registration(tmp_path: Path) -> None:
    found = unknown(registration_disagreements(tmp_path))
    assert not found, "\n".join(found[:20]) + f"\n({len(found)} in all)"


# Adjudication --------------------------------------------------------------------------------------------------


def replay_adjudication(records: tuple[Record, ...], anchors: tuple[Anchor, ...]) -> object:
    return adjudication_module.replay_state(records)


ADJUDICATION_WRITES: dict[str, Callable[[AdjudicationRegistry, JsonValue], object]] = {
    K.KIND_EVENT: lambda r, p: r.register_event(EventSpec.from_payload(p)),
    K.KIND_RULE: lambda r, p: r.register_rule(SourceRule.from_payload(p)),
    K.KIND_CONTENT: lambda r, p: r.archive_content(ArchivedContent.from_payload(p)),
    K.KIND_RECORD: lambda r, p: r.submit_record(ResolutionRecord.from_payload(p)),
    K.KIND_OBSERVATION: lambda r, p: r.submit_observation(AbsenceObservation.from_payload(p)),
    K.KIND_STATUS: lambda r, p: r.declare_source_status(SourceStatus.from_payload(p)),
    # the rows a disposition writes are the path's own: the adjudication of their event at their receipt
    **{kind: (lambda r, p: r.adjudicate(p["event_id"]))  # type: ignore[index, call-overload, arg-type]
       for kind in (K.KIND_DISPOSITION, K.KIND_DEFECT, K.KIND_KNOWABLE, K.KIND_INCIDENT)},
}


def write_adjudication(ledger: Ledger, row: Record) -> None:
    ADJUDICATION_WRITES[row.kind](AdjudicationRegistry(ledger), row.payload)


def adjudication_disagreements(tmp_path: Path) -> list[str]:
    ledger, store = adjudication_ledger(tmp_path / "reference.sqlite")
    records = ledger.records()
    assert {r.kind for r in records} == K.ADJUDICATION_KINDS
    scratch = tmp_path / "oracle"
    scratch.mkdir()
    # Incidents decide nothing and are read as written (pass 5 X2, reading P6-R1): replay may accept one the path
    # would not write, never refuse one it writes.
    return disagreements(records, store.anchors(), K.ADJUDICATION_KINDS, replay_adjudication, write_adjudication,
                         scratch, read_as_written=frozenset({K.KIND_INCIDENT}))


def test_invariant_3_adjudication(tmp_path: Path) -> None:
    found = unknown(adjudication_disagreements(tmp_path))
    assert not found, "\n".join(found[:20]) + f"\n({len(found)} in all)"


# Point in time -------------------------------------------------------------------------------------------------


def ingest_row(ledger: Ledger, row: Record) -> None:
    PointInTimeStore(ledger).ingest(FeatureRow.from_payload(row.payload))


def test_invariant_3_point_in_time(tmp_path: Path) -> None:
    ledger, store = point_in_time_ledger(tmp_path / "reference.sqlite")
    scratch = tmp_path / "oracle"
    scratch.mkdir()
    found = disagreements(ledger.records(), store.anchors(), K.POINT_IN_TIME_KINDS,
                          lambda records, _: point_in_time_module.replay_state(records),
                          ingest_row,
                          scratch)
    assert not found, "\n".join(found[:20]) + f"\n({len(found)} in all)"


# The gate --------------------------------------------------------------------------------------------------------

# The fields of a gate row the gate itself may write with any value: the clock readings (the time source's), an epoch's
# identifier (drawn at random), its reason, release and tolerance (the running gate's), an abort's reason, and a check's
# subject, verdict and reason, which replay does not recompute (reading P6-R1).
GATE_FREE: dict[str, tuple[tuple[Any, ...], ...]] = {
    K.KIND_EPOCH: (("baseline",), ("epoch",), ("reason",), ("release_digest",), ("tolerance",)),
    # an intent's and a commit's reading is continuous with the epoch's baseline: its boot identifier is not free, and
    # a time is free only within the tolerance, which the perturbations below may exceed (issue #37, pass 8 Codex 8-2)
    K.KIND_INTENT: (("reading", "wall"), ("reading", "monotonic")),
    K.KIND_ABORT: (("reading",), ("reason",)),
    K.KIND_COMMIT: (("reading", "wall"), ("reading", "monotonic")),
    # a check's verdict is free between the two the gate writes, and only between them (pass 9 P9-11: replay refuses
    # any other, a rule this test did not try)
    K.KIND_CHECK: (("reading",), ("subject",), ("reason",)),
}
GATE_FREE_VERDICTS = ("('verdict',)='admitted'", "('verdict',)='refused'")
# The perturbations of time the gate itself can make, for which there is no oracle: another receipt, a reading at its
# own receipt, a time moved in several fields (pass 9 P9-11).
GATE_TIMES = ("receipt ", "every ")


def test_invariant_3_gate(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    rig.promote(issue(rig.epoch(), "n-1"))
    rig.gate.perform("sim_read")
    with pytest.raises(Refusal):
        rig.gate.perform("sim_execution")
    rig.store.available = False
    with pytest.raises(Refusal):
        rig.promote(issue(rig.epoch(), "n-2", level="SIM_EXECUTION"))  # the intent anchor fails: aborted
    rig.store.available = True
    rig.gate.demote("test")
    rig.gate.anchor_epoch()
    records, anchors = rig.ledger.records(), rig.ledger.local_anchors()
    assert {r.kind for r in records} == K.GATE_KINDS
    replay_gate(records, max(a.prefix_length for a in anchors), RULES, anchors)  # the reference reads
    found = []
    for index, row, label in candidates(records, K.GATE_KINDS):
        if label == "as written" or any(label.startswith(str(free)[:-1]) for free in GATE_FREE[row.kind]) \
                or label.startswith(GATE_FREE_VERDICTS + GATE_TIMES) or label.endswith("=the receipt"):
            continue
        prefix = records[:index]
        seen = anchors_at(anchors, index + 1, row.receipt_time)
        prefix_length = max((a.prefix_length for a in seen), default=0)
        try:
            replay_gate(chain(rows_of(prefix) + [(row.kind, row.record_id, row.receipt_time, row.payload)]),
                        prefix_length, RULES, seen)
        except Refusal:
            continue
        found.append(f"{row.kind} {row.record_id} {label}: replay reads a row the gate cannot have written")
    assert not found, "\n".join(found[:20]) + f"\n({len(found)} in all)"


def test_invariant_3_fails_on_a_replay_that_trusts_a_row(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The machinery finds class W: a replay that takes a second disposition row as written (pass 5 X2)."""
    ledger, store = adjudication_ledger(tmp_path / "reference.sqlite")
    monkeypatch.setattr(adjudication_module, "_check_disposition", lambda record, stored, state: None)
    scratch = tmp_path / "oracle"
    scratch.mkdir()
    found = disagreements(ledger.records(), store.anchors(), frozenset({K.KIND_DISPOSITION}), replay_adjudication,
                          write_adjudication, scratch)
    assert any("replay accepts, the write path refuses it" in f for f in found)


# Invariant 4: persisted-input equivalence -----------------------------------------------------------------------


def outcome_of(call: Callable[[], object]) -> tuple[str, object]:
    try:
        return "result", call()
    except Refusal as refusal:
        return "refused", refusal.reason


def normalised(value: object) -> object:
    """A result as text, so that a look-alike in a returned value compares as what it persists."""
    return repr(value)


class Draws:
    """Epoch identifiers drawn in order, so that two identical gates write identical ledgers."""

    def __init__(self) -> None:
        self.next = 1000

    def randbits(self, bits: int) -> int:
        self.next += 1
        return self.next


def equivalent(build: Callable[[Path], tuple[Ledger, Any]], call: Callable[[Any, str], object], text: str, alias: str,
               tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """``call`` with ``text`` and with a look-alike of ``text`` that compares as ``alias``, on two identical ledgers."""
    results = []
    for name, argument in (("plain", text), ("disguised", LooksLike(text, alias))):
        monkeypatch.setattr(gate_module, "secrets", Draws())
        ledger, subject = build(tmp_path / name)
        result = outcome_of(lambda: call(subject, argument))
        try:
            exported = ledger.export_jsonl()
        except Refusal as refusal:  # pragma: no cover - a ledger that cannot export is a difference too
            exported = f"refused {refusal.reason}"
        results.append((normalised(result), exported))
        ledger.close()
    (plain, plain_ledger), (disguised, disguised_ledger) = results
    problems = []
    if plain != disguised:
        problems.append(f"{text!r} as {alias!r}: plain gives {plain}, the look-alike {disguised}")
    if plain_ledger != disguised_ledger:
        problems.append(f"{text!r} as {alias!r}: the ledgers differ")
    return problems


def registration_subject(path: Path) -> tuple[Ledger, RegistrationRegistry]:
    path.mkdir()
    ledger, _ = registration_ledger(path / "l.sqlite")
    ledger._clock.set(day(46))  # type: ignore[attr-defined]  # after every close, so sealed reads are open
    return ledger, RegistrationRegistry(ledger)


def adjudication_subject(path: Path) -> tuple[Ledger, AdjudicationRegistry]:
    path.mkdir()
    ledger, _ = adjudication_ledger(path / "l.sqlite")
    r = AdjudicationRegistry(ledger)
    ledger._clock.set(aday(120))  # type: ignore[attr-defined]
    r.submit_observation(observation(115, event_id="H"))
    return ledger, r


def gate_subject(path: Path) -> tuple[Ledger, CapabilityGate]:
    path.mkdir()
    rig = Rig(path)
    rig.tick()
    return rig.ledger, rig.gate


def reader_subject(path: Path) -> tuple[Ledger, AsOfReader]:
    path.mkdir()
    ledger, _ = point_in_time_ledger(path / "l.sqlite")
    return ledger, PointInTimeStore(ledger).reader(datetime(2026, 1, 9, tzinfo=timezone.utc))


def issuance_subject(path: Path) -> tuple[Ledger, None]:
    path.mkdir()
    return Ledger(path / "l.sqlite", ManualClock(day(1))), None


def _issuance_versions(provider: str) -> dict[str, str]:
    return {provider if p == "P-A" else p: v for p, v in VERSIONS.items()}


# (entry point, builder, call, text, alias): the alias is another value the subject holds, so that a decision taken
# on the look-alike's comparison rather than on its text differs from the plain one.
ENTRY_POINTS: list[tuple[str, Callable[[Path], tuple[Ledger, Any]], Callable[[Any, Any], object], str, str]] = [
    ("RegistrationRegistry.arm_version", registration_subject, lambda r, a: r.arm_version(a), "B-2", "B-1"),
    ("RegistrationRegistry.event", registration_subject, lambda r, a: r.event(a), "E-3", "E-1"),
    ("RegistrationRegistry.forecasts_of", registration_subject, lambda r, a: r.forecasts_of(a), "E-2", "E-1"),
    ("RegistrationRegistry.forecasts_for_baseline", registration_subject, lambda r, a: r.forecasts_for_baseline(a),
     "E-2", "E-1"),
    ("RegistrationRegistry.slot_states", registration_subject, lambda r, a: r.slot_states(a), "E-3", "E-1"),
    ("RegistrationRegistry.claim_status", registration_subject, lambda r, a: r.claim_status(a), "claim-3", "claim-1"),
    ("RegistrationRegistry.seed_of", registration_subject, lambda r, a: r.seed_of(a), "cal-2", "cal-1"),
    ("RegistrationRegistry.submit_forecast", registration_subject,
     lambda r, a: r.submit_forecast(replace(forecast("E-1"), event_id=a)), "E-3", "E-1"),
    ("AdjudicationRegistry.adjudicate", adjudication_subject, lambda r, a: r.adjudicate(a), "G", "H"),
    ("AdjudicationRegistry.submit_observation", adjudication_subject,
     lambda r, a: r.submit_observation(replace(observation(116, event_id="H"), event_id=a)), "Z", "H"),
    ("CapabilityGate.perform", gate_subject, lambda g, a: g.perform(a), "sim_execution", "research"),
    ("CapabilityGate.demote", gate_subject, lambda g, a: g.demote(a) and None, "reason-a", "reason-b"),
    ("CapabilityGate.promote", gate_subject,
     lambda g, a: g.promote(replace(issue(g.state().epoch, "n-1"), environment=a), EVIDENCE), "env-2", "env-1"),
    ("CapabilityGate.__init__", gate_subject,
     lambda g, a: CapabilityGate(g._ledger, g._verifier, g._time, a, g._release_digest, 1.0).promote(
         issue(g.state().epoch + 0, "n-1", environment="env-2"), EVIDENCE).status, "env-1", "env-2"),
    ("AsOfReader.series", reader_subject, lambda r, a: r.series(a, "f"), "Z", "X"),
    ("AsOfReader.row", reader_subject, lambda r, a: r.row("X", "f", a), "v9", "v1"),
    ("PointInTimeStore.ingest", reader_subject,
     lambda r, a: r._store.ingest(FeatureRow("X", "f", 2.0, datetime(2026, 1, 1, tzinfo=timezone.utc),
                                             datetime(2026, 1, 2, tzinfo=timezone.utc), a)), "v9", "v1"),
    ("check_issuance.event_id", issuance_subject,
     lambda _, a: check_issuance(a, VERSIONS, [output(p, event_id="E-2") for p in ("P-A", "P-B", "P-C")],
                                 jev(event_id="E-2"), slot_id="primary").status, "E-1", "E-2"),
    ("check_issuance.slot_id", issuance_subject,
     lambda _, a: check_issuance("E-1", VERSIONS, [output(p, slot_id="other") for p in ("P-A", "P-B", "P-C")],
                                 jev(), slot_id=a).status, "primary", "other"),
    ("check_issuance.arm_versions", issuance_subject,
     lambda _, a: check_issuance("E-1", _issuance_versions(a), [output(p) for p in ("P-A", "P-B", "P-C")],
                                 jev(), slot_id="primary").status, "P-X", "P-A"),
]


# Entry points that fail the invariant, each a finding of issue #37: a strict expected failure until its fix lands,
# which removes the entry. None is open: P8-1 to P8-5, found here at the pass-8 pin c37d048, were fixed by PR #89.
OPEN_FINDINGS: dict[str, str] = {}


@pytest.mark.parametrize("name, build, call, text, alias", [
    pytest.param(*entry, id=entry[0], marks=[pytest.mark.xfail(strict=True, reason=OPEN_FINDINGS[entry[0]])]
                 if entry[0] in OPEN_FINDINGS else []) for entry in ENTRY_POINTS])
def test_invariant_4_persisted_input_equivalence(name: str, build: Callable[[Path], tuple[Ledger, Any]],
                                                 call: Callable[[Any, Any], object], text: str, alias: str,
                                                 tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    problems = equivalent(build, call, text, alias, tmp_path, monkeypatch)
    assert not problems, f"{name}: " + "; ".join(problems)


# Public entry points that take no text a decision reads: a schema object (read back through ``as_persisted``, pass 7
# P7-R3, and covered here by one representative per registry), or nothing.
SCHEMA_OBJECT_ENTRY_POINTS = frozenset({
    "RegistrationRegistry.register_arm_version", "RegistrationRegistry.correct_cutoff",
    "RegistrationRegistry.log_candidate", "RegistrationRegistry.commit_base_rate",
    "RegistrationRegistry.register_cluster", "RegistrationRegistry.request_void", "RegistrationRegistry.register_claim",
    "RegistrationRegistry.anchor_confirmatory_register", "RegistrationRegistry.record_calibration",
    "RegistrationRegistry.supply_beacon_output", "RegistrationRegistry.state", "RegistrationRegistry.candidate_counts",
    "AdjudicationRegistry.register_event", "AdjudicationRegistry.register_rule",
    "AdjudicationRegistry.archive_content", "AdjudicationRegistry.submit_record",
    "AdjudicationRegistry.declare_source_status", "AdjudicationRegistry.state",
    "CapabilityGate.state", "CapabilityGate.anchor_epoch",
    "PointInTimeStore.reader", "PointInTimeStore.reader_for",
})


def test_every_public_entry_point_is_covered() -> None:
    public = {f"{owner.__name__}.{name}" for owner in (RegistrationRegistry, AdjudicationRegistry, CapabilityGate,
                                                      PointInTimeStore, AsOfReader)
              for name, member in inspect.getmembers(owner, inspect.isfunction) if not name.startswith("_")}
    covered = {name.split(".")[0] + "." + name.split(".")[1] for name, *_ in ENTRY_POINTS if "." in name}
    missing = public - covered - SCHEMA_OBJECT_ENTRY_POINTS
    assert not missing, f"public entry points without a persisted-input case: {sorted(missing)}"


# The machinery of invariants 1 and 2 fails on the defects it is for ---------------------------------------------


def test_invariant_2_fails_on_a_restore_that_drops_a_persisted_wall_time(tmp_path: Path,
                                                                        monkeypatch: pytest.MonkeyPatch) -> None:
    """Pass 7, Codex 7-1: a restore that kept receipts only lost the wall time a gate check persisted."""
    clock = RollbackAfterNextRead(day(1))
    time = ManualTimeSource(clock)
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    gate = CapabilityGate(ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    time.advance(timedelta(seconds=1))
    clock.step = timedelta(milliseconds=500)  # the check's wall time is above its receipt
    gate.perform("research")
    assert invariants.check_ledger(ledger, str(tmp_path / "l.sqlite"), (RULES,), tmp_path) == []
    with monkeypatch.context() as patch:
        patch.setattr(store_module, "_persisted_wall", lambda records: None)
        problems = invariants.check_ledger(ledger, str(tmp_path / "l.sqlite"), (RULES,), tmp_path)
    assert any(problem.startswith("write-restore: the clock floor") for problem in problems)


def test_invariant_1_fails_on_a_returned_value_the_ledger_does_not_hold(tmp_path: Path,
                                                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Pass 4, A7: ``adjudicate`` returned a knowable time computed on a stale snapshot."""
    ledger, _ = adjudication_ledger(tmp_path / "l.sqlite")
    registry = AdjudicationRegistry(ledger)
    stored = registry.adjudicate("F")
    assert invariants.AFTER[(AdjudicationRegistry, "adjudicate")](registry, stored, "F") == []
    stale = replace(stored, knowable_at=aday(100))
    problems = invariants.AFTER[(AdjudicationRegistry, "adjudicate")](registry, stale, "F")
    assert problems and "knowable_at" in problems[0]


def test_invariant_1_checks_a_write_called_with_keyword_arguments(tmp_path: Path) -> None:
    """PR #88 review 4417450701 (P2): the post-write check took the call's positional arguments only, so a write
    called by keyword failed in the check after it had completed."""
    clock = ManualClock(aday(1))
    registry = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    registry.register_rule(rule())
    registry.register_event(aspec())
    clock.set(aday(111))
    registry.submit_observation(observation=observation(110))  # at 69a6cd0: TypeError in the check
    assert registry.adjudicate(event_id="E").disposition == "RESOLVED_NO"


# Invariants 5 to 7 (pass 9): the machinery fails on the defects it is for --------------------------------------------


def test_invariant_5_fails_on_a_receipt_below_an_anchor_and_on_a_floor_below_a_bound() -> None:
    """A record received below the publication time of an anchor of a shorter prefix, a gate reading below an earlier
    receipt, and a ledger whose clock floor is below the latest persisted bound are each a problem."""
    reading: JsonValue = {"wall": format_timestamp(day(1)), "monotonic": 0.0, "boot_id": "boot-1"}
    records = chain([("candidate", "a", format_timestamp(day(2)), {}),
                     ("gate_check", "b", format_timestamp(day(2)), {"reading": reading}),
                     ("candidate", "c", format_timestamp(day(3)), {})])
    late_anchor = Anchor(1, records[0].entry_hash, format_timestamp(day(4)))
    problems = invariants.clock_problems(records, (late_anchor,), format_timestamp(day(3)), "written")
    assert any("gate_check b has reading" in p for p in problems)  # a sample below the receipt before it
    assert any("candidate c has receipt" in p for p in problems)  # received below the anchor of a shorter prefix
    assert any("refuses its clock below" in p for p in problems)  # the floor is under the anchor's time
    clean = chain([("candidate", "a", format_timestamp(day(2)), {})])
    assert invariants.clock_problems(clean, (Anchor(1, clean[0].entry_hash, format_timestamp(day(2))),),
                                     format_timestamp(day(2)), "written") == []


def test_invariant_6_fails_on_a_replay_that_skips_the_rule_the_write_path_refuses_by(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Criteria recorded after the issuance window opened are refused online (``late_registration``, pass 1 C2); a
    replay that admitted rows without their rule would read the same row appended raw (pass 6 Y1)."""
    clock = ManualClock(aday(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    clock.set(aday(80))  # after the window of the event opened
    late = aspec(event_id="LATE")
    with pytest.raises(Refusal) as refused:
        registry.register_event(late)
    assert refused.value.reason == "late_registration"
    assert invariants.symmetry_problems(registry, "register_event", late, refused.value, tmp_path) == []
    monkeypatch.setattr(adjudication_module, "_replayed", lambda record, expected_id, admit: None)
    problems = invariants.symmetry_problems(registry, "register_event", late, refused.value, tmp_path)
    assert problems and problems[0].startswith("refusal symmetry: AdjudicationRegistry.register_event refused "
                                               "late_registration")


def test_every_write_path_is_covered_by_invariant_6() -> None:
    """Every public method of the registries and the store that writes a row is wrapped by invariant 6, or is a read,
    or writes only rows its own refusals never leave unwritten (``adjudicate``: a refused adjudication has no
    disposition to append)."""
    wrapped = {f"{owner.__name__}.{name}" for owner, name in invariants.SYMMETRY}
    reads_or_derived = {
        "RegistrationRegistry.arm_version", "RegistrationRegistry.event", "RegistrationRegistry.slot_states",
        "RegistrationRegistry.forecasts_for_baseline", "RegistrationRegistry.claim_status",
        "RegistrationRegistry.seed_of", "RegistrationRegistry.state", "RegistrationRegistry.candidate_counts",
        "AdjudicationRegistry.state", "AdjudicationRegistry.adjudicate",
        "PointInTimeStore.reader", "PointInTimeStore.reader_for",
    }
    public = {f"{owner.__name__}.{name}" for owner in (RegistrationRegistry, AdjudicationRegistry, PointInTimeStore)
              for name, _ in inspect.getmembers(owner, inspect.isfunction) if not name.startswith("_")}
    assert public - wrapped - reads_or_derived == set()


def test_invariant_7_fails_on_a_release_without_its_disclosure_row(tmp_path: Path,
                                                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """Pass 8 Codex 8-1: a read that released sealed forecasts after the close persisted nothing."""
    ledger, _ = registration_ledger(tmp_path / "l.sqlite")
    registry = RegistrationRegistry(ledger)
    assert invariants.AFTER[(RegistrationRegistry, "forecasts_of")](registry, (), "E-1") == []  # E-1 is released
    monkeypatch.setattr(RegistrationRegistry, "_disclose", lambda self, event_id: None)
    registry._invariants_quiet = 1  # type: ignore[attr-defined]  # the defect is made on purpose: not the fixture's
    released = registry.forecasts_of("E-2")  # closed at day 40, read at day 45, two forecasts and no row
    assert released
    problems = invariants.AFTER[(RegistrationRegistry, "forecasts_of")](registry, released, "E-2")
    assert problems and "E-2" in problems[0]


# Open findings of pass 9 at the pin 811ba9d, each a strict expected failure until its fix lands (the fix removes the
# mark and its entry in ``invariants.KNOWN_OPEN``).


@pytest.mark.parametrize("read", ["forecasts_of", "forecasts_for_baseline", "slot_states"])
def test_p9_1_a_read_that_decided_the_close_bounds_the_clock_when_nothing_is_sealed(tmp_path: Path, read: str) -> None:
    """E-2 closes at day 40 with no forecast. A read at day 41 answers as only a closed event can (an empty release, or
    every slot an abstention, ``18`` M-5) and persists nothing; the clock stepped back to day 30, above every receipt,
    then admits a forecast that fills the slot the read reported as an abstention (RC-109; ``17`` item 2 "Clock")."""
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = RegistrationRegistry(ledger)
    registry.register_arm_version(arm("A-1", "2026-01-05"))
    registry.register_arm_version(arm("DESIGN_C-1", "2026-01-01"))
    registry.register_arm_version(arm("FULL-1", "2026-01-03", ["A-1"]))
    registry.commit_base_rate(BaseRate("RC-1", 0.2))
    registry.log_candidate(CandidateEntry("cand-E-2", "E-2", "src", day(1), "registered", "predicate match"))
    clock.set(day(10))
    registry.register_cluster(registration([spec("E-2", cluster_id="C-2")], cluster_id="C-2"))
    clock.set(day(41))
    result = getattr(registry, read)("E-2")
    if read == "slot_states":
        assert {s.arm_id: s.status for s in result}["FULL"] == "abstention"
    else:
        assert result == ()
    assert invariants.AFTER[(RegistrationRegistry, read)](registry, result, "E-2") == []  # at 811ba9d: no row
    clock.set(day(30))
    with pytest.raises(Refusal) as refused:
        registry.submit_forecast(forecast("E-2"))  # at 811ba9d: admitted, filling FULL's slot
    assert refused.value.reason == "clock_rollback"


def test_p9_2_a_commit_read_below_a_persisted_wall_time_confers_no_level(tmp_path: Path) -> None:
    """The protected operation takes no step on a reading below the latest wall time a persisted reading observed: it
    refuses ``clock_rollback`` (RC-37, RC-65; ``17`` item 2 "Clock"). Replay judges an intent's and a commit's reading
    by its boot identifier and drift only (pass 8 Codex 8-2), so a commit appended raw with the epoch's start reading,
    below its own intent's, is read and confers its level: ``perform("sim_read")`` is admitted."""
    rig = Rig(tmp_path)
    rig.tick()

    def killed() -> None:
        raise RuntimeError("the gate stops after its intent anchor")

    rig.gate.hooks["after_intent_anchor"] = killed
    with pytest.raises(RuntimeError):
        rig.promote(issue(rig.epoch(), "a"))
    state = rig.gate.state()
    (intent_id,) = state.intents
    stale = state.baseline
    assert stale is not None and stale.wall < state.intents[intent_id].reading.wall
    anchor = rig.ledger.local_anchors()[-1]
    rig.ledger.append(K.KIND_COMMIT, gate_ledger_id("gate-commit", intent_id),
                      CommitRecord(intent_id, anchor.prefix_length, anchor.digest, stale).to_payload())
    rig.ledger.anchor()
    rig.tick()
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("sim_read")  # at 811ba9d: admitted at SIM_READ_ONLY
    assert refused.value.reason == "invalid_gate_ledger"


def test_invariant_1_replays_the_module_after_a_write_whose_row_it_refuses(tmp_path: Path) -> None:
    """Pass 9 P9-11: a write path that writes a row its own replay refuses (here a claim received after its period
    started, as a write without its ``late_claim`` check would) is found right after the write, not only when a test
    reads the ledger again."""
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = RegistrationRegistry(ledger)
    claim = ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                 "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1")
    clock.set(day(61))
    written = ledger.append(K.KIND_CLAIM, registration_module._ledger_id("claim", "claim-1"), claim.to_payload())
    problems = invariants.AFTER[(RegistrationRegistry, "register_claim")](registry, written, claim)
    assert problems and "own replay refuses the ledger it wrote" in problems[0]
    with pytest.raises(Refusal):
        registry.event("E-1")  # the ledger is unreadable from here on
