"""The offline capability model (``17`` section 3 item 5, A5; ``research/19-phase1-handoff.md`` section 3.3).

- A capability is verified over its whole tuple under one canonical serialisation (RC-62), through a ``Verifier``;
  Phase 1's is a harness double with no key material (the owner's public-key verifier and the key handling are
  OD10).
- The protected operation verifies and consumes the capability itself, in the writer transaction; no object is
  authority (RC-43, RC-46). It runs the four anchored steps of item 5 (RC-153, RC-158, RC-197).
- Every clock-dependent check persists its reading before its verdict; expiry is read against the ledger's
  high-water mark; a boot-id change or a drift beyond the tolerance from the epoch baseline is a discontinuity
  (RC-37, RC-65, RC-73, RC-100).
- The epoch is rotated at every process start, every demotion and every discontinuity, and the rotation is
  anchored before the gate leaves demoted-unanchored; every start begins at the floor (RC-74, RC-103, RC-123).
"""
from cpe.capability.gate import CapabilityGate, PromotionOutcome
from cpe.capability.levels import ACTIONS, FLOOR, LEVELS, LIVE
from cpe.capability.signing import HarnessVerifier, Verifier
from cpe.capability.state import GateRules, GateState, replay_gate
from cpe.capability.timesource import ClockReading, HostTimeSource, ManualTimeSource, TimeSource

__all__ = [
    "ACTIONS",
    "FLOOR",
    "LEVELS",
    "LIVE",
    "CapabilityGate",
    "ClockReading",
    "GateRules",
    "GateState",
    "HarnessVerifier",
    "HostTimeSource",
    "ManualTimeSource",
    "PromotionOutcome",
    "TimeSource",
    "Verifier",
    "replay_gate",
]
