# Causal Proof Engine (CPE), research starter v0.2 (review patch of 2026-10-16)

**This is an experimental decision-science prototype, not an autonomous investment bot.**

- Implements source-time guards to reject look-ahead leakage.
- Implements a small robust two-scenario log-utility allocator, conditioned on uncertain probabilities.
- Implements an online e-process for pre-registered comparisons of Brier scores.
- Implements a hash-chained append-only ledger for tracking *all* researched companies, including failures and rejects.
- Implements a Saxo **SIM precheck-only** order payload; there is **no method that places an order**.
- Includes Lean theorems compiled on a pinned toolchain (see proofs/lean-toolchain) and a typed Python Jev adapter with an injectable transport (no network in tests).
- v0.2 adds: committed e-process (cpe/eprocess.py), forecast registry (cpe/registry.py), correlation-aware fusion with abstention (cpe/fusion.py), scenario allocator (cpe/allocation.py), ledger anchors, and a fail-closed Saxo gate state machine with LIVE promotion blocked in code.

This does not currently include real market data, causal discovery, historic point-in-time datasets, validated prediction calibration, exchange handling, portfolio valuation, complete cost modelling, Saxo account login, live order execution, or autonomous multi-model access. Those are engineering and research milestones, not delivered features.

## Quick start

```bash
cd source_v0_2
pip install -e .[test]
python -m pytest -q   # 31 passed
python -m examples.synthetic_demo
```

To use Saxo's SIM order precheck, set `SAXO_SIM_ACCESS_TOKEN` using the official developer portal and call `cpe.saxo_sim.sim_precheck` with a real **SIM** account key, valid instrument UIC and supported order constraints. Never insert credentials in the repo.

To compile Lean proofs later, install Lean4 with mathlib and run the .lean file with `lake env lean proofs/BetThreshold.lean` inside the configured project. Currently unverified syntax.

Read `docs/RFC.md` for the full research proposal and `docs/Saxo.md` for the broker onboarding sequence.
