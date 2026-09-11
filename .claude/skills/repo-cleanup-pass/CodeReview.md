# Code-Review: `.claude/skills/repo-cleanup-pass`

*Erstellt: 2026-09-11*

Reviewer: Claude (Fable 5.1), im Auftrag des Entwicklers. Gegenstand sind die acht Dateien des Skill-Ordners (per `ls` bestätigt, weitere gibt es nicht): `SKILL.md`, `rules.md`, `IMPORTANT.md`, `files/branch-diff.py`, `files/find-sandbox-masks.sh`, `files/readme-audit.sh`, `files/datelines-since.sh`, `files/repack-package-readme.sh`. Diese Datei ist die eigene Befunddatei des Reviewers nach Projekt-CLAUDE.md „Reviews und ihre Bearbeitung"; sie wird bei der Nachbearbeitung mit ihrem Datum als Anhang übernommen und hier entfernt.

## 1 Umfang und Grenzen des Reviews

Das Review war auf Lesezugriffe beschränkt; Bash-Kommandos liefen nur nach Einzelfreigabe des Entwicklers und ausschließlich lesend. Ausgeführt wurden: `ls` auf Skill-Ordner, Projektwurzel und `.claude/`; `git ls-tree`, `git worktree list`, `git branch -a`, `git status`, `git log` und `git show master:README*.md`; `git ls-files '*README*.md'` und zwei `grep`-Läufe; die drei ausgabe-only-Werkzeuge des Skills (`readme-audit.sh`, `datelines-since.sh master`, `find-sandbox-masks.sh`); `branch-diff.py --from dev --to master` mit Ablage im Scratchpad; die Tabellenprüfung des Skills `correct-zaaack-md-editor-mistakes` als reiner Befundlauf (Ergebnis: keine Artefakte, keine unlesbaren Dateien); dazu `/proc/self/mounts`, `test -w` und `tempfile.gettempdir()` zur Klärung der Sandbox-Lage.

Nicht ausgeführt: der Datei-Abgleich selbst (Schritt 1, 3, 4, 5), `repack-package-readme.sh`, und jeder schreibende Git-Befehl. Aussagen darüber, wie sich Git unter der Sandbox beim Branchwechsel verhält, bleiben deshalb aus Mount-Lage und Git-Zustand **abgeleitet**; das steht dann am Befund.

Vollständig gelesen wurden neben dem Skill-Ordner: die Projekt-`CLAUDE.md`, `skill-dev-doc.md` (alle Kapitel und Anhang A), `.claude/git-worktree-model.json`, beide Wurzel-READMEs, `work-plan.md`, `.claude/settings.json`, `skills/parallel-sessions/SKILL.de.md` und `rules.de.md`. Stichproben: Kopfzeilen von `skills/temp-debug-code/README.md`, `skills/README.md`, `skills/common-code-generation/CLAUDE-snippet.de.md`, `CLAUDE.md-Snippets/README.md` und `common-snippets.de.md`, Kopfkommentar von `home-.claude-sharing/scripts/pack_packages.sh`.

## 2 Maßstab

Angelegt wurden: die Projekt-`CLAUDE.md` (Worktree-Modell, Projekt-Skills im Entwicklungszweig, Datumszeilen, ein normatives Zuhause je Aussage, Plan- und Review-Regeln), die Regeln des Worktree-Modells aus `skills/parallel-sessions/rules.de.md` (weil die Projekt-`CLAUDE.md` sie für dieses Repo verbindlich erklärt), und `skill-dev-doc.md` als Bauanleitung „für jeden Skill dieses Repositories — gleich in welchem Ordner er entsteht".

**Annahme zur Geltung der `skill-dev-doc.md`:** Sie beansprucht jeden Skill des Repositories, verlangt aber in Kapitel 5 und 5.3 Dinge, die für ein Werkzeug ohne Auslieferung gegenstandslos sind (Download-Pakete, Installationskapitel, Lizenzfeld). Dieses Review legt deshalb nur die Kapitel an, die vom Verlassen des Repos unabhängig sind: Trigger (Kapitel 2), Zweiteilung (5.2), Wortwahl (7), README als Ort für Stand und Begründung (5, 6.1), Prüfwerkzeuge (Anhang A). Ob das die richtige Auswahl ist, entscheidet der Entwickler (Frage F1, Befund B10).

Schweregrade: **hoch** = der Ablauf bricht oder verstößt gegen eine Schutzregel des Repos; **mittel** = falsche oder widersprüchliche Aussage, die beim nächsten Durchgang zu falschen Befunden oder unterlassener Arbeit führt; **niedrig** = Robustheit, Doppelung, Kosmetik. Wo eine Aussage nicht am laufenden System geprüft ist, steht **abgeleitet**; wo ein Lauf sie gezeigt hat, steht **beobachtet**.

## 3 Ausgangslage aus den Läufen

Stand 11. September 2026, für den nächsten Review als Vergleichsbasis:

| Messung | Ergebnis |
| --- | --- |
| `branch-diff.py --from dev --to master` | zu übernehmen 0, zu löschen 0, bewusst ausgeschlossen 39, Infra 0 |
| `git ls-tree master -- .claude/skills/` | leer; letzter master-Commit „Projekt-Skills aus master entfernt" (373b142) |
| `git worktree list` | nur der Haupt-Checkout, auf `dev`; `dev` ein Commit vor `origin/dev`, `master` und `infra` gleichauf |
| `/proc/self/mounts` | `.claude/skills`, `.claude/settings.json`, `.claude/settings.local.json` als `ro` eingehängt; `.claude/hooks` als Attrappe |
| `find-sandbox-masks.sh` | 19 Attrappen, deckungsgleich mit den `??`-Zeilen von `git status` |
| `readme-audit.sh` | 30 READMEs, alle mit Datum, alle mit Querverweis |
| `grep "blob/master" --include="*.md"` | 20 READMEs in genau den 10 Bereichen mit `downloads/` |
| `git diff --name-only master..HEAD` | 25 gequotete Pfade (Baustellen-Skills), die in der Ausgabe von `datelines-since.sh` fehlen |
| `tempfile.gettempdir()` unter Sandbox | `/tmp/claude-1000`, gleich `$TMPDIR` |
| Tabellenprüfung (zaaack) auf den Skill-Ordner | `files: []`, `unreadable: []` |

Projektwurzel: Die sechs Bereichsordner der Übersichtstabelle sind vollständig; daneben nur `.research/`, `.claude/`, `.vscode/`, `.git/` und die Sandbox-Attrappen. `.research/` enthält keine README.

## 4 Befunde: hoch

### B1 — Der Skill arbeitet im Haupt-Checkout und committet auf `dev` und `master`; das Worktree-Modell verbietet genau das

**Ort:** `SKILL.md`, Schritt 1 („auf dev, dann ebenso auf master: … git commit"), Schritt 3 („git checkout master"), Schritt 5 („git checkout dev"), Abschnitt „Was in jedem Fall gilt" („Ein Checkpoint-Commit je Etappe"); `rules.md`, Einleitung („die aus ihr erwachsenden Korrekturen gehören in den Entwicklungszweig") und „Jede endet mit einem Checkpoint-Commit".

**Befund:** Die Projekt-`CLAUDE.md` erklärt das Worktree-Modell für dieses Repo verbindlich. Dessen Regeln (`skills/parallel-sessions/rules.de.md`, „Das Arbeitsmodell" und „Regeln, die nie vereinfacht werden") sagen: Der Haupt-Checkout steht auf dem Integrationsbranch und gehört dem Nutzer, Claude schreibt dort keine Dateien und committet dort nur den freigegebenen Squash; der Releasebranch ist „kein Arbeitsort"; jede Handlung, die den Haupt-Checkout berührt, ist Freigabestufe „Jedes Mal". Der Skill wechselt im Haupt-Checkout den Branch, committet dort direkt auf `dev` und `master` und legt Checkpoint-Commits auf `dev` ab. Er erwähnt das Modell nicht und benennt den Widerspruch nicht. Die globale Arbeitsanweisung („Vorrang der Anweisungsebenen") verlangt: Widerspricht ein Skill einer projektspezifischen Schutzregel, gilt die Schutzregel, und der Widerspruch wird benannt.

**Vorschlag:** Entscheidung des Entwicklers festhalten, im Skill selbst (Frage F2). Zwei Wege: (a) Der Skill wird als begründete Ausnahme vom Modell deklariert, mit ausdrücklicher Freigabe je Etappe und dem Hinweis, dass der Haupt-Checkout während der Schritte 3 bis 5 auf `master` steht. (b) Der Skill folgt dem Modell: Korrekturen der Tiefenprüfung auf einer Werkbank mit Squash nach `dev`; der Übertrag nach `master` in einem eigenen Worktree (`git worktree add <worktree_dir>/_release master`), sodass der Haupt-Checkout unberührt bleibt. Weg (b) löst nebenbei B2: Die Sandbox hängt die absoluten Pfade des Haupt-Checkouts `ro` ein (beobachtet), derselbe Unterpfad eines Worktrees ist davon nicht erfasst (abgeleitet). Vorbehalt: die in `parallel-sessions` dokumentierte Kollision zwischen Sandbox und Worktrees (Issue 80278).

### B2 — Die „Bekannte Bedingung" zur Sandbox beschreibt einen Fall, der nicht mehr eintritt, und übersieht die Fälle, die jetzt eintreten

**Ort:** `SKILL.md`, Schritt 3, Absatz „Bekannte Bedingung: `.claude/skills/` ist unter aktiver Sandbox nur lesbar" (Z. 88–91); Schritt 1.

**Befund, Teil 1:** Der Absatz behandelt den Fall, dass die Übertragungsliste Dateien aus `.claude/skills/` enthält („etwa diesen Skill selbst"). Seit der dritten Ausschlussklasse (`^\.claude/skills/` in `DEFAULT_EXCLUDES`) kann dieser Fall nicht mehr eintreten: `branch-diff.py` sortiert jeden solchen Pfad in „Bewusst ausgeschlossen" (beobachtet: alle acht Dateien des Skills stehen dort). Der Absatz ist gegenstandslos und führt in die Irre.

**Befund, Teil 2:** Der Sandbox-Konflikt liegt jetzt an zwei anderen Stellen. Erstens: `master` trägt den Skill-Ordner nicht mehr (beobachtet). `git checkout master` muss deshalb die acht Skill-Dateien aus dem Arbeitsbaum entfernen und `git checkout dev` sie wieder anlegen; `.claude/skills` ist unter der Sandbox als `ro` eingehängt und `test -w` verneint (beobachtet). Der Branchwechsel in Schritt 3 und 5 scheitert damit als Ganzes, nicht für einzelne Dateien (abgeleitet, Git nicht ausgeführt). Zweitens: `.claude/settings.json` gehört zu den `infra_files` und ist ebenfalls als `ro` eingehängt (beobachtet). Schritt 1 (`git restore --source=infra -- … .claude/settings.json …`) trifft dieselbe Sperre, ohne dass der Skill dort einen Hinweis trägt (abgeleitet).

**Vorschlag:** Den Absatz in Schritt 3 streichen. Stattdessen eine Voraussetzung an den Anfang des Datei-Abgleichs: Unter aktiver Sandbox sind Schritt 1, 3 und 5 nicht durchführbar; die Sandbox wird für den Abgleich abgeschaltet, oder der Abgleich läuft nach Weg (b) aus B1. Der Hinweis „Der Index bekommt den richtigen Inhalt trotzdem" entfällt dann.

## 5 Befunde: mittel

### B3 — Die Wurzel-READMEs verweisen im Release-Zweig auf einen Ordner, der dort fehlt (Nebenbefund außerhalb des Skill-Ordners)

**Ort:** `README.md` (Wurzel), Absatz „Two files in the project root accompany …", letzter Satz („… is carried by the project's own skill `.claude/skills/repo-cleanup-pass/`"); `README.de.md`, Absatz „Zwei Dateien in der Projektwurzel begleiten …", letzter Satz.

**Befund:** Beide Sätze stehen wortgleich in `master` (beobachtet: `git show master:README.md`, Zeile 27, beide Sprachen). `master` ist bei GitHub die Startseite und trägt den genannten Ordner nicht. Der Leser des veröffentlichten Standes bekommt einen Verweis ins Leere. Die Tiefenprüfung (Etappe 1) hätte das nicht gefunden: Sie prüft Tabelle, Reifezeichen, Standzeile, Sprachverweise und Auslieferungsform, nicht die Ordnerverweise in der Prosa.

**Vorschlag:** Den Satz in beiden Fassungen um „nur im Entwicklungszweig `dev`" ergänzen oder den Verweis auf den Skill aus der Wurzel-README nehmen; Datumszeilen nachziehen; `master` nachziehen. Ob Etappe 1 um eine Prüfung der Prosa-Verweise auf Ordner erweitert wird, ist Ermessen des Entwicklers.

### B4 — Zwei Fassungen der Querverweis-Regel, die zweite unvollständig; der Hinweis auf eine offene Umstellung ist überholt

**Ort:** `rules.md`, Etappe 2, Absatz „Die Form des Querverweises" mit dem Codeblock und dem Satz „Die Regel selbst … steht in der Projekt-`CLAUDE.md`" (Z. 41–48); Unterabschnitt „Der Querverweis in Dateien, die ins Paket wandern", letzter Absatz („… noch nicht überall ausgeführt. Wer diese Etappe fährt, prüft mit.", Z. 60). Mitbetroffen: `skill-dev-doc.md`, A.2, erste Zeile der Vergleichstabelle („… noch offen — **bis dahin die einzige Meldung mit Substanz**").

**Befund:** Die Projekt-`CLAUDE.md` legt seit dem 11. September 2026 fest, dass die Form des Querverweises ausschließlich in `skill-dev-doc.md`, Kapitel 5.1 steht („Hier steht sie absichtlich nicht ein zweites Mal"). `rules.md` trägt eine zweite Fassung: relative Verweise als Regelform, dazu die Repo-URL für paketwandernde Dateien. Kapitel 5.1 kennt zusätzlich `blob/master` statt `HEAD` samt Begründung und den Suchweg `grep -rn "blob/master"`; das fehlt in `rules.md`. Zwei gleichrangige Fassungen derselben Festlegung verstoßen gegen „genau ein normatives Zuhause". Der Satz „noch nicht überall ausgeführt" ist überholt: Alle zehn Bereiche mit `downloads/` tragen in beiden Sprachfassungen die Repo-URL, die fünf übrigen READMEs verweisen relativ und wandern in kein Paket (beobachtet). Dieselbe überholte Aussage steht in der Tabelle in A.2; nach Projekt-`CLAUDE.md` („Treffen wir auf einen überholten Verweis, wird er mitbereinigt") gehört sie mit weg.

**Vorschlag:** In Etappe 2 den Codeblock und den Satz zur Projekt-`CLAUDE.md` durch einen Verweis auf Kapitel 5.1 ersetzen; den letzten Absatz des Unterabschnitts streichen, die Festlegung vom 10. September als Verweis auf 5.1 behalten. In A.2 die erste Tabellenzeile auf den erledigten Stand bringen.

### B5 — `readme-audit.sh` erkennt weder die Datumszeile noch den Querverweis in der vorgeschriebenen Form

**Ort:** `files/readme-audit.sh`, Zeilen `date=$(grep -m1 -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' "$f" …)` und `if grep -qE '\[(English version|Deutsche Fassung)\]' "$f"`.

**Befund (abgeleitet):** Als Datum gilt das erste datumsähnliche Muster irgendwo in der Datei. Eine README ohne Datumszeile, die im Text ein ISO-Datum nennt, wird nie als `KEINS` gemeldet, obwohl `rules.md` sagt, `KEINS` sei „immer ein Befund". Das Schwesterwerkzeug `datelines-since.sh` prüft das strenge Muster `^\*(Stand|Last updated): …\*`. Beim Querverweis wird nur geprüft, ob der Linktext irgendwo vorkommt; weder die Position (kursive Zeile unmittelbar unter der Datumszeile) noch die Form (Repo-URL bei paketwandernden Dateien, relativ sonst, Kapitel 5.1) wird erfasst. `rules.md` sagt „Andere Formen … werden angeglichen", das Werkzeug kann sie aber nicht zeigen; im heutigen Lauf steht bei allen 30 READMEs „vorhanden", die Form bleibt unsichtbar.

**Vorschlag:** Dasselbe Datumszeilen-Muster wie in `datelines-since.sh` verwenden. Den Querverweis als eigene Zeile prüfen (`^\*\[(English version|Deutsche Fassung)\]\(`) und eine Spalte ausgeben, ob das Ziel absolut (`https://`) oder relativ ist; dann ist Kapitel 5.1 mechanisch prüfbar.

### B6 — `datelines-since.sh` verliert gequotete Pfade still und prüft gegen „heute" statt gegen das Änderungsdatum

**Ort:** `files/datelines-since.sh`, beide Schleifen `git diff --name-only "$REF"..HEAD | while read -r f`; `TODAY=${2:-$(date +%F)}` und `if [ "$date" = "$TODAY" ]`; `rules.md`, Etappe 3, Satz „`<ref>` ist der Stand, gegen den verglichen wird — der Commit vor Beginn des Durchgangs oder der Release-Zweig".

**Befund, Teil 1 (beobachtet):** `git diff --name-only master..HEAD` liefert 25 Pfade in Anführungszeichen (die Baustellen-Skills, Nicht-ASCII im Ordnernamen). Keiner davon erscheint in der Ausgabe des Skripts, weder in der ersten noch in der zweiten Liste: `[ -f "$f" ]` scheitert am gequoteten Namen und `continue` verschluckt die Datei. Heute ist das folgenlos, weil diese Ordner ohnehin nicht geprüft werden; der Mechanismus trifft aber jeden Pfad mit Nicht-ASCII-Zeichen. Der Skill warnt in Schritt 4 selbst vor genau diesem Effekt, und `readme-audit.sh` behandelt ihn mit `-z` richtig. Dazu: `read -r` ohne `IFS=` beschneidet Randleerzeichen.

**Befund, Teil 2 (abgeleitet):** Als richtig gilt nur eine Datumszeile mit dem heutigen Datum. Sobald die Änderungen seit `<ref>` mehr als einen Tag umfassen, und `rules.md` empfiehlt als `<ref>` auch den Release-Zweig, meldet das Werkzeug jede korrekt datierte Datei als `NACHZIEHEN`. Das widerspricht der eigenen Regel „Das Datum gehört zur Datei". Außerdem sieht `"$REF"..HEAD` nur Committetes; `rules.md` sagt nicht, dass das Werkzeug erst nach dem Checkpoint-Commit aussagekräftig ist.

**Vorschlag:** `git diff --name-only -z "$REF"..HEAD | while IFS= read -r -d '' f`. Kriterium: Datumszeile nicht älter als der letzte Commit, der die Datei seit `<ref>` geändert hat (`git log -1 --format=%cs "$REF"..HEAD -- "$f"`), mit `TODAY` nur als Obergrenze. In `rules.md` sagen, ob das Werkzeug vor oder nach dem Checkpoint-Commit läuft.

### B7 — Etappe 5 widerspricht `skill-dev-doc.md`, Anhang A.2, bei der Behandlung wiederkehrender Meldungen

**Ort:** `rules.md`, Etappe 5, Tabelle, Zeile „Legitim repo-extern" („Wiederholt sich die Meldung bei jedem Durchgang, gehört der Name in die `EXTERN`-Menge des Prüfers"); `skill-dev-doc.md`, A.2, Absatz „Vier Fundarten meldet er, die keine Fehler sind" („Sie werden deshalb beim Ansehen des Ergebnisses aussortiert, nicht im Werkzeug") und die Vergleichstabelle vom 10. September 2026.

**Befund:** A.2 entscheidet ausdrücklich gegen eine gepflegte Ausnahmeliste im Werkzeug und liefert stattdessen eine Tabelle der geprüften, akzeptierten Meldungen, gegen die der nächste Durchgang vergleicht. `rules.md` weist an, den Namen in `EXTERN` aufzunehmen, und erwähnt die Vergleichstabelle nicht. Wer Etappe 5 fährt, urteilt neu statt zu vergleichen, und zwar gegen die Festlegung im Quelldokument des Werkzeugs.

**Vorschlag:** Den `EXTERN`-Satz streichen; stattdessen: „Meldungen gegen die Tabelle in A.2 halten; nur was dort nicht steht, ist neu zu beurteilen, und das Ergebnis wandert in diese Tabelle." Soll die Regel anders lauten, wird sie in A.2 geändert, nicht hier.

### B8 — Die Aussage zu `$TMPDIR` stimmt nicht mit dem Verhalten von `tempfile.mkdtemp` überein

**Ort:** `SKILL.md`, Schritt 2, letzter Satz („**Nicht `$TMPDIR` verwenden:** Die Variable existiert nur, solange die Sandbox läuft."); `files/branch-diff.py`, Docstring („relying on $TMPDIR would break outside the sandbox") und `Path(tempfile.mkdtemp(prefix="repo-cleanup-"))`.

**Befund (beobachtet):** `tempfile.gettempdir()` liefert unter der Sandbox `/tmp/claude-1000`, also den Wert von `$TMPDIR`. Ohne `--out` legt das Skript die Arbeitslisten genau dort ab, wo der Text sie nicht haben will. Der ausgegebene absolute Pfad bleibt nur so lange gültig, wie dieses Verzeichnis nicht weggeräumt wird; wird die Sandbox für Schritt 3 abgeschaltet (der „saubere" Weg aus Schritt 3), ist das nicht gesichert (abgeleitet). Der Docstring beschreibt die Absicht, das Skript setzt sie nicht um; der Satz in Schritt 2 ist in dieser Verkürzung falsch.

**Vorschlag:** Entweder `--out` in `SKILL.md` verbindlich auf einen festen, nicht versionierten Ort setzen, oder im Skript ohne `--out` ein Verzeichnis unabhängig von `$TMPDIR` wählen (`tempfile.mkdtemp(dir="/tmp")` oder ein Pfad unter dem Repo, den `.gitignore` deckt). Den Satz in Schritt 2 danach neu fassen.

### B9 — Es gibt keinen Ort für Stand, Begründungen, Messbefunde und Offenes; sie stehen im Skill-Körper

**Ort:** Der Ordner insgesamt (keine `README.md`); `SKILL.md`, Z. 26 („Am 11. September 2026 genau so passiert …"), Z. 84–86, Z. 88–91, Z. 109, Z. 111 („Beim ersten Lauf … 25 Fehlalarme"); `rules.md`, Z. 56–60, Z. 99 („gemessen am 11. September 2026"); die deutschen Laufzeitmeldungen aller fünf Skripte.

**Befund:** `skill-dev-doc.md`, Kapitel 5, verlangt je Skill eine `README.md` als Ort für Leistung, Feinheiten, Stand und Offenes und erlaubt der `SKILL.md`, für Begründungen dorthin zu verweisen, damit der Skilltext schlank bleibt. Die Projekt-`CLAUDE.md` sagt: „Wo es keinen Fahrplan gibt, benennt die README das Offene." Dieser Skill hat keine README. Folgen: Datierte Anekdoten und Messprotokolle stehen im Skill-Körper und in der Regeldatei und werden bei jedem Durchgang in den Kontext geladen, obwohl sie für die Ausführung nicht gebraucht werden (Kapitel 7: „Does this paragraph justify its token cost?"); der überholte Hinweis aus B4 hatte keinen anderen Platz als eine Regeldatei; und die deutschen Laufzeitmeldungen der Skripte haben keinen Vorgabenteil, der sie begründet, obwohl die Projekt-`CLAUDE.md` genau das verlangt („wo der Bereich das mit Begründung festgelegt hat"). `IMPORTANT.md` deckt nur den Verbleib im Entwicklungszweig ab.

**Vorschlag:** Eine `README.md` (deutsch, ohne Paket, ohne Installationskapitel, mit Datumszeile) mit: Zweck und Abgrenzung, Stand, Begründungen und Messbefunden (die Absätze aus den genannten Zeilen wandern dorthin, im Skilltext bleibt je Regel ein Halbsatz „warum"), Grenzen der Werkzeuge, Festlegung zur Sprache der Laufzeitmeldungen, Offenes. `SKILL.md` und `rules.md` verdichten sich auf Regeln und Kommandos. Abhängig von F1.

### B10 — Die Geltung der `skill-dev-doc.md` für Projekt-Skills unter `.claude/skills/` ist unbestimmt

**Ort:** `skill-dev-doc.md`, Einleitung („Bauanleitung für jeden Skill dieses Repositories — gleich in welchem Ordner er entsteht") gegen Kapitel 5 („Jeder Skill liegt unter `skills/<skill-name>/`", Pflichtfeld `license`, `downloads/`) und 5.3.

**Befund:** Die Doku beansprucht den Skill und verlangt zugleich Dinge, die für ein Werkzeug ohne Auslieferung gegenstandslos sind. Nach Arbeitsanweisungen §1.5 ist eine mehrdeutige Doku ein Defekt, der zu benennen ist. Dieses Review hat eine Auswahl der Kapitel angelegt (Abschnitt 2); ob sie stimmt, ist nicht aus der Doku ableitbar.

**Vorschlag:** Ein Absatz in `skill-dev-doc.md` (Einleitung oder Kapitel 5), der für Skills unter `.claude/skills/` festlegt, welche Kapitel gelten. Frage F1.

## 6 Befunde: niedrig und Kleinkram

Kleinkram wird nach Projekt-`CLAUDE.md` gesammelt und am Ende in einem Zug erledigt; jeder Punkt behält seine Nummer.

- **B11 — „Zwei Klassen" mit drei Einträgen.** `SKILL.md`, „Was im Release-Zweig fehlen soll", Satz „Zwei Klassen, und sie sind keine Nachlässigkeit:" vor drei Punkten. Beim Ergänzen der dritten Klasse nicht nachgezogen; ein Wort. Die anderen Zählstellen („alle DREI Klassen" in Schritt 4, „Three classes" in `branch-diff.py`) stimmen.
- **B12 — Ein Ausschluss verhindert nur den Übertrag, er räumt nichts weg.** `SKILL.md`, „Was im Release-Zweig fehlen soll". Der erste Lauf hatte den Skill nach `master` übertragen; die Kopien sind am 11. September von Hand entfernt worden (Commit 373b142, beobachtet). Weder `branch-diff.py` noch die erste Gegenprobe hätten sie je gemeldet, weil beide den Pfad ausfiltern. Ein Satz dazu im Text, damit beim nächsten Ergänzen einer Klasse das einmalige Entfernen aus `master` nicht vergessen wird.
- **B13 — Verweis auf einen anderen Skill.** `SKILL.md`, „Was in jedem Fall gilt", Punkt „… die Tabellenprüfung des Skills `correct-zaaack-md-editor-mistakes` laufen lassen." Kapitel 2.3 der Vorgaben verbietet Verweise auf andere Skills (Begründung: Installierbarkeit). Hier kommt hinzu, dass die globale `CLAUDE.md` dieselbe Pflicht vor Markdown-Commits schon trägt; der Satz ist eine Doppelung. Entscheidung: behalten, weil der Skill nur in diesem Repo gilt, oder streichen wegen der Doppelung.
- **B14 — Doppelung der Befundregeln.** `SKILL.md`, Z. 21–22, wiederholt fast wörtlich zwei Punkte aus Projekt-`CLAUDE.md`, „Befundlisten abarbeiten". Ein normatives Zuhause; hier genügt ein Querverweis. Der dritte Satz („Bevor etwas als Verstoß gemeldet wird, ist nachzusehen, ob es nicht ausdrücklich so festgelegt wurde") ist die eigentliche Ergänzung und kann bleiben.
- **B15 — Zweite Gegenprobe in Schritt 4 setzt den Pfad textuell in einen Shell-String.** `xargs … -I{} sh -c '… git show dev:"{}" …'`. Ein Anführungszeichen oder `$` im Pfad bricht die Probe; der Zweck der NUL-Trennung wird an dieser Stelle unterlaufen (abgeleitet). Robust: `xargs -0 -r -n1 -a "$LISTEN/take.z" sh -c 'a=$(git show dev:"$1" | sha256sum); b=$(git show master:"$1" | sha256sum); [ "$a" = "$b" ] || echo "ABWEICHUNG: $1"' _`.
- **B16 — `find-sandbox-masks.sh`: die Einrückung greift nie.** `path=${path#./}` schneidet `./` ab, danach kann `sed 's|^\./|  |'` nichts ersetzen; die Liste erscheint ohne Einrückung (beobachtet im heutigen Lauf). Kosmetik.
- **B17 — `repack-package-readme.sh`, drei Kleinigkeiten (abgeleitet).** `TOP` wird bei mehr als einem Ordner im Archiv mehrzeilig, geprüft wird nur auf leer; `find … | xargs sha256sum` ohne `-print0`/`-0`; und `rules.md` zählt die Zeitstempel zur Prüfung („Vergleicht man `unzip -l` vor und nach dem Packen …"), das Skript prüft aber nur Inhalte. Klarstellen, dass der Zeitstempel-Vergleich Handarbeit ist. Bei Fehlschlag ist das Paket bereits ersetzt; der Vorzustand liegt nur noch in Git.
- **B18 — `IMPORTANT.md` ist englisch.** Projekt-`CLAUDE.md`: Dateinamen englisch, Inhalte deutsch. Laut Commit „Hinweis des Entwicklers, korrekturgelesen" bewusst so. Zur Bestätigung (Frage F3); wenn gewollt, nichts zu tun.
- **B19 — Unbenannte Voraussetzungen des Datei-Abgleichs.** Schritt 3 setzt voraus: sauberer Arbeitsbaum, Haupt-Checkout auf `dev`, Arbeitsverzeichnis in der Repo-Wurzel (die Listen sind wurzelrelativ, `git checkout dev -- …` löst relativ zum Arbeitsverzeichnis auf), und `master` in keinem anderen Worktree ausgecheckt (sonst verweigert `git checkout master`). Heute alle erfüllt (beobachtet), keine steht im Text. Wird B1 nach Weg (b) gelöst, entfallen die letzten beiden.
- **B20 — Die Frage an den Nutzer nennt nicht alle Etappen.** `SKILL.md`, „Zuerst fragen, dann arbeiten": „READMEs, Sprachfassungen und Zip-Pakete"; die Tiefenprüfung umfasst auch Datumszeilen (Etappe 3) und den Verweisprüfer (Etappe 5), die `description` nennt die Datumszeilen. Frage vervollständigen.
- **B21 — Ladeanweisung ohne Pfadausdruck.** `SKILL.md`: „Lies `rules.md` im Ordner dieses Skills". Kapitel 5.2 sieht `${CLAUDE_SKILL_DIR}/rules.md` vor. Bei einem Projekt-Skill mit festem Pfad harmlos; zur Einheitlichkeit anpassen, falls die Vorgaben gelten (F1).

## 7 Fragen an den Entwickler

- **F1** Gilt `skill-dev-doc.md` für `.claude/skills/`, und wenn ja, welche Kapitel? Davon hängen B9, B10, B13, B21 und das fehlende `license`-Feld ab.
- **F2** Zu B1: Ausnahme vom Worktree-Modell im Skill festschreiben, oder den Skill auf Werkbank und Release-Worktree umbauen?
- **F3** Ist `IMPORTANT.md` bewusst englisch (B18)?

## 8 Geprüft und in Ordnung

Damit der nächste Review nachprüft statt neu herleitet:

- Frontmatter: `name` gleich Ordnername; `description` in der dritten Person, Hauptanwendungsfall vorn, ereignisförmig („wenn ein Vorhaben abgeschlossen ist und in den master soll …"), Geltungsgrenze am Ende; Länge weit unter der Kappung.
- Zweiteilung nach 5.2 umgesetzt und mit dem verlangten Begründungssatz („kostet nur Kontext") versehen; `rules.md` wird nur im Tiefenprüfungsfall geladen.
- `branch-diff.py`: läuft (beobachtet); `--no-renames` ist mit der Feldpaarung im Skript richtig begründet; `-z` macht `core.quotepath` entbehrlich; Ausschlussmuster in `DEFAULT_EXCLUDES`, Liste in `SKILL.md` und Filter der ersten Gegenprobe stimmen überein (drei Klassen); Infra-Muster aus der Modelldatei mit `(/|$)` korrekt; Richtung der Löschliste (Status `D` aus `git diff master dev` = in `master` vorhanden, in `dev` entfallen) stimmt; Arbeitslisten NUL-terminiert; `--out` funktioniert.
- Schritt 1: Gegenprobe `git diff --stat infra <zweig> -- <infra_files>` deckt auch Dateien ab, die `restore` nicht entfernt.
- Schritt 4: `core.quotepath=false` in der ersten Probe ist nötig und begründet (die 25 gequoteten Pfade sind beobachtet); die zweite Probe vergleicht Blobs, nicht den Arbeitsbaum.
- `readme-audit.sh`: läuft (beobachtet, 30 Zeilen, keine Befunde); `-z` und `LC_ALL=C sort -z` richtig; Partnerbestimmung deckt die Umkehrung in der Wurzel ab; Baustellen-Skills werden am ersten Zeichen erkannt, wie in `branch-diff.py`.
- `datelines-since.sh`: Das Muster `^\*(Stand|Last updated): …\*` trifft READMEs und Snippet-Dateien gleichermaßen (Stichproben: `skills/README.md`, `skills/common-code-generation/CLAUDE-snippet.de.md`, `CLAUDE.md-Snippets/common-snippets.de.md`).
- `repack-package-readme.sh`: Sprachzuordnung `_de_` → `README.md`, `_en_` → `README.en.md` entspricht der README-Regel unterhalb der Wurzel; `cp -p` und `zip -9 -o -X` mit sortierter Liste entsprechen 5.3 und A.1; Rückgabewert 1 bei Abweichung.
- `find-sandbox-masks.sh`: läuft (beobachtet, 19 Attrappen, deckungsgleich mit `git status`); `test -c`/`test -b` je Pfad statt `find -type c` ist richtig begründet; leeres Array unter `set -u` korrekt behandelt.
- `rules.md`, Etappe 1: Reifezeichen-Liste stimmt mit der Legende beider Wurzel-READMEs überein; alle Bereichsverweise der englischen Wurzel-README zeigen auf `README.en.md`; alle sechs Bereichsordner der Wurzel stehen in der Tabelle, kein Ordner fehlt (beobachtet).
- `rules.md`, Etappe 4: `home-.claude-sharing/scripts/pack_packages.sh` existiert und hält laut Kopfkommentar seine Quellen in `files/`, wie behauptet.
- Ausführungsbits aller fünf Skripte gesetzt; Quelltext, Kommentare und Docstrings englisch; Markdown-Dateien ein Absatz je Zeile; keine Tabellen-Artefakte im Ordner (beobachtet).

## 9 Nicht geprüft

Der Datei-Abgleich selbst und `repack-package-readme.sh` wurden nicht ausgeführt. Ob Git beim Branchwechsel unter der Sandbox tatsächlich abbricht (B2), ist aus Mount-Lage und Zustand von `master` abgeleitet, nicht vorgeführt.
