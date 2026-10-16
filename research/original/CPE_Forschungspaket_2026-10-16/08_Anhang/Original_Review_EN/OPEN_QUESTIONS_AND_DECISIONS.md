# OPEN_QUESTIONS_AND_DECISIONS.md

Date 2026-10-16. Items marked **blocking** must be answered before the gate leaves `SIM_READ_ONLY`.

## A. Evidence not available in this review

| # | Question | Why it matters | How to validate | Owner |
|---|---|---|---|---|
| Q1 (**blocking**) | Can an individual Saxo OpenAPI app keep an unattended session alive (refresh-token lifetime and rotation policy) for days/weeks? The PKCE page shows only example values (`expires_in 1200`, `refresh_token_expires_in 2400`). | Defines whether "hands-off" is possible on the broker side at all. | Step 5 of the implementation sequence: 72-hour unattended refresh test in SIM; ask Saxo OpenAPI support in writing. | Salah |
| Q2 (**blocking**) | Which of the three LLM providers permit unattended, scheduled use under the owner's subscriptions? Verified: Anthropic Max monthly API credits (Agent SDK/API); OpenAI documents API keys for programmatic workflows and Enterprise-only automation tokens; Gemini CLI personal quotas with headless use unaddressed, and a June 2026 "Antigravity CLI" replacement notice for some tiers. | Legality and continuity of the research pipeline; budget. | Read each provider's current terms page on the day of setup; keep dated screenshots in the ledger; default to API keys where terms are unclear. | Salah |
| Q3 | Does the Saxo precheck endpoint accept/ignore `ManualOrder`, and which `FieldGroups` values are valid? The precheck reference page does not list `ManualOrder` or enumerate `FieldGroups`. | Payload correctness. | First SIM precheck call (step 8) with and without the field; archive responses. | Salah |
| Q4 | Is `/trade/v2/orders/multileg/precheck` available, and for which exchanges? Only a navigation link was seen. | Options are excluded from the pilot anyway; relevant for later phases. | Reference docs at implementation time. | Salah |
| Q5 | Source of a point-in-time investable universe with delistings for backtests (licensed dataset vs reconstruction from Saxo `/ref` snapshots going forward). | Survivorship audit; Design-C base rates. | Price quotes from vendors; decide after Q1/Q2. | Salah |
| Q6 | Saxo Bank (Schweiz) AG retail entitlements: OpenAPI availability, commission schedule, minimum ticket sizes, FX conversion fees, which asset types are enabled on the account. | Pilot risk limits (commission ≤ 1 percent of ticket), instrument whitelist. | Account documents and the `/ref` + `/port` readback in SIM_READ_ONLY; no account data in AI chats. | Salah |
| Q7 | Does linking a funded live account to SIM provide delayed market data (help article dated 2026-09-07, not fetched here)? | Quote staleness gate in SIM. | Fetch and archive the article; test after linking. | Salah |
| Q8 | Jev early-access timing, rate limits, and whether `jev-latest` changes without notice (response `model` field is the version of record). | Mandatory component availability. | `GET /v1/models` daily; adapter already records returned model. | Salah / TypeSafe |
| Q9 | Swiss tax classification risk (professional securities trader) under an automated low-turnover design. | Could make gains taxable income plus social contributions. | Written opinion from a Swiss tax adviser before LIVE; design constraint already set (median holding > 12 months, no derivatives). | Salah |

## B. Critical assumptions and their validation

| Assumption | Validation |
|---|---|
| Milestone-event skill transfers to 10x-candidate discrimination. | Rank correlation between fused rare-target intervals and realized 3-year returns on the shadow book; reported from year 3; explicitly unproven before that. |
| Three LLMs are not merely three views of the same training corpus. | `effective_models` tracked monthly; if it stays < 1.5, the "independence" premise is false and the committee is reduced to one model plus adversarial prompts (cheaper) while keeping Jev. |
| Jev classification probabilities are stable enough to gate research. | Complement-gap and repeat-call noise measured on 200 fixed documents monthly. |
| Coherence projection improves calibration. | `−coherence` ablation. |
| Leading stress indicators reduce drawdown net of false alarms. | H6 crisis backtest on vintage data; if falsified, throttle removed. |
| Fully paid instruments at Saxo have bounded loss. | True by construction for Stock/ETF/Bond/Fund (loss ≤ paid amount); the allocator asserts `R ≥ −1`. |
| Ledger anchors are stored outside the research user's reach. | Monthly owner verification from a separate machine; CI fails if the anchor path is writable by the research user. |

## C. Decisions taken in this review (reversible by the owner)

1. Decision: REVISE, no capital, LIVE blocked in code.
2. Design B (credal network) as research engine, Design A (LP) as certificate layer, Design C as mandatory baseline; selection by ablation after 150 resolved events.
3. Fusion thresholds pre-registered: spread 0.30, width 0.35, Jev complement gap 0.15, Jev primary-evidence 0.60, relevance 0.50, shrinkage 0.30, min history 20.
4. E-process: α = 0.05, λ_max = 0.5, GRAPA-style predictable λ, running-max rejection.
5. Pilot whitelist: Stock, Etf, Bond, MutualFund; caps: gross 100 percent, per position 20 percent, max 8 positions, cash floor 10 percent, worst-scenario loss per position ≤ 15 percent of pilot capital, turnover cap 24 round-trips/year.
6. Rare probabilities (< 5 percent) are never elicited directly; derived by decomposition and floored by cohort base rates; evaluated by discrimination only for two years.
7. Year-one primary metric is forecast skill, not P&L; H2 runs as a 5-year shadow experiment.

## D. Expected costs (planning, not quotes)

Subscriptions $140 to $330/month; metered overflow $0 to $400/month; Jev < $100/month; data license four figures per year if purchased; hardware already owned. Annualized research cost of roughly $3,000 to $10,000 exceeds the investable capital; the owner should decide explicitly whether the project is funded as research or as investment.

## E. Things I could not do in this session

- No Saxo account or connector access; no live precheck executed.
- No LLM provider calls; adapters for Claude/OpenAI/Gemini remain to be written against the contract in spec §5.
- Help-center article on SIM market data and the multi-leg precheck reference page were not fetched.
- No historical dataset; no backtest was run. Every performance statement in the package is synthetic or hypothetical.
