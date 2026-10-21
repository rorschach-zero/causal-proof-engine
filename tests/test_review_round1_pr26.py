"""Regression tests for the review of PR #26 (Codex review at 2bac84f), one per finding applied.

Each test fails at 2bac84f and passes after the fix. Finding 4333446625 (binding the Jev record to the digest of
its triaged inputs) needs a definition of that input bundle, which `17` does not give; it is listed for the owner
and has no test.
"""
from __future__ import annotations

from cpe.schemas import Forecast, ResearchOutput
from cpe.validation import check_issuance
from tests.test_input_validation import PROVIDERS, VERSIONS, jev, output
from tests.test_schemas import HEX



def test_4333446622_an_object_that_cannot_serialise_rejects_instead_of_crashing() -> None:
    broken = ResearchOutput("P-B", "E-1", Forecast("E-1", "P-B", "primary", "P-B-1", 0.4, 0.3, 0.5, HEX, HEX, (),
                                                   claimed_issued_at="yesterday"),  # type: ignore[arg-type]
                            HEX, ())
    decision = check_issuance("E-1", VERSIONS, [output("P-A"), broken, output("P-C")], jev(), slot_id="primary")
    assert decision.status == "rejected"
    assert [(p.reason, p.subject) for p in decision.problems][0] == ("invalid_object", "outputs[1]")


def test_4333446630_an_output_of_another_arm_version_than_the_registered_one_rejects() -> None:
    later = output("P-B", arm_version_id="P-B-2")
    decision = check_issuance("E-1", VERSIONS, [output("P-A"), later, output("P-C")], jev(), slot_id="primary")
    assert decision.status == "rejected"
    assert [(p.reason, p.subject) for p in decision.problems] == [("wrong_arm_version", "outputs[1]"),
                                                                 ("missing_provider", "P-B")]
    assert check_issuance("E-1", VERSIONS, [output(p) for p in PROVIDERS], jev(), slot_id="primary").status == "issuable"
