# Fehlersuche über den Nutzer

Du erreichst den Quelltext nicht selbst. Jede Probe, die laufen soll, führt der Nutzer aus; jede Zeile, die eingefügt oder stillgelegt werden muss, trägt er ein. Daraus folgt die Leitlinie dieses Teils: **So wenig verlangen wie möglich — und für alles, was Du doch verlangst, genau sagen, was zu tun ist.**

## Wo die Probe laufen muss

Bevor Du eine Probe entwirfst, klär eine Frage: **Wo lebt der Fehler?**

- **Reicht die Logik zur Klärung** — ein Rechenweg, eine Zeichenkettenbehandlung, ein Sortierverhalten —, dann führe die Probe **selbst** aus, in Deiner eigenen Ausführungsumgebung. Das kostet den Nutzer nichts und geht sofort.
- **Hängt der Fehler an seiner Umgebung** — an Versionen, installierten Abhängigkeiten, echten Daten, Hardware, Dateisystem, Zeit —, dann **beweist Deine Ausführungsumgebung nichts.** Sie ist eine andere Maschine. Die Probe gehört auf seinen Rechner.

Bist Du unsicher, welcher Fall vorliegt, sag es und frag ihn. Eine Probe, die am falschen Ort läuft, erzeugt ein Ergebnis, das nichts bedeutet — und das ist schlimmer als keine Probe.

## Die kleinste Probe zuerst

Verlange nur, was die Frage beantwortet. In dieser Reihenfolge:

1. **Ohne Ausführung klären.** Manches beantwortet ein Blick in den Quelltext, eine Nachfrage oder eine Fehlermeldung, die schon vorliegt. Dann läuft nichts.
2. **Eine Probe von außen**, die den Quelltext nicht anfasst. Die Form hängt an der Sprache:
   - **Interpretierte Sprachen:** ein Kommandozeilen-Aufruf, oft ein Einzeiler — etwa `python -c "…"`.
   - **Übersetzte Sprachen:** eine Kommandozeile, die übersetzt und startet, oder ein kleines eigenständiges Programm, das er übersetzt und laufen lässt.
   - **Wo beides zu eng wird:** ein kurzes Treiberprogramm, das er neben das Projekt legt und aufruft.
3. **Ein eigenes Skript**, wenn ein Aufruf nicht mehr trägt — mehrere Schritte, Aufbau und Abbau, Auswertung.
4. **Erst dann in den Quelltext eingreifen.** Wenn ein Zwischenwert von außen nicht zu erreichen ist, muss eine Zeile hinein oder eine stillgelegt werden. Das ist keine letzte Stufe, sondern gehört oft schon zu Stufe 2 — der Punkt ist nicht, es zu vermeiden, sondern es **klein** zu halten.

Fasse in jedem Fall so wenig an wie möglich, und lass den Nutzer nach jedem Schritt entscheiden, ob der nächste nötig ist.

## Wie Du eine Änderung übergibst

Wenn er etwas eintragen soll, muss er es ohne Rückfrage tun können:

- **Die Stelle beschreibst Du über ihren Inhalt** — Funktionsname, umgebende Zeilen —, **nie über Zeilennummern.** Die verschieben sich mit jeder Änderung.
- **Gib die Einrückung mit**, so wie sie an der Stelle gilt.
- **Sag, was mit dem Original geschieht:** stehen lassen, stilllegen, ersetzen.
- **Ein Schritt nach dem anderen.** Nicht fünf Eingriffe auf einmal, deren Ergebnisse sich überlagern.

## Wie Du das Ergebnis zurückbekommst

Sag ihm ausdrücklich, **was Du sehen willst**: die ganze Ausgabe, die letzten Zeilen, die Fehlermeldung samt Rückverfolgung. Und rechne damit, dass er etwas anderes zurückgibt, als Du erwartet hast — frag nach, statt aus einer unklaren Ausgabe zu schließen.

## Die Kennzeichnung

Was jetzt gilt, hat der Nutzer entschieden (siehe `user-choice.de.md`):

- **Er hat zugestimmt** → lies `marks.de.md` aus dem Ordner dieses Skills und gib die Zeilen fertig markiert an ihn weiter. **Den Suchlauf führt er aus, nicht Du.** Nenne ihm deshalb beim Aufräumen das Suchmuster und, wenn Du sie kennst, die erwartete Trefferzahl.
- **Er hat eine eigene Markierung vorgeschlagen** → benutze seine, unverändert. `marks.de.md` wird dann nicht geladen.
- **Er will keine** → markiere nicht.

## Aufräumen

Der Rückbau liegt beim Nutzer, und er entscheidet, wann. Deine Aufgabe ist, ihn dabei nicht im Stich zu lassen:

- Ist eine Probe erledigt, sag es — und sag, was sie rückgängig macht.
- Bei stillgelegten Originalzeilen: nenne die Zeile, die wieder aktiv werden muss.
- Hat er markieren lassen, nenne zum Schluss das Suchmuster, mit dem er den Rest findet.

Eine eigene Rückbauliste musst Du nicht führen — der Chat trägt sie bereits. Fragt er danach, stell sie aus dem Verlauf zusammen.
