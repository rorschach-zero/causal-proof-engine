# 03 Probability and causal modeling

Entry point for `03/01`, `03/03` (fusion is covered in `05-multi-model-orchestration.md`), `03/05`, `04/01`,
and the identification-class rules in `02/01` §4.2. §1–§4 summarise the original; §5 is review.

## 1. Coherence by credal sets (Design A) — ESTABLISHED

Given binary events E₁…Eₙ, world states Ω = {0,1}ⁿ, marginal intervals [lᵢ, uᵢ] and logical constraints
A ⇒ B (worlds with A ∧ ¬B removed), the credal set is

P = { q ≥ 0 on Ω : Σ q = 1, lᵢ ≤ Σ_{ω∈Eᵢ} q(ω) ≤ uᵢ, q(ω) = 0 on forbidden ω }.

Feasibility and bounds for a target event T come from two linear programmes (min and max of Σ_{ω∈T} q). This is
probabilistic logic (Nilsson 1986) and imprecise probability (Walley 1991). The reference implementation
(`ref/cpe/coherence.py`, HiGHS via SciPy) is correct for n ≤ 14 (16,384 worlds in ≈ 0.3 s, REPRODUCED).

Known limits stated by the package: exponential in n; an LP with zero objective returns an arbitrary vertex
(attack F8), so only the interval output may be used downstream; conditional information P(B | A) does not
enter; intervals become vacuous when many events are loosely constrained; coherence is conditional on the
asserted constraints and says nothing about their truth.

**Reference distribution** (`03/01` §2, not implemented): if a single distribution is needed for reporting,
it is a labelled estimator, either maximum entropy over P or minimum KL to a Design-C prior. The allocator
uses the vertex set of P (max-min), never a single distribution.

**No multiplication of marginals** (`03/01` §4): for E ⇒ D ⇒ C only P(E) ≤ P(D) ≤ P(C) follows; multiplying
conditionals assumes an independence that investment chains violate (shared drivers: financing regime,
management, demand).

## 2. Credal network (Design B) — HYPOTHESIS as a research engine

Nodes = EventSpecs, edges = mechanisms. Each researcher gives conditional intervals P(child | parent
configuration) only where it can justify them; inference by M = 2,000 Monte Carlo draws of the CPT entries
uniformly within the fused intervals; target interval = [5th, 95th] percentile plus the min/max hull.
Complexity O(M · edges). The package states plainly that uniform sampling is a heuristic and does not recover
exact credal bounds (exact credal inference is NP-hard; 2U exists for polytrees). The exact LP is run on the
≤ 14-node decision projection; on disagreement the LP governs and the gap is logged.

Pre-registered claim: Design B is better calibrated than A on graphs with > 14 nodes; tested by ablation after
150 resolved events.

## 3. Base-rate hazard baseline (Design C) — the competitor that must be beaten

No graph, no LLM: cohort base rates of milestone events and 10x outcomes conditioned on observable firm
characteristics at the as-of date, with conformal prediction intervals. Design C also supplies the floor for
rare probabilities (`03/05` §2) and the prior for the min-KL reference distribution.

## 4. What "causal" means in CPE (`04/01` §2, `02/01` §4.2)

In v0.1 the "causal graph" was logical implication only (finding P0-SCI-02). v0.2 splits claims into:

- **logical links** (A ⊆ B by definition, e.g. "revenue > X" ⇒ "revenue > Y" for X > Y, "approval granted" ⇒
  "application filed"): the only constraints that enter the LP; certified by the Lean lemma `implication_prob_le`;
- **mechanisms** with a mandatory `identification_class ∈ {natural_experiment, instrument, policy_variation,
  dose_response, none}`, an exogenous-variation description, stated assumptions, dated primary sources,
  counter-mechanisms and substitutes. Class `none` mechanisms inform the narrative and the event decomposition
  only; they never become probability constraints.

The edge is tested on event forecasts, not on the truth of the DAG. The package rejects both "LLM narrative as
DAG" and "trend following finds yesterday's winners": mechanisms generate hypotheses, events test them, prices
are late information.

**Rare probabilities** (`03/05`): never elicit below 0.05; decompose into a chain of conditional events each in
[0.1, 0.9] where possible, each a registrable event with its own horizon; derive the rare interval through the
credal net or LP; floor the lower bound by the cohort base rate with cohort size reported; round to 0.05 when
the cohort is under 200; evaluate rare targets by discrimination only for two years.

## 5. Review

**Coherent mathematical foundation? Partly.** The pieces that are mathematics (credal LP, implication
ordering, convex pooling of intervals, max-min growth over a finite credal set) are correct and standard. The
piece that is called "causal" is a labelling discipline, not an inference procedure. That is defensible as long
as nobody claims the system *identifies* causal effects. Concretely:

1. **Identification classes are declared, never verified.** Nothing checks that a mechanism labelled
   `natural_experiment` has the properties of one (exogenous assignment, no anticipation, no simultaneous
   confounder). A researcher model can type any label. REVISION: for each class, require a typed
   `identification_argument` with the specific fields that class needs (for a natural experiment: the assignment
   variable, the treated and control units, the timing, the stated threats to validity), and let round 2 of the
   adversarial protocol target exactly those fields. Score, over time, whether mechanisms of each class predict
   their downstream events better than class `none`; if they do not, the taxonomy is decoration.
2. **The LP ignores conditional structure; the credal net ignores exactness; the hand-off between them is
   informal.** "On disagreement the LP governs" is only meaningful on the ≤ 14-node projection. Define the
   projection rule (which nodes are "decision-relevant") before the first forecast, and log the projection per
   PCCB. REVISION: consider replacing uniform CPT sampling with vertex enumeration per edge (interval
   endpoints), which gives an outer bound of the credal net's hull on small graphs and makes the A/B comparison
   meaningful.
3. **Two sources of width are conflated.** Interval width in CPE mixes epistemic disagreement between models,
   imprecision inside each model, and the Monte Carlo spread of Design B. Report them separately; the ABSTAIN
   thresholds (`03/03` §4) act on the total and will fire for the wrong reasons otherwise.
4. **Decomposition chains are not free of the independence problem.** `03/05` prescribes decomposing a rare
   target into milestone events, each in [0.1, 0.9]. The implied rare probability then comes from the credal
   net, which is correct, but the *elicitation* of each conditional from a model that has just seen the whole
   chain is not independent across links (a model that believes the thesis will inflate every conditional).
   Elicit links in separate calls with only the parent context, and test chain-level calibration against
   base rates of the full chain where cohorts exist.
5. **The base-rate floor needs its own evidence.** Design C base rates for milestone events (regulatory decisions,
   certifications, contract awards) require historical cohorts that nobody has assembled. Until they exist the
   floor is a guess; the package's rule "no floor → discrimination only" (`06/03`) is the right fallback, but it
   should be the *default* assumption for year one, not the exception.
6. **Which probability claims can be formally verified** (also in `04-formal-verification.md`): the
   implication-ordering bound, the LP bounds themselves (via dual certificates), convexity-preservation of the
   fused interval, the max-min reduction to vertices, nonnegativity of the e-process factor, worst-loss bounds.
   **Which require empirical calibration:** every interval any model emits, every Design-C base rate, every
   Jev classification probability, the Design B heuristic hull, and the central transfer claim. Formal
   verification can establish that the machinery respects the axioms; it cannot say anything about whether the
   inputs are honest.
7. **Novelty assessment** (also in `10-adversarial-review.md` §7): credal LP coherence + imprecise pooling +
   anytime-valid testing are each established; the combination with a typed identification taxonomy and a
   commit-before-resolve registry as an operating discipline is an integration proposal. The genuinely new,
   testable hypothesis is that this discipline produces measurable milestone skill (H1) and lead time (H5).
   Everything about 10x is downstream of that and is correctly deferred.
