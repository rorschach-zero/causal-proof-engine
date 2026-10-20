"""Capability record (``17`` section 3 item 5, schema only).

The signature covers the whole tuple (capability, environment, release digest, evidence digest, epoch, nonce,
expiry) under the canonical serialisation of ``cpe.canonical``, so that no field can be substituted under a valid
signature (RC-62). Verification, epochs and consumption live in the capability model; this module defines the
record and the bytes that are signed.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cpe.canonical import canonical_bytes
from cpe.schemas.common import (
    Payload,
    require_digest,
    require_identifier,
    require_keys,
    require_mapping,
    require_non_negative_int,
    require_timestamp,
    timestamp_payload,
)

_SIGNED_KEYS = frozenset({"capability", "environment", "release_digest", "evidence_digest", "epoch", "nonce", "expiry"})
_CAPABILITY_KEYS = _SIGNED_KEYS | {"signature"}


@dataclass(frozen=True)
class Capability:
    capability: str
    environment: str
    release_digest: str
    evidence_digest: str
    epoch: int
    nonce: str
    expiry: datetime
    signature: str

    def signed_payload(self) -> Payload:
        return {
            "capability": self.capability,
            "environment": self.environment,
            "release_digest": self.release_digest,
            "evidence_digest": self.evidence_digest,
            "epoch": self.epoch,
            "nonce": self.nonce,
            "expiry": timestamp_payload(self.expiry),
        }

    def signed_bytes(self) -> bytes:
        """The exact bytes the owner signs: the canonical form of the seven signed fields."""
        return canonical_bytes(self.signed_payload())

    @classmethod
    def from_payload(cls, payload: object) -> Capability:
        mapping = require_mapping(payload, "Capability")
        require_keys(mapping, "Capability", _CAPABILITY_KEYS, frozenset())
        return cls(
            capability=require_identifier(mapping["capability"], "capability"),
            environment=require_identifier(mapping["environment"], "environment"),
            release_digest=require_digest(mapping["release_digest"], "release_digest"),
            evidence_digest=require_digest(mapping["evidence_digest"], "evidence_digest"),
            epoch=require_non_negative_int(mapping["epoch"], "epoch"),
            nonce=require_identifier(mapping["nonce"], "nonce"),
            expiry=require_timestamp(mapping["expiry"], "expiry"),
            signature=require_identifier(mapping["signature"], "signature"),
        )

    def to_payload(self) -> Payload:
        payload = self.signed_payload()
        payload["signature"] = self.signature
        return payload
