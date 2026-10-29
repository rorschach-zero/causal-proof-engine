# 01 Implementierungssequenz Windows 11 und Saxo (Empfehlung, noch nicht auszuführen)

Zielmaschine: Windows 11, RTX 5090, grosser Arbeitsspeicher. Jeder Schritt hat Akzeptanztest und Fehlerpfad. Befehle sind nur angegeben, wo das Werkzeug im Paket verifiziert wurde; Saxo-seitige UI-Schritte folgen den am 16.10.2026 gelesenen Learn-Seiten und können im Wortlaut abweichen. **Nichts hier platziert eine Order. LIVE ist im Referenzcode blockiert.** Die Sequenz ist eine Empfehlung für die Zeit nach der gemeinsamen Prüfung mit Codex; sie ist kein Auftrag, jetzt zu bauen.

Sicherheitsregeln für alle Schritte: nie Tokens, App-Secrets, Account-Keys, Bestände oder Passwörter in einen AI-Chat einfügen; Repo in einem Ordner ohne Secrets halten; vor Schritt 7 drei Windows-Benutzerkonten anlegen (`cpe-research`, `cpe-promoter`, `cpe-executor`) gemäss `02/01` Abschnitt 2.

## Schritt 0 (heute, 30 Minuten): Paket lokal verifizieren
1. ZIP entpacken; `MANIFEST.sha256` prüfen (PowerShell: `Get-FileHash -Algorithm SHA256 <Datei>` und vergleichen).
2. Dieses Paket an die Codex-Gegenprüfung geben. Nicht mit dem Bau beginnen, bevor beide Reviews zu Q1 und Q2 übereinstimmen.
Akzeptanz: Hashes stimmen. Fehlerpfad: bei Abweichung Paket verwerfen und neu anfordern.

## Schritt 1 (Tag 1): Python-Umgebung und Referenztests
Voraussetzung: Python 3.11 oder neuer von python.org (hier geprüft auf 3.13.16).
```powershell
cd <repo>\08_Anhang\Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN\source_v0_2
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[test]
python -m pytest -q
```
Akzeptanz: `31 passed`. Fehlerpfad: scheitern `scipy`/`numpy`-Wheels, Python 3.12 verwenden; scheitert ein Test, stoppen und Testnamen beiden Reviewern melden.

## Schritt 2 (Tag 1 bis 2): Lean-Zertifikats-Toolchain (optional für M0, Pflicht vor SIM_PRECHECK)
Pins: Lean `leanprover/lean4:v4.35.0`, Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2` (`proofs/lean-toolchain`, `proofs/lake-manifest.json`). elan von https://github.com/leanprover/elan installieren (Windows-Installer), dann in einem neuen Ordner:
```powershell
lake +leanprover/lean4:v4.35.0 new cpe_proofs math
cd cpe_proofs
# lake-manifest.json durch proofs/lake-manifest.json und lean-toolchain durch proofs/lean-toolchain ersetzen
lake exe cache get
copy ..\proofs\*.lean CpeProofs\
lake env lean CpeProofs\BetThreshold.lean
lake env lean CpeProofs\RiskBudget.lean
```
Akzeptanz: beide Befehle Exit 0; `RiskBudget.lean` druckt vier Zeilen `depends on axioms: [propext, Classical.choice, Quot.sound]`. Kosten: rund 8 GB Platte für den Mathlib-Cache (gemessen 7,8 GB), 20 bis 40 Minuten Download. Fehlerpfad: scheitert `lake exe cache get` hinter einem Proxy, auf einem offenen Netz ausführen; weicht Mathlibs `lean-toolchain` ab, exakt das gepinnte Manifest verwenden, nicht `lake update`.

## Schritt 3 (Tag 2): Ledger-Verankerung und Eigentümersecret
1. Eigentümersecret einmal erzeugen (PowerShell: `[Convert]::ToBase64String((1..32 | % { Get-Random -Max 256 }) -as [byte[]])`); nur im Windows Credential Manager des Eigentümerkontos speichern.
2. Ankerspeicher an einem Ort anlegen, den das Research-Konto nicht beschreiben kann (OneDrive/iCloud-Ordner des Eigentümerkontos oder zweite Maschine).
3. Geplante tägliche Aufgabe, die `AppendOnlyLedger.anchor(secret)` aufruft und das JSON in den Ankerspeicher schreibt.
Akzeptanz: `verify_against_anchor` besteht von einer zweiten Maschine aus nur mit Ankerdatei und Ledgerkopie. Fehlerpfad: ist der Ankerspeicher vom Research-Konto beschreibbar, ist der Anker dekorativ; zuerst Berechtigungen korrigieren.

## Schritt 4 (Tag 3 bis 5): Saxo-SIM-Applikation und Read-only-Readback (**erste sichere externe Aktion**)
1. Bei https://www.developer.saxo registrieren (SIM). SIM-Applikation anlegen. **Ein-Tages-SIM-Token** aus dem Developer Portal beziehen; es ist "only authorized for the simulation environment".
2. `SAXO_SIM_ACCESS_TOKEN` nur in der Sitzung des Executor-Kontos setzen (`$env:SAXO_SIM_ACCESS_TOKEN = '<token>'`), nie in einer Datei.
3. `scripts/sim_readback.py` schreiben und ausführen (in M1; nicht im Paket, weil die Pfade zuerst in der Referenzdokumentation für das Konto bestätigt werden müssen): Aufrufe für Konten, Salden, Positionen, Orders und eine Instrumentdetail-Abfrage; Digests und den **Hash** des `AccountKey` (nicht den Key) im Ledger ablegen.
4. Gate `RESEARCH_ONLY → SIM_READ_ONLY` mit Eigentümer-HMAC über den Hash des Readback-Berichts promoten.
Akzeptanz: 7 Tage in Folge protokollierte Readbacks; keine 401/403; Abgleich des simulierten 100'000-USD-Saldos. Fehlerpfad: 401 bedeutet abgelaufenes Ein-Tages-Token (täglich erwartet); 403 auf einem Endpunkt bedeutet fehlenden Scope der SIM-App, in Q1 festhalten und Saxo-Support fragen; jeder andere Fehler: stoppen.

## Schritt 5 (Woche 2 bis 3): OAuth-PKCE-Applikation und Test des unbeaufsichtigten Refresh
1. PKCE-Applikation anlegen (Redirect-URI `http://localhost:<port>/callback`), `/authorize` → `/token` mit `code_challenge_method=S256` implementieren, Refresh-Token im Credential Manager (Executor-Konto) speichern.
2. Reale `expires_in` und `refresh_token_expires_in` messen und prüfen, ob der Refresh 72 Stunden lang wiederholt unbeaufsichtigt gelingt.
Akzeptanz: 72 Stunden durchgehend gültige Sitzungen ohne Browser-Login. Fehlerpfad: lassen sich Sitzungen nicht unbeaufsichtigt halten, ist "hands-off" brokerseitig unmöglich; Rückfall auf vom Eigentümer ausgelöste Sitzungen (z. B. ein Login pro Tag), als dauerhafte Randbedingung festgehalten (Q1).

## Schritt 6 (Woche 3 bis 6): Register, Ingest-Log und Jev-Triage im Betrieb (Research-Konto)
1. Jev-Early-Access beantragen (Warteliste, Vendor-Blog 15.09.2026); nach Erhalt `TYPESAFE_API_KEY` im Credential Manager (Research-Konto) speichern.
2. `GET /v1/models` ausführen und Modellnamen samt `release_date` im Ledger festhalten.
3. Ingest-Log mit 3 bis 5 Quellenfamilien mit Publikationsverzögerungseinträgen starten; `ask_noul_pair` auf jedem Dokument; die ersten 20 EventSpecs von Hand registrieren, die drei LLMs *noch nicht* in der Schleife.
Akzeptanz: 100 Dokumente triagiert, Komplement-Gap-Histogramm erstellt, 20 Ereignisse mit Design-C-Baseline-Prognosen committet. Fehlerpfad: verzögert sich der Jev-Zugang, den `−Jev`-Ablationsarm (Regeln + lokaler Klassifikator) verwenden und den Jev-Platz im Schema als Pflicht beibehalten, damit stromabwärts nichts stillschweigend adaptiert.

## Schritt 7 (Woche 6 bis 10): Drei-Modell-Adapter innerhalb der Abo-Bedingungen
1. Claude: monatlichen Max-API-Credit beanspruchen (7 Tage Wartefrist), eine Console-Organisation verknüpfen, Agent SDK oder Messages API mit diesem Key verwenden (Supportartikel 17154008). Budgetalarm bei 80 Prozent des Credits.
2. OpenAI: kein API-Key. Codex CLI mit ChatGPT-Login als täglicher, vom Eigentümer gestarteter Batch (ein Befehl, interaktive Sitzung, Ergebnisse ins Register). Plus vs. Pro erst nach Volumenmessung entscheiden.
3. Gemini: Gemini CLI mit Google AI Pro; unbeaufsichtigt, sofern die am Einrichtungstag gelesenen Bedingungen dies decken, sonst ebenfalls eigentümergestarteter Batch (Q2). Kein Gemini-API-Key.
4. Tages-Token-Deckel je Anbieter im Adapter; Kosten je Prognose protokollieren.
Akzeptanz: drei unabhängige Runde-1-Outputs je Ereignis, schemavalidiert, kein Cross-Reading (getrennte Prozesse, kein geteilter Kontext); Fusion liefert FORECAST / ABSTAIN / RE_RESEARCH; E-Prozess gegen Design C läuft. Fehlerpfad: sind die Bedingungen eines Anbieters für unbeaufsichtigte Nutzung unklar, diesen Anbieter interaktiv in einem täglichen, vom Eigentümer ausgelösten Batch betreiben und die Abhängigkeit festhalten; nie eine Consumer-Web-UI automatisieren.

## Schritt 8 (Monat 3 bis 4): SIM_PRECHECK
Mit Eigentümer-HMAC nach Evidenz aus Schritt 4 bis 7 promoten. `sim_precheck` nur auf Whitelist-Instrumenten; `Cost`, `EstimatedCashRequired`, `MarginImpactBuySell`, `PreCheckResult`, `ErrorInfo` archivieren.
Akzeptanz: 30 Prechecks über ≥ 10 Instrumente; Kostenfelder geparst; kein `ErrorInfo`. Fehlerpfad: Precheck-Fehler zu `ExternalReference` oder `FieldGroups` bedeuten, dass die dokumentierte Request-Form für die Berechtigung abweicht; Builder mit Test anpassen, nie Payloads von Hand editieren.

## Schritt 9 (Monat 4 bis 6): SIM_EXECUTION (Code zu schreiben, separat zu prüfen)
Schreibt `POST /trade/v2/orders` mit `ManualOrder:false`, `x-request-id`, `ExternalReference`; behandelt `TradeNotCompleted` durch `/port`-Readback vor jedem Retry; Storno-Pfad; Abgleich jedes Fills mit einem Zertifikat; Kill-Switch-Watchdog.
Akzeptanz: 60 Tage, null Doppelorders, null Orders ohne Zertifikat, Abgleich sauber. Dieser Schritt erfordert ein zweites Code-Review (Codex) vor dem Merge.

## Schritt 10 (Monat 6+): Shadow-Live-Quotes; LIVE bleibt blockiert
LIVE-Applikation (erfordert getestete SIM-App und finanziertes Konto) erst nach Schritt 1 bis 9 und einem unabhängigen Sicherheitsreview des Executors. Der Referenzcode wirft bei LIVE-Promotion `PermissionError`; Freischaltung ist ein separates Release mit eigenem Review.

## Kosten (Planungsgrössen, keine Offerten)
- Nur die bestehenden Abonnements (Max, ChatGPT Plus/Pro, Google AI Pro); kein Metering geplant (`02/03`).
- Jev realistisch unter 10 USD/Monat bei 200 Dokumenten/Tag, Obergrenze unter 100 USD/Monat.
- Daten: nur öffentliche, kostenlose Quellen; kein lizenziertes Point-in-Time-Universum im ersten Jahr (Q5 auf Vorwärtsrekonstruktion gesetzt).
- Platte: rund 10 GB für Lean + Mathlib; Ledger und Archive wachsen 1 bis 5 GB/Jahr bei 200 Dokumenten/Tag.
- Zeit: wiederkehrende Pflichten des Eigentümers sind die monatliche Ankerprüfung und die Gate-Promotionen; alles andere ist innerhalb der Broker-Sitzungsgrenze unbeaufsichtigt ausgelegt.
