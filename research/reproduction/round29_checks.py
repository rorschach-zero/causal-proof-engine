"""Round-29 checks for the Codex findings on PR #4 at 53a1313 (no reference code, no network).

Codex review 5563019358 of 53a1313, five inline findings: 4307043404 (RC-202, the replayed close read against the
time a registration record is written), 4307043409 (RC-203, a commit identity; not reproducible from the repository,
no block), 4307043412 (RC-204, late registrations absent from the VOID-cap numerator), 4307043414 (RC-205, a delayed
registration out of the monitor's record order), 4307043423 (RC-206, the reproduction lock without hashes; checked by
pip, no block).

Setting of RC-187, RC-191 and RC-200 (Appendices Y, Z and AB): 200 eligible clusters, half with mean increment +d and
half -d, so the eligible-population mean is exactly zero; noise sd sigma; Bernoulli inclusion at pi = 0.5; one-sided
test of the included mean at the nominal 1.645 and at the illustrated c* = 2.254.
"""
import json
import math
import numpy as np

out = {}

# ================= 4307043404 (RC-202): the replayed close read at the written registration time =================
# 17 v25 section 2 item 2: after the audit, "every registration at or after the replayed tau leaves the cohort". The
# RC-200 schedule fixes t_reg,b but the close rule does not say which registration time it reads. Read at the time
# the record is written, a drawn cluster listed before tau whose record is delayed past tau leaves the cohort, so the
# RC-200 removal returns through the close. Remedy: cohort membership is read from the audited stream (a drawn cluster
# belongs to the cohort iff its candidate entry precedes tau) and the T_R condition from t_reg,b; a record written
# after t_reg,b is a late registration, boxed, whatever its written time.
def membership(listed_at, t_reg, written_at, tau, rule):
    reference = written_at if rule == 'v25' else listed_at
    if reference >= tau:
        return 'leaves_cohort_exploratory'
    if written_at > t_reg:
        return 'in_cohort_late_registration_box_rule_under_void_cap'
    return 'in_cohort_scored'

fixture = {'K_on_schedule': (38, 45, 45), 'L_delayed_past_tau': (38, 45, 55), 'M_listed_after_tau': (52, 65, 65)}
out['4307043404 RC-202 fixture'] = {
    'tau': 50,
    'clusters': {k: {'listed_at': la, 't_reg': tr, 'written_at': wa,
                     'v25': membership(la, tr, wa, 50, 'v25'), 'remedy': membership(la, tr, wa, 50, 'remedy')}
                 for k, (la, tr, wa) in fixture.items()}}

rng = np.random.default_rng(2290)
NC, D, SIG, PI, H = 200, 0.01, 0.02, 0.5, 20000
mu = np.where(np.arange(NC) < NC // 2, D, -D)
neg = np.arange(NC) >= NC // 2

def t_stat(x):
    return x.mean() / (x.std(ddof=1) / math.sqrt(x.size))

def delay_past_tau(q):
    rej = {'v25_nom': 0, 'v25_cal': 0, 'honest_nom': 0, 'honest_cal': 0, 'vertex_nom': 0, 'vertex_cal': 0}
    for _ in range(H):
        drawn = rng.random(NC) < PI
        x = mu + SIG * rng.standard_normal(NC)
        delayed = drawn & neg & (rng.random(NC) < q)
        for name, t in (('v25', t_stat(x[drawn & ~delayed])), ('honest', t_stat(x[drawn])),
                        ('vertex', t_stat(np.where(delayed, -1.0, x)[drawn]))):
            rej[f'{name}_nom'] += t > 1.645
            rej[f'{name}_cal'] += t > 2.254
    return {k: round(v / H, 4) for k, v in rej.items()}

rc202 = {'clusters': NC, 'd': D, 'sigma': SIG, 'pi': PI, 'histories': H}
for q in (0.1, 0.25, 0.5):
    rc202[f'drawn_negative_share_written_after_tau={q}'] = delay_past_tau(q)
out['4307043404 RC-202 null population'] = rc202

# ================= 4307043412 (RC-204): late registrations and drawn omissions in the cap numerator =================
# 17 v25 section 6: share = (1/N) sum_k v_k / s_k, v_k = members adjudicated VOID or pending at T_A. A late
# registration (RC-200) and a drawn omission (RC-191) "count against the cap" in the prose, but neither is VOID or
# pending: their outcomes are known. Fixture: 100 two-member clusters, none pre-declared VOID; two members adjudicated
# VOID in two clusters; six whole clusters late registrations; two drawn omitted members of logged clusters.
N, S_K = 100, 2
void_members = 2
late_clusters = 6
omitted_members = 2
v25_share = void_members * (1 / S_K) / N
remedy_share = (void_members * (1 / S_K) + late_clusters * 1 + omitted_members * (1 / S_K)) / N
out['4307043412 RC-204 cap fixture'] = {
    'clusters': N, 'members_per_cluster': S_K, 'void_members': void_members, 'late_registration_clusters':
    late_clusters, 'drawn_omitted_members': omitted_members,
    'v25_share': round(v25_share, 4), 'remedy_share': round(remedy_share, 4),
    'v25_under_5pct_cap': v25_share <= 0.05, 'remedy_under_5pct_cap': remedy_share <= 0.05}

# ================= 4307043414 (RC-205): a delayed registration out of the monitor's record order =================
# 17 v25 section 3 item 3: the watermark argument ("a registration at time t has H > t") and the predecessor set read
# the registration records actually written. Pairs (B_i, A_i) with B_i before A_i in record order; under the null
# every increment is a fair +-1 and the factor is 1 + lam X, lam = 0.5 fixed. A YES of A_i is publicly knowable
# before B_i's scheduled registration with probability q. The registrar withholds B_i's record when A_i is a known
# YES and the running wealth is at or above w_min. v25: A_i's factor is committed without B_i, and B_i, a late
# registration at the lower end of its box (1 - lam), is consumed at the end. Remedy: the predecessor set is read
# from the anchored batches and the draws at t_reg,b, so B_i is committed at its own record-order position at the
# lower end of its box, before A_i.
rng = np.random.default_rng(2291)
P, LAM, HM, THRESH, Q = 60, 0.5, 20000, 20.0, 1.0
xb = rng.choice([-1.0, 1.0], (HM, P))
xa = rng.choice([-1.0, 1.0], (HM, P))
early = (xa > 0) & (rng.random((HM, P)) < Q)

def crossing(rule, w_min):
    crossed = 0
    for h in range(HM):
        w = m = 1.0
        tail = 0
        for i in range(P):
            fa, fb = 1 + LAM * xa[h, i], 1 + LAM * xb[h, i]
            withheld = rule != 'honest' and early[h, i] and w >= w_min
            if withheld and rule == 'v25':
                w *= fa
                m = max(m, w)
                tail += 1
                continue
            w *= (1 - LAM) if withheld else fb
            m = max(m, w)
            w *= fa
            m = max(m, w)
        w *= (1 - LAM) ** tail
        crossed += max(m, w) >= THRESH
    return round(crossed / HM, 4)

rc205 = {'pairs': P, 'lambda': LAM, 'paths': HM, 'threshold': THRESH, 'q_yes_knowable_before_t_reg_of_B': Q,
         'honest': crossing('honest', 0.0)}
for w_min in (0.0, 10.0):
    rc205[f'withhold_B_when_A_known_yes_and_wealth_at_least={w_min}'] = {
        'v25': crossing('v25', w_min), 'remedy': crossing('remedy', w_min)}

# Codex's interleaving: A with H_A = 100, B with H_B = 50 drawn in a batch with t_reg,b = 20, B's record written at
# 110. v25 consumes A (at 100 + D) before B; the remedy commits B at 50 + D at its lower end, before A.
def order(rule, d):
    events = [('A', 100 + d), ('B', 50 + d if rule == 'remedy' else max(50 + d, 110))]
    return [k for k, _ in sorted(events, key=lambda e: e[1])]

rc205['codex_fixture_D=0'] = {'v25': order('v25', 0), 'remedy': order('remedy', 0)}
out['4307043414 RC-205'] = rc205

print(json.dumps(out, indent=1))
