## 3.3 Dokumentrollen

Stand (2026-09-20): Rollensatz, Rolle `decisions`, Funktionsnamen und Markerposition sind entschieden (vormals Q-08 bis Q-11, siehe `status.md`); die Absatzrolle kam am 2026-09-21 hinzu. Rollen, Funktionen und ihre Zuordnung stehen vollständig in Kapitel 1.3.3; hier stehen die Form des Markers, die Herkunft der Namen und das Dreiersschema als Rollensatz.

### 3.3.1 Rollenmarker

Der Rollenmarker steht in eckigen Klammern mit dem Präfix `DS` (document structure) und dem englischen Schlüsselwort der Rolle. Für einen Abschnitt steht er am Ende der Überschrift — `## Laufzeitsicht [DS:runtime]` — und gilt bis zur nächsten Überschrift gleicher oder höherer Ordnung, Unterabschnitte ohne eigene Rolle eingeschlossen. Für einen Rollenwechsel innerhalb eines Abschnitts steht er am Ende des Absatzes und gilt für diesen Absatz; feiner wird nicht gewechselt, ein Definitionsmarker am Satz geht der Rolle vor (Kapitel 1.3.3). So bleibt er beim Rendern sichtbar und `grep`-bar und wandert beim Umsortieren mit seinem Text (Position an der Überschrift entschieden am 2026-09-20, Absatzrolle ergänzt am 2026-09-21). Nummern, Dateinamen und die Sprache der Überschriften sind frei; nichts, was der Skill liest, hängt an ihnen (Vorgabe 2.3). Die Funktionen eines Abschnitts folgen aus seiner Rolle über die Tabelle in Kapitel 1.3.3; der Regelteil ist erweiterbar, indem er eine neue Rolle mit ihrer Funktion definiert.

**B-11 erledigt (2026-10-04): Die Rollentabelle steht jetzt als Abschnitt 3 in `rules-core.de.md`, zweispaltig.** Der Befund war richtig — die Zuordnung Rolle auf Funktion wird zur Laufzeit gebraucht, denn die Pflicht zum Zitatmarker hängt an `relate`, die erhöhte Reibungsschwelle an `global`, und von der Markerprüfung ausgenommen sind `nonbinding` und `register`. Die drei Verweise, die dafür auf „Kapitel 1.3.3" zeigten und beim Nutzer ins Leere liefen, zeigen jetzt auf diesen Abschnitt.

Zwei Begründungen, die ich zwischenzeitlich für eine **eigene Datei** vorgebracht hatte, tragen nicht: dass mehrere Regelzweige die Tabelle gemeinsam bräuchten — das legt genau die Querverweise zwischen Zweigen nahe, die Vorgabe 2.15 ausschließt —, und dass eine eigene Datei Kontext spare, was sie nicht tut, weil die Tabelle in jeder Sitzung gebraucht wird. Mit dem Zusammenlegen der beiden Regelteile ist die Dateifrage ohnehin gegenstandslos geworden.

**Übernommen wurden nur zwei der drei Spalten.** Die Zuordnung Rolle auf Funktion kostet gemessen 161 Token, die vollständige Tabelle 725 — Faktor viereinhalb bei jedem Skillstart. Die mittlere Spalte, die beschreibt, worum es in einem Abschnitt der jeweiligen Rolle geht, trägt zu keiner Laufzeitregel bei; sie wird gebraucht, wenn die Instanz dem Entwickler eine Rolle **vorschlägt**, und das geschieht bei der Erstanlage oder im Plan. Wo sie im ausgelieferten Skill landet — `rules-startup.de.md` oder `rules-planning.de.md` —, ist noch offen und steht als Rest in Fahrplanschritt 10.

Das normative Zuhause bleibt Kapitel 1.3.3; was im Skilltext steht, ist Ableitung.

### 3.3.2 Kennung eines Bereichs

**Ein Abschnitt, auf den ein geplanter Schritt als Umbauziel zeigen soll, trägt eine stabile Kennung** (entschieden am 2026-10-02). Warum über eine Kennung und nicht über Datei und Überschrift adressiert wird, steht in Kapitel 1.7.3; hier steht die Form.

Die Kennung hängt im Rollenmarker hinter der Rolle, durch ein Leerzeichen getrennt: `## Die Pipeline [DS:building-blocks S-03]`. Das ist keine neue Markerart, sondern ein zweites Feld in einem vorhandenen — dieselbe Bauform wie im Register, wo hinter der ID Schlüsselwörter folgen. Der Buchstabe `S` steht für section; `D` gehört den Festlegungen, und eigene Kennungen für geplante Schritte sind verworfen (`rules-planning.de.md`), der Buchstabe ist also frei. Zweistellig genügt, weil Bereiche um Größenordnungen seltener sind als Festlegungen.

Vergeben wird sie vom Skript nach demselben Prinzip wie eine ID: nie neu vergeben, auch nicht nach dem Entfernen eines Abschnitts. Eine eigene Registerzeile braucht es nicht — der Marker im Text ist die Quelle, das Skript findet die vergebenen Kennungen mit einer Suche, und der Abgleich meldet Dubletten. Wer eine Kennung bekommt, bekommt auch seine Rolle ausgeschrieben; eine Kennung ohne Rolle gibt es nicht.

**Warum der Marker sichtbar bleibt und nicht in einem HTML-Kommentar steht** (geprüft am 2026-10-02 an einem CommonMark-Renderer). Ein Kommentar wäre für den Leser unsichtbar, solange der Renderer rohes HTML durchlässt. Tut er das nicht — viele schalten HTML aus Sicherheitsgründen ab —, wird der Kommentar maskiert und erscheint als Text, also auffälliger als die eckigen Klammern, und zwar gerade dort, wo niemand den Renderer kontrolliert. Dazu kommt das Risiko, dass ein Editor beim Speichern Kommentare wegräumt oder verschiebt. Der Gewinn beträfe ohnehin nur die gerenderte Ansicht, während der Entwickler im Quelltext arbeitet.

Ein Punkt spricht dennoch für die Kommentarform und ist hier festgehalten, falls die Probe ihn bestätigt: **die Sprungziele.** Aus einer Überschrift entsteht ein Anker aus ihrem Text; der sichtbare Marker wandert mit hinein — gemessen `#die-pipeline-dsbuilding-blocks-s-03` statt `#die-pipeline`. Wer in seiner Doku mit Links auf Überschriften arbeitet, bekommt unschöne und beim Rollenwechsel brechende Ziele. Ein Wechsel der Form wäre später möglich, ohne IDs, Register oder Auswirkungsrechnung zu berühren: Die Form steht im Regelteil, nicht im Mechanismus.

### 3.3.3 Herkunft der Rollennamen

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

### 3.3.4 Das Dreiersschema des Vorläufers als Rollensatz

Das Schema ist in Anhang A beschrieben. Segment 1 „Zusammenhänge" entspricht `goals`, `constraints`, `context`, `strategy`, `runtime` und `quality`; Segment 2 „Vorgaben" entspricht `crosscutting` und `constraints`; Segment 3 „Einheiten" entspricht `building-blocks` und `deployment`. Wer das Dreiersschema weiterführt, kennzeichnet seine drei Dateien mit den passenden Rollen; die Verkettungsregel („Dateireihenfolge ergibt ein gültiges Dokument") bleibt als Empfehlung.
