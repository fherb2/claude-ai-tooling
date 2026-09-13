# Code-Review: `.claude/skills/repo-cleanup-pass`

*Erstellt: 2026-09-11*

Reviewer: Claude (Fable 5.1), im Auftrag des Entwicklers. Gegenstand sind die acht Dateien des Skill-Ordners (per `ls` bestätigt, weitere gibt es nicht): `SKILL.md`, `rules.md`, `IMPORTANT.md`, `files/branch-diff.py`, `files/find-sandbox-masks.sh`, `files/readme-audit.sh`, `files/datelines-since.sh`, `files/repack-package-readme.sh`. Diese Datei ist die Befunddatei des Reviewers. **Für diesen Skill wird kein Review-Anhang und keine eigene Doku angelegt** (Festlegung des Entwicklers vom 13. September 2026): Er ist Hilfsmittel für die Entwicklung dieses Repositories, kein Produkt. Abgearbeitete Befunde werden hier ersatzlos gestrichen; ist die Datei leer, wird sie gelöscht.

## 1 Umfang und Grenzen des Reviews

Das Review war auf Lesezugriffe beschränkt; Bash-Kommandos liefen nur nach Einzelfreigabe des Entwicklers und ausschließlich lesend. Ausgeführt wurden: `ls` auf Skill-Ordner, Projektwurzel und `.claude/`; `git ls-tree`, `git worktree list`, `git branch -a`, `git status`, `git log` und `git show master:README*.md`; `git ls-files '*README*.md'` und zwei `grep`-Läufe; die drei ausgabe-only-Werkzeuge des Skills (`readme-audit.sh`, `datelines-since.sh master`, `find-sandbox-masks.sh`); `branch-diff.py --from dev --to master` mit Ablage im Scratchpad; die Tabellenprüfung des Skills `correct-zaaack-md-editor-mistakes` als reiner Befundlauf (Ergebnis: keine Artefakte, keine unlesbaren Dateien); dazu `/proc/self/mounts`, `test -w` und `tempfile.gettempdir()` zur Klärung der Sandbox-Lage.

Nicht ausgeführt: der Datei-Abgleich selbst (Schritt 1, 3, 4, 5), `repack-package-readme.sh`, und jeder schreibende Git-Befehl. Aussagen darüber, wie sich Git unter der Sandbox beim Branchwechsel verhält, bleiben deshalb aus Mount-Lage und Git-Zustand **abgeleitet**; das steht dann am Befund.

Vollständig gelesen wurden neben dem Skill-Ordner: die Projekt-`CLAUDE.md`, `skill-dev-doc.md` (alle Kapitel und Anhang A), `.claude/git-worktree-model.json`, beide Wurzel-READMEs, `work-plan.md`, `.claude/settings.json`, `skills/parallel-sessions/SKILL.de.md` und `rules.de.md`. Stichproben: Kopfzeilen von `skills/temp-debug-code/README.md`, `skills/README.md`, `skills/common-code-generation/CLAUDE-snippet.de.md`, `CLAUDE.md-Snippets/README.md` und `common-snippets.de.md`, Kopfkommentar von `home-.claude-sharing/scripts/pack_packages.sh`.

## 2 Maßstab

Angelegt wurden: die Projekt-`CLAUDE.md` (Worktree-Modell, Projekt-Skills im Entwicklungszweig, Datumszeilen, ein normatives Zuhause je Aussage, Plan- und Review-Regeln), die Regeln des Worktree-Modells aus `skills/parallel-sessions/rules.de.md` (weil die Projekt-`CLAUDE.md` sie für dieses Repo verbindlich erklärt), und `skill-dev-doc.md` als Bauanleitung „für jeden Skill dieses Repositories — gleich in welchem Ordner er entsteht".

**Zur Geltung der `skill-dev-doc.md` — Festlegung des Entwicklers vom 13. September 2026:** Sie gilt für diesen Skill **nicht**. Er ist Hilfsmittel für die Entwicklung dieses Repositories, kein Produkt und kein Gegenstand der Skill-Entwicklung; die Bauvorschriften für ausgelieferte Skills (README-Pflicht, Download-Paket, Lizenzfeld, Trigger-Form, Pfadausdrücke, Verbot von Verweisen auf andere Skills) binden ihn nicht.

**Davon unberührt** bleibt `skill-dev-doc.md` als **normatives Zuhause** repo-weiter Festlegungen und der Werkzeuge, die dieser Skill benutzt: Kapitel 5.1 (Form der Sprachverweise) und Anhang A (Prüfwerkzeuge) gelten weiter — nicht weil sie den Skill *bauen*, sondern weil er sie *anwendet* und prüft. Befunde, die am ersten Maßstab gemessen wurden, sind hinfällig; die am zweiten gemessenen bleiben.

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

## 5 Befunde: mittel

**Vorschlag:** `git diff --name-only -z "$REF"..HEAD | while IFS= read -r -d '' f`. Kriterium: Datumszeile nicht älter als der letzte Commit, der die Datei seit `<ref>` geändert hat (`git log -1 --format=%cs "$REF"..HEAD -- "$f"`), mit `TODAY` nur als Obergrenze. In `rules.md` sagen, ob das Werkzeug vor oder nach dem Checkpoint-Commit läuft.

## 6 Befunde: niedrig und Kleinkram

Kleinkram wird nach Projekt-`CLAUDE.md` gesammelt und am Ende in einem Zug erledigt; jeder Punkt behält seine Nummer.

- **B20 — Die Frage an den Nutzer nennt nicht alle Etappen.** `SKILL.md`, „Zuerst fragen, dann arbeiten": „READMEs, Sprachfassungen und Zip-Pakete"; die Tiefenprüfung umfasst auch Datumszeilen (Etappe 3) und den Verweisprüfer (Etappe 5), die `description` nennt die Datumszeilen. Frage vervollständigen.

## 8 Geprüft und in Ordnung

Damit der nächste Review nachprüft statt neu herleitet:

- Frontmatter: `name` gleich Ordnername; `description` in der dritten Person, Hauptanwendungsfall vorn, ereignisförmig („wenn ein Vorhaben abgeschlossen ist und in den master soll …"), Geltungsgrenze am Ende; Länge weit unter der Kappung.
- Zweiteilung nach 5.2 umgesetzt und mit dem verlangten Begründungssatz („kostet nur Kontext") versehen; `rules.md` wird nur im Tiefenprüfungsfall geladen.
- `branch-diff.py`: läuft (beobachtet); `--no-renames` ist mit der Feldpaarung im Skript richtig begründet; `-z` macht `core.quotepath` entbehrlich; Ausschlussmuster in `DEFAULT_EXCLUDES`, Liste in `SKILL.md` und Filter der ersten Gegenprobe stimmen überein (drei Klassen); Infra-Muster aus der Modelldatei mit `(/|$)` korrekt; Richtung der Löschliste (Status `D` aus `git diff master dev` = in `master` vorhanden, in `dev` entfallen) stimmt; Arbeitslisten NUL-terminiert; `--out` funktioniert.
- Schritt 1: Gegenprobe `git diff --stat infra <zweig> -- <infra_files>` deckt auch Dateien ab, die `restore` nicht entfernt.
- Schritt 4: `core.quotepath=false` in der ersten Probe ist nötig und begründet (die 25 gequoteten Pfade sind beobachtet); die zweite Probe vergleicht Blobs, nicht den Arbeitsbaum.
- `readme-audit.py` (bis 13. September 2026 `readme-audit.sh`): läuft (beobachtet, 30 Zeilen für 30 versionierte READMEs, mechanisch gegengezählt, keine Befunde); NUL-sichere Pfadbehandlung und C-Sortierung beim Umbau erhalten; Partnerbestimmung deckt die Umkehrung in der Wurzel ab; Baustellen-Skills werden am ersten Zeichen erkannt, wie in `branch-diff.py`.
- `datelines-since.py` (bis 13. September 2026 `.sh`): Das Muster `^\*(Stand|Last updated): …\*` trifft READMEs und Snippet-Dateien gleichermaßen (Stichproben: `skills/README.md`, `skills/common-code-generation/CLAUDE-snippet.de.md`, `CLAUDE.md-Snippets/common-snippets.de.md`).
- `repack-package-readme.sh`: Sprachzuordnung `_de_` → `README.md`, `_en_` → `README.en.md` entspricht der README-Regel unterhalb der Wurzel; `cp -p` und `zip -9 -o -X` mit sortierter Liste entsprechen 5.3 und A.1; Rückgabewert 1 bei Abweichung.
- `find-sandbox-masks.sh`: läuft (beobachtet, 19 Attrappen, deckungsgleich mit `git status`); `test -c`/`test -b` je Pfad statt `find -type c` ist richtig begründet; leeres Array unter `set -u` korrekt behandelt.
- `rules.md`, Etappe 1: Reifezeichen-Liste stimmt mit der Legende beider Wurzel-READMEs überein; alle Bereichsverweise der englischen Wurzel-README zeigen auf `README.en.md`; alle sechs Bereichsordner der Wurzel stehen in der Tabelle, kein Ordner fehlt (beobachtet).
- `rules.md`, Etappe 4: `home-.claude-sharing/scripts/pack_packages.sh` existiert und hält laut Kopfkommentar seine Quellen in `files/`, wie behauptet.
- Ausführungsbits aller fünf Skripte gesetzt; Quelltext, Kommentare und Docstrings englisch; Markdown-Dateien ein Absatz je Zeile; keine Tabellen-Artefakte im Ordner (beobachtet).

## 9 Nicht geprüft

`repack-package-readme.sh` wurde nicht ausgeführt.

**Nachtrag 13. September 2026:** Der frühere Zweifel, ob Git beim Branchwechsel unter der Sandbox tatsächlich abbricht, ist inzwischen geklärt — beobachtet statt abgeleitet: `git stash` und `git checkout infra` scheiterten unter aktiver Sandbox tatsächlich am Entfernen von `.claude/skills/`-Dateien aus dem Arbeitsbaum, liefen nach Abschalten der Sandbox sauber durch. Der Datei-Abgleich selbst wurde daraufhin auf eine Plumbing-Route umgestellt, die diesen Konflikt strukturell vermeidet (`master`/`infra` werden nie mehr ausgecheckt) und ebenfalls real getestet — an freischwebenden Commits, nie an echten Branches.
