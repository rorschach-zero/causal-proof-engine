# RFC-RUST-001 — Rust-first Causal Proof Engine: frontier architecture research

**As of:** 2026-10-16 (CH); **implementation planning date:** 2026-10-17  
**Status:** PROPOSED — owner has requested Rust-first direction; implementation and amendments to binding governance still require separate review and recorded approval.  
**Repository research baseline:** `research/claude-handoff`; latest reconciliation for reading: PR #4, branch `claude/reconciliation-round-1`, with `research/16-reconciliation-matrix.md` v7 and `research/17-phase1-amended-specification.md` v4.  
**No execution today:** this is a design/research record only. No model providers, Jev, Saxo credentials, brokerage orders or live portfolio functionality are authorized by this RFC.

## 1. Thesis, constraints and decision

**Proposal:** move the *authoritative CPE application core* to Rust while retaining Lean 4 for formal mathematical claims and small, independent Python/SciPy reference oracles for scientific cross-checks. This is **Rust-first, not Rust-only**. Do not migrate unchanged Python v0.1/v0.2 demonstration code line-for-line: Codex confirmed scientific and state-boundary defects in those demonstrations. Specify and independently test the intended invariants before implementation.

**Reasoning:** memory safety, explicit ownership/concurrency, enum/newtype domain contracts, structured errors and tooling make Rust attractive for a 10-year+ service handling time-dependent research records and (much later) broker authority. These properties reduce some software failure modes; **they do not imply causal identification, correctly calibrated probabilities, crash foresight or positive returns**. Language choice cannot replace scientific validation.

**Current blockers:** research matrix lists owner decisions **OD1, OD2, OD9a and OD10** plus scientific defects RC-60 and RC-64..RC-79 not yet adopted. The current `AGENTS.md` still mandates typed Python for the first kernel; this RFC must not silently override it. A reviewed owner-approved governance amendment is mandatory before replacing that requirement.

### Architecture selection matrix (proposal, not a measured benchmark)

| Candidate | Reliability / invariant enforcement | Scientific ecosystem | Delivery speed | Proposed role |
|---|---|---|---|---|
| Pure Python | Runtime validation and strong tests required | Excellent (NumPy/SciPy/statistics) | Strong for experiments | Independent oracle only, not authoritative writer |
| Rust + Lean + independent Python oracles | Strong type checks, Rust safety tooling, formal + dynamic checks | Good with separate statistical oracle | Moderate | **Preferred** |
| Entirely Rust including ML/proof tooling | Still requires external Lean and evidence | Restricts library/reproducibility choices | Slower | Reject unnecessary language purity |
| Multiple always-on services from day 1 | More IAM and distributed consistency paths | No inherent scientific benefit | Slow | Reject for Phase 1 |

**Confirm by an evidence-based trial, not by slogans:** implement the same small transactional event-register and probability-boundary fixture in Rust and, as an external reference, Python; compare specification coverage, reliability under mutation/fault tests, complexity, maintainer comprehension, CI time and dependency risk. Do not claim speed superiority without measurements.

## 2. Minimal architecture with clear authority boundaries

Phase 1 **offline / synthetic only** (single Rust workspace and process, no network):

1. `cpe-domain`: immutable typed `EvidenceId`, `EventId`, `EntityId`, `ClusterId`, `ModelId`, `Outcome`, `Forecast`, `EventSpec`, `DecisionCertificate` and their validated constructors. Reject NaN, infinities, out-of-range probabilities, ambiguous predicates and missing mandatory model/Jev records. Use newtypes, enums, `Result`, avoid `unwrap` in paths receiving untrusted data.
2. `cpe-ledger`: single authoritative transactional writer (SQLite; **`rusqlite` synchronous** for small offline workload), atomic commit of events + derived state, reproducible canonical JSONL export and deterministic replay. A hash chain verifies only against a separately trusted anchor; call locally self-attested history self-attested. Commit acknowledgment and durable anchor cutoffs must be explicit. For loss-intolerant ledger, evaluate SQLite `WAL` + `synchronous=FULL` and actual filesystem guarantees; test power-loss/recovery semantics.
3. `cpe-registry`: deterministic forecast registration, immutable event identity and cluster membership, fixed `available_at`/published/observed/accepted/occurred/resolved times, typed resolution predicates; prohibit choosing favorable result versions or late submissions after a public outcome. Use committed receipts rather than LLM-provided timestamps as authority.
4. `cpe-evaluation`: separate proper-scoring contracts for prospectively committed point probabilities, cluster-aware pre-registered null/estimand, fixed-horizon (not unjustified anytime-valid) tests, explicit VOID/missingness bounds, leakage controls and comparison baselines. Default to no claimed `alpha` result unless power and assumptions hold.
5. `cpe-gates`: offline model of signed, expiring, environment-scoped **capabilities**, with monotonic epoch/nonce consumption and crash/rollback tests. It may model authorization but cannot give real trading authority in Phase 1. Enforce capability at the *protected operation boundary*, not merely in an object constructed by a caller.
6. `cpe-protocols`: versioned JSON Schema / fixtures for three independent frontier-model responses **plus Jev**. Phase 1 uses synthetic records; no provider clients. Scientific ablation protocols may omit a component by explicit experimental ID, but cannot issue a production consensus certificate lacking any mandatory component.

**Component split:** start with one Rust workspace, simple crates/modules only where contracts justify them, no Kubernetes, no microservices, no message broker, no vector DB, no broker adapter and no runtime self-modification in Phase 1. Rust `tokio` and SQLx are **not needed** in the offline single-writer core; introduce them when there is a measured asynchronous I/O requirement.

### Future **separate** trust zones (not built tomorrow)

- **Ingest/research:** read public sources, permit provider-specific external inference, write *proposed* hypotheses; never write trusted outcomes/anchors or reach a broker.
- **Admission & evidence:** trusted receipt clock, source byte hashing, publication-lag enforcement, immutable content snapshots, append-and-ack under one identity.
- **Promoter/evaluator:** frozen pre-registered experiments, isolated reproducible runs, no access to broker secrets or mutable training data, governed promotion budget.
- **Control owner:** independently authenticated policy approvals and anchors (not held by research agent).
- **Broker/executor (last):** separate principal, secrets/egress, read-only Saxo SIM before simulated prechecks, no model-provider connectivity; only signed bounded commands after separate review and approval.

Using GitHub Actions as an unattended scheduler/CI is fine; **never treat an ephemeral Actions filesystem as the durable investment ledger**. A permanent cloud writer/managed storage is a separately costed later decision.

## 3. Frontier techniques: what is verified, and what must be experimentally earned

| Frontier item / evidence | Application to CPE | Limitation / proof obligation | Stage |
|---|---|---|---|
| Rust stable **1.99.0**, Edition 2024 (released 2026-10-01) | Pinned compiler, `cargo fmt`, clippy, lockfile and typed kernel | Stable compiler does not validate business logic | Phase 1 |
| **Kani** model checker, ASE 2026; supports Rust proof harnesses | Prove bounded state-machine properties (invalid nonces, arithmetic overflow, no forbidden transitions) by executable model checking | Bounded state; not a proof of forecasting performance; tool has feature limits | Phase 1 exploration; gate in later phase |
| **Verus** verified Rust (active research) | Candidate for selected strongly invariant Rust functions | Supports a subset of Rust; dependency/setup proof overhead; benchmark vs Kani | Experimental, not day-one dependency |
| **Lean 4 / Mathlib** (pinned Lake toolchain) | Check mathematical lemmas: finite-state chain identities, constraints, expected-value algebra and risk bounds conditional on assumptions | Lean compilation not yet independently reproduced; proofs are not empirical investing guarantees | Phase 1 proof spike |
| SQLite transactional writer; FULL sync | Durable record semantics without distributed infrastructure | External anchor + backups and trusted writer still necessary; simulated crash ≠ real cloud failure | Phase 1 |
| **Polars** / **DataFusion** over Arrow + Parquet | At scale, analytical PIT scan, joins and columnar backtests | Hundreds of events/year do not justify big engine now; choose one on workload benchmark | Phase 2+ |
| **petgraph** typed graph algorithms | Causal-mechanism dependency graph for economic change, entity/sector links | A graph edge is not a causal identification result | Phase 3+ |
| **Temporal leakage in LLM backtesting** (Zhang/Stadie, 2026) and **NBER PIT LMs** (Kelly et al., 2026) | Matched clean controls, explicit publication/receipt lag and prospective evaluation before claiming edge | A chronological document snapshot does not remove LLM training-memory leakage | Phase 1 experiment grammar, Phase 2 data |
| **CARE confounder-aware aggregation** (ICML 2026); correlated LLM errors | Independent first-round evidence bundles, measure model-error correlations and shared source confounders, proper-score baselines | More models ≠ independent truth; no automatic majority-vote authority | Phase 2–4 |
| **Online certificate-driven time-series calibration under shift** (UAI 2026) | Candidate adaptation test for market regime shifts with predict-then-update and declared temporal assumptions | Paper's guarantees depend on model assumptions; no automatic portfolio drawdown guarantee | Research challenger after baseline |
| **StockBench** (2025) | Benchmark simple buy/hold, index, momentum/fundamentals against agentic policies | Strong models often fail to beat baselines; simulation != real execution | Later shadow evaluation |
| **cargo-vet / cargo-deny**, GitHub secret-boundary docs | Pin/audit dependencies and enforce licence/secrets/PR-runner separation; propose staged rollout | `cargo vet` with broad exceptions isn't equivalent to a real audit | Phase 1 CI + later hardening |
| **Graphify code graph** | Optional navigation and change-impact aid for Claude/Codex | It is not the economic causal world model or a verifier; cloud privacy must be reviewed | Developer-tool controlled benchmark |
| **Turbopuffer** | Optional replaceable hybrid retrieval index for primary-source corpus | Never canonical event store; PIT filters enforced externally; monthly costs | Phase 2 benchmark |

**Research opportunities we can actually test (not claimed novelties):**

- **Mechanism-to-shareholder-value pipeline**: frozen chain `exogenous change → adoption → supplier pricing / competition → earnings + dilution → total return vs entry valuation`. Score every intermediate prediction separately and link it to terminal investable return. Compare against source-only, keyword, fundamental and market-price baselines.
- **Missed-winner/failed-candidate audit**: archive *all* eligible firms (including rejected Jev leads, nonshortlisted and delisted), use stratified sample of rejects with known weights. Prevent survivor-only “10x discovery” anecdotes.
- **Blinded four-part committee**: Claude/OpenAI/Gemini independently process precommitted source bundles; Jev provides compulsory structured triage records. Only after round 1 can a shared model reconcile claims; calibrate weights on past *independent* outcome clusters and evaluate on new cohorts.
- **Verified decision certificate**: Rust type constraints + Kani bounded state checks + Lean conditional math + a separately scored prospective market forecast. None alone proves an investment is profitable.
- **Reversible regime change**: detect early stresses from timestamped leading indicators, but only alter exposure under a tested policy that explicitly models false alarms and missed recoveries. Hard portfolio limits take precedence over retrospective labels of “future compounder”.

## 4. Data architecture and "frontier" ongoing scanning

Before optimizing an index, define **five possible primary-source families** with licences, formats, lags and independent event yield; measure three before enabling an always-on source scanner:

- SEC EDGAR (US filings, new contracts and financial restatements);
- Patent legal-status / official patent office publication (qualification/IP outcomes; distinguish filings from commercial success);
- US/EU official regulatory, clinical trial and product approval registers (select deterministic events);
- Government procurement/grants and public industrial-capacity documents;
- Utility, grid/operator, energy, manufacturing or transport capacity/permit records.

Use a **research changelog** that records dated changes in methods, protocols and relevant software releases, and evaluates whether each finding should change CPE. Proposed review rhythm: weekly source/benchmark triage; monthly architecture and reproducibility check; quarterly adversarial method review. Automatic updates change no approved risk/security policy.

Evidence record must contain **source URI, immutable byte hash, document version, `published_at`, `first_observed_at`, `available_at`, `retrieved_at`, source permissions, entity mapping and reasons for rejection**. Retrieval indexes and model context are disposable views. Core legal/technical facts need canonical provenance. No web-sourced raw prompt can grant an agent authority.

## 5. Evaluation and implementation decisions

**Minimum comparative experiment** (days, not months, before broad rewrite):

- Match semantics across Rust and Python reference: randomized invalid inputs, duplicate semantic outcomes, late knowledge vs late occurrence, VOID, failed commit, crash/replay, rollback, tampered ledger/anchor, non-finite probability, tampered capability.
- Prove fixed cases in Kani where feasible; prove a small mathematical identity in Lean + explicit known-false proof failure; compare exact results to independent Python/SciPy oracle where Rust numeric implementations are nontrivial.
- Keep time-of-availability and complete evidence population as **separate scientific validity gates**; a correct Rust program can still produce an invalid financial research result if inputs are contaminated.
- Measure test runtime, dependency count, lockfile/reproducibility, CPU/RAM and reviewer comprehension, not just throughput.
- Stop if new implementation silently changes an estimand, accepted evidence boundary or loss policy.

### Phase-1 start gate for 2026-10-17

Owner must record **OD1** (offline Phase 1), **OD2** (corrected scientific methods), **OD9a** (remove mathematically invalid floor + replace leakage rule in canonical governance), **OD10** (apply or explicitly defer RC-60, RC-64..79) *before* implementation of conflicting code. A Rust-first decision adds a narrow **governance amendment** replacing Python-first requirements with Rust-first and naming Python only as an independent research oracle. This RFC authorizes none of those changes by itself.

After approval, begin only the smallest vertical slice: (a) pinned Rust workspace; (b) EventSpec/Forecast schema and temporal grammar; (c) one transactional evidence append/read/replay; (d) fault/property tests and CI; (e) mathematically targeted Lean/Kani spike. **Do not start full AI orchestration, causal net, Graphify synchronization, Jev/Saxo clients or trading.**

### Exit gates (reproduced, not arbitrary slogans)

- Rust `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, `cargo test --locked` green on pinned stable; CI logs accessible; no claimed tests without execution.
- Fuzz/property tests reject all specified malformed inputs; ledger replay after commit failure and crash equals the acknowledged state; no acknowledgement of a phantom record.
- Ledger tampering detected **relative to independently retained anchor**; unanchored window reported, not hidden.
- One Lean theorem plus deliberately false control checked on pinned toolchain; Kani proof harness feasible or documented blocker.
- No broker/model credentials or extra cloud expenses; no direct changes to `main`; independent Claude↔Codex technical review; owner accepts PR before merging.
- First-day deliverable can be only a design spike and benchmark if OD owners/scientific blockers remain unresolved; never mislabel it implemented.

## 6. Direct sources (first-party / primary scientific; retrieved 2026-10-16)

- Rust release 1.99 (2026-10-01): https://blog.rust-lang.org/2026/10/01/Rust-1.99.0/
- Rust 2024 edition: https://doc.rust-lang.org/stable/edition-guide/rust-2024/
- Rust Kani model checker (limitations): https://github.com/model-checking/kani and https://github.com/model-checking/kani/blob/main/docs/src/getting-started.md
- Verus Rust verification (subset/experimental): https://github.com/verus-lang/verus
- Lean 4: https://github.com/leanprover/lean4
- SQLite transaction durability: https://www.sqlite.org/pragma.html
- rusqlite transactions: https://docs.rs/rusqlite/latest/rusqlite/struct.Transaction.html
- DataFusion: https://datafusion.apache.org/
- Polars lazy engine: https://docs.pola.rs/user-guide/lazy/using/
- petgraph: https://docs.rs/petgraph/latest/petgraph/
- cargo-vet: https://mozilla.github.io/cargo-vet/
- GitHub Actions trust boundary: https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
- NBER PIT language models (2026-05): https://www.nber.org/papers/w35247
- Temporal leakage in LLM backtesting (2026-08): https://arxiv.org/abs/2608.02985
- CARE confounder-aware aggregation (ICML 2026-07): https://proceedings.mlr.press/v306/zhao26aq.html
- Online certificate-driven calibration under shift (UAI 2026-08): https://proceedings.mlr.press/v337/huang26b.html
- StockBench (2025): https://arxiv.org/abs/2510.02209
- Graphify code graph: https://github.com/Graphify-Labs/graphify
- Claude Code Routine API (experimental): https://platform.claude.com/docs/en/api/claude-code/routines-fire
- Saxo security/OpenAPI SIM: https://www.developer.saxo/openapi/learn/security

## 7. Decision record

- **Owner-requested direction:** Rust-first production kernel; Lean proofs and independent Python test oracles allowed; cloud-only development and eventual operation.
- **This document:** a reviewable architecture proposal, *not* implementation authorization or scientific proof.
- **Outstanding:** adoption of OD1/OD2/OD9a/OD10, Rust governance amendment, exact environment spending permissions, narrow source-family selection.
- **Do not** replace CPE's causal research goals with a conventional momentum trader; the design must test *early economic mechanism discovery* and economic capture, not merely follow already accelerated sectors.
