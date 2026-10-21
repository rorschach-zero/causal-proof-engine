# 20 Phase 3 readiness: SIM read-only, executor principal (PROPOSED)

Status: `PROPOSED`, 2026-10-21, written on `main` at `ac4c640`. Documentation only. **Phase 3 is not approved.**
Nothing here authorises broker code, a Saxo client, network code or credential handling, and no part of this
document was produced by contacting Saxo or any provider (`AGENTS.md` §3, §11; `CLAUDE.md`). Every
recommendation below is the **delegate's recommendation** for the owner to confirm or replace; none is a
decision.

Sources read for this document: `AGENTS.md`; `CLAUDE.md`; `research/README.md`; `08`; `09` (Q1 to Q9, N12);
`12` (Phase 3 and amendments 4, 5 and 13); `14`; `16` §3 rows RC-14, RC-15, RC-16, RC-20, RC-60, §6 (OD6, OD9b,
OD10); `17` §3 item 5, item 6, A0, §5 (T-07, T-08, T-30 to T-35), §5.1 (F-09, F-12), §7; `19` §2, §5, §7, §9;
`cpe/capability/` at `ac4c640`; the archived `02/02`, `07/01` steps 4 and 5 and `ref/docs/Saxo.md`; issue #3
comments `6297828986`, `6297969313`, `6298303061`, `6300164338` and `6312263652`.

Every statement about Saxo below is either cited to the archived research, where it is `PACKAGE-VERIFIED`
(read by the package author on 2026-10-16, no bytes archived, `08` header, `14` §A) or reported by Codex
(`UNVERIFIED` here, `README.md` RC-36 rule), or is labelled `UNVERIFIED`. No web search was used.

## 1. Phase 3 scope, as the research defines it

The defining text is `12` Phase 3: "Separate OS principal and process; token from the OS credential store;
`/port` and `/ref` readbacks; reconciliation report; monthly universe snapshot and candidate log started (R20);
72-hour PKCE refresh test (Q1); Q3/Q6/Q7 answered empirically. Gate promoted RESEARCH_ONLY → SIM_READ_ONLY by
owner MAC recorded in the ledger. Exit: 7 consecutive days of readbacks; Q1 answered; independent review
including a token-leak audit. Phases 2 and 3 can run in parallel; they share nothing but the ledger."

| # | Item | Source | Notes |
|---|---|---|---|
| S1 | Executor is a separate OS principal and a separate process | `12` Phase 3; `08` §5 "Executor design"; `09` §3 D8 (four principals with separate accounts and secrets); `AGENTS.md` §3 ("Research agents never import or call the executor. Executor code never has model-provider access.") | `16` RC-20: OS accounts are "not a tested boundary (both agree)"; the boundary must be tested on the chosen host (§5 P3-07) |
| S2 | Token held in the OS credential store of the executor principal, never in the process environment or a file | `12` Phase 3; `08` §5 observation 4; `AGENTS.md` §3 secrets bullet; `07/01` step 5 item 1 (refresh token in the executor account's credential store) | `07/01` step 4 sets the one-day portal token as an environment variable of the executor session; `08` §5 observation 4 accepts that only for an interactive session, not for the executor service |
| S3 | `/port` readbacks (accounts, balances, positions, orders) and `/ref` readbacks (instruments and details) | `08` §3 SIM_READ_ONLY row (from `02/02` §3); `07/01` step 4 item 3; `ref/docs/Saxo.md` items 5 and 6 | exact read paths are `UNVERIFIED` (`08` §2, `14` B12); `08` §5 requires them confirmed against the reference docs and archived as bytes on the day they are read; `07/01` step 4 stores digests and the **hash** of the `AccountKey`, never the key |
| S4 | Reconciliation report (simulated balance, positions, open orders) with its ledger record type | `08` §3 evidence bundle; `08` §5 executor design; `07/01` step 4 acceptance ("reconciliation of the simulated 100,000 USD balance") | the SIM balance of USD 100,000 is `PACKAGE-VERIFIED` (`08` §1) |
| S5 | Monthly universe snapshot and candidate log | `12` Phase 3 (R20); `12` amendment 5; `09` Q5 | amendment 5 moves the **start** of universe and candidate logging to the first authorised research ingest of Phase 2; Phase 3 adds the `/ref` snapshot as the forward-reconstructed universe of Q5. Under OD11 (b) and comment `6298303061` Q is externally fixed and never subsampled; how a `/ref` universe snapshot relates to Q is not stated anywhere (owner question O-6, §3) |
| S6 | 72-hour unattended PKCE refresh test (Q1) | `12` Phase 3; `09` Q1 (blocking); `07/01` step 5; `02/02` §5; `14` A4, B1 | the documented lifetimes (`expires_in` 1200 s, `refresh_token_expires_in` 2400 s) are examples only; rotation and re-login policy are not described (`08` §1). Q1 concerns an individual **LIVE** application (`02/02` §2, `08` §2); the test runs in SIM, so it answers Q1 for SIM only, and the LIVE answer stays `UNVERIFIED` (P3-09, P-15) |
| S7 | Q3, Q6 and Q7 answered empirically | `12` Phase 3; `09` §1 | **conflict:** Q3 (does precheck accept `ManualOrder`) is answered empirically only by calling `POST /trade/v2/orders/precheck`, which is a SIM_PRECHECK call (`08` §3, §5 "Precheck phase"; `12` Phase 5), not a SIM_READ_ONLY call. Decision sheet D-5 (§3). Q6 is answered from account documents and `/ref`/`/port` readbacks (`09` Q6). Q7 needs a funded live account linked to SIM (`08` amendment 3, Codex's documentation-level read `UNVERIFIED` here); linking is an owner decision (D-6) |
| S8 | Promotion RESEARCH_ONLY → SIM_READ_ONLY by the owner's public-key capability | `12` amendment 13 (RC-107), which supersedes the "owner MAC" of the `12` Phase 3 row and of `07/01` step 4; `08` amendments 4 and 5; `17` §3 item 5 | the tuple is capability, environment, release digest, evidence digest, epoch, nonce, expiry; consumed-authorisation store; epoch rotated and anchored at process start and every demotion; acknowledgement only after the commit record is in an anchored prefix (`17` §3 item 5, four steps) |
| S9 | Exit: 7 consecutive days of readbacks; Q1 answered; independent review including a token-leak audit | `12` Phase 3; `08` §3 SIM_READ_ONLY evidence bundle ("7 days of successful readbacks, reconciliation report"); `07/01` step 4 acceptance (7 days logged, no 401/403) | `07/01` step 4 reads a 401 as the expected daily expiry of the one-day token; under the PKCE path of S6 a 401 is a finding |

**Out of scope of Phase 3** (`12` Phase 3, Phase 5, Phase 7; `08` §3; `AGENTS.md` §3):

- any order: placement, modification, cancellation, in SIM or LIVE; `POST /trade/v2/orders` (Phase 7);
- precheck, `POST /trade/v2/orders/precheck` (SIM_PRECHECK, Phase 5);
- **any write endpoint** of any service group, and any HTTP method other than the read method the
  reference docs name for the confirmed read paths;
- LIVE in any form: the LIVE gateway path, the LIVE auth host, a LIVE application, `SHADOW_LIVE_QUOTES`
  (`08` §3), `LIVE_EXECUTION` (blocked in code, `cpe/capability/levels.py`);
- streaming (`08` §1 lists streaming hosts; `08` §3 grants no streaming call to SIM_READ_ONLY);
- model-provider access from the executor, and any research-side import of the executor (`AGENTS.md` §3);
- any account data, token, app secret or `AccountKey` in Git, logs, prompts, fixtures or AI chats
  (`AGENTS.md` §3; `09` Q6 "no account data in AI chats").

## 2. Prerequisites checklist

Status: **done**, **open** (work by agents or reviewers), **owner action** (only the owner can do it).

| # | Prerequisite | Status | Source |
|---|---|---|---|
| P-1 | Phase 1 quality gate: whole-codebase audit at one commit by Codex and a fresh Claude session, with no reproducing P1; mutation-testing run over `cpe/` with every survivor killed or recorded; P1 reproduction rule | **open** (audit in progress in another session) | issue #3 comment `6312263652` item 3. Its text names "real data, providers or Phase 2"; a SIM readback is the first external data. Delegate's reading: the gate applies to Phase 3's first external contact (B-7), not to its offline steps; the owner may say otherwise |
| P-2 | Written approval of Phase 3, with its exact scope | **owner action** | `AGENTS.md` §1, §11; `CLAUDE.md` "Phase"; `12` preamble. Decision sheet D-1 |
| P-3 | OD10, at least for T-34 and the secret-handling code of `17` §3 item 5, which includes the production owner-key verifier and its key handling | **owner action** (deferred by comment `6297828986`) | `17` A0; `19` §2, §5, §7; `cpe/capability/signing.py` docstring (the production verifier "and every piece of key handling around it, is deferred with the secret-handling code of item 5 (`17` A0, OD10)"). Decision sheet D-2 |
| P-4 | Hosting and runtime of the executor principal (N12, filed under OD6 by `16` RC-20) | **owner action** | `09` N12 and §6 N12 row; `12` amendment 4 (N12 at the Phase 2 gate); `16` RC-20, §6 OD6. Phase 3 may run in parallel with Phase 2 (`12` Phase 3), so N12 must be answered before Phase 3 starts either way. Decision sheet D-3 |
| P-5 | OD6, production holder of the `AnchorStore` | **owner action**; **needed** | `19` §5 ("OD6: the production holder of the `AnchorStore` (Phase 1 uses the harness-owned double, RC-34)"). Needed because a promotion acknowledges only after its commit record is in an externally anchored prefix (`17` §3 item 5), and the harness double is not an external anchor. Note: `16` §6 names OD6 "Hosting at the Phase 2 gate" while `19` §5 files the anchor holder under OD6; the two are one owner decision in the delegate's reading; D-3 covers the hosting and this row the anchor holder, so that either can be confirmed alone |
| P-6 | Owner's signing key pair and the executor's copy of the public key | **owner action** after P-3 | The sources require verification with the owner's public key (`08` amendment 4; `17` §3 item 5) and a key that is never caller-supplied (F-09). They give no provisioning protocol. `REVISION` (the delegate's proposal, for review): the key pair is generated on an owner device, and the owner places the public key on the executor host |
| P-7 | Saxo SIM application created by the owner | **owner action** | `12` Phase 2 owner actions; `08` §5 "Account and policy"; `07/01` step 4. Guide in §4 |
| P-8 | Written question to Saxo OpenAPI support on unattended refresh-token lifetime and rotation for an individual app (Q1), and on whether automated order entry (`ManualOrder:false`) is permitted on the owner's account type | **owner action** | `08` §5 "Account and policy", observation 2; `09` Q1 |
| P-9 | Whether a daily owner login is acceptable if Q1 is negative | **owner action** | `07/02` §E question 2; `08` §5; `09` §3. Decision sheet D-4 |
| P-10 | Capability model as built must express SIM read-only as an environment-scoped capability that grants no LIVE action | **open** (engineering, offline) | `08` amendment 4 and `16` RC-14 ("explicit capabilities × environment" instead of a linear enum). **Reproduced on `ac4c640`** (`python3 -I`, Python 3.13.16, from the repository root): `permits("SIM_READ_ONLY", "shadow_quotes")` returns `True`, because `cpe/capability/levels.py` ranks the levels linearly (`RESEARCH_ONLY < SHADOW_LIVE_QUOTES < SIM_READ_ONLY < SIM_EXECUTION`) and `shadow_quotes` is a LIVE read-only action (`08` §3). T-33 tests only the converse direction. No test fails today because no Phase 1 code performs either action; it must be fixed before a SIM_READ_ONLY promotion means anything (build plan step B-1) |
| P-11 | Read paths of `/port` and `/ref`, and the read method for each, confirmed against the reference docs and archived as bytes on the day they are read | **open**, at implementation | `08` §2, §5; `14` B12 |
| P-12 | `AGENTS.md` §3 secrets wording made hosting-neutral, if a host without an "OS credential store" is chosen | **owner action**, conditional | `16` §6 OD9b, proposed §3 wording ("in the secret store of the principal that needs them, never in the process environment of untrusted code"); not applied. Needed only if D-3 picks a host where the secret store is not the OS's. The `12` Phase 3 row and the D-1 scope sentence also name an OS principal and its OS credential store, so such a host additionally needs a dated amendment of `12` Phase 3 and a matching D-1 scope sentence |
| P-13 | Whether linking a funded live account to SIM (Q7) is wanted | **owner action** | `08` amendment 3; `ref/docs/Saxo.md` item 3 ("only if desired and authorized"). Decision sheet D-6 |
| P-14 | D1 to D13 confirmed or amended (D8 four principals is the executor's basis) | not recorded in the sources read | `09` §5 |
| P-15 | Phase 3 exit criteria reconciled with the read-only scope: a dated amendment of the `12` Phase 3 row that moves the empirical Q3 to Phase 5 (D-5), states the Q7 criterion if D-6 (b) is chosen, and states that the 72-hour SIM test answers Q1 for SIM only (S6) | **owner action** | `12` Phase 3 asks for Q3, Q6 and Q7 "answered empirically" and "Q1 answered"; until amended, Phase 3 cannot exit under D-5 (a) or D-6 (b) |

## 3. Decision sheets, ready to confirm

Each sheet gives the question, options with consequences, and the **delegate's recommendation**. None is
decided.

### D-1 Phase 3 approval

**Question.** Does the owner approve Phase 3, and in exactly which scope?

| Option | Consequence |
|---|---|
| (a) Approve the scope sentence below, effective when P-1, P-2 (this), P-3, P-4 and P-5 hold | build plan §7 can start with its offline PRs; first live call only after P-6 to P-8 |
| (b) Approve offline preparation only (build plan steps B-1 to B-5, fakes and recorded fixtures, no network code that can reach Saxo) | no external contact; Q1 stays open, and with it the "hands-off" premise (`02/02` §5) |
| (c) Defer | calendar time only; Phase 2 is unaffected (`12` Phase 3, "share nothing but the ledger") |

**Scope sentence to approve (option a):**

> Phase 3 is approved: a separate executor OS principal and process, on the host chosen under N12, holding the
> Saxo SIM token only in that principal's credential store, may make read-only calls to the SIM `/port` and
> `/ref` read paths confirmed and archived under `08` §5, write their archived responses, a reconciliation
> report and a monthly `/ref` universe snapshot to the ledger, and run the 72-hour PKCE refresh test (Q1); the
> gate moves from RESEARCH_ONLY to SIM_READ_ONLY only by a capability signed with my key under `17` §3 item 5;
> no order, no precheck, no write endpoint, no streaming, no LIVE environment and no model-provider access are
> authorised; exit is 7 consecutive days of readbacks, the SIM result of the 72-hour test recorded against Q1, and an
> independent review including a token-leak audit.

**Delegate's recommendation:** (b) now, (a) once P-1 holds. P-1 gates the first external contact (B-7), not the
offline steps. The offline steps carry most of the risk-reducing
work and touch nothing external.

### D-2 OD10: secret handling and T-34

**Question.** OD10 as filed in `16` §6 is "approve or revert the version-5 to version-49 diffs of `17`". It
gates T-34 and the secret-handling code of `17` §3 item 5 (`17` A0), and with them the production owner-key
verifier (`cpe/capability/signing.py`). Phase 3 cannot hold a token without it.

`17` A0 allows OD10 to be recorded as "approval of this version-5 diff, **or the owner's explicit choice of
other wording for T-34**". The RC-60 wording (`16` RC-60, proposed for T-34 and the RC-15 row, applied in `17`
v5 and since then part of the frozen OD10 record) is:

> "no object reachable from the escaping exception, by attribute, slot, container, closure or `args`, holds the
> raw secret; the probe traverses object state, not `repr`; the secret is held only in frames that have
> returned before any exception escapes, and the outcome passed upward is a typed value, never the exception
> object".

| Option | What the owner approves | Consequence |
|---|---|---|
| (a) Approve OD10 in full | versions 5 to 49 of `17` as the specification | also re-opens the statistics text that OD11 (b) replaced (`19` §2); far more than Phase 3 needs |
| (b) **Narrow OD10 for the secret path** | (i) the RC-60 wording above as the pass condition of T-34 and F-12; (ii) the secret-handling code of `17` §3 item 5 under it; (iii) the production `Verifier` with the owner's public key, behind the existing `Verifier` interface; (iv) every other part of versions 5 to 49 stays frozen as the research record, as comment `6297828986` set | unblocks exactly T-34, F-12 and the verifier; nothing else changes |
| (c) Other wording for T-34 | the owner's text, per `17` A0 | needs one review of that text first |
| (d) Keep deferred | nothing | Phase 3 cannot hold a token; only offline steps B-1 and B-4 of §7 proceed (B-5 depends on B-2, which needs OD10) |

**Delegate's recommendation:** (b), with the four parts stated as above. A confirming reply could read: "OD10,
narrow: T-34 and F-12 pass under the RC-60 wording; the secret-handling code of `17` §3 item 5 and the
owner-key verifier may be built under it; versions 5 to 49 otherwise stay frozen."

### D-3 N12: hosting and runtime of the executor principal

**Question.** Where does the executor principal run? The OS credential store needs a **persistent** machine,
and a 72-hour unattended refresh (S6) and 7 consecutive days of readbacks (S9) need a host that stays up. An
ephemeral cloud agent session is neither persistent nor separate from the agents, so it is excluded in every
option.

Research positions: `07/01` assumes a Windows host with separate OS accounts; `09` N12 proposes containerised
core services with Windows as the host; `16` RC-20 records that OS accounts are not a tested boundary and puts a
costed choice (minimal cloud, hybrid, local-only) at the Phase 2 gate, with identical acceptance tests (IAM
denial, egress denial, clean-account restore) for whichever is chosen; `16` §6 OD6 gives Codex's illustrative
envelope of about USD 1,000 a year and calls local-only the weakest boundary; `09` D10 plans USD 0 of
additional cost in year one.

| Option | Security consequence | Cost and operation |
|---|---|---|
| (a) Owner's own everyday machine, executor as a separate OS account | weakest: the owner's account, browser, and any locally run agent tools share the machine; an OS account is not a tested boundary (RC-20); a compromise of the owner's session is one privilege step from the token | USD 0; uptime depends on the machine being on for 72 h and 7 days |
| (b) Small dedicated VM in the owner's own cloud account, administered only by the owner, running only the executor | separate machine from every agent session; egress allow-list and IAM denial testable (RC-20); the token never exists where agents run; the cloud account itself becomes a credential to protect (`UNVERIFIED`: which OS credential store a headless VM offers, see P-12) | recurring cost, against D10; owner duty for patching |
| (c) Dedicated physical machine owned by the owner (for example a spare computer), running only the executor | same separation as (b) without a cloud account; physical security and uptime are the owner's | USD 0 if the machine exists; power and network uptime are the owner's |
| (d) Managed host (platform that runs the process for the owner) | the platform operator and its secret service are inside the trust boundary; "OS credential store" no longer applies (P-12) | recurring cost; least owner maintenance |

**Never:** a host where agent sessions run (cloud agent containers, CI runners, the machine an agent uses to
work on this repository). Those are where a compromised agent would look first (§6).

**Delegate's recommendation:** (c) if a spare machine exists, otherwise (b). Both keep the token off every
machine where an agent runs, both allow the RC-20 tests, and (c) keeps D10. (a) is not recommended.

### D-4 Q1 fallback: daily owner login

**Question.** If the 72-hour test fails (no unattended refresh), is one owner login per day an acceptable
permanent constraint? (`07/02` §E question 2; `02/02` §5; `08` §5 observation 1.)

| Option | Consequence |
|---|---|
| (a) Yes, daily login is acceptable | Phase 3 exits on a negative Q1 with the constraint recorded; later phases plan around it |
| (b) No | a negative Q1 ends the "hands-off" premise for Saxo (`02/02` §5); the programme decides on the broker before Phase 5 |

**Delegate's recommendation:** decide before the test runs, so that the result cannot steer the criterion
(`AGENTS.md` §8, pre-registration). The delegate leans to (a), as `08` §5 observation 1 does.

### D-5 Q3 inside a read-only phase

**Question.** `12` asks Phase 3 to answer Q3 empirically, but Q3 is answered only by a precheck call, which
`08` §3 places in SIM_PRECHECK.

| Option | Consequence |
|---|---|
| (a) Move the empirical answer of Q3 to Phase 5 (SIM_PRECHECK); Phase 3 records only the documentation-level state of `08` §1 | read-only stays read-only; the `12` Phase 3 row needs an amendment |
| (b) Allow one precheck call in Phase 3 | widens the write surface of Phase 3 by a `POST`; contradicts `08` §3 |

**Delegate's recommendation:** (a).

### D-6 Q7: link a funded live account to SIM?

**Question.** Codex reports that linking a funded live account enables delayed data in SIM (`08` amendment 3,
`UNVERIFIED` here). Testing that needs the owner to link the account (`ref/docs/Saxo.md` item 3).

| Option | Consequence |
|---|---|
| (a) Link, and test Q7 empirically in Phase 3 | delayed quotes for available live instruments, per Codex's read of the help article (`08` amendment 3, `UNVERIFIED` here); what else the link exposes to the SIM application or its API is not stated in any source read (`UNVERIFIED`) |
| (b) Do not link; Q7 stays at documentation level | quote age in SIM stays unmeasured until Phase 5 (`08` §5 observation 3) |

**Delegate's recommendation:** (b) for Phase 3; revisit at Phase 5, where quote age matters.

### Further owner questions (no recommendation needed now)

- O-6: how the monthly `/ref` universe snapshot (S5) relates to the externally fixed question set Q of OD11 (b).
- O-7: whether the `AccountKey` hash of `07/01` step 4 is keyed (a plain hash of a low-entropy identifier can be
  inverted by enumeration; `UNVERIFIED` how much entropy an `AccountKey` has).

## 4. Owner setup guide for the Saxo SIM application

**Never paste a credential, app key, app secret, token, authorisation code, refresh token or `AccountKey` into a
chat, a pull request, an issue, a commit, a log or any file in this repository** (`AGENTS.md` §3). The system
reads secrets only from the executor principal's credential store. If one is pasted anywhere by mistake, treat it
as compromised and stop. Which recovery the portal offers for each kind of credential (revoking a token,
regenerating an app secret, replacing an application): `UNVERIFIED — check in the Saxo developer portal`, per
credential, before the first login (gap G-9).

Steps marked `UNVERIFIED — check in the Saxo developer portal` are not established by the archived research.
No URL or value below is invented; every URL is quoted from the archive.

1. **Register at the Saxo developer portal (SIM).** `07/01` step 4 item 1: register at
   `https://www.developer.saxo` (SIM). Account type, identity checks and terms at registration:
   `UNVERIFIED — check in the Saxo developer portal`.
2. **Create a SIM application.** `07/01` step 4 item 1 and `ref/docs/Saxo.md` item 1 (which links
   `https://www.developer.saxo/openapi/learn/environments`). SIM and LIVE applications do not share app key and
   secret (`08` §1, `PACKAGE-VERIFIED`). Create a SIM application only; do not request LIVE credentials.
3. **Choose the application type for the PKCE flow.** `07/01` step 5 item 1 ("PKCE application") and
   `ref/docs/Saxo.md` item 4 (`https://www.developer.saxo/openapi/learn/oauth-authorization-code-grant-pkce`):
   Authorization Code with PKCE, `code_challenge_method=S256` mandatory, verifier 43 to 128 characters (`08` §1,
   `PACKAGE-VERIFIED`). The name of the type or grant option in the portal, and whether a PKCE application also
   issues an app secret: `UNVERIFIED — check in the Saxo developer portal`.
4. **Set the redirect URI.** `07/01` step 5 item 1 gives the form `http://localhost:<port>/callback`. The port is
   not fixed by the research; it is chosen at implementation. Whether the registered URI must match the one the
   flow sends exactly, and whether the portal accepts a loopback `http` redirect, wildcard ports or several
   redirects: `UNVERIFIED — check in the Saxo developer portal`.
5. **Scopes and permissions.** `07/01` step 4 reads a 403 on an endpoint as "missing scope of the SIM app". Which
   permissions a SIM application has by default and whether read-only can be requested explicitly:
   `UNVERIFIED — check in the Saxo developer portal`. Prefer the narrowest setting the portal offers.
6. **Environment endpoints** (`08` §1, `PACKAGE-VERIFIED`, re-read on setup day per `14` A1): SIM gateway base
   `https://gateway.saxobank.com/sim/openapi`; SIM auth host `sim.logonvalidation.net`. The full `/authorize`
   and `/token` URLs on that host: `UNVERIFIED — check in the Saxo developer portal`.
7. **One-day portal token** (optional, for a first manual check only). SIM-only (`08` §1). `07/01` step 4
   sets it in the executor session's environment; for the executor service this is not acceptable (`08` §5
   observation 4). Use it, if at all, only in an interactive session of the executor account, never on an agent
   host.
8. **Do not link a live account** unless D-6 says so.
9. **Record on setup day, outside the repository:** the date, the application's name, and dated screenshots or
   saved copies of the environments and PKCE pages (`14` A1, A4; `09` Q2 practice). Archiving page bytes into the
   ingest log happens later, by the executor, per `08` §5.
10. **Send the Saxo support question** of P-8 in writing and keep the reply.

**Identifiers the system needs later.** The owner enters only the configuration rows (app key, app secret if one
exists, redirect URI, environment), and only on the executor host. Tokens are produced by the flow and the
`AccountKey` is read by the executor; the owner never handles either by hand.

| Identifier | Source | Secret? |
|---|---|---|
| App key of the SIM application | `08` §1 ("app key and secret"); that the app key is the OAuth client identifier of the PKCE flow is `UNVERIFIED — check in the Saxo developer portal` | treat as confidential; `UNVERIFIED` whether Saxo treats it as public |
| App secret, if the portal issues one for this type | `08` §1 | secret |
| Redirect URI, as registered | `07/01` step 5 | not secret |
| Environment: SIM gateway base and SIM auth host | `08` §1 | not secret |
| Refresh token and access token | produced by the flow, never typed by the owner | secret; credential store only (`07/01` step 5) |
| `AccountKey` | read by the executor from `/port`, never entered | stored only as a hash (`07/01` step 4; O-7) |

**Gaps for the owner to check in the portal** (no web search was used to fill them): G-1 application type name
for PKCE; G-2 whether that type has an app secret; G-3 loopback redirect and port rules; G-4 default and
selectable scopes; G-5 the exact `/authorize` and `/token` URLs; G-6 the real access and refresh lifetimes and
the rotation policy (Q1, measured by the 72-hour test); G-7 the exact `/port` and `/ref` read paths (`14` B12);
G-8 whether a SIM application must be renewed or expires; G-9 the recovery available for each kind of credential
if one is exposed; G-10 whether the registered redirect URI must match exactly.

## 5. Phase 3 acceptance tests

"Offline" means buildable now against fakes, recorded or synthetic fixtures and a fake transport, with no code
that can reach Saxo; "live SIM" means it needs the owner's setup (§4) and the chosen host (D-3). Test IDs are
new (P3-nn) and map to existing ones.

| ID | Test | Pass condition | Maps to | Offline / live |
|---|---|---|---|---|
| P3-01 | **Read-only enforcement at the capability boundary.** Every request the executor can form is checked against an allow-list of (method, path) built from the confirmed read paths before any transport object exists; presented: every non-read method on an allowed path, `/trade/v2/orders`, `/trade/v2/orders/precheck`, any other service group, a path-traversal or encoded variant of an allowed path, a streaming host | every one refused with a typed reason, at the boundary; nothing reaches the transport. `REVISION` (a release-bound defence, not in `08` §3): the Phase 3 release refuses them whatever level the gate holds, because SIM_PRECHECK and SIM_EXECUTION add precheck and orders only in their own later releases (`12` Phase 5, Phase 7); the refusal is a ledger check record | `08` §3; `08` amendment 2 (path- and credential-based policy, RC-16); `17` T-32 pattern (no object is authority); F-11 principle (not constructible before transport) | offline (fake transport) |
| P3-02 | **Environment separation.** LIVE gateway path, LIVE auth host, a capability with environment LIVE, a SIM capability presented to a gate configured for another environment | refused; `wrong_environment` for the capability case | `08` §1, amendment 2; `17` T-31 (environment field), T-33 | offline |
| P3-03 | **Capability levels are per environment.** SIM_READ_ONLY granted alone | permits `sim_read` only; denies `shadow_quotes` and `sim_execution` (fails on `ac4c640`, P-10) | `16` RC-14; `08` amendment 4; T-33 | offline |
| P3-04 | **Promotion with the production verifier.** T-30, T-31 and T-35 re-run with the owner-key verifier in place of `HarnessVerifier`, with a test key pair; the key is loaded by the executor, never supplied by the caller | all pass as in Phase 1; F-09 rejected | `17` §3 item 5, T-30, T-31, T-35, F-09 | offline (test key); one live promotion signed by the owner |
| P3-05 | **T-34 under OD10, HTTP source of F-12.** Synthetic bearer canary in an error raised by the fake transport, in nested exceptions, structured errors and encoded (base64, URL) forms | canary absent from logs, error payloads and the whole reachable exception graph, probed by object state, under the RC-60 wording (D-2) | `17` T-34, F-12, §3 item 6; `16` RC-15, RC-47, RC-55, RC-60 | offline; gated on OD10 |
| P3-06 | **Credential store, not environment.** Token read only through the credential-store interface of the executor principal; the process environment and child processes carry no token; a researcher-principal process attempting the read is denied | interface tests pass against a fake store; on the host, the researcher's read fails with a permission error | `08` §5 observation 4; `AGENTS.md` §3; `07/01` step 5 | offline (fake store); live on host |
| P3-07 | **Process and principal separation on the host.** Researcher principal cannot read the executor's store or files; researcher egress to the Saxo hosts denied; executor has no model-provider access; clean-account restore; the researcher principal and every agent host cannot write to the production `AnchorStore` of OD6 (credential and IAM denial) | the three RC-20 tests (IAM denial, egress denial, clean-account restore) pass on the chosen host, and the anchor-store write is denied to every principal but its holder (`09` §2: "CI fails if the anchor path is writable by the researcher"); static check that no research module imports the executor (`17` §3 item 8, a lint, not the pass condition) | `16` RC-20; `08` §5; `AGENTS.md` §3; `17` T-08 | live on host (no Saxo call needed) |
| P3-08 | **Token lifecycle state machine.** Fake `/authorize` and `/token` with injected clock: S256 challenge, verifier length 43 to 128, refresh before expiry, refresh-token expiry, rotation, a failed refresh | refresh failure demotes or halts with a typed outcome; no token in any record; lifetimes read from the response, never assumed | `08` §1 (PKCE facts, `PACKAGE-VERIFIED`); `17` T-35 clock rules | offline |
| P3-09 | **72-hour unattended refresh (Q1, SIM-scoped).** Real SIM application, no browser step after the first login | 72 h of continuously valid sessions; measured `expires_in` and `refresh_token_expires_in` and rotation behaviour recorded as the **SIM** result; a failure records the SIM result negative and applies D-4. Q1 as defined in `02/02` §2 and `08` §2 concerns an individual **LIVE** application; no source establishes that SIM and LIVE share lifetimes or rotation, so the LIVE answer stays `UNVERIFIED` until separate evidence (for example the written reply of P-8) | `12` Phase 3; `09` Q1; `07/01` step 5; `14` A4, B1 | live SIM |
| P3-10 | **Readback record.** Each readback recorded by its digest and receipt time, with the `AccountKey` only as its hash (`07/01` step 4 item 3); the reference-document pages of the read paths archived as bytes on the day read (`08` §5) | replay reproduces each readback record; no raw `AccountKey` and no unredacted account response body in the ledger or JSONL. Archiving redacted response bodies, if wanted for reconciliation replay, is a `REVISION` that needs its own review | `08` §5; `07/01` step 4 item 3 | offline (synthetic fixtures whose shape is `UNVERIFIED` until P-11); live SIM |
| P3-11 | **Reconciliation report.** Ledger record type over simulated balance, positions and open orders; fixtures with a match, a balance mismatch, a missing position, an unexpected open order | report states each difference; a mismatch is a finding recorded in the ledger, never silently corrected | `08` §3, §5 | offline; live SIM |
| P3-12 | **Demotion.** (i) Sourced: an explicit demotion and a clock discontinuity rotate the epoch and leave the gate at the floor (`17` §3 item 5, T-30, T-35); `08` §3 demotes to SIM_READ_ONLY on a missing mandatory pre-trade input, heartbeat loss or anchor failure, which in a read-only phase is already the level held. (ii) `REVISION` (a new Phase 3 policy, for review): anchor failure and heartbeat loss stop readbacks and demote to the floor; a 401 or 403 on an allowed path stops readbacks and is recorded as a finding without demotion | (i) as in Phase 1; (ii) as written once reviewed | `08` §3 rules; `17` §3 item 5, T-30, T-35 | offline |
| P3-13 | **Monthly `/ref` universe snapshot.** Snapshot archived and anchored on a fixed calendar | one snapshot per month, anchored; a missed month is reported | `12` Phase 3 (R20), amendment 5; `09` Q5 | offline (fixtures); live SIM |
| P3-14 | **Token-leak audit.** Independent reviewer scans ledger, JSONL, logs, crash dumps, CI artefacts, the Git tree and history, PR and issue text for the canary and for any real token or app-secret prefix; reviews every code path that touches the store | no hit; findings reproduced as failing tests (P1 rule, `6312263652` item 3) | `12` Phase 3 exit; `14` D6 | offline part (canary scan in CI); live part at exit |
| P3-15 | **Seven consecutive days of readbacks.** | 7 consecutive days with every scheduled readback archived and reconciled; no 401/403 under the PKCE path | `12` Phase 3; `08` §3; `07/01` step 4 | live SIM |
| P3-16 | **Q6 recorded.** Entitlements read from account documents and `/ref`/`/port` | recorded in `09` without account data in any AI chat | `09` Q6; `14` B4 | live SIM and owner |

## 6. Threat model summary for the first external connection

**Assets.** The SIM refresh and access tokens; the app key and any app secret; the `AccountKey`; the owner's
signing key; the ledger and its external anchors; gate state.

**Token lifecycle.** The owner completes the first PKCE login on the executor host; the executor stores the
refresh token in its principal's credential store; access tokens live only in memory of the executor process
and only in frames that return before any exception escapes (RC-60 wording); a refresh failure halts reads
and demotes; revocation is the owner's action, by whatever mechanism the portal offers (`UNVERIFIED`, G-9). Lifetimes and rotation are `UNVERIFIED` until P3-09.

**Process separation.** Researcher and executor are different OS principals and processes on the host of D-3;
they share only the ledger (`12` Phase 3). The executor has no model-provider access; research code never
imports or calls it (`AGENTS.md` §3). The executor's egress is limited to the Saxo hosts; because SIM and LIVE
share `gateway.saxobank.com`, SIM is enforced by path and credential at the adapter (`08` amendment 2), and
LIVE credentials do not exist in Phase 3.

**Logging and redaction.** Errors are typed outcomes; no request object, header or exception object is logged
or passed upward (`08` §5; RC-15, RC-60); `Bearer ` and canary scans in CI (`12` Phase 1 tests; `14` D6);
readback bodies are archived as bytes in the ledger, which therefore must not contain tokens (P3-10, P3-14).

**What a compromised agent session can reach.** The repository, its CI, and any machine where agents run:
code, fixtures, the ledger copy it is given, PR and issue text. It can propose a malicious change, which review
and CI must catch (`AGENTS.md` §9).

**What it cannot reach, if D-3, P-5 and P3-07 (including its anchor-store denial) hold.** The executor host, its
credential store, the token, the app secret, the owner's signing key and the external anchor store (OD6). It cannot promote the gate, because a
promotion needs the owner's signature over the whole tuple and an anchored commit (`17` §3 item 5), and it
cannot reach Saxo from where it runs (egress denial, P3-07). **This holds only if no token, key or secret is
ever pasted into an agent's context** (§4), and only if code that reaches the executor host is reviewed first.

**Residual risks.** A malicious change merged into executor code runs with the token; mitigations are the
read-only allow-list at the boundary (P3-01), independent review of every executor PR (`AGENTS.md` §9) and the
token-leak audit (P3-14). On host option (a) of D-3 the owner's own session is a further path. SIM account
data, though simulated, is account data and stays out of AI chats (`09` Q6).

## 7. Build plan, after approval

Small PRs against `main`, one component each, each with one Codex review and the round caps of comment
`6312263652` item 4. Steps B-1 to B-5 are offline and touch no network; none of them can reach Saxo.

| Step | PR | Needs | Offline? |
|---|---|---|---|
| B-1 | Capability levels per environment: SIM_READ_ONLY grants SIM reads only (P3-03); read-only action names | D-1 (b) or (a) | yes |
| B-2 | Secret confinement, T-34 and F-12 with a fake HTTP source (P3-05) | D-2 | yes |
| B-3 | Production owner-key `Verifier` behind the existing interface; dependency added, pinned and justified (`AGENTS.md` §6); P3-04 with a test key pair | D-2 | yes |
| B-4 | Executor package skeleton: request allow-list and environment policy before any transport object (P3-01, P3-02); demotion triggers (P3-12); fake transport only | D-1 | yes |
| B-5 | Token lifecycle against a fake auth server and a fake credential store (P3-06 offline, P3-08); readback archive, reconciliation report and universe snapshot record types over synthetic fixtures (P3-10, P3-11, P3-13 offline) | D-1, B-2 | yes |
| B-6 | Host provisioning runbook and the RC-20 tests on the chosen host (P3-07); no Saxo call | D-3, P-5 | host |
| B-7 | Read paths confirmed and archived (P-11); real transport added behind the B-4 boundary; the owner signs the SIM_READ_ONLY capability over a pre-read evidence bundle (release digest, the B-6 host tests, the archived read-path pages) and the gate is promoted (P3-04 live); then the first readback. The gate admits no read below SIM_READ_ONLY (`08` §3; `perform("sim_read")` at `ac4c640`), so the order of `07/01` step 4, which reads first and promotes on the readback report, cannot pass the boundary. The content of the pre-read bundle is a `REVISION` for review | D-1 (a), P-1, P-6, P-7 | live SIM |
| B-8 | 72-hour refresh test (P3-09); 7 days of readbacks (P3-15); Q6 (P3-16) | B-7, D-4 decided beforehand | live SIM |
| B-9 | Exit review and token-leak audit (P3-14); `09` updated with the SIM-scoped Q1 result, Q6, and Q7 if D-6 (a) | B-8, P-15 | review |

**Order in which owner actions unblock the rest:**

1. D-1 (b): B-1 and B-4 can start; they are local and use a fake transport, so the P-1 quality gate does not hold them.
2. D-2 (OD10): B-2, B-3, B-5.
3. D-3 (N12) and P-5 (OD6 anchor holder): B-6.
4. P-1 quality gate passed, P-7 SIM application (§4), P-6 signing key, P-8 support question, D-1 (a): B-7.
5. D-4 decided before the test: B-8.
6. P-15 (the `12` Phase 3 amendment): B-9, then the owner decides on Phase 5 (SIM_PRECHECK), where D-5 places Q3.
