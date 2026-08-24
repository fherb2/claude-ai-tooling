*Stand: 2026-08-24*

*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger, der den Skill auslöst. Beim Installieren: alles unterhalb der Trennlinie in die `CLAUDE.md` des Zielorts übernehmen; diese Datei bleibt dort liegen, wirksam ist allein die `CLAUDE.md`. Der Skill läuft ohne den Trigger nur bei ausdrücklichem `/parallel-sessions`-Aufruf.*

*Der Wortlaut nennt die Anzeichen als Ereignisse und bindet die Prüfung zusätzlich an eine Handlung — das erste schreibende Git-Kommando der Sitzung. Beim Anpassen darf der Anker verschoben, aber nicht weggelassen werden. Wichtiger noch als dieser Text ist die `description` des Skills: Sie entscheidet zuerst darüber, ob überhaupt ausgelöst wird.*

---

## Parallele Sitzungen und Worktree-Arbeitsmodell

Erwähnt der Nutzer einen zweiten offenen Chat, eine zweite Claude-Instanz
oder gleichzeitige Arbeit an diesem Repository, konsultiere sofort den
Skill `parallel-sessions`. Ebenso, wenn im Arbeitsbaum Änderungen
auftauchen, die nicht aus dieser Sitzung stammen.

Und bevor du in einer Sitzung zum ersten Mal ein schreibendes
Git-Kommando ausführst (`commit`, `add`, `push`, `checkout`, `restore`,
`reset`, `merge`), prüfe: Liegt einer dieser Fälle vor, arbeitet diese
Sitzung in einem Git-Worktree, oder existiert im Projekt die Datei
`.claude/git-worktree-model.json`? Dann konsultiere zuerst den Skill
`parallel-sessions`.
