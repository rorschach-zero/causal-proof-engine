"""Resolution rules: from source records and observations to a disposition with its ``knowable_at``.

Pure functions over schema objects. Assumptions, each from ``17`` section 3 item 1:
- Logical finality F = deadline + latency window is the latest time an outcome can be determinable (RC-77).
- A timely record is one whose evidenced publication time is at or before F; for a source that evidences no
  publication times, the observer's read time stands in and the source cannot evidence absence (RC-113).
- YES needs evidence that the occurrence met the deadline; a reported occurrence with no occurrence time and no
  evidence of lateness is VOID (outcome-dependent, counted against the cap); EXPIRED_NO needs evidence of lateness
  or of definitive non-occurrence (RC-71, F-02a, F-02b).
- On a terminal-falsifier predicate the falsifier's publication is the NO, and absence of a falsifier at finality
  is the YES; on a milestone-deadline predicate absence at finality is the NO (``17`` A-member "on a
  terminal-falsifier predicate a breach is a NO").
- Absence at finality is evidenced by an archived read at or after F showing no record, or, under the
  monotone-publication condition, by the earliest matching record published after F (RC-113). With neither, the
  member stays OPEN; under the source's failure condition it is VOID.
- What a record claims is derived from its archived content by the registered predicate, never taken from the
  caller: a record whose content is not the one it names, whose content holds no evidence, or whose stated claim
  disagrees with the evaluation is refused (PR #18 finding 4329664953).
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast

from cpe.adjudication.content import ArchivedContent
from cpe.adjudication.predicate import evaluate
from cpe.adjudication.records import AbsenceObservation, Claim, ResolutionRecord, SourceRule, SourceStatus
from cpe.errors import Refusal
from cpe.schemas.common import Payload, optional_timestamp, require_identifier, require_keys, require_mapping, timestamp_payload
from cpe.schemas.event import EventSpec, ResolutionTimestamps

Disposition = Literal["OPEN", "RESOLVED_YES", "RESOLVED_NO", "EXPIRED_NO", "VOID"]
FINAL: frozenset[str] = frozenset({"RESOLVED_YES", "RESOLVED_NO", "EXPIRED_NO", "VOID"})
IncidentKind = Literal["receipt_lag", "observer_outage", "late_publication"]
INCIDENT_KINDS: tuple[str, ...] = ("receipt_lag", "observer_outage", "late_publication")


@dataclass(frozen=True)
class ReceivedRecord:
    """A source record with the registry's server receipt time and the archived content it names."""

    record: ResolutionRecord
    receipt: datetime
    content: ArchivedContent

    def claim(self, spec: EventSpec) -> Claim:
        """The claim the archived content supports under the event's registered predicate."""
        return check_record_content(self, spec)

    def publication(self, rule: SourceRule) -> datetime:
        """The evidenced publication time, or the observer's read time for a source that evidences none."""
        if rule.publishes_evidenced_times:
            if self.record.evidenced_publication_time is None:
                raise Refusal("missing_publication_time", f"{self.record.record_id}: the source rule promises "
                              "evidenced publication times")
            return self.record.evidenced_publication_time
        return self.record.first_observed_at

    def knowable(self, rule: SourceRule) -> datetime:
        """The earliest time this record made the outcome publicly determinable: its publication, or the
        occurrence time when the occurrence is itself a public act (RC-52, RC-146)."""
        published = self.publication(rule)
        occurrence = self.record.occurrence_time
        if rule.occurrence_is_public_act and occurrence is not None:
            return min(published, occurrence)
        return published


@dataclass(frozen=True)
class Defect:
    record_id: str
    detail: str

    def to_payload(self) -> Payload:
        return {"record_id": self.record_id, "detail": self.detail}

    @classmethod
    def from_payload(cls, payload: object) -> Defect:
        mapping = require_mapping(payload, "Defect")
        require_keys(mapping, "Defect", frozenset({"record_id", "detail"}), frozenset())
        return cls(require_identifier(mapping["record_id"], "record_id"), str(mapping["detail"]))


@dataclass(frozen=True)
class Incident:
    kind: IncidentKind
    reference_id: str
    detail: str

    def to_payload(self) -> Payload:
        return {"kind": self.kind, "reference_id": self.reference_id, "detail": self.detail}

    @classmethod
    def from_payload(cls, payload: object) -> Incident:
        mapping = require_mapping(payload, "Incident")
        require_keys(mapping, "Incident", frozenset({"kind", "reference_id", "detail"}), frozenset())
        kind = mapping["kind"]
        if kind not in INCIDENT_KINDS:
            raise Refusal("invalid_choice", f"incident kind must be one of {', '.join(INCIDENT_KINDS)}")
        return cls(cast(IncidentKind, kind),
                   require_identifier(mapping["reference_id"], "reference_id"), str(mapping["detail"]))


@dataclass(frozen=True)
class Adjudication:
    event_id: str
    disposition: Disposition
    knowable_at: datetime | None
    adjudicated_at: datetime | None
    basis: str
    timestamps: ResolutionTimestamps | None
    deciding_record_id: str | None = None
    defects: tuple[Defect, ...] = ()
    incidents: tuple[Incident, ...] = ()

    @property
    def final(self) -> bool:
        return self.disposition in FINAL

    def to_payload(self) -> Payload:
        return {
            "event_id": self.event_id,
            "disposition": self.disposition,
            "knowable_at": timestamp_payload(self.knowable_at),
            "adjudicated_at": timestamp_payload(self.adjudicated_at),
            "basis": self.basis,
            "timestamps": None if self.timestamps is None else self.timestamps.to_payload(),
            "deciding_record_id": self.deciding_record_id,
            "defects": [d.to_payload() for d in self.defects],
            "incidents": [i.to_payload() for i in self.incidents],
        }

    @classmethod
    def from_payload(cls, payload: object) -> Adjudication:
        mapping = require_mapping(payload, "Adjudication")
        require_keys(mapping, "Adjudication", frozenset({
            "event_id", "disposition", "knowable_at", "adjudicated_at", "basis", "timestamps", "deciding_record_id",
            "defects", "incidents"}), frozenset())
        disposition = mapping["disposition"]
        if disposition not in ("OPEN", *FINAL):
            raise Refusal("invalid_choice", "unknown disposition")
        deciding = mapping["deciding_record_id"]
        defects, incidents = mapping["defects"], mapping["incidents"]
        if not isinstance(defects, list) or not isinstance(incidents, list):
            raise Refusal("invalid_list", "defects and incidents are lists")
        return cls(
            event_id=require_identifier(mapping["event_id"], "event_id"),
            disposition=cast(Disposition, disposition),
            knowable_at=optional_timestamp(mapping["knowable_at"], "knowable_at"),
            adjudicated_at=optional_timestamp(mapping["adjudicated_at"], "adjudicated_at"),
            basis=str(mapping["basis"]),
            timestamps=None if mapping["timestamps"] is None else ResolutionTimestamps.from_payload(mapping["timestamps"]),
            deciding_record_id=None if deciding is None else require_identifier(deciding, "deciding_record_id"),
            defects=tuple(Defect.from_payload(d) for d in defects),
            incidents=tuple(Incident.from_payload(i) for i in incidents),
        )


def check_record_is_final_enough(record: ResolutionRecord, spec: EventSpec, rule: SourceRule) -> None:
    """Refuse a NO before the deadline on an eventually-by-deadline predicate (F-03, T-04): it is not final."""
    if record.source_id != spec.predicate.source:
        raise Refusal("wrong_source", f"{record.record_id} is from {record.source_id}, the event resolves by "
                      f"{spec.predicate.source}")
    if spec.predicate_kind == "milestone-deadline" and record.claim == "not-occurred" and not record.definitive:
        published = record.evidenced_publication_time if rule.publishes_evidenced_times else record.first_observed_at
        if published is not None and published < spec.deadline:
            raise Refusal("not_final", f"{record.record_id}: a NO before the deadline is not logically final")


def check_record_content(received: ReceivedRecord, spec: EventSpec) -> Claim:
    """Evaluate the registered predicate over the record's archived content and return the claim it supports.

    Refused: content other than the one the record names, content of another source, content holding no evidence
    (a selector or field that matches nothing is not a NO), and a stated claim the evaluation contradicts."""
    record, content = received.record, received.content
    if content.sha256 != record.content_digest:
        raise Refusal("content_mismatch", f"{record.record_id} names content {record.content_digest}, not "
                      f"{content.sha256}")
    if content.source_id != record.source_id:
        raise Refusal("wrong_source", f"{record.record_id}: the content is from {content.source_id}")
    evaluated = evaluate(spec.predicate, content)
    if evaluated is None:
        raise Refusal("no_evidence", f"{record.record_id}: the archived content matches no record and field of the "
                      "registered predicate")
    if evaluated != record.claim:
        raise Refusal("claim_disagrees", f"{record.record_id} states {record.claim!r}, the archived content "
                      f"evaluates to {evaluated!r}")
    return evaluated


def check_record_chronology(received: ReceivedRecord) -> None:
    """Evidence cannot postdate the trusted receipt of the record that carries it."""
    record = received.record
    if record.first_observed_at > received.receipt:
        raise Refusal("evidence_after_receipt", f"{record.record_id}: observed after its receipt")
    if record.evidenced_publication_time is not None and record.evidenced_publication_time > received.receipt:
        raise Refusal("evidence_after_receipt", f"{record.record_id}: published after its receipt")
    if record.occurrence_time is not None and record.occurrence_time > received.receipt:
        raise Refusal("evidence_after_receipt", f"{record.record_id}: occurred after its receipt")
    published = record.evidenced_publication_time
    if published is not None and published > record.first_observed_at:
        raise Refusal("evidence_order", f"{record.record_id}: observed before its evidenced publication")
    if record.occurrence_time is not None:
        if published is not None and record.occurrence_time > published:
            raise Refusal("evidence_order", f"{record.record_id}: published before its occurrence")
        if record.occurrence_time > record.first_observed_at:
            raise Refusal("evidence_order", f"{record.record_id}: observed before its occurrence")


def _lower_bound(spec: EventSpec) -> datetime:
    """The earliest occurrence the registered predicate covers: ``not_before`` on a milestone predicate, the
    earliest-knowable bound (``falsifier_observable_from`` at the earliest) on a terminal-falsifier predicate."""
    return spec.predicate.not_before if spec.predicate_kind == "milestone-deadline" else spec.earliest_knowable_bound


def _decide(received: ReceivedRecord, spec: EventSpec, rule: SourceRule) -> tuple[Disposition, datetime, str] | None:
    """What a timely record decides, with the knowable time it gives and the basis; None if it decides nothing.

    An occurrence before the predicate's lower bound is outside the registered predicate and decides nothing."""
    record = received.record
    published = received.publication(rule)
    occurrence = record.occurrence_time
    knowable = received.knowable(rule)
    if occurrence is not None and occurrence < _lower_bound(spec):
        return None
    claim = received.claim(spec)
    if spec.predicate_kind == "milestone-deadline":
        if claim == "occurred":
            if occurrence is not None:
                if occurrence <= spec.deadline:
                    return "RESOLVED_YES", knowable, "timely occurrence evidenced"
                return "EXPIRED_NO", knowable, "occurrence after the deadline"
            if record.lateness_evidence:
                return "EXPIRED_NO", published, "lateness evidenced without an occurrence time"
            return "VOID", published, "occurrence reported with no occurrence time and no evidence of lateness (RC-71)"
        if record.definitive:
            return "EXPIRED_NO", published, "definitive non-occurrence evidenced"
        return None
    if claim != "occurred":
        return None
    if occurrence is None:
        if record.lateness_evidence:
            return None  # a falsifier evidenced as after the deadline falsifies nothing
        return "VOID", published, "falsifier reported with no occurrence time and no evidence of lateness (RC-71)"
    if occurrence <= spec.deadline:
        return "RESOLVED_NO", knowable, "terminal falsifier published"
    return None


def _contradicts(received: ReceivedRecord, spec: EventSpec, disposition: Disposition) -> bool:
    """A late report of a timely occurrence contradicts a final NO, EXPIRED_NO or VOID on a milestone predicate,
    and a late timely falsifier contradicts a final YES on a terminal-falsifier predicate."""
    record = received.record
    if received.claim(spec) != "occurred":
        return False
    occurrence = record.occurrence_time
    if occurrence is None:
        timely = not record.lateness_evidence
    else:
        timely = _lower_bound(spec) <= occurrence <= spec.deadline
    if spec.predicate_kind == "milestone-deadline":
        return timely and disposition != "RESOLVED_YES"
    return timely and disposition == "RESOLVED_YES"


def adjudicate(spec: EventSpec, rule: SourceRule, records: Sequence[ReceivedRecord],
               observations: Sequence[AbsenceObservation], statuses: Sequence[SourceStatus], now: datetime,
               observation_receipts: Mapping[str, datetime] | None = None,
               status_receipts: Mapping[SourceStatus, datetime] | None = None) -> Adjudication:
    """Adjudicate one event at ``now`` from what the registry holds. Deterministic in its inputs.

    ``statuses`` is the declared status history of the source as the registry held it by finality; the
    declaration in force at logical finality decides whether the failure condition holds (RC-88: a later
    declaration changes nothing). ``observation_receipts`` gives the registry receipt of each observation by id,
    so that an absence-based disposition records when its deciding evidence entered the registry, and
    ``status_receipts`` does the same for each status, so that a status-decided VOID records the status's receipt.
    Each receipt lies at or after the time it evidences and at or before ``now``.

    ``knowable_at`` is the earliest of the deciding evidence's knowable time and the occurrence time of any record
    of a public act within the predicate's bounds, timely or late (RC-146 read with RC-88, decided 2026-10-21 on
    4330044547): the publication partition decides the disposition, which stays immutable, while a public
    occurrence makes the outcome determinable whenever its record is published."""
    receipts = observation_receipts or {}
    held_statuses = status_receipts or {}
    for observation in observations:
        receipt = receipts.get(observation.observation_id)
        if receipt is not None:
            if receipt < observation.observed_at:
                raise Refusal("evidence_after_receipt", f"observation {observation.observation_id} received before it was made")
            if receipt > now:
                raise Refusal("receipt_after_now", f"observation {observation.observation_id} is received after the adjudication time")
    for status, receipt in held_statuses.items():
        if receipt < status.declared_at or receipt > now:
            raise Refusal("evidence_after_receipt" if receipt < status.declared_at else "receipt_after_now",
                          f"the status of {status.source_id} declared at {timestamp_payload(status.declared_at)}")
    if rule.source_id != spec.predicate.source:
        raise Refusal("wrong_source", "the rule does not belong to the event's resolution source")
    finality = spec.logical_finality
    for received in records:
        if received.record.event_id != spec.event_id:
            raise Refusal("wrong_event", f"{received.record.record_id} concerns {received.record.event_id}")
        check_record_content(received, spec)
        check_record_is_final_enough(received.record, spec, rule)
        check_record_chronology(received)
        if received.receipt > now:
            raise Refusal("receipt_after_now", f"{received.record.record_id} is received after the adjudication time")
    for observation in observations:
        if observation.event_id != spec.event_id or observation.source_id != rule.source_id:
            raise Refusal("wrong_source", f"observation {observation.observation_id} is not of this event's source")
    for status in statuses:
        if status.source_id != rule.source_id:
            raise Refusal("wrong_source", f"the status of {status.source_id} is not of this event's source")
    in_force = [s for s in statuses if s.declared_at <= finality]
    status_at_finality = max(in_force, key=lambda s: s.declared_at) if in_force else None
    # Timeliness is the source's publication inside the latency window (RC-105); the knowable time, which on a
    # public act may be earlier, only stamps the result.
    ordered = sorted(records, key=lambda r: (r.publication(rule), r.record.record_id))
    timely = [r for r in ordered if r.publication(rule) <= finality]
    late = [r for r in ordered if r.publication(rule) > finality]

    disposition: Disposition = "OPEN"
    knowable: datetime | None = None
    basis = "no decisive record"
    evidence_receipt = now  # the receipt of the deciding evidence; the adjudication time when none decides
    deciding: ReceivedRecord | None = None
    incidents: list[Incident] = []
    decided = [(decision, received) for received in timely if (decision := _decide(received, spec, rule)) is not None]
    if decided:  # among timely deciding records, the one that made the outcome determinable first (RC-146)
        (disposition, knowable, basis), deciding = min(
            decided, key=lambda d: (d[0][1], d[1].publication(rule), d[1].record.record_id))

    if deciding is not None:
        if deciding.receipt > finality or deciding.record.first_observed_at > finality:
            incidents.append(Incident("receipt_lag", deciding.record.record_id,
                                      "record published inside the window and received after it (RC-105)"))
    elif now >= finality:
        absence_at: datetime | None = None
        absence_basis = ""
        reads = sorted((o.observed_at, o.observation_id) for o in observations if finality <= o.observed_at <= now)
        if reads:
            absence_at, absence_basis = reads[0][0], "archived observation of absence at or after finality"
            evidence_receipt = receipts.get(reads[0][1], now)
        elif rule.monotone_publication and late:
            first_late = late[0]
            absence_at = first_late.record.first_observed_at
            absence_basis = (f"earliest matching record {first_late.record.record_id} published after finality "
                             "under the monotone-publication condition (RC-113)")
            evidence_receipt = first_late.receipt
        # Before any disposition, a record published after finality that proves expiry on its content (an
        # occurrence after the deadline, or definitive non-occurrence) still decides; its late publication is an
        # incident. A late report of a timely occurrence proves nothing on its own.
        late_expiry: tuple[ReceivedRecord, tuple[Disposition, datetime, str]] | None = None
        if absence_at is None:
            for received in late:
                decision = _decide(received, spec, rule)
                if decision is not None and decision[0] == "EXPIRED_NO":
                    late_expiry = received, decision
                    break
        if status_at_finality is not None and status_at_finality.failed:
            disposition, knowable, basis = "VOID", finality, "source rule failure condition met"
            evidence_receipt = held_statuses.get(status_at_finality, now)
        elif absence_at is not None:
            disposition = "RESOLVED_NO" if spec.predicate_kind == "milestone-deadline" else "RESOLVED_YES"
            knowable, basis = finality, absence_basis
            if absence_at > finality:
                incidents.append(Incident("observer_outage", spec.event_id,
                                          f"the source was first read at {timestamp_payload(absence_at)}, after finality"))
        elif late_expiry is not None:
            deciding, (disposition, knowable, basis) = late_expiry
            incidents.append(Incident("late_publication", deciding.record.record_id,
                                      "expiry evidenced by a record published after finality (RC-105), adjudicated on "
                                      "its content before any disposition"))
        elif not rule.publishes_evidenced_times:
            disposition, knowable, basis = "VOID", finality, (
                "the source cannot evidence absence at finality and no observation exists (RC-113)")

    defects: list[Defect] = []
    if disposition in FINAL:
        for received in late:
            if _contradicts(received, spec, disposition):
                defects.append(Defect(received.record.record_id, "report of timely occurrence published after "
                                                                 "finality; the disposition stands (RC-88)"))

    if disposition not in FINAL:
        return Adjudication(spec.event_id, "OPEN", None, None, basis, None)
    assert knowable is not None
    if rule.occurrence_is_public_act:
        public = [r.record.occurrence_time for r in records
                  if r.claim(spec) == "occurred" and r.record.occurrence_time is not None
                  and r.record.occurrence_time >= _lower_bound(spec)]
        knowable = min([knowable, *[t for t in public if t is not None]])
    timestamps = ResolutionTimestamps(
        receipt=deciding.receipt if deciding is not None else evidence_receipt,
        occurrence=deciding.record.occurrence_time if deciding is not None else None,
        publication=deciding.publication(rule) if deciding is not None else None,
        adjudication=now,
    )
    return Adjudication(spec.event_id, disposition, knowable, now, basis, timestamps,
                        deciding.record.record_id if deciding is not None else None, tuple(defects), tuple(incidents))
