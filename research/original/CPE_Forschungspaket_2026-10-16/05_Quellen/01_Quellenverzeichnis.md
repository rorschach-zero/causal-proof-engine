# 01 Quellenverzeichnis

Alle Quellen mit Datum des Zugriffs und Verifikationsstatus. "Verifiziert" bedeutet: Inhalt am genannten Datum gegen die genannte URL gelesen. "Titel verifiziert" bedeutet: Existenz und Titel über die arXiv-API bestätigt, Inhalt nicht vollständig gelesen. "UNVERIFIZIERT" bedeutet: in dieser Sitzung nicht abrufbar oder nicht geprüft. "Allgemeinwissen" bedeutet: Standardliteratur, in dieser Sitzung nicht gegen eine URL geprüft.

## A. Saxo Bank OpenAPI (verifiziert 16.10.2026)
1. Environments: https://www.developer.saxo/openapi/learn/environments
2. Order Placement (ManualOrder, x-request-id, TradeNotCompleted, FX-Optionen): https://www.developer.saxo/openapi/learn/order-placement
3. Precheck-Referenz: https://www.developer.saxo/openapi/referencedocs/trade/v2/orders/post__trade__precheck
4. OAuth Authorization Code mit PKCE: https://www.developer.saxo/openapi/learn/oauth-authorization-code-grant-pkce
5. LIVE-Credentials für Direktkunden: https://www.developer.saxo/openapi/learn/direct-clients-request-for-openapi-application-credentials-for-the-live-environ
6. UNVERIFIZIERT: Multi-Leg-Precheck https://www.developer.saxo/openapi/referencedocs/trade/v2/orders/post__trade__multileg_precheck (nur als Link gesehen)
7. UNVERIFIZIERT: Hilfeartikel SIM-Marktdaten nach Live-Verknüpfung (07.09.2026) https://openapi.help.saxo/hc/en-us/articles/4416934146449-How-do-I-connect-a-Live-account-to-a-SIM-Demo-account
8. Nicht einzeln geprüft (aus v0.1 übernommen): Reference Data https://www.developer.saxo/openapi/learn/reference-data ; Port Orders https://www.developer.saxo/openapi/referencedocs/port/v1/orders ; Core Business Concepts https://www.developer.saxo/openapi/learn/core-business-concepts ; Welcome https://www.developer.saxo/openapi/learn/welcome

## B. TypeSafe Jev
9. Live OpenAPI-Dokument (verifiziert, archiviert als `typesafe_openapi_2026-10-16.json`): https://api.typesafe.ai/openapi.json (Swagger-UI unter https://api.typesafe.ai/docs)
10. Vendor-Blog "Introducing System One models and Jev" (verifiziert 16.10.2026, Blogdatum 15.09.2026): https://typesafe.ai/blog/introducing-system-one-models-and-jev
11. arXiv 2609.37647 "Evaluating and Benchmarking the System One Model Jev" (Titel verifiziert): https://arxiv.org/abs/2609.37647
12. arXiv 2609.33209 "Beyond Calibration: Do a Typed-Decision Model's Probabilities Obey the Probability Axioms?" (Abstract verifiziert): https://arxiv.org/abs/2609.33209
13. Sekundärquellen zum Preis (nicht als Primärquelle verwendet): eesel.ai "TypeSafe Jev pricing (2026)" https://www.eesel.ai/blog/typesafe-jev-pricing

## C. Modellzugang und Abonnements (verifiziert 16.10.2026)
14. Anthropic: "Use the Claude Agent SDK with your Claude plan" https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
15. Anthropic: "Monthly API credits for Max and Team plans" https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans
16. OpenAI Codex Authentifizierung: https://learn.chatgpt.com/docs/auth (Redirect von https://developers.openai.com/codex/auth)
17. OpenAI Codex Pricing: https://learn.chatgpt.com/docs/pricing (Redirect von https://developers.openai.com/codex/pricing)
18. Gemini CLI Quotas and Pricing: https://geminicli.com/docs/resources/quota-and-pricing/
19. Gemini for Google Cloud Quotas (Stand 13.10.2026): https://docs.cloud.google.com/gemini/docs/quotas
20. Google-Blog (24.09.2025) Gemini CLI höhere Limits für AI Pro/Ultra: https://blog.google/innovation-and-ai/technology/developers-tools/gemini-cli-code-assist-higher-limits/
21. UNVERIFIZIERT (aus v0.1): Gemini 4 Argon Modellseite https://ai.google.dev/gemini-api/docs/latest-model

## D. Statistik, Entscheidungstheorie, Kausalität
22. Ramdas, Ruf, Larsson, Koolen, "Admissible anytime-valid sequential inference must rely on nonnegative martingales" (Titel verifiziert): https://arxiv.org/abs/2009.03167
23. Waudby-Smith, Ramdas, "Estimating means of bounded random variables by betting" (Allgemeinwissen, Formel UNVERIFIZIERT): https://arxiv.org/abs/2010.09686
24. Laroche, Trichelair, Tachet des Combes, "Safe Policy Improvement with Baseline Bootstrapping" (ICML 2019, aus v0.1): https://proceedings.mlr.press/v97/laroche19a.html
25. "Safe Policy Improvement Approaches and their Limitations" (Titel verifiziert): https://arxiv.org/abs/2208.00724
26. Adams, MacKay, "Bayesian Online Changepoint Detection" (aus v0.1): https://arxiv.org/abs/0710.3742
27. "StockBench: Can LLM Agents Trade Stocks Profitably In Real-world Markets?" (Titel verifiziert): https://arxiv.org/abs/2510.02209
28. Nilsson, "Probabilistic logic", Artificial Intelligence 28 (1986) (Allgemeinwissen)
29. Walley, "Statistical Reasoning with Imprecise Probabilities" (1991) (Allgemeinwissen)
30. Kelly, "A New Interpretation of Information Rate" (1956); MacLean, Thorp, Ziemba (Hrsg.), "The Kelly Capital Growth Investment Criterion" (2010) (Allgemeinwissen)
31. Brier (1950); Gneiting, Raftery, "Strictly Proper Scoring Rules, Prediction, and Estimation" (2007) (Allgemeinwissen)
32. Survivorship und extreme Gewinner (aus v0.1, nicht geprüft): https://www.tandfonline.com/doi/full/10.1080/0015198X.2023.2188870
33. AlphaEvolve (aus v0.1, nicht geprüft): https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/

## E. Lean und Mathlib
34. Lean 4: https://lean-lang.org/theorem_proving_in_lean4/ (aus v0.1)
35. Mathlib4: https://github.com/leanprover-community/mathlib4 ; verwendete Revision `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2` mit Lean `leanprover/lean4:v4.35.0` (lokal kompiliert 16.10.2026; GitHub-API war über den Sitzungsproxy nicht erreichbar, der Mathlib-Cache wurde über `lake exe cache get` bezogen)
36. elan-Installer: https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh (elan 4.2.4)

## F. Schweizer Steuerrecht (Allgemeinwissen, keine Rechtsberatung)
37. ESTV Kreisschreiben Nr. 36 "Gewerbsmässiger Wertschriftenhandel" (Kriterien: Haltedauer, Transaktionsvolumen, Fremdfinanzierung, Derivateeinsatz). In dieser Sitzung nicht abgerufen; mit Steuerberater zu klären.

## G. Eingabedokumente des Reviews
38. `CLAUDE_REVIEW_PROMPT.md`, `INDEPENDENT_AUDIT_FINDINGS.md`, `REVIEW_SCORECARD.csv`, `START_HERE.md`, `MANIFEST.sha256` und `source_v0_1/` aus `CPE_Claude_Independent_Review_2026-10-16.zip` (Manifest 20/20 verifiziert). Die separat hochgeladene `CPE_Claude_Review_Prompt 1.md` war byte-identisch mit der im ZIP enthaltenen Fassung.
