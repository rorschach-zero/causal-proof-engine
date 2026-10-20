# 04 Langlebigkeit und Evolution über 25 Jahre

Eigentümervorgabe vom 16.10.2026: Das Projekt muss sich über die nächsten 25 Jahre ständig verbessern und selbständig weiterentwickeln; neue, bessere Modelle werden laufend eingebaut; alles wird wissenschaftlich erfasst und bewiesen. Dieses Kapitel legt fest, was dafür unveränderlich sein muss, was sich frei entwickeln darf, und was "bewiesen" über 25 Jahre ehrlich bedeuten kann.

## 1. Das Prinzip: Modelle sind Gäste, die Institution ist das Datensystem

Über 25 Jahre wird jedes Modell, das heute existiert, ersetzt, vermutlich mehrfach; Anbieter verschwinden, APIs ändern sich, Abos werden umgebaut. Was bleibt, ist das, was das System über die Welt und über sich selbst gelernt hat: das Prognoseregister, der verankerte Ledger, die aufgelösten Ereignisse, die Kalibrierhistorie je Prognostiker, die eingefrorenen Holdouts, die Zertifikate. Das Design folgt deshalb der Regel aus dem ursprünglichen RFC, hier verschärft: **Forscher sind ersetzbar, das Daten- und Testsystem ist die Institution.**

## 2. Unveränderlicher Kern und evolvierbare Hülle

| Kern (nur Eigentümer, mit externem Review, jede Änderung als "Verfassungsänderung" im Ledger) | Hülle (darf sich autonom entwickeln, über Proposer/Promoter) |
|---|---|
| Ledger-Format und Verankerung | Prompts, Rollenbeschreibungen, Fragetemplates |
| Prognoseregister-Schema und Bewertungsregeln | Feature-Extraktoren, Parser, Quellenfamilien |
| Evaluationsprotokoll (Proper Scores, E-Prozess, Holdout-Regeln, α-Budget) | Graph-Templates, Mechanismusbibliothek, Credal-Netz-Struktur |
| Gate-Zustandsmaschine und Promotionsregeln | Kalibrierkarten, Fusionsgewichte (innerhalb vorregistrierter Schwellen) |
| Risikolimits und Instrumenten-Whitelist | Exit-Regeln, Hazard-Modell-Features (nicht die Aktionen) |
| Prinzipaltrennung und Secrets-Regeln | Modellauswahl je Rolle, Degradationsleiter |
| Die Pflicht: drei unabhängige Modelle plus typisierte Triage | Welche konkreten Modelle die Plätze besetzen |

Der Kern hat eine Versionsnummer; jede Kernänderung dokumentiert, welche historischen Auswertungen dadurch nicht mehr vergleichbar sind, und friert die alte Auswertung als Artefakt ein.

## 3. Modellwechsel als Standardvorgang, nicht als Ausnahme

Jedes neue Modell (auch ein neues Claude, ein neues Jev, ein ganz neuer Anbieter) durchläuft denselben Weg:

1. **Schatten**: Es prognostiziert parallel, ohne Gewicht in der Fusion, auf dieselben registrierten Ereignisse. Es beginnt mit Kalibrierhistorie null; nichts wird vom Vorgänger geerbt.
2. **Nachweis**: Committeter E-Prozess gegen den Amtsinhaber derselben Rolle auf prospektiven Ereignissen; Mindestzahl aufgelöster Ereignisse (vorregistriert, z. B. 150) und E-Wert ≥ 1/α.
3. **Promotion**: Durch den Promoter auf eingefrorenen Holdouts, nie durch den Forscher selbst. Das alte Modell bleibt einen weiteren Zyklus als Ablationsarm.
4. **Ruhestand**: Ein Modell wird abgesetzt, wenn der umgekehrte E-Prozess (Amtsinhaber gegen besten Herausforderer) seine Unterlegenheit zeigt oder der Anbieter es abschaltet. Seine Prognosen bleiben für immer im Register, mit Modellname und Version.

Die Rolle "typisierte Triage" (heute Jev) ist als abstrakter Platz definiert. Verschwindet TypeSafe, besetzt ein anderes typisiertes oder ein lokal betriebenes Modell den Platz, nach demselben Nachweisweg; der Platz bleibt Pflicht, das Produkt nicht.

Modellwissensstichtage werden je Prognose festgehalten; ein neues Modell, dessen Trainingsdaten die Auflösung alter Ereignisse enthalten, wird auf diesen Ereignissen nicht bewertet (Kontaminationsregel aus `04/03`).

## 4. Wissenschaftliche Erfassung über 25 Jahre

- **Vorregistrierung als Dauerzustand**: jede Behauptung, jedes Artefakt, jede Schwelle wird vor der Entblindung im Ledger festgelegt. Nachträgliche Umdeutung ist technisch unmöglich (Anker) und prozessual verboten.
- **α-Budget**: Über 25 Jahre werden Tausende Artefakte getestet. Ohne Budget sammeln sich Scheinbefunde an. Jedes Jahr erhält ein festes Budget an primären Tests (z. B. α = 0,05 je Artefakt bei maximal 20 Artefakten im Jahr); exploratorische Tests werden gezählt und berichtet, führen aber nie zu Promotion. Alternativ FDR-Kontrolle über die Jahresartefakte; die Wahl ist eine Kernentscheidung.
- **Anytime-gültige Statistik**: E-Prozesse erlauben beliebig langes Weiterbeobachten ohne Gültigkeitsverlust; dasselbe Instrument überwacht auch Verschlechterung (umgekehrter E-Prozess), sodass ein System, das 2030 gut war und 2040 nicht mehr ist, entdeckt wird.
- **Jahresbericht, automatisch**: Jedes Jahr erzeugt das System einen Bericht aus dem Ledger: registrierte und aufgelöste Ereignisse, Kalibrierung je Modell, E-Werte, Ablationen, Promotionen und Ablehnungen, Negativergebnisse, Kosten, Gate-Historie, Schattenbuch gegen Benchmarks, Etappenzielstatus (`04/04`). Der Bericht wird mit seinem Hash verankert. Negativergebnisse werden nicht weggelassen.
- **Reproduzierbarkeit**: jede Auswertung ist aus Ledger, Register und gepinnten Artefakten (Code-Hash, Modellname, Prompt-Hash, Lean-Toolchain) neu berechenbar. Umgebungen werden als Container oder Lockfiles festgehalten; alle Formate sind offen (JSONL, Parquet, Markdown), kein proprietäres Datenbankformat ohne Export.

## 5. Was "bewiesen" bedeuten kann, und was nicht

Drei Arten von Nachweis, strikt getrennt und so benannt:

1. **Formal bewiesen** (Lean): nur bedingte Mathematik, "aus Annahmen folgt Konklusion". Gilt für Rechenregeln des Allokators, Kohärenzschranken, Budgetgrenzen, E-Prozess-Faktoren. Nie für Marktaussagen. Bei Toolchain-Wechsel werden alle Beweise neu kompiliert; ein Beweis, der nicht mehr kompiliert, verliert seinen Status, bis er repariert ist.
2. **Statistisch nachgewiesen** (E-Prozesse, Proper Scores): Aussagen der Form "unter der Nullhypothese wäre das, was wir sehen, mit Wahrscheinlichkeit höchstens α aufgetreten". Gültig für Prognose-Skill und für Verbesserungen; nie eine Garantie für die Zukunft.
3. **Empirisch belegt** (Track Record): Schattenbuch und reales Buch gegen Benchmarks mit Konfidenzintervallen. Über 25 Jahre ist das der stärkste verfügbare Beleg, aber Evidenz, kein Beweis; Regimewechsel können jeden Track Record entwerten.

Das System darf nie "bewiesen" sagen, wo es "belegt" meint. Diese Sprachregel ist Teil des Kerns.

## 6. Selbständige Weiterentwicklung: Grenzen der Autonomie

Die Schleife darf alles in der Hülle vorschlagen und über den Promoter einführen, einschliesslich Vorschläge, die die Schleife selbst betreffen (neue Suchstrategien, neue Artefakttypen). Sie darf nie: den Kern ändern, ihre eigenen Holdouts erzeugen oder einsehen, ihre eigene Promotion ausführen, Risikolimits oder Gates berühren, Live-P&L als Belohnung verwenden, oder eine Kernänderung dem Eigentümer als Hüllenänderung unterschieben (der Promoter prüft den Änderungsumfang gegen eine Liste der Kernartefakte und lehnt ab).

Vorschläge zur Kernänderung sind erlaubt, aber nur als Text an den Eigentümer, mit vorregistrierter Begründung; sie werden nie automatisch umgesetzt.

## 7. Kontinuität über ein Vierteljahrhundert

- **Anbieter verschwinden**: Jeder Anbieter ist über einen Adapter angebunden; das Fehlen eines Anbieters bremst die Forschung und friert Orders ein, zerstört aber nichts. Mindestens ein lokal betreibbares Modell je Rolle wird als Notbesetzung gepflegt (RTX 5090 heute, Nachfolger später).
- **Formate und Code altern**: Jährlicher "Wiederherstellungstest": Ledger, Register und ein Jahresbericht werden auf einer frischen Maschine aus den Archiven neu aufgebaut. Scheitert er, ist das ein P0.
- **Der Eigentümer**: Runbooks für jeden wiederkehrenden Handgriff (Ankerprüfung, Gate-Promotion, OpenAPI-Login, Terms-Prüfung); Schlüsselhinterlegung für Gate-Secret und Ankerspeicher; ein Totmannschalter, der bei ausbleibender Ankerprüfung über eine festgelegte Frist das Gate auf RESEARCH_ONLY setzt und alle Orders einfriert. Eine Nachfolgeregelung ist in den ersten Jahren nicht nötig, aber vor jeder Kapitalerhöhung über den Piloten hinaus zu dokumentieren.
- **Kosten und Abos**: Die Abo-only-Regel (`02/03`) wird jährlich überprüft; jede Änderung ist ein Eigentümerentscheid mit Ledgereintrag.
- **Regulatorik und Steuern**: jährliche Prüfung der Schweizer Einstufungskriterien (`06/01` Q9) und der Saxo-Bedingungen; Änderungen können Limits im Kern erzwingen.

## 8. Was in den ersten zwölf Monaten davon gebaut wird

Nur das, was die späteren Jahre nicht ausschliesst: offene Formate, Kern-Versionsnummer, Modellname und Version in jeder Prognose, Schattenplatz für Herausforderermodelle im Register, Jahresberichtsgenerator als einfaches Skript, Wiederherstellungstest als Checkliste. Die vollständige Modellwechsel-Pipeline und das α-Budget kommen, sobald das zweite Modell je Rolle existiert.
