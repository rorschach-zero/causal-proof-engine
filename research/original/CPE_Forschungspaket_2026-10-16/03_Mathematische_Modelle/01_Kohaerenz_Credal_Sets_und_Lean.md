# 01 Kohärenz, Credal Sets und Lean-Zertifikate

## 1. Das Kohärenzproblem (Design A, wie in v0.1 implementiert)

Gegeben n binäre Ereignisse E_1, …, E_n, Weltzustände Ω = {0,1}^n (2^n Welten), Intervalle [l_i, u_i] je Ereignis und logische Constraints der Form A ⇒ B (Welten mit A = 1 und B = 0 werden entfernt). Die Credal-Menge ist

P_t = { q : Ω → ℝ_{≥0} | Σ_ω q(ω) = 1, l_i ≤ Σ_{ω ∈ E_i} q(ω) ≤ u_i ∀ i, q(ω) = 0 für verbotene ω }.

Machbarkeit und die Schranken für ein Zielereignis T ergeben sich aus zwei linearen Programmen:

min / max Σ_{ω ∈ T} q(ω) unter den obigen Nebenbedingungen.

Das ist die klassische probabilistische Logik (Nilsson 1986) beziehungsweise die Theorie imprecise probabilities (Walley 1991). v0.1 implementiert sie korrekt mit HiGHS; die Tests `test_joint_coherence_detects_logical_contradiction` und `test_three_event_chain_bounds` bestätigen Widerspruchserkennung und Monotonie entlang Implikationsketten.

Eigenschaften und Grenzen:
- Komplexität O(2^n) Variablen; 14 Ereignisse = 16'384 Welten in 0,34 s, 20 Ereignisse wären 1 Mio. Welten. Der Guard n ≤ 14 fehlte in `event_probability_bounds` (behoben im Referenzcode).
- Die LP-Lösung mit Nullzielfunktion ist ein beliebiger Eckpunkt der Credal-Menge (Befund F8). Stromabwärts DARF nur die Intervallausgabe verwendet werden.
- Nur Marginalintervalle und Implikationen: bedingte Information (P(B | A)) geht nicht ein. Bei vielen lose beschränkten Ereignissen werden die Zielintervalle vakuös ([0, u] oder [l, 1]).
- Die Kohärenz ist bedingt auf die behaupteten Constraints; sie sagt nichts über deren empirische Wahrheit.

## 2. Referenzverteilung (nicht implementiert, als Schätzer zu kennzeichnen)

Wird für Szenariogewichte eine einzelne Verteilung benötigt, ist sie als Schätzer auszuweisen, nicht als "die" Verteilung. Zwei Kandidaten:

- Max-Entropie: q* = argmax_{q ∈ P_t} −Σ q(ω) log q(ω). Konvex, eindeutig, bevorzugt keine Welt ohne Grund.
- Min-KL zu einer Prior π (Design-C-Basisraten): q* = argmin_{q ∈ P_t} Σ q(ω) log(q(ω)/π(ω)).

Beide sind konvexe Programme über der Credal-Menge; Lösung mit einem Interior-Point-Verfahren. Der Allokator verwendet standardmässig die Eckpunktmenge der Credal-Menge (Max-Min), die Referenzverteilung nur zur Berichterstattung.

## 3. Design B: Credal-Netz für den Forschungsgraphen

Knoten = EventSpecs, Kanten = Mechanismen. Jeder Forscher liefert bedingte Intervalle P(child | parent-Konfiguration) ∈ [l, u] nur für Konfigurationen, die er begründen kann; sonst Abstention. Inferenz: M = 2'000 Ziehungen, in jeder Ziehung werden alle CPT-Einträge gleichverteilt im Intervall gezogen (nach Fusion der drei Forscher je Kante), vorwärts propagiert; das Zielintervall ist das [5., 95.]-Perzentil über Ziehungen plus die Hülle (Min/Max). Komplexität O(M · Kanten), unabhängig von 2^n.

Was Design B nicht leistet: eine Garantie, dass die Hülle die exakte Credal-Schranke erreicht (die gleichverteilte Ziehung ist eine Heuristik; exakte Credal-Netz-Inferenz ist NP-hart, Verfahren wie 2U existieren für polytree-artige Strukturen). Für die Entscheidungsprojektion (≤ 14 Knoten) wird darum zusätzlich das exakte LP aus Abschnitt 1 gerechnet; stimmen beide nicht überein, gilt das LP und die Abweichung wird protokolliert.

HYPOTHESE: Design B ist auf Graphen mit > 14 Knoten besser kalibriert als Design A. Test durch Ablation nach 150 aufgelösten Ereignissen (`04/03`).

## 4. Verbot der Multiplikation von Marginalen

Für eine Kette E ⇒ D ⇒ C gilt nur P(E) ≤ P(D) ≤ P(C). Die Multiplikation P(E) = P(E|D) · P(D|C) · P(C) setzt Unabhängigkeit voraus, die in Investmentketten typischerweise verletzt ist (gemeinsame Treiber: Finanzierungsregime, Management, Nachfrage). Sowohl das LP als auch das Credal-Netz vermeiden Multiplikation per Konstruktion; die Korrelation zwischen den Fehlern der drei Modelle wird in der Fusionsschicht (`03/03`) behandelt, nicht hier.

## 5. Lean-Zertifikate: formale Semantik

Ein kompiliertes Lean-Theorem beweist, dass die **Konklusion aus den Hypothesen folgt**. Es beweist nie, dass eine Hypothese (ein Wahrscheinlichkeitsintervall, ein Auszahlungsmultiplikator, eine Korrelation) in der Welt wahr ist. Darum sind Zertifikate immer in der Form "unter den Annahmen H_1, …, H_k gilt C" zu lesen, und jedes Zertifikat listet H_1, …, H_k explizit.

Kompiliert am 16.10.2026 auf Lean `leanprover/lean4:v4.35.0`, Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`, alle nur mit den Standardaxiomen `propext`, `Classical.choice`, `Quot.sound`:

Aus v0.1 (`BetThreshold.lean`, trivial):
- `positive_expected_multiple_iff`: 10p + (1−p)/5 > 1 ⇔ p > 4/49.
- `long_call_loss_at_most_premium`: Prämie − Auszahlung ≤ Prämie, falls Auszahlung ≥ 0.
- `purchased_call_budget`: Prämie ≤ Budget ⇒ Prämie − Auszahlung ≤ Budget.

Neu (`RiskBudget.lean`), die Lemmata, auf die Allokator, LP und E-Prozess tatsächlich angewiesen sind:
- `growth_min_at_lower_bound`: für p_l ≤ p und l_f ≤ l_s gilt growthLin(p_l) ≤ growthLin(p). Rechtfertigt, dass `core.py` nur `p_success_low` verwendet.
- `expected_multiple_mono`: arithmetisches Erwartungsmultiple ist monoton in p bei up ≥ down.
- `fully_paid_worst_loss_le_cap`: 0 ≤ w ≤ c, 0 ≤ down ≤ 1 ⇒ w(1 − down) ≤ c.
- `portfolio_worst_loss_le_sum_caps` und `portfolio_worst_loss_le_budget`: Summe der Worst-Case-Verluste ≤ Summe der Caps ≤ Budget.
- `implication_prob_le`: A ⇒ B und q ≥ 0 ⇒ Σ_{A} q ≤ Σ_{B} q (die LP-Monotonie, formal).
- `eprocess_factor_nonneg`: 0 ≤ λ ≤ 1, −1 ≤ x ≤ 1 ⇒ 1 + λx ≥ 0 (Nichtnegativität, die Ville braucht).

Negativkontrolle: ein Theorem mit falscher Schwelle (1/10 statt 4/49) scheitert mit `linarith failed`. Damit ist belegt, dass die Toolchain prüft und nicht nur durchwinkt.

Was Lean im CPE nie leisten wird: beweisen, dass ein Management Ziele erreicht, dass ein Intervall die wahre Wahrscheinlichkeit enthält, oder dass eine Strategie Gewinn macht. H4 ist deshalb keine Hypothese, sondern eine Aussage über das Modell: ein zertifizierter Orderplan hat null Logik- und Budgetverletzungen im zertifizierten Modell.
