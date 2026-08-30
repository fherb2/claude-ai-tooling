# temp-debug-code — Kennzeichnung von temporärem Debug-Code

*Stand: 2026-08-30*

*[English version](README.en.md)*

**✅☑ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, stille Trigger für beide Umgebungen vorhanden, deutsche und englische Fassung vorhanden. — Mit inhaltlichen Unterschieden zwischen der Version für Claude.ai / Claude Desktop (Chat + Cowork) sowie Claude Code.

**Versieht jede Zeile, die nur zur Fehlersuche entsteht, mit einer festen, suchbaren Marke** — eingefügte Debug- und `print`-Ausgaben ebenso wie Originalcode, der für die Dauer der Fehlersuche stillgelegt wird. Alle Marken beginnen mit derselben Zeichenfolge, deshalb findet ein einziger Suchlauf restlos jede Änderung, die zum Debuggen entstanden ist. Darauf beruht der ganze Zweck: Der Originalzustand bleibt vollständig wiederherstellbar — ohne Erinnerung und auch von jemandem, der nicht dabei war.

Der zweite Teil des Skills ist das Aufräumen: Bevor eine gefundene Ursache gemeldet oder die eigentliche Korrektur geschrieben wird, prüft Claude, ob noch Debug-Code im Quelltext steht — auch solcher aus einem früheren Auftrag —, und entfernt ihn beziehungsweise legt ihn dem Nutzer vor.

**Wo Claude die Dateien nicht selbst erreicht** — auf claude.ai und in Claude Desktop (Chat + Cowork) —, kommt ein zweiter Gegenstand hinzu: welche Probe wo ausgeführt wird und wie sie dem Nutzer übergeben wird. Dort entscheidet außerdem **er**, ob überhaupt markiert wird, denn er trägt die Zeilen ein und baut sie wieder aus.

**Nicht** gemeint ist Debug-Code, der dauerhaft im Quelltext bleiben soll: Ausgaben hinter einem Debug-Flag, hinter einer Log-Stufe oder hinter einer Konfigurationsvariablen. Das ist regulärer Programmcode, wird nicht markiert und folgt den üblichen Regeln des Projekts.

**Die Regeln binden Claude, nicht den Nutzer.** Sie gelten für Debug-Code, den Claude schreibt oder vorschlägt. Vorgefundene Markierungen werden nicht an ihnen gemessen: Der Nutzer markiert, wie er will, und bekommt keinen Hinweis auf eine abweichende Schreibweise. Nach fremden Resten sucht Claude nur, wenn er darum gebeten wird — und dann wird jede Fundstelle einzeln mit dem Nutzer geklärt, bevor sich etwas ändert.

## Aufbau

Der Skill ist geteilt, damit in einer Sitzung nur die Anweisungen im Kontext liegen, die für die vorliegende Lage gelten:

| Datei | Inhalt | wann geladen |
| --- | --- | --- |
| `SKILL.md` | Geltungsbereich · Vorrang der Projektvorgaben · die Umgebungsfrage · Verzweigung | immer |
| `rules-local.de.md` | Claude macht alles selbst: Kennzeichnungspflicht, Selbsttest, Aufräumen, Rückbau | bei unmittelbarem Dateizugriff |
| `user-choice.de.md` | Kurzfassung mit Beispiel, damit der Nutzer entscheiden kann | wenn Claude über den Nutzer arbeitet |
| `rules-handover.de.md` | Wo die Probe laufen muss, wie sie klein bleibt und wie sie übergeben wird | ebenso, in jedem Fall |
| `marks.de.md` | Die Marken selbst: fünf Marken, drei Fälle, Verschachtelung, Kennungen | aus einer der beiden Regeldateien, sobald gekennzeichnet wird |

Die Marken stehen **einmal je Sprache**. Sie sind in beiden Umgebungen zeichengleich; verschieden ist nur, wer sie setzt und wer den Suchlauf ausführt.

## Installation

Dieser Skill hat **zwei stille Trigger** — einen für jede Umgebung. Welcher der richtige ist, nimmt Dir das Paket ab: Es enthält bereits den passenden, unter dem Namen `CLAUDE-snippet.md`.

### Claude Code

1. **Paket herunterladen.** `downloads/temp-debug-code_de_local.zip`

2. **Entpacken.** Das Archiv enthält einen Ordner `temp-debug-code/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt der Skill für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.

3. **Stillen Trigger übernehmen.** Das musst Du händisch tun. Claude erkennt dann leichter aus dem Kontext heraus, ob der Skill geladen werden soll. Dazu: Aus `CLAUDE-snippet.md` kommt **alles unterhalb der Trennlinie** in die `CLAUDE.md` des gewählten Orts. Der kursive Text darüber bleibt zurück; die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Trigger ist.

   Ohne diesen Schritt wirkt der Skill nur beim ausdrücklichen Aufruf mit `/temp-debug-code`.

### claude.ai und Claude Desktop (Chat + Cowork)

1. **Paket herunterladen.** `downloads/temp-debug-code_de_web.zip`

2. **Hochladen.** Im dafür vorgesehenen Verwaltungsfeld für Skills der Anwendung das Archiv hochladen. Der Skill gilt danach für Dein Konto — nicht für Deine Organisation, und nicht gleichzeitig in Claude Code.

3. **Stillen Trigger übernehmen.** Das musst Du händisch tun. Claude erkennt dann leichter aus dem Kontext heraus, ob der Skill geladen werden soll. Dazu: Aus `CLAUDE-snippet.md` im Archiv kommt **alles unterhalb der Trennlinie** in das Anweisungsfeld — global für das Konto oder für das einzelne Projekt.

   Ohne diesen Schritt wirkt der Skill nur beim ausdrücklichen Aufruf mit `/temp-debug-code`.

**Warum der Trigger hier besonders zählt:** Der Auslöser ist Claudes eigene Handlung beziehungsweise ihr Vorschlag — der Nutzer fragt „warum kommt hier 3 raus?“, und die Entscheidung, eine `print`-Zeile einzubauen, fällt Claude. Es gibt also keine Anfrage, gegen die die `description` abgeglichen werden könnte.

## Details

**Die Marken.** Fünf Stück, zeichengenau einzuhalten: ` @@~DEBUG >>kennung<< ~@@ ` an jeder einzeln eingefügten Debug-Zeile, ` @@~DEBUG: ORIGINAL >>kennung<< ~@@ ` an jeder stillgelegten Originalzeile, ` @@~DEBUG: START >>kennung<< ~~~~~~~~~~~~@@ ` und ` @@~DEBUG: END >>kennung<< ~~~~~~~~~~~~@@ ` um Blöcke ab fünf Debug-Zeilen, dazu die Trennzeile ` @@~~~~~~~~~~~~~~~~~~~~~~~~@@ ` vor jedem START und nach jedem END. Die genauen Fälle und Beispiele für Python, C-artige Sprachen und Shell stehen in `marks.de.md`.

**Warum `@@~` der Rahmen ist.** Das Rahmenzeichen darf nicht mit dem Kommentarzeichen einer Sprache kollidieren, kein Regex-Metazeichen sein, keine Sonderbedeutung in der Shell haben und in Quelltext praktisch nicht vorkommen — gesucht wird nach `@@~`, nicht nach `@@` allein. Geprüft und verworfen wurden: `%%`, weil `%%~` in Windows-Batch gängige Syntax ist (`%%~dp0`); `!!`, weil eine interaktive Bash `!!` auch in doppelten Anführungszeichen als History-Expansion auflöst und der Selbsttest-Befehl damit stillschweigend etwas anderes täte; `||`, weil `|` ein Metazeichen ist und Escaping erzwänge; und `§`, weil es auf US-Tastaturen nicht existiert. Die beiden Kollisionen von `@@` — Rubys Klassenvariablen und die Hunk-Köpfe in Diffs — treffen das Suchmuster nicht, weil dort nie eine Tilde folgt. Wer den Skill anpasst, sollte den Rahmen deshalb nicht gegen ein bequemeres Zeichen tauschen.

**Warum die Tilden nie zu zweit auftreten.** Zwei Tilden sind in Markdown Durchstreichung, und Kommentare und Docstrings könnten Markdown enthalten. Erlaubt ist deshalb eine Tilde oder drei und mehr; die Anzahl selbst ist reine Optik und für die Suche gleichgültig.

**Die Marken sind in beiden Sprachfassungen gleich.** Sie sind Marker und keine Prosa und wurden bewusst nicht übersetzt: Sonst fände ein Projekt, in dem beide Fassungen im Umlauf waren, seinen Debug-Code nicht mehr mit einem einzigen Suchlauf.

**Kennungen und Verschachtelung.** Jede Marke trägt zwischen `>>` und `<<` die Kennung ihres Debug-Vorhabens. Sie ist nötig, weil Debug-Vorhaben ineinander entstehen: Ein zweites beginnt mitten im ersten, und beim Aufräumen des inneren muss erkennbar bleiben, welche stillgelegte Zeile zum äußeren gehört. Ohne Kennung wäre das nur aus der Lage im Code zu erraten — und eine falsche Zuordnung reaktiviert Originalcode, den das noch laufende Vorhaben stillgelegt hat. Der Schaden sieht dann wie ein Programmfehler aus, nicht wie ein Aufräumfehler. Die Kennung benennt deshalb die Frage, der nachgegangen wird, nicht die Codestelle: Zwei Vorhaben in derselben Funktion bekämen sonst dieselbe.

**Der Selbsttest.** Nach dem Schreiben der Debug-Änderungen läuft `grep -rn '@@~DEBUG' .` und die Trefferzahl wird gegen die Zahl der Änderungen gehalten: jede Blockmarkierung zählt zwei Treffer, jede sonstige markierte Zeile einen. Stimmen die Zahlen nicht, fehlt eine Marke. Beim Aufräumen läuft stattdessen `grep -rn '@@~' .` — dieses Muster findet zusätzlich die Trennzeilen, die sonst liegenblieben. **Wo Claude keinen Dateizugriff hat, führt der Nutzer diese Läufe aus**; Claude nennt ihm das Muster und die erwartete Trefferzahl.

**Warum der Nutzer entscheidet, wenn Claude die Dateien nicht erreicht.** Dort kostet jede Marke ihn Arbeit — er trägt sie ein und baut sie aus. Also legt Claude ihm die Wahl einmal vor, kurz und mit einem Beispiel, und hält sich an seine Antwort. Lehnt er ab, wird gefragt, ob eine einfachere Markierung gewünscht ist; sein Vorschlag gilt dann unverändert und wird nicht beurteilt. Eine Rückbauliste führt Claude nicht — der Chat trägt sie bereits.

**Warum die Methodenschritte nur im Handover-Fall stehen.** Mit unmittelbarem Dateizugriff entscheidet Claude selbst, wie debuggt wird, wie gestartet und wie ausgewertet wird; das ist Handwerk und braucht keine Regel. Erst wenn der Nutzer dazwischensitzt, wird die Wahl der Probe zur Frage — weil jeder Schritt ihn Arbeit kostet und weil die eigene Ausführungsumgebung nicht seine ist.

**Originalcode wird nie gelöscht,** nur auskommentiert. Die stillgelegte Zeile ist die einzige verlässliche Quelle für den Rückweg — sie steht im Suchlauf, im Diff und noch dort, wenn jemand anders aufräumt.

**Aufräumen richtet sich nach dem Auftrag, nicht nach dem Alter.** Debug-Code aus dem laufenden Auftrag entfernt Claude selbständig; Debug-Code aus einem abgeschlossenen Auftrag legt er dem Nutzer vor. Lehnt der Nutzer ab, kommt dieselbe Stelle erst bei einem neuen Tag, einem neuen Chat oder auf ausdrücklichen Auftrag wieder zur Sprache. **Entschieden wird dabei nie per Skript:** Der Suchlauf findet die Marken, was an einer Fundstelle geschieht, prüft Claude an ihr selbst — Markierungen können völlig anders gesetzt sein, als die Regeln es vorsehen.

**Die Anker in den Triggern.** Beide Snippets binden an Claudes eigene Handlung, nicht an eine Anfrage des Nutzers — im einen Fall an das Einfügen, im anderen an den Vorschlag. Der Satz „auch dann, wenn der Nutzer nicht von Debugging gesprochen hat“ ist jeweils der wirksame Teil. Das Handover-Snippet hat zusätzlich den Auftrag, die Frage nach der Kennzeichnung rechtzeitig auszulösen — nämlich bevor der Nutzer die erste Zeile von Hand einträgt.

## Stand und Offenes

**Status:** Anweisungen vollständig, Frontmatter gesetzt, zwei stille Trigger, Description in der dritten Person. Am 29. August 2026 sind die Marken vollständig neu gefasst worden — Rahmen `@@~` statt der alten Doppelraute, Kennung je Debug-Vorhaben, Verschachtelung, Trennzeilen —, und am 30. August ist der Skill in einen gemeinsamen Teil und zwei Umgebungszweige geteilt worden. Beide Sprachfassungen sind dabei gemeinsam entstanden.

**Offen:** Die neue Markenform und die Teilung waren noch nie im Einsatz. Das macht den Skill nicht unbenutzbar — sein erster Einsatz ist zugleich ihre Erprobung. Ungeprüft ist insbesondere, ob ein hochgeladener Skill auf claude.ai die nachgeladenen Dateien tatsächlich zieht.

**Bewusst offen gelassen:** Ob der Skill auf claude.ai überhaupt installiert wird, ist eine Nutzungsentscheidung und keine technische Frage. Die Description kostet dort dauerhaft Platz in der Skill-Listung, ob sie auslöst oder nicht.
