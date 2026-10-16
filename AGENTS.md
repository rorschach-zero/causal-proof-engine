# AGENTS.md: engineering policy for the Causal Proof Engine

This is the canonical engineering policy of this repository. It binds every contributor, human or AI
(Claude Code, OpenAI Codex, or any other agent). `CLAUDE.md` is a short entry point that defers to this file.
Where a tool default and this file disagree, this file wins.

## 1. What this project is

CPE is a research programme investigating whether a causal, multi-model, formally checked forecasting system
can identify early, non-obvious economic change and turn it into exceptional long-term compounding. The research
objective is to test whether USD 4,000 could compound toward USD 400,000 over ten years. **That is an
experimental objective, not an assumed or guaranteed outcome.** Nothing in this repository is investment advice.

Current phase: research foundation under independent review. **No implementation of the investment engine is
authorised.** See `research/README.md` and `research/12-roadmap.md`.

## 2. Non-negotiable product requirements

The eventual system must provide all of the following. They are design constraints, not aspirations to trade off:

1. Three independently reasoning frontier AI models **plus Jev** (TypeSafe typed-decision model) as first-class,
   mandatory research components. No forecast is produced with fewer than three model outputs plus Jev triage.
   No simple majority vote.
2. A causal world model capable of identifying early, non-obvious economic changes across all sectors, from
   physical, scientific, demographic, institutional and economic first principles, not from price charts.
3. Scientifically grounded probabilistic forecasts: interval forecasts on registered events with exact
   resolution criteria, proper scoring, calibration tracking, and anytime-valid sequential tests.
4. Formal verification in Lean 4 of the mathematical and logical claims that admit it, under explicitly listed
   hypotheses. A proof never implies profit.
5. Point-in-time evidence and immutable prediction histories: observer-timestamped ingest, archived bytes,
   append-only anchored ledger, forecasts committed before outcomes can be known.
6. Learning from successes, failures, missed opportunities, rejected investments and counterfactual outcomes
   (shadow books: no-exit, entry-shadow, random control; late-exit and premature-exit audits).
7. Detection and evaluation of extreme asymmetric opportunities, with rare probabilities derived by
   decomposition and floored by cohort base rates, never elicited directly below 5 %.
8. Long-term portfolio management across relevant financial instruments, extended class by class through the
   acceptance ladder in `research/07-portfolio-and-risk.md`.
9. Adaptive risk management without naive panic-selling: leading hazard indicators, hysteresis, throttling of
   new purchases and cash-floor changes, never forced liquidation of thesis-intact positions.
10. Autonomous scientific improvement with independent evaluation: proposer/promoter separation, frozen
    hash-pinned holdouts, pre-registered thresholds, canaries, time-shifted holdouts; live P&L is never a reward.
11. Eventually, controlled Saxo Bank integration, beginning with simulation (SIM read-only first).

## 3. Safety boundaries (hard)

- **No live trading.** No code path may place, modify or cancel a real order. LIVE gate promotion stays blocked
  in code until a separately reviewed and expressly authorised release.
- **Initial live pilot: at most USD 1,000**, only after separate written approval, an independent security and
  risk review of the order path, and all gate evidence bundles. The remaining USD 3,000 stays outside the
  system until prospective evidence exists.
- **No broker credentials, API keys, tokens, account keys or private account data in Git, logs, prompts,
  test fixtures or AI chats.** Secrets live in the OS credential store of the principal that needs them.
- **No margin, no uncovered options, no instruments with unbounded loss, no automated short positions** in the
  pilot. Instrument whitelist: fully paid Stock, Etf, Bond, MutualFund, tradability read from broker reference data.
- **No weakening of security or risk controls to make tests pass.** A failing safety test is a finding, not an
  obstacle.
- **No unreviewed changes to `main`.** All work goes through pull requests with independent review.
- Research agents never import or call the executor. Executor code never has model-provider access.
- The self-improvement loop may never modify risk limits, gate state, broker permissions, evaluation datasets,
  the ledger, or fusion thresholds.

## 4. Repository layout

| Path | Purpose | Rules |
|---|---|---|
| `research/original/` | the delivered research package, verbatim | **read-only archive**; never edited, translated or reformatted; excluded from tooling; its reference code is evidence, not project code |
| `research/*.md` | English foundation documents: topic entry points, critique, improvements, roadmap, checklists | source of truth for decisions; every change is a reviewed PR |
| `AGENTS.md`, `CLAUDE.md` | governance | changes require owner approval |
| `.claude/settings.json` | tool configuration (attribution disabled) | keep in sync with §7 |
| `.githooks/` | versioned git hooks (`commit-msg` rejects attribution trailers) | enable with `git config core.hooksPath .githooks` |
| (future) `cpe/`, `tests/`, `proofs/` | implementation, tests, Lean proofs | only after the roadmap phase is approved |

## 5. Language

All code, comments, identifiers, commit messages, documentation and review notes are written in **English**.
The single exception is the verbatim archive under `research/original/`, which keeps its original language
as the historical record; every chapter in it has an English entry point in `research/`.

## 6. Engineering standards

- **Beautiful, readable, well-structured code.** Small modules with one responsibility; names that say what a
  thing is; no cleverness that needs a comment to be understood.
- **Minimal complexity, no redundant implementations.** One way to do each thing. Before adding a module, show
  that no existing one does the job. Delete code that is superseded instead of keeping it "for reference".
- **Root-cause solutions, not workarounds.** When a test, a tool or a policy is in the way, fix the cause.
  Document the cause and the fix in the commit message.
- **Clear architecture and purposeful abstractions.** Abstractions are introduced when a second concrete case
  exists, not before. Interfaces between principals (researcher, promoter, executor, owner) are explicit contracts.
- **Documented scientific assumptions and technical decisions.** Every component states what it assumes, in a
  docstring or a design note, with a reference. Decisions are recorded in
  `research/09-open-questions-and-decisions.md` (later in an ADR directory).
- **Strict typing, testing and reproducibility.** Python with full type annotations checked in CI; property
  and fault-injection tests for safety-relevant code; pinned dependencies and Lean toolchain; every reported
  number reproducible from committed code and data by a command named in the PR.
- **Open formats only** for durable data (JSONL, Parquet, Markdown); no proprietary store without an export path.
- **Dependencies** are added only when genuinely necessary, pinned, and justified in the PR.

## 7. Provenance and attribution

Truthful internal provenance is mandatory; decoration is prohibited.

- Commits are authored and committed under the repository owner's identity (`Salah Aouaj <salah@hydeout.ch>`)
  unless the owner designates another human author. Commit messages describe **what changed and why**.
- **Prohibited in commits, pull requests, source code, comments and documentation:** AI attribution trailers
  (for example `Co-Authored-By: Claude …`), tool session URLs (`Claude-Session: …`, `claude.ai/code/session…`),
  promotional footers ("Generated with …"), emoji badges, decorative watermarks, or any other AI marking in any
  form. This applies to Claude Code, Codex and every other tool. Tool defaults that add such lines must be
  switched off (`.claude/settings.json` sets `attribution.commit`, `attribution.pr` to empty and
  `sessionUrl` to false; the `commit-msg` hook rejects violations).
- **Required provenance** lives in content, not in trailers: which research document a change implements,
  which finding it addresses, which command reproduces a result, and which review approved it (PR reference).
  Which assistant drafted a change may be stated in plain prose in the PR description when it matters for review.
- Never falsify authorship metadata, never rewrite shared history (`main` or another person's branch), never
  amend or force-push over commits that others may have fetched.

## 8. Scientific standards

- **Three kinds of evidence, never mixed in language:** formally proved (Lean, conditional on listed hypotheses),
  statistically shown (e-processes, proper scores, pre-registered α), empirically supported (track record with
  confidence intervals). Simulated performance is never live performance; coherence is never predictive
  correctness; a proof never implies profit.
- **Labels are mandatory:** `ESTABLISHED`, `HYPOTHESIS`, `UNVERIFIED`, `PACKAGE-VERIFIED`, `REPRODUCED`,
  `CONFIRMED-DEFECT`, `REVISION` (definitions in `research/README.md`).
- **No invented test results, fake proofs or fabricated research.** Report what was run, with the command and
  the environment. If something was not run, say so. A claim about an external document carries the date it
  was read and, where possible, an archived copy.
- **Pre-registration before unblinding.** Hypotheses, thresholds and primary metrics are written down before
  the data that tests them are seen. Changes require a dated amendment with justification.
- **One primary test per claim.** Exploratory comparisons are reported with their count and never justify
  promotion. Negative results are published in the ledger and in the annual report.
- **Survivorship and leakage controls are part of the method,** not an afterthought: point-in-time universe
  including delistings, publication-lag shifted series, vintage data, purged and embargoed walk-forward,
  model knowledge cutoffs recorded per forecast.

## 9. Review and merge policy

- Every change goes through a pull request against `main`. Direct pushes to `main` are prohibited.
- Important changes (anything under `research/` that changes a decision, anything that will become safety,
  risk, ledger, gate, or broker code, and any dependency or toolchain change) require **independent review by a
  different reviewer than the author**: for Claude-authored work, Codex or the owner; for Codex-authored work,
  Claude or the owner. The owner approves governance and risk-limit changes personally.
- Reviewers verify claims, not prose: re-run the named commands, check that labels are honest, check that no
  safety boundary moved.
- A PR is mergeable when: CI is green, the independent review is recorded, every number in the description is
  reproducible, and no prohibited attribution appears in commits or description.

## 10. Git workflow

- Branch names: `research/<topic>`, `feature/<topic>`, `fix/<topic>`, `review/<topic>`.
- Small, meaningful, reviewable commits with messages in English: a one-line summary, a blank line, then the
  reasoning. No trailers of any kind except `Reviewed-by:` naming a human when the owner asks for it.
- Rebase or amend only your own unpushed commits. Merge the base branch to resolve conflicts on shared branches.
- Tags for frozen research states are signed by the owner.

## 11. Conduct of AI agents in this repository

Agents may: read everything, propose changes via PR, run the project's own tests and checks, write
documentation and code within an approved roadmap phase, and critique each other's work frankly.

Agents must not: implement trading execution, connect broker credentials, place or simulate orders against a
real account, install dependencies without a stated need, claim verification they did not perform, silently
narrow or widen an assigned scope, merge anything, change governance files without owner approval, or add any
attribution, watermark or promotional text.

When an agent disagrees with a prior decision, it records the disagreement with reasons in the relevant
research document under a `REVISION` label and leaves the original text intact. The owner decides.

## 12. Definition of done (for any task)

Scope delivered in full or the gap stated explicitly; tests and checks actually run and reported with output;
documentation updated; labels honest; no secrets; no attribution; independent review requested.
