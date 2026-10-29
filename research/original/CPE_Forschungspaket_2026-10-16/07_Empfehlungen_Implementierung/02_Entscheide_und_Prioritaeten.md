# 02 Entscheide, Prioritäten und was zuerst nicht gebaut wird

## A. Im Review getroffene Entscheide (vom Eigentümer revidierbar)

1. Entscheid REVISE; kein Kapital; LIVE im Referenzcode blockiert.
2. Design B (Credal-Netz) als Forschungsmaschine, Design A (LP) als Zertifikatsschicht, Design C als verpflichtende Baseline; Auswahl per Ablation nach 150 aufgelösten Ereignissen.
3. Fusionsschwellen vorregistriert: Spannweite 0,30, Breite 0,35, Jev-Komplement-Gap 0,15, Jev-Primärevidenz 0,60, Relevanz 0,50, Schrumpfung 0,30, Mindesthistorie 20.
4. E-Prozess: α = 0,05, λ_max = 0,5, GRAPA-artiges prädiktierbares λ, Ablehnung über laufendes Maximum.
5. Pilot-Whitelist Stock, Etf, Bond, MutualFund; Caps: brutto 100 Prozent, je Position 20 Prozent, maximal 8 Positionen, Cash-Floor 10 Prozent, Worst-Case-Verlust je Position ≤ 15 Prozent des Pilotkapitals, Umschlagsgrenze 24 Round-Trips/Jahr.
6. Seltene Wahrscheinlichkeiten (< 5 Prozent) werden nie direkt elizitiert; abgeleitet durch Zerlegung, geflort durch Kohortenbasisraten; zwei Jahre nur Diskrimination.
7. Primärmetrik im ersten Jahr ist Prognose-Skill, nicht P&L; H2 läuft als 5-Jahres-Schattenexperiment.
8. Vier Prinzipale (Researcher, Promoter, Executor, Eigentümer) mit getrennten Konten und Secrets.
9. Risk-off beschränkt sich auf Drosselung neuer Käufe und Cash-Floor; nie Zwangsliquidation thesenintakter Positionen; Verkauf nur bei Thesenbruch.
13. Horizonterweiterung: Forschung ist ab Tag eins klassenübergreifend; Umsetzung in Positionen gestaffelt über eine Erweiterungsleiter mit fünf Abnahmekriterien je Klasse (Instrumentenmodell, Lean-Verlustschranke, Daten, Broker-Nachweis, Kapitalschwelle); Methodenscanner hält KI- und Finanzforschung aktuell (`02/05`, Eigentümervorgabe 16.10.2026).
12. 25-Jahres-Horizont: unveränderlicher Kern mit Versionsnummer, evolvierbare Hülle über Proposer/Promoter, jedes neue Modell über Schatten, Nachweis, Promotion, Ruhestand; α-Budget je Jahr; automatischer, verankerter Jahresbericht; jährlicher Wiederherstellungstest; Totmannschalter (`02/04`, Eigentümervorgabe 16.10.2026).
11. Der Nordstern 100x in zehn Jahren bleibt bestehen; Gewinn in jedem Kalenderjahr und Indexsieg in jedem Einzeljahr sind keine Ziele, weil sie dem Nordstern widersprechen; Etappenziele gemäss `04/04` (Eigentümerentscheid 16.10.2026).
10. Betrieb ausschliesslich über die bestehenden Abonnements plus Jev; zusätzliche Kosten im ersten Jahr 0 USD geplant; OpenAI als eigentümergestarteter täglicher Batch; jede Abweichung ist ein Eigentümerentscheid mit Ledgereintrag (Eigentümervorgabe 16.10.2026).

## B. Reihenfolge nach Abhängigkeit (nicht nach Attraktivität)

| Priorität | Baustein | Warum zuerst |
|---|---|---|
| 1 | Verankerter Ledger + Prognoseregister | ohne sie ist nichts, was danach kommt, bewertbar |
| 2 | Saxo SIM read-only | klärt Q1, Q3, Q6, Q7 früh und billig |
| 3 | Ingest-Log + Jev-Triage | erzeugt die ersten registrierbaren Ereignisse; klärt Q8 |
| 4 | Design-C-Baseline | ohne Baseline kein H0-Test |
| 5 | Drei-Modell-Adapter + Fusion | erst jetzt entsteht die eigentliche Forschungsmaschine; klärt Q2 |
| 6 | E-Prozess-Monitore, Kalibrierkarten, Ablationen | Auswertung |
| 7 | Credal-Netz (Design B), Hazard-Modell | nach ersten 100 Ereignissen, nicht vorher |
| 8 | Allokator, Zertifikate, SIM-Precheck | erst wenn Prognosen existieren, die es zu allokieren gibt |
| 9 | Promoter-Skript, Selbstverbesserung | erst wenn es etwas zu verbessern gibt und Holdouts eingefroren sind |
| 10 | SIM-Execution, Shadow-Live | nach Gate-Evidenz |

## C. Was ausdrücklich nicht gebaut wird, bevor die Gegenprüfung abgeschlossen ist

- Kein Repository, kein Produktionscode, keine Adapter gegen Anbieter-APIs.
- Keine Order-Platzierungsfunktion (auch nicht in SIM).
- Kein LIVE-Pfad in irgendeiner Form.
- Keine Optimierung oder Kalibrierung gegen Live-Daten des Kontos.
- Keine Derivate, keine Margin, kein Short, auch nicht "nur zum Testen".

## D. Was von v0.1 bewusst beibehalten wird

Die Grundidee des PCCB als typisiertes, versioniertes Forschungsobjekt; die Trennung "Forscher sind ersetzbar, das Daten- und Testsystem ist die Institution"; die Gate-Sequenz RESEARCH_ONLY bis LIVE_CAPPED_1000; die Prompts der drei Forscher als Runde-1-Instruktionen (versioniert); die Ablehnung von Ticker-first-Research; der Wald-Test als Pflichtbestandteil; das Zwei-Zustands-Modell als pädagogisches Beispiel, nicht als Allokator.

## E. Zwei Fragen, die nur der Eigentümer beantworten kann

1. Beantwortet am 16.10.2026: Betrieb nur über bestehende Abonnements plus Jev, so wenig Kosten wie möglich. Damit ist das Volumen durch Kontingente begrenzt (5 bis 10 Runden/Tag) und der OpenAI-Anteil läuft als täglicher Handgriff.
2. Ist eine tägliche Anmeldung bei Saxo akzeptabel, falls Q1 negativ ausfällt? Die Antwort bestimmt, ob "hands-off" ein Ziel bleibt oder zu "ein Klick pro Tag" wird. Da OpenAI ohnehin einen täglichen Handgriff braucht, läge ein Saxo-Login im selben Ritual.
