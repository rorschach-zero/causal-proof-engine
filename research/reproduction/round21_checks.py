"""Round-21 checks for the Codex findings on PR #4 at d18a4b7 (no reference code, no network).

Codex review 5562492917 (four inline findings). Blocks are keyed by comment ID; comment 4306617510 (RC-172) is a
commit-identity claim checked against the repository's refs and has no block here. The block-sum statistic is the
primary of 17 section 3 item 3: mean over clusters, variance sum_b (sum_{k in b} (X_k - theta))^2 / N^2 * G/(G - 1),
rejection iff t > c on G - 1 degrees of freedom.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, norm, t as student_t

out = {}

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def rate(reject):
    return {'rate': round(float(reject.mean()), 4), 'upper_99': round(binom_upper(int(reject.sum()), reject.size, 0.99), 4)}

def block_t(x, block, emits, g_from):
    """t statistic and G for one sample. x: increments, block: block index, emits: bool mask of emitting clusters,
    g_from: 'emitting' counts blocks with an emitted increment, 'eligible' every block with any eligible cluster."""
    xe, be = x[emits], block[emits]
    n = xe.size
    g = np.unique(be).size if g_from == 'emitting' else np.unique(block).size
    if n == 0 or g < 2:
        return -math.inf, g
    theta = xe.mean()
    s = np.bincount(be, weights=xe - theta)
    v = (s ** 2).sum() / n ** 2 * g / (g - 1)
    return (theta / math.sqrt(v) if v > 0 else -math.inf), g

# ================= 4306617507 (RC-171): the eta budget truncates the eligible population =================
# Singleton clusters, 50 eligible candidates per block over 24 blocks (1,200), each maturing in its registration
# block (horizon 0, a simplification that leaves T_A out of the check). Law (a) of 16 Appendix N: X = -0.24 at Y = 1
# and +0.16 at Y = 0, E[X] = 0.16 - 0.4 q at P(Y = 1) = q. FULL's effect is +delta in blocks 1-12 and -delta in
# blocks 13-24, so the eligible population of the window [T_0, T_R] satisfies the average null. Every candidate carries
# the same per-member bound u = eta_max / 600, so the Boole sum reaches eta_max at the 600th registration.
# Version 18: every later registration is refused, the cohort is blocks 1-12 and the estimand is still stated over
# [T_0, T_R]. Proposed: the budget closes the registration window at tau, the record time of the first refused
# registration, every source at once, and the estimand is the eligible population of [T_0, tau); the null class is
# stated and calibrated on that window, so the null law is one whose average is zero over the cohort as registered.
REPS = 20000
NB, PER = 24, 50
rng = np.random.default_rng(2171)
blocks_all = np.repeat(np.arange(NB), PER)
c_nom_24 = float(student_t.ppf(0.95, NB - 1))
c_nom_12 = float(student_t.ppf(0.95, 12 - 1))
rc171 = {'critical_values': {'nominal_G=24': round(c_nom_24, 4), 'nominal_G=12': round(c_nom_12, 4), 'c_2.254': 2.254}}
def law_a(q):
    return np.where(rng.random(q.shape) < q, -0.24, 0.16)
for delta in (0.01, 0.02):
    q_split = np.where(blocks_all < 12, (0.16 - delta) / 0.4, (0.16 + delta) / 0.4)
    q_null = np.full(NB * PER, 0.16 / 0.4)
    emit_all = np.ones(NB * PER, bool)
    cells = {'full_window_weak_null': [], 'v18_truncated_weak_null_of_window': [], 'proposed_window_null_on_[T0,tau)': []}
    first = blocks_all < 12
    for _ in range(REPS):
        x = law_a(q_split)
        t_full, _ = block_t(x, blocks_all, emit_all, 'emitting')
        t_trunc, _ = block_t(x[first], blocks_all[first], emit_all[first], 'emitting')
        x0 = law_a(q_null[first])
        t_win, _ = block_t(x0, blocks_all[first], emit_all[first], 'emitting')
        cells['full_window_weak_null'].append((t_full, 24))
        cells['v18_truncated_weak_null_of_window'].append((t_trunc, 12))
        cells['proposed_window_null_on_[T0,tau)'].append((t_win, 12))
    row = {}
    for name, vals in cells.items():
        tt = np.array([v[0] for v in vals])
        g = vals[0][1]
        row[name] = {'G': g, 'nominal': rate(tt > float(student_t.ppf(0.95, g - 1))), 'c_2.254': rate(tt > 2.254)}
    rc171[f'delta={delta}'] = row
# Unequal per-member bounds: under the version-18 refusal a high-bound candidate is refused while a later low-bound one
# still fits, so after the budget first binds only low-bound sources enter; with bounds u_A < u_B at most
# ceil(u_B / u_A) - 1 further A registrations follow the first refused B one. The close rule admits none.
rc171['v18_refusal_boundary_extra_low_bound_registrations'] = {f'u_B/u_A={r}': math.ceil(r) - 1 for r in (2, 10, 100)}
rc171['reading'] = ('refusing every registration after the Boole sum reaches eta_max gives later eligible candidates '
                    'probability zero; under a weak null over [T_0, T_R] with +delta early and -delta late the truncated '
                    'cohort rejects far above alpha; stating the estimand and the null class over [T_0, tau), tau an '
                    'outcome-blind stopping time of the registration counts, restores the level on that window')
out['RC171_eta_budget_window'] = rc171

# ================= 4306617512 (RC-173): calibration miscoverage in the level budget =================
# A simulated calibration certifies every evaluated point with simultaneous confidence 1 - gamma (gamma = 0.01).
# Over repetitions of calibration and experiment the rejection probability is E[size(c*)]; on the miscoverage event
# size(c*) is bounded only by 1, so P(reject) <= (1 - gamma) * a + gamma for a certification level a.
alpha, gamma = 0.05, 0.01
rc173 = {'codex_worst_case_at_a=0.05': round((1 - gamma) * alpha + gamma, 4)}
spend = {}
for eta_max in (0.0, 0.005, 0.01):
    for g in (0.01, 0.001):
        a = alpha - eta_max - g
        spend[f'eta_max={eta_max},gamma={g}'] = {'certification_level': round(a, 4),
                                                 'worst_case_bound_a+gamma+eta_max': round(a + g + eta_max, 4)}
rc173['spent_level'] = spend
# Exact behaviour of the upper-bound rule on one point of a continuous family (K = 1): with R replications, c* is the
# (k + 1)-th largest simulated statistic, k the largest count whose one-sided upper bound at confidence 1 - gamma is
# <= a; its true size is then 1 - U_(R-k), distributed Beta(k + 1, R - k), exactly and whatever the continuous law.
def ucb_rule(a, R, conf):
    k = 0
    while binom_upper(k + 1, R, conf) <= a:
        k += 1
    if binom_upper(k, R, conf) > a:
        return None
    sz = beta(k + 1, R - k)
    return {'max_count': k, 'observed_rate_ceiling': round(k / R, 5), 'P_true_size_above_a': float(f'{sz.sf(a):.3g}'),
            'E_true_size': round(float(sz.mean()), 5)}
exact = {}
for a in (0.05, 0.04, 0.03):
    for R in (20000, 100000):
        for K in (1, 100):
            exact[f'a={a},R={R},K={K}'] = ucb_rule(a, R, 1 - gamma / K)
rc173['upper_bound_rule_single_point_exact'] = exact
rc173['normal_cutoff_at_level'] = {f'a={a}': round(float(norm.isf(a)), 4) for a in (0.05, 0.04, 0.03)}
rc173['reading'] = ('the coverage failure of a simulated calibration is a probability the level-alpha claim must spend; '
                    'certifying at alpha - eta_max - gamma bounds the rejection rate by alpha in the worst case; on a '
                    'continuous point the rule miscovers with probability below gamma and its expected size is well below '
                    'the certified level, so the worst case is a bound, not an observed rate')
out['RC173_calibration_miscoverage'] = rc173

# ================= 4306617514 (RC-174): blocks with no emitted increment counted in G =================
# Codex's case: two blocks with scored clusters and 22 blocks whose eligible clusters are all pending or VOID.
x2 = np.array([0.30, 0.10, 0.20, 0.00])
b2 = np.array([0, 0, 1, 1])
t2, _ = block_t(x2, b2, np.ones(4, bool), 'emitting')
x24 = np.concatenate([x2, np.zeros(22)])
b24 = np.concatenate([b2, np.arange(2, 24)])
e24 = np.concatenate([np.ones(4, bool), np.zeros(22, bool)])
t24, _ = block_t(x24, b24, e24, 'eligible')
rc174 = {'codex_case': {'G=2_emitting': {'t': round(t2, 4), 'critical_nominal_1df': round(float(student_t.ppf(0.95, 1)), 4),
                                          'rejects': bool(t2 > student_t.ppf(0.95, 1))},
                        'G=24_eligible': {'t': round(t24, 4), 'critical_nominal_23df': round(float(student_t.ppf(0.95, 23)), 4),
                                          'rejects': bool(t24 > student_t.ppf(0.95, 23))}}}
# Null X in {-0.2, +0.2} equiprobable (16 Appendix F and J), Poisson supply per period over 24 periods, empty periods
# allowed; each eligible cluster is non-emitting (all members adjudicated VOID or pending at T_A) w.p. q, independently
# of its outcome. Version 18 counts every block with an eligible cluster in G and the degrees of freedom; proposed:
# only blocks with at least one emitted increment.
REPS = 20000
rng = np.random.default_rng(2174)
sim = {}
for lam in (0.5, 1.0, 2.0):
    for q in (0.1, 0.2, 0.4):
        rej = {'eligible': [], 'emitting': []}
        g_extra = []
        for _ in range(REPS):
            counts = rng.poisson(lam, 24)
            block = np.repeat(np.arange(24), counts)
            x = np.where(rng.random(block.size) < 0.5, -0.2, 0.2)
            emits = rng.random(block.size) >= q
            for mode in rej:
                tt, g = block_t(x, block, emits, mode)
                rej[mode].append(g >= 2 and tt > student_t.ppf(0.95, g - 1))
            g_extra.append(np.unique(block).size - np.unique(block[emits]).size)
        sim[f'poisson_mean={lam},nonemitting_share={q}'] = {
            'mean_nonemitting_blocks': round(float(np.mean(g_extra)), 3),
            'v18_G_eligible_blocks': rate(np.array(rej['eligible'])),
            'proposed_G_emitting_blocks': rate(np.array(rej['emitting']))}
rc174['valid_null_nominal_cutoff'] = sim
rc174['reading'] = ('a block whose eligible clusters all emit nothing adds a zero block sum and one to G, which shrinks the '
                    'G/(G - 1) factor and the critical value without adding an observation; counting only blocks with an '
                    'emitted increment is the RC-97 rule applied to emission rather than to registration')
out['RC174_G_from_emitting_blocks'] = rc174

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
