# Fahrplan: Nachladbare Claude-Code-Skills

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details zu jedem Schritt stehen in `implementation_doku.md`. Abgeschlossene Schritte werden aus dieser Liste vollständig entfernt, nicht nur markiert; sie erscheinen danach als Zeile in `status.md`. Nummern erledigter Schritte werden beim Streichen nicht neu vergeben (repo-weite Regel, `.claude/CLAUDE.md`).

## Schritte

1. **Design des ersten Skills (Übersetzung software-entwicklungsnaher Dokumente) besprechen — Punkt für Punkt, nicht alles auf einmal.** Bereits geklärt: Vorhaben-Status (eigenständig), Speicherort-Semantik, Testverfahren, Doku-Struktur. Noch offen und als Nächstes dran: ob und wie der Skill den Nutzer bei Aktivierung selbst nach bestimmten Entscheidungen fragt (z. B. Übersetzungsrichtung, ob der Sync-Workflow — eine Änderung aus einer Sprachfassung in die andere nachziehen — mit abgedeckt wird), um nicht für jede Nuance einen eigenen, fast identischen Skill zu brauchen.
2. Danach die Glossar-Idee (feste Begriffsliste für Terminologie-Entscheidungen wie „Pipe bleibt Pipe") bei der inhaltlichen Ausgestaltung einbringen.
3. Danach die restlichen offenen Punkte einzeln besprechen: Umgang mit Codeblöcken (wörtliche Wiedergabe vs. illustrative Beispiele), Umgang mit Eigennamen/Produktnamen und wörtlichen Code-Markern, Namenskonvention für Zieldateien (`<datei>.de.md`), Standard-Umgang mit Lizenz-/Rechtstexten, Ein-Absatz-pro-Zeile-Formatierung, Ton/Anrede.
4. `README.md` (Deutsch) für dieses Vorhaben erstellen — welche Lizenz dafür anwendbar ist, ist noch zu klären.
5. Segment 2 (Vorgaben) füllen, sobald projektweite Festlegungen abgestimmt sind.
6. Ersten Skill entwerfen und als erstes Kapitel in Segment 3 dokumentieren.
7. Klären, ob der automatische „Transport" eines fertigen Skills an seinen Zielort (`.claude/skills/` bzw. `~/.claude/skills/`) Teil dieses Vorhabens werden soll, oder ob das dauerhaft beim Nutzer bzw. bei `home-.claude-sharing` bleibt.
