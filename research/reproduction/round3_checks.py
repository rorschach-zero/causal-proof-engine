"""Round-3 checks for the Codex findings on PR #4 at 43754cc (no reference code, no network)."""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA, THRESHOLD, LAM_MAX = 0.05, 20.0, 0.5

# ---- r4296395259 (RC-48): A3 / T-10 keep 2,000 replications with a 95 % bound <= 0.06 ----
def k_max(n_rep, conf, limit):
    return max(k for k in range(0, int(n_rep * 0.2)) if beta.ppf(conf, k + 1, n_rep - k) <= limit)
a3 = {}
for n_rep, conf in [(2000, 0.95), (20000, 0.99)]:
    k = k_max(n_rep, conf, 0.06)
    a3[f'n={n_rep},conf={conf}'] = {'k_max': k,
                                   'P_pass_if_size_exactly_0.05': round(float(binom.cdf(k, n_rep, 0.05)), 6),
                                   'P_pass_if_size_0.06': round(float(binom.cdf(k, n_rep, 0.06)), 6),
                                   'P_pass_if_size_0.07': float(binom.cdf(k, n_rep, 0.07))}
out['RC48_a3_design'] = a3

# ---- archived GRAPA recurrence (vectorised), identical to 16 Appendix A ----
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
    return peak

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))

# Baseline 0.4, challenger 0.6, so X = (0.4-Y)^2 - (0.6-Y)^2 = 0.4*Y - 0.2 and E[X | P(Y=1)=q] = 0.4*q - 0.2.
def increments(q, rng):
    y = (rng.random(q.shape) < q).astype(float)
    return 0.4 * y - 0.2

def fixed_horizon_sizes(xs, periods, blocks):
    """One-sided tests of mean X <= 0 at alpha: naive (clusters iid) and block-clustered (t with G-1 df)."""
    res = {}
    k = xs.shape[1]
    m = xs.mean(axis=1); sd = xs.std(axis=1, ddof=1)
    with np.errstate(divide='ignore', invalid='ignore'):          # sd = 0 gives +/-inf or nan, counted as written
        tn = m / (sd / math.sqrt(k))
        res['naive_iid_cluster_t'] = float((tn > student_t.ppf(1 - ALPHA, k - 1)).mean())
        for b in blocks:
            g = periods // b
            bm = xs.reshape(xs.shape[0], g, -1).mean(axis=2)      # block means, equal block sizes
            tb = bm.mean(axis=1) / (bm.std(axis=1, ddof=1) / math.sqrt(g))
            res[f'block_of_{b}_periods_t_df{g-1}'] = float((tb > student_t.ppf(1 - ALPHA, g - 1)).mean())
    return res

REPS, PERIODS, PER_PERIOD = 20000, 24, 5
K = PERIODS * PER_PERIOD                                           # 120 clusters, closed in calendar order
rng = np.random.default_rng(2026)
families = {}

# (0) valid clustered null restated at 20,000 replications: independent clusters, q = 0.5.
q0 = np.full((REPS, K), 0.5)
x0 = increments(q0, rng)
fa0 = int((grapa_paths(x0) >= THRESHOLD).sum())
families['independent_clusters_valid_null'] = {
    'eprocess_crossings': fa0, 'eprocess_rate': fa0 / REPS,
    'exact_upper_99': round(binom_upper(fa0, REPS, 0.99), 6),
    'fixed_horizon_size': fixed_horizon_sizes(x0, PERIODS, (1, 3, 6))}

# (1) r4296395273 (RC-49): macro shock shared by every cluster open in a calendar period, iid across periods.
shock = rng.choice([-0.3, 0.3], size=(REPS, PERIODS))
q1 = np.repeat(0.5 + shock, PER_PERIOD, axis=1)
x1 = increments(q1, rng)
fa1 = int((grapa_paths(x1) >= THRESHOLD).sum())
families['macro_shock_iid_periods'] = {
    'description': 'q_t = 0.5 +/- 0.3 per period, 5 clusters per period, marginal E[X] = 0',
    'eprocess_crossings': fa1, 'eprocess_rate': fa1 / REPS,
    'exact_lower_99': round(float(beta.ppf(0.01, fa1, REPS - fa1 + 1)), 6),
    'fixed_horizon_size': fixed_horizon_sizes(x1, PERIODS, (1, 3, 6))}

# (2) persistent macro regime: shock follows a two-state chain with persistence 0.9 (mean zero).
s = np.empty((REPS, PERIODS)); s[:, 0] = rng.choice([-0.3, 0.3], size=REPS)
for tt in range(1, PERIODS):
    stay = rng.random(REPS) < 0.9
    s[:, tt] = np.where(stay, s[:, tt - 1], -s[:, tt - 1])
q2 = np.repeat(0.5 + s, PER_PERIOD, axis=1)
x2 = increments(q2, rng)
fa2 = int((grapa_paths(x2) >= THRESHOLD).sum())
families['macro_shock_persistent_regime'] = {
    'description': 'two-state regime, P(stay) = 0.9, stationary mean zero',
    'eprocess_crossings': fa2, 'eprocess_rate': fa2 / REPS,
    'fixed_horizon_size': fixed_horizon_sizes(x2, PERIODS, (1, 3, 6)),
    'note': 'period means are autocorrelated; a block of one period is not a valid unit here; the block length is a pre-registered dependence model'}

# (3) r4296395298 (RC-50): time-varying skill, average effect exactly zero (first half +, second half -).
q3 = np.concatenate([np.full((REPS, K // 2), 0.8), np.full((REPS, K // 2), 0.2)], axis=1)   # E[X] = +0.12 then -0.12
x3 = increments(q3, rng)
fa3 = int((grapa_paths(x3) >= THRESHOLD).sum())
families['time_varying_skill_average_zero'] = {
    'description': 'E[X_k] = +0.12 for k <= 60, -0.12 for k > 60; average over the population = 0',
    'eprocess_crossings_by_120': fa3, 'eprocess_rate': fa3 / REPS,
    'fixed_horizon_size': fixed_horizon_sizes(x3, PERIODS, (1, 3, 6))}

# (4) time-varying skill, average effect NEGATIVE: first 40 clusters +0.12, remaining 80 clusters -0.08.
q4 = np.concatenate([np.full((REPS, 40), 0.8), np.full((REPS, 80), 0.3)], axis=1)
x4 = increments(q4, rng)
avg4 = (40 * 0.12 + 80 * (0.4 * 0.3 - 0.2)) / 120
fa4 = int((grapa_paths(x4) >= THRESHOLD).sum())
families['time_varying_skill_average_negative'] = {
    'description': 'E[X_k] = +0.12 for k <= 40, -0.08 for k > 40',
    'population_average_effect': round(avg4, 5),
    'eprocess_crossings_by_120': fa4, 'eprocess_rate': fa4 / REPS,
    'fixed_horizon_rejections': fixed_horizon_sizes(x4, PERIODS, (1, 3, 6))}
out['RC49_RC50_null_families'] = families
out['RC49_RC50_reading'] = ('the e-process controls the error of the sequential conditional null E[X_k | F_(k-1)] <= 0; '
                            'under cross-cluster dependence or time-varying skill that null is false while the '
                            'population-average null holds, so a crossing is not evidence about the average estimand')

# ---- r4296395308 (RC-52): forecast eligibility against the earliest time the outcome was knowable ----
def eligible(forecast_receipt, knowable_at, first_outcome_receipt):
    return forecast_receipt < min(knowable_at, first_outcome_receipt)
out['RC52_publication_gap'] = {
    'publication_10:00_forecast_received_10:05_outcome_received_10:30':
        {'eligible_under_v2_T-02_rule': 605 < 630, 'eligible_under_v3_rule': eligible(605, 600, 630)},
    'forecast_received_09:55': {'eligible_under_v3_rule': eligible(595, 600, 630)}}

# ---- r4296395335 (RC-54): deterministic oracle fixtures for the shrinkage estimator ----
def logit(p): return math.log(p / (1 - p))
def expit(z): return 1 / (1 + math.exp(-z))
a, b = 2.0, 18.0                      # pre-registered reference-class prior, mean 0.10
fixtures = {}
for s_, n_ in [(5, 20), (0, 50), (0, 0)]:
    post = beta(a + s_, b + n_ - s_)
    fixtures[f's={s_},n={n_}'] = {'posterior': f'Beta({a + s_:g}, {b + n_ - s_:g})',
                                  'mean': round(float(post.mean()), 6),
                                  'q05': round(float(post.ppf(0.05)), 6), 'q95': round(float(post.ppf(0.95)), 6),
                                  'naive_s_over_n': (s_ / n_) if n_ else None}
out['RC54_beta_posterior_fixtures'] = fixtures
n0 = 20.0                             # pre-registered: model weight w(n) = n0 / (n0 + n)
logit_fx = {}
for p_model, (s_, n_) in [(0.001, (5, 20)), (0.001, (0, 0)), (0.5, (5, 20))]:
    ref = (a + s_) / (a + b + n_)
    w = n0 / (n0 + n_)
    p_out = expit(w * logit(p_model) + (1 - w) * logit(ref))
    logit_fx[f'p_model={p_model},s={s_},n={n_}'] = {'reference_rate': round(ref, 6), 'w_model': round(w, 4),
                                                   'point': round(p_out, 6)}
out['RC54_logit_shrinkage_fixtures'] = logit_fx
out['RC54_trivial_implementation_fails'] = fixtures['s=5,n=20']['naive_s_over_n'] != fixtures['s=5,n=20']['mean']

# ---- RC-55 (self-reported, issue #3 comment 6218965225): frame locals keep a secret reachable ----
def canary(): return 'SYNTHETIC-' + 'CANARY-r3'
class Transport(Exception):
    def __init__(self, request): super().__init__('transport'); self.request = request
class Sanitized(RuntimeError): pass
class Redacted:
    def __init__(self, value): self._value = value
    def __repr__(self): return 'Redacted(***)'
def reachable(exc):
    seen, found, stack = set(), [], [exc]
    while stack:
        e = stack.pop()
        if e is None or id(e) in seen: continue
        seen.add(id(e)); found.append(e); stack += [e.__context__, e.__cause__]
        tb = e.__traceback__
        while tb is not None:
            for v in tb.tb_frame.f_locals.values():
                (stack if isinstance(v, BaseException) else found).append(v)
            tb = tb.tb_next
    return found
def leaks(exc): return any(canary() in repr(o) for o in reachable(exc))
def case_from_none():
    headers = {'Authorization': f'Bearer {canary()}'}
    try: raise Transport(headers)
    except Transport: raise Sanitized('transport error') from None
def case_context_none():
    headers = {'Authorization': f'Bearer {canary()}'}
    try: raise Transport(headers)
    except Transport:
        s_ = Sanitized('transport error'); s_.__context__ = None; raise s_
def case_outside_plain_local():
    headers = {'Authorization': f'Bearer {canary()}'}; kind = None
    try: raise Transport(headers)
    except Transport as ex: kind = type(ex).__name__
    raise Sanitized(f'transport error: {kind}')
def case_outside_redacted():
    auth = Redacted(f'Bearer {canary()}'); kind = None
    try: raise Transport({'Authorization': auth})
    except Transport as ex: kind = type(ex).__name__
    raise Sanitized(f'transport error: {kind}')
table = {}
for name, fn in [('from_None_in_handler', case_from_none), ('context_None_in_handler', case_context_none),
                 ('outside_handler_plain_local', case_outside_plain_local), ('outside_handler_redacting_holder', case_outside_redacted)]:
    try: fn()
    except Sanitized as s_: table[name] = {'context_is_None': s_.__context__ is None, 'canary_reachable': leaks(s_)}
out['RC55_exception_graph_canary'] = table
out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
