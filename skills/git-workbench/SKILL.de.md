---
name: git-workbench
description: Regelt, wie eine Claude-Sitzung in einem Git-Repository committet — direkt auf dem aktuellen Zweig, auf einer eigenen Werkbank mit Absicherungs-Commits und Squash-Abschluss, oder isoliert in einem eigenen Git-Worktree, wenn mehrere Sitzungen gleichzeitig arbeiten. Verwenden, bevor in einer Sitzung zum ersten Mal ein schreibendes Git-Kommando ausgeführt wird, sobald der Nutzer einen zweiten offenen Chat oder eine zweite Claude-Instanz erwähnt, fremde Änderungen im Arbeitsbaum auftauchen oder die Sitzung in einem Git-Worktree beginnt, oder wenn der Nutzer /git-workbench aufruft.
license: CC0-1.0
---

# Wie diese Sitzung committet

Diese Datei klärt nur die Betriebsart; die Abläufe und Regeln stehen in Regeldateien desselben Ordners und werden erst geladen, wenn feststeht, was gebraucht wird. Die Teilung ist Absicht: Die Maschinerie für parallele Sitzungen kostet in den anderen Betriebsarten keinen Kontext.

## Die Betriebsart bestimmen

Lies `.claude/git-workbench.json`, Feld `mode`. Fehlt die Datei oder das Feld, gilt `ask`.

| `mode` | Bedeutung |
| --- | --- |
| `direct` | Commits direkt auf dem Zweig, auf dem die Sitzung steht; jeder freigegebene Schritt ein dauerhafter Commit. Eine gültige Betriebsart, keine Abweichung — sie wird nicht erneut in Frage gestellt. |
| `workbench` | Eine eigene Werkbank (ein kurzlebiger Zweig) mit Absicherungs-Commits, am Ende ein Squash in Menschenkörnung. |
| `worktree` | Wie `workbench`, aber in einem eigenen Worktree — für mehrere Sitzungen gleichzeitig. |
| `ask` | Du fragst — einmal je Sitzung, beim ersten schreibenden Git-Kommando. |

**Bei `ask`:** Nenne den Zweig, auf dem die Sitzung steht, und die Lage: Steht die Sitzung in einem Worktree (`git rev-parse --git-dir --git-common-dir` — zwei verschiedene Pfade heißen ja)? Ist eine zweite Sitzung erwähnt, tauchen fremde Änderungen auf? Schlage daraus eine Betriebsart vor und frage. Die Antwort gilt für die Sitzung. Steht die Sitzung bereits in einem Worktree, ist die Betriebsart `worktree`, ohne Frage.

**Zweite Sitzung ohne Isolation.** Ist eine zweite Sitzung im Spiel und die Betriebsart nicht `worktree`, gilt zuerst die Sofortregel: Frage den Nutzer, **welche Sitzung eigenständig schreibende Git-Kommandos ausführen darf** (`commit`, `add`, `push`, `checkout`, `restore`, `reset`, `merge`). Bis zur Antwort führt diese Sitzung keines davon aus; lesende Kommandos (`status`, `diff`, `log`, `fetch`) bleiben erlaubt. Einmal erteilte Hoheit gilt für die Sitzung fort. Biete `worktree` an — kurz, ohne Drängen —, denn dann braucht niemand mehr eine Hoheit: Keine zwei Sitzungen teilen dann denselben Arbeitsbaum.

## Den Entwicklungszweig kennen

Werkbank und Squash brauchen einen Zielzweig. Führt das Projekt die Datei `.claude/git-branch-model.json`, steht er dort im Feld `integration_branch`. Sonst frage den Nutzer einmal je Sitzung — mit dem gerade ausgecheckten Zweig als Vorschlag, nicht als Annahme. Speichere den Wert nirgends.

## Regeln laden

- In jeder Betriebsart, sobald ein schreibendes Git-Kommando ansteht: **`${CLAUDE_SKILL_DIR}/rules.de.md` vollständig lesen** und ab dann danach arbeiten.
- In `worktree` zusätzlich **`rules-worktree.de.md`** aus demselben Ordner — vor dem ersten `git worktree`-Kommando.

Liegt keine Datei dieses Namens dort, sieh im Skill-Ordner nach, welche Regeldateien es gibt — beim Installieren kann umbenannt worden sein. Bevor Du gelesen hast, führe kein schreibendes Git-Kommando aus.

## Aufklären, statt vorauszusetzen

Wird dieser Skill in einem Projekt zum ersten Mal wirksam — bei der ersten Frage in `ask`, beim Anlegen der ersten Werkbank, bei der Ersteinrichtung —, sage in wenigen Sätzen, was Du gleich tust und warum. Der Nutzer hat den Skill womöglich nur installiert und sieht zu, was geschieht. Für alles Weitere liegt die README im Ordner dieses Skills: Nenne sie als Nachschlagewerk und zitiere bei Nachfragen aus ihr, statt zu rekonstruieren. Ihr Dateiname ist nicht verlässlich — sieh im Ordner nach; findest Du sie nicht, antworte ohne sie.
