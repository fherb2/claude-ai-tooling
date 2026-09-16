*Stand: 2026-09-15*

*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger, der den Skill auslöst. Beim Installieren: alles unterhalb der Trennlinie in die `CLAUDE.md` des Zielorts übernehmen; diese Datei bleibt dort liegen, wirksam ist allein die `CLAUDE.md`. Der Skill läuft ohne den Trigger nur bei ausdrücklichem `/git-branch-model`-Aufruf.*

*Der Wortlaut nennt die Anlässe als Ereignisse und bindet die Prüfung zusätzlich an eine Handlung — das erste schreibende Git-Kommando der Sitzung. Beim Anpassen darf der Anker verschoben, aber nicht weggelassen werden. Wichtiger noch als dieser Text ist die `description` des Skills: Sie entscheidet zuerst darüber, ob überhaupt ausgelöst wird.*

---

## Zweigmodell des Projekts

Will der Nutzer etwas in den Release bringen, einen Zweig anlegen oder
zusammenführen oder eine zentrale Datei des Projekts ändern (die
Projekt-CLAUDE.md, Editor- oder Werkzeugkonfiguration, `.gitignore`),
konsultiere zuerst den Skill `git-branch-model`.

Und bevor du in einer Sitzung zum ersten Mal ein schreibendes
Git-Kommando ausführst (`commit`, `add`, `push`, `checkout`, `restore`,
`reset`, `merge`), prüfe: Existiert im Projekt die Datei
`.claude/git-branch-model.json`? Dann konsultiere zuerst den Skill
`git-branch-model`.
