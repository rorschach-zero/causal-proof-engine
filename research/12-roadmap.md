# 12 Initial implementation roadmap

A proposal (REVISION) for what would be built, in what order, with what exit criteria, **if and only if** the
Codex review and the owner approve. It follows the dependency order the package itself gives (`07/02` §B) and
the ten-step sequence in `07/01`, adjusted by the findings in this review. No phase authorises trading
execution, broker credentials in code, or orders of any kind. Every phase ends with an independent review.

## Phase 0: research foundation (this pull request)

Deliverables: verbatim archive, English foundation documents, governance (`AGENTS.md`, `CLAUDE.md`), attribution
controls. Exit: Codex review completed against `13-codex-review-checklist.md`; owner confirms or amends D1–D13;
N1 (source families) and N12 (runtime) answered. **No code.**

## Phase 1: measurement apparatus, offline, synthetic data only

Build the smallest set of components that make anything afterwards evaluable. Pure Python, typed, tested,
no network, no providers, no broker.

| Component | Content | Review items applied |
|---|---|---|
| Ledger | append-only store with segment files or SQLite-append and canonical JSONL export; anchors as owner-side records; replay API | R1, N3, N4 |
| Registry | EventSpec with typed resolution predicate (grammar v1), Forecast, statuses, deterministic resolver interface, `EXPIRED_NO` for late YES, full replay from ledger | R4, R5-prep |
| E-process | consumes registry resolutions in ledger order; predictable λ; running-max rejection; replay equals online | R3 |
| Gate | ledger record types `gate_promoted` / `gate_demoted`; derivation by replay; no in-memory authority | R2 |
| Fusion | covariance-based minimum-variance weights, non-negativity fallback, typed decisions, width decomposition | R8, R7 |
| Schemas | JSON schema for `ResearchOutput`, `EventSpec`, `Forecast`, `JevTriage`, `Certificate` | schema first |
| Tests and CI | unit and property tests (anchor detects any byte change; replay invariants; e-process false alarm ≤ α + 0.015 over several seeds; fusion RE_RESEARCH on any missing input); static gate "no research module imports the executor"; log scan for `Bearer `; Python 3.11 and 3.13; Lean job on the pinned toolchain for the kept lemmas | `04/03` §6 |
| Restore test | rebuild all state from the ledger on a clean checkout; part of CI | `02/04` §7 |
| Power study | simulation report for N8; year-one criterion proposal | N8 |

Exit criteria: CI green; restore test green; power report published; independent review (Codex) of the code;
amendments N7, N9, N10, N11 recorded. Estimated size: a few thousand lines including tests. Deliberately not
built: credal net, hazard model, allocator, adapters, Jev client, anything that talks to a network.

## Phase 2: ingest, Jev triage, Design C, first registered events (owner actions interleaved)

Owner actions first (none of them code): create the Saxo SIM application; request Jev early access; read and
archive provider terms (Q2); choose three source families from the N1 profiles; schedule the monthly anchor
check.

| Component | Content |
|---|---|
| Ingest log | archived bytes, SHA-256, observer-signed `first_observed_at`, `available_at`, source family, publication-lag table entries with evidence; three source families only |
| Jev adapter | typed client against the archived OpenAPI, both polarities, complement gap, retries, token ceiling, structural (not string) credential guard; initial 200-document calibration run; one pre-registered threshold amendment (R12) |
| Design C | cohort base rates for the chosen event classes where free data exist; otherwise explicit "no floor" |
| Event registration | first 100 events registered by hand under the `HUMAN` forecaster id with the eligibility rule pre-registered (R21); Design-C baseline forecasts committed |
| Supply measurement | events per source family per week; lags measured against the table |

Exit: ≥ 100 registered events with Design-C forecasts committed; anchors verified from a second machine;
supply rate consistent with the year-one plan or the plan revised; independent review.

## Phase 3: SIM read-only (executor principal) — first external broker action

Separate OS principal and process; token from the OS credential store; `/port` and `/ref` readbacks;
reconciliation report; monthly universe snapshot and candidate log started (R20); 72-hour PKCE refresh test
(Q1); Q3/Q6/Q7 answered empirically. Gate promoted RESEARCH_ONLY → SIM_READ_ONLY by owner MAC recorded in the
ledger. Exit: 7 consecutive days of readbacks; Q1 answered; independent review including a token-leak audit.
Phases 2 and 3 can run in parallel; they share nothing but the ledger.

## Phase 4: three-model adapters and fusion in operation

Adapters for Claude (Max API credits), Gemini (per terms) and OpenAI (owner batch, constrained per R11), each
against the `ResearchOutput` schema; per-item blinding records (N6); model configuration pinned per call (R15);
fusion live; primary e-process started against Design C; ablation forecaster ids registered (including
`single-model-three-roles`, R10); reasoning-overlap metrics (R9). Exit: three independent round-1 outputs per
event, schema-valid, no cross-reading evidenced by blinding records; first 50 fused forecasts committed;
independent review.

## Phase 5: evaluation, credal net, hazard model, allocator, certificates (no orders)

After ≥ 100 resolved events: reliability diagrams; A vs B ablation; identification-class skill table (R5);
hazard model on vintage data as an exploratory H6; scenario grammar and allocator producing certificates that
are checked in exact arithmetic (R13); SIM_PRECHECK promoted by owner MAC; 30 prechecks with cost fields
archived; cost model as a component. Exit: 150 resolved events; design selection recorded; independent review.

## Phase 6: promoter and self-improvement

Only when there is something to improve and frozen holdouts exist: promoter principal with environment pinning
(R17), canary namespace (R16), rolling prospective holdouts (R18), e-value combination rule (R19), degradation
action rule. Exit: first promotion or rejection recorded end to end; independent review.

## Phase 7: SIM execution — separate release, separate review

Order placement in SIM only, with idempotency, cancel path, reconciliation, kill switch and fault injection;
Codex second review required before merge (`07/01` step 9). Exit: 60 days, zero duplicate orders, every fill
reconciled. Shadow live quotes afterwards. **LIVE remains blocked throughout this roadmap.** A LIVE pilot of at
most USD 1,000 is a separate programme decision requiring the gates in `01/01` §5, an independent security and
risk review of the order path, and the owner's written approval.

## What this roadmap deliberately does not contain

Trading execution outside SIM; broker credentials in any file; derivatives, margin, shorts "for testing";
optimisation against live account data; a licensed point-in-time dataset (Q5 decision); any claim about returns
before Phase 5 has data.

## Amendments after the Codex review (REVISION, 2026-10-16)

Recorded after reconciliation round 1 (`16-reconciliation-matrix.md`); the text above is left as written.

1. **Phase 1 table is superseded** by `17-phase1-amended-specification.md`, which carries the amended scope,
   acceptance criteria A0–A8 and the acceptance-test matrix. The differences are listed in `17` §2.
2. **"Anchor detects any byte change" (RC-13)** is an overclaim: a rewritten and rehashed suffix after the last
   anchor passes verification (REPRODUCED). The correct property is "any change inside the anchored prefix,
   and truncation below it"; the restore test reports the unanchored window explicitly.
3. **"`EXPIRED_NO` for late YES" (RC-11)** is replaced by the temporal semantics in `17` §3 item 1.
4. **Phase 0 exit** additionally requires: Codex round 2 on the reconciliation commit, and owner decisions
   OD1–OD2 (`16` §6). N12 (runtime and hosting) is answered at the Phase 2 gate, not in Phase 0 (RC-20).
5. **Phase 2** starts point-in-time universe and candidate logging at the first authorised research ingest, not
   at the first SIM readback (Codex R20 amendment), and adds the stratified Jev-reject audit (RC-17).
6. **Phase 0 exit, round 2 (RC-33).** Implementation of the shrinkage estimator and the leak detector
   additionally requires OD9a (`AGENTS.md` §2 items 7 and 10 wording), because both would otherwise contradict
   binding product requirements; `17` A0 lists OD1, OD2 and OD9a as prerequisites. Phase 2 months 1–3 are a
   blinded burn-in cohort excluded from the primary test (RC-39).
7. **Phase 0 exit, round 3 (RC-49, RC-50).** "Primary e-process started against Design C" in Phase 2 is
   superseded: the primary confirmatory test is the fixed-horizon paired cluster test with a pre-registered
   dependence model, and the e-process runs as the anytime-valid monitor of the conditional null (`17` §6).
   Codex round 3 on `43754cc` is processed in `16` §3b; the round budget of issue #3 is spent for RC-01 and
   RC-15, so Phase 0 exit now waits on owner decisions OD1, OD2 and OD9a, not on a further review round.
8. **Phase 0 exit, round 4 (RC-56 to RC-63).** Codex's review of `d46c204` is processed in `16` §3c: the
   primary test has a single 24-month cut-off, power is stated for the primary test itself, every signed
   capability field is mutated in T-31, and each kernel has a positive control (T-36). RC-60 (the redacting
   holder still stores the secret) is reproduced but not applied because the RC-15 budget is spent (OD10).
   Every item Codex has touched has now used its budget; later automatic reviews are recorded for the owner
   without revision (`16` §4.6). Phase 0 exit waits on OD1, OD2, OD9a and, for T-34, OD10.
9. **Phase 0 exit, round 5 (RC-64 to RC-71, recorded only).** Codex's review of `88abaa4` is recorded in `16`
   §3d without revision. Three findings reproduce against Claude's own earlier remedies (`16` Appendix F): the
   clock watermark must advance on rejected checks too (RC-65), the primary statistic must be cluster-weighted
   with calendar blocks used only for the variance (RC-69), and the round-4 power figure under period shocks
   was computed over 120 periods where the design has 24 (47 % is 18 %, RC-70). The others define partial-VOID
   arithmetic, a maturation rule, membership tests from registration, the late-YES label and the A0/OD10
   conflict. All nine recorded findings (RC-60, RC-64 to RC-71) wait on OD10; Phase 0 exit waits on OD1, OD2,
   OD9a and OD10.
10. **Phase 0 exit, round 6 (RC-72 to RC-79, recorded only; last automatic round).** Codex's review of `4de18e5`
    is recorded in `16` §3e without revision. Five findings reproduce (`16` Appendix G): the primary test's A3
    size bound is a calibration on the specified families, not finite-sample validity (exact size 7.3 % on a
    zero-mean two-point null, up to 15 % on skewed ones; the distribution-free alternative has no power at 24
    blocks, RC-72); neither the clock wording nor its round-5 repair detects an idle window before a rollback
    (RC-73); a nonce consumed after the last anchor is replayable after a restore (RC-74); the scored forecast
    revision is unspecified (RC-75); a NO by expiry is knowable before the source's record (RC-77). Three are
    requirements of `02` §5 and `AGENTS.md` §8 that `17` never carried: a common issuance window and evidence
    cutoff for both arms, which moves the start of the primary cohort to Phase 4 (RC-76); a pre-registered
    inclusion predicate with an audited candidate log (RC-78); point-in-time leakage fixtures and an as-of read
    interface for T-15 (RC-79). All seventeen recorded findings (RC-60, RC-64 to RC-79) wait on OD10. Because
    each record-only push re-triggers a full automatic review of unchanged text, no further round is recorded
    by the routine on its own; Phase 0 exit waits on OD1, OD2, OD9a and OD10.
