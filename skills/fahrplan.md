# Fahrplan: Nachladbare Claude-Code-Skills

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details zu jedem Schritt stehen in `implementation_doku.md`. Abgeschlossene Schritte werden aus dieser Liste vollständig entfernt, nicht nur markiert; sie erscheinen danach als Zeile in `status.md`. Nummern erledigter Schritte werden beim Streichen nicht neu vergeben (repo-weite Regel, `.claude/CLAUDE.md`).

## Schritte

3. Die verbliebenen offenen Punkte des Übersetzungs-Skills einzeln besprechen und in `SKILL.md` sowie Kapitel 3.1 festschreiben: Namenskonvention für Zieldateien (`<datei>.de.md`), Sync-Workflow (Änderung von einer Sprachfassung in die andere nachziehen), Standard-Umgang mit Lizenz- und Rechtstexten, Ein-Absatz-pro-Zeile-Formatierung, Ton und Anrede.
7. Klären, ob der automatische „Transport" eines fertigen Skills an seinen Zielort (`.claude/skills/` bzw. `~/.claude/skills/`) Teil dieses Vorhabens werden soll, oder ob das dauerhaft beim Nutzer bzw. bei `home-.claude-sharing` bleibt.
9. Die drei Skill-Entwürfe (`translation-task`, `parallel-sessions`, `software-dev-doc-fh`) mit dem Nutzer durchgehen — Inhalt, Umfang, Wortlaut der Trigger — und freigeben oder überarbeiten. Grundlage sind die bestehenden `CLAUDE.md`-Dateien in diesem Repo, im Home-Verzeichnis und in den übrigen Projekten unter `~/git/`.
10. Für `parallel-sessions` die beiden offenen Festlegungen entscheiden (Kapitel 3.2): Branch-Benennung der Werkbank im Worktree-Modus und Umgang mit `arbeitsdaten.json` beim Zusammenführen. Ergebnis gehört in die `CLAUDE.md` der betroffenen Projekte, nicht in den Skill.
11. Für „Softwareaufgabe erkennen" (Kapitel 3.4) entscheiden, ob es ein eigenständiger Skill oder die Vorstufe von `software-dev-doc-fh` wird; den Trigger dabei nach Vorgabe 2.1 geankert neu formulieren.
12. Die freigegebenen Skills an ihren Zielorten installieren und im Alltag erproben — insbesondere, ob die stillen Trigger im echten Betrieb zuverlässig und ohne Fehlauslösungen greifen.
13. Klären, ob die vorhandenen Skills `konzept-segmentierung` und `konsistenzpruefung` in dieses Vorhaben überführt und dem Namensschema angeglichen werden.
14. Den stillen Trigger von `common-code-generation-de` nach 1.6 messen: Wegwerf-Projekt mit Ladeindikator, Description des echten Skills, nicht-interaktive Läufe gegen Sonnet. Beide Bedingungen einzeln prüfen — den Anker an einer Anfrage, die wie eine reine Frage klingt und in einer Codeänderung endet, und das Frontend-Ereignis. Ergebnis in Kapitel 3.5 nachtragen.
15. `common-code-generation-de` in die `README.md` aufnehmen (Abschnitt „Die Skills im Einzelnen" nach Vorgabe 2.3); dort stehen bisher nur die drei zuerst entwickelten Skills.
