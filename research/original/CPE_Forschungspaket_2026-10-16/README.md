# Causal Proof Engine (CPE): Forschungspaket zum unabhängigen Review vom 16. Oktober 2026

**Autor des Reviews:** Claude (Fable 5.1), unabhängiger wissenschaftlicher und technischer Co-Architekt.
**Auftraggeber:** Salah Aouaj. **Gegenstand:** Review-Bundle `CPE_Claude_Independent_Review_2026-10-16.zip` (v0.1-Prototyp, Manifest mit 20 SHA-256-Werten vollständig verifiziert).
**Zweck dieses Pakets:** Alle Ergebnisse des Reviews in einer lesbaren, themenorientierten Struktur, damit die Forschung zusammen mit Codex unabhängig geprüft und daraus die endgültige technische Spezifikation entwickelt werden kann.

> **Status: Forschung, keine Implementierung.** Dieses Paket enthält keine Anweisung, Code zu schreiben oder ein Repository anzulegen. Der im Anhang enthaltene Referenzcode ist ein Vorschlag, der ausschliesslich als Beleg für Reproduzierbarkeit und als Diskussionsgrundlage dient. Es wird kein Live-Handel aktiviert; LIVE-Promotion ist im Referenzcode absichtlich blockiert.

---

## 1. Entscheid in einem Absatz

**REVISE.** Kein Kapital, auch nicht der 1'000-Dollar-Pilot. v0.1 ist ein ehrliches Forschungsgerüst mit korrekter Arithmetik, enthält aber kein Element, das heute einen Investmentvorteil erzeugen könnte: keine Daten, keine Prognosen, keine Kalibrierhistorie, keine Modelladapter, kein Broker-Lesezugriff, keine kausale Identifikation, und einen Ledger sowie einen E-Prozess, deren Schnittstellen prospektive nicht von nachträglichen Einträgen unterscheiden können. Vier tragende Behauptungen des Systems sind derzeit nicht falsifizierbar, weil der Messapparat fehlt. Die richtige Antwort ist, den Messapparat zuerst zu spezifizieren (Prognoseregister, verankerter Ledger, E-Prozess mit Commit vor Auflösung, Fusion mit Abstention, Saxo SIM read-only), ihn 6 bis 12 Monate auf Hunderten kurzfristiger registrierter Ereignisse laufen zu lassen, und erst dann zu fragen, ob die Hypothese "10x vor der Trendbeschleunigung" überhaupt testbar ist.

## 2. Fünf harte Aussagen, die der Eigentümer akzeptieren sollte

1. Der neuartige Vorteil (kohärente, kausal zerlegte Multi-Modell-Prognosen schlagen Einzelmodell und Basisraten bei 10x/100x-Ereignissen) **kann innerhalb von 12 Monaten statistisch nicht nachgewiesen werden.** Kalibrierung seltener Ereignisse braucht Hunderte aufgelöster seltener Ereignisse; ein 10-Jahres-10x-Ereignis löst sich in 10 Jahren auf. In 12 Monaten nachweisbar ist Prognosegüte auf Meilenstein-Ereignissen mit 1 bis 9 Monaten Horizont, Jev-Triage-Recall und Betriebsintegrität in SIM.
2. Die ökonomische Hypothese (H2) **ist auf einem 1'000-Dollar-Buch nicht auswertbar.** Bei einem konzentrierten Small-Cap-Buch mit 40 bis 60 Prozent annualisierter Volatilität hat die Einjahresrendite einen Standardfehler, der jedes plausible Alpha weit übersteigt. Der Pilot validiert die Mechanik, nicht Alpha.
3. Das Ziel 4'000 auf 400'000 USD in 10 Jahren bleibt der Nordstern (Eigentümerentscheid 16.10.2026). Es erfordert 58,49 Prozent CAGR bei Vollinvestition ab Tag null (100^(1/10) = 1,5849, nachgerechnet) und strukturell eine Trefferquote um 45 Prozent bei 10x-Gewinnern in gut drei Jahren, dreimal hintereinander, oder seltenere 30x bis 50x-Gewinner (`04/04`). Das ist ein Richtungsziel, keine Erwartung; Gewinn in jedem Kalenderjahr ist ausdrücklich kein Ziel, weil er dem Nordstern widerspricht. Kapitalruin ist unter jeder Politik, die dieses Ziel plausibel erreichen könnte, eine reale Möglichkeit.
4. "Hands-off" hat eine brokerseitige Grenze, die keine Software beseitigt: Saxo-OpenAPI-Sitzungen laufen über OAuth mit kurzen Lebensdauern im dokumentierten Beispiel (`expires_in: 1200`, `refresh_token_expires_in: 2400` Sekunden). Ob eine langlebige unbeaufsichtigte Sitzung für eine individuelle LIVE-App möglich ist, ist **UNVERIFIZIERT** und die wichtigste kontoabhängige Frage (Q1).
5. Der Betrieb läuft ausschliesslich über die bestehenden Abonnements des Eigentümers plus Jev (Eigentümervorgabe vom 16.10.2026, zusätzliche Kosten im ersten Jahr: 0 USD geplant). Verifiziert: Anthropic-Max-Pläne enthalten monatliche Claude-Platform-API-Credits (100 USD bei Max 5x, 200 USD bei Max 20x), nutzbar mit Agent SDK und Messages API; Gemini-CLI-Kontingente für Google AI Pro (1'500 Anfragen/Tag) sind publiziert. OpenAI dokumentiert für programmatische Workflows API-Keys und beschränkt Automatisierungs-Tokens auf Enterprise; OpenAI läuft deshalb als täglicher, vom Eigentümer gestarteter Batch. Die Dreier-Pflicht bleibt erfüllt, nur nicht vollautomatisch (Details `02/03`).

## 3. Dateistruktur und Lesereihenfolge

```
CPE_Forschungspaket_2026-10-16/
├── README.md                                   ← diese Datei (zentraler Einstieg)
├── 01_Forschungsergebnisse/
│   ├── 01_Executive_Summary.md                 Entscheid, Kernaussagen, Genehmigungskriterien, erster Schritt
│   ├── 02_Befunde_v0.1_mit_Reproduktion.md     Alle P0/P1/P2-Befunde mit Datei:Zeile, Reproduktion F1 bis F10, Fix
│   └── 03_Verifikationsprotokoll.md            Was tatsächlich ausgeführt und extern verifiziert wurde
├── 02_Systemarchitektur/
│   ├── 01_Architektur_v0.2.md                  Gesamtarchitektur, Prinzipale, Datenschicht, Modellrollen, Fusion, Sicherheit
│   ├── 02_Saxo_Broker_Integration_und_Gates.md Verifizierte Saxo-Fakten, Gate-Zustandsmaschine, Pilot-Whitelist
│   ├── 03_Modellzugang_Abonnements_Kosten.md   Zugangsrouten je Anbieter, Budget, Degradationsleiter
│   ├── 04_Langlebigkeit_und_Evolution_25_Jahre.md  Kern vs. Hülle, Modellwechsel als Standardvorgang, α-Budget, Jahresbericht, Kontinuität
│   └── 05_Horizonterweiterung_Assetklassen_und_Forschungsaktualitaet.md  Erweiterungsleiter (Rohstoffe, Krypto, Optionen, Futures), Methodenscanner
├── 03_Mathematische_Modelle/
│   ├── 01_Kohaerenz_Credal_Sets_und_Lean.md    LP-Kohärenz, Credal-Netz, Referenzverteilung, kompilierte Lean-Lemmata
│   ├── 02_E-Prozess_und_sequentielle_Tests.md  Supermartingal, Ville, prädiktierbares Lambda, Fehlerquellen, Korrektur
│   ├── 03_Fusion_korrelierter_Prognosen.md     Minimum-Varianz-Gewichte, effektive Modellzahl, Abstention
│   ├── 04_Allokation_und_Ruinrisiko.md         Kelly-Herleitung, Fehler in v0.1, Szenario-Max-Min, Pilot-Limits
│   ├── 05_Seltene_Wahrscheinlichkeiten.md      Methodik für p < 5 Prozent, Zerlegung, Basisraten, Diskrimination
│   └── 06_Krisen_Hazard_Modell.md              Vorlaufende Inputs, Hysterese, Thesenbruch vs. Preis, Backtest-Set
├── 04_Wissenschaftliche_Begruendung/
│   ├── 01_Originalitaet_und_Stand_der_Forschung.md  Etabliert vs. neu; Kausalität vs. Implikation; Designs A/B/C
│   ├── 02_Hypothesen_und_Falsifikation.md      H0 bis H6 mit Falsifikatoren
│   ├── 03_Experimente_Baselines_Ablationen.md  Scores, Baselines, Leakage-Kontrollen, Ablationen, CI, Jahr-1-Ergebnisse
│   └── 04_Nordstern_und_Etappenziele.md        100x als Nordstern, Zielarithmetik, Etappenziele, was kein Ziel ist
├── 05_Quellen/
│   ├── 01_Quellenverzeichnis.md                Alle Quellen mit Datum und Verifikationsstatus
│   └── typesafe_openapi_2026-10-16.json        Archivierte Jev-API-Spezifikation
├── 06_Offene_Probleme_und_Risiken/
│   ├── 01_Offene_Fragen_Q1_bis_Q9.md           Blockierende und nicht blockierende Fragen mit Validierungsweg
│   ├── 02_Risikoregister.md                    Risiken nach Klasse, Eintrittswahrscheinlichkeit, Wirkung, Gegenmassnahme
│   └── 03_Annahmen_und_Validierung.md          Kritische Annahmen und wie sie geprüft werden
├── 07_Empfehlungen_Implementierung/
│   ├── 01_Implementierungssequenz_Windows_Saxo.md  Zehn Schritte mit Akzeptanztests, Fehlerpfaden, Kosten
│   ├── 02_Entscheide_und_Prioritaeten.md       Getroffene Entscheide, Reihenfolge, was zuerst nicht gebaut wird
│   ├── 03_Scorecard.md                         Alle 21 Kriterien mit Verdikt (lesbare Fassung)
│   └── Scorecard.csv                           Dieselbe Scorecard als CSV
├── 08_Anhang/
│   ├── Original_Review_EN/                     Die sieben englischen Originaldokumente, unverändert
│   └── Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/
│       ├── README.md, PATCH_v01_to_v02.diff, source_v0_2/   Reproduzierbarer Beleg (31 Tests), kein Build-Auftrag
│       └── EVIDENZ_LOGS/                       pytest-Logs, Angriffsskript, Lean-Kompilierlog
└── MANIFEST.sha256
```

Empfohlene Lesereihenfolge für die Gegenprüfung mit Codex: README → 01/01 → 01/02 → 03 (alle) → 04 (alle) → 02 (alle) → 06 → 07. Die Quellen in 05 sind von überall referenziert.

## 4. Verbindliche Ziele und Randbedingungen (unverändert übernommen, ergänzt am 16.10.2026)

Ergänzung des Eigentümers: Das Projekt muss sich über die nächsten 25 Jahre ständig verbessern und selbständig weiterentwickeln, neue bessere Modelle laufend einbauen und alles wissenschaftlich erfassen und nachweisen. Wie das architektonisch gesichert wird (unveränderlicher Kern, evolvierbare Hülle, Modellwechsel als Standardvorgang, α-Budget über Jahrzehnte, automatischer Jahresbericht, Wiederherstellungstest, Totmannschalter) steht in `02/04`. Sprachregel: formal bewiesen (Lean, bedingt), statistisch nachgewiesen (E-Prozesse), empirisch belegt (Track Record) werden nie vermischt.

Weitere Ergänzung: Das System bleibt bei KI- und Finanzforschung auf dem Stand (Methodenscanner, Methodenledger), erweitert seine Finanzwerkzeuge laufend und dehnt seinen Horizont über Aktien hinaus aus (Rohstoffe, Metalle, Energie, Krypto über börsennotierte Vehikel, Optionen mit definiertem Risiko; Futures, Short-Optionen, CFDs nur nach Kernänderung). Jede neue Assetklasse durchläuft denselben Nachweisweg wie ein neues Modell: `02/05`.

Drei unabhängige Spitzenmodelle (Claude, OpenAI, Gemini) plus Jev als obligatorische Kernkomponenten; keine einfache Mehrheitsentscheidung; kontinuierliche Selbstverbesserung von Hypothesen, Features, Prognose- und Kausalmodell; branchenunabhängige Entdeckung aus physikalischen, wissenschaftlichen, demografischen, institutionellen und ökonomischen ersten Prinzipien; Saxo-zuerst mit SIM; nur der Eigentümer autorisiert Zugänge, Limits und LIVE-Aktivierung; maximal 1'000 USD live im ersten Jahr, 3'000 USD ausserhalb; keine Margin, keine ungedeckten Optionen, keine Instrumente mit unbegrenztem Verlust, keine automatisierten Short-Positionen im Pilot; Windows 11 mit RTX 5090 als Entwicklungsumgebung; Präferenz für bestehende Abonnements statt Token-Kosten, ohne Umgehung von Produktkontrollen.

## 5. Schnellverifikation (10 Minuten)

```
sha256sum -c MANIFEST.sha256
cd 08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/source_v0_2
pip install -e .[test] && python -m pytest -q        # erwartet: 31 passed
```

Das Ausführen der Tests ist Verifikation des Belegs, keine Implementierung des Systems.

## 6. Kennzeichnung

Durchgehend: **HYPOTHESE** markiert unbewiesene wissenschaftliche Behauptungen; **UNVERIFIZIERT** markiert externe Aussagen, die in dieser Sitzung nicht gegen eine Primärquelle geprüft werden konnten; **verifiziert (Datum)** markiert gegen eine offizielle Quelle geprüfte Aussagen. Simulierte Leistung ist nie Live-Leistung; mathematische Kohärenz ist nie prädiktive Korrektheit; ein formaler Beweis impliziert nie einen Gewinn.

## 7. Sofortiger erster Schritt für den Eigentümer

Saxo-Developer-Portal-SIM-Applikation anlegen und ein Ein-Tages-SIM-Token auf dem Windows-Rechner beziehen; die Referenztests lokal ausführen; ein einziges Read-only-SIM-Readback durchführen und dessen Digest im verankerten Ledger ablegen. Nichts anderes vorher, insbesondere keine LLM-Pipeline und keine Orders.
