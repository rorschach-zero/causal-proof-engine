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
  the leverage correction, against the true variance and at the nominal t cutoff;
- S12 (reassessment R4, RC-297): a null law with theta < 0 whose centred shape lies outside the class, and the
  pointwise monotonicity in theta of the block t and of the leverage-corrected weighted t under a location shift;
- S13 (RC-298): the calibration budget spent per component against spent across the union of all laws of all
  components, its joint certificate and its cost in cutoff and power;
- S14 (RC-300): calibration sizes at which no cutoff is certifiable, and their refusal;
- S15 (RC-301): the variance of a period mean when the period component and the cluster errors are correlated;
- S16 (reassessment R5, RC-302): the unconditional size of the whole procedure, calibration and test together, which
  is (j + 1)/(n + 1) at a certified index j by exchangeability, against the bound alpha + 0.01 that the 99 %
  certificate alone gives, exactly and by an end-to-end simulation;
- S16 (reassessment R6, RC-306): for a class of several laws, where the cutoff is the maximum of the law-wise cutoffs,
  (j + 1)/(n + 1) is an upper bound on the procedure's size, not its value; an end-to-end simulation of the whole
  multi-law calibration and test shows the size of each law against that bound;
- S16 (reassessment R7, RC-310): that multi-law simulation repeated on three further seeds, so the seed check R6
  quoted is committed output, pooled with and without the seed that prompted it, and the normal law alone on seeds
  that played no part in that choice;
- S17 (reassessment R7, RC-309): an operator who anchors m calibration records and runs only the one with the
  smallest cutoff, exactly and by an end-to-end simulation, and one who reports whichever of m cohorts rejects;
- S18 (reassessment R8, RC-312): S_max confirmatory claims calibrated with the index chosen at alpha against the index
  chosen at alpha/S_max, the bound check (j + 1)/(n + 1) <= alpha/S_max on each, the smallest certifiable calibration,
  and the familywise error of S_max = 2 claims end to end.
Run from the repository root in the hash-locked environment of research/reproduction/requirements.txt:
    python research/reproduction/reassessment_sims.py
Deterministic: every section uses its own fixed seed. The output is one JSON object; a table row is one line of it
(RC-288: section headers printed as `"name":` lines were not JSON).
"""
import itertools
import json

import numpy as np
from scipy import integrate, optimize, stats

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


def certified_cutoff(t, budget, alpha=ALPHA):
    """Smallest order statistic of the calibration draws t of one law whose exceedance probability is at most alpha
    with probability at least 1 - budget (RC-292). A claim that is one of S_max confirmatory claims passes
    alpha = ALPHA / S_max, which every step below then uses (RC-312). For a continuous statistic the exceedance
    probability of the (j + 1)-th largest draw is Beta(j + 1, n - j), whatever the law. The caller spends the 0.01 of
    the whole family across every law of every component and statistic it certifies, budget = 0.01 / (total laws), so
    the union bound certifies size <= alpha on all of them at 99 % joint confidence over the calibration (RC-298). The
    empirical 0.95 quantile has exceedance probability above alpha about half of the time. When even the sample
    maximum fails the condition, (1 - alpha)^n > budget, no cutoff is certified and the calibration is refused
    (RC-300). The 99 % certificate alone bounds the unconditional size only by alpha + 0.01 (RC-302); the procedure's
    unconditional size on the calibrated law is (j + 1)/(n + 1) by exchangeability, and a cutoff for which that
    exceeds alpha is refused."""
    n = t.size
    j = certified_index(n, budget, alpha)
    if j is None:
        raise ValueError(f'no certifiable cutoff: (1 - {alpha})^{n} > {budget}; '
                         f'n >= {minimum_calibration_size(budget, alpha)} draws are needed')
    if marginal_size(j, n) > alpha:
        raise ValueError(f'unconditional size {marginal_size(j, n)} of index {j} exceeds alpha')
    return float(np.sort(t)[::-1][j])


def certified_index(n, budget, alpha=ALPHA):
    """Index j of the order statistic that certified_cutoff returns for n draws, or None when it refuses (RC-300)."""
    if stats.beta.sf(alpha, 1, n) > budget:
        return None
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if stats.beta.sf(alpha, mid + 1, n - mid) <= budget:
            lo = mid
        else:
            hi = mid - 1
    return lo


def marginal_size(j, n):
    """Unconditional probability, over calibration and test together, that a fresh draw of the calibrated law exceeds
    the (j + 1)-th largest of n calibration draws: (j + 1)/(n + 1) for a continuous statistic, by exchangeability of
    the n + 1 draws (RC-302)."""
    return (j + 1) / (n + 1)


def minimum_calibration_size(budget, alpha=ALPHA):
    """Smallest n with (1 - alpha)^n <= budget: below it not even the sample maximum is certified (RC-300)."""
    return int(np.ceil(np.log(budget) / np.log(1 - alpha)))


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
        cert[(law, share)] = certified_cutoff(t, 0.01 / len(in_class))
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
    for its own law the familywise error is at most alpha. The two cutoffs share the family's calibration budget 0.01
    (RC-298). Marginal validity of each component suffices whatever the
    dependence between components, because the first true null in the order must reject for any error to occur."""
    rng = np.random.default_rng(29)
    g, cal_reps, reps = 24, 200000, 100000
    first, second = ('iid normal', 0.2), ('equicorrelated rho=0.5', 0.8)
    budget = 0.01 / 2  # one law in each of the two components share the family's 0.01 (RC-298)
    c_first = certified_cutoff(t_statistic(null_period_means(rng, first[0], cal_reps, g, first[1])), budget)
    c_second = certified_cutoff(t_statistic(null_period_means(rng, second[0], cal_reps, g, second[1])), budget)
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


def weighted_t(means, w):
    """The event-weighted mean of F10 Studentized by the leverage-corrected variance estimate."""
    return means @ w / np.sqrt(leverage_corrected_variance(means, w))


def s12_composite_null():
    """RC-297. The class L fixes laws at theta = 0, while H0 is theta <= 0. (a) Codex's example: with probability 0.1
    every period sits in a common positive regime (0.01 + 0.001 z), otherwise at -0.1 + 0.02 z, so theta = -0.089;
    it rejects at the S9 cutoff in about 10 %, and so does its centred shape (M - theta), which is therefore outside
    every class whose certified cutoff is 3.357. (b) Under a location shift M = theta + U, with the law of U fixed, both
    statistics are translation-equivariant in the mean and invariant in the variance estimate, so a shift below zero
    can only remove rejections: counted draw by draw on every law of the S9 class."""
    rng = np.random.default_rng(37)
    g, reps, c_cert = 24, 200000, 3.357  # c_cert as computed in S9
    regime = rng.random((reps, 1)) < 0.1
    means = np.where(regime, 0.01 + 0.001 * rng.normal(0, 1, (reps, g)), -0.1 + 0.02 * rng.normal(0, 1, (reps, g)))
    theta = 0.1 * 0.01 + 0.9 * -0.1
    hits, hits_centred = int((t_statistic(means) > c_cert).sum()), int((t_statistic(means - theta) > c_cert).sum())
    counterexample = {'theta': round(theta, 4), 'rejection_at_c_cert': round(hits / reps, 4),
                      'lower_99': round(float(stats.beta.ppf(0.01, hits, reps - hits + 1)), 4),
                      'centred_shape_rejection_at_c_cert': round(hits_centred / reps, 4)}
    counts = np.array([30] * 12 + [3] * 12)
    w = counts / counts.sum()
    rows = []
    for law, share in [(law, share) for law in ['iid normal', 'AR(1) rho=0.25', 'AR(1) rho=0.5', 'skewed two-point']
                       for share in [0.2, 0.8]]:
        u = null_period_means(rng, law, reps // 4, g, share)
        row = {'law': law, 'period_share': share}
        for name, statistic in [('block_t', t_statistic), ('weighted_t', lambda m: weighted_t(m, w))]:
            at_zero = statistic(u) > c_cert
            row[f'{name}_size_theta_0'] = round(float(at_zero.mean()), 5)
            for shift in [0.05, 0.2]:
                below = statistic(u - shift) > c_cert
                row[f'{name}_size_theta_minus_{shift}'] = round(float(below.mean()), 5)
                row[f'{name}_new_rejections_minus_{shift}'] = int((below & ~at_zero).sum())
        rows.append(row)
    return {'G': g, 'reps': reps, 'location_reps': reps // 4, 'c_cert': c_cert, 'weights': 'two count levels',
            'shift_unit': 'standard deviation of a period mean', 'counterexample': counterexample, 'location_shift': rows}


def s13_family_budget():
    """RC-298. A fixed sequence of three components, each with the eight laws of the S9 class (an illustration: each
    component has its own class in the design). Spending 0.01 / 8 inside each component certifies each component at
    99 %, and the union bound leaves the family 1 - 3 * 0.01 = 97 %; spending 0.01 / 24 across the union restores 99 %.
    The failure probabilities are the exact Beta tails at the selected order statistics; the cost is the change in
    cutoff and in noncentral-t power at the S3 point."""
    rng = np.random.default_rng(43)
    g, cal_reps, components = 24, 200000, 3
    in_class = [(law, share) for law in ['iid normal', 'AR(1) rho=0.25', 'AR(1) rho=0.5', 'skewed two-point']
                for share in [0.2, 0.8]]
    draws = [t_statistic(null_period_means(rng, law, cal_reps, g, share)) for law, share in in_class]
    sd = (0.01 ** 2 + 0.10 ** 2 / 25) ** 0.5
    rows = []
    for scheme, budget in [('per component', 0.01 / len(in_class)),
                           ('union of all laws', 0.01 / (components * len(in_class)))]:
        cutoffs = [certified_cutoff(t, budget) for t in draws]
        failure = 0.0
        for t, c in zip(draws, cutoffs):
            j = int((t > c).sum())  # the selected cutoff is the (j + 1)-th largest draw
            failure += float(stats.beta.sf(ALPHA, j + 1, cal_reps - j))
        c = max(cutoffs)
        rows.append({'scheme': scheme, 'budget_per_law': round(budget, 6), 'c_cert': round(c, 3),
                     'component_failure_bound': round(failure, 5),
                     'family_failure_bound': round(components * failure, 5),
                     'power_delta_0.01': round(float(stats.nct.sf(c, g - 1, 0.01 / (sd / np.sqrt(g)))), 4),
                     'power_delta_0.02': round(float(stats.nct.sf(c, g - 1, 0.02 / (sd / np.sqrt(g)))), 4)})
    return {'G': g, 'calibration_reps': cal_reps, 'components': components, 'laws_per_component': len(in_class),
            'rows': rows}


def s14_unattainable_certification():
    """RC-300. Even the sample maximum of n draws exceeds the alpha quantile with probability (1 - alpha)^n, so no
    cutoff is certified when that exceeds the budget. Codex's example: 8 laws and n = 100. certified_cutoff refuses."""
    rows = []
    for n, laws in [(100, 8), (130, 8), (131, 8), (200000, 8), (200000, 24)]:
        budget = 0.01 / laws
        try:
            certified_cutoff(np.random.default_rng(47).normal(0, 1, n), budget)
            refused = False
        except ValueError:
            refused = True
        rows.append({'n': n, 'laws': laws, 'budget_per_law': round(budget, 6),
                     'log10_maximum_failure_probability': round(n * float(np.log10(1 - ALPHA)), 3),
                     'minimum_n': minimum_calibration_size(budget), 'refused': refused})
    return {'rows': rows}


def s15_within_period_covariance():
    """RC-301. Period mean M_b = a_b + e_bar_b with a_b of variance tau^2 and n cluster errors of variance sigma^2.
    Var(M_b) = tau^2 + sigma^2 / n + 2 Cov(a_b, e_bar_b) + sigma^2 (n - 1) rho_w / n, with rho_w the mean pairwise
    correlation of the errors within a period; F1's tau^2 + sigma^2 / n needs both covariance terms to vanish."""
    rng = np.random.default_rng(53)
    reps, n, tau, sigma = 200000, 25, 0.01, 0.1
    a = rng.normal(0, tau, (reps, 1))
    rho_w = 0.05
    cases = [('independent components', sigma * rng.normal(0, 1, (reps, n)), 0.0, 0.0),
             ('errors offset the period component', -a + np.sqrt(sigma ** 2 - tau ** 2) * rng.normal(0, 1, (reps, n)),
              -tau ** 2, tau ** 2 / sigma ** 2),
             ('equicorrelated errors rho_w=0.05',
              sigma * (np.sqrt(rho_w) * rng.normal(0, 1, (reps, 1)) + np.sqrt(1 - rho_w) * rng.normal(0, 1, (reps, n))),
              0.0, rho_w)]
    rows = []
    for label, errors, cov, rho in cases:
        rows.append({'case': label, 'simulated_var': float(f'{float((a[:, 0] + errors.mean(1)).var()):.4g}'),
                     'f1_formula': float(f'{tau ** 2 + sigma ** 2 / n:.4g}'),
                     'general_formula': float(f'{tau ** 2 + sigma ** 2 / n + 2 * cov + sigma ** 2 * (n - 1) * rho / n:.4g}')})
    return {'n': n, 'tau': tau, 'sigma': sigma, 'reps': reps, 'rows': rows}


def s16_unconditional_size():
    """RC-302. The 99 % certificate is a statement about the random cutoff: with probability 0.99 over the calibration
    its size is <= alpha. On its own that bounds the unconditional size of calibration and test together only by
    0.99 alpha + 0.01. Rejection against one law's own cutoff has unconditional probability P(T_new > T_(j+1)) =
    (j + 1)/(n + 1), exact for a continuous statistic whatever the law, because the n calibration draws and the fresh
    draw are exchangeable. A class of several laws rejects only above the largest law-wise cutoff, so for it (j + 1)/(n + 1)
    is an upper bound on the size, generally not attained (RC-306). Reported as that bound for the certifications of
    S9, S10, S13 and S14 and over a grid of n and budgets; by an end-to-end simulation on uniform draws for one law,
    where the bound is exact; and by an end-to-end simulation of a three-law class, calibrated law by law, cut off at
    the maximum and tested on a fresh draw of each law."""
    used = [('S9, K = 8', 200000, 0.01 / 8), ('S10, two laws', 200000, 0.01 / 2),
            ('S13 per component', 200000, 0.01 / 8), ('S13 union, K = 24', 200000, 0.01 / 24),
            ('S14 minimum n, K = 8', 131, 0.01 / 8), ('S14 minimum n, K = 24', 152, 0.01 / 24)]
    rows = []
    for name, n, budget in used:
        j = certified_index(n, budget)
        rows.append({'certification': name, 'n': n, 'budget_per_law': round(budget, 6), 'index_j': j,
                     'unconditional_size_bound': round(marginal_size(j, n), 6),
                     'certificate_only_bound': round((1 - 0.01) * ALPHA + 0.01, 4)})
    worst = {'n': None, 'budget_per_law': None, 'unconditional_size_bound': 0.0}
    grid = np.unique(np.round(np.logspace(np.log10(131), 6, 2000)).astype(int))
    for k in [1, 2, 3, 8, 24, 100, 1000]:
        for n in grid:
            j = certified_index(int(n), 0.01 / k)
            if j is not None and marginal_size(j, int(n)) > worst['unconditional_size_bound']:
                worst = {'n': int(n), 'budget_per_law': round(0.01 / k, 6),
                         'unconditional_size_bound': round(marginal_size(j, int(n)), 6)}
    committed = multi_law_counts(59)
    rng = np.random.default_rng(53)
    simulated, reps, batch = [], 200000, 10000
    for n, budget in [(131, 0.01 / 8), (1000, 0.01 / 8), (1000, 0.01)]:
        j = certified_index(n, budget)
        rejections = failures = 0
        for _ in range(reps // batch):
            cal = rng.random((batch, n))
            cutoff = -np.partition(-cal, j, axis=1)[:, j]
            rejections += int((rng.random(batch) > cutoff).sum())
            failures += int((1 - cutoff > ALPHA).sum())
        rate = rejections / reps
        simulated.append({'n': n, 'budget_per_law': round(budget, 6), 'index_j': j, 'reps': reps,
                          'exact_unconditional_size': round(marginal_size(j, n), 5),
                          'simulated_rejection': round(rate, 5),
                          'upper_99': round(float(stats.beta.ppf(0.99, rejections + 1, reps - rejections)), 5),
                          'certificate_failure_rate': round(failures / reps, 5)})
    return {'certifications_used': rows, 'grid_worst': {'n_range': [131, 1000000], 'points': int(grid.size),
                                                         'budgets': '0.01/k, k in 1, 2, 3, 8, 24, 100, 1000', **worst},
            'end_to_end': simulated, 'end_to_end_three_laws': multi_law_size(committed),
            'end_to_end_three_laws_seed_check': seed_check(committed, [60, 61, 62])}


def multi_law_counts(seed):
    """RC-306. The whole procedure on a class of three laws of the statistic: each law is calibrated on its own n draws,
    the cutoff is the largest of the three certified cutoffs, and a fresh draw of each law is tested against it. Per law
    it counts rejections against the class cutoff, to compare with the bound (j + 1)/(n + 1), and against that law's own
    cutoff, where the bound is exact. The laws differ in their upper tails, so the maximum binds for some and not for
    others."""
    rng = np.random.default_rng(seed)
    laws = {'normal': lambda size: rng.standard_normal(size), 'student t3': lambda size: rng.standard_t(3, size),
            'normal x 0.7': lambda size: 0.7 * rng.standard_normal(size)}
    n, reps, batch = 1000, 200000, 5000
    budget = 0.01 / len(laws)
    j = certified_index(n, budget)
    at_class = dict.fromkeys(laws, 0)
    at_own = dict.fromkeys(laws, 0)
    for _ in range(reps // batch):
        own = {name: -np.partition(-draw((batch, n)), j, axis=1)[:, j] for name, draw in laws.items()}
        cutoff = np.max(np.stack(list(own.values())), axis=0)
        for name, draw in laws.items():
            fresh = draw(batch)
            at_class[name] += int((fresh > cutoff).sum())
            at_own[name] += int((fresh > own[name]).sum())
    return {'n': n, 'budget': budget, 'index_j': j, 'reps': reps, 'at_class': at_class, 'at_own': at_own}


def multi_law_size(counts):
    """The rows of one run of multi_law_counts: per law the rejection rate against the class cutoff, with its 99 %
    upper bound, and against the law's own cutoff."""
    reps, at_class, at_own = counts['reps'], counts['at_class'], counts['at_own']
    rows = [{'law': name, 'rejection_at_class_cutoff': round(at_class[name] / reps, 5),
             'upper_99': round(float(stats.beta.ppf(0.99, at_class[name] + 1, reps - at_class[name])), 5),
             'rejection_at_own_cutoff': round(at_own[name] / reps, 5)} for name in at_class]
    return {'n': counts['n'], 'laws': len(at_class), 'budget_per_law': round(counts['budget'], 6),
            'index_j': counts['index_j'], 'reps': reps, 'bound': round(marginal_size(counts['index_j'], counts['n']), 5),
            'rows': rows}


def seed_check(committed, seeds):
    """RC-310. The three-law simulation on further seeds, one row per seed and law. Seed 59 was looked at again because
    its normal law came out 3.6 standard errors above the exact rate against its own cutoff, so a pool that includes
    it is selected; the rates against each law's own cutoff are pooled over the further seeds alone and over all four,
    each with a two-sided 99 % Clopper-Pearson interval, against the bound, which is exact there. A separate check
    draws the normal law alone on 1,600,000 repetitions from seeds that played no part in that selection."""
    runs = [multi_law_counts(seed) for seed in seeds]
    rows = [{'seed': seed, 'law': name, 'rejection_at_class_cutoff': round(run['at_class'][name] / run['reps'], 5),
             'rejection_at_own_cutoff': round(run['at_own'][name] / run['reps'], 5)}
            for seed, run in zip(seeds, runs) for name in run['at_own']]
    return {'bound': round(marginal_size(committed['index_j'], committed['n']), 5), 'rows': rows,
            'pooled_at_own_cutoff': {'seeds 60 to 62': pooled_own(runs),
                                     'seeds 59 to 62, selected': pooled_own([committed] + runs)},
            'normal_alone': normal_alone([100, 101, 102, 103], committed['n'], committed['index_j'])}


def pooled_own(runs):
    """Per law, the rejections against the law's own cutoff summed over runs, with a two-sided 99 % interval."""
    total = sum(run['reps'] for run in runs)
    pooled = []
    for name in runs[0]['at_own']:
        own = sum(run['at_own'][name] for run in runs)
        pooled.append({'law': name, 'reps': total, 'rejection_at_own_cutoff': round(own / total, 5),
                       'lower_99': round(float(stats.beta.ppf(0.005, own, total - own + 1)), 5),
                       'upper_99': round(float(stats.beta.ppf(0.995, own + 1, total - own)), 5)})
    return pooled


def normal_alone(seeds, n, j):
    """The normal law alone, calibrated on n draws and tested against its own (j + 1)-th largest draw, 400,000
    repetitions per seed, pooled, with a two-sided 99 % interval around the exact (j + 1)/(n + 1)."""
    reps, batch, rejections = 400000, 5000, 0
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for _ in range(reps // batch):
            cutoff = -np.partition(-rng.standard_normal((batch, n)), j, axis=1)[:, j]
            rejections += int((rng.standard_normal(batch) > cutoff).sum())
    total = reps * len(seeds)
    return {'seeds': seeds, 'n': n, 'index_j': j, 'reps': total, 'exact': round(marginal_size(j, n), 5),
            'simulated_rejection': round(rejections / total, 5),
            'lower_99': round(float(stats.beta.ppf(0.005, rejections, total - rejections + 1)), 5),
            'upper_99': round(float(stats.beta.ppf(0.995, rejections + 1, total - rejections)), 5)}


def selected_size(n, j, m):
    """Unconditional rejection probability when m calibration records of one law are drawn independently and the test
    is run only against the smallest of their m cutoffs (RC-309). The exceedance probability of each record's cutoff is
    Beta(j + 1, n - j), and the fresh statistic is independent of the records, so the rate is E[max of m such Betas] =
    integral over [0, 1] of 1 - F(x)^m. For m = 1 it is (j + 1)/(n + 1). For a class of several laws each record's
    cutoff is at least that law's own cutoff, so this is an upper bound there too."""
    value, _ = integrate.quad(lambda x: 1 - stats.beta.cdf(x, j + 1, n - j) ** m, 0, 1,
                              points=[(j + 1) / (n + 1)], limit=200)
    return value


def s17_record_selection():
    """RC-309. R6 forbade a second calibration record for one cohort, but not records under different cohort
    identifiers. An operator who anchors m records, reads their beacon rounds and runs only the cohort with the smallest
    cutoff tests against the minimum of m exchangeable order statistics: its size exceeds the bound (j + 1)/(n + 1) for
    every m >= 2. Reported exactly for the certifications of S16 and the three-law example, with the smallest m at
    which it exceeds alpha; checked end to end on uniform draws; and, for an operator who runs m independent cohorts and
    reports whichever rejects, 1 - (1 - b)^m with b the bound."""
    used = [('S14 minimum n, K = 8', 131, 0.01 / 8), ('three-law example', 1000, 0.01 / 3),
            ('S9, K = 8', 200000, 0.01 / 8)]
    rows = []
    for name, n, budget in used:
        j = certified_index(n, budget)
        m_star = 1
        while selected_size(n, j, m_star) <= ALPHA:
            m_star *= 2
        lo, hi = m_star // 2, m_star
        while hi - lo > 1:
            mid = (lo + hi) // 2
            lo, hi = (lo, mid) if selected_size(n, j, mid) > ALPHA else (mid, hi)
        rows.append({'certification': name, 'n': n, 'index_j': j, 'bound': round(marginal_size(j, n), 5),
                     'min_of_m_cutoffs': {str(m): round(selected_size(n, j, m), 5) for m in [1, 2, 3, 5, 10, 100]},
                     'smallest_m_above_alpha': hi,
                     'report_any_of_m': {str(m): round(1 - (1 - marginal_size(j, n)) ** m, 5) for m in [2, 3, 5]}})
    rng = np.random.default_rng(67)
    n, budget, m, reps, batch = 1000, 0.01 / 3, 5, 200000, 2000
    j = certified_index(n, budget)
    rejections = 0
    for _ in range(reps // batch):
        cutoffs = -np.partition(-rng.random((batch, m, n)), j, axis=2)[:, :, j]
        rejections += int((rng.random(batch) > cutoffs.min(axis=1)).sum())
    simulated = {'n': n, 'index_j': j, 'm': m, 'reps': reps, 'exact': round(selected_size(n, j, m), 5),
                 'simulated_rejection': round(rejections / reps, 5),
                 'lower_99': round(float(stats.beta.ppf(0.005, rejections, reps - rejections + 1)), 5),
                 'upper_99': round(float(stats.beta.ppf(0.995, rejections + 1, reps - rejections)), 5)}
    return {'rows': rows, 'end_to_end': simulated}


def s18_claim_level():
    """RC-312. R7 certified each of S_max confirmatory claims at alpha / S_max only in the final bound check, while the
    index, the certificate and the fresh-size check stayed at alpha. For each certification of S17 and each S_max the
    index chosen at alpha and the index chosen at alpha / S_max are compared on that check: the first fails it for
    every S_max >= 2 at n = 1,000 and n = 200,000, and at n = 131 it passes while its certificate states only
    exceedance <= alpha. The smallest calibration that certifies at alpha / S_max is reported. End to end, two true
    null claims, each calibrated on its own n = 1,000 uniform draws at alpha / 2, reject at least once with
    probability 1 - (1 - b)^2 <= 2 b <= alpha, b the bound of one claim."""
    used = [('S14 minimum n, K = 8', 131, 0.01 / 8), ('three-law example', 1000, 0.01 / 3),
            ('S9, K = 8', 200000, 0.01 / 8)]
    rows = []
    for name, n, budget in used:
        for s_max in [1, 2, 3, 5]:
            level = ALPHA / s_max
            j_alpha, j_level = certified_index(n, budget), certified_index(n, budget, level)
            rows.append({'certification': name, 'n': n, 's_max': s_max, 'claim_level': round(level, 5),
                         'index_at_alpha': j_alpha, 'bound_at_alpha': round(marginal_size(j_alpha, n), 5),
                         'bound_check_at_alpha': marginal_size(j_alpha, n) <= level,
                         'index_at_claim_level': j_level,
                         'bound_at_claim_level': None if j_level is None else round(marginal_size(j_level, n), 5),
                         'minimum_n_at_claim_level': minimum_calibration_size(budget, level)})
    rng = np.random.default_rng(71)
    n, budget, s_max, reps, batch = 1000, 0.01 / 3, 2, 200000, 2000
    j = certified_index(n, budget, ALPHA / s_max)
    familywise = 0
    for _ in range(reps // batch):
        cutoffs = -np.partition(-rng.random((batch, s_max, n)), j, axis=2)[:, :, j]
        familywise += int((rng.random((batch, s_max)) > cutoffs).any(axis=1).sum())
    bound = marginal_size(j, n)
    simulated = {'n': n, 's_max': s_max, 'index_j': j, 'reps': reps, 'bound_per_claim': round(bound, 5),
                 'exact_familywise': round(1 - (1 - bound) ** s_max, 5),
                 'simulated_familywise': round(familywise / reps, 5),
                 'lower_99': round(float(stats.beta.ppf(0.005, familywise, reps - familywise + 1)), 5),
                 'upper_99': round(float(stats.beta.ppf(0.995, familywise + 1, reps - familywise)), 5)}
    return {'rows': rows, 'end_to_end': simulated}


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
                ('S10 component cutoffs', s10_component_cutoffs), ('S11 weighted variance', s11_weighted_variance),
                ('S12 composite null', s12_composite_null), ('S13 family budget', s13_family_budget),
                ('S14 unattainable certification', s14_unattainable_certification),
                ('S15 within-period covariance', s15_within_period_covariance),
                ('S16 unconditional size', s16_unconditional_size),
                ('S17 record selection', s17_record_selection), ('S18 claim level', s18_claim_level)]
    print(dumps({name: section() for name, section in sections}))


if __name__ == '__main__':
    main()
