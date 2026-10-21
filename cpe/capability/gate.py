"""The offline capability model: the gate and its protected operations (``17`` section 3 item 5, A5).

Enforcement is at the action boundary: a protected operation verifies the capability and consumes its nonce in
the writer transaction itself; no object held in the process is authority, and the state is replayed from the
ledger for every decision (RC-43, RC-46). The protected operation of Phase 1 is a gate promotion, run in four
recoverable steps against the external anchor store (RC-153, RC-158, RC-197). Every clock-dependent check writes
its reading before its verdict, and the clock rules of item 2 apply (RC-37, RC-65, RC-73, RC-100). The epoch is
rotated at every process start, at every demotion and at every clock discontinuity (RC-74, RC-103, RC-123).
"""
from __future__ import annotations

import logging
import math
import secrets
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from cpe.canonical import JsonValue, digest_of
from cpe.capability.levels import ACTIONS, permits, promotion_target, rank
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
from cpe.capability.signing import Verifier
from cpe.capability.state import GateState, replay_gate
from cpe.capability.timesource import ClockReading, TimeSource
from cpe.clock import parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Anchor, Ledger, Record
from cpe.schemas import Capability

log = logging.getLogger("cpe.capability")

Write = tuple[str, str, JsonValue]
Decide = Callable[[GateState, datetime], Write]
PromotionStatus = Literal["acknowledged", "superseded"]


def _ledger_id(prefix: str, *parts: str) -> str:
    return f"{prefix}:{digest_of(list(parts))}"


@dataclass(frozen=True)
class PromotionOutcome:
    """The acknowledgement of a promotion: given only after the commit record is inside an anchored prefix; the
    level reported is the gate's at that moment, which a demotion recorded after the commit supersedes."""

    intent_id: str
    status: PromotionStatus
    level: str
    commit_anchor: Anchor


class CapabilityGate:
    """One gate on one ledger. Constructing it is the process start: pending intents are aborted, an unanchored
    commit is anchored and takes effect at its position, the epoch is rotated and the gate is at the floor."""

    def __init__(self, ledger: Ledger, verifier: Verifier, time_source: TimeSource, environment: str,
                 release_digest: str, slew_tolerance_seconds: float) -> None:
        if not math.isfinite(slew_tolerance_seconds) or slew_tolerance_seconds <= 0:  # NaN or inf would disable RC-73, RC-100
            raise Refusal("invalid_tolerance", "the slew tolerance is a finite positive number of seconds (owner field)")
        self._ledger = ledger
        self._verifier = verifier
        self._time = time_source
        self._environment = environment
        self._release_digest = release_digest
        self._tolerance = slew_tolerance_seconds
        self._lock = threading.RLock()
        self.hooks: dict[str, Callable[[], None]] = {}  # test hooks, one per point of the four-step protocol
        self._start()

    # state ----------------------------------------------------------------------------------------------------

    def state(self) -> GateState:
        """Replayed from the ledger and its local anchor copy (self-attested; the restore path verifies)."""
        with self._lock:
            anchors = self._ledger.local_anchors()
            prefix = max((a.prefix_length for a in anchors), default=0)
            return replay_gate(self._ledger.records(), prefix)

    def _hook(self, point: str) -> None:
        hook = self.hooks.pop(point, None)
        if hook is not None:
            hook()

    def _append(self, decide: Decide) -> Record:
        """One read-decide-write against the chain head the decision was taken on; a head that moved makes the
        decision recompute on the new state (another writer on the same ledger, this gate or another)."""
        with self._lock:
            for _ in range(8):
                state = self.state()
                try:
                    now = self._ledger.now()
                except Refusal as refusal:
                    if refusal.reason == "clock_rollback":  # fails closed and is logged (item 2 "Clock", RC-37)
                        log.warning("clock rollback refused: %s", refusal)
                    raise
                kind, record_id, payload = decide(state, now)
                try:
                    return self._ledger.append(kind, record_id, payload, expected_head=state.head)
                except Refusal as refusal:
                    if refusal.reason != "stale_head":
                        raise
            raise Refusal("contended", "the ledger kept advancing while the record was being decided")

    def _try_anchor(self) -> Anchor | None:
        """An anchor attempt; any failure of the store or its transport is an unconfirmed anchor (the ledger keeps
        the attempt pending, PR #20). Only process-termination exceptions (``BaseException`` outside
        ``Exception``) escape."""
        try:
            return self._ledger.anchor()
        except Exception as error:
            log.warning("anchor not confirmed: %r", error)
            return None

    # clock ----------------------------------------------------------------------------------------------------

    def _raw_reading(self, now: datetime) -> ClockReading:
        return ClockReading(now, self._time.monotonic(), self._time.boot_id())

    def _reading(self, state: GateState, now: datetime) -> ClockReading:
        """The reading of this check. The wall time is the ledger's server clock, already refused below the
        high-water mark (RC-37, RC-65). A boot-id change, or a wall-minus-monotonic offset that differs from the
        epoch baseline by more than the tolerance, is an unverifiable discontinuity: the epoch is rotated at once,
        which invalidates every outstanding capability until the owner signs for the new epoch (RC-73, RC-100)."""
        reading = self._raw_reading(now)
        base = state.baseline
        if base is not None:
            detail = ""
            if reading.boot_id != base.boot_id:
                detail = f"boot id {base.boot_id} became {reading.boot_id}"
            elif abs(reading.offset() - base.offset()) > self._tolerance:
                detail = (f"wall-minus-monotonic drifted {reading.offset() - base.offset():.3f}s from the epoch "
                          f"baseline (tolerance {self._tolerance}s)")
            if detail:
                self._rotate(f"discontinuity:{detail}", reading)
                log.warning("clock discontinuity, re-authorisation required: %s", detail)
                raise Refusal("clock_discontinuity", f"{detail}; every outstanding capability is invalid")
        return reading

    # epochs -----------------------------------------------------------------------------------------------------

    def _rotate(self, reason: str, baseline: ClockReading | None = None) -> Record:
        """Persist the rotation (and the floor) in one writer transaction, then anchor it; an anchor failure never
        rolls it back: the gate stays demoted-unanchored until ``anchor_epoch`` succeeds (RC-103, RC-123)."""
        def decide(state: GateState, now: datetime) -> Write:
            reading = baseline if baseline is not None else self._raw_reading(now)
            # the identifier is random (not a secret): unique across restores, which a counter is not (RC-123)
            record = EpochRecord(secrets.randbits(62), state.epoch_index + 1, reason, reading)
            return KIND_EPOCH, _ledger_id("gate-epoch", str(record.index), str(record.epoch)), record.to_payload()

        record = self._append(decide)
        self._try_anchor()
        return record

    def _start(self) -> None:
        with self._lock:
            state = self.state()
            if state.unanchored_commits:  # RC-158: anchored under its key, takes effect at its position, unacknowledged
                self._try_anchor()
            for intent_id in state.pending_intents:  # RC-153: no state change ever takes effect from a pending intent
                self._abort(intent_id, "aborted at process start")
            self._rotate("start")

    def anchor_epoch(self) -> bool:
        """Retry the anchor of the current epoch; True once it is anchored."""
        with self._lock:
            if self.state().epoch_anchored:
                return True
            return self._try_anchor() is not None

    def demote(self, reason: str) -> GateState:
        """Demotion to the floor with the epoch rotation in one writer transaction; takes effect at once, anchored
        after; until anchored the gate is demoted-unanchored (RC-103, RC-123)."""
        with self._lock:
            self._rotate(f"demotion:{reason}")
            return self.state()

    # the action boundary ----------------------------------------------------------------------------------------

    def perform(self, action: str) -> Record:
        """Authorise ``action`` against the replayed gate state, never against an object the caller holds (RC-46);
        the check and its reading are persisted before the verdict."""
        verdict: tuple[str, str] = ("admitted", "")

        def decide(state: GateState, now: datetime) -> Write:
            nonlocal verdict
            reading = self._reading(state, now)
            if action not in ACTIONS:
                verdict = ("refused", "unknown_action")
            elif state.epoch_unanchored:
                verdict = ("refused", "epoch_unanchored")
            elif not permits(state.level, action):
                verdict = ("refused", "level_insufficient")
            else:
                verdict = ("admitted", "")
            check = CheckRecord(f"action:{action}", verdict[0], verdict[1], reading)
            return KIND_CHECK, _ledger_id("gate-check", state.head), check.to_payload()

        with self._lock:
            record = self._append(decide)
            if verdict[0] == "refused":
                raise Refusal(verdict[1], f"{action} is refused at level {self.state().level}")
            return record

    # the protected operation ------------------------------------------------------------------------------------

    def _validate(self, state: GateState, capability: Capability, evidence_digest: str, now: datetime) -> str | None:
        """The reason a presentation is refused, or None. Whole-tuple signature first (RC-62), then the environment,
        release, evidence, expiry, epoch, anchoring and nonce checks."""
        if not self._verifier.verify(capability.signed_bytes(), capability.signature):
            return "invalid_signature"
        if capability.environment != self._environment:
            return "wrong_environment"
        if capability.release_digest != self._release_digest:
            return "wrong_release"
        if capability.evidence_digest != evidence_digest:
            return "evidence_mismatch"
        if capability.expiry <= now:  # ``now`` is at or above the persisted high-water mark (RC-37)
            return "expired"
        if capability.epoch != state.epoch:
            return "stale_epoch"
        if state.epoch_unanchored:
            return "epoch_unanchored"
        if self._intent_id(capability) in state.intents:
            return "nonce_consumed"
        if rank(promotion_target(capability.capability)) <= rank(state.level):
            return "not_a_promotion"  # a lowering goes through ``demote``, which rotates the epoch (RC-103)
        return None

    @staticmethod
    def _intent_id(capability: Capability) -> str:
        """The nonce's identity in the ledger: one intent per (epoch, nonce), enforced by the ledger's unique
        record identifier inside the writer transaction (RC-43)."""
        return _ledger_id("gate-intent", str(capability.epoch), capability.nonce)

    def _abort(self, intent_id: str, reason: str) -> Record:
        """Append the abort of a pending intent with its reading. The reading is taken without the discontinuity
        test: an abort only settles a consumed nonce and authorises nothing, and it must be writable right after
        a discontinuity has rotated the epoch."""
        def decide(state: GateState, now: datetime) -> Write:
            record = AbortRecord(intent_id, reason, self._raw_reading(now))
            return KIND_ABORT, _ledger_id("gate-abort", intent_id), record.to_payload()

        return self._append(decide)

    def promote(self, capability: Capability, evidence: JsonValue) -> PromotionOutcome:
        """The protected operation: promote the gate to the level the capability names, on ``evidence`` whose
        digest the capability binds. Four recoverable steps: intent, anchor of the intent, commit record, anchor
        of the commit; the change takes effect at the commit record's position once that anchor is confirmed."""
        capability = Capability.from_payload(capability.to_payload())  # validated in full, as it will be replayed
        target = promotion_target(capability.capability)
        evidence_digest = digest_of(evidence)
        intent_id = self._intent_id(capability)
        refusal: str | None = None

        def intent(state: GateState, now: datetime) -> Write:
            nonlocal refusal
            reading = self._reading(state, now)
            refusal = self._validate(state, capability, evidence_digest, now)
            if refusal is not None:
                check = CheckRecord(f"presentation:{capability.nonce}", "refused", refusal, reading)
                return KIND_CHECK, _ledger_id("gate-check", state.head), check.to_payload()
            record = IntentRecord(intent_id, capability, target, reading)
            return KIND_INTENT, intent_id, record.to_payload()

        with self._lock:
            self._hook("before_intent")
            appended = self._append(intent)  # step 1: the nonce is consumed from here on every branch
            if refusal is not None:
                raise Refusal(refusal, f"capability {capability.nonce} refused")
            if parse_timestamp(appended.receipt_time) >= capability.expiry:  # the receipt is the time that counts
                self._abort(intent_id, "the intent was received at or after the capability's expiry")
                raise Refusal("expired", f"capability {capability.nonce} expired before its intent was received")
            self._hook("after_intent")
            intent_anchor = self._try_anchor()  # step 2
            if intent_anchor is None:
                self._abort(intent_id, "anchor of the intent failed")
                raise Refusal("anchor_failed", "the intent could not be anchored; nothing is acknowledged")
            self._hook("after_intent_anchor")
            aborted: str | None = None

            def commit(state: GateState, now: datetime) -> Write:  # step 3
                nonlocal aborted
                aborted = None  # decided afresh on every attempt against the current head
                reading = self._reading(state, now)
                if intent_id in state.aborted:
                    raise Refusal("intent_aborted", state.aborted[intent_id])
                stored = state.intents[intent_id]
                if state.epoch != stored.capability.epoch or state.epoch_seq is None \
                        or state.epoch_seq > state.intent_seq[intent_id]:
                    aborted = "epoch rotated since the intent (RC-197)"
                elif rank(stored.target_level) <= rank(state.level):
                    aborted = f"the gate reached {state.level} since the intent; a commit never lowers it"
                if aborted is not None:
                    record_abort = AbortRecord(intent_id, aborted, reading)
                    return KIND_ABORT, _ledger_id("gate-abort", intent_id), record_abort.to_payload()
                record = CommitRecord(intent_id, intent_anchor.prefix_length, intent_anchor.digest, reading)
                return KIND_COMMIT, _ledger_id("gate-commit", intent_id), record.to_payload()

            try:
                self._append(commit)
            except Refusal as step3:
                if step3.reason == "clock_discontinuity":  # the epoch has rotated: settle the consumed nonce now
                    self._abort(intent_id, f"clock discontinuity at step 3: {step3.detail}")
                raise
            if aborted is not None:
                raise Refusal("superseded", aborted)
            self._hook("after_commit_record")
            commit_anchor = self._try_anchor()  # step 4
            if commit_anchor is None:
                raise Refusal("commit_in_doubt", "the commit record is not anchored; nothing is acknowledged, "
                              "the next process start anchors it")
            self._hook("after_commit_anchor")
            state = self.state()
            if intent_id not in state.effective:
                raise Refusal("commit_in_doubt", "the commit record lies outside every local anchor")
            status: PromotionStatus = "superseded" if intent_id in state.superseded else "acknowledged"
            return PromotionOutcome(intent_id, status, state.level, commit_anchor)

