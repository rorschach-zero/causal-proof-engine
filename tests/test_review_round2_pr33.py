"""Regression tests for Codex's review of PR #33 at f126085 (round 2). Each fails at f126085 and passes after the
fix."""
from __future__ import annotations

import pytest

from cpe.errors import Refusal
from cpe.pointintime import brier, detect_leak


@pytest.mark.parametrize("forecasts, outcomes", [([0.5, 0.5], [1]), ([], [])])
def test_4335243608_the_public_brier_score_refuses_a_malformed_sample(forecasts: list[float],
                                                                     outcomes: list[int]) -> None:
    with pytest.raises(Refusal) as refused:
        brier(forecasts, outcomes)
    assert refused.value.reason == "invalid_sample"


@pytest.mark.parametrize("bound", [True, False, "0.05", None])
def test_4335243616_a_bound_that_is_not_a_number_is_refused(bound: object) -> None:
    with pytest.raises(Refusal) as refused:
        detect_leak([0.9, 0.1], [1, 0], bound=bound, permutations=10, seed=1)  # type: ignore[arg-type]
    assert refused.value.reason == "invalid_bound"
