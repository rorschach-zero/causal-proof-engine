# 01 Executive Summary

Datum 16.10.2026. Reviewer: Claude (Fable 5.1). Input: `CPE_Claude_Independent_Review_2026-10-16.zip`, Manifest vollständig verifiziert.

## 1. Entscheid

**REVISE. Kein Kapital, einschliesslich des 1'000-Dollar-Piloten. Das Programm wird nicht abgelehnt.**

Begründung: v0.1 ist nach eigener Aussage (README) ein Forschungsgerüst. Seine Arithmetik ist korrekt, wo sie existiert (Kelly-Schwelle 4/49, Optimum 0,025 bei p = 0,10, Kohärenz-LP). Es fehlt aber alles, was einen Vorteil messbar machen könnte: Daten, Prognosen mit Auflösungskriterium, Kalibrierhistorie, Modelladapter, Broker-Lesezugriff, kausale Identifikation. Ledger und E-Prozess haben Schnittstellen, die nachträgliche Einträge nicht von prospektiven unterscheiden. Daraus folgt: Messapparat zuerst, Vorteilsnachweis danach.

## 2. Was in dieser Sitzung tatsächlich getan wurde

- Alle Quelldateien gelesen, Manifest geprüft, 11 Tests reproduziert (Python 3.13.16).
- Zehn Angriffs- und Prüfskripte gegen v0.1 ausgeführt (F1 bis F10), Ergebnisse protokolliert.
- Lean 4 mit Mathlib auf gepinnter Toolchain installiert, `BetThreshold.lean` kompiliert, Negativkontrolle bestätigt, sieben weitere Lemmata formuliert und kompiliert.
- Jev-API-Schema aus dem live `openapi.json` von api.typesafe.ai verifiziert und archiviert.
- Saxo-Dokumentation (Environments, Order Placement, Precheck-Referenz, PKCE, LIVE-Credentials) gelesen; Abo-Bedingungen von Anthropic, OpenAI und Google gelesen; arXiv-Titel der zitierten Papiere über die arXiv-API bestätigt.
- Eine v0.2-Referenzimplementierung als Beleg geschrieben (31 Tests), ausdrücklich als Vorschlag, nicht als Build-Auftrag.

## 3. Die fünf harten Aussagen

Siehe README Abschnitt 2; sie werden hier nicht verkürzt wiederholt, sondern in den Fachkapiteln begründet: Aussage 1 und 2 in `03_Mathematische_Modelle/05` und `04_Wissenschaftliche_Begruendung/02`; Aussage 3 in `03/04`; Aussage 4 in `02/02`; Aussage 5 in `02/03`.

## 4. Schwerwiegendste Befunde (Kurzform, Details in 01/02)

| ID | Schwere | Kern |
|---|---|---|
| P0-SCI-01 | P0 | Es existiert kein Prognoseobjekt mit Auflösungskriterium, Verfall, Bewertungsregel; "10x potential" würde validieren. |
| P0-SCI-02 | P0 | "Kausal" ist nur logische Implikation; keine Identifikationsstrategie. |
| P0-ARCH-01 | P0 | Dreier-Komitee und Jev fehlen; einziger Adapter ist eine nicht ausgeführte TypeScript-Skizze. |
| P0-BRKR-01 | P0 | Kein SIM-Lesezugriff; Precheck ist der einzige Aufruf und nicht zustandsgesichert. |
| P0-STAT-01 | P0 | E-Prozess-API kann ihre Gültigkeitsbedingungen nicht durchsetzen (Hindsight, Duplikate, absorbierende Null). |
| P1-LEDGER-01 | P1 | Hash-Kette ist durch Neuschreiben plus Re-Hash umgehbar. |
| P1-COH-01/02 | P1 | Exponentielle Enumeration ohne Guard; LP liefert beliebigen Eckpunkt. |
| P1-RISK-01/02 | P1 | Nur binäres Kelly, Kosteneinheiten falsch; keine Krisenpolitik. |
| P1-DATA-01 | P1 | Zeitstempel selbstdeklariert. |
| P1-ACCESS-01 | P1 | Unbeaufsichtigter Drei-Modell-Zugang per Abo nur teilweise gedeckt; gelöst durch eigentümergestarteten OpenAI-Batch (`02/03`). |
| P1-SEC-01 | P1 | Fehlerpfade können das Bearer-Token mittragen. |
| P1-SAXO-01 | P1 | Precheck-Payload nicht mit dokumentiertem Request abgeglichen. |

## 5. Was den Entscheid zu APPROVE ändern würde (für SIM_EXECUTION, nicht LIVE)

1. 300 oder mehr registrierte Ereignisse in mindestens 6 Sektoren, davon mindestens 150 aufgelöst; fusionierte Prognosen schlagen die Basisraten-Baseline (Design C) im Brier-Score, der committete E-Prozess überschreitet 1/α bei α = 0,05, vorregistriert.
2. Ablation zeigt, dass die Drei-Modell-Fusion das beste Einzelmodell im Log-Score schlägt, mit effektiver Modellzahl über 1,5.
3. Jev-Triage-Recall seltener nützlicher Leads mindestens 0,8 bei höchstens 20 Prozent der Kosten der LLM-Triage, prospektiv gemessen.
4. Ledger-Anker monatlich vom Eigentümer von einer unabhängigen Maschine verifiziert; null Ankerfehler.
5. SIM read-only, Precheck und Abgleich 60 Tage in Folge fehlerfrei bei Gate `SIM_PRECHECK`.
6. Antworten auf die offenen Fragen Q1 bis Q6.

LIVE_CAPPED_1000 erfordert zusätzlich ein unabhängiges Sicherheits- und Risiko-Review des Ordersignierprozesses; es ist im Referenzcode hart blockiert.

## 6. Erster Schritt

Saxo-SIM-App anlegen, Ein-Tages-Token beziehen, Referenztests lokal laufen lassen, ein Read-only-Readback im Ledger verankern. Nichts anderes vorher.
