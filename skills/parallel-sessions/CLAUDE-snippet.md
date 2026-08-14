*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger, der
den Skill auslöst. Beim Installieren: alles unterhalb der Trennlinie in die
`CLAUDE.md` des Zielorts übernehmen, danach diese Datei löschen. Der Skill
läuft ohne den Trigger nur bei ausdrücklichem `/parallel-sessions`-Aufruf.*

*Der Wortlaut nennt die Anzeichen als Ereignisse und bindet die Prüfung
zusätzlich an eine Handlung — das erste schreibende Git-Kommando der
Sitzung. Beim Anpassen darf der Anker verschoben, aber nicht weggelassen
werden. Wichtiger noch als dieser Text ist die `description` des Skills:
Sie entscheidet zuerst darüber, ob überhaupt ausgelöst wird.*

---

## Parallel arbeitende Claude-Instanzen

Erwähnt der Nutzer einen zweiten offenen Chat, eine zweite Claude-Instanz
oder gleichzeitige Arbeit an diesem Repository, konsultiere sofort den
Skill `parallel-sessions`. Ebenso, wenn im Arbeitsbaum Änderungen
auftauchen, die nicht aus dieser Sitzung stammen.

Und bevor du in einer Sitzung zum ersten Mal ein schreibendes
Git-Kommando ausführst (`commit`, `add`, `push`, `checkout`, `restore`,
`reset`, `merge`), prüfe, ob einer dieser Fälle vorliegt.
