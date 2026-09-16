# Regeln der Betriebsart `worktree`

Diese Datei ergänzt `rules.de.md` um die Isolation: Jede Sitzung bekommt ihre Werkbank in einem eigenen Worktree unter `<worktree-dir>`, und der Haupt-Checkout bleibt dem Nutzer. Alles aus `rules.de.md` gilt weiter; hier steht nur, was hinzukommt.

<!-- TEMP ISSUE-80278 ANFANG -->

## Bekannte Kollision: Bash-Sandbox und Worktrees

Bevor der erste `git worktree`-Befehl dieser Sitzung läuft (Sitzungsbeginn oder Fortsetzen auf einem anderen Rechner), zweistufig prüfen:

1. **Läuft die Bash-Sandbox in dieser Sitzung?** Erkennbar allein am Kontext, ohne Werkzeugaufruf: Ein System-Reminder, der eine aktive Sandbox-Policy beschreibt (u. a. „Bash tool commands run in a sandbox"), oder eine Meldung, dass die Sandbox gerade abgeschaltet wurde („has been disabled"), zeigt „an"; fehlt jeder solche Hinweis, gilt „aus". Undokumentiertes Verhalten, in dieser Form beobachtet am 2. September 2026 — keine `settings.json`-Prüfung, die über mehrere Scopes verteilt und dadurch potentiell irreführend wäre. Läuft sie nicht: Rest dieses Abschnitts überspringen, normal fortfahren.
2. **Nur wenn sie läuft:** [Issue #80278](https://github.com/anthropics/claude-code/issues/80278) per WebFetch abrufen. Grund: Die Sandbox maskiert `.git/config.worktree`, sobald `git worktree` `extensions.worktreeConfig=true` setzt — danach scheitert jedes Git-Kommando, auch `git status`.
   - Steht dort weiterhin „open": den Nutzer auf die Kollision hinweisen und fragen, ob die Sandbox jetzt abschaltbar ist oder die Betriebsart `worktree` gerade entbehrlich (dann `workbench` oder `direct`). Je nach Antwort fortfahren oder mit dem Nutzer absprechen, wie Kollisionen ausgeschlossen werden.
   - Steht dort nicht mehr „open": dem Nutzer melden, dass die Lösung im Issue zu analysieren und dieser Abschnitt zu überarbeiten ist — und dass die überarbeitete Fassung auch auf anderen Rechnern neu zu installieren ist, weil der Skill dort nur als Kopie liegt. Danach normal fortfahren.

<!-- TEMP ISSUE-80278 ENDE -->

## Sitzungsbeginn: eigene Werkbank anlegen

```bash
git fetch origin
# Entwicklungszweig aktuell? Sonst erst vorspulen (nur Fast-Forward):
git rev-list --count <integration>..origin/<integration>
# Liegen verwaiste Werkbaenke herum? (siehe unten)
git worktree list
# Werkbank samt Worktree anlegen (Ablageort aus git-workbench.json):
git worktree add <worktree-dir>/<topic> -b <workbench-prefix><topic> <integration>
```

Ab jetzt geschieht **alle** Datei- und Git-Arbeit dieser Sitzung im eigenen Worktree — auch wenn die Sitzung im Haupt-Checkout gestartet wurde, dann über absolute Pfade dorthin. Nach dem Anlegen die dann gültige CLAUDE.md des Worktrees beachten.

## Verwaiste Werkbänke melden

Eine Sitzung endet, ihr Worktree bleibt liegen — niemand räumt ihn weg. Claude Codes eigener Sweep fasst nur Worktrees von Subagenten und Hintergrundsitzungen an und rührt die per `--worktree` oder von Hand angelegten nie an. Prüfe deshalb zu Sitzungsbeginn, was `git worktree list` außer dem Haupt-Checkout und der eigenen Werkbank noch zeigt, und **melde jeden Fund**, statt ihn zu übergehen. Zu jedem gehören zwei Fragen:

```bash
git -C <worktree> status --short          # unversionierte oder geaenderte Arbeit?
git log --oneline <integration>..<branch> # unverschmolzene Commits?
```

Ein sauberer Arbeitsbaum heißt **nicht**, dass nichts zu retten ist: Die Arbeit steckt dann im Zweig. Ist dort etwas unverschmolzen, gehört es vor die eigene Arbeit — sonst fasst eine spätere Werkbank dieselben Dateien an, und die alte Arbeit geht beim Squash unter. Entschieden wird das vom Nutzer; Worktree und Zweig entfernst du erst nach seiner Zustimmung.

## Im Worktree arbeiten — oder aus dem Haupt-Checkout heraus

Zwei Wege führen in die eigene Werkbank, und sie unterscheiden sich darin, was Claude Code selbst durchsetzt:

- **Über absolute Pfade**, während die Sitzung im Haupt-Checkout steht. Nichts wird erzwungen; es gelten allein die Regeln dieses Skills.
- **Mit `EnterWorktree`** wechselt die Sitzung wirklich hinein. Der Chat läuft weiter, es wandert nur die Ablage des Transkripts mit dem Arbeitsverzeichnis. Ab dann blockiert Claude Code jede Schreiboperation in den Haupt-Checkout, jede Umleitung von Git dorthin (`git -C`, `--git-dir`, `GIT_DIR`, ein vorangestelltes `cd`) und jedes Kommando, dessen Ziel es nicht verifizieren kann — darunter Heredocs mit nicht gequoteten Begrenzern.

Der zweite Weg ist der sicherere, der erste der beweglichere. Wer isoliert arbeitet, verlässt den Worktree vor dem Squash mit `ExitWorktree`: Der Squash findet im Haupt-Checkout statt und wäre sonst gesperrt.

- Kein Kommando, das fremde Worktrees, fremde Zweige oder den Haupt-Checkout verändert.
- Der Absicherungs-Commit umfasst den ganzen Baum des eigenen Worktrees — der enthält nur die eigene Arbeit.

## Werkbank auf anderem Rechner fortsetzen

Git synchronisiert Zweige, nie Worktree-Verzeichnisse. Über Rechnergrenzen deshalb:

- **Vor dem Rechnerwechsel**, auf Zuruf des Nutzers: die Werkbank pushen — beim ersten Mal `git push -u origin <workbench>`, damit die Upstream-Verknüpfung steht und `git status` Unveröffentlichtes melden kann. Die Push-Regel aus `rules.de.md` gilt dabei.
- **Am anderen Rechner**: `git fetch origin`, dann den Worktree an den vorhandenen Zweig anbinden:

```bash
# Zweig existiert lokal noch nicht:
git worktree add --track -b <workbench> <worktree-dir>/<topic> origin/<workbench>
# Zweig existiert lokal (fruehere Sitzung auf diesem Rechner) -- anbinden, dann vorspulen:
git worktree add <worktree-dir>/<topic> <workbench>
```

## Ergänzungen zum Abschluss

Zur Checkliste in `rules.de.md`:

- **Vor dem Squash `ExitWorktree`**, wenn die Sitzung isoliert im Worktree steht — sonst ist der Haupt-Checkout gesperrt.
- **Der Squash wird ausdrücklich in den Haupt-Checkout adressiert** (`git -C <haupt-checkout> merge --squash <workbench>`), nie über das Arbeitsverzeichnis einer laufenden Kette: Ein `cd` aus einem früheren Kettenglied wirkt fort, und ein Squash im Worktree der Werkbank merged den Zweig in sich selbst — „nichts zu committen", die Kette bricht mitten im Ablauf ab (viermal an einem Tag beobachtet, 26. August 2026).
- **Aufräumen** nach Zustimmung: erst `git worktree remove <worktree-dir>/<topic>`, dann den Zweig löschen. Kein Kommando läuft dabei mit Arbeitsverzeichnis im Worktree, der entfernt wird.

## Regeln, die nie vereinfacht werden

- Jede Sitzung schreibt nur in ihren eigenen Worktree. Der Haupt-Checkout gehört dem Nutzer; einzige Ausnahme ist der freigegebene Squash-Commit.
- Verwaiste Worktrees werden gemeldet, nie stillschweigend entfernt — und nie stillschweigend übergangen.
