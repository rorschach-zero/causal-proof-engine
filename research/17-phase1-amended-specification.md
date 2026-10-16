# 17 Amended Phase 1 specification and acceptance-test matrix (PROPOSED)

Jointly reviewable specification of the offline, synthetic-data measurement apparatus that both reviews
recommend as the only work to approve next. It amends `12-roadmap.md` Phase 1 with the dispositions in
`16-reconciliation-matrix.md` and Codex's exit criteria (`15-codex-review.md` §H). Status: **PROPOSED**,
awaiting Codex round 2 and owner decision OD1. Nothing is implemented; no roadmap phase is approved by this
document. REVISION throughout unless labelled otherwise.

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
| (not present) | shrinkage estimator replacing the base-rate floor, with property tests | RC-03 |
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
3. **Statistics kernel.** E-process consumer fed only by registry resolutions, one increment per outcome
   cluster at the cluster's resolution time, predictable λ (archived GRAPA rule, λ_max = 0.5), running
   maximum; fixed-horizon cluster-robust paired Brier comparison at pre-registered cut-offs; proper scores
   (Brier, log clipped at a pre-registered bound); IUT evaluation over a declared comparator set; α-spending
   ledger; shrinkage estimator for rare probabilities (Beta posterior for cohort data, logit shrinkage of a
   model estimate with a pre-registered weight function).
4. **Fusion (baseline only).** Input validation (finite, 0 ≤ low ≤ point ≤ high ≤ 1), mandatory-input check
   (three providers plus Jev record), typed decisions, equal weights; second-moment simplex pool behind a
   flag, evaluated on synthetic data only; n_eff as a diagnostic with the degenerate-history case flagged.
5. **Capability model (offline).** Signature verification with the owner's public key; epoch, nonce,
   expiry, environment and release checks; consumed-authorization store; demotion persistence; state replayed
   from the ledger; no network path exists.
6. **Negative controls and fault injection (permanent in the test suite).** Every counterexample in
   `15-codex-review.md` B4 and every probe P1–P5; valid-null, clustered-null and interleaved-null e-process
   generators with Monte Carlo bounds; forbidden-future-information leak detector; backdating;
   phantom-on-failure; replayed, forged, expired, wrong-environment, wrong-release capabilities; NaN, reversed
   and out-of-range inputs; truncated and suffix-rehashed ledgers; clock rollback; concurrent submissions;
   secret canaries in logs, exception contexts and structured error paths.
7. **Power and protocol report.** Reproduce the D1 table with an independent recurrence check; extend to
   clustered outcomes, missingness and abstention; publish the detectable effect at 300 and 600
   independent-equivalent units; draft the Phase 2 statistical contract (§6).
8. **CI.** Pinned direct and transitive dependencies with hashes; Python 3.11 and 3.13; strict type checking;
   property tests; Lean job on the pinned toolchain for the retained lemmas including a deliberately false
   proof that must fail, with a network or cache failure reported as "not verified", never as pass;
   provider-neutral check of commit and PR text for attribution trailers; `research/original/` verified by
   manifest and excluded from all tooling; static check that no research module imports the executor
   package (useful, not sufficient: dynamic paths are covered by T-34).

**Explicitly out of scope.** Credal network, hazard model, allocator and cost model, provider adapters, Jev
client, SIM read-only, any hosting or cloud identity, self-improvement loop, any learned calibration, any real
event, any change to `AGENTS.md` (OD9 is the owner's).

## 4. Acceptance criteria (all must hold)

| # | Criterion | Codex §H exit criterion it satisfies |
|---|---|---|
| A1 | Replay of any valid synthetic history equals online state byte for byte; injected append failure, process death, concurrency, truncation and clock rollback produce no acknowledged phantom record; restore from a clean checkout reports the anchored prefix and the unanchored window | H3 |
| A2 | Every B4 counterexample and every probe P1–P5 is rejected or correctly graded, with a named test per case; backdated submissions cannot become prospective evidence | H4 |
| A3 | Clustered-null, interleaved-null and valid-null simulations: one-sided 95 % Monte Carlo upper bound on the crossing rate ≤ 0.06 at α = 0.05 for the cluster-level process; per-event betting on clustered data is retained as the invalid-null control and must exceed it | H6 |
| A4 | All malformed, non-finite, incoherent or incomplete research inputs rejected across the property-test domain; no silent dropping or duplicate-provider overwrite | H2 |
| A5 | Forged, replayed, expired, wrong-environment, wrong-release capability records rejected; demotion survives restart; no in-process constructor creates an elevated state; no offline proof is described as deployed isolation | H5 |
| A6 | Power and protocol report reviewed, seeds and generators committed; detectable effect at 300 and 600 independent-equivalent units; Phase 2 contract drafted for OD4 | H6 |
| A7 | CI green including the Lean known-false rejection and malformed-certificate tests; dependency lock reproducible; attribution check present; `research/original/` unchanged by manifest | H7 |
| A8 | Independent review by a reviewer other than the author; owner acceptance of scope; local green tests alone do not satisfy merge policy | H8 |
| A0 | Owner decisions OD1–OD2 recorded before implementation starts; OD3–OD5 recorded before the Phase 2 contract is frozen | H1 |

## 5. Acceptance-test matrix

Each test is a CI check or a reviewed artefact. "Fixture" names the synthetic generator or counterexample.
Status for all rows: **not implemented** (Phase 1 not approved).

| Test | Criterion | Fixture / generator | Pass condition | Matrix IDs |
|---|---|---|---|---|
| T-01 | A2 | event and forecast with `known_at` years in the past, submitted now | rejected; receipt time is the server clock; `known_at` stored as an audited caller claim | RC-02 |
| T-02 | A2 | forecast submitted after the cluster's first member resolved | rejected for betting; retained as a labelled late forecast | RC-01, RC-02 |
| T-03 | A2 | YES with occurrence time before the deadline, observed after it within the latency window | graded YES | RC-11 |
| T-04 | A2 | YES with occurrence time after the deadline; NO before the deadline on an eventually-by-deadline predicate; NO on a logically final predicate | EXPIRED_NO; rejected (not final); RESOLVED_NO | RC-11 |
| T-05 | A1 | injected write failure during registration, commit, resolution and capability change | no state change; no acknowledged record; replay equals pre-failure state | RC-12 |
| T-06 | A1 | process killed between write and acknowledgement; two concurrent submissions of the same id | at most one durable record; replay deterministic | RC-12 |
| T-07 | A1 | ledger edited inside the anchored prefix; truncated below the anchor; suffix rewritten after the anchor | first two detected; third reported as "unanchored window of n records", never as verified | RC-13 |
| T-08 | A1 | clean checkout in CI, laptop and a container job | identical replayed state digest in all three | RC-20 |
| T-09 | A7 | commit message and PR body containing attribution trailers, session links, promotional footers | CI check fails; clean text passes | RC-26 |
| T-10 | A3 | 120 clusters × 5 events, shared fair outcome per cluster, 2,000 replications, archived λ rule | cluster-level crossing rate upper bound ≤ 0.06; per-event rate recorded and > 0.06 (invalid-null control) | RC-01 |
| T-11 | A3 | same events in a random interleaved order | per-event rate still > 0.06; cluster-level rate within bound | RC-01 |
| T-12 | A3 / A6 | fixed-horizon cluster-robust paired Brier test on the same generators | nominal size on the valid null within the Monte Carlo bound; power reported beside the e-process | RC-01 |
| T-13 | A6 | IUT over a declared comparator set with one comparator under the null | conjunction does not reject; size ≤ α by construction | RC-08 |
| T-14 | A6 | α-spending ledger with pre-registered sequence | cumulative spend never exceeds α_total; a promotion attempt after exhaustion is refused and logged | RC-08 |
| T-15 | A6 | feature containing the outcome injected into a synthetic challenger | leak detector flags inflation above the pre-registered bound; shuffled-label null distribution reported | RC-09 |
| T-16 | A6 | D1 generator rows (b ∈ {0.2, 0.5}, δ grid) plus clustered and missingness variants | counts reproduce D1 within Monte Carlo error; detectable effect stated at 300 and 600 units | RC-24 |
| T-20 | A4 | cohort (s, n) with reference-class prior; model estimate outside the cohort range | shrinkage output monotone in s, within [0, 1], ordered low ≤ point ≤ high; no floor applied; no rounding | RC-03 |
| T-21 | A4 | nested chain with declared conditionals | LP identity P(E) = P(E\|D)P(D\|C)P(C) holds to numerical tolerance; conditional bounds entered as linear constraints | RC-04, RC-10 |
| T-22 | A4 | interval-only forecast; point outside its interval | both rejected by the scorer and the schema | RC-05 |
| T-23 | A4 | orthogonal-error fixture (sd 0.02 / 0.30 / 0.30); constant-bias fixture | second-moment pool ≈ (0.991, 0.004, 0.004) and down-weights the biased model; equal weights returned when the flag is off | RC-06 |
| T-24 | A4 | identical varying histories; constant duplicate histories | n_eff = 1.25 reported with a "degenerate history" flag on the constant case; n_eff appears in no decision path | RC-07 |
| T-25 | A4 | small exact credal instance | inner LP over the whole credal set returns a worst case ≤ any sampled-subset worst case | RC-10 |
| T-26 | A4 | NaN, reversed, > 1, missing provider, duplicate provider | rejected with typed reasons; no equal-weight fallback on invalid input | RC-15 |
| T-27 | A4 | hand-built payload bypassing the typed builder; NaN price; non-multiple lot | not constructible or rejected before any transport object exists | RC-15 |
| T-28 | A4 | fused forecast with two providers or no Jev record | issuance held; no two-of-three fallback | RC-17 |
| T-29 | A2 | EventSpec without `predicate_kind` or `cluster_id` | rejected | RC-19, RC-01 |
| T-30 | A5 | valid capability replayed after demotion; after expiry; with a stale epoch; with a consumed nonce | all rejected; demotion state read back after restart | RC-12 |
| T-31 | A5 | capability signed with a non-owner key; wrong environment; wrong release digest | rejected | RC-12 |
| T-32 | A5 | direct construction of an elevated state object from research code | impossible by type (no public constructor) or detected by the static check | RC-12 |
| T-33 | A5 | capability set with `SHADOW_LIVE_QUOTES` only | SIM execution denied; reconciliation and authorised cancellation allowed during halt | RC-14 |
| T-34 | A4 / A5 | synthetic secret canary in headers, request objects, nested exceptions, structured errors, encoded (base64, URL) forms | canary absent from logs, exception contexts and error payloads | RC-15 |
| T-40 | A7 | Lean job with a deliberately false lemma; job run with the Mathlib cache unreachable | false lemma fails; cache failure reported as "not verified" and the job is red | `04-formal-verification.md` |
| T-41 | A7 | `research/original/` manifest and tree hash | 71 OK; tree hash unchanged | integrity |

## 6. Phase 2 statistical contract (draft, to be frozen only after OD3–OD5)

| Field | Draft value | Decision needed |
|---|---|---|
| Estimand | difference in expected Brier between FULL and Design C per outcome cluster, averaged over the pre-registered eligible-event population | none |
| Sampling unit | pre-declared outcome cluster | none |
| Primary test | cluster-level committed e-process, α = 0.05, λ_max = 0.5, running maximum; secondary fixed-horizon cluster-robust paired test at cut-offs 12 and 24 months after first cohort entry | none |
| Smallest useful effect | to be set | OD4 |
| Planned supply | to be measured in Phase 2 month 1–3 before freezing | OD5 |
| Confirmatory conjunction | IUT over {Design C, each single provider, single-provider-three-roles, equal-weight committee} | none |
| Missing data | VOID counted, excluded from skill, reported; sensitivity with VOID as NO; abstentions scored at the baseline forecast and reported separately | none |
| Stopping rule | anytime-valid for the e-process; fixed horizon for the secondary; futility declared if the detectable effect at measured supply exceeds OD4 | OD4 |
| Promotion budget | α-spending sequence per RC-08 | OD3 |

## 7. Evaluator side-channel tests (specified now, built in Phase 6)

Exfiltration canaries in evaluator-only data; logs, crash dumps, telemetry and parser errors scanned for
canaries; bounded feedback (pass/fail plus coarse diagnostics); cap on adaptive proposals per period;
evaluator and scorer are separate processes so a submitted artefact never receives labels; no executable
deserialisation or template evaluation of artefacts.

## 8. Size and review

One Python package, no services, no message queue, no cloud SDKs, SQLite plus JSONL, a few thousand lines
including tests. Independent review of the Phase 1 code by Codex (author: Claude) or by Claude (author:
Codex), per `AGENTS.md` §9; owner acceptance of A8. Nothing in Phase 1 is architecture that Phase 2 would
have to remove under any hosting choice (OD6).
