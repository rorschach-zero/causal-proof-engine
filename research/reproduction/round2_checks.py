"""Round-2 arithmetic checks for the Codex findings on PR #4 (no reference code needed)."""
import json, math
import numpy as np
from scipy.stats import beta, binom

out = {}
# Finding r4294987398: exact one-sided 95 % upper bound with 0 of 2000.
n = 2000
out['exact_upper_0_of_2000'] = round(1 - 0.05 ** (1 / n), 6)
out['clopper_pearson_0_of_2000'] = round(float(beta.ppf(0.95, 1, n)), 6)
out['round1_pseudocount_normal_value'] = round(0 + 1.645 * math.sqrt((1 / n) * 1 / n), 6)
# How many crossings would still satisfy A3 (bound <= 0.06) at n = 2000?
k_max = max(k for k in range(0, 200) if beta.ppf(0.95, k + 1, n - k) <= 0.06)
out['max_crossings_of_2000_with_upper_bound_le_0.06'] = k_max
out['upper_bound_at_that_k'] = round(float(beta.ppf(0.95, k_max + 1, n - k_max)), 5)

# Finding r4294987465: VOID imputed as NO is not conservative for a paired Brier difference.
def paired_brier_increment(p_full, p_base, y):
    return (p_base - y) ** 2 - (p_full - y) ** 2   # positive favours FULL
out['void_example'] = {'p_full': 0.1, 'p_base': 0.9,
                       'impute_Y0': round(paired_brier_increment(0.1, 0.9, 0), 3),
                       'impute_Y1': round(paired_brier_increment(0.1, 0.9, 1), 3)}
out['worst_case_rule'] = 'impute Y=1 if p_full < p_base else Y=0 gives the increment least favourable to FULL'
# Worst-case bound over m VOIDs with |X| <= 1: mean increment shifts by at most m/N.
out['void_bound_shift_example'] = {'N': 300, 'm_void': 15, 'max_shift_of_mean_increment': round(15 / 300, 4)}

# Finding r4294987395: a single-run IUT check is flaky and can pass a wrong implementation.
alpha = 0.05
out['iut_single_run'] = {
    'P_correct_impl_rejects_null_comparator_once': alpha,
    'P_wrong_impl_size_0.10_passes_single_run': 1 - 0.10,
    'P_wrong_impl_size_0.10_passes_MC_bound_check_n2000': round(float(binom.cdf(k_max, 2000, 0.10)), 8),
    'P_correct_impl_fails_MC_bound_check_n2000': round(1 - float(binom.cdf(k_max, 2000, 0.05)), 6)}
# Deterministic oracle: conjunction rejects iff every component rejects.
import itertools
comps = [0.01, 0.20, 0.03]
out['iut_oracle_example'] = {'component_p': comps, 'reject_all_at_0.05': all(p <= alpha for p in comps),
                             'min_e_value_rule': 'reject iff min_j e_j >= 1/alpha'}

# T-13 design: replications and margin so that a correct level-alpha test passes with high
# probability while an over-sized implementation fails.
design = {}
for n_rep, margin, conf in [(2000, 0.01, 0.95), (10000, 0.01, 0.99), (20000, 0.01, 0.99)]:
    k_max_d = max(k for k in range(0, int(n_rep * 0.2)) if beta.ppf(conf, k + 1, n_rep - k) <= alpha + margin)
    design[f'n={n_rep},margin={margin},conf={conf}'] = {
        'k_max': k_max_d,
        'P_pass_size_0.05': round(float(binom.cdf(k_max_d, n_rep, 0.05)), 6),
        'P_pass_size_0.06': round(float(binom.cdf(k_max_d, n_rep, 0.06)), 6),
        'P_pass_size_0.07': float(binom.cdf(k_max_d, n_rep, 0.07)),
        'P_pass_size_0.10': float(binom.cdf(k_max_d, n_rep, 0.10))}
out['t13_design'] = design

# Finding r4296205661 (RC-47): does sanitising __context__ inside the handler prevent chaining?
def chained_context(style):
    try:
        try:
            raise ValueError('bearer SYNTHETIC-CANARY')
        except ValueError as e:
            if style == 'set_none_in_handler':
                new = RuntimeError('sanitised'); new.__context__ = None; raise new
            if style == 'from_none_in_handler':
                raise RuntimeError('sanitised') from None
            summary = type(e).__name__          # keep only a sanitised summary, leave the handler
        raise RuntimeError(f'sanitised ({summary})')
    except RuntimeError as r:
        return 'CANARY' in repr(r.__context__)
out['exception_context_canary_reachable'] = {s: chained_context(s) for s in
    ('set_none_in_handler', 'from_none_in_handler', 'translate_outside_handler')}

# Finding r4296205602 (RC-41): bound of the per-event paired Brier increment and of 1 + lambda * mean.
corners = [abs((pb - y) ** 2 - (pf - y) ** 2) for pb in (0.0, 1.0) for pf in (0.0, 1.0) for y in (0, 1)]
out['increment_bound'] = {'max_abs_X_i': max(corners), 'min_factor_at_lambda_max_0.5': 1 - 0.5 * max(corners)}

# Finding r4294987471 / r4294987415: no arithmetic; design-level.
print(json.dumps(out, indent=2))
