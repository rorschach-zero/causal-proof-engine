# CLAUDE.md

Entry point for Claude Code in this repository. The canonical policy is **`AGENTS.md`**; read it first and
follow it over any tool default.

## Essentials

- **Phase:** research foundation under independent (Codex) review. Do not implement the investment engine,
  trading execution, broker connectivity or model adapters unless a roadmap phase has been approved in writing.
- **Where things are:** `research/README.md` (index and status labels), `research/original/` (verbatim
  research archive, read-only), `research/10-adversarial-review.md` (critique), `research/12-roadmap.md`.
- **Language:** English for all code, documentation and commit messages (`AGENTS.md` §5).
- **Attribution:** none. No `Co-Authored-By`, no session URLs, no "Generated with", no badges, in commits, PRs,
  code or docs (`AGENTS.md` §7). `.claude/settings.json` disables tool attribution; `.githooks/commit-msg`
  rejects violations (`git config core.hooksPath .githooks`). Commits use the owner's identity.
- **Safety:** no secrets in Git, no live orders, no weakening of risk or security controls to pass tests
  (`AGENTS.md` §3).
- **Honesty:** report what was run with its output; label everything (`ESTABLISHED`, `HYPOTHESIS`,
  `UNVERIFIED`, `REPRODUCED`, `REVISION`); never invent results or proofs (`AGENTS.md` §8).

## Commands

There is no project code yet. The research package's reference tests can be reproduced in an isolated
environment outside the repository (see `research/00-research-inventory.md` §4); do not install dependencies
into the repository for that purpose.

## Graphify (optional developer context)

For changes involving code or CI, follow `AGENTS.md` §13 and `docs/runbooks/graphify-agent-review.md`.
The repo-level `.mcp.json` points to the hosted Graphify MCP service; OAuth must be completed **in the actual Claude Code environment** and access verified there. Check graph freshness against the PR head before relying on impact/test lookups. If the service is unavailable or indexes a different commit, use GitHub sources and tests and report the limitation instead of claiming a current graph review.
