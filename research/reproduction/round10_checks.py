"""Round-10 checks for the Codex findings on PR #4 at 922956b (no reference code, no network).

Review 5558887072. Each block is keyed by the review-comment id it answers. The cluster-weighted statistic with
block-sum variance, the D1-type generator and the two-point calibration are those of 16 Appendix F, H and J.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA = 0.05
PERIODS = 24
CRIT = float(student_t.ppf(1 - ALPHA, PERIODS - 1))        # nominal one-sided critical value on 23 df, 1.7139

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

def cw_t_many(x):
    """x: (reps, clusters) with clusters = PERIODS * per, blocks of one period; cluster-weighted statistic, block-sum
    variance on G - 1 df (16 Appendix F). A zero-variance sample returns -inf (never rejects; Appendix G convention)."""
    reps, n = x.shape
    per = n // PERIODS
    theta = x.mean(axis=1)
    dev = (x - theta[:, None]).reshape(reps, PERIODS, per).sum(axis=2)
    v = (dev ** 2).sum(axis=1) / n ** 2 * PERIODS / (PERIODS - 1)
    tt = np.full(reps, -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt

def cw_t_masked(x, keep):
    """Same statistic over the kept clusters only; blocks = periods, G = occupied blocks (RC-97). x, keep: (reps, n)."""
    reps, n = x.shape
    per = n // PERIODS
    k = keep.astype(float)
    nk = k.sum(axis=1)
    theta = (x * k).sum(axis=1) / nk
    dev = ((x - theta[:, None]) * k).reshape(reps, PERIODS, per).sum(axis=2)
    occ = (k.reshape(reps, PERIODS, per).sum(axis=2) > 0)
    g = occ.sum(axis=1)
    v = (dev ** 2).sum(axis=1) / nk ** 2 * g / (g - 1)
    tt = np.full(reps, -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt, g

# ---- the two-point calibration of Appendix J (RC-94), repeated so that this script stands alone ----
def t_of_k(k, a, b, G=24):
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
def calibrated_crit(eps_min):
    grid = [e for e in eps_grid if e >= eps_min]
    for c in np.arange(CRIT, 30.0, 0.001):
        if max(exact_size(e, c) for e in grid) <= ALPHA:
            return float(round(c, 3))
    return None
CSTAR = {eps_min: calibrated_crit(eps_min) for eps_min in (0.05, 0.2, 0.3)}
CRITS = {'nominal_1.7139': CRIT, **{f'c*_eps_min_{e}': c for e, c in CSTAR.items()}}

# ================= r4303569704 (RC-108): the four scalars do not define the null class =================
# A law that satisfies every scalar of the version-7 class (block length one period, |p_FULL - p_baseline| = 0.2
# under any d_max >= 0.2, shock amplitude 0.3, no rare-catastrophe shape) and is still oversized at every c*
# calibrated on the two-point family: the persistent two-state regime of Appendix D. q_t = 0.5 + 0.3 s_t, s_t a
# two-state chain with P(stay) = rho, Y ~ Bern(q_t) per cluster, baseline 0.4, FULL 0.6, X = 0.4 Y - 0.2 (E X = 0
# under the stationary law). Serial dependence is the parameter the version-7 scalars do not carry.
def regime_sizes(rho, per, reps, seed):
    r = np.random.default_rng(seed)
    n = PERIODS * per
    s = np.empty((reps, PERIODS))
    s[:, 0] = r.choice([-1.0, 1.0], size=reps)
    flip = r.random((reps, PERIODS - 1)) >= rho
    for t in range(1, PERIODS):
        s[:, t] = np.where(flip[:, t - 1], -s[:, t - 1], s[:, t - 1])
    q = 0.5 + 0.3 * np.repeat(s, per, axis=1)
    y = (r.random((reps, n)) < q).astype(float)
    x = 0.4 * y - 0.2
    tt = cw_t_many(x)
    return {name: round(float((tt > c).mean()), 4) for name, c in CRITS.items()}
rc108 = {'calibrated_crit_two_point_family': {f'eps_min_{e}': c for e, c in CSTAR.items()},
         'scalars_of_the_law': {'block_length_periods': 1, 'abs_p_full_minus_p_baseline': 0.2, 'shock_amplitude': 0.3,
                                'catastrophe_share': 'not a two-point shape; symmetric +/-0.3 periods', 'supply_shock_dependence': 'none'}}
rc108['size_by_persistence_120_clusters'] = {f'P(stay)={rho}': regime_sizes(rho, 5, 20000, 10800 + int(rho * 100)) for rho in (0.5, 0.7, 0.8, 0.9, 0.95)}
rc108['size_by_persistence_600_clusters'] = {f'P(stay)={rho}': regime_sizes(rho, 25, 10000, 10850 + int(rho * 100)) for rho in (0.5, 0.9)}
rc108['reading'] = ('P(stay) = 0.5 is the independent-period family (size at the nominal value within the bound, as in Appendix D); '
                    'the same four scalars with P(stay) = 0.9 give a law outside every bound at every calibrated c*, and raising the '
                    'supply does not help, because the dependence is between blocks and not within them. The class N must therefore '
                    'be a complete generator family whose parameters include the serial dependence of the block shocks (and the '
                    'supply-shock dependence of Appendix F), with a pre-registered box, and the worst case is taken over a grid of that '
                    'box; four scalars admit laws on which the calibrated critical value is not level alpha')
out['RC108_null_class_incomplete'] = rc108

# ================= r4303569710 (RC-109): an empty baseline slot selects the scored cohort =================
# (a) non-adversarial: two event types; FULL has +delta on type A and -delta on type B (average exactly zero); the
# baseline process fails on a fraction f of type B members (no reference class available). Version 7 adjudicates
# such a member VOID at t_close, so it leaves the primary; version 8 fills the slot from the committed reference
# base rate, so it stays. Null generator per member: Y ~ Bern(0.5); type A: baseline 0.5 +/- sqrt(delta), FULL 0.5;
# type B: baseline 0.5, FULL 0.5 +/- sqrt(delta). 600 singleton clusters, 25 per period.
def selection_check(delta, f_fail_B, reps, seed):
    r = np.random.default_rng(seed)
    per = 25; n = PERIODS * per
    y = (r.random((reps, n)) < 0.5).astype(float)
    s = r.choice([-1.0, 1.0], size=(reps, n))
    is_A = r.random((reps, n)) < 0.5
    x_A = ((0.5 + s * math.sqrt(delta)) - y) ** 2 - (0.5 - y) ** 2          # E = +delta
    x_B = (0.5 - y) ** 2 - ((0.5 + s * math.sqrt(delta)) - y) ** 2          # E = -delta
    x = np.where(is_A, x_A, x_B)
    fail = (~is_A) & (r.random((reps, n)) < f_fail_B)
    keep = ~fail
    t_full = cw_t_many(x)
    t_cc, g = cw_t_masked(x, keep)
    return {'delta': delta, 'baseline_failure_rate_on_type_B': f_fail_B, 'overall_void_share': round(float(fail.mean()), 4),
            'mean_increment_all_members': round(float(x.mean()), 5),
            'mean_increment_complete_cases_v7': round(float((x * keep).sum() / keep.sum()), 5),
            'arithmetic_expected_complete_case_mean': round(delta * (0.5 - 0.5 * (1 - f_fail_B)) / (0.5 + 0.5 * (1 - f_fail_B)), 5),
            'rejection_rate_v7_member_removed': round(float((t_cc > CRIT).mean()), 4),
            'rejection_rate_v8_member_kept': round(float((t_full > CRIT).mean()), 4),
            'rejection_rate_v7_99pct_upper': round(binom_upper(int((t_cc > CRIT).sum()), reps, 0.99), 4)}
rc109 = {'non_adversarial_selection': [selection_check(0.1, 0.1, 20000, 10901), selection_check(0.1, 0.4, 20000, 10902),
                                        selection_check(0.02, 0.4, 20000, 10903)]}
# (b) the asymmetry: under version 7 an empty FULL or comparator slot keeps the member (X = 0 for that comparison)
# while an empty baseline slot removes it; the two dispositions of one fixture member under each version.
rc109['disposition_asymmetry_v7'] = {'empty_FULL_slot_at_t_close': 'member kept, FULL scored at the baseline forecast, X = 0',
                                      'empty_comparator_slot_at_t_close': 'member kept, comparator scored at the baseline forecast',
                                      'empty_baseline_slot_at_t_close': 'member adjudicated VOID, leaves the primary (under the cap)'}
rc109['v8_rule'] = {'baseline_primary_slot': 'computed by the registry from the Design C base rate committed in the ledger before the issuance window opens (RC-106 reference data); there is no baseline submission and the slot cannot be empty; a member whose reference class has no committed base rate is refused at registration, before any forecast (candidate log)',
                    'sealing': 'no arm is served another arm\'s forecast on a member before t_close; forecasts are sealed commitments until the window closes',
                    'other_arms': 'an empty FULL or comparator slot is an abstention scored at the baseline forecast, counted per arm against a pre-registered abstention cap; no empty slot of any arm removes a member from the primary'}
rc109['reading'] = ('a baseline failure correlated with event type turns a zero-average null into a positive complete-case mean (arithmetic: '
                    'delta (1 - (1 - f)) / (1 + (1 - f)) over equal type shares) and inflates the primary rejection rate; keeping the member '
                    'with the committed base rate in the baseline slot restores the nominal rate; the adversarial version is RC-85 (Appendix I) '
                    'with the baseline process as the selecting party and needs no new simulation')
out['RC109_baseline_slot_selection'] = rc109

# ================= r4303569715 (RC-110): a burn-in YES can be public before the freeze =================
rc110 = {'fixture': {'freeze_recorded_at': 100, 'burn_in_event': {'registered_at': 50, 'not_before': 60, 'deadline': 130, 'latency_window': 10,
                                                                  'maturity_deadline_plus_window': 140, 'public_occurrence_at': 90}},
         'v7_T37_check_maturity_after_freeze': 140 > 100, 'knowable_at_by_occurrence': 90, 'knowable_before_freeze': 90 < 100,
         'v8_T37_check_not_before_after_freeze': 60 > 100,
         'terminal_falsifier_variant': {'registered_at': 50, 'not_before': 110, 'falsifier_observable_from': 50, 'falsifier_public_at': 80,
                                        'v8_not_before_check_alone': 110 > 100, 'knowable_at': 80, 'knowable_before_freeze': True,
                                        'v8_rule': 'the registration requires the EventSpec\'s earliest-knowable bound (min of not_before and the earliest time a terminal falsifier can be observed) to be after the freeze'},
         'reading': 'the version-7 condition bounds the latest finality time and not the earliest knowable time; for an eventually-by-deadline predicate the two differ by the whole resolution window, and for a terminal-falsifier predicate by more'}
out['RC110_burn_in_early_yes'] = rc110

# ================= r4303569722 (RC-111): the T-36 (b) oracle requires rejection at the nominal value =================
blocks = np.array([0.05, 0.10, 0.00, 0.05])
t_b = float(blocks.mean() / (blocks.std(ddof=1) / 2.0))
rc111 = {'oracle_statistic_t': round(t_b, 6), 'df': 3, 'decision_by_critical_value': {name: bool(t_b > c) for name, c in CRITS.items()},
         'nominal_crit_3df': round(float(student_t.ppf(0.95, 3)), 4)}
rc111['note_on_df'] = 'the version-7 oracle compares a 3-df statistic with the 3-df nominal value (2.3534) and rejects; a calibrated c* is a property of the pre-registered class at the design\'s G and is not a function of df, so the decision oracle must take c* as a parameter and the statistic oracle must be df-free'
# (c) the T-36 positive-control alternative restated at the calibrated value: Appendix E's D1 generator, b = 0.5,
# delta = 0.08, 120 independent clusters, five per period, p = b +/- sqrt(delta), Y ~ Bern(p), X = (b - Y)^2 - (p - Y)^2.
r = np.random.default_rng(11100)
reps = 20000; per = 5; n = PERIODS * per
p = 0.5 + math.sqrt(0.08) * r.choice([-1.0, 1.0], size=(reps, n))
y = (r.random((reps, n)) < p).astype(float)
x = (0.5 - y) ** 2 - (p - y) ** 2
tt = cw_t_many(x)
pc = {}
for name, c in CRITS.items():
    k = int((tt > c).sum())
    pc[name] = {'rejection_rate': round(k / reps, 4), 'exact_99pct_lower_bound': round(binom_lower(k, reps, 0.99), 4)}
rc111['positive_control_b_0.5_delta_0.08_120_clusters_appendix_E_generator'] = pc
rc111['reading'] = 'a correct implementation of the calibrated test fails the version-7 oracle whenever c* exceeds the oracle statistic; T-36 (b) becomes a statistic oracle (value and p to 1e-6) plus a decision oracle parametrised by c*, and the (c) lower bound is restated per c* from the rates above'
out['RC111_T36_oracle_at_cstar'] = rc111

# ================= r4303569729 (RC-112): a cutoff corrected after outcomes selects the cohort by date =================
# Null: 600 singleton clusters registered 25 per month over 24 months; FULL and baseline both carry a calibration
# error of magnitude 0.2 with independent signs (mean-zero, positive-variance increments). A later "correction" of
# the arm's cutoff to month m excludes every member with not_before <= m (the version-7 F-27 path); the actor chooses
# m in {0, ..., 12} after the outcomes are known. Rejection rate at the nominal value over the occupied blocks.
r = np.random.default_rng(11200)
reps = 20000; per = 25; n = PERIODS * per
y = (r.random((reps, n)) < 0.5).astype(float)
sf = r.choice([-1.0, 1.0], size=(reps, n)); sb = r.choice([-1.0, 1.0], size=(reps, n))
x = ((0.5 + 0.2 * sb) - y) ** 2 - ((0.5 + 0.2 * sf) - y) ** 2
month = np.tile(np.repeat(np.arange(PERIODS), per), (reps, 1))
best_t = np.full(reps, -np.inf); best_m = np.zeros(reps, dtype=int)
t_by_m = {}
for m in range(0, 13):
    keep = month >= m
    tt, g = cw_t_masked(x, keep)
    t_by_m[m] = tt
    better = tt > best_t
    best_t = np.where(better, tt, best_t); best_m = np.where(better, m, best_m)
rc112 = {'no_correction_rejection_rate': round(float((t_by_m[0] > CRIT).mean()), 4),
         'rejection_rate_with_outcome_chosen_correction_month': round(float((best_t > CRIT).mean()), 4),
         'rejection_rate_99pct_upper': round(binom_upper(int((best_t > CRIT).sum()), reps, 0.99), 4),
         'mean_chosen_month': round(float(best_m.mean()), 3),
         'share_of_cohort_removed_at_mean_month': round(float(best_m.mean()) / PERIODS, 3),
         'v8_rule': 'the cutoff is one immutable field of the arm version record, created before any event is registered under it; a Forecast references the arm version and carries no cutoff of its own; a correction withdraws the arm version and every member registered under it leaves the primary for every comparison involving that arm as one cohort (counted against the cap, imputed +/-1), never member by member',
         'reading': 'a date rule applied member by member is outcome-blind in its criterion and outcome-dependent in its timing: choosing when to correct is choosing which members leave; withdrawing the whole cohort leaves no choice that depends on outcomes'}
out['RC112_cutoff_correction_selection'] = rc112

# ================= r4303569735 (RC-113): observer outage combined with a late publication =================
D, W = 100, 10
rc113 = {'deadline': D, 'latency_window': W, 'finality': D + W, 'observer_down': [100, 130], 'first_read_at': 130,
         'cases': {
             'record_published_115_occurrence_95_source_evidences_publication_times': {
                 'v7': 'member open until the observer reads; T-04 then says "by content": YES ignores the latency rule, NO lacks the observation of absence, the text says a late report is never VOID',
                 'v8': 'NO at 110 with knowable_at = 110: under the source rule\'s monotone-publication condition (OD5) the earliest matching record\'s evidenced publication time 115 > 110 is itself the archived observation that no record existed at 110; the record is a source-latency defect, the outage an integrity incident; identical to the disposition the observer would have reached by reading at 110'},
             'record_published_105_first_observed_130': {'v7': 'YES (RC-105)', 'v8': 'YES (unchanged)'},
             'no_record_when_read_at_130': {'v7': 'NO at 110 (observation of absence after the window)', 'v8': 'NO at 110 (unchanged)'},
             'record_published_115_source_cannot_evidence_publication_times': {
                 'v7': 'undefined', 'v8': 'adjudicated VOID at 110 under the source rule\'s failure condition (the source cannot evidence absence); such a source is an OD5 exclusion at registration'}},
         'invariant': 'the disposition of a member is a function of the archived source records and the pre-registered source rule alone, never of when the observer happened to read',
         'reading': 'the missing case had two rules that could not both hold; it is closed by stating what counts as an observation of absence when the observer was down: the late record itself, under a source rule that makes publication times monotone and evidenced'}
out['RC113_outage_plus_late_publication'] = rc113

# ================= r4303569739 (RC-114): the maximum horizon subtracted twice =================
T_A, H_max = 24, 6
T_R = T_A - H_max
rc114 = {'analysis_date_T_A_months': T_A, 'H_max': H_max, 'registration_cut_off_T_R': T_R,
         'event_registered_18_horizon_6': {'maturity': 24, 'eligible_under_maturity_<=_T_A': True, 'eligible_under_misreading_maturity_<=_T_R': False},
         'share_of_a_uniform_cohort_lost_under_the_misreading': round((T_R - (T_R - H_max)) / T_R, 3),
         'implication': 'registration <= T_R and declared horizon <= H_max give maturity <= T_A, so the maturity condition is implied; it is restated with the analysis date named so that the two cut-offs cannot be read as one',
         'reading': 'the sentence used "the 24-month cut-off" for the analysis date two clauses after calling the registration cut-off "the cut-off"; under the reading Codex gives, a third of the accrued cohort leaves'}
out['RC114_accrual_double_subtraction'] = rc114

# ================= r4303569744 (RC-115): T-17 and F-24 disagree on pre-declared members =================
xa = 0.1
rc115 = {'cluster_A_scored_member_increment': xa,
         'T17_v7_wording_pre_declared_sibling_imputed_+/-1': {'bounds_on_cluster_increment': [round((xa - 1) / 2, 3), round((xa + 1) / 2, 3)], 'cap_count': 1},
         'section3_and_F24_v7_pre_declared_outside_cap_and_bounds': {'bounds_on_cluster_increment': [xa, xa], 'cap_count': 0, 'audit_count_by_reason': 1},
         'cluster_B_two_pre_declared': {'T17_v7': 'counts two against the cap', 'section3_F24_v7': 'outside the cap; two in the candidate log and the VOID audit by reason'},
         'v8_choice': 'section 3 and F-24: a pre-declared member is fixed in the registration record before any forecast or outcome exists and is a population choice, like a candidate-log rejection; the cap and the bounds cover members that left the scored population after registration',
         'reading': 'round 9 rewrote section 3 and F-24 for RC-87 and RC-90 and left the T-17 pass condition at its round-7 wording; the two cannot both be implemented'}
out['RC115_T17_F24_pre_declared'] = rc115

out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
