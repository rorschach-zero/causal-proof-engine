"""Round-35 checks for the Codex findings on PR #4 at c570b9b (no reference code, no network).

Codex's review 5563393400 of c570b9b, two inline findings, both P1:
- 4307407873 (RC-218): version 31 reads every member's cluster assignment from the point-in-time state of its
  listing. When an earlier cluster's outcome is knowable before a later member is listed, that state can itself be
  written after the outcome: a source links B to A only after a favourable A, and the rule removes B.
- 4307407877 (RC-219): version 31 calls the eta close tau "blind to every outcome" because it is computed from the
  eligible candidate stream. When the stream responds to outcomes already public in the registration window, tau is
  a stopping time of those outcomes.

Setting of Appendices AF to AH: cluster increment +-0.2, one-sided t at the nominal 1.645, 20,000 replications.
"""
import json

import numpy as np
from scipy.stats import binom

out = {}
REPS, CRIT = 20_000, 1.645


def t_stat(s, w):
    n = w.sum(1)
    m = (s * w).sum(1) / n
    sd = np.sqrt(((s - m[:, None]) ** 2 * w).sum(1) / (n - 1))
    return m / (sd / np.sqrt(n))


def rate(rej):
    return round(float(rej.mean()), 4)


def coin(rng, shape, delta=0.0):
    return np.where(rng.random(shape) < 0.5 + delta / 0.4, 0.2, -0.2)


# ================= 4307407873 (RC-218): linkage written after a predecessor's outcome =================
# 300 pairs: A registered in batch 1, B listed in batch 2 after A's outcome is knowable, both registered.
# Law C(q): B = -A with probability 0.5 and an independent fair increment otherwise (the cluster rule did not link
# the dependent pair at A's listing); after a favourable A, the state written at B's listing links B to A with
# probability q (Codex's example). Law F(q): after a favourable A the source lists a follow-up B with probability q,
# B = A, and links it to A truthfully; no B exists otherwise (the RC-215 law with the sign reversed).
# Rules: version31_remove, the linked B is a post-registration member of A and leaves every statistic; retain, a
# linkage written after A's earliest-knowable bound is ignored and B stays its own cluster; box_lower_end, the linked
# B enters at the lower end of the box {B excluded, B included}, which for a positive t means B included when -0.2
# and excluded when +0.2; enrolment_closed, the remedy: a cohort enrols only candidates whose earliest-knowable bound
# follows the end of its enrolment window, so B is listed before any outcome of A is knowable (its linkage, at the
# same marginal rate, cannot read A) or after that window (B is not in this cohort's confirmatory population).
PAIRS = 300
rng = np.random.default_rng(3501)


def law_c(q, delta=0.0):
    a = coin(rng, (REPS, PAIRS), delta)
    dep = rng.random((REPS, PAIRS)) < 0.5
    b = np.where(dep, -a, coin(rng, (REPS, PAIRS), delta))
    linked_after = (a > 0) & (rng.random((REPS, PAIRS)) < q)
    linked_blind = rng.random((REPS, PAIRS)) < float(linked_after.mean())
    s = np.concatenate([a, b], 1)
    ones = np.ones_like(a)

    def keep(linked):
        return np.concatenate([ones, (~linked).astype(float)], 1)

    box = np.concatenate([ones, (~(linked_after & (b > 0))).astype(float)], 1)
    return {'share_linked': round(float(linked_after.mean()), 4),
            'version31_remove': rate(t_stat(s, keep(linked_after)) > CRIT),
            'retain': rate(t_stat(s, keep(np.zeros_like(linked_after))) > CRIT),
            'box_lower_end': rate(t_stat(s, box) > CRIT),
            'enrolment_closed': rate(t_stat(s, keep(linked_blind)) > CRIT),
            'non_confirmatory_if_any_late_link': rate((t_stat(s, keep(linked_after)) > CRIT)
                                                      & ~linked_after.any(1))}


def law_f(q):
    a = coin(rng, (REPS, PAIRS))
    listed = (a > 0) & (rng.random((REPS, PAIRS)) < q)
    s = np.concatenate([a, a], 1)
    ones = np.ones_like(a)
    with_b = np.concatenate([ones, listed.astype(float)], 1)
    without_b = np.concatenate([ones, np.zeros_like(a)], 1)
    return {'share_listed': round(float(listed.mean()), 4),
            'version31_remove': rate(t_stat(s, without_b) > CRIT),
            'retain': rate(t_stat(s, with_b) > CRIT),
            'box_lower_end': rate(t_stat(s, without_b) > CRIT),
            'enrolment_closed': rate(t_stat(s, without_b) > CRIT)}


out['4307407873 RC-218 exactly null, law C(q): link written after a favourable predecessor'] = {
    f'q={q}': law_c(q) for q in (0.05, 0.10, 0.20)}
out['4307407873 RC-218 exactly null, law F(q): follow-up listed and linked after a favourable predecessor'] = {
    f'q={q}': law_f(q) for q in (0.05, 0.10, 0.20)}


def law_r(r, delta=0.02):
    # Linkage independent of every outcome (rate r), A and B independent: the power each rule keeps.
    a = coin(rng, (REPS, PAIRS), delta)
    b = coin(rng, (REPS, PAIRS), delta)
    linked = rng.random((REPS, PAIRS)) < r
    s = np.concatenate([a, b], 1)
    ones = np.ones_like(a)
    remove = np.concatenate([ones, (~linked).astype(float)], 1)
    box = np.concatenate([ones, (~(linked & (b > 0))).astype(float)], 1)
    return {'version31_remove_and_enrolment_closed': rate(t_stat(s, remove) > CRIT),
            'box_lower_end': rate(t_stat(s, box) > CRIT)}


out['4307407873 RC-218 delta = 0.02, linkage independent of outcome R(r)'] = {
    f'r={r}': law_r(r) for r in (0.025, 0.05, 0.10)}

# ================= 4307407877 (RC-219): an eta close driven by outcome-triggered supply =================
# One cluster registered per slot (pi = 1), slots 0 to 599; cluster i's outcome is knowable at slot i + L. The eta
# budget fits the planned 600 candidates, so tau = T_R when supply follows the plan. Strategy close_when_ahead(s):
# from slot 200 on, at the first slot t at which the clusters already resolved (i <= t - L) have t > s, the source
# lists one predicate-matching candidate whose late-record bound exhausts the remaining budget; tau = t and the
# cohort is clusters 0 to t - 1. Every inclusion draw is untouched. The same cohort arises with no eta close at all
# when the source stops listing at that slot and the window ends at T_R (the non-confirmatory-if-binding route).
# Remedy enrolment_closed: no cohort outcome is knowable before the enrolment end (L >= 600), so the resolved prefix
# is empty and the source's close can depend on no outcome; tau is drawn uniformly on [200, 600) as the most such a
# source can do.
N, T_MIN = 600, 200
rng = np.random.default_rng(3502)


def close_when_ahead(lag, s_trigger):
    x = coin(rng, (REPS, N))
    c1, c2 = np.cumsum(x, 1), np.cumsum(x * x, 1)
    n = np.arange(1, N + 1)
    mean = c1 / n
    var = (c2 - n * mean ** 2) / np.maximum(n - 1, 1)
    t_prefix = mean / np.sqrt(np.maximum(var, 1e-12) / n)
    slots = np.arange(T_MIN, N)
    resolved = slots - lag
    trig = t_prefix[:, resolved] > s_trigger
    fired = trig.any(1)
    tau = np.where(fired, slots[np.argmax(trig, 1)], N)
    t_final = t_prefix[np.arange(REPS), tau - 1]
    tau_blind = rng.integers(T_MIN, N + 1, REPS)
    t_blind = t_prefix[np.arange(REPS), tau_blind - 1]
    return {'share_closed_early': round(float(fired.mean()), 4),
            'version31_tau_from_stream': rate(t_final > CRIT),
            'fixed_T_R_honest_supply': rate(t_prefix[:, -1] > CRIT),
            'non_confirmatory_if_binding': rate((t_prefix[:, -1] > CRIT) & ~fired),
            'enrolment_closed_tau_blind': rate(t_blind > CRIT)}


out['4307407877 RC-219 exactly null, close when the resolved prefix is ahead'] = {
    f'L={lag}, s={s}': close_when_ahead(lag, s) for lag in (50, 100) for s in (1.0, 1.645)}


def exact_null_rate(n):
    # Exact rejection rate of the t statistic on n fair +-0.2 increments, by the number k of +0.2.
    k = np.arange(n + 1)
    p = k / n
    with np.errstate(divide='ignore', invalid='ignore'):
        t = 0.2 * (2 * p - 1) / np.sqrt(0.04 * 4 * p * (1 - p) / (n - 1))
    return float(binom.pmf(k, n, 0.5)[np.nan_to_num(t, nan=-np.inf) > CRIT].sum())


exact = [exact_null_rate(n) for n in range(T_MIN, N + 1)]
out['4307407877 RC-219 exact null rate, tau uniform on [200, 600] and independent of outcomes'] = {
    'mean_over_tau': round(float(np.mean(exact)), 4), 'min_over_n': round(min(exact), 4),
    'max_over_n': round(max(exact), 4), 'n=600': round(exact[-1], 4)}

print(json.dumps(out, indent=1))
