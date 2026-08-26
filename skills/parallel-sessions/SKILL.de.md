---
name: parallel-sessions
description: Führt die Zusammenarbeit mehrerer gleichzeitig arbeitender Claude-Code-Sitzungen im selben Repository — jede Sitzung auf eigener Werkbank in einem eigenen Git-Worktree, zentrale Dateien wie die CLAUDE.md über einen Infra-Branch verteilt, Abschluss per Squash-Merge. Verwenden, sobald der Nutzer einen zweiten offenen Chat, eine zweite Claude-Instanz oder gleichzeitige Arbeit erwähnt, fremde Änderungen im Arbeitsbaum auftauchen, eine Sitzung in einem Git-Worktree beginnt oder das Projekt das Worktree-Arbeitsmodell vereinbart hat, oder wenn der Nutzer /parallel-sessions aufruft.
license: CC0-1.0
---

# Parallele Claude-Sitzungen über Git-Worktrees

Diese Datei klärt nur, welcher Fall vorliegt; die Abläufe und Regeln des Arbeitsmodells stehen in einer Regeldatei desselben Ordners und werden erst geladen, wenn das Modell hier wirklich gilt. Die Teilung ist Absicht: Der Skill löst auch in Sitzungen aus, in denen das Modell nicht vereinbart ist, und dann bleibt der Kontext frei.

## Die Lage feststellen

Prüfe zuerst, welcher der drei Fälle vorliegt:

1. **Das Projekt hat das Worktree-Arbeitsmodell vereinbart** — erkennbar an der Datei `.claude/git-worktree-model.json`; die Namen von Branches, Ablageort und Infra-Dateien stehen in dieser Datei, nicht im Skill. **Lies dann `${CLAUDE_SKILL_DIR}/rules.de.md` vollständig und arbeite ab dann danach.** Liegt dort keine Datei dieses Namens, sieh im Skill-Ordner nach, welche Regeldatei es gibt — beim Installieren kann umbenannt worden sein. Bevor Du sie gelesen hast, führe kein schreibendes Git-Kommando aus.
2. **Kein Modell vereinbart, aber eine zweite Sitzung arbeitet oder ist angekündigt.** Dann gilt die Sofortregel (nächster Abschnitt), und dem Nutzer wird die Ersteinrichtung des Modells angeboten — kurz und ohne Drängen, denn sie ändert seine Arbeitsweise. Will er sie, lies die Regeldatei wie in Fall 1: Die Ersteinrichtung steht dort.
3. **Weder noch** — eine einzelne Sitzung, kein Modell: Dieser Skill verlangt dann nichts, und die Regeldatei wird nicht geladen.

Ob die laufende Sitzung selbst in einem Worktree steht, zeigt `git rev-parse --git-dir --git-common-dir`: Unterscheiden sich die beiden Pfade, ist es ein Worktree.

## Sofortregel ohne vereinbartes Modell: Schreibhoheit klären

Frage den Nutzer, **welche Sitzung eigenständig schreibende Git-Kommandos ausführen darf** (`commit`, `add`, `push`, `checkout`, `restore`, `reset`, `merge`). Bis zur Antwort führt diese Sitzung keines davon aus; lesende Kommandos (`status`, `diff`, `log`, `fetch`) bleiben erlaubt. Einmal erteilte Hoheit gilt für die Sitzung fort; umverteilen kann der Nutzer sie jederzeit, dafür meldet er sich aktiv.

Diese Regel ist der Rückfallweg. Sie wird vom Worktree-Modell abgelöst, sobald es eingerichtet ist: Dann braucht niemand mehr eine Hoheit, weil keine zwei Sitzungen denselben Arbeitsbaum teilen.
