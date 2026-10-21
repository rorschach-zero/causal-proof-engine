"""Regression tests for the second review of PR #18 (review 5590659094 at 87c1fc7), one per finding applied.

Each test fails at 87c1fc7 and passes after the fix. Finding 4329442698 (the reviewer's name in a test
docstring) is listed for the owner in the pull request and has no test.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry, ResolutionRecord, SourceStatus, adjudicate
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from tests.test_adjudication import day, observation, record, rule, spec, submit


def registry(tmp_path: Path, at: float) -> tuple[AdjudicationRegistry, ManualClock, Ledger]:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    reg = AdjudicationRegistry(ledger)
    reg.register_rule(rule())
    reg.register_event(spec())
    clock.set(day(at))
    return reg, clock, ledger


def test_4329442644_a_timestamp_less_falsifier_report_is_void_not_no() -> None:
    falsifier = spec("terminal-falsifier")
    out = adjudicate(falsifier, rule(), [record("r", published=61)], [], [], day(62))
    assert out.disposition == "VOID" and "RC-71" in out.basis
    late = record("r", published=61, lateness=True)
    assert adjudicate(falsifier, rule(), [late], [], [], day(62)).disposition == "OPEN"
    survived = adjudicate(falsifier, rule(), [late], [observation(110)], [], day(111))
    assert survived.disposition == "RESOLVED_YES" and survived.defects == ()


def test_4329442661_an_incident_found_after_the_disposition_is_persisted_and_replayed(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 111)
    reg.submit_observation(observation(110))
    first = reg.adjudicate("E")
    assert first.disposition == "RESOLVED_NO" and first.incidents == ()
    clock.set(day(113))
    submit(reg, record("r", occurrence=95, published=105))
    again = reg.adjudicate("E")
    assert again.disposition == "RESOLVED_NO"
    assert [(i.kind, i.reference_id) for i in again.incidents] == [("receipt_lag", "r")]
    assert reg.adjudicate("E") == again
    assert [r.kind for r in ledger.records()].count("integrity_incident") == 1
    ledger.close()
    reopened = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    assert reopened.adjudicate("E") == again


def test_4329442606_an_occurrence_after_the_receipt_is_refused(tmp_path: Path) -> None:
    with pytest.raises(Refusal) as pure:
        adjudicate(spec(), rule(), [record("r", occurrence=120, published=105, received=110)], [], [], day(110))
    assert pure.value.reason == "evidence_after_receipt"
    reg, _, _ = registry(tmp_path, 110)
    with pytest.raises(Refusal) as refused:
        submit(reg, record("r", occurrence=120, published=105))
    assert refused.value.reason == "evidence_after_receipt"


def test_4329442625_a_record_received_after_now_is_refused() -> None:
    with pytest.raises(Refusal) as refused:
        adjudicate(spec(), rule(), [record("r", occurrence=95, published=105, received=120)], [], [], day(100))
    assert refused.value.reason == "receipt_after_now"


def test_4329442739_a_record_id_at_the_identifier_limit_is_admitted(tmp_path: Path) -> None:
    reg, _, ledger = registry(tmp_path, 106)
    long_id = "r" * 256
    submit(reg, record(long_id, occurrence=95, published=105))
    assert reg.adjudicate("E").deciding_record_id == long_id
    assert all(len(r.record_id) <= 256 for r in ledger.records())


def test_4329442713_an_expired_no_on_a_public_act_is_knowable_at_the_occurrence() -> None:
    out = adjudicate(spec(), rule(public_act=True), [record("r", occurrence=105, published=108)], [], [], day(109))
    assert (out.disposition, out.knowable_at) == ("EXPIRED_NO", day(105))


def test_4329442687_a_status_of_another_source_is_refused() -> None:
    with pytest.raises(Refusal) as refused:
        adjudicate(spec(), rule(), [], [observation(110)], [SourceStatus("other", True, day(100))], day(111))
    assert refused.value.reason == "wrong_source"


def test_4329442759_an_event_is_registered_before_its_issuance_window_and_after_its_source_rule(tmp_path: Path) -> None:
    clock = ManualClock(day(25))
    reg = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    with pytest.raises(Refusal) as no_rule:
        reg.register_event(spec())
    assert no_rule.value.reason == "unknown_source"
    clock.set(day(10))
    reg.register_rule(rule())
    clock.set(day(25))
    with pytest.raises(Refusal) as late:
        reg.register_event(spec())
    assert late.value.reason == "late_registration"
    clock.set(day(19))
    reg.register_event(spec())
    clock.set(day(25))
    reg.register_event(spec())  # the same registration again is idempotent


STAMP = day(95).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@pytest.mark.parametrize("payload_fields, fields", [
    ({"claim": "not-occurred", "occurrence_time": STAMP}, {"claim": "not-occurred", "occurrence_time": day(95)}),
    ({"claim": "not-occurred", "lateness_evidence": True}, {"claim": "not-occurred", "lateness_evidence": True}),
    ({"claim": "occurred", "definitive": True}, {"claim": "occurred", "definitive": True}),
])
def test_4329442770_an_internally_contradictory_record_is_refused(payload_fields: dict[str, object],
                                                                  fields: dict[str, object]) -> None:
    payload = {"record_id": "r", "event_id": "E", "source_id": "src", "content_digest": "0" * 64,
               "first_observed_at": day(1).strftime("%Y-%m-%dT%H:%M:%S.%fZ"), **payload_fields}
    with pytest.raises(Refusal) as refused:
        ResolutionRecord.from_payload(payload)
    assert refused.value.reason == "inconsistent_record"
    with pytest.raises(Refusal):
        ResolutionRecord("r", "E", "src", first_observed_at=day(1), content_digest="0" * 64,
                         **fields)  # type: ignore[arg-type]


def test_4329442675_the_status_in_force_at_finality_decides(tmp_path: Path) -> None:
    failed, recovered = SourceStatus("src", True, day(100)), SourceStatus("src", False, day(120))
    out = adjudicate(spec(), rule(), [], [observation(110)], [failed, recovered], day(121))
    assert out.disposition == "VOID"
    early_recovery = SourceStatus("src", False, day(105))
    assert adjudicate(spec(), rule(), [], [observation(110)], [failed, early_recovery], day(121)).disposition == "RESOLVED_NO"
    reg, clock, ledger = registry(tmp_path, 100)
    reg.declare_source_status(failed)
    clock.set(day(120))
    reg.declare_source_status(recovered)
    reg.submit_observation(observation(110))
    clock.set(day(121))
    assert reg.adjudicate("E").disposition == "VOID"
    ledger.close()
    reopened = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    assert reopened.adjudicate("E").disposition == "VOID"
