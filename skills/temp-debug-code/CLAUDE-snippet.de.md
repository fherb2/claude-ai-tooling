*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger, der
den Skill auslöst. Beim Installieren: alles unterhalb der Trennlinie in die
`CLAUDE.md` des Zielorts übernehmen, danach diese Datei löschen. Der Skill
läuft ohne den Trigger nur bei ausdrücklichem `/temp-debug-code`-Aufruf.*

*Dieser Trigger ist auf einen Auslöser angewiesen, den der Nutzer nie
ausspricht: Er fragt „warum kommt hier 3 raus?", und die Entscheidung, eine
`print`-Zeile einzubauen, trifft Claude selbst. Es gibt also keine Anfrage,
gegen die die `description` abgeglichen werden könnte — der Wortlaut bindet
deshalb an die eigene Handlung, und der Satz „auch dann, wenn der Nutzer
nicht von Debugging gesprochen hat" ist der wirksame Teil. Beim Anpassen an
ein Projekt darf er verschoben, aber nicht weggelassen werden. Der zweite
Absatz ist der Anker für die andere Hälfte des Skills, das Aufräumen; ohne
ihn feuert der Skill nur beim Einfügen und nie beim Entfernen.*

---

## Temporärer Debug-Code

Sobald du eine Zeile einfügst, die nur der Fehlersuche dient — eine
`print`- oder Log-Ausgabe, einen festen Testwert, eine übersprungene
Prüfung —, oder sobald du bestehenden Code zum Testen auskommentierst,
konsultiere zuvor den Skill `temp-debug-code` und halte dich an dessen
Kennzeichnungsregeln. Das gilt auch dann, wenn der Nutzer nicht von
Debugging gesprochen hat: Der Auslöser ist deine eigene Handlung, nicht
seine Anfrage.

Und bevor du eine gefundene Fehlerursache meldest oder die eigentliche
Korrektur schreibst, prüfe, ob im Quelltext noch temporärer Debug-Code
steht — auch solcher aus einem früheren Auftrag. Der Skill regelt, was
davon du selbst entfernst und was du dem Nutzer zur Entscheidung
vorlegst.
