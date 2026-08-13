# Fahrplan: Syncthing-Sync für `~/.claude`

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details zu jedem Schritt stehen in `implementierungs_doku.md` (Kapitelverweise unten). Abgeschlossene Schritte werden aus dieser Liste vollständig entfernt, nicht nur markiert; sie erscheinen danach als Zeile in `status.md`.

Der Mechanismus selbst ist fertig und seit dem 11. August 2026 auf beiden Rechnern im Betrieb. Die Dokumentation ist in sich geprüft, und der Abgleich der Doku gegen den Code hat stattgefunden — was folgt, ist im Kern die Abarbeitung seiner Befunde.

Wie Befundlisten abgearbeitet werden, wo ein Plan steht und wie ein Review nachbearbeitet wird, steht repo-weit in `.claude/CLAUDE.md` — ebenso die Regel, dass Nummern beim Streichen erledigter Schritte nicht neu vergeben werden. **Für dieses Vorhaben heißt das:** Der Review und seine Bearbeitung liegen in `implementierungs_doku.md`, Anhang B; ein Schritt, der kein Review-Befund ist, wird hier im Fahrplan ausdetailliert, sobald er ansteht.

## Schritte

1. **Die Befunde des Code-Abgleichs abarbeiten.** Review und Bearbeitung: Anhang B der Doku — 33 Befunde, erhoben am 13. August 2026 von einer getrennten, rein lesenden Sitzung gegen den Stand `192fede`. Zehn sind erledigt (1, 2, 3, 4, 6, 10, 25, 26, 27, 29), darunter alle drei, die der Review als gravierend kennzeichnet. Kein Plan offen; als nächstes Abschnitt I ab Befund 5, dann II bis IV. Abschnitt VI des Reviews betrifft Sitzungsprotokolle und gehört nicht hierher, sondern zu Schritt 4.

2. **Anwenderdokumentation und README** aus Segment 1 ableiten (1.11 ist dafür als Vorlage angelegt). **Bedingung, die diesen Schritt auslöst, und der Grund für den Warnhinweis in der README:** Das Werkzeug läuft bisher ausschließlich beim Entwickler, als Quasi-Testbetrieb. Der Hinweis „Nicht benutzen" bleibt so lange stehen und entfällt erst, wenn es auch Kollegen benutzen dürfen — dieser Zeitpunkt ist der Anlass für die Anwenderdokumentation, nicht ein Restposten am Ende.

3. **Beobachtungsbetrieb:** Zu protokollieren, welche Dateien real Konfliktkopien erzeugen (F7) und ob das Überschreiben eine laufende Instanz stört (F3). Dabei einmal den **realen** Zwischennamen beim Empfang einer größeren Datei sehen — der Namensfilter aus 3.1 stützt sich bisher nur auf das dokumentierte Format (Kap. 3.8). Ebenfalls offen: F11, das Größenordnungsargument in 1.4 bei einem langlebigen Account gegenprüfen.

4. **Geparkter Fall: Konflikte in Sitzungsprotokollen.** Vollständig in `offener_fall_chatprotokolle.md`, nächste Schritte dort in Abschnitt 9. Bewusst **nicht** in die Doku eingepflegt, damit es einen Stand gibt, an dem Doku und Code widerspruchsfrei zueinander stehen und als Ausgangspunkt taugen.

5. **Zustandsverzeichnisse unter `~/.claude`: Ausschluss und Veraltung.** Zwei offene Entscheidungen, beide noch nicht getroffen. *Erstens der Ausschluss:* `paste-cache`, `image-cache` und `debug` sind laut Doku entbehrlich — beim Löschen geht „nothing user-facing" verloren, und der eingefügte Text selbst steht vollständig im Sitzungsprotokoll, der Cache trägt nur das erneute Absenden eines aus der Historie zurückgeholten Prompts; sein Fehlen ist ein vorgesehener Normalfall mit definiertem Verhalten. `todos`, `statsig` und `logs` sind Altlasten, die nicht mehr geschrieben werden. Alle sind Kandidaten für `.stignore` (maßgebliche Liste in 2.8). *Zweitens die Veraltung:* `plans/` und `tasks/` sind **kein** Cache, sondern Zustand, der beim Rechnerwechsel mitwandern muss. Dort ist nicht der Ausschluss das Problem, sondern dass ein Plan oder eine Aufgabenliste innerhalb einer Sitzung überholt wird, ohne dass der Nutzer das sieht — mit einer Ignore-Datei nicht lösbar. Dazu offen: ob `plansDirectory` (nimmt nur absolute oder `~/`-Pfade, aus Projekt-Einstellungen erst nach dem Workspace-Trust-Dialog wirksam) auf einen Ort im Projekt umgestellt wird. Belege: [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory), [Settings](https://code.claude.com/docs/en/settings), [Paste large content](https://code.claude.com/docs/en/terminal-config).

6. **Windows-Pendant** entwickeln (Kap. 3.7).

## Dauerhaft

- Die README trägt den Hinweis „Nicht benutzen!", solange das Werkzeug nicht zur Weitergabe freigegeben ist. **Widersprüche zwischen ihr und der Doku sind bis dahin erlaubt** und kein Befund — dieselbe Erlaubnis, die `chats-export` unter „Dauerhaft" führt. Sie gilt bis auf Widerruf und wird in jedem Vorhaben getrennt aufgehoben, nicht zentral; sie steht deshalb bewusst nicht in `.claude/CLAUDE.md`.
