"""Round-47 checks for the Codex findings on PR #4 at 7c23175 (no reference code, no network).

Codex's PR #4 comment 6257574713 on 7c23175, three findings (two P1, one P2); two are checked here:
- finding 2 (RC-265): M_late counts the distinct pairs of anchored variance blocks that single late links connect, so
  late links that reach primary blocks only through a component without a primary cluster count zero while their
  subsets give several partitions;
- finding 3 (RC-266): the final anchored union is read from the last batch's snapshots and the late links from
  (T_E, T_D], so a link first archived after the last snapshot and by T_E is in neither set.
Finding 1 (RC-264) is a commit identity; it has no script.
"""
import itertools
import json

import numpy as np
from scipy import stats


def components(nodes, links):
    parent = {v: v for v in nodes}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for a, b in links:
        parent[find(a)] = find(b)
    return {v: find(v) for v in nodes}


def block_partition(block_of, links):
    """The partition of the calendar blocks of the primary clusters into variance blocks under `links`."""
    comp = components(list(block_of) + [v for link in links for v in link if v not in block_of], links)
    groups = {}
    for cluster, block in block_of.items():
        groups.setdefault(comp[cluster], set()).add(block)
    blocks = sorted({b for b in block_of.values()})
    parent = {b: b for b in blocks}
    for group in groups.values():
        first = min(group)
        for b in group:
            parent[b] = first
    return frozenset(frozenset(b for b in blocks if parent[b] == root) for root in set(parent.values()))


def distinct_partitions(block_of, anchored, late):
    return {block_partition(block_of, anchored + list(sub)) for r in range(len(late) + 1)
            for sub in itertools.combinations(late, r)}


def count_v43(block_of, anchored, late):
    """Version 43: distinct pairs of anchored variance blocks that one late link connects."""
    part = block_partition(block_of, anchored)
    vblock = {c: next(p for p in part if block_of[c] in p) for c in block_of}
    return len({frozenset((vblock[a], vblock[b])) for a, b in late
                if a in vblock and b in vblock and vblock[a] != vblock[b]})


def count_remedy(block_of, anchored, late):
    """Remedy: distinct pairs of nodes that late links connect, a node being an anchored variance block or a component
    of the anchored union without a primary cluster (an event absent from the union is a component of its own)."""
    nodes = list(block_of) + [v for link in anchored + late for v in link if v not in block_of]
    comp = components(nodes, anchored)
    part = block_partition(block_of, anchored)
    node = {v: comp[v] for v in nodes}
    for c in block_of:
        vb = next(p for p in part if block_of[c] in p)
        for v in nodes:
            if comp[v] == comp[c]:
                node[v] = vb
    return len({frozenset((node[a], node[b])) for a, b in late if node[a] != node[b]})


out = {}

# Finding 2. k disjoint paths E_i - X_i - F_i: E_i primary in block 2i, X_i a sampled-out cluster in no anchored link,
# F_i primary in block 2i + 1, both links of each path first archived after T_E (k = 1 is the RC-259 topology).
f2 = {}
for k in range(1, 7):
    block_of = {**{f'E{i}': 2 * i for i in range(k)}, **{f'F{i}': 2 * i + 1 for i in range(k)}}
    late = [(f'E{i}', f'X{i}') for i in range(k)] + [(f'X{i}', f'F{i}') for i in range(k)]
    f2[f'k = {k}'] = {
        'late links': len(late),
        'distinct partitions over the subsets': len(distinct_partitions(block_of, [], late)),
        'version-43 count (bound 2^count)': count_v43(block_of, [], late),
        'remedy count (bound 2^count)': count_remedy(block_of, [], late),
    }
out['finding 2, RC-265: late links through sampled-out clusters, no anchored link'] = f2

# Finding 3. Timeline: last batch window ends at T_W = 80, its snapshots are anchored at t_reg = 90, T_E = 100,
# T_D = 200. E is primary in block 1, F in block 2; their link is first archived at 95 by one eligible universe.
T_SNAP, T_E, T_D = 90, 100, 200
links = [{'link': ('E', 'F'), 'archived': 95}]
block_of = {'E': 1, 'F': 2}
anchored = [x['link'] for x in links if x['archived'] <= T_SNAP]
late_v43 = [x['link'] for x in links if T_E < x['archived'] <= T_D]
late_remedy = [x['link'] for x in links if x['archived'] <= T_D and x['link'] not in anchored]


def show(parts):
    return sorted(' '.join(sorted('{' + ', '.join(map(str, sorted(p))) + '}' for p in part)) for part in parts)


out['finding 3, RC-266: link E-F first archived at 95, snapshot at 90, T_E = 100'] = {
    'version 43': {'anchored links': ['-'.join(x) for x in anchored], 'late links': ['-'.join(x) for x in late_v43],
                   'partitions evaluated': show(distinct_partitions(block_of, anchored, late_v43))},
    'remedy (every link archived by T_D outside the final anchored union is late)': {
        'late links': ['-'.join(x) for x in late_remedy], 'partitions evaluated': show(distinct_partitions(block_of, anchored, late_remedy))},
}

# Finding 3, size. The chain law of 16 Appendix AR with every cluster drawn: G blocks of 10 clusters in 10 slots, one
# common component of variance 0.9 per chain of links in a slot; links in the last snapshot at 0.02 per slot of each
# boundary, and each boundary genuinely linked in all slots, first archived after the last snapshot and by T_E, with
# probability p; no link after T_E. Version 43 reads only the snapshot links; the remedy reads the others as late
# links and rejects only on every subset. Nominal 0.95 t quantile on g - 1 df, g < 2 no rejection.
REPS, PER, R, Q_SNAP = 10_000, 10, 0.9, 0.02
rng = np.random.default_rng(47)
crit = {g: stats.t.ppf(0.95, g - 1) for g in range(2, 50)}


def chain_values(blocks, linked):
    chain = np.vstack([np.zeros((1, PER), dtype=int), np.cumsum(~linked, axis=0)])
    in_chain = np.zeros((blocks, PER), dtype=bool)
    in_chain[:-1] |= linked
    in_chain[1:] |= linked
    common = rng.standard_normal((blocks, PER))[chain, np.arange(PER)]
    shared = np.sqrt(R) * common + np.sqrt(1 - R) * rng.standard_normal((blocks, PER))
    return np.where(in_chain, shared, rng.standard_normal((blocks, PER)))


def reject(theta, n, resid, joined):
    """Rows of `joined` (partitions x boundaries) are joined-boundary sets; True where the statistic rejects."""
    joined = np.atleast_2d(joined)
    rows, blocks = joined.shape[0], resid.size
    labels = np.hstack([np.zeros((rows, 1), dtype=int), np.cumsum(~joined, axis=1)])
    sums = np.bincount((labels + blocks * np.arange(rows)[:, None]).ravel(), weights=np.tile(resid, rows),
                       minlength=rows * blocks).reshape(rows, blocks)
    g = labels[:, -1] + 1
    res = np.zeros(rows, dtype=bool)
    ok = g >= 2
    se = np.sqrt((sums[ok] ** 2).sum(axis=1) / n ** 2 * g[ok] / (g[ok] - 1))
    res[ok] = theta / se > np.array([crit[v] for v in g[ok]])
    return res


size = {}
for blocks in (24, 48):
    for p in (0.1, 0.2):
        rej_v43 = rej_remedy = 0
        for _ in range(REPS):
            snap = rng.random((blocks - 1, PER)) < Q_SNAP
            snap_b = snap.any(axis=1)
            gap = rng.random(blocks - 1) < p
            x = chain_values(blocks, snap | gap[:, None])
            n, theta = x.size, x.mean()
            resid = (x - theta).sum(axis=1)
            rej_v43 += bool(reject(theta, n, resid, snap_b)[0])
            extra = np.flatnonzero(gap & ~snap_b)
            bits = (np.arange(2 ** extra.size)[:, None] >> np.arange(extra.size)) & 1
            joined = np.tile(snap_b, (bits.shape[0], 1))
            joined[:, extra] = bits.astype(bool)
            rej_remedy += bool(reject(theta, n, resid, joined).all())
        size[f'G={blocks}, p={p}'] = {'version 43 (snapshot links only)': rej_v43 / REPS,
                                      'remedy (every subset of the later links)': rej_remedy / REPS}
out['finding 3, RC-266: null rejection rate, chain law, r = 0.9, 10,000 replications'] = size

print(json.dumps(out, indent=1, ensure_ascii=False))
