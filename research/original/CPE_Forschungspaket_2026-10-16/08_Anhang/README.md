# 08 Anhang

## Original_Review_EN/
Die sieben englischen Originaldokumente des Reviews (CLAUDE_REVIEW.md, CPE_v0.2_REVISED_SPEC.md, SCIENTIFIC_EXPERIMENTS.md, IMPLEMENTATION_SEQUENCE_WINDOWS_SAXO.md, OPEN_QUESTIONS_AND_DECISIONS.md, REVIEW_SCORECARD.csv, START_HERE.md), unverändert. Sie sind die Grundlage der deutschen Kapitel 01 bis 07 und bleiben für die Gegenprüfung durch Codex erhalten. Abweichung: Abschnitt 8 von `CLAUDE_REVIEW.md` und die Kostenangaben in `OPEN_QUESTIONS_AND_DECISIONS.md` (gemischtes Abo-plus-Metering-Budget von 200 bis 600 USD/Monat) sind durch die Eigentümervorgabe vom 16.10.2026 (nur Abos plus Jev) überholt; massgeblich ist `02_Systemarchitektur/03_Modellzugang_Abonnements_Kosten.md`.

## Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/
Reproduzierbarer Beleg, kein Build-Auftrag:
- `PATCH_v01_to_v02.diff`: Unified Diff von v0.1 zu v0.2 (17 Dateien).
- `source_v0_2/`: vollständiger gepatchter Baum; `pip install -e .[test] && python -m pytest -q` ergibt 31 passed (Python 3.13.16, 16.10.2026). Enthält die kompilierten Lean-Dateien mit Toolchain-Pins unter `proofs/`.
- `README.md`: Zuordnung jeder Codeänderung zu einem Befund; Breaking Changes.
- `EVIDENZ_LOGS/`: pytest-Logs v0.1 und v0.2, Angriffsskript mit Ausgabe (F1 bis F10), Lean-Kompilierlog, archivierte TypeSafe-OpenAPI.

Der Code dient dazu, dass Codex die Befunde nachvollziehen und die vorgeschlagenen Korrekturen prüfen kann. Die endgültige technische Spezifikation wird erst nach der gemeinsamen Prüfung entwickelt; dieser Code ist nicht die Implementierung des Systems. Es existiert keine Funktion, die eine Order platziert; LIVE-Promotion wirft `PermissionError`.
