# Fahrplan des Repositories

Die anstehenden Schritte in der Reihenfolge ihrer Bearbeitung. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben, neue Schritte zählen hoch.

**Dieser Fahrplan gilt repository-weit.** Er lag bis zum 27. August 2026 in `skills/`, weil die Arbeit dort begann; seine Schritte betrafen aber längst alle Bereiche (zuletzt die Dateinamen-Prüfung und die Zielwelt-Sortierung). Vorhaben mit eigenem, abgegrenztem Entwicklungsstand führen daneben weiter ihren eigenen: `skills/chat-export/work-plan-v2.md` und `home-.claude-sharing/work-plan.md`.

Was hier **nicht** steht: der Zustand eines Skills oder Bereichs und alles, was zwar geplant, aber noch nicht auf der Tagesordnung ist. Beides trägt die `README.md` des jeweiligen Skills bzw. Bereichs. Der Fahrplan gibt die Folgeschritte der Projektbearbeitung vor, keine Zukunftsvisionen.

Eine `status.md` führt das Vorhaben `skills/` nicht.

Die Nummern sind Kennungen, keine Reihenfolge: Maßgeblich ist, in welcher Folge die Schritte hier stehen. Ab Schritt 3 ist auch die nicht festgelegt — diese Schritte hängen nicht voneinander ab.

## 13 `git-branch-model`: garantierte Auslösung bei Sonnet

**Unmittelbar nächster Schritt** (Festlegung des Entwicklers vom 16. September 2026 — beide Skills sollen bald abschließend lauffähig sein). Ausgangslage: Die Trigger-Messung vom 16. September 2026 (README von `git-branch-model`, „Stand und Offenes") hat gezeigt, dass Sonnet am gemeinsamen Anker mit `git-workbench` nur den Skill lädt, dessen `description` den Auftrag wörtlich trifft — die zweite Bedingung „existiert `.claude/git-branch-model.json`?" aus dem CLAUDE.md-Trigger führt es nicht aus. Eine schärfere Description hat das Problem nicht behoben (0 von 3 Läufen) und in Projekten ohne Zweigmodell zum Überfeuern geführt; verworfen.

**Lösungsidee, aus einem älteren Fall übertragen** (Chat vom 2. September 2026, `recall-skills-after-compact`: dort ein `SessionStart`-Hook mit `compact`-Matcher, weil nach einer Kompaktierung kein Text-Anker existiert, an dem ein Trigger ansetzen könnte). Der heutige Fall liegt anders — ein Text-Anker existiert, nur die Priorisierung zwischen zwei passenden Skills geht bei Sonnet falsch —, aber dieselbe Bauform trägt: ein `PreToolUse`-Hook auf `Bash`, der bei einem Git-Schreibkommando greift. Die „leichte Variante" (Deine Formulierung vom 2. September): Der Hook führt den Abgleich nicht selbst aus, sondern legt der Instanz nur vor, dass `.claude/git-branch-model.json` existiert und der Skill zu konsultieren ist — die Entscheidung bleibt bei der Instanz, aber der Hinweis kommt garantiert an, nicht als Trigger-Text, der überstimmt werden kann.

**Umzusetzen, mit Bau und Nachmessung als ein Schritt:**

1. **Hook-Matcher festlegen.** Welche Bash-Kommandos den Hook auslösen — `git commit`, `git push`, `git checkout`, `git merge` mindestens; zu klären, ob ein Substring-Matcher auf `^git ` reicht oder feiner unterschieden werden muss (ein lesendes `git status` soll nicht auslösen).
2. **Hook-Skript schreiben**, nach dem Muster von `recall_skills_after_compact.py` (Kap. 5.0 der Vorgaben): prüft `.claude/git-branch-model.json` im aktuellen Projekt, legt bei Vorhandensein eine knappe Anweisung auf stdout, scheitert sonst still mit Exit 0. Keine mitgelieferte Erklärung des Mechanismus (Kap. 5.0: „jede mitgelieferte Erklärung lädt zum Nachforschen ein" — am ersten Praxistest von `recall-skills-after-compact` belegt).
3. **`settings-json-snippet.de/en.md` für `git-branch-model`** anlegen, gleich gebaut wie bei `recall-skills-after-compact`: Datumszeile, kursive Kopfnotiz (JSON wird eingefügt, nicht angehängt; Pfad trägt `$HOME`, kein Platzhalter — Kap. 5.0 nennt den Schaden: ein `/home/<user>/…`-Platzhalter wird mitkopiert, übersehen, und der Hook scheitert still), Trennlinie, der zu übernehmende `hooks`-Block. `SKILL.de/en.md` bekommt dafür Vorlage C aus Kap. 6.1 (dritter Installationsschritt „Hook verdrahten" statt „Stillen Trigger übernehmen").
4. **Probe ohne Ereignis** in der Kopfnotiz: das Hook-Kommando von Hand ausführen, ohne auf ein echtes Git-Kommando zu warten — Pflicht nach Kap. 5.0, nicht Komfort.
5. **Bauen im Wegwerf-Projekt**, nicht im Repo selbst: Hook einrichten, mit `claude -p` in mehreren frischen Chats gegen ein Testprojekt mit und ohne `.claude/git-branch-model.json` prüfen, ob die Anweisung ankommt und die Instanz danach tatsächlich `git-branch-model` konsultiert — nicht nur, dass der Hook feuert. Mehrere Testchats, nicht einer: Der alte Fall wurde erst nach einem fehlgeschlagenen und zwei weiteren Läufen als belegt behandelt. Zwei Lehren aus der Messung vom 16. September 2026, die den Aufbau binden: **Standard-Berechtigungsmodus, nicht `--permission-mode plan`** — im Planmodus erkennt die Instanz den Trigger, lädt den Skill aber nicht, weil sie den Plan erst beenden will und `ExitPlanMode` im `-p`-Lauf fehlt; das `Skill`-Werkzeug braucht keine Freigabe, ein verweigertes `git commit` stört nicht. Und **Fixture-Dateien per `git rm` entfernen, nie per `rm -f`** — ein `reset --hard` vor jedem Lauf holt sonst die committete Datei zurück, und die „ohne"-Variante misst still dasselbe wie die „mit"-Variante. Die installierten Skills gleichen Namens vor jedem Lauf ganz aus `~/.claude/skills/` heraus (der Nutzer-Skill schlägt den Projekt-Indikator), danach byteidentisch zurück.
6. **Übernahme in dieses Repo**, mit Freigabe: `settings-json-snippet.de/en.md` in `~/.claude/settings.json` einfügen (die dort schon einen `hooks`-Block für `recall-skills-after-compact` trägt — einfügen, nicht ersetzen), Wirkung in einer echten Sitzung dieses Repos prüfen.
7. **README nachziehen**: der Messbefund von heute bleibt stehen, ergänzt um „Lösung: Hook, siehe Installation"; „Stand und Offenes" verliert den Satz „wie die Auslösung garantiert werden kann, ist offen".
8. **Zielwelt bleibt `local`** (Kap. 5.0: Hooks gibt es auf claude.ai nicht; nur `_de_local`/`_en_local`-Pakete, kein `_web`).

**Danach entscheiden, nicht vorwegnehmen:** ob `git-workbench` einen entsprechenden Hook ebenfalls braucht — die Messung vom 16. September zeigt es bei allen drei Modellen zuverlässig feuernd, ein Hook wäre dort unbegründet, solange sich das nicht ändert.

## 11 `vscode-dev-container`: Feldnachweise abschließen

**Der erste Bau ist gelaufen** (5./7. September 2026, zwei Rechner): Image gebaut, Container gestartet, Claude-Erweiterung v2.1.263 lief, Pfad und Sitzungsschlüssel wie entworfen. Was dabei auffiel, steckt in der README des Bausteins samt Prüfliste mit Spalte „geprüft"; drei fehlende Pakete (`openssh-client`, `bubblewrap`, `socat`) sind im Dockerfile nachgetragen, die Ordnerstruktur auf `.devcontainer/` + `.claude/` umgestellt.

Offen bleiben die drei Punkte, die Hardware oder eine Messung brauchen:

1. **Die `DOCKER-USER`-Regel je Rechner festlegen** — mit den `ACCEPT`-Ausnahmen für die dort angeschlossenen Geräte (Kameras, Messtechnik). Ohne sie ist das Firmennetz aus dem Container erreichbar; das ist der Punkt, an dem der Baustein sein drittes Schutzziel einlöst oder nicht.
2. **Die offene Frage zu `--network host` messen**: Ob `DOCKER-USER` dort tatsächlich nicht greift, ist aus der Docker-Netzarchitektur abgeleitet und nicht nachgemessen. Der Test ist ein Verbindungsversuch auf eine interne Adresse, einmal mit Bridge- und einmal mit Host-Netz.
3. **Die zwei letzten Prüflistenzeilen abtasten**, die noch „offen" tragen: `git fetch` aus dem Container heraus und der Internet-Abruf.

**Die Baustellenmarke ist unabhängig davon schon gefallen:** Die beiden Wurzel-READMEs tragen seit dem 10. September 2026 ✅ statt 🚧 — Entscheidung des Entwicklers, gestützt auf den gelungenen Feldbau („einmal erfolgreich gelaufen, kann also verwendet werden"). Dieser Schritt hängt damit nicht mehr an der Marke, sondern nur noch an den drei Punkten oben; erledigt sind sie erst, wenn die Prüfliste in der README des Bausteins keine Zeile „offen" mehr trägt.

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
