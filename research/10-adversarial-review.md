# 10 Adversarial review

An independent scientific critique of the proposed CPE architecture, structured by the eight questions of the
handoff brief. Each section gives a verdict, the reasoning, and concrete improvements (numbered R-items are
specified in `11-proposed-improvements.md`). Labels follow `research/README.md`.

## 0. Conflict of interest and what this review rests on

The research package was written by Claude (Fable 5.1). This review was written by Claude Code, the same model
family. Shared training, shared blind spots and a pull toward self-consistency are real risks; the reader
should weight disagreements with the package more than agreements. To limit the risk, this review relied on
executable checks rather than on reading alone: the 31 and 11 reference tests were re-run, the v0.1 tree was
reconstructed by reverse patch and the ten attacks re-executed, the arithmetic was re-derived, and six probes
were written against behaviour the package's own tests do not cover (`00-research-inventory.md` §4,
`01-architecture.md` §3). Everything not executable (Saxo, provider terms, Lean compile, arXiv contents) remains
PACKAGE-VERIFIED or UNVERIFIED and is listed in `14-unverified-claims.md`. Codex should treat the agreements
below as hypotheses to attack.

## The five most important concerns, in order

1. **The discovery engine does not exist on paper.** The measurement apparatus is specified to the field;
   the source of candidate events is a paragraph. Without named source families, licences, parsers and a
   yield estimate, the 600-event year and H5 are unsupported (§8, N1).
2. **The year-one success criterion may be unreachable by construction.** Power was shown only against an
   uninformative baseline; against a real base-rate model the detectable Brier gain at 300–600 events with
   λ_max = 0.5 is unknown (§3, N8). If it is large, "failure" in year one would be uninformative.
3. **Independence of the three models is assumed, not engineered or measured at the source.** n_eff on errors is
   a lagging diagnostic. Same bundle, same triage, same prompt author (§4, R9).
4. **The reference code's safety properties are not properties of the code.** The gate is advisory in-process,
   the registry forgets its state on restart, late-YES is graded YES (§8 and `01-architecture.md` §3). Any
   implementation that starts from this code inherits the gaps unless they are designed out first (R1, R2, R4).
5. **The programme's load-bearing claim, milestone skill transfers to pre-trend 10x discrimination, has no
   test before year three** and no mechanism in the design that would make it more likely to be true. Every
   year-one result is compatible with its falsity (§8).

## 1. Does the causal forecasting architecture have a coherent mathematical foundation?

**Verdict: the probabilistic machinery is coherent; the causal layer is a taxonomy, not an inference method;
the two are correctly kept apart.**

What is sound (ESTABLISHED, checked): credal sets by LP with implication constraints and exact bounds; the
rule that only logical links constrain probabilities; the ban on multiplying marginals; convex pooling of
intervals preserving coverage; max-min log growth over a finite credal set reducing to vertices; the test
supermartingale with predictable λ < 1 and Ville's inequality; the worst case at the lower probability bound.

What is not mathematics: "mechanism with identification class". Declaring a mechanism a natural experiment does
not identify anything. The package knows this (`04/01` §2) and routes class-`none` claims away from the
probability layer, which is the right firewall. But classes other than `none` get no verification either; they
differ from `none` only by a label.

What is heuristic and labelled as such: Design B's uniform CPT sampling (not a credal bound); the reference
distribution (not implemented); the λ rule's power (not its validity).

Where the foundation is incomplete: the interface between the credal net (hundreds of nodes) and the exact LP
(≤ 14) is "projection to decision-relevant events", undefined; width from model disagreement, within-model
imprecision and Monte Carlo spread are summed into one interval that drives ABSTAIN decisions; the scoring
quantity for interval forecasts is the midpoint, which never rewards honest width.

Improvements: R5 (typed identification arguments per class, scored over time), R6 (vertex-endpoint credal
inference and a declared projection rule), R7 (decompose width into its sources; abstain on the right one), N7
(declare the scored quantity and add a proper interval score).

## 2. Can multiple models and Jev produce a measurable advantage over simpler alternatives?

**Verdict: measurable yes, because the ablation table contains the right controls; advantage unknown; the
design under-engineers the one property, independence, that would make an advantage attributable to the
committee rather than to volume.**

The decisive controls exist: single-LLM arms, the equal-weight pooling arm (isolates correlation-aware
fusion), the −Jev arm at equal recall budget (isolates Jev versus rules plus a local classifier). One control is
missing: a single model playing all three roles with self-consistency sampling (R10). If FULL fails to beat
that, the three-provider committee is paying for diversity it does not get.

Fusion mechanics: the correlation-only weighting ignores accuracy (probe P4, R8); the 2-of-3 ban makes the
slowest provider the throughput cap, correctly; the owner-started OpenAI batch is a different experimental
condition unless logged and constrained (R11). Jev's thresholds are pre-registered constants chosen without
Jev data; one pre-registered recalibration after the first 200 documents should be allowed (R12).

Jev specifically: the independent evaluation cited (mean complement gap 0.064, five times repeat noise) makes
Jev a classifier with measurable incoherence, exactly how the package uses it. Its mandatory status is an owner
decision; scientifically, its justification is H3 and nothing else, and H3 is testable within the year.

## 3. Which probability claims can be formally verified and which require empirical calibration?

**Verdict: the package draws this line correctly in prose; the current Lean content sits almost entirely on
the trivial side of it.**

Formally verifiable (and worth it, R13): LP bounds via dual certificates in exact arithmetic; allocation
certificates against concrete limits; gate state-machine safety; ledger verification properties; the
supermartingale property and Ville's inequality under explicit measurability assumptions; coverage
preservation of convex interval pooling.

Formally verifiable but currently vacuous: the ten existing lemmas (linear arithmetic). Keep them as pipeline
proof, do not cite them as risk evidence.

Empirical only: every interval any model emits; Design-C base rates; Jev probabilities; Design B's hull; the
central transfer claim; H6's net benefit. No proof can touch these, and the package says so.

A specific statistical point: the e-process is valid only if the registry is the sole writer of resolutions, in
resolution order, with λ computed before each outcome is incorporated. The reference code keeps two separate
commit concepts (registry and e-process) and no ledger replay. Validity in practice depends on R2 and R3.

## 4. Risks from shared model bias, hallucinations, data leakage and backtest overfitting

**Shared bias.** Three frontier models on overlapping corpora, one evidence bundle, one prompt author. n_eff
detects error correlation after the fact; it does not detect shared *omissions* (all three miss the same
counter-mechanism), which is the failure mode that matters for rare events. R9 adds source-level diversity and
reasoning-overlap metrics; R10 adds the single-model control.

**Hallucination.** The design's defence is structural: forecasts must cite evidence ids from the archived
bundle; events must have a named resolution source; Jev checks "dated primary evidence". Residual risk: a model
fabricates a mechanism that is consistent with real evidence; the system cannot tell. Defence is the adversarial
round and, over time, the identification-class scoring (R5). Round 2 only runs on ABSTAIN items today; a random
audit sample of FORECAST items should also go through round 2 (R14).

**Data leakage.** The controls are good: `known_at` inside the resolution window rejected (tested), publication
lags, vintage data, model knowledge cutoffs recorded and cutoff-overlapping events excluded. Two gaps: cutoff
dates published by providers are approximate and models have post-cutoff tool access unless disabled; prompts
must forbid browsing and the adapter must verify the model configuration per call (R15). And the owner-batch
path lets a human see items before commitment (R11).

**Backtest overfitting.** There are no backtests yet, which is the honest state. When they come: Design C and
the hazard model are the trained components; purged, embargoed walk-forward and the single primary test are
specified. The crisis backtest set of ~8 episodes cannot support H6 beyond exploration (`07-portfolio-and-risk.md`
§6 item 5). The ablation table's ten arms are ten tests without family-wise control (N9).

## 5. How should the system improve without optimising against its own test data?

**Verdict: the proposer/promoter design is correct in shape; four details decide whether it works.**

(1) Canaries must live in a promoter-only namespace, never in researcher-visible or calibration data (R16).
(2) The promoter must pin its whole evaluation environment and accept artefacts only as data, never as code
(R17). (3) Frozen historical holdouts are screening only; confirmation comes from events registered after the
proposal (rolling prospective holdouts) (R18). (4) The α-budget should be replaced by what e-values natively
support: multiplicative combination for independent artefacts, e-BH for discovery control (R19).

And the simplest control of all: live P&L is never an input to promotion. The package states it; the
implementation should make it impossible by data access, not by policy (the promoter principal has no read path
to the broker ledger).

## 6. How must survivorship bias and missing historical failures be handled?

**Verdict: the package's Wald test is the right frame; it is unfunded for history and unbuilt for the future.**

Forward: from the first `/ref` snapshot, every listing including later bankruptcies, delistings and reverse
splits; every candidate the scanner touched with `considered_at`, decision and reason; three shadow books.
This is cheap and must start on day one of SIM_READ_ONLY (R20); it is the only survivorship-free data the
programme will ever own.

Backward: Q5 was decided as "no licensed PIT dataset in year one". Consequence, stated plainly: there is no
historical cohort for Design C base rates on 10x outcomes, so the rare-probability floor has no data, and the
H6 crisis backtest universe is survivorship-biased unless a free delisting-inclusive source is found. The
package's fallback (discrimination only, no floor) is the honest one and should be the default assumption in
the year-one plan, not a contingency (`03-probability-and-causal-modeling.md` §5 item 5).

Event-level survivorship is not addressed anywhere and is new to this review: which events get *registered* is
a selection; failed theses that never produced a registrable event never appear in skill statistics. Register
the eligibility rule, log rejected candidates, and score a random subsample of eligible events (R21).

## 7. Which innovations are genuinely novel hypotheses rather than renamed existing techniques?

| Claimed innovation | Assessment |
|---|---|
| PCCB as a typed object joining origin, mechanism, events, belief, value capture, adversarial case, decision, audit trail | an integration and discipline proposal; each part is standard; the claim that the discipline yields skill is H1/H5, testable |
| Credal-set coherence of multi-model intervals | renamed existing technique (probabilistic logic, imprecise probability); the application to LLM committee outputs is new practice, not new method |
| Identification class on mechanisms gating what enters probability math | a useful editorial rule; becomes a hypothesis only with R5 (does class predict downstream skill?) |
| Commit-before-resolve registry plus e-process as the promotion criterion | established statistics (anytime-valid testing) applied as an engineering discipline; the novelty is institutional |
| Correlation-aware fusion with typed abstention and Jev gating | minimum-variance pooling is standard; typed abstention and triage gating are design choices whose value is H1/H3 |
| Proposer/promoter with canaries, time-shifted holdouts, shuffled labels | assembled from known ML-evaluation hygiene; the combination under anytime-valid tests is good practice, not a discovery |
| Hazard-driven throttle with hysteresis, never forced liquidation | a policy with a weak literature base, honestly flagged; H6 |
| Asset-class ladder, method scanner, 25-year core/shell | governance, not science |
| **"Discovery before trend acceleration" from first principles** | the only genuinely novel empirical hypothesis in the programme (H5 and the transfer claim); nothing in the design yet makes it more plausible than its negation |

Nothing in the package is misrepresented as a scientific discovery; the RFC says so in its first paragraph.
The risk is rhetorical drift later. The language rule in `02/04` §5 is the right guard.

## 8. What must be demonstrated before any investment strategy can be trusted?

In order, each a precondition for the next; none is met today.

1. **Restorable, tamper-evident record.** Registry rebuilt from the anchored ledger on a clean machine, anchor
   outside the researcher's reach, verified monthly, zero failures (R1, R2, R20).
2. **Supply.** A named source list producing registrable events at the planned rate for one quarter, with
   publication lags documented (N1).
3. **Power.** A published simulation showing the detectable effect at 300 and 600 events against a realistic
   Design-C baseline, and a year-one criterion set from it (N8).
4. **Skill.** H0 rejected on prospectively registered milestone events with the committed e-process, FULL
   beating every single-model arm and the single-model-three-roles control, n_eff > 1.5, abstention < 40 %,
   VOID < 10 %.
5. **Lead.** H5 measured by the specified external-mention process with a median ≥ 60 days.
6. **Discrimination.** Rank correlation of rare-target intervals with realised multi-year returns in the
   shadow book, from year 2 onward, with the random-selection control beside it.
7. **Operations.** SIM read-only, precheck and reconciliation clean for 60 consecutive days; executor as a
   separate principal replaying gate state from the ledger; fault-injection suite green; no token in any log.
8. **Economics.** Only then: a shadow book of USD 100,000 notional for ≥ 5 years with bootstrap intervals
   against the always-invested and random controls (H2). The USD 1,000 pilot, if ever enabled, tests
   operations, not alpha, and says so in every report.

Until item 4, the system is an event-forecasting experiment. Until item 6, it is not an investment research
system. Until item 8, no result about returns exists. The package says all of this; this review agrees and
adds that items 1–3 are missing from its own year-one plan as explicit gates.
