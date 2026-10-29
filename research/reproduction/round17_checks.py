"""Round-17 checks for the Codex findings on PR #4 at 018057b (no reference code, no network).

Review 5562186477. Each block is keyed by the review-comment id it answers. The cluster-weighted statistic with
block-sum variance over occupied blocks is that of 16 Appendix F and L to Q; the GRAPA recurrence is that of 16
Appendix A.
"""
import itertools, json, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
ALPHA = 0.05
REPS = 20000

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def rate(reject):
    return {'rate': round(float(reject.mean()), 4), 'upper_99': round(binom_upper(int(reject.sum()), reject.size, 0.99), 4)}
def t_many(x, blocks, nb):
    # many samples on one design: theta = mean over clusters, block-sum variance over occupied blocks on G - 1 df
    reps, n = x.shape
    theta = x.mean(axis=1)
    idx = (np.arange(reps)[:, None] * nb + blocks[None, :]).ravel()
    bs = np.bincount(idx, weights=(x - theta[:, None]).ravel(), minlength=reps * nb).reshape(reps, nb)
    g = np.unique(blocks).size
    v = (bs ** 2).sum(axis=1) / n ** 2 * g / (g - 1)
    tt = np.full(reps, -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt
def block_sums(d, blocks, nb):
    reps = d.shape[0]
    idx = (np.arange(reps)[:, None] * nb + blocks[None, :]).ravel()
    return np.bincount(idx, weights=d.ravel(), minlength=reps * nb).reshape(reps, nb)
def bound_reject(lo, hi, blocks, nb, c, kappa):
    # Conservative box rule: theta at the lower ends against c times an upper bound on the standard error over the
    # box, ||v(mid)|| + kappa * sqrt(sum_g R_g^2). Version 14 used kappa = 1, valid for equal block sizes only.
    n = lo.shape[1]
    g = np.unique(blocks).size
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    s_mid = block_sums(mid - mid.mean(axis=1)[:, None], blocks, nb)
    r = block_sums(half, blocks, nb)
    se_up = (np.sqrt((s_mid ** 2).sum(axis=1)) + kappa * np.sqrt((r ** 2).sum(axis=1))) / n * np.sqrt(g / (g - 1))
    return (lo.mean(axis=1) > c * se_up) & (se_up > 0)
def kappa_of(sizes):
    sizes = np.asarray(sizes, float)
    return float(np.sqrt(sizes.size * (sizes ** 2).sum()) / sizes.sum())

# ================= r4306404681 (RC-155): the box bound with unequal block sizes =================
# v(x)_g = sum_{k in g} (x_k - theta) = z_g - (n_g / N) sum(z), z = block sums, so v = P z with P = I - n 1^T / N.
# P is idempotent; it is an orthogonal projection only when every n_g is equal. For an oblique projection
# P = I - u w^T with w^T u = 1 the operator norm is ||u|| ||w||, here kappa = sqrt(G sum n_g^2) / N >= 1.
rc155 = {}
n91 = np.array([9.0, 1.0])
P = np.eye(2) - np.outer(n91 / n91.sum(), np.ones(2))
z = np.array([0.0, 1.0])
rc155['codex_fixture_sizes_9_1'] = {'P_z': [round(float(v), 4) for v in P @ z], 'norm_P_z': round(float(np.linalg.norm(P @ z)), 4),
                                    'version_14_bound_sqrt_sum_R2': 1.0, 'kappa': round(kappa_of(n91), 4),
                                    'largest_singular_value_of_P': round(float(np.linalg.svd(P, compute_uv=False)[0]), 4)}
rng = np.random.default_rng(17551)
worst = 0.0
for _ in range(500):
    sizes = rng.integers(1, 30, rng.integers(2, 40)).astype(float)
    Pm = np.eye(sizes.size) - np.outer(sizes / sizes.sum(), np.ones(sizes.size))
    worst = max(worst, abs(np.linalg.svd(Pm, compute_uv=False)[0] - kappa_of(sizes)))
rc155['max_abs_svd_minus_kappa_over_500_random_designs'] = float(f'{worst:.3e}')
rc155['kappa_equal_sizes_24x25'] = kappa_of([25] * 24)
def kappa_affected(sizes, affected_blocks):
    # Exact constant for the box: the largest singular value of P restricted to the columns of the occupied blocks
    # that contain an affected member (only those R_g are non-zero). It is at most kappa.
    sizes = np.asarray(sizes, float)
    Pm = np.eye(sizes.size) - np.outer(sizes / sizes.sum(), np.ones(sizes.size))
    return float(np.linalg.svd(Pm[:, list(affected_blocks)], compute_uv=False)[0])
# Decision level. Design: one block of 100 clusters and 23 singleton blocks (N = 123, G = 24). One affected member
# alone in a singleton block with interval [-0.75, 0.25] (FULL free, p_baseline = 0.5, Y = 1); every other cluster
# at X = a. Then v(x) = (x_i - a) P e_g, aligned with the box direction, which is where the version-14 bound is
# farthest from the truth.
sizes = np.array([100] + [1] * 23)
blocks = np.repeat(np.arange(24), sizes)
nb, n = 24, int(sizes.sum())
lo_v, hi_v = -0.75, 0.25
k_a = kappa_affected(sizes, [23])
dec = {'design': {'block_sizes': '1 x 100 and 23 x 1', 'N': n, 'kappa_global': round(kappa_of(sizes), 4),
                  'kappa_affected_block': round(k_a, 4),
                  'affected': 'one member alone in a singleton block, interval [-0.75, 0.25]'}}
def criterion(lo, hi, kappa):
    # theta at the lower ends divided by the bounded standard error: the bound rejects iff this exceeds c
    g = np.unique(blocks).size
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    s_mid = block_sums(mid - mid.mean(axis=1)[:, None], blocks, nb)
    r = block_sums(half, blocks, nb)
    se_up = (np.sqrt((s_mid ** 2).sum(axis=1)) + kappa * np.sqrt((r ** 2).sum(axis=1))) / n * np.sqrt(g / (g - 1))
    return lo.mean(axis=1) / se_up
for a in (0.022, 0.024, 0.026):
    x = np.full((1, n), a)
    lo, hi = x.copy(), x.copy(); lo[0, -1], hi[0, -1] = lo_v, hi_v
    tv = []
    for v in (lo_v, hi_v):
        yv = x.copy(); yv[0, -1] = v
        tv.append(float(t_many(yv, blocks, nb)[0]))
    dec[f'all_others_at_{a}'] = {'t_at_vertices': [round(v, 3) for v in tv], 'exact_min_t': round(min(tv), 3),
                                 'version_14_bound_value': round(float(criterion(lo, hi, 1.0)[0]), 3),
                                 'corrected_bound_value': round(float(criterion(lo, hi, k_a)[0]), 3),
                                 'at_c_2.254': {'exact_rejects': min(tv) > 2.254,
                                                'version_14_bound_rejects': bool(criterion(lo, hi, 1.0)[0] > 2.254),
                                                'corrected_bound_rejects': bool(criterion(lo, hi, k_a)[0] > 2.254)}}
# With noise: every other cluster at a + 0.01 * standard normal, a on a grid around the cutoff.
tot = {'exact': 0, 'version_14': 0, 'corrected': 0, 'version_14_rejects_where_exact_does_not': 0,
       'corrected_rejects_where_exact_does_not': 0}
for a in (0.020, 0.022, 0.024, 0.026, 0.028):
    rng = np.random.default_rng(17552)
    x = a + 0.01 * rng.standard_normal((REPS, n))
    lo, hi = x.copy(), x.copy(); lo[:, -1], hi[:, -1] = lo_v, hi_v
    tmins = np.full(REPS, np.inf)
    for v in (lo_v, hi_v):
        yv = x.copy(); yv[:, -1] = v
        tmins = np.minimum(tmins, t_many(yv, blocks, nb))
    exact = tmins > 2.254
    v14 = bound_reject(lo, hi, blocks, nb, 2.254, 1.0)
    new = bound_reject(lo, hi, blocks, nb, 2.254, k_a)
    tot['exact'] += int(exact.sum()); tot['version_14'] += int(v14.sum()); tot['corrected'] += int(new.sum())
    tot['version_14_rejects_where_exact_does_not'] += int((v14 & ~exact).sum())
    tot['corrected_rejects_where_exact_does_not'] += int((new & ~exact).sum())
dec['noisy_samples_5_x_20000'] = tot
# Random unequal designs, two to four affected members in random blocks with random intervals: the corrected bound
# never rejects where the exact vertex rule does not: for c > 0, theta_lo > c * se_up implies theta - c * se > 0 at
# every point, so a positive bound value never exceeds the minimum of t over the vertices.
rng = np.random.default_rng(17553)
viol = checked = pos = 0
for _ in range(400):
    g = int(rng.integers(6, 25))
    sz = rng.integers(1, 15, g); bl = np.repeat(np.arange(g), sz); nn = int(sz.sum())
    m = int(rng.integers(2, 5)); idx = rng.choice(nn, m, replace=False)
    x = rng.normal(rng.uniform(0, 0.15), 0.1, (1, nn))
    l = rng.uniform(-1, 0.5, m); h = l + rng.uniform(0.05, 0.5, m)
    lo, hi = x.copy(), x.copy(); lo[0, idx], hi[0, idx] = l, h
    tm = np.inf
    for corner in itertools.product(*zip(l, h)):
        yv = x.copy(); yv[0, idx] = corner
        tm = min(tm, float(t_many(yv, bl, g)[0]))
    ka = kappa_affected(sz, np.unique(bl[idx]))
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    s_mid = block_sums(mid - mid.mean(axis=1)[:, None], bl, g)
    r = block_sums(half, bl, g)
    se_up = (np.sqrt((s_mid ** 2).sum()) + ka * np.sqrt((r ** 2).sum())) / nn * np.sqrt(g / (g - 1))
    bound_t = float(lo.mean() / se_up)
    checked += 1
    pos += bound_t > 0
    viol += (bound_t > 0) and (bound_t > tm + 1e-12)
dec['random_unequal_designs'] = {'checked': checked, 'positive_bound_values': int(pos),
                                 'positive_bound_above_exact_min_t': int(viol)}
rc155['decision_level'] = dec
# Equal sizes: the constant 1 used in Appendix Q (24 blocks of 25) is an upper bound on kappa_affected, so every
# Appendix Q figure stands.
out['RC155_unequal_block_bound'] = rc155

# ================= r4306404685 (RC-156): a provider's cutoff breach propagates to the arms that consume it =================
# Fixture: providers A, B, C and Jev with declared cutoffs; FULL consumes A, B, C and Jev; the equal-weight committee
# consumes A, B and C; single-provider-three-roles for A consumes A; Design C is a registry computation from a
# committed base rate and consumes no model. A member's adjudicated knowable_at is 15.
declared = {'A': 20, 'B': 10, 'C': 8, 'Jev': 5, 'FULL': 12, 'committee': 12, 'three_roles_A': 12, 'single_A': 20}
inputs = {'FULL': ['A', 'B', 'C', 'Jev'], 'committee': ['A', 'B', 'C'], 'three_roles_A': ['A'], 'single_A': ['A']}
def derived(arm):
    return max([declared[arm]] + [derived(a) for a in inputs.get(arm, [])])
knowable = 15
rc156 = {'fixture': {'knowable_at': knowable,
                     'version_14_breached_arms': sorted(a for a in declared if a in inputs and declared[a] >= knowable),
                     'derived_cutoffs': {a: derived(a) for a in inputs},
                     'proposed_breached_arms': sorted(a for a in inputs if derived(a) >= knowable),
                     'FULL_vs_DesignC_box_in_version_14': 'a point (FULL fixed): the honest FULL forecast is not in it',
                     'FULL_vs_DesignC_box_proposed': '[(p_baseline - Y)^2 - 1, (p_baseline - Y)^2] (FULL free)'}}
# Null laws of 16 Appendix N (a) and P (c), 600 singleton clusters in 24 maturity blocks of 25. A breach hits a YES
# member at the given share; provider A is informed (p_A = 1) and FULL passes a weight w of A's forecast through:
# p_FULL = (1 - w) p_F + w. Version 14 marks only A breached, so the FULL-Design C comparison scores FULL's informed
# forecast; the proposed rule marks FULL breached by derivation and the box frees FULL's forecast in [0, 1].
NB, PER = 24, 25
N = NB * PER
BLK = np.repeat(np.arange(NB), PER)
KEQ = 1.0
for name, (pb, pf, py) in {'a_appendixN': (0.5, 0.3, 0.4), 'c_appendixP': (0.9, 0.1, 0.5)}.items():
    rng = np.random.default_rng(17561)
    y = (rng.random((REPS, N)) < py).astype(float)
    u = rng.random((REPS, N))
    x_h = (pb - y) ** 2 - (pf - y) ** 2
    th = t_many(x_h, BLK, NB)
    row = {'honest': {'nominal': rate(th > student_t.ppf(1 - ALPHA, NB - 1)), 'c_2.254': rate(th > 2.254)}}
    for share in (0.01, 0.02, 0.04):
        br = (y == 1) & (u < share / py)
        lo = np.where(br, (pb - y) ** 2 - 1, x_h); hi = np.where(br, (pb - y) ** 2, x_h)
        cell = {}
        for w in (1 / 3, 1.0):
            pfi = (1 - w) * pf + w
            x_v14 = np.where(br, (pb - 1) ** 2 - (pfi - 1) ** 2, x_h)
            tv = t_many(x_v14, BLK, NB)
            cell[f'pass_through_{round(w, 3)}'] = {'version_14_FULL_not_breached': {
                'nominal': rate(tv > student_t.ppf(1 - ALPHA, NB - 1)), 'c_2.254': rate(tv > 2.254)}}
        for lab, c in (('nominal', student_t.ppf(1 - ALPHA, NB - 1)), ('c_2.254', 2.254)):
            prop = bound_reject(lo, hi, BLK, NB, c, KEQ)
            cell[f'proposed_box_{lab}'] = rate(prop)
            cell[f'proposed_rejects_where_honest_does_not_{lab}'] = int((prop & ~(th > c)).sum())
        row[f'breach_share_{share}'] = cell
    rc156[f'law_{name}'] = row
out['RC156_breach_propagation'] = rc156

# ================= r4306404688 (RC-157): monitor factors committed before a late defect is recorded =================
# Law c of 16 Appendix P: p_baseline = 0.9, p_FULL = 0.1, Y ~ Bern(0.5), X = +0.8 at NO and -0.8 at YES, mean zero.
# 600 clusters in record order; archived GRAPA bettor (lambda_max = 0.5), running maximum against 1/alpha.
# A source-latency defect is a YES graded NO (X committed at +0.8 instead of -0.8); defects on a share r of members.
# Version 14: the factor is committed at H_k from the graded value and never rewritten, whenever the defect record
# appears. Proposed: the factor of cluster k is committed at H_k + D (the same defect-closure horizon as the primary);
# a defect recorded by then enters at the lower end of its box (-0.8 here); a share phi of defects is recorded only
# after H_k + D and stays at the graded value. The crossing rate is then at most the honest rate + P(any such defect).
def grapa_cross(xs, lam_max=0.5):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    for k in range(n_steps):
        if k < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / k
            var = np.maximum(0.0, (s2 - s1 * s1 / k) / (k - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * k / (k + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, k]); peak = np.maximum(peak, wealth)
        s1 += xs[:, k]; s2 += xs[:, k] ** 2
    return peak >= 1 / ALPHA
rng = np.random.default_rng(17571)
y = (rng.random((REPS, N)) < 0.5).astype(float)
u, w = rng.random((REPS, N)), rng.random((REPS, N))
x_h = (0.9 - y) ** 2 - (0.1 - y) ** 2
honest = grapa_cross(x_h)
rc157 = {'honest': rate(honest)}
for r in (0.01, 0.02, 0.05):
    d = (y == 1) & (u < r / 0.5)
    x_v14 = np.where(d, 0.8, x_h)
    cell = {'version_14_committed_at_graded_value': rate(grapa_cross(x_v14))}
    for phi in (0.0, 0.05):
        late = d & (w < phi)
        x_prop = np.where(late, 0.8, x_h)
        rej = grapa_cross(x_prop)
        p_late = float(late.any(axis=1).mean())
        cell[f'proposed_late_share_{phi}'] = {'rate': rate(rej), 'P_any_late': round(p_late, 4),
                                              'honest_plus_P_any_late': round(float(honest.mean()) + p_late, 4),
                                              'crosses_where_honest_does_not': int((rej & ~honest).sum())}
    rc157[f'defect_share_{r}'] = cell
out['RC157_monitor_late_defects'] = rc157

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
