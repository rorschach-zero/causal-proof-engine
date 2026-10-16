# SCIENTIFIC_EXPERIMENTS.md: falsification plan for CPE v0.2

Date 2026-10-16. All thresholds below are pre-registered by inclusion in this file; changing one requires a ledger entry `preregistration_amendment` with justification, written before the affected data are unblinded.

## 1. Primary null and what disproves the novel advantage

**H0:** fused CPE forecasts have no lower expected Brier score than the Design-C base-rate model on prospectively registered milestone events.
**Test:** `CommittedEProcess` with baseline = Design-C, challenger = CPE fusion, α = 0.05, λ from past increments only (GRAPA-style, λ_max = 0.5). One e-process for the primary test; secondary e-processes (per sector, per horizon, per model) are exploratory and reported with their count.
**Disproof of the novel advantage:** after 300 resolved events the primary e-value never reached 20, **or** the best single model's e-process versus the fusion reached 20. Either outcome is published in the ledger and in a dated negative-result note.

Power sanity check (simulation in `tests/test_v02_regressions.py::test_eprocess_has_power_when_challenger_better`): with an uninformative baseline and a well-calibrated challenger the e-value crosses 20 well within 300 events. Against a reasonable base-rate baseline the required improvement is smaller, so 300 events is a floor, not a guarantee of power; the plan budgets 600 registered events in year one (≈ 2 per working day) across ≥ 6 sectors, horizons 1 to 9 months.

## 2. Scoring rules and reporting

- Brier and log score per forecast (interval midpoint for scoring; interval coverage reported separately as the fraction of resolved events whose outcome frequency within a bin lies inside the fused interval).
- Reliability diagrams by horizon {≤1m, 1-3m, 3-9m}, by sector, by source family, by forecaster; bins require ≥ 30 events.
- Discrimination: AUC and Spearman rank correlation for rare targets; calibration not reported for bins with < 50 events.
- Abstention rate, re-research rate, VOID rate per source; a forecaster is scored only on items where it did not abstain *and* an abstention penalty is reported separately (fraction abstained, and Brier of the fusion on items it abstained on, to detect strategic abstention).
- Discovery lead time (H5): days between `event_registered` and first external mention; resolved by an independent search process with its own dated log.

## 3. Baselines (all mandatory, all committed to the registry with the same timestamps)

1. Design-C cohort base rate (historical frequency of the event class conditioned on observables at as-of).
2. Market-implied where available (option-implied move probabilities for listed names; analyst dispersion); marked absent otherwise.
3. Single LLM (each of the three, round-1 output only).
4. Equal-weight average of the three (naive pooling) to isolate the value of correlation-aware fusion.
5. Random-selection control for H2 with identical sizing rules.
6. Always-invested benchmark for H6.

## 4. Data hygiene and leakage controls

- Purged, embargoed walk-forward for any trained component (calibration maps, hazard model, Design-C): purge window = max horizon of overlapping events; embargo = 30 days.
- Every backtest series shifted by its publication-lag entry; vintage data where available (ALFRED); sources without a lag entry are excluded.
- Point-in-time universe with delistings; corporate-action-adjusted returns from the as-of date; the Wald audit reports the share of candidates that later delisted.
- Timestamp lag test: a forecast with `known_at` inside the resolution window is rejected by the registry (tested).
- Reality-check against many hypotheses: the self-improvement loop runs one primary e-process per artifact; exploratory comparisons are reported with the number of comparisons; no promotion on an exploratory test.
- Overfitting controls for the promoter: shuffled-label holdout (must show no gain), time-shifted holdout, canary events with promoter-only outcomes, hash-pinned datasets listed in the ledger.
- Contamination: LLM round-1 prompts contain only the archived evidence bundle; model knowledge cutoffs are recorded per forecast; events whose resolution date precedes the model's cutoff are excluded from skill statistics (they are kept for pipeline tests only).

## 5. Ablations (pre-registered arms; each arm is a separate forecaster id in the registry)

| Arm | Change | Primary metric | Pass criterion (year 1) |
|---|---|---|---|
| FULL | as specified | Brier, log, coverage | reference |
| −Jev | rules + local 7-14B classifier at equal recall budget | lead recall, cost, downstream Brier | H3 falsified if FULL recall − arm recall < 0.1 at equal cost |
| −LLM_i (×3) | drop one researcher, fusion on two + Jev | Brier | fusion value shown if FULL beats every −LLM_i by e-value ≥ 20 |
| single LLM (×3) | one researcher only | Brier | see §1 |
| −coherence | naive pooled point probabilities, no LP/credal projection | coherence error, Brier | coherence error must be > 0 and Brier worse, else coherence layer is removed from the critical path |
| −certificates | no Lean/LP certificate gate | logic/budget violations in SIM | must be 0 in FULL, > 0 in arm, else H4 is vacuous |
| −counterfactual ledger | no shadow books | not a forecast arm; evaluated on decision audit | n/a |
| Design A vs B | LP vs credal network on graphs with > 14 nodes | Brier, coverage, runtime | select after 150 resolutions |
| price-trend | 12-1 momentum on the same universe | H2 shadow | benchmark |
| buy-and-hold / cash | | H2 shadow | benchmark |

Jev-specific prospective measurements: recall of leads later judged useful by round-2 research, false-positive rate, complement gap distribution, latency, cost per 1,000 documents, drift of the returned `model` name over time.

Source-induced error stress: re-run FULL with one source family removed at a time; report Brier change; a single source family driving > 50 percent of skill is flagged as fragility.

## 6. CI thresholds (block merge unless met)

- All tests pass on Python 3.11 and 3.13; Lean files compile on the pinned toolchain (`proofs/lean-toolchain`, `proofs/lake-manifest.json`).
- Property tests: ledger anchor detects any single-byte change; e-process false-alarm Monte Carlo ≤ α + 0.015; fusion returns RE_RESEARCH on any missing mandatory input.
- Static gates: no module under `cpe/` imports the executor; no string matching `Bearer ` or `refresh_token` in logs produced by the test suite.
- Fault injection: Jev 503 storms, Saxo 429/5xx, clock skew, truncated ledger, malformed LLM JSON; required behaviour is fail-closed (no order path reachable), documented in the test names.

## 7. First-year outcomes (what success and failure look like)

- Quarter 1: registry live, ≥ 100 events registered, anchors verified, SIM_READ_ONLY reached.
- Quarter 2: ≥ 250 events registered, ≥ 60 resolved, first reliability diagrams (exploratory), SIM_PRECHECK.
- Quarter 3: ≥ 450 registered, ≥ 150 resolved, Design A vs B selection, Jev ablation read-out.
- Quarter 4: ≥ 600 registered, ≥ 300 resolved, primary e-process read-out; SIM_EXECUTION only if the gate evidence bundle is complete.
- Success: primary e-value ≥ 20 with FULL beating every single model; abstention < 40 percent; VOID < 10 percent.
- Failure: primary e-value < 20 **and** no single model ≥ 20 either (no skill anywhere: stop and publish), or a single model ≥ 20 while FULL < 20 (fusion is harmful: redesign fusion, keep registry).

Nothing in year one tests H2. H2 is a 5-year shadow experiment with pre-registered bootstrap reporting; the $1,000 pilot, if ever enabled, tests operations.
