"""Anchors and the anchor store (RC-34).

An anchor names a committed prefix of the ledger by its length and the chain digest at that length. A digest only
detects tampering if the copy it is compared against cannot be rewritten by the ledger writer, so anchors are
published through the ``AnchorStore`` interface. In Phase 1 the external store is ``HarnessAnchorStore``, an
in-memory, append-only double owned by the test harness: the writer can publish to it and never rewrite it. Its
export is a record the owner can commit to Git. Which production holder replaces it is OD6.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cpe.canonical import JsonValue, require_hex_digest
from cpe.clock import parse_timestamp
from cpe.errors import Refusal
from cpe.schemas.common import Payload, require_keys, require_mapping, require_non_negative_int

_ANCHOR_KEYS = frozenset({"prefix_length", "digest", "published_at"})


@dataclass(frozen=True)
class Anchor:
    prefix_length: int
    digest: str
    published_at: str

    @classmethod
    def from_payload(cls, payload: object) -> Anchor:
        mapping = require_mapping(payload, "Anchor")
        require_keys(mapping, "Anchor", _ANCHOR_KEYS, frozenset())
        length = require_non_negative_int(mapping["prefix_length"], "prefix_length")
        if length < 1:
            raise Refusal("invalid_anchor", "an anchor covers at least one record")
        parse_timestamp(mapping["published_at"], "published_at")
        return cls(length, require_hex_digest(mapping["digest"], "digest"), str(mapping["published_at"]))

    def to_payload(self) -> Payload:
        return {"prefix_length": self.prefix_length, "digest": self.digest, "published_at": self.published_at}


class AnchorStore(Protocol):
    """Append-only store of anchors held outside the writer's control."""

    def publish(self, anchor: Anchor) -> None: ...

    def anchors(self) -> tuple[Anchor, ...]: ...


class HarnessAnchorStore:
    """The Phase 1 test double: append-only, in memory, owned by the harness, exportable for Git."""

    def __init__(self, anchors: tuple[Anchor, ...] = ()) -> None:
        self._anchors: list[Anchor] = []
        for anchor in anchors:
            self.publish(anchor)

    def publish(self, anchor: Anchor) -> None:
        if self._anchors:
            last = self._anchors[-1]
            if anchor.prefix_length < last.prefix_length:
                raise Refusal("anchor_regression", "an anchor never covers a shorter prefix than its predecessor")
            if anchor.prefix_length == last.prefix_length:
                if anchor.digest != last.digest:
                    raise Refusal("anchor_conflict", f"prefix {anchor.prefix_length} is already anchored with another digest")
                return
        self._anchors.append(anchor)

    def anchors(self) -> tuple[Anchor, ...]:
        return tuple(self._anchors)

    def export(self) -> list[JsonValue]:
        return [anchor.to_payload() for anchor in self._anchors]

    @classmethod
    def from_export(cls, exported: object) -> HarnessAnchorStore:
        if not isinstance(exported, list):
            raise Refusal("invalid_anchor_export", "an anchor export is a list of anchors")
        return cls(tuple(Anchor.from_payload(item) for item in exported))


class UnavailableAnchorStore:
    """A store whose every call fails: models an outage, so that callers must fail closed (T-30)."""

    def publish(self, anchor: Anchor) -> None:
        raise Refusal("anchor_store_unavailable", "the anchor store did not answer")

    def anchors(self) -> tuple[Anchor, ...]:
        raise Refusal("anchor_store_unavailable", "the anchor store did not answer")
