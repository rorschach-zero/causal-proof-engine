# CPE research foundation

This directory holds the complete research record of the Causal Proof Engine (CPE) at the point of handoff
for independent review (Codex). It contains **no implementation**. Nothing here places orders, holds
credentials or calls a model provider.

## Two layers, kept apart

| Layer | Where | Status |
|---|---|---|
| **Original research** (German, with English originals in its appendix) | `original/CPE_Forschungspaket_2026-10-16/` | verbatim, read-only, SHA-256 manifest verified |
| **Foundation documents** (English): per-topic entry points, review findings, proposed revisions | `research/*.md` (this directory) | authored 2026-10-16 on branch `research/claude-handoff` |

The original package states its own conclusions. The foundation documents summarise them, point into them,
and add an independent critique. Wherever the two differ, the difference is labelled. **No original conclusion
was rewritten.** A proposal that is not part of the original is marked `REVISION`.

## Reading order

1. `00-research-inventory.md`: what the package contains, what was verified here, internal inconsistencies.
2. `01-architecture.md` through `09-open-questions-and-decisions.md`: one document per topic.
3. `10-adversarial-review.md`: the independent scientific critique (eight questions).
4. `11-proposed-improvements.md`: concrete revisions, each tied to a finding.
5. `12-roadmap.md`: what would be built first, with exit criteria, if the review approves.
6. `13-codex-review-checklist.md`: what Codex is asked to check and where to disagree.
7. `14-unverified-claims.md`: every claim that is not yet verified, with a verification path.
8. `15-codex-review.md`: the independent Codex review (on branch `review/codex-20261016`, PR #2; not yet in
   this branch's tree).
9. `16-reconciliation-matrix.md`: the versioned Claude–Codex reconciliation matrix (v26, round 25: six findings on the round-24 commit, all applied to the specification, which moves to version 22: the record limit and the search budget are now fixed once per cohort in its primary contract, because a limit per family was reset by relabelling the family; the search may not read a point's own random stream before fixing the point; each sampling draw comes from a public beacon round published after its candidate batch is anchored, because a sampling seed could be chosen; the η budget closes registration on the bounds of every eligible candidate, because a close counted on registrations depended on the draws; A3 now states the certification rule of the tests; and an evidence figure of round 24 is correctly described as an upper bound; round 24: three findings on the round-23 commit, all applied to the specification, which moved to version 21: a simulated family's first calibration record now fixes the most records
   it may have and the search budget, because an allocation over the records realised so far and a record that had to
   contain the search's own output both failed, and the seed value comes only from a public beacon round named in the
   record, because a value its contributor could try offline was selectable; round 23: three findings on the round-22
   commit, one applied to the specification, which moved to version 20: a simulated calibration's seed is now derived from a value that does not
   exist until its calibration record is anchored, because a seed only committed before the cohort could be chosen
   among several runs; one provenance claim not reproduced, and one whose evidence showed that the round-22 test was
   confounded by the order of the push and the PR edit; round 22: two provenance findings on the round-21 commit, none on the
   specification, which stays at version 19; one not reproduced, and one that found the pull request's title and
   description nine rounds stale, now advanced; round 21: the four
   findings of Codex's review of the version-18 specification, three applied and one not reproduced: the η budget
   closes the registration window for every source and the estimand is stated over that window, a simulated
   calibration spends its miscoverage in the level budget, and G counts only blocks with an emitted increment;
   round 20: the seven
   findings of Codex's comment on the version-17 specification, six applied and one not reproduced, among them the
   late-record budget η_max now bounding the probability of any late record over the whole cohort, members
   pre-declared VOID adjudicated so that a registration breach on one removes its cluster, and source withdrawal
   deferred to the next cohort; round 19: the three findings of Codex's comment on the version-16 specification, two
   applied and one not reproduced, every component certified at α − η_max and the issuance breach routed through the
   box rule; round 18: the three
   findings of Codex's review of the version-15 specification, all applied, among them the protected operation's
   commit record anchored before the change takes effect and is acknowledged, all-VOID clusters counted in the VOID
   cap, and one inclusion probability for every sampled cluster; round 17: the three
   findings of Codex's review of the version-14 specification, all applied, among them the closed-form box bound
   now carrying the design's own constant for unequal blocks, cutoff breaches propagated to every arm that consumes
   the breached provider, and monitor factors committed only after the defect-closure horizon; round 16: the seven
   findings of Codex's review of the version-13 specification, six applied and one not reproduced, among them
   breached and defective members now entering by a box rule whose decision is dominated by the decision on the
   honest sample, because the least favourable outcome was not conservative, a decision date after a defect-closure
   horizon, and cutoff corrections after the first registration ending the claim; round 15: the five
   findings of Codex's review of the version-12 specification, all applied, among them registration-breach
   clusters now outside the scored population because zeros placed after the outcomes move the statistic, and
   late-source defects scored at their least favourable outcome; round 14: the four
   findings of Codex's review of the version-11 specification, three applied and one not reproduced, among them
   a member knowable before its cluster's registration, now named and shown to enter at X = 0, and the §6
   estimand gated by the earliest-knowable bound; round 13: the six
   findings of Codex's review of the version-10 specification, all applied, among them two selections on a known
   outcome (a member knowable before a model cutoff excluded after its outcome, and registration after a public
   terminal falsifier) and the statement of the monitor's null in the record-order filtration it uses; round 12:
   eight of the nine findings of Codex's two reviews of the version-9 specification, among them a post-unblinding
   cutoff correction that now ends the confirmatory claim; round 11: the eight
   findings of Codex's review of the version-8 specification, seven applied and one not reproduced, among them
   the calibration criterion that admitted a size above α and the committed two-point critical values that were
   exceeded between their own grid points and are replaced by exact-supremum values, with every power figure
   restated at them; round 10: the eight findings of Codex's review of the version-7 specification, five of them
   defects in round-9 remedies, among them a null class stated as four scalars that a persistent-regime law
   satisfies while oversized at every calibrated critical value, all reproduced where checkable and applied;
   round 9 applied the twenty-one
   findings of Codex's two reviews of the version-6 specification under the owner's directive, six of them
   defects in round-7 and round-8 remedies and one a monitor-ordering rule carried since round 2; round 8 applied two defects in round-7 remedies; round 7 applied the
   seventeen findings recorded in rounds 4–6 and the four of Codex's seventh review as the OD10 decision diff,
   on the owner's instruction that a round budget never closes a finding), reproduced evidence, the one
   remaining disagreement (hosting timing, an owner decision) and owner decisions.
10. `17-phase1-amended-specification.md`: the proposed amended Phase 1 (version 22; versions 5 to 22 are the
    OD10 decision diff) and its acceptance-test matrix, including the restated mandatory counterexample
    fixtures (§5.1).
11. `reproduction/`: the reproduction scripts of `16`, one committed file per appendix, with pinned requirements
    and `check_appendix_scripts.py`, which verifies each file byte for byte against its appendix block; evidence
    scripts, not project code.

Documents `02`, `03`, `06`, `07`, `08`, `09`, `11` and `12` end with an appended amendments section dated
2026-10-16; the text above those sections is unchanged from the reviewed head `8b2dba7`.

## Status labels used throughout

| Label | Meaning |
|---|---|
| `ESTABLISHED` | textbook method or published result; cited |
| `HYPOTHESIS` | pre-registered scientific claim of the programme; untested |
| `UNVERIFIED` | external factual claim that neither the package nor this session checked against a primary source |
| `PACKAGE-VERIFIED` | the package reports checking it against a primary source on 2026-10-16; **not** re-checked in this session |
| `REPRODUCED` | re-executed or re-derived in this session (details in `00-research-inventory.md` §4) |
| `CONFIRMED-DEFECT` | a defect in the reference code demonstrated by a probe in this session |
| `REVISION` | a proposal of this review, not part of the original research |

A claim that only the other reviewer checked (for example a primary-source read reported in
`15-codex-review.md`) stays `UNVERIFIED` in documents on this branch, with the reviewer's report cited by
section and date; no label is borrowed for it (`16-reconciliation-matrix.md` RC-36).

Three kinds of evidence are never mixed, following the package's own rule: **formally proved** (Lean,
conditional on hypotheses), **statistically shown** (e-processes, proper scores), **empirically supported**
(track record). Simulated performance is never live performance. A compiled theorem never implies profit.

## Short references into the original package

Foundation documents cite original chapters as `NN/MM` (directory/file prefix), e.g. `03/02` is
`original/CPE_Forschungspaket_2026-10-16/03_Mathematische_Modelle/02_E-Prozess_und_sequentielle_Tests.md`.
The English originals are cited by file name, e.g. `EN/CLAUDE_REVIEW.md` is
`original/.../08_Anhang/Original_Review_EN/CLAUDE_REVIEW.md`. Reference code is cited as `ref/cpe/ledger.py`,
meaning `original/.../08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/source_v0_2/cpe/ledger.py`.

| Alias | Path under `original/CPE_Forschungspaket_2026-10-16/` |
|---|---|
| `README` | `README.md` |
| `01/01` – `01/03` | `01_Forschungsergebnisse/` |
| `02/01` – `02/05` | `02_Systemarchitektur/` |
| `03/01` – `03/06` | `03_Mathematische_Modelle/` |
| `04/01` – `04/04` | `04_Wissenschaftliche_Begruendung/` |
| `05/01` | `05_Quellen/01_Quellenverzeichnis.md` |
| `06/01` – `06/03` | `06_Offene_Probleme_und_Risiken/` |
| `07/01` – `07/03` | `07_Empfehlungen_Implementierung/` |
| `EN/*` | `08_Anhang/Original_Review_EN/` |
| `ref/*` | `08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/source_v0_2/` |
| `evidence/*` | `08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/EVIDENZ_LOGS/` |

## Authorship and conflict of interest

The original package was produced by Claude (Fable 5.1) in an earlier session as an independent review of a
v0.1 prototype. The foundation documents were produced by Claude Code (also Fable 5.1). The same model
family therefore wrote both the research and this critique. That is a known bias risk (shared blind spots,
self-consistency pressure) and is the reason an independent Codex review is a precondition for any
implementation decision. See `10-adversarial-review.md` §0.
