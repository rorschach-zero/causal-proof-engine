# Causal Proof Engine

Private research and engineering repository for an evidence-based, multi-model causal forecasting and
portfolio research system.

## Project status

**Research foundation imported; independent review in progress.** The completed research package
(2026-10-16) is archived verbatim under `research/original/` and organised, summarised and critiqued in English
under `research/`. This repository contains **no implementation**: no trading application, no broker
connectivity, no model adapters, no executable strategy, and no validated predictive results. Implementation
starts only after the Codex review of the research foundation and the owner's approval of Phase 1
(`research/12-roadmap.md`).

## Where to start

| If you want to | Read |
|---|---|
| understand the rules of this repository | `AGENTS.md` (canonical), `CLAUDE.md` (entry point for Claude Code) |
| find your way through the research | `research/README.md` |
| know what was delivered and what was checked | `research/00-research-inventory.md` |
| read the architecture and its review | `research/01-architecture.md` |
| see the independent critique | `research/10-adversarial-review.md` |
| see what is proposed to change | `research/11-proposed-improvements.md` |
| see what is not yet verified | `research/14-unverified-claims.md` |
| review this work (Codex) | `research/13-codex-review-checklist.md` |

## Research objective

To investigate whether an initial USD 4,000 could achieve exceptional long-term compounding toward USD 400,000
over ten years. This is a highly ambitious experimental objective, not an assumed or guaranteed outcome.
Nothing here is investment advice.

## Intended architecture (summary)

- Independent research by three frontier models (Claude, OpenAI, Gemini) with Jev as a mandatory typed
  triage component; no simple majority vote; correlation-aware fusion with explicit abstention.
- Point-in-time evidence, registered events with exact resolution criteria, interval forecasts, proper scores,
  anytime-valid sequential tests, and Lean certificates for the mathematics that admits them.
- An append-only, anchored ledger recording predictions, rejected ideas, misses, failures and counterfactuals.
- Separate principals and testable layers for research, promotion, portfolio policy, risk constraints and
  eventual Saxo **simulation**.
- Independent review before merging, reproducible tests, restrained dependencies, English documentation.

## Safety boundary

No broker credentials or private account data may be committed. **Live orders and leverage are out of scope**
until a separately reviewed and expressly authorised release; an initial live pilot, if ever approved, is capped
at USD 1,000 after verified safeguards. Formal verification establishes correctness relative to stated
assumptions, not profitable real-world forecasts. Simulated performance is never live performance.

## Working in this repository

All work goes through pull requests against `main` with independent review. Enable the versioned hooks once
per clone: `git config core.hooksPath .githooks`. No AI attribution, session links or promotional markers in
commits, pull requests, code or documentation (`AGENTS.md` §7).
