# CLAUDE_REVIEW.md: Independent review of Causal Proof Engine v0.1

**Reviewer:** Claude (Fable 5.1), acting as independent scientific / security / financial-research reviewer and co-designer.
**Date:** 2026-10-16. **Input:** `CPE_Claude_Independent_Review_2026-10-16.zip` (manifest verified, all 20 SHA-256 digests match).
**Scope:** everything in `source_v0_1/`, `INDEPENDENT_AUDIT_FINDINGS.md`, `REVIEW_SCORECARD.csv`, plus external verification of Saxo, TypeSafe Jev, Lean/Mathlib and model-access terms.
**Written for cross-review by an OpenAI reasoning model; every external claim carries a dated source or is marked UNVERIFIED.**

---

## 0. Executive decision

**Decision: REVISE. Do not approve for any capital, including the $1,000 pilot. Do not reject the program.**

Reasoning in one paragraph. v0.1 is an honest research skeleton (its README says so) and its arithmetic is correct where it exists. But it contains no element that could produce an investment edge today: no data, no forecasts, no calibration history, no model adapters, no broker read access, no causal identification, and a ledger and e-process whose APIs cannot distinguish prospective from hindsight entries. Four of the system's load-bearing claims are currently unfalsifiable because the measurement apparatus is missing. The right response is to build the measurement apparatus first (forecast registry, anchored ledger, committed e-process, fusion with abstention, SIM read-only), run it for 6 to 12 months on hundreds of short-horizon registered events, and only then ask whether the "10x before trend acceleration" hypothesis is testable at all. I have produced that apparatus as a tested v0.2 patch (31 tests pass, Lean files compile on a pinned toolchain).

**Hard statements the owner should accept now:**

1. The novel advantage (coherent multi-model causal forecasts beating single-model and base-rate baselines on *10x/100x* events) **cannot be statistically demonstrated within 12 months.** Rare-event calibration needs on the order of hundreds of resolved rare events; a 10-year 10x event resolves in 10 years. What *can* be demonstrated in 12 months is forecast skill on 1-to-9-month milestone events (regulatory decisions, certifications, capacity commissioning, contract awards), Jev triage recall, and operational integrity in SIM. The spec and experiment plan are re-scoped to that.
2. The economic hypothesis (H2) **cannot be evaluated on a $1,000 live book.** With a concentrated small-cap book of annualized volatility 40 to 60 percent, one year of returns has a standard error far larger than any plausible alpha. The pilot validates plumbing, not alpha. Forecast scores, not P&L, are the primary metric for years 1 and 2.
3. The 4,000 to 400,000 USD target implies 58.49 percent CAGR with all capital invested from day zero (100^(1/10) = 1.5849, confirmed). With $1,000 deployed in year one and $3,000 held back, the required CAGR on deployed capital is higher. This is a tail aspiration; nothing in this review supports treating it as an expectation. Capital ruin is a live possibility under any policy that could plausibly reach it.
4. "Hands-off" has a broker-side constraint that no software can remove: Saxo OpenAPI sessions are issued through OAuth with short refresh lifetimes in the documented example (`expires_in: 1200`, `refresh_token_expires_in: 2400` seconds; source: https://www.developer.saxo/openapi/learn/oauth-authorization-code-grant-pkce, read 2026-10-16). Whether a long-lived unattended session is possible for an individual LIVE app is **UNVERIFIED** and is the single most important account-dependent question (OPEN_QUESTIONS Q1).
5. Subscription-only unattended access to all three LLMs is **partially possible, not fully.** Verified 2026-10-16: Anthropic Max plans include monthly Claude Platform API credits ($100 on Max 5x, $200 on Max 20x) usable with the Agent SDK and Messages API, and `claude -p` still draws on subscription limits (support.claude.com articles 15036540 and 17154008). OpenAI documents API keys as the route "for programmatic Codex CLI workflows, such as CI/CD" and restricts "access tokens for trusted automation" to Enterprise workspaces (https://learn.chatgpt.com/docs/auth). Gemini CLI quotas for Google AI Pro (1,500 requests/day) and Ultra (2,000/day) are published for personal accounts but headless use is not addressed (https://geminicli.com/docs/resources/quota-and-pricing/). Budget estimate in §8.

---

## 1. What was actually reproduced (evidence in `EVIDENCE/`)

| Item | Result | Evidence file |
|---|---|---|
| Manifest | 20/20 SHA-256 match | shell `sha256sum -c MANIFEST.sha256` |
| v0.1 tests | `11 passed` (Python 3.13.16, scipy 1.18.1, httpx 2.13.0) | `pytest_v01.log` |
| Ledger full-rewrite attack | `verify_chain()` returns **True** after rewriting a forecast and re-hashing (tamper NOT detected) | `attack_v01_output.log` F1 |
| E-process hindsight entry | API accepts challenger probability chosen after the outcome; same outcome can be fed 20 times (e-value 9.6) | F3, F5 |
| E-process absorbing zero | `betting_fraction=1` yields e-value 0 forever after one wrong call | F4 |
| Kelly FOC | `w* = 0.025` at p=0.10 and `0.0522` at p=0.12 confirmed numerically; threshold 4/49 confirmed | F6 |
| Cost-unit mismatch | growth (log units) compared with cost *fraction*; equal only to first order | F6 |
| Coherence scaling | 14 events = 16,384 worlds, 0.34 s; `event_probability_bounds` had **no** n≤14 guard | F7 |
| LP picks arbitrary vertex | KL/proper-score reference distribution from RFC §1 not implemented | F8 |
| Evidence provenance | `http://` accepted, digest not derived from content | F9 |
| Precheck payload | accepts `AssetType='NotAnAssetType'`, `Amount=0.0001`, `OrderPrice=1e-9` | F10 |
| **Lean** | `BetThreshold.lean` **compiles and checks** on Lean `v4.35.0` + Mathlib `cfc55fc5…` (standard axioms only); negative control (false theorem) fails as expected. The "NOT COMPILED" label can be removed; the content remains trivial algebra. | `lean_compile.log` |
| v0.2 patch | `31 passed` | `pytest_v02.log` |

---

## 2. Findings (P0 = blocks any capital or invalidates the science; P1 = must fix before SIM execution; P2 = should fix)

Format: ID, severity, location, what is wrong, reproducible proof, fix, owner. "Owner" is Salah unless a vendor is named.

### P0

**P0-SCI-01: No forecast object exists; nothing can be graded.**
`core.py:43-66` `BinaryThesis` has `success_definition: str` free text and a probability interval, but no `known_at`, no resolution source, no grading rule, no expiry semantics, no forecaster identity per interval. "10x potential" would validate. Proof: `BinaryThesis(..., success_definition='10x potential', ...)` passes `validate()`.
Fix: `cpe/registry.py` (v0.2) with `EventSpec` (statement, resolution source, machine-checkable predicate, `resolves_not_before`, `expires_at`, grading rule version; vague-wording guard) and `Forecast` (as_of, known_at, interval, forecaster, abstention, reasoning digest), ledger-backed, immutable ids, late forecasts rejected. Test `test_registry_rejects_vague_and_non_prospective`.

**P0-SCI-02: "Causal" is logical implication only; no identification strategy anywhere.**
`coherence.py:53-58` constraints are `A ⇒ B` world filters. This is de Finetti/Nilsson probabilistic-logic coherence (Nilsson 1986, "Probabilistic logic"), not causal inference. No interventions, instruments, natural experiments, or event-study design appear in code or RFC beyond prose. An LLM asserting "regulation ⇒ demand" is a correlation-or-narrative claim.
Fix (spec §4): split the graph into (a) *logical* constraints (used by the LP, certified by Lean `implication_prob_le`), (b) *mechanistic* claims each tagged with an identification class {natural experiment, instrument, dose-response, RCT-like policy variation, none} and a dated primary source, and (c) a rule that only (a) enters probability math; (b) enters the research narrative and the *event decomposition*. Edge is tested on event forecasts, not on the truth of the DAG.

**P0-ARCH-01: Three-model committee and Jev are absent; the only adapter is a TypeScript sketch.**
`adapters/jev_example.ts` is not executed, has no schema validation, no retries, no timestamps. No Claude/OpenAI/Gemini code. Proof: `grep -r "anthropic\|openai\|gemini" cpe/` returns nothing.
Fix: `cpe/fusion.py` (mandatory three intervals + Jev triage, correlation-aware min-variance weights, effective-model count, typed abstention / re-research) and `cpe/jev_adapter.py` (schema verified against live `openapi.json`, complement-pair coherence measurement, retries, cost ceiling, credential-leak guard). Adapters for the three LLMs remain to be written against the access routes in §8; their *contract* is fixed in spec §5.

**P0-BRKR-01: No SIM read access; precheck is the only call and it is unguarded by state.**
`saxo_sim.py:41-50` posts to precheck with a bearer from env; nothing prevents calling it from research code. No `/port` readback, no `/ref` instrument readback, no reconciliation.
Fix: `Gate` state machine (`RESEARCH_ONLY → SIM_READ_ONLY → SIM_PRECHECK → SIM_EXECUTION → SHADOW_LIVE_QUOTES → LIVE_CAPPED_1000`), one-step promotion only with HMAC owner authorization, LIVE promotion hard-blocked in code, kill-switch demotion open to anyone. `sim_precheck` requires `SIM_PRECHECK`. Tests `test_gate_promotion_requires_owner_and_blocks_live`, `test_precheck_payload_whitelist_and_gate`.

**P0-STAT-01: E-process API cannot enforce its own validity conditions.**
`core.py:150-160` takes `(baseline_probability, challenger_probability, outcome)` in one call: no commitment time, no event id, no resolution window, static λ, λ=1 allowed. Proofs F3, F4, F5.
Fix: `cpe/eprocess.py` `CommittedEProcess`: `commit()` before `resolve()`, immutable forecasts, duplicate rejection, resolution not before declared window, predictable λ from past increments only (GRAPA-style, clipped to λ_max<1), running-max rejection (valid by Ville). Monte Carlo test shows false-alarm rate ≤ α under the null and power under a true improvement.

### P1

**P1-LEDGER-01: Hash chain is rewritable.** `ledger.py:36-47`. Proof F1. Fix: `seq`, monotone `written_at`, `anchor()` / `verify_against_anchor()` with optional HMAC; threat model T1-T5 documented in module docstring. Anchors are only meaningful if stored outside the writer's reach (second disk/account, signed git tag, OpenTimestamps; the latter UNVERIFIED as a service, listed as an option). Test `test_full_rewrite_detected_with_anchor`.

**P1-COH-01: Exponential enumeration; missing guard.** `coherence.py:76-100`. Fix applied (guard). Structural fix in spec §4.3: credal network / factored inference for the research graph, LP only for the ≤14 decision-relevant events.

**P1-COH-02: LP returns an arbitrary vertex (F8); downstream code could mistake it for "the" distribution.** Fix: only use `event_probability_bounds` output (interval) downstream; the reference distribution (max-entropy or min-KL to a base-rate prior) is a separate, clearly labelled estimator (spec §4.4). Not implemented in v0.2 code; marked TODO.

**P1-RISK-01: Single binary Kelly.** `core.py:95-128`. Correct for its model; `p_success_high` unused; no portfolio, no correlation, no costs beyond a fixed fraction; cost unit mismatch (fixed in patch). Fix: `cpe/allocation.py` scenario-based max-min log growth over a finite credal set with gross cap, per-position caps, hard worst-scenario-loss constraint, fractional Kelly. Test reproduces 0.025 in the binary case. Still a toy for options/path dependence; the pilot whitelist excludes those instruments so the toy is sufficient for the pilot.

**P1-RISK-02: No crisis / re-entry policy in code.** Spec §7 specifies hazard inputs that are knowable in real time, hysteresis, thesis-break vs price stops, false-alarm accounting, and the mandatory always-invested benchmark. Explicit statement: tactical timing evidence in the literature is weak; policy limits risk-off actions to *new-buy throttling and cash-cap changes*, never to forced liquidation of thesis-intact positions.

**P1-DATA-01: Self-declared timestamps.** `core.py:28-40`. Fix: `https` only, `evidence_digest(bytes)` helper, spec §3 ingest log (observer-signed `first_observed_at`, archived snapshot, publication-lag table per source, version/correction handling).

**P1-ACCESS-01: Unattended three-model access by subscription is only partially supported.** See §8.

**P1-SEC-01: Secrets and error paths.** v0.1 `response.raise_for_status()` raises `httpx.HTTPStatusError` carrying the request object (and therefore the bearer header) up the stack; a generic exception logger would persist it. Fix: `SaxoHttpError` re-raise without request object; token never logged. Remaining: OS keychain / DPAPI storage on Windows, separate order-signing process (spec §9).

**P1-SAXO-01: Payload fields not aligned with documented precheck request.** `ManualOrder` is not listed on the precheck reference page (read 2026-10-16); `ExternalReference` (≤50 chars) exists and was unused; the duplicate-protection mechanism is the `x-request-id` header on placement ("exactly the same order within 15 seconds without specifying a different x-request-id header will be rejected", https://www.developer.saxo/openapi/learn/order-placement). Fix applied in payload builder.

### P2

**P2-CORE-01** cost-unit mismatch (fixed). **P2-EVID-01** URL/digest shallow (partly fixed; archive layer in spec). **P2-INSTR-01** free-text `asset_type` (fixed: pilot whitelist `Stock, Etf, Bond, MutualFund`; `tradable` must come from `/ref` readback). **P2-TEST-01** 11 tests ≠ working system (agreed; now 31, still not a working system). **P2-LEAN-01** "NOT COMPILED" header now false; replaced with pinned-toolchain note; theorems remain trivial (`linarith`) and prove nothing about markets. Added `RiskBudget.lean` with the lemmas the allocator actually relies on (worst case at lower bound, cap ⇒ bounded loss, sum of caps ⇒ budget, implication ⇒ P(A) ≤ P(B), e-process factor nonnegativity).

---

## 3. Mandatory investigation A: originality and edge

**What is established algorithm vs novel integration hypothesis.**

| Component | Status | Reference (general knowledge unless dated) |
|---|---|---|
| Credal set via LP over world states | Established (probabilistic logic; imprecise probability) | Nilsson 1986; Walley 1991 |
| Logical implication ⇒ marginal ordering | Trivial; now Lean-checked | `RiskBudget.lean` |
| Test supermartingale with predictable λ | Established | Ramdas et al. 2020 (arXiv:2009.03167, title verified via arXiv API 2026-10-16) |
| Fractional / robust Kelly | Established | Kelly 1956; MacLean, Thorp, Ziemba 2010 |
| Proper scoring, reliability diagrams | Established | Brier 1950; Gneiting & Raftery 2007 |
| Jev typed decisions | Vendor product (released 2026-09-15, $0.042/MTok input, output free per vendor blog; independent evaluations arXiv:2609.37647 and 2609.33209 exist, titles verified) | see §6 |
| **PCCB as a typed object joining the above** | **Novel integration hypothesis, untested** | RFC §0 |
| **Claim: coherent multi-model causal decomposition improves calibration on pre-trend 10x events** | **Novel, untested, and not testable in 12 months at the 10x horizon** | this review |

**Is any causal link more than correlation or assertion?** In v0.1, no. The RFC's example chain (regulation → certification → capacity → profit → 10x) is a narrative with implications. To support a *structural* claim one needs: a specified intervention (what would change if the regulation were repealed?), an exogenous source of variation (staggered adoption across jurisdictions, court rulings, tariff shocks), the observed-world assumptions (no anticipation, SUTVA across firms, no simultaneous confounding policy), and an outcome measurable before price. Spec §4.2 makes the identification class a mandatory typed field and forbids identification-class `none` claims from entering probability constraints.

**Two competing designs for a proof-carrying, coherent, multi-model causal bet** (full comparison in spec §4.5):

*Design A, Credal-LP certificate (v0.1 lineage).* Marginal intervals + logical constraints → LP feasibility and bounds → max-min growth. Strengths: transparent, every step certifiable, contradiction detection. Weaknesses: exponential in events, vacuous intervals when many events are loosely constrained, ignores conditional structure, no learning.

*Design B, Factored credal network with calibrated leaves.* A DAG over events with *conditional* probability intervals per edge supplied by each model, inference by Monte Carlo over sampled CPTs (cheap, scales to hundreds of nodes), leaves calibrated against a historical cohort base-rate model (Design C) via isotonic/Platt maps learned only on resolved events; conformal-style intervals at the target. Strengths: scales, uses conditional information, learns calibration. Weaknesses: certification only of the final ≤14-node projection, structure must be elicited, dependence between CPT errors across models must be modelled (fusion layer).

*Design C, Base-rate hazard baseline (mandatory competitor).* No graph, no LLM: cohort base rates of milestone events and of 10x outcomes conditioned on observable firm characteristics at the as-of date, with conformal prediction intervals.

Recommendation: **B as the research engine, A as the certificate layer on the decision-relevant projection, C as the baseline that must be beaten.** Selection is by pre-registered ablation on Brier/log skill and discrimination, not by novelty.

**Probabilities below 5 percent.** Methodology (spec §4.6): never elicit a point estimate below 5 percent from any LLM or from Jev; decompose into a chain of conditional events each elicited in [0.1, 0.9] where possible; let the LP/credal net produce the implied interval for the rare target; floor the lower bound with the Design-C cohort base rate; report as an interval with the cohort n; within 12 months evaluate only *discrimination* (AUC, rank correlation) for rare targets, calibration only for events with ≥ 50 resolutions per bin.

**Joint distributions and tails.** Multiplying marginals is forbidden by construction (LP, or credal net sampling); multi-model error correlation is estimated and used in fusion weights (`effective_models` drops from 3 toward 1 when models agree for the same reasons, test `test_correlated_models_do_not_count_three_times`); source-induced errors are stress-tested by the "single-source ablation" in SCIENTIFIC_EXPERIMENTS §5.

**Shifting worlds, financing regimes, endogenous pricing.** Handled as explicit scenario axes in the allocation scenario set (rates/credit regime × thesis outcome), with the regime hazard model of spec §7 feeding scenario weights, and with the rule that a thesis whose value capture depends on continuous external financing is tagged `financing_dependent` and capped lower.

---

## 4. Investigation B: multi-model and Jev as primary

Verified Jev facts (live OpenAPI document https://api.typesafe.ai/openapi.json, title "TypeSafe", version 0.2.0, fetched 2026-10-16, saved as `EVIDENCE/typesafe_openapi_2026-10-16.json`): `POST /v1/systemone` with `{model, state, questions{name → NoulQuestion|ChoiceQuestion|ScoreQuestion|BoxQuestion}}`, bearer auth, response `{model, answers, usage{input_tokens, output_tokens}}`; `GET /v1/models` returns `{name, description, release_date}`; score questions carry an ordered rubric (≤10 levels) and return expected score plus per-level probabilities; choice cardinality ≤255. No origin-timestamp field exists; timestamps are the caller's responsibility (adapter records `requested_at`, `received_at`, returned `model`).

Independent evaluation (arXiv:2609.33209, abstract read 2026-10-16): on 480 complement pairs Jev's p(X)+p(not X) misses 1 by 0.064 on average (95% CI 0.055 to 0.072), about five times repeat-call noise, concentrated where it is uncertain. Consequence: Jev output is a classification signal with measurable incoherence, not a probability of investment success. The adapter asks every noul question in both polarities and records the gap; items with gap > 0.15 are routed to re-research (`FusionPolicy.max_jev_complement_gap`).

Mandatory responsibilities (spec §5): Jev = ingest triage (dated-primary-evidence check, event relevance, duplicate clustering, contradiction alarm, escalation), run on every ingested document; its outputs gate whether the three LLMs are invoked, so a missing Jev record blocks the pipeline (`fuse()` returns `RE_RESEARCH`). Ablation `minus Jev` replaces it with rules + a small local model (RTX 5090 allows a 7-14B classifier) at equal recall budget.

Disagreement protocol: independent round 1 (no cross-reading, enforced by separate prompts and no shared context), fusion with correlation-aware weights, abstain if midpoint spread > 0.30 or fused width > 0.35, round 2 adversarial cross-examination only for abstained items, no forecast ever produced by fewer than three models plus Jev.

---

## 5. Investigation C: self-improvement validity

Beyond the e-process fix: the spec separates *proposer* (any model may propose features, parsers, graph templates, exit rules) from *promoter* (deterministic acceptance script run by a separate OS user with read-only access to frozen, hash-pinned holdout sets; thresholds pre-registered; rollback by default). Reward hacking tests that would fail under hindsight tuning: (1) shuffled-label holdout must yield no improvement; (2) time-shifted holdout (challenger trained with data up to T must not beat baseline on events resolved before T − lag); (3) "canary" events with fabricated outcomes known only to the promoter; (4) e-process with λ computed from past only (already enforced). No optimization against the live $1,000 account: live P&L is not an input to any promotion criterion in the spec.

---

## 6. Investigation D: risk-of-ruin and crisis policy

Kelly audit: formula and threshold correct; using the lower bound is justified by monotonicity (Lean `growth_min_at_lower_bound`); parameter uncertainty in p already shrinks w via the lower bound; correlated tails handled by scenario set; stale data and liquidation risk handled by gate rules (no order unless quote age < threshold and instrument whitelisted); no margin, no options, no futures, no CFDs in the pilot. Explicit derivation and remaining gaps in spec §6.

Crisis: specify precursors knowable in real time (HY OAS level and 3-month change, SLOOS tightening net percentage with its publication lag, 3m-10y curve, NFCI, VIX term-structure inversion, breadth), hysteresis bands, and the rule set in spec §7. The backtest list (2000, 2008, 2011, 2015-16, 2018, 2020, 2022, 2025 if applicable) must use vintage data (ALFRED for FRED series); what *not* to predict: the date of the bottom, the magnitude of a drawdown, idiosyncratic frauds.

Swiss context (general knowledge, not legal advice, **verify with a Swiss tax adviser**): private investors' capital gains are generally tax-free, but the tax authority can classify an individual as a professional securities trader (ESTV Kreisschreiben Nr. 36) using criteria such as short holding periods, transaction volume relative to portfolio, use of leverage and derivatives beyond hedging; classification makes gains taxable income with social-security contributions. A high-turnover automated system raises this risk; the spec therefore sets a low-turnover design constraint (median holding period target > 12 months; no derivatives in pilot).

---

## 7. Investigation E: Saxo verification table (all read 2026-10-16)

| Claim | Verified? | Source |
|---|---|---|
| SIM base `https://gateway.saxobank.com/sim/openapi`, LIVE `https://gateway.saxobank.com/openapi`; auth `sim.logonvalidation.net` / `live.logonvalidation.net` | Yes | developer.saxo/openapi/learn/environments |
| One-day Developer-Portal tokens are SIM-only | Yes | same |
| "certain specific functionality such as reporting and market data are not available in SIM" | Yes | same |
| LIVE app requires at least one SIM app and a funded live account; evaluation mostly automatic | Yes | developer.saxo/openapi/learn/direct-clients-request-for-openapi-application-credentials-for-the-live-environ |
| PKCE: `/authorize`, `/token`, S256 required, example `expires_in 1200`, `refresh_token_expires_in 2400` | Yes (example values; policy not stated) | developer.saxo/openapi/learn/oauth-authorization-code-grant-pkce |
| Precheck request fields incl. `ExternalReference` ≤50 chars; `ManualOrder` not listed on precheck page | Yes | developer.saxo/openapi/referencedocs/trade/v2/orders/post__trade__precheck |
| `ManualOrder` semantics; automated = "generated and/or routed without human intervention"; field "will soon be made mandatory" | Yes | developer.saxo/openapi/learn/order-placement |
| Duplicate protection via `x-request-id` within 15 s; `TradeNotCompleted` handling | Yes | same |
| FX Options not tradable via OpenAPI | Yes | same |
| Multi-leg precheck endpoint `/trade/v2/orders/multileg/precheck` | **UNVERIFIED** (only a navigation link seen) |: |
| SIM delayed market data after linking a live account (help article dated 2026-09-07) | **UNVERIFIED** (not fetched) | openapi.help.saxo article 4416934146449 |
| OpenAPI availability and permissions for Saxo Bank (Schweiz) AG retail clients | **UNVERIFIED, account-dependent** |: |
| Long-lived refresh / unattended session for individual LIVE app | **UNVERIFIED** |: |

No Saxo connector is installed in this session; no account data was accessed.

---

## 8. Investigation on access and cost (read 2026-10-16)

| Model | Route | Verified status | Monthly cost basis |
|---|---|---|---|
| Claude | Max plan + monthly Platform API credits via Agent SDK / Messages API; `claude -p` against subscription limits | Verified: Max 5x $100/month credits, Max 20x $200/month, no rollover, not usable for interactive Claude Code; claimable after 7 days on plan (support.claude.com/en/articles/17154008, update dated 2026-10-07; article 15036540) | Max 5x list price plus $0 extra up to the credit; API overflow at list token prices |
| OpenAI | Codex CLI/SDK included in Plus/Pro; API key "for programmatic Codex CLI workflows, such as CI/CD"; "access tokens for trusted automation" require an Enterprise workspace admin | Verified (learn.chatgpt.com/docs/auth, /docs/pricing). Unattended `codex exec` under a personal Plus/Pro login is **not documented as supported**; treat as policy-gray and plan API-key fallback | Plus or Pro subscription; API fallback at list prices |
| Gemini | Gemini CLI with Google AI Pro (1,500 req/day) or Ultra (2,000 req/day), personal accounts; API key free tier 250 req/day Flash only | Verified quotas (geminicli.com/docs/resources/quota-and-pricing); headless use not addressed; note "Gemini CLI was replaced by Antigravity CLI on June 18th, 2026" for unpaid and Google One users, effect on AI Pro **UNVERIFIED** | AI Pro subscription; API fallback at list prices |
| Jev | API key, early access waitlist | Verified pricing $0.042/MTok input, output free (typesafe.ai blog 2026-09-15); rate limits not stated | At 2 billion input tokens/month ≈ $84; negligible |

Budget estimate (assumptions stated, not quotes): subscriptions roughly $140 to $330 per month depending on tiers (Max 5x or 20x; ChatGPT Plus or Pro; Google AI Pro). Research volume assumption: 200 ingested documents/day through Jev (≈ 2 k tokens each = 0.4 M tokens/day, ≈ $0.50/month), 20 full three-model research rounds/day at ≈ 150 k tokens per model per round = 9 M tokens/day/model. At that volume the Claude credit ($100 to $200) covers only part of a month at Fable-class list prices; realistic unattended operation needs either lower volume (≈ 5 rounds/day), cheaper models for round-1 triage with Fable-class models only for adversarial round 2, or an API budget of several hundred dollars per month. **Conclusion: fully subscription-funded unattended operation of all three frontier models at research scale is not available; a mixed subscription-plus-metered budget of roughly $200 to $600/month is the realistic planning figure. This exceeds 20 percent per year of the $4,000 capital and must be treated as a research cost, not an investment cost.**

---

## 9. What would change my decision to APPROVE (for SIM_EXECUTION, not LIVE)

1. 300 or more registered events across ≥ 6 sectors with ≥ 150 resolved, fused forecasts beating Design-C base rates on Brier with the committed e-process crossing 1/α at α = 0.05, pre-registered.
2. Ablation showing the three-model fusion beats the best single model on log score with effective-model count > 1.5.
3. Jev triage recall of rare useful leads ≥ 0.8 at ≤ 20 percent of the cost of LLM triage, measured prospectively.
4. Ledger anchors verified monthly by the owner from an independent machine; zero anchor failures.
5. SIM read-only, precheck and reconciliation tests passing for 60 consecutive days with the gate at `SIM_PRECHECK`.
6. Answers to OPEN_QUESTIONS Q1-Q6.

LIVE_CAPPED_1000 additionally requires an independent security and risk review of the order-signing process; it is hard-blocked in the v0.2 code.

---

## 10. Immediate first step for the owner

Create the Saxo Developer Portal **SIM** application and obtain a one-day SIM token on the Windows machine; run the v0.2 test suite locally; then run the SIM read-only readback script (IMPLEMENTATION_SEQUENCE step 4) once and archive its output in the anchored ledger. Nothing else, and no LLM research pipeline, until that readback works.
