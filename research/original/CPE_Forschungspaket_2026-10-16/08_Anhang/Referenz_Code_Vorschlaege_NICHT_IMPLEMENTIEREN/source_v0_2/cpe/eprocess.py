"""Commit-before-resolve e-process for pre-registered Brier comparisons (v0.2).

Fixes v0.1 `ChallengerEvidence` (core.py:136-165), which accepted forecast
probabilities at *resolution* time and therefore could not distinguish a
prospective forecast from a hindsight one, had no event identity (the same
outcome could be fed repeatedly), used a static betting fraction, and allowed
betting_fraction == 1 (absorbing zero).

Statistical statement (unchanged, now enforced by the API):
  X_t = Brier(baseline_t) - Brier(challenger_t)  in [-1, 1]
  M_n = prod_{t<=n} (1 + lam_t X_t), lam_t in [0, lam_max], lam_max < 1,
  lam_t measurable w.r.t. information BEFORE outcome t is revealed.
Under H0: E[X_t | F_{t-1}] <= 0 for all t, M is a nonnegative supermartingale
with M_0 = 1 and P(exists n: M_n >= 1/alpha) <= alpha (Ville).

What this does NOT give you: validity if forecasts are edited after commit,
if the pair (baseline, challenger) is chosen after seeing which pair "won",
or if the e-value is compared against many alphas chosen post hoc.
Resolution ORDER matters: events are incorporated in resolution order and
lam_t is computed from previously resolved events only, so delayed labels
are handled correctly as long as `resolve` is called once per event.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import isfinite
from typing import Callable


def _aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.utcoffset() is not None


@dataclass(frozen=True)
class CommittedForecastPair:
    event_id: str
    baseline_p: float
    challenger_p: float
    committed_at: datetime
    resolves_not_before: datetime  # earliest time the outcome can be known


def grapa_lambda(past_x: list[float], lam_max: float = 0.5, shrink: float = 1.0) -> float:
    """Predictable betting fraction from PAST increments only.

    Approximate growth-rate-optimal lambda = clip(mean/ (var + mean^2)) shrunk
    toward 0 for small n. With no history returns 0 (no bet) -> M stays 1.
    Reference idea: Waudby-Smith & Ramdas, "Estimating means of bounded random
    variables by betting" (2020, arXiv:2010.09686). UNVERIFIED here beyond the
    nonnegativity property, which is what validity needs; lambda only affects power.
    """
    n = len(past_x)
    if n < 2:
        return 0.0
    m = sum(past_x) / n
    v = sum((x - m) ** 2 for x in past_x) / (n - 1)
    denom = v + m * m
    if denom <= 0:
        return 0.0
    lam = m / denom
    lam *= n / (n + shrink * 10)  # shrink for small samples
    return float(max(0.0, min(lam_max, lam)))


class CommittedEProcess:
    """E-process over committed (pre-registered) forecast pairs."""

    def __init__(self, lambda_rule: Callable[[list[float]], float] | None = None,
                 lam_max: float = 0.5) -> None:
        if not (0.0 <= lam_max < 1.0):
            raise ValueError('lam_max must be in [0,1); 1 creates an absorbing zero')
        self.lam_max = lam_max
        self._rule = lambda_rule or (lambda past: grapa_lambda(past, lam_max=lam_max))
        self._committed: dict[str, CommittedForecastPair] = {}
        self._resolved: dict[str, int] = {}
        self._x_history: list[float] = []
        self.evalue = 1.0
        self.max_evalue = 1.0

    # ---- commitment phase -------------------------------------------------
    def commit(self, pair: CommittedForecastPair) -> None:
        for p in (pair.baseline_p, pair.challenger_p):
            if not (isfinite(p) and 0.0 <= p <= 1.0):
                raise ValueError('Probabilities must be in [0,1]')
        if not (_aware(pair.committed_at) and _aware(pair.resolves_not_before)):
            raise ValueError('Timestamps must be timezone-aware')
        if pair.resolves_not_before <= pair.committed_at:
            raise ValueError('Forecast must be committed strictly before resolution window')
        if pair.event_id in self._committed:
            raise ValueError(f'Event {pair.event_id} already committed; forecasts are immutable')
        self._committed[pair.event_id] = pair

    # ---- resolution phase -------------------------------------------------
    def resolve(self, event_id: str, outcome: int, resolved_at: datetime) -> float:
        if outcome not in (0, 1):
            raise ValueError('Outcome must be binary')
        if event_id not in self._committed:
            raise ValueError(f'No committed forecast for {event_id}: hindsight entry rejected')
        if event_id in self._resolved:
            raise ValueError(f'Event {event_id} already resolved: duplicate rejected')
        pair = self._committed[event_id]
        if not _aware(resolved_at) or resolved_at < pair.resolves_not_before:
            raise ValueError('Resolution before the declared resolution window is not allowed')
        lam = self._rule(list(self._x_history))  # predictable: uses past only
        if not (0.0 <= lam <= self.lam_max):
            raise ValueError('lambda rule violated [0, lam_max]')
        x = (pair.baseline_p - outcome) ** 2 - (pair.challenger_p - outcome) ** 2
        self.evalue *= (1.0 + lam * x)
        self.max_evalue = max(self.max_evalue, self.evalue)
        self._x_history.append(x)
        self._resolved[event_id] = outcome
        return self.evalue

    # ---- inference ----------------------------------------------------------
    def reject_null(self, alpha: float) -> bool:
        """alpha must be PRE-REGISTERED. Anytime-valid: may be checked at any n."""
        if not 0 < alpha < 1:
            raise ValueError('alpha invalid')
        return self.max_evalue >= 1.0 / alpha  # running max: valid by Ville

    @property
    def n(self) -> int:
        return len(self._resolved)

    @property
    def pending(self) -> int:
        return len(self._committed) - len(self._resolved)
