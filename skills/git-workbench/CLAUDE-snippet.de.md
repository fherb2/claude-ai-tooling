*Stand: 2026-09-15*

*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger, der den Skill auslöst. Beim Installieren: alles unterhalb der Trennlinie in die `CLAUDE.md` des Zielorts übernehmen; diese Datei bleibt dort liegen, wirksam ist allein die `CLAUDE.md`. Der Skill läuft ohne den Trigger nur bei ausdrücklichem `/git-workbench`-Aufruf.*

*Der Wortlaut nennt die Anzeichen als Ereignisse und bindet die Prüfung zusätzlich an eine Handlung — das erste schreibende Git-Kommando der Sitzung. Beim Anpassen darf der Anker verschoben, aber nicht weggelassen werden. Wichtiger noch als dieser Text ist die `description` des Skills: Sie entscheidet zuerst darüber, ob überhaupt ausgelöst wird.*

---

## Commits dieser Sitzung: direkt, Werkbank oder Worktree

Erwähnt der Nutzer einen zweiten offenen Chat, eine zweite Claude-Instanz
oder gleichzeitige Arbeit an diesem Repository, konsultiere sofort den
Skill `git-workbench`. Ebenso, wenn im Arbeitsbaum Änderungen auftauchen,
die nicht aus dieser Sitzung stammen, oder die Sitzung in einem
Git-Worktree beginnt.

Und bevor du in einer Sitzung zum ersten Mal ein schreibendes
Git-Kommando ausführst (`commit`, `add`, `push`, `checkout`, `restore`,
`reset`, `merge`), konsultiere zuerst den Skill `git-workbench`: Er
klärt, in welcher Betriebsart diese Sitzung committet.
