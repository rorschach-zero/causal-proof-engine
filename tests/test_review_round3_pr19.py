"""Regression tests for the third review of PR #19 (automatic review at c218c42), the four findings the owner
assigned to the registration follow-up, plus PR #19 deviation 8 (the same gap as finding 4329836216).

Each test fails at ea4ae68 (main after PR #19) and passes after the fix, except the guard test of the
amend-in-place branch (``test_4329836196_a_correction_before_any_registration_still_amends_in_place``), which
passes at both and shows that the closure count leaves a correction without registrations as it was.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from cpe.errors import Refusal
from cpe.registration import CandidateEntry, ClaimPreregistration, CutoffCorrection
from tests.test_registration import arm, day, registration, spec
from tests.test_review_round1_pr19 import claim, make


def test_4329836245_a_candidate_listed_after_the_ledger_clock_is_refused(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)  # the clock is on day 10
    with pytest.raises(Refusal) as refused:
        r.log_candidate(CandidateEntry("cand-F", "F-1", "src", day(11), "registered", "predicate match"))
    assert refused.value.reason == "future_listing"
    assert "F-1" not in r.state().candidate_by_event
    r.log_candidate(CandidateEntry("cand-F", "F-1", "src", day(10), "registered", "predicate match"))
    assert r.state().candidate_by_event["F-1"].listed_at == day(10)


def test_4329836262_one_calibration_record_identifier_binds_at_most_one_claim(tmp_path: Path) -> None:
    r, _, _ = make(tmp_path)
    r.register_claim(claim("claim-1", "cal-1"))
    with pytest.raises(Refusal) as refused:
        r.register_claim(claim("claim-2", "cal-1"))
    assert refused.value.reason == "calibration_record_reserved"
    assert "claim-2" not in r.state().claims
    r.register_claim(claim("claim-2", "cal-2"))


def test_4329836196_a_correction_to_a_consumed_version_withdraws_it_and_its_consumers(tmp_path: Path) -> None:
    r, clock, _ = make(tmp_path)  # C-1 is registered under FULL-1, which consumes A-1; A-1 is no arm of C-1
    _, registered_under = r.correct_cutoff(CutoffCorrection("A-1", date(2026, 1, 20), "ev-2"))
    assert registered_under is True
    state = r.state()
    assert state.arm_versions["A-1"].declared_cutoff == date(2026, 1, 5)  # the registered record is not amended
    assert {"A-1", "FULL-1"} <= state.withdrawn  # RC-150 withdrawal follows the consumption graph (RC-156)
    for version_id in ("A-1", "FULL-1"):
        with pytest.raises(Refusal) as refused:
            r.register_cluster(registration([spec("E-9", "C-9")], "C-9",
                                            arms={"FULL": "FULL-1", "A": "A-1", "DESIGN_C": "DESIGN_C-1"}))
        assert refused.value.reason == "arm_version_withdrawn" and version_id in r.state().withdrawn
    with pytest.raises(Refusal) as consumer:  # a new version cannot build on a withdrawn input either
        r.register_arm_version(arm("FULL-2", "2026-01-03", ["A-1"]))
    assert consumer.value.reason == "arm_version_withdrawn"


def test_4329836196_a_correction_before_any_registration_still_amends_in_place(tmp_path: Path) -> None:
    r, _, _ = make(tmp_path)
    r.register_arm_version(arm("B-1", "2026-01-02"))
    r.register_arm_version(arm("B2-1", "2026-01-02", ["B-1"]))  # a consumer that is registered under no cluster
    _, registered_under = r.correct_cutoff(CutoffCorrection("B-1", date(2026, 1, 4), "ev-2"))
    assert registered_under is False
    state = r.state()
    assert state.arm_versions["B-1"].declared_cutoff == date(2026, 1, 4) and not state.withdrawn


def test_4329836216_deviation_8_an_empty_family_order_is_refused_at_construction() -> None:
    with pytest.raises(Refusal) as refused:
        ClaimPreregistration("c", "fixed_question_set", "Q", "h", day(1), day(60), day(400), "period-balanced",
                             (), (), "cal")
    assert refused.value.reason == "invalid_family"


def test_4329836216_a_claim_is_validated_in_full_before_the_append(tmp_path: Path) -> None:
    r, _, _ = make(tmp_path)
    bad = ClaimPreregistration(" claim-1", "fixed_question_set", "Q", "h", day(1), day(60), day(400),
                               "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1")
    with pytest.raises(Refusal) as refused:
        r.register_claim(bad)
    assert refused.value.reason == "invalid_identifier"
    assert r.state().claims == {}  # the state still replays and holds nothing
