"""Round-24 checks for the Codex findings on PR #4 at 68e9415 (no reference code, no network).

Codex's automatic review 5562620826 of 68e9415 (three inline findings, all on 17 section 3 item 3, the round-23
remedy RC-179): 4306742760 (RC-180, the recalibration allocation), 4306742763 (RC-181, search points in the anchored
record), 4306742767 (RC-182, a selectable v).

Setting of RC-179 (Appendix W): on one continuous null point, c* sits just above the (m + 1)-th largest of R simulated
statistics, m the largest count whose exact one-sided upper bound at confidence 1 - g is <= L, so its true size is
Beta(m + 1, R - m) exactly and the record miscovers when that size exceeds L. Version 20 certifies each of the S
records of a family so far at g = gamma_cal / (K S), with S the number of records when the claim is made.
"""
import json
import math
import numpy as np
from scipy.stats import beta

out = {}
L, G, R = 0.04, 0.01, 20000

def m_max(R, L, g):
    """Largest rejection count m whose exact one-sided upper bound at confidence 1 - g is <= L."""
    lo, hi = 0, R
    if beta.ppf(1 - g, 1, R) > L:
        return -1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if beta.ppf(1 - g, mid + 1, R - mid) <= L:
            lo = mid
        else:
            hi = mid - 1
    return lo

def q(g):
    """Exact probability that one record certified at confidence 1 - g miscovers (true size > L)."""
    m = m_max(R, L, g)
    return float(beta.sf(L, m + 1, R - m)), m

# ================= 4306742760 (RC-180): an allocation that depends on the realised S =================
# (a) Oracle stopping, the supremum over stopping rules: stop at the first S whose newest record, certified at
# gamma_cal / S, miscovers. Its probability is 1 - prod_{s <= N} (1 - q(gamma_cal / s)), a lower bound on the
# version-20 failure probability for every rule that may stop anywhere up to N attempts.
rc180 = {'L': L, 'gamma_cal': G, 'K': 1, 'R': R}
qs, ms, surv = {}, {}, 1.0
checkpoints = (1, 2, 5, 10, 20, 50, 100, 1000)
oracle = {}
for s in range(1, max(checkpoints) + 1):
    qv, mv = q(G / s)
    surv *= 1 - qv
    if s in checkpoints:
        oracle[f'N={s}'] = round(1 - surv, 4)
        qs[f's={s}'] = round(qv, 5)
        ms[f's={s}'] = mv
rc180['per_attempt_miscoverage_q_s'] = qs
rc180['certified_count_m_s'] = ms
rc180['v20_oracle_stopping_P_miscover_within_N'] = oracle
# Harmonic tail: q_s is close to gamma_cal / s, so the failure probability grows like gamma_cal * ln N without bound.
rc180['harmonic_approximation_1-exp(-q1*H_N)'] = {f'N={N}': round(1 - math.exp(-qs['s=1'] * sum(1 / s for s in range(1, N + 1))), 4)
                                                for N in (100, 1000, 10 ** 6)}

# (b) A rule an analyst can apply without knowing the true size: recalibrate until the newest record's c* is below
# the first record's c* (equivalently its true size is above the first record's), at most N_cap attempts, and keep
# the record that stopped, certified at its own S. Monte Carlo over the exact Beta laws.
rng = np.random.default_rng(2180)
H = 200000
def beat_first(levels, cap):
    """levels(s) gives the confidence parameter of record s when the family has s records; returns P(miscover)."""
    sizes = np.empty((H, cap))
    for s in range(1, cap + 1):
        m = m_max(R, L, levels(s))
        sizes[:, s - 1] = rng.beta(m + 1, R - m, size=H)
    first = sizes[:, 0]
    kept = first.copy()
    done = np.zeros(H, dtype=bool)
    for s in range(2, cap + 1):
        stop = (~done) & (sizes[:, s - 1] > first)
        kept[stop] = sizes[stop, s - 1]
        done |= stop
    return round(float((kept > L).mean()), 4), round(float(done.mean()), 4)
rc180['beat_first_rule'] = {}
for cap in (5, 20):
    p_v20, stopped = beat_first(lambda s: G / s, cap)
    p_fixed, _ = beat_first(lambda s, c=cap: G / c, cap)
    rc180['beat_first_rule'][f'N_cap={cap}'] = {'v20_retrospective_gamma_over_S': p_v20, 'stopped_before_cap': stopped,
                                                'fixed_S_max_gamma_over_S_max': p_fixed}

# (c) Remedy: S_max pre-registered in the family's first record, every record certified at gamma_cal / (K S_max),
# no record beyond S_max. Any stopping rule is covered by the union over S_max records: <= 1 - (1 - q)^S_max.
rc180['remedy_fixed_S_max_union_bound'] = {}
for S_max in (1, 3, 10):
    qv, _ = q(G / S_max)
    rc180['remedy_fixed_S_max_union_bound'][f'S_max={S_max}'] = round(1 - (1 - qv) ** S_max, 4)
# (d) Codex's alternative: a summable allocation fixed in advance, w_s = 6 / (pi^2 s^2), record s at gamma_cal w_s.
surv = 1.0
for s in range(1, 1001):
    surv *= 1 - q(G * 6 / (math.pi ** 2 * s ** 2))[0]
tail = G * 6 / math.pi ** 2 * sum(1 / s ** 2 for s in range(1001, 10 ** 6)) + G * 6 / math.pi ** 2 / 10 ** 6
rc180['alternative_summable_w_s'] = {'P_miscover_any_of_first_1000': round(1 - surv, 4),
                                     'union_tail_bound_beyond_1000': round(tail, 6)}
out['4306742760 RC-180'] = rc180

# ================= 4306742763 (RC-181): seeded search points cannot be in the record that fixes the seed =========
# A toy seeded search over a one-dimensional box: its realised points are a function of s, so a record that must
# contain them cannot be anchored before s exists. What can be anchored is the procedure and its budget K_max.
def toy_search(seed, K_max=8):
    r = np.random.default_rng(seed)
    pts = []
    for _ in range(K_max):
        x = float(r.uniform(0.0, 1.0))
        pts.append(round(x, 6))
        if x > 0.9:   # data-dependent stop: the realised count K varies with the seed
            break
    return pts
rc181 = {f'seed={sd}': {'points': toy_search(sd), 'K_realised': len(toy_search(sd))} for sd in (1, 2, 3)}
rc181['points_identical_across_seeds'] = len({tuple(toy_search(sd)) for sd in (1, 2, 3)}) == 1
rc181['K_max'] = 8
out['4306742763 RC-181'] = rc181

# ================= 4306742767 (RC-182): a v the contributor can try offline =================
# If the party supplying v can compute s = SHA-256(record || v) for candidates before revealing one, revealing the
# best of n candidates is the k-seed selection of RC-179 with k = n: P(true size > L) = 1 - (1 - q)^n.
q1, m1 = q(G)
rc182 = {'m': m1, 'P_true_size_above_L_best_of_n': {f'n={n}': round(1 - (1 - q1) ** n, 4) for n in (1, 10, 50, 1000)}}
out['4306742767 RC-182'] = rc182

print(json.dumps(out, indent=1))
