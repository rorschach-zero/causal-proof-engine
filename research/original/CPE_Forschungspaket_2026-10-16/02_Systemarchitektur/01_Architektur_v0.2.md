# 01 Systemarchitektur v0.2 (vorgeschlagen)

Status: Forschungsarchitektur zur gemeinsamen Prüfung; ersetzt `source_v0_1/docs/RFC.md` inhaltlich. Konventionen: MUSS / DARF NICHT sind in Code oder Tests durchsetzbar; SOLL ist Entwurfsleitlinie; HYPOTHESE markiert unbewiesene wissenschaftliche Behauptungen.

## 1. Gesamtbild

```
Quellen (Filings, Register, Normungsgremien, Beschaffung, Patente, Studien, Bewilligungen, Demografie, Preise)
   │  Ingest-Log: beobachtersigniertes first_observed_at, archivierte Bytes, SHA-256, Publikationsverzögerungstabelle
   ▼
Jev-Triage (obligatorisch): datierte Primärquelle? relevant für welchen registrierten Mechanismus? Duplikat? Widerspruch?
   │  Komplementpaar-geprüfte noul-Fragen; Eskalationsscore
   ▼
Drei unabhängige Forscher (Claude, OpenAI, Gemini), Runde 1 blind
   │  typisierte PCCB-Fragmente: Mechanismus (mit Identifikationsklasse), Ereignisse (EventSpec), Intervallprognosen
   ▼
Kohärenzschicht: Credal-Netz (Design B) für den Forschungsgraphen; LP-Zertifikat (Design A) auf ≤ 14 Entscheidungsereignissen
   │  fusionierte Intervalle (korrelationsbewusst), Abstain-/Re-Research-Entscheide
   ▼
Register + verankerter Ledger (Commit vor Ergebnis) ──► E-Prozess-Monitore, Kalibrierkarten, Ablationen
   │
   ▼
Wertschöpfungsmodell → Szenarioset → robuste Allokation (Max-Min-Log-Wachstum, Caps, Worst-Loss) → Zertifikat
   │
   ▼
Gate-Zustandsmaschine → Saxo SIM read-only → Precheck → (SIM-Execution) → (Shadow-Live-Quotes) → [LIVE blockiert]
```

Das PCCB (Proof-Carrying Causal Bet) aus dem RFC bleibt das zentrale Forschungsobjekt. Seine acht Bestandteile (origin, mechanism, events, belief, value_capture, adversarial_case, decision, audit_trail) werden beibehalten; neu ist, dass jeder Bestandteil ein typisiertes Schema mit Zeitstempeln und Identifikationsklasse hat und dass "belief" ausschliesslich aus registrierten Ereignisprognosen besteht.

## 2. Prinzipale und Trennung der Verantwortung

Vier Prinzipale mit getrennten Betriebssystemkonten und Secrets:

| Prinzipal | Darf | Darf nicht |
|---|---|---|
| **Researcher** | alle LLM-/Jev-Aufrufe, Ingest, Register-Schreibzugriff (append-only), Vorschläge an den Promoter | Broker-Secrets besitzen; Executor-Modul importieren; Holdouts verändern |
| **Promoter** | eingefrorene Holdouts lesen, deterministisches Akzeptanzskript ausführen, Promotion/Rejection in den Ledger schreiben | Code schreiben; Limits ändern |
| **Executor** | Broker-Tokens halten, Zertifikate prüfen, Precheck/Orders senden (Orders erst ab SIM_EXECUTION) | LLM-Zugang; Research-Daten verändern |
| **Eigentümer** | Gate-HMAC-Secret, Ankerspeicher, Promotion um einen Schritt, LIVE-Freigabe (separates Release) | nichts automatisiert; alle Aktionen werden protokolliert |

Die Selbstverbesserungsschleife DARF NICHT verändern: Risikolimits, Gate-Zustand, Broker-Berechtigungen, Evaluationsdatensätze, Ledger, Fusionsschwellen. Live-P&L des 1'000-Dollar-Kontos ist nie ein Input für Promotion.

## 3. Datenschicht

### 3.1 Ingest-Log (ersetzt selbstdeklarierte Zeitstempel)
Jedes Dokument D erhält `{doc_id, source_url (https), archived_sha256, archived_bytes_path, published_at (quellendeklariert), first_observed_at (Beobachteruhr, signiert), observer_id, fetch_headers_digest, language, parser_version, extraction_uncertainty}`. `available_at := max(published_at, first_observed_at)` wird berechnet, nie geliefert. Die Beobachteruhr ist NTP-diszipliniert, Drift wird täglich protokolliert. Korrekturen und Revisionen erzeugen eine neue `doc_id` mit `supersedes`-Zeiger; Prognosen zitieren die Version, die sie verwendet haben.

### 3.2 Publikationsverzögerungstabelle
Je Quellenfamilie die typische Verzögerung zwischen Ereignis und öffentlicher Verfügbarkeit (z. B. SLOOS quartalsweise mit rund einem Monat Verzögerung; EDGAR tagesgleich; FDA 510(k) wöchentliche Batches; EU-Beschaffung TED täglich). Backtests MÜSSEN jede Reihe um die dokumentierte Verzögerung verschieben und Vintage-Daten verwenden, wo sie existieren (ALFRED für FRED-Reihen). Quellen ohne Eintrag DÜRFEN NICHT in Backtests verwendet werden.

### 3.3 Point-in-Time-Universum (Wald-Test)
Monatlicher Snapshot des bei Saxo investierbaren Universums (aus `/ref`-Readback ab SIM_READ_ONLY; historische Rekonstruktion aus lizenziertem PIT-Datensatz ist offene Frage Q5): jedes Listing inklusive späterer Konkurse, Delistings, Reverse Splits, Übernahmen. Jeder Kandidat, den der Scanner je berührt hat, wird mit `considered_at`, Entscheid (`invest | reject | uninvestable | watch`) und Grund in den Ledger geschrieben. Schattenbücher: `no_exit_shadow` für jeden Ausstieg, `entry_shadow` für jede Ablehnung mit These, `random_control` nach Datum und Grösse gematcht.

## 4. Prognose- und Kohärenzschicht (mathematische Details in `03/01`, `03/03`)

### 4.1 EventSpec und Forecast
Eine Prognose ist `P(Ereignis E löst bis expires_at mit JA auf)`, wobei E hat: Aussage, `resolution_source` (benannte Datenbank oder Dokumentklasse), `resolution_predicate` (maschinell prüfbarer Regeltext, versioniert), `resolves_not_before`, `expires_at`, `grading_rule_version`. Vage Prädikate (`potential`, `could`, `might`, `significant`, `strong`) werden abgelehnt. Prognosen tragen `as_of` (Informationsstichtag), `known_at` (Wanduhr), Intervall `[p_low, p_high]`, Prognostiker plus Version, Evidenz-IDs, Digest der Begründung, `abstained`. Breite > 0,5 wird als Abstention gewertet. Status: COMMITTED → RESOLVED_YES / RESOLVED_NO / EXPIRED_NO / VOID. VOID-Rate je Quelle ist eine überwachte Kennzahl; VOID wird nie stillschweigend fallen gelassen.

### 4.2 Mechanismusobjekte mit Identifikationsklasse
`Mechanism {id, cause_event, effect_event, direction, identification_class ∈ {natural_experiment, instrument, policy_variation, dose_response, none}, exogenous_variation_description, swa_assumptions[], primary_sources[], counter_mechanisms[], substitutes[]}`. Nur logische Verknüpfungen (A ⊆ B per Definition, z. B. "Umsatz > X" ⇒ "Umsatz > Y" für X > Y, oder "Zulassung erteilt" ⇒ "Antrag eingereicht") gehen als Constraints in das LP. Mechanismen der Klasse `none` gehen nur in Narrativ und Ereigniszerlegung. Das ist die formale Grenze zwischen "kausales Schliessen als Hypothesengenerierung" und "Wahrscheinlichkeitsmathematik".

### 4.3 Design B als Forschungsmaschine, Design A als Zertifikatsschicht, Design C als Baseline
Vergleich und Auswahlkriterien in `04/01`. Kurz: Credal-Netz mit bedingten Intervallen je Kante, Inferenz durch Monte Carlo über gezogene CPTs (M = 2'000), Zielintervall als [5., 95.] Perzentil plus Hülle; LP-Zertifikat nur auf der Entscheidungsprojektion (≤ 14 Ereignisse); Basisraten-Hazard-Modell ohne Graph und ohne LLM als verpflichtende Vergleichsgrösse.

### 4.4 Fusion
Eingaben: drei Intervalle plus Jev-Triage-Datensatz. Gewichte `w = R⁻¹1 / (1ᵀR⁻¹1)` aus der geschrumpften Fehlerkorrelationsmatrix vergangener standardisierter Fehler; Rückfall auf Gleichgewichte mit Flag; fusioniertes Intervall als Konvexkombination; `effective_models = (Σw)² / (wᵀRw)`. Entscheide: `FORECAST`, `ABSTAIN` (Spannweite der Mittelpunkte > 0,30 oder Breite > 0,35 oder eine Abstention), `RE_RESEARCH` (fehlender Input, Jev inkohärent, Evidenz nicht datiert-primär oder nicht relevant). Schwellen sind vorregistrierte Konstanten; Änderung ist eine Promoter-Aktion mit Ledgereintrag. Runde 2 (adversariale Gegenprüfung) läuft nur für ABSTAIN-Items und erzeugt neue Prognose-IDs, nie Änderungen.

## 5. Modellrollen und Verträge

| Rolle | Claude Fable 5.1 | OpenAI (Astra-Klasse) | Gemini (Argon-Klasse) | Jev |
|---|---|---|---|---|
| Obligatorischer Runde-1-Output | Mechanismen + Zerlegung + Intervalle, tickerfrei | adversariale Rekonstruktion, Gegenbeispiele, Lean-Skizzen, Intervalle | alternative Zukünfte, Substitute, Wertschöpfung, Intervalle | Triage-noul-Paare, choice-Klassifikation, Duplikat-Clustering |
| Verboten | Runde-1-Output anderer Modelle lesen; Ticker vor Mechanismus | Broker-Orders | Broker-Orders | alles ausser Klassifikation; jegliche Broker- oder Kontodaten |
| Kalibrierung verfolgt | je Prognostiker, Horizont, Sektor, Quellenfamilie | gleich | gleich | je Fragetemplate; Komplement-Gap je Aufruf |
| Veto | jedes Modell darf ABSTAIN → Item geht in Runde 2 | gleich | gleich | Inkohärenz-Gap > 0,15 → RE_RESEARCH |

Adaptervertrag (anbieterunabhängig): `research(bundle) -> ResearchOutput` als typisiertes JSON gegen ein Schema validiert, drei Retries mit exponentiellem Backoff, harte Tages-Token-Deckel je Anbieter, Degradationsleiter {voll → günstigeres Modell für Runde 1 → Warteschlange}, und die Regel, dass ein **fehlender obligatorischer Pre-Trade-Input neue Orders einfriert** (Gate demotiert automatisch auf SIM_READ_ONLY). Die Prompts in `prompts/` bleiben die Runde-1-Instruktionen; sie MÜSSEN versioniert sein und ihr Hash wird in jeder Prognose festgehalten.

Jev-Einsatzregeln (aus RFC §6 übernommen und verschärft): hochvolumige Triage von Quellentyp, Ereignisrelevanz, Neuheitskandidaten, Duplikat-Clustering, Widerspruchsalarm, Eskalation; Head-to-Head-Vergleich gegen billige Regeln und ein kleines lokales Modell in vorregistrierter randomisierter Ablation; Kohärenzprojektion auf seine Ausgaben; Kalibrierung gegen ereignisspezifische empirische Ergebnisse, nicht gegen Vendor-Benchmarks. Jev DARF NIE allein Handelsgrössen bestimmen, 10x-Wahrscheinlichkeiten aus Narrativen schätzen, Lean-/Risikozertifikate überstimmen oder Instruktionen an Saxo weitergeben.

## 6. Wertschöpfung, Allokation, Risikolimits
Mathematik in `03/04`. Für jede These: Umsatz-, Margen-, Kapitalintensitäts- und Aktienzahlpfade unter dem Szenarioset; Gesamtrendite-Multiplikator R_k je Szenario nach geschätzter Verwässerung, nach Saxo-Kommissionen und Spread (aus Precheck `Cost`), nach FX (CHF/USD, Instrumentwährung) und nach einer vom Eigentümer gelieferten Steuerannahme. Ein grosser Markt ist keine grosse Rendite für heutige Aktionäre: das Modell MUSS das implizite Einstiegsmultiple und das erforderliche Endmultiple ausweisen.

## 7. Krisen- und Erholungspolitik
Vollständig in `03/06`. Grundsatz: vorlaufende, in Echtzeit bekannte Inputs; Hazard-Verteilung mit Kalibrierintervall statt "CRASH = JA"; Hysterese; Trennung von systemischem Risiko vor Verlusten, realisiertem Drawdown ohne Fundamentalverschlechterung, dauerhafter Thesenbeeinträchtigung und temporärer Liquiditätspanik.

## 8. Selbstverbesserungsschleife
Langlebigkeit über 25 Jahre, Modellwechsel und die Grenzen der Autonomie sind in `02/04` ausgeführt; dieser Abschnitt beschreibt den Mechanismus.
**Proposer** (jedes Modell, jederzeit) schlägt ein versioniertes Artefakt vor (Feature-Extraktor, Parser, Graph-Template, Exit-Regel, Prompt) mit vorregistrierter Behauptung und dem Holdout, das es verbessern soll. **Promoter** (separates OS-Konto, deterministisches Skript) bewertet auf hash-gepinnten eingefrorenen Holdouts (`holdouts/<name>.sha256` im Ledger gelistet), zeitverschobenen Holdouts, Shuffled-Label-Kontrollen und Canary-Ereignissen; akzeptiert nur, wenn der committete E-Prozess gegen den Amtsinhaber 1/α überschreitet (α = 0,05, ein Test je Artefakt) und keine Kontrolle verletzt ist; schreibt `promotion` oder `rejection` in den Ledger; behält Rollback. Alles Weitere in `04/03` Abschnitt 4.

## 9. Sicherheitsarchitektur
- Secrets: Saxo-App-Key/-Secret, Refresh-Tokens, Jev-Key, LLM-Keys im Windows Credential Manager (DPAPI) unter dem jeweiligen Konto; nie in `.env`-Dateien im Repo; nie im Prompt-Kontext; Redaktionsfilter auf allen LLM-gerichteten Texten (der Jev-Referenzadapter lehnt credential-ähnliche Strings ab).
- Ordersignierung: der Executor akzeptiert nur ein Zertifikat `{certificate_id, instrument, amount, limit, gate_state, ledger_head_hash, promoter_signature}`; er prüft Ledger-Anker und Gate erneut vor jedem Precheck; Research-Code kann das Executor-Modul nicht importieren (getrennte venv und Konto).
- Ledger-Verankerung: täglicher Anker an einen zweiten physischen Ort, den das Researcher-Konto nicht beschreiben kann (Cloud-Laufwerk des Eigentümers oder separate Maschine); monatliche Verifikation durch den Eigentümer von einer unabhängigen Maschine; optional externe Zeitstempelung (OpenTimestamps oder signierte Git-Tags; als Dienste UNVERIFIZIERT).
- Egress: Researcher-Allowlist = {api.anthropic.com, api.openai.com, generativelanguage.googleapis.com, api.typesafe.ai, Datenquellen}; Executor-Allowlist = {gateway.saxobank.com, sim.logonvalidation.net, live.logonvalidation.net}. Windows-Firewall-Regeln je Konto oder lokaler Proxy.
- Idempotenz: `ExternalReference = certificate_id`, frischer `x-request-id` je Versuch, kein Retry nach `TradeNotCompleted` ohne `/port`-Readback.
- Notfall: `Gate.demote()` über CLI und über einen Watchdog bei Heartbeat-Verlust aufrufbar; storniert selbst nichts (es existiert noch kein Storno-Code), blockiert aber alle neuen Prechecks/Orders.
- Audit: jeder HTTP-Aufruf an Saxo mit Body-Digest, Status, Latenz protokolliert, nie das Token.

## 10. Exakte Änderungen gegenüber v0.1

| Bereich | v0.1 | v0.2 |
|---|---|---|
| Prognoseobjekt | `BinaryThesis` Freitext | `EventSpec` + `Forecast` Register, ledgergestützt, Sperre vager Wörter |
| E-Prozess | `ChallengerEvidence(p_b, p_c, y)` | `CommittedEProcess.commit()/resolve()`, prädiktierbares λ, λ_max < 1, laufendes Maximum |
| Ledger | Hash-Kette | + `seq`, monotone Zeit, Anker mit HMAC, Bedrohungsmodell |
| Kohärenz | LP, Guard nur in einer Funktion | Guard in beiden; Eckpunkt nicht stromabwärts verwendet; Credal-Netz-Design ergänzt |
| Allokation | binäres Kelly, Einheitenfehler | Einheiten korrigiert; Szenario-Max-Min-Allokator mit Caps und Worst-Loss |
| Fusion | keine | korrelationsbewusste Gewichte, Abstention, Jev-Gating |
| Jev | TS-Skizze | typisierter Python-Adapter, schemaverifiziert, Komplement-Gap, Retries, Deckel |
| Saxo | Precheck mit `ManualOrder` und Freitext-Assettyp | Gate-Maschine, Whitelist, `ExternalReference`, `x-request-id`, Handelbarkeit aus Readback, tokensichere Fehler |
| Lean | unkompiliert, 3 triviale Theoreme | kompiliert auf gepinnter Toolchain; + 7 Lemmata, auf die Allokator und LP angewiesen sind |
| Evidenz | `http` ok, Digest ungeprüft | nur `https`, Digest-Helfer, Ingest-Log-Spezifikation |
| Tests | 11 | 31 |
