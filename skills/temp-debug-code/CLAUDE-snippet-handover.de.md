*Stand: 2026-08-29*

*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger für
Umgebungen ohne unmittelbaren Zugriff auf den Dateibaum — claude.ai und
Claude Desktop. Für Claude Code gilt stattdessen
`CLAUDE-snippet-local.de.md`; übernommen wird immer nur eine der beiden.
Beim Installieren: alles unterhalb der Trennlinie in das Anweisungsfeld des
Zielorts übernehmen — global für das Konto oder je Projekt. Der Skill läuft
ohne den Trigger nur bei ausdrücklichem `/temp-debug-code`-Aufruf.*

*Der Auslöser ist hier ein anderer als bei Claude Code: Claude fügt nichts
selbst ein, sondern schlägt es dem Nutzer vor. Der Wortlaut bindet deshalb
an den Vorschlag, nicht an die Ausführung. Der Satz „auch dann, wenn der
Nutzer nicht von Debugging gesprochen hat“ ist auch hier der wirksame Teil
— er fragt „warum kommt hier 3 raus?“, und dass daraus eine Probe wird,
entscheidet Claude. Der zweite Absatz sorgt dafür, dass die Frage nach der
Kennzeichnung einmal gestellt wird, bevor der Nutzer die erste Zeile von
Hand einträgt; danach ist es zu spät.*

---

## Temporärer Debug-Code

Sobald du dem Nutzer eine Code-Änderung vorschlägst, die nur der
Fehlersuche dient — eine `print`- oder Log-Ausgabe, einen festen Testwert,
eine übersprungene Prüfung, eine zum Testen auskommentierte Zeile —,
konsultiere zuvor den Skill `temp-debug-code`. Das gilt auch dann, wenn
der Nutzer nicht von Debugging gesprochen hat: Der Auslöser ist dein
Vorschlag, nicht seine Anfrage.

Der Skill klärt zuerst, ob solche Zeilen überhaupt gekennzeichnet werden
sollen — das entscheidet der Nutzer, denn er trägt sie ein und baut sie
wieder aus. Kläre das, bevor du ihm die erste Änderung gibst, und nicht
erst, wenn schon mehrere im Quelltext stehen.
