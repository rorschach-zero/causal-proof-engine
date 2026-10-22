"""Whole-codebase audit, pass 2 (issue #37): the provenance and canonical-form findings of the Codex auditor (issue
#37 comment ``6346290601``, findings 9 and 11). Each test failed on the audit commit
``2998824d0330ef028a8cc2cb7682a40f6fc23763``."""
from __future__ import annotations

import pytest

from cpe.canonical import canonical_bytes
from cpe.errors import Refusal
from cpe.validation import check_issuance
from tests.test_input_validation import PROVIDERS, VERSIONS, jev, output
from tools.check_provenance import text_findings, trailer_findings


# 9 (P2): a folded trailer with whitespace before the colon is still a trailer --------------------------------------

def test_codex_9_a_folded_trailer_with_a_spaced_colon_is_found() -> None:
    message = "Fix\n\nCo-Authored-By : Claude\n continuation\n"  # git reads "Co-Authored-By: Claude continuation"
    assert text_findings(message, "m")  # at 2998824: no finding
    assert trailer_findings(message, "m") == ["m: trailer 'Co-Authored-By' (only Reviewed-by is allowed)"]


def test_codex_9_a_folded_reviewed_by_is_still_allowed() -> None:
    message = "Fix\n\nReviewed-by : Salah Aouaj\n <salah@hydeout.ch>\n"
    assert text_findings(message, "m") == [] and trailer_findings(message, "m") == []


# 11 (P3): nesting too deep for the canonical form is a typed refusal -----------------------------------------------

def deep(levels: int) -> list[object]:
    value: list[object] = []
    for _ in range(levels):
        value = [value]
    return value


def test_codex_11_deep_nesting_is_a_typed_refusal() -> None:
    with pytest.raises(Refusal) as refused:
        canonical_bytes(deep(1100))  # type: ignore[arg-type]
    assert refused.value.reason == "nesting_too_deep"  # at 2998824: RecursionError


def test_codex_11_a_deeply_nested_jev_is_a_rejected_issuance() -> None:
    decision = check_issuance("E-1", VERSIONS, [output(p) for p in PROVIDERS], jev(result_positive=deep(1100)),
                              slot_id="primary")
    assert decision.status == "rejected"
    assert [p.reason for p in decision.problems] == ["nesting_too_deep"]
