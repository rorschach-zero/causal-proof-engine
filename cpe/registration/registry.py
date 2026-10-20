"""The pre-registration registry on the ledger. State is rebuilt from the ledger on every operation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from cpe.clock import parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import Ledger, Record
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
from cpe.schemas.common import Payload, timestamp_payload

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
KIND_SEED = "calibration_seed"

SlotStatus = Literal["filled", "open", "abstention", "baseline"]


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
    claims: dict[str, ClaimPreregistration] = field(default_factory=dict)
    register: ConfirmatoryRegister | None = None
    register_seq: int | None = None
    calibrations: dict[str, CalibrationRecord] = field(default_factory=dict)
    calibration_seq: dict[str, int] = field(default_factory=dict)
    calibration_by_claim: dict[str, str] = field(default_factory=dict)
    beacon_outputs: dict[str, BeaconOutput] = field(default_factory=dict)
    seeds: dict[str, str] = field(default_factory=dict)


def replay_state(records: tuple[Record, ...]) -> _State:
    state = _State()
    for record in records:
        payload = record.payload
        if record.kind == KIND_ARM_VERSION:
            version = ArmVersion.from_payload(payload)
            state.arm_versions[version.arm_version_id] = version
        elif record.kind == KIND_CUTOFF_CORRECTION:
            state.withdrawn.add(CutoffCorrection.from_payload(payload).arm_version_id)
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
            for version_id in registration.arm_versions.values():
                state.registrations_under[version_id] = state.registrations_under.get(version_id, 0) + 1
        elif record.kind == KIND_BASE_RATE:
            rate = BaseRate.from_payload(payload)
            state.base_rates[rate.reference_class_id] = rate.rate
        elif record.kind == KIND_FORECAST:
            forecast = Forecast.from_payload(payload)
            received = ReceivedForecast(forecast, record.record_id, parse_timestamp(record.receipt_time))
            state.forecasts[(forecast.event_id, forecast.arm_id, forecast.slot_id)] = received
            state.forecasts_by_event.setdefault(forecast.event_id, []).append(received)
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
            output = BeaconOutput.from_payload(payload)
            state.beacon_outputs[output.calibration_record_id] = output
        elif record.kind == KIND_SEED:
            assert isinstance(payload, dict)
            state.seeds[str(payload["calibration_record_id"])] = str(payload["seed"])
    return state


class RegistrationRegistry:
    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger

    def state(self) -> _State:
        return replay_state(self._ledger.records())

    # arm versions -------------------------------------------------------------------------------------------

    def register_arm_version(self, version: ArmVersion) -> Record:
        state = self.state()
        if version.arm_version_id in state.arm_versions:
            raise Refusal("arm_version_immutable", f"{version.arm_version_id} is already registered")
        for consumed in version.consumes:
            if consumed not in state.arm_versions:
                raise Refusal("unknown_arm_version", f"{version.arm_version_id} consumes unregistered {consumed}")
        return self._ledger.append(KIND_ARM_VERSION, f"arm-version:{version.arm_version_id}", version.to_payload())

    def correct_cutoff(self, correction: CutoffCorrection) -> tuple[Record, bool]:
        """Record a cutoff correction. Returns the record and whether registrations already existed under the
        version: before the first registration the version is simply withdrawn and replaced by a new one; after
        it, the version is withdrawn from further registrations and the claim consequence (RC-150) is item 3's."""
        state = self.state()
        if correction.arm_version_id not in state.arm_versions:
            raise Refusal("unknown_arm_version", correction.arm_version_id)
        if correction.arm_version_id in state.withdrawn:
            raise Refusal("arm_version_withdrawn", f"{correction.arm_version_id} is already withdrawn")
        registered_under = state.registrations_under.get(correction.arm_version_id, 0) > 0
        record = self._ledger.append(KIND_CUTOFF_CORRECTION, f"cutoff-correction:{correction.arm_version_id}",
                                     correction.to_payload())
        return record, registered_under

    # candidate log ------------------------------------------------------------------------------------------

    def log_candidate(self, entry: CandidateEntry) -> Record:
        state = self.state()
        if entry.event_id in state.forecasts_by_event:
            raise Refusal("candidate_after_forecast", f"a forecast on {entry.event_id} already exists (RC-78)")
        if entry.event_id in state.candidate_by_event:
            raise Refusal("candidate_exists", f"{entry.event_id} is already in the candidate log")
        return self._ledger.append(KIND_CANDIDATE, f"candidate:{entry.candidate_id}", entry.to_payload())

    def candidate_counts(self) -> dict[str, dict[str, int]]:
        counts: dict[str, dict[str, int]] = {}
        for entry in self.state().candidates.values():
            by_reason = counts.setdefault(entry.decision, {})
            by_reason[entry.reason] = by_reason.get(entry.reason, 0) + 1
        return counts

    # clusters and events ------------------------------------------------------------------------------------

    def commit_base_rate(self, rate: BaseRate) -> Record:
        if rate.reference_class_id in self.state().base_rates:
            raise Refusal("base_rate_immutable", f"{rate.reference_class_id} already has a committed base rate")
        return self._ledger.append(KIND_BASE_RATE, f"base-rate:{rate.reference_class_id}", rate.to_payload())

    def register_cluster(self, registration: ClusterRegistration, now: datetime) -> Record:
        state = self.state()
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
            if version_id in state.withdrawn:
                raise Refusal("arm_version_withdrawn", f"{version_id} is withdrawn from registrations (RC-150)")
            cutoff = effective_cutoff(version_id, state.arm_versions)
            for spec in registration.events:
                if spec.earliest_knowable_bound.date() <= cutoff:
                    raise Refusal("cutoff_after_e_i", f"{spec.event_id}: e_i is not after the effective cutoff "
                                  f"{cutoff.isoformat()} of arm {arm_id} (RC-138)")
        return self._ledger.append(KIND_CLUSTER, f"cluster:{cluster_id}", registration.to_payload())

    def event(self, event_id: str) -> EventSpec:
        spec = self.state().events.get(event_id)
        if spec is None:
            raise Refusal("unknown_event", f"{event_id} is not registered")
        return spec

    def request_void(self, request: VoidRequest) -> Record:
        """Logged with its receipt time; it changes no state (RC-85, RC-87)."""
        if request.event_id not in self.state().events:
            raise Refusal("unknown_event", f"{request.event_id} is not registered")
        return self._ledger.append(KIND_VOID_REQUEST, f"void-request:{request.request_id}", request.to_payload())

    # forecasts ----------------------------------------------------------------------------------------------

    def submit_forecast(self, forecast: Forecast) -> Record:
        state = self.state()
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
        record_id = f"forecast:{forecast.event_id}:{forecast.arm_id}:{forecast.slot_id}"
        return self._ledger.append(KIND_FORECAST, record_id, forecast.to_payload())

    def forecasts_of(self, event_id: str) -> tuple[ReceivedForecast, ...]:
        return tuple(self.state().forecasts_by_event.get(event_id, ()))

    def forecasts_for_baseline(self, event_id: str, now: datetime) -> tuple[ReceivedForecast, ...]:
        """The baseline process may read the arms' forecasts only after the issuance close (RC-109)."""
        spec = self.event(event_id)
        if now < spec.issuance_close:
            raise Refusal("read_before_close", "the baseline process reads no forecast before the issuance close (RC-109)")
        return self.forecasts_of(event_id)

    def slot_states(self, event_id: str, now: datetime) -> tuple[SlotState, ...]:
        """Every (arm, slot) of the event: filled, open, or, after the issuance close, an abstention; the
        baseline slot carries the committed base rate (RC-109; ``18`` M-5 slot state)."""
        state = self.state()
        spec = state.events.get(event_id)
        if spec is None:
            raise Refusal("unknown_event", f"{event_id} is not registered")
        registration = state.clusters[state.event_cluster[event_id]]
        closed = now >= spec.issuance_close
        states: list[SlotState] = []
        for arm_id in sorted(registration.arm_versions):
            for slot_id in spec.scoring_slots:
                if arm_id == registration.baseline_arm_id:
                    states.append(SlotState(event_id, arm_id, slot_id, "baseline", None, state.base_rates[spec.reference_class_id]))
                    continue
                received = state.forecasts.get((event_id, arm_id, slot_id))
                if received is not None and spec.issuance_open <= received.receipt <= spec.issuance_close:
                    states.append(SlotState(event_id, arm_id, slot_id, "filled", received.record_id, received.forecast.point))
                else:  # a submission outside the window never fills the slot; it is kept as a labelled forecast
                    states.append(SlotState(event_id, arm_id, slot_id, "abstention" if closed else "open"))
        return tuple(states)

    # claims, register, calibration --------------------------------------------------------------------------

    def register_claim(self, claim: ClaimPreregistration) -> Record:
        state = self.state()
        if claim.population_kind != "fixed_question_set":
            raise Refusal("non_confirmatory_population", "a population that is a source listing is not Q (18 M-8)")
        if claim.claim_id in state.claims:
            raise Refusal("claim_immutable", f"{claim.claim_id} is already registered")
        return self._ledger.append(KIND_CLAIM, f"claim:{claim.claim_id}", claim.to_payload())

    def anchor_confirmatory_register(self, register: ConfirmatoryRegister) -> Record:
        """Phase 1's one register, written once, before any beacon output exists (RC-311, RC-315)."""
        state = self.state()
        if state.register is not None:
            raise Refusal("register_immutable", "Phase 1 has one confirmatory register; a second or an amendment confers nothing")
        if state.beacon_outputs:
            raise Refusal("register_after_beacon", "the register must be anchored before the beacon round of any calibration record")
        return self._ledger.append(KIND_REGISTER, f"register:{register.register_id}", register.to_payload())

    def claim_status(self, claim_id: str) -> Literal["confirmatory", "exploratory"]:
        state = self.state()
        if claim_id not in state.claims:
            raise Refusal("unknown_claim", claim_id)
        if state.register is not None and claim_id in state.register.confirmatory_claim_ids:
            return "confirmatory"
        return "exploratory"

    def record_calibration(self, calibration: CalibrationRecord) -> Record:
        """One record per claim, bound both ways before any beacon round (RC-304, RC-309)."""
        state = self.state()
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
        return self._ledger.append(KIND_CALIBRATION, f"calibration:{calibration.calibration_record_id}",
                                   calibration.to_payload())

    def _anchor_time_covering(self, seq: int) -> datetime | None:
        for anchor in self._ledger.local_anchors():
            if anchor.prefix_length >= seq:
                return parse_timestamp(anchor.published_at)
        return None

    def supply_beacon_output(self, output: BeaconOutput) -> tuple[Record, str]:
        """Record the beacon output of a calibration record and derive its seed.

        The record must lie inside an anchored prefix whose anchor precedes the round's publication; the register,
        if any, must be anchored before the round too; a second output for the record is refused; the seed is
        SHA-256(record ‖ value) and never supplied (RC-187, RC-304, RC-311).
        """
        state = self.state()
        calibration = state.calibrations.get(output.calibration_record_id)
        if calibration is None:
            raise Refusal("unknown_calibration_record", output.calibration_record_id)
        if calibration.beacon_id != output.beacon_id:
            raise Refusal("wrong_beacon", f"the record names beacon {calibration.beacon_id}")
        if output.calibration_record_id in state.beacon_outputs:
            raise Refusal("second_seed", "the calibration runs once on one beacon output (RC-187, RC-304)")
        anchored_at = self._anchor_time_covering(state.calibration_seq[output.calibration_record_id])
        if anchored_at is None or anchored_at >= output.published_at:
            raise Refusal("round_before_anchor", "the beacon round must be published after the record's anchor (RC-182, RC-304)")
        if state.register_seq is not None:
            register_anchored_at = self._anchor_time_covering(state.register_seq)
            if register_anchored_at is None or register_anchored_at >= output.published_at:
                raise Refusal("register_not_anchored", "the confirmatory register must be anchored before the round (RC-311)")
        record = self._ledger.append(KIND_BEACON, f"beacon:{output.calibration_record_id}", output.to_payload())
        seed = derive_seed(calibration.to_payload(), output.value)
        payload: Payload = {"calibration_record_id": output.calibration_record_id, "seed": seed,
                            "derived_at": timestamp_payload(parse_timestamp(record.receipt_time))}
        self._ledger.append(KIND_SEED, f"seed:{output.calibration_record_id}", payload)
        return record, seed

    def seed_of(self, calibration_record_id: str) -> str:
        seed = self.state().seeds.get(calibration_record_id)
        if seed is None:
            raise Refusal("no_seed", f"{calibration_record_id} has no beacon output yet; no draw before the round (RC-187)")
        return seed
