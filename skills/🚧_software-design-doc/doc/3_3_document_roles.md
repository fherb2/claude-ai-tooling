## 3.3 Dokumentrollen

Stand (2026-09-20): Rollensatz, Rolle `decisions`, Funktionsnamen und Markerposition sind entschieden (vormals Q-08 bis Q-11, siehe `status.md`). Rollen, Funktionen und ihre Zuordnung stehen vollständig in Kapitel 1.3.3; hier stehen die Form des Markers, die Herkunft der Namen und das Dreiersschema als Rollensatz.

### 3.3.1 Rollenmarker

Der Rollenmarker steht am Ende der Überschrift (entschieden am 2026-09-20): in eckigen Klammern das Präfix `DS` (document structure) und das englische Schlüsselwort der Rolle — `## Laufzeitsicht [DS:runtime]`. So bleibt er beim Rendern sichtbar und `grep`-bar und wandert beim Umsortieren mit seinem Abschnitt. Nummern, Dateinamen und die Sprache der Überschriften sind frei; nichts, was der Skill liest, hängt an ihnen (Vorgabe 2.3). Die Funktionen eines Abschnitts folgen aus seiner Rolle über die Tabelle in Kapitel 1.3.3; der Regelteil ist erweiterbar, indem er eine neue Rolle mit ihrer Funktion definiert.

### 3.3.2 Herkunft der Rollennamen

Die Inhaltsrollen folgen dem arc42-Schema; warum diese Quelle und nicht eine der drei anderen erwogenen, steht in Anhang B, Abschnitt B.3. Die deutschen Entsprechungen sind bei der Umsetzung gegen die deutsche arc42-Vorlage zu prüfen. Die fünf Rollen der Projektarbeit (`plan`, `status`, `concept`, `appendix`, `register`) haben keine arc42-Herkunft.

| Rolle | arc42 | deutsch (zu prüfen) |
|---|---|---|
| `goals` | 1 Introduction and Goals | Einführung und Ziele |
| `constraints` | 2 Constraints | Randbedingungen |
| `context` | 3 Context and Scope | Kontextabgrenzung |
| `strategy` | 4 Solution Strategy | Lösungsstrategie |
| `building-blocks` | 5 Building Block View | Bausteinsicht |
| `runtime` | 6 Runtime View | Laufzeitsicht |
| `deployment` | 7 Deployment View | Verteilungssicht |
| `crosscutting` | 8 Crosscutting Concepts | Querschnittliche Konzepte |
| `decisions` | 9 Architecture Decisions | Architekturentscheidungen |
| `quality` | 10 Quality Requirements | Qualitätsanforderungen |
| `risks` | 11 Risks and Technical Debt | Risiken und technische Schulden |
| `glossary` | 12 Glossary | Glossar |

### 3.3.3 Das Dreiersschema des Vorläufers als Rollensatz

Das Schema ist in Anhang A beschrieben. Segment 1 „Zusammenhänge" entspricht `goals`, `constraints`, `context`, `strategy`, `runtime` und `quality`; Segment 2 „Vorgaben" entspricht `crosscutting` und `constraints`; Segment 3 „Einheiten" entspricht `building-blocks` und `deployment`. Wer das Dreiersschema weiterführt, kennzeichnet seine drei Dateien mit den passenden Rollen; die Verkettungsregel („Dateireihenfolge ergibt ein gültiges Dokument") bleibt als Empfehlung.
