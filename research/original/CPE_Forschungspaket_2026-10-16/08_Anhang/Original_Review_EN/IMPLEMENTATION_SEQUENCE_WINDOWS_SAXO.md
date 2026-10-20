# IMPLEMENTATION_SEQUENCE_WINDOWS_SAXO.md: step-by-step for the owner

Target machine: Windows 11, RTX 5090, large RAM. Every step has an acceptance test and a failure path. Commands are given only where I verified the tool exists in the package; Saxo-side UI steps are described from the official learn pages read 2026-10-16 and may differ in wording. **Nothing below places an order. LIVE is blocked in code.**

Safety rules for all steps: never paste tokens, app secrets, account keys, holdings or passwords into any AI chat; keep the repo in a folder without secrets; use three Windows user accounts as in spec §2 (`cpe-research`, `cpe-promoter`, `cpe-executor`) before step 7.

---

## Step 0 (today, 30 minutes): verify the review package locally

1. Unzip `CPE_Claude_Review_Output_2026-10-16.zip`; check `MANIFEST.sha256` (PowerShell: `Get-FileHash -Algorithm SHA256 <file>` and compare).
2. Hand `CLAUDE_REVIEW.md`, the spec, this file and `PATCH_PROPOSALS/` to the OpenAI cross-review as planned. Do not start building until both reviews agree on OPEN_QUESTIONS Q1 and Q2.

Acceptance: hashes match. Failure path: if any hash differs, discard the package and request a re-send.

## Step 1 (day 1): Python environment and tests

Prerequisite: Python 3.11 or newer installed from python.org (verified in this review on 3.13.16).

```powershell
cd <repo>\PATCH_PROPOSALS\source_v0_2
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[test]
python -m pytest -q
```

Acceptance: `31 passed`. Failure path: if `scipy`/`numpy` wheels fail on your Python version, use Python 3.12; if a test fails, stop and report the failing test name to both reviewers.

## Step 2 (day 1-2): Lean certificate toolchain (optional for M0, required before SIM_PRECHECK)

Pinned: Lean `leanprover/lean4:v4.35.0`, Mathlib rev `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2` (`proofs/lean-toolchain`, `proofs/lake-manifest.json`). Install elan from https://github.com/leanprover/elan (Windows installer), then in a new folder:

```powershell
lake +leanprover/lean4:v4.35.0 new cpe_proofs math
cd cpe_proofs
# replace lake-manifest.json with proofs/lake-manifest.json and lean-toolchain with proofs/lean-toolchain
lake exe cache get
copy ..\proofs\*.lean CpeProofs\
lake env lean CpeProofs\BetThreshold.lean
lake env lean CpeProofs\RiskBudget.lean
```

Acceptance: both commands exit 0; `RiskBudget.lean` prints four `depends on axioms: [propext, Classical.choice, Quot.sound]` lines. Cost: ~8 GB disk for the Mathlib cache (measured 7.8 GB here), 20-40 minutes download. Failure path: if `lake exe cache get` fails behind a proxy, run on a plain network; if Mathlib's `lean-toolchain` differs, use exactly the pinned manifest rather than `lake update`.

## Step 3 (day 2): ledger anchoring and owner secret

1. Generate the owner secret once (PowerShell): `[Convert]::ToBase64String((1..32 | % { Get-Random -Max 256 }) -as [byte[]])`; store it in Windows Credential Manager under the owner account only.
2. Create the anchor store on a location the research user cannot write (OneDrive/iCloud folder of the owner account, or a second machine).
3. Run a scripted daily task that calls `AppendOnlyLedger.anchor(secret)` and writes the JSON to the anchor store.

Acceptance: `verify_against_anchor` passes from a second machine using only the anchor file and a copy of the ledger. Failure path: if the anchor store is writable by the research user, the anchor is decorative; fix permissions first.

## Step 4 (day 3-5): Saxo SIM application and read-only readback (**first safe external action**)

1. Register at https://www.developer.saxo (SIM). Create a SIM application. Obtain a **one-day SIM token** from the Developer Portal; it is "only authorized for the simulation environment" (environments page).
2. Set `SAXO_SIM_ACCESS_TOKEN` in the executor user's session only (`$env:SAXO_SIM_ACCESS_TOKEN = '<token>'`), never in a file.
3. Write and run `scripts/sim_readback.py` (to be written in M1; not in this package because paths must first be confirmed in the reference docs for your account): calls for accounts, balances, positions, orders and one instrument details lookup; stores digests and the `AccountKey` **hash** (not the key) in the ledger.
4. Promote the gate `RESEARCH_ONLY → SIM_READ_ONLY` with an owner HMAC over the readback report hash.

Acceptance: 7 consecutive days of readbacks logged; no 401/403; reconciliation of the simulated $100,000 balance. Failure path: 401 means the one-day token expired (expected daily); 403 on an endpoint means the SIM app lacks that scope, record it in OPEN_QUESTIONS Q1 and ask Saxo support; any other error, stop.

## Step 5 (week 2-3): OAuth PKCE application and unattended refresh test

1. Create a PKCE application (redirect URI `http://localhost:<port>/callback`), implement `/authorize` → `/token` with `code_challenge_method=S256`, store the refresh token in Credential Manager (executor user).
2. Measure the real `expires_in` and `refresh_token_expires_in` and whether refresh succeeds repeatedly for 72 hours unattended.

Acceptance: 72 hours of continuous valid sessions without a browser login. Failure path: if sessions cannot be kept alive unattended, "hands-off" is impossible on the broker side; the design falls back to owner-triggered sessions (e.g., one login per day) and this is recorded as a permanent constraint (Q1).

## Step 6 (week 3-6): registry, ingest log and Jev triage in production (research user)

1. Request Jev early access (waitlist, vendor blog 2026-09-15); on receipt, store `TYPESAFE_API_KEY` in Credential Manager (research user).
2. Run `GET /v1/models` and record the model names and `release_date` in the ledger.
3. Start the ingest log with 3 to 5 source families that have publication-lag entries; run `JevClient.ask_noul_pair` on each document; register the first 20 EventSpecs by hand with the three LLMs *not yet* in the loop.

Acceptance: 100 documents triaged, complement-gap histogram produced, 20 events committed with Design-C baseline forecasts. Failure path: if Jev access is delayed, use the `−Jev` ablation arm (rules + local classifier) and keep the Jev slot mandatory in the schema so nothing downstream silently adapts.

## Step 7 (week 6-10): three-model adapters within subscription terms

1. Claude: claim the Max monthly API credit (7-day eligibility), link one Console organization, use the Agent SDK or Messages API with that key (support article 17154008). Budget alert at 80 percent of the credit.
2. OpenAI: use an API key for scheduled runs (documented route for programmatic workflows); keep Codex CLI with ChatGPT sign-in for interactive adversarial sessions only. Decide Plus vs Pro after measuring volume.
3. Gemini: Gemini CLI with Google AI Pro for interactive runs; for scheduled runs verify current headless policy (Q2) and otherwise use a Gemini API key.
4. Enforce per-provider daily token ceilings in the adapter; log cost per forecast.

Acceptance: 3 independent round-1 outputs per event, schema-validated, no cross-reading (separate processes, no shared context); fusion produces FORECAST / ABSTAIN / RE_RESEARCH; e-process versus Design-C running. Failure path: if any provider's terms are unclear for unattended use, run that provider interactively on a daily owner-triggered batch and record the dependency; never automate a consumer web UI.

## Step 8 (month 3-4): SIM_PRECHECK

Promote with the owner HMAC after step 4-7 evidence. Run `sim_precheck` on whitelisted instruments only; archive `Cost`, `EstimatedCashRequired`, `MarginImpactBuySell`, `PreCheckResult`, `ErrorInfo`.

Acceptance: 30 prechecks across ≥ 10 instruments; cost fields parsed; no `ErrorInfo`. Failure path: precheck errors on `ExternalReference` or `FieldGroups` mean the documented request shape differs for your entitlement; adjust the builder with a test, never by hand-editing payloads.

## Step 9 (month 4-6): SIM_EXECUTION (code to be written, reviewed separately)

Writes `POST /trade/v2/orders` with `ManualOrder:false`, `x-request-id`, `ExternalReference`; handles `TradeNotCompleted` by `/port` readback before any retry; cancel path; reconciliation of every fill to a certificate; kill switch watchdog.

Acceptance: 60 days, zero duplicate orders, zero orders without a certificate, reconciliation clean. This step requires a second code review (OpenAI) before merge.

## Step 10 (month 6+): shadow live quotes; LIVE remains blocked

LIVE application request (requires tested SIM app and funded account) only after steps 1-9 and an independent security review of the executor. The v0.2 code raises `PermissionError` on LIVE promotion by design; enabling it is a separate release with its own review.

## Costs (planning figures, not quotes)

- Subscriptions: $140 to $330/month depending on tiers; metered overflow $0 to $400/month depending on research volume (CLAUDE_REVIEW §8).
- Jev: < $100/month at 2 billion input tokens.
- Data: public sources free; a licensed point-in-time universe is an open item (Q5), typically a four-figure annual cost.
- Disk: ~10 GB for Lean + Mathlib; ledger and archives grow ~1-5 GB/year at 200 documents/day.
- Time: the owner's recurring duties are the monthly anchor verification and the gate promotions; everything else is designed to be unattended within the broker-session constraint.
