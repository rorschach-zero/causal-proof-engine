"""Hardening pass H1 (ledger, adjudication, registration, canonical), the findings the owner's delegate decided
to fix on 2026-10-21 (parent session, after PR #26). Each test fails at 2122567 and passes after the fix."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from cpe.adjudication import SourceStatus, adjudicate
from cpe.canonical import canonical_bytes
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Anchor, HarnessAnchorStore, Ledger
from cpe.registration import CandidateEntry
from cpe.validation import check_issuance
from tests.test_adjudication import day, observation, record, rule, spec
from tests.test_input_validation import PROVIDERS, VERSIONS, jev, output
from tests.test_registration import day as rday
from tests.test_review_round1_pr19 import make
from tests.test_review_round2_pr18 import registry


class LandedThenTimeoutStore(HarnessAnchorStore):
    """Commits the next anchor and then reports an acknowledgement timeout, once."""

    def __init__(self) -> None:
        super().__init__()
        self.land_then_fail = False

    def publish(self, anchor: Anchor) -> None:
        super().publish(anchor)
        if self.land_then_fail:
            self.land_then_fail = False
            raise Refusal("anchor_store_unavailable", "acknowledgement timed out after the anchor landed")


def test_4329904090_a_retried_anchor_settles_with_the_external_anchor_time(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    store = LandedThenTimeoutStore()
    ledger = Ledger(tmp_path / "l.sqlite", clock, store)
    ledger.append("event", "e-1", {"i": 1})
    store.land_then_fail = True
    with pytest.raises(Refusal):
        ledger.anchor()
    clock.set(day(2))
    settled = ledger.anchor()
    assert settled == store.anchors()[0] and settled.published_at.startswith("2026-01-02")  # day(1), the first attempt
    assert ledger.local_anchors() == store.anchors()  # the local copy names the time the store holds


def test_4330044561_the_deciding_timely_public_act_is_the_earliest_knowable_one() -> None:
    public = rule(public_act=True)
    records = [record("later-occurrence", occurrence=95, published=100), record("earlier", occurrence=90, published=105)]
    out = adjudicate(spec(), public, records, [], [], day(106))
    assert out.disposition == "RESOLVED_YES" and out.knowable_at == day(90) and out.deciding_record_id == "earlier"


def test_4330044547_a_public_occurrence_sets_knowable_at_even_when_published_late() -> None:
    late = record("late", occurrence=90, published=118, observed=118, received=118)
    out = adjudicate(spec(), rule(public_act=True), [late], [observation(110)], [], day(119))
    assert out.disposition == "RESOLVED_NO"  # the publication partition decides the disposition (RC-88, RC-105)
    assert out.knowable_at == day(90)  # the public act made the outcome determinable at 90 (RC-146)
    assert [d.record_id for d in out.defects] == ["late"]
    private = adjudicate(spec(), rule(), [late], [observation(110)], [], day(119))
    assert private.knowable_at == day(110)  # not a public act: finality


def test_4330044580_a_status_decided_void_records_the_status_receipt(tmp_path: Path) -> None:
    reg, clock, _ = registry(tmp_path, 101)
    reg.declare_source_status(SourceStatus("src", True, day(100)))  # received at 101, before finality
    clock.set(day(120))
    reg.submit_observation(observation(110))  # received at 120
    clock.set(day(121))
    out = reg.adjudicate("E")
    assert out.disposition == "VOID" and out.timestamps is not None and out.timestamps.receipt == day(101)


@pytest.mark.parametrize("receipt", [105.0, 125.0])
def test_4330044588_observation_receipts_are_bounded_by_the_observation_and_now(receipt: float) -> None:
    with pytest.raises(Refusal) as refused:
        adjudicate(spec(), rule(), [], [observation(110)], [], day(120), {"obs-110": day(receipt)})
    assert refused.value.reason == ("evidence_after_receipt" if receipt < 110 else "receipt_after_now")


def test_4333728786_a_cyclic_value_is_a_refusal_not_a_recursion_error() -> None:
    cyclic: list[object] = []
    cyclic.append(cyclic)
    with pytest.raises(Refusal) as refused:
        canonical_bytes(cyclic)  # type: ignore[arg-type]
    assert refused.value.reason == "cyclic_value"
    looped: dict[str, object] = {}
    looped["self"] = looped
    decision = check_issuance("E-1", VERSIONS, [output(p) for p in PROVIDERS], jev(result_positive=looped),
                              slot_id="primary")
    assert decision.status == "rejected" and decision.problems[0].reason == "cyclic_value"


def test_4330096692_a_naive_listing_time_is_a_refusal(tmp_path: Path) -> None:
    r, _, _ = make(tmp_path)
    with pytest.raises(Refusal) as refused:
        r.log_candidate(CandidateEntry("cand-F", "F-1", "src", datetime(2026, 1, 5), "registered", "ok"))
    assert refused.value.reason == "naive_timestamp"


def test_4330096714_the_listing_time_is_checked_against_the_appended_receipt(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)  # high-water mark at day 10
    clock.set(rday(20))
    r.before_write = lambda: clock.set(rday(12))  # the clock moves back between the decision and the append
    with pytest.raises(Refusal) as refused:
        r.log_candidate(CandidateEntry("cand-F", "F-1", "src", rday(15), "registered", "ok"))
    assert refused.value.reason == "future_listing"
    assert "F-1" not in r.state().candidate_by_event


def test_ledger_append_admit_hook_sees_the_receipt(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    seen: list[datetime] = []
    ledger.append("event", "e-1", {"i": 1}, admit=seen.append)
    assert seen == [day(1)]

    def refuse(receipt: datetime) -> None:
        raise Refusal("refused_at_receipt", "")

    with pytest.raises(Refusal):
        ledger.append("event", "e-2", {"i": 2}, admit=refuse)
    assert ledger.state.count == 1
