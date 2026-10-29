from datetime import datetime,timezone,timedelta
import hashlib
import pytest
from cpe.core import Evidence, BinaryThesis, robust_binary_allocation, ChallengerEvidence, coherent_binary_probs
from cpe.ledger import AppendOnlyLedger
from cpe.saxo_sim import SaxoInstrument, build_precheck_payload, SIM_API

NOW=datetime(2026,10,16,tzinfo=timezone.utc)

def thesis(low=.10, high=.15, up=10., down=.2):
 return BinaryThesis('X', NOW+timedelta(days=3650), 'Defined binary return at 2036 date', low, high, up, down, ('e1',), 'test1')

def test_success_threshold():
 # 10x upside / 0.2x downside: required probability > 4/49 (= 8.163%) for positive arithmetic EV.
 low=robust_binary_allocation(thesis(.06,.20),forecast_at=NOW)
 assert low.max_portfolio_fraction == 0
 high=robust_binary_allocation(thesis(.10,.20),forecast_at=NOW)
 assert high.max_portfolio_fraction == pytest.approx(.025)
 assert high.robust_log_growth_before_fixed_costs > 0

def test_clamped_risk():
 result=robust_binary_allocation(thesis(.20,.30),forecast_at=NOW,max_fraction=.015)
 assert result.max_portfolio_fraction == pytest.approx(.015)

def test_fixed_cost_reject():
 r=robust_binary_allocation(thesis(.10,.15),forecast_at=NOW,fixed_cost_fraction_of_portfolio=.01)
 assert r.max_portfolio_fraction == 0

def test_incoherent_probability_rejected():
 with pytest.raises(ValueError):robust_binary_allocation(thesis(.8,.2),forecast_at=NOW)
 assert not coherent_binary_probs(.8,.4)
 assert coherent_binary_probs(.8,.2)

def test_no_future_evidence():
 h=hashlib.sha256(b'test').hexdigest()
 e=Evidence('E1','https://example.org/document',h,NOW,NOW,NOW+timedelta(seconds=1),'Test')
 with pytest.raises(ValueError,match='LOOKAHEAD'):
  e.verify_as_of(NOW)
 e.verify_as_of(NOW+timedelta(seconds=2))

def test_eprocess_proper_and_bounded():
 with pytest.warns(DeprecationWarning):
  e=ChallengerEvidence(.5)
 for outcome in [1,1,1,1]:
  e.update(.5,.9,outcome)
 assert e.evalue > 1
 with pytest.raises(ValueError):e.update(.5,1.2,1)

def test_ledger_and_detection(tmp_path):
 f=tmp_path/'events.jsonl'
 x=AppendOnlyLedger(f)
 x.append('screened',{'ticker':'SYNTHETIC','selected':False})
 x.append('forecast',{'p':.3})
 assert x.verify_chain()
 f.write_text(f.read_text().replace('SYNTHETIC','FAKED'))
 assert not x.verify_chain()

def test_saxo_sim_never_executes():
 # v0.2: tradability must come from reference-data readback; certificate id is mandatory;
 # ManualOrder is NOT part of the documented precheck request and is no longer sent.
 payload,headers=build_precheck_payload(SaxoInstrument(123,'Stock','fake-sim-key',tradable=True),3,limit_price=9.9,certificate_id='PCCB-TEST')
 assert 'ManualOrder' not in payload
 assert payload['OrderType']=='Limit'
 assert '/sim/' in SIM_API
 assert payload['FieldGroups']==['Costs','MarginImpactBuySell']
 assert 'x-request-id' in headers

from cpe.coherence import ProbabilityInterval, coherent_joint, event_probability_bounds

def test_joint_coherence_detects_logical_contradiction():
    # If A implies B, P(A) must not exceed P(B).
    impossible=coherent_joint({'A':ProbabilityInterval(.4,.5), 'B':ProbabilityInterval(.1,.2)},
                               implications=(('A','B'),))
    assert impossible is None

def test_joint_coherence_projected():
    bounds={'A':ProbabilityInterval(.2,.3), 'B':ProbabilityInterval(.4,.5)}
    joint=coherent_joint(bounds, implications=(('A','B'),))
    assert joint is not None
    assert joint.verify(bounds)
    assert joint.marginal('A') <= joint.marginal('B')
    lo,hi=event_probability_bounds(bounds,'A',implications=(('A','B'),))
    assert lo==pytest.approx(.2, abs=1e-6)
    assert hi==pytest.approx(.3, abs=1e-6)


def test_three_event_chain_bounds():
    # E => D => C; no independence multiplication permitted.
    bounds={'E':ProbabilityInterval(.05,.1), 'D':ProbabilityInterval(.2,.4),'C':ProbabilityInterval(.5,.7)}
    joint=coherent_joint(bounds,(('E','D'),('D','C')))
    assert joint is not None
    assert joint.marginal('E') <= joint.marginal('D') <= joint.marginal('C')
