# PATCH_PROPOSALS

Two equivalent forms of the same change set:

1. `PATCH_v01_to_v02.diff`: unified diff (`diff -ruN source_v0_1 source_v0_2`, 17 files). Apply with `git apply` or `patch -p1` inside a copy of `source_v0_1`.
2. `source_v0_2/`: the complete patched tree, ready to run: `pip install -e .[test] && python -m pytest -q` → 31 passed (Python 3.13.16, 2026-10-16).

## Files changed or added

| File | Change | Finding |
|---|---|---|
| `cpe/eprocess.py` (new) | commit-before-resolve e-process, predictable λ, λ_max<1, running-max rejection | P0-STAT-01 |
| `cpe/registry.py` (new) | EventSpec / Forecast registry with vague-word guard, prospective check, immutable ids, ledger-backed | P0-SCI-01 |
| `cpe/fusion.py` (new) | mandatory 3 LLM + Jev, correlation-aware weights, effective-model count, typed abstention | P0-ARCH-01/03 |
| `cpe/jev_adapter.py` (new) | typed Jev client per live OpenAPI, complement-gap, retries, cost ceiling, credential guard, injectable transport | P0-ARCH-02 |
| `cpe/allocation.py` (new) | scenario max-min log-growth allocator with caps, worst-loss, fractional Kelly | P1-RISK-01 |
| `cpe/ledger.py` | seq, monotone time, anchors (HMAC), threat model | P1-LEDGER-01 |
| `cpe/saxo_sim.py` | gate state machine, pilot whitelist, ExternalReference, x-request-id, token-safe errors, LIVE blocked | P0-BRKR-01, P1-SAXO-01, P1-SEC-01 |
| `cpe/core.py` | cost-unit fix, https-only, `evidence_digest`, `ChallengerEvidence` deprecated | P2-CORE-01, P2-EVID-01 |
| `cpe/coherence.py` | n≤14 guard in `event_probability_bounds` | P1-COH-01 |
| `proofs/BetThreshold.lean` | header now states compiled toolchain | P2-LEAN-01 |
| `proofs/RiskBudget.lean` (new) | 7 compiled lemmas used by allocator/LP/e-process | H4 |
| `proofs/lean-toolchain`, `proofs/lake-manifest.json`, `proofs/lakefile.toml` (new) | exact pins | SCI-05 |
| `tests/test_v02_regressions.py` (new) | 20 regression tests, each tied to a finding | all |
| `tests/test_engine.py` | one legacy test updated to the stricter precheck contract; deprecation warning asserted | P1-SAXO-01 |
| `pyproject.toml` | version 0.2.0, numpy dependency | |

## Deliberate non-changes

- No function places an order. `Gate.promote` to `LIVE_CAPPED_1000` raises.
- No tokens, keys or account identifiers appear anywhere in this tree.
- No provider adapter for Claude/OpenAI/Gemini is included; the contract is in the spec and the access terms are an open question (Q2).

## Breaking changes vs v0.1

- `build_precheck_payload` now returns `(body, headers)`, requires `certificate_id`, requires `tradable=True` on the instrument, and no longer emits `ManualOrder` (undocumented on the precheck reference page).
- `sim_precheck(gate, payload, headers, ...)` requires a `Gate` at `SIM_PRECHECK` or above.
- `ChallengerEvidence(1.0)` now raises; the class warns on construction.
- `Evidence` rejects `http://` URLs.
