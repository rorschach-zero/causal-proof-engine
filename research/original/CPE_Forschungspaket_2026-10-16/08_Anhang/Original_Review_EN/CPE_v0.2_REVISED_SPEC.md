# CPE v0.2 Revised Specification (canonical research spec)

**Status:** implementation-ready for milestones M0 to M3; research hypothesis, not a validated strategy.
**Date:** 2026-10-16. **Supersedes:** `source_v0_1/docs/RFC.md`. **Code:** `PATCH_PROPOSALS/source_v0_2/`.
**Language convention:** MUST / MUST NOT are enforceable in code or tests; SHOULD is design guidance; HYPOTHESIS marks an unproven scientific claim.

Non-negotiables carried over unchanged: three independent frontier LLMs plus Jev as mandatory core components; continuous learning of hypotheses, features, forecasting and causal models; sector-independent first-principles discovery; Saxo-first SIM implementation; owner-only authorization of access, limits and LIVE activation; at most $1,000 live in year one; no margin, no naked options, no unlimited-loss instruments, no automated short exposure in the pilot.

---

## 1. Scientific hypotheses (each with its falsifier; details in SCIENTIFIC_EXPERIMENTS.md)

- **H1 (calibration).** HYPOTHESIS: fused, coherence-projected forecasts from three independent LLM researchers plus Jev triage have lower Brier and log loss than (a) the best single LLM, (b) the Design-C base-rate model, on prospectively registered milestone events. Falsified if the committed e-process versus baseline (b) stays below 1/α after 300 resolved events, or if any single model beats the fusion by ≥ 0.01 Brier with e-value ≥ 20.
- **H2 (economic).** HYPOTHESIS: after-cost long-horizon returns of the certified book exceed a cash benchmark, an equal-weight global equity ETF benchmark, and a random-selection control with identical position sizing. **Not evaluable within 12 months at $1,000**; evaluated in shadow (paper) with a $100,000 notional over ≥ 5 years, reported with bootstrap confidence intervals.
- **H3 (Jev).** HYPOTHESIS: Jev triage reaches ≥ 0.8 recall of rare useful leads at ≤ 20 percent of the cost of LLM triage without degrading downstream calibration. Falsified by the randomized ablation in experiments §5.
- **H4 (certificates).** Statement, not hypothesis: a certified order plan has zero logic / budget violations *in the certified model*. Lean theorems in `proofs/` are compiled on a pinned toolchain; this says nothing about data or model risk.
- **H5 (discovery lead time).** HYPOTHESIS: the first-principles scanner registers candidate events a median ≥ 60 days before the first sell-side or mainstream-media mention of the same mechanism. Measured by a dated "first external mention" field resolved by a separate search process.
- **H6 (crisis policy).** HYPOTHESIS: the hazard-driven throttle reduces maximum drawdown relative to always-invested by more than its false-alarm cost over the crisis backtest set. If falsified, the throttle is removed and only thesis-break sells remain.

Rare-event (10x/100x) calibration is explicitly **out of scope for statistical validation in years 1 and 2**; only discrimination (ranking) of such candidates is measured.

---

## 2. System overview

```
Sources (filings, registers, standards bodies, procurement, patents, trials, permits, demographics, prices)
   │  ingest log: observer-signed first_observed_at, archived bytes, sha256, publication lag table
   ▼
Jev triage (mandatory): dated-primary? relevant-to-which-registered-mechanism? duplicate? contradiction?
   │  gap-checked noul pairs; escalation score
   ▼
Three independent researchers (Claude, OpenAI, Gemini), round 1 blind
   │  typed PCCB fragments: mechanism (with identification class), events (EventSpec), interval forecasts
   ▼
Coherence layer: credal network (Design B) for the research graph; LP certificate (Design A) on ≤14 decision events
   │  fused intervals (correlation-aware), abstain / re-research decisions
   ▼
Registry + anchored ledger (commit before outcome) ──► e-process monitors, calibration maps, ablations
   │
   ▼
Value-capture model → scenario set → robust allocation (max-min log growth, caps, worst-loss) → certificate
   │
   ▼
Gate state machine → Saxo SIM read-only → precheck → (SIM execution) → (shadow live quotes) → [LIVE blocked]
```

Three principals with separate OS users and secrets: **Researcher** (all LLM/Jev code; no broker secrets), **Promoter** (frozen holdouts, acceptance script; read-only on code), **Executor** (broker tokens, order signing; no LLM access). The owner is a fourth principal who holds the gate HMAC secret and the ledger anchor store.

---

## 3. Data layer

### 3.1 Ingest log (replaces self-declared timestamps)

Every document D gets a record `{doc_id, source_url(https), archived_sha256, archived_bytes_path, published_at(source-declared), first_observed_at(observer clock, signed), observer_id, fetch_headers_digest, language, parser_version, extraction_uncertainty}`. `available_at := max(published_at, first_observed_at)` and is computed, never supplied. The observer clock is NTP-disciplined and its drift logged daily. Corrections/revisions create a new `doc_id` with `supersedes` pointer; forecasts cite the version they used.

### 3.2 Publication-lag table

Per source family, the typical delay between the event and public availability (e.g. SLOOS quarterly with ~1-month lag; EDGAR same day; FDA 510(k) weekly batch; EU procurement TED daily). Backtests MUST shift every series by its documented lag and use vintage data where it exists (ALFRED for FRED). Sources without a lag entry MUST NOT be used in backtests.

### 3.3 Point-in-time universe (Wald test)

A monthly snapshot of the investable universe at Saxo (from `/ref` readback once SIM_READ_ONLY is reached; historical reconstruction from a licensed PIT dataset is an OPEN QUESTION, Q5): every listing incl. later bankruptcies, delistings, reverse splits, acquisitions. Every candidate the scanner ever touched is written to the ledger with `considered_at`, decision (`invest | reject | uninvestable | watch`) and reason. Shadow books: `no_exit_shadow` for every exit, `entry_shadow` for every rejection with a thesis, `random_control` matched by date and sizing.

---

## 4. Forecast and coherence layer

### 4.1 EventSpec and Forecast (implemented in `cpe/registry.py`)

A forecast is `P(event E resolves YES by expires_at)` where E has: statement, `resolution_source` (named database or document class), `resolution_predicate` (machine-checkable rule text, versioned), `resolves_not_before`, `expires_at`, `grading_rule_version`. Vague predicates (`potential`, `could`, `might`, `significant`, `strong`) are rejected. Forecasts carry `as_of` (information cutoff), `known_at` (wall-clock), interval `[p_low, p_high]`, forecaster + version, evidence ids, reasoning digest, `abstained`. Width > 0.5 is recorded as abstention. Status: COMMITTED → RESOLVED_YES / RESOLVED_NO / EXPIRED_NO / VOID. VOID rate per source is a monitored metric; VOID is never silently dropped.

### 4.2 Mechanism objects with identification class

`Mechanism {id, cause_event, effect_event, direction, identification_class ∈ {natural_experiment, instrument, policy_variation, dose_response, none}, exogenous_variation_description, swa_assumptions[], primary_sources[], counter_mechanisms[], substitutes[]}`. Only `logical` links (A ⊆ B by definition, e.g. "revenue > X" ⇒ "revenue > Y" for X > Y, or "approval granted" ⇒ "application filed") enter the LP as constraints. Mechanisms with class `none` enter the narrative and the event decomposition only. This is the formal boundary between "causal reasoning as hypothesis generation" and "probability math".

### 4.3 Design B: credal network for the research graph

Nodes = EventSpecs; edges = mechanisms; each researcher supplies conditional intervals `P(child | parent configuration) ∈ [l,u]` only for configurations they can justify, else abstain. Inference: sample CPTs uniformly within intervals (M = 2,000 draws), propagate, report the interval of the target marginal as [5th, 95th] percentile across draws plus the envelope. Complexity O(M · edges). Dependence between researchers' CPT errors is handled in the fusion layer before sampling (fused intervals per edge). HYPOTHESIS: this is better calibrated than Design A on graphs with > 14 nodes; tested by ablation.

### 4.4 Design A: LP certificate on the decision projection

For the ≤ 14 events that appear in the value-capture model, run `coherent_joint` / `event_probability_bounds` with logical constraints; the certificate records the LP bounds. The reference distribution used for scenario weights is the **max-entropy** feasible distribution (or min-KL to the Design-C prior), computed by a separate convex solve and labelled as an estimator; the raw LP vertex MUST NOT be used (finding P1-COH-02).

### 4.5 Design comparison (pre-registered selection criteria)

| Criterion | A: Credal LP | B: Credal network | C: Base-rate baseline |
|---|---|---|---|
| Scales to research graphs | No (2^n) | Yes | n/a |
| Uses conditional information | No | Yes | No |
| Certifiable in Lean | Yes (bounds, implications) | Projection only | No |
| Learns calibration | No | Yes (leaf maps) | Yes |
| Risk of vacuous intervals | High for n > 8 | Moderate | Low |
| Role in v0.2 | Certificate layer | Research engine | Mandatory baseline |

Selection after 150 resolved events by Brier/log skill and interval coverage; the losing design is kept as an ablation arm for one more cycle, then retired.

### 4.6 Rare probabilities (< 5 percent)

MUST NOT elicit point probabilities < 0.05 from LLMs or Jev. Decompose into a chain whose links are in [0.1, 0.9] where possible; derive the rare target interval from the network; floor the lower bound by the Design-C cohort base rate with cohort size n reported; report `[p_low, p_high, n_cohort]`. Evaluate rare targets by discrimination only until ≥ 50 resolutions per probability bin exist.

### 4.7 Fusion (implemented in `cpe/fusion.py`)

Inputs: three intervals + Jev triage record. Weights `w = R⁻¹1 / (1ᵀR⁻¹1)` from the shrunk error-correlation matrix of past standardized errors; fallback to equal weights with a flag; fused interval = convex combination; `effective_models = (Σw)² / (wᵀRw)`. Decisions: `FORECAST`, `ABSTAIN` (spread > 0.30 or width > 0.35 or any abstention), `RE_RESEARCH` (missing input, Jev incoherent, evidence not dated-primary or not relevant). Thresholds are pre-registered constants; changing them is a promoter action logged to the ledger. Round 2 (adversarial cross-examination) runs only for ABSTAIN items and produces new forecast ids, never edits.

---

## 5. Model roles and contracts

| Role | Claude Fable 5.1 | OpenAI (Astra class) | Gemini (Argon class) | Jev |
|---|---|---|---|---|
| Mandatory round-1 output | mechanisms + decomposition + intervals, ticker-free | adversarial reconstruction, counterexamples, Lean sketches, intervals | alternative futures, substitutes, value-capture, intervals | triage noul pairs, choice classification, duplicate clustering |
| Forbidden | reading other models' round-1 output; tickers before mechanism | broker orders | broker orders | anything but classification; any broker or account data |
| Calibration tracked | per forecaster, per horizon, per sector, per source family | same | same | per question template; complement gap per call |
| Veto | any model may ABSTAIN → item goes to round 2 | same | same | incoherence gap > 0.15 → RE_RESEARCH |

Adapter contract (provider-independent): `research(bundle) -> ResearchOutput` with typed JSON validated against a schema, three retries with exponential backoff, hard per-day token ceilings per provider, degradation ladder {full → cheaper model for round 1 → queue}, and the rule that a **missing mandatory pre-trade input freezes new orders** (gate demotes to SIM_READ_ONLY automatically). Prompts in `prompts/` remain the round-1 instructions; they MUST be versioned and their hash recorded in every forecast.

Access routes and budget: see CLAUDE_REVIEW §8 and OPEN_QUESTIONS Q2.

---

## 6. Value capture, allocation and risk limits

### 6.1 Value-capture model

For each thesis: revenue/margin/capital-intensity/share-count paths under the scenario set; total shareholder return multiple R_k per scenario after estimated dilution, after Saxo commissions and spread (from precheck `Cost`), after FX (CHF/USD, instrument currency) and after an owner-supplied tax assumption. A large market is not a large return to today's holders: the model MUST state the implied entry multiple and the required terminal multiple.

### 6.2 Allocation (implemented in `cpe/allocation.py`)

`max_w min_{q∈Q} Σ_k q_k log(1 + R_k·w)` with w ≥ 0, Σw ≤ gross_cap, w_i ≤ cap_i, worst-scenario loss ≤ max_loss; then `w ← f·w` with fractional Kelly f = 0.5. Q is the vertex set of the LP credal set or a hand-specified stress set; scenarios encode dependence (macro regime × thesis outcome). Derivation notes: binary case reduces to `w* = −(p a + (1−p) b)/(a b)` (verified); using p_low is justified by `growth_min_at_lower_bound` (Lean); estimation error in p is handled by the interval, not by an additional shrink; correlated tails only through scenarios; path dependence, margin and option exercise are **not modelled**, hence the pilot instrument whitelist.

### 6.3 Pilot risk limits (LIVE_CAPPED_1000, when and if ever enabled)

- Instruments: `Stock, Etf, Bond, MutualFund` only, fully paid, `tradable` confirmed from `/ref` readback; no CFD, FX, options, futures, no short.
- Gross exposure cap 100 percent of pilot capital; per-position cap 20 percent (≤ $200); minimum ticket such that commission ≤ 1 percent of ticket (Saxo commission schedule is account-dependent, OPEN QUESTION Q6); max 8 positions; cash floor 10 percent.
- Worst-scenario loss per position ≤ 15 percent of pilot capital (R_k ≥ −0.75 assumption for fully paid equity; bankruptcy scenario explicit).
- Turnover: target median holding period > 12 months; hard cap 24 round-trips per year (Swiss professional-trader classification risk, CLAUDE_REVIEW §6).
- Diversify sources of risk, not tickers: ≤ 40 percent of exposure sharing the same first-order mechanism; ≤ 50 percent in one currency other than CHF/USD.
- Data staleness: no precheck/order if the instrument quote age > 15 minutes or the gate heartbeat is older than 5 minutes.

### 6.4 Risk-of-ruin reporting

Monthly Monte Carlo over the scenario sets: P(drawdown > 50 percent within 5 years), expected shortfall 5 percent, probability of reaching 10x in 10 years under the model. Reported as model outputs with the inputs' provenance; never as promises.

---

## 7. Crisis and recovery policy (ex-ante, not reactive)

Inputs (all with publication-lag entries): HY OAS level and 3-month change; SLOOS net tightening; 3m-10y curve; NFCI; VIX 1m/3m term-structure ratio; equity breadth (percent above 200-day); funding stress (FRA-OIS or equivalent, source to be chosen). Model: Bayesian online change-point or logistic hazard on 6-month forward drawdown > 15 percent, trained on vintage data, outputs a hazard distribution with calibration interval. Actions, with hysteresis (enter at hazard upper band, exit at lower band, minimum dwell 30 days):

1. Hazard HIGH: throttle new buys to zero, raise cash floor to 30 percent via *not re-investing* and via exits that are independently thesis-justified; never forced liquidation of thesis-intact positions.
2. Thesis break (registered event resolves NO on a load-bearing node, or a counter-mechanism event resolves YES): sell regardless of price regime.
3. Price-only drawdown without thesis change: no action; logged for the "late exit" audit.
4. Re-entry: when hazard exits the lower band, resume buys at half speed for 60 days.

Metrics: fraction of protective actions that occur after > 50 percent of the eventual drawdown; rebound missed; false-alarm cost; always-invested benchmark. Backtest episodes: 2000-02, 2007-09, 2011, 2015-16, 2018 Q4, 2020, 2022, plus any 2024-26 episode with vintage data. Statement of limits: the system does not predict crashes; it reduces exposure when leading stress indicators are elevated and accepts the false-alarm cost measured by H6.

---

## 8. Self-improvement loop

- **Proposer** (any model, any time): proposes a versioned artifact (feature extractor, parser, graph template, exit rule, prompt) with a pre-registered claim and the holdout it should improve.
- **Promoter** (separate OS user, deterministic script): evaluates on hash-pinned frozen holdouts (`holdouts/<name>.sha256` listed in the ledger), time-shifted holdouts, shuffled-label controls and canary events; accepts only if the committed e-process versus the incumbent crosses 1/α (α = 0.05, pre-registered, one test per artifact) and no control is violated; writes `promotion` or `rejection` to the ledger; keeps rollback.
- **Immutable by the loop:** risk limits, gate state, broker permissions, evaluation datasets, ledger, fusion thresholds.
- **Never an input:** live P&L of the $1,000 account.

---

## 9. Security architecture

- Secrets: Saxo app key/secret, refresh tokens, Jev key, LLM keys in the Windows Credential Manager (DPAPI) under the Executor / Researcher user respectively; never in `.env` files inside the repo; never in prompt context; redaction filter on all LLM-bound text (`jev_adapter` already refuses credential-like strings).
- Order signing: the Executor process accepts only a certificate `{certificate_id, instrument, amount, limit, gate_state, ledger_head_hash, promoter_signature}`; it re-verifies the ledger anchor and the gate before any precheck; research code cannot import the executor module (enforced by separate venv and user).
- Ledger anchoring: daily `anchor()` written to a second physical location the Researcher user cannot write (owner's cloud drive or a separate machine); monthly owner verification from an independent machine; optional external timestamping (OpenTimestamps or signed git tags; UNVERIFIED as services).
- Egress: Researcher user allow-list = {api.anthropic.com, api.openai.com, generativelanguage.googleapis.com, api.typesafe.ai, data sources}; Executor allow-list = {gateway.saxobank.com, sim.logonvalidation.net, live.logonvalidation.net}. Windows Firewall per-user rules or a local proxy.
- Idempotency: `ExternalReference = certificate_id`, fresh `x-request-id` per attempt, no retry on `TradeNotCompleted` without a `/port` readback.
- Emergency: `Gate.demote()` callable from a CLI and from a watchdog on heartbeat loss; cancels nothing by itself (no cancel code exists yet) but blocks all new prechecks/orders.
- Audit: every HTTP call to Saxo logged with digest of body, status, latency, never the token.

---

## 10. Saxo gate specification

| State | Allowed calls | Promotion evidence bundle |
|---|---|---|
| RESEARCH_ONLY | none | n/a |
| SIM_READ_ONLY | `/port/v1/accounts/me`, `/port/v1/balances`, `/port/v1/positions`, `/port/v1/orders`, `/ref/v1/instruments`, `/ref/v1/instruments/details` (paths to be confirmed against reference docs at implementation; the learn pages verified do not list them individually) | 7 days of successful readbacks, reconciliation report |
| SIM_PRECHECK | plus `POST /trade/v2/orders/precheck` with pilot whitelist | 30 prechecks across ≥ 10 instruments, cost fields archived |
| SIM_EXECUTION | plus SIM `POST /trade/v2/orders` with `ManualOrder:false`, `x-request-id`, `ExternalReference` (code not yet written) | 60 days, zero duplicate orders, reconciliation of every fill to a certificate |
| SHADOW_LIVE_QUOTES | LIVE read-only app, no write scopes | 90 days shadow book vs benchmarks |
| LIVE_CAPPED_1000 | blocked in code; requires separate release + external risk gate | independent security review |

Promotion is one step at a time with an owner HMAC over `(from, to, evidence_bundle_sha256)`; demotion is unrestricted.

---

## 11. Changes from v0.1 (exact)

| Area | v0.1 | v0.2 |
|---|---|---|
| Forecast object | `BinaryThesis` free text | `EventSpec` + `Forecast` registry, ledger-backed, vague-word guard |
| E-process | `ChallengerEvidence(p_b, p_c, y)` | `CommittedEProcess.commit()/resolve()`, predictable λ, λ_max < 1, running max |
| Ledger | hash chain | + `seq`, monotone time, anchors with HMAC, threat model |
| Coherence | LP, guard only in one function | guard in both; vertex not used downstream; credal network design added |
| Allocation | binary Kelly, cost-unit bug | fixed units; scenario max-min allocator with caps and worst-loss |
| Fusion | none | correlation-aware weights, abstention, Jev gating |
| Jev | TS sketch | Python typed adapter, schema-verified, complement gap, retries, ceilings |
| Saxo | precheck with `ManualOrder` and free-text asset type | gate machine, whitelist, `ExternalReference`, `x-request-id`, tradability from readback, token-safe errors |
| Lean | uncompiled, 3 trivial theorems | compiled on pinned toolchain; + 7 lemmas the allocator and LP rely on |
| Evidence | `http` ok, digest unchecked | `https` only, digest helper, ingest-log spec |
| Tests | 11 | 31 |
