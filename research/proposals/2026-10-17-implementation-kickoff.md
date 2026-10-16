# 2026-10-17 — CPE Rust-first cloud kickoff (owner / Codex / Claude)

**Purpose:** The owner can open this file tomorrow and continue without reconstructing the conversation. This is a **handoff and approval checklist**, not a scheduled unattended start.

**Canonical RFC:** [Rust-first frontier research](2026-10-16-rust-first-frontier-rfc.md).  
**Research baseline:** PR #1 `research/claude-handoff`; scientific independent review PR #2; most recent reconciliation PR #4 `claude/reconciliation-round-1`.  
**Scope:** no real data ingest, no financial recommendation engine, no Saxo connection, no trading, no model keys, no additional paid services.

## A. Owner decisions — before code

Record dated responses on a GitHub Issue/PR:

- [ ] **Rust-first technical direction:** accept Rust as authoritative CPE kernel, Python solely as independent experiment/oracle when appropriate, Lean 4 for formal mathematical claims. Explicitly approve a focused change to `AGENTS.md` §6/§8 Python-first requirements after review.
- [ ] **OD1:** approve an **offline-only, synthetic Phase 1** scope (no network, model-provider APIs, brokerage).
- [ ] **OD2:** approve the statistically sound corrections from Codex/Claude, particularly no arbitrary rare-probability floor; pre-registered cluster-aware tests; point-probability proper scoring with honest interval semantics.
- [ ] **OD9a:** allow precisely scoped `AGENTS.md` updates for cohort priors/shrinkage and for temporal leakage controls.
- [ ] **OD10:** decide disposition of *all* RC-60 and RC-64..79 unresolved scientific/security findings before a test claiming validity is implemented; unresolved P0 items remain blockers, not workarounds.
- [ ] Confirm **no additional subscription/API/cloud spend and no live brokerage permissions** without later explicit approval.

Decisions remaining for later phases: provider entitlements, Jev rate/terms, source licensing, independent anchor/cloud account, financial asset/risk caps and brokerage API permissions.

## B. Morning technical reconciliation (one small PR)

**Codex Cloud (independent architecture integrator, maximum available effort)**

1. Read the Rust RFC, current `AGENTS.md`, PR #2 scientific review and latest `research/16`/`research/17` on PR #4 at **exact commit SHA**; do not silently substitute older versions.
2. Produce a dependency-light RFC amendment: new crate boundary table and explicit preconditions that map each applicable acceptance test to a Rust test / Kani harness / Lean proof / independent Python oracle.
3. Challenge whether the first component should be `rusqlite` or SQLite-free in-memory state; choose with fault-test/recovery evidence, not a blanket rule.
4. Identify the correct integration branch and provenance/merge order of PRs #1/#2/#4 before writing files on `main`.
5. Propose, **do not self-approve**, a minimal governance language amendment. No full system rewrite today.

**Claude Code (independent science/verification reviewer)**

1. Review the Rust RFC and Codex mapping independently; identify semantic changes from the approved Python specification.
2. Challenge temporal admission, cluster closure, missing outcomes, sequential tests and cryptographic capability rollback/replay.
3. Construct synthetic counterexamples for any improper claims; distinguish a statistical theorem from validity of its application.
4. Test minimum reproducible acceptance set and security constraints. Review dependency choices and reject unnecessary framework layers.

Disagreements are tracked in a single matrix, not resolved by forced vote. If owner approvals are missing, deliver **reviewed architecture only**, no implementation.

## C. First approved vertical slice (smallest practical code)

After owner approval and independent review, use separate task branches:

- `feature/rust-domain-ledger`: pinned `Cargo.toml`, `rust-toolchain.toml`, lockfile; typed `EventSpec`, `EvidenceReceipt`, `Forecast` and chronology checks; one transactional append/read/export/replay; no network.
- `review/claude-rust-ledger`: synthetic invalid data, failed append, reboot/replay, tampering against independent anchor test, concurrency and clock rollback; independent review of Codex implementation.
- Separate **proof spike**: compile one Lean mathematics lemma and a deliberately false lemma that must fail; Kani bounded checks on a small Rust state transition; document all limitations.

**Definition of done for the vertical slice:**
`cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, `cargo test --locked`, type/schema property tests, CI logs and secrets scan. No false claim of independent proof if Mathlib or Kani is unavailable. Full replay equality from acknowledged transaction receipts. No injection of untrusted economic conclusions into proof assumptions.

## D. Frontier watch: research intake without hype

A weekly **scientific diff** (not a generic newsletter) should evaluate:
- New Rust stable/security advisories and ecosystem changes.
- Verified Rust tools (Kani/Verus) and Lean 4/Mathlib pin updates.
- Point-in-time LLM modeling, correlated-error pooling, online calibration, robust causal evaluation.
- Time-indexed source ingestion, data licences and anti-lookahead benchmarks.
- Secure autonomous agents and resource/cost controls.

Record for each: primary source/date → real design benefit → evidence grade → cost/risk → experiment → recommendation **ADOPT / TEST / WATCH / REJECT**. Never update dependencies or change portfolio policy on publication alone.

## E. Paste-ready launch prompt for Codex Cloud (only after owner decisions)

```text
CPE kickoff, 2026-10-17. Repository rorschach-zero/causal-proof-engine.
Read research/proposals/2026-10-16-rust-first-frontier-rfc.md and
research/proposals/2026-10-17-implementation-kickoff.md in the Rust
proposal PR, then the latest PR #4 scientific reconciliation, PR #2
review and AGENTS.md. Work at very-high scientific/engineering rigor.

First: present the exact pending owner approvals OD1/OD2/OD9a/OD10
and identify incompatible Python-first governance text. If missing,
perform architecture and acceptance-test mapping only; no code.

Once recorded as approved: create a tiny Rust-first, synthetic-only
vertical slice (typed event schema, trustworthy timestamps, one
transactional ledger append/export/replay) on a separate branch and
PR. Preserve the older research archive unchanged. Pin dependencies,
run fmt/clippy/tests, include reproducible failure-injection tests.
Explicitly separate conditional formal math from empirical forecast
performance. No Jev/network/provider/Saxo/broker integration, no
secret acquisition, no extra spending. Request independent Claude
review before any merge.
```

## F. Links

- Shared GitHub: https://github.com/rorschach-zero/causal-proof-engine
- Codex Cloud: https://chatgpt.com/codex
- Claude Code Cloud: https://claude.ai/code
- Research PR #1: https://github.com/rorschach-zero/causal-proof-engine/pull/1
- Codex scientific review PR #2: https://github.com/rorschach-zero/causal-proof-engine/pull/2
- Latest science reconciliation PR #4: https://github.com/rorschach-zero/causal-proof-engine/pull/4
- Controlled Claude dispatch PR #5 (already merged): https://github.com/rorschach-zero/causal-proof-engine/pull/5
