# Fahrplan des Repositories

Die anstehenden Schritte in der Reihenfolge ihrer Bearbeitung. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben, neue Schritte zählen hoch.

**Dieser Fahrplan gilt repository-weit.** Er lag bis zum 27. August 2026 in `skills/`, weil die Arbeit dort begann; seine Schritte betrafen aber längst alle Bereiche (zuletzt die Dateinamen-Prüfung und die Zielwelt-Sortierung). Vorhaben mit eigenem, abgegrenztem Entwicklungsstand führen daneben weiter ihren eigenen: `skills/chat-export/work-plan-v2.md` und `home-.claude-sharing/work-plan.md`.

Was hier **nicht** steht: der Zustand eines Skills oder Bereichs und alles, was zwar geplant, aber noch nicht auf der Tagesordnung ist. Beides trägt die `README.md` des jeweiligen Skills bzw. Bereichs. Der Fahrplan gibt die Folgeschritte der Projektbearbeitung vor, keine Zukunftsvisionen.

Eine `status.md` führt das Vorhaben `skills/` nicht.

Die Nummern sind Kennungen, keine Reihenfolge: Maßgeblich ist, in welcher Folge die Schritte hier stehen. Ab Schritt 3 ist auch die nicht festgelegt — diese Schritte hängen nicht voneinander ab.

## 11 `vscode-dev-container`: erster Bau und Prüfliste

**Unmittelbar nächster Schritt.** Die Rezeptur ist geschrieben und in sich geprüft (Shell-Syntax, JSON, Markdown), aber **noch nie gebaut** — Docker steht dieser Sitzung nicht zur Verfügung. Solange der erste Bau aussteht, ist jede Zusage des Bausteins unbelegt.

Zu tun, in dieser Reihenfolge:

1. **Bauen und öffnen.** `Dockerfile`, `devcontainer.json` und `files/` in ein Testprojekt kopieren, dort **Reopen in Container**. Erwartete Stolperstellen, die dabei zuerst auffallen würden: die Umbenennung des mitgelieferten `ubuntu`-Kontos in der ersten `RUN`-Anweisung, die `pipx`-Installationen unter dem umbenannten Nutzer, und ob `${localEnv:SSH_AUTH_SOCK}` gesetzt ankommt.
2. **Die Prüfliste aus der README des Bausteins abarbeiten** und ihr Ergebnis dort unter „Offen" festhalten. Sie prüft Pfad, Sitzungsschlüssel, Abwesenheit von `~/.ssh`, den Agenten, die Netzsperre.
3. **Die `DOCKER-USER`-Regel je Rechner festlegen** — mit den `ACCEPT`-Ausnahmen für die dort angeschlossenen Geräte (Kameras, Messtechnik). Ohne sie ist das Firmennetz aus dem Container erreichbar; das ist der Punkt, an dem der Baustein sein drittes Schutzziel einlöst oder nicht.
4. **Die offene Frage zu `--network host` messen**: Ob `DOCKER-USER` dort tatsächlich nicht greift, ist aus der Docker-Netzarchitektur abgeleitet und nicht nachgemessen. Der Test ist ein Verbindungsversuch auf eine interne Adresse, einmal mit Bridge- und einmal mit Host-Netz.

Erst danach ist die Baustellenmarke in den beiden Wurzel-READMEs von 🚧 auf ✅ zu ändern.

**Nicht Teil dieses Schritts** und getrennt zu entscheiden: die beiden Befunde an der Konfiguration des Entwicklers (die A2-Schlüssel liegen in der Benutzer-`settings.json` unter `sandbox.credentials` statt unter `sandbox.filesystem` und bleiben dadurch wirkungslos; Block A2 in `safety-related/sandbox-settings.de.md` nennt `~/.claude/credentials.json`, die Datei heißt `.credentials.json`). Beide stehen im Anhang von `safety-related/vscode-topologies.de.md`.

## 3 Anweisungs-Inventar zuordnen

Die Posten des Anweisungs-Inventars (T1–T27; liegt in einem temporären Arbeitsordner) werden einzeln zugeordnet. Der Ordner entfällt erst, wenn **alle** Posten in Skills eingepflegt sind — mit ihm dann auch `original/`. Solange auch nur einer offen ist, bleibt beides stehen. Claude reicht sie vorsortiert durch — gebündelt nach vorgeschlagenem Skill-Zuhause, je Posten mit Herkunft, Varianten und einem Geltungsbereichs-Vorschlag nach Kapitel 8.3 der `skill-dev-doc.md` (nur Coding / alle Arbeitsformen / andere) —, und der Entwickler legt je Posten die Zuordnung fest oder bestätigt sie. Maßstab der Verteilung ist das Arbeitsmodell in Kapitel 8.2. Die bestätigte Zuhause-Liste wird anschließend in der `skill-dev-doc.md` festgeschrieben; erst danach beginnt die Ausformulierung der einzelnen Skills.

Damit erledigt sich zugleich der übergreifend offene Punkt „Neuordnung der Arbeitsanweisungen zu Skill-Zuhausen“.

**Der Schritt ist größer als sein ursprünglicher Zuschnitt und wird bei Beginn untergliedert** (Festlegung des Entwicklers vom 27. August 2026). Dreierlei dazu: T2, T8 bis T13 und T16 sind erledigt und stehen in Kapitel 6 des Inventars (verarbeitet in `common-code-generation`, `temp-debug-code` und `web-code-editing`); ihre Passagen sind am 29. August 2026 aus den Quelldateien entfernt worden, nachdem jeder Posten einzeln gegen die Stelle im übernehmenden Skill geprüft und vom Entwickler freigegeben war — die unveränderten Quelldateien liegen im Unterordner `original/`. Die noch offenen Posten tragen in den Quelldateien vorn ihre Inventarnummer in eckigen Klammern, ein Absatz je Posten. Die durch die globale CLAUDE.md abgedeckten Posten (T1, T3, T6, T7, T21, T22) gelten ausdrücklich **nicht** als erledigt — die globale CLAUDE.md wird selbst noch zu dynamisch ladenden Skills durchgearbeitet, und diese Posten sind dafür Referenzmaterial. Und die Zielwelt-Sortierung wirkt herein: Je Posten ist auch zu bestimmen, in welche Zielwelt-Gruppe sein Zuhause gehört — die Gruppen und das Zuordnungskriterium stehen in Kapitel 9 der `skill-dev-doc.md`.

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
