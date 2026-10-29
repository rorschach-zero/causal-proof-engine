"""Correlation-aware multi-model fusion with explicit abstention (v0.2).

Mandatory inputs per event: an interval forecast from EACH of the three LLM
researchers (Claude, OpenAI, Gemini) and a Jev triage record. Missing mandatory
input => decision RE_RESEARCH, never a silent 2-of-3.

Fusion is NOT majority voting:
  1. Each forecaster's historical standardized errors e_i = (p_i - y) are used to
     estimate the error correlation matrix R (shrunk toward identity).
  2. Weights are the minimum-variance pooling weights w = R^-1 1 / (1' R^-1 1),
     clipped to [0,1] and renormalised (if clipping is needed we fall back to
     equal weights and flag it). Three models that always agree therefore
     count roughly as ONE source, not three.
  3. The fused credal interval is the convex combination of the input intervals.
  4. Abstention is explicit: large disagreement, wide fused interval, a model's
     abstention, or Jev flagging the evidence as not a dated primary claim all
     stop the pipeline with a typed reason.

All thresholds are pre-registered constants (see FusionPolicy); they are not
tuned on the live ledger.

HYPOTHESIS (untested): that this fusion has lower Brier than the best single
model on prospectively registered events. See SCIENTIFIC_EXPERIMENTS.md H1/H3.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence
import numpy as np


class Decision(str, Enum):
    FORECAST = 'forecast'
    ABSTAIN = 'abstain'
    RE_RESEARCH = 're_research'


@dataclass(frozen=True)
class ModelInterval:
    forecaster: str
    p_low: float
    p_high: float
    abstained: bool = False

    @property
    def mid(self) -> float:
        return 0.5 * (self.p_low + self.p_high)


@dataclass(frozen=True)
class JevTriage:
    """Typed Jev outputs. These are classification probabilities, NOT investment probabilities."""
    dated_primary_evidence: float      # noul: evidence has date + traceable primary source
    relevance_to_event: float          # noul: evidence bears on the registered event
    complement_gap: float              # |p(X) + p(not X) - 1| measured on this call


@dataclass(frozen=True)
class FusionPolicy:
    required: tuple[str, ...] = ('claude', 'openai', 'gemini')
    max_disagreement: float = 0.30      # max spread of midpoints before abstain
    max_fused_width: float = 0.35
    min_jev_primary: float = 0.60
    min_jev_relevance: float = 0.50
    max_jev_complement_gap: float = 0.15
    shrink_to_identity: float = 0.30    # Ledoit-Wolf style shrinkage weight
    min_history: int = 20               # below this, equal weights


@dataclass(frozen=True)
class FusionResult:
    decision: Decision
    p_low: float
    p_high: float
    weights: dict[str, float]
    disagreement: float
    effective_models: float
    reasons: tuple[str, ...]


def error_correlation(errors: np.ndarray, shrink: float) -> np.ndarray:
    """errors: (n_events, n_models) matrix of p_i - y. Returns shrunk correlation."""
    n, m = errors.shape
    if n < 2:
        return np.eye(m)
    c = np.corrcoef(errors, rowvar=False)
    c = np.nan_to_num(c, nan=0.0)
    np.fill_diagonal(c, 1.0)
    return (1 - shrink) * c + shrink * np.eye(m)


def min_variance_weights(R: np.ndarray) -> tuple[np.ndarray, bool]:
    m = R.shape[0]
    ones = np.ones(m)
    try:
        inv = np.linalg.solve(R, ones)
    except np.linalg.LinAlgError:
        return ones / m, True
    w = inv / inv.sum()
    if (w < 0).any() or not np.isfinite(w).all():
        return ones / m, True  # fallback flagged
    return w, False


def effective_models(w: np.ndarray, R: np.ndarray) -> float:
    return float(w.sum() ** 2 / (w @ R @ w))


def fuse(intervals: Sequence[ModelInterval], jev: JevTriage | None,
         error_history: np.ndarray | None, policy: FusionPolicy = FusionPolicy()) -> FusionResult:
    reasons: list[str] = []
    by_name = {iv.forecaster: iv for iv in intervals}
    missing = [r for r in policy.required if r not in by_name]
    if missing or jev is None:
        return FusionResult(Decision.RE_RESEARCH, 0.0, 1.0, {}, 1.0, 0.0,
                            tuple([f'missing mandatory input: {m}' for m in missing] + ([] if jev else ['missing jev triage'])))
    if jev.complement_gap > policy.max_jev_complement_gap:
        reasons.append(f'jev incoherent on this item (complement gap {jev.complement_gap:.2f})')
    if jev.dated_primary_evidence < policy.min_jev_primary:
        reasons.append('jev: evidence not a dated primary claim')
    if jev.relevance_to_event < policy.min_jev_relevance:
        reasons.append('jev: evidence not relevant to registered event')
    if reasons:
        return FusionResult(Decision.RE_RESEARCH, 0.0, 1.0, {}, 1.0, 0.0, tuple(reasons))

    ordered = [by_name[r] for r in policy.required]
    if any(iv.abstained for iv in ordered):
        return FusionResult(Decision.ABSTAIN, 0.0, 1.0, {}, 1.0, 0.0,
                            tuple(f'{iv.forecaster} abstained' for iv in ordered if iv.abstained))
    m = len(ordered)
    if error_history is not None and error_history.shape[0] >= policy.min_history and error_history.shape[1] == m:
        R = error_correlation(error_history, policy.shrink_to_identity)
    else:
        R = np.eye(m)
        reasons.append('insufficient history: equal weights')
    w, fell_back = min_variance_weights(R)
    if fell_back:
        reasons.append('weights fell back to equal (negative or singular solution)')
    lows = np.array([iv.p_low for iv in ordered]); highs = np.array([iv.p_high for iv in ordered])
    mids = 0.5 * (lows + highs)
    p_low = float(w @ lows); p_high = float(w @ highs)
    disagreement = float(mids.max() - mids.min())
    n_eff = effective_models(w, R)
    weights = {iv.forecaster: float(wi) for iv, wi in zip(ordered, w)}
    if disagreement > policy.max_disagreement:
        reasons.append(f'disagreement {disagreement:.2f} > {policy.max_disagreement}')
        return FusionResult(Decision.ABSTAIN, p_low, p_high, weights, disagreement, n_eff, tuple(reasons))
    if (p_high - p_low) > policy.max_fused_width:
        reasons.append(f'fused width {p_high - p_low:.2f} > {policy.max_fused_width}')
        return FusionResult(Decision.ABSTAIN, p_low, p_high, weights, disagreement, n_eff, tuple(reasons))
    return FusionResult(Decision.FORECAST, p_low, p_high, weights, disagreement, n_eff, tuple(reasons))
