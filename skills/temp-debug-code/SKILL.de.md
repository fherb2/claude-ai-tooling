---
name: temp-debug-code
description: Regeln für temporären Debug-Code — eingefügte Debug- und print-Ausgaben sowie zum Testen stillgelegter Originalcode werden mit festen, suchbaren Marken versehen, damit sie später rückstandsfrei entfernt und der Originalzustand vollständig wiederhergestellt werden kann. Wo Claude die Dateien des Nutzers nicht selbst erreicht, kommt hinzu, welche Probe wo ausgeführt und wie sie übergeben wird. Verwenden, bevor in einer Sitzung zum ersten Mal eine Debug-Ausgabe eingefügt, bestehender Code zum Testen auskommentiert oder eine solche Änderung dem Nutzer vorgeschlagen wird, oder wenn der Nutzer /temp-debug-code aufruft.
license: CC0-1.0
---

# Temporärer Debug-Code und zeitweises Stilllegen von Originalcode

## Wofür diese Regeln gelten — und wofür nicht

Diese Regeln gelten ausschließlich für **temporären** Debug-Code: für Zeilen, die nur zur Fehlersuche entstehen und wieder verschwinden sollen, sobald die Ursache gefunden ist. Dazu gehört ebenso der Originalcode, den Du für die Dauer der Fehlersuche stilllegst.

Nicht Gegenstand dieser Regeln ist Debug-Code, der dauerhaft im Quelltext bleiben soll — etwa Ausgaben hinter einem Debug-Flag, hinter einer Log-Stufe oder hinter einer Konfigurationsvariablen. Solcher Code ist regulärer Programmcode, wird nicht markiert und folgt den üblichen Regeln des Projekts.

**Diese Regeln binden Dich, nicht den Nutzer.** Sie gelten für Debug-Code, den Du schreibst oder vorschlägst. Was Du im Bestand vorfindest, misst Du nicht an ihnen: Der Nutzer markiert seinen Debug-Code, wie er will, und darf jederzeit anders. Aus einer abweichenden Schreibweise folgt kein Hinweis und kein Korrekturvorschlag.

## Vorgaben des Projekts gehen vor

Hat das Projekt zum Umgang mit Debug-Code etwas festgelegt, gilt das und nicht dieser Skill — auch dort, wo er sonst keine Wahl lässt. Wo Du danach siehst:

- **Die Anweisungsdatei des Projekts** — die projekteigene `CLAUDE.md` beziehungsweise das Anweisungsfeld des Projekts — liegt ohnehin im Kontext. Mehr ist dort nicht zu tun.
- **Arbeitest Du über den Nutzer** und steht die Antwort nicht schon im Kontext, sieh im Projektwissen nach. Das ist ein flacher Ort, ein Blick genügt.
- **Erreichst Du den Dateibaum selbst**, verlässt Du Dich auf die Anweisungsdatei. Gibt es begleitende Projektdokumentation, sagt sie in aller Regel, wo. Kämme keine Unterordner durch.

Findest Du eine solche Festlegung erst später, gilt sie **ab dann** und überstimmt, was hier steht.

## In welcher Umgebung arbeitest Du?

Alles Weitere hängt an einer einzigen Unterscheidung:

**Erreichst Du den Dateibaum des Projekts unmittelbar — mit Werkzeugen, die seine Dateien lesen und schreiben?** In Claude Code ist das so. Auf claude.ai und in Claude Desktop nicht: Dort arbeitest Du über den Nutzer, er ist die Hand am Quelltext.

> **Projektwissen ist nicht der Dateibaum.** Findest Du Dateien unter `/mnt/project/` oder an einer vergleichbaren Stelle, sind das **Kopien**. Wer dort etwas ändert, ändert nichts am Projekt des Nutzers. Ein Fund dort beweist keinen Vollzugriff.

- **Du erreichst den Dateibaum selbst** → lies `${CLAUDE_SKILL_DIR}/rules-local.de.md` und arbeite danach.
- **Du arbeitest über den Nutzer** → lies `user-choice.de.md` aus dem Ordner dieses Skills und arbeite danach.

## Warum dieser Skill geteilt ist

Die beiden Fälle sind nicht zwei Formulierungen derselben Sache, sondern zwei Mechanismen: Einmal handelst Du, einmal der Nutzer. Und ob überhaupt markiert wird, entscheidet im zweiten Fall er — denn er trägt die Arbeit. Regeln, die für die vorliegende Lage nicht gelten, würden hier nur Kontext kosten und die Entscheidung verwischen. Deshalb steht in dieser Datei allein, was in beiden Fällen gilt; alles Weitere wird nachgeladen, sobald feststeht, was gebraucht wird.
