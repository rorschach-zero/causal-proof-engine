"""Ledger records of the capability model. Every clock-dependent check writes one of them, so that its reading is
persisted in the same transaction as its verdict (RC-37, RC-65, RC-73)."""
from __future__ import annotations

from dataclasses import dataclass

from cpe.canonical import digest_of, require_hex_digest
from cpe.capability.timesource import ClockReading
from cpe.errors import Refusal
from cpe.schemas import Capability
from cpe.schemas.common import (
    Payload,
    require_digest,
    require_identifier,
    require_keys,
    require_mapping,
    require_non_negative_int,
)

KIND_EPOCH = "gate_epoch"
KIND_INTENT = "gate_intent"
KIND_ABORT = "gate_abort"
KIND_COMMIT = "gate_commit"
KIND_CHECK = "gate_check"
GATE_KINDS = frozenset({KIND_EPOCH, KIND_INTENT, KIND_ABORT, KIND_COMMIT, KIND_CHECK})

EpochReason = str  # "start", "demotion:<reason>", "discontinuity:<detail>"


def _text(value: object, field: str) -> str:
    """A text field of a gate record, refused rather than coerced when it is not a string (issue #37, pass 3)."""
    if not isinstance(value, str):
        raise Refusal("invalid_text", f"{field} must be a string")
    return value


def intent_ledger_id(capability: Capability) -> str:
    """The nonce's identity in the ledger: one intent per (epoch, nonce), enforced by the ledger's unique record
    identifier inside the writer transaction (RC-43). The protected operation writes it and replay requires it."""
    return f"gate-intent:{digest_of([str(capability.epoch), capability.nonce])}"


def epoch_ledger_id(index: int, epoch: int) -> str:
    """The rotation's identity in the ledger: the gate writes it and replay requires it."""
    return f"gate-epoch:{digest_of([str(index), str(epoch)])}"


@dataclass(frozen=True)
class EpochRecord:
    """An epoch rotation: at process start, at every demotion and at every clock discontinuity. The gate is at
    the floor from this record on; the reading is the clock baseline of the epoch (RC-74, RC-100, RC-103).

    ``epoch`` is the identifier a capability names, drawn fresh at every rotation and never a counter: a counter
    repeats after a restore that drops a rotation, and a capability signed for the dropped epoch would act again
    (RC-123 (ii)). ``index`` orders the rotations of one ledger."""

    epoch: int
    index: int
    reason: EpochReason
    baseline: ClockReading
    # The release the gate ran when it opened the epoch: the intents of the epoch are replayed against it, so that a
    # later release replays a ledger an earlier one wrote (PR #51 review 4353051510). Absent on epochs written
    # before it was recorded; those are replayed against the running release.
    release_digest: str | None = None

    @classmethod
    def from_payload(cls, payload: object) -> EpochRecord:
        m = require_mapping(payload, "EpochRecord")
        require_keys(m, "EpochRecord", frozenset({"epoch", "index", "reason", "baseline"}),
                     frozenset({"release_digest"}))
        index = require_non_negative_int(m["index"], "index")
        if index < 1:
            raise Refusal("invalid_epoch", "epoch indices start at 1")
        release = m.get("release_digest")
        return cls(require_non_negative_int(m["epoch"], "epoch"), index, _text(m["reason"], "reason"),
                   ClockReading.from_payload(m["baseline"]),
                   None if release is None else require_digest(release, "release_digest"))

    def to_payload(self) -> Payload:
        payload: Payload = {"epoch": self.epoch, "index": self.index, "reason": self.reason,
                            "baseline": self.baseline.to_payload()}
        if self.release_digest is not None:
            payload["release_digest"] = self.release_digest
        return payload


@dataclass(frozen=True)
class IntentRecord:
    """Step 1 of a protected operation: the capability consumed (its nonce is the record's identity), the state
    change it describes, not yet effective (RC-153)."""

    intent_id: str
    capability: Capability
    target_level: str
    reading: ClockReading

    @classmethod
    def from_payload(cls, payload: object) -> IntentRecord:
        m = require_mapping(payload, "IntentRecord")
        require_keys(m, "IntentRecord", frozenset({"intent_id", "capability", "target_level", "reading"}), frozenset())
        return cls(require_identifier(m["intent_id"], "intent_id"), Capability.from_payload(m["capability"]),
                   require_identifier(m["target_level"], "target_level"), ClockReading.from_payload(m["reading"]))

    def to_payload(self) -> Payload:
        return {"intent_id": self.intent_id, "capability": self.capability.to_payload(),
                "target_level": self.target_level, "reading": self.reading.to_payload()}


@dataclass(frozen=True)
class AbortRecord:
    """An intent that will never take effect: its nonce stays consumed (RC-153, RC-197). An abort is a
    clock-dependent check like any other, so it carries its reading (RC-65)."""

    intent_id: str
    reason: str
    reading: ClockReading

    @classmethod
    def from_payload(cls, payload: object) -> AbortRecord:
        m = require_mapping(payload, "AbortRecord")
        require_keys(m, "AbortRecord", frozenset({"intent_id", "reason", "reading"}), frozenset())
        return cls(require_identifier(m["intent_id"], "intent_id"), _text(m["reason"], "reason"), ClockReading.from_payload(m["reading"]))

    def to_payload(self) -> Payload:
        return {"intent_id": self.intent_id, "reason": self.reason, "reading": self.reading.to_payload()}


@dataclass(frozen=True)
class CommitRecord:
    """Step 3: references the intent and the anchor that covers it; effective only once it lies inside an anchored
    prefix itself, at its own ledger position (RC-158, RC-197)."""

    intent_id: str
    intent_anchor_prefix: int
    intent_anchor_digest: str
    reading: ClockReading

    @classmethod
    def from_payload(cls, payload: object) -> CommitRecord:
        m = require_mapping(payload, "CommitRecord")
        require_keys(m, "CommitRecord", frozenset({"intent_id", "intent_anchor_prefix", "intent_anchor_digest", "reading"}),
                     frozenset())
        return cls(require_identifier(m["intent_id"], "intent_id"),
                   require_non_negative_int(m["intent_anchor_prefix"], "intent_anchor_prefix"),
                   require_hex_digest(m["intent_anchor_digest"], "intent_anchor_digest"),
                   ClockReading.from_payload(m["reading"]))

    def to_payload(self) -> Payload:
        return {"intent_id": self.intent_id, "intent_anchor_prefix": self.intent_anchor_prefix,
                "intent_anchor_digest": self.intent_anchor_digest, "reading": self.reading.to_payload()}


@dataclass(frozen=True)
class CheckRecord:
    """A clock-dependent check that wrote no other record: a refused presentation or an action-boundary check,
    with its reading and verdict (RC-65: rejected checks persist their time too)."""

    subject: str
    verdict: str
    reason: str
    reading: ClockReading

    @classmethod
    def from_payload(cls, payload: object) -> CheckRecord:
        m = require_mapping(payload, "CheckRecord")
        require_keys(m, "CheckRecord", frozenset({"subject", "verdict", "reason", "reading"}), frozenset())
        return cls(_text(m["subject"], "subject"), _text(m["verdict"], "verdict"), _text(m["reason"], "reason"), ClockReading.from_payload(m["reading"]))

    def to_payload(self) -> Payload:
        return {"subject": self.subject, "verdict": self.verdict, "reason": self.reason, "reading": self.reading.to_payload()}
