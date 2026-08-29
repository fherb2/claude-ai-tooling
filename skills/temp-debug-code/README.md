# temp-debug-code — Kennzeichnung von temporärem Debug-Code

*Stand: 2026-08-29*

**✅☑ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden, deutsche und englische Fassung vorhanden.

**Versieht jede Zeile, die nur zur Fehlersuche entsteht, mit einer festen, suchbaren Marke** — eingefügte Debug- und `print`-Ausgaben ebenso wie Originalcode, der für die Dauer der Fehlersuche stillgelegt wird. Alle Marken beginnen mit derselben Zeichenfolge, deshalb findet ein einziger Suchlauf restlos jede Änderung, die zum Debuggen entstanden ist. Darauf beruht der ganze Zweck: Der Originalzustand bleibt vollständig wiederherstellbar — ohne Erinnerung und auch von jemandem, der nicht dabei war.

Der zweite Teil des Skills ist das Aufräumen: Bevor eine gefundene Ursache gemeldet oder die eigentliche Korrektur geschrieben wird, prüft Claude, ob noch Debug-Code im Quelltext steht — auch solcher aus einem früheren Auftrag —, und entfernt ihn beziehungsweise legt ihn dem Nutzer vor.

**Nicht** gemeint ist Debug-Code, der dauerhaft im Quelltext bleiben soll: Ausgaben hinter einem Debug-Flag, hinter einer Log-Stufe oder hinter einer Konfigurationsvariablen. Das ist regulärer Programmcode, wird nicht markiert und folgt den üblichen Regeln des Projekts.

**Die Regeln binden Claude, nicht den Nutzer.** Sie gelten für Debug-Code, den Claude schreibt. Vorgefundene Markierungen werden nicht an ihnen gemessen: Der Nutzer markiert, wie er will, und bekommt keinen Hinweis auf eine abweichende Schreibweise. Nach fremden Resten sucht Claude nur, wenn er darum gebeten wird — und dann wird jede Fundstelle einzeln mit dem Nutzer geklärt, bevor sich etwas ändert.

## Installation

1. **Zielort wählen.** Der Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:

   | Ort         | Pfad                                  | Gilt für                  |
   | ----------- | ------------------------------------- | ------------------------- |
   | Persönlich  | `~/.claude/skills/temp-debug-code/`   | alle Projekte des Nutzers |
   | Projekt     | `.claude/skills/temp-debug-code/`     | nur dieses Projekt        |

2. **Eine Sprachversion des Ordners `temp-debug-code/` kopieren.** `SKILL` und `CLAUDE-snippet` liegen je zweimal vor — `SKILL.de.md`/`SKILL.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Mit gehören alle Dateien der gewählten Sprache, README eingeschlossen. Die gewählte SKILL-Fassung heißt am Zielort `SKILL.md` — ob umbenannt oder zusätzlich abgelegt, ist gleichgültig; Claude Code erkennt ausschließlich diesen Namen. Die Datumszeilen zeigen später, von welchem Stand die Installation ist.

3. **Stillen Trigger übernehmen.** Der Inhalt der `CLAUDE-snippet.md` — passend zur gewählten Sprachfassung — kommt **unterhalb der Trennlinie** in die `CLAUDE.md` des Zielorts — bei persönlicher Installation in `~/.claude/CLAUDE.md`, bei einer Projektinstallation in die `CLAUDE.md` des Projekts. Der kursive Text oberhalb der Trennlinie wird nicht mitkopiert. Die Snippet-Dateien bleiben am Zielort liegen; wirksam ist allein die `CLAUDE.md`, ihre Datumszeilen zeigen den Stand des übernommenen Triggers.

   Ohne diesen Schritt wirkt der Skill nur bei ausdrücklichem Aufruf mit `/temp-debug-code`. Das ist hier besonders folgenreich: Der Auslöser ist Claudes eigene Handlung — der Nutzer fragt „warum kommt hier 3 raus?", und die Entscheidung, eine `print`-Zeile einzubauen, fällt Claude selbst. Es gibt also keine Anfrage, gegen die die `description` abgeglichen werden könnte.

## Details

**Die Marken.** Fünf Stück, zeichengenau einzuhalten: ` @@~DEBUG >>kennung<< ~@@ ` an jeder einzeln eingefügten Debug-Zeile, ` @@~DEBUG: ORIGINAL >>kennung<< ~@@ ` an jeder stillgelegten Originalzeile, ` @@~DEBUG: START >>kennung<< ~~~~~~~~~~~~@@ ` und ` @@~DEBUG: END >>kennung<< ~~~~~~~~~~~~@@ ` um Blöcke ab fünf Debug-Zeilen, dazu die Trennzeile ` @@~~~~~~~~~~~~~~~~~~~~~~~~@@ ` vor jedem START und nach jedem END. Die genauen Fälle und Beispiele für Python, C-artige Sprachen und Shell stehen in der `SKILL.md`.

**Warum `@@~` der Rahmen ist.** Das Rahmenzeichen darf nicht mit dem Kommentarzeichen einer Sprache kollidieren, kein Regex-Metazeichen sein, keine Sonderbedeutung in der Shell haben und in Quelltext praktisch nicht vorkommen — gesucht wird nach `@@~`, nicht nach `@@` allein. Geprüft und verworfen wurden: `%%`, weil `%%~` in Windows-Batch gängige Syntax ist (`%%~dp0`); `!!`, weil eine interaktive Bash `!!` auch in doppelten Anführungszeichen als History-Expansion auflöst und der Selbsttest-Befehl damit stillschweigend etwas anderes täte; `||`, weil `|` ein Metazeichen ist und Escaping erzwänge; und `§`, weil es auf US-Tastaturen nicht existiert. Die beiden Kollisionen von `@@` — Rubys Klassenvariablen und die Hunk-Köpfe in Diffs — treffen das Suchmuster nicht, weil dort nie eine Tilde folgt. Wer den Skill anpasst, sollte den Rahmen deshalb nicht gegen ein bequemeres Zeichen tauschen.

**Warum die Tilden nie zu zweit auftreten.** Zwei Tilden sind in Markdown Durchstreichung, und Kommentare und Docstrings könnten Markdown enthalten. Erlaubt ist deshalb eine Tilde oder drei und mehr; die Anzahl selbst ist reine Optik und für die Suche gleichgültig.

**Die Marken sind in beiden Sprachfassungen gleich.** Sie sind Marker und keine Prosa und wurden bewusst nicht übersetzt: Sonst fände ein Projekt, in dem beide Fassungen im Umlauf waren, seinen Debug-Code nicht mehr mit einem einzigen Suchlauf.

**Kennungen und Verschachtelung.** Jede Marke trägt zwischen `>>` und `<<` die Kennung ihres Debug-Vorhabens. Sie ist nötig, weil Debug-Vorhaben ineinander entstehen: Ein zweites beginnt mitten im ersten, und beim Aufräumen des inneren muss erkennbar bleiben, welche stillgelegte Zeile zum äußeren gehört. Ohne Kennung wäre das nur aus der Lage im Code zu erraten — und eine falsche Zuordnung reaktiviert Originalcode, den das noch laufende Vorhaben stillgelegt hat. Der Schaden sieht dann wie ein Programmfehler aus, nicht wie ein Aufräumfehler. Die Kennung benennt deshalb die Frage, der nachgegangen wird, nicht die Codestelle: Zwei Vorhaben in derselben Funktion bekämen sonst dieselbe.

**Der Selbsttest.** Nach dem Schreiben der Debug-Änderungen läuft `grep -rn '@@~DEBUG' .` und die Trefferzahl wird gegen die Zahl der Änderungen gehalten: jede Blockmarkierung zählt zwei Treffer, jede sonstige markierte Zeile einen. Stimmen die Zahlen nicht, fehlt eine Marke. Beim Aufräumen läuft stattdessen `grep -rn '@@~' .` — dieses Muster findet zusätzlich die Trennzeilen, die sonst liegenblieben.

**Originalcode wird nie gelöscht,** nur auskommentiert. Die stillgelegte Zeile ist die einzige verlässliche Quelle für den Rückweg — sie steht im Suchlauf, im Diff und noch dort, wenn jemand anders aufräumt.

**Aufräumen richtet sich nach dem Auftrag, nicht nach dem Alter.** Debug-Code aus dem laufenden Auftrag entfernt Claude selbständig; Debug-Code aus einem abgeschlossenen Auftrag legt er dem Nutzer vor. Lehnt der Nutzer ab, kommt dieselbe Stelle erst bei einem neuen Tag, einem neuen Chat oder auf ausdrücklichen Auftrag wieder zur Sprache. **Entschieden wird dabei nie per Skript:** Der Suchlauf findet die Marken, was an einer Fundstelle geschieht, prüft Claude an ihr selbst — Markierungen können völlig anders gesetzt sein, als die Regeln es vorsehen.

**Der Anker im Trigger.** Der Absatz in der `CLAUDE.md` bindet an die eigene Handlung, und der Satz „auch dann, wenn der Nutzer nicht von Debugging gesprochen hat" ist der wirksame Teil. Sein zweiter Absatz ist der Anker für das Aufräumen; ohne ihn feuert der Skill nur beim Einfügen und nie beim Entfernen. Beim Anpassen an ein Projekt dürfen beide verschoben, aber nicht weggelassen werden.

## Stand und Offenes

**Status:** Anweisungen vollständig, Frontmatter gesetzt, Wortlaut überarbeitet, stiller Trigger vorhanden, Description in der dritten Person. Am 29. August 2026 sind die Marken vollständig neu gefasst worden — Rahmen `@@~` statt der alten Doppelraute, Kennung je Debug-Vorhaben, Verschachtelung, Trennzeilen —, und beide Sprachfassungen sind dabei gemeinsam nachgezogen worden. Die Erprobung am Zielort findet statt, wenn der Skill dort gebraucht wird.

**Offen:** Die neue Markenform war noch nie im Einsatz. Das macht den Skill nicht unbenutzbar — sein erster Einsatz ist zugleich ihre Erprobung.
