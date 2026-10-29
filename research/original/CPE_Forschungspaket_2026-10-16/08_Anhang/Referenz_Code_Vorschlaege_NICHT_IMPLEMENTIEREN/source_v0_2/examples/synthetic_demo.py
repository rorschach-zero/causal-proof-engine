"""Run with: python -m examples.synthetic_demo. SYNTHETIC DATA ONLY."""
from datetime import datetime, timezone
from cpe.core import BinaryThesis, robust_binary_allocation, ChallengerEvidence

now = datetime(2026, 10, 16, 6, 0, tzinfo=timezone.utc)
thesis = BinaryThesis(
    hypothesis_id='DEMO-100X-001',
    success_horizon=datetime(2036,10,16,tzinfo=timezone.utc),
    success_definition='Synthetic asset pays 10x or 0.2x in 10 years',
    p_success_low=.10, p_success_high=.15,
    upside_multiple=10.0, downside_multiple=.2,
    evidence_ids=('synthetic-evidence-only',), forecaster_version='demo-v0'
)
cert = robust_binary_allocation(thesis,forecast_at=now,max_fraction=.05)
print('SYNTHETIC allocation certificate:',cert)
monitor = ChallengerEvidence(betting_fraction=.5)
for label in [1,1,0,1,0,1,1,0,1,1]:
    monitor.update(.5,.7,label)
print('SYNTHETIC e-value vs baseline:',round(monitor.evalue,3), 'N:',monitor.n)
print('NOT investment advice: synthetic assumptions, unvalidated probabilities, no Saxo orders sent.')
