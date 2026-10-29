"""The pre-registration registry on the ledger. State is rebuilt from the ledger on every operation; every time
comes from the ledger's clock; every write names the chain head it was decided on, so a decision no longer valid
against a record another writer admitted in between is recomputed, never committed."""
from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from typing import Literal

from cpe.canonical import JsonValue, digest_of
from cpe.clock import format_timestamp, parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Anchor, Ledger, Record
from cpe.ledger.record import GENESIS_HASH
from cpe.registration.records import (
    BaseRate,
    BeaconOutput,
    CalibrationRecord,
    CandidateEntry,
    ClaimPreregistration,
    ClusterRegistration,
    ConfirmatoryRegister,
    CutoffCorrection,
    VoidRequest,
)
from cpe.registration.seeds import derive_seed
from cpe.schemas import ArmVersion, EventSpec, Forecast, effective_cutoff
from cpe.schemas.common import Payload

KIND_ARM_VERSION = "arm_version"
KIND_CUTOFF_CORRECTION = "cutoff_correction"
KIND_CANDIDATE = "candidate"
KIND_CLUSTER = "cluster_registration"
KIND_VOID_REQUEST = "void_request"
KIND_BASE_RATE = "base_rate"
KIND_FORECAST = "forecast"
KIND_CLAIM = "claim_preregistration"
KIND_REGISTER = "confirmatory_register"
KIND_CALIBRATION = "calibration_record"
KIND_BEACON = "beacon_output"
KIND_ROUND_REFUSED = "beacon_round_refused"

SlotStatus = Literal["filled", "open", "abstention", "baseline"]
Write = tuple[str, str, JsonValue]


def _ledger_id(prefix: str, *parts: str) -> str:
    """A ledger identifier for a registry record: the prefix and the digest of its parts, so that external
    identifiers of any admitted length, with any character, yield one identifier within the limit and distinct
    parts never collide."""
    return f"{prefix}:{digest_of(list(parts))}"


@dataclass(frozen=True)
class SlotState:
    event_id: str
    arm_id: str
    slot_id: str
    status: SlotStatus
    forecast_record_id: str | None = None
    value: float | None = None


@dataclass(frozen=True)
class ReceivedForecast:
    forecast: Forecast
    record_id: str
    receipt: datetime


@dataclass
class _State:
    head: str = GENESIS_HASH
    arm_versions: dict[str, ArmVersion] = field(default_factory=dict)
    withdrawn: set[str] = field(default_factory=set)
    registrations_under: dict[str, int] = field(default_factory=dict)
    candidates: dict[str, CandidateEntry] = field(default_factory=dict)
    candidate_by_event: dict[str, CandidateEntry] = field(default_factory=dict)
    clusters: dict[str, ClusterRegistration] = field(default_factory=dict)
    cluster_registered_at: dict[str, datetime] = field(default_factory=dict)
    events: dict[str, EventSpec] = field(default_factory=dict)
    event_cluster: dict[str, str] = field(default_factory=dict)
    base_rates: dict[str, float] = field(default_factory=dict)
    forecasts: dict[tuple[str, str, str], ReceivedForecast] = field(default_factory=dict)
    forecasts_by_event: dict[str, list[ReceivedForecast]] = field(default_factory=dict)
    submissions: dict[tuple[str, str, str], int] = field(default_factory=dict)
    claims: dict[str, ClaimPreregistration] = field(default_factory=dict)
    register: ConfirmatoryRegister | None = None
    register_seq: int | None = None
    calibrations: dict[str, CalibrationRecord] = field(default_factory=dict)
    calibration_seq: dict[str, int] = field(default_factory=dict)
    calibration_by_claim: dict[str, str] = field(default_factory=dict)
    beacon_outputs: dict[str, BeaconOutput] = field(default_factory=dict)
    beacon_seq: dict[str, int] = field(default_factory=dict)
    seeds: dict[str, str] = field(default_factory=dict)
    # Beacon rounds refused because the register was not anchored before them: each one shows that a round bound to
    # a Phase 1 calibration record was published at that time (RC-311; issue #37, pass 3 F4).
    refused_rounds: dict[str, BeaconOutput] = field(default_factory=dict)
    local_anchors: tuple[Anchor, ...] = ()  # read with the snapshot, never by a decision under the ledger's lock
    pending_anchors: tuple[Anchor, ...] = ()  # attempts not yet confirmed, read with the snapshot


def _payload_of(value: ArmVersion | CutoffCorrection | BaseRate | ClusterRegistration | VoidRequest
                | ConfirmatoryRegister | CalibrationRecord | BeaconOutput | CandidateEntry | Forecast
                | ClaimPreregistration) -> Payload:
    """The payload a write would persist, for validation in full as replay will read it: a directly constructed
    object that bypasses its schema is refused before anything is written, never committed as a row that every
    later replay refuses (issue #37, Codex 5). An object whose fields cannot be serialised is refused alike."""
    try:
        return value.to_payload()
    except Refusal:
        raise
    except Exception as error:
        raise Refusal("invalid_object", f"{type(value).__name__} cannot be serialised: {error!r}") from None


def _consumption_closure(version_id: str, versions: dict[str, ArmVersion]) -> set[str]:
    """The version and every version it consumes, transitively: the set whose declared cutoffs compose its
    effective cutoff (RC-156)."""
    closure: set[str] = set()
    pending = [version_id]
    while pending:
        current = pending.pop()
        if current in closure:
            continue
        closure.add(current)
        pending.extend(versions[current].consumes)
    return closure


def _consumers(version_id: str, versions: dict[str, ArmVersion]) -> set[str]:
    """The version and every version that consumes it, transitively: every version whose effective cutoff a
    correction to it would change."""
    return {other for other in versions if version_id in _consumption_closure(other, versions)}


def replay_state(records: tuple[Record, ...]) -> _State:
    state = _State()
    for record in records:
        state.head = record.entry_hash
        payload = record.payload
        if record.kind == KIND_ARM_VERSION:
            version = ArmVersion.from_payload(payload)
            state.arm_versions[version.arm_version_id] = version
        elif record.kind == KIND_CUTOFF_CORRECTION:
            correction = CutoffCorrection.from_payload(payload)
            if state.registrations_under.get(correction.arm_version_id, 0) > 0:
                # RC-150: withdrawn from further registrations, with every version whose effective cutoff is
                # composed from the corrected one (RC-156); a replacement version with evidence follows
                state.withdrawn |= _consumers(correction.arm_version_id, state.arm_versions)
            else:  # before any registration the correction amends the declared cutoff and its evidence
                version = state.arm_versions[correction.arm_version_id]
                state.arm_versions[correction.arm_version_id] = replace(
                    version, declared_cutoff=correction.corrected_cutoff, cutoff_evidence_id=correction.evidence_id)
        elif record.kind == KIND_CANDIDATE:
            entry = CandidateEntry.from_payload(payload)
            state.candidates[entry.candidate_id] = entry
            state.candidate_by_event[entry.event_id] = entry
        elif record.kind == KIND_CLUSTER:
            registration = ClusterRegistration.from_payload(payload)
            state.clusters[registration.cluster.cluster_id] = registration
            state.cluster_registered_at[registration.cluster.cluster_id] = parse_timestamp(record.receipt_time)
            for spec in registration.events:
                state.events[spec.event_id] = spec
                state.event_cluster[spec.event_id] = registration.cluster.cluster_id
            for version_id in registration.arm_versions.values():  # a registration counts under every input too
                for consumed in _consumption_closure(version_id, state.arm_versions):
                    state.registrations_under[consumed] = state.registrations_under.get(consumed, 0) + 1
        elif record.kind == KIND_BASE_RATE:
            rate = BaseRate.from_payload(payload)
            state.base_rates[rate.reference_class_id] = rate.rate
        elif record.kind == KIND_FORECAST:
            forecast = Forecast.from_payload(payload)
            received = ReceivedForecast(forecast, record.record_id, parse_timestamp(record.receipt_time))
            key = (forecast.event_id, forecast.arm_id, forecast.slot_id)
            state.submissions[key] = state.submissions.get(key, 0) + 1
            state.forecasts_by_event.setdefault(forecast.event_id, []).append(received)
            spec = state.events[forecast.event_id]
            if spec.issuance_open <= received.receipt <= spec.issuance_close:
                state.forecasts[key] = received  # only a receipt inside the window fills the slot (RC-75, RC-87)
        elif record.kind == KIND_CLAIM:
            claim = ClaimPreregistration.from_payload(payload)
            _check_claim(record, claim, state)
            state.claims[claim.claim_id] = claim
        elif record.kind == KIND_REGISTER:
            register = ConfirmatoryRegister.from_payload(payload)
            _check_register(record, register, state)
            state.register = register
            state.register_seq = record.seq
        elif record.kind == KIND_CALIBRATION:
            calibration = CalibrationRecord.from_payload(payload)
            _check_calibration(record, calibration, state)
            state.calibrations[calibration.calibration_record_id] = calibration
            state.calibration_seq[calibration.calibration_record_id] = record.seq
            state.calibration_by_claim[calibration.claim_id] = calibration.calibration_record_id
        elif record.kind == KIND_BEACON:
            assert isinstance(payload, dict)
            output = BeaconOutput.from_payload(payload["output"])
            seed = _check_beacon(record, output, payload["seed"], state)
            state.beacon_outputs[output.calibration_record_id] = output
            state.beacon_seq[output.calibration_record_id] = record.seq
            state.seeds[output.calibration_record_id] = seed
        elif record.kind == KIND_ROUND_REFUSED:
            assert isinstance(payload, dict)
            output = BeaconOutput.from_payload(payload["output"])
            _check_refused_round(record, output, payload.get("reason"), state)
            state.refused_rounds[output.calibration_record_id] = output
    return state


# Replay re-validates every row that bears on a claim's status or a seed as the registry validated it when it wrote
# the row, so that a row written through the ledger by anything else (a second register, a register after a beacon
# round, a seed not derived from its round) refuses the ledger rather than being read as authority (issue #37,
# pass 4 W2, W3; pass 3 F5). The checks against anchor times are made with the anchors, in ``check_anchor_times``.

def _invalid(record: Record, problem: str) -> Refusal:
    return Refusal("invalid_record", f"{record.kind} {record.record_id} {problem}")


def _check_claim(record: Record, claim: ClaimPreregistration, state: _State) -> None:
    receipt = parse_timestamp(record.receipt_time)
    if record.record_id != _ledger_id("claim", claim.claim_id) or claim.claim_id in state.claims:
        raise _invalid(record, "is not the one record of its claim")
    if claim.population_kind != "fixed_question_set":
        raise _invalid(record, "has a population that is not a fixed question set (18 M-8)")
    if any(other.calibration_record_id == claim.calibration_record_id for other in state.claims.values()):
        raise _invalid(record, "names a calibration record reserved for another claim (18 M-1 (i))")
    if receipt >= claim.period_start or claim.question_set_fixed_at > receipt:
        raise _invalid(record, "was received outside [question set fixed, period start)")


def _check_register(record: Record, register: ConfirmatoryRegister, state: _State) -> None:
    receipt = parse_timestamp(record.receipt_time)
    if record.record_id != _ledger_id("register") or state.register is not None:
        raise _invalid(record, "is a second register, which confers nothing (18 R9)")
    if state.beacon_outputs or state.refused_rounds:
        raise _invalid(record, "follows a beacon round of a calibration record (RC-311)")
    for claim_id in register.confirmatory_claim_ids:
        claim = state.claims.get(claim_id)
        if claim is None or receipt >= claim.period_start:
            raise _invalid(record, f"lists {claim_id}, which is unregistered or whose period has started")


def _check_calibration(record: Record, calibration: CalibrationRecord, state: _State) -> None:
    claim = state.claims.get(calibration.claim_id)
    if record.record_id != _ledger_id("calibration", calibration.calibration_record_id) \
            or calibration.calibration_record_id in state.calibrations \
            or calibration.claim_id in state.calibration_by_claim:
        raise _invalid(record, "is not the one calibration record of its claim")
    if claim is None or claim.calibration_record_id != calibration.calibration_record_id:
        raise _invalid(record, "is not bound both ways to a registered claim (18 M-1 (i))")
    if parse_timestamp(record.receipt_time) >= claim.period_start:
        raise _invalid(record, "was received after its claim's period started")


def _check_round(record: Record, output: BeaconOutput, state: _State, prefix: str) -> CalibrationRecord:
    calibration = state.calibrations.get(output.calibration_record_id)
    if record.record_id != _ledger_id(prefix, output.calibration_record_id) or calibration is None:
        raise _invalid(record, "is not written for a recorded calibration record")
    if (calibration.beacon_id, calibration.round_id) != (output.beacon_id, output.round_id):
        raise _invalid(record, "names a round other than its calibration record's")
    if output.calibration_record_id in state.beacon_outputs or output.calibration_record_id in state.refused_rounds:
        raise _invalid(record, "follows a round already supplied or refused for its calibration record")
    if output.published_at > parse_timestamp(record.receipt_time):
        raise _invalid(record, "was received before its round was published")
    return calibration


def _check_beacon(record: Record, output: BeaconOutput, seed: JsonValue, state: _State) -> str:
    calibration = _check_round(record, output, state, "beacon")
    derived = derive_seed(calibration.to_payload(), output.value)
    if seed != derived:
        raise _invalid(record, "carries a seed not derived from its record and round (RC-187, RC-304)")
    return derived


def _check_refused_round(record: Record, output: BeaconOutput, reason: object, state: _State) -> None:
    _check_round(record, output, state, "round-refused")
    if state.register_seq is None:
        raise _invalid(record, "refuses a round with no register to be anchored before it (RC-311)")
    if reason not in ("round_before_anchor", "register_not_anchored"):
        raise _invalid(record, "names no refusal the registry writes")


def _anchor_time_covering(anchors: tuple[Anchor, ...], seq: int) -> datetime | None:
    for anchor in anchors:
        if anchor.prefix_length >= seq:
            return parse_timestamp(anchor.published_at)
    return None


def check_anchor_times(state: _State) -> None:
    """Every supplied round was published after the anchor of its calibration record, and after the register's
    anchor when the register preceded it (RC-182, RC-304, RC-311). A later anchor only covers more, so a row the
    registry wrote stays valid as anchors settle."""
    for calibration_id, output in state.beacon_outputs.items():
        anchored_at = _anchor_time_covering(state.local_anchors, state.calibration_seq[calibration_id])
        late = anchored_at is None or anchored_at >= output.published_at
        if not late and state.register_seq is not None and state.register_seq < state.beacon_seq[calibration_id]:
            register_anchored_at = _anchor_time_covering(state.local_anchors, state.register_seq)
            late = register_anchored_at is None or register_anchored_at >= output.published_at
        if late:
            raise Refusal("invalid_record", f"the round of {calibration_id} was published before an anchor it "
                          "must follow, and no seed is drawn from it (RC-304, RC-311)")
    for calibration_id, output in state.refused_rounds.items():
        # A round is recorded as refused only when the register was not anchored before it; a row that says so of a
        # round the register's anchor preceded would bar a seed the registry would draw (PR #51 review 4353051504).
        assert state.register_seq is not None  # checked on replay
        register_anchored_at = _anchor_time_covering(state.local_anchors, state.register_seq)
        if register_anchored_at is not None and register_anchored_at < output.published_at:
            raise Refusal("invalid_record", f"the refused round of {calibration_id} was published after the "
                          "register's anchor, so the registry would not have refused it (RC-311)")


class RegistrationRegistry:
    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger
        self._lock = threading.RLock()
        self.before_write: Callable[[], None] | None = None  # test hook, run between the decision and the write

    def state(self) -> _State:
        records, local_anchors, pending_anchors = self._ledger.snapshot()  # one read under the ledger's lock
        state = replay_state(records)
        state.local_anchors = local_anchors
        state.pending_anchors = pending_anchors
        check_anchor_times(state)
        return state

    def _write(self, decide: Callable[[_State, datetime], Write]) -> Record:
        """One read-decide-write: ``decide`` validates against a snapshot and names the record to append; the
        append is made against the snapshot's chain head, and a head that moved (another writer on the same
        ledger, this registry or another) refuses the append, so the decision is recomputed on the new state.
        ``decide`` runs on a clock sample first, to refuse early, and again on the receipt the append assigns,
        which is the decision written: every "before" bound (e_i, the issuance open, a period start, a listing
        time) holds for the record's own receipt, not for an earlier sample (issue #37, C1). The anchors the decision
        read are expected unchanged as well: an anchor that lands between the snapshot and the append moves no chain
        head, and a round recorded as refused for a register the anchor covered would refuse every later replay
        (issue #37, pass 5 R2)."""
        with self._lock:
            for _ in range(8):
                state = self.state()
                now = self._ledger.now()
                kind, record_id, payload = decide(state, now)
                if self.before_write is not None:
                    hook, self.before_write = self.before_write, None
                    hook()
                try:
                    return self._ledger.append(kind, record_id, payload, expected_head=state.head,
                                               admit=lambda receipt: decide(state, receipt),
                                               expected_anchors=(state.local_anchors, state.pending_anchors))
                except Refusal as refusal:
                    if refusal.reason != "stale_head":
                        raise
            raise Refusal("contended", "the ledger kept advancing while the record was being decided")

    # arm versions -------------------------------------------------------------------------------------------

    def register_arm_version(self, version: ArmVersion) -> Record:
        version = ArmVersion.from_payload(_payload_of(version))

        def decide(state: _State, now: datetime) -> Write:
            if version.arm_version_id in state.arm_versions:
                raise Refusal("arm_version_immutable", f"{version.arm_version_id} is already registered")
            for consumed in version.consumes:
                if consumed not in state.arm_versions:
                    raise Refusal("unknown_arm_version", f"{version.arm_version_id} consumes unregistered {consumed}")
                if consumed in state.withdrawn:
                    raise Refusal("arm_version_withdrawn", f"{version.arm_version_id} consumes withdrawn {consumed}, "
                                  "whose declared cutoff was corrected (RC-150, RC-156)")
            return KIND_ARM_VERSION, _ledger_id("arm-version", version.arm_version_id), version.to_payload()

        return self._write(decide)

    def arm_version(self, version_id: str) -> ArmVersion:
        """The version as registered, with any correction made before its first registration applied."""
        version = self.state().arm_versions.get(version_id)
        if version is None:
            raise Refusal("unknown_arm_version", version_id)
        return version

    def correct_cutoff(self, correction: CutoffCorrection) -> tuple[Record, bool]:
        """Record a cutoff correction. Returns the record and whether registrations already existed under the
        version, directly or through a version that consumes it (RC-156): before the first registration the
        correction amends the version's declared cutoff and evidence in place; after it, the version and every
        version that consumes it are withdrawn from further registrations and the claim consequence (RC-150)
        is item 3's."""
        correction = CutoffCorrection.from_payload(_payload_of(correction))
        registered_under = False

        def decide(state: _State, now: datetime) -> Write:
            nonlocal registered_under
            if correction.arm_version_id not in state.arm_versions:
                raise Refusal("unknown_arm_version", correction.arm_version_id)
            if correction.arm_version_id in state.withdrawn:
                raise Refusal("arm_version_withdrawn", f"{correction.arm_version_id} is already withdrawn")
            registered_under = state.registrations_under.get(correction.arm_version_id, 0) > 0
            return (KIND_CUTOFF_CORRECTION,
                    _ledger_id("cutoff-correction", correction.arm_version_id, correction.evidence_id),
                    correction.to_payload())

        record = self._write(decide)
        return record, registered_under

    # candidate log ------------------------------------------------------------------------------------------

    def log_candidate(self, entry: CandidateEntry) -> Record:
        entry = CandidateEntry.from_payload(_payload_of(entry))  # validated in full, a naive time is a Refusal

        def decide(state: _State, now: datetime) -> Write:
            if entry.event_id in state.forecasts_by_event:
                raise Refusal("candidate_after_forecast", f"a forecast on {entry.event_id} already exists (RC-78)")
            if entry.event_id in state.candidate_by_event:
                raise Refusal("candidate_exists", f"{entry.event_id} is already in the candidate log")
            if entry.listed_at > now:
                raise Refusal("future_listing", f"{entry.candidate_id} is listed after its receipt; a listing time is "
                              "at or before the entry's receipt (RC-78)")
            return KIND_CANDIDATE, _ledger_id("candidate", entry.candidate_id), entry.to_payload()

        return self._write(decide)

    def candidate_counts(self) -> dict[str, dict[str, int]]:
        counts: dict[str, dict[str, int]] = {}
        for entry in self.state().candidates.values():
            by_reason = counts.setdefault(entry.decision, {})
            by_reason[entry.reason] = by_reason.get(entry.reason, 0) + 1
        return counts

    # clusters and events ------------------------------------------------------------------------------------

    def commit_base_rate(self, rate: BaseRate) -> Record:
        rate = BaseRate.from_payload(_payload_of(rate))

        def decide(state: _State, now: datetime) -> Write:
            if rate.reference_class_id in state.base_rates:
                raise Refusal("base_rate_immutable", f"{rate.reference_class_id} already has a committed base rate")
            return KIND_BASE_RATE, _ledger_id("base-rate", rate.reference_class_id), rate.to_payload()

        return self._write(decide)

    def register_cluster(self, registration: ClusterRegistration) -> Record:
        """Write the registration record, decided against its own receipt (RC-87, RC-138). Validated as replay
        will read it, so every time is compared in UTC as it is persisted (issue #37, Codex 6)."""
        registration = ClusterRegistration.from_payload(_payload_of(registration))

        def decide(state: _State, now: datetime) -> Write:
            cluster_id = registration.cluster.cluster_id
            if cluster_id in state.clusters:
                raise Refusal("cluster_immutable", f"{cluster_id} is already registered (RC-66)")
            for spec in registration.events:
                candidate = state.candidate_by_event.get(spec.event_id)
                if candidate is None:
                    raise Refusal("no_candidate_entry", f"{spec.event_id} has no prior candidate entry (RC-78)")
                if candidate.decision != "registered":
                    raise Refusal("candidate_not_registered", f"{spec.event_id} was {candidate.decision}")
                if spec.event_id in state.events:
                    raise Refusal("event_registered", f"{spec.event_id} is already a member of {state.event_cluster[spec.event_id]}")
                if now >= spec.earliest_knowable_bound:
                    raise Refusal("registration_after_e_i", f"the registration record would follow e_i of {spec.event_id} (RC-138)")
                if spec.issuance_open < now:
                    raise Refusal("issuance_before_registration", f"{spec.event_id}'s issuance window opens before the registration record (RC-87)")
                if spec.reference_class_id not in state.base_rates:
                    raise Refusal("no_base_rate", f"{spec.event_id}'s reference class has no committed base rate (RC-109)")
            for arm_id, version_id in registration.arm_versions.items():
                version = state.arm_versions.get(version_id)
                if version is None:
                    raise Refusal("unknown_arm_version", f"arm {arm_id} names unregistered {version_id}")
                if version.arm_id != arm_id:
                    raise Refusal("arm_mismatch", f"{version_id} is a version of arm {version.arm_id}, not of {arm_id}")
                if version_id in state.withdrawn:
                    raise Refusal("arm_version_withdrawn", f"{version_id} is withdrawn from registrations (RC-150)")
                cutoff = effective_cutoff(version_id, state.arm_versions)
                for spec in registration.events:
                    if date.fromisoformat(format_timestamp(spec.earliest_knowable_bound)[:10]) <= cutoff:  # UTC
                        raise Refusal("cutoff_after_e_i", f"{spec.event_id}: e_i is not after the effective cutoff "
                                      f"{cutoff.isoformat()} of arm {arm_id} (RC-138)")
            return KIND_CLUSTER, _ledger_id("cluster", cluster_id), registration.to_payload()

        return self._write(decide)

    def event(self, event_id: str) -> EventSpec:
        spec = self.state().events.get(event_id)
        if spec is None:
            raise Refusal("unknown_event", f"{event_id} is not registered")
        return spec

    def request_void(self, request: VoidRequest) -> Record:
        """Logged with its receipt time; it changes no state (RC-85, RC-87)."""
        request = VoidRequest.from_payload(_payload_of(request))

        def decide(state: _State, now: datetime) -> Write:
            if request.event_id not in state.events:
                raise Refusal("unknown_event", f"{request.event_id} is not registered")
            return KIND_VOID_REQUEST, _ledger_id("void-request", request.request_id), request.to_payload()

        return self._write(decide)

    # forecasts ----------------------------------------------------------------------------------------------

    def submit_forecast(self, forecast: Forecast) -> Record:
        """Admit a forecast, validated in full as its payload will be replayed. A receipt inside the issuance
        window fills its (event, arm, slot); one outside the window is kept, labelled by its receipt, and fills
        nothing (RC-75, RC-87)."""
        forecast = Forecast.from_payload(_payload_of(forecast))

        def decide(state: _State, now: datetime) -> Write:
            spec = state.events.get(forecast.event_id)
            if spec is None:
                raise Refusal("before_registration", f"{forecast.event_id} has no registration record (RC-87)")
            registration = state.clusters[state.event_cluster[forecast.event_id]]
            if forecast.arm_id == registration.baseline_arm_id:
                raise Refusal("baseline_not_submittable", "the baseline slot is computed from the committed base rate (RC-109)")
            expected_version = registration.arm_versions.get(forecast.arm_id)
            if expected_version is None:
                raise Refusal("unknown_arm", f"arm {forecast.arm_id} is not pre-registered for {forecast.event_id}")
            if forecast.arm_version_id != expected_version:
                raise Refusal("wrong_arm_version", f"{forecast.arm_id} is pre-registered as {expected_version} (RC-96)")
            if forecast.slot_id not in spec.scoring_slots:
                raise Refusal("unknown_slot", f"{forecast.slot_id} is not a slot of {forecast.event_id} (RC-89)")
            key = (forecast.event_id, forecast.arm_id, forecast.slot_id)
            if key in state.forecasts:
                raise Refusal("slot_occupied", f"slot {forecast.slot_id} of {forecast.arm_id} on {forecast.event_id} is filled (RC-75)")
            record_id = _ledger_id("forecast", forecast.event_id, forecast.arm_id, forecast.slot_id,
                                   str(state.submissions.get(key, 0) + 1))
            return KIND_FORECAST, record_id, forecast.to_payload()

        return self._write(decide)

    def _closed(self, spec: EventSpec, now: datetime) -> bool:
        """Submissions are eligible up to and including the close; reads open strictly after it, so no read can
        precede a submission at the same server time."""
        return now > spec.issuance_close

    def forecasts_of(self, event_id: str) -> tuple[ReceivedForecast, ...]:
        """The event's forecasts, every one with its receipt; sealed until the issuance window has closed, so that
        no arm reads another's forecast while it can still submit (RC-109)."""
        state = self.state()
        spec = state.events.get(event_id)
        if spec is None:
            raise Refusal("unknown_event", f"{event_id} is not registered")
        if not self._closed(spec, self._ledger.now()):
            raise Refusal("read_before_close", "forecasts are sealed until the issuance window has closed (RC-109)")
        return tuple(state.forecasts_by_event.get(event_id, ()))

    def forecasts_for_baseline(self, event_id: str) -> tuple[ReceivedForecast, ...]:
        """The baseline process may read the arms' forecasts only after the issuance close (RC-109)."""
        return self.forecasts_of(event_id)

    def slot_states(self, event_id: str) -> tuple[SlotState, ...]:
        """Every (arm, slot) of the event at the ledger clock: filled, open, or, after the issuance close, an
        abstention; a filled slot's value is shown only after the close; the baseline slot carries the committed
        base rate (RC-109; ``18`` M-5 slot state)."""
        state = self.state()
        spec = state.events.get(event_id)
        if spec is None:
            raise Refusal("unknown_event", f"{event_id} is not registered")
        registration = state.clusters[state.event_cluster[event_id]]
        closed = self._closed(spec, self._ledger.now())
        states: list[SlotState] = []
        for arm_id in sorted(registration.arm_versions):
            for slot_id in spec.scoring_slots:
                if arm_id == registration.baseline_arm_id:
                    states.append(SlotState(event_id, arm_id, slot_id, "baseline", None, state.base_rates[spec.reference_class_id]))
                    continue
                received = state.forecasts.get((event_id, arm_id, slot_id))
                if received is not None:
                    states.append(SlotState(event_id, arm_id, slot_id, "filled", received.record_id,
                                            received.forecast.point if closed else None))
                else:  # a submission outside the window never fills the slot; it is kept as a labelled forecast
                    states.append(SlotState(event_id, arm_id, slot_id, "abstention" if closed else "open"))
        return tuple(states)

    # claims, register, calibration --------------------------------------------------------------------------

    def register_claim(self, claim: ClaimPreregistration) -> Record:
        """A claim is recorded after its question set is fixed and before its evaluation period begins; its
        fields are then fixed (``18`` M-8). Validated in full as its payload will be replayed; its calibration
        record identifier is reserved for it alone (``18`` M-1 (i))."""
        claim = ClaimPreregistration.from_payload(_payload_of(claim))

        def decide(state: _State, now: datetime) -> Write:
            if claim.population_kind != "fixed_question_set":
                raise Refusal("non_confirmatory_population", "a population that is a source listing is not Q (18 M-8)")
            if claim.claim_id in state.claims:
                raise Refusal("claim_immutable", f"{claim.claim_id} is already registered")
            for other in state.claims.values():
                if other.calibration_record_id == claim.calibration_record_id:
                    raise Refusal("calibration_record_reserved", f"{claim.calibration_record_id} is the calibration "
                                  f"record of {other.claim_id}; one record binds one claim (18 M-1 (i))")
            if now >= claim.period_start:
                raise Refusal("late_claim", f"{claim.claim_id}: the claim must be recorded before its period starts")
            if claim.question_set_fixed_at > now:
                raise Refusal("question_set_not_fixed", f"{claim.claim_id}: the question set is fixed before the claim is recorded")
            return KIND_CLAIM, _ledger_id("claim", claim.claim_id), claim.to_payload()

        return self._write(decide)

    def anchor_confirmatory_register(self, register: ConfirmatoryRegister) -> Record:
        """Phase 1's one register, written once, before any beacon output exists and before the evaluation period
        of every claim it lists, naming registered claims only (RC-311, RC-315)."""
        register = ConfirmatoryRegister.from_payload(_payload_of(register))

        def decide(state: _State, now: datetime) -> Write:
            if state.register is not None:
                raise Refusal("register_immutable", "Phase 1 has one confirmatory register; a second or an amendment confers nothing")
            if state.beacon_outputs:
                raise Refusal("register_after_beacon", "the register must be anchored before the beacon round of any calibration record")
            for claim_id in register.confirmatory_claim_ids:
                claim = state.claims.get(claim_id)
                if claim is None:
                    raise Refusal("unknown_claim", f"the register names {claim_id}, which has no pre-registration")
                if now >= claim.period_start:
                    raise Refusal("register_after_period_start", f"the register must precede the evaluation period of {claim_id}")
            return KIND_REGISTER, _ledger_id("register"), register.to_payload()

        try:
            return self._write(decide)
        except Refusal as refusal:
            if refusal.reason == "duplicate_record_id":
                raise Refusal("register_immutable", "Phase 1 has one confirmatory register") from None
            raise

    def claim_status(self, claim_id: str) -> Literal["confirmatory", "exploratory"]:
        """Confirmatory once the one register lists the claim and an anchor covers the register's record, unless a
        recorded beacon round of a calibration record bound to a Phase 1 claim was published at or before that anchor:
        the register was then not anchored before the round of every calibration record, and every claim is
        exploratory (RC-311, ``18`` M-1 (i)). The status does not change: it was exploratory from the anchor on, and
        the registry learns the round's publication time when the round is supplied (issue #37, pass 3 F4)."""
        state = self.state()
        if claim_id not in state.claims:
            raise Refusal("unknown_claim", claim_id)
        register = state.register
        if register is None or state.register_seq is None or claim_id not in register.confirmatory_claim_ids:
            return "exploratory"
        anchored_at = self._anchor_time_covering(state, state.register_seq)
        if anchored_at is None:
            return "exploratory"
        if any(round_.published_at <= anchored_at for round_ in state.refused_rounds.values()):
            return "exploratory"
        return "confirmatory"

    def record_calibration(self, calibration: CalibrationRecord) -> Record:
        """One record per claim, bound both ways, recorded before the claim's evaluation period and before any
        beacon round (RC-304, RC-309)."""
        calibration = CalibrationRecord.from_payload(_payload_of(calibration))

        def decide(state: _State, now: datetime) -> Write:
            claim = state.claims.get(calibration.claim_id)
            if claim is None:
                raise Refusal("unknown_claim", f"{calibration.claim_id} has no pre-registration")
            if claim.calibration_record_id != calibration.calibration_record_id:
                raise Refusal("binding_mismatch", f"the pre-registration of {claim.claim_id} names "
                              f"{claim.calibration_record_id}, not {calibration.calibration_record_id}")
            if calibration.claim_id in state.calibration_by_claim:
                raise Refusal("second_calibration_record", f"{calibration.claim_id} already has its one calibration record")
            if calibration.calibration_record_id in state.calibrations:
                raise Refusal("calibration_record_exists", calibration.calibration_record_id)
            if now >= claim.period_start:
                raise Refusal("late_calibration", f"{calibration.calibration_record_id}: the calibration is recorded "
                              "before the claim's evaluation period")
            return KIND_CALIBRATION, _ledger_id("calibration", calibration.calibration_record_id), calibration.to_payload()

        return self._write(decide)

    @staticmethod
    def _anchor_time_covering(state: _State, seq: int) -> datetime | None:
        return _anchor_time_covering(state.local_anchors, seq)

    def supply_beacon_output(self, output: BeaconOutput) -> tuple[Record, str]:
        """Record the beacon output of a calibration record and derive its seed, in one durable record.

        The output must be of the beacon and the round the record names, published after the record's anchor and
        not after the ledger clock; the register, if any, must be anchored before the round too; a second output
        for the record is refused; the seed is SHA-256(record ‖ value), derived here and never supplied
        (RC-187, RC-304, RC-311).
        """
        output = BeaconOutput.from_payload(_payload_of(output))
        seed = ""
        refusal: Refusal | None = None

        def decide(state: _State, now: datetime) -> Write:
            nonlocal seed, refusal
            refusal = None  # decided afresh on every attempt
            calibration = state.calibrations.get(output.calibration_record_id)
            if calibration is None:
                raise Refusal("unknown_calibration_record", output.calibration_record_id)
            if output.calibration_record_id in state.beacon_outputs:
                raise Refusal("second_seed", "the calibration runs once on one beacon output (RC-187, RC-304)")
            if calibration.beacon_id != output.beacon_id:
                raise Refusal("wrong_beacon", f"the record names beacon {calibration.beacon_id}")
            if calibration.round_id != output.round_id:
                raise Refusal("wrong_round", f"the record names round {calibration.round_id} of {calibration.beacon_id}")
            if output.calibration_record_id in state.refused_rounds:
                # The round is on record as published before the register's anchor; no later supply of it, whatever
                # time or value it claims, is weighed again (PR #48 review 4352111655).
                raise Refusal("register_not_anchored", "the round was published before the confirmatory register's "
                              "anchor and is recorded as refused (RC-311)")
            if output.published_at > now:
                raise Refusal("future_round", "a round is supplied after its publication, never before")
            anchored_at = self._anchor_time_covering(state, state.calibration_seq[output.calibration_record_id])
            calibration_late = anchored_at is None or anchored_at >= output.published_at
            register_late = register_pending = False
            if state.register_seq is not None:
                register_anchored_at = self._anchor_time_covering(state, state.register_seq)
                register_late = register_anchored_at is None or register_anchored_at >= output.published_at
                # An unconfirmed anchor attempt covering the register before the round may have landed: the register
                # is then not known to be late, and nothing that binds is written until the attempt settles (issue
                # #37, pass 4 R1).
                register_pending = register_late and any(
                    anchor.prefix_length >= state.register_seq and parse_timestamp(anchor.published_at) < output.published_at
                    for anchor in state.pending_anchors)
            if register_pending:
                if calibration_late:
                    raise Refusal("round_before_anchor", "the beacon round must be published after the record's "
                                  "anchor (RC-182, RC-304)")
                raise Refusal("anchor_pending", "the anchor of the confirmatory register is not yet confirmed; the "
                              "round is weighed once it settles (RC-311)")
            if calibration_late:
                refusal = Refusal("round_before_anchor", "the beacon round must be published after the record's "
                                  "anchor (RC-182, RC-304)")
            elif register_late:
                refusal = Refusal("register_not_anchored", "the confirmatory register must be anchored before the "
                                  "round (RC-311)")
            if register_late:
                # A round published before the register's anchor is written, at its receipt, whichever timing check
                # refuses it first: it makes every claim exploratory and claim_status must read it (issue #37, pass 3
                # F4; PR #48 review 4352111663). A round refused only for the calibration record's anchor is not
                # written, so that a supplier's wrong time can still be corrected.
                assert refusal is not None
                return (KIND_ROUND_REFUSED, _ledger_id("round-refused", output.calibration_record_id),
                        {"output": output.to_payload(), "reason": refusal.reason})
            if refusal is not None:
                raise refusal
            seed = derive_seed(calibration.to_payload(), output.value)
            payload: Payload = {"output": output.to_payload(), "seed": seed}
            return KIND_BEACON, _ledger_id("beacon", output.calibration_record_id), payload

        record = self._write(decide)
        if refusal is not None:
            raise refusal
        return record, seed

    def seed_of(self, calibration_record_id: str) -> str:
        seed = self.state().seeds.get(calibration_record_id)
        if seed is None:
            raise Refusal("no_seed", f"{calibration_record_id} has no beacon output yet; no draw before the round (RC-187)")
        return seed
