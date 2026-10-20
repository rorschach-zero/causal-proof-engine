"""Round-15 checks for the Codex findings on PR #4 at 0bef5f8 (no reference code, no network).

Review 5562023932. Each block is keyed by the review-comment id it answers. The cluster-weighted statistic with
block-sum variance over occupied blocks is that of 16 Appendix F, L, M, N and O. Findings 4306255029 (the OD10 range
in the header of 17) and 4306255038 (the Phase 2 "track record" wording) are text findings checked by the commands
of 16 Appendix P and are not in this script.
"""
import json, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
ALPHA = 0.05
NB, PER = 24, 25
N = NB * PER

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
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
def t_from_block_sums(s, n_g):
    # the same statistic from block sums and block counts (zeros change n_g, never s)
    n = n_g.sum()
    theta = s.sum() / n
    g = int((n_g > 0).sum())
    v = ((s - n_g * theta) ** 2).sum() / n ** 2 * g / (g - 1)
    return float(theta / np.sqrt(v))
def rates(tt, g, crits):
    res = {}
    for label, c in crits:
        cc = student_t.ppf(1 - ALPHA, g - 1) if c is None else c
        r = tt > cc
        res[label] = {'rate': round(float(r.mean()), 4), 'upper_99': round(binom_upper(int(r.sum()), r.size, 0.99), 4)}
    return res
CRITS = (('nominal_G-1_df', None), ('c_2.254', 2.254))
BLK = np.repeat(np.arange(NB), PER)

# ================= r4306255023 (RC-143): registration-breach clusters placed in a chosen maturity block =================
# Codex's fixture: 24 blocks of 25 clusters under the null, one block with sum 11, 30 X = 0 clusters added to it,
# t from 2.167 to 2.261 across the cutoff 2.254. Codex gives the block sum and the two t values, not the sample;
# increments of +/-1 are the scale at which a block of 25 can sum to 11. Search over 200 x 5,000 seeded null samples:
# every sample whose t lies in [2.160, 2.175] and which has a block summing to 11; 30 zeros are added to the first
# such block. Reported: how many such samples exist, how many cross 2.254, and the first that does.
rng = np.random.default_rng(1543)
n_g = np.full(NB, PER)
hits, flips, fixture = 0, 0, None
for _ in range(200):
    x = np.where(rng.random((5000, N)) < 0.5, 1.0, -1.0)
    s_all = x.reshape(5000, NB, PER).sum(axis=2)
    for s in s_all[(s_all == 11).any(axis=1)]:
        t_before = t_from_block_sums(s, n_g)
        if not 2.160 <= t_before <= 2.175:
            continue
        j = int(np.flatnonzero(s == 11)[0])
        n_add = n_g.copy(); n_add[j] += 30
        t_after = t_from_block_sums(s, n_add)
        hits += 1
        if t_after > 2.254:
            flips += 1
            if fixture is None:
                fixture = {'block_sums': [int(v) for v in s], 'chosen_block': j,
                           't_before': round(t_before, 4), 't_after_30_zeros_in_chosen_block': round(t_after, 4),
                           't_with_breach_clusters_outside_the_scored_population': round(t_before, 4)}
rc143 = {'samples_t_2.160_to_2.175_with_a_block_sum_11': hits, 'of_which_30_zeros_cross_2.254': flips,
         'first_crossing_sample': fixture}
# Null, two laws: (a) X = +/-0.2 fair; (b) law (a) of 16 Appendix N (p_b = 0.5, p_F = 0.3, Y ~ Bern(0.4), E[X] = 0).
# A registrar who has seen the outcomes adds m registration-breach clusters (X = 0 under version 12) to the one
# maturity block that maximises t (an upper bound for this attacker: every block's sum is taken as known), or to
# uniformly drawn blocks (Appendix O). Proposed: registration-breach clusters are outside the scored population, so
# the statistic is the one of the 600 registered clusters whatever the registrar adds.
REPS = 20000
laws = {'a_pm0.2': lambda r: np.where(r.random((REPS, N)) < 0.5, 0.2, -0.2),
        'b_appendixN_law_a': lambda r: np.where(r.random((REPS, N)) < 0.4, -0.24, 0.16)}
for name, draw in laws.items():
    rng = np.random.default_rng(15431)
    x = draw(rng)
    s = x.reshape(REPS, NB, PER).sum(axis=2)
    t0, g0 = cw_t_blocks(x, np.broadcast_to(BLK, x.shape), NB)
    row = {'excluded_or_none_added': rates(t0, g0, CRITS)}
    for m in (6, 15, 30):
        best = np.full(REPS, -np.inf)
        n = N + m
        theta = s.sum(axis=1) / n
        for j in range(NB):
            n_g = np.full(NB, PER); n_g[j] += m
            v = ((s - n_g[None, :] * theta[:, None]) ** 2).sum(axis=1) / n ** 2 * NB / (NB - 1)
            best = np.maximum(best, theta / np.sqrt(v))
        blk_rand = np.concatenate([np.broadcast_to(BLK, (REPS, N)), rng.integers(0, NB, (REPS, m))], axis=1)
        tr, gr = cw_t_blocks(np.concatenate([x, np.zeros((REPS, m))], axis=1), blk_rand, NB)
        row[f'added_{m}'] = {'version_12_X_0_chosen_block': rates(best, np.full(REPS, NB), CRITS),
                             'version_12_X_0_random_blocks': rates(tr, gr, CRITS)}
    rc143[f'law_{name}'] = row
rc143['reading'] = ('zeros are not inert: they move the cluster mean and every block deviation, so a placement chosen '
                    'after the outcomes raises the rejection rate while a random placement does not; outside the '
                    'scored population they change nothing')
out['RC143_registration_breach_zeros'] = rc143

# ================= r4306255032 (RC-145): a late record shows that a timely YES was graded NO =================
# Codex's arithmetic: p_FULL = 0.1, p_baseline = 0.9, X = (p_b - Y)^2 - (p_F - Y)^2.
def x_of(pb, pf, y):
    return round((pb - y) ** 2 - (pf - y) ** 2, 4)
rc145 = {'codex_arithmetic': {'X_true_YES': x_of(0.9, 0.1, 1), 'X_graded_NO': x_of(0.9, 0.1, 0)}}
# Null: 600 singleton clusters, 24 maturity blocks of 25, E[X] = 0 under the true outcome. A source-latency defect
# turns a true YES into a permanent graded NO; defects hit a share r of all members, drawn among YES members only
# (a NO cannot be late). Laws: (c) Codex's p_F = 0.1, p_b = 0.9, Y ~ Bern(0.5); (b) law (a) of Appendix N.
# Version 12: the graded outcome is scored. Proposed: the graded disposition stays in the ledger, and the primary
# scores a member with a recorded defect at the outcome least favourable to FULL of {graded, evidenced}.
for name, (pb, pf, py) in {'c_codex': (0.9, 0.1, 0.5), 'b_appendixN_law_a': (0.5, 0.3, 0.4)}.items():
    rng = np.random.default_rng(15451)
    row = {}
    y = (rng.random((REPS, N)) < py).astype(float)
    u = rng.random((REPS, N))
    x_true = (pb - y) ** 2 - (pf - y) ** 2
    t0, g0 = cw_t_blocks(x_true, np.broadcast_to(BLK, x_true.shape), NB)
    row['no_defect'] = rates(t0, g0, CRITS)
    for r in (0.005, 0.01, 0.02):
        defect = (y == 1) & (u < r / py)
        x_graded = np.where(defect, (pb - 0) ** 2 - (pf - 0) ** 2, x_true)
        x_lf = np.where(defect, np.minimum(x_graded, x_true), x_true)
        tg, gg = cw_t_blocks(x_graded, np.broadcast_to(BLK, x_true.shape), NB)
        tl, gl = cw_t_blocks(x_lf, np.broadcast_to(BLK, x_true.shape), NB)
        row[f'defect_share_{r}'] = {'mean_defects': round(float(defect.sum(axis=1).mean()), 2),
                                    'version_12_graded': rates(tg, gg, CRITS),
                                    'proposed_least_favourable': rates(tl, gl, CRITS)}
    rc145[f'law_{name}'] = row
out['RC145_late_source_defects'] = rc145

# ================= r4306255034 (RC-146): knowable_at is the earliest of the three times =================
# Codex's fixture: public occurrence 90, deadline + window 110, publication 118.
times = {'public_occurrence': 90, 'deadline_plus_window': 110, 'publication': 118}
out['RC146_knowable_at'] = {'times': times, 'min_rule_knowable_at': min(times.values()),
                            'last_of_these_reading': max(times.values()),
                            'forecast_at_100_eligible_under_min': 100 < min(times.values()),
                            'forecast_at_100_eligible_under_last': 100 < max(times.values())}

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
