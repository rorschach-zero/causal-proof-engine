"""Ledger records and the hash chain."""
from __future__ import annotations

from dataclasses import dataclass

from cpe.canonical import ZERO_DIGEST, JsonValue, digest_of, require_hex_digest
from cpe.errors import Refusal
from cpe.schemas.common import Payload, require_identifier, require_keys, require_mapping, require_non_negative_int
from cpe.clock import parse_timestamp

_RECORD_KEYS = frozenset({"seq", "record_id", "kind", "receipt_time", "payload", "prev_hash", "entry_hash"})


def entry_digest(seq: int, record_id: str, kind: str, receipt_time: str, payload: JsonValue, prev_hash: str) -> str:
    """SHA-256 over the canonical form of every field but the entry hash itself."""
    return digest_of({
        "seq": seq,
        "record_id": record_id,
        "kind": kind,
        "receipt_time": receipt_time,
        "payload": payload,
        "prev_hash": prev_hash,
    })


@dataclass(frozen=True)
class Record:
    """One admitted record: position, identity, kind, server receipt time, payload and chain hashes."""

    seq: int
    record_id: str
    kind: str
    receipt_time: str
    payload: JsonValue
    prev_hash: str
    entry_hash: str

    def expected_hash(self) -> str:
        return entry_digest(self.seq, self.record_id, self.kind, self.receipt_time, self.payload, self.prev_hash)

    @classmethod
    def from_payload(cls, payload: object) -> Record:
        mapping = require_mapping(payload, "Record")
        require_keys(mapping, "Record", _RECORD_KEYS, frozenset())
        seq = require_non_negative_int(mapping["seq"], "seq")
        if seq < 1:
            raise Refusal("invalid_record", "seq starts at 1")
        parse_timestamp(mapping["receipt_time"], "receipt_time")
        return cls(
            seq=seq,
            record_id=require_identifier(mapping["record_id"], "record_id"),
            kind=require_identifier(mapping["kind"], "kind"),
            receipt_time=str(mapping["receipt_time"]),
            payload=mapping["payload"],
            prev_hash=require_hex_digest(mapping["prev_hash"], "prev_hash"),
            entry_hash=require_hex_digest(mapping["entry_hash"], "entry_hash"),
        )

    def to_payload(self) -> Payload:
        return {
            "seq": self.seq,
            "record_id": self.record_id,
            "kind": self.kind,
            "receipt_time": self.receipt_time,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


GENESIS_HASH = ZERO_DIGEST
