# 02 Saxo-Broker-Integration und Gates

Kein Saxo-Connector ist installiert; es wurden keine Kontodaten abgerufen. Alle Aussagen in Abschnitt 1 wurden am 16.10.2026 gegen offizielle developer.saxo-Seiten geprüft; Abschnitt 2 listet, was nicht geprüft werden konnte.

## 1. Verifizierte Fakten

| Behauptung | Quelle |
|---|---|
| SIM-Basis `https://gateway.saxobank.com/sim/openapi`, LIVE `https://gateway.saxobank.com/openapi`; Auth `sim.logonvalidation.net` / `live.logonvalidation.net`; Streaming `sim-streaming.saxobank.com/sim/oapi/streaming/ws` / `live-streaming.saxobank.com/oapi/streaming/ws` | learn/environments |
| SIM ist "a copy of our live environment with a simulated $100,000.- account value"; technische Probleme dort haben niedrigere Priorität | learn/environments |
| Ein-Tages-Tokens des Developer Portals gelten nur für SIM | learn/environments |
| "certain specific functionality such as reporting and market data are not available in SIM" | learn/environments |
| LIVE-Token nur über Security-Flows; App-Key/Secret zwischen SIM und LIVE nicht geteilt; LIVE verlangt "permission and testing before applications are deployed" | learn/environments |
| LIVE-App für Direktkunden: mindestens eine SIM-App, finanziertes Live-Konto, Bestätigung ausreichender SIM-Tests, Bewertung meist automatisch, Credentials "within minutes", Apps "extensively monitored" | learn/direct-clients-request-… |
| PKCE: `/authorize`, `/token`, S256 verpflichtend, `code_verifier` 43 bis 128 Zeichen, Beispiel `expires_in 1200`, `refresh_token_expires_in 2400`; Refresh per POST ohne Browser-Schritt gezeigt; Rotation und Re-Login nicht beschrieben | learn/oauth-authorization-code-grant-pkce |
| Precheck-Request-Felder inkl. `ExternalReference` ≤ 50 Zeichen; `ManualOrder` nicht auf der Precheck-Seite; `FieldGroups`-Werte nicht enumeriert (Beispiel `MarginImpactBuySell`, `Costs`); Antwort `PreCheckResult`, `EstimatedCashRequired`, `Cost`, `CostInAccountCurrency`, `ErrorInfo`, `MarginImpactBuySell` | referencedocs/trade/v2/orders/post__trade__precheck |
| `ManualOrder`-Semantik; automatisiert = "generated and/or routed without human intervention"; Feld "will soon be made mandatory for almost all applications"; Beispiele setzen `true` | learn/order-placement |
| Duplikatschutz: gleiche Order innerhalb 15 Sekunden ohne anderen `x-request-id` abgelehnt; bei laufender Order keinen zweiten Aufruf; `TradeNotCompleted` = Status unbekannt, über Portfolio prüfen | learn/order-placement |
| FX-Optionen nicht über OpenAPI handelbar; `ToOpenClose` nur für StockIndexOption, StockOption, FuturesOption; bis zu drei Related Orders | learn/order-placement |

## 2. UNVERIFIZIERT (kontoabhängig oder nicht abgerufen)

- Multi-Leg-Precheck-Endpunkt (nur Navigationslink gesehen); Optionen sind im Pilot ohnehin ausgeschlossen.
- Verzögerte SIM-Marktdaten nach Verknüpfung mit einem Live-Konto (Hilfeartikel vom 07.09.2026 nicht abgerufen).
- OpenAPI-Verfügbarkeit, Kommissionsschema, Mindest-Ticketgrössen, FX-Umrechnungsgebühren, freigeschaltete Assettypen für Retail-Kunden der Saxo Bank (Schweiz) AG.
- Langlebige unbeaufsichtigte Sitzung (Refresh-Token-Lebensdauer und Rotation) für eine individuelle LIVE-App. **Blockierend** für "hands-off" (Q1).
- Ob der Precheck `ManualOrder` akzeptiert oder ignoriert (Q3).
- Die genauen Pfade der `/port`- und `/ref`-Lese-Endpunkte wurden in dieser Sitzung nicht einzeln gegen die Referenzdokumentation geprüft; die in `01/03` genannten Pfade sind bei der Implementierung zu bestätigen.

## 3. Gate-Zustandsmaschine (Spezifikation)

| Zustand | Erlaubte Aufrufe | Evidenzbündel für Promotion |
|---|---|---|
| RESEARCH_ONLY | keine | n/a |
| SIM_READ_ONLY | Konten, Salden, Positionen, Orders (`/port`), Instrumente und Instrumentdetails (`/ref`) | 7 Tage erfolgreiche Readbacks, Abgleichbericht |
| SIM_PRECHECK | plus `POST /trade/v2/orders/precheck` mit Pilot-Whitelist | 30 Prechecks über ≥ 10 Instrumente, Kostenfelder archiviert |
| SIM_EXECUTION | plus SIM `POST /trade/v2/orders` mit `ManualOrder:false`, `x-request-id`, `ExternalReference` (Code existiert nicht) | 60 Tage, null Doppelorders, Abgleich jedes Fills mit einem Zertifikat |
| SHADOW_LIVE_QUOTES | LIVE-Read-only-App, keine Schreibrechte | 90 Tage Schattenbuch vs. Benchmarks |
| LIVE_CAPPED_1000 | im Referenzcode blockiert; separates Release plus externes Risiko-Gate | unabhängiges Sicherheitsreview |

Regeln: Promotion nur um einen Schritt mit Eigentümer-HMAC über `(from, to, evidence_bundle_sha256)`; Demotion uneingeschränkt (Kill-Switch); automatische Demotion auf SIM_READ_ONLY bei fehlendem obligatorischem Pre-Trade-Input, Heartbeat-Verlust oder Ankerfehler.

## 4. Pilot-Instrumente und Ordergates (für LIVE_CAPPED_1000, falls je aktiviert)

- Whitelist `Stock, Etf, Bond, MutualFund`, voll bezahlt, `tradable` nur aus `/ref`-Readback, nie von Hand gesetzt. Ausgeschlossen: alle CFDs, FxSpot, FxForward, FxOption, StockOption, StockIndexOption, FuturesOption, FutureContracts, FutureStrategies; kein Short.
- Order-Payload: `OrderType Limit`, `DayOrder`, `ExternalReference = certificate_id`, frischer `x-request-id` je Versuch, Stock/ETF-Mengen ganzzahlig ≥ Losgrösse, Preisplausibilität gegen letzte Quote.
- Pre-Trade-Gates: Session gesund, Quote-Alter < 15 Minuten, Gate-Heartbeat < 5 Minuten, USD/CHF-Umrechnung bekannt, keine doppelte Zertifikats-ID, Marktöffnungszeiten, Precheck ohne `ErrorInfo`, Worst-Case-Verlust und Kommission innerhalb Limits; Pre-Trade-Disclaimer werden nicht automatisch akzeptiert.
- Nach-Trade: jeder Fill wird gegen das Zertifikat abgeglichen; Abweichungen demotieren das Gate.

## 5. Unbeaufsichtigter Betrieb: die ehrliche Einordnung

Selbst mit perfekter Software hängt "hands-off" daran, ob Saxo eine Sitzung ohne Browser-Login über Tage und Wochen aufrechterhalten lässt. Die PKCE-Dokumentation zeigt einen browserlosen Refresh, aber nur Beispiellebensdauern von 20 bzw. 40 Minuten und keine Rotationspolitik. Der 72-Stunden-Refresh-Test (Implementierungssequenz Schritt 5) entscheidet, ob das Zielbild erreichbar ist oder ob der Eigentümer sich täglich einmal anmelden muss. Das ist eine dauerhafte Randbedingung, keine Software-Frage.
