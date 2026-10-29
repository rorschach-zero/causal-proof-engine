"""Round-43 checks for the Codex findings on PR #4 at 4fb9fd0 (no reference code, no network).

Codex's PR #4 comment 6255462322 on 4fb9fd0, four findings (three P1, one P2); three are checked here:
- finding 1 (RC-250): a cross-universe link that first appears in a later batch's snapshot joins events that version 39
  has already drawn apart, and version 39 reads the union both at each batch anchor and, cumulatively, at the audit.
- finding 3 (RC-252): the Phase 2 late-record measurement starts at deadline + window, said to be possibly later than
  T_D, so that it would not bound a late record of an early public occurrence.
- finding 4 (RC-253): the flow sequences of the section 7 YAML hold unquoted prose, which YAML reads as mappings and
  separate items.
Finding 2 (RC-251) is a commit identity and has no script.
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


def components(links, events):
    """Connected components of the events under the given links, each written as its sorted ids joined by '+'."""
    parent = {e: e for e in events}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for a, b in links:
        parent[find(b)] = find(a)
    groups = {}
    for e in events:
        groups.setdefault(find(e), set()).add(e)
    return sorted('+'.join(sorted(g)) for g in groups.values())


# ================= finding 1 (RC-250): a cross-universe link anchored after the first draw =================
# Batch calendar: window b = [20 (b - 1), 20 b), the snapshots of every universe anchored at t_reg,b = 20 b.
# U1 lists E at 15 as a singleton; U3 lists F at 18 as a singleton; U2 lists E and F at 30 and links them, so the E-F
# link is first in U2's batch-2 snapshot. Case B: F is in U2 only (listed at 30).
# - version 39 at the batch-1 anchor (17 lines 772-776): the union of the snapshots anchored to date;
# - version 39 at the audit (17 lines 790-792): b(k) "over the cumulative point-in-time state of the cohort's
#   universes (every universe snapshot anchored to date, re-enumerated at the audit)";
# - remedy: each cluster is fixed by the union anchored with its own batch b(k); a later-anchored link merges no
#   registered cluster, and an event first listed in a later window that it joins to k is a post-registration member.
snapshots = {1: {'events': {'E': 15, 'F': 18}, 'links': []},
             2: {'events': {'E': 15, 'F': 18}, 'links': [('E', 'F')]}}
at_batch_1 = components(snapshots[1]['links'], snapshots[1]['events'])
at_audit = components(snapshots[2]['links'], snapshots[2]['events'])
out['finding 1, RC-250: clusters of E and F (U1: E at 15, U3: F at 18, U2: E-F link from the batch-2 snapshot)'] = {
    'version 39 at the batch-1 anchor (drawn with s_1)': at_batch_1,
    'version 39 re-enumerated at the audit (cumulative union)': at_audit,
    'remedy: registered clusters': at_batch_1,
    'remedy: the E-F link': 'conflict reported by count and universe; joins the variance blocks of E and F',
}
case_b = {'E': 15, 'F': 30}
out['finding 1, RC-250, case B: F in U2 only, listed at 30 with its link to E'] = {
    'batch-1 union': components([], {'E': 15}),
    'remedy: cluster of F': 'E (b(k) = 1); F is a post-registration member, never a cluster of its own',
}
apart = [(draw('round43-s1', f'E{n}'), draw('round43-s1', f'F{n}')) for n in range(N)]
whole = [draw('round43-s1', f'E{n}+F{n}') for n in range(N)]
out['finding 1, RC-250: draws of 10,000 such pairs, pi = 0.5'] = {
    'E and F drawn apart at batch 1 and not both in the sample': sum(not (a and b) for a, b in apart),
    'E and F drawn apart, exactly one in the sample': sum(a != b for a, b in apart),
    'registrar sample (apart) and audit re-enumeration (E+F whole) differ on E': sum(
        a != w for (a, _), w in zip(apart, whole)),
    'differ under the remedy (one reading)': 0,
}


# Size of the primary when late cross-universe links join clusters of adjacent calendar blocks. Exactly null law:
# G blocks of 10 clusters; at each block boundary each of the 10 clusters of block b is linked with probability q to
# the cluster in the same slot of block b + 1, and a linked pair shares a component of variance r (r = 0.9) of its
# unit variance; every cluster is drawn (pi = 1, so only the dependence is at issue). Statistic of 17 section 6: the
# mean over clusters with the block-sum variance on G - 1 df, one-sided at the 0.95 t quantile; `calendar` uses the
# calendar blocks, `joined` the blocks joined by every link (a chain of linked blocks is one variance block).
def size_table(rng, reps, blocks, q, r=0.9, per=10):
    reject_cal = reject_join = 0
    joined_counts = []
    for _ in range(reps):
        x = rng.standard_normal((blocks, per))
        linked = rng.random((blocks - 1, per)) < q
        common = rng.standard_normal((blocks - 1, per))
        for b in range(blocks - 1):
            idx = linked[b]
            if idx.any():
                e1 = rng.standard_normal(idx.sum())
                e2 = rng.standard_normal(idx.sum())
                x[b, idx] = np.sqrt(r) * common[b, idx] + np.sqrt(1 - r) * e1
                x[b + 1, idx] = np.sqrt(r) * common[b, idx] + np.sqrt(1 - r) * e2
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


rng = np.random.default_rng(43)
toy = {}
for blocks in (24, 48, 100):
    for q in (0.0, 0.02, 0.05, 0.2):
        toy[f'G={blocks}, q={q}'] = size_table(rng, 20_000, blocks, q)
out['finding 1, RC-250: null rejection rate, 10 clusters per block, linked pairs share r = 0.9, 20,000 replications'] = toy


# ================= finding 3 (RC-252): the start of the late-record measurement =================
# 17 section 6 (Accrual): T_R = T_A - H_max, and a cluster is eligible only if listed before tau <= T_E <= T_R with a
# declared horizon (latency window included) of at most H_max; T_D = T_A + D (17 section 3 item 3, RC-149).
# Codex's case: an eligible event E occurs publicly at 90 < T_E = 100, and the occurrence archive records it only
# after T_D. A record is late iff it is after T_D; the Phase 2 bound is on P(record - (deadline + window) > D).
T_A, H_max, D, T_E = 400, 300, 60, 100
T_R, T_D = T_A - H_max, T_A + D
grid = [(listing, horizon) for listing in range(0, T_E, 5) for horizon in range(1, H_max + 1, 7)]
maturities = [listing + horizon for listing, horizon in grid]
record = T_D + 1
E = {'listing': 40, 'occurrence': 90, 'deadline + window': 40 + 250}
out['finding 3, RC-252: maturity of every eligible candidate against T_D'] = {
    'T_A, T_R, T_D, D': [T_A, T_R, T_D, D],
    'eligible candidates on the grid': len(grid),
    'latest deadline + window': max(maturities),
    'smallest T_D - (deadline + window)': min(T_D - m for m in maturities),
    'Codex case: E occurs at 90, recorded at T_D + 1; delay from deadline + window': record - E['deadline + window'],
    'that delay exceeds D, so P(delay > D) counts the record': record - E['deadline + window'] > D,
    'a maturity after T_D needs a declared horizon above': T_D - (T_E - 1),
    'which exceeds H_max': T_D - (T_E - 1) > H_max,
}


# ================= finding 4 (RC-253): unquoted prose in the section 7 flow sequences =================
# The round-42 line Codex cites, as committed at 4fb9fd0 (its first two items), and the same text double-quoted.
COMMITTED = ('[RC-245 (deterministic: universe cluster of A at 15 and B at 30 with A omitted goes to batch 2, s_2, '
             't_reg 40, member B under version 38 and to batch 1, s_1, t_reg 20, member A under the universe rule; '
             'draws differ for 5,038 of 10,000 such clusters at pi = 0.5), RC-249 (checked)]')


def flow_items(text):
    """The items a YAML flow sequence holds: split at every comma outside quotes (YAML ignores parentheses)."""
    items, cur, quote = [], '', None
    for c in text[1:-1]:
        if quote:
            cur += c
            quote = None if c == quote else quote
        elif c == '"' and not cur.strip():
            quote, cur = c, cur + c
        elif c == ',':
            items.append(cur.strip())
            cur = ''
        else:
            cur += c
    return items + [cur.strip()]


def intended_items(text):
    """The items the prose intends: split at commas outside parentheses."""
    items, cur, depth = [], '', 0
    for c in text[1:-1]:
        depth += (c == '(') - (c == ')')
        if c == ',' and depth == 0:
            items.append(cur.strip())
            cur = ''
        else:
            cur += c
    return items + [cur.strip()]


def plain_defects(items):
    """Plain items that YAML reads as a mapping (': ') or that a comma cut inside parentheses."""
    return [i for i in items if not i.startswith('"') and (': ' in i or i.count('(') != i.count(')'))]


quoted = '[' + ', '.join(json.dumps(i) for i in intended_items(COMMITTED)) + ']'
out['finding 4, RC-253: the round-42 reproduced line, first two items'] = {
    'items YAML reads, as committed': len(flow_items(COMMITTED)),
    'items intended': len(intended_items(COMMITTED)),
    'plain items read as a mapping or cut inside parentheses, as committed': len(plain_defects(flow_items(COMMITTED))),
    'first item YAML reads, as committed': flow_items(COMMITTED)[0],
    'items YAML reads, double-quoted': len(flow_items(quoted)),
    'plain defects, double-quoted': len(plain_defects(flow_items(quoted))),
}

print(json.dumps(out, indent=1, ensure_ascii=False))
