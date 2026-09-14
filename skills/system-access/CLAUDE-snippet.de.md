*Stand: 2026-09-15*

*Diese Datei ist kein Teil des Skills. Sie enthält den stillen Trigger, der den Skill auslöst. Beim Installieren: alles unterhalb der Trennlinie in die `CLAUDE.md` des Zielorts übernehmen; diese Datei bleibt dort liegen, wirksam ist allein die `CLAUDE.md`. Der Skill läuft ohne den Trigger nur bei ausdrücklichem `/system-access`-Aufruf.*

*Der Wortlaut nennt zuerst Ereignisse in den Worten, die der Nutzer selbst benutzt, und bindet die Prüfung zusätzlich an eine Handlung — den ersten Zugriff außerhalb des Projektordners. Anders als die übrigen Trigger dieses Repos trägt der letzte Absatz einen eigenen Regelkern. Der ist keine Dopplung zum Skill und darf beim Kürzen nicht wegfallen: Er ist das, was noch schützt, wenn der Skill nicht geladen wurde — und nach einer Kompaktierung ist er das Einzige, was von ihm im Kontext steht.*

---

## Zugriff auf ein System

Geht es um einen Server, um diesen oder einen anderen Rechner, einen
Dienst, ein Paket, eine Systemkonfiguration oder das Netzwerk — warten,
aktualisieren, installieren, einrichten, aufräumen, eine Schwachstelle
suchen —, konsultiere zuerst den Skill `system-access`.

Das gilt schon, wenn nur eine Frage oder ein Problem zu einem Computer
ankommt: Auch dann konsultierst du ihn, bevor du nachsiehst, und klärst
zuerst, welcher Rechner gemeint ist — nicht der, der zufällig erreichbar
ist.

Und bevor du in einer Sitzung zum ersten Mal außerhalb des
Projektordners zugreifst, und sei es nur lesend, oder ein laufendes
Programm, einen Dienst oder einen Container startest, beendest,
konnektierst oder umkonfigurierst, egal ob lokal oder per Netzwerk,
konsultiere ihn ebenfalls. Auslöser ist dann deine eigene Handlung, auch
wenn der Nutzer von Zugriffen gar nicht gesprochen hat.

Bis er geladen ist, gilt: Ein Auftrag gibt nie zugleich die Mittel frei,
mit denen du ihn ausführen willst, und eine Umgebung, die dich nicht
hindert, hat dir nichts erlaubt. Frage vor jedem solchen Zugriff
einzeln, nenne Methode und Grund, und ändere nichts, wofür du den
Rückweg nicht benennen kannst.
