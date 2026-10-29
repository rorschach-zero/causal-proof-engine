"""Whole-codebase audit (issue #37): the P3 findings in the ledger, the capability model and the canonical form,
from pass 3 (comment 6348183848) and pass 4 (comment 6349971614). Each raised an untyped error, or coerced a value,
where ``AGENTS.md`` section 6 requires a typed refusal. Every test failed on the pass-4 commit
``c3d6233dbaeb71eb71cb128394099b23cef285b5``. The pass-3 expiry beyond the UTC range is fixed with C1 (PR #52) and
tested there."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpe.canonical import JsonValue, canonical_bytes
from cpe.capability import CapabilityGate
from cpe.capability.records import AbortRecord, CheckRecord, EpochRecord
from cpe.clock import ManualClock, format_timestamp
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger, Record
from cpe.ledger.record import GENESIS_HASH, entry_digest
from cpe.ledger.store import records_from_jsonl
from tests.test_capability import ENV, OWNER, RELEASE, Rig, at, issue


def test_records_from_jsonl_gives_invalid_export_for_a_deeply_nested_line() -> None:
    """store.py:338-343 catches ValueError only; json.loads raises RecursionError on a deeply nested line."""
    with pytest.raises(Refusal) as refused:
        records_from_jsonl("[" * 100_000 + "]" * 100_000 + "\n")
    assert refused.value.reason == "invalid_export"


def _chain(specs: list[tuple[str, str]]) -> list[Record]:
    records: list[Record] = []
    head = GENESIS_HASH
    for seq, (kind, record_id) in enumerate(specs, start=1):
        receipt = format_timestamp(at(seq))
        payload: JsonValue = {"i": seq}
        entry = entry_digest(seq, record_id, kind, receipt, payload, head)
        records.append(Record(seq, record_id, kind, receipt, payload, head, entry))
        head = entry
    return records


def test_restore_refuses_a_duplicate_record_id_with_a_typed_refusal(tmp_path: Path) -> None:
    """replay() (replay.py:376-388) does not check record-id uniqueness, so an archive the online writer could never
    hold replays cleanly and Ledger.restore (store.py:310-327) surfaces the UNIQUE constraint as a raw
    sqlite3.IntegrityError."""
    exported = "".join(canonical_bytes(r.to_payload()).decode("ascii") + "\n"
                       for r in _chain([("note", "same-id"), ("note", "same-id")]))
    records = records_from_jsonl(exported)
    with pytest.raises(Refusal):
        Ledger.restore(tmp_path / "r.sqlite", ManualClock(at(10)), records, HarnessAnchorStore())


def test_a_lone_surrogate_signature_is_an_invalid_signature(rig: Rig) -> None:
    """signing.py:444 encodes the signature as UTF-8; a lone surrogate (a valid identifier per require_identifier)
    raises UnicodeEncodeError inside the decision, so nothing is persisted and the refusal is untyped."""
    forged = replace(issue(rig.epoch(), "s"), signature="\ud800")
    assert rig.refused(forged) in ("invalid_signature", "invalid_identifier")
    assert not OWNER.verify(b"message", "\ud800")


def test_an_unhashable_action_is_refused_typed(rig: Rig) -> None:
    """gate.py:219 ``action not in ACTIONS`` raises TypeError for an unhashable action, after the reading was
    taken and before any check record is written."""
    with pytest.raises(Refusal) as refused:
        rig.gate.perform(["research"])  # type: ignore[arg-type]
    assert refused.value.reason == "unknown_action"


def test_a_non_numeric_slew_tolerance_is_invalid_tolerance(rig: Rig) -> None:
    """gate.py:72-77 math.isfinite('1') raises TypeError; the owner field is refused untyped."""
    with pytest.raises(Refusal) as refused:
        CapabilityGate(rig.ledger, OWNER, rig.time, ENV, RELEASE, "1")  # type: ignore[arg-type]
    assert refused.value.reason == "invalid_tolerance"


def _reading() -> dict[str, object]:
    return {"wall": format_timestamp(at(1)), "monotonic": 1.0, "boot_id": "boot-1"}


def test_gate_records_refuse_rather_than_coerce_text_fields() -> None:
    """records.py:159, 201, 246 use ``str(...)`` on reason, subject and verdict: a replayed gate record with a list
    or a number in those fields is silently coerced, not refused (AGENTS.md section 6)."""
    with pytest.raises(Refusal):
        EpochRecord.from_payload({"epoch": 1, "index": 1, "reason": ["start"], "baseline": _reading()})
    with pytest.raises(Refusal):
        CheckRecord.from_payload({"subject": 7, "verdict": {"admitted": True}, "reason": None, "reading": _reading()})


@pytest.fixture
def rig(tmp_path: Path) -> Rig:
    return Rig(tmp_path)


@pytest.mark.parametrize("kind, record_id", [("note", "\ud800"), ("\udfff", "n-1")])
def test_a_surrogate_in_a_record_identifier_or_kind_is_a_typed_refusal(tmp_path: Path, kind: str,
                                                                        record_id: str) -> None:
    """pass 4: require_identifier admitted a surrogate code point, and the SQLite insert raised UnicodeEncodeError."""
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(datetime(2026, 1, 1, tzinfo=timezone.utc)))
    with pytest.raises(Refusal) as refused:
        ledger.append(kind, record_id, {})
    assert refused.value.reason == "invalid_identifier"
    assert ledger.records() == ()


def test_an_abort_record_refuses_a_reason_that_is_not_text() -> None:
    with pytest.raises(Refusal) as refused:
        AbortRecord.from_payload({"intent_id": "i-1", "reason": 3, "reading": _reading()})
    assert refused.value.reason == "invalid_text"
