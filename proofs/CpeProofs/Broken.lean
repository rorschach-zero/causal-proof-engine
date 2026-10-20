-- Negative control of the Lean job (17 T-40): the threshold is wrong (1/10 instead of 4/49), so this file
-- must fail to compile with "linarith failed". It is not imported by the library root and is compiled on its
-- own by tools/lean_check.sh, which turns a successful compilation of this file into a red job.
import Mathlib

theorem positive_expected_multiple_iff_broken (p : ℝ) :
    p * (10 : ℝ) + (1 - p) * (1 / 5 : ℝ) > 1 ↔ p > 1 / 10 := by
  constructor <;> intro h <;> linarith
