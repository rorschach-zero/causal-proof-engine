"""Whole-codebase audit, pass 2 (issue #37): the reproduced defects. Each test failed on the audit commit
``2998824d0330ef028a8cc2cb7682a40f6fc23763``."""
from __future__ import annotations

import pytest

from cpe.canonical import canonical_bytes
from cpe.errors import Refusal


class HidingInt(int):
    """An integer whose own ``__repr__`` hides its size."""

    def __repr__(self) -> str:
        return "1"


class FailingInt(int):
    """An integer whose own ``__repr__`` fails."""

    def __repr__(self) -> str:
        raise ValueError("no representation")


# P3: the integer limit is judged on the form json writes, not on a subclass's repr (PR #39 review 4348066271) -----

def test_a_huge_integer_subclass_is_still_refused() -> None:
    with pytest.raises(Refusal) as refused:
        canonical_bytes({"value": HidingInt(10 ** 5000)})
    assert refused.value.reason == "integer_too_large"


def test_a_small_integer_subclass_with_a_failing_repr_is_canonical() -> None:
    assert canonical_bytes({"value": FailingInt(5)}) == canonical_bytes({"value": 5})
