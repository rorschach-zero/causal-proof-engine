"""Round-5 checks for the Codex findings on PR #4 at 88abaa4 (no reference code, no network).

Evidence only: the findings are recorded, not applied (16 section 4.6, OD10). Generators and the
block-of-one-period t test are those of 16 Appendix D and E.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
ALPHA, THRESHOLD, LAM_MAX = 0.05, 20.0, 0.5

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

def block_t(xs, per_period, block_periods=1):
    """Appendix D/E statistic: one-sided t over equal-sized calendar-block MEANS."""
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

def increments(q, rng_):
    y = (rng_.random(q.shape) < q).astype(float)
    return 0.4 * y - 0.2

# ================= r4296914298 (RC-65): watermark advanced only by admissions =================
# Toy state machine. A capability is valid iff now < expiry and now >= watermark (fail closed on rollback).
# Variant A persists the watermark only when a check is admitted; variant B persists max(now) on every
# clock-dependent check, admitted or rejected. Codex's replay: last admission at t0 = 10, capability expires
# at t1 = 20, presented at t2 = 30 (rejected: expired), clock rolled back to t = 15, presented again.
def run_clock_variant(advance_on_reject):
    watermark = 0.0; log = []
    def check(now, expiry):
        nonlocal watermark
        if now < watermark:
            verdict = 'rejected_rollback'
        elif now >= expiry:
            verdict = 'rejected_expired'
        else:
            verdict = 'admitted'
        if verdict == 'admitted' or advance_on_reject:
            watermark = max(watermark, now)
        log.append((now, expiry, verdict, watermark))
        return verdict
    check(10, 100)            # an unrelated admission at t0 = 10
    check(30, 20)             # the expired capability presented at t2 = 30
    replay = check(15, 20)    # clock rolled back to t = 15 < t1 = 20, same capability
    return replay, log
clock = {}
for name, flag in (('A_watermark_on_admission_only_(v4_text)', False), ('B_watermark_on_every_check', True)):
    verdict, log = run_clock_variant(flag)
    clock[name] = {'replay_after_rollback': verdict, 'log': [f'now={n} expiry={e} {v} watermark={w}' for n, e, v, w in log]}
out['RC65_clock_watermark_replay'] = clock

# ================= r4296914341 (RC-69): equal block means versus the per-cluster estimand =================
# Deterministic oracle 1: two calendar blocks of sizes 1 and 9.
blocks = [np.array([0.5]), np.full(9, -0.1)]
allx = np.concatenate(blocks)
equal_block_mean_estimate = float(np.mean([b.mean() for b in blocks]))
cluster_weighted_estimate = float(allx.mean())
def cluster_weighted_t(blocks):
    """theta = mean over clusters; variance = sum over blocks of (sum within block of (X - theta))^2 / N^2,
    with the G/(G-1) small-sample factor; G-1 degrees of freedom (block-sum / cluster-robust form)."""
    allx = np.concatenate(blocks); n = len(allx); g = len(blocks)
    theta = allx.mean()
    v = sum(((b - theta).sum()) ** 2 for b in blocks) / n ** 2 * g / (g - 1)
    return float(theta), float(theta / math.sqrt(v)) if v > 0 else float('inf'), g - 1
rc69 = {'oracle_1_block_sizes_1_and_9': {'values': 'block 1: one cluster at +0.5; block 2: nine clusters at -0.1',
                                         'equal_block_mean_estimate': round(equal_block_mean_estimate, 6),
                                         'cluster_weighted_estimate': round(cluster_weighted_estimate, 6),
                                         'sign_reversed': (equal_block_mean_estimate > 0) != (cluster_weighted_estimate > 0)}}
# Deterministic oracle 2: four unequal blocks, for T-36 (b).
blocks2 = [np.array([0.10, 0.00]), np.array([0.05, 0.15, 0.10]), np.array([0.00, 0.05, 0.05, 0.10]), np.array([0.20])]
theta2, t2, df2 = cluster_weighted_t(blocks2)
bm2 = [float(b.mean()) for b in blocks2]
t_equal2 = float(np.mean(bm2) / (np.std(bm2, ddof=1) / math.sqrt(4)))
rc69['oracle_2_block_sizes_2_3_4_1'] = {'blocks': [list(map(float, b)) for b in blocks2],
                                       'cluster_weighted_estimate': round(theta2, 6), 'cluster_weighted_t': round(t2, 6), 'df': df2,
                                       'one_sided_p': round(float(1 - student_t.cdf(t2, df2)), 6),
                                       'equal_block_mean_estimate': round(float(np.mean(bm2)), 6), 'equal_block_mean_t': round(t_equal2, 6)}
# Simulation: unequal supply per period. (i) supply independent of the period shock (Poisson mean 5, at least 1)
# under the valid null and under independent period shocks of +/- 0.3: both statistics should hold size.
# (ii) supply covarying with the shock (8 clusters in a +0.3 period, 2 in a -0.3 period): the per-cluster
# estimand of 17 section 6 is then E[X] = (8*0.12 - 2*0.12)/10 = +0.072 > 0 while the period-average is 0,
# so the two statistics test different hypotheses; reported, not bounded.
REPS, PERIODS = 20000, 24
rng = np.random.default_rng(5026)
def sim_unequal(rng_, shock_amp, covary, delta=0.0):
    rej_equal = np.zeros(REPS, bool); rej_cw = np.zeros(REPS, bool); est_cw = np.zeros(REPS); est_eq = np.zeros(REPS)
    for rpt in range(REPS):
        sh = rng_.choice([-shock_amp, shock_amp], size=PERIODS) if shock_amp > 0 else np.zeros(PERIODS)
        if covary:
            sizes = np.where(sh > 0, 8, 2)
        else:
            sizes = np.maximum(1, rng_.poisson(5, size=PERIODS))
        blocks = []
        for tt in range(PERIODS):
            q = 0.5 + 2.5 * delta + sh[tt]
            blocks.append(increments(np.full(sizes[tt], q), rng_))
        bm = np.array([b.mean() for b in blocks])
        t_eq = bm.mean() / (bm.std(ddof=1) / math.sqrt(PERIODS))
        theta, t_cw, df = cluster_weighted_t(blocks)
        crit = student_t.ppf(1 - ALPHA, PERIODS - 1)
        rej_equal[rpt] = t_eq > crit; rej_cw[rpt] = t_cw > crit; est_cw[rpt] = theta; est_eq[rpt] = bm.mean()
    return {'equal_block_mean_t_reject': round(float(rej_equal.mean()), 5),
            'cluster_weighted_block_sum_t_reject': round(float(rej_cw.mean()), 5),
            'exact_upper_99_equal': round(binom_upper(int(rej_equal.sum()), REPS, 0.99), 5),
            'exact_upper_99_cluster_weighted': round(binom_upper(int(rej_cw.sum()), REPS, 0.99), 5),
            'mean_estimate_equal_block': round(float(est_eq.mean()), 5), 'mean_estimate_cluster_weighted': round(float(est_cw.mean()), 5)}
rc69['size_poisson_supply_valid_null'] = sim_unequal(rng, 0.0, False)
rc69['size_poisson_supply_iid_period_shocks'] = sim_unequal(rng, 0.3, False)
rc69['supply_covarying_with_shock_(estimands_differ)'] = sim_unequal(rng, 0.3, True)
out['RC69_unequal_blocks'] = rc69

# ================= r4296914351 (RC-70): power at exactly 24 calendar periods =================
# Appendix E used five clusters per period, so 600 clusters spanned 120 periods. Here PERIODS = 24 and the
# cluster count sets the clusters per period. Independent clusters (D1 generator) first.
POW_REPS = 10000
def d1_paths(b, delta, kk, r):
    p = b + math.sqrt(delta) * r.choice([-1., 1.], size=(POW_REPS, kk))
    yy = (r.random(p.shape) < p).astype(float)
    return (b - yy) ** 2 - (p - yy) ** 2
power24 = {}
for b in (0.5, 0.2):
    for delta in (0.005, 0.01, 0.02):
        for per_period in (5, 12, 25):
            kk = PERIODS * per_period
            r = np.random.default_rng(2400 + int(b * 10) * 100 + int(delta * 1000) * 10 + per_period)
            xs = d1_paths(b, delta, kk, r)
            fh = int(block_t_rejects(xs, per_period).sum())
            ep = int((grapa_paths(xs)[1] >= THRESHOLD).sum())
            power24[f'b={b},delta={delta},clusters={kk}(24x{per_period})'] = {
                'fixed_horizon_block1_power_24_periods': round(fh / POW_REPS, 4), 'eprocess_monitor_crossing_rate': round(ep / POW_REPS, 4)}
out['RC70_power_independent_clusters_24_periods'] = power24
# Independent period shocks of +/- 0.3 over exactly 24 periods (Appendix D/E generator, X in {-0.2, +0.2}).
shock24 = {}
for amp in (0.0, 0.3):
    for delta in (0.0, 0.01, 0.02, 0.03, 0.05, 0.08):
        for per_period in (5, 12, 25, 50):
            kk = PERIODS * per_period
            r = np.random.default_rng(7400 + int(delta * 1000) * 10 + per_period + int(amp * 10) * 1000)
            sh = r.choice([-amp, amp], size=(POW_REPS, PERIODS))
            q = np.repeat(0.5 + 2.5 * delta + sh, per_period, axis=1)
            xs = increments(q, r)
            fh = int(block_t_rejects(xs, per_period).sum())
            shock24[f'shock=+/-{amp},delta={delta},clusters={kk}(24x{per_period})'] = round(fh / POW_REPS, 4)
out['RC70_power_macro_shock_24_periods'] = {
    'generator': 'baseline 0.4, challenger 0.6, q_t = 0.5 + 2.5 delta +/- shock per period, 24 periods; block-of-one-period t, 23 df',
    'appendix_E_comparison': 'Appendix E shock=0.3, delta=0.02, 600 clusters over 120 periods: 0.47',
    'cells': shock24}
# Normal-theory check of the plateau: block means have sd sqrt(0.12^2 + 0.04/n) over 24 blocks; the
# detectable delta at 80 % power with 24 blocks is about (1.714 + 0.856) * se, se = sd / sqrt(24).
plateau = {}
for per_period in (5, 25, 50, 1000):
    sd = math.sqrt(0.12 ** 2 + 0.04 / per_period)
    se = sd / math.sqrt(PERIODS)
    plateau[f'24x{per_period}'] = {'block_mean_sd': round(sd, 5), 'se_of_mean': round(se, 5),
                                   'delta_at_80pct_power_normal_theory': round((student_t.ppf(0.95, 23) + student_t.ppf(0.80, 23)) * se, 4)}
out['RC70_detectable_delta_plateau_normal_theory'] = plateau

out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
