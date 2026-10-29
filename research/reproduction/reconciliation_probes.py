"""Reconciliation probes for research/16-reconciliation-matrix.md (round 1, re-run in round 2).

Runs against a scratch copy of the archived v0.2 reference code (path = argv[1]).
No network, no credentials. Reproduces the counterexamples the reconciliation
matrix relies on and evaluates the two proposed remedies (cluster-level betting,
second-moment simplex pooling). Written for the matrix independently of the
script in 15-codex-review.md Appendix 1; it does not import or copy it.
"""
import json, math, sys, tempfile, warnings
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.optimize import minimize
from scipy.stats import beta

sys.path.insert(0, sys.argv[1])
from cpe.ledger import AppendOnlyLedger, _canonical
from cpe.registry import EventSpec, Forecast, ForecastRegistry, Forecaster
from cpe.fusion import ModelInterval, JevTriage, fuse, error_correlation, min_variance_weights
from cpe.eprocess import CommittedEProcess, CommittedForecastPair, grapa_lambda
from cpe.saxo_sim import Gate, GateState, OwnerAuthorization

out = {}
T0 = datetime(2020, 1, 1, tzinfo=timezone.utc)

def spec(eid):
    return EventSpec(eid, 'Revenue exceeds threshold by expiry', 'audited filing',
                     'revenue > 100', T0 + timedelta(days=1), T0 + timedelta(days=30), 'v1')

# ---- RC-02, RC-11, RC-12, RC-13: registry and ledger ----
with tempfile.TemporaryDirectory() as d:
    ledger = AppendOnlyLedger(Path(d) / 'ledger.jsonl')
    reg = ForecastRegistry(ledger)
    reg.register_event(spec('late'))
    reg.resolve('late', True, T0 + timedelta(days=40), 'audit', 'ev-late')
    out['RC11_late_yes_status'] = reg.status('late').value
    out['RC12_restart_knows_events'] = len(ForecastRegistry(ledger)._events)
    reg.register_event(spec('backdated'))
    reg.commit_forecast(Forecast('f1', 'backdated', Forecaster.CLAUDE, 'v', 0.4, 0.6,
                                 T0, T0, ('e',), 'z' * 64))
    out['RC02_backdated_2020_forecast_accepted_today'] = True
    reg.register_event(spec('early'))
    reg.resolve('early', False, T0 + timedelta(days=2), 'audit', 'ev-early')
    out['RC11_early_no_before_deadline_status'] = reg.status('early').value
    with patch.object(ledger, 'append', side_effect=OSError('injected')):
        try:
            reg.register_event(spec('phantom'))
        except OSError:
            pass
    out['RC12_phantom_event_after_failed_append'] = 'phantom' in reg._events
    anchor = ledger.anchor()
    ledger.append('forecast', {'p': 0.1})
    rows = [json.loads(line) for line in ledger.path.read_text().splitlines()]
    rows[-1]['payload']['p'] = 0.99
    rows[-1].pop('entry_hash')
    rows[-1]['entry_hash'] = sha256(_canonical(rows[-1])).hexdigest()
    ledger.path.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    out['RC13_rehashed_unanchored_suffix_verifies'] = ledger.verify_against_anchor(anchor)

# ---- RC-12: gate replay ----
g = Gate(); key = b'synthetic-owner-key'
auth = OwnerAuthorization(GateState.RESEARCH_ONLY, GateState.SIM_READ_ONLY, 'bundle',
                          Gate.expected_mac(key, GateState.RESEARCH_ONLY, GateState.SIM_READ_ONLY, 'bundle'))
g.promote(auth, key); g.demote('kill'); g.promote(auth, key)
out['RC12_state_after_replaying_old_authorization'] = g.state.value

# ---- RC-03, RC-04 arithmetic ----
out['RC03_floor_rule_on_[0.001,0.01]_base_0.02'] = [max(0.001, 0.02), 0.01]
out['RC04_nested_chain_product'] = (0.01 / 0.1) * (0.1 / 0.5) * 0.5

# ---- RC-06, RC-07: fusion weights ----
z = np.tile(np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1.]]), (10, 1))
errors_p4 = z * np.array([0.02, 0.30, 0.30])
w_corr, _ = min_variance_weights(error_correlation(errors_p4, 0.3))
out['RC06_correlation_weights_P4'] = [round(x, 4) for x in w_corr]

def second_moment_simplex(errors, shrink=0.1):
    """Minimise w'Sw on the simplex, S = shrunk uncentred second moment of past errors."""
    m = errors.T @ errors / len(errors)
    s = (1 - shrink) * m + shrink * np.diag(np.diag(m))
    k = errors.shape[1]
    res = minimize(lambda w: w @ s @ w, np.ones(k) / k, method='SLSQP',
                   bounds=[(0, 1)] * k, constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1}])
    return res.x

out['RC06_second_moment_weights_P4'] = [round(x, 3) for x in second_moment_simplex(errors_p4)]
rng = np.random.default_rng(1)
bias_fixture = np.column_stack([np.full(40, 0.20) + 0.01 * rng.standard_normal(40),
                                0.05 * rng.standard_normal(40), 0.05 * rng.standard_normal(40)])
cov = np.cov(bias_fixture, rowvar=False)
v = np.linalg.solve(cov, np.ones(3))
out['RC06_covariance_only_weights_bias_fixture'] = [round(x, 3) for x in v / v.sum()]
out['RC06_second_moment_weights_bias_fixture'] = [round(x, 3) for x in second_moment_simplex(bias_fixture)]

names = ['claude', 'openai', 'gemini']; jev = JevTriage(0.9, 0.9, 0.0)
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    out['RC07_neff_constant_duplicate_histories'] = fuse([ModelInterval(n, .4, .6) for n in names], jev, np.ones((20, 3))).effective_models
out['RC07_neff_identical_varying_histories'] = round(fuse([ModelInterval(n, .4, .6) for n in names], jev, np.tile(np.arange(20.)[:, None], (1, 3))).effective_models, 4)
out['RC07_neff_closed_form_3/(3-2*0.3)'] = round(3 / (3 - 0.6), 4)
for tag, lo, hi in [('nan', float('nan'), float('nan')), ('reversed', .8, .2), ('over_one', 1.2, 1.3)]:
    out['RC15_fusion_accepts_' + tag] = fuse([ModelInterval(n, lo, hi) for n in names], jev, None).decision.value

# ---- RC-01: e-process cloned outcomes ----
def run_path(xs):
    ep = CommittedEProcess()
    for i, x in enumerate(xs):
        ep.commit(CommittedForecastPair(str(i), .25, .75, T0, T0 + timedelta(days=1)))
        ep.resolve(str(i), int(x > 0), T0 + timedelta(days=2))
    return ep
plus = run_path([.5] * 30); minus = run_path([-.5] * 30)
out['RC01_cloned_30_outcomes'] = {'e_if_shared_outcome_is_1': round(plus.evalue, 4),
                                  'e_if_shared_outcome_is_0': round(minus.evalue, 4),
                                  'crossing_probability_under_fair_shared_outcome': 0.5 * plus.reject_null(.05) + 0.5 * minus.reject_null(.05)}

# Vectorised archived GRAPA recurrence, checked against the reference on one path.
def grapa_paths(xs, lam_max=0.5, threshold=20.0, checkpoints=()):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    snaps = {}
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
        if n + 1 in checkpoints:
            snaps[n + 1] = peak.copy()
    return wealth, peak, snaps
check = np.random.default_rng(5).choice([-.5, .5], size=(1, 80))
ref = run_path(list(check[0])).evalue
vec = grapa_paths(check)[0][0]
out['RC01_vectorised_recurrence_matches_reference'] = bool(np.isclose(ref, vec, rtol=1e-12))

def binom_upper(k, n, conf=0.95):
    """One-sided exact (Clopper-Pearson) upper confidence bound for a binomial proportion."""
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))

# Clustered no-skill null: baseline 0.4, challenger 0.6, outcome Y~Bern(0.5) shared by every
# event in a cluster. X = (0.4-Y)^2 - (0.6-Y)^2 = +0.2 if Y=1 else -0.2. Marginal mean zero.
REPS, CLUSTERS, PER = 2000, 120, 5
rng = np.random.default_rng(2026)
y = rng.integers(0, 2, size=(REPS, CLUSTERS))
x_cluster = np.where(y == 1, 0.2, -0.2)
x_event = np.repeat(x_cluster, PER, axis=1)                  # 600 per-event increments
_, peak_event, _ = grapa_paths(x_event)
_, peak_cluster, _ = grapa_paths(x_cluster)
fa_event = float((peak_event >= 20).mean()); fa_cluster = float((peak_cluster >= 20).mean())
out['RC01_clustered_null'] = {'replications': REPS, 'clusters': CLUSTERS, 'events_per_cluster': PER,
                              'false_alarm_per_event_betting': fa_event,
                              'false_alarm_per_cluster_betting': fa_cluster,
                              'mc_upper_95_per_cluster_exact_binomial': round(binom_upper(int(round(fa_cluster * REPS)), REPS), 6)}
# Same with a shuffled (interleaved) order of events across clusters: dependence persists.
perm = rng.permutation(CLUSTERS * PER)
_, peak_shuf, _ = grapa_paths(x_event[:, perm])
out['RC01_clustered_null']['false_alarm_per_event_betting_interleaved_order'] = float((peak_shuf >= 20).mean())

# Independent power check of four rows of Codex D1 (same generator specification, seeds 17, 29, 43);
# the (0.2, 0.02) row was added in round 2 (RC-45) because 02 section 6 cited it without reproduction.
power = {}
for b, delta in [(0.5, 0.01), (0.5, 0.02), (0.2, 0.01), (0.2, 0.02)]:
    counts = {300: 0, 600: 0}
    for seed in (17, 29, 43):
        r = np.random.default_rng(seed)
        p = b + math.sqrt(delta) * r.choice([-1., 1.], size=(2000, 600))
        yy = (r.random(p.shape) < p).astype(float)
        xs = (b - yy) ** 2 - (p - yy) ** 2
        snaps = grapa_paths(xs, checkpoints=(300, 600))[2]
        for n, pk in snaps.items():
            counts[n] += int((pk >= 20).sum())
    power[f'b={b},delta={delta}'] = {'crossings_by_300_of_6000': counts[300], 'crossings_by_600_of_6000': counts[600]}
out['RC24_power_rows'] = power

# alpha-spending shape
out['RC08_alpha_spending_0.05/(j(j+1))'] = {j: round(0.05 / (j * (j + 1)), 5) for j in (1, 2, 5, 10)}
out['RC08_sum_to_infinity'] = 0.05
print(json.dumps(out, indent=2, allow_nan=False))
