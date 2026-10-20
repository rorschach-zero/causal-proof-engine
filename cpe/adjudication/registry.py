"""The adjudication registry on the ledger: records in, immutable dispositions out, state by replay."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from cpe.adjudication.records import AbsenceObservation, ResolutionRecord, SourceRule, SourceStatus
from cpe.adjudication.rules import FINAL, Adjudication, ReceivedRecord, adjudicate, check_record_is_final_enough
from cpe.clock import parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Ledger, Record
from cpe.schemas.event import EventSpec

KIND_RULE = "source_rule"
KIND_RECORD = "resolution_record"
KIND_OBSERVATION = "absence_observation"
KIND_STATUS = "source_status"
KIND_DISPOSITION = "disposition"
KIND_DEFECT = "source_latency_defect"
KIND_INCIDENT = "integrity_incident"


@dataclass
class _EventState:
    records: list[ReceivedRecord] = field(default_factory=list)
    observations: list[AbsenceObservation] = field(default_factory=list)
    disposition: Adjudication | None = None
    defect_record_ids: set[str] = field(default_factory=set)


@dataclass
class _State:
    rules: dict[str, SourceRule] = field(default_factory=dict)
    status: dict[str, SourceStatus] = field(default_factory=dict)
    events: dict[str, _EventState] = field(default_factory=dict)

    def event(self, event_id: str) -> _EventState:
        return self.events.setdefault(event_id, _EventState())


def replay_state(records: tuple[Record, ...]) -> _State:
    state = _State()
    for record in records:
        payload = record.payload
        assert isinstance(payload, dict)
        if record.kind == KIND_RULE:
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
            event_id, defect_id = payload["event_id"], payload["record_id"]
            assert isinstance(event_id, str) and isinstance(defect_id, str)
            state.event(event_id).defect_record_ids.add(defect_id)
    return state


class AdjudicationRegistry:
    """Writes source rules, records, observations and dispositions to the ledger; reads its state by replay only."""

    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger

    def state(self) -> _State:
        return replay_state(self._ledger.records())

    def register_rule(self, rule: SourceRule) -> None:
        existing = self.state().rules.get(rule.source_id)
        if existing is not None:
            if existing != rule:
                raise Refusal("rule_immutable", f"source {rule.source_id} already has a different rule")
            return
        self._ledger.append(KIND_RULE, f"rule:{rule.source_id}", rule.to_payload())

    def submit_record(self, record: ResolutionRecord, spec: EventSpec) -> Record:
        if record.event_id != spec.event_id:
            raise Refusal("wrong_event", f"{record.record_id} does not concern {spec.event_id}")
        rule = self.state().rules.get(record.source_id)
        if rule is None:
            raise Refusal("unknown_source", f"{record.source_id} has no registered source rule (OD5)")
        check_record_is_final_enough(record, spec, rule)
        if rule.publishes_evidenced_times and record.evidenced_publication_time is None:
            raise Refusal("missing_publication_time", f"{record.record_id}: the source evidences publication times")
        return self._ledger.append(KIND_RECORD, f"record:{record.record_id}", record.to_payload())

    def submit_observation(self, observation: AbsenceObservation) -> Record:
        if observation.source_id not in self.state().rules:
            raise Refusal("unknown_source", f"{observation.source_id} has no registered source rule (OD5)")
        return self._ledger.append(KIND_OBSERVATION, f"observation:{observation.observation_id}", observation.to_payload())

    def declare_source_status(self, status: SourceStatus) -> Record:
        if status.source_id not in self.state().rules:
            raise Refusal("unknown_source", f"{status.source_id} has no registered source rule (OD5)")
        return self._ledger.append(KIND_STATUS, f"status:{status.source_id}:{status.declared_at.isoformat()}",
                                   status.to_payload())

    def adjudicate(self, spec: EventSpec, now: datetime) -> Adjudication:
        """Adjudicate the event at ``now``. A final disposition is written once and never rewritten; a record
        that arrives after it can only add a source-latency defect (RC-88)."""
        state = self.state()
        rule = state.rules.get(spec.predicate.source)
        if rule is None:
            raise Refusal("unknown_source", f"{spec.predicate.source} has no registered source rule (OD5)")
        event = state.event(spec.event_id)
        fresh = adjudicate(spec, rule, event.records, event.observations, state.status.get(rule.source_id), now)
        if event.disposition is not None:
            stored = event.disposition
            for defect in fresh.defects:
                if defect.record_id not in event.defect_record_ids:
                    self._ledger.append(KIND_DEFECT, f"defect:{spec.event_id}:{defect.record_id}",
                                        {"event_id": spec.event_id, "record_id": defect.record_id, "detail": defect.detail})
            return stored
        if fresh.disposition in FINAL:
            self._ledger.append(KIND_DISPOSITION, f"disposition:{spec.event_id}", fresh.to_payload())
            for defect in fresh.defects:
                self._ledger.append(KIND_DEFECT, f"defect:{spec.event_id}:{defect.record_id}",
                                    {"event_id": spec.event_id, "record_id": defect.record_id, "detail": defect.detail})
            for index, incident in enumerate(fresh.incidents):
                self._ledger.append(KIND_INCIDENT, f"incident:{spec.event_id}:{index}",
                                    {"event_id": spec.event_id, **incident.to_payload()})
        return fresh
