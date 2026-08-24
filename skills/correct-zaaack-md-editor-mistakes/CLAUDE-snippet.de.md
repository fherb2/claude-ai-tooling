*Stand: 2026-08-24*

*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger, der
den Skill auslöst. Beim Installieren: alles unterhalb der Trennlinie in die
`CLAUDE.md` des Zielorts übernehmen; diese Datei bleibt dort
liegen, wirksam ist allein die `CLAUDE.md`. Der Skill
läuft ohne den Trigger nur bei ausdrücklichem
`/correct-zaaack-md-editor-mistakes`-Aufruf.*

*Der Auslöser ist nichts, was der Nutzer ausspricht: Er bittet um eine
Änderung an einer Datei, und dass darin beschädigter Leerraum steht, weiß
vorher niemand — sichtbar ist er ohnehin kaum und im Fall des geschützten
Leerzeichens gar nicht. Es gibt also keine Anfrage, gegen die die
`description` abgeglichen werden könnte; der Wortlaut bindet deshalb an zwei
eigene Handlungen, das erste Lesen oder Ändern einer Markdown-Datei und den
Commit. Beim Anpassen an ein Projekt dürfen die Anker verschoben, aber nicht
weggelassen werden. Der Satz über das Gedächtnis ist der wirksame Teil gegen
Wiederholung: Ohne ihn beginnt die Prüfung in jeder Sitzung von neuem — und
das ausgerechnet bei einem Skill, der unbemerkt im Hintergrund arbeiten soll.*

*Nicht hineinschreiben, dass die Datei eine Tabelle enthalten muss. Die
Bedingung klingt sparsam, verleitet aber dazu, zuerst selbst nach Tabellen zu
suchen — genau die Arbeit, die das Werkzeug des Skills in einem Durchlauf
erledigt.*

*Der dritte Absatz — die Dauerfreigabe — muss hier stehen und darf nicht
weggelassen werden, auch wenn der Skill-Körper dasselbe sagt. Gemessen am
24. August 2026 mit Sonnet 5 und Opus 5: Steht die Freigabe nur im
Skill-Körper, legen beide Modelle einen Plan vor und korrigieren nichts;
steht sie zusätzlich hier, korrigieren beide sofort und melden hinterher.
Der Grund ist die Rangordnung — eine Planpflicht in der `CLAUDE.md` gilt
bedingungslos, eine Freigabe im Skill-Körper tritt gegen sie an und
verliert. Ohne diesen Absatz feuert der Trigger zwar, aber die Automatik
bleibt aus.*

---

## Markdown-Tabellen: Artefakte eines WYSIWYG-Editors

Bevor du in einer Sitzung zum ersten Mal eine Markdown-Datei liest oder
änderst, und bevor du Markdown-Dateien committest, konsultiere den Skill
`correct-zaaack-md-editor-mistakes`. Manche WYSIWYG-Editoren fressen beim
Speichern Leerzeichen in Tabellen und ersetzen andere durch geschützte;
beides fällt beim Lesen nicht auf, und niemand bittet von sich aus darum,
danach zu suchen.

Diese Korrektur ist dauerhaft freigegeben: Du führst sie ohne Rückfrage aus
und legst sie nicht als Plan vor. Sie betrifft ausschließlich Leerraum
innerhalb von Tabellenzeilen — kein Wort, keine Zeichensetzung. Melde
hinterher, was Du geändert hast.

Steht im Gedächtnis dieses Projekts schon, ob es betroffen ist, folge dem
und frage nicht erneut.
