"""Regression tests for the second review of PR #16 (review 5590424973 at f469fd7), one per finding applied.

Each test fails at f469fd7 and passes after the fix. Finding 4329259263 (the reviewer's name in a test docstring)
is listed for the owner in the pull request and has no test.
"""
from __future__ import annotations

import threading
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger, replay
from cpe.schemas import EventSpec, ResolutionPredicate
from cpe.schemas.forecast import JevRecord
from tests.test_ledger import fill
from tests.test_schemas import HEX, event_payload, predicate_payload


def jev_payload(**overrides: object) -> dict[str, object]:
    return {"jev_record_id": "J-1", "event_id": "E-1", "inputs_digest": HEX, "result_positive": {"score": 0.7},
            "result_negative": {"score": 0.2}, "model_hash": HEX, "routing_result": "route-A", "cost": 0.01,
            **overrides}


@pytest.mark.parametrize("value", [float("nan"), (1, 2), {"a": object()}, float("inf")])
def test_4329259192_jev_results_must_be_finite_json(value: object) -> None:
    for field in ("result_positive", "result_negative"):
        with pytest.raises(Refusal):
            JevRecord.from_payload(jev_payload(**{field: value}))


def test_4329259185_anchor_times_enter_the_clock_high_water_mark(tmp_path: Path, clock: ManualClock,
                                                                 anchor_store: HarnessAnchorStore) -> None:
    path = tmp_path / "l.sqlite"
    ledger = Ledger(path, clock, anchor_store)
    fill(ledger, clock, 1)
    clock.advance(timedelta(hours=1))
    anchor = ledger.anchor()
    clock.set(clock.now() - timedelta(minutes=30))
    with pytest.raises(Refusal) as refusal:
        ledger.append("event", "after-rollback", {})
    assert refusal.value.reason == "clock_rollback"
    assert ledger.state.count == 1
    ledger.close()
    reopened = Ledger(path, clock, anchor_store)
    with pytest.raises(Refusal) as again:
        reopened.append("event", "after-rollback", {})
    assert again.value.reason == "clock_rollback"
    clock.advance(timedelta(hours=1))
    record = reopened.append("event", "after-rollback", {})
    assert record.receipt_time > anchor.published_at


def test_4329259212_non_string_keys_are_a_typed_refusal() -> None:
    payload: dict[Any, Any] = {**event_payload(), 7: "x"}
    with pytest.raises(Refusal) as refusal:
        EventSpec.from_payload(payload)
    assert refusal.value.reason == "invalid_field_name"


def test_4329259199_an_unrepresentable_latency_window_is_refused_at_construction() -> None:
    with pytest.raises(Refusal) as refusal:
        EventSpec.from_payload(event_payload(latency_window_seconds=10**1000))
    assert refusal.value.reason == "invalid_window"
    with pytest.raises(Refusal):
        EventSpec.from_payload(event_payload(latency_window_seconds=10**12))


def test_4329259219_the_state_view_is_a_snapshot(ledger: Ledger, clock: ManualClock) -> None:
    fill(ledger, clock, 2)
    before = ledger.state_digest()
    view = ledger.state
    view.count = 99
    view.head = "0" * 64
    view.kinds["event"] = 0
    assert ledger.state_digest() == before
    ledger.append("event", "r-2", {})
    assert ledger.state.count == 3 and replay(ledger.records()).digest() == ledger.state_digest()


def test_4329259240_verify_takes_one_snapshot_under_the_ledger_lock(tmp_path: Path, clock: ManualClock) -> None:
    inner = HarnessAnchorStore()

    class RacingStore:
        """An external store whose read lets another thread append and anchor while the verification runs."""

        def __init__(self) -> None:
            self.armed = False
            self.thread: threading.Thread | None = None

        def publish(self, anchor: Anchor) -> None:
            inner.publish(anchor)

        def anchors(self) -> tuple[Anchor, ...]:
            if self.armed and self.thread is None:
                self.thread = threading.Thread(target=lambda: (ledger.append("event", "late", {}), ledger.anchor()))
                self.thread.start()
                self.thread.join(timeout=1.0)
            return inner.anchors()

    store = RacingStore()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    fill(ledger, clock, 3)
    ledger.anchor()
    clock.advance(timedelta(seconds=1))
    store.armed = True
    report = ledger.verify(store)
    assert store.thread is not None
    store.thread.join()
    assert report.intact and report.anchored_prefix == 3
    assert ledger.verify(store).intact and ledger.state.count == 4


def test_4329259250_an_accepted_json_value_is_not_the_caller_alias() -> None:
    value = ["YES"]
    predicate = ResolutionPredicate.from_payload({**predicate_payload(), "comparator": "in", "value": value})
    value.append("NO")
    assert predicate.value == ["YES"]
    results: dict[str, object] = {"score": 0.7}
    record = JevRecord.from_payload(jev_payload(result_positive=results))
    results["score"] = 0.0
    assert record.result_positive == {"score": 0.7}
