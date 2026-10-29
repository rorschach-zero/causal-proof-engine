"""Round-25 checks for the Codex findings on PR #4 at a281c1a (no reference code, no network).

Codex's automatic review 5562699808 of a281c1a (six inline findings): 4306808044 (RC-183, an attempt budget reset by
relabelling a family), 4306808046 (RC-184, the oracle-stopping figure is an upper bound, not a lower one),
4306808051 (RC-185, A3 left at the single-attempt rule; deterministic, no check here), 4306808057 (RC-186, a search
that reads a point's own stream before fixing it), 4306808061 (RC-187, a selectable sampling seed), 4306808064
(RC-188, the eta close is a stopping time of the inclusion draws).

Setting of RC-179 and RC-180 (Appendices W and X): on one continuous null point, c* sits just above the (m + 1)-th
largest of R simulated statistics, m the largest count whose exact one-sided upper bound at confidence 1 - g is <= L,
so its true size is Beta(m + 1, R - m) exactly and the record miscovers when that size exceeds L.
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

# ================= 4306808044 (RC-183): S_max per family, families relabelled at will =================
# Each relabelled family carries its own S_max = 1 and certifies at gamma_cal / K_max; keeping the smallest c* over
# n relabelled families is the k-seed selection of Appendix W with k = n. Remedy: one S_max per cohort contract,
# counted over every calibration record that cites the contract, whatever its generator, search or label.
q1, m1 = q(G)
rc183 = {'m': m1, 'v21_per_family_S_max_1_best_of_n_families': {f'n={n}': round(1 - (1 - q1) ** n, 4)
                                                                 for n in (1, 2, 5, 10)}}
rc183['remedy_contract_S_max_union_bound'] = {}
for S_max in (1, 5, 10):
    qv, _ = q(G / S_max)
    rc183['remedy_contract_S_max_union_bound'][f'S_max={S_max}'] = round(1 - (1 - qv) ** S_max, 4)
out['4306808044 RC-183'] = rc183

# ================= 4306808046 (RC-184): direction of the oracle-stopping figure =================
# P(some record among the first N miscovers) = 1 - prod (1 - q_s) contains the miscoverage event of the record kept
# by any rule that stops within N records, so it is an upper bound over those rules, attained only by the oracle
# that sees the true size. The always-stop-at-the-first rule gives q_1; the beat-first rule (Appendix X) lies between.
surv, oracle = 1.0, {}
for s in range(1, 101):
    surv *= 1 - q(G / s)[0]
    if s in (1, 5, 20, 100):
        oracle[f'N={s}'] = round(1 - surv, 4)
rc184 = {'v20_allocation_P_some_record_miscovers_within_N': oracle,
         'v20_allocation_stop_at_first_record': round(q1, 4),
         'v20_allocation_beat_first_appendix_X': {'N_cap=5': 0.0175, 'N_cap=20': 0.0200},
         'ordering_holds': bool(q1 <= 0.0175 <= oracle['N=5'] and 0.0200 <= oracle['N=20'])}
out['4306808046 RC-184'] = rc184

# ================= 4306808057 (RC-186): a search that reads a point's own stream =================
# A point's statistic is a function of its stream of R uniforms. The search may place point j at one of M
# coordinates; coordinate k maps the same uniforms to statistics frac(U + k / M), each a valid continuous null law.
# c* is set just above the (m + 1)-th largest statistic, so its true size is the upper tail above that order
# statistic. A search that reads the stream and keeps the coordinate with the smallest c* selects among M nearly
# independent order statistics; a search whose choice is drawn from a separate controller stream does not.
rng = np.random.default_rng(2186)
H = 10000
def search_miscoverage(M, reads_point_stream):
    bad = 0
    for _ in range(H):
        u = rng.random(R)
        if reads_point_stream:
            sizes = []
            for k in range(M):
                t = np.mod(u + k / M, 1.0)
                c = np.partition(t, R - m1 - 1)[R - m1 - 1]
                sizes.append(1.0 - c)
            size = max(sizes)
        else:
            k = int(rng.integers(M))
            t = np.mod(u + k / M, 1.0)
            size = 1.0 - np.partition(t, R - m1 - 1)[R - m1 - 1]
        bad += size > L
    return round(bad / H, 4)
rc186 = {'m': m1, 'histories': H, 'exact_q_1': round(q1, 4)}
for M in (2, 10):
    rc186[f'M={M}'] = {'search_reads_point_stream': search_miscoverage(M, True),
                       'controller_stream_only': search_miscoverage(M, False),
                       'best_of_M_law_1-(1-q)^M': round(1 - (1 - q1) ** M, 4)}
out['4306808057 RC-186'] = rc186

# ================= 4306808061 (RC-187): a sampling seed tried before it is committed =================
# 200 eligible clusters, half with mean increment +d and half -d (eligible-population mean exactly zero), noise sd
# sigma, Bernoulli inclusion at pi = 0.5. The analyst tries n seeds and keeps the one that includes the most
# positive-stratum clusters net of negative ones. One-sided test of the included mean at the nominal 1.645 and at
# the illustrated c* = 2.254.
rng = np.random.default_rng(2187)
NC, D, SIG, PI, H2 = 200, 0.01, 0.02, 0.5, 20000
mu = np.where(np.arange(NC) < NC // 2, D, -D)
def sampling_rejection(n_seeds):
    rej_nom = rej_cal = 0
    shift = 0.0
    for _ in range(H2):
        draws = rng.random((n_seeds, NC)) < PI
        score = (draws * np.sign(mu)).sum(axis=1)
        keep = draws[int(np.argmax(score))]
        x = mu[keep] + SIG * rng.standard_normal(int(keep.sum()))
        t = x.mean() / (x.std(ddof=1) / math.sqrt(x.size))
        rej_nom += t > 1.645
        rej_cal += t > 2.254
        shift += mu[keep].mean()
    return {'rejection_at_1.645': round(rej_nom / H2, 4), 'rejection_at_2.254': round(rej_cal / H2, 4),
            'mean_included_true_effect': round(shift / H2, 5)}
rc187 = {'clusters': NC, 'd': D, 'sigma': SIG, 'pi': PI, 'histories': H2}
for n in (1, 10, 50):
    rc187[f'best_of_n_seeds={n}'] = sampling_rejection(n)
out['4306808061 RC-187'] = rc187

# ================= 4306808064 (RC-188): the eta close as a stopping time of the inclusion draws =================
# (a) Codex's example, exact enumeration: budget 1, candidates A (u = .6, +d), B (u = .4, -d), C (u = .6), pi = .5.
# Version 21 counts the bounds of registered candidates only; the window closes at C when C's registration would
# carry the sum above 1.
def v21_close_at_C(a, b, c):
    s = 0.0
    for drawn, u in ((a, 0.6), (b, 0.4)):
        if drawn:
            s += u
    return bool(c and s + 0.6 > 1.0 + 1e-12)
cases = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
closing = [x for x in cases if v21_close_at_C(*x)]
p_close = len(closing) / 8
rc188 = {'codex_example': {'P_window_closes_at_C': p_close,
                           'P_A_registered_given_window_A_B': sum(x[0] for x in closing) / len(closing),
                           'P_B_registered_given_window_A_B': sum(x[1] for x in closing) / len(closing)}}
# (b) A stream of eligible candidates, each a high-bound source (u = 0.03, effect +d) or a low-bound one (u = 0.02,
# effect -d) with probability 1/2, pi = 0.5, at a budget that admits about four registrations and at one that admits
# about forty. Version 21 closes on the registered sum; the remedy closes on the sum over every eligible candidate,
# drawn or not, so the close is a function of the eligible stream only. Reported: E[sum over registered of
# (effect - eligible-window mean)] / E[registered count], in units of d, with its Monte Carlo standard error over ten
# batches. Under the remedy the draws are independent Bernoulli(pi) given the window, so the expectation is zero.
rng = np.random.default_rng(2188)
UH, UL = 0.03, 0.02
def close_bias(on_eligible, budget, histories):
    batch = []
    for _ in range(10):
        num = den = 0.0
        for _ in range(histories // 10):
            s, win, reg = 0.0, [], []
            while True:
                high = rng.random() < 0.5
                u, e = (UH, 1.0) if high else (UL, -1.0)
                drawn = rng.random() < PI
                add = u if on_eligible else (u if drawn else 0.0)
                if s + add > budget + 1e-12:
                    break
                s += add
                win.append(e)
                if drawn:
                    reg.append(e)
            if reg:
                mw = sum(win) / len(win)
                num += sum(e - mw for e in reg)
                den += len(reg)
        batch.append(num / den)
    b = np.array(batch)
    return {'bias_in_d': round(float(b.mean()), 4), 'mc_se': round(float(b.std(ddof=1) / math.sqrt(10)), 4)}
rc188['stream'] = {'u_high': UH, 'u_low': UL, 'pi': PI}
for budget, histories in ((0.1, 200000), (1.0, 50000)):
    rc188['stream'][f'budget={budget}'] = {'histories': histories,
                                           'v21_close_on_registered': close_bias(False, budget, histories),
                                           'remedy_close_on_eligible': close_bias(True, budget, histories)}
out['4306808064 RC-188'] = rc188

print(json.dumps(out, indent=1))
