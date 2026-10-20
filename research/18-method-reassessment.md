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

**Evidence.** Every number below marked `REPRODUCED` comes from `research/reproduction/reassessment_sims.py`.
Its output is committed in `16` Appendix AW and checked by `check_appendix_scripts.py`. Derivations are paper
arguments, not Lean proofs. External literature is cited for orientation only: it was not re-read in this
execution and is `UNVERIFIED` as to exact statements.

## 0. Summary

| # | Finding | Label |
|---|---|---|
| F1 | Once a period-level component exists, the information in the primary is set by the number G of independent calendar periods, not by the number of events. As n → ∞ the minimum detectable effect tends to (t_α + t_β)·τ/√G. | derivation; REPRODUCED |
| F2 | An outcome-rate shock reaches the paired Brier difference only through FULL's mean lean away from the baseline: τ ≈ 2·s·\|E(p − b)\|. That quantity is observable before any outcome. | derivation; REPRODUCED on a toy law |
| F3 | No test of the average null over a finite G is valid under unrestricted serial dependence of the period means. Validity needs a pre-registered bound ρ_max that 24 periods cannot verify. | ESTABLISHED in kind; REPRODUCED for AR(1) |
| F4 | Outcome-independent inclusion is not identifiable from listing data. It can be established only by design, and the reference-universe holder's own selection is unprovable from the data. | constructive counterexample; REPRODUCED |
| F5 | If the population is the reference universe itself and every one of its events is forecast, abstentions scored at baseline, the omission audit, draw and box rule add no identifying power. The universe already carries the whole selection assumption. | derivation |
| F6 | With omitted share m and divergence bound d, the sign of θ is identified only if m < θ/(θ + d). At θ = 0.01 and d = 0.5 that means m < 1.96 %. | derivation; REPRODUCED |
| F7 | The six-comparator intersection-union conjunction loses power steeply. With 80 % marginals it rejects in 26 % (uncorrelated) to 68 % (r = 0.9). A fixed-sequence order keeps 80 % for the first claim at the same familywise α. | ESTABLISHED; REPRODUCED |
| F8 | The anytime-valid betting e-process has zero power at G = 24 for δ ≤ 0.02 under every cap tested. It needs about 104–260 independent periods and a divergence bound. "Anytime-valid versus fixed-horizon" is not the binding choice; G is. | REPRODUCED |
| F9 | The record shows the signature of overfitting to review: 280 RC items in 52 rounds and a specification grown from 16.7 KB to 405.5 KB. Rounds 43–52 mostly repair consequences of the round-43 late-link rule or process metadata. | measured on the repository; the interpretation is a HYPOTHESIS |

**Recommendation (§6): narrow the claim and simplify the method.**

- **Keep** the infrastructure: ledger, timestamps, pre-registration, paired Brier, worst-case VOID bounds, and the e-process as monitor only.
- **Replace** source-selected events audited against a reference universe with an externally fixed question set forecast exhaustively.
- **Replace** the calibrated c* over an enumerated null class with linked variance blocks and every-subset late partitions, using instead a period-level test with one stated dependence assumption.
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
- whether the null class N contains the true law.

## 2. Identifiability and impossibility

**F1. Information is bounded by the number of periods.** Write the period mean of the increments as
M_b = θ + a_b + ē_b. Here a_b is a period-level component with variance τ², and ē_b is the average of n_b
cluster-level errors of variance σ². For any test whose validity rests on independence across periods, the
variance of θ̂ is at least (τ² + σ²/n)/G. The minimum detectable effect of the one-sided level-α test at power
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
- **The period-level variance of the primary is governed by a quantity observable before outcomes,** FULL's mean lean per period, read at issuance. The outcome-rate shock s can be estimated from reference-class history. Neither needs a registered outcome. At pre-registration, which precedes the forecasts, the bound must come from a blinded burn-in's forecasts or from a pre-registered cap on the mean lean. This holds for the outcome-rate channel only; other channels, such as skill that varies by period, are not covered.
- A system with no skill that only adds noise is worse than the baseline (δ = −noise², −0.0099 at noise 0.1, S1). The one-sided null θ ≤ 0 correctly includes it.

Whether the ± 0.3 increment shocks of `17` §6 are realistic under this channel is **EXPERIMENT_REQUIRED**. Settling
it needs the forecast lean and the reference-class outcome-rate variation, both measurable without outcomes of
registered events.

**F3. Serial dependence is an assumption, not a result.** If the period means may be arbitrarily persistent, no
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

Validity therefore needs a pre-registered bound ρ_max. With the critical value inflated by
√((1 + ρ_max)/(1 − ρ_max)), size holds:
- 0.36–0.96 % at ρ_max = 0.5;
- 0–0.04 % at ρ_max = 0.9.

Power falls with it (S3c, REPRODUCED):
- at δ = 0.01, from 68 % to 25–28 % at ρ_max = 0.5;
- at δ = 0.02, to 1.9–10.7 % at ρ_max = 0.9.

ρ_max cannot be verified from 24 periods. A test of serial correlation on G = 24 period means has little power;
that power was **not simulated here**. The assumption is a design input justified from reference-class history,
exactly like the block length in `17`.

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

**F6. Omissions are tolerable only far below the effect.** If a share m of the population is unobserved and every
paired increment lies in [−d, d], with d the bound on |p_F − p_C|, the identified set of θ is
(1 − m)·θ_obs + m·[−d, d]. The sign is identified only if m < θ/(θ + d) (S4, REPRODUCED):

| θ | d = 0.2 | d = 0.5 | d = 1.0 |
|---|---|---|---|
| 0.005 | 2.44 % | 0.99 % | 0.50 % |
| 0.010 | 4.76 % | 1.96 % | 0.99 % |
| 0.020 | 9.09 % | 3.85 % | 1.96 % |

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

**F8. Anytime validity does not buy information.** Ville's inequality makes a betting e-process valid at every
stopping time under the record-order conditional null. Its power over G independent periods is still limited by G.
Setup (S3b, 20,000 replications):
- period-mean standard deviation 0.0224 (τ = 0.01, σ = 0.1, n = 25);
- predictable plug-in bets, capped at λ = 0.5 (valid for increments in [−1, 1]) or λ = 2.5 (valid only if |p_F − p_C| ≤ 0.2 by design).

| Periods G | δ = 0.01, λ ≤ 0.5 | δ = 0.01, λ ≤ 2.5 | δ = 0.02, λ ≤ 2.5 |
|---|---|---|---|
| 24 | 0.0 % | 0.0 % | 0.0 % |
| 104 | 0.0 % | 13.1 % | 99.98 % |
| 260 | 0.0 % | 99.96 % | 100 % |
| 520 | 4.0 % | 100 % | 100 % |

The fixed-horizon block t on the same means detects δ = 0.01 at G = 24 in 68.7 %. An anytime-valid primary is
feasible only with:
- about 100–260 independent periods, for example weekly periods over two to five years, if weekly shocks are independent (itself an F3 assumption); and
- a pre-registered divergence bound.

The confidence-sequence literature makes the same point: betting confidence sequences (Waudby-Smith and Ramdas)
and e-values for comparing forecasters (Henzi and Ziegel; Choe and Ramdas) are valid under weak assumptions and
pay for it in sample size. These are UNVERIFIED citations, not re-read here.

## 3. Feasibility

**Minimum detectable effect at 80 % power, one-sided α = 0.05** (block t on G period means, σ = 0.1 per cluster,
n clusters per period; S2, REPRODUCED):

| τ | G | n = 25 | n = 100 | n → ∞ |
|---|---|---|---|---|
| 0 | 24 | 0.0105 | 0.0052 | 0 |
| 0.005 | 24 | 0.0108 | 0.0059 | 0.0026 |
| 0.01 | 24 | 0.0117 | 0.0074 | 0.0052 |
| 0.02 | 24 | 0.0148 | 0.0117 | 0.0105 |
| 0.01 | 48 | 0.0082 | 0.0052 | 0.0036 |
| 0.01 | 104 | 0.0055 | 0.0035 | 0.0025 |
| 0.02 | 104 | 0.0069 | 0.0055 | 0.0049 |

**Independent periods needed for 80 % power at n = 100:**

| Target δ | τ = 0.005 | τ = 0.01 | τ = 0.02 |
|---|---|---|---|
| 0.005 | 33 | 51 | 126 |
| 0.010 | 10 | 14 | 33 |
| 0.020 | 4 | 5 | 10 |

**Reading:**
- With monthly periods, a 24-month horizon and 100 resolvable clusters per month (2,400 clusters), δ = 0.01 is detectable if τ ≤ 0.01. δ = 0.005 needs more than four years of monthly periods at τ = 0.01.
- Supply of 25 clusters per month (600 clusters) moves the δ = 0.01 boundary to about τ = 0.005.
- Supply, the forecast divergence (σ), the lean (τ, F2) and the effect size are all unknown before Phase 2. Measuring the first three needs no registered outcome: **EXPERIMENT_REQUIRED**, the Phase 2 supply measurement of `17` §6, extended to lean and divergence.

**What these numbers do not cover:**
- the IUT, which divides the power as in F7;
- persistence, which multiplies the variance by up to (1 + ρ)/(1 − ρ) (F3);
- omissions, which must stay below F6's limit;
- the calibrated c* of `17`, which is larger than t_α and lowers power further (`17` §6 reports 28–60 % at δ = 0.01 and 600 clusters where the nominal value gives 78 %).

These bounds are optimistic for the current method and roughly attainable for the simplified one.

**Late evidence and correlated forecasts.**
- In the current method, late links change the variance blocks after the outcomes. That is the source of rounds 43–52 (RC-250 to RC-274).
- If the period is the unit of inference, cross-cluster links within a period need no rule at all, because the block sum already absorbs any within-period dependence. Links that cross periods are serial dependence and fall under the ρ_max assumption of F3, with a pre-registered sensitivity analysis that merges adjacent periods (G/2 blocks of two months).
- Correlated comparator forecasts matter only to the conjunction (F7); the first claim of a fixed sequence does not depend on them.

## 4. Alternatives compared

| | A. Current (`17` v49) | B. Externally fixed question set, period-level fixed-horizon test | C. Anytime-valid e-process / confidence sequence on period means | D. External benchmark or randomised question sampling | E. Partial-identification report |
|---|---|---|---|---|---|
| Population | source listings audited against a reference universe; omissions drawn and boxed | every question of a set fixed by an independent party before forecasting (or a beacon-seeded subsample) | as B | questions supplied by a third-party benchmark or tournament stream, or sampled at random from a large external pool | any of the above |
| Selection assumption | universe holder independent of relative skill (unprovable), plus supply exogeneity screened on a burn-in | universe holder independent of relative skill (unprovable; same residual as A) | as B | the benchmark's question writer independent of the arms (unprovable) | none for the bound itself; the width carries it |
| Dependence assumption | the true law lies in the enumerated null class N; links archived by T_D | period means independent, or AR with ρ ≤ ρ_max pre-registered | the record-order conditional null (stronger than the average null, `17` §3 item 3) | as B | stated per bound |
| Finite-sample guarantee | calibration on N_0 only (A3 says so) | t on G − 1 df: exact for independent normal period means; conservative at conventional α for a small number of independent, heterogeneous group estimates (Ibragimov and Müller; UNVERIFIED citation, conditions not re-read) | exact (Ville) under its null, for bounded increments | as B | the identified set is exact under the stated bounds |
| Power at G = 24, δ = 0.01, τ = 0.01, n = 25 | below B's 68.7 % (calibrated c* and the IUT) | 68.7 % (one comparison) | 0.0 % | as B | the sign is decided only if m < θ/(θ + d) |
| Complexity | 405 KB specification, 280 RC items, every-subset partitions, K_max budget | one test, one assumption (ρ_max), one sensitivity analysis | small kernel; already archived (GRAPA) | depends on the external provider; little CPE machinery | arithmetic |
| What it cannot do | confirm under persistence or selection outside N | confirm under persistence beyond ρ_max; say anything about questions outside the set | detect useful effects within two years | guarantee that the questions match CPE's target domain | turn a bound into a point estimate |

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
   - one pre-registered persistence bound ρ_max with its inflated critical value;
   - G_min;
   - a merge-adjacent-periods sensitivity analysis;
   - E's identified set reported beside the primary.

   The calibration of A3 becomes an implementation check of this one test on its stated law (size and power fixtures), not a certification over a class (F1–F3).
3. *Multiplicity.* A fixed-sequence family replaces the six-comparator IUT. Its first hypothesis is H0: θ(FULL − Design C) ≤ 0; the next is FULL against the best pre-registered single provider, then FULL against the equal-weight committee, each at α only after its predecessor rejects (F7). The order is an owner decision.

**Narrow the claim.** Proposed wording: "On the pre-registered question set Q, fixed by [holder] before forecasting, over periods [T_0, T_A), the expected Brier score of CPE's issued forecasts is lower than that of the Design C base rate (one-sided α = 0.05), under the stated assumption that period-level means have serial correlation at most ρ_max and that Q's composition is independent of the arms' relative skill." It makes no claim outside Q, none about investment value, and none from the monitor.

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
| M-1 | Size of the block t on G = 24 independent normal period means (20,000 replications) | 99 % upper bound ≤ 0.06; S3 gives 4.86 % (bound 5.23 %) |
| M-2 | Invalid control: the cluster-iid t on the same data | must exceed the M-1 bound at τ > 0; S3 gives 6.85 % (bound 7.28 %), so the control needs τ large enough to separate (OD4 sets the family) |
| M-3 | Size under AR(1) at ρ = ρ_max with the inflated critical value | upper bound ≤ 0.06; S3c gives 0.96 % at ρ_max = 0.5 |
| M-4 | Power at the pre-registered δ, τ, n and G | simulated power within ± 0.02 of the MDE formula (S2: 0.804, 0.803, 0.798 at the predicted 0.8) |
| M-5 | Exhaustive coverage: an event of Q with no FULL forecast by its issuance close | scored at the baseline forecast; an implementation that drops it fails |
| M-6 | Fixed-sequence familywise error under every configuration of true and false nulls (20,000 replications each) | upper bound ≤ 0.06 for each configuration; a later hypothesis is never tested after an earlier non-rejection |
| M-7 | Identified set: inject omitted share m with adversarial increments ±d | the reported interval contains the true θ in every replication; the sign is declared only when m < θ_obs/(θ_obs + d) |
| M-8 | Selection fixture of F4 (world B) presented as a source-listed population | refused as non-confirmatory, because the population is not Q; an implementation that accepts it fails |
| M-9 | Monitor never confirms | a crossing of the e-process produces no confirmatory record (the anytime-valid monitor row of `17` §6) |

Not yet written as code: M-6 to M-9 are specifications here. M-1 to M-4 are backed by S2, S3 and S3c.

## 8. Proof and assumption boundary

| Claim | Status |
|---|---|
| F1 information bound, F6 identified set, F7 IUT ≤ min marginal and fixed-sequence FWER | derivation (paper); the F7 FWER part is a textbook result, ESTABLISHED |
| F2 τ ≈ 2·s·\|E(p − b)\| | first-order derivation; REPRODUCED on one toy law only; other channels of period dependence not covered |
| F3 no uniform test under unrestricted persistence | ESTABLISHED in kind (`16` Appendix H); REPRODUCED for AR(1); ρ_max itself is UNPROVED and must be assumed |
| F4 non-identifiability of selection from listings | constructive counterexample, REPRODUCED; general for any test that reads listings only |
| F5 audit adds no identification once Q is the universe | derivation; relies on abstention = forecast b under a proper score |
| F8 betting power vs G | REPRODUCED for the plug-in rule; another betting rule could do somewhat better, but not escape the G bound of F1 |
| Holder's selection independent of relative skill | UNPROVED; untestable from the data under any design here |
| Realistic δ, τ, σ, supply | EXPERIMENT_REQUIRED (Phase 2 measurement; lean and divergence need no outcomes) |
| F9 overfitting | HYPOTHESIS with the discriminator of §5 |

## 9. Owner decision OD11 (new; options and consequences, not chosen)

| Option | Consequence |
|---|---|
| (a) Retain `17` v49 as the confirmatory method and continue rounds | keeps the audited-source design and the calibration on N; review cost per round stays as in rounds 43–52; power below B's |
| (b) Simplify to B as in §6, keeping `17`'s infrastructure | needs a dated amendment of `17` replacing the §3 item 3 primary and the §6 rows named in §6 above; the retired machinery stays in the record; Codex reviews the amendment at its exact SHA |
| (c) Narrow to D first (external benchmark) and run B later in the CPE domain | earliest falsifiable skill evidence; answers a different question; benchmark terms belong with OD8 |
| (d) Pause confirmatory design until the Phase 2 measurements (supply, lean, divergence, reference-class ρ) exist | no rounds wasted on parameters that are unknown; calendar cost only |

Options (b) to (d) leave OD1–OD10 in place. Under (b), several OD4 fields lapse with the machinery they parametrise: M_late, K_max and S_max, the null-class box and γ_cal. ρ_max and the period length replace them. That change is itself part of the decision.

## 10. What was run and what was not

**Run:**
- `python -I research/reproduction/reassessment_sims.py`, twice, byte-identical, about 13 s each, under Python 3.11.17 in a venv built with `pip install --require-hashes --no-deps -r research/reproduction/requirements.txt` (numpy 2.4.6, scipy 1.17.1). The output is committed in `16` Appendix AW.
- `check_appendix_scripts.py` without `--reference-code`, on the committed tree. The result is reported in the commit and the handoff.

**Not run:**
- a power simulation of the serial-correlation test at G = 24;
- M-6 to M-9;
- B's power at the calibrated levels of an OD4 class;
- any real data, provider or network.

**Next responsible agent.** Codex: an independent adversarial review of this document and Appendix AW at the exact
commit that carries them. The checks to make:
- reproduce S1–S5;
- look for a counterexample to F5 (a selection path that survives an exhaustive forecast of Q);
- look for a counterexample to F2's use as a pre-registration bound;
- check whether the fixed-sequence order loses a claim the owner needs.

The owner: OD11. No agreement is claimed until Codex has reviewed that commit.
