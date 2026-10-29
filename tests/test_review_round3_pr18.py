"""Regression tests for the third review of PR #18 (review 5590934590 at 998931d), carried by the follow-up pull
request against main. Each test fails at PR #18's head and passes after the fix. Finding 4329664953 (evaluating
the registered predicate against archived source content) is gated on OD9a and has no test here."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry, SourceStatus, adjudicate, classify_forecast
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from tests.test_adjudication import day, observation, record, rule, spec
from tests.test_review_round2_pr18 import registry


def test_4329664923_a_terminal_falsifier_is_bounded_by_its_observable_from_time() -> None:
    falsifier = spec("terminal-falsifier", not_before=20, issuance=(1, 20))
    early = spec("terminal-falsifier", not_before=50, issuance=(1, 5))
    early_payload = {**early.to_payload(), "falsifier_observable_from": day(5).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
    from cpe.schemas import EventSpec

    early = EventSpec.from_payload(early_payload)
    assert early.earliest_knowable_bound == day(5)
    out = adjudicate(early, rule(), [record("r", occurrence=6, published=6)], [], [], day(7))
    assert (out.disposition, out.knowable_at) == ("RESOLVED_NO", day(6))
    still_outside = adjudicate(early, rule(), [record("r", occurrence=4, published=6)], [], [], day(7))
    assert still_outside.disposition == "OPEN"
    assert adjudicate(falsifier, rule(), [record("r", occurrence=21, published=22)], [], [], day(23)).disposition == "RESOLVED_NO"


def test_4329664911_late_public_act_records_are_partitioned_by_publication_time() -> None:
    public = rule(public_act=True)
    late = record("late", occurrence=90, published=118, observed=118, received=118)
    out = adjudicate(spec(), public, [late], [observation(110)], [], day(119))
    assert out.disposition == "RESOLVED_NO" and [d.record_id for d in out.defects] == ["late"]
    timely = record("r", occurrence=90, published=105)
    assert adjudicate(spec(), public, [timely], [], [], day(106)).knowable_at == day(90)


def test_4329664961_a_forecast_at_the_registration_timestamp_is_not_before_registration() -> None:
    assert classify_forecast(day(20), spec(), day(20), None) == "eligible"
    assert classify_forecast(day(19), spec(), day(20), None) == "before_registration"


def test_4329664966_a_status_received_after_finality_does_not_decide(tmp_path: Path) -> None:
    reg, clock, _ = registry(tmp_path, 120)
    reg.declare_source_status(SourceStatus("src", True, day(100)))  # backdated: declared at 100, received at 120
    reg.submit_observation(observation(110))
    clock.set(day(121))
    assert reg.adjudicate("E").disposition == "RESOLVED_NO"


def test_4329664947_an_absence_based_disposition_records_the_observation_receipt(tmp_path: Path) -> None:
    reg, clock, _ = registry(tmp_path, 110)
    reg.submit_observation(observation(110))
    clock.set(day(130))
    out = reg.adjudicate("E")
    assert out.disposition == "RESOLVED_NO" and out.timestamps is not None
    assert out.timestamps.receipt == day(110) and out.timestamps.adjudication == day(130)


@pytest.mark.parametrize("fields", [
    {"occurrence": 103, "published": 100, "observed": 100},
    {"occurrence": 95, "published": 105, "observed": 103},
    {"occurrence": 104, "published": None, "observed": 103},
])
def test_4329664930_evidence_timestamps_are_ordered(fields: dict[str, float | None]) -> None:
    received = record("r", occurrence=fields["occurrence"], published=fields["published"], observed=fields["observed"],
                      received=106)
    with pytest.raises(Refusal) as refused:
        adjudicate(spec(), rule(evidenced=fields["published"] is not None), [received], [], [], day(106))
    assert refused.value.reason == "evidence_order"
