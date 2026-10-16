# Causal Proof Engine

Private research and engineering repository for an evidence-based, multi-model causal forecasting and portfolio research system.

## Project status

**Bootstrap only — research/design review in progress.** The finished Claude research package has not yet been imported. This repository does not yet contain an approved trading application, an executable portfolio strategy, or validated predictive results.

## Intended architecture

- Independent research by multiple models (Claude, OpenAI, Gemini) with Jev as a first-class signal-processing component.
- Point-in-time evidence, explicit hypotheses, causal forecasts, calibrated probabilities and formal checks where applicable.
- An append-only decision ledger recording predictions, rejected ideas, misses, failures and counterfactuals.
- Separate, testable layers for research, portfolio policy, risk constraints and eventual Saxo **simulation**.
- Independent code review, reproducible tests, restrained dependencies and documentation understandable to human engineers.

## Safety boundary

No broker credentials or private account data may be committed. **Live orders and leverage are out of scope** until a separately reviewed and expressly authorized release. Formal verification establishes correctness relative to stated assumptions, not profitable real-world forecasts.

## Next steps

1. Import Claude's completed research as a reviewed, versioned proposal.
2. Establish one canonical engineering policy for Codex and Claude Code.
3. Run an independent architecture review before writing production components.
4. Add minimal reproducible project tooling, tests and CI.
5. Connect Saxo SIM only after the risk and execution contracts are verified.

See the pull requests for the development history. Do not merge unreviewed changes to the main branch.
