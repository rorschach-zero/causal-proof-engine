<!-- DRAFT of research/19-phase1-handoff.md §11 "Phase 1 audit" (issue #37). Placeholders in angle brackets are open; it is to be folded into research/19 when the audit verdict is known. -->

## 11. Phase 1 audit

This is the quality gate of issue #3 comment `6312263652`, item 3 (first bullet): a whole-codebase audit by two auditors, Claude and Codex, tracked in issue #37.

The rules come from the coordinator's brief:
- A P1 counts as a defect only when it is reproduced as a failing test in this repository's suite.
- A finding that asks for more specification is listed for the owner and never applied.
- Every reproduced defect is fixed in an audit-fix PR against `main`, with its failing-then-passing tests, one Codex review and no fix rounds.
- The audit passes when one complete pass by both auditors, at a new pinned commit, yields no reproduced P1.
- At most three passes were planned. After pass 3 was not passed, the owner amended the gate on 2026-10-22 (issue #37):
  - every reproduced defect is fixed, P2s and P3s included;
  - the audit is not stopped by a pass count;
  - after each pass the owner gets the findings by severity and the trend, and decides whether to continue;
  - a pass passes when neither auditor reproduces a P1 at its pinned commit.

### 11.1 Pass 1, at `04fee700fee9eb1d9565d56737a8b90c34297051`

**Claude** (issue #37 comment `6340083787`) read every module of `cpe/` and `tools/` end to end against `17`, `18` §6, this document and `AGENTS.md`. Each suspected defect was written as a test first.

| # | Severity | Finding | Fixed in |
|---|---|---|---|
| C1 | P1 | Registration "before" bounds (e_i, issuance open, and the period start of claim, calibration and register) were checked against a clock sample taken before the append, not against the receipt it assigns | PR #38 |
| C2 | P1 | The same for the event criteria of the adjudication registry (issuance open) | PR #38 |
| C3 | P2 | Without a kernel boot id, the fallback id was one per object, not one per process, so a second gate in the process read a reboot | PR #39 |
| C4 | P2 | Late-report defects were judged against a fresh adjudication's disposition, not the stored one (RC-88) | PR #39 |
| C5 | P2 | `tools/lean_check.sh` reported `VERIFIED` for a lemma closed by `sorry` | PR #39 |
| C6 | P3 | Integers beyond Python's digit limit or the float range raised `ValueError` or `OverflowError`, not a typed refusal | PR #39 |
| G1 | gap | Golden ledger identifiers for every record kind (the identifier format is a contract, §10) | PR #40 |

**Codex.** The full-tree review requested on issue #37 did not run: the repository had no Codex cloud environment (comment `6340394552`). Pass 1 was therefore not a complete pass by both auditors.

**Reviews of the pass-1 audit-fix PRs.**
- PR #38, `4348027365` (P1): says the commit has a Codex author and an attribution footer. **Not reproduced.** The commit has the owner identity and no footer, `tools/check_provenance.py` reports 0 findings, and T-09 is green.
- PR #39, `4348066271` (P2): `repr` on an `int` subclass. **Reproduced**, a regression of C6; fixed in pass 2 (D1, PR #41).
- PR #39, `4348066268` (P2): an incremental Lean build may not reprint the `sorry` warning. **Not reproduced** (no Lean toolchain was run). CI builds from clean, so T-40 is unaffected. No change (coordinator, 2026-10-22).
- PR #40: no Codex review within 45 minutes.

### 11.2 Pass 2, at `2998824d0330ef028a8cc2cb7682a40f6fc23763`

This is the merge of PR #40; it holds every pass-1 fix.

**Claude** (issue #37 comment `6341609567`) read the diff `04fee70..2998824` in full. It also re-read the write paths of the adjudication registry, the registration registry, the capability gate and the point-in-time store, for a second writer on the same ledger.

| # | Severity | Finding | Fixed in |
|---|---|---|---|
| D1 | P3 | `4348066271`: the integer limit of the canonical form was judged on a subclass's `repr`, not on the form `json` writes | PR #41 |
| D2 | P3 | A second adjudication registry on the same ledger: a rule, an event or a post-disposition side row that the other writer landed first was refused as `duplicate_record_id` instead of being read back | PR #42 |

**Codex.** The `@codex` mention on issue #37 still answered "create an environment" (comments `6345625196`, `6345740284`), so the owner ran the review in the Codex web UI against the published environment. The answer is in comment `6346290601`; the classification is in comment `6346675397`.

Every finding was reproduced by a test committed in this suite that fails on a `git archive` of `2998824` on Python 3.13.16 and 3.11.17:

| # | Severity | Finding | Fixed in |
|---|---|---|---|
| 1 | P1 | The high-water mark held a check's receipt, not the wall time it observed, so a capability seen as expired was acknowledged after a rollback inside the slew tolerance (a path other than H4 `4334622032`) | PR #43 |
| 2 | P1 | An earlier evidenced publication did not correct a stored disposition's `knowable_at` (RC-146) | PR #44 |
| 3 | P1 | An `OPEN` adjudication dropped an evidenced public occurrence (RC-146; reading in §11.4) | PR #44 |
| 4 | P1 | A late expiry gave a `knowable_at` after logical finality (RC-77, F-21b) | PR #44 |
| 5 | P2 | An arm version was written without its schema, so its row broke every later replay | PR #45 |
| 6 | P2 | The cutoff rule compared the local date of e_i, not its UTC date | PR #45 |
| 7 | P2 | `FULL` could be the baseline arm (`18` M-5) | PR #45 |
| 8 | P2 | Only the deciding record was checked for receipt lag (RC-105) | PR #44 |
| 9 | P2 | A folded trailer with a spaced colon passed the provenance check (T-09) | PR #46 |
| 10 | P3 | A non-ASCII signature raised `TypeError` instead of `invalid_signature` | PR #43 |
| 11 | P3 | Deep acyclic nesting raised `RecursionError` instead of a typed refusal | PR #46 |

**Pass 2 is not passed**: findings 1 to 4 are reproduced P1s.

**Reviews of the pass-2 audit-fix PRs.**
- PRs #41, #42 and #46: no findings.
- PR #44: two findings, both reproduced and fixed in the follow-up PR #47:
  - `4351249330` (P1): a contradicting timely publication did not correct the stored `knowable_at` (reading in §11.4);
  - `4351249349` (P2): an `OPEN` result dropped its incidents.
- PR #45, `4351265741` (P1): says commit `4d3af82` has a non-owner author and a footer. **Not reproduced**: `4d3af82` is in no ref of the repository, and the head has the owner identity.
- PR #43: no Codex review within 45 minutes.
- PR #47: no Codex review within 45 minutes.

### 11.3 Pass 3, at `b48c952c67c4d4358f82d3f811f744d47bdeb0b4`

This is the merge of PR #47; it holds every fix of passes 1 and 2 (issue #37 comment `6347957337`).

**Claude** (issue #37 comment `6348183848`) read every module of `cpe/` and `tools/` end to end:
- `tools/` was read by the auditor;
- `cpe/` was split into three components, each read by an independent reviewer. Every reported test was re-run and every claim was checked against the documents by the auditor.

| # | Severity | Finding | Fixed in |
|---|---|---|---|
| F4 | **P1** | `claim_status` answered "confirmatory" for a claim whose register was anchored after the beacon round of a bound calibration record. The refused round was not written (RC-311, `18` M-1 (i)) | PR #48 |
| T1 | P2 | The provenance check split `git log` output on U+001E and U+001F, so a message holding them hid trailers git reads (T-09) | PR #49 |
| A2, A3 | P2 | A record id longer than 256 characters, or an `EventSpec` built with a negative latency window, was admitted online, and replay then refused the whole ledger | PR #54 |
| A4 | P2 | An order comparator over a non-number was registered, so every record was refused | PR #54 |
| F5 | P2, re-rated **P1** at pass 4 | Replay took a beacon output's seed as written, without recomputing SHA-256(record ‖ v) (RC-187, RC-304). Re-rated with class W: a persisted result the documents name | PR #51 |
| C-d | P2 | A `list` subclass with an overridden `__iter__` was silently truncated by the canonical form | PR #55 |
| — | P3 | 15 typed-refusal and hygiene findings (issue #37 comment `6348183848`) | PRs #52 (expiry), #57, #58; adjudication P3s pending |

**Codex**: not run. The owner could not reach the Codex environment, and pass 3 was already not passed by the Claude auditor's F4. Codex's pass-4 review takes its place.

**Pass 3 is not passed: F4 is a reproduced P1.**

### 11.3a Pass 4, at `c3d6233dbaeb71eb71cb128394099b23cef285b5`

Authorised by the owner after pass 3, and pinned at the merge of PR #50 on `f77577a`: every fix of passes 1 to 3 (PRs #38 to #50) and nothing else (issue #37 comment `6349749845`). The owner amended the gate the same day (comment `6349142513`): every reproduced defect is fixed, P2 and P3 included; a pass passes when neither auditor reproduces a P1; the owner decides after each pass whether to continue.

**Claude** (issue #37 comment `6349971614`): `tools/` was read by the auditor, and `cpe/` by three independent reviewers (adjudication; registration, point-in-time, issuance and schemas; ledger, capability and canonical form). Every reported test was re-run on a `git archive` of the pinned commit, where the suite gives 650 passed. The coordinator classified class W and C1.

| # | Severity | Finding | Fixed in |
|---|---|---|---|
| W1 | **P1** | Replay of the gate never verified an intent's signature: an intent with a capability another key signed, and its commit, appended through the ledger, gave the gate a level (17 item 5, RC-43, RC-46) | PR #51 |
| W2 | **P1** | A second register row was read as the register (`18` R9) | PR #51 |
| W3 | **P1** | A register row after a seeded round was read as the register (`18` §6 M-1, RC-311) | PR #51 |
| C1 | **P1** | `format_timestamp` wrote a year below 1000 without padding and the high-water mark compared text, so a clock rolled back below year 1000 was admitted (17 item 2). Reachable only with an injected clock; the gate compared instants | PR #52 |
| T2 | P2 | The provenance check missed trailers git reads in a block with a comment line, or a mixed block led by a git-generated line (T-09) | PR #53 |
| R1 | P2 | A round supplied while the register's anchor was pending but held by the store was recorded as refused and bound for good; no seed could ever be drawn | PR #56, superseded unmerged by PR #61 (below) |
| K1, K2 | P2 | Surrogate code points: two different strings had one canonical form, and two keys merged into one in the ledger | PR #55 |
| A5 | P2 | The adjudication registry wrote values its own replay refuses (the class of A2 to A4) | PR #54 |
| A6 | P2 | The status identifier depended on the time zone of the declared instant | PR #54 |
| A7 | P2 | A disposition corrected on a stale snapshot was returned while the ledger held another | PR #54 |
| — | P3 | `check_issuance(outputs=None)`; naive datetimes in two adjudication calls; a `late_publication` incident persisted against a VOID its record never decided; surrogates in record identifiers | PRs #57, #58, #62 |

**Codex reviews of the pass-4 fix PRs** (one review per PR, no fix rounds; a PR with a reproduced P1 regression is superseded, never merged):

| Review finding | Severity | Finding | Outcome |
|---|---|---|---|
| `4353051497` (PR #51) | **P1** | A commit citing its intent's own sequence and entry hash, with no intent anchor published, was accepted as step 2 | PR #63 |
| `4353051510` (PR #51) | P2 | A gate started under a new release could not replay a ledger an earlier release had promoted | PR #63 |
| `4353051504` (PR #51) | P2 | A raw refused-round row for a round the register's anchor preceded passed replay | PR #63 |
| `4353163782` (PR #54) | P2 | A `str` subclass mimicking an archived digest passed the content check, and the written record was unreadable | PR #62 |
| `4353163787` (PR #54) | P2 | A legacy status identifier formed from an offset let a second status of the same instant land | PR #62 |
| `4353231816` (PR #56) | **P1**, regression of #56 | A disproved pending anchor attempt was trusted; a claim stayed confirmatory although its register was anchored after the round | never landed; PR #56 superseded by PR #61 |
| `4353231824` (PR #56) | P2 | The local anchors and the pending attempts were read in two calls | PR #61 |
| `4353380374` (PR #59) | **P1**, regression of #59 | A gate of an earlier release replayed a later release's intent and acted at its level | never landed; PR #59 superseded by PR #63 |
| `4353380367` (PR #59) | **P1** | An intent anchor published after the commit was accepted as step 2 | PR #63 |
| `4353380358` (PR #59) | P2 | A refused-round row written under the old R1 made the ledger unreadable once the register anchor settled | PR #61 writes no such row; PR #63 refuses one on replay |
| `4353380381` (PR #59) | P2 | Gate state read the anchors and the records in two calls | PR #63 |
| `4414429445` (PR #63) | P2 | A held pending anchor attempt stayed pending after a larger anchor succeeded, so an eligible round was refused `anchor_pending` until the ledger was reopened (origin R1, PR #61; present on `main` `bba974d`) | PR #65 |
| `4414429436` (PR #63) | — | Claimed a commit `f152594` with a Codex author and a session footer. Not reproducible: the object is absent from the repository, the PR's commits carry the owner's identity and no trailer, and the provenance check reports 0 findings. Recorded as a reviewer artifact | no action |

**Codex pass 4**, run by the owner in the web UI: <PENDING: findings and classification.>

**Pass 4 is not passed: W1, W2, W3 and C1 are reproduced P1s** (F5 re-rated P1 with them). A new pass follows at a new pin once the fixes are merged.

### 11.3b Pass 5, at `b34c7212ca688d72611c3fd09b4eba170f94b44b`

Pinned on 2026-10-29 at `main` after PRs #60, #55, #57, #58, #61, #62, #63, #65 and #64 (#56 and #59 superseded): every reproduced defect of passes 1 to 4 and of the fix-PR reviews is fixed there (issue #37 comment `6502230845`).

**Claude** (a fresh audit session; issue #37 comment `6502823989`): every module of `cpe/` and `tools/` read at the pin (`tools/mutation_report.py` at structure level), `ci.yml` and `pr-text.yml`. Every suspected defect written as a pytest test on a `git archive` of the pin (Python 3.13.17), where the existing suite passes; every test below fails there. Classified by the coordinator on 2026-10-29.

| # | Severity | Finding | Fixed in |
|---|---|---|---|
| X1 | **P1** | Registration replay took forecast rows as written: a second row for a filled slot replaced its value (RC-75), a row under another arm version filled the slot (RC-96); the rows a forecast is judged against (cluster registration, candidate, arm version, correction, base rate) likewise | PR #70 |
| X2 | **P1** | Adjudication replay took disposition, knowable-correction and defect rows as written: a second disposition row turned `RESOLVED_NO` into `RESOLVED_YES` (RC-88), a correction naming no record lowered `knowable_at` (RC-146) | PR #71 |
| L1 | **P1** | Reopening a ledger cleared a disproved anchor attempt and its staged time with it, so a record was admitted below a persisted wall time (`17` item 2 "Clock"; the C1 precedent). `test_4329707427` had encoded the drop; its expectation is changed | PR #69 |
| R2 | P2 | An anchor landing between a registration snapshot and its append was not seen (an anchor moves no chain head): a round was recorded as refused against stale anchors and every later read refused the ledger | PR #67 |
| T3 | P3 | The pull request title pre-check missed titles git reads as trailers (`Fix:`, `1Fix: y`), which then fail T-09 on `main` (the incident of comment `6500990530`) | PR #66 |
| B1 | P3 | The import boundary did not forbid `posix` (nor `nt`, `_posixsubprocess`, `_winapi`, `_socket`, `_ssl`) | PR #66 |
| — | P3 | A text evidence cutoff and a text capability expiry raised `AttributeError`; raw registration rows of an unknown version or event raised `KeyError` | PRs #68, #70 |

**Codex reviews of the pass-5 fix PRs:**
- PR #66: no findings.
- PR #67, `4415215845` (P1 badge): claims commit `d47a396` with a Codex identity and a session footer. **Not reproduced**: no such object in the repository; the PR's commit carries the owner identity and no trailer; the provenance check reports 0 findings. A reviewer artifact, as `4414429436`.
- PR #69: no findings.
- PR #70, `4415337967`, and PR #71, `4415379656` (P1 badges): the same claim, about commits `c3f0c6c` and `c6977dd`. **Not reproduced**: neither object exists in the repository, each PR's commit carries the owner identity, and the provenance check reports 0 findings. Reviewer artifacts.
- PR #68: requested at opening (16:46 UTC); still running with no findings at 17:31 UTC, past the 45-minute window; merged with that reason recorded.
- PR #72 (P3-c, a non-string identifier at nine read interfaces refused as `invalid_identifier`): no findings. Opened as a draft with a one-line body, its full body read back footer-free before it was marked ready (the coordinator's workaround); unlike #67, #70 and #71, its review raised no claim about a nonexistent commit. One sample.

**Merged** on 2026-10-29 by the coordinator: #66 (`6320cb4`), #67 (`65e3f80`), #69 (`1c49ac5`), #70 (`b25b376`), #71 (`00168e7`), #72 (`b6d52a4`) and #68 (`1dca8d7`). Each open PR was trial-merged onto the new `main` and passed the suite before the next merge. Every reproduced finding of pass 5 is fixed on `main` at `1dca8d75ab6f49a82397cd493714d8602131538b`.

**Codex pass 5**, run by the owner in the web UI: not received by the pass-6 pin; Codex's full-tree review of pass 6 takes its place.

**Pass 5 is not passed: X1, X2 and L1 are reproduced P1s.**

### 11.3c Pass 6, at `1dca8d75ab6f49a82397cd493714d8602131538b`

Authorised by the owner on 2026-10-29 (17:13 UTC) and pinned at the merge of #68, which holds every fix of passes 1 to 5. Records on issue #37: Claude interim `6504124270`, classification of Codex's review `6504609509`.

**Claude** (a fresh session, session 8): `cpe/` and `tools/` read end to end, `tools/mutation_report.py` in full, and `tests/` line by line (the full read by an independent reviewer, every item verified by the auditor). The suite at the pin gives 830 passed.

| # | Severity | Finding | Fixed in |
|---|---|---|---|
| Y1 | **P1** | Adjudication replay took `event_spec` and `source_rule` rows as written: a second `event_spec` row replaced the criteria (a YES became `EXPIRED_NO` under a forged deadline), a first `event_spec` received after `issuance_open` was read as registered, and a second `source_rule` replaced the rule (`knowable_at` day 96 became 95). Also Codex 6-1 | PR #74 |
| E1 | **P1** | Gate replay took a `gate_epoch` row's epoch identifier as written: a repeated epoch revived a capability signed for it and never presented, acknowledged at `SIM_READ_ONLY` (RC-73, RC-100, RC-123) | PR #75 |
| A8 | P2 | A clock rollback between `adjudicate`'s clock read and the disposition append wrote `adjudicated_at` after the receipt, so replay refused every later read | PR #77 |
| B2 | P3 | The import boundary passed `logging.handlers`, `logging.config` and `concurrent.futures` | PR #76 |
| R3 | P3 | A raw `beacon_output` or `beacon_round_refused` row raised `KeyError` on replay (reproduced at the pin) | PR #80 |
| — | P3 | Test hygiene: six tests could not fail for the reason they name (PR #33 `4335189761` either-reason; the C1 year-999 bare raises; the F-21b clause refused by its window; the T-32 planted object; the T-30 landed-mode no-op; PR #19 `4329836196`'s duplicate loop) | PR #79 (supersedes #78) |

**Codex pass 6**: automatic review `5702392824` of the whole-tree PR #73, three P1 badges (findings `4415890495`, `4415890506`, `4415890522`).
- 6-1: Y1, reproduced (PR #74).
- 6-2: `RegistrationRegistry.state()` exposes sealed forecasts. First recorded as the specification question open since pass 2; **decided by the coordinator as a P2 defect** with reading P6-R2 (§11.4). PR #81: `state()` redacts the forecasts of events whose issuance window is open; the unredacted `_state()` is internal to replay.
- 6-3: a gate check's persisted wall time above its receipt did not bound other registries' receipts. **Reproduced, P1.** PR #77: `Ledger.append(observed=)` keeps the maximum in an `observed_walls` table, reloaded at open.
- Codex did not answer the readings or the read-only items of the request.

**Closed replay (PR #80, reading P6-R1).** Every replay is closed: `cpe/ledger/kinds.py` names every record kind by module; each replay re-validates its own kinds, skips the others' and refuses an unknown kind (`unknown_kind`). Admission rules were added for `void_request`, `integrity_incident`, `gate_abort`, `gate_commit` and `gate_check`. Deviation for the owner: a `gate_check`'s verdict is not recomputed on replay, because `replay_gate` takes the caller's trusted prefix.

**Codex reviews of the pass-6 fix PRs** (one each, no fix rounds):
- #74, #75, #76, #77, #79, #80 and #81: no findings.
- #78, `4416169908` (P2): on Python 3.14 `strftime` pads year 999, so the C1 test's pinned `invalid_timestamp` failed there. **Reproduced** on Python 3.14.6; #78 was closed unmerged and superseded by #79, which uses a literal stamp.

**Merged** on 2026-10-29: #74 (`3704aab`), #75 (`f957507`), #77 (`6035777`), #76 (`1651f4e`), #79 (`3927321`), #80 (`60895af`), #81 (`c55e4ce`, head `468e97a`, 18:36 UTC). Every reproduced pass-6 finding is fixed on `main` after #81, which is the pass-7 pin if the owner authorises one. Pass-6 report: issue #37 comment `6505239514`.

**Pass 6 is not passed: Y1, E1 and 6-3 are reproduced P1s.**

### 11.4 Deviations and readings, for the owner

- **An `OPEN` member with an evidenced public occurrence** (pass 2, Codex 3). `17` defines `knowable_at` = min(publication, public occurrence, deadline + window) for an outcome, but does not say what an undecided member carries.
  - Reading applied: the disposition stays `OPEN`, and the member carries its earliest evidenced public occurrence, capped at finality, as `knowable_at`. A sibling forecast after it is therefore late (T-02).
  - An `OPEN` member without a public occurrence has no knowable time, so the F-21b gap before the formal record is closed only once the member is decided.
- **A stored disposition's `knowable_at` is corrected by the earliest evidenced publication of any timely deciding record**, whether or not that record agrees with the disposition (pass 2, Codex 2 and PR #44 `4351249330`; coordinator's reading). The disposition never changes (RC-88), and a contradiction stays a recorded defect or incident. This extends to publications the rule H1 review `4334622042` applied to public occurrences. It touches S2.

- **The gate fails closed below the latest observed wall time** (PR #43; accepted by the coordinator as consistent with the ledger's own mark).
  - The gate refuses every decision while the wall clock is below the latest wall time a persisted reading observed, including the rotation at process start.
  - So a gate constructed after a restart with the clock rolled back past that time raises `clock_rollback` until the clock passes it.
  - The margin over the receipt high-water mark is at most the slew tolerance.

- **A refused beacon round is recorded** (PR #48): `claim_status` reads it. A claim was exploratory from the register's anchor on if a round preceded the anchor, so "a claim's status never changing" holds. The round's publication time is the supplier's attested input (RC-311, `18` M-1 (i)).

- **A round's first recorded attestation binds** (PR #50; approved by the coordinator on 2026-10-22; RC-311, `18` M-1 (i)).
  - Once a round is recorded as published before the register's anchor, a later and contradictory attestation of the same round is refused. The claim stays exploratory, and no seed is drawn.
  - A round refused only because the calibration record's own anchor came after it, with no late register, stays correctable.
  - This changed one step of `test_m1_binding_register_and_beacon_seed`; PR #50 states the old and new expectation.
  - It sits beside the open question of evidence binding for beacon outputs.

- **Replay re-validates every authority-bearing row, and a forged row refuses the whole ledger** (PR #51; coordinator's design). A party able to append to the ledger can stop every later read but gains no level, status or seed. Not re-checked on replay: the evidence a capability binds (only its digest is on the ledger), whether an intent was a promotion, and whether its epoch was anchored when it was written (replay cannot know the anchors of that moment).
- **An unconfirmed anchor attempt never makes a refused round bind** (R1): the round is refused `anchor_pending` and weighed again once the attempt settles.
- **PR #56 was superseded, not merged** (coordinator, 2026-10-22). Its one Codex review reproduced a P1 regression of that PR (`4353231816`: a disproved pending attempt was trusted, and a claim stayed confirmatory although its register was anchored after the round) and a P2 (`4353231824`: two anchor reads raced). The review cap stops fix rounds but never lands a reproduced P1 regression on `main`; R1 and both fixes landed in PR #61.
- **PR #59 was superseded, not merged** (coordinator, 2026-10-22). Its one Codex review reproduced a P1 regression of that PR (`4353380374`), a P1 present on `main` (`4353380367`) and two P2s (`4353380358`, `4353380381`). They landed with #59's fixes in PR #63, built on PR #61.
- **Release continuity per epoch** (PR #63; coordinator's reading). Each epoch is replayed under the release that opened it, and a gate acts only in an epoch its own release opened: an older release still running refuses every action with `stale_release` until its own start rotates the epoch. Neither 17 item 5 nor RC-74, RC-103 or RC-123 states upgrade continuity.
- **A ledger already holding a refused-round row written under the old R1 is refused on replay** (PR #63, `4353380358`). Such a row is the R1 defect itself.
- **The canonical form takes plain containers only** (PR #55): a subclass is refused even when it serialises faithfully.

- **Class W extended to forecast, disposition and knowable-correction rows (reading P5-R1; coordinator, 2026-10-29).** Replay admits every row that sets what a forecast is judged against, every disposition, correction and defect only by the rule its write path applies; a row the registry would have refused refuses the ledger (PRs #70, #71). A disposition is recomputed on replay from the state it was appended against; a correction must be at a time its named record evidences. Incident rows decide nothing and are read as written.
- **The clock bound of a staged anchor attempt survives its disproof and a reopen (reading P5-R2; coordinator, 2026-10-29).** The disproved row is still cleared (§9.1 stands); its staged time stays in the anchor high-water mark (PR #69).
- **Pass 6 readings** (session 8; for the owner, none changes a document):
  - (a) P5-R1 extended to every adjudication row kind (criteria, rule, content, records, observations, statuses); status rows are checked for one status per source and instant rather than by identifier, because of PR #54's legacy offsets (PR #74).
  - (b) An epoch row must be a fresh rotation: canonical identifier, an epoch id never seen before on the ledger (PR #75).
  - (c) The observed-wall mark is ledger-local, like P5-R2's retired times: a JSONL restore rebuilds receipts only, and the gate still bounds itself by its replayed readings (PR #77).
  - (d) The disposition append refuses a receipt below its adjudication time (`clock_rollback`) (PR #77).
- **P6-R1 (coordinator-approved): replay is closed in every module** (PR #80). Each replay re-validates its own record kinds, skips the kinds of other modules and refuses an unknown kind. A `gate_check`'s verdict is not recomputed (the caller's trusted prefix decides it).
- **P6-R2 (coordinator): the public snapshot never carries a sealed forecast; the unredacted snapshot is internal to replay** (PR #81).

### 11.5 Specification questions, for the owner

Listed, not applied (issue #37 comments `6340083787`, `6346675397`).

From pass 1:
- **S1.** The adjudication registry and the pre-registration registry each record an `EventSpec`, and nothing checks that the two agree. `17` does not say which registry is the authority for the resolution criteria.
- **S2.** Among timely deciding records the earliest knowable time wins (RC-146). A timestamp-less report that decides VOID can therefore win over an evidenced timely YES published later but before finality. `17` gives no rule for conflicting timely records.
- **S3.** A public occurrence lowers `knowable_at` for every final disposition, including a VOID by the source's failure condition. Whether a VOID has a knowable time set by an occurrence it did not resolve is not stated.
- **S4.** A record published inside the window but received after an absence-based NO was stored is logged only as a `receipt_lag` incident, not as a contradiction of the stored disposition (the question of PR #18 `4329838021`).

From pass 2:
- **`RegistrationRegistry.state()` exposure.** It returned forecast values before the issuance close, while `forecasts_of()` refused the same read (RC-109). **Decided in pass 6** (Codex 6-2, coordinator): a P2 defect, fixed by PR #81 under reading P6-R2; no longer open.
- **Questions already open in the handoff**, still unresolved:
  - the exact input bundle the Jev record's digest binds;
  - whether covering anchors must precede evaluation periods;
  - the evidence bindings for absence observations, raw source bytes and attested availability.

From pass 3 (issue #37 comment `6348183848`), Q1 to Q14:
- **Adjudication:**
  - a timestamp-less occurrence published before `not_before` or inside the window (RC-71);
  - lateness evidence published before the deadline;
  - a status-decided VOID in t*_k;
  - an absence read after finality for a source without evidenced times.
- **Registration:**
  - RC-150 amended in place;
  - the seed input;
  - the beacon value format;
  - Design C consuming nothing;
  - revision-slot windows;
  - issuance opening at the registration receipt;
  - source-listing claims;
  - `record_calibration` before any round.
- **Capability gate:**
  - a demotion refused during a rollback inside the tolerance;
  - an acknowledgement refused after its commit took effect.
- **Pass 4** (issue #37 comment `6349971614`, P4-Q1 to P4-Q7):
  - a calibration record written after the register's anchor whose round precedes that anchor turns every confirmatory claim exploratory (RC-311 read literally) against `18` R9 "no claim's status changes after that anchor";
  - a source without evidenced times is "an OD5 exclusion at registration" in `17`, yet `register_event` accepts one;
  - a status declared before finality but received after it: declared time or receipt;
  - a late timestamp-less "occurred" record leaves the member OPEN indefinitely (F-02b may intend VOID);
  - a stored definitive EXPIRED_NO, then a timely report of an earlier occurrence published after finality, logs nothing (RC-88);
  - a field value of `null` under `eq` evaluates to not-occurred;
  - `claim_status` can move from exploratory to confirmatory when a held anchor settles.

### 11.6 Not defects (recorded for a later cleanup)

- **Written and never read:**
  - `GateState.commit_seq` and the values of `GateState.commits`;
  - the registration replay's `cluster_registered_at`.
- **Read but redundant:** the adjudication replay's `defect_record_ids`.
  - `REVISION` of pass 1, which called it never read: the stored-disposition path reads it, and the replayed disposition's defects hold the same rows.
- **Unreachable on any ledger the registries write:**
  - the `duplicate_record_id` mapping of `anchor_confirmatory_register`;
  - the second `commit_in_doubt` of `promote`;
  - the `unknown_source` of `submit_observation`;
  - from pass 6: `calibration_record_exists` in `record_calibration`, and the `unknown_source` guards of `AdjudicationRegistry.adjudicate` and `_rule_of` after PR #74.

None of these changes a result.

### 11.7 Verdict

Pass 3 was not passed (open P1: F4, fixed in PR #48). The owner authorised one bounded re-verification pass, pass 4.

Pass 4 was not passed (W1 to W3, C1, A7, F5 and two review P1s, fixed in PRs #51 to #65). Pass 5, at `b34c721`, is not passed by the Claude auditor: X1, X2 and L1 are reproduced P1s (fixes in PRs #69 to #71).

The owner authorised pass 6 on 2026-10-29 (17:13 UTC, in the chat); it is pinned at `main` `1dca8d75ab6f49a82397cd493714d8602131538b`, the merge of #68, which holds every fix of passes 1 to 5.

**Pass 6, Codex.** The full-tree review runs as Codex's automatic review of PR #73. The branch `audit/pass6-full-tree` (`fc93e11`) is an ours-merge of the pin `1dca8d7` with the empty orphan base `994a014`, opened against `audit/empty-base`. The PR is never merged, and its T-09 is red by construction. The review started at 17:39 UTC. The Claude side of pass 6 is a fresh session (session 8), which classifies the Codex findings.

Pass 6, at `1dca8d7`, is not passed: Y1 and E1 (Claude) and 6-3 (Codex) are reproduced P1s (fixes in PRs #74, #75, #77). Codex pass 5 was not received.

**Trend of reproduced P1s**, as the pass-6 auditor records it:
- pass 1: Claude 1;
- pass 2: Codex 4, Claude 0, fix-PR reviews 1;
- pass 3: Claude 1;
- pass 4: Claude 6, fix-PR reviews 2;
- pass 5: Claude 3;
- pass 6: Claude 2, Codex 1 new (6-1 is Y1).

**Pass 7** is pinned at `main` `c55e4cee65656355850bde32b07059e37d8b523b`, the merge of #81 (coordinator, 2026-10-29); every reproduced finding of passes 1 to 6 is fixed there. A fresh session (session 9) runs the Claude side.

<PENDING: pass 7 of both auditors; "passed at <SHA>: neither auditor reproduced a P1" when a pass passes.>
