# Fehlersuche mit unmittelbarem Zugriff

Du erreichst den Dateibaum des Projekts selbst. Damit liegt die ganze Fehlersuche bei Dir: Du entscheidest, welche Probe nötig ist, wie sie ausgeführt wird und wie ihr Ergebnis zu lesen ist. **Vorschriften dazu stehen hier nicht** — das ist Handwerk, keine Regel.

Geregelt ist nur eines: **was Du im Quelltext hinterlässt, solange die Suche läuft.**

## Die Kennzeichnung ist nicht verhandelbar

Jede Zeile, die Du zum Debuggen einfügst, und jede Originalzeile, die Du dafür stilllegst, wird markiert. Ohne Rückfrage, in jeder Sitzung.

Das hat zwei Gründe, und beide gelten unabhängig davon, wie sorgfältig Du arbeitest:

- **Der Nutzer sieht, wo Du gerade eingreifst.** Er liest nicht jede Deiner Änderungen mit. Die Marke ist die Stelle, an der sein Blick hängen bleibt.
- **Du findest selbst zurück.** Am Ende der Suche muss der Originalzustand vollständig wiederherstellbar sein — ohne Erinnerung, auch von jemandem, der nicht dabei war. Eine unmarkierte Debug-Zeile ist kein Schönheitsfehler, sondern ein Rest, den niemand mehr findet.

Die einzige Ausnahme ist eine Vorgabe des Projekts, die es anders regelt.

**Lies jetzt `${CLAUDE_SKILL_DIR}/marks.de.md`.** Dort stehen die Marken und die Fälle, in denen sie gesetzt werden.

## Der Selbsttest, verpflichtend

Führe den Suchlauf aus, sobald Du Deine Debug-Änderungen geschrieben hast, und vergleiche die Trefferzahl mit dem, was Du geändert hast:

```
grep -rn '@@~DEBUG' .
```

Jede Blockmarkierung zählt zwei Treffer (Anfang und Ende), jede sonstige markierte Zeile einen. Stimmen die Zahlen nicht überein, fehlt eine Marke — such sie, bevor Du weiterarbeitest.

## Debug-Code wieder entfernen

**Der Rückbau ist Deine Entscheidung, nie die eines Skripts.** Der Suchlauf findet die Marken; was an einer Fundstelle geschieht, prüfst Du an ihr selbst — anhand aller Informationen, die Du über das Codefragment hast oder Dir beschaffen kannst. Rechne damit, dass Markierungen völlig anders und unstrukturiert gesetzt sind, als diese Regeln es vorsehen: Der Nutzer editiert selbst, und er tut es nicht nach Deinem Schema. Sieh genau hin, bevor Du eine Zeile entfernst oder wieder aktivierst.

Bevor Du neuen Debug-Code einfügst, prüfe, ob vorhandener seinen Zweck erfüllt hat und entfernt werden kann. Ausschlaggebend ist dabei nicht, wann er entstanden ist, sondern **zu welchem Problemlösungsauftrag er gehört**:

- Gehört er zu dem Auftrag, an dem Du gerade arbeitest, und hat er seinen Dienst getan, entfernst Du ihn selbständig und aktivierst die dabei stillgelegten Codebereiche wieder.
- Gehört er zu einem früheren, bereits abgeschlossenen Auftrag, entscheidest Du nicht selbst: Lege dem Nutzer die Stelle vor und lass ihn entscheiden. Entscheidet er sich gegen das Entfernen, schlägst Du dieselbe Stelle erst dann wieder vor, wenn ein neuer Tag oder ein neuer Chat begonnen hat oder wenn der Nutzer Dich ausdrücklich beauftragt, Debug-Code zu finden und zu entfernen.

Wenn Du Debug-Code entfernst, prüfe sehr genau, ob dabei stillgelegter Originalcode wieder zu aktivieren ist. Die Trennzeilen eines Blocks gehen mit ihm weg. Führe zum Schluss den zweiten Suchlauf aus — er findet zusätzlich die Trennzeilen:

```
grep -rn '@@~' .
```

Was er noch findet, ist noch nicht aufgeräumt.

## Der beauftragte Suchlauf nach Resten

Von sich aus sprichst Du eine fremde oder vergessene Markierung nicht an; dazu sagt die `SKILL.md` das Nötige. Bittet Dich der Nutzer aber ausdrücklich, nach solchen Resten zu suchen und sie mit ihm zu bereinigen, gilt an jeder Fundstelle dieselbe Reihenfolge:

1. **Klären, was dort vorliegt** — gemeinsam mit dem Nutzer, bevor irgendetwas geschieht. Was Du selbst herausfinden kannst, findest Du vorher heraus und legst es mit vor.
2. **Der Nutzer entscheidet, wie die Stelle anzupassen ist.** Entfernen, stehenlassen, umschreiben — er wählt. Eine Empfehlung darfst Du geben, die Entscheidung nimmst Du ihm nicht ab.
3. **Erst danach änderst Du die Stelle.**

Jede Fundstelle für sich: Eine Entscheidung an der einen überträgt sich nicht auf die nächste, auch wenn beide gleich aussehen.
