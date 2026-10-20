"""The adjudication registry on the ledger: records in, immutable dispositions out, state by replay."""
from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field, replace

from cpe.adjudication.records import AbsenceObservation, ResolutionRecord, SourceRule, SourceStatus
from cpe.adjudication.rules import (
    FINAL,
    Adjudication,
    Defect,
    ReceivedRecord,
    adjudicate,
    check_record_chronology,
    check_record_is_final_enough,
)
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


@dataclass
class _EventState:
    spec: EventSpec | None = None
    records: list[ReceivedRecord] = field(default_factory=list)
    observations: list[AbsenceObservation] = field(default_factory=list)
    disposition: Adjudication | None = None
    defect_record_ids: set[str] = field(default_factory=set)


@dataclass
class _State:
    head: str = ""
    rules: dict[str, SourceRule] = field(default_factory=dict)
    status: dict[str, SourceStatus] = field(default_factory=dict)
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
            state.event(observation.event_id).observations.append(observation)
        elif record.kind == KIND_STATUS:
            status = SourceStatus.from_payload(payload)
            state.status[status.source_id] = status
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
        """Pre-register the resolution criteria once; a different specification under the same id is refused."""
        with self._lock:
            existing = self.state().event(spec.event_id).spec
            if existing is not None:
                if existing != spec:
                    raise Refusal("event_immutable", f"{spec.event_id} is registered with other criteria")
                return
            self._ledger.append(KIND_EVENT, f"event:{spec.event_id}", spec.to_payload())

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
            self._ledger.append(KIND_RULE, f"rule:{rule.source_id}", rule.to_payload())

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
            return self._ledger.append(KIND_RECORD, f"record:{record.record_id}", record.to_payload())

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
            return self._ledger.append(KIND_OBSERVATION, f"observation:{observation.observation_id}", observation.to_payload())

    def declare_source_status(self, status: SourceStatus) -> Record:
        with self._lock:
            if status.source_id not in self.state().rules:
                raise Refusal("unknown_source", f"{status.source_id} has no registered source rule (OD5)")
            if status.declared_at > self._ledger.now():
                raise Refusal("evidence_after_receipt", f"{status.source_id}: status declared after its receipt")
            return self._ledger.append(KIND_STATUS, f"status:{status.source_id}:{status.declared_at.isoformat()}",
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
                fresh = adjudicate(spec, rule, event.records, event.observations, state.status.get(rule.source_id), now)
                if self.before_write is not None:
                    hook, self.before_write = self.before_write, None
                    hook()
                if event.disposition is not None:
                    stored = event.disposition
                    for defect in fresh.defects:
                        if defect.record_id not in event.defect_record_ids:
                            self._ledger.append(KIND_DEFECT, f"defect:{event_id}:{defect.record_id}",
                                                {"event_id": event_id, "record_id": defect.record_id, "detail": defect.detail})
                            stored = replace(stored, defects=stored.defects + (defect,))
                    return stored
                if fresh.disposition not in FINAL:
                    return fresh
                try:
                    self._ledger.append(KIND_DISPOSITION, f"disposition:{event_id}", fresh.to_payload(),
                                        expected_head=state.head)
                except Refusal as refusal:
                    if refusal.reason != "stale_head":
                        raise
                    continue
                for defect in fresh.defects:
                    self._ledger.append(KIND_DEFECT, f"defect:{event_id}:{defect.record_id}",
                                        {"event_id": event_id, "record_id": defect.record_id, "detail": defect.detail})
                for index, incident in enumerate(fresh.incidents):
                    self._ledger.append(KIND_INCIDENT, f"incident:{event_id}:{index}",
                                        {"event_id": event_id, **incident.to_payload()})
                return fresh
            raise Refusal("contended", f"{event_id}: the ledger kept advancing during adjudication")
