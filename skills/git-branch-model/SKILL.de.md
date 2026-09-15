---
name: git-branch-model
description: Regelt die Zweigführung eines Git-Projekts (Branch-Modell) — ein Entwicklungszweig als Hauptlinie, ein Release-Zweig für den veröffentlichten Stand, Themenzweige je Aufgabe und ein Verwaltungszweig für Dateien, die auf jedem Zweig gleich sein müssen (Projekt-CLAUDE.md, Editor- und Werkzeugkonfiguration, .gitignore), verteilt durch Überlagern statt Merge. Verwenden, sobald etwas in den Release oder nach master soll, ein Zweig angelegt oder zusammengeführt wird, eine zentrale Datei des Projekts geändert werden soll oder das Projekt die Datei .claude/git-branch-model.json führt, oder wenn der Nutzer /git-branch-model aufruft.
license: CC0-1.0
---

# Zweigführung eines Git-Projekts

Diese Datei klärt nur, ob das Zweigmodell in diesem Projekt gilt; die Rollen, Abläufe und Regeln stehen in einer Regeldatei desselben Ordners und werden erst geladen, wenn es gilt oder eingerichtet werden soll. Die Teilung ist Absicht: Der Skill löst auch in Projekten aus, die kein Zweigmodell führen, und dann bleibt der Kontext frei.

## Die Lage feststellen

1. **Das Projekt führt das Zweigmodell** — erkennbar an der Datei `.claude/git-branch-model.json`; die Namen der Zweige, die Art der Release-Übernahme und die Liste der Verwaltungsdateien stehen in dieser Datei, nicht im Skill. **Lies dann `${CLAUDE_SKILL_DIR}/rules.de.md` vollständig und arbeite ab dann danach.** Liegt dort keine Datei dieses Namens, sieh im Skill-Ordner nach, welche Regeldatei es gibt — beim Installieren kann umbenannt worden sein. Bevor Du sie gelesen hast, führe kein schreibendes Git-Kommando aus.
2. **Kein Zweigmodell, aber ein Anlass** — der Nutzer will etwas in den Release bringen, einen Zweig zusammenführen oder eine zentrale Datei ändern. Dann biete die Ersteinrichtung des Modells an — in zwei Sätzen und ohne Drängen, denn sie ändert seine Arbeitsweise. Will er sie, lies die Regeldatei wie in Fall 1: Die Ersteinrichtung steht dort.
3. **Weder noch:** Dieser Skill verlangt dann nichts, und die Regeldatei wird nicht geladen.

## Aufklären, statt vorauszusetzen

Wird dieser Skill in einem Projekt zum ersten Mal wirksam — bei der Ersteinrichtung oder beim ersten Eingriff, den der Nutzer nicht selbst verlangt hat —, sage in wenigen Sätzen, was das Modell tut und was Du gleich tun wirst. Der Nutzer hat den Skill womöglich nur installiert und sieht zu, was geschieht. Für alles Weitere liegt die README im Ordner dieses Skills: Nenne sie als Nachschlagewerk und zitiere bei Nachfragen aus ihr, statt zu rekonstruieren. Ihr Dateiname ist nicht verlässlich — sieh im Ordner nach; findest Du sie nicht, antworte ohne sie.
