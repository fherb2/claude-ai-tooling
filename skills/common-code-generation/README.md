# common-code-generation — Allgemeine Regeln für das Erzeugen und Ändern von Code

*Stand: 2026-08-30*

**✅ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden, deutsche und englische Fassung vorhanden. — Keine inhaltlichen Unterschiede zwischen der Version für Claude.ai / Claude Desktop (Chat + Cowork) sowie Claude Code.

**Sammelt die allgemeinen Regeln der Zusammenarbeit beim Erzeugen und Ändern von Code** — die Art Festlegungen, die sonst in jeder `CLAUDE.md` wiederholt stehen müsste: englische Benennungen im Quelltext, kein ungefragt erweiterter Funktionsumfang, sparsamer Umgang mit Rechenzeit und Speicher. Benennungen und Optimierungen werden dabei **vorgeschlagen, nicht entschieden**; die Entscheidung bleibt beim Nutzer.

Die Regeln gelten, sobald in einer Sitzung Code entsteht oder geändert wird — und von da an durchgehend, nicht nur für den Schritt, der sie ausgelöst hat.

**Nicht** Gegenstand ist die Pflicht, vor einer Dateiänderung einen Plan vorzulegen und die Zustimmung abzuwarten. Sie bleibt in der `CLAUDE.md` des Projekts, weil ein Skill nur wahrscheinlich lädt, eine Schutzregel aber sicher greifen muss. Ebenfalls nicht Gegenstand: der Aufbau von Konzept- und Implementierungsdokumentation und der Umgang mit temporärem Debug-Code.

## Installation

### Claude Code

1. **Paket herunterladen.** `downloads/common-code-generation_de_local.zip`

2. **Entpacken.** Das Archiv enthält einen Ordner `common-code-generation/` mit allen Dateien. Entpacke ihn nach `~/.claude/skills/` — dann gilt der Skill für alle Projekte — oder nach `.claude/skills/` im Projekt, dann nur dort. Ein vorhandener Ordner gleichen Namens wird ersetzt; es bleibt nichts Altes liegen.

3. **Stillen Trigger übernehmen.** Das musst Du händisch tun. Claude erkennt dann leichter aus dem Kontext heraus, ob der Skill geladen werden soll. Dazu: Aus `CLAUDE-snippet.md` kommt **alles unterhalb der Trennlinie** in die `CLAUDE.md` des gewählten Orts. Der kursive Text darüber bleibt zurück; die Datei selbst bleibt im Skill-Ordner liegen und zeigt an ihrer Datumszeile, von welchem Stand der übernommene Trigger ist.

   Ohne diesen Schritt wirkt der Skill nur beim ausdrücklichen Aufruf mit `/common-code-generation`.

### claude.ai und Claude Desktop (Chat + Cowork)

1. **Paket herunterladen.** `downloads/common-code-generation_de_web.zip`

2. **Hochladen.** Im dafür vorgesehenen Verwaltungsfeld für Skills der Anwendung das Archiv hochladen. Der Skill gilt danach für Dein Konto — nicht für Deine Organisation, und nicht gleichzeitig in Claude Code.

3. **Stillen Trigger übernehmen.** Das musst Du händisch tun. Claude erkennt dann leichter aus dem Kontext heraus, ob der Skill geladen werden soll. Dazu: Aus `CLAUDE-snippet.md` im Archiv kommt **alles unterhalb der Trennlinie** in das Anweisungsfeld — global für das Konto oder für das einzelne Projekt.

   Ohne diesen Schritt wirkt der Skill nur beim ausdrücklichen Aufruf mit `/common-code-generation`.

Beide Pakete tragen denselben Inhalt — der Skill unterscheidet sich zwischen den Zielwelten nicht. Getrennt sind sie allein, damit der Name sagt, wohin das Archiv gehört.

## Details

**Sprache und Benennungen.** Alles im Quelltext — Bezeichner, Kommentare, Docstrings — steht auf Englisch. Selbst gewählte Namen werden dem Nutzer übersichtlich zur Entscheidung vorgelegt; kurz und treffend geht vor lang, und die Code-Styling-Vorgaben des Projekts gelten primär. Will der Nutzer sie durchbrechen, wird er darauf hingewiesen — hat aber das letzte Wort.

**Kein ungefragter Funktionsumfang.** Erzeugt wird nur, was für die Aufgabe zwingend nötig ist. Nice-to-have-Funktionen und Qualitätsverbesserungen werden früh **vorgeschlagen** und nachträglich ergänzt, nicht stillschweigend eingebaut. Der bereits realisierte Funktionsumfang wird nie ohne vorherige Absprache erweitert.

**Rangfolge der Ressourcen.** Rechenzeit (besonders in Schleifen, häufig gerufenen Funktionen und bei I/O), dann Arbeitsspeicher, dann Massenspeicher. Stehen Optimierungen einander entgegen, entscheidet der Nutzer über die Priorität.

**Optimierungen gegen die Realität prüfen.** Bevor ein Vorschlag unterbreitet wird, sind zwei Fragen zu beantworten: Lohnt er sich im tatsächlichen Anwendungsfall — auch gemessen an der erhöhten Wahrscheinlichkeit, unentdeckte Fehler einzubauen? Und ist sein Effekt über die Gesamtapplikation überhaupt relevant? Fehlt dafür Wissen über Nutzung, Hardware und geplanten Endzustand, wird gefragt statt geraten.

**Vorwissen in Schleifen.** Treten in einer Schleife mehrere Abbruchkriterien auf, werden sie nach Vorwissen über die Daten so angeordnet, dass im Mittel früh abgebrochen wird. Dazu gehört der Hinweis an den Nutzer, dass der Compiler die Reihenfolge im Maschinencode ohnehin ändert und sich das nur über Direktiven oder Argumente sicherstellen lässt.

**Warum der Anker so früh liegt.** Der Skill ist kein Ablauf mit einem Startmoment, sondern ein Regelwerk, das ab der ersten Zeile Code durchgehend gilt. Weil sein Körper nach dem Laden für den Rest der Sitzung im Kontext bleibt, zählt allein der früheste Treffer (Vorgaben, Kapitel 2.1). Die im Skilltext selbst genannten Momente — benennen, vorschlagen, entscheiden — kämen zu spät. Beim Anpassen an ein Projekt darf der Anker verschoben, aber nicht weggelassen werden.

**Und die Plan-Pflicht bleibt draußen,** so verlockend es aussieht, sie hierher zu holen: Ein Trigger ist probabilistisch, eine Schutzregel muss sicher greifen.

**Zur Entstehung.** Der Text stammt aus einer `CLAUDE.md` des Nutzers. Am 16. August 2026 überarbeitet: Die zuvor getrennten Rollenwörter „Entwickler" und „Anwender" sind entfallen — es gibt nur noch den Nutzer, den Menschen im Chat (Vorgaben, Kapitel 7). Mit ihnen entfielen die Abschnitte über Bedienergonomie und Umgangston, und der stille Trigger verlor seine zweite Bedingung: Er sollte auch feuern, sobald die Applikation ein eigenes Frontend enthält oder Daten an ein externes liefert. Bleibt es dabei, dass Ergonomie kein Gegenstand dieses Skills ist, hat der Trigger nur noch den Anker an der ersten Codeberührung. Die englische Fassung ist am selben Tag als Übersetzung der deutschen entstanden.

## Stand und Offenes

**Status:** Anweisungen vollständig, Frontmatter gesetzt, stiller Trigger vorhanden, Description in der dritten Person. Bei der Nutzung noch beobachten, ob Anpassungen nötig werden; die Erprobung am Zielort findet statt, wenn der Skill dort gebraucht wird.

**Offen:** derzeit nichts.
