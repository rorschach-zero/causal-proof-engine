# 01 Offene Fragen Q1 bis Q9

**Blockierend** bedeutet: muss beantwortet sein, bevor das Gate `SIM_READ_ONLY` verlässt.

| # | Frage | Warum es zählt | Validierungsweg | Zuständig |
|---|---|---|---|---|
| Q1 (**blockierend**) | Kann eine individuelle Saxo-OpenAPI-App eine unbeaufsichtigte Sitzung (Refresh-Token-Lebensdauer und Rotation) über Tage/Wochen halten? Die PKCE-Seite zeigt nur Beispielwerte (`expires_in 1200`, `refresh_token_expires_in 2400`). | Entscheidet, ob "hands-off" brokerseitig überhaupt möglich ist. | Implementierungsschritt 5: 72-Stunden-Refresh-Test in SIM; schriftliche Anfrage an Saxo OpenAPI Support. | Salah |
| Q2 (**blockierend**) | Welche der drei LLM-Anbieter erlauben unbeaufsichtigte, geplante Nutzung unter den Abonnements des Eigentümers? Verifiziert: Anthropic-Max-API-Credits (Agent SDK/API); OpenAI dokumentiert API-Keys für programmatische Workflows und Enterprise-only-Automatisierungstokens; Gemini-CLI-Kontingente für persönliche Konten, Headless nicht adressiert, Antigravity-CLI-Hinweis Juni 2026. | Rechtmässigkeit und Kontinuität der Forschungspipeline; Budget. | Am Einrichtungstag die aktuellen Terms-Seiten lesen; datierte Screenshots im Ledger; bei Unklarheit eigentümergestarteter Batch, keine API-Keys (Eigentümervorgabe Abo-only). | Salah |
| Q3 | Akzeptiert oder ignoriert der Saxo-Precheck `ManualOrder`, und welche `FieldGroups`-Werte sind gültig? Die Precheck-Referenz listet `ManualOrder` nicht und enumeriert `FieldGroups` nicht. | Payload-Korrektheit. | Erster SIM-Precheck (Schritt 8) mit und ohne Feld; Antworten archivieren. | Salah |
| Q4 | Ist `/trade/v2/orders/multileg/precheck` verfügbar und für welche Börsen? Nur ein Navigationslink wurde gesehen. | Optionen sind im Pilot ohnehin ausgeschlossen; relevant für spätere Phasen. | Referenzdokumentation bei Implementierung. | Salah |
| Q5 | Quelle eines Point-in-Time-Universums mit Delistings für Backtests (lizenzierter Datensatz vs. Vorwärtsrekonstruktion aus Saxo-`/ref`-Snapshots). | Survivorship-Audit; Design-C-Basisraten. | Entscheid 16.10.2026: keine Lizenzkosten im ersten Jahr; Vorwärtsrekonstruktion aus Saxo-`/ref`-Snapshots; historischer Wald-Audit nur mit kostenlosen Quellen. | Salah |
| Q6 | Retail-Berechtigungen der Saxo Bank (Schweiz) AG: OpenAPI-Verfügbarkeit, Kommissionsschema, Mindest-Ticketgrössen, FX-Umrechnungsgebühren, freigeschaltete Assettypen. | Pilot-Risikolimits (Kommission ≤ 1 Prozent des Tickets), Instrumenten-Whitelist. | Kontodokumente und `/ref`-/`/port`-Readback in SIM_READ_ONLY; keine Kontodaten in AI-Chats. | Salah |
| Q7 | Liefert die Verknüpfung eines finanzierten Live-Kontos mit SIM verzögerte Marktdaten (Hilfeartikel vom 07.09.2026, hier nicht abgerufen)? | Quote-Staleness-Gate in SIM. | Artikel abrufen und archivieren; nach Verknüpfung testen. | Salah |
| Q8 | Jev-Early-Access-Zeitplan, Rate-Limits, und ob `jev-latest` ohne Ankündigung wechselt (das `model`-Feld der Antwort ist die Version of Record). | Verfügbarkeit einer obligatorischen Komponente. | `GET /v1/models` täglich; Adapter protokolliert zurückgegebenes Modell. | Salah / TypeSafe |
| Q9 | Schweizer Steuerrisiko der Einstufung als gewerbsmässiger Wertschriftenhändler unter einem automatisierten Design mit niedrigem Umschlag. | Könnte Gewinne zu steuerbarem Einkommen plus Sozialabgaben machen. | Schriftliche Stellungnahme eines Schweizer Steuerberaters vor LIVE; Designrandbedingung bereits gesetzt (Median-Haltedauer > 12 Monate, keine Derivate). | Salah |

## Was in dieser Sitzung nicht möglich war
- Kein Saxo-Konto- oder Connector-Zugriff; kein Live-Precheck ausgeführt.
- Keine LLM-Anbieter-Aufrufe; Adapter für Claude/OpenAI/Gemini bleiben gegen den Vertrag in `02/01` Abschnitt 5 zu schreiben.
- Hilfeartikel zu SIM-Marktdaten und die Multi-Leg-Precheck-Referenzseite wurden nicht abgerufen.
- Kein historischer Datensatz; kein Backtest gelaufen. Jede Leistungsaussage im Paket ist synthetisch oder hypothetisch.
