"""Simulations of the method reassessment in research/18-method-reassessment.md (no reference code, no network).

Owner directive on PR #4, comment 6283736614 (2026-10-20): reassess whether the Phase-1 statistical proof method is
identifiable, valid and practically useful, and compare it with fundamentally different approaches. Each section
below backs one numbered claim of `18`:
- S1: the paired cluster increment X = Brier(baseline) - Brier(FULL) under an explicit forecast law, giving the
  per-cluster standard deviation sigma and the period-level standard deviation tau that a shared outcome shock adds;
- S2: power and minimum detectable effect of the block-level test as a function of the number of independent
  periods G, the period-level standard deviation tau and the clusters per period n (analytic, checked by simulation);
- S3: size and power on G = 24 block means of four tests (cluster-iid t, block t, block sign-flip, betting
  e-process) under independent, serially dependent and skewed period shocks;
- S3b: the betting e-process against the number of independent blocks G;
- S3c: the block t under a pre-registered persistence bound rho_max (variance-inflated critical value);
- S4: non-identifiability of outcome-independent selection from listing metadata, and the identified set of the
  population mean under an omitted share m;
- S5: power of the six-comparator intersection-union conjunction against a fixed-sequence (gatekeeping) order;
- S6 (reassessment R2, RC-282 and RC-286): the block t calibrated over a complete, pre-registered validity class of
  joint laws of the period means, its size inside the class, and laws outside the class that a scalar persistence
  bound admits (equicorrelation, odd/even common shocks);
- S7 (RC-290): familywise error of the fixed-sequence family under the complete joint generator of acceptance test
  M-6;
- S8 (RC-281, RC-284, RC-289): exact examples: the sharp bound d(2 - d) on a paired Brier increment under a divergence
  bound d, an event-weighted and a period-balanced mean of opposite sign, and two outcome laws with the same forecasts
  and different increment standard deviations;
- S9 (reassessment R3, RC-292 and RC-296): a cutoff certified at size <= alpha by an order-statistic bound on the
  calibration draws of each law of the class, against the empirical 0.95 quantile, and power at the certified cutoff
  against the exact noncentral-t power at that cutoff;
- S10 (RC-295): a fixed-sequence family whose later component has a different joint law, tested at the first
  component's cutoff and at a cutoff certified for its own law;
- S11 (RC-294): the variance estimate of the event-weighted mean of F10 with known weights, as written in R2 and with
  the leverage correction, against the true variance and at the nominal t cutoff.
Run from the repository root in the hash-locked environment of research/reproduction/requirements.txt:
    python research/reproduction/reassessment_sims.py
Deterministic: every section uses its own fixed seed. The output is one JSON object; a table row is one line of it
(RC-288: section headers printed as `"name":` lines were not JSON).
"""
import itertools
import json

import numpy as np
from scipy import optimize, stats

ALPHA = 0.05


def forecast_law(rng, n_periods, n_per, base_rate, skill, noise, shock, lean):
    """Paired increments X = (b - Y)^2 - (p - Y)^2 for n_per clusters in each of n_periods periods.

    True event probabilities q ~ Beta(mean base_rate, concentration 4); the FULL forecast is
    p = clip(base_rate + lean + skill * (q - base_rate) + N(0, noise^2), 0.01, 0.99), lean a systematic offset of
    FULL from the baseline; the baseline forecast is base_rate.
    A period shock z ~ N(0, 1) shifts every outcome probability of the period by shock * z (clipped), so outcomes
    of one period share a common component that no outcome cluster can absorb.
    """
    a, b = 4 * base_rate, 4 * (1 - base_rate)
    q = rng.beta(a, b, size=(n_periods, n_per))
    p = np.clip(base_rate + lean + skill * (q - base_rate) + rng.normal(0, noise, q.shape), 0.01, 0.99)
    z = rng.normal(0, 1, (n_periods, 1))
    q_obs = np.clip(q + shock * z, 0.0, 1.0)
    y = (rng.random(q.shape) < q_obs).astype(float)
    return (base_rate - y) ** 2 - (p - y) ** 2


def s1_forecast_law():
    rng = np.random.default_rng(20261020)
    rows = []
    for skill, noise, lean in [(0.0, 0.10, 0.0), (0.25, 0.10, 0.0), (0.5, 0.10, 0.0), (0.5, 0.05, 0.0),
                               (0.5, 0.05, 0.05), (0.5, 0.05, 0.10)]:
        for shock in [0.0, 0.03, 0.06]:
            x = forecast_law(rng, 4000, 50, 0.3, skill, noise, shock, lean)
            period_means = x.mean(axis=1)
            sigma = float(x.std())
            tau2 = max(float(period_means.var()) - sigma ** 2 / 50, 0.0)
            rows.append({'skill': skill, 'noise': noise, 'lean': lean, 'shock': shock,
                         'delta': round(float(x.mean()), 4), 'sigma': round(sigma, 3), 'tau': round(tau2 ** 0.5, 4),
                         'tau_first_order_2_shock_lean': round(2 * shock * lean, 4)})
    return rows


def mde(g, tau, sigma, n, power=0.8):
    """Smallest mean detected with the given power by the one-sided t test on G independent normal block means.

    Exact: the Studentized mean is noncentral t on G - 1 df with noncentrality mean / se, so the MDE is se times the
    noncentrality whose upper tail beyond the critical value equals the power (RC-287: the sum of two central t
    quantiles is an approximation, poorest at small G)."""
    se = np.sqrt((tau ** 2 + sigma ** 2 / n) / g)
    crit = stats.t.ppf(1 - ALPHA, g - 1)
    noncentrality = optimize.brentq(lambda nc: stats.nct.sf(crit, g - 1, nc) - power, 0.0, 50.0, xtol=1e-12)
    return float(noncentrality * se)


def s2_power_table():
    sigma = 0.10
    table = []
    for tau in [0.0, 0.005, 0.01, 0.02]:
        for g in [12, 24, 48, 104, 260]:
            table.append({'tau': tau, 'G': g,
                          'mde_n25': round(mde(g, tau, sigma, 25), 4),
                          'mde_n100': round(mde(g, tau, sigma, 100), 4),
                          'mde_n_inf': round(mde(g, tau, sigma, 10 ** 9), 4)})
    rng = np.random.default_rng(7)
    checks = []
    for tau, g, n in [(0.01, 24, 25), (0.01, 104, 25), (0.005, 24, 100)]:
        delta = mde(g, tau, sigma, n)
        reps = 20000
        means = delta + rng.normal(0, tau, (reps, g)) + rng.normal(0, sigma / np.sqrt(n), (reps, g))
        t = means.mean(1) / (means.std(1, ddof=1) / np.sqrt(g))
        checks.append({'tau': tau, 'G': g, 'n': n, 'delta': round(delta, 4),
                       'simulated_power': round(float((t > stats.t.ppf(1 - ALPHA, g - 1)).mean()), 4)})
    needed = []
    for tau in [0.005, 0.01, 0.02]:
        for delta in [0.005, 0.01, 0.02]:
            g = 3
            while mde(g, tau, sigma, 100) > delta and g < 100000:
                g += 1
            needed.append({'tau': tau, 'delta': delta, 'G_needed_n100': g})
    return {'sigma': sigma, 'mde': table, 'simulation_check': checks, 'periods_needed_for_80pct': needed}


def block_t_reject(means):
    g = means.shape[1]
    sd = means.std(1, ddof=1)
    t = np.where(sd > 0, means.mean(1) / np.where(sd > 0, sd, 1) * np.sqrt(g), 0.0)
    return t > stats.t.ppf(1 - ALPHA, g - 1)


def sign_flip_reject(rng, means, flips=999):
    """Monte Carlo sign-flip test of the block means (exact for independent, symmetric block means)."""
    obs = means.mean(1)
    signs = rng.choice([-1.0, 1.0], size=(flips, means.shape[1]))
    null = means @ signs.T / means.shape[1]
    p = (1 + (null >= obs[:, None]).sum(1)) / (flips + 1)
    return p <= ALPHA


def betting_reject(means, lam_cap):
    """Predictable plug-in betting e-process on block means, rejecting when wealth reaches 1/alpha at any block.

    Anytime-valid when 1 + lam * x > 0 for every possible block mean x: lam_cap = 0.5 needs x > -2, which every Brier
    difference (range [-1, 1]) meets; lam_cap = 2.5 needs x > -0.4, which holds only if |p_FULL - p_baseline| <= 0.2 by
    design, because a divergence bound d bounds the increment by d(2 - d) = 0.36 (RC-281, S8)."""
    reps, g = means.shape
    log_w = np.zeros(reps)
    crossed = np.zeros(reps, dtype=bool)
    s1 = np.zeros(reps)
    s2 = np.zeros(reps)
    for b in range(g):
        if b == 0:
            lam = np.zeros(reps)
        else:
            mu = s1 / b
            var = s2 / b - mu ** 2
            lam = np.clip(mu / (var + mu ** 2 + 1e-12), 0.0, lam_cap)
        x = means[:, b]
        log_w += np.log1p(lam * x)
        crossed |= log_w >= np.log(1 / ALPHA)
        s1 += x
        s2 += x ** 2
    return crossed


def period_shocks(rng, kind, reps, g, tau):
    if kind == 'iid normal':
        return rng.normal(0, tau, (reps, g))
    if kind.startswith('AR(1)'):
        rho = float(kind.split('=')[1])
        e = rng.normal(0, tau * np.sqrt(1 - rho ** 2), (reps, g))
        out = np.empty((reps, g))
        out[:, 0] = rng.normal(0, tau, reps)
        for b in range(1, g):
            out[:, b] = rho * out[:, b - 1] + e[:, b]
        return out
    if kind == 'skewed two-point':
        # mean zero, sd tau, a rare large negative period (probability 0.05)
        p = 0.05
        hi, lo = tau * np.sqrt(p / (1 - p)), -tau * np.sqrt((1 - p) / p)
        return np.where(rng.random((reps, g)) < p, lo, hi)
    if kind.startswith('equicorrelated'):
        # every pair of periods correlated rho: one common shock for all periods
        rho = float(kind.split('=')[1])
        return tau * (np.sqrt(rho) * rng.normal(0, 1, (reps, 1)) + np.sqrt(1 - rho) * rng.normal(0, 1, (reps, g)))
    if kind == 'odd/even common shocks':
        # one shock shared by the odd periods, another by the even ones: lag-one correlation zero, two effective draws
        shared = rng.normal(0, tau, (reps, 2))
        return np.where(np.arange(g) % 2 == 0, shared[:, [0]], shared[:, [1]])
    raise ValueError(kind)


def s3_tests():
    rng = np.random.default_rng(11)
    g, n, sigma, tau, reps = 24, 25, 0.10, 0.01, 20000
    rows = []
    for kind in ['iid normal', 'AR(1) rho=0.5', 'AR(1) rho=0.9', 'skewed two-point']:
        for delta in [0.0, 0.01, 0.02]:
            shocks = period_shocks(rng, kind, reps, g, tau)
            noise = rng.normal(0, sigma, (reps, g, n))
            x = delta + shocks[:, :, None] + noise
            means = x.mean(2)
            flat = x.reshape(reps, -1)
            t_iid = flat.mean(1) / (flat.std(1, ddof=1) / np.sqrt(g * n))
            half = reps // 4  # the sign-flip test uses a quarter of the replications to bound run time
            rows.append({
                'shock law': kind, 'delta': delta,
                'cluster_iid_t': round(float((t_iid > stats.norm.ppf(1 - ALPHA)).mean()), 4),
                'block_t': round(float(block_t_reject(means).mean()), 4),
                'block_sign_flip': round(float(sign_flip_reject(rng, means[:half]).mean()), 4),
                'betting_cap_0.5': round(float(betting_reject(means, 0.5).mean()), 4),
                'betting_cap_2.5': round(float(betting_reject(means, 2.5).mean()), 4),
            })
    upper = {r['shock law'] + ' / ' + k: round(float(stats.beta.ppf(0.99, r[k] * reps + 1, reps - r[k] * reps)), 4)
             for r in rows if r['delta'] == 0.0 for k in ['block_t', 'cluster_iid_t']}
    return {'G': g, 'n': n, 'sigma': sigma, 'tau': tau, 'reps': reps, 'sign_flip_reps': reps // 4, 'rows': rows,
            'clopper_pearson_99_upper_at_delta_0': upper}


def s3b_betting_horizon():
    """The betting e-process needs calendar time: crossing rate against the number of independent blocks G."""
    rng = np.random.default_rng(12)
    sigma_b, reps = (0.01 ** 2 + 0.10 ** 2 / 25) ** 0.5, 20000
    rows = []
    for g in [24, 104, 260, 520]:
        for delta in [0.0, 0.01, 0.02]:
            means = delta + rng.normal(0, sigma_b, (reps, g))
            rows.append({'G': g, 'delta': delta,
                         'betting_cap_0.5': round(float(betting_reject(means, 0.5).mean()), 4),
                         'betting_cap_2.5': round(float(betting_reject(means, 2.5).mean()), 4),
                         'block_t_fixed_horizon': round(float(block_t_reject(means).mean()), 4)})
    # a zero count is not zero power: its one-sided 99 % Clopper-Pearson upper bound is 1 - 0.01^(1/reps) (RC-285)
    return {'block_sd': round(sigma_b, 4), 'reps': reps, 'rows': rows,
            'clopper_pearson_99_upper_for_zero_crossings': round(1 - 0.01 ** (1 / reps), 6)}


def s3c_bounded_persistence():
    """Block t with its critical value inflated by sqrt((1 + rho_max) / (1 - rho_max)), the AR(1) long-run variance
    factor of a mean, when the period shocks follow AR(1) with rho <= rho_max (rho_max pre-registered)."""
    rng = np.random.default_rng(14)
    g, n, sigma, tau, reps = 24, 25, 0.10, 0.01, 20000
    rows = []
    for rho_max in [0.5, 0.9]:
        for rho in sorted({0.0, rho_max}):
            for delta in [0.0, 0.01, 0.02]:
                shocks = period_shocks(rng, f'AR(1) rho={rho}', reps, g, tau) if rho > 0 else rng.normal(0, tau, (reps, g))
                means = delta + shocks + rng.normal(0, sigma / np.sqrt(n), (reps, g))
                sd = means.std(1, ddof=1)
                t = means.mean(1) / (sd / np.sqrt(g))
                crit = stats.t.ppf(1 - ALPHA, g - 1) * np.sqrt((1 + rho_max) / (1 - rho_max))
                rows.append({'rho_max': rho_max, 'true_rho': rho, 'delta': delta, 'critical_value': round(float(crit), 3),
                             'rejection': round(float((t > crit).mean()), 4)})
    return {'G': g, 'n': n, 'sigma': sigma, 'tau': tau, 'reps': reps, 'rows': rows}


def s4_selection():
    """World A lists a fixed count of events per period at random; world B lists the same count, chosen by a signal
    correlated with the (unobserved at listing) paired increment. The listing metadata (count per period, timing) are
    identical by construction; the listed-population mean differs."""
    rng = np.random.default_rng(13)
    periods, universe, listed, reps = 24, 30, 10, 4000
    res = {}
    for world in ['A random', 'B signal-selected']:
        reject = 0
        listed_mean = []
        for _ in range(reps):
            x = rng.normal(0.0, 0.10, (periods, universe)) + rng.normal(0, 0.01, (periods, 1))  # exact null
            if world.startswith('A'):
                idx = np.argsort(rng.random((periods, universe)), axis=1)[:, :listed]
            else:
                signal = x + rng.normal(0, 0.15, x.shape)
                idx = np.argsort(-signal, axis=1)[:, :listed]
            chosen = np.take_along_axis(x, idx, axis=1)
            m = chosen.mean(1)
            listed_mean.append(m.mean())
            reject += bool(block_t_reject(m[None, :])[0])
        res[world] = {'listed_count_per_period': listed, 'mean_listed_increment': round(float(np.mean(listed_mean)), 4),
                      'block_t_rejection': round(reject / reps, 4)}
    bounds = []
    for d in [0.2, 0.5, 1.0]:
        bound = d * (2 - d)  # sharp bound of a paired Brier increment when |p_F - p_C| <= d (RC-281, S8)
        for theta in [0.005, 0.01, 0.02]:
            # identified set of the population mean: (1 - m) theta_obs + m [-D, D] with D = d(2 - d);
            # sign identified iff (1 - m) theta > m D
            m_max = theta / (theta + bound)
            bounds.append({'divergence_bound_d': d, 'increment_bound_d_2_minus_d': round(bound, 4),
                           'theta_observed': theta, 'max_omitted_share_for_sign': round(m_max, 4)})
    return {'non_identifiability': res, 'omission_bounds': bounds}


def s5_conjunction():
    rng = np.random.default_rng(17)
    reps = 200000
    rows = []
    for marginal in [0.8, 0.9]:
        mu = stats.norm.ppf(1 - ALPHA) + stats.norm.ppf(marginal)
        for r in [0.0, 0.5, 0.9]:
            for j in [1, 3, 6]:
                cov = np.full((j, j), r) + np.eye(j) * (1 - r)
                z = rng.multivariate_normal(np.full(j, mu), cov, size=reps)
                iut = (z > stats.norm.ppf(1 - ALPHA)).all(1).mean()
                rows.append({'marginal_power': marginal, 'correlation': r, 'J': j,
                             'iut_joint_power': round(float(iut), 4), 'fixed_sequence_first_claim_power': marginal})
    return rows


def t_statistic(means):
    g = means.shape[1]
    return means.mean(1) / (means.std(1, ddof=1) / np.sqrt(g))


def null_period_means(rng, law, reps, g, share):
    """Period means under theta = 0 with unit variance: a period component of variance `share` drawn from `law` (its
    marginal shape and its covariance across periods) plus independent normal cluster noise of variance 1 - share.
    The t statistic is scale-free, so (law, share) is a complete joint law of the statistic under the null."""
    return np.sqrt(share) * period_shocks(rng, law, reps, g, 1.0) + np.sqrt(1 - share) * rng.normal(0, 1, (reps, g))


def s6_validity_class():
    """The block t calibrated over an example validity class L: the critical value c_L is the largest simulated 0.95
    quantile of t over the laws of L, then checked on fresh draws, inside L and outside it. The share 0.2 is the
    S3 point (tau = 0.01, sigma = 0.1, n = 25); share 0.8 is a period-dominated law. L is an example, not a proposal:
    the class is an owner input (OD11)."""
    rng = np.random.default_rng(21)
    g, cal_reps, reps = 24, 200000, 20000
    in_class = [(law, share) for law in ['iid normal', 'AR(1) rho=0.25', 'AR(1) rho=0.5', 'skewed two-point']
                for share in [0.2, 0.8]]
    outside = [('equicorrelated rho=0.5', 0.8), ('odd/even common shocks', 0.8)]
    nominal = stats.t.ppf(1 - ALPHA, g - 1)
    ar_inflated = nominal * np.sqrt((1 + 0.5) / (1 - 0.5))  # the S3c critical value at rho_max = 0.5
    quantiles = {(law, share): float(np.quantile(t_statistic(null_period_means(rng, law, cal_reps, g, share)), 1 - ALPHA))
                 for law, share in in_class}
    c_class = max(quantiles.values())
    level = 1 - 0.01 / len(in_class)  # 99 % simultaneous over the laws of L (Bonferroni)
    rows = []
    for law, share in in_class + outside:
        t = t_statistic(null_period_means(rng, law, reps, g, share))
        hits = int((t > c_class).sum())
        rows.append({'law': law, 'period_share': share, 'in_class': (law, share) in quantiles,
                     'q95': round(quantiles[(law, share)], 3) if (law, share) in quantiles else None,
                     'size_nominal_t': round(float((t > nominal).mean()), 4),
                     'size_ar1_inflated_rho_max_0.5': round(float((t > ar_inflated).mean()), 4),
                     'size_c_class': round(hits / reps, 4),
                     'upper_c_class': round(float(stats.beta.ppf(level, hits + 1, reps - hits)), 4)})
    sd = (0.01 ** 2 + 0.10 ** 2 / 25) ** 0.5  # period-mean sd at the S3 point
    power = []
    for delta in [0.01, 0.02]:
        means = delta + sd * null_period_means(rng, 'iid normal', reps, g, 0.2)
        t = t_statistic(means)
        power.append({'delta': delta, 'law': 'iid normal', 'period_share': 0.2,
                      'power_nominal_t': round(float((t > nominal).mean()), 4),
                      'power_c_class': round(float((t > c_class).mean()), 4)})
    return {'G': g, 'calibration_reps': cal_reps, 'reps': reps, 'nominal_critical_value': round(float(nominal), 3),
            'ar1_inflated_critical_value': round(float(ar_inflated), 3), 'c_class': round(c_class, 3),
            'simultaneous_confidence': round(level, 5), 'rows': rows, 'power_at_s3_point': power}


def s7_fixed_sequence():
    """Acceptance test M-6: J = 3 hypotheses tested in a fixed order, each at alpha and only after every earlier one
    rejected. Statistics jointly normal with unit variances and equal pairwise correlation r; mean 0 for a true null
    (the boundary of H0), z_(1-alpha) + z_power for a false null; every pattern of true and false nulls with at least
    one true null, all false nulls of one pattern at the same marginal power. The familywise error of each
    configuration is checked with a one-sided Clopper-Pearson bound simultaneous over all configurations."""
    rng = np.random.default_rng(19)
    reps, j = 100000, 3
    crit = stats.norm.ppf(1 - ALPHA)
    rows = []
    for r in [-0.4, 0.0, 0.5, 0.9]:
        cov = np.full((j, j), r) + np.eye(j) * (1 - r)
        for false_nulls in itertools.product([False, True], repeat=j):
            if all(false_nulls):
                continue
            for power in ([0.5, 0.8, 0.99] if any(false_nulls) else [None]):
                shift = 0.0 if power is None else crit + stats.norm.ppf(power)
                z = rng.multivariate_normal(np.where(false_nulls, shift, 0.0), cov, size=reps)
                rejected = np.cumprod(z > crit, axis=1).astype(bool)  # tested only after every predecessor rejected
                errors = int((rejected & ~np.array(false_nulls)).any(1).sum())
                rows.append({'r': r, 'nulls': ''.join('F' if f else 'T' for f in false_nulls), 'power': power,
                             'fwer': round(errors / reps, 4), 'errors': errors})
    level = 1 - 0.01 / len(rows)
    for row in rows:
        row['upper'] = round(float(stats.beta.ppf(level, row['errors'] + 1, reps - row['errors'])), 4)
    return {'J': j, 'reps': reps, 'configurations': len(rows), 'simultaneous_confidence': round(level, 6),
            'max_upper': max(row['upper'] for row in rows), 'rows': rows}


def s8_exact_examples():
    grid = np.linspace(0.0, 1.0, 1001)
    p, b = np.meshgrid(grid, grid)
    increment = np.maximum(np.abs((b - 1) ** 2 - (p - 1) ** 2), np.abs(b ** 2 - p ** 2))  # Y = 1 and Y = 0
    bound = [{'d': d, 'grid_sup_increment': round(float(increment[np.abs(p - b) <= d + 1e-12].max()), 6),
              'd_2_minus_d': round(d * (2 - d), 6)} for d in [0.2, 0.5, 1.0]]
    counts, means = np.array([100, 1]), np.array([-0.01, 0.10])
    estimand = {'events_per_period': counts.tolist(), 'period_means': means.tolist(),
                'event_weighted': round(float((counts * means).sum() / counts.sum()), 6),
                'period_balanced': round(float(means.mean()), 6)}
    # one forecast pair, two outcome probabilities: X = 0.13 if Y = 1 and -0.07 if Y = 0, so sd = 0.2 sqrt(q(1 - q))
    p_full, p_base = 0.4, 0.3
    hi, lo = (p_base - 1) ** 2 - (p_full - 1) ** 2, p_base ** 2 - p_full ** 2
    sigma = [{'p_full': p_full, 'p_base': p_base, 'q': q, 'mean': round(q * hi + (1 - q) * lo, 6),
              'sd': round(abs(hi - lo) * np.sqrt(q * (1 - q)), 6),
              'forecast_only_bound': round(abs(p_full - p_base) * max(p_full + p_base, 2 - p_full - p_base), 6)}
             for q in [0.3, 0.5]]
    return {'increment_bound': bound, 'estimand_weighting': estimand, 'sigma_needs_outcomes': sigma}


def certified_cutoff(t, n_laws):
    """Smallest order statistic of the calibration draws t of one law whose exceedance probability is at most alpha
    with probability at least 1 - 0.01 / n_laws (RC-292). For a continuous statistic the exceedance probability of
    the (j + 1)-th largest draw is Beta(j + 1, n - j), whatever the law, so taking the largest such cutoff over the
    n_laws laws of a class certifies size <= alpha on every one of them at 99 % joint confidence over the
    calibration. The empirical 0.95 quantile has exceedance probability above alpha about half of the time."""
    n = t.size
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if stats.beta.sf(ALPHA, mid + 1, n - mid) <= 0.01 / n_laws:
            lo = mid
        else:
            hi = mid - 1
    return float(np.sort(t)[::-1][lo])


def s9_certified_cutoff():
    """The S6 example class calibrated twice on the same draws: c_emp, the largest empirical 0.95 quantile (the R2
    rule), and c_cert, the largest certified cutoff. Each is checked on 200,000 fresh draws per law. Power at the S3
    point is compared with the exact noncentral-t power at the cutoff actually used (RC-296: the S2 oracle is exact
    only at the nominal cutoff)."""
    rng = np.random.default_rng(23)
    g, cal_reps, reps, power_reps = 24, 200000, 200000, 20000
    in_class = [(law, share) for law in ['iid normal', 'AR(1) rho=0.25', 'AR(1) rho=0.5', 'skewed two-point']
                for share in [0.2, 0.8]]
    q95, cert = {}, {}
    for law, share in in_class:
        t = t_statistic(null_period_means(rng, law, cal_reps, g, share))
        q95[(law, share)] = float(np.quantile(t, 1 - ALPHA))
        cert[(law, share)] = certified_cutoff(t, len(in_class))
    c_emp, c_cert = max(q95.values()), max(cert.values())
    level = 1 - 0.01 / len(in_class)
    rows = []
    for law, share in in_class:
        t = t_statistic(null_period_means(rng, law, reps, g, share))
        row = {'law': law, 'period_share': share, 'q95': round(q95[(law, share)], 3),
               'certified': round(cert[(law, share)], 3)}
        for name, c in [('c_emp', c_emp), ('c_cert', c_cert)]:
            hits = int((t > c).sum())
            row[f'size_{name}'] = round(hits / reps, 5)
            row[f'lower_{name}'] = round(float(stats.beta.ppf(1 - level, hits, reps - hits + 1)), 5)
            row[f'upper_{name}'] = round(float(stats.beta.ppf(level, hits + 1, reps - hits)), 5)
        rows.append(row)
    sd = (0.01 ** 2 + 0.10 ** 2 / 25) ** 0.5
    power = []
    for name, c in [('nominal', stats.t.ppf(1 - ALPHA, g - 1)), ('c_emp', c_emp), ('c_cert', c_cert)]:
        for delta in [0.01, 0.02]:
            t = t_statistic(delta + sd * null_period_means(rng, 'iid normal', power_reps, g, 0.2))
            power.append({'cutoff': name, 'value': round(float(c), 3), 'delta': delta,
                          'simulated': round(float((t > c).mean()), 4),
                          'noncentral_t_at_cutoff': round(float(stats.nct.sf(c, g - 1, delta / (sd / np.sqrt(g)))), 4)})
    return {'G': g, 'calibration_reps': cal_reps, 'reps': reps, 'power_reps': power_reps,
            'simultaneous_confidence': round(level, 5), 'c_emp': round(c_emp, 3), 'c_cert': round(c_cert, 3),
            'rows': rows, 'power_at_s3_point': power}


def s10_component_cutoffs():
    """Fixed sequence of two components: the first false (delta = 0.03, independent normal means, share 0.2), the
    second a true null whose period means are equicorrelated (0.5, share 0.8). Tested at the first component's
    certified cutoff, the second rejects a true null far above alpha once the first gate opens; at a cutoff certified
    for its own law the familywise error is at most alpha. Marginal validity of each component suffices whatever the
    dependence between components, because the first true null in the order must reject for any error to occur."""
    rng = np.random.default_rng(29)
    g, cal_reps, reps = 24, 200000, 100000
    first, second = ('iid normal', 0.2), ('equicorrelated rho=0.5', 0.8)
    c_first = certified_cutoff(t_statistic(null_period_means(rng, first[0], cal_reps, g, first[1])), 1)
    c_second = certified_cutoff(t_statistic(null_period_means(rng, second[0], cal_reps, g, second[1])), 1)
    sd = (0.01 ** 2 + 0.10 ** 2 / 25) ** 0.5
    t1 = t_statistic(0.03 + sd * null_period_means(rng, first[0], reps, g, first[1]))
    t2 = t_statistic(null_period_means(rng, second[0], reps, g, second[1]))
    rows = []
    for name, c in [('first component cutoff', c_first), ('own certified cutoff', c_second)]:
        errors = int(((t1 > c_first) & (t2 > c)).sum())
        rows.append({'second_cutoff': name, 'value': round(c, 3), 'first_rejects': round(float((t1 > c_first).mean()), 4),
                     'fwer': round(errors / reps, 4),
                     'upper_99': round(float(stats.beta.ppf(0.99, errors + 1, reps - errors)), 4)})
    return {'G': g, 'calibration_reps': cal_reps, 'reps': reps, 'first': list(first), 'second_true_null': list(second),
            'rows': rows}


def r2_weighted_variance(means, w):
    """The variance estimate of the event-weighted mean written in `18` R2: sum w_b^2 (M_b - theta_E)^2 G / (G - 1)."""
    g = means.shape[1]
    resid = means - (means @ w)[:, None]
    return (w ** 2 * resid ** 2).sum(1) * g / (g - 1)


def leverage_corrected_variance(means, w):
    """sum w_b^2 (M_b - theta_E)^2 / (1 - 2 w_b + sum w^2): unbiased for Var(theta_E) when the period means are
    independent with a common variance, because Var(M_b - theta_E) = v (1 - 2 w_b + sum w^2) then."""
    resid = means - (means @ w)[:, None]
    return (w ** 2 * resid ** 2 / (1 - 2 * w + (w ** 2).sum())).sum(1)


def s11_weighted_variance():
    """RC-294. Codex's example (two independent period means of variance 1, weights 100/101 and 1/101) and G = 24 with
    three count vectors, under period means of common variance and of variance proportional to 1/n_b (independent
    events, no period component): the mean of each variance estimate over the true variance, and the size of the
    weighted t at the nominal t cutoff. Neither estimate makes the nominal cutoff valid, so the cutoff of the weighted
    statistic is calibrated over the class with its weight vector."""
    rng = np.random.default_rng(31)
    w = np.array([100.0, 1.0]) / 101
    means = rng.normal(0, 1, (400000, 2))
    codex = {'weights': '100/101, 1/101', 'true_variance': round(float((w ** 2).sum()), 5),
             'r2_expectation_exact': round(8 * 100 ** 2 / 101 ** 4, 6),
             'r2_mean_simulated': round(float(r2_weighted_variance(means, w).mean()), 6),
             'leverage_corrected_mean_simulated': round(float(leverage_corrected_variance(means, w).mean()), 4)}
    g, reps = 24, 100000
    nominal = stats.t.ppf(1 - ALPHA, g - 1)
    rows = []
    for label, counts in [('one dominant period', np.array([100] + [1] * 23)),
                          ('two count levels', np.array([30] * 12 + [3] * 12)),
                          ('geometric 1 to 100', np.round(np.geomspace(1, 100, g)))]:
        w = counts / counts.sum()
        for law, sd in [('common variance', np.ones(g)), ('variance 1/n_b', 1 / np.sqrt(counts))]:
            means = rng.normal(0, 1, (reps, g)) * sd
            true_var = float((w ** 2 * sd ** 2).sum())
            theta = means @ w
            row = {'counts': label, 'law': law}
            for name, estimate in [('r2', r2_weighted_variance), ('leverage_corrected', leverage_corrected_variance)]:
                v = estimate(means, w)
                row[f'{name}_mean_over_true'] = round(float(v.mean()) / true_var, 3)
                row[f'{name}_size_nominal_t'] = round(float((theta / np.sqrt(v) > nominal).mean()), 4)
            rows.append(row)
    return {'codex_example': codex, 'G': g, 'reps': reps, 'rows': rows}


def dumps(value, depth=0):
    """JSON text of value: a container holding containers spans lines, anything else stays on one line, so the
    committed output is one JSON object whose table rows are single lines (RC-288)."""
    pad, inner = ' ' * depth, ' ' * (depth + 1)
    if isinstance(value, dict) and any(isinstance(v, (list, dict)) for v in value.values()):
        items = [f'{inner}{json.dumps(key)}: {dumps(item, depth + 1)}' for key, item in value.items()]
        return '{\n' + ',\n'.join(items) + '\n' + pad + '}'
    if isinstance(value, list) and any(isinstance(v, (list, dict)) for v in value):
        return '[\n' + ',\n'.join(f'{inner}{dumps(item, depth + 1)}' for item in value) + '\n' + pad + ']'
    return json.dumps(value)


def main():
    sections = [('S1 forecast law', s1_forecast_law), ('S2 power', s2_power_table), ('S3 tests', s3_tests),
                ('S3b betting horizon', s3b_betting_horizon), ('S3c bounded persistence', s3c_bounded_persistence),
                ('S4 selection', s4_selection), ('S5 conjunction', s5_conjunction),
                ('S6 validity class', s6_validity_class), ('S7 fixed sequence', s7_fixed_sequence),
                ('S8 exact examples', s8_exact_examples), ('S9 certified cutoff', s9_certified_cutoff),
                ('S10 component cutoffs', s10_component_cutoffs), ('S11 weighted variance', s11_weighted_variance)]
    print(dumps({name: section() for name, section in sections}))


if __name__ == '__main__':
    main()
