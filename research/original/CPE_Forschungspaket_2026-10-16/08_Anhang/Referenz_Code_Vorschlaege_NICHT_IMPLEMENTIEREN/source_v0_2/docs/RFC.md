# Causal Proof Engine: Scientific Research & Engineering RFC v0.1

**Version:** 2026-10-16. **Status:** Hypothesis / experimental specification, not a validated strategy. **Objective:** discover neglected nonlinear future changes, translate them to falsifiable economic scenarios, select bounded-risk multi-asset positions, and adapt without learning from hindsight.

## 0. The intellectual invention we propose

The **Proof-Carrying Causal Bet (PCCB)** is a typed, versioned research object that joins causal mechanisms, calibrated probabilistic event forecasts, financial value capture, and mathematically checkable execution constraints. The *assembly and testing architecture* is our original **research proposal**. None of the individual ingredients, or our potential edge, is claimed as a novel proven scientific discovery.

A `PCCB` has a unique ex-ante identifier and a strict as-of timestamp. Its content is:

1. `origin`: independently archived primary documents with publication dates, first availability, checksums, original language, parser output, and extraction uncertainty;
2. `mechanism`: causal DAG / structural equations, external shocks, necessary conditions, purported interventions, counterexamples, substitution paths and independently observed causal links;
3. `events`: exact observable milestones and horizon dates; events are individually testable and defined before outcomes;
4. `belief`: probability *intervals* or a set of compatible joint distributions, model version, calibration cohort, historical score, assumptions and missing information;
5. `value_capture`: change in prices/volume/margins/capital intensity/share count, time to cash flow, dilution, valuation, option payoffs and opportunity costs;
6. `adversarial_case`: competing mechanisms, failure cases and what evidence would overturn the thesis;
7. `decision`: a robust utility optimization and mathematical risk/permission constraints;
8. `audit_trail`: first prediction, every update, simulated action, actual fill, realized outcome, rejected alternatives and the corresponding shadow-book comparison.

Nothing is traded directly because an LLM writes a persuasive narrative. A candidate trade requires a PCCB whose assumptions are independently reviewable and which passes technical and risk gates.

## 1. Scientific core: coherent *joint* uncertainty, not three confidence scores

Suppose causal nodes include `A=regulation takes effect`, `B=customer product certified`, `C=capacity expands`, `D=profit above threshold`, `E=shareholder return >=10x`. The model is not allowed to compute `P(E)` by multiplying arbitrary independent values. It defines admissible world states Ω and logical/mechanistic constraints, for example `E -> D`, `D -> (B & C)` **only if actually justified** by a business mechanism.

Each researcher supplies testable marginal probability intervals `[l_i,u_i]` for identifiable events, with citation and forecaster history. We propose computing a *credal set*:

`P_t = {q over Ω : q(ω)>=0, sum q=1, l_i <= sum_{ω in E_i} q(ω) <= u_i, causal logical constraints hold}`

This ensures arithmetic coherence of event probabilities **conditional on asserted constraints**. If P_t is empty, escalate a contradiction; do not average contradictory confidence values. Minimize a proper scoring or KL objective to choose a reference distribution only after feasibility checks. Do not confuse a coherent probability distribution with true causal identification.

Lean 4/mat​​hlib formalizes probability axioms, implication constraints, payoff identities, option loss bounds and conditional risk-budget propositions. It cannot prove that a company's managers will meet targets. Empirical procedures must justify the input intervals and causal assumptions; all certificates list these hypotheses explicitly.

## 2. Original candidate algorithm: evidence-to-profit causal search

**Unblinded market data and tickers arrive late, not early.** This matters because seeking 'the next NVIDIA' in price charts teaches the system to find yesterday's winners.

**Step A: world-first scanner:** continuously ingest science, permits, regulation, standards, physical supply chains, public procurement, factory commissioning, qualifications, medical/device approvals, demographic/energy/credit data, company filings. Record *all* hypothesized changes, including rejected and non-investable ones.

**Step B: causal expansion:** for each change, run independent branches:
- prerequisites: what must happen first?
- substitutes: what cheap alternative could eliminate the bottleneck?
- delayed costs: what capital, time and regulation are required?
- distribution: who has pricing power, who is commoditized?
- countertrend: what makes the entire opportunity disappear?

**Step C: signal selection:** identify measurements that *precede* revenue: verified qualification, an independently timed test, batch-scale yield, contract prices, production bottleneck or safety certification. Each signal must be archived with time, expected result, null hypothesis and horizon.

**Step D: economic sensitivity:** derive margins, shares, dilution and enterprise value under several mutually consistent worlds. Estimate a distribution over shareholder total-return multiples, inclusive of bankruptcy/delisting, transaction costs and time value. Distinguish a large market from a high return to today's stockholders.

**Step E: portfolio decision:** select among *all* permitted Saxo instruments as delivery methods for exposure, but never invent option quotes. Compare stock, fractional share if permitted, ETF, bond, option, futures, FX hedge, etc. on real liquidity and after-cost utility. Directional shorting/margin derivatives excluded from initial $1,000 pilot.

## 3. Robust allocation and tail outcomes

Let R_j be scenario-specific total return per unit invested and w the fraction of wealth invested. For probability uncertainty set `P_t`, choose

`max_w min_{q∈P_t} E_q[log(1+w R)] - trading_cost(w)`

subject to hard budgets, no prohibited leverage, liquidity constraints, local currency exposure limits, mark-to-market drawdown policy and worst-case premium loss caps.

Other objectives (probability of reaching target, expected log growth, conditional value-at-risk, probability of ruin) form a Pareto frontier, not a magic single score. The goal 4,000→400,000 USD in 10 years requires 58.49% annual compounded returns if fully invested from day 0, which is an aspirational tail target, not a fitted mean.

**Illustrative two-state model:** 10x upside; 0.2x downside; success p=12%. The expected arithmetic multiple is `0.12*10+0.88*0.2 = 1.376`, but investing the *whole portfolio* has expected log wealth `0.12 ln(10)+0.88 ln(0.2) ≈ -1.14`, disastrous for compounding. Within these artificial assumptions, full-Kelly single-bet weight is about 5.22%. If defensible lower probability is 10%, robust optimal fraction falls to 2.5%; if lower bound is <=4/49 ≈8.16%, no positive arithmetic edge under the model. This is why possibility of 10x alone is irrelevant to bet sizing.

A real multi-asset risk model needs dependent tail scenarios, financing/liquidity stress, options path-dependent losses, and transaction costs. The simple two-state math in the starter is a pedagogical test, **not** a live allocator.

## 4. Continuous statistical falsification and self-improvement

**Prospective test registry:** every prediction is committed before evidence arrives, including event date, class, p interval, reference forecast, and any experimental treatment of Jev or other models. No retroactive rewording; append corrective entries to the ledger.

**Proper scores:** Brier and logarithmic scores for events; reliability plots segmented by time horizon, sector, source, and surprise type. Financial returns are secondary; forecast consistency is a precondition for trusting the system.

**E-process for perpetual monitoring:** each trial records `X_t = Brier_baseline - Brier_challenger ∈[-1,1]`. Under the conditional null `E[X_t | past] <= 0`, with pre-selected predictable `λ_t ∈ [0,1]`, `M_n=Π(1+λ_t X_t)` is a nonnegative test supermartingale. Ville's inequality limits the false alarm probability for ever declaring improvement when `M_n ≥ 1/α`. Its assumptions MUST be honored: prospective forecasts, no duplicated unresolved events, proper handling of overlapping outcomes, predefined significance budget, and no selection of just the winning tests. This is a statistical guarantee about that null **not** a guarantee of future profits.

**Safe policy improvement:** an evolved decision policy is deployed only after challenger-vs-baseline out-of-time tests, independent strategies, simulated stress and a period of shadow operation. Literature on safe policy improvement offers theoretical guarantees under specified environment assumptions, not unconditional protection in markets with regime shifts.

**Evolutionary research:** models may propose feature selectors, causal graphs, valuation policies, document parsers, mathematical bounds and exit algorithms. Every new version is containerized and tested against immutable benchmarks; critics actively search for artifacts, contamination and hidden peeking. Risk engine, broker permissions, and audit history are NEVER mutable by the self-improver.

**Survivorship-aware loss lab: the Abraham Wald test:** store every security in the historical investable universe at the time it was first observed, including bankruptcies, delistings, splits, reverse splits, acquisitions, stale tickers, secondary offerings and liquidity failures; track *all* considered hypotheses and positions, including losers never bought. For each exit, maintain a counterfactual 'no exit' shadow policy, and for each non-entry an entry-shadow. Evaluate ex-ante policies over the entire cohort, not cherry-picked spectacular outcomes. Distinguish genuinely bad thesis, bad timing, premature good-thesis exit, good sale before collapse, and luck.

## 5. Crisis handling: predictive, not reactive panic liquidation

Create causal **regime hazard** models for recession, systemic funding stress, liquidity withdrawals, and individual-company impairment. Inputs must be *leading, knowable in real time*: credit spreads, lending standards, repo/funding stress, earnings guidance revisions, capital-market closures, refinancing schedule, and liquidity rather than just an equity 200-day average.

A regime detector emits a *distribution over near-term hazards* plus a calibration interval, not a literal 'CRASH=YES'. Separate:
- systemic risk rising **before** portfolio losses;
- realized drawdown without deterioration in underlying earnings;
- durable thesis impairment that justifies selling even late;
- temporary liquidity panic with attractive forward expected return.

Use asymmetric threshold and hysteresis for reductions and restoring exposure. Research an alternate always-invested benchmark. Explicitly test how often protective exits occur after most damage is done, how much the model misses in rebounds, and whether avoiding losses dominates unnecessary false alarms. No system can guarantee exiting before crashes.

## 6. Jev: a useful component, not a probability oracle

TypeSafe Jev, released 15 September 2026, provides low-latency typed decisions for Choice, Score, Noul questions. Vendor claims include 70-500ms, $0.042/million input tokens, and structured probabilities. Independent evaluation (arxiv:2609.37647) finds substantial classification strength but task-dependent calibration; another study (arxiv:2609.33209) finds probabilities across complement questions are internally inconsistent.

**Appropriate use:** high-volume triage of source type, event relevance, novelty candidates, duplicated claim clustering, contradiction alarms, and escalation to deeper models. Evaluate Jev head-to-head against cheap rules and a small local model in a preregistered randomized ablation; include end-to-end cost, true positive rate, recall of rare useful leads, systematic bias and downstream investment research quality. Use a coherence projection on its output probabilities and calibrate against event-specific empirical outcomes, not vendor general benchmark scores.

**Never use Jev alone** to decide trade sizes, estimate 10x event probability from arbitrary narratives, override Lean/risk certificates, or pass instructions to Saxo.

## 7. The three scientific agents and adversarial protocol

- **Claude Fable 5.1:** causal discovery, industrial mechanism, historical analogues, counterfactual alternatives; tasked to *avoid tickers* during early graph generation.
- **OpenAI Astra:** adversarial causal research, data audit, formal specification generation, counterexamples, Lean attempts, uncertainty stress tests.
- **Gemini 4 Argon:** independent technical and scientific reasoning, alternate futures and non-consensus search, evaluation of economic value capture.

The researchers should start independently and should have access to source evidence, not each other's conclusions. They submit structured, cited, timestamped candidates and competing forecasts. A second round cross-examines disagreements. The portfolio policy compares evidence and actual historical forecast quality, not simple 2-of-3 majority vote. Researchers are replaceable; the persistent independent data and testing system is the institution.

Important operational constraint: Chat subscriptions generally do not authorize unattended access to commercial models. Model adapters require valid supported APIs, desktop automation with adequate permissions, or other permitted programmatic access; do not rely on bypassing websites or accounts. This prototype has not called Claude/Astra/Gemini.

## 8. Saxo OpenAPI: setup and trading gates

Source: https://www.developer.saxo/openapi/learn/environments

1. Register on https://www.developer.saxo and create SIM application; first use one-day SIM token and the Explorer.
2. Link a funded live account to SIM if appropriate for market-data entitlements; independent Saxo help dated 2026-09-07 says this unlocks delayed quotes on available live-account instruments. Do not assume live prices in generic SIM.
3. Implement OAuth Authorization Code + PKCE and secure refresh-token rotation. No tokens in source, logs or prompt context.
4. Query `/ref` instrument universe; identify actual UIC, AssetType, lot size, tradability, min amounts, option roots, option expiry, margin and permitted order types; verify account-specific entitlements.
5. Read `/port` account cash, open orders and positions; subscribe to position/order event streams.
6. Draft candidate orders locally with versioned thesis certificate; call SIM `POST /trade/v2/orders/precheck` with cost and margin fields; do not automatically accept pretrade disclaimers.
7. For multileg listed options, only use supported option roots and `/trade/v2/orders/multileg/precheck`. Saxo notes exchange-specific restrictions. Saxo documentation states FX options are not placeable through OpenAPI, despite the wider Saxo product range.
8. After SIM integration, request a separately provisioned LIVE application and permissions. Do not infer that SIM rights grant LIVE writes.
9. If LIVE automatic order entry is explicitly enabled on this account, set `ManualOrder: false` on actually machine-originated orders, consistent with Saxo definitions. No order placement in the starter repository.
10. Gate on session health, stale data, USD/CHF conversion, duplicate order IDs, adverse gap / option exercise risk, market hours, order pre-check, worst-case loss and commission; reconcile every fill back to certificate.

Gate transitions: `RESEARCH_ONLY` -> `SIM_READ_ONLY` -> `SIM_PRECHECK` -> `SIM_EXECUTION` -> `SHADOW_LIVE_QUOTES` -> `LIVE_CAPPED_1000`; transitions require objective tests and owner authorization. No automatic promotion by the research agents.

Instruments: equities, ETFs, exchange-traded options and spreads when supported, bonds, funds, futures, permitted commodity/FX exposures, and CFDs only if specifically authorized and risk-engineered. Test and classify every instrument separately: some require leverage, have unlimited contingent losses or need special documentation, so the initial $1000 pilot limits actual exposure to fully paid, loss-bounded instruments.

## 9. Test plan: explicit falsification

**H0 (primary):** Compared to pre-registered baselines, CPE produces no improvement in out-of-sample event forecast Brier/log scores net of selection effects.

**H1 (scientific):** Consistent event-time primary data, coherent joint distributions, and causal falsifiers measurably improve calibrated future event predictions over sources-only LLM and price-only baselines.

**H2 (economic):** Conditioned on financing and risk constraints, CPE's recommendations generate higher *after-cost* long-horizon risk-adjusted performance than simple equity/multi-asset benchmarks and a random trading control.

**H3 (Jev):** Jev triage improves rare true-signal recall at given research cost without systematic degradation of calibration.

**H4 (Lean):** A formally constrained order plan reduces logic/risk-budget violations to zero *in the validator's mathematical model*. This does not remove execution, data or model risk.

Ablations: [full CPE], [without causal graph], [without proof gate], [without Jev], [without counterfactual ledger], [LLM-only], [price trend], [buy and hold], [cash/treasury benchmark]. Freeze historical training windows, run purged walk-forward with data publication lags and honest transaction costs. Include every historical constituent, bankrupt and delisted names. Pre-register experiments and exposure limits; report negative outcomes.

Metrics: Brier/log skill, event discovery lead time and false alarms, forecast calibration by subclass, probability coherence error, e-values/false discovery control, drawdown/expected shortfall, CAGR, turnover, fill slippage, spread, cost ratio, realized vs counterfactual return, and proportion of gains from rare outsized winners. The first $1000 live experiment mainly validates operation and research quality, **not** a 10-year extreme-return claim.

## 10. Build milestones by dependency, not guesswork

- **M0: Local offline tests pass.** CPE two-state certificate and all research controls run on synthetic data; Lean drafts separately compile and verify in Lean CI.
- **M1: Saxo SIM connection.** Account, instruments, quote access, holdings readback, SIM precheck and order reconciliation verified with user's own authorized Saxo account.
- **M2: Scientific data pipeline.** Real first-party sources, timestamped snapshots, reliability and entity mapping; 100+ pre-registered milestone forecasts from several independent sectors.
- **M3: Coherent forecasting.** Credal-set feasibility solver, formally certified constraints, paper alternative strategies, proper-score calibration and prospective e-process monitoring.
- **M4: Multi-model reasoning.** Claude/Astra/Gemini with authorized access, source-locked independent generation, blinded adversarial research, model quality history.
- **M5: Safe self-improvement.** Evolver generates candidate algorithms and prompts; frozen holdouts, evidence threshold and shadow acceptance procedure, broker gates immutable.
- **M6: Pilot capital.** Only after permissions and limits confirmed; up to $1,000 live, uninvested $3,000 remains outside until prospectively validated. No leveraged short gamma, no naked derivatives.

## Research references (inspected 2026-10-16)

- Lean4: https://lean-lang.org/theorem_proving_in_lean4/
- Mathlib: https://github.com/leanprover-community/mathlib4
- Jev vendor: https://typesafe.ai/blog/introducing-system-one-models-and-jev (2026-09-15)
- Independent Jev benchmark: https://arxiv.org/abs/2609.37647 (2026-09-29)
- Jev probability coherence: https://arxiv.org/abs/2609.33209 (2026-09-27)
- E-process/martingales: https://arxiv.org/abs/2009.03167
- Safe Policy Improvement: https://proceedings.mlr.press/v97/laroche19a.html (2019)
- Safe improvement caveats: https://arxiv.org/abs/2208.00724
- AlphaEvolve: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/ (2025-05-14)
- Bayesian Online Changepoint Detection: https://arxiv.org/abs/0710.3742
- Survivorship and extraordinary winners: https://www.tandfonline.com/doi/full/10.1080/0015198X.2023.2188870 (2023)
- StockBench: https://arxiv.org/abs/2510.02209
- Gemini 4 Argon: https://ai.google.dev/gemini-api/docs/latest-model (2026-10-13)
- Saxo SIM/LIVE: https://www.developer.saxo/openapi/learn/environments
- Saxo direct client LIVE credentials: https://www.developer.saxo/openapi/learn/direct-clients-request-for-openapi-application-credentials-for-the-live-environ
- Saxo order precheck: https://www.developer.saxo/openapi/referencedocs/trade/v2/orders/post__trade__precheck
- Saxo OpenAPI instruments: https://www.developer.saxo/openapi/learn/core-business-concepts
- Saxo auto/manual order: https://www.developer.saxo/openapi/learn/order-placement

