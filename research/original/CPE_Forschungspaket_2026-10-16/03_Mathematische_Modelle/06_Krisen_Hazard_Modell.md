# 06 Krisen-Hazard-Modell und Wiedereinstiegspolitik

Ziel aus dem Auftrag: nicht verkaufen, nachdem der Crash bereits stattgefunden hat; ex-ante Risikoreduktion testen statt Crash-Vorhersage behaupten; Wiedereinstiegsbedingungen erhalten.

## 1. Inputs (alle mit Eintrag in der Publikationsverzögerungstabelle)

High-Yield-OAS (Niveau und 3-Monats-Änderung); SLOOS Netto-Verschärfung der Kreditstandards (quartalsweise, rund ein Monat Verzögerung); Zinskurve 3 M bis 10 J; NFCI; VIX-Terminstruktur (1 M / 3 M); Marktbreite (Anteil über 200-Tage-Linie); Funding-Stress (FRA-OIS oder Äquivalent, Quelle zu wählen); Revisionen der Gewinnprognosen; Refinanzierungskalender der Portfoliofirmen. Nur Grössen, die in Echtzeit bekannt sind; ein 200-Tage-Durchschnitt des Aktienindex allein genügt nicht.

## 2. Modell

Bayesian Online Changepoint Detection (Adams und MacKay, arXiv:0710.3742) oder logistisches Hazard-Modell auf das Ereignis "Drawdown > 15 Prozent in den nächsten 6 Monaten", trainiert auf Vintage-Daten (ALFRED). Ausgabe: Hazard-Verteilung mit Kalibrierintervall, kein "CRASH = JA". Purged Walk-Forward mit Embargo; die Kalibrierung des Hazard-Modells wird wie jede andere Prognose im Register geführt.

## 3. Trennung der Fälle

1. Systemisches Risiko steigt **vor** Portfolioverlusten (Hazard hoch, Thesen intakt).
2. Realisierter Drawdown ohne Verschlechterung der Fundamentaldaten.
3. Dauerhafte Thesenbeeinträchtigung, die auch späten Verkauf rechtfertigt.
4. Temporäre Liquiditätspanik mit attraktiver erwarteter Vorwärtsrendite.

## 4. Aktionen mit Hysterese

Eintritt bei oberem Hazard-Band, Austritt bei unterem Band, Mindestverweildauer 30 Tage.

1. Hazard HOCH: neue Käufe auf null drosseln; Cash-Floor auf 30 Prozent anheben, und zwar durch Nicht-Reinvestition und durch Ausstiege, die unabhängig thesenbegründet sind; **nie** Zwangsliquidation thesenintakter Positionen.
2. Thesenbruch (ein registriertes tragendes Ereignis löst mit NEIN auf, oder ein Gegenmechanismus-Ereignis mit JA): Verkauf unabhängig vom Preisregime.
3. Reiner Preis-Drawdown ohne Thesenänderung: keine Aktion; für das "Late-Exit-Audit" protokolliert.
4. Wiedereinstieg: wenn der Hazard das untere Band verlässt, Käufe 60 Tage lang mit halber Geschwindigkeit.

Keine preisbasierten Stopps. Gap-Tests: Szenarien mit Eröffnungslücken von −30 Prozent werden im Allokator-Szenarioset geführt, da Stopps Lücken nicht schützen.

## 5. Kennzahlen und Falsifikator (H6)

Anteil der Schutzaktionen, die nach > 50 Prozent des späteren Drawdowns erfolgen; verpasste Erholung; Fehlalarmkosten; Vergleich mit Always-invested. Backtest-Episoden: 2000 bis 2002, 2007 bis 2009, 2011, 2015/16, Q4 2018, 2020, 2022, plus jede Episode 2024 bis 2026 mit Vintage-Daten. H6 falsifiziert, wenn die Drosselung den maximalen Drawdown nicht um mehr als ihre Fehlalarmkosten reduziert; dann wird die Drosselung entfernt und nur der Thesenbruch-Verkauf bleibt.

## 6. Was nicht vorhergesagt wird

Das Datum des Tiefs, die Grösse eines Drawdowns, idiosynkratische Betrugsfälle. Die Literatur zu taktischem Timing ist schwach; das System behauptet keine Crash-Vorhersage, sondern reduziert Exposure bei erhöhten Vorlaufindikatoren und akzeptiert die durch H6 gemessenen Fehlalarmkosten.
