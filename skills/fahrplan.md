# Fahrplan des Vorhabens `skills/`

Die anstehenden Schritte in der Reihenfolge ihrer Bearbeitung. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben, neue Schritte zählen hoch.

Was hier **nicht** steht: der Zustand eines Skills und alles, was zwar geplant, aber noch nicht auf der Tagesordnung ist. Beides trägt die `README.md` des jeweiligen Skills. Der Fahrplan gibt die Folgeschritte der Projektbearbeitung vor, keine Zukunftsvisionen.

Eine `status.md` führt dieses Vorhaben nicht.

Die Reihenfolge ist ab Schritt 4 nicht festgelegt — diese Schritte hängen nicht voneinander ab.

## 1 Durchsicht des Regeltextes von `pedantic-text-editing`

Läuft. Der Skill liegt auf der Werkbank `claude-wb/pedantic-text-editing`, noch nicht auf `dev`. Der ausdetaillierte Plan des Schrittes steht dort unter „Offen" in `skills/🚧_pedantic-text-editing/README.md`, weil er den Inhalt des Skills betrifft und mit ihm zusammen übernommen wird. Nach der Durchsicht: beide Sprachfassungen nachziehen, `ziel.md` entfernen, stillen Trigger schreiben, Baustellenschild entfernen.

## 2 Zweiteilung nachziehen

Ergebnis der Durchsicht vom 25. August 2026: Alle zehn Skills des Repos wurden gegen Kapitel 5.2 der Vorgaben geprüft. Ein Skill ist ein klarer Fall, drei brauchen eine Reaktion anderer Art.

- **`parallel-sessions` teilen.** Der Skill hat die Konstruktion bereits, ohne sie zu nutzen: „Die Lage feststellen" endet in Fall 3 mit „Dieser Skill verlangt dann nichts", und das ist in jedem Projekt ohne `.claude/git-worktree-model.json` der Normalfall. Im Gate bleiben Frontmatter, Lagefeststellung und die **Sofortregel** — letztere gilt gerade dann, wenn kein Modell vereinbart ist, also in dem Fall, in dem der Regelteil nie geladen wird. Ab „Das Arbeitsmodell" wandert alles in die nachgeladene Regeldatei; gemessen am Stand vom 25. August sind das Zeile 27 bis 152 gegen 26 Zeilen Gate. Beide Sprachfassungen, beide READMEs. Anschließend `dev` und `master`, danach installiert der Entwickler neu — die bereits installierte Fassung ist dann überholt.
- **Vorgaben 5.2 um eine dritte Bedingung ergänzen:** Die Entscheidung muss **ohne** den Regelteil zu treffen sein. Beleg ist `correct-zaaack-md-editor-mistakes`: Er erfüllt beide bisherigen Bedingungen — es gibt eine Klärung, ob das Projekt betroffen ist, und ein Nein ist realistisch —, lässt sich aber trotzdem nicht teilen, weil die Entscheidung erst nach einem Lauf der Werkzeuge fällt und die stehen im größten Teil des Regeltextes. In der README dieses Skills festhalten, dass die Teilung geprüft und verworfen wurde, damit die nächste Durchsicht ihn nicht erneut meldet.
- **`chat-export` vormerken.** Der Skill bricht hart ab, wenn die Browser-Werkzeuge nicht an der Nachricht hängen — ein häufiger und bei 167 Zeilen teurer Ausgang. Er gehört aber zu einem eigenen Vorhaben mit eigenen Vorgaben; vor einer Umsetzung sind dessen Regeln ausführlich zu prüfen, statt Kapitel 5.2 dorthin zu übertragen.
- **`🚧_software-dev-doc-fh`** bekommt keine eigene Runde. Der Skill hat bisher gar keinen Klärungsschritt, es wäre also einer zu entwerfen und nicht einer umzubauen. Das wird bei der Arbeit an diesem Skill mitentschieden; der Hinweis steht in seiner README.

## 3 Anweisungs-Inventar zuordnen

Die Posten des Anweisungs-Inventars (T1–T27; liegt in einem temporären Arbeitsordner, der nach Abschluss entfällt) werden einzeln zugeordnet. Claude reicht sie vorsortiert durch — gebündelt nach vorgeschlagenem Skill-Zuhause, je Posten mit Herkunft, Varianten und einem Geltungsbereichs-Vorschlag nach Kapitel 8.3 der `implementation_doku.md` (nur Coding / alle Arbeitsformen / andere) —, und der Entwickler legt je Posten die Zuordnung fest oder bestätigt sie. Maßstab der Verteilung ist das Arbeitsmodell in Kapitel 8.2. Die bestätigte Zuhause-Liste wird anschließend in der `implementation_doku.md` festgeschrieben; erst danach beginnt die Ausformulierung der einzelnen Skills.

Damit erledigt sich zugleich der übergreifend offene Punkt „Neuordnung der Arbeitsanweisungen zu Skill-Zuhausen".

## 4 `🚧_translation-task`: die fünf offenen Festlegungen

Die fünf Punkte unter „Noch nicht festgelegt" in der `SKILL.md` einzeln besprechen und dort festschreiben: Namenskonvention für Zieldateien, Sync-Workflow zwischen zwei Sprachfassungen, Umgang mit Lizenz- und Rechtstexten, Ein-Absatz-pro-Zeile-Formatierung, Ton und Anrede.

## 5 `🚧_software-dev-doc-fh`: Zugehörigkeit der beiden Werkzeug-Skills klären

Klären, ob die vorhandenen Skills `konzept-segmentierung` und `konsistenzpruefung` in dieses Vorhaben überführt und dem Namensschema angeglichen werden. Sie sind Werkzeuge innerhalb dieses Standards und liegen bisher nur unter `~/.claude/skills/`. Zu bedenken ist dabei: Sobald sie hier liegen, verstößt die `SKILL.md` mit ihrem Abschnitt „Zusammenspiel mit anderen Skills" gegen Kapitel 2.3 der Vorgaben — kein Skill-Körper verweist auf einen anderen Skill dieses Verzeichnisses.

Bei dieser Gelegenheit fällt auch die Entscheidung über die Zweiteilung aus Schritt 2.

## 6 `🚧_softwareaufgabe-erkennen`: über den Fortbestand entscheiden

Entscheiden, ob daraus ein eigenständiger Skill wird, ob er die Vorstufe von `software-dev-doc-fh` ist — oder ob er sich mit `common-code-generation` erledigt hat, der inzwischen einen Teil davon trägt. Erst danach lohnt Arbeit am Inhalt. Fällt die Entscheidung für einen eigenen Skill: den Trigger nach Kapitel 2 der Vorgaben geankert neu formulieren, nicht als Hintergrund-Beobachtung.

## 7 `🚧_web-code-artefacts`: aus der Rohfassung einen Skill machen

- Frontmatter anlegen (`name`, `description`, `license`); die `description` nach Kapitel 2 der Vorgaben formulieren — dritte Person, Hauptanwendungsfall vorn.
- Den Text in Abschnitte gliedern und vom Ich-Ton der Vorlage („ich entscheide", „sage mir also") auf die Anrede an Claude umstellen.
- Entscheiden, ob der Skill einen stillen Trigger braucht. Der Auslöser — es entsteht Code im Web-Frontend — ist eine Umgebungsbedingung, keine Anfrage; die reguläre Description erreicht ihn womöglich nicht.
- Klären, ob der Skill überhaupt in Claude Code gehört: Artefakte gibt es dort nicht. Möglicherweise ist sein Zielort ausschließlich claude.ai.

## 8 `🚧_zotero-use`: Probelauf und Werkzeugentscheidung

- Probelauf gegen das echte Konto: Lesen sofort, Schreiben mit frisch erzeugtem Zotero-Web-API-Key gegen eine Wegwerf-Testsammlung (nichts Echtes riskieren).
- Dabei klären, ob `zotero-cli-cc` Sammlungs-Management schon kann oder ob ein dünner Zusatz nötig ist.
- Danach erst: Werkzeug-Entscheidung (`zotero-cli-cc` vs. `zotero-mcp` vs. Plugin-Variante `cookjohn/zotero-mcp`) und Verpackung als Skill.

## 9 `tiefen-recherche`: zwei Erprobungen nachholen

Der Skill bleibt dabei **benutzbar** — beide Punkte betreffen die Absicherung, nicht die Funktion. Dass ein Skill irgendwann einen nicht absehbaren Fehler hervorruft, lässt sich ohnehin nicht ausschließen; das ist kein Grund, ihn als unfertig zu führen.

- Die Wirksamkeit des Selbsttests nachmessen. Der passende Prüffall: eine Wiederholung der Sammelrecherche mit anschließendem Abgleich aller Links gegen die tatsächlich abgerufenen Seiten.
- Den claude.ai-Zweig der Ergebnisübergabe (automatisches Artefakt) dort erproben.
