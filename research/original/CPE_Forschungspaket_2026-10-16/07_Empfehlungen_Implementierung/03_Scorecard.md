# 03 Scorecard (lesbare Fassung)

Alle 20 Kriterien der ursprünglichen `REVIEW_SCORECARD.csv` plus SEC-01. Verdikte beziehen sich auf v0.1; Klammern nennen den Stand des v0.2-Referenzvorschlags. Die Spalten entsprechen der CSV in diesem Ordner (englische Originalformulierung beibehalten, damit CSV und Markdown übereinstimmen).

## ARCH-01: All three independent LLMs required on major decisions

- Status vor Review: BLOCKED
- Evidenz/Lücke: No adapters
- Verdikt: FAIL (v0.1); contract + fusion gate delivered in v0.2 (cpe/fusion.py: RE_RESEARCH on any missing model); adapters still unwritten
- Korrekturmassnahme: Write provider adapters per spec §5 within verified access routes (Q2); test_fusion_requires_all_three_models_and_jev passes
- Primärquelle: support.claude.com/en/articles/17154008 (2026-10-07); learn.chatgpt.com/docs/auth; geminicli.com/docs/resources/quota-and-pricing (read 2026-10-16)

## ARCH-02: Jev mandatory core signal and typed probability pipeline

- Status vor Review: BLOCKED
- Evidenz/Lücke: Illustrative adapter only
- Verdikt: PARTIAL: Python adapter schema-verified against live openapi.json (v0.2.0); complement-gap measured; Jev is a hard gate in fusion; no live call made
- Korrekturmassnahme: Obtain early-access key; run GET /v1/models; prospective calibration before any probability use
- Primärquelle: https://api.typesafe.ai/openapi.json (fetched 2026-10-16, saved in EVIDENCE/); arXiv:2609.33209

## ARCH-03: Disagreement, correlation and abstention protocol

- Status vor Review: UNTESTED
- Evidenz/Lücke: Spec only
- Verdikt: PASS (design) / UNTESTED (empirically): correlation-aware min-variance weights; effective_models; typed ABSTAIN/RE_RESEARCH; test_correlated_models_do_not_count_three_times passes
- Korrekturmassnahme: Run ablations §5 of SCIENTIFIC_EXPERIMENTS; track effective_models monthly
- Primärquelle: PATCH_PROPOSALS/source_v0_2/cpe/fusion.py

## DATA-01: Trusted as-of and publication timestamping

- Status vor Review: PARTIAL
- Evidenz/Lücke: Self declared timestamps
- Verdikt: FAIL (v0.1); v0.2: https-only + digest helper + ingest-log spec; observer-signed timestamps not yet coded
- Korrekturmassnahme: Implement ingest log (spec §3.1) and publication-lag table (§3.2) in M2
- Primärquelle: core.py:28-40 (v0.1); spec §3

## DATA-02: Complete point-in-time asset universe including failures

- Status vor Review: BLOCKED
- Evidenz/Lücke: No dataset
- Verdikt: FAIL; no dataset exists; Wald audit specified
- Korrekturmassnahme: Decide licensed PIT dataset vs forward reconstruction (Q5)
- Primärquelle: spec §3.3

## SCI-01: Causal identification vs observational correlation

- Status vor Review: UNTESTED
- Evidenz/Lücke: Claims not empirically identified
- Verdikt: FAIL (v0.1: implications only); v0.2 adds identification_class and the rule that only logical links enter probability math
- Korrekturmassnahme: Implement Mechanism objects (spec §4.2); edge tested on event forecasts not DAG truth
- Primärquelle: coherence.py:53-58; spec §4.2

## SCI-02: Probability coherence with useful scaling

- Status vor Review: PARTIAL
- Evidenz/Lücke: LP finite 14 events
- Verdikt: PARTIAL: guard added to event_probability_bounds; LP vertex flagged as non-reference; credal network (Design B) specified not coded
- Korrekturmassnahme: Implement Design B in M3; keep LP for ≤14 decision events
- Primärquelle: attack F7/F8 in EVIDENCE/attack_v01_output.log

## SCI-03: Calibration on rare 10x events

- Status vor Review: BLOCKED
- Evidenz/Lücke: No labels or cohorts
- Verdikt: FAIL and NOT ACHIEVABLE in 12 months (stated explicitly); discrimination-only evaluation for 2 years; <5% elicitation forbidden
- Korrekturmassnahme: Design-C cohort base rates; decomposition; floor by base rate (spec §4.6)
- Primärquelle: CLAUDE_REVIEW §0 and §3

## SCI-04: Sequential e-process statistical assumptions tested

- Status vor Review: PARTIAL
- Evidenz/Lücke: Toy only
- Verdikt: FAIL (v0.1 API accepts hindsight; absorbing zero; duplicates); PASS in v0.2: commit-before-resolve; predictable λ; λ_max<1; MC false-alarm ≤ α; power test
- Korrekturmassnahme: Use CommittedEProcess only; ChallengerEvidence deprecated
- Primärquelle: cpe/eprocess.py; tests test_eprocess_*; attacks F3-F5

## SCI-05: Lean proofs compiled in CI

- Status vor Review: BLOCKED
- Evidenz/Lücke: Lean unavailable in starter
- Verdikt: PASS (compiled here): BetThreshold.lean and RiskBudget.lean check on Lean v4.35.0 + Mathlib cfc55fc5…; negative control fails as expected; theorems are conditional algebra only
- Korrekturmassnahme: Add CI job with pinned toolchain (step 2)
- Primärquelle: EVIDENCE/lean_compile.log

## SELF-01: Closed-loop experiment with shadow challenger and promotions

- Status vor Review: BLOCKED
- Evidenz/Lücke: No experiment runner
- Verdikt: FAIL; promoter/proposer separation and anti-reward-hacking controls specified; not coded
- Korrekturmassnahme: Implement promoter script with frozen hash-pinned holdouts in M5
- Primärquelle: spec §8; SCIENTIFIC_EXPERIMENTS §4

## SELF-02: Tamper-evident evidence and externally anchored snapshots

- Status vor Review: BLOCKED
- Evidenz/Lücke: Hash chain alone
- Verdikt: FAIL (v0.1: full rewrite undetected; attack F1); PASS in v0.2 given an external anchor store: anchors with HMAC; seq; monotone time; truncation detected
- Korrekturmassnahme: Owner anchor store outside research user's write permission; monthly verification
- Primärquelle: cpe/ledger.py; test_full_rewrite_detected_with_anchor

## RISK-01: Full multi-asset costs, FX, path dependent risk

- Status vor Review: BLOCKED
- Evidenz/Lücke: Single toy binary allocation
- Verdikt: PARTIAL: cost-unit bug fixed; scenario max-min allocator with caps and worst-loss; path dependence/options/margin NOT modelled (hence pilot whitelist)
- Korrekturmassnahme: Costs/FX/tax enter scenario returns (spec §6.1); options excluded from pilot
- Primärquelle: cpe/allocation.py; attack F6

## RISK-02: Ex-ante crash avoidance and recovery policy

- Status vor Review: BLOCKED
- Evidenz/Lücke: Not coded
- Verdikt: FAIL (not coded); policy specified with leading inputs; hysteresis; thesis-break vs price; H6 falsifier; no crash prediction claimed
- Korrekturmassnahme: Implement hazard model on vintage data; run crisis backtest set
- Primärquelle: spec §7

## BRKR-01: Saxo SIM read-only auth, account and instruments

- Status vor Review: BLOCKED
- Evidenz/Lücke: Precheck-only code
- Verdikt: FAIL (no readback code); gate machine requires SIM_READ_ONLY evidence before precheck; endpoint paths to confirm at implementation
- Korrekturmassnahme: Step 4 of implementation sequence
- Primärquelle: developer.saxo/openapi/learn/environments (read 2026-10-16)

## BRKR-02: Saxo official API precheck

- Status vor Review: PARTIAL
- Evidenz/Lücke: Local payload and HTTP client, no account
- Verdikt: PARTIAL: payload aligned with documented request (ExternalReference; ManualOrder removed as undocumented on precheck); x-request-id; whitelist; gate-guarded; no call made
- Korrekturmassnahme: Q3 on first SIM call
- Primärquelle: developer.saxo/openapi/referencedocs/trade/v2/orders/post__trade__precheck

## BRKR-03: Saxo live execution risk firewall

- Status vor Review: BLOCKED
- Evidenz/Lücke: No live adapter by design
- Verdikt: PASS (by design): LIVE promotion raises PermissionError; executor principal and signing spec written
- Korrekturmassnahme: Separate release + independent review before any LIVE code
- Primärquelle: cpe/saxo_sim.py Gate.promote; test_gate_promotion_requires_owner_and_blocks_live

## OPS-01: API/subscription cost and authorized unattended use

- Status vor Review: UNKNOWN
- Evidenz/Lücke: No credentials/terms reviewed
- Verdikt: PARTIAL: Anthropic Max credits verified; OpenAI API-key route for automation verified; Gemini quotas verified; unattended consumer-subscription use NOT fully supported; budget $200-600/month
- Korrekturmassnahme: Q2; default to API keys where terms unclear
- Primärquelle: CLAUDE_REVIEW §8 sources

## TEST-01: Current unit tests

- Status vor Review: PASS
- Evidenz/Lücke: 11 Python tests run 2026-10-16
- Verdikt: PASS reproduced: 11 passed (Py 3.13.16); v0.2: 31 passed
- Korrekturmassnahme: Keep both suites; add CI thresholds
- Primärquelle: EVIDENCE/pytest_v01.log; EVIDENCE/pytest_v02.log

## TEST-02: Fault injection + end-to-end paper evidence

- Status vor Review: BLOCKED
- Evidenz/Lücke: Not implemented
- Verdikt: PARTIAL: fault-injection tests for Jev 503 storms; cost ceiling; gate denial; malformed JSON; no end-to-end paper run exists
- Korrekturmassnahme: Implement E2E SIM paper loop in M1-M3
- Primärquelle: tests/test_v02_regressions.py

## SEC-01: Secrets never reach LLMs or logs

- Status vor Review: UNLISTED
- Evidenz/Lücke: v0.1 raise_for_status propagates request with bearer header
- Verdikt: PARTIAL: SaxoHttpError strips request; Jev adapter refuses credential-like strings; Credential Manager + per-user egress specified
- Korrekturmassnahme: Implement three-principal setup before step 7
- Primärquelle: cpe/saxo_sim.py; cpe/jev_adapter.py; spec §9
