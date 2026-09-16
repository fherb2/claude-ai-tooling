# Regeln des Zweigmodells

Diese Regeln gelten ab jetzt für die gesamte Sitzung. Begründungen und Feinheiten stehen in der README dieses Skill-Ordners (`${CLAUDE_SKILL_DIR}`) — zieh sie bei Nachfragen des Nutzers heran, statt zu rekonstruieren, und nenne sie ihm beim ersten Wirksamwerden als Nachschlagewerk. Der Dateiname ist dabei nicht verlässlich: Beim Installieren kann umbenannt worden sein. Sieh im Ordner nach; findest Du sie nicht, antworte ohne sie.

## Die vier Rollen

Konkrete Namen legt `.claude/git-branch-model.json` fest (Felder: `integration_branch`, `release_branch`, `release_transfer`, `management_branch`, `management_files`).

| Rolle | Feld | Was dort geschieht |
| --- | --- | --- |
| **Entwicklungszweig** (etwa `dev`) | `integration_branch` | Die Hauptlinie der Entwicklung. Trägt alles, was in Arbeit ist; jeder Commit bleibt erhalten. |
| **Release-Zweig** (etwa `master`) | `release_branch` | Der veröffentlichte Stand. Kein Arbeitsort: Dort wird nichts geändert, dorthin wird nur übernommen. |
| **Themenzweige** (frei benannt) | — | Je Aufgabe einer, vom Entwicklungszweig abgezweigt und per Merge in ihn zurückgeführt. Ihre Commits bleiben erhalten. |
| **Verwaltungszweig** (etwa `repo-management`) | `management_branch`, `management_files` | Ein orphaner Zweig ohne gemeinsame Herkunft mit den anderen. Trägt ausschließlich die Verwaltungsdateien: das, was auf jedem Zweig gleich sein muss. Wird nie gemergt — seine Dateien werden über jeden anderen Zweig gelegt. |

**Die Grenze, die Menschen- von Maschinenkörnung trennt.** Commits, die ein Mensch gesetzt hat, behalten ihre Körnung: Ein Themenzweig wird gemergt, seine Historie bleibt. Absicherungs-Commits einer Maschine — Zwischenstände einer Sitzung, die nur das Zurückgehen ermöglichen — gehören nicht in diese Historie; sie werden auf die Körnung gebracht, die ein Mensch gewählt hätte, bevor sie den Entwicklungszweig erreichen. Wie eine Sitzung das tut, regelt sie selbst; dieses Modell verlangt nur, dass sie es tut.

## Der Entwicklungszweig und seine Themenzweige

- Der Entwicklungszweig ist der Arbeitsort. Der Haupt-Checkout des Nutzers steht in aller Regel auf ihm.
- Eine abgegrenzte Aufgabe — ein Issue, ein Thema — darf einen eigenen Zweig bekommen. Er zweigt vom Entwicklungszweig ab und kehrt per Merge zurück (`git merge`, ohne `--squash`); ob mit Merge-Commit oder als Fast-Forward, entscheidet der Nutzer. Vor dem Merge den Stand des Entwicklungszweigs holen und Konflikte auf dem Themenzweig lösen.
- Wer einen Themenzweig anlegt, benennt ihn nach der Aufgabe, englisch und kurz. Ein Präfix schreibt dieses Modell nicht vor.

## Release-Übernahme

Wann etwas in den Release-Zweig übernommen wird, entscheidet der Nutzer; die Übernahme selbst ist jedes Mal freigabepflichtig. Wie sie geschieht, legt `release_transfer` fest — und die beiden Werte schließen einander aus:

**`merge` — ein Produkt.** Der Entwicklungszweig wird in den Release-Zweig gemergt, ohne `--squash`; die Historie bleibt durchgehend. Vorher: Abgleich der Verwaltungsdateien (unten) auf dem Entwicklungszweig, `git fetch`, und kein unveröffentlichter Stand, den der Merge übergehen würde.

**`file-sync` — mehrere Produkte.** Wird jeweils nur ein Teil des Entwicklungsstands veröffentlicht, ist ein Merge unmöglich: Er nimmt alles oder nichts, und nach einer ersten Teilübernahme rechnete jeder spätere Merge mit einer Merge-Basis, die den Zustand nie beschrieben hat. Deshalb:

- Die beiden Zweige haben **getrennte Historien**. Übertragen wird Datei für Datei; „jeder Commit bleibt erhalten" gilt innerhalb des Entwicklungszweigs, nicht über die Grenze zum Release-Zweig.
- Der Release-Zweig wird **nie ausgecheckt**. Sein Baum lässt sich auf Objektebene fortschreiben (`read-tree`/`update-index`/`write-tree`/`commit-tree`/`update-ref` mit einer alternativen Index-Datei), ohne den Arbeitsbaum zu berühren.
- **Verwaltungsdateien kommen nie aus dem Entwicklungszweig**, sondern immer aus dem Verwaltungszweig — auf beide Zweige gleich.
- Was im Release-Zweig bewusst fehlen soll (Unfertiges, Entwicklungswerkzeug), ist eine Festlegung des Projekts. Das ausgearbeitete Übertragungsrezept samt Ausschlussliste und Gegenprobe gehört deshalb in das Projekt, nicht in diesen Skill; dieser Skill nennt nur die Invarianten.

## Der Verwaltungszweig

### Was auf ihn gehört

Alles, was auf **jedem** Zweig identisch sein muss — und nur das. Das Kriterium ist nicht „ist es Konfiguration", sondern „muss es überall gleich sein":

- **Konfiguration**: die Projekt-CLAUDE.md, Editor- und Linter-Einstellungen, `.gitignore`, die Konfigurationsdateien dieses und verwandter Modelle.
- **Werkzeug mit eigener Logik**, sofern es zweigunabhängig ist: ein Projekt-Skill, der auf jedem Zweig gleich gebraucht wird, eine CI-Konfiguration.
- **Nicht**: ein Werkzeug, das nur auf dem Entwicklungszweig gebraucht wird. Die Verteilung legte es auch auf den Release-Zweig.

Die Liste steht in `management_files`; sie ändert sich nur mit Zustimmung des Nutzers.

### Verteilung: Überlagern statt Mergen

Der Verwaltungszweig wird **nie** gemergt und von **keinem** anderen Zweig abgeleitet. Seine Dateien werden geholt:

```bash
git restore --source=<management> -- <management-files>
```

Das schreibt die Fassung des Verwaltungszweigs in den Arbeitsbaum, in dem die Sitzung arbeitet; die Änderung wandert mit dem nächsten Commit auf dem dortigen Zweig mit. Für jede Verwaltungsdatei gibt es genau eine gültige Fassung — die auf dem Verwaltungszweig —, und Überschreiben ist immer die richtige Auflösung. **Unter einer Bedingung:** Die lokale Fassung ist veraltet, nicht neu. Genau das prüft der Abgleich.

### Der Abgleich mit Richtungsprüfung

**Wann:** bevor in einer Sitzung zum ersten Mal ein schreibendes Git-Kommando läuft, und vor jeder Release-Übernahme. Der Abgleich läuft im Arbeitsbaum, in dem die Sitzung arbeitet.

**Schritt 1 — Weicht etwas ab?**

```bash
git diff --name-only <management> -- <management-files>
```

Leer: nichts zu tun. Sonst je genannter Datei Schritt 2.

**Schritt 2 — In welche Richtung?** Die lokale Fassung ist entweder ein früherer Stand des Verwaltungszweigs (dann ist sie **veraltet**) oder sie enthält etwas, das dort nie stand (dann ist sie **neu**):

```bash
BLOB=$(git hash-object <datei>)                       # Fassung im Arbeitsbaum
git log --oneline --find-object=$BLOB <management>    # kam dieser Inhalt je auf dem Verwaltungszweig vor?
```

- **Ausgabe nicht leer → veraltet.** `git restore --source=<management> -- <datei>` ausführen und dem Nutzer in einem Satz melden. Ebenso bei einer Datei, die lokal fehlt, auf dem Verwaltungszweig aber existiert.
- **Ausgabe leer → neu.** Anhalten und nicht überschreiben: Jemand hat die Datei außerhalb des Verwaltungszweigs geändert, und `restore` würde diese Arbeit vernichten. Dem Nutzer die Abweichung zeigen (`git diff <management> -- <datei>`) und den Weg vorschlagen, die Änderung auf den Verwaltungszweig zu bringen (nächster Abschnitt). Ebenso bei einer Datei, die lokal in der Liste steht, auf dem Verwaltungszweig aber fehlt.
- **Ein markiertes Experiment** (unten) ist eine gewollte Abweichung in Richtung „neu": nicht überschreiben, nicht melden — außer vor der Release-Übernahme, dort endet es.

`--find-object` braucht Git ≥ 2.16.

### Verwaltungsdateien ändern

Dauerhafte Änderungen an Verwaltungsdateien entstehen **ausschließlich auf dem Verwaltungszweig**. Weil er orphan ist und nur wenige Dateien trägt, wird er nicht im Haupt-Checkout ausgecheckt — das leerte den Arbeitsbaum —, sondern in einem vorübergehenden Worktree. Jeder Commit dort ist freigabepflichtig.

**Kleine Änderung:**

```bash
git worktree add <tmp> <management>        # vorübergehender Worktree
# Änderung dort vornehmen, committen
git worktree remove <tmp>
git restore --source=<management> -- <management-files>   # im eigenen Arbeitsbaum
```

**Größere oder iterative Arbeit** — ein Skill, ein Hook, etwas, das mehrere Anläufe braucht — auf einem **Arbeitszweig, der vom Verwaltungszweig abzweigt** und per Squash in ihn zurückkehrt. Das verletzt die Invariante nicht: „Von keinem anderen Zweig abgeleitet, nie gemergt" meint den Verkehr mit Entwicklungs- und Release-Zweig. Ein Zweig, der vom Verwaltungszweig kommt, enthält nur Verwaltungsdateien, und seine Rückkehr per Squash lässt die Historie des Verwaltungszweigs sauber. Wie eine Sitzung ihre Arbeitszweige führt, regelt sie selbst.

Danach dem Nutzer melden: Andere **laufende** Sitzungen und andere Zweige übernehmen die Änderung erst bei ihrem nächsten Abgleich.

<!-- TEMP ISSUE-80278 ANFANG -->
Läuft in der Sitzung eine Bash-Sandbox, kann `git worktree add` an einer bekannten Kollision scheitern, nach der auch `git status` versagt ([Issue #80278](https://github.com/anthropics/claude-code/issues/80278)). Ob die Sandbox läuft, zeigt allein der Kontext: Ein System-Reminder, der eine aktive Sandbox-Policy beschreibt, heißt „an". Dann vor dem ersten `git worktree`-Kommando den Nutzer fragen, ob die Sandbox kurz abschaltbar ist, oder ihm die Änderung auf dem Verwaltungszweig überlassen.
<!-- TEMP ISSUE-80278 ENDE -->

### Experimente

Soll eine zentrale Änderung erst erprobt werden, bevor sie auf den Verwaltungszweig geht — ein neuer Regel-Absatz in der CLAUDE.md, ein Hook in den Settings —, darf ihre Kopie im eigenen Arbeitsbaum dafür geändert werden. Bedingungen:

- Der geänderte Block ist eingefasst in `<!-- MANAGEMENT-EXPERIMENT ANFANG <zweig> <datum> -->` und `<!-- MANAGEMENT-EXPERIMENT ENDE -->`.
- Das Experiment endet durch den Abgleich, nie durch Zurückeditieren von Hand — und die Experimentfassung wird **nie** gemergt und **nie** in den Release übernommen. Vor jeder Release-Übernahme muss `grep -rn "MANAGEMENT-EXPERIMENT"` leer sein.
- Bewährt sich die Regel, wird sie ohne Marken neu auf dem Verwaltungszweig eingepflegt.
- Holt ein zwischenzeitlicher Abgleich neue Zentraländerungen, wird der markierte Block danach wieder eingesetzt.

## Ersteinrichtung des Modells

Nur auf ausdrücklichen Wunsch des Nutzers, als vorgelegter Plan. Schritte:

1. **Namen und Art klären**: Entwicklungszweig, Release-Zweig, Verwaltungszweig, `release_transfer` (ein Produkt → `merge`, mehrere → `file-sync`), die Liste der Verwaltungsdateien. Für den Verwaltungszweig einen Namen wählen, der sagt, was darauf liegt — nicht `infra`: Das ist in der IT für Deployment belegt.
2. **Entwicklungszweig anlegen**, falls es ihn nicht gibt; der Haupt-Checkout wechselt dorthin.
3. **Verwaltungszweig als Orphan anlegen** (`git worktree add --orphan -b <management> <tmp>`, Git ≥ 2.42), die Verwaltungsdateien aus dem Entwicklungszweig übernehmen (`git checkout <integration> -- <datei…>` im Orphan-Worktree), committen, Worktree entfernen, mit `-u` pushen.
4. **`.claude/git-branch-model.json` schreiben** — und sie selbst in `management_files` aufnehmen: Sie muss auf jedem Zweig gleich sein.
5. **Stillen Trigger prüfen** in der CLAUDE.md des Zielorts. Liegt die Projekt-CLAUDE.md auf dem Verwaltungszweig, geschieht die Änderung dort.
6. **Aufklären**: dem Nutzer sagen, was ab jetzt automatisch geschieht (der Abgleich in Richtung „veraltet") und was jedes Mal gefragt wird, und die README als Nachschlagewerk nennen.

## Freigabestufen

Diese Stufen gelten für die genannten Handlungen auch dann, wenn an anderer Stelle für vergleichbare Tätigkeiten anderes vereinbart ist. Nur eine ausdrückliche Einzelanweisung des Nutzers im Chat geht vor.

| Stufe | Handlungen |
| --- | --- |
| **Automatisch, mit Meldung** | Lesende Git-Kommandos; Abgleich in Richtung „veraltet"; Experiment-Suche |
| **Nach Rückfrage** | Abgleich in Richtung „neu" — der Weg wird vorgeschlagen, nicht ausgeführt |
| **Einmal je Projekt** | Ersteinrichtung; die Liste der Verwaltungsdateien und jede spätere Änderung an ihr |
| **Jedes Mal** | `push`; jeder Commit auf dem Verwaltungszweig; jede Release-Übernahme; Anlegen und Löschen von Zweigen; Merge eines Themenzweigs |

## Regeln, die nie vereinfacht werden

- Keine dauerhafte Änderung an Verwaltungsdateien außerhalb des Verwaltungszweigs. Lokale Änderungen daran sind Experimente: markiert, sterblich, nie gemergt.
- Der Verwaltungszweig wird nie in einen anderen Zweig gemergt und von keinem anderen Zweig abgeleitet. Verteilung ausschließlich per `restore --source`.
- Der Abgleich überschreibt nur, was veraltet ist. Was neu ist, wird gemeldet.
- Der Release-Zweig ist kein Arbeitsort. In der Betriebsart `file-sync` wird er nie ausgecheckt und nie gemergt.
- Absicherungs-Commits einer Maschine erreichen den Entwicklungszweig nur in Menschenkörnung.
