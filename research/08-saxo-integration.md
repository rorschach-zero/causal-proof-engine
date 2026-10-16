# 08 Saxo integration requirements

Entry point for `02/02`, `07/01` steps 4–10, `ref/cpe/saxo_sim.py`, `ref/docs/Saxo.md`. §1–§4 summarise the
original; §5 is review. **This session did not contact Saxo.** All facts below are PACKAGE-VERIFIED (read on
2026-10-16 by the package author, not archived as bytes) or UNVERIFIED as marked.

## 1. Facts the package verified against developer.saxo (`02/02` §1, `01/03` §2)

- Environments: SIM base `https://gateway.saxobank.com/sim/openapi`, LIVE `https://gateway.saxobank.com/openapi`;
  auth `sim.logonvalidation.net` / `live.logonvalidation.net`; streaming hosts per environment. SIM is "a copy of
  our live environment with a simulated $100,000 account value"; "certain specific functionality such as
  reporting and market data are not available in SIM". One-day Developer Portal tokens are SIM-only. App key and
  secret are not shared between SIM and LIVE; LIVE requires "permission and testing before applications are
  deployed".
- LIVE credentials for direct clients: at least one SIM app, a funded live account, confirmation of sufficient
  SIM testing; evaluation mostly automatic, credentials "within minutes"; LIVE apps "extensively monitored".
- OAuth Authorization Code with PKCE: `/authorize`, `/token`, S256 mandatory, verifier 43–128 chars; documented
  example `expires_in 1200`, `refresh_token_expires_in 2400` seconds; refresh by POST without a browser step
  shown; rotation and re-login policy not described.
- Precheck `POST /trade/v2/orders/precheck`: fields include AccountKey, Amount, AssetType, BuySell, OrderType,
  OrderPrice, OrderDuration, Uic, `ExternalReference` (≤ 50 chars), `FieldGroups` (values not enumerated;
  examples `Costs`, `MarginImpactBuySell`); `ManualOrder` is **not** listed on the precheck page; response
  carries `PreCheckResult`, `EstimatedCashRequired`, `Cost`, `CostInAccountCurrency`, `ErrorInfo`,
  `MarginImpactBuySell`.
- Order placement: `ManualOrder` "indicates if the order is originated by a manual or automatic action";
  automated = "generated and/or routed without human intervention"; the field "will soon be made mandatory for
  almost all applications"; an order generated automatically but confirmed by the user before sending counts as
  manual. Duplicate protection: an identical order within 15 seconds without a different `x-request-id` header
  is rejected; on timeout `TradeNotCompleted` means status unknown, check the portfolio. FX options are not
  tradable via OpenAPI; up to three related orders; `ToOpenClose` only for option types.

## 2. Not verified (`02/02` §2)

Multi-leg precheck endpoint (navigation link only); SIM delayed market data after linking a live account (help
article of 2026-09-07 not fetched); OpenAPI availability, commission schedule, minimum ticket sizes, FX
conversion fees and enabled asset types for Saxo Bank (Schweiz) AG retail clients; **long-lived unattended
session for an individual LIVE app (Q1, blocking)**; whether precheck accepts or ignores `ManualOrder` (Q3);
exact `/port` and `/ref` read paths (to be confirmed against the reference docs at implementation).

## 3. Gate state machine (`02/02` §3)

| State | Allowed calls | Evidence bundle for promotion |
|---|---|---|
| RESEARCH_ONLY | none | n/a |
| SIM_READ_ONLY | accounts, balances, positions, orders (`/port`); instruments and details (`/ref`) | 7 days of successful readbacks, reconciliation report |
| SIM_PRECHECK | plus precheck with the pilot whitelist | 30 prechecks over ≥ 10 instruments, cost fields archived |
| SIM_EXECUTION | plus SIM `POST /trade/v2/orders` with `ManualOrder:false`, `x-request-id`, `ExternalReference` (**code does not exist**) | 60 days, zero duplicate orders, every fill reconciled to a certificate |
| SHADOW_LIVE_QUOTES | LIVE read-only app, no write rights | 90 days shadow book vs benchmarks |
| LIVE_CAPPED_1000 | blocked in reference code; separate release plus external risk gate | independent security review |

Rules: promotion one step at a time with owner HMAC over `(from, to, evidence_bundle_sha256)`; demotion
unrestricted (kill switch); automatic demotion to SIM_READ_ONLY on a missing mandatory pre-trade input,
heartbeat loss or anchor failure.

## 4. Pilot instrument and order gates (`02/02` §4), if LIVE is ever enabled

Whitelist Stock, Etf, Bond, MutualFund, fully paid; `tradable` only from `/ref` readback; all CFDs, FX, options,
futures excluded; no shorts. Orders: `OrderType Limit`, `DayOrder`, `ExternalReference = certificate_id`, fresh
`x-request-id` per attempt, integer quantities ≥ lot size, price plausibility against the last quote. Pre-trade:
session healthy, quote age < 15 min, gate heartbeat < 5 min, USD/CHF known, no duplicate certificate id, market
hours, precheck without `ErrorInfo`, worst-case loss and commission within limits, pre-trade disclaimers never
auto-accepted. Post-trade: every fill reconciled against its certificate; deviations demote the gate.

## 5. Review and requirements for the eventual integration

**Nothing here is implemented, and nothing in this repository should call Saxo until the roadmap phase that
authorises SIM read-only is approved and the owner has created the SIM application.** The requirements below
restate the package's design as a checklist and add the review's conditions (REVISION where new).

Account and policy (owner actions, before any code):
- [ ] Saxo Developer Portal SIM application created by the owner; one-day SIM token handled only in the
      executor principal's session, never in a file (`07/01` step 4).
- [ ] Written question to Saxo OpenAPI support on unattended refresh-token lifetime and rotation for an
      individual app (Q1), and on whether automated order entry (`ManualOrder:false`) is permitted on the
      owner's account type (REVISION: this is an account-permission and conduct question, not only a field).
- [ ] Retail entitlements of Saxo Bank (Schweiz) AG read from account documents and `/ref` readback (Q6).
- [ ] Decision whether a daily owner login is acceptable if Q1 is negative (`07/02` §E question 2).

Executor design (before SIM_READ_ONLY code):
- [ ] Executor is a separate OS principal and process; gate state derived by replaying the anchored ledger
      (REVISION, from probe P5); owner MAC verified by the executor itself.
- [ ] Token-safe error types (no request objects, no headers in exceptions or logs); redaction tests in CI.
- [ ] Egress allow-list for the executor limited to the Saxo hosts; researcher principal cannot reach them.
- [ ] Read paths (`/port/v1/...`, `/ref/v1/instruments/...`) confirmed against current reference docs and
      archived as bytes in the ingest log on the day they are read.
- [ ] Reconciliation report format (simulated balance, positions, open orders) and its ledger record type.

Precheck phase:
- [ ] Payload builder exactly as documented, with Q3 resolved empirically on the first SIM call (with and
      without `ManualOrder`), responses archived.
- [ ] `FieldGroups` values discovered and recorded; cost fields parsed into the cost model
      (`07-portfolio-and-risk.md` §6 item 7).

Execution phase (separate review, Codex second review required by `07/01` step 9):
- [ ] Idempotency: `ExternalReference = certificate_id`, fresh `x-request-id` per attempt, no retry after
      `TradeNotCompleted` without a `/port` readback; cancel path; kill-switch watchdog.
- [ ] Every fill reconciled to a certificate; mismatch demotes the gate automatically.
- [ ] 60-day SIM evidence bundle before any discussion of shadow-live quotes.

Observations:
1. **"Hands-off" is a broker-side question before it is a software question** (`02/02` §5). The package is
   right to make Q1 blocking. If Saxo requires periodic interactive login, the architecture does not change; the
   owner's daily ritual (already needed for the OpenAI batch) absorbs it.
2. **The `ManualOrder` semantics have a compliance dimension.** Saxo monitors LIVE apps and intends to make the
   flag mandatory. An automated research system that places orders must declare them automatic. Whether the
   owner's account is permitted to do so is a question for Saxo, to be asked in writing before SIM_EXECUTION
   code is written, not before LIVE.
3. **SIM has no market data** per the environments page; quotes come from readbacks and may be delayed or
   absent (Q7). The staleness gate (15 minutes) may be unsatisfiable in SIM; the precheck phase should measure
   quote age distribution and set the gate from data.
4. **The reference `sim_precheck` reads the token from an environment variable.** Acceptable for a one-day SIM
   token in an interactive session; not acceptable for the executor service, which must read from the OS
   credential store and never from the process environment (environment variables leak into crash dumps and
   child processes).
