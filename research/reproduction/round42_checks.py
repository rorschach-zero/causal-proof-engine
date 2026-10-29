"""Round-42 checks for the Codex findings on PR #4 at 492bc6a (no reference code, no network).

Codex's PR #4 comment 6254996147 on 492bc6a, five findings (four P1, one P2); four are checked here:
- finding 1 (RC-245): version 38 derives a cluster's batch b(k) from the listing times in the source's archive, so a
  source that omits a cluster's earliest member moves the whole cluster to a later batch, seed and registration time.
- finding 2 (RC-246): the pre-enrolment-breach audit of version 38 reads only the resolution source's publications,
  while the adjudicated `knowable_at` is the earliest of publication, public occurrence and logical finality.
- finding 4 (RC-248): two eligible sources' reference universes can hold one event with two different linkages, and
  version 38 names no rule that chooses between them.
- finding 5 (RC-249): the appendix checker reads the first version label of each document, so a second, stale label of
  the same form passes.
Finding 3 (RC-247) is a commit identity and has no script.
"""
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path

out = {}
HERE = Path(__file__).resolve().parent
PI, N = 0.5, 10_000


def fixture(name, sha256):
    """A committed input under fixtures/, pinned by its SHA-256 (RC-236)."""
    data = (HERE / 'fixtures' / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == sha256, name
    return data.decode('utf-8')


def draw(seed, cluster_id):
    digest = hashlib.sha256(f'{seed}:{cluster_id}'.encode()).digest()
    return int.from_bytes(digest, 'big') / 2 ** 256 < PI


# ================= finding 1 (RC-245): the batch of a cluster =================
# Batch calendar: window b = [20 (b - 1), 20 b), t_reg,b = 20 b. Universe cluster k = {A, B}; the universe lists A at
# 15 (window 1) and B at 30 (window 2). The source omits A and lists B at 30.
# - version 38 (17 lines 763-767 at 492bc6a): b(k) is the first window holding the listing time of one of k's members,
#   at the audit "the listing times in the source's archive";
# - remedy: b(k) is the first window holding the universe listing time of one of k's members.
def window(t):
    return t // 20 + 1


universe_listing = {'A': 15, 'B': 30}
source_listing = {'B': 30}
fixture_rows = {}
for rule, listing in (('version 38 (source archive)', source_listing), ('remedy (reference universe)', universe_listing)):
    b = min(window(t) for t in listing.values())
    fixture_rows[rule] = {'b(k)': b, 't_reg,b(k)': 20 * b, 'seed': f's_{b}',
                          'registration-time members': sorted(e for e, t in universe_listing.items()
                                                              if window(t) == b)}
out['finding 1, RC-245: batch of the universe cluster {A at 15, B at 30} when the source omits A'] = fixture_rows

# 10,000 such clusters, each drawn at pi = 0.5 by its cluster id with the seed of its batch. The honest universe
# sample uses s_1; version 38 uses s_2 for every cluster whose window-1 member the source omits.
s1 = [draw('round42-s1', f'k{n}') for n in range(N)]
s2 = [draw('round42-s2', f'k{n}') for n in range(N)]
out['finding 1, RC-245: draws of 10,000 such clusters, pi = 0.5'] = {
    'drawn differently (version 38 against the honest universe sample)': sum(a != b for a, b in zip(s1, s2)),
    'in the honest sample, not in the version-38 sample': sum(a and not b for a, b in zip(s1, s2)),
    'in the version-38 sample, not in the honest sample': sum(b and not a for a, b in zip(s1, s2)),
    'drawn differently (remedy)': 0,
}

# ================= finding 2 (RC-246): every route by which an outcome becomes knowable =================
# T_E = 100. `knowable_at` (17 lines 410-414) is min(publication time, public occurrence time, deadline + window).
# Every event has a declared earliest-knowable bound after T_E, so it is eligible; E occurs publicly at 90, before
# its bound, and its resolution source publishes the formal record only at 145. F is a control. For H the archive of
# public occurrence evidence cannot be read at the audit.
# - version 38 (17 lines 537-541): the audit reads the resolution record's publications up to T_E;
# - remedy: the audit recomputes the adjudicated knowable_at of every eligible event from every route.
T_E = 100
events = {'E': {'publication': 145, 'occurrence': 90, 'deadline': 140, 'window': 10},
          'F': {'publication': 125, 'occurrence': 120, 'deadline': 140, 'window': 10},
          'H': {'publication': 150, 'occurrence': None, 'deadline': 140, 'window': 10}}
unreadable_occurrence = {'H'}


def knowable_at(e):
    routes = [e['publication'], e['deadline'] + e['window']]
    return min(routes + ([e['occurrence']] if e['occurrence'] is not None else []))


out['finding 2, RC-246: pre-enrolment breaches found, T_E = 100'] = {
    'adjudicated knowable_at': {k: knowable_at(e) for k, e in events.items()},
    'version 38 (resolution-record publications)': sorted(k for k, e in events.items() if e['publication'] <= T_E),
    'version 38, primary exploratory for an unreadable record': False,
    'remedy (adjudicated knowable_at over every route)': sorted(
        k for k, e in events.items() if k not in unreadable_occurrence and knowable_at(e) <= T_E),
    'remedy, events whose route evidence cannot be read (primary exploratory)': sorted(unreadable_occurrence),
}

# ================= finding 4 (RC-248): overlapping reference universes =================
# Universe U1 (of source S1) links E and F; universe U2 (of source S2) holds E as a singleton and G. The event identity
# is the committed cross-universe key (here the letter). Version 38 takes the cluster of an event from "the"
# universe, so E's cluster id is U1's or U2's according to which universe supplies it.
universes = {'U1': [{'E', 'F'}], 'U2': [{'E'}, {'G'}]}
v38_ids = {u: next('+'.join(sorted(c)) for c in clusters if 'E' in c) for u, clusters in universes.items()}


def union_clusters(order):
    """Connected components of the union of every universe's point-in-time links, merged in the given order."""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x

    for u in order:
        for cluster in universes[u]:
            first, *rest = sorted(cluster)
            find(first)
            for e in rest:
                parent[find(e)] = find(first)
    groups = {}
    for e in parent:
        groups.setdefault(find(e), set()).add(e)
    return sorted('+'.join(sorted(g)) for g in groups.values())


out['finding 4, RC-248: cluster of E under two overlapping universes'] = {
    'version 38, E supplied by U1': v38_ids['U1'],
    'version 38, E supplied by U2': v38_ids['U2'],
    'remedy (union of the links), every order of the universes': sorted(
        {' | '.join(union_clusters(order)) for order in itertools.permutations(universes)}),
}
by_u1 = [draw('round42-batch-seed', f'E{n}+F{n}') for n in range(N)]
by_u2 = [draw('round42-batch-seed', f'E{n}') for n in range(N)]
out['finding 4, RC-248: draws of E over 10,000 such overlaps, pi = 0.5'] = {
    'drawn differently by the two universes (version 38)': sum(a != b for a, b in zip(by_u1, by_u2)),
    'drawn differently (remedy, one cohort-wide cluster)': 0,
}

# ================= finding 5 (RC-249): a second, stale version label =================
# A version-matched synthetic tree (the fixture of round40_checks.py, with one appendix and its output) whose
# documents agree in their first labels; each scenario appends a second label of the same form with other values.
# The checker of round 40 (unchanged to 492bc6a) and the round-42 checker are read from committed fixtures, so this
# output does not change with a later checker.
SCRIPT = "print('{\"x\": 2}')\n"
MATRIX = ('**Version:** v5, 2026-10-18. **Round:** 1 (fixture)\n\n'
          '<!-- round2-script:start -->\n```python\n' + SCRIPT + '```\n<!-- round2-script:end -->\n\n'
          '```json\n{"x": 2}\n```\n')
SPEC = 'version 5 (round 1: fixture)\n'
README = ('9. `16-reconciliation-matrix.md`: fixture (v5, round 1: fixture)\n'
          '10. `17-phase1-amended-specification.md`: fixture (version 5; versions 5 to 5 are)\n')
STALE = {'matrix': '\n**Version:** v6, 2026-10-18. **Round:** 2 (stale)\n',
         'specification': '\nversion 6 (round 2: stale)\n',
         'reading order': '9. `16-reconciliation-matrix.md`: stale (v6, round 2: stale)\n'}


def tree(root, stale, checker_source):
    rep = root / 'research' / 'reproduction'
    rep.mkdir(parents=True)
    docs = {'16-reconciliation-matrix.md': MATRIX + (STALE['matrix'] if stale == 'matrix' else ''),
            '17-phase1-amended-specification.md': SPEC + (STALE['specification'] if stale == 'specification' else ''),
            'README.md': README + (STALE['reading order'] if stale == 'reading order' else '')}
    for name, text in docs.items():
        (root / 'research' / name).write_text(text)
    (rep / 'round2_checks.py').write_text(SCRIPT)
    (rep / 'inventory.txt').write_text('round2_checks.py round2\n')
    (rep / 'check_appendix_scripts.py').write_text(checker_source)


checkers = {'round 40': fixture('check_appendix_scripts.round40.py.txt',
                                'c1e8b1799fcc0c0ddaee38d7f56b3319a0fd8c23ba6001be1568c69444c4c889'),
            'round 42': fixture('check_appendix_scripts.round42.py.txt',
                                '888cd6dd7b1c4eb6d8580bf09e777f37e8328dbf65cc13d3607b59123e64c2c8')}
res = {}
for stale in (None, 'matrix', 'specification', 'reading order'):
    scenario = 'one label each' if stale is None else f'a second, stale {stale} label'
    for name, source in checkers.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tree(root, stale, source)
            run = subprocess.run([sys.executable, '-I', 'research/reproduction/check_appendix_scripts.py'],
                                 cwd=root, capture_output=True, text=True)
        assert 'Traceback' not in run.stderr, (scenario, name, run.stderr)
        res[f'{scenario} / checker {name}'] = {'exit_code': run.returncode,
                                               'stdout': run.stdout.strip().splitlines()}
out['finding 5, RC-249: duplicate version labels'] = res

print(json.dumps(out, indent=1))
