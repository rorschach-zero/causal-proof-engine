# Saxo implementation: SIM-first, safe-by-default

Saxo documentation verified on 2026-10-16. This project includes a precheck-only SIM client. It does not initiate purchases or sales.

## Access

1. Create Saxo OpenAPI SIM app: https://www.developer.saxo/openapi/learn/environments
2. Obtain a SIM test token using official Developer Portal (time limited). Set as `SAXO_SIM_ACCESS_TOKEN` in a secure process environment, not `.env` committed to Git.
3. Link an activated/live funded Saxo account only if desired and authorized; Saxo help dated Sep 7, 2026 reports SIM receives delayed market data for available live instruments. Without this, SIM quote access may be limited: https://openapi.help.saxo/hc/en-us/articles/4416934146449-How-do-I-connect-a-Live-account-to-a-SIM-Demo-account
4. Create proper OAuth PKCE application and renewable sessions; no unattended open browser authentication shortcuts. https://www.developer.saxo/openapi/learn/oauth-authorization-code-grant-pkce
5. Get relevant instrument UIC and AssetType from RefData: https://www.developer.saxo/openapi/learn/reference-data
6. Use PORT `/port/v1/orders` and position endpoints to reconcile state: https://www.developer.saxo/openapi/referencedocs/port/v1/orders
7. Call SIM-only `/trade/v2/orders/precheck` using account key, UIC, asset type, limit, amount. Review costs, disclaimers and `PreCheckResult`, including `ErrorInfo` before proposing any order: https://www.developer.saxo/openapi/referencedocs/trade/v2/orders/post__trade__precheck
8. Multi-leg listed option precheck is separately supported when instrument exchange permits: https://www.developer.saxo/openapi/referencedocs/trade/v2/orders/post__trade__multileg_precheck
9. LIVE app approval is independent: https://www.developer.saxo/openapi/learn/direct-clients-request-for-openapi-application-credentials-for-the-live-environ
10. Saxo docs distinguish automated entries from manual and require `ManualOrder: false` for fully autonomous systems. https://www.developer.saxo/openapi/learn/order-placement

## Live promotion checklist

- Explicit owner account authorization, Saxo LIVE credentials, and appropriate instruments/permissions.
- Independent immutable risk engine, kill switch and trade freeze on data/transport errors.
- Portfolio limits and worst-case full-premium loss limits with no margin debt in pilot.
- Bid/ask, liquidity, market hours, live account FX conversion, commission and pretrade disclaimer inspection.
- Idempotent order references, account/position reconciliation, fill data and alert logging.
- Signed strategy version and proof certificate per candidate order, including published_at/known_at cutoffs.
- Shadow comparison vs no-trade, cash, broad equity index and static ETF benchmark.

Do not interpret SIM as realistic liquidity/execution. Paper trading does not prove alpha.
