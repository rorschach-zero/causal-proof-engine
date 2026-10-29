# 01 Originalität, Stand der Forschung und konkurrierende Designs

## 1. Etabliert versus neu

| Komponente | Status | Referenz |
|---|---|---|
| Credal-Menge per LP über Weltzuständen | etabliert (probabilistische Logik, imprecise probability) | Nilsson 1986; Walley 1991 (Allgemeinwissen) |
| Implikation ⇒ Ordnung der Marginale | trivial; Lean-geprüft | `RiskBudget.lean` |
| Test-Supermartingal mit prädiktierbarem λ | etabliert | Ramdas et al. 2020, arXiv:2009.03167 (Titel verifiziert) |
| Fraktionales / robustes Kelly | etabliert | Kelly 1956; MacLean, Thorp, Ziemba 2010 (Allgemeinwissen) |
| Proper Scoring, Reliability-Diagramme | etabliert | Brier 1950; Gneiting und Raftery 2007 (Allgemeinwissen) |
| Safe Policy Improvement | etabliert mit Einschränkungen | Laroche et al. 2019; arXiv:2208.00724 (Titel verifiziert) |
| Bayesian Online Changepoint Detection | etabliert | arXiv:0710.3742 |
| Jev typisierte Entscheidungen | Vendor-Produkt (15.09.2026) mit unabhängigen Evaluationen | arXiv:2609.37647, 2609.33209 (Titel verifiziert) |
| **PCCB als typisiertes Objekt, das obige verbindet** | **neuartige Integrationshypothese, ungetestet** | RFC §0 |
| **Behauptung: kohärente, kausal zerlegte Multi-Modell-Prognosen verbessern Kalibrierung bei Vor-Trend-10x-Ereignissen** | **neu, ungetestet, auf 10x-Horizont in 12 Monaten nicht testbar** | dieses Review |

## 2. Ist irgendeine "kausale" Verknüpfung mehr als Korrelation oder Behauptung?

In v0.1: nein. Die Beispielkette des RFC (Regulierung → Zertifizierung → Kapazität → Gewinn → 10x) ist ein Narrativ mit Implikationen. Eine **strukturelle** Behauptung braucht: eine spezifizierte Intervention (was änderte sich, würde die Regulierung aufgehoben?), eine exogene Variationsquelle (gestaffelte Einführung über Jurisdiktionen, Gerichtsurteile, Zollschocks), die Annahmen über die beobachtete Welt (keine Antizipation, SUTVA über Firmen, keine gleichzeitige konfundierende Politik) und ein Ergebnis, das vor dem Preis messbar ist. Die Architektur macht die Identifikationsklasse zu einem Pflichtfeld und verbietet Klasse-`none`-Behauptungen in Wahrscheinlichkeitsconstraints (`02/01` Abschnitt 4.2).

Kritik in beide Richtungen, wie im Auftrag verlangt: flaches kausales Schliessen (LLM-Narrative als DAG) ist ebenso abzulehnen wie übervorsichtiges Trendfolgen (das per Konstruktion "gestrige Gewinner" findet) und wie unbegründete Extrembehauptungen nach oben. Der Weg dazwischen ist: Mechanismen als Hypothesengeneratoren, Ereignisse als Testobjekte, Preise als späte Information.

## 3. Zwei konkurrierende Designs für eine beweistragende, kohärente, Multi-Modell-Kausalwette, plus Baseline

**Design A, Credal-LP-Zertifikat (v0.1-Linie).** Marginalintervalle plus logische Constraints → LP-Machbarkeit und Schranken → Max-Min-Wachstum. Stärken: transparent, jeder Schritt zertifizierbar, Widerspruchserkennung. Schwächen: exponentiell in der Ereigniszahl, vakuöse Intervalle bei vielen lose beschränkten Ereignissen, ignoriert bedingte Struktur, lernt nicht.

**Design B, faktorisiertes Credal-Netz mit kalibrierten Blättern.** DAG über Ereignisse mit bedingten Wahrscheinlichkeitsintervallen je Kante von jedem Modell; Inferenz durch Monte Carlo über gezogene CPTs (günstig, skaliert auf Hunderte Knoten); Blätter gegen ein historisches Kohortenbasisratenmodell (Design C) über isotonische oder Platt-Karten kalibriert, die nur auf aufgelösten Ereignissen gelernt werden; konformale Intervalle am Ziel. Stärken: skaliert, nutzt bedingte Information, lernt Kalibrierung. Schwächen: Zertifizierung nur der finalen ≤ 14-Knoten-Projektion; Struktur muss elizitiert werden; Abhängigkeit zwischen CPT-Fehlern der Modelle muss in der Fusionsschicht modelliert werden.

**Design C, Basisraten-Hazard-Baseline (verpflichtender Konkurrent).** Kein Graph, kein LLM: Kohortenbasisraten von Meilenstein-Ereignissen und 10x-Ausgängen, bedingt auf beobachtbare Firmenmerkmale zum Stichtag, mit konformalen Prognoseintervallen.

| Kriterium | A: Credal-LP | B: Credal-Netz | C: Basisraten-Baseline |
|---|---|---|---|
| Skaliert auf Forschungsgraphen | nein (2^n) | ja | n/a |
| Nutzt bedingte Information | nein | ja | nein |
| In Lean zertifizierbar | ja (Schranken, Implikationen) | nur Projektion | nein |
| Lernt Kalibrierung | nein | ja (Blattkarten) | ja |
| Risiko vakuöser Intervalle | hoch bei n > 8 | mittel | niedrig |
| Rolle in v0.2 | Zertifikatsschicht | Forschungsmaschine | verpflichtende Baseline |

Empfehlung: **B als Forschungsmaschine, A als Zertifikatsschicht auf der entscheidungsrelevanten Projektion, C als Baseline, die geschlagen werden muss.** Auswahl nach 150 aufgelösten Ereignissen über Brier/Log-Skill und Intervallabdeckung, nicht über Neuheitsrhetorik; das unterlegene Design bleibt einen Zyklus als Ablationsarm, dann wird es stillgelegt.

Vergleich mit weiteren Alternativen aus dem Auftrag: einfache Bayes-Netze (Punkt-CPTs) sind ein Spezialfall von B mit Breite null und werden als Ablation geführt; dynamische Bayes-Netze lohnen sich erst, wenn Zeitreihenstruktur in den Ereignissen explizit modelliert wird (nicht im ersten Jahr); robuste Bayes-Verfahren entsprechen dem Credal-Ansatz; konformale Verfahren liefern die Intervalle in C und an den Blättern von B; Märkte und implizite Wahrscheinlichkeiten sind Baseline 2 in `04/03`, wo verfügbar; klassische Kausalinferenz-Baselines (Event Studies, Differenz-in-Differenzen) sind die Identifikationsklassen, keine Prognosemaschine.

## 4. Was Prognosen tragen müssen

Jede Prognose: Stichtag (`as_of`), Erstellzeit (`known_at`), exaktes Auflösungskriterium, Verfall, objektive Bewertungsregel. "10x-Potenzial" ist keine Prognose. Das Register erzwingt dies (`01/02` P0-SCI-01).

## 5. Sich verschiebende Welten, Finanzierungsregime, endogene Preise, Kontrafaktuale

- Regime als explizite Szenarioachsen im Allokator-Szenarioset (Zins-/Kreditregime × Thesenausgang), gewichtet aus dem Hazard-Modell.
- Thesen, deren Wertschöpfung von fortlaufender externer Finanzierung abhängt, werden als `financing_dependent` markiert und niedriger gedeckelt.
- Endogene Preisbildung: das System prognostiziert Ereignisse, nicht Preise; das Wertschöpfungsmodell weist Einstiegs- und erforderliches Endmultiple aus, sodass "der Markt hat es bereits eingepreist" eine messbare Grösse ist.
- Kontrafaktuale: Schattenbücher (`no_exit_shadow`, `entry_shadow`, `random_control`) und das Late-Exit-Audit.
