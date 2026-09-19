# Anhang B — Recherchen und Rechenmodell

Beurteilungsmaterial zum Vorhaben, nicht Teil der Festlegungen. Statuskennzeichnung: **belegt** = am Primärdokument oder am Verlagsabstract geprüft; **unbestätigt** = nur aus Suchzusammenfassungen oder Titeln.

## B.1 Fuzzy-Technik und LLM-Agenten (2026-09-16/17)

Anlass war die Überlegung, die Härteableitung durch eine Fuzzy-Inferenz in einem Skript rechnen zu lassen. Die Idee wurde zurückgestellt (Entscheidungsliste statt Fuzzy, Kapitel 3.1); die Recherche bleibt als Wissensstand.

**Am fertigen LLM (Inferenzzeit):** Eine kleine, seit 2024 wachsende Literatur koppelt ein eingefrorenes LLM mit einem externen Fuzzy-Inferenzsystem in drei Mustern: das LLM liefert Eingänge oder Konfidenzen und das FIS entscheidet (Lin et al. 2026, Applied Energy — LLM extrahiert Fuzzy-Regeln aus Dokumenten, FIS berechnet Eignungswerte; Zeng et al. 2026, IEEE TFS — unsichere Teilantworten, Fuzzy-Aggregation; alle belegt); das FIS als Regler um das LLM (Agrawal et al. 2026 — Mamdani-Router nur für unklare Anfragen; Wang et al. 2025, IEEE TFS — Fuzzy-Min-Max-Netz steuert Contrastive Decoding; belegt); das LLM erzeugt Regelbasen oder Fuzzy Cognitive Maps (Kosko-Gruppe 2025/26; Ioshchikhes et al. 2026; belegt). Ren 2026, Ocean Engineering (belegt) nennt „Skill" ein versioniertes Modul mit Fuzzy-Inferenz-Templates und expertengeprüften Gewichtsupdates. In der Literatur zu Agenten-Skills im Werkzeugsinn kommt „fuzzy" nicht vor (SoK Agentic Skills, Februar 2026, belegt); Aktivierung läuft über Retrieval, LLM-Routing und scharfe Prädikate. Die Arbeit, die „Fuzzy" nur als Prompt-Schema ohne Rechenkern umsetzt (Figueiredo 2025, belegt), ist die Variante, die dieses Vorhaben verworfen hat.

**Beim Training:** punktuell und klein. Fuzzy-Mengen als Annotationsdimensionen für Finetuning (Zheng et al. 2025; Du 2025; belegt), als Alignment-Ziel (Pan et al. 2026, AAAI — Probabilistic Fuzzy DPO; belegt), als Architektur (Oskin 2026 — Fuzzy-Operatoren in der FFN-Schicht bei 125M Parametern; Huang und Raza 2025; belegt), als graduelle Belohnung ohne mengentheoretischen Sinn (CrowdVLM-R1 2025, belegt). Kein Beleg für gezieltes Fähigkeitenlernen über Fuzzy-Technik.

**Zwei Befunde stützen den Entwurf:** LLMs sind selbst schlecht im Fuzzy-Schließen — der FRoG-Benchmark zeigt inverses Skalieren (belegt) —, und die Zählung auf Titelebene (OpenAlex, „fuzzy" und „language model" im Titel, 2020–2026) ergibt 127 Arbeiten mit Sprung 2024 → 2025.

**Nicht am Primärdokument geprüft:** Song et al. 2026, Expert Systems with Applications (LLM-Konfidenz → Fuzzy-Variablen → Selbstkorrektur; „uncertainty-aware fine-tuning"); Ahmed, Hagras et al. 2026, FUZZ-IEEE (Fuzzy-Attribution für LoRA); Zhang et al. 2025, Pattern Recognition Letters. Der Abruf über das Institutsnetz scheiterte an der Bot-Erkennung der Verlage, nicht an der Lizenz; die Dateien wären über den Browser des Entwicklers zu holen.

## B.2 Vorhandene Werkzeuge für IDs, Register und Lebenszyklus (2026-09-17)

Kein Werkzeug leistet die Kombination aus Prosa mit Inline-Markern, Attributregister, Härtelebenszyklus und Pflege durch den Agenten. Jede Komponente existiert einzeln:

| Werkzeug | Was es vormacht | Was ihm für dieses Vorhaben fehlt | Status |
|---|---|---|---|
| OpenFastTrace (Java) | IDs `req~name~1` in Markdown, Coverage-Tags im Code, `trace` meldet Ungedecktes und veraltete Verweise bei Revisionswechsel | Härte, Begründungen; Java-Laufzeit; Items als Blöcke in der Prosa | belegt (Demo, README) |
| Doorstop (Python) | Items als YAML-Dateien; Links tragen den Fingerabdruck des Elternteils; `review` meldet „suspect links"; `active: false` | Prosa lebt in den Items; eine Datei je Fakt | belegt |
| Sphinx-Needs | Needs mit ID, Status, Links; VSCode-Erweiterung | Sphinx-Build und RST | belegt (Abstract-Ebene) |
| ADR / MADR, adr-manager (VSCode) | Status „superseded by"; Lint der Abschnittsstruktur | eine Datei je Entscheidung; Prototyp | belegt |
| OpenSpec, Spec Kit, Kiro | Lebenszyklus von Änderungen (propose, apply, archive); Spezifikation als Wahrheit für Agenten | keine Fakten-IDs, kein Status je Aussage; die Taxonomie (arXiv 2606.04967) kennt Traceability nur als Mechanismus | belegt |
| Zylos Research, 06.09.2026 | Formatvertrag plus deterministischer, nur lesender Lint für LLM-gepflegte Dateien; ausdrücklich gegen LLM-Konsistenzprüfung | Forschungsnotiz | belegt |

Übernommen wurden Ideen: Fingerabdruck und „suspect link" (Doorstop), kaskadierende Meldung bei Änderung (OpenFastTrace), `superseded by` (ADR), Lint statt Erinnerung (Zylos). Einbettung wurde verworfen: Beide Tracing-Werkzeuge halten den Text im Item, dieses Vorhaben hält ihn in der Prosa; ihre Datenmodelle (Eltern-Kind-Hierarchie, Coverage-Stufen) bilden nicht auf die Härteregeln ab.

Für die Kantenrechnung: networkx bietet `single_source_dijkstra_path_length(G, source, cutoff, weight=funktion)` und `ego_graph(distance=…)` — genau die gewichtete Nachbarschaft (belegt, Doku 3.6.1). Textgraph-Bibliotheken (text2graphapi, PyTextRank) bauen Wort-Kookkurrenz-Graphen aus Rohtext; das ist die NLP-Schicht, die das Vorhaben ausschließt.

## B.3 Standards für Designdokumentation (2026-09-17)

Anlass war die Frage, woher die Namen der Inhaltsrollen kommen sollen (Kapitel 3.3.2).

**arc42** (belegt an arc42.org): zwölf Abschnitte — Introduction and Goals, Constraints, Context and Scope, Solution Strategy, Building Block View, Runtime View, Deployment View, Crosscutting Concepts, Architecture Decisions, Quality Requirements, Risks and Technical Debt, Glossary. Lizenz CC BY-SA 4.0, deutsche Fassung vorhanden. Identifikatoren je Aussage schreibt arc42 nicht vor.

**Google-Design-Docs** (unbestätigt, aus Sekundärquellen): Kontext und Umfang, Ziele und Nicht-Ziele, Entwurf, erwogene Alternativen, Querschnittsbelange; bewusst informell, kein fester Abschnittssatz.

**IEEE 1016 Software Design Description** (unbestätigt): Sichten `context`, `composition`, `logical`, `dependency`, `information`, `patterns use`, `interface`.

**ISO/IEC/IEEE 42010** (unbestätigt): definiert die Begriffe viewpoint, view und concern, schreibt aber keine Sichten vor.

**Diátaxis** betrifft Anwenderdokumentation und ist hier nicht einschlägig.

**Ergebnis:** arc42 ist die einzige der Quellen mit einem festen, benannten Abschnittssatz in beiden Sprachen und ohne Lizenzhürde — deshalb die Wahl. Die deutschen Entsprechungen in der Tabelle in 3.3.2 sind Modellwissen und bei der Umsetzung gegen die deutsche Vorlage zu prüfen.

## B.4 Hook-Dokumentation (2026-09-17)

Die Hook-Referenz von Claude Code wurde für Kapitel 3.7 gelesen. Belegt: Ereignisse `PreToolUse`, `PostToolUse`, `SessionStart` mit ihren Matchern; Feld `if` in der Syntax der Berechtigungsregeln; Exit 2 blockiert bei `PreToolUse`; `additionalContext` bei `PostToolUse`; Klartext auf stdout wird bei `SessionStart` Kontext; Hooks im Skill-Frontmatter gelten ab Aufruf für die Sitzung; Pfadplatzhalter `${CLAUDE_PROJECT_DIR}` und `${CLAUDE_PLUGIN_ROOT}`.

## B.5 Rechenmodell zur Größe der Kandidatenlisten

Synthetisches Modell, im Scratch der Sitzung gerechnet, nicht aufbewahrt; für die Probe neu aufzusetzen. Aufbau: acht Kapitel mit je vier Abschnitten zu je fünf Absätzen; Festlegungen zufällig verteilt; je Kapitel `relate`-Absätze, die je vier Festlegungen des Kapitels und mit 15 % Wahrscheinlichkeit je eine fremde zitieren. Kanten: gleicher Absatz 0,8; Mitzitat 0,7; gleicher Abschnitt 0,4; Nachbarabschnitt 0,2; gleiches Kapitel 0,05. Verglichen: Hops über Kanten ab 0,7 (Tiefe 1 und 2) und der beste Pfad als Produkt der Gewichte mit Dämpfung 0,7 je Hop und Abbruchschwelle.

| Festlegungen | Tiefe 1 (Median / p90) | Tiefe 2 | gewichtet, Abbruch 0,40 | gewichtet, Abbruch 0,25 |
|---|---|---|---|---|
| 40 | 4 / 7 | 7 / 11 | 4 / 7 | 4 / 8 |
| 120 | 4 / 8 | 14 / 22 | 4 / 8 | 10 / 17 |
| 300 | 5 / 9 | 22 / 38 | 5 / 9 | 23 / 33 |

Lesart und Grenzen: Tiefe 1 bleibt in jeder Dokugröße bei einer Handvoll; Tiefe 2 wächst mit der Doku; die gewichtete Variante ist ein stetiger Regler zwischen beiden. Ein erster Lauf ohne Dämpfung erreichte das ganze Dokument, weil Ketten aus Kanten mit Gewicht 1,0 nie abbrechen — daraus die Dämpfung. Das Modell kennt keine Relevanz der Kandidaten und keine echte Verteilung von Zitaten; es zeigt die Form der Skalierung, nicht ihre Werte in einer realen Doku. Der Einwand des Entwicklers gilt: Mit Nähe-Kanten wächst die Kantenzahl, und die Zahl der Entscheidungen hängt nicht nur an Kanten mit Gewicht 1,0.
