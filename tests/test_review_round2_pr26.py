"""Regression test for the second review of PR #26 (Codex review at 51fd378).

The test fails at 51fd378 and passes after the fix.
"""
from __future__ import annotations

from cpe.validation import check_issuance
from tests.test_input_validation import PROVIDERS, VERSIONS, jev, output


def test_4333589198_every_output_must_be_for_the_slot_being_issued() -> None:
    revision = [output(p, slot_id="revision-1") for p in PROVIDERS]
    decision = check_issuance("E-1", VERSIONS, revision, jev(), slot_id="primary")
    assert decision.status == "rejected"
    assert {(p.reason, p.subject) for p in decision.problems if p.reason == "wrong_slot"} == {
        ("wrong_slot", f"outputs[{i}]") for i in range(3)}
    mixed = [output("P-A"), output("P-B", slot_id="revision-1"), output("P-C")]
    assert check_issuance("E-1", VERSIONS, mixed, jev(), slot_id="primary").status == "rejected"
    primary = [output(p) for p in PROVIDERS]
    assert check_issuance("E-1", VERSIONS, primary, jev(), slot_id="primary").status == "issuable"
