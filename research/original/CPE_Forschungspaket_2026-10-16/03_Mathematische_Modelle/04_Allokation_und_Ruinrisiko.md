# 04 Allokation und Ruinrisiko

## 1. Audit des binären Kelly-Modells aus v0.1

Zweizustandsmodell: Anteil w des Vermögens, Erfolgsmultiplikator up, Misserfolgsmultiplikator down, Erfolgswahrscheinlichkeit p. Erwartetes Log-Wachstum

g(w) = p · ln(1 + w(up − 1)) + (1 − p) · ln(1 + w(down − 1)).

Mit a = up − 1 > 0 und b = down − 1 < 0 liefert die Bedingung erster Ordnung

w* = −(p a + (1 − p) b) / (a b).

Nachgerechnet (F6): up = 10, down = 0,2, p = 0,10 ⇒ w* = 0,025 (Grid-Argmax 0,025); p = 0,12 ⇒ w* = 0,0522; positives arithmetisches Erwartungsmultiple genau dann, wenn 10p + 0,2(1 − p) > 1 ⇔ p > 4/49 ≈ 8,16 Prozent (Lean-kompiliert). Vollinvestition bei p = 0,12 ergibt E[ln] = 0,12 ln 10 + 0,88 ln 0,2 ≈ −1,14: katastrophal für Compounding, obwohl das arithmetische Multiple 1,376 beträgt. Daraus folgt die zentrale Lehre des RFC: die Möglichkeit von 10x allein ist für die Positionsgrösse irrelevant.

Robustheit: Da g in p linear ist und ln(1 + wa) ≥ ln(1 + wb), ist das Minimum über [p_low, p_high] bei p_low (Lean `growth_min_at_lower_bound`). Die Verwendung von p_low ist also korrekt; p_high bleibt in v0.1 ungenutzt und könnte für eine Max-Regret-Diagnose dienen.

Fehler in v0.1: `lower_growth <= fixed_cost_fraction_of_portfolio` vergleicht Log-Wachstum mit einem Kostenanteil c. Korrekt ist der Vergleich mit −ln(1 − c) (Log-Kosten der Zahlung eines Anteils c). Für kleine c gleich bis zur ersten Ordnung, für c nahe 1 falsch; c ≥ 1 war nicht abgefangen. Im Referenzcode behoben (Test `test_fixed_cost_uses_log_units`).

Was das Modell nicht kann: mehrere Positionen, Korrelation der Tails, Instrumente, Pfadabhängigkeit, Steuern, Gebühren jenseits eines Fixanteils, Optionsgriechen, Margin, Liquidation, veraltete Daten.

## 2. Szenariobasierte robuste Allokation (Referenzcode `allocation.py`)

Modell: K gemeinsame Szenarien, N voll bezahlte Instrumente, R[k, i] = Gesamtrenditemultiplikator minus 1 von Instrument i in Szenario k (−1 = Totalverlust), nach Kosten, FX und Steuern durch den Aufrufer. Die Unsicherheit über Szenariowahrscheinlichkeiten ist eine endliche Credal-Menge Q = {q_1, …, q_J} (Eckpunkte des machbaren Polytops aus dem Kohärenz-LP oder handspezifizierte Stressvektoren).

Zielfunktion: max_w min_{q ∈ Q} Σ_k q_k ln(1 + R_k · w)
Nebenbedingungen: w ≥ 0; Σ w ≤ gross_cap; w_i ≤ cap_i; Worst-Case-Verlust −min_k R_k · w ≤ max_loss (hart, pfadfrei). Danach fraktionales Kelly w ← f · w mit f = 0,5.

Lösung in Epigraphform (maximiere t unter t ≤ Wachstum(w, q_j) für alle j) mit SLSQP. Der Referenztest reproduziert den Binärfall (w = 0,025 bei Q = {p = 0,10, p = 0,15}) und prüft, dass max_loss und Caps bindend respektiert werden.

Warum das weiterhin ein Spielzeug ist: Szenarien sind diskret; die gemeinsame Abhängigkeit muss vom Aufrufer in das Szenarioset kodiert werden (Makroregime × Thesenausgang); kein Pfad innerhalb des Horizonts, keine Margin, keine Liquidation, keine Optionsausübung, kein Rebalancing. Für einen 1'000-Dollar-Pilot mit voll bezahlten Instrumenten ist es ausreichend; für Derivate nicht, weshalb diese im Pilot ausgeschlossen sind.

HYPOTHESE (keine Theorie): fraktionales robustes Kelly auf kalibrierten Credal-Inputs vermeidet Ruin. Ruin bleibt möglich, wenn die Inputs fehlkalibriert sind.

## 3. Herleitung unter Parameterunsicherheit, Kosten und Tails

- Parameterunsicherheit in p: bereits durch die Intervallgrenze abgedeckt; ein zusätzlicher Schrumpffaktor würde doppelt zählen. Fraktionales Kelly (f = 0,5) adressiert Modellunsicherheit jenseits des Intervalls (Modellfehlspezifikation, nicht nur Parameterfehler).
- Transaktionskosten: gehen in R_k ein (Kommission, Spread aus Precheck `Cost`, FX-Umrechnung), nicht als nachträglicher Abzug.
- Korrelierte Tails: ausschliesslich über das Szenarioset; ein Szenario "alle Thesen scheitern gleichzeitig" (Finanzierungsregime bricht) MUSS im Set enthalten sein, mit Gewicht aus dem Hazard-Modell (`03/06`).
- Basisratenunsicherheit: Q enthält den Eckpunkt mit der Design-C-Basisrate als Untergrenze.
- Veraltete Daten, Liquidation, Margin, Optionsausübung: Gate-Regeln (`02/02` Abschnitt 4), nicht der Allokator.
- Pfadabhängige Auszahlungen: nicht modelliert; Instrumente mit Pfadabhängigkeit sind im Pilot ausgeschlossen.
- Stoppzeiten: keine preisbasierten Stopps; Ausstieg nur bei Thesenbruch oder Hazard-Politik (`03/06`).

## 4. Pilot-Risikolimits (LIVE_CAPPED_1000, nur falls je aktiviert)

- Instrumente: Stock, Etf, Bond, MutualFund, voll bezahlt, Handelbarkeit aus `/ref`-Readback; keine CFDs, FX, Optionen, Futures, kein Short.
- Brutto-Exposure ≤ 100 Prozent des Pilotkapitals; Positionscap 20 Prozent (≤ 200 USD); Mindestticket so, dass Kommission ≤ 1 Prozent des Tickets (Kommissionsschema kontoabhängig, Q6); maximal 8 Positionen; Cash-Floor 10 Prozent.
- Worst-Case-Verlust je Position ≤ 15 Prozent des Pilotkapitals (Annahme R_k ≥ −0,75 für voll bezahlte Aktien; Konkursszenario explizit).
- Umschlag: Ziel Median-Haltedauer > 12 Monate; harte Obergrenze 24 Round-Trips pro Jahr (Schweizer Einstufungsrisiko als gewerbsmässiger Wertschriftenhändler, `06/02`).
- Risikoquellen statt Ticker diversifizieren: ≤ 40 Prozent des Exposures teilen denselben Erstordnungsmechanismus; ≤ 50 Prozent in einer Währung ausser CHF/USD.
- Datenfrische: kein Precheck/keine Order bei Quote-Alter > 15 Minuten oder Gate-Heartbeat > 5 Minuten.

## 5. Ruinrisiko-Berichterstattung

Monatliche Monte-Carlo-Simulation über die Szenariosets: P(Drawdown > 50 Prozent innerhalb 5 Jahren), Expected Shortfall 5 Prozent, P(10x in 10 Jahren) unter dem Modell. Berichtet als Modellausgaben mit Provenienz der Inputs, nie als Zusage.

## 6. Die Zielarithmetik

100^(1/10) − 1 = 58,49 Prozent CAGR bei Vollinvestition von 4'000 USD ab Tag null. Mit 1'000 USD im ersten Jahr und 3'000 USD erst nach Evidenz ist die erforderliche Rendite auf dem eingesetzten Kapital höher (abhängig vom Einsatzzeitpunkt der 3'000 USD). Zur Einordnung, als Allgemeinwissen ohne Quelle in diesem Paket: langjährig dokumentierte öffentliche Rekorde liegen bei rund 20 bis 30 Prozent CAGR; höhere Raten sind kapazitätsbeschränkt und nicht öffentlich replizierbar. Der Zielwert ist ein Tail-Anspruch; der Vergleich mit einem Always-invested-Benchmark ist obligatorisch.
