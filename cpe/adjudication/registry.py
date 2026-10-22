"""The adjudication registry on the ledger: archived content and records in, immutable dispositions out, state by
replay."""
from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Protocol, TypeVar

from cpe.adjudication.content import ArchivedContent
from cpe.adjudication.records import AbsenceObservation, ResolutionRecord, SourceRule, SourceStatus
from cpe.adjudication.rules import (
    FINAL,
    Adjudication,
    Defect,
    Incident,
    ReceivedRecord,
    adjudicate,
    check_record_chronology,
    check_record_content,
    check_record_is_final_enough,
    earliest_public_occurrence,
    late_contradictions,
)
from cpe.canonical import digest_of
from cpe.clock import parse_timestamp
from cpe.schemas.common import Payload, require_identifier, require_keys, timestamp_payload
from cpe.errors import Refusal
from cpe.ledger import Ledger, Record
from cpe.schemas.event import EventSpec

KIND_EVENT = "event_spec"
KIND_RULE = "source_rule"
KIND_RECORD = "resolution_record"
KIND_OBSERVATION = "absence_observation"
KIND_STATUS = "source_status"
KIND_DISPOSITION = "disposition"
KIND_DEFECT = "source_latency_defect"
KIND_INCIDENT = "integrity_incident"
KIND_CONTENT = "resolution_content"
KIND_KNOWABLE = "knowable_correction"
KINDS: frozenset[str] = frozenset({KIND_EVENT, KIND_RULE, KIND_RECORD, KIND_OBSERVATION, KIND_STATUS, KIND_DISPOSITION,
                                   KIND_DEFECT, KIND_INCIDENT, KIND_CONTENT, KIND_KNOWABLE})


class _Persisted(Protocol):
    def to_payload(self) -> Payload: ...


_T = TypeVar("_T")


def _as_replayed(value: _Persisted, from_payload: Callable[[object], _T]) -> _T:
    """The value as replay will read it: every input is validated in full through its payload before anything is
    computed or written, so that the registry never writes a row its own replay refuses, and every later reader of
    the ledger fails (issue #37, pass 3 A2, A3; pass 4 A5). An object whose fields cannot be serialised is refused
    alike."""
    try:
        payload = value.to_payload()
    except Refusal:
        raise
    except Exception as error:
        raise Refusal("invalid_object", f"{type(value).__name__} cannot be serialised: {error!r}") from None
    return from_payload(payload)


def _ledger_id(prefix: str, *parts: str) -> str:
    """A ledger identifier for a registry record: the prefix and the digest of its parts, so that an external
    identifier of any admitted length, with any character, yields one identifier within the limit."""
    return f"{prefix}:{digest_of(list(parts))}"


@dataclass
class _EventState:
    spec: EventSpec | None = None
    records: list[ReceivedRecord] = field(default_factory=list)
    observations: list[AbsenceObservation] = field(default_factory=list)
    observation_receipts: dict[str, datetime] = field(default_factory=dict)
    disposition: Adjudication | None = None
    defect_record_ids: set[str] = field(default_factory=set)


@dataclass
class _State:
    head: str = ""
    rules: dict[str, SourceRule] = field(default_factory=dict)
    status: dict[str, list[tuple[SourceStatus, datetime]]] = field(default_factory=dict)  # with the receipt
    events: dict[str, _EventState] = field(default_factory=dict)
    contents: dict[str, tuple[ArchivedContent, datetime]] = field(default_factory=dict)  # by SHA-256, with receipt

    def event(self, event_id: str) -> _EventState:
        return self.events.setdefault(event_id, _EventState())


def replay_state(records: tuple[Record, ...]) -> _State:
    state = _State()
    for record in records:
        state.head = record.entry_hash
        if record.kind not in KINDS:
            continue  # another registry's record on the same ledger, whatever its payload
        payload = record.payload
        if not isinstance(payload, dict):
            raise Refusal("invalid_payload", f"{record.record_id}: a {record.kind} record carries a mapping")
        if record.kind == KIND_EVENT:
            spec = EventSpec.from_payload(payload)
            state.event(spec.event_id).spec = spec
        elif record.kind == KIND_RULE:
            rule = SourceRule.from_payload(payload)
            state.rules[rule.source_id] = rule
        elif record.kind == KIND_CONTENT:
            content = ArchivedContent.from_payload(payload)
            receipt = parse_timestamp(record.receipt_time, "receipt_time")
            if content.available_at > receipt:  # the bound archive_content enforces online (PR #32 4335196673)
                raise Refusal("evidence_after_receipt", f"{record.record_id}: content available after its receipt")
            state.contents[content.sha256] = (content, receipt)
        elif record.kind == KIND_RECORD:
            resolution = ResolutionRecord.from_payload(payload)
            archived = state.contents.get(resolution.content_digest)
            if archived is None:
                raise Refusal("unknown_content", f"{resolution.record_id} names content the ledger does not hold "
                              "before it")
            state.event(resolution.event_id).records.append(
                ReceivedRecord(resolution, parse_timestamp(record.receipt_time, "receipt_time"), archived[0]))
        elif record.kind == KIND_OBSERVATION:
            observation = AbsenceObservation.from_payload(payload)
            event = state.event(observation.event_id)
            event.observations.append(observation)
            event.observation_receipts[observation.observation_id] = parse_timestamp(record.receipt_time, "receipt_time")
        elif record.kind == KIND_STATUS:
            status = SourceStatus.from_payload(payload)
            state.status.setdefault(status.source_id, []).append(
                (status, parse_timestamp(record.receipt_time, "receipt_time")))
        elif record.kind == KIND_DISPOSITION:
            adjudication = Adjudication.from_payload(payload)
            state.event(adjudication.event_id).disposition = adjudication
        elif record.kind == KIND_DEFECT:
            require_keys(payload, KIND_DEFECT, frozenset({"event_id", "record_id", "detail"}), frozenset())
            event_id = require_identifier(payload["event_id"], "event_id")
            defect_id = require_identifier(payload["record_id"], "record_id")
            detail = payload["detail"]
            if not isinstance(detail, str):
                raise Refusal("invalid_text", f"{record.record_id}: detail must be a string")
            event = state.event(event_id)
            event.defect_record_ids.add(defect_id)
            if event.disposition is not None and defect_id not in {d.record_id for d in event.disposition.defects}:
                event.disposition = replace(event.disposition,
                                            defects=event.disposition.defects + (Defect(defect_id, detail),))
        elif record.kind == KIND_KNOWABLE:
            require_keys(payload, KIND_KNOWABLE, frozenset({"event_id", "knowable_at", "record_id"}), frozenset())
            event_id = require_identifier(payload["event_id"], "event_id")
            require_identifier(payload["record_id"], "record_id")
            knowable = parse_timestamp(payload["knowable_at"], "knowable_at")
            event = state.event(event_id)
            if event.disposition is not None and event.disposition.knowable_at is not None \
                    and knowable < event.disposition.knowable_at:
                event.disposition = replace(event.disposition, knowable_at=knowable)
        elif record.kind == KIND_INCIDENT:
            if "event_id" not in payload:
                raise Refusal("missing_field", f"{record.record_id}: an integrity incident names its event")
            event_id = require_identifier(payload["event_id"], "event_id")
            incident = Incident.from_payload({k: v for k, v in payload.items() if k != "event_id"})
            event = state.event(event_id)
            if event.disposition is not None and (incident.kind, incident.reference_id) not in {
                    (i.kind, i.reference_id) for i in event.disposition.incidents}:
                event.disposition = replace(event.disposition, incidents=event.disposition.incidents + (incident,))
    return state


def _not_after(evidenced: datetime, what: str) -> Callable[[datetime], None]:
    """An append's admission check: the evidence time is at or before the receipt the append assigns, not an
    earlier clock sample (H1 review 4334622048)."""
    def admit(receipt: datetime) -> None:
        if evidenced > receipt:
            raise Refusal("evidence_after_receipt", f"{what}: evidenced after its receipt")
    return admit


class AdjudicationRegistry:
    """Writes event specifications, source rules, records, observations and dispositions to the ledger; reads its
    state by replay only; takes every time from the ledger's clock; serialises its own read-decide-write."""

    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger
        self._lock = threading.RLock()
        self.before_write: Callable[[], None] | None = None  # test hook, run between the snapshot and the write

    def state(self) -> _State:
        return replay_state(self._ledger.records())

    def register_event(self, spec: EventSpec) -> None:
        """Pre-register the resolution criteria once: after the source rule they name, before the issuance window
        opens; a different specification under the same id is refused."""
        spec = _as_replayed(spec, EventSpec.from_payload)
        with self._lock:
            for attempt in range(2):  # another writer on the same ledger that lands the event first is read back
                state = self.state()
                existing = state.event(spec.event_id).spec
                if existing is not None:
                    if existing != spec:
                        raise Refusal("event_immutable", f"{spec.event_id} is registered with other criteria")
                    return
                if spec.predicate.source not in state.rules:
                    raise Refusal("unknown_source", f"{spec.predicate.source} has no registered source rule (OD5)")

                def before_the_window(receipt: datetime) -> None:  # the receipt is the time that counts (issue #37, C2)
                    if receipt >= spec.issuance_open:
                        raise Refusal("late_registration", f"{spec.event_id}: the criteria must be recorded before "
                                      "the issuance window opens")

                before_the_window(self._ledger.now())
                try:
                    self._ledger.append(KIND_EVENT, _ledger_id("event", spec.event_id), spec.to_payload(),
                                        admit=before_the_window)
                    return
                except Refusal as refusal:
                    if refusal.reason != "duplicate_record_id" or attempt:
                        raise

    def _spec(self, state: _State, event_id: str) -> EventSpec:
        spec = state.event(event_id).spec
        if spec is None:
            raise Refusal("unknown_event", f"{event_id} has no registered specification")
        return spec

    def register_rule(self, rule: SourceRule) -> None:
        rule = _as_replayed(rule, SourceRule.from_payload)
        with self._lock:
            for attempt in range(2):  # another writer on the same ledger that lands the rule first is read back
                existing = self.state().rules.get(rule.source_id)
                if existing is not None:
                    if existing != rule:
                        raise Refusal("rule_immutable", f"source {rule.source_id} already has a different rule")
                    return
                try:
                    self._ledger.append(KIND_RULE, _ledger_id("rule", rule.source_id), rule.to_payload())
                    return
                except Refusal as refusal:
                    if refusal.reason != "duplicate_record_id" or attempt:
                        raise

    def archive_content(self, content: ArchivedContent) -> Record:
        """Archive source bytes under their SHA-256, with the ledger's receipt time. The content is an attested
        input; nothing is fetched. The same bytes with the same attestation are archived once; the same bytes with
        another attestation are refused, so that one digest names one archived read."""
        content = _as_replayed(content, ArchivedContent.from_payload)
        with self._lock:
            state = self.state()
            if content.source_id not in state.rules:
                raise Refusal("unknown_source", f"{content.source_id} has no registered source rule (OD5)")
            existing = state.contents.get(content.sha256)
            if existing is not None:
                if existing[0] != content:
                    raise Refusal("content_conflict", f"content {content.sha256} is archived with another "
                                  "attestation")
                return next(r for r in self._ledger.records() if r.record_id == _ledger_id("content", content.sha256))

            def admit(receipt: datetime) -> None:
                if content.available_at > receipt:
                    raise Refusal("evidence_after_receipt", f"content {content.sha256} is available after its receipt")
            record_id = _ledger_id("content", content.sha256)
            try:
                return self._ledger.append(KIND_CONTENT, record_id, content.to_payload(), admit=admit)
            except Refusal as refusal:
                if refusal.reason != "duplicate_record_id":
                    raise
            # Another writer on the same ledger archived the same digest first: read it back, as register_rule and
            # register_event do (issue #37, pass 3; the class of D2).
            landed = self.state().contents.get(content.sha256)
            if landed is None or landed[0] != content:
                raise Refusal("content_conflict", f"content {content.sha256} is archived with another attestation")
            return next(r for r in self._ledger.records() if r.record_id == record_id)

    def submit_record(self, record: ResolutionRecord) -> Record:
        """Admit a record that names archived content; the content must evaluate, under the registered predicate,
        to the claim the record states."""
        record = _as_replayed(record, ResolutionRecord.from_payload)
        with self._lock:
            state = self.state()
            spec = self._spec(state, record.event_id)
            rule = state.rules.get(record.source_id)
            if rule is None:
                raise Refusal("unknown_source", f"{record.source_id} has no registered source rule (OD5)")
            archived = state.contents.get(record.content_digest)
            if archived is None:
                raise Refusal("unknown_content", f"{record.record_id}: content {record.content_digest} is not archived")
            received = ReceivedRecord(record, self._ledger.now(), archived[0])
            check_record_content(received, spec)
            check_record_is_final_enough(record, spec, rule)
            if rule.publishes_evidenced_times and record.evidenced_publication_time is None:
                raise Refusal("missing_publication_time", f"{record.record_id}: the source evidences publication times")
            check_record_chronology(received)
            return self._ledger.append(KIND_RECORD, _ledger_id("record", record.record_id), record.to_payload(),
                                       admit=lambda receipt: check_record_chronology(replace(received, receipt=receipt)))

    def submit_observation(self, observation: AbsenceObservation) -> Record:
        observation = _as_replayed(observation, AbsenceObservation.from_payload)
        with self._lock:
            state = self.state()
            spec = self._spec(state, observation.event_id)
            if observation.source_id != spec.predicate.source:
                raise Refusal("wrong_source", f"{observation.source_id} is not the resolution source of {spec.event_id}")
            if observation.source_id not in state.rules:
                raise Refusal("unknown_source", f"{observation.source_id} has no registered source rule (OD5)")
            return self._ledger.append(KIND_OBSERVATION, _ledger_id("observation", observation.observation_id),
                                       observation.to_payload(), admit=_not_after(observation.observed_at,
                                                                                   observation.observation_id))

    def declare_source_status(self, status: SourceStatus) -> Record:
        """One status per source and declared instant. The status is read as replay reads it, in UTC, before its
        identifier is formed, so that one instant written in two time zones is one status, not two conflicting ones
        (issue #37, pass 4 A6); the identifier format is unchanged."""
        status = _as_replayed(status, SourceStatus.from_payload)
        with self._lock:
            if status.source_id not in self.state().rules:
                raise Refusal("unknown_source", f"{status.source_id} has no registered source rule (OD5)")
            return self._ledger.append(KIND_STATUS, _ledger_id("status", status.source_id, status.declared_at.isoformat()),
                                       status.to_payload(), admit=_not_after(status.declared_at,
                                                                             f"the status of {status.source_id}"))

    def adjudicate(self, event_id: str) -> Adjudication:
        """Adjudicate the event at the ledger's clock. A final disposition is written once, against the chain head
        the decision was computed on, and never rewritten; a record that arrives after it can only add a
        source-latency defect (RC-88)."""
        with self._lock:
            for _ in range(8):
                state = self.state()
                spec = self._spec(state, event_id)
                rule = state.rules.get(spec.predicate.source)
                if rule is None:
                    raise Refusal("unknown_source", f"{spec.predicate.source} has no registered source rule (OD5)")
                event = state.event(event_id)
                now = self._ledger.now()
                # Only a status the registry held by logical finality can decide the failure condition (RC-88).
                held = {status: receipt for status, receipt in state.status.get(rule.source_id, [])
                        if receipt <= spec.logical_finality}
                fresh = adjudicate(spec, rule, event.records, event.observations, list(held), now,
                                   event.observation_receipts, held)
                if self.before_write is not None:
                    hook, self.before_write = self.before_write, None
                    hook()
                if event.disposition is not None:
                    try:
                        self._late_rows(event_id, spec, rule, event, fresh)
                        # The disposition the ledger holds, side rows of other writers included: the rows above were
                        # computed on a snapshot another writer may have extended (issue #37, pass 4 A7).
                        stored = self.state().event(event_id).disposition
                        assert stored is not None
                        return stored
                    except Refusal as refusal:
                        if refusal.reason != "duplicate_record_id":
                            raise
                        continue  # another writer on the same ledger wrote the row first; the re-read state holds it
                if fresh.disposition not in FINAL:
                    return fresh
                # One record: the disposition with its defects and incidents embedded; nothing to lose between
                # a commit and a side row.
                try:
                    self._ledger.append(KIND_DISPOSITION, _ledger_id("disposition", event_id), fresh.to_payload(),
                                        expected_head=state.head)
                except Refusal as refusal:
                    if refusal.reason != "stale_head":
                        raise
                    continue
                return fresh
            raise Refusal("contended", f"{event_id}: the ledger kept advancing during adjudication")

    def _late_rows(self, event_id: str, spec: EventSpec, rule: SourceRule, event: _EventState,
                   fresh: Adjudication) -> Adjudication:
        """The rows found after a stored disposition: source-latency defects, a knowable-time correction and
        incidents. A row another writer landed first refuses its append as a duplicate; the caller re-reads."""
        # The disposition record embeds the defects and incidents known when it was written; side rows carry only
        # those found later. Both sets are known, so a retry adds nothing twice.
        stored = event.disposition
        assert stored is not None
        known_defects = event.defect_record_ids | {d.record_id for d in stored.defects}
        for defect in late_contradictions(spec, rule, event.records, stored.disposition):
            if defect.record_id not in known_defects:
                self._ledger.append(KIND_DEFECT, _ledger_id("defect", event_id, defect.record_id),
                                    {"event_id": event_id, "record_id": defect.record_id, "detail": defect.detail})
                stored = replace(stored, defects=stored.defects + (defect,))
        # A public occurrence that arrives after the disposition still sets knowable_at (RC-146 read with RC-88,
        # section 9.2); the disposition itself stays (H1 review 4334622042). So does the earliest evidenced
        # publication of a timely deciding record, whether or not it agrees with the stored disposition: the outcome
        # information was public from then on, and a contradiction stays a recorded defect (issue #37, Codex 2;
        # PR #44 review 4351249330; a reading, see S2).
        earliest = earliest_public_occurrence(spec, rule, event.records)
        if fresh.knowable_at is not None and fresh.deciding_record_id is not None \
                and (earliest is None or fresh.knowable_at < earliest[0]):
            earliest = fresh.knowable_at, fresh.deciding_record_id
        if earliest is not None and stored.knowable_at is not None and earliest[0] < stored.knowable_at:
            self._ledger.append(KIND_KNOWABLE, _ledger_id("knowable", event_id, earliest[1]),
                                {"event_id": event_id, "knowable_at": timestamp_payload(earliest[0]),
                                 "record_id": earliest[1]})
            stored = replace(stored, knowable_at=earliest[0])
        known = {(i.kind, i.reference_id) for i in stored.incidents}
        # A receipt lag is a fact about a record, whatever decided the member. An incident about how the member was
        # decided (a late publication, an observer outage) belongs to the stored disposition only when the fresh
        # adjudication decided it the same way (issue #37, pass 4).
        same_decision = (fresh.disposition, fresh.deciding_record_id) == (stored.disposition, stored.deciding_record_id)
        for incident in fresh.incidents:
            if incident.kind != "receipt_lag" and not same_decision:
                continue
            if (incident.kind, incident.reference_id) not in known:
                self._ledger.append(KIND_INCIDENT, _ledger_id("incident", event_id, incident.kind, incident.reference_id),
                                    {"event_id": event_id, **incident.to_payload()})
                stored = replace(stored, incidents=stored.incidents + (incident,))
        return stored
