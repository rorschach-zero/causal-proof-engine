"""The statistical second line of T-15: a detector of forecasts that are too good for the information they could use.

The as-of interface is the leakage control (``17`` section 3 item 1, RC-79); this detector only looks for a leak
that bypassed it, for example a feature whose attested ``available_at`` is false. It compares the challenger's Brier
score with the distribution of its Brier scores under shuffled outcome labels, and flags when the improvement over
the mean of that null exceeds a pre-registered bound. Its validation in Phase 1 is the positive control of T-15
(an injected-outcome feature) only; no size or power is claimed. The bound, the permutation count and the seed are
inputs fixed in advance by the caller, never chosen here.
"""
from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass

from cpe.errors import Refusal
from cpe.schemas.common import require_probability


@dataclass(frozen=True)
class LeakReport:
    """The observed Brier score, the shuffled-label null distribution it is compared with, and the verdict."""

    brier: float
    null_briers: tuple[float, ...]
    inflation: float  # mean null Brier minus observed Brier: how much better than chance alignment
    bound: float
    flagged: bool


def brier(forecasts: Sequence[float], outcomes: Sequence[int]) -> float:
    return sum((p - y) ** 2 for p, y in zip(forecasts, outcomes)) / len(forecasts)


def detect_leak(forecasts: Sequence[float], outcomes: Sequence[int], *, bound: float, permutations: int,
                seed: int) -> LeakReport:
    """Flag ``forecasts`` whose Brier score beats the mean of the shuffled-label null by more than ``bound``."""
    if not forecasts or len(forecasts) != len(outcomes):
        raise Refusal("invalid_sample", "forecasts and outcomes are non-empty and of equal length")
    checked = [require_probability(p, f"forecasts[{i}]") for i, p in enumerate(forecasts)]
    if any(isinstance(y, bool) or y not in (0, 1) for y in outcomes):
        raise Refusal("invalid_outcome", "outcomes are 0 or 1")
    if not math.isfinite(bound) or bound < 0:
        raise Refusal("invalid_bound", "the pre-registered bound is a finite non-negative number")
    if isinstance(permutations, bool) or not isinstance(permutations, int) or permutations < 1:  # 4335189809
        raise Refusal("invalid_permutations", "at least one permutation is needed")
    observed = brier(checked, outcomes)
    generator = random.Random(seed)
    shuffled = list(outcomes)
    null = []
    for _ in range(permutations):
        generator.shuffle(shuffled)
        null.append(brier(checked, shuffled))
    inflation = sum(null) / len(null) - observed
    return LeakReport(observed, tuple(null), inflation, bound, inflation > bound)
