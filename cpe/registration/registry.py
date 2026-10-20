"""The pre-registration registry on the ledger. State is rebuilt from the ledger on every operation; every time
comes from the ledger's clock; every write names the chain head it was decided on, so a decision no longer valid
against a record another writer admitted in between is recomputed, never committed."""
from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Literal

from cpe.canonical import JsonValue, digest_of
from cpe.clock import parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Ledger, Record
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
    seeds: dict[str, str] = field(default_factory=dict)


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
            state.claims[claim.claim_id] = claim
        elif record.kind == KIND_REGISTER:
            state.register = ConfirmatoryRegister.from_payload(payload)
            state.register_seq = record.seq
        elif record.kind == KIND_CALIBRATION:
            calibration = CalibrationRecord.from_payload(payload)
            state.calibrations[calibration.calibration_record_id] = calibration
            state.calibration_seq[calibration.calibration_record_id] = record.seq
            state.calibration_by_claim[calibration.claim_id] = calibration.calibration_record_id
        elif record.kind == KIND_BEACON:
            assert isinstance(payload, dict)
            output = BeaconOutput.from_payload(payload["output"])
            state.beacon_outputs[output.calibration_record_id] = output
            state.seeds[output.calibration_record_id] = str(payload["seed"])
    return state


class RegistrationRegistry:
    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger
        self._lock = threading.RLock()
        self.before_write: Callable[[], None] | None = None  # test hook, run between the decision and the write

    def state(self) -> _State:
        return replay_state(self._ledger.records())

    def _write(self, decide: Callable[[_State, datetime], Write]) -> Record:
        """One read-decide-write: ``decide`` validates against a snapshot and names the record to append; the
        append is made against the snapshot's chain head, and a head that moved (another writer on the same
        ledger, this registry or another) refuses the append, so the decision is recomputed on the new state."""
        with self._lock:
            for _ in range(8):
                state = self.state()
                now = self._ledger.now()
                kind, record_id, payload = decide(state, now)
                if self.before_write is not None:
                    hook, self.before_write = self.before_write, None
                    hook()
                try:
                    return self._ledger.append(kind, record_id, payload, expected_head=state.head)
                except Refusal as refusal:
                    if refusal.reason != "stale_head":
                        raise
            raise Refusal("contended", "the ledger kept advancing while the record was being decided")

    # arm versions -------------------------------------------------------------------------------------------

    def register_arm_version(self, version: ArmVersion) -> Record:
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
        def decide(state: _State, now: datetime) -> Write:
            if entry.event_id in state.forecasts_by_event:
                raise Refusal("candidate_after_forecast", f"a forecast on {entry.event_id} already exists (RC-78)")
            if entry.event_id in state.candidate_by_event:
                raise Refusal("candidate_exists", f"{entry.event_id} is already in the candidate log")
            if entry.listed_at > now:
                raise Refusal("future_listing", f"{entry.candidate_id} is listed after the ledger clock; a listing "
                              "time is at or before the entry's receipt (RC-78)")
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
        def decide(state: _State, now: datetime) -> Write:
            if rate.reference_class_id in state.base_rates:
                raise Refusal("base_rate_immutable", f"{rate.reference_class_id} already has a committed base rate")
            return KIND_BASE_RATE, _ledger_id("base-rate", rate.reference_class_id), rate.to_payload()

        return self._write(decide)

    def register_cluster(self, registration: ClusterRegistration) -> Record:
        """Write the registration record, admitted against the ledger clock: the same server time becomes the
        record's receipt (RC-87, RC-138)."""
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
                    if spec.earliest_knowable_bound.date() <= cutoff:
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
        forecast = Forecast.from_payload(forecast.to_payload())

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
        claim = ClaimPreregistration.from_payload(claim.to_payload())

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
        """Confirmatory once the one register lists the claim and an anchor covers the register's record."""
        state = self.state()
        if claim_id not in state.claims:
            raise Refusal("unknown_claim", claim_id)
        if (state.register is not None and state.register_seq is not None
                and claim_id in state.register.confirmatory_claim_ids
                and self._anchor_time_covering(state.register_seq) is not None):
            return "confirmatory"
        return "exploratory"

    def record_calibration(self, calibration: CalibrationRecord) -> Record:
        """One record per claim, bound both ways, recorded before the claim's evaluation period and before any
        beacon round (RC-304, RC-309)."""
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

    def _anchor_time_covering(self, seq: int) -> datetime | None:
        for anchor in self._ledger.local_anchors():
            if anchor.prefix_length >= seq:
                return parse_timestamp(anchor.published_at)
        return None

    def supply_beacon_output(self, output: BeaconOutput) -> tuple[Record, str]:
        """Record the beacon output of a calibration record and derive its seed, in one durable record.

        The output must be of the beacon and the round the record names, published after the record's anchor and
        not after the ledger clock; the register, if any, must be anchored before the round too; a second output
        for the record is refused; the seed is SHA-256(record ‖ value), derived here and never supplied
        (RC-187, RC-304, RC-311).
        """
        seed = ""

        def decide(state: _State, now: datetime) -> Write:
            nonlocal seed
            calibration = state.calibrations.get(output.calibration_record_id)
            if calibration is None:
                raise Refusal("unknown_calibration_record", output.calibration_record_id)
            if output.calibration_record_id in state.beacon_outputs:
                raise Refusal("second_seed", "the calibration runs once on one beacon output (RC-187, RC-304)")
            if calibration.beacon_id != output.beacon_id:
                raise Refusal("wrong_beacon", f"the record names beacon {calibration.beacon_id}")
            if calibration.round_id != output.round_id:
                raise Refusal("wrong_round", f"the record names round {calibration.round_id} of {calibration.beacon_id}")
            if output.published_at > now:
                raise Refusal("future_round", "a round is supplied after its publication, never before")
            anchored_at = self._anchor_time_covering(state.calibration_seq[output.calibration_record_id])
            if anchored_at is None or anchored_at >= output.published_at:
                raise Refusal("round_before_anchor", "the beacon round must be published after the record's anchor (RC-182, RC-304)")
            if state.register_seq is not None:
                register_anchored_at = self._anchor_time_covering(state.register_seq)
                if register_anchored_at is None or register_anchored_at >= output.published_at:
                    raise Refusal("register_not_anchored", "the confirmatory register must be anchored before the round (RC-311)")
            seed = derive_seed(calibration.to_payload(), output.value)
            payload: Payload = {"output": output.to_payload(), "seed": seed}
            return KIND_BEACON, _ledger_id("beacon", output.calibration_record_id), payload

        record = self._write(decide)
        return record, seed

    def seed_of(self, calibration_record_id: str) -> str:
        seed = self.state().seeds.get(calibration_record_id)
        if seed is None:
            raise Refusal("no_seed", f"{calibration_record_id} has no beacon output yet; no draw before the round (RC-187)")
        return seed
