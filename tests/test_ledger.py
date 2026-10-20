"""Ledger invariants: T-01, T-05, T-06, T-07, T-18, F-05, F-06, F-07, F-08, and the replay identity of A1."""
from __future__ import annotations

import threading
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Anchor, FaultInjector, HarnessAnchorStore, Ledger, Record, replay, verify
from cpe.ledger.anchor import UnavailableAnchorStore
from cpe.ledger.record import entry_digest
from cpe.ledger.store import records_from_jsonl


def fill(ledger: Ledger, clock: ManualClock, count: int, prefix: str = "r") -> None:
    for i in range(count):
        clock.advance(timedelta(seconds=1))
        ledger.append("event", f"{prefix}-{i}", {"i": i, "claimed_issued_at": "2020-01-01T00:00:00.000000Z"})


def rehash(records: list[Record]) -> list[Record]:
    """Recompute the chain over edited records, the way a tamperer with write access would."""
    out: list[Record] = []
    prev = records[0].prev_hash
    for record in records:
        digest = entry_digest(record.seq, record.record_id, record.kind, record.receipt_time, record.payload, prev)
        out.append(replace(record, prev_hash=prev, entry_hash=digest))
        prev = digest
    return out


def test_t01_receipt_time_is_the_server_clock_and_the_claim_is_kept_apart(ledger: Ledger, clock: ManualClock) -> None:
    record = ledger.append("forecast", "f-1", {"claimed_issued_at": "2020-01-01T00:00:00.000000Z"})
    assert record.receipt_time == "2026-01-01T00:00:00.000000Z"
    assert record.payload == {"claimed_issued_at": "2020-01-01T00:00:00.000000Z"}


@pytest.mark.parametrize("point", ["before_insert", "before_commit"])
def test_t05_f05_a_failed_append_leaves_no_record_and_no_acknowledgement(
    ledger: Ledger, clock: ManualClock, faults: FaultInjector, point: str
) -> None:
    fill(ledger, clock, 2)
    before = ledger.state_digest()
    faults.arm(point, OSError("disk full"))
    with pytest.raises(OSError):
        ledger.append("event", "phantom", {"x": 1})
    assert ledger.state_digest() == before
    assert [r.record_id for r in ledger.records()] == ["r-0", "r-1"]
    assert replay(ledger.records()).digest() == before
    ledger.append("event", "r-2", {"x": 2})
    assert ledger.state.count == 3


def test_t06_death_between_write_and_acknowledgement_leaves_at_most_one_durable_record(
    tmp_path: Path, clock: ManualClock, anchor_store: HarnessAnchorStore
) -> None:
    faults = FaultInjector()
    ledger = Ledger(tmp_path / "l.sqlite", clock, anchor_store, faults)
    faults.arm("after_commit", RuntimeError("process killed"))
    with pytest.raises(RuntimeError):
        ledger.append("event", "e-1", {"x": 1})
    ledger.close()
    reopened = Ledger(tmp_path / "l.sqlite", clock, anchor_store)
    assert [r.record_id for r in reopened.records()] == ["e-1"]
    assert reopened.state_digest() == replay(reopened.records()).digest()
    with pytest.raises(Refusal) as refusal:
        reopened.append("event", "e-1", {"x": 1})
    assert refusal.value.reason == "duplicate_record_id"
    assert reopened.state.count == 1


def test_t06_concurrent_submissions_of_one_id_admit_exactly_one(ledger: Ledger) -> None:
    outcomes: list[str] = []
    barrier = threading.Barrier(2)

    def submit() -> None:
        barrier.wait()
        try:
            ledger.append("event", "same-id", {"x": 1})
            outcomes.append("admitted")
        except Refusal as refusal:
            outcomes.append(refusal.reason)

    threads = [threading.Thread(target=submit) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(outcomes) == ["admitted", "duplicate_record_id"]
    assert ledger.state.count == 1


def test_f06_a_new_ledger_object_on_an_existing_file_replays_the_online_state(tmp_path: Path, clock: ManualClock) -> None:
    ledger = Ledger(tmp_path / "l.sqlite", clock)
    fill(ledger, clock, 5)
    online = ledger.state_digest()
    ledger.close()
    assert Ledger(tmp_path / "l.sqlite", clock).state_digest() == online


def test_a1_replay_of_the_export_equals_the_online_state_byte_for_byte(ledger: Ledger, clock: ManualClock) -> None:
    fill(ledger, clock, 7)
    ledger.append("resolution", "res-1", {"outcome": "YES", "p": 0.5, "nested": {"b": [1, 2.5], "a": None}})
    exported = records_from_jsonl(ledger.export_jsonl())
    assert exported == ledger.records()
    assert replay(exported).to_payload() == ledger.state.to_payload()
    assert replay(exported).digest() == ledger.state_digest()


def test_clock_rollback_fails_closed_without_a_record(ledger: Ledger, clock: ManualClock) -> None:
    fill(ledger, clock, 1)
    clock.set(clock.now() - timedelta(seconds=30))
    with pytest.raises(Refusal) as refusal:
        ledger.append("event", "late", {})
    assert refusal.value.reason == "clock_rollback"
    assert ledger.state.count == 1


def test_anchor_store_is_append_only_and_an_outage_fails_closed(ledger: Ledger, clock: ManualClock,
                                                                anchor_store: HarnessAnchorStore) -> None:
    fill(ledger, clock, 2)
    anchor = ledger.anchor()
    assert anchor.prefix_length == 2 and anchor_store.anchors() == (anchor,) and ledger.local_anchors() == (anchor,)
    with pytest.raises(Refusal) as refusal:
        anchor_store.publish(Anchor(2, "f" * 64, anchor.published_at))
    assert refusal.value.reason == "anchor_conflict"
    with pytest.raises(Refusal):
        anchor_store.publish(Anchor(1, "f" * 64, anchor.published_at))
    outage = Ledger(":memory:", clock, UnavailableAnchorStore())
    outage.append("event", "x", {})
    with pytest.raises(Refusal) as refusal:
        outage.anchor()
    assert refusal.value.reason == "anchor_store_unavailable"
    assert outage.local_anchors() == ()


def test_t07_tampering_truncation_and_the_unanchored_window(ledger: Ledger, clock: ManualClock,
                                                            anchor_store: HarnessAnchorStore) -> None:
    fill(ledger, clock, 2)
    ledger.anchor()
    fill(ledger, clock, 1, prefix="s")
    records = list(ledger.records())
    anchors = anchor_store.anchors()
    honest = verify(records, anchors, external=True)
    assert (honest.status, honest.anchored_prefix, honest.unanchored_window) == ("continuous", 2, 1)

    edited_in_prefix = [records[0], replace(records[1], payload={"i": 99}), records[2]]
    assert verify(edited_in_prefix, anchors, external=True).status == "tampered"
    assert verify(rehash(edited_in_prefix), anchors, external=True).status == "tampered"

    assert verify(records[:1], anchors, external=True).status == "truncated"

    suffix_rehashed = rehash([records[0], records[1], replace(records[2], payload={"i": 99})])  # F-07
    report = verify(suffix_rehashed, anchors, external=True)
    assert (report.status, report.anchored_prefix, report.unanchored_window) == ("continuous", 2, 1)
    assert "unanchored window of 1 records" in report.detail
    assert suffix_rehashed[2].entry_hash != records[2].entry_hash

    restored_to_anchor = verify(records[:2], anchors, external=True)
    assert (restored_to_anchor.status, restored_to_anchor.unanchored_window) == ("continuous", 0)
    # This report alone is not a pass condition for T-30: a restore that lands on an anchor is continuous by
    # construction (RC-74); the capability model checks consumed nonces and epochs on top of it.

    unanchored = verify(records, (), external=True)
    assert (unanchored.attestation, unanchored.unanchored_window) == ("unanchored", 3)


def test_t18_f08_a_rewritten_history_with_a_regenerated_local_anchor_is_caught_only_externally(
    tmp_path: Path, clock: ManualClock
) -> None:
    external = HarnessAnchorStore()
    ledger = Ledger(tmp_path / "honest.sqlite", clock, external)
    fill(ledger, clock, 3)
    ledger.anchor()
    forged_store = HarnessAnchorStore()  # the writer's own copy, which it can regenerate at will
    forged = Ledger(tmp_path / "forged.sqlite", ManualClock(clock.now() - timedelta(days=1)), forged_store)
    forged.append("event", "r-0", {"i": 0})
    forged.append("event", "r-1", {"i": 1})
    forged.append("event", "r-2", {"i": 2, "edited": True})
    forged.anchor()
    local_only = forged.verify()
    assert (local_only.status, local_only.attestation) == ("continuous", "self-attested")
    against_external = forged.verify(external)
    assert against_external.status == "tampered"
    assert ledger.verify(external).attestation == "verified"


def test_restore_needs_the_external_store_and_reports_the_window(tmp_path: Path, clock: ManualClock) -> None:
    external = HarnessAnchorStore()
    ledger = Ledger(tmp_path / "source.sqlite", clock, external)
    fill(ledger, clock, 4)
    ledger.anchor()
    fill(ledger, clock, 2, prefix="late")
    exported = records_from_jsonl(ledger.export_jsonl())
    restored, report = Ledger.restore(tmp_path / "restored.sqlite", clock, exported, external)
    assert restored.state_digest() == ledger.state_digest()
    assert (report.status, report.attestation, report.anchored_prefix, report.unanchored_window) == ("continuous", "verified", 4, 2)
    assert restored.local_anchors() == external.anchors()
    with pytest.raises(Refusal):
        Ledger.restore(tmp_path / "again.sqlite", clock, exported[:3] + exported[4:], external)
    with pytest.raises(Refusal):
        Ledger.restore(tmp_path / "restored.sqlite", clock, exported, external)
