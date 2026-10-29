"""Round-7 checks for the Codex findings on PR #4 at 10f8829 (no reference code, no network).

RC-80: a proof, not a simulation, of what a distribution-free bounded-mean test can do over G blocks, with a
numerical check; RC-83: power of the intersection-union conjunction under a joint generator. The archived GRAPA
rule and the cluster-weighted statistic are those of 16 Appendix A and F.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
ALPHA, LAM_MAX = 0.05, 0.5

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

def grapa_paths(xs, lam_max=LAM_MAX):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
    return wealth, peak

# ================= r4297337217 (RC-80): what any distribution-free bounded-mean test can do over G blocks =================
# Claim to replace the round-6 sentence: for ANY test phi with sup over mean-zero laws on [-1, 1] of E_P0[phi] <= alpha
# (finite-sample valid for the bounded-mean null), and ANY alternative law P1 on [-1, 1] with mean delta > 0,
#     E_P1[phi] <= alpha * (1 + delta)^G.
# Proof. Let eps = delta / (1 + delta) and P0 = (1 - eps) P1 + eps * point mass at -1. P0 lives on [-1, 1] and has
# mean (1 - eps) delta - eps = 0, so it is in the null. With probability (1 - eps)^G a P0 sample contains no -1 and
# is then distributed as a P1 sample, so E_P0[phi] >= (1 - eps)^G E_P1[phi]; with E_P0[phi] <= alpha and
# (1 - eps) = 1 / (1 + delta) the bound follows. The bound is attained by the randomised test "reject with probability
# alpha (1 + delta)^G when no -1 is observed" against this one null, so it cannot be improved without restricting the null.
G = 24
bound = {}
for delta in (0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.12, 0.13, 0.15):
    bound[f'delta={delta}'] = round(min(1.0, ALPHA * (1 + delta) ** G), 4)
delta_80 = 16 ** (1 / G) - 1          # alpha (1+delta)^G = 0.80
blocks_needed = {f'delta={d}': math.ceil(math.log(0.80 / ALPHA) / math.log(1 + d)) for d in (0.01, 0.02, 0.05, 0.08, 0.10)}
rc80 = {'statement': 'any level-alpha test valid for every mean-zero law on [-1, 1] has power <= alpha (1 + delta)^G against every alternative on [-1, 1] with mean delta',
        'G': G, 'alpha': ALPHA, 'power_upper_bound_by_delta': bound,
        'smallest_delta_with_bound_at_or_above_0.80': round(delta_80, 4),
        'blocks_needed_for_bound_0.80': blocks_needed,
        'round6_sentence_was': 'at 24 blocks there is no distribution-free bounded-mean test with power at a useful effect (tested on one kernel only)',
        'round7_sentence_is': 'over 24 blocks no finite-sample-valid bounded-mean test, of any form, has power above alpha (1 + delta)^24: 0.08 at delta = 0.02, 0.16 at 0.05, 0.32 at 0.08; 80 % needs delta >= 0.1225 or, at delta = 0.02, ' + str(blocks_needed['delta=0.02']) + ' blocks (computed, RC-102)'}
# Numerical check of the proof's two ingredients (Monte Carlo, 200,000 samples each): the catastrophe mixture has
# mean zero, and the fraction of its samples with no -1 equals (1 - eps)^G.
rng = np.random.default_rng(7001)
R = 200000
chk = {}
for delta in (0.02, 0.05, 0.08):
    eps = delta / (1 + delta)
    # P1: the D1-type alternative X in {delta - s, delta + s} with s = 0.3 (mean delta, inside [-1, 1]).
    s = 0.3
    x1 = delta + s * rng.choice([-1.0, 1.0], size=(R, G))
    cat = rng.random((R, G)) < eps
    x0 = np.where(cat, -1.0, x1)
    no_cat = ~cat.any(axis=1)
    # The randomised level-alpha test from the proof.
    reject_prob = min(1.0, ALPHA * (1 + delta) ** G)
    u = rng.random(R)
    size_mc = float(np.mean(no_cat & (u < reject_prob)))
    power_mc = float(np.mean(u < reject_prob))
    # The archived GRAPA betting test on the same P1 sample (the kernel round 6 tested) for comparison.
    w, peak = grapa_paths(x1)
    chk[f'delta={delta}'] = {'eps': round(eps, 5), 'P0_mean_mc': round(float(x0.mean()), 5),
                             'P0_fraction_without_catastrophe_mc': round(float(no_cat.mean()), 5),
                             '(1-eps)^G': round((1 - eps) ** G, 5),
                             'randomised_LR_test_size_mc': round(size_mc, 5), 'randomised_LR_test_power_mc': round(power_mc, 5),
                             'bound': round(reject_prob, 5),
                             'grapa_betting_power_on_P1': round(float((w >= 1 / ALPHA).mean()), 5),
                             'grapa_running_max_power_on_P1': round(float((peak >= 1 / ALPHA).mean()), 5)}
rc80['numerical_check'] = chk
# Constant-increment arithmetic behind the round-6 "0.29" statement (unchanged): (1 + 0.5 m)^22 >= 20.
rc80['grapa_constant_block_mean_needed_for_wealth_20_in_22_steps'] = round(2 * (20 ** (1 / 22) - 1), 4)
out['RC80_distribution_free_power_bound'] = rc80

# ================= r4297337251 (RC-83): power of the intersection-union conjunction =================
# Comparator set of 17 section 6: Design C, three single providers, the three-role provider, the equal-weight
# committee: J = 6 paired comparisons sharing FULL's forecast and the outcome. Generator per cluster: Y ~ Bern(p_F),
# FULL forecasts p_F = b, comparator c forecasts b - s_c sqrt(delta_c), s_c in {-1, +1}; X_c = (b_c - Y)^2 - (p_F - Y)^2
# has mean delta_c. Dependence between comparators is set by the signs: independent signs give uncorrelated X_c
# (they still share (p_F - Y)); equal signs give identical X_c; a shared sign with probability rho is between.
# Test per comparator: the cluster-weighted statistic with the block-sum variance of Appendix F (RC-69), 24 blocks,
# one-sided alpha = 0.05; IUT rejects iff every comparator rejects. Least-favourable configuration: every delta_c = delta.
J, PERIODS, REPS = 6, 24, 20000
crit = student_t.ppf(1 - ALPHA, PERIODS - 1)

def cw_t_many(x):
    """x: (reps, J, clusters) with clusters = PERIODS * per; returns t per (rep, J)."""
    reps, j, n = x.shape
    per = n // PERIODS
    theta = x.mean(axis=2)
    dev = (x - theta[:, :, None]).reshape(reps, j, PERIODS, per).sum(axis=3)
    v = (dev ** 2).sum(axis=2) / n ** 2 * PERIODS / (PERIODS - 1)
    with np.errstate(divide='ignore', invalid='ignore'):   # a comparator with every increment zero has v = 0 and never rejects
        return theta / np.sqrt(v)

def iut_power(b, delta, per, rho, seed):
    r = np.random.default_rng(seed)
    n = PERIODS * per
    y = (r.random((REPS, 1, n)) < b).astype(float)
    shared = r.choice([-1.0, 1.0], size=(REPS, 1, n))
    own = r.choice([-1.0, 1.0], size=(REPS, J, n))
    use_shared = r.random((REPS, J, n)) < rho
    s = np.where(use_shared, shared, own)
    bc = b - s * math.sqrt(delta)
    x = (bc - y) ** 2 - (b - y) ** 2
    tt = cw_t_many(x)
    rej = tt > crit
    marg = rej.mean(axis=0)
    joint = rej.all(axis=1).mean()
    return float(marg.mean()), float(joint)

rc83 = {'design': 'J = 6 comparators, 24 blocks, cluster-weighted statistic with block-sum variance, one-sided alpha 0.05, 20,000 replications, least-favourable configuration (every comparator at the same delta)', 'cells': {}}
for b in (0.5,):
    for delta, per in ((0.01, 25), (0.01, 50), (0.02, 12), (0.02, 25), (0.03, 12)):
        for rho in (0.0, 0.5, 1.0):
            marg, joint = iut_power(b, delta, per, rho, 8300 + int(delta * 1000) * 100 + per + int(rho * 10))
            k = f'b={b},delta={delta},clusters={PERIODS * per}(24x{per}),shared_sign_prob={rho}'
            rc83['cells'][k] = {'mean_marginal_power': round(marg, 4), 'iut_joint_power': round(joint, 4),
                                'product_of_marginals': round(marg ** J, 4),
                                'iut_99pct_lower': round(binom_lower(int(round(joint * REPS)), REPS, 0.99), 4)}
# Size of the IUT at the least-favourable null (one comparator exactly null, the rest at a strong alternative) is
# <= alpha by construction (T-13); checked here with the same generator: comparator 1 at delta 0, others at 0.08.
r = np.random.default_rng(8399)
per = 25; n = PERIODS * per
y = (r.random((REPS, 1, n)) < 0.5).astype(float)
s = r.choice([-1.0, 1.0], size=(REPS, J, n))
deltas = np.array([0.0] + [0.08] * (J - 1))[None, :, None]
bc = 0.5 - s * np.sqrt(deltas)
x = (bc - y) ** 2 - (0.5 - y) ** 2
rej = cw_t_many(x) > crit
k_iut = int(rej.all(axis=1).sum())
rc83['least_favourable_null_check'] = {'comparator_1_delta': 0.0, 'others_delta': 0.08, 'iut_rejections': k_iut,
                                        'rate': round(k_iut / REPS, 4), '99pct_upper': round(binom_upper(k_iut, REPS, 0.99), 4)}
out['RC83_iut_conjunction_power'] = rc83

out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
