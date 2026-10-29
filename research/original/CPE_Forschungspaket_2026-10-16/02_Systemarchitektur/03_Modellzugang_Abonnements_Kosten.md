# 03 Modellzugang, Abonnements und Kosten

**Vorgabe des Eigentümers (16.10.2026):** Das System wird mit seinen bestehenden Abonnements betrieben. Kosten so niedrig wie möglich: nur die Abos, Jev, und was zwingend nötig ist. Keine Scraping-Sitzungen, keine Umgehung von Produktkontrollen, keine Annahme, dass ein Consumer-Abo eine API gewährt. Dieses Kapitel ersetzt Abschnitt 8 von `08_Anhang/Original_Review_EN/CLAUDE_REVIEW.md`, der noch mit einem gemischten Abo-plus-Metering-Budget rechnete. Alle Angaben gelesen am 16.10.2026; Preise sind Planungsgrössen.

## 1. Betriebsmodell je Anbieter

| Modell | Betrieb | Verifizierter Stand | Monatskosten |
|---|---|---|---|
| Claude | Unbeaufsichtigt. Monatliche Claude-Platform-API-Credits des Max-Plans über Agent SDK oder Messages API; `claude -p` zusätzlich gegen das Abo-Limit | Max 5x 100 USD, Max 20x 200 USD Credits pro Monat; nutzbar für Messages API, Batches API, Agent SDK, Managed Agents; nicht für interaktives Claude Code; kein Rollover; 7 Tage Wartefrist; ein Plan je Console-Organisation (Artikel 17154008, Update 07.10.2026; Artikel 15036540) | 0 USD über den Max-Plan hinaus, solange das Volumen im Credit bleibt |
| Gemini | Unbeaufsichtigt, soweit die Nutzungsbedingungen am Einrichtungstag dies decken; sonst eigentümergestarteter Batch | Google AI Pro 1'500 Anfragen/Tag, Ultra 2'000/Tag für persönliche Konten (geminicli.com); Headless-Nutzung nicht adressiert; Hinweis "Gemini CLI was replaced by Antigravity CLI on June 18th, 2026" für Unpaid und Google One, Wirkung auf AI Pro UNVERIFIZIERT | 0 USD über AI Pro hinaus |
| OpenAI | **Eigentümergestarteter täglicher Batch** (ein Befehl, interaktive Codex-Sitzung, Ergebnisse gehen ins Register). Kein unbeaufsichtigtes `codex exec` unter persönlichem Login | Codex in Plus/Pro enthalten; API-Key wird "for programmatic Codex CLI workflows, such as CI/CD" genannt; "access tokens for trusted automation" nur in Enterprise-Workspaces (learn.chatgpt.com/docs/auth, /docs/pricing); Pro "currently have no five-hour limit" | 0 USD über Plus/Pro hinaus |
| Jev | API-Key, Early Access über Warteliste | 0,042 USD je Million Input-Tokens, Output kostenlos (Vendor-Blog 15.09.2026); Rate-Limits nicht genannt | bei 0,4 Mio. Tokens/Tag (200 Dokumente) rund 0,50 USD; bei 2 Mrd. Tokens/Monat rund 84 USD |

Konsequenz für die Dreier-Pflicht: Sie bleibt erfüllt, nur nicht vollautomatisch. Ein Item erhält erst dann eine Prognose, wenn alle drei Runde-1-Outputs vorliegen; OpenAI-Items warten bis zum nächsten Batch. Das verzögert Prognosen um maximal einen Tag, was bei Horizonten von 1 bis 9 Monaten unerheblich ist. Fällt der OpenAI-Batch an einem Tag aus, wird nichts mit zwei Modellen entschieden; die Items bleiben in der Warteschlange.

## 2. Was zwingend nötig ist und was nicht

Zwingend: die drei Abos (Max, ChatGPT Plus oder Pro, Google AI Pro), ein Jev-Key, Python und Lean (kostenlos), Saxo SIM (kostenlos), ein Speicherort für Ledger-Anker ausserhalb des Research-Kontos (ein vorhandenes Cloud-Laufwerk genügt).

Nicht nötig im ersten Jahr: metered API-Budgets, lizenzierte Point-in-Time-Datensätze (Q5 wird auf "Vorwärtsrekonstruktion aus Saxo-`/ref`-Snapshots" gesetzt; der historische Wald-Audit verschiebt sich, bis kostenlose oder ohnehin vorhandene Daten gefunden sind), Streaming-Marktdaten (SIM liefert keine; Quotes kommen aus Readbacks), zusätzliche Hardware (die RTX 5090 übernimmt den lokalen Klassifikator, Embeddings, Monte Carlo).

Reihenfolge der Abo-Stufen: Zuerst mit den vorhandenen Stufen starten und das Volumen im ersten Monat messen. Ein Upgrade (Max 5x auf 20x, Plus auf Pro) nur, wenn die Limits nachweislich die 600 Ereignisse pro Jahr verhindern, und nur eines zur Zeit.

## 3. Budget

Reine Abo-Kosten, die der Eigentümer ohnehin trägt, plus Jev unter 100 USD pro Monat (realistisch unter 10 USD bei 200 Dokumenten pro Tag). Zusätzliche Kosten im ersten Jahr: 0 USD geplant. Jede Abweichung davon (ein API-Key, ein Datensatz, ein Dienst) ist ein Eigentümerentscheid mit Ledgereintrag, nie eine Automatikentscheidung.

## 4. Auslegung auf Limits statt auf Geld

Mit Abos ist die Grenze nicht das Budget, sondern das Tages- und Fünf-Stunden-Kontingent. Darum:
1. Jev sortiert alles vor; die drei Modelle sehen nur Items, die Jev als datierte, relevante Primärevidenz einstuft.
2. Runde 2 (adversariale Gegenprüfung) läuft nur bei ABSTAIN, nicht standardmässig.
3. Realistisches Ziel: 5 bis 10 vollständige Forschungsrunden pro Tag, nicht 20. Das reicht für 600 registrierte Ereignisse im ersten Jahr.
4. Günstigere Modellvarianten desselben Anbieters für Runde 1, die Frontier-Variante für Runde 2 und für Sicherheitsreviews.
5. Harte Tages-Deckel je Anbieter im Adapter; Budgetalarm bei 80 Prozent des Claude-Credits; bei Erreichen eines Limits wird die Forschung gebremst, nie eine Prognose mit weniger als drei Modellen erzeugt.
6. Jev-Deckel in Tokens; bei Erreichen Pipeline-Stopp, kein stilles Weiterlaufen ohne Jev.

## 5. Dauerhafte Regel zu Nutzungsbedingungen

Die Bedingungen der Anbieter ändern sich häufig. Am Einrichtungstag und danach quartalsweise werden die Terms-Seiten gelesen und datierte Screenshots im Ledger abgelegt. Erlaubt ein Anbieter unbeaufsichtigte Nutzung ausdrücklich, wird der eigentümergestartete Batch für ihn aufgehoben; wird sie ausdrücklich untersagt, wechselt der Anbieter in den Batch. Nie wird eine Consumer-Web-Oberfläche automatisiert.

## 6. Lokale Hardware (RTX 5090)

Sinnvoller Einsatz: der `−Jev`-Ablationsarm (lokaler 7B- bis 14B-Klassifikator bei gleichem Recall-Budget), Embedding-basiertes Duplikat-Clustering, Parser und Extraktion, Monte-Carlo-Inferenz im Credal-Netz, Backtests. Nicht sinnvoll: Ersatz der drei Frontier-Modelle für Runde 1 oder 2, da die Unabhängigkeitsannahme des Komitees sonst entfällt.
