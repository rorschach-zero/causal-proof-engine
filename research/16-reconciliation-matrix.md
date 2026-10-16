# 16 Claude–Codex reconciliation matrix

Versioned record of the scientific reconciliation between the research foundation (PR #1, Claude) and the
independent review (PR #2, Codex). This document replaces the matrix v1 that was posted as a comment on PR #2
and is the single place where positions, evidence, dispositions and remaining blockers are tracked. The
original research under `research/original/` is unchanged. Nothing here authorises implementation, merges,
capital, broker connectivity or policy changes.

**Version:** v3, 2026-10-16. **Round:** 2 of 3 (Codex round 2 = the two automatic reviews of PR #4 at
`10d1581`, thirteen plus seven findings; this version is the Claude response). **Awaiting:** Codex round 3 on the exact commit of
this document. **No disposition in this matrix is a Codex agreement** until Codex has reviewed that commit;
"Codex position" quotes `research/15-codex-review.md` at commit `59206fe` (PR #2) or the PR #4 review comment
named in §3a. Codex's PR #4 review is a diff review of the two new documents; it did not address RC-01 (remedy
scope), RC-07 (n_eff retention) or RC-20 (hosting timing), so those remain open exactly as in v2. Silence in a
diff review is not agreement.

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
| Own posts | PR #2 comment `6216071592`, issue #3 comment `6216073335` (handoff 1 note) | not inputs |
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
| RC-01 | `03/02`, `02` §1: committed e-process with predictable λ tests "no skill" anytime-validly; overlapping events admissible if ledger order reflects resolution order | 30 cloned outcomes cross 20 w.p. 0.5, e = 475.0986 (REPRODUCED); clustered null 33.4 % false alarms per event, 0.0 % per cluster, 13.5 % with interleaved order (REPRODUCED, new) | A on defect; P on remedy: pre-declared outcome clusters as the betting unit are the primary fix | P0; specify estimand, filtration, clustering, maturation; fixed-horizon cluster-aware paired analysis | one increment per pre-declared outcome cluster at cluster resolution; clusters declared at registration before any member resolves; undeclared dependence found later VOIDs later members for betting; fixed-horizon cluster-robust paired Brier test as secondary; valid-null and clustered-null generators permanent | T-10, T-11, T-12 | residual cross-cluster dependence (macro shocks); real supply of independent clusters | OD4 | original `FALSIFIED`; remedy `PROPOSED`; scope `DISAGREEMENT` (§4.1) |
| RC-02 | `known_at`, `resolved_at` establish prospectivity | 2020-dated event and forecast accepted today (REPRODUCED) | A | P0 | admission time = registry service receipt clock; caller `as_of` and `known_at` audited, never trusted; backdating rejected | T-01, T-02 | trusted clock in a later hosted deployment | none | `FALSIFIED`; `PROPOSED` |
| RC-03 | D6, `03/05` §2: floor p_low at the cohort base rate | [0.001, 0.01] → [0.02, 0.01] (REPRODUCED); population rate is not an individual bound | A | P0 blocking amendment | delete the floor; declared shrinkage toward a pre-registered reference class (Beta(a+s, b+n−s) for cohort data; logit-space shrinkage of the model estimate with a pre-registered weight function of cohort size); rankings only until cohorts exist; "no direct elicitation below 0.05" kept as a workflow rule; no rounding | T-20 | choice of reference classes needs data | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-04 | `03/01` §4, repeated in `03` §1: multiplying conditionals assumes independence | nested identity P(E\|D)P(D\|C)P(C) = P(E) = 0.01 (REPRODUCED) | A (foundation repeated the error; amended in `03` §6) | CONFIRMED-DEFECT | chain rule exact for true conditionals; credal layer bounds partial information; non-nested chains keep the full conditioning history; "elicit with parent context only" limited to nested milestone chains | T-21 | none | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-05 | `04/03`: midpoint scored, coverage reported; N7: Winkler interval score as secondary | Winkler elicits outcome quantiles; containment ≠ coverage; outcome is Y ∈ {0,1}, not p | A (N7 withdrawn, `02` §6) | CONFIRMED-DEFECT | one scored point probability per forecast; interval = declared ambiguity set with width decomposed (disagreement, within-model imprecision); no coverage claim; coverage language reserved for cohort-rate intervals on repeated observations | T-22 | none | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-06 | `03/03`: weights from error correlation; R8: covariance | correlation weights 1/3 each on sd 0.02/0.30/0.30 (REPRODUCED); covariance-only puts 0.935 on a constant-bias model (REPRODUCED) | A | second-moment stacking on the simplex; equal default | min wᵀSw on the simplex, S = (1−δ)M̂ + δ·diag(M̂), M̂ the uncentred second moment of past errors; equal weights until the pool beats them on untouched future clusters | T-23 | δ and history window are development choices | none | `FALSIFIED`; `PROPOSED` |
| RC-07 | `06/03`: n_eff < 1.5 persistently falsifies independence | identical series → 1.25; constant columns → 3.0 (REPRODUCED) | P: diagnostic only, keep after fixing the constant-column path | remove as evidence | n_eff never in an acceptance criterion or gate; kept as a monitoring diagnostic with the NaN-to-zero path replaced by an explicit "degenerate history" flag | T-24 | none | none | `FALSIFIED` as evidence; `DISAGREEMENT` on retention (§4.3) |
| RC-08 | N9: "family-wise control via e-BH"; `02` §5 item 8: ten arms = ten tests | IUT needs no correction for a conjunction claim; e-BH controls FDR, not FWER | A (conflation conceded) | CONFIRMED-DEFECT; α_j = α/[j(j+1)] for promotions | primary confirmatory claim = intersection-union test over the pre-declared comparator set; artefact promotions consume a lifetime budget by α-spending with a pre-registered summable sequence; e-BH only for exploratory discovery lists; α_1 = 0.025, α_5 ≈ 0.0017, α_10 ≈ 0.00045 for the 0.05/[j(j+1)] shape (REPRODUCED) | T-13, T-14 | budget level and whether reversible promotions get a separate budget | OD3 | `PROPOSED`; level `OWNER_DECISION` |
| RC-09 | `04/03` §4, `06` §2: time-shifted holdout control | events before T − lag are legitimate training data; "must show no gain" has no tolerance | A (withdrawn, `06` §5) | CONFIRMED-DEFECT | forbidden-future-information negative controls (deliberately leaked feature must inflate detectably); shuffled-label null distributions with pre-registered bounds; fresh future cohorts | T-15 | none | none | `FALSIFIED`; `PROPOSED` |
| RC-10 | D2: Design B research engine; R6: endpoint enumeration gives an outer hull; LP governs on ≤ 14 projection | sampled or partial enumeration is an inner approximation; projection drops induced constraints; sampled Q′ ⊂ Q overestimates the worst case | A (R6 claim withdrawn, `03` §6) | amend D2/R6 | Design C plus small exact A first; B deferred until out-of-sample value; conditional bounds enter the LP as l·P(A) ≤ P(A∩B) ≤ u·P(A) with zero-mass semantics declared; robust allocation minimises over the whole declared credal set (inner LP or complete vertices) | T-25 (Phase 1 only the LP identity tests; rest later phases) | when B earns a place | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-11 | R4: late YES → EXPIRED_NO | on-time occurrence learned late is YES; early NO before the deadline is accepted (REPRODUCED) | P: Codex's refinement is better | N11 semantics | YES iff occurrence met the deadline, evidence of occurrence time required, declared latency window per source; early NO only when the predicate is logically final; four timestamps (occurrence, publication, receipt, adjudication); source loss adjudicated separately as VOID | T-03, T-04 | latency windows per source | none | `PROPOSED` |
| RC-12 | "ledger-backed registry"; gate with owner HMAC | no replay (0 events after restart); phantom after failed append; replay of a promotion after demotion; caller-supplied key (REPRODUCED) | A | P0 | transactional single writer; all state derived by replay; owner public-key signatures over (capability, environment, release digest, evidence digest, epoch, nonce, expiry); consumed authorizations stored durably; demotion persists | T-05, T-06, T-30, T-31, T-32 | key custody model (hosted phase) | OD6 for hosting | `FALSIFIED`; `PROPOSED` |
| RC-13 | `12` Phase 1: "anchor detects any byte change" | rehashed unanchored suffix passes (REPRODUCED) | A (overclaim withdrawn, `12` Amendments) | CONFIRMED-DEFECT | property: any change inside the anchored prefix, or truncation below it, is detected; the unanchored window is reported explicitly by the restore test | T-07 | anchoring cadence vs hindsight window | none | `FALSIFIED`; `PROPOSED` |
| RC-14 | linear gate enum RESEARCH_ONLY → LIVE | SHADOW_LIVE_QUOTES would inherit SIM execution; halt vs reconciliation conflated | A | capability model | explicit capabilities × environment; halt denies new risk but preserves reconciliation and explicitly authorised cancellation | T-33 | none | none | `PROPOSED` |
| RC-15 | "token never propagates"; payload validated | `__context__` keeps the bearer header; hand-built `Cfd` payload reaches transport; NaN price and non-multiple lot accepted; fusion accepts NaN / reversed / > 1 (REPRODUCED) | A | CONFIRMED-DEFECT | typed payload objects only; exception translation **outside the active handler** or sanitisation of the source exception, with the whole reachable exception graph scanned (round 1 proposed `__context__ = None`, which does not work: RC-47, REPRODUCED); synthetic-canary redaction tests on structured and encoded paths; full input validation (finite, ordered, in range) at every public function | T-26, T-34 (Phase 1); T-27 (Phase 7, RC-42) | none | none | `FALSIFIED`; `PROPOSED` (revised round 2) |
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

Not addressed by either Codex review of PR #4 and therefore unchanged: RC-01 remedy scope (§4.1), RC-20
hosting timing (§4.2), RC-07 n_eff retention (§4.3), and every `PROPOSED` disposition of §3 other than RC-15
(revised under RC-47). Relevant to issue #3 acceptance item 2: on a Markdown-only diff the automatic review
produced substantive statistical and security findings (RC-29, RC-30, RC-31, RC-38, RC-39, RC-41, RC-43,
RC-44, RC-47), not only style findings; it did not engage the open disagreements, which still need Codex's
full response.

## 4. Open disagreements (what would settle each)

4.1 **RC-01 remedy scope.** Codex: specify estimand, filtration, clustering and maturation, and use a
fixed-horizon cluster-aware paired analysis where the every-step conditional null is inappropriate. Claude:
pre-declared outcome clusters as the betting unit are sufficient as the *primary* anytime-valid test for the
dependence structure exhibited; the fixed-horizon analysis is a useful secondary. Evidence for Claude's
position: the clustered-null simulation (0.0 % vs 33.4 %). Evidence that Claude's position is incomplete:
cross-cluster dependence (a macro shock resolving many clusters the same way) is not covered by any
within-cluster rule; a declared-cluster scheme is only as good as the declaration. **Settles it:** Codex
either exhibits a dependence structure that pre-declared clusters cannot capture but that the fixed-horizon
analysis handles, or accepts cluster betting as primary with the fixed-horizon analysis as a mandatory
sensitivity report. Either outcome is acceptable to Claude; the Phase 1 kernel implements both (T-10–T-12).

4.2 **RC-20 hosting timing.** Codex: fully cloud-hosted architecture as Phase 1 exit criterion 1. Claude:
Phase 1 is offline and synthetic and needs CI, not hosting; the hosting decision belongs at the Phase 2 gate
with a costed comparison, because the owner's D10 (USD 0 incremental cost) conflicts with any hosted option
and because Codex's own ordering (C8) puts scientific uncertainty reduction before infrastructure. Both agree
that OS user accounts are not a tested boundary. **Settles it:** an owner decision (OD6). Phase 1 is written
so that neither choice requires rework (T-08).

4.3 **RC-07 n_eff retention.** Codex: remove n_eff as evidence. Claude: agreed as evidence; keep as a
monitoring diagnostic after fixing the degenerate-history path, because it is the cheapest alarm for a
committee collapsed to one source. **Settles it:** this is a small engineering preference; Claude will adopt
Codex's position if Codex objects to retaining the diagnostic on the next round.

4.4 **RC-08 α-spending level.** Shape agreed (summable sequence); level is a policy choice with a stated power
cost (α_10 ≈ 0.00045 under 0.05/[j(j+1)]). Not a scientific disagreement; **OD3**.

4.5 **RC-28 reviewer names in the matrix.** Codex reads `AGENTS.md` §7 as prohibiting the probe's "Claude"
name; Claude accepts that for the file and docstring (done) and holds that the reviewer-position columns and
the "which reviewer verified what" statements are the provenance §7 and §9 require and the owner's protocol
prescribes. Not a scientific disagreement. **Settles it:** the owner's reading of §7, recorded under OD9b if
the owner wants the wording clarified; Claude will adopt whichever reading the owner states.

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
| OD4 | Smallest useful Brier improvement to power the primary test for; the VOID-rate cap (RC-38) | at 600 independent-equivalent units the archived rule detects 0.02 with 81 % (b = 0.5) to 94 % (b = 0.2) power and 0.01 with 27–31 % (REPRODUCED, Appendix B) |
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
matrix_version: 3
date: 2026-10-16
round: 2
round_budget: 3
inputs_processed:
  research_head: 8b2dba79fe9077df53a96a6b61b1823b80930ee8
  codex_review_commit: 59206fe5f652cc3ea63114ad1c2b0fd7252962c2
  pr2_comments: [6215215092, 6215369656]
  issue3_comments: [6216073335]
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
awaiting: codex_round_3_on_this_commit
round2_items:
  accepted: [RC-29, RC-30, RC-31, RC-32, RC-33, RC-34, RC-35, RC-36, RC-37, RC-38, RC-39, RC-40,
             RC-41, RC-42, RC-43, RC-44, RC-45, RC-46, RC-47]
  partly: [RC-28]
  round1_dispositions_corrected: [RC-15]
disagreements_open: [RC-01-scope, RC-20-timing, RC-07-retention]
owner_decisions_open: [OD1, OD2, OD3, OD4, OD5, OD6, OD7, OD8, OD9a, OD9b]
prerequisites_for_A0: [OD1, OD2, OD9a]
experiments_required: [H1, H3, H5, H6, transfer-claim]
p0_status:
  e_process_protocol: remedy proposed incl. cluster closure, tests T-10..T-13, T-17 specified, not implemented
  rare_probability_and_intervals: remedy proposed, tests T-20..T-22 specified, blocked on OD9a, not implemented
  enforcement_boundaries: remedy proposed incl. anchor boundary, clock rollback, atomic nonce consumption and action-boundary enforcement, tests T-01..T-09, T-18, T-30..T-35 specified, not implemented
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
