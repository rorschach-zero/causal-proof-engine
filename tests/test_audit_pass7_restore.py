"""Whole-codebase audit, pass 7 (issue #37), at ``c55e4cee65656355850bde32b07059e37d8b523b``: the clock bound across a
restore.

- Codex 7-1 (PR #82 review comment 4416532445): a gate check persists the wall time of the sample it was decided on,
  which a rollback before its append puts above its receipt; the ledger keeps that time as a bound of every later
  receipt (pass 6 Codex 6-3). ``Ledger.restore`` rebuilt the receipt high-water mark from the records but not this
  bound, so the restore of the complete history admitted the receipt the original ledger refuses: criteria recorded
  400 ms before the issuance window opened, after a check had read 100 ms past its opening (``17`` item 2 "Clock",
  RC-37, RC-65). The wall times are in the exported records, so the restore rebuilds the bound from them.

The first test failed on the pass-7 pin; the second checks that a gate record without its reading is a typed refusal."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.capability import CapabilityGate, ManualTimeSource
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from tests.test_adjudication import day, rule, spec
from tests.test_audit_pass6_observed_wall import RollbackAfterNextRead
from tests.test_capability import ENV, OWNER, RELEASE, TOLERANCE


def test_codex7_1_a_restore_keeps_the_wall_time_a_check_persisted(tmp_path: Path) -> None:
    clock = RollbackAfterNextRead(day(1))
    time = ManualTimeSource(clock)
    store = HarnessAnchorStore()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    AdjudicationRegistry(ledger).register_rule(rule())
    gate = CapabilityGate(ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    time.advance(day(20) + timedelta(milliseconds=100) - clock.now())  # 100 ms after spec()'s issuance opens
    clock.step = timedelta(milliseconds=500)  # rolled back between the check's decision and its append
    gate.perform("research")
    records = records_from_jsonl(ledger.export_jsonl())
    ledger.close()
    restored, report = Ledger.restore(tmp_path / "restored.sqlite", clock, records, store)
    assert report.intact
    with pytest.raises(Refusal) as refused:
        AdjudicationRegistry(restored).register_event(spec())  # at c55e4ce: recorded 400 ms before the window opens
    assert refused.value.reason == "clock_rollback"


def test_a_gate_record_without_its_reading_is_a_typed_refusal_at_restore(tmp_path: Path) -> None:
    clock = RollbackAfterNextRead(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    ledger.append("gate_check", "gate-check:malformed", {"subject": "action:research"})
    records = records_from_jsonl(ledger.export_jsonl())
    with pytest.raises(Refusal) as refused:
        Ledger.restore(tmp_path / "restored.sqlite", clock, records, HarnessAnchorStore())
    assert refused.value.reason == "invalid_record"
