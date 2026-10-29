"""The point-in-time feature store and its as-of read interface (``17`` section 3 item 1, RC-79, RC-86; T-15).

Assumptions, each from ``17`` section 3 item 1 unless stated:
- A row is (entity, feature, value, ``observed_at``, ``available_at``, vintage id). ``observed_at`` is the period
  the value describes; ``available_at`` is when the value could first be read, as attested by the ingest, and is
  never after the ledger receipt of the row.
- The as-of reader is bound to one evidence cutoff t_cut, the forecast's (``EventSpec.evidence_cutoff``), and is the
  leakage control of ``AGENTS.md`` section 8: it never returns a row with ``available_at`` after t_cut. A request
  for a later as-of time, or for a row not available at t_cut, is refused deterministically.
- The read at t_cut returns, for every ``observed_at`` with at least one row available at or before t_cut, the row
  with the greatest such ``available_at`` (latest vintage, RC-86), with its vintage id; a typed empty series,
  distinct from a refusal, when no row is eligible.
- A row that is not available at t_cut and a row that does not exist are refused alike (reading of this
  component), so that a refusal does not reveal that a later vintage exists.
"""
from __future__ import annotations

import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType

from cpe.canonical import JsonValue, canonical_bytes, digest_of
from cpe.clock import format_timestamp, parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Ledger, Record
from cpe.schemas.common import (
    payload_of,
    Payload,
    require_identifier,
    require_json,
    require_keys,
    require_mapping,
    require_timestamp,
    timestamp_payload,
)
from cpe.schemas.event import EventSpec

KIND_ROW = "pit_row"

_ROW_KEYS = frozenset({"entity", "feature", "value", "observed_at", "available_at", "vintage_id"})


@dataclass(frozen=True)
class FeatureRow:
    """One vintage of one observation of one feature of one entity."""

    entity: str
    feature: str
    value: JsonValue
    observed_at: datetime
    available_at: datetime
    vintage_id: str

    @classmethod
    def from_payload(cls, payload: object) -> FeatureRow:
        mapping = require_mapping(payload, "FeatureRow")
        require_keys(mapping, "FeatureRow", _ROW_KEYS, frozenset())
        return cls(
            entity=require_identifier(mapping["entity"], "entity"),
            feature=require_identifier(mapping["feature"], "feature"),
            value=require_json(mapping["value"], "value"),
            observed_at=require_timestamp(mapping["observed_at"], "observed_at"),
            available_at=require_timestamp(mapping["available_at"], "available_at"),
            vintage_id=require_identifier(mapping["vintage_id"], "vintage_id"),
        )

    def to_payload(self) -> Payload:
        return {
            "entity": self.entity,
            "feature": self.feature,
            "value": self.value,
            "observed_at": timestamp_payload(self.observed_at),
            "available_at": timestamp_payload(self.available_at),
            "vintage_id": self.vintage_id,
        }


@dataclass(frozen=True)
class Vintage:
    """What an as-of read returns for one observation: the vintage id and its value."""

    vintage_id: str
    value: JsonValue


@dataclass(frozen=True)
class AsOfSeries:
    """The point-in-time series of one feature of one entity at a cutoff: observation time to latest vintage.
    An empty series is a result, not a refusal: nothing was available at the cutoff."""

    entity: str
    feature: str
    as_of: datetime
    observations: Mapping[datetime, Vintage]

    @property
    def empty(self) -> bool:
        return not self.observations


@dataclass
class _State:
    rows: dict[tuple[str, str, str], FeatureRow] = field(default_factory=dict)  # by (entity, feature, vintage id)


def _row_id(row: FeatureRow) -> str:
    return f"pit:{digest_of([row.entity, row.feature, row.vintage_id])}"


def _same(left: FeatureRow, right: FeatureRow) -> bool:
    """Identical persisted content: ``True`` and ``1``, or ``1`` and ``1.0``, are different values (4335189789)."""
    return canonical_bytes(left.to_payload()) == canonical_bytes(right.to_payload())


def replay_state(records: tuple[Record, ...]) -> _State:
    """The rows, each from the one record that carries its vintage under its canonical id; a second record of a
    vintage, or a row under another id, is refused rather than read as a rewrite (4335189761)."""
    state = _State()
    for record in records:
        if record.kind != KIND_ROW:
            continue  # another registry's record on the same ledger
        row = FeatureRow.from_payload(record.payload)
        if record.record_id != _row_id(row):
            raise Refusal("invalid_record_id", f"{record.record_id} is not the identifier of its vintage")
        if row.available_at > parse_timestamp(record.receipt_time, "receipt_time"):
            raise Refusal("evidence_after_receipt", f"{record.record_id}: available after its receipt")
        key = (row.entity, row.feature, row.vintage_id)
        if key in state.rows:
            raise Refusal("vintage_immutable", f"{record.record_id}: a second record of one vintage")
        state.rows[key] = row
    return state


class PointInTimeStore:
    """Feature rows on the ledger, one per (entity, feature, vintage id), immutable; state by replay only."""

    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger
        self._lock = threading.RLock()

    def _rows(self) -> tuple[FeatureRow, ...]:
        """Every vintage, without a cutoff: for the reader only, never public (4335189780)."""
        return tuple(replay_state(self._ledger.records()).rows.values())

    def ingest(self, row: FeatureRow) -> Record:
        """Append a row. A vintage is written once: the same row again returns the stored record, another row under
        the same (entity, feature, vintage id) is refused. ``available_at`` must not follow the receipt. Another
        writer on the same ledger that lands the vintage first is read back, not reported as a duplicate id
        (4335189771)."""
        row = FeatureRow.from_payload(payload_of(row))  # validated as replay will read it; never an untyped crash
        with self._lock:
            for attempt in range(2):
                existing = replay_state(self._ledger.records()).rows.get((row.entity, row.feature, row.vintage_id))
                if existing is not None:
                    if not _same(existing, row):
                        raise Refusal("vintage_immutable", f"{row.entity}/{row.feature} vintage {row.vintage_id} is "
                                      "already stored with other content")
                    return next(r for r in self._ledger.records() if r.record_id == _row_id(row))

                def admit(receipt: datetime) -> None:
                    if row.available_at > receipt:
                        raise Refusal("evidence_after_receipt", f"vintage {row.vintage_id} is available after its "
                                      "receipt")
                try:
                    return self._ledger.append(KIND_ROW, _row_id(row), row.to_payload(), admit=admit)
                except Refusal as refusal:
                    if refusal.reason != "duplicate_record_id" or attempt:
                        raise
            raise AssertionError("unreachable")

    def reader(self, evidence_cutoff: datetime) -> AsOfReader:
        return AsOfReader(self, evidence_cutoff)

    def reader_for(self, spec: EventSpec) -> AsOfReader:
        """The reader of a forecast on ``spec``: bound to the event's pre-registered evidence cutoff (RC-76)."""
        return AsOfReader(self, spec.evidence_cutoff)


class AsOfReader:
    """The only read interface of the store: every read is bounded by one evidence cutoff fixed at construction."""

    def __init__(self, store: PointInTimeStore, evidence_cutoff: datetime) -> None:
        self._store = store
        if not isinstance(evidence_cutoff, datetime):  # typed, never an AttributeError (issue #37, pass 5)
            raise Refusal("invalid_timestamp", "the evidence cutoff must be an aware datetime")
        self.evidence_cutoff = require_timestamp(timestamp_payload(evidence_cutoff), "evidence_cutoff")

    def _bounded(self, as_of: datetime | None) -> datetime:
        if as_of is None:
            return self.evidence_cutoff
        if not isinstance(as_of, datetime):
            raise Refusal("invalid_timestamp", "as_of must be an aware datetime (issue #37)")
        as_of = parse_timestamp(format_timestamp(as_of), "as_of")  # naive refused, UTC canonical (4335189800)
        if as_of > self.evidence_cutoff:
            raise Refusal("after_evidence_cutoff", f"as-of {timestamp_payload(as_of)} is after the evidence cutoff "
                          f"{timestamp_payload(self.evidence_cutoff)}")
        return as_of

    def series(self, entity: str, feature: str, as_of: datetime | None = None) -> AsOfSeries:
        """Per observation time, the vintage with the greatest ``available_at`` at or before the as-of time."""
        entity = require_identifier(entity, "entity")  # typed, never a TypeError (issue #37, pass 5)
        feature = require_identifier(feature, "feature")  # typed, never a TypeError (issue #37, pass 5)
        cut = self._bounded(as_of)
        latest: dict[datetime, FeatureRow] = {}
        for row in self._store._rows():
            if row.entity != entity or row.feature != feature or row.available_at > cut:
                continue
            held = latest.get(row.observed_at)
            if held is None or (row.available_at, row.vintage_id) > (held.available_at, held.vintage_id):
                latest[row.observed_at] = row
        observations = {observed: Vintage(row.vintage_id, row.value) for observed, row in sorted(latest.items())}
        return AsOfSeries(entity, feature, cut, MappingProxyType(observations))

    def row(self, entity: str, feature: str, vintage_id: str, as_of: datetime | None = None) -> FeatureRow:
        """One vintage, refused unless it was available at the as-of time; an unknown vintage is refused alike."""
        entity = require_identifier(entity, "entity")  # typed, never a TypeError (issue #37, pass 5)
        feature = require_identifier(feature, "feature")  # typed, never a TypeError (issue #37, pass 5)
        vintage_id = require_identifier(vintage_id, "vintage_id")  # typed, never a TypeError (issue #37, pass 5)
        cut = self._bounded(as_of)
        for row in self._store._rows():
            if (row.entity, row.feature, row.vintage_id) == (entity, feature, vintage_id) and row.available_at <= cut:
                return row
        raise Refusal("not_available", f"{entity}/{feature} vintage {vintage_id} is not available at "
                      f"{timestamp_payload(cut)}")
