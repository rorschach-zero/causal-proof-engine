# 04 Formal verification

Entry point for the Lean material (`03/01` §5, `ref/proofs/*.lean`, `evidence/lean_compile.log`) and for the
rule separating formal, statistical and empirical evidence (`02/04` §5). §1–§2 summarise the original; §3 is review.

## 1. What exists

| File | Theorem | Statement (informal) | Role claimed |
|---|---|---|---|
| `BetThreshold.lean` | `positive_expected_multiple_iff` | 10p + (1−p)/5 > 1 ⇔ p > 4/49 | pedagogical threshold |
| | `long_call_loss_at_most_premium` | payoff ≥ 0 ⇒ premium − payoff ≤ premium | loss bound for long options |
| | `purchased_call_budget` | premium ≤ budget ⇒ premium − payoff ≤ budget | budget bound |
| `RiskBudget.lean` | `growth_min_at_lower_bound` | growth linear in p is minimised at p_low when success ≥ failure branch | justifies using `p_success_low` in the Kelly code |
| | `expected_multiple_mono` | arithmetic expected multiple monotone in p when up ≥ down | |
| | `fully_paid_worst_loss_le_cap` | 0 ≤ w ≤ c, 0 ≤ down ≤ 1 ⇒ w(1 − down) ≤ c | per-position worst loss ≤ cap |
| | `portfolio_worst_loss_le_sum_caps`, `portfolio_worst_loss_le_budget` | Σ losses ≤ Σ caps ≤ B | portfolio budget |
| | `implication_prob_le` | A ⇒ B, q ≥ 0 ⇒ Σ_A q ≤ Σ_B q | LP monotonicity, formally |
| | `eprocess_factor_nonneg` | 0 ≤ λ ≤ 1, −1 ≤ x ≤ 1 ⇒ 1 + λx ≥ 0 | nonnegativity needed by Ville |

Toolchain pin: Lean `leanprover/lean4:v4.35.0`, Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`
(`lean-toolchain`, `lake-manifest.json`). The package reports exit 0 for both files with only the standard
axioms (`propext`, `Classical.choice`, `Quot.sound`) and a negative control (`Broken.lean`, threshold 1/10
instead of 4/49) failing with `linarith failed` (`evidence/lean_compile.log`). **Status: PACKAGE-VERIFIED.
Not re-compiled in this session** (no Lean toolchain; Mathlib cache ≈ 8 GB). The Lean sources were read and are
syntactically plausible; the proofs are one-tactic (`linarith`, `nlinarith`, `Finset.sum_le_sum`).

## 2. The semantics the package insists on (`03/01` §5, `02/04` §5)

A compiled theorem proves that a conclusion follows from listed hypotheses. It never proves that a hypothesis
(an interval, a payoff multiple, a correlation) is true of the world. Certificates are always read as "under
H₁…Hₖ, C" and list H₁…Hₖ. H4 is therefore not a hypothesis but a statement about the model: a certified order
plan has zero logic and budget violations *in the certified model*. On toolchain change all proofs are
recompiled; a proof that no longer compiles loses its status until repaired. The system may never say
"proved" where it means "supported".

## 3. Review

**Is the current formalisation valuable? Barely, and the package admits it** ("trivial linear arithmetic,
proves nothing about markets", `01/02` P2-LEAN-01). The ten lemmas verify facts a reviewer checks in seconds.
Their value is procedural: the pipeline for pinned, CI-checked Lean exists and a negative control shows the
checker is live. That is worth keeping. What is missing is any theorem whose *failure* would catch a real bug.

**What would be worth formalising (REVISION), in order of value per effort:**

1. **Proof-carrying LP bounds.** The credal LP's min/max bounds are the one place where the system's
   probability claims are mathematical. An LP solver's answer is not a proof; a *dual feasible solution* is a
   certificate: any dual-feasible y gives bᵀy ≤ optimum (weak duality). Emit the dual with every bound and check
   it in exact rational arithmetic; the check is linear arithmetic over rationals that Lean's `norm_num` /
   `linarith` or a verified checker handles, and it scales to 16,384 worlds. This makes "proof-carrying" literal
   for the coherence layer and makes the Design-A certificate independent of SciPy.
2. **Allocation certificate checking.** Given a concrete allocation w, caps, gross cap, max loss and the scenario
   matrix R, verify in exact arithmetic that every constraint holds. This is decidable and cheap, and it is the
   actual safety property the executor needs ("this order plan respects the limits"), as opposed to the
   generic lemma that sums of caps bound sums of losses. Encode the constraint set once; check each certificate.
3. **Gate state machine safety.** Model the gate as a finite transition system (states, `promote` guarded by a
   valid owner MAC and one-step adjacency, `demote` unguarded) and prove the invariant "no state at or above
   SIM_PRECHECK is reachable without an owner-authorised transition from the previous state". Lean can do
   this over an inductive type; so can a lighter tool (TLA+, Alloy). The property is simple, but it is the one
   the owner cares about, and the reference code currently violates it (probe P5, `01-architecture.md` §3).
4. **Ledger verification specification.** Specify `verify_chain` and `verify_against_anchor` as functions on
   lists of entries and prove: any single-entry change after the anchored prefix is detected; truncation below
   the anchored length is detected. This pins the threat model T1–T3 to a proof instead of a test.
5. **The test supermartingale.** Proving that M_n = Π(1 + λ_t X_t) with predictable λ_t ∈ [0, λ_max] and
   E[X_t | F_{t−1}] ≤ 0 is a nonnegative supermartingale, and Ville's inequality for it, is a real but
   bounded Mathlib project (conditional expectation and martingale theory exist in Mathlib). Value: it turns the
   programme's central statistical guarantee into a checked statement under explicitly listed measurability
   assumptions, which is where mistakes in practice hide (λ computed from the current outcome, duplicate events).
6. **Interval pooling preserves coverage.** If each [lᵢ, uᵢ] contains p and wᵢ ≥ 0 sum to 1, then Σ wᵢ lᵢ ≤ p ≤
   Σ wᵢ uᵢ. One line; worth having because the fusion rule relies on it and negative weights are the failure mode.

**What must never be claimed about Lean here:** that a theorem certifies a forecast, an edge, or an outcome.
The package already states this correctly; keep the sentence in every certificate.

**Process recommendations.** Lean CI job on the pinned toolchain from the first implementation PR; each
theorem carries a docstring naming the code path that depends on it and the hypothesis list; `#print axioms`
output archived per build; a theorem with no dependent code path is removed (no decorative proofs).
