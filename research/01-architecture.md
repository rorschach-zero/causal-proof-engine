# 01 Architecture

Entry point for the proposed v0.2 architecture (`02/01`, English original `EN/CPE_v0.2_REVISED_SPEC.md`) and
the architecture review of this session. §1–§2 summarise the original; §3–§5 are review.

## 1. The original proposal in one page

**Central object.** The Proof-Carrying Causal Bet (PCCB, `ref/docs/RFC.md` §0): a typed, versioned research
object with eight parts (origin, mechanism, events, belief, value_capture, adversarial_case, decision,
audit_trail). v0.2 keeps the eight parts and makes "belief" consist only of registered event forecasts.

**Pipeline** (`02/01` §1):

```
sources → ingest log (observer-signed first_observed_at, archived bytes, SHA-256, publication-lag table)
       → Jev triage (mandatory; complement-pair-checked noul questions; escalation score)
       → three independent researchers, round 1 blind (typed PCCB fragments: mechanisms with
         identification class, EventSpecs, interval forecasts)
       → coherence layer (credal network = Design B on the research graph; exact credal LP = Design A
         on ≤ 14 decision events) → fused intervals, ABSTAIN / RE_RESEARCH decisions
       → registry + anchored ledger (commit before outcome) → e-process monitors, calibration maps, ablations
       → value-capture model → scenario set → robust allocation (max-min log growth, caps, worst loss)
       → certificate → gate state machine → Saxo SIM read-only → precheck → (SIM execution) →
         (shadow live quotes) → [LIVE blocked]
```

**Four principals** with separate OS accounts and secrets (`02/01` §2): Researcher (model calls, ingest,
append-only registry writes), Promoter (frozen holdouts, deterministic acceptance script, promotion records),
Executor (broker tokens, certificates, precheck/orders), Owner (gate HMAC secret, anchor store, one-step gate
promotion, LIVE release).

**Data layer** (`02/01` §3): ingest log with `available_at := max(published_at, first_observed_at)`;
publication-lag table per source family (backtests must shift by it; sources without an entry are excluded);
point-in-time investable universe from monthly Saxo `/ref` snapshots with every considered candidate logged
(`invest | reject | uninvestable | watch`) and three shadow books.

**Forecast layer** (`02/01` §4): `EventSpec` (statement, resolution source, machine-checkable predicate,
`resolves_not_before`, `expires_at`, grading-rule version; vague words rejected) and `Forecast` (`as_of`,
`known_at`, interval, forecaster + version, evidence ids, reasoning digest, `abstained`; width > 0.5 counts as
abstention). Mechanism objects carry an identification class; only logical links enter probability math.
Designs A/B/C as described in `03-probability-and-causal-modeling.md`. Fusion as in
`05-multi-model-orchestration.md`.

**Allocation, crisis policy, self-improvement, security** are summarised in `07-portfolio-and-risk.md`,
`06-self-improvement-and-evaluation.md` and §2 below. **Gates and Saxo** in `08-saxo-integration.md`.

**Longevity** (`02/04`): immutable core (ledger format, registry schema, evaluation protocol, gate rules, risk
limits, principal separation, the three-models-plus-triage obligation) versus evolvable shell (prompts,
extractors, graph templates, calibration maps, model choice). Model replacement is a routine four-step path:
shadow → proof (committed e-process vs incumbent) → promotion → retirement. Annual anchored report; annual
restore test on a fresh machine; dead-man switch demoting the gate if anchor checks lapse.

**Asset-class extension** (`02/05`): a new class is treated like a new model and needs five artefacts
(instrument model, Lean loss bound, data and lag table, broker proof over 60 SIM days, capital threshold).

## 2. Security architecture as proposed (`02/01` §9)

Secrets in the OS credential store per principal; redaction filter on all model-bound text; executor accepts
only a certificate `{certificate_id, instrument, amount, limit, gate_state, ledger_head_hash,
promoter_signature}` and re-checks anchor and gate before each call; daily ledger anchor to a store the
researcher cannot write; per-principal egress allow-lists; idempotency via `ExternalReference = certificate_id`
and a fresh `x-request-id` per attempt; kill switch via `Gate.demote()` and a heartbeat watchdog; every broker
call logged with body digest, never the token.

## 3. Review: confirmed defects in the reference code (CONFIRMED-DEFECT)

The reference code is explicitly "not to be implemented as-is" (`08_Anhang/README.md`), but it is the only
executable statement of the design, and the package's 31 tests are cited as evidence that the P0 fixes work.
These probes (run in this session on a scratch copy; script in the session record) show behaviour the tests
do not cover. They are design inputs for whoever writes the real code.

| # | Component | Observed behaviour | Why it matters |
|---|---|---|---|
| P1 | `ref/cpe/registry.py` `resolve()` | A YES outcome resolved **after** `expires_at` is graded `RESOLVED_YES`. | The EventSpec contract says "if not YES by `expires_at` → NO". Late-YES grading inflates the skill of long-horizon optimists. Must be `EXPIRED_NO` (or the resolver must prove the criterion was met before expiry). |
| P2 | `ref/cpe/registry.py` | State is in-memory only; a new `ForecastRegistry` on the same ledger file knows no events. There is no replay from the ledger. | "Ledger-backed" is currently write-only. The ledger must be the source of truth with deterministic replay, otherwise the immutable history and the operating state can diverge silently. |
| P3 | `ref/cpe/registry.py` vague-word guard | Checks only `resolution_predicate`, only whole words; `potentially`, `could-be` pass; `statement` is unchecked. | A word list is a lint, not a guarantee. Resolution predicates need a small, machine-checkable grammar (source, field, comparator, value, date bound), see `11-proposed-improvements.md` R3. |
| P4 | `ref/cpe/fusion.py` | Weights come from the error **correlation** matrix; with uncorrelated errors of standard deviation 0.02 (one model) vs 0.30 (two models) the weights are 0.344 / 0.332 / 0.323. | The minimum-variance pool should use the error **covariance**; the current rule down-weights redundancy but ignores accuracy. A consistently better model gets no extra weight. |
| P5 | `ref/cpe/saxo_sim.py` `Gate` | `Gate(GateState.SIM_EXECUTION)` constructs a promoted gate directly; the tests themselves do this. | In-process, the gate is advisory. The safety property "no precheck or order without an owner-authorised state" cannot hold inside one process; it must be enforced by a separate executor principal that reads gate state from the anchored ledger and verifies the owner MAC itself. The spec says so (`02/01` §2, §9); the code cannot demonstrate it and the tests do not try. |
| P6 | `ref/cpe/allocation.py` | A total-loss scenario (`R = −1`) is accepted and yields `w ≈ 0`. | Edge case behaves sensibly. No action. |

Additional observations (not probed, from reading):

- `CommittedEProcess` and `ForecastRegistry` each have their own commit concept and are not connected. The
  e-process must be fed from registry resolutions, in resolution order, with the registry as the only writer.
- The ledger's `anchor(secret)` HMAC requires the owner secret at anchoring time. If the daily anchoring task
  runs under the researcher account, the secret is exposed there and the HMAC adds nothing; if it runs under
  the owner account, the HMAC is redundant because the anchor store is already outside the researcher's write
  permission. Either the anchor is an owner-side operation (then drop the HMAC and keep the store separation)
  or the anchoring uses an external timestamp authority. The threat model T1–T5 is good; the mechanism should
  be one, not two half-measures.
- `AppendOnlyLedger.append()` reads the whole file to find the tail; acceptable for a prototype, quadratic over a
  25-year ledger. Design note for the real store (segment files with a head pointer, or an embedded append-only
  database with an export path).
- The Jev credential guard (`accountkey`, `bearer `, …) is a string heuristic; it must be a structural rule
  (only whitelisted fields of the archived evidence record are ever serialised toward any model).
- The λ rule in text and code differ in clip order (`00-research-inventory.md` §5 item 6).

## 4. Review: architecture-level findings

1. **The measurement apparatus is well specified; the discovery engine is not.** Registry, ledger, e-process,
   fusion and gates are defined to the field level. The part that produces candidate events in the first
   place, the "sector-independent first-principles scanner", is a paragraph (`RFC` §2 step A, `02/01` §1) and a
   list of example source families. No source list, no licensing review, no parser plan, no estimate of event
   yield per source. The year-one target of 600 registered events (`03/05` §3) is therefore unsupported. This is
   the largest unresolved architectural decision.
2. **Independence of the three models is assumed, not engineered.** Round-1 blindness is enforced by
   "separate prompts and no shared context", but all three read the same evidence bundle prepared by the same
   ingest and triage path, with prompts of the same authorial style. Error correlation measured after the fact
   (`n_eff`) is a diagnostic, not a design. See `05-multi-model-orchestration.md` §3.
3. **The OpenAI owner-started daily batch** (`02/03`) introduces a human into the research loop. That is a
   latency cost (acceptable at 1–9 month horizons) and a contamination channel: the owner sees items before
   forecasts are committed. The protocol needs a rule that the owner never edits, filters or comments on items in
   the batch, and the batch log must be hashed into the ledger.
4. **Gate state has no durable home.** The gate is a Python object. It must be a ledger record type
   (`gate_promoted`, `gate_demoted`) with the owner MAC stored, and the executor must derive the current state by
   replaying the anchored ledger, never from process memory or a config file.
5. **Four principals on one Windows workstation** is a reasonable start but the separation claims (no import of
   the executor from research code, per-account egress rules) are operating-system configuration, which CI
   cannot test. The spec's "static gate: no module under `cpe/` imports the executor" is a package-structure test
   and should be the first CI check written.
6. **Hazard indicators are US-centric** (HY OAS, SLOOS, NFCI, VIX term structure) for a Swiss investor on a
   global universe. Either justify (US credit cycle leads global risk assets) or add region-matched inputs.
7. **The crisis policy's strongest rule ("never force-liquidate thesis-intact positions") is a prior, not a
   tested hypothesis.** H6 tests only the throttle. See `07-portfolio-and-risk.md` §4.
8. **Complexity budget.** The v0.2 design has about twelve interacting components before a single event is
   registered. The package's own build order (`07/02` §B) is right: registry + ledger, SIM read-only, ingest +
   Jev, Design C, adapters + fusion, monitors, credal net + hazard, allocator + certificates, promoter, SIM
   execution. The roadmap (`12-roadmap.md`) keeps that order and names what is explicitly deferred.

## 5. Unresolved architectural decisions (carried to `09-open-questions-and-decisions.md`)

Source families and licences for the scanner (N1); grammar of resolution predicates (N2); durable store for
ledger and registry (N3); anchoring mechanism (N4); gate state as ledger records and executor replay (N5);
how round-1 blindness is enforced and logged (N6); Design A vs B selection criteria (D2, after 150 resolutions);
reference distribution choice (`03/01` §2); α-budget vs false-discovery-rate control (`02/04` §4); provider
access routes and their terms (Q2); point-in-time universe source (Q5); Windows-only vs containerised runtime
(`02/04` §4 asks for containers or lockfiles; `07/01` is Windows-specific).
