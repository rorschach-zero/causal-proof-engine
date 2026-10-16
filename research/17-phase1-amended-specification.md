# 17 Amended Phase 1 specification and acceptance-test matrix (PROPOSED)

Jointly reviewable specification of the offline, synthetic-data measurement apparatus that both reviews
recommend as the only work to approve next. It amends `12-roadmap.md` Phase 1 with the dispositions in
`16-reconciliation-matrix.md` and Codex's exit criteria (`15-codex-review.md` §H). Status: **PROPOSED**,
version 2 (round 2: amended for the thirteen findings of Codex's review of PR #4 at `10d1581`, items RC-28 to
RC-40 in `16` §3a), awaiting Codex round 3 and owner decision OD1. Nothing is implemented; no roadmap phase is
approved by this document. REVISION throughout unless labelled otherwise.

## 1. Objective

Reduce scientific and engineering uncertainty about the measurement apparatus with synthetic data only, so
that a later, separately authorised Phase 2 can register real events under a protocol whose validity has been
demonstrated adversarially. No network, no providers, no broker, no Jev client, no hosting decision, no learned
components, no real event.

## 2. What changes relative to `12-roadmap.md` Phase 1

| `12` Phase 1 said | Amended to | Reason (matrix ID) |
|---|---|---|
| e-process consumes resolutions in ledger order | one increment per pre-declared outcome cluster; server receipt time; fixed-horizon cluster-robust paired test as secondary | RC-01, RC-02 |
| `EXPIRED_NO` for late YES | YES iff occurrence met the deadline (evidence of occurrence time required, declared latency window); early NO only when logically final; four timestamps | RC-11 |
| anchor detects any byte change | any change in the anchored prefix or truncation below it; unanchored window reported | RC-13 |
| covariance-based fusion weights | input validation first; equal weights default; second-moment simplex pool behind a flag, synthetic evaluation only | RC-06, RC-15 |
| gate records with owner MAC | capability records with owner public-key signature, environment, release digest, evidence digest, epoch, nonce, expiry; consumed-authorization store | RC-12, RC-14 |
| e-process false alarm ≤ α + 0.015 over seeds | one-sided 95 % Monte Carlo upper bound ≤ 0.06 on each valid-null family, plus an invalid-null control that must exceed it | RC-01, RC-24 |
| power study for N8 | power and protocol report with clusters, missingness and abstention; Phase 2 statistical contract drafted for OD4 | RC-24 |
| no interval-scoring decision | one scored point probability; interval as declared ambiguity set; scorer rejects interval-only forecasts | RC-05 |
| (not present) | shrinkage estimator replacing the base-rate floor, with property tests; built only after OD9a changes `AGENTS.md` §2 item 7 | RC-03, RC-33 |
| (not present) | cluster closure rule: immutable membership, single increment after every member is resolved or pre-declared VOID, λ locked at the cluster's first outcome receipt | RC-29 |
| anchors as owner-side records | anchor store outside the writer's control (separate principal); local-only anchors reported as self-attested | RC-13, RC-34 |
| (not present) | monotonic high-water-mark clock persisted in the ledger; capability checks fail closed on clock rollback | RC-37 |
| (not present) | α-spending ledger and IUT evaluation in the statistics kernel | RC-08 |
| (not present) | provider-neutral attribution check on commit and PR text in CI | RC-26 |
| time-shifted holdout in tests | forbidden-future-information leak detector | RC-09 |

## 3. Scope (build)

1. **Schemas.** `EventSpec` with typed resolution predicate (source, record selector, field, comparator, value,
   not-before, not-after), `cluster_id`, `predicate_kind ∈ {milestone-deadline, terminal-falsifier}`, four
   timestamps (occurrence, publication, receipt, adjudication), latency window. `Forecast` with one scored
   point probability, declared ambiguity interval (low ≤ point ≤ high), forecaster id and version, prompt and
   model hashes, evidence ids. `JevRecord` (inputs, both polarities, model hash, routing result, cost).
   `Capability` (owner-signed: capability, environment, release digest, evidence digest, epoch, nonce,
   expiry). `ResearchOutput` JSON schema for future adapters. `Cluster` registration record.
2. **Ledger and registry.** Single transactional writer (SQLite in one process) with canonical JSONL export;
   server receipt time on every admission; append atomic with state change (no phantom records);
   deterministic replay of registry, cluster, capability and e-process state; anchor = committed-prefix
   digest with an explicit unanchored-window report; restore from a clean checkout in CI.
   *Anchor trust boundary (RC-34).* A digest only detects tampering if the copy it is compared against cannot
   be rewritten by the ledger writer. Anchors are therefore emitted through an `AnchorStore` interface whose
   production implementation is held by a principal other than the writer (owner-held signed record, or an
   append-only store the writer has no credential for; which one is part of OD6). In Phase 1 the external
   store is a test double that the writer cannot open for writing (separate directory with a different OS
   principal in CI, or an in-memory store owned by the test harness), plus an export of every anchor as a
   record the owner can commit to Git. Verification against a local anchor copy is reported as
   **self-attested**, never as verified; the restore test names which anchor it verified against.
   *Monotonic clock (RC-37).* The ledger persists the maximum receipt time it has ever observed; any admission
   or capability check whose current time is below that high-water mark fails closed and is logged.
3. **Statistics kernel.** E-process consumer fed only by registry resolutions, one increment per outcome
   cluster, predictable λ (archived GRAPA rule, λ_max = 0.5), running maximum; fixed-horizon cluster-robust
   paired Brier comparison at pre-registered cut-offs; proper scores (Brier, log clipped at a pre-registered
   bound); IUT evaluation over a declared comparator set; α-spending ledger; shrinkage estimator for rare
   probabilities (Beta posterior for cohort data, logit shrinkage of a model estimate with a pre-registered
   weight function; built only after OD9a, see A0).
   *Cluster closure (RC-29).* A cluster's member list is immutable from its registration record onward and
   must be complete before the earliest `not_before` of any member; an EventSpec that names a cluster after
   that point is rejected, and an EventSpec registered without a cluster is its own singleton cluster. The
   cluster emits exactly one increment, X̄ over its members, and only when every member is resolved or was
   pre-declared VOID before any member's outcome was received; a cluster with an unresolved member emits
   nothing. The betting fraction λ_k for cluster k is computed from the increments of clusters closed before
   the **first outcome receipt** of any member of k and is frozen at that moment, so that no information from
   a partially resolved cluster enters its own λ. Increments enter the e-process in order of closure time. A
   dependence discovered after registration between members of different clusters is adjudicated by VOIDing
   the later cluster for betting (recorded, never silently merged). This rule closes the within-cluster
   channel only: if two clusters are open at the same time and their outcomes are dependent (a macro shock),
   the product of their factors is not a test supermartingale under any ordering rule, which is the RC-01
   open point (`16` §4.1) and the reason the fixed-horizon cluster-robust test is retained beside the
   e-process.
4. **Fusion (baseline only).** Input validation (finite, 0 ≤ low ≤ point ≤ high ≤ 1), mandatory-input check
   (three providers plus Jev record), typed decisions, equal weights; second-moment simplex pool behind a
   flag, evaluated on synthetic data only; n_eff as a diagnostic with the degenerate-history case flagged.
5. **Capability model (offline).** Signature verification with the owner's public key; epoch, nonce,
   expiry, environment and release checks; consumed-authorization store; demotion persistence; state replayed
   from the ledger; no network path exists. Expiry is checked against both the current clock and the
   persisted high-water mark (item 2): a check whose current time is below the high-water mark, or whose
   capability expired at any time at or below the high-water mark, fails closed (RC-37).
6. **Negative controls and fault injection (permanent in the test suite).** Every fixture in §5.1 (the B4
   counterexamples of `15-codex-review.md` and the probes P1–P5 of `01-architecture.md` §3, restated here so
   that this document is complete without the review branch, RC-35); valid-null, clustered-null and
   interleaved-null e-process generators with exact binomial Monte Carlo bounds; forbidden-future-information
   leak detector; backdating; phantom-on-failure; replayed, forged, expired, wrong-environment, wrong-release
   capabilities; NaN, reversed and out-of-range inputs; truncated and suffix-rehashed ledgers; simultaneous
   ledger-and-local-anchor replacement; clock rollback; cluster membership mutation and partial-cluster
   update attempts; concurrent submissions; secret canaries in logs, exception contexts and structured error
   paths.
7. **Power and protocol report.** Reproduce the D1 table with an independent recurrence check; extend to
   clustered outcomes, missingness and abstention; publish the detectable effect at 300 and 600
   independent-equivalent units; draft the Phase 2 statistical contract (§6).
8. **CI.** Pinned direct and transitive dependencies with hashes; Python 3.11 and 3.13; strict type checking;
   property tests; Lean job on the pinned toolchain for the retained lemmas including a deliberately false
   proof that must fail, with a network or cache failure reported as "not verified", never as pass;
   provider-neutral check of commit and PR text for attribution trailers; `research/original/` verified by
   manifest and excluded from all tooling; static check that no research module imports the executor
   package (useful, not sufficient: dynamic paths are covered by T-34).

**Explicitly out of scope.** Credal network and every credal-set LP (including the inner worst-case LP of
RC-10; its test moved to §7, RC-32), hazard model, allocator and cost model, provider adapters, Jev client, SIM
read-only, any hosting or cloud identity, self-improvement loop, any learned calibration, any real event, any
change to `AGENTS.md` (OD9 is the owner's; OD9a is a prerequisite of A0, not part of this scope).

## 4. Acceptance criteria (all must hold)

| # | Criterion | Codex §H exit criterion it satisfies |
|---|---|---|
| A1 | Replay of any valid synthetic history equals online state byte for byte; injected append failure, process death, concurrency, truncation and clock rollback produce no acknowledged phantom record; restore from a clean checkout reports the anchored prefix and the unanchored window | H3 |
| A2 | Every B4 counterexample and every probe P1–P5 is rejected or correctly graded, with a named test per case; backdated submissions cannot become prospective evidence | H4 |
| A3 | Clustered-null, interleaved-null and valid-null simulations: exact one-sided 95 % binomial (Clopper–Pearson) upper bound on the crossing rate ≤ 0.06 at α = 0.05 for the cluster-level process over ≥ 2,000 replications per family; per-event betting on clustered data is retained as the invalid-null control and must exceed it (RC-31) | H6 |
| A4 | All malformed, non-finite, incoherent or incomplete research inputs rejected across the property-test domain; no silent dropping or duplicate-provider overwrite | H2 |
| A5 | Forged, replayed, expired, wrong-environment, wrong-release capability records rejected; demotion survives restart; no in-process constructor creates an elevated state; no offline proof is described as deployed isolation | H5 |
| A6 | Power and protocol report reviewed, seeds and generators committed; detectable effect at 300 and 600 independent-equivalent units; Phase 2 contract drafted for OD4 | H6 |
| A7 | CI green including the Lean known-false rejection and malformed-certificate tests; dependency lock reproducible; attribution check present; `research/original/` unchanged by manifest | H7 |
| A8 | Independent review by a reviewer other than the author; owner acceptance of scope; local green tests alone do not satisfy merge policy | H8 |
| A0 | Owner decisions OD1, OD2 and OD9a (the `AGENTS.md` §2 item 7 and item 10 wording, which the shrinkage estimator and the leak detector would otherwise contradict, RC-33) recorded before implementation starts; until OD9a is recorded, T-20 and T-15 are not built and the floor is neither built nor removed; OD3–OD5 recorded before the Phase 2 contract is frozen | H1 |

## 5. Acceptance-test matrix

Each test is a CI check or a reviewed artefact. "Fixture" names the synthetic generator or counterexample.
Status for all rows: **not implemented** (Phase 1 not approved).

| Test | Criterion | Fixture / generator | Pass condition | Matrix IDs |
|---|---|---|---|---|
| T-01 | A2 | event and forecast with `known_at` years in the past, submitted now | rejected; receipt time is the server clock; `known_at` stored as an audited caller claim | RC-02 |
| T-02 | A2 | forecast submitted after the cluster's first outcome receipt | rejected for betting; retained as a labelled late forecast | RC-01, RC-02 |
| T-03 | A2 | YES with occurrence time before the deadline, observed after it within the latency window | graded YES | RC-11 |
| T-04 | A2 | YES with occurrence time after the deadline; NO before the deadline on an eventually-by-deadline predicate; NO on a logically final predicate | EXPIRED_NO; rejected (not final); RESOLVED_NO | RC-11 |
| T-05 | A1 | injected write failure during registration, commit, resolution and capability change | no state change; no acknowledged record; replay equals pre-failure state | RC-12 |
| T-06 | A1 | process killed between write and acknowledgement; two concurrent submissions of the same id | at most one durable record; replay deterministic | RC-12 |
| T-07 | A1 | ledger edited inside the anchored prefix; truncated below the anchor; suffix rewritten after the anchor | first two detected; third reported as "unanchored window of n records", never as verified | RC-13 |
| T-17 | A1 / A3 | cluster membership mutation after the cluster's first outcome receipt; EventSpec naming a closed cluster; increment requested while one member is unresolved; λ recomputed after a partial resolution | all rejected; no increment emitted until every member is resolved or pre-declared VOID; λ_k equals the value frozen at first outcome receipt; replay reproduces the same closure order | RC-29 |
| T-18 | A1 | ledger history rewritten **and** the local anchor copy replaced consistently | detected against the external `AnchorStore` double; the local-only check reports "self-attested" and the restore test fails if only a local anchor is available | RC-34 |
| T-08 | A1 | clean checkout in CI, laptop and a container job | identical replayed state digest in all three | RC-20 |
| T-09 | A7 | commit message and PR body containing attribution trailers, session links, promotional footers | CI check fails; clean text passes | RC-26 |
| T-10 | A3 | 120 clusters × 5 events, shared fair outcome per cluster, 2,000 replications, archived λ rule | cluster-level crossing rate upper bound ≤ 0.06; per-event rate recorded and > 0.06 (invalid-null control) | RC-01 |
| T-11 | A3 | same events in a random interleaved order | per-event rate still > 0.06; cluster-level rate within bound | RC-01 |
| T-12 | A3 / A6 | fixed-horizon cluster-robust paired Brier test on the same generators | nominal size on the valid null within the Monte Carlo bound; power reported beside the e-process | RC-01 |
| T-13 | A6 | (a) deterministic oracle: fixed vectors of component p-values or e-values, including exactly one component at the boundary; (b) least-favourable null: one comparator exactly null, all others at a strong alternative, 20,000 replications, α = 0.05 | (a) conjunction rejects iff every component rejects, bit-exact against the oracle; (b) exact one-sided 99 % binomial upper bound on the rejection rate ≤ 0.06 (a correct level-α test passes with probability ≥ 0.9999; a test of size 0.06 passes with probability ≈ 0.01, of size 0.07 never; REPRODUCED, `16` §2) | RC-08, RC-30 |
| T-14 | A6 | α-spending ledger with pre-registered sequence | cumulative spend never exceeds α_total; a promotion attempt after exhaustion is refused and logged | RC-08 |
| T-15 | A6 | feature containing the outcome injected into a synthetic challenger | leak detector flags inflation above the pre-registered bound; shuffled-label null distribution reported | RC-09 |
| T-16 | A6 | D1 generator rows (b ∈ {0.2, 0.5}, δ grid) plus clustered and missingness variants | counts reproduce D1 within Monte Carlo error; detectable effect stated at 300 and 600 units | RC-24 |
| T-20 | A4 | cohort (s, n) with reference-class prior; model estimate outside the cohort range | shrinkage output monotone in s, within [0, 1], ordered low ≤ point ≤ high; no floor applied; no rounding | RC-03 |
| T-21 | A4 | nested chain with declared conditionals | arithmetic identity P(E) = P(E\|D)P(D\|C)P(C) holds to numerical tolerance in the kernel; no LP in Phase 1 (the linear-constraint form moves to §7 with T-25) | RC-04, RC-32 |
| T-22 | A4 | interval-only forecast; point outside its interval | both rejected by the scorer and the schema | RC-05 |
| T-23 | A4 | orthogonal-error fixture (sd 0.02 / 0.30 / 0.30); constant-bias fixture | second-moment pool ≈ (0.991, 0.004, 0.004) and down-weights the biased model; equal weights returned when the flag is off | RC-06 |
| T-24 | A4 | identical varying histories; constant duplicate histories | n_eff = 1.25 reported with a "degenerate history" flag on the constant case; n_eff appears in no decision path | RC-07 |
| T-26 | A4 | NaN, reversed, > 1, missing provider, duplicate provider | rejected with typed reasons; no equal-weight fallback on invalid input | RC-15 |
| T-27 | A4 | hand-built payload bypassing the typed builder; NaN price; non-multiple lot | not constructible or rejected before any transport object exists | RC-15 |
| T-28 | A4 | fused forecast with two providers or no Jev record | issuance held; no two-of-three fallback | RC-17 |
| T-29 | A2 | EventSpec without `predicate_kind` or `cluster_id` | rejected | RC-19, RC-01 |
| T-30 | A5 | valid capability replayed after demotion; after expiry; with a stale epoch; with a consumed nonce | all rejected; demotion state read back after restart | RC-12 |
| T-31 | A5 | capability signed with a non-owner key; wrong environment; wrong release digest | rejected | RC-12 |
| T-32 | A5 | direct construction of an elevated state object from research code | impossible by type (no public constructor) or detected by the static check | RC-12 |
| T-33 | A5 | capability set with `SHADOW_LIVE_QUOTES` only | SIM execution denied; reconciliation and authorised cancellation allowed during halt | RC-14 |
| T-34 | A4 / A5 | synthetic secret canary in headers, request objects, nested exceptions, structured errors, encoded (base64, URL) forms | canary absent from logs, exception contexts and error payloads | RC-15 |
| T-35 | A5 | host clock rolled back after an unused capability expired; clock rolled back below the persisted high-water mark during an admission | capability rejected (expiry evaluated against the high-water mark); admission fails closed and is logged; high-water mark survives restart | RC-37 |
| T-40 | A7 | Lean job with a deliberately false lemma; job run with the Mathlib cache unreachable | false lemma fails; cache failure reported as "not verified" and the job is red | `04-formal-verification.md` |
| T-41 | A7 | `research/original/` manifest and Git tree object | `sha256sum -c MANIFEST.sha256` reports 71 OK; `git rev-parse HEAD:research/original/CPE_Forschungspaket_2026-10-16` equals `122a1619cdad4f1c7f577e26f86709c34ce86298` (the value at the reviewed head `8b2dba7`, unchanged at `10d1581` and at this commit; the tree object also detects added or renamed files, which the manifest does not) | integrity, RC-40 |

### 5.1 Mandatory counterexample fixtures (restated, RC-35)

Each fixture is reproduced against the archived v0.2 reference code by `16` Appendix A (REPRODUCED) or by
`15-codex-review.md` Appendix 1 (REPRODUCED by Codex). The Phase 1 implementation must reject or correctly
grade every one; the fixture, not the review document, is the acceptance input.

| Fixture | Input (synthetic) | Reference-code behaviour | Required Phase 1 behaviour | Test |
|---|---|---|---|---|
| F-01 backdating | event and forecast dated 2020-01-01, submitted today | accepted | rejected; receipt time is the server clock | T-01 |
| F-02 late YES | outcome YES resolved 10 days after `expires_at`, no occurrence time | `resolved_yes` | YES only with evidence that occurrence met the deadline within the declared latency window; otherwise `EXPIRED_NO` | T-03, T-04 |
| F-03 early NO | NO resolved 2 days into a 30-day eventually-by-deadline predicate | `resolved_no` | rejected (not logically final) | T-04 |
| F-04 non-hex digest | 64-character reasoning digest `'z' × 64` | accepted | rejected (hex, fixed length) | T-26 |
| F-05 phantom | `append` raises during `register_event` | event remains in memory | no state change, no acknowledgement | T-05 |
| F-06 no replay | new registry on an existing ledger | zero events known | state derived by replay equals online state | T-05, T-06 |
| F-07 suffix rehash | last record edited and `entry_hash` recomputed after the anchor | verifies | reported as unanchored window; never "verified" | T-07 |
| F-08 anchor and ledger replaced together | history rewritten and local anchor copy regenerated | (no external anchor exists) | detected against the external anchor store | T-18 |
| F-09 gate replay | valid promotion record re-used after demotion; caller supplies the signing key | promoted again | rejected (consumed nonce, stale epoch); key never caller-supplied | T-30, T-31 |
| F-10 direct construction | `Gate(SIM_EXECUTION)` built in-process (probe P5) | passes precheck | no public constructor for elevated state; static check | T-32 |
| F-11 payload bypass | hand-built `Cfd` payload, amount −1; NaN price; 11 units at lot size 10 | reaches transport / accepted | not constructible; rejected before any transport object | T-27 |
| F-12 error context | `raise … from None` after an HTTP error with a synthetic bearer header | header present in `__context__` | canary absent from exception context, logs and structured errors | T-34 |
| F-13 fusion inputs | NaN, reversed [0.8, 0.2], [1.2, 1.3] intervals | `forecast` | rejected with typed reasons | T-26 |
| F-14 n_eff | three constant identical histories; three identical varying histories | 3.0; 1.25 | "degenerate history" flag; 1.25 reported as diagnostic only | T-24 |
| F-15 cloned outcomes | 30 pairs (0.25 vs 0.75) sharing one fair outcome | e = 475.0986 or 1.0; crossing probability 0.5 | one cluster, one increment; crossing probability within the A3 bound | T-10 |
| F-16 clustered null | 120 clusters × 5 events, shared fair outcome, archived λ rule, 2,000 replications | 33.4 % per-event crossings; 13.5 % interleaved | per-cluster crossing rate with exact upper bound ≤ 0.06; per-event rate recorded as the invalid-null control | T-10, T-11 |
| F-17 correlation weights (probe P4) | orthogonal errors, sd 0.02 / 0.30 / 0.30 | weights 1/3 each | equal weights by default; second-moment pool ≈ (0.991, 0.004, 0.004) behind the flag | T-23 |
| F-18 constant bias | model 1 biased by 0.20, models 2–3 unbiased sd 0.05 | covariance-only weight 0.935 on the biased model | second-moment pool weight ≈ 0.036 on it | T-23 |
| F-19 predicate lint (probe P3) | predicate text "potentially excellent" | passes the word list | rejected by the typed predicate grammar | T-29 |
| F-20 floor inversion | interval [0.001, 0.01] with base rate 0.02 | [0.02, 0.01] | no floor; shrinkage output ordered low ≤ point ≤ high | T-20 |

## 6. Phase 2 statistical contract (draft, to be frozen only after OD3–OD5)

| Field | Draft value | Decision needed |
|---|---|---|
| Estimand | difference in expected Brier between FULL and Design C per outcome cluster, averaged over the pre-registered eligible-event population **that resolves to YES or NO**; the VOID rate is a reported co-primary quantity with a pre-registered cap above which the primary estimate is declared uninterpretable (RC-38) | cap value: OD4 |
| Sampling unit | pre-declared outcome cluster | none |
| Primary test | cluster-level committed e-process, α = 0.05, λ_max = 0.5, running maximum; secondary fixed-horizon cluster-robust paired test at cut-offs 12 and 24 months after first cohort entry | none |
| Smallest useful effect | to be set | OD4 |
| Planned supply | measured on a **blinded burn-in cohort** in Phase 2 months 1–3: events are registered and forecasts committed, but no outcome of a burn-in event is unsealed before the contract is frozen, and burn-in clusters are permanently excluded from the primary test (RC-39); only counts, cluster sizes and source metadata inform OD4–OD5 | OD5 |
| Confirmatory conjunction | IUT over {Design C, each single provider, single-provider-three-roles, equal-weight committee} | none |
| Missing data | VOID excluded from the primary (estimand above) and counted against the cap; sensitivity = worst-case bounds in both directions, imputing each VOID with the outcome least favourable to FULL (Y = 1 where p_FULL < p_baseline, else Y = 0) and then most favourable, reported as an interval around the primary (a single imputation such as "VOID as NO" is not conservative: with p_FULL = 0.1 and p_baseline = 0.9 it adds +0.8 to the paired increment, Y = 1 gives −0.8; REPRODUCED, `16` §2); a pre-registered missingness model only if the VOID mechanism is documented per source; abstentions scored at the baseline forecast and reported separately (RC-38) | none |
| Stopping rule | anytime-valid for the e-process; fixed horizon for the secondary; futility declared if the detectable effect at measured supply exceeds OD4 | OD4 |
| Promotion budget | α-spending sequence per RC-08 | OD3 |

## 7. Tests specified now and built in later phases

**Credal LP (Phase 5, RC-10, RC-32).** T-25: small exact credal instance; the inner LP over the whole declared
credal set returns a worst case ≤ any sampled-subset worst case; conditional bounds enter as linear constraints
l·P(A) ≤ P(A ∩ B) ≤ u·P(A) with declared zero-mass semantics. Not part of Phase 1 (§3, out of scope).

**Evaluator side channels (Phase 6).** Exfiltration canaries in evaluator-only data; logs, crash dumps,
telemetry and parser errors scanned for canaries; bounded feedback (pass/fail plus coarse diagnostics); cap on
adaptive proposals per period; evaluator and scorer are separate processes so a submitted artefact never
receives labels; no executable deserialisation or template evaluation of artefacts.

## 8. Size and review

One Python package, no services, no message queue, no cloud SDKs, SQLite plus JSONL, a few thousand lines
including tests. Independent review of the Phase 1 code by Codex (author: Claude) or by Claude (author:
Codex), per `AGENTS.md` §9; owner acceptance of A8. Nothing in Phase 1 is architecture that Phase 2 would
have to remove under any hosting choice (OD6).
