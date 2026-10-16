# 02 Scientific methodology

Entry point for `04/01`–`04/04` and `EN/SCIENTIFIC_EXPERIMENTS.md`. §1–§4 summarise the original; §5 is review.

## 1. Hypotheses and falsifiers (pre-registered in `04/02`)

| ID | Claim | Falsifier | Status |
|---|---|---|---|
| H0 | Fused CPE forecasts have no lower expected Brier than the Design-C base-rate model on prospectively registered milestone events (primary null). | Committed e-process (baseline = Design C, challenger = fusion, α = 0.05, λ_max = 0.5) never reaches 20 after 300 resolved events, **or** the best single model's e-process against the fusion reaches 20. | primary test, not yet started |
| H1 | Fused, coherence-projected forecasts from three LLMs plus Jev have lower Brier and log loss than the best single LLM and than Design C. | H0 not rejected, or a single model beats fusion by ≥ 0.01 Brier at e-value ≥ 20. | HYPOTHESIS |
| H2 | After-cost long-horizon returns of the certified book exceed cash, an equal-weight global equity ETF and a random-selection control with identical sizing. | Not evaluable in 12 months or at USD 1,000; shadow book with USD 100,000 notional over ≥ 5 years, bootstrap confidence intervals. | HYPOTHESIS, 5-year |
| H3 | Jev triage reaches ≥ 0.8 recall of rare useful leads at ≤ 20 % of LLM-triage cost without degrading downstream calibration. | Randomised ablation: Recall(FULL) − Recall(−Jev) < 0.1 at equal cost. | HYPOTHESIS |
| H4 | A certified order plan has zero logic and budget violations in the certified model. | Vacuity check: the −certificates arm must show > 0 violations in SIM, else the gate is superfluous. | statement about the model |
| H5 | The first-principles scanner registers candidate events a median ≥ 60 days before the first sell-side or mainstream mention of the same mechanism. | Measured on a dated "first external mention" field resolved by a separate search process. | HYPOTHESIS |
| H6 | Hazard-driven throttling reduces maximum drawdown versus always-invested by more than its false-alarm cost over the crisis backtest set. | Falsified → throttle removed; only thesis-break selling remains. | HYPOTHESIS |
| central | Milestone-event skill transfers to pre-trend 10x discrimination. | Rank correlation of rare-target intervals with realised 3-year returns in the shadow book, from year 3. | HYPOTHESIS, the programme's load-bearing claim |

The north star (100x in ten years) is a direction, explicitly not a test object (`04/04` §1).

## 2. Measurement (`04/03` §1–§3)

- Brier and log score per forecast on the interval midpoint; interval coverage reported separately.
- Reliability diagrams by horizon {≤ 1 m, 1–3 m, 3–9 m}, sector, source family, forecaster; bins ≥ 30 events;
  calibration not reported below 50 events per bin; rare targets by discrimination only (AUC, Spearman).
- Abstention, re-research and VOID rates; a forecaster is scored only where it did not abstain **and** an
  abstention penalty is reported (fusion Brier on the items it abstained on).
- Seven mandatory baselines: Design-C cohort base rate; market-implied where available; each single LLM;
  equal-weight average of the three; random-selection control (H2); always-invested (H6); 12-1 momentum and
  buy-and-hold/cash (H2).
- Leakage controls: purged and embargoed walk-forward (purge = max overlapping horizon, embargo 30 days);
  publication-lag shift; vintage data (ALFRED); point-in-time universe with delistings; registry rejects
  forecasts with `known_at` inside the resolution window; model knowledge cutoffs recorded per forecast and
  events resolved before a model's cutoff excluded from its skill statistics.

## 3. Ablation arms (`04/03` §5)

FULL; −Jev (rules + local 7–14B classifier at equal recall budget); −LLM_i (×3); single LLM (×3); −coherence
(naive pooled points); −certificates; −counterfactual ledger; Design A vs B on graphs > 14 nodes; price-trend;
buy-and-hold/cash. Each arm is its own forecaster id in the registry. Source-family leave-one-out stress: a
single family driving > 50 % of skill is a fragility flag.

## 4. Year-one plan and stop rule (`04/03` §7, `04/04` §5)

Q1 registry live, ≥ 100 events, anchors verified, SIM_READ_ONLY. Q2 ≥ 250 registered, ≥ 60 resolved,
SIM_PRECHECK. Q3 ≥ 450 / ≥ 150, Design A vs B selection, Jev ablation read-out. Q4 ≥ 600 / ≥ 300, primary
e-process read-out. Success: primary e-value ≥ 20 with FULL beating every single model, abstention < 40 %,
VOID < 10 %. Failure modes: no skill anywhere (stop and publish) or single model ≥ 20 while FULL < 20 (fusion
harmful: redesign fusion, keep registry). If neither skill nor discovery lead appears in years 1–2, the
programme pauses with capital outside the system.

## 5. Review

**What is right.** The plan tests what can be tested in a year (short-horizon event skill), refuses to test
what cannot (10x calibration), pre-registers thresholds, names baselines that would embarrass the system, and
budgets a negative result. That is more discipline than most published forecasting work.

**Gaps and concrete fixes (REVISION unless noted).**

1. **No power analysis against the real baseline.** The only power evidence is a simulation against an
   uninformative 0.5 baseline (`ref/tests` `test_eprocess_has_power_when_challenger_better`). Against a
   reasonable cohort base rate the Brier improvement per event may be 0.01–0.03; with λ_max = 0.5 and 300
   events the e-process may simply not reach 20 even if the effect is real. Before registering the first event,
   simulate power on a grid of plausible effect sizes and baseline sharpness and publish the detectable effect
   at n = 300 and n = 600. If the detectable effect is implausibly large, the year-one success criterion is
   mis-set, not the system.
2. **Event selection is itself a forecasting choice and a bias channel.** Which events get registered
   determines the base rate, the horizon mix and the difficulty. The protocol must register the *selection
   rule* (what makes an event eligible), log every candidate considered and rejected with reasons (the package
   does this for securities in the Wald test; it must do it for events too), and report skill both on all
   registered events and on a random subsample of eligible ones.
3. **The base-rate floor couples challenger and baseline.** `03/05` §2 floors the fused lower bound at the
   Design-C base rate. A forecast that can never fall below the baseline can only beat it on the upside, and
   the interval midpoint used for scoring inherits the floor. State explicitly which quantity is scored
   (midpoint of the floored interval) and run the primary test on the unfloored midpoint as a sensitivity.
4. **Interval forecasts are scored at the midpoint; coverage is a separate report.** That is acceptable but it
   means the system is never rewarded for honest width. Add a proper scoring rule for interval or credal
   forecasts (for example, score the midpoint plus report the interval score of Winkler, or use the
   lower-probability scoring rules from the imprecise-probability literature) as a secondary metric, and
   pre-register it now.
5. **"First external mention" for H5 is underspecified.** Define the corpus searched (which news and sell-side
   sources), the matching rule (mechanism, not ticker), the search date discipline (the search itself is
   time-stamped and logged), and the inter-rater procedure. Otherwise H5 is unfalsifiable in practice.
6. **VOID handling needs a rule.** VOID events (resolution source disappears) are excluded from skill but
   counted. A model that forecasts confidently on fragile sources benefits. Report skill with VOID graded as
   NO as a sensitivity, and cap the VOID rate per source family above which the family is retired.
7. **Strategic abstention is only reported, not penalised.** The 40 % flag is a reporting threshold. Pre-register
   a scoring treatment: abstentions are scored at the baseline forecast (so abstaining is never better than
   matching Design C).
8. **Multiple comparisons across the ablation table.** Each arm's "FULL beats arm at e-value ≥ 20" is a separate
   test; with ten arms the family-wise error is not controlled. Either declare the primary test alone as
   confirmatory and the arms as exploratory (then no arm can justify a design change on its own), or combine
   e-values multiplicatively across independent arms, or apply e-BH. Decide and write it into `04/02` by
   amendment.
9. **The year-one event target (600) has no supply-side justification.** See `01-architecture.md` §4 item 1.
10. **Human-in-the-loop contamination.** The owner-started OpenAI batch and the manual registration of the first
    20 EventSpecs (`07/01` step 6) put a human in the forecasting path. Log who touched what and when, and
    exclude human-authored forecasts from the committee statistics (the `HUMAN` forecaster id exists in
    `ref/cpe/registry.py`; use it).

Items 1, 2 and 8 should be resolved before the first event is registered; they change what "success in year
one" means.

## 6. Amendments after the Codex review (REVISION, 2026-10-16)

Recorded after reconciliation round 1 (`16-reconciliation-matrix.md`); the text above is left as written.

1. **§1 H0 and §4 primary read-out (RC-01).** The committed e-process tests the conditional null at every
   update. Events whose outcomes depend on one underlying announcement violate it even when every forecast was
   committed in advance (30 cloned outcomes reach e = 475 with probability 0.5; REPRODUCED). The betting unit
   becomes the pre-declared outcome cluster; a fixed-horizon cluster-robust paired comparison is the secondary
   analysis. The 300/600 *event* counts in §4 are replaced by independent-equivalent *cluster* counts to be set
   after supply is measured (OD4, OD5).
2. **§2 first bullet and §5 item 4 (RC-05).** The Winkler interval score was mis-specified: it elicits outcome
   quantiles, not an epistemic interval for a Bernoulli parameter. Withdrawn. Each forecast carries one scored
   point probability; the interval is a declared ambiguity set without a coverage claim.
3. **§5 item 3 (RC-03).** Superseded: the base-rate floor is deleted rather than kept as a sensitivity.
4. **§5 item 8 (RC-08).** "Family-wise control via e-BH" conflated error criteria. The pre-registered conjunction
   "FULL beats every comparator" is an intersection-union test needing no correction; promotions use lifetime
   α-spending; e-BH is for exploratory lists only.
5. **§2 leakage controls (RC-09).** The time-shifted holdout control is withdrawn as ill-posed; replaced by
   forbidden-future-information negative controls and fresh future cohorts.
6. **§5 item 1 (RC-24).** Power at 600 independent observations under the archived rule is ≈ 27 % (b = 0.5)
   to 31 % (b = 0.2) for a Brier gain of 0.01 and ≈ 81 % (b = 0.5) to 94 % (b = 0.2) for 0.02 (REPRODUCED,
   `16` Appendix B; the b = 0.2, δ = 0.02 row was added to the probe in round 2, RC-45, because round 1 cited
   it from Codex's D1 table without reproducing it). The year-one criterion is set only after supply and
   cluster structure are measured.
7. **§1 H0 row and §4 read-out, round 3 (RC-49, RC-50).** Item 1 made the fixed-horizon cluster-aware test the
   secondary analysis. Codex's round-3 review exhibited two structures under which the cluster-level e-process
   crosses while the population-average null holds: clusters open at the same time sharing a period shock, and
   skill that varies over time (both REPRODUCED, `16` Appendix D: 28.9 % crossings under a persistent regime,
   62.8 % under +0.12 then −0.12 skill with zero average). The e-process tests the sequential conditional null
   E[X_k | F_(k−1)] ≤ 0, which is stronger than H0 as written. Roles are therefore reassigned: the **primary
   confirmatory test of H0 is the fixed-horizon paired cluster test with a pre-registered calendar-block
   dependence model**; the committed e-process is the anytime-valid monitor of the conditional null, reported
   with that label, and its crossing is never alone a confirmatory result. "Primary e-value ≥ 20" in §4 is
   superseded accordingly. Under a persistent macro regime neither test holds size at 120 clusters over 24
   periods, so the dependence model is an input to OD4 and OD5 (`17` §6).
8. **§4 read-out and item 6 above, round 4 (RC-56, RC-61).** The primary test has one cut-off, 24 months after
   first cohort entry; the 12-month look is an interim for futility and integrity only, because two
   confirmatory looks at nominal α inflate the type-I error (8.0 % in normal theory, 8.8 % for the block test;
   REPRODUCED, `16` Appendix E). The power figures in item 6 are the monitor's; the primary test detects
   δ = 0.01 at 600 independent clusters with 80 % (b = 0.5) to 93 % (b = 0.2) power and δ = 0.02 at 300
   clusters with 80 % to 94 % (REPRODUCED, `16` Appendix E), but under independent period shocks of ± 0.3 its
   power at δ = 0.02 and 600 clusters falls to 47 %, so the dependence model, not the cluster count alone,
   determines the detectable effect (OD4).
