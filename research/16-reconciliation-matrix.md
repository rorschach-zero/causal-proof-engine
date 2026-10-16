# 16 Claude–Codex reconciliation matrix

Versioned record of the scientific reconciliation between the research foundation (PR #1, Claude) and the
independent review (PR #2, Codex). This document replaces the matrix v1 that was posted as a comment on PR #2
and is the single place where positions, evidence, dispositions and remaining blockers are tracked. The
original research under `research/original/` is unchanged. Nothing here authorises implementation, merges,
capital, broker connectivity or policy changes.

**Version:** v2, 2026-10-16. **Round:** 1 of 3 complete (Claude response). **Awaiting:** Codex round 2 on the
exact commit of this document. **No disposition in this matrix is a Codex agreement** until Codex has reviewed
that commit; "Codex position" quotes `research/15-codex-review.md` at commit `59206fe` (PR #2).

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

No Codex comment, commit or review newer than the above existed when this document was written. A later
round processes only inputs not listed here.

## 2. Executed in this session (REPRODUCED)

Environment: Linux, Python 3.11.17, numpy 2.4.6, scipy 1.17.1, pytest 9.1.1, httpx 0.28.1, isolated venv in a
scratch directory outside the repository; the reference code was copied from
`research/original/.../source_v0_2/` to scratch and never modified in place. No network call other than
package installation; no provider, broker or Jev call; no credential.

| Check | Command | Result |
|---|---|---|
| Archived v0.2 suite | `python -m pytest -q` in the scratch copy | `31 passed in 2.12s` |
| Reconciliation probes | `python -I claude_probes.py <scratch v0.2>` (script in Appendix A, written independently of Codex's Appendix 1) | output in Appendix B |

Key reproduced values (all from Appendix B):

- Cloned-outcome e-process: 30 pairs (0.25 vs 0.75), one shared fair outcome → e = 475.0986 on the favourable
  path, 1.0 on the other; crossing probability 0.5 under the marginal no-skill null. Matches Codex B4.
- Clustered no-skill null (120 clusters × 5 events, 2,000 replications, archived GRAPA rule, threshold 20):
  false-alarm rate **0.3335** with one increment per event, **0.0000** with one increment per cluster
  (one-sided 95 % Monte Carlo upper bound 0.0008). **New:** interleaving the 600 events in a random order
  still gives **0.1345**, so the dependence is not cured by resolution order; only the betting unit cures it.
- Codex power rows re-derived with an independently written vectorised recurrence (checked equal to the
  reference implementation to 1e-12 on a random path): b = 0.5, δ = 0.01 → 67 / 6,000 by n = 300 and
  1,623 / 6,000 by n = 600; b = 0.5, δ = 0.02 → 1,584 and 4,883; b = 0.2, δ = 0.01 → 21 and 1,881. All
  identical to Codex D1.
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

Not executed: Lean (no toolchain), any external fetch. Codex's primary-source reads of 2026-10-16 remain
PACKAGE-VERIFIED by Codex and UNVERIFIED by Claude.

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
| RC-15 | "token never propagates"; payload validated | `__context__` keeps the bearer header; hand-built `Cfd` payload reaches transport; NaN price and non-multiple lot accepted; fusion accepts NaN / reversed / > 1 (REPRODUCED) | A | CONFIRMED-DEFECT | typed payload objects only; `__context__ = None` set explicitly; synthetic-canary redaction tests on structured and encoded paths; full input validation (finite, ordered, in range) at every public function | T-26, T-27, T-34 | none | none | `FALSIFIED`; `PROPOSED` |
| RC-16 | `08` §4–§5: fresh `x-request-id` per retry; host allow-list separates SIM from LIVE | defeats Saxo's 15-second duplicate guard; same host, different path (Codex primary-source read, PACKAGE-VERIFIED) | A (foundation repeated it; amended in `08` §6) | CONFIRMED-DEFECT | no automatic placement retry; reconcile by durable identifiers or halt; path- and credential-based SIM/LIVE policy at the adapter | later phase; recorded in `08` §6 | Saxo idempotency facts (Q3) | none | `PROPOSED` |
| RC-17 | three models + Jev mandatory; Jev gates research | recall over Jev-approved items is not funnel recall | A | retain membership; soften routing authority; stratified reject audit | mandatory three round-1 outputs plus Jev record on every issued forecast; absence holds issuance; ablations are evaluation forecaster ids only; stratified random audit of Jev rejects with known inclusion probabilities; thresholds development-only, then frozen and validated on fresh strata | T-28 (schema) ; Phase 2 design | H1, H3 untested; shared-judge bias in the Jev benchmark (UNVERIFIED) | OD8 | `PROPOSED`; H1/H3 `EXPERIMENT_REQUIRED` |
| RC-18 | proposer/promoter with canaries and frozen holdouts | side channels: feedback, runtime, cache, logs, parser execution; holdout exhaustion | A | agree and extend | isolated network-less secret-less evaluator with pinned environment hash; evaluator/scorer separation; bounded feedback and capped proposals per period; canary namespace; rolling prospective cohorts; lifetime α-spending | Phase 6; exfiltration canary tests specified in 17 §7 | none | OD3 | `PROPOSED` |
| RC-19 | D9: never force-liquidate thesis-intact; never sell a later winner for price reasons | hindsight rule; delay ≠ failure; a 30 % cash floor is unreachable by non-purchase alone; cap vs appreciation undefined | A | amend D9 | predicate kinds `milestone-deadline` vs `terminal-falsifier` in the schema now; precedence hard risk limits > terminal falsifier > valuation/opportunity review > hazard throttle; price drawdown triggers review, never a mechanical sale; counterfactual policy arms evaluated on all entries | T-29 (schema); Phase 5 experiment | H6 power | OD7 | `PROPOSED`; H6 `EXPERIMENT_REQUIRED` |
| RC-20 | `07/01`: Windows host, four OS accounts; Codex N12: fully cloud-hosted as a Phase 1 exit criterion | OS accounts are not a tested boundary (both agree); cloud adds operating cost against D10 and precedes any reduction of scientific uncertainty | P: defer the hosting decision to the Phase 2 gate with costs; Phase 1 hosting-neutral | fully cloud, Phase 1 exit criterion 1 | Phase 1 produces container images and a clean-checkout restore test that run identically on CI, laptop or cloud job; costed choice (minimal cloud / hybrid / local-only) at the Phase 2 gate; identical acceptance tests (IAM denial, egress denial, clean-account restore) for whichever is chosen | T-08 | operating-cost envelope | OD6 | `DISAGREEMENT` on timing (§4.2); `OWNER_DECISION` |
| RC-21 | `04/04`, `07` §5: 3-year realised returns in year two; "20 % hit rate necessary"; "100 % impossible" | cohort clock starts at entry; 7.45 % suffices with five 30x cycles; 100 % is a boundary case (REPRODUCED by Codex; arithmetic re-derived) | A (amended in `07` §7) | CONFIRMED-DEFECT | milestones re-expressed as months after first cohort entry; necessity claims withdrawn; inverse table's 0.5-loser rows labelled | documentation | none | OD2 (D11) | `FALSIFIED`; `PROPOSED` |
| RC-22 | D5: position 20 %, worst loss 15 % (R ≥ −0.75 assumed), cash floor 10 %, gross 100 %, Kelly 0.5 after optimisation | fully paid equity can lose 100 %; limits jointly inconsistent | A | clarify D5 | full-loss position cap ≤ 15 %; gross ≤ 90 % with the floor; Kelly fraction inside the constrained objective, not after it | later phase (allocator tests) | Q6 commissions | none | `PROPOSED` |
| RC-23 | `03/04`: cost comparison via −ln(1 − c) | exact only under a multiplicative fee convention | A | ESTABLISHED / REVISION | cost model as a component with declared conventions, lots, FX, taxes; independent post-solve check | later phase | none | none | `PROPOSED` |
| RC-24 | `04/03` §7: 300–600 events give the year-one read-out | δ = 0.01 has ≈ 27–31 % power at 600 independent observations; ≈ 1 % at δ = 0.005 (REPRODUCED) | A | P1 | power report with clusters, missingness and abstention before the Phase 2 contract; the year-one criterion is set after supply is measured | T-16 | real supply and cluster structure | OD4, OD5 | `PROPOSED`; criterion `OWNER_DECISION` |
| RC-25 | D10: OpenAI only as an owner-started daily batch | Codex reads OpenAI's non-interactive-mode documentation as a supported scheduled route (PACKAGE-VERIFIED by Codex; UNVERIFIED by Claude) | P: verify on setup day | UNVERIFIED | setup-day verification with dated screenshots in the ledger; batch remains the fallback under R11's non-editing protocol | none in Phase 1 | provider terms | OD8 | `OWNER_DECISION` after verification |
| RC-26 | `.githooks/commit-msg` and `.claude/settings.json` enforce the attribution policy | local hook is bypassable; a tool server appended a footer to PR #1's body and to PR #2 comment `6215369656` before correction | A | CONFIRMED-DEFECT | provider-neutral CI check on commit and PR text; read-back after every tool mutation (`AGENTS.md` §7 already requires it); branch protection where available | T-09 | branch-protection visibility (API returned 403) | OD9 | `PROPOSED` |
| RC-27 (new) | `07` §6 item 1: pilot limits "mutually infeasible" until Q6 | cash is always feasible; with a 15 % full-loss cap a ticket is ≤ USD 150, so commission ≤ 1 % needs c_min ≤ USD 1.50 (Codex F; arithmetic re-derived) | A (overstatement withdrawn, `07` §7) | ESTABLISHED / REVISION | feasibility statement replaced by the exact condition; decision after Q6 | documentation | Q6 | none | `PROPOSED` |

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
| OD3 | Lifetime error budget α_total for artefact promotions, and whether reversible promotions get a separate budget | smaller budget = fewer false promotions, steeply less power after a handful of promotions |
| OD4 | Smallest useful Brier improvement to power the primary test for | at 600 independent-equivalent units the archived rule detects ≈ 0.02 with ≈ 80–94 % power and 0.01 with ≈ 30 % |
| OD5 | Five source families to profile, three to run; any paid-data allowance (Q5) | determines supply, cluster structure and licensing cost |
| OD6 | Hosting at the Phase 2 gate: minimal cloud, hybrid (cloud trusted writer + local stateless GPU compute), or local-only | Codex's illustrative envelope ≈ USD 1,000 / year; local-only is the weakest boundary |
| OD7 | Position caps for appreciated compounders (cost basis with a review ceiling vs market value with forced trims); precedence of hard limits over the thesis-intact veto | affects turnover, tax classification risk (Q9) and compounding |
| OD8 | Provider access route per provider after setup-day verification of terms; human duties implied | batch route adds a human to the loop and latency |
| OD9 | `AGENTS.md` wording changes (proposed text below) and CI enforcement of the attribution rule | governance change; owner approves personally |

**Proposed `AGENTS.md` wording (for OD9; not applied here):**

- §2 item 7: replace "floored by cohort base rates" with "shrunk toward a declared reference-class rate with
  pre-registered weights; never floored; never elicited directly below 5 %".
- §2 item 9: replace "never forced liquidation of thesis-intact positions" with "no mechanical sale on price
  alone; terminal falsifiers, hard risk limits and valuation review take precedence in the declared order".
- §2 item 10: delete "time-shifted holdouts"; add "forbidden-future-information negative controls".
- §3 secrets bullet: make hosting-neutral ("in the secret store of the principal that needs them, never in
  the process environment of untrusted code").

## 7. Machine-readable state

```yaml
matrix_version: 2
date: 2026-10-16
round: 1
round_budget: 3
inputs_processed:
  research_head: 8b2dba79fe9077df53a96a6b61b1823b80930ee8
  codex_review_commit: 59206fe5f652cc3ea63114ad1c2b0fd7252962c2
  pr2_comments: [6215215092, 6215369656]
  issue3_comments: []
awaiting: codex_round_2_on_this_commit
disagreements_open: [RC-01-scope, RC-20-timing, RC-07-retention]
owner_decisions_open: [OD1, OD2, OD3, OD4, OD5, OD6, OD7, OD8, OD9]
experiments_required: [H1, H3, H5, H6, transfer-claim]
p0_status:
  e_process_protocol: remedy proposed, tests T-10..T-12 specified, not implemented
  rare_probability_and_intervals: remedy proposed, tests T-20..T-22 specified, not implemented
  enforcement_boundaries: remedy proposed, tests T-01..T-09 and T-30..T-34 specified, not implemented
implementation_authorised: false
```

## Appendix A. Reconciliation probe script (REPRODUCED)

Written independently in this session; imports only the scratch copy of the reference code; no network, no
credentials. Extract and run from the repository root after copying `source_v0_2` to a scratch directory
with numpy, scipy, httpx and pytest installed in an isolated venv:

```sh
python - <<'PY_EXTRACT'
from pathlib import Path
text = Path('research/16-reconciliation-matrix.md').read_text()
start = text.rindex('<!-- probe-script:start -->')
end = text.index('<!-- probe-script:end -->', start)
block = text[start:end].split('```python\n', 1)[1].rsplit('```', 1)[0]
Path('/path/to/scratch/claude_probes.py').write_text(block)
PY_EXTRACT
/path/to/scratch/venv/bin/python -I /path/to/scratch/claude_probes.py /path/to/scratch/v02
```

<!-- probe-script:start -->
```python
"""Claude reconciliation probes, written independently in this session.

Runs against a scratch copy of the archived v0.2 reference code (path = argv[1]).
No network, no credentials. Reproduces the counterexamples the reconciliation
matrix relies on and evaluates the two proposed remedies (cluster-level betting,
second-moment simplex pooling).
"""
import json, math, sys, tempfile, warnings
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.optimize import minimize

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
                              'mc_upper_95_per_cluster': round(fa_cluster + 1.645 * math.sqrt(max(fa_cluster, 1 / REPS) * (1 - fa_cluster) / REPS), 4)}
# Same with a shuffled (interleaved) order of events across clusters: dependence persists.
perm = rng.permutation(CLUSTERS * PER)
_, peak_shuf, _ = grapa_paths(x_event[:, perm])
out['RC01_clustered_null']['false_alarm_per_event_betting_interleaved_order'] = float((peak_shuf >= 20).mean())

# Independent power check of two rows of Codex D1 (same generator specification, seeds 17, 29, 43).
power = {}
for b, delta in [(0.5, 0.01), (0.5, 0.02), (0.2, 0.01)]:
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

## Appendix B. Probe output (REPRODUCED, this session)

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
    "mc_upper_95_per_cluster": 0.0008,
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
