# 05 Horizonterweiterung: Assetklassen, Finanzwerkzeuge und Forschungsaktualität

Eigentümervorgabe vom 16.10.2026: Das System muss bei KI- und Finanzforschung auf dem Stand bleiben, seine Finanzwerkzeuge laufend erweitern und seinen Horizont ausdehnen. Aktien sind nur der Start; mit wachsendem Kapital soll es alles abdecken, auch Krypto, Optionen, Metalle, Energie, Öl und weiteres. Dieses Kapitel legt fest, wie das geschieht, ohne die verbindlichen Randbedingungen (Saxo-zuerst, keine Instrumente mit unbegrenztem Verlust im Pilot, keine Autonomie über Risikolimits) zu verletzen.

## 1. Grundsatz: Eine neue Assetklasse wird wie ein neues Modell behandelt

Jede Erweiterung durchläuft denselben vierstufigen Weg wie ein Modellwechsel (`02/04` Abschnitt 3): Schatten, Nachweis, Promotion, gegebenenfalls Ruhestand. Eine Assetklasse ist erst dann "im System", wenn fünf Dinge existieren und vom Promoter abgenommen sind:

1. **Instrumentenmodell**: Auszahlungsprofil, Worst-Case-Verlust, Pfadabhängigkeit, Margin- oder Nachschusspflicht, Ausübungs- und Verfallsregeln, Rollkosten. Für jede Klasse ein eigenes Kapitel im Allokator; das Zweizustands- und Szenariomodell (`03/04`) deckt nur voll bezahlte Instrumente ab.
2. **Zertifikat**: Lean-Lemma, das den Worst-Case-Verlust unter den Modellannahmen beschränkt (für Long-Optionen existiert `long_call_loss_at_most_premium` bereits; für Spreads, Futures und Short-Optionen fehlen sie). Instrumente ohne beweisbare Verlustschranke sind in keiner Phase zulässig.
3. **Daten und Verzögerungstabelle**: Quellenfamilien, Publikationsverzögerungen, Point-in-Time-Verfügbarkeit, Kosten- und Spreadmodell aus Saxo-Precheck.
4. **Broker-Nachweis**: Verfügbarkeit über Saxo OpenAPI für das konkrete Konto (`/ref`-Readback, nicht Retail-Oberfläche), Precheck-Erfolg, SIM-Ausführung über 60 Tage.
5. **Kapitalschwelle**: Mindestkapital, ab dem Gebühren, Ticketgrössen und Diversifikation die Klasse sinnvoll machen; darunter bleibt sie im Schatten.

Der Forschungsteil (Mechanismen, Ereignisse, Prognosen) ist von Anfang an klassenübergreifend; die Forschung darf heute schon über Öl, Metalle oder Krypto nachdenken. Nur die Umsetzung in Positionen ist gestaffelt.

## 2. Erweiterungsleiter (Vorschlag, Reihenfolge nach Risiko und Nachweisbarkeit)

| Stufe | Klasse | Zugangsform zuerst | Besondere Anforderungen | Frühestens |
|---|---|---|---|---|
| 0 | Aktien, ETFs, Anleihen, Fonds (voll bezahlt) | direkt | Pilot-Whitelist | Pilot |
| 1 | Rohstoffe, Metalle, Energie, Öl | ETFs/ETCs, voll bezahlt | Rollkosten und Contango im Instrumentenmodell; physisch vs. synthetisch unterschieden | nach Etappenziel Jahr 1 bis 2 |
| 2 | Krypto | börsennotierte ETPs/ETNs über Saxo, voll bezahlt | Verwahrung bleibt beim Emittenten; Emittenten- und Tracking-Risiko modelliert; Spot-Krypto ausserhalb Saxo verletzt "Saxo-zuerst" und ist nicht vorgesehen, bis der Eigentümer die Randbedingung ausdrücklich ändert | nach Stufe 1 |
| 3 | Optionen mit definiertem Risiko | Long Calls/Puts, Debit-Spreads | Verlust ≤ Prämie beziehungsweise ≤ Spread-Breite, Lean-zertifiziert; Griechen, Zeitwertverfall, Liquidität und Ausübungsregeln im Modell; Saxo `ToOpenClose` | nach Etappenziel Jahr 3 und eigener Risikoreview |
| 4 | Futures, Short-Optionen, CFDs, FX-Margin | nur nach separater Kernänderung | unbegrenzter oder margin-abhängiger Verlust; verletzt heutige Kernregel; erfordert Eigentümerentscheid mit externem Review, Nachschussmodell, Liquidationssimulation | nicht vor Kapital deutlich über Pilotniveau und nie ohne Kernänderung |

Saxo-Verfügbarkeit je Klasse ist UNVERIFIZIERT und kontoabhängig; FX-Optionen sind laut Saxo nicht über OpenAPI handelbar (`02/02`). Welche Krypto-ETPs, Rohstoff-ETCs und Optionsklassen das Konto freischaltet, zeigt erst der `/ref`-Readback (Q6).

## 3. Finanzwerkzeuge laufend erweitern

Finanzwerkzeuge (Bewertungsmodelle, Risikomasse, Kostenmodelle, Hedging-Logik, Exit-Regeln) sind Artefakte der Hülle und werden über Proposer/Promoter eingeführt. Beispiele für spätere Artefakte: Rollkostenmodell für Rohstoff-ETCs, Optionsbewertung mit impliziter Volatilitätsfläche, Emittentenrisiko-Scoring für ETPs, Währungs-Overlay, Liquiditätsmodell für kleine Nebenwerte, Steuer-Lot-Verwaltung. Jedes Werkzeug trägt eine vorregistrierte Behauptung (was es verbessern soll, gemessen woran) und wird im Schatten geprüft, bevor es Entscheidungen beeinflusst.

## 4. Auf dem Stand der KI- und Finanzforschung bleiben

Ein **Methodenscanner** läuft als Teil des Ingests: Er liest definierte Quellen (arXiv-Kategorien für Statistik, maschinelles Lernen, Kausalinferenz und Finanzen; Modellankündigungen der Anbieter; Änderungen an Saxo-OpenAPI und TypeSafe-Dokumentation), triagiert sie mit der typisierten Triage und legt relevante Funde als **Methodenkandidaten** im Register ab: Quelle, Datum, behaupteter Nutzen, betroffene Komponente, vorregistrierte Testidee. Die drei Forscher bewerten Kandidaten in einer monatlichen Methodenrunde; der Promoter führt nur ein, was den Nachweisweg besteht. Neue Modelle laufen über den Modellwechselpfad (`02/04`). Ergebnis ist ein laufender, verankerter **Methodenledger**, aus dem der Jahresbericht ausweist, welche Methoden geprüft, eingeführt, verworfen wurden. Nichts wird eingeführt, weil es neu ist; alles, weil es einen vorregistrierten Test bestanden hat.

## 5. Grenzen

- Keine Klasse der Stufe 4 ohne Kernänderung; der Kern verbietet sie heute.
- Keine Spot-Krypto-Verwahrung oder Drittbörsen, solange "Saxo-zuerst" gilt.
- Keine Klasse ohne Lean-zertifizierte Verlustschranke.
- Erweiterung erhöht nie die Gesamtrisikolimits; sie verteilt Risiko auf mehr Quellen innerhalb derselben Limits.
- Der Nordstern (`04/04`) verlangt Konzentration auf asymmetrische Thesen; Horizonterweiterung dient dem Finden besserer Thesen und Zugangsformen, nicht der Verwässerung in eine Allwetter-Allokation.
