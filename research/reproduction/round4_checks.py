"""Round-4 checks for the Codex findings on PR #4 at d46c204 (no reference code, no network)."""
import hashlib, hmac, json, math, sys, types
import numpy as np
from scipy.stats import beta, binom, norm, multivariate_normal, t as student_t

out = {}
ALPHA, THRESHOLD, LAM_MAX = 0.05, 20.0, 0.5

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

# ---- archived GRAPA recurrence (vectorised), identical to 16 Appendix A and D ----
def grapa_paths(xs, lam_max=LAM_MAX, checkpoints=()):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    snaps = {}
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
        if n + 1 in checkpoints:
            snaps[n + 1] = peak.copy()
    return wealth, peak, snaps

def block_t(xs, per_period, block_periods=1):
    """One-sided block-clustered t statistic of mean X <= 0: blocks of block_periods calendar periods."""
    n_paths, k = xs.shape
    periods = k // per_period
    g = periods // block_periods
    bm = xs[:, :g * block_periods * per_period].reshape(n_paths, g, -1).mean(axis=2)
    with np.errstate(divide='ignore', invalid='ignore'):
        tb = bm.mean(axis=1) / (bm.std(axis=1, ddof=1) / math.sqrt(g))
    return tb, g - 1

def block_t_rejects(xs, per_period, alpha=ALPHA, block_periods=1):
    tb, df = block_t(xs, per_period, block_periods)
    return tb > student_t.ppf(1 - alpha, df)

# ================= r4296649357 (RC-56): one primary claim evaluated at two cut-offs =================
# Normal theory: two one-sided tests at information fractions 0.5 and 1.0 (correlation sqrt(0.5)),
# each at nominal alpha = 0.05; P(reject at either look) under the null.
z = norm.ppf(1 - ALPHA)
rho = math.sqrt(0.5)
cov = [[1.0, rho], [rho, 1.0]]
p_neither = float(multivariate_normal(mean=[0, 0], cov=cov).cdf([z, z]))
two_look = {'nominal_alpha_each_look': ALPHA, 'information_fractions': [0.5, 1.0],
            'type_I_error_reject_at_either_look_normal_theory': round(1 - p_neither, 5)}
# Lan-DeMets O'Brien-Fleming-type spending for one-sided alpha at t = 0.5, final boundary solved so that the
# total equals alpha under the same correlation.
def obf_spend(t_frac, alpha=ALPHA):
    return 2 * (1 - norm.cdf(norm.ppf(1 - alpha / 2) / math.sqrt(t_frac)))
a1 = obf_spend(0.5)
c1 = norm.ppf(1 - a1)
def total_alpha(c2):
    return 1 - float(multivariate_normal(mean=[0, 0], cov=cov).cdf([c1, c2]))
lo, hi = 1.0, 3.0
for _ in range(60):
    mid = (lo + hi) / 2
    if total_alpha(mid) > ALPHA: lo = mid
    else: hi = mid
c2 = (lo + hi) / 2
two_look['obf_spending_option'] = {'alpha_spent_at_12_months': round(a1, 5), 'z_boundary_12_months': round(c1, 4),
                                   'z_boundary_24_months': round(c2, 4), 'nominal_level_24_months': round(1 - norm.cdf(c2), 5),
                                   'total_type_I_error': round(total_alpha(c2), 5)}
# Simulation with the block-of-one-period t test on the round-3 generator (baseline 0.4, challenger 0.6,
# X = 0.4 Y - 0.2): look 1 after 12 periods (60 clusters), look 2 after 24 periods (120 clusters).
REPS, PERIODS, PER_PERIOD = 20000, 24, 5
K = PERIODS * PER_PERIOD
rng = np.random.default_rng(4026)
def increments(q, rng_):
    y = (rng_.random(q.shape) < q).astype(float)
    return 0.4 * y - 0.2
sim = {}
fam = {'independent_clusters_valid_null': np.full((REPS, K), 0.5)}
shock = rng.choice([-0.3, 0.3], size=(REPS, PERIODS))
fam['macro_shock_iid_periods'] = np.repeat(0.5 + shock, PER_PERIOD, axis=1)
for name, q in fam.items():
    x = increments(q, rng)
    r1 = block_t_rejects(x[:, :K // 2], PER_PERIOD)
    r2 = block_t_rejects(x, PER_PERIOD)
    t1, df1 = block_t(x[:, :K // 2], PER_PERIOD); t2, df2 = block_t(x, PER_PERIOD)
    # OBF-type boundaries applied to the t statistics through their own df (nominal levels a1 and 1 - Phi(c2)).
    s1_ = t1 > student_t.ppf(1 - a1, df1); s2_ = t2 > student_t.ppf(norm.cdf(c2), df2)
    sim[name] = {'reject_12m_only': round(float(r1.mean()), 5), 'reject_24m_only': round(float(r2.mean()), 5),
                 'reject_at_either_look_both_nominal_0.05': round(float((r1 | r2).mean()), 5),
                 'exact_lower_99_either_look': round(binom_lower(int((r1 | r2).sum()), REPS, 0.99), 5),
                 'single_primary_at_24m_with_12m_futility_look_only': round(float(r2.mean()), 5),
                 'obf_spending_both_looks': round(float((s1_ | s2_).mean()), 5)}
two_look['block_t_simulation'] = sim
out['RC56_two_cutoffs'] = two_look

# ================= r4296649368 (RC-57): VOID declared between knowable_at and registry receipt =================
def void_accepted_v3(void_receipt, first_outcome_receipt):      # v3 wording: "before any member's outcome was received"
    return void_receipt < first_outcome_receipt
def void_accepted_v4(void_receipt, t_star):                      # v4 wording: before the cluster's outcome-knowable time
    return void_receipt < t_star
knowable, outcome_receipt = 600, 630                             # 10:00 publication, 10:30 registry receipt
t_star = min(knowable, outcome_receipt)
out['RC57_void_window'] = {
    'void_received_10:10': {'accepted_under_v3_rule': void_accepted_v3(610, outcome_receipt),
                            'accepted_under_v4_rule': void_accepted_v4(610, t_star)},
    'void_received_09:55': {'accepted_under_v3_rule': void_accepted_v3(595, outcome_receipt),
                            'accepted_under_v4_rule': void_accepted_v4(595, t_star)},
    'reading': 'the v3 clause used receipt time where RC-52 had already moved every other cutoff to t*_k'}

# ================= r4296649378 (RC-58): interval transformation of the shrinkage estimator =================
def logit(p): return math.log(p / (1 - p))
def expit(zz): return 1 / (1 + math.exp(-zz))
A_, B_, N0, EPS = 2.0, 18.0, 20.0, 1e-6                           # fixture prior, weight scale, logit clip
def shrink(low, point, high, s_, n_):
    post = beta(A_ + s_, B_ + n_ - s_)
    targets = (float(post.ppf(0.05)), float(post.mean()), float(post.ppf(0.95)))
    w = N0 / (N0 + n_)
    res = []
    for p_model, ref in zip((low, point, high), targets):
        p_clip = min(max(p_model, EPS), 1 - EPS)
        res.append(expit(w * logit(p_clip) + (1 - w) * logit(ref)))
    return tuple(round(v, 6) for v in res)
interval_fx = {}
for (lo_, pt_, hi_), (s_, n_) in [((0.0005, 0.001, 0.002), (5, 20)), ((0.3, 0.5, 0.7), (5, 20)),
                                  ((0.0005, 0.001, 0.002), (0, 0)), ((0.001, 0.001, 0.001), (5, 20)),
                                  ((0.0, 0.001, 0.002), (5, 20)), ((0.0005, 0.001, 0.002), (0, 50))]:
    r = shrink(lo_, pt_, hi_, s_, n_)
    interval_fx[f'model=({lo_},{pt_},{hi_}),s={s_},n={n_}'] = {'low': r[0], 'point': r[1], 'high': r[2],
                                                               'ordered': r[0] <= r[1] <= r[2]}
out['RC58_interval_fixtures'] = interval_fx
out['RC58_raw_posterior_bounds_would_violate_ordering'] = {'posterior_q05_at_(5,20)': 0.087401, 'shrunk_point': 0.014362,
                                                           'low_le_point_if_raw_bounds_used': 0.087401 <= 0.014362}

# ================= r4296649412 (RC-61): power of the fixed-horizon primary test =================
# D1 generator of 16 Appendix A: baseline b, challenger p = b +/- sqrt(delta), Y ~ Bern(p),
# X = (b - Y)^2 - (p - Y)^2 with E[X] = delta; one increment per cluster, clusters independent, five per
# calendar period, block-of-one-period variance. The e-process (monitor) is run on the same paths.
POW_REPS = 10000
power = {}
for b in (0.5, 0.2):
    for delta in (0.005, 0.01, 0.02, 0.03):
        for kk in (120, 300, 600):
            r = np.random.default_rng(1000 + int(b * 10) * 100 + int(delta * 1000) * 10 + kk // 100)
            p = b + math.sqrt(delta) * r.choice([-1., 1.], size=(POW_REPS, kk))
            yy = (r.random(p.shape) < p).astype(float)
            xs = (b - yy) ** 2 - (p - yy) ** 2
            fh = int(block_t_rejects(xs, PER_PERIOD).sum())
            ep = int((grapa_paths(xs)[1] >= THRESHOLD).sum())
            power[f'b={b},delta={delta},clusters={kk}'] = {'fixed_horizon_block1_power': round(fh / POW_REPS, 4),
                                                           'eprocess_monitor_crossing_rate': round(ep / POW_REPS, 4)}
out['RC61_power_independent_clusters'] = power
# Under independent period shocks (F-22 family, b = 0.5 structure of Appendix D): q_t = 0.5 + 2.5 delta +/- 0.3.
power_shock = {}
for amp in (0.0, 0.3):
    for delta in (0.01, 0.02, 0.03):
        for kk in (120, 300, 600):
            r = np.random.default_rng(7000 + int(delta * 1000) * 10 + kk // 100 + int(amp * 10) * 1000)
            periods = kk // PER_PERIOD
            sh = r.choice([-amp, amp], size=(POW_REPS, periods))
            q = np.repeat(0.5 + 2.5 * delta + sh, PER_PERIOD, axis=1)
            xs = increments(q, r)
            fh = int(block_t_rejects(xs, PER_PERIOD).sum())
            ep = int((grapa_paths(xs)[1] >= THRESHOLD).sum())
            power_shock[f'shock=+/-{amp},delta={delta},clusters={kk}'] = {
                'fixed_horizon_block1_power': round(fh / POW_REPS, 4), 'eprocess_monitor_crossing_rate': round(ep / POW_REPS, 4)}
out['RC61_power_macro_shock_iid_periods'] = {'generator': 'baseline 0.4, challenger 0.6, q_t = 0.5 + 2.5 delta +/- shock per period (E[X] = delta, X in {-0.2, +0.2})',
                                              'cells': power_shock}
out['RC61_persistent_regime'] = 'size not held at 120 clusters over 24 periods (16 Appendix D), so no power figure is meaningful there'

# ================= r4296649427 (RC-63): positive-control oracles for each kernel =================
# (a) deterministic e-value oracle: constant increments +0.2 under the archived rule.
# lambda = 0 for n < 2; for constant X the sample variance is 0, so lambda = (1/mean) * n/(n+10) clipped
# to 0.5, i.e. 0.5 from n = 2 on; wealth after k increments = 1.1^(k-2).
const = np.full((1, 40), 0.2)
w_const, peak_const, snaps = grapa_paths(const, checkpoints=tuple(range(1, 41)))
first_cross = min(k for k, pk in snaps.items() if pk[0] >= THRESHOLD)
oracle_e = {'constant_+0.2_after_12': round(float(grapa_paths(const[:, :12])[0][0]), 6),
            'closed_form_1.1^10': round(1.1 ** 10, 6),
            'first_crossing_step': first_cross, 'closed_form_e_at_step_34': round(1.1 ** 32, 6)}
mixed = np.array([[0.2, -0.2, 0.2, 0.2, -0.2, 0.2, 0.2, 0.2, -0.2, 0.2, 0.2, 0.2]])
oracle_e['mixed_12_vector'] = mixed[0].tolist()
oracle_e['mixed_12_e_value'] = round(float(grapa_paths(mixed)[0][0]), 6)
# (b) deterministic fixed-horizon oracle: four block means.
bm = np.array([[0.05, 0.10, 0.00, 0.05]])
tstat = float(bm.mean() / (bm.std(ddof=1) / 2))
oracle_fh = {'block_means': bm[0].tolist(), 't_statistic': round(tstat, 6), 'df': 3,
             'one_sided_p': round(float(student_t.sf(tstat, 3)), 6), 'rejects_at_0.05': bool(tstat > student_t.ppf(0.95, 3))}
# (c) pre-specified alternative with a bounded minimum rejection rate for each kernel.
pc = {}
for delta in (0.03, 0.05, 0.08):
    r = np.random.default_rng(9000 + int(delta * 100))
    p = 0.5 + math.sqrt(delta) * r.choice([-1., 1.], size=(20000, 120))
    yy = (r.random(p.shape) < p).astype(float)
    xs = (0.5 - yy) ** 2 - (p - yy) ** 2
    fh = int(block_t_rejects(xs, PER_PERIOD).sum()); ep = int((grapa_paths(xs)[1] >= THRESHOLD).sum())
    pc[f'b=0.5,delta={delta},clusters=120'] = {
        'fixed_horizon_rejections': fh, 'fixed_horizon_rate': round(fh / 20000, 4),
        'fixed_horizon_exact_lower_99': round(binom_lower(fh, 20000, 0.99), 4),
        'eprocess_crossings': ep, 'eprocess_rate': round(ep / 20000, 4),
        'eprocess_exact_lower_99': round(binom_lower(ep, 20000, 0.99), 4)}
# Pass probability of a correct kernel against a lower bound of 0.90 when its true power is 0.95 or 0.97.
k_min = min(k for k in range(20000) if binom_lower(k, 20000, 0.99) >= 0.90)
pc['fixed_horizon_bound_0.90_design'] = {'k_min_rejections_of_20000': k_min,
                           'P_pass_if_power_0.93': round(float(binom.sf(k_min - 1, 20000, 0.93)), 6),
                           'P_pass_if_power_0.95': round(float(binom.sf(k_min - 1, 20000, 0.95)), 6),
                           'P_pass_if_power_0.964_(delta_0.08)': round(float(binom.sf(k_min - 1, 20000, 0.964)), 6),
                           'P_pass_if_inert_kernel': 0.0}
k_min_e = min(k for k in range(20000) if binom_lower(k, 20000, 0.99) >= 0.60)
pc['eprocess_bound_0.60_design'] = {'k_min_crossings_of_20000': k_min_e,
                           'P_pass_if_rate_0.65': round(float(binom.sf(k_min_e - 1, 20000, 0.65)), 6),
                           'P_pass_if_rate_0.71_(delta_0.08)': round(float(binom.sf(k_min_e - 1, 20000, 0.71)), 6),
                           'P_pass_if_inert_kernel': 0.0}
out['RC63_positive_controls'] = {'eprocess_oracle': oracle_e, 'fixed_horizon_oracle': oracle_fh, 'alternative_grid': pc}

# ================= r4296649421 (RC-62): a verifier that signs a subset of the capability tuple =================
FIELDS = ('capability', 'environment', 'release_digest', 'evidence_digest', 'epoch', 'nonce', 'expiry')
cap = {'capability': 'GATE_PROMOTE_SIM', 'environment': 'SIM', 'release_digest': 'r' * 8, 'evidence_digest': 'e' * 8,
       'epoch': 7, 'nonce': 'n1', 'expiry': 1000}
key = b'synthetic-test-key-not-a-secret'
def sign(record, signed_fields):
    msg = json.dumps({f: record[f] for f in signed_fields}, sort_keys=True).encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()
def mutate(record, f):
    r = dict(record); r[f] = (r[f] + 1) if isinstance(r[f], int) else r[f] + 'x'; return r
subset = ('environment', 'release_digest')                     # what T-31 v3 exercised besides the key
sig_subset = sign(cap, subset); sig_full = sign(cap, FIELDS)
out['RC62_partial_signature'] = {
    'verifier_signing_only_environment_and_release': {f: sign(mutate(cap, f), subset) == sig_subset for f in FIELDS},
    'verifier_signing_every_field': {f: sign(mutate(cap, f), FIELDS) == sig_full for f in FIELDS},
    'reading': 'True = the mutated record still verifies; T-31 v3 mutated only key, environment and release digest'}

# ================= r4296649399 (RC-60): the redacting holder still stores the raw secret =================
def canary(): return 'SYNTHETIC-' + 'CANARY-r4'
class Transport(Exception):
    def __init__(self, request): super().__init__('transport'); self.request = request
class Sanitized(RuntimeError): pass
class Redacted:
    def __init__(self, value): self._value = value
    def __repr__(self): return 'Redacted(***)'
def reachable_repr(exc):                                            # the round-3 probe (repr only)
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
def leaks_repr(exc): return any(canary() in repr(o) for o in reachable_repr(exc))
def leaks_state(exc):
    """Traverse object state (attributes, slots, containers, closures, exception args), not repr."""
    seen, stack = set(), list(reachable_repr(exc))
    while stack:
        o = stack.pop()
        if id(o) in seen: continue
        seen.add(id(o))
        if isinstance(o, (str, bytes)):
            if canary() in (o if isinstance(o, str) else o.decode('utf-8', 'ignore')): return True
            continue
        if isinstance(o, dict): stack += list(o.keys()) + list(o.values()); continue
        if isinstance(o, (list, tuple, set, frozenset)): stack += list(o); continue
        if isinstance(o, BaseException): stack += list(o.args)
        d = getattr(o, '__dict__', None)
        if isinstance(d, dict): stack += list(d.values())
        for slot in getattr(type(o), '__slots__', ()):
            if hasattr(o, slot): stack.append(getattr(o, slot))
        if isinstance(o, types.FunctionType):
            for cell in (o.__closure__ or ()):
                try: stack.append(cell.cell_contents)
                except ValueError: pass
    return False
def case_outside_redacted():                                        # round-3 "passing" variant
    auth = Redacted(f'Bearer {canary()}'); kind = None
    try: raise Transport({'Authorization': auth})
    except Transport as ex: kind = type(ex).__name__
    raise Sanitized(f'transport error: {kind}')
def _transport_call(request):
    """Holds the secret; catches every exception; returns only a typed outcome; its frame is gone before any raise."""
    headers = {**request, 'Authorization': f'Bearer {canary()}'}
    try:
        raise Transport(headers)
    except Transport as ex:
        return type(ex).__name__
    return None
def case_secret_confined_to_returned_frame():
    kind = _transport_call({'path': '/sim/precheck'})
    if kind is not None:
        raise Sanitized(f'transport error: {kind}')
def case_confined_but_outcome_carries_exception():                  # wrong: the outcome object references the frame
    def inner():
        headers = {'Authorization': f'Bearer {canary()}'}
        try: raise Transport(headers)
        except Transport as ex: return ex
    ex = inner()
    raise Sanitized(f'transport error: {type(ex).__name__}')
table = {}
for name, fn in [('outside_handler_redacting_holder_(v3_pass)', case_outside_redacted),
                 ('secret_confined_to_frame_that_returned', case_secret_confined_to_returned_frame),
                 ('confined_but_outcome_is_the_exception_object', case_confined_but_outcome_carries_exception)]:
    try: fn()
    except Sanitized as s_:
        table[name] = {'context_is_None': s_.__context__ is None, 'repr_probe_leaks': leaks_repr(s_), 'state_probe_leaks': leaks_state(s_)}
out['RC60_object_state_canary'] = table
out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
