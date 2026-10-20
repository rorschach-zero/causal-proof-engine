-- Root of the CpeProofs library: the retained lemmas of research/04-formal-verification.md section 1, carried
-- verbatim from the archived reference package (proofs/BetThreshold.lean, proofs/RiskBudget.lean) and compiled
-- on the pinned toolchain (lean-toolchain, lake-manifest.json). A compiled theorem proves that conclusions follow
-- from listed hypotheses; it never certifies a forecast, an edge or an outcome.
import CpeProofs.BetThreshold
import CpeProofs.RiskBudget

-- The axioms of every retained theorem are printed on every build (the archived files print four of them).
#print axioms positive_expected_multiple_iff
#print axioms long_call_loss_at_most_premium
#print axioms purchased_call_budget
#print axioms CPE.growth_min_at_lower_bound
#print axioms CPE.expected_multiple_mono
#print axioms CPE.fully_paid_worst_loss_le_cap
#print axioms CPE.portfolio_worst_loss_le_sum_caps
#print axioms CPE.portfolio_worst_loss_le_budget
#print axioms CPE.implication_prob_le
#print axioms CPE.eprocess_factor_nonneg
