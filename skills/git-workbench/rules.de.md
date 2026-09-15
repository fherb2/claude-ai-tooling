# Regeln der Werkbank

Diese Regeln gelten ab jetzt für die gesamte Sitzung, in jeder Betriebsart. Begründungen und Feinheiten stehen in der README dieses Skill-Ordners (`${CLAUDE_SKILL_DIR}`) — zieh sie bei Nachfragen des Nutzers heran, statt zu rekonstruieren, und nenne sie ihm beim ersten Wirksamwerden als Nachschlagewerk. Der Dateiname ist dabei nicht verlässlich: Beim Installieren kann umbenannt worden sein. Sieh im Ordner nach; findest Du sie nicht, antworte ohne sie.

Konkrete Namen legt `.claude/git-workbench.json` fest (Felder: `mode`, `workbench_prefix`, `worktree_dir`). Den Entwicklungszweig kennt die Sitzung aus `.claude/git-branch-model.json` (Feld `integration_branch`) oder aus der Antwort des Nutzers; im Folgenden `<integration>` genannt.

## In jeder Betriebsart

- **Nie auf einem Release-Zweig committen.** Führt das Projekt ein Zweigmodell, steht sein Name dort; sonst gilt, was der Nutzer als Release-Zweig bezeichnet.
- **`push` nur nach Zustimmung im Einzelfall** — und vorher die Push-Regel (unten).
- **Kommandoketten verlassen sich nie auf ein fortwirkendes `cd`.** Jedes Git-Kommando adressiert sein Ziel selbst (`git -C <pfad>`). Kein Kommando läuft mit Arbeitsverzeichnis in einem Ordner, der im selben Zug entfernt wird.
- **Ein Commit umfasst, was zum Schritt gehört** — Doku-Anpassung und zugehörige Codeänderung im selben Commit; der Commit-Body benennt den Schritt oder den Plan, aus dem er stammt.
- **Größere Umstrukturierungen nur von einem sauberen Stand aus** (kein uncommitteter Diff), damit sie per Diff prüfbar und rücknehmbar sind.

## Betriebsart `direct`

Die Sitzung committet auf dem Zweig, auf dem sie steht. Nach jedem freigegebenen und ausgeführten Schritt ein Commit, ohne erneute Nachfrage; er ist dauerhaft und wird nicht später zusammengefasst. Es gibt keine Werkbank und nichts abzuschließen. Voraussetzung ist, dass niemand parallel im selben Arbeitsbaum arbeitet — das hat der Nutzer mit der Wahl dieser Betriebsart gesagt; frage nicht erneut danach.

## Betriebsart `workbench`

**Anlegen.** Eine Werkbank ist ein kurzlebiger Zweig `<workbench-prefix><topic>`, abgeleitet von `<integration>` — oder von dem Zweig, auf dem der Nutzer die Sitzung arbeiten lässt. Das `<topic>` schlägst Du aus der Aufgabe vor, englisch und kurz; der Nutzer bestätigt es (einmal je Sitzung). Vorher `git fetch` und prüfen, ob der Ausgangszweig hinter seinem Remote liegt — wenn ja, melden und anhalten: Das bereinigt der Nutzer zuerst.

Der Arbeitsbaum ist geteilt: Beim Wechsel auf die Werkbank muss er sauber sein. Liegt unversionierte Arbeit des Nutzers herum, frage, ob sie committet oder weggesichert wird — nie selbst mit `checkout` oder `reset` darüber hinweggehen.

**Vorhandene Werkbank.** Existiert schon ein Zweig mit dem Präfix, prüfe `git log --oneline <integration>..<werkbank>`. Liegen dort unverschmolzene Commits, gehört ihre Klärung vor die eigene Arbeit — der Nutzer entscheidet, ob sie gesquasht, verworfen oder fortgesetzt werden. Ist nichts unverschmolzen, darf die Werkbank auf den aktuellen Stand von `<integration>` neu gesetzt und wiederverwendet werden.

**Arbeiten.** Nach jedem abgeschlossenen und freigegebenen Arbeitsschritt ein **Absicherungs-Commit** auf der Werkbank, ohne Nachfrage. Zweck: ein Missverständnis, das erst Schritte später auffällt, durch einfaches Zurücksetzen korrigierbar machen. Zurückkehren auf einen früheren Stand ist ausschließlich auf der Werkbank erlaubt, nie auf einem anderen Zweig.

**Abschluss — feste Checkliste, in dieser Reihenfolge:**

1. **Stand des Zielzweigs holen:** `git fetch`; ist `<integration>` weitergewandert, ihn in die Werkbank mergen und Konflikte hier auflösen — nicht erst beim Squash.
2. **Squash vorschlagen**; den Commit-Text legt der Nutzer fest. Auf `<integration>` wechseln — in `workbench` per `git checkout <integration>` im geteilten Arbeitsbaum, in `worktree` im Haupt-Checkout, ausdrücklich adressiert mit `git -C <haupt-checkout>` —, dann `git merge --squash <werkbank>` und `git commit` **ohne `-a`**: Committet wird nur, was der Squash in den Index gelegt hat, unversionierte Handarbeit des Nutzers bleibt unberührt. Vorher `git status` zeigen.
3. **Aufräumen** nach Zustimmung: Werkbank-Zweig löschen. Für eine Folgeaufgabe wird frisch abgeleitet.

## Betriebsart `worktree`

Alles aus `workbench`, dazu die Isolation: Die Werkbank liegt in einem eigenen Worktree unter `<worktree-dir>`, und der Haupt-Checkout bleibt dem Nutzer. Was dafür hinzukommt — Anlegen, verwaiste Werkbänke, Arbeiten im Worktree, Rechnerwechsel, die Ergänzungen zum Abschluss —, steht in `rules-worktree.de.md` desselben Ordners.

## Die Push-Regel

Ein Push veröffentlicht einen Zweig — und lässt alle anderen zurück. Wer abends einen Zweig pusht und morgens am anderen Rechner weiterarbeitet, findet dort nur, was gepusht wurde.

Deshalb **vor jedem Push**, den der Nutzer verlangt oder die Sitzung vorschlägt:

```bash
git for-each-ref --format='%(refname:short) %(upstream:short) %(upstream:track)' refs/heads
```

Jeder lokale Zweig, der vor seinem Upstream liegt (`[ahead n]`) oder keinen Upstream hat, trägt Unveröffentlichtes. Je Fund fragen: „Auf `<zweig>` liegen n unveröffentlichte Commits — mitpushen?", mit Ja als Vorschlag, sofern der Nutzer nicht widerspricht. Ob ein Zweig noch gebraucht wird, lässt sich nicht zuverlässig einschätzen; deshalb wird gefragt, nicht geraten. Ein Zweig ohne Upstream wird beim ersten Push mit `-u` verknüpft, damit `git status` künftig Unveröffentlichtes melden kann.

## Ersteinrichtung

Nur auf ausdrücklichen Wunsch des Nutzers, als vorgelegter Plan:

1. **Betriebsart klären** (`direct`, `workbench`, `worktree` oder `ask`), das Werkbank-Präfix (ohne anderslautende Vorgabe `claude-wb/`) und, falls `worktree` je in Frage kommt, den Ablageort — ohne anderslautende Vorgabe `.claude/worktrees/` **innerhalb** des Repositories: Dort legt auch Claude Code seine eigenen Worktrees an, ein Wechsel dorthin braucht keine gesonderte Freigabe, der Pfad ergibt sich auf jedem Rechner aus dem Repo-Pfad, und die Arbeit liegt im Blickfeld des Editors.
2. **`.claude/git-workbench.json` schreiben.** Führt das Projekt ein Zweigmodell mit zentral verwalteten Dateien, gehört diese Datei zu ihnen; wie sie committet wird, folgt dann dessen Regeln.
3. **`.gitignore`**: Der Worktree-Ordner muss dort stehen, sonst erscheint sein Inhalt im Haupt-Checkout als unversioniert. Wie die `.gitignore` committet wird, folgt den Zweigregeln des Projekts.
4. **Stillen Trigger prüfen** in der CLAUDE.md des Zielorts.
5. **Aufklären**: dem Nutzer sagen, was ab jetzt automatisch geschieht und was gefragt wird, und die README als Nachschlagewerk nennen.

## Freigabestufen

Diese Stufen gelten für die genannten Handlungen auch dann, wenn an anderer Stelle für vergleichbare Tätigkeiten anderes vereinbart ist. Nur eine ausdrückliche Einzelanweisung des Nutzers im Chat geht vor.

| Stufe | Handlungen |
| --- | --- |
| **Automatisch, mit Meldung** | Lesende Git-Kommandos; Absicherungs-Commits auf der eigenen Werkbank; Commits in `direct` nach einem freigegebenen Schritt |
| **Einmal je Sitzung** | Betriebsart in `ask`; Anlegen der eigenen Werkbank (`<topic>` wird vorgeschlagen); Nennen des Entwicklungszweigs, wenn das Projekt ihn nicht festlegt |
| **Einmal je Projekt** | Ersteinrichtung; Präfix und Ablageort |
| **Jedes Mal** | `push`; Squash in den Entwicklungszweig; Löschen von Zweigen oder Worktrees; jede Handlung an fremden Worktrees oder am Haupt-Checkout in `worktree` |

## Regeln, die nie vereinfacht werden

- Werkbank-Arbeit erreicht den Entwicklungszweig nur per Squash, nie als Merge-Commit. Sonst wird die Absicherungs-Historie Teil der Hauptlinie, und die Squash-Disziplin ist wirkungslos.
- Der Squash-Commit wird ohne `-a` ausgeführt. Mit `-a` wandert unversionierte Handarbeit des Nutzers in den Squash.
- Zurückgesetzt wird nur auf der Werkbank. Auf keinem anderen Zweig wird Historie umgeschrieben.
- `direct` ist eine Entscheidung des Nutzers, keine Nachlässigkeit. Sie wird ausgeführt, nicht diskutiert.
