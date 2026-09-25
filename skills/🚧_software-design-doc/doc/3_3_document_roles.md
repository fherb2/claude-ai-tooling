## 3.3 Dokumentrollen

Stand (2026-09-20): Rollensatz, Rolle `decisions`, Funktionsnamen und Markerposition sind entschieden (vormals Q-08 bis Q-11, siehe `status.md`); die Absatzrolle kam am 2026-09-21 hinzu. Rollen, Funktionen und ihre Zuordnung stehen vollständig in Kapitel 1.3.3; hier stehen die Form des Markers, die Herkunft der Namen und das Dreiersschema als Rollensatz.

### 3.3.1 Rollenmarker

Der Rollenmarker steht in eckigen Klammern mit dem Präfix `DS` (document structure) und dem englischen Schlüsselwort der Rolle. Für einen Abschnitt steht er am Ende der Überschrift — `## Laufzeitsicht [DS:runtime]` — und gilt bis zur nächsten Überschrift gleicher oder höherer Ordnung, Unterabschnitte ohne eigene Rolle eingeschlossen. Für einen Rollenwechsel innerhalb eines Abschnitts steht er am Ende des Absatzes und gilt für diesen Absatz; feiner wird nicht gewechselt, ein Definitionsmarker am Satz geht der Rolle vor (Kapitel 1.3.3). So bleibt er beim Rendern sichtbar und `grep`-bar und wandert beim Umsortieren mit seinem Text (Position an der Überschrift entschieden am 2026-09-20, Absatzrolle ergänzt am 2026-09-21). Nummern, Dateinamen und die Sprache der Überschriften sind frei; nichts, was der Skill liest, hängt an ihnen (Vorgabe 2.3). Die Funktionen eines Abschnitts folgen aus seiner Rolle über die Tabelle in Kapitel 1.3.3; der Regelteil ist erweiterbar, indem er eine neue Rolle mit ihrer Funktion definiert.

**Befund B-11 (2026-09-25): Die Rollentabelle hat im ausgelieferten Skill kein Zuhause.** Sie ordnet jeder der siebzehn Rollen ihre Funktionen zu — `define`, `relate`, `global`, `nonbinding`, `plan`, `register` — und steht vollständig in Kapitel 1.3.3. Kapitel 1 wird aber nie Skilltext: In den Skill wandern 3.1, 3.2, 3.4, 3.5, 3.10 und 3.11 (siehe den Kopf von Kapitel 3), dieses Kapitel 3.3 nicht. Zur Laufzeit wird die Zuordnung an mindestens zwei Stellen gebraucht: Die Pflicht zum Zitatmarker hängt an der Funktion `relate` (Kapitel 3.2.2), und der Lint nimmt Abschnitte mit `nonbinding` und `register` von der Prüfung aus (Kapitel 3.6.6). Ohne die Tabelle kann der Skill diese beiden eigenen Regeln nicht anwenden. Zu entscheiden: wohin sie gehört. Naheliegend ist der Regelteil zu Markern und Register, weil dort beide Regeln stehen; denkbar wäre auch eine eigene nachgeladene Datei oder eine maschinenlesbare Fassung im Skript, das die Zuordnung ohnehin braucht. Das normative Zuhause bliebe in jedem Fall Kapitel 1.3.3, alles andere ist Kopie oder Ableitung.

### 3.3.2 Herkunft der Rollennamen

Die zwölf Rollen der Architekturbeschreibung folgen dem arc42-Schema; warum diese Quelle und nicht eine der drei anderen erwogenen, steht in Anhang B, Abschnitt B.3. Die deutschen Entsprechungen sind bei der Umsetzung gegen die deutsche arc42-Vorlage zu prüfen. Die fünf Rollen der Projektarbeit (`plan`, `status`, `concept`, `appendix`, `register`) haben keine arc42-Herkunft.

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
