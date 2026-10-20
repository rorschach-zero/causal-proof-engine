"""Research output: the record a future model adapter returns (``17`` section 3 item 1, "for future adapters").

No adapter exists in Phase 1; the schema fixes the contract so that an adapter cannot pass a value the registry
would have to interpret. The reasoning digest is a hex SHA-256 (fixture F-04 refuses ``'z' * 64``).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cpe.errors import Refusal
from cpe.schemas.common import (
    Payload,
    optional_timestamp,
    require_digest,
    require_identifier,
    require_identifier_tuple,
    require_keys,
    require_mapping,
    timestamp_payload,
)
from cpe.schemas.forecast import Forecast

_KEYS = frozenset({"arm_id", "event_id", "forecast", "reasoning_digest", "evidence_ids"})


@dataclass(frozen=True)
class ResearchOutput:
    arm_id: str
    event_id: str
    forecast: Forecast
    reasoning_digest: str
    evidence_ids: tuple[str, ...]
    claimed_produced_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.forecast.arm_id != self.arm_id or self.forecast.event_id != self.event_id:
            raise Refusal("inconsistent_output", "the forecast must name the output's arm and event")

    @classmethod
    def from_payload(cls, payload: object) -> ResearchOutput:
        mapping = require_mapping(payload, "ResearchOutput")
        require_keys(mapping, "ResearchOutput", _KEYS, frozenset({"claimed_produced_at"}))
        return cls(
            arm_id=require_identifier(mapping["arm_id"], "arm_id"),
            event_id=require_identifier(mapping["event_id"], "event_id"),
            forecast=Forecast.from_payload(mapping["forecast"]),
            reasoning_digest=require_digest(mapping["reasoning_digest"], "reasoning_digest"),
            evidence_ids=require_identifier_tuple(mapping["evidence_ids"], "evidence_ids", allow_empty=True),
            claimed_produced_at=optional_timestamp(mapping.get("claimed_produced_at"), "claimed_produced_at"),
        )

    def to_payload(self) -> Payload:
        return {
            "arm_id": self.arm_id,
            "event_id": self.event_id,
            "forecast": self.forecast.to_payload(),
            "reasoning_digest": self.reasoning_digest,
            "evidence_ids": list(self.evidence_ids),
            "claimed_produced_at": timestamp_payload(self.claimed_produced_at),
        }
