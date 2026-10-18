"""Round-18 checks for the Codex findings on PR #4 at 7d11065 (no reference code, no network).

Review 5562262057. Each block is keyed by the review-comment id it answers. The crash model extends the RC-153 toy
model of 16 Appendix Q; the cluster-weighted statistic with block-sum variance over occupied blocks is that of
16 Appendix F and L to R.
"""
import json, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
REPS = 20000

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def rate(reject):
    return {'rate': round(float(reject.mean()), 4), 'upper_99': round(binom_upper(int(reject.sum()), reject.size, 0.99), 4)}

# ================= r4306464068 (RC-158): anchor the commit record before acknowledging =================
# Toy model. A protected action consumes a nonce (intent record) and changes state (commit record). Protocols:
# V15 = intent, anchor of the prefix ending at the intent, commit (the state change takes effect), ack (version 15);
# V16 = intent, anchor, commit (not yet effective), anchor of the prefix ending at the commit, effect and ack.
# Start-up recovery: a pending intent (neither commit nor abort) is aborted; under V16 a commit outside every anchor
# is anchored (idempotently, keyed by the intent id) and only then takes effect, unacknowledged. A crash happens
# after each step or not at all; afterwards the ledger is kept or restored to the last anchor, recovery runs and the
# same capability is presented again.
# Invariants: I1 the action takes effect at most once; I2 no anchor covers a prefix the local ledger never held;
# I3 (Appendix Q) an acknowledged action has some anchor; I3s an acknowledged commit is in the final ledger;
# I4 no state change that took effect is lost from the final ledger.
STEPS = {'V15': ['intent', 'anchor', 'commit_effective', 'ack'],
         'V16': ['intent', 'anchor', 'commit', 'anchor', 'effect_ack']}
def run(protocol, crash_after, restore):
    ledger, anchors, applied, acked = [], [], [], []
    def apply(pos):
        applied.append(pos)
    def present(crash_at):
        if any(r == 'intent' for r in ledger):
            return
        for i, st in enumerate(STEPS[protocol]):
            if st == 'intent':
                ledger.append('intent')
            elif st == 'anchor':
                anchors.append(len(ledger))
            elif st in ('commit', 'commit_effective'):
                ledger.append('commit')
                if st == 'commit_effective':
                    apply(len(ledger) - 1)
            elif st == 'ack':
                acked.append(ledger.index('commit'))
            elif st == 'effect_ack':
                apply(len(ledger) - 1)
                acked.append(len(ledger) - 1)
            if i == crash_at:
                return
    def recover():
        if ledger and ledger[-1] == 'intent':
            ledger.append('abort')
        if protocol == 'V16' and 'commit' in ledger:
            pos = ledger.index('commit')
            if max(anchors, default=0) <= pos:
                anchors.append(len(ledger))
            if pos not in applied:
                apply(pos)
    present(crash_after)
    i2 = all(a <= len(ledger) for a in anchors)
    recover()
    if restore:
        del ledger[max(anchors, default=0):]
        recover()
    present(None)
    final = set(i for i, r in enumerate(ledger) if r == 'commit')
    return {'I1': len(applied) <= 1, 'I2': i2, 'I3': (not acked) or max(anchors, default=0) >= 1,
            'I3s': all(p in final for p in acked), 'I4': all(p in final for p in applied)}
rc158 = {}
for proto in ('V15', 'V16'):
    viol = []
    for k in list(range(len(STEPS[proto]))) + [None]:
        for restore in (False, True):
            res = run(proto, k, restore)
            bad = [key for key in ('I1', 'I2', 'I3', 'I3s', 'I4') if not res[key]]
            if bad:
                viol.append({'crash_after_step': k, 'restore_to_last_anchor': restore, 'violated': bad})
    rc158[proto] = {'cases': 2 * (len(STEPS[proto]) + 1), 'violations': viol}
out['RC158_commit_anchor_before_ack'] = rc158

# ================= r4306464071 (RC-159): all-VOID clusters in the denominator of the VOID cap =================
# 100 two-member clusters. Cluster D: both members adjudicated VOID (F-24 case D); cluster P: both members pending
# at T_A; one further cluster with one adjudicated VOID beside a scored member. Population read as the clusters that
# emit an increment (a cluster with no scored member emits nothing) against every eligible cluster with at least one
# member that is neither pre-declared VOID nor in a registration-breach cluster.
sizes = np.full(100, 2.0)
voids = np.zeros(100); voids[0] = 2; voids[1] = 2; voids[2] = 1
emits = voids < sizes
rc159 = {'clusters': 100, 'all_void_or_pending_clusters': 2,
         'share_over_emitting_clusters': round(float((voids[emits] / sizes[emits]).sum() / emits.sum()), 5),
         'share_over_every_eligible_cluster': round(float((voids / sizes).sum() / sizes.size), 5)}
out['RC159_void_cap_denominator'] = rc159

# ================= r4306464073 (RC-160): unequal inclusion probabilities in the eligible-event subsample =================
# Eligible population: 1,200 clusters over 24 calendar blocks (50 per block), half in stratum S+ with
# P(Y = 1) = 0.5 + 0.025 and half in S- with 0.5 - 0.025, baseline 0.4, challenger 0.6, so X = 0.4 Y - 0.2 has
# E[X] = +0.01 in S+ and -0.01 in S-: the eligible-population mean is exactly zero (the null holds). Stratum is a
# registration-time feature, so a sampling rule may legitimately depend on it. Each cluster enters the subsample
# independently with probability pi(S+), pi(S-). Unweighted cluster mean, block-sum variance over occupied blocks,
# G - 1 df, rejection at the nominal one-sided 5 % value and at the illustrated c* = 2.254.
nb, per = 24, 50
n = nb * per
blocks = np.repeat(np.arange(nb), per)
plus = np.tile(np.arange(per) < per // 2, nb)
q = np.where(plus, 0.525, 0.475)
def t_masked(x, m):
    cnt = m.sum(axis=1)
    theta = (x * m).sum(axis=1) / cnt
    idx = (np.arange(x.shape[0])[:, None] * nb + blocks[None, :]).ravel()
    bs = np.bincount(idx, weights=((x - theta[:, None]) * m).ravel(), minlength=x.shape[0] * nb).reshape(-1, nb)
    occ = np.bincount(idx, weights=m.ravel(), minlength=x.shape[0] * nb).reshape(-1, nb) > 0
    g = occ.sum(axis=1)
    v = (bs ** 2).sum(axis=1) / cnt ** 2 * g / (g - 1)
    return theta / np.sqrt(v), g
rc160 = {'population_mean_of_E_X': round(float(np.where(plus, 0.01, -0.01).mean()), 6) + 0.0}
for label, pp, pm in (('equal_0.5', 0.5, 0.5), ('unequal_0.6_0.4', 0.6, 0.4), ('unequal_0.8_0.2', 0.8, 0.2)):
    rng = np.random.default_rng(18601)
    y = (rng.random((REPS, n)) < q).astype(float)
    x = 0.4 * y - 0.2
    m = (rng.random((REPS, n)) < np.where(plus, pp, pm)).astype(float)
    tt, g = t_masked(x, m)
    nominal = student_t.ppf(0.95, g - 1)
    rc160[label] = {'expected_mean_of_sample': round(float((pp * 0.01 - pm * 0.01) / (pp + pm)), 4),
                    'mean_sampled_clusters': round(float(m.sum(axis=1).mean()), 1),
                    'reject_nominal': rate(tt > nominal), 'reject_c_2.254': rate(tt > 2.254)}
out['RC160_unequal_inclusion'] = rc160

out['python'] = '.'.join(map(str, sys.version_info[:3]))
print(json.dumps(out, indent=2))
