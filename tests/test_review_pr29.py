"""Codex's review of PR #29 (hardening H3), finding `4334268788`: git reads a trailer whether or not whitespace
surrounds the colon (`git interpret-trailers --parse` turns `Tested:Bob` and `Tested : Bob` into `Tested: Bob`), so
the trailer check must too. The test fails at 8ae935a and passes after the fix."""
from __future__ import annotations

from tools.check_provenance import trailer_findings


def test_4334268788_a_trailer_without_whitespace_around_the_colon_is_a_finding() -> None:
    for message in ("Fix\n\nTested:Bob", "Fix\n\nTested : Bob", "Fix\n\nTested\t:Bob",
                    "Fix\n\nReviewed-by: Salah Aouaj <salah@hydeout.ch>\nTested:Bob"):
        assert trailer_findings(message, "commit") != [], message
    assert trailer_findings("Fix\n\nReviewed-by:Salah Aouaj <salah@hydeout.ch>", "commit") == []
    assert trailer_findings("Fix\n\nThe body explains:why the change is needed.\nIt has prose lines.", "commit") == []
