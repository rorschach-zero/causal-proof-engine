"""Round-46 checks for the Codex findings on PR #4 at e77192f (no reference code, no network).

Codex's PR #4 comment 6257059140 on e77192f, three findings (all P1); one is checked here:
- finding 1 (RC-261): the RC-260 rule rejects only if the statistic rejects on the anchored variance blocks and on the
  blocks extended by every link archived by T_D; its size bound holds when the late links are all genuine or all
  outcome-selected, and a cohort with both is covered by neither.
Finding 2 (RC-262) is a commit identity and finding 3 (RC-263) a row of the specification; neither has a script.
"""
import json

import numpy as np
from scipy import stats

# Law. G calendar blocks of 10 clusters in 10 slots, every cluster drawn (pi = 1), the chain law of 16 Appendix AR:
# one common component of variance r = 0.9 per connected chain of links in a slot. With pi = 1 a link between the
# clusters of blocks b and b + 1 joins those two blocks (RC-259), so a variance partition is fixed by its set of
# joined boundaries and its variance blocks are runs of consecutive calendar blocks.
# - early links: archived by T_W, each slot of each boundary linked with probability 0.02 (Appendix AS);
# - genuine late links: true dependence first archived after T_E and by T_D; each boundary is genuinely late-linked
#   with probability p_g, in all 10 slots, so that a few late boundaries carry a material dependence;
# - selected late links: no dependence; the party that archives them sees the outcomes and chooses, among K = 10
#   candidate sets (each boundary in a set with probability p_s = 0.05), the first under which the rule rejects.
# Rules, each at the nominal 0.95 t quantile on g - 1 df, g < 2 no rejection:
# - anchored: the blocks of the early links only;
# - extended: the blocks of the early links and every late link;
# - RC-260 (version 42): anchored and extended both reject;
# - every subset (remedy): the statistic rejects on the blocks of the early links and of every subset of the late
#   links, so a rejection implies a rejection on the blocks of the genuine subset, whichever links are selected;
#   a cohort whose late links join more than M = 12 boundaries that no early link joins is not confirmatory.
REPS, PER, R, Q_EARLY, P_SEL, K, M = 10_000, 10, 0.9, 0.02, 0.05, 10, 12
rng = np.random.default_rng(46)
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
    out = np.zeros(rows, dtype=bool)
    ok = g >= 2
    se = np.sqrt((sums[ok] ** 2).sum(axis=1) / n ** 2 * g[ok] / (g[ok] - 1))
    out[ok] = theta / se > np.array([crit[v] for v in g[ok]])
    return out


def every_subset(theta, n, resid, early_b, late_b):
    extra = np.flatnonzero(late_b & ~early_b)
    if extra.size > M:
        return False, True
    bits = (np.arange(2 ** extra.size)[:, None] >> np.arange(extra.size)) & 1
    joined = np.tile(early_b, (bits.shape[0], 1))
    joined[:, extra] = bits.astype(bool)
    return bool(reject(theta, n, resid, joined).all()), False


out = {}
for blocks in (24, 48):
    for case, p_gen in (('selected', 0.0), ('genuine', 0.1), ('mixed', 0.1), ('genuine', 0.2), ('mixed', 0.2)):
        rej = {'anchored': 0, 'extended': 0, 'RC-260': 0, 'every subset': 0}
        capped, n_late = 0, []
        for _ in range(REPS):
            early = rng.random((blocks - 1, PER)) < Q_EARLY
            early_b = early.any(axis=1)
            gen_b = rng.random(blocks - 1) < p_gen
            x = chain_values(blocks, early | gen_b[:, None])
            n, theta = x.size, x.mean()
            resid = (x - theta).sum(axis=1)
            if case == 'genuine':
                candidates = [gen_b]
            else:
                candidates = [gen_b | (rng.random(blocks - 1) < P_SEL) for _ in range(K)]
            r_anch = bool(reject(theta, n, resid, early_b)[0])
            r_ext = reject(theta, n, resid, np.array([early_b | c for c in candidates]))
            rej['anchored'] += r_anch
            rej['extended'] += bool(r_ext.any())
            rej['RC-260'] += r_anch and bool(r_ext.any())
            n_late.append(int((candidates[0] & ~early_b).sum()))
            if r_anch:
                for c in candidates:
                    r_sub, was_capped = every_subset(theta, n, resid, early_b, c)
                    capped += was_capped
                    if r_sub:
                        rej['every subset'] += 1
                        break
        out[f'G={blocks}, p_genuine={p_gen}, {case}'] = {
            **{k: v / REPS for k, v in rej.items()},
            'mean late boundaries of the first candidate': round(float(np.mean(n_late)), 2),
            'candidate evaluations above M': capped,
        }

print(json.dumps({'finding 1, RC-261: null rejection rate, chain law, r = 0.9, 10,000 replications': out},
                 indent=1, ensure_ascii=False))
