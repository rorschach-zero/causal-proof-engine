# Graphify onboarding for independent CPE agents

**State:** configuration proposal; no claim that remote cloud sessions have been OAuth-authorized. All commands below use existing product subscriptions. This procedure does not introduce model API billing or additional always-on hosting.

## Source of truth

Repository: `rorschach-zero/causal-proof-engine`.
Graphify hosted MCP endpoint (official): `https://api.graphify.com/mcp`.
Only use the Graphify workspace/repository returned by `list_repositories` after OAuth. Do not hardcode a historical graph index as the authoritative PR state.

The root `AGENTS.md` is the binding CPE agent policy. `CLAUDE.md` and `GEMINI.md` defer to it. Any future vendor must load an equivalent copy of its policies and report which revision was read. Graphify is **developer tooling**, not the financial causal inference engine or proof/evaluation system.

## Agent-specific configuration

| Agent / host | Versioned repository configuration | One-time operator action inside that host | Verification |
|---|---|---|---|
| Claude Code | `.mcp.json` | Open repo in Claude Code, approve its project MCP config, complete Graphify OAuth via `/mcp` | Call `list_repositories` and `graph_stats`; compare SHA |
| Codex CLI / IDE / trusted project | `.codex/config.toml` | Open trusted repo; run `codex mcp list`; when listed run `codex mcp login graphify` and authorize in browser | Ask Codex to query CPE repository and report `repositoryId` and full `commitSha` |
| Codex Cloud / subscription review | `AGENTS.md` plus project configuration where supported | Separately enable Graphify for the **actual Codex Cloud environment**; cloud PR review does not necessarily inherit local CLI OAuth or ChatGPT plugins | One real Graphify MCP call shown in a Cloud run, with exact repo and snapshot |
| Gemini CLI (future) | `.gemini/settings.json` and `GEMINI.md` | In Gemini CLI, run `/mcp auth graphify` and complete browser OAuth | Call `list_repositories` / `graph_stats` / `query_graph` |
| Any future agent with HTTP MCP | `AGENTS.md`, this runbook, provider-supported configuration | Add `https://api.graphify.com/mcp` as Streamable HTTP, complete **that agent's** OAuth and verify the tool list | Same live MCP query, repository identity, full SHA and code-source cross-check |
| Future agent with no MCP | `AGENTS.md` | Do **not** claim Graphify connected; use raw GitHub files and tests | Mark `NOT_CONNECTED` and use GitHub source |

Never paste provider keys, OAuth tokens, Saxo secrets, private research data, or subscription session cookies into GitHub, Graphify memory, CI logs or model prompts. Never work around subscriptions by using scraped session tokens.

The Codex CLI and cloud UI have different environments. A passing Codex GitHub PR review confirms review service activity, **not** that Graphify was accessible inside that review. A completed OAuth in ChatGPT confirms only that current connector.

## Mandatory per-session smoke test

1. Identify the agent product, host, workspace, access permissions and exact GitHub PR head SHA.
2. Invoke `list_repositories` on Graphify; confirm `rorschach-zero/causal-proof-engine` with `queryable: true`.
3. Invoke `graph_stats` and record returned `repositoryId`, full `commitSha`, build ID and indexed time. A successful response proves access to an index, not coverage of the PR.
4. Ask `query_graph`: "Locate the CPE Codex review-to-Claude dispatch workflow and its regression tests; show filenames." Cross-check the files in GitHub.
5. If snapshot and GitHub PR head differ, record `STALE_INDEX`, do not claim graph coverage of the PR. Reindex using a vendor-supported, separately authorized method if available; otherwise review the current code through GitHub.
6. Report actual results and any blocker. No false `CONNECTED` if no live call succeeded.

## Scope of Graphify permissions

In the versioned Codex and Gemini configurations only read-oriented Graphify tools are allowlisted. Memory writes or workspace changes are not required for development review and must be individually authorized if ever enabled. Claude `.mcp.json` is less granular; rely on approval policy and the canonical `AGENTS.md` until per-tool permission control is available in that host.

Do not run `graphify install --project` or its hook installers automatically over existing repository agent policies. Those installers may add skills and hooks; review their exact changes in a separate PR first. An optional **local** AST graph may be used to study a PR checkout without paid model APIs, but it is a distinct source and must not be misrepresented as the hosted Graphify index.

## Connection acceptance matrix

A checkbox is complete only when a live tool response from that host is recorded on a PR or issue, with date, repo ID, Graphify build ID, full indexed SHA, GitHub head SHA and reviewer.

- [x] ChatGPT Graphify connector: confirmed repo and graph queries on 2026-10-17.
- [ ] Claude Code Cloud session: interactive OAuth plus smoke test pending.
- [ ] Codex Cloud agent session: independent Graphify query pending.
- [ ] Codex CLI / IDE: trusted-project config + interactive OAuth pending.
- [ ] Gemini CLI: config committed as a future integration; subscription access and OAuth not yet verified.
- [ ] Later vendors: template only, no automatic authorization.

## Reference documentation

- https://graphify.com/mcp
- https://graphify.com/integrations/codex
- https://geminicli.com/docs/tools/mcp-server/
- https://learn.chatgpt.com/docs/extend/mcp
- https://graphify.com/integrations/claude-code
