"""Round-36 checks for the Codex findings on PR #4 at 1316328 (no reference code, no network).

Codex's review 5563539500 of 1316328, five inline findings (four P1, one P2); three are checked here:
- 4307491641 (RC-220): version 32 admits a cluster whose earliest-knowable bound e_i follows the enrolment end T_E,
  while the batch anchor, beacon round, draw and registration record of the last window are scheduled after the
  window ends, during the registration lag. An outcome knowable between T_E and the anchor precedes the snapshot
  from which an audited omission's linkage is read.
- 4307491649 (RC-222): version 32 states the primary's null cluster by cluster (each eligible cluster's increment
  has conditional mean at most zero), which is stronger than the population-average null of section 6 and excludes
  the valid-null fixture F-23 of T-12.
- 4307491653 (RC-223): version 32 says that supply responding to a breach selects only on the boxed increment,
  "under the independence across clusters that the block statistic assumes". The block statistic assumes
  independence across calendar blocks, not across clusters; a breach can reveal a block's shared shock.

Statistic: the fixed-horizon block statistic of T-12 in its simplest form, the cluster mean over the cohort divided
by its block-sum standard error over G = 24 calendar blocks, one-sided at the nominal 1.645; 20,000 replications.
"""
import json

import numpy as np

out = {}
REPS, CRIT, G = 20_000, 1.645, 24


def block_t(x, w, block):
    """Cluster-weighted mean over the kept clusters, standard error from the centred block sums."""
    n = w.sum(1)
    m = (x * w).sum(1) / n
    centred = (x - m[:, None]) * w
    sums = np.stack([centred[:, block == g].sum(1) for g in range(G)], 1)
    se = np.sqrt((sums ** 2).sum(1) * G / (G - 1)) / n
    return m / se


def rate(rej):
    return round(float(rej.mean()), 4)


# ================= 4307491641 (RC-220): the last batch is anchored after T_E =================
# Deterministic fixture in Codex's terms. T_E = 100; the last batch window is [90, 100); the registration lag is 5,
# so the anchor is written at 101, the beacon round at 103 and the registration record at t_reg = 105. Member A has
# e_i = 100.5 and an outcome knowable at 100.5 (its bound is correct). Candidate B is an audited omission of the
# same window whose cluster assignment is read from the source archive at the anchor time 101.
T_E, WINDOW_END, LAG = 100.0, 100.0, 5.0
anchor, beacon, t_reg = WINDOW_END + 1.0, WINDOW_END + 3.0, WINDOW_END + LAG
e_a = knowable_a = 100.5
version32 = {
    'A_eligible (e_i > T_E)': e_a > T_E,
    'A_outcome_knowable_before_anchor': knowable_a < anchor,
    'B_linkage_read_after_A_outcome': anchor > knowable_a,
    'A_registration_record_before_smallest_e_i (closure rule)': t_reg < e_a,
}
# Remedy: the batch calendar of the cohort ends so that every t_reg,b <= T_E; here the last window is [85, 95).
remedy_t_reg = 95.0 + LAG
remedy = {
    'every_t_reg_at_or_before_T_E': remedy_t_reg <= T_E,
    'A_eligible (e_i > T_E)': e_a > T_E,
    'A_outcome_knowable_before_anchor': knowable_a < 95.0 + 1.0,
    'A_registration_record_before_smallest_e_i (closure rule)': remedy_t_reg < e_a,
}
out['4307491641 RC-220 fixture'] = {'version32': version32, 'calendar_ends_by_T_E': remedy}

# ================= 4307491649 (RC-222): the per-cluster null excludes F-23 =================
# F-23 of T-12: E[X_k] = +0.12 for the first 60 clusters and -0.12 for the next 60. Clusters are spread evenly over
# the 24 blocks in order, so the first 12 blocks carry +0.12 and the last 12 carry -0.12. Increments are +-0.2 around
# the cluster mean (clipped to [-1, 1]); the null class of the primary is the population-average null.
rng = np.random.default_rng(3601)
N23 = 120
mean23 = np.where(np.arange(N23) < 60, 0.12, -0.12)
block23 = np.repeat(np.arange(G), N23 // G)
x23 = np.clip(mean23 + np.where(rng.random((REPS, N23)) < 0.5, 0.2, -0.2), -1, 1)
out['4307491649 RC-222 F-23'] = {
    'clusters_with_positive_mean': int((mean23 > 0).sum()),
    'population_average_mean': round(float(mean23.mean()), 6),
    'in_version32_per_cluster_null': bool((mean23 <= 0).all()),
    'in_population_average_null': bool(mean23.mean() <= 0),
    'block_test_rejection_at_1.645': rate(block_t(x23, np.ones_like(x23), block23) > CRIT),
}

# ================= 4307491653 (RC-223): supply that responds to a revealed block shock =================
# No-skill law with a shared block shock: X_k = s_g + e_k, s_g = +-0.05 with probability 1/2 per block (a regime in
# which FULL's constant bias scores better or worse than the baseline), e_k = +-0.2, 25 eligible clusters per block
# (600). The unconditional population-average null holds (E[X_k] = 0). With probability q a block's shock becomes
# public before T_E: by a pre-enrolment breach of one of the cohort's own clusters (its outcome knowable at or
# before T_E, the first cluster of the block), or by an outcome outside the cohort (another source, an earlier
# cohort, a candidate excluded because its e_i precedes T_E). A responsive source then lists only a share f of the
# block's remaining candidates when the revealed shock is negative.
# Rules: version32, the breached cluster is boxed and nothing else changes (its increment is kept here, the box
# being about informed forecasts, which this law does not have); non_confirmatory_if_pre_enrolment_breach, the
# remedy for the cohort's own outcomes; with an outside revelation no rule of the protocol sees the response, which
# is what the supply-exogeneity assumption states.
PER, F_KEEP = 25, 0.2
N = G * PER
block = np.repeat(np.arange(G), PER)
first = np.zeros(N, bool)
first[::PER] = True


def shock_law(q, rng):
    s = np.where(rng.random((REPS, G)) < 0.5, 0.05, -0.05)
    x = s[:, block] + np.where(rng.random((REPS, N)) < 0.5, 0.2, -0.2)
    revealed = rng.random((REPS, G)) < q
    dropped = (revealed & (s < 0))[:, block] & ~first & (rng.random((REPS, N)) >= F_KEEP)
    return x, revealed, (~dropped).astype(float)


res = {}
for q in (0.05, 0.1, 0.25):
    rng = np.random.default_rng(3602 + int(q * 100))
    x, revealed, w = shock_law(q, rng)
    honest = rate(block_t(x, np.ones_like(x), block) > CRIT)
    responsive = block_t(x, w, block) > CRIT
    res[f'q={q}'] = {
        'cohorts_with_a_revelation': rate(revealed.any(1)),
        'honest_supply': honest,
        'responsive_supply (version32 on a breach; any rule on an outside revelation)': rate(responsive),
        'responsive_supply, non_confirmatory_if_pre_enrolment_breach': rate(responsive & ~revealed.any(1)),
    }
out['4307491653 RC-223 block shock revealed before T_E'] = res

# Power cost of the remedy: the confirmatory claim survives only if no eligible candidate of the cohort, drawn or
# not, has a pre-enrolment breach. With independent misdeclarations at rate p per candidate, P = (1 - p)^N.
out['RC-223 probability of no pre-enrolment breach'] = {
    f'N={n}': {f'p={p:g}': round((1 - p) ** n, 4) for p in (1e-5, 1e-4, 1e-3)} for n in (600, 1200, 2400)}

print(json.dumps(out, indent=1))
