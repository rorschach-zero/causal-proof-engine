"""Records of the pre-registration registry. Owner fields (OD4, OD5, OD11) are named values, never chosen here."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal, cast

from cpe.errors import Refusal
from cpe.schemas import ClusterRecord, EventSpec
from cpe.schemas.common import (
    identifier_list,
    require_text,
    Payload,
    require_date,
    require_digest,
    require_identifier,
    require_identifier_tuple,
    require_keys,
    require_mapping,
    require_non_negative_int,
    require_probability,
    require_timestamp,
    timestamp_payload,
)

CandidateDecision = Literal["registered", "rejected", "sampled-out"]
_CANDIDATE_KEYS = frozenset({"candidate_id", "event_id", "source_id", "listed_at", "decision", "reason"})


def _choice(value: object, field: str, allowed: tuple[str, ...]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise Refusal("invalid_choice", f"{field} must be one of {', '.join(allowed)}")
    return value


@dataclass(frozen=True)
class CandidateEntry:
    """One candidate of the log, recorded with its decision and reason before any forecast exists (RC-78)."""

    candidate_id: str
    event_id: str
    source_id: str
    listed_at: datetime
    decision: CandidateDecision
    reason: str

    @classmethod
    def from_payload(cls, payload: object) -> CandidateEntry:
        m = require_mapping(payload, "CandidateEntry")
        require_keys(m, "CandidateEntry", _CANDIDATE_KEYS, frozenset())
        return cls(require_identifier(m["candidate_id"], "candidate_id"), require_identifier(m["event_id"], "event_id"),
                   require_identifier(m["source_id"], "source_id"), require_timestamp(m["listed_at"], "listed_at"),
                   cast(CandidateDecision, _choice(m["decision"], "decision", ("registered", "rejected", "sampled-out"))),
                   require_text(m["reason"], "reason"))

    def to_payload(self) -> Payload:
        return {"candidate_id": self.candidate_id, "event_id": self.event_id, "source_id": self.source_id,
                "listed_at": timestamp_payload(self.listed_at), "decision": self.decision, "reason": self.reason}


_CLUSTER_KEYS = frozenset({"cluster", "events", "arm_versions", "baseline_arm_id"})
FULL_ARM_ID = "FULL"  # the composite arm every registration pre-registers (``17`` arms; the FULL slot is never absent)


@dataclass(frozen=True)
class ClusterRegistration:
    """The cluster registration record: members, pre-declared VOID set, the arm version pre-registered per arm."""

    cluster: ClusterRecord
    events: tuple[EventSpec, ...]
    arm_versions: dict[str, str]
    baseline_arm_id: str

    def __post_init__(self) -> None:
        ids = tuple(e.event_id for e in self.events)
        if sorted(ids) != sorted(self.cluster.member_event_ids):
            raise Refusal("invalid_cluster", "the event specifications must be exactly the cluster's members")
        for spec in self.events:
            if spec.cluster_id != self.cluster.cluster_id:
                raise Refusal("invalid_cluster", f"{spec.event_id} names cluster {spec.cluster_id}")
        if self.baseline_arm_id not in self.arm_versions:
            raise Refusal("invalid_cluster", "the baseline arm must be among the pre-registered arms")
        if FULL_ARM_ID not in self.arm_versions:
            raise Refusal("invalid_cluster", f"the {FULL_ARM_ID} arm is mandatory in every registration")
        if self.baseline_arm_id == FULL_ARM_ID:  # FULL is the composite arm, never the base-rate slot (issue #37)
            raise Refusal("invalid_cluster", f"the {FULL_ARM_ID} arm cannot be the baseline arm (``18`` M-5)")

    @classmethod
    def from_payload(cls, payload: object) -> ClusterRegistration:
        m = require_mapping(payload, "ClusterRegistration")
        require_keys(m, "ClusterRegistration", _CLUSTER_KEYS, frozenset())
        versions_raw = require_mapping(m["arm_versions"], "arm_versions")
        versions = {require_identifier(k, "arm_id"): require_identifier(v, f"arm_versions[{k}]") for k, v in versions_raw.items()}
        events_raw = m["events"]
        if not isinstance(events_raw, list):
            raise Refusal("invalid_list", "events must be a list")
        return cls(ClusterRecord.from_payload(m["cluster"]), tuple(EventSpec.from_payload(e) for e in events_raw),
                   versions, require_identifier(m["baseline_arm_id"], "baseline_arm_id"))

    def to_payload(self) -> Payload:
        return {"cluster": self.cluster.to_payload(), "events": [e.to_payload() for e in self.events],
                "arm_versions": dict(sorted(self.arm_versions.items())), "baseline_arm_id": self.baseline_arm_id}


_VOID_KEYS = frozenset({"request_id", "event_id", "reason"})


@dataclass(frozen=True)
class VoidRequest:
    """A VOID request after registration: logged, never acted on (RC-85, RC-87)."""

    request_id: str
    event_id: str
    reason: str

    @classmethod
    def from_payload(cls, payload: object) -> VoidRequest:
        m = require_mapping(payload, "VoidRequest")
        require_keys(m, "VoidRequest", _VOID_KEYS, frozenset())
        return cls(require_identifier(m["request_id"], "request_id"), require_identifier(m["event_id"], "event_id"),
                   require_text(m["reason"], "reason"))

    def to_payload(self) -> Payload:
        return {"request_id": self.request_id, "event_id": self.event_id, "reason": self.reason}


@dataclass(frozen=True)
class BaseRate:
    """Committed Design C base rate of a reference class, reference data from which the baseline slot is filled."""

    reference_class_id: str
    rate: float

    def __post_init__(self) -> None:
        require_identifier(self.reference_class_id, "reference_class_id")
        require_probability(self.rate, "rate")

    @classmethod
    def from_payload(cls, payload: object) -> BaseRate:
        m = require_mapping(payload, "BaseRate")
        require_keys(m, "BaseRate", frozenset({"reference_class_id", "rate"}), frozenset())
        return cls(require_identifier(m["reference_class_id"], "reference_class_id"), require_probability(m["rate"], "rate"))

    def to_payload(self) -> Payload:
        return {"reference_class_id": self.reference_class_id, "rate": self.rate}


_CORRECTION_KEYS = frozenset({"arm_version_id", "corrected_cutoff", "evidence_id"})


@dataclass(frozen=True)
class CutoffCorrection:
    """A correction of an arm version's declared cutoff (RC-150)."""

    arm_version_id: str
    corrected_cutoff: date
    evidence_id: str

    @classmethod
    def from_payload(cls, payload: object) -> CutoffCorrection:
        m = require_mapping(payload, "CutoffCorrection")
        require_keys(m, "CutoffCorrection", _CORRECTION_KEYS, frozenset())
        return cls(require_identifier(m["arm_version_id"], "arm_version_id"),
                   require_date(m["corrected_cutoff"], "corrected_cutoff"), require_identifier(m["evidence_id"], "evidence_id"))

    def to_payload(self) -> Payload:
        return {"arm_version_id": self.arm_version_id, "corrected_cutoff": self.corrected_cutoff.isoformat(),
                "evidence_id": self.evidence_id}


Weighting = Literal["period-balanced", "event-weighted"]
PopulationKind = Literal["fixed_question_set", "source_listing"]
_CLAIM_KEYS = frozenset({
    "claim_id", "population_kind", "question_set_id", "holder_id", "question_set_fixed_at", "period_start",
    "period_end", "weighting", "family_order", "validity_class_ids", "calibration_record_id",
})


@dataclass(frozen=True)
class ClaimPreregistration:
    """The pre-registration of one confirmatory or exploratory claim (``18`` section 6 claim wording, OD11 (b)).

    Field values (Q, its holder, the period, the weighting, the family order, the validity classes) are the
    owner's; the registry checks structure, uniqueness and binding only.
    """

    claim_id: str
    population_kind: PopulationKind
    question_set_id: str
    holder_id: str
    question_set_fixed_at: datetime
    period_start: datetime
    period_end: datetime
    weighting: Weighting
    family_order: tuple[str, ...]
    validity_class_ids: tuple[str, ...]
    calibration_record_id: str

    def __post_init__(self) -> None:
        if self.period_start >= self.period_end:
            raise Refusal("invalid_window", "period_start must precede period_end")
        if self.question_set_fixed_at >= self.period_start:
            raise Refusal("invalid_window", "the question set is fixed before the evaluation period starts")
        if not self.family_order:
            raise Refusal("invalid_family", "a claim names at least one fixed-sequence component (18 M-5)")
        if len(self.validity_class_ids) != len(self.family_order):
            raise Refusal("invalid_family", "one validity class per fixed-sequence component (RC-295)")

    @classmethod
    def from_payload(cls, payload: object) -> ClaimPreregistration:
        m = require_mapping(payload, "ClaimPreregistration")
        require_keys(m, "ClaimPreregistration", _CLAIM_KEYS, frozenset())
        return cls(
            require_identifier(m["claim_id"], "claim_id"),
            cast(PopulationKind, _choice(m["population_kind"], "population_kind", ("fixed_question_set", "source_listing"))),
            require_identifier(m["question_set_id"], "question_set_id"),
            require_identifier(m["holder_id"], "holder_id"),
            require_timestamp(m["question_set_fixed_at"], "question_set_fixed_at"),
            require_timestamp(m["period_start"], "period_start"),
            require_timestamp(m["period_end"], "period_end"),
            cast(Weighting, _choice(m["weighting"], "weighting", ("period-balanced", "event-weighted"))),
            require_identifier_tuple(m["family_order"], "family_order", allow_empty=False),
            require_identifier_tuple(m["validity_class_ids"], "validity_class_ids", allow_empty=False),
            require_identifier(m["calibration_record_id"], "calibration_record_id"),
        )

    def to_payload(self) -> Payload:
        return {
            "claim_id": self.claim_id, "population_kind": self.population_kind, "question_set_id": self.question_set_id,
            "holder_id": self.holder_id, "question_set_fixed_at": timestamp_payload(self.question_set_fixed_at),
            "period_start": timestamp_payload(self.period_start), "period_end": timestamp_payload(self.period_end),
            "weighting": self.weighting, "family_order": identifier_list(self.family_order, "family_order"),
            "validity_class_ids": identifier_list(self.validity_class_ids, "validity_class_ids"), "calibration_record_id": self.calibration_record_id,
        }


_REGISTER_KEYS = frozenset({"register_id", "s_max", "confirmatory_claim_ids"})


@dataclass(frozen=True)
class ConfirmatoryRegister:
    """Phase 1's one confirmatory register: S_max and the confirmatory claims by identifier (RC-311, RC-315)."""

    register_id: str
    s_max: int
    confirmatory_claim_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if isinstance(self.s_max, bool) or not isinstance(self.s_max, int) or self.s_max < 1:
            raise Refusal("invalid_register", "S_max is an integer of at least 1")
        if len(self.confirmatory_claim_ids) > self.s_max:
            raise Refusal("invalid_register", "the register lists at most S_max confirmatory claims")

    @classmethod
    def from_payload(cls, payload: object) -> ConfirmatoryRegister:
        m = require_mapping(payload, "ConfirmatoryRegister")
        require_keys(m, "ConfirmatoryRegister", _REGISTER_KEYS, frozenset())
        return cls(require_identifier(m["register_id"], "register_id"), require_non_negative_int(m["s_max"], "s_max"),
                   require_identifier_tuple(m["confirmatory_claim_ids"], "confirmatory_claim_ids", allow_empty=True))

    def to_payload(self) -> Payload:
        return {"register_id": self.register_id, "s_max": self.s_max,
                "confirmatory_claim_ids": identifier_list(self.confirmatory_claim_ids, "confirmatory_claim_ids")}


_CALIBRATION_KEYS = frozenset({
    "calibration_record_id", "claim_id", "algorithm_id", "calibration_size", "budget", "beacon_id", "round_id",
})


@dataclass(frozen=True)
class CalibrationRecord:
    """The calibration record of one claim: algorithm, size, budget, and the beacon round it will read, named
    before the round is published so that no round can be chosen for its value (RC-304, RC-309)."""

    calibration_record_id: str
    claim_id: str
    algorithm_id: str
    calibration_size: int
    budget: float
    beacon_id: str
    round_id: str

    def __post_init__(self) -> None:
        if self.calibration_size < 1:
            raise Refusal("invalid_calibration", "calibration_size is at least 1")
        if not 0.0 < self.budget < 1.0:
            raise Refusal("invalid_calibration", "budget lies in (0, 1)")

    @classmethod
    def from_payload(cls, payload: object) -> CalibrationRecord:
        m = require_mapping(payload, "CalibrationRecord")
        require_keys(m, "CalibrationRecord", _CALIBRATION_KEYS, frozenset())
        budget = m["budget"]
        if isinstance(budget, bool) or not isinstance(budget, (int, float)):
            raise Refusal("invalid_calibration", "budget must be a number")
        try:
            budget = float(budget)
        except OverflowError:  # an integer beyond the float range (issue #37)
            raise Refusal("invalid_calibration", "budget lies in (0, 1)") from None
        return cls(require_identifier(m["calibration_record_id"], "calibration_record_id"),
                   require_identifier(m["claim_id"], "claim_id"), require_identifier(m["algorithm_id"], "algorithm_id"),
                   require_non_negative_int(m["calibration_size"], "calibration_size"), budget,
                   require_identifier(m["beacon_id"], "beacon_id"), require_identifier(m["round_id"], "round_id"))

    def to_payload(self) -> Payload:
        return {"calibration_record_id": self.calibration_record_id, "claim_id": self.claim_id,
                "algorithm_id": self.algorithm_id, "calibration_size": self.calibration_size, "budget": self.budget,
                "beacon_id": self.beacon_id, "round_id": self.round_id}


_BEACON_KEYS = frozenset({"calibration_record_id", "beacon_id", "round_id", "value", "published_at"})


@dataclass(frozen=True)
class BeaconOutput:
    """The verified output of a public beacon round, as supplied for one calibration record."""

    calibration_record_id: str
    beacon_id: str
    round_id: str
    value: str
    published_at: datetime

    @classmethod
    def from_payload(cls, payload: object) -> BeaconOutput:
        m = require_mapping(payload, "BeaconOutput")
        require_keys(m, "BeaconOutput", _BEACON_KEYS, frozenset())
        return cls(require_identifier(m["calibration_record_id"], "calibration_record_id"),
                   require_identifier(m["beacon_id"], "beacon_id"), require_identifier(m["round_id"], "round_id"),
                   require_digest(m["value"], "value"), require_timestamp(m["published_at"], "published_at"))

    def to_payload(self) -> Payload:
        return {"calibration_record_id": self.calibration_record_id, "beacon_id": self.beacon_id,
                "round_id": self.round_id, "value": self.value, "published_at": timestamp_payload(self.published_at)}
