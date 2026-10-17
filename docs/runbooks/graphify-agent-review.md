# Graphify-assisted engineering and independent review

**Scope:** optional developer tooling for CPE, not the causal world model, the scientific source of truth, a CI verdict, or an authorization mechanism. This runbook does not approve implementation of the investment engine, change OD1/OD2/OD9a/OD10, or expand broker permissions.

## Connection and access

- Repository: `rorschach-zero/causal-proof-engine`. Current Graphify repository UUID as observed on 2026-10-17: `fd5eb8a0-cc46-48ff-8f82-cba4898857d1` (discover anew if the workspace changes).
- The repository-level `.mcp.json` declares the **hosted** Graphify MCP URL, `https://api.graphify.com/mcp`, with no credentials. It can be used by a Claude Code checkout that supports project MCP config; the user must complete OAuth when prompted. Check `/mcp` in the actual Claude environment.
- In Codex, independently install/connect the **Graphify** plugin in the Codex environment if supported, sign in with Graphify OAuth, and verify the tools are available **in the particular cloud session**. A ChatGPT connection does not prove that Codex Cloud inherited it.
- Both agents must verify `list_repositories` includes this repository with `queryable: true`; query `graph_stats` to obtain its `repositoryId` and **full** `commitSha`. If either agent lacks MCP access, report `NOT_CONNECTED` and use normal GitHub diff/source review; do not silently claim Graphify was used.
- Never put OAuth tokens, API keys, private documents, broker information, or other secrets in GitHub, Graphify Memory, prompts, or logs. Do not purchase an additional Graphify tier, install new agents, or enable paid API usage without owner approval.
- Hosted indexed main-branch content and a locally rebuilt CLI graph are **different** data sources. Do not silently substitute one for another or claim they cover the same snapshot.

## Strict commit provenance: first action in every review

1. Obtain the exact **40-character PR head SHA** directly from the current GitHub PR or checked-out Git commit and the repository identity.
2. Read the Graphify response `repositoryId` and **full** `commitSha`, not its approximate index age, abbreviated `freshness.commit` or the most recent Graphify review verdict.
3. Save the JSON response if accessible and run the offline check (stdlib only):

   ```sh
   python3 scripts/check_graphify_snapshot.py \
     --response /path/to/graphify-response.json \
     --expected-sha "$(git rev-parse HEAD)" \
     --repository-id fd5eb8a0-cc46-48ff-8f82-cba4898857d1
   ```

4. Exit code **0** means the returned graph snapshot names the same repository and exact commit. It does **not** prove that all files, tests, or PR data were indexed. Exit code **2** means `STALE_INDEX`, wrong repository, missing evidence or invalid input; fail closed for Graphify-based coverage/verification claims. Continue source review directly against the PR's actual diff, files and tests, clearly identifying Graphify as **historical context only**.
5. If the graph snapshot is older than a PR head, re-index with an approved supported facility if available and repeat the check. Do not assume the hosted service indexes unmerged PR branches automatically, and do not connect unreviewed external services to make it happen.

## Agent protocol (Claude and Codex, independently)

**Claude / implementer, before proposing a change:**
- Read `AGENTS.md`, the relevant approved spec, GitHub issue and current branch; report the change's allowed scope and current SHA.
- If available, use `recall` for prior decisions (flag candidate/unverified memories), `graphify_rank_files` or `query_graph` for navigation, and `impact_and_risk` / `graphify_file_neighbors` / `graphify_tests_for` to find affected code and candidate tests. Use repository source to confirm each consequential Graphify claim.
- Explicitly distinguish resolved/extracted edges from inferred or semantic suggestions. Lack of an edge or linked test is **not** proof of no dependency or coverage.
- Implement a root-cause fix within the separately authorized phase, run real tests and provide reproducible commands and observed output. Graphify does not execute tests.
- Prepare a reviewable PR with exact final SHA and change evidence; never self-merge or alter gate/security/scientific decisions without separate approval.

**Codex / independent reviewer, on each PR head update:**
- Re-read the current diff, relevant original research/approved specifications, and tests independently of Claude's summary.
- Independently check Graphify availability and snapshot identity; run scoped impact and tests lookup on the review target, and compare with plain GitHub code/file inspection. Treat stale graph as context only.
- Attempt falsification: boundary cases, regression tests, omitted paths, noncausal claims, uncertainty and data leakage. Separate `GRAPHIFY_SUGGESTION` from `REPRODUCED_DEFECT`, `UNVERIFIED`, and `BLOCKED`.
- Record the reviewed SHA, concrete counterexample, independent reproduction command/result and unresolved issues. A Graphify product event saying `passed` or green CI alone is not an independent scientific review.

**Both agents:** keep issues open when unresolved; avoid fabricated verification or retry-based closure. Only report resolution with evidence attached to the exact final integration SHA. When tools are unavailable, say so rather than weakening the quality gate.

## Minimal PR review record

Include this section in the PR review (or attach a file) for each reviewed SHA:

```text
Repository:
PR and exact head SHA:
Graphify agent access: Claude CONNECTED/NOT_CONNECTED; Codex CONNECTED/NOT_CONNECTED
Graphify repository UUID / build ID / indexed commit:
Snapshot result: EXACT_SHA / STALE_INDEX / UNAVAILABLE
Queries used; paths/symbols found; extracted vs inferred:
Direct GitHub diff/code observations:
Tests discovered by Graphify versus verified tests executed:
Independent counterexample or risk and evidence:
Remaining unknowns or blocked items:
Reviewer, command, environment, date:
```

## Measurable evaluation, not a graph-based correctness claim

Use three to five **real reviewed CPE implementation changes** when approved code and tests exist. For each frozen PR SHA, perform an independent plain-source/diff review and a Graphify-assisted review with the same scope. Capture verified *additional* cross-file findings, missed defects, false positives, linked tests versus executed coverage, time/tokens, and any new cloud charge. Compare the results; do not invent improvements or exclude failures. A single demonstration below is a connectivity/coverage baseline, **not** this benchmark.

### Initial observed baseline, 2026-10-17

- Graphify `list_repositories` reports CPE as ready/queryable.
- `graph_stats` on the hosted index reported **22 nodes, 26 edges, six communities**, build `501dd92c-4d08-4cd9-945a-d92d3d15ed5a`, full indexed commit `6426f29c94d5e5005861d640dd23fe40c2164b04` (main, 2026-10-16 18:01:44 UTC).
- `query_graph` correctly located the dispatch workflow and source tests; `impact_and_risk` identified `.github/workflows/claude-on-codex-review.yml` and `tests/test_review_dispatch.py` with candidate affected functions. Its `tests_unresolved: true` and `has_tests: false` for the workflow disagree with the presence of the source tests; resolve coverage by reading and executing the actual tests, not by assuming either conclusion.
- The graph is **not** the current head of research PR #7 (`00642e3a1f5d3600cb169541c60d9736d39b08e7`) or PR #4; no branch-complete review can be claimed from that main snapshot.
- The current default-branch dispatch is allowlisted to PR #4; this proposal **does not alter** dispatch logic, secrets, authorizations or CI triggers.

## Offline regression verification

```sh
python3 -m unittest discover -s tests -p 'test_graphify_snapshot.py' -v
```

This tests exact-match, stale SHA, missing/short SHA, wrong repo, malformed payload and CLI status. It **does not** test real Claude/Codex MCP authentication, CI execution, scientific correctness or actual hosted re-indexing. Record those as `NOT_VERIFIED` until exercised on the respective systems.

## Sources

- Graphify hosted MCP official connection instructions: https://graphify.com/mcp
- Graphify Codex plugin integration: https://graphify.com/blog/graphify-chatgpt-plugin
- Project review and cost constraints: GitHub Issue #6 and existing `AGENTS.md`

## Multi-vendor extension and acceptance

The cross-client configuration matrix, actual Codex and Gemini OAuth instructions, and connection acceptance checklist are maintained in `docs/runbooks/agent-mcp-onboarding.md`. This runbook applies identically to **every future AI agent**: each must demonstrate its own live MCP query before it is marked connected.

Versioned project config now includes `.mcp.json`, `.codex/config.toml`, and `.gemini/settings.json`. Project config is not an OAuth session; a successful **Codex GitHub automated review** is not evidence that Codex Cloud had access to Graphify. Likewise, a Graphify bot review with a diverged index is not a current-PR verification.

Offline configuration tests: `python3 -m unittest discover -s tests -p 'test_agent_mcp_configuration.py' -v`. GitHub workflow `.github/workflows/test-graphify-config.yml` checks both configuration and snapshot validation without credentials or external network calls; workflow execution must be verified separately.
