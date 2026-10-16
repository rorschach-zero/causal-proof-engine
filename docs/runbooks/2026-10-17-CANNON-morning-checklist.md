# Saturday 2026-10-17 — CANNON kickoff: exact user checklist and agent assignments

**Status:** REVISION — actionable briefing, **not** proof the agents are currently running unattended.  
**Owner:** one set of policy decisions and launch prompts; engineering diagnosis belongs to the agents.  
**End goal:** independently validated **CANNON_READY** release, not a review count, PR count or a "green" GitHub Action. The present platform is **not** CANNON-ready.

## Tomorrow: user actions in order (browser/mobile compatible)

### 0. Open these links (5 min)

- Main CPE project: https://github.com/rorschach-zero/causal-proof-engine
- **CANNON proposal and tomorrow plan:** https://github.com/rorschach-zero/causal-proof-engine/pull/10
- Current real-science reconciler PR #4: https://github.com/rorschach-zero/causal-proof-engine/pull/4
- Rust-first research PR #7: https://github.com/rorschach-zero/causal-proof-engine/pull/7
- Existing Claude↔Codex dispatch issue #3: https://github.com/rorschach-zero/causal-proof-engine/issues/3
- CPE Rust pilot kickoff issue #8: https://github.com/rorschach-zero/causal-proof-engine/issues/8
- Codex Cloud: https://chatgpt.com/codex
- Claude Code Cloud: https://claude.ai/code
- Claude Routines: https://claude.ai/code/routines
- Codex code review settings: https://chatgpt.com/codex/cloud/settings/code-review
- Codex cloud environment settings: https://chatgpt.com/codex/cloud/settings/environments

**Important:** Codex sessions launched locally on the PC might not appear as cloud tasks on Android. Select a **cloud environment** with the same account and repository; do not assume missing mobile history means the code or GitHub commits are lost.

### 1. Make one narrow owner approval (5 min)

On **CANNON PR #10** (or issue #3, cross-linked from it), post:

> I approve **CANNON-001 as the design and test target**, not as an implemented or already verified system. The review/repair duty must persist across sessions; retry budgets pause/replan but **never close unresolved problems**. Authorize a documentation-only and synthetic, secret-free pilot of the durable lease/idempotent replay and independent test gates on a separate branch. No provider API spend, changes to main, unattended merge, customer deployment, Saxo/broker access, trading or changed CPE risk policy are authorized. For the Rust migration and scientific method changes, prepare the exact OD1/OD2/OD9a/OD10 decision diff for my separate approval.

This **does not automatically approve** PR #4's 17 unapplied corrections or PR #7's five P1 findings; the agents must validate those and show the exact governing amendments. If owner chooses to approve actual Phase-1 implementation tomorrow, do so separately, on a dated PR and `research/09-open-questions-and-decisions.md` according to repo policy.

### 2. Start independent **Codex Cloud** architecture/remediation task (5 min)

Use **new CLOUD task** in `rorschach-zero/causal-proof-engine`; use the highest thinking effort available to your account. Paste:

```text
CANNON-001 / CPE remediation, 2026-10-17. Use the repo's
docs/proposals/CANNON-001-autonomous-multimodel-quality-protocol.md
and docs/runbooks/2026-10-17-CANNON-morning-checklist.md from the
CANNON proposal branch (not necessarily main).
Also review research PR #4 EXACT SHA
10f88298be942162f0795ae31c36a87c8284b376 and
Rust PR #7 SHA 00642e3a1f5d3600cb169541c60d9736d39b08e7,
and the current AGENTS.md on research/claude-handoff.

Determine and report what evidence proves real Claude↔Codex collaboration.
List all 17 unapplied RC findings in PR #4, and five P1 findings
in PR #7; distinguish answered-but-unresolved threads from actual defects.
Challenge each known invalid test/claim with a small counterexample
and propose exact robust fixes, with a target acceptance test.

The currently configured 3-round bound is ONLY a session budget.
No task may become DONE or be silently abandoned when retries run out.
Design durable finding state, PR-scoped leases, dedup, fresh-context
independent verification, new strategies after stagnation,
budget pause/resume, and default-FAIL CANNON acceptance.

Create ONLY a reviewed design/remediation PR plus isolated synthetic
test proposal until the owner approves the scientific and engineering
governance amendments. No modifications to main or existing science
foundation without approval; no merges, trading, secrets, API purchases,
new paid cloud resources, or runner workflows with privileges.
Report actual executed commands, unresolved blockers and exact links.
```

**Check:** output must include the exact input SHA, a finding-to-test mapping, what was actually executed, and a separate PR. A narrative saying "looks resolved" is insufficient.

### 3. Start **Claude Code Cloud** as genuinely independent reviewer (5 min)

Open the same repository/cloud project, but a separate cloud task. Paste:

```text
Independent CANNON red-team for rorschach-zero/causal-proof-engine,
2026-10-17. Read the CANNON-001 RFC, issue #3's six handoff
records, PR #4 at 10f88298be942162f0795ae31c36a87c8284b376,
and PR #7 at 00642e3a1f5d3600cb169541c60d9736d39b08e7.
Do NOT accept Codex or your own previous solution at face value.

First independently reproduce critical counterexamples:
RC-72 wrong-sized statistical test, RC-73 rollback/idle clock,
RC-74 crash/recovered consumed nonce, RC-75 hindsight forecast
revision, RC-77 late outcome, and other recorded RC-60 and
RC-64..79 issues. Compare failures to frozen expected behavior.
Critique the five PR #7 P1 blockers too.

Provide a read-only second opinion and adversarial test manifest
against a named SHA. Propose minimally changed fixes and any hard
scientific limitations, but never mark a missing result as passing.
Work within the currently approved research scope, no broker/provider
secrets, no payments, no policy edits or merge.
After Codex publishes a candidate, verify it on the exact final SHA
in a fresh independent context. Report failing tests and next
discriminating experiments until evidence supports closure.
```

### 4. Read only the important status (10 min)

- Is every known RC-60/64..79 finding represented as an OPEN testable work item?
- Are five P1 PR #7 review findings addressed, or explicitly blocking?
- Did **both** models actually run independent tests and attach reproducible artifacts, rather than merely cite the other's prose?
- Does the CANNON proof-of-concept actually survive quota/stalled runs, duplicates and deliberate retry exhaustion? **Not yet: this is what tomorrow's experiment must demonstrate.**
- Does any proposed fix change CPE statistical estimands, the `AGENTS.md` policy or risk/security constraints? If yes, approve the exact **diff** separately or leave the change pending.
- Is the candidate marked `CANNON_READY` only after a complete, independently verified frozen gate on the final combined SHA? If not, keep OPEN.

### 5. Owner decisions for actual implementation, after scientific summary

**Avoid blanket "approve all" today.** Require a compact evidence-backed options matrix first:

- **OD1:** whether an offline, synthetic Phase 1 of CPE is approved, not trading.
- **OD2:** the exact science correction set to incorporate in the decision register (no improper base-rate floor; point-score validity; dependent data; appropriate primary vs monitoring test).
- **OD9a:** owner-approved amendments to CPE governance §2 items 7 and 10 for shrinkage and real point-in-time leakage controls.
- **OD10:** exact disposition of all 17 unimplemented findings (fix, independent evidence of inapplicability, or explicitly blocked), not skipping by retry count.
- **Rust language change:** separate update to `AGENTS.md` §6 and CI, plus explicit amendment for the **anytime-valid** contract if changing which test is primary. Record decisions with date in `research/09-open-questions-and-decisions.md` in a reviewed PR.

Until that happens, the legitimate output tomorrow may be a scientifically rigorous corrected protocol and an independently verified **synthetic pilot**, not yet CPE investment code.

## What the owner does NOT have to do

No need to manually copy every finding between Claude and Codex once the durable dispatch is independently proven; that automation is the work product. No need to install tools on the owner's computer. No need to authorize provider APIs or pay for new services to complete the **documentation and synthetic pilot** already allowed. No need to fake approvals to make graphs green.

## CANNON exit tests

```text
C1  Every finding has an immutable ID, exact SHA, reproducer and owner;
    no issue erased by budget exhaustion or conversation reset.
C2  Two independent cloud agents can exchange verified findings and fixes
    without the owner hand-carrying comments; show durable receipts.
C3  Duplicate, reordered and overlapping events cause exactly one active
    PR repair lease; pending review is retained/replayed.
C4  Three consecutive failed attempts lead to a new strategy or
    PAUSED_REPLAN, never DONE/CANNON; resumption tested.
C5  A purposefully broken candidate or weakened security test stays FAIL.
C6  All affected tests rerun on the final combined commit with independent
    review; known P0/P1 all resolved or scope explicitly blocked.
C7  No unapproved spending, secrets, policy edits, merges or deployments.
C8  Record time-to-verified-merge, measured cost per accepted fix,
    CI runtime, patch conflict rate and subsequent regression escape.
```

**CANNON is a verifiable status, not a slogan or a fixed number of iterations. A persistent backlog is preferable to a false success.**

## If an agent says “max rounds reached”

Ask it to **save** (1) last good commit and SHA, (2) exact unresolved finding ID/test output, (3) hypotheses disproved, (4) a *different next diagnostic plan*, (5) its required authority/cost, and (6) a new review task/PR. Keeping the issue OPEN is mandatory. Human involvement is limited to funding/permission/scientific policy decisions, never accepting a broken implementation.

## Authentic sources

- Anthropic multi-agent coordination: https://claude.com/resources/articles/multi-agent-coordination-patterns
- Anthropic long-running harness primitives (example, not complete): https://github.com/anthropics/cwc-long-running-agents
- Empirical dynamic multi-agent concurrency paper (2026): https://arxiv.org/abs/2610.10263
- CPE Issue #3 live evidence: https://github.com/rorschach-zero/causal-proof-engine/issues/3
- CPE scientific PR #4: https://github.com/rorschach-zero/causal-proof-engine/pull/4
- CPE Rust proposal PR #7: https://github.com/rorschach-zero/causal-proof-engine/pull/7
