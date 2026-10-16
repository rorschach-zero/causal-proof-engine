"""Robust multi-scenario allocation (v0.2) replacing the single-bet binary Kelly
rule of v0.1 (core.py:95-128) for portfolio use.

Model: K joint scenarios, N fully paid instruments. R[k, i] = total return
multiple minus 1 of instrument i in scenario k (so -1 = total loss, after
costs, FX and taxes supplied by the caller). Uncertainty about the scenario
probabilities is a finite credal set Q = {q_1..q_J} (vertices of the feasible
polytope from cpe.coherence or hand-specified stress vectors).

Objective:  max_w  min_{q in Q}  sum_k q_k log(1 + R_k . w)
Constraints: w >= 0; sum w <= gross_cap; w_i <= cap_i;
             worst-scenario loss  -min_k R_k . w  <= max_loss (hard, path-free).
             Optional fractional-Kelly: w <- kelly_fraction * w.

Why this is still a toy: scenarios are discrete, joint dependence must be
encoded in the scenario set by the caller, there is no intra-horizon path,
margin, liquidation, option exercise or re-balancing. It IS enough for a
$1,000 pilot of fully paid instruments. Hypothesis, not a theorem: that
fractional robust Kelly on calibrated credal inputs avoids ruin; ruin remains
possible if inputs are miscalibrated (see spec §6).
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize


@dataclass(frozen=True)
class AllocationResult:
    weights: np.ndarray
    robust_log_growth: float
    worst_scenario_loss: float
    binding: tuple[str, ...]
    interpretation: str = ('CONDITIONAL on the scenario set, credal set and after-cost return inputs; '
                           'not a forecast and not a guarantee.')


def robust_allocation(R: np.ndarray, Q: np.ndarray, *, gross_cap: float = 0.25,
                      caps: np.ndarray | None = None, max_loss: float = 0.10,
                      kelly_fraction: float = 0.5) -> AllocationResult:
    R = np.asarray(R, float); Q = np.asarray(Q, float)
    K, N = R.shape
    if Q.ndim != 2 or Q.shape[1] != K:
        raise ValueError('Q must be (J, K)')
    if (Q < -1e-12).any() or not np.allclose(Q.sum(axis=1), 1.0, atol=1e-9):
        raise ValueError('each row of Q must be a probability vector')
    if (R < -1).any():
        raise ValueError('return multiple below zero (loss > 100%) not allowed for fully paid instruments')
    if not (0 < gross_cap <= 1 and 0 < kelly_fraction <= 1 and 0 < max_loss <= 1):
        raise ValueError('bad caps')
    caps = np.full(N, gross_cap) if caps is None else np.asarray(caps, float)

    def growth_q(w, q):
        return float(q @ np.log1p(R @ w))

    # epigraph: maximize t s.t. t <= growth_q(w,q) for all q
    x0 = np.concatenate([np.full(N, min(0.01, gross_cap / N)), [0.0]])
    cons = []
    for j in range(Q.shape[0]):
        cons.append({'type': 'ineq', 'fun': (lambda x, j=j: growth_q(x[:N], Q[j]) - x[N])})
    cons.append({'type': 'ineq', 'fun': lambda x: gross_cap - x[:N].sum()})
    cons.append({'type': 'ineq', 'fun': lambda x: max_loss + (R @ x[:N]).min()})  # worst loss <= max_loss
    bounds = [(0.0, float(c)) for c in caps] + [(None, None)]
    res = minimize(lambda x: -x[N], x0, method='SLSQP', bounds=bounds, constraints=cons,
                   options={'maxiter': 500, 'ftol': 1e-12})
    if not res.success:
        raise ArithmeticError(f'allocation solver failed: {res.message}')
    w = np.clip(res.x[:N], 0, caps) * kelly_fraction
    rg = min(growth_q(w, q) for q in Q)
    worst = float(-(R @ w).min())
    binding = []
    if abs(w.sum() / kelly_fraction - gross_cap) < 1e-6: binding.append('gross_cap')
    if abs(worst / kelly_fraction - max_loss) < 1e-6: binding.append('max_loss')
    for i in range(N):
        if abs(w[i] / kelly_fraction - caps[i]) < 1e-6: binding.append(f'cap[{i}]')
    return AllocationResult(w, rg, worst, tuple(binding))
