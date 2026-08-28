# Skills für Claude Code

*Stand: 2026-08-29*

*[English version](README.en.md)*

Wiederverwendbare Skills für Claude Code, samt der Trigger, die sie auslösen. Dieses Verzeichnis ist die Quelle — hier werden die Skills entwickelt und gepflegt. Wirksam werden sie erst, wenn sie an ihren Zielort kopiert wurden (Kapitel 3).

## 1 Die Skills im Einzelnen


| Skill                                                                    | Zweck                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`common-code-generation/`](common-code-generation/README.md)<br>✅☑ | **Allgemeine Regeln der Zusammenarbeit und Ausführung des Erzeugens und Änderns von Code abseits von Code-Style-Regeln**: z.B.: kein ungefragt erweiterter Funktionsumfang, sparsamer Umgang mit Rechenzeit und Speicher                                                                                                             |
| [`correct-zaaack-md-editor-mistakes/`](correct-zaaack-md-editor-mistakes/README.md)<br>✅☑ | **Beschädigten Leerraum in Markdown-Tabellen finden und beheben** — gefressene Leerzeichen vor Inline-Code oder Fettdruck und geschützte Leerzeichen, die jede Suche über den Wortlaut brechen, ohne sichtbar zu sein. Manche WYSIWYG-Editoren richten das beim Speichern an. |
| [`parallel-sessions/`](parallel-sessions/README.md)<br>✅☑ | **Mehrere Claude-Sitzungen gleichzeitig im selben Repository, getrennt über Git-Worktrees** — je Sitzung eine eigene Werkbank im eigenen Worktree, zentrale Dateien über einen Infra-Branch, Abschluss per Squash-Merge; ohne vereinbartes Modell als Rückfallweg die Klärung der Git-Schreibhoheit. |
| [`pedantic-text-editing/`](pedantic-text-editing/README.md)<br>✅☑ | **Textbearbeitung mit Detailtreue** — jede Änderung einzeln zur Freigabe, außerhalb der freigegebenen Stellen kein geändertes Zeichen, und hinterher der Nachweis über den Diff. Für Texte, deren Wortlaut selbst das Produkt ist; nicht für Quellcode und softwarebegleitende Dokumentation. |
| [`temp-debug-code/`](temp-debug-code/README.md)<br>✅☑               | **Eindeutige Kennzeichnung von Code, der nur für einen laufenden Debugging-Vorgang zugefügt oder geändert wird** — nicht für Debug-Code, der dauerhaft im Quelltext bleiben soll.                                                                                                                                                 |
| [`in-depth-online-literature-research/`](in-depth-online-literature-research/README.md)<br>✅☑ | **Gründliche Quellen- und Literaturrecherche, die nicht zu früh aufgibt** — systematischer Wechsel von Suchbegriffen, Kanälen und Suchebenen, Verifikationspflicht für jede Suchzusammenfassung, und statt „nichts gefunden“ ein Bericht über die noch offenen Suchwege. |
| [`🚧_software-dev-doc-fh/`](🚧_software-dev-doc-fh/README.md)            | **Dokumentationsstandard für die Planung vor der Kodierung und die laufende Mitschrift des Implementierten** — was umgesetzt wird, welche Festlegungen getroffen wurden und warum so und nicht anders. Softwareprojektbegleitende Dokumentation als Basis für Coding, Fehlersuche und späterer Schluss- und Anwenderdokumentation. |
| [`🚧_software-task-detection/`](🚧_software-task-detection/README.md)  | **Erkennen, dass eine Anfrage auf zu schreibende oder zu ändernde Software hinausläuft** — auch wenn sie Wörter wie „Code“ oder „programmieren“ nie benutzt. Bisher eine festgehaltene Idee samt Messergebnis, noch kein Skill.                                                                                                  |
| [`🚧_translation-task/`](🚧_translation-task/README.md)                  | **Übersetzung von Dokumenten mit softwareentwicklungsnahem Inhalt** — README-Dateien, Konzept- und Implementierungsdokumente, Anleitungen. Nicht auf eine Sprachrichtung festgelegt.                                                                                                                                                 |
| [`web-code-editing/`](web-code-editing/README.md)<br>✅☑ | **Code-Bearbeitung auf claude.ai**: Quellen vollständig sichern (Projektwissen liegt als Dateien unter `/mnt/project/`), geänderte Dateien mechanisch als Download zurückgeben statt sie neu zu diktieren, kleine Änderungen als Vorher/Ersetzen-Schema im Chat. Nur für claude.ai.                                                                                                                             |
| [`🚧_zotero-use/`](🚧_zotero-use/README.md) | **Claude direkt an die eigene Zotero-Bibliothek anbinden** — neue Einträge samt PDF anlegen, gezielt in Metadaten und Volltext suchen, Sammlungen verwalten. Bisher eine festgehaltene Idee samt recherchierter Architektur, noch kein Skill. |

(✅ deutsche Fassung fertig und nutzbar · ☑ englische Fassung fertig und nutzbar · 🚧 in Arbeit · ⚠️ mit Vorbehalt)

## 2 Zweck

Dieses Vorhaben entwickelt und pflegt Skills zur allgemeinen Verwendung mit Claude — im Web und lokal, auf allen Ebenen von Nutzer bis Projekt.

Eingeführt und umgesetzt wird dabei ein Konzept der **stillen Trigger**, das auch schwächeren Modellen erlaubt, einen Skill sehr früh aus dem Kontext heraus zu starten.

Dazu kommt bei manchen Skills eine **Zweiteilung**: Die `SKILL.md` klärt dann zuerst nur, ob der Skill überhaupt zur Anwendung kommt, und lädt den eigentlichen Regelteil erst bei Zustimmung aus einer zweiten Datei desselben Ordners nach. Ein Skill, der auf eine Lage auslöst, in der er oft doch nicht gebraucht wird, kostet so nur seine Klärungsseite statt seines ganzen Textes.

Vorgaben für diesen Bereich `skills/` und Erkenntnisse aus den zugehörigen Messreihen stehen in `skill-dev-doc.md`. Diese README beschreibt nur das Ergebnis: Was es gibt und wie man es benutzt. Jedes Skill hat dazu noch ein eigenes README-File mit speziellen Hinweisen und dem jeweiligen Entwicklungszustand des Skills.

## 3 Skills beschaffen und installieren

Was Skills sind, wie sie aufgebaut sind und wie Claude Code sie lädt, beschreibt die offizielle Dokumentation: **[Extend Claude with skills](https://code.claude.com/docs/en/skills)**. Diese README setzt das als bekannt voraus.

**Was hier hinzukommt, sind stille Trigger:**

Die von Anthropic vorgesehene Technik löst einen Skill über seine `description` aus: Passt sie zur Anfrage, wird der Skill geladen. Das funktioniert gut, wenn der Nutzer etwas verlangt, das dem Skill offensichtlich entspricht. Es funktioniert nicht oder schlecht, wenn der Auslöser eine Beobachtung ist, die niemand im Chat ausspricht — etwa dass gerade eine zweite Claude-Instanz oder der Nutzer im selben Repository arbeitet, obwohl der Chat die Hoheit über Commits trägt. Für solche Fälle liegt für einen Skill ein zusätzlicher Absatz in der `CLAUDE.md` des Zielorts, der die Bedingung benennt und auf den Skill verweist. Er heißt in diesem Projekt **stiller Trigger**, weil ihn üblicherweise niemand explizit für eine Aufgabe aufruft und niemand sieht: Er wirkt aus dem Hintergrund im Denkvorgang der KI, ohne dass der Nutzer etwas davon merkt. Er soll gewährleisten, dass der Skill so früh wie möglich wirkt — auch dann, wenn die KI die Übereinstimmung zwischen seiner `description` und der aktuellen Aufgabe von sich aus für zu schwach hielte, um ihn zu laden.

Skills, die einen solchen Trigger brauchen, bringen dafür eine Datei `CLAUDE-snippet.md` in ihrem Ordner mit. Ihr Inhalt wird der `CLAUDE.md` derselben Ebene per Hand zugefügt.

**In welchen Sprachen ein Skill vorliegt, ist von Fall zu Fall verschieden.** Die meisten gibt es hier nur auf Deutsch; ihre Dateien tragen dann kein Sprachkürzel und werden unverändert kopiert. Nur wo es mehrere Fassungen gibt, tragen `SKILL.md` und `CLAUDE-snippet.md` ein Sprachkürzel vor der Endung — `SKILL.de.md`/`SKILL.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Installiert wird dann genau eine Sprachversion, und die gewählte SKILL-Fassung heißt am Zielort `SKILL.md` — ob umbenannt oder zusätzlich abgelegt, ist gleichgültig; Claude Code erkennt ausschließlich diesen Namen. Die `README.md` bildet die Ausnahme: Bei mehreren Fassungen trägt nur die englische ein Kürzel (`README.en.md`); die deutsche heißt unverändert `README.md`, ganz ohne Kürzel — GitHub und GitLab zeigen beim Browsen eines Ordners automatisch nur eine Datei namens exakt `README.md` an, ein Sprachkürzel würde das verhindern (Näheres in `skill-dev-doc.md`, Kapitel 5.1). Welche Sprachvariante zu wählen ist, ergibt sich aus der Sprache im Chat, wobei die englische Fassung an sich gegenüber allen Chat-Sprachen kompatibel sein sollte.

Der Ordnername ist in allen Fassungen derselbe und trägt nie ein Kürzel; dasselbe gilt für den Skill-Namen im Frontmatter und damit für den Aufruf `/<skill-name>`.

### Installation

1. **Zielort (Wirkungsebene) wählen.** Ein Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:


   | Ort         | Pfad                                     | Gilt für                 |
   | ----------- | ---------------------------------------- | ------------------------- |
   | Persönlich | `~/.claude/skills/<skill-name>/SKILL.md` | alle Projekte des Nutzers |
   | Projekt     | `.claude/skills/<skill-name>/SKILL.md`   | nur dieses Projekt        |
2. **Den Ordner kopieren — alle Dateien.** Er hat hier bereits genau die Struktur des Zielorts und behält seinen Namen. Dateien einer anderen Sprache müssen nicht mit; alles Übrige gehört dazu, denn ein Skill kann mehr enthalten als `SKILL`, `README` und `CLAUDE-snippet` — etwa einen nachgeladenen Regelteil oder ein Skript, ohne das er nicht arbeitet. Die Datumszeilen der mitkopierten Dateien zeigen später, von welchem Stand die Installation ist. **Danach die SKILL-Datei der gewählten Sprache nach `SKILL.md` umbenennen:** Exakt diesen Namen setzt Claude Code voraus, eine `SKILL.de.md` für sich ist kein Skill. Statt umzubenennen darf sie auch zusätzlich unter diesem Namen liegen; ebenso darf eine `README.en.md` bei englischer Installation zu `README.md` werden. Alle übrigen Dateien behalten ihren Namen — die `SKILL.md` verweist auf sie, und ein umbenannter Regelteil wird nicht mehr gefunden.
3. **Stillen Trigger übernehmen, falls vorhanden.** Liegt im Ordner eine `CLAUDE-snippet`-Datei, wird ihr Inhalt **unterhalb der Trennlinie** in die `CLAUDE.md` des Zielorts übernommen — bei einem persönlichen Skill in `~/.claude/CLAUDE.md`, bei einem Projekt-Skill in dessen `CLAUDE.md`. Der Text oberhalb der Trennlinie ist die Anleitung dazu und wird nicht mitkopiert. Die Snippet-Datei selbst bleibt am Zielort liegen — in der Sprache, in der ihr Inhalt übernommen wurde: Wirksam ist allein die `CLAUDE.md`, die Datei daneben ist das Vergleichsstück, an dem sich später ablesen lässt, ob der übernommene Trigger noch dem Stand der Quelle entspricht.

Die `README` des Skills gehört mit an den Zielort: Sie ist seine Anwenderdokumentation, und die `SKILL.md` darf bei Nachfragen für Begründungen auf sie verweisen — fehlt sie, fallen Antworten auf Warum-Fragen dünner aus.

**Nichts davon ist Dogma.** Die Installation ist Sache des Nutzers; Claude unterstützt sie, überwacht sie aber nicht. Weder wird ungefragt geprüft, ob eine Installation vollständig oder aktuell ist, noch, ob eine `CLAUDE.md` zum mitgelieferten Snippet passt. Geprüft und benannt wird nur, wenn der Nutzer es ausdrücklich verlangt.

Ohne Schritt 3 funktioniert der Skill weiterhin — aber nur, wenn er ausdrücklich mit `/<skill-name>` aufgerufen wird oder die KI an Hand der Description auf den Skill ausreichend aufmerksam geworden ist.

### Beim Anpassen eines Triggers

Drei Regeln — zwei davon aus Messungen und nicht aus Geschmack, die dritte aus Anthropics eigener Vorgabe:

**Die `description` des Skills entscheidet zuerst.** Sie beginnt mit dem Hauptanwendungsfall und benutzt die Wörter, die ein Nutzer von sich aus sagen würde. Wer dort eine Einordnung voranstellt („Testskill…“, „Interne Fassung…“) oder projektinterne Fachbegriffe verwendet, die in keiner Anfrage vorkommen, kann den Trigger unwirksam machen — gemessen: derselbe Trigger-Text feuerte mit guter Beschreibung, mit schwacher nicht.

**Ein Trigger sollte an ein Ereignis oder eine Handlung gebunden sein,** nicht bloß an eine Eigenschaft der Aufgabe. „Behalte im Blick, ob diese Aufgabe komplex ist“ trägt sich nicht selbst; „bevor du zum ersten Mal eine Datei änderst, prüfe …“ oder „taucht eine Datei auf, die du nicht angefasst hast, dann …“ lösen zuverlässig aus. Die Messreihen dazu stehen in `skill-dev-doc.md`, Kapitel 3.

**Die `description` steht in der dritten Person.** Sie beschreibt den Skill — „Übersetzt Dokumente …“, „Verwenden, sobald …“ — und spricht niemanden an, weder Claude noch den Nutzer. Das ist keine Stilfrage: Die Beschreibung wird in den Systemprompt eingefügt, und ein wechselnder Blickwinkel stört dort die Auswahl unter vielen Skills. Anthropic sagt das ausdrücklich — *„Always write in third person […] inconsistent point-of-view can cause discovery problems“* ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## 4 Offene Punkte des Vorhabens

Die anstehenden Schritte samt ihrer Reihenfolge stehen im **[Fahrplan](../work-plan.md)**. Was an einem einzelnen Skill fertig ist — und was dort zwar geplant, aber noch nicht auf der Tagesordnung ist —, steht in dessen eigener `README.md` im Skill-Ordner.

## Lizenz

Alle Skills in diesem Verzeichnis stehen unter **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — der Verzicht auf alle Rechte, soweit gesetzlich möglich. Das bedeutet:

- **Nutzung ohne jede Bedingung** — privat, kommerziell, in geschlossenen wie in offenen Projekten.
- **Keine Namensnennung nötig.** Wer will, darf nennen; niemand muss.
- **Beliebig änderbar und weitergebbar**, auch in veränderter Form und unter anderem Namen.
- **Keine Pflicht, Änderungen offenzulegen** oder zurückzugeben.
- **Kein Lizenztext muss mitgegeben werden** — anders als bei MIT oder Apache-2.0, die beide Namensnennung und Mitgabe des Lizenztextes verlangen.
- **Keine Gewährleistung und keine Haftung.** Was diese Skills anrichten, verantwortet, wer sie einsetzt.

Anthropic macht keine Vorgaben zur Lizenzierung selbst geschriebener Skills, und das Skill-Format ist ein offener Standard ohne eigene Bedingungen. Anthropics eigenes Skills-Repository nutzt für die quelloffenen Skills Apache-2.0. CC0 ist hier also eine bewusste Wahl, keine Auflage — und die weitergehende: Apache-2.0 verlangt Namensnennung und Mitgabe des Lizenztextes, CC0 nicht.
