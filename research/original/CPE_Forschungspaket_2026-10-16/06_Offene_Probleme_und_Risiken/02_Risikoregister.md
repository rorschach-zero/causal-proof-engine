# 02 Risikoregister

Skala: Eintrittswahrscheinlichkeit (W) und Wirkung (A) jeweils niedrig / mittel / hoch, qualitativ; keine Zahl in diesem Register ist eine gemessene Grösse.

## A. Wissenschaftliche Risiken

| Risiko | W | A | Gegenmassnahme | Restrisiko |
|---|---|---|---|---|
| Kein Prognose-Skill vorhanden (H0 nicht verworfen) | mittel | hoch | Register und E-Prozess liefern das Ergebnis in 12 Monaten; Negativergebnis wird publiziert; Stopp-Kriterium in `04/03` §7 | akzeptiert: Programm endet mit einem sauberen Negativbefund |
| Meilenstein-Skill überträgt sich nicht auf 10x-Diskrimination | mittel bis hoch | hoch | Schattenbuch ab Jahr 3; keine Kapitalerhöhung vor Nachweis | akzeptiert, explizit als HYPOTHESE geführt |
| Drei Modelle sind faktisch ein Modell (n_eff < 1,5) | mittel | mittel | n_eff monatlich; Rückbau auf ein Modell plus adversariale Prompts bei Bestätigung | mittel |
| Jev-Inkohärenz verfälscht Triage | mittel | mittel | Komplement-Gap je Aufruf, RE_RESEARCH bei > 0,15, `−Jev`-Ablation | niedrig |
| Overfitting durch Selbstverbesserung | hoch ohne Kontrollen | hoch | Promoter-Trennung, Shuffled-Label, zeitverschobene Holdouts, Canaries, ein Test je Artefakt | niedrig bis mittel |
| Leakage durch Modellwissen (Trainingsstichtag nach Ereignis) | hoch für alte Ereignisse | hoch | Stichtage je Prognose; Ereignisse vor Modellstichtag aus Skill-Statistik ausgeschlossen | niedrig |
| Vakuöse Intervalle in Design A bei grossen Graphen | hoch | mittel | Design B als Maschine, A nur auf ≤ 14 Entscheidungsereignissen | niedrig |

## B. Finanzielle Risiken

| Risiko | W | A | Gegenmassnahme | Restrisiko |
|---|---|---|---|---|
| Kapitalruin des Piloten | mittel | hoch für den Piloten, begrenzt (1'000 USD) für den Eigentümer | voll bezahlte Instrumente, Caps, Worst-Loss-Grenze, fraktionales Kelly, 3'000 USD ausserhalb | mittel |
| Zielrendite 58,49 Prozent CAGR wird nicht erreicht | hoch | mittel (Erwartungsmanagement) | explizit als Tail-Anspruch deklariert; Always-invested-Benchmark | akzeptiert |
| Kontingente der Abos begrenzen das Forschungsvolumen | mittel | mittel | Jev-Vorsortierung, Runde 2 nur bei ABSTAIN, 5 bis 10 Runden/Tag, Upgrade nur bei nachgewiesenem Bedarf (`02/03`) | niedrig |
| Nutzungsbedingungen ändern sich (Abo-Betrieb) | mittel | mittel | quartalsweise Terms-Prüfung mit Screenshots im Ledger; Wechsel in eigentümergestarteten Batch | niedrig |
| Spät verkaufen nach Crash (Late Exit) | mittel | hoch | Hazard-Politik mit Vorlaufindikatoren, Hysterese, kein Zwangsverkauf, Late-Exit-Audit, H6 | mittel; keine Crash-Vorhersage behauptet |
| Fehlalarme der Krisenpolitik kosten Rendite | mittel | mittel | H6 misst Fehlalarmkosten; Drosselung wird entfernt, falls sie nicht netto hilft | mittel |
| Kommissionen und Spreads fressen kleine Tickets | hoch bei 1'000 USD | mittel | Mindestticket mit Kommission ≤ 1 Prozent, max. 8 Positionen, Kosten in R_k | mittel |
| FX-Risiko CHF/USD/Instrumentwährung | mittel | mittel | Währungsgrenze ≤ 50 Prozent ausserhalb CHF/USD; FX in Szenarien | mittel |
| Schweizer Einstufung als gewerbsmässiger Händler | niedrig bis mittel | hoch | Median-Haltedauer > 12 Monate, max. 24 Round-Trips/Jahr, keine Derivate; Steuerberater vor LIVE | niedrig |

## C. Technische und Sicherheitsrisiken

| Risiko | W | A | Gegenmassnahme | Restrisiko |
|---|---|---|---|---|
| Broker-Token gelangt in Logs oder LLM-Kontext | mittel in v0.1 | hoch | tokensichere Fehlertypen, Redaktionsfilter, getrennte Konten, Credential Manager, Egress-Allowlists | niedrig |
| Ledger-Manipulation (Rewrite, Truncation) | hoch in v0.1 | hoch (entwertet jede Evidenz) | Anker ausserhalb der Schreibrechte, HMAC, seq, monotone Zeit, monatliche Eigentümerprüfung | niedrig, sofern Ankerspeicher korrekt getrennt |
| Schreiberprozess selbst bösartig (T5) | niedrig | hoch | ausserhalb des Datei-Ledgers; append-only Store eines anderen Prinzipals (spätere Phase) | mittel |
| Doppelorders bei Timeouts | mittel | hoch | `x-request-id`, `ExternalReference`, kein Retry nach `TradeNotCompleted` ohne Readback | niedrig |
| Gate-Promotion durch Automation | niedrig | hoch | HMAC-Eigentümersecret, ein Schritt, LIVE im Code blockiert | niedrig |
| Uhrenversatz, veraltete Quotes | mittel | mittel | NTP, Drift-Log, Staleness-Gates | niedrig |
| Anbieterausfall (Jev, LLM, Saxo) | mittel | mittel | Retries, Degradationsleiter für Forschung, fail-closed für Orders | niedrig |
| Nutzungsbedingungen untersagen unbeaufsichtigte Abo-Nutzung | mittel | mittel | eigentümergestartete Batches (OpenAI standardmässig); keine API-Keys ohne Eigentümerentscheid; keine UI-Automatisierung | niedrig |
| Lean-Toolchain-Drift | mittel | niedrig | exakte Pins (`lean-toolchain`, `lake-manifest.json`), CI-Job | niedrig |

## D. Prozessrisiken

| Risiko | W | A | Gegenmassnahme |
|---|---|---|---|
| Vorregistrierung wird stillschweigend geändert | mittel | hoch | `preregistration_amendment` im Ledger vor Entblindung; Promoter prüft |
| Gewinner-Auswahl unter vielen Tests | hoch ohne Regel | hoch | ein primärer E-Prozess je Behauptung; exploratorische Tests mit Anzahl berichtet |
| Strategische Abstention eines Modells | mittel | mittel | Abstentionsrate und Fusions-Brier auf abstinenten Items berichtet |
| Eigentümer übernimmt Prüfpflichten nicht (Anker, Gates) | mittel | hoch | zwei wiederkehrende Pflichten explizit benannt; CI blockiert bei fehlender Ankerprüfung |
