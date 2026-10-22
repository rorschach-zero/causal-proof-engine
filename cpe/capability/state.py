"""The gate state, replayed from the ledger and the anchored prefix.

A state change is effective exactly when its commit record lies inside an anchored prefix, and it takes effect
at the commit record's ledger position, so that an epoch record after it (a demotion, a start, a discontinuity)
supersedes it live and on replay (RC-158, RC-197). The state is a plain value: holding one confers nothing, and
no protected operation accepts one as authority (RC-46).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from cpe.capability.levels import FLOOR
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
)
from cpe.capability.timesource import ClockReading
from cpe.errors import Refusal
from cpe.ledger import Record
from cpe.ledger.record import GENESIS_HASH


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


def replay_gate(records: tuple[Record, ...], anchored_prefix: int) -> GateState:
    """Replay the gate from the ledger records, with ``anchored_prefix`` the length of the longest anchored prefix
    the caller trusts (the local anchor copy is self-attested; the restore path verifies externally)."""
    state = GateState()
    for record in records:
        state.head = record.entry_hash
        if record.kind == KIND_EPOCH:
            epoch = EpochRecord.from_payload(record.payload)
            if epoch.index != state.epoch_index + 1:
                raise Refusal("invalid_gate_ledger", f"epoch index {epoch.index} does not follow {state.epoch_index}")
            state.epoch, state.epoch_index, state.epoch_seq = epoch.epoch, epoch.index, record.seq
            state.baseline = epoch.baseline
            state.observe(epoch.baseline)
            state.epoch_anchored = record.seq <= anchored_prefix
            state.level = FLOOR
            state.superseded |= state.effective  # a change effective before this record is superseded by it
        elif record.kind == KIND_INTENT:
            intent = IntentRecord.from_payload(record.payload)
            if intent.intent_id in state.intents:
                raise Refusal("invalid_gate_ledger", f"intent {intent.intent_id} appears twice")
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
            state.commits[commit.intent_id] = commit
            state.commit_seq[commit.intent_id] = record.seq
            state.observe(commit.reading)
            if record.seq <= anchored_prefix:
                state.effective.add(commit.intent_id)
                state.level = stored.target_level  # effective at its ledger position
        elif record.kind == KIND_CHECK:
            state.observe(CheckRecord.from_payload(record.payload).reading)
    return state
