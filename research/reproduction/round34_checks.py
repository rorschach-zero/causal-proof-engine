"""Round-34 checks for the Codex findings on PR #4 at 66cd6a4 (no reference code, no network).

Codex's review 5563331912 of 66cd6a4, two inline findings:
- 4307347441 (RC-216): version 30 lets the audit re-derive cluster membership from the source's archive and removes
  a logged cluster of a later batch whose members the archive assigns to an earlier cluster. Listing times are
  frozen, but the linkage metadata the cluster rule reads is not, so an archive update written after the later
  cluster's unfavourable outcome removes that cluster.
- 4307347446 (RC-217): the appendix checker reads the last start marker of a key and collects keys into a set, so a
  second, stale block under the same key is never compared.

Setting of Appendices AF and AG: cluster increment +-0.2, one-sided t at the nominal 1.645, 20,000 replications;
here 300 pairs (A in batch 1, B in batch 2), 600 clusters.
"""
import importlib.util
import json
import re
from pathlib import Path

import numpy as np

out = {}
REPS, PAIRS, CRIT = 20_000, 300, 1.645


def t_reject(s, keep=None, w=None):
    w = np.ones_like(s) if w is None else w
    n = w.sum(1)
    m = (s * w).sum(1) / n
    sd = np.sqrt(((s - m[:, None]) ** 2 * w).sum(1) / (n - 1))
    rej = m / (sd / np.sqrt(n)) > CRIT
    if keep is not None:
        rej &= keep
    return round(float(rej.mean()), 4)


# ================= 4307347441 (RC-216): linkage metadata written after an outcome =================
# Every cluster's registration-time increment is +0.2 with probability 0.5 + delta/0.4 and -0.2 otherwise. Law T(q):
# after B's increment is -0.2, the source's archive adds a linkage, with probability q, that assigns B's members to A
# (outcome-triggered). Law R(r): the linkage is added with probability r whatever B's outcome (not outcome-triggered).
# Statistics: current_state, version 30 (the audit re-derives B as post-registration members of A and B leaves the
# primary); point_in_time, the remedy (membership read from the state at B's batch snapshot, so no cluster leaves);
# boxed_lower_end, Codex's boxed-defect route (a linked B enters at the lower end -0.2 of its box and the decision is
# taken at that end); withhold_if_any_conflict, Codex's non-confirmatory route (no decision when any later
# conflicting linkage exists in the cohort).
rng = np.random.default_rng(3401)


def simulate(delta, q=0.0, r=0.0):
    a = np.where(rng.random((REPS, PAIRS)) < 0.5 + delta / 0.4, 0.2, -0.2)
    b = np.where(rng.random((REPS, PAIRS)) < 0.5 + delta / 0.4, 0.2, -0.2)
    u = rng.random((REPS, PAIRS))
    linked = ((b < 0) & (u < q)) | (u < r)
    s = np.concatenate([a, b], 1)
    keep_b = np.concatenate([np.ones_like(a), (~linked).astype(float)], 1)
    boxed = np.concatenate([a, np.where(linked, -0.2, b)], 1)
    return {'share_linked': round(float(linked.mean()), 4),
            'current_state': t_reject(s, w=keep_b), 'point_in_time': t_reject(s),
            'boxed_lower_end': t_reject(boxed),
            'withhold_if_any_conflict': t_reject(s, keep=~linked.any(1))}


null_triggered, alt_triggered, alt_random = {}, {}, {}
for q in (0.05, 0.10, 0.20):
    null_triggered[f'q={q}'] = simulate(0.0, q=q)
    alt_triggered[f'q={q}'] = simulate(0.02, q=q)
for r in (0.025, 0.05, 0.10):
    alt_random[f'r={r}'] = simulate(0.02, r=r)
out['4307347441 RC-216 exactly null, outcome-triggered linkage T(q)'] = null_triggered
out['4307347441 RC-216 delta = 0.02, outcome-triggered linkage T(q)'] = alt_triggered
out['4307347441 RC-216 delta = 0.02, linkage independent of outcome R(r)'] = alt_random
out['4307347441 RC-216 P(some conflicting linkage in a 300-pair cohort) under T(q), null'] = {
    f'q={q}': round(1 - (1 - q / 2) ** PAIRS, 6) for q in (0.05, 0.10, 0.20)}

# Remedy: every member's cluster assignment is read from the point-in-time state of its listing (the anchored
# snapshot of its window, or for an audited omission the archive's state at that snapshot's anchor time); linkage
# metadata written later never changes a registered cluster and never removes one. point_in_time is the honest
# statistic of the registration-time estimand and holds the nominal rate under T(q).

# ================= 4307347446 (RC-217): duplicate appendix markers =================
# A synthetic matrix with two blocks under one key, the earlier one stale, and the committed script equal to the
# later one. Marker lines are built by concatenation so that no line of this script is itself a marker line.
checker_path = Path(__file__).resolve().parent / 'check_appendix_scripts.py'
spec = importlib.util.spec_from_file_location('checker', checker_path)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def marker(key, kind):
    return '<' + '!-- ' + key + '-script:' + kind + ' -->'


def block(key, body):
    return f'{marker(key, "start")}\n```python\n{body}```\n{marker(key, "end")}\n'


current = 'print(2)\n'
cases = {
    'two blocks, earlier stale': 'A\n' + block('demo', 'print(1)\n') + 'B\n' + block('demo', current),
    'one block': 'A\n' + block('demo', current),
    'stray end marker after the block': 'A\n' + block('demo', current) + marker('demo', 'end') + '\n',
}


def version33_passes(text):
    # The version-33 logic: keys from start-marker lines collected into a set, the last start marker read.
    keys = set(re.findall(r'^<!-- (\w+)-script:start -->$', text, flags=re.MULTILINE))
    start = text.rindex(marker('demo', 'start'))
    end = text.index(marker('demo', 'end'), start)
    body = text[start:end].split('```python\n', 1)[1].rsplit('```', 1)[0]
    return keys == {'demo'} and body == current


def version34_passes(text):
    return not checker.marker_failures(text) and checker.fenced_block(text, 'demo') == current


out['4307347446 RC-217 checker verdict on a synthetic matrix'] = {
    name: {'version_33_passes': version33_passes(text), 'version_34_passes': version34_passes(text)}
    for name, text in cases.items()}

print(json.dumps(out, indent=1))
