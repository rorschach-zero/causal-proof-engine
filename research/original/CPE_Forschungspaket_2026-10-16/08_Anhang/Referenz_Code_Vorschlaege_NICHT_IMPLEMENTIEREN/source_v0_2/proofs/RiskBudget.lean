/-
CPE v0.2 — risk-budget certificates.
Toolchain pin: see lean-toolchain and lake-manifest.json in this project.
Everything here is conditional algebra over the reals. A compiled theorem proves
that CONCLUSIONS follow from HYPOTHESES; it never establishes that a hypothesis
(a probability interval, a payoff multiple, a correlation) is true of the world.
-/
import Mathlib

namespace CPE

/-- Two-state log-growth of wealth fraction `w` with success probability `p`,
    success log-multiple `ls = log(1 + w(up-1))` and failure log-multiple `lf`.
    We take `ls, lf` as given reals so the statement is pure linear algebra. -/
def growthLin (p ls lf : ℝ) : ℝ := p * ls + (1 - p) * lf

/-- Worst case over a probability interval is attained at the LOWER bound
    whenever the success branch is at least as good as the failure branch.
    This is the justification `core.py` relies on when it uses only `p_success_low`. -/
theorem growth_min_at_lower_bound (pl ph p ls lf : ℝ)
    (hpl : pl ≤ p) (_hph : p ≤ ph) (hls : lf ≤ ls) :
    growthLin pl ls lf ≤ growthLin p ls lf := by
  unfold growthLin
  nlinarith

/-- Arithmetic expected multiple is monotone in `p` when `up ≥ down`. -/
theorem expected_multiple_mono (pl p up down : ℝ)
    (hpl : pl ≤ p) (hud : down ≤ up) :
    pl * up + (1 - pl) * down ≤ p * up + (1 - p) * down := by
  nlinarith

/-- A fully paid long position with wealth fraction `w` and worst terminal
    multiple `down ∈ [0,1)` loses at most `w * (1 - down)` of wealth, and this is
    bounded by the position cap `c` when `w ≤ c`. -/
theorem fully_paid_worst_loss_le_cap (w c down : ℝ)
    (hw0 : 0 ≤ w) (hwc : w ≤ c) (hd0 : 0 ≤ down) (_hd1 : down ≤ 1) :
    w * (1 - down) ≤ c := by
  nlinarith

/-- Portfolio-level budget: if every position's worst-case loss is bounded by its
    cap, the total worst-case loss is bounded by the sum of caps. -/
theorem portfolio_worst_loss_le_sum_caps {ι : Type*} (s : Finset ι)
    (loss cap : ι → ℝ) (h : ∀ i ∈ s, loss i ≤ cap i) :
    ∑ i ∈ s, loss i ≤ ∑ i ∈ s, cap i :=
  Finset.sum_le_sum h

/-- If the sum of caps is within the gross budget `B`, so is the total worst loss. -/
theorem portfolio_worst_loss_le_budget {ι : Type*} (s : Finset ι)
    (loss cap : ι → ℝ) (B : ℝ) (h : ∀ i ∈ s, loss i ≤ cap i)
    (hB : ∑ i ∈ s, cap i ≤ B) :
    ∑ i ∈ s, loss i ≤ B :=
  le_trans (portfolio_worst_loss_le_sum_caps s loss cap h) hB

/-- Implication coherence: if event A implies event B (A ⊆ B as sets of worlds)
    then P(A) ≤ P(B). Stated for a finite world space with a nonnegative weight. -/
theorem implication_prob_le {Ω : Type*} (s : Finset Ω) (q : Ω → ℝ)
    (A B : Ω → Prop) [DecidablePred A] [DecidablePred B]
    (hq : ∀ ω ∈ s, 0 ≤ q ω) (hAB : ∀ ω, A ω → B ω) :
    ∑ ω ∈ s with A ω, q ω ≤ ∑ ω ∈ s with B ω, q ω := by
  apply Finset.sum_le_sum_of_subset_of_nonneg
  · intro ω hω
    simp only [Finset.mem_filter] at hω ⊢
    exact ⟨hω.1, hAB ω hω.2⟩
  · intro ω hω _
    exact hq ω (Finset.mem_filter.mp hω).1

/-- E-process step factor is nonnegative when the bet fraction is in [0,1] and the
    score difference is in [-1,1]; nonnegativity is what Ville's inequality needs. -/
theorem eprocess_factor_nonneg (lam x : ℝ)
    (hl0 : 0 ≤ lam) (hl1 : lam ≤ 1) (hx : -1 ≤ x) (_hx1 : x ≤ 1) :
    0 ≤ 1 + lam * x := by
  nlinarith

end CPE

#print axioms CPE.growth_min_at_lower_bound
#print axioms CPE.portfolio_worst_loss_le_budget
#print axioms CPE.implication_prob_le
#print axioms CPE.eprocess_factor_nonneg
