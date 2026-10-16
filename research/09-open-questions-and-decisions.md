# 09 Open questions, scientific assumptions and research decisions

Consolidates `06/01` (Q1–Q9), `06/03` (critical assumptions), `07/02` (decisions), `06/02` (risk register
pointers) and adds the questions this review raises (N1–N12). The original text is unchanged in the archive;
this document is the working list.

## 1. Open questions from the package (`06/01`)

Blocking = must be answered before the gate leaves SIM_READ_ONLY.

| # | Question | Status | Validation path | Owner |
|---|---|---|---|---|
| Q1 (**blocking**) | Can an individual Saxo OpenAPI app keep an unattended session (refresh lifetime, rotation) for days or weeks? Documented values are examples only (1200 s / 2400 s). | open | 72-hour unattended refresh test in SIM; written question to Saxo support | owner |
| Q2 (**blocking**) | Which providers permit unattended scheduled use under the owner's subscriptions? | partly answered by `02/03`: Claude via Max API credits; Gemini conditional; OpenAI owner-started batch | re-read terms on setup day, dated screenshots in the ledger; subscriptions only, no API keys without an owner decision | owner |
| Q3 | Does precheck accept or ignore `ManualOrder`; which `FieldGroups` values are valid? | open | first SIM precheck with and without the field; archive responses | owner |
| Q4 | Is the multi-leg precheck endpoint available and for which exchanges? | open, not pilot-relevant | reference docs at implementation | owner |
| Q5 | Source of a point-in-time universe with delistings. | decided for year one: forward reconstruction from Saxo `/ref` snapshots; historical Wald audit only with free sources | ongoing | owner |
| Q6 | Saxo (Schweiz) retail entitlements: OpenAPI availability, commissions, minimum tickets, FX fees, enabled asset types. | open; determines pilot feasibility (`07-portfolio-and-risk.md` §6 item 1) | account documents and `/ref`/`/port` readback in SIM_READ_ONLY; no account data in AI chats | owner |
| Q7 | Does linking a funded live account give SIM delayed market data? | open | fetch and archive the help article; test after linking | owner |
| Q8 | Jev early-access timing, rate limits, silent changes of `jev-latest`. | open | `GET /v1/models` daily; adapter logs returned model | owner / TypeSafe |
| Q9 | Swiss tax classification as professional securities trader under an automated low-turnover design. | open | written opinion from a Swiss tax adviser before LIVE; design constraint set (median holding > 12 months, ≤ 24 round trips, no derivatives) | owner |

## 2. Critical assumptions and what happens if they fail (`06/03`)

| Assumption | Validation | Consequence if false |
|---|---|---|
| Milestone-event skill transfers to 10x-candidate discrimination | rank correlation vs realised 3-year returns in the shadow book, from year 3 | an event-forecasting system without investment edge; no capital increase |
| Three LLMs are not three views of one corpus | n_eff monthly; < 1.5 persistently falsifies independence | committee reduced to one model plus adversarial prompts; Jev kept (owner decision required: conflicts with the non-negotiable three-model requirement) |
| Jev probabilities are stable enough to gate research | complement gap and repeat-call noise on 200 fixed documents monthly | raise Jev thresholds or limit Jev to duplicate clustering; the mandatory slot remains |
| Coherence projection improves calibration | −coherence ablation | remove from the critical path; keep as diagnostic |
| Leading stress indicators reduce drawdown net of false alarms | H6 on vintage data | remove the throttle; keep thesis-break selling |
| Fully paid instruments have bounded loss | by construction; allocator enforces R ≥ −1 | n/a; derivatives need a new model |
| Ledger anchors are outside the researcher's reach | monthly owner check from a separate machine; CI fails if the anchor path is writable by the researcher | anchors are decorative; evidence devalued |
| Publication lags are stable and documentable per source | table with evidence per entry; spot re-measurement | exclude the source from backtests |
| Saxo allows unattended sessions (Q1) | 72-hour refresh test | daily owner login as a permanent constraint |
| Subscriptions cover research operation (Q2) | terms on setup day; volume measured in month one | reduce volume or upgrade one subscription; no metering without owner decision |
| Design-C base rates are estimable from available data | Q5; cohort size reported | rare targets get no floor; discrimination only |
| The owner performs the two recurring duties (anchor check, gate promotion) | calendar entry; ledger record per check | automatic demotion when anchor checks lapse |

## 3. Decisions recorded in the package (`07/02` §A, reversible by the owner)

Renumbered D1–D13; the original item number is in brackets.

| # | Decision |
|---|---|
| D1 [1] | REVISE; no capital; LIVE blocked in reference code |
| D2 [2] | Design B research engine, Design A certificate layer, Design C mandatory baseline; selection by ablation after 150 resolved events |
| D3 [3] | Fusion thresholds pre-registered: spread 0.30, width 0.35, Jev complement gap 0.15, Jev primary evidence 0.60, relevance 0.50, shrinkage 0.30, minimum history 20 |
| D4 [4] | E-process: α = 0.05, λ_max = 0.5, predictable GRAPA-style λ, running-maximum rejection |
| D5 [5] | Pilot whitelist Stock, Etf, Bond, MutualFund; gross 100 %, position 20 %, ≤ 8 positions, cash floor 10 %, worst-case loss per position ≤ 15 %, ≤ 24 round trips per year |
| D6 [6] | Rare probabilities never elicited below 5 %; decomposition, base-rate floor; two years discrimination only |
| D7 [7] | Year-one primary metric is forecast skill, not P&L; H2 is a 5-year shadow experiment |
| D8 [8] | Four principals with separate accounts and secrets |
| D9 [9] | Risk-off limited to throttling new purchases and cash floor; never forced liquidation of thesis-intact positions; sell only on thesis break |
| D10 [10] | Operation only via existing subscriptions plus Jev; USD 0 additional cost planned in year one; OpenAI as owner-started daily batch; any deviation is an owner decision with a ledger entry |
| D11 [11] | North star 100x in ten years stays; profit every year and beating the index every year are not goals; milestones per `04/04` |
| D12 [12] | 25-year horizon: versioned immutable core, evolvable shell via proposer/promoter, model replacement path, annual α-budget, anchored annual report, annual restore test, dead-man switch |
| D13 [13] | Research is cross-asset from day one; positions extend class by class through the five-criteria ladder; method scanner keeps AI and finance research current |

Owner questions left open by the package (`07/02` §E): daily Saxo login acceptable if Q1 is negative?

## 4. New questions raised by this review (REVISION)

| # | Question | Why it blocks | Proposed resolution |
|---|---|---|---|
| N1 | Which source families feed the discovery scanner (names, licences, formats, lags, expected event yield)? | The 600-events-per-year target, the publication-lag table and H5 all depend on it; nothing is specified | owner and researchers list 5 candidate families with a one-page profile each before phase 2; pick 3 for year one |
| N2 | What is the grammar of a resolution predicate? | the vague-word list is bypassable (probe P3); grading disputes are otherwise inevitable | small typed DSL: source, field, comparator, value, date bound; graded by a deterministic resolver with a version |
| N3 | Durable store for ledger and registry (JSONL segments, SQLite in append-only mode, Parquet snapshots)? | replay, restore test and 25-year growth | decide in phase 1; JSONL as canonical export format regardless |
| N4 | Anchoring mechanism: owner-side anchor store only, or external timestamping (signed git tags, OpenTimestamps)? | the HMAC design is redundant or insufficient depending on who runs anchoring (`01-architecture.md` §3) | owner-side daily anchor to a store the researcher cannot write; HMAC dropped; external timestamp evaluated as an option |
| N5 | Gate state as ledger records with executor replay? | the in-process gate is advisory (probe P5) | yes; record types `gate_promoted` (with owner MAC) and `gate_demoted`; executor replays the anchored ledger |
| N6 | How is round-1 blindness enforced and evidenced? | independence claim rests on it | per-item blinding record: evidence-bundle hash, prompt hash, model id, request and response timestamps, process id; verified by the promoter |
| N7 | Which exact quantity is scored for interval forecasts, floored or unfloored midpoint, and which proper interval score is secondary? | changes what H0 tests (`02-scientific-methodology.md` §5 items 3–4) | decide and amend `04/02` before the first registration |
| N8 | Power analysis against a realistic Design-C baseline: what effect size is detectable at 300 and 600 events? | the year-one success criterion may be unreachable by construction | simulation study before phase 2; publish detectable effect |
| N9 | Family-wise error across ablation arms: confirmatory primary only, multiplicative e-value combination, or e-BH? | design changes could be justified by exploratory arms | decide once; write into `04/02` by amendment |
| N10 | Fusion weights from covariance, not correlation? | probe P4 | yes, with the same non-negativity fallback; n_eff reported on the implied correlation |
| N11 | Grading of a YES observed after `expires_at`? | probe P1 | `EXPIRED_NO`; resolver must document the decision date relative to expiry |
| N12 | Runtime: Windows-native per `07/01`, or containers for reproducibility per `02/04` §4? | restore test and CI | containerised core services with Windows as the host; owner duties remain native |

## 5. Decisions required before any implementation phase starts

From the owner: confirm D1–D13 or amend; answer N1 (source families) and N12 (runtime); confirm that a Codex
review of this foundation is the gate for phase 1. From the reviewers jointly: N2, N3, N4, N5, N7, N8, N9,
N10, N11 as amendments to the original documents, each recorded with date and reason.
