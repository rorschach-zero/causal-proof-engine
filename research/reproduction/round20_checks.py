"""Round-20 checks for the Codex findings on PR #4 at f20d1fc (no reference code, no network).

Codex comment 6248401610 (seven findings, posted as a PR comment, not as inline review comments). Blocks are keyed
by the finding's position in that comment. The cluster-weighted statistic with block-sum variance and the law (a)
forecasts are those of 16 Appendix N and T; items 2, 3, 4 and 7 are record checks and have no block here.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def rate(reject):
    return {'rate': round(float(reject.mean()), 4), 'upper_99': round(binom_upper(int(reject.sum()), reject.size, 0.99), 4)}

# ================= 6248401610 item 1 (RC-164): eta is a cohort-level probability =================
# eta = P(some breach or defect of the cohort is recorded after T_D). A per-member bound p gives, over n members,
# 1 - (1 - p)^n under independence and at most min(1, n p) under any dependence (Boole); comonotone records give p.
rc164 = {'codex_example_p_0.001_n_600': {'independent': round(1 - 0.999 ** 600, 4), 'boole_any_dependence': 0.6,
                                         'comonotone': 0.001}}
need = {}
for n in (120, 600, 1200):
    for eta_max in (0.005, 0.01):
        p_boole = eta_max / n
        p_indep = 1 - (1 - eta_max) ** (1 / n)
        # zero late records among m Phase 2 member observations: the one-sided 95 % Clopper-Pearson bound is
        # 1 - 0.05^(1/m), so m >= log(0.05) / log(1 - p) are needed to certify p
        m = math.ceil(math.log(0.05) / math.log1p(-p_boole))
        need[f'n={n},eta_max={eta_max}'] = {'per_member_bound_boole': float(f'{p_boole:.4g}'),
                                            'per_member_bound_independent': float(f'{p_indep:.4g}'),
                                            'phase2_observations_zero_late_95pct': m}
rc164['per_member_bound_needed'] = need
rc164['reading'] = ('the Phase 2 per-member bound is not eta: summed over the cohort (Boole, valid under any dependence) it is; '
                    'at 600 members eta_max = 0.01 needs a per-member bound of 1.667e-05, certified only by about 180,000 '
                    'Phase 2 member observations with no late record')
out['RC164_cohort_level_eta'] = rc164

# ================= shared null of items 5 and 6 =================
# Law (a) of 16 Appendix N: baseline 0.5, FULL 0.3, X = (p_b - Y)^2 - (p_F - Y)^2, so X = -0.24 at Y = 1 and
# +0.16 at Y = 0, and E[X] = 0.16 - 0.4 q at P(Y = 1) = q. 600 clusters in 24 maturity blocks of 25.
NB, PER = 24, 25
N = NB * PER
C_LIST = (('nominal_G-1_df', float(student_t.ppf(0.95, NB - 1))), ('c_2.254', 2.254))
def t_rows(x, w):
    n = w.sum(axis=1)
    theta = (x * w).sum(axis=1) / n
    s = ((x - theta[:, None]) * w).reshape(x.shape[0], NB, PER).sum(axis=2)
    g = (w.reshape(x.shape[0], NB, PER).sum(axis=2) > 0).sum(axis=1)
    v = (s ** 2).sum(axis=1) / n ** 2 * g / (g - 1)
    tt = np.full(x.shape[0], -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt
def xs(y):
    return np.where(y, -0.24, 0.16)

# ================= 6248401610 item 5 (RC-168): pre-declared VOIDs audited for registration breaches =================
# Clusters of three members; member outcomes share a cluster state Z ~ Bern(0.4): Y_j = Z w.p. rho, else an
# independent Bern(0.4), so every member has P(Y = 1) = 0.4 and E[X] = 0. In a share s of clusters member 1's outcome
# is public at registration (a misdeclared e_i), on either outcome, independently of it. The target population is the
# clusters with no member knowable at registration (17 section 3 item 1, RC-139 and RC-143), on which the null holds.
# Version 17: a listed member known at registration is adjudicated a registration breach and its cluster leaves the
# scored population, but a member pre-declared VOID is never adjudicated. A registrar who sees member 1's outcome
# pre-declares it VOID when it is NO (the siblings, likely NO, favour FULL) and lists it when it is YES (the cluster
# then leaves as a breach). Proposed: a pre-declared member is adjudicated like a listed one, and a knowable_at at or
# before the registration record makes its cluster a registration breach whatever its VOID flag.
REPS = 20000
rng = np.random.default_rng(2068)
rc168 = {}
for rho in (0.5, 0.8):
    z = rng.random((REPS, N)) < 0.4
    keep = rng.random((REPS, N, 3)) < rho
    y = np.where(keep, z[:, :, None], rng.random((REPS, N, 3)) < 0.4)
    x3 = xs(y)
    full_mean = x3.mean(axis=2)
    sib_mean = x3[:, :, 1:].mean(axis=2)
    ones = np.ones((REPS, N))
    row = {'no_member_known': {lab: rate(t_rows(full_mean, ones) > c) for lab, c in C_LIST}}
    for s in (0.05, 0.1, 0.2):
        known = rng.random((REPS, N)) < s
        y1 = y[:, :, 0]
        w_v17 = np.where(known & y1, 0.0, 1.0)
        x_v17 = np.where(known & ~y1, sib_mean, full_mean)
        w_prop = np.where(known, 0.0, 1.0)
        cell = {'mean_share_known': round(float(known.mean()), 4)}
        for lab, c in C_LIST:
            cell[lab] = {'version_17_void_when_NO': rate(t_rows(x_v17, w_v17) > c),
                         'proposed_audited_breach': rate(t_rows(full_mean, w_prop) > c)}
        row[f'known_share_{s}'] = cell
    rc168[f'rho={rho}'] = row
rc168['reading'] = ('a pre-declared VOID that is never adjudicated lets the registrar keep exactly the breached clusters whose known '
                    'outcome favours FULL; auditing it like a listed member removes every breached cluster whatever its outcome, '
                    'which is the target population, and the rate returns to the rate with no member known')
out['RC168_predeclared_void_audit'] = rc168

# ================= 6248401610 item 6 (RC-169): source withdrawal during accrual =================
# Singleton clusters from two source families, A and B, alternating slots in every block (equal inclusion probability).
# FULL's effect is +delta on A and -delta on B (P(Y = 1) = (0.16 -/+ delta) / 0.4), so the registered population is
# null on average (the weak null) and not source by source; delta = 0 is the strong null. A registration breach is
# recorded on a B cluster's source w.p. 0.1 when Y = 1 (only a YES can be knowable early); it changes no score here,
# so that the check isolates the reweighting. Version 17: B is withdrawn from new registrations after the first block
# at whose end its breach count exceeds 6 (or, as a fixed-time control, after block 12); its later slots are empty.
# Proposed: a withdrawal takes effect at the next cohort; the current cohort keeps registering from B.
rng = np.random.default_rng(2069)
is_b = (np.arange(N) % 2 == 1)[None, :]
block_of = np.repeat(np.arange(NB), PER)
rc169 = {}
for delta in (0.0, 0.02, 0.05):
    q = np.where(is_b, (0.16 + delta) / 0.4, (0.16 - delta) / 0.4)
    y = rng.random((REPS, N)) < q
    x = xs(y)
    ones = np.ones((REPS, N))
    breach = is_b & y & (rng.random((REPS, N)) < 0.1)
    per_block = breach.reshape(REPS, NB, PER).sum(axis=2).cumsum(axis=1)
    crossed = per_block > 6
    first = np.where(crossed.any(axis=1), crossed.argmax(axis=1), NB)
    w_trigger = np.where(is_b & (block_of[None, :] > first[:, None]), 0.0, 1.0)
    w_fixed = np.where(is_b & (block_of[None, :] >= 12), 0.0, ones)
    row = {'withdrawn_share_of_reps': round(float((first < NB - 1).mean()), 4),
           'median_withdrawal_block': int(np.median(first))}
    for lab, c in C_LIST:
        row[lab] = {'proposed_no_withdrawal_in_cohort': rate(t_rows(x, ones) > c),
                    'version_17_breach_count_trigger': rate(t_rows(x, w_trigger) > c),
                    'version_17_fixed_withdrawal_after_block_12': rate(t_rows(x, w_fixed) > c)}
    rc169[f'delta={delta}'] = row
rc169['reading'] = ('under the strong null (delta = 0) withdrawal changes little; under the weak null it reweights the cohort toward '
                    'the source on which FULL is better and the rejection rate rises with delta; keeping the cohort as registered '
                    'restores the rate')
out['RC169_source_withdrawal'] = rc169

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
