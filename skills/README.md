# Skills für Claude Code

*Stand: 2026-09-02*

*[English version](README.en.md)*

Wiederverwendbare Skills für Claude Code, claude.ai und Claude Desktop (Chat + Cowork), samt der Trigger, die sie auslösen. Dieses Verzeichnis ist die Quelle — hier werden die Skills entwickelt und gepflegt. Wirksam werden sie erst, wenn sie am Zielort installiert sind (Kapitel 3).

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
| [`chat-export/`](chat-export/README.md)<br>✅☑ | **Chats aus claude.ai in das laufende Projekt holen** — als durchsuchbare JSON-Dateien, über den angemeldeten Chrome oder aus einem Kontoexport-ZIP; auch Nachtragen bereits geholter Chats. Führt eine eigene Implementierungsdoku (siehe unten). |
| [`recall-skills-after-compact/`](recall-skills-after-compact/README.md)<br>✅☑ | **Nach jeder Kontext-Kompression an die zuvor geladenen Skills erinnern** — garantierte Fähigkeit mit Hook-Auslöser statt stillem Trigger: installiert wie ein Skill, verdrahtet über einen `settings.json`-Eintrag; zusätzlich auf Zuruf per `/recall-skills-after-compact`. |

(✅ deutsche Fassung fertig und nutzbar · ☑ englische Fassung fertig und nutzbar · 🚧 in Arbeit · ⚠️ mit Vorbehalt)

### chat-export weicht in zwei Punkten ab

**Er führt seine eigene Implementierungsdoku und seinen eigenen Fahrplan.** `implementation-doc.md` und `work-plan-v2.md` liegen in seinem Ordner, daneben der systematische Testweg zur Chrome-Anbindung und die Testsuite. Der Grund ist der Umfang: Dieser Skill ist erheblich komplexer als das Definieren einer `SKILL.md` — er bringt ein Werkzeug von 90 KB mit, das über zwei völlig verschiedene Datenquellen dasselbe Ergebnis liefern muss, und diese Zusage ist von einem eigenen Test bewacht. Das Entwicklungsmaterial reist nicht mit ins Installationspaket (Vorgaben, Kapitel 5).

**Und seine README trägt bewusst keinen Statushinweis**, nur die Bedienung: Was ein Nutzer kopiert, soll ihm sagen, wie es benutzt wird, und nicht, wie weit die Entwicklung ist. Der Stand steht deshalb hier.

**Stand:** Gebaut, an echten Daten in drei unabhängigen Sitzungen erprobt und einsetzbar — zuletzt an einem Großlauf über vier reale claude.ai-Projekte mit 171 Chats, dessen Ergebnis gegen die tatsächliche Export-ZIP verifiziert wurde: 171 von 171 gefunden, keine Abweichung. Beide Wege, Kontoexport und Web-Endpunkte, liefern nachweislich dasselbe Ergebnis. Am 22. August 2026 hat eine unabhängige Instanz die Logik gegen die Ziele der Doku geprüft; alle Befunde sind behoben.

**Offen:** Was diese Fassung nicht leistet, steht in `implementation-doc.md`, Kapitel 1.8 — kurz gefasst: ein Ordner je Quellprojekt, und dieser Ordner samt Protokoll ist der Zustand. Die nächste Ausbaustufe umreißt `work-plan-v2.md`, zwei Komplexe noch ohne Schritte. Für eine künftige Fassung vorgemerkt ist die Teilung der Anweisungsdatei; die Begründung samt Messwert steht in der Doku, Kapitel 3.3.

## 2 Zweck

Dieses Vorhaben entwickelt und pflegt Skills zur allgemeinen Verwendung mit Claude — im Web und lokal, auf allen Ebenen von Nutzer bis Projekt.

Eingeführt und umgesetzt wird dabei ein Konzept der **stillen Trigger**, das auch schwächeren Modellen erlaubt, einen Skill sehr früh aus dem Kontext heraus zu starten.

Dazu kommt bei manchen Skills eine **Zweiteilung**: Die `SKILL.md` klärt dann zuerst nur, ob der Skill überhaupt zur Anwendung kommt, und lädt den eigentlichen Regelteil erst bei Zustimmung aus einer zweiten Datei desselben Ordners nach. Ein Skill, der auf eine Lage auslöst, in der er oft doch nicht gebraucht wird, kostet so nur seine Klärungsseite statt seines ganzen Textes.

Vorgaben für diesen Bereich `skills/` und Erkenntnisse aus den zugehörigen Messreihen stehen in `skill-dev-doc.md`. Diese README beschreibt nur das Ergebnis: Was es gibt und wie man es benutzt. Jedes Skill hat dazu noch ein eigenes README-File mit speziellen Hinweisen und dem jeweiligen Entwicklungszustand des Skills.

## 3 Skills beschaffen und installieren

Was Skills sind, wie sie aufgebaut sind und wie Claude Code sie lädt, beschreibt die offizielle Dokumentation: **[Extend Claude with skills](https://code.claude.com/docs/en/skills)**. Diese README setzt das als bekannt voraus.

**Was hier hinzukommt, sind stille Trigger:**

Die von Anthropic vorgesehene Technik löst einen Skill über seine `description` aus: Passt sie zur Anfrage, wird der Skill geladen. Das funktioniert gut, wenn der Nutzer etwas verlangt, das dem Skill offensichtlich entspricht. Es funktioniert nicht oder schlecht, wenn der Auslöser eine Beobachtung ist, die niemand im Chat ausspricht — etwa dass gerade eine zweite Claude-Instanz oder der Nutzer im selben Repository arbeitet, obwohl der Chat die Hoheit über Commits trägt. Für solche Fälle liegt für einen Skill ein zusätzlicher Absatz in der `CLAUDE.md` des Zielorts, der die Bedingung benennt und auf den Skill verweist. Er heißt in diesem Projekt **stiller Trigger**, weil ihn üblicherweise niemand explizit für eine Aufgabe aufruft und niemand sieht: Er wirkt aus dem Hintergrund im Denkvorgang der KI, ohne dass der Nutzer etwas davon merkt. Er soll gewährleisten, dass der Skill so früh wie möglich wirkt — auch dann, wenn die KI die Übereinstimmung zwischen seiner `description` und der aktuellen Aufgabe von sich aus für zu schwach hielte, um ihn zu laden.

Skills, die einen solchen Trigger brauchen, bringen dafür eine `CLAUDE-snippet`-Datei mit; im Installationspaket heißt sie `CLAUDE-snippet.md`. Ihr Inhalt wird per Hand übernommen — das ist der einzige Schritt der Installation, den kein Paket abnehmen kann.

**In welchen Sprachen ein Skill vorliegt, ist von Fall zu Fall verschieden.** Wo es mehrere Fassungen gibt, tragen die Dateien hier im Repository ein Sprachkürzel vor der Endung — `SKILL.de.md`/`SKILL.en.md`, `rules.de.md`/`rules.en.md`. Welche davon mitkommt, entscheidet das gewählte Paket; die Umbenennung nach `SKILL.md`, die Claude Code voraussetzt, geschieht beim Packen. Die `README.md` bildet im Repository die Ausnahme: Bei mehreren Fassungen trägt nur die englische ein Kürzel (`README.en.md`); die deutsche heißt unverändert `README.md`, ganz ohne Kürzel — GitHub und GitLab zeigen beim Browsen eines Ordners automatisch nur eine Datei namens exakt `README.md` an, ein Sprachkürzel würde das verhindern (Näheres in `skill-dev-doc.md`, Kapitel 5.1). Welche Sprachvariante zu wählen ist, ergibt sich aus der Sprache im Chat, wobei die englische Fassung an sich gegenüber allen Chat-Sprachen kompatibel sein sollte.

Der Ordnername ist in allen Fassungen derselbe und trägt nie ein Kürzel; dasselbe gilt für den Skill-Namen im Frontmatter und damit für den Aufruf `/<skill-name>`.

### Installation

**Ein fertiger Skill wird als Archiv installiert, nicht als Ordner zusammenkopiert.** Die Archive liegen im Unterordner `downloads/` des jeweiligen Skills, eines je Sprache und Zielwelt:

| Name | Für |
| --- | --- |
| `<skill>_de_local.zip` | Claude Code, deutsche Fassung |
| `<skill>_de_web.zip` | claude.ai und Claude Desktop (Chat + Cowork), deutsche Fassung |
| `<skill>_en_local.zip` | Claude Code, englische Fassung |
| `<skill>_en_web.zip` | claude.ai und Claude Desktop (Chat + Cowork), englische Fassung |

Welche Kombinationen es für einen Skill überhaupt gibt, sagt der Vermerk hinter seinem Statushinweis; **die genauen Schritte stehen in seiner eigenen README.** Im Archiv liegt ein Ordner mit dem Namen des Skills, darin alle Dateien der gewählten Sprache — `SKILL.md`, `README.md`, gegebenenfalls nachgeladene Regeldateien, Skripte und `CLAUDE-snippet.md`. Das Aussortieren und Umbenennen, das früher Handarbeit war, nimmt das Paket ab.

**In Claude Code** wird das Archiv nach `~/.claude/skills/` entpackt — dann gilt der Skill für alle Projekte des Nutzers — oder nach `.claude/skills/` im Projekt, dann nur dort. **In claude.ai und Claude Desktop (Chat + Cowork)** wird es im dafür vorgesehenen Verwaltungsfeld für Skills hochgeladen und gilt danach für das Konto.

**Der stille Trigger bleibt Handarbeit.** Liegt im Paket eine `CLAUDE-snippet.md`, kommt **alles unterhalb der Trennlinie** in die `CLAUDE.md` des Zielorts beziehungsweise in das Anweisungsfeld der Anwendung. Der kursive Text darüber ist die Anleitung dazu und bleibt zurück; die Datei selbst bleibt liegen und ist das Vergleichsstück, an dessen Datumszeile sich später ablesen lässt, ob der übernommene Trigger noch dem Stand der Quelle entspricht.

Ohne diesen Schritt funktioniert der Skill weiterhin — aber nur, wenn er ausdrücklich mit `/<skill-name>` aufgerufen wird oder die KI an Hand der `description` auf ihn ausreichend aufmerksam geworden ist.

Die `README` des Skills liegt im Paket und gehört an den Zielort: Sie ist seine Anwenderdokumentation, und die `SKILL.md` darf bei Nachfragen für Begründungen auf sie verweisen — fehlt sie, fallen Antworten auf Warum-Fragen dünner aus.

**Nichts davon ist Dogma.** Die Installation ist Sache des Nutzers; Claude unterstützt sie, überwacht sie aber nicht. Weder wird ungefragt geprüft, ob eine Installation vollständig oder aktuell ist, noch, ob eine `CLAUDE.md` zum mitgelieferten Snippet passt. Geprüft und benannt wird nur, wenn der Nutzer es ausdrücklich verlangt.

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
