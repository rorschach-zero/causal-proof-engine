"""Round-32 checks for the Codex findings on PR #4 at 11ff591 (no reference code, no network).

Codex's automatic review of 11ff591, posted as PR #4 comment 6250629385, two findings: item 1 (RC-213, the identity
of 9c6fdcdf, checked with git and not here), item 2 (RC-214, no unique batch b for a cluster whose members are
listed in different batch windows, so its draw and its registration id (b, cluster id) are not defined).

Draw of 17 section 2 item 2: 1{SHA-256(s_b || cluster id) < pi * 2^256}, s_b = SHA-256(batch digest || v_b)
(16 Appendix Z and AA). Monitor setting of RC-212 (Appendix AE): lambda = 0.5 fixed, threshold 1/alpha = 20.
"""
import hashlib
import json
import numpy as np

out = {}
PI, LAM, THRESH = 0.5, 0.5, 20.0


def drawn(s_b, cid, pi=PI):
    return int.from_bytes(hashlib.sha256(s_b + cid.encode()).digest(), 'big') < int(pi * 2 ** 256)


s = {b: hashlib.sha256(f'fixture batch {b} digest'.encode()
                       + hashlib.sha256(f'fixture beacon round after the anchor of batch {b}'.encode()).digest()
                       ).digest() for b in (1, 2)}

# ================= 6250629385/2 (RC-214): a cluster whose members are listed in two windows =================
# Calendar: windows [0, 10) and [10, 20), Delta_reg = 2, so t_reg,1 = 12 and t_reg,2 = 22. Cluster C: member m1 listed
# at 5 (window 1), member m2 listed at 14 (window 2). Version 28 keys the draw by s_b "of that batch" and the
# registration id by "b the batch whose window contains its candidate's listing time"; C has two such b.
# (a) The draw: over 10,000 cluster ids, the share whose draw under s_1 differs from the draw under s_2.
ids = [f'cluster-{i:05d}' for i in range(10_000)]
differ = sum(drawn(s[1], c) != drawn(s[2], c) for c in ids)
# (b) The registration id: C tied in maturity with a logged cluster L of batch 1 whose cluster id lies between, so
# (1, C) precedes (1, L) and (2, C) follows it. With the RC-212 fixture values (wealth 19, L at +0.2, C a drawn
# omission at the lower end -0.99), the choice of b decides whether the crossing at L is supported.
c_id, l_id = 'cluster-00100', 'cluster-00200'
w0, x_l, x_c_low = 19.0, 0.2, -0.99


def run(order):
    w = w0; peak = w0; prefix = None; seen = []
    for name, x in order:
        w *= 1 + LAM * x; seen.append(name)
        if w >= THRESH and prefix is None:
            prefix = list(seen)
        peak = max(peak, w)
    return {'peak': round(peak, 6), 'crossing_prefix': prefix, 'supported': prefix is not None and 'C' not in prefix}


keys = {'b=1': (1, c_id), 'b=2': (2, c_id)}
key_l = (1, l_id)
fix = {}
for name, key_c in keys.items():
    order = [('C', x_c_low), ('L', x_l)] if key_c < key_l else [('L', x_l), ('C', x_c_low)]
    fix[name] = {'C_before_L': key_c < key_l, **run(order)}
out['6250629385/2 RC-214 fixture'] = {
    'draw_differs_between_s1_and_s2': {'cluster_ids': len(ids), 'differ': differ, 'share': round(differ / len(ids), 4)},
    'registration_id_choice': fix,
    'support_depends_on_choice_of_b': fix['b=1']['supported'] != fix['b=2']['supported']}

# Remedy: b(k) is the first window, over the cohort's cumulative listing, holding a member of k; k's members are those
# listed in that window; a member listed in a later window is a post-registration member, outside every confirmatory
# statistic, and changes neither k's record, maturity, draw nor key. b(k) is a function of listing times alone, so it
# is the same from the snapshots and from the archive at the audit (a definition, not checked here).

# Why not Codex's alternative "require every cluster's members to share a window", read as: a cluster that turns out
# to span two windows leaves the primary. The second listing comes after the cluster's registration, and a source can
# list a follow-up member more often after an unfavourable first outcome. Exactly null toy: 600 clusters, increment
# +-0.2 with mean zero, a follow-up listed in a later window with probability q after a -0.2 and 0 after a +0.2,
# one-sided t at 1.645, 20,000 replications. Dropping spanning clusters selects on the outcome; the remedy keeps every
# cluster with its first-window membership, which is the honest sample.
rng = np.random.default_rng(3201)
REPS, N = 20_000, 600
x = rng.choice([-0.2, 0.2], (REPS, N))
u = rng.random((REPS, N))


def reject(mask):
    n = mask.sum(1)
    m = np.where(mask, x, 0).sum(1) / n
    v = (np.where(mask, x, 0) ** 2).sum(1) / n - m ** 2
    t = m / np.sqrt(v * n / (n - 1) / n)
    return round(float((t > 1.645).mean()), 4)


alt = {}
for q in (0.02, 0.05, 0.10):
    spans = (x < 0) & (u < q)
    alt[f'q={q}'] = {'drop_spanning_clusters': reject(~spans), 'remedy_first_window': reject(np.ones_like(spans))}
out['6250629385/2 RC-214 alternative'] = alt

print(json.dumps(out, indent=1))
