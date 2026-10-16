# 14 Claims not yet verified

Every claim in the research foundation that has not been verified against a primary source or by execution,
with its status and a verification path. Status labels per `research/README.md`. "Verify by" names who can do
it; most external items need the owner's accounts.

## A. External facts the package reports as verified, not re-checked in this session (PACKAGE-VERIFIED)

| # | Claim | Where | Verify by |
|---|---|---|---|
| A1 | Saxo SIM/LIVE base URLs, auth hosts, SIM-only one-day tokens, "market data not available in SIM" | `02/02` §1 | re-read developer.saxo environments page; archive bytes in the ingest log |
| A2 | Precheck request fields, `ExternalReference` ≤ 50, `ManualOrder` absent from the precheck page, `FieldGroups` not enumerated | `02/02` §1, `01/03` §2 | re-read precheck reference; confirm on first SIM call (Q3) |
| A3 | Order-placement rules: `ManualOrder` semantics and "soon mandatory", `x-request-id` 15-second duplicate rule, `TradeNotCompleted`, FX options not via OpenAPI | `02/02` §1 | re-read order-placement page |
| A4 | PKCE flow details and example lifetimes 1200 s / 2400 s | `02/02` §1 | re-read; measure real values in the 72-hour test (Q1) |
| A5 | LIVE credential process for direct clients | `02/02` §1 | re-read; owner's account |
| A6 | TypeSafe Jev API shape (endpoints, question types, headers, usage fields, no timestamp field) | `01/03` §2; archived JSON | archived JSON is in the repo; re-fetch to detect drift |
| A7 | Jev price USD 0.042/MTok input, output free; latency 70–500 ms; early access via waitlist | vendor blog per `01/03` | re-read blog; confirm on contract |
| A8 | arXiv 2609.33209 abstract: mean complement gap 0.064 (CI 0.055–0.072) on 480 pairs; three single-label probabilities sum to 1.14 | `01/03` §2 | read the paper, not only the abstract |
| A9 | arXiv titles for 2609.37647, 2609.33209, 2009.03167, 2510.02209, 2208.00724 | `01/03` §2 | arXiv API |
| A10 | Anthropic Max plans include monthly Platform API credits (USD 100 / 200), usable with Agent SDK and Messages API, not interactive Claude Code, 7-day wait, no rollover | `02/03`, articles 15036540 and 17154008 | re-read on setup day; terms change |
| A11 | OpenAI: Codex included in Plus/Pro; API key for programmatic workflows; automation tokens Enterprise-only; Pro "no five-hour limit" | `02/03` | re-read learn.chatgpt.com on setup day |
| A12 | Gemini CLI quotas 1,000 / 1,500 / 2,000 per day by tier; Antigravity CLI replacement notice for some tiers | `02/03` | re-read geminicli.com and cloud quota page |
| A13 | Lean compile: both files exit 0 on Lean v4.35.0 + Mathlib `cfc55fc5…`, standard axioms only, negative control fails | `evidence/lean_compile.log` | re-run `lake env lean` on the pinned toolchain (≈ 8 GB cache); add a CI job |
| A14 | The v0.1 prototype reviewed had a 20-file manifest that verified 20/20 | `01/03` §1 | the v0.1 ZIP is not in this repository; v0.1 was reconstructed here by reverse patch and its 11 tests pass |

## B. External facts the package itself marks UNVERIFIED

| # | Claim or question | Where | Verify by |
|---|---|---|---|
| B1 | Long-lived unattended Saxo session for an individual LIVE app (Q1, blocking) | `06/01` | 72-hour refresh test; written answer from Saxo support |
| B2 | Multi-leg precheck endpoint availability (Q4) | `02/02` §2 | reference docs |
| B3 | SIM delayed market data after linking a live account (Q7) | `02/02` §2 | fetch help article 4416934146449; test |
| B4 | Saxo (Schweiz) retail entitlements, commissions, minimum tickets, FX fees, enabled asset types (Q6) | `02/02` §2 | account documents; `/ref` readback |
| B5 | Whether Google AI Pro is affected by the Antigravity CLI change | `02/03` | geminicli.com |
| B6 | OpenTimestamps or similar as an anchoring service | `01/02` P1-LEDGER-01 | evaluate service; decide N4 |
| B7 | Jev rate limits and early-access timing (Q8) | `06/01` | vendor |
| B8 | Exact form of the GRAPA λ formula versus Waudby-Smith and Ramdas 2020 | `03/02` §3 | read arXiv 2010.09686 §; irrelevant to validity |
| B9 | Base rate of a listed stock making 10x in three years is low single-digit percent | `04/04` §2 (stated as general knowledge) | needs a delisting-inclusive historical universe (Q5) |
| B10 | Documented long-run public track records are around 20–30 % CAGR | `03/04` §6 | citation needed before use in any report |
| B11 | Swiss professional-trader criteria (ESTV circular 36) and their application to this design (Q9) | `05/01` F | Swiss tax adviser, in writing |
| B12 | Exact `/port` and `/ref` read paths | `02/02` §2 | reference docs at implementation |

## C. Scientific hypotheses (HYPOTHESIS; verification is the research programme)

| # | Claim | Test | Earliest read-out |
|---|---|---|---|
| C1 | H1: fusion beats best single LLM and Design C on Brier/log | primary e-process + ablation arms | year 1 (≥ 300 resolved) |
| C2 | H2: after-cost returns beat cash, equal-weight global ETF, random control | 5-year shadow book, bootstrap CIs | year 5 |
| C3 | H3: Jev recall ≥ 0.8 at ≤ 20 % of LLM-triage cost | randomised −Jev ablation | year 1 |
| C4 | H5: median discovery lead ≥ 60 days | external-mention process (underspecified, N-item in `02-scientific-methodology.md`) | year 1–2 |
| C5 | H6: hazard throttle reduces max drawdown net of false alarms | crisis backtest on vintage data (≈ 8 episodes; exploratory) | when vintage data exist |
| C6 | Design B better calibrated than A on graphs > 14 nodes | A vs B ablation | after 150 resolved |
| C7 | Fractional robust Kelly on calibrated credal inputs avoids ruin | perturbed-input simulation; shadow book | ongoing |
| C8 | Milestone skill transfers to pre-trend 10x discrimination (central claim) | rank correlation with realised 3-year returns in the shadow book | year 3 |
| C9 | Three frontier models are not three views of one corpus (n_eff > 1.5) | monthly n_eff; reasoning-overlap metrics (R9) | after 20+ resolved |
| C10 | 600 registrable events per year are available from 3–5 source families | supply measurement in phase 2 (N1) | first quarter of ingest |
| C11 | A Brier improvement detectable at 300–600 events exists against a realistic Design-C baseline | power study (N8) | before phase 2 |

## D. Claims about the reference code that the package's tests support but that are not system properties

| # | Claim | Status | Note |
|---|---|---|---|
| D1 | "Gate promotion requires owner authorisation and LIVE is blocked" | true for `Gate.promote`; **not** a property of the process (probe P5) | R2 |
| D2 | "Registry is ledger-backed" | writes go to the ledger; state is not recoverable from it (probe P2) | R1 |
| D3 | "Vague predicates are rejected" | word-list lint only (probe P3) | R5-prep |
| D4 | "E-process false-alarm rate ≤ α" | Monte Carlo with n = 60 per run, 1,500 runs, one seed (REPRODUCED); validity also depends on R3 in operation | add multiple seeds and longer n in CI |
| D5 | "Correlated models do not count three times" | true for correlation; accuracy ignored (probe P4) | R8 |
| D6 | "Token never logged" | true for the shown code paths; no test asserts the absence of `Bearer ` in captured logs | add the static gate from `04/03` §6 |

## E. Provenance statements this session cannot verify

| # | Statement | Note |
|---|---|---|
| E1 | Owner decisions dated 2026-10-16 (D10–D13 and the north-star confirmation) were made by the owner | recorded only inside the package; the owner should confirm them in the review of this PR |
| E2 | The package author read the external pages on 2026-10-16 | no archived bytes (`evidence/README.md`); archive at setup |
| E3 | The v0.1 input package and the prior audit (`INDEPENDENT_AUDIT_FINDINGS.md`) exist as described | not included; `01/02` §E reconciles against it |
