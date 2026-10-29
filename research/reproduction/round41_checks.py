"""Round-41 checks for the Codex findings on PR #4 at 11dfeed (no reference code, no network).

Codex's PR #4 comment 6254552067 on 11dfeed, three findings (all P1); two are checked here:
- finding 2 (RC-243): version 37 reads an omitted universe event's cluster from the reference universe and a listed
  event's cluster from the source archive, so one universe cluster can receive two cluster ids, two draws and two
  weights.
- finding 3 (RC-244): the pre-enrolment-breach audit of version 37 reads outcome publications from each source's
  archive, which holds no record of a universe event the source never listed.
Finding 1 (RC-242) is a commit identity and has no script.
"""
import hashlib
import json

import numpy as np
from scipy import stats

out = {}


def rate(rej):
    return round(float(np.mean(rej)), 4)


# ================= finding 2 (RC-243), part 1: two cluster authorities, two draws =================
# 10,000 universe pairs {A_n, B_n}, linked in the universe's point-in-time state. The source lists A_n as a singleton
# (its archive holds no link) and does not list B_n. Version 37: A_n's cluster is the source's singleton, id 'A<n>';
# B_n is an audited omission whose cluster is the universe pair, id 'P<n>'. Each cluster is drawn by its id with the
# batch seed at pi = 0.5. The honest universe sample draws the pair whole by 'P<n>'.
SEED, PI, PAIRS = 'round41-batch-seed', 0.5, 10_000


def draw(cluster_id):
    digest = hashlib.sha256(f'{SEED}:{cluster_id}'.encode()).digest()
    return int.from_bytes(digest, 'big') / 2 ** 256 < PI


a_drawn = np.array([draw(f'A{n}') for n in range(PAIRS)])
pair_drawn = np.array([draw(f'P{n}') for n in range(PAIRS)])
out['finding 2, RC-243: draws of 10,000 universe pairs under two cluster authorities, pi = 0.5'] = {
    'A and B drawn differently (version 37)': int((a_drawn != pair_drawn).sum()),
    'A in the version-37 sample, pair not in the honest sample': int((a_drawn & ~pair_drawn).sum()),
    'pair in the honest sample, A not in the version-37 sample': int((~a_drawn & pair_drawn).sum()),
    'A and B drawn differently (universe authority for both)': 0,
}

# ================= finding 2 (RC-243), part 2: the source's linkage sets the weights =================
# Law: no skill. Block g holds 10 universe clusters of 3 events; event i of cluster k has the increment
# s_g + c_k + 0.2 r_i with s_g = +-0.05 (block shock), c_k = +-0.1 (cluster shock) and r_i = +-1, all fair, so the
# mean over clusters of the cluster means has expectation zero. Every event is listed and drawn (pi = 1), so there
# is no omission and the VOID cap and the box rule never act. The source's archive links the events of a universe
# cluster as follows: an event whose signal on r_i (right with probability RHO) is favourable is a singleton, and
# the rest of the universe cluster stays one cluster. Statistic (`17` section 3 item 3, RC-69): theta = mean over
# clusters of the cluster means, variance in the block-sum form sum_g (sum_{k in g} (X_k - theta))^2 / N^2 * G/(G-1),
# one-sided t on G - 1 degrees of freedom at 5 %.
# - version 37: the clusters of listed events are the source's (lines 726-731 of 17 at 11dfeed);
# - remedy: the clusters of every universe event are the universe's.
# RHO = 0.5 is a source whose linkage differs from the universe's without reading anything: an honest disagreement.
LOGS, CHUNK = 4_000, 500


def t_reject(sums, n_clusters):
    g = sums.shape[1]
    total = n_clusters.sum(1)
    theta = sums.sum(1) / total
    var = ((sums - n_clusters * theta[:, None]) ** 2).sum(1) / total ** 2 * g / (g - 1)
    return theta / np.sqrt(var) > stats.t.ppf(0.95, g - 1)


def linkage_chunk(rng, logs, g, rho):
    shape = (logs, g, 10, 3)
    s = np.where(rng.random((logs, g, 1, 1)) < 0.5, 0.05, -0.05)
    c = np.where(rng.random((logs, g, 10, 1)) < 0.5, 0.1, -0.1)
    r = np.where(rng.random(shape) < 0.5, 1.0, -1.0)
    x = s + c + 0.2 * r
    fav = np.where(rng.random(shape) < rho, r, -r) > 0
    universe = (x.mean(3).sum(2), np.full((logs, g), 10.0))
    rest = (~fav).sum(3)
    with np.errstate(invalid='ignore', divide='ignore'):
        rest_mean = np.where(rest > 0, (x * ~fav).sum(3) / rest, 0.0)
    source = ((x * fav).sum((2, 3)) + rest_mean.sum(2), (fav.sum(3) + (rest > 0)).sum(2).astype(float))
    return t_reject(*universe), t_reject(*source)


res = {}
for g in (24, 48, 100):
    row = {}
    for rho in (0.5, 0.75, 0.9):
        rng = np.random.default_rng(4101 + 7 * g + int(100 * rho))
        rem, v37 = [], []
        for _ in range(0, LOGS, CHUNK):
            a, b = linkage_chunk(rng, CHUNK, g, rho)
            rem.append(a)
            v37.append(b)
        row[f'rho={rho}'] = {'version 37 (source clusters for listed events)': rate(np.concatenate(v37)),
                             'remedy (universe clusters for every event)': rate(np.concatenate(rem))}
    res[f'blocks={g}'] = row
out[f'finding 2, RC-243: rejection at no skill over {LOGS:,} logs, every event listed'] = res

# ================= finding 3 (RC-244), part 1: whose record shows the breach =================
# A deterministic fixture. T_E = 100. Universe event E3 resolves early: the resolution source publishes its outcome
# at 80. The source lists E1 and E2 and never lists E3, so its archive has outcome publications for E1 and E2 only.
T_E = 100
universe_events = ('E1', 'E2', 'E3')
resolution_record = {'E1': 140, 'E2': 155, 'E3': 80}
source_archive = {'E1': 140, 'E2': 155}


def breaches(record):
    return sorted(e for e in universe_events if e in record and record[e] <= T_E)


out['finding 3, RC-244: pre-enrolment breaches found, T_E = 100'] = {
    'version 37 (each source archive)': breaches(source_archive),
    'events with no knowable_at record (version 37)': sorted(set(universe_events) - set(source_archive)),
    'remedy (the resolution record of every universe event)': breaches(resolution_record),
}

# ================= finding 3 (RC-244), part 2: a source that reads the undetected outcome =================
# Law: no skill. Block g holds 60 eligible universe events with the increment s_g + 0.2 r_i (s_g = +-0.05, r_i = +-1)
# and one more universe event whose outcome is published before T_E and reveals the sign of s_g (the RC-223 channel).
# The source never lists that event, and in a block it reveals as negative it omits a fraction Q of the 60 events at
# random; it lists everything else. Every event is a cluster of one and is drawn (pi = 1). Statistic as above.
# - no universe audit (version 36): the population is the listed events;
# - version 37: the universe audit; the omitted share of the universe above CAP makes the primary
#   non-confirmatory, otherwise every omission enters at the lower end of its box, -1; the breach is not on record;
# - remedy: the breach is read from the resolution record, so the primary is exploratory in every log.
# The box is taken at its lower end; the conservative kappa_A form is not simulated, and CAP = 0.05 is illustrative.
CAP = 0.05


def breach_chunk(rng, logs, g, q):
    neg = rng.random((logs, g)) < 0.5
    s = np.where(neg, -0.05, 0.05)
    x = s[..., None] + 0.2 * np.where(rng.random((logs, g, 60)) < 0.5, 1.0, -1.0)
    listed = ~(neg[..., None] & (rng.random((logs, g, 60)) < q))
    v36 = t_reject((x * listed).sum(2), listed.sum(2).astype(float))
    omitted = (~listed).sum(2) + 1
    share = omitted.sum(1) / (61 * g)
    boxed = (x * listed).sum(2) - omitted
    v37 = (share <= CAP) & t_reject(boxed, np.full((logs, g), 61.0))
    return v36, v37, share > CAP


res = {}
for g in (24, 48, 100):
    row = {}
    for q in (0.0, 0.02, 0.1, 0.5):
        rng = np.random.default_rng(4111 + 7 * g + int(100 * q))
        parts = [breach_chunk(rng, CHUNK, g, q) for _ in range(0, LOGS, CHUNK)]
        v36, v37, nc = (np.concatenate(p) for p in zip(*parts))
        row[f'q={q}'] = {'no universe audit (version 36)': rate(v36),
                         'version 37, breach not on record': rate(v37),
                         'version 37, non-confirmatory by the VOID cap': rate(nc),
                         'remedy, confirmatory rejections': 0.0}
    res[f'blocks={g}'] = row
out[f'finding 3, RC-244: rejection at no skill over {LOGS:,} logs, VOID cap {CAP}'] = res

print(json.dumps(out, indent=1))
