"""Append-only, anchored ledger with deterministic replay (``17`` section 3 item 2, A1).

- One transactional writer (SQLite, one process); every admission carries the server receipt time; an append is
  atomic with its state change, so a failed append leaves no phantom record and no acknowledgement (T-05, F-05).
- Every record extends a hash chain; an anchor is the digest of a committed prefix, published to an ``AnchorStore``
  held by a principal other than the writer (RC-34). Verification against the local anchor copy alone is reported
  as self-attested, never as verified (T-18, F-08).
- Replay of the canonical JSONL export reproduces the online state byte for byte (A1, T-08).
"""
from cpe.ledger.anchor import Anchor, AnchorStore, HarnessAnchorStore
from cpe.ledger.record import Record
from cpe.ledger.replay import LedgerState, VerificationReport, replay, verify
from cpe.ledger.store import FaultInjector, Ledger

__all__ = [
    "Anchor",
    "AnchorStore",
    "FaultInjector",
    "HarnessAnchorStore",
    "Ledger",
    "LedgerState",
    "Record",
    "VerificationReport",
    "replay",
    "verify",
]
