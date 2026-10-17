# Gemini CLI entry point for the Causal Proof Engine

Read `AGENTS.md` first. Its scientific, security, authorship and owner-approval requirements bind Gemini exactly as they bind Codex and Claude.

The optional Graphify project connection is declared in `.gemini/settings.json` and requires interactive OAuth authorization in the actual Gemini environment. Run `/mcp auth graphify` and verify `list_repositories`, `graph_stats` and a scoped `query_graph` for `rorschach-zero/causal-proof-engine`. Do not claim connected if these tool calls did not succeed in your session.

Follow `docs/runbooks/agent-mcp-onboarding.md` and `docs/runbooks/graphify-agent-review.md`. An index that is not at the **exact** GitHub review head is navigation context only, not code-coverage, correctness or review evidence. Review current GitHub files and execute actual tests.

Gemini is a future independent reviewer only when the owner enables that workflow. Do not contact model APIs, trade, handle Saxo credentials, alter scientific gates or spend money without a separate explicit authorization.
