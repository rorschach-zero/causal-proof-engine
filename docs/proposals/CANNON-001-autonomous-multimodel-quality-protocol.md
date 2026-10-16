# CANNON-001 — Multi-model development and evidence-gated resolution protocol

**Date:** 2026-10-16, Switzerland.  
**Classification:** REVISION — independent architecture proposal, **not binding governance, not deployed software, and not proof of an autonomous agent system**.  
**Owner term:** **CANNON** = the canonical **accepted quality state** of a version of a project, not the name of a model.  
**Scope:** shared developer infrastructure for CPE, Tidbit, Bricks, Rails and later projects. CPE is a controlled documentation-only pilot. The general-purpose development harness is a **separate product/workspace**, not a runtime dependency of CPE or any customer application.  
**Trust boundary:** this proposal cannot authorize new providers, keys, cloud spending, self-modifying governance, trading, production deployments or merges.

## 1. Why the present Claude↔Codex loop is NOT CANNON

**REPRODUCED from live repository records, 2026-10-16:**

- [Issue #3](https://github.com/rorschach-zero/causal-proof-engine/issues/3) explicitly adopts a maximum three review rounds and stops at that budget; it is **not a commitment to resolving every defect**.
- GitHub's merged dispatcher `.github/workflows/claude-on-codex-review.yml` presently triggers **only PR #4** on edits to a Codex bot summary comment, checks the current PR SHA and branches beginning `claude/`, and calls a Claude Code Routine. This is a useful **working, limited handoff**, not a general multi-project platform.
- The [issue #3 six handoff logs](https://github.com/rorschach-zero/causal-proof-engine/issues/3) demonstrate that Claude processed independent Codex criticisms, reproduced counterexamples and made revisions in the actual repo. That proves cooperation is more than two chatbots agreeing in prose.
- One dispatch resulted in overlapping Claude sessions acting on the same PR and SHA, and one lost its push race. No **durable session lease**, no atomic deduplication of events, and no verified cross-session recovery policy are implemented. A fixed PR allowlist is still active.
- [Scientific PR #4](https://github.com/rorschach-zero/causal-proof-engine/pull/4), last checked at `10f88298be942162f0795ae31c36a87c8284b376`, retains **55 formally unresolved review threads** (many contain previous responses, so 55 ≠ 55 distinct unfixed defects); matrix v7 records **17 actual unapplied findings**: RC-60 and RC-64 through RC-79, including reproduced faults in statistical-size guarantees, forecast revision selection, nonce replay and rollback clocks. That is a blocking scientific backlog, not CANNON.
- [Rust proposal PR #7](https://github.com/rorschach-zero/causal-proof-engine/pull/7), reviewed at `00642e3a1f5d3600cb169541c60d9736d39b08e7`, has **five Codex P1 findings** about evidence labels, contradictory anytime-valid governance, absent pinned PR #4 commit, missing canonical decision-register approvals and mutable research references. All five must be independently adjudicated, not marked resolved by timeout.
- Codex Automatic Code Review is a **PR diff reviewer**, not the same thing as an independent high-effort scientific validation agent. Green GitHub workflow status does not imply that Claude fixed the issues or that science is true.
- Graphify is connected and queryable but its first indexed source is `main@6426f29` (22 code-graph nodes), **not** the research PR branches. Its code graph cannot certify the architecture at PR #4 or #7. Graphify's review itself warned its index was stale.

**Conclusion:** multi-agent handoffs have been observed; **reliable autonomous closure, quality-gated merge, lack of retry abandonment and coverage of every project have not been demonstrated**. This RFC does not claim otherwise.

## 2. Invariants — must be enforced outside any model

1. **Default DENY / default FAIL.** At creation, each acceptance criterion and independently verified finding starts `PASS=false`; only the CI artifact/verifier identity can set it `true`. No model can fabricate a success string or edit the effective criteria as part of a fix.
2. **Open until evidence-proved closure.** Reaching 3 / 10 / N retries is a **session budget** or **replan trigger**, never a state named `DONE`, `FIXED` or `CANNON`. No finding disappears merely because the agent's plan expires or a quota resets.
3. **No infinite-spend loop.** A session may stop on quota, deadlock, missing authority, repeated identical output, unknown science or external dependency. It MUST atomically checkpoint a failing durable task with reproducible details and a next diagnostic experiment; it is eligible to resume under an authorized budget. **Unbounded lifetime retry commitments cannot imply unlimited costs or guarantee a solution to every possible task**.
4. **Distinct verifier.** The implementing model never supplies the only approval. Independently rerun tests/commands, inspect diff and commit SHA, and use a separate vendor or fresh isolated verification context. An LLM verdict without external reproducible evidence is not sufficient.
5. **Counterexample before patch where feasible.** Convert each verified bug into a smallest failing test or static proof assertion; demand the test fail on the old commit and pass on the corrected one. Review of a fix must look for nearby counterexamples and regression tests. Never weaken a failing test or security policy just to turn CI green.
6. **Immutable inputs / no silent scope edits.** Every run identifies `project_id, contract_hash, base_sha, candidate_sha, finding_ids, evidence_ids`. A finding only closes on the SHA the verifier examined. If the code/spec advances, impacted evidence is stale and needs revalidation.
7. **Explicit authority tiers.** Agents may research, write on isolated branches, test and propose PRs under preapproved scopes. Policy changes, security boundaries, destructive changes, live deploys, purchases, external credential grants and finance/broker actions require separate owner-signed authorization. A model, PR comment or repository file must not grant itself that authorization.
8. **Least privilege and provenance.** Reviewer is read-only against the candidate code; builder cannot change signed acceptance criteria; runner holds no live secrets. Supply-chain provenance stays truthful even when marketing footers are disabled.
9. **Never change an objective to claim victory.** If a requested quality target is impossible under current constraints or its validity is scientifically unsettled, mark `BLOCKED_UNPROVED` (with disproof/experiment) instead of passing or lowering thresholds.
10. **Git compatibility is a transitional evidence store, not a performance assumption.** We may develop a faster patch artifact/change graph in front of Git, but only retire Git when a replacement demonstrates atomic durable history, auditability, offline backup, verified reproducible restore, merge correctness and vendor portability at lower measured cost.

## 3. State machine and durable records

State transitions, enforced by one small trusted controller (not the writing agent):

```text
INTAKE -> SPEC_FROZEN -> ASSIGNED -> BUILDING -> CANDIDATE
CANDIDATE -> REPRO_TESTING -> ADVERSARIAL_REVIEW
ADVERSARIAL_REVIEW -> REPAIR_REQUIRED -> BUILDING
ADVERSARIAL_REVIEW -> VERIFIED_CANDIDATE -> CANNON_READY
CANNON_READY -> OWNER_APPROVAL_PENDING or POLICY_ELIGIBLE_MERGE -> MERGED
ANY_ACTIVE -> PAUSED_BUDGET | PAUSED_DEPENDENCY | BLOCKED_UNPROVED
PAUSED_* -> ASSIGNED (on permitted resume; never silently close)
BLOCKED_UNPROVED -> SPEC_FROZEN (only on new evidence or explicit re-scope)
```

Every transition creates an append-only, timestamped **Evidence Record**:
`work_item_id, repo, contract_sha256, source_commit, target_commit, path_ownership, writer_id, verifier_id, provider/model version, scoped grant, attempt_id, lease_epoch, event_id, started_at, finished_at, cost_estimate, actual_cost_if_available, finding_id, reproduction_command, old_behavior, new_behavior, artifact_digest, verdict, remaining_risk, next_experiment`.

A `CANNON_READY` candidate requires ALL findings in its **frozen scope** to have completed verification against **the same final commit**, zero unwaived P0/P1, negative controls passing, signed review evidence, tests on a clean builder-independent runner and all mandatory risk/security gates. A scope exception is a conspicuous owner-approved exclusion, never a hidden dropped requirement. Separately classify `MERGED` and `DEPLOYED`; CANNON-ready is not automatically production-safe.

## 4. Resolver policy: NO silent abandoning after three rounds

The review **horizon is evidence-based, not attempt-count-based**. Finite attempts are a resource safety tool.

```text
for each active finding:
  VERIFY preexisting counterexample and exact SHA
  RUN isolated diagnosis; rank competing root-cause hypotheses
  PICK a distinct repair strategy with an explicit falsifiable prediction
  IMPLEMENT in an isolated change artifact (one writer per ownership unit)
  TEST: preexisting regression, adversarial/mutation/property, integration
  SECOND_VENDOR REVIEW using fresh context, read-only access
  if all required evidence confirms: propose closure tied to final SHA
  else: record new evidence and select a changed strategy
  if no new information, lease failure, budget hit, missing permission:
       SAVE reproducible blocked state and next diagnostic experiment
       WAIT / RESUME under authorized schedule or owner decision
  NEVER set PASS on a failed, expired or merely retried item
```

**Anti-oscillation rules:** hash failed patch attempts and observed test result; the same `(bug, base, patch_strategy, failure_signature)` cannot be resubmitted without new evidence. Two independent repair strategies producing the same result trigger a **root-cause research fork** (minimal counterexample, inspect specification, formal model, environment or dependency). When two vendors disagree, each proposes a *discriminating experiment*; a measured result, not consensus pressure, settles the point. If no discriminating experiment exists, the issue remains scientifically unresolved.

**Escalation meaning:** an escalation is a request for **new authority, funding or a real policy choice**, or a durable scientific unknown—not asking the owner to do debugging. It must show precise conflicting assumptions, alternatives and risks. Agent may automatically resume when its preauthorized budget replenishes and an approved schedule/queue actually exists. Such an always-on scheduler **is not deployed today**.

## 5. Multi-vendor roles without correlated rubber stamps

- **Planner/orchestrator:** constructs task DAG and frozen acceptance contract; writes no production code in reviewer role.
- **Implementer:** Claude Code or Codex cloud per task; constrained write grants to its isolated work area.
- **Independent critic:** other vendor first, with no access to author's private scratchpad and no write permission. Challenge specs, not style alone.
- **Adversarial validator:** deterministic CI/mutation/fuzz/model checking, plus fresh-context independent vendor where ambiguity remains. For frontends, real browser interaction/screenshots and accessibility checks; for CPE, deterministic counterexamples plus Lean/Kani where suited.
- **Integrator:** one lease per affected file/module and single integration queue; precompute conflict/semantic-impact paths; may parallelize nonoverlapping tasks. Must rerun *all changed impact surface* checks on **combined** commit. A green unit test on individual patches is not merge proof.
- **Cost/strategy governor:** routes simpler tasks to the lowest adequate permitted model; expensive science/security reviews to stronger independent models; tracks usefulness, cost and remaining time. Never bypasses quality to meet throughput targets.
- **Independent audit trail:** trusted event writer anchored outside agent's writable workspace; reviewer trace uses the exact run artifact hash, not chat excerpts.

Two-model independence does not equal unbiased truth: shared prompts, source corpora and model training can correlate errors. Prefer tool-based oracles and held-out adversarial fixtures wherever possible.

## 6. Speed without dangerous merge shortcuts

**Throughput definition:** median hours **from scoped task to independently verified accepted integration**, alongside *post-merge incident rate*, *reverted change rate*, *defect escape*, *cost per accepted correct change*, *CI runtime* and *finding age*. **PR count/hour alone is not quality or real velocity.**

Order of optimization:
1. Small changes with minimal ownership overlap; dependency graph suggests separable parallel work.
2. Run cheap deterministic checks early and expensive independent reviews on candidates that pass; for high-risk semantic changes run full proof/adversarial checks regardless of size.
3. Cache build/test artifacts and pass compact **evidence manifests** between vendors instead of entire chats or repeat repo scans.
4. Assign exactly one integration writer per affected code region; serialize shared schema changes. An append-only change graph can prepare compatible patches; only an independent runner authorizes publication.
5. Pin base commits, codegraph freshness, schema/test dependencies. Do not accept Graphify's stale/inferred review as verification.
6. Benchmark git worktrees + atomic CI with an alternative patch-DAG approach before replacing git-based audit. Git's history is a useful compatibility/rollback primitive even if human-centric PR workflows are slow.

**Merge authority by risk class** (future after owner authorizes and test policy is proven):
- Tier A: formatting, isolated nonbehavioral docs: auto-merge may be considered after all artifact gates and explicit policy.
- Tier B: user-visible features in Tidbit/Bricks/Rails: auto-merge only after high-confidence automated behavior tests, second model review, successful staging replay and an owner-approved policy.
- Tier C: CPE scientific estimands, money flows, authentication, safety controls and irreversible changes: **no unattended merge/deploy under current authorization**. Architectural ambitions do not override owner-controlled scope.

## 7. Technology and boundaries

Recommended pilot implementation **after** policy approval:
- **Rust** for the small trusted controller, artifact/lease state machine, capability gates and deterministic test-result evaluator (initially a single service and transactional database, not a distributed platform).
- **Git + GitHub** as temporary durable interoperability/audit adapter. Integrate Claude Code Cloud and Codex Cloud through officially supported event/API surfaces; **verify subscription rights** before designing headless, recurring cross-provider runs. Do not scrape session cookies, share personal tokens or silently pay per-token API bills.
- **PostgreSQL / SQLite** depending on whether multi-worker durability and leader election are actually required. For day-one prototype with one dispatcher, SQLite transactional leases are enough. Later expand to managed Postgres with fencing tokens and outbox/idempotency. No distributed lock based solely on PR comments.
- **Content-addressed artifacts** (source snapshot, patch, test log, model output, evaluation certificate) using immutable SHA-256 digests; replaceable cache/search layer. Branch/source links remain pointers, never evidence by themselves.
- **No prompts as permissions.** Use workflow credentials tied to trusted branches, short-lived grants, egress restrictions and a separate secrets control plane. The existing GitHub Actions dispatch token boundary and per-PR lock must be hardened before any general rollout.
- **Graphify** may speed cross-file change impact; never stands in for tests. **Turbopuffer** may later index project/research documents; never becomes canonical code/version/audit store.

## 8. CPE pilot: measurable acceptance tests before scaling

The existing [issue #3](https://github.com/rorschach-zero/causal-proof-engine/issues/3) currently calls for six handoffs at most and stops; this RFC changes the **meaning of retry exhaustion**, not provider rate/safety caps.

**Readiness matrix, default FAIL**:

| Test | Required evidence | Present 2026-10-16? |
|---|---|---|
| Same-SHA reviewer handshake | Codex review ID mapped to Claude response commit and tested counterexample | YES, documented on issue #3 / PR #4 |
| Two independent unattended handoffs | Durable log of two review→repair cycles | YES, documented (six Claude handoffs) |
| Per-PR single-running-session lease | Two overlapping completion events produce one active session, and pending review gets replayed | **NO; a real collision occurred** |
| Durable dedup across GitHub comment edits/restarts | Inject duplicate, reorder and replay, prove exactly-once *effect* | **NO** |
| Resume after cost/quota/stall | Task stays `PAUSED_*` and executes when authorized scheduler resumes it | **NO** |
| New tactic after stagnation | Reproduced root cause, switched strategy, baseline fails new negative test | PARTIAL: PR #4 scientific corrections; no generic policy |
| Validator separation | Clean-environment independent test and separate vendor signed result | PARTIAL: some Python counterexamples reproduced; no broad CI evidence |
| Resolve all PR #4 material defects | RC-60 + RC-64…RC-79 each corrected and independently validated or scientifically shown inapplicable | **NO: 17 unapplied** |
| All PR #7 P1 findings | Five P1 resolved or independently rejected with evidence against pinned SHA | **NO** |
| Autonomous CANNON publication | Frozen acceptance criteria, verified combined SHA, no P0/P1, approved authority | **NO** |

**Result:** CPE is **NOT CANNON**. The current Claude↔Codex review loop has shown valuable adversarial collaboration, but may pause while genuine faults remain; that must be fixed before it can be called autonomous high-quality delivery.

### Proof-of-collaboration experiment (tomorrow, controlled, synthetic)

1. Freeze a synthetic test PR containing a deliberately faulty Rust/Python time boundary and an independent hidden regression (e.g. duplicate nonce after crash; do **not** import broker code).
2. Obtain one independent Codex finding with minimal reproduction, then Claude's independently tested fix. On the new SHA, have Codex challenge the new solution. Force an artificial `3 session attempts consumed` state; verify **finding remains OPEN** and persists across fresh sessions.
3. Deliver multiple identical/overlapping `review completed` events. Prove one active lease, exactly-once durable effect, and pending reviews processed on resume.
4. Test a missing permission / exhausted subscription case. Verify state becomes `PAUSED_BUDGET`, no cost overrun, no `CANNON_READY`, and an actually configured resume later picks it up.
5. Require independent CI/mutation/fuzz and a review that can flag deliberately weakened assertions. The end-to-end task must be resolved with evidence; do not claim true autonomy on a workflow that requires owner copy/paste between providers.
6. Measure accepted throughput and incremental model/cloud cost. Compare to current GitHub PR model. Merge/publish **only after separate owner policy and scientific scope acceptance**.

## 9. Day-one backlog and decision checklist

**CPE-specific:** preserve the canonical scientific matrix in PR #4, 55 review threads and 17 unapplied true findings; authorize agent research on the findings, not blanket adoption of unreviewed fixes. Prioritize RC-72 (invalid size test), RC-73 and RC-74 (clock/nonce replay), RC-75 and RC-77 (hindsight/late admission), RC-76 (common cutoff), RC-78/79 (eligible population and leakage controls); include RC-60 and RC-64..71 with machine-readable dispositions. Review current PR #7 five P1 findings before merging it.

**CANNON-specific:** implement idempotent review event capture and per-PR lease in an isolated branch first, then durable work item states and independent default-FAIL CI. Never remove the current PR #4 allowlist until a synthetic hostile dispatch test passes. Separate the control plane from CPE investments and any customer accounts.

**Owner acts only on policy/authorization:** scientific estimand choice, acceptance of governance changes, provider/subscription legal and spending permissions, scope of auto-merge and data residency. Agents handle code repair and diagnostic experiments without requesting owner repetition.

**No unbounded risk:** prolonged scientific uncertainty stays prominently OPEN with the best known evidence and next discriminating experiment, not false assurance of guaranteed resolution.

## 10. Primary reading and evidence

- CPE authoritative local audit: [Issue #3](https://github.com/rorschach-zero/causal-proof-engine/issues/3), [PR #4](https://github.com/rorschach-zero/causal-proof-engine/pull/4) at `10f88298be942162f0795ae31c36a87c8284b376`, [PR #7](https://github.com/rorschach-zero/causal-proof-engine/pull/7) at `00642e3a1f5d3600cb169541c60d9736d39b08e7`, [existing dispatch](https://github.com/rorschach-zero/causal-proof-engine/blob/main/.github/workflows/claude-on-codex-review.yml).
- Anthropic, *Multi-agent coordination patterns* (2026-04-10): https://claude.com/resources/articles/multi-agent-coordination-patterns — generator/verifier loops, team races and orchestrator bottlenecks (ESTABLISHED as published vendor design guidance, not proof of our implementation).
- Anthropic sample, *Harness Primitives for Long-Running Claude Agents* (2026): https://github.com/anthropics/cwc-long-running-agents — default-fail, independent fresh-context evaluator, agent-written checkpoint; explicitly an example, not a turnkey maintained service (ESTABLISHED as described by the maintainers).
- Li et al., *When Sub-Agents Work in Parallel* (2026-10-07): https://arxiv.org/abs/2610.10263 — 354 tasks / 2,124 executions examining dynamic concurrency and failure modes (ESTABLISHED as authors' reported experimental design; external generalization UNVERIFIED).
- Anthropic *Projects redesigned* (2026-09-17): https://claude.com/resources/articles/projects-redesigned — cloud threads on distinct branches; overlap still has merge conflicts.
- **UNVERIFIED**: content of owner's linked Anthropic video https://youtube.com/watch?v=hiI0Vk4NgeY could not be retrieved reliably in this environment on 2026-10-16; no architectural claim in this RFC is attributed to unseen video content.

## 11. Proposed governance impact — review required

This is a proposed shared engineering overlay. It must not silently replace the current CPE `AGENTS.md` or authorize automatic merges. If independently validated and accepted, extract a small reusable CANNON repository/control plane with one project-specific `canon-policy.yaml` + source-of-truth acceptance manifest per project, **schema-validated and owner-signed**. Include `policy_version` and prevent any agent from writing or self-approving that file.

**Target, not yet achieved:** autonomous diagnosis/repair/resume across separately subscribed vendors, with permanently visible blockers and objectively tested candidate releases. `CANNON_READY` means verification criteria are satisfied, **never** an unqualified guarantee that software has no defects.