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
9. `16-reconciliation-matrix.md`: the versioned Claude–Codex reconciliation matrix (v15, round 14: the four
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
10. `17-phase1-amended-specification.md`: the proposed amended Phase 1 (version 12; versions 5 to 12 are the
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
