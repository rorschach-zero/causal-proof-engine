"""Every record kind the Phase 1 ledger may hold, by the module that writes it.

Replay is closed (issue #37, pass 6, reading P6-R1): each module re-validates every row of its own kinds by the rule its
write path applies, skips the rows of another module's kinds, and refuses the ledger on a kind no module writes, so that
no row is read as authority, or ignored, without a rule. The kinds are named here once; each module imports its own.
"""
from __future__ import annotations

from cpe.errors import Refusal

# the pre-registration registry (cpe.registration)
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
KIND_DISCLOSURE = "forecast_disclosure"
REGISTRATION_KINDS: frozenset[str] = frozenset({
    KIND_ARM_VERSION, KIND_CUTOFF_CORRECTION, KIND_CANDIDATE, KIND_CLUSTER, KIND_VOID_REQUEST, KIND_BASE_RATE,
    KIND_FORECAST, KIND_CLAIM, KIND_REGISTER, KIND_CALIBRATION, KIND_BEACON, KIND_ROUND_REFUSED, KIND_DISCLOSURE,
})

# the resolution-rule and adjudication registry (cpe.adjudication)
KIND_EVENT = "event_spec"
KIND_RULE = "source_rule"
KIND_RECORD = "resolution_record"
KIND_OBSERVATION = "absence_observation"
KIND_STATUS = "source_status"
KIND_DISPOSITION = "disposition"
KIND_DEFECT = "source_latency_defect"
KIND_INCIDENT = "integrity_incident"
KIND_CONTENT = "resolution_content"
KIND_KNOWABLE = "knowable_correction"
ADJUDICATION_KINDS: frozenset[str] = frozenset({
    KIND_EVENT, KIND_RULE, KIND_RECORD, KIND_OBSERVATION, KIND_STATUS, KIND_DISPOSITION, KIND_DEFECT, KIND_INCIDENT,
    KIND_CONTENT, KIND_KNOWABLE,
})

# the offline capability model (cpe.capability)
KIND_EPOCH = "gate_epoch"
KIND_INTENT = "gate_intent"
KIND_ABORT = "gate_abort"
KIND_COMMIT = "gate_commit"
KIND_CHECK = "gate_check"
GATE_KINDS: frozenset[str] = frozenset({KIND_EPOCH, KIND_INTENT, KIND_ABORT, KIND_COMMIT, KIND_CHECK})

# the point-in-time feature store (cpe.pointintime)
KIND_ROW = "pit_row"
POINT_IN_TIME_KINDS: frozenset[str] = frozenset({KIND_ROW})

LEDGER_KINDS: frozenset[str] = REGISTRATION_KINDS | ADJUDICATION_KINDS | GATE_KINDS | POINT_IN_TIME_KINDS


def owned(kind: str, own: frozenset[str], record_id: str) -> bool:
    """Whether a row of ``kind`` is the replaying module's to re-validate; False for another module's kind; a refusal
    for a kind no module writes."""
    if kind not in LEDGER_KINDS:
        raise Refusal("unknown_kind", f"{record_id} has kind {kind!r}, which no registry writes")
    return kind in own
