# 05 Multi-model orchestration

Entry point for the model roles and adapter contract (`02/01` §5), fusion (`03/03`), access routes (`02/03`),
and Jev (`RFC` §6, `02/01` §5). §1–§4 summarise the original; §5 is review.

## 1. Roles (`02/01` §5)

| | Claude (Fable class) | OpenAI (Astra class) | Gemini (Argon class) | Jev (TypeSafe) |
|---|---|---|---|---|
| Mandatory round-1 output | mechanisms, decomposition, intervals; ticker-free | adversarial reconstruction, counterexamples, Lean sketches, intervals | alternative futures, substitutes, value capture, intervals | triage noul pairs, choice classification, duplicate clustering |
| Forbidden | reading other models' round-1 output; tickers before mechanisms | broker orders | broker orders | anything but classification; any broker or account data |
| Calibration tracked | per forecaster, horizon, sector, source family | same | same | per question template; complement gap per call |
| Veto | may ABSTAIN → round 2 | same | same | complement gap > 0.15 → RE_RESEARCH |

Adapter contract: `research(bundle) → ResearchOutput` as typed JSON validated against a schema; three retries
with exponential backoff; hard daily token caps per provider; degradation ladder {full → cheaper model for
round 1 → queue}; a missing mandatory pre-trade input freezes new orders (gate auto-demotes to SIM_READ_ONLY).
Prompts (`ref/prompts/*.md`) are the round-1 instructions, versioned, hash recorded in every forecast.

Jev rules (`02/01` §5): high-volume triage of source type, event relevance, novelty, duplicates,
contradictions, escalation; head-to-head against cheap rules and a local model in a pre-registered randomised
ablation; coherence projection on its outputs; calibration against event-specific outcomes, never vendor
benchmarks. Jev never sizes trades, never estimates 10x probabilities from narratives, never overrides
certificates, never talks to Saxo.

## 2. Fusion (`03/03`, `ref/cpe/fusion.py`)

Inputs: three intervals plus a Jev triage record. Weights w = R_δ⁻¹1 / (1ᵀR_δ⁻¹1) from the error correlation
matrix of past standardised errors, shrunk toward identity with δ = 0.30; equal weights below 20 resolved
events or when any weight is negative or non-finite (flagged). Fused interval = convex combination.
Effective models n_eff = (Σw)² / (wᵀR_δw): 3 for independent equal weights, 1 for perfectly correlated.
Decision table (pre-registered constants): missing model or Jev record → RE_RESEARCH; Jev complement gap >
0.15 → RE_RESEARCH; Jev p(dated primary) < 0.60 or p(relevance) < 0.50 → RE_RESEARCH; any abstention →
ABSTAIN; midpoint spread > 0.30 → ABSTAIN; fused width > 0.35 → ABSTAIN; else FORECAST. Round 2 (adversarial
cross-examination) runs only for ABSTAIN items and creates new forecast ids; round-1 forecasts are never edited.

## 3. Access routes under the owner's subscription-only decision (`02/03`)

Claude: unattended via the Max plan's monthly Platform API credits (Agent SDK / Messages API); Gemini:
unattended if the terms read on setup day allow it, else owner-started batch; OpenAI: **owner-started daily
batch** (interactive Codex session, results into the registry; no unattended `codex exec` under a personal
login); Jev: API key, early access, ≈ USD 0.50/month at 200 documents/day. Consequence: an item receives a
forecast only when all three round-1 outputs exist; OpenAI items wait for the next batch (≤ 1 day delay).
Throughput is quota-bound: 5–10 full rounds per day, enough for 600 events per year. Terms pages re-read
quarterly with dated screenshots in the ledger. No consumer web UI is ever automated.

## 4. Where the RTX 5090 fits (`02/03` §6)

The −Jev ablation arm (local 7–14B classifier), embedding-based duplicate clustering, parsers, Monte Carlo for
the credal net, backtests. Not a substitute for any of the three frontier models (independence premise).

## 5. Review

**Can three models plus Jev produce a measurable advantage over simpler alternatives?** Unknown, and the
package is honest that it is unknown (H1, H3). The design does include the comparisons that would show it
(single-LLM arms, equal-weight pooling arm, −Jev arm). The problems are in whether the advantage, if any,
would be attributable to independence rather than to volume.

1. **Independence is asserted, not engineered.** The three models receive the same evidence bundle,
   produced by one ingest path and one Jev triage, under prompts written by one author in one style, asking
   for the same artefact types. Three frontier models trained on overlapping corpora will agree for shared
   reasons; n_eff measured on *errors* detects that only after many resolutions and only for the error
   component. REVISION: (a) measure reasoning overlap directly (Jaccard of cited evidence ids, of named
   mechanisms, of counter-mechanisms) per item and report it next to n_eff; (b) give the three roles
   genuinely different inputs where the protocol allows (e.g. the adversary receives the thesis fragments plus
   the evidence; the alternative-futures researcher receives the evidence only); (c) run a periodic
   "same-prompt" control in which all three get the identical Claude prompt, to measure how much of the
   observed diversity comes from the role prompts versus the models.
2. **Correlation-only weights ignore accuracy** (probe P4, `01-architecture.md` §3). Use the shrunk error
   *covariance* for minimum-variance pooling; keep the non-negativity fallback. Report n_eff on the
   covariance-implied correlation.
3. **The 2-of-3 ban makes availability the binding constraint.** With OpenAI as a daily human batch and
   quota caps everywhere, the pipeline's throughput is the slowest provider's. That is the right trade for the
   non-negotiable requirement; it must be measured (items waiting per provider, median latency to forecast)
   and the owner must accept that a provider outage pauses research, not that it degrades to two models.
4. **Owner-started batch is a contamination and consistency risk.** Specify that the batch runs the same
   adapter code with the same bundles, that the owner performs no selection or editing, and that the batch
   transcript hash is ledgered. Otherwise OpenAI forecasts are a different experimental condition.
5. **Jev's role is well bounded, but its gate thresholds (0.60 dated-primary, 0.50 relevance, 0.15 gap) are
   unmotivated constants.** They are pre-registered, which is good, but they were chosen without any Jev
   data. Plan an initial calibration phase (first 200 documents, both polarities, repeat calls) and allow one
   pre-registered amendment of these constants before the primary test starts; after that they are frozen.
6. **Prompt versioning is necessary but not sufficient.** Model versions change under the alias
   (`jev-latest`, provider model names). The adapter must record the returned model identifier and treat a
   change as a new forecaster id (the package says this for Jev; make it uniform).
7. **Schema first.** The adapter contract is prose. Writing the JSON schema for `ResearchOutput` (mechanisms
   with identification arguments, EventSpecs, interval forecasts, evidence ids, abstention) is cheap, enables
   the three adapters to be written independently, and lets the fusion and registry be tested with synthetic
   outputs before any provider is called. This is the first orchestration artefact to build.
8. **What a simpler alternative looks like, for the record:** one frontier model with three role prompts and
   self-consistency sampling, plus Design C. If FULL does not beat that control (it is not in the ablation
   table; REVISION: add it as the `single-model-three-roles` arm), the three-provider requirement is paying for
   independence it does not get. The requirement stays non-negotiable by owner decision; the arm tells the
   owner what it costs.
