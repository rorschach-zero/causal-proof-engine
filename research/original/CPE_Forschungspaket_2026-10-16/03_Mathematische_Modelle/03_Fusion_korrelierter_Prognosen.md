# 03 Fusion korrelierter Prognosen und Abstention

## 1. Warum keine Mehrheitsentscheidung

Drei Modelle, die auf ähnlichen Korpora trainiert sind, machen korrelierte Fehler. Eine 2-von-3-Mehrheit behandelt sie als drei unabhängige Zeugen und überschätzt die Evidenz. Konsens ist keine Evidenz; ein Konsens aus denselben Gründen ist eine Stimme.

## 2. Minimum-Varianz-Pooling

Seien e_i = p_i − y die standardisierten Fehler der Modelle i = 1..m über die aufgelösten Ereignisse, R die daraus geschätzte Fehlerkorrelationsmatrix, geschrumpft zur Identität: R_δ = (1 − δ)R̂ + δI mit δ = 0,30 (Ledoit-Wolf-artige Schrumpfung, Konstante vorregistriert). Die Gewichte des varianzminimalen unverzerrten linearen Pools sind

w = R_δ⁻¹ 1 / (1ᵀ R_δ⁻¹ 1).

Treten negative oder nicht endliche Gewichte auf (etwa bei nahezu kollinearen Fehlern), fällt die Fusion auf Gleichgewichte zurück und setzt ein Flag; negative Gewichte würden ein Modell "gegen sich selbst" verwenden, was mit Intervallprognosen nicht interpretierbar ist. Unter 20 aufgelösten Ereignissen gelten Gleichgewichte.

Effektive Modellzahl: n_eff = (Σ w_i)² / (wᵀ R_δ w). Bei R = I und Gleichgewichten gilt n_eff = 3; bei R = 11ᵀ (vollständig korreliert) n_eff = 1. Der Referenztest `test_correlated_models_do_not_count_three_times` zeigt mit zwei fast identischen und einem unabhängigen Modell n_eff < 2,5 und ein höheres Gewicht für das unabhängige Modell. n_eff wird monatlich berichtet; bleibt es dauerhaft unter 1,5, ist die Unabhängigkeitsprämisse des Komitees falsch (siehe Annahmen in `06/03`).

## 3. Fusion von Intervallen

Das fusionierte Intervall ist die Konvexkombination der Eingangsintervalle: [Σ w_i l_i, Σ w_i u_i]. Das ist eine konservative, gültige Pooling-Regel für Credal-Mengen (die Konvexkombination von Mengen, die die wahre Wahrscheinlichkeit enthalten, enthält sie weiterhin, sofern die Gewichte nichtnegativ sind). Uneinigkeit D = max_i mid_i − min_i mid_i.

## 4. Entscheidungslogik (vorregistrierte Konstanten)

| Bedingung | Entscheid |
|---|---|
| fehlendes Modell oder fehlender Jev-Datensatz | RE_RESEARCH (nie stilles 2-von-3) |
| Jev-Komplement-Gap > 0,15 | RE_RESEARCH ("Jev inkohärent auf diesem Item") |
| Jev p(datierte Primärquelle) < 0,60 oder p(Relevanz) < 0,50 | RE_RESEARCH |
| ein Modell abstinent | ABSTAIN, Item in Runde 2 |
| D > 0,30 | ABSTAIN |
| fusionierte Breite > 0,35 | ABSTAIN |
| sonst | FORECAST mit Gewichten, D, n_eff, Gründen |

Runde 2 (adversariale Gegenprüfung) sieht die Runde-1-Outputs der anderen Modelle, erzeugt aber neue Prognose-IDs; Runde-1-Prognosen werden nie editiert, damit die Unabhängigkeit von Runde 1 messbar bleibt.

## 5. Strategische Abstention

Ein Modell könnte Abstention nutzen, um nur bei leichten Items bewertet zu werden. Gegenmassnahmen: Abstentionsrate je Modell wird berichtet; der Brier der Fusion auf Items, bei denen ein Modell abstinent war, wird separat ausgewiesen; ein Modell mit Abstentionsrate > 40 Prozent über 100 Items wird im Promoter-Bericht markiert.

## 6. HYPOTHESE

Diese Fusion hat auf prospektiv registrierten Ereignissen einen niedrigeren Brier als das beste Einzelmodell und als der naive Mittelwert. Falsifikator: `04/02` H1; Ablationsarme "single LLM" und "naiv gepoolt" in `04/03`.
