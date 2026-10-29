"""Round-28 checks for the Codex findings on PR #4 at 8e27c47 (no reference code, no network).

Codex's automatic review of 8e27c47, posted as PR #4 comment 6249849655 (four findings, keyed by order):
6249849655/1 (RC-198, the item-keyed omission draw left in 17 section 2 item 2; deterministic, the count is Appendix
AA's), 6249849655/2 (RC-199, tool names in 17 section 8; textual), 6249849655/3 (RC-200, a drawn cluster whose
registration is delayed until its outcome is public), 6249849655/4 (RC-201, the section 7 state of 16; textual).

Setting of RC-187 and RC-191 (Appendices Y and Z): 200 eligible clusters, half with mean increment +d and half -d, so
the eligible-population mean is exactly zero; noise sd sigma; Bernoulli inclusion at pi = 0.5; one-sided test of the
included mean at the nominal 1.645 and at the illustrated c* = 2.254.
"""
import json
import math
import numpy as np

out = {}

# ================= 6249849655/3 (RC-200): registration delayed until the outcome is public =================
# 17 v24 section 3 item 1: a cluster whose knowable_at is at or before its registration record is a registration
# breach and leaves the scored population. Nothing fixes when a drawn cluster must be registered, so a registrar who
# delays the registration of drawn clusters of one stratum until their outcomes are public turns them into
# registration breaches, although the log is complete and every draw is unchosen. Here a share q of the drawn
# negative-stratum clusters is delayed past its knowable time.
# Remedy: the committed code registers every drawn cluster at its batch's scheduled time t_reg,b, fixed by the
# pre-registered batch calendar; the registration-breach test reads t_reg,b, and a registration recorded after
# t_reg,b is a late registration that enters as a missing cluster (every slot free) under the VOID cap and through the
# box rule. The box rejects only if every point of the box rejects, the honest sample is a point of the box, and the
# vertex with every late increment at -1 is another point, so its rejection rate bounds the box's from above.
rng = np.random.default_rng(2200)
NC, D, SIG, PI, H = 200, 0.01, 0.02, 0.5, 20000
mu = np.where(np.arange(NC) < NC // 2, D, -D)
neg = np.arange(NC) >= NC // 2

def t_stat(x):
    return x.mean() / (x.std(ddof=1) / math.sqrt(x.size))

def delay(q):
    rej = {'v24_nom': 0, 'v24_cal': 0, 'honest_nom': 0, 'honest_cal': 0, 'vertex_nom': 0, 'vertex_cal': 0}
    shift = late = included = 0.0
    for _ in range(H):
        drawn = rng.random(NC) < PI
        x = mu + SIG * rng.standard_normal(NC)
        delayed = drawn & neg & (rng.random(NC) < q)
        t_v24 = t_stat(x[drawn & ~delayed])
        t_honest = t_stat(x[drawn])
        x_vertex = np.where(delayed, -1.0, x)
        t_vertex = t_stat(x_vertex[drawn])
        for name, t in (('v24', t_v24), ('honest', t_honest), ('vertex', t_vertex)):
            rej[f'{name}_nom'] += t > 1.645
            rej[f'{name}_cal'] += t > 2.254
        shift += mu[drawn & ~delayed].mean()
        late += delayed.sum()
        included += drawn.sum()
    return {'v24_delayed_clusters_removed_as_registration_breaches': {
                'rejection_at_1.645': round(rej['v24_nom'] / H, 4), 'rejection_at_2.254': round(rej['v24_cal'] / H, 4),
                'mean_included_true_effect': round(shift / H, 5)},
            'honest_sample_registered_on_schedule': {
                'rejection_at_1.645': round(rej['honest_nom'] / H, 4), 'rejection_at_2.254': round(rej['honest_cal'] / H, 4)},
            'remedy_box_vertex_late_increments_at_minus_1': {
                'rejection_at_1.645': round(rej['vertex_nom'] / H, 4), 'rejection_at_2.254': round(rej['vertex_cal'] / H, 4)},
            'late_share_of_drawn_clusters': round(late / included, 4)}

rc200 = {'clusters': NC, 'd': D, 'sigma': SIG, 'pi': PI, 'histories': H}
for q in (0.0, 0.1, 0.25, 0.5, 1.0):
    rc200[f'delayed_share_of_drawn_negative_stratum={q}'] = delay(q)

# Deterministic schedule fixture: batch window [0, 10), scheduled registration t_reg = 12, beacon round published at
# 11. Cluster P is registered on schedule; Q is delayed to 20 and its outcome is knowable at 15; R's outcome is
# knowable at 8, before t_reg, and is a registration breach under both rules.
def classify(knowable_at, registered_at, t_reg, rule):
    reference = registered_at if rule == 'v24' else t_reg
    if knowable_at <= reference:
        return 'registration_breach_outside_scored_population'
    if rule == 'remedy' and registered_at > t_reg:
        return 'late_registration_missing_cluster_box_rule_under_void_cap'
    return 'scored'

fixture = {'P': (30, 12), 'Q': (15, 20), 'R': (8, 12)}
rc200['schedule_fixture'] = {
    't_reg': 12,
    'clusters': {k: {'knowable_at': ka, 'registered_at': ra,
                     'v24': classify(ka, ra, 12, 'v24'), 'remedy': classify(ka, ra, 12, 'remedy')}
                 for k, (ka, ra) in fixture.items()}}
out['6249849655/3 RC-200'] = rc200

print(json.dumps(out, indent=1))
