-- Compiled and checked 2026-10-16 with Lean leanprover/lean4:v4.35.0 and Mathlib rev cfc55fc58714a59dc06e6e79edc6d1d95140d3c2 (see proofs/lean-toolchain, proofs/lake-manifest.json).
-- Proves ALGEBRA under stated hypotheses only; says nothing about p's empirical value.
import Mathlib

-- If the return is 10x on success and 0.2x on failure, expected multiple >1
-- iff success probability >4/49. This proves algebra only, not p's empirical value.
theorem positive_expected_multiple_iff (p : ℝ) :
    p * (10 : ℝ) + (1 - p) * (1 / 5 : ℝ) > 1 ↔ p > 4 / 49 := by
  constructor <;> intro h <;> linarith

-- A fully paid call cannot lose more than its premium when its terminal payoff is nonnegative.
theorem long_call_loss_at_most_premium (premium payoff : ℝ)
    (hpayoff : 0 ≤ payoff) : premium - payoff ≤ premium := by
  linarith

-- If an order's premium does not exceed a budget, the terminal premium loss does not exceed it.
theorem purchased_call_budget (premium payoff budget : ℝ)
    (hpayoff : 0 ≤ payoff) (hbudget : premium ≤ budget) :
    premium - payoff ≤ budget := by
  linarith
