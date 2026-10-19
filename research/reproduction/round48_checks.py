"""Round-48 checks for the Codex findings on PR #4 at 1918c72 (no reference code, no network).

Codex's PR #4 comment 6258096826 on 1918c72, four findings (all P1); two are checked here:
- finding 1 (RC-267): the variance blocks project each component of the anchored union onto the calendar blocks of
  its primary clusters, and two components whose block sets overlap must be joined transitively; the round-47 helper
  `block_partition` overwrote a shared block's parent and returned a set of blocks that is not their closure;
- finding 4 (RC-270): every late partition has its own simulated c*, while the confidence of each point is
  1 - gamma_cal/(K_max * S_max) with K_max summed over the components only; the cost of also counting the late
  partitions in K_max is shown on the certification bound.
Finding 2 (RC-268) is a commit identity and finding 3 (RC-269) a contract row; they have no script.
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


def block_partition_v47(block_of, links):
    """The round-47 helper (round47_checks.py), verbatim: a shared block keeps the parent of the last group read."""
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


def block_partition(block_of, links):
    """Remedy: the variance blocks are the connected components of the bipartite graph of the components of the union
    and the calendar blocks, a component adjacent to every block that holds one of its primary clusters."""
    nodes = list(block_of) + [v for link in links for v in link if v not in block_of]
    comp = components(nodes, links)
    graph = [(('component', comp[c]), ('block', b)) for c, b in block_of.items()]
    joined = components([('block', b) for b in block_of.values()] + [('component', comp[c]) for c in block_of], graph)
    blocks = sorted(set(block_of.values()))
    return frozenset(frozenset(b for b in blocks if joined[('block', b)] == root)
                     for root in {joined[('block', b)] for b in blocks})


def show(part):
    return ' '.join(sorted('{' + ', '.join(map(str, sorted(p))) + '}' for p in part))


out = {}

# Finding 1, fixture. Component A holds primary clusters a1 (block 1) and a2 (block 2), component B holds b2 (block 2)
# and b3 (block 3); A and B share no link. Blocks 1, 2 and 3 must form one variance block.
block_of = {'a1': 1, 'a2': 2, 'b2': 2, 'b3': 3}
links = [('a1', 'a2'), ('b2', 'b3')]
out['finding 1, RC-267: A on blocks 1-2, B on blocks 2-3'] = {
    'round-47 helper': show(block_partition_v47(block_of, links)),
    'remedy (bipartite components)': show(block_partition(block_of, links)),
    'remedy, links read in the other order': show(block_partition(dict(reversed(list(block_of.items()))),
                                                                  links[::-1])),
}

# Finding 1, the Appendix AU fixtures under the remedy: no block set there overlaps another, so every output stands.
au = {}
for k in range(1, 7):
    bo = {**{f'E{i}': 2 * i for i in range(k)}, **{f'F{i}': 2 * i + 1 for i in range(k)}}
    late = [(f'E{i}', f'X{i}') for i in range(k)] + [(f'X{i}', f'F{i}') for i in range(k)]
    subsets = [list(sub) for r in range(len(late) + 1) for sub in itertools.combinations(late, r)]
    au[f'k = {k}'] = {
        'distinct partitions, round-47 helper': len({block_partition_v47(bo, sub) for sub in subsets}),
        'distinct partitions, remedy': len({block_partition(bo, sub) for sub in subsets}),
    }
au['E-F archived at 95, remedy'] = sorted({show(block_partition({'E': 1, 'F': 2}, sub)) for sub in ([], [('E', 'F')])})
out['finding 1, RC-267: Appendix AU fixtures under the remedy'] = au

# Finding 1, size. The chain law of 16 Appendix AR with every cluster drawn: G blocks of 10 clusters in 10 slots, each
# cluster linked with probability q to the cluster in the same slot of the next block, one common component of
# variance 0.9 per chain of links; every link is anchored, none late. Chains in different slots overlap on a block
# whenever one ends where another starts. The statistic of Appendix AR (the mean, block-sum variance on G - 1 df,
# nominal 0.95 t quantile, G < 2 no rejection) on the variance blocks of each rule.
REPS, PER, R = 10_000, 10, 0.9
rng = np.random.default_rng(48)


def chain_values(blocks, linked):
    chain = np.vstack([np.zeros((1, PER), dtype=int), np.cumsum(~linked, axis=0)])
    in_chain = np.zeros((blocks, PER), dtype=bool)
    in_chain[:-1] |= linked
    in_chain[1:] |= linked
    common = rng.standard_normal((blocks, PER))[chain, np.arange(PER)]
    shared = np.sqrt(R) * common + np.sqrt(1 - R) * rng.standard_normal((blocks, PER))
    return np.where(in_chain, shared, rng.standard_normal((blocks, PER)))


def rejects(x, part):
    theta, n = x.mean(), x.size
    label = {b: i for i, p in enumerate(sorted(part, key=min)) for b in p}
    g = len(part)
    if g < 2:
        return False
    sums = np.zeros(g)
    np.add.at(sums, [label[b] for b in range(x.shape[0])], (x - theta).sum(axis=1))
    se = np.sqrt((sums ** 2).sum() / n ** 2 * g / (g - 1))
    return bool(theta / se > stats.t.ppf(0.95, g - 1))


size = {}
for blocks in (24, 48):
    bo = {(b, s): b for b in range(blocks) for s in range(PER)}
    for q in (0.05, 0.2):
        rej = {'calendar blocks': 0, 'round-47 helper': 0, 'remedy': 0}
        not_closed = 0
        for _ in range(REPS):
            linked = rng.random((blocks - 1, PER)) < q
            x = chain_values(blocks, linked)
            ln = [((b, s), (b + 1, s)) for b, s in zip(*np.nonzero(linked))]
            p47, p48 = block_partition_v47(bo, ln), block_partition(bo, ln)
            not_closed += p47 != p48
            rej['calendar blocks'] += rejects(x, [{b} for b in range(blocks)])
            rej['round-47 helper'] += rejects(x, p47)
            rej['remedy'] += rejects(x, p48)
        size[f'G={blocks}, q={q}'] = {**{key: v / REPS for key, v in rej.items()},
                                      'share of samples where the two rules differ': not_closed / REPS}
out['finding 1, RC-267: null rejection rate, chain law, r = 0.9, 10,000 replications'] = size

# Finding 4, cost. On one simulated point at R = 20,000 replications, the largest number of rejections whose exact
# one-sided Clopper-Pearson upper bound at confidence 1 - gamma_cal / (K * S * 2^m) is at most alpha - eta_max - gamma_cal
# = 0.04 (alpha = 0.05, eta_max = 0, gamma_cal = 0.01, K * S = 1), against m = 0 (the late partitions not counted).
REPL, LEVEL, GAMMA = 20_000, 0.04, 0.01


def max_certifiable(conf):
    lo, hi = 0, REPL
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if stats.beta.ppf(conf, mid + 1, REPL - mid) <= LEVEL:
            lo = mid
        else:
            hi = mid - 1
    return lo


out['finding 4, RC-270: largest certifiable observed size at R = 20,000, bound 0.04'] = {
    f'2^M_late = {2 ** m}': max_certifiable(1 - GAMMA / 2 ** m) / REPL for m in range(7)}

print(json.dumps(out, indent=1, ensure_ascii=False))
