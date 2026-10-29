"""Round-14 checks for the Codex findings on PR #4 at b1935db (no reference code, no network).

Review 5561953685. Each block is keyed by the review-comment id it answers. The cluster-weighted statistic with
block-sum variance over occupied blocks is that of 16 Appendix F, L, M and N. Finding 4306188722 (a commit
identity) needs the repository and is not in this script.
"""
import json, sys
from datetime import date
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
ALPHA = 0.05

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
def rates(tt, g, crits):
    res = {}
    for label, c in crits:
        cc = student_t.ppf(1 - ALPHA, g - 1) if c is None else c
        r = tt > cc
        res[label] = {'rate': round(float(r.mean()), 4), 'upper_99': round(binom_upper(int(r.sum()), r.size, 0.99), 4)}
    return res
CRITS = (('nominal_G-1_df', None), ('c_2.254', 2.254))

# ================= r4306188719 (RC-139): outcome knowable before the cluster's registration record =================
# Codex's fixture: arm cutoff 0, adjudicated knowable_at 5, registration record 10, declared e_i 20. Version 11 checks
# registration < e_i and cutoff < e_i (both pass) and knowable_at <= cutoff (no breach). Version 11 also admits a
# forecast only if it is received after the registration record (RC-87) and strictly before t*_k (RC-52, RC-92), and
# scores every arm without an eligible forecast at t_close as an abstention at the baseline forecast (RC-104, RC-109).
fx = {'arm_cutoff': 0, 'knowable_at': 5, 'registration': 10, 'declared_e_i': 20, 'forecast_receipts': [11, 12, 15]}
t_star = fx['knowable_at']
eligible = [r for r in fx['forecast_receipts'] if fx['registration'] < r < t_star]
pb, pf = 0.5, 0.3
x_scored_normally = {y: round((pb - y) ** 2 - (pf - y) ** 2, 4) for y in (0, 1)}
x_version_11 = {y: (x_scored_normally[y] if eligible else 0.0) for y in (0, 1)}
rc139 = {'fixture': {**fx, 'version_11_registration_check_passes': fx['registration'] < fx['declared_e_i'],
                     'version_11_cutoff_check_passes': fx['arm_cutoff'] < fx['declared_e_i'],
                     'version_11_rc135_breach': fx['knowable_at'] <= fx['arm_cutoff'],
                     't_star_k': t_star, 'eligible_forecast_receipts': eligible,
                     'X_if_scored_normally_by_Y': x_scored_normally, 'X_under_version_11_by_Y': x_version_11,
                     'X_least_favourable_imputation': min(x_version_11.values()),
                     'eligibility_interval_empty': fx['registration'] >= t_star}}
# Null law (a) of 16 Appendix N (p_b = 0.5, p_F = 0.3, Y ~ Bern(0.4), E[X_i] = 0), 600 registered singleton clusters in
# 24 maturity blocks. A registrar adds m clusters whose outcome is already public at registration and chooses NO
# outcomes, which favour FULL under this law (X = +0.16). Codex's reading: the added members are scored normally.
# Version 11: every forecast on them is after t*_k, every arm abstains, X = 0 whatever Y.
rng = np.random.default_rng(1439)
N, REPS = 600, 20000
row = {}
blk0 = np.broadcast_to(np.repeat(np.arange(24), 25), (REPS, N))
x = np.where(rng.random((REPS, N)) < 0.4, x_scored_normally[1], x_scored_normally[0])
t0, g0 = cw_t_blocks(x, blk0, 24)
row['none_added'] = rates(t0, g0, CRITS)
for m in (6, 15, 30):
    blk_add = rng.integers(0, 24, (REPS, m))
    blk = np.concatenate([blk0, blk_add], axis=1)
    xn = np.concatenate([x, np.full((REPS, m), x_scored_normally[0])], axis=1)
    xz = np.concatenate([x, np.zeros((REPS, m))], axis=1)
    tn, gn = cw_t_blocks(xn, blk, 24)
    tz, gz = cw_t_blocks(xz, blk, 24)
    row[f'added_{m}_share_{round(m / (N + m), 4)}'] = {'scored_normally': rates(tn, gn, CRITS),
                                                        'version_11_abstention_X_0': rates(tz, gz, CRITS)}
rc139['law_a_known_NO_added_after_publication'] = row
rc139['reading'] = ('the selection channel exists only if the member is scored from forecasts received after its outcome '
                    'was knowable; version 11 admits no such forecast (registration < receipt < t*_k is empty), so every '
                    'arm abstains and X = 0 at both outcomes, which is also the least favourable imputation; the added '
                    'zeros leave the rate at or below the no-addition rate; the record gap is that the case is neither '
                    'named nor reported, and an arm abstention cap would count it against the arm')
out['RC139_knowable_before_registration'] = rc139

# ================= r4306188724 (RC-141): the conditional factor of the RC-133 construction =================
# Law of 16 Appendix N, RC-133: B = +/-0.5 fair, sign(A) = sign(B) with probability rho, lambda_A = 0.5 after B > 0
# and 0 after B < 0. Round 13 reported 1 + 0.5 * 0.5 * 0.5 * (2 rho - 1) as the factor conditional on the record-order
# past; the extra 0.5 is the probability that B > 0, so that value is the unconditional expectation.
rng = np.random.default_rng(1441)
rc141 = {}
for rho in (0.5, 0.75, 0.9, 1.0):
    xb = np.where(rng.random(200000) < 0.5, 0.5, -0.5)
    xa = np.where(rng.random(200000) < rho, xb, -xb)
    f = 1 + np.where(xb > 0, 0.5, 0.0) * xa
    rc141[f'rho_{rho}'] = {'exact_given_B_positive': round(1 + 0.5 * 0.5 * (2 * rho - 1), 4),
                           'exact_given_B_negative': 1.0,
                           'exact_unconditional': round(1 + 0.5 * 0.5 * 0.5 * (2 * rho - 1), 4),
                           'simulated_given_B_positive': round(float(f[xb > 0].mean()), 4),
                           'simulated_given_B_negative': round(float(f[xb < 0].mean()), 4),
                           'simulated_unconditional': round(float(f.mean()), 4)}
out['RC141_conditional_factor'] = rc141

# ================= r4306188725 (RC-142): the section 6 estimand compares the cutoff with not_before =================
# Codex's fixture: terminal-falsifier member, falsifier_observable_from 2026-02-01, arm cutoff 2026-02-28,
# not_before 2026-03-01. Section 3 (version 11) admits the member iff cutoff < e_i; the section 6 estimand row of
# version 11 admits it iff cutoff < not_before.
nb, fo, cut = date(2026, 3, 1), date(2026, 2, 1), date(2026, 2, 28)
e_i = min(nb, fo)
out['RC142_estimand_bound'] = {'e_i': e_i.isoformat(), 'section_3_v11_admits': cut < e_i,
                               'section_6_v11_admits': cut < nb, 'version_12_admits_in_section_3_and_6': cut < e_i,
                               'agree_in_v11': (cut < e_i) == (cut < nb)}

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
