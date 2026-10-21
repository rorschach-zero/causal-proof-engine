"""The resolution-content archive record: the source bytes a resolution record rests on, content-addressed.

Assumptions (hand-off section 3.1, decided 2026-10-21; PR #18 round-3 finding 4329664953):
- The caller supplies the bytes as an attested input; nothing is fetched. The archive keeps the bytes, their
  SHA-256, the media type, the source and the attested ``available_at``; the receipt time is the ledger's.
- A declared digest that does not match the bytes is refused; replay recomputes the digest from the stored bytes.
- The archive is faithful: it stores bytes of any media type. Whether a media type can be evaluated is decided by
  the predicate evaluator (``cpe.adjudication.predicate``), which refuses what it does not support.
"""
from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime

from cpe.canonical import require_hex_digest, sha256_hex
from cpe.errors import Refusal
from cpe.schemas.common import Payload, require_identifier, require_keys, require_mapping, require_timestamp, timestamp_payload

_CONTENT_KEYS = frozenset({"content_base64", "sha256", "media_type", "source_id", "available_at"})


@dataclass(frozen=True)
class ArchivedContent:
    """Bytes of one source read, as attested by the observer, under the SHA-256 that addresses them."""

    content: bytes
    sha256: str
    media_type: str
    source_id: str
    available_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.content, bytes):
            raise Refusal("invalid_content", "content must be bytes")
        require_hex_digest(self.sha256, "sha256")
        require_identifier(self.media_type, "media_type")
        require_identifier(self.source_id, "source_id")
        if sha256_hex(self.content) != self.sha256:
            raise Refusal("digest_mismatch", f"the bytes do not have the declared SHA-256 {self.sha256}")

    @classmethod
    def from_payload(cls, payload: object) -> ArchivedContent:
        mapping = require_mapping(payload, "ArchivedContent")
        require_keys(mapping, "ArchivedContent", _CONTENT_KEYS, frozenset())
        encoded = mapping["content_base64"]
        if not isinstance(encoded, str):
            raise Refusal("invalid_content", "content_base64 must be a string")
        try:
            content = base64.b64decode(encoded.encode("ascii"), validate=True)
        except (binascii.Error, UnicodeEncodeError):
            raise Refusal("invalid_content", "content_base64 is not strict base64") from None
        if base64.b64encode(content).decode("ascii") != encoded:
            raise Refusal("invalid_content", "content_base64 is not in its one canonical encoding")
        return cls(
            content=content,
            sha256=require_hex_digest(mapping["sha256"], "sha256"),
            media_type=require_identifier(mapping["media_type"], "media_type"),
            source_id=require_identifier(mapping["source_id"], "source_id"),
            available_at=require_timestamp(mapping["available_at"], "available_at"),
        )

    def to_payload(self) -> Payload:
        return {
            "content_base64": base64.b64encode(self.content).decode("ascii"),
            "sha256": self.sha256,
            "media_type": self.media_type,
            "source_id": self.source_id,
            "available_at": timestamp_payload(self.available_at),
        }
