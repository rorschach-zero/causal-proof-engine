"""Adversarial reproduction scripts against source_v0_1. Run with: python -I attack_v01.py <path-to-source_v0_1>"""
import sys, json, time, hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from cpe.core import Evidence, BinaryThesis, robust_binary_allocation, ChallengerEvidence, growth
from cpe.ledger import AppendOnlyLedger
from cpe.coherence import ProbabilityInterval, coherent_joint, event_probability_bounds
from hashlib import sha256

NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)
print("=== F1: ledger full-rewrite attack (re-hash whole chain) ===")
tmp = Path(sys.argv[2]) / "ledger.jsonl"
tmp.parent.mkdir(parents=True, exist_ok=True)
if tmp.exists(): tmp.unlink()
L = AppendOnlyLedger(tmp)
L.append("forecast", {"id": "H1", "p": 0.05, "outcome": None})
L.append("resolution", {"id": "H1", "outcome": 1})
assert L.verify_chain()
# attacker rewrites p=0.05 -> p=0.60 and re-chains everything
entries = [json.loads(l) for l in tmp.read_text().splitlines()]
entries[0]["payload"]["p"] = 0.60
prev = "GENESIS"
out = []
for e in entries:
    e.pop("entry_hash"); e["prev_hash"] = prev
    e["entry_hash"] = sha256(json.dumps(e, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    prev = e["entry_hash"]; out.append(json.dumps(e, sort_keys=True, ensure_ascii=False))
tmp.write_text("\n".join(out) + "\n")
print("verify_chain after hindsight rewrite:", L.verify_chain(), "(True == tamper NOT detected)")

print("\n=== F2: ledger hash is computed with different separators than stored line (works, but fragile) ===")
line = tmp.read_text().splitlines()[0]
print("stored line uses ', ' separators:", ", " in line, "-> hash recomputed via canonical dumps; ok but any re-serializer must replicate exactly")

print("\n=== F3: e-process accepts hindsight-chosen forecasts (no commitment before outcome) ===")
e = ChallengerEvidence(0.5)
outcomes = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]
for y in outcomes:
    # 'challenger' probability chosen AFTER seeing outcome y: p=1 if y else 0
    e.update(0.5, float(y), y)
print("e-value with hindsight challenger after 10 trials:", round(e.evalue, 2), "reject at 0.05:", e.reject_null())
print("-> API lets the caller pass challenger_probability at resolution time; nothing enforces commit-before-resolve.")

print("\n=== F4: e-process absorbing zero with betting_fraction=1 ===")
e = ChallengerEvidence(1.0)
e.update(0.0, 1.0, 0)  # challenger totally wrong once
print("e-value:", e.evalue, "-> permanently 0; valid as e-process but betting_fraction=1 is never sensible; no guard.")

print("\n=== F5: e-process lambda is static, not predictable-adaptive; no delayed-label/order handling ===")
print("ChallengerEvidence has no event ids, no timestamps, no dedup -> same resolution can be fed twice:")
e = ChallengerEvidence(0.5)
for _ in range(20): e.update(0.5, 0.9, 1)
print("e-value after feeding ONE outcome 20 times:", round(e.evalue, 1), "reject:", e.reject_null())

print("\n=== F6: Kelly FOC check and cost-unit mismatch ===")
th = BinaryThesis("X", NOW + timedelta(days=3650), "def", 0.10, 0.15, 10.0, 0.2, ("e1",), "v")
c = robust_binary_allocation(th, forecast_at=NOW)
print("w at p_low=0.10:", c.max_portfolio_fraction, "(expected 0.025)")
# numeric check of optimum
import numpy as np
ws = np.linspace(0, 0.2, 20001)
g = [growth(w, 0.10, 10.0, 0.2) for w in ws]
print("numeric argmax:", ws[int(np.argmax(g))])
# fixed cost compares log-growth to a cost FRACTION of portfolio; correct comparison is growth vs -log(1-c)
cfrac = 0.002
print("growth(w*)=", round(growth(0.025, 0.10, 10, 0.2), 5), " cost fraction:", cfrac, " -log(1-c):", round(-np.log(1 - cfrac), 5))
# p_high is never used -> robust in name only against the lower bound; upper bound could be used for a max-regret check
print("p_success_high used anywhere in allocation?  No (grep core.py).")
# max_fraction=0 degenerate: certificate says risk_valid True with w=0 -> fine; but max_fraction >= 1 forbidden while w_opt may exceed 1 silently clamped
th2 = BinaryThesis("Y", NOW + timedelta(days=30), "def", 0.9, 0.95, 1.5, 0.9, ("e1",), "v")
c2 = robust_binary_allocation(th2, forecast_at=NOW, max_fraction=0.99)
print("w_opt for p=.9,up=1.5,down=.9 (unclamped formula):", -(0.9*0.5 + 0.1*(-0.1))/(0.5*-0.1), "-> clamp to", c2.max_portfolio_fraction)

print("\n=== F7: coherence scaling and missing guard in event_probability_bounds ===")
names = [f"E{i}" for i in range(14)]
iv = {n: ProbabilityInterval(0.1, 0.9) for n in names}
t0 = time.time(); cj = coherent_joint(iv); t1 = time.time()
print("coherent_joint 14 events:", round(t1 - t0, 2), "s, worlds:", len(cj.worlds))
try:
    coherent_joint({f"E{i}": ProbabilityInterval(0.1, 0.9) for i in range(15)})
except ValueError as ex:
    print("coherent_joint n=15 ->", ex)
print("event_probability_bounds has NO n<=14 guard (2^n enumeration unbounded):", "len(events)>14" not in open(sys.argv[1] + "/cpe/coherence.py").read().split("def event_probability_bounds")[1])

print("\n=== F8: coherence returns an arbitrary LP vertex, not a reference distribution ===")
b = {"A": ProbabilityInterval(0.2, 0.3), "B": ProbabilityInterval(0.4, 0.5)}
j = coherent_joint(b, (("A", "B"),))
print("joint picked:", dict(zip(j.worlds, [round(p, 3) for p in j.probabilities])))
print("-> c=0 objective; HiGHS returns a vertex; RFC's KL/proper-score selection is not implemented.")

print("\n=== F9: Evidence authenticity checks are shallow ===")
h = hashlib.sha256(b"anything").hexdigest()
ev = Evidence("E", "http://example.org/x", h, NOW, NOW, NOW, "claim")
ev.verify_as_of(NOW)
print("http:// (non-TLS) URL + hash not derived from content accepted: OK (no exception) -> self-declared provenance")

print("\n=== F10: precheck payload hard-codes ManualOrder=False and fixed FieldGroups; no schema validation ===")
from cpe.saxo_sim import build_precheck_payload, SaxoInstrument
p = build_precheck_payload(SaxoInstrument(1, "NotAnAssetType", "k"), 0.0001, limit_price=1e-9)
print("accepts AssetType='NotAnAssetType', Amount=0.0001, price=1e-9:", p["AssetType"], p["Amount"], p["OrderPrice"])
print("\nALL ATTACKS COMPLETED")
