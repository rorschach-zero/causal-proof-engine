# 19 Phase 1 hand-off (PROPOSED)

Dated hand-off from the research foundation to the first implementation session, written 2026-10-20 on the
delegated decisions recorded in issue #3 comment `6297828986` (OD11 (b), OD1, OD2, OD9a, OD10). Status:
**PROPOSED**, a `REVISION` of this review. It **selects** from `17-phase1-amended-specification.md`,
`18-method-reassessment.md`, that comment and Codex's strategy review of PR #4; it adds no specification, changes
no text of `16`, `17` or `18` and chooses no owner field. The owner confirmed the decisions on 2026-10-20 (issue #3
comment `6297969313`, 18:18 UTC, relayed in `6297994651`), so they are `OWNER_DECISION`; code starts only after the
owner merges this document (comment `6297828986`, "Hand-off before code").

## 1. Sources and exact SHAs

| Source | Identity | Note |
|---|---|---|
| Branch `claude/reconciliation-round-1` (PR #4), head at writing | commit `8d5dbb97a9d8f7091491f44c9910ebd0e0583549` (R9, 2026-10-20 16:02 UTC) | the tree this document is written on |
| `main` after the merges of PR #4 (`f68a222`) and PR #1 | commit `b2e6cbfc374c9b628a6956bffd0e98a6c0a5ac2e` | contains `8d5dbb9`; the base of the hand-off PR |
| `17-phase1-amended-specification.md`, version 49 | blob `02c1203b421295373cbdf66846025eee237d41e5` | identical at `62d4c2a` and `8d5dbb9` (`git diff --quiet 62d4c2a 8d5dbb9 -- research/17-phase1-amended-specification.md`) |
| `18-method-reassessment.md`, revision R9 | blob `fd2e51ef057b8bd80e55f43aa36fcf427b4d62b9` | R8 at `62d4c2a` is blob `f1d80edfedb61663f24bf617d54b607716cb8a7b`; R9 adds RC-315 (one confirmatory register for all of Phase 1) and RC-317 (checker), `16` §3bg |
| `16-reconciliation-matrix.md`, v53 | blob `ccedb1e001dab4118f8627c529e2bf78e1dbf9a2` at `8d5dbb9` | §6 holds the consolidated owner decisions OD1 to OD11 and the proposed `AGENTS.md` wording for OD9a |
| Decision comment | issue #3 comment `6297828986`, 2026-10-20 18:11 UTC | reads `18` at `62d4c2a0ebc6b6ac934aed63f61e2f308e838404`; confirmed by the owner's reply `6297969313` (18:18 UTC) |
| Codex strategy review | PR #4 review `5586708590` on `62d4c2a`, inline comments `4326311665`, `4326311683`, `4326311701`, `4326311717` | §2 below records how each is answered |
| Original research package | tree `122a1619cdad4f1c7f577e26f86709c34ce86298` (`research/original/CPE_Forschungspaket_2026-10-16`) | `MANIFEST.sha256`: 71 OK on this tree (run here, §6) |

The decision comment and Codex's review read R8. R9 changes nothing of `17` and nothing of the OD11 (b) scope;
its one substantive change, RC-315, is carried into §3 and §4 below (the confirmatory register).

## 2. Decisions this hand-off rests on

Quoted in substance from comment `6297828986`; the comment is the record.

- **OD11 (b).** The confirmatory design is simplified to `18` §6: an externally fixed question set Q forecast
  exhaustively, a period-level fixed-horizon block t calibrated over one pre-registered validity class 𝓛, a
  fixed-sequence family, the e-process as a monitor that never confirms. Numerical parameters (period length, G,
  δ, 𝓛, weighting, family order) are frozen after a separate Phase 4 design and burn-in cohort, under a
  deterministic selection rule anchored before any design-cohort measurement is seen; the calibration algorithm,
  size, claim binding, single-attempt rule and beacon round are fixed in advance (`18` §7 M-1). Every result stays
  conditional on 𝓛. S_max counts fixed-sequence families, one family binding its whole order, every 𝓛_j and cutoff
  and one complete report before any beacon output. The dated amendment of `17` §3 item 3 and §6 is written later
  as one document and reviewed once. Review rounds on PR #4 end; later Codex findings on `16`, `17` or `18` are
  listed for the owner, not applied.
- **OD1.** Approved for the invariant infrastructure only: schemas; the ledger with anchoring and replay; the four
  timestamps with the resolution-rule and adjudication registry; the pre-registration registry; the offline
  capability model; input validation; CI; only the negative controls and fixtures that survive under (b).
  Everything offline, on synthetic data. Not built: `17` §3 item 3 (the statistics kernel), the audited-source and
  late-link controls that (b) retires, T-34 and the secret-handling code (OD10).
- **OD2** approved (dated amendments in `09-open-questions-and-decisions.md`). **OD9a** approved as worded in `16`
  §6, items 7 and 10, to be applied in a separate PR the owner merges personally. **OD10** deferred: versions 5 to
  49 of `17` stay frozen as the research record.

**Codex's four strategy comments and where each lands.**

| Comment | Finding (short) | Answered by |
|---|---|---|
| `4326311665` | freeze design selection before Phase 1; OD1 list omits the adjudication registry; name the surviving fixtures; a hand-off with exact SHAs, retained and retired requirements, owner fields, test mapping, reproduction commands, no-execution boundary | OD1 names the resolution-rule and adjudication registry; OD11 (b) anchors the selection rule; this document (§1, §3, §4, §5, §6, §7) |
| `4326311683` | define whether S_max counts families or component hypotheses before relying on fixed-sequence power | OD11 (b): S_max counts families; one family binds its order, every 𝓛_j and cutoff, one report. The power recomputation Codex asks for belongs to the amendment, not to Phase 1 code (§5) |
| `4326311701` | membership in 𝓛 is unprovable from measurements; state the result as conditional, with a generative rationale, out-of-class sensitivity and a refusal policy | OD11 (b), fourth bullet; the three items are owner fields of the amendment (§5) |
| `4326311717` | Phase 2 cannot produce the inputs to freeze G, δ, 𝓛 and the order; freeze after a disjoint Phase 4 design cohort | OD11 (b), second bullet: freeze after the Phase 4 design and burn-in cohort, confirmatory cohort disjoint from it |

## 3. Requirements of `17` §3 items 1, 2 and 4 to 8 under OD11 (b)

Status words: **retained** (built in Phase 1 under OD1); **retired** (removed by OD11 (b), `18` §6 "Replace",
stays in the record under OD10); **with item 3** (part of the statistics kernel or of the amendment of `17` §3
item 3 and §6; not Phase 1 code); **gated** (retained, built only after the named owner action); **open** (not
named by OD1 and not retired by `18` §6; the owner names it, §5).

### 3.1 Item 1, schemas

| Requirement (`17` §3 item 1) | Status | Reason |
|---|---|---|
| `EventSpec`: typed resolution predicate, mandatory `cluster_id`, `predicate_kind`, four timestamps, latency window, adjudicated `knowable_at` with evidence (RC-52), `falsifier_observable_from`, earliest-knowable bound e_i (RC-138) | retained | OD1: schemas, four timestamps; `18` §6 retains the four timestamps and the resolution rules |
| `Forecast` (point, declared interval, arm version id, prompt and model hashes, evidence ids); no cutoff field of its own (RC-112) | retained | OD1: schemas |
| `ArmVersion`: immutable record before any registration, declared cutoff as an UNVERIFIED claim with evidence (RC-98), consumed arms and effective cutoff (RC-156); registration refused when e_i is at or before the effective cutoff (RC-138); submission refusals for own cutoff or a later arm version (RC-112) | retained | OD1: pre-registration registry and four timestamps; `18` §6 retains "pre-registration before unblinding" |
| Breach classes from timestamps: early-knowability (RC-135), registration (RC-139, read at t_reg, RC-200), issuance (RC-163); their counts and reports | retained as adjudication categories | they are functions of the four timestamps and the registration record; OD1: adjudication registry |
| What a breach does in the statistic: box rule, "outside the scored population", cap exclusions | with item 3 | `17` §3 item 3 defines the box rule; OD1 does not build item 3 |
| Cutoff correction (RC-150): withdrawal of the arm version, new version with evidence | retained | registry rule; OD1: pre-registration registry |
| Cutoff correction ending the confirmatory claim | with item 3 | a claim-level consequence of the primary test |
| `JevRecord`, `Capability`, `ResearchOutput` JSON schema, `Cluster` registration record | retained | OD1: schemas |
| Scoring slot key (event id, arm, slot), second record and other version refused at submission, primary slot named in advance (RC-75, RC-89, RC-96) | retained | registry rule; the slot's use in the increment is item 3 |
| Logical finality: `knowable_at` = min(publication, public occurrence, deadline + window) (RC-77, RC-146); latency window applied to the evidenced publication time (RC-105); disposition at finality immutable (RC-88); observation of absence and the monotone-publication condition (RC-113); source-latency defect logged, never changes an outcome | retained | OD1: resolution-rule and adjudication registry; `18` §6 retains the resolution rules |
| Withdrawal of a source from the next cohort on its registration-breach count or defect rate (RC-169) | open | `18` §6 "Replace" 1 retires the listing role of sources, not a resolution source's pre-registered integrity bound, and OD1 does not name the rule; the per-source defect log stays (above) |
| Late-record budget η_max, the η close of the registration window and its replay (RC-164, RC-171, RC-188, RC-193), calibration at α − η_max, decision date T_D = T_A + D and monitor factors at H_k + D (RC-149, RC-157), the Phase 2 late-record measurement | with item 3 | the A3 calibration over N is replaced by the calibration over 𝓛 (`18` §6 "Replace" 2); what survives of T_D and D is the amendment's to state |
| Outcome-blind enrolment T_E (RC-219, RC-220), pre-enrolment breach audit against resolution records (RC-223, RC-244, RC-246), supply-exogeneity hypothesis and screen (RC-228 to RC-241) | retired | `18` F5: the audit adds no identification once Q is the universe; `18` §6 "Replace" 1 retires the screen; Q is fixed before forecasting |
| Resolution rules (RC-11, RC-71): occurrence-time rule, YES needs evidence of timely occurrence, VOID when a YES has no time, `EXPIRED_NO` needs evidence | retained | OD1: resolution-rule registry |
| Point-in-time store and as-of read interface (RC-79, RC-86) | gated: OD9a | `17` A0 and item 1 ("built only after OD9a, with T-15"); the Phase 1 brief builds it after the OD9a wording is merged into `AGENTS.md` |
| Evaluation of the registered predicate (selector, field, comparator, value) against the archived source content at adjudication (PR #18 round-3 finding `4329664953`) | retained: a separate component, after the hardening PRs (decided 2026-10-21) | first recorded here as gated on OD9a; PR #24 review finding `4330128184` showed that OD9a governs the as-of feature store and the leak controls, not the archive of resolution bytes. Decided by the owner's delegate on 2026-10-21 (§9.5, corrected after `4334268792`, §9.9): the resolution-content archive (the archived source bytes of each resolution record, content-addressed, with the evaluator over selector, field, comparator and value) is its own component, not gated on OD9a, and is scheduled independently of the point-in-time feature store, which stays gated on the OD9a wording. Until then the record's `claim` is the observer's attestation (PR #18 deviation 2) and the adjudication registry trusts it |

### 3.2 Item 2, ledger and registry

| Requirement (`17` §3 item 2) | Status | Reason |
|---|---|---|
| Single transactional writer, canonical JSONL export, server receipt time, append atomic with state change, deterministic replay of registry, cluster and capability state, anchor as committed-prefix digest with the unanchored-window report, restore from a clean checkout in CI | retained | OD1: ledger with anchoring and replay |
| Replay of e-process state | with item 3 | the e-process is item 3 |
| Candidate log (RC-78): candidate recorded before any forecast, registration refused without a prior entry, entry after a forecast refused, log in the ledger and the replay | retained | OD1: pre-registration registry |
| Exhaustive enumeration from anchored source snapshots, audit against the source archive, drawn omissions under the cap and the box rule (RC-191, RC-195, RC-198) | retired | `18` §6 "Replace" 1: omission audit, draw and box rule retired |
| Reference universe (RC-239, RC-241), one cluster authority across universes (RC-243, RC-248), one reading of the union (RC-250) | retired | `18` §6 "Replace" 1; Q replaces the source listing audited against a universe |
| Variance blocks from linked components, late links, every-subset partitions, M_late, K_max count (RC-250 to RC-274) | retired | `18` §6 "Replace" 2 and §3 "Late evidence"; OD11 (b): M_late and K_max lapse |
| Batch of a cluster (RC-214), post-registration members (RC-215), point-in-time cluster assignment (RC-216), close replay (RC-193), registration schedule and batch calendar (RC-200), beacon deadline (RC-208) | retired | listing-window machinery of the audited-source design (`18` §6 "Replace" 1) |
| Cluster membership fixed at registration; a later relationship never changes a registered cluster's members, record or key, and merges nothing (RC-66, RC-216, T-17, T-19) | retained | `18` §6 retains paired increments per outcome cluster; the immutability is a registry invariant |
| Beacon-seeded draw 1{SHA-256(s_b ‖ id_k) < π·2^256} with s_b from a round published after the anchor, no draw before the round, one declaration per cluster (RC-187) | retained for the calibration seed only; no draw over Q | issue #3 comment `6298303061` (clarification of OD11 (b), 2026-10-20): Q is forecast exhaustively, no event draw over Q is built in any phase, and beacon-seeded sampling serves the calibration record only (`18` M-1 (i), RC-304) |
| Anchor trust boundary (RC-34): `AnchorStore` interface, harness-owned double in Phase 1, "self-attested" never reported as verified | retained | OD1: anchoring; the production holder is OD6 (§5) |
| Clock (RC-37, RC-65, RC-73, RC-100): every check persisted before its verdict, high-water mark, discontinuity against the epoch baseline | retained | OD1: capability model and ledger |
| Epoch rotation at start and at demotion (RC-74, RC-103); demotion without the anchor store, demoted-unanchored state, start at the floor (RC-123) | retained | OD1: offline capability model |

### 3.3 Items 4 to 8

| Requirement | Status | Reason |
|---|---|---|
| Item 4: input validation (finite, 0 ≤ low ≤ point ≤ high ≤ 1), mandatory-input check (three providers plus Jev), typed decisions | retained | OD1: input validation |
| Item 4: equal-weight fusion, second-moment pool behind a flag, n_eff diagnostic with the degenerate-history flag | open | `18` §6 retains "the capability, CI and fixture work of items 4 to 8"; OD1 names input validation only |
| Item 5: whole-tuple signature verification under one canonical serialisation (RC-62); epoch, nonce, expiry, environment, release checks; consumed-authorization store; demotion persistence and rotation in one writer transaction; expiry against the high-water mark; four-step anchored commit of a protected operation (RC-153, RC-158, RC-197); enforcement at the action boundary, no object is authority (RC-43, RC-46) | retained | OD1: offline capability model; `17` A5 |
| Item 5: the secret-handling code named in A0 | gated: OD10 | `17` A0; comment `6297828986` "Not built" |
| Item 6: negative controls and fault injection | per fixture, §4.2 | OD1: "only those negative controls and fixtures that survive under (b)" |
| Item 7: power and protocol report (D1 table, detectable effect at 300 and 600 units, Phase 2 contract draft) | with item 3 | the figures are those of the retired primary; `18` §3 and M-4 give the simplified method's, inside the amendment |
| Item 8: pinned hashed dependencies, Python 3.11 and 3.13, strict typing, property tests, attribution and commit-identity check (T-09), `research/original/` by manifest and excluded from tooling, static no-executor-import check | retained | OD1: CI |
| Item 8: Lean job with a deliberately false proof, cache failure reported as "not verified" (T-40) | retained | OD1: CI; `17` A7 and item 8 include the job, and its false-proof and cache-failure cases need no Phase 1 lemma; `04-formal-verification.md` holds the retained lemmas |
| "Explicitly out of scope" list of `17` §3 (credal LP, hazard model, allocator, adapters, Jev client, SIM, hosting, self-improvement loop, learned calibration, real events, `AGENTS.md`) | unchanged | out of scope before and after (b) |

## 4. Acceptance tests and fixtures

### 4.1 Tests of `17` §5

| Test | `17` criterion | Status | What survives | `18` §7 |
|---|---|---|---|---|
| T-01 | A2 | retained | backdating refused; receipt time is the server clock | — |
| T-02 | A2 | retained in part | every exclusion from recorded timestamps (receipt after t*_k, after `knowable_at`, after finality, outside the window, after t_cut) and every refusal at submission or registration (slot, version, pre-registration, cutoff, own cutoff, later arm version); the box-rule clauses are with item 3 | — |
| T-03, T-04 | A2 | retained | every disposition rule; the F-02c box-rule clause is with item 3 | — |
| T-05, T-06, T-07, T-08, T-18 | A1 | retained | phantom-free failure, at most one durable record, anchored-prefix detection, self-attested versus verified, identical replay digest in three environments; the "both scored" schedule clause of T-06 is with item 3 | — |
| T-09 | A7 | retained | attribution text, merge message before and after the merge, author and committer identity (OD9b names the list) | — |
| T-10, T-11 | A3 | with item 3 | e-process crossing rates | M-9 |
| T-12 | A3 / A6 | retired | the calibrated c* over N, its families and controls | M-1 to M-4, M-7 |
| T-13 | A6 | retired | the IUT | M-6 |
| T-14 | A6 | with item 3 | α-spending ledger (item 3 lists it; OD3) | — |
| T-15 | A6 | gated: OD9a | as-of interface cases (a) to (d), oracle (e) on F-25, leak detector | — |
| T-16 | A6 | retired | power of the retired primary and IUT | M-4 |
| T-17 | A1 / A3 | retained in part | membership mutation refused at every stage; registration refused when the record follows e_i (RC-138); registration-breach classification (RC-139, RC-168); VOID requests after registration logged and inert (RC-57, RC-85, RC-87); t*_k over all members; replay of refusals; increment, λ, cap and emission clauses are with item 3 | — |
| T-19 | A1 / A3 | retained in part | merge or VOID citing a dependence refused, declaration defect logged; the archive-linkage sensitivity clause (RC-216) is retired | — |
| T-20 | A4 | with item 3 | shrinkage estimator (item 3; OD9a) | — |
| T-21 | A4 | open | nested-chain identity "in the kernel"; no Phase 1 kernel is named | — |
| T-22, T-26, T-28, T-29 | A4 / A2 | retained | interval-only and point-outside-interval refused; NaN, reversed, out-of-range, missing and duplicate provider refused with typed reasons; issuance held without three providers plus Jev; `predicate_kind` and `cluster_id` mandatory | — |
| T-23, T-24 | A4 | open | second-moment pool, n_eff (item 4 beyond validation) | — |
| T-30, T-31, T-32, T-35 | A5 | retained | every capability case, every crash and demotion interleaving of the four steps, every mutated signed field, fabricated state objects, clock rollback, idle window, reboot, slew | — |
| T-33 | A5 | retained as the denial check | `SHADOW_LIVE_QUOTES` alone denies SIM execution; the halt-time cancellation clause is SIM-phase behaviour (`17` §3 out of scope) | — |
| T-34 | A4 / A5 | gated: OD10 | secret canary over the reachable exception graph | — |
| T-36 | A3 / A6 | with item 3 | kernel positive controls and oracles | M-4 |
| T-37 | A1 / A6 | retained in part | registration without a candidate entry refused; entry after a forecast refused; byte-for-byte replay of the log; report counts equal the log's; every audit, omission, draw, close, schedule, beacon-deadline, universe and supply clause is retired (no draw over Q, issue #3 comment `6298303061`); the beacon-seed refusals of RC-187 apply to the calibration record under M-1 (i) (§4.3) | M-8 (a source-listed population is not Q) |
| T-39 | A3 / A6 | with item 3 | monitor order | M-9 |
| T-40 | A7 | retained | false lemma fails; cache failure is "not verified" | — |
| T-41 | A7 | retained | manifest 71 OK; tree `122a1619…` | — |

### 4.2 Fixtures of `17` §5.1 and controls of §3 item 6

| Fixture | Status | Note |
|---|---|---|
| F-01, F-03, F-04, F-05, F-06, F-07, F-08, F-09, F-10, F-13, F-19, F-21, F-21b | retained | backdating, early NO, non-hex digest, phantom, replay, suffix rehash, anchor and ledger replaced together, gate replay, direct construction, fusion inputs, predicate lint, publication gap, expiry gap |
| F-02a to F-02e | retained | all five dispositions; the F-02c box-rule clause is with item 3 |
| F-24 | retained in part | pre-declared VOID members outside the population and in the audit (A, B); adjudication from both late records with both requests in the VOID audit (C); adjudicated VOID at finality under a failed source (D, E); t*_k exclusion (F); empty FULL slot recorded as an abstention, member without a committed base rate refused, baseline submission and pre-close read refused (G); the request at 0.5 changes no state; emission, cap and imputation clauses are with item 3 |
| F-27 | retained in part | registration refusals against the arm version record and e_i; breach classification; correction before the first registration replaces the version; own-cutoff forecast refused; composite effective cutoff (RC-156); box-rule and non-confirmatory clauses are with item 3 |
| F-25 | gated: OD9a | as-of oracle (T-15) |
| F-12 | gated: OD10 | error context canary (T-34) |
| F-11 | Phase 7 | unchanged (RC-42) |
| F-14, F-17, F-18 | open | n_eff, correlation weights, constant bias (item 4 beyond validation) |
| F-20 | with item 3 | floor inversion (shrinkage, T-20) |
| F-15, F-16, F-26 | with item 3 | cloned outcomes, clustered null, monitor order (M-9) |
| F-22, F-23 | retired | macro-shock and time-varying generators of the retired primary; `18` M-1 to M-3 state the laws of 𝓛 and the out-of-class control for the simplified method |
| Item 6 controls not listed as fixtures: truncated and suffix-rehashed ledgers, simultaneous ledger-and-anchor replacement, clock rollback, cluster membership mutation, concurrent submissions and concurrent presentation of one capability, replayed, forged, expired, wrong-environment and wrong-release capabilities, NaN, reversed and out-of-range inputs | retained | T-06, T-07, T-17, T-18, T-26, T-30, T-31, T-35 |
| Partial-cluster update attempts (λ recomputed after a partial resolution) | with item 3 | T-17 increment clauses |
| Valid-null, clustered-null and interleaved-null e-process generators | with item 3 | T-10, T-11 |
| Forbidden-future-information leak detector | gated: OD9a | T-15 second line |
| Secret canaries in logs, structured errors and the reachable exception graph | gated: OD10 | T-34 |

### 4.3 `18` §7 M-1 to M-9: what of each is Phase 1

| M | Phase 1 part | Not Phase 1 |
|---|---|---|
| M-1 | the record invariants of (i): a calibration record names exactly one claim, the claim's anchored pre-registration names the record, both anchors precede the record's beacon round, a second record for a cohort is refused, a seed other than SHA-256(anchored record ‖ v) or one computed before the round is published is refused (the RC-187 refusals of T-37, carried to the calibration record; selection among records is the S17 invalid control), every bound claim is reported; Phase 1's one confirmatory register, anchored with S_max before the beacon round of any calibration record bound to any Phase 1 claim, listing the confirmatory claims by identifier, a claim's status never changing (RC-304, RC-309, RC-311, RC-315). With OD11 (b) S_max counts families and a family binds its order, every 𝓛_j and cutoff and one report | the cutoff c_𝓛, its certification, refusal and fresh-size checks ((i) second half, (ii) to (v)) |
| M-2, M-3, M-4, M-6, M-7 | none | kernel size, power, familywise error and identified set |
| M-5 | the slot state: an event of Q with no FULL forecast by its issuance close is recorded as an abstention (RC-109) | scoring the abstention at the baseline forecast |
| M-8 | the pre-registration registry refuses, as non-confirmatory, a cohort whose population is a source listing rather than Q | — |
| M-9 | none | the monitor and its crossings |

The amendment of `17` §3 item 3 and §6 (OD11 (b)) carries M-1 to M-9 in full; Codex reviews it at its exact SHA.

## 5. Open owner fields

Phase 1 code leaves each as a named `OWNER_DECISION` field; none is chosen here.

- **Owner actions named in comment `6297828986`:** done on 2026-10-20: the "Confirmed" reply (`6297969313`), the
  merge of PR #4 into `research/claude-handoff` (`f68a222`) and of PR #1 into `main` (`b2e6cbf`). Remaining: the merge
  of this document; the OD9a PR (gates the point-in-time store and T-15); OD10 (gates T-34 and the secret-handling
  code); the amendment of `17` §3 item 3 and §6 (one document, one review).
- **OD11 (b), fields of the amendment** (`18` §6, §9; Codex `4326311683`, `4326311701`, `4326311717`): the holder
  of Q and its fixing date; period length, G and G_min; δ; the validity class 𝓛 of each fixed-sequence component
  with its generative rationale, out-of-class sensitivity analysis and refusal policy; the estimand weighting
  (RC-69, `18` F10); the family order; S_max; the calibration size, budget and beacon; the deterministic selection
  rule with tie-breakers and feasibility thresholds, anchored before the design cohort; the design-cohort and
  burn-in dates. Closed on 2026-10-20 by issue #3 comment `6298303061` (clarification of OD11 (b), same delegation):
  Q is never subsampled, no event draw over Q is built in any phase, and beacon-seeded sampling serves the
  calibration record only.
- **OD3:** α_total for promotions (T-14, with item 3).
- **OD4 fields the retained schemas carry as values:** the VOID cap and the abstention cap per arm, H_max, d_max,
  the timestamp that assigns a cluster to a calendar block (RC-129); M_late, K_max, the null-class box and γ_cal
  lapse under (b) (`18` §9).
- **OD5, per source:** occurrence-time rule, latency window, failure condition, monotone-publication condition,
  observation duty at finality, `falsifier_observable_from`, defect-closure horizon D_s; the named beacon and
  whether a fallback beacon is pre-registered (RC-208).
- **OD6:** the production holder of the `AnchorStore` (Phase 1 uses the harness-owned double, RC-34).
- **OD8:** the model knowledge cutoff each provider declares per model version (RC-98).
- **OD9b:** the designated author and committer identities for T-09 (RC-81); the `AGENTS.md` §2 item 3 wording
  (RC-84); the reading of §7 on reviewer names (RC-28).
- **Specification questions raised in review, for the owner (none applied):**
  - PR #19 deviation 6 (findings `4329369309`, `4329659300`, `4329659293`): the bounds applied are "claim,
    calibration record and register recorded before `period_start`"; whether the claim's own record must also be
    anchored before the period, and by which anchor cadence, is not stated (RC-304 names the anchor for the
    calibration record and the register, not for the claim).
  - PR #19 round-3 finding `4329836229`: the anchor that makes a listed claim confirmatory may be published after
    the claim's evaluation period; whether the covering anchor's publication must precede every listed claim's
    `period_start` is the same anchor-before-period question.
  - PR #19 deviation 7 (finding `4329369285`): the calibration record names one beacon round in advance; the
    alternative, a deterministic rule such as "the first round published after the record's anchor", needs the
    beacon's round schedule, which no record carries.
  - PR #18 round-4 finding `4329838021`: under the monotone-publication condition the earliest late record among
    those submitted is taken as proof that nothing matched at finality, while the registry holds only what was
    submitted; RC-113 makes the condition the source rule's promise (OD5), and whether an archived read must
    accompany the record is for the owner.
  - PR #26 round-1 finding `4333446625`: the Jev record's `inputs_digest` should be bound to the inputs Jev
    triaged, so that a stale record with the right `event_id` cannot make an issuance issuable; `17` names the
    field but not the input bundle it is taken over (the research outputs, the evidence, or the prompt). Once the
    bundle is defined, the fix in `cpe/validation/issuance.py` is one expected-digest argument and one comparison.
- **Not assigned by OD1 (§3.1 to §4.1):** the fusion pool and n_eff (T-23, T-24, F-14, F-17, F-18); the
  nested-chain identity (T-21); the source withdrawal rule of RC-169; the SIM-phase clause of T-33.
- **Branch base:** this document is written on `8d5dbb9` (R9), while the decision comment reads `62d4c2a` (R8);
  `17` is identical at both and the R9 change is carried (§1); `main` at `b2e6cbf` contains `8d5dbb9`.

## 6. Reproduction commands

Source identity (run here on `8d5dbb9`; outputs as stated in §1):

```sh
git rev-parse 8d5dbb9 62d4c2a
git rev-parse 8d5dbb9:research/17-phase1-amended-specification.md
git rev-parse 8d5dbb9:research/18-method-reassessment.md
git rev-parse 62d4c2a:research/18-method-reassessment.md
git diff --quiet 62d4c2a 8d5dbb9 -- research/17-phase1-amended-specification.md && echo "17 identical"
git rev-parse 8d5dbb9:research/original/CPE_Forschungspaket_2026-10-16
(cd research/original/CPE_Forschungspaket_2026-10-16 && sha256sum -c MANIFEST.sha256 | grep -c ': OK')
```

Evidence scripts of `16` and `18` (`research/reproduction/README.md`; not run for this document):

```sh
python -m venv /path/to/venv && /path/to/venv/bin/pip install --require-hashes --no-deps -r research/reproduction/requirements.txt
cp -r research/original/CPE_Forschungspaket_2026-10-16/08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/source_v0_2 /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/check_appendix_scripts.py --reference-code /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/reassessment_sims.py
```

The pinned environment is Python 3.11.17 with `requirements.txt` (numpy 2.4.6, scipy 1.17.1); `18` §10 records
the R9 run. The archived reference tests are reproduced outside the repository as `00-research-inventory.md` §4
describes. Phase 1 code adds its own commands in its PRs (`AGENTS.md` §6: every reported number reproducible from
committed code by a command named in the PR).

## 7. No-execution boundary

- Offline and synthetic only: no network, no provider, no model adapter, no Jev client, no broker, no SIM, no
  credential, no paid API, no real event, no money (comment `6297828986`; `AGENTS.md` §3; `17` §3 "Explicitly out
  of scope").
- No statistics kernel (`17` §3 item 3), no audited-source or late-link control, no T-34 or secret-handling code
  until OD10, no point-in-time store or T-15 until the OD9a wording is merged into `AGENTS.md` (`17` A0).
- No edit of `research/original/`, `16`, `17` or `18`; no governance change; no change to risk policy; no merge
  and no push to `main` (`AGENTS.md` §3, §4, §9, §11).
- No weakening of a safety or risk control to pass a test; a failing safety test is a finding (`AGENTS.md` §3).
- Dependencies pinned with hashes in project files and installed in a virtual environment outside the
  repository; the reproduction scripts are evidence, never imported by project code
  (`research/reproduction/README.md`).
- No AI attribution marking in commits, PRs, comments, code or docs: no attribution trailer, session link,
  promotional footer or badge; required provenance lives in content (`AGENTS.md` §7).
- Every PR reports what was run with its output; nothing is claimed that was not run (`AGENTS.md` §8, §12).

Build order after the merge of this document (the Phase 1 brief): small PRs against `main`, one component each,
starting with schemas plus the ledger, replay and the restore test, then CI; the simplest code that passes the
mapped tests; every deviation listed in the PR description; Codex reviews each PR, at most two fix rounds.

## 8. What was run and what was not

**Run** (2026-10-20, on `8d5dbb9`): the `git rev-parse` and `git diff --quiet` commands of §6, with the values of
§1; `sha256sum -c MANIFEST.sha256` on the archived package, 71 OK; the version-label check of
`research/reproduction/check_appendix_scripts.py` on the matrix, the specification and `research/README.md` after the
reading-order entry for this document was added, run from the repository root as

```sh
python3 -I -c "
import sys; sys.path.insert(0, 'research/reproduction')
import check_appendix_scripts as c
print(c.version_failures(c.MATRIX.read_text(encoding='utf-8'), c.SPEC.read_text(encoding='utf-8'), c.README.read_text(encoding='utf-8')))"
```

which printed `[]` (no failure; Python 3.13.16, no third-party package needed, the full checker and its evidence
scripts not run).

**Not run:** the evidence scripts of `16` and `18`; any Phase 1 code (none exists); any test of `17` §5 (all
rows remain "not implemented").

**Next responsible agent.** Codex: one review of this document at its exact commit. Factual errors are fixed; every
other finding is listed for the owner in the PR description. The owner: the merge of this document, after which
Phase 1 code starts.

## 9. Phase 1 hardening list

Every Codex finding raised on a follow-up PR, or on a component after its follow-up PR was open, one line each
with this session's assessment: **defect** (a fix with a failing-then-passing test is possible and worth its
code), **specification question** (the finding asks for text that `17`, `18` or an owner decision does not give),
or **not worth its code** (the path is far-fetched or the fix costs more than it prevents). Nothing here is
applied: follow-up PRs take no fix rounds, and the owner decides what, if anything, a later PR carries. Findings
raised on a component PR before its follow-up was open are recorded in that PR's description and were applied in
the follow-up (PR #16 round 3 in PR #20; PR #17 rounds 3 and 4 in PR #22; PR #18 rounds 3 and 4 in PR #21 but for
the two above; PR #19 round 3 in PR #23). Written 2026-10-20 at the heads PR #20 `21d2b63`, PR #21 `26163e2`,
PR #22 `fcffeaf`, PR #23 `2e4a72c`; later findings are appended by the PR that lists them.

### 9.1 Ledger follow-up (PR #20)

- `4329707438` (P1), `4329707419` (P2), `4329707427` (P2): the pending anchor row deleted on a refused publish
  (lost publication time, replaced published row, memory and disk disagreeing). **Decided by the owner and
  applied in `0166f6b`**: a pending row is never deleted because a publish was refused or failed, since a refusal
  does not prove the store did not commit; open-time reconciliation against a reachable store settles it (the
  store holds it: a local anchor) or clears it (the store provably lacks it); the attempt is staged in a separate
  `pending_anchors` table; the high-water mark is reloaded from disk after every outcome. (Corrected 2026-10-21
  per PR #24 review finding `4330128201`: this line first read "pending rows are never deleted", which overstated
  the decision.)
- `4329904090` (P2): a retry after a store that committed the anchor and then reported a timeout republishes
  and records the retry's `published_at`, while an idempotent store keeps the original, so the local copy names a
  publication time at which nothing was published externally. **Defect**: when `anchors()` already holds the
  prefix and digest, settle the pending row with the external anchor's time instead of publishing again (a few
  lines in `Ledger.anchor()`, one test with the harness store).

### 9.2 Adjudication follow-up (PR #21)

- `4330044547` (P1): with `occurrence_is_public_act`, an occurrence before finality whose publication follows
  finality is now `late` (the partition of `4329664911`), so the public knowability at the occurrence is lost for
  eligibility and a forecast received after the public occurrence stays eligible. **Specification question**: the
  partition applied RC-105 and RC-88 as the owner accepted (deviation 9 of PR #18); RC-146 makes the public
  occurrence a knowable time; which of the two stamps t*_k when they disagree is not stated. A defensive reading
  (keep the disposition, take the public occurrence for the knowable time) is possible if the owner wants it.
  **Decided 2026-10-21 by the owner's delegate** (with PR #24 review finding `4330128194`) as a reading of RC-146
  with RC-88: the publication partition decides the disposition, which stays immutable, and `knowable_at` is the
  earliest of the evidenced publication, the public-act occurrence and logical finality, so a public occurrence
  sets `knowable_at` even when its record is published late. Applied in H1 (PR #27), tested on this finding's
  case (occurrence 90, publication 118, finality 110: `RESOLVED_NO`, `knowable_at` 90).
- `4330044561` (P1): among several timely public-act records, selection by publication order can choose a later
  occurrence's knowable time (occurrence 95 published 100 over occurrence 90 published 105), against RC-146's
  "earliest". **Defect**: partition by publication, select the deciding timely record by its knowable time.
- `4330044572` (P2): `classify_forecast` labels a forecast eligible when its receipt equals the registration time,
  on the reading that the ledger sequence put the registration first; a caller of the pure function cannot show
  that from timestamps alone. **Not worth its code** on the registry path, where `submit_forecast` refuses a
  forecast before the registration record exists, so no forecast-first pair at one timestamp reaches the ledger;
  if the pure function is ever called with other inputs, a sequence argument is the fix.
- `4330044580` (P2): when a failed status and an absence observation coexist, the status decides VOID while the
  recorded receipt is the observation's. **Defect**: pass the status receipts through and record the deciding
  status's receipt (the registry already keeps them on replay).
- `4330044588` (P1): the `observation_receipts` input of the pure `adjudicate` is not checked against
  `observed_at <= receipt <= now`, as resolution-record receipts are. **Defect** of the pure function's contract,
  two comparisons; on the registry path the ledger guarantees both bounds (submission refuses an observation
  after the clock, the clock never runs below a receipt).

### 9.3 CI follow-up (PR #22)

- `4330035931` (P2): the trailer check matches keys ending in `-by` only (`Tested: Bob` passes) and exempts
  `Reviewed-by:` whatever its value. **Defect** against `AGENTS.md` §10 ("no trailers of any kind except
  `Reviewed-by:` naming a human"): parse the trailer block and refuse every key but `Reviewed-by`; whose name counts
  as human is the open OD9b field (RC-28), so the value check beyond the assistant-name list is a **specification
  question**.
- `4330035940` (P2): `from os.path import *` and a relative `from .os import *` are reported as star imports of
  `os`. **Defect** (a false positive fails CI): keep `ImportFrom.level` and match the module `os` exactly.
- `4330035947` (P1): `import os.path` binds the local name `os` but yields no alias, so `os.system(...)` through it
  passes the process-use check, a regression of PR #22 against the earlier implementation. **Defect**: an
  unaliased dotted import of `os` binds `os`.
- `4330035955` (P2): a line opening with "Generated by" is a promotional footer whatever follows, so ordinary
  provenance prose ("Generated by make_fixture.py ...") is refused. **Not worth its code**: the structural match
  was the owner's choice in `4329652621` (any such line is a finding), a false positive is visible in the T-09 job
  and reworded, and narrowing the match reopens the gap that finding closed.

### 9.4 Registration follow-up (PR #23)

Written 2026-10-20 as "none at `2e4a72c`"; Codex's automatic review of `2e4a72c` arrived after the stop point:

- `4330096692` (P2): a directly constructed `CandidateEntry` with a naive `listed_at` raises `TypeError` in the
  comparison with the ledger clock instead of the refusal `naive_timestamp`. **Defect**: validate the entry through
  its payload before the decision.
- `4330096714` (P1): `listed_at` is compared with the decision's clock sample, not with the receipt the append
  assigns; a clock that moves back between the two, above the high-water mark, admits an entry received before
  its listing time. **Defect**, the same root as PR #25's `4333434011`: a ledger append that checks a predicate
  against its own receipt closes both.
- `4330096680` (P1), `4330096701` (P1): replay of a ledger written by the release before PR #23 (a consumer
  registered after its input's withdrawal; two claims naming one calibration record) is not repaired. **Not worth
  its code**: both need a ledger from a release that never shipped; no such ledger exists outside the tests.

### 9.5 Hand-off update (PR #24)

Codex's review of `188a1e1`:

- `4330128184` (P1): predicate evaluation against archived resolution content is not gated on OD9a, which
  governs the as-of feature store keyed by `available_at`. **Specification question (the reading of a gate)**,
  decided below.
- `4330128194` (P1): `4330044547` is a defect, not a specification question: RC-146 defines `knowable_at` as the
  earliest of the three times, while RC-88 keeps only the disposition immutable. Decided with `4330044547` (§9.2).
- `4330128201` (P2): §9.1 overstated `0166f6b` as "pending rows are never deleted". **Factual correction**,
  applied in §9.1.

### 9.6 Offline capability model (PR #25)

Codex's automatic review of `050ff07`, after the two fix rounds:

- `4333626167` (P1): with two gates on one ledger, a lower commit can follow a higher commit that is written but
  not yet anchored, and replay lowers the gate without a rotation. **Defect**.
- `4333626175` (P1): a reboot or slew discontinuity between steps 3 and 4 is not seen before the acknowledgement.
  **Defect**.
- `4333626183` (P2): a rollback at the append's own clock sample is refused by the ledger but not logged by the
  gate. **Defect**.
- `4333626186` (P2): `ACTIONS` is a mutable module dictionary. **Defect**.
- `4333626188` (P2): a faulty time source writes an unvalidated reading that replay later refuses. **Defect**.
- `4333626194` (P1): a start-up abort decided on a snapshot can land after another gate's commit, and replay
  refuses the ledger. **Defect**.

### 9.7 Input validation (PR #26)

- `4333446625` (P1, round 1): bind the Jev record to the digest of its triaged inputs. **Specification question**,
  in §5.
- `4333728786` (P2, review of `4c8ed14`): a cyclic JSON value raises `RecursionError` instead of a refusal; the root
  is `cpe/canonical._check_json`, shared by every schema that accepts free JSON. **Defect**.
- `4333728777` (P1, review of `4c8ed14`): names commit `ee355e5` with Codex's identity; the object is not in this
  repository and the PR's commits carry the designated identity. **Not a defect**: the review-checkout identity,
  the OD9b pattern of PR #17's `4329073542`.

### 9.8 Decisions of 2026-10-21

The owner's delegate (the parent session of the Phase 1 work) triaged §9.1 to §9.7 on 2026-10-21, after PR #26.
One hardening pass, three PRs against `main` at `2122567`, one Codex review each and no fix rounds:

| Finding | Decision | Where |
|---|---|---|
| `4329904090` | fix: settle a retried anchor from the store's existing anchor | H1, PR #27 |
| `4330044561` | fix: the deciding timely record is the earliest knowable | H1, PR #27 |
| `4330044547`, `4330128194` | fix as the reading of RC-146 with RC-88 recorded in §9.2 | H1, PR #27 |
| `4330044580` | fix: a status-decided VOID records the status receipt | H1, PR #27 |
| `4330044588` | fix: receipts given to the pure `adjudicate` are bounded | H1, PR #27 |
| `4333728786` | fix: `cpe/canonical` refuses cyclic values | H1, PR #27 |
| `4330096692` | fix: a naive listing time is a refusal | H1, PR #27 |
| `4330096714`, `4333434011` | fix: `Ledger.append` checks a predicate against its own receipt, used by the candidate log and the capability gate | H1, PR #27 |
| `4333626167`, `4333626175`, `4333626183`, `4333626186`, `4333626188`, `4333626194` | fix | H2, PR #28 |
| `4330035947`, `4330035940` | fix | H3 |
| `4330035931` | fix: parse the trailer block, refuse every key but `Reviewed-by`; whose name counts as human stays OD9b | H3 |
| `4330128201` | factual correction of §9.1 | H3 |
| `4330128184` | predicate evaluation is not gated on OD9a; the resolution-content archive and its evaluator are a separate component, scheduled independently of the OD9a-gated point-in-time feature store (§3.1; corrected after `4334268792`) | H3 (this text) |
| `4333446625` | specification question for the owner (§5) | H3 (this text) |
| `4330035955`, `4330044572` | not fixed: not worth their code, as assessed in §9.2 and §9.3 | — |
| `4330096680`, `4330096701` | not fixed: need a ledger from a release that never shipped | — |
| `4333728777` | not fixed: the review-checkout identity, OD9b pattern | — |

Findings Codex raises on H1, H2 and H3 are listed in their descriptions and appended below.

### 9.9 Hardening PRs (H1 to H3)

- H1 (PR #27, `dd8af3f`, merged at `5c0cbf6` on green CI and the parent session's verification): Codex's review
  never returned (requested 2026-10-21 07:02 UTC, still "running" at 08:02 UTC). It was not re-requested (one
  review per hardening PR); a late finding is appended here by whoever reads it.
- H2 (PR #28, `336b970`), `4333981363` (P1): remove the reviewer's name from the docstring of
  `tests/test_hardening_h2.py` as an AI marking. **Not a defect**: naming the review a regression test answers is
  the provenance `AGENTS.md` §7 requires ("which finding it addresses"); the owner confirmed this reading for the
  same finding on PR #16 (`4329259263`) and PR #18 (`4329442698`).
- H3 (PR #29, `898ec19`), `4334268788` (P2): the trailer parse requires whitespace after the colon, while git
  accepts `Tested:Bob` as a trailer, so a prohibited key written without the space passes. **Defect**: accept the
  form without whitespace (`[ \t]*`), or delegate to `git interpret-trailers --parse`. Not fixed (no fix rounds on
  the hardening PRs).
- H3 (PR #29, `898ec19`), `4334268792` (P1): §3.1 says predicate evaluation is not gated on OD9a but is built
  "together with the point-in-time store", which stays gated on OD9a until its `AGENTS.md` wording is merged; read
  literally, the decision re-gates it. **Specification question for the owner's delegate**: whether the archive of
  resolution bytes is separable from the OD9a-gated as-of feature store, so that predicate evaluation can be
  scheduled on its own. **Decided by the owner's delegate on 2026-10-21: separable.** The resolution-content
  archive and its evaluator are their own component, not gated on OD9a, scheduled independently of the
  point-in-time feature store, which stays gated on the OD9a wording. §3.1 and §9.8 are corrected accordingly
  (a correction of the decision text, not a fix round). `4334268788` stays listed for the next code PR that
  touches `tools/check_provenance.py`.
