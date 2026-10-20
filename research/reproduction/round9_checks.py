"""Round-9 checks for the Codex findings on PR #4 at 8af2ae9 (no reference code, no network).

Reviews 5556950582 and 5558680831. Each block is keyed by the review-comment id it answers. The archived
GRAPA rule, the D1-type generator and the cluster-weighted statistic are those of 16 Appendix A, F and H.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA, LAM_MAX = 0.05, 0.5
PERIODS = 24

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

def cw_t_blocks(blocks):
    """Cluster-weighted statistic with block-sum variance (Appendix F) over a list of per-block arrays."""
    x = np.concatenate(blocks); n = x.size; g = len(blocks)
    theta = x.mean()
    dev = np.array([(b - theta).sum() for b in blocks])
    v = (dev ** 2).sum() / n ** 2 * g / (g - 1)
    return float(theta), float(theta / math.sqrt(v)) if v > 0 else 0.0, g - 1

def cw_t_many(x):
    """x: (reps, J, clusters), clusters = PERIODS * per; returns t per (rep, J)."""
    reps, j, n = x.shape
    per = n // PERIODS
    theta = x.mean(axis=2)
    dev = (x - theta[:, :, None]).reshape(reps, j, PERIODS, per).sum(axis=3)
    v = (dev ** 2).sum(axis=2) / n ** 2 * PERIODS / (PERIODS - 1)
    with np.errstate(divide='ignore', invalid='ignore'):
        return theta / np.sqrt(v)

# ================= r4301994299 (RC-93): the committed IUT null check was degenerate =================
# Appendix H set comparator 1 to delta = 0 in the generator bc = b - s sqrt(delta), which gives bc = b exactly, so
# X_1 = (b - Y)^2 - (b - Y)^2 = 0 for every cluster: zero variance, t undefined, never rejects. Reproduced, then
# replaced by a null comparator with mean-zero, non-zero-variance increments: FULL and the null comparator both
# carry a calibration error of magnitude c with independent signs, X = (b + s_c c - Y)^2 - (b + s_F c - Y)^2.
J, REPS = 6, 20000
crit = student_t.ppf(1 - ALPHA, PERIODS - 1)
r = np.random.default_rng(8399)
per = 25; n = PERIODS * per
y = (r.random((REPS, 1, n)) < 0.5).astype(float)
s = r.choice([-1.0, 1.0], size=(REPS, J, n))
deltas = np.array([0.0] + [0.08] * (J - 1))[None, :, None]
x_old = ((0.5 - s * np.sqrt(deltas)) - y) ** 2 - (0.5 - y) ** 2
rc93 = {'committed_check_comparator_1': {'max_abs_increment': float(np.abs(x_old[:, 0, :]).max()),
                                         'variance': float(x_old[:, 0, :].var()),
                                         'reading': 'every increment of the null comparator is exactly zero, so its t statistic is undefined and the conjunction can never reject; the 0 of 20,000 was mechanical'}}
def iut_null_check(c, seed):
    r_ = np.random.default_rng(seed)
    y_ = (r_.random((REPS, 1, n)) < 0.5).astype(float)
    s_full = r_.choice([-1.0, 1.0], size=(REPS, 1, n))
    s_c = r_.choice([-1.0, 1.0], size=(REPS, J, n))
    p_full = 0.5 + s_full * c
    bc = np.empty((REPS, J, n))
    bc[:, 0:1, :] = 0.5 + s_c[:, 0:1, :] * c                       # null comparator: same error magnitude, independent sign
    bc[:, 1:, :] = 0.5 - s_c[:, 1:, :] * math.sqrt(0.08)           # the others at delta = 0.08 against a calibrated FULL
    x = (bc - y_) ** 2 - (p_full - y_) ** 2
    x[:, 1:, :] = ((bc[:, 1:, :] - y_) ** 2 - (0.5 - y_) ** 2)
    tt = cw_t_many(x)
    rej = tt > crit
    k1 = int(rej[:, 0].sum()); k_iut = int(rej.all(axis=1).sum())
    return {'c': c, 'null_comparator_mean_increment': round(float(x[:, 0, :].mean()), 5),
            'null_comparator_increment_variance': round(float(x[:, 0, :].var()), 5),
            'null_comparator_marginal_rejections': k1, 'null_comparator_rate': round(k1 / REPS, 4),
            'iut_rejections': k_iut, 'iut_rate': round(k_iut / REPS, 4),
            'iut_99pct_upper': round(binom_upper(k_iut, REPS, 0.99), 4),
            'within_A3_bound_0.06': binom_upper(k_iut, REPS, 0.99) <= 0.06}
rc93['non_degenerate_null_checks'] = [iut_null_check(0.1, 9301), iut_null_check(0.2, 9302)]
rc93['reading'] = 'with a null comparator whose increments have mean zero and positive variance the IUT rejects at about the nominal rate, which is the least-favourable size check T-13 (b) and T-16 require; the committed check is withdrawn'
out['RC93_iut_non_degenerate_null'] = rc93

# ================= r4303397714 (RC-102): 140 or 141 blocks =================
rc102 = {}
for G_ in (140, 141):
    rc102[f'bound_at_delta_0.02_G={G_}'] = round(ALPHA * 1.02 ** G_, 6)
rc102['ceil_log_16_over_log_1.02'] = math.ceil(math.log(0.80 / ALPHA) / math.log(1.02))
rc102['reading'] = 'the bound reaches 0.80 at 141 blocks (0.799823 at 140); the Appendix H sentence string was hand-typed as 140 and is corrected to the computed value'
out['RC102_blocks_needed'] = rc102

# ================= r4303397684 (RC-95): order in which increments enter the monitor =================
# (a) Codex's two-cluster example. A knowable at 10, closes at 30, X_A fair in {-1, +1}; B knowable and closes at
# 20, X_B fair given X_A = +1 and X_B = -1 given X_A = -1. lambda_A = 0.5 frozen. Closure order applies B then A.
rc95 = {}
pa = {(+1, +1): 0.25, (+1, -1): 0.25, (-1, -1): 0.5}   # (X_A, X_B) joint law
e_xb_given_xa = {xa: sum(p * xb for (a, xb), p in pa.items() if a == xa) / sum(p for (a, _), p in pa.items() if a == xa) for xa in (+1, -1)}
e_fac_a_given_xb_plus = sum(p * (1 + 0.5 * a) for (a, xb), p in pa.items() if xb == +1) / sum(p for (_, xb), p in pa.items() if xb == +1)
rc95['codex_example'] = {'E[X_A]': 0.0, 'E[X_B|X_A=+1]': e_xb_given_xa[+1], 'E[X_B|X_A=-1]': e_xb_given_xa[-1],
                         'conditional_null_in_knowable_order_holds': True,
                         'E[1+0.5 X_A | X_B=+1]_closure_order': e_fac_a_given_xb_plus,
                         'reading': 'in closure order the factor for A has conditional expectation 1.5 after B is seen, so the closure-ordered wealth is not a supermartingale; Codex is right that closure order carries no Ville guarantee'}
# (b) Does the running maximum actually exceed alpha? Not with a single late cluster and a fixed lambda (the final
# product has expectation <= 1, so P(final >= 20) <= alpha, and the B-prefix is a supermartingale given X_A). The
# channel that inflates it is outcome-dependent timing: for an eventually-by-deadline predicate a YES is knowable
# at the occurrence and a NO only at logical finality, so both closure order and knowable order place YES clusters
# earlier than NO clusters. Toy: 120 clusters registered one per interval, X_k = +c (YES) or -c (NO) fair,
# lambda = 0.5 fixed; a YES closes 1 interval after registration, a NO 6 intervals after (finality). Three orders:
# closure (knowable) order, registration order, and pre-registered maturity order H_k = registration + 6, which is
# outcome-independent.
R = 20000; N = 120; c = 0.5; lam = 0.5
def running_max_cross(xs, order_key):
    idx = np.argsort(order_key, axis=1, kind='stable')
    xo = np.take_along_axis(xs, idx, axis=1)
    w = np.cumprod(1 + lam * xo, axis=1)
    return float((w.max(axis=1) >= 1 / ALPHA).mean()), float((w[:, -1] >= 1 / ALPHA).mean())
toy = {}
for lag in (6, 12, 24, 120):
    rng = np.random.default_rng(9500 + lag)
    x = np.where(rng.random((R, N)) < 0.5, c, -c)
    reg = np.arange(N)[None, :].repeat(R, 0)
    close = reg + np.where(x > 0, 1, lag)
    cross_close, final_close = running_max_cross(x, close)
    cross_mat, final_mat = running_max_cross(x, reg + lag)
    toy[f'NO_closes_{lag}_intervals_after_registration'] = {
        'closure_or_knowable_order_running_max_crossing': round(cross_close, 4),
        'closure_order_99pct_lower': round(binom_lower(int(round(cross_close * R)), R, 0.99), 4),
        'pre_registered_maturity_order_running_max_crossing': round(cross_mat, 4),
        'maturity_order_99pct_upper': round(binom_upper(int(round(cross_mat * R)), R, 0.99), 4),
        'final_product_crossing_(order_free)': round(final_close, 4)}
worst = max(v['closure_or_knowable_order_running_max_crossing'] for v in toy.values())
rc95['outcome_dependent_timing_toy'] = {
    'design': '120 fair clusters registered one per interval, X = +/-0.5, lambda = 0.5 fixed; a YES closes 1 interval after registration, a NO only at its finality, lag intervals after; running maximum over the ordered partial products, 20,000 paths',
    'cells': toy, 'ville_bound': ALPHA,
    'reading': f'ordering by closure time (or by outcome-knowable time, which coincides with it here) places early-resolving YES clusters before late-resolving NO clusters; the running maximum then crosses 1/alpha in up to {worst:.1%} of paths against a Ville bound of 5 %, while the final product and the pre-registered maturity order H_k (deadline + latency window, known at registration) stay within the bound. The monitor therefore applies increments in H_k order and buffers a closed cluster until every cluster with a smaller H_k is final; knowable order is not a sufficient remedy because knowable_at is itself outcome-dependent for eventually-by-deadline predicates'}
out['RC95_monitor_order'] = rc95

# ================= r4303397708 (RC-101): the conjunction power bound without positive association =================
rc101 = {}
p = 0.8
rc101['six_components_at_0.8'] = {'product_of_marginals': round(p ** J, 4), 'frechet_lower_bound': max(0.0, J * p - (J - 1)),
                                  'frechet_upper_bound_(min)': p}
# Explicit joint law with every marginal power 0.8 and joint power 0: five of the six failure events partition the
# sample space (0.2 each) and the sixth coincides with one of them.
rng = np.random.default_rng(9101)
u = rng.random(200000)
fail = np.stack([(u >= 0.2 * j) & (u < 0.2 * (j + 1)) for j in range(5)] + [(u >= 0.0) & (u < 0.2)], axis=1)
rej = ~fail
rc101['explicit_construction'] = {'marginal_powers_mc': [round(float(v), 4) for v in rej.mean(axis=0)], 'joint_power_mc': float(rej.all(axis=1).mean()),
                                  'reading': 'six tests with 80 % power each and zero joint power; the statement that IUT power lies between the product of marginals and the smallest marginal is false without positive association'}
# IUT under negatively dependent comparator errors in the Appendix H generator: comparators in three pairs with
# opposite signs, so that within a pair X_c + X_c' = 2 delta (perfectly anti-correlated noise).
def iut_power_pairs(b, delta, per, seed, anti):
    r_ = np.random.default_rng(seed)
    n_ = PERIODS * per
    y_ = (r_.random((REPS, 1, n_)) < b).astype(float)
    own = r_.choice([-1.0, 1.0], size=(REPS, 3, n_))
    s_ = np.concatenate([own, -own if anti else r_.choice([-1.0, 1.0], size=(REPS, 3, n_))], axis=1)
    bc = b - s_ * math.sqrt(delta)
    x_ = (bc - y_) ** 2 - (b - y_) ** 2
    rej_ = cw_t_many(x_) > crit
    return float(rej_.mean(axis=0).mean()), float(rej_.all(axis=1).mean())
cells = {}
for delta, per in ((0.01, 25), (0.01, 50), (0.02, 25)):
    m_ind, j_ind = iut_power_pairs(0.5, delta, per, 9110 + per + int(delta * 1000), False)
    m_anti, j_anti = iut_power_pairs(0.5, delta, per, 9110 + per + int(delta * 1000), True)
    cells[f'delta={delta},clusters={PERIODS * per}'] = {
        'independent_signs': {'mean_marginal': round(m_ind, 4), 'iut_joint': round(j_ind, 4), 'product': round(m_ind ** J, 4)},
        'three_anti_correlated_pairs': {'mean_marginal': round(m_anti, 4), 'iut_joint': round(j_anti, 4), 'product': round(m_anti ** J, 4),
                                        'frechet_lower': round(max(0.0, J * m_anti - (J - 1)), 4)}}
rc101['appendix_H_generator_with_anti_correlated_pairs'] = cells
rc101['reading'] = 'with anti-correlated comparator errors the conjunction power falls below the product of the marginals; the design is powered under a pre-registered dependence assumption (OD4) or under the Frechet lower bound, and T-16 carries a negatively dependent generator'
out['RC101_conjunction_power_negative_dependence'] = rc101

# ================= r4303397692 (RC-97): empty calendar blocks =================
# Valid null, Poisson supply with mean m per period and zeros allowed; two conventions for the block-sum variance:
# (i) G = 24 and 23 df with empty blocks contributing zero, (ii) G = number of occupied blocks and G - 1 df.
def increments_null(k, rng_):
    # Appendix F's valid null: X = 0.4 Y - 0.2 with Y ~ Bern(0.5), so X in {-0.2, +0.2} with mean zero.
    y_ = (rng_.random(k) < 0.5).astype(float)
    return 0.4 * y_ - 0.2
def sim_empty(m, seed, reps=10000):
    rng_ = np.random.default_rng(seed)
    rej_all = np.zeros(reps, bool); rej_occ = np.zeros(reps, bool); occ = np.zeros(reps, int)
    for i in range(reps):
        sizes = rng_.poisson(m, size=PERIODS)
        blocks = [increments_null(k, rng_) for k in sizes if k > 0]
        if len(blocks) < 2:
            continue
        xall = np.concatenate(blocks); nn = xall.size; theta = xall.mean()
        dev = np.array([(b - theta).sum() for b in blocks])
        g = len(blocks); occ[i] = g
        v_all = (dev ** 2).sum() / nn ** 2 * PERIODS / (PERIODS - 1)
        v_occ = (dev ** 2).sum() / nn ** 2 * g / (g - 1)
        rej_all[i] = theta / math.sqrt(v_all) > student_t.ppf(1 - ALPHA, PERIODS - 1) if v_all > 0 else False
        rej_occ[i] = theta / math.sqrt(v_occ) > student_t.ppf(1 - ALPHA, g - 1) if v_occ > 0 else False
    return {'mean_supply_per_period': m, 'mean_occupied_blocks': round(float(occ.mean()), 2), 'min_occupied_blocks': int(occ[occ > 0].min()),
            'size_G24_df23_empty_blocks_counted': round(float(rej_all.mean()), 4), '99pct_upper_G24': round(binom_upper(int(rej_all.sum()), reps, 0.99), 4),
            'size_G_occupied_df_occupied_minus_1': round(float(rej_occ.mean()), 4), '99pct_upper_occ': round(binom_upper(int(rej_occ.sum()), reps, 0.99), 4)}
rc97 = {'poisson_mean_1': sim_empty(1.0, 9701), 'poisson_mean_0.5': sim_empty(0.5, 9702), 'poisson_mean_2': sim_empty(2.0, 9703)}
rc97['reading'] = 'counting empty periods in G and the degrees of freedom is anti-conservative when many periods are empty; the contract counts occupied blocks only, pre-registers a minimum number of occupied blocks, and T-12 adds zero-supply periods'
out['RC97_empty_blocks'] = rc97

# ================= r4303397680 (RC-94): calibrating the critical value over a pre-registered null class =================
# Two-point block-mean family: block mean +a with probability 1 - eps, -b with probability eps, mean zero, b = 0.9.
# The one-sided t over 24 blocks depends only on the number k of positive blocks; exact size by the binomial. A
# sample with zero variance (every block equal) never rejects, as in Appendix G; the alternative convention (t = +inf
# when every block is positive) makes the size at eps = 0.02 equal to 0.98^24 = 0.62 and no calibration possible.
def t_of_k(k, a, b, G=24):
    # Zero-variance samples (k = 0 or k = G) never reject: the convention of Appendix G, now stated in 17 (T-36).
    vals = np.array([a] * k + [-b] * (G - k))
    if k in (0, G):
        return -np.inf
    return float(vals.mean() / (vals.std(ddof=1) / math.sqrt(G)))
_tk = {}
def exact_size(eps, c, b=0.9, G=24):
    key = (eps, b, G)
    if key not in _tk:
        a = eps * b / (1 - eps)
        _tk[key] = (np.array([t_of_k(k, a, b, G) for k in range(G + 1)]), binom.pmf(np.arange(G + 1), G, 1 - eps))
    tk, pk = _tk[key]
    return float(pk[tk > c].sum())
eps_grid = np.round(np.arange(0.02, 0.501, 0.005), 3)
sizes_nominal = {f'eps={e}': round(exact_size(e, crit), 4) for e in (0.02, 0.05, 0.1, 0.2, 0.3, 0.5)}
rc94 = {'exact_size_at_nominal_crit_1.7139_by_catastrophe_probability': sizes_nominal,
        'sup_size_over_eps_in_[0.02,0.5]_at_nominal_crit': round(max(exact_size(e, crit) for e in eps_grid), 4)}
def calibrated_crit(eps_min):
    grid = [e for e in eps_grid if e >= eps_min]
    for c in np.arange(crit, 30.0, 0.001):
        if max(exact_size(e, c) for e in grid) <= ALPHA:
            return float(round(c, 3))
    return None
cal = {}
for eps_min in (0.05, 0.1, 0.2, 0.3):
    c_star = calibrated_crit(eps_min)
    # Power at the calibrated critical value on the D1-type alternative (b = 0.5, delta = 0.02, 600 and 1,200 clusters).
    pw = {}
    for per_ in (25, 50):
        r_ = np.random.default_rng(9400 + per_ + int(eps_min * 100))
        n_ = PERIODS * per_
        y_ = (r_.random((REPS, 1, n_)) < 0.5).astype(float)
        s_ = r_.choice([-1.0, 1.0], size=(REPS, 1, n_))
        x_ = ((0.5 - s_ * math.sqrt(0.02)) - y_) ** 2 - (0.5 - y_) ** 2
        tt = cw_t_many(x_)[:, 0]
        pw[f'clusters={n_}'] = {'power_at_nominal_crit': round(float((tt > crit).mean()), 4), 'power_at_calibrated_crit': (round(float((tt > c_star).mean()), 4) if c_star is not None else 'no critical value below 30 holds size')}
    cal[f'catastrophe_share_at_least_{eps_min}'] = {'calibrated_crit': c_star, 'sup_size_at_calibrated_crit': (round(max(exact_size(e, c_star) for e in eps_grid if e >= eps_min), 4) if c_star is not None else None), 'power_delta_0.02': pw}
rc94['calibrated_critical_value_by_null_class'] = cal
rc94['reading'] = 'a null class defined by a lower bound on the catastrophe share can be calibrated exactly: the critical value is the smallest value whose worst-case size over the class is at most alpha, and power is restated at that value; the wider the class (the smaller eps_min), the larger the critical value and the lower the power at a given supply, which is the RC-80 bound seen from the null side; OD4 chooses the class from reference-class history and the contract reports the calibrated value and the power at it, so the nominal 5 % claim holds over the whole pre-registered class and not only on the families with no pass condition'
out['RC94_null_class_calibration'] = rc94

# ================= r4303397703 (RC-100): cumulative clock drift =================
tol = 2.0
rc100 = {}
for rule in ('per_check', 'baseline'):
    wall, mono = 0.0, 0.0; base = wall - mono; last = base; expiry = 60.0; log = []; admitted_after_real_expiry = 0
    for i in range(100):
        mono += 1.0; wall += 1.0 - 0.75           # the attacker slews the wall clock by -0.75 s per check, below tolerance
        off = wall - mono
        ok = abs(off - (last if rule == 'per_check' else base)) <= tol
        last = off
        if not ok:
            log.append(f'check {i + 1}: discontinuity, offset {off:+.2f}'); break
        if mono > expiry and wall <= expiry:
            admitted_after_real_expiry += 1
    rc100[rule] = {'checks_run': i + 1, 'final_wall': round(wall, 2), 'final_monotonic': round(mono, 2), 'cumulative_offset': round(wall - mono, 2),
                   'admissions_after_real_expiry_of_a_capability_expiring_at_60': admitted_after_real_expiry, 'log': log}
rc100['reading'] = 'per-check drift lets a sequence of small slews keep an expired capability valid; comparing the offset to the baseline persisted at the epoch start detects it at the first check whose cumulative offset exceeds the tolerance'
out['RC100_clock_drift'] = rc100

# ================= r4303397718 (RC-103): epoch rotation on demotion =================
def gate_run(rotate_on_demotion):
    epoch = 1; consumed = set(); state = 'RESEARCH_ONLY'; log = []
    caps = {'A': {'epoch': 1, 'nonce': 'a'}, 'B': {'epoch': 1, 'nonce': 'b'}}
    def present(name):
        nonlocal state
        cap = caps[name]
        if cap['epoch'] != epoch: log.append(f'{name}: rejected stale epoch'); return
        if cap['nonce'] in consumed: log.append(f'{name}: rejected consumed nonce'); return
        consumed.add(cap['nonce']); state = 'SIM_READ_ONLY'; log.append(f'{name}: promoted')
    present('A')
    state = 'RESEARCH_ONLY'; log.append('demoted')
    if rotate_on_demotion:
        epoch += 1; log.append(f'epoch rotated to {epoch} and anchored')
    present('B')
    return {'final_state': state, 'log': log}
rc103 = {'v6_rule': gate_run(False), 'v7_rule_rotate_on_demotion': gate_run(True),
         'reading': 'an unused capability signed before the demotion re-promotes the gate under the version-6 rule; rotating and anchoring the epoch on every demotion makes it stale'}
out['RC103_epoch_on_demotion'] = rc103

# ================= r4303397689 (RC-96): forecaster version in the slot key =================
# Two versions of the same forecaster submit to the default slot; an implementation that admits both and scores
# the better one after the outcome reproduces the RC-75 channel. Honest null: both versions draw p from the same
# calibrated law, Y ~ Bern(0.5), baseline 0.5.
rng = np.random.default_rng(9601)
Rn = 200000
yv = (rng.random(Rn) < 0.5).astype(float)
p1 = np.clip(0.5 + 0.2 * rng.standard_normal(Rn), 0.01, 0.99)
p2 = np.clip(0.5 + 0.2 * rng.standard_normal(Rn), 0.01, 0.99)
x1 = (0.5 - yv) ** 2 - (p1 - yv) ** 2
x2 = (0.5 - yv) ** 2 - (p2 - yv) ** 2
rc96 = {'expected_increment_version_fixed_in_advance': round(float(x1.mean()), 4),
        'expected_increment_better_version_chosen_after_outcome': round(float(np.maximum(x1, x2).mean()), 4),
        'reading': 'a slot key that includes the forecaster version admits two records per slot and re-opens outcome-dependent selection; the key is (event, arm, slot) and the version is pre-registered per arm'}
out['RC96_version_in_slot_key'] = rc96

# ================= r4301994294 (RC-92), r4303397725 (RC-104), r4301994282 (RC-88), r4303397727 (RC-105): deterministic fixtures =================
rc_det = {}
# RC-92: member 1 adjudicated VOID at 10 (timestamp-less record), member 2 resolves at 20; forecast on member 2 at 15.
t_star_v6 = min([20]); t_star_v7 = min([10, 20])
rc_det['RC92_t_star_with_adjudicated_void'] = {'t_star_v6_scored_members_only': t_star_v6, 't_star_v7_all_members': t_star_v7,
                                                'forecast_at_15_eligible_v6': 15 < t_star_v6, 'forecast_at_15_eligible_v7': 15 < t_star_v7}
# RC-104: member resolves YES at 30; FULL's only submission at 31 (after publication at 30); issuance close t_close = 20.
rc_det['RC104_missing_arm'] = {'v6': 'member has Y but FULL is not scored; neither pre-declared nor adjudicated VOID; cluster never closes',
                                'v7': 'at t_close = 20 the FULL slot is empty: FULL abstains, scored at the baseline forecast (X = 0 for the member), reported separately; the 31 submission is labelled late; if the baseline arm is empty at t_close the member is adjudicated VOID at t_close (outcome-independent, under the cap, imputed +/-1)'}
# RC-88 and RC-105: deadline 100, latency window 10. Four records.
cases = {'published_105_received_118_(registry_outage)': {'v6': 'VOID (receipt after deadline + window)', 'v7': 'YES (publication 105 <= 110); receipt lag logged as an integrity incident'},
         'published_112_received_113_(source_late)': {'v6': 'NO at 110 by finality, then the text also says VOID: inconsistent', 'v7': 'NO at 110 is immutable; the 112 report is a source-latency defect logged against the source; never YES, never VOID'},
         'no_record_observed_at_110_living_source': {'v6': 'NO at 110', 'v7': 'NO at 110, requires an archived observation of absence at or after 110'},
         'no_record_source_defunct_at_110': {'v6': 'adjudicated VOID', 'v7': 'adjudicated VOID (unchanged)'}}
rc_det['RC88_RC105_finality_dispositions'] = cases
out['deterministic_fixtures'] = rc_det

out['python'] = sys.version.split()[0]
json.dump(out, sys.stdout, indent=2)
print()
