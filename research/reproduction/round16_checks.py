"""Round-16 checks for the Codex findings on PR #4 at 36a1768 (no reference code, no network).

Review 5562093769. Each block is keyed by the review-comment id it answers. The cluster-weighted statistic with
block-sum variance over occupied blocks is that of 16 Appendix F and L to P. Finding 4306320671 (a commit identity)
is checked by the git commands of 16 Appendix Q and is not in this script.
"""
import itertools, json, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
ALPHA = 0.05
NB, PER = 24, 25
N = NB * PER
REPS = 20000
C_NOM = float(student_t.ppf(1 - ALPHA, NB - 1))
CRITS = (('nominal_G-1_df', C_NOM), ('c_2.254', 2.254))
BLK = np.repeat(np.arange(NB), PER)

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def t_stat(x, blocks):
    # one sample: theta = mean over clusters, variance = block-sum form over occupied blocks on G - 1 df
    x = np.asarray(x, float); blocks = np.asarray(blocks)
    n = x.size
    theta = x.mean()
    labels = np.unique(blocks)
    g = labels.size
    s = np.array([(x[blocks == b] - theta).sum() for b in labels])
    v = (s ** 2).sum() / n ** 2 * g / (g - 1)
    return float(theta / np.sqrt(v)) if v > 0 else float('-inf')
def t_rows(x):
    # many samples on the fixed design BLK (24 occupied blocks of 25)
    theta = x.mean(axis=1)
    s = (x - theta[:, None]).reshape(x.shape[0], NB, PER).sum(axis=2)
    v = (s ** 2).sum(axis=1) / N ** 2 * NB / (NB - 1)
    tt = np.full(x.shape[0], -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt
def rate(reject):
    return {'rate': round(float(reject.mean()), 4), 'upper_99': round(binom_upper(int(reject.sum()), reject.size, 0.99), 4)}
def robust_bound_reject(lo, hi, c):
    # Conservative form of the box rule on the fixed design: reject only if theta at the lower end of every
    # interval exceeds c times an upper bound on the standard error over the whole box. With equal block sizes the
    # map w -> w - (n_g / N) sum(w) is an orthogonal projection, so ||v(x) - v(mid)|| <= sqrt(sum_g R_g^2), where R_g
    # sums the half-widths of the intervals in block g. Rejection here implies rejection at every point of the box.
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    theta_mid = mid.mean(axis=1)
    s_mid = (mid - theta_mid[:, None]).reshape(mid.shape[0], NB, PER).sum(axis=2)
    r = half.reshape(mid.shape[0], NB, PER).sum(axis=2)
    se_up = (np.sqrt((s_mid ** 2).sum(axis=1)) + np.sqrt((r ** 2).sum(axis=1))) / N * np.sqrt(NB / (NB - 1))
    theta_lo = lo.mean(axis=1)
    return (theta_lo > c * se_up) & (se_up > 0)
def robust_exact(x, blocks, idx, lo, hi, c):
    # Exact box rule for a few affected members: theta(x) - c * se(x) is concave in the affected increments (an affine
    # function minus a norm of an affine function), so its minimum over the box is at a vertex.
    ts = []
    for corner in itertools.product(*[(a, b) for a, b in zip(lo, hi)]):
        y = np.array(x, float); y[idx] = corner
        ts.append(t_stat(y, blocks))
    return min(ts), min(ts) > c

# ================= r4306320659 (RC-148): the least-favourable substitution is not conservative =================
# Codex's fixture: 24 singleton blocks, 23 increments of 0.001 and one breached pair with p_baseline = 0, p_FULL = 0.02.
blocks = np.arange(24)
base = [0.001] * 23
x_y1 = (0 - 1) ** 2 - (0.02 - 1) ** 2
x_y0 = (0 - 0) ** 2 - (0.02 - 0) ** 2
rc148 = {'codex_fixture': {'X_at_Y1': round(x_y1, 4), 'X_at_Y0_least_favourable': round(x_y0, 4),
                           't_at_Y1': round(t_stat(base + [x_y1], blocks), 3),
                           't_at_least_favourable_Y0': round(t_stat(base + [x_y0], blocks), 3)}}
# Proposed: a comparison rejects only if it rejects at every value of the affected increments in their intervals.
# As a source-latency defect (forecasts clean, outcome in doubt) the interval is [X(Y=0), X(Y=1)]; as an
# early-knowability breach with Y = 1 recorded and FULL's forecast possibly informed, it is
# [(b - Y)^2 - 1, (b - Y)^2] = [0, 1].
for name, (a, b) in {'defect_interval': (x_y0, x_y1), 'breach_interval_Y1': (0.0, 1.0)}.items():
    lo_t = t_stat(base + [a], blocks); hi_t = t_stat(base + [b], blocks)
    rc148['codex_fixture'][name] = {'interval': [round(a, 4), round(b, 4)], 't_at_lower_end': round(lo_t, 3),
                                    't_at_upper_end': round(hi_t, 3),
                                    'rejects_at_nominal_or_any_c_star': min(lo_t, hi_t) > C_NOM}
# Concavity: on random samples with two affected members the minimum of theta - c*se over a 41 x 41 grid of the box
# is never below the minimum over its four vertices.
rng = np.random.default_rng(16481)
worst_gap = np.inf
for _ in range(200):
    x = rng.normal(0.02, 0.2, 48).clip(-1, 1); blk = np.repeat(np.arange(12), 4)
    idx = rng.choice(48, 2, replace=False)
    def f(vals):
        y = x.copy(); y[idx] = vals
        theta = y.mean(); s = np.array([(y[blk == g] - theta).sum() for g in range(12)])
        return theta - 2.254 * np.sqrt((s ** 2).sum() / 48 ** 2 * 12 / 11)
    grid = np.linspace(-1, 1, 41)
    gmin = min(f((u, w)) for u in grid for w in grid)
    vmin = min(f(v) for v in itertools.product((-1, 1), (-1, 1)))
    worst_gap = min(worst_gap, gmin - vmin)
rc148['concavity_grid_minus_vertex_min_over_200_samples'] = round(float(worst_gap), 12)
# Null laws of 16 Appendix N (law a: p_b = 0.5, p_F = 0.3, Y ~ Bern(0.4)) and P (law c: p_b = 0.9, p_F = 0.1,
# Y ~ Bern(0.5)), 600 singleton clusters in 24 maturity blocks. Breaches hit YES members only (only a YES can be
# knowable early), at shares of all members; the breached FULL forecast is informed: p_FULL = 1 on a YES.
# honest = every member scored from its honest forecast; v13 = the breach scored at the outcome least favourable to
# FULL with the forecast it carries; proposed = the box rule with Y recorded and FULL's forecast free in [0, 1].
for name, (pb, pf, py) in {'a_appendixN': (0.5, 0.3, 0.4), 'c_appendixP': (0.9, 0.1, 0.5)}.items():
    rng = np.random.default_rng(16482)
    y = (rng.random((REPS, N)) < py).astype(float)
    u = rng.random((REPS, N))
    x_honest = (pb - y) ** 2 - (pf - y) ** 2
    t_h = t_rows(x_honest)
    row = {'honest': {lab: rate(t_h > c) for lab, c in CRITS}}
    for share in (0.01, 0.02, 0.04):
        br = (y == 1) & (u < share / py)
        x_v13 = np.where(br, np.minimum((pb - 1) ** 2 - (1 - 1) ** 2, (pb - 0) ** 2 - (1 - 0) ** 2), x_honest)
        lo = np.where(br, (pb - y) ** 2 - 1, x_honest)
        hi = np.where(br, (pb - y) ** 2, x_honest)
        t_v = t_rows(x_v13)
        cell = {'mean_breaches': round(float(br.sum(axis=1).mean()), 2)}
        for lab, c in CRITS:
            rob = robust_bound_reject(lo, hi, c)
            cell[lab] = {'version_13_least_favourable': rate(t_v > c), 'proposed_box_rule': rate(rob),
                         'proposed_rejects_where_honest_does_not': int((rob & ~(t_h > c)).sum())}
        row[f'breach_share_{share}'] = cell
    rc148[f'law_{name}'] = row
# Power cost under an alternative (law a with Y ~ Bern(0.35): E[X] = +0.02), and the exact vertex rule against the
# conservative bound on 300 samples with three breaches each.
rng = np.random.default_rng(16483)
y = (rng.random((REPS, N)) < 0.35).astype(float)
u = rng.random((REPS, N))
x_honest = (0.5 - y) ** 2 - (0.3 - y) ** 2
t_h = t_rows(x_honest)
pw = {'honest': {lab: round(float((t_h > c).mean()), 4) for lab, c in CRITS}}
for share in (0.005, 0.01, 0.02):
    br = (y == 1) & (u < share / 0.35)
    lo = np.where(br, (0.5 - y) ** 2 - 1, x_honest); hi = np.where(br, (0.5 - y) ** 2, x_honest)
    pw[f'breach_share_{share}'] = {lab: round(float(robust_bound_reject(lo, hi, c).mean()), 4) for lab, c in CRITS}
rc148['power_delta_0.02_600_clusters'] = pw
agree, exact_only, bound_only = 0, 0, 0
for r in range(300):
    idx = np.flatnonzero(y[r] == 1)[:3]
    lo_r, hi_r = (0.5 - 1) ** 2 - 1, (0.5 - 1) ** 2
    _, ex = robust_exact(x_honest[r], BLK, idx, [lo_r] * 3, [hi_r] * 3, 2.254)
    lo = x_honest[r:r + 1].copy(); hi = lo.copy(); lo[0, idx] = lo_r; hi[0, idx] = hi_r
    bd = bool(robust_bound_reject(lo, hi, 2.254)[0])
    agree += ex == bd; exact_only += ex and not bd; bound_only += bd and not ex
rc148['exact_vertex_vs_bound_300_samples_3_breaches_c_2.254'] = {'agree': agree, 'exact_only': exact_only,
                                                                 'bound_only': bound_only}
out['RC148_box_rule'] = rc148

# ================= r4306320663 (RC-149): defects still latent at the analysis date =================
# Law c (Codex's forecasts). Defects on a share r of members, YES members only; a share phi of them is recorded only
# after the decision. Recorded defects go to the box rule (both outcomes); latent ones are scored at the graded NO.
# On the event "no latent defect" the box decision implies the honest decision, so
# size <= honest size + P(at least one latent defect); the check prints both sides.
rng = np.random.default_rng(16491)
pb, pf, py = 0.9, 0.1, 0.5
y = (rng.random((REPS, N)) < py).astype(float)
u, w = rng.random((REPS, N)), rng.random((REPS, N))
x_honest = (pb - y) ** 2 - (pf - y) ** 2
x_no = (pb - 0) ** 2 - (pf - 0) ** 2
rc149 = {}
for lab, c in CRITS:
    honest = t_rows(x_honest) > c
    rows = {'honest': rate(honest)}
    for r, phi in ((0.01, 0.0), (0.01, 0.05), (0.01, 0.2), (0.01, 1.0), (0.002, 0.05)):
        d = (y == 1) & (u < r / py)
        latent = d & (w < phi)
        recorded = d & ~latent
        lo = np.where(recorded, np.minimum(x_no, x_honest), np.where(latent, x_no, x_honest))
        hi = np.where(recorded, np.maximum(x_no, x_honest), lo)
        rej = robust_bound_reject(lo, hi, c)
        p_latent = float(latent.any(axis=1).mean())
        rows[f'defect_share_{r}_latent_share_{phi}'] = {'box_rule_rate': rate(rej), 'P_any_latent': round(p_latent, 4),
                                                         'honest_plus_P_any_latent': round(float(honest.mean()) + p_latent, 4)}
    rc149[lab] = rows
out['RC149_latent_defects'] = rc149

# ================= r4306320668 (RC-150): cohort withdrawal informed by forecasts before any outcome =================
# Twenty arm-version cohorts of 30 clusters (interleaved over the 24 maturity blocks), cohort expected increments
# +delta for ten and -delta for ten (population average exactly zero), X = mu_c +/- 0.2. Forecasts reveal mu_c before
# any outcome. Withdrawing one -delta cohort is 5 % of the cohort, inside a 5 % cap; Codex's case is two cohorts.
rc150 = {}
for delta in (0.02, 0.05):
    rng = np.random.default_rng(16501)
    cohort = np.arange(N) % 20
    mu = np.where(cohort < 10, delta, -delta)
    x = mu[None, :] + np.where(rng.random((REPS, N)) < 0.5, 0.2, -0.2)
    keep = cohort != 10
    xk = x[:, keep]; bk = BLK[keep]
    theta = xk.mean(axis=1)
    s = np.zeros((REPS, NB))
    for g in range(NB):
        s[:, g] = (xk[:, bk == g] - theta[:, None]).sum(axis=1)
    tk = theta / np.sqrt((s ** 2).sum(axis=1) / keep.sum() ** 2 * NB / (NB - 1))
    t_all = t_rows(x)
    two = np.where(np.arange(N) % 2 == 0, delta, -delta)[None, :] + np.where(rng.random((REPS, N)) < 0.5, 0.2, -0.2)
    keep2 = np.arange(N) % 2 == 0
    x2 = two[:, keep2]; b2 = BLK[keep2]; th2 = x2.mean(axis=1)
    s2 = np.zeros((REPS, NB))
    for g in range(NB):
        s2[:, g] = (x2[:, b2 == g] - th2[:, None]).sum(axis=1)
    t2 = th2 / np.sqrt((s2 ** 2).sum(axis=1) / keep2.sum() ** 2 * NB / (NB - 1))
    rc150[f'delta_{delta}'] = {lab: {'no_withdrawal': rate(t_all > c), 'one_of_20_cohorts_withdrawn': rate(tk > c),
                                     'codex_two_cohorts_one_withdrawn': rate(t2 > c)} for lab, c in CRITS}
out['RC150_forecast_informed_withdrawal'] = rc150

# ================= r4306320676 (RC-152): forecast pairs beyond d_max =================
# Clipping FULL's scored forecast into [p_ref - d_max, p_ref + d_max] at t_close is a function of the sealed forecasts
# alone. Fixture: p_baseline 0.5, p_FULL 0.9, d_max 0.2.
def brier_x(pb, pf, yv):
    return round((pb - yv) ** 2 - (pf - yv) ** 2, 4)
rc152 = {'fixture': {'scored_p_FULL': round(min(max(0.9, 0.5 - 0.2), 0.5 + 0.2), 4),
                     'X_clipped': {'Y1': brier_x(0.5, 0.7, 1), 'Y0': brier_x(0.5, 0.7, 0)},
                     'X_unclipped': {'Y1': brier_x(0.5, 0.9, 1), 'Y0': brier_x(0.5, 0.9, 0)}}}
# Dropping over-limit pairs after the forecasts are seen: 10 % of members carry an over-limit FULL forecast
# (p_F = 0.9, p_b = 0.5, Y ~ Bern(0.5), E[X] = -0.16), the rest p_F = 0.6, p_b = 0.5, Y ~ Bern(q) with q set so that
# the population mean is zero. The three dispositions answer three different questions (the raw forecaster over the
# population, the clipped rule over the population, the raw forecaster over a forecast-selected subpopulation), so the
# rule has to be fixed before any forecast exists; only clipping keeps every member and every pair inside d_max.
rng = np.random.default_rng(16521)
over = rng.random((REPS, N)) < 0.1
q_in = 0.5 + 0.16 * 0.1 / 0.9 / 0.2
y = (rng.random((REPS, N)) < np.where(over, 0.5, q_in)).astype(float)
x_raw = np.where(over, (0.5 - y) ** 2 - (0.9 - y) ** 2, (0.5 - y) ** 2 - (0.6 - y) ** 2)
x_clip = np.where(over, (0.5 - y) ** 2 - (0.7 - y) ** 2, x_raw)
rc152['law_means'] = {'raw_FULL_all_members': round(float(x_raw.mean()), 4),
                      'clipped_FULL_all_members': round(float(x_clip.mean()), 4),
                      'raw_FULL_within_limit_members_only': round(float(x_raw[~over].mean()), 4)}
theta = np.where(over, 0, x_raw).sum(axis=1) / (~over).sum(axis=1)
dev = np.where(over, 0, x_raw - theta[:, None]).reshape(REPS, NB, PER).sum(axis=2)
t_drop = theta / np.sqrt((dev ** 2).sum(axis=1) / (~over).sum(axis=1) ** 2 * NB / (NB - 1))
rc152['rates'] = {lab: {'drop_over_limit': rate(t_drop > c), 'include_unclipped': rate(t_rows(x_raw) > c),
                        'clip_at_t_close': rate(t_rows(x_clip) > c)} for lab, c in CRITS}
out['RC152_d_max'] = rc152

# ================= r4306320679 (RC-153): crash recovery across the external anchor =================
# Toy model. A protected action consumes a nonce and changes state. Protocols: L = local commit, then anchor, then ack;
# A = anchor the would-be prefix, then local commit, then ack; P = local intent record (nonce consumed, state change
# not effective), anchor of the prefix ending at the intent, local commit record, ack; a pending intent at start is
# aborted. A crash happens after each step; afterwards the ledger is either kept or restored to the last anchor and
# the same capability is presented again. Invariants: I1 the action takes effect at most once; I2 no external anchor
# covers a prefix the local ledger never held; I3 an acknowledged action is in an anchored prefix.
def run(protocol, crash_after, restore):
    ledger, anchors, effects, acked = [], [], 0, False
    def anchor():
        anchors.append(len(ledger))
    def present():
        nonlocal effects, acked
        consumed = any(r[0] in ('commit', 'intent') for r in ledger)
        if consumed:
            return
        steps = {'L': ['commit', 'anchor', 'ack'], 'A': ['anchor_ahead', 'commit', 'ack'],
                 'P': ['intent', 'anchor', 'commit', 'ack']}[protocol]
        for i, st in enumerate(steps):
            if st == 'commit':
                ledger.append(('commit',))
                effects += 1
            elif st == 'intent':
                ledger.append(('intent',))
            elif st == 'anchor':
                anchor()
            elif st == 'anchor_ahead':
                anchors.append(len(ledger) + 1)
            elif st == 'ack':
                acked = True
            if crash_after is not None and i == crash_after:
                return 'crash'
        return 'done'
    first = present()
    if first == 'crash':
        if protocol == 'P' and ledger and ledger[-1][0] == 'intent':
            ledger.append(('abort',))
    i2 = all(a <= len(ledger) for a in anchors)
    if restore:
        last = max(anchors) if anchors else 0
        if last > len(ledger):
            return {'I1': True, 'I2': False, 'I3': True, 'note': 'anchor beyond local ledger: replay cannot verify'}
        ledger = ledger[:last]
        if protocol == 'P' and ledger and ledger[-1][0] == 'intent':
            ledger.append(('abort',))
    acked_anchored = (not acked) or (max(anchors, default=0) >= 1)
    crash_after = None
    present()
    return {'I1': effects <= 1, 'I2': i2, 'I3': acked_anchored}
rc153 = {}
for proto, nsteps in (('L', 3), ('A', 3), ('P', 4)):
    viol = []
    for k in list(range(nsteps)) + [None]:
        for restore in (False, True):
            res = run(proto, k, restore)
            bad = [key for key in ('I1', 'I2', 'I3') if not res[key]]
            if bad:
                viol.append({'crash_after_step': k, 'restore_to_last_anchor': restore, 'violated': bad})
    rc153[proto] = viol
out['RC153_anchor_crash_points'] = rc153

# ================= r4306320684 (RC-154): denominator of the VOID cap =================
# Codex's case: 100 clusters, one of 50 members, the rest of 2; two VOIDs in the large cluster, or the two members of
# a two-member cluster. Shares: member fraction, cluster fraction and the cluster-weighted share (1/N) sum v_k / s_k.
def shares(sizes, voids):
    sizes, voids = np.array(sizes), np.array(voids)
    return {'member_fraction': round(float(voids.sum() / sizes.sum()), 5),
            'cluster_fraction_any_void': round(float((voids > 0).mean()), 5),
            'cluster_weighted_share': round(float((voids / sizes).mean()), 5)}
sizes = [50] + [2] * 99
rc154 = {'two_voids_in_the_50_member_cluster': shares(sizes, [2] + [0] * 99),
         'two_voids_forming_one_2_member_cluster': shares(sizes, [0, 2] + [0] * 98)}
# The worst-case interval of the imputed estimate (1/N) sum_k (1/s_k) sum_i X_i, VOID members at -1 and +1, has width
# 2 * the cluster-weighted share exactly; checked on 1,000 random designs.
rng = np.random.default_rng(16541)
dev_max = 0.0
for _ in range(1000):
    k = rng.integers(20, 200); s = rng.integers(1, 8, k); v = rng.binomial(s, 0.05)
    xs = [rng.uniform(-1, 1, si) for si in s]
    lo = np.mean([(x[vi:].sum() - vi) / si for x, vi, si in zip(xs, v, s)])
    hi = np.mean([(x[vi:].sum() + vi) / si for x, vi, si in zip(xs, v, s)])
    dev_max = max(dev_max, abs((hi - lo) - 2 * float((v / s).mean())))
rc154['max_abs_width_minus_2_share_over_1000_designs'] = float(f'{dev_max:.3e}')
out['RC154_void_cap_denominator'] = rc154

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
