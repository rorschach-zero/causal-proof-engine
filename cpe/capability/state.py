"""The gate state, replayed from the ledger and the anchored prefix.

A state change is effective exactly when its commit record lies inside an anchored prefix, and it takes effect
at the commit record's ledger position, so that an epoch record after it (a demotion, a start, a discontinuity)
supersedes it live and on replay (RC-158, RC-197). The state is a plain value: holding one confers nothing, and
no protected operation accepts one as authority (RC-46).

Replay re-validates every intent and commit as the protected operation validated it when it wrote them: a gate
record written through the ledger by anything other than the protected operation (a forged capability, an intent
under another identity, a commit the operation would have aborted) refuses the ledger, and never confers a level
(issue #37, pass 4 W1).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from cpe.capability.levels import FLOOR, promotion_target, rank
from cpe.capability.records import (
    KIND_ABORT,
    KIND_CHECK,
    KIND_COMMIT,
    KIND_EPOCH,
    KIND_INTENT,
    AbortRecord,
    CheckRecord,
    CommitRecord,
    EpochRecord,
    IntentRecord,
    intent_ledger_id,
)
from cpe.capability.signing import Verifier
from cpe.capability.timesource import ClockReading
from cpe.clock import parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Anchor, Record
from cpe.ledger.record import GENESIS_HASH


@dataclass(frozen=True)
class GateRules:
    """What the protected operation checks a capability against, and replay with it: the owner's signature over the
    whole tuple, the environment and the release (RC-43, RC-46, RC-62)."""

    verifier: Verifier
    environment: str
    release_digest: str


@dataclass
class GateState:
    head: str = GENESIS_HASH
    epoch: int = 0
    epoch_index: int = 0
    epoch_seq: int | None = None
    baseline: ClockReading | None = None
    epoch_anchored: bool = False
    level: str = FLOOR
    intents: dict[str, IntentRecord] = field(default_factory=dict)
    intent_seq: dict[str, int] = field(default_factory=dict)
    aborted: dict[str, str] = field(default_factory=dict)
    commits: dict[str, CommitRecord] = field(default_factory=dict)
    commit_seq: dict[str, int] = field(default_factory=dict)
    effective: set[str] = field(default_factory=set)
    superseded: set[str] = field(default_factory=set)
    # The latest wall time any persisted reading observed. A check decided on one clock sample can be received at
    # an earlier one after a rollback; the time it observed bounds the clock as its receipt does (RC-65, issue #37).
    observed: datetime | None = None
    epoch_release: str | None = None  # the release the current epoch was opened under, when recorded

    def observe(self, reading: ClockReading) -> None:
        if self.observed is None or reading.wall > self.observed:
            self.observed = reading.wall

    @property
    def epoch_unanchored(self) -> bool:
        """True from a rotation until its record is anchored: demoted-unanchored after a demotion, and the start
        state before the start rotation is anchored; every promotion and protected action is refused (RC-123)."""
        return self.epoch_seq is not None and not self.epoch_anchored

    @property
    def pending_intents(self) -> tuple[str, ...]:
        return tuple(i for i in self.intents if i not in self.aborted and i not in self.commits)

    @property
    def unanchored_commits(self) -> tuple[str, ...]:
        return tuple(i for i in self.commits if i not in self.effective)


def _check_intent(record: Record, intent: IntentRecord, state: GateState, rules: GateRules) -> None:
    """The checks the protected operation made before it wrote this intent (``CapabilityGate._validate``), on the
    record as persisted. The evidence is not on the ledger, only its digest inside the signed capability."""
    capability = intent.capability
    problem = None
    if not rules.verifier.verify(capability.signed_bytes(), capability.signature):
        problem = "carries no valid owner signature"
    elif capability.environment != rules.environment:
        problem = f"names environment {capability.environment!r}"
    elif capability.release_digest != (state.epoch_release or rules.release_digest):
        problem = "names a release other than its epoch's"
    elif record.record_id != intent_ledger_id(capability) or intent.intent_id != record.record_id:
        problem = "is not written under its nonce's identity"
    elif intent.target_level != promotion_target(capability.capability):
        problem = f"targets {intent.target_level}, not the level its capability names"
    elif capability.expiry <= parse_timestamp(record.receipt_time):
        problem = "was received at or after its capability's expiry"
    elif state.epoch_seq is None or capability.epoch != state.epoch:
        problem = "names an epoch other than the current one"
    # Whether it was a promotion is not re-checked here: the level the operation saw counted only the commits
    # anchored at that time, which replay cannot know. A commit that does not raise the gate refuses the ledger.
    if problem is not None:
        raise Refusal("invalid_gate_ledger", f"intent {intent.intent_id} {problem}")


def _check_commit(record: Record, commit: CommitRecord, state: GateState, hashes: list[str],
                  anchors: frozenset[tuple[int, str]]) -> None:
    """The checks step 3 made before it wrote this commit rather than an abort: the epoch has not rotated since the
    intent, the commit raises the gate above every commit of the epoch, and it cites a published anchor, one of the
    ledger's anchors, of a prefix that covers the intent and ends at a record of this chain; a hash-chain reference
    to a prefix nobody anchored is not step 2 (PR #51 review 4353051497)."""
    stored = state.intents[commit.intent_id]
    intent_seq = state.intent_seq[commit.intent_id]
    problem = None
    if stored.capability.epoch != state.epoch or state.epoch_seq is None or state.epoch_seq > intent_seq:
        problem = "follows a rotation of its intent's epoch"
    else:
        written = [state.intents[i].target_level for i in state.commits
                   if state.intents[i].capability.epoch == state.epoch]
        if rank(stored.target_level) <= rank(max([state.level, *written], key=rank)):
            problem = "does not raise the gate"
        elif not intent_seq <= commit.intent_anchor_prefix < record.seq \
                or hashes[commit.intent_anchor_prefix - 1] != commit.intent_anchor_digest \
                or (commit.intent_anchor_prefix, commit.intent_anchor_digest) not in anchors:
            problem = "cites no published anchor of a prefix covering its intent"
    if problem is not None:
        raise Refusal("invalid_gate_ledger", f"commit of {commit.intent_id} {problem}")


def replay_gate(records: tuple[Record, ...], anchored_prefix: int, rules: GateRules,
                anchors: tuple[Anchor, ...]) -> GateState:
    """Replay the gate from the ledger records, with ``anchored_prefix`` the length of the longest anchored prefix
    the caller trusts and ``anchors`` the anchors it holds (the local anchor copy is self-attested; the restore path
    verifies externally), and every intent and commit re-validated under ``rules``."""
    published = frozenset((anchor.prefix_length, anchor.digest) for anchor in anchors)
    state = GateState()
    hashes: list[str] = []
    for record in records:
        state.head = record.entry_hash
        hashes.append(record.entry_hash)
        if record.kind == KIND_EPOCH:
            epoch = EpochRecord.from_payload(record.payload)
            if epoch.index != state.epoch_index + 1:
                raise Refusal("invalid_gate_ledger", f"epoch index {epoch.index} does not follow {state.epoch_index}")
            state.epoch, state.epoch_index, state.epoch_seq = epoch.epoch, epoch.index, record.seq
            state.baseline = epoch.baseline
            state.epoch_release = epoch.release_digest
            state.observe(epoch.baseline)
            state.epoch_anchored = record.seq <= anchored_prefix
            state.level = FLOOR
            state.superseded |= state.effective  # a change effective before this record is superseded by it
        elif record.kind == KIND_INTENT:
            intent = IntentRecord.from_payload(record.payload)
            if intent.intent_id in state.intents:
                raise Refusal("invalid_gate_ledger", f"intent {intent.intent_id} appears twice")
            _check_intent(record, intent, state, rules)
            state.intents[intent.intent_id] = intent
            state.intent_seq[intent.intent_id] = record.seq
            state.observe(intent.reading)
        elif record.kind == KIND_ABORT:
            abort = AbortRecord.from_payload(record.payload)
            if abort.intent_id not in state.intents or abort.intent_id in state.commits:
                raise Refusal("invalid_gate_ledger", f"abort of {abort.intent_id} without a pending intent")
            state.aborted[abort.intent_id] = abort.reason
            state.observe(abort.reading)
        elif record.kind == KIND_COMMIT:
            commit = CommitRecord.from_payload(record.payload)
            stored = state.intents.get(commit.intent_id)
            if stored is None or commit.intent_id in state.aborted or commit.intent_id in state.commits:
                raise Refusal("invalid_gate_ledger", f"commit of {commit.intent_id} without a pending intent")
            if stored.capability.epoch != state.epoch:
                raise Refusal("invalid_gate_ledger", f"commit of {commit.intent_id} after its epoch rotated")
            _check_commit(record, commit, state, hashes, published)
            state.commits[commit.intent_id] = commit
            state.commit_seq[commit.intent_id] = record.seq
            state.observe(commit.reading)
            if record.seq <= anchored_prefix:
                state.effective.add(commit.intent_id)
                state.level = stored.target_level  # effective at its ledger position
        elif record.kind == KIND_CHECK:
            state.observe(CheckRecord.from_payload(record.payload).reading)
    return state
