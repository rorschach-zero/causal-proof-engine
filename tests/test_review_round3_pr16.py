"""Regression tests for the third review of PR #16 (review 5590755736 at aec3e23), carried by the follow-up pull
request against main. Each test fails at 1215f6f (main after PR #16) and passes after the fix."""
from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger
from cpe.ledger.anchor import UnavailableAnchorStore
from cpe.ledger.store import records_from_jsonl
from cpe.schemas import ArmVersion, effective_cutoff
from tests.test_ledger import fill


def test_4329521346_an_anchor_published_externally_survives_a_crash_before_its_local_copy(
    tmp_path: Path, clock: ManualClock
) -> None:
    inner = HarnessAnchorStore()
    ledger_box: list[Ledger] = []

    class CrashAfterPublish:
        def publish(self, anchor: Anchor) -> None:
            inner.publish(anchor)
            ledger_box[0]._conn.close()  # the process dies right after the external publication

        def anchors(self) -> tuple[Anchor, ...]:
            return inner.anchors()

    path = tmp_path / "l.sqlite"
    ledger = Ledger(path, clock, CrashAfterPublish())
    ledger_box.append(ledger)
    fill(ledger, clock, 2)
    clock.advance(timedelta(hours=1))
    with pytest.raises(sqlite3.ProgrammingError):
        ledger.anchor()
    assert len(inner.anchors()) == 1
    clock.set(clock.now() - timedelta(minutes=30))
    reopened = Ledger(path, clock, inner)
    with pytest.raises(Refusal) as refusal:
        reopened.append("event", "after-crash", {})
    assert refusal.value.reason == "clock_rollback"
    assert reopened.local_anchors() == inner.anchors()
    assert reopened.verify(inner).intact and reopened.verify(inner).anchored_prefix == 2
    clock.advance(timedelta(hours=1))
    reopened.append("event", "after-crash", {})


def test_4329521356_a_deep_acyclic_consumption_chain_resolves_without_recursion() -> None:
    depth = 1100
    versions: dict[str, ArmVersion] = {}
    for i in range(depth):
        consumes = [f"v-{i - 1}"] if i else []
        versions[f"v-{i}"] = ArmVersion.from_payload({
            "arm_version_id": f"v-{i}", "arm_id": "v", "forecaster_id": "f", "forecaster_version": str(i),
            "declared_cutoff": "2026-01-01" if i != 7 else "2026-02-01", "cutoff_evidence_id": "ev",
            "cutoff_claim_label": "UNVERIFIED", "consumes": consumes,
        })
    assert effective_cutoff(f"v-{depth - 1}", versions).isoformat() == "2026-02-01"
    versions["v-0"] = ArmVersion.from_payload({**versions["v-0"].to_payload(), "consumes": [f"v-{depth - 1}"]})
    with pytest.raises(Refusal) as refusal:
        effective_cutoff(f"v-{depth - 1}", versions)
    assert refusal.value.reason == "invalid_arm_graph"


def test_4329521367_the_state_snapshot_is_taken_under_the_ledger_lock(ledger: Ledger, clock: ManualClock) -> None:
    fill(ledger, clock, 2)
    seen: list[int] = []
    reader = threading.Thread(target=lambda: seen.append(ledger.state.count))
    with ledger._lock:
        reader.start()
        reader.join(timeout=0.5)
        assert reader.is_alive() and seen == []  # the read waits for the lock
    reader.join()
    assert seen == [2]


def test_4329521375_the_export_is_written_as_bytes_without_newline_translation(
    ledger: Ledger, clock: ManualClock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fill(ledger, clock, 2)

    def no_text_write(self: Path, *args: object, **kwargs: object) -> int:
        raise AssertionError("the export must not go through newline-translating text writes")

    monkeypatch.setattr(Path, "write_text", no_text_write)
    target = tmp_path / "export.jsonl"
    ledger.write_export(target)
    assert target.read_bytes() == ledger.export_jsonl().encode("ascii")
    assert b"\r" not in target.read_bytes()


def test_4329521383_the_manual_clock_refuses_a_naive_time_on_set(clock: ManualClock) -> None:
    with pytest.raises(Refusal) as refusal:
        clock.set(datetime(2026, 1, 2))
    assert refusal.value.reason == "naive_timestamp"
    assert clock.now().year == 2026 and clock.now().day == 1


def test_4329521388_a_duplicate_key_in_an_imported_line_is_refused(ledger: Ledger, clock: ManualClock) -> None:
    fill(ledger, clock, 1)
    line = ledger.export_jsonl().rstrip("\n")
    assert line.startswith("{")
    duplicated = line[:-1] + ',"kind":"forecast"}'
    with pytest.raises(Refusal) as refusal:
        records_from_jsonl(duplicated + "\n")
    assert refusal.value.reason == "invalid_export" and "duplicate" in refusal.value.detail
    assert records_from_jsonl(line + "\n")[0].kind == "event"


# The three findings of the review of c5aa4c4 (4329707438, 4329707419, 4329707427), decided by the owner against
# the deletion of a pending anchor row; each test fails at c5aa4c4 and e110c93.


class _PersistsThenTimesOut:
    """A store that commits the anchor and then reports a timeout: a refusal that proves nothing."""

    def __init__(self) -> None:
        self.inner = HarnessAnchorStore()

    def publish(self, anchor: Anchor) -> None:
        self.inner.publish(anchor)
        raise Refusal("anchor_store_unavailable", "acknowledgement timed out")

    def anchors(self) -> tuple[Anchor, ...]:
        return self.inner.anchors()


class _Refusing:
    """A store that refuses every publish and holds nothing."""

    def publish(self, anchor: Anchor) -> None:
        raise Refusal("anchor_store_unavailable", "the anchor store did not answer")

    def anchors(self) -> tuple[Anchor, ...]:
        return ()


def test_4329707438_a_pending_row_survives_a_refusal_that_may_have_committed(tmp_path: Path, clock: ManualClock) -> None:
    store = _PersistsThenTimesOut()
    path = tmp_path / "l.sqlite"
    ledger = Ledger(path, clock, store)
    fill(ledger, clock, 2)
    clock.advance(timedelta(hours=1))
    with pytest.raises(Refusal):
        ledger.anchor()
    assert ledger.local_anchors() == () and len(store.anchors()) == 1
    clock.set(clock.now() - timedelta(minutes=30))
    with pytest.raises(Refusal) as refused:  # the pending row still bounds the clock in this process
        ledger.append("event", "late", {})
    assert refused.value.reason == "clock_rollback"
    ledger.close()
    reopened = Ledger(path, clock, store.inner)  # reconciliation against a store that holds the anchor confirms it
    assert reopened.local_anchors() == store.anchors()
    with pytest.raises(Refusal):
        reopened.append("event", "late", {})


def test_4329707419_a_repeat_anchor_never_replaces_the_published_row(tmp_path: Path, clock: ManualClock) -> None:
    inner = HarnessAnchorStore()
    ledger = Ledger(tmp_path / "l.sqlite", clock, inner)
    fill(ledger, clock, 2)
    first = ledger.anchor()
    assert ledger.anchor() == first and len(inner.anchors()) == 1  # a repeat at the same prefix is the same anchor
    ledger._anchor_store = _Refusing()  # the store now fails; the published row must survive the failed attempt
    with pytest.raises(Refusal):
        ledger.anchor()
    assert ledger.local_anchors() == (first,)
    assert ledger.verify(inner).intact and ledger.verify(inner).anchored_prefix == 2


def test_4329707427_memory_and_disk_agree_after_a_refused_publish(tmp_path: Path, clock: ManualClock) -> None:
    path = tmp_path / "l.sqlite"
    ledger = Ledger(path, clock, _Refusing())
    fill(ledger, clock, 2)
    clock.advance(timedelta(hours=1))
    attempt = clock.now()
    with pytest.raises(Refusal):
        ledger.anchor()
    assert ledger._anchor_high_water == ledger._load_anchor_high_water()
    clock.set(attempt - timedelta(minutes=30))
    with pytest.raises(Refusal):
        ledger.append("event", "late", {})
    ledger.close()
    unreachable = Ledger(path, clock, UnavailableAnchorStore())  # no store to ask: the pending row stays
    with pytest.raises(Refusal):
        unreachable.append("event", "late", {})
    unreachable.close()
    cleared = Ledger(path, clock, _Refusing())  # a reachable store that provably lacks the anchor clears the row
    cleared.append("event", "late", {})
    assert cleared.local_anchors() == () and cleared._anchor_high_water == ""
