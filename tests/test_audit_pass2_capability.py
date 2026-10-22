"""Whole-codebase audit, pass 2 (issue #37): the capability findings of the Codex auditor (issue #37 comment
``6346290601``, findings 1 and 10). Each test failed on the audit commit ``2998824d0330ef028a8cc2cb7682a40f6fc23763``."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from pathlib import Path

from cpe.capability import CapabilityGate, HarnessVerifier, ManualTimeSource
from cpe.capability.records import CheckRecord
from cpe.capability.state import replay_gate
from cpe.clock import parse_timestamp
from cpe.ledger import Ledger
from tests.test_capability import ENV, OWNER, RELEASE, RULES, TOLERANCE, FlakyStore, Rig, issue
from tests.test_hardening_h4 import RollbackClock


def rollback_rig(tmp_path: Path) -> tuple[Rig, RollbackClock]:
    rig = Rig(tmp_path)
    clock = RollbackClock(rig.clock.now())
    time = ManualTimeSource(clock)
    rig.clock, rig.time, rig.store = clock, time, FlakyStore()
    rig.ledger = Ledger(tmp_path / "rollback.sqlite", clock, rig.store, rig.faults)
    rig.gate = CapabilityGate(rig.ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    rig.tick()
    return rig, clock


# 1 (P1): the high-water mark holds the wall time a check observed, not only its receipt --------------------------

def test_codex_1_a_capability_seen_expired_is_not_valid_again_after_a_rollback(tmp_path: Path) -> None:
    rig, clock = rollback_rig(tmp_path)
    start = clock.now()
    capability = issue(rig.epoch(), "a", expiry=start + timedelta(seconds=0.9))
    clock.set(start + timedelta(seconds=1))
    clock.rollback = timedelta(seconds=0.5)  # the decision reads +1 s; the append's receipt reads +0.5 s
    assert rig.refused(capability) == "expired"
    clock.set(start + timedelta(seconds=0.6))  # inside the slew tolerance, below the time the check observed
    # At 2998824 the high-water mark was the receipt (+0.5 s) and this presentation was acknowledged.
    assert rig.refused(capability) == "clock_rollback"
    clock.set(start + timedelta(seconds=1))  # at the observed time again, the capability is past its expiry
    assert rig.refused(capability) == "expired"
    state = rig.gate.state()
    assert not state.intents and state.level == "RESEARCH_ONLY"
    assert state.observed == start + timedelta(seconds=1)


def test_codex_1_the_observed_time_is_replayed(tmp_path: Path) -> None:
    rig, clock = rollback_rig(tmp_path)
    start = clock.now()
    clock.rollback = timedelta(seconds=0.5)
    rig.gate.perform("research")  # an action-boundary check observes ``start`` and is received at ``start - 0.5``
    records = tuple(rig.ledger.records())
    assert replay_gate(records, 0, RULES, ()).observed == start
    assert parse_timestamp(records[-1].receipt_time) < CheckRecord.from_payload(records[-1].payload).reading.wall


# 10 (P3): a non-ASCII signature is an invalid signature, written as a refused check ------------------------------

def test_codex_10_a_non_ascii_signature_is_an_invalid_signature(tmp_path: Path) -> None:
    assert HarnessVerifier("owner").verify(b"message", "é") is False  # at 2998824: TypeError
    rig = Rig(tmp_path)
    rig.tick()
    capability = replace(issue(rig.epoch(), "a"), signature="é")
    assert rig.refused(capability) == "invalid_signature"
    checks = [CheckRecord.from_payload(r.payload) for r in rig.ledger.records() if r.kind == "gate_check"]
    assert [c.reason for c in checks if c.subject == "presentation:a"] == ["invalid_signature"]
