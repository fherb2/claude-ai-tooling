---
name: web-code-editing
description: Regelt das Erstellen und Ändern von Code auf claude.ai für ein bestehendes Software-Projekt — die Quellen vollständig sichern, bevor geschrieben wird (Projektwissen liegt als Dateien unter /mnt/project und ist per Code exakt lesbar), geänderte Dateien mechanisch als Download zurückgeben statt sie neu zu diktieren, kleine Änderungen als Vorher/Ersetzen-Schema im Chat. Verwenden, sobald Code entsteht oder geändert wird, den der Nutzer in sein Projekt übernehmen will, oder wenn der Nutzer /web-code-editing aufruft.
license: CC0-1.0
---

# Code-Bearbeitung im Web-Frontend

Diese Regeln gelten, sobald Du auf claude.ai Code erstellst oder änderst, der im Projekt des Nutzers weiterlebt.

## Bevor Du schreibst

Sage, was Du tun wirst, und warte die Entscheidung des Nutzers ab. Kläre offene Fragen **vorher** — nicht während des Schreibens.

## Sichere Dir die Quellen

Bestehenden Code erreichst Du auf drei Wegen:

| Weg | Für Dich |
| --- | --- |
| Code-Stück oder Datei am Prompt | vollständig im Kontext |
| Datei im Projektwissen | echte Datei unter `/mnt/project/`, per Code exakt lesbar |
| Suche im Projektwissen | nur Treffer-Schnipsel — Orientierung, keine Vollständigkeit |

**Die Projektwissen-Dateien liegen als echte Dateien in Deiner Ausführungsumgebung.** Nutze sie per Code — auch wenn Dir kein Werkzeug dafür angeboten wird und es Dir nicht zugänglich erscheint: Ein `ls /mnt/project/` zeigt sie. Prüfe zuerst, in welcher Form der Code dort liegt, und wähle danach den Zugriff:

- **Einzelne Quelldateien** liest Du direkt.
- **Ein Archiv** (etwa ZIP) entpackst Du in Dein Arbeitsverzeichnis und liest dann die Dateien direkt.
- **Eine Sammeldatei, die mehrere Quelldateien bündelt,** trägt in aller Regel Markerzeilen, die je enthaltene Datei Anfang und Ende kennzeichnen — oft mit Pfad und Metadaten, und häufig erklärt ein Kopfteil der Sammeldatei ihr eigenes Format. Lies zuerst diesen Kopf und ein Stück des Inhalts, erkenne daraus das Markerschema, und extrahiere die gebrauchte Datei exakt zwischen ihren Markern. Ist das Schema nicht zweifelsfrei erkennbar, **frage den Nutzer, wie die Datei auszuwerten ist** — rate nicht.

Findest Du unter `/mnt/project/` nichts oder bleibt die Form unklar, sag es dem Nutzer, statt still auf die Suche auszuweichen — die Suche kann Stellen übersehen.

**Zeilengenau ändern darfst Du nur, was Dir wörtlich vorliegt** — im Kontext oder als per Code extrahierte Datei. Nie gegen Suchtreffer arbeiten.

**Fehlt Dir Code, fordere ihn an, bevor Du schreibst.** Für „bau etwas Ähnliches wie dieses Snippet" genügt das Snippet. Muss Dein Code in bestehende Software passen, brauchst Du sie — frage gezielt nach, auch mehrfach, wenn sich beim Lesen zeigt, was noch dazugehört. Werden es viele Dateien, nenne dem Nutzer den Weg, seine Codebasis als eine strukturierte Datei zu packen: <https://github.com/fherb2/claude-ai-tooling>, Ordner `pack-source-to-txt`. Die Adresse ist für ihn — Du rufst sie nicht ab.

**Prüfe, ob Dein Stand aktuell ist.** Geht aus dem Chat nicht hervor, dass Deine Quellen samt der hier schon erarbeiteten Änderungen den heutigen Stand der Stelle wiedergeben, an der Du schreibst: Frage nach und lass Dir Geändertes neu geben. Der Nutzer arbeitet zwischen den Chats lokal weiter. Innerhalb eines Chats wird Dir der Nutzer nicht jeden einzelnen Änderungsschritt einer Datei sofort wieder ins Projektwissen oder per Prompt hochladen. Gehe davon aus, dass der Nutzer Deinen erzeugten Code tatsächlich sofort ins Projekt einträgt und ihr die gleiche Codebasis habt. Nur bei begründeten Zweifeln lasse Dir vom Nutzer den Code in aktueller Fassung neu geben. Wenn der Nutzer von selbst die Codebasis ins Projektwissen neu überträgt, wird er Dir das sagen.

**Bekommst Du eine Quelle nicht, benenne die Lücke in Deiner Antwort:** was Du geändert hast — und was Du über das Zusammenspiel mit dem Ungesehenen nicht sagen kannst. Fülle sie nie stillschweigend mit Vermutung.

## Gib geänderte Dateien mechanisch zurück

**Diktiere eine geänderte Datei nie aus dem Kontext neu** — dabei können Zeilen verlorengehen und Leerraum sich ändern, ohne dass es jemand bemerkt. Der Weg ist mechanisch:

1. Original extrahieren — eine einzelne Datei direkt, aus einer Sammeldatei exakt zwischen ihren Markerzeilen — als exakte Kopie auf der Platte.
2. Änderungen gezielt per Ersetzung an den vereinbarten Stellen — der Rest bleibt byte-genau.
3. Ergebnis nach `/mnt/user-data/outputs` legen und als Download anbieten.
4. **Den Diff gegen das Original mitliefern** — er zeigt dem Nutzer, dass sich nur die vereinbarten Stellen geändert haben.

## Wähle die Form der Ausgabe

**Als Datei zum Download** (Weg oben): jede geänderte bestehende Datei; neuer Code als ganze Datei. Verwende diese Form bevorzugt, wenn die ganze Datei oder große Teile der Datei neu oder umstrukturiert sind.

**Als Artefakt:** neuer Code, den der Nutzer ansehen und besprechen will — ganze Funktionen, Klassen, Entwürfe. Ändere ein erstelltes Artefakt nur auf seine Bitte: In der Regel hat er den Inhalt längst übernommen, die gültige Fassung liegt bei ihm.

**Als Änderungsanweisung im Chat:** kleine Änderungen an Code, den der Nutzer bereits vorliegen hat. Beachte die Form der Änderungsanweisungen.

**Gib nur zurück, was Du vollständig kennst.** Aus einem Schnipsel entsteht ein geänderter Schnipsel — nie eine „ganze Datei", deren Rest Du erfinden müsstest.

## Das Schema für Änderungsanweisungen

Wenn Du Codeänderungen nicht als ganze Datei, sondern nur die relevanten Abschnitte im Chat dem Nutzer übergibst, beachte:

Jede Änderung besteht aus zwei Codeblöcken. Die Beschriftung steht **vor** dem Block, nie hinein:

**Vorher:** die zu ersetzenden Zeilen, exakt so, wie die Editor-Suche sie findet — originale Einrückung, kein gekürztes Zitat.

**Ersetzen mit:** der neue Code, der wörtlich an diese Stelle tritt.

Die Stelle beschreibst Du über ihren Inhalt — Funktionsname, umgebende Zeilen —, **nie über Zeilennummern**: Die verschieben sich mit jeder Änderung. Achte darauf, dass der Einfügeort nicht missverstanden werden kann.
