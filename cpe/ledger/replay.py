"""Replay and verification.

``replay`` rebuilds the ledger state from records alone; the online writer maintains the same state, and the two
digests must agree byte for byte (A1). ``verify`` compares the chain with the anchors: a chain break or a digest
mismatch inside an anchored prefix is tampering; a ledger shorter than its anchor is truncated; records beyond the
last anchor form the unanchored window, which is reported and never called verified (T-07, F-07). Anchors read from
the writer's own copy give a self-attested report only (T-18).
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Literal

from cpe.canonical import JsonValue, digest_of
from cpe.errors import Refusal
from cpe.ledger.anchor import Anchor
from cpe.ledger.record import GENESIS_HASH, Record


@dataclass
class LedgerState:
    """What the ledger itself knows: how many records, the chain head, the receipt-time high-water mark and
    the record count per kind. Registries that replay their own state build on it."""

    count: int = 0
    head: str = GENESIS_HASH
    high_water: str = ""
    kinds: dict[str, int] = field(default_factory=dict)

    def apply(self, record: Record) -> None:
        if record.seq != self.count + 1:
            raise Refusal("chain_gap", f"record {record.record_id} has seq {record.seq}, expected {self.count + 1}")
        if record.prev_hash != self.head:
            raise Refusal("chain_break", f"record {record.seq} does not extend the chain head")
        if record.entry_hash != record.expected_hash():
            raise Refusal("hash_mismatch", f"record {record.seq} does not match its own hash")
        if record.receipt_time < self.high_water:
            raise Refusal("receipt_time_regression", f"record {record.seq} is received before its predecessor")
        self.count = record.seq
        self.head = record.entry_hash
        self.high_water = record.receipt_time
        self.kinds[record.kind] = self.kinds.get(record.kind, 0) + 1

    def to_payload(self) -> JsonValue:
        return {"count": self.count, "head": self.head, "high_water": self.high_water,
                "kinds": dict(sorted(self.kinds.items()))}

    def digest(self) -> str:
        return digest_of(self.to_payload())


def replay(records: Iterable[Record]) -> LedgerState:
    state = LedgerState()
    for record in records:
        state.apply(record)
    return state


Status = Literal["continuous", "tampered", "truncated"]
Attestation = Literal["verified", "self-attested", "unanchored"]


@dataclass(frozen=True)
class VerificationReport:
    status: Status
    attestation: Attestation
    anchored_prefix: int
    unanchored_window: int
    detail: str

    @property
    def intact(self) -> bool:
        return self.status == "continuous"


def _chain_break(records: Sequence[Record]) -> int | None:
    """Position (seq) of the first record that breaks the chain, or None."""
    head = GENESIS_HASH
    for index, record in enumerate(records, start=1):
        if record.seq != index or record.prev_hash != head or record.entry_hash != record.expected_hash():
            return index
        head = record.entry_hash
    return None


def verify(records: Sequence[Record], anchors: Sequence[Anchor], *, external: bool) -> VerificationReport:
    """Verify ``records`` against ``anchors``.

    ``external`` says whether the anchors came from the anchor store (verified) or from the writer's own copy
    (self-attested). With no anchor at all every record is in the unanchored window.
    """
    attestation: Attestation = "verified" if external else "self-attested"
    broken_at = _chain_break(records)
    if not anchors:
        if broken_at is not None:
            return VerificationReport("tampered", "unanchored", 0, 0, f"chain broken at record {broken_at}")
        return VerificationReport("continuous", "unanchored", 0, len(records), f"unanchored window of {len(records)} records")
    latest = max(anchors, key=lambda anchor: anchor.prefix_length)
    if len(records) < latest.prefix_length:
        return VerificationReport("truncated", attestation, 0, 0,
                                  f"ledger holds {len(records)} records, anchor covers {latest.prefix_length}")
    if broken_at is not None and broken_at <= latest.prefix_length:
        return VerificationReport("tampered", attestation, 0, 0, f"chain broken at record {broken_at} inside the anchored prefix")
    for anchor in anchors:
        if anchor.prefix_length <= len(records) and records[anchor.prefix_length - 1].entry_hash != anchor.digest:
            return VerificationReport("tampered", attestation, 0, 0,
                                      f"digest at prefix {anchor.prefix_length} differs from the anchor")
    if broken_at is not None:
        return VerificationReport("tampered", attestation, latest.prefix_length, 0,
                                  f"chain broken at record {broken_at} after the anchored prefix")
    window = len(records) - latest.prefix_length
    return VerificationReport("continuous", attestation, latest.prefix_length, window,
                              f"anchored prefix of {latest.prefix_length} records ({attestation}), "
                              f"unanchored window of {window} records")
