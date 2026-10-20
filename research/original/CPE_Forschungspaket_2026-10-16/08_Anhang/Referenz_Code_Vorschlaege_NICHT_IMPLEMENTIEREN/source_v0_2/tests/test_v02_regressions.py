"""v0.2 regression tests. Each test is tied to a review finding (see CLAUDE_REVIEW.md IDs)."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
import random
import pytest
import numpy as np

from cpe.ledger import AppendOnlyLedger
from cpe.eprocess import CommittedEProcess, CommittedForecastPair, grapa_lambda
from cpe.core import BinaryThesis, robust_binary_allocation, Evidence, evidence_digest, growth
from cpe.coherence import ProbabilityInterval, event_probability_bounds
from cpe.registry import ForecastRegistry, EventSpec, Forecast, Forecaster, ForecastStatus
from cpe.fusion import fuse, ModelInterval, JevTriage, FusionPolicy, Decision, effective_models, min_variance_weights
from cpe.jev_adapter import JevClient, JevMalformed, parse_noul_response
from cpe.saxo_sim import Gate, GateState, OwnerAuthorization, SaxoInstrument, build_precheck_payload, sim_precheck
from cpe.allocation import robust_allocation

NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)
D = timedelta(days=1)


# ---------------------------------------------------------------- P1-LEDGER-01
def test_full_rewrite_detected_with_anchor(tmp_path):
    f = tmp_path / 'l.jsonl'
    L = AppendOnlyLedger(f)
    L.append('forecast', {'id': 'H1', 'p': 0.05})
    L.append('resolution', {'id': 'H1', 'outcome': 1})
    anchor = L.anchor(secret=b'owner-secret')
    assert L.verify_against_anchor(anchor, secret=b'owner-secret')
    # attacker rewrites p and re-hashes the whole chain (v0.1 attack F1)
    entries = [json.loads(l) for l in f.read_text().splitlines()]
    entries[0]['payload']['p'] = 0.60
    prev = 'GENESIS'; out = []
    for e in entries:
        e.pop('entry_hash'); e['prev_hash'] = prev
        e['entry_hash'] = hashlib.sha256(json.dumps(e, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        prev = e['entry_hash']; out.append(json.dumps(e, sort_keys=True, ensure_ascii=False))
    f.write_text('\n'.join(out) + '\n')
    assert L.verify_chain()                       # internal chain still consistent ...
    assert not L.verify_against_anchor(anchor, secret=b'owner-secret')   # ... but anchor catches it
    # truncation also caught
    f.write_text(out[0] + '\n')
    assert not L.verify_against_anchor(anchor, secret=b'owner-secret')
    # forged anchor caught
    bad = dict(anchor); bad['head_hash'] = prev
    assert not L.verify_against_anchor(bad, secret=b'owner-secret')


def test_ledger_seq_and_monotone_time(tmp_path):
    L = AppendOnlyLedger(tmp_path / 'l.jsonl')
    L.append('a', {}); L.append('b', {})
    lines = (tmp_path / 'l.jsonl').read_text().splitlines()
    e = json.loads(lines[1]); assert e['seq'] == 1


# ---------------------------------------------------------------- P1-EPROC-01..04
def _pair(i, pb, pc):
    return CommittedForecastPair(f'E{i}', pb, pc, NOW, NOW + D)


def test_eprocess_rejects_hindsight_and_duplicates():
    e = CommittedEProcess()
    with pytest.raises(ValueError, match='hindsight'):
        e.resolve('never-committed', 1, NOW + 2 * D)
    e.commit(_pair(1, 0.5, 0.9))
    with pytest.raises(ValueError, match='immutable'):
        e.commit(_pair(1, 0.5, 0.99))          # cannot overwrite a committed forecast
    with pytest.raises(ValueError, match='before the declared'):
        e.resolve('E1', 1, NOW)                 # resolution inside commit window
    e.resolve('E1', 1, NOW + 2 * D)
    with pytest.raises(ValueError, match='duplicate'):
        e.resolve('E1', 1, NOW + 2 * D)


def test_eprocess_no_absorbing_zero():
    with pytest.raises(ValueError):
        CommittedEProcess(lam_max=1.0)


def test_eprocess_false_alarm_rate_under_null():
    """Under H0 (challenger == baseline in distribution), P(sup M >= 1/alpha) <= alpha.
    Monte Carlo with a fixed seed; margin accounts for MC error (binomial sd ~0.5%)."""
    rng = random.Random(7)
    alpha, runs, n = 0.05, 1500, 60
    alarms = 0
    for r in range(runs):
        e = CommittedEProcess()
        for i in range(n):
            # both forecasters are equally (mis)calibrated noisy versions of truth p
            p = rng.random()
            pb = min(1, max(0, p + rng.gauss(0, 0.2)))
            pc = min(1, max(0, p + rng.gauss(0, 0.2)))
            e.commit(_pair(i, pb, pc))
            e.resolve(f'E{i}', int(rng.random() < p), NOW + 2 * D)
        alarms += e.reject_null(alpha)
    assert alarms / runs <= alpha + 0.015


def test_eprocess_has_power_when_challenger_better():
    rng = random.Random(3)
    e = CommittedEProcess()
    for i in range(300):
        p = rng.random()
        e.commit(_pair(i, 0.5, p))           # baseline uninformative, challenger = truth
        e.resolve(f'E{i}', int(rng.random() < p), NOW + 2 * D)
    assert e.reject_null(0.05)


def test_grapa_lambda_predictable_and_bounded():
    assert grapa_lambda([]) == 0.0
    assert 0 <= grapa_lambda([0.1, 0.2, -0.05] * 10, lam_max=0.5) <= 0.5


# ---------------------------------------------------------------- P2-CORE-01 cost units
def test_fixed_cost_uses_log_units():
    th = BinaryThesis('X', NOW + 3650 * D, 'def', 0.10, 0.15, 10.0, 0.2, ('e1',), 'v')
    g = growth(0.025, 0.10, 10.0, 0.2)       # ~0.00211
    # cost fraction c with -log(1-c) just below g must still allow the bet
    c = 1 - np.exp(-(g - 1e-5))
    assert robust_binary_allocation(th, forecast_at=NOW, fixed_cost_fraction_of_portfolio=c).max_portfolio_fraction > 0
    c = 1 - np.exp(-(g + 1e-5))
    assert robust_binary_allocation(th, forecast_at=NOW, fixed_cost_fraction_of_portfolio=c).max_portfolio_fraction == 0
    with pytest.raises(ValueError):
        robust_binary_allocation(th, forecast_at=NOW, fixed_cost_fraction_of_portfolio=1.0)


# ---------------------------------------------------------------- P2-EVID-01
def test_evidence_requires_tls_and_digest_helper():
    h = evidence_digest(b'archived bytes')
    with pytest.raises(ValueError, match='TLS'):
        Evidence('E', 'http://example.org/x', h, NOW, NOW, NOW, 's').verify_as_of(NOW)
    Evidence('E', 'https://example.org/x', h, NOW, NOW, NOW, 's').verify_as_of(NOW)


# ---------------------------------------------------------------- P1-COH-01
def test_bounds_guard_prevents_exponential_blowup():
    with pytest.raises(ValueError, match='1-14'):
        event_probability_bounds({f'E{i}': ProbabilityInterval(0, 1) for i in range(15)}, 'E0')


# ---------------------------------------------------------------- P0-SCI-01 registry
def test_registry_rejects_vague_and_non_prospective(tmp_path):
    reg = ForecastRegistry(AppendOnlyLedger(tmp_path / 'l.jsonl'))
    with pytest.raises(ValueError, match='vague'):
        EventSpec('EV1', 'Company X has 10x potential', 'src', 'strong potential upside', NOW + 30 * D, NOW + 365 * D, 'g1').validate()
    spec = EventSpec('EV1', 'FDA grants 510(k) clearance for device D', 'FDA 510(k) database',
                     'row with K-number for applicant X and device D exists with decision date <= expires_at',
                     NOW + 30 * D, NOW + 365 * D, 'g1')
    reg.register_event(spec)
    digest = hashlib.sha256(b'reasoning').hexdigest()
    late = Forecast('F1', 'EV1', Forecaster.CLAUDE, 'fable-5.1', 0.2, 0.4, NOW + 31 * D, NOW + 31 * D, ('e1',), digest)
    with pytest.raises(ValueError, match='not prospective'):
        reg.commit_forecast(late)
    wide = Forecast('F1', 'EV1', Forecaster.CLAUDE, 'fable-5.1', 0.1, 0.9, NOW, NOW, ('e1',), digest)
    with pytest.raises(ValueError, match='abstention'):
        reg.commit_forecast(wide)
    ok = Forecast('F1', 'EV1', Forecaster.CLAUDE, 'fable-5.1', 0.2, 0.4, NOW, NOW, ('e1',), digest)
    reg.commit_forecast(ok)
    with pytest.raises(ValueError, match='immutable'):
        reg.commit_forecast(ok)
    reg.resolve('EV1', False, NOW + 400 * D, 'fda-db-check-v1', 'ev-res-1')
    assert reg.status('EV1') == ForecastStatus.EXPIRED_NO
    with pytest.raises(ValueError, match='already resolved'):
        reg.commit_forecast(Forecast('F2', 'EV1', Forecaster.GEMINI, 'argon', 0.2, 0.4, NOW, NOW, ('e1',), digest))


# ---------------------------------------------------------------- P0-ARCH-01..03 fusion
JEV_OK = JevTriage(0.9, 0.8, 0.03)


def test_fusion_requires_all_three_models_and_jev():
    ivs = [ModelInterval('claude', 0.2, 0.3), ModelInterval('openai', 0.25, 0.35)]
    r = fuse(ivs, JEV_OK, None)
    assert r.decision == Decision.RE_RESEARCH and 'gemini' in ' '.join(r.reasons)
    ivs.append(ModelInterval('gemini', 0.2, 0.3))
    assert fuse(ivs, None, None).decision == Decision.RE_RESEARCH


def test_fusion_abstains_on_disagreement_and_jev_incoherence():
    ivs = [ModelInterval('claude', 0.05, 0.10), ModelInterval('openai', 0.6, 0.7), ModelInterval('gemini', 0.2, 0.3)]
    r = fuse(ivs, JEV_OK, None)
    assert r.decision == Decision.ABSTAIN and r.disagreement > 0.3
    ivs = [ModelInterval('claude', 0.2, 0.3), ModelInterval('openai', 0.25, 0.35), ModelInterval('gemini', 0.2, 0.3)]
    assert fuse(ivs, JevTriage(0.9, 0.8, 0.30), None).decision == Decision.RE_RESEARCH
    assert fuse(ivs, JEV_OK, None).decision == Decision.FORECAST


def test_correlated_models_do_not_count_three_times():
    rng = np.random.default_rng(0)
    n = 200
    truth_err = rng.normal(0, 0.2, n)
    # claude & openai share the same error; gemini independent
    hist = np.column_stack([truth_err, truth_err + rng.normal(0, 0.01, n), rng.normal(0, 0.2, n)])
    ivs = [ModelInterval('claude', 0.2, 0.3), ModelInterval('openai', 0.2, 0.3), ModelInterval('gemini', 0.2, 0.3)]
    r = fuse(ivs, JEV_OK, hist)
    assert r.effective_models < 2.5
    assert r.weights['gemini'] > r.weights['claude']
    R = np.ones((3, 3))
    assert effective_models(np.ones(3) / 3, R) == pytest.approx(1.0)
    assert effective_models(np.ones(3) / 3, np.eye(3)) == pytest.approx(3.0)


# ---------------------------------------------------------------- P0-ARCH-02 Jev adapter
def test_jev_adapter_parses_and_rejects_malformed():
    good = {'model': 'jev-2026-09-15', 'answers': {'q': {'type': 'noul', 'noul': 0.8}, 'q_not': {'type': 'noul', 'noul': 0.25}},
            'usage': {'input_tokens': 100, 'output_tokens': 2}}
    calls = []
    def transport(url, headers, body, timeout):
        calls.append(body); return 200, good
    c = JevClient(api_key='x', transport=transport)
    r = c.ask_noul_pair('evidence text', 'Is it dated?', 'Is it undated?')
    assert r.p_yes == 0.8 and r.complement_gap == pytest.approx(0.05) and r.model_returned == 'jev-2026-09-15'
    assert set(calls[0]['questions']) == {'q', 'q_not'} and calls[0]['model'] == 'jev-latest'
    with pytest.raises(JevMalformed):
        parse_noul_response({'model': 'm', 'answers': {'q': {'type': 'noul', 'noul': 1.7}, 'q_not': {'type': 'noul', 'noul': 0.1}}}, ('q', 'q_not'))
    with pytest.raises(JevMalformed):
        parse_noul_response({'model': 'm', 'answers': {'q': {'type': 'choice'}}}, ('q', 'q_not'))
    with pytest.raises(ValueError, match='credential'):
        c.ask_noul_pair({'AccountKey': 'abc'}, 'q', 'nq')


def test_jev_adapter_retries_then_fails_closed():
    n = {'i': 0}
    def flaky(url, headers, body, timeout):
        n['i'] += 1; return 503, {}
    c = JevClient(api_key='x', transport=flaky, max_retries=1)
    with pytest.raises(RuntimeError, match='unavailable'):
        c.ask_noul_pair('s', 'q', 'nq')
    assert n['i'] == 2
    c = JevClient(api_key='x', transport=flaky, cost_ceiling_tokens=0)
    with pytest.raises(RuntimeError, match='ceiling'):
        c.ask_noul_pair('s', 'q', 'nq')


# ---------------------------------------------------------------- P0-BRKR gates
def test_gate_promotion_requires_owner_and_blocks_live():
    g = Gate(); secret = b'owner'
    mac = Gate.expected_mac(secret, GateState.RESEARCH_ONLY, GateState.SIM_READ_ONLY, 'abc')
    g.promote(OwnerAuthorization(GateState.RESEARCH_ONLY, GateState.SIM_READ_ONLY, 'abc', mac), secret)
    assert g.state == GateState.SIM_READ_ONLY
    with pytest.raises(PermissionError, match='one step'):
        mac2 = Gate.expected_mac(secret, GateState.SIM_READ_ONLY, GateState.SIM_EXECUTION, 'abc')
        g.promote(OwnerAuthorization(GateState.SIM_READ_ONLY, GateState.SIM_EXECUTION, 'abc', mac2), secret)
    with pytest.raises(PermissionError, match='invalid'):
        g.promote(OwnerAuthorization(GateState.SIM_READ_ONLY, GateState.SIM_PRECHECK, 'abc', '00' * 32), secret)
    g = Gate(GateState.SHADOW_LIVE_QUOTES)
    mac3 = Gate.expected_mac(secret, GateState.SHADOW_LIVE_QUOTES, GateState.LIVE_CAPPED_1000, 'abc')
    with pytest.raises(PermissionError, match='LIVE promotion is blocked'):
        g.promote(OwnerAuthorization(GateState.SHADOW_LIVE_QUOTES, GateState.LIVE_CAPPED_1000, 'abc', mac3), secret)
    assert g.demote('kill') == GateState.RESEARCH_ONLY


def test_precheck_payload_whitelist_and_gate(monkeypatch):
    inst = SaxoInstrument(123, 'Stock', 'k', tradable=True)
    body, headers = build_precheck_payload(inst, 3, limit_price=9.9, certificate_id='PCCB-0001')
    assert 'ManualOrder' not in body and body['ExternalReference'] == 'PCCB-0001' and 'x-request-id' in headers
    with pytest.raises(ValueError, match='not permitted'):
        build_precheck_payload(SaxoInstrument(1, 'CfdOnStock', 'k', tradable=True), 1, limit_price=1, certificate_id='c')
    with pytest.raises(ValueError, match='tradability'):
        build_precheck_payload(SaxoInstrument(1, 'Stock', 'k'), 1, limit_price=1, certificate_id='c')
    with pytest.raises(ValueError, match='whole number'):
        build_precheck_payload(inst, 0.5, limit_price=1, certificate_id='c')
    monkeypatch.setenv('SAXO_SIM_ACCESS_TOKEN', 'dummy')
    with pytest.raises(PermissionError, match='below required'):
        sim_precheck(Gate(), body, headers)   # RESEARCH_ONLY gate: no network call is made


# ---------------------------------------------------------------- P1-RISK-01 allocation
def test_robust_allocation_reduces_to_binary_kelly():
    R = np.array([[9.0], [-0.8]])                    # 10x or 0.2x
    Q = np.array([[0.10, 0.90], [0.15, 0.85]])        # credal vertices p in {0.10, 0.15}
    r = robust_allocation(R, Q, gross_cap=0.5, max_loss=0.5, kelly_fraction=1.0)
    assert r.weights[0] == pytest.approx(0.025, abs=2e-4)


def test_robust_allocation_respects_max_loss_and_caps():
    R = np.array([[2.0, 0.5], [-0.9, -0.9], [0.1, 0.1]])
    Q = np.array([[0.3, 0.3, 0.4]])
    r = robust_allocation(R, Q, gross_cap=0.3, max_loss=0.05, kelly_fraction=1.0)
    assert r.worst_scenario_loss <= 0.05 + 1e-6 and r.weights.sum() <= 0.3 + 1e-6
    with pytest.raises(ValueError):
        robust_allocation(np.array([[-1.5]]), np.array([[1.0]]))
