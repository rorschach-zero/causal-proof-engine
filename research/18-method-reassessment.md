# 18 Method reassessment of the Phase 1 statistical proof (PROPOSED)

Constructive reassessment requested by the owner's research directive on PR #4 (comment `6283736614`,
2026-10-20 04:57 UTC): before further incremental rounds, decide whether the confirmatory method of
`17-phase1-amended-specification.md` is identifiable, valid and practically useful, compare it with fundamentally
different approaches, and recommend whether to retain, simplify, replace or narrow the claim. Status:
**PROPOSED**, a `REVISION` of this review. It changes no text of `17` and no owner decision. Nothing here
authorises implementation, merges, broker access, spending or a governance change.

**Baseline.** The directive names `a22f9df2e2621df4d8b5c51c2f5e326c7504b74a` as the baseline to verify against
live HEAD. On 2026-10-20 `origin/claude/reconciliation-round-1` resolved to exactly that SHA, so this document
reassesses `17` version 49 and `16` v53 as they stand there. Codex's automatic review of `a22f9df` is recorded
as failed (summary comment `6216072575`, 2026-10-19 06:10 UTC), with no findings posted, so nothing in this
document rests on a Codex review of that commit.

**Revision R2 (2026-10-20).** Codex reviewed R1 at `f7aba62` (review `5581408643` and PR comment `6284764514`). R2
applies the ten findings that reproduce, RC-281, RC-282 and RC-284 to RC-291 (`16` §3az):
- the sharp Brier-increment bound d(2 − d) in F6, F8 and M-7;
- a complete validity class 𝓛 in place of the scalar bound ρ_max, covering shape as well as dependence (F3);
- the estimand weighting (F10);
- the zero-crossing bound (F8);
- exact noncentral-t power (§3);
- valid JSON output;
- what Phase 2 can measure without outcomes (§3);
- the M-6 generator (§7);
- the experiments inventory of `16` §7.

The commit-identity finding (RC-283) does not reproduce and is recorded for OD9b.

**Revision R3 (2026-10-20).** Codex reviewed R2 at `69c2e00` (PR comment `6285725411`, five findings). R3 applies
the four that reproduce, RC-292 and RC-294 to RC-296 (`16` §3ba):
- c_𝓛 is a cutoff certified at size ≤ α by an order-statistic bound, not the empirical 0.95 quantile, and M-1 no
  longer accepts 0.06 (F3, §7; S9);
- the weighted statistic of F10 uses a leverage-corrected variance and a calibrated cutoff, never the nominal t (S11);
- every component of the fixed sequence has its own validity class and certified cutoff (F7, §6; S10);
- M-4 compares power with the noncentral-t power at the cutoff actually used (S9).

The commit-identity finding (RC-293) does not reproduce and is recorded for OD9b.

**Revision R4 (2026-10-20).** Codex reviewed R3 at `038714c` (PR comment `6286736153`, five findings). R4 applies
the four that reproduce, RC-297, RC-298, RC-300 and RC-301 (`16` §3bb):
- 𝓛 is a class of centred shapes, the laws of M_b − θ. The null is every θ ≤ 0 shift of a law in 𝓛, and the boundary
  θ = 0 is least favourable because both statistics move monotonically under a shift (F3; S12);
- the 0.01 calibration budget is spent across the union of all laws of all components and statistics (F3, F7; S13);
- a calibration too small to certify any cutoff is refused (F3, M-1; S14);
- F1 states the covariance assumptions behind its variance and gives the general expression (S15).

The commit-identity finding (RC-299) does not reproduce and is recorded for OD9b.

**Revision R5 (2026-10-20).** Codex reviewed R4 at `67c7c03` (review `5583218458`, two inline findings). R5 applies
the one that reproduces, RC-302 (`16` §3bc):
- the 99 % certificate alone bounds the unconditional size of calibration and test together only by
  0.99·α + 0.01 = 0.0595. The level claimed is now the unconditional size of the whole procedure, which is
  (j + 1)/(n + 1) ≤ α on every law of 𝓛 by exchangeability, and the certificate is stated as a separate, conditional
  guarantee. A certified index whose unconditional size would exceed α is refused (F3, §6, M-1; S16).

The commit-identity finding (RC-303) does not reproduce and is recorded for OD9b.

**Revision R6 (2026-10-20).** Codex reviewed R5 at `2a37e0d` (PR comment `6288785191`, four findings). R6 applies
the three that reproduce, RC-304, RC-306 and RC-307 (`16` §3bd):
- the unconditional size is a statement over the calibration randomness, so that randomness must be redrawn in every
  repetition of the procedure. M-1 no longer recomputes c_𝓛 from pre-registered seeds: the seed is drawn from a
  public beacon round published after the calibration record is anchored, the rule `17` already applies to its
  simulated families, and the calibration runs once. A fixed, chosen seed makes the cutoff a constant whose size only
  the conditional certificate covers (F3, M-1; RC-304);
- for a class of several laws, (j + 1)/(n + 1) is an upper bound on the size, not its value, and S16 now simulates
  the complete multi-law calibration and test (F3, §8; S16; RC-306);
- the reading order of `research/README.md` names R5 and R6 (RC-307).

The commit-identity finding (RC-305) does not reproduce and is recorded for OD9b.

**Revision R7 (2026-10-20).** Codex reviewed R6 at `9308e43` (review `5584264319`, three inline findings). R7
applies the two that reproduce, RC-309 and RC-310 (`16` §3be):
- the one-record rule of R6 bound a cohort, not a claim. Records anchored under different cohort identifiers let an
  operator run only the cohort with the smallest cutoff, whose size exceeds (j + 1)/(n + 1) for every m ≥ 2 records
  (S17). Each record is now bound to exactly one claim before its beacon round, every bound claim is reported, and
  a statement over several claims certifies each at α/S_max. S_max therefore does not lapse under OD11 (b) (F3,
  M-1, the claim wording, §8, §9; RC-309);
- the seed check R6 quoted for the three-law simulation is committed output of S16. Pooled without the seed that
  prompted it, and on unselected seeds of the normal law alone, the rate is consistent with the exact value (F3;
  RC-310).

The commit-identity finding (RC-308) does not reproduce and is recorded for OD9b.

**Revision R8 (2026-10-20).** Codex reviewed R7 at `008111e` (review `5584951289`, four inline findings). R8 applies
the three that reproduce, RC-311, RC-312 and RC-314 (`16` §3bf):
- R7 fixed the number of confirmatory claims before the first beacon round but not which claims they are. With
  several bound claims and S_max = 1, the operator could read every cutoff and then label the one with the smallest
  confirmatory: that is the minimum-of-m selection of S17 again. The set of confirmatory claims, by identifier, is now
  anchored with S_max before the beacon round of any record bound to a claim of the family, and a claim's status
  never changes (F3, M-1 (i); RC-311);
- R7 applied α/S_max only in the final bound check, while the index, the certificate and the fresh-size check stayed
  at α, and `certified_index` hard-coded α. Each confirmatory claim is now calibrated at α/S_max throughout: index,
  certificate, refusal, fresh-size check and bound (F3, M-1, the claim wording, §8; S18; RC-312);
- the OD10-record check of `check_appendix_scripts.py` also rejects an entry for a version outside 23 to the
  specification version (RC-314; `16` §3bf).

The commit-identity finding (RC-313) does not reproduce and is recorded for OD9b.

**Revision R9 (2026-10-20).** Codex reviewed R8 at `62d4c2a` (review `5585864739`, three inline findings). R9
applies the two that reproduce, RC-315 and RC-317 (`16` §3bg):
- R8 anchored the confirmatory set per family, so an operator could anchor two family pre-registrations, each naming
  one confirmatory claim with S_max = 1, and test both at α. Phase 1 now has one confirmatory register, anchored once
  with S_max before the beacon round of any calibration record bound to any Phase 1 claim; it lists every
  confirmatory claim of Phase 1 by identifier, at most S_max of them across all families, and every other claim is
  exploratory (F3, M-1 (i), the claim wording, §9; RC-315);
- the OD10-record check of `check_appendix_scripts.py` also rejects any "version N" in the row that does not start
  an entry, whatever precedes it (RC-317; `16` §3bg).

The commit-identity finding (RC-316) does not reproduce and is recorded for OD9b.

**Evidence.** Every number below marked `REPRODUCED` comes from `research/reproduction/reassessment_sims.py`.
Its output is committed in `16` Appendix AW and checked by `check_appendix_scripts.py`. Derivations are paper
arguments, not Lean proofs. External literature is cited for orientation only: it was not re-read in this
execution and is `UNVERIFIED` as to exact statements.

## 0. Summary

| # | Finding | Label |
|---|---|---|
| F1 | Once a period-level component exists, the information in the primary is set by the number G of independent calendar periods, not by the number of events. As n → ∞ the minimum detectable effect tends to (t_α + t_β)·τ/√G. | derivation; REPRODUCED |
| F2 | An outcome-rate shock reaches the paired Brier difference only through FULL's mean lean away from the baseline: τ ≈ 2·s·\|E(p − b)\|. That quantity is observable before any outcome. | derivation; REPRODUCED on a toy law |
| F3 | No test of the average null over a finite G is valid under an unrestricted joint law of the period means. Validity needs a pre-registered, complete validity class 𝓛 of centred joint laws (shape and covariance), which 24 periods cannot verify. Neither a scalar bound on serial correlation nor independence alone is such a class. | ESTABLISHED in kind; REPRODUCED for AR(1), equicorrelation, odd/even shocks and a skewed law |
| F4 | Outcome-independent inclusion is not identifiable from listing data. It can be established only by design, and the reference-universe holder's own selection is unprovable from the data. | constructive counterexample; REPRODUCED |
| F5 | If the population is the reference universe itself and every one of its events is forecast, abstentions scored at baseline, the omission audit, draw and box rule add no identifying power. The universe already carries the whole selection assumption. | derivation |
| F6 | With omitted share m and divergence bound d, a paired Brier increment is bounded by d(2 − d), and the sign of θ is identified only if m < θ/(θ + d(2 − d)). At θ = 0.01 and d = 0.5 that means m < 1.32 %. | derivation; REPRODUCED |
| F7 | The six-comparator intersection-union conjunction loses power steeply. With 80 % marginals it rejects in 26 % (uncorrelated) to 68 % (r = 0.9). A fixed-sequence order keeps 80 % for the first claim at the same familywise α. | ESTABLISHED; REPRODUCED |
| F8 | The anytime-valid betting e-process crossed in none of 20,000 replications at G = 24 for δ ≤ 0.02 under every cap tested (99 % upper bound 0.023 %). It needs about 104–260 independent periods and a divergence bound. "Anytime-valid versus fixed-horizon" is not the binding choice; G is. | REPRODUCED |
| F9 | The record shows the signature of overfitting to review: 280 RC items in 52 rounds and a specification grown from 16.7 KB to 405.5 KB. Rounds 43–52 mostly repair consequences of the round-43 late-link rule or process metadata. | measured on the repository; the interpretation is a HYPOTHESIS |
| F10 | A period-level test fixes the weighting of its estimand. The unweighted block t estimates the period-balanced mean, not the mean over the questions of Q, and the two can differ in sign. | exact example; REPRODUCED |

**Recommendation (§6): narrow the claim and simplify the method.**

- **Keep** the infrastructure: ledger, timestamps, pre-registration, paired Brier, worst-case VOID bounds, and the e-process as monitor only.
- **Replace** source-selected events audited against a reference universe with an externally fixed question set forecast exhaustively.
- **Replace** the calibrated c* over an enumerated null class with linked variance blocks and every-subset late partitions, using instead a period-level test calibrated over one pre-registered validity class.
- **Replace** the six-way conjunction with a fixed-sequence family whose first claim is FULL against Design C.
- **State the claim** as forecast skill on that question set over that period, never as investment value.

The adoption is owner decision OD11 (§9); this document does not choose it.

## 1. The current method, stated exactly

From `17` §3 item 3, §6 and A3 at `a22f9df`. The table separates what the specification defines from what it
must assume.

| Element | As specified at `a22f9df` |
|---|---|
| Unit | pre-declared outcome cluster k; its paired increment X̄_k = mean over registration-time members of Brier(Design C) − Brier(FULL) |
| Population | the predicate-matching events of every eligible source's reference universe, listed in [T_0, τ), each cluster drawn with probability π by a beacon-seeded hash, membership fixed at registration |
| Estimand | θ = population mean of X̄_k over eligible clusters that resolve YES or NO |
| Null / alternative | H0: θ ≤ 0; H1: θ > 0 (one-sided), for FULL against each of six comparators, decided as an IUT |
| Statistic | θ̂ = mean over clusters; variance = block-sum over variance blocks (calendar blocks of each cluster's maturity, joined by the connected components of the final anchored dependency union, closed transitively), on G − 1 df |
| Decision | reject only if t > c* on the anchored blocks **and** on the blocks extended by each subset of the late links (at most 2^M_late partitions), each with its own G, G_min and c* |
| Error guarantee | size ≤ α − η_max (− γ_cal where simulated) over the committed enumerated set N_0 of a generator family N, per component; a calibration on that family, explicitly **not** a finite-sample validity property (A3) |
| Sequential | fixed horizon (one analysis date T_A, decision at T_D = T_A + D); the e-process monitors the sequential conditional null in record order and never confirms |
| Dependence | calendar blocks plus linked components. Cross-block dependence beyond the links, and persistence across blocks, are covered only as far as N reaches. |
| Completeness / selection | omissions against the reference universe are drawn and enter at the lower end of their box; supply exogeneity is a HYPOTHESIS screened on a burn-in; the universe holder's selection is a stated residual |
| Missingness | VOID cap; worst-case imputation bounds; breaches and defects by the box rule |

**Observable:** listings and their timestamps; forecasts and their receipt times; outcomes and adjudications;
the anchored ledger; base rates; forecast divergence |p_F − p_C|; FULL's mean lean E(p_F − p_C) per period.

**Unobservable from the data:**
- the universe holder's selection rule;
- whether a source's listing depends on relative skill (only screened);
- the serial dependence of period-level shocks beyond what G periods reveal;
- the dependence of clusters through links never archived;
- whether the null class N contains the true law;
- the increment standard deviation σ: it depends on the outcome law, and forecasts give only an upper bound (§3).

## 2. Identifiability and impossibility

**F1. Information is bounded by the number of periods.** Write the period mean of the increments as
M_b = θ + a_b + ē_b. Here a_b is a period-level component with variance τ², and ē_b is the average of n_b
cluster-level errors of variance σ². In general (R4, RC-301)
Var(M_b) = τ² + σ²/n + 2·Cov(a_b, ē_b) + σ²·(n − 1)·ρ_w/n,
where ρ_w is the mean pairwise correlation of the cluster errors within a period. The formulas below assume that both
covariance terms vanish: a_b uncorrelated with the errors, and the errors uncorrelated with each other. S15 shows the
difference at τ = 0.01, σ = 0.1 and n = 25. The formula τ² + σ²/n gives 0.00050. Errors that offset the period
component (Cov = −τ²) give 0.00040, and equicorrelated errors (ρ_w = 0.05) give 0.00098. Both agree with the
general expression (REPRODUCED). A positive ρ_w adds a part, σ²·ρ_w, that does not vanish as n grows. It is
period-level variance and belongs to τ². A negative covariance makes the formula conservative. Under those
assumptions, and for any test whose validity rests on independence across periods, the variance of θ̂ is
(τ² + σ²/n)/G. The minimum detectable effect of the one-sided level-α test at power
1 − β is therefore about (t_α,G−1 + t_β,G−1)·√((τ² + σ²/n)/G), which tends to (t_α + t_β)·τ/√G as n grows. More
events per period stop helping once σ²/n ≪ τ²; only more independent periods do. The simulation confirms the
formula: power 80.4 %, 80.3 % and 79.8 % at the predicted MDE in three cells, 20,000 replications each (S2,
REPRODUCED). This is the general form of what `17` already found case by case:
- "no supply detects δ < 0.065" under ± 0.3 period shocks;
- "120 clusters over 24 periods admit no valid test" under a persistent regime.

**F2. Where τ comes from.** Take one event with baseline forecast b, FULL forecast p and outcome probability q:
- the paired increment is X = (b − Y)² − (p − Y)², so E[X | q] = (b − p)(b + p − 2q);
- therefore ∂E[X | q]/∂q = 2(p − b);
- a period-level shift Δq = s·z of every outcome probability moves the period mean of X by 2·s·z·E(p − b), to first order;
- hence τ ≈ 2·s·|E(p − b)|.

Under the toy forecast law of S1 (base rate 0.3, 4,000 periods of 50 events):
- with no lean, outcome shocks of s = 0.03 and 0.06 produce τ ≤ 0.003;
- with a lean of 0.05 and 0.1, the simulated τ is 0.0037, 0.0068, 0.0064 and 0.0117, against first-order values of 0.003, 0.006, 0.006 and 0.012 (REPRODUCED).

Two consequences follow:
- **The outcome-rate channel of the period-level variance is governed by FULL's mean lean per period, which is observable before outcomes.** It is read at issuance. The outcome-rate shock s is estimated from the outcome history of the reference class, not from registered outcomes. At pre-registration, which precedes the forecasts, the bound must come from a blinded burn-in's forecasts or from a pre-registered cap on the mean lean. This covers the outcome-rate channel only. Other channels, such as skill that varies by period, need matured blinded outcomes or a pre-registered conservative bound.
- A system with no skill that only adds noise is worse than the baseline (δ = −noise², −0.0099 at noise 0.1, S1). The one-sided null θ ≤ 0 correctly includes it.

Whether the ± 0.3 increment shocks of `17` §6 are realistic under this channel is **EXPERIMENT_REQUIRED**. Settling
it needs the forecast lean and the reference-class outcome-rate variation, both measurable without outcomes of
registered events.

**F3. The joint law of the period means is an assumption, not a result.** If the period means may be arbitrarily persistent, no
finite G separates θ > 0 from a slowly drifting zero-mean shock. The distribution-free limit α(1 + δ)^G of `16`
Appendix H is one expression of this.

Under AR(1) period shocks (τ = 0.01, n = 25, σ = 0.1, G = 24, 20,000 replications), the block t rejects at
δ = 0 in:

| Shock law | Rejection | 99 % upper bound |
|---|---|---|
| independent | 4.86 % | 5.23 % |
| ρ = 0.5 | 7.59 % | 8.04 % |
| ρ = 0.9 | 18.68 % | 19.33 % |

The block sign-flip test fails the same way: 4.6 %, 7.58 % and 19.0 % (S3, REPRODUCED).

Under Gaussian AR(1) with ρ ≤ ρ_max, inflating the critical value by √((1 + ρ_max)/(1 − ρ_max)) restores size:
- 0.36–0.96 % at ρ_max = 0.5;
- 0–0.04 % at ρ_max = 0.9.

Power falls with it (S3c, REPRODUCED):
- at δ = 0.01, from 68 % to 25–28 % at ρ_max = 0.5;
- at δ = 0.02, to 1.9–10.7 % at ρ_max = 0.9.

**A scalar bound on serial correlation is not a validity condition.** It fixes neither the covariance at other
lags nor the marginal shape. The following laws satisfy a lag-one bound of 0.5, yet at period share 0.8 the
AR(1)-inflated cutoff rejects them at θ = 0 in (S6, REPRODUCED):
- equicorrelation 0.5: 24.1 %; the variance of the mean of the period component is inflated by 1 + 23·0.5 = 12.5, not 3;
- odd/even common shocks, with lag-one correlation 0 and two effective draws: 25.7 %.

**Independence alone is not one either.** A skewed law with a rare large negative period has nominal-cutoff size:
- 6.16 % in S3 (99 % upper bound 6.57 %);
- 20.8 % at period share 0.8 (S6).

**The defensible form is a pre-registered validity class 𝓛.** It is a finite set of complete joint laws of the
period means under θ = 0, each fixing:
- the marginal shape;
- the covariance across periods;
- the share of period-level variance.

**𝓛 holds centred shapes, and the null is composite** (R4, RC-297). H0 is θ ≤ 0, so a class fixed only at θ = 0 says
nothing about a law with θ < 0 of another shape. Codex's example shows this. With probability 0.1 every period sits
in a common positive regime (0.01 + 0.001·z), and otherwise at −0.1 + 0.02·z. Then θ = −0.089, yet the block t
rejects at the S9 cutoff in 10.0 % (99 % lower bound 9.87 %; S12, REPRODUCED). Each law of 𝓛 is therefore the law
of the centred period means U_b = M_b − θ. The null is the set of laws θ + U with θ ≤ 0 and the law of U in 𝓛.

The boundary θ = 0 is then least favourable, by a pointwise argument (derivation). Shifting every period mean by
θ shifts the block mean by θ and leaves the sample standard deviation unchanged. So t(θ + U) = t(U) + θ·√G/s(U) ≤
t(U) for θ ≤ 0, on every draw. The weighted statistic of F10 behaves the same way: its weights sum to one, and its
residuals do not depend on θ. S12 confirms this on every law of the example class. Shifts of 0.05 and 0.2
period-mean standard deviations below zero add no rejection on any of 50,000 draws per law, for either statistic.

Codex's law is not a counterexample to this rule. Its centred shape also rejects in 10.0 %, so it lies outside any
class whose certified cutoff is 3.357. The assumption is that the centred shape does not depend on θ. A null system
whose shape changes as θ falls is covered only if every centred shape it can take is in 𝓛. The noise-only system of
F2 is such a case: its shape changes with the noise. The assumption cannot be tested from G = 24 periods, as for 𝓛
itself.

**The critical value c_𝓛 is certified, not estimated** (R3, RC-292). For each law of 𝓛, draw n calibration values
of the block t under θ = 0 and take the smallest order statistic whose exceedance probability is at most α with
probability at least 1 − 0.01/K. For a continuous statistic the exceedance probability of the (j + 1)-th largest
draw is Beta(j + 1, n − j) whatever the law, so this needs no further assumption. c_𝓛 is the largest of these
cutoffs over 𝓛.

**K counts every law certified anywhere in the family** (R4, RC-298). K = Σ_j |𝓛_j| over all components of the
fixed sequence (F7), counting each law once more for each weighted variant (F10). The union bound then gives size at
most α, with probability at least 0.99 over the calibration draws, on every law of every class at once. Spending
0.01/|𝓛_j| inside each component gives each component 99 %, but the family only 1 − Σ 0.01 (97 % with three
components). S13 shows this with three components of the eight example laws:
- per component: an exact Beta failure bound of 0.00998 per component and 0.02995 for the family;
- across the union: 0.00987 for the family;
- the cutoff rises from 3.365 to 3.368, and power at δ = 0.01 falls from 15.37 % to 15.33 % (REPRODUCED).

For a fixed configuration of true and false nulls, only the first true null's cutoff matters. That configuration is
unknown, so the certificate must hold for all components together.

**A calibration that cannot certify is refused** (R4, RC-300). Even the sample maximum of n draws exceeds the α
quantile with probability (1 − α)^n. If (1 − α)^n > 0.01/K, no cutoff is certified. The calibration then needs
n ≥ ln(0.01/K)/ln(1 − α), which is 131 draws at K = 8 and 152 at K = 24. Codex's example of n = 100 and K = 8 fails
(0.95^100 = 0.0059 > 0.00125). R3's search returned the sample maximum anyway; the script now refuses (S14,
REPRODUCED).

With probability at least 0.99 over the calibration draws, the size is then at most α on every law of every 𝓛_j and
on every θ ≤ 0 shift of them. The empirical 0.95 quantile, which R2 used, has an exceedance probability above α
about half the time. The claim holds over 𝓛 only.

**The level is the unconditional size, not the certificate** (R5, RC-302). The 99 % statement is about the random
cutoff. On its own it bounds the probability that calibration and test together reject a true null only by
0.99·α + 0.01 = 0.0595, because on the 1 % failure event the cutoff's size can be anything. The procedure's
unconditional size is smaller than both (derivation). Let the true centred law be ℓ in 𝓛_j, with its own certified
cutoff c_ℓ, the (j + 1)-th largest of its n calibration draws. Then c_𝓛j ≥ c_ℓ, so a rejection at c_𝓛j is also a
rejection at c_ℓ. The fresh statistic and the n calibration draws are n + 1 exchangeable draws of a continuous
statistic, and j depends on n and the budget only, so P(T > c_ℓ) = (j + 1)/(n + 1) exactly, whatever ℓ is. The
procedure's size on ℓ, P(T > c_𝓛j), is therefore at most (j + 1)/(n + 1); with more than one law in 𝓛_j it is
generally smaller, because c_𝓛j is the largest of the law-wise cutoffs (R6, RC-306). A θ ≤ 0 shift only lowers T. The fixed sequence
rejects a true null only if its first true null rejects, so the familywise error is at most the same quantity. None
of this uses the union bound or the 0.01 budget.

**The calibration randomness is redrawn in every repetition** (R6, RC-304). "Unconditional" averages over the n
calibration draws. That average describes the procedure only if each repetition of the whole experiment draws them
afresh and independently of the forecasts and outcomes. With a fixed, pre-registered seed, as R5's M-1 had, every
repetition reuses one realised cutoff, and its size is that cutoff's conditional size. Only the 99 % certificate
covers that: on the 1 % event it can exceed α. R6 therefore draws the seed as `17` draws the seed of a simulated
family (RC-153, RC-182): s = SHA-256(the anchored calibration record ‖ v), v the verified output of a public
randomness beacon round named in the record and published after the record's external anchor. The calibration then
runs once on s, and its cutoff is the one the record designates. The record fixes the laws of every 𝓛_j, n, the
budget and the code. A repetition of the protocol anchors a new record and reads a new round, so the exchangeability
argument applies to it. Two assumptions remain, both stated rather than proved:
- the beacon output is unpredictable at the anchor and independent of the period means;
- the generator stream derived from s behaves as independent draws of each law.

A second calibration record for the same cohort would let the cutoff be picked among realised calibrations, and the
argument above does not cover that. Under the rule here it makes the claim non-confirmatory. Codex's other two
remedies were considered:
- a deterministic certificate of the realised cutoff would need the exceedance probability of every law of 𝓛 in
  closed form, which the example class does not have;
- keeping the 0.01 inside α would cost power that the drawn seed makes unnecessary.

**One record per claim, bound before any cutoff exists** (R7, RC-309). The argument covers the one record a test
uses, not a record chosen once its cutoff is known. Forbidding a second record for one cohort does not prevent that.
An operator can anchor m records under different cohort identifiers, read their beacon rounds and run only the
cohort with the smallest cutoff. That test uses the minimum of m exchangeable order statistics. For one law it
rejects with probability E[max of m draws of Beta(j + 1, n − j)], which exceeds (j + 1)/(n + 1) for every m ≥ 2
(S17, exact):
- at n = 1,000 with j = 31 (the three-law example), 3.197 % for one record, 3.509 % for two, 3.866 % for five and
  4.759 % for a hundred; end to end at m = 5 over 200,000 repetitions, 3.843 % (99 % interval 3.733–3.955 %);
- the certified index leaves a margin below α, so the level is exceeded only from m = 269 records at n = 1,000,
  468 at n = 131 and 479 at n = 200,000; the bound the argument states fails already at m = 2;
- an operator who runs m cohorts and reports whichever rejects does far worse, 1 − (1 − b)^m with b the bound:
  6.29 % at m = 2 and 14.99 % at m = 5 for b = 3.197 %.

R7 therefore binds each record to its claim before any output of the record exists:
- the claim's pre-registration (cohort, Q, statistic, fixed sequence) names exactly one calibration record, the
  record names the claim, and both are anchored before the record's beacon round is published;
- every anchored calibration record is in the append-only ledger, and every claim bound to one is tested and
  reported whatever its cutoff and result. A bound claim that is not tested counts as not rejected (`AGENTS.md` §8
  publishes negative results);
- a statement that draws on more than one bound claim, such as "one of the cohorts confirmed", is a multiplicity
  over them. The number of confirmatory claims is S_max. Since each claim has one record, that number plays the role
  of `17`'s OD4 field S_max, the most calibration records a family may have (1 if none is recorded), so S_max does
  not lapse under OD11 (b) (§9). With S_max = 1, Phase 1 has one confirmatory claim, and every other bound claim is
  exploratory.

**Which claims are confirmatory is fixed before any cutoff exists** (R8, RC-311). Fixing only the number leaves the
labels free. An operator who binds m claims and declares S_max = 1 can read all m cutoffs and then call the claim with
the smallest one confirmatory, reporting the rest as exploratory. That satisfies the reporting rule above, but the
confirmatory test is the minimum-of-m selection of S17, whose size exceeds (j + 1)/(n + 1) for every m ≥ 2 (3.509 %
at m = 2 against 3.197 %). A label chosen after outcomes is the report-any-of-m case, 6.29 % at m = 2. So the family's
pre-registration lists the confirmatory claims by identifier, at most S_max of them, and is anchored with S_max
before the beacon round of any calibration record bound to a claim of the family. Every other bound claim, including
one registered later, is exploratory, and no claim's status changes after that anchor.

**One confirmatory register for all of Phase 1** (R9, RC-315). Scoping that set to "the family" leaves the families
free. An operator can anchor two family pre-registrations, each naming one confirmatory claim with S_max = 1, before
both beacon rounds, and test and report both: each claim is then certified at α, and the chance that at least one
of two independent true nulls confirms is 1 − (1 − α)² = 9.75 % at exact size α, or 6.29 % at the bound
(j + 1)/(n + 1) = 3.197 % of n = 1,000 (S17's report-any-of-m rate at m = 2). Choosing afterwards which family to
cite is the same selection. So Phase 1 has exactly one confirmatory register: a single ledger record, anchored with
S_max before the beacon round of any calibration record bound to any Phase 1 claim, that lists every confirmatory
claim of Phase 1 by identifier, at most S_max in total, whatever family, cohort or pre-registration each belongs to.
A claim not listed there, in any family and including one registered later, is exploratory. A second register, or
an amendment of the first, confers no confirmatory status; only the first anchored register counts, and the
append-only ledger shows any other. S_max therefore counts confirmatory claims across Phase 1, not per family, and
the union bound below runs over every confirmatory claim of Phase 1.

**Each confirmatory claim is calibrated at α/S_max throughout** (R8, RC-312). R7 applied α/S_max only in the bound
check, so a calibration that followed the rest of the text at α either always failed that check or certified each
claim at α. With α_c = α/S_max, the index is the smallest order statistic whose exceedance probability is ≤ α_c with
probability ≥ 1 − 0.01/K; the refusal is (1 − α_c)^n > 0.01/K; the fresh-size check is against α_c; and the bound is
(j + 1)/(n + 1) ≤ α_c. S18 (REPRODUCED) shows why every step must change:
- at n = 1,000 (budget 0.01/3), the index chosen at α is j = 31 with bound 3.197 %. That fails the bound check for
  every S_max ≥ 2. At α/2 the index is j = 12, with bound 1.299 %; at α/5 it is j = 2, with bound 0.300 %;
- at n = 200,000 (K = 8), the index chosen at α (bound 4.853 %) also fails for every S_max ≥ 2. At α/2 the bound is
  2.395 %;
- at n = 131 (K = 8), the index chosen at α passes the bound check for S_max up to 5 (bound 0.758 %), but its
  certificate states only exceedance ≤ α. At α/2 the calibration is refused, because it needs n ≥ 265 (398 at S_max =
  3, 666 at S_max = 5);
- end to end, two true-null claims, each calibrated on its own 1,000 draws at α/2, reject at least once in 2.517 % of
  200,000 repetitions (99 % interval 2.428–2.609 %). The exact rate for independent claims is 2.581 %, below α. The
  union bound needs no independence.

`certified_cutoff`, `certified_index` and `minimum_calibration_size` take α_c as an argument. At S_max = 1 no cutoff,
power or table value changes.

Each bound claim then has unconditional size ≤ (j + 1)/(n + 1) whatever the other records show. For a confirmatory
claim that is ≤ α/S_max, so the union bound over the S_max confirmatory claims gives familywise error ≤ α. The
binding rests on the anchors and the ledger, not on a statistical assumption. The script cannot test it; M-1 (i)
checks it on the record.

(j + 1)/(n + 1) ≤ α is not proved in general for the certified index, so `certified_cutoff` checks it and refuses a
cutoff that fails. S16 (REPRODUCED) gives:
- bounds of 4.854 % for S9's certification (n = 200,000, K = 8), 4.838 % at K = 24 and 0.758 % at S14's minimum
  n = 131. These are bounds on the procedure, exact only for a class of one law (RC-306);
- a worst case of 4.949 % over 1,973 calibration sizes from 131 to 10⁶ and seven budgets, so the check never fires;
- for one law, end to end over 200,000 repetitions, 0.779 % against an exact 0.758 % at n = 131, and 3.528 % against
  3.497 % at n = 1,000 with a budget of 0.01, where the certificate failed in 0.94 % of calibrations;
- for a three-law class (normal, Student t with 3 df, and normal scaled by 0.7), each law calibrated on its own
  n = 1,000 draws at budget 0.01/3 and cut off at the maximum, over 200,000 repetitions against a bound of 3.197 %:
  - Student t: 3.195 %, because its cutoff is almost always the maximum;
  - normal: 0.250 %;
  - scaled normal: 0.005 %.

  Against each law's own cutoff, the rates are 3.195 %, 3.340 % and 3.170 %. The normal law's 3.340 % lies about
  3.6 standard errors above the exact 3.197 %. R6 read this as sampling variation from three further seeds it did
  not commit. S16 now commits that check (R7, RC-310):
  - seeds 60 to 62 give the normal law 3.236 %, 3.256 % and 3.208 %, the values R6 quoted. Pooled over the three,
    3.233 % (99 % interval 3.175–3.293 %); the exact 3.197 % lies inside;
  - pooled with seed 59, the normal law gives 3.260 % (3.209–3.311 %), which excludes it. That pool includes the
    seed chosen for re-examination because it was high, so it is not a test;
  - the normal law alone on seeds 100 to 103, which played no part in that choice, gives 3.180 % over 1,600,000
    repetitions (3.145–3.216 %), around the exact value.

  The committed seed is kept. The evidence for the sampling-variation reading is now the committed, unselected
  checks, not the R6 sentence.

Codex's first remedy, deducting the failure probability from α, is therefore not needed. The conditional
certificate keeps its 0.01 budget as a separate statement: with 99 % probability the calibration actually drawn has
size ≤ α on every law. Both statements need the fresh statistic to follow exactly a law of 𝓛 that was calibrated.

The example class (REPRODUCED) holds Gaussian AR(1) at ρ ∈ {0, 0.25, 0.5} and the skewed two-point law, each at
period shares 0.2 and 0.8. It is certified as one component alone, so K = 8. On it (S9, 200,000 calibration and
200,000 fresh draws per law):
- the empirical rule gives c = 3.335, and at the binding law, the skewed law at share 0.8, its fresh size is 5.06 %;
- the certified cutoff is c_𝓛 = 3.357, with fresh size 4.93 % at that law (99 % simultaneous bounds 4.78–5.07 %);
  the nominal value is 1.714;
- outside 𝓛 the test still fails: at R2's cutoff 21.5 % (equicorrelation) and 23.2 % (odd/even shocks) (S6);
- at the S3 point, power at c_𝓛 falls from 68.4 % to 15.2 % at δ = 0.01 and from 99.5 % to 82.7 % at δ = 0.02.

A fresh simulation cannot confirm a size of at most 0.05 at the binding law: its upper bound is 5.07 % for an
estimate of 4.93 %. The guarantee comes from the order-statistic argument; the fresh draws only detect a cutoff that
was computed wrongly (M-1).

The example is not a proposal. It shows that the class sets the power, and that one extreme law in it can set c_𝓛
alone.

𝓛 cannot be verified from 24 periods. A test of serial correlation on G = 24 period means has little power; that
power was **not simulated here**. 𝓛 is a design input justified from reference-class history, exactly like the
block length in `17`, and choosing it is part of OD11.

**F4. Outcome-independent inclusion is not identifiable from listing data.** Build two worlds with the same
listing metadata: a fixed count of 10 events per period out of 30, at the same times.
- In world A the 10 are chosen at random.
- In world B they are the 10 with the largest value of a signal correlated with the paired increment, under an exactly null universe.

The listing data are identical by construction, so any test that reads only listings has power equal to its
size. Yet the listed mean is 0.000 in world A and 0.059 in world B, and the block t on the listed events rejects
in 5.3 % against 100 % (S4, REPRODUCED). This is the general form of RC-241.

Outcome-independent inclusion can therefore come only from design:
- (a) a population fixed by a party without access to forecasts or outcomes, before the forecasts exist; or
- (b) randomisation with a seed nobody can choose.

`17` uses both: the reference universe and the beacon-seeded draw. The holder's own selection stays an unprovable
assumption under every design that uses a third-party population. `17` already states this residual.

**F5. Given a reference universe, the audit machinery adds no identification.** Suppose the eligible population
is defined as the predicate-matching events of a reference universe held by a party independent of the models
(`17` §3 item 2, RC-239 and RC-241). The source listing is then only a route by which events reach CPE. Change
the design so that CPE forecasts **every** universe event, or a beacon-seeded subsample of them, directly. An
event FULL does not forecast in time is an abstention scored at the baseline forecast; `17` already scores empty
non-baseline slots that way (RC-109).

Then:
- no omission exists to audit, draw or put in a box;
- the estimand is the mean improvement of CPE's **issued** forecasts, abstentions included, over the baseline on that population.

Strategic abstention cannot inflate it under the Brier score. Every forecast, abstention included, is fixed before
the outcome-knowable time t*_k, as `17` already requires. An abstention is then the forecast b, and replacing a
forecast by b when b is expected to score better is itself forecast skill under a proper score.

What remains is the holder's selection (F4) and the period dependence (F1–F3). Neither is touched by the audit,
the omission draw or the box rule. Those mechanisms protect against a source that drops events, a threat that an
exhaustive forecast of the universe removes by construction.

**F6. Omissions are tolerable only far below the effect.** Suppose a share m of the population is unobserved and
d bounds |p_F − p_C|. The paired increment (b − Y)² − (p − Y)² = (p − b)(p + b − 2Y) then lies in [−D, D] with
D = d(2 − d). This bound is sharp: it is attained at min(p, b) = 0 with Y = 1. On a 1001-point grid the supremum is
0.36, 0.75 and 1 at d = 0.2, 0.5 and 1 (S8, REPRODUCED). R1 used D = d, which is too narrow for every d < 1. For
example, b = 0.2, p = 0 and Y = 1 give an increment of −0.36 at d = 0.2 (RC-281).

The identified set of θ is (1 − m)·θ_obs + m·[−D, D]. The sign is identified only if m < θ/(θ + D) (S4, REPRODUCED):

| θ | d = 0.2 (D = 0.36) | d = 0.5 (D = 0.75) | d = 1.0 (D = 1) |
|---|---|---|---|
| 0.005 | 1.37 % | 0.66 % | 0.50 % |
| 0.010 | 2.70 % | 1.32 % | 0.99 % |
| 0.020 | 5.26 % | 2.60 % | 1.96 % |

This explains the power collapse that `17` reports at 1 % and 3 % omissions, and it holds for every estimator: it
is an identification limit, not a property of the box rule. A pre-registered divergence bound d widens the
tolerable share. That restricts what FULL may forecast, and it is an owner choice.

**F7. The conjunction is a different claim, and an expensive one.** An intersection-union test over J
comparators confirms only if every component rejects; its power is at most the smallest marginal, and the Fréchet
lower bound is max(0, Σ p_j − (J − 1)), as `17` already states. With equal marginals of 80 % (Gaussian test
statistics, 200,000 replications; S5, REPRODUCED):

| Correlation | J = 1 | J = 3 | J = 6 |
|---|---|---|---|
| 0.0 | 80.1 % | 51.1 % | 26.5 % |
| 0.5 | 80.0 % | 61.1 % | 47.6 % |
| 0.9 | 80.0 % | 72.2 % | 67.8 % |

A fixed-sequence (hierarchical) procedure tests H0(FULL vs Design C) at α and, only if it rejects, the next
hypothesis at α, and so on. It controls the familywise error at α and keeps 80 % power for the first claim; this is
a standard result of gatekeeping procedures (Maurer, Hothorn and Lehmacher, 1995; ESTABLISHED, not re-read). The
cost is substantive, not statistical: the fixed sequence confirms "FULL beats Design C" even when "FULL beats every
single provider" fails. `AGENTS.md` §2 item 1 requires the three models plus Jev as components; it does not
require the confirmatory claim to be the conjunction. H1 of `02` is a hypothesis, not a requirement.

**The guarantee needs every component to be a level-α test of its own null** (R3, RC-295). An error requires the
first true null in the order to be rejected, and that happens with probability at most α if its own test is
level α. Nothing about the dependence between components is needed. A cutoff calibrated for the first component
does not make a later one valid: provider and committee increments can have another shape and serial dependence.
In S10 the first component is false and always rejects. The second is a true null with equicorrelated period means
(0.5, share 0.8). At the first component's certified cutoff, 1.734, the familywise error is 33.9 %. At a cutoff
certified for the second component's own law, 7.118, it is 4.91 % (99 % upper bound 5.07 %). Each component j
therefore has its own pre-registered validity class 𝓛_j of the centred joint laws of its own period means, and its
own certified cutoff c_𝓛j. All the cutoffs share the family's budget 0.01/K (F3, RC-298). S10 has two laws, so each
uses 0.005; R3 used 0.01 for each, which gave 1.733 and 7.113.

**F8. Anytime validity does not buy information.** Ville's inequality makes a betting e-process valid at every
stopping time under the record-order conditional null. Its power over G independent periods is still limited by G.
Setup (S3b, 20,000 replications):
- period-mean standard deviation 0.0224 (τ = 0.01, σ = 0.1, n = 25);
- predictable plug-in bets, capped at λ = 0.5 or at λ = 2.5;
- λ = 0.5 is valid for every increment in [−1, 1];
- λ = 2.5 needs every increment to exceed −0.4. A design bound |p_F − p_C| ≤ 0.2 ensures that, because it bounds the increment by d(2 − d) = 0.36 (F6).

| Periods G | δ = 0.01, λ ≤ 0.5 | δ = 0.01, λ ≤ 2.5 | δ = 0.02, λ ≤ 2.5 |
|---|---|---|---|
| 24 | 0 of 20,000 | 0 of 20,000 | 0 of 20,000 |
| 104 | 0 of 20,000 | 13.1 % | 99.98 % |
| 260 | 0 of 20,000 | 99.96 % | 100 % |
| 520 | 4.0 % | 100 % | 100 % |

A cell with no crossing in 20,000 replications is not zero power. Its one-sided 99 % Clopper–Pearson upper bound
is 0.023 % (S3b, RC-285).

The fixed-horizon block t on the same means detects δ = 0.01 at G = 24 in 68.7 %. An anytime-valid primary is
feasible only with:
- about 100–260 independent periods, for example weekly periods over two to five years, if weekly shocks are independent (itself an F3 assumption); and
- a pre-registered divergence bound.

The confidence-sequence literature makes the same point: betting confidence sequences (Waudby-Smith and Ramdas)
and e-values for comparing forecasters (Henzi and Ziegel; Choe and Ramdas) are valid under weak assumptions and
pay for it in sample size. These are UNVERIFIED citations, not re-read here.

**F10. A period-level test fixes the weighting of its estimand.** Write n_b for the number of events of Q in
period b and θ_b for their mean improvement. The unweighted block t estimates the period-balanced mean
θ_P = (1/G)·Σ_b θ_b. That is not the event-level mean over Q, θ_E = Σ_b n_b·θ_b / Σ_b n_b. The two differ whenever
period means vary with period counts, and they can differ in sign. A period of 100 events at −0.01 and one of a
single event at +0.10 give θ_E = −0.0089 and θ_P = +0.045 (S8, REPRODUCED; RC-284).

Each estimand has its consistent test:
- θ_P with the unweighted block t;
- θ_E with the weighted mean θ̂_E = Σ_b w_b·M_b, w_b = n_b / Σ n, Studentized by the leverage-corrected estimate
  V̂ = Σ_b w_b²·(M_b − θ̂_E)² / (1 − 2w_b + Σ_j w_j²), with a cutoff certified over 𝓛 for its weight vector. Its laws
  count in the family's K (F3).

**The weighted statistic has no nominal cutoff** (R3, RC-294). R2 wrote V̂ = Σ_b w_b²·(M_b − θ̂_E)²·G/(G − 1) on
G − 1 df. That estimate collapses when one weight dominates. For two independent period means of variance σ² with
weights 100/101 and 1/101, the true variance is 0.980·σ² and the expectation of R2's estimate is 0.00077·σ². With a
dominant period at G = 24, the size at the nominal t cutoff is 44.9 % (S11).

The leverage-corrected V̂ is unbiased when the period means are independent with a common variance, because
Var(M_b − θ̂_E) is then σ²·(1 − 2w_b + Σ w²). It is not unbiased otherwise: with variances proportional to 1/n_b and
one dominant period, its mean is 4.25 times the truth. Even when it is unbiased, the Studentized ratio is not t on
G − 1 df: S11 gives 5.5–6.9 % at the nominal cutoff over three weight vectors and two laws. The cutoff of the
weighted statistic is therefore certified like c_𝓛, over the laws of 𝓛 with the fixed weight vector.

Q is fixed before forecasting, so the weights are known constants. 𝓛 must then include the weight vector, because
c_𝓛 depends on it. Which estimand is confirmatory is the open OD4 field of RC-69 (per cluster or period-balanced).
This document does not choose; the claim must name the one tested.

## 3. Feasibility

**Minimum detectable effect at 80 % power, one-sided α = 0.05** (block t on G independent normal period means,
σ = 0.1 per cluster, n clusters per period). Power is the exact noncentral-t power. R1 summed two central t
quantiles, which overstates the MDE by up to 1 % at G = 4 (RC-287). S2, REPRODUCED:

| τ | G | n = 25 | n = 100 | n → ∞ |
|---|---|---|---|---|
| 0 | 24 | 0.0105 | 0.0052 | 0 |
| 0.005 | 24 | 0.0108 | 0.0058 | 0.0026 |
| 0.01 | 24 | 0.0117 | 0.0074 | 0.0052 |
| 0.02 | 24 | 0.0148 | 0.0117 | 0.0105 |
| 0.01 | 48 | 0.0081 | 0.0052 | 0.0036 |
| 0.01 | 104 | 0.0055 | 0.0035 | 0.0025 |
| 0.02 | 104 | 0.0069 | 0.0055 | 0.0049 |

**Independent periods needed for 80 % power at n = 100** (unchanged under the exact power):

| Target δ | τ = 0.005 | τ = 0.01 | τ = 0.02 |
|---|---|---|---|
| 0.005 | 33 | 51 | 126 |
| 0.010 | 10 | 14 | 33 |
| 0.020 | 4 | 5 | 10 |

**Reading:**
- With monthly periods, a 24-month horizon and 100 resolvable clusters per month (2,400 clusters), δ = 0.01 is detectable if τ ≤ 0.01. δ = 0.005 needs more than four years of monthly periods at τ = 0.01.
- Supply of 25 clusters per month (600 clusters) moves the δ = 0.01 boundary to about τ = 0.005.
- Supply, σ, τ and the effect size are all unknown before Phase 2 (RC-289):
  - supply needs no outcome;
  - σ is the increment's standard deviation, so it depends on the outcome law. Forecasts give only an upper bound: |X| ≤ |p − b|·max(p + b, 2 − p − b). The same forecasts p = 0.4 and b = 0.3 give σ = 0.092 at outcome probability 0.3 and 0.100 at 0.5, under the forecast-only bound 0.13 (S8);
  - τ's outcome-rate channel needs the lean (forecasts) and s (outcome history of the reference class). Every other channel needs matured blinded outcomes or a pre-registered conservative bound.

  **EXPERIMENT_REQUIRED**: the Phase 2 supply measurement of `17` §6, extended to the lean, the divergence and the σ bound, plus a reference-class history of outcome rates and their dependence. These are the entries of `16` §7 `experiments_required` (RC-291).

**What these numbers do not cover:**
- the IUT, which divides the power as in F7;
- dependence or shape beyond independent normal means, which raises the critical value to c_𝓛 (F3: 15.2 % power at δ = 0.01 at the certified c_𝓛 of the example class, S9);
- omissions, which must stay below F6's limit;
- the calibrated c* of `17`, which is larger than t_α and lowers power further (`17` §6 reports 28–60 % at δ = 0.01 and 600 clusters where the nominal value gives 78 %).

These bounds are optimistic for the current method and roughly attainable for the simplified one.

**Late evidence and correlated forecasts.**
- In the current method, late links change the variance blocks after the outcomes. That is the source of rounds 43–52 (RC-250 to RC-274).
- If the period is the unit of inference, cross-cluster links within a period need no rule at all, because the block sum already absorbs any within-period dependence. Links that cross periods are serial dependence and fall under the validity class 𝓛 of F3, with a pre-registered sensitivity analysis that merges adjacent periods (G/2 blocks of two months).
- Correlated comparator forecasts matter only to the conjunction (F7); the first claim of a fixed sequence does not depend on them.

## 4. Alternatives compared

| | A. Current (`17` v49) | B. Externally fixed question set, period-level fixed-horizon test | C. Anytime-valid e-process / confidence sequence on period means | D. External benchmark or randomised question sampling | E. Partial-identification report |
|---|---|---|---|---|---|
| Population | source listings audited against a reference universe; omissions drawn and boxed | every question of a set fixed by an independent party before forecasting (or a beacon-seeded subsample) | as B | questions supplied by a third-party benchmark or tournament stream, or sampled at random from a large external pool | any of the above |
| Selection assumption | universe holder independent of relative skill (unprovable), plus supply exogeneity screened on a burn-in | universe holder independent of relative skill (unprovable; same residual as A) | as B | the benchmark's question writer independent of the arms (unprovable) | none for the bound itself; the width carries it |
| Dependence assumption | the true law lies in the enumerated null class N; links archived by T_D | the joint law of the centred period means M_b − θ (shape and covariance) lies in a pre-registered validity class 𝓛, whatever θ (F3) | the record-order conditional null (stronger than the average null, `17` §3 item 3) | as B | stated per bound |
| Finite-sample guarantee | calibration on N_0 only (A3 says so) | size ≤ α on every θ ≤ 0 shift of every law of 𝓛 with probability ≥ 0.99 over the calibration draws (certified c_𝓛, S9, S12, S13); nothing outside 𝓛 (S6) | exact (Ville) under its null, for bounded increments | as B | the identified set is exact under the stated bounds |
| Power at G = 24, δ = 0.01, τ = 0.01, n = 25 | below B's (calibrated c* and the IUT) | 68.7 % at the nominal cutoff (𝓛 = independent normal means); 15.2 % at the certified c_𝓛 of the example class (S9) | no crossing in 20,000 (≤ 0.023 %) | as B | the sign is decided only if m < θ/(θ + d(2 − d)) |
| Complexity | 405 KB specification, 280 RC items, every-subset partitions, K_max budget | one test, one assumption (𝓛), one sensitivity analysis | small kernel; already archived (GRAPA) | depends on the external provider; little CPE machinery | arithmetic |
| What it cannot do | confirm under persistence or selection outside N | confirm under a law outside 𝓛; say anything about questions outside the set | detect useful effects within two years | guarantee that the questions match CPE's target domain | turn a bound into a point estimate |

**Approach A.** Valid as a calibration on its families, but its validity grows with each rule, and its residual
assumptions are the same as B's: the holder's selection and persistence.

**Approach B.** Removes by design what A removes by audit. Its one statistical assumption is visible and
pre-registered.

**Approach C.** Remains the right monitor. It cannot be the primary at the supply and horizon now planned.

**Approach D.**
- It is the cheapest route to a falsifiable claim of forecast skill, and the closest to established practice in LLM forecasting evaluation.
- It answers a different question: skill on the benchmark's questions, not on CPE's economic-inflection domain.
- It also raises a provider-terms question for OD8.

**Approach E.** Is not an alternative to a test but the honest way to report any of them when omissions or VOIDs
exist. It should accompany every primary.

**Approach outside Phase 1.** Randomised control in the investment sense (random-control shadow books, `AGENTS.md`
§2 item 6) answers the separate economic-value question. No design above says anything about investment returns.

## 5. Has the method overfit to its reviews?

**Measured on the repository at `a22f9df`:**
- `16` names 280 distinct RC items over 52 rounds, between 2026-10-16 and 2026-10-19.
- `17` grew from 16,727 bytes at its first commit (`10d1581`) to 405,507 bytes, over 50 commits.
- The phrase "gap of my" (an earlier remedy) occurs 25 times in the matrix, and "propagation gap" 35 times.
- Rounds 43–52 applied RC-250 to RC-280. Almost all of them repair consequences of RC-250, the late-link variance blocks, or process metadata: the T-09 merge message, OD10 record keeping.
- The P1 identity finding returned each round (29 non-reproducing SHAs) is review-environment noise, not science.

**Interpretation (HYPOTHESIS).** The core assumptions are the inclusion mechanism and the period dependence, and
F4 and F3 show that neither is identifiable from the data. Each round therefore adds a rule that closes one
exhibited path while leaving the unidentifiable core in place, and the new rule creates the next edge case. Many
individual remedies were genuine: they fixed real anti-conservative paths. The claim here is about the trajectory,
not about any single fix.

**Discriminator.** Submit the simplified design B, written to the same standard, to the same reviewer. If the
hypothesis is right, B's core (population, statistic, assumption) draws markedly fewer genuine findings per round
than A's late-link and audit sections did in rounds 43–52. If B draws findings at A's rate, the hypothesis is
falsified, and the difficulty lies in the problem, not in the method.

## 6. Recommendation: narrow and simplify

**Retain** (they are what makes any claim auditable, and none is implicated in F1–F8):
- point-in-time ledger with anchoring and replay;
- four timestamps and the resolution rules;
- pre-registration before unblinding;
- beacon-seeded sampling where a subsample is needed;
- paired Brier increments per outcome cluster;
- abstention scored at baseline;
- worst-case VOID bounds;
- fixed-horizon primary;
- the e-process as a monitor that never confirms;
- the capability, CI and fixture work of `17` §3 items 1, 2 and 4–8.

**Replace:**
1. *Population.* An externally fixed question set (the reference universe itself), forecast exhaustively by every arm, replaces source listings audited against that universe. This retires, for any source whose universe is the population, the omission audit and draw, the box rule for omissions, the supply-exogeneity screen and the fixed-count analysis (F5). A source family without such a universe is not confirmatory; `17` already says this.
2. *Statistic and validity.* The block t on the G period means replaces the calibrated c* over an enumerated null class, with variance blocks joined by linked components, late partitions, every-subset decisions, M_late and K_max:
   - one pre-registered period length;
   - one pre-registered validity class 𝓛 with its certified critical value c_𝓛 (F3);
   - the estimand weighting, period-balanced or event-weighted, with its matching statistic and, for the weighted one, its own certified cutoff (F10);
   - G_min;
   - a merge-adjacent-periods sensitivity analysis;
   - E's identified set reported beside the primary.

   The calibration of A3 becomes the calibration of this one test over the laws of 𝓛, with size and power fixtures (F1–F3). It is no longer a certification over a generator family of the whole pipeline.
3. *Multiplicity.* A fixed-sequence family replaces the six-comparator IUT. Its first hypothesis is H0: θ(FULL − Design C) ≤ 0; the next is FULL against the best pre-registered single provider, then FULL against the equal-weight committee, each at α only after its predecessor rejects (F7). Each component j has its own validity class 𝓛_j and certified cutoff c_𝓛j (F7, RC-295). The order is an owner decision.

**Narrow the claim.** Proposed wording: "On the pre-registered question set Q, fixed by [holder] before forecasting, over periods [T_0, T_A), the [period-balanced | event-weighted] mean improvement in Brier score of CPE's issued forecasts over the Design C base rate is positive (one-sided, unconditional size ≤ 0.05/S_max over calibration and test together, S_max the number of confirmatory claims of Phase 1, listed by identifier with this one in its one confirmatory register, anchored before the beacon round of any calibration record bound to a Phase 1 claim; the calibration seed drawn from a public beacon round published after the calibration record, bound to this claim alone, is anchored; the cutoff also certified at size ≤ 0.05/S_max with 99 % confidence over the calibration). This holds under two stated assumptions: the joint law of the centred period means lies in the pre-registered class 𝓛 whatever the mean, and Q's composition is independent of the arms' relative skill." The bracket is the OD4 weighting (F10). The claim makes no claim outside Q or 𝓛, none about investment value, and none from the monitor.

**Decision matrix** (++ strong, + adequate, − weak, −− fails; evidence in §2–§4):

| Criterion | Retain A | Simplify to B | Replace by C as primary | Narrow to D | E alone |
|---|---|---|---|---|---|
| Validity rests on stated, inspectable assumptions | − (N and the links) | ++ | ++ | + | ++ |
| Power at 24 months, δ = 0.01 | − | + if τ ≤ 0.01 and n ≥ 25 | −− | + | n/a |
| Selection risk | + (audited; holder residual) | + (by design; same residual) | + | + (benchmark residual) | n/a |
| Complexity and review cost | −− | ++ | ++ | ++ | ++ |
| Relevance to CPE's domain | ++ | ++ if Q is in the domain | ++ | − | as base |
| Falsifiable acceptance tests | + (many) | ++ (§7) | ++ | + | + |

## 7. Falsifiable acceptance tests for the recommended method

Each test is phrased so that a wrong implementation fails it. Thresholds follow A3's Clopper–Pearson form.

| ID | Test | Pass condition |
|---|---|---|
| M-1 | Certified cutoff and fresh size of the block t on every law of 𝓛, for each component j of the fixed sequence with its own 𝓛_j, and for the weighted statistic with its weight vector (RC-292, RC-294, RC-295, RC-297, RC-298, RC-300, RC-302, RC-304, RC-306, RC-309, RC-311, RC-312, RC-315) | With α_c = 0.05/S_max (RC-312): (i) c_𝓛 recomputed from the seed s = SHA-256(anchored calibration record ‖ v) and the recorded calibration size equals the registered value. v must be the verified output of the beacon round named in the record, published after the record's anchor; a record whose seed was chosen, whose round precedes its anchor, or which is the cohort's second calibration record fails (RC-304); the record names exactly one claim, that claim's anchored pre-registration names the record, and both anchors precede the round; a record bound to no claim or to a claim registered after its round, a bound claim missing from the report, or a confirmatory statement over more claims than S_max fails (RC-309); a claim that is not listed by identifier in Phase 1's one confirmatory register, anchored with S_max before the beacon round of every calibration record bound to any Phase 1 claim, is exploratory, and a report that calls it confirmatory, changes any claim's status after that anchor, lists more than S_max confirmatory claims across all families, or cites a second register or an amended one, fails (RC-311, RC-315); it is the largest over 𝓛 of the smallest calibration order statistic whose exceedance probability is ≤ α_c with probability ≥ 1 − 0.01/K, K the number of laws certified across all components and statistics (F3). (ii) On 200,000 fresh draws per law, no one-sided lower Clopper–Pearson bound, simultaneous at 99 % over all K laws, exceeds α_c. S9 (S_max = 1): c_𝓛 = 3.357, binding law 4.93 % (bounds 4.78–5.07 %). The empirical-quantile cutoff 3.335 passes (ii) but fails (i); the nominal cutoff fails (ii). (iii) A calibration with (1 − α_c)^n > 0.01/K is refused, not certified: S14 refuses n = 100 at K = 8; S18 refuses n = 131 at K = 8 and S_max = 2. (iv) On the same draws shifted below θ = 0, no draw rejects that did not reject at θ = 0 (S12). (v) Each certified index j satisfies (j + 1)/(n + 1) ≤ α_c, the bound on the unconditional size of calibration and test together; an index that fails is refused (RC-302, RC-306, RC-309; S16: a bound of 4.854 % for S9's certification at S_max = 1). An implementation that selects the index at 0.05 and checks only (v) at α_c fails: S18 shows that the index chosen at 0.05 fails (v) for every S_max ≥ 2 at n = 1,000 and n = 200,000 (RC-312) |
| M-2 | Invalid control: the cluster-iid t on the same data | its one-sided 99 % lower Clopper–Pearson bound must exceed 0.05 at τ > 0; S3 gives 6.85 % (99 % upper bound 7.28 %), so the control needs τ large enough to separate (OD4 sets the family) |
| M-3 | Out-of-class control: a law outside 𝓛 that satisfies the same scalar persistence bound | its one-sided 99 % lower Clopper–Pearson bound at c_𝓛 must exceed 0.05, so that the report cannot extend the claim beyond 𝓛. S6 gives 21.5 % (equicorrelation 0.5) and 23.2 % (odd/even shocks) |
| M-4 | Power at the pre-registered δ, τ, n and G on independent normal means, at the cutoff actually used (RC-296) | simulated power within ± 0.02 of the noncentral-t power at that cutoff, P(T > c) with T noncentral t on G − 1 df and noncentrality δ/se. At the nominal cutoff S2 gives 0.802, 0.803, 0.795 at 0.8; at c_𝓛 = 3.357, S9 gives 0.152 against 0.155 (δ = 0.01) and 0.827 against 0.829 (δ = 0.02). Power at c_𝓛 under a law of 𝓛 other than independent normal means has no closed form and is reported, not tested |
| M-5 | Exhaustive coverage: an event of Q with no FULL forecast by its issuance close | scored at the baseline forecast; an implementation that drops it fails |
| M-6 | Fixed-sequence familywise error under the joint generator of S7. J = 3 hypotheses in the fixed order. Statistics are jointly normal with unit variances and equal pairwise correlation r ∈ {−0.4, 0, 0.5, 0.9}. A true null has mean 0, the boundary of H0. A false null has mean z_(1−α) + z_π, with π ∈ {0.5, 0.8, 0.99} shared by the false nulls of a configuration. Every pattern with at least one true null is run: 76 configurations, 100,000 replications each (RC-290) | every one-sided Clopper–Pearson upper bound at confidence 1 − 0.01/76 ≤ 0.06; S7 gives at most 5.39 %. A later hypothesis is never tested after an earlier non-rejection |
| M-7 | Identified set: inject omitted share m with adversarial increments ±d(2 − d) | the reported interval contains the true θ in every replication; the sign is declared only when m < θ_obs/(θ_obs + d(2 − d)) |
| M-8 | Selection fixture of F4 (world B) presented as a source-listed population | refused as non-confirmatory, because the population is not Q; an implementation that accepts it fails |
| M-9 | Monitor never confirms | a crossing of the e-process produces no confirmatory record (the anytime-valid monitor row of `17` §6) |

M-1 to M-4 and M-6 are backed by S2, S3, S6, S7 and S9 to S14. M-6 keeps its 0.06 threshold because its
cutoffs are exact normal quantiles: there the threshold is a Monte Carlo tolerance for checking the gating, not a
size claim. M-5 and M-7 to M-9 are specifications here, not yet code.

## 8. Proof and assumption boundary

| Claim | Status |
|---|---|
| F1 information bound, F6 identified set with the sharp increment bound d(2 − d), F7 IUT ≤ min marginal and fixed-sequence FWER | derivation (paper); the bound is checked on a grid (S8); the F7 FWER part is a textbook result, ESTABLISHED, and checked on the M-6 generator (S7) |
| F2 τ ≈ 2·s·\|E(p − b)\| | first-order derivation; REPRODUCED on one toy law only; other channels of period dependence not covered |
| F3 no uniform test under an unrestricted joint law; neither a scalar persistence bound nor independence is a validity class | ESTABLISHED in kind (`16` Appendix H); REPRODUCED for AR(1), equicorrelation, odd/even shocks and a skewed law (S3, S3c, S6); 𝓛 itself is UNPROVED and must be assumed |
| F4 non-identifiability of selection from listings | constructive counterexample, REPRODUCED; general for any test that reads listings only |
| F5 audit adds no identification once Q is the universe | derivation; relies on abstention = forecast b under a proper score |
| F8 betting power vs G | REPRODUCED for the plug-in rule; a zero count is reported with its upper bound; another betting rule could do somewhat better, but not escape the G bound of F1 |
| F10 period-balanced and event-weighted estimands differ, in sign too | exact example (S8); the choice is the OD4 field of RC-69 |
| Certified cutoff: size ≤ α (α/S_max for each confirmatory claim, RC-312) on every law of 𝓛 with probability ≥ 0.99 over the calibration | derivation (order statistics of a continuous statistic; paper); checked on the example class (S9); says nothing outside 𝓛 |
| Unconditional size of calibration and test together ≤ (j + 1)/(n + 1) ≤ α on every law of 𝓛, every θ ≤ 0 shift and the fixed-sequence family | derivation (exchangeability; paper); an upper bound, exact for a class of one law (RC-306); (j + 1)/(n + 1) ≤ α checked by the script on every certification, not proved in general; end-to-end simulations for one law and for a three-law class in S16; holds only if the calibration seed is drawn from a beacon round after the record's anchor and the calibration runs once (RC-304), and only if the record is bound to one claim before its round and every bound claim is reported, with the S_max confirmatory claims named by identifier before any of their rounds (RC-311) and each calibrated at α/S_max in index, certificate, refusal and checks (RC-309, RC-312; S18; selection among unbound records exceeds the bound for every m ≥ 2, exactly and end to end in S17); assumes the beacon output independent of the period means; says nothing outside 𝓛 |
| Fixed sequence: marginal level α of each component suffices for familywise α | derivation (paper); the failure with a shared cutoff and the repair are REPRODUCED (S10) |
| Boundary θ = 0 least favourable for both statistics when 𝓛 holds centred shapes that do not depend on θ | derivation (translation equivariance; paper); checked draw by draw on the example class (S12); the shape assumption is UNPROVED and untestable from G = 24 |
| Family certificate at 99 % with the budget 0.01/K over all laws of all components | union bound (paper); exact Beta failure bounds in S13 |
| F1 variance (τ² + σ²/n)/G | holds when the period component and the cluster errors are mutually uncorrelated; general expression checked in S15 |
| Leverage-corrected variance of θ̂_E unbiased under independent period means of common variance | derivation (paper); checked by simulation (S11); not unbiased under unequal variances, and the ratio is not t-distributed |
| Holder's selection independent of relative skill | UNPROVED; untestable from the data under any design here |
| Realistic δ, τ, σ, supply | EXPERIMENT_REQUIRED (Phase 2 measurement): supply and lean need no outcomes; σ has only a forecast-only upper bound; τ beyond the outcome-rate channel needs matured blinded outcomes |
| F9 overfitting | HYPOTHESIS with the discriminator of §5 |

## 9. Owner decision OD11 (new; options and consequences, not chosen)

| Option | Consequence |
|---|---|
| (a) Retain `17` v49 as the confirmatory method and continue rounds | keeps the audited-source design and the calibration on N; review cost per round stays as in rounds 43–52; power below B's |
| (b) Simplify to B as in §6, keeping `17`'s infrastructure | needs a dated amendment of `17` replacing the §3 item 3 primary and the §6 rows named in §6 above; the retired machinery stays in the record; Codex reviews the amendment at its exact SHA |
| (c) Narrow to D first (external benchmark) and run B later in the CPE domain | earliest falsifiable skill evidence; answers a different question; benchmark terms belong with OD8 |
| (d) Pause confirmatory design until the Phase 2 measurements (supply, lean, the σ bound, reference-class outcome rates and their dependence) exist | no rounds wasted on parameters that are unknown; calendar cost only |

Options (b) to (d) leave OD1–OD10 in place. Under (b), several OD4 fields lapse with the machinery they parametrise: M_late, K_max, the null-class box and γ_cal. S_max does not lapse: under (b) it is the number of confirmatory claims of Phase 1, named by identifier in its one confirmatory register before the beacon round of any Phase 1 calibration record, across all families, each bound to one calibration record before its beacon round and calibrated at α/S_max throughout (RC-309, RC-311, RC-312, RC-315, §2). The validity class 𝓛 of each fixed-sequence component (𝓛_j, RC-295), a class of centred shapes assumed not to depend on θ (RC-297), and the period length replace them, and the weighting stays the OD4 field of RC-69. That change is itself part of the decision. 𝓛 sets the power (F3), so choosing it is a trade between validity and power that the owner makes, not this document.

## 10. What was run and what was not

**Run (R9):**
- `python -I research/reproduction/check_appendix_scripts.py --reference-code <scratch copy of source_v0_2>` on the R9 tree, under Python 3.11.17 in a venv built with `pip install --require-hashes --no-deps -r research/reproduction/requirements.txt` (numpy 2.4.6, scipy 1.17.1). It runs `reassessment_sims.py` among the 48 scripts and compares each output byte for byte with its committed appendix block, which R9 does not change; the result is reported in the commit and the handoff. `reassessment_sims.py` is unchanged in R9, so it is not rerun separately. A run on R8's tree `62d4c2a`, started in parallel, was stopped by the session's time limit before it reported and is not counted.
- The OD10-record check of `check_appendix_scripts.py` on the committed matrix, and on copies with "; version 50 …", "; version 49 …", "; version 22 …" or " (Version  50 …)" appended to the §6 OD10 row: R8's checker returns no failure on any of them; R9's returns none on the committed matrix and one on each copy, and, as before, one on ", version 50 …" (RC-314) and on a second " and version 49 …" entry (RC-280) (RC-317).
- RC-315 is arithmetic on committed numbers: 1 − 0.95² = 9.75 %, and 1 − (1 − 0.03197)² = 6.29 %, S17's report-any-of-m rate at m = 2.

**Not run:**
- a power simulation of the serial-correlation test at G = 24;
- M-5 and M-7 to M-9;
- B's power at c_𝓛 for any class other than the example, among them the example without its binding skewed law;
- the certified cutoff of the event-weighted statistic over any class (S11 measures only the nominal cutoff);
- validity classes 𝓛_j for the provider and committee components;
- a beacon-seeded calibration on a real anchored record, and the claim binding of RC-309 and the confirmatory register of RC-315 on a real ledger;
- any real data, provider or network.

**Next responsible agent.** Codex: an independent adversarial review of this document and Appendix AW at the exact
commit that carries them. The checks to make:
- reproduce S1–S18;
- check the exchangeability argument of the unconditional size, the drawn calibration seed, the claim binding and the one Phase 1 confirmatory register it now relies on, and whether a law inside 𝓛, a protocol repetition or a selection path among bound records, claim labels, families or registers breaks it;
- check that α/S_max now reaches every step of the calibration of a confirmatory claim (RC-312);
- check the order-statistic argument of the certified cutoff, and look for a law inside a declared 𝓛 that it misses;
- check the location-shift argument of F3 and the family budget 0.01/K;
- check whether the leverage-corrected weighted statistic needs more than a certified cutoff over 𝓛 to be valid;
- look for a counterexample to F5 (a selection path that survives an exhaustive forecast of Q);
- look for a counterexample to F2's use as a pre-registration bound;
- check whether the fixed-sequence order loses a claim the owner needs.

The owner: OD11. No agreement is claimed until Codex has reviewed that commit.
