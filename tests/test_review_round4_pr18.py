"""Regression tests for the fourth review of PR #18 (review at c6e3bbe), the three findings the owner assigned to
the adjudication follow-up. Each test fails at 06422fa and passes after the fix. Finding 4329838021 (the
monotone-publication condition is the source's declared promise) is a specification question and has no test."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.adjudication import adjudicate
from cpe.adjudication.registry import KIND_DEFECT
from cpe.canonical import JsonValue
from cpe.ledger import Ledger, Record
from cpe.ledger.store import Admit
from tests.test_adjudication import day, observation, record, rule, spec, submit
from tests.test_review_round2_pr18 import registry


def test_4329838002_a_late_record_proving_expiry_decides_before_any_disposition() -> None:
    # deadline 100, finality 110; no observation; the source is not monotone: the only evidence is published late
    after_deadline = record("late", occurrence=103, published=115, observed=115, received=115)
    out = adjudicate(spec(), rule(), [after_deadline], [], [], day(120))
    assert out.disposition == "EXPIRED_NO" and out.deciding_record_id == "late"
    assert [(i.kind, i.reference_id) for i in out.incidents] == [("late_publication", "late")]
    assert out.timestamps is not None and out.timestamps.publication == day(115)
    definitive = record("d", claim="not-occurred", definitive=True, published=115, observed=115, received=115)
    assert adjudicate(spec(), rule(), [definitive], [], [], day(120)).disposition == "EXPIRED_NO"
    # a late report of a timely occurrence proves nothing on its own: the event stays open without an observation
    timely_claim = record("t", occurrence=90, published=115, observed=115, received=115)
    assert adjudicate(spec(), rule(), [timely_claim], [], [], day(120)).disposition == "OPEN"
    # an archived observation of absence still decides NO, the late expiry record only agrees
    with_observation = adjudicate(spec(), rule(), [after_deadline], [observation(110)], [], day(120))
    assert with_observation.disposition == "RESOLVED_NO" and with_observation.deciding_record_id is None


def test_4329838030_a_retry_after_the_disposition_commit_adds_no_duplicate_defect(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 110)
    reg.submit_observation(observation(110))
    clock.set(day(111))
    assert reg.adjudicate("E").disposition == "RESOLVED_NO"  # committed before the late record exists
    clock.set(day(120))
    submit(reg, record("late", occurrence=90, published=115, observed=115))  # its defect is a side row
    original = ledger.append

    def dies_on_the_first_defect_row(kind: str, record_id: str, payload: JsonValue, expected_head: str | None = None,
                                     admit: Admit | None = None) -> Record:
        if kind == KIND_DEFECT:
            ledger.append = original  # type: ignore[method-assign]
            raise RuntimeError("process died after the disposition commit")
        return original(kind, record_id, payload, expected_head, admit)

    ledger.append = dies_on_the_first_defect_row  # type: ignore[method-assign, assignment]
    with pytest.raises(RuntimeError):  # the fault fires (issue #37, pass 7: it never did, defects being embedded)
        reg.adjudicate("E")
    ledger.append = original  # type: ignore[method-assign]
    assert KIND_DEFECT not in [r.kind for r in ledger.records()]
    out = reg.adjudicate("E")
    assert out.disposition == "RESOLVED_NO" and [d.record_id for d in out.defects] == ["late"]
    replayed = reg.state().events["E"].disposition
    assert replayed is not None and [d.record_id for d in replayed.defects] == ["late"]
    assert reg.adjudicate("E") == out


def test_4329838013_replay_ignores_records_of_other_kinds_whatever_their_payload(tmp_path: Path) -> None:
    reg, clock, ledger = registry(tmp_path, 50)
    ledger.append("forecast", "other:1", 7)  # another registry's kinds, whatever their payload
    ledger.append("gate_check", "other:2", "scalar")
    assert reg.state().events["E"].spec is not None
    clock.set(day(120))
    reg.submit_observation(observation(110))
    assert reg.adjudicate("E").disposition == "RESOLVED_NO"
