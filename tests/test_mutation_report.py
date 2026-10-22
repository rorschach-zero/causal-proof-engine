"""The mutation report tool (``tools/mutation_report.py``): its structural rules and the reproduction of the committed
classification (``research/19`` section 10)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.mutation_report import apply_changes, main, parse_name, rule_for

ORIGINAL = '''def f(value: object, field: str = "value") -> str:
    if not isinstance(value, str):
        raise Refusal("invalid", f"{field} must be a string")
    return value.encode("ascii").decode("ascii")'''


@pytest.mark.parametrize("mutated, category", [
    (ORIGINAL.replace('f"{field} must be a string"', "None"), "text"),
    (ORIGINAL.replace('"{field} must be a string"', '"XX{field} must be a stringXX"'), "text"),
    (ORIGINAL.replace(', f"{field} must be a string")', ")"), "text"),
    (ORIGINAL.replace('field: str = "value"', 'field: str = "VALUE"'), "text"),
    (ORIGINAL.replace('encode("ascii")', 'encode("ASCII")'), "equivalent"),
])
def test_rules_classify_messages_labels_and_codec_case(mutated: str, category: str) -> None:
    ruled = rule_for(ORIGINAL, mutated)
    assert ruled is not None and ruled[0] == category


@pytest.mark.parametrize("mutated", [
    ORIGINAL.replace('Refusal("invalid"', 'Refusal("XXinvalidXX"'),  # the reason code is behaviour
    ORIGINAL.replace("if not isinstance", "if isinstance"),
    ORIGINAL.replace('decode("ascii")', 'decode("utf-8")'),
])
def test_behaviour_is_never_classified_by_a_rule(mutated: str) -> None:
    assert rule_for(ORIGINAL, mutated) is None


def test_changes_are_applied_by_line() -> None:
    assert apply_changes("a\nb\nc", [[1, 2, ["B", "B2"]]]) == "a\nB\nB2\nc"
    assert parse_name("cpe.ledger.store.xǁLedgerǁappend__mutmut_12") == ("cpe.ledger.store", "xǁLedgerǁappend")


def test_the_committed_classification_reproduces(capsys: pytest.CaptureFixture[str]) -> None:
    data = Path(__file__).resolve().parent.parent / "research" / "mutation"
    status = main(["classify", "--results", str(data / "results.txt"), "--evidence", str(data / "evidence.json"),
                   "--manual", str(data / "manual.tsv"), "--table", str(data / "classification.tsv"), "--check"])
    assert status == 0, capsys.readouterr().out
