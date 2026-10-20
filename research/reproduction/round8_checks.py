"""Round-8 checks for the Codex findings on PR #4 at 37ac018 (no reference code, no network).

RC-85: the version-5 VOID cutoff depends on t*_k, which an all-VOID cluster never has; a toy closure state machine
shows which VOID declarations each rule admits, and a Monte Carlo shows what outcome-dependent removal inside the
VOID cap does to the primary test under the null. RC-86: T-15 has refusal cases only; a deterministic as-of oracle
table and four defective readers show which oracle each reader fails. The cluster-weighted statistic is that of
16 Appendix F; the two-point null generator is that of Appendix D/E.
"""
import json, math, sys
import numpy as np
from scipy.stats import t as student_t

out = {}
ALPHA = 0.05

def cluster_weighted_t(x, n_blocks, w=None):
    """theta = mean over clusters; variance = block-sum (cluster-robust) form over n_blocks calendar blocks, G/(G-1)
    factor, G-1 df (17 section 3 item 3, RC-69). x has shape (reps, clusters) in calendar order; clusters are
    assigned to blocks round-robin by position. w is an optional 0/1 mask of the clusters that remain (a removed
    cluster keeps its calendar position and contributes nothing)."""
    reps, n = x.shape
    if w is None:
        w = np.ones_like(x)
    n_eff = w.sum(axis=1)
    theta = (w * x).sum(axis=1) / n_eff
    dev = w * (x - theta[:, None])
    blocks = np.arange(n) % n_blocks
    bs = np.stack([dev[:, blocks == b].sum(axis=1) for b in range(n_blocks)], axis=1)
    v = (bs ** 2).sum(axis=1) / n_eff ** 2 * n_blocks / (n_blocks - 1)
    return theta, theta / np.sqrt(v)

# ================= r4301920287 (RC-85), part (a): toy closure state machine =================
# One cluster of two members. Freeze instant t_freeze = earliest not_before = 5 (the RC-29 instant at which membership
# is immutable). Deadline D = 40, declared latency window L = 10, so logical finality (RC-77) is at 50. Each member's
# outcome is publicly determinable at its publication time k_i and the registry receives the source's record at r_i.
# Both arms' forecasts were received at t = 1 (issuance window [0, 4]).
#
# Rule v5 (17 version 5): a VOID declaration is accepted when received; "a pre-declared VOID has no outcome and no
# knowable_at", so the member's record is not adjudicated; at closure a VOID received at or after t*_k is refused and
# the member is scored from its record, where t*_k = min over RESOLVED members of min(receipt, knowable_at). With no
# resolved member t*_k does not exist and nothing is refused.
# Rule v6 (proposed): the VOID set is frozen with the membership at t_freeze; after t_freeze a VOID request changes no
# state (it is logged in the VOID audit); every record received is adjudicated and an outcome always wins; at finality
# with no record the pre-registered source rule decides NO (eventually-by-deadline predicate, source alive) or an
# adjudicated, outcome-dependent VOID (source failed); adjudicated VOIDs count against the cap and are imputed in the
# worst-case bounds; a cluster is all-VOID only by the freeze or by the source rule at finality, never by declaration.
T_FREEZE, FINALITY = 5, 50

def run(rule, void_requests, records, source_failed):
    """void_requests: {member: time}; records: {member: (publication_time, receipt_time)}."""
    state = {m: 'open' for m in (1, 2)}
    knowable = {}
    audit = []
    events = sorted([(t, 'void', m) for m, t in void_requests.items()] +
                    [(r, 'record', m) for m, (k, r) in records.items()] + [(FINALITY, 'finality', None)])
    for t, kind, m in events:
        if kind == 'void':
            if rule == 'v5':
                state[m] = 'void_declared'; audit.append(f'{t}: VOID member {m} accepted')
            else:
                if t < T_FREEZE:
                    state[m] = 'void_predeclared'; audit.append(f'{t}: VOID member {m} pre-declared (before freeze)')
                else:
                    audit.append(f'{t}: VOID request member {m} after freeze: logged, no state change')
        elif kind == 'record':
            k, r = records[m]
            if rule == 'v5' and state[m] == 'void_declared':
                audit.append(f'{t}: record for VOID member {m} not adjudicated (no knowable_at)')
            elif state[m] == 'void_predeclared':
                audit.append(f'{t}: record for pre-declared VOID member {m} ignored')
            else:
                state[m] = 'scored'; knowable[m] = min(k, r); audit.append(f'{t}: member {m} scored, knowable_at {k}')
        else:
            for mm in (1, 2):
                if state[mm] == 'open':
                    if rule == 'v6':
                        state[mm] = 'void_adjudicated' if source_failed else 'scored_NO_by_finality'
                        audit.append(f'{t}: member {mm} {state[mm]} by source rule')
                    else:
                        state[mm] = 'pending'
    if rule == 'v5':
        resolved_times = [min(records[mm]) for mm in (1, 2) if state[mm] == 'scored']
        t_star = min(resolved_times) if resolved_times else None
        for mm in (1, 2):
            if state[mm] == 'void_declared':
                if t_star is not None and void_requests[mm] >= t_star:
                    state[mm] = 'scored'; audit.append(f'closure: VOID member {mm} at {void_requests[mm]} >= t*_k {t_star}: refused, scored')
                else:
                    audit.append(f'closure: VOID member {mm} stands (t*_k {"undefined" if t_star is None else t_star})')
    scored = [mm for mm in (1, 2) if state[mm].startswith('scored')]
    voids = [mm for mm in (1, 2) if state[mm].startswith('void')]
    return {'end_state': state, 'increment_emitted': len(scored) > 0 and len(scored) + len(voids) == 2,
            'members_in_increment': scored, 'void_members_against_cap': voids,
            'imputed_in_worst_case_bounds': voids if rule == 'v6' else 'unspecified for an all-VOID cluster in v5',
            'audit': audit}

scenarios = {
    'S1_pre_freeze_void_both': dict(void_requests={1: 3, 2: 4}, records={1: (10, 30), 2: (12, 32)}, source_failed=False),
    'S2_void_both_after_publication_before_receipt': dict(void_requests={1: 11, 2: 13}, records={1: (10, 30), 2: (12, 32)}, source_failed=False),
    'S3_void_one_after_publication_sibling_resolves': dict(void_requests={2: 13}, records={1: (10, 30), 2: (12, 32)}, source_failed=False),
    'S4_source_failed_no_records': dict(void_requests={1: 20, 2: 21}, records={}, source_failed=True),
    'S5_source_failed_one_record': dict(void_requests={2: 21}, records={1: (10, 30)}, source_failed=True),
    'S6_no_void_no_record_source_alive': dict(void_requests={}, records={}, source_failed=False),
}
rc85a = {}
for name, sc in scenarios.items():
    rc85a[name] = {'v5': run('v5', **sc), 'v6': run('v6', **sc)}
rc85a['reading'] = ('S2 is Codex\'s channel: under v5 both post-publication VOIDs stand because no member is resolved and t*_k '
                    'is undefined, and the cluster leaves the point estimate; under v6 both records are adjudicated and the '
                    'cluster is scored. S3 shows v5 refusing the same VOID when a sibling resolves, so the gap is exactly the '
                    'all-VOID case. S4 and S5 show the legitimate all-VOID and partial-VOID routes under v6 (source rule at '
                    'finality), both outcome-dependent, both against the cap and in the bounds.')
out['RC85a_closure_state_machine'] = rc85a

# ================= r4301920287 (RC-85), part (b): what removal inside the cap does to the primary =================
# Valid null, independent clusters, 24 calendar blocks, 20,000 replications. Generator of Appendix D/E: q = 0.5,
# X = 0.4 Y - 0.2 in {-0.2, +0.2} (baseline 0.4, challenger 0.6), and a continuous variant: p_true ~ U(0.05, 0.95),
# both arms p_true + N(0, 0.1) clipped to [0.01, 0.99] (equal skill, so E[X] = 0), Y ~ Bernoulli(p_true).
# An adversary who sees the outcomes declares the q N clusters with the most negative increments VOID, q = cap. The
# primary is recomputed over the remaining clusters; the worst-case lower bound re-imputes every removed cluster with
# the outcome least favourable to FULL. Reported: rejection rate of the primary, mean shift, and how often the lower
# bound still rejects.
REPS, BLOCKS = 20000, 24
rng = np.random.default_rng(8501)
crit = float(student_t.ppf(1 - ALPHA, BLOCKS - 1))

def two_point(n):
    y = (rng.random((REPS, n)) < 0.5).astype(float)
    return 0.4 * y - 0.2, np.full((REPS, n), 0.4), np.full((REPS, n), 0.6)

def continuous(n):
    p = rng.uniform(0.05, 0.95, size=(REPS, n))
    pc = np.clip(p + rng.normal(0, 0.1, size=(REPS, n)), 0.01, 0.99)
    pf = np.clip(p + rng.normal(0, 0.1, size=(REPS, n)), 0.01, 0.99)
    y = (rng.random((REPS, n)) < p).astype(float)
    return (pc - y) ** 2 - (pf - y) ** 2, pc, pf

rc85b = {'design': f'{REPS} replications, {BLOCKS} blocks, one-sided alpha {ALPHA}, t critical {crit:.4f} on {BLOCKS - 1} df; '
                   'removal = the q N most negative cluster increments declared VOID after the outcomes are known'}
for gname, gen in (('two_point_null', two_point), ('continuous_null', continuous)):
    for n in (300, 600):
        x, pc, pf = gen(n)
        rank = np.argsort(np.argsort(x, axis=1), axis=1)   # rank 0 = most negative increment, per replication
        res = {}
        for q in (0.0, 0.02, 0.05, 0.10):
            k = int(round(q * n))
            keep = (rank >= k).astype(float)                 # clusters stay at their calendar position
            theta, tt = cluster_weighted_t(x, BLOCKS, keep)
            entry = {'removed': k, 'primary_rejection_rate': round(float((tt > crit).mean()), 4),
                     'mean_of_point_estimate': round(float(theta.mean()), 5)}
            if k > 0:
                # least favourable to FULL: Y = 1 where p_FULL < p_baseline, else Y = 0 (17 section 6, Missing data)
                y_lf = (pf < pc).astype(float)
                x_lf = (pc - y_lf) ** 2 - (pf - y_lf) ** 2
                x_lower = np.where(keep > 0, x, x_lf)
                th_l, t_l = cluster_weighted_t(x_lower, BLOCKS)
                entry['worst_case_lower_bound_rejection_rate'] = round(float((t_l > crit).mean()), 4)
                entry['mean_of_lower_bound_estimate'] = round(float(th_l.mean()), 5)
            res[f'cap={q}'] = entry
        rc85b[f'{gname},clusters={n}'] = res
rc85b['reading'] = ('The cap bounds how many clusters leave, not the bias. With no removal the primary holds 5 % on both nulls; '
                    'removing the 2 % least favourable clusters gives 10-13 % (two-point) and 31-47 % (continuous), 5 % gives '
                    '23-34 % and 77-95 %, 10 % gives 56-81 % and 99-100 %, while the worst-case lower bound stays at 5 % '
                    'throughout. The point estimate, not the bound, is what the primary tests, so the removal decision must be '
                    'outcome-independent (frozen) or adjudicated by the source rule, never declared.')
out['RC85b_selective_void_under_null'] = rc85b

# ================= r4301920289 (RC-86): positive as-of oracles for T-15 =================
# Fixture F-25: one entity, one feature, five rows (observed_at, available_at, vintage, value).
F25 = [(10, 12, 'v1', 1.00),   # first release of the period-10 observation
       (10, 20, 'v2', 1.50),   # revision of it
       (5, 25, 'v3', 0.70),    # backfilled earlier period, inserted after later data exist
       (30, 40, 'v4', 2.00),   # publication-lagged observation
       (10, 50, 'v6', 1.40)]   # second revision of period 10
CUTS = (11, 12, 19, 20, 24, 25, 39, 40, 49, 50)

def oracle(t_cut):
    """Point-in-time truth: for every observed_at with a row available at or before t_cut, the row with the greatest
    available_at <= t_cut (the latest vintage an agent at t_cut could have read); 'latest' = greatest observed_at."""
    series = {}
    for obs, avail, vin, val in F25:
        if avail <= t_cut and (obs not in series or avail > series[obs][0]):
            series[obs] = (avail, vin, val)
    return {obs: (vin, val) for obs, (avail, vin, val) in sorted(series.items())}

def reader_reference(t_cut):
    return oracle(t_cut)
def reader_refuse_all(t_cut):
    raise PermissionError('refused')
def reader_oldest_eligible(t_cut):
    series = {}
    for obs, avail, vin, val in F25:
        if avail <= t_cut and (obs not in series or avail < series[obs][0]):
            series[obs] = (avail, vin, val)
    return {obs: (vin, val) for obs, (avail, vin, val) in sorted(series.items())}
def reader_filters_on_observed_at(t_cut):
    series = {}
    for obs, avail, vin, val in F25:
        if obs <= t_cut and (obs not in series or avail > series[obs][0]):
            series[obs] = (avail, vin, val)
    return {obs: (vin, val) for obs, (avail, vin, val) in sorted(series.items())}
def reader_latest_regardless(t_cut):
    series = {}
    for obs, avail, vin, val in F25:
        if obs not in series or avail > series[obs][0]:
            series[obs] = (avail, vin, val)
    return {obs: (vin, val) for obs, (avail, vin, val) in sorted(series.items())}

def row_refused(reader, t_cut):
    """The four refusal cases of T-15 (a)-(d): a read of a specific row with available_at > t_cut must be refused.
    A reader passes if it never returns a row with available_at > t_cut."""
    try:
        got = reader(t_cut)
    except PermissionError:
        return True
    avail_of = {(obs, vin): avail for obs, avail, vin, val in F25}
    return all(avail_of[(obs, vin)] <= t_cut for obs, (vin, val) in got.items())

readers = {'reference': reader_reference, 'refuse_all': reader_refuse_all, 'oldest_eligible_vintage': reader_oldest_eligible,
           'filters_on_observed_at': reader_filters_on_observed_at, 'latest_regardless_of_cutoff': reader_latest_regardless}
oracle_table = {f't_cut={c}': {str(k): list(v) for k, v in oracle(c).items()} for c in CUTS}
rc86 = {'fixture_F25': [list(r) for r in F25], 'oracle': oracle_table, 'readers': {}}
for name, rd in readers.items():
    pos_fail, ref_fail = [], []
    for c in CUTS:
        try:
            got = rd(c)
        except PermissionError:
            got = 'refused'
        if got != oracle(c):
            pos_fail.append(c)
        if not row_refused(rd, c):
            ref_fail.append(c)
    rc86['readers'][name] = {'passes_refusal_cases': not ref_fail, 'refusal_failures_at': ref_fail,
                             'passes_positive_oracles': not pos_fail, 'positive_oracle_failures_at': pos_fail}
rc86['reading'] = ('refuse_all and oldest_eligible_vintage pass every refusal case of T-15 as written and fail the positive '
                   'oracles; filters_on_observed_at is the classic leak (it returns v6 at t_cut = 11) and fails both; only '
                   'the reference reader passes both, so T-15 needs the oracle table beside the refusals.')
out['RC86_as_of_positive_oracles'] = rc86

out['python'] = sys.version.split()[0]
json.dump(out, sys.stdout, indent=2)
print()
