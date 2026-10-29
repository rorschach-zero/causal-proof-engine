"""Pre-registration registry (``17`` section 3 items 1 and 2; hand-off sections 3.1, 3.2, 4.3).

Everything a forecast is later judged against is written before the forecast exists and never rewritten:
- arm versions with their declared cutoffs, created before any registration under them (RC-98, RC-112, RC-150);
- the candidate log, one entry per candidate before any forecast on it (RC-78);
- the cluster registration record that fixes the members, the pre-declared VOID set and the arm versions per arm
  (RC-66, RC-85, RC-87, RC-96, RC-138); a VOID request after it changes no state;
- forecasts keyed by (event, arm, slot), one per slot, the baseline slot computed from a committed base rate
  (RC-75, RC-89, RC-109);
- the claim pre-registration, the one confirmatory register of Phase 1 anchored with S_max before any beacon
  round, and one calibration record per claim bound to it before its beacon round, whose seed is derived from the
  record and the beacon output and never chosen (``18`` M-1 (i); RC-187, RC-304, RC-309, RC-311, RC-315; M-8).
"""
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
from cpe.registration.registry import RegistrationRegistry, SlotState
from cpe.registration.seeds import derive_seed

__all__ = [
    "BaseRate",
    "BeaconOutput",
    "CalibrationRecord",
    "CandidateEntry",
    "ClaimPreregistration",
    "ClusterRegistration",
    "ConfirmatoryRegister",
    "CutoffCorrection",
    "RegistrationRegistry",
    "SlotState",
    "VoidRequest",
    "derive_seed",
]
