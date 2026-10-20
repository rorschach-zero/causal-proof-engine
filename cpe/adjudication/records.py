"""Records the adjudication reads: the source rule, source records, observations of absence and source status.

The source rule carries the OD5 fields as named values; nothing here chooses them. A source that cannot evidence
publication times cannot evidence absence (RC-113) and is an OD5 exclusion at registration.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast

from cpe.errors import Refusal
from cpe.schemas.common import (
    Payload,
    optional_timestamp,
    require_identifier,
    require_keys,
    require_mapping,
    require_timestamp,
    timestamp_payload,
)

Claim = Literal["occurred", "not-occurred"]

_RULE_KEYS = frozenset({"source_id", "occurrence_is_public_act", "publishes_evidenced_times", "monotone_publication"})


def _require_bool(value: object, field: str) -> bool:
    if not isinstance(value, bool):
        raise Refusal("invalid_flag", f"{field} must be true or false")
    return value


@dataclass(frozen=True)
class SourceRule:
    """Pre-registered rule of one resolution source (OD5 fields, named, not chosen here).

    - ``occurrence_is_public_act``: the occurrence time is itself a public determination (RC-52), so it enters
      ``knowable_at``; otherwise only the evidenced publication time does.
    - ``publishes_evidenced_times``: records carry evidenced publication times; without them the source cannot
      evidence absence at finality (RC-113).
    - ``monotone_publication``: the source publishes records with evidenced times and never removes one, so the
      earliest matching record published after finality is itself the observation of absence at finality (RC-113).
    """

    source_id: str
    occurrence_is_public_act: bool
    publishes_evidenced_times: bool
    monotone_publication: bool

    def __post_init__(self) -> None:
        if self.monotone_publication and not self.publishes_evidenced_times:
            raise Refusal("invalid_source_rule", "the monotone-publication condition needs evidenced publication times")

    @classmethod
    def from_payload(cls, payload: object) -> SourceRule:
        mapping = require_mapping(payload, "SourceRule")
        require_keys(mapping, "SourceRule", _RULE_KEYS, frozenset())
        return cls(
            source_id=require_identifier(mapping["source_id"], "source_id"),
            occurrence_is_public_act=_require_bool(mapping["occurrence_is_public_act"], "occurrence_is_public_act"),
            publishes_evidenced_times=_require_bool(mapping["publishes_evidenced_times"], "publishes_evidenced_times"),
            monotone_publication=_require_bool(mapping["monotone_publication"], "monotone_publication"),
        )

    def to_payload(self) -> Payload:
        return {
            "source_id": self.source_id,
            "occurrence_is_public_act": self.occurrence_is_public_act,
            "publishes_evidenced_times": self.publishes_evidenced_times,
            "monotone_publication": self.monotone_publication,
        }


_RECORD_REQUIRED = frozenset({"record_id", "event_id", "source_id", "claim", "first_observed_at"})
_RECORD_OPTIONAL = frozenset({"occurrence_time", "evidenced_publication_time", "lateness_evidence", "definitive"})


@dataclass(frozen=True)
class ResolutionRecord:
    """A record of the resolution source about the event, as the observer archived it.

    ``first_observed_at`` is the observer's read time (beside the evidenced publication time, RC-105);
    ``lateness_evidence`` says the record evidences that the occurrence was after the deadline, ``definitive``
    that the event had definitively not occurred by the deadline (RC-71). The registry adds the receipt time.
    """

    record_id: str
    event_id: str
    source_id: str
    claim: Claim
    first_observed_at: datetime
    occurrence_time: datetime | None = None
    evidenced_publication_time: datetime | None = None
    lateness_evidence: bool = False
    definitive: bool = False

    @classmethod
    def from_payload(cls, payload: object) -> ResolutionRecord:
        mapping = require_mapping(payload, "ResolutionRecord")
        require_keys(mapping, "ResolutionRecord", _RECORD_REQUIRED, _RECORD_OPTIONAL)
        claim = mapping["claim"]
        if claim not in ("occurred", "not-occurred"):
            raise Refusal("invalid_choice", "claim must be occurred or not-occurred")
        return cls(
            record_id=require_identifier(mapping["record_id"], "record_id"),
            event_id=require_identifier(mapping["event_id"], "event_id"),
            source_id=require_identifier(mapping["source_id"], "source_id"),
            claim=cast(Claim, claim),
            first_observed_at=require_timestamp(mapping["first_observed_at"], "first_observed_at"),
            occurrence_time=optional_timestamp(mapping.get("occurrence_time"), "occurrence_time"),
            evidenced_publication_time=optional_timestamp(mapping.get("evidenced_publication_time"),
                                                          "evidenced_publication_time"),
            lateness_evidence=_require_bool(mapping.get("lateness_evidence", False), "lateness_evidence"),
            definitive=_require_bool(mapping.get("definitive", False), "definitive"),
        )

    def to_payload(self) -> Payload:
        return {
            "record_id": self.record_id,
            "event_id": self.event_id,
            "source_id": self.source_id,
            "claim": self.claim,
            "first_observed_at": timestamp_payload(self.first_observed_at),
            "occurrence_time": timestamp_payload(self.occurrence_time),
            "evidenced_publication_time": timestamp_payload(self.evidenced_publication_time),
            "lateness_evidence": self.lateness_evidence,
            "definitive": self.definitive,
        }


_OBSERVATION_KEYS = frozenset({"observation_id", "event_id", "source_id", "observed_at"})


@dataclass(frozen=True)
class AbsenceObservation:
    """An archived read of the source at ``observed_at`` showing no matching record (the observation duty, OD5)."""

    observation_id: str
    event_id: str
    source_id: str
    observed_at: datetime

    @classmethod
    def from_payload(cls, payload: object) -> AbsenceObservation:
        mapping = require_mapping(payload, "AbsenceObservation")
        require_keys(mapping, "AbsenceObservation", _OBSERVATION_KEYS, frozenset())
        return cls(
            observation_id=require_identifier(mapping["observation_id"], "observation_id"),
            event_id=require_identifier(mapping["event_id"], "event_id"),
            source_id=require_identifier(mapping["source_id"], "source_id"),
            observed_at=require_timestamp(mapping["observed_at"], "observed_at"),
        )

    def to_payload(self) -> Payload:
        return {"observation_id": self.observation_id, "event_id": self.event_id, "source_id": self.source_id,
                "observed_at": timestamp_payload(self.observed_at)}


_STATUS_KEYS = frozenset({"source_id", "failed", "declared_at"})


@dataclass(frozen=True)
class SourceStatus:
    """Whether the source rule's failure condition holds for the source (declared with its evidence time)."""

    source_id: str
    failed: bool
    declared_at: datetime

    @classmethod
    def from_payload(cls, payload: object) -> SourceStatus:
        mapping = require_mapping(payload, "SourceStatus")
        require_keys(mapping, "SourceStatus", _STATUS_KEYS, frozenset())
        return cls(
            source_id=require_identifier(mapping["source_id"], "source_id"),
            failed=_require_bool(mapping["failed"], "failed"),
            declared_at=require_timestamp(mapping["declared_at"], "declared_at"),
        )

    def to_payload(self) -> Payload:
        return {"source_id": self.source_id, "failed": self.failed, "declared_at": timestamp_payload(self.declared_at)}
