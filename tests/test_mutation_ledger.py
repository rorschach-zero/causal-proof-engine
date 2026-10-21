"""Mutation testing, ``cpe/ledger``: tests that kill mutants the suite let survive at ac4c640 (``research/19``
section "Mutation testing"). Each pins behaviour the ledger promises: the reason code of every refusal, every field
of a verification report on every branch, and the restore and anchor paths."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta, timezone
from pathlib import Path

import pytest

from cpe.clock import ManualClock, SystemClock
from cpe.errors import Refusal
from cpe.ledger import Anchor, FaultInjector, HarnessAnchorStore, Ledger, Record, VerificationReport, replay, verify
from cpe.ledger.anchor import UnavailableAnchorStore
from cpe.ledger.store import records_from_jsonl
from tests.test_ledger import fill, rehash


def reason(call: object, *args: object, **kwargs: object) -> str:
    assert callable(call)
    with pytest.raises(Refusal) as refused:
        call(*args, **kwargs)
    return refused.value.reason


def records_of(ledger: Ledger, clock: ManualClock, count: int) -> list[Record]:
    fill(ledger, clock, count)
    return list(ledger.records())


# replay ----------------------------------------------------------------------------------------------------------

def test_replay_names_each_chain_defect(ledger: Ledger, clock: ManualClock) -> None:
    records = records_of(ledger, clock, 3)
    assert reason(replay, [records[0], records[2]]) == "chain_gap"
    assert reason(replay, [records[0], replace(records[1], prev_hash="0" * 64)]) == "chain_break"
    assert reason(replay, [records[0], replace(records[1], payload={"i": 99})]) == "hash_mismatch"
    earlier = replace(records[1], receipt_time="2025-01-01T00:00:00.000000Z")
    assert reason(replay, rehash([records[0], earlier])) == "receipt_time_regression"


def test_a_record_whose_only_defect_is_its_own_hash_breaks_the_chain(ledger: Ledger, clock: ManualClock) -> None:
    records = records_of(ledger, clock, 2)
    edited = [records[0], replace(records[1], payload={"i": 99})]  # seq and prev_hash still right
    report = verify(edited, [], external=False)
    assert report == VerificationReport("tampered", "unanchored", 0, 0, "chain broken at record 2")


# verify: every branch, every field --------------------------------------------------------------------------------

def test_verify_reports_every_field_on_every_branch(ledger: Ledger, clock: ManualClock) -> None:
    records = records_of(ledger, clock, 4)
    two, four = Anchor(2, records[1].entry_hash, records[1].receipt_time), Anchor(4, records[3].entry_hash, records[3].receipt_time)
    broken_third = [*records[:2], replace(records[2], payload={"i": 99}), records[3]]

    plain = verify(records, [], external=True)
    assert (plain.status, plain.attestation, plain.anchored_prefix, plain.unanchored_window) == ("continuous", "unanchored", 0, 4)
    assert plain.intact

    for external, attestation in ((True, "verified"), (False, "self-attested")):
        short = verify(records[:3], [four], external=external)
        assert (short.status, short.attestation, short.anchored_prefix, short.unanchored_window) == ("truncated", attestation, 0, 0)
        inside = verify(broken_third, [four], external=external)
        assert (inside.status, inside.attestation, inside.anchored_prefix, inside.unanchored_window) == ("tampered", attestation, 0, 0)
        mismatch = verify(records, [Anchor(2, "f" * 64, two.published_at), four], external=external)
        assert (mismatch.status, mismatch.attestation, mismatch.anchored_prefix, mismatch.unanchored_window) == ("tampered", attestation, 0, 0)
        after = verify(broken_third, [two], external=external)
        assert (after.status, after.attestation, after.anchored_prefix, after.unanchored_window) == ("tampered", attestation, 2, 0)
        good = verify(records, [two], external=external)
        assert (good.status, good.attestation, good.anchored_prefix, good.unanchored_window) == ("continuous", attestation, 2, 2)
        assert not inside.intact and not after.intact


def test_a_break_at_the_last_anchored_record_is_inside_the_anchored_prefix(ledger: Ledger, clock: ManualClock) -> None:
    records = records_of(ledger, clock, 3)
    broken = [records[0], replace(records[1], payload={"i": 99}), records[2]]
    report = verify(broken, [Anchor(2, records[1].entry_hash, records[1].receipt_time)], external=True)
    assert (report.status, report.anchored_prefix) == ("tampered", 0)


# record and anchor schemas -----------------------------------------------------------------------------------------

def test_record_and_anchor_payloads_are_bounded_below(ledger: Ledger, clock: ManualClock) -> None:
    record = records_of(ledger, clock, 1)[0]
    assert reason(Record.from_payload, {**record.to_payload(), "seq": 0}) == "invalid_record"
    assert Record.from_payload(record.to_payload()) == record
    anchor = Anchor(1, record.entry_hash, record.receipt_time)
    assert Anchor.from_payload(anchor.to_payload()) == anchor  # a one-record anchor is valid
    assert reason(Anchor.from_payload, {**anchor.to_payload(), "prefix_length": 0}) == "invalid_anchor"


def test_the_harness_store_refuses_a_regression_and_a_malformed_export() -> None:
    store = HarnessAnchorStore()
    store.publish(Anchor(2, "a" * 64, "2026-01-01T00:00:00.000000Z"))
    assert reason(store.publish, Anchor(1, "b" * 64, "2026-01-01T00:00:01.000000Z")) == "anchor_regression"
    assert reason(HarnessAnchorStore.from_export, {"prefix_length": 2}) == "invalid_anchor_export"
    assert HarnessAnchorStore.from_export(store.export()).anchors() == store.anchors()


def test_the_unavailable_store_refuses_both_calls() -> None:
    store = UnavailableAnchorStore()
    assert reason(store.publish, Anchor(1, "a" * 64, "2026-01-01T00:00:00.000000Z")) == "anchor_store_unavailable"
    assert reason(store.anchors) == "anchor_store_unavailable"


# the writer: anchor, restore, export --------------------------------------------------------------------------------

def test_anchor_refusals_are_named(tmp_path: Path, clock: ManualClock) -> None:
    assert reason(Ledger(tmp_path / "none.sqlite", clock).anchor) == "no_anchor_store"
    assert reason(Ledger(tmp_path / "empty.sqlite", clock, HarnessAnchorStore()).anchor) == "empty_ledger"


class FailingStore(HarnessAnchorStore):
    def publish(self, anchor: Anchor) -> None:
        raise Refusal("anchor_store_unavailable", "down")


def test_a_failed_publish_keeps_the_staged_time_as_the_clock_bound(tmp_path: Path, clock: ManualClock) -> None:
    ledger = Ledger(tmp_path / "l.sqlite", clock, FailingStore())
    fill(ledger, clock, 1)
    clock.advance(timedelta(seconds=10))
    staged = clock.now()
    with pytest.raises(Refusal):
        ledger.anchor()
    clock.set(staged - timedelta(seconds=1))  # above every receipt, below the staged publication time
    assert reason(ledger.now) == "clock_rollback"
    clock.set(staged)
    assert ledger.now() == staged


def test_restore_keeps_the_store_and_the_faults_and_takes_the_last_record_anchor(tmp_path: Path,
                                                                                 clock: ManualClock) -> None:
    store = HarnessAnchorStore()
    original = Ledger(tmp_path / "a.sqlite", clock, store)
    fill(original, clock, 3)
    original.anchor()  # an anchor covering exactly every exported record
    faults = FaultInjector()
    restored, report = Ledger.restore(tmp_path / "b.sqlite", clock, original.records(), store, faults)
    assert report.anchored_prefix == 3 and restored.local_anchors() == store.anchors()
    clock.advance(timedelta(seconds=1))
    restored.append("event", "after", {})
    assert restored.anchor().prefix_length == 4  # the restored ledger kept its anchor store
    faults.arm("before_insert", RuntimeError("injected"))
    with pytest.raises(RuntimeError):  # and its fault injector
        restored.append("event", "faulted", {})
    assert reason(Ledger.restore, tmp_path / "b.sqlite", clock, original.records(), store) == "restore_target_not_empty"


def test_an_export_with_a_blank_line_keeps_every_record_after_it(ledger: Ledger, clock: ManualClock) -> None:
    records = records_of(ledger, clock, 3)
    lines = ledger.export_jsonl().splitlines()
    text = "\n".join([lines[0], "", *lines[1:]]) + "\n"
    assert records_from_jsonl(text) == tuple(records)
    assert reason(records_from_jsonl, "{not json\n") == "invalid_export"


def test_the_system_clock_reads_aware_utc_time() -> None:
    now = SystemClock().now()
    assert now.tzinfo is timezone.utc
