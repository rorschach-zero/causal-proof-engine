"""Round-31 checks for the Codex findings on PR #4 at a2b2f78 (no reference code, no network).

Codex review 5563173568 of a2b2f78, three inline findings: 4307196384 (RC-210, a crossing called supported before
the audit of a batch that may hold a predecessor), 4307196389 (RC-211, the identity of c31a1e7e, checked with git and
not here), 4307196393 (RC-212, no frozen order key for an omitted cluster that ties a logged cluster's maturity).

Monitor setting of RC-205 and RC-207 (Appendices AC and AD): pairs (B_i, A_i), B_i before A_i in record order,
lambda = 0.5 fixed, running maximum against 1/alpha = 20.
"""
import json
import numpy as np

out = {}
THRESH, LAM_MAX = 20.0, 0.5


def grapa_lambda(s1, s2, n):
    """Archived GRAPA bet after n increments with sums s1, s2 (16 Appendix A and D)."""
    if n < 2:
        return 0.0
    mean = s1 / n
    var = max(0.0, (s2 - s1 * s1 / n) / (n - 1))
    den = var + mean * mean
    lam = mean / den * n / (n + 10) if den > 0 else 0.0
    return min(max(lam, 0.0), LAM_MAX)


# ================= 4307196384 (RC-210): which batches a supported crossing must wait for =================
# 17 v27 calls a crossing supported once every batch "with a cluster in its record-order prefix" has v_b and is
# audited. An omitted cluster is in no batch until the audit, so a batch whose logged clusters all follow the
# crossing does not count, although its omission precedes it. Toy: A_i in batch 1 (audited before any crossing),
# B_i in batch 2, whose logged clusters all mature after the last A_i; the registrar leaves B_i out of batch 2
# whenever A_i is a known YES. v27: a crossing on the live path is issued as supported (batch 1 is the only batch
# with a logged cluster in the prefix, and it is audited); batch 2's audit at T_D then finds the omission and
# withdraws it, too late for an anytime-valid signal. After every audit the two rules keep the same crossings (those
# reached before the first omission); they differ in what is issued as supported before batch 2's audit. Remedy: a crossing at cluster k waits for every batch with
# t_reg,b < H_k, the batches that can hold a predecessor, so nothing is issued as supported before batch 2's audit.
rng = np.random.default_rng(3071)            # the draws of Appendix AD, so the honest rate is the same
P, LAM, HM = 60, 0.5, 20000
xb = rng.choice([-1.0, 1.0], (HM, P))
xa = rng.choice([-1.0, 1.0], (HM, P))
early = xa > 0


def batch_wait(w_min):
    honest = issued_v27 = issued_remedy = supported = 0
    for h in range(HM):
        w_live = m_live = w_hon = m_hon = 1.0
        clean = True
        for i in range(P):
            fa, fb = 1 + LAM * xa[h, i], 1 + LAM * xb[h, i]
            omitted = early[h, i] and w_live >= w_min
            if clean and omitted:
                clean = False
                supported += m_live >= THRESH
            w_hon *= fb; m_hon = max(m_hon, w_hon); w_hon *= fa; m_hon = max(m_hon, w_hon)
            if not omitted:
                w_live *= fb; m_live = max(m_live, w_live)
            w_live *= fa; m_live = max(m_live, w_live)
        honest += m_hon >= THRESH
        issued_v27 += m_live >= THRESH       # supported when issued under v27; batch 2 not yet audited
        if clean:
            supported += m_live >= THRESH
    return {'honest': round(honest / HM, 4),
            'v27_issued_as_supported_before_batch_2_audit': round(issued_v27 / HM, 4),
            'remedy_issued_as_supported_before_batch_2_audit': round(issued_remedy / HM, 4),
            'supported_after_every_audit_both_rules': round(supported / HM, 4)}


rc210 = {'pairs': P, 'lambda': LAM, 'paths': HM, 'threshold': THRESH}
for w_min in (0.0, 10.0):
    rc210[f'omit_B_when_A_known_yes_and_wealth_at_least={w_min}'] = batch_wait(w_min)

# The remedy's batch set is complete: a cluster of batch b has not_before > t_reg,b and H > not_before, so no batch
# with t_reg,b >= H_k can hold a cluster that precedes k. Random calendars: every predecessor of every k lies in a
# batch with t_reg,b < H_k.
rng = np.random.default_rng(3101)
violations = checked = 0
for _ in range(500):
    nb = 8
    t_reg = np.cumsum(rng.uniform(1.0, 5.0, nb))
    batch = rng.integers(0, nb, 200)
    not_before = t_reg[batch] + rng.uniform(0.01, 3.0, 200)
    hk = not_before + rng.uniform(0.01, 40.0, 200)
    for k in range(200):
        pred = hk <= hk[k]
        pred[k] = False
        violations += int(np.any(t_reg[batch[pred]] >= hk[k]))
        checked += 1
rc210['predecessor_in_batch_with_t_reg_at_or_after_H_k'] = {'clusters_checked': checked, 'violations': violations}
out['4307196384 RC-210'] = rc210

# ================= 4307196393 (RC-212): the order key of an omitted cluster =================
# v27 assigns the tie-breaking registration id at t_reg,b from the anchored batch and v_b. An omitted cluster is not
# in the anchored batch, so when its maturity equals a logged cluster's its position is undefined, and an id
# assigned at the audit can put it on either side. Fixture 1 (lambda = 0.5 fixed): wealth 19 before the tie, A logged
# with increment +0.2, B a drawn omission entered at the lower end of its box, -0.99 (16 Appendix AD).
w0, x_a, x_b_low = 19.0, 0.2, -0.99


def run(order):
    w = w0; peak = w0; cross_at = None; seen = []
    for name, x in order:
        w *= 1 + LAM * x; seen.append(name)
        if w >= THRESH and cross_at is None:
            cross_at = list(seen)
        peak = max(peak, w)
    supported = cross_at is not None and 'B' not in cross_at
    return {'peak': round(peak, 6), 'crossing_prefix': cross_at, 'supported': supported}


fix1 = {'A_before_B': run([('A', x_a), ('B', x_b_low)]), 'B_before_A': run([('B', x_b_low), ('A', x_a)])}
fix1['support_depends_on_audit_time_id'] = fix1['A_before_B']['supported'] != fix1['B_before_A']['supported']
# Fixture 2 (archived GRAPA): the ten increments of Appendix AD, then the tied pair, then C. lambda_C is the same,
# but lambda_A depends on whether B precedes A.
hist = [0.8, -0.8, 0.8, 0.8, -0.8, 0.8, 0.8, -0.8, 0.8, 0.8]


def lam_after(values):
    return round(grapa_lambda(sum(values), sum(v * v for v in values), len(values)), 6)


fix2 = {'lambda_A_with_B_after_A': lam_after(hist), 'lambda_A_with_B_before_A': lam_after(hist + [x_b_low])}

# Remedy: the order key is (H_k, b, cluster id), b the batch whose window contains the candidate's listing time and
# the cluster id derived by the committed cluster rule, both from the source listing (snapshot, or the archive at the
# audit), so an omitted cluster's position is frozen before its draw. On logged clusters it is v27's order (batch
# order, then cluster id, after H_k). Random batches with ties: the two orders agree on every logged cluster, and the
# omitted clusters' keys are the same whether they are derived from the snapshot or at the audit.
rng = np.random.default_rng(3102)
agree = trials = 0
for _ in range(500):
    n = 120
    b = rng.integers(0, 6, n)
    cid = rng.permutation(10_000)[:n]
    hk = rng.integers(10, 20, n)                     # integer maturities: many ties
    logged = rng.random(n) < 0.8
    idx = np.flatnonzero(logged)
    reg_id = np.empty(n, dtype=int)                  # v27: ids at t_reg,b in batch order, then cluster id
    order_v27 = sorted(idx, key=lambda j: (b[j], cid[j]))
    for r, j in enumerate(order_v27):
        reg_id[j] = r
    by_v27 = sorted(idx, key=lambda j: (hk[j], reg_id[j]))
    by_key = [j for j in sorted(range(n), key=lambda j: (hk[j], b[j], cid[j])) if logged[j]]
    agree += by_v27 == by_key
    trials += 1
out['4307196393 RC-212'] = {'fixture_fixed_lambda': fix1, 'fixture_grapa': fix2,
                            'remedy_key_matches_v27_order_on_logged_clusters': {'trials': trials, 'agree': agree}}

print(json.dumps(out, indent=1))
