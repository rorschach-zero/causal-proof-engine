"""Round-40 checks for the Codex findings on PR #4 at 2bac6a9 (no reference code, no network).

Codex's PR #4 comment 6253981699 on 2bac6a9, six findings (four P1, two P2); four are checked here:
- finding 3 (RC-238): the screen's permutation p is at least 1/(B + 1), so with B = 19 permutations it can never
  reach half of a 5 % level and a perfectly associated source passes.
- finding 4 (RC-239): sources that suppress the same blocks leave them with no member of any source, so the blocks
  enter neither family of the version-36 screen.
- finding 5 (RC-240): the appendix checker compares only the first of several output blocks.
- finding 6 (RC-241): a source that lists a fixed number of signal-favourable events from every block gives both
  count slopes a constant regressor.
The remedy for findings 4 and 6 (version 37) audits each source's listing against an independent universe: every
predicate-matching event of the universe that the source does not list is an audited omission, which enters under the
VOID cap and the box rule. Finding 1 (RC-236) is checked by running the full checker in a tree without Git history,
outside this script; finding 2 (RC-237) is a commit identity and has no script.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

out = {}
HERE = Path(__file__).resolve().parent


def fixture(name, sha256):
    """A committed input under fixtures/, pinned by its SHA-256 (RC-236)."""
    data = (HERE / 'fixtures' / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == sha256, name
    return data.decode('utf-8')


def rate(rej):
    return round(float(np.mean(rej)), 4)


# ================= the screen of version 36 (round39_checks.py, unchanged) =================
J, ALPHA = 6, 0.05


def hc3_t(a, c, mask):
    """HC3 t of the slope of c on a over the blocks (last axis) in `mask`; 0 where fewer than three blocks or a
    constant regressor leave no slope."""
    with np.errstate(divide='ignore', invalid='ignore'):
        n = mask.sum(-1, keepdims=True)
        a_c = np.where(mask, a - np.where(mask, a, 0).sum(-1, keepdims=True) / n, 0.0)
        c = np.where(mask, c, 0.0)
        sxx = (a_c ** 2).sum(-1, keepdims=True)
        slope = (a_c * c).sum(-1, keepdims=True) / sxx
        resid = np.where(mask, c - c.sum(-1, keepdims=True) / n - slope * a_c, 0.0)
        lev = np.where(mask, 1 / n + a_c ** 2 / sxx, 0.0)
        t = (slope / np.sqrt((a_c ** 2 * resid ** 2 / (1 - lev) ** 2).sum(-1, keepdims=True)) * sxx)[..., 0]
    return np.where((n[..., 0] >= 3) & np.isfinite(t), t, 0.0)


def max_t(a, resp, mask):
    return np.max([np.abs(hc3_t(a, resp[..., j], mask)) for j in range(resp.shape[-1])], 0)


def permutation_p(rng, a, resp, mask, perms):
    """(1 + #{permuted max |t| >= observed}) / (perms + 1), A's counts shuffled among the family's blocks."""
    observed = max_t(a, resp, mask)
    key = np.where(mask[:, None, :], rng.random((a.shape[0], perms, a.shape[1])), np.inf)
    source = np.argsort(key, -1)
    target = np.argsort(np.broadcast_to(~mask[:, None, :], key.shape), -1, kind='stable')
    shuffled = np.empty(key.shape)
    np.put_along_axis(shuffled, target, np.take_along_axis(np.broadcast_to(a[:, None, :], key.shape), source, -1), -1)
    null = max_t(shuffled, resp[:, None], mask[:, None, :])
    return (1 + (null >= observed[:, None] - 1e-12).sum(1)) / (perms + 1)


# ================= finding 3 (RC-238): the resolution of the permutation p =================
# A source whose listing count determines the block response up to noise of 1e-6 (24 blocks, counts 1 to 24, one
# component): the strongest association there is. Its p is the smallest the rule can produce, 1/(B + 1).
rng = np.random.default_rng(4001)
counts = np.arange(1.0, 25.0)[None, :]
response = (counts + 1e-6 * rng.standard_normal(counts.shape))[..., None]
mask = np.ones(counts.shape, bool)
res = {}
for perms in (19, 39, 199):
    p = float(permutation_p(rng, counts, response, mask, perms)[0])
    res[f'B={perms}'] = {'p': round(p, 4), 'minimum 1/(B+1)': round(1 / (perms + 1), 4),
                         'fails at p <= ALPHA/2 = 0.025': p <= ALPHA / 2}
res['smallest B with 1/(B+1) <= ALPHA/2'] = int(np.ceil(2 / ALPHA - 1))
out['finding 3, RC-238: permutation p of a perfectly associated source'] = res

# ================= findings 4 and 6 (RC-239, RC-241): selection the count screen cannot see =================
# Law: no skill unless DELTA > 0, J = 6 components. Block g has an independent universe of U_A ~ Bin(40, 0.75)
# events for source A and U_O ~ Bin(64, 0.78) for the other sources O; event i of component j has the increment
# s_gj + 0.2 r_ij (+ DELTA for the primary pair, j = 0), s_gj = +-0.05 shared by every source, r_ij = +-1.
# Sources (universe semantics: an honest source lists its whole universe, or omits each event at random with
# probability r):
# - joint: A and O both list nothing in the blocks where a signal, right with probability RHO, says s_g0 < 0
#   (finding 4), and their whole universe elsewhere;
# - fixed10: A lists exactly 10 events per block, those whose signal on r_i0 (right with probability RHO) is
#   positive first, ties broken at random (finding 6); O honest;
# - drop1: A omits the one event per block whose signal is lowest (a selection under the cap); O honest.
# Statistics, over the logs:
# - screen36: A fails the version-36 rule (own and leave-out families, J components, max |t| permutation, B = 199);
# - primary36: the toy primary over the listed members, block mean of j = 0 over the blocks with a member, one-sided
#   t over blocks at the nominal 1.645;
# - remedy: the universe audit of version 37 with every omission drawn (pi = 1): the omitted share of the
#   cohort's universe above the VOID cap CAP makes the primary non-confirmatory; otherwise each omitted event enters
#   at the lower end of its box, -1 (the primary pair's Brier difference lies in [-1, 1]), and the same t is taken
#   over every universe block. The lower-end point bounds the box minimum of the numerator only; the conservative
#   kappa_A form of the box rule is not simulated, and CAP = 0.05 is illustrative (OD4).
RHO, CAP, PERMS, LOGS, SIM_CHUNK = 0.75, 0.05, 199, 2_000, 100


def log_chunk(rng, logs, g, source, delta, r_omit):
    u_a = rng.binomial(40, 0.75, (logs, g))
    u_o = rng.binomial(64, 0.78, (logs, g))
    n_max = 64
    shock = np.where(rng.random((logs, g, 1, J)) < 0.5, 0.05, -0.05)
    skill = np.zeros(J)
    skill[0] = delta

    def events(u):
        exists = np.arange(n_max)[None, None, :] < u[..., None]
        r = np.where(rng.random((logs, g, n_max, J)) < 0.5, 1.0, -1.0)
        return exists, shock + 0.2 * r + skill, r[..., 0]

    exist_a, inc_a, r_a = events(u_a)
    exist_o, inc_o, _ = events(u_o)
    list_a = exist_a & (rng.random(exist_a.shape) >= r_omit)
    list_o = exist_o & (rng.random(exist_o.shape) >= r_omit)
    if source == 'joint':
        signal = np.where(rng.random((logs, g)) < RHO, shock[:, :, 0, 0], -shock[:, :, 0, 0])
        list_a &= (signal > 0)[..., None]
        list_o &= (signal > 0)[..., None]
    elif source in ('fixed10', 'drop1'):
        signal = np.where(rng.random(r_a.shape) < RHO, r_a, -r_a) + 1e-3 * rng.random(r_a.shape)
        rank = np.argsort(np.argsort(np.where(exist_a, -signal, np.inf), -1), -1)
        list_a = exist_a & ((rank < 10) if source == 'fixed10' else (rank < u_a[..., None] - 1))
    return u_a, u_o, inc_a, inc_o, list_a, list_o


def block_mean(inc, listed):
    with np.errstate(invalid='ignore', divide='ignore'):
        return (inc * listed[..., None]).sum(2) / listed.sum(2)[..., None]


def block_t(m, present):
    n = present.sum(1)
    mean = np.where(present, m, 0).sum(1) / n
    var = np.where(present, (m - mean[:, None]) ** 2, 0).sum(1) / (n - 1)
    return mean / np.sqrt(var / n)


def simulate(rng, g, source, delta, r_omit, screen):
    rows = {'screen36': [], 'primary36': [], 'remedy': [], 'non_confirmatory': [], 'omitted_share': []}
    for _ in range(0, LOGS, SIM_CHUNK):
        u_a, u_o, inc_a, inc_o, list_a, list_o = log_chunk(rng, SIM_CHUNK, g, source, delta, r_omit)
        count_a = list_a.sum(2).astype(float)
        if screen:
            own, other = block_mean(inc_a, list_a), block_mean(inc_o, list_o)
            p = np.minimum(permutation_p(rng, count_a, own, count_a > 0, PERMS),
                           permutation_p(rng, count_a, other, list_o.sum(2) > 0, PERMS))
            rows['screen36'].append(p <= ALPHA / 2)
        listed = list_a.sum(2) + list_o.sum(2)
        listed_sum = (inc_a[..., 0] * list_a).sum(2) + (inc_o[..., 0] * list_o).sum(2)
        with np.errstate(invalid='ignore', divide='ignore'):
            rows['primary36'].append(block_t(listed_sum / listed, listed > 0) > 1.645)
        exist_a = np.arange(inc_a.shape[2])[None, None, :] < u_a[..., None]
        exist_o = np.arange(inc_o.shape[2])[None, None, :] < u_o[..., None]
        omitted = (exist_a & ~list_a).sum(2) + (exist_o & ~list_o).sum(2)
        share = omitted.sum(1) / (u_a + u_o).sum(1)
        boxed = (listed_sum - omitted) / (u_a + u_o)
        rows['remedy'].append((share <= CAP) & (block_t(boxed, np.ones(boxed.shape, bool)) > 1.645))
        rows['non_confirmatory'].append(share > CAP)
        rows['omitted_share'].append(share)
    result = {}
    for name, values in rows.items():
        if values:
            values = np.concatenate(values)
            result[name] = round(float(values.mean()), 4)
    return result


SOURCES = (('honest, complete listing', 'honest', 0.0, 0.0, True),
           ('joint suppression of the signal-negative blocks by A and O (finding 4)', 'joint', 0.0, 0.0, True),
           ('A lists a fixed 10 signal-favourable events per block (finding 6)', 'fixed10', 0.0, 0.0, True),
           ('A omits its one most signal-unfavourable event per block', 'drop1', 0.0, 0.0, False),
           ('honest, 1 % random omissions', 'honest', 0.0, 0.01, False),
           ('honest, 3 % random omissions', 'honest', 0.0, 0.03, False),
           ('skill 0.02, complete listing', 'honest', 0.02, 0.0, False),
           ('skill 0.02, 1 % random omissions', 'honest', 0.02, 0.01, False),
           ('skill 0.02, 3 % random omissions', 'honest', 0.02, 0.03, False))
res = {}
for g in (24, 48, 100):
    row = {}
    for number, (label, source, delta, r_omit, screen) in enumerate(SOURCES):
        row[label] = simulate(np.random.default_rng(4002 + 13 * g + number), g, source, delta, r_omit, screen)
    res[f'blocks={g}'] = row
out[f'findings 4 and 6, RC-239 and RC-241: rejection rates over {LOGS:,} logs, VOID cap {CAP}'] = res

# ================= finding 5 (RC-240): a second, stale output block =================
# A version-matched synthetic tree (the fixture of round39_checks.py) whose round3 appendix holds its committed
# output and then a second json block with a different value. The checker of 784183f (unchanged to 2bac6a9) and the
# round-40 checker are read from committed fixtures, so this output does not change with a later checker.
SCRIPT = "print('{\"x\": %d}')\n"
DOCS = {'research/17-phase1-amended-specification.md': 'version 5 (round 1: fixture)\n',
        'research/README.md': '9. `16-reconciliation-matrix.md`: fixture (v5, round 1: fixture)\n'
                              '10. `17-phase1-amended-specification.md`: fixture (version 5; versions 5 to 5 are)\n'}


def block(n, stale):
    extra = f'```json\n{{"x": {n + 100}}}\n```\n\n' if stale else ''
    return (f'<!-- round{n}-script:start -->\n```python\n{SCRIPT % n}```\n<!-- round{n}-script:end -->\n\n'
            f'```json\n{{"x": {n}}}\n```\n\n' + extra)


def tree(root, stale, checker_source):
    rep = root / 'research' / 'reproduction'
    rep.mkdir(parents=True)
    (root / 'research' / '16-reconciliation-matrix.md').write_text(
        '**Version:** v5, 2026-10-18. **Round:** 1 (fixture)\n\n' + block(2, False) + block(3, stale))
    for name, text in DOCS.items():
        (root / name).write_text(text)
    for n in (2, 3):
        (rep / f'round{n}_checks.py').write_text(SCRIPT % n)
    (rep / 'inventory.txt').write_text('round2_checks.py round2\nround3_checks.py round3\n')
    (rep / 'check_appendix_scripts.py').write_text(checker_source)


checkers = {'784183f': fixture('check_appendix_scripts.784183f.py.txt',
                               'ed85ed70a300b4d245c4d3080cfe25d0aaf5df3c6b1f45419123e2bb31f2d31d'),
            'round 40': fixture('check_appendix_scripts.round40.py.txt',
                                'c1e8b1799fcc0c0ddaee38d7f56b3319a0fd8c23ba6001be1568c69444c4c889')}
res = {}
for scenario, stale in (('one output block', False), ('a second, stale output block', True)):
    for name, source in checkers.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tree(root, stale, source)
            run = subprocess.run([sys.executable, '-I', 'research/reproduction/check_appendix_scripts.py'],
                                 cwd=root, capture_output=True, text=True)
        assert 'Traceback' not in run.stderr, (scenario, name, run.stderr)
        res[f'{scenario} / checker {name}'] = {'exit_code': run.returncode,
                                               'stdout': run.stdout.strip().splitlines()}
out['finding 5, RC-240: duplicate output blocks'] = res

print(json.dumps(out, indent=1))
