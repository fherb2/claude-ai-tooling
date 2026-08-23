# temp-debug-code — Kennzeichnung von temporärem Debug-Code

**✅☑ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden, deutsche und englische Fassung vorhanden.

**Versieht jede Zeile, die nur zur Fehlersuche entsteht, mit einer festen, suchbaren Marke** — eingefügte Debug- und `print`-Ausgaben ebenso wie Originalcode, der für die Dauer der Fehlersuche stillgelegt wird. Alle Marken beginnen mit derselben Zeichenfolge, deshalb findet ein einziger Suchlauf restlos jede Änderung, die zum Debuggen entstanden ist. Darauf beruht der ganze Zweck: Der Originalzustand bleibt vollständig wiederherstellbar — ohne Erinnerung, auch von jemandem, der nicht dabei war, und notfalls per Skript.

Der zweite Teil des Skills ist das Aufräumen: Bevor eine gefundene Ursache gemeldet oder die eigentliche Korrektur geschrieben wird, prüft Claude, ob noch Debug-Code im Quelltext steht — auch solcher aus einem früheren Auftrag —, und entfernt ihn beziehungsweise legt ihn dem Nutzer vor.

**Nicht** gemeint ist Debug-Code, der dauerhaft im Quelltext bleiben soll: Ausgaben hinter einem Debug-Flag, hinter einer Log-Stufe oder hinter einer Konfigurationsvariablen. Das ist regulärer Programmcode, wird nicht markiert und folgt den üblichen Regeln des Projekts.

## Installation

1. **Zielort wählen.** Der Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:

   | Ort         | Pfad                                  | Gilt für                  |
   | ----------- | ------------------------------------- | ------------------------- |
   | Persönlich  | `~/.claude/skills/temp-debug-code/`   | alle Projekte des Nutzers |
   | Projekt     | `.claude/skills/temp-debug-code/`     | nur dieses Projekt        |

2. **Ordner `temp-debug-code/` unter seinem unveränderten Namen kopieren, Sprachfassung wählen.** `SKILL.md` und `CLAUDE-snippet.md` liegen je zweimal vor — `SKILL.de.md`/`SKILL.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Mitkopiert wird nur die gewünschte Fassung, und ihr Sprachkürzel entfällt dabei: Aus `SKILL.de.md` wird am Zielort `SKILL.md`. Bleibt das Kürzel stehen, findet Claude Code den Skill nicht. Die `README.md` ist schon die deutsche Fassung ohne Kürzel; nur wer die englische will, benennt `README.en.md` am Zielort in `README.md` um.

3. **Stillen Trigger übernehmen.** Der Inhalt der `CLAUDE-snippet.md` — passend zur gewählten Sprachfassung — kommt **unterhalb der Trennlinie** in die `CLAUDE.md` des Zielorts — bei persönlicher Installation in `~/.claude/CLAUDE.md`, bei einer Projektinstallation in die `CLAUDE.md` des Projekts. Der kursive Text oberhalb der Trennlinie wird nicht mitkopiert. Danach die `CLAUDE-snippet.md` am Zielort löschen, damit der Trigger nicht zweimal existiert.

   Ohne diesen Schritt wirkt der Skill nur bei ausdrücklichem Aufruf mit `/temp-debug-code`. Das ist hier besonders folgenreich: Der Auslöser ist Claudes eigene Handlung — der Nutzer fragt „warum kommt hier 3 raus?", und die Entscheidung, eine `print`-Zeile einzubauen, fällt Claude selbst. Es gibt also keine Anfrage, gegen die die `description` abgeglichen werden könnte.

## Details

**Die Marken.** Vier Stück, zeichengenau einzuhalten, jeweils mit einem führenden und einem abschließenden Leerzeichen: ` # DEBUG # ` an jeder einzeln eingefügten Debug-Zeile, ` # DEBUG: ORIGINAL # ` an jeder stillgelegten Originalzeile, ` # DEBUG: START ------------ # ` und ` # DEBUG: END ------------ # ` um Blöcke ab fünf Debug-Zeilen. Die genauen Fälle und Beispiele für Python, C-artige Sprachen und Shell stehen in der `SKILL.md`.

**Warum zwei Rauten hintereinander stehen.** Das `#` am Anfang und Ende einer Marke ist Bestandteil der Marke, nicht der Kommentar-Marker der Sprache. In Python trifft es deshalb auf ein zweites `#`. Das sieht nach einem Versehen aus, ist aber der Grund, warum die Marke in jeder Sprache gleich lautet und ein einziges Suchmuster genügt. Wer den Skill anpasst, sollte diese vermeintliche Dopplung nicht wegvereinfachen — damit fällt die Sprachunabhängigkeit.

**Der Selbsttest.** Nach dem Schreiben der Debug-Änderungen läuft `grep -rn " # DEBUG" .` und die Trefferzahl wird gegen die Zahl der Änderungen gehalten: jede Blockmarkierung zählt zwei Treffer, jede sonstige markierte Zeile einen. Stimmen die Zahlen nicht, fehlt eine Marke.

**Originalcode wird nie gelöscht,** nur auskommentiert. Die stillgelegte Zeile ist die einzige verlässliche Quelle für den Rückweg — sie steht im Suchlauf, im Diff und noch dort, wenn jemand anders aufräumt.

**Aufräumen richtet sich nach dem Auftrag, nicht nach dem Alter.** Debug-Code aus dem laufenden Auftrag entfernt Claude selbständig; Debug-Code aus einem abgeschlossenen Auftrag legt er dem Nutzer vor. Lehnt der Nutzer ab, kommt dieselbe Stelle erst bei einem neuen Tag, einem neuen Chat oder auf ausdrücklichen Auftrag wieder zur Sprache.

**Der Anker im Trigger.** Der Absatz in der `CLAUDE.md` bindet an die eigene Handlung, und der Satz „auch dann, wenn der Nutzer nicht von Debugging gesprochen hat" ist der wirksame Teil. Sein zweiter Absatz ist der Anker für das Aufräumen; ohne ihn feuert der Skill nur beim Einfügen und nie beim Entfernen. Beim Anpassen an ein Projekt dürfen beide verschoben, aber nicht weggelassen werden.

## Stand und Offenes

**Status:** Anweisungen vollständig, Frontmatter gesetzt, Wortlaut überarbeitet, stiller Trigger vorhanden, Description in der dritten Person. Die englische Fassung ist am 17. August 2026 als Übersetzung der deutschen entstanden; die Marken sind darin zeichengleich, denn sie sind Marker und keine Prosa. Die Erprobung am Zielort findet statt, wenn der Skill dort gebraucht wird.

**Offen:** derzeit nichts.
