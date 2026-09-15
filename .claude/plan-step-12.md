# Plan zu Fahrplanschritt 12: Zweigmodell und Werkbank trennen

*Fixiert am 2026-09-15 auf Grundlage der Besprechung mit dem Entwickler. Dieser Plan gilt als beschlossen; Abweichungen bei der Ausführung werden vorgelegt, nicht stillschweigend eingebaut (Arbeitsanweisungen §1.4). Die Datei ist vorübergehend und wird gelöscht, sobald Schritt 12 erledigt ist — eine vom Entwickler freigegebene Ausnahme von der Regel „keine eigenen Plan-Dateien" der Projekt-CLAUDE.md, weil der Plan für den Fahrplan zu lang ist und über mehrere Sitzungen trägt.*

## 1 Ausgangslage

Der Skill `parallel-sessions` und seine Konfigurationsdatei `.claude/git-worktree-model.json` vermischen drei Dinge, die nur historisch zusammengehören:

1. **Die Führung eines Git-Projekts** — Entwicklungszweig, Release-Zweig, Themenzweige, und ein orphaner Zweig für Dateien, die auf jedem Zweig gleich sein müssen (bisher `infra`). Das ist eine Art, ein Repository zu führen, unabhängig davon, ob je ein Agent darin arbeitet.
2. **Die Commit-Körnung einer Claude-Sitzung** — Absicherungs-Commits auf einer Werkbank, am Ende ein Squash in Menschenkörnung. Das ist die eigentliche Herkunft der Werkbank; Parallelität war nie ihr Hauptzweck.
3. **Echte Parallelarbeit mehrerer Sitzungen** — je Sitzung ein Worktree unter `.claude/worktrees/`. Das ist keine dritte Sache, sondern Punkt 2 mit Isolation.

Folgen der Vermischung: Wer Worktrees abschalten will, indem er die Datei löscht, verliert die Verwaltungsdisziplin mit. Der Abgleich der zentralen Dateien hängt als einziger Auslöser am Worktree-Skill. Und der Abgleich selbst kennt keine Richtung — am 7. September 2026 wurde er dadurch zur Rücksetzungsfalle (Drift zwischen `dev` und `infra`, behoben mit `14f9190`).

Was dieses Repository tatsächlich tut, stand nirgends festgeschrieben: `master` wird nie gemergt, sondern Datei für Datei fortgeschrieben (`repo-cleanup-pass`), weil bei mehreren Produkten Teilübernahmen und echte Merges einander ausschließen. „Jeder Commit bleibt erhalten" gilt innerhalb von `dev`, nicht über die Grenze zu `master`.

## 2 Beschlossene Entscheidungen

| Nr. | Frage | Entscheidung |
| --- | --- | --- |
| 1 | Name Skill A | `git-branch-model` |
| 2 | Name Skill B | `git-workbench` — `parallel-sessions` wird umbenannt, weil der alte Name nur noch eine von drei Betriebsarten beschreibt |
| 3 | Name des Verwaltungszweigs in diesem Repo | `repo-management` (statt `infra`; „infra" ist in der IT für Deployment belegt). Rollenname in der Prosa: Verwaltungszweig |
| 4 | Betriebsarten von B | `direct` / `workbench` / `worktree` / `ask`; Standard ohne Konfigurationsdatei ist `ask`. `direct` ist eine gültige Variante, die die Instanz nicht immer wieder in Frage stellt |
| 5 | Sind die beiden Konfigurationsdateien Verwaltungsdateien? | Ja — sie müssen auf jedem Zweig gleich sein, und `repo-cleanup-pass` liest sie |
| 6 | Sprachfassungen für A | Deutsch zuerst, Englisch danach; B behält beide |
| 7 | Globale `~/.claude/CLAUDE.md`: §1.7 durch B ablösen? | Ja. §1.7, der `arbeitsdaten.json`-Absatz in §1.2 und der Verweis in §1.6 entfallen aus „NOCH EINZUORDNEN"; B ist ihre Einordnung. Der Entwickler prüft vorher, ob andere Projekte noch nach §1.7 arbeiten, und passt dort gegebenenfalls die Projekt-CLAUDE.md an |
| 8 | Namensgleichheit Datei ↔ Skill (`.claude/git-branch-model.json`) | Bleibt so. B nennt eine Projektdatei, keinen Skill; Kap. 2.3 der Vorgaben ist gewahrt |
| 9 | Zustandsdatei | Keine, weder für A noch für B. Den Zustand tragen `git worktree list` und die Zweigliste |
| 10 | `pre-commit`-Hook über `core.hooksPath` | Nicht Teil dieses Schritts; bleibt als benannte Härtungsoption in der README von A |
| 11 | `.claude/skills/repo-cleanup-pass` | Bleibt auf `dev`. Nicht weil Werkzeuge nicht auf den Verwaltungszweig dürften, sondern weil dieses eine nur auf `dev` gehört — die Verteilung legte es sonst auch auf `master` |

## 3 Gemeinsame Gestaltungsregeln für beide Skills

- **Zwei Skills, die einander nicht kennen.** Keiner nennt den anderen (Vorgaben Kap. 2.3). Gekoppelt sind sie ausschließlich über eine Projektdatei: B liest aus `.claude/git-branch-model.json` genau einen Wert, wenn die Datei da ist.
- **Dünne `SKILL.md`, nachgeladene Regeldateien** nach Kap. 5.2. Die `SKILL.md` klärt nur die Lage und lädt, was gilt.
- **Aufklärung beim Wirksamwerden.** Der Entwickler installiert die Skills und sieht, was passiert — davon ist auszugehen. Wird ein Skill in einem Projekt erstmals wirksam (Ersteinrichtung, erste Rückfrage in `ask`), erklärt er in wenigen Sätzen, was er tut und was er gleich tun wird, und nennt die README im Skill-Ordner als Nachschlagewerk. Bei Nachfragen zitiert er aus ihr; die README reist im Paket mit, ihr Dateiname wird nicht vorausgesetzt (Kap. 5). Die Regeldateien wiederholen deshalb keine Begründungen — sie wissen nur, wo die Doku liegt.
- **Anker beider Trigger ist das erste schreibende Git-Kommando der Sitzung** (`commit`, `add`, `push`, `checkout`, `restore`, `reset`, `merge`), nicht „Sitzungsbeginn" — den erkennt die Instanz nicht zuverlässig. Zwei Trigger am selben Anker sind zulässig (Kap. 2.3).
- **Ein Wort je Begriff** (Kap. 7): „Zweig" statt wechselnd „Branch"/„Zweig"; „Nutzer" für den Menschen im Chat.
- **Zielwelt beider Skills: nur Claude Code** (Kap. 9; Git gibt es auf claude.ai nicht). Pakete: `_de_local`, `_en_local`.
- **Dateinamen englisch, Prosa deutsch bzw. englisch je Fassung.** Marken im Text folgen der Rolle: aus `INFRA-EXPERIMENT` wird `MANAGEMENT-EXPERIMENT`.

## 4 Skill A — `git-branch-model`

**Zweck.** Regelt, wie ein Git-Projekt geführt wird. Gilt in jedem Projekt mit Zweigmodell, auch wenn nie eine Werkbank entsteht.

**Vier Rollen**, konkrete Namen in der Konfigurationsdatei:

| Rolle | Beispiel | Was dort geschieht |
| --- | --- | --- |
| Entwicklungszweig | `dev` | Hauptlinie der Entwicklung; jeder Commit bleibt erhalten |
| Release-Zweig | `master` | Der veröffentlichte Stand; kein Arbeitsort |
| Themenzweige | frei benannt, je Aufgabe | Vom Entwicklungszweig abgezweigt, per Merge zurückgeführt; Historie bleibt |
| Verwaltungszweig | `repo-management` | Orphan; trägt nur Dateien, die auf jedem Zweig gleich sein müssen; wird nie gemergt, sondern per `git restore --source` übergelegt |

**Die Regel, die Themenzweig und Werkbank unterscheidet**, spricht A aus: Commits, die ein Mensch gesetzt hat, behalten ihre Körnung (Merge). Absicherungs-Commits einer Maschine werden auf Menschenkörnung gebracht (Squash) — das Verfahren dafür ist Sache von B, A benennt nur die Grenze.

**Release-Übernahme in zwei Betriebsarten**, Feld `release_transfer`:

- `merge` — Ein-Produkt-Projekt: der Entwicklungszweig wird zu einem sinnvollen Zeitpunkt in den Release-Zweig gemergt, Historie bleibt.
- `file-sync` — Mehr-Produkt-Projekt: getrennte Historien, Übertrag Datei für Datei, der Release-Zweig wird nie ausgecheckt. A nennt die Invarianten (kein Merge, kein Checkout nötig, Verwaltungsdateien kommen vom Verwaltungszweig, Übertrag auf Objektebene möglich); das ausgearbeitete Rezept bleibt Sache des Projekts — hier `repo-cleanup-pass`.

**Der Verwaltungszweig — was darauf darf:** alles, was auf jedem Zweig identisch sein muss. Konfiguration (Projekt-CLAUDE.md, Editor, Linter, `.gitignore`) ebenso wie Werkzeug mit eigener Logik (zweigunabhängiger Projekt-Skill, CI). Kriterium ist „muss überall gleich sein", nicht „ist Konfiguration". Ein Werkzeug, das nur auf den Entwicklungszweig gehört, fällt heraus, weil die Verteilung es auch auf den Release-Zweig legte.

**Ändern von Verwaltungsdateien.** Dauerhafte Änderung nur auf dem Verwaltungszweig. Kleine Änderung direkt dort, jeweils mit Freigabe. Größere oder iterative Arbeit — ein Skill, ein Hook — auf einer **Werkbank vom Verwaltungszweig**, per Squash zurück in ihn. Das verletzt die Invariante nicht: „wird von keinem Zweig abgeleitet, nie gemergt" meint den Verkehr mit Entwicklungs- und Release-Zweig; die Historie des Verwaltungszweigs enthält weiterhin nur Verwaltungsdateien. Die Experimentregel (markierter Block auf einer Werkbank, endet durch den Abgleich, nie gemergt) wandert von B nach A.

**Der Abgleich mit Richtungsprüfung** — der Kern der Korrektur. Beim ersten schreibenden Git-Kommando prüft A, ob Verwaltungsdateien im Arbeitsbaum vom Verwaltungszweig abweichen. Weichen sie ab, wird die **Richtung** bestimmt: Ist die lokale Fassung ein früherer Stand des Verwaltungszweigs (ihr Blob kommt in dessen Historie für diese Datei vor), ist sie **veraltet** — überschreiben und melden. Kommt ihr Blob dort nicht vor, enthält sie **Neues** — anhalten, melden, nicht überschreiben; der richtige Weg ist dann, die Änderung auf den Verwaltungszweig zu bringen. Damit wird aus „Abgleich bei Sitzungsbeginn, automatisch" ein „bei Bedarf, richtungsabhängig". Das ist das Sicherungsnetz, das beim Herauslösen aus B sonst verlorenginge.

**Ersteinrichtung** (nur auf Wunsch, als Plan): Namen klären, Entwicklungszweig anlegen falls nötig, Verwaltungszweig als Orphan anlegen (`git worktree add --orphan`, Git ≥ 2.42) und die Verwaltungsdateien übernehmen, Konfigurationsdatei schreiben und selbst in die Liste aufnehmen, Trigger in der CLAUDE.md des Zielorts prüfen.

**Konfigurationsdatei `.claude/git-branch-model.json`**, Felder: `integration_branch`, `release_branch`, `release_transfer` (`merge` | `file-sync`), `management_branch`, `management_files` (Liste; enthält auch die beiden Konfigurationsdateien). Die ersten beiden Schlüssel behalten ihren heutigen Namen — `repo-cleanup-pass` liest sie schon; nur `infra_*` wird zu `management_*`.

**Freigabestufen:** Abgleich in Richtung „veraltet" automatisch mit Meldung; Abgleich in Richtung „Neues" nur nach Rückfrage; jeder Commit auf dem Verwaltungszweig, jede Release-Übernahme, jedes Löschen von Zweigen jedes Mal; Ersteinrichtung und Änderungen an der Verwaltungsdateiliste einmal je Projekt.

**Trigger.** Anker: erstes schreibendes Git-Kommando, wenn `.claude/git-branch-model.json` existiert. Ereignisse: der Nutzer spricht von Release, vom Zusammenführen oder Anlegen eines Zweigs, vom Ändern einer zentralen Datei. Ohne Konfigurationsdatei bietet A die Ersteinrichtung nur auf ein solches Ereignis hin an, kurz und ohne Drängen.

**Dateien in `skills/git-branch-model/`:** `SKILL.de.md` (dünn: liegt die Datei vor oder liegt ein Ereignis an? dann `rules.de.md` laden), `rules.de.md` (Rollen, Übernahme, Verwaltungszweig, Abgleich, Ersteinrichtung, Freigabestufen, Invarianten), `README.md` (nach Kap. 6.1; die Begründungen, die heute in der README von `parallel-sessions` zum Infra-Zweig stehen, wandern hierher; dazu die Härtungsoption Hook), `CLAUDE-snippet.de.md`; englische Fassungen nach Teil I.

## 5 Skill B — `git-workbench`

**Zweck.** Regelt, wie eine Claude-Sitzung in einem Git-Repository committet — in welcher Körnung und wie isoliert. Gilt in jeder Sitzung, die committet, auch ohne Zweigmodell.

**Vier Werte für `mode`:**

| `mode` | Verhalten | Voraussetzung |
| --- | --- | --- |
| `direct` | Commits direkt auf dem Zweig, auf dem die Sitzung steht; jeder freigegebene Schritt ein dauerhafter Commit | Niemand arbeitet parallel im selben Arbeitsbaum |
| `workbench` | Werkbank `<prefix><topic>` vom aktuellen Zweig, Checkpoint-Commits ohne Nachfrage, am Ende Squash zurück | Einzelne Sitzung; Zwischenschritte sollen nicht in die Historie |
| `worktree` | Wie `workbench`, aber in eigenem Worktree unter `worktree_dir` | Mehrere Sitzungen gleichzeitig |
| `ask` | Beim ersten schreibenden Git-Kommando: aktuellen Zweig nennen, Lage nennen (steht die Sitzung in einem Worktree? ist eine zweite Sitzung erwähnt?), eine Betriebsart vorschlagen, fragen. Die Antwort gilt für die Sitzung | Standard ohne Konfigurationsdatei |

**Kernregeln in jeder Betriebsart:** nie auf dem Release-Zweig committen; `push` nur mit Zustimmung im Einzelfall; die Push-Regel unten; der Squash-Commit ohne `-a`. Die alte Sofortregel „Schreibhoheit klären" bleibt als Rückfall für den Fall zweite Sitzung ohne Worktree.

**Was B von A braucht — genau einen Wert:** den Entwicklungszweig, damit klar ist, wovon die Werkbank abzweigt und wohin der Squash geht. Liegt `.claude/git-branch-model.json` vor, liest B `integration_branch` dort. Sonst fragt B einmal je Sitzung, mit dem aktuell ausgecheckten Zweig als Vorschlag — nicht als Annahme. B speichert den Wert nie selbst.

**Die Push-Regel, verallgemeinert.** Vor jedem Push, den der Nutzer verlangt oder die Sitzung vorschlägt, prüft B alle lokalen Zweige auf unveröffentlichte Commits und fragt je Fund: „Auf `<zweig>` liegen n unveröffentlichte Commits — mitpushen?", Ja als Vorschlag. Hängt nicht mehr am Begriff „offene Werkbank" und erfasst Entwicklungs- und Verwaltungszweig gleichermaßen. Das ist der beobachtbare Moment für Rechnerwechsel oder Sitzungsende.

**Squash-Abschluss** (aus den heutigen Regeln, ohne die Infra-Schritte): Stand des Zielzweigs holen und Konflikte auf der Werkbank lösen; Squash vorschlagen, Commit-Text vom Nutzer; in `worktree`-Betriebsart vorher `ExitWorktree`, Ausführung ausdrücklich im Haupt-Checkout adressiert; danach Werkbank und Worktree nach Zustimmung entfernen.

**Ersteinrichtung** (nur auf Wunsch): Betriebsart, Präfix und Ablageort klären — als Ablageort ohne anderslautende Vorgabe `.claude/worktrees/` im Repository; der Eintrag in `.gitignore` ist nötig, und wie er committet wird, folgt den Zweigregeln des Projekts —, Konfigurationsdatei schreiben, Trigger prüfen.

**Konfigurationsdatei `.claude/git-workbench.json`**, Felder: `mode`, `workbench_prefix`, `worktree_dir`.

**Freigabestufen:** Checkpoint-Commits automatisch; Anlegen der Werkbank einmal je Sitzung; Squash, Push, Löschen von Zweigen und Worktrees, jede Handlung an fremden Worktrees oder am Haupt-Checkout jedes Mal; Ersteinrichtung einmal je Projekt.

**Trigger.** Anker: erstes schreibendes Git-Kommando, unbedingt — erst dann entscheidet B, ob es etwas zu tun gibt. Ereignisse wie heute: zweiter Chat oder zweite Instanz erwähnt, fremde Änderungen im Arbeitsbaum, Sitzung beginnt in einem Worktree.

**Dateien in `skills/git-workbench/`** (Ordner per `git mv` aus `skills/parallel-sessions/`): `SKILL.de.md` (dünn: Betriebsart bestimmen — Datei lesen oder fragen —, `rules.de.md` laden, in `worktree` zusätzlich `rules-worktree.de.md`), `rules.de.md` (Werkbank, Checkpoints, Squash-Abschluss, Push-Regel, Sofortregel, Freigabestufen, Ersteinrichtung, Invarianten), `rules-worktree.de.md` (alles Worktree-Spezifische aus den heutigen Regeln: Anlegen, verwaiste Werkbänke, Arbeiten im Worktree oder über absolute Pfade, `EnterWorktree`/`ExitWorktree`, Rechnerwechsel, der markierte Abschnitt zur Sandbox-Kollision Issue #80278), `README.md` (nach Kap. 6.1; die Begründungen zu Worktrees, Ablageort, Aufräumen bleiben hier, die zum Infra-Zweig gehen nach A), `CLAUDE-snippet.de.md`; englische Fassungen. Die alten Pakete in `downloads/` werden ersetzt.

## 6 Teil I — Produkt: Claude arbeitet hintereinander weg

**Stand: Teil I ist am 15. September 2026 vollständig ausgeführt** (Commits `956a20c` bis zum Paket-Commit auf `dev`; der empfohlene Halt entfiel auf Anweisung des Entwicklers, die Texte sind noch nicht von ihm gelesen). Teil II beginnt mit II.1.

Alles auf `dev`, Betriebsart `direct`, je Schritt ein Checkpoint-Commit. Vor jedem Commit mit Markdown die Tabellenprüfung; am Ende jeder Sitzung der Aktualitätsprüfer für Pakete (Vorgaben Anhang A.3).

| Schritt | Inhalt |
| --- | --- |
| I.1 | `skills/git-branch-model/` anlegen: `SKILL.de.md`, `rules.de.md`, `README.md`, `CLAUDE-snippet.de.md` |
| I.2 | `git mv skills/parallel-sessions skills/git-workbench`; `SKILL.de.md`, `rules.de.md`, `rules-worktree.de.md`, `README.md`, `CLAUDE-snippet.de.md` neu fassen; alte Pakete entfernen |
| I.3 | `skill-dev-doc.md`: in 5.1 den Dateinamen `git-worktree-model.json` → `git-branch-model.json`; in 5.2 einen klärenden Satz, der „ein Anliegen in zwei Dateien" von „zwei Anliegen mit je eigener Geltung, gekoppelt höchstens über eine Projektdatei" unterscheidet; in 9.4 die Zeile `parallel-sessions` durch zwei Zeilen ersetzen (beide „nur code"); in der A.2-Tabelle die Zeile zu `rules.de.md`/`rules.en.md` nachziehen |
| I.4 | `skills/README.md` und `README.en.md`: Übersichtstabelle — Zeile B umbenannt und neu beschrieben, Zeile A neu |
| — | **Empfohlener Halt:** Der Entwickler liest die deutschen Skilltexte (Kap. 4.1 erlaubt die Inhaltsprüfung ohne Installation). Gibt er frei oder sagt er „weiter", folgt der Rest ohne Rückfrage; sonst werden Korrekturen vor der Übersetzung eingearbeitet |
| I.5 | Englische Fassungen für A und B: `SKILL.en.md`, `rules.en.md`, `rules-worktree.en.md`, `README.en.md`, `CLAUDE-snippet.en.md`; Querverweise nach Kap. 5.1 (`blob/master`) |
| I.6 | Pakete bauen (Anhang A.1): `git-branch-model_de_local.zip`, `_en_local.zip`, `git-workbench_de_local.zip`, `_en_local.zip`; Verweisprüfer A.2 und Aktualitätsprüfer A.3 laufen lassen und die Meldungen gegen die A.2-Tabelle abgleichen |
| I.7 | Datumszeilen aller berührten READMEs und Snippets nachziehen |

## 7 Teil II — Projektumstellung: schrittweise mit dem Entwickler

Jeder Schritt wird vorgelegt und einzeln freigegeben; Commits auf dem Verwaltungszweig und alles außerhalb des Repositories brauchen die Freigabe ausdrücklich.

| Schritt | Inhalt |
| --- | --- |
| II.1 | Zweig `infra` → `repo-management`: lokal umbenennen, mit `-u` pushen, alten Remote-Zweig löschen. Handzettel für die anderen Rechner: `git fetch --prune`, lokalen Zweig umbenennen, Upstream setzen |
| II.2 | Konfigurationsdateien aufteilen: `.claude/git-branch-model.json` und `.claude/git-workbench.json` auf dem Verwaltungszweig anlegen, beide in `management_files` aufnehmen, committen; per `restore` nach `dev` holen; `.claude/git-worktree-model.json` auf `dev` löschen; Commit auf `dev` |
| II.3 | Projekt-`CLAUDE.md` auf dem Verwaltungszweig: Abschnitt „Arbeitsmodell: Git-Worktrees" durch einen Abschnitt ersetzen, der beide Skills und beide Dateien nennt und die Betriebsart dieses Repos festhält; im Abschnitt „Projekt-Skills gehören dem Entwicklungszweig" `infra` → `repo-management` und „ausschließlich die fünf zentralen Dateien" → „nur die Verwaltungsdateien laut Liste"; committen, nach `dev` holen |
| II.4 | `repo-cleanup-pass` nachziehen: `SKILL.md` (Dateiname, Schlüssel, Zweigname, Wortwahl an den zehn Stellen), `files/branch-diff.py` (Dateiname, `infra_files` → `management_files`, Ausgabetext), `IMPORTANT.md` (Zweigname); Commit auf `dev` |
| II.5 | Installation: `~/.claude/skills/parallel-sessions/` entfernen, `git-branch-model/` und `git-workbench/` aus den Paketen einspielen — außerhalb des Repos, daher Freigabe. Über `home-.claude-sharing` wandert das vermutlich auf die anderen Rechner mit; nicht geprüft |
| II.6 | Globale `~/.claude/CLAUDE.md`: Trigger-Absatz „Parallele Sitzungen und Worktree-Arbeitsmodell" durch die zwei Trigger-Absätze aus den Snippets ersetzen; aus „NOCH EINZUORDNEN" entfallen §1.7 vollständig, der `arbeitsdaten.json`-Absatz in §1.2 und der Verweis auf §1.7 in §1.6. Textvorschlag von Claude; Änderung durch den Entwickler oder nach Freigabe. Vorher prüft der Entwickler andere Projekte, die noch nach §1.7 arbeiten |
| II.7 | Memory `parallel-sessions-trigger-messung.md` auf die neuen Namen umschreiben; die Messung bleibt offen und gilt nun für zwei Skills |
| II.8 | Optional: Trigger-Messung nach Kap. 4.2 für beide Skills, Befund in die READMEs |
| II.9 | Schritt 12 aus `work-plan.md` entfernen; diese Plandatei löschen |
| II.10 | Abgleich nach `master` per `repo-cleanup-pass` — auf Zuruf des Entwicklers |

**Zwischen II.2 und II.5 ist kurz kein Skill wirksam:** Der installierte alte findet seine Datei nicht mehr, die neuen sind noch nicht eingespielt. In Betriebsart `direct` mit wartendem Entwickler ist das unschädlich.

## 8 Nicht betroffen

`CLAUDE.md-Snippets/` (grenzt Skill-Trigger ausdrücklich aus), `home-.claude-sharing/`, die Wurzel-READMEs (nennen den Skill nicht), `.gitignore` (der Eintrag `/.claude/worktrees/` bleibt richtig: Worktrees sind Arbeitskopien des Repositories, keine Projektdateien).
