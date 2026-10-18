"""Round-39 checks for the Codex findings on PR #4 at 784183f (no reference code, no network).

Codex's PR #4 comment 6252440988 on 784183f, four findings (three P1, one P2); three are checked here:
- finding 1 (RC-232): G_scr of version 35 counts only the burn-in blocks that hold a listed event of the source, so
  a source that lists nothing in the blocks it expects to be unfavourable removes them from the screen, and the
  remaining blocks carry no slope. The remedy counts every calendar block and adds a response every block has
  whatever the source lists: the block's mean increment over the burn-in members of the other sources.
- finding 3 (RC-234): the screen of version 35 regresses only the increment of the primary pair, so a source that
  selects on another confirmatory component's increment passes. The remedy screens every component; its joint rule
  refers each family's maximum |t| to permutations of the source's listing counts, because Bonferroni over the 2J
  slopes with t critical values is oversized at burn-in block counts.
- finding 4 (RC-235): the intact fixture of round38_checks.py holds no specification and no research README, so
  the remedy checker of 784183f raised FileNotFoundError in all three scenarios, and its recorded exit code 1 for
  the intact tree contradicts the round-38 claim that it exits 0. The checker, unchanged since 784183f, is read from
  that commit and run here on version-matched fixtures with every exit code asserted.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy import stats

out = {}
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# ================= findings 1 and 3 (RC-232, RC-234): the burn-in supply screen =================
# Burn-in law: no skill, J = 6 confirmatory components (Design C, three single providers, single-provider-three-roles,
# equal-weight committee). In block g, component j has a shock s_gj = +-0.05, shared by every source, and each
# listed event adds independent noise +-0.2 per component. Source A has 25 candidates per block, the other sources
# together 50; an honest source lists each with probability 0.8. A selecting source A uses a signal, right with
# probability rho = 0.75, of the sign of one component's shock in each block, published before the block opens
# (the signal-chosen calendar of Appendix AK), and keeps a share KEEP of the block's candidates where the signal says
# negative. KEEP = 0 suppresses the block entirely (finding 1). Event noise is independent across components, a
# simplification: real components share FULL and are correlated, which neither joint rule below needs.
# Statistics: the HC3 t of the slope of a block response on A's listing count. The own family regresses A's own
# block mean increment over the blocks where A lists (version 35 used its primary-pair member alone); the leave-out
# family regresses the block mean increment of the other sources' members over every block that has one, so a block
# A leaves empty still counts (RC-232). Two joint rules over the 2J slopes (RC-234): Bonferroni with t critical
# values at n - 2 df, and the remedy, the maximum |t| of each family referred to PERMS permutations of A's counts
# across that family's blocks, the source failing when either family's permutation p is at most ALPHA / 2.
J, N_A, N_O, P_LIST, RHO, ALPHA, PERMS, CHUNK = 6, 25, 50, 0.8, 0.75, 0.05, 199, 250


def block_means(rng, count, shock):
    """Mean increment per block and component over `count` listed events with shock `shock`; nan where empty."""
    noise = rng.binomial(np.broadcast_to(count[..., None], shock.shape), 0.5)
    with np.errstate(divide='ignore', invalid='ignore'):
        return shock + 0.2 * (2 * noise - count[..., None]) / count[..., None]


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
    return np.max([np.abs(hc3_t(a, resp[..., j], mask)) for j in range(J)], 0)


def permutation_p(rng, a, resp, mask):
    """Permutation p of the family's max |t|: A's counts are shuffled among the family's blocks, the other blocks
    keep their (unused) values."""
    observed = max_t(a, resp, mask)
    key = np.where(mask[:, None, :], rng.random((a.shape[0], PERMS, a.shape[1])), np.inf)
    source = np.argsort(key, -1)
    target = np.argsort(np.broadcast_to(~mask[:, None, :], key.shape), -1, kind='stable')
    shuffled = np.empty(key.shape)
    np.put_along_axis(shuffled, target, np.take_along_axis(np.broadcast_to(a[:, None, :], key.shape), source, -1), -1)
    null = max_t(shuffled, resp[:, None], mask[:, None, :])
    return (1 + (null >= observed[:, None] - 1e-12).sum(1)) / (PERMS + 1)


def screens(rng, logs, g, select_on, keep, own_shock):
    common = np.where(rng.random((logs, g, J)) < 0.5, 0.05, -0.05)
    shock_a = common
    if own_shock:  # A's increments carry a source-specific shock the other sources do not share
        shock_a = np.where(rng.random((logs, g, J)) < 0.5, 0.05, -0.05)
    p_keep = np.full((logs, g), P_LIST)
    if select_on is not None:
        signal = np.where(rng.random((logs, g)) < RHO, shock_a[..., select_on], -shock_a[..., select_on])
        p_keep = np.where(signal < 0, P_LIST * keep, P_LIST)
    count_a = rng.binomial(N_A, p_keep)
    count_o = rng.binomial(N_O, P_LIST, (logs, g))
    own = block_means(rng, count_a, shock_a)
    other = block_means(rng, count_o, common)
    listed, all_blocks = count_a > 0, count_o > 0
    df_own, df_out = np.maximum(listed.sum(1) - 2, 1), np.maximum(all_blocks.sum(1) - 2, 1)
    t_own = np.stack([hc3_t(count_a, own[..., j], listed) for j in range(J)], 1)
    t_out = np.stack([hc3_t(count_a, other[..., j], all_blocks) for j in range(J)], 1)
    p_own = 2 * stats.t.sf(np.abs(t_own), df_own[:, None])
    p_out = 2 * stats.t.sf(np.abs(t_out), df_out[:, None])
    perm = np.concatenate([np.minimum(permutation_p(rng, count_a[i:i + CHUNK], own[i:i + CHUNK], listed[i:i + CHUNK]),
                                      permutation_p(rng, count_a[i:i + CHUNK], other[i:i + CHUNK],
                                                    all_blocks[i:i + CHUNK]))
                           for i in range(0, logs, CHUNK)])
    with np.errstate(invalid='ignore'):  # nan in a log where A lists nothing, left out of the mean
        listed_mean = np.nansum(own[..., 0] * count_a, 1) / count_a.sum(1)
    return {
        'version35 (own, primary pair, t at n - 2 df)': rate(p_own[:, 0] < ALPHA),
        'leave-out, primary pair, t at n - 2 df': rate(p_out[:, 0] < ALPHA),
        'own and leave-out, every component, Bonferroni t': rate(np.minimum(p_own.min(1), p_out.min(1))
                                                                   < ALPHA / (2 * J)),
        'remedy: own and leave-out, every component, max |t| permutation': rate(perm <= ALPHA / 2),
        'mean G_scr of version 35': round(float(listed.sum(1).mean()), 2),
        "mean of A's listed primary-pair increments": round(float(np.nanmean(listed_mean)), 4),
    }


def rate(rej):
    return round(float(np.mean(rej)), 4)


LOGS = 4_000
SOURCES = (('honest', None, 1.0, False),
           ('calendar rho=0.75 on the primary pair, keep 0.2 (Appendix AK source)', 0, 0.2, False),
           ('calendar rho=0.75 on the primary pair, keep 0 (finding 1)', 0, 0.0, False),
           ('calendar rho=0.75 on single provider P1, keep 0.2 (finding 3)', 1, 0.2, False),
           ('calendar rho=0.75 on single provider P1, keep 0', 1, 0.0, False),
           ('honest, source-specific shock', None, 1.0, True),
           ('calendar rho=0.75 on a source-specific primary-pair shock, keep 0.2', 0, 0.2, True),
           ('calendar rho=0.75 on a source-specific primary-pair shock, keep 0 (residual)', 0, 0.0, True))
res = {}
for g in (12, 24, 48, 100):
    row = {}
    for number, (label, select_on, keep, own_shock) in enumerate(SOURCES):
        rng = np.random.default_rng(3901 + 11 * g + number)
        row[label] = screens(rng, LOGS, g, select_on, keep, own_shock)
    res[f'blocks={g}'] = row
out[f'findings 1 and 3, RC-232 and RC-234: rejection rate of the supply screen over {LOGS:,} logs, level 0.05'] = res

# ================= finding 4 (RC-235): the checker fixtures =================
# The round-38 fixture (a matrix only), intact, and a version-matched fixture (matrix v5 / round 1, specification
# version 5 / round 1, reading order v5 / round 1 and version 5 / versions 5 to 5), intact, with round3_checks.py and
# its block deleted together, and with the inventory deleted as well. The checker is read from commit 784183f, not
# from the working tree, so that this output does not change with a later checker (round38_checks.py reads the
# working checker, so Appendix AL reproduces only while the checker is unchanged).
SCRIPT = "print('{\"x\": %d}')\n"
DOCS = {'research/17-phase1-amended-specification.md': 'version 5 (round 1: fixture)\n',
        'research/README.md': '9. `16-reconciliation-matrix.md`: fixture (v5, round 1: fixture)\n'
                              '10. `17-phase1-amended-specification.md`: fixture (version 5; versions 5 to 5 are)\n'}


def block(n):
    return (f'<!-- round{n}-script:start -->\n```python\n{SCRIPT % n}```\n<!-- round{n}-script:end -->\n\n'
            f'```json\n{{"x": {n}}}\n```\n\n')


def tree(root, rounds, inventory, docs, checker_source):
    rep = root / 'research' / 'reproduction'
    rep.mkdir(parents=True)
    header = '**Version:** v5, 2026-10-18. **Round:** 1 (fixture)\n\n' if docs else ''
    (root / 'research' / '16-reconciliation-matrix.md').write_text(header + ''.join(block(n) for n in rounds))
    for name in docs:
        (root / name).write_text(DOCS[name])
    for n in rounds:
        (rep / f'round{n}_checks.py').write_text(SCRIPT % n)
    if inventory:
        (rep / 'inventory.txt').write_text(''.join(f'round{n}_checks.py round{n}\n' for n in (2, 3)))
    (rep / 'check_appendix_scripts.py').write_text(checker_source)


CHECKER = subprocess.run(
    ['git', '-C', str(REPO), 'show', '784183f118f4218091ac6408510b05b4984de4ef:'
     'research/reproduction/check_appendix_scripts.py'], capture_output=True, text=True, check=True).stdout
# (fixture, rounds, inventory, documents, expected exit code, expected traceback)
SCENARIOS = (('round-38 fixture, intact', (2, 3), True, (), 1, True),
             ('version-matched, intact', (2, 3), True, tuple(DOCS), 0, False),
             ('version-matched, co_deleted', (2,), True, tuple(DOCS), 1, False),
             ('version-matched, inventory_deleted', (2,), False, tuple(DOCS), 1, False))
res = {}
for scenario, rounds, inventory, docs, code, raises in SCENARIOS:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        tree(root, rounds, inventory, docs, CHECKER)
        run = subprocess.run([sys.executable, '-I', 'research/reproduction/check_appendix_scripts.py'],
                             cwd=root, capture_output=True, text=True)
    traceback = 'Traceback' in run.stderr
    assert (run.returncode, traceback) == (code, raises), (scenario, run.returncode, run.stderr)
    res[scenario] = {'exit_code': run.returncode,
                     'raised': run.stderr.strip().splitlines()[-1] if traceback else None,
                     'stdout': run.stdout.strip().splitlines()}
out['finding 4, RC-235: the checker of 784183f on the round-38 and version-matched fixtures, exit codes asserted'] = res

print(json.dumps(out, indent=1))
