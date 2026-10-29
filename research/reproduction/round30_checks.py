"""Round-30 checks for the Codex findings on PR #4 at ba11fe8 (no reference code, no network).

Codex review 5563100293 of ba11fe8, three inline findings: 4307124385 (RC-207, an audited omission outside the
monitor's record order), 4307124387 (RC-208, a sampling beacon that misses T_D), 4307124393 (RC-209, the GRAPA
lambda channel of a late registration).

Monitor setting of RC-205 (Appendix AC): pairs (B_i, A_i), B_i before A_i in record order, a YES of A_i publicly
knowable before B_i's batch is anchored; running maximum against 1/alpha = 20. Primary setting of RC-187 (Appendix
Y): equal-probability inclusion at pi = 0.5, one-sided test of the included mean at 1.645 and at c* = 2.254.
"""
import json
import math
import numpy as np

out = {}
ALPHA, THRESH, LAM_MAX = 0.05, 20.0, 0.5
GRID = np.arange(1, 11) * 0.05          # the proposed fixed-lambda mixture: 0.05, ..., 0.50, equal weights


def grapa_lambda(s1, s2, n):
    """Archived GRAPA bet after n increments with sums s1, s2 (16 Appendix A and D)."""
    if n < 2:
        return 0.0
    mean = s1 / n
    var = max(0.0, (s2 - s1 * s1 / n) / (n - 1))
    den = var + mean * mean
    lam = mean / den * n / (n + 10) if den > 0 else 0.0
    return min(max(lam, 0.0), LAM_MAX)


def grapa_peak(xs):
    """Vectorised archived GRAPA running maximum over the rows of xs."""
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); w = np.ones(n_paths); peak = np.ones(n_paths)
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.clip(np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10), 0.0, LAM_MAX)
        w = w * (1 + lam * xs[:, n]); peak = np.maximum(peak, w)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
    return peak


def mixture_peak(xs):
    """Running maximum of the equal-weight mixture over GRID of fixed-lambda products."""
    comp = np.ones((xs.shape[0], GRID.size)); peak = np.ones(xs.shape[0])
    for n in range(xs.shape[1]):
        comp = comp * (1 + GRID[None, :] * xs[:, n][:, None])
        peak = np.maximum(peak, comp.mean(axis=1))
    return peak


def rate(flags):
    return round(float(np.mean(flags)), 4)


# ================= 4307124385 (RC-207): an audited omission outside the monitor's record order =================
# 17 v26: the predecessor set is read from the anchored batches, and an omission is absent from its batch by
# definition, so its factor is missing from the running path until the audit, which may run just before T_D. Toy of
# Appendix AC with lambda = 0.5 fixed: the registrar leaves B_i out of the snapshot when A_i is a known YES (and the
# wealth is at least w_min). v26: the running maximum is read on the path without B_i, and B_i enters at the audit
# at the lower end of its box (1 - lambda), after every crossing. Remedy: a crossing stays provisional until the audit;
# at the audit the path is replayed with every drawn omission at its own record-order position at the lower end of its
# box, and every crossing whose prefix contains an omission's position is withdrawn, so a supported crossing lies on a
# prefix identical to the honest one. The replayed path (fixed lambda) is reported beside it.
rng = np.random.default_rng(3071)
P, LAM, HM = 60, 0.5, 20000
xb = rng.choice([-1.0, 1.0], (HM, P))
xa = rng.choice([-1.0, 1.0], (HM, P))
early = xa > 0


def omission_paths(w_min):
    provisional = replayed = honest = supported = 0
    for h in range(HM):
        w_live = m_live = w_rep = m_rep = w_hon = m_hon = 1.0
        clean = True
        for i in range(P):
            fa, fb = 1 + LAM * xa[h, i], 1 + LAM * xb[h, i]
            omitted = early[h, i] and w_live >= w_min
            if clean and omitted:
                clean = False
                supported += m_live >= THRESH
            w_hon *= fb; m_hon = max(m_hon, w_hon); w_hon *= fa; m_hon = max(m_hon, w_hon)
            if not omitted:
                w_live *= fb; m_live = max(m_live, w_live)
            w_live *= fa; m_live = max(m_live, w_live)
            w_rep *= (1 - LAM) if omitted else fb; m_rep = max(m_rep, w_rep)
            w_rep *= fa; m_rep = max(m_rep, w_rep)
        provisional += m_live >= THRESH
        replayed += m_rep >= THRESH
        honest += m_hon >= THRESH
        if clean:
            supported += m_live >= THRESH
    return {'honest': round(honest / HM, 4), 'v26_crossing_before_audit': round(provisional / HM, 4),
            'remedy_supported_crossing': round(supported / HM, 4), 'replayed_path_fixed_lambda': round(replayed / HM, 4)}


rc207 = {'pairs': P, 'lambda': LAM, 'paths': HM, 'threshold': THRESH}
for w_min in (0.0, 10.0):
    rc207[f'omit_B_when_A_known_yes_and_wealth_at_least={w_min}'] = omission_paths(w_min)
out['4307124385 RC-207'] = rc207

# ================= 4307124387 (RC-208): a sampling beacon that misses T_D =================
# Four batches of 50 eligible clusters, an exactly null eligible population: batches 1-3 at mean +d, batch 4 at -3d.
# If batch 4's beacon publishes no round by T_D and the decision is taken on batches 1-3 (the reading Codex
# describes), batch 4 has inclusion probability zero. Remedy: the primary is non-confirmatory (no claim) when any
# batch of the cohort has no verified beacon round by T_D, so its rejection rate on that event is zero.
rng = np.random.default_rng(3072)
REPS, NB, D, SIG, PI = 20000, 50, 0.005, 0.02, 0.5
means = np.concatenate([np.full(3 * NB, D), np.full(NB, -3 * D)])
x = means[None, :] + SIG * rng.standard_normal((REPS, 4 * NB))
inc = rng.random((REPS, 4 * NB)) < PI


def t_reject(mask, c):
    n = mask.sum(axis=1)
    s = np.where(mask, x, 0.0).sum(axis=1)
    ss = np.where(mask, x * x, 0.0).sum(axis=1)
    mean = s / n
    sd = np.sqrt(np.maximum(0.0, (ss - n * mean * mean) / (n - 1)))
    return mean / (sd / np.sqrt(n)) > c


drop4 = inc.copy(); drop4[:, 3 * NB:] = False
out['4307124387 RC-208'] = {
    'batches': 4, 'clusters_per_batch': NB, 'd': D, 'sigma': SIG, 'pi': PI, 'replications': REPS,
    'eligible_population_mean': float(means.mean()),
    'all_beacons_published': {'reject_at_1.645': rate(t_reject(inc, 1.645)), 'reject_at_2.254': rate(t_reject(inc, 2.254))},
    'batch_4_beacon_missing_decided_on_batches_1_to_3': {'reject_at_1.645': rate(t_reject(drop4, 1.645)),
                                                        'reject_at_2.254': rate(t_reject(drop4, 2.254))},
    'remedy_non_confirmatory_on_that_event': 0.0}

# ================= 4307124393 (RC-209): the GRAPA lambda channel of a late registration =================
# (a) Deterministic fixture: history of 10 increments, then B (honest X_B = +0.8) and A. Under the withholding
# strategy B is late iff A is a known YES, so B enters at the lower end of its box and lambda_A, computed by the
# archived rule from the record-order predecessors, takes a different value according to A's outcome.
hist = [0.8, -0.8, 0.8, 0.8, -0.8, 0.8, 0.8, -0.8, 0.8, 0.8]
LOWER_YES, LOWER_NO = -0.99, -0.19   # lower end of the box at p_baseline = 0.9 with FULL's slot free, Y = 1 and Y = 0


def lam_after(values):
    return round(grapa_lambda(sum(values), sum(v * v for v in values), len(values)), 6)


fixture = {'lambda_A_if_A_is_NO_B_on_schedule': lam_after(hist + [0.8]),
           'lambda_A_if_A_is_YES_B_withheld_lower_end_Y=0': lam_after(hist + [LOWER_NO]),
           'mixture_weights_and_grid_independent_of_history': [round(float(g), 2) for g in GRID]}
fixture['lambda_A_depends_on_A_outcome_under_v26'] = (fixture['lambda_A_if_A_is_NO_B_on_schedule']
                                                      != fixture['lambda_A_if_A_is_YES_B_withheld_lower_end_Y=0'])

# (b) Simulation, law c of Appendix P (p_baseline 0.9, p_FULL 0.1, Y ~ Bern(0.5), X = +0.8 at NO, -0.8 at YES):
# 300 pairs (B_i, A_i). A YES of A_i (a loss for FULL) is known before B_i's batch is anchored. Strategy: withhold
# B_i when A_i is a known YES, so B_i enters at its position at the lower end of its box (v26, RC-205), which lowers
# the GRAPA lambda applied to A_i. Variants: always, and only when the current lambda is zero (B_i's own factor is
# then 1 whatever its value, so the withholding costs nothing on B_i). Remedy: a crossing whose prefix contains a
# late-registration factor is withdrawn (a supported crossing lies on a prefix identical to the honest one). OD10
# alternative: a fixed-lambda mixture, which reads no history, so the same strategy only lowers its factors.
rng = np.random.default_rng(3073)
PAIRS, HM2 = 300, 4000
yb = rng.random((HM2, PAIRS)) < 0.5
ya = rng.random((HM2, PAIRS)) < 0.5
x_b = np.where(yb, -0.8, 0.8); x_a = np.where(ya, -0.8, 0.8)
low_b = np.where(yb, LOWER_YES, LOWER_NO)


def interleave(b, a):
    z = np.empty((b.shape[0], 2 * b.shape[1])); z[:, 0::2] = b; z[:, 1::2] = a
    return z


honest_x = interleave(x_b, x_a)


def grapa_strategy(only_when_lambda_zero):
    crossed = supported = 0
    for h in range(HM2):
        s1 = s2 = 0.0; n = 0; w = m = 1.0
        clean = True
        for i in range(PAIRS):
            lam = grapa_lambda(s1, s2, n)
            withhold = ya[h, i] and (lam == 0.0 or not only_when_lambda_zero)
            if clean and withhold:
                clean = False
                supported += m >= THRESH
            xb_used = low_b[h, i] if withhold else x_b[h, i]
            w *= 1 + lam * xb_used; m = max(m, w); s1 += xb_used; s2 += xb_used * xb_used; n += 1
            lam = grapa_lambda(s1, s2, n)
            w *= 1 + lam * x_a[h, i]; m = max(m, w); s1 += x_a[h, i]; s2 += x_a[h, i] ** 2; n += 1
        crossed += m >= THRESH
        if clean:
            supported += m >= THRESH
    return {'v26_crossing': round(crossed / HM2, 4), 'remedy_supported_crossing': round(supported / HM2, 4)}


withheld_all = interleave(np.where(ya, low_b, x_b), x_a)
out['4307124393 RC-209'] = {
    'fixture': fixture, 'pairs': PAIRS, 'paths': HM2, 'threshold': THRESH,
    'grapa': {'honest': rate(grapa_peak(honest_x) >= THRESH),
              'v26_withhold_B_when_A_known_yes': grapa_strategy(False),
              'v26_withhold_B_when_A_known_yes_and_lambda_zero': grapa_strategy(True)},
    'od10_alternative_mixture': {'honest': rate(mixture_peak(honest_x) >= THRESH),
                'withhold_B_when_A_known_yes': rate(mixture_peak(withheld_all) >= THRESH)},
    'mixture_pointwise_at_or_below_honest_every_step': bool(np.all(
        np.maximum.accumulate(np.cumprod(1 + GRID[None, None, :] * withheld_all[:200, :, None], axis=1).mean(axis=2), axis=1)
        <= np.maximum.accumulate(np.cumprod(1 + GRID[None, None, :] * honest_x[:200, :, None], axis=1).mean(axis=2), axis=1)
        + 1e-12))}

# ================= the OD10 alternative (fixed-lambda mixture) against T-36: oracles and power =================
# T-36 (a) oracles for the mixture and T-36 (c) alternative (b = 0.5, delta = 0.08, 120 clusters, D1 generator of 16
# Appendix A), where the archived GRAPA monitor crosses at 0.711 (Appendix E).
def mixture_wealth(seq):
    comp = np.ones(GRID.size); path = []
    for v in seq:
        comp = comp * (1 + GRID * v); path.append(float(comp.mean()))
    return path


const = mixture_wealth([0.2] * 200)
vec12 = [0.2, -0.2, 0.2, 0.2, -0.2, 0.2, 0.2, 0.2, -0.2, 0.2, 0.2, 0.2]
rng = np.random.default_rng(3074)
REPS3, B0, DELTA, K = 20000, 0.5, 0.08, 120
p = B0 + math.sqrt(DELTA) * rng.choice([-1.0, 1.0], size=(REPS3, K))
yy = (rng.random(p.shape) < p).astype(float)
xs = (B0 - yy) ** 2 - (p - yy) ** 2
rng = np.random.default_rng(3075)
y0 = (rng.random((REPS3, 600)) < 0.5).astype(float)
x0 = (0.9 - y0) ** 2 - (0.1 - y0) ** 2
out['od10_alternative_mixture_T36'] = {
    'oracle_twelve_constant_+0.2': round(const[11], 6),
    'oracle_first_crossing_of_20_constant_+0.2': next(i + 1 for i, v in enumerate(const) if v >= THRESH),
    'oracle_wealth_at_first_crossing': round(next(v for v in const if v >= THRESH), 6),
    'oracle_12_vector': round(mixture_wealth(vec12)[-1], 6),
    'power_b=0.5_delta=0.08_clusters=120': {'grapa': rate(grapa_peak(xs) >= THRESH),
                                           'mixture': rate(mixture_peak(xs) >= THRESH)},
    'null_law_c_600_clusters': {'grapa': rate(grapa_peak(x0) >= THRESH), 'mixture': rate(mixture_peak(x0) >= THRESH)}}

print(json.dumps(out, indent=1))
