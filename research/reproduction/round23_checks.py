"""Round-23 checks for the Codex findings on PR #4 at d7661b6 (no reference code, no network).

Codex's automatic review of d7661b6, posted as PR #4 comment 6248847770 (three findings, keyed /1 to /3). Items /1
(RC-177, a commit-identity claim) and /2 (RC-178, a squash-message claim) are checked against the repository's refs
and the PR #4 timeline and have no block here. Item /3 (RC-179) is checked below.

Setting of 17 section 3 item 3 (RC-117, RC-173): on one continuous null point, c* is the smallest value at which an
exact one-sided Clopper-Pearson upper bound at confidence 1 - g on the simulated rejection rate over R replications
is <= L. With m = the largest count whose bound is <= L, c* sits just above the (m + 1)-th largest simulated
statistic, so its true size is the tail probability of that order statistic, distributed Beta(m + 1, R - m) exactly
for any continuous statistic. An analyst who runs k seeds and commits the one with the smallest c* keeps the largest
of k independent such sizes.
"""
import json
import numpy as np
from scipy.stats import beta, norm

out = {}

def m_max(R, L, g):
    """Largest rejection count m whose exact one-sided upper bound at confidence 1 - g is <= L."""
    lo, hi = 0, R
    if beta.ppf(1 - g, 1, R) > L:
        return -1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if beta.ppf(1 - g, mid + 1, R - mid) <= L:
            lo = mid
        else:
            hi = mid - 1
    return lo

def selected(R, L, g, k):
    """Exact law of the true size of the smallest c* over k seeds: the max of k iid Beta(m + 1, R - m)."""
    m = m_max(R, L, g)
    d = beta(m + 1, R - m)
    p_exceed = 1.0 - d.cdf(L) ** k
    xs = np.linspace(0.0, 2 * L, 200001)
    pdf_max = k * d.cdf(xs) ** (k - 1) * d.pdf(xs)
    mean = float(np.trapezoid(xs * pdf_max, xs))
    q99 = float(d.ppf(0.99 ** (1.0 / k)))
    return {'m': m, 'P(true size > L)': round(float(p_exceed), 4), 'mean true size': round(mean, 5),
            '99th percentile true size': round(q99, 5)}

# ================= 6248847770/3 (RC-179): seed selection voids the gamma_cal coverage =================
# L = alpha - eta_max - gamma_cal at eta_max = 0, alpha = 0.05, gamma_cal = 0.01, K = 1; g = gamma_cal / K.
L, G = 0.04, 0.01
rc179 = {'L': L, 'gamma_cal': G, 'K': 1}
for R in (20000, 100000):
    rc179[f'R={R}'] = {f'k={k}': selected(R, L, G, k) for k in (1, 2, 5, 10, 20, 50)}

# Monte Carlo cross-check of the exact law at R = 20,000, k = 10, with standard normal null statistics.
rng = np.random.default_rng(2179)
R, k, CAL = 20000, 10, 2000
m = m_max(R, L, G)
sizes = np.empty(CAL)
for i in range(CAL):
    best = np.inf
    for _ in range(k):
        x = rng.standard_normal(R)
        c = np.partition(x, R - m - 1)[R - m - 1]
        best = min(best, c)
    sizes[i] = norm.sf(best)
rc179['monte_carlo_R=20000_k=10'] = {'calibrations': CAL, 'P(true size > L)': round(float((sizes > L).mean()), 4),
                                     'mean true size': round(float(sizes.mean()), 5)}

# Two remedies. (a) One seed per family, fixed by randomness that does not exist until the calibration's code, N_0,
# R and gamma_cal are anchored: the analyst has k = 1 by construction. (b) A declared attempt budget S with every
# attempt in the ledger: each attempt is certified at confidence 1 - g / S, so the max over S attempts exceeds L with
# probability <= g. (b) holds only if the attempt count is verifiable, which nothing in the repository makes it.
rc179['remedy_a_k=1'] = {f'R={R}': selected(R, L, G, 1) for R in (20000, 100000)}
rc179['remedy_b_budget_S'] = {f'S={S}': {f'R={R}': selected(R, L, G / S, S) for R in (20000, 100000)} for S in (5, 20)}
out['6248847770/3 RC-179'] = rc179

print(json.dumps(out, indent=1))
