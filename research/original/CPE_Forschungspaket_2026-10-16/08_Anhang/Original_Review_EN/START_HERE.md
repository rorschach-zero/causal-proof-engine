# START HERE: Claude independent review output, 2026-10-16

Reviewer: Claude (Fable 5.1). Input package: `CPE_Claude_Independent_Review_2026-10-16.zip` (manifest verified). This package is written to be cross-reviewed by an OpenAI reasoning model; every file is standalone Markdown, CSV, code or logs.

## Decision

**REVISE. No capital, including the $1,000 pilot. LIVE promotion is blocked in code.** Reasons and findings: `CLAUDE_REVIEW.md`.

## Files (the seven required outputs)

1. `CLAUDE_REVIEW.md`: decision, P0/P1/P2 findings with file:line, reproductions, fixes, dated sources, access/cost analysis, approval criteria, immediate first step.
2. `CPE_v0.2_REVISED_SPEC.md`: canonical research spec (hypotheses, data layer, forecast/coherence designs A/B/C, fusion, model roles, allocation and risk limits, crisis policy, self-improvement, security, Saxo gates, exact changes from v0.1).
3. `SCIENTIFIC_EXPERIMENTS.md`: falsification plan, scores, baselines, leakage controls, ablations, CI thresholds, year-one outcomes.
4. `IMPLEMENTATION_SEQUENCE_WINDOWS_SAXO.md`: ten steps starting with the safest action, acceptance tests, failure paths, costs.
5. `PATCH_PROPOSALS/`: unified diff plus the full patched `source_v0_2/` tree (31 tests pass) and compiled Lean proofs with pinned toolchain.
6. `OPEN_QUESTIONS_AND_DECISIONS.md`: blocking questions Q1-Q9, assumptions, decisions, costs, what could not be done.
7. `REVIEW_SCORECARD.csv`: all 20 original criteria plus SEC-01, with verdicts and sources.

Supporting: `EVIDENCE/` (pytest logs for v0.1 and v0.2, attack reproduction script and output, Lean compile log with toolchain pins, saved TypeSafe OpenAPI document), `MANIFEST.sha256`.

## How to verify quickly (10 minutes)

```
sha256sum -c MANIFEST.sha256
cd PATCH_PROPOSALS/source_v0_2 && pip install -e .[test] && python -m pytest -q      # expect 31 passed
python -I ../../EVIDENCE/attack_v01_reproduction.py <path to source_v0_1> /tmp/x     # reproduces v0.1 weaknesses
```

## Unproven hypotheses (flagged throughout as HYPOTHESIS)

H1 calibration gain from fusion, H2 economic edge, H3 Jev recall at lower cost, H5 discovery lead time, H6 crisis throttle benefit, and the central claim that milestone-event skill transfers to pre-trend 10x discrimination. None is supported by data in this package. Rare-event (10x/100x) calibration cannot be demonstrated within 12 months; this is stated, not hedged.

## Immediate first step for the owner

Create the Saxo Developer Portal SIM application and obtain a one-day SIM token on the Windows machine; run the v0.2 tests locally; run one read-only SIM readback and anchor its digest in the ledger. No LLM pipeline and no orders before that.
