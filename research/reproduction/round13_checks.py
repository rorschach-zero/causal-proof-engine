"""Round-13 checks for the Codex findings on PR #4 at 6fa4f0c (no reference code, no network).

Review 5560193272. Each block is keyed by the review-comment id it answers. The cluster-weighted statistic with
block-sum variance over occupied blocks is that of 16 Appendix F, L and M.
"""
import json, sys
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

# ================= r4304595889 (RC-133): chronological filtration versus record-order filtration =================
# Codex's example: A knowable at 10 with H_A = 100, B with H_B = 50 final at 50. Record order is (H, id): B precedes A,
# so the monitor computes A's betting fraction after B's increment, while version 10 section 3 item 3 defined
# F_(k-1) as everything recorded before A's outcome-knowable time (10), which excludes B.
# Law: pairs (B_j, A_j) in record order B_1, A_1, B_2, A_2, ...; every increment is +/-0.5 with probability one half,
# independent of everything recorded before A_j's knowable time (B_j is not final then), and sign(A_j) = sign(B_j)
# with probability rho. The chronological conditional null of version 10 holds on every path and for every rho; the
# record-order null holds only at rho = 0.5. Predictable one-sided bettor in record order: lambda = 0.5 after a
# positive previous increment, else 0 (an illustration of a predictable rule, not the archived GRAPA rule).
rng = np.random.default_rng(1331)
REPS, PAIRS = 20000, 60
rc133 = {'fixture': {'record_order': ['B (H=50)', 'A (H=100)'], 'B_in_version_10_F_of_A': False, 'B_in_record_order_F_of_A': True}}
for rho in (0.5, 0.75, 0.9, 1.0):
    xb = np.where(rng.random((REPS, PAIRS)) < 0.5, 0.5, -0.5)
    xa = np.where(rng.random((REPS, PAIRS)) < rho, xb, -xb)
    seq = np.empty((REPS, 2 * PAIRS))
    seq[:, 0::2], seq[:, 1::2] = xb, xa
    lam = np.zeros_like(seq)
    lam[:, 1:] = np.where(seq[:, :-1] > 0, 0.5, 0.0)
    logw = np.cumsum(np.log1p(lam * seq), axis=1)
    cross = logw.max(axis=1) >= np.log(1 / ALPHA)
    rc133[f'rho_{rho}'] = {'chronological_null_holds': True, 'record_order_null_holds': rho == 0.5,
                           'E_factor_A_given_B_positive': round(1 + 0.5 * 0.5 * (2 * rho - 1), 4),
                           'E_factor_A_given_B_negative': 1.0,
                           'E_factor_A_unconditional_over_B': round(1 + 0.5 * 0.5 * 0.5 * (2 * rho - 1), 4),
                           'crossing_rate': round(float(cross.mean()), 4),
                           'upper_99': round(binom_upper(int(cross.sum()), REPS, 0.99), 4)}
rc133['reading'] = ('Ville bounds the crossing rate under the record-order null only (rho = 0.5); for rho > 0.5 the version-10 '
                    'chronological null holds on every path while the monitor crosses, so a crossing has to be labelled as '
                    'evidence against the record-order null; the filtration is defined once, as the record-order predecessors')
out['RC133_filtration'] = rc133

# ================= r4304595901 (RC-135): early-knowability breach removed after the outcome =================
# Null: 600 singleton clusters, 24 maturity blocks of 25. Member i has baseline p_b and FULL p_F, Y ~ Bern((p_b+p_F)/2),
# which makes E[X_i] = 0 exactly for X = (p_b - Y)^2 - (p_F - Y)^2. A breach is a registered member whose outcome was
# knowable at or before an arm's cutoff; only a YES can be knowable early (a NO is knowable at logical finality, after
# not_before), so a breach hits a YES member with probability r. Law (a): p_b = 0.5, p_F = 0.3 on every member (the
# least favourable direction for this channel: FULL's Brier loss on a YES is the larger one). Law (b): p_b, p_F
# uniform on (0.05, 0.95), independently. Version 10: breached members are excluded from the skill statistics.
# Proposed: a breached member stays and is scored at its least favourable outcome, min(X(Y=0), X(Y=1)).
rng = np.random.default_rng(1335)
N, REPS = 600, 20000
blk = np.broadcast_to(np.repeat(np.arange(24), 25), (REPS, N))
rc135 = {}
for law in ('a_FULL_below_baseline', 'b_uniform_forecasts'):
    if law.startswith('a'):
        pb, pf = np.full((REPS, N), 0.5), np.full((REPS, N), 0.3)
    else:
        pb, pf = rng.uniform(0.05, 0.95, (REPS, N)), rng.uniform(0.05, 0.95, (REPS, N))
    y = rng.random((REPS, N)) < (pb + pf) / 2
    x1, x0 = (pb - 1) ** 2 - (pf - 1) ** 2, pb ** 2 - pf ** 2
    x = np.where(y, x1, x0)
    t0, g0 = cw_t_blocks(x, blk, 24)
    row = {'no_breach': rates(t0, g0, CRITS)}
    for r in (0.025, 0.05, 0.1, 0.2):
        breach = y & (rng.random((REPS, N)) < r)
        # Version 10: exclude breached members (cluster-weighted mean over the members that remain).
        w = (~breach).astype(float)
        theta = (x * w).sum(axis=1) / w.sum(axis=1)
        dev = (x - theta[:, None]) * w
        idx = (np.arange(REPS)[:, None] * 24 + blk).ravel()
        bs = np.bincount(idx, weights=dev.ravel(), minlength=REPS * 24).reshape(REPS, 24)
        occ = np.bincount(idx, weights=w.ravel(), minlength=REPS * 24).reshape(REPS, 24) > 0
        g = occ.sum(axis=1)
        v = (bs ** 2).sum(axis=1) / w.sum(axis=1) ** 2 * g / (g - 1)
        tv10 = theta / np.sqrt(v)
        xk = np.where(breach, np.minimum(x0, x1), x)
        tk, gk = cw_t_blocks(xk, blk, 24)
        row[f'breach_share_of_YES_{r}'] = {'mean_breach_share_of_members': round(float(breach.mean()), 4),
                                           'version_10_excluded': rates(tv10, g, CRITS),
                                           'kept_at_least_favourable_outcome': rates(tk, gk, CRITS)}
    rc135[law] = row
rc135['reading'] = ('excluding breached members is a complete-case selection on YES; under law (a) it raises the rejection rate '
                    'at every breach share and cutoff, above alpha from a 1 % breach share at the nominal cutoff and from 2 % at '
                    '2.254; under law (b) the selection cancels on average; keeping the member at its least favourable outcome '
                    'is never above the no-breach size, because the imputed increment is at most the true one, and its cost '
                    'is power, which law (b) shows grows with the breach share')
out['RC135_early_knowability_breach'] = rc135

# ================= r4304595918 (RC-138): registration after a terminal falsifier is public =================
# Deterministic fixture: terminal-falsifier event, falsifier observable from 5 (declared), falsifier public at 6,
# not_before 20, cluster registration record at 10. Version 10 requires registration before the earliest not_before
# only; the proposed rule requires it before the earliest-knowable bound min(not_before, falsifier observable-from).
fixture = {'registration': 10, 'falsifier_observable_from': 5, 'falsifier_public': 6, 'not_before': 20}
rc138 = {'fixture': {**fixture,
                     'version_10_accepts': fixture['registration'] < fixture['not_before'],
                     'proposed_accepts': fixture['registration'] < min(fixture['not_before'], fixture['falsifier_observable_from'])}}
# Selection: law (a) of RC-135 (a NO is favourable to FULL, X = +0.16); 600 clusters registered in time; a registrar
# who may register terminal-falsifier events until not_before adds m late clusters chosen from candidates whose
# falsifier is already public (known NO), in random blocks. No forecast exists at registration under either rule.
rng = np.random.default_rng(1338)
REPS = 20000
y = rng.random((REPS, N)) < 0.4
x = np.where(y, -0.24, 0.16)
row = {'none_added': rates(*cw_t_blocks(x, blk, 24), CRITS)}
for m in (6, 15, 30):
    xa = np.concatenate([x, np.full((REPS, m), 0.16)], axis=1)
    ba = np.concatenate([blk, rng.integers(0, 24, (REPS, m))], axis=1)
    row[f'known_NO_added_{m}'] = {'share_of_cohort': round(m / (N + m), 4), **rates(*cw_t_blocks(xa, ba, 24), CRITS)}
rc138['selection_under_version_10'] = row
rc138['reading'] = ('a registration that may follow a public falsifier selects members on a known outcome; the earliest-knowable '
                    'bound, which version 10 applied to the burn-in only, has to bound every registration and the cutoff check')
out['RC138_falsifier_registration'] = rc138

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
