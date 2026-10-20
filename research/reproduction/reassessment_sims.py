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
- S5: power of the six-comparator intersection-union conjunction against a fixed-sequence (gatekeeping) order.
Run from the repository root in the hash-locked environment of research/reproduction/requirements.txt:
    python research/reproduction/reassessment_sims.py
Deterministic: every section uses its own fixed seed. The output is one JSON value per line, a table row per line.
"""
import json

import numpy as np
from scipy import stats

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
    """Smallest mean detected with the given power by the one-sided t test on G block means (normal block means)."""
    se = np.sqrt((tau ** 2 + sigma ** 2 / n) / g)
    return float((stats.t.ppf(1 - ALPHA, g - 1) + stats.t.ppf(power, g - 1)) * se)


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

    Anytime-valid when 1 + lam * x > 0 for every possible block mean x: lam_cap = 0.5 needs |x| <= 1, the range of a
    Brier difference; lam_cap = 2.5 needs |x| <= 0.2, which holds only if |p_FULL - p_baseline| <= 0.2 by design."""
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
    return {'block_sd': round(sigma_b, 4), 'reps': reps, 'rows': rows}


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
        for theta in [0.005, 0.01, 0.02]:
            # identified set of the population mean: (1 - m) theta_obs + m [-d, d]; sign identified iff (1-m) theta > m d
            m_max = theta / (theta + d)
            bounds.append({'divergence_bound_d': d, 'theta_observed': theta, 'max_omitted_share_for_sign': round(m_max, 4)})
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


def emit(name, value, depth=0):
    """One JSON line per table row, so that the committed output reads as tables."""
    pad = ' ' * depth
    if isinstance(value, dict) and any(isinstance(v, (list, dict)) for v in value.values()):
        print(f'{pad}{json.dumps(name)}:')
        for key, item in value.items():
            emit(key, item, depth + 1)
    elif isinstance(value, list):
        print(f'{pad}{json.dumps(name)}:')
        for item in value:
            print(f'{pad} {json.dumps(item)}')
    else:
        print(f'{pad}{json.dumps(name)}: {json.dumps(value)}')


def main():
    for name, section in [('S1 forecast law', s1_forecast_law), ('S2 power', s2_power_table), ('S3 tests', s3_tests),
                          ('S3b betting horizon', s3b_betting_horizon),
                          ('S3c bounded persistence', s3c_bounded_persistence), ('S4 selection', s4_selection),
                          ('S5 conjunction', s5_conjunction)]:
        emit(name, section())


if __name__ == '__main__':
    main()
