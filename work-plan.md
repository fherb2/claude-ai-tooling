# Fahrplan des Repositories

Die anstehenden Schritte in der Reihenfolge ihrer Bearbeitung. Erledigte Schritte fliegen raus; die Nummern der übrigen werden dabei **nicht** neu vergeben, neue Schritte zählen hoch.

**Dieser Fahrplan gilt repository-weit.** Er lag bis zum 27. August 2026 in `skills/`, weil die Arbeit dort begann; seine Schritte betrafen aber längst alle Bereiche (zuletzt die Dateinamen-Prüfung und die Zielwelt-Sortierung). Vorhaben mit eigenem, abgegrenztem Entwicklungsstand führen daneben weiter ihren eigenen: `chat-export/work-plan-v2.md` und `home-.claude-sharing/work-plan.md`.

Was hier **nicht** steht: der Zustand eines Skills oder Bereichs und alles, was zwar geplant, aber noch nicht auf der Tagesordnung ist. Beides trägt die `README.md` des jeweiligen Skills bzw. Bereichs. Der Fahrplan gibt die Folgeschritte der Projektbearbeitung vor, keine Zukunftsvisionen.

Eine `status.md` führt das Vorhaben `skills/` nicht.

Die Nummern sind Kennungen, keine Reihenfolge: Maßgeblich ist, in welcher Folge die Schritte hier stehen. Ab Schritt 3 ist auch die nicht festgelegt — diese Schritte hängen nicht voneinander ab.

## 3 Anweisungs-Inventar zuordnen

Die Posten des Anweisungs-Inventars (T1–T27; liegt in einem temporären Arbeitsordner, der nach Abschluss entfällt) werden einzeln zugeordnet. Claude reicht sie vorsortiert durch — gebündelt nach vorgeschlagenem Skill-Zuhause, je Posten mit Herkunft, Varianten und einem Geltungsbereichs-Vorschlag nach Kapitel 8.3 der `skill-dev-doc.md` (nur Coding / alle Arbeitsformen / andere) —, und der Entwickler legt je Posten die Zuordnung fest oder bestätigt sie. Maßstab der Verteilung ist das Arbeitsmodell in Kapitel 8.2. Die bestätigte Zuhause-Liste wird anschließend in der `skill-dev-doc.md` festgeschrieben; erst danach beginnt die Ausformulierung der einzelnen Skills.

Damit erledigt sich zugleich der übergreifend offene Punkt „Neuordnung der Arbeitsanweisungen zu Skill-Zuhausen“.

**Der Schritt ist größer als sein ursprünglicher Zuschnitt und wird bei Beginn untergliedert** (Festlegung des Entwicklers vom 27. August 2026). Dreierlei dazu: T2, T12, T13 und T16 sind erledigt und aus Inventar wie Quelldateien entfernt (abgedeckt durch `common-code-generation` bzw. `temp-debug-code`). Die durch die globale CLAUDE.md abgedeckten Posten (T1, T3, T6, T7, T21, T22) gelten ausdrücklich **nicht** als erledigt — die globale CLAUDE.md wird selbst noch zu dynamisch ladenden Skills durchgearbeitet, und diese Posten sind dafür Referenzmaterial. Und die Zielwelt-Sortierung (Schritt 12) wirkt herein: Je Posten ist auch zu bestimmen, in welche Zielwelt-Gruppe sein Zuhause gehört.

## 4 `🚧_translation-task`: die fünf offenen Festlegungen

Die fünf Punkte unter „Noch nicht festgelegt“ in der `SKILL.md` einzeln besprechen und dort festschreiben: Namenskonvention für Zieldateien, Sync-Workflow zwischen zwei Sprachfassungen, Umgang mit Lizenz- und Rechtstexten, Ein-Absatz-pro-Zeile-Formatierung, Ton und Anrede.

## 5 `🚧_software-dev-doc-fh`: Zugehörigkeit der beiden Werkzeug-Skills klären

Klären, ob die vorhandenen Skills `konzept-segmentierung` und `konsistenzpruefung` in dieses Vorhaben überführt und dem Namensschema angeglichen werden. Sie sind Werkzeuge innerhalb dieses Standards und liegen bisher nur unter `~/.claude/skills/`. Zu bedenken ist dabei: Sobald sie hier liegen, verstößt die `SKILL.md` mit ihrem Abschnitt „Zusammenspiel mit anderen Skills“ gegen Kapitel 2.3 der Vorgaben — kein Skill-Körper verweist auf einen anderen Skill dieses Verzeichnisses.

Bei dieser Gelegenheit fällt auch die Entscheidung über die Zweiteilung aus Schritt 2.

## 6 `🚧_software-task-detection`: über den Fortbestand entscheiden

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

## 9 `in-depth-online-literature-research`: zwei Erprobungen nachholen

Der Skill bleibt dabei **benutzbar** — beide Punkte betreffen die Absicherung, nicht die Funktion. Dass ein Skill irgendwann einen nicht absehbaren Fehler hervorruft, lässt sich ohnehin nicht ausschließen; das ist kein Grund, ihn als unfertig zu führen.

- Die Wirksamkeit des Selbsttests nachmessen. Der passende Prüffall: eine Wiederholung der Sammelrecherche mit anschließendem Abgleich aller Links gegen die tatsächlich abgerufenen Seiten.
- Den claude.ai-Zweig der Ergebnisübergabe (automatisches Artefakt) dort erproben.

## 12 Bereiche und Skills nach Zielwelt sortieren

Alle Bereiche und Skills des Repos werden in drei Gruppen sortiert (Festlegung des Entwicklers vom 27. August 2026): **web- und Claude-Code-fähig**, **nur Claude-Code-fähig** und **nur web-fähig** (claude.ai). Manche Skills wird es in beiden Zielwelten in abgewandelter Form geben, weil der Claude-Code-Wortlaut auf claude.ai so nicht funktioniert. Das Ergebnis wird als Festlegung in der `skill-dev-doc.md` festgeschrieben; die Zuordnung je Posten in Schritt 3 benutzt dieselben Gruppen.

## 13 `pedantic-text-editing`: die Ausführung einem Skript übergeben

**Betriebsbefund des Entwicklers vom 27. August 2026:** Nach der Freigabe — oft „alle" — führt die Instanz jede einzelne Änderung als eigene Werkzeugoperation aus. Bei einer Runde mit bis zu 30 Stellen dauert das sehr lange, und der Aufwand wächst mit jeder Stelle, obwohl der Vorgang mechanisch ist: Alle Angaben liegen zum Zeitpunkt der Ausführung bereits vor — Vorher-Stück, Nachher-Stück, Zeilennummer, und zwar bezogen auf die **unveränderte** Ausgangsdatei.

**Ansatz:** Ein Skript im Skill-Ordner führt die freigegebenen Ersetzungen in einem Lauf aus. Seine Datenquelle ist die Befunddatei, die ohnehin vor der Ausführung entsteht und committet wird (Abschnitt 8 und 11 der Regeln): Sie trägt je Fund die ID, die Zeilennummer, Vorher und Nachher in leerraumtreuen Codeblöcken sowie den Freigabestand in der Blocküberschrift.

**Vor dem Bau zu klären:**

- **Mehrere Funde in derselben Zeile** sind der Normalfall (im Beispiel des Entwicklers zweimal Zeile 17, zweimal Zeile 42). Das Skript muss sie nacheinander auf dieselbe Zeile anwenden und melden, wenn zwei Vorher-Stücke einander überlappen.
- **Die Zeilennummer bezieht sich auf den Ausgangsstand.** Solange keine Ersetzung Zeilen hinzufügt oder entfernt, bleibt sie gültig; ob mehrzeilige Ersetzungen überhaupt zugelassen werden, ist zu entscheiden.
- **Eindeutigkeit:** Innerhalb der genannten Zeile muss das Vorher-Stück genau einmal vorkommen. Trifft es mehrfach oder gar nicht, wird die Stelle nicht geraten, sondern gemeldet — dieselbe Regel wie heute in Abschnitt 10.
- **Freigabestand:** Woher nimmt das Skript, welche IDs freigegeben sind? Entweder aus der Blocküberschrift der Befunddatei oder als Aufrufparameter; beides ist möglich, eines ist festzulegen.
- **Die Gegenprobe bleibt Pflicht** (Abschnitt 11) und wird nicht durch das Skript ersetzt. Sie kann aber von ihm gestützt werden: Trefferzahl gegen freigegebene IDs, dazu weiterhin der Blick in `git diff`.
- **Format-Empfindlichkeit:** Der Parser liest eine Markdown-Datei. Fasst ein Editor sie an, kann Leerraum verlorengehen — genau der Grund, aus dem die Befunddatei heute schon Blöcke statt Tabellenzeilen benutzt. Das Skript muss einen unlesbaren Block melden statt ihn zu überspringen.

**Zusammenhang mit Schritt 12:** Dasselbe Skript ist der einzige bekannte Weg zu einer Web-Fassung, die ihr Detailtreue-Versprechen mechanisch hält — auf claude.ai läuft der Rückweg sonst durch die Inferenz und erzeugt eine Abschrift. Die Entscheidung über die Web-Fassung sollte deshalb nach diesem Schritt fallen, nicht davor.
