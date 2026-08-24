# correct-zaaack-md-editor-mistakes — beschädigten Leerraum in Markdown-Tabellen finden und beheben

*Stand: 2026-08-24*

*[English version](README.en.md)*

✅☑ **Fertig und benutzbar, in beiden Sprachfassungen.** Werkzeuge, Skilltext und stiller Trigger stehen, das Frontmatter ist gesetzt. Was noch offen ist, steht im Schlussabschnitt — es hindert den Einsatz nicht.

## Überblick

**Manche WYSIWYG-Editoren für Markdown beschädigen beim Speichern die Tabellen der bearbeiteten Datei. Dieser Skill lässt Claude den Schaden selbst finden und beheben, ohne dass der Nutzer bei jeder Gelegenheit darauf hinweisen muss.** Beobachtet wurde das Verhalten an `zaaack.markdown-editor` für VSCode; die Werkzeuge fragen aber nicht nach dem Editor, sondern nach dem Schaden, und sind deshalb nicht an ihn gebunden.

Drei Dinge leistet der Skill. Er lässt Claude die Artefakte erkennen, sobald sie zum ersten Mal auffallen. Er holt beim Nutzer eine Dauerfreigabe ein, damit die Korrektur danach ohne Rückfrage läuft — sonst legt Claude nach seinen sonstigen Regeln jede Dateiänderung erst zur Entscheidung vor, und die Automatik wäre keine. Und er hält das Ergebnis im Projektgedächtnis fest, damit die Frage nicht in jeder Sitzung neu gestellt wird.

**Abgrenzung.** Der Skill formatiert kein Markdown und räumt keine Tabellen auf. Er behebt genau zwei Sorten beschädigten Leerraums in Tabellenzeilen und lässt alles andere unberührt: kein Wort, keine Zeichensetzung, keine Spaltenausrichtung, keine doppelten Leerzeilen. Er wirkt nur dort, wo Claude Dateien lesen und schreiben kann; in claude.ai ist er gegenstandslos, weil die Werkzeuge fehlen und `${CLAUDE_SKILL_DIR}` dort nicht aufgelöst wird.

## Installation

**1. Zielort wählen.**

| Ort         | Pfad                                                        | Gilt für                  |
| ----------- | ----------------------------------------------------------- | ------------------------- |
| Persönlich  | `~/.claude/skills/correct-zaaack-md-editor-mistakes/`       | alle Projekte des Nutzers |
| Projekt     | `.claude/skills/correct-zaaack-md-editor-mistakes/`         | nur dieses Projekt        |

Wer den Editor überhaupt benutzt, benutzt ihn in aller Regel überall — der persönliche Ort ist deshalb der naheliegende. Dagegen spricht einzig `SKIP` (siehe „Der Geltungsbereich"): Die Ausnahmeliste ist projektbezogen, und eine persönliche Installation trägt für alle Projekte dieselbe.

**2. Ordner vollständig kopieren und die Sprachfassung wählen.** Der Ordnername bleibt unverändert, der Ordner wird komplett kopiert. `SKILL.md` und `CLAUDE-snippet.md` liegen hier zweisprachig; die gewünschte SKILL-Fassung wird am Zielort **zusätzlich** als `SKILL.md` abgelegt — Claude Code erkennt ausschließlich diesen Namen, eine `SKILL.de.md` allein ist kein Skill. Alles Übrige, beide READMEs und die Snippet-Dateien eingeschlossen, bleibt unverändert liegen; die Datumszeilen zeigen den Stand der Installation.

```text
SKILL.de.md  oder  SKILL.en.md          ->  zusätzlich als SKILL.md ablegen
README.md, README.en.md                 ->  unverändert mit
CLAUDE-snippet.de.md, CLAUDE-snippet.en.md  ->  unverändert mit
md_table_artifacts.py, scan_md_tables.py, fix_md_tables.py
```

Welche Sprache, richtet sich nach der, in der üblicherweise gearbeitet wird: Der Körper der `SKILL.md` liegt nach dem Laden für den Rest der Sitzung im Kontext und prägt die Sprache, in der Claude anschließend antwortet.

Ein `__pycache__/` entsteht, sobald die Werkzeuge einmal gelaufen sind. Es gehört nicht mit an den Zielort und wird auch nicht mitversioniert.

**Die `README.md` ist bei diesem Skill keine Beigabe, sondern Pflicht.** Bei anderen Skills kostet ihr Fehlen am Zielort nur Begründungstiefe bei Nachfragen; hier verweist die `SKILL.md` für die Hook-Einrichtung ausdrücklich auf sie, statt die Beschreibung dauerhaft im Kontext mitzuschleppen. Fehlt sie, zeigt der Verweis ins Leere.

**3. Stillen Trigger übernehmen.** Der Inhalt **unterhalb der Trennlinie** in `CLAUDE-snippet.de.md` bzw. `CLAUDE-snippet.en.md` wird in die `CLAUDE.md` des Zielorts übernommen — bei persönlicher Installation in `~/.claude/CLAUDE.md`, bei projektbezogener in die des Projekts. Die kursiven Absätze oberhalb der Trennlinie sind die Anleitung dazu und werden nicht mitkopiert; sie nennen auch, was beim Anpassen des Wortlauts nicht wegfallen darf. Die Snippet-Dateien wandern mit an den Zielort und bleiben dort liegen: Wirksam ist allein die `CLAUDE.md`; ihre Datumszeilen zeigen, von welchem Stand der übernommene Trigger ist.

Ohne diesen Schritt funktioniert der Skill weiter, wird aber nur geladen, wenn er ausdrücklich mit `/correct-zaaack-md-editor-mistakes` aufgerufen wird oder eine Anfrage seiner Beschreibung nahe genug kommt. Das ist bei diesem Skill der Regelfall des Versagens: Niemand bittet von sich aus darum, Tabellen auf Leerzeichen zu prüfen.

**4. Optional den Hook einrichten** — siehe „Verlässlichkeit: der Hook".

## Details

### Was der Editor anrichtet

Zwei Arten sind belegt.

**Gefressene Leerzeichen** vor einem öffnenden Trenner für Inline-Code oder Fettdruck. Beispiele aus diesem Repository, vor der Korrektur:

```text
so stand es da                so muss es heißen
GNU`find`                     GNU `find`
macOS:`brew install jq`       macOS: `brew install jq`
claude.ai**und** lokal        claude.ai **und** lokal
```

Sichtbar, wenn man darauf achtet — und genau deshalb leicht zu übersehen.

**Diese Beispiele stehen in einem Codeblock und nicht in einer Tabelle, und das ist keine Geschmacksfrage.** Die Werkzeuge unterscheiden ein dokumentiertes Gegenbeispiel nicht von einem echten Defekt: Stünden die kaputten Fassungen in einer Tabellenzeile, hielte der Prüfer sie für Fundstellen und der Korrektor würde die Dokumentation reparieren, bis sie nichts mehr zeigt. Genau das ist beim Schreiben dieser Datei eingetreten — elf gemeldete „Artefakte" in einer Datei, die nur beschreibt. Der Prüfer sieht ausschließlich Zeilen an, die mit `|` beginnen; ein Codeblock ist damit immun. Wer die Beispiele umformatiert, holt den Fehler zurück.

**Geschützte Leerzeichen** (U+00A0) anstelle gewöhnlicher. Das ist die schlimmere Art: Im gerenderten Text sieht man keinen Unterschied und im Editor auch nicht, aber jede Suche über den Wortlaut scheitert. Wer nach „Vorgaben automatisch" sucht, findet die Zeile nicht, obwohl sie dasteht. Sechs solche Zeichen standen in diesem Repository, alle in Tabellen, keines absichtlich.

**Was nicht gemessen ist:** ob der Editor auch außerhalb von Tabellen Leerzeichen frisst. Bisher sind Artefakte ausschließlich in Tabellenzeilen aufgetreten, und die Werkzeuge sehen deshalb auch nur dort hin. Ob es weitere Arten gibt, ist ebenso offen. Wer eine findet, erweitert `md_table_artifacts.py` — und trägt sie hier nach.

### Die drei Grenzen — und warum sie so gezogen sind

Sie stehen samt Begründung in den Docstrings von `md_table_artifacts.py`. Dort, weil sie beim Umbau des Kerns gelesen werden müssen: Alle drei sehen wie Nachlässigkeiten aus und sind keine.

**Ein Leerzeichen wird nur *vor* einem Trenner eingesetzt, nie *dahinter*.** Eine an eine Code-Spanne geklebte Endung ist normale Prosa: `` `uuid`s `` heißt „mehrere uuid" und ist richtig so. Wer die Regel symmetrisch macht, zerstört solche Stellen. Der Prüfer meldet sie unter `notes`, damit ein Mensch sie einmal ansieht.

**Einfaches `*kursiv*` wird nicht erkannt.** Erkannt werden `**fett**` und `` `code` ``. Bei einem einzelnen Sternchen ist die Verwechslungsgefahr mit Aufzählungszeichen und Rechenzeichen zu groß, und eine falsche Korrektur wäre still. Diese Lücke fängt kein Werkzeug ab — sie ist der einzige Punkt, an dem Claude selbst hinsehen muss. Eine solche Stelle ist in diesem Repository aufgetreten und von Hand behoben worden.

**Doppelte Leerzeilen vor Tabellen werden nicht angetastet.** Der Markdown-Linter meldet sie (`MD012`), 35-mal in diesem Repository. Sie ändern die Darstellung nicht, und der Editor setzt sie beim nächsten Speichern wieder ein — dagegen anzuputzen ist verlorene Mühe.

### Wie die Werkzeuge gebaut sind

Drei Dateien, und die Aufteilung hat je einen Grund.

`md_table_artifacts.py` trägt die Regeln: was ein Artefakt ist, was in den Geltungsbereich fällt, wie eine Tabellenzeile repariert wird, und welche Artefaktarten überhaupt reparabel sind. Es wird nur importiert, nie aufgerufen. **Der Grund ist keine Ordnungsliebe:** Vorher stand die Erkennung in beiden Kommandos, und zwei Fassungen derselben Regel driften auseinander. Dann meldet der Prüfer Stellen, die der Korrektor nicht anfasst — oder, schlimmer, der Korrektor ändert etwas, das der Prüfer nie gemeldet hat.

`scan_md_tables.py` bekommt **einen** Pfad und steigt selbst bis in jede Verzweigung hinab. Es schreibt nie, damit ein falsch gesetzter Schalter in einem Hook keinen stillen Schaden anrichten kann.

`fix_md_tables.py` liest die Liste des Prüfers von `stdin` und arbeitet nur die genannten Dateien ab.

**Kein Zustand auf der Platte.** Der Prüfer schreibt sein JSON nach `stdout`; in der Korrekturstufe fließt es direkt weiter, ohne die Platte zu berühren. Keine Zwischendatei heißt: keine veraltete Liste, kein Aufräumen, nichts, was zwischen Sitzungen liegenbleibt.

**Die Liste trägt Pfade und Anzahlen, keine Zeilennummern.** Der Korrektor liest jede Datei ohnehin neu und leitet seine Reparaturen aus dem aktuellen Inhalt ab. Eine Zeilennummer wäre veraltet, sobald zwischen den beiden Läufen gespeichert wird, und würde ihn an die falsche Stelle greifen lassen. Aus dem gleichen Grund lässt die Korrekturstufe den Prüfer erneut laufen, statt eine Liste aufzubewahren.

**Zwei Listen, und der Unterschied ist der Kern der Sache.** `files` ist die Arbeitsliste und bestimmt allein den Rückgabewert. `notes` trägt, was gemeldet aber absichtlich nie korrigiert wird. Wären die Notizen in der Arbeitsliste, könnte die Leerprobe nie aufgehen: Der Rückgabewert bliebe für immer 1, und ein Hook schlüge bei jedem Commit an, ohne dass es je etwas zu tun gäbe. Genau so war die erste Fassung gebaut, und in diesem Repository wäre der Fehler sofort eingetreten — `home-.claude-sharing/offener_fall_chatprotokolle.md` trägt in Zeile 101 ein gewolltes `` `uuid`s ``.

### Der Geltungsbereich: `SKIP`

`SKIP` in `md_table_artifacts.py` nennt die Pfadbestandteile, die nie angesehen werden. Derzeit sind das `/.git/` und der Ordner der abgelegten Arbeitsanweisungen dieses Repositories. **Das ist die eine projektbezogene Einstellung** — wer die Werkzeuge in ein anderes Projekt bringt, prüft die Liste zuerst.

`SKIP` liegt im Kern und nicht im Korrektor, damit der Geltungsbereich nicht an zwei Stellen entschieden wird.

### Verlässlichkeit: der Hook

Ein Skill wird geladen, wenn etwas auf ihn hindeutet — nicht mit Sicherheit. Für „bei jedem Commit, ohne Ausnahme" ist das zu wenig. Das leistet nur ein Hook, weil Claude Code ihn ausführt, ohne dass ein Modell sich dafür entscheiden muss: *„certain actions always happen rather than relying on the LLM to choose to run them"* ([Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide)).

Der Eintrag gehört in `.claude/settings.json` des Projekts — laut Doku die Ebene, die versioniert und geteilt werden darf. Zwei Ereignisse tragen die Aufgabe:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/skills/correct-zaaack-md-editor-mistakes/scan_md_tables.py \"$CLAUDE_PROJECT_DIR\" | python3 ~/.claude/skills/correct-zaaack-md-editor-mistakes/fix_md_tables.py" }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "if": "Bash(git commit*)", "command": "python3 ~/.claude/skills/correct-zaaack-md-editor-mistakes/scan_md_tables.py \"$CLAUDE_PROJECT_DIR\" | python3 ~/.claude/skills/correct-zaaack-md-editor-mistakes/fix_md_tables.py && git -C \"$CLAUDE_PROJECT_DIR\" add -A" }]
      }
    ]
  }
}
```

Drei Feinheiten dazu:

**Der Pfad muss absolut sein.** Mit einem absoluten Wurzelpfad gibt der Prüfer absolute Pfade aus, und damit ist das Arbeitsverzeichnis des Korrektors gleichgültig. Mit einem relativen Pfad müssten beide aus demselben Verzeichnis laufen — in einem Hook eine unnötige Annahme.

**Das `git add -A` im Commit-Hook** ist nötig, weil der Hook vor dem Commit läuft: Ohne erneutes Vormerken landet die Korrektur nicht in dem Commit, den sie retten soll. Der Umfang `-A` entspricht der Festlegung dieses Repositories, immer das Gesamtprojekt zu committen; wer selektiv committet, braucht hier etwas anderes.

**Nicht auf `*.md` eingeschränkt.** Der Matcher `Edit|Write` feuert nach jeder Dateiänderung, nicht nur nach Markdown. Das ist Absicht: Der ganze Durchlauf über dieses Repository dauert 50 ms, davon ein Fünftel Interpreterstart — eine Einschränkung würde nichts einsparen und eine Bedingungssyntax verlangen, die hier nicht nachgeprüft wurde.

**Eine Lücke bleibt, und sie ist grundsätzlich.** Speichert der Nutzer in seinem Editor, läuft kein Werkzeug von Claude — also feuert auch kein Hook auf Werkzeugereignisse. Seine Änderungen fallen erst auf, wenn Claude die Datei das nächste Mal anfasst oder committet. Das Ereignis `FileChanged` wäre dafür gedacht, taugt aber nicht: Sein Matcher nimmt nur wörtliche Dateinamen, „Claude Code splits this value into literal filenames rather than evaluating it as a regex" ([Hooks reference](https://code.claude.com/docs/en/hooks)), und der zulässige Zeichensatz ist auf „letters, digits, `_`, and `|` only" beschränkt. Für „alle `*.md`" müsste man jede Datei einzeln auflisten.

### Was im Gedächtnis landet — und was nicht

Der Skill lässt Claude festhalten, ob dieses Projekt betroffen ist, und **auch eine Absage**. Ohne die zweite Hälfte beginnt die Rückfrage in jeder Sitzung von neuem.

Festgehalten wird eine Feststellung über das Projekt, nicht eine Behauptung über den Nutzer. Der Grund: Artefakte in einer Datei beweisen nur, dass die Datei durch so einen Editor gegangen ist — das kann ein Kollege gewesen sein oder ein alter Commit.

**Das Projektgedächtnis liegt unter `~/.claude/projects/<projekt>/memory/` und gilt nur für dieses Projekt.** Im nächsten Repository beginnt die Frage von vorn. Wer den Editor überall benutzt, nimmt die Feststellung besser in `~/.claude/CLAUDE.md` auf; der Skill schlägt das vor, schreibt dort aber nicht selbst hinein.

### Stand des Wissens

Erkennung und Korrektur sind an einem Prüfbaum mit Grenzfällen belegt: Ordnername mit Leerzeichen und Emoji (übersteht den Weg durch JSON in den Korrektor), gewollte Endung an einer Code-Spanne (unverändert, per Prüfsummenvergleich), `.git` ausgenommen (ebenso), Datei ohne Tabelle übergangen. Danach Leerprobe mit leerer Arbeitsliste und Rückgabewert 0.

Am echten Repository: 67 Markdown-Dateien, 1.037 KB, davon 28 mit Tabellen. Erster Aufräumlauf: 40 gefressene Leerzeichen und 6 geschützte in 8 Dateien. Laufzeit des Prüfers über alles 50 ms.

Nicht belegt ist alles, was oben ausdrücklich als „nicht gemessen" steht — insbesondere, ob der Editor außerhalb von Tabellen Schaden anrichtet.

### Auslösung: gemessen am 24. August 2026

Verfahren nach Kapitel 4.2 der Vorgaben: Wegwerf-Projekt mit einer `CLAUDE.md`, die nur den Trigger trägt, und einem Ladeindikator, dessen `description` die echte ist. Nachgewiesen am Strom von `claude -p --output-format stream-json --verbose`, nicht an der Selbstauskunft des Modells. Je Bedingung ein Lauf — Richtungsbefund, kein Beweis.

| Bedingung | Sonnet 5 | Opus 5 |
| --- | --- | --- |
| themenfremde Frage (darf nicht feuern) | feuert nicht | feuert nicht |
| „Ergänze in `doku.md` eine Tabellenzeile" | feuert | feuert |
| „Committe die Änderungen" | feuert | feuert |
| ausdrücklich nach Leerzeichen gefragt | feuert | feuert |

**Der Trigger feuert früh genug.** Bei Opus war der Skill-Aufruf die erste Handlung überhaupt, bei Sonnet die zweite — in beiden Fällen vor dem ersten Lesen der Datei. Das ist die Eigenschaft, auf der Kapitel 2.1 besteht: Ein späterer Treffer rettet keine Entscheidung, die vorher schon gefallen ist.

**Die Dauerfreigabe wirkt nicht, solange sie nur im Skill steht.** A/B-Vergleich mit gleichem Prompt, gleichen Modellen und gleichem Skill; geändert wurde allein der `CLAUDE.md`-Eintrag:

| Der Freigabesatz steht … | Sonnet 5 | Opus 5 |
| --- | --- | --- |
| nur im Skill-Körper | Plan vorgelegt, nichts korrigiert | Plan vorgelegt, nichts korrigiert |
| auch im `CLAUDE.md`-Eintrag | korrigiert und gemeldet | korrigiert und gemeldet |

Der Grund ist die Rangordnung. Die Regel „keine Dateiänderung ohne vorgelegten Plan" steht in der `CLAUDE.md` und gilt bedingungslos; eine Freigabe, die nur im Skill-Körper steht, tritt gegen sie an und verliert. Beide Modelle entschieden gleich, ohne zu zögern. **Wer die Automatik will, muss den Freigabesatz in den `CLAUDE.md`-Eintrag aufnehmen** — im Skill allein ist er wirkungslos.

Nebenbefund, der die Grenze der Freigabe bestätigt: In der wirksamen Fassung korrigierten beide Modelle den Leerraum ohne Rückfrage, meldeten ihn hinterher — und legten die *eigentliche* Aufgabe, eine neue Tabellenzeile, weiterhin als Plan vor. Die Freigabe deckt also genau das, was sie benennt, und nicht mehr. Der produktive Prüfer bestätigte danach: keine Fundstelle mehr, die Handkorrektur der Modelle deckte sich mit dem, was das Werkzeug getan hätte.

## Stand und Offenes

**Status.** Fertig und benutzbar. Werkzeuge geprüft, Skilltext und stiller Trigger ausformuliert, Frontmatter gesetzt, beide Sprachfassungen vorhanden.

**Offen:**

- **Ob der Editor außerhalb von Tabellen Schaden anrichtet**, ist nicht gemessen. Fällt so ein Fall auf, gehört er in `md_table_artifacts.py` und in diese README.

**Zum Namen.** `correct-zaaack-md-editor-mistakes` nennt einen bestimmten Editor, obwohl die Werkzeuge nach dem Schaden fragen und nicht nach dessen Urheber — sie greifen bei jedem Editor, der dasselbe anrichtet. Ein Name wie `md-table-whitespace` wäre haltbarer. Der Name ist bewusst so gewählt und keine Nachlässigkeit; wer ihn ändert, ändert Ordnername, `name` im Frontmatter beider `SKILL`-Fassungen, den Slash-Aufruf und den Verweis in beiden `CLAUDE-snippet`-Fassungen mit.

**Bewusst offen gelassen:**

- **Ob ein Hook eingerichtet wird, entscheidet das Zielprojekt.** Der Skill setzt keinen und kann keinen setzen; er benennt ihn und beschreibt die Einrichtung.
- **Der Inhalt von `SKIP`** gehört dem Zielprojekt. Die derzeitige Liste ist die dieses Repositories und keine Empfehlung.
