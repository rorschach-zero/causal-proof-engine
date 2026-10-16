# 13 Independent review checklist for Codex

Purpose: give the second reviewer a precise, finite list of things to verify or dispute, and a format for the
answer, so that the owner can decide on Phase 1 with two independent views. Please verify by executing where
possible, and please try to falsify the agreements between the package and this review (same model family on
both sides; see `10-adversarial-review.md` §0).

## 1. Integrity and provenance (expected time: 15 minutes)

- [ ] `cd research/original/CPE_Forschungspaket_2026-10-16 && sha256sum -c MANIFEST.sha256` → 71 OK.
- [ ] `git diff --stat main..research/claude-handoff -- research/original` shows additions only; no file under
      `research/original/` differs from the ZIP (ZIP SHA-256 in `original/IMPORT_NOTE.md`).
- [ ] No commit on the branch contains attribution trailers or session links (`git log --format=%B main..`).
- [ ] No secrets: `git grep -nEi 'api[_-]?key|bearer |refresh_token|AKIA' -- . ':!research/original'` returns
      only policy text.

## 2. Reproduce the executable evidence (expected time: 30 minutes, isolated venv outside the repository)

- [ ] `pytest -q` on a copy of `ref/` → 31 passed.
- [ ] Reverse-apply `PATCH_v01_to_v02.diff` to a copy of `ref/` → 16-file v0.1 tree; `pytest -q` → 11 passed.
- [ ] `python -I evidence/attack_v01_reproduction.py <v0.1 copy> <scratch>` → output matches
      `evidence/attack_v01_output.log` apart from timings.
- [ ] Re-run the six probes described in `01-architecture.md` §3 (P1–P6) or write your own; confirm or refute
      each CONFIRMED-DEFECT.
- [ ] Optional if you have Lean: compile `ref/proofs/*.lean` on the pinned toolchain; confirm the negative control fails.

## 3. Check the package's P0 findings against the code you reconstructed

For each of P0-SCI-01, P0-SCI-02, P0-ARCH-01, P0-BRKR-01, P0-STAT-01 (`01/02` §B): is the v0.1 defect real; is
the v0.2 fix a fix; is it a fix at the level of the design or only of the demo code? State one line each.

## 4. Dispute the review

For each of the eight sections of `10-adversarial-review.md`, answer: agree / disagree / partly, with the
strongest counter-argument you can construct. Specifically:

- [ ] §1: Is there a mathematical flaw this review missed in the credal LP, the pooling rule, the max-min
      reduction, or the e-process construction? Check `grapa_lambda` for any dependence on the current outcome.
- [ ] §2: Is the proposed `single-model-three-roles` control (R10) fair, or does it stack the deck against the
      committee? Propose a better control if so.
- [ ] §3: Which of the six proposed formalisation targets (R13) are worth the effort first? Would you drop any?
- [ ] §4: Name a leakage path neither the package nor this review lists.
- [ ] §5: Is the e-value combination rule (R19) the right replacement for the α-budget, or would you keep a
      fixed annual budget for simplicity?
- [ ] §6: Is forward-only point-in-time data sufficient for a credible Design C in years 1–2, or is the
      no-licensed-data decision (Q5) a false economy?
- [ ] §7: Do you agree that "discovery before trend acceleration" is the only genuinely novel empirical claim?
      What would make it more plausible a priori?
- [ ] §8: Is the ordering of the eight preconditions right? Would you move any gate earlier or later?

## 5. Decisions to confirm or amend (`09-open-questions-and-decisions.md`)

- [ ] D1–D13: list any you would change and why.
- [ ] N1–N12: for each, agree with the proposed resolution or propose another.
- [ ] Thresholds in D3/D4: any you consider unjustified enough to block pre-registration?

## 6. Governance

- [ ] `AGENTS.md`: anything missing, contradictory, or impossible to follow with your tooling? In particular
      §7 (provenance and attribution): confirm you can comply.
- [ ] `12-roadmap.md` Phase 1 scope: too large, too small, wrong order?

## 7. Requested output format

A single Markdown file `research/15-codex-review.md` on a branch `review/codex-<date>` (not on `main`), with:
(a) the executed checks of §1–§2 with commands and outputs; (b) one table for §3; (c) one section per item of
§4 with verdict and counter-argument; (d) a list of amendments you propose, each tagged with the D/N/R item it
changes; (e) your own top five concerns, which may differ from this review's; (f) a recommendation: proceed to
Phase 1 as specified, proceed with amendments, or do not proceed. Label every statement with the status labels
from `research/README.md`. Do not edit anything under `research/original/`.
