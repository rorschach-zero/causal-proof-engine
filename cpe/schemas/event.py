"""Event specification, cluster registration record and the four resolution timestamps (``17`` section 3 item 1).

Assumptions stated with the schema:
- A predicate is typed (source, record selector, field, comparator, value, not-before, not-after); free text is not
  a predicate and is refused (fixture F-19, probe P3).
- ``cluster_id`` is mandatory; a singleton is declared explicitly as a cluster with one member (RC-53).
- The earliest-knowable bound e_i is ``not_before`` for a milestone-deadline predicate and the minimum of
  ``not_before`` and ``falsifier_observable_from`` for a terminal-falsifier predicate; it is fixed at registration and
  depends on no outcome (RC-138).
- The issuance window closes at or before e_i, because issuance closes before any outcome can be knowable; the
  evidence cutoff lies inside the window (RC-76, RC-163).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, cast, get_args

from cpe.canonical import JsonValue
from cpe.errors import Refusal
from cpe.schemas.common import (
    Payload,
    optional_timestamp,
    require_identifier,
    require_identifier_tuple,
    require_json,
    require_keys,
    require_mapping,
    require_non_negative_int,
    require_timestamp,
    timestamp_payload,
)

PredicateKind = Literal["milestone-deadline", "terminal-falsifier"]
Comparator = Literal["eq", "ne", "lt", "le", "gt", "ge", "in"]

_PREDICATE_KEYS = frozenset({"source", "record_selector", "field", "comparator", "value", "not_before", "not_after"})


def _require_choice(value: object, field: str, allowed: tuple[str, ...]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise Refusal("invalid_choice", f"{field} must be one of {', '.join(allowed)}")
    return value


def require_predicate_kind(value: object, field: str = "predicate_kind") -> PredicateKind:
    return cast(PredicateKind, _require_choice(value, field, get_args(PredicateKind)))


def require_comparator(value: object, field: str = "comparator") -> Comparator:
    return cast(Comparator, _require_choice(value, field, get_args(Comparator)))


@dataclass(frozen=True)
class ResolutionPredicate:
    """What record of which source resolves the event, and the window in which the outcome can occur."""

    source: str
    record_selector: str
    field: str
    comparator: Comparator
    value: JsonValue
    not_before: datetime
    not_after: datetime

    def __post_init__(self) -> None:
        if self.not_before >= self.not_after:
            raise Refusal("invalid_window", "not_before must precede not_after")
        if self.comparator == "in":
            if not isinstance(self.value, list) or not self.value:
                raise Refusal("invalid_predicate_value", "comparator 'in' needs a non-empty list")
        elif isinstance(self.value, (list, dict)):
            raise Refusal("invalid_predicate_value", f"comparator {self.comparator!r} needs a scalar value")

    @classmethod
    def from_payload(cls, payload: object) -> ResolutionPredicate:
        mapping = require_mapping(payload, "ResolutionPredicate")
        require_keys(mapping, "ResolutionPredicate", _PREDICATE_KEYS, frozenset())
        value = require_json(mapping["value"], "value")
        if isinstance(value, dict):
            raise Refusal("invalid_predicate_value", "value must be a scalar or a list")
        return cls(
            source=require_identifier(mapping["source"], "source"),
            record_selector=require_identifier(mapping["record_selector"], "record_selector"),
            field=require_identifier(mapping["field"], "field"),
            comparator=require_comparator(mapping["comparator"]),
            value=value,
            not_before=require_timestamp(mapping["not_before"], "not_before"),
            not_after=require_timestamp(mapping["not_after"], "not_after"),
        )

    def to_payload(self) -> Payload:
        return {
            "source": self.source,
            "record_selector": self.record_selector,
            "field": self.field,
            "comparator": self.comparator,
            "value": self.value,
            "not_before": timestamp_payload(self.not_before),
            "not_after": timestamp_payload(self.not_after),
        }


_EVENT_REQUIRED = frozenset({
    "event_id", "cluster_id", "predicate_kind", "predicate", "latency_window_seconds", "issuance_open",
    "issuance_close", "evidence_cutoff", "reference_class_id",
})
_EVENT_OPTIONAL = frozenset({"falsifier_observable_from", "scoring_slots", "primary_slot"})
DEFAULT_SLOT = "primary"


@dataclass(frozen=True)
class EventSpec:
    """A registered event: typed predicate, cluster, timing fields and scoring slots."""

    event_id: str
    cluster_id: str
    predicate_kind: PredicateKind
    predicate: ResolutionPredicate
    latency_window_seconds: int
    issuance_open: datetime
    issuance_close: datetime
    evidence_cutoff: datetime
    reference_class_id: str
    falsifier_observable_from: datetime | None = None
    scoring_slots: tuple[str, ...] = (DEFAULT_SLOT,)
    primary_slot: str = DEFAULT_SLOT

    def __post_init__(self) -> None:
        if self.predicate_kind == "terminal-falsifier" and self.falsifier_observable_from is None:
            raise Refusal("missing_field", "a terminal-falsifier predicate declares falsifier_observable_from (OD5)")
        if self.predicate_kind == "milestone-deadline" and self.falsifier_observable_from is not None:
            raise Refusal("unknown_field", "falsifier_observable_from belongs to a terminal-falsifier predicate only")
        if not self.scoring_slots or len(set(self.scoring_slots)) != len(self.scoring_slots):
            raise Refusal("invalid_slots", "scoring_slots must be a non-empty list of distinct slot ids")
        if self.primary_slot not in self.scoring_slots:
            raise Refusal("invalid_slots", "primary_slot must name one of the scoring slots (RC-76)")
        if not self.issuance_open <= self.evidence_cutoff <= self.issuance_close:
            raise Refusal("invalid_window", "issuance_open <= evidence_cutoff <= issuance_close is required (RC-76)")
        if self.issuance_close > self.earliest_knowable_bound:
            raise Refusal("invalid_window", "issuance closes at or before the earliest-knowable bound (RC-163)")
        try:
            self.deadline + timedelta(seconds=self.latency_window_seconds)
        except (OverflowError, ValueError):
            raise Refusal("invalid_window", "the latency window puts logical finality beyond any representable "
                          "time") from None

    @property
    def deadline(self) -> datetime:
        return self.predicate.not_after

    @property
    def logical_finality(self) -> datetime:
        """deadline + latency window: the latest time at which the outcome is publicly determinable (RC-77)."""
        return self.deadline + timedelta(seconds=self.latency_window_seconds)

    @property
    def earliest_knowable_bound(self) -> datetime:
        """e_i of RC-138."""
        if self.falsifier_observable_from is None:
            return self.predicate.not_before
        return min(self.predicate.not_before, self.falsifier_observable_from)

    @classmethod
    def from_payload(cls, payload: object) -> EventSpec:
        mapping = require_mapping(payload, "EventSpec")
        require_keys(mapping, "EventSpec", _EVENT_REQUIRED, _EVENT_OPTIONAL)
        slots_raw = mapping.get("scoring_slots", [DEFAULT_SLOT])
        slots = require_identifier_tuple(slots_raw, "scoring_slots", allow_empty=False)
        primary = mapping.get("primary_slot", slots[0] if len(slots) == 1 else None)
        if primary is None:
            raise Refusal("missing_field", "an EventSpec with several slots names its primary_slot (RC-76)")
        return cls(
            event_id=require_identifier(mapping["event_id"], "event_id"),
            cluster_id=require_identifier(mapping["cluster_id"], "cluster_id"),
            predicate_kind=require_predicate_kind(mapping["predicate_kind"]),
            predicate=ResolutionPredicate.from_payload(mapping["predicate"]),
            latency_window_seconds=require_non_negative_int(mapping["latency_window_seconds"], "latency_window_seconds"),
            issuance_open=require_timestamp(mapping["issuance_open"], "issuance_open"),
            issuance_close=require_timestamp(mapping["issuance_close"], "issuance_close"),
            evidence_cutoff=require_timestamp(mapping["evidence_cutoff"], "evidence_cutoff"),
            reference_class_id=require_identifier(mapping["reference_class_id"], "reference_class_id"),
            falsifier_observable_from=optional_timestamp(mapping.get("falsifier_observable_from"),
                                                         "falsifier_observable_from"),
            scoring_slots=slots,
            primary_slot=require_identifier(primary, "primary_slot"),
        )

    def to_payload(self) -> Payload:
        payload: Payload = {
            "event_id": self.event_id,
            "cluster_id": self.cluster_id,
            "predicate_kind": self.predicate_kind,
            "predicate": self.predicate.to_payload(),
            "latency_window_seconds": self.latency_window_seconds,
            "issuance_open": timestamp_payload(self.issuance_open),
            "issuance_close": timestamp_payload(self.issuance_close),
            "evidence_cutoff": timestamp_payload(self.evidence_cutoff),
            "reference_class_id": self.reference_class_id,
            "scoring_slots": list(self.scoring_slots),
            "primary_slot": self.primary_slot,
        }
        if self.falsifier_observable_from is not None:
            payload["falsifier_observable_from"] = timestamp_payload(self.falsifier_observable_from)
        return payload


_TIMESTAMP_KEYS = frozenset({"occurrence", "publication", "receipt", "adjudication"})


@dataclass(frozen=True)
class ResolutionTimestamps:
    """The four timestamps of an outcome: occurrence, publication, receipt, adjudication.

    Receipt is the registry's server time and is always present; the others are evidenced or still unknown. The
    rules that derive ``knowable_at`` from them belong to the adjudication registry.
    """

    receipt: datetime
    occurrence: datetime | None = None
    publication: datetime | None = None
    adjudication: datetime | None = None

    @classmethod
    def from_payload(cls, payload: object) -> ResolutionTimestamps:
        mapping = require_mapping(payload, "ResolutionTimestamps")
        require_keys(mapping, "ResolutionTimestamps", frozenset({"receipt"}), _TIMESTAMP_KEYS - {"receipt"})
        return cls(
            receipt=require_timestamp(mapping["receipt"], "receipt"),
            occurrence=optional_timestamp(mapping.get("occurrence"), "occurrence"),
            publication=optional_timestamp(mapping.get("publication"), "publication"),
            adjudication=optional_timestamp(mapping.get("adjudication"), "adjudication"),
        )

    def to_payload(self) -> Payload:
        return {
            "receipt": timestamp_payload(self.receipt),
            "occurrence": timestamp_payload(self.occurrence),
            "publication": timestamp_payload(self.publication),
            "adjudication": timestamp_payload(self.adjudication),
        }


_CLUSTER_KEYS = frozenset({"cluster_id", "member_event_ids"})


@dataclass(frozen=True)
class ClusterRecord:
    """Registration record of an outcome cluster: its members, and which of them are pre-declared VOID (RC-85)."""

    cluster_id: str
    member_event_ids: tuple[str, ...]
    pre_declared_void: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not set(self.pre_declared_void) <= set(self.member_event_ids):
            raise Refusal("invalid_cluster", "pre_declared_void must name members of the cluster")

    @classmethod
    def from_payload(cls, payload: object) -> ClusterRecord:
        mapping = require_mapping(payload, "ClusterRecord")
        require_keys(mapping, "ClusterRecord", _CLUSTER_KEYS, frozenset({"pre_declared_void"}))
        return cls(
            cluster_id=require_identifier(mapping["cluster_id"], "cluster_id"),
            member_event_ids=require_identifier_tuple(mapping["member_event_ids"], "member_event_ids", allow_empty=False),
            pre_declared_void=require_identifier_tuple(mapping.get("pre_declared_void", []), "pre_declared_void",
                                                       allow_empty=True),
        )

    def to_payload(self) -> Payload:
        return {
            "cluster_id": self.cluster_id,
            "member_event_ids": list(self.member_event_ids),
            "pre_declared_void": list(self.pre_declared_void),
        }

