# 11 Proposed architecture improvements

Every item is a REVISION: a proposal of this review, not part of the original research. Each names the finding
it answers, what to change, what it costs, and how its value would be shown. Items marked **before phase 1**
change what is built first; the rest can be adopted as amendments later. Nothing here authorises
implementation; see `12-roadmap.md`.

## A. Record and registry (measurement apparatus)

**R1 Ledger as the single source of truth with deterministic replay** (probe P2; `01-architecture.md` §3).
Registry, gate and e-process state are derived by replaying the ledger; no component keeps authoritative state
in memory or in a side file. Cost: a small replay module and a restore test. Validation: the restore test
(`02/04` §7) passes from month one. **Before phase 1.**

**R2 Gate state as ledger records, verified by the executor** (probe P5). Record types `gate_promoted`
(from, to, evidence hash, owner MAC) and `gate_demoted` (reason, actor). The executor principal replays the
anchored ledger, verifies the MAC chain itself, and refuses any call above the derived state. Cost: moderate;
removes the in-process `Gate` object. Validation: a test that no code path in the research package can
construct a promoted state; a fault-injection test that a forged record is rejected. **Before phase 1.**

**R3 One commit concept.** The registry is the only writer of forecasts and resolutions; the e-process consumes
registry resolution events in ledger order and computes λ from the prefix. Remove `CommittedEProcess.commit`
as a public API. Validation: property test that the e-value computed by replay equals the online value.
**Before phase 1.**

**R4 Grading rule for late YES** (probe P1). A YES observed after `expires_at` is `EXPIRED_NO`; the resolver
records the decision date and the evidence id. Validation: unit test; amendment to `02/01` §4.1.
**Before phase 1.**

**R5-prep Resolution-predicate grammar** (probe P3; N2). Replace the vague-word list with a small typed
predicate: `{source, record_selector, field, comparator, value, not_before, not_after}`, versioned, graded by a
deterministic resolver. Free text stays in `statement` for humans. Cost: a schema and a resolver per source
family (needed anyway). Validation: every registered event is machine-gradeable or VOID by construction.
**Before phase 2.**

**R20 Start the point-in-time universe and shadow books on the first SIM readback.** Monthly `/ref` snapshot,
candidate log with `considered_at`, decision and reason, and the three shadow books, from day one of
SIM_READ_ONLY. Cost: low. Value: the only survivorship-free dataset the programme will own.

**R21 Event-level eligibility registration.** Pre-register what makes an event eligible, log rejected
candidates with reasons, and report skill on all registered events and on a random subsample of eligible events
(`10-adversarial-review.md` §6).

## B. Statistics and evaluation

**N8 Power study before the first registration.** Simulate the committed e-process against a realistic Design-C
baseline over a grid of Brier improvements (0.005–0.05) and baseline sharpness; publish the detectable effect
at n = 300 and n = 600 and set the year-one criterion from it. Cost: a day. **Before phase 2.**

**N7 Declare the scored quantity.** Score the unfloored fused midpoint as primary; report the floored version
and a proper interval score (for example the Winkler interval score at the pre-registered level) as secondary.
Amend `04/02`. **Before phase 2.**

**N9 Family-wise control across ablation arms.** Primary e-process is confirmatory; arms are exploratory unless
combined by multiplication (independent arms) or e-BH. Amend `04/02`. **Before phase 2.**

**R7 Decompose interval width.** Report model disagreement, within-model imprecision and Monte Carlo spread
separately; ABSTAIN on disagreement and imprecision, not on Monte Carlo spread, which is a compute parameter.

**R8 Covariance-based fusion weights** (probe P4; N10). Minimum-variance weights from the shrunk error
covariance; keep the non-negativity fallback; report n_eff on the implied correlation. Validation: the probe
scenario yields a materially higher weight for the more accurate model.

**R12 One pre-registered Jev recalibration.** After the first 200 triaged documents (both polarities, repeat
calls), allow a single amendment of the three Jev thresholds; freeze thereafter.

**R14 Random audit of FORECAST items through round 2.** A pre-registered fraction (e.g. 10 %) of FORECAST items
also receives adversarial cross-examination; the comparison of audited versus unaudited Brier estimates the
value of round 2 and catches consistent hallucinated mechanisms.

**R19 Replace the annual α-budget** with e-value combination rules native to the method (`06-self-improvement…`
§4 item 4). Core decision; owner approval.

**Abstention scoring.** Score abstentions at the Design-C forecast so abstaining is never better than matching
the baseline (`02-scientific-methodology.md` §5 item 7).

## C. Causal layer and coherence

**R5 Typed identification arguments.** For each class other than `none`, require the fields that class needs
(assignment variable, units, timing, threats to validity for a natural experiment; instrument and exclusion
argument for an instrument; dose variable and monotonicity for dose-response). Round 2 targets those fields.
Over time, score whether mechanisms of each class predict their downstream events better than class `none`;
if not, collapse the taxonomy. Validation: the class-conditional skill table in the annual report.

**R6 Vertex-endpoint credal inference and a declared projection rule.** Replace uniform CPT sampling with
enumeration of interval endpoints per edge on small graphs (outer hull), keep sampling as an approximation on
large graphs with the gap logged; define "decision-relevant projection" (the events that enter the scenario
set) before the first PCCB.

**Elicit chain links separately.** Each conditional in a decomposition chain is elicited in its own call with
only the parent context (`03-probability-and-causal-modeling.md` §5 item 4).

## D. Formal verification

**R13 Formalise what would catch bugs** (`04-formal-verification.md` §3): LP dual certificates checked in exact
arithmetic; allocation certificate checking against concrete limits; gate state-machine invariant; ledger
verification properties; the supermartingale property under explicit measurability assumptions; coverage of
convex interval pooling. Remove theorems with no dependent code path.

## E. Orchestration and independence

**R9 Engineer and measure independence.** Role-specific inputs where the protocol allows; per-item blinding
record (bundle hash, prompt hash, model id, timestamps, process id) verified by the promoter (N6); reasoning-
overlap metrics (Jaccard of cited evidence, mechanisms, counter-mechanisms) reported beside n_eff; a periodic
same-prompt control.

**R10 Add the `single-model-three-roles` ablation arm.** One frontier model, three role prompts,
self-consistency sampling, plus Design C. Reports what the three-provider requirement buys.

**R11 Constrain the owner-started batch.** Same adapter code and bundles; no selection or editing by the
owner; transcript hash ledgered; items touched by the owner before commitment flagged.

**R15 Pin model configuration per call.** Browsing and tools disabled for round-1 calls; the adapter records
and verifies the model configuration and returned model identifier; a changed identifier is a new forecaster id.

**Schema first.** Publish the `ResearchOutput` JSON schema before any adapter is written
(`05-multi-model-orchestration.md` §5 item 7).

## F. Self-improvement

**R16 Canary namespace.** Canaries live in a promoter-only registry namespace, never shown as resolved to
researcher models, excluded from every statistic except the promoter's integrity check.

**R17 Promoter environment pinning.** The promoter pins the hash of code, data and dependencies per decision and
accepts artefacts only as data through a fixed interface; promoter code changes are core changes.

**R18 Rolling prospective holdouts.** Confirmation only on events registered after the proposal; frozen
historical sets for screening.

**Degradation action rule.** A pre-registered action (weight reduction, retirement, owner alert) attached to the
reverse e-process.

## G. Portfolio and risk

**Cost model as a component** with tests (commissions, spreads, FX, stamp duty, dividend withholding); never a
caller convention.

**Derived Kelly fraction.** Choose the fraction from perturbed-input simulations against a pre-registered
drawdown ceiling (`07-portfolio-and-risk.md` §6 item 2).

**Scenario grammar and coverage backtest** (`07-portfolio-and-risk.md` §6 item 3).

**Financing-event class** registered for every `financing_dependent` thesis so liquidity death is a thesis
break (`07-portfolio-and-risk.md` §6 item 4).

**Pilot feasibility decision after Q6**: either a 2–3 position operations pilot or a relaxed commission rule
with stated drag.

## H. Process

**English only** for all new material (owner instruction of 2026-10-16; `AGENTS.md` §5).

**Amend, do not overwrite.** Every adopted improvement becomes a dated amendment note next to the original
chapter reference in `09-open-questions-and-decisions.md`; the archive stays verbatim.

**Independent review of the reviewer.** Because the research and this review share a model family, the Codex
review should explicitly try to falsify the agreements in `10-adversarial-review.md`, not only check the
disagreements (`13-codex-review-checklist.md`).
