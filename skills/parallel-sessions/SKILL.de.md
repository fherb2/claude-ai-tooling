---
name: parallel-sessions
description: Führt die Zusammenarbeit mehrerer gleichzeitig arbeitender Claude-Code-Sitzungen im selben Repository — jede Sitzung auf eigener Werkbank in einem eigenen Git-Worktree, zentrale Dateien wie die CLAUDE.md über einen Infra-Branch verteilt, Abschluss per Squash-Merge. Verwenden, sobald der Nutzer einen zweiten offenen Chat, eine zweite Claude-Instanz oder gleichzeitige Arbeit erwähnt, fremde Änderungen im Arbeitsbaum auftauchen, eine Sitzung in einem Git-Worktree beginnt oder das Projekt das Worktree-Arbeitsmodell vereinbart hat, oder wenn der Nutzer /parallel-sessions aufruft.
license: CC0-1.0
---

# Parallele Claude-Sitzungen über Git-Worktrees

Dieser Skill trägt nur die Abläufe und Regeln. Begründungen und Feinheiten stehen in der README seines Ordners (`${CLAUDE_SKILL_DIR}`) — zieh sie bei Nachfragen des Nutzers heran, statt zu rekonstruieren. Der Dateiname ist dabei nicht verlässlich: Beim Installieren kann umbenannt worden sein. Sieh im Ordner nach; findest Du sie nicht, antworte ohne sie.

## Die Lage feststellen

Prüfe zuerst, welcher der drei Fälle vorliegt:

1. **Das Projekt hat das Worktree-Arbeitsmodell vereinbart** — erkennbar an der Datei `.claude/git-worktree-model.json`. Dann gilt der Alltagsablauf unten; die Namen von Branches, Ablageort und Infra-Dateien stehen in dieser Datei, nicht in diesem Skill.
2. **Kein Modell vereinbart, aber eine zweite Sitzung arbeitet oder ist angekündigt.** Dann gilt die Sofortregel (nächster Abschnitt), und dem Nutzer wird die Ersteinrichtung des Modells angeboten — kurz und ohne Drängen, denn sie ändert seine Arbeitsweise.
3. **Weder noch** — eine einzelne Sitzung, kein Modell: Dieser Skill verlangt dann nichts.

Ob die laufende Sitzung selbst in einem Worktree steht, zeigt `git rev-parse --git-dir --git-common-dir`: Unterscheiden sich die beiden Pfade, ist es ein Worktree.

## Sofortregel ohne vereinbartes Modell: Schreibhoheit klären

Frage den Nutzer, **welche Sitzung eigenständig schreibende Git-Kommandos ausführen darf** (`commit`, `add`, `push`, `checkout`, `restore`, `reset`, `merge`). Bis zur Antwort führt diese Sitzung keines davon aus; lesende Kommandos (`status`, `diff`, `log`, `fetch`) bleiben erlaubt. Einmal erteilte Hoheit gilt für die Sitzung fort; umverteilen kann der Nutzer sie jederzeit, dafür meldet er sich aktiv.

Diese Regel ist der Rückfallweg. Sie wird vom Worktree-Modell abgelöst, sobald es eingerichtet ist: Dann braucht niemand mehr eine Hoheit, weil keine zwei Sitzungen denselben Arbeitsbaum teilen.

## Das Arbeitsmodell

Vier Branch-Rollen, deren konkrete Namen `.claude/git-worktree-model.json` festlegt (Felder: `integration_branch`, `release_branch`, `workbench_prefix`, `worktree_dir`, `infra_branch`, `infra_files`):

- **Releasebranch** (etwa `master`): nur Fertiges. Kein Arbeitsort.
- **Integrationsbranch** (etwa `dev`): trägt alles in Entwicklung. Der Haupt-Checkout des Nutzers steht auf ihm; er ist **sein** Arbeitsbereich — Claude schreibt dort keine Dateien und committet dort nur den freigegebenen Squash (siehe Abschluss).
- **Werkbänke** (etwa `claude-wb/<topic>`): je gleichzeitiger Sitzung eine, vom Integrationsbranch abgeleitet, jede in ihrem eigenen Worktree. Kurzlebig: Nach dem Squash-Merge wird sie verworfen.
- **Infra-Branch** (etwa `infra`): ein orphaner Branch, der ausschließlich die zentralen Dateien trägt (`infra_files`: CLAUDE.md des Projekts, Editor- und Werkzeugkonfiguration, `.gitignore` …). Er wird **nie gemergt**; verteilt wird per `git restore --source=<infra> -- <infra-files>`, das jede Sitzung selbst in ihrem Worktree ausführt.

### Sitzungsbeginn: eigene Werkbank anlegen

```bash
git fetch origin
# Integrationsbranch aktuell? Sonst erst vorspulen (nur Fast-Forward):
git rev-list --count <integration>..origin/<integration>
# Werkbank samt Worktree anlegen (Ablageort aus git-worktree-model.json):
git worktree add <worktree-dir>/<topic> -b <workbench-prefix><topic> <integration>
```

Das `<topic>` schlägst du aus der Aufgabe vor — englisch und kurz; der Nutzer bestätigt es (Freigabestufen unten). Ab jetzt geschieht **alle** Datei- und Git-Arbeit dieser Sitzung im eigenen Worktree — auch wenn die Sitzung im Haupt-Checkout gestartet wurde, dann über absolute Pfade dorthin.

Unmittelbar nach dem Anlegen — und ebenso zu Beginn jeder späteren Sitzung auf einer schon bestehenden Werkbank — der **Infra-Abgleich**:

```bash
git -C <worktree> restore --source=<infra> -- <infra-files>
```

Ändert er etwas, melde das dem Nutzer in einem Satz; die Änderungen wandern mit dem nächsten Checkpoint-Commit mit. Nach dem Abgleich die dann gültige CLAUDE.md der Sitzung beachten.

### Werkbank auf anderem Rechner fortsetzen

Git synchronisiert Branches, nie Worktree-Verzeichnisse. Über Rechnergrenzen deshalb:

- **Vor dem Rechnerwechsel**, auf Zuruf des Nutzers: die Werkbank pushen — beim ersten Mal `git push -u origin <workbench>`, damit die Upstream-Verknüpfung steht und `git status` Unveröffentlichtes melden kann.
- **Am anderen Rechner**: `git fetch origin`, dann den Worktree an den vorhandenen Branch anbinden:

```bash
# Branch existiert lokal noch nicht:
git worktree add --track -b <workbench> <worktree-dir>/<topic> origin/<workbench>
# Branch existiert lokal (frühere Sitzung auf diesem Rechner) — anbinden, dann vorspulen:
git worktree add <worktree-dir>/<topic> <workbench>
```

- Danach wie bei jedem Sitzungsbeginn: Infra-Abgleich, weiterarbeiten.

### Arbeiten auf der Werkbank

- Nach jedem abgeschlossenen Arbeitsschritt ein **Checkpoint-Commit** im eigenen Worktree, ohne Nachfrage. Er umfasst den ganzen Baum des Worktrees — der enthält nur die eigene Arbeit.
- Kein Kommando, das fremde Worktrees, fremde Branches oder den Haupt-Checkout verändert.
- `push` der Werkbank nur nach Zustimmung im Einzelfall.

### Zentrale Dateien ändern (Infra)

Dauerhafte Änderungen an Infra-Dateien entstehen **ausschließlich auf dem Infra-Branch** — nie als Werkbank-Commit. Ablauf, jeweils mit Zustimmung des Nutzers:

```bash
git worktree add <worktree-dir>/_infra <infra>   # temporärer Worktree
# Änderung dort vornehmen, committen
git worktree remove <worktree-dir>/_infra
git -C <worktree> restore --source=<infra> -- <infra-files>
```

Danach dem Nutzer melden: Andere **laufende** Sitzungen übernehmen die Änderung erst bei ihrem nächsten Infra-Abgleich — wer sie sofort braucht, stößt den Abgleich dort an.

### Infra-Änderungen erproben (Experimente)

Soll eine zentrale Änderung erst erprobt werden, bevor sie auf den Infra-Branch geht — ein neuer Regel-Absatz in der CLAUDE.md, ein Hook in den Settings, eine geänderte Linter-Konfiguration —, darf die Werkbank dafür ihre Kopie der Infra-Datei ändern. Bedingungen:

- Der geänderte Block wird eingefasst in die Marken `<!-- INFRA-EXPERIMENT ANFANG <workbench> <datum> -->` und `<!-- INFRA-EXPERIMENT ENDE -->`.
- Das Experiment endet immer durch den Infra-Abgleich (ein Befehl, siehe oben) — nie durch Zurückeditieren von Hand, und die Experimentfassung wird **nie** gemergt.
- Bewährt sich die Regel, wird sie ohne Marken neu auf dem Infra-Branch eingepflegt (voriger Abschnitt).
- Holt ein zwischenzeitlicher Infra-Abgleich neue Zentraländerungen, setzt du den markierten Block danach wieder ein.

### Abschluss einer Aufgabe

Feste Checkliste, in dieser Reihenfolge:

1. **Infra-Abgleich**: `git diff <infra> -- <infra-files>` muss leer sein; sonst `restore` — damit endet auch jedes Experiment.
2. **Experiment-Suche**: `grep -rn "INFRA-EXPERIMENT" <worktree>` muss leer sein.
3. **Integrationsstand holen**: `git fetch`; ist der Integrationsbranch weitergewandert, ihn in die Werkbank mergen und Konflikte hier auflösen — nicht erst beim Squash.
4. **Squash-Merge vorschlagen**; den Commit-Text legt der Nutzer fest. Ausführung im Haupt-Checkout auf dem Integrationsbranch: `git merge --squash <workbench>`, dann `git commit` **ohne `-a`** — committet wird nur, was der Squash in den Index gelegt hat, unversionierte Handarbeit des Nutzers bleibt unberührt. Vorher `git status` zeigen.
5. **Aufräumen** nach Zustimmung: Worktree entfernen (`git worktree remove`), Werkbank-Branch löschen. Für eine Folgeaufgabe wird frisch vom Integrationsbranch abgeleitet.

### Ersteinrichtung des Modells

Nur auf ausdrücklichen Wunsch des Nutzers, als vorgelegter Plan. Schritte: Namen klären (Integrations-, Release-, Infra-Branch, Werkbank-Präfix, Ablageort — als Ablageort wird ohne anderslautende Vorgabe der Geschwisterordner `<repo>-worktrees` neben dem Repository vorgeschlagen, weil er sich auf jedem Rechner deterministisch aus dem Repo-Pfad ergibt) und Infra-Dateiliste festlegen; Integrationsbranch anlegen, falls es ihn nicht gibt; Infra-Branch als orphan anlegen (`git worktree add --orphan -b <infra> <tmp>`, benötigt Git ≥ 2.42) und die Infra-Dateien per `git checkout <integration> -- <datei…>` übernehmen; `.claude/git-worktree-model.json` mit den Feldern von oben schreiben; den stillen Trigger dieses Skills in der Projekt-CLAUDE.md prüfen — die liegt danach selbst auf dem Infra-Branch.

## Freigabestufen

Diese Stufen gelten für die genannten Handlungen auch dann, wenn an anderer Stelle für vergleichbare Tätigkeiten anderes vereinbart ist. Nur eine ausdrückliche Einzelanweisung des Nutzers im Chat geht vor.

| Stufe | Handlungen |
| --- | --- |
| **Automatisch, mit Meldung** | Lesende Git-Kommandos; Infra-Abgleich im eigenen Worktree (Sitzungsbeginn und Abschluss-Schritt 1); Checkpoint-Commits auf der eigenen Werkbank; Experiment-Suche |
| **Einmal je Sitzung** | Anlegen der eigenen Werkbank samt Worktree (`<topic>` wird vorgeschlagen) |
| **Einmal je Projekt** | Ersteinrichtung des Modells; Ablageort der Worktrees; die Infra-Dateiliste und jede spätere Änderung an ihr |
| **Jedes Mal** | `push`; jeder Commit auf dem Infra-Branch; Squash-Merge in den Integrationsbranch; Löschen von Branches oder Worktrees; jede Handlung, die fremde Worktrees oder den Haupt-Checkout berührt |

## Regeln, die nie vereinfacht werden

- Keine dauerhafte Änderung an Infra-Dateien außerhalb des Infra-Branches. Werkbank-Änderungen daran sind Experimente: markiert, sterblich, nie gemergt.
- Der Infra-Branch wird nie gemergt und von keinem anderen Branch abgeleitet. Verteilung ausschließlich per `restore --source`.
- Jede Sitzung schreibt nur in ihren eigenen Worktree. Der Haupt-Checkout gehört dem Nutzer; einzige Ausnahme ist der freigegebene Squash-Commit.
- In den Integrationsbranch kommt Werkbank-Arbeit nur per Squash, nie als Merge-Commit.
