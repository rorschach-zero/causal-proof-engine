"""Round-19 checks for the Codex findings on PR #4 at ceaeda1 (no reference code, no network).

Codex comment 6248247231 (three findings, posted as a PR comment, not as inline review comments). Blocks are keyed
by the finding's position in that comment. The exact two-point family is that of 16 Appendix L; the cluster-weighted
statistic with block-sum variance and the box-rule bound for equal block sizes are those of 16 Appendix N and Q.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def rate(reject):
    return {'rate': round(float(reject.mean()), 4), 'upper_99': round(binom_upper(int(reject.sum()), reject.size, 0.99), 4)}

# ================= 6248247231 item 1 (RC-161): certify the primary at alpha - eta_max =================
# Union bound of 17 section 3 item 3: size <= (calibrated size) + eta. Certifying the calibrated size at alpha gives
# alpha + eta_max; certifying it at alpha - eta_max gives alpha. Exact two-point family of 16 Appendix L
# (block mean +a w.p. 1 - eps, -b w.p. eps, a = eps b / (1 - eps), b = 0.9, 24 blocks); c* is the exact supremum
# over eps >= eps_min on a 1e-5 sweep, rounded up to 0.001.
G = 24
KS = np.arange(G + 1)
def two_point_t(eps, b=0.9):
    eps = np.asarray(eps, float)[:, None]
    a = eps * b / (1 - eps)
    k = KS[None, :]
    mean = (k * a - (G - k) * b) / G
    var = (k * (a - mean) ** 2 + (G - k) * (-b - mean) ** 2) / (G - 1)
    with np.errstate(divide='ignore', invalid='ignore'):
        tk = mean / np.sqrt(var / G)
    tk[:, [0, G]] = -np.inf
    return tk
def two_point_pmf(eps):
    return binom.pmf(KS[None, :], G, 1 - np.asarray(eps, float)[:, None])
def size_over(eps, c):
    return (two_point_pmf(eps) * (two_point_t(eps) > c)).sum(axis=1)
def c_star(eps, level):
    tk = two_point_t(eps); pm = two_point_pmf(eps)
    order = np.argsort(-tk, axis=1)
    ts = np.take_along_axis(tk, order, axis=1); ps = np.take_along_axis(pm, order, axis=1)
    j = (np.cumsum(ps, axis=1) > level + 1e-12).argmax(axis=1)
    return float(math.ceil(ts[np.arange(len(eps)), j].max() * 1000) / 1000)
dense = np.round(np.arange(0.02, 0.50001, 1e-5), 5)
rc161 = {}
for eps_min in (0.05, 0.2, 0.3):
    d = dense[dense >= eps_min - 1e-9]
    row = {}
    for eta_max in (0.0, 0.005, 0.01):
        c = c_star(d, 0.05 - eta_max)
        row[f'eta_max={eta_max}'] = {'certified_level': round(0.05 - eta_max, 3), 'c_star': c,
                                     'sup_size_at_c_star': round(float(size_over(d, c).max()), 5),
                                     'union_bound_on_size': round(float(size_over(d, c).max()) + eta_max, 5)}
    row['union_bound_if_certified_at_alpha'] = {f'eta_max={e}': round(0.05 + e, 3) for e in (0.005, 0.01)}
    rc161[f'eps_min={eps_min}'] = row
rc161['reading'] = ('a c* certified at alpha bounds the size only by alpha + eta_max; certified at alpha - eta_max it bounds it by alpha; '
                    'at eta_max = 0 the values are the Appendix L values 3.207, 2.693 and 2.254, and every positive eta_max raises c*')
out['RC161_alpha_minus_eta_max'] = rc161

# ================= 6248247231 item 3 (RC-163): outcome knowable after the cutoff, before forecast receipt =================
# Null of 16 Appendix N law (a) and (b): 600 singleton clusters in 24 maturity blocks of 25, baseline p_b, FULL p_F,
# Y ~ Bern((p_b + p_F) / 2), so E[X_i] = 0 for X = (p_b - Y)^2 - (p_F - Y)^2. Codex's case: arm cutoff 0,
# registration 1, adjudicated knowable_at 5, FULL's forecast received at 6, declared e_i 20. Only a YES can be
# knowable before the deadline on a milestone-deadline predicate, so the misdeclared bound hits a YES member with
# probability r. Version 16 has no breach for it (5 is after the cutoff and after the registration record) and
# excludes the forecast at adjudication (receipt 6 is not before t*_k = 5); the slot is neither eligible nor empty.
# Two readings of version 16: the member leaves the primary (complete case), or FULL's slot is scored as an
# abstention at the baseline forecast (X = 0). Proposed: the member enters through the box rule with FULL's slot free
# in [0, 1] and Y recorded, i.e. X in [(p_b - 1)^2 - 1, (p_b - 1)^2]; the honest sample (FULL's forecast as made,
# before the outcome) is a point of the box, so the box decision never rejects where the honest test does not.
N, NB, PER, REPS = 600, 24, 25, 20000
C_LIST = (('nominal_G-1_df', float(student_t.ppf(0.95, NB - 1))), ('c_2.254', 2.254))
def t_rows(x, w=None):
    if w is None:
        w = np.ones_like(x)
    n = w.sum(axis=1)
    theta = (x * w).sum(axis=1) / n
    s = ((x - theta[:, None]) * w).reshape(x.shape[0], NB, PER).sum(axis=2)
    g = (w.reshape(x.shape[0], NB, PER).sum(axis=2) > 0).sum(axis=1)
    v = (s ** 2).sum(axis=1) / n ** 2 * g / (g - 1)
    tt = np.full(x.shape[0], -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt
def box_reject(lo, hi, c):
    # equal block sizes: the block-centring map is an orthogonal projection (kappa = 1, 16 Appendix Q and R)
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    theta_mid = mid.mean(axis=1)
    s_mid = (mid - theta_mid[:, None]).reshape(mid.shape[0], NB, PER).sum(axis=2)
    r = half.reshape(mid.shape[0], NB, PER).sum(axis=2)
    se_up = (np.sqrt((s_mid ** 2).sum(axis=1)) + np.sqrt((r ** 2).sum(axis=1))) / N * np.sqrt(NB / (NB - 1))
    return (lo.mean(axis=1) > c * se_up) & (se_up > 0)
rng = np.random.default_rng(1963)
rc163 = {}
for law in ('a_FULL_below_baseline', 'b_uniform_forecasts'):
    if law.startswith('a'):
        pb, pf = np.full((REPS, N), 0.5), np.full((REPS, N), 0.3)
    else:
        pb, pf = rng.uniform(0.05, 0.95, (REPS, N)), rng.uniform(0.05, 0.95, (REPS, N))
    y = rng.random((REPS, N)) < (pb + pf) / 2
    x = np.where(y, (pb - 1) ** 2 - (pf - 1) ** 2, pb ** 2 - pf ** 2)
    t_honest = t_rows(x)
    row = {'no_misdeclared_bound': {lab: rate(t_honest > c) for lab, c in C_LIST}}
    for r in (0.01, 0.02, 0.04):
        hit = y & (rng.random((REPS, N)) < r)
        t_cc = t_rows(x, (~hit).astype(float))
        t_ab = t_rows(np.where(hit, 0.0, x))
        lo = np.where(hit, (pb - 1) ** 2 - 1, x); hi = np.where(hit, (pb - 1) ** 2, x)
        cell = {'mean_share_of_members': round(float(hit.mean()), 4)}
        for lab, c in C_LIST:
            bx = box_reject(lo, hi, c)
            cell[lab] = {'version_16_member_excluded': rate(t_cc > c), 'version_16_slot_as_abstention': rate(t_ab > c),
                         'proposed_box_rule': rate(bx), 'box_rejects_where_honest_does_not': int((bx & ~(t_honest > c)).sum())}
        row[f'misdeclared_share_of_YES_{r}'] = cell
    rc163[law] = row
rc163['reading'] = ('both readings of version 16 select on the outcome, because only a YES can be knowable inside the issuance window: under law (a) '
                    'they raise the rejection rate at every share and cutoff, under law (b) the selection cancels on average; '
                    'the box rule never rejects where the honest test does not, and its cost is power')
out['RC163_issuance_breach'] = rc163

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
