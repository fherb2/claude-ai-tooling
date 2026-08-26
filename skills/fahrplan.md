# Fahrplan des Vorhabens `skills/`

Die anstehenden Schritte in der Reihenfolge ihrer Bearbeitung. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben, neue Schritte zählen hoch.

Was hier **nicht** steht: der Zustand eines Skills und alles, was zwar geplant, aber noch nicht auf der Tagesordnung ist. Beides trägt die `README.md` des jeweiligen Skills. Der Fahrplan gibt die Folgeschritte der Projektbearbeitung vor, keine Zukunftsvisionen.

Eine `status.md` führt dieses Vorhaben nicht.

Die Nummern sind Kennungen, keine Reihenfolge: Maßgeblich ist, in welcher Folge die Schritte hier stehen. Ab Schritt 3 ist auch die nicht festgelegt — diese Schritte hängen nicht voneinander ab.

## 11 Englisch prüfen: Dateinamen, Skripte, Skript-Dokumentation

Das Repository liegt auf einer weltweit zugänglichen Plattform. Zu prüfen und gegebenenfalls zu korrigieren ist deshalb, ob **Dateinamen, Skripte und die Dokumentation von Skripten** durchgehend englisch sind. **Nicht** Gegenstand ist die deutsche Prosa: Die Arbeitssprache des Repositories bleibt Deutsch, und READMEs liegen ohnehin zweisprachig vor.

Dieser Schritt reicht über `skills/` hinaus und betrifft alle Bausteine; einen repository-weiten Fahrplan gibt es nicht, deshalb steht er hier. Wächst er, bekommt er einen eigenen Ort.

Zu durchsuchen sind drei Klassen:

- **Dateinamen.** Auffällig sind unter anderem `implementation_doku.md`, `implementierungs_doku.md`, `version2_fahrplan.md`, `chrome-zugriff.de.md`, `offener_fall_chatprotokolle.md`, `konfliktloesung.md`, `Syncthing-Synology-Konfigurationsanleitung-allgemein.md`, `fahrplan.md`, `noch-geplant.md` sowie die Skill-Ordner `tiefen-recherche` und `🚧_softwareaufgabe-erkennen`.
- **Skripte:** Bezeichner, Kommentare, Docstrings, Hilfetexte und Ausgaben an den Nutzer.
- **Dokumentation von Skripten** — also das, was einen Skriptaufruf, seine Parameter und seine Ausgabe erklärt, unabhängig davon, in welcher Datei es steht.

Vier Dinge machen daraus eine Prüfung mit Entscheidungen und keinen mechanischen Durchlauf:

1. **Jede Umbenennung zieht Verweise nach sich.** Ein Dateiname steht in READMEs, in der Doku und in Skripten; nach jeder Umbenennung gehört ein Suchlauf über den alten Namen dazu, sonst bleiben tote Verweise stehen.
2. **Bei Skill-Ordnern ist der Name die Schnittstelle.** Der Ordnername ist zugleich das Frontmatter-Feld `name` und damit der Slash-Aufruf. `tiefen-recherche` umzubenennen ändert `/tiefen-recherche` für jede bereits installierte Kopie — das ist eine Änderung am Verhalten, nicht an einer Datei, und muss einzeln entschieden werden.
3. **`fahrplan.md` und `status.md` sind von außen vorgegeben** (Arbeitsanweisungen §2.3). Ihre Namen zu ändern hieße, die globale `CLAUDE.md` zu ändern — das entscheidet der Entwickler, nicht dieser Schritt.
4. **Was in einer nicht-englischen Sprachfassung steht, bleibt dort.** Ein `.de.md` ist kein Verstoß, sondern die Kennzeichnung einer Sprachfassung.

Ergebnis des Schrittes ist zuerst eine **Liste der Fundstellen mit Vorschlag**, nicht eine ausgeführte Umbenennung. Entschieden wird je Fund.

## 3 Anweisungs-Inventar zuordnen

Die Posten des Anweisungs-Inventars (T1–T27; liegt in einem temporären Arbeitsordner, der nach Abschluss entfällt) werden einzeln zugeordnet. Claude reicht sie vorsortiert durch — gebündelt nach vorgeschlagenem Skill-Zuhause, je Posten mit Herkunft, Varianten und einem Geltungsbereichs-Vorschlag nach Kapitel 8.3 der `implementation_doku.md` (nur Coding / alle Arbeitsformen / andere) —, und der Entwickler legt je Posten die Zuordnung fest oder bestätigt sie. Maßstab der Verteilung ist das Arbeitsmodell in Kapitel 8.2. Die bestätigte Zuhause-Liste wird anschließend in der `implementation_doku.md` festgeschrieben; erst danach beginnt die Ausformulierung der einzelnen Skills.

Damit erledigt sich zugleich der übergreifend offene Punkt „Neuordnung der Arbeitsanweisungen zu Skill-Zuhausen“.

## 4 `🚧_translation-task`: die fünf offenen Festlegungen

Die fünf Punkte unter „Noch nicht festgelegt“ in der `SKILL.md` einzeln besprechen und dort festschreiben: Namenskonvention für Zieldateien, Sync-Workflow zwischen zwei Sprachfassungen, Umgang mit Lizenz- und Rechtstexten, Ein-Absatz-pro-Zeile-Formatierung, Ton und Anrede.

## 5 `🚧_software-dev-doc-fh`: Zugehörigkeit der beiden Werkzeug-Skills klären

Klären, ob die vorhandenen Skills `konzept-segmentierung` und `konsistenzpruefung` in dieses Vorhaben überführt und dem Namensschema angeglichen werden. Sie sind Werkzeuge innerhalb dieses Standards und liegen bisher nur unter `~/.claude/skills/`. Zu bedenken ist dabei: Sobald sie hier liegen, verstößt die `SKILL.md` mit ihrem Abschnitt „Zusammenspiel mit anderen Skills“ gegen Kapitel 2.3 der Vorgaben — kein Skill-Körper verweist auf einen anderen Skill dieses Verzeichnisses.

Bei dieser Gelegenheit fällt auch die Entscheidung über die Zweiteilung aus Schritt 2.

## 6 `🚧_softwareaufgabe-erkennen`: über den Fortbestand entscheiden

Entscheiden, ob daraus ein eigenständiger Skill wird, ob er die Vorstufe von `software-dev-doc-fh` ist — oder ob er sich mit `common-code-generation` erledigt hat, der inzwischen einen Teil davon trägt. Erst danach lohnt Arbeit am Inhalt. Fällt die Entscheidung für einen eigenen Skill: den Trigger nach Kapitel 2 der Vorgaben geankert neu formulieren, nicht als Hintergrund-Beobachtung.

## 7 `🚧_web-code-artefacts`: aus der Rohfassung einen Skill machen

- Frontmatter anlegen (`name`, `description`, `license`); die `description` nach Kapitel 2 der Vorgaben formulieren — dritte Person, Hauptanwendungsfall vorn.
- Den Text in Abschnitte gliedern und vom Ich-Ton der Vorlage („ich entscheide“, „sage mir also“) auf die Anrede an Claude umstellen.
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
