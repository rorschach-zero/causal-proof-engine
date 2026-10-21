"""Regression test for Codex's review of PR #32 at c5ba103 (round 1). Fails at c5ba103 and passes after the fix."""
from __future__ import annotations

import pytest

from cpe.adjudication import MEDIA_TYPE_JSON, ArchivedContent, evaluate
from cpe.canonical import sha256_hex
from cpe.errors import Refusal
from tests.test_adjudication import day, spec


@pytest.mark.parametrize("depth", [2_000, 50_000])
def test_4335042318_deeply_nested_content_is_a_typed_refusal(depth: int) -> None:
    data = b'{"sel":{"f":' + b"[" * depth + b"]" * depth + b"}}"
    content = ArchivedContent(data, sha256_hex(data), MEDIA_TYPE_JSON, "src", day(0))
    with pytest.raises(Refusal) as refused:
        evaluate(spec().predicate, content)
    assert refused.value.reason == "non_canonical_content"
