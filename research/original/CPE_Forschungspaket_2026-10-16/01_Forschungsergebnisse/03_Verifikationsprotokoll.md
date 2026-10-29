# 03 Verifikationsprotokoll

Was in der Review-Sitzung vom 16.10.2026 tatsächlich ausgeführt oder gegen eine Primärquelle geprüft wurde. Nicht Geprüftes ist als UNVERIFIZIERT markiert und in `06/01` als offene Frage geführt.

## 1. Lokale Ausführung

| Schritt | Umgebung | Ergebnis |
|---|---|---|
| Manifestprüfung | `sha256sum -c MANIFEST.sha256` | 20/20 OK |
| v0.1-Tests | Python 3.13.16, scipy 1.18.1, httpx 2.13.0, pytest 8 | `11 passed` |
| Angriffsskript F1 bis F10 | `python -I attack_v01_reproduction.py` | siehe `01/02` Abschnitt A |
| Lean-Toolchain | elan 4.2.4; `lake new … math`; `lake exe cache get` (9'040 Dateien, 7,8 GB) | Lean `leanprover/lean4:v4.35.0`, Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2` |
| `BetThreshold.lean` | `lake env lean` | exit 0; alle drei Theoreme hängen nur von `propext`, `Classical.choice`, `Quot.sound` ab |
| `RiskBudget.lean` (neu, 7 Lemmata) | `lake env lean` | exit 0; gleiche Axiome |
| Negativkontrolle | Theorem mit falscher Schwelle 1/10 statt 4/49 | `linarith failed`, exit 1 (Toolchain prüft tatsächlich) |
| Referenzimplementierung v0.2 | `python -m pytest -q` | `31 passed` (auch nach Entpacken aus dem ZIP) |
| Secret-Scan | Regex auf Literale ≥ 24 Zeichen in `.py` | keine Treffer |

## 2. Extern verifiziert (gelesen 16.10.2026)

### Saxo OpenAPI
- Environments-Seite: SIM-Basis `https://gateway.saxobank.com/sim/openapi`, LIVE `https://gateway.saxobank.com/openapi`; Streaming `sim-streaming.saxobank.com` / `live-streaming.saxobank.com`; Auth `sim.logonvalidation.net` / `live.logonvalidation.net`. Ein-Tages-Tokens aus dem Developer Portal "are only authorized for the simulation environment". "certain specific functionality such as reporting and market data are not available in SIM". LIVE-Tokens nur über Security-Flows; App-Key und Secret werden zwischen SIM und LIVE nicht geteilt.
- Order-Placement-Seite: `ManualOrder` "Indicates if the order is originated by a manual or automatic action", derzeit optional, "will soon be made mandatory for almost all applications"; automatisiert = "generated and/or routed without human intervention", Ausführungsalgorithmen eingeschlossen; Order, die automatisch erzeugt, aber vom Nutzer vor dem Senden bestätigt wird, gilt als manuell. Platzierung `POST …/trade/v2/orders`, Änderung `PATCH`, Storno `DELETE …/trade/v2/orders/{OrderId}`. Duplikatschutz: identische Order innerhalb 15 Sekunden ohne anderen `x-request-id`-Header wird abgelehnt; bei Timeout `TradeNotCompleted` Status unbekannt, über Portfolio prüfen. FX-Optionen "not currently tradable via OpenAPI". Bis zu drei Orders in Relation; `FutureStrategies` ohne Related Orders.
- Precheck-Referenz: Felder AccountKey, AlgoOrderData (nur Live), Amount, AmountType (MutualFunds), AssetType, BuySell, ExecuteAtTradingSession, ExternalReference (String, max. 50), FieldGroups (Werte nicht enumeriert; Beispiel `MarginImpactBuySell`, `Costs`), ForwardDate, IsForceOpen, OrderDuration, OrderId, OrderPrice (optional bei Market), Orders, OrderType, PositionId, StopLimitPrice, StrategyId, SwitchInstrumentUic, ToOpenClose, TraderId, TraspasoIn, Uic. `ManualOrder` erscheint auf dieser Seite nicht. Antwort: `PreCheckResult`, `EstimatedCashRequired`, `Cost`/`CostInAccountCurrency`, `ErrorInfo`, `MarginImpactBuySell`.
- PKCE-Seite: `/authorize` und `/token`; `response_type=code`, `client_id`, `redirect_uri`, `state`, `code_challenge`, `code_challenge_method` ("MUST use S256 unless otherwise agreed"); Token-Tausch mit `grant_type=authorization_code` und `code_verifier`; Beispielantwort `expires_in: 1200`, `refresh_token_expires_in: 2400`; Refresh per `grant_type=refresh_token` mit `code_verifier`; Rotation nicht beschrieben; keine Aussage zu Re-Login-Pflicht.
- LIVE-Credentials für Direktkunden: mindestens eine SIM-App nötig; Live-Konto muss finanziert sein; Bewertung "in most cases handled automatically", Credentials "within minutes"; LIVE-Apps "extensively monitored"; keine Aussage zu Handelsberechtigungen, automatisiertem Handel oder `ManualOrder`.

### TypeSafe Jev
- Live `openapi.json` (Titel "TypeSafe", Version 0.2.0, archiviert in `05_Quellen/`): `GET /v1/models` (Name, Beschreibung, `release_date`); `POST /v1/systemone` mit `{model, state, questions, assets?}`; Fragetypen `noul` (Antwort: Wahrscheinlichkeit 0 bis 1), `choice` (Kriterien ≤ 255, Antwort: `choice`, `confidence`, `probabilities`), `score` (geordnete Rubrik ≤ 10 Stufen, Antwort: erwarteter Score, `confidence`, `legend`, `probabilities`), `box` (Bild). Bearer-Auth. Header `TypeSafe-Danger-Zone-Images` und `TypeSafe-Danger-Zone-Long-Context`. `usage.input_tokens` abrechenbar, `output_tokens` "currently free of charge". Kein Zeitstempelfeld.
- Vendor-Blog (15.09.2026): Preis "$0.042 / MTok" Input, Output "FREE"; Latenz "70ms-500ms"; Kalibrierungsbehauptung "higher confidence means higher accuracy"; Referenzantworten der Evals sind der Durchschnitt von GPT-6 Astra und Fable 5.1; Einschränkungen: keine Stringgenerierung, Kardinalität 255, Evals vom Modellteam geschrieben; Early Access über Warteliste; Rate-Limits nicht genannt.
- arXiv 2609.33209 (Abstract): auf 480 Komplementpaaren verfehlt p(X) + p(nicht X) die 1 um 0,064 im Mittel (95 %-KI 0,055 bis 0,072), rund fünfmal das Wiederholungsrauschen, konzentriert bei Unsicherheit; drei Einzel-Label-Wahrscheinlichkeiten summieren im Mittel auf 1,14. Vergleich Qwen3.8-27B: First-Token-Readout verfehlt um 0,293, verbalisiert um 0,122.
- arXiv-Titel per API bestätigt: 2609.37647 "Evaluating and Benchmarking the System One Model Jev"; 2609.33209 "Beyond Calibration: Do a Typed-Decision Model's Probabilities Obey the Probability Axioms?"; 2009.03167 "Admissible anytime-valid sequential inference must rely on nonnegative martingales"; 2510.02209 "StockBench: Can LLM Agents Trade Stocks Profitably In Real-world Markets?"; 2208.00724 "Safe Policy Improvement Approaches and their Limitations".

### Modellzugang
- support.claude.com Artikel 15036540: Update 15.06.2026, angekündigte Änderungen pausiert, "For now, nothing has changed"; Update 07.10.2026: Max- und Team-Pläne enthalten monatliche API-Credits für Agent SDK, `claude -p`, Claude API, Managed Agents; Abonnenten können Agent SDK, `claude -p` und Drittanbieter-Apps weiterhin gegen Abo-Limits nutzen.
- Artikel 17154008: Max 5x 100 USD/Monat, Max 20x 200 USD/Monat, Team Standard 20 USD/Sitz, Premium 100 USD/Sitz, Pool max. 500 USD; nutzbar für Messages API, Batches API, Playground, Managed Agents, Agent SDK; nicht für interaktives Claude Code, Extra-Nutzung, Bedrock/Vertex/Foundry; GitHub-Action-, IDE- und Desktop-gestartete Läufe zählen als Claude Code; kein Rollover; 7 Tage Wartefrist; ein Plan verknüpft mit einer Console-Organisation; "the Agent SDK credit announced in June isn't available".
- learn.chatgpt.com/docs/pricing: Codex in Free, Go, Plus, Pro, Business, Edu, Enterprise enthalten; API-Key "Great for automation in shared environments like CI"; Pro "currently have no five-hour limit"; GPT-5.5 aus Codex mit ChatGPT-Login am 14.10.2026 entfernt; API-Key-Sitzungen nicht betroffen.
- learn.chatgpt.com/docs/auth: ChatGPT-Login über Browser; API-Key "for programmatic Codex CLI workflows, such as CI/CD"; "Codex access tokens" für "trusted scripts, schedulers, and private CI runners", nur in Enterprise-Workspaces durch Admin-Freigabe; Credential-Speicher `auth.json` oder OS-Keyring.
- geminicli.com Quota-Seite: Login mit Google kostenlos 1'000 Anfragen/Tag; Google AI Pro 1'500/Tag; AI Ultra 2'000/Tag (persönliche Konten); API-Key Free Tier 250/Tag nur Flash; Banner: "Gemini CLI was replaced by Antigravity CLI on June 18th, 2026" für Unpaid Tier und Google-One-Nutzer; Headless-Nutzung nicht adressiert. Google-Cloud-Quota-Seite (Stand 13.10.2026): Standard 1'500, Enterprise 2'000 Anfragen/Tag für Gemini CLI und Agent Mode kombiniert.

## 3. UNVERIFIZIERT (nicht abrufbar oder nicht geprüft)

- Saxo Multi-Leg-Precheck-Endpunkt `/trade/v2/orders/multileg/precheck` (nur Navigationslink gesehen).
- Saxo-Hilfeartikel 4416934146449 (SIM erhält verzögerte Marktdaten nach Verknüpfung mit Live-Konto, datiert 07.09.2026): nicht abgerufen.
- OpenAPI-Verfügbarkeit und Berechtigungen für Retail-Kunden der Saxo Bank (Schweiz) AG: kontoabhängig.
- Langlebige unbeaufsichtigte Saxo-Sitzung für eine individuelle LIVE-App.
- Ob Google AI Pro vom Antigravity-CLI-Wechsel betroffen ist.
- OpenTimestamps und vergleichbare Zeitstempeldienste als Ankerlösung.
- Jev-Rate-Limits und Early-Access-Zeitplan.
- Es wurde kein Saxo-Konto, kein LLM-Anbieter und kein Jev-Endpunkt mit Credentials angesprochen. Kein Kontodatenzugriff.
