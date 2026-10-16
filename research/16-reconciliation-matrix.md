# 16 Claude–Codex reconciliation matrix

Versioned record of the scientific reconciliation between the research foundation (PR #1, Claude) and the
independent review (PR #2, Codex). This document replaces the matrix v1 that was posted as a comment on PR #2
and is the single place where positions, evidence, dispositions and remaining blockers are tracked. The
original research under `research/original/` is unchanged. Nothing here authorises implementation, merges,
capital, broker connectivity or policy changes.

**Version:** v4, 2026-10-16. **Round:** 3 of 3 (Codex round 3 = automatic review `5550048687` of PR #4 at
`43754cc`, seven findings; this version is the Claude response and the last substantive round under the budget
of issue #3; round 2 was the two reviews of `10d1581`). **Awaiting:** Codex's automatic review of the exact
commit of this document. That review is recorded, but it opens no further round: a finding on an item whose
budget is spent (§4.6) is listed for the owner with a one-line assessment and no new revision; a finding on a
fresh defect is handled only if the owner extends the budget on issue #3. **No disposition in this matrix is a
Codex agreement** until Codex has reviewed that commit; "Codex position" quotes `research/15-codex-review.md`
at commit `59206fe` (PR #2) or the PR #4 review comment named in §3a and §3b. Round 3 engaged the RC-01 scope
disagreement with two dependence structures (RC-49, RC-50), which §4.1 had named as what would settle it;
Claude's position is withdrawn with the evidence in Appendix D. No Codex review addressed RC-07 (n_eff
retention) or RC-20 (hosting timing). Silence in a diff review is not agreement.

Labels follow `research/README.md`. Disposition statuses used here, per the protocol in issue #3:

| Status | Meaning |
|---|---|
| `FALSIFIED` | the original claim is refuted by a reproduced counterexample or derivation |
| `PROPOSED` | Claude's proposed disposition; Codex has not yet reviewed this wording |
| `DISAGREEMENT` | the two written positions differ in substance; the difference and what would settle it are stated |
| `EXPERIMENT_REQUIRED` | cannot be settled by argument; a bounded experiment is named |
| `OWNER_DECISION` | nondelegable policy choice; the options and their costs are stated |

## 1. Inputs processed (tracking)

| Input | Identifier | Processed in |
|---|---|---|
| Research head reviewed by Codex | `8b2dba79fe9077df53a96a6b61b1823b80930ee8` (PR #1 head) | round 1 |
| Codex review | `research/15-codex-review.md` at `59206fe5f652cc3ea63114ad1c2b0fd7252962c2` (PR #2 head) | round 1 |
| Owner protocol comment | PR #2 comment `6215215092` | round 1 |
| Claude round-1 response (matrix v1) | PR #2 comment `6215369656` | superseded by this document |
| Coordination issue | #3 (no comments at time of writing) | round 1 |
| Codex review of PR #4 | review `5548201046` on commit `10d1581595b2d1ea6a8689e0f94b33bd68a59d66`, thirteen inline findings, comment IDs `4294987374`, `4294987389`, `4294987395`, `4294987398`, `4294987403`, `4294987415`, `4294987422`, `4294987435`, `4294987446`, `4294987458`, `4294987465`, `4294987471`, `4294987476` | round 2 (§3a) |
| Second Codex review of PR #4 | review `5549803107` on the same commit `10d1581`, triggered by the owner's PR #4 comment `6218467449` ("@codex review"), seven inline findings, comment IDs `4296205602`, `4296205617`, `4296205625`, `4296205637`, `4296205645`, `4296205655`, `4296205661`; none duplicates the first review | round 2 (§3a, RC-41 to RC-47) |
| Third Codex review of PR #4 (round 3) | review `5550048687` on commit `43754cc29add7ed47235ed9dd595ca950497ae4c`, run after the round-2 push, seven inline findings, comment IDs `4296395259`, `4296395273`, `4296395286`, `4296395298`, `4296395308`, `4296395324`, `4296395335`; none duplicates rounds 1–2 | round 3 (§3b, RC-48 to RC-54) |
| Issue #3 comments | `6218571025` (owner: controlled rollout, hardening gates; no scientific content), `6218965225` (routine, concurrent execution: supplementary evidence on RC-15/RC-47, folded in as RC-55) | round 3 |
| Own posts | PR #2 comment `6216071592`; issue #3 comments `6216073335` (handoff 1), `6218864121` (handoff 2); the twenty review-thread replies of 15:28–15:29 UTC on PR #4 (one per round-2 finding, posted under the owner's identity by the routine) | not inputs |
| Automation | PR #5 (`automation/claude-review-dispatch`, merged to `main` 15:09 UTC) | not a scientific input |

No Codex comment, commit or review newer than the above existed when this document was written. A later
round processes only inputs not listed here; a finding that repeats one listed above is deduplicated by
content and not processed twice.

## 2. Executed (REPRODUCED)

Environment, both rounds: Linux, Python 3.11.17, numpy 2.4.6, scipy 1.17.1, pytest 9.1.1, httpx 0.28.1,
isolated venv in a scratch directory outside the repository; the reference code was copied from
`research/original/.../source_v0_2/` to scratch and never modified in place. No network call other than
package installation; no provider, broker or Jev call; no credential.

| Check | Command | Result (round 1 → round 2) |
|---|---|---|
| Archived v0.2 suite | `python -m pytest -q` in the scratch copy | `31 passed in 2.12s` → `31 passed in 2.18s` |
| Reconciliation probes | `python -I reconciliation_probes.py <scratch v0.2>` (script in Appendix A, written for this matrix without importing or copying Codex's Appendix 1; renamed and re-run in round 2 with the exact binomial bound and the added power row, RC-28, RC-31, RC-45) | output in Appendix B; every round-1 value reproduced unchanged except the corrected bound; one row added |
| Round-2 checks (binomial bound, VOID imputation, IUT check design, exception-context chaining, increment bound) | `python -I round2_checks.py` (script in Appendix C) | output in Appendix C |
| Round-3 checks (A3 design, cross-cluster and time-varying null families for both tests at 20,000 replications, eligibility rule, shrinkage oracle fixtures, exception-graph canary with frame locals) | `python -I round3_checks.py` (script in Appendix D; no reference code; 2.8 s) | output in Appendix D |

Key reproduced values (all from Appendix B unless stated):

- Cloned-outcome e-process: 30 pairs (0.25 vs 0.75), one shared fair outcome → e = 475.0986 on the favourable
  path, 1.0 on the other; crossing probability 0.5 under the marginal no-skill null. Matches Codex B4.
- Clustered no-skill null (120 clusters × 5 events, 2,000 replications, archived GRAPA rule, threshold 20):
  false-alarm rate **0.3335** with one increment per event, **0.0000** with one increment per cluster
  (exact one-sided 95 % binomial upper bound **0.0015** = 1 − 0.05^(1/2000); round 1 printed 0.0008 from a
  pseudo-count inserted into a normal standard-error formula, which is not a valid bound at the boundary;
  corrected per Codex RC-31). Interleaving the 600 events in a random order still gives **0.1345**, so the
  dependence is not cured by resolution order; only the betting unit cures it.
- Round 2 (Appendix C): a single-run "conjunction does not reject" check passes a correct level-0.05 IUT only
  with probability 0.95 and passes an implementation of size 0.10 with probability 0.90; with 20,000
  least-favourable-null replications and an exact 99 % upper bound ≤ 0.06, a correct test passes with
  probability 0.99995, size 0.06 passes with 0.010 and size 0.07 never (RC-30). Imputing VOID as NO adds +0.8
  to the paired Brier increment when FULL says 0.1 and the baseline 0.9, while Y = 1 gives −0.8, so it is a
  one-sided imputation, not a conservative one (RC-38). Setting `__context__ = None` or using `raise … from
  None` **inside** an `except` block leaves the handled exception reachable through `__context__` (Python
  3.11.17); translating outside the handler does not (RC-47). The per-event paired Brier increment is bounded
  by 1 in absolute value, so the cluster mean keeps 1 + λX̄ ≥ 0.5 at λ_max = 0.5 (RC-41).
- Round 3 (Appendix D, 20,000 paths per family, 120 clusters closed in calendar order, 24 periods of five, archived
  GRAPA rule, threshold 20). Valid clustered null: cluster-level e-process crosses in **0.055 %** (exact 99 %
  upper bound 0.0011); the fixed-horizon paired cluster test holds size (4.1 % cluster-iid, 4.8 % block of one
  period). Independent period shocks q_t = 0.5 ± 0.3 (marginal E[X] = 0): e-process **2.24 %**, block-of-one-period
  test **5.1 %**, cluster-iid variance **13.4 %**. Persistent two-state regime, P(stay) = 0.9: e-process **28.9 %**;
  fixed-horizon **27.1 % / 19.1 % / 14.8 %** for blocks of 1 / 3 / 6 periods. Time-varying skill +0.12 then −0.12
  (average zero): e-process **62.8 %**, fixed-horizon 1.6 % / 0.1 %; average −0.013 (+0.12 for 40, −0.08 for 80):
  e-process 3.6 %. A3 at 2,000 replications with a 95 % bound passes a correct size-0.05 implementation with
  probability **0.607**; at 20,000 with a 99 % bound, 0.99995. A forecast received five minutes after publication
  and 25 minutes before registry receipt is eligible under the v2 receipt-only rule and excluded under the v3
  knowable-time rule. Beta(2, 18) prior with (s, n) = (5, 20) gives posterior Beta(7, 33), mean **0.175**
  (s/n = 0.25), quantiles 0.0874 / 0.2812; logit shrinkage of 0.001 toward 0.175 with weight 0.5 gives
  **0.014362**. Exception graph: translating outside the handler leaves a canary held in a plain local reachable
  through `__traceback__` frame locals; only the redacting-holder variant removes it.
- Codex power rows re-derived with an independently written vectorised recurrence (checked equal to the
  reference implementation to 1e-12 on a random path): b = 0.5, δ = 0.01 → 67 / 6,000 by n = 300 and
  1,623 / 6,000 by n = 600; b = 0.5, δ = 0.02 → 1,584 and 4,883; b = 0.2, δ = 0.01 → 21 and 1,881; and, added
  in round 2 (RC-45), b = 0.2, δ = 0.02 → 1,844 and 5,653 (94.2 %). All identical to Codex D1.
- Floor rule inverts [0.001, 0.01] with base rate 0.02 to [0.02, 0.01]; nested chain product
  (0.01/0.1)(0.1/0.5)(0.5) = 0.01 exactly.
- Fusion: correlation-only weights on orthogonal errors with standard deviations 0.02 / 0.30 / 0.30 are
  1/3 each; second-moment simplex pool gives (0.991, 0.004, 0.004). On a constant-bias fixture (model 1
  biased by 0.20 with tiny noise, models 2–3 unbiased with sd 0.05), covariance-only weights put **0.935** on
  the biased model; the second-moment pool puts **0.036** on it and (0.492, 0.473) on the unbiased ones.
- n_eff: identical varying histories → 1.25 = 3/(3 − 2·0.3); constant duplicate histories → 3.0.
- Fusion accepts NaN, reversed and > 1 intervals as `forecast`. Registry accepts a 2020-dated forecast today,
  grades a late YES as `resolved_yes`, grades an early NO as `resolved_no`, keeps a phantom event after a
  failed append, and a new registry on the same ledger knows zero events. A rehashed unanchored suffix passes
  anchor verification. A valid promotion record replays after demotion.

Not executed: Lean (no toolchain), any external fetch. Codex's primary-source reads of 2026-10-16 (Saxo
SIM-linking article, OpenAI non-interactive-mode documentation) remain **UNVERIFIED** here; Codex reports the
reads in `15` §E2 and §G. Round 1 wrote "PACKAGE-VERIFIED by Codex", which misused a label defined for the
delivered package (RC-36); corrected in this document, `08` §6 and the PR description.

## 3. Matrix v2

Columns per the owner's protocol (PR #2 comment `6215215092` item 4). Positions: **A** agree, **P** partly,
**D** disagree. OD numbers refer to §6. "Codex position" is as written in `15-codex-review.md`; "Codex on v2"
is empty until Codex reviews this commit.

| ID | Original claim | Counterexample / evidence | Claude position | Codex position (15 @ 59206fe) | Proposed disposition | Validation test (17-phase1 T-ids) | Remaining uncertainty | OD | Status |
|---|---|---|---|---|---|---|---|---|---|
| RC-01 | `03/02`, `02` §1: committed e-process with predictable λ tests "no skill" anytime-validly; overlapping events admissible if ledger order reflects resolution order | 30 cloned outcomes cross 20 w.p. 0.5, e = 475.0986 (REPRODUCED); clustered null 33.4 % false alarms per event, 0.0 % per cluster, 13.5 % with interleaved order (REPRODUCED); **round 3:** under time-varying skill with zero average effect the cluster-level e-process crosses in 62.8 % of paths, under a persistent macro regime in 28.9 %, where the fixed-horizon paired cluster test gives 0.1 % and (block of one period) 27.1 % (REPRODUCED, Appendix D) | A on defect; rounds 1–2: P on remedy (cluster betting sufficient as primary); **round 3: A on remedy scope.** Codex exhibited the two structures §4.1 named (RC-49, RC-50); the e-process tests the sequential conditional null, which is not the §6 average-effect estimand | P0; specify estimand, filtration, clustering, maturation; fixed-horizon cluster-aware paired analysis where the every-step conditional null is inappropriate | one increment per pre-declared outcome cluster, explicit `cluster_id` on every EventSpec (RC-53), closure rule RC-29/RC-41, eligibility against the outcome-knowable time (RC-52), no post-registration VOID or merge for dependence (RC-51); **primary confirmatory test for the average-effect estimand = fixed-horizon paired cluster test with a pre-registered calendar-block dependence model; the cluster-level e-process is the anytime-valid monitor of the sequential conditional null, labelled as such, never alone a confirmatory result or a promotion trigger**; valid-null, clustered-null, interleaved, macro-shock and time-varying generators permanent | T-02, T-10, T-11, T-12, T-17, T-19, T-29 | persistent macro regimes: at 120 clusters over 24 periods no tested block length holds size for either method (REPRODUCED); the dependence model and the supply it needs belong to OD4/OD5 | OD4, OD5 | original `FALSIFIED`; remedy `PROPOSED` (revised round 3); scope disagreement **withdrawn by Claude** (§4.1); regime dependence `EXPERIMENT_REQUIRED` |
| RC-02 | `known_at`, `resolved_at` establish prospectivity | 2020-dated event and forecast accepted today (REPRODUCED) | A | P0 | admission time = registry service receipt clock; caller `as_of` and `known_at` audited, never trusted; backdating rejected | T-01, T-02 | trusted clock in a later hosted deployment | none | `FALSIFIED`; `PROPOSED` |
| RC-03 | D6, `03/05` §2: floor p_low at the cohort base rate | [0.001, 0.01] → [0.02, 0.01] (REPRODUCED); population rate is not an individual bound | A | P0 blocking amendment | delete the floor; declared shrinkage toward a pre-registered reference class (Beta(a+s, b+n−s) for cohort data; logit-space shrinkage of the model estimate with a pre-registered weight function of cohort size); rankings only until cohorts exist; "no direct elicitation below 0.05" kept as a workflow rule; no rounding | T-20 | choice of reference classes needs data | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-04 | `03/01` §4, repeated in `03` §1: multiplying conditionals assumes independence | nested identity P(E\|D)P(D\|C)P(C) = P(E) = 0.01 (REPRODUCED) | A (foundation repeated the error; amended in `03` §6) | CONFIRMED-DEFECT | chain rule exact for true conditionals; credal layer bounds partial information; non-nested chains keep the full conditioning history; "elicit with parent context only" limited to nested milestone chains | T-21 | none | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-05 | `04/03`: midpoint scored, coverage reported; N7: Winkler interval score as secondary | Winkler elicits outcome quantiles; containment ≠ coverage; outcome is Y ∈ {0,1}, not p | A (N7 withdrawn, `02` §6) | CONFIRMED-DEFECT | one scored point probability per forecast; interval = declared ambiguity set with width decomposed (disagreement, within-model imprecision); no coverage claim; coverage language reserved for cohort-rate intervals on repeated observations | T-22 | none | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-06 | `03/03`: weights from error correlation; R8: covariance | correlation weights 1/3 each on sd 0.02/0.30/0.30 (REPRODUCED); covariance-only puts 0.935 on a constant-bias model (REPRODUCED) | A | second-moment stacking on the simplex; equal default | min wᵀSw on the simplex, S = (1−δ)M̂ + δ·diag(M̂), M̂ the uncentred second moment of past errors; equal weights until the pool beats them on untouched future clusters | T-23 | δ and history window are development choices | none | `FALSIFIED`; `PROPOSED` |
| RC-07 | `06/03`: n_eff < 1.5 persistently falsifies independence | identical series → 1.25; constant columns → 3.0 (REPRODUCED) | P: diagnostic only, keep after fixing the constant-column path | remove as evidence | n_eff never in an acceptance criterion or gate; kept as a monitoring diagnostic with the NaN-to-zero path replaced by an explicit "degenerate history" flag | T-24 | none | none | `FALSIFIED` as evidence; retention `PROPOSED` (§4.3: Codex raised no objection in three reviews) |
| RC-08 | N9: "family-wise control via e-BH"; `02` §5 item 8: ten arms = ten tests | IUT needs no correction for a conjunction claim; e-BH controls FDR, not FWER | A (conflation conceded) | CONFIRMED-DEFECT; α_j = α/[j(j+1)] for promotions | primary confirmatory claim = intersection-union test over the pre-declared comparator set; artefact promotions consume a lifetime budget by α-spending with a pre-registered summable sequence; e-BH only for exploratory discovery lists; α_1 = 0.025, α_5 ≈ 0.0017, α_10 ≈ 0.00045 for the 0.05/[j(j+1)] shape (REPRODUCED) | T-13, T-14 | budget level and whether reversible promotions get a separate budget | OD3 | `PROPOSED`; level `OWNER_DECISION` |
| RC-09 | `04/03` §4, `06` §2: time-shifted holdout control | events before T − lag are legitimate training data; "must show no gain" has no tolerance | A (withdrawn, `06` §5) | CONFIRMED-DEFECT | forbidden-future-information negative controls (deliberately leaked feature must inflate detectably); shuffled-label null distributions with pre-registered bounds; fresh future cohorts | T-15 | none | none | `FALSIFIED`; `PROPOSED` |
| RC-10 | D2: Design B research engine; R6: endpoint enumeration gives an outer hull; LP governs on ≤ 14 projection | sampled or partial enumeration is an inner approximation; projection drops induced constraints; sampled Q′ ⊂ Q overestimates the worst case | A (R6 claim withdrawn, `03` §6) | amend D2/R6 | Design C plus small exact A first; B deferred until out-of-sample value; conditional bounds enter the LP as l·P(A) ≤ P(A∩B) ≤ u·P(A) with zero-mass semantics declared; robust allocation minimises over the whole declared credal set (inner LP or complete vertices) | T-25 (Phase 1 only the LP identity tests; rest later phases) | when B earns a place | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-11 | R4: late YES → EXPIRED_NO | on-time occurrence learned late is YES; early NO before the deadline is accepted (REPRODUCED) | P: Codex's refinement is better | N11 semantics | YES iff occurrence met the deadline, evidence of occurrence time required, declared latency window per source; early NO only when the predicate is logically final; four timestamps (occurrence, publication, receipt, adjudication); source loss adjudicated separately as VOID | T-03, T-04 | latency windows per source | none | `PROPOSED` |
| RC-12 | "ledger-backed registry"; gate with owner HMAC | no replay (0 events after restart); phantom after failed append; replay of a promotion after demotion; caller-supplied key (REPRODUCED) | A | P0 | transactional single writer; all state derived by replay; owner public-key signatures over (capability, environment, release digest, evidence digest, epoch, nonce, expiry); consumed authorizations stored durably; demotion persists | T-05, T-06, T-30, T-31, T-32 | key custody model (hosted phase) | OD6 for hosting | `FALSIFIED`; `PROPOSED` |
| RC-13 | `12` Phase 1: "anchor detects any byte change" | rehashed unanchored suffix passes (REPRODUCED) | A (overclaim withdrawn, `12` Amendments) | CONFIRMED-DEFECT | property: any change inside the anchored prefix, or truncation below it, is detected; the unanchored window is reported explicitly by the restore test | T-07 | anchoring cadence vs hindsight window | none | `FALSIFIED`; `PROPOSED` |
| RC-14 | linear gate enum RESEARCH_ONLY → LIVE | SHADOW_LIVE_QUOTES would inherit SIM execution; halt vs reconciliation conflated | A | capability model | explicit capabilities × environment; halt denies new risk but preserves reconciliation and explicitly authorised cancellation | T-33 | none | none | `PROPOSED` |
| RC-15 | "token never propagates"; payload validated | `__context__` keeps the bearer header; hand-built `Cfd` payload reaches transport; NaN price and non-multiple lot accepted; fusion accepts NaN / reversed / > 1 (REPRODUCED) | A | CONFIRMED-DEFECT | typed payload objects only; exception translation **outside the active handler and** no frame that can raise holds the secret in a plain local (redacting holder whose `__repr__` never shows the value), with the whole reachable exception graph including traceback frame locals scanned (round 1 proposed `__context__ = None`, which does not work, RC-47; round 2 proposed translation outside the handler, which is necessary but not sufficient, RC-55; both REPRODUCED); synthetic-canary redaction tests on structured and encoded paths; full input validation (finite, ordered, in range) at every public function | T-26, T-34 (Phase 1); T-27 (Phase 7, RC-42) | none | none | `FALSIFIED`; `PROPOSED` (revised rounds 2 and 3) |
| RC-16 | `08` §4–§5: fresh `x-request-id` per retry; host allow-list separates SIM from LIVE | defeats Saxo's 15-second duplicate guard; same host, different path (Codex primary-source read reported in `15` §E2; UNVERIFIED here) | A (foundation repeated it; amended in `08` §6) | CONFIRMED-DEFECT | no automatic placement retry; reconcile by durable identifiers or halt; path- and credential-based SIM/LIVE policy at the adapter | later phase; recorded in `08` §6 | Saxo idempotency facts (Q3) | none | `PROPOSED` |
| RC-17 | three models + Jev mandatory; Jev gates research | recall over Jev-approved items is not funnel recall | A | retain membership; soften routing authority; stratified reject audit | mandatory three round-1 outputs plus Jev record on every issued forecast; absence holds issuance; ablations are evaluation forecaster ids only; stratified random audit of Jev rejects with known inclusion probabilities; thresholds development-only, then frozen and validated on fresh strata | T-28 (schema) ; Phase 2 design | H1, H3 untested; shared-judge bias in the Jev benchmark (UNVERIFIED) | OD8 | `PROPOSED`; H1/H3 `EXPERIMENT_REQUIRED` |
| RC-18 | proposer/promoter with canaries and frozen holdouts | side channels: feedback, runtime, cache, logs, parser execution; holdout exhaustion | A | agree and extend | isolated network-less secret-less evaluator with pinned environment hash; evaluator/scorer separation; bounded feedback and capped proposals per period; canary namespace; rolling prospective cohorts; lifetime α-spending | Phase 6; exfiltration canary tests specified in 17 §7 | none | OD3 | `PROPOSED` |
| RC-19 | D9: never force-liquidate thesis-intact; never sell a later winner for price reasons | hindsight rule; delay ≠ failure; a 30 % cash floor is unreachable by non-purchase alone; cap vs appreciation undefined | A | amend D9 | predicate kinds `milestone-deadline` vs `terminal-falsifier` in the schema now; precedence hard risk limits > terminal falsifier > valuation/opportunity review > hazard throttle; price drawdown triggers review, never a mechanical sale; counterfactual policy arms evaluated on all entries | T-29 (schema); Phase 5 experiment | H6 power | OD7 | `PROPOSED`; H6 `EXPERIMENT_REQUIRED` |
| RC-20 | `07/01`: Windows host, four OS accounts; Codex N12: fully cloud-hosted as a Phase 1 exit criterion | OS accounts are not a tested boundary (both agree); cloud adds operating cost against D10 and precedes any reduction of scientific uncertainty | P: defer the hosting decision to the Phase 2 gate with costs; Phase 1 hosting-neutral | fully cloud, Phase 1 exit criterion 1 | Phase 1 produces container images and a clean-checkout restore test that run identically on CI, laptop or cloud job; costed choice (minimal cloud / hybrid / local-only) at the Phase 2 gate; identical acceptance tests (IAM denial, egress denial, clean-account restore) for whichever is chosen | T-08 | operating-cost envelope | OD6 | `DISAGREEMENT` on timing (§4.2); `OWNER_DECISION` |
| RC-21 | `04/04`, `07` §5: 3-year realised returns in year two; "20 % hit rate necessary"; "100 % impossible" | cohort clock starts at entry; 7.45 % suffices with five 30x cycles; 100 % is a boundary case (REPRODUCED by Codex; arithmetic re-derived) | A (amended in `07` §7) | CONFIRMED-DEFECT | milestones re-expressed as months after first cohort entry; necessity claims withdrawn; inverse table's 0.5-loser rows labelled | documentation | none | OD2 (D11) | `FALSIFIED`; `PROPOSED` |
| RC-22 | D5: position 20 %, worst loss 15 % (R ≥ −0.75 assumed), cash floor 10 %, gross 100 %, Kelly 0.5 after optimisation | fully paid equity can lose 100 %; limits jointly inconsistent | A | clarify D5 | full-loss position cap ≤ 15 %; gross ≤ 90 % with the floor; Kelly fraction inside the constrained objective, not after it | later phase (allocator tests) | Q6 commissions | none | `PROPOSED` |
| RC-23 | `03/04`: cost comparison via −ln(1 − c) | exact only under a multiplicative fee convention | A | ESTABLISHED / REVISION | cost model as a component with declared conventions, lots, FX, taxes; independent post-solve check | later phase | none | none | `PROPOSED` |
| RC-24 | `04/03` §7: 300–600 events give the year-one read-out | δ = 0.01 has ≈ 27–31 % power at 600 independent observations; ≈ 1 % at δ = 0.005 (REPRODUCED) | A | P1 | power report with clusters, missingness and abstention before the Phase 2 contract; the year-one criterion is set after supply is measured | T-16 | real supply and cluster structure | OD4, OD5 | `PROPOSED`; criterion `OWNER_DECISION` |
| RC-25 | D10: OpenAI only as an owner-started daily batch | Codex reads OpenAI's non-interactive-mode documentation as a supported scheduled route (UNVERIFIED here; Codex reports the read in `15` §G) | P: verify on setup day | UNVERIFIED | setup-day verification with dated screenshots in the ledger; batch remains the fallback under R11's non-editing protocol | none in Phase 1 | provider terms | OD8 | `OWNER_DECISION` after verification |
| RC-26 | `.githooks/commit-msg` and `.claude/settings.json` enforce the attribution policy | local hook is bypassable; a tool server appended a footer to PR #1's body and to PR #2 comment `6215369656` before correction | A | CONFIRMED-DEFECT | provider-neutral CI check on commit and PR text; read-back after every tool mutation (`AGENTS.md` §7 already requires it); branch protection where available | T-09 | branch-protection visibility (API returned 403) | OD9 | `PROPOSED` |
| RC-27 (new) | `07` §6 item 1: pilot limits "mutually infeasible" until Q6 | cash is always feasible; with a 15 % full-loss cap a ticket is ≤ USD 150, so commission ≤ 1 % needs c_min ≤ USD 1.50 (Codex F; arithmetic re-derived) | A (overstatement withdrawn, `07` §7) | ESTABLISHED / REVISION | feasibility statement replaced by the exact condition; decision after Q6 | documentation | Q6 | none | `PROPOSED` |

### 3a. Round 2: Codex's reviews of PR #4 (commit `10d1581`, reviews `5548201046` and `5549803107`)

Thirteen plus seven inline findings, each with a Codex-assigned severity (P1 or P2). Every one was examined
against the documents and, where it carries a number or a logical claim, reproduced (Appendix C). Positions
as before: **A** agree, **P** partly, **D** disagree. "Resolved in" names the change made in round 2; every
disposition is `PROPOSED` until Codex reviews the resulting commit.

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in (this commit) | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-28 | Probe docstring and file name brand the artefact as a Claude product; `AGENTS.md` §7 prohibits AI marking in documentation (`4294987374`, P1) | RC-26 | **P.** The file name and docstring carry no information a reviewer needs; renamed `reconciliation_probes.py`, docstring neutral (Appendix A). The reviewer names in the matrix columns ("Claude position", "Codex position") and in the statuses are **required provenance**: the owner's protocol (PR #2 comment `6215215092` item 4) prescribes those columns, `AGENTS.md` §7 puts required provenance "in content, not in trailers", and §9 requires knowing which reviewer authored what. They stay. The branch prefix `claude/` is prescribed by issue #3 and the dispatch workflow of PR #5 | Appendix A, B; PR description | scan of changed files for attribution patterns (RC-26, T-09) | `PROPOSED`; owner may rule on the column names under OD9b |
| RC-29 | Cluster closure undefined: membership could change after outcomes arrive, or an increment could be emitted from a partial cluster, making the increment outcome-dependent (`4294987389`, P1) | RC-01 | **A.** v2 said "declared at registration before any member resolves" and "at the cluster's resolution time" without defining either. Selection of members or of the emission time after seeing outcomes is exactly the hindsight channel RC-02 closes for single events. Added: immutable membership complete before the earliest member `not_before`; one increment only when every member is resolved or pre-declared VOID; λ_k frozen at the cluster's first outcome receipt (a stronger condition than Codex asked for, needed so that no partial information of cluster k enters its own λ); closure-time ordering; later-discovered cross-cluster dependence VOIDs the later cluster. Stated limit: the rule does not cover dependence between clusters open at the same time, which remains the RC-01 open point (§4.1) | `17` §3 item 3, §2 table | T-17 (new), T-02 (reworded) | `PROPOSED` |
| RC-30 | T-13 single-run IUT check is flaky (a correct test rejects a null comparator with probability α) and a lucky seed passes an over-sized implementation (`4294987395`, P1) | RC-08 | **A.** REPRODUCED (Appendix C): 0.95 pass for a correct test, 0.90 pass for size 0.10. Replaced by (a) a deterministic oracle for the conjunction logic and (b) 20,000 least-favourable-null replications with an exact 99 % upper bound ≤ 0.06, which passes a correct test with probability 0.99995 and a size-0.06 test with 0.010. The same reasoning fixes the margin and replication count of A3, which v2 left implicit | `17` T-13, A3 | T-13 | `PROPOSED` |
| RC-31 | Monte Carlo bound 0.0008 for 0 of 2,000 is wrong; exact one-sided 95 % bound is 1 − 0.05^(1/2000) ≈ 0.0015 (`4294987398`, P2) | RC-01 | **A.** REPRODUCED: 0.001497 (closed form and Clopper–Pearson agree). The round-1 formula inserted a pseudo-count into a normal approximation, which is not a bound at the boundary. Corrected in the probe (`binom_upper`), §2, Appendix B, and A3 now names the exact binomial bound. The conclusion (bound ≤ 0.06) is unchanged | §2, Appendix A, B; `17` A3 | T-10, T-11 | `PROPOSED` |
| RC-32 | T-25 requires an exact credal instance and an inner LP although the credal network is out of Phase 1 scope (`4294987403`, P2) | RC-10 | **A.** Inconsistent as written. T-25 moved to `17` §7 (Phase 5); T-21 reduced to the arithmetic chain-rule identity with no LP; "out of scope" now names every credal LP explicitly. Adding the LP to Phase 1 was the alternative; it would add a solver dependency for no reduction of scientific uncertainty | `17` §3 out of scope, T-21, §7 | T-21 (Phase 1), T-25 (Phase 5) | `PROPOSED` |
| RC-33 | A0 lets implementation start on OD1–OD2 while the shrinkage estimator contradicts the still-binding `AGENTS.md` §2 item 7 floor and OD9 is open (`4294987415`, P1) | RC-03, RC-09 | **A.** The same contradiction holds for item 10 ("time-shifted holdouts") and the leak detector T-15. Building the floor knowingly would implement a FALSIFIED rule; building the replacement before the governance text changes would contradict §2. OD9 is split: **OD9a** (items 7 and 10 wording) becomes a prerequisite of A0; until it is recorded, T-20 and T-15 are not built and the floor is neither built nor removed. **OD9b** (item 9, §3 secrets wording, CI enforcement) can follow | §6 (OD9a/OD9b), `17` A0, §2 table; `12` amendments item 6 | A0 is a reviewed artefact, not a test | `PROPOSED`; `OWNER_DECISION` (OD9a) |
| RC-34 | Committed-prefix digest detects tampering only if the trusted anchor cannot be rewritten; scope specifies no external anchor and tests no simultaneous ledger-and-anchor replacement (`4294987422`, P1) | RC-13 | **A.** The property proved by T-07 is "detects changes relative to an anchor the verifier trusts"; v2 did not say where that anchor lives. Added an `AnchorStore` interface held by a principal other than the writer (Phase 1: a test double the writer cannot open for writing, plus an owner-committable export; the production holder is part of OD6); verification against a local copy is reported as "self-attested" | `17` §3 item 2, §2 table | T-18 (new), T-07 | `PROPOSED`; production holder `OWNER_DECISION` (OD6) |
| RC-35 | Mandatory acceptance cases are defined in `15-codex-review.md`, which is absent from this tree (`4294987435`, P2) | new | **A.** `15` is on `review/codex-20261016` (PR #2) and not in `research/claude-handoff`; merging it is not Claude's to do. Restated the twenty fixtures with exact inputs, reference-code behaviour and required behaviour in `17` §5.1, each tied to a T-id. P1–P5 were already in-tree (`01-architecture.md` §3) and are now cited there | `17` §5.1, §3 item 6 | every T-id in §5.1 | `PROPOSED` |
| RC-36 | "PACKAGE-VERIFIED by Codex" misuses a label defined for the delivered package (`4294987446`, P2) | RC-16, RC-25 | **A.** The README defines `PACKAGE-VERIFIED` as "the package reports checking it"; a reviewer's read is a different fact. Rather than add a label (the label list is in `AGENTS.md` §8 and is the owner's), the claims are `UNVERIFIED` here with the reviewer's report cited by section and date, as Codex's first option proposes. Corrected in `08` §6, §2 and §3 of this document, README label note, PR description | `08` §6; §2, RC-16, RC-25; `research/README.md` | none (documentation) | `PROPOSED` |
| RC-37 | Capability expiry depends on wall-clock time; after a clock rollback an expired unused capability can validate again because no consumed nonce or newer epoch need exist (`4294987458`, P1) | RC-12 | **A.** Correct as a logical argument; the reference code has no expiry at all, so it is a design gap in v2, not a reproduced defect. Added a persisted high-water mark of observed receipt time; admissions and capability checks below it fail closed; expiry is evaluated against max(current clock, high-water mark) | `17` §3 items 2 and 5, §2 table | T-35 (new), T-30 | `PROPOSED` |
| RC-38 | "Sensitivity with VOID as NO" is not conservative for a paired Brier difference; excluding VOIDs changes the estimand when missingness is informative (`4294987465`, P1) | RC-24 | **A.** REPRODUCED (+0.8 vs −0.8 on the 0.1 / 0.9 example). The estimand is now stated on the resolvable population with the VOID rate as a capped co-primary quantity; the sensitivity is a worst-case interval in both directions (each VOID imputed with the outcome least favourable to FULL, then most favourable); a missingness model only with a documented per-source mechanism. The cap value joins OD4 | `17` §6 estimand and missing-data rows | Phase 2 contract (reviewed artefact); generator with informative missingness in T-16 | `PROPOSED`; cap `OWNER_DECISION` (OD4) |
| RC-39 | Measuring supply in Phase 2 months 1–3 before freezing OD4–OD5 lets the design change after confirmatory outcomes are visible while the cohort stays in the estimand (`4294987471`, P1) | RC-24 | **A.** Months 1–3 become a blinded burn-in cohort: registered and committed, outcomes sealed until the contract is frozen, permanently excluded from the primary test; only counts, cluster sizes and source metadata inform OD4–OD5 | `17` §6 planned-supply row | Phase 2 contract; registry test that burn-in clusters carry a non-primary flag that replay preserves | `PROPOSED` |
| RC-40 | T-41 "tree hash unchanged" has no recorded reference value or procedure (`4294987476`, P2) | integrity | **A.** Recorded: `git rev-parse HEAD:research/original/CPE_Forschungspaket_2026-10-16` = `122a1619cdad4f1c7f577e26f86709c34ce86298` at `8b2dba7`, `10d1581` and this commit (REPRODUCED); kept beside the manifest because the Git tree object also detects added or renamed files, which `sha256sum -c` cannot | `17` T-41 | T-41 | `PROPOSED` |

| RC-41 | The single cluster increment is undefined as sum, mean or weighted aggregate; a sum can leave the bounded domain and make 1 + λX negative; a mean changes the weighting relative to an event-level estimand (`4296205602`, P1) | RC-01, RC-29 | **A.** The round-2 text had written "X̄" without defining or bounding it. Defined: unweighted mean of member increments X_i = (p_baseline − Y)² − (p_FULL − Y)² ∈ [−1, 1], so X̄ ∈ [−1, 1] and 1 + λX̄ ≥ 0.5 at λ_max = 0.5 (REPRODUCED, Appendix C); the mean is the estimand's own weighting (§6: per cluster, clusters equal); the event-weighted average is descriptive only | `17` §3 item 3, T-17 | T-17 | `PROPOSED` |
| RC-42 | T-27 requires order-payload, price, lot-size and transport-boundary behaviour although Phase 1 excludes broker adapters and execution code (`4296205617`, P2) | RC-15, RC-32 | **A.** Same inconsistency as RC-32. T-27 and fixture F-11 moved to `17` §7 (Phase 7); the HTTP source of F-12 noted as Phase 3 with the canary scanner tested on synthetic exception graphs in Phase 1; A2 restricted to fixtures whose component Phase 1 builds | `17` §3 item 6, A2, §5.1, §7 | T-26, T-29 (Phase 1); T-27 (Phase 7) | `PROPOSED` |
| RC-43 | Two concurrent presentations of one capability can both pass the unconsumed-nonce check before either writes the consumed record; T-30 covers sequential replay only (`4296205625`, P1) | RC-12 | **A.** Verification outside the writer transaction is a time-of-check/time-of-use gap. Required: epoch check, nonce insertion under a uniqueness constraint, state change and acknowledgement in one writer transaction; T-30 gains a concurrent-presentation case in which exactly one acts | `17` §3 item 5, T-30 | T-30 | `PROPOSED` |
| RC-44 | T-14 debits α only on successful promotion, so unlimited unsuccessful challengers cost nothing and the lifetime control is void (`4296205637`, P1) | RC-08 | **A.** The v2 wording "cumulative spend never exceeds α_total" left the debit event undefined. α_j is reserved and irreversibly debited at test registration, before evaluation data are unsealed; failed, cancelled and interrupted tests keep the debit; j indexes attempts. Consequence for OD3: the power cost of 0.05/[j(j+1)] is per attempt, so the budget question is sharper than v2 stated | `17` §3 item 3, T-14; OD3 row | T-14 | `PROPOSED`; level `OWNER_DECISION` (OD3) |
| RC-45 | `02` §6 item 6 labels "81–94 %" REPRODUCED although Appendix B has only the b = 0.5 row (81.4 %); the 94 % endpoint (b = 0.2, δ = 0.02) was not reproduced (`4296205645`, P2) | RC-24 | **A.** Correct: the 94 % came from Codex's D1 table. The row was added to the probe and re-run: 1,844 / 6,000 by n = 300 and 5,653 / 6,000 by n = 600 (94.2 %), identical to D1; the label is now earned and the sentence names both baselines | Appendix A, B; §2; `02` §6 item 6; OD4 row | T-16 | `PROPOSED` (`REPRODUCED` for the value) |
| RC-46 | A non-public constructor or static check cannot make elevated state unforgeable in Python; T-32 accepts type-level inaccessibility as sufficient; the protected operation must validate and consume the capability itself (`4296205655`, P1) | RC-12, RC-14 | **A.** Object visibility is not a security boundary. The protected operation verifies the signature and consumes the nonce in the writer transaction; a fabricated object (constructor, reflection, dynamic import) presented to it is rejected for lack of a valid signed capability; the static check is a lint. A5 reworded | `17` §3 item 5, A5, T-32 | T-32 | `PROPOSED` |
| RC-47 | Setting `__context__ = None` inside the handler does not prevent chaining; Python re-attaches the active exception at raise time, and `from None` only suppresses rendering (`4296205661`, P1) | RC-15 | **A.** REPRODUCED on Python 3.11.17 (Appendix C): the canary stays reachable in both in-handler variants and is absent only when the translation happens outside the handler. Round 1's disposition for RC-15 was wrong and is revised in §3; T-34 now scans the whole reachable exception graph and requires translation outside the handler or sanitisation of the source exception | §3 RC-15; `17` §3 item 6, T-34, F-12 | T-34 | `PROPOSED` (round-1 disposition corrected) |

Not addressed by either round-2 review and therefore unchanged after round 2: RC-01 remedy scope (§4.1), RC-20
hosting timing (§4.2), RC-07 n_eff retention (§4.3), and every `PROPOSED` disposition of §3 other than RC-15
(revised under RC-47). Relevant to issue #3 acceptance item 2: on a Markdown-only diff the automatic review
produced substantive statistical and security findings (RC-29, RC-30, RC-31, RC-38, RC-39, RC-41, RC-43,
RC-44, RC-47), not only style findings.

### 3b. Round 3: Codex's review of PR #4 at `43754cc` (review `5550048687`)

Seven inline findings, all P1, all on `17-phase1-amended-specification.md`; none repeats a round-1 or round-2
finding. Each was examined against the text and, where it carries a number or a logical claim, reproduced
(Appendix D). RC-55 is not a Codex finding: it is the supplementary evidence posted on issue #3 (comment
`6218965225`) by the concurrent routine execution, folded in here as announced there. Every disposition is
`PROPOSED` until Codex reviews the resulting commit; this is the last round under the budget (§4.6).

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in (this commit) | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-48 | A3 and T-10 keep 2,000 replications with a 95 % bound ≤ 0.06, which rejects a correct size-0.05 implementation about 39 % of the time; Appendix C already derived this and raised T-13 to 20,000 (`4296395259`, P1) | RC-30, RC-31 | **A.** REPRODUCED: pass probability 0.607 at 2,000 / 95 %, 0.99995 at 20,000 / 99 %. Round 2 fixed T-13 and left A3, T-10, T-11 inconsistent. All three now use the T-13 design (20,000 replications, exact one-sided 99 % bound ≤ 0.06); the valid clustered null re-run at 20,000 gives 11 crossings (0.055 %, bound 0.0011). The deterministic-oracle alternative Codex offers is used where a closed form exists (T-13 (a), T-20 (b)); the crossing rate of an adaptive e-process has none | `17` §2 table, A3, T-10, T-11 | T-10, T-11 | `PROPOSED` |
| RC-49 | §3 concedes that simultaneously open clusters sharing a macro shock make the product no test supermartingale, yet §6 designates that process as the anytime-valid primary test; the primary must impose conditional independence, combine dependent clusters, or use a method robust to the declared dependence (`4296395273`, P1) | RC-01, RC-29 | **A.** This is the structure §4.1 asked Codex to exhibit, and it is reproduced: with independent period shocks the cluster-level e-process stays under α empirically (2.24 %, forty times its valid-null rate) but has no level guarantee; with a persistent regime it crosses in 28.9 % of paths. Codex's third option is adopted: the primary confirmatory test of the average-effect estimand is the fixed-horizon paired cluster test with a pre-registered calendar-block dependence model (5.1 % under independent period shocks where the cluster-iid variance gives 13.4 %). Honest limit, found while reproducing: under the persistent regime **no tested block length holds size at 120 clusters over 24 periods** (27.1 % / 19.1 % / 14.8 % for blocks of 1 / 3 / 6 periods). That is a supply-and-horizon fact for OD4/OD5, not a Phase 1 defect; it is recorded as `EXPERIMENT_REQUIRED` with the generator committed | `17` §2 table, §3 item 3 ("what each test tests"), A3, T-12, §6 primary-test and stopping-rule rows; §3 RC-01 row; §4.1 | T-12 | `PROPOSED`; regime dependence `EXPERIMENT_REQUIRED` |
| RC-50 | The e-process is valid for the sequential null E[X_k \| past] ≤ 0 at every update, not for the population-average null stated as the estimand; time-varying performance with non-positive average can cross early (`4296395298`, P1) | RC-01 | **A.** REPRODUCED: skill +0.12 for sixty clusters then −0.12 for sixty (average exactly zero) crosses in 62.8 % of paths; +0.12 for forty then −0.08 for eighty (average −0.013) in 3.6 %; the fixed-horizon test rejects in 0.1 % and 0.08 %. Codex's first option is taken for the monitor and its second for the confirmatory claim: the e-process is kept as the anytime-valid monitor of the explicitly stated conditional null, reported continuously with that label, and a crossing triggers an integrity and dependence review but never a confirmatory result or a promotion; the average-effect estimand is tested by the fixed-horizon primary (RC-49). Together RC-49 and RC-50 close the RC-01 scope disagreement in Codex's favour | `17` §3 item 3, §6 "anytime-valid monitor" row, T-12, F-23; `02` §6 item 7 | T-12 | `PROPOSED` |
| RC-51 | "A dependence discovered after registration VOIDs the later cluster" lets an unfavourable increment be removed on post-outcome information while a favourable one stays; require a deterministic rule applied before outcomes are unsealed, or retain the increments (`4296395286`, P1) | RC-29 | **A.** The round-2 sentence reopened, for cross-cluster dependence, the hindsight channel RC-29 had closed within clusters. Codex's second option is the simpler one and has no discretionary step: a dependence discovered after registration is never a ground for VOID or merge; both clusters stay in the confirmatory process as registered; the discovery is logged as a declaration defect and reported in a dependence audit (count, list, calendar position) that feeds the dependence model of the primary test. A pre-outcome window for safe VOIDing exists in principle, but verifying "before any outcome was knowable" needs the adjudicated `knowable_at`, which is only available afterwards, so the rule would itself be retroactive; retention avoids that | `17` §2 table, §3 item 3; new T-19 | T-19 | `PROPOSED` |
| RC-52 | T-02's cutoff at first registry receipt admits forecasts submitted between publication and receipt, which can incorporate the known result; adjudication must retroactively exclude forecasts committed after the outcome became knowable (`4296395308`, P1) | RC-02, RC-29 | **A.** The schema already carried publication and occurrence times without using them for eligibility. Added the adjudicated `knowable_at` (publication time, or occurrence time when the occurrence is itself public), the cluster's outcome-knowable time t*_k = min over members of min(receipt, `knowable_at`), eligibility iff forecast receipt < t*_k, and λ_k frozen at t*_k rather than at first receipt. The exclusion is deterministic from recorded timestamps (no sign-dependent discretion, unlike RC-51's VOID); worked example in Appendix D (10:05 forecast after a 10:00 publication excluded, 09:55 eligible) | `17` §3 items 1 and 3, T-02, T-17, F-21, §6 estimand row | T-02, T-17 | `PROPOSED` |
| RC-53 | §3 creates an implicit singleton cluster for an EventSpec without `cluster_id` while T-29 requires the same input to be rejected; no implementation satisfies both (`4296395324`, P1) | RC-29 | **A.** Contradiction confirmed. Explicit `cluster_id` everywhere: an implicit singleton default is exactly how fixture F-15 (thirty cloned outcomes) would re-enter as thirty "independent" clusters without anyone declaring anything; forcing the declaration puts the dependence question at registration, where RC-51 now requires it to be settled. §3 reworded, T-29 kept | `17` §2 table, §3 items 1 and 3, T-29 | T-29 | `PROPOSED` |
| RC-54 | T-20's pass conditions are satisfied by an estimator returning s/n with low = point = high, implementing neither the Beta posterior nor the logit shrinkage; add deterministic fixtures against the specified formulas (`4296395335`, P1) | RC-03, RC-33 | **A.** REPRODUCED that the trivial implementation passes the property checks (s/n = 0.25 at (5, 20) satisfies monotone, ordered, in range). T-20 gains an oracle part with fixture parameters prior Beta(2, 18), w(n) = n₀/(n₀ + n), n₀ = 20: posterior Beta(7, 33) mean 0.175, quantiles 0.0874 / 0.2812; Beta(2, 68) mean 0.028571; the prior at n = 0; shrunk points 0.014362, 0.001 and 0.315334 (Appendix D). The fixture parameters are test values; the production prior and weight are pre-registered in the Phase 2 contract. Still built only after OD9a (RC-33) | `17` §2 table, T-20 | T-20 | `PROPOSED`; blocked on OD9a |
| RC-55 (self-reported) | Translating outside the handler is necessary but not sufficient: a secret held in a plain local of the raising frame remains reachable through `__traceback__` → `tb_frame.f_locals`, which structured loggers and crash reporters capture (issue #3 comment `6218965225`; round-2 probe checked `__context__` only) | RC-15, RC-47 | **A.** REPRODUCED (Appendix D): canary reachable in both in-handler variants and in the outside-handler variant with a plain local; absent only with a redacting holder. T-34 as written in v2 already fails the third variant, so the test was right and the remedy text was incomplete; the RC-15 disposition and T-34 now require both conditions. The reference `sim_precheck` holds `token` and `h` as locals and would fail T-34 even after moving the `raise` | §3 RC-15 row; `17` T-34 | T-34 | `PROPOSED` |

Not addressed by Codex in round 3: RC-07 n_eff retention (§4.3) and RC-20 hosting timing (§4.2). Round 3 did
engage the open scientific disagreement RC-01 (§4.1). Relevant to issue #3 acceptance item 2: the third
automatic review again produced statistical findings on a Markdown-only diff (RC-49 to RC-52 are about test
validity and hindsight channels), and this time two of them (RC-49, RC-50) addressed an open disagreement
directly, so the native route covered that part of the protocol for RC-01.

## 4. Open disagreements (what would settle each)

4.1 **RC-01 remedy scope: withdrawn by Claude in round 3.** Rounds 1–2: Codex asked for estimand, filtration,
clustering and maturation to be specified and for a fixed-horizon cluster-aware paired analysis where the
every-step conditional null is inappropriate; Claude held that pre-declared outcome clusters as the betting unit
were sufficient as the primary anytime-valid test, and wrote that the disagreement would be settled if Codex
exhibited a dependence structure that pre-declared clusters cannot capture but the fixed-horizon analysis
handles. Round 3 did that twice (RC-49: simultaneously open clusters sharing a period shock; RC-50:
time-varying skill with zero average), and both reproduce (Appendix D: 28.9 % and 62.8 % crossings for the
e-process against 27.1 %-with-block-of-one and 0.1 % for the fixed-horizon test; under independent period
shocks 2.2 % against 5.1 %). The underlying fact is that the e-process tests the sequential conditional null,
which is not the §6 estimand. Disposition: the fixed-horizon paired cluster test with a pre-registered
calendar-block dependence model is the primary confirmatory test; the e-process is the anytime-valid monitor
of the conditional null, labelled as such. What round 3 added beyond Codex's finding: under a persistent regime
neither method holds size at 120 clusters over 24 periods at any tested block length, so the dependence model
and the supply it needs are an `EXPERIMENT_REQUIRED` input to OD4/OD5, with the generator committed in T-12.
Codex has not reviewed this wording; it is `PROPOSED`.

4.2 **RC-20 hosting timing.** Codex: fully cloud-hosted architecture as Phase 1 exit criterion 1. Claude:
Phase 1 is offline and synthetic and needs CI, not hosting; the hosting decision belongs at the Phase 2 gate
with a costed comparison, because the owner's D10 (USD 0 incremental cost) conflicts with any hosted option
and because Codex's own ordering (C8) puts scientific uncertainty reduction before infrastructure. Both agree
that OS user accounts are not a tested boundary. **Settles it:** an owner decision (OD6). Phase 1 is written
so that neither choice requires rework (T-08).

4.3 **RC-07 n_eff retention.** Codex: remove n_eff as evidence. Claude: agreed as evidence; keep as a
monitoring diagnostic after fixing the degenerate-history path, because it is the cheapest alarm for a
committee collapsed to one source. Round 2 wrote that Claude would adopt Codex's position if Codex objected on
the next round; none of the three automatic reviews objected. The diagnostic stays as `PROPOSED` (T-24: n_eff
in no decision path); the owner can strike it at no cost.

4.4 **RC-08 α-spending level.** Shape agreed (summable sequence); level is a policy choice with a stated power
cost (α_10 ≈ 0.00045 under 0.05/[j(j+1)]). Not a scientific disagreement; **OD3**.

4.5 **RC-28 reviewer names in the matrix.** Codex reads `AGENTS.md` §7 as prohibiting the probe's "Claude"
name; Claude accepts that for the file and docstring (done) and holds that the reviewer-position columns and
the "which reviewer verified what" statements are the provenance §7 and §9 require and the owner's protocol
prescribes. Not a scientific disagreement. **Settles it:** the owner's reading of §7, recorded under OD9b if
the owner wants the wording clarified; Claude will adopt whichever reading the owner states.

4.6 **Round budget (issue #3: three rounds per issue).** Rounds used: RC-01 and its children RC-29, RC-41,
RC-49, RC-50, RC-51, RC-52, RC-53 → 3 (matrix v1/v2; round 2; round 3): **budget spent**; RC-15 with RC-47 and
RC-55 → 3: **budget spent**; every other item → at most 2. Codex's automatic review of this commit is expected
(PR #4 triggers it on push). The next routine execution reads it, deduplicates by comment ID against §1 and §7,
and: for a finding on a budget-spent item, appends a row to §3c with Codex's claim and a one-line Claude
assessment, status `OWNER_DECISION` (budget), and changes no other text; for a finding that exposes a fresh
defect in an item with budget left, it may make one further bounded revision; for findings that only restate
earlier positions, it records the comment IDs as processed and does nothing else. No further round is opened
on RC-01 or RC-15 without the owner extending the budget on issue #3. The three P0 families stay blocked on
OD1, OD2 and OD9a regardless.

## 5. Open hypotheses with bounded experiments (not disagreements)

| Hypothesis | Experiment (as amended) | Earliest read-out |
|---|---|---|
| H1 fusion beats best single model and Design C | IUT over the comparator set on prospective clusters; cluster-level e-process | after supply is measured (OD4) |
| H3 Jev recall ≥ 0.8 at ≤ 20 % cost | stratified randomised routing incl. reject audit with inclusion probabilities; non-inferiority design | Phase 2+ |
| H5 ≥ 60-day discovery lead | frozen media corpus and query protocol; price-acceleration rule registered separately | Phase 2+ |
| H6 hazard throttle adds value net of false alarms | locked counterfactual policy arms on all entries, one crisis cluster held out | when vintage data exist |
| central transfer claim (milestone skill → 10x discrimination) | rank correlation with realised 3-year returns from cohort entry + 36 months | year 3 after first cohort entry |

## 6. Owner decisions required (consolidated)

| OD | Decision | Options and stated costs |
|---|---|---|
| OD1 | Approve the amended Phase 1 scope and acceptance criteria in `17-phase1-amended-specification.md`, or choose a research-only pause | pause costs calendar time only; approval authorises offline synthetic work, no network |
| OD2 | Authorise recording the scientific dispositions (RC-03, 04, 05, 10, 21 and the N7/N9/N10/N11 amendments) as dated amendments to D2, D3, D4, D6, D9, D11 in `09-open-questions-and-decisions.md`; archive untouched | none beyond review time |
| OD3 | Lifetime error budget α_total for artefact promotions, and whether reversible promotions get a separate budget | smaller budget = fewer false promotions, steeply less power after a handful of **attempts** (α_j is debited per registered test, not per success, RC-44) |
| OD4 | Smallest useful Brier improvement to power the primary test for; the VOID-rate cap (RC-38); the calendar-block dependence model (block length) of the primary fixed-horizon test (RC-49) | at 600 independent-equivalent units the archived rule detects 0.02 with 81 % (b = 0.5) to 94 % (b = 0.2) power and 0.01 with 27–31 % (REPRODUCED, Appendix B); those figures assume independent clusters: under a persistent macro regime 120 clusters over 24 periods admit no valid test at any tested block length (REPRODUCED, Appendix D), so the dependence model must be justified from reference-class history before supply is read |
| OD5 | Five source families to profile, three to run; any paid-data allowance (Q5) | determines supply, cluster structure and licensing cost |
| OD6 | Hosting at the Phase 2 gate: minimal cloud, hybrid (cloud trusted writer + local stateless GPU compute), or local-only | Codex's illustrative envelope ≈ USD 1,000 / year; local-only is the weakest boundary |
| OD7 | Position caps for appreciated compounders (cost basis with a review ceiling vs market value with forced trims); precedence of hard limits over the thesis-intact veto | affects turnover, tax classification risk (Q9) and compounding |
| OD8 | Provider access route per provider after setup-day verification of terms; human duties implied | batch route adds a human to the loop and latency |
| OD9a | `AGENTS.md` §2 item 7 (floor → shrinkage) and §2 item 10 (time-shifted holdouts → forbidden-future-information controls) wording, proposed text below; **prerequisite of A0** because the Phase 1 shrinkage estimator (T-20) and leak detector (T-15) would otherwise contradict binding product requirements (RC-33) | governance change; owner approves personally; until recorded, T-20 and T-15 are not built |
| OD9b | `AGENTS.md` §2 item 9 and §3 secrets wording; CI enforcement of the attribution rule; the owner's reading of §7 on reviewer names in reconciliation documents (RC-28) | governance change; owner approves personally; not a prerequisite of A0 |

**Proposed `AGENTS.md` wording (for OD9a and OD9b; not applied here):**

- §2 item 7: replace "floored by cohort base rates" with "shrunk toward a declared reference-class rate with
  pre-registered weights; never floored; never elicited directly below 5 %".
- §2 item 9: replace "never forced liquidation of thesis-intact positions" with "no mechanical sale on price
  alone; terminal falsifiers, hard risk limits and valuation review take precedence in the declared order".
- §2 item 10: delete "time-shifted holdouts"; add "forbidden-future-information negative controls".
- §3 secrets bullet: make hosting-neutral ("in the secret store of the principal that needs them, never in
  the process environment of untrusted code").

## 7. Machine-readable state

```yaml
matrix_version: 4
date: 2026-10-16
round: 3
round_budget: 3
inputs_processed:
  research_head: 8b2dba79fe9077df53a96a6b61b1823b80930ee8
  codex_review_commit: 59206fe5f652cc3ea63114ad1c2b0fd7252962c2
  pr2_comments: [6215215092, 6215369656]
  issue3_comments: [6216073335, 6218571025, 6218864121, 6218965225]
  pr4_reviews:
    - review_id: 5548201046
      commit: 10d1581595b2d1ea6a8689e0f94b33bd68a59d66
      comment_ids: [4294987374, 4294987389, 4294987395, 4294987398, 4294987403, 4294987415, 4294987422,
                    4294987435, 4294987446, 4294987458, 4294987465, 4294987471, 4294987476]
      items: [RC-28, RC-29, RC-30, RC-31, RC-32, RC-33, RC-34, RC-35, RC-36, RC-37, RC-38, RC-39, RC-40]
    - review_id: 5549803107
      commit: 10d1581595b2d1ea6a8689e0f94b33bd68a59d66
      trigger_comment: 6218467449
      comment_ids: [4296205602, 4296205617, 4296205625, 4296205637, 4296205645, 4296205655, 4296205661]
      items: [RC-41, RC-42, RC-43, RC-44, RC-45, RC-46, RC-47]
    - review_id: 5550048687
      commit: 43754cc29add7ed47235ed9dd595ca950497ae4c
      comment_ids: [4296395259, 4296395273, 4296395286, 4296395298, 4296395308, 4296395324, 4296395335]
      items: [RC-48, RC-49, RC-50, RC-51, RC-52, RC-53, RC-54]
awaiting: codex_review_of_this_commit_record_only
round2_items:
  accepted: [RC-29, RC-30, RC-31, RC-32, RC-33, RC-34, RC-35, RC-36, RC-37, RC-38, RC-39, RC-40,
             RC-41, RC-42, RC-43, RC-44, RC-45, RC-46, RC-47]
  partly: [RC-28]
  round1_dispositions_corrected: [RC-15]
round3_items:
  accepted: [RC-48, RC-49, RC-50, RC-51, RC-52, RC-53, RC-54]
  self_reported: [RC-55]
  disagreements_withdrawn_by_claude: [RC-01-scope]
  round2_dispositions_corrected: [RC-15, RC-29-cross-cluster-void, RC-29-implicit-singleton, A3-replications]
budget_spent_items: [RC-01, RC-29, RC-41, RC-49, RC-50, RC-51, RC-52, RC-53, RC-15, RC-47, RC-55]
next_execution:
  on_codex_review_of_this_commit: record_in_section_3c; revise_only_fresh_defects_on_items_with_budget
  on_no_new_input: do_nothing
disagreements_open: [RC-20-timing]   # both positions recorded; settled by OD6, not by a further round
disagreements_resolved_pending_codex_review: [RC-01-scope]
owner_decision_items: [RC-20-timing (OD6), RC-07-retention (owner may strike), RC-28 (OD9b)]
owner_decisions_open: [OD1, OD2, OD3, OD4, OD5, OD6, OD7, OD8, OD9a, OD9b]
prerequisites_for_A0: [OD1, OD2, OD9a]
experiments_required: [H1, H3, H5, H6, transfer-claim, persistent-regime-dependence-model (OD4/OD5)]
p0_status:
  e_process_protocol: remedy proposed; fixed-horizon paired cluster test primary, e-process monitor of the conditional null; tests T-02, T-10..T-13, T-17, T-19 specified, not implemented
  rare_probability_and_intervals: remedy proposed, tests T-20 (with oracle)..T-22 specified, blocked on OD9a, not implemented
  enforcement_boundaries: remedy proposed incl. anchor boundary, clock rollback, atomic nonce consumption, action-boundary enforcement and redacting holders, tests T-01..T-09, T-18, T-30..T-35 specified, not implemented
implementation_authorised: false
```

## Appendix A. Reconciliation probe script (REPRODUCED)

Written for this matrix without importing or copying the script in `15` Appendix 1; imports only the scratch
copy of the reference code; no network, no credentials. Round 2 renamed it, neutralised the docstring (RC-28),
replaced the pseudo-count bound by the exact binomial bound (RC-31) and added the (b = 0.2, δ = 0.02) power
row (RC-45); nothing else changed. Extract and run
from the repository root after copying `source_v0_2` to a scratch directory with numpy, scipy, httpx and
pytest installed in an isolated venv:

```sh
python - <<'PY_EXTRACT'
from pathlib import Path
text = Path('research/16-reconciliation-matrix.md').read_text()
start = text.rindex('<!-- probe-script:start -->')
end = text.index('<!-- probe-script:end -->', start)
block = text[start:end].split('```python\n', 1)[1].rsplit('```', 1)[0]
Path('/path/to/scratch/reconciliation_probes.py').write_text(block)
PY_EXTRACT
/path/to/scratch/venv/bin/python -I /path/to/scratch/reconciliation_probes.py /path/to/scratch/v02
```

<!-- probe-script:start -->
```python
"""Reconciliation probes for research/16-reconciliation-matrix.md (round 1, re-run in round 2).

Runs against a scratch copy of the archived v0.2 reference code (path = argv[1]).
No network, no credentials. Reproduces the counterexamples the reconciliation
matrix relies on and evaluates the two proposed remedies (cluster-level betting,
second-moment simplex pooling). Written for the matrix independently of the
script in 15-codex-review.md Appendix 1; it does not import or copy it.
"""
import json, math, sys, tempfile, warnings
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.optimize import minimize
from scipy.stats import beta

sys.path.insert(0, sys.argv[1])
from cpe.ledger import AppendOnlyLedger, _canonical
from cpe.registry import EventSpec, Forecast, ForecastRegistry, Forecaster
from cpe.fusion import ModelInterval, JevTriage, fuse, error_correlation, min_variance_weights
from cpe.eprocess import CommittedEProcess, CommittedForecastPair, grapa_lambda
from cpe.saxo_sim import Gate, GateState, OwnerAuthorization

out = {}
T0 = datetime(2020, 1, 1, tzinfo=timezone.utc)

def spec(eid):
    return EventSpec(eid, 'Revenue exceeds threshold by expiry', 'audited filing',
                     'revenue > 100', T0 + timedelta(days=1), T0 + timedelta(days=30), 'v1')

# ---- RC-02, RC-11, RC-12, RC-13: registry and ledger ----
with tempfile.TemporaryDirectory() as d:
    ledger = AppendOnlyLedger(Path(d) / 'ledger.jsonl')
    reg = ForecastRegistry(ledger)
    reg.register_event(spec('late'))
    reg.resolve('late', True, T0 + timedelta(days=40), 'audit', 'ev-late')
    out['RC11_late_yes_status'] = reg.status('late').value
    out['RC12_restart_knows_events'] = len(ForecastRegistry(ledger)._events)
    reg.register_event(spec('backdated'))
    reg.commit_forecast(Forecast('f1', 'backdated', Forecaster.CLAUDE, 'v', 0.4, 0.6,
                                 T0, T0, ('e',), 'z' * 64))
    out['RC02_backdated_2020_forecast_accepted_today'] = True
    reg.register_event(spec('early'))
    reg.resolve('early', False, T0 + timedelta(days=2), 'audit', 'ev-early')
    out['RC11_early_no_before_deadline_status'] = reg.status('early').value
    with patch.object(ledger, 'append', side_effect=OSError('injected')):
        try:
            reg.register_event(spec('phantom'))
        except OSError:
            pass
    out['RC12_phantom_event_after_failed_append'] = 'phantom' in reg._events
    anchor = ledger.anchor()
    ledger.append('forecast', {'p': 0.1})
    rows = [json.loads(line) for line in ledger.path.read_text().splitlines()]
    rows[-1]['payload']['p'] = 0.99
    rows[-1].pop('entry_hash')
    rows[-1]['entry_hash'] = sha256(_canonical(rows[-1])).hexdigest()
    ledger.path.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    out['RC13_rehashed_unanchored_suffix_verifies'] = ledger.verify_against_anchor(anchor)

# ---- RC-12: gate replay ----
g = Gate(); key = b'synthetic-owner-key'
auth = OwnerAuthorization(GateState.RESEARCH_ONLY, GateState.SIM_READ_ONLY, 'bundle',
                          Gate.expected_mac(key, GateState.RESEARCH_ONLY, GateState.SIM_READ_ONLY, 'bundle'))
g.promote(auth, key); g.demote('kill'); g.promote(auth, key)
out['RC12_state_after_replaying_old_authorization'] = g.state.value

# ---- RC-03, RC-04 arithmetic ----
out['RC03_floor_rule_on_[0.001,0.01]_base_0.02'] = [max(0.001, 0.02), 0.01]
out['RC04_nested_chain_product'] = (0.01 / 0.1) * (0.1 / 0.5) * 0.5

# ---- RC-06, RC-07: fusion weights ----
z = np.tile(np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1.]]), (10, 1))
errors_p4 = z * np.array([0.02, 0.30, 0.30])
w_corr, _ = min_variance_weights(error_correlation(errors_p4, 0.3))
out['RC06_correlation_weights_P4'] = [round(x, 4) for x in w_corr]

def second_moment_simplex(errors, shrink=0.1):
    """Minimise w'Sw on the simplex, S = shrunk uncentred second moment of past errors."""
    m = errors.T @ errors / len(errors)
    s = (1 - shrink) * m + shrink * np.diag(np.diag(m))
    k = errors.shape[1]
    res = minimize(lambda w: w @ s @ w, np.ones(k) / k, method='SLSQP',
                   bounds=[(0, 1)] * k, constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1}])
    return res.x

out['RC06_second_moment_weights_P4'] = [round(x, 3) for x in second_moment_simplex(errors_p4)]
rng = np.random.default_rng(1)
bias_fixture = np.column_stack([np.full(40, 0.20) + 0.01 * rng.standard_normal(40),
                                0.05 * rng.standard_normal(40), 0.05 * rng.standard_normal(40)])
cov = np.cov(bias_fixture, rowvar=False)
v = np.linalg.solve(cov, np.ones(3))
out['RC06_covariance_only_weights_bias_fixture'] = [round(x, 3) for x in v / v.sum()]
out['RC06_second_moment_weights_bias_fixture'] = [round(x, 3) for x in second_moment_simplex(bias_fixture)]

names = ['claude', 'openai', 'gemini']; jev = JevTriage(0.9, 0.9, 0.0)
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    out['RC07_neff_constant_duplicate_histories'] = fuse([ModelInterval(n, .4, .6) for n in names], jev, np.ones((20, 3))).effective_models
out['RC07_neff_identical_varying_histories'] = round(fuse([ModelInterval(n, .4, .6) for n in names], jev, np.tile(np.arange(20.)[:, None], (1, 3))).effective_models, 4)
out['RC07_neff_closed_form_3/(3-2*0.3)'] = round(3 / (3 - 0.6), 4)
for tag, lo, hi in [('nan', float('nan'), float('nan')), ('reversed', .8, .2), ('over_one', 1.2, 1.3)]:
    out['RC15_fusion_accepts_' + tag] = fuse([ModelInterval(n, lo, hi) for n in names], jev, None).decision.value

# ---- RC-01: e-process cloned outcomes ----
def run_path(xs):
    ep = CommittedEProcess()
    for i, x in enumerate(xs):
        ep.commit(CommittedForecastPair(str(i), .25, .75, T0, T0 + timedelta(days=1)))
        ep.resolve(str(i), int(x > 0), T0 + timedelta(days=2))
    return ep
plus = run_path([.5] * 30); minus = run_path([-.5] * 30)
out['RC01_cloned_30_outcomes'] = {'e_if_shared_outcome_is_1': round(plus.evalue, 4),
                                  'e_if_shared_outcome_is_0': round(minus.evalue, 4),
                                  'crossing_probability_under_fair_shared_outcome': 0.5 * plus.reject_null(.05) + 0.5 * minus.reject_null(.05)}

# Vectorised archived GRAPA recurrence, checked against the reference on one path.
def grapa_paths(xs, lam_max=0.5, threshold=20.0, checkpoints=()):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    snaps = {}
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
        if n + 1 in checkpoints:
            snaps[n + 1] = peak.copy()
    return wealth, peak, snaps
check = np.random.default_rng(5).choice([-.5, .5], size=(1, 80))
ref = run_path(list(check[0])).evalue
vec = grapa_paths(check)[0][0]
out['RC01_vectorised_recurrence_matches_reference'] = bool(np.isclose(ref, vec, rtol=1e-12))

def binom_upper(k, n, conf=0.95):
    """One-sided exact (Clopper-Pearson) upper confidence bound for a binomial proportion."""
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))

# Clustered no-skill null: baseline 0.4, challenger 0.6, outcome Y~Bern(0.5) shared by every
# event in a cluster. X = (0.4-Y)^2 - (0.6-Y)^2 = +0.2 if Y=1 else -0.2. Marginal mean zero.
REPS, CLUSTERS, PER = 2000, 120, 5
rng = np.random.default_rng(2026)
y = rng.integers(0, 2, size=(REPS, CLUSTERS))
x_cluster = np.where(y == 1, 0.2, -0.2)
x_event = np.repeat(x_cluster, PER, axis=1)                  # 600 per-event increments
_, peak_event, _ = grapa_paths(x_event)
_, peak_cluster, _ = grapa_paths(x_cluster)
fa_event = float((peak_event >= 20).mean()); fa_cluster = float((peak_cluster >= 20).mean())
out['RC01_clustered_null'] = {'replications': REPS, 'clusters': CLUSTERS, 'events_per_cluster': PER,
                              'false_alarm_per_event_betting': fa_event,
                              'false_alarm_per_cluster_betting': fa_cluster,
                              'mc_upper_95_per_cluster_exact_binomial': round(binom_upper(int(round(fa_cluster * REPS)), REPS), 6)}
# Same with a shuffled (interleaved) order of events across clusters: dependence persists.
perm = rng.permutation(CLUSTERS * PER)
_, peak_shuf, _ = grapa_paths(x_event[:, perm])
out['RC01_clustered_null']['false_alarm_per_event_betting_interleaved_order'] = float((peak_shuf >= 20).mean())

# Independent power check of four rows of Codex D1 (same generator specification, seeds 17, 29, 43);
# the (0.2, 0.02) row was added in round 2 (RC-45) because 02 section 6 cited it without reproduction.
power = {}
for b, delta in [(0.5, 0.01), (0.5, 0.02), (0.2, 0.01), (0.2, 0.02)]:
    counts = {300: 0, 600: 0}
    for seed in (17, 29, 43):
        r = np.random.default_rng(seed)
        p = b + math.sqrt(delta) * r.choice([-1., 1.], size=(2000, 600))
        yy = (r.random(p.shape) < p).astype(float)
        xs = (b - yy) ** 2 - (p - yy) ** 2
        snaps = grapa_paths(xs, checkpoints=(300, 600))[2]
        for n, pk in snaps.items():
            counts[n] += int((pk >= 20).sum())
    power[f'b={b},delta={delta}'] = {'crossings_by_300_of_6000': counts[300], 'crossings_by_600_of_6000': counts[600]}
out['RC24_power_rows'] = power

# alpha-spending shape
out['RC08_alpha_spending_0.05/(j(j+1))'] = {j: round(0.05 / (j * (j + 1)), 5) for j in (1, 2, 5, 10)}
out['RC08_sum_to_infinity'] = 0.05
print(json.dumps(out, indent=2, allow_nan=False))
```
<!-- probe-script:end -->

## Appendix B. Probe output (REPRODUCED, round 2 re-run)

Identical to the round-1 output except the key `mc_upper_95_per_cluster_exact_binomial` (was
`mc_upper_95_per_cluster: 0.0008`) and the added row `b=0.2,delta=0.02`.

```json
{
  "RC11_late_yes_status": "resolved_yes",
  "RC12_restart_knows_events": 0,
  "RC02_backdated_2020_forecast_accepted_today": true,
  "RC11_early_no_before_deadline_status": "resolved_no",
  "RC12_phantom_event_after_failed_append": true,
  "RC13_rehashed_unanchored_suffix_verifies": true,
  "RC12_state_after_replaying_old_authorization": "SIM_READ_ONLY",
  "RC03_floor_rule_on_[0.001,0.01]_base_0.02": [
    0.02,
    0.01
  ],
  "RC04_nested_chain_product": 0.01,
  "RC06_correlation_weights_P4": [
    0.3333,
    0.3333,
    0.3333
  ],
  "RC06_second_moment_weights_P4": [
    0.991,
    0.004,
    0.004
  ],
  "RC06_covariance_only_weights_bias_fixture": [
    0.935,
    0.018,
    0.047
  ],
  "RC06_second_moment_weights_bias_fixture": [
    0.036,
    0.492,
    0.473
  ],
  "RC07_neff_constant_duplicate_histories": 3.0,
  "RC07_neff_identical_varying_histories": 1.25,
  "RC07_neff_closed_form_3/(3-2*0.3)": 1.25,
  "RC15_fusion_accepts_nan": "forecast",
  "RC15_fusion_accepts_reversed": "forecast",
  "RC15_fusion_accepts_over_one": "forecast",
  "RC01_cloned_30_outcomes": {
    "e_if_shared_outcome_is_1": 475.0986,
    "e_if_shared_outcome_is_0": 1.0,
    "crossing_probability_under_fair_shared_outcome": 0.5
  },
  "RC01_vectorised_recurrence_matches_reference": true,
  "RC01_clustered_null": {
    "replications": 2000,
    "clusters": 120,
    "events_per_cluster": 5,
    "false_alarm_per_event_betting": 0.3335,
    "false_alarm_per_cluster_betting": 0.0,
    "mc_upper_95_per_cluster_exact_binomial": 0.001497,
    "false_alarm_per_event_betting_interleaved_order": 0.1345
  },
  "RC24_power_rows": {
    "b=0.5,delta=0.01": {
      "crossings_by_300_of_6000": 67,
      "crossings_by_600_of_6000": 1623
    },
    "b=0.5,delta=0.02": {
      "crossings_by_300_of_6000": 1584,
      "crossings_by_600_of_6000": 4883
    },
    "b=0.2,delta=0.01": {
      "crossings_by_300_of_6000": 21,
      "crossings_by_600_of_6000": 1881
    },
    "b=0.2,delta=0.02": {
      "crossings_by_300_of_6000": 1844,
      "crossings_by_600_of_6000": 5653
    }
  },
  "RC08_alpha_spending_0.05/(j(j+1))": {
    "1": 0.025,
    "2": 0.00833,
    "5": 0.00167,
    "10": 0.00045
  },
  "RC08_sum_to_infinity": 0.05
}
```

## Appendix C. Round-2 arithmetic checks (REPRODUCED)

Needs no reference code. Run with `python -I round2_checks.py` in the same venv (extract the block as in
Appendix A, between the `round2-script` markers).

<!-- round2-script:start -->
```python
"""Round-2 arithmetic checks for the Codex findings on PR #4 (no reference code needed)."""
import json, math
import numpy as np
from scipy.stats import beta, binom

out = {}
# Finding r4294987398: exact one-sided 95 % upper bound with 0 of 2000.
n = 2000
out['exact_upper_0_of_2000'] = round(1 - 0.05 ** (1 / n), 6)
out['clopper_pearson_0_of_2000'] = round(float(beta.ppf(0.95, 1, n)), 6)
out['round1_pseudocount_normal_value'] = round(0 + 1.645 * math.sqrt((1 / n) * 1 / n), 6)
# How many crossings would still satisfy A3 (bound <= 0.06) at n = 2000?
k_max = max(k for k in range(0, 200) if beta.ppf(0.95, k + 1, n - k) <= 0.06)
out['max_crossings_of_2000_with_upper_bound_le_0.06'] = k_max
out['upper_bound_at_that_k'] = round(float(beta.ppf(0.95, k_max + 1, n - k_max)), 5)

# Finding r4294987465: VOID imputed as NO is not conservative for a paired Brier difference.
def paired_brier_increment(p_full, p_base, y):
    return (p_base - y) ** 2 - (p_full - y) ** 2   # positive favours FULL
out['void_example'] = {'p_full': 0.1, 'p_base': 0.9,
                       'impute_Y0': round(paired_brier_increment(0.1, 0.9, 0), 3),
                       'impute_Y1': round(paired_brier_increment(0.1, 0.9, 1), 3)}
out['worst_case_rule'] = 'impute Y=1 if p_full < p_base else Y=0 gives the increment least favourable to FULL'
# Worst-case bound over m VOIDs with |X| <= 1: mean increment shifts by at most m/N.
out['void_bound_shift_example'] = {'N': 300, 'm_void': 15, 'max_shift_of_mean_increment': round(15 / 300, 4)}

# Finding r4294987395: a single-run IUT check is flaky and can pass a wrong implementation.
alpha = 0.05
out['iut_single_run'] = {
    'P_correct_impl_rejects_null_comparator_once': alpha,
    'P_wrong_impl_size_0.10_passes_single_run': 1 - 0.10,
    'P_wrong_impl_size_0.10_passes_MC_bound_check_n2000': round(float(binom.cdf(k_max, 2000, 0.10)), 8),
    'P_correct_impl_fails_MC_bound_check_n2000': round(1 - float(binom.cdf(k_max, 2000, 0.05)), 6)}
# Deterministic oracle: conjunction rejects iff every component rejects.
import itertools
comps = [0.01, 0.20, 0.03]
out['iut_oracle_example'] = {'component_p': comps, 'reject_all_at_0.05': all(p <= alpha for p in comps),
                             'min_e_value_rule': 'reject iff min_j e_j >= 1/alpha'}

# T-13 design: replications and margin so that a correct level-alpha test passes with high
# probability while an over-sized implementation fails.
design = {}
for n_rep, margin, conf in [(2000, 0.01, 0.95), (10000, 0.01, 0.99), (20000, 0.01, 0.99)]:
    k_max_d = max(k for k in range(0, int(n_rep * 0.2)) if beta.ppf(conf, k + 1, n_rep - k) <= alpha + margin)
    design[f'n={n_rep},margin={margin},conf={conf}'] = {
        'k_max': k_max_d,
        'P_pass_size_0.05': round(float(binom.cdf(k_max_d, n_rep, 0.05)), 6),
        'P_pass_size_0.06': round(float(binom.cdf(k_max_d, n_rep, 0.06)), 6),
        'P_pass_size_0.07': float(binom.cdf(k_max_d, n_rep, 0.07)),
        'P_pass_size_0.10': float(binom.cdf(k_max_d, n_rep, 0.10))}
out['t13_design'] = design

# Finding r4296205661 (RC-47): does sanitising __context__ inside the handler prevent chaining?
def chained_context(style):
    try:
        try:
            raise ValueError('bearer SYNTHETIC-CANARY')
        except ValueError as e:
            if style == 'set_none_in_handler':
                new = RuntimeError('sanitised'); new.__context__ = None; raise new
            if style == 'from_none_in_handler':
                raise RuntimeError('sanitised') from None
            summary = type(e).__name__          # keep only a sanitised summary, leave the handler
        raise RuntimeError(f'sanitised ({summary})')
    except RuntimeError as r:
        return 'CANARY' in repr(r.__context__)
out['exception_context_canary_reachable'] = {s: chained_context(s) for s in
    ('set_none_in_handler', 'from_none_in_handler', 'translate_outside_handler')}

# Finding r4296205602 (RC-41): bound of the per-event paired Brier increment and of 1 + lambda * mean.
corners = [abs((pb - y) ** 2 - (pf - y) ** 2) for pb in (0.0, 1.0) for pf in (0.0, 1.0) for y in (0, 1)]
out['increment_bound'] = {'max_abs_X_i': max(corners), 'min_factor_at_lambda_max_0.5': 1 - 0.5 * max(corners)}

# Finding r4294987471 / r4294987415: no arithmetic; design-level.
print(json.dumps(out, indent=2))
```
<!-- round2-script:end -->

Output:

```json
{
  "exact_upper_0_of_2000": 0.001497,
  "clopper_pearson_0_of_2000": 0.001497,
  "round1_pseudocount_normal_value": 0.000822,
  "max_crossings_of_2000_with_upper_bound_le_0.06": 102,
  "upper_bound_at_that_k": 0.05984,
  "void_example": {
    "p_full": 0.1,
    "p_base": 0.9,
    "impute_Y0": 0.8,
    "impute_Y1": -0.8
  },
  "worst_case_rule": "impute Y=1 if p_full < p_base else Y=0 gives the increment least favourable to FULL",
  "void_bound_shift_example": {
    "N": 300,
    "m_void": 15,
    "max_shift_of_mean_increment": 0.05
  },
  "iut_single_run": {
    "P_correct_impl_rejects_null_comparator_once": 0.05,
    "P_wrong_impl_size_0.10_passes_single_run": 0.9,
    "P_wrong_impl_size_0.10_passes_MC_bound_check_n2000": 0.0,
    "P_correct_impl_fails_MC_bound_check_n2000": 0.393261
  },
  "iut_oracle_example": {
    "component_p": [
      0.01,
      0.2,
      0.03
    ],
    "reject_all_at_0.05": false,
    "min_e_value_rule": "reject iff min_j e_j >= 1/alpha"
  },
  "t13_design": {
    "n=2000,margin=0.01,conf=0.95": {
      "k_max": 102,
      "P_pass_size_0.05": 0.606739,
      "P_pass_size_0.06": 0.047114,
      "P_pass_size_0.07": 0.0003050828854872164,
      "P_pass_size_0.10": 1.0460703080855882e-15
    },
    "n=10000,margin=0.01,conf=0.99": {
      "k_max": 544,
      "P_pass_size_0.05": 0.978355,
      "P_pass_size_0.06": 0.008995,
      "P_pass_size_0.07": 1.308824218554986e-10,
      "P_pass_size_0.10": 2.645531303440866e-61
    },
    "n=20000,margin=0.01,conf=0.99": {
      "k_max": 1122,
      "P_pass_size_0.05": 0.999953,
      "P_pass_size_0.06": 0.009982,
      "P_pass_size_0.07": 9.812816862921764e-16,
      "P_pass_size_0.10": 4.181300507765669e-111
    }
  },
  "exception_context_canary_reachable": {
    "set_none_in_handler": true,
    "from_none_in_handler": true,
    "translate_outside_handler": false
  },
  "increment_bound": {
    "max_abs_X_i": 1.0,
    "min_factor_at_lambda_max_0.5": 0.5
  }
}
```

The `iut_single_run` block shows why T-13 needs its own margin: at 2,000 replications a correct level-0.05
test fails an "upper bound ≤ 0.06" check 39 % of the time. The `t13_design` block fixes the chosen design
(20,000 replications, exact one-sided 99 % upper bound ≤ 0.06, reached at 1,122 rejections): pass probability
0.99995 for a test of size 0.05, 0.0100 for size 0.06, below 10⁻¹⁵ for size 0.07. The
`exception_context_canary_reachable` block is the RC-47 reproduction; `increment_bound` is RC-41.

## Appendix D. Round-3 checks (REPRODUCED)

Needs no reference code and no network. Run with `python -I round3_checks.py` in the same isolated venv as
Appendix A (Python 3.11.17, numpy 2.4.6, scipy 1.17.1; 2.8 s), extracting the block between the
`round3-script` markers as in Appendix A. Seeds are fixed; two consecutive runs produced byte-identical
output. The generator is the one of Appendix A (baseline 0.4, challenger 0.6, X = 0.4·Y − 0.2) with 120
clusters closed in calendar order over 24 periods of five; the archived GRAPA recurrence is the Appendix A
function.

<!-- round3-script:start -->
```python
"""Round-3 checks for the Codex findings on PR #4 at 43754cc (no reference code, no network)."""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA, THRESHOLD, LAM_MAX = 0.05, 20.0, 0.5

# ---- r4296395259 (RC-48): A3 / T-10 keep 2,000 replications with a 95 % bound <= 0.06 ----
def k_max(n_rep, conf, limit):
    return max(k for k in range(0, int(n_rep * 0.2)) if beta.ppf(conf, k + 1, n_rep - k) <= limit)
a3 = {}
for n_rep, conf in [(2000, 0.95), (20000, 0.99)]:
    k = k_max(n_rep, conf, 0.06)
    a3[f'n={n_rep},conf={conf}'] = {'k_max': k,
                                   'P_pass_if_size_exactly_0.05': round(float(binom.cdf(k, n_rep, 0.05)), 6),
                                   'P_pass_if_size_0.06': round(float(binom.cdf(k, n_rep, 0.06)), 6),
                                   'P_pass_if_size_0.07': float(binom.cdf(k, n_rep, 0.07))}
out['RC48_a3_design'] = a3

# ---- archived GRAPA recurrence (vectorised), identical to 16 Appendix A ----
def grapa_paths(xs, lam_max=LAM_MAX):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
    return peak

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))

# Baseline 0.4, challenger 0.6, so X = (0.4-Y)^2 - (0.6-Y)^2 = 0.4*Y - 0.2 and E[X | P(Y=1)=q] = 0.4*q - 0.2.
def increments(q, rng):
    y = (rng.random(q.shape) < q).astype(float)
    return 0.4 * y - 0.2

def fixed_horizon_sizes(xs, periods, blocks):
    """One-sided tests of mean X <= 0 at alpha: naive (clusters iid) and block-clustered (t with G-1 df)."""
    res = {}
    k = xs.shape[1]
    m = xs.mean(axis=1); sd = xs.std(axis=1, ddof=1)
    with np.errstate(divide='ignore', invalid='ignore'):          # sd = 0 gives +/-inf or nan, counted as written
        tn = m / (sd / math.sqrt(k))
        res['naive_iid_cluster_t'] = float((tn > student_t.ppf(1 - ALPHA, k - 1)).mean())
        for b in blocks:
            g = periods // b
            bm = xs.reshape(xs.shape[0], g, -1).mean(axis=2)      # block means, equal block sizes
            tb = bm.mean(axis=1) / (bm.std(axis=1, ddof=1) / math.sqrt(g))
            res[f'block_of_{b}_periods_t_df{g-1}'] = float((tb > student_t.ppf(1 - ALPHA, g - 1)).mean())
    return res

REPS, PERIODS, PER_PERIOD = 20000, 24, 5
K = PERIODS * PER_PERIOD                                           # 120 clusters, closed in calendar order
rng = np.random.default_rng(2026)
families = {}

# (0) valid clustered null restated at 20,000 replications: independent clusters, q = 0.5.
q0 = np.full((REPS, K), 0.5)
x0 = increments(q0, rng)
fa0 = int((grapa_paths(x0) >= THRESHOLD).sum())
families['independent_clusters_valid_null'] = {
    'eprocess_crossings': fa0, 'eprocess_rate': fa0 / REPS,
    'exact_upper_99': round(binom_upper(fa0, REPS, 0.99), 6),
    'fixed_horizon_size': fixed_horizon_sizes(x0, PERIODS, (1, 3, 6))}

# (1) r4296395273 (RC-49): macro shock shared by every cluster open in a calendar period, iid across periods.
shock = rng.choice([-0.3, 0.3], size=(REPS, PERIODS))
q1 = np.repeat(0.5 + shock, PER_PERIOD, axis=1)
x1 = increments(q1, rng)
fa1 = int((grapa_paths(x1) >= THRESHOLD).sum())
families['macro_shock_iid_periods'] = {
    'description': 'q_t = 0.5 +/- 0.3 per period, 5 clusters per period, marginal E[X] = 0',
    'eprocess_crossings': fa1, 'eprocess_rate': fa1 / REPS,
    'exact_lower_99': round(float(beta.ppf(0.01, fa1, REPS - fa1 + 1)), 6),
    'fixed_horizon_size': fixed_horizon_sizes(x1, PERIODS, (1, 3, 6))}

# (2) persistent macro regime: shock follows a two-state chain with persistence 0.9 (mean zero).
s = np.empty((REPS, PERIODS)); s[:, 0] = rng.choice([-0.3, 0.3], size=REPS)
for tt in range(1, PERIODS):
    stay = rng.random(REPS) < 0.9
    s[:, tt] = np.where(stay, s[:, tt - 1], -s[:, tt - 1])
q2 = np.repeat(0.5 + s, PER_PERIOD, axis=1)
x2 = increments(q2, rng)
fa2 = int((grapa_paths(x2) >= THRESHOLD).sum())
families['macro_shock_persistent_regime'] = {
    'description': 'two-state regime, P(stay) = 0.9, stationary mean zero',
    'eprocess_crossings': fa2, 'eprocess_rate': fa2 / REPS,
    'fixed_horizon_size': fixed_horizon_sizes(x2, PERIODS, (1, 3, 6)),
    'note': 'period means are autocorrelated; a block of one period is not a valid unit here; the block length is a pre-registered dependence model'}

# (3) r4296395298 (RC-50): time-varying skill, average effect exactly zero (first half +, second half -).
q3 = np.concatenate([np.full((REPS, K // 2), 0.8), np.full((REPS, K // 2), 0.2)], axis=1)   # E[X] = +0.12 then -0.12
x3 = increments(q3, rng)
fa3 = int((grapa_paths(x3) >= THRESHOLD).sum())
families['time_varying_skill_average_zero'] = {
    'description': 'E[X_k] = +0.12 for k <= 60, -0.12 for k > 60; average over the population = 0',
    'eprocess_crossings_by_120': fa3, 'eprocess_rate': fa3 / REPS,
    'fixed_horizon_size': fixed_horizon_sizes(x3, PERIODS, (1, 3, 6))}

# (4) time-varying skill, average effect NEGATIVE: first 40 clusters +0.12, remaining 80 clusters -0.08.
q4 = np.concatenate([np.full((REPS, 40), 0.8), np.full((REPS, 80), 0.3)], axis=1)
x4 = increments(q4, rng)
avg4 = (40 * 0.12 + 80 * (0.4 * 0.3 - 0.2)) / 120
fa4 = int((grapa_paths(x4) >= THRESHOLD).sum())
families['time_varying_skill_average_negative'] = {
    'description': 'E[X_k] = +0.12 for k <= 40, -0.08 for k > 40',
    'population_average_effect': round(avg4, 5),
    'eprocess_crossings_by_120': fa4, 'eprocess_rate': fa4 / REPS,
    'fixed_horizon_rejections': fixed_horizon_sizes(x4, PERIODS, (1, 3, 6))}
out['RC49_RC50_null_families'] = families
out['RC49_RC50_reading'] = ('the e-process controls the error of the sequential conditional null E[X_k | F_(k-1)] <= 0; '
                            'under cross-cluster dependence or time-varying skill that null is false while the '
                            'population-average null holds, so a crossing is not evidence about the average estimand')

# ---- r4296395308 (RC-52): forecast eligibility against the earliest time the outcome was knowable ----
def eligible(forecast_receipt, knowable_at, first_outcome_receipt):
    return forecast_receipt < min(knowable_at, first_outcome_receipt)
out['RC52_publication_gap'] = {
    'publication_10:00_forecast_received_10:05_outcome_received_10:30':
        {'eligible_under_v2_T-02_rule': 605 < 630, 'eligible_under_v3_rule': eligible(605, 600, 630)},
    'forecast_received_09:55': {'eligible_under_v3_rule': eligible(595, 600, 630)}}

# ---- r4296395335 (RC-54): deterministic oracle fixtures for the shrinkage estimator ----
def logit(p): return math.log(p / (1 - p))
def expit(z): return 1 / (1 + math.exp(-z))
a, b = 2.0, 18.0                      # pre-registered reference-class prior, mean 0.10
fixtures = {}
for s_, n_ in [(5, 20), (0, 50), (0, 0)]:
    post = beta(a + s_, b + n_ - s_)
    fixtures[f's={s_},n={n_}'] = {'posterior': f'Beta({a + s_:g}, {b + n_ - s_:g})',
                                  'mean': round(float(post.mean()), 6),
                                  'q05': round(float(post.ppf(0.05)), 6), 'q95': round(float(post.ppf(0.95)), 6),
                                  'naive_s_over_n': (s_ / n_) if n_ else None}
out['RC54_beta_posterior_fixtures'] = fixtures
n0 = 20.0                             # pre-registered: model weight w(n) = n0 / (n0 + n)
logit_fx = {}
for p_model, (s_, n_) in [(0.001, (5, 20)), (0.001, (0, 0)), (0.5, (5, 20))]:
    ref = (a + s_) / (a + b + n_)
    w = n0 / (n0 + n_)
    p_out = expit(w * logit(p_model) + (1 - w) * logit(ref))
    logit_fx[f'p_model={p_model},s={s_},n={n_}'] = {'reference_rate': round(ref, 6), 'w_model': round(w, 4),
                                                   'point': round(p_out, 6)}
out['RC54_logit_shrinkage_fixtures'] = logit_fx
out['RC54_trivial_implementation_fails'] = fixtures['s=5,n=20']['naive_s_over_n'] != fixtures['s=5,n=20']['mean']

# ---- RC-55 (self-reported, issue #3 comment 6218965225): frame locals keep a secret reachable ----
def canary(): return 'SYNTHETIC-' + 'CANARY-r3'
class Transport(Exception):
    def __init__(self, request): super().__init__('transport'); self.request = request
class Sanitized(RuntimeError): pass
class Redacted:
    def __init__(self, value): self._value = value
    def __repr__(self): return 'Redacted(***)'
def reachable(exc):
    seen, found, stack = set(), [], [exc]
    while stack:
        e = stack.pop()
        if e is None or id(e) in seen: continue
        seen.add(id(e)); found.append(e); stack += [e.__context__, e.__cause__]
        tb = e.__traceback__
        while tb is not None:
            for v in tb.tb_frame.f_locals.values():
                (stack if isinstance(v, BaseException) else found).append(v)
            tb = tb.tb_next
    return found
def leaks(exc): return any(canary() in repr(o) for o in reachable(exc))
def case_from_none():
    headers = {'Authorization': f'Bearer {canary()}'}
    try: raise Transport(headers)
    except Transport: raise Sanitized('transport error') from None
def case_context_none():
    headers = {'Authorization': f'Bearer {canary()}'}
    try: raise Transport(headers)
    except Transport:
        s_ = Sanitized('transport error'); s_.__context__ = None; raise s_
def case_outside_plain_local():
    headers = {'Authorization': f'Bearer {canary()}'}; kind = None
    try: raise Transport(headers)
    except Transport as ex: kind = type(ex).__name__
    raise Sanitized(f'transport error: {kind}')
def case_outside_redacted():
    auth = Redacted(f'Bearer {canary()}'); kind = None
    try: raise Transport({'Authorization': auth})
    except Transport as ex: kind = type(ex).__name__
    raise Sanitized(f'transport error: {kind}')
table = {}
for name, fn in [('from_None_in_handler', case_from_none), ('context_None_in_handler', case_context_none),
                 ('outside_handler_plain_local', case_outside_plain_local), ('outside_handler_redacting_holder', case_outside_redacted)]:
    try: fn()
    except Sanitized as s_: table[name] = {'context_is_None': s_.__context__ is None, 'canary_reachable': leaks(s_)}
out['RC55_exception_graph_canary'] = table
out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
```
<!-- round3-script:end -->

Output:

```json
{
  "RC48_a3_design": {
    "n=2000,conf=0.95": {
      "k_max": 102,
      "P_pass_if_size_exactly_0.05": 0.606739,
      "P_pass_if_size_0.06": 0.047114,
      "P_pass_if_size_0.07": 0.0003050828854872164
    },
    "n=20000,conf=0.99": {
      "k_max": 1122,
      "P_pass_if_size_exactly_0.05": 0.999953,
      "P_pass_if_size_0.06": 0.009982,
      "P_pass_if_size_0.07": 9.812816862921764e-16
    }
  },
  "RC49_RC50_null_families": {
    "independent_clusters_valid_null": {
      "eprocess_crossings": 11,
      "eprocess_rate": 0.00055,
      "exact_upper_99": 0.001074,
      "fixed_horizon_size": {
        "naive_iid_cluster_t": 0.04095,
        "block_of_1_periods_t_df23": 0.04795,
        "block_of_3_periods_t_df7": 0.0476,
        "block_of_6_periods_t_df3": 0.04815
      }
    },
    "macro_shock_iid_periods": {
      "description": "q_t = 0.5 +/- 0.3 per period, 5 clusters per period, marginal E[X] = 0",
      "eprocess_crossings": 448,
      "eprocess_rate": 0.0224,
      "exact_lower_99": 0.020035,
      "fixed_horizon_size": {
        "naive_iid_cluster_t": 0.1343,
        "block_of_1_periods_t_df23": 0.05105,
        "block_of_3_periods_t_df7": 0.05075,
        "block_of_6_periods_t_df3": 0.05185
      }
    },
    "macro_shock_persistent_regime": {
      "description": "two-state regime, P(stay) = 0.9, stationary mean zero",
      "eprocess_crossings": 5781,
      "eprocess_rate": 0.28905,
      "fixed_horizon_size": {
        "naive_iid_cluster_t": 0.3372,
        "block_of_1_periods_t_df23": 0.27145,
        "block_of_3_periods_t_df7": 0.1913,
        "block_of_6_periods_t_df3": 0.1476
      },
      "note": "period means are autocorrelated; a block of one period is not a valid unit here; the block length is a pre-registered dependence model"
    },
    "time_varying_skill_average_zero": {
      "description": "E[X_k] = +0.12 for k <= 60, -0.12 for k > 60; average over the population = 0",
      "eprocess_crossings_by_120": 12555,
      "eprocess_rate": 0.62775,
      "fixed_horizon_size": {
        "naive_iid_cluster_t": 0.01585,
        "block_of_1_periods_t_df23": 0.00095,
        "block_of_3_periods_t_df7": 0.0,
        "block_of_6_periods_t_df3": 0.0
      }
    },
    "time_varying_skill_average_negative": {
      "description": "E[X_k] = +0.12 for k <= 40, -0.08 for k > 40",
      "population_average_effect": -0.01333,
      "eprocess_crossings_by_120": 727,
      "eprocess_rate": 0.03635,
      "fixed_horizon_rejections": {
        "naive_iid_cluster_t": 0.00395,
        "block_of_1_periods_t_df23": 0.0008,
        "block_of_3_periods_t_df7": 0.0,
        "block_of_6_periods_t_df3": 0.0
      }
    }
  },
  "RC49_RC50_reading": "the e-process controls the error of the sequential conditional null E[X_k | F_(k-1)] <= 0; under cross-cluster dependence or time-varying skill that null is false while the population-average null holds, so a crossing is not evidence about the average estimand",
  "RC52_publication_gap": {
    "publication_10:00_forecast_received_10:05_outcome_received_10:30": {
      "eligible_under_v2_T-02_rule": true,
      "eligible_under_v3_rule": false
    },
    "forecast_received_09:55": {
      "eligible_under_v3_rule": true
    }
  },
  "RC54_beta_posterior_fixtures": {
    "s=5,n=20": {
      "posterior": "Beta(7, 33)",
      "mean": 0.175,
      "q05": 0.087401,
      "q95": 0.281236,
      "naive_s_over_n": 0.25
    },
    "s=0,n=50": {
      "posterior": "Beta(2, 68)",
      "mean": 0.028571,
      "q05": 0.005174,
      "q95": 0.066914,
      "naive_s_over_n": 0.0
    },
    "s=0,n=0": {
      "posterior": "Beta(2, 18)",
      "mean": 0.1,
      "q05": 0.019033,
      "q95": 0.226374,
      "naive_s_over_n": null
    }
  },
  "RC54_logit_shrinkage_fixtures": {
    "p_model=0.001,s=5,n=20": {
      "reference_rate": 0.175,
      "w_model": 0.5,
      "point": 0.014362
    },
    "p_model=0.001,s=0,n=0": {
      "reference_rate": 0.1,
      "w_model": 1.0,
      "point": 0.001
    },
    "p_model=0.5,s=5,n=20": {
      "reference_rate": 0.175,
      "w_model": 0.5,
      "point": 0.315334
    }
  },
  "RC54_trivial_implementation_fails": true,
  "RC55_exception_graph_canary": {
    "from_None_in_handler": {
      "context_is_None": false,
      "canary_reachable": true
    },
    "context_None_in_handler": {
      "context_is_None": false,
      "canary_reachable": true
    },
    "outside_handler_plain_local": {
      "context_is_None": true,
      "canary_reachable": true
    },
    "outside_handler_redacting_holder": {
      "context_is_None": true,
      "canary_reachable": false
    }
  },
  "python": "3.11.17"
}
```

Reading. `RC48_a3_design` is the finding reproduced: the round-2 A3 design accepts a correct implementation
with probability 0.607. `RC49_RC50_null_families`: the cluster-level e-process is far below α on the valid
clustered null (0.055 %) and stays below α under independent period shocks (2.24 %), but has no level guarantee
there and loses control under a persistent regime (28.9 %) and under time-varying skill with zero average
(62.8 %), because in those families the sequential conditional null is false while the population-average null
is true. The fixed-horizon paired cluster test with a block-of-one-period variance holds size under independent
period shocks (5.1 %) where the cluster-iid variance does not (13.4 %), and is conservative under time-varying
skill; under the persistent regime no tested block length holds size (27.1 % / 19.1 % / 14.8 %), which with
P(stay) = 0.9 over 24 periods means roughly three independent regimes, too few for any test at this supply.
`RC52_publication_gap` is the eligibility rule on the worked example. `RC54_*` are the T-20 oracle values; the
trivial s/n implementation differs from the posterior mean (0.25 vs 0.175). `RC55_exception_graph_canary` is
the frame-locals table: only the redacting-holder variant removes the canary from the reachable graph.
