"""Round-45 checks for the Codex findings on PR #4 at f44abbb (no reference code, no network).

Codex's PR #4 comment 6256562747 on f44abbb, three findings (all P1); two are checked here:
- finding 2 (RC-259): the joining rule of 17 section 3 item 2 joins the variance blocks of a link only when both of its
  endpoints are primary clusters, so two drawn clusters connected only through an undrawn cluster stay apart;
- finding 3 (RC-260): a link first archived after T_E joins nothing, so a genuine late dependency leaves dependent
  primary clusters in separate variance blocks.
Finding 1 (RC-258) is a commit identity; it has no script.
"""
import json

import numpy as np
from scipy import stats

out = {}


def components(nodes, edges):
    parent = {n: n for n in nodes}

    def find(n):
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    for a, b in edges:
        parent[find(a)] = find(b)
    return {n: find(n) for n in nodes}


# ================= finding 2 (RC-259): a path through an undrawn cluster =================
# Final anchored union: E in calendar block 1, X in block 2, F in block 3; links E-X and X-F; X is sampled out.
# - version 41 (17 section 3 item 2): every link "that connects primary clusters of different calendar blocks" joins
#   those blocks; neither E-X nor X-F has two primary endpoints, so nothing is joined;
# - remedy: the connected components of the complete final union (drawn or not), projected onto the primary clusters;
#   the blocks of the primary clusters of one component form one variance block.
block = {'E': 1, 'X': 2, 'F': 3}
drawn = {'E': True, 'X': False, 'F': True}
links = [('E', 'X'), ('X', 'F')]
v41 = sorted({tuple(sorted((block[a], block[b]))) for a, b in links if drawn[a] and drawn[b] and block[a] != block[b]})
comp = components(block, links)
joined = {}
for n in block:
    if drawn[n]:
        joined.setdefault(comp[n], set()).add(block[n])
out['finding 2, RC-259: E (block 1) - X (block 2, undrawn) - F (block 3)'] = {
    'version 41 joined block pairs': v41,
    'remedy variance blocks of the primary clusters': sorted(sorted(s) for s in joined.values()),
}


# Toy. Exactly null law of 16 Appendix AR (one common component of variance r = 0.9 per connected chain of links in a
# slot; G blocks of 10 clusters; each cluster linked with probability q to the cluster in the same slot of the next
# block), now with sampling: each cluster is drawn independently with probability pi. Statistic of Appendix AR on the
# drawn clusters: the mean with the block-sum variance on G - 1 df, one-sided at the 0.95 t quantile.
def chain_values(rng, blocks, per, linked, r):
    chain = np.vstack([np.zeros((1, per), dtype=int), np.cumsum(~linked, axis=0)])
    in_chain = np.zeros((blocks, per), dtype=bool)
    in_chain[:-1] |= linked
    in_chain[1:] |= linked
    common = rng.standard_normal((blocks, per))[chain, np.arange(per)]
    shared = np.sqrt(r) * common + np.sqrt(1 - r) * rng.standard_normal((blocks, per))
    return np.where(in_chain, shared, rng.standard_normal((blocks, per)))


def block_labels(blocks, per, link_sets, drawn, rule):
    """Variance block of each calendar block. `primary`: a link joins its two blocks only when both endpoints are
    drawn (version 41); `component`: the blocks of the drawn clusters of one connected chain are joined (remedy)."""
    parent = list(range(blocks))

    def find(b):
        while parent[b] != b:
            parent[b] = parent[parent[b]]
            b = parent[b]
        return b

    for linked in link_sets:
        if rule == 'primary':
            for b, s in zip(*np.nonzero(linked & drawn[:-1] & drawn[1:])):
                parent[find(b)] = find(b + 1)
        else:
            chain = np.vstack([np.zeros((1, per), dtype=int), np.cumsum(~linked, axis=0)])
            for s in range(per):
                first = {}
                for b in np.flatnonzero(drawn[:, s]):
                    c = chain[b, s]
                    if c in first:
                        parent[find(b)] = find(first[c])
                    else:
                        first[c] = b
    return np.array([find(b) for b in range(blocks)])


def t_reject(x, drawn, labels):
    n = drawn.sum()
    if n == 0:
        return False, 0
    theta = x[drawn].mean()
    resid = np.where(drawn, x - theta, 0.0).sum(axis=1)
    _, inv = np.unique(labels, return_inverse=True)
    sums = np.bincount(inv, weights=resid)
    g = len(sums)
    if g < 2:
        return False, g
    se = np.sqrt((sums ** 2).sum() / n ** 2 * g / (g - 1))
    return bool(theta / se > stats.t.ppf(0.95, g - 1)), g


def compose(*link_sets):
    """Chains of the union of several link sets on the same adjacent-slot graph."""
    return np.logical_or.reduce(link_sets)


rng = np.random.default_rng(45)
REPS, PER, R = 10_000, 10, 0.9
toy = {}
for blocks in (24, 48):
    for q in (0.05, 0.1):
        for pi in (1.0, 0.5):
            rej = {'primary': 0, 'component': 0}
            gs = {'primary': [], 'component': []}
            for _ in range(REPS):
                linked = rng.random((blocks - 1, PER)) < q
                x = chain_values(rng, blocks, PER, linked, R)
                drawn = rng.random((blocks, PER)) < pi
                for rule in rej:
                    rejected, g = t_reject(x, drawn, block_labels(blocks, PER, [linked], drawn, rule))
                    rej[rule] += rejected
                    gs[rule].append(g)
            toy[f'G={blocks}, q={q}, pi={pi}'] = {
                'version 41 (links with two primary endpoints)': rej['primary'] / REPS,
                'remedy (components of the final union)': rej['component'] / REPS,
                'mean G version 41': round(float(np.mean(gs['primary'])), 2),
                'mean G remedy': round(float(np.mean(gs['component'])), 2),
            }
out['finding 2, RC-259: null rejection rate, chain law, r = 0.9, 10,000 replications'] = toy


# ================= finding 3 (RC-260): links first archived after T_E =================
# Two link sets on the same law: `early` links (archived by T_W, rate q_e) and `late` links (first archived after T_E
# and by T_D, rate q_l). Every cluster is drawn (pi = 1) and the remedy of finding 2 is used throughout.
# Statistics: `early` joins the blocks by the early links only (version 41); `all` by every link archived by T_D;
# `both` rejects only if `early` and `all` reject (the remedy). Two cases:
# - genuine: the late links are true dependence (the chain law over early and late links together);
# - selected: the late links carry no dependence (chain law over the early links only), and the party writing them
#   sees the outcomes and chooses, among K = 10 candidate late link sets of rate q_l, one under which `all` rejects,
#   if any does (an outcome-selected link set).
K = 10
late = {}
for blocks in (24, 48):
    for q_e, q_l in ((0.02, 0.05), (0.02, 0.1)):
        for case in ('genuine', 'selected'):
            rej = {'early': 0, 'all': 0, 'both': 0}
            for _ in range(REPS):
                early = rng.random((blocks - 1, PER)) < q_e
                drawn = np.ones((blocks, PER), dtype=bool)
                if case == 'genuine':
                    late_links = rng.random((blocks - 1, PER)) < q_l
                    x = chain_values(rng, blocks, PER, compose(early, late_links), R)
                    candidates = [late_links]
                else:
                    x = chain_values(rng, blocks, PER, early, R)
                    candidates = [rng.random((blocks - 1, PER)) < q_l for _ in range(K)]
                r_early, _ = t_reject(x, drawn, block_labels(blocks, PER, [early], drawn, 'component'))
                r_all = False
                for late_links in candidates:
                    r_all, _ = t_reject(x, drawn, block_labels(blocks, PER, [compose(early, late_links)], drawn,
                                                              'component'))
                    if r_all:
                        break
                rej['early'] += r_early
                rej['all'] += r_all
                rej['both'] += r_early and r_all
            late[f'G={blocks}, q_early={q_e}, q_late={q_l}, {case}'] = {k: v / REPS for k, v in rej.items()}
out['finding 3, RC-260: null rejection rate with late links, r = 0.9, 10,000 replications'] = late

print(json.dumps(out, indent=1, ensure_ascii=False))
