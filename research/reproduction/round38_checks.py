"""Round-38 checks for the Codex findings on PR #4 at 98b03fc (no reference code, no network).

Codex's review 5563809881 of 98b03fc, three inline findings (one P1, two P2); two are checked here:
- 4307728264 (RC-229): the supply-exogeneity screen of version 34 runs on the Phase 2 candidate log, but Phase 2
  issues no forecast, so no Phase 2 block has the realised increment of the primary pair the screen regresses. The
  remedy moves the screen to the Phase 4 blinded burn-in cohort, which commits forecasts and is excluded from the
  primary; the cost checked here is the screen's size and power on burn-in-sized logs.
- 4307728271 (RC-230): the appendix checker derives the scripts it requires from the appendix keys and the files
  present, so deleting a script and its appendix block together passes. The remedy checks against a committed
  inventory; both checkers are run here on a synthetic two-script tree.
- 4307728277 (RC-231): the reading order of research/README.md names matrix v37 / round 36 and specification
  version 33 while the matrix and the specification of 98b03fc are v38 / round 37 and version 34. The third finding
  of this class (RC-137, RC-167); the remedy adds a version-label check to the checker, run here on 98b03fc.
"""
import json
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy import stats

out = {}
HERE = Path(__file__).resolve().parent

# ================= 4307728264 (RC-229): the increment screen on a burn-in-sized log =================
# The laws of Appendix AK (b): no skill, X_k = s_g + e_k with s_g = +-0.05 per block and e_k = +-0.2; an honest
# source lists each candidate with probability 0.8; a responsive source, in a share q of blocks where the block's
# shock is revealed before its later events, lists each later event with probability 0.2 when the shock is negative;
# the signal-chosen calendar thins every block a pre-T_0 signal, right with probability rho, calls negative. The screen
# is the robust slope of the block's realised mean increment on the source's listing count. Version 34 sized it on a
# 400-block Phase 2 log, which cannot exist without forecasts; a burn-in of the first three months of Phase 4 has as
# many blocks as the block length (OD4) cuts three months into, and fewer events per block.
F_KEEP = 0.2


def law(rng, reps, g, per):
    s = np.where(rng.random((reps, g)) < 0.5, 0.05, -0.05)
    b = np.repeat(np.arange(g), per)
    x = s[:, b] + np.where(rng.random((reps, g * per)) < 0.5, 0.2, -0.2)
    return s, b, x


def slope_t(a, c):
    """Slope of c on a over blocks with its HC0 and HC3 standard errors; returns (t_HC0, t_HC3)."""
    with np.errstate(divide='ignore', invalid='ignore'):
        a = a - a.mean(1, keepdims=True)
        sxx = (a ** 2).sum(1)
        slope = (a * c).sum(1) / sxx
        resid = c - c.mean(1, keepdims=True) - slope[:, None] * a
        lev = 1 / a.shape[1] + a ** 2 / sxx[:, None]
        se0 = np.sqrt((a ** 2 * resid ** 2).sum(1)) / sxx
        se3 = np.sqrt((a ** 2 * resid ** 2 / (1 - lev) ** 2).sum(1)) / sxx
        return slope / se0, slope / se3


def rate(rej):
    return round(float(np.mean(rej)), 4)


LOGS = 4_000
res = {}
for per in (25, 10):
    for k in (6, 12, 24, 48, 100, 400):
        row = {}
        for label, q, rho in (('honest', 0.0, None), ('responsive q=0.25', 0.25, None),
                              ('calendar rho=0.75', 1.0, 0.75)):
            rng = np.random.default_rng(3801 + 7 * k + per + int(q * 100) + (0 if rho is None else 1000))
            s, b, x = law(rng, LOGS, k, per)
            revealed = rng.random((LOGS, k)) < q
            if rho is not None:
                s = np.where(rng.random((LOGS, k)) < rho, s, -s)
            later = np.ones(k * per, bool)
            later[::per] = False
            keep_p = np.where((revealed & (s < 0))[:, b] & later, F_KEEP, 0.8)
            listed = (rng.random((LOGS, k * per)) < keep_p).astype(float)
            count = listed.reshape(LOGS, k, per).sum(2)
            inc = (x * listed).reshape(LOGS, k, per).sum(2) / np.maximum(count, 1)
            t0, t3 = slope_t(count, inc)
            degenerate = ~np.isfinite(t0)  # every block with the same count: no slope is estimable
            row[label] = {'HC0_normal (version 34 statistic)': rate(np.abs(np.nan_to_num(t0)) > stats.norm.ppf(0.975)),
                          'HC3_t(K-2)': rate(np.abs(np.nan_to_num(t3)) > stats.t.ppf(0.975, k - 2)),
                          'degenerate_share': rate(degenerate)}
        res[f'blocks={k} events_per_block={per}'] = row
out['4307728264 RC-229 increment screen, two-sided 5 %, rejection rate over 4,000 logs'] = res

# ================= 4307728271 (RC-230): deleting a script with its appendix block =================
# A synthetic tree with two evidence scripts, round2 and round3, each byte-identical to its appendix block and
# printing its committed output. Scenario `co_deleted` removes round3_checks.py and the round3 block together;
# `inventory_deleted` removes the inventory as well. The version-34 checker is that of commit 98b03fc and the remedy
# checker that of 784183f, both read from committed fixtures (RC-236).
SCRIPT = "print('{\"x\": %d}')\n"


def block(n):
    return (f'<!-- round{n}-script:start -->\n```python\n{SCRIPT % n}```\n<!-- round{n}-script:end -->\n\n'
            f'```json\n{{"x": {n}}}\n```\n\n')


def tree(root, rounds, inventory, checker_source):
    rep = root / 'research' / 'reproduction'
    rep.mkdir(parents=True)
    (root / 'research' / '16-reconciliation-matrix.md').write_text(''.join(block(n) for n in rounds))
    for n in rounds:
        (rep / f'round{n}_checks.py').write_text(SCRIPT % n)
    if inventory:
        (rep / 'inventory.txt').write_text(''.join(f'round{n}_checks.py round{n}\n' for n in (2, 3)))
    (rep / 'check_appendix_scripts.py').write_text(checker_source)


def fixture(name, sha256):
    """A committed historical input under fixtures/, pinned by its SHA-256 (RC-236: reading it with git show from
    commits that a squash merge leaves unreachable broke the reproduction from the committed revision)."""
    data = (HERE / 'fixtures' / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == sha256, name
    return data.decode('utf-8')


checkers = {
    'version34_checker': fixture('check_appendix_scripts.98b03fc.py.txt',
                                 '544b95d1a131e3295d354720d76baf4e28167b1e5d7a28b95b3b8b4cd8b10d9f'),
    'remedy_checker': fixture('check_appendix_scripts.784183f.py.txt',
                              'ed85ed70a300b4d245c4d3080cfe25d0aaf5df3c6b1f45419123e2bb31f2d31d'),
}
res = {}
for scenario, rounds, inventory in (('intact', (2, 3), True), ('co_deleted', (2,), True),
                                    ('inventory_deleted', (2,), False)):
    for name, source in checkers.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tree(root, rounds, inventory, source)
            run = subprocess.run([sys.executable, '-I', 'research/reproduction/check_appendix_scripts.py'],
                                 cwd=root, capture_output=True, text=True)
            res[f'{scenario} / {name}'] = {'exit_code': run.returncode, 'stdout': run.stdout.strip().splitlines()}
out['4307728271 RC-230 checker on a synthetic tree'] = res

# ================= 4307728277 (RC-231): version labels of the reading order =================
# The remedy checker's version_failures, run on the lines of each commit's three documents that its four labels are
# read from (fixtures labels-3fe4b06 and labels-98b03fc, RC-236).
remedy = {'__name__': 'remedy_checker', '__file__': str(HERE / 'fixtures' / 'check_appendix_scripts.784183f.py.txt')}
exec(compile(checkers['remedy_checker'], remedy['__file__'], 'exec'), remedy)
LABELS = {'3fe4b06': ('baf8d425377ae5fab430a66ca2122f2a62fef958e2b6385f83ed77dd6cf506ad',
                      '182e30901e29f02eb502df39e010a0aa1ba8f403f66c88dc78a34337246190d3',
                      'e5f7cb18af387f173881b54f4be572d395b90a15b9e880d374ae40181184a714'),
          '98b03fc': ('0226470eeef9f549bf8e00867c6144d45acf247f33a057d44766bd42ef5c17cc',
                      'a5c3113eaa2048fb8c2aedd87008fb98b70a52f1b3636c5fdcebb8a1479dc83f',
                      'e5f7cb18af387f173881b54f4be572d395b90a15b9e880d374ae40181184a714')}
res = {}
for commit, digests in LABELS.items():
    texts = [fixture(f'labels-{commit}/{name}', digest) for name, digest in
             zip(('16-reconciliation-matrix.md', '17-phase1-amended-specification.md', 'README.md'), digests)]
    res[commit] = remedy['version_failures'](*texts) or ['labels agree']
out['4307728277 RC-231 version-label check'] = res

print(json.dumps(out, indent=1))
