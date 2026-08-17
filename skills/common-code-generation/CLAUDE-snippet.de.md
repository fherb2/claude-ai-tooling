*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger, der
den Skill auslöst. Beim Installieren: alles unterhalb der Trennlinie in die
`CLAUDE.md` des Zielorts übernehmen, danach diese Datei löschen. Der Skill
läuft ohne den Trigger nur bei ausdrücklichem
`/common-code-generation`-Aufruf.*

*Der Anker („bevor du in einer Sitzung zum ersten Mal …") darf beim Anpassen
an ein Projekt verschoben, aber nicht weggelassen werden. Er liegt bewusst so
früh: Der Skill ist ein Regelwerk, das ab der ersten Zeile Code gilt, und sein
Körper bleibt nach dem Laden für den Rest der Sitzung im Kontext — ein später
Treffer rettet die Entscheidungen nicht mehr, die vorher schon gefallen sind.*

---

## Regeln beim Schreiben von Code

Bevor du in einer Sitzung zum ersten Mal Quelltext schreibst oder
änderst, konsultiere den Skill `common-code-generation`. Das gilt
auch, wenn niemand von Code gesprochen hat und die Anfrage wie eine
Frage klingt — „warum bricht das Skript bei großen Dateien ab?",
„kannst du mal schauen, warum die Liste leer bleibt?" —, denn auch
daraus entsteht geänderter Quelltext. Du benötigst den Skill aber nicht für
Code, der unmittelbar in der Sitzung auf der CLI oder im Scratch ausgeführt
werden soll.
