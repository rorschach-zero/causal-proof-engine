"""Forecast, arm version and Jev records (``17`` section 3 item 1).

Assumptions stated with the schema:
- A forecast carries one scored point probability and a declared ambiguity interval low <= point <= high (RC-05,
  T-22); the interval is a declared set with no coverage claim.
- A forecast carries no knowledge cutoff of its own: the cutoff is a property of the arm version it names, and a
  submission with a cutoff field is refused (RC-112).
- An arm version is an immutable record that declares the model knowledge cutoff as an UNVERIFIED provider claim
  with the evidence it was read from (RC-98), and lists the arm versions it consumes (RC-156). Its effective cutoff
  is the latest declared cutoff over itself and every input, recursively.
- The caller's own issuance time is an audited claim; the ledger's receipt time is the server clock (T-01).
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

from cpe.canonical import JsonValue
from cpe.errors import Refusal
from cpe.schemas.common import (
    identifier_list,
    Payload,
    optional_timestamp,
    require_date,
    require_digest,
    require_identifier,
    require_identifier_tuple,
    require_json,
    require_keys,
    require_mapping,
    require_non_negative_number,
    require_probability,
    timestamp_payload,
)

_FORECAST_REQUIRED = frozenset({
    "event_id", "arm_id", "slot_id", "arm_version_id", "point", "low", "high", "prompt_hash", "model_hash",
    "evidence_ids",
})
_FORECAST_OPTIONAL = frozenset({"claimed_issued_at"})


@dataclass(frozen=True)
class Forecast:
    event_id: str
    arm_id: str
    slot_id: str
    arm_version_id: str
    point: float
    low: float
    high: float
    prompt_hash: str
    model_hash: str
    evidence_ids: tuple[str, ...]
    claimed_issued_at: datetime | None = None

    def __post_init__(self) -> None:
        for name in ("point", "low", "high"):
            require_probability(getattr(self, name), name)
        if not self.low <= self.point <= self.high:
            raise Refusal("interval_disorder", "low <= point <= high is required (RC-05)")

    @classmethod
    def from_payload(cls, payload: object) -> Forecast:
        mapping = require_mapping(payload, "Forecast")
        if "cutoff" in mapping or "knowledge_cutoff" in mapping:
            raise Refusal("forecast_carries_cutoff", "a Forecast has no cutoff of its own; the arm version has (RC-112)")
        require_keys(mapping, "Forecast", _FORECAST_REQUIRED, _FORECAST_OPTIONAL)
        return cls(
            event_id=require_identifier(mapping["event_id"], "event_id"),
            arm_id=require_identifier(mapping["arm_id"], "arm_id"),
            slot_id=require_identifier(mapping["slot_id"], "slot_id"),
            arm_version_id=require_identifier(mapping["arm_version_id"], "arm_version_id"),
            point=require_probability(mapping["point"], "point"),
            low=require_probability(mapping["low"], "low"),
            high=require_probability(mapping["high"], "high"),
            prompt_hash=require_digest(mapping["prompt_hash"], "prompt_hash"),
            model_hash=require_digest(mapping["model_hash"], "model_hash"),
            evidence_ids=require_identifier_tuple(mapping["evidence_ids"], "evidence_ids", allow_empty=True),
            claimed_issued_at=optional_timestamp(mapping.get("claimed_issued_at"), "claimed_issued_at"),
        )

    def to_payload(self) -> Payload:
        return {
            "event_id": self.event_id,
            "arm_id": self.arm_id,
            "slot_id": self.slot_id,
            "arm_version_id": self.arm_version_id,
            "point": self.point,
            "low": self.low,
            "high": self.high,
            "prompt_hash": self.prompt_hash,
            "model_hash": self.model_hash,
            "evidence_ids": identifier_list(self.evidence_ids, "evidence_ids"),
            "claimed_issued_at": timestamp_payload(self.claimed_issued_at),
        }


CUTOFF_CLAIM_LABEL: Literal["UNVERIFIED"] = "UNVERIFIED"

_ARM_VERSION_KEYS = frozenset({
    "arm_version_id", "arm_id", "forecaster_id", "forecaster_version", "declared_cutoff", "cutoff_evidence_id",
    "cutoff_claim_label", "consumes",
})


@dataclass(frozen=True)
class ArmVersion:
    """Immutable registration of one forecaster version under one arm, with its declared knowledge cutoff."""

    arm_version_id: str
    arm_id: str
    forecaster_id: str
    forecaster_version: str
    declared_cutoff: date
    cutoff_evidence_id: str
    consumes: tuple[str, ...]
    cutoff_claim_label: Literal["UNVERIFIED"] = CUTOFF_CLAIM_LABEL

    def __post_init__(self) -> None:
        if self.cutoff_claim_label != CUTOFF_CLAIM_LABEL:
            raise Refusal("invalid_label", "a declared cutoff is recorded as an UNVERIFIED provider claim (RC-98)")
        if self.arm_version_id in self.consumes:
            raise Refusal("invalid_arm_graph", "an arm version cannot consume itself")

    @classmethod
    def from_payload(cls, payload: object) -> ArmVersion:
        mapping = require_mapping(payload, "ArmVersion")
        require_keys(mapping, "ArmVersion", _ARM_VERSION_KEYS, frozenset())
        label = mapping["cutoff_claim_label"]
        if label != CUTOFF_CLAIM_LABEL:
            raise Refusal("invalid_label", "cutoff_claim_label must be UNVERIFIED (RC-98)")
        return cls(
            arm_version_id=require_identifier(mapping["arm_version_id"], "arm_version_id"),
            arm_id=require_identifier(mapping["arm_id"], "arm_id"),
            forecaster_id=require_identifier(mapping["forecaster_id"], "forecaster_id"),
            forecaster_version=require_identifier(mapping["forecaster_version"], "forecaster_version"),
            declared_cutoff=require_date(mapping["declared_cutoff"], "declared_cutoff"),
            cutoff_evidence_id=require_identifier(mapping["cutoff_evidence_id"], "cutoff_evidence_id"),
            consumes=require_identifier_tuple(mapping["consumes"], "consumes", allow_empty=True),
        )

    def to_payload(self) -> Payload:
        return {
            "arm_version_id": self.arm_version_id,
            "arm_id": self.arm_id,
            "forecaster_id": self.forecaster_id,
            "forecaster_version": self.forecaster_version,
            "declared_cutoff": self.declared_cutoff.isoformat(),
            "cutoff_evidence_id": self.cutoff_evidence_id,
            "cutoff_claim_label": self.cutoff_claim_label,
            "consumes": identifier_list(self.consumes, "consumes"),
        }


def effective_cutoff(arm_version_id: str, versions: Mapping[str, ArmVersion]) -> date:
    """The latest declared cutoff over the arm version and every arm version it consumes, recursively (RC-156).

    A version that is not registered, or a cycle in the consumption graph, is refused: the cutoff of such an arm is
    undefined and no comparison may use it. Each version is resolved once (shared inputs are not re-walked), by an
    explicit stack, so a consumption chain of any registered depth resolves.
    """
    resolved: dict[str, date] = {}
    path: list[str] = []
    on_path: set[str] = set()
    stack: list[tuple[str, ArmVersion | None]] = [(arm_version_id, None)]  # (version id, the version once looked up)
    while stack:
        current, looked_up = stack.pop()
        if looked_up is not None:  # every input resolved: fold them in
            latest = looked_up.declared_cutoff
            for consumed in looked_up.consumes:
                latest = max(latest, resolved[consumed])
            resolved[current] = latest
            path.pop()
            on_path.discard(current)
            continue
        if current in resolved:
            continue
        if current in on_path:
            raise Refusal("invalid_arm_graph", f"{current} consumes itself through {' -> '.join(path)}")
        version = versions.get(current)
        if version is None:
            raise Refusal("unknown_arm_version", f"{current} is not registered")
        on_path.add(current)
        path.append(current)
        stack.append((current, version))
        for consumed in reversed(version.consumes):
            if consumed not in resolved:
                stack.append((consumed, None))
    return resolved[arm_version_id]


_JEV_KEYS = frozenset({
    "jev_record_id", "event_id", "inputs_digest", "result_positive", "result_negative", "model_hash",
    "routing_result", "cost",
})


@dataclass(frozen=True)
class JevRecord:
    """Jev triage record: the inputs, both polarities, the model hash, the routing result and the cost."""

    jev_record_id: str
    event_id: str
    inputs_digest: str
    result_positive: JsonValue
    result_negative: JsonValue
    model_hash: str
    routing_result: str
    cost: float

    @classmethod
    def from_payload(cls, payload: object) -> JevRecord:
        mapping = require_mapping(payload, "JevRecord")
        require_keys(mapping, "JevRecord", _JEV_KEYS, frozenset())
        return cls(
            jev_record_id=require_identifier(mapping["jev_record_id"], "jev_record_id"),
            event_id=require_identifier(mapping["event_id"], "event_id"),
            inputs_digest=require_digest(mapping["inputs_digest"], "inputs_digest"),
            result_positive=require_json(mapping["result_positive"], "result_positive"),
            result_negative=require_json(mapping["result_negative"], "result_negative"),
            model_hash=require_digest(mapping["model_hash"], "model_hash"),
            routing_result=require_identifier(mapping["routing_result"], "routing_result"),
            cost=require_non_negative_number(mapping["cost"], "cost"),
        )

    def to_payload(self) -> Payload:
        return {
            "jev_record_id": self.jev_record_id,
            "event_id": self.event_id,
            "inputs_digest": self.inputs_digest,
            "result_positive": self.result_positive,
            "result_negative": self.result_negative,
            "model_hash": self.model_hash,
            "routing_result": self.routing_result,
            "cost": self.cost,
        }
