"""Round-12 checks for the Codex findings on PR #4 at 78225fd (no reference code, no network).

Reviews 5559198689 and 5560119353. Each block is keyed by the review-comment id it answers. The exact two-point
block-mean family and the cluster-weighted statistic with block-sum variance are those of 16 Appendix F, J and L.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA = 0.05
G = 24
KS = np.arange(G + 1)

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def kmax(bound, n, conf):
    lo, hi = 0, n
    while lo < hi:                                    # largest k with binom_upper(k, n, conf) <= bound
        mid = (lo + hi + 1) // 2
        if binom_upper(mid, n, conf) <= bound:
            lo = mid
        else:
            hi = mid - 1
    return lo

# Exact two-point block-mean family of 16 Appendix J and L (block mean +a w.p. 1 - eps, -b w.p. eps, b = 0.9).
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
def size_strict(eps, c):
    return (two_point_pmf(eps) * (two_point_t(eps) > c)).sum(axis=1)
def size_weak(eps, c):
    return (two_point_pmf(eps) * (two_point_t(eps) >= c)).sum(axis=1)
dense = np.round(np.arange(0.02, 0.50001, 1e-5), 5)

# ================= r4303816929 (RC-124): published cutoffs rounded to nearest instead of upward =================
rc124 = {}
for eps_min, exact, nearest, up in ((0.1, 3.207, 3.21, 3.21), (0.2, 2.693, 2.69, 2.70), (0.3, 2.254, 2.25, 2.26)):
    d = dense[dense >= eps_min - 1e-9]
    row = {}
    for label, c in (('three_decimals', exact), ('two_decimals_nearest', nearest), ('two_decimals_upward', up)):
        sz = size_strict(d, c); i = int(sz.argmax())
        row[f'{label}={c}'] = {'sup_size': round(float(sz[i]), 5), 'argmax_eps': float(d[i]),
                               'fraction_of_sweep_above_alpha': round(float((sz > ALPHA).mean()), 4)}
    rc124[f'eps_min={eps_min}'] = row
rc124['reading'] = ('2.69 and 2.25 are below the exact-supremum values 2.693 and 2.254 and exceed alpha inside their own classes; '
                    'a published cutoff keeps three decimals or is rounded upward, never to nearest')
out['RC124_rounding'] = rc124

# ================= r4303816943 (RC-127): rejection inequality in calibration and decision =================
# The calibration of Appendix J and L rejects iff t > c and selects, per eps, the attained value t_(j*) at which the
# descending cumulative mass first exceeds alpha. At that attained value the weak inequality t >= c adds the mass
# of the tied atom. Exact sizes at the per-eps critical value under both inequalities.
def crit_per_eps(eps):
    tk = two_point_t(eps); pm = two_point_pmf(eps)
    order = np.argsort(-tk, axis=1)
    ts = np.take_along_axis(tk, order, axis=1); ps = np.take_along_axis(pm, order, axis=1)
    cum = np.cumsum(ps, axis=1)
    j = (cum > ALPHA).argmax(axis=1)
    return ts[np.arange(len(eps)), j]
rc127 = {'per_eps_attained_critical_value': {}}
for e in (0.1, 0.2, 0.3):
    c = float(crit_per_eps(np.array([e]))[0])
    rc127['per_eps_attained_critical_value'][f'eps={e}'] = {
        'c': round(c, 6), 'size_strict_t_gt_c': round(float(size_strict(np.array([e]), c)[0]), 5),
        'size_weak_t_ge_c': round(float(size_weak(np.array([e]), c)[0]), 5)}
# At the rounded-up published values no atom of the sweep sits exactly on c, so both inequalities agree there.
rc127['published_values_sup_size_strict_vs_weak'] = {}
for eps_min, c in ((0.1, 3.207), (0.2, 2.693), (0.3, 2.254)):
    d = dense[dense >= eps_min - 1e-9]
    rc127['published_values_sup_size_strict_vs_weak'][f'c={c}'] = [round(float(size_strict(d, c).max()), 5),
                                                                   round(float(size_weak(d, c).max()), 5)]
rc127['reading'] = ('a cutoff selected as an attained value of a discrete statistic under t > c is oversized under t >= c by the mass '
                    'of the tied atom; calibration, the T-36 decision oracle and the production IUT use the strict inequality, and a '
                    'tie at c does not reject')
out['RC127_inequality'] = rc127

# ================= r4303816933 (RC-125): equal-maturity tie predecessors =================
# Version 9 applies cluster k at max(final_k, H_k, final of every cluster with a SMALLER H). Order of record:
# (H, registration id). Fixed rule: apply at max(H_k, final of every cluster at or before k in (H, id) order).
def apply_times(H, final, rule):
    n = len(H)
    order = np.lexsort((np.arange(n), H))            # (H, registration id)
    t = np.empty(n)
    if rule == 'v9_smaller_H_only':
        for k in range(n):
            smaller = final[H < H[k]]
            t[k] = max(final[k], H[k], smaller.max() if smaller.size else -np.inf)
    else:
        run = -np.inf
        for k in order:
            run = max(run, final[k])
            t[k] = max(H[k], run)
    seq = sorted(range(n), key=lambda k: (t[k], H[k], k))   # simultaneous applications in (H, id) order
    return t, seq
def in_record_order(H, seq):
    return all((H[a], a) < (H[b], b) for a, b in zip(seq, seq[1:]))
# Codex's fixture: A (id 0) and B (id 1) share H = 50; B is final at 52, A at 60.
H_fix = np.array([50.0, 50.0]); F_fix = np.array([60.0, 52.0])
rc125 = {'fixture': {}}
for rule in ('v9_smaller_H_only', 'record_order_predecessors'):
    t, seq = apply_times(H_fix, F_fix, rule)
    rc125['fixture'][rule] = {'apply_times': {'A': float(t[0]), 'B': float(t[1])}, 'sequence': ['AB'[k] for k in seq],
                              'in_record_order': in_record_order(H_fix, seq)}
# Random paths: 40 clusters registered at integer months 0..23 in id order, integer horizons 1..12 (ties frequent),
# half final one month after registration, half final at H + Uniform(0, 2) months.
rng = np.random.default_rng(20261017)
PATHS = 2000
bad = {'v9_smaller_H_only': 0, 'record_order_predecessors': 0}
delay = {'v9_smaller_H_only': [], 'record_order_predecessors': []}
for _ in range(PATHS):
    reg = np.sort(rng.integers(0, 24, 40)).astype(float)
    H = reg + rng.integers(1, 13, 40)
    early = rng.random(40) < 0.5
    final = np.where(early, reg + 1, H + rng.uniform(0, 2, 40))
    for rule in bad:
        t, seq = apply_times(H, final, rule)
        bad[rule] += not in_record_order(H, seq)
        delay[rule].append(float((t - final).mean()))
rc125['random_paths'] = {rule: {'fraction_out_of_record_order': round(bad[rule] / PATHS, 4),
                                'mean_delay_after_finality_months': round(float(np.mean(delay[rule])), 3)} for rule in bad}
rc125['reading'] = ('with equal maturities the version-9 buffer consumes ties in finality order, which is outcome-timed; waiting for '
                    'every (H, registration id) predecessor keeps the consumed sequence in the order that defines lambda_k')
out['RC125_equal_maturity'] = rc125

# ================= r4303816948 (RC-129): which timestamp assigns a cluster to a calendar block =================
# 600 clusters, registration uniform over [0, 24) months, horizon uniform over [1, 6), maturity H = registration +
# horizon; the outcome becomes knowable uniformly inside (registration, H) and is received Exp(mean 0.25) later.
# One-month blocks; the statistic is the cluster-weighted mean with block-sum variance over occupied blocks
# (RC-69, RC-97), nominal one-sided cutoff on G - 1 df. Null (a): independent clusters, X = +/-0.2.
# Null (b): every cluster maturing in month m shares a shock s_m = +/-0.3 (independent across months), X = 0.4 Y - 0.2
# with P(Y = 1) = 0.5 + s_m, so the dependence follows the maturity month.
N, REPS = 600, 20000
def cw_t_blocks(x, blocks, nb):
    reps, n = x.shape
    theta = x.mean(axis=1)
    dev = x - theta[:, None]
    idx = (np.arange(reps)[:, None] * nb + blocks).ravel()
    bs = np.bincount(idx, weights=dev.ravel(), minlength=reps * nb).reshape(reps, nb)
    occ = np.bincount(idx, minlength=reps * nb).reshape(reps, nb) > 0
    g = occ.sum(axis=1)
    v = (bs ** 2).sum(axis=1) / n ** 2 * g / (g - 1)
    tt = np.full(reps, -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt, g
rng = np.random.default_rng(1291)
reg = rng.uniform(0, 24, (REPS, N))
H = reg + rng.uniform(1, 6, (REPS, N))
know = reg + rng.uniform(0, 1, (REPS, N)) * (H - reg)
recv = know + rng.exponential(0.25, (REPS, N))
NB = 31
stamps = {'registration': reg, 'knowable_at': know, 'receipt': recv, 'maturity': H}
blocks = {k: np.minimum(np.floor(v).astype(int), NB - 1) for k, v in stamps.items()}
rc129 = {'fixture': {}}
# Deterministic fixture: one cluster registered 2026-01-20, knowable 2026-02-10, received 2026-03-02, maturity 2026-04-30.
rc129['fixture'] = {'registration': 'block 2026-01', 'knowable_at': 'block 2026-02', 'receipt': 'block 2026-03', 'maturity': 'block 2026-04'}
for name, x in (('independent_clusters', np.where(rng.random((REPS, N)) < 0.5, 0.2, -0.2)), ('shock_in_maturity_month', None)):
    if x is None:
        s = np.where(rng.random((REPS, NB)) < 0.5, 0.3, -0.3)
        q = 0.5 + np.take_along_axis(s, blocks['maturity'], axis=1)
        x = 0.4 * (rng.random((REPS, N)) < q) - 0.2
    rej = {}
    for k in stamps:
        tt, g = cw_t_blocks(x, blocks[k], NB)
        crit = student_t.ppf(1 - ALPHA, g - 1)
        rej[k] = tt > crit
    any_rej = np.logical_or.reduce([rej[k] for k in stamps])
    rc129[name] = {**{f'size_{k}': round(float(r.mean()), 4) for k, r in rej.items()},
                   'size_choose_after_outcomes_any_of_four': round(float(any_rej.mean()), 4),
                   'upper_99_of_choice': round(binom_upper(int(any_rej.sum()), REPS, 0.99), 4)}
rc129['reading'] = ('the four timestamps give four block structures; choosing among them after the outcomes is a selection of the '
                    'variance and is oversized; the block is fixed by the maturity H_k recorded at registration, which is outcome-'
                    'independent, and a block structure that does not follow the dependence (registration blocks under a maturity-'
                    'month shock) is oversized even when fixed in advance, so the dependence model and the timestamp are one OD4 choice')
out['RC129_block_assignment'] = rc129

# ================= r4304527990 (RC-130): the calibration confidence across all IUT components =================
rc130 = {'union_guarantee_per_component_99pct_J6': round(1 - 6 * 0.01, 2), 'observed_rate_ceiling': {}}
for reps in (20000, 100000):
    for k_total in (100, 600):
        conf = 1 - 0.01 / k_total
        rc130['observed_rate_ceiling'][f'reps={reps},K_total={k_total}'] = round(kmax(ALPHA, reps, conf) / reps, 5)
rc130['reading'] = ('a 99 % calibration per component gives a 94 % simultaneous statement over six components; K counts every '
                    'evaluated point of every component (sum of K_j), which costs about 0.1 percentage point of observed-rate '
                    'ceiling at 20,000 replications')
out['RC130_iut_confidence'] = rc130

# ================= r4304528000 (RC-132): post-unblinding correction of one arm version of many =================
# Null: 600 independent clusters, X = +/-0.2, 24 one-month blocks of 25 in registration order; a provider's twenty arm
# versions each cover 30 consecutive clusters (5 % each, inside a 5 % cap). Version 9: a cutoff correction filed
# after the outcomes removes that version's cohort. Strategy: correct the version whose removal maximises t.
rng = np.random.default_rng(1320)
REPS = 20000
x = np.where(rng.random((REPS, N)) < 0.5, 0.2, -0.2)
blk = np.repeat(np.arange(24), 25)
ver = np.repeat(np.arange(20), 30)
t_all, _ = cw_t_blocks(x, np.broadcast_to(blk, x.shape), 24)
t_best = t_all.copy()
for v in range(20):
    keep = ver != v
    tv, _ = cw_t_blocks(x[:, keep], np.broadcast_to(blk[keep], (REPS, keep.sum())), 24)
    t_best = np.maximum(t_best, tv)
rc132 = {}
for label, c in (('nominal_1.714', float(student_t.ppf(1 - ALPHA, 23))), ('c_2.693', 2.693), ('c_2.254', 2.254)):
    rc132[label] = {'no_correction': round(float((t_all > c).mean()), 4),
                    'v9_one_outcome_chosen_version_removed': round(float((t_best > c).mean()), 4),
                    'post_unblinding_correction_makes_primary_non_confirmatory': round(float((t_all > c).mean()), 4)}
rc132['reading'] = ('removing the worst of twenty version cohorts after the outcomes roughly doubles to triples the null rejection '
                    'rate at every cutoff; when a post-unblinding correction can only end the confirmatory claim, the strategy has '
                    'no gain and the size is the no-correction size')
out['RC132_version_selection'] = rc132

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
