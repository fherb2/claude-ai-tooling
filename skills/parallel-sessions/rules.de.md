# Regeln des Worktree-Arbeitsmodells

Diese Regeln gelten ab jetzt für die gesamte Sitzung. Begründungen und Feinheiten stehen in der README dieses Skill-Ordners (`${CLAUDE_SKILL_DIR}`) — zieh sie bei Nachfragen des Nutzers heran, statt zu rekonstruieren. Der Dateiname ist dabei nicht verlässlich: Beim Installieren kann umbenannt worden sein. Sieh im Ordner nach; findest Du sie nicht, antworte ohne sie.

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
# Liegen verwaiste Werkbaenke herum? (siehe unten)
git worktree list
# Werkbank samt Worktree anlegen (Ablageort aus git-worktree-model.json):
git worktree add <worktree-dir>/<topic> -b <workbench-prefix><topic> <integration>
```

Das `<topic>` schlägst du aus der Aufgabe vor — englisch und kurz; der Nutzer bestätigt es (Freigabestufen unten). Ab jetzt geschieht **alle** Datei- und Git-Arbeit dieser Sitzung im eigenen Worktree — auch wenn die Sitzung im Haupt-Checkout gestartet wurde, dann über absolute Pfade dorthin.

Unmittelbar nach dem Anlegen — und ebenso zu Beginn jeder späteren Sitzung auf einer schon bestehenden Werkbank — der **Infra-Abgleich**:

```bash
git -C <worktree> restore --source=<infra> -- <infra-files>
```

Ändert er etwas, melde das dem Nutzer in einem Satz; die Änderungen wandern mit dem nächsten Checkpoint-Commit mit. Nach dem Abgleich die dann gültige CLAUDE.md der Sitzung beachten.

### Verwaiste Werkbänke melden

Eine Sitzung endet, ihr Worktree bleibt liegen — niemand räumt ihn weg. Claude Codes eigener Sweep fasst nur Worktrees von Subagenten und Hintergrundsitzungen an und rührt die per `--worktree` oder von Hand angelegten nie an. Prüfe deshalb zu Sitzungsbeginn, was `git worktree list` außer dem Haupt-Checkout und der eigenen Werkbank noch zeigt, und **melde jeden Fund**, statt ihn zu übergehen. Zu jedem gehören zwei Fragen:

```bash
git -C <worktree> status --short          # unversionierte oder geaenderte Arbeit?
git log --oneline <integration>..<branch> # unverschmolzene Commits?
```

Ein sauberer Arbeitsbaum heißt **nicht**, dass nichts zu retten ist: Die Arbeit steckt dann im Branch. Ist dort etwas unverschmolzen, gehört es vor die eigene Arbeit — sonst fasst eine spätere Werkbank dieselben Dateien an und die alte Arbeit geht beim Squash unter. Entschieden wird das vom Nutzer; Worktree und Branch entfernst du erst nach seiner Zustimmung.

### Im Worktree arbeiten — oder aus dem Haupt-Checkout heraus

Zwei Wege führen in die eigene Werkbank, und sie unterscheiden sich darin, was Claude Code selbst durchsetzt:

- **Über absolute Pfade**, während die Sitzung im Haupt-Checkout steht. Nichts wird erzwungen; es gelten allein die Regeln dieses Skills.
- **Mit `EnterWorktree`** wechselt die Sitzung wirklich hinein. Der Chat läuft weiter, es wandert nur die Ablage des Transkripts mit dem Arbeitsverzeichnis. Ab dann blockiert Claude Code jede Schreiboperation in den Haupt-Checkout, jede Umleitung von Git dorthin (`git -C`, `--git-dir`, `GIT_DIR`, ein vorangestelltes `cd`) und jedes Kommando, dessen Ziel es nicht verifizieren kann — darunter Heredocs mit nicht gequoteten Begrenzern.

Der zweite Weg ist der sicherere, der erste der beweglichere. Wer isoliert arbeitet, verlässt den Worktree vor dem Squash-Merge mit `ExitWorktree`: Der Merge findet im Haupt-Checkout statt und wäre sonst gesperrt.

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
4. **Squash-Merge vorschlagen**; den Commit-Text legt der Nutzer fest. Steht die Sitzung isoliert im Worktree, zuerst `ExitWorktree` — sonst ist der Haupt-Checkout gesperrt. Ausführung im Haupt-Checkout auf dem Integrationsbranch: `git merge --squash <workbench>`, dann `git commit` **ohne `-a`** — committet wird nur, was der Squash in den Index gelegt hat, unversionierte Handarbeit des Nutzers bleibt unberührt. Vorher `git status` zeigen.
5. **Aufräumen** nach Zustimmung: Worktree entfernen (`git worktree remove`), Werkbank-Branch löschen. Für eine Folgeaufgabe wird frisch vom Integrationsbranch abgeleitet.

### Ersteinrichtung des Modells

Nur auf ausdrücklichen Wunsch des Nutzers, als vorgelegter Plan. Schritte: Namen klären (Integrations-, Release-, Infra-Branch, Werkbank-Präfix, Ablageort — als Ablageort wird ohne anderslautende Vorgabe `.claude/worktrees/` **innerhalb** des Repositories vorgeschlagen: Dort legt auch Claude Code seine eigenen Worktrees an, ein Wechsel dorthin per `EnterWorktree` braucht keine gesonderte Freigabe, der Pfad ergibt sich auf jedem Rechner aus dem Repo-Pfad, und vor allem liegt der Worktree damit innerhalb des Ordners, den der Editor des Nutzers geöffnet hat — außerhalb sieht er die Arbeit nicht. Der Ordner gehört in die `.gitignore`, sonst erscheint sein Inhalt im Haupt-Checkout als unversioniert) und Infra-Dateiliste festlegen; Integrationsbranch anlegen, falls es ihn nicht gibt; Infra-Branch als orphan anlegen (`git worktree add --orphan -b <infra> <tmp>`, benötigt Git ≥ 2.42) und die Infra-Dateien per `git checkout <integration> -- <datei…>` übernehmen; `.claude/git-worktree-model.json` mit den Feldern von oben schreiben; den stillen Trigger dieses Skills in der Projekt-CLAUDE.md prüfen — die liegt danach selbst auf dem Infra-Branch.

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
