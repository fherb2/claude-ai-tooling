# Fahrplan des Repositories

Die anstehenden Schritte in der Reihenfolge ihrer Bearbeitung. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben, neue Schritte zählen hoch.

**Dieser Fahrplan gilt repository-weit.** Er lag bis zum 27. August 2026 in `skills/`, weil die Arbeit dort begann; seine Schritte betrafen aber längst alle Bereiche (zuletzt die Dateinamen-Prüfung und die Zielwelt-Sortierung). Vorhaben mit eigenem, abgegrenztem Entwicklungsstand führen daneben weiter ihren eigenen: `chat-export/work-plan-v2.md` und `home-.claude-sharing/work-plan.md`.

Was hier **nicht** steht: der Zustand eines Skills oder Bereichs und alles, was zwar geplant, aber noch nicht auf der Tagesordnung ist. Beides trägt die `README.md` des jeweiligen Skills bzw. Bereichs. Der Fahrplan gibt die Folgeschritte der Projektbearbeitung vor, keine Zukunftsvisionen.

Eine `status.md` führt das Vorhaben `skills/` nicht.

Die Nummern sind Kennungen, keine Reihenfolge: Maßgeblich ist, in welcher Folge die Schritte hier stehen. Schritt 14 steht bewusst vorn — Schritt 3 arbeitet mit dem Inventar, das dort erst wiederhergestellt wird. Ab Schritt 3 ist die Folge dann nicht mehr festgelegt; diese Schritte hängen nicht voneinander ab.

## 14 Die Beschneidung des Anweisungs-Inventars zurücknehmen

**Dies ist der ausgearbeitete Plan des nächsten Schritts; er ist noch nicht ausgeführt.**

Am 27. und 28. August 2026 wurden erledigte Inventarposten aus der `INVENTAR.md` **und** aus den Quelldateien gelöscht. Der Entwickler hat dieses Vorgehen am 29. August 2026 als Fehleinschätzung verworfen: Das Belegmaterial bleibt vollständig, und Erledigtes wird nicht entfernt, sondern in ein eigenes Kapitel verschoben. Betroffen sind acht Posten — T2, T8, T9, T10, T11, T12, T13 und T16 — sowie die Passagen der Quelldateien, auf die ihre Fundstellenangaben zeigen. Die Nummern bleiben dabei bei ihren ursprünglichen Inhalten; neu vergeben wird nichts.

Quelle der Rücknahme ist der Commit `23f868f` vom 26. August 2026, der letzte Stand vor der ersten Löschung. Für die sechs beschnittenen Quelldateien ist er zugleich der Importzustand: An ihnen wurde zwischen Anlage und Beschneidung nichts geändert, ein `git restore` führt sie deshalb ohne Verlust auf das Original zurück. Für die `INVENTAR.md` gilt das **nicht** — sie hat seither acht Verbesserungen erfahren, die erhalten bleiben müssen; dort wird selektiv zurückgetragen statt restauriert.

**A — Quelldateien.** `git restore --source=23f868f --` auf `claude.ai-pro-allgemein.txt`, `birdnet-audio-walker.txt`, `GigE-CameraStreamingServer.txt`, `RTCP Camera Streamer and Player.txt`, `Scheludko-Zelle allgemein.txt` und `Scheludko-Zelle Bildverarbeitung.txt`. Die `modellbahn-fahrpult.txt` bleibt unberührt — sie wurde nie beschnitten. Gegenprobe danach: Die beiden CAM-Zwillinge müssen wieder byte-identisch sein, und der Diff zwischen BIRD und SCH‑B muss wieder genau den einen Unterschiedssatz zeigen (Beschriftung vor den Block statt hinein), statt wie heute leer auszufallen.

**B — Die Musterdatei aufnehmen.** `muster-fuer-projektanweisungen.md` wird mitcommittet und im Inventar erschlossen: Kürzel **MUSTER**, eine Zeile in der Quellentabelle von Kapitel 1, dort außerdem „sieben Textdateien" auf acht; in Kapitel 2 ein Absatz zu ihrer Stellung — sie ist die gepflegte Vorlage, aus der die CAM-Fassung hervorging (identische Tippfehler, identische T19-Frühform), und damit ein Indiz zur offenen Frage 5.4-1 nach der Chronologie; in der Themenmatrix von Kapitel 3 eine weitere Spalte.

**C — Das neue Kapitel 6.** Hinter Kapitel 5 entsteht „6 Erledigte Einträge" mit einem Kopfabsatz, der Anlass und Datum der Rücknahme nennt. Darin die acht Einträge in Nummernfolge, im Wortlaut aus `23f868f`. Jeder bekommt eine Zeile, die seinen heutigen Verbleib benennt: welcher Skill-Ordner ihn verarbeitet hat und wann. Die Ordnernamen im übernommenen Wortlaut werden auf die heutigen umgestellt — `web-code-artefacts` beziehungsweise `skills/🚧_web-code-artefacts/` heißt heute `skills/web-code-editing/` und ist fertig, nicht mehr „in Arbeit". Die Gruppenzugehörigkeit (A bis F) wird je Eintrag vermerkt, weil die Gruppenüberschriften in Kapitel 4 bleiben, wo sie sind; die dort entstandene Lücke bei Gruppe C bleibt bestehen, ihre beiden Einträge stehen künftig in Kapitel 6.

**D — Anpassungen im bestehenden Text.** Der Dateikopf verliert seine zwei Erledigt-Notizen und bekommt stattdessen einen Satz, der auf Kapitel 6 zeigt. In Kapitel 3 kehren die acht Matrixzeilen zurück, darunter eine Zeile, die sagt, welche Nummern erledigt sind und wo sie stehen. Der Vorspann zu Gruppe B in Kapitel 4 meldet T8–T11 künftig als nach Kapitel 6 verschoben statt als entfernt; in Kapitel 5.1 wird derselbe Verweis nachgezogen. In 5.2 kehren die zwei gelöschten Tabellenzeilen **nicht** zurück, stattdessen ein Verweis auf Kapitel 6 — so bleibt die Unterscheidung gewahrt: „abgedeckt" heißt, das heutige Regelwerk enthält die Anweisung bereits, „erledigt" heißt, aus ihr wurde ein Skill. Und die drei Verweise, die beim Löschen zu „vormals T9", „vormals T16" und „vormals T12/T13" umformuliert wurden (in T19, T21 und T25), zeigen wieder auf die Nummern, ergänzt um die Kapitelangabe; ihre inhaltliche Präzisierung — welcher Skill die Regel heute trägt — bleibt erhalten.

**E — Was außerhalb des Ordners nachzuziehen ist.** Eine einzige Stelle: In Schritt 3 dieses Fahrplans wird der Satz falsch, T2, T12, T13 und T16 seien „aus Inventar wie Quelldateien entfernt"; er wird auf den neuen Stand gebracht. Die übrigen T-Verweise im Repo bleiben richtig — die beiden READMEs von `web-code-editing` nennen T8–T11 als verarbeitete Herkunft, was zutrifft, und die T-Nummern in `software-dev-doc-fh` und `home-.claude-sharing` gehören zu eigenen, unabhängigen Nummernkreisen.

**Prüfungen zum Abschluss.** Tabellen-Scan über die geänderten Markdown-Dateien; die Gegenprobe der Quelldateien aus Teil A; und die Kontrolle, dass jede der 27 Nummern genau einmal als Eintrag vorkommt — in Kapitel 4 oder in Kapitel 6, nie in beiden.

Der Ordner trägt das 🚷-Schild und liegt deshalb nicht auf master; ein Release entfällt, die Arbeit endet auf dev.

## 3 Anweisungs-Inventar zuordnen

Die Posten des Anweisungs-Inventars (T1–T27; liegt in einem temporären Arbeitsordner, der nach Abschluss entfällt) werden einzeln zugeordnet. Claude reicht sie vorsortiert durch — gebündelt nach vorgeschlagenem Skill-Zuhause, je Posten mit Herkunft, Varianten und einem Geltungsbereichs-Vorschlag nach Kapitel 8.3 der `skill-dev-doc.md` (nur Coding / alle Arbeitsformen / andere) —, und der Entwickler legt je Posten die Zuordnung fest oder bestätigt sie. Maßstab der Verteilung ist das Arbeitsmodell in Kapitel 8.2. Die bestätigte Zuhause-Liste wird anschließend in der `skill-dev-doc.md` festgeschrieben; erst danach beginnt die Ausformulierung der einzelnen Skills.

Damit erledigt sich zugleich der übergreifend offene Punkt „Neuordnung der Arbeitsanweisungen zu Skill-Zuhausen“.

**Der Schritt ist größer als sein ursprünglicher Zuschnitt und wird bei Beginn untergliedert** (Festlegung des Entwicklers vom 27. August 2026). Dreierlei dazu: T2, T8 bis T13 und T16 sind erledigt und stehen in Kapitel 6 des Inventars (verarbeitet in `common-code-generation`, `temp-debug-code` und `web-code-editing`); die Quelldateien tragen ihre Passagen weiterhin vollständig. Die durch die globale CLAUDE.md abgedeckten Posten (T1, T3, T6, T7, T21, T22) gelten ausdrücklich **nicht** als erledigt — die globale CLAUDE.md wird selbst noch zu dynamisch ladenden Skills durchgearbeitet, und diese Posten sind dafür Referenzmaterial. Und die Zielwelt-Sortierung wirkt herein: Je Posten ist auch zu bestimmen, in welche Zielwelt-Gruppe sein Zuhause gehört — die Gruppen und das Zuordnungskriterium stehen in Kapitel 9 der `skill-dev-doc.md`.

## 4 `🚧_translation-task`: die fünf offenen Festlegungen

Die fünf Punkte unter „Noch nicht festgelegt“ in der `SKILL.md` einzeln besprechen und dort festschreiben: Namenskonvention für Zieldateien, Sync-Workflow zwischen zwei Sprachfassungen, Umgang mit Lizenz- und Rechtstexten, Ein-Absatz-pro-Zeile-Formatierung, Ton und Anrede.

## 5 `🚧_software-dev-doc-fh`: Zugehörigkeit der beiden Werkzeug-Skills klären

Klären, ob die vorhandenen Skills `konzept-segmentierung` und `konsistenzpruefung` in dieses Vorhaben überführt und dem Namensschema angeglichen werden. Sie sind Werkzeuge innerhalb dieses Standards und liegen bisher nur unter `~/.claude/skills/`. Zu bedenken ist dabei: Sobald sie hier liegen, verstößt die `SKILL.md` mit ihrem Abschnitt „Zusammenspiel mit anderen Skills“ gegen Kapitel 2.3 der Vorgaben — kein Skill-Körper verweist auf einen anderen Skill dieses Verzeichnisses.

Bei dieser Gelegenheit fällt auch die Entscheidung über die Zweiteilung aus Schritt 2.

## 6 `🚧_software-task-detection`: über den Fortbestand entscheiden

Entscheiden, ob daraus ein eigenständiger Skill wird, ob er die Vorstufe von `software-dev-doc-fh` ist — oder ob er sich mit `common-code-generation` erledigt hat, der inzwischen einen Teil davon trägt. Erst danach lohnt Arbeit am Inhalt. Fällt die Entscheidung für einen eigenen Skill: den Trigger nach Kapitel 2 der Vorgaben geankert neu formulieren, nicht als Hintergrund-Beobachtung.

## 7 `web-code-editing`: auf claude.ai erproben

Der Skilltext ist fertig und mit dem Entwickler abgestimmt (28. August 2026, Verarbeitung der Inventar-Posten T8–T11 samt Live-Tests an einem 39.898-Zeilen-Projektwissen); Zielwelt ist ausschließlich claude.ai (`skill-dev-doc.md` 9.4). Es bleibt:

- **Als Custom Skill hochladen und erproben** (ZIP über Settings → Features): Löst die `description` aus? Findet die Instanz `/mnt/project/` auf Anweisung? Dabei fällt zugleich die Prüffrage aus `skill-dev-doc.md` 1.4 mit ab (zieht ein hochgeladener Skill gebündelte Dateien nach).
- **Trigger-Absatz für das Anweisungsfeld** (global oder je Projekt) formulieren, falls die `description` allein nicht zuverlässig auslöst.

## 8 `🚧_zotero-use`: Probelauf und Werkzeugentscheidung

- Probelauf gegen das echte Konto: Lesen sofort, Schreiben mit frisch erzeugtem Zotero-Web-API-Key gegen eine Wegwerf-Testsammlung (nichts Echtes riskieren).
- Dabei klären, ob `zotero-cli-cc` Sammlungs-Management schon kann oder ob ein dünner Zusatz nötig ist.
- Danach erst: Werkzeug-Entscheidung (`zotero-cli-cc` vs. `zotero-mcp` vs. Plugin-Variante `cookjohn/zotero-mcp`) und Verpackung als Skill.

## 9 `in-depth-online-literature-research`: zwei Erprobungen nachholen

Der Skill bleibt dabei **benutzbar** — beide Punkte betreffen die Absicherung, nicht die Funktion. Dass ein Skill irgendwann einen nicht absehbaren Fehler hervorruft, lässt sich ohnehin nicht ausschließen; das ist kein Grund, ihn als unfertig zu führen.

- Die Wirksamkeit des Selbsttests nachmessen. Der passende Prüffall: eine Wiederholung der Sammelrecherche mit anschließendem Abgleich aller Links gegen die tatsächlich abgerufenen Seiten.
- Den claude.ai-Zweig der Ergebnisübergabe (automatisches Artefakt) dort erproben.
