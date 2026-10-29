"""Round-27 checks for the Codex findings on PR #4 at e564237 (no reference code, no network).

Codex review 5562875208 of e564237, five inline findings: 4306919946 (RC-193, the eta close when the audit finds
omissions), 4306919950 (RC-194, the label PROVED; textual), 4306919953 (RC-195, cluster records of audited omissions),
4306919957 (RC-196, the appendix checker; checked on a scratch tree, no block here), 4306919961 (RC-197, a demotion
between the steps of the four-step protocol).
"""
import hashlib
import json
import numpy as np

out = {}

# ================= 4306919946 (RC-193): the eta close over the log, not over the audited stream =================
# 17 v23 closes the registration window at tau, the first eligible candidate whose bound carries the running sum over
# every eligible candidate above eta_max (RC-188). The registry can only sum what is in the log. An omission the audit
# finds later is eligible, so the close computed over the log is later than the close over the eligible stream, and
# v23 acts on an omission only if it is drawn. Remedy: replay the close over the audited stream (log plus every
# omission at its listing time); registrations at or after the replayed tau leave the cohort by a pre-declared rule.
def close(stream, eta_max):
    """Record time of the first candidate whose bound carries the running sum above eta_max; None if it never binds."""
    total = 0.0
    for time, u in stream:
        total += u
        if total > eta_max + 1e-12:
            return time
    return None

ex = [(1, 0.6, 'A', True), (2, 0.6, 'B', False), (3, 0.3, 'C', True), (4, 0.3, 'D', True)]   # B never logged
tau_eligible = close([(t, u) for t, u, _, _ in ex], 1.0)
tau_log = close([(t, u) for t, u, _, logged in ex if logged], 1.0)
rc193 = {'example': {
    'eta_max': 1.0, 'candidates': [{'id': c, 'time': t, 'u': u, 'logged': lg} for t, u, c, lg in ex],
    'tau_over_eligible_stream': tau_eligible, 'tau_over_log_v23': tau_log,
    'cohort_over_eligible_stream': [c for t, _, c, _ in ex if t < tau_eligible],
    'cohort_over_log_v23': [c for t, _, c, lg in ex if lg and t < tau_log],
    'logged_bound_sum_inside_v23_window': round(sum(u for t, u, _, lg in ex if lg and t < tau_log), 3),
}}

# Monte Carlo: 400 candidates per stream, bounds 0.002 or 0.008 with equal probability, eta_max = 0.5, a share f of
# the high-bound candidates never logged, pi = 0.5. Reported: how often the v23 close falls later than the close over
# the eligible stream, by how many candidates, and the share of the analysed (logged, drawn) registrations that lie at
# or after the eligible close; and that the replay over log plus omissions equals the eligible close in every stream.
rng = np.random.default_rng(2193)
N, H, ETA, PI = 400, 5000, 0.5, 0.5
for f in (0.1, 0.25, 0.5):
    later = replay_equal = 0
    extension = []
    outside = analysed = 0
    for _ in range(H):
        u = np.where(rng.random(N) < 0.5, 0.008, 0.002)
        logged = ~((u == 0.008) & (rng.random(N) < f))
        drawn = rng.random(N) < PI
        times = np.arange(N)
        t_el = close(zip(times, u), ETA)
        t_lg = close(zip(times[logged], u[logged]), ETA)
        t_el = N if t_el is None else t_el
        t_lg = N if t_lg is None else t_lg
        audited = sorted(list(zip(times[logged], u[logged])) + list(zip(times[~logged], u[~logged])))
        t_rp = close(audited, ETA)
        replay_equal += (N if t_rp is None else t_rp) == t_el
        later += t_lg > t_el
        extension.append(t_lg - t_el)
        in_v23 = logged & drawn & (times < t_lg)
        analysed += int(in_v23.sum())
        outside += int((in_v23 & (times >= t_el)).sum())
    rc193[f'high_bound_omitted_share={f}'] = {
        'streams': H, 'v23_close_later_than_eligible_close': round(later / H, 4),
        'mean_extension_candidates': round(float(np.mean(extension)), 2),
        'analysed_registrations_at_or_after_eligible_close': round(outside / analysed, 4),
        'replayed_close_equals_eligible_close': round(replay_equal / H, 4)}
out['4306919946 RC-193'] = rc193

# ================= 4306919953 (RC-195): cluster records of an audited omission =================
# 17 v23 draws an omission by its own item id and enters a drawn omission as a missing cluster. An omitted member of a
# multi-member outcome cluster has no frozen cluster record: its draw keyed by item id can differ from the draw of its
# cluster, which section 6 draws whole by the cluster id, and as a separate missing cluster it carries no maturity and
# no calendar block, while the honest cluster's maturity is the latest member horizon. Remedy: the committed
# enumerator derives the complete cluster records (membership, maturity, block) from the anchored snapshot, the audit
# re-derives them, and an omitted member enters its derived cluster, drawn by that cluster's id.
def draw(s_b, key, pi):
    return int.from_bytes(hashlib.sha256(s_b + key.encode()).digest(), 'big') < int(pi * 2 ** 256)

clusters = {f'k{j:03d}': [f'src-A/{2 * j:04d}', f'src-A/{2 * j + 1:04d}'] for j in range(100)}   # two members each
omitted = {c for j, (k, ms) in enumerate(clusters.items()) if j % 2 == 0 for c in ms[1:]}         # second member of every other cluster
v_b = hashlib.sha256(b'fixture beacon round published after the anchor of batch b').digest()
batch = json.dumps(sorted(c for ms in clusters.values() for c in ms if c not in omitted), separators=(',', ':')).encode()
s_b = hashlib.sha256(batch + v_b).digest()
disagree = sum(draw(s_b, m, 0.5) != draw(s_b, k, 0.5) for k, ms in clusters.items() for m in ms if m in omitted)
# Maturity: member horizons in months, quarterly blocks [0, 3), [3, 6), ...; logged member at 5, omitted member at 9.
H_logged, H_omitted = 5, 9
rc195 = {
    'clusters': len(clusters), 'omitted_members': len(omitted),
    'omitted_member_draw_by_item_id_differs_from_its_cluster_draw': disagree,
    'maturity_fixture': {'honest_cluster_maturity': max(H_logged, H_omitted), 'honest_block': max(H_logged, H_omitted) // 3,
                         'v23_logged_cluster_maturity': H_logged, 'v23_logged_cluster_block': H_logged // 3,
                         'v23_missing_cluster_maturity': None},
    'cluster_increment_fixture': {'members': {'a_logged': 0.4, 'b_omitted': -0.2},
                                  'honest_clusters': 1, 'honest_increment': round((0.4 - 0.2) / 2, 3),
                                  'v23_clusters': 2, 'v23_increments': [0.4, 'missing (box)']},
}
out['4306919953 RC-195'] = rc195

# ================= 4306919961 (RC-197): a demotion between the steps of the four-step protocol =================
# Toy model of 17 v23 section 3 item 5: (1) intent checks the capability's epoch; (2) anchor the intent; (3) commit
# record; (4) anchor the commit, after which the change takes effect. A demotion rotates the epoch and sets the gate
# to the floor in its own writer transaction, and may run in any gap. Invariant: after a demotion that follows the
# intent's epoch check, the gate is at the floor, live and on replay, and live state equals replay state.
def run(demote_at, remedy):
    ledger, live = [], {'epoch': 1, 'gate': 'floor'}
    def demote():
        ledger.append(('demote',))
        live['epoch'] += 1
        live['gate'] = 'floor'
    steps = ['intent', 'anchor_intent', 'commit', 'anchor_commit']
    intent_epoch = None
    aborted = False
    for i, step in enumerate(steps):
        if demote_at == i:
            demote()
        if step == 'intent':
            if live['epoch'] != 1:                       # capability signed for epoch 1
                return {'outcome': 'rejected_stale_epoch_at_intent'}
            intent_epoch = live['epoch']
            ledger.append(('intent',))
        elif step == 'commit':
            demoted_since = any(r == ('demote',) for r in ledger[ledger.index(('intent',)):])
            if remedy and (live['epoch'] != intent_epoch or demoted_since):
                ledger.append(('abort',))
                aborted = True
            else:
                ledger.append(('commit',))
        elif step == 'anchor_commit' and not aborted:
            if remedy:                                   # effect at the commit's ledger position
                live['gate'] = replay(ledger)
            else:                                        # effect at confirmation time
                live['gate'] = 'promoted'
    if demote_at == len(steps):
        demote()
    return {'live_gate': live['gate'], 'replay_gate': replay(ledger), 'ledger': [r[0] for r in ledger]}

def replay(ledger):
    gate = 'floor'
    for rec in ledger:
        gate = 'promoted' if rec == ('commit',) else 'floor' if rec == ('demote',) else gate
    return gate

labels = {None: 'no_demotion', 0: 'before_step_1', 1: 'gap_1_2', 2: 'gap_2_3', 3: 'gap_3_4', 4: 'after_step_4'}
rc197 = {}
for remedy in (False, True):
    rows, violations = {}, 0
    for at, name in labels.items():
        r = run(at, remedy)
        if 'live_gate' in r and at not in (None,):
            bad = r['live_gate'] != 'floor' or r['replay_gate'] != 'floor'
            violations += bad
            r['violates_invariant'] = bad
        rows[name] = r
    rows['violations'] = violations
    rc197['remedy_epoch_recheck_and_ledger_order' if remedy else 'v23'] = rows
out['4306919961 RC-197'] = rc197

print(json.dumps(out, indent=1))
