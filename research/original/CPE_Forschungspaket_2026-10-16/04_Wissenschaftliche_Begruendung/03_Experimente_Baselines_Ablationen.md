# 03 Experimente, Baselines, Ablationen, Overfitting-Kontrollen

## 1. Scoring-Regeln und Berichterstattung
- Brier und Log-Score je Prognose (Intervallmittelpunkt für das Scoring; Intervallabdeckung separat als Anteil aufgelöster Ereignisse, deren Ergebnishäufigkeit im Bin innerhalb des fusionierten Intervalls liegt).
- Reliability-Diagramme nach Horizont {≤ 1 M, 1 bis 3 M, 3 bis 9 M}, Sektor, Quellenfamilie, Prognostiker; Bins ≥ 30 Ereignisse.
- Diskrimination: AUC und Spearman-Rangkorrelation für seltene Ziele; Kalibrierung nicht berichtet für Bins < 50 Ereignisse.
- Abstentionsrate, Re-Research-Rate, VOID-Rate je Quelle; ein Prognostiker wird nur auf Items bewertet, bei denen er nicht abstinent war, **und** eine Abstentionsstrafe wird separat berichtet (Abstentionsanteil und Brier der Fusion auf den abstinenten Items, zur Erkennung strategischer Abstention).
- Entdeckungsvorlauf (H5): Tage zwischen `event_registered` und erster externer Erwähnung.
- Power-Plausibilisierung: der Referenztest zeigt, dass ein kalibrierter Challenger gegen eine uninformative Baseline die 20 deutlich innerhalb von 300 Ereignissen erreicht; gegen eine vernünftige Basisraten-Baseline ist die Verbesserung kleiner, 300 Ereignisse sind deshalb eine Untergrenze. Der Plan budgetiert 600 registrierte Ereignisse im ersten Jahr.

## 2. Baselines (alle verpflichtend, alle mit denselben Zeitstempeln im Register)
1. Design-C-Kohortenbasisrate.
2. Marktimplizit, wo verfügbar (optionsimplizite Bewegungswahrscheinlichkeiten, Analystenstreuung); sonst als fehlend markiert.
3. Einzel-LLM (jedes der drei, nur Runde-1-Output).
4. Gleichgewichteter Mittelwert der drei (naives Pooling), um den Wert der korrelationsbewussten Fusion zu isolieren.
5. Zufallsauswahl-Kontrolle für H2 mit identischen Sizing-Regeln.
6. Always-invested-Benchmark für H6.
7. Preistrend (12-1-Momentum) und Buy-and-Hold / Cash für H2.

## 3. Datenhygiene und Leakage-Kontrollen
- Purged, embargoed Walk-Forward für jede trainierte Komponente (Kalibrierkarten, Hazard-Modell, Design C): Purge-Fenster = maximaler Horizont überlappender Ereignisse; Embargo 30 Tage.
- Jede Backtest-Reihe um ihren Publikationsverzögerungseintrag verschoben; Vintage-Daten wo verfügbar; Quellen ohne Eintrag ausgeschlossen.
- Point-in-Time-Universum mit Delistings; Corporate-Action-bereinigte Renditen ab Stichtag; der Wald-Audit berichtet den Anteil später delisteter Kandidaten.
- Zeitstempel-Test: eine Prognose mit `known_at` im Auflösungsfenster wird vom Register abgelehnt (getestet).
- Reality-Check gegen viele Hypothesen: ein primärer E-Prozess je Artefakt; exploratorische Vergleiche mit Anzahl berichtet; keine Promotion auf exploratorischen Tests.
- Overfitting-Kontrollen des Promoters: Shuffled-Label-Holdout (muss keinen Gewinn zeigen), zeitverschobener Holdout, Canary-Ereignisse mit nur dem Promoter bekannten Ergebnissen, hash-gepinnte Datensätze im Ledger.
- Kontamination: Runde-1-Prompts enthalten nur das archivierte Evidenzbündel; Wissensstichtage der Modelle werden je Prognose festgehalten; Ereignisse, deren Auflösungsdatum vor dem Stichtag des Modells liegt, werden aus Skill-Statistiken ausgeschlossen (nur für Pipeline-Tests behalten).

## 4. Anti-Reward-Hacking in der Selbstverbesserung
Tests, die unter Hindsight-Tuning scheitern würden: (1) Shuffled-Label-Holdout darf keine Verbesserung zeigen; (2) zeitverschobener Holdout: ein Challenger, der mit Daten bis T trainiert wurde, darf die Baseline auf Ereignissen, die vor T − Verzögerung aufgelöst wurden, nicht schlagen; (3) Canary-Ereignisse mit fingierten, nur dem Promoter bekannten Ergebnissen; (4) E-Prozess mit λ nur aus der Vergangenheit (bereits erzwungen). Keine Optimierung gegen das Live-Konto: Live-P&L ist kein Input eines Promotionskriteriums. Promotion nur über den Promoter mit deterministischem Skript, Schwellen vorregistriert, Rollback standardmässig.

## 5. Ablationen (vorregistrierte Arme; jeder Arm ist eine eigene Prognostiker-ID im Register)

| Arm | Änderung | Primärmetrik | Kriterium (Jahr 1) |
|---|---|---|---|
| FULL | wie spezifiziert | Brier, Log, Abdeckung | Referenz |
| −Jev | Regeln + lokaler 7B bis 14B-Klassifikator bei gleichem Recall-Budget | Lead-Recall, Kosten, Brier stromabwärts | H3 falsifiziert, wenn Recall(FULL) − Recall(Arm) < 0,1 bei gleichen Kosten |
| −LLM_i (×3) | ein Forscher entfernt, Fusion auf zwei + Jev | Brier | Fusionswert gezeigt, wenn FULL jeden −LLM_i mit E-Wert ≥ 20 schlägt |
| Einzel-LLM (×3) | nur ein Forscher | Brier | siehe H0 |
| −Kohärenz | naiv gepoolte Punktwahrscheinlichkeiten, keine LP-/Credal-Projektion | Kohärenzfehler, Brier | Kohärenzfehler muss > 0 und Brier schlechter sein, sonst Kohärenzschicht aus dem kritischen Pfad entfernen |
| −Zertifikate | kein Lean-/LP-Zertifikatsgate | Logik-/Budgetverletzungen in SIM | 0 in FULL, > 0 im Arm, sonst H4 vakuös |
| −kontrafaktischer Ledger | keine Schattenbücher | kein Prognosearm; Entscheidungsaudit | n/a |
| Design A vs B | LP vs Credal-Netz auf Graphen > 14 Knoten | Brier, Abdeckung, Laufzeit | Auswahl nach 150 Auflösungen |
| Preistrend | 12-1-Momentum auf demselben Universum | H2-Schatten | Benchmark |
| Buy-and-Hold / Cash | | H2-Schatten | Benchmark |

Jev-spezifische prospektive Messungen: Recall von Leads, die in Runde 2 als nützlich beurteilt werden; Falsch-Positiv-Rate; Verteilung des Komplement-Gaps; Latenz; Kosten je 1'000 Dokumente; Drift des zurückgegebenen `model`-Namens.

Quelleninduzierter Stress: FULL mit je einer entfernten Quellenfamilie; Brier-Änderung berichten; treibt eine Familie > 50 Prozent der Skill, Fragilitätsmeldung.

## 6. CI-Schwellen (blockieren Merge, falls nicht erfüllt)
- Alle Tests auf Python 3.11 und 3.13; Lean-Dateien kompilieren auf gepinnter Toolchain.
- Property-Tests: Ledger-Anker erkennt jede Ein-Byte-Änderung; E-Prozess-Fehlalarm-Monte-Carlo ≤ α + 0,015; Fusion liefert RE_RESEARCH bei jedem fehlenden Pflichtinput.
- Statische Gates: kein Modul unter `cpe/` importiert den Executor; keine Strings `Bearer ` oder `refresh_token` in Logs der Testsuite.
- Fehlerinjektion: Jev-503-Stürme, Saxo 429/5xx, Uhrenversatz, abgeschnittener Ledger, fehlerhaftes LLM-JSON; geforderte Reaktion ist fail-closed (kein Orderpfad erreichbar).

## 7. Ergebnisse im ersten Jahr
- Quartal 1: Register live, ≥ 100 Ereignisse registriert, Anker verifiziert, SIM_READ_ONLY erreicht.
- Quartal 2: ≥ 250 registriert, ≥ 60 aufgelöst, erste Reliability-Diagramme (exploratorisch), SIM_PRECHECK.
- Quartal 3: ≥ 450 registriert, ≥ 150 aufgelöst, Auswahl Design A vs B, Jev-Ablation ausgelesen.
- Quartal 4: ≥ 600 registriert, ≥ 300 aufgelöst, primärer E-Prozess ausgelesen; SIM_EXECUTION nur, wenn das Gate-Evidenzbündel vollständig ist.
- Erfolg: primärer E-Wert ≥ 20 mit FULL besser als jedes Einzelmodell; Abstention < 40 Prozent; VOID < 10 Prozent.
- Misserfolg: primärer E-Wert < 20 **und** kein Einzelmodell ≥ 20 (nirgends Skill: stoppen und publizieren), oder ein Einzelmodell ≥ 20 bei FULL < 20 (Fusion schadet: Fusion neu entwerfen, Register behalten).

Nichts im ersten Jahr testet H2. H2 ist ein 5-Jahres-Schattenexperiment mit vorregistrierter Bootstrap-Berichterstattung; der 1'000-Dollar-Pilot, falls je aktiviert, testet den Betrieb.
