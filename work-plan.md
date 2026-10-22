# Fahrplan des Repositories

Die anstehenden Schritte in der Reihenfolge ihrer Bearbeitung. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben, neue Schritte zählen hoch.

**Dieser Fahrplan gilt repository-weit.** Er lag bis zum 27. August 2026 in `skills/`, weil die Arbeit dort begann; seine Schritte betrafen aber längst alle Bereiche (zuletzt die Dateinamen-Prüfung und die Zielwelt-Sortierung). Vorhaben mit eigenem, abgegrenztem Entwicklungsstand führen daneben weiter ihren eigenen: `skills/chat-export/work-plan-v2.md` und `home-.claude-sharing/work-plan.md`.

Was hier **nicht** steht: der Zustand eines Skills oder Bereichs und alles, was zwar geplant, aber noch nicht auf der Tagesordnung ist. Beides trägt die `README.md` des jeweiligen Skills bzw. Bereichs. Der Fahrplan gibt die Folgeschritte der Projektbearbeitung vor, keine Zukunftsvisionen.

Eine `status.md` führt das Vorhaben `skills/` nicht.

Die Nummern sind Kennungen, keine Reihenfolge: Maßgeblich ist, in welcher Folge die Schritte hier stehen. Ab Schritt 3 ist auch die nicht festgelegt — diese Schritte hängen nicht voneinander ab.

## 12 Private Adressen aus der Git-Historie entfernen

**Stand.** Erledigt für `claude-ai-tooling` (22./23. Oktober 2026): die Historie aller drei Zweige umgeschrieben, geprüft und gepusht, das Arbeitsverzeichnis nachgezogen. Offen sind die übrigen GitHub-Repos unter `~/git/` (`logdruid` erst, wenn der Entwickler die dort arbeitende andere Instanz für beendet erklärt), danach die Repos, die nur auf GitHub liegen, zuletzt die Ablaufbeschreibung für die anderen Rechner. Zurückgestellt ist `birdnet-audio-walker`: Auf einem anderen Rechner liegt dort noch Ungepushtes (23. Oktober 2026). Der Plan des nächsten Teilschritts steht am Ende dieses Schritts.

**Anlass.** GitHub blockiert Pushes, deren jüngster Commit eine private Adresse trägt (Einstellung „Block command line pushes that expose my email“). Die Identitätskonfiguration dieses Rechners ist umgestellt (22. Oktober 2026: global `fherb2` mit GitHub-noreply-Adresse, Helmholtz-Repos per `includeIf` über die Remote-URL); dieser Schritt bereinigt die Historie der GitHub-Repos.

**Festlegungen des Entwicklers (22./23. Oktober 2026).** Die ganze Historie wird umgeschrieben, zentral von diesem Rechner aus; auf den anderen Rechnern ist alles gepusht, ihre Klone werden danach ersetzt, nicht repariert. Ersetzt wird, wo Name oder Adresse **automatisch** verwendet wurden — Commit-Identitäten, Metadaten, von Werkzeugen übernommene Kontodaten —, nicht in Prosa, Pfaden, Beispielen oder `.research`. Die Regel des Skills `git-workbench` „Auf keinem anderen Zweig wird Historie umgeschrieben“ ist für diesen Vorgang ausdrücklich aufgehoben. Werkzeug ist `git-filter-repo` v2.47.0 als Einzelskript im Scratchpad. Sicherungen, Ersetzungslisten und Zuordnungen liegen unter `~/git/_rewrite-backup/`; die Listen enthalten die privaten Adressen und gehören in kein Repository. Texte dieses Vorgangs — Fahrplan, Commit-Nachrichten, die Ablaufbeschreibung für die anderen Rechner — nennen die privaten Adressen und die ersetzten Zeichenfolgen nie wörtlich; ihr Wortlaut steht nur in den Dateien dort. Grund: Im ersten Probelauf hat der Plan selbst die Adressen wieder ins Repository gebracht. Einen Antrag beim GitHub-Support, die alten Commits aus zwischengespeicherten Ansichten zu entfernen, gibt es für kein Projekt.

**Weitere Festlegungen (23. Oktober 2026).** HZDR-Adressen müssen aus GitHub-Projekten immer heraus; sie werden wie die GMX-Adresse zu `fherb2` mit der noreply-Adresse. Autorzeilen in Paket-Metadaten (`setup.cfg`, `pyproject.toml` und Ähnliches) werden rückwirkend zu Name `fherb2` und noreply-Adresse. Auf GitHub wird immer über die SSH-URL zugegriffen — HTTPS läuft aus der Umgebung der Claude-Sitzung ins Leere (beobachtet; vermutlich deren Sandbox) —, und auch neu angelegte lokale Klone bekommen die SSH-URL. Vor jedem Projekt fragt Claude, ob auf einem anderen Rechner noch Ungepushtes liegt. Es wird immer nur ein Projekt bearbeitet; danach werden seine Scratchpad-Ordner gelöscht.

**Verfahren, bewährt an `claude-ai-tooling`** — je Repository:

- **Sicherung:** ein Git-Bundle aller Refs nach `~/git/_rewrite-backup/<repo>-<datum>.bundle`, geprüft mit `git bundle verify`.
- **Ersetzungslisten:** die gemeinsame `mailmap` (beide privaten Adressen → `fherb2` mit noreply-Adresse, für Autor, Committer und Tagger); je Repository eine eigene Textersetzungsliste für automatisch übernommene Daten, deren Fälle dem Entwickler einzeln vorgelegt werden.
- **Umschreiben** in einer frischen nackten Kopie im Scratchpad — von GitHub per SSH, oder vom Arbeitsverzeichnis (`git clone --bare --no-local`), wenn dort Ungepushtes mitgehen soll —, nie im Arbeitsverzeichnis selbst: In einem nicht frischen Klon verschiebt das Werkzeug `refs/remotes/origin/*` nach `refs/heads/*` und entfernt `origin`. Immer mit `--date-order`: Verweise in Commit-Nachrichten laufen zwischen Zweigen womöglich in beide Richtungen, und ohne zeitliche Reihenfolge bleibt eine Richtung unaufgelöst (`claude-ai-tooling`: 14 Verweise von `master` auf `dev`; ein zweiter Durchlauf machte über die Gegenrichtung alles wieder ungültig).
- **Prüfung vor dem Push** mit `~/git/_rewrite-backup/verify_rewrite.py`, Commit für Commit: Eltern, Zeitstempel und Nachrichten bis auf zitierte Hashes gleich, nur erlaubte Identitäten, jeder Verweis auf den richtigen neuen Commit, alle geänderten Inhaltszeilen aufgelistet. Dazu die Restvorkommen der Adressen und die gemeinsame Herkunft der Zweige.
- **Push** mit `--force-with-lease` auf die zuletzt bekannten GitHub-Stände; danach im Arbeitsverzeichnis `fetch`, der ausgecheckte Zweig per `checkout -B`, die übrigen per `branch -f` — kein `reset --hard`.
- **Nacharbeiten:** in Dateien zitierte Hashes über die `commit-map` nachziehen; sie wird nach `~/git/_rewrite-backup/` kopiert, weil das Scratchpad mit der Sitzung verschwindet.

**Auswirkungen, die jedes Repository trifft.** Alle Commit-Hashes ändern sich, Signaturen entfallen. Lokale Stashes und Reflogs hängen an der alten Historie, werden aber nie gepusht. Auf anderen Rechnern werden die Klone ersetzt (alten umbenennen, frisch klonen, ignorierte lokale Dateien bei Bedarf übernehmen), nicht repariert. Auf GitHub bleiben die alten Commits über ihre Hashes in zwischengespeicherten Ansichten erreichbar.

**Plan für `birdnet_crawler`, noch nicht ausgeführt.** Ausgangslage: nur der Zweig `main`; keine Tags, keine Stashes, keine ungepushte Arbeit, auch nicht auf anderen Rechnern; LFS mit 20 Dateien an der Spitze; die Remote-URL nutzt HTTPS mit Zugangsdaten im Klartext. In der Historie stehen die GMX-Adresse, beide HZDR-Adressen und in `src/setup.cfg` zwei Autorzeilen mit Namen und GMX-Adresse — je nur in einer Fassung. Pfade in der Container-Registry des HZDR, die HZDR-Domain in einer Commit-Nachricht, der Name in der `README.md` und fremde Autoren unter `test_zone/` bleiben.

- **Teil A — Vorbereitung, Probelauf, Prüfung; auf GitHub ändert sich nichts.** Die `mailmap` wird um die zweite HZDR-Adresse ergänzt; eine eigene Ersetzungsliste `replacements-birdnet_crawler.txt` trägt die zwei Autorzeilen (Name → `fherb2`, Adresse → noreply-Adresse). Das Bundle des lokalen Klons kommt nach `~/git/_rewrite-backup/`. Im Scratchpad entsteht eine nackte Kopie von GitHub per SSH als unberührtes Original und daraus eine zweite, die umgeschrieben wird (Mailmap, Ersetzungsliste, `--date-order`). Weicht `main` auf GitHub vom lokalen ab, wird angehalten. Geprüft wird wie im Verfahren oben, dazu: keine LFS-Verweisdatei verändert, und die Kopie trägt keinen `pre-push`-Hook — sonst versuchte LFS beim Push, Objekte hochzuladen, die in der Kopie fehlen; auf GitHub liegen sie unverändert.
- **Teil B — Push, eigene Freigabe.** `--force-with-lease` auf den Stand des Originals.
- **Teil C — lokalen Klon ersetzen, aufräumen.** Claude benennt den alten Klon in `birdnet_crawler.old` um; den neuen klont der Entwickler in seiner Shell per SSH-URL, weil LFS die großen Dateien über HTTPS holt. Hat der Entwickler den neuen Klon geprüft, löscht Claude den alten und die Scratchpad-Ordner des Projekts. Mit dem alten Klon verschwinden auch die Zugangsdaten aus seiner Remote-URL.

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
