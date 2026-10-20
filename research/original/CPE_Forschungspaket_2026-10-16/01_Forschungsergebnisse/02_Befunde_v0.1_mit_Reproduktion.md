# 02 Befunde zu v0.1 mit Reproduktion

Schweregrade: **P0** blockiert jedes Kapital oder entwertet die Wissenschaft; **P1** muss vor SIM-Execution behoben sein; **P2** sollte behoben werden. "Owner" ist Salah, sofern kein Anbieter genannt ist. Reproduktionsnachweise liegen in `08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/EVIDENZ_LOGS/`.

## A. Reproduktionsprotokoll (Angriffsskript `attack_v01_reproduction.py`, Ausgabe `attack_v01_output.log`)

| Nr. | Test | Ergebnis |
|---|---|---|
| F1 | Ledger: einen Prognosewert p = 0,05 auf 0,60 ändern, gesamte Kette neu hashen | `verify_chain()` liefert **True**: Manipulation nicht erkannt |
| F2 | Ledger: Zeile wird mit anderen Separatoren gespeichert als gehasht | Funktioniert, aber fragil: jeder Re-Serialisierer muss die kanonische Form exakt reproduzieren |
| F3 | E-Prozess: Challenger-Wahrscheinlichkeit erst nach Kenntnis des Ergebnisses übergeben (p = 1 bei y = 1, p = 0 bei y = 0) | Wird akzeptiert; E-Wert 3,25 nach 10 Versuchen; nichts erzwingt Commit vor Auflösung |
| F4 | E-Prozess: `betting_fraction = 1`, ein einziger ganz falscher Aufruf | E-Wert dauerhaft 0 (absorbierende Null); kein Guard |
| F5 | E-Prozess: dasselbe Ergebnis 20-mal einspeisen | E-Wert 9,6; keine Ereignisidentität, keine Deduplikation, kein Zeitstempel |
| F6 | Kelly-FOC numerisch prüfen | w* = 0,025 bei p = 0,10 bestätigt (Grid-Argmax 0,025); Kostenvergleich in falschen Einheiten (log-Wachstum vs. Kostenanteil); `p_success_high` wird nirgends verwendet; Formelwert 8,8 bei p = 0,9, up = 1,5, down = 0,9 wird still auf max_fraction geklemmt |
| F7 | Kohärenz: 14 Ereignisse | 16'384 Welten, 0,34 s; `event_probability_bounds` hatte **keinen** n ≤ 14-Guard (2^n unbeschränkt) |
| F8 | Kohärenz: zurückgegebene Verteilung | LP mit Nullzielfunktion liefert einen beliebigen Eckpunkt (hier {FF: 0,5, FT: 0,3, TT: 0,2}); die im RFC beschriebene KL-/Proper-Score-Referenzverteilung ist nicht implementiert |
| F9 | Evidenz: `http://`-URL und beliebiger 64-Hex-String als Digest | Akzeptiert; Provenienz ist selbstdeklariert |
| F10 | Precheck-Payload: `AssetType='NotAnAssetType'`, `Amount=0.0001`, `OrderPrice=1e-9` | Akzeptiert; keine Schemavalidierung |

Weitere ausgeführte Prüfungen: Manifest 20/20 korrekt; v0.1-Tests `11 passed`; Lean-Datei kompiliert auf Lean v4.35.0 + Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`, Negativkontrolle (falsches Theorem) scheitert erwartungsgemäss; Referenzimplementierung `31 passed`.

## B. P0-Befunde

### P0-SCI-01: Kein Prognoseobjekt, nichts ist bewertbar
`core.py:43-66` `BinaryThesis` hat `success_definition: str` als Freitext und ein Wahrscheinlichkeitsintervall, aber kein `known_at`, keine Auflösungsquelle, keine Bewertungsregel, keine Verfallssemantik, keine Prognostiker-Identität je Intervall. Beweis: `BinaryThesis(..., success_definition='10x potential', ...)` passiert `validate()`.
Fix: Prognoseregister mit `EventSpec` (Aussage, Auflösungsquelle, maschinell prüfbares Prädikat, `resolves_not_before`, `expires_at`, Bewertungsregel-Version; Sperre vager Wörter) und `Forecast` (`as_of`, `known_at`, Intervall, Prognostiker, Abstention, Digest der Begründung), ledgergestützt, unveränderliche IDs, verspätete Prognosen abgelehnt. Referenz: `cpe/registry.py`, Test `test_registry_rejects_vague_and_non_prospective`.

### P0-SCI-02: "Kausal" ist nur logische Implikation
`coherence.py:53-58` filtert Welten nach `A ⇒ B`. Das ist probabilistische Logik im Sinne von de Finetti und Nilsson (1986), keine Kausalinferenz. Keine Interventionen, Instrumente, natürliche Experimente oder Event-Study-Designs im Code; im RFC nur Prosa. Ein LLM, das "Regulierung ⇒ Nachfrage" behauptet, liefert eine Korrelations- oder Narrativbehauptung.
Fix (siehe `04/01` und `02/01`): Graph aufteilen in (a) logische Constraints (gehen in das LP, Lean-zertifiziert durch `implication_prob_le`), (b) mechanistische Behauptungen mit Identifikationsklasse {natürliches Experiment, Instrument, Politikvariation, Dosis-Wirkung, keine} und datierter Primärquelle, (c) Regel: nur (a) geht in die Wahrscheinlichkeitsmathematik, (b) in Narrativ und Ereigniszerlegung. Der Vorteil wird an Ereignisprognosen getestet, nicht an der Wahrheit des DAG.

### P0-ARCH-01: Dreier-Komitee und Jev fehlen
`adapters/jev_example.ts` wird nicht ausgeführt, hat keine Schemavalidierung, keine Retries, keine Zeitstempel. Kein Claude-/OpenAI-/Gemini-Code. Beweis: `grep -r "anthropic\|openai\|gemini" cpe/` liefert nichts.
Fix: Fusionsmodul (obligatorisch drei Intervalle plus Jev-Triage, korrelationsbewusste Minimum-Varianz-Gewichte, effektive Modellzahl, typisierte Abstention / Re-Research) und typisierter Jev-Adapter (Schema gegen live `openapi.json` verifiziert, Komplementpaar-Kohärenz, Retries, Kostendeckel, Credential-Leak-Guard). Die drei LLM-Adapter bleiben zu schreiben; ihr Vertrag ist in `02/01` fixiert.

### P0-BRKR-01: Kein SIM-Lesezugriff, Precheck ungesichert
`saxo_sim.py:41-50` postet mit Bearer aus der Umgebung an Precheck; nichts verhindert den Aufruf aus Research-Code. Kein `/port`-Readback, kein `/ref`-Instrumenten-Readback, kein Abgleich.
Fix: Gate-Zustandsmaschine `RESEARCH_ONLY → SIM_READ_ONLY → SIM_PRECHECK → SIM_EXECUTION → SHADOW_LIVE_QUOTES → LIVE_CAPPED_1000`, Promotion nur um einen Schritt mit HMAC-Eigentümerautorisierung, LIVE im Code hart blockiert, Kill-Switch-Demotion für jeden offen. `sim_precheck` verlangt `SIM_PRECHECK`.

### P0-STAT-01: E-Prozess kann seine Gültigkeit nicht erzwingen
`core.py:150-160` nimmt `(baseline_probability, challenger_probability, outcome)` in einem Aufruf: keine Commit-Zeit, keine Ereignis-ID, kein Auflösungsfenster, statisches λ, λ = 1 erlaubt. Beweise F3, F4, F5.
Fix: `CommittedEProcess` mit `commit()` vor `resolve()`, unveränderliche Prognosen, Duplikate abgelehnt, Auflösung nicht vor deklariertem Fenster, prädiktierbares λ nur aus vergangenen Inkrementen (GRAPA-artig, auf λ_max < 1 geklemmt), Ablehnung über laufendes Maximum (gültig nach Ville). Monte-Carlo-Test zeigt Fehlalarmrate ≤ α unter der Nullhypothese und Power bei echter Verbesserung.

## C. P1-Befunde

**P1-LEDGER-01: Hash-Kette neu schreibbar.** `ledger.py:36-47`, Beweis F1. Fix: `seq`, monotones `written_at`, `anchor()` / `verify_against_anchor()` mit optionalem HMAC; Bedrohungsmodell T1 bis T5. Anker sind nur sinnvoll, wenn sie ausserhalb der Schreibrechte des Schreibers liegen (zweite Platte/Konto, signierter Git-Tag, OpenTimestamps; letzteres als Dienst UNVERIFIZIERT).

**P1-COH-01: Exponentielle Enumeration; fehlender Guard.** `coherence.py:76-100`. Guard ergänzt. Struktureller Fix: Credal-Netz für den Forschungsgraphen, LP nur für ≤ 14 entscheidungsrelevante Ereignisse (`03/01`).

**P1-COH-02: LP liefert beliebigen Eckpunkt (F8).** Fix: nur die Intervallausgabe von `event_probability_bounds` stromabwärts verwenden; Referenzverteilung (Max-Entropie oder Min-KL zu einer Basisraten-Prior) als separater, klar benannter Schätzer; nicht im Referenzcode implementiert, als TODO markiert.

**P1-RISK-01: Nur binäres Kelly.** `core.py:95-128`. Für sein Modell korrekt; `p_success_high` ungenutzt; kein Portfolio, keine Korrelation, keine Kosten ausser Fixanteil; Einheitenfehler (im Referenzcode behoben). Fix: Szenario-Max-Min-Log-Wachstum über endliche Credal-Menge mit Brutto-Cap, Positionscaps, harter Worst-Case-Verlustgrenze, fraktionalem Kelly (`03/04`). Test reproduziert 0,025 im Binärfall. Für Optionen/Pfadabhängigkeit weiterhin ein Spielzeug; die Pilot-Whitelist schliesst diese Instrumente aus.

**P1-RISK-02: Keine Krisen-/Wiedereinstiegspolitik im Code.** Spezifiziert in `03/06`: in Echtzeit bekannte Vorlaufindikatoren, Hysterese, Thesenbruch vs. reine Preisstopps, Fehlalarmkosten, verpflichtende Always-invested-Benchmark. Explizit: Evidenz für taktisches Timing in der Literatur ist schwach; Risk-off beschränkt sich auf Drosselung neuer Käufe und Cash-Floor-Anpassung, nie auf Zwangsliquidation thesenintakter Positionen.

**P1-DATA-01: Selbstdeklarierte Zeitstempel.** `core.py:28-40`. Fix: nur `https`, `evidence_digest(bytes)`, Ingest-Log mit beobachtersigniertem `first_observed_at`, archiviertem Snapshot, Publikationsverzögerungstabelle je Quelle, Versions-/Korrekturhandling (`02/01`).

**P1-ACCESS-01: Abo-Zugang nur teilweise.** Siehe `02/03`.

**P1-SEC-01: Secrets in Fehlerpfaden.** v0.1 `response.raise_for_status()` wirft `httpx.HTTPStatusError` mit dem Request-Objekt (und damit dem Bearer-Header); ein generischer Exception-Logger würde es persistieren. Fix: eigener Fehlertyp ohne Request-Objekt; Token nie geloggt. Verbleibend: DPAPI-Speicherung unter Windows, separater Ordersignierprozess.

**P1-SAXO-01: Payload nicht mit dokumentiertem Precheck-Request abgeglichen.** `ManualOrder` ist auf der Precheck-Referenzseite nicht gelistet (gelesen 16.10.2026); `ExternalReference` (≤ 50 Zeichen) existiert und war ungenutzt; der Duplikatschutz läuft über den `x-request-id`-Header beim Platzieren ("exactly the same order within 15 seconds without specifying a different x-request-id header will be rejected"). Fix im Payload-Builder.

## D. P2-Befunde

**P2-CORE-01** Kosteneinheiten (behoben). **P2-EVID-01** URL/Digest flach (teilweise behoben; Archivschicht spezifiziert). **P2-INSTR-01** Freitext-`asset_type` (behoben: Pilot-Whitelist `Stock, Etf, Bond, MutualFund`; `tradable` muss aus `/ref`-Readback stammen). **P2-TEST-01** 11 Tests sind kein funktionierendes System (zugestimmt; jetzt 31, immer noch kein funktionierendes System). **P2-LEAN-01** Kopfzeile "NOT COMPILED" ist jetzt falsch; ersetzt durch Hinweis auf gepinnte Toolchain; Theoreme bleiben triviale lineare Arithmetik und beweisen nichts über Märkte. Ergänzt um `RiskBudget.lean` mit den Lemmata, auf die der Allokator tatsächlich angewiesen ist.

## E. Abgleich mit den vorläufigen Auditbefunden

Alle 16 Zeilen von `INDEPENDENT_AUDIT_FINDINGS.md` wurden reproduziert oder bestätigt. Abweichungen: (1) Lean ist nicht mehr "uncompiled", sondern kompiliert; der Inhalt bleibt trivial. (2) Die E-Prozess-Kritik war zu milde formuliert: nicht nur die Annahmen sind unbeprüft, die API lässt Hindsight-Einträge aktiv zu. (3) Der Punkt "URL validation too shallow" ist ein Teil des grösseren Problems fehlender Ingest-Provenienz. (4) Zusätzlicher Befund P1-SEC-01 (Token in Fehlerpfaden), der im Audit fehlte.
