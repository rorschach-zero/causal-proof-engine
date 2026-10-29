"""Round-44 checks for the Codex findings on PR #4 at 51a3405 (no reference code, no network).

Codex's PR #4 comment 6256095422 on 51a3405, four findings (two P1, two P2); two are checked here:
- finding 1 (RC-254): the batch b(k) of 17 section 3 item 3 is still read "over the cumulative point-in-time state ...
  re-enumerated at the audit", which the round-43 rule RC-250 replaced for the cluster itself.
- finding 2 (RC-255): the round-43 toy of RC-250 overwrites the shared component of a cluster linked across two
  consecutive boundaries, so a declared link loses its dependence.
Finding 3 (RC-256) is a commit identity and finding 4 (RC-257) a text repair of section 7; neither has a script.
"""
import hashlib
import json

import numpy as np
from scipy import stats

out = {}
PI, N = 0.5, 10_000


def draw(seed, cluster_id):
    digest = hashlib.sha256(f'{seed}:{cluster_id}'.encode()).digest()
    return int.from_bytes(digest, 'big') / 2 ** 256 < PI


# ================= finding 1 (RC-254): b(k) re-enumerated at the audit =================
# Batch calendar: window b = [20 (b - 1), 20 b), the snapshots of every universe anchored at t_reg,b = 20 b.
# U1 lists E at 15 as a singleton; U2 lists G at 25 as a singleton; U3 first links E and G in its batch-3 snapshot.
# - version 40 for the cluster (RC-250): read once, from the union anchored at the batch that draws it: E at batch 1,
#   G at batch 2 (the batch-2 union holds no E-G link);
# - version 40 for b(k) (17 lines 821-824): the first window holding a member's listing time, over the cumulative state
#   re-enumerated at the audit: the audit's union makes E+G one cluster, whose first member E falls in window 1;
# - remedy: b(k) is the batch at which the union anchored to date first holds a member of k, and the audit reads it
#   from that batch's anchored union, so G keeps b = 2 and the seed s_2.
listing = {'E': 15, 'G': 25}
first_link_batch = 3
window = {e: t // 20 + 1 for e, t in listing.items()}
out['finding 1, RC-254: batch of G (U1: E at 15, U2: G at 25, U3: E-G link from the batch-3 snapshot)'] = {
    'drawn by the registrar (one reading, RC-250)': {'cluster': 'G', 'b(k)': window['G'], 'seed': f"s_{window['G']}"},
    'version 40 b(k) re-enumerated at the audit': {'cluster': 'E+G', 'b(k)': min(window.values()),
                                                   'seed': f"s_{min(window.values())}"},
    'link first anchored at batch': first_link_batch,
    'remedy': {'cluster': 'G', 'b(k)': window['G'], 'seed': f"s_{window['G']}",
               'E-G link': 'merges nothing; joins the variance blocks of E and G'},
}
registrar = [draw('round44-s2', f'G{n}') for n in range(N)]
audit = [draw('round44-s1', f'E{n}+G{n}') for n in range(N)]
out['finding 1, RC-254: draws of G over 10,000 such pairs, pi = 0.5'] = {
    'registrar (G with s_2) and version-40 audit (E+G with s_1) differ': sum(a != b for a, b in zip(registrar, audit)),
    'differ under the remedy (b(k) read at the drawing batch)': 0,
}


# ================= finding 2 (RC-255): the shared component of a linked chain =================
# Exactly null law of 16 Appendix AQ: G blocks of 10 clusters; at each block boundary each cluster of block b is linked
# with probability q to the cluster in the same slot of block b + 1; every cluster is drawn (pi = 1). Two
# constructions of the dependence:
# - `round 43`: the Appendix AQ loop, which gives each linked pair a fresh common component and so overwrites the
#   component of a cluster linked on both sides (its link to the earlier block is lost);
# - `chain`: one common component of variance r per connected chain of links in a slot, so every declared linked
#   pair, and every pair of one chain, shares variance r (r = 0.9) of its unit variance.
# Statistic of 17 section 6 as in Appendix AQ: the mean over clusters with the block-sum variance on G - 1 df,
# one-sided at the 0.95 t quantile, on calendar blocks and on blocks joined by every link.
def round43_values(rng, blocks, per, linked, r):
    x = rng.standard_normal((blocks, per))
    common = rng.standard_normal((blocks - 1, per))
    for b in range(blocks - 1):
        idx = linked[b]
        if idx.any():
            e1 = rng.standard_normal(idx.sum())
            e2 = rng.standard_normal(idx.sum())
            x[b, idx] = np.sqrt(r) * common[b, idx] + np.sqrt(1 - r) * e1
            x[b + 1, idx] = np.sqrt(r) * common[b, idx] + np.sqrt(1 - r) * e2
    return x


def chain_values(rng, blocks, per, linked, r):
    chain = np.vstack([np.zeros((1, per), dtype=int), np.cumsum(~linked, axis=0)])
    in_chain = np.zeros((blocks, per), dtype=bool)
    in_chain[:-1] |= linked
    in_chain[1:] |= linked
    common = rng.standard_normal((blocks, per))[chain, np.arange(per)]
    shared = np.sqrt(r) * common + np.sqrt(1 - r) * rng.standard_normal((blocks, per))
    return np.where(in_chain, shared, rng.standard_normal((blocks, per)))


def linked_pair_covariance(rng, values, blocks, q, r=0.9, per=10, reps=2_000):
    """Pooled sample covariance of the declared linked pairs (unit variances, so the target is r)."""
    prods = []
    for _ in range(reps):
        linked = rng.random((blocks - 1, per)) < q
        x = values(rng, blocks, per, linked, r)
        prods.append((x[:-1] * x[1:])[linked])
    return round(float(np.concatenate(prods).mean()), 3)


def size_table(rng, values, reps, blocks, q, r=0.9, per=10):
    reject_cal = reject_join = 0
    joined_counts = []
    for _ in range(reps):
        linked = rng.random((blocks - 1, per)) < q
        x = values(rng, blocks, per, linked, r)
        n = x.size
        theta = x.mean()
        for kind in ('calendar', 'joined'):
            if kind == 'calendar':
                sums = (x - theta).sum(axis=1)
            else:
                cut = np.concatenate(([True], ~linked.any(axis=1)))
                sums = np.add.reduceat((x - theta).sum(axis=1), np.flatnonzero(cut))
                joined_counts.append(len(sums))
            g = len(sums)
            if g < 2:
                continue
            se = np.sqrt((sums ** 2).sum() / n ** 2 * g / (g - 1))
            if theta / se > stats.t.ppf(0.95, g - 1):
                if kind == 'calendar':
                    reject_cal += 1
                else:
                    reject_join += 1
    return {'calendar blocks': reject_cal / reps, 'joined blocks': reject_join / reps,
            'mean joined G': round(float(np.mean(joined_counts)), 2)}


rng = np.random.default_rng(44)
out['finding 2, RC-255: mean product of declared linked pairs, G = 48, 2,000 replications (target 0.9)'] = {
    f'q={q}': {'round 43': linked_pair_covariance(rng, round43_values, 48, q),
               'chain': linked_pair_covariance(rng, chain_values, 48, q)}
    for q in (0.05, 0.2)
}
toy = {}
for blocks in (24, 48, 100):
    for q in (0.0, 0.02, 0.05, 0.2):
        toy[f'G={blocks}, q={q}'] = size_table(rng, chain_values, 20_000, blocks, q)
out['finding 2, RC-255: null rejection rate, one common component per linked chain, r = 0.9, 20,000 replications'] = toy

print(json.dumps(out, indent=1, ensure_ascii=False))
