"""Round-6 checks for the Codex findings on PR #4 at 4de18e5 (no reference code, no network).

Evidence only: the findings are recorded, not applied (16 section 4.6, OD10). The D1 generator, the archived
GRAPA rule and the block t test are those of 16 Appendix A, D and E.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA, LAM_MAX = 0.05, 0.5

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))

def grapa_paths(xs, lam_max=LAM_MAX):
    """Archived GRAPA rule (16 Appendix A): predictable lambda, wealth and running maximum."""
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

# ================= r4297109177 (RC-72): one-sided t test over 24 two-point block means =================
# Every cluster in a calendar block shares one outcome Y; baseline 0.9518, FULL 0.0518.
# X = (b - Y)^2 - (p - Y)^2 = +0.90324 if Y = 0 (probability 0.4982), -0.89676 if Y = 1 (0.5018).
def two_point_values(b, p):
    return (b - 0) ** 2 - (p - 0) ** 2, (b - 1) ** 2 - (p - 1) ** 2   # X(Y=0), X(Y=1)

def t_size_two_point(a, c, q0, g, alpha=ALPHA):
    """Exact size of the one-sided t test over g iid block means taking value a (prob q0) or c (prob 1 - q0).
    With two-point values the statistic depends only on the count k of a-valued blocks (closed form)."""
    crit = float(student_t.ppf(1 - alpha, g - 1))
    k = np.arange(g + 1)
    m = (k * a + (g - k) * c) / g
    var = (k * (a - m) ** 2 + (g - k) * (c - m) ** 2) / (g - 1)
    # A sample with every block equal has no sample variance; the statistic is undefined and is counted as
    # no rejection here (an implementation that maps a zero denominator to +inf would add P(all blocks equal)).
    var = np.where(var < 1e-12, 0.0, var)
    with np.errstate(divide='ignore', invalid='ignore'):
        tk = np.where(var > 0, m / np.sqrt(var / g), -np.inf)
    rej = tk > crit
    size = float(binom.pmf(k[rej], g, q0).sum())
    kmin = int(k[rej].min()) if rej.any() else None
    return size, kmin, crit

a, c = two_point_values(0.9518, 0.0518)
q0 = 0.4982
mean_null = q0 * a + (1 - q0) * c
size24, kmin24, crit24 = t_size_two_point(a, c, q0, 24)
rc72 = {'codex_null': {'X_if_Y0': round(a, 5), 'X_if_Y1': round(c, 5), 'P_Y0': q0, 'mean': round(mean_null, 6),
                       'G': 24, 't_crit_23df': round(crit24, 4), 'min_positive_blocks_to_reject': kmin24,
                       'exact_size': round(size24, 5), 'exceeds_A3_ceiling_0.06': bool(size24 > 0.06)}}
# The same count under a symmetric two-point null (+/- 0.9, P = 0.5): where does the threshold fall?
size_sym, kmin_sym, _ = t_size_two_point(0.9, -0.9, 0.5, 24)
rc72['symmetric_two_point_null_G24'] = {'exact_size': round(size_sym, 5), 'min_positive_blocks_to_reject': kmin_sym}
# Maximum exact size over zero-mean two-point nulls (a in (0, 1], c = -a q0 / (1 - q0) >= -1) as G grows.
grid = {}
for g in (24, 36, 48, 72, 96, 120, 240):
    worst = (0.0, None)
    for a_ in np.linspace(0.02, 1.0, 50):
        for q in np.linspace(0.02, 0.98, 97):
            c_ = -a_ * q / (1 - q)
            if c_ < -1:
                continue
            s, _, _ = t_size_two_point(a_, c_, q, g)
            if s > worst[0]:
                worst = (s, {'a': round(float(a_), 3), 'c': round(float(c_), 4), 'P_a': round(float(q), 3),
                             'P_all_blocks_equal': round(float(q) ** g, 4)})
    grid[f'G={g}'] = {'max_exact_size': round(worst[0], 4), 'at': worst[1]}
rc72['max_size_of_t_over_two_point_zero_mean_nulls'] = grid
# Deterministic ceiling of the bounded betting test at G = 24: lambda = 0 for the first two blocks, then at most
# 0.5; with every block mean at +x the final wealth is (1 + 0.5 x)^22, which must reach 1/alpha = 20 to reject.
rc72['betting_test_wealth_ceiling_G24'] = {f'all_block_means_{x}': round((1 + 0.5 * x) ** 22, 3) for x in (0.02, 0.05, 0.1, 0.2, 0.3)}
rc72['betting_test_smallest_constant_block_mean_reaching_20_at_G24'] = round(2 * (20 ** (1 / 22) - 1), 4)

# A finite-sample-valid alternative on the same block means: the archived GRAPA betting test run over the G
# block means (bounded in [-1, 1]), evaluated at the fixed horizon G, reject iff final wealth >= 1/alpha.
# Ville's inequality makes it valid for every bounded null with E[X_g | past] <= 0, at any G.
rng = np.random.default_rng(61)
R = 20000
ys = (rng.random((R, 24)) < (1 - q0)).astype(float)       # Y = 1 with probability 0.5018
xs_null = np.where(ys == 0, a, c)
wealth, peak = grapa_paths(xs_null)
k_bet = int((wealth >= 1 / ALPHA).sum()); k_bet_peak = int((peak >= 1 / ALPHA).sum())
# t test on the same paths (Monte Carlo check of the exact value above)
tb = xs_null.mean(axis=1) / (xs_null.std(axis=1, ddof=1) / math.sqrt(24))
k_t = int((tb > crit24).sum())
rc72['monte_carlo_on_codex_null_20000'] = {
    't_test_rejections': k_t, 't_test_rate': round(k_t / R, 4), 't_test_99pct_upper': round(binom_upper(k_t, R, 0.99), 4),
    'betting_test_final_wealth_rejections': k_bet, 'betting_rate': round(k_bet / R, 4),
    'betting_99pct_upper': round(binom_upper(k_bet, R, 0.99), 4),
    'betting_running_max_rejections': k_bet_peak, 'betting_running_max_rate': round(k_bet_peak / R, 4)}

# Power cost of the valid alternative under the Appendix E/F alternative with 24 periods:
# D1 generator, b = 0.5, independent clusters, n_per clusters per period, block = one period.
def d1_increments(b, delta, n_cl, rng_):
    p = b + math.sqrt(delta)
    y = (rng_.random(n_cl) < p).astype(float)
    return (b - y) ** 2 - (p - y) ** 2
power = {}
for delta in (0.02, 0.05, 0.08):
    for per in (25, 50):
        rej_t = 0; rej_bet = 0
        bm = np.empty((R, 24))
        for r in range(R):
            x = d1_increments(0.5, delta, 24 * per, rng).reshape(24, per).mean(axis=1)
            bm[r] = x
        tb = bm.mean(axis=1) / (bm.std(axis=1, ddof=1) / math.sqrt(24))
        rej_t = int((tb > crit24).sum())
        w, _ = grapa_paths(bm)
        rej_bet = int((w >= 1 / ALPHA).sum())
        power[f'delta={delta}_clusters_per_period={per}'] = {'t_power': round(rej_t / R, 3), 'betting_power': round(rej_bet / R, 3)}
rc72['power_at_24_periods_b0.5_independent_clusters'] = power
out['RC72_t_test_on_two_point_block_means'] = rc72

# ================= r4297109194 (RC-73): clock rollback across an idle expiry window =================
# Toy state machine. Variant A: v4 wording (watermark advanced by admissions). Variant B: RC-65 wording
# (watermark advanced by every check). Variant C: the check also persists the monotonic clock and the boot id
# with the wall clock; a wall-minus-monotonic drift beyond the tolerance, or a new boot id, is an unverifiable
# discontinuity that invalidates every outstanding capability until re-authorisation.
def run_idle_variant(variant):
    state = {'watermark': 0.0, 'mono_ref': None, 'wall_ref': None, 'boot': None, 'reauth_needed': False}
    log = []
    def check(wall, mono, boot, expiry):
        if variant == 'C':
            if state['boot'] is not None and (boot != state['boot'] or abs((wall - mono) - (state['wall_ref'] - state['mono_ref'])) > 1.0):
                state['reauth_needed'] = True
            state['wall_ref'], state['mono_ref'], state['boot'] = wall, mono, boot
            if state['reauth_needed']:
                verdict = 'rejected_clock_discontinuity_reauthorise'
                log.append((wall, mono, verdict)); return verdict
        if wall < state['watermark']:
            verdict = 'rejected_rollback'
        elif wall >= expiry:
            verdict = 'rejected_expired'
        else:
            verdict = 'admitted'
        if verdict == 'admitted' or variant in ('B', 'C'):
            state['watermark'] = max(state['watermark'], wall)
        log.append((wall, mono, verdict)); return verdict
    check(10, 100, 'boot-1', 100)        # last observed time t0 = 10 (an unrelated admission)
    # capability expires at t1 = 20; machine idle until real time 30; no check occurs in between
    replay = check(15, 120, 'boot-1', 20)  # wall clock rolled back to 15 (monotonic clock has advanced 20)
    restart = check(15, 3, 'boot-2', 20)   # same, after a reboot (monotonic clock reset, new boot id)
    return replay, restart, log
rc73 = {}
for v, name in (('A', 'A_v4_watermark_on_admission'), ('B', 'B_RC65_watermark_on_every_check'), ('C', 'C_monotonic_clock_and_boot_id')):
    replay, restart, log = run_idle_variant(v)
    rc73[name] = {'replay_after_idle_rollback': replay, 'replay_after_reboot': restart,
                  'log': [f'wall={w} mono={m} {vd}' for w, m, vd in log]}
out['RC73_idle_expiry_window_rollback'] = rc73

# ================= r4297109203 (RC-74): nonce consumed after the last anchor, then restored away =================
# Toy ledger: records carry consumed nonces; an anchor covers a prefix; restore truncates the local ledger to the
# anchored prefix. Variant A (v4): acknowledge inside the writer transaction, anchor asynchronously.
# Variant B: acknowledge only after the record is in an externally anchored prefix. Variant C: the epoch is
# rotated and anchored synchronously on every process start; capabilities carry the epoch.
class Ledger:
    def __init__(self):
        self.records = []; self.anchored_len = 0; self.external_anchor_digest = None; self.epoch = 1
    def anchor(self):
        self.anchored_len = len(self.records); self.external_anchor_digest = ('anchor', tuple(self.records))
    def restore_to_anchor(self):
        self.records = list(self.external_anchor_digest[1]); self.anchored_len = len(self.records)
        self.epoch = max([r[2] for r in self.records if r[0] == 'epoch'] + [1])

def protected_action(ledger, nonce, cap_epoch, variant):
    if cap_epoch != ledger.epoch:
        return 'rejected_stale_epoch'
    if any(r[0] == 'nonce' and r[1] == nonce for r in ledger.records):
        return 'rejected_nonce_consumed'
    ledger.records.append(('nonce', nonce, cap_epoch))
    if variant == 'B':
        ledger.anchor()                       # durable externally before the acknowledgement
    return 'acknowledged'

def run_restore_variant(variant):
    led = Ledger(); log = []
    if variant == 'C':
        led.epoch += 1; led.records.append(('epoch', 'start-1', led.epoch)); led.anchor()
    led.records.append(('event', 'e1', led.epoch)); led.anchor()           # last asynchronous anchor
    cap = ('nonce-7', led.epoch)                                            # capability signed for this epoch
    log.append(('first presentation', protected_action(led, cap[0], cap[1], variant)))
    led.restore_to_anchor()                                                 # SQLite and JSONL suffix restored to the anchor
    if variant == 'C':
        led.epoch += 1; led.records.append(('epoch', 'start-2', led.epoch)); led.anchor()   # process restarts after the restore
    log.append(('replay after restore', protected_action(led, cap[0], cap[1], variant)))
    return log
rc74 = {name: dict(run_restore_variant(v)) for v, name in (('A', 'A_v4_ack_in_transaction_async_anchor'),
                                                            ('B', 'B_ack_after_external_anchor'),
                                                            ('C', 'C_epoch_rotated_and_anchored_on_start'))}
out['RC74_unanchored_nonce_restored_away'] = rc74

# ================= r4297109207 (RC-75): two eligible revisions, one scored after the outcome =================
# Event with true P(Y = 1) = q; two eligible FULL forecasts 0.3 and 0.7 (different ids, both before t*_k).
# Baseline forecasts q itself. Expected paired increment when the scored revision is the one nearest Y.
rc75 = {}
for q in (0.5, 0.3):
    exp_honest = {}
    for p in (0.3, 0.7):
        exp_honest[f'p={p}'] = round(q * ((q - 1) ** 2 - (p - 1) ** 2) + (1 - q) * (q ** 2 - p ** 2), 4)
    nearest = q * ((q - 1) ** 2 - (0.7 - 1) ** 2) + (1 - q) * (q ** 2 - 0.3 ** 2)
    rc75[f'q={q}'] = {'expected_increment_scoring_each_revision_honestly': exp_honest,
                      'expected_increment_scoring_the_revision_nearest_Y': round(nearest, 4)}
out['RC75_revision_selected_after_outcome'] = rc75

# ================= r4297109220 (RC-77): NO by logical finality before the source's formal record =================
# Eventually-by-deadline event, deadline D = 100, declared latency window L = 10, no timely occurrence.
# The source's formal 'did not occur' record is received at 118. A forecast is received at 113.
D, L, receipt, forecast_receipt = 100, 10, 118, 113
knowable_v4 = receipt                     # v4: knowable_at = publication (the formal record) or occurrence
knowable_proposed = min(receipt, D + L)   # proposed: logical finality at D + L
out['RC77_logical_finality'] = {'deadline': D, 'latency_window': L, 'formal_record_received': receipt,
                                'forecast_received': forecast_receipt,
                                'v4_knowable_at': knowable_v4, 'v4_forecast_eligible': forecast_receipt < knowable_v4,
                                'proposed_knowable_at': knowable_proposed, 'proposed_forecast_eligible': forecast_receipt < knowable_proposed}

out['environment'] = {'python': sys.version.split()[0], 'numpy': np.__version__, 'scipy': __import__('scipy').__version__}
print(json.dumps(out, indent=2))
