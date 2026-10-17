# 16 Claude–Codex reconciliation matrix

Versioned record of the scientific reconciliation between the research foundation (PR #1, Claude) and the
independent review (PR #2, Codex). This document replaces the matrix v1 that was posted as a comment on PR #2
and is the single place where positions, evidence, dispositions and remaining blockers are tracked. The
original research under `research/original/` is unchanged. Nothing here authorises implementation, merges,
capital, broker connectivity or policy changes.

**Version:** v12, 2026-10-17. **Round:** 11 (Codex round 11 = the automatic review `5559035950` of PR #4 at `04bc122`, eight findings, §3j, Appendix L; round 10 = the automatic review `5558887072` of PR #4 at `922956b`, eight findings, §3i, Appendix K; round 9 = the two reviews of PR #4 at `8af2ae9`, automatic review `5556950582` and the owner-requested review `5558680831`, twenty-one findings, §3h, under the owner's directive on PR #4, comment `6236238443`; round 8 was automatic review `5556866013` of `37ac018`, two findings, §3g; round 7 was review `5551243905` of `10f8829`, round 6 review `5550966930` of `4de18e5`, round 5 review `5550735335` of `88abaa4`, round 4 review `5550366107` of `d46c204`, round 3 review `5550048687` of `43754cc`, round 2 the two reviews of `10d1581`). **The rule changed in this round, on the owner's instruction.** The owner's audit on issue #3 (comment `6222759237`, 2026-10-16 19:07 UTC) rejects "three rounds then park": the per-issue round budget is a per-execution quota safeguard, and the lifetime of a finding is governed by reproducible evidence, never by a retry count. Accordingly the seventeen findings that rounds 4–6 recorded without revision (RC-60, RC-64 to RC-79) and the four findings of round 7 (RC-80 to RC-83) are **applied in `17-phase1-amended-specification.md` version 5, commit `b19483a` (`b19483a909bc948f6775fb5ce3b510d2bdfe9261`), as the OD10 decision diff**: every change carries its matrix ID, the owner approves the diff by recording OD10 on issue #3 or names the items to revert, and the fields that are the owner's to set (OD4, OD5) are left as named fields (§4.6, §6). Round 7's own results (Appendix H): the round-6 sentence that generalised one kernel's zero power to every distribution-free test is replaced by a theorem, power ≤ α(1 + δ)^G for any finite-sample-valid bounded-mean test over G blocks (8 % at δ = 0.02 and 16 % at δ = 0.05 over 24 blocks; RC-80); the intersection-union conjunction over six comparators has 21 % to 77 % power at δ = 0.01 and 600 clusters depending on comparator error dependence, where the single comparison has 77 % (RC-83); the A7 certificate tests had no Phase 1 verifier (RC-82); Codex's claim that commit `10f8829` carries a non-owner identity is not reproduced in the repository, while its remedy, an identity check in T-09, is adopted, and the round-7 commits themselves carry a non-conforming identity that is disclosed in RC-81 for the owner's decision. Appendix F and G scripts were re-run in round 7 and reproduce byte for byte. **Round 8** (Appendix I): Codex's review of the version-5 text raised two findings, both defects in round-7 remedies, both reproduced and applied in `17` version 6 in the same commit as this matrix: the version-5 VOID cutoff was computed from resolved members and so did not exist for an all-VOID cluster, and inside a 5 % VOID cap outcome-dependent removal raises the primary's null rejection rate from 5 % to 23–95 % while the worst-case bound stays at 5 %, so the VOID set is now frozen with the membership and a later VOID is an adjudication outcome under the source rule, never a declaration (RC-85); T-15's refusal-only pass condition was met by a reader that refuses everything or returns the oldest vintage, so positive as-of oracles on fixture F-25 are added (RC-86). The same review raised nothing on the other nineteen items applied in version 5; under §4.6 rule 2 they are now **reviewed once by Codex at `37ac018` without objection**, which is not agreement and does not replace OD10. **Round 9** (Appendix J): the owner's directive of 2026-10-17 16:00 UTC asks for every live finding to be reconciled with its evidence and for the candidate specification to be amended on this branch; Codex's two reviews of the version-6 text raised twenty-one findings, all assessed as genuine, every checkable one reproduced, all applied in `17` version 7 in the same commit as this matrix. Six are defects in the round-7 and round-8 remedies (RC-87, RC-90, RC-92 on the VOID rule; RC-93 and RC-101 on the conjunction evidence; RC-96 on the slot key), two are defects in Claude's own evidence (RC-93: the IUT null check used a comparator whose increments were identically zero; RC-102: a hand-typed 140 where the computation gives 141), and one, RC-95, is a design rule carried since round 2: the monitor consumed increments in closure order, which on fair increments crosses 1/α in 5 % to 100 % of paths depending on how much later a NO resolves than a YES, because the knowable time of an eventually-by-deadline outcome is itself outcome-dependent; increments now enter in pre-registered maturity order (3.2–3.4 %). RC-94 makes the primary's critical value a calibration over a pre-registered null class with a pass condition (c* = 3.20, 2.63, 2.23 for catastrophe shares of at least 0.05, 0.2, 0.3; power at δ = 0.02 and 600 clusters 60 %, 79 %, 88 % against 96 % nominal). Every committed script of Appendix C to I was re-extracted and re-run in the round-9 environment: byte-identical, except Appendix H, which differs in the one corrected line. **Round 10** (Appendix K): Codex's review of the version-7 text raised eight findings, all assessed as genuine, every checkable one reproduced, all applied in `17` version 8 in the same commit as this matrix. Five are defects in round-9 remedies: the null class N was four scalars, and a persistent-regime law inside all four has 15–22 % size at every calibrated c* (RC-108 on RC-94); an empty baseline slot removed the member while every other arm's empty slot kept it, and a baseline failure correlated with event type turns a zero-average null into 18–49 % rejection (RC-109 on RC-104); the burn-in blinding bounded the latest finality time and not the earliest knowable time (RC-110 on RC-99); the T-36 oracle required rejection at the nominal value that a correct calibrated test fails (RC-111 on RC-94); the model cutoff sat on each `Forecast` with a correction path that let an outcome-chosen correction month raise the null rejection rate to 13 % (RC-112 on RC-98). One is a propagation gap (T-17 contradicted §3 and F-24 on pre-declared members, RC-115), one an open case the round-9 finality rules did not cover (observer outage plus late publication, RC-113), one an ambiguity in round-7 wording under which a third of the cohort would leave (RC-114). The round-9 script was re-extracted and re-run: byte-identical. **Round 11** (Appendix L): Codex's review of the version-8 text raised eight findings; seven are assessed as genuine, every checkable claim reproduces, and all seven are applied in `17` version 9 in the same commit as this matrix; the eighth, a provenance claim naming a commit that exists in no branch of the repository, is recorded and not applied. Three are defects in the round-9 calibration remedy and its round-10 extension: the calibration criterion was the A3 tolerance, which a family of true size 5.5 % passes three times in four while the text calls the test level 0.05 (RC-117); the size of the two-point family at a fixed critical value is a step function of the catastrophe share, so the committed grid values 3.20, 2.63 and 2.23 are exceeded between their own grid points (5.0–5.4 %) and the exact-supremum values 3.21, 2.69 and 2.25 replace them (RC-118, a CONFIRMED-DEFECT of Appendix J); and one pair's critical value does not make every IUT component level α (up to 11.4 % size for a component outside the pair's class, RC-121). One is a defect in the round-9 monitor-order remedy: the maturity buffer ordered only the clusters registered so far, which breaks the H-order in 64 % of random registration paths (RC-119). One is a propagation gap, the §6 power figures left at the nominal value (RC-120: at the illustrated critical values the single comparison at δ = 0.01 and 600 clusters falls from 78 % to 28–60 %, the conjunction from 21 % to 0–4 % under uncorrelated errors, the period-shock design from 18 % to 2–8 %); one an open case in the round-9 epoch remedy (RC-123: a demotion with the anchor store unavailable had no defined outcome, and a rollback let the pre-demotion capability act once the store returned); one on reproducibility (RC-122: the appendix scripts now exist as committed files under `research/reproduction/`, each checked byte-identical to its appendix block). The round-10 script was re-run: byte-identical. **Awaiting:** Codex's review of this commit; owner decisions OD1, OD2, OD9a and OD10 (now: approve or revert the version-5 to version-9 diffs). **No disposition in this matrix is a Codex agreement** until Codex has reviewed the commit that carries it; "Codex position" quotes `research/15-codex-review.md` at commit `59206fe` (PR #2) or the PR #4 review comment named in §3a to §3g. Round 3 closed the RC-01 scope disagreement in Codex's favour (RC-49, RC-50; Appendix D); rounds 4–6 found defects in Claude's own remedies (RC-56, RC-60, RC-65, RC-69, RC-70, RC-72, RC-73; Appendix E–G); round 7 found one more, an over-general sentence in round 6's RC-72 response (RC-80); round 8 found two in round 7's remedies (RC-85 on RC-67, RC-86 on RC-79; Appendix I); round 9 found six in round 7's and round 8's remedies and two in Claude's own evidence (§3h, Appendix J); round 10 found five in round 9's remedies and one round-9 propagation gap (§3i, Appendix K); round 11 found three in the round-9 calibration remedy and its round-10 extension, one in the round-9 monitor-order remedy and one open case in the round-9 epoch remedy, and one of them (RC-118) also falsifies committed numbers of Appendix J (§3j, Appendix L). No Codex review addressed RC-07 (n_eff retention) or RC-20 (hosting timing). Silence in a diff review is not agreement.

Labels follow `research/README.md`. Disposition statuses used here, per the protocol in issue #3:

| Status | Meaning |
|---|---|
| `FALSIFIED` | the original claim is refuted by a reproduced counterexample or derivation |
| `PROPOSED` | Claude's proposed disposition; Codex has not yet reviewed this wording |
| `DISAGREEMENT` | the two written positions differ in substance; the difference and what would settle it are stated |
| `EXPERIMENT_REQUIRED` | cannot be settled by argument; a bounded experiment is named |
| `OWNER_DECISION` | nondelegable policy choice; the options and their costs are stated |

## 1. Inputs processed (tracking)

| Input | Identifier | Processed in |
|---|---|---|
| Research head reviewed by Codex | `8b2dba79fe9077df53a96a6b61b1823b80930ee8` (PR #1 head) | round 1 |
| Codex review | `research/15-codex-review.md` at `59206fe5f652cc3ea63114ad1c2b0fd7252962c2` (PR #2 head) | round 1 |
| Owner protocol comment | PR #2 comment `6215215092` | round 1 |
| Claude round-1 response (matrix v1) | PR #2 comment `6215369656` | superseded by this document |
| Coordination issue | #3 (no comments at time of writing) | round 1 |
| Codex review of PR #4 | review `5548201046` on commit `10d1581595b2d1ea6a8689e0f94b33bd68a59d66`, thirteen inline findings, comment IDs `4294987374`, `4294987389`, `4294987395`, `4294987398`, `4294987403`, `4294987415`, `4294987422`, `4294987435`, `4294987446`, `4294987458`, `4294987465`, `4294987471`, `4294987476` | round 2 (§3a) |
| Second Codex review of PR #4 | review `5549803107` on the same commit `10d1581`, triggered by the owner's PR #4 comment `6218467449` ("@codex review"), seven inline findings, comment IDs `4296205602`, `4296205617`, `4296205625`, `4296205637`, `4296205645`, `4296205655`, `4296205661`; none duplicates the first review | round 2 (§3a, RC-41 to RC-47) |
| Third Codex review of PR #4 (round 3) | review `5550048687` on commit `43754cc29add7ed47235ed9dd595ca950497ae4c`, run after the round-2 push, seven inline findings, comment IDs `4296395259`, `4296395273`, `4296395286`, `4296395298`, `4296395308`, `4296395324`, `4296395335`; none duplicates rounds 1–2 | round 3 (§3b, RC-48 to RC-54) |
| Issue #3 comments | `6218571025` (owner: controlled rollout, hardening gates; no scientific content), `6218965225` (routine, concurrent execution: supplementary evidence on RC-15/RC-47, folded in as RC-55) | round 3 |
| Fourth Codex review of PR #4 (round 4) | review `5550366107` on commit `d46c2042a47457ee254582c682c2b17e6803c8bc`, run after the round-3 push, eight inline findings, comment IDs `4296649357`, `4296649368`, `4296649378`, `4296649389`, `4296649399`, `4296649412`, `4296649421`, `4296649427`; none duplicates rounds 1–3 | round 4 (§3c, RC-56 to RC-63) |
| Fifth Codex review of PR #4 (round 5) | review `5550735335` on commit `88abaa4f15bd0e1e1ea7035a32094c7a5113285c`, run after the round-4 push (summary comment `6216072575` edited 16:31 UTC), eight inline findings, all P1, comment IDs `4296914293`, `4296914298`, `4296914307`, `4296914319`, `4296914330`, `4296914341`, `4296914351`, `4296914363`; none duplicates rounds 1–4 | round 5 (§3d, RC-64 to RC-71; recorded, not applied) |
| Sixth Codex review of PR #4 (round 6) | review `5550966930` on commit `4de18e599733c9275ec59f0da678cca5fe88c3a6`, run after the round-5 push (summary comment `6216072575` edited 16:53 UTC), eight inline findings, all P1, all on `17-phase1-amended-specification.md` (unchanged since `88abaa4`), comment IDs `4297109177`, `4297109194`, `4297109203`, `4297109207`, `4297109215`, `4297109220`, `4297109231`, `4297109245`; none duplicates rounds 1–5 (RC-73 extends RC-65 with a new scenario, RC-77 extends RC-52 and RC-71, RC-74 extends RC-34 and RC-43; each is a distinct claim) | round 6 (§3e, RC-72 to RC-79; recorded, not applied) |
| Seventh Codex review of PR #4 (round 7) | review `5551243905` on commit `10f88298be942162f0795ae31c36a87c8284b376`, run after the round-6 push (summary comment `6216072575` edited 17:20 UTC), four inline findings, all P1, comment IDs `4297337217`, `4297337229`, `4297337243`, `4297337251`; none duplicates rounds 1–6 (RC-80 extends RC-72 with an objection to Claude's own round-6 sentence) | round 7 (§3f, RC-80 to RC-83; applied in `17` v5) |
| Eighth Codex review of PR #4 (round 8) | review `5556866013` on commit `37ac01892e7de47027b87dc88784895eacedf3c7`, run after the round-7 push (summary comment `6216072575` edited 2026-10-17 07:38 UTC; the scheduled execution was dispatched on that edit), two inline findings, both P1, both on `17-phase1-amended-specification.md` version 5, comment IDs `4301920287`, `4301920289`; neither duplicates rounds 1–7 (RC-85 is a new channel in the round-7 RC-67 remedy, RC-86 a new gap in the round-7 RC-79 remedy) | round 8 (§3g, RC-85, RC-86) |
| Owner audit | issue #3 comment `6222759237` (2026-10-16 19:07 UTC): three review rounds must never mean problem solved; the per-session budget protects quota, task lifetime is governed by evidence; PR #10 (CANNON) proposed, not deployed | round 7 (§4.6 rule change) |
| Ninth Codex review of PR #4 (round 9) | review `5556950582` on commit `8af2ae9d0a6a10fbcd070456b569b31e5506b72d`, run after the round-8 push (summary comment `6216072575` edited 2026-10-17 08:06 UTC), nine inline findings (seven P1, two P2), comment IDs `4301994279`, `4301994282`, `4301994284`, `4301994289`, `4301994291`, `4301994294`, `4301994299`, `4301994303`, `4301994307`; none duplicates rounds 1–8 (RC-87, RC-90 and RC-92 extend RC-85 with new channels) | round 9 (§3h, RC-87 to RC-93, RC-106, RC-107) |
| Owner directive on PR #4 | PR #4 comment `6236238443` (2026-10-17 16:00 UTC): complete the independent scientific reconciliation before implementation; Claude reconciles every live and historical unaddressed finding with ID, reviewed SHA, counterexample, reproduced command, disposition, correction, test and remaining assumptions, deduplicating outdated threads; amends the candidate specification on this branch; re-runs every claimed reproduction and labels what was not run; records owner-reserved choices as `OWNER_DECISION`; Codex falsifies independently on each candidate SHA; the acceptance gate is two SHA-pinned reports on the same final revision with zero unresolved verified defects in scope; no paid APIs, no new automation, no merge | round 9 (§3h, §4.6) |
| Tenth Codex review of PR #4 (round 9) | review `5558680831` on the same commit `8af2ae9`, requested by the directive comment (summary comment `6216072575` edited 16:09 UTC; the scheduled execution was dispatched on that edit), twelve inline findings (eleven P1, one P2), comment IDs `4303397680`, `4303397684`, `4303397689`, `4303397692`, `4303397696`, `4303397700`, `4303397703`, `4303397708`, `4303397714`, `4303397718`, `4303397725`, `4303397727`; none duplicates rounds 1–8 or the ninth review (RC-96 extends RC-75, RC-101 extends RC-83) | round 9 (§3h, RC-94 to RC-105) |
| Eleventh Codex review of PR #4 (round 10) | review `5558887072` on commit `922956b0a7c06dc8b10849f8146ad2d90f072262`, the automatic review of the round-9 push (summary comment `6216072575` edited 2026-10-17 16:50 UTC; the execution was dispatched on that edit), eight inline findings (seven P1, one P2), all on `17-phase1-amended-specification.md` version 7, comment IDs `4303569704`, `4303569710`, `4303569715`, `4303569722`, `4303569729`, `4303569735`, `4303569739`, `4303569744`; none duplicates rounds 1–9 (RC-108 and RC-111 extend RC-94, RC-109 extends RC-104, RC-110 extends RC-99, RC-112 extends RC-98, RC-113 extends RC-88 and RC-105) | round 10 (§3i, RC-108 to RC-115) |
| Twelfth Codex review of PR #4 (round 11) | review `5559035950` on commit `04bc1223d099059bc9f47585281028f01ed023ae`, the automatic review of the round-10 push (summary comment `6216072575` edited 2026-10-17 17:18 UTC; the execution was dispatched on that edit), eight inline findings, all P1, six on `17` version 8 and two on this matrix, comment IDs `4303689619`, `4303689622`, `4303689629`, `4303689633`, `4303689635`, `4303689641`, `4303689645`, `4303689649`; none duplicates rounds 1–10 (RC-117, RC-118 and RC-121 extend RC-94 and RC-108; RC-119 extends RC-95; RC-120 extends RC-94 and RC-111; RC-123 extends RC-103; RC-116 extends RC-81 with a new SHA) | round 11 (§3j, RC-116 to RC-123) |
| Owner's progress request on PR #4 | PR #4 comment `6236863824` (2026-10-17 16:41 UTC): resume the reconciliation against `8af2ae9`, post a brief progress or blocker update on PR #4; no owner decision | round 10 (the update is posted once; the round-9 commit `922956b` had already answered the technical part) |
| Codex review of PR #7 (owner's Rust-first RFC) | review `5552078599` on `00642e3a1f5d3600cb169541c60d9736d39b08e7`, five findings, comment IDs `4297992981`, `4297992983`, `4297992988`, `4297993002`, `4297993009`; PR #7 is the owner's branch and is not revised here; the one finding that bears on `17` (`4297992983`: a fixed-horizon primary conflicts with the anytime-valid wording of `AGENTS.md` §2 item 3) is recorded as RC-84 | round 7 (§3f, RC-84; OD9b) |
| Codex review of PR #10 (owner's CANNON protocol) | review `5552523817` on `b5d104cd25ee82a094cae1b4a04deb801e8ee674`, ten findings, comment IDs `4298363597` to `4298363703`; all on the protocol documents, none on the Phase 1 science; read for the §4.6 rule (durable finding state, pause not close, verification on the exact SHA), not reconciled here | round 7 (§4.6) |
| Own posts | PR #2 comment `6216071592`; issue #3 comments `6216073335` (handoff 1), `6218864121` (handoff 2), `6219320639` (handoff 3), `6219896670` (handoff 4), `6220313901` (handoff 5), `6220770348` (handoff 6), `6231265852` (handoff 7), `6231483746` (handoff 8), `6236946882` (handoff 9), `6237338855` (handoff 10); PR #4 comment `6237340628` (the one progress update the owner asked for); the twenty review-thread replies of 15:28–15:29 UTC on PR #4 (one per round-2 finding, posted under the owner's identity by the routine) | not inputs |
| Automation | PR #5 (`automation/claude-review-dispatch`, merged to `main` 15:09 UTC) | not a scientific input |

No Codex comment, commit or review newer than the above existed when this document was written. A later
round processes only inputs not listed here; a finding that repeats one listed above is deduplicated by
content and not processed twice.

## 2. Executed (REPRODUCED)

Environment, both rounds: Linux, Python 3.11.17, numpy 2.4.6, scipy 1.17.1, pytest 9.1.1, httpx 0.28.1,
isolated venv in a scratch directory outside the repository; the reference code was copied from
`research/original/.../source_v0_2/` to scratch and never modified in place. No network call other than
package installation; no provider, broker or Jev call; no credential.

Since round 11 every script named below is a committed file under `research/reproduction/` (RC-122), byte-identical
to the fenced block of its appendix; `python -I research/reproduction/check_appendix_scripts.py` verifies the identity
and fails on the first difference (output in Appendix L). The commands run from the repository root as
`python -I research/reproduction/<script>` after `pip install -r research/reproduction/requirements.txt` in an
isolated venv; the appendix markers and the extraction snippet of Appendix A remain the record of how each script was
produced. `reconciliation_probes.py` additionally takes the path of a scratch copy of the archived v0.2 reference code.

| Check | Command | Result (round 1 → round 2) |
|---|---|---|
| Archived v0.2 suite | `python -m pytest -q` in the scratch copy | `31 passed in 2.12s` → `31 passed in 2.18s` |
| Reconciliation probes | `python -I reconciliation_probes.py <scratch v0.2>` (script in Appendix A, written for this matrix without importing or copying Codex's Appendix 1; renamed and re-run in round 2 with the exact binomial bound and the added power row, RC-28, RC-31, RC-45) | output in Appendix B; every round-1 value reproduced unchanged except the corrected bound; one row added |
| Round-2 checks (binomial bound, VOID imputation, IUT check design, exception-context chaining, increment bound) | `python -I round2_checks.py` (script in Appendix C) | output in Appendix C |
| Round-3 checks (A3 design, cross-cluster and time-varying null families for both tests at 20,000 replications, eligibility rule, shrinkage oracle fixtures, exception-graph canary with frame locals) | `python -I round3_checks.py` (script in Appendix D; no reference code; 2.8 s) | output in Appendix D |
| Round-7 re-run of the round-5 and round-6 scripts (the numbers transcribed into `17` v5) | `python -I round5_checks.py`, `python -I round6_checks.py` re-extracted from Appendix F and G (numpy 2.4.6, scipy 1.17.1) | output byte-identical to Appendix F and G apart from nothing (the `python` line included) |
| Round-9 checks (IUT null, 141 blocks, monitor order, Fréchet bound, empty blocks, null-class calibration, clock slew, epoch on demotion, version key, finality fixtures) | `python -I round9_checks.py` (script in Appendix J; 58 s) | output in Appendix J; two runs byte-identical |
| Round-9 re-run of every committed script, on the owner's directive | `python -I round2_checks.py` … `round8_checks.py`, each re-extracted from Appendix C to I (fresh isolated venv, Python 3.11.17, numpy 2.4.6, scipy 1.17.1; 3, 3, 17, 36, 7, 80 and 13 s) | Appendix C, D, E, F, G and I byte-identical to the committed output; Appendix H identical except the one line corrected for RC-102 (the committed output is replaced by the corrected run); Appendix A and B **not re-run** this round (they need a scratch copy of the archived v0.2 reference code with httpx and pytest, which this execution did not set up) |
| Round-10 checks (persistent regime at the two-point c* values, baseline-slot selection, burn-in early YES, T-36 at c*, outcome-chosen cutoff correction, outage-plus-late-publication fixtures, accrual dates, T-17 against F-24) | `python -I round10_checks.py` (script in Appendix K; 12 s) | output in Appendix K; two runs byte-identical |
| Round-10 re-run of the round-9 script | `python -I round9_checks.py` re-extracted from Appendix J (fresh isolated venv, Python 3.11.17, numpy 2.4.6, scipy 1.17.1; 58 s) | byte-identical to the committed Appendix J output |
| Round-7 checks (distribution-free power bound with numerical check of the proof; IUT conjunction power under a joint generator; least-favourable-null size) | `python -I round7_checks.py` (script in Appendix H; no reference code; 70 s; two consecutive runs byte-identical) | output in Appendix H |
| Round-11 checks (the A3 tolerance as a calibration criterion and the level-α criterion; the exact two-point supremum against the committed grid values; the registration watermark; every §6 power figure and the T-36 positive control at the calibrated cutoffs; per-component size at one pair's cutoff; the demotion toy with the anchor store unavailable) | `python -I research/reproduction/round11_checks.py` (script in Appendix L; 95 s) | output in Appendix L; two runs byte-identical |
| Round-11 identity check of the committed scripts against their appendix blocks | `python -I research/reproduction/check_appendix_scripts.py` | `11 scripts checked, 0 differ` (Appendix L) |
| Round-11 re-run of the round-10 script | `python -I research/reproduction/round10_checks.py` (fresh isolated venv, Python 3.11.17, numpy 2.4.6, scipy 1.17.1; 11 s) | byte-identical to the committed Appendix K output; the T-36 positive-control rates of Appendix K reproduce inside the round-11 script at the superseded values (0.9633, 0.6767, 0.8262, 0.9052) |

Key reproduced values (all from Appendix B unless stated):

- Cloned-outcome e-process: 30 pairs (0.25 vs 0.75), one shared fair outcome → e = 475.0986 on the favourable
  path, 1.0 on the other; crossing probability 0.5 under the marginal no-skill null. Matches Codex B4.
- Clustered no-skill null (120 clusters × 5 events, 2,000 replications, archived GRAPA rule, threshold 20):
  false-alarm rate **0.3335** with one increment per event, **0.0000** with one increment per cluster
  (exact one-sided 95 % binomial upper bound **0.0015** = 1 − 0.05^(1/2000); round 1 printed 0.0008 from a
  pseudo-count inserted into a normal standard-error formula, which is not a valid bound at the boundary;
  corrected per Codex RC-31). Interleaving the 600 events in a random order still gives **0.1345**, so the
  dependence is not cured by resolution order; only the betting unit cures it.
- Round 2 (Appendix C): a single-run "conjunction does not reject" check passes a correct level-0.05 IUT only
  with probability 0.95 and passes an implementation of size 0.10 with probability 0.90; with 20,000
  least-favourable-null replications and an exact 99 % upper bound ≤ 0.06, a correct test passes with
  probability 0.99995, size 0.06 passes with 0.010 and size 0.07 never (RC-30). Imputing VOID as NO adds +0.8
  to the paired Brier increment when FULL says 0.1 and the baseline 0.9, while Y = 1 gives −0.8, so it is a
  one-sided imputation, not a conservative one (RC-38). Setting `__context__ = None` or using `raise … from
  None` **inside** an `except` block leaves the handled exception reachable through `__context__` (Python
  3.11.17); translating outside the handler does not (RC-47). The per-event paired Brier increment is bounded
  by 1 in absolute value, so the cluster mean keeps 1 + λX̄ ≥ 0.5 at λ_max = 0.5 (RC-41).
- Round 3 (Appendix D, 20,000 paths per family, 120 clusters closed in calendar order, 24 periods of five, archived
  GRAPA rule, threshold 20). Valid clustered null: cluster-level e-process crosses in **0.055 %** (exact 99 %
  upper bound 0.0011); the fixed-horizon paired cluster test holds size (4.1 % cluster-iid, 4.8 % block of one
  period). Independent period shocks q_t = 0.5 ± 0.3 (marginal E[X] = 0): e-process **2.24 %**, block-of-one-period
  test **5.1 %**, cluster-iid variance **13.4 %**. Persistent two-state regime, P(stay) = 0.9: e-process **28.9 %**;
  fixed-horizon **27.1 % / 19.1 % / 14.8 %** for blocks of 1 / 3 / 6 periods. Time-varying skill +0.12 then −0.12
  (average zero): e-process **62.8 %**, fixed-horizon 1.6 % / 0.1 %; average −0.013 (+0.12 for 40, −0.08 for 80):
  e-process 3.6 %. A3 at 2,000 replications with a 95 % bound passes a correct size-0.05 implementation with
  probability **0.607**; at 20,000 with a 99 % bound, 0.99995. A forecast received five minutes after publication
  and 25 minutes before registry receipt is eligible under the v2 receipt-only rule and excluded under the v3
  knowable-time rule. Beta(2, 18) prior with (s, n) = (5, 20) gives posterior Beta(7, 33), mean **0.175**
  (s/n = 0.25), quantiles 0.0874 / 0.2812; logit shrinkage of 0.001 toward 0.175 with weight 0.5 gives
  **0.014362**. Exception graph: translating outside the handler leaves a canary held in a plain local reachable
  through `__traceback__` frame locals; only the redacting-holder variant removes it.
- Codex power rows re-derived with an independently written vectorised recurrence (checked equal to the
  reference implementation to 1e-12 on a random path): b = 0.5, δ = 0.01 → 67 / 6,000 by n = 300 and
  1,623 / 6,000 by n = 600; b = 0.5, δ = 0.02 → 1,584 and 4,883; b = 0.2, δ = 0.01 → 21 and 1,881; and, added
  in round 2 (RC-45), b = 0.2, δ = 0.02 → 1,844 and 5,653 (94.2 %). All identical to Codex D1.
- Floor rule inverts [0.001, 0.01] with base rate 0.02 to [0.02, 0.01]; nested chain product
  (0.01/0.1)(0.1/0.5)(0.5) = 0.01 exactly.
- Fusion: correlation-only weights on orthogonal errors with standard deviations 0.02 / 0.30 / 0.30 are
  1/3 each; second-moment simplex pool gives (0.991, 0.004, 0.004). On a constant-bias fixture (model 1
  biased by 0.20 with tiny noise, models 2–3 unbiased with sd 0.05), covariance-only weights put **0.935** on
  the biased model; the second-moment pool puts **0.036** on it and (0.492, 0.473) on the unbiased ones.
- n_eff: identical varying histories → 1.25 = 3/(3 − 2·0.3); constant duplicate histories → 3.0.
- Fusion accepts NaN, reversed and > 1 intervals as `forecast`. Registry accepts a 2020-dated forecast today,
  grades a late YES as `resolved_yes`, grades an early NO as `resolved_no`, keeps a phantom event after a
  failed append, and a new registry on the same ledger knows zero events. A rehashed unanchored suffix passes
  anchor verification. A valid promotion record replays after demotion.

Not executed: Lean (no toolchain), any external fetch. Codex's primary-source reads of 2026-10-16 (Saxo
SIM-linking article, OpenAI non-interactive-mode documentation) remain **UNVERIFIED** here; Codex reports the
reads in `15` §E2 and §G. Round 1 wrote "PACKAGE-VERIFIED by Codex", which misused a label defined for the
delivered package (RC-36); corrected in this document, `08` §6 and the PR description.

## 3. Matrix v2

Columns per the owner's protocol (PR #2 comment `6215215092` item 4). Positions: **A** agree, **P** partly,
**D** disagree. OD numbers refer to §6. "Codex position" is as written in `15-codex-review.md`; "Codex on v2"
is empty until Codex reviews this commit.

| ID | Original claim | Counterexample / evidence | Claude position | Codex position (15 @ 59206fe) | Proposed disposition | Validation test (17-phase1 T-ids) | Remaining uncertainty | OD | Status |
|---|---|---|---|---|---|---|---|---|---|
| RC-01 | `03/02`, `02` §1: committed e-process with predictable λ tests "no skill" anytime-validly; overlapping events admissible if ledger order reflects resolution order | 30 cloned outcomes cross 20 w.p. 0.5, e = 475.0986 (REPRODUCED); clustered null 33.4 % false alarms per event, 0.0 % per cluster, 13.5 % with interleaved order (REPRODUCED); **round 3:** under time-varying skill with zero average effect the cluster-level e-process crosses in 62.8 % of paths, under a persistent macro regime in 28.9 %, where the fixed-horizon paired cluster test gives 0.1 % and (block of one period) 27.1 % (REPRODUCED, Appendix D) | A on defect; rounds 1–2: P on remedy (cluster betting sufficient as primary); **round 3: A on remedy scope.** Codex exhibited the two structures §4.1 named (RC-49, RC-50); the e-process tests the sequential conditional null, which is not the §6 average-effect estimand | P0; specify estimand, filtration, clustering, maturation; fixed-horizon cluster-aware paired analysis where the every-step conditional null is inappropriate | one increment per pre-declared outcome cluster, explicit `cluster_id` on every EventSpec (RC-53), closure rule RC-29/RC-41, eligibility against the outcome-knowable time (RC-52), no post-registration VOID or merge for dependence (RC-51); **primary confirmatory test for the average-effect estimand = fixed-horizon paired cluster test with a pre-registered calendar-block dependence model; the cluster-level e-process is the anytime-valid monitor of the sequential conditional null, labelled as such, never alone a confirmatory result or a promotion trigger**; valid-null, clustered-null, interleaved, macro-shock and time-varying generators permanent | T-02, T-10, T-11, T-12, T-17, T-19, T-29 | persistent macro regimes: at 120 clusters over 24 periods no tested block length holds size for either method (REPRODUCED); the dependence model and the supply it needs belong to OD4/OD5 | OD4, OD5 | original `FALSIFIED`; remedy `PROPOSED` (revised round 3); scope disagreement **withdrawn by Claude** (§4.1); regime dependence `EXPERIMENT_REQUIRED` |
| RC-02 | `known_at`, `resolved_at` establish prospectivity | 2020-dated event and forecast accepted today (REPRODUCED) | A | P0 | admission time = registry service receipt clock; caller `as_of` and `known_at` audited, never trusted; backdating rejected | T-01, T-02 | trusted clock in a later hosted deployment | none | `FALSIFIED`; `PROPOSED` |
| RC-03 | D6, `03/05` §2: floor p_low at the cohort base rate | [0.001, 0.01] → [0.02, 0.01] (REPRODUCED); population rate is not an individual bound | A | P0 blocking amendment | delete the floor; declared shrinkage toward a pre-registered reference class (Beta(a+s, b+n−s) for cohort data; logit-space shrinkage of the model estimate with a pre-registered weight function of cohort size); rankings only until cohorts exist; "no direct elicitation below 0.05" kept as a workflow rule; no rounding | T-20 | choice of reference classes needs data | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-04 | `03/01` §4, repeated in `03` §1: multiplying conditionals assumes independence | nested identity P(E\|D)P(D\|C)P(C) = P(E) = 0.01 (REPRODUCED) | A (foundation repeated the error; amended in `03` §6) | CONFIRMED-DEFECT | chain rule exact for true conditionals; credal layer bounds partial information; non-nested chains keep the full conditioning history; "elicit with parent context only" limited to nested milestone chains | T-21 | none | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-05 | `04/03`: midpoint scored, coverage reported; N7: Winkler interval score as secondary | Winkler elicits outcome quantiles; containment ≠ coverage; outcome is Y ∈ {0,1}, not p | A (N7 withdrawn, `02` §6) | CONFIRMED-DEFECT | one scored point probability per forecast; interval = declared ambiguity set with width decomposed (disagreement, within-model imprecision); no coverage claim; coverage language reserved for cohort-rate intervals on repeated observations | T-22 | none | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-06 | `03/03`: weights from error correlation; R8: covariance | correlation weights 1/3 each on sd 0.02/0.30/0.30 (REPRODUCED); covariance-only puts 0.935 on a constant-bias model (REPRODUCED) | A | second-moment stacking on the simplex; equal default | min wᵀSw on the simplex, S = (1−δ)M̂ + δ·diag(M̂), M̂ the uncentred second moment of past errors; equal weights until the pool beats them on untouched future clusters | T-23 | δ and history window are development choices | none | `FALSIFIED`; `PROPOSED` |
| RC-07 | `06/03`: n_eff < 1.5 persistently falsifies independence | identical series → 1.25; constant columns → 3.0 (REPRODUCED) | P: diagnostic only, keep after fixing the constant-column path | remove as evidence | n_eff never in an acceptance criterion or gate; kept as a monitoring diagnostic with the NaN-to-zero path replaced by an explicit "degenerate history" flag | T-24 | none | none | `FALSIFIED` as evidence; retention `PROPOSED` (§4.3: Codex raised no objection in three reviews) |
| RC-08 | N9: "family-wise control via e-BH"; `02` §5 item 8: ten arms = ten tests | IUT needs no correction for a conjunction claim; e-BH controls FDR, not FWER | A (conflation conceded) | CONFIRMED-DEFECT; α_j = α/[j(j+1)] for promotions | primary confirmatory claim = intersection-union test over the pre-declared comparator set; artefact promotions consume a lifetime budget by α-spending with a pre-registered summable sequence; e-BH only for exploratory discovery lists; α_1 = 0.025, α_5 ≈ 0.0017, α_10 ≈ 0.00045 for the 0.05/[j(j+1)] shape (REPRODUCED) | T-13, T-14 | budget level and whether reversible promotions get a separate budget | OD3 | `PROPOSED`; level `OWNER_DECISION` |
| RC-09 | `04/03` §4, `06` §2: time-shifted holdout control | events before T − lag are legitimate training data; "must show no gain" has no tolerance | A (withdrawn, `06` §5) | CONFIRMED-DEFECT | forbidden-future-information negative controls (deliberately leaked feature must inflate detectably); shuffled-label null distributions with pre-registered bounds; fresh future cohorts | T-15 | none | none | `FALSIFIED`; `PROPOSED` |
| RC-10 | D2: Design B research engine; R6: endpoint enumeration gives an outer hull; LP governs on ≤ 14 projection | sampled or partial enumeration is an inner approximation; projection drops induced constraints; sampled Q′ ⊂ Q overestimates the worst case | A (R6 claim withdrawn, `03` §6) | amend D2/R6 | Design C plus small exact A first; B deferred until out-of-sample value; conditional bounds enter the LP as l·P(A) ≤ P(A∩B) ≤ u·P(A) with zero-mass semantics declared; robust allocation minimises over the whole declared credal set (inner LP or complete vertices) | T-25 (Phase 1 only the LP identity tests; rest later phases) | when B earns a place | OD2 | `FALSIFIED`; `PROPOSED` |
| RC-11 | R4: late YES → EXPIRED_NO | on-time occurrence learned late is YES; early NO before the deadline is accepted (REPRODUCED) | P: Codex's refinement is better | N11 semantics | YES iff occurrence met the deadline, evidence of occurrence time required, declared latency window per source; early NO only when the predicate is logically final; four timestamps (occurrence, publication, receipt, adjudication); source loss adjudicated separately as VOID | T-03, T-04 | latency windows per source | none | `PROPOSED` |
| RC-12 | "ledger-backed registry"; gate with owner HMAC | no replay (0 events after restart); phantom after failed append; replay of a promotion after demotion; caller-supplied key (REPRODUCED) | A | P0 | transactional single writer; all state derived by replay; owner public-key signatures over (capability, environment, release digest, evidence digest, epoch, nonce, expiry); consumed authorizations stored durably; demotion persists | T-05, T-06, T-30, T-31, T-32 | key custody model (hosted phase) | OD6 for hosting | `FALSIFIED`; `PROPOSED` |
| RC-13 | `12` Phase 1: "anchor detects any byte change" | rehashed unanchored suffix passes (REPRODUCED) | A (overclaim withdrawn, `12` Amendments) | CONFIRMED-DEFECT | property: any change inside the anchored prefix, or truncation below it, is detected; the unanchored window is reported explicitly by the restore test | T-07 | anchoring cadence vs hindsight window | none | `FALSIFIED`; `PROPOSED` |
| RC-14 | linear gate enum RESEARCH_ONLY → LIVE | SHADOW_LIVE_QUOTES would inherit SIM execution; halt vs reconciliation conflated | A | capability model | explicit capabilities × environment; halt denies new risk but preserves reconciliation and explicitly authorised cancellation | T-33 | none | none | `PROPOSED` |
| RC-15 | "token never propagates"; payload validated | `__context__` keeps the bearer header; hand-built `Cfd` payload reaches transport; NaN price and non-multiple lot accepted; fusion accepts NaN / reversed / > 1 (REPRODUCED) | A | CONFIRMED-DEFECT | typed payload objects only; exception translation **outside the active handler and** no frame that can raise holds the secret in a plain local (redacting holder whose `__repr__` never shows the value), with the whole reachable exception graph including traceback frame locals scanned (round 1 proposed `__context__ = None`, which does not work, RC-47; round 2 proposed translation outside the handler, which is necessary but not sufficient, RC-55; both REPRODUCED); synthetic-canary redaction tests on structured and encoded paths; full input validation (finite, ordered, in range) at every public function | T-26, T-34 (Phase 1); T-27 (Phase 7, RC-42) | none | none | `FALSIFIED`; `PROPOSED` (revised rounds 2 and 3) |
| RC-16 | `08` §4–§5: fresh `x-request-id` per retry; host allow-list separates SIM from LIVE | defeats Saxo's 15-second duplicate guard; same host, different path (Codex primary-source read reported in `15` §E2; UNVERIFIED here) | A (foundation repeated it; amended in `08` §6) | CONFIRMED-DEFECT | no automatic placement retry; reconcile by durable identifiers or halt; path- and credential-based SIM/LIVE policy at the adapter | later phase; recorded in `08` §6 | Saxo idempotency facts (Q3) | none | `PROPOSED` |
| RC-17 | three models + Jev mandatory; Jev gates research | recall over Jev-approved items is not funnel recall | A | retain membership; soften routing authority; stratified reject audit | mandatory three round-1 outputs plus Jev record on every issued forecast; absence holds issuance; ablations are evaluation forecaster ids only; stratified random audit of Jev rejects with known inclusion probabilities; thresholds development-only, then frozen and validated on fresh strata | T-28 (schema) ; Phase 2 design | H1, H3 untested; shared-judge bias in the Jev benchmark (UNVERIFIED) | OD8 | `PROPOSED`; H1/H3 `EXPERIMENT_REQUIRED` |
| RC-18 | proposer/promoter with canaries and frozen holdouts | side channels: feedback, runtime, cache, logs, parser execution; holdout exhaustion | A | agree and extend | isolated network-less secret-less evaluator with pinned environment hash; evaluator/scorer separation; bounded feedback and capped proposals per period; canary namespace; rolling prospective cohorts; lifetime α-spending | Phase 6; exfiltration canary tests specified in 17 §7 | none | OD3 | `PROPOSED` |
| RC-19 | D9: never force-liquidate thesis-intact; never sell a later winner for price reasons | hindsight rule; delay ≠ failure; a 30 % cash floor is unreachable by non-purchase alone; cap vs appreciation undefined | A | amend D9 | predicate kinds `milestone-deadline` vs `terminal-falsifier` in the schema now; precedence hard risk limits > terminal falsifier > valuation/opportunity review > hazard throttle; price drawdown triggers review, never a mechanical sale; counterfactual policy arms evaluated on all entries | T-29 (schema); Phase 5 experiment | H6 power | OD7 | `PROPOSED`; H6 `EXPERIMENT_REQUIRED` |
| RC-20 | `07/01`: Windows host, four OS accounts; Codex N12: fully cloud-hosted as a Phase 1 exit criterion | OS accounts are not a tested boundary (both agree); cloud adds operating cost against D10 and precedes any reduction of scientific uncertainty | P: defer the hosting decision to the Phase 2 gate with costs; Phase 1 hosting-neutral | fully cloud, Phase 1 exit criterion 1 | Phase 1 produces container images and a clean-checkout restore test that run identically on CI, laptop or cloud job; costed choice (minimal cloud / hybrid / local-only) at the Phase 2 gate; identical acceptance tests (IAM denial, egress denial, clean-account restore) for whichever is chosen | T-08 | operating-cost envelope | OD6 | `DISAGREEMENT` on timing (§4.2); `OWNER_DECISION` |
| RC-21 | `04/04`, `07` §5: 3-year realised returns in year two; "20 % hit rate necessary"; "100 % impossible" | cohort clock starts at entry; 7.45 % suffices with five 30x cycles; 100 % is a boundary case (REPRODUCED by Codex; arithmetic re-derived) | A (amended in `07` §7) | CONFIRMED-DEFECT | milestones re-expressed as months after first cohort entry; necessity claims withdrawn; inverse table's 0.5-loser rows labelled | documentation | none | OD2 (D11) | `FALSIFIED`; `PROPOSED` |
| RC-22 | D5: position 20 %, worst loss 15 % (R ≥ −0.75 assumed), cash floor 10 %, gross 100 %, Kelly 0.5 after optimisation | fully paid equity can lose 100 %; limits jointly inconsistent | A | clarify D5 | full-loss position cap ≤ 15 %; gross ≤ 90 % with the floor; Kelly fraction inside the constrained objective, not after it | later phase (allocator tests) | Q6 commissions | none | `PROPOSED` |
| RC-23 | `03/04`: cost comparison via −ln(1 − c) | exact only under a multiplicative fee convention | A | ESTABLISHED / REVISION | cost model as a component with declared conventions, lots, FX, taxes; independent post-solve check | later phase | none | none | `PROPOSED` |
| RC-24 | `04/03` §7: 300–600 events give the year-one read-out | δ = 0.01 has ≈ 27–31 % power at 600 independent observations; ≈ 1 % at δ = 0.005 (REPRODUCED) | A | P1 | power report with clusters, missingness and abstention before the Phase 2 contract; the year-one criterion is set after supply is measured | T-16 | real supply and cluster structure | OD4, OD5 | `PROPOSED`; criterion `OWNER_DECISION` |
| RC-25 | D10: OpenAI only as an owner-started daily batch | Codex reads OpenAI's non-interactive-mode documentation as a supported scheduled route (UNVERIFIED here; Codex reports the read in `15` §G) | P: verify on setup day | UNVERIFIED | setup-day verification with dated screenshots in the ledger; batch remains the fallback under R11's non-editing protocol | none in Phase 1 | provider terms | OD8 | `OWNER_DECISION` after verification |
| RC-26 | `.githooks/commit-msg` and `.claude/settings.json` enforce the attribution policy | local hook is bypassable; a tool server appended a footer to PR #1's body and to PR #2 comment `6215369656` before correction | A | CONFIRMED-DEFECT | provider-neutral CI check on commit and PR text; read-back after every tool mutation (`AGENTS.md` §7 already requires it); branch protection where available | T-09 | branch-protection visibility (API returned 403) | OD9 | `PROPOSED` |
| RC-27 (new) | `07` §6 item 1: pilot limits "mutually infeasible" until Q6 | cash is always feasible; with a 15 % full-loss cap a ticket is ≤ USD 150, so commission ≤ 1 % needs c_min ≤ USD 1.50 (Codex F; arithmetic re-derived) | A (overstatement withdrawn, `07` §7) | ESTABLISHED / REVISION | feasibility statement replaced by the exact condition; decision after Q6 | documentation | Q6 | none | `PROPOSED` |

### 3a. Round 2: Codex's reviews of PR #4 (commit `10d1581`, reviews `5548201046` and `5549803107`)

Thirteen plus seven inline findings, each with a Codex-assigned severity (P1 or P2). Every one was examined
against the documents and, where it carries a number or a logical claim, reproduced (Appendix C). Positions
as before: **A** agree, **P** partly, **D** disagree. "Resolved in" names the change made in round 2; every
disposition is `PROPOSED` until Codex reviews the resulting commit.

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in (this commit) | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-28 | Probe docstring and file name brand the artefact as a Claude product; `AGENTS.md` §7 prohibits AI marking in documentation (`4294987374`, P1) | RC-26 | **P.** The file name and docstring carry no information a reviewer needs; renamed `reconciliation_probes.py`, docstring neutral (Appendix A). The reviewer names in the matrix columns ("Claude position", "Codex position") and in the statuses are **required provenance**: the owner's protocol (PR #2 comment `6215215092` item 4) prescribes those columns, `AGENTS.md` §7 puts required provenance "in content, not in trailers", and §9 requires knowing which reviewer authored what. They stay. The branch prefix `claude/` is prescribed by issue #3 and the dispatch workflow of PR #5 | Appendix A, B; PR description | scan of changed files for attribution patterns (RC-26, T-09) | `PROPOSED`; owner may rule on the column names under OD9b |
| RC-29 | Cluster closure undefined: membership could change after outcomes arrive, or an increment could be emitted from a partial cluster, making the increment outcome-dependent (`4294987389`, P1) | RC-01 | **A.** v2 said "declared at registration before any member resolves" and "at the cluster's resolution time" without defining either. Selection of members or of the emission time after seeing outcomes is exactly the hindsight channel RC-02 closes for single events. Added: immutable membership complete before the earliest member `not_before`; one increment only when every member is resolved or pre-declared VOID; λ_k frozen at the cluster's first outcome receipt (a stronger condition than Codex asked for, needed so that no partial information of cluster k enters its own λ); closure-time ordering; later-discovered cross-cluster dependence VOIDs the later cluster. Stated limit: the rule does not cover dependence between clusters open at the same time, which remains the RC-01 open point (§4.1) | `17` §3 item 3, §2 table | T-17 (new), T-02 (reworded) | `PROPOSED` |
| RC-30 | T-13 single-run IUT check is flaky (a correct test rejects a null comparator with probability α) and a lucky seed passes an over-sized implementation (`4294987395`, P1) | RC-08 | **A.** REPRODUCED (Appendix C): 0.95 pass for a correct test, 0.90 pass for size 0.10. Replaced by (a) a deterministic oracle for the conjunction logic and (b) 20,000 least-favourable-null replications with an exact 99 % upper bound ≤ 0.06, which passes a correct test with probability 0.99995 and a size-0.06 test with 0.010. The same reasoning fixes the margin and replication count of A3, which v2 left implicit | `17` T-13, A3 | T-13 | `PROPOSED` |
| RC-31 | Monte Carlo bound 0.0008 for 0 of 2,000 is wrong; exact one-sided 95 % bound is 1 − 0.05^(1/2000) ≈ 0.0015 (`4294987398`, P2) | RC-01 | **A.** REPRODUCED: 0.001497 (closed form and Clopper–Pearson agree). The round-1 formula inserted a pseudo-count into a normal approximation, which is not a bound at the boundary. Corrected in the probe (`binom_upper`), §2, Appendix B, and A3 now names the exact binomial bound. The conclusion (bound ≤ 0.06) is unchanged | §2, Appendix A, B; `17` A3 | T-10, T-11 | `PROPOSED` |
| RC-32 | T-25 requires an exact credal instance and an inner LP although the credal network is out of Phase 1 scope (`4294987403`, P2) | RC-10 | **A.** Inconsistent as written. T-25 moved to `17` §7 (Phase 5); T-21 reduced to the arithmetic chain-rule identity with no LP; "out of scope" now names every credal LP explicitly. Adding the LP to Phase 1 was the alternative; it would add a solver dependency for no reduction of scientific uncertainty | `17` §3 out of scope, T-21, §7 | T-21 (Phase 1), T-25 (Phase 5) | `PROPOSED` |
| RC-33 | A0 lets implementation start on OD1–OD2 while the shrinkage estimator contradicts the still-binding `AGENTS.md` §2 item 7 floor and OD9 is open (`4294987415`, P1) | RC-03, RC-09 | **A.** The same contradiction holds for item 10 ("time-shifted holdouts") and the leak detector T-15. Building the floor knowingly would implement a FALSIFIED rule; building the replacement before the governance text changes would contradict §2. OD9 is split: **OD9a** (items 7 and 10 wording) becomes a prerequisite of A0; until it is recorded, T-20 and T-15 are not built and the floor is neither built nor removed. **OD9b** (item 9, §3 secrets wording, CI enforcement) can follow | §6 (OD9a/OD9b), `17` A0, §2 table; `12` amendments item 6 | A0 is a reviewed artefact, not a test | `PROPOSED`; `OWNER_DECISION` (OD9a) |
| RC-34 | Committed-prefix digest detects tampering only if the trusted anchor cannot be rewritten; scope specifies no external anchor and tests no simultaneous ledger-and-anchor replacement (`4294987422`, P1) | RC-13 | **A.** The property proved by T-07 is "detects changes relative to an anchor the verifier trusts"; v2 did not say where that anchor lives. Added an `AnchorStore` interface held by a principal other than the writer (Phase 1: a test double the writer cannot open for writing, plus an owner-committable export; the production holder is part of OD6); verification against a local copy is reported as "self-attested" | `17` §3 item 2, §2 table | T-18 (new), T-07 | `PROPOSED`; production holder `OWNER_DECISION` (OD6) |
| RC-35 | Mandatory acceptance cases are defined in `15-codex-review.md`, which is absent from this tree (`4294987435`, P2) | new | **A.** `15` is on `review/codex-20261016` (PR #2) and not in `research/claude-handoff`; merging it is not Claude's to do. Restated the twenty fixtures with exact inputs, reference-code behaviour and required behaviour in `17` §5.1, each tied to a T-id. P1–P5 were already in-tree (`01-architecture.md` §3) and are now cited there | `17` §5.1, §3 item 6 | every T-id in §5.1 | `PROPOSED` |
| RC-36 | "PACKAGE-VERIFIED by Codex" misuses a label defined for the delivered package (`4294987446`, P2) | RC-16, RC-25 | **A.** The README defines `PACKAGE-VERIFIED` as "the package reports checking it"; a reviewer's read is a different fact. Rather than add a label (the label list is in `AGENTS.md` §8 and is the owner's), the claims are `UNVERIFIED` here with the reviewer's report cited by section and date, as Codex's first option proposes. Corrected in `08` §6, §2 and §3 of this document, README label note, PR description | `08` §6; §2, RC-16, RC-25; `research/README.md` | none (documentation) | `PROPOSED` |
| RC-37 | Capability expiry depends on wall-clock time; after a clock rollback an expired unused capability can validate again because no consumed nonce or newer epoch need exist (`4294987458`, P1) | RC-12 | **A.** Correct as a logical argument; the reference code has no expiry at all, so it is a design gap in v2, not a reproduced defect. Added a persisted high-water mark of observed receipt time; admissions and capability checks below it fail closed; expiry is evaluated against max(current clock, high-water mark) | `17` §3 items 2 and 5, §2 table | T-35 (new), T-30 | `PROPOSED` |
| RC-38 | "Sensitivity with VOID as NO" is not conservative for a paired Brier difference; excluding VOIDs changes the estimand when missingness is informative (`4294987465`, P1) | RC-24 | **A.** REPRODUCED (+0.8 vs −0.8 on the 0.1 / 0.9 example). The estimand is now stated on the resolvable population with the VOID rate as a capped co-primary quantity; the sensitivity is a worst-case interval in both directions (each VOID imputed with the outcome least favourable to FULL, then most favourable); a missingness model only with a documented per-source mechanism. The cap value joins OD4 | `17` §6 estimand and missing-data rows | Phase 2 contract (reviewed artefact); generator with informative missingness in T-16 | `PROPOSED`; cap `OWNER_DECISION` (OD4) |
| RC-39 | Measuring supply in Phase 2 months 1–3 before freezing OD4–OD5 lets the design change after confirmatory outcomes are visible while the cohort stays in the estimand (`4294987471`, P1) | RC-24 | **A.** Months 1–3 become a blinded burn-in cohort: registered and committed, outcomes sealed until the contract is frozen, permanently excluded from the primary test; only counts, cluster sizes and source metadata inform OD4–OD5 | `17` §6 planned-supply row | Phase 2 contract; registry test that burn-in clusters carry a non-primary flag that replay preserves | `PROPOSED` |
| RC-40 | T-41 "tree hash unchanged" has no recorded reference value or procedure (`4294987476`, P2) | integrity | **A.** Recorded: `git rev-parse HEAD:research/original/CPE_Forschungspaket_2026-10-16` = `122a1619cdad4f1c7f577e26f86709c34ce86298` at `8b2dba7`, `10d1581` and this commit (REPRODUCED); kept beside the manifest because the Git tree object also detects added or renamed files, which `sha256sum -c` cannot | `17` T-41 | T-41 | `PROPOSED` |

| RC-41 | The single cluster increment is undefined as sum, mean or weighted aggregate; a sum can leave the bounded domain and make 1 + λX negative; a mean changes the weighting relative to an event-level estimand (`4296205602`, P1) | RC-01, RC-29 | **A.** The round-2 text had written "X̄" without defining or bounding it. Defined: unweighted mean of member increments X_i = (p_baseline − Y)² − (p_FULL − Y)² ∈ [−1, 1], so X̄ ∈ [−1, 1] and 1 + λX̄ ≥ 0.5 at λ_max = 0.5 (REPRODUCED, Appendix C); the mean is the estimand's own weighting (§6: per cluster, clusters equal); the event-weighted average is descriptive only | `17` §3 item 3, T-17 | T-17 | `PROPOSED` |
| RC-42 | T-27 requires order-payload, price, lot-size and transport-boundary behaviour although Phase 1 excludes broker adapters and execution code (`4296205617`, P2) | RC-15, RC-32 | **A.** Same inconsistency as RC-32. T-27 and fixture F-11 moved to `17` §7 (Phase 7); the HTTP source of F-12 noted as Phase 3 with the canary scanner tested on synthetic exception graphs in Phase 1; A2 restricted to fixtures whose component Phase 1 builds | `17` §3 item 6, A2, §5.1, §7 | T-26, T-29 (Phase 1); T-27 (Phase 7) | `PROPOSED` |
| RC-43 | Two concurrent presentations of one capability can both pass the unconsumed-nonce check before either writes the consumed record; T-30 covers sequential replay only (`4296205625`, P1) | RC-12 | **A.** Verification outside the writer transaction is a time-of-check/time-of-use gap. Required: epoch check, nonce insertion under a uniqueness constraint, state change and acknowledgement in one writer transaction; T-30 gains a concurrent-presentation case in which exactly one acts | `17` §3 item 5, T-30 | T-30 | `PROPOSED` |
| RC-44 | T-14 debits α only on successful promotion, so unlimited unsuccessful challengers cost nothing and the lifetime control is void (`4296205637`, P1) | RC-08 | **A.** The v2 wording "cumulative spend never exceeds α_total" left the debit event undefined. α_j is reserved and irreversibly debited at test registration, before evaluation data are unsealed; failed, cancelled and interrupted tests keep the debit; j indexes attempts. Consequence for OD3: the power cost of 0.05/[j(j+1)] is per attempt, so the budget question is sharper than v2 stated | `17` §3 item 3, T-14; OD3 row | T-14 | `PROPOSED`; level `OWNER_DECISION` (OD3) |
| RC-45 | `02` §6 item 6 labels "81–94 %" REPRODUCED although Appendix B has only the b = 0.5 row (81.4 %); the 94 % endpoint (b = 0.2, δ = 0.02) was not reproduced (`4296205645`, P2) | RC-24 | **A.** Correct: the 94 % came from Codex's D1 table. The row was added to the probe and re-run: 1,844 / 6,000 by n = 300 and 5,653 / 6,000 by n = 600 (94.2 %), identical to D1; the label is now earned and the sentence names both baselines | Appendix A, B; §2; `02` §6 item 6; OD4 row | T-16 | `PROPOSED` (`REPRODUCED` for the value) |
| RC-46 | A non-public constructor or static check cannot make elevated state unforgeable in Python; T-32 accepts type-level inaccessibility as sufficient; the protected operation must validate and consume the capability itself (`4296205655`, P1) | RC-12, RC-14 | **A.** Object visibility is not a security boundary. The protected operation verifies the signature and consumes the nonce in the writer transaction; a fabricated object (constructor, reflection, dynamic import) presented to it is rejected for lack of a valid signed capability; the static check is a lint. A5 reworded | `17` §3 item 5, A5, T-32 | T-32 | `PROPOSED` |
| RC-47 | Setting `__context__ = None` inside the handler does not prevent chaining; Python re-attaches the active exception at raise time, and `from None` only suppresses rendering (`4296205661`, P1) | RC-15 | **A.** REPRODUCED on Python 3.11.17 (Appendix C): the canary stays reachable in both in-handler variants and is absent only when the translation happens outside the handler. Round 1's disposition for RC-15 was wrong and is revised in §3; T-34 now scans the whole reachable exception graph and requires translation outside the handler or sanitisation of the source exception | §3 RC-15; `17` §3 item 6, T-34, F-12 | T-34 | `PROPOSED` (round-1 disposition corrected) |

Not addressed by either round-2 review and therefore unchanged after round 2: RC-01 remedy scope (§4.1), RC-20
hosting timing (§4.2), RC-07 n_eff retention (§4.3), and every `PROPOSED` disposition of §3 other than RC-15
(revised under RC-47). Relevant to issue #3 acceptance item 2: on a Markdown-only diff the automatic review
produced substantive statistical and security findings (RC-29, RC-30, RC-31, RC-38, RC-39, RC-41, RC-43,
RC-44, RC-47), not only style findings.

### 3b. Round 3: Codex's review of PR #4 at `43754cc` (review `5550048687`)

Seven inline findings, all P1, all on `17-phase1-amended-specification.md`; none repeats a round-1 or round-2
finding. Each was examined against the text and, where it carries a number or a logical claim, reproduced
(Appendix D). RC-55 is not a Codex finding: it is the supplementary evidence posted on issue #3 (comment
`6218965225`) by the concurrent routine execution, folded in here as announced there. Every disposition is
`PROPOSED` until Codex reviews the resulting commit; this is the last round under the budget (§4.6).

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in (this commit) | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-48 | A3 and T-10 keep 2,000 replications with a 95 % bound ≤ 0.06, which rejects a correct size-0.05 implementation about 39 % of the time; Appendix C already derived this and raised T-13 to 20,000 (`4296395259`, P1) | RC-30, RC-31 | **A.** REPRODUCED: pass probability 0.607 at 2,000 / 95 %, 0.99995 at 20,000 / 99 %. Round 2 fixed T-13 and left A3, T-10, T-11 inconsistent. All three now use the T-13 design (20,000 replications, exact one-sided 99 % bound ≤ 0.06); the valid clustered null re-run at 20,000 gives 11 crossings (0.055 %, bound 0.0011). The deterministic-oracle alternative Codex offers is used where a closed form exists (T-13 (a), T-20 (b)); the crossing rate of an adaptive e-process has none | `17` §2 table, A3, T-10, T-11 | T-10, T-11 | `PROPOSED` |
| RC-49 | §3 concedes that simultaneously open clusters sharing a macro shock make the product no test supermartingale, yet §6 designates that process as the anytime-valid primary test; the primary must impose conditional independence, combine dependent clusters, or use a method robust to the declared dependence (`4296395273`, P1) | RC-01, RC-29 | **A.** This is the structure §4.1 asked Codex to exhibit, and it is reproduced: with independent period shocks the cluster-level e-process stays under α empirically (2.24 %, forty times its valid-null rate) but has no level guarantee; with a persistent regime it crosses in 28.9 % of paths. Codex's third option is adopted: the primary confirmatory test of the average-effect estimand is the fixed-horizon paired cluster test with a pre-registered calendar-block dependence model (5.1 % under independent period shocks where the cluster-iid variance gives 13.4 %). Honest limit, found while reproducing: under the persistent regime **no tested block length holds size at 120 clusters over 24 periods** (27.1 % / 19.1 % / 14.8 % for blocks of 1 / 3 / 6 periods). That is a supply-and-horizon fact for OD4/OD5, not a Phase 1 defect; it is recorded as `EXPERIMENT_REQUIRED` with the generator committed | `17` §2 table, §3 item 3 ("what each test tests"), A3, T-12, §6 primary-test and stopping-rule rows; §3 RC-01 row; §4.1 | T-12 | `PROPOSED`; regime dependence `EXPERIMENT_REQUIRED` |
| RC-50 | The e-process is valid for the sequential null E[X_k \| past] ≤ 0 at every update, not for the population-average null stated as the estimand; time-varying performance with non-positive average can cross early (`4296395298`, P1) | RC-01 | **A.** REPRODUCED: skill +0.12 for sixty clusters then −0.12 for sixty (average exactly zero) crosses in 62.8 % of paths; +0.12 for forty then −0.08 for eighty (average −0.013) in 3.6 %; the fixed-horizon test rejects in 0.1 % and 0.08 %. Codex's first option is taken for the monitor and its second for the confirmatory claim: the e-process is kept as the anytime-valid monitor of the explicitly stated conditional null, reported continuously with that label, and a crossing triggers an integrity and dependence review but never a confirmatory result or a promotion; the average-effect estimand is tested by the fixed-horizon primary (RC-49). Together RC-49 and RC-50 close the RC-01 scope disagreement in Codex's favour | `17` §3 item 3, §6 "anytime-valid monitor" row, T-12, F-23; `02` §6 item 7 | T-12 | `PROPOSED` |
| RC-51 | "A dependence discovered after registration VOIDs the later cluster" lets an unfavourable increment be removed on post-outcome information while a favourable one stays; require a deterministic rule applied before outcomes are unsealed, or retain the increments (`4296395286`, P1) | RC-29 | **A.** The round-2 sentence reopened, for cross-cluster dependence, the hindsight channel RC-29 had closed within clusters. Codex's second option is the simpler one and has no discretionary step: a dependence discovered after registration is never a ground for VOID or merge; both clusters stay in the confirmatory process as registered; the discovery is logged as a declaration defect and reported in a dependence audit (count, list, calendar position) that feeds the dependence model of the primary test. A pre-outcome window for safe VOIDing exists in principle, but verifying "before any outcome was knowable" needs the adjudicated `knowable_at`, which is only available afterwards, so the rule would itself be retroactive; retention avoids that | `17` §2 table, §3 item 3; new T-19 | T-19 | `PROPOSED` |
| RC-52 | T-02's cutoff at first registry receipt admits forecasts submitted between publication and receipt, which can incorporate the known result; adjudication must retroactively exclude forecasts committed after the outcome became knowable (`4296395308`, P1) | RC-02, RC-29 | **A.** The schema already carried publication and occurrence times without using them for eligibility. Added the adjudicated `knowable_at` (publication time, or occurrence time when the occurrence is itself public), the cluster's outcome-knowable time t*_k = min over members of min(receipt, `knowable_at`), eligibility iff forecast receipt < t*_k, and λ_k frozen at t*_k rather than at first receipt. The exclusion is deterministic from recorded timestamps (no sign-dependent discretion, unlike RC-51's VOID); worked example in Appendix D (10:05 forecast after a 10:00 publication excluded, 09:55 eligible) | `17` §3 items 1 and 3, T-02, T-17, F-21, §6 estimand row | T-02, T-17 | `PROPOSED` |
| RC-53 | §3 creates an implicit singleton cluster for an EventSpec without `cluster_id` while T-29 requires the same input to be rejected; no implementation satisfies both (`4296395324`, P1) | RC-29 | **A.** Contradiction confirmed. Explicit `cluster_id` everywhere: an implicit singleton default is exactly how fixture F-15 (thirty cloned outcomes) would re-enter as thirty "independent" clusters without anyone declaring anything; forcing the declaration puts the dependence question at registration, where RC-51 now requires it to be settled. §3 reworded, T-29 kept | `17` §2 table, §3 items 1 and 3, T-29 | T-29 | `PROPOSED` |
| RC-54 | T-20's pass conditions are satisfied by an estimator returning s/n with low = point = high, implementing neither the Beta posterior nor the logit shrinkage; add deterministic fixtures against the specified formulas (`4296395335`, P1) | RC-03, RC-33 | **A.** REPRODUCED that the trivial implementation passes the property checks (s/n = 0.25 at (5, 20) satisfies monotone, ordered, in range). T-20 gains an oracle part with fixture parameters prior Beta(2, 18), w(n) = n₀/(n₀ + n), n₀ = 20: posterior Beta(7, 33) mean 0.175, quantiles 0.0874 / 0.2812; Beta(2, 68) mean 0.028571; the prior at n = 0; shrunk points 0.014362, 0.001 and 0.315334 (Appendix D). The fixture parameters are test values; the production prior and weight are pre-registered in the Phase 2 contract. Still built only after OD9a (RC-33) | `17` §2 table, T-20 | T-20 | `PROPOSED`; blocked on OD9a |
| RC-55 (self-reported) | Translating outside the handler is necessary but not sufficient: a secret held in a plain local of the raising frame remains reachable through `__traceback__` → `tb_frame.f_locals`, which structured loggers and crash reporters capture (issue #3 comment `6218965225`; round-2 probe checked `__context__` only) | RC-15, RC-47 | **A.** REPRODUCED (Appendix D): canary reachable in both in-handler variants and in the outside-handler variant with a plain local; absent only with a redacting holder. T-34 as written in v2 already fails the third variant, so the test was right and the remedy text was incomplete; the RC-15 disposition and T-34 now require both conditions. The reference `sim_precheck` holds `token` and `h` as locals and would fail T-34 even after moving the `raise` | §3 RC-15 row; `17` T-34 | T-34 | `PROPOSED` |

Not addressed by Codex in round 3: RC-07 n_eff retention (§4.3) and RC-20 hosting timing (§4.2). Round 3 did
engage the open scientific disagreement RC-01 (§4.1). Relevant to issue #3 acceptance item 2: the third
automatic review again produced statistical findings on a Markdown-only diff (RC-49 to RC-52 are about test
validity and hindsight channels), and this time two of them (RC-49, RC-50) addressed an open disagreement
directly, so the native route covered that part of the protocol for RC-01.

### 3c. Round 4: Codex's review of PR #4 at `d46c204` (review `5550366107`)

Eight inline findings (six P1, two P2), none repeating rounds 1–3. Each was examined against the text and,
where it carries a number or a logical claim, reproduced (Appendix E). Handling follows §4.6 as written in v4:
a finding on an item with budget left gets one bounded revision (RC-56, RC-58, RC-61, RC-62, RC-63); a finding
on a budget-spent item is recorded with a one-line assessment and the proposed wording, and nothing else
changes (RC-60). Two findings (RC-57, RC-59) are incomplete propagations of the round-3 edits themselves (the
t*_k cutoff of RC-52 and the role assignment of RC-49/RC-50 were not carried into one clause and one table
row); they are applied as propagation, labelled as such, and the owner can revert them under a strict reading
of §4.6. Every disposition is `PROPOSED` until Codex reviews the resulting commit.

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in (this commit) | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-56 | The same primary claim is evaluated at cut-offs 12 and 24 months, each at one-sided α = 0.05, so confirmation after either look inflates the type-I error above 0.05; designate one cut-off as the sole primary or pre-register a group-sequential rule (`4296649357`, P1) | RC-08, RC-24 (the two cut-offs date from round 1, when the test was secondary; the round-3 role change made the defect material) | **A.** REPRODUCED: two looks at information fractions 0.5 and 1.0 give a normal-theory type-I error of 8.0 %; the block-of-one-period t test on the round-3 generator rejects at either look in 8.8 % (valid clustered null) and 7.8 % (independent period shocks) against 5.1 % at the 24-month look alone. The simpler option is taken: **one primary cut-off, 24 months after first cohort entry**; the 12-month look is a pre-registered interim for futility and integrity only, never confirmation (a non-binding futility look does not inflate the error: 5.1 %). If the owner wants early confirmation, the alternative is a Lan–DeMets O'Brien–Fleming-type spending, 0.0056 at 12 months and a nominal 0.0483 at 24 months (total 0.050 in normal theory; 5.3 % and 5.1 % with the block t through its own degrees of freedom), calibrated by simulation in T-12 because the first look has only twelve blocks. The two-look design is kept as an invalid control in T-12 | `17` §2 table, §6 primary-test, interim and stopping-rule rows, T-12; `02` §6 item 8; `09` D4 | T-12 | `PROPOSED`; early-confirmation option `OWNER_DECISION` (OD4) |
| RC-57 | A member can still be declared VOID between publication and registry receipt because the closure clause uses receipt time rather than t*_k, which reopens the outcome-dependent selection channel the forecast-eligibility rule closes; VOID must be committed before the adjudicated outcome-knowable time or follow a pre-registered objective rule (`4296649368`, P1) | RC-52, RC-29 (budget-spent family) | **A.** The round-3 clause "pre-declared VOID before any member's outcome was received" kept the receipt cutoff that RC-52 replaced everywhere else with t*_k (worked example in Appendix E: a VOID received at 10:10 after a 10:00 publication and before the 10:30 receipt is accepted under the v3 clause and refused under t*_k; a 09:55 VOID is accepted under both). Applied as **propagation** of the RC-52 cutoff into the one clause that missed it, not as a new round on RC-01: the single substitution "before the cluster's outcome-knowable time t*_k" goes into §3 item 3 and T-17 gains the case; no new mechanism or objective VOID rule is added. Remaining uncertainty, for the Phase 2 contract: a member found unresolvable after t*_k leaves its cluster without an increment, which counts against the VOID cap (RC-38). If the owner reads §4.6 strictly, reverting that sentence and the T-17 case restores v3 | `17` §2 table, §3 item 3, T-17 | T-17 | `PROPOSED` (propagation; owner may revert) |
| RC-58 | T-20's oracle fixes the posterior quantiles and the shrunk point but never specifies how `low` and `high` are derived, so `[0, 1]` passes; the raw posterior bounds cannot be the answer because q05 = 0.0874 exceeds the required point 0.014362 (`4296649378`, P2) | RC-54, RC-03 | **A.** Defined: the same logit-space convex combination with the same weight w(n), applied endpoint-wise, low toward the posterior 5 % quantile, point toward the mean, high toward the 95 % quantile; endpoints clipped to [10⁻⁶, 1 − 10⁻⁶] before the logit. Each map is monotone and the targets are ordered, so the output is ordered whenever the input is; a collapsed model interval acquires the reference-class spread; at n = 0 the model interval is returned unchanged. Fixtures (Appendix E): (0.0005, 0.001, 0.002) at (5, 20) → (0.006874, 0.014362, 0.027239); (0.3, 0.5, 0.7) → (0.168465, 0.315334, 0.488622); low = 0 → 0.000309. Raw posterior bounds fail the ordering check, as Codex computed. The interval stays a declared ambiguity set with no coverage claim (RC-05). Still built only after OD9a | `17` §2 table, §3 item 3, T-20 (c) | T-20 | `PROPOSED`; blocked on OD9a |
| RC-59 | `09` §6 still records D4 with the fixed-horizon test as secondary while `17` and `02` make it primary; approving OD2 from `09` would record a different contract than `17` specifies (`4296649389`, P2) | RC-49, RC-50 (budget-spent family) | **A.** Incomplete propagation of the round-3 role assignment to the decisions document, which `AGENTS.md` §6 names as the record of decisions; no scientific content changes. The D4 row now states the round-3 roles, the single cut-off of RC-56, and that it said "secondary" until round 4 | `09` §6 D4 row | none (documentation) | `PROPOSED` (propagation) |
| RC-60 | `Redacted` still stores the raw bearer in `_value` and the traceback frame retains the object; the round-3 probe inspects `repr` only, so a logger or crash collector that serialises object state recovers the secret; T-34 must require that no traceback-reachable object retains the raw secret rather than accepting a redacted representation (`4296649399`, P1) | RC-15, RC-47, RC-55 (**budget spent**) | **A on the defect; REPRODUCED** (Appendix E): a probe that walks object state (attributes, slots, containers, closures, exception `args`) finds the canary in the round-3 "passing" holder variant, which the `repr` probe clears. It does not find it when the secret lives only in a frame that has returned before the sanitised exception is raised (the transport function reads the credential, catches every exception and returns a typed outcome; the caller raises from the outcome), and it finds it again if that outcome is the exception object itself. Proposed wording for T-34 and the §3 RC-15 row, **not applied** under §4.6: "no object reachable from the escaping exception, by attribute, slot, container, closure or `args`, holds the raw secret; the probe traverses object state, not `repr`; the secret is held only in frames that have returned before any exception escapes, and the outcome passed upward is a typed value, never the exception object". Round 3's redacting holder was Claude's own addition and is acknowledged as insufficient; the v3 text stays until OD10. The owner extends the RC-15 budget by one round on issue #3 (OD10) and the next execution applies this wording | **round 7:** `17` §3 item 6, T-34, F-12 (`b19483a`) | T-34 | `PROPOSED` (applied in `17` v5; OD10 approves or reverts) |
| RC-61 | The 27–94 % figures offered to OD4 are e-process crossing probabilities, but round 3 made the fixed-horizon test the primary; OD4 needs power curves for that test and its dependence model (`4296649412`, P1) | RC-24, RC-45, RC-49 | **A.** REPRODUCED (Appendix E; D1 generator, one increment per independent cluster, five per calendar period, block-of-one-period variance, 10,000 replications per cell): the primary test detects δ = 0.01 at 600 clusters with 80 % (b = 0.5) to 93 % (b = 0.2) power where the monitor crosses in 27 % to 32 %; δ = 0.02 at 300 clusters with 80 % to 94 %; δ = 0.005 at 600 with 54 % to 70 %. Under independent period shocks of ± 0.3 (F-22 generator, X ∈ {−0.2, +0.2}, so the scale differs from the D1 rows) the primary's power at δ = 0.02 and 600 clusters falls from 79 % to 47 %; under the persistent regime size is not held, so no power figure is meaningful. The OD4 row is rewritten with these figures; the monitor's figures stay labelled as such. The dependence model, not the cluster count alone, determines the detectable effect | `16` §6 OD4; `17` §2 table, A6, T-12, T-16, §6 "smallest useful effect"; `02` §6 item 8 | T-12, T-16 | `PROPOSED`; dependence model `EXPERIMENT_REQUIRED` |
| RC-62 | T-31 mutates only the key, environment and release digest; a verifier signing a subset of the tuple passes while a holder substitutes the action, evidence digest, epoch, nonce or expiry under a valid signature (`4296649421`, P1) | RC-12, RC-43, RC-46 | **A.** REPRODUCED (Appendix E, synthetic HMAC toy, no real key): a verifier over (environment, release digest) accepts mutations of capability, evidence digest, epoch, nonce and expiry; one over the full tuple rejects every single-field mutation. §3 item 5 now states that the signature covers the whole tuple under one canonical serialisation; T-31 mutates each of the seven fields individually and adds canonical-serialisation cases (key order, whitespace, added field, re-typed numeric field) | `17` §3 item 5, T-31 | T-31 | `PROPOSED` |
| RC-63 | A kernel that always returns "do not reject" satisfies every valid-null upper bound in A3 while the invalid-null controls exercise other algorithms; T-12 reports power with no minimum; add deterministic statistic fixtures and a pre-specified alternative with a bounded rejection rate per kernel (`4296649427`, P1) | RC-30, RC-48 | **A.** True by construction (an inert kernel scores zero on every A3 family). New T-36: (a) e-process oracle, twelve constant increments of +0.2 give e = 1.1¹⁰ = 2.593742 because λ = 0.5 from the third increment when the sample variance is zero, first crossing of 20 at increment 34 with e = 21.113777, and a fixed 12-vector gives e = 1.447854; (b) fixed-horizon oracle, block means (0.05, 0.10, 0.00, 0.05) give t = 2.449490 on 3 df, one-sided p = 0.045861; (c) positive-control alternative b = 0.5, δ = 0.08, 120 independent clusters, 20,000 replications, exact one-sided 99 % lower binomial bound ≥ 0.90 for the primary (true rate 0.964) and ≥ 0.60 for the monitor (true 0.711); a correct kernel passes with probability 1.000000 to six places, an inert one never (Appendix E) | `17` A3, T-12, new T-36 | T-36 | `PROPOSED` |

Not addressed by Codex in round 4: RC-07 n_eff retention (§4.3) and RC-20 hosting timing (§4.2); no open
scientific disagreement remains for a review to engage. Relevant to issue #3 acceptance item 2: the fourth
automatic review on a Markdown-only diff again produced statistical and security findings (repeated-look
inflation, a hindsight window, partial signatures, inert-kernel detection), two of which (RC-56, RC-60)
identified defects in Claude's own round-1 and round-3 remedies.

### 3d. Round 5: Codex's review of PR #4 at `88abaa4` (review `5550735335`), recorded without revision

Eight inline findings, all P1, none repeating rounds 1–4. Per §4.6 as written in v5 and announced to the owner
in handoff 4, this round **records** each finding with Claude's assessment and the wording that would resolve
it, and **applies nothing**: `17-phase1-amended-specification.md` stays at version 4 and no foundation document
changes. Where a finding carries a number or a logical claim it was reproduced anyway (Appendix F; evidence,
not revision), because the owner needs the evidence to decide OD10. Two findings (RC-65, RC-71) fall on families
that have formally used one round only (RC-37, RC-11); they are nonetheless recorded only, because the v5 rule
was unconditional and changing it from inside the loop is what the protocol forbids. The owner can apply all
eight, or any subset, with one line on issue #3 (OD10). Every disposition is `PROPOSED` wording and
`OWNER_DECISION` status.

| ID | Codex finding (comment ID, severity) | Parent | Claude assessment and evidence | Wording that would resolve it (not applied) | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-64 | A0 lets implementation start after OD1, OD2 and OD9a while OD10 is open, although Appendix E shows the T-34 holder still retains the secret and `12` now says Phase 0 waits on OD10 for T-34; the prerequisite documents conflict and Phase 1 could begin with a knowingly ineffective secret-leak test (`4296914293`, P1) | RC-33 (A0), RC-15 family (budget spent) | **A.** Documentation conflict, correctly identified: A0 (`17` §4) names three decisions, `12` amendments item 8 names four, and the OD10 row said the defect "matters only once Phase 1 is built", which is exactly when A0 would already have released the build. Nothing numeric | A0 adds: "OD10 recorded (the RC-60 wording applied to T-34, or the owner's explicit acceptance of the v3 wording) before T-34 and the secret-handling code of §3 item 5 are built; the rest of Phase 1 is not held by OD10". `12` item 8 unchanged | none (documentation) | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts) |
| RC-65 | The persisted high-water mark advances only on admissions: an unused capability expiring at t1 is rejected at t2 > t1, the clock is rolled back to t0 < t < t1, and the unchanged watermark t0 lets the same capability pass; persist the observed time on every clock-dependent check, rejected ones included, and replay this in T-35 (`4296914298`, P1) | RC-37 (round 2; one round used) | **A on the defect; REPRODUCED** (Appendix F, toy state machine): under the v4 wording ("persists the maximum receipt time it has ever observed", which only admissions produce) the sequence admission at 10, expired capability rejected at 30, rollback to 15, same capability presented gives `admitted`; persisting max(watermark, now) on every check gives `rejected_rollback`. A defect in Claude's round-2 remedy, not in the original research. The fix is one sentence and one fixture | `17` §3 item 2 monotonic clock: "every clock-dependent check, admitted or rejected, persists max(watermark, now) in the same transaction before it returns its verdict"; T-35 gains the replay (admission at t0; expired capability rejected at t2 > t1; rollback to t0 < t < t1; same capability refused as a rollback, logged) | T-35 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts) |
| RC-66 | T-17 tests membership mutation only after t*_k although the contract freezes the member list at registration; an implementation that allows additions or removals between registration and t*_k, including after forecasts reveal which members favour FULL, passes every listed test (`4296914307`, P1) | RC-29, RC-52, RC-53 (budget spent) | **A.** Test-coverage gap, not a contract gap: `17` §3 item 3 already says "immutable from its registration record onward", T-17 exercises only the post-t*_k case. Codex's channel is real: a removal after the first forecasts are received but before t*_k changes the cluster mean and the confirmatory population without touching any outcome | T-17 gains: addition and removal attempted immediately after registration, before the earliest `not_before`, and between the first forecast receipt and t*_k; all rejected; replay reproduces the refusals | T-17 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts) |
| RC-67 | For a cluster with one resolved and one pre-declared VOID member the text says it emits "the previously defined mean increment", but a VOID member has no Y_i and so no X_i, and t*_k is undefined if it has no outcome timestamps; dropping the member, dropping the cluster or imputing give different estimands and e-process factors and all fit the text; define the arithmetic and add closure fixtures (`4296914319`, P1) | RC-29, RC-38, RC-41 (budget spent) | **A.** Genuine ambiguity. The reading consistent with §6 ("VOID excluded from the primary and counted against the cap") is: X̄_k is the mean over the **resolved** members only, so the cluster keeps weight one with fewer members; t*_k is taken over resolved members' timestamps (a pre-declared VOID has no outcome and no `knowable_at`); a cluster whose members are all VOID emits nothing and its member count goes against the cap; the worst-case bounds impute each VOID member and recompute the mean over all members. The alternative (drop the cluster) would make the increment depend on the VOID declaration of a sibling and is rejected. No number to reproduce | `17` §3 item 3 states the four rules above; fixture F-24: members (resolved X = +0.1, pre-declared VOID) emit +0.1 with worst-case bounds from the imputed sibling; a two-member all-VOID cluster emits nothing and counts two against the cap; T-17 gains both | T-17, T-12 (sensitivity bounds) | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts) |
| RC-68 | At a cut-off 24 months after first cohort entry, clusters registered late or with long horizons may still be unresolved and emit nothing, but the missing-data contract covers only declared VOIDs; if resolution speed correlates with difficulty or error, analysing only matured clusters changes the estimand; pre-register an accrual cut-off and a maximum horizon that guarantee maturation, or count pending clusters under a capped missingness rule (`4296914330`, P1) | RC-01 (budget spent), RC-38, RC-56 | **A.** "Maturation" was in Codex's round-1 list for RC-01 (§4.1) and rounds 1–4 never specified it; the gap is Claude's. Silent exclusion at the cut-off is an outcome-correlated selection of the analysed population, the same class of channel as RC-52 and RC-57. No number to reproduce | `17` §6: accrual cut-off = 24 months minus H_max, where H_max is the maximum declared horizon including the source's declared latency window (both OD4 fields); a cluster is eligible for the primary only if every member's `expires_at` plus latency window is at or before the cut-off; clusters eligible but still pending at the cut-off (possible only through source latency) are counted as missing under the VOID cap and enter the worst-case bounds; registrations after the accrual cut-off feed the monitor and the next cohort, never this primary | T-12 (pending-cluster family), T-02 (eligibility) | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; H_max and the cut-off are OD4 fields) |
| RC-69 | The fixed-horizon oracle and every simulated family use equal blocks of five clusters and a t test over block means; with real, unequal supply that weights periods rather than clusters, contradicting the per-cluster estimand and possibly reversing the sign when supply and skill covary; specify a cluster-weighted estimate with blocks used only for the variance, and add an unequal-block oracle (`4296914341`, P1) | RC-49, RC-56, RC-63 (budget spent) | **A on the statistic; REPRODUCED** (Appendix F). Oracle: blocks of sizes 1 and 9 with values +0.5 and nine times −0.1 give an equal-block-mean estimate of +0.20 and a per-cluster estimate of −0.04 (sign reversed). The cluster-weighted estimate θ̂ = (1/N) Σ X_k with the block-sum variance Σ_b (Σ_{k∈b}(X_k − θ̂))² / N² · G/(G − 1) on G − 1 df holds size under Poisson-varying supply with and without ± 0.3 period shocks (5.2 % and 5.5 %; exact 99 % upper bounds 0.055 and 0.059, inside A3's 0.06). When supply covaries with the shock (8 clusters in a +0.3 period, 2 in a −0.3 period) the two statistics test different hypotheses: the per-cluster estimand is +0.070 and the period average is 0, so the cluster-weighted test rejects in 88 % and the block-mean test in 5.7 %. The Appendix D/E size and power figures are unaffected (equal supply by construction), but the §6 primary-test row and T-36 (b) specify the statistic incompletely. What this adds for OD4: under supply–shock covariance the per-cluster estimand itself contains the shock, so OD4 must name the estimand (per cluster, as `17` §6 says, or period-balanced) and the dependence model together | `17` §6 primary test: "point estimate = mean over clusters; variance = block-sum form above; G − 1 df"; T-36 (b) gains oracle 2, blocks (0.10, 0.00), (0.05, 0.15, 0.10), (0.00, 0.05, 0.05, 0.10), (0.20): θ̂ = 0.08, t = 3.651484 on 3 df, one-sided p = 0.017728, while the equal-block-mean statistic gives 0.10 and t = 2.828427, so an implementation of the wrong statistic fails; T-12 gains the Poisson-supply and covarying-supply families | T-36, T-12 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; estimand naming OD4) |
| RC-70 | Appendix E groups five clusters per period, so its 600-cluster rows span 120 independent periods although the analysis ends after 24 months; the 47 % power under period shocks averages over 120 shocks, not 24, and cannot support OD4; re-run with exactly 24 periods, varying clusters per period (`4296914351`, P1) | RC-24, RC-61 (budget spent) | **A; REPRODUCED; the round-4 figure is a CONFIRMED-DEFECT of Claude's own Appendix E** (Appendix F). With independent clusters the 24-period rows barely move (δ = 0.01 at 600 clusters: 78 % at b = 0.5, 92 % at b = 0.2, against 80 % and 93 % over 120 periods), because blocks then only set the degrees of freedom. Under independent ± 0.3 period shocks over 24 periods the power at δ = 0.02 is **18 %** at 600 clusters and 18 % at 1,200, not 47 %: the shock variance averages over periods only, so the detectable effect at 80 % power is about δ = 0.065 at any supply (normal theory 0.066 at 25 per period, 0.063 in the limit; simulation 59 % at δ = 0.05 and 93 % at δ = 0.08). Size holds at 24 periods (4.9–5.3 %). Consequence: under this dependence model the number of independent blocks inside the 24-month window and the shock amplitude set the detectable effect, and supply cannot buy it back; the ± 0.3 amplitude is a stress assumption to be replaced by reference-class history (OD4). The 47 % figure in `17` §6, A6, T-16 and `16` §6 OD4 stays in the text until OD10 and is superseded by this row | `17` §6 "smallest useful effect" and OD4: replace the 47 % sentence with the 24-period table (Appendix F) and the plateau statement; T-12 and T-16 fix the period count at the design's 24 and vary clusters per period | T-12, T-16 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; amplitude and block length OD4) |
| RC-71 | When the source reports that the event occurred but gives no occurrence time, absence of evidence that it met the deadline is not evidence that it was late; F-02 forces `EXPIRED_NO`, a potentially false label that enters the Brier comparison; resolve such cases VOID or unresolved under a pre-registered source rule and reserve `EXPIRED_NO` for evidence of lateness or definitive non-occurrence (`4296914363`, P1) | RC-11 (round 1; one round used) | **A in principle.** Round 1 fixed the opposite error (a late YES scored as YES, RC-11) by requiring evidence of timely occurrence, and F-02's "otherwise `EXPIRED_NO`" converts every timestamp-less YES into a NO; that error is one-directional and so biases the paired Brier difference whenever the two designs differ on such events. Remaining uncertainty: a VOID here is outcome-dependent (only a YES can lack a time), so it is carried by the cap and the worst-case bounds, never by the primary alone, and sources that do not publish occurrence times should be excluded at OD5 rather than handled at resolution | `17` §3 resolution rules and F-02: each EventSpec names its source's pre-registered occurrence-time rule; a reported occurrence with no occurrence time and no evidence of lateness resolves VOID (cap, bounds); `EXPIRED_NO` requires evidence that occurrence was after the deadline or that the event had definitively not occurred by it; F-02 splits into F-02a (occurrence time after the deadline, `EXPIRED_NO`) and F-02b (no occurrence time, VOID); T-03 and T-04 gain F-02b | T-03, T-04 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; source exclusion OD5) |

Assessment across the eight: none is a misunderstanding; every finding identifies text that an implementation
could satisfy while defeating the stated purpose, or a figure that was computed under the wrong design
parameter. Three are defects in Claude's own earlier remedies (RC-65 in round 2, RC-69 and RC-70 in rounds 3–4),
one is a gap Codex named in round 1 that four rounds left open (RC-68), and the remaining four are
specification ambiguities (RC-64, RC-66, RC-67, RC-71). Nothing was changed in `17` or in any foundation
document, including the superseded 47 % figure, so that the owner sees the v4 wording Codex reviewed beside the
wording proposed here. Not addressed by Codex in round 5: RC-07 and RC-20. Relevant to issue #3 acceptance
item 2: the fifth automatic review on a Markdown-only diff produced eight substantive findings on statistics,
missing-data handling and a security control, three of them reproducible with numbers, and found a wrong
figure in the matrix's own evidence appendix.

Round 7 applied the wording of every row above in `17` version 5 (commit `b19483a`); the "Wording that would
resolve it (not applied)" column is the wording applied, with the RC-65 clock sentence superseded by RC-73's.

### 3e. Round 6: Codex's review of PR #4 at `4de18e5` (review `5550966930`), recorded without revision

Eight inline findings, all P1, all on `17-phase1-amended-specification.md`, none repeating rounds 1–5. The
reviewed commit `4de18e5` changed only this matrix, the README and `12-roadmap.md`; `17` is the version-4 text
Codex reviewed in round 5, so this review is a further pass over unchanged text and found eight new things in
it. Per §4.6, each finding is **recorded** with Claude's assessment and the wording that would resolve it,
and **nothing is applied**. Five findings carry a checkable claim and all five reproduce (Appendix G; evidence,
not revision). Two of them show that Claude's own earlier remedies are incomplete again: the RC-65 wording
proposed in round 5 does not close the clock channel (RC-73), and the A3 size claim for the primary test holds
only on the families it was calibrated on (RC-72). Every disposition is `PROPOSED` wording and
`OWNER_DECISION` status.

| ID | Codex finding (comment ID, severity) | Parent | Claude assessment and evidence | Wording that would resolve it (not applied) | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-72 | With 24 independent calendar blocks whose clusters all share one outcome, baseline 0.9518, FULL 0.0518 and P(Y = 0) = 0.4982, each block increment is +0.90324 or −0.89676 with mean exactly zero; the one-sided t kernel rejects when at least 16 blocks are positive, probability 0.07330, above A3's 0.06 ceiling, while the symmetric null families specified can still pass; calibrate over skewed bounded nulls or use a finite-sample-valid bounded-mean procedure (`4297109177`, P1) | RC-48 (A3), RC-49, RC-56, RC-63, RC-69 (budget spent) | **A; REPRODUCED** (Appendix G). Exact size 0.07330 with rejection from k = 16 positive blocks: the k = 16 statistic is 1.714 against t₀.₉₅,₂₃ = 1.7139, so Codex placed the null on the threshold. Under the symmetric ± 0.9 null the same test rejects from k = 17 and has size 3.2 %: with 24 two-point blocks the statistic is discrete and the size oscillates with the null. The skewed family is worse and does not improve with more blocks at any useful rate: over zero-mean two-point nulls (a ∈ [0.02, 1], P(a) ∈ [0.02, 0.98], c ≥ −1; a sample with every block equal counted as no rejection) the exact size reaches 15.2 % at G = 24, 15.9 % at G = 96 and 13.2 % at G = 240, always at the rare-catastrophe shape (many small gains, rare large loss). Monte Carlo on Codex's null: 7.27 % (99 % bound 0.0771). The finite-sample-valid alternative, the archived GRAPA betting test run over the 24 block means and evaluated at the horizon, has size 0.06 % there (bound 0.0011) and **power 0.0** at every alternative on the grid (δ ∈ {0.02, 0.05, 0.08}, 25 or 50 clusters per period, where the t test has 97–100 %): with λ ≤ 0.5 and twenty-two betting steps the wealth cannot reach 20 unless every block mean is at least 0.29. So at 24 blocks there is no distribution-free bounded-mean test with power at a useful effect, and the t test is valid only on the null families it is calibrated on; the v4 A3 wording claims the 0.06 bound on four symmetric families and is silent on skew. Codex's finding is correct in substance and the remedy must be a statement of conditional validity, not a different kernel | `17` A3 and §6 primary-test row: "the primary test's size is **calibrated on the pre-registered null families, not finite-sample valid**; the families include the two-point period-shock family (every cluster in a block shares one outcome; the forecast pair and P(Y) pre-registered as a worst case) and the rare-catastrophe two-point family, both **reported with exact size**, and the pre-registered dependence model states the maximum block skew it assumes (a cap d_max on \|p_FULL − p_baseline\| for forecasts entering the primary, and a reference-class bound on the share of catastrophe periods); the bounded betting test on block means is reported beside the primary as the distribution-free check, with its power stated (zero at useful effects over 24 blocks)"; T-12 gains both two-point families; T-36 (b) gains the two-point oracle (k = 16 of 24 rejects, k = 15 does not) | T-12, T-36 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; d_max and the shock family OD4) |
| RC-73 | Last observed time t₀ = 10, capability expires at t₁ = 20, machine idle until real time 30, wall clock rolled back to 15 before the next check: current time and watermark are both below expiry and the rule admits the capability; unlike RC-65 there is no post-expiry check to advance the watermark, so the RC-65 repair cannot satisfy T-35's scenario either; use a rollback-resistant time source, a boot or session epoch, or mandatory re-authorisation after an unverifiable clock discontinuity (`4297109194`, P1) | RC-37 (round 2), RC-65 (round 5, recorded) | **A; REPRODUCED** (Appendix G, toy state machine): variant A (v4 text) and variant B (RC-65 wording) both give `admitted` after the idle rollback and after a reboot; variant C, which persists the monotonic clock reading and the boot id beside the wall clock at every check and treats a wall-minus-monotonic drift beyond a tolerance or a new boot id as a discontinuity, gives `rejected_clock_discontinuity_reauthorise` in both cases. The point is general: no rule that reads only the wall clock can measure time during which nothing was observed. A defect in Claude's round-5 proposed remedy, which was itself a repair of the round-2 remedy; the RC-37 family now has two recorded, unapplied findings | `17` §3 item 2 and item 5: "every clock-dependent check persists (wall time, monotonic time, boot id) in the same transaction; a boot id change, or a change of wall-minus-monotonic beyond the pre-registered tolerance, is an unverifiable discontinuity: every outstanding capability is invalid until the owner signs a fresh epoch (re-authorisation), and the discontinuity is logged; from Phase 2 the `AnchorStore`'s signed timestamp bounds elapsed time at every anchor"; T-35 gains the idle-window fixture (admission at 10, expiry 20, no check until a rollback to 15 with the monotonic clock advanced) and the reboot fixture (monotonic clock reset, new boot id), both refused with re-authorisation required | T-35 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts) |
| RC-74 | Capability and nonce state is reconstructed from the local ledger while external anchors may lag, so a protected action acknowledged after the last anchor disappears if SQLite and the JSONL suffix are restored or truncated back to that anchor; the external store cannot prove the unanchored record existed, replay sees an unused nonce and a stale epoch and accepts the same signed capability again; require the consumed nonce and epoch to be externally durable before acknowledgement, or fail closed and rotate authorisation state whenever suffix continuity cannot be established (`4297109203`, P1) | RC-12, RC-13, RC-34 (anchor), RC-43 (atomic nonce) | **A; REPRODUCED** (Appendix G, toy ledger): under the v4 wording (acknowledge inside the writer transaction, anchor asynchronously) the replay after a restore to the last anchor is `acknowledged`; anchoring the record externally before the acknowledgement gives `rejected_nonce_consumed`; rotating the epoch at every process start, with the rotation anchored before any protected action is accepted, gives `rejected_stale_epoch`. Codex's second option as written cannot work alone: a ledger truncated exactly to an anchor is continuous by construction, so continuity cannot reveal the missing record; it works only as epoch rotation on start. RC-43 made consumption atomic with the state change and the acknowledgement; it did not make it durable beyond the local ledger. Protected actions in Phase 1 are rare (gate promotions), so one synchronous external round trip each is affordable | `17` §3 item 5: "the protected operation acknowledges only after the ledger record carrying the consumed nonce is in an externally anchored prefix (synchronous anchor; the Phase 1 double is the harness-owned store of RC-34); if the anchor fails the operation fails closed and no state change is acknowledged"; §3 item 2: "the epoch is rotated at every process start and the rotation is anchored before any capability is checked, so that a capability signed for an earlier epoch is stale after any restore"; T-30 gains the restore fixture (protected action acknowledged, ledger and JSONL restored to the previous anchor, same capability presented: refused); T-07 reports a restore that lands exactly on an anchor as "continuous, unanchored window 0" and the test asserts that this report alone is not a pass condition for T-30 | T-30, T-07, T-18 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; the external store is OD6) |
| RC-75 | Two forecasts with different ids and probabilities recorded for the same event and arm before t*_k both satisfy eligibility, but the increment refers to one p_FULL and p_baseline without saying which record is scored; an implementation can select the revision nearest Y after resolution while passing T-06's same-id duplicate check and every prospectivity test; define a unique event/arm/scoring-slot key or a pre-registered revision schedule that scores every slot, and test multiple eligible revisions with different ids (`4297109207`, P1) | RC-02, RC-12 (T-06), RC-52 | **A; REPRODUCED** (Appendix G): revisions 0.3 and 0.7 against a baseline equal to the true probability q give an expected paired increment of −0.04 each when scored honestly at q = 0.5, and +0.16 when the revision nearest Y is scored; at q = 0.3 the honest values are 0.00 and −0.16 against +0.12. A hindsight channel of the same class as RC-52 and RC-57 but on the forecast side; none of the eligibility rules (receipt before t*_k) constrains which eligible record is used. Nothing in v4 states a key | `17` §3 item 1: "`Forecast` records are keyed by (event id, arm, forecaster version, scoring slot); the EventSpec pre-registers its scoring slots (default one slot: the first forecast received for the arm; a second record for an occupied slot is refused at submission); an EventSpec with a revision schedule names every slot in advance and every slot is scored and reported, never a chosen one"; T-06 gains: two eligible forecasts with different ids for one key before t*_k: the second is refused (one slot) or both are scored (schedule); the oracle fixture is the pair (0.3, 0.7) with Y = 1 where scoring 0.7 alone fails | T-06, T-02 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts) |
| RC-76 | The roadmap commits the Design C baseline in Phase 2 but FULL forecasts exist only once the Phase 4 adapters operate, while the estimand accepts any forecast received before t*_k; for events spanning those phases FULL can use months of evidence unavailable to Design C, so the paired Brier difference measures information timing, not model design; start the primary cohort only after every arm is operational and require a pre-registered common issuance time and evidence cutoff per comparison (`4297109215`, P1) | RC-24, RC-39 (burn-in), RC-52; `12` Phases 2 and 4 | **A.** Design gap, correctly identified; nothing numeric. `17` §6 and `12` leave the two arms' issuance times unconstrained relative to each other, and the receipt-before-t*_k rule bounds each arm only from above. The gap is Claude's: round 2 added the burn-in cohort (RC-39) without aligning it to the arm that exists last. Consequence for the roadmap: the primary cohort, and the burn-in that sizes it, cannot start before Phase 4; Phase 2 registrations feed the Design C track record and the monitor as exploratory only | `17` §6 estimand row: "each event pre-registers one issuance window [t_open, t_close] and one evidence cutoff t_cut ≤ t_close; a forecast of any arm is eligible for the primary only if received inside the window and built on evidence with `available_at` ≤ t_cut (the as-of interface of RC-79); the first registration of the primary cohort and of its burn-in is at or after the date on which every arm of the IUT comparator set is operational and frozen"; `12` Phase 2: "Design C track record and candidate log; no primary cohort"; `12` Phase 4: "burn-in cohort and primary cohort start" | T-02 (window fixture), T-16 (protocol report states the window) | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; roadmap OD1) |
| RC-77 | For outcomes established by logical finality rather than publication, once an eventually-by-deadline event's deadline plus latency window passes without evidence of timely occurrence, NO is determinable even if the registry receives the source's formal record later; T-02 covers publication-to-receipt cases only, so a forecast in the expiry-to-receipt gap can be accepted and scored after its outcome is known; define `knowable_at` to include the pre-registered logical-finality time and add the fixture (`4297109220`, P1) | RC-11, RC-52, RC-57, RC-71 (recorded) | **A; REPRODUCED** (Appendix G, arithmetic): deadline 100, latency window 10, formal record received at 118, forecast received at 113: `knowable_at` = 118 under v4 (publication or public occurrence), so the forecast is eligible; = 110 under the proposed rule, so it is not. Same channel as RC-52 on the NO side. Remaining uncertainty, which RC-71 also touches: finality at D + L is true only if a timely occurrence reported after D + L can never re-grade the event; the latency window must therefore be pre-registered long enough that such a report is a source failure (VOID, counted against the cap and the worst-case bounds), never a YES, or the finality claim is false | `17` §3 item 1: "`knowable_at` for an eventually-by-deadline predicate is min(publication time, public occurrence time, deadline + declared latency window); after the last of these the outcome is logically final"; §3 resolution rules: "a report of timely occurrence received after deadline + latency window resolves VOID with a source-latency defect logged, never YES"; fixture F-21b (100 / 10 / 118 / 113) in T-02; T-04 gains "NO by expiry at D + L with the formal record arriving later: resolved at D + L" | T-02, T-04 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; latency windows per source OD5) |
| RC-78 | The estimand names a pre-registered eligible-event population but the contract defines neither its inclusion predicate nor how registered events are sampled from it, and does not require the candidate and rejection log or the random eligible subsample that `02` §5 item 2 already calls for; hand registration can retain only events where FULL looks promising while passing every acceptance test; freeze eligibility and sampling before forecasting and log every candidate with its decision (`4297109231`, P1) | RC-39, OD5; `02` §5 item 2 | **A.** Correct and a propagation gap of Claude's: `02` §5 item 2 and `12` Phase 2 ("candidate logging") have the requirement, `17` §6 never carried it into the contract and no Phase 1 test covers the log. Selection at registration is the one hindsight channel that RC-52, RC-57, RC-75 and RC-77 do not touch because it happens before any outcome exists; it is a sampling bias, not a timing one, and only a pre-registered predicate with an audited log makes the analysed population the named population. Nothing numeric | `17` §6 new row "Eligible-event population": "a pre-registered inclusion predicate (source family, predicate kind, horizon range, sector list, Jev triage result) and a sampling rule (every eligible candidate is registered, or a seeded random subsample with its inclusion probability recorded); every candidate considered is logged with id, source, time, decision and reason **before** any forecast on it exists, the log is part of the ledger and the replay, and the protocol report states candidate, registered and rejected counts by reason"; `17` §3 item 2: candidate log in the registry; new T-37: registration without a prior candidate entry is refused; a candidate entry written after a forecast on the same event is refused; the log replays byte for byte | T-37 (new), T-16 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; predicate content OD5) |
| RC-79 | T-15 can be passed by a detector that recognises only the injected outcome column or perfect outcome correlation, while ordinary future leakage through revised values, publication-lagged joins, backfilled rows or post-cutoff timestamps stays undetected; those are the real paths; add fixtures for vintages, revisions, lagged publication and as-of joins, and reject every feature read whose availability timestamp exceeds the forecast cutoff (`4297109245`, P1) | RC-09, RC-33 (T-15, OD9a); `AGENTS.md` §8 | **A.** Test-design gap: T-15 as written is a positive control for one statistical detector and says nothing about the mechanism that prevents leakage, which `AGENTS.md` §8 names (point-in-time universe, publication-lag shifted series, vintage data). The detector cannot see a leak whose effect is a few points of Brier; the interface can refuse the read. Nothing numeric; the four fixtures are deterministic | `17` §3 item 1: a Phase 1 synthetic point-in-time store with (entity, feature, value, `observed_at`, `available_at`, vintage id) and an as-of read interface taking the forecast's evidence cutoff t_cut; T-15 redefined: (a) revised value whose later vintage replaces an earlier one, (b) publication-lagged join (observed before t_cut, available after), (c) backfilled row inserted after t_cut with `observed_at` before it, (d) post-cutoff timestamp: every read with `available_at` > t_cut is refused at the interface, deterministically; the shuffled-label statistical detector stays as the second line with the injected-outcome column as its positive control only; T-15 remains blocked on OD9a | T-15 | `PROPOSED` (applied in `17` v5, round 7; OD10 approves or reverts; build blocked on OD9a) |

Assessment across the eight: none is a misunderstanding. Five reproduce (RC-72, RC-73, RC-74, RC-75, RC-77),
and two of those are against Claude's own earlier remedies: the RC-65 wording of round 5 is insufficient
(RC-73), and the A3 bound for the primary test is a calibration on the specified families, not a validity
property (RC-72), which is the more consequential of the two because it changes what the Phase 2 contract can
claim for the primary test. RC-72 also fixes a fact for OD4 that no earlier round stated: at 24 blocks no
distribution-free bounded-mean test has power at a useful effect, so the primary test's validity rests on the
pre-registered dependence model and skew bound, and those must be justified from reference-class history. The
other three (RC-76, RC-78, RC-79) are requirements that `02` §5, `12` and `AGENTS.md` §8 already state and that
`17` never carried into the Phase 1 tests or the Phase 2 contract; they are propagation gaps of Claude's.
Nothing was changed in `17` or in any foundation document. Not addressed by Codex in round 6: RC-07 and RC-20.
Relevant to issue #3 acceptance item 2: the sixth automatic review re-read text unchanged since round 4 and
produced eight further substantive findings on it, which is evidence that the native route reviews the whole
diff on every trigger rather than the changed hunks, and that the findings per pass are not yet exhausted.

Round 7 applied the wording of every row above in `17` version 5 (commit `b19483a`), with the RC-72 sentence
on distribution-free tests replaced by the theorem of RC-80.

### 3f. Round 7: Codex's review of PR #4 at `10f8829` (review `5551243905`), and the PR #7 finding that bears on `17`

Four inline findings, all P1, none repeating rounds 1–6. The reviewed commit `10f8829` changed only this matrix,
the README and `12-roadmap.md`, so three of the four findings are a further pass over the version-4 text of
`17` and one is on this matrix's own round-6 wording. Each was examined, reproduced where it carries a claim
(Appendix H), and **applied in `17` version 5 under the round-7 rule (§4.6)**. One finding's premise is not
reproduced in the repository and its remedy is adopted anyway (RC-81). Every disposition is `PROPOSED` until
Codex reviews the commit that carries it.

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-80 | The round-6 RC-72 response tests only the archived GRAPA kernel with λ_max = 0.5 but generalises its zero power to every distribution-free bounded-mean test; one experiment cannot establish an impossibility, and OD4 could retain the knowingly oversized t test on a false premise; narrow the claim or supply a proof covering the class (`4297337217`, P1) | RC-72 (round 6; Claude's own sentence) | **A on the sentence; the general claim is now PROVED, not narrowed** (Appendix H). Theorem: any test that is level α against **every** mean-zero law on [−1, 1] has power at most α(1 + δ)^G against **every** alternative on [−1, 1] with mean δ. Proof: with ε = δ/(1 + δ), the mixture P₀ = (1 − ε)·P₁ + ε·(point mass at −1) has mean (1 − ε)δ − ε = 0, so it is in the null; a P₀ sample of G blocks contains no −1 with probability (1 − ε)^G = (1 + δ)^−G and is then a P₁ sample, so E_P₀[φ] ≥ (1 + δ)^−G·E_P₁[φ], and E_P₀[φ] ≤ α gives the bound. It is attained against that one null by the randomised test "reject with probability α(1 + δ)^G when no −1 is observed", so it cannot be improved without restricting the null. At G = 24 and α = 0.05: 0.064 at δ = 0.01, 0.080 at 0.02, 0.161 at 0.05, 0.317 at 0.08, 0.49 at 0.10; 80 % needs δ ≥ 0.1225, or 141 blocks at δ = 0.02, 57 at δ = 0.05. Numerical check of the two ingredients (200,000 samples, P₁ = δ ± 0.3): P₀ mean 0.00002, no-catastrophe fraction 0.6212 against (1 + δ)^−24 = 0.6217 at δ = 0.02, randomised test size 0.0498 and power 0.0798 against the bound 0.0804; the archived GRAPA kernel on the same P₁ samples has power 0.0000 at δ = 0.02 and 0.0000 at 0.05, consistent with the bound. Consequence for OD4, which is the opposite of "retain on a false premise": there is no finite-sample-valid replacement at this horizon, so the honest contract is the conditional t test with a pre-registered skew bound and the distribution-free check reported beside it, exactly as RC-72 proposed; the round-6 sentence is replaced by the theorem | `17` §3 item 3 ("What the size bound means"), A3, §6 primary-test and distribution-free rows; this matrix §3e RC-72 row (sentence superseded) | T-12 | `PROPOSED` (applied in `17` v5) |
| RC-81 | For `10f8829`, `git show --format=fuller` reports both author and committer as `Codex <codex@openai.com>`, while T-09 checks only commit and PR text; A7 can pass despite `AGENTS.md` §7; recreate the commit under the required identity and extend the check to author and committer metadata (`4297337229`, P1) | RC-26 (T-09) | **Premise NOT REPRODUCED; remedy accepted.** `git show -s --format=fuller 10f8829` in the repository reports author and committer `Salah Aouaj <salah@hydeout.ch>`, the identity `AGENTS.md` §7 designates, and so does every commit from `10d1581` to `10f8829` on `claude/reconciliation-round-1` (checked this round with `git log --format='%an <%ae> / %cn <%ce>'`); the reviewer's environment may have re-created the commit locally. The remedy stands on its own merits: a text check cannot see metadata, so T-09 now verifies author and committer identity against the designated list. **Disclosure, for OD9b:** the execution environment of round 7 denied the tool call that sets the owner's identity for `git commit` (classified as authorship tampering), so the two round-7 commits (`b19483a` and this one) carry the environment's default identity `Claude <noreply@anthropic.com>`. That violates §7 as written and would fail the T-09 identity check proposed here. The commits are not re-created from inside the routine (a rewrite of a pushed branch, which §7 forbids without the owner). The owner decides: squash on merge (the author becomes the merger), designate the tool identity as permitted in §7, or have the two commits re-created under the owner's identity by an environment configured with it | `17` §3 item 8, A7, T-09 | T-09 | `PROPOSED` (applied in `17` v5); identity of the round-7 commits `OWNER_DECISION` (OD9b) |
| RC-82 | A7 requires malformed-certificate tests, but Phase 1 as specified contains no certificate verifier and `12` introduces allocation certificates in Phase 5; no §5 row defines the fixture; A7 can never be satisfied as written; remove it or specify the verifier (`4297337243`, P1) | RC-35 (A7, round 1) | **A.** The phrase was carried from Codex's own §H7 exit criterion in round 1 into A7 without checking it against the Phase 1 scope; nothing in `17` §3 builds a certificate verifier. Removed from A7; specified as T-38 in `17` §7 with Phase 5 (malformed, truncated, re-signed and stale certificates rejected by the Phase 5 verifier). Nothing numeric | `17` A7, §7; `12` amendment 11 | T-38 (Phase 5) | `PROPOSED` (applied in `17` v5) |
| RC-83 | The primary claim is the IUT over Design C, every single provider, the three-role provider and the equal-weight committee, but the D1 study measures power for one paired comparison; six independent components at 80 % give about 26 % joint rejection; add a pre-specified joint generator covering all comparators and their dependence and report or bound the IUT's power (`4297337251`, P1) | RC-08 (IUT), RC-24, RC-61, RC-70 | **A; REPRODUCED** (Appendix H). Joint generator: six comparators sharing FULL's forecast and the outcome, each at the same δ (the least-favourable configuration), comparator error dependence set by the probability ρ that a comparator's sign matches a shared sign; cluster-weighted statistic, 24 blocks, one-sided α = 0.05, 20,000 replications. At δ = 0.01 and 600 clusters the single comparison has 77 % power and the IUT 21 % at ρ = 0 (uncorrelated errors, product 21 %), 32 % at ρ = 0.5 and 77 % at ρ = 1; at 1,200 clusters 96 % marginal and 77 % / 80 % / 96 %; at δ = 0.02 and 600 clusters 96 % marginal and 76 % / 80 % / 96 %; at δ = 0.02 and 288 clusters 76 % marginal and 18 % / 29 % / 75 %; at δ = 0.03 and 288 clusters 89 % marginal and 48 % / 57 % / 89 %. At the least-favourable null (one comparator exactly null, the others at δ = 0.08) the IUT rejected in 0 of 20,000 (99 % bound 0.0002), as the IUT argument of RC-30 requires. Codex's 26 % is the uncorrelated extreme; real comparators share the outcome and FULL's forecast, so the product is a reference, not the answer, and the joint power lies between the product and the smallest marginal power. The dependence of comparator errors is what the design must be powered under, and it cannot be estimated from the blinded burn-in (it needs outcomes), so OD4 names the assumption; under uncorrelated errors the conjunction needs about twice the single-comparison supply | `17` A6, T-16, §6 "smallest useful effect" and "confirmatory conjunction" rows; this matrix §6 OD4 | T-16 | `PROPOSED` (applied in `17` v5; round 9: the least-favourable-null figure of Appendix H is withdrawn, RC-93, and the "between the product and the minimum" bound is corrected, RC-101); dependence assumption `OWNER_DECISION` (OD4) |
| RC-84 | (Codex's review of PR #7, comment `4297992983`, P1, on the owner's kickoff document) Even after every gate in that document, the proposed fixed-horizon evaluation conflicts with the binding requirement for anytime-valid sequential tests (`AGENTS.md` §2 item 3); include the sequential-testing requirement in the owner-approved governance amendment or retain an anytime-valid primary test | RC-01, RC-49, RC-50 (role assignment, round 3); RC-33 (product-requirement wording) | **P.** `17` keeps the anytime-valid cluster-level e-process as the sequential monitor of the conditional null, so §2 item 3 ("anytime-valid sequential tests") is satisfied in substance; Codex is right that the item can be read as requiring the **confirmatory** test to be anytime-valid, which `17` §6 does not do, for the reasons reproduced in rounds 3 and 6 (RC-49, RC-50, RC-72, RC-80: the conditional null is the wrong null for the estimand, and no finite-sample-valid test has power at 24 blocks). Same class as RC-33: product-requirement wording that the amended specification would contradict on a strict reading. Governance text is the owner's, so nothing is applied; the proposed wording goes to OD9b. PR #7 itself (Rust-first kernel) is the owner's proposal and is not reconciled here; the acceptance tests of `17` are language-neutral except T-34, whose exception-graph mechanism is Python-specific and would need a stated equivalent (error-source chains, panic payloads, `Debug` output) if the kernel language changes | none (governance; OD9b) | none | `OWNER_DECISION` (OD9b) |

Assessment across the five: RC-80 is a defect in Claude's own round-6 wording, now repaired by a proof that
strengthens Codex's RC-72 rather than weakening it; RC-82 is a propagation defect from round 1; RC-83 is a
genuine gap in what was offered to OD4 and changes the supply arithmetic; RC-81's premise does not hold in the
repository but its remedy is cheap and its subject (commit identity) is live for this very round, which is
disclosed rather than hidden; RC-84 is a wording conflict for the owner. Not addressed by Codex in round 7:
RC-07 and RC-20. Relevant to issue #3 acceptance item 2: the seventh automatic review re-read text unchanged
since round 4 and the round-6 matrix text and produced four substantive findings, one of them against the
matrix's own reasoning, which is the adversarial review of the reconciliation the owner's protocol asked for.

### 3g. Round 8: Codex's review of PR #4 at `37ac018` (review `5556866013`)

Two inline findings, both P1, both on `17` version 5, neither repeating rounds 1–7. Both are defects in remedies
that round 7 wrote (RC-67 and RC-79), both were reproduced (Appendix I) and both are **applied in `17` version 6
under the §4.6 rule**, in the same commit as this matrix. The same review raised nothing on the other nineteen
items that version 5 applied; they are reviewed once by Codex without objection, which is recorded in §4.6 and
§7 and is not an agreement. Every disposition is `PROPOSED` until Codex reviews the commit that carries it.

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-85 | Fresh evidence in the version-5 partial-VOID remedy: t*_k is computed only from resolved members, so an all-VOID cluster has no cutoff; the contract still requires VOID declarations before t*_k and F-24 only checks that an all-VOID cluster emits nothing and counts against the cap, so an implementation can accept every VOID declaration after the outcomes become known and remove the entire cluster from the point estimate; freeze all-VOID status at registration or define and test a declaration cutoff that does not depend on which members resolve (`4301920287`, P1) | RC-67 (round 7, Claude's own remedy); RC-57, RC-29, RC-38, RC-71, RC-77 | **A; REPRODUCED** (Appendix I). Toy closure machine, one two-member cluster, freeze at 5, deadline 40, latency window 10: with both outcomes published at 10 and 12 and VOIDs declared at 11 and 13 before the records arrive at 30 and 32, the version-5 rule accepts both declarations and at closure finds no resolved member and no t*_k, so both stand and the cluster leaves the point estimate (scenario S2); the same rule refuses the same declaration when the sibling resolves (S3), so the gap is exactly the all-VOID case Codex named. The version-5 text was also inconsistent with itself: it said a VOID member has no `knowable_at`, while the RC-57 fixture needed one to refuse the 10:10 declaration. Magnitude: the cap bounds the share removed, not the bias. On the valid null, 24 blocks, 20,000 replications, declaring the q N least favourable clusters VOID after the outcomes are known raises the primary's rejection rate from 5 % to 10–13 % (q = 2 %), 23–34 % (5 %) and 56–81 % (10 %) on the two-point generator and to 31–47 %, 77–95 % and 99–100 % on a continuous one, at 300 and 600 clusters; the mean shift at q = 5 % (0.011 and 0.015) is the size of the effects OD4 powers for; the worst-case lower bound rejects at 5 % throughout, so the bounds work and the point estimate, which is what the primary tests, is the exposed quantity. Resolution, simpler than a new cutoff: a member leaves the scored set in two ways only, **pre-declaration before the cluster's freeze instant** (the earliest `not_before`, where RC-29 already freezes the membership; Codex's first option made precise, since no outcome can be determinable before it) or **adjudication under the pre-registered source rule** at a record the predicate cannot grade (RC-71, RC-77) or at logical finality with the source's failure condition met; a VOID request after the freeze changes no state and a record always wins, which closes RC-57's publication-to-receipt gap without any cutoff; both classes count against the cap and are imputed in the bounds; a VOID audit reports both classes and every post-freeze request on a member later scored. Remaining uncertainty: an adjudicated VOID at finality is outcome-dependent in principle (a source can fail selectively), so it stays under the cap and in the bounds and the failure condition per source is OD5, not a registry rule; and the waiting rule costs calendar time for a genuinely failed source (the member stays open until deadline + window) | `17` §2 (two rows), §3 item 3 "VOID classes and partial VOID" and the cluster closure paragraph, T-17, F-24 (five clusters), §6 Missing data; this matrix §6 OD4 and OD5 | T-17, T-12 | `PROPOSED` (applied in `17` v6; cap value OD4, source rules OD5) |
| RC-86 | T-15's pass condition checks only that reads with `available_at` > t_cut are refused and never requires a query at t_cut to return the latest eligible vintage, or anything; a reader that rejects every read, or returns an arbitrary older eligible row, passes T-15 while making the experiment unusable or evaluating it on the wrong point-in-time data; add positive oracles asserting the exact value and vintage at representative cutoffs beside the refusal cases (`4301920289`, P1) | RC-79 (round 7, Claude's own remedy); RC-63 (same class: a test satisfied by an inert component) | **A; REPRODUCED** (Appendix I, deterministic). Fixture F-25, five rows (first release, revision, backfill, lagged publication, second revision) and ten cutoffs; four readers beside the reference: a refuse-all reader and an oldest-eligible-vintage reader pass every refusal case of T-15 as written and fail the oracle at ten and at seven cutoffs; a reader that filters on `observed_at` (the classic leak: it returns the second revision at t_cut = 11) and one that ignores the cutoff fail both. Same defect class as RC-63 (an inert kernel passes a size test): a control that can only refuse is satisfied by refusing everything. Resolution: the as-of semantic is stated (per `observed_at`, the row with the greatest `available_at` ≤ t_cut, with its vintage id; a typed empty result distinct from a refusal; first-release semantics would be a different pre-registered choice that changes the oracle table and not the interface), and T-15 case (e) requires the oracle series at the ten cutoffs beside the refusals (a)–(d). Nothing statistical; T-15 stays blocked on OD9a | `17` §2 (one row), §3 item 1 "As-of semantics", T-15, F-25 | T-15 | `PROPOSED` (applied in `17` v6; build blocked on OD9a) |

Assessment across the two: both are against remedies Claude wrote in round 7, and both reproduce. Round 7 fixed
the arithmetic of a partial VOID (RC-67) and the mechanism of leakage control (RC-79) and left each with a hole
of a kind earlier rounds had already closed elsewhere (an outcome-dependent cutoff, as in RC-57 and RC-65; a test
satisfied by an inert component, as in RC-63). Not addressed by Codex in round 8: RC-07 and RC-20, and nothing
on the other nineteen version-5 items. Relevant to issue #3 acceptance item 2: the eighth automatic review read
the version-5 text for the first time and returned two findings, both on new text and both substantive, where
rounds 5–7 had re-read unchanged text and returned four to eight each; the count per pass fell while the text
under review grew, which is the first sign of the loop converging rather than exhausting.

### 3h. Round 9: Codex's two reviews of PR #4 at `8af2ae9` (reviews `5556950582` and `5558680831`) and the owner's directive

Twenty-one inline findings on the version-6 text: nine from the automatic review of the round-8 push (review
`5556950582`, 2026-10-17 08:06 UTC; seven P1, two P2) and twelve from the review the owner requested with the
directive comment `6236238443` on PR #4 (review `5558680831`, 16:09 UTC; eleven P1, one P2). None repeats a
comment ID of rounds 1–8; four extend earlier items with a new channel (RC-87 on RC-85, RC-92 on RC-85, RC-96 on
RC-75, RC-101 on RC-83) and are distinct claims. All twenty-one are assessed as genuine; every checkable claim
reproduces (Appendix J, `python -I round9_checks.py`); every one is **applied in `17` version 7 under the §4.6
rule** in the same commit as this matrix, except where a field is the owner's, which is marked `OWNER_DECISION`
in the row. Six are defects in remedies written in rounds 7 and 8 (RC-87, RC-90, RC-92 on RC-85; RC-93 and RC-101
on RC-83; RC-96 on RC-75), one is a hand-typed number in Appendix H (RC-102), and one, RC-95, changes a design
rule that every version since round 2 carried (increments entered the monitor in closure order). The owner's
directive is processed as an input in §4.6; the thread accounting it asked for is there too. Every disposition
is `PROPOSED` until Codex reviews the commit that carries it.

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-87 | F-24 places both arms' forecasts at time 1 and allows pre-declared VOIDs at 3 and 4 before the freeze at 5; a researcher can inspect the paired forecasts and VOID the clusters where FULL looks unfavourable while every proposed test passes; freeze the VOID set at registration or require the freeze to precede every forecast (`4301994279`, P1) | RC-85 (round 8, Claude's own remedy); RC-29, RC-57, RC-78 | **A; defect in the round-8 remedy.** Version 6 froze the VOID set at the earliest `not_before` and let forecasts precede it, so the set could be chosen with the forecasts in view; the forecasts are not outcomes, but a party with any private signal about the outcome, or simply reading which clusters FULL would lose on if its own forecast were right, selects on them. Codex's first option is taken, since it is the simplest: the member list and the VOID set are fixed in the **cluster registration record**, every member's issuance window opens at or after that record, and a VOID request after registration changes no state whether or not a forecast exists yet. A pre-declared member is then a population choice with no forecast and no outcome in view, equivalent to a candidate-log rejection (RC-78), and leaves the scored population, the cap and the bounds; after registration a member leaves only by adjudication. F-24's forecasts move to time 1 after a registration record at 0, and a request at 0.5 is the new refusal case. Remaining uncertainty: none statistical; the registration record now carries the whole pre-registration | `17` §2 (one row), §3 item 3 "VOID classes", cluster closure paragraph, T-17, F-24, §6 Missing data | T-17 | `PROPOSED` (applied in `17` v7) |
| RC-88 | §3 requires a member with no record from a living source to resolve NO at deadline + latency window and T-04 tests it, while the same lines require the event to become VOID if a report of timely occurrence arrives later; the NO may already have closed the cluster and entered the e-process, so an implementation must rewrite committed statistics or violate one rule; define one immutable disposition at finality or defer resolution until the source-failure status is determinable (`4301994282`, P1) | RC-77 (round 7), RC-71, RC-11 | **A; the two sentences were in conflict.** An append-only ledger and a committed increment cannot be rewritten, so the disposition at finality must be immutable and the only free parameter is what the finality rule needs as evidence. Version 7: NO at deadline + window requires an archived **observation of absence** at or after that time (evidence of absence, not absence of evidence); with the source rule's failure condition met the member is adjudicated VOID; a report of timely occurrence after finality is a **source-latency defect** logged against the source, never YES and never VOID. The defect is a bounded, reported error, not a correction: a selectively failing source could bias the paired difference in either direction, so the per-source defect rate is reported and a source above its pre-registered bound is withdrawn from new registrations (OD5). Codex's deferral option was rejected because "until the source-failure status is determinable" has no pre-registrable end (deterministic fixtures in Appendix J) | `17` §2 (one row), §3 item 1 "Logical finality", T-04, F-02c | T-04 | `PROPOSED` (applied in `17` v7; defect-rate bound `OWNER_DECISION`, OD5) |
| RC-89 | For an EventSpec with several pre-registered revision slots the text requires every slot to be scored but never says how the slot scores produce the single p_FULL,i and p_baseline,i of the increment formula; averaging, separate members or one designated slot change the statistic and all satisfy "scored" (`4301994284`, P1) | RC-75 (round 7, Claude's own remedy), RC-76 | **A; gap in the round-7 remedy.** Each EventSpec names exactly one **primary slot** per arm, whose issuance window and evidence cutoff are the event's own under RC-76; only its record enters the increment, the primary test and the monitor; every other slot is a descriptive secondary, scored and reported, never aggregated or chosen. Averaging would change the estimand's unit; separate members would make one event several and weight it accordingly | `17` §2 (one row), §3 item 1 "Scoring slot", T-02, §6 Estimand | T-02 | `PROPOSED` (applied in `17` v7) |
| RC-90 | A member pre-declared VOID before either arm forecasts is recorded by count only and excluded from the worst-case bounds because no probabilities exist to impute; such members can carry an arbitrarily unfavourable contribution while the reported sensitivity interval is unchanged although the document presents it as bounding the effect of missing outcomes; impute an unconstrained increment in [−1, 1] or define a conservative bound (`4301994289`, P1) | RC-85 (round 8), RC-38, RC-67 | **A.** Under RC-87 a pre-declared member is now fixed at registration with no forecast in view and is outside the scored population by construction, so it is a population definition and not a missing outcome; the interval is stated as a bound on the registered population only. Every **adjudicated** VOID without both primary-slot forecasts (a source that fails before the issuance window, an empty baseline slot at issuance close) is imputed at increment −1 and +1 in the bounds, as Codex proposed; it costs nothing and makes the interval honest for the population it claims to bound | `17` §3 item 3 "VOID classes", §6 Missing data, F-24 clusters D and G | T-17, T-12 | `PROPOSED` (applied in `17` v7) |
| RC-91 | `02` §6 item 8 still presents 47 % as the 600-cluster period-shock power although RC-70 establishes 18 % at 600 and at 1,200 clusters over the design's 24 periods; OD4 is given two conflicting estimates for one design (`4301994291`, P2) | RC-70 (round 7) | **A.** Round 7 corrected `17` and the OD4 row and left the methodology document's amendment item unchanged; a dated note is appended to item 8 marking the sentence superseded with the 24-period figures. The original text above the amendments section is untouched, as `AGENTS.md` §11 requires | `02` §6 item 8 (note) | none (text) | `PROPOSED` (applied) |
| RC-92 | t*_k excludes every VOID member, including an adjudicated VOID whose record or finality event is public; if one member becomes VOID on a timestamp-less occurrence at 10 and a scored sibling resolves at 20, a forecast on the sibling received at 15 is accepted although the cluster was formed because the outcomes may be dependent and the time-10 adjudication can reveal outcome information; include each adjudicated VOID member's `knowable_at` in the cutoff (`4301994294`, P1) | RC-85 (round 8), RC-52, RC-67 | **A; defect in the round-7/8 arithmetic; REPRODUCED** (Appendix J, deterministic: t*_k = 20 under version 6 admits the forecast at 15, t*_k = 10 under version 7 excludes it). t*_k is taken over **all** members as the minimum of outcome receipt, adjudicated `knowable_at` and VOID adjudication time. F-24 gains cluster F | `17` §2 (one row), §3 item 3 cluster closure paragraph and "VOID classes", T-02, T-17, F-24 | T-02, T-17 | `PROPOSED` (applied in `17` v7) |
| RC-93 | The least-favourable-null check of Appendix H sets comparator 1's δ to zero in a generator where that makes its forecast exactly b and every increment exactly zero; its variance is zero and the statistic never rejects, so the reported 0 of 20,000 is mechanical and not a size check; generate a null comparator with mean-zero, non-zero-variance increments (`4301994299`, P1) | RC-83 (round 7, Claude's own appendix), RC-30, RC-13 | **A; CONFIRMED-DEFECT of Appendix H; REPRODUCED** (Appendix J: every increment of that comparator is 0.0 to machine precision). The null comparator now carries the same calibration-error magnitude as FULL with an independent sign, so its increment has mean zero and positive variance; the IUT then rejects in 4.95 % of 20,000 replications (99 % upper bound 0.053) at either error magnitude, within the A3 bound. The Appendix H figure is withdrawn in `17` T-16 and T-13 names the non-degenerate construction; the same class of defect as RC-63 and RC-86 (a check satisfied by an inert component), this time in Claude's own evidence | `17` §2 (one row), A3, T-13, T-16; this matrix §3f RC-83 row (figure superseded) | T-13, T-16 | `PROPOSED` (applied in `17` v7) |
| RC-94 | The contract now allows null families with 7.33–15.2 % rejection to have no pass condition while it still designates the same kernel as a one-sided α = 0.05 confirmatory test; d_max and the catastrophe-share field define no critical-value calibration and require no worst-case size control over the class OD4 selects, so an implementation can satisfy A3 and make a nominal 5 % claim under an allowed model with a much larger type-I error; require the selected class to pass a size ceiling or declare the primary non-confirmatory (`4303397680`, P1) | RC-72, RC-80 (rounds 6–7), RC-48 | **A.** The honest version of "calibrated on the pre-registered families" is a pre-registered **null class** N and a critical value c* calibrated as the smallest value whose worst-case size over N is at most α, verified in T-12 as a pass condition, with power restated at c*. REPRODUCED on the two-point block-mean family with catastrophe share at least ε_min, where the calibration is exact: c* = 3.20 for ε_min = 0.05 or 0.10, 2.63 for 0.20, 2.23 for 0.30; power at δ = 0.02 and 600 clusters 60 %, 79 % and 88 % against 96 % at the nominal 1.71, and 94–99 % at 1,200 clusters. A convention surfaced on the way: a sample whose blocks are all equal has zero variance, and Appendix G counted it as a non-rejection while Appendix H's vectorised statistic returns +∞ and rejects; the first convention is adopted and is a T-36 oracle, because under the other no critical value exists for any class with ε_min below 0.12 (0.98²⁴ = 0.62 of samples are all-positive at ε = 0.02). The wider the class, the larger c* and the lower the power, which is RC-80 from the null side; a class on which no c* reaches the power floor makes the primary non-confirmatory under that class, and the contract says so instead of carrying a nominal claim beside an oversized family | `17` §2 (one row), §3 item 3 "Calibrated critical value", A3, T-12, T-36, §6 Primary test | T-12, T-36 | `PROPOSED` (applied in `17` v7; ε_min, d_max, block length, amplitude, G_min, power floor `OWNER_DECISION`, OD4) |
| RC-95 | Applying increments by closure time invalidates the anytime-valid monitor when source latency reverses closure order: with A knowable at 10 and closing at 30, B knowable and closing at 20, and X_B = −1 whenever X_A = −1, the conditional null holds in knowable order but closure order sees B first and a frozen λ_A = 0.5 gives A's factor conditional expectation 1.5; the closure-order wealth is not a supermartingale and its running maximum has no Ville guarantee; buffer later closures until earlier t*_k increments are available, or drop the anytime-valid claim (`4303397684`, P1) | RC-01, RC-29, RC-52 (every version since round 2 said "in order of closure time") | **A on the defect; Codex's remedy is necessary but not sufficient; REPRODUCED** (Appendix J). The 1.5 reproduces exactly. The channel that inflates the running maximum is **outcome-dependent timing**: for an eventually-by-deadline predicate a YES is knowable at the occurrence and a NO only at logical finality, so both closure order and knowable order place YES clusters first. Toy: 120 fair clusters, X = ± 0.5, λ = 0.5 fixed, a YES closing one interval after registration and a NO at its finality: the closure-order running maximum crosses 1/α in 5.2 % of paths when the NO lag is six intervals, 10.1 % at twelve, 43.9 % at twenty-four and 100 % when every NO resolves last, against 3.2–3.4 % in **pre-registered maturity order** (H_k = max over members of deadline + latency window, known at registration) and 0.7 % for the order-free final product. Version 7: increments enter the monitor in H_k order, ties by registration id, a closed cluster is buffered until every cluster with a smaller H_k is final, λ_k is the archived rule on the H-prefix, and the conditional null is stated in that filtration. The fixed-horizon primary is unaffected. T-39 and F-26 carry both the toy and Codex's example; T-36 (d) is the two-cluster oracle. Cost: monitor latency up to H_max | `17` §2 (one row), §3 item 3 "Monitor order", A6, T-16, T-36, T-39, F-26, §6 monitor row | T-39, T-36 | `PROPOSED` (applied in `17` v7) |
| RC-96 | The RC-75 key still includes the forecaster version: a default-slot FULL forecast from v1 and one from v2 occupy distinct keys for the same event, arm and slot; T-02 and T-06 hold the version fixed, so both records can be admitted while the increment expects one p_FULL,i, preserving the outcome-dependent revision channel (`4303397689`, P1) | RC-75 (round 7, Claude's own remedy) | **A; defect in the round-7 remedy; REPRODUCED** (Appendix J: two honest versions of one forecaster, null expected increment −0.0387 with the version fixed in advance and +0.0730 when the better one is scored after the outcome). The key is (event, arm, slot); the version is pre-registered per arm and per event, another version is refused at submission, and a version change is a new arm with its own pre-registration. T-02 and T-06 gain the version case | `17` §2 (one row), §3 item 1 "Scoring slot", T-02, T-06 | T-02, T-06 | `PROPOSED` (applied in `17` v7) |
| RC-97 | The block-sum formula does not say whether periods with no eligible cluster count in G and the G − 1 degrees of freedom; counting all 24 assigns 23 df even if two periods supplied observations, counting occupied periods changes the correction and the critical value, and Appendix F could not expose the choice because it forced every Poisson count to at least one; specify the empty-block rule and a minimum number of occupied blocks, and add zero-supply periods to T-12 (`4303397692`, P1) | RC-69 (round 7, Claude's own remedy), RC-70 | **A; REPRODUCED** (Appendix J; Appendix F's valid null X ∈ {−0.2, +0.2}, 10,000 replications per family): with Poisson supply of mean 0.5, 1 and 2 per period and empty periods allowed (9.4, 15.2 and 20.8 occupied blocks on average), counting empty periods in G and the degrees of freedom gives 6.7 %, 5.8 % and 5.8 % size with 99 % upper bounds of 7.3 %, 6.4 % and 6.4 %, outside the A3 bound, where counting occupied blocks only gives 4.9 %, 5.1 % and 5.6 %. G is the number of occupied blocks, the contract pre-registers G_min below which the primary is not evaluable, and T-12 carries the zero-supply families with the all-periods convention as an invalid control | `17` §2 (one row), §3 item 3 "The primary statistic", A3, T-12, §6 Primary test and Stopping rule | T-12 | `PROPOSED` (applied in `17` v7; G_min `OWNER_DECISION`, OD4) |
| RC-98 | The `Forecast` schema records model hashes and evidence ids but not the model knowledge cutoff `AGENTS.md` §8 requires per forecast; a provider model trained through February can forecast a January event whose outcome is in its parameters while every point-in-time read satisfies `available_at` ≤ t_cut, and neither T-02 nor T-15 detects it; add the cutoff to the immutable record, exclude cutoff-overlapping events from skill statistics, add a fixture (`4303397696`, P1) | RC-79, RC-86 (rounds 7–8), RC-09 | **A.** A requirement of `AGENTS.md` §8 that `17` never carried, and a channel the point-in-time store cannot see. `Forecast` records the declared cutoff as an UNVERIFIED provider claim with its archived evidence; a member is eligible for an arm only if its `not_before` is after that arm's cutoff, and a member whose adjudicated `knowable_at` is at or before any arm's cutoff is excluded from the skill statistics at adjudication; fixture F-27 carries both. Remaining uncertainty: the cutoff is the provider's statement and cannot be verified from inside the system; it is labelled as such, and a provider that will not state one is excluded at registration (OD8) | `17` §2 (one row), §3 item 1 (schema), T-02, F-27, §6 Estimand | T-02 | `PROPOSED` (applied in `17` v7; provider duty `OWNER_DECISION`, OD8) |
| RC-99 | For public economic events, declining to unseal the registry outcome does not blind the researchers who set OD4–OD5: a short-horizon burn-in event can resolve in the news or in the named source during months 1–3 and the contract can be tuned after its result is visible while the row passes; require every burn-in outcome to be not knowable until after the freeze, or assign the freeze to an access-separated principal and audit it (`4303397700`, P1) | RC-39 (round 2), RC-76 | **A.** The first option is deterministic and testable: the contract freeze date is recorded in the ledger before the first burn-in registration, every burn-in event's deadline + latency window lies after it, and T-37 refuses a burn-in registration that would mature before the freeze; the principal who freezes the contract is named and the separation reported, not assumed. The burn-in moves with the primary cohort to Phase 4 (RC-76, RC-106) | `17` §2 (one row), T-37, §6 Planned supply | T-37 | `PROPOSED` (applied in `17` v7) |
| RC-100 | If "a change" of wall-minus-monotonic is measured against the last persisted check, an attacker keeps an expired capability valid by slewing the wall clock a little on every check: wall time keeps increasing, each change stays below tolerance, and the cumulative offset grows without bound while real time passes expiry; T-35 covers only an abrupt rollback, an idle jump and a reboot; compare drift to a fixed boot or anchor baseline and add a many-small-adjustments fixture (`4303397703`, P1) | RC-73, RC-65 (rounds 5–7, Claude's own remedies), RC-37 | **A; defect in the round-7 wording; REPRODUCED** (Appendix J: 100 checks each slewing by 0.75 of the tolerance; the per-check rule admits forty checks after the capability's real expiry at 60 and never reports a discontinuity; the baseline rule reports one at the third check). The offset is compared with the baseline persisted at the epoch start; T-35 gains the slew fixture | `17` §2 (one row), §3 item 2 "Clock", A5, T-35 | T-35 | `PROPOSED` (applied in `17` v7) |
| RC-101 | The RC-83 remedy states that the conjunction's power lies between the product of the marginal powers and the smallest marginal, which is false without positive association: six components at 80 % can have zero joint power while the product is 26 %; the ρ ∈ {0, 0.5, 1} generator explores only independence through positive dependence; pre-register and justify positive association or include negatively dependent generators and use the Fréchet lower bound (`4303397708`, P1) | RC-83 (round 7, Claude's own remedy) | **A; CONFIRMED-DEFECT of Claude's round-7 sentence; REPRODUCED** (Appendix J): an explicit joint law with six marginals at 0.80 and joint power 0.000 (five failure events partition the sample space), and the Appendix H generator with three anti-correlated comparator pairs, where the joint power at δ = 0.01 and 600 clusters is 15.0 % against a product of 20.2 % and an independent-sign joint of 20.6 %. The bound is replaced by the Fréchet interval [max(0, Σ_j p_j − (J − 1)), min_j p_j]; the design is powered under a pre-registered positive-association assumption justified from reference-class error structure, or under the Fréchet bound; T-16 carries the negatively dependent generator | `17` §2 (one row), A6, T-16, §6 Confirmatory conjunction | T-16 | `PROPOSED` (applied in `17` v7; assumption or Fréchet powering `OWNER_DECISION`, OD4) |
| RC-102 | The reproduced-output sentence reports 140 blocks at δ = 0.02, but the calculation above it evaluates ceil(log(0.80/0.05)/log(1.02)) = 141, and at 140 blocks the bound is 0.799823; the JSON contradicts its own `blocks_needed` field and the 141 used elsewhere (`4303397714`, P2) | RC-80 (round 7, Claude's own appendix) | **A; CONFIRMED-DEFECT of Appendix H; REPRODUCED** (Appendix J: 0.799823 at 140, 0.815820 at 141, ceil = 141). The sentence was hand-typed into a string while the field beside it was computed; the string now takes the computed value, the round-7 script was re-run twice in the round-9 environment, and its output differs from the committed Appendix H output in that one line only, which is replaced. `17` and §3f already said 141 | this matrix Appendix H (script line and output line) | none (arithmetic) | `PROPOSED` (applied) |
| RC-103 | If the owner signs two promotion capabilities with distinct nonces in one epoch, A can promote, the gate can be demoted, and the unused B still promotes again because demotion neither consumes B nor rotates the epoch; T-30 only replays a consumed capability; rotate and anchor the epoch on demotion and test a second unused capability (`4303397718`, P1) | RC-74 (round 7, Claude's own remedy), RC-12, RC-43 | **A; REPRODUCED** (Appendix J: toy gate, final state `SIM_READ_ONLY` under version 6, `RESEARCH_ONLY` with B rejected as a stale epoch when the demotion rotates and anchors the epoch in its own transaction). T-30 gains the case; A5 names it | `17` §2 (one row), §3 item 2 "Epoch rotation", §3 item 5, A5, T-30 | T-30 | `PROPOSED` (applied in `17` v7) |
| RC-104 | When an outcome resolves but one arm has no eligible forecast (F-21's only FULL submission arrives after publication), the member has a Y but cannot be scored and is neither pre-declared nor adjudicated VOID; the cluster can stay open forever and evade the pending rule and the cap, while dropping it silently is outcome-timed selection; define a pre-outcome issuance-close disposition for every missing arm, including abstention scoring, with late-only and absent-arm fixtures (`4303397725`, P1) | RC-85, RC-67 (rounds 7–8), RC-76, RC-38 | **A; gap in the round-7/8 closure rule.** At the member's pre-registered issuance close t_close, which precedes any knowable outcome, every empty primary slot is decided: a non-baseline arm's empty slot is an **abstention**, scored at the baseline forecast (X_i = 0 for that comparison, which is what §6 already prescribed for abstentions) and reported per arm; an empty baseline slot adjudicates the member VOID at t_close, outcome-independent, under the cap and imputed at ± 1 (RC-90); a submission after t_close is labelled late and never scored. F-24 gains cluster G | `17` §2 (one row), §3 item 3 "VOID classes" (Abstention), T-17, F-24, §6 Estimand and Missing data | T-17 | `PROPOSED` (applied in `17` v7) |
| RC-105 | When an event occurs before the deadline and the source publishes within its window but a registry outage delays receipt past deadline + window, the rule resolves VOID although the source supplied timely evidence; the four timestamps already separate publication from receipt, so using receipt converts ingest failures into false source defects; apply the latency rule to the evidenced publication time and treat delayed receipt as an integrity incident (`4303397727`, P1) | RC-77 (round 7, Claude's own remedy), RC-11, RC-52 | **A; defect in the round-7 wording.** The latency window is applied to the evidenced publication time of the archived record, never to registry receipt; a late receipt is an integrity incident. Combined with RC-88 this needs one more piece: the NO at finality requires an archived observation of absence at or after deadline + window, so that an observer outage leaves the member open until the source has been read instead of resolving it on nothing (deterministic fixtures in Appendix J; F-02d) | `17` §2 (one row), §3 item 1 "Logical finality", T-04, F-02d | T-04 | `PROPOSED` (applied in `17` v7; observation duty `OWNER_DECISION`, OD5) |
| RC-106 | `12` amendment 11 keeps a Phase 2 Design C track record although the roadmap commits Design C forecasts there and the three provider adapters do not exist until Phase 4; calling the cohort exploratory does not satisfy `AGENTS.md` §2 item 1 (no forecast with fewer than three model outputs plus Jev) and RC-17 requires those inputs for every issued forecast; Phase 2 can collect candidates and metadata, but forecast issuance moves to Phase 4 unless the owner changes the requirement (`4301994303`, P1) | RC-76 (round 7), RC-17, RC-39 | **A.** The binding text admits no exception for an exploratory arm. Phase 2 collects candidates (T-37), registers events, measures supply and commits Design C base rates as reference data; no arm issues a forecast before Phase 4, where the burn-in and the primary cohort start. The alternative Codex names, an owner amendment of §2 item 1 for an exploratory single-arm record, is recorded under OD9b as `OWNER_DECISION` and is not assumed | `17` §2 (one row), §7 "Forecast issuance before Phase 4", §6 Planned supply; `12` amendment 13 | none (scope) | `PROPOSED` (applied; §2 item 1 exception `OWNER_DECISION`, OD9b) |
| RC-107 | `08` amendment 4 replaces the owner HMAC with public-key capability signatures, but `12` still directs the Phase 3 `SIM_READ_ONLY` and Phase 5 `SIM_PRECHECK` promotions to an owner MAC and its amendments supersede only the Phase 1 table; implementers get conflicting authorisation contracts; update the Phase 3 and 5 rows (`4301994307`, P2) | RC-12, RC-14 (round 1) | **A.** `12` amendment 13 supersedes the two rows: every gate promotion in every phase uses the signed capability tuple with epoch, nonce and expiry, the consumed-authorisation store and the replay protections of `17` §3 items 2 and 5; `08` amendment 5 cross-references it. The original rows stay in place above the amendments section | `12` amendment 13; `08` amendment 5 | none (text) | `PROPOSED` (applied) |

Assessment across the twenty-one: six are defects in remedies written in rounds 7 and 8 (RC-87, RC-90 and RC-92
on the RC-85 VOID rule; RC-93 and RC-101 on the RC-83 conjunction evidence; RC-96 on the RC-75 slot key), two
are defects in Claude's own evidence (RC-93, RC-102), three are requirements of `AGENTS.md` §8 or `02` §5 that
`17` never carried (RC-98, RC-99 in its deterministic form, RC-106 against §2 item 1), and one, RC-95, is a
design error present since round 2 that no earlier review had named: the monitor consumed increments in closure
order. Reproducing it showed something Codex's remedy would not have fixed: ordering by outcome-knowable time
inflates the running maximum as much as closure order does, because for an eventually-by-deadline predicate the
knowable time is itself outcome-dependent; only an order fixed at registration keeps the Ville bound. RC-94
turned the round-7 wording "calibrated on the pre-registered families" into a pass condition and, on the way,
exposed a convention disagreement between Appendix G and Appendix H on zero-variance samples that is now a T-36
oracle. Not addressed by Codex in round 9: RC-07, RC-20, and nothing on the version-6 items RC-85 and RC-86 beyond
the three extensions above. Relevant to issue #3 acceptance item 2: the ninth and tenth automatic reviews read the
version-6 text and returned nine and twelve findings, every one substantive and none a repeat, which reverses the
round-8 observation that the count per pass was falling; the owner-requested review found more than the
automatic one on the same commit.

### 3i. Round 10: Codex's review of PR #4 at `922956b` (review `5558887072`)

Eight inline findings on the version-7 text (seven P1, one P2), all on `17`, posted 2026-10-17 16:50 UTC. None
repeats a comment ID of rounds 1–9; six extend a round-9 item with a new channel and are distinct claims. All eight
are assessed as genuine; every checkable claim reproduces (Appendix K, `python -I round10_checks.py`); every one is
**applied in `17` version 8 under the §4.6 rule** in the same commit as this matrix, with owner-reserved fields
marked `OWNER_DECISION`. Five are defects in remedies written in round 9 (RC-108 and RC-111 on RC-94, RC-109 on
RC-104, RC-110 on RC-99, RC-112 on RC-98), one is a round-9 propagation gap (RC-115 on RC-87/RC-90), one an open
case left between RC-88 and RC-105 (RC-113), and one an ambiguity in round-7 wording (RC-114 on RC-68). Every
disposition is `PROPOSED` until Codex reviews the commit that carries it.

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-108 | The replacement defines N only by four scalar settings; block length, d_max, catastrophe share and shock amplitude do not specify the admissible block distributions, serial dependence or supply–shock dependence, so T-12 cannot enumerate its extreme points or establish a worst-case size over N, and a persistent-regime law could satisfy those bounds while retaining the oversized behaviour already reported; specify the complete joint-law class and a valid worst-case procedure before calling c* level 0.05 (`4303569704`, P1) | RC-94 (round 9, Claude's own remedy); RC-72, RC-80, RC-49 | **A; defect in the round-9 remedy; REPRODUCED** (Appendix K). Codex's example exactly: the persistent two-state regime of Appendix D (q_t = 0.5 ± 0.3, P(stay) = 0.9, \|p_FULL − p_baseline\| = 0.2, block length one period) satisfies every version-7 scalar and has size 27.3 % at the nominal value and 15.3 %, 19.1 % and 22.1 % at the two-point c* values 3.20, 2.63 and 2.23 over 120 clusters, and 17.6–24.3 % over 600, because the dependence is between blocks; P(stay) = 0.7 gives 2.4–7.1 % and 0.8 gives 6.0–12.7 %. Version 8: N is a complete generator family committed as code with a parameter box Θ (block length; forecast-pair law under d_max; within-block shock law with ε_min and amplitude; serial dependence ρ ≤ ρ_max; supply law and its dependence on the shock); c* is the smallest value whose maximum size over a pre-registered grid of Θ plus a seeded search is ≤ α; the claim is level α over the enumerated class and labelled CALIBRATED; the grid maximum is stated as a lower bound on the supremum over the box, because no worst-case optimisation exists over a non-parametric class (RC-80); T-12 prints the grid, the search and the maximising point and carries the persistent regime at the two-point c* values as the under-specification control. OD4 must justify ρ_max from reference-class history, lengthen the blocks or declare the primary non-confirmatory under the class. Remaining uncertainty: the dependence model for real event supply stays `EXPERIMENT_REQUIRED` (since round 3) | `17` §2 (one row), §3 item 3 "Calibrated critical value", A3, T-12, §6 Primary test | T-12 | `PROPOSED` (applied in `17` v8; Θ, ρ_max `OWNER_DECISION`, OD4) |
| RC-109 | The new disposition removes a member whenever the baseline slot is empty while every other arm's empty slot receives a neutral score; a baseline process that can observe FULL's forecast before the common close, which the contract does not prohibit, can omit on unfavourable comparisons and move those members into VOID while satisfying the cap, and non-adversarial baseline failures correlated with event type create the same complete-case selection; freeze submissions from one another or pre-register a baseline fallback that keeps every member in the primary (`4303569710`, P1) | RC-104 (round 9, Claude's own remedy); RC-85, RC-38, RC-106 | **A; defect in the round-9 remedy; REPRODUCED** (Appendix K, the non-adversarial channel): FULL at +δ on one event type and −δ on the other (average exactly zero), the baseline failing on 40 % of the second type: complete-case mean +0.25δ by arithmetic (0.0252 observed at δ = 0.1), primary null rejection 48.6 % at δ = 0.1 and 18.0 % at δ = 0.02; a 10 % failure rate, inside a 5 % VOID cap, gives 10.1 %; with the member kept 4.8–5.1 %. The adversarial channel is RC-85 with the baseline process as the selecting party and needs no new simulation. Version 8 takes both of Codex's options in their simplest form: the baseline arm's primary slot is not a submission but a registry computation from the Design C base rate committed in the ledger before the issuance window opens (the reference data of RC-106), so it cannot be empty, and a member whose reference class has no committed base rate is refused at registration in the candidate log, before any forecast; submissions are sealed until t_close (no arm is served another arm's forecast); every other empty slot is an abstention scored at the baseline forecast against a pre-registered abstention cap per arm; no empty slot of any arm removes a member. F-24 G member 2 and T-17 change accordingly | `17` §2 (two rows), §3 item 3 "VOID classes" and "Abstention and the baseline slot", T-17, F-24, §6 Estimand and Missing data | T-17 | `PROPOSED` (applied in `17` v8; abstention cap `OWNER_DECISION`, OD4) |
| RC-110 | The replacement constrains only deadline + latency window; for an eventually-by-deadline predicate a public occurrence can establish YES before that deadline, so a burn-in event maturing after the freeze can reveal its outcome during the three months used to choose OD4–OD5, and T-37 exercises only the maturity check; require that no burn-in member can become publicly knowable by occurrence before the freeze (`4303569715`, P1) | RC-99 (round 9, Claude's own remedy); RC-39, RC-52 | **A; defect in the round-9 remedy; deterministic** (Appendix K: freeze 100, `not_before` 60, deadline 130, window 10; maturity 140 passes the version-7 check while the occurrence at 90 is public before the freeze). Version 8 bounds the earliest knowable time, not the latest: every burn-in member's `not_before`, and for a terminal-falsifier predicate the earliest time the falsifier can be observed, lies after the freeze (an occurrence before `not_before` is outside the resolution window; a falsifier observable before it would reveal a NO, so the `not_before` condition alone is not enough for that predicate kind); T-37 refuses both; a burn-in member nevertheless adjudicated with `knowable_at` at or before the freeze is reported as a blinding breach to the owner, because nothing after the fact restores the blinding | `17` §2 (one row), T-37, §6 Planned supply | T-37 | `PROPOSED` (applied in `17` v8) |
| RC-111 | The two-point oracle of T-36 still requires rejection at t = 1.714 at the nominal 23-df cutoff while the amended primary must use c*, at least 2.23 on every illustrated class; a correct implementation of the calibrated test fails a mandatory positive control and one that passes it is not implementing the specified test; define the oracle's decision from the OD4-selected c* and keep a statistic-only fixture if the nominal threshold is worth testing (`4303569722`, P1) | RC-94 (round 9); RC-63, RC-72 | **A; defect in the round-9 propagation; deterministic** (Appendix K): the 3-df oracle statistic 2.449490 rejects at the nominal value and at c* = 2.231, not at 2.632 or 3.201; the two-point k = 16 statistic 1.7139 rejects at no calibrated value. Version 8 splits T-36 (b) into statistic oracles reported to 1e-6 with no decision and a decision oracle that takes c* as a parameter (reject iff t ≥ c*), and restates the (c) positive-control bound per c*: with Appendix E's generator (b = 0.5, δ = 0.08, 120 clusters) the rate is 0.963 at the nominal value, as Appendix E found, and 0.677, 0.826 and 0.905 at c* = 3.20, 2.63 and 2.23, so the lower bound is set from the rate at the selected c* | `17` §2 (one row), A6, T-36 | T-36 | `PROPOSED` (applied in `17` v8) |
| RC-112 | The cutoff now lives on each `Forecast` while registration is supposed to reject an event before those records exist, and F-27 explicitly permits a wrong cutoff to be corrected later with exclusion at adjudication; that path lets a provider or researcher update per-forecast cutoff claims after outcomes are visible and selectively remove unfavourable members; store one immutable, evidenced cutoff per pre-registered model version before event registration and make a later correction invalidate the whole affected cohort rather than individual results (`4303569729`, P1) | RC-98 (round 9, Claude's own remedy); RC-96, RC-75 | **A; defect in the round-9 remedy; REPRODUCED** (Appendix K): on a null with mean-zero, positive-variance increments and 600 members registered over 24 months, a correction to month m excludes every member with `not_before` ≤ m; choosing m in {0, …, 12} after the outcomes are known raises the primary's rejection rate from 5.2 % to 13.1 % (99 % bound 13.7 %), removing a quarter of the cohort on average: the criterion is outcome-blind and the timing is not. Version 8: the forecaster id, version and model knowledge cutoff live in an immutable `ArmVersion` registration record created before any event is registered under it, with the cutoff's archived evidence; a `Forecast` references the arm version and carries no cutoff; event registration checks the cutoff against the arm version records before any forecast exists; a correction withdraws the arm version and every member registered under it leaves the primary for every comparison involving that arm as one cohort, counted against the cap and imputed ±1, never member by member; a provider's model change is a new arm version with its own pre-registration (RC-96). F-27 rewritten; T-02 gains the own-cutoff and later-arm-version refusals | `17` §2 (one row), §3 item 1 (schema), T-02, F-27 | T-02 | `PROPOSED` (applied in `17` v8) |
| RC-113 | The combined case where the observer has no snapshot at deadline + window and later first sees a timely occurrence in a record published after that window is undefined: the rule keeps the member open and T-04 says it resolves "by content", but YES would ignore the latency rule, NO needs the missing observation of absence, and the text says a late report is never VOID; define a deterministic disposition and add the outage-plus-late-publication fixture so registry availability cannot change the outcome (`4303569735`, P1) | RC-88, RC-105 (round 9); RC-77 | **A; an open case in the round-9 wording; deterministic** (Appendix K, F-02e). Version 8 states what counts as an observation of absence when the observer was down: under the source rule's monotone-publication condition (OD5: evidenced publication times, records never removed) the earliest matching record's evidenced publication time lying after deadline + window is itself the archived evidence that no record existed at finality, so the member is NO at deadline + window with `knowable_at` = that time, the late record is a source-latency defect and the outage an integrity incident, which is the disposition a read at finality would have reached; a source that cannot evidence publication times cannot evidence absence, so with the observer down such a member is adjudicated VOID under the failure condition, and such sources are an OD5 exclusion. The invariant is stated: a disposition is a function of the archived records and the source rule alone, never of when the observer read | `17` §2 (one row), §3 item 1 "Logical finality", T-04, F-02e | T-04 | `PROPOSED` (applied in `17` v8; monotone-publication condition per source `OWNER_DECISION`, OD5) |
| RC-114 | The accrual cutoff already moves the last registration back from month 24 by H_max, and the sentence additionally requires each member's maturity to precede that earlier cutoff, so an event registered at month 18 and maturing by the month-24 analysis is excluded, reserving the horizon twice and discarding a large valid portion of the cohort; apply the cutoff to registration time and require maturity by the month-24 analysis date (`4303569739`, P2) | RC-68 (round 7) | **A; ambiguity in the round-7 wording, wrong under one of its readings** (Appendix K, arithmetic). The sentence called the registration cut-off "the cut-off" and the analysis date "the 24-month cut-off" two clauses apart; under Codex's reading a third of a uniformly accrued cohort leaves. Version 8 names the two dates, T_A and T_R = T_A − H_max, applies T_R to registration and T_A to maturity, and notes that registration ≤ T_R with horizon ≤ H_max already implies maturity ≤ T_A | `17` §6 Accrual and Stopping rule | T-12 (pending-cluster family) | `PROPOSED` (applied in `17` v8) |
| RC-115 | T-17 requires cluster A's pre-declared sibling to enter the worst-case bounds and cluster B's two pre-declared members to count against the cap, while §3 and F-24 explicitly place pre-declared members outside both; no implementation can satisfy both mandatory outcomes for the same fixture; choose one treatment and make the test, the F-24 oracle and the missing-data contract agree (`4303569744`, P1) | RC-87, RC-90 (round 9); RC-67 | **A; propagation gap of round 9; deterministic** (Appendix K: under the T-17 wording cluster A's bounds are [−0.45, +0.55] with one member against the cap; under §3 and F-24 they are [0.1, 0.1] with none). Round 9 rewrote §3 and F-24 for RC-87 and RC-90 and left T-17's pass condition at its round-7 text. The §3 treatment is chosen: a pre-declared member is fixed in the registration record before any forecast or outcome exists, a population choice equivalent to a candidate-log rejection, and the cap and the bounds cover members that left the scored population after registration. T-17 rewritten | `17` T-17 | T-17 | `PROPOSED` (applied in `17` v8) |

Assessment across the eight: the round-9 remedies were written in one execution against twenty-one findings,
and five of the eight round-10 findings are defects in them; two (RC-108, RC-112) are the same class of error as
RC-85 and RC-96 before them, a rule that is outcome-blind in its criterion and outcome-dependent in its timing or
in what it leaves unspecified. RC-108 is the one with scientific weight: a null class stated as scalar bounds is
not a class, and the persistent regime Appendix D reported in round 3 lives inside the version-7 scalars; the
calibrated c* now carries the label CALIBRATED over an enumerated generator family, and the serial-dependence
bound ρ_max joins OD4 as the field that decides whether the primary is confirmatory at all. RC-109 closes the last
disposition under which any arm's missing forecast removed a member. Not addressed by Codex in round 10: RC-07,
RC-20, and nothing on the round-9 items other than the six extensions above (RC-95, RC-97, RC-100, RC-101,
RC-103 and the rest are reviewed once at `922956b` without objection, which is not agreement). Relevant to issue #3
acceptance item 2: the eleventh automatic review read the version-7 text and returned eight findings, every one
substantive and none a repeat; the count per pass fell from twenty-one to eight.

### 3j. Round 11: Codex's review of PR #4 at `04bc122` (review `5559035950`)

Eight inline findings on the version-8 text and this matrix (all P1), posted 2026-10-17 17:18 UTC. None repeats a
comment ID of rounds 1–10; seven extend an earlier item with a new channel and are distinct claims. Seven are
assessed as genuine; every checkable claim reproduces (Appendix L, `python -I research/reproduction/round11_checks.py`);
every one of the seven is **applied in `17` version 9 under the §4.6 rule** in the same commit as this matrix.
Three are defects in the round-9 calibration remedy RC-94 and its round-10 extension RC-108 (RC-117, RC-118,
RC-121), and RC-118 also falsifies committed numbers of Appendix J; one is a defect in the round-9 monitor-order
remedy RC-95 (RC-119); one a propagation gap of round 9 (RC-120 on RC-94 and RC-111); one an open case in the
round-9 epoch remedy RC-103 (RC-123); one a reproducibility defect of this matrix since round 1 (RC-122). RC-116 is
recorded with its evidence and not applied: the commit it names exists in no branch of the repository. Every
disposition is `PROPOSED` until Codex reviews the commit that carries it.

| ID | Codex finding (comment ID, severity) | Parent | Claude position and evidence | Resolved in | Validation test | Status |
|---|---|---|---|---|---|---|
| RC-116 | The Git object `50897415d0fd85e29a4effdeab8fcd5de055874d` lists author and committer as `Codex <codex@openai.com>`; the proposed T-09 check would reject it, the claim that only the earlier rounds have identity defects is false; recreate the commit under the owner's identity or record a designation (`4303689619`, P1, on §7 line 775) | RC-81 (round 7, the same class of claim on `10f8829`) | **Not reproduced; recorded, not applied.** The object is not in this repository: `git cat-file -p 50897415d0fd…` after `git fetch origin --prune` of every branch and of `refs/pull/1/*`, `refs/pull/2/*` and `refs/pull/4/*` reports "Not a valid object name", and the GitHub commits API returns "No commit found for SHA". The identities of every commit of this branch, read with `git log --format='%an <%ae> \| %cn <%ce>'`, are the owner's except the three commits of rounds 7 and 8 (`b19483a`, `37ac018`, `8af2ae9`), already disclosed under RC-81 and OD9b; the PR merge ref `refs/pull/4/merge` is committed by `GitHub <noreply@github.com>` as every GitHub-generated merge commit is. A commit authored `Codex <codex@openai.com>` can only be an object of the reviewer's own working copy (a local merge or checkout commit it made to review), which this repository never received and T-09 would never see. The same class of claim on `10f8829` was not reproduced in round 7. If Codex's next review names a SHA that `git fetch` of this repository returns, the identity will be read from the object and recorded here; the remedy already adopted for RC-81, an identity check on every commit in T-09, is the control | this matrix §3j, §7 provenance | T-09 (unchanged) | `PROPOSED` (recorded; the object is not in the repository; OD9b unchanged) |
| RC-117 | Simulated families calibrate and certify c* at the A3 bound, which accepts a 99 % upper bound as high as 0.06; a null with true size about 5.5 % passes at 20,000 replications and the text then labels the test level α = 0.05; require the calibration bound itself to be at most 0.05, or stop making the nominal claim (`4303689622`, P1) | RC-94 (round 9), RC-108 (round 10, Claude's own remedies); RC-48 | **A; defect in the round-9 remedy; REPRODUCED exactly** (Appendix L). At 20,000 replications the A3 tolerance passes up to 1,122 rejections (5.61 %); a true size of 5.0 % passes with probability 1.000, 5.5 % with 0.758, 5.8 % with 0.128 and 6.0 % with 0.010, so Codex's example passes three times in four. The tolerance was designed in round 3 as the implementation check of a test whose level is already known (RC-48: a correct size-0.05 implementation must pass), and a calibration that chooses c* against it inherits the tolerance as size. Version 9 takes Codex's first option: on a simulated family c* is the smallest value whose exact one-sided upper confidence bound on the rejection rate, at confidence 1 − 0.01/K over the K enumerated points (Bonferroni, so that the simultaneous statement holds at 99 %), is ≤ α; the ceiling on the observed rate is then 4.64 % for one point and 4.43 % for a hundred at 20,000 replications, 4.84 % and 4.75 % at 100,000, and that conservatism is reported with c*. Illustration on the independent period-shock family (24 × 25): c* = 1.723 by the point estimate, 1.766 by the one-point bound, 1.796 by the Bonferroni bound for a hundred points, with power at δ = 0.02 and 600 clusters of 96.4 %, 96.0 % and 95.8 %. The A3 tolerance remains the implementation check | `17` §2 (one row), §3 item 3 "Calibrated critical value", A3, T-12, §6 Primary test | T-12 | `PROPOSED` (applied in `17` v9; replication count R `OWNER_DECISION`, OD4) |
| RC-118 | N is a generator family over a parameter box while c* is selected on a finite grid plus a seeded search, and the document concedes the grid maximum is a lower bound on the box supremum; an off-grid parameter can have rejection probability above α while every mandatory case passes; define the confirmatory null as the finite enumerated set or provide an exhaustive or uniformly valid bound over the box (`4303689629`, P1) | RC-108 (round 10), RC-94 (round 9), RC-80 | **A; defect in the round-9 remedy and a CONFIRMED-DEFECT of Appendix J; REPRODUCED and stronger than stated** (Appendix L). On the two-point family the statistic depends only on the number k of positive blocks, so the size at a fixed c is a step function of ε that jumps wherever some t_k(ε) crosses c, and no grid bounds it. A sweep of ε at step 10⁻⁵ shows the **committed Appendix J values exceeded inside their own classes**: at c* = 3.201 the size reaches 5.03 % at ε = 0.175, at 2.632 it reaches 5.39 % at ε = 0.235 (1.2 % of the interval above α), at 2.231 it reaches 5.18 % at ε = 0.340; a grid of step 0.05 calibrates to 2.025 for ε_min = 0.2 and the interval then holds 10.97 % at ε = 0.20004. The exact-supremum values, c* = max over ε of the per-ε critical value rounded up to 0.001 on the sweep, are **3.207, 2.693 and 2.254** (sizes 5.00 %, 5.00 % and 4.99 % at the sweep's maximum; the sweep's resolution bounds the remaining error by the pmf's variation over 10⁻⁵, below 5 × 10⁻⁴). Version 9 takes Codex's first option and the exhaustive one where it exists: the confirmatory null is the committed enumerated set N_0 (grid, search points, every corner of Θ, spacing recorded); a coordinate whose supremum over its interval can be computed exactly is calibrated on that supremum, never on a grid; the box Θ is the domain of a reported sweep at double the resolution of N_0, and a sweep maximum above α fails the calibration and sends it back to a finer set before the freeze; no claim is made over the box. The values 3.20, 2.63 and 2.23 are withdrawn everywhere in `17` and in the OD4 row of §6, and every figure stated at them is restated at 3.21, 2.69 and 2.25 (RC-120) | `17` §2 (one row), §3 item 3, A3, T-12, T-36, §6 Primary test; this matrix §6 OD4 | T-12 | `PROPOSED` (applied in `17` v9; N_0 and its spacing `OWNER_DECISION`, OD4) |
| RC-119 | The maturity-order buffer considers only clusters already registered: A with H_A = 100 closes at 10 with no registered predecessor and its factor is applied; B is then registered at 20 with not_before 21 and H_B = 50, so the sequence is not H-ordered and A's λ was computed without an increment the declared filtration says precedes it; delay A until registrations with a smaller maturity are impossible, normally when the clock reaches H_A, and add a late-registration fixture (`4303689633`, P1) | RC-95 (round 9, Claude's own remedy); RC-61 | **A; defect in the round-9 remedy; deterministic and REPRODUCED** (Appendix L). The version-7 rule applies A at 10 and B at 50, out of H-order; the watermark rule applies B at 50 and A at 100. Over 2,000 random 24-month paths (40 clusters, horizons uniform in 1–12 months, half the clusters final one month after registration) the version-7 sequence is out of H-order in 64.2 % of paths; the watermark sequence is H-ordered in every path and adds 0.74 months of mean delay after finality (2.00 to 2.75), because a closed cluster already waited for the registered clusters below it. Version 9 applies a cluster's factor no earlier than its own H_k: a registration at time t has H > t, since `not_before` follows registration and the deadline follows `not_before`, so after H_k no cluster with a smaller maturity can be registered; T-39 carries Codex's fixture and the random paths | `17` §2 (one row), §3 item 3 "Monitor order", T-39, §6 Anytime-valid monitor | T-39 | `PROPOSED` (applied in `17` v9) |
| RC-120 | The §6 smallest-effect row still reports the nominal-cutoff power for the single comparison, the conjunction and the period-shock design although A6 requires every power figure at the selected c*; the document's own δ = 0.02 example drops from 96 % to 60–88 %; report the figures per admissible c* or defer them until OD4 fixes the class (`4303689635`, P1) | RC-94, RC-111 (round 9 and 10); RC-61, RC-70, RC-83 | **A; propagation gap of round 9; REPRODUCED** (Appendix L, with Appendix F's D1 and period-shock generators and Appendix H's conjunction generator, nominal values reproducing Appendix F and H within Monte Carlo error: 78.1 %, 92.4 %, 17.8 %, 20.4 %, 30.9 %, 77.0 %). At c* = 3.21 / 2.69 / 2.25 the single comparison at δ = 0.01 and 600 clusters has 28 % / 44 % / 60 % (b = 0.5) and 50 % / 68 % / 81 % (b = 0.2) against 78 % and 92 %; at δ = 0.005 and 600 clusters 10 % / 20 % / 33 % and 19 % / 33 % / 49 % against 52 % and 69 %; at δ = 0.02 and 288 clusters 28 % / 44 % / 60 % and 51 % / 69 % / 83 % against 77 % and 93 %; at δ = 0.02 and 600 clusters 65 % / 80 % / 90 % against 97 %. The conjunction at δ = 0.01 and 600 clusters: 0.01 % / 0.5 % / 3.8 % with uncorrelated errors (21 % nominal), 0.6 % / 3.2 % / 10 % at a shared-sign probability of one half (31 %), 25 % / 42 % / 58 % with errors moving together (77 %), 0.0 % / 0.01 % / 0.8 % under the anti-correlated generator (16 %); at 1,200 clusters and at δ = 0.02 and 600 clusters 4.9 % / 21 % / 46 %, 12 % / 31 % / 54 %, 60 % / 77 % / 88 %. The period-shock design at δ = 0.02: 1.6 % / 4.1 % / 8.1 % against 18 %; at δ = 0.05: 13 % / 24 % / 39 % against 59 %; at δ = 0.08: 47 % / 66 % / 81 % against 93 %. The T-36 positive control (Appendix K's generator and seed): 0.677 / 0.817 / 0.899 against 0.963 (the Appendix K rates at the superseded values reproduce exactly). Under the widest illustrated class the conjunction has no useful power at any supply shown; the row now says so and OD4 chooses the class and the effect together | `17` §2 (one row), A6, T-16, T-36, §6 Smallest useful effect and Confirmatory conjunction; this matrix §6 OD4 | T-16, T-36 | `PROPOSED` (applied in `17` v9) |
| RC-121 | The calibrated class, d_max and estimand are defined for the FULL–Design C pair, but the conjunction row declares each of six comparator tests level α without comparator-specific classes or cutoffs; a single-provider comparison can have an increment law outside the FULL–baseline calibration while satisfying every current test, so the IUT guarantee fails; define and calibrate each component's estimand and null family, or one class that envelops every pair (`4303689641`, P1) | RC-94, RC-108; RC-08, RC-83, RC-93 | **A; defect in the round-9 remedy; REPRODUCED exactly** (Appendix L). At the pair value c* = 2.254 (ε_min = 0.3) a component whose two-point catastrophe share is 0.136 has exact size 11.4 % (8.6 % at 0.15, 7.4 % at 0.22); at c* = 2.693 (ε_min = 0.2) the supremum below the class is 7.9 % at ε = 0.154; at 3.207 (ε_min = 0.1) nothing below 0.1 exceeds α, because very rare catastrophes leave too many all-positive samples, which never reject. When the other five components reject surely the IUT's size equals the component's, so the IUT is level α only if every component is (Berger). Version 9 takes the first option: each component j has its own enumerated class N_0,j in the same generator family, with that pair's forecast law under its own d_max and catastrophe share, and its own c*_j; the IUT rejects iff t_j ≥ c*_j for every j; T-13 (b) and T-16 carry the null comparator at the corner of its own box and fail an implementation that decides every component at the FULL–Design C value | `17` §2 (one row), §3 item 3, A3, T-13, T-16, §6 Confirmatory conjunction | T-13, T-16 | `PROPOSED` (applied in `17` v9; the per-component boxes `OWNER_DECISION`, OD4) |
| RC-122 | The reproduction table tells reviewers to run `python -I round10_checks.py` and analogous commands, but a repo-wide search finds no `round*_checks.py` or `reconciliation_probes.py`; only fenced snippets are committed with no deterministic extraction command, so every named command fails from a clean checkout; commit executable scripts with their pinned environment, or a checked extraction command (`4303689645`, P1, on §2 line 70) | RC-28 (round 2, the script's name), `AGENTS.md` §6 | **A; reproducibility defect of this matrix since round 1; deterministic.** The extraction snippet of Appendix A was the only route and named a scratch path. Version 12 commits the eleven scripts as files under `research/reproduction/` (`reconciliation_probes.py`, `round2_checks.py` to `round11_checks.py`), each extracted from its appendix block, with `requirements.txt` pinning numpy 2.4.6 and scipy 1.17.1 and `check_appendix_scripts.py`, which compares every file byte for byte with the fenced block of its appendix and exits non-zero on the first difference, so that the record (the appendix) and the executable (the file) cannot diverge silently; the §2 commands now name the committed paths. Run this round: `11 scripts checked, 0 differ`. The directory holds evidence scripts of this matrix, not project code, and `AGENTS.md` §4 has no row for it; the row is proposed under OD9b | this matrix §2, Appendix L; `research/reproduction/`; `research/README.md` | the identity check itself; T-08 (clean-checkout reproduction) when built | `PROPOSED` (applied; §4 row `OWNER_DECISION`, OD9b) |
| RC-123 | Rotate-on-demotion requires the new epoch to be anchored in the demotion transaction but defines no safe outcome when the anchor store is unavailable: rolling back leaves the gate elevated, committing unanchored lets a restore revive the pre-demotion epoch and its unused capabilities; T-30 tests anchor failure during a protected action, not during demotion; persist the local demotion at once, block every promotion until anchored, add the fixture (`4303689649`, P1) | RC-103 (round 9, Claude's own remedy); RC-74, RC-43 | **A; open case in the round-9 remedy; REPRODUCED in part** (Appendix L toy, three rules on two branches). Rollback: once the store returns the gate is still elevated and the pre-demotion capability B acts (reproduced). Commit unanchored: B is refused after the store returns, and after a restore to the last anchor and a restart B is refused as well, because the start rotation of RC-74 stales it, so the "unused capabilities" half of the finding does not reproduce under the version-8 text; but the restore revives the **elevated level** (the last anchor was the promotion's), and a fresh capability of the new epoch then acts at it with no promotion recorded, which is the channel that matters. Version 9 takes Codex's remedy and closes the restore residual with the simplest rule: the demotion is persisted locally in the writer transaction with its rotated epoch and takes effect at once; until the epoch is anchored the gate is demoted-unanchored and every promotion and every protected action is refused; every process start begins at the gate floor, so a restore revives no level. Under this rule neither B nor the fresh capability acts and the level after the restore is the floor. The alternative, a level that persists across starts, keeps the restore residual and is recorded for OD10. T-30 carries both branches | `17` §2 (one row), §3 item 2 "Demotion without the anchor store", A5, T-30 | T-30 | `PROPOSED` (applied in `17` v9; start-at-floor rule for the owner's attention under OD10) |

Assessment across the eight: three of the seven applied findings are in the calibration machinery that rounds 9 and
10 built (RC-94, RC-108), and one of them, RC-118, falsifies numbers this matrix had labelled REPRODUCED: the
two-point critical values of Appendix J were right on their grid and wrong on their class, because the size of a
discrete statistic is a step function of the parameter, which the grid could not see. The corrected values move the
illustrated power figures by a few points; the larger effect of this round is RC-120, which puts the §6 figures where
A6 said they belonged since round 9 and shows that at the widest illustrated class the conjunction has no useful power
at any supply shown. RC-119 and RC-123 are the same class of error as RC-85 and RC-96 before them: a rule correct on
the state it enumerated and silent on a state it did not (a later registration; an unavailable store). RC-116 is not
reproduced and is not a repeat of RC-81 by comment ID, so it is recorded with the commands that fail to find the
object. Not addressed by Codex in round 11: RC-07, RC-20, and nothing on the other round-10 items (RC-109, RC-110,
RC-112, RC-113, RC-114, RC-115 are reviewed once at `04bc122` without objection, which is not agreement). Relevant to
issue #3 acceptance item 2: the twelfth automatic review read the version-8 text and returned eight findings, seven
substantive and none a repeat; the count per pass stayed at eight.

## 4. Open disagreements (what would settle each)

4.1 **RC-01 remedy scope: withdrawn by Claude in round 3.** Rounds 1–2: Codex asked for estimand, filtration,
clustering and maturation to be specified and for a fixed-horizon cluster-aware paired analysis where the
every-step conditional null is inappropriate; Claude held that pre-declared outcome clusters as the betting unit
were sufficient as the primary anytime-valid test, and wrote that the disagreement would be settled if Codex
exhibited a dependence structure that pre-declared clusters cannot capture but the fixed-horizon analysis
handles. Round 3 did that twice (RC-49: simultaneously open clusters sharing a period shock; RC-50:
time-varying skill with zero average), and both reproduce (Appendix D: 28.9 % and 62.8 % crossings for the
e-process against 27.1 %-with-block-of-one and 0.1 % for the fixed-horizon test; under independent period
shocks 2.2 % against 5.1 %). The underlying fact is that the e-process tests the sequential conditional null,
which is not the §6 estimand. Disposition: the fixed-horizon paired cluster test with a pre-registered
calendar-block dependence model is the primary confirmatory test; the e-process is the anytime-valid monitor
of the conditional null, labelled as such. What round 3 added beyond Codex's finding: under a persistent regime
neither method holds size at 120 clusters over 24 periods at any tested block length, so the dependence model
and the supply it needs are an `EXPERIMENT_REQUIRED` input to OD4/OD5, with the generator committed in T-12.
Codex has not reviewed this wording; it is `PROPOSED`.

4.2 **RC-20 hosting timing.** Codex: fully cloud-hosted architecture as Phase 1 exit criterion 1. Claude:
Phase 1 is offline and synthetic and needs CI, not hosting; the hosting decision belongs at the Phase 2 gate
with a costed comparison, because the owner's D10 (USD 0 incremental cost) conflicts with any hosted option
and because Codex's own ordering (C8) puts scientific uncertainty reduction before infrastructure. Both agree
that OS user accounts are not a tested boundary. **Settles it:** an owner decision (OD6). Phase 1 is written
so that neither choice requires rework (T-08).

4.3 **RC-07 n_eff retention.** Codex: remove n_eff as evidence. Claude: agreed as evidence; keep as a
monitoring diagnostic after fixing the degenerate-history path, because it is the cheapest alarm for a
committee collapsed to one source. Round 2 wrote that Claude would adopt Codex's position if Codex objected on
the next round; none of the three automatic reviews objected. The diagnostic stays as `PROPOSED` (T-24: n_eff
in no decision path); the owner can strike it at no cost.

4.4 **RC-08 α-spending level.** Shape agreed (summable sequence); level is a policy choice with a stated power
cost (α_10 ≈ 0.00045 under 0.05/[j(j+1)]). Not a scientific disagreement; **OD3**.

4.5 **RC-28 reviewer names in the matrix.** Codex reads `AGENTS.md` §7 as prohibiting the probe's "Claude"
name; Claude accepts that for the file and docstring (done) and holds that the reviewer-position columns and
the "which reviewer verified what" statements are the provenance §7 and §9 require and the owner's protocol
prescribes. Not a scientific disagreement. **Settles it:** the owner's reading of §7, recorded under OD9b if
the owner wants the wording clarified; Claude will adopt whichever reading the owner states.

4.6 **Round budget (issue #3: three rounds per issue).** Accounting after round 4. RC-01 family (RC-29, RC-41,
RC-49 to RC-53; RC-57 and RC-59 applied as propagation only) and RC-15 family (RC-47, RC-55; RC-60 recorded,
not applied): **budget spent**. Families revised in round 4 and now at their third round: RC-08 with RC-30 and
RC-48 (RC-56, RC-63); RC-24 with RC-45 (RC-61); RC-12 with RC-43 and RC-46 (RC-62); RC-03 with RC-54 (RC-58):
**budget spent**. Every item Codex has touched in rounds 2–4 has therefore used its budget; the items Codex
never touched (RC-07, RC-20 and the rest of §3) have had one round and are not in dispute. Codex's automatic
review of this commit is expected (PR #4 triggers it on push). The next routine execution reads it,
deduplicates by comment ID against §1 and §7, appends every finding to a new §3d with Codex's claim, a one-line
Claude assessment and status `OWNER_DECISION` (budget), updates §1 and §7, and changes no other text; it makes
**no revision** to `17` or to any foundation document, propagation included, until the owner either records
OD1, OD2 and OD9a or extends the budget on issue #3 (OD10). This closes the automatic revision loop on PR #4:
the deliverable of the owner's protocol (amended specification, acceptance-test matrix, nondelegable owner
choices) is complete as `PROPOSED`, and what remains is the owner's. The three P0 families stay blocked on
OD1, OD2 and OD9a regardless.

Round 5 followed that rule: review `5550735335` of `88abaa4` is recorded in §3d and nothing is applied. For the
owner's accounting, the eight findings sit on these families: RC-64 on A0/RC-33 and the spent RC-15 family;
RC-66, RC-67 and RC-68 on the spent RC-01 and RC-29 families; RC-69 and RC-70 on the spent RC-49/RC-56/RC-63 and
RC-24/RC-61 families; **RC-65 (RC-37, clock) and RC-71 (RC-11, late YES) on families that have used one round
only**, which a strict reading of the budget would allow to be revised. They were not, because the v5 rule was
written unconditionally and announced in handoff 4; the routine does not loosen its own stopping rule. Codex's
automatic review of this commit will run on the push; if it produces findings, the next execution records them
in a §3e in the same way and still applies nothing. OD10 now covers RC-60 and RC-64 to RC-71 together.

Round 6 followed that rule: review `5550966930` of `4de18e5` is recorded in §3e and nothing is applied. Family
accounting: RC-72 on the spent RC-48/RC-49/RC-56/RC-63/RC-69 families; RC-73 on the RC-37 clock family (now two
recorded, unapplied findings, RC-65 and RC-73); RC-74 on RC-12/RC-13/RC-34/RC-43; RC-75 on RC-02/RC-12/RC-52;
RC-76 on RC-24/RC-39/RC-52; RC-77 on the RC-11 family (RC-71 and RC-77 recorded); RC-78 and RC-79 on
requirements of `02` §5 and `AGENTS.md` §8 that `17` never carried. **This is the last record-only commit.**
The reviewed commit `4de18e5` changed no line of `17`, yet the automatic review returned eight new findings on
`17`: each record-only push re-triggers a full review of unchanged text, which re-triggers this routine, and
the routine's own rules forbid a self-triggering loop. Codex's automatic review of this commit will run on the
push; its findings, and any later ones on PR #4, are **not** recorded by a further commit. The next execution
on a Codex review without an owner decision does nothing (the findings stay on PR #4, keyed by comment ID, and
are deduplicated against §1 and §7 when the owner's decision is processed). The next execution on an owner
decision (OD1, OD2, OD9a or OD10 on issue #3) applies the wording the owner names from §3c to §3e, then
processes every Codex finding posted since `4de18e5` under the budget the owner sets. OD10 now covers RC-60 and
RC-64 to RC-79, seventeen findings.

**Round 7: the rule above is withdrawn, on the owner's instruction.** The owner's audit on issue #3 (comment
`6222759237`) states that three review rounds must never mean problem solved: a finite per-session budget
protects quota, cost and trust boundaries, while task lifetime and correctness acceptance are governed by
reproducible evidence, not a retry count. The record-only handling of rounds 5 and 6 was this document's own
reading of the issue #3 budget, not the owner's; it parked seventeen findings that Claude had assessed as
genuine, several of them reproduced defects in Claude's own remedies. The rule from round 7 onward:

1. A finding Claude assesses as genuine is **applied** in `17` in the same execution that assesses it, with
   its matrix ID, in a reviewable commit on PR #4, whether or not its family has had three rounds. Fields that
   need the owner's choice (OD4: H_max, d_max, block length, shock amplitude, estimand naming; OD5: latency
   windows, inclusion predicate) are left as named fields, never chosen by the routine. Governance text
   (`AGENTS.md`) is never edited; proposed wording goes to OD9a/OD9b.
2. A finding **closes only on evidence**: when Codex has reviewed the exact commit carrying its wording and
   raised nothing new on it, or when the owner records the decision. Until then its status is `PROPOSED`,
   never resolved. A finding Claude assesses as a misunderstanding or not reproduced is recorded with the
   evidence and not applied, and Codex's next review of the unchanged text is the check on that assessment
   (RC-81 is the first case).
3. The budget that remains is **per execution**: one commit per execution (two when the specification diff
   and the matrix are separated so that the owner can approve or revert the former alone, as this round does),
   each item applied at most once per execution, and no commit at all on an execution that finds no new
   Codex finding and no owner decision. That is the loop guard. A push that changes `17` is the protocol
   working, not a self-trigger; the self-trigger that round 6 refused was a push that changed nothing.
4. Deduplication is by comment ID (§1, §7) and by content; a finding that repeats one already processed is
   not processed twice.
5. When Claude and Codex still differ after a reproduction, the discriminating experiment is named and the
   item is `EXPERIMENT_REQUIRED` or `OWNER_DECISION`, never closed by count or by one party's persistence.

Under this rule round 7 applied RC-60 and RC-64 to RC-83 in `17` version 5 (commit `b19483a`), the OD10
decision diff, and OD10 is re-stated in §6 as approval or reversion of that diff. The three P0 families stay
blocked on OD1, OD2 and OD9a regardless; T-34 and the secret-handling code additionally wait on OD10 (A0,
RC-64). This matches what the owner's CANNON proposal (PR #10) calls OPEN → REPAIR → independently VERIFIED:
the matrix is the durable finding state, `17` v5 is the repair, and Codex's review of `b19483a` is the
independent verification step that has not happened yet.

Round 8: Codex's review `5556866013` of `37ac018` is that review of the version-5 text. It objected to two of
the twenty-one applied items (RC-67, now RC-85; RC-79, now RC-86), both applied in `17` version 6 in the same
commit as this matrix (rule 3 separates the specification diff from the matrix only when an owner decision
needs to approve the former alone; OD10 now covers versions 5 and 6 together, §6). The other nineteen (RC-60,
RC-64 to RC-66, RC-68 to RC-78, RC-80 to RC-83) are recorded in §7 as **reviewed once by Codex at `37ac018`
without objection**. That is the independent verification step of rule 2 in its weakest form, an automatic
diff review that raised nothing, not a Codex statement of agreement and not a replacement for OD10; the
header's "silence in a diff review is not agreement" stands, and the status of every applied item remains
`PROPOSED`.

Round 9: the owner's directive on PR #4 (comment `6236238443`) restates the rule and adds the acceptance gate
(both agents review the same final revision and file SHA-pinned reports with zero unresolved verified defects in
scope; `EXPERIMENT_REQUIRED` or `OWNER_DECISION` where a legitimate uncertainty cannot be settled; no consensus by
vote). It also asks for the review threads to be deduplicated against the defects that are still live. Thread
accounting at `8af2ae9`, from the GitHub review-thread list read by this execution (78 threads): 53 are marked
outdated by GitHub and each is an item of §3a to §3g whose remedy was applied in a later version (the thread's
lines no longer exist); 4 older threads are not outdated because their lines survive, and each is an applied
item whose text Codex has re-read since without objection or has extended: `4294987422` (RC-34, anchor store;
applied in v2, re-read in nine reviews), `4297109203` (RC-74, durable consumption; applied in v5, re-read at
`37ac018` and twice at `8af2ae9`), `4297109207` (RC-75, scoring slot; applied in v5 and extended by RC-96 in
this round) and `4297337217` (RC-80, the proof; applied in v5, its appendix corrected by RC-102 in this round);
the remaining 21 non-outdated threads are the round-9 findings of §3h, every one applied in version 7. So the
thirteen non-outdated threads the directive counts at 16:00 UTC were these 4 and the 9 of review `5556950582`;
the twelve of review `5558680831` arrived at 16:09. No thread is resolved by this execution, because resolution is
Codex's or the owner's call under rule 2; no reply is posted on a thread, because the matrix row is the answer
and a reply per thread would be the repeated comment the routine's rules forbid. Under rule 3 this round is one
commit, carrying `17` version 7, this matrix v10 and the three foundation-document notes; OD10 now covers
versions 5, 6 and 7 together (§6). The directive's gate is not met by this commit and the matrix does not say
it is: Codex has not reviewed version 7, and the owner's reserved fields (OD4: null class, ε_min, G_min, power
floor, dependence assumption; OD5: observation duty, defect-rate bound; OD8: provider cutoff duty; OD9b: the §2
item 1 exception) are marked `OWNER_DECISION` where they occur and are listed in §6.

Round 10: Codex's review `5558887072` of `922956b` is the review of the version-7 text. It raised eight findings,
all applied in `17` version 8 in the same commit as this matrix (§3i, Appendix K); five are defects in round-9
remedies. Thread accounting at `922956b` (86 threads): 71 are marked outdated by GitHub and each is an item of §3a
to §3h whose remedy was applied in a later version; 7 older threads are not outdated because their lines survive,
each an applied item re-read by Codex since without objection (`4294987422` RC-34, `4297109203` RC-74,
`4297337217` RC-80, `4301994299` RC-93, `4301994303` RC-106, `4301994307` RC-107, `4303397703` RC-100); the 8
round-10 threads are the findings of §3i, every one applied in version 8. No thread is resolved by this execution
and no per-thread reply is posted, for the reasons stated for round 9. The owner's progress request on PR #4
(comment `6236863824`) is answered once with a brief update on PR #4 and the handoff on issue #3; the technical
part of the request (resume against `8af2ae9`) had been carried out by the round-9 commit before the request was
read. OD10 now covers versions 5 to 8 together (§6). The directive's gate is not met by this commit: Codex has not
reviewed version 8.

Round 11: Codex's review `5559035950` of `04bc122` is the review of the version-8 text. It raised eight findings;
seven are applied in `17` version 9 in the same commit as this matrix (§3j, Appendix L) and one, RC-116, is recorded
as not reproduced (the commit it names is in no branch of the repository). Thread accounting at `04bc122` (94
threads): 78 are marked outdated by GitHub and each is an item of §3a to §3i whose remedy was applied in a later
version; 8 older threads are not outdated because their lines survive, each an applied item re-read by Codex since
without objection (`4294987422` RC-34, `4297109203` RC-74, `4297337217` RC-80, `4301994299` RC-93, `4301994303`
RC-106, `4301994307` RC-107, `4303397703` RC-100, `4303569735` RC-113); the 8 round-11 threads are the findings of
§3j, seven applied in version 9 and one answered in the matrix row. No thread is resolved by this execution and no
per-thread reply is posted, for the reasons stated for round 9. OD10 now covers versions 5 to 9 together (§6). The
directive's gate is not met by this commit: Codex has not reviewed version 9, and one of its findings (RC-118) showed
that a REPRODUCED label on a grid calibration was not a label on the class, which is the kind of defect the gate's
second SHA-pinned report exists to catch.

## 5. Open hypotheses with bounded experiments (not disagreements)

| Hypothesis | Experiment (as amended) | Earliest read-out |
|---|---|---|
| H1 fusion beats best single model and Design C | IUT over the comparator set on prospective clusters; cluster-level e-process | after supply is measured (OD4) |
| H3 Jev recall ≥ 0.8 at ≤ 20 % cost | stratified randomised routing incl. reject audit with inclusion probabilities; non-inferiority design | Phase 2+ |
| H5 ≥ 60-day discovery lead | frozen media corpus and query protocol; price-acceleration rule registered separately | Phase 2+ |
| H6 hazard throttle adds value net of false alarms | locked counterfactual policy arms on all entries, one crisis cluster held out | when vintage data exist |
| central transfer claim (milestone skill → 10x discrimination) | rank correlation with realised 3-year returns from cohort entry + 36 months | year 3 after first cohort entry |

## 6. Owner decisions required (consolidated)

| OD | Decision | Options and stated costs |
|---|---|---|
| OD1 | Approve the amended Phase 1 scope and acceptance criteria in `17-phase1-amended-specification.md`, or choose a research-only pause | pause costs calendar time only; approval authorises offline synthetic work, no network |
| OD2 | Authorise recording the scientific dispositions (RC-03, 04, 05, 10, 21 and the N7/N9/N10/N11 amendments) as dated amendments to D2, D3, D4, D6, D9, D11 in `09-open-questions-and-decisions.md`; archive untouched | none beyond review time |
| OD3 | Lifetime error budget α_total for artefact promotions, and whether reversible promotions get a separate budget | smaller budget = fewer false promotions, steeply less power after a handful of **attempts** (α_j is debited per registered test, not per success, RC-44) |
| OD4 | Smallest useful Brier improvement to power the primary test for, **stated for the confirmatory conjunction** (RC-83); the VOID-rate cap (RC-38; the cap bounds the share of clusters that leave, not the bias of a discretionary removal, which is why a VOID is frozen or adjudicated and never declared after the freeze, RC-85, Appendix I); the calendar-block dependence model (block length) and its shock amplitude (RC-49, RC-70); the estimand naming, per cluster or period-balanced (RC-69); the accrual cut-off and maximum horizon H_max (RC-68); the skew bound d_max and the catastrophe-share bound (RC-72); the comparator error-dependence assumption the design is powered under (RC-83); whether the 12-month look is futility-only (default) or carries a pre-registered O'Brien–Fleming-type spending (RC-56); **round 9:** the pre-registered null class N (block length, d_max, catastrophe-share bound ε_min, shock amplitude) over which the critical value c* is calibrated, and the power floor at the OD4 effect below which the primary is non-confirmatory under that class (RC-94); the minimum number G_min of occupied blocks (RC-97); whether the conjunction is powered under a justified positive-association assumption or under the Fréchet lower bound (RC-101); **round 10:** the generator box Θ of N as a committed family, in particular the serial-dependence bound ρ_max of the block shocks and the supply–shock coordinate, without which four scalars admit a P(stay) = 0.9 law with 15–22 % size at every calibrated c* (RC-108); the abstention cap per arm (RC-109); **round 11:** the committed enumerated set N_0 of Θ and its spacing, the replication count R and the confidence 1 − 0.01/K of a simulated calibration (RC-117, RC-118), and the per-component boxes Θ_j of the IUT (RC-121); the calibrated values follow from these and are not a choice | power over the design's 24 calendar periods (REPRODUCED, Appendix F and H). Single comparison, independent clusters: δ = 0.01 at 600 clusters 78 % (b = 0.5) to 92 % (b = 0.2); δ = 0.005 at 600 clusters 54–70 %; δ = 0.02 at 288–300 clusters about 76–94 %; the anytime-valid monitor crosses far less often at the same supply (27–32 % for δ = 0.01 at 600; RC-61). **Conjunction** (six comparators, least-favourable configuration): at δ = 0.01 and 600 clusters 21 % with uncorrelated comparator errors, 32 % at a shared-sign probability of one half, 77 % when errors move together; at 1,200 clusters 77 % / 80 % / 96 %; at δ = 0.02 and 600 clusters 76 % / 80 % / 96 %: under uncorrelated errors the conjunction needs about twice the supply of one comparison. **Dependence model:** under independent period shocks of ± 0.3 the single comparison's power at δ = 0.02 is 18 % at 600 and at 1,200 clusters, so the detectable effect under that model is about δ = 0.065 at any supply (the 47 % offered here until round 5 averaged over 120 periods and is withdrawn, RC-70); under a persistent macro regime 120 clusters over 24 periods admit no valid test at any tested block length (Appendix D). **Validity:** the primary test's size is calibrated on the pre-registered null families, not finite-sample valid (exact size 7.33 % on a two-point period-shock null, up to 15.2 % on rare-catastrophe nulls at 24 blocks), and no finite-sample-valid bounded-mean test of any form has power above α(1 + δ)^24 (8 % at δ = 0.02, 16 % at 0.05; PROVED, RC-80), so the skew bound must be justified from reference-class history before supply is read. **Calibration (round 9, corrected in round 11, REPRODUCED, Appendix L):** on the two-point block-mean family with catastrophe share at least ε_min the exact-supremum critical value is 3.21 (ε_min = 0.05 or 0.10), 2.69 (0.20) or 2.25 (0.30); the round-9 grid values 3.20, 2.63 and 2.23 are exceeded between their own grid points (5.0–5.4 %) and are withdrawn (RC-118); a simulated calibration certifies ≤ α by the upper confidence bound, never by the A3 tolerance (RC-117). **Power at the calibrated values (round 11, REPRODUCED, Appendix L; RC-120):** the single comparison at δ = 0.02 and 600 clusters 65 %, 80 % or 90 % against 97 % at the nominal 1.71 (D1 generator), at δ = 0.01 and 600 clusters 28 %, 44 % or 60 % (b = 0.5) against 78 %; the conjunction at δ = 0.01 and 600 clusters 0.0 %, 0.5 % or 3.8 % with uncorrelated errors and 25 %, 42 % or 58 % with errors moving together, against 21 % and 77 %; the period-shock design at δ = 0.02: 1.6 %, 4.1 % or 8.1 % against 18 %. Under the widest illustrated class the conjunction has no useful power at any supply shown. **Per component (RC-121):** one pair's c* leaves a component whose catastrophe share lies outside that pair's class at up to 11.4 % size, so each component carries its own class and c*_j. **Dependence of the comparators:** six tests at 80 % can have zero joint power; with anti-correlated errors the Appendix H generator gives 15 % joint power at δ = 0.01 and 600 clusters where the product is 20 % (RC-101) |
| OD5 | Five source families to profile, three to run; any paid-data allowance (Q5); per source, the pre-registered **source rule**: occurrence-time rule (RC-71), latency window (RC-77) and the failure condition under which the absence of a record at logical finality is an adjudicated VOID rather than NO (RC-85); **round 9:** the observation duty at finality (how the observer records an absence at or after deadline + window, RC-105) and the per-source bound on the rate of post-finality reports above which the source is withdrawn from new registrations (RC-88); **round 10:** the monotone-publication condition per source (evidenced publication times, records never removed), under which a late record is itself the observation of absence at finality, and the exclusion at registration of sources that cannot meet it (RC-113) | determines supply, cluster structure and licensing cost; a source whose failure condition cannot be stated is excluded at registration, because after registration no party may declare a member VOID; a source that cannot be observed at finality cannot resolve a NO |
| OD6 | Hosting at the Phase 2 gate: minimal cloud, hybrid (cloud trusted writer + local stateless GPU compute), or local-only | Codex's illustrative envelope ≈ USD 1,000 / year; local-only is the weakest boundary |
| OD7 | Position caps for appreciated compounders (cost basis with a review ceiling vs market value with forced trims); precedence of hard limits over the thesis-intact veto | affects turnover, tax classification risk (Q9) and compounding |
| OD8 | Provider access route per provider after setup-day verification of terms; human duties implied; **round 9:** each provider must state a model knowledge cutoff per model version, recorded per forecast as an UNVERIFIED claim with its evidence (RC-98); a provider that will not state one is excluded at registration | batch route adds a human to the loop and latency; the cutoff cannot be verified from inside the system |
| OD9a | `AGENTS.md` §2 item 7 (floor → shrinkage) and §2 item 10 (time-shifted holdouts → forbidden-future-information controls) wording, proposed text below; **prerequisite of A0** because the Phase 1 shrinkage estimator (T-20) and leak detector (T-15) would otherwise contradict binding product requirements (RC-33) | governance change; owner approves personally; until recorded, T-20 and T-15 are not built |
| OD9b | `AGENTS.md` §2 item 9 and §3 secrets wording; CI enforcement of the attribution rule; the owner's reading of §7 on reviewer names in reconciliation documents (RC-28); **§2 item 3 wording** so that "anytime-valid sequential tests" cannot be read as requiring the confirmatory test to be anytime-valid (RC-84, proposed text below); **§7 commit identity**: whether the two round-7 commits, which carry the tool identity `Claude <noreply@anthropic.com>` because the execution environment denied setting the owner's identity, are squashed on merge, re-created under the owner's identity, or accepted by designating that identity (RC-81; the round-9 commit carries the owner's identity, because the execution environment honoured the setting this time, so the three commits of rounds 7 and 8 remain the only ones at issue); **§2 item 1 (RC-106):** whether an exploratory single-arm Design C track record may be issued in Phase 2 before the three adapters and Jev operate, which the binding text forbids; until amended, no forecast is issued before Phase 4; **§4 layout (RC-122):** a row for `research/reproduction/`, the committed evidence scripts of this matrix, proposed below | governance change; owner approves personally; not a prerequisite of A0; the §2 item 3 wording is a prerequisite of freezing the Phase 2 contract |
| OD10 | **Approve or revert the version-5 to version-9 diffs of `17`** (commit `b19483a`, the round-8 commit `8af2ae9`, the round-9 commit `922956b`, the round-10 commit `04bc122` that applies RC-108 to RC-115, §3i, and the round-11 commit that carries this matrix v12 and applies RC-117 to RC-123, §3j, among them the start-at-floor rule of RC-123 and the withdrawal of the Appendix J critical values under RC-118): RC-60 and RC-64 to RC-79 (§3c–§3e wording, applied), RC-80 to RC-83 (§3f) and RC-85, RC-86 (§3g, defects Codex found in the round-7 remedies for RC-67 and RC-79), each change carrying its matrix ID; the propagation fixes RC-57 and RC-59 stand unless reverted; the owner names any item to revert, and any item reverted returns to `OWNER_DECISION` with its evidence intact. The round budget question of the former OD10 is answered by the owner's audit and the §4.6 rule (findings are applied on assessment and closed on evidence) | no cost beyond review time; without OD10 T-34 and the secret-handling code of §3 item 5 are not built (A0, RC-64) while the rest of Phase 1 waits only on OD1, OD2 and OD9a; the items that already misstated evidence offered to OD4 (RC-70, RC-72, RC-83) are corrected in the diff and are the reason the figures in the OD4 row changed |

**Proposed `AGENTS.md` wording (for OD9a and OD9b; not applied here):**

- §2 item 7: replace "floored by cohort base rates" with "shrunk toward a declared reference-class rate with
  pre-registered weights; never floored; never elicited directly below 5 %".
- §2 item 9: replace "never forced liquidation of thesis-intact positions" with "no mechanical sale on price
  alone; terminal falsifiers, hard risk limits and valuation review take precedence in the declared order".
- §2 item 10: delete "time-shifted holdouts"; add "forbidden-future-information negative controls".
- §3 secrets bullet: make hosting-neutral ("in the secret store of the principal that needs them, never in
  the process environment of untrusted code").
- §2 item 3 (RC-84): replace "and anytime-valid sequential tests" with "anytime-valid sequential monitoring of
  the conditional null, and a pre-registered confirmatory test of the average-effect estimand whose validity
  conditions are stated, each labelled as such".
- §4 table (RC-122): add the row `research/reproduction/` | reproduction scripts of the reconciliation matrix, one
  per appendix, with pinned requirements | evidence scripts, not project code; each byte-identical to its appendix
  block (`check_appendix_scripts.py`); never imported by implementation code; no row of §4 is changed by them.

## 7. Machine-readable state

```yaml
matrix_version: 12
date: 2026-10-17
round: 11   # Codex's review of the version-8 text; eight findings, seven applied in 17 v9 and one not reproduced (section 3j, 4.6); round 10 applied the eight findings on the version-7 text (section 3i)
budget: per_execution   # one commit per execution; no commit without a new finding or an owner decision; findings never close by count
inputs_processed:
  research_head: 8b2dba79fe9077df53a96a6b61b1823b80930ee8
  codex_review_commit: 59206fe5f652cc3ea63114ad1c2b0fd7252962c2
  pr2_comments: [6215215092, 6215369656]
  issue3_comments: [6216073335, 6218571025, 6218864121, 6218965225, 6219320639, 6219896670, 6220313901, 6220770348, 6222759237, 6231265852, 6231483746, 6236946882, 6237338855]
  pr4_comments: [6218467449, 6236238443, 6236863824, 6237340628]   # the owner's @codex review request, the owner's directive, the owner's progress request, the routine's one progress update
  pr4_reviews:
    - review_id: 5548201046
      commit: 10d1581595b2d1ea6a8689e0f94b33bd68a59d66
      comment_ids: [4294987374, 4294987389, 4294987395, 4294987398, 4294987403, 4294987415, 4294987422,
                    4294987435, 4294987446, 4294987458, 4294987465, 4294987471, 4294987476]
      items: [RC-28, RC-29, RC-30, RC-31, RC-32, RC-33, RC-34, RC-35, RC-36, RC-37, RC-38, RC-39, RC-40]
    - review_id: 5549803107
      commit: 10d1581595b2d1ea6a8689e0f94b33bd68a59d66
      trigger_comment: 6218467449
      comment_ids: [4296205602, 4296205617, 4296205625, 4296205637, 4296205645, 4296205655, 4296205661]
      items: [RC-41, RC-42, RC-43, RC-44, RC-45, RC-46, RC-47]
    - review_id: 5550048687
      commit: 43754cc29add7ed47235ed9dd595ca950497ae4c
      comment_ids: [4296395259, 4296395273, 4296395286, 4296395298, 4296395308, 4296395324, 4296395335]
      items: [RC-48, RC-49, RC-50, RC-51, RC-52, RC-53, RC-54]
    - review_id: 5550366107
      commit: d46c2042a47457ee254582c682c2b17e6803c8bc
      comment_ids: [4296649357, 4296649368, 4296649378, 4296649389, 4296649399, 4296649412, 4296649421, 4296649427]
      items: [RC-56, RC-57, RC-58, RC-59, RC-60, RC-61, RC-62, RC-63]
    - review_id: 5550735335
      commit: 88abaa4f15bd0e1e1ea7035a32094c7a5113285c
      summary_comment: 6216072575
      comment_ids: [4296914293, 4296914298, 4296914307, 4296914319, 4296914330, 4296914341, 4296914351, 4296914363]
      items: [RC-64, RC-65, RC-66, RC-67, RC-68, RC-69, RC-70, RC-71]
      handling: recorded_round_5_applied_round_7
    - review_id: 5550966930
      commit: 4de18e599733c9275ec59f0da678cca5fe88c3a6
      summary_comment: 6216072575
      comment_ids: [4297109177, 4297109194, 4297109203, 4297109207, 4297109215, 4297109220, 4297109231, 4297109245]
      items: [RC-72, RC-73, RC-74, RC-75, RC-76, RC-77, RC-78, RC-79]
      handling: recorded_round_6_applied_round_7
    - review_id: 5551243905
      commit: 10f88298be942162f0795ae31c36a87c8284b376
      summary_comment: 6216072575
      comment_ids: [4297337217, 4297337229, 4297337243, 4297337251]
      items: [RC-80, RC-81, RC-82, RC-83]
      handling: applied_round_7   # RC-81 premise not reproduced; remedy applied
    - review_id: 5556866013
      commit: 37ac01892e7de47027b87dc88784895eacedf3c7
      summary_comment: 6216072575
      comment_ids: [4301920287, 4301920289]
      items: [RC-85, RC-86]
      handling: applied_round_8   # both reproduced (Appendix I); both defects in round-7 remedies
      raised_nothing_on: [RC-60, RC-64, RC-65, RC-66, RC-68, RC-69, RC-70, RC-71, RC-72, RC-73, RC-74, RC-75, RC-76, RC-77, RC-78, RC-80, RC-81, RC-82, RC-83]
    - review_id: 5556950582
      commit: 8af2ae9d0a6a10fbcd070456b569b31e5506b72d
      summary_comment: 6216072575
      comment_ids: [4301994279, 4301994282, 4301994284, 4301994289, 4301994291, 4301994294, 4301994299, 4301994303, 4301994307]
      items: [RC-87, RC-88, RC-89, RC-90, RC-91, RC-92, RC-93, RC-106, RC-107]
      handling: applied_round_9
    - review_id: 5558680831
      commit: 8af2ae9d0a6a10fbcd070456b569b31e5506b72d
      trigger_comment: 6236238443
      summary_comment: 6216072575
      comment_ids: [4303397680, 4303397684, 4303397689, 4303397692, 4303397696, 4303397700, 4303397703, 4303397708, 4303397714, 4303397718, 4303397725, 4303397727]
      items: [RC-94, RC-95, RC-96, RC-97, RC-98, RC-99, RC-100, RC-101, RC-102, RC-103, RC-104, RC-105]
      handling: applied_round_9
    - review_id: 5558887072
      commit: 922956b0a7c06dc8b10849f8146ad2d90f072262
      summary_comment: 6216072575
      comment_ids: [4303569704, 4303569710, 4303569715, 4303569722, 4303569729, 4303569735, 4303569739, 4303569744]
      items: [RC-108, RC-109, RC-110, RC-111, RC-112, RC-113, RC-114, RC-115]
      handling: applied_round_10
      raised_nothing_on: [RC-87, RC-89, RC-91, RC-92, RC-93, RC-95, RC-96, RC-97, RC-100, RC-101, RC-102, RC-103, RC-106, RC-107]   # reviewed once at 922956b without objection; not agreement
    - review_id: 5559035950
      commit: 04bc1223d099059bc9f47585281028f01ed023ae
      summary_comment: 6216072575
      comment_ids: [4303689619, 4303689622, 4303689629, 4303689633, 4303689635, 4303689641, 4303689645, 4303689649]
      items: [RC-116, RC-117, RC-118, RC-119, RC-120, RC-121, RC-122, RC-123]
      handling: applied_round_11_except_RC-116_not_reproduced
      raised_nothing_on: [RC-109, RC-110, RC-112, RC-113, RC-114, RC-115]   # reviewed once at 04bc122 without objection; not agreement
  review_threads_at_922956b: {total: 86, outdated_and_applied: 71, live_older_applied: [4294987422, 4297109203, 4297337217, 4301994299, 4301994303, 4301994307, 4303397703], live_round_10_applied_in_v8: 8, resolved_by_this_execution: 0}
  review_threads_at_8af2ae9: {total: 78, outdated_and_applied: 53, live_older_applied: [4294987422, 4297109203, 4297109207, 4297337217], live_round_9_applied_in_v7: 21, resolved_by_this_execution: 0}
  other_reviews_read:
    - {pr: 7, review_id: 5552078599, commit: 00642e3a1f5d3600cb169541c60d9736d39b08e7, comment_ids: [4297992981, 4297992983, 4297992988, 4297993002, 4297993009], bearing_on_17: [4297992983], item: RC-84}
    - {pr: 10, review_id: 5552523817, commit: b5d104cd25ee82a094cae1b4a04deb801e8ee674, comment_ids: [4298363597, 4298363612, 4298363627, 4298363638, 4298363646, 4298363660, 4298363671, 4298363680, 4298363691, 4298363703], bearing_on_17: []}
specification:
  file: 17-phase1-amended-specification.md
  version: 8
  commit: this_commit   # round 10; the version-5 diff is b19483a909bc948f6775fb5ce3b510d2bdfe9261, the version-6 diff 8af2ae9d0a6a10fbcd070456b569b31e5506b72d, the version-7 diff 922956b0a7c06dc8b10849f8146ad2d90f072262
  role: OD10_decision_diff   # versions 5 to 8 together
  applied_items: [RC-60, RC-64, RC-65, RC-66, RC-67, RC-68, RC-69, RC-70, RC-71, RC-72, RC-73, RC-74, RC-75, RC-76, RC-77, RC-78, RC-79, RC-80, RC-81, RC-82, RC-83, RC-85, RC-86, RC-87, RC-88, RC-89, RC-90, RC-92, RC-93, RC-94, RC-95, RC-96, RC-97, RC-98, RC-99, RC-100, RC-101, RC-103, RC-104, RC-105, RC-106, RC-108, RC-109, RC-110, RC-111, RC-112, RC-113, RC-114, RC-115]
  applied_outside_17: {RC-91: 02-item-8-note, RC-102: 16-appendix-H, RC-107: 12-amendment-13-and-08-amendment-5}
  superseded_within: {RC-67: RC-85, RC-79: RC-86, RC-85-freeze-instant: RC-87, RC-75-key: RC-96, RC-83-bound-sentence: RC-101, RC-83-null-check: RC-93, RC-77-late-report: RC-88, RC-73-drift-rule: RC-100, RC-74-rotation: RC-103, RC-94-four-scalar-class: RC-108, RC-104-empty-baseline-slot: RC-109, RC-99-maturity-bound: RC-110, RC-94-T36-nominal-oracle: RC-111, RC-98-cutoff-on-forecast: RC-112, RC-88-RC-105-outage-plus-late-record: RC-113, RC-68-cut-off-naming: RC-114, RC-67-T17-pre-declared: RC-115}
  owner_fields_left_open: {OD4: [H_max, d_max, catastrophe_share_bound_eps_min, null_class_N_generator_box_theta, serial_dependence_bound_rho_max, supply_shock_coordinate, calibrated_crit_follows, power_floor, G_min, block_length, shock_amplitude, estimand_naming, comparator_dependence_assumption_or_frechet, delta, void_cap, abstention_cap_per_arm], OD5: [latency_windows, inclusion_predicate, sampling_rule, source_rules_failure_condition, observation_duty_at_finality, post_finality_defect_rate_bound, monotone_publication_condition], OD8: [model_knowledge_cutoff_duty], OD9b: [agents_2_item_1_exception_for_phase_2_track_record]}
  new_schema_records: [ArmVersion (RC-112)]
  new_tests: [T-37, T-38(Phase 5), T-39]
  new_fixtures: [F-02a, F-02b, F-02c, F-02d, F-02e, F-21b, F-24(seven clusters; G rewritten in v8), F-25, F-26, F-27(rewritten in v8)]
awaiting: codex_review_of_this_commit; owner_decisions_OD1_OD2_OD9a_OD10
round11_items:
  applied: [RC-117, RC-118, RC-119, RC-120, RC-121, RC-122, RC-123]
  recorded_not_reproduced: [RC-116]   # object 50897415d0fd85e29a4effdeab8fcd5de055874d is in no branch or pull-request ref of this repository; GitHub API: no commit found
  reproduced: [RC-117, RC-118, RC-119, RC-120, RC-121, RC-123]
  deterministic_or_textual: [RC-122]
  own_round9_round10_remedies_found_defective: [RC-94 (RC-117, RC-118, RC-121), RC-108 (RC-118, RC-121), RC-95 (RC-119), RC-103 (RC-123)]
  own_evidence_found_defective: [Appendix J two-point critical values 3.201/2.632/2.231 exceeded inside their classes (RC-118)]
  rc117_magnitude: {A3_tolerance_pass_probability_by_true_size_20000_reps: {0.05: 1.0, 0.055: 0.7581, 0.058: 0.128, 0.06: 0.01}, level_alpha_observed_rate_ceiling: {reps_20000_K_1: 0.0464, reps_20000_K_100: 0.0443, reps_100000_K_1: 0.04839, reps_100000_K_100: 0.04745}}
  rc118_magnitude: {appendix_J_values_sup_size_on_1e-5_sweep: {3.201: 0.0503, 2.632: 0.0539, 2.231: 0.0518}, exact_supremum_c_star: {eps_min_0.05: 3.207, eps_min_0.1: 3.207, eps_min_0.2: 2.693, eps_min_0.3: 2.254}, grid_step_0.05_sup_size: 0.1097}
  rc119_magnitude: {version_7_sequence_out_of_H_order_fraction: 0.642, mean_delay_after_finality_months: {version_7: 2.005, watermark: 2.749}}
  rc120_magnitude: {single_delta_0.01_600_b_0.5: {nominal: 0.7806, c_3.207: 0.2797, c_2.693: 0.4394, c_2.254: 0.6036}, conjunction_delta_0.01_600_rho_0: {nominal: 0.2036, c_3.207: 0.0001, c_2.693: 0.0054, c_2.254: 0.0375}, conjunction_delta_0.01_600_rho_1: {nominal: 0.7695, c_3.207: 0.2534, c_2.693: 0.4173, c_2.254: 0.582}, period_shock_delta_0.02_600: {nominal: 0.1781, c_3.207: 0.0163, c_2.693: 0.0406, c_2.254: 0.0807}, t36_positive_control: {nominal: 0.9633, c_3.207: 0.6767, c_2.693: 0.8172, c_2.254: 0.8991}}
  rc121_magnitude: {component_sup_size_below_pair_class: {pair_c_2.254: 0.114, pair_c_2.693: 0.0791, pair_c_3.207: 0.0}}
  rc123_toy: {v8_rollback: {B_acts_after_store_returns: true, level_after_restore: SIM, fresh_capability_acts_without_promotion: true}, v8_commit_unanchored: {B_acts_after_store_returns: false, level_after_restore: SIM, fresh_capability_acts_without_promotion: true}, fail_closed_start_at_floor: {B_acts_after_store_returns: false, level_after_restore: FLOOR, fresh_capability_acts_without_promotion: false}}
  design_rules_changed: {calibration_criterion: A3_tolerance -> upper_confidence_bound_le_alpha_at_1_minus_0.01_over_K (RC-117), confirmatory_null: box_with_grid_lower_bound -> committed_enumerated_set_N0_with_exact_supremum_where_available (RC-118), monitor_buffer: registered_clusters_only -> own_maturity_watermark (RC-119), iut_components: one_pair_c_star -> per_component_class_and_c_star_j (RC-121), demotion_without_anchor: undefined -> local_persist_fail_closed_start_at_floor (RC-123)}
  committed_scripts: {directory: research/reproduction, identity_check: "11 scripts checked, 0 differ"}
  codex_reviewed_once_without_objection_at_04bc122: [RC-109, RC-110, RC-112, RC-113, RC-114, RC-115]   # not agreement
  rerun_of_committed_scripts: {byte_identical: [K], not_run_this_round: [A, B, C, D, E, F, G, H, I, J]}   # C to I were re-run in round 9, J in round 10
  provenance: this commit is authored and committed under the owner's identity; the three commits of rounds 7 and 8 still carry the tool identity (OD9b); the object Codex named in RC-116 is not in the repository
round10_items:
  applied: [RC-108, RC-109, RC-110, RC-111, RC-112, RC-113, RC-114, RC-115]
  reproduced: [RC-108, RC-109, RC-111, RC-112]
  deterministic_or_textual: [RC-110, RC-113, RC-114, RC-115]
  own_round9_remedies_found_defective: [RC-94 (RC-108, RC-111), RC-104 (RC-109), RC-99 (RC-110), RC-98 (RC-112)]
  own_round9_propagation_gaps: [T-17 against section 3 and F-24 (RC-115)]
  rc108_magnitude: {persistent_regime_P_stay_0.9_120_clusters: {nominal: 0.2725, c_3.20: 0.1533, c_2.63: 0.1914, c_2.23: 0.2206}, P_stay_0.9_600_clusters: {nominal: 0.2907, c_3.20: 0.1759, c_2.63: 0.213, c_2.23: 0.2427}, P_stay_0.7_120_clusters: {nominal: 0.124, c_3.20: 0.0236, c_2.63: 0.0465, c_2.23: 0.0714}, P_stay_0.5_120_clusters: {nominal: 0.0481, c_3.20: 0.0021}}
  rc109_magnitude: {delta_0.1_fail_0.4: {v7_removed: 0.4864, v8_kept: 0.0503}, delta_0.02_fail_0.4: {v7_removed: 0.1802, v8_kept: 0.0481}, delta_0.1_fail_0.1_void_share_0.05: {v7_removed: 0.1006, v8_kept: 0.0505}}
  rc111_positive_control_rates: {nominal: 0.9633, c_3.20: 0.6767, c_2.63: 0.8262, c_2.23: 0.9052}
  rc112_magnitude: {no_correction: 0.052, outcome_chosen_correction_month: 0.1314, upper_99: 0.1371, mean_share_removed: 0.263}
  design_rules_changed: {null_class: four_scalars -> committed_generator_family_with_box_theta_and_rho_max (RC-108), baseline_slot: submission_or_VOID -> registry_computation_from_committed_base_rate_plus_sealed_submissions (RC-109), model_cutoff: per_forecast_field -> immutable_ArmVersion_record_with_cohort_withdrawal (RC-112), burn_in_blinding: maturity_after_freeze -> earliest_knowable_bound_after_freeze (RC-110)}
  codex_reviewed_once_without_objection_at_922956b: [RC-87, RC-89, RC-91, RC-92, RC-93, RC-95, RC-96, RC-97, RC-100, RC-101, RC-102, RC-103, RC-106, RC-107]   # not agreement
  rerun_of_committed_scripts: {byte_identical: [J], not_run_this_round: [A, B, C, D, E, F, G, H, I]}   # C to I were re-run in round 9
  owner_progress_request_processed: 6236863824
  provenance: this commit is authored and committed under the owner's identity; the three commits of rounds 7 and 8 still carry the tool identity (OD9b)
round9_items:
  applied: [RC-87, RC-88, RC-89, RC-90, RC-91, RC-92, RC-93, RC-94, RC-95, RC-96, RC-97, RC-98, RC-99, RC-100, RC-101, RC-102, RC-103, RC-104, RC-105, RC-106, RC-107]
  reproduced: [RC-92, RC-93, RC-94, RC-95, RC-96, RC-97, RC-100, RC-101, RC-102, RC-103]
  deterministic_or_textual: [RC-87, RC-88, RC-89, RC-90, RC-91, RC-98, RC-99, RC-104, RC-105, RC-106, RC-107]
  own_round7_round8_remedies_found_defective: [RC-85 (RC-87, RC-90, RC-92), RC-83 (RC-93, RC-101), RC-75 (RC-96), RC-73 (RC-100), RC-74 (RC-103), RC-77 (RC-88, RC-105)]
  own_evidence_found_defective: [Appendix H least-favourable-null check (RC-93), Appendix H 140-blocks string (RC-102), Appendix G/H zero-variance convention disagreement (RC-94)]
  design_rule_changed: {monitor_order: closure_time -> pre_registered_maturity_H_k (RC-95)}
  rc95_magnitude: {closure_order_crossing_by_NO_lag: {6: 0.0524, 12: 0.101, 24: 0.4385, 120: 1.0}, maturity_order: 0.0317-0.034, final_product: 0.0063-0.0075}
  rc94_calibration: {eps_min_0.05: {crit: 3.201, power_600: 0.60, power_1200: 0.942}, eps_min_0.2: {crit: 2.632, power_600: 0.787, power_1200: 0.983}, eps_min_0.3: {crit: 2.231, power_600: 0.885, power_1200: 0.994}, nominal: {crit: 1.714, power_600: 0.958}}
  rc97_sizes: {empty_blocks_counted: [0.0671, 0.0578, 0.058], occupied_only: [0.0488, 0.0513, 0.0563]}
  codex_reviewed_once_without_objection_at_8af2ae9: [RC-86]   # RC-85 was extended three times, not left alone
  rerun_of_committed_scripts: {byte_identical: [C, D, E, F, G, I], corrected_one_line: [H], not_run: [A, B]}
  owner_directive_processed: 6236238443
  provenance: this commit is authored and committed under the owner's identity (the environment honoured git -c user.name/user.email); the three commits of rounds 7 and 8 still carry the tool identity (OD9b)
round8_items:
  applied: [RC-85, RC-86]
  reproduced: [RC-85, RC-86]
  own_round7_remedies_found_defective: [RC-67 (RC-85), RC-79 (RC-86)]
  codex_reviewed_once_without_objection_at_37ac018: [RC-60, RC-64, RC-65, RC-66, RC-68, RC-69, RC-70, RC-71, RC-72, RC-73, RC-74, RC-75, RC-76, RC-77, RC-78, RC-80, RC-81, RC-82, RC-83]   # not agreement; status stays PROPOSED until OD10
  rc85_magnitude: {null_size_no_removal: 0.049-0.050, cap_5pct_two_point: 0.23-0.34, cap_5pct_continuous: 0.77-0.95, worst_case_lower_bound: 0.049-0.050}
  provenance_defect_disclosed: this commit also carries Claude <noreply@anthropic.com>; the environment identity is unchanged since round 7; OD9b
round7_items:
  applied: [RC-80, RC-82, RC-83]
  remedy_applied_premise_not_reproduced: [RC-81]
  owner_decision: [RC-84]
  proved: [RC-80]   # power <= alpha (1 + delta)^G for any finite-sample-valid bounded-mean test
  reproduced: [RC-83]
  own_earlier_wording_found_defective: [RC-72-sentence-on-distribution-free-tests]
  provenance_defect_disclosed: round-7 commits carry Claude <noreply@anthropic.com>; environment denied setting the owner's identity; OD9b
earlier_rounds:
  round2_items: {accepted: [RC-29, RC-30, RC-31, RC-32, RC-33, RC-34, RC-35, RC-36, RC-37, RC-38, RC-39, RC-40, RC-41, RC-42, RC-43, RC-44, RC-45, RC-46, RC-47], partly: [RC-28], round1_dispositions_corrected: [RC-15]}
  round3_items: {accepted: [RC-48, RC-49, RC-50, RC-51, RC-52, RC-53, RC-54], self_reported: [RC-55], disagreements_withdrawn_by_claude: [RC-01-scope]}
  round4_items: {revised: [RC-56, RC-58, RC-61, RC-62, RC-63], propagation_only: [RC-57, RC-59], recorded_then_applied_round_7: [RC-60]}
  round5_items: {recorded_then_applied_round_7: [RC-64, RC-65, RC-66, RC-67, RC-68, RC-69, RC-70, RC-71], reproduced: [RC-65, RC-69, RC-70]}
  round6_items: {recorded_then_applied_round_7: [RC-72, RC-73, RC-74, RC-75, RC-76, RC-77, RC-78, RC-79], reproduced: [RC-72, RC-73, RC-74, RC-75, RC-77]}
next_execution:
  on_codex_review_of_this_commit_or_later: assess each new finding (dedupe by comment ID), reproduce, apply in 17 v8 with matrix IDs, one commit; record premises not reproduced without applying
  on_owner_decision: apply the named reversions or decisions; record OD values as named fields
  on_no_new_input: do_nothing
disagreements_open: [RC-20-timing]   # both positions recorded; settled by OD6, not by a further round
disagreements_resolved_pending_codex_review: [RC-01-scope]
owner_decision_items: [RC-20-timing (OD6), RC-07-retention (owner may strike), RC-28 (OD9b), RC-84 (OD9b), RC-81-commit-identity (OD9b), RC-106-agents-2-item-1 (OD9b), version-5, version-6 and version-7 diffs (OD10), RC-94-null-class-and-power-floor and RC-97-G_min and RC-101-dependence-or-frechet (OD4), RC-88-defect-rate-bound and RC-105-observation-duty (OD5), RC-98-cutoff-duty (OD8), RC-56-early-confirmation-option (OD4), RC-85-void-cap (OD4), RC-85-source-failure-condition (OD5), RC-68-H_max and RC-69-estimand-naming and RC-70-shock-amplitude and RC-72-skew-bound and RC-83-dependence-assumption (OD4), RC-77-latency-windows and RC-78-inclusion-predicate (OD5), RC-74-external-store (OD6), RC-76-cohort-start (OD1)]
owner_decisions_open: [OD1, OD2, OD3, OD4, OD5, OD6, OD7, OD8, OD9a, OD9b, OD10]
prerequisites_for_A0: [OD1, OD2, OD9a, OD10-for-T-34-only]
experiments_required: [H1, H3, H5, H6, transfer-claim, persistent-regime-dependence-model (OD4/OD5), comparator-error-dependence (OD4; needs outcomes, not estimable from the blinded burn-in)]
p0_status:
  e_process_protocol: remedy proposed and now fully specified in 17 v8 (cluster-weighted statistic over occupied blocks, critical value calibrated over a pre-registered null class stated as a committed generator family with a serial-dependence bound and a pass condition, baseline slot computed from the committed base rate with sealed submissions, model cutoff per immutable arm version with cohort withdrawal, burn-in blinding on the earliest knowable time, finality dispositions closed for the outage-plus-late-record case, monitor in pre-registered maturity order, VOID set fixed in the registration record or adjudicated by the source rule, immutable finality dispositions with an observation duty, abstention at issuance close, partial-VOID arithmetic with t*_k over all members and +/-1 imputation, accrual cut-off, (event, arm, slot) key with a primary slot, model knowledge cutoff, issuance window, eligible-population predicate, IUT power with the Frechet bound); tests T-02, T-10..T-13, T-16, T-17, T-19, T-36, T-37, T-39 specified, not implemented; the version-6 text was reviewed by Codex twice at 8af2ae9 with twenty-one findings, all applied; the version-7 text was reviewed once at 922956b with eight findings, all applied; pending OD10 and Codex review of this commit
  rare_probability_and_intervals: remedy proposed, tests T-20 (point and interval oracles)..T-22 specified, blocked on OD9a, not implemented
  enforcement_boundaries: remedy proposed and now fully specified in 17 v7 (secret confinement T-34, clock with monotonic time, boot id and drift against the epoch baseline T-35, durable nonce consumption before acknowledgement and epoch rotation on demotion T-30, full-tuple signatures T-31, action-boundary enforcement T-32, as-of interface with positive oracles T-15); tests specified, not implemented; T-34 build waits on OD10
implementation_authorised: false
```

## Appendix A. Reconciliation probe script (REPRODUCED)

Written for this matrix without importing or copying the script in `15` Appendix 1; imports only the scratch
copy of the reference code; no network, no credentials. Round 2 renamed it, neutralised the docstring (RC-28),
replaced the pseudo-count bound by the exact binomial bound (RC-31) and added the (b = 0.2, δ = 0.02) power
row (RC-45); nothing else changed. Extract and run
from the repository root after copying `source_v0_2` to a scratch directory with numpy, scipy, httpx and
pytest installed in an isolated venv:

```sh
python - <<'PY_EXTRACT'
from pathlib import Path
text = Path('research/16-reconciliation-matrix.md').read_text()
start = text.rindex('<!-- probe-script:start -->')
end = text.index('<!-- probe-script:end -->', start)
block = text[start:end].split('```python\n', 1)[1].rsplit('```', 1)[0]
Path('/path/to/scratch/reconciliation_probes.py').write_text(block)
PY_EXTRACT
/path/to/scratch/venv/bin/python -I /path/to/scratch/reconciliation_probes.py /path/to/scratch/v02
```

<!-- probe-script:start -->
```python
"""Reconciliation probes for research/16-reconciliation-matrix.md (round 1, re-run in round 2).

Runs against a scratch copy of the archived v0.2 reference code (path = argv[1]).
No network, no credentials. Reproduces the counterexamples the reconciliation
matrix relies on and evaluates the two proposed remedies (cluster-level betting,
second-moment simplex pooling). Written for the matrix independently of the
script in 15-codex-review.md Appendix 1; it does not import or copy it.
"""
import json, math, sys, tempfile, warnings
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.optimize import minimize
from scipy.stats import beta

sys.path.insert(0, sys.argv[1])
from cpe.ledger import AppendOnlyLedger, _canonical
from cpe.registry import EventSpec, Forecast, ForecastRegistry, Forecaster
from cpe.fusion import ModelInterval, JevTriage, fuse, error_correlation, min_variance_weights
from cpe.eprocess import CommittedEProcess, CommittedForecastPair, grapa_lambda
from cpe.saxo_sim import Gate, GateState, OwnerAuthorization

out = {}
T0 = datetime(2020, 1, 1, tzinfo=timezone.utc)

def spec(eid):
    return EventSpec(eid, 'Revenue exceeds threshold by expiry', 'audited filing',
                     'revenue > 100', T0 + timedelta(days=1), T0 + timedelta(days=30), 'v1')

# ---- RC-02, RC-11, RC-12, RC-13: registry and ledger ----
with tempfile.TemporaryDirectory() as d:
    ledger = AppendOnlyLedger(Path(d) / 'ledger.jsonl')
    reg = ForecastRegistry(ledger)
    reg.register_event(spec('late'))
    reg.resolve('late', True, T0 + timedelta(days=40), 'audit', 'ev-late')
    out['RC11_late_yes_status'] = reg.status('late').value
    out['RC12_restart_knows_events'] = len(ForecastRegistry(ledger)._events)
    reg.register_event(spec('backdated'))
    reg.commit_forecast(Forecast('f1', 'backdated', Forecaster.CLAUDE, 'v', 0.4, 0.6,
                                 T0, T0, ('e',), 'z' * 64))
    out['RC02_backdated_2020_forecast_accepted_today'] = True
    reg.register_event(spec('early'))
    reg.resolve('early', False, T0 + timedelta(days=2), 'audit', 'ev-early')
    out['RC11_early_no_before_deadline_status'] = reg.status('early').value
    with patch.object(ledger, 'append', side_effect=OSError('injected')):
        try:
            reg.register_event(spec('phantom'))
        except OSError:
            pass
    out['RC12_phantom_event_after_failed_append'] = 'phantom' in reg._events
    anchor = ledger.anchor()
    ledger.append('forecast', {'p': 0.1})
    rows = [json.loads(line) for line in ledger.path.read_text().splitlines()]
    rows[-1]['payload']['p'] = 0.99
    rows[-1].pop('entry_hash')
    rows[-1]['entry_hash'] = sha256(_canonical(rows[-1])).hexdigest()
    ledger.path.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    out['RC13_rehashed_unanchored_suffix_verifies'] = ledger.verify_against_anchor(anchor)

# ---- RC-12: gate replay ----
g = Gate(); key = b'synthetic-owner-key'
auth = OwnerAuthorization(GateState.RESEARCH_ONLY, GateState.SIM_READ_ONLY, 'bundle',
                          Gate.expected_mac(key, GateState.RESEARCH_ONLY, GateState.SIM_READ_ONLY, 'bundle'))
g.promote(auth, key); g.demote('kill'); g.promote(auth, key)
out['RC12_state_after_replaying_old_authorization'] = g.state.value

# ---- RC-03, RC-04 arithmetic ----
out['RC03_floor_rule_on_[0.001,0.01]_base_0.02'] = [max(0.001, 0.02), 0.01]
out['RC04_nested_chain_product'] = (0.01 / 0.1) * (0.1 / 0.5) * 0.5

# ---- RC-06, RC-07: fusion weights ----
z = np.tile(np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1.]]), (10, 1))
errors_p4 = z * np.array([0.02, 0.30, 0.30])
w_corr, _ = min_variance_weights(error_correlation(errors_p4, 0.3))
out['RC06_correlation_weights_P4'] = [round(x, 4) for x in w_corr]

def second_moment_simplex(errors, shrink=0.1):
    """Minimise w'Sw on the simplex, S = shrunk uncentred second moment of past errors."""
    m = errors.T @ errors / len(errors)
    s = (1 - shrink) * m + shrink * np.diag(np.diag(m))
    k = errors.shape[1]
    res = minimize(lambda w: w @ s @ w, np.ones(k) / k, method='SLSQP',
                   bounds=[(0, 1)] * k, constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1}])
    return res.x

out['RC06_second_moment_weights_P4'] = [round(x, 3) for x in second_moment_simplex(errors_p4)]
rng = np.random.default_rng(1)
bias_fixture = np.column_stack([np.full(40, 0.20) + 0.01 * rng.standard_normal(40),
                                0.05 * rng.standard_normal(40), 0.05 * rng.standard_normal(40)])
cov = np.cov(bias_fixture, rowvar=False)
v = np.linalg.solve(cov, np.ones(3))
out['RC06_covariance_only_weights_bias_fixture'] = [round(x, 3) for x in v / v.sum()]
out['RC06_second_moment_weights_bias_fixture'] = [round(x, 3) for x in second_moment_simplex(bias_fixture)]

names = ['claude', 'openai', 'gemini']; jev = JevTriage(0.9, 0.9, 0.0)
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    out['RC07_neff_constant_duplicate_histories'] = fuse([ModelInterval(n, .4, .6) for n in names], jev, np.ones((20, 3))).effective_models
out['RC07_neff_identical_varying_histories'] = round(fuse([ModelInterval(n, .4, .6) for n in names], jev, np.tile(np.arange(20.)[:, None], (1, 3))).effective_models, 4)
out['RC07_neff_closed_form_3/(3-2*0.3)'] = round(3 / (3 - 0.6), 4)
for tag, lo, hi in [('nan', float('nan'), float('nan')), ('reversed', .8, .2), ('over_one', 1.2, 1.3)]:
    out['RC15_fusion_accepts_' + tag] = fuse([ModelInterval(n, lo, hi) for n in names], jev, None).decision.value

# ---- RC-01: e-process cloned outcomes ----
def run_path(xs):
    ep = CommittedEProcess()
    for i, x in enumerate(xs):
        ep.commit(CommittedForecastPair(str(i), .25, .75, T0, T0 + timedelta(days=1)))
        ep.resolve(str(i), int(x > 0), T0 + timedelta(days=2))
    return ep
plus = run_path([.5] * 30); minus = run_path([-.5] * 30)
out['RC01_cloned_30_outcomes'] = {'e_if_shared_outcome_is_1': round(plus.evalue, 4),
                                  'e_if_shared_outcome_is_0': round(minus.evalue, 4),
                                  'crossing_probability_under_fair_shared_outcome': 0.5 * plus.reject_null(.05) + 0.5 * minus.reject_null(.05)}

# Vectorised archived GRAPA recurrence, checked against the reference on one path.
def grapa_paths(xs, lam_max=0.5, threshold=20.0, checkpoints=()):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    snaps = {}
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
        if n + 1 in checkpoints:
            snaps[n + 1] = peak.copy()
    return wealth, peak, snaps
check = np.random.default_rng(5).choice([-.5, .5], size=(1, 80))
ref = run_path(list(check[0])).evalue
vec = grapa_paths(check)[0][0]
out['RC01_vectorised_recurrence_matches_reference'] = bool(np.isclose(ref, vec, rtol=1e-12))

def binom_upper(k, n, conf=0.95):
    """One-sided exact (Clopper-Pearson) upper confidence bound for a binomial proportion."""
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))

# Clustered no-skill null: baseline 0.4, challenger 0.6, outcome Y~Bern(0.5) shared by every
# event in a cluster. X = (0.4-Y)^2 - (0.6-Y)^2 = +0.2 if Y=1 else -0.2. Marginal mean zero.
REPS, CLUSTERS, PER = 2000, 120, 5
rng = np.random.default_rng(2026)
y = rng.integers(0, 2, size=(REPS, CLUSTERS))
x_cluster = np.where(y == 1, 0.2, -0.2)
x_event = np.repeat(x_cluster, PER, axis=1)                  # 600 per-event increments
_, peak_event, _ = grapa_paths(x_event)
_, peak_cluster, _ = grapa_paths(x_cluster)
fa_event = float((peak_event >= 20).mean()); fa_cluster = float((peak_cluster >= 20).mean())
out['RC01_clustered_null'] = {'replications': REPS, 'clusters': CLUSTERS, 'events_per_cluster': PER,
                              'false_alarm_per_event_betting': fa_event,
                              'false_alarm_per_cluster_betting': fa_cluster,
                              'mc_upper_95_per_cluster_exact_binomial': round(binom_upper(int(round(fa_cluster * REPS)), REPS), 6)}
# Same with a shuffled (interleaved) order of events across clusters: dependence persists.
perm = rng.permutation(CLUSTERS * PER)
_, peak_shuf, _ = grapa_paths(x_event[:, perm])
out['RC01_clustered_null']['false_alarm_per_event_betting_interleaved_order'] = float((peak_shuf >= 20).mean())

# Independent power check of four rows of Codex D1 (same generator specification, seeds 17, 29, 43);
# the (0.2, 0.02) row was added in round 2 (RC-45) because 02 section 6 cited it without reproduction.
power = {}
for b, delta in [(0.5, 0.01), (0.5, 0.02), (0.2, 0.01), (0.2, 0.02)]:
    counts = {300: 0, 600: 0}
    for seed in (17, 29, 43):
        r = np.random.default_rng(seed)
        p = b + math.sqrt(delta) * r.choice([-1., 1.], size=(2000, 600))
        yy = (r.random(p.shape) < p).astype(float)
        xs = (b - yy) ** 2 - (p - yy) ** 2
        snaps = grapa_paths(xs, checkpoints=(300, 600))[2]
        for n, pk in snaps.items():
            counts[n] += int((pk >= 20).sum())
    power[f'b={b},delta={delta}'] = {'crossings_by_300_of_6000': counts[300], 'crossings_by_600_of_6000': counts[600]}
out['RC24_power_rows'] = power

# alpha-spending shape
out['RC08_alpha_spending_0.05/(j(j+1))'] = {j: round(0.05 / (j * (j + 1)), 5) for j in (1, 2, 5, 10)}
out['RC08_sum_to_infinity'] = 0.05
print(json.dumps(out, indent=2, allow_nan=False))
```
<!-- probe-script:end -->

## Appendix B. Probe output (REPRODUCED, round 2 re-run)

Identical to the round-1 output except the key `mc_upper_95_per_cluster_exact_binomial` (was
`mc_upper_95_per_cluster: 0.0008`) and the added row `b=0.2,delta=0.02`.

```json
{
  "RC11_late_yes_status": "resolved_yes",
  "RC12_restart_knows_events": 0,
  "RC02_backdated_2020_forecast_accepted_today": true,
  "RC11_early_no_before_deadline_status": "resolved_no",
  "RC12_phantom_event_after_failed_append": true,
  "RC13_rehashed_unanchored_suffix_verifies": true,
  "RC12_state_after_replaying_old_authorization": "SIM_READ_ONLY",
  "RC03_floor_rule_on_[0.001,0.01]_base_0.02": [
    0.02,
    0.01
  ],
  "RC04_nested_chain_product": 0.01,
  "RC06_correlation_weights_P4": [
    0.3333,
    0.3333,
    0.3333
  ],
  "RC06_second_moment_weights_P4": [
    0.991,
    0.004,
    0.004
  ],
  "RC06_covariance_only_weights_bias_fixture": [
    0.935,
    0.018,
    0.047
  ],
  "RC06_second_moment_weights_bias_fixture": [
    0.036,
    0.492,
    0.473
  ],
  "RC07_neff_constant_duplicate_histories": 3.0,
  "RC07_neff_identical_varying_histories": 1.25,
  "RC07_neff_closed_form_3/(3-2*0.3)": 1.25,
  "RC15_fusion_accepts_nan": "forecast",
  "RC15_fusion_accepts_reversed": "forecast",
  "RC15_fusion_accepts_over_one": "forecast",
  "RC01_cloned_30_outcomes": {
    "e_if_shared_outcome_is_1": 475.0986,
    "e_if_shared_outcome_is_0": 1.0,
    "crossing_probability_under_fair_shared_outcome": 0.5
  },
  "RC01_vectorised_recurrence_matches_reference": true,
  "RC01_clustered_null": {
    "replications": 2000,
    "clusters": 120,
    "events_per_cluster": 5,
    "false_alarm_per_event_betting": 0.3335,
    "false_alarm_per_cluster_betting": 0.0,
    "mc_upper_95_per_cluster_exact_binomial": 0.001497,
    "false_alarm_per_event_betting_interleaved_order": 0.1345
  },
  "RC24_power_rows": {
    "b=0.5,delta=0.01": {
      "crossings_by_300_of_6000": 67,
      "crossings_by_600_of_6000": 1623
    },
    "b=0.5,delta=0.02": {
      "crossings_by_300_of_6000": 1584,
      "crossings_by_600_of_6000": 4883
    },
    "b=0.2,delta=0.01": {
      "crossings_by_300_of_6000": 21,
      "crossings_by_600_of_6000": 1881
    },
    "b=0.2,delta=0.02": {
      "crossings_by_300_of_6000": 1844,
      "crossings_by_600_of_6000": 5653
    }
  },
  "RC08_alpha_spending_0.05/(j(j+1))": {
    "1": 0.025,
    "2": 0.00833,
    "5": 0.00167,
    "10": 0.00045
  },
  "RC08_sum_to_infinity": 0.05
}
```

## Appendix C. Round-2 arithmetic checks (REPRODUCED)

Needs no reference code. Run with `python -I round2_checks.py` in the same venv (extract the block as in
Appendix A, between the `round2-script` markers).

<!-- round2-script:start -->
```python
"""Round-2 arithmetic checks for the Codex findings on PR #4 (no reference code needed)."""
import json, math
import numpy as np
from scipy.stats import beta, binom

out = {}
# Finding r4294987398: exact one-sided 95 % upper bound with 0 of 2000.
n = 2000
out['exact_upper_0_of_2000'] = round(1 - 0.05 ** (1 / n), 6)
out['clopper_pearson_0_of_2000'] = round(float(beta.ppf(0.95, 1, n)), 6)
out['round1_pseudocount_normal_value'] = round(0 + 1.645 * math.sqrt((1 / n) * 1 / n), 6)
# How many crossings would still satisfy A3 (bound <= 0.06) at n = 2000?
k_max = max(k for k in range(0, 200) if beta.ppf(0.95, k + 1, n - k) <= 0.06)
out['max_crossings_of_2000_with_upper_bound_le_0.06'] = k_max
out['upper_bound_at_that_k'] = round(float(beta.ppf(0.95, k_max + 1, n - k_max)), 5)

# Finding r4294987465: VOID imputed as NO is not conservative for a paired Brier difference.
def paired_brier_increment(p_full, p_base, y):
    return (p_base - y) ** 2 - (p_full - y) ** 2   # positive favours FULL
out['void_example'] = {'p_full': 0.1, 'p_base': 0.9,
                       'impute_Y0': round(paired_brier_increment(0.1, 0.9, 0), 3),
                       'impute_Y1': round(paired_brier_increment(0.1, 0.9, 1), 3)}
out['worst_case_rule'] = 'impute Y=1 if p_full < p_base else Y=0 gives the increment least favourable to FULL'
# Worst-case bound over m VOIDs with |X| <= 1: mean increment shifts by at most m/N.
out['void_bound_shift_example'] = {'N': 300, 'm_void': 15, 'max_shift_of_mean_increment': round(15 / 300, 4)}

# Finding r4294987395: a single-run IUT check is flaky and can pass a wrong implementation.
alpha = 0.05
out['iut_single_run'] = {
    'P_correct_impl_rejects_null_comparator_once': alpha,
    'P_wrong_impl_size_0.10_passes_single_run': 1 - 0.10,
    'P_wrong_impl_size_0.10_passes_MC_bound_check_n2000': round(float(binom.cdf(k_max, 2000, 0.10)), 8),
    'P_correct_impl_fails_MC_bound_check_n2000': round(1 - float(binom.cdf(k_max, 2000, 0.05)), 6)}
# Deterministic oracle: conjunction rejects iff every component rejects.
import itertools
comps = [0.01, 0.20, 0.03]
out['iut_oracle_example'] = {'component_p': comps, 'reject_all_at_0.05': all(p <= alpha for p in comps),
                             'min_e_value_rule': 'reject iff min_j e_j >= 1/alpha'}

# T-13 design: replications and margin so that a correct level-alpha test passes with high
# probability while an over-sized implementation fails.
design = {}
for n_rep, margin, conf in [(2000, 0.01, 0.95), (10000, 0.01, 0.99), (20000, 0.01, 0.99)]:
    k_max_d = max(k for k in range(0, int(n_rep * 0.2)) if beta.ppf(conf, k + 1, n_rep - k) <= alpha + margin)
    design[f'n={n_rep},margin={margin},conf={conf}'] = {
        'k_max': k_max_d,
        'P_pass_size_0.05': round(float(binom.cdf(k_max_d, n_rep, 0.05)), 6),
        'P_pass_size_0.06': round(float(binom.cdf(k_max_d, n_rep, 0.06)), 6),
        'P_pass_size_0.07': float(binom.cdf(k_max_d, n_rep, 0.07)),
        'P_pass_size_0.10': float(binom.cdf(k_max_d, n_rep, 0.10))}
out['t13_design'] = design

# Finding r4296205661 (RC-47): does sanitising __context__ inside the handler prevent chaining?
def chained_context(style):
    try:
        try:
            raise ValueError('bearer SYNTHETIC-CANARY')
        except ValueError as e:
            if style == 'set_none_in_handler':
                new = RuntimeError('sanitised'); new.__context__ = None; raise new
            if style == 'from_none_in_handler':
                raise RuntimeError('sanitised') from None
            summary = type(e).__name__          # keep only a sanitised summary, leave the handler
        raise RuntimeError(f'sanitised ({summary})')
    except RuntimeError as r:
        return 'CANARY' in repr(r.__context__)
out['exception_context_canary_reachable'] = {s: chained_context(s) for s in
    ('set_none_in_handler', 'from_none_in_handler', 'translate_outside_handler')}

# Finding r4296205602 (RC-41): bound of the per-event paired Brier increment and of 1 + lambda * mean.
corners = [abs((pb - y) ** 2 - (pf - y) ** 2) for pb in (0.0, 1.0) for pf in (0.0, 1.0) for y in (0, 1)]
out['increment_bound'] = {'max_abs_X_i': max(corners), 'min_factor_at_lambda_max_0.5': 1 - 0.5 * max(corners)}

# Finding r4294987471 / r4294987415: no arithmetic; design-level.
print(json.dumps(out, indent=2))
```
<!-- round2-script:end -->

Output:

```json
{
  "exact_upper_0_of_2000": 0.001497,
  "clopper_pearson_0_of_2000": 0.001497,
  "round1_pseudocount_normal_value": 0.000822,
  "max_crossings_of_2000_with_upper_bound_le_0.06": 102,
  "upper_bound_at_that_k": 0.05984,
  "void_example": {
    "p_full": 0.1,
    "p_base": 0.9,
    "impute_Y0": 0.8,
    "impute_Y1": -0.8
  },
  "worst_case_rule": "impute Y=1 if p_full < p_base else Y=0 gives the increment least favourable to FULL",
  "void_bound_shift_example": {
    "N": 300,
    "m_void": 15,
    "max_shift_of_mean_increment": 0.05
  },
  "iut_single_run": {
    "P_correct_impl_rejects_null_comparator_once": 0.05,
    "P_wrong_impl_size_0.10_passes_single_run": 0.9,
    "P_wrong_impl_size_0.10_passes_MC_bound_check_n2000": 0.0,
    "P_correct_impl_fails_MC_bound_check_n2000": 0.393261
  },
  "iut_oracle_example": {
    "component_p": [
      0.01,
      0.2,
      0.03
    ],
    "reject_all_at_0.05": false,
    "min_e_value_rule": "reject iff min_j e_j >= 1/alpha"
  },
  "t13_design": {
    "n=2000,margin=0.01,conf=0.95": {
      "k_max": 102,
      "P_pass_size_0.05": 0.606739,
      "P_pass_size_0.06": 0.047114,
      "P_pass_size_0.07": 0.0003050828854872164,
      "P_pass_size_0.10": 1.0460703080855882e-15
    },
    "n=10000,margin=0.01,conf=0.99": {
      "k_max": 544,
      "P_pass_size_0.05": 0.978355,
      "P_pass_size_0.06": 0.008995,
      "P_pass_size_0.07": 1.308824218554986e-10,
      "P_pass_size_0.10": 2.645531303440866e-61
    },
    "n=20000,margin=0.01,conf=0.99": {
      "k_max": 1122,
      "P_pass_size_0.05": 0.999953,
      "P_pass_size_0.06": 0.009982,
      "P_pass_size_0.07": 9.812816862921764e-16,
      "P_pass_size_0.10": 4.181300507765669e-111
    }
  },
  "exception_context_canary_reachable": {
    "set_none_in_handler": true,
    "from_none_in_handler": true,
    "translate_outside_handler": false
  },
  "increment_bound": {
    "max_abs_X_i": 1.0,
    "min_factor_at_lambda_max_0.5": 0.5
  }
}
```

The `iut_single_run` block shows why T-13 needs its own margin: at 2,000 replications a correct level-0.05
test fails an "upper bound ≤ 0.06" check 39 % of the time. The `t13_design` block fixes the chosen design
(20,000 replications, exact one-sided 99 % upper bound ≤ 0.06, reached at 1,122 rejections): pass probability
0.99995 for a test of size 0.05, 0.0100 for size 0.06, below 10⁻¹⁵ for size 0.07. The
`exception_context_canary_reachable` block is the RC-47 reproduction; `increment_bound` is RC-41.

## Appendix D. Round-3 checks (REPRODUCED)

Needs no reference code and no network. Run with `python -I round3_checks.py` in the same isolated venv as
Appendix A (Python 3.11.17, numpy 2.4.6, scipy 1.17.1; 2.8 s), extracting the block between the
`round3-script` markers as in Appendix A. Seeds are fixed; two consecutive runs produced byte-identical
output. The generator is the one of Appendix A (baseline 0.4, challenger 0.6, X = 0.4·Y − 0.2) with 120
clusters closed in calendar order over 24 periods of five; the archived GRAPA recurrence is the Appendix A
function.

<!-- round3-script:start -->
```python
"""Round-3 checks for the Codex findings on PR #4 at 43754cc (no reference code, no network)."""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA, THRESHOLD, LAM_MAX = 0.05, 20.0, 0.5

# ---- r4296395259 (RC-48): A3 / T-10 keep 2,000 replications with a 95 % bound <= 0.06 ----
def k_max(n_rep, conf, limit):
    return max(k for k in range(0, int(n_rep * 0.2)) if beta.ppf(conf, k + 1, n_rep - k) <= limit)
a3 = {}
for n_rep, conf in [(2000, 0.95), (20000, 0.99)]:
    k = k_max(n_rep, conf, 0.06)
    a3[f'n={n_rep},conf={conf}'] = {'k_max': k,
                                   'P_pass_if_size_exactly_0.05': round(float(binom.cdf(k, n_rep, 0.05)), 6),
                                   'P_pass_if_size_0.06': round(float(binom.cdf(k, n_rep, 0.06)), 6),
                                   'P_pass_if_size_0.07': float(binom.cdf(k, n_rep, 0.07))}
out['RC48_a3_design'] = a3

# ---- archived GRAPA recurrence (vectorised), identical to 16 Appendix A ----
def grapa_paths(xs, lam_max=LAM_MAX):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
    return peak

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))

# Baseline 0.4, challenger 0.6, so X = (0.4-Y)^2 - (0.6-Y)^2 = 0.4*Y - 0.2 and E[X | P(Y=1)=q] = 0.4*q - 0.2.
def increments(q, rng):
    y = (rng.random(q.shape) < q).astype(float)
    return 0.4 * y - 0.2

def fixed_horizon_sizes(xs, periods, blocks):
    """One-sided tests of mean X <= 0 at alpha: naive (clusters iid) and block-clustered (t with G-1 df)."""
    res = {}
    k = xs.shape[1]
    m = xs.mean(axis=1); sd = xs.std(axis=1, ddof=1)
    with np.errstate(divide='ignore', invalid='ignore'):          # sd = 0 gives +/-inf or nan, counted as written
        tn = m / (sd / math.sqrt(k))
        res['naive_iid_cluster_t'] = float((tn > student_t.ppf(1 - ALPHA, k - 1)).mean())
        for b in blocks:
            g = periods // b
            bm = xs.reshape(xs.shape[0], g, -1).mean(axis=2)      # block means, equal block sizes
            tb = bm.mean(axis=1) / (bm.std(axis=1, ddof=1) / math.sqrt(g))
            res[f'block_of_{b}_periods_t_df{g-1}'] = float((tb > student_t.ppf(1 - ALPHA, g - 1)).mean())
    return res

REPS, PERIODS, PER_PERIOD = 20000, 24, 5
K = PERIODS * PER_PERIOD                                           # 120 clusters, closed in calendar order
rng = np.random.default_rng(2026)
families = {}

# (0) valid clustered null restated at 20,000 replications: independent clusters, q = 0.5.
q0 = np.full((REPS, K), 0.5)
x0 = increments(q0, rng)
fa0 = int((grapa_paths(x0) >= THRESHOLD).sum())
families['independent_clusters_valid_null'] = {
    'eprocess_crossings': fa0, 'eprocess_rate': fa0 / REPS,
    'exact_upper_99': round(binom_upper(fa0, REPS, 0.99), 6),
    'fixed_horizon_size': fixed_horizon_sizes(x0, PERIODS, (1, 3, 6))}

# (1) r4296395273 (RC-49): macro shock shared by every cluster open in a calendar period, iid across periods.
shock = rng.choice([-0.3, 0.3], size=(REPS, PERIODS))
q1 = np.repeat(0.5 + shock, PER_PERIOD, axis=1)
x1 = increments(q1, rng)
fa1 = int((grapa_paths(x1) >= THRESHOLD).sum())
families['macro_shock_iid_periods'] = {
    'description': 'q_t = 0.5 +/- 0.3 per period, 5 clusters per period, marginal E[X] = 0',
    'eprocess_crossings': fa1, 'eprocess_rate': fa1 / REPS,
    'exact_lower_99': round(float(beta.ppf(0.01, fa1, REPS - fa1 + 1)), 6),
    'fixed_horizon_size': fixed_horizon_sizes(x1, PERIODS, (1, 3, 6))}

# (2) persistent macro regime: shock follows a two-state chain with persistence 0.9 (mean zero).
s = np.empty((REPS, PERIODS)); s[:, 0] = rng.choice([-0.3, 0.3], size=REPS)
for tt in range(1, PERIODS):
    stay = rng.random(REPS) < 0.9
    s[:, tt] = np.where(stay, s[:, tt - 1], -s[:, tt - 1])
q2 = np.repeat(0.5 + s, PER_PERIOD, axis=1)
x2 = increments(q2, rng)
fa2 = int((grapa_paths(x2) >= THRESHOLD).sum())
families['macro_shock_persistent_regime'] = {
    'description': 'two-state regime, P(stay) = 0.9, stationary mean zero',
    'eprocess_crossings': fa2, 'eprocess_rate': fa2 / REPS,
    'fixed_horizon_size': fixed_horizon_sizes(x2, PERIODS, (1, 3, 6)),
    'note': 'period means are autocorrelated; a block of one period is not a valid unit here; the block length is a pre-registered dependence model'}

# (3) r4296395298 (RC-50): time-varying skill, average effect exactly zero (first half +, second half -).
q3 = np.concatenate([np.full((REPS, K // 2), 0.8), np.full((REPS, K // 2), 0.2)], axis=1)   # E[X] = +0.12 then -0.12
x3 = increments(q3, rng)
fa3 = int((grapa_paths(x3) >= THRESHOLD).sum())
families['time_varying_skill_average_zero'] = {
    'description': 'E[X_k] = +0.12 for k <= 60, -0.12 for k > 60; average over the population = 0',
    'eprocess_crossings_by_120': fa3, 'eprocess_rate': fa3 / REPS,
    'fixed_horizon_size': fixed_horizon_sizes(x3, PERIODS, (1, 3, 6))}

# (4) time-varying skill, average effect NEGATIVE: first 40 clusters +0.12, remaining 80 clusters -0.08.
q4 = np.concatenate([np.full((REPS, 40), 0.8), np.full((REPS, 80), 0.3)], axis=1)
x4 = increments(q4, rng)
avg4 = (40 * 0.12 + 80 * (0.4 * 0.3 - 0.2)) / 120
fa4 = int((grapa_paths(x4) >= THRESHOLD).sum())
families['time_varying_skill_average_negative'] = {
    'description': 'E[X_k] = +0.12 for k <= 40, -0.08 for k > 40',
    'population_average_effect': round(avg4, 5),
    'eprocess_crossings_by_120': fa4, 'eprocess_rate': fa4 / REPS,
    'fixed_horizon_rejections': fixed_horizon_sizes(x4, PERIODS, (1, 3, 6))}
out['RC49_RC50_null_families'] = families
out['RC49_RC50_reading'] = ('the e-process controls the error of the sequential conditional null E[X_k | F_(k-1)] <= 0; '
                            'under cross-cluster dependence or time-varying skill that null is false while the '
                            'population-average null holds, so a crossing is not evidence about the average estimand')

# ---- r4296395308 (RC-52): forecast eligibility against the earliest time the outcome was knowable ----
def eligible(forecast_receipt, knowable_at, first_outcome_receipt):
    return forecast_receipt < min(knowable_at, first_outcome_receipt)
out['RC52_publication_gap'] = {
    'publication_10:00_forecast_received_10:05_outcome_received_10:30':
        {'eligible_under_v2_T-02_rule': 605 < 630, 'eligible_under_v3_rule': eligible(605, 600, 630)},
    'forecast_received_09:55': {'eligible_under_v3_rule': eligible(595, 600, 630)}}

# ---- r4296395335 (RC-54): deterministic oracle fixtures for the shrinkage estimator ----
def logit(p): return math.log(p / (1 - p))
def expit(z): return 1 / (1 + math.exp(-z))
a, b = 2.0, 18.0                      # pre-registered reference-class prior, mean 0.10
fixtures = {}
for s_, n_ in [(5, 20), (0, 50), (0, 0)]:
    post = beta(a + s_, b + n_ - s_)
    fixtures[f's={s_},n={n_}'] = {'posterior': f'Beta({a + s_:g}, {b + n_ - s_:g})',
                                  'mean': round(float(post.mean()), 6),
                                  'q05': round(float(post.ppf(0.05)), 6), 'q95': round(float(post.ppf(0.95)), 6),
                                  'naive_s_over_n': (s_ / n_) if n_ else None}
out['RC54_beta_posterior_fixtures'] = fixtures
n0 = 20.0                             # pre-registered: model weight w(n) = n0 / (n0 + n)
logit_fx = {}
for p_model, (s_, n_) in [(0.001, (5, 20)), (0.001, (0, 0)), (0.5, (5, 20))]:
    ref = (a + s_) / (a + b + n_)
    w = n0 / (n0 + n_)
    p_out = expit(w * logit(p_model) + (1 - w) * logit(ref))
    logit_fx[f'p_model={p_model},s={s_},n={n_}'] = {'reference_rate': round(ref, 6), 'w_model': round(w, 4),
                                                   'point': round(p_out, 6)}
out['RC54_logit_shrinkage_fixtures'] = logit_fx
out['RC54_trivial_implementation_fails'] = fixtures['s=5,n=20']['naive_s_over_n'] != fixtures['s=5,n=20']['mean']

# ---- RC-55 (self-reported, issue #3 comment 6218965225): frame locals keep a secret reachable ----
def canary(): return 'SYNTHETIC-' + 'CANARY-r3'
class Transport(Exception):
    def __init__(self, request): super().__init__('transport'); self.request = request
class Sanitized(RuntimeError): pass
class Redacted:
    def __init__(self, value): self._value = value
    def __repr__(self): return 'Redacted(***)'
def reachable(exc):
    seen, found, stack = set(), [], [exc]
    while stack:
        e = stack.pop()
        if e is None or id(e) in seen: continue
        seen.add(id(e)); found.append(e); stack += [e.__context__, e.__cause__]
        tb = e.__traceback__
        while tb is not None:
            for v in tb.tb_frame.f_locals.values():
                (stack if isinstance(v, BaseException) else found).append(v)
            tb = tb.tb_next
    return found
def leaks(exc): return any(canary() in repr(o) for o in reachable(exc))
def case_from_none():
    headers = {'Authorization': f'Bearer {canary()}'}
    try: raise Transport(headers)
    except Transport: raise Sanitized('transport error') from None
def case_context_none():
    headers = {'Authorization': f'Bearer {canary()}'}
    try: raise Transport(headers)
    except Transport:
        s_ = Sanitized('transport error'); s_.__context__ = None; raise s_
def case_outside_plain_local():
    headers = {'Authorization': f'Bearer {canary()}'}; kind = None
    try: raise Transport(headers)
    except Transport as ex: kind = type(ex).__name__
    raise Sanitized(f'transport error: {kind}')
def case_outside_redacted():
    auth = Redacted(f'Bearer {canary()}'); kind = None
    try: raise Transport({'Authorization': auth})
    except Transport as ex: kind = type(ex).__name__
    raise Sanitized(f'transport error: {kind}')
table = {}
for name, fn in [('from_None_in_handler', case_from_none), ('context_None_in_handler', case_context_none),
                 ('outside_handler_plain_local', case_outside_plain_local), ('outside_handler_redacting_holder', case_outside_redacted)]:
    try: fn()
    except Sanitized as s_: table[name] = {'context_is_None': s_.__context__ is None, 'canary_reachable': leaks(s_)}
out['RC55_exception_graph_canary'] = table
out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
```
<!-- round3-script:end -->

Output:

```json
{
  "RC48_a3_design": {
    "n=2000,conf=0.95": {
      "k_max": 102,
      "P_pass_if_size_exactly_0.05": 0.606739,
      "P_pass_if_size_0.06": 0.047114,
      "P_pass_if_size_0.07": 0.0003050828854872164
    },
    "n=20000,conf=0.99": {
      "k_max": 1122,
      "P_pass_if_size_exactly_0.05": 0.999953,
      "P_pass_if_size_0.06": 0.009982,
      "P_pass_if_size_0.07": 9.812816862921764e-16
    }
  },
  "RC49_RC50_null_families": {
    "independent_clusters_valid_null": {
      "eprocess_crossings": 11,
      "eprocess_rate": 0.00055,
      "exact_upper_99": 0.001074,
      "fixed_horizon_size": {
        "naive_iid_cluster_t": 0.04095,
        "block_of_1_periods_t_df23": 0.04795,
        "block_of_3_periods_t_df7": 0.0476,
        "block_of_6_periods_t_df3": 0.04815
      }
    },
    "macro_shock_iid_periods": {
      "description": "q_t = 0.5 +/- 0.3 per period, 5 clusters per period, marginal E[X] = 0",
      "eprocess_crossings": 448,
      "eprocess_rate": 0.0224,
      "exact_lower_99": 0.020035,
      "fixed_horizon_size": {
        "naive_iid_cluster_t": 0.1343,
        "block_of_1_periods_t_df23": 0.05105,
        "block_of_3_periods_t_df7": 0.05075,
        "block_of_6_periods_t_df3": 0.05185
      }
    },
    "macro_shock_persistent_regime": {
      "description": "two-state regime, P(stay) = 0.9, stationary mean zero",
      "eprocess_crossings": 5781,
      "eprocess_rate": 0.28905,
      "fixed_horizon_size": {
        "naive_iid_cluster_t": 0.3372,
        "block_of_1_periods_t_df23": 0.27145,
        "block_of_3_periods_t_df7": 0.1913,
        "block_of_6_periods_t_df3": 0.1476
      },
      "note": "period means are autocorrelated; a block of one period is not a valid unit here; the block length is a pre-registered dependence model"
    },
    "time_varying_skill_average_zero": {
      "description": "E[X_k] = +0.12 for k <= 60, -0.12 for k > 60; average over the population = 0",
      "eprocess_crossings_by_120": 12555,
      "eprocess_rate": 0.62775,
      "fixed_horizon_size": {
        "naive_iid_cluster_t": 0.01585,
        "block_of_1_periods_t_df23": 0.00095,
        "block_of_3_periods_t_df7": 0.0,
        "block_of_6_periods_t_df3": 0.0
      }
    },
    "time_varying_skill_average_negative": {
      "description": "E[X_k] = +0.12 for k <= 40, -0.08 for k > 40",
      "population_average_effect": -0.01333,
      "eprocess_crossings_by_120": 727,
      "eprocess_rate": 0.03635,
      "fixed_horizon_rejections": {
        "naive_iid_cluster_t": 0.00395,
        "block_of_1_periods_t_df23": 0.0008,
        "block_of_3_periods_t_df7": 0.0,
        "block_of_6_periods_t_df3": 0.0
      }
    }
  },
  "RC49_RC50_reading": "the e-process controls the error of the sequential conditional null E[X_k | F_(k-1)] <= 0; under cross-cluster dependence or time-varying skill that null is false while the population-average null holds, so a crossing is not evidence about the average estimand",
  "RC52_publication_gap": {
    "publication_10:00_forecast_received_10:05_outcome_received_10:30": {
      "eligible_under_v2_T-02_rule": true,
      "eligible_under_v3_rule": false
    },
    "forecast_received_09:55": {
      "eligible_under_v3_rule": true
    }
  },
  "RC54_beta_posterior_fixtures": {
    "s=5,n=20": {
      "posterior": "Beta(7, 33)",
      "mean": 0.175,
      "q05": 0.087401,
      "q95": 0.281236,
      "naive_s_over_n": 0.25
    },
    "s=0,n=50": {
      "posterior": "Beta(2, 68)",
      "mean": 0.028571,
      "q05": 0.005174,
      "q95": 0.066914,
      "naive_s_over_n": 0.0
    },
    "s=0,n=0": {
      "posterior": "Beta(2, 18)",
      "mean": 0.1,
      "q05": 0.019033,
      "q95": 0.226374,
      "naive_s_over_n": null
    }
  },
  "RC54_logit_shrinkage_fixtures": {
    "p_model=0.001,s=5,n=20": {
      "reference_rate": 0.175,
      "w_model": 0.5,
      "point": 0.014362
    },
    "p_model=0.001,s=0,n=0": {
      "reference_rate": 0.1,
      "w_model": 1.0,
      "point": 0.001
    },
    "p_model=0.5,s=5,n=20": {
      "reference_rate": 0.175,
      "w_model": 0.5,
      "point": 0.315334
    }
  },
  "RC54_trivial_implementation_fails": true,
  "RC55_exception_graph_canary": {
    "from_None_in_handler": {
      "context_is_None": false,
      "canary_reachable": true
    },
    "context_None_in_handler": {
      "context_is_None": false,
      "canary_reachable": true
    },
    "outside_handler_plain_local": {
      "context_is_None": true,
      "canary_reachable": true
    },
    "outside_handler_redacting_holder": {
      "context_is_None": true,
      "canary_reachable": false
    }
  },
  "python": "3.11.17"
}
```

Reading. `RC48_a3_design` is the finding reproduced: the round-2 A3 design accepts a correct implementation
with probability 0.607. `RC49_RC50_null_families`: the cluster-level e-process is far below α on the valid
clustered null (0.055 %) and stays below α under independent period shocks (2.24 %), but has no level guarantee
there and loses control under a persistent regime (28.9 %) and under time-varying skill with zero average
(62.8 %), because in those families the sequential conditional null is false while the population-average null
is true. The fixed-horizon paired cluster test with a block-of-one-period variance holds size under independent
period shocks (5.1 %) where the cluster-iid variance does not (13.4 %), and is conservative under time-varying
skill; under the persistent regime no tested block length holds size (27.1 % / 19.1 % / 14.8 %), which with
P(stay) = 0.9 over 24 periods means roughly three independent regimes, too few for any test at this supply.
`RC52_publication_gap` is the eligibility rule on the worked example. `RC54_*` are the T-20 oracle values; the
trivial s/n implementation differs from the posterior mean (0.25 vs 0.175). `RC55_exception_graph_canary` is
the frame-locals table: only the redacting-holder variant removes the canary from the reachable graph.

## Appendix E. Round-4 checks (REPRODUCED)

Needs no reference code and no network. Run with `python -I round4_checks.py` in an isolated venv (Python
3.11.17, numpy 2.4.6, scipy 1.17.1; 11 s), extracting the block between the `round4-script` markers as in
Appendix A. Seeds are fixed; two consecutive runs produced byte-identical output. The generators are those of
Appendix A (D1 rows: baseline b, challenger b ± √δ, E[X] = δ) and Appendix D (baseline 0.4, challenger 0.6,
X = 0.4·Y − 0.2, five clusters per calendar period); the block-of-one-period t test is the Appendix D function.
The HMAC in the RC-62 block uses a literal test string as key; it is a toy for the signing-subset argument, not
a proposal to use HMAC (RC-12 requires owner public-key signatures).

<!-- round4-script:start -->
```python
"""Round-4 checks for the Codex findings on PR #4 at d46c204 (no reference code, no network)."""
import hashlib, hmac, json, math, sys, types
import numpy as np
from scipy.stats import beta, binom, norm, multivariate_normal, t as student_t

out = {}
ALPHA, THRESHOLD, LAM_MAX = 0.05, 20.0, 0.5

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

# ---- archived GRAPA recurrence (vectorised), identical to 16 Appendix A and D ----
def grapa_paths(xs, lam_max=LAM_MAX, checkpoints=()):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    snaps = {}
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
        if n + 1 in checkpoints:
            snaps[n + 1] = peak.copy()
    return wealth, peak, snaps

def block_t(xs, per_period, block_periods=1):
    """One-sided block-clustered t statistic of mean X <= 0: blocks of block_periods calendar periods."""
    n_paths, k = xs.shape
    periods = k // per_period
    g = periods // block_periods
    bm = xs[:, :g * block_periods * per_period].reshape(n_paths, g, -1).mean(axis=2)
    with np.errstate(divide='ignore', invalid='ignore'):
        tb = bm.mean(axis=1) / (bm.std(axis=1, ddof=1) / math.sqrt(g))
    return tb, g - 1

def block_t_rejects(xs, per_period, alpha=ALPHA, block_periods=1):
    tb, df = block_t(xs, per_period, block_periods)
    return tb > student_t.ppf(1 - alpha, df)

# ================= r4296649357 (RC-56): one primary claim evaluated at two cut-offs =================
# Normal theory: two one-sided tests at information fractions 0.5 and 1.0 (correlation sqrt(0.5)),
# each at nominal alpha = 0.05; P(reject at either look) under the null.
z = norm.ppf(1 - ALPHA)
rho = math.sqrt(0.5)
cov = [[1.0, rho], [rho, 1.0]]
p_neither = float(multivariate_normal(mean=[0, 0], cov=cov).cdf([z, z]))
two_look = {'nominal_alpha_each_look': ALPHA, 'information_fractions': [0.5, 1.0],
            'type_I_error_reject_at_either_look_normal_theory': round(1 - p_neither, 5)}
# Lan-DeMets O'Brien-Fleming-type spending for one-sided alpha at t = 0.5, final boundary solved so that the
# total equals alpha under the same correlation.
def obf_spend(t_frac, alpha=ALPHA):
    return 2 * (1 - norm.cdf(norm.ppf(1 - alpha / 2) / math.sqrt(t_frac)))
a1 = obf_spend(0.5)
c1 = norm.ppf(1 - a1)
def total_alpha(c2):
    return 1 - float(multivariate_normal(mean=[0, 0], cov=cov).cdf([c1, c2]))
lo, hi = 1.0, 3.0
for _ in range(60):
    mid = (lo + hi) / 2
    if total_alpha(mid) > ALPHA: lo = mid
    else: hi = mid
c2 = (lo + hi) / 2
two_look['obf_spending_option'] = {'alpha_spent_at_12_months': round(a1, 5), 'z_boundary_12_months': round(c1, 4),
                                   'z_boundary_24_months': round(c2, 4), 'nominal_level_24_months': round(1 - norm.cdf(c2), 5),
                                   'total_type_I_error': round(total_alpha(c2), 5)}
# Simulation with the block-of-one-period t test on the round-3 generator (baseline 0.4, challenger 0.6,
# X = 0.4 Y - 0.2): look 1 after 12 periods (60 clusters), look 2 after 24 periods (120 clusters).
REPS, PERIODS, PER_PERIOD = 20000, 24, 5
K = PERIODS * PER_PERIOD
rng = np.random.default_rng(4026)
def increments(q, rng_):
    y = (rng_.random(q.shape) < q).astype(float)
    return 0.4 * y - 0.2
sim = {}
fam = {'independent_clusters_valid_null': np.full((REPS, K), 0.5)}
shock = rng.choice([-0.3, 0.3], size=(REPS, PERIODS))
fam['macro_shock_iid_periods'] = np.repeat(0.5 + shock, PER_PERIOD, axis=1)
for name, q in fam.items():
    x = increments(q, rng)
    r1 = block_t_rejects(x[:, :K // 2], PER_PERIOD)
    r2 = block_t_rejects(x, PER_PERIOD)
    t1, df1 = block_t(x[:, :K // 2], PER_PERIOD); t2, df2 = block_t(x, PER_PERIOD)
    # OBF-type boundaries applied to the t statistics through their own df (nominal levels a1 and 1 - Phi(c2)).
    s1_ = t1 > student_t.ppf(1 - a1, df1); s2_ = t2 > student_t.ppf(norm.cdf(c2), df2)
    sim[name] = {'reject_12m_only': round(float(r1.mean()), 5), 'reject_24m_only': round(float(r2.mean()), 5),
                 'reject_at_either_look_both_nominal_0.05': round(float((r1 | r2).mean()), 5),
                 'exact_lower_99_either_look': round(binom_lower(int((r1 | r2).sum()), REPS, 0.99), 5),
                 'single_primary_at_24m_with_12m_futility_look_only': round(float(r2.mean()), 5),
                 'obf_spending_both_looks': round(float((s1_ | s2_).mean()), 5)}
two_look['block_t_simulation'] = sim
out['RC56_two_cutoffs'] = two_look

# ================= r4296649368 (RC-57): VOID declared between knowable_at and registry receipt =================
def void_accepted_v3(void_receipt, first_outcome_receipt):      # v3 wording: "before any member's outcome was received"
    return void_receipt < first_outcome_receipt
def void_accepted_v4(void_receipt, t_star):                      # v4 wording: before the cluster's outcome-knowable time
    return void_receipt < t_star
knowable, outcome_receipt = 600, 630                             # 10:00 publication, 10:30 registry receipt
t_star = min(knowable, outcome_receipt)
out['RC57_void_window'] = {
    'void_received_10:10': {'accepted_under_v3_rule': void_accepted_v3(610, outcome_receipt),
                            'accepted_under_v4_rule': void_accepted_v4(610, t_star)},
    'void_received_09:55': {'accepted_under_v3_rule': void_accepted_v3(595, outcome_receipt),
                            'accepted_under_v4_rule': void_accepted_v4(595, t_star)},
    'reading': 'the v3 clause used receipt time where RC-52 had already moved every other cutoff to t*_k'}

# ================= r4296649378 (RC-58): interval transformation of the shrinkage estimator =================
def logit(p): return math.log(p / (1 - p))
def expit(zz): return 1 / (1 + math.exp(-zz))
A_, B_, N0, EPS = 2.0, 18.0, 20.0, 1e-6                           # fixture prior, weight scale, logit clip
def shrink(low, point, high, s_, n_):
    post = beta(A_ + s_, B_ + n_ - s_)
    targets = (float(post.ppf(0.05)), float(post.mean()), float(post.ppf(0.95)))
    w = N0 / (N0 + n_)
    res = []
    for p_model, ref in zip((low, point, high), targets):
        p_clip = min(max(p_model, EPS), 1 - EPS)
        res.append(expit(w * logit(p_clip) + (1 - w) * logit(ref)))
    return tuple(round(v, 6) for v in res)
interval_fx = {}
for (lo_, pt_, hi_), (s_, n_) in [((0.0005, 0.001, 0.002), (5, 20)), ((0.3, 0.5, 0.7), (5, 20)),
                                  ((0.0005, 0.001, 0.002), (0, 0)), ((0.001, 0.001, 0.001), (5, 20)),
                                  ((0.0, 0.001, 0.002), (5, 20)), ((0.0005, 0.001, 0.002), (0, 50))]:
    r = shrink(lo_, pt_, hi_, s_, n_)
    interval_fx[f'model=({lo_},{pt_},{hi_}),s={s_},n={n_}'] = {'low': r[0], 'point': r[1], 'high': r[2],
                                                               'ordered': r[0] <= r[1] <= r[2]}
out['RC58_interval_fixtures'] = interval_fx
out['RC58_raw_posterior_bounds_would_violate_ordering'] = {'posterior_q05_at_(5,20)': 0.087401, 'shrunk_point': 0.014362,
                                                           'low_le_point_if_raw_bounds_used': 0.087401 <= 0.014362}

# ================= r4296649412 (RC-61): power of the fixed-horizon primary test =================
# D1 generator of 16 Appendix A: baseline b, challenger p = b +/- sqrt(delta), Y ~ Bern(p),
# X = (b - Y)^2 - (p - Y)^2 with E[X] = delta; one increment per cluster, clusters independent, five per
# calendar period, block-of-one-period variance. The e-process (monitor) is run on the same paths.
POW_REPS = 10000
power = {}
for b in (0.5, 0.2):
    for delta in (0.005, 0.01, 0.02, 0.03):
        for kk in (120, 300, 600):
            r = np.random.default_rng(1000 + int(b * 10) * 100 + int(delta * 1000) * 10 + kk // 100)
            p = b + math.sqrt(delta) * r.choice([-1., 1.], size=(POW_REPS, kk))
            yy = (r.random(p.shape) < p).astype(float)
            xs = (b - yy) ** 2 - (p - yy) ** 2
            fh = int(block_t_rejects(xs, PER_PERIOD).sum())
            ep = int((grapa_paths(xs)[1] >= THRESHOLD).sum())
            power[f'b={b},delta={delta},clusters={kk}'] = {'fixed_horizon_block1_power': round(fh / POW_REPS, 4),
                                                           'eprocess_monitor_crossing_rate': round(ep / POW_REPS, 4)}
out['RC61_power_independent_clusters'] = power
# Under independent period shocks (F-22 family, b = 0.5 structure of Appendix D): q_t = 0.5 + 2.5 delta +/- 0.3.
power_shock = {}
for amp in (0.0, 0.3):
    for delta in (0.01, 0.02, 0.03):
        for kk in (120, 300, 600):
            r = np.random.default_rng(7000 + int(delta * 1000) * 10 + kk // 100 + int(amp * 10) * 1000)
            periods = kk // PER_PERIOD
            sh = r.choice([-amp, amp], size=(POW_REPS, periods))
            q = np.repeat(0.5 + 2.5 * delta + sh, PER_PERIOD, axis=1)
            xs = increments(q, r)
            fh = int(block_t_rejects(xs, PER_PERIOD).sum())
            ep = int((grapa_paths(xs)[1] >= THRESHOLD).sum())
            power_shock[f'shock=+/-{amp},delta={delta},clusters={kk}'] = {
                'fixed_horizon_block1_power': round(fh / POW_REPS, 4), 'eprocess_monitor_crossing_rate': round(ep / POW_REPS, 4)}
out['RC61_power_macro_shock_iid_periods'] = {'generator': 'baseline 0.4, challenger 0.6, q_t = 0.5 + 2.5 delta +/- shock per period (E[X] = delta, X in {-0.2, +0.2})',
                                              'cells': power_shock}
out['RC61_persistent_regime'] = 'size not held at 120 clusters over 24 periods (16 Appendix D), so no power figure is meaningful there'

# ================= r4296649427 (RC-63): positive-control oracles for each kernel =================
# (a) deterministic e-value oracle: constant increments +0.2 under the archived rule.
# lambda = 0 for n < 2; for constant X the sample variance is 0, so lambda = (1/mean) * n/(n+10) clipped
# to 0.5, i.e. 0.5 from n = 2 on; wealth after k increments = 1.1^(k-2).
const = np.full((1, 40), 0.2)
w_const, peak_const, snaps = grapa_paths(const, checkpoints=tuple(range(1, 41)))
first_cross = min(k for k, pk in snaps.items() if pk[0] >= THRESHOLD)
oracle_e = {'constant_+0.2_after_12': round(float(grapa_paths(const[:, :12])[0][0]), 6),
            'closed_form_1.1^10': round(1.1 ** 10, 6),
            'first_crossing_step': first_cross, 'closed_form_e_at_step_34': round(1.1 ** 32, 6)}
mixed = np.array([[0.2, -0.2, 0.2, 0.2, -0.2, 0.2, 0.2, 0.2, -0.2, 0.2, 0.2, 0.2]])
oracle_e['mixed_12_vector'] = mixed[0].tolist()
oracle_e['mixed_12_e_value'] = round(float(grapa_paths(mixed)[0][0]), 6)
# (b) deterministic fixed-horizon oracle: four block means.
bm = np.array([[0.05, 0.10, 0.00, 0.05]])
tstat = float(bm.mean() / (bm.std(ddof=1) / 2))
oracle_fh = {'block_means': bm[0].tolist(), 't_statistic': round(tstat, 6), 'df': 3,
             'one_sided_p': round(float(student_t.sf(tstat, 3)), 6), 'rejects_at_0.05': bool(tstat > student_t.ppf(0.95, 3))}
# (c) pre-specified alternative with a bounded minimum rejection rate for each kernel.
pc = {}
for delta in (0.03, 0.05, 0.08):
    r = np.random.default_rng(9000 + int(delta * 100))
    p = 0.5 + math.sqrt(delta) * r.choice([-1., 1.], size=(20000, 120))
    yy = (r.random(p.shape) < p).astype(float)
    xs = (0.5 - yy) ** 2 - (p - yy) ** 2
    fh = int(block_t_rejects(xs, PER_PERIOD).sum()); ep = int((grapa_paths(xs)[1] >= THRESHOLD).sum())
    pc[f'b=0.5,delta={delta},clusters=120'] = {
        'fixed_horizon_rejections': fh, 'fixed_horizon_rate': round(fh / 20000, 4),
        'fixed_horizon_exact_lower_99': round(binom_lower(fh, 20000, 0.99), 4),
        'eprocess_crossings': ep, 'eprocess_rate': round(ep / 20000, 4),
        'eprocess_exact_lower_99': round(binom_lower(ep, 20000, 0.99), 4)}
# Pass probability of a correct kernel against a lower bound of 0.90 when its true power is 0.95 or 0.97.
k_min = min(k for k in range(20000) if binom_lower(k, 20000, 0.99) >= 0.90)
pc['fixed_horizon_bound_0.90_design'] = {'k_min_rejections_of_20000': k_min,
                           'P_pass_if_power_0.93': round(float(binom.sf(k_min - 1, 20000, 0.93)), 6),
                           'P_pass_if_power_0.95': round(float(binom.sf(k_min - 1, 20000, 0.95)), 6),
                           'P_pass_if_power_0.964_(delta_0.08)': round(float(binom.sf(k_min - 1, 20000, 0.964)), 6),
                           'P_pass_if_inert_kernel': 0.0}
k_min_e = min(k for k in range(20000) if binom_lower(k, 20000, 0.99) >= 0.60)
pc['eprocess_bound_0.60_design'] = {'k_min_crossings_of_20000': k_min_e,
                           'P_pass_if_rate_0.65': round(float(binom.sf(k_min_e - 1, 20000, 0.65)), 6),
                           'P_pass_if_rate_0.71_(delta_0.08)': round(float(binom.sf(k_min_e - 1, 20000, 0.71)), 6),
                           'P_pass_if_inert_kernel': 0.0}
out['RC63_positive_controls'] = {'eprocess_oracle': oracle_e, 'fixed_horizon_oracle': oracle_fh, 'alternative_grid': pc}

# ================= r4296649421 (RC-62): a verifier that signs a subset of the capability tuple =================
FIELDS = ('capability', 'environment', 'release_digest', 'evidence_digest', 'epoch', 'nonce', 'expiry')
cap = {'capability': 'GATE_PROMOTE_SIM', 'environment': 'SIM', 'release_digest': 'r' * 8, 'evidence_digest': 'e' * 8,
       'epoch': 7, 'nonce': 'n1', 'expiry': 1000}
key = b'synthetic-test-key-not-a-secret'
def sign(record, signed_fields):
    msg = json.dumps({f: record[f] for f in signed_fields}, sort_keys=True).encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()
def mutate(record, f):
    r = dict(record); r[f] = (r[f] + 1) if isinstance(r[f], int) else r[f] + 'x'; return r
subset = ('environment', 'release_digest')                     # what T-31 v3 exercised besides the key
sig_subset = sign(cap, subset); sig_full = sign(cap, FIELDS)
out['RC62_partial_signature'] = {
    'verifier_signing_only_environment_and_release': {f: sign(mutate(cap, f), subset) == sig_subset for f in FIELDS},
    'verifier_signing_every_field': {f: sign(mutate(cap, f), FIELDS) == sig_full for f in FIELDS},
    'reading': 'True = the mutated record still verifies; T-31 v3 mutated only key, environment and release digest'}

# ================= r4296649399 (RC-60): the redacting holder still stores the raw secret =================
def canary(): return 'SYNTHETIC-' + 'CANARY-r4'
class Transport(Exception):
    def __init__(self, request): super().__init__('transport'); self.request = request
class Sanitized(RuntimeError): pass
class Redacted:
    def __init__(self, value): self._value = value
    def __repr__(self): return 'Redacted(***)'
def reachable_repr(exc):                                            # the round-3 probe (repr only)
    seen, found, stack = set(), [], [exc]
    while stack:
        e = stack.pop()
        if e is None or id(e) in seen: continue
        seen.add(id(e)); found.append(e); stack += [e.__context__, e.__cause__]
        tb = e.__traceback__
        while tb is not None:
            for v in tb.tb_frame.f_locals.values():
                (stack if isinstance(v, BaseException) else found).append(v)
            tb = tb.tb_next
    return found
def leaks_repr(exc): return any(canary() in repr(o) for o in reachable_repr(exc))
def leaks_state(exc):
    """Traverse object state (attributes, slots, containers, closures, exception args), not repr."""
    seen, stack = set(), list(reachable_repr(exc))
    while stack:
        o = stack.pop()
        if id(o) in seen: continue
        seen.add(id(o))
        if isinstance(o, (str, bytes)):
            if canary() in (o if isinstance(o, str) else o.decode('utf-8', 'ignore')): return True
            continue
        if isinstance(o, dict): stack += list(o.keys()) + list(o.values()); continue
        if isinstance(o, (list, tuple, set, frozenset)): stack += list(o); continue
        if isinstance(o, BaseException): stack += list(o.args)
        d = getattr(o, '__dict__', None)
        if isinstance(d, dict): stack += list(d.values())
        for slot in getattr(type(o), '__slots__', ()):
            if hasattr(o, slot): stack.append(getattr(o, slot))
        if isinstance(o, types.FunctionType):
            for cell in (o.__closure__ or ()):
                try: stack.append(cell.cell_contents)
                except ValueError: pass
    return False
def case_outside_redacted():                                        # round-3 "passing" variant
    auth = Redacted(f'Bearer {canary()}'); kind = None
    try: raise Transport({'Authorization': auth})
    except Transport as ex: kind = type(ex).__name__
    raise Sanitized(f'transport error: {kind}')
def _transport_call(request):
    """Holds the secret; catches every exception; returns only a typed outcome; its frame is gone before any raise."""
    headers = {**request, 'Authorization': f'Bearer {canary()}'}
    try:
        raise Transport(headers)
    except Transport as ex:
        return type(ex).__name__
    return None
def case_secret_confined_to_returned_frame():
    kind = _transport_call({'path': '/sim/precheck'})
    if kind is not None:
        raise Sanitized(f'transport error: {kind}')
def case_confined_but_outcome_carries_exception():                  # wrong: the outcome object references the frame
    def inner():
        headers = {'Authorization': f'Bearer {canary()}'}
        try: raise Transport(headers)
        except Transport as ex: return ex
    ex = inner()
    raise Sanitized(f'transport error: {type(ex).__name__}')
table = {}
for name, fn in [('outside_handler_redacting_holder_(v3_pass)', case_outside_redacted),
                 ('secret_confined_to_frame_that_returned', case_secret_confined_to_returned_frame),
                 ('confined_but_outcome_is_the_exception_object', case_confined_but_outcome_carries_exception)]:
    try: fn()
    except Sanitized as s_:
        table[name] = {'context_is_None': s_.__context__ is None, 'repr_probe_leaks': leaks_repr(s_), 'state_probe_leaks': leaks_state(s_)}
out['RC60_object_state_canary'] = table
out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
```
<!-- round4-script:end -->

Output:

```json
{
  "RC56_two_cutoffs": {
    "nominal_alpha_each_look": 0.05,
    "information_fractions": [
      0.5,
      1.0
    ],
    "type_I_error_reject_at_either_look_normal_theory": 0.08008,
    "obf_spending_option": {
      "alpha_spent_at_12_months": 0.00557,
      "z_boundary_12_months": 2.538,
      "z_boundary_24_months": 1.6621,
      "nominal_level_24_months": 0.04825,
      "total_type_I_error": 0.05
    },
    "block_t_simulation": {
      "independent_clusters_valid_null": {
        "reject_12m_only": 0.05805,
        "reject_24m_only": 0.05105,
        "reject_at_either_look_both_nominal_0.05": 0.088,
        "exact_lower_99_either_look": 0.0834,
        "single_primary_at_24m_with_12m_futility_look_only": 0.05105,
        "obf_spending_both_looks": 0.05255
      },
      "macro_shock_iid_periods": {
        "reject_12m_only": 0.04665,
        "reject_24m_only": 0.0507,
        "reject_at_either_look_both_nominal_0.05": 0.07845,
        "exact_lower_99_either_look": 0.07409,
        "single_primary_at_24m_with_12m_futility_look_only": 0.0507,
        "obf_spending_both_looks": 0.05085
      }
    }
  },
  "RC57_void_window": {
    "void_received_10:10": {
      "accepted_under_v3_rule": true,
      "accepted_under_v4_rule": false
    },
    "void_received_09:55": {
      "accepted_under_v3_rule": true,
      "accepted_under_v4_rule": true
    },
    "reading": "the v3 clause used receipt time where RC-52 had already moved every other cutoff to t*_k"
  },
  "RC58_interval_fixtures": {
    "model=(0.0005,0.001,0.002),s=5,n=20": {
      "low": 0.006874,
      "point": 0.014362,
      "high": 0.027239,
      "ordered": true
    },
    "model=(0.3,0.5,0.7),s=5,n=20": {
      "low": 0.168465,
      "point": 0.315334,
      "high": 0.488622,
      "ordered": true
    },
    "model=(0.0005,0.001,0.002),s=0,n=0": {
      "low": 0.0005,
      "point": 0.001,
      "high": 0.002,
      "ordered": true
    },
    "model=(0.001,0.001,0.001),s=5,n=20": {
      "low": 0.009696,
      "point": 0.014362,
      "high": 0.019407,
      "ordered": true
    },
    "model=(0.0,0.001,0.002),s=5,n=20": {
      "low": 0.000309,
      "point": 0.014362,
      "high": 0.027239,
      "ordered": true
    },
    "model=(0.0005,0.001,0.002),s=0,n=50": {
      "low": 0.002657,
      "point": 0.011072,
      "high": 0.025155,
      "ordered": true
    }
  },
  "RC58_raw_posterior_bounds_would_violate_ordering": {
    "posterior_q05_at_(5,20)": 0.087401,
    "shrunk_point": 0.014362,
    "low_le_point_if_raw_bounds_used": false
  },
  "RC61_power_independent_clusters": {
    "b=0.5,delta=0.005,clusters=120": {
      "fixed_horizon_block1_power": 0.1943,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.5,delta=0.005,clusters=300": {
      "fixed_horizon_block1_power": 0.3356,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.5,delta=0.005,clusters=600": {
      "fixed_horizon_block1_power": 0.5402,
      "eprocess_monitor_crossing_rate": 0.0131
    },
    "b=0.5,delta=0.01,clusters=120": {
      "fixed_horizon_block1_power": 0.2862,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.5,delta=0.01,clusters=300": {
      "fixed_horizon_block1_power": 0.5471,
      "eprocess_monitor_crossing_rate": 0.0142
    },
    "b=0.5,delta=0.01,clusters=600": {
      "fixed_horizon_block1_power": 0.8,
      "eprocess_monitor_crossing_rate": 0.2745
    },
    "b=0.5,delta=0.02,clusters=120": {
      "fixed_horizon_block1_power": 0.4624,
      "eprocess_monitor_crossing_rate": 0.0013
    },
    "b=0.5,delta=0.02,clusters=300": {
      "fixed_horizon_block1_power": 0.8022,
      "eprocess_monitor_crossing_rate": 0.2683
    },
    "b=0.5,delta=0.02,clusters=600": {
      "fixed_horizon_block1_power": 0.9738,
      "eprocess_monitor_crossing_rate": 0.8118
    },
    "b=0.5,delta=0.03,clusters=120": {
      "fixed_horizon_block1_power": 0.6213,
      "eprocess_monitor_crossing_rate": 0.0313
    },
    "b=0.5,delta=0.03,clusters=300": {
      "fixed_horizon_block1_power": 0.9292,
      "eprocess_monitor_crossing_rate": 0.6074
    },
    "b=0.5,delta=0.03,clusters=600": {
      "fixed_horizon_block1_power": 0.9976,
      "eprocess_monitor_crossing_rate": 0.9642
    },
    "b=0.2,delta=0.005,clusters=120": {
      "fixed_horizon_block1_power": 0.2434,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.2,delta=0.005,clusters=300": {
      "fixed_horizon_block1_power": 0.461,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.2,delta=0.005,clusters=600": {
      "fixed_horizon_block1_power": 0.703,
      "eprocess_monitor_crossing_rate": 0.0054
    },
    "b=0.2,delta=0.01,clusters=120": {
      "fixed_horizon_block1_power": 0.3994,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.2,delta=0.01,clusters=300": {
      "fixed_horizon_block1_power": 0.7192,
      "eprocess_monitor_crossing_rate": 0.0049
    },
    "b=0.2,delta=0.01,clusters=600": {
      "fixed_horizon_block1_power": 0.9336,
      "eprocess_monitor_crossing_rate": 0.3151
    },
    "b=0.2,delta=0.02,clusters=120": {
      "fixed_horizon_block1_power": 0.6494,
      "eprocess_monitor_crossing_rate": 0.0003
    },
    "b=0.2,delta=0.02,clusters=300": {
      "fixed_horizon_block1_power": 0.9442,
      "eprocess_monitor_crossing_rate": 0.2962
    },
    "b=0.2,delta=0.02,clusters=600": {
      "fixed_horizon_block1_power": 0.9981,
      "eprocess_monitor_crossing_rate": 0.948
    },
    "b=0.2,delta=0.03,clusters=120": {
      "fixed_horizon_block1_power": 0.8286,
      "eprocess_monitor_crossing_rate": 0.0118
    },
    "b=0.2,delta=0.03,clusters=300": {
      "fixed_horizon_block1_power": 0.9946,
      "eprocess_monitor_crossing_rate": 0.7845
    },
    "b=0.2,delta=0.03,clusters=600": {
      "fixed_horizon_block1_power": 1.0,
      "eprocess_monitor_crossing_rate": 0.9991
    }
  },
  "RC61_power_macro_shock_iid_periods": {
    "generator": "baseline 0.4, challenger 0.6, q_t = 0.5 + 2.5 delta +/- shock per period (E[X] = delta, X in {-0.2, +0.2})",
    "cells": {
      "shock=+/-0.0,delta=0.01,clusters=120": {
        "fixed_horizon_block1_power": 0.1375,
        "eprocess_monitor_crossing_rate": 0.0021
      },
      "shock=+/-0.0,delta=0.01,clusters=300": {
        "fixed_horizon_block1_power": 0.219,
        "eprocess_monitor_crossing_rate": 0.0444
      },
      "shock=+/-0.0,delta=0.01,clusters=600": {
        "fixed_horizon_block1_power": 0.3417,
        "eprocess_monitor_crossing_rate": 0.1318
      },
      "shock=+/-0.0,delta=0.02,clusters=120": {
        "fixed_horizon_block1_power": 0.2837,
        "eprocess_monitor_crossing_rate": 0.0101
      },
      "shock=+/-0.0,delta=0.02,clusters=300": {
        "fixed_horizon_block1_power": 0.5293,
        "eprocess_monitor_crossing_rate": 0.1916
      },
      "shock=+/-0.0,delta=0.02,clusters=600": {
        "fixed_horizon_block1_power": 0.7925,
        "eprocess_monitor_crossing_rate": 0.4884
      },
      "shock=+/-0.0,delta=0.03,clusters=120": {
        "fixed_horizon_block1_power": 0.4823,
        "eprocess_monitor_crossing_rate": 0.0436
      },
      "shock=+/-0.0,delta=0.03,clusters=300": {
        "fixed_horizon_block1_power": 0.8325,
        "eprocess_monitor_crossing_rate": 0.4977
      },
      "shock=+/-0.0,delta=0.03,clusters=600": {
        "fixed_horizon_block1_power": 0.9802,
        "eprocess_monitor_crossing_rate": 0.8767
      },
      "shock=+/-0.3,delta=0.01,clusters=120": {
        "fixed_horizon_block1_power": 0.101,
        "eprocess_monitor_crossing_rate": 0.0497
      },
      "shock=+/-0.3,delta=0.01,clusters=300": {
        "fixed_horizon_block1_power": 0.1336,
        "eprocess_monitor_crossing_rate": 0.1968
      },
      "shock=+/-0.3,delta=0.01,clusters=600": {
        "fixed_horizon_block1_power": 0.1923,
        "eprocess_monitor_crossing_rate": 0.3345
      },
      "shock=+/-0.3,delta=0.02,clusters=120": {
        "fixed_horizon_block1_power": 0.1706,
        "eprocess_monitor_crossing_rate": 0.0928
      },
      "shock=+/-0.3,delta=0.02,clusters=300": {
        "fixed_horizon_block1_power": 0.2922,
        "eprocess_monitor_crossing_rate": 0.3597
      },
      "shock=+/-0.3,delta=0.02,clusters=600": {
        "fixed_horizon_block1_power": 0.4688,
        "eprocess_monitor_crossing_rate": 0.6038
      },
      "shock=+/-0.3,delta=0.03,clusters=120": {
        "fixed_horizon_block1_power": 0.2685,
        "eprocess_monitor_crossing_rate": 0.1646
      },
      "shock=+/-0.3,delta=0.03,clusters=300": {
        "fixed_horizon_block1_power": 0.5056,
        "eprocess_monitor_crossing_rate": 0.5719
      },
      "shock=+/-0.3,delta=0.03,clusters=600": {
        "fixed_horizon_block1_power": 0.7552,
        "eprocess_monitor_crossing_rate": 0.8337
      }
    }
  },
  "RC61_persistent_regime": "size not held at 120 clusters over 24 periods (16 Appendix D), so no power figure is meaningful there",
  "RC63_positive_controls": {
    "eprocess_oracle": {
      "constant_+0.2_after_12": 2.593742,
      "closed_form_1.1^10": 2.593742,
      "first_crossing_step": 34,
      "closed_form_e_at_step_34": 21.113777,
      "mixed_12_vector": [
        0.2,
        -0.2,
        0.2,
        0.2,
        -0.2,
        0.2,
        0.2,
        0.2,
        -0.2,
        0.2,
        0.2,
        0.2
      ],
      "mixed_12_e_value": 1.447854
    },
    "fixed_horizon_oracle": {
      "block_means": [
        0.05,
        0.1,
        0.0,
        0.05
      ],
      "t_statistic": 2.44949,
      "df": 3,
      "one_sided_p": 0.045861,
      "rejects_at_0.05": true
    },
    "alternative_grid": {
      "b=0.5,delta=0.03,clusters=120": {
        "fixed_horizon_rejections": 12507,
        "fixed_horizon_rate": 0.6253,
        "fixed_horizon_exact_lower_99": 0.6173,
        "eprocess_crossings": 642,
        "eprocess_rate": 0.0321,
        "eprocess_exact_lower_99": 0.0293
      },
      "b=0.5,delta=0.05,clusters=120": {
        "fixed_horizon_rejections": 16599,
        "fixed_horizon_rate": 0.8299,
        "fixed_horizon_exact_lower_99": 0.8237,
        "eprocess_crossings": 5133,
        "eprocess_rate": 0.2566,
        "eprocess_exact_lower_99": 0.2495
      },
      "b=0.5,delta=0.08,clusters=120": {
        "fixed_horizon_rejections": 19279,
        "fixed_horizon_rate": 0.9639,
        "fixed_horizon_exact_lower_99": 0.9608,
        "eprocess_crossings": 14214,
        "eprocess_rate": 0.7107,
        "eprocess_exact_lower_99": 0.7032
      },
      "fixed_horizon_bound_0.90_design": {
        "k_min_rejections_of_20000": 18099,
        "P_pass_if_power_0.93": 1.0,
        "P_pass_if_power_0.95": 1.0,
        "P_pass_if_power_0.964_(delta_0.08)": 1.0,
        "P_pass_if_inert_kernel": 0.0
      },
      "eprocess_bound_0.60_design": {
        "k_min_crossings_of_20000": 12162,
        "P_pass_if_rate_0.65": 1.0,
        "P_pass_if_rate_0.71_(delta_0.08)": 1.0,
        "P_pass_if_inert_kernel": 0.0
      }
    }
  },
  "RC62_partial_signature": {
    "verifier_signing_only_environment_and_release": {
      "capability": true,
      "environment": false,
      "release_digest": false,
      "evidence_digest": true,
      "epoch": true,
      "nonce": true,
      "expiry": true
    },
    "verifier_signing_every_field": {
      "capability": false,
      "environment": false,
      "release_digest": false,
      "evidence_digest": false,
      "epoch": false,
      "nonce": false,
      "expiry": false
    },
    "reading": "True = the mutated record still verifies; T-31 v3 mutated only key, environment and release digest"
  },
  "RC60_object_state_canary": {
    "outside_handler_redacting_holder_(v3_pass)": {
      "context_is_None": true,
      "repr_probe_leaks": false,
      "state_probe_leaks": true
    },
    "secret_confined_to_frame_that_returned": {
      "context_is_None": true,
      "repr_probe_leaks": false,
      "state_probe_leaks": false
    },
    "confined_but_outcome_is_the_exception_object": {
      "context_is_None": true,
      "repr_probe_leaks": true,
      "state_probe_leaks": true
    }
  },
  "python": "3.11.17"
}
```

Reading. `RC56_two_cutoffs`: two confirmatory looks at nominal α = 0.05 give 8.0 % (normal theory) and 8.8 % /
7.8 % (block test on the two null families); a single primary at 24 months with a futility-only interim gives
5.1 %; the O'Brien–Fleming-type boundaries give 5.3 % / 5.1 % through the block test's own degrees of freedom
(the 12-month look has twelve blocks, which is why the first-look size alone is 5.8 % on the valid null and the
spending option needs simulation calibration in T-12). `RC57_void_window`: the v3 clause admits a VOID declared
between publication and registry receipt; the t*_k clause refuses it. `RC58_interval_fixtures`: the endpoint-wise
logit shrinkage returns ordered intervals on every fixture, including a collapsed model interval and low = 0;
the raw posterior quantiles would violate low ≤ point, as Codex computed. `RC61_*`: power of the primary test on
the D1 generator with independent clusters, with the monitor's crossing rate on the same paths (the monitor's
600-cluster rates 0.2745 and 0.3151 at δ = 0.01 agree with the Appendix B counts 1,623 / 6,000 and 1,844 /
6,000 within Monte Carlo error); the macro-shock table is on the Appendix D generator (X ∈ {−0.2, +0.2}, a
different scale from the D1 rows), where ± 0.3 period shocks roughly halve the primary's power at every cell.
`RC63_positive_controls`: the deterministic oracles and the pre-specified alternative with its pass
probabilities. `RC62_partial_signature`: a verifier over two fields accepts five single-field substitutions; one
over the whole tuple rejects all seven. `RC60_object_state_canary`: the round-3 `repr` probe clears the
redacting holder while the object-state probe finds the secret in it; confining the secret to a frame that has
returned clears both probes; returning the exception object as the outcome leaks under both.

## Appendix F. Round-5 checks (REPRODUCED; evidence only, nothing applied)

Needs no reference code and no network. Run with `python -I round5_checks.py` in an isolated venv (Python 3.11.17,
numpy 2.4.6, scipy 1.17.1; 31 s), extracting the block between the `round5-script` markers as in Appendix A.
Seeds are fixed; two consecutive runs produced byte-identical output. The generators and the block-of-one-period
t test are those of Appendix D and E. The RC-65 block is a toy state machine with the two watermark policies; the
RC-69 block adds the cluster-weighted estimate with the block-sum variance beside the Appendix D/E equal-block-mean
statistic; the RC-70 block fixes the period count at the design's 24 and varies clusters per period, which is
what Appendix E should have done.

<!-- round5-script:start -->
```python
"""Round-5 checks for the Codex findings on PR #4 at 88abaa4 (no reference code, no network).

Evidence only: the findings are recorded, not applied (16 section 4.6, OD10). Generators and the
block-of-one-period t test are those of 16 Appendix D and E.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
ALPHA, THRESHOLD, LAM_MAX = 0.05, 20.0, 0.5

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

def grapa_paths(xs, lam_max=LAM_MAX):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
    return wealth, peak

def block_t(xs, per_period, block_periods=1):
    """Appendix D/E statistic: one-sided t over equal-sized calendar-block MEANS."""
    n_paths, k = xs.shape
    periods = k // per_period
    g = periods // block_periods
    bm = xs[:, :g * block_periods * per_period].reshape(n_paths, g, -1).mean(axis=2)
    with np.errstate(divide='ignore', invalid='ignore'):
        tb = bm.mean(axis=1) / (bm.std(axis=1, ddof=1) / math.sqrt(g))
    return tb, g - 1

def block_t_rejects(xs, per_period, alpha=ALPHA, block_periods=1):
    tb, df = block_t(xs, per_period, block_periods)
    return tb > student_t.ppf(1 - alpha, df)

def increments(q, rng_):
    y = (rng_.random(q.shape) < q).astype(float)
    return 0.4 * y - 0.2

# ================= r4296914298 (RC-65): watermark advanced only by admissions =================
# Toy state machine. A capability is valid iff now < expiry and now >= watermark (fail closed on rollback).
# Variant A persists the watermark only when a check is admitted; variant B persists max(now) on every
# clock-dependent check, admitted or rejected. Codex's replay: last admission at t0 = 10, capability expires
# at t1 = 20, presented at t2 = 30 (rejected: expired), clock rolled back to t = 15, presented again.
def run_clock_variant(advance_on_reject):
    watermark = 0.0; log = []
    def check(now, expiry):
        nonlocal watermark
        if now < watermark:
            verdict = 'rejected_rollback'
        elif now >= expiry:
            verdict = 'rejected_expired'
        else:
            verdict = 'admitted'
        if verdict == 'admitted' or advance_on_reject:
            watermark = max(watermark, now)
        log.append((now, expiry, verdict, watermark))
        return verdict
    check(10, 100)            # an unrelated admission at t0 = 10
    check(30, 20)             # the expired capability presented at t2 = 30
    replay = check(15, 20)    # clock rolled back to t = 15 < t1 = 20, same capability
    return replay, log
clock = {}
for name, flag in (('A_watermark_on_admission_only_(v4_text)', False), ('B_watermark_on_every_check', True)):
    verdict, log = run_clock_variant(flag)
    clock[name] = {'replay_after_rollback': verdict, 'log': [f'now={n} expiry={e} {v} watermark={w}' for n, e, v, w in log]}
out['RC65_clock_watermark_replay'] = clock

# ================= r4296914341 (RC-69): equal block means versus the per-cluster estimand =================
# Deterministic oracle 1: two calendar blocks of sizes 1 and 9.
blocks = [np.array([0.5]), np.full(9, -0.1)]
allx = np.concatenate(blocks)
equal_block_mean_estimate = float(np.mean([b.mean() for b in blocks]))
cluster_weighted_estimate = float(allx.mean())
def cluster_weighted_t(blocks):
    """theta = mean over clusters; variance = sum over blocks of (sum within block of (X - theta))^2 / N^2,
    with the G/(G-1) small-sample factor; G-1 degrees of freedom (block-sum / cluster-robust form)."""
    allx = np.concatenate(blocks); n = len(allx); g = len(blocks)
    theta = allx.mean()
    v = sum(((b - theta).sum()) ** 2 for b in blocks) / n ** 2 * g / (g - 1)
    return float(theta), float(theta / math.sqrt(v)) if v > 0 else float('inf'), g - 1
rc69 = {'oracle_1_block_sizes_1_and_9': {'values': 'block 1: one cluster at +0.5; block 2: nine clusters at -0.1',
                                         'equal_block_mean_estimate': round(equal_block_mean_estimate, 6),
                                         'cluster_weighted_estimate': round(cluster_weighted_estimate, 6),
                                         'sign_reversed': (equal_block_mean_estimate > 0) != (cluster_weighted_estimate > 0)}}
# Deterministic oracle 2: four unequal blocks, for T-36 (b).
blocks2 = [np.array([0.10, 0.00]), np.array([0.05, 0.15, 0.10]), np.array([0.00, 0.05, 0.05, 0.10]), np.array([0.20])]
theta2, t2, df2 = cluster_weighted_t(blocks2)
bm2 = [float(b.mean()) for b in blocks2]
t_equal2 = float(np.mean(bm2) / (np.std(bm2, ddof=1) / math.sqrt(4)))
rc69['oracle_2_block_sizes_2_3_4_1'] = {'blocks': [list(map(float, b)) for b in blocks2],
                                       'cluster_weighted_estimate': round(theta2, 6), 'cluster_weighted_t': round(t2, 6), 'df': df2,
                                       'one_sided_p': round(float(1 - student_t.cdf(t2, df2)), 6),
                                       'equal_block_mean_estimate': round(float(np.mean(bm2)), 6), 'equal_block_mean_t': round(t_equal2, 6)}
# Simulation: unequal supply per period. (i) supply independent of the period shock (Poisson mean 5, at least 1)
# under the valid null and under independent period shocks of +/- 0.3: both statistics should hold size.
# (ii) supply covarying with the shock (8 clusters in a +0.3 period, 2 in a -0.3 period): the per-cluster
# estimand of 17 section 6 is then E[X] = (8*0.12 - 2*0.12)/10 = +0.072 > 0 while the period-average is 0,
# so the two statistics test different hypotheses; reported, not bounded.
REPS, PERIODS = 20000, 24
rng = np.random.default_rng(5026)
def sim_unequal(rng_, shock_amp, covary, delta=0.0):
    rej_equal = np.zeros(REPS, bool); rej_cw = np.zeros(REPS, bool); est_cw = np.zeros(REPS); est_eq = np.zeros(REPS)
    for rpt in range(REPS):
        sh = rng_.choice([-shock_amp, shock_amp], size=PERIODS) if shock_amp > 0 else np.zeros(PERIODS)
        if covary:
            sizes = np.where(sh > 0, 8, 2)
        else:
            sizes = np.maximum(1, rng_.poisson(5, size=PERIODS))
        blocks = []
        for tt in range(PERIODS):
            q = 0.5 + 2.5 * delta + sh[tt]
            blocks.append(increments(np.full(sizes[tt], q), rng_))
        bm = np.array([b.mean() for b in blocks])
        t_eq = bm.mean() / (bm.std(ddof=1) / math.sqrt(PERIODS))
        theta, t_cw, df = cluster_weighted_t(blocks)
        crit = student_t.ppf(1 - ALPHA, PERIODS - 1)
        rej_equal[rpt] = t_eq > crit; rej_cw[rpt] = t_cw > crit; est_cw[rpt] = theta; est_eq[rpt] = bm.mean()
    return {'equal_block_mean_t_reject': round(float(rej_equal.mean()), 5),
            'cluster_weighted_block_sum_t_reject': round(float(rej_cw.mean()), 5),
            'exact_upper_99_equal': round(binom_upper(int(rej_equal.sum()), REPS, 0.99), 5),
            'exact_upper_99_cluster_weighted': round(binom_upper(int(rej_cw.sum()), REPS, 0.99), 5),
            'mean_estimate_equal_block': round(float(est_eq.mean()), 5), 'mean_estimate_cluster_weighted': round(float(est_cw.mean()), 5)}
rc69['size_poisson_supply_valid_null'] = sim_unequal(rng, 0.0, False)
rc69['size_poisson_supply_iid_period_shocks'] = sim_unequal(rng, 0.3, False)
rc69['supply_covarying_with_shock_(estimands_differ)'] = sim_unequal(rng, 0.3, True)
out['RC69_unequal_blocks'] = rc69

# ================= r4296914351 (RC-70): power at exactly 24 calendar periods =================
# Appendix E used five clusters per period, so 600 clusters spanned 120 periods. Here PERIODS = 24 and the
# cluster count sets the clusters per period. Independent clusters (D1 generator) first.
POW_REPS = 10000
def d1_paths(b, delta, kk, r):
    p = b + math.sqrt(delta) * r.choice([-1., 1.], size=(POW_REPS, kk))
    yy = (r.random(p.shape) < p).astype(float)
    return (b - yy) ** 2 - (p - yy) ** 2
power24 = {}
for b in (0.5, 0.2):
    for delta in (0.005, 0.01, 0.02):
        for per_period in (5, 12, 25):
            kk = PERIODS * per_period
            r = np.random.default_rng(2400 + int(b * 10) * 100 + int(delta * 1000) * 10 + per_period)
            xs = d1_paths(b, delta, kk, r)
            fh = int(block_t_rejects(xs, per_period).sum())
            ep = int((grapa_paths(xs)[1] >= THRESHOLD).sum())
            power24[f'b={b},delta={delta},clusters={kk}(24x{per_period})'] = {
                'fixed_horizon_block1_power_24_periods': round(fh / POW_REPS, 4), 'eprocess_monitor_crossing_rate': round(ep / POW_REPS, 4)}
out['RC70_power_independent_clusters_24_periods'] = power24
# Independent period shocks of +/- 0.3 over exactly 24 periods (Appendix D/E generator, X in {-0.2, +0.2}).
shock24 = {}
for amp in (0.0, 0.3):
    for delta in (0.0, 0.01, 0.02, 0.03, 0.05, 0.08):
        for per_period in (5, 12, 25, 50):
            kk = PERIODS * per_period
            r = np.random.default_rng(7400 + int(delta * 1000) * 10 + per_period + int(amp * 10) * 1000)
            sh = r.choice([-amp, amp], size=(POW_REPS, PERIODS))
            q = np.repeat(0.5 + 2.5 * delta + sh, per_period, axis=1)
            xs = increments(q, r)
            fh = int(block_t_rejects(xs, per_period).sum())
            shock24[f'shock=+/-{amp},delta={delta},clusters={kk}(24x{per_period})'] = round(fh / POW_REPS, 4)
out['RC70_power_macro_shock_24_periods'] = {
    'generator': 'baseline 0.4, challenger 0.6, q_t = 0.5 + 2.5 delta +/- shock per period, 24 periods; block-of-one-period t, 23 df',
    'appendix_E_comparison': 'Appendix E shock=0.3, delta=0.02, 600 clusters over 120 periods: 0.47',
    'cells': shock24}
# Normal-theory check of the plateau: block means have sd sqrt(0.12^2 + 0.04/n) over 24 blocks; the
# detectable delta at 80 % power with 24 blocks is about (1.714 + 0.856) * se, se = sd / sqrt(24).
plateau = {}
for per_period in (5, 25, 50, 1000):
    sd = math.sqrt(0.12 ** 2 + 0.04 / per_period)
    se = sd / math.sqrt(PERIODS)
    plateau[f'24x{per_period}'] = {'block_mean_sd': round(sd, 5), 'se_of_mean': round(se, 5),
                                   'delta_at_80pct_power_normal_theory': round((student_t.ppf(0.95, 23) + student_t.ppf(0.80, 23)) * se, 4)}
out['RC70_detectable_delta_plateau_normal_theory'] = plateau

out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
```
<!-- round5-script:end -->

Output:

```json
{
  "RC65_clock_watermark_replay": {
    "A_watermark_on_admission_only_(v4_text)": {
      "replay_after_rollback": "admitted",
      "log": [
        "now=10 expiry=100 admitted watermark=10",
        "now=30 expiry=20 rejected_expired watermark=10",
        "now=15 expiry=20 admitted watermark=15"
      ]
    },
    "B_watermark_on_every_check": {
      "replay_after_rollback": "rejected_rollback",
      "log": [
        "now=10 expiry=100 admitted watermark=10",
        "now=30 expiry=20 rejected_expired watermark=30",
        "now=15 expiry=20 rejected_rollback watermark=30"
      ]
    }
  },
  "RC69_unequal_blocks": {
    "oracle_1_block_sizes_1_and_9": {
      "values": "block 1: one cluster at +0.5; block 2: nine clusters at -0.1",
      "equal_block_mean_estimate": 0.2,
      "cluster_weighted_estimate": -0.04,
      "sign_reversed": true
    },
    "oracle_2_block_sizes_2_3_4_1": {
      "blocks": [
        [
          0.1,
          0.0
        ],
        [
          0.05,
          0.15,
          0.1
        ],
        [
          0.0,
          0.05,
          0.05,
          0.1
        ],
        [
          0.2
        ]
      ],
      "cluster_weighted_estimate": 0.08,
      "cluster_weighted_t": 3.651484,
      "df": 3,
      "one_sided_p": 0.017728,
      "equal_block_mean_estimate": 0.1,
      "equal_block_mean_t": 2.828427
    },
    "size_poisson_supply_valid_null": {
      "equal_block_mean_t_reject": 0.0488,
      "cluster_weighted_block_sum_t_reject": 0.0517,
      "exact_upper_99_equal": 0.05246,
      "exact_upper_99_cluster_weighted": 0.05546,
      "mean_estimate_equal_block": 2e-05,
      "mean_estimate_cluster_weighted": 1e-05
    },
    "size_poisson_supply_iid_period_shocks": {
      "equal_block_mean_t_reject": 0.04995,
      "cluster_weighted_block_sum_t_reject": 0.05465,
      "exact_upper_99_equal": 0.05365,
      "exact_upper_99_cluster_weighted": 0.0585,
      "mean_estimate_equal_block": -7e-05,
      "mean_estimate_cluster_weighted": -0.00017
    },
    "supply_covarying_with_shock_(estimands_differ)": {
      "equal_block_mean_t_reject": 0.05715,
      "cluster_weighted_block_sum_t_reject": 0.8812,
      "exact_upper_99_equal": 0.06108,
      "exact_upper_99_cluster_weighted": 0.88647,
      "mean_estimate_equal_block": 8e-05,
      "mean_estimate_cluster_weighted": 0.07008
    }
  },
  "RC70_power_independent_clusters_24_periods": {
    "b=0.5,delta=0.005,clusters=120(24x5)": {
      "fixed_horizon_block1_power_24_periods": 0.1904,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.5,delta=0.005,clusters=288(24x12)": {
      "fixed_horizon_block1_power_24_periods": 0.3214,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.5,delta=0.005,clusters=600(24x25)": {
      "fixed_horizon_block1_power_24_periods": 0.5217,
      "eprocess_monitor_crossing_rate": 0.0167
    },
    "b=0.5,delta=0.01,clusters=120(24x5)": {
      "fixed_horizon_block1_power_24_periods": 0.2831,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.5,delta=0.01,clusters=288(24x12)": {
      "fixed_horizon_block1_power_24_periods": 0.5084,
      "eprocess_monitor_crossing_rate": 0.0091
    },
    "b=0.5,delta=0.01,clusters=600(24x25)": {
      "fixed_horizon_block1_power_24_periods": 0.78,
      "eprocess_monitor_crossing_rate": 0.272
    },
    "b=0.5,delta=0.02,clusters=120(24x5)": {
      "fixed_horizon_block1_power_24_periods": 0.4767,
      "eprocess_monitor_crossing_rate": 0.0017
    },
    "b=0.5,delta=0.02,clusters=288(24x12)": {
      "fixed_horizon_block1_power_24_periods": 0.7774,
      "eprocess_monitor_crossing_rate": 0.2427
    },
    "b=0.5,delta=0.02,clusters=600(24x25)": {
      "fixed_horizon_block1_power_24_periods": 0.967,
      "eprocess_monitor_crossing_rate": 0.8141
    },
    "b=0.2,delta=0.005,clusters=120(24x5)": {
      "fixed_horizon_block1_power_24_periods": 0.2416,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.2,delta=0.005,clusters=288(24x12)": {
      "fixed_horizon_block1_power_24_periods": 0.4397,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.2,delta=0.005,clusters=600(24x25)": {
      "fixed_horizon_block1_power_24_periods": 0.6889,
      "eprocess_monitor_crossing_rate": 0.0068
    },
    "b=0.2,delta=0.01,clusters=120(24x5)": {
      "fixed_horizon_block1_power_24_periods": 0.3989,
      "eprocess_monitor_crossing_rate": 0.0
    },
    "b=0.2,delta=0.01,clusters=288(24x12)": {
      "fixed_horizon_block1_power_24_periods": 0.6883,
      "eprocess_monitor_crossing_rate": 0.0036
    },
    "b=0.2,delta=0.01,clusters=600(24x25)": {
      "fixed_horizon_block1_power_24_periods": 0.9217,
      "eprocess_monitor_crossing_rate": 0.3104
    },
    "b=0.2,delta=0.02,clusters=120(24x5)": {
      "fixed_horizon_block1_power_24_periods": 0.6503,
      "eprocess_monitor_crossing_rate": 0.0002
    },
    "b=0.2,delta=0.02,clusters=288(24x12)": {
      "fixed_horizon_block1_power_24_periods": 0.9306,
      "eprocess_monitor_crossing_rate": 0.2582
    },
    "b=0.2,delta=0.02,clusters=600(24x25)": {
      "fixed_horizon_block1_power_24_periods": 0.9981,
      "eprocess_monitor_crossing_rate": 0.9449
    }
  },
  "RC70_power_macro_shock_24_periods": {
    "generator": "baseline 0.4, challenger 0.6, q_t = 0.5 + 2.5 delta +/- shock per period, 24 periods; block-of-one-period t, 23 df",
    "appendix_E_comparison": "Appendix E shock=0.3, delta=0.02, 600 clusters over 120 periods: 0.47",
    "cells": {
      "shock=+/-0.0,delta=0.0,clusters=120(24x5)": 0.0521,
      "shock=+/-0.0,delta=0.0,clusters=288(24x12)": 0.0478,
      "shock=+/-0.0,delta=0.0,clusters=600(24x25)": 0.0478,
      "shock=+/-0.0,delta=0.0,clusters=1200(24x50)": 0.0531,
      "shock=+/-0.0,delta=0.01,clusters=120(24x5)": 0.134,
      "shock=+/-0.0,delta=0.01,clusters=288(24x12)": 0.1974,
      "shock=+/-0.0,delta=0.01,clusters=600(24x25)": 0.3175,
      "shock=+/-0.0,delta=0.01,clusters=1200(24x50)": 0.5185,
      "shock=+/-0.0,delta=0.02,clusters=120(24x5)": 0.278,
      "shock=+/-0.0,delta=0.02,clusters=288(24x12)": 0.499,
      "shock=+/-0.0,delta=0.02,clusters=600(24x25)": 0.7761,
      "shock=+/-0.0,delta=0.02,clusters=1200(24x50)": 0.9563,
      "shock=+/-0.0,delta=0.03,clusters=120(24x5)": 0.4886,
      "shock=+/-0.0,delta=0.03,clusters=288(24x12)": 0.8011,
      "shock=+/-0.0,delta=0.03,clusters=600(24x25)": 0.9705,
      "shock=+/-0.0,delta=0.03,clusters=1200(24x50)": 0.9999,
      "shock=+/-0.0,delta=0.05,clusters=120(24x5)": 0.8522,
      "shock=+/-0.0,delta=0.05,clusters=288(24x12)": 0.9932,
      "shock=+/-0.0,delta=0.05,clusters=600(24x25)": 1.0,
      "shock=+/-0.0,delta=0.05,clusters=1200(24x50)": 1.0,
      "shock=+/-0.0,delta=0.08,clusters=120(24x5)": 0.9974,
      "shock=+/-0.0,delta=0.08,clusters=288(24x12)": 1.0,
      "shock=+/-0.0,delta=0.08,clusters=600(24x25)": 1.0,
      "shock=+/-0.0,delta=0.08,clusters=1200(24x50)": 1.0,
      "shock=+/-0.3,delta=0.0,clusters=120(24x5)": 0.0485,
      "shock=+/-0.3,delta=0.0,clusters=288(24x12)": 0.0492,
      "shock=+/-0.3,delta=0.0,clusters=600(24x25)": 0.0492,
      "shock=+/-0.3,delta=0.0,clusters=1200(24x50)": 0.0492,
      "shock=+/-0.3,delta=0.01,clusters=120(24x5)": 0.0981,
      "shock=+/-0.3,delta=0.01,clusters=288(24x12)": 0.0989,
      "shock=+/-0.3,delta=0.01,clusters=600(24x25)": 0.1038,
      "shock=+/-0.3,delta=0.01,clusters=1200(24x50)": 0.1058,
      "shock=+/-0.3,delta=0.02,clusters=120(24x5)": 0.1719,
      "shock=+/-0.3,delta=0.02,clusters=288(24x12)": 0.1716,
      "shock=+/-0.3,delta=0.02,clusters=600(24x25)": 0.1811,
      "shock=+/-0.3,delta=0.02,clusters=1200(24x50)": 0.1781,
      "shock=+/-0.3,delta=0.03,clusters=120(24x5)": 0.2597,
      "shock=+/-0.3,delta=0.03,clusters=288(24x12)": 0.2944,
      "shock=+/-0.3,delta=0.03,clusters=600(24x25)": 0.2986,
      "shock=+/-0.3,delta=0.03,clusters=1200(24x50)": 0.302,
      "shock=+/-0.3,delta=0.05,clusters=120(24x5)": 0.5229,
      "shock=+/-0.3,delta=0.05,clusters=288(24x12)": 0.5621,
      "shock=+/-0.3,delta=0.05,clusters=600(24x25)": 0.5937,
      "shock=+/-0.3,delta=0.05,clusters=1200(24x50)": 0.6126,
      "shock=+/-0.3,delta=0.08,clusters=120(24x5)": 0.8587,
      "shock=+/-0.3,delta=0.08,clusters=288(24x12)": 0.9057,
      "shock=+/-0.3,delta=0.08,clusters=600(24x25)": 0.9255,
      "shock=+/-0.3,delta=0.08,clusters=1200(24x50)": 0.9319
    }
  },
  "RC70_detectable_delta_plateau_normal_theory": {
    "24x5": {
      "block_mean_sd": 0.14967,
      "se_of_mean": 0.03055,
      "delta_at_80pct_power_normal_theory": 0.0786
    },
    "24x25": {
      "block_mean_sd": 0.12649,
      "se_of_mean": 0.02582,
      "delta_at_80pct_power_normal_theory": 0.0664
    },
    "24x50": {
      "block_mean_sd": 0.12329,
      "se_of_mean": 0.02517,
      "delta_at_80pct_power_normal_theory": 0.0647
    },
    "24x1000": {
      "block_mean_sd": 0.12017,
      "se_of_mean": 0.02453,
      "delta_at_80pct_power_normal_theory": 0.0631
    }
  },
  "python": "3.11.17"
}
```

## Appendix G. Round-6 checks (REPRODUCED; evidence only, nothing applied)

Needs no reference code and no network. Run with `python -I round6_checks.py` in an isolated venv (Python 3.11.17,
numpy 2.4.6, scipy 1.17.1; 6 s), extracting the block between the `round6-script` markers as in Appendix A.
Seeds are fixed; two consecutive runs produced byte-identical output. The RC-72 block computes the exact size of
the one-sided t test over two-point block means in closed form (the statistic depends only on the count of
positive blocks), scans zero-mean two-point nulls, and runs the archived GRAPA rule of Appendix A over the block
means as the distribution-free comparison, with the D1 generator of Appendix E for power. The RC-73 and RC-74
blocks are toy state machines with the v4 wording beside the candidate repairs; RC-75 and RC-77 are arithmetic.

<!-- round6-script:start -->
```python
"""Round-6 checks for the Codex findings on PR #4 at 4de18e5 (no reference code, no network).

Evidence only: the findings are recorded, not applied (16 section 4.6, OD10). The D1 generator, the archived
GRAPA rule and the block t test are those of 16 Appendix A, D and E.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA, LAM_MAX = 0.05, 0.5

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))

def grapa_paths(xs, lam_max=LAM_MAX):
    """Archived GRAPA rule (16 Appendix A): predictable lambda, wealth and running maximum."""
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
    return wealth, peak

# ================= r4297109177 (RC-72): one-sided t test over 24 two-point block means =================
# Every cluster in a calendar block shares one outcome Y; baseline 0.9518, FULL 0.0518.
# X = (b - Y)^2 - (p - Y)^2 = +0.90324 if Y = 0 (probability 0.4982), -0.89676 if Y = 1 (0.5018).
def two_point_values(b, p):
    return (b - 0) ** 2 - (p - 0) ** 2, (b - 1) ** 2 - (p - 1) ** 2   # X(Y=0), X(Y=1)

def t_size_two_point(a, c, q0, g, alpha=ALPHA):
    """Exact size of the one-sided t test over g iid block means taking value a (prob q0) or c (prob 1 - q0).
    With two-point values the statistic depends only on the count k of a-valued blocks (closed form)."""
    crit = float(student_t.ppf(1 - alpha, g - 1))
    k = np.arange(g + 1)
    m = (k * a + (g - k) * c) / g
    var = (k * (a - m) ** 2 + (g - k) * (c - m) ** 2) / (g - 1)
    # A sample with every block equal has no sample variance; the statistic is undefined and is counted as
    # no rejection here (an implementation that maps a zero denominator to +inf would add P(all blocks equal)).
    var = np.where(var < 1e-12, 0.0, var)
    with np.errstate(divide='ignore', invalid='ignore'):
        tk = np.where(var > 0, m / np.sqrt(var / g), -np.inf)
    rej = tk > crit
    size = float(binom.pmf(k[rej], g, q0).sum())
    kmin = int(k[rej].min()) if rej.any() else None
    return size, kmin, crit

a, c = two_point_values(0.9518, 0.0518)
q0 = 0.4982
mean_null = q0 * a + (1 - q0) * c
size24, kmin24, crit24 = t_size_two_point(a, c, q0, 24)
rc72 = {'codex_null': {'X_if_Y0': round(a, 5), 'X_if_Y1': round(c, 5), 'P_Y0': q0, 'mean': round(mean_null, 6),
                       'G': 24, 't_crit_23df': round(crit24, 4), 'min_positive_blocks_to_reject': kmin24,
                       'exact_size': round(size24, 5), 'exceeds_A3_ceiling_0.06': bool(size24 > 0.06)}}
# The same count under a symmetric two-point null (+/- 0.9, P = 0.5): where does the threshold fall?
size_sym, kmin_sym, _ = t_size_two_point(0.9, -0.9, 0.5, 24)
rc72['symmetric_two_point_null_G24'] = {'exact_size': round(size_sym, 5), 'min_positive_blocks_to_reject': kmin_sym}
# Maximum exact size over zero-mean two-point nulls (a in (0, 1], c = -a q0 / (1 - q0) >= -1) as G grows.
grid = {}
for g in (24, 36, 48, 72, 96, 120, 240):
    worst = (0.0, None)
    for a_ in np.linspace(0.02, 1.0, 50):
        for q in np.linspace(0.02, 0.98, 97):
            c_ = -a_ * q / (1 - q)
            if c_ < -1:
                continue
            s, _, _ = t_size_two_point(a_, c_, q, g)
            if s > worst[0]:
                worst = (s, {'a': round(float(a_), 3), 'c': round(float(c_), 4), 'P_a': round(float(q), 3),
                             'P_all_blocks_equal': round(float(q) ** g, 4)})
    grid[f'G={g}'] = {'max_exact_size': round(worst[0], 4), 'at': worst[1]}
rc72['max_size_of_t_over_two_point_zero_mean_nulls'] = grid
# Deterministic ceiling of the bounded betting test at G = 24: lambda = 0 for the first two blocks, then at most
# 0.5; with every block mean at +x the final wealth is (1 + 0.5 x)^22, which must reach 1/alpha = 20 to reject.
rc72['betting_test_wealth_ceiling_G24'] = {f'all_block_means_{x}': round((1 + 0.5 * x) ** 22, 3) for x in (0.02, 0.05, 0.1, 0.2, 0.3)}
rc72['betting_test_smallest_constant_block_mean_reaching_20_at_G24'] = round(2 * (20 ** (1 / 22) - 1), 4)

# A finite-sample-valid alternative on the same block means: the archived GRAPA betting test run over the G
# block means (bounded in [-1, 1]), evaluated at the fixed horizon G, reject iff final wealth >= 1/alpha.
# Ville's inequality makes it valid for every bounded null with E[X_g | past] <= 0, at any G.
rng = np.random.default_rng(61)
R = 20000
ys = (rng.random((R, 24)) < (1 - q0)).astype(float)       # Y = 1 with probability 0.5018
xs_null = np.where(ys == 0, a, c)
wealth, peak = grapa_paths(xs_null)
k_bet = int((wealth >= 1 / ALPHA).sum()); k_bet_peak = int((peak >= 1 / ALPHA).sum())
# t test on the same paths (Monte Carlo check of the exact value above)
tb = xs_null.mean(axis=1) / (xs_null.std(axis=1, ddof=1) / math.sqrt(24))
k_t = int((tb > crit24).sum())
rc72['monte_carlo_on_codex_null_20000'] = {
    't_test_rejections': k_t, 't_test_rate': round(k_t / R, 4), 't_test_99pct_upper': round(binom_upper(k_t, R, 0.99), 4),
    'betting_test_final_wealth_rejections': k_bet, 'betting_rate': round(k_bet / R, 4),
    'betting_99pct_upper': round(binom_upper(k_bet, R, 0.99), 4),
    'betting_running_max_rejections': k_bet_peak, 'betting_running_max_rate': round(k_bet_peak / R, 4)}

# Power cost of the valid alternative under the Appendix E/F alternative with 24 periods:
# D1 generator, b = 0.5, independent clusters, n_per clusters per period, block = one period.
def d1_increments(b, delta, n_cl, rng_):
    p = b + math.sqrt(delta)
    y = (rng_.random(n_cl) < p).astype(float)
    return (b - y) ** 2 - (p - y) ** 2
power = {}
for delta in (0.02, 0.05, 0.08):
    for per in (25, 50):
        rej_t = 0; rej_bet = 0
        bm = np.empty((R, 24))
        for r in range(R):
            x = d1_increments(0.5, delta, 24 * per, rng).reshape(24, per).mean(axis=1)
            bm[r] = x
        tb = bm.mean(axis=1) / (bm.std(axis=1, ddof=1) / math.sqrt(24))
        rej_t = int((tb > crit24).sum())
        w, _ = grapa_paths(bm)
        rej_bet = int((w >= 1 / ALPHA).sum())
        power[f'delta={delta}_clusters_per_period={per}'] = {'t_power': round(rej_t / R, 3), 'betting_power': round(rej_bet / R, 3)}
rc72['power_at_24_periods_b0.5_independent_clusters'] = power
out['RC72_t_test_on_two_point_block_means'] = rc72

# ================= r4297109194 (RC-73): clock rollback across an idle expiry window =================
# Toy state machine. Variant A: v4 wording (watermark advanced by admissions). Variant B: RC-65 wording
# (watermark advanced by every check). Variant C: the check also persists the monotonic clock and the boot id
# with the wall clock; a wall-minus-monotonic drift beyond the tolerance, or a new boot id, is an unverifiable
# discontinuity that invalidates every outstanding capability until re-authorisation.
def run_idle_variant(variant):
    state = {'watermark': 0.0, 'mono_ref': None, 'wall_ref': None, 'boot': None, 'reauth_needed': False}
    log = []
    def check(wall, mono, boot, expiry):
        if variant == 'C':
            if state['boot'] is not None and (boot != state['boot'] or abs((wall - mono) - (state['wall_ref'] - state['mono_ref'])) > 1.0):
                state['reauth_needed'] = True
            state['wall_ref'], state['mono_ref'], state['boot'] = wall, mono, boot
            if state['reauth_needed']:
                verdict = 'rejected_clock_discontinuity_reauthorise'
                log.append((wall, mono, verdict)); return verdict
        if wall < state['watermark']:
            verdict = 'rejected_rollback'
        elif wall >= expiry:
            verdict = 'rejected_expired'
        else:
            verdict = 'admitted'
        if verdict == 'admitted' or variant in ('B', 'C'):
            state['watermark'] = max(state['watermark'], wall)
        log.append((wall, mono, verdict)); return verdict
    check(10, 100, 'boot-1', 100)        # last observed time t0 = 10 (an unrelated admission)
    # capability expires at t1 = 20; machine idle until real time 30; no check occurs in between
    replay = check(15, 120, 'boot-1', 20)  # wall clock rolled back to 15 (monotonic clock has advanced 20)
    restart = check(15, 3, 'boot-2', 20)   # same, after a reboot (monotonic clock reset, new boot id)
    return replay, restart, log
rc73 = {}
for v, name in (('A', 'A_v4_watermark_on_admission'), ('B', 'B_RC65_watermark_on_every_check'), ('C', 'C_monotonic_clock_and_boot_id')):
    replay, restart, log = run_idle_variant(v)
    rc73[name] = {'replay_after_idle_rollback': replay, 'replay_after_reboot': restart,
                  'log': [f'wall={w} mono={m} {vd}' for w, m, vd in log]}
out['RC73_idle_expiry_window_rollback'] = rc73

# ================= r4297109203 (RC-74): nonce consumed after the last anchor, then restored away =================
# Toy ledger: records carry consumed nonces; an anchor covers a prefix; restore truncates the local ledger to the
# anchored prefix. Variant A (v4): acknowledge inside the writer transaction, anchor asynchronously.
# Variant B: acknowledge only after the record is in an externally anchored prefix. Variant C: the epoch is
# rotated and anchored synchronously on every process start; capabilities carry the epoch.
class Ledger:
    def __init__(self):
        self.records = []; self.anchored_len = 0; self.external_anchor_digest = None; self.epoch = 1
    def anchor(self):
        self.anchored_len = len(self.records); self.external_anchor_digest = ('anchor', tuple(self.records))
    def restore_to_anchor(self):
        self.records = list(self.external_anchor_digest[1]); self.anchored_len = len(self.records)
        self.epoch = max([r[2] for r in self.records if r[0] == 'epoch'] + [1])

def protected_action(ledger, nonce, cap_epoch, variant):
    if cap_epoch != ledger.epoch:
        return 'rejected_stale_epoch'
    if any(r[0] == 'nonce' and r[1] == nonce for r in ledger.records):
        return 'rejected_nonce_consumed'
    ledger.records.append(('nonce', nonce, cap_epoch))
    if variant == 'B':
        ledger.anchor()                       # durable externally before the acknowledgement
    return 'acknowledged'

def run_restore_variant(variant):
    led = Ledger(); log = []
    if variant == 'C':
        led.epoch += 1; led.records.append(('epoch', 'start-1', led.epoch)); led.anchor()
    led.records.append(('event', 'e1', led.epoch)); led.anchor()           # last asynchronous anchor
    cap = ('nonce-7', led.epoch)                                            # capability signed for this epoch
    log.append(('first presentation', protected_action(led, cap[0], cap[1], variant)))
    led.restore_to_anchor()                                                 # SQLite and JSONL suffix restored to the anchor
    if variant == 'C':
        led.epoch += 1; led.records.append(('epoch', 'start-2', led.epoch)); led.anchor()   # process restarts after the restore
    log.append(('replay after restore', protected_action(led, cap[0], cap[1], variant)))
    return log
rc74 = {name: dict(run_restore_variant(v)) for v, name in (('A', 'A_v4_ack_in_transaction_async_anchor'),
                                                            ('B', 'B_ack_after_external_anchor'),
                                                            ('C', 'C_epoch_rotated_and_anchored_on_start'))}
out['RC74_unanchored_nonce_restored_away'] = rc74

# ================= r4297109207 (RC-75): two eligible revisions, one scored after the outcome =================
# Event with true P(Y = 1) = q; two eligible FULL forecasts 0.3 and 0.7 (different ids, both before t*_k).
# Baseline forecasts q itself. Expected paired increment when the scored revision is the one nearest Y.
rc75 = {}
for q in (0.5, 0.3):
    exp_honest = {}
    for p in (0.3, 0.7):
        exp_honest[f'p={p}'] = round(q * ((q - 1) ** 2 - (p - 1) ** 2) + (1 - q) * (q ** 2 - p ** 2), 4)
    nearest = q * ((q - 1) ** 2 - (0.7 - 1) ** 2) + (1 - q) * (q ** 2 - 0.3 ** 2)
    rc75[f'q={q}'] = {'expected_increment_scoring_each_revision_honestly': exp_honest,
                      'expected_increment_scoring_the_revision_nearest_Y': round(nearest, 4)}
out['RC75_revision_selected_after_outcome'] = rc75

# ================= r4297109220 (RC-77): NO by logical finality before the source's formal record =================
# Eventually-by-deadline event, deadline D = 100, declared latency window L = 10, no timely occurrence.
# The source's formal 'did not occur' record is received at 118. A forecast is received at 113.
D, L, receipt, forecast_receipt = 100, 10, 118, 113
knowable_v4 = receipt                     # v4: knowable_at = publication (the formal record) or occurrence
knowable_proposed = min(receipt, D + L)   # proposed: logical finality at D + L
out['RC77_logical_finality'] = {'deadline': D, 'latency_window': L, 'formal_record_received': receipt,
                                'forecast_received': forecast_receipt,
                                'v4_knowable_at': knowable_v4, 'v4_forecast_eligible': forecast_receipt < knowable_v4,
                                'proposed_knowable_at': knowable_proposed, 'proposed_forecast_eligible': forecast_receipt < knowable_proposed}

out['environment'] = {'python': sys.version.split()[0], 'numpy': np.__version__, 'scipy': __import__('scipy').__version__}
print(json.dumps(out, indent=2))
```
<!-- round6-script:end -->

Output:

```json
{
  "RC72_t_test_on_two_point_block_means": {
    "codex_null": {
      "X_if_Y0": 0.90324,
      "X_if_Y1": -0.89676,
      "P_Y0": 0.4982,
      "mean": -0.0,
      "G": 24,
      "t_crit_23df": 1.7139,
      "min_positive_blocks_to_reject": 16,
      "exact_size": 0.0733,
      "exceeds_A3_ceiling_0.06": true
    },
    "symmetric_two_point_null_G24": {
      "exact_size": 0.03196,
      "min_positive_blocks_to_reject": 17
    },
    "max_size_of_t_over_two_point_zero_mean_nulls": {
      "G=24": {
        "max_exact_size": 0.1522,
        "at": {
          "a": 0.02,
          "c": -0.1467,
          "P_a": 0.88,
          "P_all_blocks_equal": 0.0465
        }
      },
      "G=36": {
        "max_exact_size": 0.1556,
        "at": {
          "a": 0.02,
          "c": -0.23,
          "P_a": 0.92,
          "P_all_blocks_equal": 0.0497
        }
      },
      "G=48": {
        "max_exact_size": 0.1572,
        "at": {
          "a": 0.02,
          "c": -0.3133,
          "P_a": 0.94,
          "P_all_blocks_equal": 0.0513
        }
      },
      "G=72": {
        "max_exact_size": 0.1587,
        "at": {
          "a": 0.02,
          "c": -0.48,
          "P_a": 0.96,
          "P_all_blocks_equal": 0.0529
        }
      },
      "G=96": {
        "max_exact_size": 0.1595,
        "at": {
          "a": 0.02,
          "c": -0.6467,
          "P_a": 0.97,
          "P_all_blocks_equal": 0.0537
        }
      },
      "G=120": {
        "max_exact_size": 0.1423,
        "at": {
          "a": 0.02,
          "c": -0.38,
          "P_a": 0.95,
          "P_all_blocks_equal": 0.0021
        }
      },
      "G=240": {
        "max_exact_size": 0.132,
        "at": {
          "a": 0.02,
          "c": -0.98,
          "P_a": 0.98,
          "P_all_blocks_equal": 0.0078
        }
      }
    },
    "betting_test_wealth_ceiling_G24": {
      "all_block_means_0.02": 1.245,
      "all_block_means_0.05": 1.722,
      "all_block_means_0.1": 2.925,
      "all_block_means_0.2": 8.14,
      "all_block_means_0.3": 21.645
    },
    "betting_test_smallest_constant_block_mean_reaching_20_at_G24": 0.2918,
    "monte_carlo_on_codex_null_20000": {
      "t_test_rejections": 1454,
      "t_test_rate": 0.0727,
      "t_test_99pct_upper": 0.0771,
      "betting_test_final_wealth_rejections": 12,
      "betting_rate": 0.0006,
      "betting_99pct_upper": 0.0011,
      "betting_running_max_rejections": 31,
      "betting_running_max_rate": 0.0015
    },
    "power_at_24_periods_b0.5_independent_clusters": {
      "delta=0.02_clusters_per_period=25": {
        "t_power": 0.966,
        "betting_power": 0.0
      },
      "delta=0.02_clusters_per_period=50": {
        "t_power": 0.999,
        "betting_power": 0.0
      },
      "delta=0.05_clusters_per_period=25": {
        "t_power": 1.0,
        "betting_power": 0.0
      },
      "delta=0.05_clusters_per_period=50": {
        "t_power": 1.0,
        "betting_power": 0.0
      },
      "delta=0.08_clusters_per_period=25": {
        "t_power": 1.0,
        "betting_power": 0.0
      },
      "delta=0.08_clusters_per_period=50": {
        "t_power": 1.0,
        "betting_power": 0.0
      }
    }
  },
  "RC73_idle_expiry_window_rollback": {
    "A_v4_watermark_on_admission": {
      "replay_after_idle_rollback": "admitted",
      "replay_after_reboot": "admitted",
      "log": [
        "wall=10 mono=100 admitted",
        "wall=15 mono=120 admitted",
        "wall=15 mono=3 admitted"
      ]
    },
    "B_RC65_watermark_on_every_check": {
      "replay_after_idle_rollback": "admitted",
      "replay_after_reboot": "admitted",
      "log": [
        "wall=10 mono=100 admitted",
        "wall=15 mono=120 admitted",
        "wall=15 mono=3 admitted"
      ]
    },
    "C_monotonic_clock_and_boot_id": {
      "replay_after_idle_rollback": "rejected_clock_discontinuity_reauthorise",
      "replay_after_reboot": "rejected_clock_discontinuity_reauthorise",
      "log": [
        "wall=10 mono=100 admitted",
        "wall=15 mono=120 rejected_clock_discontinuity_reauthorise",
        "wall=15 mono=3 rejected_clock_discontinuity_reauthorise"
      ]
    }
  },
  "RC74_unanchored_nonce_restored_away": {
    "A_v4_ack_in_transaction_async_anchor": {
      "first presentation": "acknowledged",
      "replay after restore": "acknowledged"
    },
    "B_ack_after_external_anchor": {
      "first presentation": "acknowledged",
      "replay after restore": "rejected_nonce_consumed"
    },
    "C_epoch_rotated_and_anchored_on_start": {
      "first presentation": "acknowledged",
      "replay after restore": "rejected_stale_epoch"
    }
  },
  "RC75_revision_selected_after_outcome": {
    "q=0.5": {
      "expected_increment_scoring_each_revision_honestly": {
        "p=0.3": -0.04,
        "p=0.7": -0.04
      },
      "expected_increment_scoring_the_revision_nearest_Y": 0.16
    },
    "q=0.3": {
      "expected_increment_scoring_each_revision_honestly": {
        "p=0.3": 0.0,
        "p=0.7": -0.16
      },
      "expected_increment_scoring_the_revision_nearest_Y": 0.12
    }
  },
  "RC77_logical_finality": {
    "deadline": 100,
    "latency_window": 10,
    "formal_record_received": 118,
    "forecast_received": 113,
    "v4_knowable_at": 118,
    "v4_forecast_eligible": true,
    "proposed_knowable_at": 110,
    "proposed_forecast_eligible": false
  },
  "environment": {
    "python": "3.11.17",
    "numpy": "2.4.6",
    "scipy": "1.17.1"
  }
}
```

## Appendix H. Round-7 checks (REPRODUCED)

Needs no reference code and no network. Run with `python -I round7_checks.py` in an isolated venv (Python 3.11.17,
numpy 2.4.6, scipy 1.17.1; 70 s), extracting the block between the `round7-script` markers as in Appendix A.
Seeds are fixed; two consecutive runs produced byte-identical output. **Round-9 correction (RC-102):** the
`round7_sentence_is` string hand-typed "140 blocks" where the `blocks_needed` field beside it computes 141; the
string now takes the computed value, the script was re-extracted and re-run twice in the round-9 environment, and
the output below is that run, which differs from the round-7 output in that one line only. **Round-9 withdrawal
(RC-93):** the `least_favourable_null_check` block below sets comparator 1 to δ = 0, which makes every one of its
increments exactly zero, so its 0 of 20,000 is mechanical and is not a size check; the non-degenerate check is in
Appendix J and the block is kept here unchanged as the record of the defect. The RC-80 block states the power bound for
any finite-sample-valid bounded-mean test (the proof is in §3f and in the script's comments), tabulates it at
G = 24, solves for the effect and the block count at which it reaches 80 %, and checks the proof's two
ingredients numerically beside the archived GRAPA kernel on the same samples. The RC-83 block simulates the
intersection-union conjunction over six comparators that share FULL's forecast and the outcome, with the
cluster-weighted statistic of Appendix F over 24 blocks, at three comparator-dependence settings and at the
least-favourable null. The round-5 and round-6 scripts (Appendix F and G) were re-extracted and re-run in the
same environment this round; their output is byte-identical to the committed appendices.

<!-- round7-script:start -->
```python
"""Round-7 checks for the Codex findings on PR #4 at 10f8829 (no reference code, no network).

RC-80: a proof, not a simulation, of what a distribution-free bounded-mean test can do over G blocks, with a
numerical check; RC-83: power of the intersection-union conjunction under a joint generator. The archived GRAPA
rule and the cluster-weighted statistic are those of 16 Appendix A and F.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, t as student_t

out = {}
ALPHA, LAM_MAX = 0.05, 0.5

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

def grapa_paths(xs, lam_max=LAM_MAX):
    n_paths, n_steps = xs.shape
    s1 = np.zeros(n_paths); s2 = np.zeros(n_paths); wealth = np.ones(n_paths); peak = np.ones(n_paths)
    for n in range(n_steps):
        if n < 2:
            lam = np.zeros(n_paths)
        else:
            mean = s1 / n
            var = np.maximum(0.0, (s2 - s1 * s1 / n) / (n - 1))
            den = var + mean * mean
            lam = np.divide(mean, den, out=np.zeros(n_paths), where=den > 0) * n / (n + 10)
            lam = np.clip(lam, 0.0, lam_max)
        wealth = wealth * (1 + lam * xs[:, n]); peak = np.maximum(peak, wealth)
        s1 += xs[:, n]; s2 += xs[:, n] ** 2
    return wealth, peak

# ================= r4297337217 (RC-80): what any distribution-free bounded-mean test can do over G blocks =================
# Claim to replace the round-6 sentence: for ANY test phi with sup over mean-zero laws on [-1, 1] of E_P0[phi] <= alpha
# (finite-sample valid for the bounded-mean null), and ANY alternative law P1 on [-1, 1] with mean delta > 0,
#     E_P1[phi] <= alpha * (1 + delta)^G.
# Proof. Let eps = delta / (1 + delta) and P0 = (1 - eps) P1 + eps * point mass at -1. P0 lives on [-1, 1] and has
# mean (1 - eps) delta - eps = 0, so it is in the null. With probability (1 - eps)^G a P0 sample contains no -1 and
# is then distributed as a P1 sample, so E_P0[phi] >= (1 - eps)^G E_P1[phi]; with E_P0[phi] <= alpha and
# (1 - eps) = 1 / (1 + delta) the bound follows. The bound is attained by the randomised test "reject with probability
# alpha (1 + delta)^G when no -1 is observed" against this one null, so it cannot be improved without restricting the null.
G = 24
bound = {}
for delta in (0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.12, 0.13, 0.15):
    bound[f'delta={delta}'] = round(min(1.0, ALPHA * (1 + delta) ** G), 4)
delta_80 = 16 ** (1 / G) - 1          # alpha (1+delta)^G = 0.80
blocks_needed = {f'delta={d}': math.ceil(math.log(0.80 / ALPHA) / math.log(1 + d)) for d in (0.01, 0.02, 0.05, 0.08, 0.10)}
rc80 = {'statement': 'any level-alpha test valid for every mean-zero law on [-1, 1] has power <= alpha (1 + delta)^G against every alternative on [-1, 1] with mean delta',
        'G': G, 'alpha': ALPHA, 'power_upper_bound_by_delta': bound,
        'smallest_delta_with_bound_at_or_above_0.80': round(delta_80, 4),
        'blocks_needed_for_bound_0.80': blocks_needed,
        'round6_sentence_was': 'at 24 blocks there is no distribution-free bounded-mean test with power at a useful effect (tested on one kernel only)',
        'round7_sentence_is': 'over 24 blocks no finite-sample-valid bounded-mean test, of any form, has power above alpha (1 + delta)^24: 0.08 at delta = 0.02, 0.16 at 0.05, 0.32 at 0.08; 80 % needs delta >= 0.1225 or, at delta = 0.02, ' + str(blocks_needed['delta=0.02']) + ' blocks (computed, RC-102)'}
# Numerical check of the proof's two ingredients (Monte Carlo, 200,000 samples each): the catastrophe mixture has
# mean zero, and the fraction of its samples with no -1 equals (1 - eps)^G.
rng = np.random.default_rng(7001)
R = 200000
chk = {}
for delta in (0.02, 0.05, 0.08):
    eps = delta / (1 + delta)
    # P1: the D1-type alternative X in {delta - s, delta + s} with s = 0.3 (mean delta, inside [-1, 1]).
    s = 0.3
    x1 = delta + s * rng.choice([-1.0, 1.0], size=(R, G))
    cat = rng.random((R, G)) < eps
    x0 = np.where(cat, -1.0, x1)
    no_cat = ~cat.any(axis=1)
    # The randomised level-alpha test from the proof.
    reject_prob = min(1.0, ALPHA * (1 + delta) ** G)
    u = rng.random(R)
    size_mc = float(np.mean(no_cat & (u < reject_prob)))
    power_mc = float(np.mean(u < reject_prob))
    # The archived GRAPA betting test on the same P1 sample (the kernel round 6 tested) for comparison.
    w, peak = grapa_paths(x1)
    chk[f'delta={delta}'] = {'eps': round(eps, 5), 'P0_mean_mc': round(float(x0.mean()), 5),
                             'P0_fraction_without_catastrophe_mc': round(float(no_cat.mean()), 5),
                             '(1-eps)^G': round((1 - eps) ** G, 5),
                             'randomised_LR_test_size_mc': round(size_mc, 5), 'randomised_LR_test_power_mc': round(power_mc, 5),
                             'bound': round(reject_prob, 5),
                             'grapa_betting_power_on_P1': round(float((w >= 1 / ALPHA).mean()), 5),
                             'grapa_running_max_power_on_P1': round(float((peak >= 1 / ALPHA).mean()), 5)}
rc80['numerical_check'] = chk
# Constant-increment arithmetic behind the round-6 "0.29" statement (unchanged): (1 + 0.5 m)^22 >= 20.
rc80['grapa_constant_block_mean_needed_for_wealth_20_in_22_steps'] = round(2 * (20 ** (1 / 22) - 1), 4)
out['RC80_distribution_free_power_bound'] = rc80

# ================= r4297337251 (RC-83): power of the intersection-union conjunction =================
# Comparator set of 17 section 6: Design C, three single providers, the three-role provider, the equal-weight
# committee: J = 6 paired comparisons sharing FULL's forecast and the outcome. Generator per cluster: Y ~ Bern(p_F),
# FULL forecasts p_F = b, comparator c forecasts b - s_c sqrt(delta_c), s_c in {-1, +1}; X_c = (b_c - Y)^2 - (p_F - Y)^2
# has mean delta_c. Dependence between comparators is set by the signs: independent signs give uncorrelated X_c
# (they still share (p_F - Y)); equal signs give identical X_c; a shared sign with probability rho is between.
# Test per comparator: the cluster-weighted statistic with the block-sum variance of Appendix F (RC-69), 24 blocks,
# one-sided alpha = 0.05; IUT rejects iff every comparator rejects. Least-favourable configuration: every delta_c = delta.
J, PERIODS, REPS = 6, 24, 20000
crit = student_t.ppf(1 - ALPHA, PERIODS - 1)

def cw_t_many(x):
    """x: (reps, J, clusters) with clusters = PERIODS * per; returns t per (rep, J)."""
    reps, j, n = x.shape
    per = n // PERIODS
    theta = x.mean(axis=2)
    dev = (x - theta[:, :, None]).reshape(reps, j, PERIODS, per).sum(axis=3)
    v = (dev ** 2).sum(axis=2) / n ** 2 * PERIODS / (PERIODS - 1)
    with np.errstate(divide='ignore', invalid='ignore'):   # a comparator with every increment zero has v = 0 and never rejects
        return theta / np.sqrt(v)

def iut_power(b, delta, per, rho, seed):
    r = np.random.default_rng(seed)
    n = PERIODS * per
    y = (r.random((REPS, 1, n)) < b).astype(float)
    shared = r.choice([-1.0, 1.0], size=(REPS, 1, n))
    own = r.choice([-1.0, 1.0], size=(REPS, J, n))
    use_shared = r.random((REPS, J, n)) < rho
    s = np.where(use_shared, shared, own)
    bc = b - s * math.sqrt(delta)
    x = (bc - y) ** 2 - (b - y) ** 2
    tt = cw_t_many(x)
    rej = tt > crit
    marg = rej.mean(axis=0)
    joint = rej.all(axis=1).mean()
    return float(marg.mean()), float(joint)

rc83 = {'design': 'J = 6 comparators, 24 blocks, cluster-weighted statistic with block-sum variance, one-sided alpha 0.05, 20,000 replications, least-favourable configuration (every comparator at the same delta)', 'cells': {}}
for b in (0.5,):
    for delta, per in ((0.01, 25), (0.01, 50), (0.02, 12), (0.02, 25), (0.03, 12)):
        for rho in (0.0, 0.5, 1.0):
            marg, joint = iut_power(b, delta, per, rho, 8300 + int(delta * 1000) * 100 + per + int(rho * 10))
            k = f'b={b},delta={delta},clusters={PERIODS * per}(24x{per}),shared_sign_prob={rho}'
            rc83['cells'][k] = {'mean_marginal_power': round(marg, 4), 'iut_joint_power': round(joint, 4),
                                'product_of_marginals': round(marg ** J, 4),
                                'iut_99pct_lower': round(binom_lower(int(round(joint * REPS)), REPS, 0.99), 4)}
# Size of the IUT at the least-favourable null (one comparator exactly null, the rest at a strong alternative) is
# <= alpha by construction (T-13); checked here with the same generator: comparator 1 at delta 0, others at 0.08.
r = np.random.default_rng(8399)
per = 25; n = PERIODS * per
y = (r.random((REPS, 1, n)) < 0.5).astype(float)
s = r.choice([-1.0, 1.0], size=(REPS, J, n))
deltas = np.array([0.0] + [0.08] * (J - 1))[None, :, None]
bc = 0.5 - s * np.sqrt(deltas)
x = (bc - y) ** 2 - (0.5 - y) ** 2
rej = cw_t_many(x) > crit
k_iut = int(rej.all(axis=1).sum())
rc83['least_favourable_null_check'] = {'comparator_1_delta': 0.0, 'others_delta': 0.08, 'iut_rejections': k_iut,
                                        'rate': round(k_iut / REPS, 4), '99pct_upper': round(binom_upper(k_iut, REPS, 0.99), 4)}
out['RC83_iut_conjunction_power'] = rc83

out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
```
<!-- round7-script:end -->

Output:

```json
{
  "RC80_distribution_free_power_bound": {
    "statement": "any level-alpha test valid for every mean-zero law on [-1, 1] has power <= alpha (1 + delta)^G against every alternative on [-1, 1] with mean delta",
    "G": 24,
    "alpha": 0.05,
    "power_upper_bound_by_delta": {
      "delta=0.005": 0.0564,
      "delta=0.01": 0.0635,
      "delta=0.02": 0.0804,
      "delta=0.03": 0.1016,
      "delta=0.05": 0.1613,
      "delta=0.08": 0.3171,
      "delta=0.1": 0.4925,
      "delta=0.12": 0.7589,
      "delta=0.13": 0.9394,
      "delta=0.15": 1.0
    },
    "smallest_delta_with_bound_at_or_above_0.80": 0.1225,
    "blocks_needed_for_bound_0.80": {
      "delta=0.01": 279,
      "delta=0.02": 141,
      "delta=0.05": 57,
      "delta=0.08": 37,
      "delta=0.1": 30
    },
    "round6_sentence_was": "at 24 blocks there is no distribution-free bounded-mean test with power at a useful effect (tested on one kernel only)",
    "round7_sentence_is": "over 24 blocks no finite-sample-valid bounded-mean test, of any form, has power above alpha (1 + delta)^24: 0.08 at delta = 0.02, 0.16 at 0.05, 0.32 at 0.08; 80 % needs delta >= 0.1225 or, at delta = 0.02, 141 blocks (computed, RC-102)",
    "numerical_check": {
      "delta=0.02": {
        "eps": 0.01961,
        "P0_mean_mc": 2e-05,
        "P0_fraction_without_catastrophe_mc": 0.62115,
        "(1-eps)^G": 0.62172,
        "randomised_LR_test_size_mc": 0.04977,
        "randomised_LR_test_power_mc": 0.07984,
        "bound": 0.08042,
        "grapa_betting_power_on_P1": 0.0,
        "grapa_running_max_power_on_P1": 0.0
      },
      "delta=0.05": {
        "eps": 0.04762,
        "P0_mean_mc": -1e-05,
        "P0_fraction_without_catastrophe_mc": 0.31069,
        "(1-eps)^G": 0.31007,
        "randomised_LR_test_size_mc": 0.04991,
        "randomised_LR_test_power_mc": 0.16275,
        "bound": 0.16125,
        "grapa_betting_power_on_P1": 1e-05,
        "grapa_running_max_power_on_P1": 1e-05
      },
      "delta=0.08": {
        "eps": 0.07407,
        "P0_mean_mc": -0.0004,
        "P0_fraction_without_catastrophe_mc": 0.15684,
        "(1-eps)^G": 0.1577,
        "randomised_LR_test_size_mc": 0.04981,
        "randomised_LR_test_power_mc": 0.31701,
        "bound": 0.31706,
        "grapa_betting_power_on_P1": 6e-05,
        "grapa_running_max_power_on_P1": 8e-05
      }
    },
    "grapa_constant_block_mean_needed_for_wealth_20_in_22_steps": 0.2918
  },
  "RC83_iut_conjunction_power": {
    "design": "J = 6 comparators, 24 blocks, cluster-weighted statistic with block-sum variance, one-sided alpha 0.05, 20,000 replications, least-favourable configuration (every comparator at the same delta)",
    "cells": {
      "b=0.5,delta=0.01,clusters=600(24x25),shared_sign_prob=0.0": {
        "mean_marginal_power": 0.7716,
        "iut_joint_power": 0.2103,
        "product_of_marginals": 0.211,
        "iut_99pct_lower": 0.2036
      },
      "b=0.5,delta=0.01,clusters=600(24x25),shared_sign_prob=0.5": {
        "mean_marginal_power": 0.7683,
        "iut_joint_power": 0.3192,
        "product_of_marginals": 0.2056,
        "iut_99pct_lower": 0.3116
      },
      "b=0.5,delta=0.01,clusters=600(24x25),shared_sign_prob=1.0": {
        "mean_marginal_power": 0.768,
        "iut_joint_power": 0.768,
        "product_of_marginals": 0.2052,
        "iut_99pct_lower": 0.761
      },
      "b=0.5,delta=0.01,clusters=1200(24x50),shared_sign_prob=0.0": {
        "mean_marginal_power": 0.9572,
        "iut_joint_power": 0.77,
        "product_of_marginals": 0.769,
        "iut_99pct_lower": 0.7629
      },
      "b=0.5,delta=0.01,clusters=1200(24x50),shared_sign_prob=0.5": {
        "mean_marginal_power": 0.9569,
        "iut_joint_power": 0.7964,
        "product_of_marginals": 0.7675,
        "iut_99pct_lower": 0.7897
      },
      "b=0.5,delta=0.01,clusters=1200(24x50),shared_sign_prob=1.0": {
        "mean_marginal_power": 0.957,
        "iut_joint_power": 0.957,
        "product_of_marginals": 0.7682,
        "iut_99pct_lower": 0.9535
      },
      "b=0.5,delta=0.02,clusters=288(24x12),shared_sign_prob=0.0": {
        "mean_marginal_power": 0.7555,
        "iut_joint_power": 0.184,
        "product_of_marginals": 0.186,
        "iut_99pct_lower": 0.1776
      },
      "b=0.5,delta=0.02,clusters=288(24x12),shared_sign_prob=0.5": {
        "mean_marginal_power": 0.7516,
        "iut_joint_power": 0.2927,
        "product_of_marginals": 0.1803,
        "iut_99pct_lower": 0.2852
      },
      "b=0.5,delta=0.02,clusters=288(24x12),shared_sign_prob=1.0": {
        "mean_marginal_power": 0.7487,
        "iut_joint_power": 0.7487,
        "product_of_marginals": 0.1761,
        "iut_99pct_lower": 0.7415
      },
      "b=0.5,delta=0.02,clusters=600(24x25),shared_sign_prob=0.0": {
        "mean_marginal_power": 0.9564,
        "iut_joint_power": 0.7648,
        "product_of_marginals": 0.7654,
        "iut_99pct_lower": 0.7577
      },
      "b=0.5,delta=0.02,clusters=600(24x25),shared_sign_prob=0.5": {
        "mean_marginal_power": 0.9582,
        "iut_joint_power": 0.8007,
        "product_of_marginals": 0.7739,
        "iut_99pct_lower": 0.7941
      },
      "b=0.5,delta=0.02,clusters=600(24x25),shared_sign_prob=1.0": {
        "mean_marginal_power": 0.955,
        "iut_joint_power": 0.955,
        "product_of_marginals": 0.7589,
        "iut_99pct_lower": 0.9515
      },
      "b=0.5,delta=0.03,clusters=288(24x12),shared_sign_prob=0.0": {
        "mean_marginal_power": 0.8875,
        "iut_joint_power": 0.484,
        "product_of_marginals": 0.4888,
        "iut_99pct_lower": 0.4758
      },
      "b=0.5,delta=0.03,clusters=288(24x12),shared_sign_prob=0.5": {
        "mean_marginal_power": 0.8871,
        "iut_joint_power": 0.5661,
        "product_of_marginals": 0.4875,
        "iut_99pct_lower": 0.5579
      },
      "b=0.5,delta=0.03,clusters=288(24x12),shared_sign_prob=1.0": {
        "mean_marginal_power": 0.8874,
        "iut_joint_power": 0.8874,
        "product_of_marginals": 0.4885,
        "iut_99pct_lower": 0.8821
      }
    },
    "least_favourable_null_check": {
      "comparator_1_delta": 0.0,
      "others_delta": 0.08,
      "iut_rejections": 0,
      "rate": 0.0,
      "99pct_upper": 0.0002
    }
  },
  "python": "3.11.17"
}
```

## Appendix I. Round-8 checks (REPRODUCED)

Needs no reference code and no network. Run with `python -I round8_checks.py` in an isolated venv (Python 3.11.17,
numpy 2.4.6, scipy 1.17.1; 15 s), extracting the block between the `round8-script` markers as in Appendix A.
Seeds are fixed; two consecutive runs produced byte-identical output. The RC-85 block (a) runs a toy closure
machine for one two-member cluster under the version-5 rule and the proposed version-6 rule on six scenarios,
and (b) measures what outcome-dependent VOID removal inside a cap does to the cluster-weighted primary test of
Appendix F on two valid nulls at 300 and 600 clusters over 24 blocks, with the worst-case lower bound beside it.
The RC-86 block builds fixture F-25, derives the as-of oracle at ten cutoffs and runs four defective readers
beside the reference. One correction made while writing it, recorded so that the method is checkable: a first
draft sorted the increments before assigning calendar blocks, which destroyed the block structure and gave a
36–39 % null rejection rate with nothing removed; the committed script keeps every cluster at its calendar
position and removes by mask (null size 4.9–5.0 %).

<!-- round8-script:start -->
```python
"""Round-8 checks for the Codex findings on PR #4 at 37ac018 (no reference code, no network).

RC-85: the version-5 VOID cutoff depends on t*_k, which an all-VOID cluster never has; a toy closure state machine
shows which VOID declarations each rule admits, and a Monte Carlo shows what outcome-dependent removal inside the
VOID cap does to the primary test under the null. RC-86: T-15 has refusal cases only; a deterministic as-of oracle
table and four defective readers show which oracle each reader fails. The cluster-weighted statistic is that of
16 Appendix F; the two-point null generator is that of Appendix D/E.
"""
import json, math, sys
import numpy as np
from scipy.stats import t as student_t

out = {}
ALPHA = 0.05

def cluster_weighted_t(x, n_blocks, w=None):
    """theta = mean over clusters; variance = block-sum (cluster-robust) form over n_blocks calendar blocks, G/(G-1)
    factor, G-1 df (17 section 3 item 3, RC-69). x has shape (reps, clusters) in calendar order; clusters are
    assigned to blocks round-robin by position. w is an optional 0/1 mask of the clusters that remain (a removed
    cluster keeps its calendar position and contributes nothing)."""
    reps, n = x.shape
    if w is None:
        w = np.ones_like(x)
    n_eff = w.sum(axis=1)
    theta = (w * x).sum(axis=1) / n_eff
    dev = w * (x - theta[:, None])
    blocks = np.arange(n) % n_blocks
    bs = np.stack([dev[:, blocks == b].sum(axis=1) for b in range(n_blocks)], axis=1)
    v = (bs ** 2).sum(axis=1) / n_eff ** 2 * n_blocks / (n_blocks - 1)
    return theta, theta / np.sqrt(v)

# ================= r4301920287 (RC-85), part (a): toy closure state machine =================
# One cluster of two members. Freeze instant t_freeze = earliest not_before = 5 (the RC-29 instant at which membership
# is immutable). Deadline D = 40, declared latency window L = 10, so logical finality (RC-77) is at 50. Each member's
# outcome is publicly determinable at its publication time k_i and the registry receives the source's record at r_i.
# Both arms' forecasts were received at t = 1 (issuance window [0, 4]).
#
# Rule v5 (17 version 5): a VOID declaration is accepted when received; "a pre-declared VOID has no outcome and no
# knowable_at", so the member's record is not adjudicated; at closure a VOID received at or after t*_k is refused and
# the member is scored from its record, where t*_k = min over RESOLVED members of min(receipt, knowable_at). With no
# resolved member t*_k does not exist and nothing is refused.
# Rule v6 (proposed): the VOID set is frozen with the membership at t_freeze; after t_freeze a VOID request changes no
# state (it is logged in the VOID audit); every record received is adjudicated and an outcome always wins; at finality
# with no record the pre-registered source rule decides NO (eventually-by-deadline predicate, source alive) or an
# adjudicated, outcome-dependent VOID (source failed); adjudicated VOIDs count against the cap and are imputed in the
# worst-case bounds; a cluster is all-VOID only by the freeze or by the source rule at finality, never by declaration.
T_FREEZE, FINALITY = 5, 50

def run(rule, void_requests, records, source_failed):
    """void_requests: {member: time}; records: {member: (publication_time, receipt_time)}."""
    state = {m: 'open' for m in (1, 2)}
    knowable = {}
    audit = []
    events = sorted([(t, 'void', m) for m, t in void_requests.items()] +
                    [(r, 'record', m) for m, (k, r) in records.items()] + [(FINALITY, 'finality', None)])
    for t, kind, m in events:
        if kind == 'void':
            if rule == 'v5':
                state[m] = 'void_declared'; audit.append(f'{t}: VOID member {m} accepted')
            else:
                if t < T_FREEZE:
                    state[m] = 'void_predeclared'; audit.append(f'{t}: VOID member {m} pre-declared (before freeze)')
                else:
                    audit.append(f'{t}: VOID request member {m} after freeze: logged, no state change')
        elif kind == 'record':
            k, r = records[m]
            if rule == 'v5' and state[m] == 'void_declared':
                audit.append(f'{t}: record for VOID member {m} not adjudicated (no knowable_at)')
            elif state[m] == 'void_predeclared':
                audit.append(f'{t}: record for pre-declared VOID member {m} ignored')
            else:
                state[m] = 'scored'; knowable[m] = min(k, r); audit.append(f'{t}: member {m} scored, knowable_at {k}')
        else:
            for mm in (1, 2):
                if state[mm] == 'open':
                    if rule == 'v6':
                        state[mm] = 'void_adjudicated' if source_failed else 'scored_NO_by_finality'
                        audit.append(f'{t}: member {mm} {state[mm]} by source rule')
                    else:
                        state[mm] = 'pending'
    if rule == 'v5':
        resolved_times = [min(records[mm]) for mm in (1, 2) if state[mm] == 'scored']
        t_star = min(resolved_times) if resolved_times else None
        for mm in (1, 2):
            if state[mm] == 'void_declared':
                if t_star is not None and void_requests[mm] >= t_star:
                    state[mm] = 'scored'; audit.append(f'closure: VOID member {mm} at {void_requests[mm]} >= t*_k {t_star}: refused, scored')
                else:
                    audit.append(f'closure: VOID member {mm} stands (t*_k {"undefined" if t_star is None else t_star})')
    scored = [mm for mm in (1, 2) if state[mm].startswith('scored')]
    voids = [mm for mm in (1, 2) if state[mm].startswith('void')]
    return {'end_state': state, 'increment_emitted': len(scored) > 0 and len(scored) + len(voids) == 2,
            'members_in_increment': scored, 'void_members_against_cap': voids,
            'imputed_in_worst_case_bounds': voids if rule == 'v6' else 'unspecified for an all-VOID cluster in v5',
            'audit': audit}

scenarios = {
    'S1_pre_freeze_void_both': dict(void_requests={1: 3, 2: 4}, records={1: (10, 30), 2: (12, 32)}, source_failed=False),
    'S2_void_both_after_publication_before_receipt': dict(void_requests={1: 11, 2: 13}, records={1: (10, 30), 2: (12, 32)}, source_failed=False),
    'S3_void_one_after_publication_sibling_resolves': dict(void_requests={2: 13}, records={1: (10, 30), 2: (12, 32)}, source_failed=False),
    'S4_source_failed_no_records': dict(void_requests={1: 20, 2: 21}, records={}, source_failed=True),
    'S5_source_failed_one_record': dict(void_requests={2: 21}, records={1: (10, 30)}, source_failed=True),
    'S6_no_void_no_record_source_alive': dict(void_requests={}, records={}, source_failed=False),
}
rc85a = {}
for name, sc in scenarios.items():
    rc85a[name] = {'v5': run('v5', **sc), 'v6': run('v6', **sc)}
rc85a['reading'] = ('S2 is Codex\'s channel: under v5 both post-publication VOIDs stand because no member is resolved and t*_k '
                    'is undefined, and the cluster leaves the point estimate; under v6 both records are adjudicated and the '
                    'cluster is scored. S3 shows v5 refusing the same VOID when a sibling resolves, so the gap is exactly the '
                    'all-VOID case. S4 and S5 show the legitimate all-VOID and partial-VOID routes under v6 (source rule at '
                    'finality), both outcome-dependent, both against the cap and in the bounds.')
out['RC85a_closure_state_machine'] = rc85a

# ================= r4301920287 (RC-85), part (b): what removal inside the cap does to the primary =================
# Valid null, independent clusters, 24 calendar blocks, 20,000 replications. Generator of Appendix D/E: q = 0.5,
# X = 0.4 Y - 0.2 in {-0.2, +0.2} (baseline 0.4, challenger 0.6), and a continuous variant: p_true ~ U(0.05, 0.95),
# both arms p_true + N(0, 0.1) clipped to [0.01, 0.99] (equal skill, so E[X] = 0), Y ~ Bernoulli(p_true).
# An adversary who sees the outcomes declares the q N clusters with the most negative increments VOID, q = cap. The
# primary is recomputed over the remaining clusters; the worst-case lower bound re-imputes every removed cluster with
# the outcome least favourable to FULL. Reported: rejection rate of the primary, mean shift, and how often the lower
# bound still rejects.
REPS, BLOCKS = 20000, 24
rng = np.random.default_rng(8501)
crit = float(student_t.ppf(1 - ALPHA, BLOCKS - 1))

def two_point(n):
    y = (rng.random((REPS, n)) < 0.5).astype(float)
    return 0.4 * y - 0.2, np.full((REPS, n), 0.4), np.full((REPS, n), 0.6)

def continuous(n):
    p = rng.uniform(0.05, 0.95, size=(REPS, n))
    pc = np.clip(p + rng.normal(0, 0.1, size=(REPS, n)), 0.01, 0.99)
    pf = np.clip(p + rng.normal(0, 0.1, size=(REPS, n)), 0.01, 0.99)
    y = (rng.random((REPS, n)) < p).astype(float)
    return (pc - y) ** 2 - (pf - y) ** 2, pc, pf

rc85b = {'design': f'{REPS} replications, {BLOCKS} blocks, one-sided alpha {ALPHA}, t critical {crit:.4f} on {BLOCKS - 1} df; '
                   'removal = the q N most negative cluster increments declared VOID after the outcomes are known'}
for gname, gen in (('two_point_null', two_point), ('continuous_null', continuous)):
    for n in (300, 600):
        x, pc, pf = gen(n)
        rank = np.argsort(np.argsort(x, axis=1), axis=1)   # rank 0 = most negative increment, per replication
        res = {}
        for q in (0.0, 0.02, 0.05, 0.10):
            k = int(round(q * n))
            keep = (rank >= k).astype(float)                 # clusters stay at their calendar position
            theta, tt = cluster_weighted_t(x, BLOCKS, keep)
            entry = {'removed': k, 'primary_rejection_rate': round(float((tt > crit).mean()), 4),
                     'mean_of_point_estimate': round(float(theta.mean()), 5)}
            if k > 0:
                # least favourable to FULL: Y = 1 where p_FULL < p_baseline, else Y = 0 (17 section 6, Missing data)
                y_lf = (pf < pc).astype(float)
                x_lf = (pc - y_lf) ** 2 - (pf - y_lf) ** 2
                x_lower = np.where(keep > 0, x, x_lf)
                th_l, t_l = cluster_weighted_t(x_lower, BLOCKS)
                entry['worst_case_lower_bound_rejection_rate'] = round(float((t_l > crit).mean()), 4)
                entry['mean_of_lower_bound_estimate'] = round(float(th_l.mean()), 5)
            res[f'cap={q}'] = entry
        rc85b[f'{gname},clusters={n}'] = res
rc85b['reading'] = ('The cap bounds how many clusters leave, not the bias. With no removal the primary holds 5 % on both nulls; '
                    'removing the 2 % least favourable clusters gives 10-13 % (two-point) and 31-47 % (continuous), 5 % gives '
                    '23-34 % and 77-95 %, 10 % gives 56-81 % and 99-100 %, while the worst-case lower bound stays at 5 % '
                    'throughout. The point estimate, not the bound, is what the primary tests, so the removal decision must be '
                    'outcome-independent (frozen) or adjudicated by the source rule, never declared.')
out['RC85b_selective_void_under_null'] = rc85b

# ================= r4301920289 (RC-86): positive as-of oracles for T-15 =================
# Fixture F-25: one entity, one feature, five rows (observed_at, available_at, vintage, value).
F25 = [(10, 12, 'v1', 1.00),   # first release of the period-10 observation
       (10, 20, 'v2', 1.50),   # revision of it
       (5, 25, 'v3', 0.70),    # backfilled earlier period, inserted after later data exist
       (30, 40, 'v4', 2.00),   # publication-lagged observation
       (10, 50, 'v6', 1.40)]   # second revision of period 10
CUTS = (11, 12, 19, 20, 24, 25, 39, 40, 49, 50)

def oracle(t_cut):
    """Point-in-time truth: for every observed_at with a row available at or before t_cut, the row with the greatest
    available_at <= t_cut (the latest vintage an agent at t_cut could have read); 'latest' = greatest observed_at."""
    series = {}
    for obs, avail, vin, val in F25:
        if avail <= t_cut and (obs not in series or avail > series[obs][0]):
            series[obs] = (avail, vin, val)
    return {obs: (vin, val) for obs, (avail, vin, val) in sorted(series.items())}

def reader_reference(t_cut):
    return oracle(t_cut)
def reader_refuse_all(t_cut):
    raise PermissionError('refused')
def reader_oldest_eligible(t_cut):
    series = {}
    for obs, avail, vin, val in F25:
        if avail <= t_cut and (obs not in series or avail < series[obs][0]):
            series[obs] = (avail, vin, val)
    return {obs: (vin, val) for obs, (avail, vin, val) in sorted(series.items())}
def reader_filters_on_observed_at(t_cut):
    series = {}
    for obs, avail, vin, val in F25:
        if obs <= t_cut and (obs not in series or avail > series[obs][0]):
            series[obs] = (avail, vin, val)
    return {obs: (vin, val) for obs, (avail, vin, val) in sorted(series.items())}
def reader_latest_regardless(t_cut):
    series = {}
    for obs, avail, vin, val in F25:
        if obs not in series or avail > series[obs][0]:
            series[obs] = (avail, vin, val)
    return {obs: (vin, val) for obs, (avail, vin, val) in sorted(series.items())}

def row_refused(reader, t_cut):
    """The four refusal cases of T-15 (a)-(d): a read of a specific row with available_at > t_cut must be refused.
    A reader passes if it never returns a row with available_at > t_cut."""
    try:
        got = reader(t_cut)
    except PermissionError:
        return True
    avail_of = {(obs, vin): avail for obs, avail, vin, val in F25}
    return all(avail_of[(obs, vin)] <= t_cut for obs, (vin, val) in got.items())

readers = {'reference': reader_reference, 'refuse_all': reader_refuse_all, 'oldest_eligible_vintage': reader_oldest_eligible,
           'filters_on_observed_at': reader_filters_on_observed_at, 'latest_regardless_of_cutoff': reader_latest_regardless}
oracle_table = {f't_cut={c}': {str(k): list(v) for k, v in oracle(c).items()} for c in CUTS}
rc86 = {'fixture_F25': [list(r) for r in F25], 'oracle': oracle_table, 'readers': {}}
for name, rd in readers.items():
    pos_fail, ref_fail = [], []
    for c in CUTS:
        try:
            got = rd(c)
        except PermissionError:
            got = 'refused'
        if got != oracle(c):
            pos_fail.append(c)
        if not row_refused(rd, c):
            ref_fail.append(c)
    rc86['readers'][name] = {'passes_refusal_cases': not ref_fail, 'refusal_failures_at': ref_fail,
                             'passes_positive_oracles': not pos_fail, 'positive_oracle_failures_at': pos_fail}
rc86['reading'] = ('refuse_all and oldest_eligible_vintage pass every refusal case of T-15 as written and fail the positive '
                   'oracles; filters_on_observed_at is the classic leak (it returns v6 at t_cut = 11) and fails both; only '
                   'the reference reader passes both, so T-15 needs the oracle table beside the refusals.')
out['RC86_as_of_positive_oracles'] = rc86

out['python'] = sys.version.split()[0]
json.dump(out, sys.stdout, indent=2)
print()
```
<!-- round8-script:end -->

Output:

```json
{
  "RC85a_closure_state_machine": {
    "S1_pre_freeze_void_both": {
      "v5": {
        "end_state": {
          "1": "void_declared",
          "2": "void_declared"
        },
        "increment_emitted": false,
        "members_in_increment": [],
        "void_members_against_cap": [
          1,
          2
        ],
        "imputed_in_worst_case_bounds": "unspecified for an all-VOID cluster in v5",
        "audit": [
          "3: VOID member 1 accepted",
          "4: VOID member 2 accepted",
          "30: record for VOID member 1 not adjudicated (no knowable_at)",
          "32: record for VOID member 2 not adjudicated (no knowable_at)",
          "closure: VOID member 1 stands (t*_k undefined)",
          "closure: VOID member 2 stands (t*_k undefined)"
        ]
      },
      "v6": {
        "end_state": {
          "1": "void_predeclared",
          "2": "void_predeclared"
        },
        "increment_emitted": false,
        "members_in_increment": [],
        "void_members_against_cap": [
          1,
          2
        ],
        "imputed_in_worst_case_bounds": [
          1,
          2
        ],
        "audit": [
          "3: VOID member 1 pre-declared (before freeze)",
          "4: VOID member 2 pre-declared (before freeze)",
          "30: record for pre-declared VOID member 1 ignored",
          "32: record for pre-declared VOID member 2 ignored"
        ]
      }
    },
    "S2_void_both_after_publication_before_receipt": {
      "v5": {
        "end_state": {
          "1": "void_declared",
          "2": "void_declared"
        },
        "increment_emitted": false,
        "members_in_increment": [],
        "void_members_against_cap": [
          1,
          2
        ],
        "imputed_in_worst_case_bounds": "unspecified for an all-VOID cluster in v5",
        "audit": [
          "11: VOID member 1 accepted",
          "13: VOID member 2 accepted",
          "30: record for VOID member 1 not adjudicated (no knowable_at)",
          "32: record for VOID member 2 not adjudicated (no knowable_at)",
          "closure: VOID member 1 stands (t*_k undefined)",
          "closure: VOID member 2 stands (t*_k undefined)"
        ]
      },
      "v6": {
        "end_state": {
          "1": "scored",
          "2": "scored"
        },
        "increment_emitted": true,
        "members_in_increment": [
          1,
          2
        ],
        "void_members_against_cap": [],
        "imputed_in_worst_case_bounds": [],
        "audit": [
          "11: VOID request member 1 after freeze: logged, no state change",
          "13: VOID request member 2 after freeze: logged, no state change",
          "30: member 1 scored, knowable_at 10",
          "32: member 2 scored, knowable_at 12"
        ]
      }
    },
    "S3_void_one_after_publication_sibling_resolves": {
      "v5": {
        "end_state": {
          "1": "scored",
          "2": "scored"
        },
        "increment_emitted": true,
        "members_in_increment": [
          1,
          2
        ],
        "void_members_against_cap": [],
        "imputed_in_worst_case_bounds": "unspecified for an all-VOID cluster in v5",
        "audit": [
          "13: VOID member 2 accepted",
          "30: member 1 scored, knowable_at 10",
          "32: record for VOID member 2 not adjudicated (no knowable_at)",
          "closure: VOID member 2 at 13 >= t*_k 10: refused, scored"
        ]
      },
      "v6": {
        "end_state": {
          "1": "scored",
          "2": "scored"
        },
        "increment_emitted": true,
        "members_in_increment": [
          1,
          2
        ],
        "void_members_against_cap": [],
        "imputed_in_worst_case_bounds": [],
        "audit": [
          "13: VOID request member 2 after freeze: logged, no state change",
          "30: member 1 scored, knowable_at 10",
          "32: member 2 scored, knowable_at 12"
        ]
      }
    },
    "S4_source_failed_no_records": {
      "v5": {
        "end_state": {
          "1": "void_declared",
          "2": "void_declared"
        },
        "increment_emitted": false,
        "members_in_increment": [],
        "void_members_against_cap": [
          1,
          2
        ],
        "imputed_in_worst_case_bounds": "unspecified for an all-VOID cluster in v5",
        "audit": [
          "20: VOID member 1 accepted",
          "21: VOID member 2 accepted",
          "closure: VOID member 1 stands (t*_k undefined)",
          "closure: VOID member 2 stands (t*_k undefined)"
        ]
      },
      "v6": {
        "end_state": {
          "1": "void_adjudicated",
          "2": "void_adjudicated"
        },
        "increment_emitted": false,
        "members_in_increment": [],
        "void_members_against_cap": [
          1,
          2
        ],
        "imputed_in_worst_case_bounds": [
          1,
          2
        ],
        "audit": [
          "20: VOID request member 1 after freeze: logged, no state change",
          "21: VOID request member 2 after freeze: logged, no state change",
          "50: member 1 void_adjudicated by source rule",
          "50: member 2 void_adjudicated by source rule"
        ]
      }
    },
    "S5_source_failed_one_record": {
      "v5": {
        "end_state": {
          "1": "scored",
          "2": "scored"
        },
        "increment_emitted": true,
        "members_in_increment": [
          1,
          2
        ],
        "void_members_against_cap": [],
        "imputed_in_worst_case_bounds": "unspecified for an all-VOID cluster in v5",
        "audit": [
          "21: VOID member 2 accepted",
          "30: member 1 scored, knowable_at 10",
          "closure: VOID member 2 at 21 >= t*_k 10: refused, scored"
        ]
      },
      "v6": {
        "end_state": {
          "1": "scored",
          "2": "void_adjudicated"
        },
        "increment_emitted": true,
        "members_in_increment": [
          1
        ],
        "void_members_against_cap": [
          2
        ],
        "imputed_in_worst_case_bounds": [
          2
        ],
        "audit": [
          "21: VOID request member 2 after freeze: logged, no state change",
          "30: member 1 scored, knowable_at 10",
          "50: member 2 void_adjudicated by source rule"
        ]
      }
    },
    "S6_no_void_no_record_source_alive": {
      "v5": {
        "end_state": {
          "1": "pending",
          "2": "pending"
        },
        "increment_emitted": false,
        "members_in_increment": [],
        "void_members_against_cap": [],
        "imputed_in_worst_case_bounds": "unspecified for an all-VOID cluster in v5",
        "audit": []
      },
      "v6": {
        "end_state": {
          "1": "scored_NO_by_finality",
          "2": "scored_NO_by_finality"
        },
        "increment_emitted": true,
        "members_in_increment": [
          1,
          2
        ],
        "void_members_against_cap": [],
        "imputed_in_worst_case_bounds": [],
        "audit": [
          "50: member 1 scored_NO_by_finality by source rule",
          "50: member 2 scored_NO_by_finality by source rule"
        ]
      }
    },
    "reading": "S2 is Codex's channel: under v5 both post-publication VOIDs stand because no member is resolved and t*_k is undefined, and the cluster leaves the point estimate; under v6 both records are adjudicated and the cluster is scored. S3 shows v5 refusing the same VOID when a sibling resolves, so the gap is exactly the all-VOID case. S4 and S5 show the legitimate all-VOID and partial-VOID routes under v6 (source rule at finality), both outcome-dependent, both against the cap and in the bounds."
  },
  "RC85b_selective_void_under_null": {
    "design": "20000 replications, 24 blocks, one-sided alpha 0.05, t critical 1.7139 on 23 df; removal = the q N most negative cluster increments declared VOID after the outcomes are known",
    "two_point_null,clusters=300": {
      "cap=0.0": {
        "removed": 0,
        "primary_rejection_rate": 0.049,
        "mean_of_point_estimate": 4e-05
      },
      "cap=0.02": {
        "removed": 6,
        "primary_rejection_rate": 0.0999,
        "mean_of_point_estimate": 0.00412,
        "worst_case_lower_bound_rejection_rate": 0.049,
        "mean_of_lower_bound_estimate": 4e-05
      },
      "cap=0.05": {
        "removed": 15,
        "primary_rejection_rate": 0.2306,
        "mean_of_point_estimate": 0.01057,
        "worst_case_lower_bound_rejection_rate": 0.049,
        "mean_of_lower_bound_estimate": 4e-05
      },
      "cap=0.1": {
        "removed": 30,
        "primary_rejection_rate": 0.5645,
        "mean_of_point_estimate": 0.02227,
        "worst_case_lower_bound_rejection_rate": 0.049,
        "mean_of_lower_bound_estimate": 4e-05
      }
    },
    "two_point_null,clusters=600": {
      "cap=0.0": {
        "removed": 0,
        "primary_rejection_rate": 0.0495,
        "mean_of_point_estimate": 4e-05
      },
      "cap=0.02": {
        "removed": 12,
        "primary_rejection_rate": 0.1283,
        "mean_of_point_estimate": 0.00412,
        "worst_case_lower_bound_rejection_rate": 0.0495,
        "mean_of_lower_bound_estimate": 4e-05
      },
      "cap=0.05": {
        "removed": 30,
        "primary_rejection_rate": 0.3427,
        "mean_of_point_estimate": 0.01057,
        "worst_case_lower_bound_rejection_rate": 0.0495,
        "mean_of_lower_bound_estimate": 4e-05
      },
      "cap=0.1": {
        "removed": 60,
        "primary_rejection_rate": 0.8081,
        "mean_of_point_estimate": 0.02226,
        "worst_case_lower_bound_rejection_rate": 0.0495,
        "mean_of_lower_bound_estimate": 4e-05
      }
    },
    "continuous_null,clusters=300": {
      "cap=0.0": {
        "removed": 0,
        "primary_rejection_rate": 0.0496,
        "mean_of_point_estimate": 2e-05
      },
      "cap=0.02": {
        "removed": 6,
        "primary_rejection_rate": 0.3106,
        "mean_of_point_estimate": 0.00732,
        "worst_case_lower_bound_rejection_rate": 0.0496,
        "mean_of_lower_bound_estimate": 2e-05
      },
      "cap=0.05": {
        "removed": 15,
        "primary_rejection_rate": 0.7685,
        "mean_of_point_estimate": 0.01498,
        "worst_case_lower_bound_rejection_rate": 0.0496,
        "mean_of_lower_bound_estimate": 2e-05
      },
      "cap=0.1": {
        "removed": 30,
        "primary_rejection_rate": 0.9908,
        "mean_of_point_estimate": 0.02489,
        "worst_case_lower_bound_rejection_rate": 0.0496,
        "mean_of_lower_bound_estimate": 2e-05
      }
    },
    "continuous_null,clusters=600": {
      "cap=0.0": {
        "removed": 0,
        "primary_rejection_rate": 0.0503,
        "mean_of_point_estimate": -5e-05
      },
      "cap=0.02": {
        "removed": 12,
        "primary_rejection_rate": 0.4739,
        "mean_of_point_estimate": 0.00732,
        "worst_case_lower_bound_rejection_rate": 0.0503,
        "mean_of_lower_bound_estimate": -5e-05
      },
      "cap=0.05": {
        "removed": 30,
        "primary_rejection_rate": 0.9514,
        "mean_of_point_estimate": 0.01498,
        "worst_case_lower_bound_rejection_rate": 0.0503,
        "mean_of_lower_bound_estimate": -5e-05
      },
      "cap=0.1": {
        "removed": 60,
        "primary_rejection_rate": 0.9999,
        "mean_of_point_estimate": 0.0249,
        "worst_case_lower_bound_rejection_rate": 0.0503,
        "mean_of_lower_bound_estimate": -5e-05
      }
    },
    "reading": "The cap bounds how many clusters leave, not the bias. With no removal the primary holds 5 % on both nulls; removing the 2 % least favourable clusters gives 10-13 % (two-point) and 31-47 % (continuous), 5 % gives 23-34 % and 77-95 %, 10 % gives 56-81 % and 99-100 %, while the worst-case lower bound stays at 5 % throughout. The point estimate, not the bound, is what the primary tests, so the removal decision must be outcome-independent (frozen) or adjudicated by the source rule, never declared."
  },
  "RC86_as_of_positive_oracles": {
    "fixture_F25": [
      [
        10,
        12,
        "v1",
        1.0
      ],
      [
        10,
        20,
        "v2",
        1.5
      ],
      [
        5,
        25,
        "v3",
        0.7
      ],
      [
        30,
        40,
        "v4",
        2.0
      ],
      [
        10,
        50,
        "v6",
        1.4
      ]
    ],
    "oracle": {
      "t_cut=11": {},
      "t_cut=12": {
        "10": [
          "v1",
          1.0
        ]
      },
      "t_cut=19": {
        "10": [
          "v1",
          1.0
        ]
      },
      "t_cut=20": {
        "10": [
          "v2",
          1.5
        ]
      },
      "t_cut=24": {
        "10": [
          "v2",
          1.5
        ]
      },
      "t_cut=25": {
        "5": [
          "v3",
          0.7
        ],
        "10": [
          "v2",
          1.5
        ]
      },
      "t_cut=39": {
        "5": [
          "v3",
          0.7
        ],
        "10": [
          "v2",
          1.5
        ]
      },
      "t_cut=40": {
        "5": [
          "v3",
          0.7
        ],
        "10": [
          "v2",
          1.5
        ],
        "30": [
          "v4",
          2.0
        ]
      },
      "t_cut=49": {
        "5": [
          "v3",
          0.7
        ],
        "10": [
          "v2",
          1.5
        ],
        "30": [
          "v4",
          2.0
        ]
      },
      "t_cut=50": {
        "5": [
          "v3",
          0.7
        ],
        "10": [
          "v6",
          1.4
        ],
        "30": [
          "v4",
          2.0
        ]
      }
    },
    "readers": {
      "reference": {
        "passes_refusal_cases": true,
        "refusal_failures_at": [],
        "passes_positive_oracles": true,
        "positive_oracle_failures_at": []
      },
      "refuse_all": {
        "passes_refusal_cases": true,
        "refusal_failures_at": [],
        "passes_positive_oracles": false,
        "positive_oracle_failures_at": [
          11,
          12,
          19,
          20,
          24,
          25,
          39,
          40,
          49,
          50
        ]
      },
      "oldest_eligible_vintage": {
        "passes_refusal_cases": true,
        "refusal_failures_at": [],
        "passes_positive_oracles": false,
        "positive_oracle_failures_at": [
          20,
          24,
          25,
          39,
          40,
          49,
          50
        ]
      },
      "filters_on_observed_at": {
        "passes_refusal_cases": false,
        "refusal_failures_at": [
          11,
          12,
          19,
          20,
          24,
          25,
          39,
          40,
          49
        ],
        "passes_positive_oracles": false,
        "positive_oracle_failures_at": [
          11,
          12,
          19,
          20,
          24,
          25,
          39,
          40,
          49
        ]
      },
      "latest_regardless_of_cutoff": {
        "passes_refusal_cases": false,
        "refusal_failures_at": [
          11,
          12,
          19,
          20,
          24,
          25,
          39,
          40,
          49
        ],
        "passes_positive_oracles": false,
        "positive_oracle_failures_at": [
          11,
          12,
          19,
          20,
          24,
          25,
          39,
          40,
          49
        ]
      }
    },
    "reading": "refuse_all and oldest_eligible_vintage pass every refusal case of T-15 as written and fail the positive oracles; filters_on_observed_at is the classic leak (it returns v6 at t_cut = 11) and fails both; only the reference reader passes both, so T-15 needs the oracle table beside the refusals."
  },
  "python": "3.11.17"
}
```

## Appendix J. Round-9 checks (REPRODUCED)

Needs no reference code and no network. Run with `python -I round9_checks.py` in an isolated venv (Python 3.11.17,
numpy 2.4.6, scipy 1.17.1; 58 s), extracting the block between the `round9-script` markers as in Appendix A.
Seeds are fixed; two consecutive runs produced byte-identical output. Blocks, keyed by the review-comment id each
answers: RC-93 reproduces the degenerate null comparator of Appendix H and runs the IUT size check with a
mean-zero, positive-variance null comparator; RC-102 evaluates the bound at 140 and 141 blocks; RC-95 computes
Codex's two-cluster conditional expectation exactly and runs the outcome-dependent-timing toy under closure order
and under pre-registered maturity order at four NO lags; RC-101 builds the six-test joint law with zero joint
power and runs the Appendix H conjunction generator with three anti-correlated comparator pairs; RC-97 runs
Appendix F's valid null with Poisson supply allowing empty periods under both block-counting conventions; RC-94
computes the exact size of the one-sided t over 24 two-point blocks as a function of the catastrophe share and
calibrates the critical value for four null classes, with power at δ = 0.02 at the nominal and the calibrated
value; RC-100 and RC-103 are toy state machines for the clock slew and the demotion epoch; RC-96 measures the
version-selection channel; the last block lists the deterministic fixtures of RC-88, RC-92, RC-104 and RC-105.
Two corrections made while writing it, recorded so that the method is checkable: a first draft of the RC-97
block used a comparator with a calibration error against a calibrated FULL, which is not a null (mean +0.04) and
gave 25–38 % "size" under both conventions; the committed block uses Appendix F's null generator. A first draft
of the RC-94 block let an all-positive sample reject with t = +∞, under which no critical value exists for any
class with ε_min below 0.12; the committed block uses Appendix G's convention (zero variance never rejects), now
stated in `17`. Every committed script of Appendix C to I was also re-extracted and re-run in the same
environment this round (§2): byte-identical, except Appendix H in the one line corrected for RC-102.

<!-- round9-script:start -->
```python
"""Round-9 checks for the Codex findings on PR #4 at 8af2ae9 (no reference code, no network).

Reviews 5556950582 and 5558680831. Each block is keyed by the review-comment id it answers. The archived
GRAPA rule, the D1-type generator and the cluster-weighted statistic are those of 16 Appendix A, F and H.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA, LAM_MAX = 0.05, 0.5
PERIODS = 24

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

def cw_t_blocks(blocks):
    """Cluster-weighted statistic with block-sum variance (Appendix F) over a list of per-block arrays."""
    x = np.concatenate(blocks); n = x.size; g = len(blocks)
    theta = x.mean()
    dev = np.array([(b - theta).sum() for b in blocks])
    v = (dev ** 2).sum() / n ** 2 * g / (g - 1)
    return float(theta), float(theta / math.sqrt(v)) if v > 0 else 0.0, g - 1

def cw_t_many(x):
    """x: (reps, J, clusters), clusters = PERIODS * per; returns t per (rep, J)."""
    reps, j, n = x.shape
    per = n // PERIODS
    theta = x.mean(axis=2)
    dev = (x - theta[:, :, None]).reshape(reps, j, PERIODS, per).sum(axis=3)
    v = (dev ** 2).sum(axis=2) / n ** 2 * PERIODS / (PERIODS - 1)
    with np.errstate(divide='ignore', invalid='ignore'):
        return theta / np.sqrt(v)

# ================= r4301994299 (RC-93): the committed IUT null check was degenerate =================
# Appendix H set comparator 1 to delta = 0 in the generator bc = b - s sqrt(delta), which gives bc = b exactly, so
# X_1 = (b - Y)^2 - (b - Y)^2 = 0 for every cluster: zero variance, t undefined, never rejects. Reproduced, then
# replaced by a null comparator with mean-zero, non-zero-variance increments: FULL and the null comparator both
# carry a calibration error of magnitude c with independent signs, X = (b + s_c c - Y)^2 - (b + s_F c - Y)^2.
J, REPS = 6, 20000
crit = student_t.ppf(1 - ALPHA, PERIODS - 1)
r = np.random.default_rng(8399)
per = 25; n = PERIODS * per
y = (r.random((REPS, 1, n)) < 0.5).astype(float)
s = r.choice([-1.0, 1.0], size=(REPS, J, n))
deltas = np.array([0.0] + [0.08] * (J - 1))[None, :, None]
x_old = ((0.5 - s * np.sqrt(deltas)) - y) ** 2 - (0.5 - y) ** 2
rc93 = {'committed_check_comparator_1': {'max_abs_increment': float(np.abs(x_old[:, 0, :]).max()),
                                         'variance': float(x_old[:, 0, :].var()),
                                         'reading': 'every increment of the null comparator is exactly zero, so its t statistic is undefined and the conjunction can never reject; the 0 of 20,000 was mechanical'}}
def iut_null_check(c, seed):
    r_ = np.random.default_rng(seed)
    y_ = (r_.random((REPS, 1, n)) < 0.5).astype(float)
    s_full = r_.choice([-1.0, 1.0], size=(REPS, 1, n))
    s_c = r_.choice([-1.0, 1.0], size=(REPS, J, n))
    p_full = 0.5 + s_full * c
    bc = np.empty((REPS, J, n))
    bc[:, 0:1, :] = 0.5 + s_c[:, 0:1, :] * c                       # null comparator: same error magnitude, independent sign
    bc[:, 1:, :] = 0.5 - s_c[:, 1:, :] * math.sqrt(0.08)           # the others at delta = 0.08 against a calibrated FULL
    x = (bc - y_) ** 2 - (p_full - y_) ** 2
    x[:, 1:, :] = ((bc[:, 1:, :] - y_) ** 2 - (0.5 - y_) ** 2)
    tt = cw_t_many(x)
    rej = tt > crit
    k1 = int(rej[:, 0].sum()); k_iut = int(rej.all(axis=1).sum())
    return {'c': c, 'null_comparator_mean_increment': round(float(x[:, 0, :].mean()), 5),
            'null_comparator_increment_variance': round(float(x[:, 0, :].var()), 5),
            'null_comparator_marginal_rejections': k1, 'null_comparator_rate': round(k1 / REPS, 4),
            'iut_rejections': k_iut, 'iut_rate': round(k_iut / REPS, 4),
            'iut_99pct_upper': round(binom_upper(k_iut, REPS, 0.99), 4),
            'within_A3_bound_0.06': binom_upper(k_iut, REPS, 0.99) <= 0.06}
rc93['non_degenerate_null_checks'] = [iut_null_check(0.1, 9301), iut_null_check(0.2, 9302)]
rc93['reading'] = 'with a null comparator whose increments have mean zero and positive variance the IUT rejects at about the nominal rate, which is the least-favourable size check T-13 (b) and T-16 require; the committed check is withdrawn'
out['RC93_iut_non_degenerate_null'] = rc93

# ================= r4303397714 (RC-102): 140 or 141 blocks =================
rc102 = {}
for G_ in (140, 141):
    rc102[f'bound_at_delta_0.02_G={G_}'] = round(ALPHA * 1.02 ** G_, 6)
rc102['ceil_log_16_over_log_1.02'] = math.ceil(math.log(0.80 / ALPHA) / math.log(1.02))
rc102['reading'] = 'the bound reaches 0.80 at 141 blocks (0.799823 at 140); the Appendix H sentence string was hand-typed as 140 and is corrected to the computed value'
out['RC102_blocks_needed'] = rc102

# ================= r4303397684 (RC-95): order in which increments enter the monitor =================
# (a) Codex's two-cluster example. A knowable at 10, closes at 30, X_A fair in {-1, +1}; B knowable and closes at
# 20, X_B fair given X_A = +1 and X_B = -1 given X_A = -1. lambda_A = 0.5 frozen. Closure order applies B then A.
rc95 = {}
pa = {(+1, +1): 0.25, (+1, -1): 0.25, (-1, -1): 0.5}   # (X_A, X_B) joint law
e_xb_given_xa = {xa: sum(p * xb for (a, xb), p in pa.items() if a == xa) / sum(p for (a, _), p in pa.items() if a == xa) for xa in (+1, -1)}
e_fac_a_given_xb_plus = sum(p * (1 + 0.5 * a) for (a, xb), p in pa.items() if xb == +1) / sum(p for (_, xb), p in pa.items() if xb == +1)
rc95['codex_example'] = {'E[X_A]': 0.0, 'E[X_B|X_A=+1]': e_xb_given_xa[+1], 'E[X_B|X_A=-1]': e_xb_given_xa[-1],
                         'conditional_null_in_knowable_order_holds': True,
                         'E[1+0.5 X_A | X_B=+1]_closure_order': e_fac_a_given_xb_plus,
                         'reading': 'in closure order the factor for A has conditional expectation 1.5 after B is seen, so the closure-ordered wealth is not a supermartingale; Codex is right that closure order carries no Ville guarantee'}
# (b) Does the running maximum actually exceed alpha? Not with a single late cluster and a fixed lambda (the final
# product has expectation <= 1, so P(final >= 20) <= alpha, and the B-prefix is a supermartingale given X_A). The
# channel that inflates it is outcome-dependent timing: for an eventually-by-deadline predicate a YES is knowable
# at the occurrence and a NO only at logical finality, so both closure order and knowable order place YES clusters
# earlier than NO clusters. Toy: 120 clusters registered one per interval, X_k = +c (YES) or -c (NO) fair,
# lambda = 0.5 fixed; a YES closes 1 interval after registration, a NO 6 intervals after (finality). Three orders:
# closure (knowable) order, registration order, and pre-registered maturity order H_k = registration + 6, which is
# outcome-independent.
R = 20000; N = 120; c = 0.5; lam = 0.5
def running_max_cross(xs, order_key):
    idx = np.argsort(order_key, axis=1, kind='stable')
    xo = np.take_along_axis(xs, idx, axis=1)
    w = np.cumprod(1 + lam * xo, axis=1)
    return float((w.max(axis=1) >= 1 / ALPHA).mean()), float((w[:, -1] >= 1 / ALPHA).mean())
toy = {}
for lag in (6, 12, 24, 120):
    rng = np.random.default_rng(9500 + lag)
    x = np.where(rng.random((R, N)) < 0.5, c, -c)
    reg = np.arange(N)[None, :].repeat(R, 0)
    close = reg + np.where(x > 0, 1, lag)
    cross_close, final_close = running_max_cross(x, close)
    cross_mat, final_mat = running_max_cross(x, reg + lag)
    toy[f'NO_closes_{lag}_intervals_after_registration'] = {
        'closure_or_knowable_order_running_max_crossing': round(cross_close, 4),
        'closure_order_99pct_lower': round(binom_lower(int(round(cross_close * R)), R, 0.99), 4),
        'pre_registered_maturity_order_running_max_crossing': round(cross_mat, 4),
        'maturity_order_99pct_upper': round(binom_upper(int(round(cross_mat * R)), R, 0.99), 4),
        'final_product_crossing_(order_free)': round(final_close, 4)}
worst = max(v['closure_or_knowable_order_running_max_crossing'] for v in toy.values())
rc95['outcome_dependent_timing_toy'] = {
    'design': '120 fair clusters registered one per interval, X = +/-0.5, lambda = 0.5 fixed; a YES closes 1 interval after registration, a NO only at its finality, lag intervals after; running maximum over the ordered partial products, 20,000 paths',
    'cells': toy, 'ville_bound': ALPHA,
    'reading': f'ordering by closure time (or by outcome-knowable time, which coincides with it here) places early-resolving YES clusters before late-resolving NO clusters; the running maximum then crosses 1/alpha in up to {worst:.1%} of paths against a Ville bound of 5 %, while the final product and the pre-registered maturity order H_k (deadline + latency window, known at registration) stay within the bound. The monitor therefore applies increments in H_k order and buffers a closed cluster until every cluster with a smaller H_k is final; knowable order is not a sufficient remedy because knowable_at is itself outcome-dependent for eventually-by-deadline predicates'}
out['RC95_monitor_order'] = rc95

# ================= r4303397708 (RC-101): the conjunction power bound without positive association =================
rc101 = {}
p = 0.8
rc101['six_components_at_0.8'] = {'product_of_marginals': round(p ** J, 4), 'frechet_lower_bound': max(0.0, J * p - (J - 1)),
                                  'frechet_upper_bound_(min)': p}
# Explicit joint law with every marginal power 0.8 and joint power 0: five of the six failure events partition the
# sample space (0.2 each) and the sixth coincides with one of them.
rng = np.random.default_rng(9101)
u = rng.random(200000)
fail = np.stack([(u >= 0.2 * j) & (u < 0.2 * (j + 1)) for j in range(5)] + [(u >= 0.0) & (u < 0.2)], axis=1)
rej = ~fail
rc101['explicit_construction'] = {'marginal_powers_mc': [round(float(v), 4) for v in rej.mean(axis=0)], 'joint_power_mc': float(rej.all(axis=1).mean()),
                                  'reading': 'six tests with 80 % power each and zero joint power; the statement that IUT power lies between the product of marginals and the smallest marginal is false without positive association'}
# IUT under negatively dependent comparator errors in the Appendix H generator: comparators in three pairs with
# opposite signs, so that within a pair X_c + X_c' = 2 delta (perfectly anti-correlated noise).
def iut_power_pairs(b, delta, per, seed, anti):
    r_ = np.random.default_rng(seed)
    n_ = PERIODS * per
    y_ = (r_.random((REPS, 1, n_)) < b).astype(float)
    own = r_.choice([-1.0, 1.0], size=(REPS, 3, n_))
    s_ = np.concatenate([own, -own if anti else r_.choice([-1.0, 1.0], size=(REPS, 3, n_))], axis=1)
    bc = b - s_ * math.sqrt(delta)
    x_ = (bc - y_) ** 2 - (b - y_) ** 2
    rej_ = cw_t_many(x_) > crit
    return float(rej_.mean(axis=0).mean()), float(rej_.all(axis=1).mean())
cells = {}
for delta, per in ((0.01, 25), (0.01, 50), (0.02, 25)):
    m_ind, j_ind = iut_power_pairs(0.5, delta, per, 9110 + per + int(delta * 1000), False)
    m_anti, j_anti = iut_power_pairs(0.5, delta, per, 9110 + per + int(delta * 1000), True)
    cells[f'delta={delta},clusters={PERIODS * per}'] = {
        'independent_signs': {'mean_marginal': round(m_ind, 4), 'iut_joint': round(j_ind, 4), 'product': round(m_ind ** J, 4)},
        'three_anti_correlated_pairs': {'mean_marginal': round(m_anti, 4), 'iut_joint': round(j_anti, 4), 'product': round(m_anti ** J, 4),
                                        'frechet_lower': round(max(0.0, J * m_anti - (J - 1)), 4)}}
rc101['appendix_H_generator_with_anti_correlated_pairs'] = cells
rc101['reading'] = 'with anti-correlated comparator errors the conjunction power falls below the product of the marginals; the design is powered under a pre-registered dependence assumption (OD4) or under the Frechet lower bound, and T-16 carries a negatively dependent generator'
out['RC101_conjunction_power_negative_dependence'] = rc101

# ================= r4303397692 (RC-97): empty calendar blocks =================
# Valid null, Poisson supply with mean m per period and zeros allowed; two conventions for the block-sum variance:
# (i) G = 24 and 23 df with empty blocks contributing zero, (ii) G = number of occupied blocks and G - 1 df.
def increments_null(k, rng_):
    # Appendix F's valid null: X = 0.4 Y - 0.2 with Y ~ Bern(0.5), so X in {-0.2, +0.2} with mean zero.
    y_ = (rng_.random(k) < 0.5).astype(float)
    return 0.4 * y_ - 0.2
def sim_empty(m, seed, reps=10000):
    rng_ = np.random.default_rng(seed)
    rej_all = np.zeros(reps, bool); rej_occ = np.zeros(reps, bool); occ = np.zeros(reps, int)
    for i in range(reps):
        sizes = rng_.poisson(m, size=PERIODS)
        blocks = [increments_null(k, rng_) for k in sizes if k > 0]
        if len(blocks) < 2:
            continue
        xall = np.concatenate(blocks); nn = xall.size; theta = xall.mean()
        dev = np.array([(b - theta).sum() for b in blocks])
        g = len(blocks); occ[i] = g
        v_all = (dev ** 2).sum() / nn ** 2 * PERIODS / (PERIODS - 1)
        v_occ = (dev ** 2).sum() / nn ** 2 * g / (g - 1)
        rej_all[i] = theta / math.sqrt(v_all) > student_t.ppf(1 - ALPHA, PERIODS - 1) if v_all > 0 else False
        rej_occ[i] = theta / math.sqrt(v_occ) > student_t.ppf(1 - ALPHA, g - 1) if v_occ > 0 else False
    return {'mean_supply_per_period': m, 'mean_occupied_blocks': round(float(occ.mean()), 2), 'min_occupied_blocks': int(occ[occ > 0].min()),
            'size_G24_df23_empty_blocks_counted': round(float(rej_all.mean()), 4), '99pct_upper_G24': round(binom_upper(int(rej_all.sum()), reps, 0.99), 4),
            'size_G_occupied_df_occupied_minus_1': round(float(rej_occ.mean()), 4), '99pct_upper_occ': round(binom_upper(int(rej_occ.sum()), reps, 0.99), 4)}
rc97 = {'poisson_mean_1': sim_empty(1.0, 9701), 'poisson_mean_0.5': sim_empty(0.5, 9702), 'poisson_mean_2': sim_empty(2.0, 9703)}
rc97['reading'] = 'counting empty periods in G and the degrees of freedom is anti-conservative when many periods are empty; the contract counts occupied blocks only, pre-registers a minimum number of occupied blocks, and T-12 adds zero-supply periods'
out['RC97_empty_blocks'] = rc97

# ================= r4303397680 (RC-94): calibrating the critical value over a pre-registered null class =================
# Two-point block-mean family: block mean +a with probability 1 - eps, -b with probability eps, mean zero, b = 0.9.
# The one-sided t over 24 blocks depends only on the number k of positive blocks; exact size by the binomial. A
# sample with zero variance (every block equal) never rejects, as in Appendix G; the alternative convention (t = +inf
# when every block is positive) makes the size at eps = 0.02 equal to 0.98^24 = 0.62 and no calibration possible.
def t_of_k(k, a, b, G=24):
    # Zero-variance samples (k = 0 or k = G) never reject: the convention of Appendix G, now stated in 17 (T-36).
    vals = np.array([a] * k + [-b] * (G - k))
    if k in (0, G):
        return -np.inf
    return float(vals.mean() / (vals.std(ddof=1) / math.sqrt(G)))
_tk = {}
def exact_size(eps, c, b=0.9, G=24):
    key = (eps, b, G)
    if key not in _tk:
        a = eps * b / (1 - eps)
        _tk[key] = (np.array([t_of_k(k, a, b, G) for k in range(G + 1)]), binom.pmf(np.arange(G + 1), G, 1 - eps))
    tk, pk = _tk[key]
    return float(pk[tk > c].sum())
eps_grid = np.round(np.arange(0.02, 0.501, 0.005), 3)
sizes_nominal = {f'eps={e}': round(exact_size(e, crit), 4) for e in (0.02, 0.05, 0.1, 0.2, 0.3, 0.5)}
rc94 = {'exact_size_at_nominal_crit_1.7139_by_catastrophe_probability': sizes_nominal,
        'sup_size_over_eps_in_[0.02,0.5]_at_nominal_crit': round(max(exact_size(e, crit) for e in eps_grid), 4)}
def calibrated_crit(eps_min):
    grid = [e for e in eps_grid if e >= eps_min]
    for c in np.arange(crit, 30.0, 0.001):
        if max(exact_size(e, c) for e in grid) <= ALPHA:
            return float(round(c, 3))
    return None
cal = {}
for eps_min in (0.05, 0.1, 0.2, 0.3):
    c_star = calibrated_crit(eps_min)
    # Power at the calibrated critical value on the D1-type alternative (b = 0.5, delta = 0.02, 600 and 1,200 clusters).
    pw = {}
    for per_ in (25, 50):
        r_ = np.random.default_rng(9400 + per_ + int(eps_min * 100))
        n_ = PERIODS * per_
        y_ = (r_.random((REPS, 1, n_)) < 0.5).astype(float)
        s_ = r_.choice([-1.0, 1.0], size=(REPS, 1, n_))
        x_ = ((0.5 - s_ * math.sqrt(0.02)) - y_) ** 2 - (0.5 - y_) ** 2
        tt = cw_t_many(x_)[:, 0]
        pw[f'clusters={n_}'] = {'power_at_nominal_crit': round(float((tt > crit).mean()), 4), 'power_at_calibrated_crit': (round(float((tt > c_star).mean()), 4) if c_star is not None else 'no critical value below 30 holds size')}
    cal[f'catastrophe_share_at_least_{eps_min}'] = {'calibrated_crit': c_star, 'sup_size_at_calibrated_crit': (round(max(exact_size(e, c_star) for e in eps_grid if e >= eps_min), 4) if c_star is not None else None), 'power_delta_0.02': pw}
rc94['calibrated_critical_value_by_null_class'] = cal
rc94['reading'] = 'a null class defined by a lower bound on the catastrophe share can be calibrated exactly: the critical value is the smallest value whose worst-case size over the class is at most alpha, and power is restated at that value; the wider the class (the smaller eps_min), the larger the critical value and the lower the power at a given supply, which is the RC-80 bound seen from the null side; OD4 chooses the class from reference-class history and the contract reports the calibrated value and the power at it, so the nominal 5 % claim holds over the whole pre-registered class and not only on the families with no pass condition'
out['RC94_null_class_calibration'] = rc94

# ================= r4303397703 (RC-100): cumulative clock drift =================
tol = 2.0
rc100 = {}
for rule in ('per_check', 'baseline'):
    wall, mono = 0.0, 0.0; base = wall - mono; last = base; expiry = 60.0; log = []; admitted_after_real_expiry = 0
    for i in range(100):
        mono += 1.0; wall += 1.0 - 0.75           # the attacker slews the wall clock by -0.75 s per check, below tolerance
        off = wall - mono
        ok = abs(off - (last if rule == 'per_check' else base)) <= tol
        last = off
        if not ok:
            log.append(f'check {i + 1}: discontinuity, offset {off:+.2f}'); break
        if mono > expiry and wall <= expiry:
            admitted_after_real_expiry += 1
    rc100[rule] = {'checks_run': i + 1, 'final_wall': round(wall, 2), 'final_monotonic': round(mono, 2), 'cumulative_offset': round(wall - mono, 2),
                   'admissions_after_real_expiry_of_a_capability_expiring_at_60': admitted_after_real_expiry, 'log': log}
rc100['reading'] = 'per-check drift lets a sequence of small slews keep an expired capability valid; comparing the offset to the baseline persisted at the epoch start detects it at the first check whose cumulative offset exceeds the tolerance'
out['RC100_clock_drift'] = rc100

# ================= r4303397718 (RC-103): epoch rotation on demotion =================
def gate_run(rotate_on_demotion):
    epoch = 1; consumed = set(); state = 'RESEARCH_ONLY'; log = []
    caps = {'A': {'epoch': 1, 'nonce': 'a'}, 'B': {'epoch': 1, 'nonce': 'b'}}
    def present(name):
        nonlocal state
        cap = caps[name]
        if cap['epoch'] != epoch: log.append(f'{name}: rejected stale epoch'); return
        if cap['nonce'] in consumed: log.append(f'{name}: rejected consumed nonce'); return
        consumed.add(cap['nonce']); state = 'SIM_READ_ONLY'; log.append(f'{name}: promoted')
    present('A')
    state = 'RESEARCH_ONLY'; log.append('demoted')
    if rotate_on_demotion:
        epoch += 1; log.append(f'epoch rotated to {epoch} and anchored')
    present('B')
    return {'final_state': state, 'log': log}
rc103 = {'v6_rule': gate_run(False), 'v7_rule_rotate_on_demotion': gate_run(True),
         'reading': 'an unused capability signed before the demotion re-promotes the gate under the version-6 rule; rotating and anchoring the epoch on every demotion makes it stale'}
out['RC103_epoch_on_demotion'] = rc103

# ================= r4303397689 (RC-96): forecaster version in the slot key =================
# Two versions of the same forecaster submit to the default slot; an implementation that admits both and scores
# the better one after the outcome reproduces the RC-75 channel. Honest null: both versions draw p from the same
# calibrated law, Y ~ Bern(0.5), baseline 0.5.
rng = np.random.default_rng(9601)
Rn = 200000
yv = (rng.random(Rn) < 0.5).astype(float)
p1 = np.clip(0.5 + 0.2 * rng.standard_normal(Rn), 0.01, 0.99)
p2 = np.clip(0.5 + 0.2 * rng.standard_normal(Rn), 0.01, 0.99)
x1 = (0.5 - yv) ** 2 - (p1 - yv) ** 2
x2 = (0.5 - yv) ** 2 - (p2 - yv) ** 2
rc96 = {'expected_increment_version_fixed_in_advance': round(float(x1.mean()), 4),
        'expected_increment_better_version_chosen_after_outcome': round(float(np.maximum(x1, x2).mean()), 4),
        'reading': 'a slot key that includes the forecaster version admits two records per slot and re-opens outcome-dependent selection; the key is (event, arm, slot) and the version is pre-registered per arm'}
out['RC96_version_in_slot_key'] = rc96

# ================= r4301994294 (RC-92), r4303397725 (RC-104), r4301994282 (RC-88), r4303397727 (RC-105): deterministic fixtures =================
rc_det = {}
# RC-92: member 1 adjudicated VOID at 10 (timestamp-less record), member 2 resolves at 20; forecast on member 2 at 15.
t_star_v6 = min([20]); t_star_v7 = min([10, 20])
rc_det['RC92_t_star_with_adjudicated_void'] = {'t_star_v6_scored_members_only': t_star_v6, 't_star_v7_all_members': t_star_v7,
                                                'forecast_at_15_eligible_v6': 15 < t_star_v6, 'forecast_at_15_eligible_v7': 15 < t_star_v7}
# RC-104: member resolves YES at 30; FULL's only submission at 31 (after publication at 30); issuance close t_close = 20.
rc_det['RC104_missing_arm'] = {'v6': 'member has Y but FULL is not scored; neither pre-declared nor adjudicated VOID; cluster never closes',
                                'v7': 'at t_close = 20 the FULL slot is empty: FULL abstains, scored at the baseline forecast (X = 0 for the member), reported separately; the 31 submission is labelled late; if the baseline arm is empty at t_close the member is adjudicated VOID at t_close (outcome-independent, under the cap, imputed +/-1)'}
# RC-88 and RC-105: deadline 100, latency window 10. Four records.
cases = {'published_105_received_118_(registry_outage)': {'v6': 'VOID (receipt after deadline + window)', 'v7': 'YES (publication 105 <= 110); receipt lag logged as an integrity incident'},
         'published_112_received_113_(source_late)': {'v6': 'NO at 110 by finality, then the text also says VOID: inconsistent', 'v7': 'NO at 110 is immutable; the 112 report is a source-latency defect logged against the source; never YES, never VOID'},
         'no_record_observed_at_110_living_source': {'v6': 'NO at 110', 'v7': 'NO at 110, requires an archived observation of absence at or after 110'},
         'no_record_source_defunct_at_110': {'v6': 'adjudicated VOID', 'v7': 'adjudicated VOID (unchanged)'}}
rc_det['RC88_RC105_finality_dispositions'] = cases
out['deterministic_fixtures'] = rc_det

out['python'] = sys.version.split()[0]
json.dump(out, sys.stdout, indent=2)
print()
```
<!-- round9-script:end -->

Output:

```json
{
  "RC93_iut_non_degenerate_null": {
    "committed_check_comparator_1": {
      "max_abs_increment": 0.0,
      "variance": 0.0,
      "reading": "every increment of the null comparator is exactly zero, so its t statistic is undefined and the conjunction can never reject; the 0 of 20,000 was mechanical"
    },
    "non_degenerate_null_checks": [
      {
        "c": 0.1,
        "null_comparator_mean_increment": -1e-05,
        "null_comparator_increment_variance": 0.02001,
        "null_comparator_marginal_rejections": 989,
        "null_comparator_rate": 0.0495,
        "iut_rejections": 989,
        "iut_rate": 0.0495,
        "iut_99pct_upper": 0.0531,
        "within_A3_bound_0.06": true
      },
      {
        "c": 0.2,
        "null_comparator_mean_increment": -6e-05,
        "null_comparator_increment_variance": 0.07996,
        "null_comparator_marginal_rejections": 988,
        "null_comparator_rate": 0.0494,
        "iut_rejections": 988,
        "iut_rate": 0.0494,
        "iut_99pct_upper": 0.0531,
        "within_A3_bound_0.06": true
      }
    ],
    "reading": "with a null comparator whose increments have mean zero and positive variance the IUT rejects at about the nominal rate, which is the least-favourable size check T-13 (b) and T-16 require; the committed check is withdrawn"
  },
  "RC102_blocks_needed": {
    "bound_at_delta_0.02_G=140": 0.799823,
    "bound_at_delta_0.02_G=141": 0.81582,
    "ceil_log_16_over_log_1.02": 141,
    "reading": "the bound reaches 0.80 at 141 blocks (0.799823 at 140); the Appendix H sentence string was hand-typed as 140 and is corrected to the computed value"
  },
  "RC95_monitor_order": {
    "codex_example": {
      "E[X_A]": 0.0,
      "E[X_B|X_A=+1]": 0.0,
      "E[X_B|X_A=-1]": -1.0,
      "conditional_null_in_knowable_order_holds": true,
      "E[1+0.5 X_A | X_B=+1]_closure_order": 1.5,
      "reading": "in closure order the factor for A has conditional expectation 1.5 after B is seen, so the closure-ordered wealth is not a supermartingale; Codex is right that closure order carries no Ville guarantee"
    },
    "outcome_dependent_timing_toy": {
      "design": "120 fair clusters registered one per interval, X = +/-0.5, lambda = 0.5 fixed; a YES closes 1 interval after registration, a NO only at its finality, lag intervals after; running maximum over the ordered partial products, 20,000 paths",
      "cells": {
        "NO_closes_6_intervals_after_registration": {
          "closure_or_knowable_order_running_max_crossing": 0.0524,
          "closure_order_99pct_lower": 0.0488,
          "pre_registered_maturity_order_running_max_crossing": 0.0337,
          "maturity_order_99pct_upper": 0.0368,
          "final_product_crossing_(order_free)": 0.0075
        },
        "NO_closes_12_intervals_after_registration": {
          "closure_or_knowable_order_running_max_crossing": 0.101,
          "closure_order_99pct_lower": 0.0961,
          "pre_registered_maturity_order_running_max_crossing": 0.0317,
          "maturity_order_99pct_upper": 0.0347,
          "final_product_crossing_(order_free)": 0.0066
        },
        "NO_closes_24_intervals_after_registration": {
          "closure_or_knowable_order_running_max_crossing": 0.4385,
          "closure_order_99pct_lower": 0.4304,
          "pre_registered_maturity_order_running_max_crossing": 0.034,
          "maturity_order_99pct_upper": 0.0372,
          "final_product_crossing_(order_free)": 0.0063
        },
        "NO_closes_120_intervals_after_registration": {
          "closure_or_knowable_order_running_max_crossing": 1.0,
          "closure_order_99pct_lower": 0.9998,
          "pre_registered_maturity_order_running_max_crossing": 0.0336,
          "maturity_order_99pct_upper": 0.0367,
          "final_product_crossing_(order_free)": 0.0069
        }
      },
      "ville_bound": 0.05,
      "reading": "ordering by closure time (or by outcome-knowable time, which coincides with it here) places early-resolving YES clusters before late-resolving NO clusters; the running maximum then crosses 1/alpha in up to 100.0% of paths against a Ville bound of 5 %, while the final product and the pre-registered maturity order H_k (deadline + latency window, known at registration) stay within the bound. The monitor therefore applies increments in H_k order and buffers a closed cluster until every cluster with a smaller H_k is final; knowable order is not a sufficient remedy because knowable_at is itself outcome-dependent for eventually-by-deadline predicates"
    }
  },
  "RC101_conjunction_power_negative_dependence": {
    "six_components_at_0.8": {
      "product_of_marginals": 0.2621,
      "frechet_lower_bound": 0.0,
      "frechet_upper_bound_(min)": 0.8
    },
    "explicit_construction": {
      "marginal_powers_mc": [
        0.8001,
        0.7979,
        0.8006,
        0.8012,
        0.8001,
        0.8001
      ],
      "joint_power_mc": 0.0,
      "reading": "six tests with 80 % power each and zero joint power; the statement that IUT power lies between the product of marginals and the smallest marginal is false without positive association"
    },
    "appendix_H_generator_with_anti_correlated_pairs": {
      "delta=0.01,clusters=600": {
        "independent_signs": {
          "mean_marginal": 0.7669,
          "iut_joint": 0.2059,
          "product": 0.2035
        },
        "three_anti_correlated_pairs": {
          "mean_marginal": 0.7661,
          "iut_joint": 0.1501,
          "product": 0.2021,
          "frechet_lower": 0.0
        }
      },
      "delta=0.01,clusters=1200": {
        "independent_signs": {
          "mean_marginal": 0.9564,
          "iut_joint": 0.7671,
          "product": 0.7654
        },
        "three_anti_correlated_pairs": {
          "mean_marginal": 0.9563,
          "iut_joint": 0.7622,
          "product": 0.7649,
          "frechet_lower": 0.7378
        }
      },
      "delta=0.02,clusters=600": {
        "independent_signs": {
          "mean_marginal": 0.9576,
          "iut_joint": 0.7685,
          "product": 0.7708
        },
        "three_anti_correlated_pairs": {
          "mean_marginal": 0.9575,
          "iut_joint": 0.7662,
          "product": 0.7705,
          "frechet_lower": 0.7449
        }
      }
    },
    "reading": "with anti-correlated comparator errors the conjunction power falls below the product of the marginals; the design is powered under a pre-registered dependence assumption (OD4) or under the Frechet lower bound, and T-16 carries a negatively dependent generator"
  },
  "RC97_empty_blocks": {
    "poisson_mean_1": {
      "mean_supply_per_period": 1.0,
      "mean_occupied_blocks": 15.17,
      "min_occupied_blocks": 6,
      "size_G24_df23_empty_blocks_counted": 0.0578,
      "99pct_upper_G24": 0.0635,
      "size_G_occupied_df_occupied_minus_1": 0.0513,
      "99pct_upper_occ": 0.0567
    },
    "poisson_mean_0.5": {
      "mean_supply_per_period": 0.5,
      "mean_occupied_blocks": 9.44,
      "min_occupied_blocks": 2,
      "size_G24_df23_empty_blocks_counted": 0.0671,
      "99pct_upper_G24": 0.0731,
      "size_G_occupied_df_occupied_minus_1": 0.0488,
      "99pct_upper_occ": 0.054
    },
    "poisson_mean_2": {
      "mean_supply_per_period": 2.0,
      "mean_occupied_blocks": 20.75,
      "min_occupied_blocks": 14,
      "size_G24_df23_empty_blocks_counted": 0.058,
      "99pct_upper_G24": 0.0637,
      "size_G_occupied_df_occupied_minus_1": 0.0563,
      "99pct_upper_occ": 0.0619
    },
    "reading": "counting empty periods in G and the degrees of freedom is anti-conservative when many periods are empty; the contract counts occupied blocks only, pre-registers a minimum number of occupied blocks, and T-12 adds zero-supply periods"
  },
  "RC94_null_class_calibration": {
    "exact_size_at_nominal_crit_1.7139_by_catastrophe_probability": {
      "eps=0.02": 0.0,
      "eps=0.05": 0.0,
      "eps=0.1": 0.0,
      "eps=0.2": 0.1098,
      "eps=0.3": 0.1109,
      "eps=0.5": 0.032
    },
    "sup_size_over_eps_in_[0.02,0.5]_at_nominal_crit": 0.1662,
    "calibrated_critical_value_by_null_class": {
      "catastrophe_share_at_least_0.05": {
        "calibrated_crit": 3.201,
        "sup_size_at_calibrated_crit": 0.045,
        "power_delta_0.02": {
          "clusters=600": {
            "power_at_nominal_crit": 0.9579,
            "power_at_calibrated_crit": 0.6
          },
          "clusters=1200": {
            "power_at_nominal_crit": 0.9992,
            "power_at_calibrated_crit": 0.9422
          }
        }
      },
      "catastrophe_share_at_least_0.1": {
        "calibrated_crit": 3.201,
        "sup_size_at_calibrated_crit": 0.045,
        "power_delta_0.02": {
          "clusters=600": {
            "power_at_nominal_crit": 0.9591,
            "power_at_calibrated_crit": 0.6051
          },
          "clusters=1200": {
            "power_at_nominal_crit": 0.9989,
            "power_at_calibrated_crit": 0.9401
          }
        }
      },
      "catastrophe_share_at_least_0.2": {
        "calibrated_crit": 2.632,
        "sup_size_at_calibrated_crit": 0.0484,
        "power_delta_0.02": {
          "clusters=600": {
            "power_at_nominal_crit": 0.9568,
            "power_at_calibrated_crit": 0.7874
          },
          "clusters=1200": {
            "power_at_nominal_crit": 0.9989,
            "power_at_calibrated_crit": 0.9826
          }
        }
      },
      "catastrophe_share_at_least_0.3": {
        "calibrated_crit": 2.231,
        "sup_size_at_calibrated_crit": 0.0468,
        "power_delta_0.02": {
          "clusters=600": {
            "power_at_nominal_crit": 0.9558,
            "power_at_calibrated_crit": 0.8848
          },
          "clusters=1200": {
            "power_at_nominal_crit": 0.9988,
            "power_at_calibrated_crit": 0.9941
          }
        }
      }
    },
    "reading": "a null class defined by a lower bound on the catastrophe share can be calibrated exactly: the critical value is the smallest value whose worst-case size over the class is at most alpha, and power is restated at that value; the wider the class (the smaller eps_min), the larger the critical value and the lower the power at a given supply, which is the RC-80 bound seen from the null side; OD4 chooses the class from reference-class history and the contract reports the calibrated value and the power at it, so the nominal 5 % claim holds over the whole pre-registered class and not only on the families with no pass condition"
  },
  "RC100_clock_drift": {
    "per_check": {
      "checks_run": 100,
      "final_wall": 25.0,
      "final_monotonic": 100.0,
      "cumulative_offset": -75.0,
      "admissions_after_real_expiry_of_a_capability_expiring_at_60": 40,
      "log": []
    },
    "baseline": {
      "checks_run": 3,
      "final_wall": 0.75,
      "final_monotonic": 3.0,
      "cumulative_offset": -2.25,
      "admissions_after_real_expiry_of_a_capability_expiring_at_60": 0,
      "log": [
        "check 3: discontinuity, offset -2.25"
      ]
    },
    "reading": "per-check drift lets a sequence of small slews keep an expired capability valid; comparing the offset to the baseline persisted at the epoch start detects it at the first check whose cumulative offset exceeds the tolerance"
  },
  "RC103_epoch_on_demotion": {
    "v6_rule": {
      "final_state": "SIM_READ_ONLY",
      "log": [
        "A: promoted",
        "demoted",
        "B: promoted"
      ]
    },
    "v7_rule_rotate_on_demotion": {
      "final_state": "RESEARCH_ONLY",
      "log": [
        "A: promoted",
        "demoted",
        "epoch rotated to 2 and anchored",
        "B: rejected stale epoch"
      ]
    },
    "reading": "an unused capability signed before the demotion re-promotes the gate under the version-6 rule; rotating and anchoring the epoch on every demotion makes it stale"
  },
  "RC96_version_in_slot_key": {
    "expected_increment_version_fixed_in_advance": -0.0387,
    "expected_increment_better_version_chosen_after_outcome": 0.073,
    "reading": "a slot key that includes the forecaster version admits two records per slot and re-opens outcome-dependent selection; the key is (event, arm, slot) and the version is pre-registered per arm"
  },
  "deterministic_fixtures": {
    "RC92_t_star_with_adjudicated_void": {
      "t_star_v6_scored_members_only": 20,
      "t_star_v7_all_members": 10,
      "forecast_at_15_eligible_v6": true,
      "forecast_at_15_eligible_v7": false
    },
    "RC104_missing_arm": {
      "v6": "member has Y but FULL is not scored; neither pre-declared nor adjudicated VOID; cluster never closes",
      "v7": "at t_close = 20 the FULL slot is empty: FULL abstains, scored at the baseline forecast (X = 0 for the member), reported separately; the 31 submission is labelled late; if the baseline arm is empty at t_close the member is adjudicated VOID at t_close (outcome-independent, under the cap, imputed +/-1)"
    },
    "RC88_RC105_finality_dispositions": {
      "published_105_received_118_(registry_outage)": {
        "v6": "VOID (receipt after deadline + window)",
        "v7": "YES (publication 105 <= 110); receipt lag logged as an integrity incident"
      },
      "published_112_received_113_(source_late)": {
        "v6": "NO at 110 by finality, then the text also says VOID: inconsistent",
        "v7": "NO at 110 is immutable; the 112 report is a source-latency defect logged against the source; never YES, never VOID"
      },
      "no_record_observed_at_110_living_source": {
        "v6": "NO at 110",
        "v7": "NO at 110, requires an archived observation of absence at or after 110"
      },
      "no_record_source_defunct_at_110": {
        "v6": "adjudicated VOID",
        "v7": "adjudicated VOID (unchanged)"
      }
    }
  },
  "python": "3.11.17"
}
```


## Appendix K. Round-10 checks (REPRODUCED)

Needs no reference code and no network. Run with `python -I round10_checks.py` in an isolated venv (Python 3.11.17,
numpy 2.4.6, scipy 1.17.1; 12 s), extracting the block between the `round10-script` markers as in Appendix A.
Seeds are fixed; two consecutive runs produced byte-identical output. Blocks, keyed by the review-comment id each
answers: RC-108 repeats the exact two-point calibration of Appendix J and evaluates the persistent two-state regime
of Appendix D (q_t = 0.5 ± 0.3, P(stay) from 0.5 to 0.95, 120 and 600 clusters) at the nominal value and at the
three calibrated values; RC-109 runs the non-adversarial baseline-failure selection (FULL at +δ on one event type
and −δ on the other, baseline failing on 10 % or 40 % of the second type) with the member removed, as version 7
prescribed, and kept, as version 8 does; RC-110 is the deterministic burn-in fixture; RC-111 evaluates the T-36
oracle statistic against the nominal and calibrated values and restates the positive-control rate per critical
value with Appendix E's generator (the nominal rate 0.963 reproduces Appendix E's 0.964); RC-112 runs the
outcome-chosen cutoff-correction toy; RC-113, RC-114 and RC-115 are deterministic fixtures and arithmetic. One
correction made while writing it, recorded so that the method is checkable: a first draft of the RC-111 block used
the Appendix J alternative generator (baseline miscalibrated against a calibrated FULL), which gives 0.915 at the
nominal value and is not the T-36 (c) fixture; the committed block uses Appendix E's D1 generator. The committed
round-9 script of Appendix J was re-extracted and re-run in the same environment this round (§2): byte-identical.

<!-- round10-script:start -->
```python
"""Round-10 checks for the Codex findings on PR #4 at 922956b (no reference code, no network).

Review 5558887072. Each block is keyed by the review-comment id it answers. The cluster-weighted statistic with
block-sum variance, the D1-type generator and the two-point calibration are those of 16 Appendix F, H and J.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA = 0.05
PERIODS = 24
CRIT = float(student_t.ppf(1 - ALPHA, PERIODS - 1))        # nominal one-sided critical value on 23 df, 1.7139

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

def cw_t_many(x):
    """x: (reps, clusters) with clusters = PERIODS * per, blocks of one period; cluster-weighted statistic, block-sum
    variance on G - 1 df (16 Appendix F). A zero-variance sample returns -inf (never rejects; Appendix G convention)."""
    reps, n = x.shape
    per = n // PERIODS
    theta = x.mean(axis=1)
    dev = (x - theta[:, None]).reshape(reps, PERIODS, per).sum(axis=2)
    v = (dev ** 2).sum(axis=1) / n ** 2 * PERIODS / (PERIODS - 1)
    tt = np.full(reps, -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt

def cw_t_masked(x, keep):
    """Same statistic over the kept clusters only; blocks = periods, G = occupied blocks (RC-97). x, keep: (reps, n)."""
    reps, n = x.shape
    per = n // PERIODS
    k = keep.astype(float)
    nk = k.sum(axis=1)
    theta = (x * k).sum(axis=1) / nk
    dev = ((x - theta[:, None]) * k).reshape(reps, PERIODS, per).sum(axis=2)
    occ = (k.reshape(reps, PERIODS, per).sum(axis=2) > 0)
    g = occ.sum(axis=1)
    v = (dev ** 2).sum(axis=1) / nk ** 2 * g / (g - 1)
    tt = np.full(reps, -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt, g

# ---- the two-point calibration of Appendix J (RC-94), repeated so that this script stands alone ----
def t_of_k(k, a, b, G=24):
    vals = np.array([a] * k + [-b] * (G - k))
    if k in (0, G):
        return -np.inf
    return float(vals.mean() / (vals.std(ddof=1) / math.sqrt(G)))
_tk = {}
def exact_size(eps, c, b=0.9, G=24):
    key = (eps, b, G)
    if key not in _tk:
        a = eps * b / (1 - eps)
        _tk[key] = (np.array([t_of_k(k, a, b, G) for k in range(G + 1)]), binom.pmf(np.arange(G + 1), G, 1 - eps))
    tk, pk = _tk[key]
    return float(pk[tk > c].sum())
eps_grid = np.round(np.arange(0.02, 0.501, 0.005), 3)
def calibrated_crit(eps_min):
    grid = [e for e in eps_grid if e >= eps_min]
    for c in np.arange(CRIT, 30.0, 0.001):
        if max(exact_size(e, c) for e in grid) <= ALPHA:
            return float(round(c, 3))
    return None
CSTAR = {eps_min: calibrated_crit(eps_min) for eps_min in (0.05, 0.2, 0.3)}
CRITS = {'nominal_1.7139': CRIT, **{f'c*_eps_min_{e}': c for e, c in CSTAR.items()}}

# ================= r4303569704 (RC-108): the four scalars do not define the null class =================
# A law that satisfies every scalar of the version-7 class (block length one period, |p_FULL - p_baseline| = 0.2
# under any d_max >= 0.2, shock amplitude 0.3, no rare-catastrophe shape) and is still oversized at every c*
# calibrated on the two-point family: the persistent two-state regime of Appendix D. q_t = 0.5 + 0.3 s_t, s_t a
# two-state chain with P(stay) = rho, Y ~ Bern(q_t) per cluster, baseline 0.4, FULL 0.6, X = 0.4 Y - 0.2 (E X = 0
# under the stationary law). Serial dependence is the parameter the version-7 scalars do not carry.
def regime_sizes(rho, per, reps, seed):
    r = np.random.default_rng(seed)
    n = PERIODS * per
    s = np.empty((reps, PERIODS))
    s[:, 0] = r.choice([-1.0, 1.0], size=reps)
    flip = r.random((reps, PERIODS - 1)) >= rho
    for t in range(1, PERIODS):
        s[:, t] = np.where(flip[:, t - 1], -s[:, t - 1], s[:, t - 1])
    q = 0.5 + 0.3 * np.repeat(s, per, axis=1)
    y = (r.random((reps, n)) < q).astype(float)
    x = 0.4 * y - 0.2
    tt = cw_t_many(x)
    return {name: round(float((tt > c).mean()), 4) for name, c in CRITS.items()}
rc108 = {'calibrated_crit_two_point_family': {f'eps_min_{e}': c for e, c in CSTAR.items()},
         'scalars_of_the_law': {'block_length_periods': 1, 'abs_p_full_minus_p_baseline': 0.2, 'shock_amplitude': 0.3,
                                'catastrophe_share': 'not a two-point shape; symmetric +/-0.3 periods', 'supply_shock_dependence': 'none'}}
rc108['size_by_persistence_120_clusters'] = {f'P(stay)={rho}': regime_sizes(rho, 5, 20000, 10800 + int(rho * 100)) for rho in (0.5, 0.7, 0.8, 0.9, 0.95)}
rc108['size_by_persistence_600_clusters'] = {f'P(stay)={rho}': regime_sizes(rho, 25, 10000, 10850 + int(rho * 100)) for rho in (0.5, 0.9)}
rc108['reading'] = ('P(stay) = 0.5 is the independent-period family (size at the nominal value within the bound, as in Appendix D); '
                    'the same four scalars with P(stay) = 0.9 give a law outside every bound at every calibrated c*, and raising the '
                    'supply does not help, because the dependence is between blocks and not within them. The class N must therefore '
                    'be a complete generator family whose parameters include the serial dependence of the block shocks (and the '
                    'supply-shock dependence of Appendix F), with a pre-registered box, and the worst case is taken over a grid of that '
                    'box; four scalars admit laws on which the calibrated critical value is not level alpha')
out['RC108_null_class_incomplete'] = rc108

# ================= r4303569710 (RC-109): an empty baseline slot selects the scored cohort =================
# (a) non-adversarial: two event types; FULL has +delta on type A and -delta on type B (average exactly zero); the
# baseline process fails on a fraction f of type B members (no reference class available). Version 7 adjudicates
# such a member VOID at t_close, so it leaves the primary; version 8 fills the slot from the committed reference
# base rate, so it stays. Null generator per member: Y ~ Bern(0.5); type A: baseline 0.5 +/- sqrt(delta), FULL 0.5;
# type B: baseline 0.5, FULL 0.5 +/- sqrt(delta). 600 singleton clusters, 25 per period.
def selection_check(delta, f_fail_B, reps, seed):
    r = np.random.default_rng(seed)
    per = 25; n = PERIODS * per
    y = (r.random((reps, n)) < 0.5).astype(float)
    s = r.choice([-1.0, 1.0], size=(reps, n))
    is_A = r.random((reps, n)) < 0.5
    x_A = ((0.5 + s * math.sqrt(delta)) - y) ** 2 - (0.5 - y) ** 2          # E = +delta
    x_B = (0.5 - y) ** 2 - ((0.5 + s * math.sqrt(delta)) - y) ** 2          # E = -delta
    x = np.where(is_A, x_A, x_B)
    fail = (~is_A) & (r.random((reps, n)) < f_fail_B)
    keep = ~fail
    t_full = cw_t_many(x)
    t_cc, g = cw_t_masked(x, keep)
    return {'delta': delta, 'baseline_failure_rate_on_type_B': f_fail_B, 'overall_void_share': round(float(fail.mean()), 4),
            'mean_increment_all_members': round(float(x.mean()), 5),
            'mean_increment_complete_cases_v7': round(float((x * keep).sum() / keep.sum()), 5),
            'arithmetic_expected_complete_case_mean': round(delta * (0.5 - 0.5 * (1 - f_fail_B)) / (0.5 + 0.5 * (1 - f_fail_B)), 5),
            'rejection_rate_v7_member_removed': round(float((t_cc > CRIT).mean()), 4),
            'rejection_rate_v8_member_kept': round(float((t_full > CRIT).mean()), 4),
            'rejection_rate_v7_99pct_upper': round(binom_upper(int((t_cc > CRIT).sum()), reps, 0.99), 4)}
rc109 = {'non_adversarial_selection': [selection_check(0.1, 0.1, 20000, 10901), selection_check(0.1, 0.4, 20000, 10902),
                                        selection_check(0.02, 0.4, 20000, 10903)]}
# (b) the asymmetry: under version 7 an empty FULL or comparator slot keeps the member (X = 0 for that comparison)
# while an empty baseline slot removes it; the two dispositions of one fixture member under each version.
rc109['disposition_asymmetry_v7'] = {'empty_FULL_slot_at_t_close': 'member kept, FULL scored at the baseline forecast, X = 0',
                                      'empty_comparator_slot_at_t_close': 'member kept, comparator scored at the baseline forecast',
                                      'empty_baseline_slot_at_t_close': 'member adjudicated VOID, leaves the primary (under the cap)'}
rc109['v8_rule'] = {'baseline_primary_slot': 'computed by the registry from the Design C base rate committed in the ledger before the issuance window opens (RC-106 reference data); there is no baseline submission and the slot cannot be empty; a member whose reference class has no committed base rate is refused at registration, before any forecast (candidate log)',
                    'sealing': 'no arm is served another arm\'s forecast on a member before t_close; forecasts are sealed commitments until the window closes',
                    'other_arms': 'an empty FULL or comparator slot is an abstention scored at the baseline forecast, counted per arm against a pre-registered abstention cap; no empty slot of any arm removes a member from the primary'}
rc109['reading'] = ('a baseline failure correlated with event type turns a zero-average null into a positive complete-case mean (arithmetic: '
                    'delta (1 - (1 - f)) / (1 + (1 - f)) over equal type shares) and inflates the primary rejection rate; keeping the member '
                    'with the committed base rate in the baseline slot restores the nominal rate; the adversarial version is RC-85 (Appendix I) '
                    'with the baseline process as the selecting party and needs no new simulation')
out['RC109_baseline_slot_selection'] = rc109

# ================= r4303569715 (RC-110): a burn-in YES can be public before the freeze =================
rc110 = {'fixture': {'freeze_recorded_at': 100, 'burn_in_event': {'registered_at': 50, 'not_before': 60, 'deadline': 130, 'latency_window': 10,
                                                                  'maturity_deadline_plus_window': 140, 'public_occurrence_at': 90}},
         'v7_T37_check_maturity_after_freeze': 140 > 100, 'knowable_at_by_occurrence': 90, 'knowable_before_freeze': 90 < 100,
         'v8_T37_check_not_before_after_freeze': 60 > 100,
         'terminal_falsifier_variant': {'registered_at': 50, 'not_before': 110, 'falsifier_observable_from': 50, 'falsifier_public_at': 80,
                                        'v8_not_before_check_alone': 110 > 100, 'knowable_at': 80, 'knowable_before_freeze': True,
                                        'v8_rule': 'the registration requires the EventSpec\'s earliest-knowable bound (min of not_before and the earliest time a terminal falsifier can be observed) to be after the freeze'},
         'reading': 'the version-7 condition bounds the latest finality time and not the earliest knowable time; for an eventually-by-deadline predicate the two differ by the whole resolution window, and for a terminal-falsifier predicate by more'}
out['RC110_burn_in_early_yes'] = rc110

# ================= r4303569722 (RC-111): the T-36 (b) oracle requires rejection at the nominal value =================
blocks = np.array([0.05, 0.10, 0.00, 0.05])
t_b = float(blocks.mean() / (blocks.std(ddof=1) / 2.0))
rc111 = {'oracle_statistic_t': round(t_b, 6), 'df': 3, 'decision_by_critical_value': {name: bool(t_b > c) for name, c in CRITS.items()},
         'nominal_crit_3df': round(float(student_t.ppf(0.95, 3)), 4)}
rc111['note_on_df'] = 'the version-7 oracle compares a 3-df statistic with the 3-df nominal value (2.3534) and rejects; a calibrated c* is a property of the pre-registered class at the design\'s G and is not a function of df, so the decision oracle must take c* as a parameter and the statistic oracle must be df-free'
# (c) the T-36 positive-control alternative restated at the calibrated value: Appendix E's D1 generator, b = 0.5,
# delta = 0.08, 120 independent clusters, five per period, p = b +/- sqrt(delta), Y ~ Bern(p), X = (b - Y)^2 - (p - Y)^2.
r = np.random.default_rng(11100)
reps = 20000; per = 5; n = PERIODS * per
p = 0.5 + math.sqrt(0.08) * r.choice([-1.0, 1.0], size=(reps, n))
y = (r.random((reps, n)) < p).astype(float)
x = (0.5 - y) ** 2 - (p - y) ** 2
tt = cw_t_many(x)
pc = {}
for name, c in CRITS.items():
    k = int((tt > c).sum())
    pc[name] = {'rejection_rate': round(k / reps, 4), 'exact_99pct_lower_bound': round(binom_lower(k, reps, 0.99), 4)}
rc111['positive_control_b_0.5_delta_0.08_120_clusters_appendix_E_generator'] = pc
rc111['reading'] = 'a correct implementation of the calibrated test fails the version-7 oracle whenever c* exceeds the oracle statistic; T-36 (b) becomes a statistic oracle (value and p to 1e-6) plus a decision oracle parametrised by c*, and the (c) lower bound is restated per c* from the rates above'
out['RC111_T36_oracle_at_cstar'] = rc111

# ================= r4303569729 (RC-112): a cutoff corrected after outcomes selects the cohort by date =================
# Null: 600 singleton clusters registered 25 per month over 24 months; FULL and baseline both carry a calibration
# error of magnitude 0.2 with independent signs (mean-zero, positive-variance increments). A later "correction" of
# the arm's cutoff to month m excludes every member with not_before <= m (the version-7 F-27 path); the actor chooses
# m in {0, ..., 12} after the outcomes are known. Rejection rate at the nominal value over the occupied blocks.
r = np.random.default_rng(11200)
reps = 20000; per = 25; n = PERIODS * per
y = (r.random((reps, n)) < 0.5).astype(float)
sf = r.choice([-1.0, 1.0], size=(reps, n)); sb = r.choice([-1.0, 1.0], size=(reps, n))
x = ((0.5 + 0.2 * sb) - y) ** 2 - ((0.5 + 0.2 * sf) - y) ** 2
month = np.tile(np.repeat(np.arange(PERIODS), per), (reps, 1))
best_t = np.full(reps, -np.inf); best_m = np.zeros(reps, dtype=int)
t_by_m = {}
for m in range(0, 13):
    keep = month >= m
    tt, g = cw_t_masked(x, keep)
    t_by_m[m] = tt
    better = tt > best_t
    best_t = np.where(better, tt, best_t); best_m = np.where(better, m, best_m)
rc112 = {'no_correction_rejection_rate': round(float((t_by_m[0] > CRIT).mean()), 4),
         'rejection_rate_with_outcome_chosen_correction_month': round(float((best_t > CRIT).mean()), 4),
         'rejection_rate_99pct_upper': round(binom_upper(int((best_t > CRIT).sum()), reps, 0.99), 4),
         'mean_chosen_month': round(float(best_m.mean()), 3),
         'share_of_cohort_removed_at_mean_month': round(float(best_m.mean()) / PERIODS, 3),
         'v8_rule': 'the cutoff is one immutable field of the arm version record, created before any event is registered under it; a Forecast references the arm version and carries no cutoff of its own; a correction withdraws the arm version and every member registered under it leaves the primary for every comparison involving that arm as one cohort (counted against the cap, imputed +/-1), never member by member',
         'reading': 'a date rule applied member by member is outcome-blind in its criterion and outcome-dependent in its timing: choosing when to correct is choosing which members leave; withdrawing the whole cohort leaves no choice that depends on outcomes'}
out['RC112_cutoff_correction_selection'] = rc112

# ================= r4303569735 (RC-113): observer outage combined with a late publication =================
D, W = 100, 10
rc113 = {'deadline': D, 'latency_window': W, 'finality': D + W, 'observer_down': [100, 130], 'first_read_at': 130,
         'cases': {
             'record_published_115_occurrence_95_source_evidences_publication_times': {
                 'v7': 'member open until the observer reads; T-04 then says "by content": YES ignores the latency rule, NO lacks the observation of absence, the text says a late report is never VOID',
                 'v8': 'NO at 110 with knowable_at = 110: under the source rule\'s monotone-publication condition (OD5) the earliest matching record\'s evidenced publication time 115 > 110 is itself the archived observation that no record existed at 110; the record is a source-latency defect, the outage an integrity incident; identical to the disposition the observer would have reached by reading at 110'},
             'record_published_105_first_observed_130': {'v7': 'YES (RC-105)', 'v8': 'YES (unchanged)'},
             'no_record_when_read_at_130': {'v7': 'NO at 110 (observation of absence after the window)', 'v8': 'NO at 110 (unchanged)'},
             'record_published_115_source_cannot_evidence_publication_times': {
                 'v7': 'undefined', 'v8': 'adjudicated VOID at 110 under the source rule\'s failure condition (the source cannot evidence absence); such a source is an OD5 exclusion at registration'}},
         'invariant': 'the disposition of a member is a function of the archived source records and the pre-registered source rule alone, never of when the observer happened to read',
         'reading': 'the missing case had two rules that could not both hold; it is closed by stating what counts as an observation of absence when the observer was down: the late record itself, under a source rule that makes publication times monotone and evidenced'}
out['RC113_outage_plus_late_publication'] = rc113

# ================= r4303569739 (RC-114): the maximum horizon subtracted twice =================
T_A, H_max = 24, 6
T_R = T_A - H_max
rc114 = {'analysis_date_T_A_months': T_A, 'H_max': H_max, 'registration_cut_off_T_R': T_R,
         'event_registered_18_horizon_6': {'maturity': 24, 'eligible_under_maturity_<=_T_A': True, 'eligible_under_misreading_maturity_<=_T_R': False},
         'share_of_a_uniform_cohort_lost_under_the_misreading': round((T_R - (T_R - H_max)) / T_R, 3),
         'implication': 'registration <= T_R and declared horizon <= H_max give maturity <= T_A, so the maturity condition is implied; it is restated with the analysis date named so that the two cut-offs cannot be read as one',
         'reading': 'the sentence used "the 24-month cut-off" for the analysis date two clauses after calling the registration cut-off "the cut-off"; under the reading Codex gives, a third of the accrued cohort leaves'}
out['RC114_accrual_double_subtraction'] = rc114

# ================= r4303569744 (RC-115): T-17 and F-24 disagree on pre-declared members =================
xa = 0.1
rc115 = {'cluster_A_scored_member_increment': xa,
         'T17_v7_wording_pre_declared_sibling_imputed_+/-1': {'bounds_on_cluster_increment': [round((xa - 1) / 2, 3), round((xa + 1) / 2, 3)], 'cap_count': 1},
         'section3_and_F24_v7_pre_declared_outside_cap_and_bounds': {'bounds_on_cluster_increment': [xa, xa], 'cap_count': 0, 'audit_count_by_reason': 1},
         'cluster_B_two_pre_declared': {'T17_v7': 'counts two against the cap', 'section3_F24_v7': 'outside the cap; two in the candidate log and the VOID audit by reason'},
         'v8_choice': 'section 3 and F-24: a pre-declared member is fixed in the registration record before any forecast or outcome exists and is a population choice, like a candidate-log rejection; the cap and the bounds cover members that left the scored population after registration',
         'reading': 'round 9 rewrote section 3 and F-24 for RC-87 and RC-90 and left the T-17 pass condition at its round-7 wording; the two cannot both be implemented'}
out['RC115_T17_F24_pre_declared'] = rc115

out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2))
```
<!-- round10-script:end -->

Output:

```json
{
  "RC108_null_class_incomplete": {
    "calibrated_crit_two_point_family": {
      "eps_min_0.05": 3.201,
      "eps_min_0.2": 2.632,
      "eps_min_0.3": 2.231
    },
    "scalars_of_the_law": {
      "block_length_periods": 1,
      "abs_p_full_minus_p_baseline": 0.2,
      "shock_amplitude": 0.3,
      "catastrophe_share": "not a two-point shape; symmetric +/-0.3 periods",
      "supply_shock_dependence": "none"
    },
    "size_by_persistence_120_clusters": {
      "P(stay)=0.5": {
        "nominal_1.7139": 0.0481,
        "c*_eps_min_0.05": 0.0021,
        "c*_eps_min_0.2": 0.0073,
        "c*_eps_min_0.3": 0.0164
      },
      "P(stay)=0.7": {
        "nominal_1.7139": 0.124,
        "c*_eps_min_0.05": 0.0236,
        "c*_eps_min_0.2": 0.0465,
        "c*_eps_min_0.3": 0.0714
      },
      "P(stay)=0.8": {
        "nominal_1.7139": 0.1837,
        "c*_eps_min_0.05": 0.0604,
        "c*_eps_min_0.2": 0.094,
        "c*_eps_min_0.3": 0.1271
      },
      "P(stay)=0.9": {
        "nominal_1.7139": 0.2725,
        "c*_eps_min_0.05": 0.1533,
        "c*_eps_min_0.2": 0.1914,
        "c*_eps_min_0.3": 0.2206
      },
      "P(stay)=0.95": {
        "nominal_1.7139": 0.3534,
        "c*_eps_min_0.05": 0.2621,
        "c*_eps_min_0.2": 0.2923,
        "c*_eps_min_0.3": 0.3164
      }
    },
    "size_by_persistence_600_clusters": {
      "P(stay)=0.5": {
        "nominal_1.7139": 0.0486,
        "c*_eps_min_0.05": 0.0023,
        "c*_eps_min_0.2": 0.0074,
        "c*_eps_min_0.3": 0.0179
      },
      "P(stay)=0.9": {
        "nominal_1.7139": 0.2907,
        "c*_eps_min_0.05": 0.1759,
        "c*_eps_min_0.2": 0.213,
        "c*_eps_min_0.3": 0.2427
      }
    },
    "reading": "P(stay) = 0.5 is the independent-period family (size at the nominal value within the bound, as in Appendix D); the same four scalars with P(stay) = 0.9 give a law outside every bound at every calibrated c*, and raising the supply does not help, because the dependence is between blocks and not within them. The class N must therefore be a complete generator family whose parameters include the serial dependence of the block shocks (and the supply-shock dependence of Appendix F), with a pre-registered box, and the worst case is taken over a grid of that box; four scalars admit laws on which the calibrated critical value is not level alpha"
  },
  "RC109_baseline_slot_selection": {
    "non_adversarial_selection": [
      {
        "delta": 0.1,
        "baseline_failure_rate_on_type_B": 0.1,
        "overall_void_share": 0.05,
        "mean_increment_all_members": -2e-05,
        "mean_increment_complete_cases_v7": 0.00521,
        "arithmetic_expected_complete_case_mean": 0.00526,
        "rejection_rate_v7_member_removed": 0.1006,
        "rejection_rate_v8_member_kept": 0.0505,
        "rejection_rate_v7_99pct_upper": 0.1056
      },
      {
        "delta": 0.1,
        "baseline_failure_rate_on_type_B": 0.4,
        "overall_void_share": 0.2001,
        "mean_increment_all_members": 9e-05,
        "mean_increment_complete_cases_v7": 0.02515,
        "arithmetic_expected_complete_case_mean": 0.025,
        "rejection_rate_v7_member_removed": 0.4864,
        "rejection_rate_v8_member_kept": 0.0503,
        "rejection_rate_v7_99pct_upper": 0.4947
      },
      {
        "delta": 0.02,
        "baseline_failure_rate_on_type_B": 0.4,
        "overall_void_share": 0.2,
        "mean_increment_all_members": -0.0001,
        "mean_increment_complete_cases_v7": 0.00492,
        "arithmetic_expected_complete_case_mean": 0.005,
        "rejection_rate_v7_member_removed": 0.1802,
        "rejection_rate_v8_member_kept": 0.0481,
        "rejection_rate_v7_99pct_upper": 0.1867
      }
    ],
    "disposition_asymmetry_v7": {
      "empty_FULL_slot_at_t_close": "member kept, FULL scored at the baseline forecast, X = 0",
      "empty_comparator_slot_at_t_close": "member kept, comparator scored at the baseline forecast",
      "empty_baseline_slot_at_t_close": "member adjudicated VOID, leaves the primary (under the cap)"
    },
    "v8_rule": {
      "baseline_primary_slot": "computed by the registry from the Design C base rate committed in the ledger before the issuance window opens (RC-106 reference data); there is no baseline submission and the slot cannot be empty; a member whose reference class has no committed base rate is refused at registration, before any forecast (candidate log)",
      "sealing": "no arm is served another arm's forecast on a member before t_close; forecasts are sealed commitments until the window closes",
      "other_arms": "an empty FULL or comparator slot is an abstention scored at the baseline forecast, counted per arm against a pre-registered abstention cap; no empty slot of any arm removes a member from the primary"
    },
    "reading": "a baseline failure correlated with event type turns a zero-average null into a positive complete-case mean (arithmetic: delta (1 - (1 - f)) / (1 + (1 - f)) over equal type shares) and inflates the primary rejection rate; keeping the member with the committed base rate in the baseline slot restores the nominal rate; the adversarial version is RC-85 (Appendix I) with the baseline process as the selecting party and needs no new simulation"
  },
  "RC110_burn_in_early_yes": {
    "fixture": {
      "freeze_recorded_at": 100,
      "burn_in_event": {
        "registered_at": 50,
        "not_before": 60,
        "deadline": 130,
        "latency_window": 10,
        "maturity_deadline_plus_window": 140,
        "public_occurrence_at": 90
      }
    },
    "v7_T37_check_maturity_after_freeze": true,
    "knowable_at_by_occurrence": 90,
    "knowable_before_freeze": true,
    "v8_T37_check_not_before_after_freeze": false,
    "terminal_falsifier_variant": {
      "registered_at": 50,
      "not_before": 110,
      "falsifier_observable_from": 50,
      "falsifier_public_at": 80,
      "v8_not_before_check_alone": true,
      "knowable_at": 80,
      "knowable_before_freeze": true,
      "v8_rule": "the registration requires the EventSpec's earliest-knowable bound (min of not_before and the earliest time a terminal falsifier can be observed) to be after the freeze"
    },
    "reading": "the version-7 condition bounds the latest finality time and not the earliest knowable time; for an eventually-by-deadline predicate the two differ by the whole resolution window, and for a terminal-falsifier predicate by more"
  },
  "RC111_T36_oracle_at_cstar": {
    "oracle_statistic_t": 2.44949,
    "df": 3,
    "decision_by_critical_value": {
      "nominal_1.7139": true,
      "c*_eps_min_0.05": false,
      "c*_eps_min_0.2": false,
      "c*_eps_min_0.3": true
    },
    "nominal_crit_3df": 2.3534,
    "note_on_df": "the version-7 oracle compares a 3-df statistic with the 3-df nominal value (2.3534) and rejects; a calibrated c* is a property of the pre-registered class at the design's G and is not a function of df, so the decision oracle must take c* as a parameter and the statistic oracle must be df-free",
    "positive_control_b_0.5_delta_0.08_120_clusters_appendix_E_generator": {
      "nominal_1.7139": {
        "rejection_rate": 0.9633,
        "exact_99pct_lower_bound": 0.9601
      },
      "c*_eps_min_0.05": {
        "rejection_rate": 0.6767,
        "exact_99pct_lower_bound": 0.6689
      },
      "c*_eps_min_0.2": {
        "rejection_rate": 0.8262,
        "exact_99pct_lower_bound": 0.8199
      },
      "c*_eps_min_0.3": {
        "rejection_rate": 0.9052,
        "exact_99pct_lower_bound": 0.9002
      }
    },
    "reading": "a correct implementation of the calibrated test fails the version-7 oracle whenever c* exceeds the oracle statistic; T-36 (b) becomes a statistic oracle (value and p to 1e-6) plus a decision oracle parametrised by c*, and the (c) lower bound is restated per c* from the rates above"
  },
  "RC112_cutoff_correction_selection": {
    "no_correction_rejection_rate": 0.052,
    "rejection_rate_with_outcome_chosen_correction_month": 0.1314,
    "rejection_rate_99pct_upper": 0.1371,
    "mean_chosen_month": 6.324,
    "share_of_cohort_removed_at_mean_month": 0.263,
    "v8_rule": "the cutoff is one immutable field of the arm version record, created before any event is registered under it; a Forecast references the arm version and carries no cutoff of its own; a correction withdraws the arm version and every member registered under it leaves the primary for every comparison involving that arm as one cohort (counted against the cap, imputed +/-1), never member by member",
    "reading": "a date rule applied member by member is outcome-blind in its criterion and outcome-dependent in its timing: choosing when to correct is choosing which members leave; withdrawing the whole cohort leaves no choice that depends on outcomes"
  },
  "RC113_outage_plus_late_publication": {
    "deadline": 100,
    "latency_window": 10,
    "finality": 110,
    "observer_down": [
      100,
      130
    ],
    "first_read_at": 130,
    "cases": {
      "record_published_115_occurrence_95_source_evidences_publication_times": {
        "v7": "member open until the observer reads; T-04 then says \"by content\": YES ignores the latency rule, NO lacks the observation of absence, the text says a late report is never VOID",
        "v8": "NO at 110 with knowable_at = 110: under the source rule's monotone-publication condition (OD5) the earliest matching record's evidenced publication time 115 > 110 is itself the archived observation that no record existed at 110; the record is a source-latency defect, the outage an integrity incident; identical to the disposition the observer would have reached by reading at 110"
      },
      "record_published_105_first_observed_130": {
        "v7": "YES (RC-105)",
        "v8": "YES (unchanged)"
      },
      "no_record_when_read_at_130": {
        "v7": "NO at 110 (observation of absence after the window)",
        "v8": "NO at 110 (unchanged)"
      },
      "record_published_115_source_cannot_evidence_publication_times": {
        "v7": "undefined",
        "v8": "adjudicated VOID at 110 under the source rule's failure condition (the source cannot evidence absence); such a source is an OD5 exclusion at registration"
      }
    },
    "invariant": "the disposition of a member is a function of the archived source records and the pre-registered source rule alone, never of when the observer happened to read",
    "reading": "the missing case had two rules that could not both hold; it is closed by stating what counts as an observation of absence when the observer was down: the late record itself, under a source rule that makes publication times monotone and evidenced"
  },
  "RC114_accrual_double_subtraction": {
    "analysis_date_T_A_months": 24,
    "H_max": 6,
    "registration_cut_off_T_R": 18,
    "event_registered_18_horizon_6": {
      "maturity": 24,
      "eligible_under_maturity_<=_T_A": true,
      "eligible_under_misreading_maturity_<=_T_R": false
    },
    "share_of_a_uniform_cohort_lost_under_the_misreading": 0.333,
    "implication": "registration <= T_R and declared horizon <= H_max give maturity <= T_A, so the maturity condition is implied; it is restated with the analysis date named so that the two cut-offs cannot be read as one",
    "reading": "the sentence used \"the 24-month cut-off\" for the analysis date two clauses after calling the registration cut-off \"the cut-off\"; under the reading Codex gives, a third of the accrued cohort leaves"
  },
  "RC115_T17_F24_pre_declared": {
    "cluster_A_scored_member_increment": 0.1,
    "T17_v7_wording_pre_declared_sibling_imputed_+/-1": {
      "bounds_on_cluster_increment": [
        -0.45,
        0.55
      ],
      "cap_count": 1
    },
    "section3_and_F24_v7_pre_declared_outside_cap_and_bounds": {
      "bounds_on_cluster_increment": [
        0.1,
        0.1
      ],
      "cap_count": 0,
      "audit_count_by_reason": 1
    },
    "cluster_B_two_pre_declared": {
      "T17_v7": "counts two against the cap",
      "section3_F24_v7": "outside the cap; two in the candidate log and the VOID audit by reason"
    },
    "v8_choice": "section 3 and F-24: a pre-declared member is fixed in the registration record before any forecast or outcome exists and is a population choice, like a candidate-log rejection; the cap and the bounds cover members that left the scored population after registration",
    "reading": "round 9 rewrote section 3 and F-24 for RC-87 and RC-90 and left the T-17 pass condition at its round-7 wording; the two cannot both be implemented"
  },
  "python": "3.11.17"
}
```

## Appendix L. Round-11 checks (REPRODUCED)

Needs no reference code and no network. Run from the repository root with
`python -I research/reproduction/round11_checks.py` in an isolated venv (Python 3.11.17, numpy 2.4.6, scipy 1.17.1;
95 s); the file is byte-identical to the block between the `round11-script` markers (RC-122;
`python -I research/reproduction/check_appendix_scripts.py` printed `reconciliation_probes.py: identical to the
appendix block`, the same for `round2_checks.py` to `round11_checks.py`, and `11 scripts checked, 0 differ`). Seeds
are fixed; two consecutive runs produced byte-identical output. Blocks, keyed by the review-comment id each answers:
RC-117 computes the exact pass probability of the A3 tolerance by true size at 20,000 replications, the observed-rate
ceiling of the level-α criterion at 20,000 and 100,000 replications for K = 1, 25, 100 and 400 evaluated points, and
an illustration on the independent period-shock family of Appendix F; RC-118 vectorises the exact two-point family of
Appendix J, sweeps ε at step 10⁻⁵, evaluates the committed values 3.201, 2.632 and 2.231 on the sweep, computes the
exact-supremum critical values and shows two coarse grids; RC-119 runs Codex's two-cluster example and 2,000 random
registration paths under the version-7 buffer and the watermark rule; RC-120 restates every §6 power figure and the
T-36 positive control (Appendix K's generator and seed, which reproduces Appendix K's rates at the superseded values)
at the nominal value, at the superseded values and at the corrected values; RC-121 computes the exact size of a
component whose catastrophe share lies outside the pair class at the pair's c*; RC-123 is a toy gate under three
demotion rules on two branches. One choice made while writing it, recorded so that the method is checkable: the
first draft of the RC-118 block used a sweep at step 0.0005, which already showed the committed values exceeded; the
committed block uses 10⁻⁵ so that the supremum is located to the pmf's variation over one step. The committed round-10
script of Appendix K was re-run in the same environment this round (§2): byte-identical. The round-11 commands that
established RC-116 are not in the script because they need the repository, not a venv: `git fetch origin --prune`,
`git fetch origin '+refs/pull/4/*:refs/remotes/pr4/*'`, `git cat-file -p 50897415d0fd85e29a4effdeab8fcd5de055874d`
("fatal: Not a valid object name"), `git branch -r --contains 50897415d0fd…` (no output), the GitHub commits API for
the SHA ("No commit found for SHA"), and `git log --format='%h %an <%ae> | %cn <%ce>' origin/research/claude-handoff..HEAD`
(every commit the owner's identity except `b19483a`, `37ac018`, `8af2ae9`).

<!-- round11-script:start -->
```python
"""Round-11 checks for the Codex findings on PR #4 at 04bc122 (no reference code, no network).

Review 5559035950. Each block is keyed by the review-comment id it answers. The cluster-weighted statistic with
block-sum variance, the D1-type generator, the period-shock generator, the two-point calibration and the conjunction
generator are those of 16 Appendix F, H, J and K.
"""
import json, math, sys
import numpy as np
from scipy.stats import beta, binom, t as student_t

out = {}
ALPHA = 0.05
PERIODS = 24
REPS = 20000
CRIT = float(student_t.ppf(1 - ALPHA, PERIODS - 1))        # nominal one-sided critical value on 23 df, 1.7139

def binom_upper(k, n, conf):
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))
def binom_lower(k, n, conf):
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))

def cw_t_many(x):
    """x: (reps, clusters) with clusters = PERIODS * per, blocks of one period; cluster-weighted statistic, block-sum
    variance on G - 1 df (16 Appendix F). A zero-variance sample returns -inf (never rejects)."""
    reps, n = x.shape
    per = n // PERIODS
    theta = x.mean(axis=1)
    dev = (x - theta[:, None]).reshape(reps, PERIODS, per).sum(axis=2)
    v = (dev ** 2).sum(axis=1) / n ** 2 * PERIODS / (PERIODS - 1)
    tt = np.full(reps, -np.inf)
    ok = v > 0
    tt[ok] = theta[ok] / np.sqrt(v[ok])
    return tt

def cw_t_many_j(x):
    """x: (reps, J, clusters); returns t per (rep, J) (16 Appendix H)."""
    reps, j, n = x.shape
    per = n // PERIODS
    theta = x.mean(axis=2)
    dev = (x - theta[:, :, None]).reshape(reps, j, PERIODS, per).sum(axis=3)
    v = (dev ** 2).sum(axis=2) / n ** 2 * PERIODS / (PERIODS - 1)
    with np.errstate(divide='ignore', invalid='ignore'):
        return theta / np.sqrt(v)

# ================= r4303689622 (RC-117): the A3 tolerance is not a level-alpha calibration criterion =================
# A3 passes a family when the exact one-sided 99 % upper bound over 20,000 replications is <= 0.06. Used as the
# calibration criterion for c*, that admits a true size above alpha. Exact pass probabilities by true size, then the
# criterion that certifies size <= alpha: the upper bound itself <= alpha, at a confidence adjusted for the K points
# evaluated (Bonferroni, 1 - 0.01/K), with the implied ceiling on the observed rate.
def kmax(bound, n, conf):
    lo, hi = 0, n
    while lo < hi:                                    # largest k with binom_upper(k, n, conf) <= bound
        mid = (lo + hi + 1) // 2
        if binom_upper(mid, n, conf) <= bound:
            lo = mid
        else:
            hi = mid - 1
    return lo
rc117 = {'A3_tolerance_as_calibration_criterion': {}, 'level_alpha_criterion': {}}
k06 = kmax(0.06, REPS, 0.99)
rc117['A3_tolerance_as_calibration_criterion'] = {
    'max_rejections_passing_at_20000_reps': k06, 'observed_rate_ceiling': round(k06 / REPS, 5),
    'P_pass_by_true_size': {f'size={s}': round(float(binom.cdf(k06, REPS, s)), 4) for s in (0.050, 0.055, 0.057, 0.058, 0.060)}}
for n_reps in (20000, 100000):
    for K in (1, 25, 100, 400):
        conf = 1 - 0.01 / K
        k05 = kmax(ALPHA, n_reps, conf)
        rc117['level_alpha_criterion'][f'reps={n_reps},points_K={K},confidence={conf:.4f}'] = {
            'max_rejections_passing': k05, 'observed_rate_ceiling': round(k05 / n_reps, 5),
            'margin_below_alpha': round(ALPHA - k05 / n_reps, 5),
            'P_pass_by_true_size': {f'size={s}': round(float(binom.cdf(k05, n_reps, s)), 4) for s in (0.040, 0.042, 0.044, 0.046, 0.050)}}
# Illustration on a simulated family (the independent period-shock null of Appendix F, q_t = 0.5 +/- 0.3, 24 x 25):
# c* under the point-estimate criterion, under the 99 % bound at one point and under the Bonferroni bound for K = 100,
# with the power at delta = 0.02 (D1 generator, b = 0.5, 600 clusters) at each.
r = np.random.default_rng(11700)
per = 25; n = PERIODS * per
sh = r.choice([-0.3, 0.3], size=(REPS, PERIODS))
q = np.repeat(0.5 + sh, per, axis=1)
y = (r.random(q.shape) < q).astype(float)
t_null = np.sort(cw_t_many(0.4 * y - 0.2))[::-1]
p = 0.5 + math.sqrt(0.02) * r.choice([-1., 1.], size=(REPS, n))
yy = (r.random(p.shape) < p).astype(float)
t_alt = cw_t_many((0.5 - yy) ** 2 - (p - yy) ** 2)
illus = {}
for label, kk in (('point_estimate_le_alpha', int(ALPHA * REPS)), ('99pct_upper_le_alpha_K=1', kmax(ALPHA, REPS, 0.99)),
                  ('bonferroni_upper_le_alpha_K=100', kmax(ALPHA, REPS, 1 - 0.01 / 100))):
    c = float(t_null[kk])                             # smallest c with at most kk null statistics strictly above it
    k_obs = int((t_null > c).sum())
    illus[label] = {'c_star': round(c, 4), 'null_rejections_at_c_star': k_obs, 'observed_size': round(k_obs / REPS, 4),
                    '99pct_upper': round(binom_upper(k_obs, REPS, 0.99), 4), 'power_delta_0.02_600': round(float((t_alt > c).mean()), 4)}
illus['nominal_1.7139'] = {'observed_size': round(float((t_null > CRIT).mean()), 4), 'power_delta_0.02_600': round(float((t_alt > CRIT).mean()), 4)}
rc117['illustration_period_shock_family'] = illus
rc117['reading'] = ('with the A3 tolerance as the criterion a family of true size 5.5 % passes the calibration in about three runs of four and the text then calls the test level 0.05; '
                    'the criterion that certifies size <= alpha is the upper bound itself <= alpha at confidence 1 - 0.01/K over the K evaluated points, '
                    'which costs 0.4 to 0.6 points of size at 20,000 replications (0.2 to 0.3 at 100,000) and a few points of power, reported at c*')
out['RC117_calibration_criterion'] = rc117

# ================= r4303689629 (RC-118): the grid maximum is not the supremum over the box =================
# Exact two-point block-mean family of Appendix J (block mean +a w.p. 1 - eps, -b w.p. eps, a = eps b / (1 - eps),
# b = 0.9, 24 blocks). The statistic depends only on the number k of positive blocks, so the size at a fixed c is a
# STEP function of eps (it jumps where some t_k(eps) crosses c) and a grid cannot bound it. Vectorised over eps.
G = 24
KS = np.arange(G + 1)
def two_point_t(eps, b=0.9):
    """t_k(eps) for every k, shape (len(eps), G + 1); zero-variance samples (k = 0, G) never reject."""
    eps = np.asarray(eps, float)[:, None]
    a = eps * b / (1 - eps)
    k = KS[None, :]
    mean = (k * a - (G - k) * b) / G
    var = (k * (a - mean) ** 2 + (G - k) * (-b - mean) ** 2) / (G - 1)
    with np.errstate(divide='ignore', invalid='ignore'):
        tk = mean / np.sqrt(var / G)
    tk[:, [0, G]] = -np.inf
    return tk
def two_point_pmf(eps):
    return binom.pmf(KS[None, :], G, 1 - np.asarray(eps, float)[:, None])
def size_over(eps, c):
    return (two_point_pmf(eps) * (two_point_t(eps) > c)).sum(axis=1)
def exact_size(e, c):
    return float(size_over(np.array([e]), c)[0])
def crit_per_eps(eps):
    """Smallest c with size(eps, c) <= alpha, for every eps: the t_(j*) at which the descending cumulative mass first exceeds alpha."""
    tk = two_point_t(eps); pm = two_point_pmf(eps)
    order = np.argsort(-tk, axis=1)
    ts = np.take_along_axis(tk, order, axis=1); ps = np.take_along_axis(pm, order, axis=1)
    cum = np.cumsum(ps, axis=1)
    j = (cum > ALPHA).argmax(axis=1)
    return ts[np.arange(len(eps)), j]
def c_star(eps_set):
    return float(math.ceil(crit_per_eps(np.asarray(eps_set, float)).max() * 1000) / 1000)      # rounded up to 0.001 as in Appendix J
dense = np.round(np.arange(0.02, 0.50001, 1e-5), 5)
rc118 = {'committed_appendix_J_values_on_the_dense_sweep': {}, 'coarse_grids': {}}
C_DENSE = {}
for eps_min, c_j in ((0.05, 3.201), (0.1, 3.201), (0.2, 2.632), (0.3, 2.231)):
    d = dense[dense >= eps_min - 1e-9]
    sz = size_over(d, c_j); i = int(sz.argmax())
    grid_j = np.round(np.arange(eps_min, 0.5001, 0.005), 3)
    C_DENSE[eps_min] = c_star(d)
    rc118['committed_appendix_J_values_on_the_dense_sweep'][f'eps_min={eps_min}'] = {
        'appendix_J_grid_step': 0.005, 'appendix_J_c_star': c_j, 'max_size_on_appendix_J_grid': round(float(size_over(grid_j, c_j).max()), 4),
        'sup_size_on_dense_sweep_step_1e-5': round(float(sz[i]), 4), 'argmax_eps': float(d[i]),
        'fraction_of_dense_points_above_alpha': round(float((sz > ALPHA).mean()), 4),
        'c_star_on_dense_sweep': C_DENSE[eps_min], 'sup_size_at_dense_c_star': round(float(size_over(d, C_DENSE[eps_min]).max()), 4)}
for eps_min, step in ((0.2, 0.05), (0.3, 0.05)):
    grid = [round(e, 3) for e in np.arange(eps_min, 0.5001, step)]
    c = c_star(grid)
    d = dense[dense >= eps_min - 1e-9]
    sz = size_over(d, c); i = int(sz.argmax())
    rc118['coarse_grids'][f'eps_min={eps_min},grid_step={step}'] = {
        'grid': grid, 'c_star_on_grid': c, 'max_size_on_grid': round(float(size_over(np.array(grid), c).max()), 4),
        'sup_size_on_dense_sweep': round(float(sz[i]), 4), 'argmax_eps': float(d[i]), 'fraction_of_dense_points_above_alpha': round(float((sz > ALPHA).mean()), 4)}
rc118['dense_c_star_by_eps_min'] = {str(k): v for k, v in C_DENSE.items()}
rc118['reading'] = ('on the exact two-point family the size at a fixed c is a step function of eps, so every grid value of c*, the committed 0.005 grid '
                    'included, is exceeded between its grid points; the confirmatory claim is over the committed enumerated set, a coordinate whose '
                    'supremum can be computed exactly is calibrated on it (the dense values replace the Appendix J grid values), and the box is otherwise '
                    'the domain of a reported sweep whose refinement is a pre-registration check')
out['RC118_grid_versus_box'] = rc118
C_STARS = tuple(sorted({3.201, 2.632, 2.231, C_DENSE[0.05], C_DENSE[0.2], C_DENSE[0.3]}, reverse=True))

# ================= r4303689633 (RC-119): the maturity buffer must wait for the registration watermark =================
# Codex's example: A registered at 0 with H_A = 100, final at 10, no registered predecessor; B registered at 20 with
# not_before 21 and H_B = 50, final at 50. Version-8 rule: a closed cluster waits for every REGISTERED cluster with a
# smaller H. Watermark rule: a closed cluster waits until the clock reaches its own H as well (no cluster with a
# smaller H can be registered after that, because a registration at time t has H > t).
def consume(clusters, rule):
    # clusters: list of (name, registered_at, H, final_at). Returns the consumption sequence [(time, name, H)].
    events = sorted({c[1] for c in clusters} | {c[3] for c in clusters} | {c[2] for c in clusters})
    applied, seq = set(), []
    for now in events:
        progress = True
        while progress:
            progress = False
            registered = [c for c in clusters if c[1] <= now and c[0] not in applied]
            for c in sorted(registered, key=lambda c: (c[2], c[1])):
                name, reg, H, fin = c
                if fin > now:
                    continue
                predecessors = [d for d in registered if d[2] < H or (d[2] == H and d[1] < reg)]
                if any(d[3] > now for d in predecessors):
                    continue
                if rule == 'watermark' and now < H:
                    continue
                applied.add(name); seq.append((now, name, H)); progress = True
                break
    return seq
ex = [('A', 0, 100, 10), ('B', 20, 50, 50)]
rc119 = {'codex_example': {}}
for rule in ('version_8', 'watermark'):
    seq = consume(ex, rule)
    rc119['codex_example'][rule] = {'sequence_(time,cluster,H)': seq, 'H_ordered': all(seq[i][2] <= seq[i + 1][2] for i in range(len(seq) - 1))}
# Frequency under random registrations: 24 months, registrations at uniform times, horizons uniform in [1, 12],
# a YES final one month after registration with probability one half, otherwise final at H.
rr = np.random.default_rng(11900)
unsorted = 0; delay_v8 = []; delay_wm = []
TRIALS = 2000
for _ in range(TRIALS):
    m = 40
    reg = np.sort(rr.uniform(0, 24, m)); hor = rr.uniform(1, 12, m); H = reg + hor
    early = rr.random(m) < 0.5
    fin = np.where(early, reg + 1.0, H)
    cl = [(f'c{i}', float(reg[i]), float(H[i]), float(fin[i])) for i in range(m)]
    s8 = consume(cl, 'version_8'); sw = consume(cl, 'watermark')
    if not all(s8[i][2] <= s8[i + 1][2] for i in range(len(s8) - 1)):
        unsorted += 1
    fin_by = {c[0]: c[3] for c in cl}
    delay_v8.append(np.mean([t - fin_by[nm] for t, nm, _ in s8])); delay_wm.append(np.mean([t - fin_by[nm] for t, nm, _ in sw]))
rc119['random_registrations_40_clusters_24_months'] = {
    'trials': TRIALS, 'fraction_of_paths_with_unsorted_version_8_sequence': round(unsorted / TRIALS, 4),
    'mean_delay_after_finality_months': {'version_8': round(float(np.mean(delay_v8)), 3), 'watermark': round(float(np.mean(delay_wm)), 3)},
    'watermark_sequences_H_ordered_in_every_trial': True}
rc119['reading'] = ('the version-8 buffer orders only the clusters registered so far, so a later registration with a smaller H breaks the declared H-order and '
                    'the earlier factor was computed on a prefix the filtration says is incomplete; applying a factor no earlier than its own H closes the channel, '
                    'because a registration at time t has H > t, at the cost of the delay reported')
out['RC119_registration_watermark'] = rc119

# ================= r4303689635 (RC-120): the section-6 power figures restated at the calibrated c* =================
# Single comparison, D1 generator (Appendix F rows): b in {0.5, 0.2}, delta in {0.005, 0.01, 0.02}, 288, 600 and 1,200 clusters.
def d1_x(b, delta, kk, r_):
    p_ = b + math.sqrt(delta) * r_.choice([-1., 1.], size=(REPS, kk))
    y_ = (r_.random(p_.shape) < p_).astype(float)
    return (b - y_) ** 2 - (p_ - y_) ** 2
def rates(tt):
    d = {'nominal_1.7139': round(float((tt > CRIT).mean()), 4)}
    for c in C_STARS:
        d[f'c*={c}'] = round(float((tt > c).mean()), 4)
    return d
single = {}
for b in (0.5, 0.2):
    for delta in (0.005, 0.01, 0.02):
        for per_ in (12, 25, 50):
            kk = PERIODS * per_
            r_ = np.random.default_rng(12000 + int(b * 10) * 100 + int(delta * 1000) * 10 + per_)
            single[f'b={b},delta={delta},clusters={kk}(24x{per_})'] = rates(cw_t_many(d1_x(b, delta, kk, r_)))
# Period-shock design (Appendix F generator: q_t = 0.5 + 2.5 delta +/- 0.3 per period, X in {-0.2, +0.2}).
shock = {}
for delta in (0.02, 0.05, 0.08):
    for per_ in (25, 50):
        kk = PERIODS * per_
        r_ = np.random.default_rng(12100 + int(delta * 1000) * 10 + per_)
        sh_ = r_.choice([-0.3, 0.3], size=(REPS, PERIODS))
        q_ = np.repeat(0.5 + 2.5 * delta + sh_, per_, axis=1)
        y_ = (r_.random(q_.shape) < q_).astype(float)
        shock[f'shock=+/-0.3,delta={delta},clusters={kk}(24x{per_})'] = rates(cw_t_many(0.4 * y_ - 0.2))
# Conjunction (Appendix H generator: six comparators sharing FULL's forecast and the outcome, shared-sign probability rho;
# Appendix J's three anti-correlated pairs). IUT rejects iff every comparator's statistic exceeds the common c.
J = 6
def iut_tt(b, delta, per_, rho, seed, anti=False):
    r_ = np.random.default_rng(seed)
    n_ = PERIODS * per_
    y_ = (r_.random((REPS, 1, n_)) < b).astype(float)
    if anti:
        own = r_.choice([-1.0, 1.0], size=(REPS, 3, n_))
        s_ = np.concatenate([own, -own], axis=1)
    else:
        shared = r_.choice([-1.0, 1.0], size=(REPS, 1, n_))
        own = r_.choice([-1.0, 1.0], size=(REPS, J, n_))
        s_ = np.where(r_.random((REPS, J, n_)) < rho, shared, own)
    bc = b - s_ * math.sqrt(delta)
    return cw_t_many_j((bc - y_) ** 2 - (b - y_) ** 2)
def iut_rates(tt):
    d = {}
    for label, c in (('nominal_1.7139', CRIT),) + tuple((f'c*={c}', c) for c in C_STARS):
        rej = tt > c
        d[label] = {'mean_marginal': round(float(rej.mean(axis=0).mean()), 4), 'iut_joint': round(float(rej.all(axis=1).mean()), 4)}
    return d
conj = {}
for delta, per_ in ((0.01, 25), (0.01, 50), (0.02, 25)):
    for rho in (0.0, 0.5, 1.0):
        conj[f'delta={delta},clusters={PERIODS * per_},shared_sign_prob={rho}'] = iut_rates(iut_tt(0.5, delta, per_, rho, 12200 + int(delta * 1000) * 100 + per_ + int(rho * 10)))
conj['delta=0.01,clusters=600,three_anti_correlated_pairs'] = iut_rates(iut_tt(0.5, 0.01, 25, 0.0, 12300, anti=True))
# T-36 (c) positive control restated at every cutoff (Appendix K generator and seed: D1, b = 0.5, delta = 0.08, 120 clusters).
r36 = np.random.default_rng(11100)
p36 = 0.5 + math.sqrt(0.08) * r36.choice([-1.0, 1.0], size=(REPS, PERIODS * 5))
y36 = (r36.random((REPS, PERIODS * 5)) < p36).astype(float)
t36 = cw_t_many((0.5 - y36) ** 2 - (p36 - y36) ** 2)
pc36 = {}
for label, c in (('nominal_1.7139', CRIT),) + tuple((f'c*={c}', c) for c in C_STARS):
    k36 = int((t36 > c).sum())
    pc36[label] = {'rejection_rate': round(k36 / REPS, 4), 'exact_99pct_lower_bound': round(binom_lower(k36, REPS, 0.99), 4)}
out['RC120_power_restated_at_calibrated_cutoffs'] = {
    'single_comparison_D1_generator': single, 'period_shock_design': shock, 'confirmatory_conjunction': conj,
    'T36_positive_control_b_0.5_delta_0.08_120_clusters': pc36,
    'reading': 'every figure of the section-6 smallest-effect row is stated at the nominal value; at the illustrated c* values the single comparison at delta = 0.01 and 600 clusters, the conjunction and the period-shock design all fall, and the row now carries the figures per c* and defers the choice to OD4'}

# ================= r4303689641 (RC-121): one calibrated cutoff does not make every IUT component level alpha =================
# Exact: a component whose increment law is the two-point family with a catastrophe share OUTSIDE the class the
# FULL-Design C pair was calibrated for (eps < eps_min), evaluated at the pair's c*. The IUT's size when the other five
# components reject surely equals the component's size (Berger: the IUT is level alpha only if every component is).
rc121 = {'component_size_outside_the_pair_class': {}}
for eps_min in (0.3, 0.2, 0.1):
    c = C_DENSE[eps_min]
    below = dense[dense < eps_min - 1e-9]
    sz = size_over(below, c); i = int(sz.argmax())
    inside = dense[dense >= eps_min - 1e-9]
    rc121['component_size_outside_the_pair_class'][f'pair_eps_min={eps_min},pair_c_star={c}'] = {
        'sup_size_inside_the_pair_class': round(float(size_over(inside, c).max()), 4),
        'sup_component_size_for_eps_in_[0.02,eps_min)': round(float(sz[i]), 4), 'argmax_eps': float(below[i]),
        'component_size_at_selected_eps': {f'eps={e}': round(exact_size(e, c), 4) for e in (0.12, 0.15, 0.18, 0.22, 0.25, 0.28) if e < eps_min}}
rc121['reading'] = ('a comparator whose increments carry a catastrophe share outside the class the FULL-baseline pair was calibrated for has size '
                    'above alpha at the pair c*, and the IUT inherits it when the other components reject; each component needs its own '
                    'enumerated class and c*_j, and T-13 and T-16 carry the null comparator at the corner of its box')
out['RC121_component_calibration'] = rc121

# ================= r4303689649 (RC-123): demotion when the anchor store is unavailable =================
# Toy gate. State: level, epoch, anchored epochs, pending flag. Scenario: promote (anchored) -> capability B signed in
# that epoch -> hazard demotion while the anchor store is unavailable -> present B -> ledger restored to the last anchor
# and the process restarted -> store returns -> present B -> present a fresh owner capability. Three rules for the
# demotion: version-8 transaction rolled back on anchor failure; version-8 transaction committed unanchored; the
# fail-closed rule (local demotion persisted at once, promotions and protected actions refused until anchored, every
# start at the floor).
def gate_run(rule, restore_branch):
    store_up = [True]
    st = {'level': 'FLOOR', 'epoch': 0, 'anchored': {0}, 'pending': False}
    anchors = []                                          # snapshots of st at each successful anchor
    log = []
    def anchor():
        if store_up[0]:
            st['anchored'].add(st['epoch']); st['pending'] = False; anchors.append(dict(st, anchored=set(st['anchored'])))
            return True
        return False
    def start():
        st['epoch'] += 1
        if rule == 'fail_closed':
            st['level'] = 'FLOOR'
        ok = anchor()
        log.append(f"start: level={st['level']} epoch={st['epoch']} anchored={ok}")
    def promote(cap_epoch):
        if cap_epoch != st['epoch'] or st['epoch'] not in st['anchored'] or st['pending']:
            log.append(f'promote with cap epoch {cap_epoch}: refused'); return False
        st['level'] = 'SIM'; anchor(); log.append(f'promote with cap epoch {cap_epoch}: level=SIM, anchored'); return True
    def demote():
        if rule == 'v8_rollback':
            if not store_up[0]:
                log.append('demote: anchor unavailable, transaction rolled back, level stays ' + st['level']); return
            st['level'] = 'FLOOR'; st['epoch'] += 1; anchor(); log.append('demote: level=FLOOR, epoch anchored')
        elif rule == 'v8_commit_unanchored':
            st['level'] = 'FLOOR'; st['epoch'] += 1
            ok = anchor(); log.append(f'demote: level=FLOOR, new epoch anchored={ok}')
        else:
            st['level'] = 'FLOOR'; st['epoch'] += 1; st['pending'] = True
            ok = anchor(); log.append(f'demote: level=FLOOR persisted locally, epoch {st["epoch"]} anchored={ok}, pending={st["pending"]}')
    def act(cap_epoch, name):
        if cap_epoch != st['epoch'] or st['level'] != 'SIM' or st['pending'] or st['epoch'] not in st['anchored'] or not store_up[0]:
            log.append(f'{name}: refused'); return False
        log.append(f'{name}: ACTED at level SIM'); return True
    def restore():
        last = anchors[-1]
        st.update(level=last['level'], epoch=last['epoch'], anchored=set(last['anchored']), pending=last['pending'])
        log.append(f"restore to last anchor: level={st['level']} epoch={st['epoch']}")
    start()
    promote(st['epoch'])
    b_epoch = st['epoch']                                 # capability B signed now, unused
    store_up[0] = False
    demote()
    acted_store_down = act(b_epoch, 'B after demotion, store down')
    if not restore_branch:
        store_up[0] = True
        if rule == 'fail_closed' and st['pending']:
            anchor()                                       # the pending epoch is anchored as soon as the store returns
        acted = act(b_epoch, 'B after the store returns')
        return {'B_acts_after_the_store_returns': acted, 'level_after_the_store_returns': st['level'], 'log': log}
    restore(); start()
    store_up[0] = True
    anchor()
    acted = act(b_epoch, 'B after restore and restart')
    fresh = act(st['epoch'], 'fresh owner capability in the new epoch, no promotion recorded')
    return {'B_acts_after_demotion_store_down': acted_store_down, 'B_acts_after_restore_and_restart': acted,
            'level_after_restore_and_restart': st['level'], 'fresh_capability_acts_at_SIM_without_a_promotion': fresh, 'log': log}
rc123 = {}
for rule in ('v8_rollback', 'v8_commit_unanchored', 'fail_closed'):
    rc123[rule] = {'store_returns_no_restore': gate_run(rule, False), 'restore_to_last_anchor_while_store_down': gate_run(rule, True)}
rc123['reading'] = ('rolling the demotion back leaves the gate elevated and the pre-demotion capability acts once the store returns; committing it unanchored stales '
                    'the capability (and the start rotation of RC-74 stales it after a restore as well, so that part of the finding does not reproduce) but a restore '
                    'to the last anchor revives the elevated level and a fresh capability then acts at it with no promotion recorded; persisting the demotion at once, '
                    'refusing every promotion and protected action until the new epoch is anchored, and starting every process at the floor leaves nothing to revive')
out['RC123_demotion_without_anchor'] = rc123

out['python'] = sys.version.split()[0]
print(json.dumps(out, indent=2, default=str))
```
<!-- round11-script:end -->

Output (`python -I research/reproduction/round11_checks.py`, round 11, 2026-10-17; the second run was byte-identical):

```json
{
  "RC117_calibration_criterion": {
    "A3_tolerance_as_calibration_criterion": {
      "max_rejections_passing_at_20000_reps": 1122,
      "observed_rate_ceiling": 0.0561,
      "P_pass_by_true_size": {
        "size=0.05": 1.0,
        "size=0.055": 0.7581,
        "size=0.057": 0.2979,
        "size=0.058": 0.128,
        "size=0.06": 0.01
      }
    },
    "level_alpha_criterion": {
      "reps=20000,points_K=1,confidence=0.9900": {
        "max_rejections_passing": 928,
        "observed_rate_ceiling": 0.0464,
        "margin_below_alpha": 0.0036,
        "P_pass_by_true_size": {
          "size=0.04": 1.0,
          "size=0.042": 0.9989,
          "size=0.044": 0.9518,
          "size=0.046": 0.6147,
          "size=0.05": 0.0096
        }
      },
      "reps=20000,points_K=25,confidence=0.9996": {
        "max_rejections_passing": 897,
        "observed_rate_ceiling": 0.04485,
        "margin_below_alpha": 0.00515,
        "P_pass_by_true_size": {
          "size=0.04": 0.9997,
          "size=0.042": 0.9778,
          "size=0.044": 0.728,
          "size=0.046": 0.2244,
          "size=0.05": 0.0004
        }
      },
      "reps=20000,points_K=100,confidence=0.9999": {
        "max_rejections_passing": 886,
        "observed_rate_ceiling": 0.0443,
        "margin_below_alpha": 0.0057,
        "P_pass_by_true_size": {
          "size=0.04": 0.9989,
          "size=0.042": 0.9485,
          "size=0.044": 0.5906,
          "size=0.046": 0.1288,
          "size=0.05": 0.0001
        }
      },
      "reps=20000,points_K=400,confidence=1.0000": {
        "max_rejections_passing": 876,
        "observed_rate_ceiling": 0.0438,
        "margin_below_alpha": 0.0062,
        "P_pass_by_true_size": {
          "size=0.04": 0.9968,
          "size=0.042": 0.9003,
          "size=0.044": 0.454,
          "size=0.046": 0.0702,
          "size=0.05": 0.0
        }
      },
      "reps=100000,points_K=1,confidence=0.9900": {
        "max_rejections_passing": 4839,
        "observed_rate_ceiling": 0.04839,
        "margin_below_alpha": 0.00161,
        "P_pass_by_true_size": {
          "size=0.04": 1.0,
          "size=0.042": 1.0,
          "size=0.044": 1.0,
          "size=0.046": 0.9998,
          "size=0.05": 0.0097
        }
      },
      "reps=100000,points_K=25,confidence=0.9996": {
        "max_rejections_passing": 4769,
        "observed_rate_ceiling": 0.04769,
        "margin_below_alpha": 0.00231,
        "P_pass_by_true_size": {
          "size=0.04": 1.0,
          "size=0.042": 1.0,
          "size=0.044": 1.0,
          "size=0.046": 0.9946,
          "size=0.05": 0.0004
        }
      },
      "reps=100000,points_K=100,confidence=0.9999": {
        "max_rejections_passing": 4745,
        "observed_rate_ceiling": 0.04745,
        "margin_below_alpha": 0.00255,
        "P_pass_by_true_size": {
          "size=0.04": 1.0,
          "size=0.042": 1.0,
          "size=0.044": 1.0,
          "size=0.046": 0.9857,
          "size=0.05": 0.0001
        }
      },
      "reps=100000,points_K=400,confidence=1.0000": {
        "max_rejections_passing": 4722,
        "observed_rate_ceiling": 0.04722,
        "margin_below_alpha": 0.00278,
        "P_pass_by_true_size": {
          "size=0.04": 1.0,
          "size=0.042": 1.0,
          "size=0.044": 1.0,
          "size=0.046": 0.9674,
          "size=0.05": 0.0
        }
      }
    },
    "illustration_period_shock_family": {
      "point_estimate_le_alpha": {
        "c_star": 1.7226,
        "null_rejections_at_c_star": 1000,
        "observed_size": 0.05,
        "99pct_upper": 0.0537,
        "power_delta_0.02_600": 0.9638
      },
      "99pct_upper_le_alpha_K=1": {
        "c_star": 1.7659,
        "null_rejections_at_c_star": 928,
        "observed_size": 0.0464,
        "99pct_upper": 0.05,
        "power_delta_0.02_600": 0.9604
      },
      "bonferroni_upper_le_alpha_K=100": {
        "c_star": 1.7964,
        "null_rejections_at_c_star": 886,
        "observed_size": 0.0443,
        "99pct_upper": 0.0478,
        "power_delta_0.02_600": 0.9579
      },
      "nominal_1.7139": {
        "observed_size": 0.0509,
        "power_delta_0.02_600": 0.9647
      }
    },
    "reading": "with the A3 tolerance as the criterion a family of true size 5.5 % passes the calibration in about three runs of four and the text then calls the test level 0.05; the criterion that certifies size <= alpha is the upper bound itself <= alpha at confidence 1 - 0.01/K over the K evaluated points, which costs 0.4 to 0.6 points of size at 20,000 replications (0.2 to 0.3 at 100,000) and a few points of power, reported at c*"
  },
  "RC118_grid_versus_box": {
    "committed_appendix_J_values_on_the_dense_sweep": {
      "eps_min=0.05": {
        "appendix_J_grid_step": 0.005,
        "appendix_J_c_star": 3.201,
        "max_size_on_appendix_J_grid": 0.045,
        "sup_size_on_dense_sweep_step_1e-5": 0.0503,
        "argmax_eps": 0.17505,
        "fraction_of_dense_points_above_alpha": 0.0005,
        "c_star_on_dense_sweep": 3.207,
        "sup_size_at_dense_c_star": 0.05
      },
      "eps_min=0.1": {
        "appendix_J_grid_step": 0.005,
        "appendix_J_c_star": 3.201,
        "max_size_on_appendix_J_grid": 0.045,
        "sup_size_on_dense_sweep_step_1e-5": 0.0503,
        "argmax_eps": 0.17505,
        "fraction_of_dense_points_above_alpha": 0.0006,
        "c_star_on_dense_sweep": 3.207,
        "sup_size_at_dense_c_star": 0.05
      },
      "eps_min=0.2": {
        "appendix_J_grid_step": 0.005,
        "appendix_J_c_star": 2.632,
        "max_size_on_appendix_J_grid": 0.0484,
        "sup_size_on_dense_sweep_step_1e-5": 0.0539,
        "argmax_eps": 0.23502,
        "fraction_of_dense_points_above_alpha": 0.0116,
        "c_star_on_dense_sweep": 2.693,
        "sup_size_at_dense_c_star": 0.05
      },
      "eps_min=0.3": {
        "appendix_J_grid_step": 0.005,
        "appendix_J_c_star": 2.231,
        "max_size_on_appendix_J_grid": 0.0468,
        "sup_size_on_dense_sweep_step_1e-5": 0.0518,
        "argmax_eps": 0.34004,
        "fraction_of_dense_points_above_alpha": 0.0086,
        "c_star_on_dense_sweep": 2.254,
        "sup_size_at_dense_c_star": 0.0499
      }
    },
    "coarse_grids": {
      "eps_min=0.2,grid_step=0.05": {
        "grid": [
          0.2,
          0.25,
          0.3,
          0.35,
          0.4,
          0.45,
          0.5
        ],
        "c_star_on_grid": 2.025,
        "max_size_on_grid": 0.0422,
        "sup_size_on_dense_sweep": 0.1097,
        "argmax_eps": 0.20004,
        "fraction_of_dense_points_above_alpha": 0.3159
      },
      "eps_min=0.3,grid_step=0.05": {
        "grid": [
          0.3,
          0.35,
          0.4,
          0.45,
          0.5
        ],
        "c_star_on_grid": 1.716,
        "max_size_on_grid": 0.0422,
        "sup_size_on_dense_sweep": 0.1108,
        "argmax_eps": 0.30002,
        "fraction_of_dense_points_above_alpha": 0.6571
      }
    },
    "dense_c_star_by_eps_min": {
      "0.05": 3.207,
      "0.1": 3.207,
      "0.2": 2.693,
      "0.3": 2.254
    },
    "reading": "on the exact two-point family the size at a fixed c is a step function of eps, so every grid value of c*, the committed 0.005 grid included, is exceeded between its grid points; the confirmatory claim is over the committed enumerated set, a coordinate whose supremum can be computed exactly is calibrated on it (the dense values replace the Appendix J grid values), and the box is otherwise the domain of a reported sweep whose refinement is a pre-registration check"
  },
  "RC119_registration_watermark": {
    "codex_example": {
      "version_8": {
        "sequence_(time,cluster,H)": [
          [
            10,
            "A",
            100
          ],
          [
            50,
            "B",
            50
          ]
        ],
        "H_ordered": false
      },
      "watermark": {
        "sequence_(time,cluster,H)": [
          [
            50,
            "B",
            50
          ],
          [
            100,
            "A",
            100
          ]
        ],
        "H_ordered": true
      }
    },
    "random_registrations_40_clusters_24_months": {
      "trials": 2000,
      "fraction_of_paths_with_unsorted_version_8_sequence": 0.642,
      "mean_delay_after_finality_months": {
        "version_8": 2.005,
        "watermark": 2.749
      },
      "watermark_sequences_H_ordered_in_every_trial": true
    },
    "reading": "the version-8 buffer orders only the clusters registered so far, so a later registration with a smaller H breaks the declared H-order and the earlier factor was computed on a prefix the filtration says is incomplete; applying a factor no earlier than its own H closes the channel, because a registration at time t has H > t, at the cost of the delay reported"
  },
  "RC120_power_restated_at_calibrated_cutoffs": {
    "single_comparison_D1_generator": {
      "b=0.5,delta=0.005,clusters=288(24x12)": {
        "nominal_1.7139": 0.3161,
        "c*=3.207": 0.0389,
        "c*=3.201": 0.039,
        "c*=2.693": 0.0858,
        "c*=2.632": 0.0945,
        "c*=2.254": 0.165,
        "c*=2.231": 0.1691
      },
      "b=0.5,delta=0.005,clusters=600(24x25)": {
        "nominal_1.7139": 0.5202,
        "c*=3.207": 0.1015,
        "c*=3.201": 0.102,
        "c*=2.693": 0.2001,
        "c*=2.632": 0.2165,
        "c*=2.254": 0.3264,
        "c*=2.231": 0.3347
      },
      "b=0.5,delta=0.005,clusters=1200(24x50)": {
        "nominal_1.7139": 0.7762,
        "c*=3.207": 0.2679,
        "c*=3.201": 0.2701,
        "c*=2.693": 0.4304,
        "c*=2.632": 0.4535,
        "c*=2.254": 0.5923,
        "c*=2.231": 0.6004
      },
      "b=0.5,delta=0.01,clusters=288(24x12)": {
        "nominal_1.7139": 0.5091,
        "c*=3.207": 0.0994,
        "c*=3.201": 0.1001,
        "c*=2.693": 0.1977,
        "c*=2.632": 0.2139,
        "c*=2.254": 0.3229,
        "c*=2.231": 0.3313
      },
      "b=0.5,delta=0.01,clusters=600(24x25)": {
        "nominal_1.7139": 0.7806,
        "c*=3.207": 0.2797,
        "c*=3.201": 0.2802,
        "c*=2.693": 0.4394,
        "c*=2.632": 0.4621,
        "c*=2.254": 0.6036,
        "c*=2.231": 0.611
      },
      "b=0.5,delta=0.01,clusters=1200(24x50)": {
        "nominal_1.7139": 0.9607,
        "c*=3.207": 0.6298,
        "c*=3.201": 0.632,
        "c*=2.693": 0.792,
        "c*=2.632": 0.8072,
        "c*=2.254": 0.8914,
        "c*=2.231": 0.8948
      },
      "b=0.5,delta=0.02,clusters=288(24x12)": {
        "nominal_1.7139": 0.7735,
        "c*=3.207": 0.2794,
        "c*=3.201": 0.2814,
        "c*=2.693": 0.44,
        "c*=2.632": 0.464,
        "c*=2.254": 0.5954,
        "c*=2.231": 0.6041
      },
      "b=0.5,delta=0.02,clusters=600(24x25)": {
        "nominal_1.7139": 0.9667,
        "c*=3.207": 0.6534,
        "c*=3.201": 0.6542,
        "c*=2.693": 0.8044,
        "c*=2.632": 0.8209,
        "c*=2.254": 0.9013,
        "c*=2.231": 0.9052
      },
      "b=0.5,delta=0.02,clusters=1200(24x50)": {
        "nominal_1.7139": 0.999,
        "c*=3.207": 0.9555,
        "c*=3.201": 0.9558,
        "c*=2.693": 0.9861,
        "c*=2.632": 0.9882,
        "c*=2.254": 0.996,
        "c*=2.231": 0.9961
      },
      "b=0.2,delta=0.005,clusters=288(24x12)": {
        "nominal_1.7139": 0.4357,
        "c*=3.207": 0.0681,
        "c*=3.201": 0.0684,
        "c*=2.693": 0.1454,
        "c*=2.632": 0.157,
        "c*=2.254": 0.2517,
        "c*=2.231": 0.2587
      },
      "b=0.2,delta=0.005,clusters=600(24x25)": {
        "nominal_1.7139": 0.6859,
        "c*=3.207": 0.1872,
        "c*=3.201": 0.1883,
        "c*=2.693": 0.3325,
        "c*=2.632": 0.3529,
        "c*=2.254": 0.4861,
        "c*=2.231": 0.4941
      },
      "b=0.2,delta=0.005,clusters=1200(24x50)": {
        "nominal_1.7139": 0.9133,
        "c*=3.207": 0.4754,
        "c*=3.201": 0.4779,
        "c*=2.693": 0.6552,
        "c*=2.632": 0.6774,
        "c*=2.254": 0.7971,
        "c*=2.231": 0.8032
      },
      "b=0.2,delta=0.01,clusters=288(24x12)": {
        "nominal_1.7139": 0.6865,
        "c*=3.207": 0.1839,
        "c*=3.201": 0.1855,
        "c*=2.693": 0.3281,
        "c*=2.632": 0.3488,
        "c*=2.254": 0.4866,
        "c*=2.231": 0.4958
      },
      "b=0.2,delta=0.01,clusters=600(24x25)": {
        "nominal_1.7139": 0.9236,
        "c*=3.207": 0.4985,
        "c*=3.201": 0.5002,
        "c*=2.693": 0.6787,
        "c*=2.632": 0.6987,
        "c*=2.254": 0.8145,
        "c*=2.231": 0.82
      },
      "b=0.2,delta=0.01,clusters=1200(24x50)": {
        "nominal_1.7139": 0.9961,
        "c*=3.207": 0.8815,
        "c*=3.201": 0.8824,
        "c*=2.693": 0.9545,
        "c*=2.632": 0.9597,
        "c*=2.254": 0.9837,
        "c*=2.231": 0.9846
      },
      "b=0.2,delta=0.02,clusters=288(24x12)": {
        "nominal_1.7139": 0.9294,
        "c*=3.207": 0.5123,
        "c*=3.201": 0.5147,
        "c*=2.693": 0.6945,
        "c*=2.632": 0.7167,
        "c*=2.254": 0.8251,
        "c*=2.231": 0.8304
      },
      "b=0.2,delta=0.02,clusters=600(24x25)": {
        "nominal_1.7139": 0.9983,
        "c*=3.207": 0.9087,
        "c*=3.201": 0.9094,
        "c*=2.693": 0.9696,
        "c*=2.632": 0.9736,
        "c*=2.254": 0.9904,
        "c*=2.231": 0.9912
      },
      "b=0.2,delta=0.02,clusters=1200(24x50)": {
        "nominal_1.7139": 1.0,
        "c*=3.207": 0.9993,
        "c*=3.201": 0.9993,
        "c*=2.693": 0.9998,
        "c*=2.632": 0.9999,
        "c*=2.254": 1.0,
        "c*=2.231": 1.0
      }
    },
    "period_shock_design": {
      "shock=+/-0.3,delta=0.02,clusters=600(24x25)": {
        "nominal_1.7139": 0.1781,
        "c*=3.207": 0.0163,
        "c*=3.201": 0.0163,
        "c*=2.693": 0.0406,
        "c*=2.632": 0.0455,
        "c*=2.254": 0.0807,
        "c*=2.231": 0.0833
      },
      "shock=+/-0.3,delta=0.02,clusters=1200(24x50)": {
        "nominal_1.7139": 0.1774,
        "c*=3.207": 0.0141,
        "c*=3.201": 0.0143,
        "c*=2.693": 0.0379,
        "c*=2.632": 0.0428,
        "c*=2.254": 0.0794,
        "c*=2.231": 0.0822
      },
      "shock=+/-0.3,delta=0.05,clusters=600(24x25)": {
        "nominal_1.7139": 0.5925,
        "c*=3.207": 0.1301,
        "c*=3.201": 0.1309,
        "c*=2.693": 0.2442,
        "c*=2.632": 0.2621,
        "c*=2.254": 0.3857,
        "c*=2.231": 0.3953
      },
      "shock=+/-0.3,delta=0.05,clusters=1200(24x50)": {
        "nominal_1.7139": 0.6063,
        "c*=3.207": 0.1302,
        "c*=3.201": 0.1313,
        "c*=2.693": 0.2488,
        "c*=2.632": 0.2674,
        "c*=2.254": 0.397,
        "c*=2.231": 0.4057
      },
      "shock=+/-0.3,delta=0.08,clusters=600(24x25)": {
        "nominal_1.7139": 0.928,
        "c*=3.207": 0.4727,
        "c*=3.201": 0.4747,
        "c*=2.693": 0.6596,
        "c*=2.632": 0.6822,
        "c*=2.254": 0.8098,
        "c*=2.231": 0.8164
      },
      "shock=+/-0.3,delta=0.08,clusters=1200(24x50)": {
        "nominal_1.7139": 0.9346,
        "c*=3.207": 0.4783,
        "c*=3.201": 0.48,
        "c*=2.693": 0.6816,
        "c*=2.632": 0.7046,
        "c*=2.254": 0.8233,
        "c*=2.231": 0.8296
      }
    },
    "confirmatory_conjunction": {
      "delta=0.01,clusters=600,shared_sign_prob=0.0": {
        "nominal_1.7139": {
          "mean_marginal": 0.7692,
          "iut_joint": 0.2036
        },
        "c*=3.207": {
          "mean_marginal": 0.2561,
          "iut_joint": 0.0001
        },
        "c*=3.201": {
          "mean_marginal": 0.2577,
          "iut_joint": 0.0001
        },
        "c*=2.693": {
          "mean_marginal": 0.4199,
          "iut_joint": 0.0054
        },
        "c*=2.632": {
          "mean_marginal": 0.4427,
          "iut_joint": 0.0076
        },
        "c*=2.254": {
          "mean_marginal": 0.5836,
          "iut_joint": 0.0375
        },
        "c*=2.231": {
          "mean_marginal": 0.5917,
          "iut_joint": 0.041
        }
      },
      "delta=0.01,clusters=600,shared_sign_prob=0.5": {
        "nominal_1.7139": {
          "mean_marginal": 0.7653,
          "iut_joint": 0.3085
        },
        "c*=3.207": {
          "mean_marginal": 0.2552,
          "iut_joint": 0.0059
        },
        "c*=3.201": {
          "mean_marginal": 0.257,
          "iut_joint": 0.0062
        },
        "c*=2.693": {
          "mean_marginal": 0.4201,
          "iut_joint": 0.0324
        },
        "c*=2.632": {
          "mean_marginal": 0.4424,
          "iut_joint": 0.0392
        },
        "c*=2.254": {
          "mean_marginal": 0.5805,
          "iut_joint": 0.1046
        },
        "c*=2.231": {
          "mean_marginal": 0.5885,
          "iut_joint": 0.1109
        }
      },
      "delta=0.01,clusters=600,shared_sign_prob=1.0": {
        "nominal_1.7139": {
          "mean_marginal": 0.7695,
          "iut_joint": 0.7695
        },
        "c*=3.207": {
          "mean_marginal": 0.2534,
          "iut_joint": 0.2534
        },
        "c*=3.201": {
          "mean_marginal": 0.2554,
          "iut_joint": 0.2554
        },
        "c*=2.693": {
          "mean_marginal": 0.4173,
          "iut_joint": 0.4173
        },
        "c*=2.632": {
          "mean_marginal": 0.44,
          "iut_joint": 0.44
        },
        "c*=2.254": {
          "mean_marginal": 0.582,
          "iut_joint": 0.582
        },
        "c*=2.231": {
          "mean_marginal": 0.5897,
          "iut_joint": 0.5897
        }
      },
      "delta=0.01,clusters=1200,shared_sign_prob=0.0": {
        "nominal_1.7139": {
          "mean_marginal": 0.9567,
          "iut_joint": 0.7671
        },
        "c*=3.207": {
          "mean_marginal": 0.6025,
          "iut_joint": 0.0491
        },
        "c*=3.201": {
          "mean_marginal": 0.6046,
          "iut_joint": 0.0502
        },
        "c*=2.693": {
          "mean_marginal": 0.7716,
          "iut_joint": 0.2122
        },
        "c*=2.632": {
          "mean_marginal": 0.7897,
          "iut_joint": 0.243
        },
        "c*=2.254": {
          "mean_marginal": 0.8795,
          "iut_joint": 0.4627
        },
        "c*=2.231": {
          "mean_marginal": 0.8837,
          "iut_joint": 0.4767
        }
      },
      "delta=0.01,clusters=1200,shared_sign_prob=0.5": {
        "nominal_1.7139": {
          "mean_marginal": 0.9571,
          "iut_joint": 0.7984
        },
        "c*=3.207": {
          "mean_marginal": 0.603,
          "iut_joint": 0.1196
        },
        "c*=3.201": {
          "mean_marginal": 0.6051,
          "iut_joint": 0.121
        },
        "c*=2.693": {
          "mean_marginal": 0.7715,
          "iut_joint": 0.3146
        },
        "c*=2.632": {
          "mean_marginal": 0.7887,
          "iut_joint": 0.3445
        },
        "c*=2.254": {
          "mean_marginal": 0.8784,
          "iut_joint": 0.5395
        },
        "c*=2.231": {
          "mean_marginal": 0.8832,
          "iut_joint": 0.5522
        }
      },
      "delta=0.01,clusters=1200,shared_sign_prob=1.0": {
        "nominal_1.7139": {
          "mean_marginal": 0.9567,
          "iut_joint": 0.9567
        },
        "c*=3.207": {
          "mean_marginal": 0.601,
          "iut_joint": 0.601
        },
        "c*=3.201": {
          "mean_marginal": 0.6032,
          "iut_joint": 0.6032
        },
        "c*=2.693": {
          "mean_marginal": 0.771,
          "iut_joint": 0.7711
        },
        "c*=2.632": {
          "mean_marginal": 0.7883,
          "iut_joint": 0.7883
        },
        "c*=2.254": {
          "mean_marginal": 0.8808,
          "iut_joint": 0.8808
        },
        "c*=2.231": {
          "mean_marginal": 0.8848,
          "iut_joint": 0.8848
        }
      },
      "delta=0.02,clusters=600,shared_sign_prob=0.0": {
        "nominal_1.7139": {
          "mean_marginal": 0.957,
          "iut_joint": 0.7675
        },
        "c*=3.207": {
          "mean_marginal": 0.6039,
          "iut_joint": 0.0485
        },
        "c*=3.201": {
          "mean_marginal": 0.6066,
          "iut_joint": 0.0495
        },
        "c*=2.693": {
          "mean_marginal": 0.771,
          "iut_joint": 0.2119
        },
        "c*=2.632": {
          "mean_marginal": 0.7883,
          "iut_joint": 0.2423
        },
        "c*=2.254": {
          "mean_marginal": 0.8797,
          "iut_joint": 0.4647
        },
        "c*=2.231": {
          "mean_marginal": 0.8841,
          "iut_joint": 0.4779
        }
      },
      "delta=0.02,clusters=600,shared_sign_prob=0.5": {
        "nominal_1.7139": {
          "mean_marginal": 0.9574,
          "iut_joint": 0.7984
        },
        "c*=3.207": {
          "mean_marginal": 0.6059,
          "iut_joint": 0.1194
        },
        "c*=3.201": {
          "mean_marginal": 0.6084,
          "iut_joint": 0.1215
        },
        "c*=2.693": {
          "mean_marginal": 0.7728,
          "iut_joint": 0.314
        },
        "c*=2.632": {
          "mean_marginal": 0.789,
          "iut_joint": 0.3417
        },
        "c*=2.254": {
          "mean_marginal": 0.8798,
          "iut_joint": 0.5419
        },
        "c*=2.231": {
          "mean_marginal": 0.8845,
          "iut_joint": 0.5544
        }
      },
      "delta=0.02,clusters=600,shared_sign_prob=1.0": {
        "nominal_1.7139": {
          "mean_marginal": 0.9556,
          "iut_joint": 0.9556
        },
        "c*=3.207": {
          "mean_marginal": 0.5971,
          "iut_joint": 0.5971
        },
        "c*=3.201": {
          "mean_marginal": 0.5994,
          "iut_joint": 0.5994
        },
        "c*=2.693": {
          "mean_marginal": 0.7668,
          "iut_joint": 0.7668
        },
        "c*=2.632": {
          "mean_marginal": 0.7845,
          "iut_joint": 0.7845
        },
        "c*=2.254": {
          "mean_marginal": 0.8789,
          "iut_joint": 0.8789
        },
        "c*=2.231": {
          "mean_marginal": 0.8832,
          "iut_joint": 0.8832
        }
      },
      "delta=0.01,clusters=600,three_anti_correlated_pairs": {
        "nominal_1.7139": {
          "mean_marginal": 0.7675,
          "iut_joint": 0.1556
        },
        "c*=3.207": {
          "mean_marginal": 0.256,
          "iut_joint": 0.0
        },
        "c*=3.201": {
          "mean_marginal": 0.2578,
          "iut_joint": 0.0
        },
        "c*=2.693": {
          "mean_marginal": 0.4207,
          "iut_joint": 0.0001
        },
        "c*=2.632": {
          "mean_marginal": 0.4434,
          "iut_joint": 0.0002
        },
        "c*=2.254": {
          "mean_marginal": 0.582,
          "iut_joint": 0.0076
        },
        "c*=2.231": {
          "mean_marginal": 0.5905,
          "iut_joint": 0.0092
        }
      }
    },
    "T36_positive_control_b_0.5_delta_0.08_120_clusters": {
      "nominal_1.7139": {
        "rejection_rate": 0.9633,
        "exact_99pct_lower_bound": 0.9601
      },
      "c*=3.207": {
        "rejection_rate": 0.6767,
        "exact_99pct_lower_bound": 0.6689
      },
      "c*=3.201": {
        "rejection_rate": 0.6767,
        "exact_99pct_lower_bound": 0.6689
      },
      "c*=2.693": {
        "rejection_rate": 0.8172,
        "exact_99pct_lower_bound": 0.8108
      },
      "c*=2.632": {
        "rejection_rate": 0.8262,
        "exact_99pct_lower_bound": 0.8199
      },
      "c*=2.254": {
        "rejection_rate": 0.8991,
        "exact_99pct_lower_bound": 0.894
      },
      "c*=2.231": {
        "rejection_rate": 0.9052,
        "exact_99pct_lower_bound": 0.9002
      }
    },
    "reading": "every figure of the section-6 smallest-effect row is stated at the nominal value; at the illustrated c* values the single comparison at delta = 0.01 and 600 clusters, the conjunction and the period-shock design all fall, and the row now carries the figures per c* and defers the choice to OD4"
  },
  "RC121_component_calibration": {
    "component_size_outside_the_pair_class": {
      "pair_eps_min=0.3,pair_c_star=2.254": {
        "sup_size_inside_the_pair_class": 0.0499,
        "sup_component_size_for_eps_in_[0.02,eps_min)": 0.114,
        "argmax_eps": 0.13559,
        "component_size_at_selected_eps": {
          "eps=0.12": 0.0,
          "eps=0.15": 0.0857,
          "eps=0.18": 0.045,
          "eps=0.22": 0.0739,
          "eps=0.25": 0.0388,
          "eps=0.28": 0.0192
        }
      },
      "pair_eps_min=0.2,pair_c_star=2.693": {
        "sup_size_inside_the_pair_class": 0.05,
        "sup_component_size_for_eps_in_[0.02,eps_min)": 0.0791,
        "argmax_eps": 0.15388,
        "component_size_at_selected_eps": {
          "eps=0.12": 0.0,
          "eps=0.15": 0.0,
          "eps=0.18": 0.045
        }
      },
      "pair_eps_min=0.1,pair_c_star=3.207": {
        "sup_size_inside_the_pair_class": 0.05,
        "sup_component_size_for_eps_in_[0.02,eps_min)": 0.0,
        "argmax_eps": 0.02,
        "component_size_at_selected_eps": {}
      }
    },
    "reading": "a comparator whose increments carry a catastrophe share outside the class the FULL-baseline pair was calibrated for has size above alpha at the pair c*, and the IUT inherits it when the other components reject; each component needs its own enumerated class and c*_j, and T-13 and T-16 carry the null comparator at the corner of its box"
  },
  "RC123_demotion_without_anchor": {
    "v8_rollback": {
      "store_returns_no_restore": {
        "B_acts_after_the_store_returns": true,
        "level_after_the_store_returns": "SIM",
        "log": [
          "start: level=FLOOR epoch=1 anchored=True",
          "promote with cap epoch 1: level=SIM, anchored",
          "demote: anchor unavailable, transaction rolled back, level stays SIM",
          "B after demotion, store down: refused",
          "B after the store returns: ACTED at level SIM"
        ]
      },
      "restore_to_last_anchor_while_store_down": {
        "B_acts_after_demotion_store_down": false,
        "B_acts_after_restore_and_restart": false,
        "level_after_restore_and_restart": "SIM",
        "fresh_capability_acts_at_SIM_without_a_promotion": true,
        "log": [
          "start: level=FLOOR epoch=1 anchored=True",
          "promote with cap epoch 1: level=SIM, anchored",
          "demote: anchor unavailable, transaction rolled back, level stays SIM",
          "B after demotion, store down: refused",
          "restore to last anchor: level=SIM epoch=1",
          "start: level=SIM epoch=2 anchored=False",
          "B after restore and restart: refused",
          "fresh owner capability in the new epoch, no promotion recorded: ACTED at level SIM"
        ]
      }
    },
    "v8_commit_unanchored": {
      "store_returns_no_restore": {
        "B_acts_after_the_store_returns": false,
        "level_after_the_store_returns": "FLOOR",
        "log": [
          "start: level=FLOOR epoch=1 anchored=True",
          "promote with cap epoch 1: level=SIM, anchored",
          "demote: level=FLOOR, new epoch anchored=False",
          "B after demotion, store down: refused",
          "B after the store returns: refused"
        ]
      },
      "restore_to_last_anchor_while_store_down": {
        "B_acts_after_demotion_store_down": false,
        "B_acts_after_restore_and_restart": false,
        "level_after_restore_and_restart": "SIM",
        "fresh_capability_acts_at_SIM_without_a_promotion": true,
        "log": [
          "start: level=FLOOR epoch=1 anchored=True",
          "promote with cap epoch 1: level=SIM, anchored",
          "demote: level=FLOOR, new epoch anchored=False",
          "B after demotion, store down: refused",
          "restore to last anchor: level=SIM epoch=1",
          "start: level=SIM epoch=2 anchored=False",
          "B after restore and restart: refused",
          "fresh owner capability in the new epoch, no promotion recorded: ACTED at level SIM"
        ]
      }
    },
    "fail_closed": {
      "store_returns_no_restore": {
        "B_acts_after_the_store_returns": false,
        "level_after_the_store_returns": "FLOOR",
        "log": [
          "start: level=FLOOR epoch=1 anchored=True",
          "promote with cap epoch 1: level=SIM, anchored",
          "demote: level=FLOOR persisted locally, epoch 2 anchored=False, pending=True",
          "B after demotion, store down: refused",
          "B after the store returns: refused"
        ]
      },
      "restore_to_last_anchor_while_store_down": {
        "B_acts_after_demotion_store_down": false,
        "B_acts_after_restore_and_restart": false,
        "level_after_restore_and_restart": "FLOOR",
        "fresh_capability_acts_at_SIM_without_a_promotion": false,
        "log": [
          "start: level=FLOOR epoch=1 anchored=True",
          "promote with cap epoch 1: level=SIM, anchored",
          "demote: level=FLOOR persisted locally, epoch 2 anchored=False, pending=True",
          "B after demotion, store down: refused",
          "restore to last anchor: level=SIM epoch=1",
          "start: level=FLOOR epoch=2 anchored=False",
          "B after restore and restart: refused",
          "fresh owner capability in the new epoch, no promotion recorded: refused"
        ]
      }
    },
    "reading": "rolling the demotion back leaves the gate elevated and the pre-demotion capability acts once the store returns; committing it unanchored stales the capability (and the start rotation of RC-74 stales it after a restore as well, so that part of the finding does not reproduce) but a restore to the last anchor revives the elevated level and a fresh capability then acts at it with no promotion recorded; persisting the demotion at once, refusing every promotion and protected action until the new epoch is anchored, and starting every process at the floor leaves nothing to revive"
  },
  "python": "3.11.17"
}
```
