# 02 E-Prozess und sequentielle Tests

## 1. Die statistische Aussage

Für jedes aufgelöste Ereignis t mit Ergebnis y_t ∈ {0,1}, Baseline-Prognose b_t und Challenger-Prognose c_t sei

X_t = (b_t − y_t)² − (c_t − y_t)² ∈ [−1, 1]

die Brier-Verbesserung des Challengers. Mit einem Einsatz λ_t ∈ [0, λ_max], λ_max < 1, der nur von der Information vor Aufdeckung von y_t abhängt (prädiktierbar), ist

M_n = Π_{t ≤ n} (1 + λ_t X_t)

unter der Nullhypothese H0: E[X_t | F_{t−1}] ≤ 0 für alle t ein nichtnegatives Supermartingal mit M_0 = 1. Villes Ungleichung liefert P(∃ n : M_n ≥ 1/α) ≤ α. Das ist eine Aussage über H0, nicht über künftige Gewinne. Referenz: Ramdas et al., arXiv:2009.03167 (Titel per arXiv-API bestätigt).

Nichtnegativität des Faktors (1 + λX ≥ 0 für λ ≤ 1, X ≥ −1) ist in Lean als `eprocess_factor_nonneg` kompiliert.

## 2. Was die Gültigkeit voraussetzt und was v0.1 verletzt

| Voraussetzung | v0.1 (`core.py:136-165`) | Nachweis |
|---|---|---|
| Prognosen vor dem Ergebnis festgelegt | API nimmt b_t, c_t erst bei Auflösung entgegen; Hindsight-Werte werden akzeptiert | F3 |
| Jedes Ereignis genau einmal | keine Ereignis-ID; dasselbe Ergebnis 20-mal eingespeist ergibt E-Wert 9,6 | F5 |
| λ_t prädiktierbar | statisch (zulässig), aber nicht aus der Historie lernbar; keine Power-Optimierung | Code |
| λ_max < 1 | λ = 1 erlaubt; ein einziger ganz falscher Aufruf setzt M dauerhaft auf 0 | F4 |
| Reihenfolge nach Auflösung bei verzögerten Labels | keine Zeitstempel, keine Ordnung | Code |
| Überlappende Ereignisse | keine Behandlung; formal zulässig, solange die Filtration die Auflösungsreihenfolge abbildet | Analyse |
| α vorregistriert | `reject_null(alpha)` zu jeder Zeit mit jedem α aufrufbar | Code |
| Keine Auswahl des Gewinners unter vielen Tests | keine Zählung von Tests | Code |

## 3. Die Korrektur (CommittedEProcess, Referenzcode)

- `commit(event_id, b, c, committed_at, resolves_not_before)`: Prognosen sind unveränderlich; ein zweiter Commit für dieselbe ID wird abgelehnt; `resolves_not_before` muss strikt nach `committed_at` liegen.
- `resolve(event_id, y, resolved_at)`: nur für committete IDs ("hindsight entry rejected"); Duplikate abgelehnt; Auflösung vor dem deklarierten Fenster abgelehnt; λ_t wird **vor** Einbezug von X_t aus der Liste bisheriger X berechnet.
- λ-Regel (GRAPA-artig, prädiktierbar): λ = clip(m / (v + m²), 0, λ_max) · n/(n + 10) mit m = Mittelwert, v = Stichprobenvarianz der bisherigen X; ohne Historie λ = 0 (M bleibt 1). Die Form ist an Waudby-Smith und Ramdas, "Estimating means of bounded random variables by betting" (arXiv:2010.09686) angelehnt; hier nur die Nichtnegativität als gültigkeitsrelevant behandelt, λ beeinflusst allein die Power. Die exakte Übereinstimmung mit der publizierten Formel ist UNVERIFIZIERT und für die Gültigkeit irrelevant.
- `reject_null(α)` prüft das laufende Maximum von M (nach Ville zulässig); α ist als vorregistrierte Konstante zu führen.
- Verzögerte Labels: Ereignisse werden in Auflösungsreihenfolge einbezogen; da λ_t nur vergangene aufgelöste Ereignisse nutzt, bleibt die Prädiktierbarkeit erhalten.

Monte-Carlo-Nachweis (Test `test_eprocess_false_alarm_rate_under_null`): 1'500 Läufe à 60 Ereignisse, beide Prognostiker gleich verrauscht, α = 0,05; Fehlalarmrate ≤ α + 0,015. Power (Test `test_eprocess_has_power_when_challenger_better`): uninformative Baseline 0,5 gegen kalibrierten Challenger, E-Wert ≥ 20 innerhalb von 300 Ereignissen.

## 4. Verbleibende Einschränkungen (nicht durch Code behebbar)

- Wird das Paar (Baseline, Challenger) erst nach Einsicht in die Ergebnisse gewählt, ist der Test ungültig. Darum: ein primärer E-Prozess je vorregistrierter Behauptung; alle weiteren sind exploratorisch und werden mit ihrer Anzahl berichtet.
- Nicht-stationäre Welt: H0 ist eine bedingte Aussage je Schritt; ein Challenger, der in Regime 1 besser und in Regime 2 schlechter ist, kann M zuerst über 1/α treiben. Die Entscheidung "Verbesserung festgestellt" ist nach Ville trotzdem gültig für die Aussage "nicht überall ≤ 0"; sie ist keine Garantie künftiger Überlegenheit. Darum verlangt der Promoter zusätzlich zeitverschobene Holdouts.
- Brier-Differenz auf Intervallmittelpunkten: Intervallabdeckung ist separat zu berichten (`04/03`).
