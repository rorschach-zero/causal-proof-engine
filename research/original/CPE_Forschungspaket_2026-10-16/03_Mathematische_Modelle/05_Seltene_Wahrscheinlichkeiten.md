# 05 Seltene Wahrscheinlichkeiten und Kalibrierung unter Selektion

## 1. Das Problem

Die Zielereignisse des Systems (10x in 10 Jahren) haben Basisraten im einstelligen Prozentbereich oder darunter, lösen sich über Jahre auf, und die Kandidaten sind selektiert (das System schaut nur auf Fälle, die es interessant findet). Drei Konsequenzen:

1. Kalibrierung im Bereich p < 5 Prozent braucht Hunderte aufgelöster Ereignisse je Bin. Ein Bin bei 2 Prozent mit 50 Ereignissen erwartet 1 Treffer; die Varianz macht jede Kalibrieraussage wertlos.
2. Selektion verzerrt: die Basisrate "unter den vom System geprüften Kandidaten" ist nicht die Basisrate "im Universum". Kalibrierung ist daher **bedingt auf Selektion** zu messen, mit dem Selektionsprozess als Teil des registrierten Protokolls.
3. LLMs und Jev liefern bei seltenen Ereignissen keine verlässlichen Punktwerte; die unabhängige Jev-Evaluation zeigt Inkohärenz gerade bei Unsicherheit.

## 2. Methodik (verbindlich)

- Es DÜRFEN KEINE Punktwahrscheinlichkeiten unter 0,05 von LLMs oder Jev elizitiert werden.
- Zerlegung in eine Kette bedingter Ereignisse, deren Glieder möglichst in [0,1, 0,9] liegen (Beispiel: Zulassung erteilt → erster Grosskunde qualifiziert → Kapazität in Betrieb → Bruttomarge über Schwelle → Umsatz über Schwelle). Jedes Glied ist ein registrierbares Ereignis mit eigenem Horizont.
- Das Intervall für das seltene Ziel ergibt sich aus dem Credal-Netz beziehungsweise dem LP, nicht durch Multiplikation.
- Die Untergrenze wird mit der Design-C-Kohortenbasisrate geflort: p_low := max(p_low, Basisrate(Kohorte)), wobei die Kohorte durch zum Stichtag beobachtbare Merkmale definiert ist und ihre Grösse n berichtet wird. Ausgabe: `[p_low, p_high, n_cohort]`.
- Bewertung seltener Ziele in den ersten zwei Jahren ausschliesslich über Diskrimination (AUC, Spearman-Rangkorrelation gegen realisierte 3-Jahres-Renditen im Schattenbuch); Kalibrierung erst ab 50 Auflösungen je Bin.
- Keine falsche Präzision: Intervalle werden auf 0,05 gerundet berichtet, wenn n_cohort < 200.

## 3. Kalibrierung der Meilenstein-Ereignisse (das, was in 12 Monaten messbar ist)

Horizonte 1 bis 9 Monate, Ziel 600 registrierte Ereignisse im ersten Jahr (≈ 2 je Arbeitstag) über mindestens 6 Sektoren. Reliability-Diagramme nach Horizont {≤ 1 M, 1 bis 3 M, 3 bis 9 M}, Sektor, Quellenfamilie, Prognostiker; Bins mit ≥ 30 Ereignissen. Isotonische oder Platt-Kalibrierkarten je Prognostiker werden nur auf aufgelösten Ereignissen gelernt und als versionierte Artefakte durch den Promoter freigegeben.

## 4. Modellkorrelation und quellinduzierte Fehler

- Hohe Modellkorrelation: n_eff aus `03/03`; Stresstest durch die Ablationen "−LLM_i".
- Quellinduzierte Fehler: Re-Run mit je einer entfernten Quellenfamilie; treibt eine einzelne Familie > 50 Prozent der Skill, ist das eine Fragilitätsmeldung.
- Narrativdrift: der Ingest speichert Dokumentversionen; Prognosen zitieren die verwendete Version; später korrigierte Quellen werden in der Auswertung markiert.

## 5. Was ausdrücklich nicht behauptet wird

Dass Meilenstein-Skill auf 10x-Diskrimination übertragbar ist, ist eine HYPOTHESE (die zentrale des Programms). Sie wird frühestens ab Jahr 3 über das Schattenbuch geprüft und bis dahin als unbewiesen geführt.
