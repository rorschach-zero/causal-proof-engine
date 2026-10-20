"""The adjudication registry on the ledger: records in, immutable dispositions out, state by replay."""
from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime

from cpe.adjudication.records import AbsenceObservation, ResolutionRecord, SourceRule, SourceStatus
from cpe.adjudication.rules import (
    FINAL,
    Adjudication,
    Defect,
    Incident,
    ReceivedRecord,
    adjudicate,
    check_record_chronology,
    check_record_is_final_enough,
)
from cpe.canonical import digest_of
from cpe.clock import parse_timestamp
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

    def event(self, event_id: str) -> _EventState:
        return self.events.setdefault(event_id, _EventState())


def replay_state(records: tuple[Record, ...]) -> _State:
    state = _State()
    for record in records:
        state.head = record.entry_hash
        payload = record.payload
        assert isinstance(payload, dict)
        if record.kind == KIND_EVENT:
            spec = EventSpec.from_payload(payload)
            state.event(spec.event_id).spec = spec
        elif record.kind == KIND_RULE:
            rule = SourceRule.from_payload(payload)
            state.rules[rule.source_id] = rule
        elif record.kind == KIND_RECORD:
            resolution = ResolutionRecord.from_payload(payload)
            state.event(resolution.event_id).records.append(
                ReceivedRecord(resolution, parse_timestamp(record.receipt_time, "receipt_time")))
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
            event_id, defect_id, detail = payload["event_id"], payload["record_id"], payload["detail"]
            assert isinstance(event_id, str) and isinstance(defect_id, str) and isinstance(detail, str)
            event = state.event(event_id)
            event.defect_record_ids.add(defect_id)
            if event.disposition is not None and defect_id not in {d.record_id for d in event.disposition.defects}:
                event.disposition = replace(event.disposition,
                                            defects=event.disposition.defects + (Defect(defect_id, detail),))
        elif record.kind == KIND_INCIDENT:
            event_id = payload["event_id"]
            assert isinstance(event_id, str)
            incident = Incident.from_payload({k: v for k, v in payload.items() if k != "event_id"})
            event = state.event(event_id)
            if event.disposition is not None and (incident.kind, incident.reference_id) not in {
                    (i.kind, i.reference_id) for i in event.disposition.incidents}:
                event.disposition = replace(event.disposition, incidents=event.disposition.incidents + (incident,))
    return state


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
        with self._lock:
            state = self.state()
            existing = state.event(spec.event_id).spec
            if existing is not None:
                if existing != spec:
                    raise Refusal("event_immutable", f"{spec.event_id} is registered with other criteria")
                return
            if spec.predicate.source not in state.rules:
                raise Refusal("unknown_source", f"{spec.predicate.source} has no registered source rule (OD5)")
            if self._ledger.now() >= spec.issuance_open:
                raise Refusal("late_registration", f"{spec.event_id}: the criteria must be recorded before the "
                              "issuance window opens")
            self._ledger.append(KIND_EVENT, _ledger_id("event", spec.event_id), spec.to_payload())

    def _spec(self, state: _State, event_id: str) -> EventSpec:
        spec = state.event(event_id).spec
        if spec is None:
            raise Refusal("unknown_event", f"{event_id} has no registered specification")
        return spec

    def register_rule(self, rule: SourceRule) -> None:
        with self._lock:
            existing = self.state().rules.get(rule.source_id)
            if existing is not None:
                if existing != rule:
                    raise Refusal("rule_immutable", f"source {rule.source_id} already has a different rule")
                return
            self._ledger.append(KIND_RULE, _ledger_id("rule", rule.source_id), rule.to_payload())

    def submit_record(self, record: ResolutionRecord) -> Record:
        with self._lock:
            state = self.state()
            spec = self._spec(state, record.event_id)
            rule = state.rules.get(record.source_id)
            if rule is None:
                raise Refusal("unknown_source", f"{record.source_id} has no registered source rule (OD5)")
            check_record_is_final_enough(record, spec, rule)
            if rule.publishes_evidenced_times and record.evidenced_publication_time is None:
                raise Refusal("missing_publication_time", f"{record.record_id}: the source evidences publication times")
            check_record_chronology(ReceivedRecord(record, self._ledger.now()))
            return self._ledger.append(KIND_RECORD, _ledger_id("record", record.record_id), record.to_payload())

    def submit_observation(self, observation: AbsenceObservation) -> Record:
        with self._lock:
            state = self.state()
            spec = self._spec(state, observation.event_id)
            if observation.source_id != spec.predicate.source:
                raise Refusal("wrong_source", f"{observation.source_id} is not the resolution source of {spec.event_id}")
            if observation.source_id not in state.rules:
                raise Refusal("unknown_source", f"{observation.source_id} has no registered source rule (OD5)")
            if observation.observed_at > self._ledger.now():
                raise Refusal("evidence_after_receipt", f"{observation.observation_id}: observed after its receipt")
            return self._ledger.append(KIND_OBSERVATION, _ledger_id("observation", observation.observation_id),
                                       observation.to_payload())

    def declare_source_status(self, status: SourceStatus) -> Record:
        with self._lock:
            if status.source_id not in self.state().rules:
                raise Refusal("unknown_source", f"{status.source_id} has no registered source rule (OD5)")
            if status.declared_at > self._ledger.now():
                raise Refusal("evidence_after_receipt", f"{status.source_id}: status declared after its receipt")
            return self._ledger.append(KIND_STATUS, _ledger_id("status", status.source_id, status.declared_at.isoformat()),
                                       status.to_payload())

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
                statuses = [status for status, receipt in state.status.get(rule.source_id, [])
                            if receipt <= spec.logical_finality]
                fresh = adjudicate(spec, rule, event.records, event.observations, statuses, now,
                                   event.observation_receipts)
                if self.before_write is not None:
                    hook, self.before_write = self.before_write, None
                    hook()
                if event.disposition is not None:
                    stored = event.disposition
                    for defect in fresh.defects:
                        if defect.record_id not in event.defect_record_ids:
                            self._ledger.append(KIND_DEFECT, _ledger_id("defect", event_id, defect.record_id),
                                                {"event_id": event_id, "record_id": defect.record_id, "detail": defect.detail})
                            stored = replace(stored, defects=stored.defects + (defect,))
                    known = {(i.kind, i.reference_id) for i in stored.incidents}
                    for incident in fresh.incidents:
                        if (incident.kind, incident.reference_id) not in known:
                            self._ledger.append(KIND_INCIDENT, _ledger_id("incident", event_id, incident.kind, incident.reference_id),
                                                {"event_id": event_id, **incident.to_payload()})
                            stored = replace(stored, incidents=stored.incidents + (incident,))
                    return stored
                if fresh.disposition not in FINAL:
                    return fresh
                try:
                    self._ledger.append(KIND_DISPOSITION, _ledger_id("disposition", event_id), fresh.to_payload(),
                                        expected_head=state.head)
                except Refusal as refusal:
                    if refusal.reason != "stale_head":
                        raise
                    continue
                for defect in fresh.defects:
                    self._ledger.append(KIND_DEFECT, _ledger_id("defect", event_id, defect.record_id),
                                        {"event_id": event_id, "record_id": defect.record_id, "detail": defect.detail})
                for incident in fresh.incidents:
                    self._ledger.append(KIND_INCIDENT, _ledger_id("incident", event_id, incident.kind, incident.reference_id),
                                        {"event_id": event_id, **incident.to_payload()})
                return fresh
            raise Refusal("contended", f"{event_id}: the ledger kept advancing during adjudication")
