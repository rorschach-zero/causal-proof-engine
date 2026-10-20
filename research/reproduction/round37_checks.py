"""Round-37 checks for the Codex findings on PR #4 at 3fe4b06 (no reference code, no network).

Codex's review 5563721285 of 3fe4b06, four inline findings (three P1, one P2); three are checked here:
- 4307641029 (RC-226): `--reference-code` given without a value is parsed as no reference code, so the checker
  reports the probe output as not compared and can exit 0 although the caller asked for the comparison.
- 4307641032 (RC-227): version 33 counts a pre-enrolment breach of an undrawn eligible candidate, first recorded
  after T_D, as a late record covered by eta, while eta is still defined over the members of the primary cohort and
  its bounds u_i,m over members only.
- 4307641036 (RC-228): version 33 says a source listing from a calendar published before T_0 satisfies supply
  exogeneity by construction, and tests every other source by the association of its listing rate with the block's
  realised outcome rate. Neither establishes independence from the increments: a calendar can be chosen on a
  pre-T_0 signal of a block's relative skill, and a source can respond to relative skill at a constant YES rate.

Statistic: the fixed-horizon block statistic of Appendix AJ, one-sided at the nominal 1.645, G = 24 calendar blocks.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import stats

out = {}
REPS, CRIT, G, PER = 20_000, 1.645, 24, 25
N = G * PER
block = np.repeat(np.arange(G), PER)


def block_t(x, w, block, g=G):
    """Cluster-weighted mean over the kept clusters, standard error from the centred block sums."""
    n = w.sum(1)
    m = (x * w).sum(1) / n
    centred = (x - m[:, None]) * w
    sums = np.stack([centred[:, block == b].sum(1) for b in range(g)], 1)
    se = np.sqrt((sums ** 2).sum(1) * g / (g - 1)) / n
    return m / se


def rate(rej):
    return round(float(np.mean(rej)), 4)


# ================= 4307641029 (RC-226): a valueless --reference-code =================
checker = Path(__file__).resolve().parent / 'check_appendix_scripts.py'
version33_parse = {}
for argv in (['--reference-code'], ['--reference-code', '--other'], ['--reference-code', 'v02']):
    version33_parse[' '.join(argv)] = argv[argv.index('--reference-code') + 1:][:1]
remedy = {}
for argv in (['--reference-code'], ['--reference-code', '--reference-code'], ['--reference-code', 'a', 'b'],
             ['--reference-code', 'no/such/directory'], ['--other']):
    run = subprocess.run([sys.executable, '-I', str(checker), *argv], capture_output=True, text=True)
    remedy[' '.join(argv)] = {'exit_code': run.returncode, 'stdout': run.stdout.strip()}
out['4307641029 RC-226 argument parsing'] = {'version33_reference_value': version33_parse,
                                             'remedy_checker': remedy}

# ================= 4307641032 (RC-227): eta over members, a late breach of an undrawn candidate =================
# Two eligible candidates of one window, A and C, each drawn independently with pi = 1/2. u_A and u_C bound the
# probability that a breach of the candidate (here a pre-enrolment breach, an outcome knowable at or before T_E) is
# first recorded after T_D. Version 33 defines eta as the probability that a breach or defect of a member of the
# primary cohort is recorded after T_D; the size argument of item (i) charges to eta the probability that a
# pre-enrolment breach of any eligible candidate, drawn or not, is recorded after T_D.
PI, U_A, U_C = 0.5, 0.004, 0.006
eta_members = 1 - (1 - PI * U_A) * (1 - PI * U_C)
needed = 1 - (1 - U_A) * (1 - U_C)
out['4307641032 RC-227 fixture'] = {
    'eta_version33 (registered members)': round(eta_members, 6),
    'P(late pre-enrolment breach of an eligible candidate), charged to eta in (i)': round(needed, 6),
    'undrawn_C_late_breach_outside_eta_version33': round((1 - PI) * U_C, 6),
    'eta_max_at_version33_eta (bound fails if eta_max = eta)': bool(needed <= eta_members),
    'boole_sum_over_eligible (the close of RC-188)': round(U_A + U_C, 6),
    'eta_over_eligible_at_most_boole_sum': bool(needed <= U_A + U_C),
}

# ================= 4307641036 (RC-228): supply exogeneity is not timing and not the outcome rate =================
# No-skill law of Appendix AJ: X_k = s_g + e_k, s_g = +-0.05 per block with probability 1/2, e_k = +-0.2, 24 blocks
# of 25 eligible clusters; the unconditional population-average null holds. Outcomes Y_k are Bernoulli(1/2)
# independent of the shock and of e_k, so the YES rate carries nothing about the relative skill (Codex's case).
F_KEEP = 0.2


def law(rng, reps, g, per):
    s = np.where(rng.random((reps, g)) < 0.5, 0.05, -0.05)
    b = np.repeat(np.arange(g), per)
    x = s[:, b] + np.where(rng.random((reps, g * per)) < 0.5, 0.2, -0.2)
    y = (rng.random((reps, g * per)) < 0.5).astype(float)
    return s, b, x, y


# (a) A calendar published before T_0, chosen on a pre-T_0 signal of each block's shock that is right with
# probability rho: in a block signalled negative the calendar holds only a fifth of the block's events (at least one).
res = {}
for rho in (0.6, 0.75, 0.9):
    rng = np.random.default_rng(3701 + int(rho * 100))
    s, b, x, _ = law(rng, REPS, G, PER)
    signal_neg = np.where(rng.random((REPS, G)) < rho, s < 0, s > 0)
    first = np.zeros(N, bool)
    first[::PER] = True
    w = (~(signal_neg[:, b] & ~first & (rng.random((REPS, N)) >= F_KEEP))).astype(float)
    res[f'rho={rho}'] = {'honest_calendar': rate(block_t(x, np.ones_like(x), b) > CRIT),
                         'pre_T0_calendar_on_signal': rate(block_t(x, w, b) > CRIT)}
out['4307641036 RC-228 (a) pre-T0 calendar chosen on a relative-skill signal'] = res


# (b) The Phase 2 test of a source's supply. A Phase 2 log of K blocks of 25 candidate events. An honest source lists
# each with probability 0.8. In a share q of blocks a relative-skill shock is revealed before the block's later events
# (by an outside outcome, Appendix AJ); a responsive source then lists each later event with probability 0.2 when the
# revealed shock is negative; the law (a) source thins on its pre-T_0 signal instead. Per block: the listed count, the
# realised YES rate and the realised mean increment (the Brier-score difference of the primary pair) over the listed
# events. Version 33 tests the association of the listing with the YES rate; the remedy tests the association of the
# listing with the mean increment. Two-sided robust slope test over blocks at 5 %; 1,000 Phase 2 logs.
def slope_reject(a, c):
    """Two-sided 5 % test of a zero slope of c on a over blocks, with the heteroscedasticity-robust (HC0) standard
    error: a thinned block has fewer listed events and so a noisier rate, which a plain correlation t-test would
    read as association."""
    a = a - a.mean(1, keepdims=True)
    sxx = (a ** 2).sum(1)
    slope = (a * c).sum(1) / sxx
    resid = c - c.mean(1, keepdims=True) - slope[:, None] * a
    se = np.sqrt((a ** 2 * resid ** 2).sum(1)) / sxx
    return np.abs(slope / se) > stats.norm.ppf(0.975)


K, LOGS = 400, 1_000
res = {}
for label, q, rho in (('honest', 0.0, None), ('q=0.1', 0.1, None), ('q=0.25', 0.25, None), ('q=0.5', 0.5, None),
                      ('pre_T0_calendar rho=0.75 (law (a))', 1.0, 0.75)):
    rng = np.random.default_rng(3711 + int(q * 100) + (0 if rho is None else 1000))
    s, b, x, y = law(rng, LOGS, K, PER)
    revealed = rng.random((LOGS, K)) < q
    if rho is not None:
        s = np.where(rng.random((LOGS, K)) < rho, s, -s)  # the source acts on its signal, right with probability rho
    later = np.ones(K * PER, bool)
    later[::PER] = False
    keep_p = np.where((revealed & (s < 0))[:, b] & later, F_KEEP, 0.8)
    listed = (rng.random((LOGS, K * PER)) < keep_p).astype(float)
    count = listed.reshape(LOGS, K, PER).sum(2)
    safe = np.maximum(count, 1)
    yes = (y * listed).reshape(LOGS, K, PER).sum(2) / safe
    inc = (x * listed).reshape(LOGS, K, PER).sum(2) / safe
    res[label] = {'outcome_rate_test (version 33)': rate(slope_reject(count, yes)),
                  'increment_test (remedy)': rate(slope_reject(count, inc))}
out['4307641036 RC-228 (b) Phase 2 supply test at a constant YES rate, rejection rate'] = res

print(json.dumps(out, indent=1))
