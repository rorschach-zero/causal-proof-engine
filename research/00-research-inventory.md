# 00 Research inventory and source map

Scope: everything delivered in `CPE_Forschungspaket_2026-10-16.zip`, what each file is, where it comes from,
what was checked in this session, and the inconsistencies found. Provenance details of the import itself are
in `original/IMPORT_NOTE.md`.

## 1. Package identity

| Item | Value |
|---|---|
| Title (package README) | "Causal Proof Engine (CPE): Forschungspaket zum unabhängigen Review vom 16. Oktober 2026" |
| Author of the research | Claude (Fable 5.1), acting as independent reviewer and co-architect of a v0.1 prototype |
| Commissioned by | the repository owner (named in the package) |
| Input the package reviewed | `CPE_Claude_Independent_Review_2026-10-16.zip` (v0.1 prototype, 20-file manifest); **not included** in this package; v0.1 source was reconstructed here by reverse-applying the shipped diff (see §4) |
| Decision recorded | **REVISE**: no capital, not even the USD 1,000 pilot; measurement apparatus first; LIVE blocked in reference code |
| Language | German chapters (01–07) derived from seven English originals (`EN/*`); reference code and prompts in English |
| Integrity | `MANIFEST.sha256`, 71 entries, all OK in the ZIP and in the repository copy |

## 2. File inventory

Status column: **O** original research text, **D** derived from an English original (German rendering),
**C** reference code or evidence, **=** byte-identical duplicate of another file.

### `README.md` and `MANIFEST.sha256`
| File | Status | Content |
|---|---|---|
| `README.md` | O | decision paragraph, five "hard statements", structure, binding goals, verification recipe, labelling rules |
| `MANIFEST.sha256` | C | SHA-256 of all 71 other files |

### `01_Forschungsergebnisse/` (findings)
| File | Status | Content |
|---|---|---|
| `01_Executive_Summary.md` | D | decision, what was executed, P0/P1 table, approval criteria for SIM_EXECUTION, first step |
| `02_Befunde_v0.1_mit_Reproduktion.md` | D | attack reproduction F1–F10, P0-SCI-01/02, P0-ARCH-01, P0-BRKR-01, P0-STAT-01, P1 and P2 findings, reconciliation with a prior audit |
| `03_Verifikationsprotokoll.md` | D | what was run locally (tests, Lean, secret scan) and what was read externally (Saxo, TypeSafe, provider terms, arXiv), plus an explicit UNVERIFIED list |

### `02_Systemarchitektur/` (architecture)
| File | Status | Content |
|---|---|---|
| `01_Architektur_v0.2.md` | D (from `EN/CPE_v0.2_REVISED_SPEC.md`) | pipeline, four principals, ingest log, publication-lag table, point-in-time universe, EventSpec/Forecast, mechanism objects with identification class, designs A/B/C, fusion, model roles and adapter contract, allocation, crisis policy, self-improvement, security, exact v0.1→v0.2 changes |
| `02_Saxo_Broker_Integration_und_Gates.md` | D | Saxo facts (package-verified), unverified items, gate state machine with promotion evidence, pilot instrument whitelist, unattended-session caveat |
| `03_Modellzugang_Abonnements_Kosten.md` | O (new, supersedes `EN/CLAUDE_REVIEW.md` §8) | subscription-only operating model per provider, OpenAI as owner-started daily batch, budget USD 0 beyond subscriptions plus Jev, quota-bound throughput |
| `04_Langlebigkeit_und_Evolution_25_Jahre.md` | O (new) | immutable core vs evolvable shell, model replacement as routine, α-budget, annual report, restore test, dead-man switch, three kinds of evidence |
| `05_Horizonterweiterung_Assetklassen_und_Forschungsaktualitaet.md` | O (new) | asset-class extension ladder (stages 0–4) with five acceptance criteria, method scanner and method ledger |

### `03_Mathematische_Modelle/` (mathematics)
| File | Status | Content |
|---|---|---|
| `01_Kohaerenz_Credal_Sets_und_Lean.md` | D | credal LP (Nilsson/Walley), reference distribution (not implemented), credal network Design B, no-multiplication rule, the ten compiled Lean lemmas and their meaning |
| `02_E-Prozess_und_sequentielle_Tests.md` | D | test supermartingale, Ville, validity conditions violated by v0.1, `CommittedEProcess` fix, λ rule, residual limits |
| `03_Fusion_korrelierter_Prognosen.md` | D | min-variance pooling on shrunk error correlation, effective model count, interval convex combination, decision table, strategic abstention |
| `04_Allokation_und_Ruinrisiko.md` | D | binary Kelly audit (w* = 0.025 at p = 0.10), cost-unit bug, scenario max-min allocator, pilot risk limits, ruin reporting, target arithmetic |
| `05_Seltene_Wahrscheinlichkeiten.md` | D | no elicitation below 0.05, decomposition, base-rate floor, discrimination-only evaluation for two years |
| `06_Krisen_Hazard_Modell.md` | D | leading inputs, BOCPD/logistic hazard, four-case separation, hysteresis actions, H6 falsifier, crisis backtest set |

### `04_Wissenschaftliche_Begruendung/` (scientific justification)
| File | Status | Content |
|---|---|---|
| `01_Originalitaet_und_Stand_der_Forschung.md` | D | established vs novel table, what "causal" would require, designs A/B/C comparison, forecast requirements, regimes and counterfactuals |
| `02_Hypothesen_und_Falsifikation.md` | D (from `EN/SCIENTIFIC_EXPERIMENTS.md` §1) | H0–H6 with falsifiers, north star as non-test object |
| `03_Experimente_Baselines_Ablationen.md` | D | scoring, seven baselines, leakage controls, anti-reward-hacking, ablation arms, CI thresholds, year-one outcomes |
| `04_Nordstern_und_Etappenziele.md` | O (new) | 100x arithmetic (hit-rate tables), what is not a goal, staged milestones, early stop criterion |

### `05_Quellen/` (sources)
| File | Status | Content |
|---|---|---|
| `01_Quellenverzeichnis.md` | O | 38 sources with access date and verification status (A Saxo, B TypeSafe, C model access, D statistics, E Lean, F Swiss tax, G review inputs) |
| `typesafe_openapi_2026-10-16.json` | C, = `evidence/typesafe_openapi_2026-10-16.json` | archived live OpenAPI document of api.typesafe.ai (title TypeSafe, version 0.2.0; endpoints `GET /v1/models`, `POST /v1/systemone`; 20 schemas) |

### `06_Offene_Probleme_und_Risiken/` (open problems)
| File | Status | Content |
|---|---|---|
| `01_Offene_Fragen_Q1_bis_Q9.md` | D | Q1 (unattended Saxo session) and Q2 (provider terms) blocking; Q3–Q9 |
| `02_Risikoregister.md` | O | scientific, financial, technical/security, process risks with qualitative likelihood/impact |
| `03_Annahmen_und_Validierung.md` | D | twelve critical assumptions, validation path, consequence if false |

### `07_Empfehlungen_Implementierung/` (implementation recommendations)
| File | Status | Content |
|---|---|---|
| `01_Implementierungssequenz_Windows_Saxo.md` | D | ten steps (verify package → tests → Lean → anchors → SIM read-only → PKCE refresh test → registry/Jev → adapters → SIM_PRECHECK → SIM_EXECUTION → shadow), acceptance tests, failure paths, costs |
| `02_Entscheide_und_Prioritaeten.md` | O | thirteen decisions (reversible by owner), dependency-ordered build list, what is explicitly not built, two owner questions |
| `03_Scorecard.md` | D | 21 criteria with pre-review status, verdict, remediation, source |
| `Scorecard.csv` | = `EN/REVIEW_SCORECARD.csv` | same scorecard as CSV |

### `08_Anhang/Original_Review_EN/` (English originals, unchanged)
`START_HERE.md`, `CLAUDE_REVIEW.md`, `CPE_v0.2_REVISED_SPEC.md`, `SCIENTIFIC_EXPERIMENTS.md`,
`IMPLEMENTATION_SEQUENCE_WINDOWS_SAXO.md`, `OPEN_QUESTIONS_AND_DECISIONS.md`, `REVIEW_SCORECARD.csv`.
Section 8 of `CLAUDE_REVIEW.md` and the cost section of `OPEN_QUESTIONS_AND_DECISIONS.md` are declared
superseded by `02/03` (owner decision: subscriptions only).

### `08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/` (reference code, explicitly not to be implemented as-is)
| Path | Content |
|---|---|
| `README.md` | mapping of each v0.2 code change to a finding; breaking changes vs v0.1 |
| `PATCH_v01_to_v02.diff` | unified diff v0.1 → v0.2, 17 files |
| `source_v0_2/cpe/` | `core.py` (evidence, binary thesis, Kelly, deprecated e-process), `coherence.py` (credal LP), `ledger.py` (hash chain + anchors), `registry.py` (EventSpec/Forecast), `eprocess.py` (commit-before-resolve), `fusion.py`, `jev_adapter.py`, `allocation.py` (scenario max-min), `saxo_sim.py` (gate machine, precheck payload) |
| `source_v0_2/proofs/` | `BetThreshold.lean` (3 theorems), `RiskBudget.lean` (7 lemmas), `lean-toolchain` (v4.35.0), `lake-manifest.json` (Mathlib `cfc55fc5…`), `lakefile.toml` |
| `source_v0_2/tests/` | `test_engine.py` (11 legacy tests), `test_v02_regressions.py` (20 tests tied to findings) |
| `source_v0_2/prompts/` | round-1 instructions for the three researchers |
| `source_v0_2/docs/` | `RFC.md` (the **v0.1 research proposal**, the origin of the PCCB idea), `Saxo.md` (v0.1 onboarding notes) |
| `source_v0_2/adapters/jev_example.ts`, `examples/synthetic_demo.py` | v0.1 illustrations, not executed |
| `EVIDENZ_LOGS/` | `pytest_v01.log` (11 passed), `pytest_v02.log` (31 passed), `attack_v01_reproduction.py` + output (F1–F10), `lean_compile.log`, archived OpenAPI JSON |

## 3. Source map (external sources the research relies on)

Full list with URLs: `05/01`. Summary by verification status **as reported by the package**. None of the
external sources were re-fetched in this session (no network verification was attempted; see `14-unverified-claims.md`).

| Family | Package status | Load-bearing for |
|---|---|---|
| Saxo OpenAPI learn pages: environments, order placement, precheck reference, PKCE, LIVE credentials | PACKAGE-VERIFIED 2026-10-16 (read, not archived as bytes) | gate design, payload fields, `x-request-id`, `ManualOrder`, session-lifetime question Q1 |
| Saxo multi-leg precheck, SIM market-data help article, Swiss retail entitlements, unattended session policy | UNVERIFIED | Q1, Q4, Q6, Q7 |
| TypeSafe Jev: live OpenAPI JSON (archived), vendor blog (price, latency), arXiv 2609.37647 and 2609.33209 | PACKAGE-VERIFIED (JSON archived; arXiv titles via API; 2609.33209 abstract read) | Jev adapter schema, complement-gap threshold 0.15, cost model |
| Anthropic, OpenAI, Google subscription and quota pages | PACKAGE-VERIFIED 2026-10-16 (terms change frequently) | operating model `02/03`, Q2 |
| Statistics: Ramdas et al. 2020 (2009.03167); Waudby-Smith & Ramdas (2010.09686, formula UNVERIFIED); Laroche 2019; 2208.00724; Adams & MacKay BOCPD; StockBench | titles verified via arXiv API; contents partly read | e-process validity, λ rule, safe policy improvement caveats, hazard model |
| Nilsson 1986, Walley 1991, Kelly 1956, MacLean/Thorp/Ziemba 2010, Brier 1950, Gneiting & Raftery 2007 | general knowledge, not checked | coherence LP, Kelly, proper scoring |
| Lean 4 / Mathlib pins | compiled locally by the package author; log archived | `04-formal-verification.md` |
| ESTV circular no. 36 (Swiss professional-trader classification) | not retrieved; tax adviser required | turnover limits, Q9 |
| tandfonline 2023 (survivorship), AlphaEvolve blog, Gemini model page | carried over from v0.1, not checked | background only |

## 4. Checks performed in this session

| Check | Method | Result |
|---|---|---|
| ZIP integrity and safety | `unzip -l`, symlink/traversal scan, `sha256sum -c MANIFEST.sha256`, credential-pattern grep | 71/71 OK; no symlinks; no credentials; ZIP SHA-256 `dc69e2a7…6415` |
| v0.2 reference tests | isolated venv (Python 3.13.16, numpy 2.5.4, scipy 1.18.1, httpx 0.28.1, pytest 9.1.1), `pytest -q` on a scratch copy | **31 passed** (REPRODUCED) |
| v0.1 reconstruction | `patch -R -p1 < PATCH_v01_to_v02.diff` on a copy of `source_v0_2` | clean reverse apply; resulting tree has the 16 v0.1 files |
| v0.1 reference tests | `pytest -q` on the reconstructed tree | **11 passed** (REPRODUCED) |
| Attack script F1–F10 | `python -I attack_v01_reproduction.py <v0.1> <scratch>` | output matches `attack_v01_output.log` line for line except timing (0.27 s vs 0.26 s) (REPRODUCED) |
| Python syntax | `py_compile` on all `.py` in the appendix | all compile |
| Arithmetic | independent re-derivation | 100^(1/10) − 1 = 0.5849; Kelly w* = 0.025 (p = 0.10), 0.0522 (p = 0.12); threshold 4/49 = 0.0816; E[ln] at full investment = −1.14; hit-rate tables in `04/04` reproduce (see §5 item 5) |
| OpenAPI archive | parse, list endpoints and schemas | valid JSON; `GET /v1/models`, `POST /v1/systemone`; 20 schemas; both copies identical |
| Duplicates | `cmp` | `Scorecard.csv` ≡ `REVIEW_SCORECARD.csv`; both OpenAPI copies identical |
| EN ↔ DE consistency | header and threshold spot checks (`EN/CPE_v0.2_REVISED_SPEC.md` vs `02/01`; `EN/IMPLEMENTATION_SEQUENCE…` vs `07/01`) | structure and numeric thresholds match on all spot checks |
| Lean compilation | **not re-run** (no Lean toolchain here; Mathlib cache is ~8 GB) | `lean_compile.log` taken as PACKAGE-VERIFIED only |
| External sources | **not re-fetched** | all remain PACKAGE-VERIFIED or UNVERIFIED |
| Reference-code probes P1–P6 | `probe` script against the v0.2 tree | five defects confirmed, one edge case fine; see `01-architecture.md` §3 |

## 5. Internal inconsistencies and gaps found in the package

None of these change the package's decision (REVISE). They are listed so that Codex does not rediscover them
and so that the foundation documents can state the resolved reading.

1. **Scorecard still carries the superseded access policy.** `07/03` and `Scorecard.csv` (OPS-01) say
   "default to API keys where terms unclear; budget $200–600/month". The owner decision of 2026-10-16 (`02/03`)
   forbids API keys without an owner decision and plans USD 0 beyond subscriptions. `08_Anhang/README.md`
   names `CLAUDE_REVIEW.md` §8 and `OPEN_QUESTIONS` §D as superseded but not the scorecard. Likewise
   `EN/OPEN_QUESTIONS_AND_DECISIONS.md` Q2 says "default to API keys" while the German `06/01` Q2 says the
   opposite. **Resolved reading:** `02/03` governs.
2. **Reference-code README contradicts the Lean evidence.** `ref/README.md` line 26 still says Lean syntax
   is "currently unverified", while `evidence/lean_compile.log` and the header of `ref/proofs/BetThreshold.lean`
   record a successful compile on a pinned toolchain. Stale v0.1 text.
3. **`ref/docs/RFC.md` is the v0.1 RFC and `ref/docs/Saxo.md` is v0.1 guidance.** `Saxo.md` item 10 says
   fully autonomous systems "require `ManualOrder: false`", whereas v0.2 removed `ManualOrder` from the
   *precheck* payload (undocumented there) and defers it to the not-yet-written placement payload. The
   package README says `02/01` supersedes the RFC's content. Both files are kept because the RFC is the
   origin of the PCCB concept.
4. **Decision numbering in `07/02` §A is out of order** (1–9, then 13, 12, 11, 10). Cosmetic; the
   foundation document `09-open-questions-and-decisions.md` renumbers them D1–D13 and keeps the original number.
5. **Hit-rate table in `04/04` §2 (second table) mixes loser multiples without labelling them per row.**
   Rows at 10 % and 20 % use a 0.5x loser (1.45x, 2.40x per cycle); rows at 30 % and 45 % use 0.3x (3.21x,
   4.67x). The heading says "0.3x to 0.5x", so it is not wrong, but a reader cannot reproduce a row without
   guessing. Arithmetic re-derived here is correct for the implied values.
6. **λ rule: text and code differ in the order of clip and shrink.** `03/02` §3 writes
   `λ = clip(m/(v+m²), 0, λ_max) · n/(n+10)`; `ref/cpe/eprocess.py` computes `clip(m/(v+m²) · n/(n+10), 0, λ_max)`.
   When the raw ratio exceeds λ_max the code bets more than the text says. Validity is unaffected (both
   stay in `[0, λ_max]`); power and documentation differ.
7. **The event-source list for the discovery scanner is never enumerated.** The whole discovery premise
   ("sector-independent first-principles scanner") rests on source families that `02/01` §3.2 only exemplifies
   (SLOOS, EDGAR, FDA 510(k), TED) and `07/01` step 6 calls "3 to 5 source families". Which families, their
   licences, formats and lags, is an open design decision (recorded as N1 in `09-open-questions-and-decisions.md`).
8. **Externally read documentation was not archived.** `evidence/README.md` states that the Saxo and
   provider pages were read but not saved as bytes. Every PACKAGE-VERIFIED external claim therefore rests on
   the author's reading on one day; the package itself asks the owner to archive them at setup.
9. **Environment detail cannot be checked.** `01/03` lists "httpx 2.13.0"; tests pass here on httpx 0.28.1
   with the declared constraint `httpx>=0.26`. Immaterial to results.
10. **The package reviews its own code.** The v0.2 reference code and the 31 tests that validate it were written
    by the same author in the same session as the findings they address. The tests demonstrate the described
    behaviour; they are not independent evidence that the design is right. The probes in
    `01-architecture.md` §3 show defects those tests do not cover.

## 6. Classification of the research content

| Class | Items |
|---|---|
| **Established methods** (ESTABLISHED) | credal sets via LP over world states; implication ⇒ marginal ordering; test supermartingales with predictable λ and Ville's inequality; fractional and robust Kelly; proper scoring rules and reliability diagrams; purged/embargoed walk-forward; Bayesian online changepoint detection; min-variance pooling; isotonic/Platt calibration; conformal intervals |
| **New research hypotheses** (HYPOTHESIS, pre-registered in `04/02`) | H1 fusion calibration gain; H2 economic edge; H3 Jev recall at lower cost; H5 discovery lead ≥ 60 days; H6 hazard throttle net benefit; Design B better calibrated than A on large graphs (`03/01` §3); fractional robust Kelly on calibrated credal inputs avoids ruin (`03/04` §2); the central claim that milestone skill transfers to pre-trend 10x discrimination (`03/05` §5) |
| **Statements about the model, not hypotheses** | H4: a certified order plan has zero logic/budget violations *in the certified model* |
| **Unverified external claims** (UNVERIFIED) | see `14-unverified-claims.md` |
| **Proposed innovations requiring experimental validation** | PCCB as a typed object joining the above (`RFC` §0); three-model + Jev committee with correlation-aware fusion and typed abstention; mechanism objects with identification class gating what enters probability math; commit-before-resolve e-process as a promotion criterion; proposer/promoter separation with canaries and time-shifted holdouts; the asset-class extension ladder; the method scanner. Each needs the ablation arm named in `04/03` §5 before it can be called an advantage. |
