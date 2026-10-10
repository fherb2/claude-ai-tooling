---
name: stignore-release
description: Übernimmt eine geänderte Syncthing-Ausschlussliste (.stignore) aus ~/.claude in das Vorhaben home-.claude-sharing und liefert sie aus — Kopie nach files/, Datumszeilen der READMEs, neue Download-Pakete samt loser downloads/.stignore, Commit und Übertragung in den master. Verwenden, sobald der Nutzer meldet, er habe seine .stignore geändert oder ein neues Muster eingetragen, etwa "ich hab die .stignore erweitert, übernimm das" oder "die neue stignore muss ins Projekt". Gilt nur für dieses Repository.
---

# Ausschlussliste übernehmen und ausliefern

Der Normalfall: Bei einer Konfliktlösung ist in `~/.claude/.stignore` ein Muster hinzugekommen, samt Begründung als Kommentar. Diese Fassung soll ins Repo und von dort an alle Rechner. Die mechanische Arbeit erledigt `home-.claude-sharing/scripts/release_stignore.sh`; dieser Skill legt den Ablauf darum herum fest.

Die Begründungen der Muster stehen als Kommentare in der Liste selbst. Sie in Kapitel 3.9 der Implementierungsdoku nachzutragen, ist **nicht** Teil dieses Ablaufs.

## Ablauf

1. **Vorschau.** `home-.claude-sharing/scripts/release_stignore.sh --dry-run` ausführen — ohne Argument liest es `~/.claude/.stignore`. Dem Nutzer die hinzugekommenen und entfallenen Muster zeigen. Liegt die neue Fassung woanders, ihren Pfad als Argument übergeben und vorher beim Nutzer bestätigen lassen.
   - **Schutzprüfung verweigert:** Die Meldung wörtlich weitergeben und anhalten. Die Quelldatei gehört dem Nutzer; repariere sie nicht selbst.
   - **„Unveraendert":** nichts zu tun, dem Nutzer melden.
2. **Übernehmen.** Dasselbe ohne `--dry-run`. Das Skript kopiert nach `files/.stignore`, setzt beide Datumszeilen auf heute und ruft `pack_packages.sh` auf. Dessen Ergebnis muss „Alle Pruefungen bestanden." lauten; eine Abweichung wörtlich melden und anhalten.
3. **Tabellenprüfung** der geänderten Markdown-Dateien auf Editor-Artefakte, wie vor jedem Commit mit Markdown.
4. **Commit auf `dev`** mit ausdrücklichen Pfaden, nie `git add -A`. Betroffen sind genau: `home-.claude-sharing/files/.stignore`, `README.md`, `README.en.md`, `downloads/.stignore` und die beiden `downloads/claude-sync-watch_*_local.zip` (alle unter `home-.claude-sharing/`). Im Commit-Text die neuen Muster nennen.
5. **Übertragung in den `master` — nur nach Freigabe des Nutzers.** Genau die Dateien dieses Commits, ohne `master` auszuchecken (der Release-Zweig ist kein Arbeitsort). Vorher `git worktree list`: Steht `master` in einem anderen Worktree, fragen statt fortfahren. Aus der Repo-Wurzel:

   ```bash
   FILES="<die Pfade aus Schritt 4>"
   IDX=$(mktemp -p "${TMPDIR:-/tmp}")
   GIT_INDEX_FILE="$IDX" git read-tree master
   git ls-tree dev -- $FILES | GIT_INDEX_FILE="$IDX" git update-index --index-info
   TREE=$(GIT_INDEX_FILE="$IDX" git write-tree)
   COMMIT=$(git commit-tree "$TREE" -p master -m "Datei-Abgleich: home-.claude-sharing (.stignore)")
   git diff --stat master "$COMMIT"     # ansehen, dann erst den Ref bewegen
   git update-ref refs/heads/master "$COMMIT"
   rm -f "$IDX"
   ```

   Gegenprobe: jede dieser Dateien per `sha256sum` von `git show dev:<pfad>` und `git show master:<pfad>` vergleichen; außerdem muss `git diff --name-only master dev -- home-.claude-sharing` leer sein. Ist es das nicht, lagen schon vorher Unterschiede vor — dem Nutzer nennen, nicht mitübertragen.
6. **Nicht pushen.** Den Befehl nennen: `git -C <repo> push origin dev master`.

## Was Du am Ende meldest

- die neuen und entfallenen Muster, das neue Datum, das Ergebnis der Paketprüfung, die beiden Commits;
- **die Verteilung, die noch aussteht:** Die Liste wandert nicht mit. Auf jedem Rechner ist die lose Datei nach `~/.claude-sync-watch/` und `~/.claude/` zu kopieren (Befehl in der README des Vorhabens, Abschnitt „Nur die Ausschlussliste aktualisieren"), danach den Ordner in Syncthing neu einlesen lassen. Am Knoten wird der Inhalt im Reiter *Ignore Patterns* ersetzt.
