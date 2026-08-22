# Skills für Claude Code

*[English version](README.en.md)*

Wiederverwendbare Skills für Claude Code, samt der Trigger, die sie auslösen. Dieses Verzeichnis ist die Quelle — hier werden die Skills entwickelt und gepflegt. Wirksam werden sie erst, wenn sie an ihren Zielort kopiert wurden (Kapitel 3).

## 1 Die Skills im Einzelnen


| Skill                                                                    | Zweck                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`common-code-generation/`](common-code-generation/README.de.md)<br>✅☑ | **Allgemeine Regeln der Zusammenarbeit und Ausführung des Erzeugens und Änderns von Code abseits von Code-Style-Regeln**: z.B.: kein ungefragt erweiterter Funktionsumfang, sparsamer Umgang mit Rechenzeit und Speicher                                                                                                             |
| [`parallel-sessions/`](parallel-sessions/README.md)<br>✅                | **Mehrere Claude-Instanzen gleichzeitig im selben Repository**: Arbeit mit oder ohne Worktree. Klärt die Zusammenarbeit, wenn mehrere Claude-Code-Instanzen gleichzeitig im selben Repository arbeiten. (noch ohne Worktree-Funktion)                                                                                                |
| [`software-dev-doc-fh/`](software-dev-doc-fh/README.md)<br>🚧            | **Dokumentationsstandard für die Planung vor der Kodierung und die laufende Mitschrift des Implementierten** — was umgesetzt wird, welche Festlegungen getroffen wurden und warum so und nicht anders. Softwareprojektbegleitende Dokumentation als Basis für Coding, Fehlersuche und späterer Schluss- und Anwenderdokumentation. |
| [`softwareaufgabe-erkennen/`](softwareaufgabe-erkennen/README.md)<br>🚧  | **Erkennen, dass eine Anfrage auf zu schreibende oder zu ändernde Software hinausläuft** — auch wenn sie Wörter wie „Code" oder „programmieren" nie benutzt. Bisher eine festgehaltene Idee samt Messergebnis, noch kein Skill.                                                                                                  |
| [`temp-debug-code/`](temp-debug-code/README.de.md)<br>✅☑               | **Eindeutige Kennzeichnung von Code, der nur für einen laufenden Debugging-Vorgang zugefügt oder geändert wird** — nicht für Debug-Code, der dauerhaft im Quelltext bleiben soll.                                                                                                                                                 |
| [`translation-task/`](translation-task/README.md)<br>🚧                  | **Übersetzung von Dokumenten mit softwareentwicklungsnahem Inhalt** — README-Dateien, Konzept- und Implementierungsdokumente, Anleitungen. Nicht auf eine Sprachrichtung festgelegt.                                                                                                                                                 |
| [`web-code-artefacts/`](web-code-artefacts/README.md)<br>🚧              | **Umgang mit Code-Artefakten im Web-Frontend**: wann Code als Artefakt entsteht und wann als Änderungsanweisung im Chat, und in welcher Form Änderungen an bereits übernommenem Code mitgeteilt werden.                                                                                                                             |

(✅ deutsche Fassung fertig und nutzbar · ☑ englische Fassung fertig und nutzbar · 🚧 in Arbeit · ⚠️ mit Vorbehalt)

## 2 Zweck

Dieses Vorhaben entwickelt und pflegt Skills zur allgemeinen Verwendung mit Claude — im Web und lokal, auf allen Ebenen von Nutzer bis Projekt.

Eingeführt und umgesetzt wird dabei ein Konzept der **stillen Trigger**, das auch schwächeren Modellen erlaubt, einen Skill sehr früh aus dem Kontext heraus zu starten.

Vorgaben für diesen Bereich `skills/` und Erkenntnisse aus den zugehörigen Messreihen stehen in `implementation_doku.md`. Diese README beschreibt nur das Ergebnis: Was es gibt und wie man es benutzt. Jedes Skill hat dazu noch ein eigenes README-File mit speziellen Hinweisen und dem jeweiligen Entwicklungszustand des Skills.

## 3 Skills beschaffen und installieren

Was Skills sind, wie sie aufgebaut sind und wie Claude Code sie lädt, beschreibt die offizielle Dokumentation: **[Extend Claude with skills](https://code.claude.com/docs/en/skills)**. Diese README setzt das als bekannt voraus.

**Was hier hinzukommt, sind stille Trigger:**

Die von Anthropic vorgesehene Technik löst einen Skill über seine `description` aus: Passt sie zur Anfrage, wird der Skill geladen. Das funktioniert gut, wenn der Nutzer etwas verlangt, das dem Skill offensichtlich entspricht. Es funktioniert nicht oder schlecht, wenn der Auslöser eine Beobachtung ist, die niemand im Chat ausspricht — etwa dass gerade eine zweite Claude-Instanz oder der Nutzer im selben Repository arbeitet, obwohl der Chat die Hoheit über Commits trägt. Für solche Fälle liegt für einen Skill ein zusätzlicher Absatz in der `CLAUDE.md` des Zielorts, der die Bedingung benennt und auf den Skill verweist. Er heißt in diesem Projekt **stiller Trigger**, weil ihn üblicherweise niemand explizit für eine Aufgabe aufruft und niemand sieht: Er wirkt aus dem Hintergrund im Denkvorgang der KI, ohne dass der Nutzer etwas davon merkt. Er soll gewährleisten, dass der Skill so früh wie möglich wirkt — auch dann, wenn die KI die Übereinstimmung zwischen seiner `description` und der aktuellen Aufgabe von sich aus für zu schwach hielte, um ihn zu laden.

Skills, die einen solchen Trigger brauchen, bringen dafür eine Datei `CLAUDE-snippet.md` in ihrem Ordner mit. Ihr Inhalt wird der `CLAUDE.md` derselben Ebene per Hand zugefügt.

**In welchen Sprachen ein Skill vorliegt, ist von Fall zu Fall verschieden.** Die meisten gibt es hier nur auf Deutsch; ihre Dateien heißen dann schlicht `SKILL.md`, `README.md` und `CLAUDE-snippet.md` und werden unverändert kopiert. Nur wo es mehrere Fassungen gibt, tragen sie ein Sprachkürzel vor der Endung — `SKILL.de.md` und `SKILL.en.md`, ebenso `README.de.md`/`README.en.md` und `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Dann wird genau **eine** Fassung installiert, und ihr Kürzel entfällt dabei: Claude Code erkennt ausschließlich den Namen `SKILL.md`. Welche Sprachvariante zu wählen ist, ergibt sich aus der Sprache im Chat, wobei die englische Fassung an sich gegenüber allen Chat-Sprachen kompatibel sein sollte.

Der Ordnername ist in allen Fassungen derselbe und trägt nie ein Kürzel; dasselbe gilt für den Skill-Namen im Frontmatter und damit für den Aufruf `/<skill-name>`.

### Installation

1. **Zielort (Wirkungsebene) wählen.** Ein Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:


   | Ort         | Pfad                                     | Gilt für                 |
   | ----------- | ---------------------------------------- | ------------------------- |
   | Persönlich | `~/.claude/skills/<skill-name>/SKILL.md` | alle Projekte des Nutzers |
   | Projekt     | `.claude/skills/<skill-name>/SKILL.md`   | nur dieses Projekt        |
2. **Skill-Ordner kopieren, gegebenenfalls Sprachfassung wählen.** Der Ordner hier hat bereits genau die Struktur des Zielorts. Kopiert wird er unter seinem unveränderten Namen. Gibt es von einer Datei mehrere Sprachfassungen, kommt nur die gewünschte mit, und ihr Sprachkürzel entfällt dabei: Aus `SKILL.de.md` wird am Zielort `SKILL.md`, damit Claude sie als das akzeptiert, was sie ist. Bleibt das Kürzel stehen, findet Claude Code den Skill möglicherweise nicht, da der Dateiname `SKILL.md` von Anthropic für Skills definiert wurde.
3. **Stillen Trigger übernehmen, falls vorhanden.** Liegt im Ordner eine `CLAUDE-snippet.md`, wird ihr Inhalt **unterhalb der Trennlinie** in die `CLAUDE.md` des Zielorts übernommen — bei einem persönlichen Skill in `~/.claude/CLAUDE.md`, bei einem Projekt-Skill in dessen `CLAUDE.md`. Der Text oberhalb der Trennlinie ist die Anleitung dazu und wird nicht mitkopiert. Danach wird die `CLAUDE-snippet.md` am Zielort gelöscht: Bliebe sie liegen, gäbe es den Trigger zweimal, und die Fassungen driften beim nächsten Anpassen auseinander.

Die `README.md` des Skills darf am Zielort liegen bleiben — sie ist zugleich seine Anwenderdokumentation und dort so nützlich wie hier.

Ohne Schritt 3 funktioniert der Skill weiterhin — aber nur, wenn er ausdrücklich mit `/<skill-name>` aufgerufen wird oder die KI an Hand der Description auf den Skill ausreichend aufmerksam geworden ist.

### Beim Anpassen eines Triggers

Drei Regeln — zwei davon aus Messungen und nicht aus Geschmack, die dritte aus Anthropics eigener Vorgabe:

**Die `description` des Skills entscheidet zuerst.** Sie beginnt mit dem Hauptanwendungsfall und benutzt die Wörter, die ein Nutzer von sich aus sagen würde. Wer dort eine Einordnung voranstellt („Testskill…", „Interne Fassung…") oder projektinterne Fachbegriffe verwendet, die in keiner Anfrage vorkommen, kann den Trigger unwirksam machen — gemessen: derselbe Trigger-Text feuerte mit guter Beschreibung, mit schwacher nicht.

**Ein Trigger sollte an ein Ereignis oder eine Handlung gebunden sein,** nicht bloß an eine Eigenschaft der Aufgabe. „Behalte im Blick, ob diese Aufgabe komplex ist" trägt sich nicht selbst; „bevor du zum ersten Mal eine Datei änderst, prüfe …" oder „taucht eine Datei auf, die du nicht angefasst hast, dann …" lösen zuverlässig aus. Die Messreihen dazu stehen in `implementation_doku.md`, Kapitel 3.

**Die `description` steht in der dritten Person.** Sie beschreibt den Skill — „Übersetzt Dokumente …", „Verwenden, sobald …" — und spricht niemanden an, weder Claude noch den Nutzer. Das ist keine Stilfrage: Die Beschreibung wird in den Systemprompt eingefügt, und ein wechselnder Blickwinkel stört dort die Auswahl unter vielen Skills. Anthropic sagt das ausdrücklich — *„Always write in third person […] inconsistent point-of-view can cause discovery problems"* ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## 4 Offene Punkte des Vorhabens

Was an einem einzelnen Skill offen ist, steht in dessen eigener `README.md` im Skill-Ordner.

Übergreifend offen ist:

- Die Neuordnung der Arbeitsanweisungen zu Skill-Zuhausen (Arbeitsmodell: `implementation_doku.md`, Kapitel 8).

**Nächster Schritt (Plan, noch nicht ausgeführt):** Die Posten des Anweisungs-Inventars (T1–T27; liegt in einem temporären Arbeitsordner, der nach Abschluss entfällt) werden einzeln zugeordnet. Claude reicht sie vorsortiert durch — gebündelt nach vorgeschlagenem Skill-Zuhause, je Posten mit Herkunft, Varianten und einem Geltungsbereichs-Vorschlag nach Kapitel 8.3 der `implementation_doku.md` (nur Coding / alle Arbeitsformen / andere) —, und der Entwickler legt je Posten die Zuordnung fest oder bestätigt sie. Maßstab der Verteilung ist das Arbeitsmodell in Kapitel 8.2. Die bestätigte Zuhause-Liste wird anschließend in der `implementation_doku.md` festgeschrieben; erst danach beginnt die Ausformulierung der einzelnen Skills.

## Lizenz

Alle Skills in diesem Verzeichnis stehen unter **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — der Verzicht auf alle Rechte, soweit gesetzlich möglich. Das bedeutet:

- **Nutzung ohne jede Bedingung** — privat, kommerziell, in geschlossenen wie in offenen Projekten.
- **Keine Namensnennung nötig.** Wer will, darf nennen; niemand muss.
- **Beliebig änderbar und weitergebbar**, auch in veränderter Form und unter anderem Namen.
- **Keine Pflicht, Änderungen offenzulegen** oder zurückzugeben.
- **Kein Lizenztext muss mitgegeben werden** — anders als bei MIT oder Apache-2.0, die beide Namensnennung und Mitgabe des Lizenztextes verlangen.
- **Keine Gewährleistung und keine Haftung.** Was diese Skills anrichten, verantwortet, wer sie einsetzt.

Anthropic macht keine Vorgaben zur Lizenzierung selbst geschriebener Skills, und das Skill-Format ist ein offener Standard ohne eigene Bedingungen. Anthropics eigenes Skills-Repository nutzt für die quelloffenen Skills Apache-2.0. CC0 ist hier also eine bewusste Wahl, keine Auflage — und die weitergehende: Apache-2.0 verlangt Namensnennung und Mitgabe des Lizenztextes, CC0 nicht.
