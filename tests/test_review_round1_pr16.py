"""Regression tests for the Codex review of PR #16 (review 5589..., commit 9c1127c). Each test fails on 9c1127c."""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from datetime import timedelta
from pathlib import Path

import pytest

from cpe.clock import ManualClock, parse_timestamp
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.schemas import ArmVersion, EventSpec, Forecast, ResolutionPredicate, effective_cutoff
from tests.test_schemas import HEX, arm, event_payload, forecast_payload, predicate_payload


def test_4329009760_anchor_refuses_a_clock_below_the_high_water_mark(ledger: Ledger, clock: ManualClock) -> None:
    clock.advance(timedelta(hours=1))
    ledger.append("event", "e-1", {})
    clock.set(clock.now() - timedelta(minutes=30))
    with pytest.raises(Refusal) as refusal:
        ledger.anchor()
    assert refusal.value.reason == "clock_rollback"
    assert ledger.local_anchors() == ()


@pytest.mark.parametrize("kind, record_id", [("", "r-1"), ("event", ""), (7, "r-1"), ("event", " r ")])
def test_4329009766_append_validates_kind_and_record_id(ledger: Ledger, kind: object, record_id: object) -> None:
    with pytest.raises(Refusal) as refusal:
        ledger.append(kind, record_id, {})  # type: ignore[arg-type]
    assert refusal.value.reason == "invalid_identifier"
    assert ledger.state.count == 0


@pytest.mark.parametrize("value", [float("nan"), (1, 2), {"in": ["a", object()]}, float("inf")])
def test_4329009776_predicate_value_must_be_finite_json(value: object) -> None:
    payload = predicate_payload()
    if isinstance(value, dict):
        payload["comparator"], payload["value"] = "in", value["in"]
    else:
        payload["value"] = value
    with pytest.raises(Refusal):
        ResolutionPredicate.from_payload(payload)


class CountingVersions(Mapping[str, ArmVersion]):
    def __init__(self, versions: dict[str, ArmVersion]) -> None:
        self._versions = versions
        self.lookups = 0

    def __getitem__(self, key: str) -> ArmVersion:
        self.lookups += 1
        return self._versions[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._versions)

    def __len__(self) -> int:
        return len(self._versions)


def test_4329009781_effective_cutoff_resolves_each_shared_input_once() -> None:
    versions: dict[str, ArmVersion] = {"V-0": arm("V-0", "2026-01-01", []), "V-1": arm("V-1", "2026-01-02", ["V-0"])}
    for i in range(2, 60):
        versions[f"V-{i}"] = arm(f"V-{i}", "2026-01-03", [f"V-{i - 1}", f"V-{i - 2}"])
    counting = CountingVersions(versions)
    assert effective_cutoff("V-59", counting).isoformat() == "2026-01-03"
    assert counting.lookups == 60


def test_4329009793_oversized_integers_are_typed_refusals() -> None:
    with pytest.raises(Refusal) as refusal:
        Forecast.from_payload(forecast_payload(point=10**1000))
    assert refusal.value.reason == "invalid_probability"
    from cpe.schemas.forecast import JevRecord

    with pytest.raises(Refusal) as refusal:
        JevRecord.from_payload({"jev_record_id": "J", "event_id": "E", "inputs_digest": HEX, "result_positive": 1,
                                "result_negative": 0, "model_hash": HEX, "routing_result": "r", "cost": 10**1000})
    assert refusal.value.reason == "invalid_number"


def test_4329009804_anchor_verifies_the_chain_against_existing_external_anchors(tmp_path: Path, clock: ManualClock) -> None:
    store = HarnessAnchorStore()
    honest = Ledger(tmp_path / "honest.sqlite", clock, store)
    for i in range(3):
        clock.advance(timedelta(seconds=1))
        honest.append("event", f"r-{i}", {"i": i})
    honest.anchor()
    rewritten = Ledger(tmp_path / "rewritten.sqlite", clock, store)
    for i in range(4):
        clock.advance(timedelta(seconds=1))
        rewritten.append("event", f"r-{i}", {"i": i, "edited": True})
    with pytest.raises(Refusal) as refusal:
        rewritten.anchor()
    assert refusal.value.reason == "anchor_conflict"
    assert len(store.anchors()) == 1
    truncated = Ledger(tmp_path / "truncated.sqlite", clock, store)
    clock.advance(timedelta(seconds=1))
    truncated.append("event", "r-0", {"i": 0})
    with pytest.raises(Refusal) as short:
        truncated.anchor()
    # the ledger's own check refuses before it stages anything, not the store's regression check (issue #37, pass 9)
    assert short.value.reason == "anchor_conflict" and truncated.pending_anchors() == ()
    clock.advance(timedelta(seconds=1))
    honest.append("event", "r-3", {"i": 3})
    assert honest.anchor().prefix_length == 4


@pytest.mark.parametrize("text", ["2026-9-01T00:00:00.000000Z", "2026-09-01T00:00:00.0Z", "2026-09-01T0:00:00.000000Z"])
def test_4329009812_timestamps_must_be_in_the_exact_canonical_form(text: str) -> None:
    with pytest.raises(Refusal) as refusal:
        parse_timestamp(text, "receipt_time")
    assert refusal.value.reason == "invalid_timestamp"
    assert parse_timestamp("2026-09-01T00:00:00.000000Z").month == 9
