# Fahrplan des Repositories

Die anstehenden Schritte in der Reihenfolge ihrer Bearbeitung. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben, neue Schritte zählen hoch.

**Dieser Fahrplan gilt repository-weit.** Er lag bis zum 27. August 2026 in `skills/`, weil die Arbeit dort begann; seine Schritte betrafen aber längst alle Bereiche (zuletzt die Dateinamen-Prüfung und die Zielwelt-Sortierung). Vorhaben mit eigenem, abgegrenztem Entwicklungsstand führen daneben weiter ihren eigenen: `skills/chat-export/work-plan-v2.md` und `home-.claude-sharing/work-plan.md`.

Was hier **nicht** steht: der Zustand eines Skills oder Bereichs und alles, was zwar geplant, aber noch nicht auf der Tagesordnung ist. Beides trägt die `README.md` des jeweiligen Skills bzw. Bereichs. Der Fahrplan gibt die Folgeschritte der Projektbearbeitung vor, keine Zukunftsvisionen.

Eine `status.md` führt das Vorhaben `skills/` nicht.

Die Nummern sind Kennungen, keine Reihenfolge: Maßgeblich ist, in welcher Folge die Schritte hier stehen. Ab Schritt 3 ist auch die nicht festgelegt — diese Schritte hängen nicht voneinander ab.

## 12 Private Adressen aus der Git-Historie entfernen — Teilschritt `claude-ai-tooling`

**Plan, noch nicht ausgeführt.**

**Anlass.** GitHub blockiert Pushes, deren jüngster Commit eine private Adresse trägt (Einstellung „Block command line pushes that expose my email“). In diesem Repository tragen alle Commits private Identitäten: zwei Varianten mit der privaten GMX-Adresse und einmal eine dienstliche HZDR-Adresse mit vollem Namen. Die Identitätskonfiguration dieses Rechners ist bereits umgestellt (22. Oktober 2026: global `fherb2` mit GitHub-noreply-Adresse, Helmholtz-Repos per `includeIf` über die Remote-URL). Dieser Schritt schreibt die Historie dieses Repositories um. Die übrigen GitHub-Repos folgen als eigene Schritte; `logdruid` erst, wenn der Entwickler die dort arbeitende andere Instanz für beendet erklärt.

**Festlegungen des Entwicklers (22. Oktober 2026).** Die ganze Historie wird umgeschrieben, zentral von diesem Rechner aus; auf den anderen Rechnern ist alles gepusht, ihre Klone werden danach ersetzt, nicht repariert. Ersetzt wird, wo Name oder Adresse **automatisch** verwendet wurden — Commit-Identitäten, Metadaten, von Werkzeugen übernommene Kontodaten —, nicht in Prosa, Pfaden, Beispielen oder `.research`. Die Regel des Skills `git-workbench` „Auf keinem anderen Zweig wird Historie umgeschrieben“ ist für diesen Vorgang ausdrücklich aufgehoben. Werkzeug ist `git-filter-repo` v2.47.0 als Einzelskript im Scratchpad. Sicherungen und Ersetzungslisten liegen unter `~/git/_rewrite-backup/`; sie enthalten die privaten Adressen und gehören in kein Repository. Texte dieses Vorgangs — dieser Plan, Commit-Nachrichten, die spätere Ablaufbeschreibung für die anderen Rechner — nennen die privaten Adressen und die ersetzten Zeichenfolgen nie wörtlich; ihr Wortlaut steht nur in den Dateien dort. Grund: Im ersten Probelauf (22. Oktober 2026) hat genau dieser Plan die Adressen wieder ins Repository gebracht.

**12.1 Ausgangsstand.** Dieser Plan wird auf `dev` committet, damit der Stand sauber ist. Die zwei bisher ungepushten Commits (`7baba3a` auf `dev`, `99b0965` auf `master`) werden nicht vorab gepusht, sondern mit umgeschrieben. Ab hier bis 12.7 entsteht im Arbeitsverzeichnis kein weiterer Commit.

**12.2 Sicherung.** Ein Git-Bundle mit allen Refs des Arbeitsverzeichnisses — Zweige, Remote-Refs, Stash — nach `~/git/_rewrite-backup/claude-ai-tooling-2026-10-22.bundle`, danach mit `git bundle verify` geprüft. Es ist der Rückweg für jeden folgenden Teilschritt: Aus ihm lassen sich die alten Zweige lokal wie auf GitHub wiederherstellen (Letzteres würde die alten Adressen erneut veröffentlichen).

**12.3 Werkzeug.** Einmaliger Netzabruf: die Datei `git-filter-repo` vom Tag `v2.47.0` des Repositories `newren/git-filter-repo` in einen eigenen, leeren Scratchpad-Ordner. Aufgerufen wird sie mit `python3 -I`. Keine Installation, kein Eingriff ins System; mit der Sitzung ist sie weg.

**12.4 Ersetzungslisten** unter `~/git/_rewrite-backup/`:

- `mailmap`: Die private GMX-Adresse und die dienstliche HZDR-Adresse werden zu `fherb2 <11900157+fherb2@users.noreply.github.com>` — für Autor, Committer und Tagger, unabhängig vom bisherigen Namen. Der Committer `GitHub <noreply@github.com>` der drei Web-Commits bleibt.
- `replacements-claude-ai-tooling.txt`, drei wörtliche Ersetzungen von Kontodaten, die claude.ai erzeugt und eine Claude-Instanz in die Doku übernommen hat: der Organisationsname mit der GMX-Adresse (heute in `skills/chat-export/chrome-access.de.md` und `.en.md`), der Organisationsname mit dem Vornamen (heute in `skills/chat-export/SKILL.de.md` und `.en.md`) und eine Anmeldezeile mit Vorname und GMX-Adresse (nur in der Historie, frühere `Zielvorlage.md`). Ersetzt wird jeweils durch die Platzhalter `<email>` und `<Name>`. Unberührt bleibt die HZDR-Adresse im zitierten Sitzungskontext unter `.research/`.

**12.5 Umschreiben** in einer frischen, nackten Kopie (bare clone) des Arbeitsverzeichnisses im Scratchpad. Sie enthält `dev`, `master` und `repo-management` samt der zwei ungepushten Commits, aber keine Remote-Refs und keinen Stash. Grund für die Kopie: Laut Handbuch verschiebt das Werkzeug in einem nicht frischen Klon `refs/remotes/origin/*` nach `refs/heads/*` und entfernt `origin`; das Arbeitsverzeichnis bleibt so bis 12.7 unberührt. Das Werkzeug läuft mit Mailmap und Ersetzungsliste; Hashes, die in Commit-Nachrichten zitiert sind, passt es selbst an und hält die Zuordnung alt → neu in `filter-repo/commit-map` fest.

Das Werkzeug läuft dabei mit `--date-order`, bearbeitet die Commits also nach ihrem Zeitstempel statt Zweig für Zweig. Grund: Commit-Nachrichten verweisen zwischen den Zweigen in beide Richtungen — 14 Verweise von `master` auf `dev` (Datei-Abgleiche, „übernommen aus dev …“), 3 von `dev` auf `master`. Ohne die Option bearbeitet das Werkzeug einen Zweig nach dem anderen und kann Verweise auf Commits, die es noch nicht bearbeitet hat, nicht umsetzen (erster Probelauf, 22. Oktober 2026: 14 alte Hashes blieben stehen); ein zweiter Durchlauf über die `master`-Nachrichten änderte über die Gegenrichtung auch `dev` und machte die eben gesetzten Hashes wieder ungültig. Von den 34 Verweisen zeigen 33 auf einen älteren Commit, einer auf einen Commit mit demselben Zeitstempel. Sechs weitere hash-artige Zeichenfolgen in Nachrichten zeigten schon vorher auf keinen Commit und bleiben, wie sie sind.

**12.6 Prüfung vor dem Push.** In der umgeschriebenen Kopie: nur noch die Identitäten `fherb2 <noreply>` und `GitHub <noreply@github.com>`; die GMX-Adresse in keinem Inhalt eines Commits mehr, die HZDR-Adresse nur noch unter `.research/`; je Zweig dieselbe Zahl an Commits wie vorher, mit denselben Zeitstempeln und Betreffzeilen; Commit für Commit unterscheiden sich die Inhalte nur in den Zeilen aus 12.4 und die Nachrichten nur in zitierten Hashes; jeder Verweis in einer Commit-Nachricht zeigt auf genau den neuen Commit, der aus dem ursprünglich zitierten entstanden ist; `repo-management` hat weiterhin keine gemeinsame Herkunft mit `dev`. Weicht etwas ab: anhalten und melden.

**12.7 Push — eigene Freigabe.** Force-Push der drei Zweige aus der Kopie nach GitHub. Lehnt GitHub ab (etwa durch eine Schutzregel des Zweigs), wird angehalten. Danach im Arbeitsverzeichnis: `fetch`; der ausgecheckte Zweig `dev` wird per Zweigwechsel auf den neuen Stand gesetzt, der uncommittete Änderungen mitnimmt statt sie zu verwerfen (kein `reset --hard`); `master` und `repo-management` werden umgehängt. Die alten Objekte bleiben lokal über Reflog, Stash und Bundle erreichbar.

**12.8 Nacharbeiten.** In `.claude/skills/repo-cleanup-pass/SKILL.md` den zitierten Hash `373b142` durch den neuen aus der `commit-map` ersetzen (Commit auf `dev`, Push mit Freigabe). Im Memory dieses Projekts die Hashes `d92b65c` und `3b4a377` nachziehen — nur mit Zustimmung des Entwicklers, die Datei liegt unter `~/.claude/`.

**Auswirkungen über das Ziel hinaus.** Alle Commit-Hashes ändern sich; in den Dateien wird nur `373b142` zitiert. Die drei signierten Web-Commits verlieren ihre Signatur. Der lokale Stash vom 24. September bleibt auf der alten Basis, wird aber nie gepusht. Auf anderen Rechnern sind die Klone zu ersetzen (alten umbenennen, frisch klonen, ignorierte lokale Dateien bei Bedarf übernehmen). Auf GitHub bleiben die alten Commits über ihre Hashes in zwischengespeicherten Ansichten erreichbar, bis der GitHub-Support sie entfernt — ob diese Anfrage gestellt wird, entscheidet der Entwickler gesondert.

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

## 5 `🚧_software-design-doc`: Zugehörigkeit der beiden Werkzeug-Skills klären

Klären, ob die vorhandenen Skills `konzept-segmentierung` und `konsistenzpruefung` in dieses Vorhaben überführt und dem Namensschema angeglichen werden. Sie sind Werkzeuge innerhalb dieses Standards und liegen bisher nur unter `~/.claude/skills/`. Zu bedenken ist dabei: Sobald sie hier liegen, verstößt die `SKILL.md` mit ihrem Abschnitt „Zusammenspiel mit anderen Skills“ gegen Kapitel 2.3 der Vorgaben — kein Skill-Körper verweist auf einen anderen Skill dieses Verzeichnisses.

Bei dieser Gelegenheit fällt auch die Entscheidung über die Zweiteilung aus Schritt 2.

## 6 `🚧_software-task-detection`: über den Fortbestand entscheiden

Entscheiden, ob daraus ein eigenständiger Skill wird, ob er die Vorstufe von `software-design-doc` ist — oder ob er sich mit `common-code-generation` erledigt hat, der inzwischen einen Teil davon trägt. Erst danach lohnt Arbeit am Inhalt. Fällt die Entscheidung für einen eigenen Skill: den Trigger nach Kapitel 2 der Vorgaben geankert neu formulieren, nicht als Hintergrund-Beobachtung.

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
