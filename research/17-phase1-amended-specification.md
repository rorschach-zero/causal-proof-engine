# 17 Amended Phase 1 specification and acceptance-test matrix (PROPOSED)

Jointly reviewable specification of the offline, synthetic-data measurement apparatus that both reviews
recommend as the only work to approve next. It amends `12-roadmap.md` Phase 1 with the dispositions in
`16-reconciliation-matrix.md` and Codex's exit criteria (`15-codex-review.md` §H). Status: **PROPOSED**,
version 5 (round 7: applies the seventeen findings that rounds 4–6 had recorded without revision, RC-60 and
RC-64 to RC-79 in `16` §3c–§3e, and the four findings of Codex's review of PR #4 at `10f8829`, RC-80 to RC-83 in
`16` §3f; round 4 had amended it for RC-56 to RC-63, round 3 for RC-48 to RC-55, round 2 for RC-28 to RC-47).
**This version is the OD10 decision diff:** every change carries its matrix ID, the owner approves it by
recording OD10 on issue #3 or names the items to revert, and fields that are the owner's to set (OD4: H_max,
d_max, block length, shock amplitude, estimand naming; OD5: latency windows, inclusion predicate) are left as
named fields, not chosen here. Awaiting Codex's review of this commit and owner decisions OD1 and OD10. Nothing
is implemented; no roadmap phase is approved by this document. REVISION throughout unless labelled otherwise.

## 1. Objective

Reduce scientific and engineering uncertainty about the measurement apparatus with synthetic data only, so
that a later, separately authorised Phase 2 can register real events under a protocol whose validity has been
demonstrated adversarially. No network, no providers, no broker, no Jev client, no hosting decision, no learned
components, no real event.

## 2. What changes relative to `12-roadmap.md` Phase 1

| `12` Phase 1 said | Amended to | Reason (matrix ID) |
|---|---|---|
| e-process consumes resolutions in ledger order | one increment per pre-declared outcome cluster; server receipt time; **primary confirmatory test for the average-effect estimand = fixed-horizon paired cluster test with a pre-registered calendar-block dependence model; the cluster-level e-process is the anytime-valid monitor of the sequential conditional null** (roles assigned in round 3 after Codex exhibited cross-cluster and time-varying structures; REPRODUCED) | RC-01, RC-02, RC-49, RC-50 |
| `EXPIRED_NO` for late YES | YES iff occurrence met the deadline (evidence of occurrence time required, declared latency window); early NO only when logically final; four timestamps | RC-11 |
| anchor detects any byte change | any change in the anchored prefix or truncation below it; unanchored window reported | RC-13 |
| covariance-based fusion weights | input validation first; equal weights default; second-moment simplex pool behind a flag, synthetic evaluation only | RC-06, RC-15 |
| gate records with owner MAC | capability records with owner public-key signature, environment, release digest, evidence digest, epoch, nonce, expiry; consumed-authorization store | RC-12, RC-14 |
| e-process false alarm ≤ α + 0.015 over seeds | exact one-sided 99 % binomial upper bound ≤ 0.06 on each valid-null family over 20,000 replications (a 95 % bound at 2,000 replications rejects a correct size-0.05 implementation 39 % of the time, RC-48; REPRODUCED), plus an invalid-null control that must exceed it | RC-01, RC-24, RC-48 |
| power study for N8 | power and protocol report with clusters, missingness and abstention, for the fixed-horizon primary test and for the monitor separately (the primary detects δ = 0.01 at 600 independent clusters with 80–93 % power where the monitor crosses in 27–32 %; REPRODUCED, `16` Appendix E); Phase 2 statistical contract drafted for OD4 | RC-24, RC-61 |
| secondary fixed-horizon test at cut-offs 12 and 24 months (round 1) | one primary cut-off, 24 months after first cohort entry; the 12-month look is a pre-registered interim for futility and integrity only, never confirmation (two confirmatory looks at nominal α give a type-I error of 8.0 % in normal theory and 8.8 % for the block test on the valid clustered null; REPRODUCED); an O'Brien–Fleming-type spending over both looks is the alternative for OD4 | RC-56 |
| no interval-scoring decision | one scored point probability; interval as declared ambiguity set; scorer rejects interval-only forecasts | RC-05 |
| (not present) | shrinkage estimator replacing the base-rate floor, with property tests; built only after OD9a changes `AGENTS.md` §2 item 7 | RC-03, RC-33 |
| (not present) | cluster closure rule: immutable membership declared explicitly for every EventSpec (no implicit singleton, RC-53), single increment after every member is resolved or pre-declared VOID before the cluster's outcome-knowable time t*_k (round 3 wrote "before any member's outcome was received", which left the publication-to-receipt gap open for VOID declarations; RC-57, propagation of RC-52), λ locked at t*_k; a dependence discovered after registration is never a ground for VOID or merge (RC-51) | RC-29, RC-51, RC-53, RC-57 |
| (not present) | forecast eligibility against the earliest time an outcome was knowable (adjudicated `knowable_at`), not only against registry receipt | RC-52 |
| (not present) | deterministic oracle fixtures for the shrinkage estimator (Beta posterior and logit-shrinkage values), beside the property tests; the interval transformation is defined (endpoint-wise logit shrinkage toward the posterior 5 % quantile, mean and 95 % quantile) with deterministic expected bounds | RC-54, RC-58 |
| (not present) | positive-control oracles for each test kernel: deterministic e-value and fixed-horizon statistic fixtures and a pre-specified alternative with an exact lower binomial bound on the rejection rate, so that an inert kernel fails (T-36) | RC-63 |
| (not present) | T-31 mutates each of the seven signed capability fields individually under an otherwise valid signature, with canonical-serialisation cases | RC-62 |
| anchors as owner-side records | anchor store outside the writer's control (separate principal); local-only anchors reported as self-attested | RC-13, RC-34 |
| (not present) | monotonic high-water-mark clock persisted in the ledger; capability checks fail closed on clock rollback | RC-37 |
| (not present) | α-spending ledger and IUT evaluation in the statistics kernel | RC-08 |
| (not present) | provider-neutral attribution check on commit and PR text in CI; the same check verifies that author and committer identity of every commit are on the designated list (`AGENTS.md` §7), because text checks cannot see metadata (round 7) | RC-26, RC-81 |
| (not present) | T-34 requires secret **confinement**, not a redacting representation: no object reachable from the escaping exception holds the raw secret; the probe traverses object state, not `repr` (round 4's redacting holder was itself insufficient; REPRODUCED) | RC-60 |
| monotonic high-water mark from receipt times | every clock-dependent check persists (wall time, monotonic time, boot id) in the same transaction, admitted or rejected; a boot-id change or a wall-minus-monotonic drift beyond tolerance is an unverifiable discontinuity that invalidates every outstanding capability until re-authorisation (the receipt-time watermark admitted an expired capability after a rollback, and after an idle window no wall-clock rule can; REPRODUCED) | RC-65, RC-73 |
| nonce consumption atomic with acknowledgement | acknowledgement only after the record carrying the consumed nonce is in an externally anchored prefix; epoch rotated and anchored at every process start (a nonce consumed after the last anchor is replayable after a restore; REPRODUCED) | RC-74 |
| (not present) | `Forecast` keyed by (event id, arm, forecaster version, scoring slot); the scored record is fixed by the key, never chosen after the outcome (scoring the revision nearest Y turns an honest −0.04 into +0.16; REPRODUCED) | RC-75 |
| `knowable_at` = publication or public occurrence | `knowable_at` also includes logical finality, deadline + declared latency window, for eventually-by-deadline predicates; a timely occurrence reported after that window resolves VOID, never YES (REPRODUCED, arithmetic) | RC-77 |
| F-02: timestamp-less late YES → `EXPIRED_NO` | a reported occurrence with no occurrence time and no evidence of lateness resolves VOID (cap, bounds); `EXPIRED_NO` requires evidence of lateness or of definitive non-occurrence | RC-71 |
| (not present) | partial-VOID arithmetic: the increment is the mean over **resolved** members; t*_k over resolved members' timestamps; an all-VOID cluster emits nothing and counts its members against the cap; worst-case bounds impute the VOID members | RC-67 |
| (not present) | membership mutation tested from registration onward, not only after t*_k | RC-66 |
| (not present) | accrual cut-off = 24 months − H_max and a maximum declared horizon H_max (OD4 fields); eligible-but-pending clusters count as missing under the cap | RC-68 |
| t test over equal calendar-block means | point estimate = mean over clusters; variance = block-sum (cluster-robust) form on G − 1 df; blocks set only the variance (equal block means weight periods and reverse the sign on an unequal-supply oracle; REPRODUCED) | RC-69 |
| A3 bound stated as if a validity property | the primary test's size is **calibrated on the pre-registered null families, not finite-sample valid**: two-point and rare-catastrophe families reported with exact size (7.3 % and up to 15 % at 24 blocks); the Phase 2 contract pre-registers a skew bound; and **no finite-sample-valid bounded-mean test of any form** has power above α(1 + δ)^G over G blocks (PROVED, `16` Appendix H: 8 % at δ = 0.02 and 16 % at δ = 0.05 over 24 blocks), so the conditional t test is the only route at this horizon | RC-72, RC-80 |
| 47 % power at δ = 0.02 under ± 0.3 period shocks | 18 % at 600 and at 1,200 clusters over the design's 24 periods: the detectable effect under that model is about δ = 0.065 at any supply; the 47 % figure averaged over 120 periods and is withdrawn | RC-70 |
| power stated for one paired comparison | power stated for the **confirmatory conjunction** (IUT over six comparators) under a joint generator at its least-favourable configuration: 21 % to 77 % at δ = 0.01 and 600 clusters depending on comparator error dependence, where the single comparison has 77 % (REPRODUCED, `16` Appendix H) | RC-83 |
| (not present) | one pre-registered issuance window and evidence cutoff per event for every arm; the primary cohort and its burn-in start only when every arm of the comparator set is operational (Phase 4 of `12`); Phase 2 registrations are a Design C track record and exploratory | RC-76 |
| (not present) | pre-registered eligible-event inclusion predicate and sampling rule; every candidate logged with its decision before any forecast exists; T-37 | RC-78 |
| T-15 = one injected-outcome detector | synthetic point-in-time store with `observed_at`, `available_at` and vintage id, an as-of read interface that refuses every read with `available_at` after the forecast's evidence cutoff; the statistical detector is the second line | RC-79 |
| A7 requires malformed-certificate tests | removed from A7: Phase 1 has no certificate verifier (certificates are Phase 5, `12`); the test moves to §7 with its phase | RC-82 |
| A0 names OD1, OD2, OD9a | A0 also requires OD10 before T-34 and the secret-handling code are built; the rest of Phase 1 is not held by OD10 | RC-64 |
| time-shifted holdout in tests | forbidden-future-information leak detector | RC-09 |

## 3. Scope (build)

1. **Schemas.** `EventSpec` with typed resolution predicate (source, record selector, field, comparator, value,
   not-before, not-after), mandatory `cluster_id` (a singleton is declared explicitly as a cluster with one
   member; there is no implicit default, RC-53), `predicate_kind ∈ {milestone-deadline, terminal-falsifier}`,
   four timestamps (occurrence, publication, receipt, adjudication), latency window, and the adjudicated
   `knowable_at`: the earliest time at which the outcome was publicly determinable (the publication time, or the
   occurrence time when the occurrence is itself a public act), recorded with its evidence and audited (RC-52).
   `Forecast` with one scored point probability, declared ambiguity interval (low ≤ point ≤ high), forecaster id and version, prompt and
   model hashes, evidence ids. `JevRecord` (inputs, both polarities, model hash, routing result, cost).
   `Capability` (owner-signed: capability, environment, release digest, evidence digest, epoch, nonce,
   expiry). `ResearchOutput` JSON schema for future adapters. `Cluster` registration record.
   *Scoring slot (RC-75).* `Forecast` records are keyed by (event id, arm, forecaster version, scoring slot).
   The EventSpec pre-registers its scoring slots; the default is one slot, filled by the first forecast received
   for the arm, and a second record for an occupied slot is refused at submission. An EventSpec with a revision
   schedule names every slot in advance, and every slot is scored and reported, never a chosen one: scoring the
   revision nearest the outcome turns an honest null expected increment of −0.04 into +0.16 (REPRODUCED, `16`
   Appendix G). Nothing in the eligibility rules (receipt before t*_k) constrains which eligible record is used;
   only the key does.
   *Logical finality (RC-77).* For an eventually-by-deadline predicate, `knowable_at` = min(publication time,
   public occurrence time, deadline + declared latency window): after the last of these the outcome is logically
   final, and a forecast received in the gap between deadline + window and the source's formal record is not
   eligible (fixture F-21b: deadline 100, window 10, record received 118, forecast received 113; eligible under
   the version-4 rule, not under this one; REPRODUCED). A report of timely occurrence received after deadline +
   window resolves VOID with a source-latency defect logged, never YES; otherwise the finality claim is false,
   so the latency window is pre-registered per source long enough that such a report is a source failure.
   *Resolution rules (RC-11, RC-71).* Each EventSpec names its source's pre-registered occurrence-time rule.
   YES requires evidence that the occurrence met the deadline. A reported occurrence with no occurrence time
   and no evidence of lateness resolves VOID (counted against the cap and carried by the worst-case bounds,
   because only a YES can lack a time, so this VOID is outcome-dependent); `EXPIRED_NO` requires evidence that
   the occurrence was after the deadline or that the event had definitively not occurred by it (F-02a, F-02b).
   Sources that do not publish occurrence times are a matter for OD5 (exclusion at registration), not for
   resolution.
   *Point-in-time store (RC-79).* A synthetic point-in-time store with (entity, feature, value, `observed_at`,
   `available_at`, vintage id) and an **as-of read interface** that takes the forecast's evidence cutoff t_cut
   and refuses, deterministically, every read whose `available_at` is after t_cut. The interface, not a
   statistical detector, is the leakage control named by `AGENTS.md` §8; the detector of T-15 is the second
   line. Built only after OD9a, with T-15.
2. **Ledger and registry.** Single transactional writer (SQLite in one process) with canonical JSONL export;
   server receipt time on every admission; append atomic with state change (no phantom records);
   deterministic replay of registry, cluster, capability and e-process state; anchor = committed-prefix
   digest with an explicit unanchored-window report; restore from a clean checkout in CI.
   *Candidate log (RC-78).* The registry holds the eligible-event candidate log of §6: every candidate
   considered is recorded with id, source, time, decision and reason **before** any forecast on it exists; a
   registration without a prior candidate entry, and a candidate entry written after a forecast on the same
   event, are refused; the log is part of the ledger and of the replay (T-37).
   *Anchor trust boundary (RC-34).* A digest only detects tampering if the copy it is compared against cannot
   be rewritten by the ledger writer. Anchors are therefore emitted through an `AnchorStore` interface whose
   production implementation is held by a principal other than the writer (owner-held signed record, or an
   append-only store the writer has no credential for; which one is part of OD6). In Phase 1 the external
   store is a test double that the writer cannot open for writing (separate directory with a different OS
   principal in CI, or an in-memory store owned by the test harness), plus an export of every anchor as a
   record the owner can commit to Git. Verification against a local anchor copy is reported as
   **self-attested**, never as verified; the restore test names which anchor it verified against.
   *Clock (RC-37, RC-65, RC-73).* Every clock-dependent check, admitted or rejected, persists (wall time,
   monotonic time, boot id) in the same transaction before it returns its verdict, and the persisted wall time
   is a high-water mark: a check whose wall time is below it fails closed and is logged. A boot-id change, or a
   change of wall-minus-monotonic beyond the pre-registered tolerance, is an **unverifiable discontinuity**:
   every outstanding capability is invalid until the owner signs a fresh epoch (re-authorisation), and the
   discontinuity is logged. Two earlier wordings are withdrawn with evidence (`16` Appendix F and G): a
   watermark advanced only by admissions admits an expired capability after a rollback (RC-65), and no rule that
   reads only the wall clock can see an idle window before a rollback or a reboot (RC-73). From Phase 2 the
   `AnchorStore`'s signed timestamp bounds elapsed time at every anchor.
   *Epoch rotation (RC-74).* The capability epoch is rotated at every process start and the rotation is
   anchored before any capability is checked, so that a capability signed for an earlier epoch is stale after
   any restore; item 5 states the acknowledgement rule that goes with it.
3. **Statistics kernel.** Fixed-horizon paired comparison of cluster increments at pre-registered cut-offs
   with a pre-registered calendar-block dependence model (the primary confirmatory test of the §6 average-effect
   estimand); e-process consumer fed only by registry resolutions, one increment per outcome cluster,
   predictable λ (archived GRAPA rule, λ_max = 0.5), running maximum (the anytime-valid monitor); proper scores
   (Brier, log clipped at a pre-registered bound); IUT evaluation over a declared comparator set; α-spending
   ledger; shrinkage estimator for rare probabilities (Beta posterior for cohort data, logit shrinkage of a
   model estimate with a pre-registered weight function; built only after OD9a, see A0).
   *Shrinkage of the interval (RC-58).* The estimator maps the model's declared (low, point, high) and the
   cohort (s, n) to (low′, point′, high′) by the same logit-space convex combination with the same weight
   w(n), applied endpoint-wise: low toward the posterior 5 % quantile, point toward the posterior mean, high
   toward the posterior 95 % quantile; endpoints are clipped to [10⁻⁶, 1 − 10⁻⁶] before the logit. Each map is
   monotone and the three targets are ordered, so low′ ≤ point′ ≤ high′ whenever the inputs are ordered; a
   collapsed model interval acquires the reference-class spread, and at n = 0 the model interval is returned
   unchanged. The output interval remains a declared ambiguity set with no coverage claim (RC-05).
   *What each test tests (RC-49, RC-50).* The e-process is a test of the **sequential conditional null**
   E[X_k | F_(k−1)] ≤ 0 at every closure, where F_(k−1) is everything recorded before the cluster's
   outcome-knowable time. That null is stronger than the §6 estimand's null (population-average Brier
   difference ≤ 0): it is false, while the average null is true, whenever skill varies over time or clusters
   open at the same time share a shock. Under a two-state macro regime the cluster-level e-process crosses in
   28.9 % of 20,000 paths, and under skill that is +0.12 for the first sixty clusters and −0.12 for the next
   sixty (average exactly zero) in 62.8 %; the valid clustered null gives 0.055 % (REPRODUCED, `16` Appendix
   D). A crossing is therefore evidence against the conditional null only, is labelled as such, and is never
   alone a confirmatory result or a promotion trigger. The fixed-horizon test addresses the average estimand
   directly; its variance uses calendar blocks as the dependence unit (period-level shocks are the dependence
   that pre-declared outcome clusters cannot capture), with the block length pre-registered in the Phase 2
   contract from reference-class history, never from registered outcomes. Its limits are stated rather than
   hidden: with independent period shocks the block-of-one-period test holds size (5.1 %) where a naive
   cluster-iid variance does not (13.4 %); with a persistent regime (P(stay) = 0.9) **no tested block length
   holds size at 120 clusters over 24 periods** (14.8 % to 27.1 %), which is a supply and horizon question for
   OD4 and OD5, not a property any Phase 1 code can fix (`16` §4.1, Appendix D).
   *The primary statistic (RC-69).* The point estimate is the mean over clusters, θ̂ = (1/N) Σ_k X̄_k, which is
   the §6 estimand; calendar blocks enter **only the variance**, in the block-sum (cluster-robust) form
   Σ_b (Σ_{k∈b} (X̄_k − θ̂))² / N² · G/(G − 1) on G − 1 degrees of freedom. A t test over equal block means
   estimates a period-weighted quantity instead: on blocks of sizes 1 and 9 with values +0.5 and nine times
   −0.1 it gives +0.20 where the per-cluster estimate is −0.04, and when supply covaries with the period shock
   the two statistics test different hypotheses (88 % against 5.7 % rejection; REPRODUCED, `16` Appendix F).
   Under supply–shock covariance the per-cluster estimand itself contains the shock, so OD4 names the estimand
   (per cluster, as §6 says, or period-balanced) together with the dependence model.
   *What the size bound means (RC-72, RC-80).* The primary test's size is **calibrated on the pre-registered
   null families of T-12; it is not finite-sample valid for every bounded-mean null.** On a two-point
   period-shock null where every cluster in a block shares one outcome and the block increment is +0.903 or
   −0.897 with mean zero, the one-sided t over 24 blocks has exact size 7.33 %; over zero-mean two-point nulls
   it reaches 15.2 % at 24 blocks, always at the rare-catastrophe shape (REPRODUCED, `16` Appendix G). No other
   kernel repairs this at the design's horizon, and the statement is a theorem, not a simulation result
   (`16` Appendix H): any test that is level α against **every** mean-zero law on [−1, 1] has power at most
   α(1 + δ)^G against every alternative with mean δ, because the mean-zero mixture (1 − ε)·P₁ + ε·δ₋₁ with
   ε = δ/(1 + δ) produces a P₁-distributed sample with probability (1 + δ)^−G. Over G = 24 blocks that is 8 %
   at δ = 0.02, 16 % at δ = 0.05 and 32 % at δ = 0.08; 80 % needs δ ≥ 0.1225, or 141 blocks at δ = 0.02. The
   Phase 2 contract therefore pre-registers the null families it is calibrated on, a cap d_max on
   |p_FULL − p_baseline| for forecasts entering the primary and a reference-class bound on the share of
   catastrophe periods (the skew bound; OD4), reports the two-point families with their exact size, and reports
   the bounded betting test over block means beside the primary as the distribution-free check with its power
   stated (zero at every useful effect over 24 blocks for the archived kernel; at most the bound above for any
   kernel).
   *Partial VOID (RC-67).* For a cluster with resolved and pre-declared VOID members the increment is the mean
   over the **resolved** members, so the cluster keeps weight one with fewer members; t*_k is taken over the
   resolved members' timestamps (a pre-declared VOID has no outcome and no `knowable_at`); a cluster whose
   members are all VOID emits nothing and its member count goes against the VOID cap; the worst-case bounds of
   §6 impute each VOID member and recompute the mean over all members (fixture F-24). Dropping the cluster is
   rejected because it would make the increment depend on the VOID declaration of a sibling.
   *α-spending semantics (RC-44).* The ledger reserves and irreversibly debits α_j when the j-th promotion
   test is **registered**, before its evaluation data are unsealed; a failed, non-rejecting, cancelled or
   interrupted test keeps its debit, and j indexes attempts, not promotions. A debit that happened only on
   success would let a proposer run unlimited challengers at no cost.
   *Cluster increment (RC-41).* Member i contributes X_i = (p_baseline,i − Y_i)² − (p_FULL,i − Y_i)², which lies
   in [−1, 1] for probabilities in [0, 1]; the cluster increment is the **unweighted mean** X̄_k over the
   members, so X̄_k ∈ [−1, 1] and 1 + λ_k X̄_k ≥ 0.5 at λ_max = 0.5 (REPRODUCED, `16` Appendix C); a sum is not
   admissible. The mean matches the §6 estimand (expected Brier difference per cluster, clusters equally
   weighted); the event-weighted average is reported as a descriptive secondary, never bet on.
   *Cluster closure (RC-29, RC-51, RC-52, RC-53).* A cluster's member list is immutable from its registration
   record onward and must be complete before the earliest `not_before` of any member; an EventSpec that names
   a cluster after that point is rejected, and an EventSpec without a `cluster_id` is rejected (a singleton is
   declared as a one-member cluster; an implicit default would let dependence go undeclared silently, which is
   fixture F-15, RC-53). The cluster emits exactly one increment, the mean X̄_k defined above, and only when
   every member is resolved or was pre-declared VOID before the cluster's outcome-knowable time t*_k defined
   below (a VOID declaration received at or after t*_k is refused and the member is scored as resolved, because
   the publication-to-receipt gap would otherwise let a member be dropped on a known outcome; RC-57, the same
   cutoff RC-52 applies to forecasts and to λ); a cluster with an unresolved member emits nothing. The
   cluster's **outcome-knowable time** is t*_k = min over members of min(outcome receipt time, adjudicated `knowable_at`); because `knowable_at` is
   adjudicated after the fact, t*_k is computed at closure from recorded timestamps and is deterministic. The
   betting fraction λ_k is computed from the increments of clusters closed before t*_k and is frozen there, so
   that no information from a partially resolved or publicly knowable member enters its own λ. Forecasts on a
   member are eligible for the increment only if their server receipt time is strictly before t*_k; a forecast
   received after the outcome was publicly knowable but before the registry received it is excluded by this
   rule, deterministically, at adjudication (RC-52; a receipt-only cutoff admitted it). Increments enter the
   e-process in order of closure time. **Dependence between clusters discovered after registration is never a
   ground for VOID or merge** (RC-51): any such adjudication after outcomes can be known would let an
   unfavourable increment leave and a favourable one stay, so both clusters remain in the confirmatory process
   exactly as registered, the discovery is recorded as a declaration defect, and the dependence audit (count,
   list, calendar position) is reported beside every read-out and feeds the dependence model of the primary
   test. Dependence is declared once, at registration, when nothing about any outcome is known. This rule
   closes the within-cluster channel only; cross-cluster dependence is handled by the role assignment above.
4. **Fusion (baseline only).** Input validation (finite, 0 ≤ low ≤ point ≤ high ≤ 1), mandatory-input check
   (three providers plus Jev record), typed decisions, equal weights; second-moment simplex pool behind a
   flag, evaluated on synthetic data only; n_eff as a diagnostic with the degenerate-history case flagged.
5. **Capability model (offline).** Signature verification with the owner's public key over the **whole**
   tuple (capability, environment, release digest, evidence digest, epoch, nonce, expiry) under one canonical
   serialisation, so that no field can be substituted under a valid signature (RC-62); epoch, nonce,
   expiry, environment and release checks; consumed-authorization store; demotion persistence; state replayed
   from the ledger; no network path exists. Expiry is checked against both the current clock and the
   persisted high-water mark (item 2): a check whose current time is below the high-water mark, or whose
   capability expired at any time at or below the high-water mark, fails closed (RC-37); a clock discontinuity
   (item 2) invalidates every outstanding capability until re-authorisation (RC-73).
   *Durable consumption (RC-74).* The protected operation acknowledges only after the ledger record carrying
   the consumed nonce is inside an externally anchored prefix (synchronous anchor; the Phase 1 double is the
   harness-owned store of RC-34). If the anchor fails, the operation fails closed and no state change is
   acknowledged. Atomic consumption (RC-43) made the nonce unusable twice in one ledger; it did not make the
   consumption survive a restore to the last anchor, after which replay saw an unused nonce and a stale epoch
   and accepted the same signed capability again (REPRODUCED, `16` Appendix G). Protected actions in Phase 1
   are rare (gate promotions), so one synchronous external round trip each is affordable.
   *Enforcement at the action boundary (RC-43, RC-46).* The protected operation itself (in Phase 1: gate
   promotion and any other state change that a capability authorises) verifies the signature and performs
   the epoch check, the nonce insertion under a uniqueness constraint, the state change and the
   acknowledgement in **one writer transaction**; a second presentation of the same nonce, concurrent or
   later, fails inside that transaction. No object is authority: a state object fabricated through a
   non-public constructor, reflection or a dynamic import carries no valid signed capability and is rejected
   by the operation. The static "no research import of the executor" check is a lint, not evidence.
6. **Negative controls and fault injection (permanent in the test suite).** Every fixture in §5.1 whose
   component is in Phase 1 scope (the B4 counterexamples of `15-codex-review.md` and the probes P1–P5 of
   `01-architecture.md` §3, restated here so that this document is complete without the review branch,
   RC-35; the two broker-path fixtures are listed with their later phase, RC-42); valid-null, clustered-null and
   interleaved-null e-process generators with exact binomial Monte Carlo bounds; macro-shock (independent
   periods and persistent regime) and time-varying-skill generators (RC-49, RC-50; F-22, F-23);
   publication-to-receipt gap forecasts (F-21); forbidden-future-information
   leak detector; backdating; phantom-on-failure; replayed, forged, expired, wrong-environment, wrong-release
   capabilities; NaN, reversed and out-of-range inputs; truncated and suffix-rehashed ledgers; simultaneous
   ledger-and-local-anchor replacement; clock rollback; cluster membership mutation and partial-cluster
   update attempts; concurrent submissions and concurrent presentation of one capability; secret canaries in
   logs, structured error paths and the **whole reachable exception graph** (`__context__`, `__cause__`,
   traceback frame locals), because sanitising `__context__` inside an `except` block does not prevent
   chaining (REPRODUCED, RC-47); the canary probe traverses **object state** (attributes, slots, containers,
   closures, exception `args`), not `repr`, because a holder with a redacting `repr` still stores the raw
   secret in an attribute that a crash collector serialises (REPRODUCED, RC-60).
7. **Power and protocol report.** Reproduce the D1 table with an independent recurrence check; extend to
   clustered outcomes, missingness and abstention; publish the detectable effect at 300 and 600
   independent-equivalent units; draft the Phase 2 statistical contract (§6).
8. **CI.** Pinned direct and transitive dependencies with hashes; Python 3.11 and 3.13; strict type checking;
   property tests; Lean job on the pinned toolchain for the retained lemmas including a deliberately false
   proof that must fail, with a network or cache failure reported as "not verified", never as pass;
   provider-neutral check of commit and PR text for attribution trailers, and of every commit's author and
   committer identity against the designated list of `AGENTS.md` §7 (RC-81: a text check cannot see
   metadata); `research/original/` verified by manifest and excluded from all tooling; static check that no
   research module imports the executor package (useful, not sufficient: dynamic paths are covered by T-34).

**Explicitly out of scope.** Credal network and every credal-set LP (including the inner worst-case LP of
RC-10; its test moved to §7, RC-32), hazard model, allocator and cost model, provider adapters, Jev client, SIM
read-only, any hosting or cloud identity, self-improvement loop, any learned calibration, any real event, any
change to `AGENTS.md` (OD9 is the owner's; OD9a is a prerequisite of A0, not part of this scope).

## 4. Acceptance criteria (all must hold)

| # | Criterion | Codex §H exit criterion it satisfies |
|---|---|---|
| A1 | Replay of any valid synthetic history equals online state byte for byte; injected append failure, process death, concurrency, truncation and clock rollback produce no acknowledged phantom record; restore from a clean checkout reports the anchored prefix and the unanchored window | H3 |
| A2 | Every §5.1 fixture whose component is in Phase 1 scope is rejected or correctly graded, with a named test per case (F-11 and the HTTP source of F-12 are deferred to their phases, RC-42); backdated submissions cannot become prospective evidence | H4 |
| A3 | Over ≥ 20,000 replications per family, exact one-sided 99 % binomial (Clopper–Pearson) upper bound ≤ 0.06 at α = 0.05 (a correct size-0.05 implementation passes with probability 0.99995, size 0.06 with 0.010, RC-48; REPRODUCED) on: the cluster-level e-process crossing rate for the valid-null, clustered-null and interleaved-null families; the fixed-horizon primary test's rejection rate, with the cluster-weighted statistic and its pre-registered block unit (RC-69), for those families, the independent-period macro-shock family and the Poisson-supply families (RC-69). Per-event betting on clustered data, and the cluster-iid variance on the macro-shock family, are retained as invalid-null controls and must exceed the bound. The e-process crossing rate on the macro-shock and time-varying families, and both methods on the persistent-regime family, are **reported, not bounded** (RC-49, RC-50): they are the evidence for the role assignment in §3 item 3 and the input to OD4. **The bound is a calibration on these pre-registered families, not a finite-sample validity property** (RC-72): the two-point period-shock family (exact size 7.33 % at 24 blocks) and the rare-catastrophe two-point family (up to 15.2 %) are reported with their exact size and no pass condition, the Phase 2 contract carries the skew bound that makes them out of scope (§6), and no kernel of any form can do better than α(1 + δ)^G against every bounded-mean null (PROVED, RC-80, `16` Appendix H). Each kernel must also pass the positive controls of T-36 (deterministic oracles and a bounded minimum rejection rate under a pre-specified alternative), because an inert kernel satisfies every upper bound above (RC-63) | H6 |
| A4 | All malformed, non-finite, incoherent or incomplete research inputs rejected across the property-test domain; no silent dropping or duplicate-provider overwrite | H2 |
| A5 | Forged, replayed, expired, wrong-environment, wrong-release and concurrently presented capability records rejected; demotion survives restart; a fabricated in-process state object is never accepted as authority by a protected operation (RC-46); no offline proof is described as deployed isolation | H5 |
| A6 | Power and protocol report reviewed, seeds and generators committed; detectable effect at 300 and 600 independent-equivalent units for the fixed-horizon primary test and, separately, for the monitor (RC-61), computed over the design's 24 calendar periods with clusters per period varied (RC-70); power of the **confirmatory conjunction** (IUT over the comparator set) under the joint generator of T-16 at its least-favourable configuration, for at least the two dependence extremes (RC-83); Phase 2 contract drafted for OD4 | H6 |
| A7 | CI green including the Lean known-false rejection; dependency lock reproducible; attribution and commit-identity check present (T-09); `research/original/` unchanged by manifest (the malformed-certificate tests named here until round 7 belong to the Phase 5 certificate verifier and are specified in §7, RC-82) | H7 |
| A8 | Independent review by a reviewer other than the author; owner acceptance of scope; local green tests alone do not satisfy merge policy | H8 |
| A0 | Owner decisions OD1, OD2 and OD9a (the `AGENTS.md` §2 item 7 and item 10 wording, which the shrinkage estimator and the leak detector would otherwise contradict, RC-33) recorded before implementation starts; until OD9a is recorded, T-20, T-15 and the point-in-time store are not built and the floor is neither built nor removed; **OD10 recorded (approval of this version-5 diff, or the owner's explicit choice of other wording for T-34) before T-34 and the secret-handling code of §3 item 5 are built; the rest of Phase 1 is not held by OD10** (RC-64); OD3–OD5 recorded before the Phase 2 contract is frozen | H1 |

## 5. Acceptance-test matrix

Each test is a CI check or a reviewed artefact. "Fixture" names the synthetic generator or counterexample.
Status for all rows: **not implemented** (Phase 1 not approved).

| Test | Criterion | Fixture / generator | Pass condition | Matrix IDs |
|---|---|---|---|---|
| T-01 | A2 | event and forecast with `known_at` years in the past, submitted now | rejected; receipt time is the server clock; `known_at` stored as an audited caller claim | RC-02 |
| T-02 | A2 | forecast received after the cluster's first outcome receipt; forecast received after the adjudicated `knowable_at` of a member but before the registry received that outcome (fixture F-21); forecast received after deadline + latency window but before the source's formal record on an eventually-by-deadline predicate (fixture F-21b, RC-77); forecast received outside the event's pre-registered issuance window or built on evidence with `available_at` after its evidence cutoff t_cut (RC-76); two eligible forecasts with different ids for one (event, arm, forecaster version, slot) key (RC-75) | all excluded from the increment at adjudication, deterministically from recorded timestamps; retained as labelled late or out-of-window forecasts; a forecast received before every cutoff and inside the window is eligible; for the slot case the second record is refused at submission under a one-slot EventSpec and both are scored under a schedule | RC-01, RC-02, RC-52, RC-75, RC-76, RC-77 |
| T-03 | A2 | YES with occurrence time before the deadline, observed after it within the latency window; YES reported with no occurrence time and no evidence of lateness (F-02b) | graded YES; resolved VOID with the source rule named (never `EXPIRED_NO`, RC-71) | RC-11, RC-71 |
| T-04 | A2 | YES with occurrence time after the deadline (F-02a); NO before the deadline on an eventually-by-deadline predicate; NO on a logically final predicate; NO by expiry at deadline + latency window with the source's formal record arriving later; report of timely occurrence arriving after deadline + latency window | EXPIRED_NO; rejected (not final); RESOLVED_NO; resolved NO at deadline + window with `knowable_at` = that time (RC-77); VOID with a source-latency defect logged, never YES (RC-77) | RC-11, RC-71, RC-77 |
| T-05 | A1 | injected write failure during registration, commit, resolution and capability change | no state change; no acknowledged record; replay equals pre-failure state | RC-12 |
| T-06 | A1 | process killed between write and acknowledgement; two concurrent submissions of the same id; two eligible forecasts with different ids for one scoring-slot key before t*_k (oracle pair 0.3 and 0.7 with Y = 1, RC-75) | at most one durable record; replay deterministic; the slot case: second record refused (one slot) or both scored (schedule), and an implementation that scores 0.7 alone fails | RC-12, RC-75 |
| T-07 | A1 | ledger edited inside the anchored prefix; truncated below the anchor; suffix rewritten after the anchor; ledger and JSONL restored to exactly the last anchor | first two detected; third reported as "unanchored window of n records", never as verified; the fourth reported as "continuous, unanchored window 0", and the test asserts that this report alone is not a pass condition for T-30 (a restore that lands on an anchor is continuous by construction, RC-74) | RC-13, RC-74 |
| T-17 | A1 / A3 | cluster membership addition and removal attempted immediately after registration, before the earliest `not_before`, between the first forecast receipt and t*_k, and after t*_k (RC-66); EventSpec naming a closed cluster; increment requested while one member is unresolved; λ recomputed after a partial resolution or after a member's `knowable_at` precedes its receipt; VOID declaration for a member received after that member's adjudicated `knowable_at` but before the registry received its outcome (10:00 publication, 10:10 VOID, 10:30 receipt; RC-57); cluster of members at the probability corners (0 and 1); fixture F-24: a cluster with one resolved member (X = +0.1) and one pre-declared VOID member, and a two-member all-VOID cluster (RC-67) | all mutations rejected at every stage and the refusals replayed; the 10:10 VOID is refused and the member is scored (a 09:55 VOID is accepted); no increment emitted until every member is resolved or pre-declared VOID; λ_k equals the value frozen at t*_k = min over resolved members of min(outcome receipt, adjudicated `knowable_at`); the emitted increment is the mean over resolved members and lies in [−1, 1], so 1 + λX̄ ≥ 0.5; F-24 emits +0.1 with worst-case bounds from the imputed sibling, and the all-VOID cluster emits nothing and counts two against the cap; replay reproduces the same closure order | RC-29, RC-41, RC-52, RC-57, RC-66, RC-67 |
| T-19 | A1 / A3 | VOID or merge request citing a dependence between two registered clusters: before any outcome, after one cluster's first outcome receipt, after an adjudicated `knowable_at` | refused in every case; both clusters' increments stay in the confirmatory process as registered; a declaration defect is logged and appears in the dependence audit with its calendar position; replay reproduces the refusal and the audit entry | RC-51 |
| T-18 | A1 | ledger history rewritten **and** the local anchor copy replaced consistently | detected against the external `AnchorStore` double; the local-only check reports "self-attested" and the restore test fails if only a local anchor is available | RC-34 |
| T-08 | A1 | clean checkout in CI, laptop and a container job | identical replayed state digest in all three | RC-20 |
| T-09 | A7 | commit message and PR body containing attribution trailers, session links, promotional footers; a commit whose author or committer identity is not on the designated list of `AGENTS.md` §7 | CI check fails; clean text passes; the identity case fails on metadata, which a text check cannot see (RC-81) | RC-26, RC-81 |
| T-10 | A3 | 120 clusters × 5 events, shared fair outcome per cluster, 20,000 replications, archived λ rule | cluster-level crossing rate exact 99 % upper bound ≤ 0.06 (0.055 % observed, bound 0.0011; REPRODUCED); per-event rate recorded and > 0.06 (invalid-null control) | RC-01, RC-48 |
| T-11 | A3 | same events in a random interleaved order, 20,000 replications | per-event rate still > 0.06; cluster-level rate within the 99 % bound | RC-01, RC-48 |
| T-12 | A3 / A6 | fixed-horizon paired cluster test (cluster-weighted statistic, block-sum variance, RC-69) over exactly 24 calendar periods with clusters per period varied (RC-70) on: valid null; clustered null; interleaved null; independent-period macro shock (q_t = 0.5 ± 0.3, F-22); time-varying skill with zero and with negative average (F-23); persistent two-state regime (P(stay) = 0.9); Poisson-varying supply with and without ± 0.3 period shocks and supply covarying with the shock (8 clusters in a +0.3 period, 2 in a −0.3 period; RC-69); the two-point period-shock null (every cluster in a block shares one outcome, block increment +0.903 or −0.897) and the rare-catastrophe two-point family (RC-72); the pending-cluster family (clusters eligible but unresolved at the cut-off, RC-68) | size within the A3 bound on the valid, clustered, interleaved, independent-shock, time-varying and Poisson-supply families (block-of-one-period: 4.8 % valid null, 5.1 % macro shock, 0.1 % time-varying; Poisson supply 5.2 % and 5.5 %; REPRODUCED); the cluster-iid variance on the macro-shock family exceeds the bound (13.4 %, invalid control); the equal-block-mean statistic on the covarying-supply family is reported beside the cluster-weighted one (5.7 % against 88 %: different hypotheses, RC-69); on the persistent regime the sizes for blocks of 1, 3 and 6 periods (27.1 %, 19.1 %, 14.8 %) are reported with no pass condition; the two-point families are reported with exact size (7.33 %; up to 15.2 %) and no pass condition, and the bounded betting test over block means is reported beside them (size 0.06 %, power 0.0 on the grid; RC-72); the pending-cluster family must show the pending clusters counted as missing under the cap and inside the worst-case bounds, never silently excluded (RC-68); the e-process crossing rate on every family is reported beside it (2.2 % independent macro shock, 28.9 % persistent regime, 62.8 % time-varying zero-average); power reported for both methods on the grid δ ∈ {0.005, 0.01, 0.02, 0.03} × {120, 288, 600, 1,200} clusters over 24 periods (independent clusters: 78 % at b = 0.5 and 92 % at b = 0.2 for the primary at δ = 0.01 and 600; under independent period shocks of ± 0.3 the primary's power at δ = 0.02 is 18 % at 600 and 18 % at 1,200 clusters, so the detectable effect under that model is about δ = 0.065 at any supply; REPRODUCED, `16` Appendix F); the two-look design (12 and 24 months, both confirmatory at nominal α) is retained as an invalid control and must exceed the bound (8.8 % observed, RC-56) | RC-01, RC-49, RC-50, RC-56, RC-61, RC-68, RC-69, RC-70, RC-72 |
| T-13 | A6 | (a) deterministic oracle: fixed vectors of component p-values or e-values, including exactly one component at the boundary; (b) least-favourable null: one comparator exactly null, all others at a strong alternative, 20,000 replications, α = 0.05 | (a) conjunction rejects iff every component rejects, bit-exact against the oracle; (b) exact one-sided 99 % binomial upper bound on the rejection rate ≤ 0.06 (a correct level-α test passes with probability ≥ 0.9999; a test of size 0.06 passes with probability ≈ 0.01, of size 0.07 never; REPRODUCED, `16` §2) | RC-08, RC-30 |
| T-14 | A6 | α-spending ledger with pre-registered sequence; fixtures: a test that fails to reject, a test cancelled after registration, a process killed mid-test, a test that rejects | α_j is debited at registration in every case and never refunded; cumulative spend never exceeds α_total; a promotion attempt after exhaustion is refused and logged; replay reproduces the debits | RC-08, RC-44 |
| T-15 | A6 | point-in-time store and as-of read interface (RC-79): (a) a revised value whose later vintage replaces an earlier one; (b) a publication-lagged join (observed before t_cut, available after); (c) a backfilled row inserted after t_cut with `observed_at` before it; (d) a post-cutoff timestamp; then the statistical second line: a feature containing the outcome injected into a synthetic challenger | every read with `available_at` > t_cut is refused at the interface, deterministically, in cases (a)–(d); the leak detector flags the injected-outcome inflation above the pre-registered bound as its positive control only, with the shuffled-label null distribution reported; blocked on OD9a | RC-09, RC-79 |
| T-16 | A6 | D1 generator rows (b ∈ {0.2, 0.5}, δ grid) plus clustered and missingness variants, for the fixed-horizon primary and for the monitor, over 24 periods with clusters per period varied (RC-70); the joint generator of the confirmatory conjunction (RC-83): six comparators sharing FULL's forecast and the outcome, each at the same δ (least-favourable configuration), with comparator error dependence set by the shared-sign probability ρ ∈ {0, 0.5, 1} | monitor counts reproduce D1 within Monte Carlo error; primary power reproduces `16` Appendix F within Monte Carlo error (δ = 0.01 at 600 independent clusters over 24 periods: 78 % at b = 0.5, 92 % at b = 0.2); IUT power reproduces `16` Appendix H within Monte Carlo error (δ = 0.01, 600 clusters: 21 % at ρ = 0, 32 % at ρ = 0.5, 77 % at ρ = 1, where the single comparison has 77 %; at 1,200 clusters 77 % / 80 % / 96 %; δ = 0.02 at 600 clusters: 76 % / 80 % / 96 %); the IUT's rejection rate at the least-favourable null (one comparator exactly null, the others at δ = 0.08) is within the A3 bound (0 of 20,000); detectable effect stated at 300 and 600 units for each kernel and for the conjunction at each ρ; the protocol report states the issuance window, evidence cutoff and comparator-dependence assumption it was powered under (RC-76, RC-83) | RC-24, RC-61, RC-70, RC-83 |
| T-20 | A4 | (a) property domain: cohort (s, n) with reference-class prior, model estimate outside the cohort range; (b) deterministic oracle with fixture parameters prior Beta(2, 18), model weight w(n) = n₀/(n₀ + n), n₀ = 20: (s, n) = (5, 20) → posterior Beta(7, 33); (0, 50) → Beta(2, 68); (0, 0) → the prior; model estimates 0.001 and 0.5 | (a) output monotone in s, within [0, 1], ordered low ≤ point ≤ high; no floor applied; no rounding; (b) posterior mean, 5 % and 95 % quantiles equal 0.175 / 0.0874 / 0.2812, 0.028571 / 0.005174 / 0.066914 and 0.1 / 0.019033 / 0.226374 to 1e-6; shrunk point for p_model = 0.001 at (5, 20) equals 0.014362, at (0, 0) equals 0.001 (w = 1, no cohort), and for p_model = 0.5 at (5, 20) equals 0.315334 (REPRODUCED, `16` Appendix D); (c) interval oracle (RC-58): model (low, point, high) = (0.0005, 0.001, 0.002) at (5, 20) → (0.006874, 0.014362, 0.027239); (0.3, 0.5, 0.7) at (5, 20) → (0.168465, 0.315334, 0.488622); (0.0005, 0.001, 0.002) at (0, 0) → unchanged; the collapsed interval (0.001, 0.001, 0.001) at (5, 20) → (0.009696, 0.014362, 0.019407); low = 0 at (5, 20) → low′ = 0.000309 (clip before the logit); (0.0005, 0.001, 0.002) at (0, 50) → (0.002657, 0.011072, 0.025155), all to 1e-6 (REPRODUCED, `16` Appendix E); an implementation returning s/n (0.25 at (5, 20)), collapsing low = point = high, returning [0, 1], or returning the raw posterior quantiles as bounds (0.0874 > the required point 0.014362) fails; the fixture parameters are test values, not the pre-registered production prior and weight (Phase 2 contract) | RC-03, RC-54, RC-58 |
| T-21 | A4 | nested chain with declared conditionals | arithmetic identity P(E) = P(E\|D)P(D\|C)P(C) holds to numerical tolerance in the kernel; no LP in Phase 1 (the linear-constraint form moves to §7 with T-25) | RC-04, RC-32 |
| T-22 | A4 | interval-only forecast; point outside its interval | both rejected by the scorer and the schema | RC-05 |
| T-23 | A4 | orthogonal-error fixture (sd 0.02 / 0.30 / 0.30); constant-bias fixture | second-moment pool ≈ (0.991, 0.004, 0.004) and down-weights the biased model; equal weights returned when the flag is off | RC-06 |
| T-24 | A4 | identical varying histories; constant duplicate histories | n_eff = 1.25 reported with a "degenerate history" flag on the constant case; n_eff appears in no decision path | RC-07 |
| T-26 | A4 | NaN, reversed, > 1, missing provider, duplicate provider | rejected with typed reasons; no equal-weight fallback on invalid input | RC-15 |
| T-28 | A4 | fused forecast with two providers or no Jev record | issuance held; no two-of-three fallback | RC-17 |
| T-29 | A2 | EventSpec without `predicate_kind`; EventSpec without `cluster_id` (a singleton must be declared as a one-member cluster; no implicit default) | both rejected | RC-19, RC-01, RC-53 |
| T-30 | A5 | valid capability replayed after demotion; after expiry; with a stale epoch; with a consumed nonce; the same valid capability presented by two processes at once; a protected action acknowledged, then ledger and JSONL restored to the previous anchor and the same capability presented (RC-74); the anchor store made unavailable during a protected action | all rejected; exactly one of the concurrent presentations acts and the other fails inside the writer transaction; demotion state read back after restart; the restore case is refused (consumed nonce in the anchored prefix, or stale epoch after the rotation on start); with the anchor store unavailable the operation fails closed and acknowledges nothing | RC-12, RC-43, RC-74 |
| T-31 | A5 | capability signed with a non-owner key; then, under an otherwise valid owner signature, each of the seven signed fields mutated individually: capability (action), environment, release digest, evidence digest, epoch, nonce, expiry; canonical-serialisation cases: the same tuple serialised with a different key order or whitespace, a record with an added field, a numeric field re-typed as a string | every mutated record rejected (a verifier that signs only environment and release digest accepts the other five mutations; REPRODUCED, `16` Appendix E); the re-serialised identical tuple verifies; the added-field and re-typed records fail | RC-12, RC-62 |
| T-32 | A5 | elevated state object fabricated from research code through the non-public constructor, through reflection and through a dynamic import, then presented to a protected operation | the operation rejects it because no valid signed capability accompanies it; the static import check reports the import but is not the pass condition | RC-12, RC-46 |
| T-33 | A5 | capability set with `SHADOW_LIVE_QUOTES` only | SIM execution denied; reconciliation and authorised cancellation allowed during halt | RC-14 |
| T-34 | A4 / A5 | synthetic secret canary in nested exceptions raised inside and outside `except` blocks, structured errors, encoded (base64, URL) forms; the secret held in a plain local of the raising frame; held only in a holder with a redacting `repr`; held only in a frame that has returned before any exception escapes, with (i) a typed outcome value and (ii) the exception object itself passed upward; in Phase 1 the source exception is synthetic (no HTTP) | canary absent from logs, error payloads and every exception reachable through `__context__`, `__cause__` and traceback frame locals, where the probe traverses **object state** (attributes, slots, containers, closures, exception `args`), not `repr`; passes only when translation happens outside the active handler **and** the secret is held only in frames that have returned before any exception escapes **and** the outcome passed upward is a typed value, never the exception object; the plain-local variant fails (RC-55), the redacting-holder variant fails because the object-state probe finds the raw secret in its attribute (RC-60), and variant (ii) fails; REPRODUCED, `16` Appendix D and E | RC-15, RC-47, RC-55, RC-60 |
| T-35 | A5 | host clock rolled back after an unused capability expired; clock rolled back below the persisted high-water mark during an admission; admission at t₀, an expired capability rejected at t₂ > t₁, rollback to t₀ < t < t₁, the same capability presented (RC-65); idle window: admission at 10, expiry 20, no check until a rollback to 15 with the monotonic clock advanced (RC-73); reboot: monotonic clock reset and new boot id (RC-73) | capability rejected (expiry evaluated against the high-water mark); admission fails closed and is logged; high-water mark survives restart; the RC-65 sequence is refused as a rollback because the rejected check persisted its time; the idle-window and reboot cases are refused as clock discontinuities with re-authorisation required (the receipt-time watermark and the every-check watermark both admit them; REPRODUCED, `16` Appendix F and G) | RC-37, RC-65, RC-73 |
| T-36 | A3 / A6 | positive controls for each kernel: (a) e-process oracle, twelve constant increments of +0.2 under the archived rule; forty constant increments; the fixed 12-vector (+0.2, −0.2, +0.2, +0.2, −0.2, +0.2, +0.2, +0.2, −0.2, +0.2, +0.2, +0.2); (b) fixed-horizon oracles: block means (0.05, 0.10, 0.00, 0.05); unequal blocks (0.10, 0.00), (0.05, 0.15, 0.10), (0.00, 0.05, 0.05, 0.10), (0.20) (RC-69); two-point oracle, 24 blocks of ± 0.9 with k positive (RC-72); (c) pre-specified alternative b = 0.5, δ = 0.08, 120 independent clusters (D1 generator, five per period), 20,000 replications | (a) e = 1.1¹⁰ = 2.593742 after twelve (λ = 0.5 from the third increment because the sample variance is zero), first crossing of 20 at increment 34 with e = 21.113777, e = 1.447854 for the 12-vector, all to 1e-6; (b) t = 2.449490 on 3 df, one-sided p = 0.045861, rejects at α = 0.05; unequal blocks: θ̂ = 0.08, t = 3.651484 on 3 df, one-sided p = 0.017728, while the equal-block-mean statistic gives 0.10 and t = 2.828427, so an implementation of the wrong statistic fails (REPRODUCED, `16` Appendix F); two-point oracle: k = 16 rejects and k = 15 does not (statistic 1.714 against t₀.₉₅,₂₃ = 1.7139; REPRODUCED, `16` Appendix G); (c) exact one-sided 99 % lower binomial bound on the rejection rate ≥ 0.90 for the primary (true rate 0.964) and ≥ 0.60 for the monitor (true 0.711): a correct kernel passes with probability 1.000000 to six places, a kernel that never rejects fails (REPRODUCED, `16` Appendix E) | RC-63, RC-69, RC-72 |
| T-37 | A1 / A6 | candidate log (RC-78): registration of an event with no prior candidate entry; a candidate entry written after a forecast on the same event exists; a full synthetic candidate stream with registered, rejected and sampled-out decisions | the first two refused; the log replays byte for byte; the protocol report's candidate, registered and rejected counts by reason equal the log's | RC-78 |
| T-40 | A7 | Lean job with a deliberately false lemma; job run with the Mathlib cache unreachable | false lemma fails; cache failure reported as "not verified" and the job is red | `04-formal-verification.md` |
| T-41 | A7 | `research/original/` manifest and Git tree object | `sha256sum -c MANIFEST.sha256` reports 71 OK; `git rev-parse HEAD:research/original/CPE_Forschungspaket_2026-10-16` equals `122a1619cdad4f1c7f577e26f86709c34ce86298` (the value at the reviewed head `8b2dba7`, unchanged at `10d1581` and at this commit; the tree object also detects added or renamed files, which the manifest does not) | integrity, RC-40 |

### 5.1 Mandatory counterexample fixtures (restated, RC-35)

Each fixture is reproduced against the archived v0.2 reference code by `16` Appendix A (REPRODUCED) or by
`15-codex-review.md` Appendix 1 (REPRODUCED by Codex). The Phase 1 implementation must reject or correctly
grade every fixture whose component it builds; the fixture, not the review document, is the acceptance
input. F-11 belongs to the order-payload builder (Phase 7) and the HTTP source of F-12 to the first network
principal (Phase 3); both stay listed so that the later phase inherits them (RC-42).

| Fixture | Input (synthetic) | Reference-code behaviour | Required Phase 1 behaviour | Test |
|---|---|---|---|---|
| F-01 backdating | event and forecast dated 2020-01-01, submitted today | accepted | rejected; receipt time is the server clock | T-01 |
| F-02 late YES | F-02a: outcome YES with occurrence time 10 days after `expires_at`; F-02b: outcome YES resolved 10 days after `expires_at` with **no** occurrence time and no evidence of lateness | `resolved_yes` (both) | F-02a: `EXPIRED_NO`; F-02b: VOID under the source's pre-registered occurrence-time rule, counted against the cap (RC-71; until round 7 this fixture forced `EXPIRED_NO`, a one-directional error that biases the paired difference) | T-03, T-04 |
| F-03 early NO | NO resolved 2 days into a 30-day eventually-by-deadline predicate | `resolved_no` | rejected (not logically final) | T-04 |
| F-04 non-hex digest | 64-character reasoning digest `'z' × 64` | accepted | rejected (hex, fixed length) | T-26 |
| F-05 phantom | `append` raises during `register_event` | event remains in memory | no state change, no acknowledgement | T-05 |
| F-06 no replay | new registry on an existing ledger | zero events known | state derived by replay equals online state | T-05, T-06 |
| F-07 suffix rehash | last record edited and `entry_hash` recomputed after the anchor | verifies | reported as unanchored window; never "verified" | T-07 |
| F-08 anchor and ledger replaced together | history rewritten and local anchor copy regenerated | (no external anchor exists) | detected against the external anchor store | T-18 |
| F-09 gate replay | valid promotion record re-used after demotion; caller supplies the signing key | promoted again | rejected (consumed nonce, stale epoch); key never caller-supplied | T-30, T-31 |
| F-10 direct construction | `Gate(SIM_EXECUTION)` built in-process (probe P5) | passes precheck | no public constructor for elevated state; static check | T-32 |
| F-11 payload bypass (Phase 7) | hand-built `Cfd` payload, amount −1; NaN price; 11 units at lot size 10 | reaches transport / accepted | not constructible; rejected before any transport object | T-27 (§7) |
| F-12 error context | `raise … from None` after an HTTP error with a synthetic bearer header (Phase 1: synthetic source exception; HTTP source in Phase 3) | header present in `__context__` | canary absent from the whole reachable exception graph, logs and structured errors, probed by object state; translation outside the handler, secret confined to returned frames, typed outcome passed upward (RC-60) | T-34 |
| F-13 fusion inputs | NaN, reversed [0.8, 0.2], [1.2, 1.3] intervals | `forecast` | rejected with typed reasons | T-26 |
| F-14 n_eff | three constant identical histories; three identical varying histories | 3.0; 1.25 | "degenerate history" flag; 1.25 reported as diagnostic only | T-24 |
| F-15 cloned outcomes | 30 pairs (0.25 vs 0.75) sharing one fair outcome | e = 475.0986 or 1.0; crossing probability 0.5 | one cluster, one increment; crossing probability within the A3 bound | T-10 |
| F-16 clustered null | 120 clusters × 5 events, shared fair outcome, archived λ rule, 2,000 replications | 33.4 % per-event crossings; 13.5 % interleaved | per-cluster crossing rate with exact upper bound ≤ 0.06; per-event rate recorded as the invalid-null control | T-10, T-11 |
| F-17 correlation weights (probe P4) | orthogonal errors, sd 0.02 / 0.30 / 0.30 | weights 1/3 each | equal weights by default; second-moment pool ≈ (0.991, 0.004, 0.004) behind the flag | T-23 |
| F-18 constant bias | model 1 biased by 0.20, models 2–3 unbiased sd 0.05 | covariance-only weight 0.935 on the biased model | second-moment pool weight ≈ 0.036 on it | T-23 |
| F-19 predicate lint (probe P3) | predicate text "potentially excellent" | passes the word list | rejected by the typed predicate grammar | T-29 |
| F-20 floor inversion | interval [0.001, 0.01] with base rate 0.02 | [0.02, 0.01] | no floor; shrinkage output ordered low ≤ point ≤ high | T-20 |
| F-21 publication gap (round 3) | outcome published 10:00, forecast received 10:05, registry receives the outcome 10:30 | (receipt-only cutoff admits it) | excluded from the increment at adjudication; a 09:55 forecast is eligible | T-02 |
| F-21b expiry gap (round 7) | eventually-by-deadline predicate, deadline 100, latency window 10, source's formal NO record received at 118, forecast received at 113 | (receipt-only and publication-only cutoffs admit it) | `knowable_at` = 110 by logical finality; forecast excluded (RC-77) | T-02, T-04 |
| F-22 macro shock (round 3) | 24 periods × 5 clusters, q_t = 0.5 ± 0.3 per period (independent), and a two-state regime with P(stay) = 0.9; marginal E[X] = 0 | (no cluster or period structure in the reference code) | fixed-horizon test with calendar-block variance within the A3 bound on the independent family; sizes reported for the persistent family; e-process rate reported (2.2 % and 28.9 %) | T-12 |
| F-23 time-varying skill (round 3) | E[X_k] = +0.12 for the first 60 clusters, −0.12 for the next 60 (average zero); +0.12 for 40 then −0.08 for 80 (average −0.013) | (not applicable) | fixed-horizon test within the bound (0.1 %, 0.08 %); e-process crossing rate reported (62.8 %, 3.6 %) and labelled as evidence against the conditional null only | T-12 |
| F-24 partial VOID (round 7) | cluster A: one resolved member with X = +0.1 and one pre-declared VOID member; cluster B: two pre-declared VOID members | (not applicable) | A emits +0.1 (mean over resolved members) with worst-case bounds from the imputed sibling; B emits nothing and counts two against the VOID cap (RC-67) | T-17, T-12 |

## 6. Phase 2 statistical contract (draft, to be frozen only after OD3–OD5)

| Field | Draft value | Decision needed |
|---|---|---|
| Estimand | difference in expected Brier between FULL and Design C per outcome cluster, averaged over the pre-registered eligible-event population **that resolves to YES or NO**, using only forecasts received before the cluster's outcome-knowable time t*_k (RC-52), inside the event's pre-registered issuance window and built on evidence with `available_at` ≤ its evidence cutoff (RC-76); **each event pre-registers one issuance window [t_open, t_close] and one evidence cutoff t_cut ≤ t_close for every arm**, so that the paired difference measures model design and not information timing; the first registration of the primary cohort and of its burn-in is at or after the date on which every arm of the IUT comparator set is operational and frozen (Phase 4 of `12`; Phase 2 registrations are a Design C track record and candidate log, exploratory); the VOID rate is a reported co-primary quantity with a pre-registered cap above which the primary estimate is declared uninterpretable (RC-38); the point estimate is the mean over clusters (RC-69) | cap value and estimand naming (per cluster or period-balanced): OD4 |
| Eligible-event population | a pre-registered inclusion predicate (source family, predicate kind, horizon range, sector list, Jev triage result) and a sampling rule (every eligible candidate is registered, or a seeded random subsample with its inclusion probability recorded); every candidate considered is logged with id, source, time, decision and reason **before** any forecast on it exists; the log is part of the ledger and the replay (T-37), and the protocol report states candidate, registered and rejected counts by reason (RC-78; the requirement of `02` §5 item 2 that `17` never carried) | predicate content: OD5 |
| Accrual and maturation | accrual cut-off = 24 months − H_max, where H_max is the maximum declared horizon including the source's declared latency window; a cluster is eligible for the primary only if every member's `expires_at` plus latency window is at or before the 24-month cut-off; clusters eligible but still pending at the cut-off (possible only through source latency) are counted as missing under the VOID cap and enter the worst-case bounds; registrations after the accrual cut-off feed the monitor and the next cohort, never this primary (RC-68: silent exclusion of unmatured clusters is an outcome-correlated selection of the analysed population) | H_max and the cut-off: OD4 |
| Sampling unit | pre-declared outcome cluster | none |
| Primary test | fixed-horizon paired comparison of cluster increments at **one** cut-off, 24 months after first cohort entry, one-sided α = 0.05; **statistic:** point estimate = mean over clusters, variance = block-sum (cluster-robust) form over pre-registered calendar blocks on G − 1 df (RC-69), block length justified from reference-class history, never from registered outcomes (RC-49, RC-50); **validity:** the size is calibrated on the pre-registered null families of T-12 and is not finite-sample valid for every bounded-mean null; the contract pre-registers a cap d_max on \|p_FULL − p_baseline\| for forecasts entering the primary and a reference-class bound on the share of catastrophe periods (the skew bound), and reports the two-point families with their exact size; no finite-sample-valid test of any form can replace it at this horizon (power ≤ α(1 + δ)^24; PROVED, RC-72, RC-80); the 12-month look is an interim for futility and integrity only and can never confirm (two confirmatory looks at nominal α inflate the type-I error to 8.0 % in normal theory and 8.8 % on the block test; a non-binding futility look leaves it at 5.1 %; REPRODUCED, RC-56) | block length, dependence model, d_max and the catastrophe-share bound: OD4 |
| Distribution-free check | the archived bounded betting test (GRAPA, λ_max = 0.5) run over the calendar-block means and evaluated at the horizon, reported beside the primary with its size (0.06 % on the two-point null) and its power (0.0 at every useful effect over 24 blocks; at most α(1 + δ)^24 for any such test); it is a check on the skew assumption, never a replacement for the primary (RC-72, RC-80) | none |
| Interim look (optional) | if early confirmation is wanted, a pre-registered Lan–DeMets O'Brien–Fleming-type spending over the two looks: 0.0056 at 12 months and a nominal 0.0483 at 24 months (total 0.050 in normal theory; 5.3 % and 5.1 % on the block test through its own degrees of freedom, to be calibrated by simulation in T-12 because the first look has few blocks; REPRODUCED, RC-56) | whether to adopt it: OD4 |
| Anytime-valid monitor | cluster-level committed e-process, α = 0.05, λ_max = 0.5, running maximum, of the sequential conditional null E[X_k \| F_(k−1)] ≤ 0; reported continuously with that label; a crossing triggers an integrity and dependence review, never a confirmatory claim or a promotion (it crosses in 62.8 % of paths under time-varying skill with zero average effect; REPRODUCED) | none |
| Smallest useful effect | to be set **for the confirmatory conjunction**, not for one paired comparison (RC-83). Single comparison, over the design's 24 periods (RC-70): power of the primary at 600 independent clusters is 78 % (b = 0.5) to 92 % (b = 0.2) for δ = 0.01, and 54–70 % for δ = 0.005; at 288–300 clusters about 76–94 % for δ = 0.02. Conjunction (six comparators sharing FULL's forecast and the outcome, each at δ, REPRODUCED `16` Appendix H): at δ = 0.01 and 600 clusters the IUT rejects in 21 % when comparator errors are uncorrelated, 32 % at a shared-sign probability of one half and 77 % when they move together; at 1,200 clusters 77 % / 80 % / 96 %; at δ = 0.02 and 600 clusters 76 % / 80 % / 96 %. Under independent period shocks of ± 0.3 over 24 periods the single comparison's power at δ = 0.02 is 18 % at 600 and at 1,200 clusters: the detectable effect under that model is about δ = 0.065 at any supply, so the dependence model and its amplitude, not the cluster count, set it (RC-70; the 47 % figure stated here until round 7 averaged over 120 periods and is withdrawn) | δ, the comparator-dependence assumption the design is powered under, and the shock amplitude: OD4 |
| Planned supply | measured on a **blinded burn-in cohort** in Phase 2 months 1–3: events are registered and forecasts committed, but no outcome of a burn-in event is unsealed before the contract is frozen, and burn-in clusters are permanently excluded from the primary test (RC-39); only counts, cluster sizes and source metadata inform OD4–OD5 | OD5 |
| Confirmatory conjunction | IUT over {Design C, each single provider, single-provider-three-roles, equal-weight committee}; each component at α, no multiplicity correction (RC-08); its power is the least-favourable-configuration power of T-16, which lies between the product of the marginal powers and the smallest marginal power depending on comparator error dependence (RC-83); the supply that makes the conjunction detect δ at 80 % is up to twice the single-comparison supply when comparator errors are uncorrelated (REPRODUCED, `16` Appendix H) | dependence assumption: OD4 |
| Missing data | VOID excluded from the primary (estimand above) and counted against the cap; sensitivity = worst-case bounds in both directions, imputing each VOID with the outcome least favourable to FULL (Y = 1 where p_FULL < p_baseline, else Y = 0) and then most favourable, reported as an interval around the primary (a single imputation such as "VOID as NO" is not conservative: with p_FULL = 0.1 and p_baseline = 0.9 it adds +0.8 to the paired increment, Y = 1 gives −0.8; REPRODUCED, `16` §2); a pre-registered missingness model only if the VOID mechanism is documented per source; abstentions scored at the baseline forecast and reported separately (RC-38) | none |
| Stopping rule | fixed horizon for the primary at the single 24-month cut-off (RC-56) with the accrual cut-off and H_max above (RC-68); the 12-month interim and the monitor may trigger an early futility or integrity review, never early confirmation; futility declared if the detectable effect **of the conjunction** at measured supply **under the pre-registered dependence model** exceeds OD4 (under a persistent macro regime, 120 clusters over 24 months admit no valid test at any tested block length; under ± 0.3 independent period shocks no supply detects δ < 0.065; REPRODUCED) | OD4 |
| Promotion budget | α-spending sequence per RC-08 | OD3 |

## 7. Tests specified now and built in later phases

**Credal LP (Phase 5, RC-10, RC-32).** T-25: small exact credal instance; the inner LP over the whole declared
credal set returns a worst case ≤ any sampled-subset worst case; conditional bounds enter as linear constraints
l·P(A) ≤ P(A ∩ B) ≤ u·P(A) with declared zero-mass semantics. Not part of Phase 1 (§3, out of scope).

**Allocation certificates (Phase 5, RC-82).** T-38: malformed, truncated, re-signed and stale allocation certificates presented to the certificate verifier of `12` Phase 5 are rejected; moved here from A7 in round 7 because Phase 1 contains no certificate verifier and A7 could never have been satisfied as written.

**Order payload boundary (Phase 7, RC-15, RC-42).** T-27: hand-built payload bypassing the typed builder, NaN
price, non-multiple lot (fixture F-11); not constructible or rejected before any transport object exists. The
typed-builder principle applies in Phase 1 only to the research schemas (T-26, T-29).

**Evaluator side channels (Phase 6).** Exfiltration canaries in evaluator-only data; logs, crash dumps,
telemetry and parser errors scanned for canaries; bounded feedback (pass/fail plus coarse diagnostics); cap on
adaptive proposals per period; evaluator and scorer are separate processes so a submitted artefact never
receives labels; no executable deserialisation or template evaluation of artefacts.

## 8. Size and review

One Python package, no services, no message queue, no cloud SDKs, SQLite plus JSONL, a few thousand lines
including tests. Independent review of the Phase 1 code by Codex (author: Claude) or by Claude (author:
Codex), per `AGENTS.md` §9; owner acceptance of A8. Nothing in Phase 1 is architecture that Phase 2 would
have to remove under any hosting choice (OD6).
