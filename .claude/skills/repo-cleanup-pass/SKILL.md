---
name: repo-cleanup-pass
description: Bringt den Release-Zweig dieses Repositories auf den Stand des Entwicklungszweigs — entweder als reinen Datei-Abgleich oder mit vorgeschalteter Tiefenprüfung über READMEs, Sprachfassungen, Datumszeilen und Download-Pakete. Verwenden, wenn ein Vorhaben abgeschlossen ist und in den master soll, wenn der master nachgezogen werden muss, oder wenn zu prüfen ist, ob beim stückweisen Übertragen etwas liegengeblieben ist. Gilt nur für dieses Repository.
---

# Abgleich- und Aufräumdurchgang für dieses Repository

Dieser Durchgang hat zwei Tiefen, und die Wahl trifft der Nutzer.

## Zuerst fragen, dann arbeiten

**Stelle dem Nutzer diese Frage und warte auf seine Antwort:**

> Soll der Durchgang nur die Dateien abgleichen, die in `dev` neu oder verändert sind — oder vorher eine Tiefenprüfung über die Inhalte der Bereiche laufen, insbesondere über die READMEs, die Sprachfassungen und die Zip-Pakete?

- **Nur Datei-Abgleich:** Alles, was zu tun ist, steht unten in diesem Dokument. **Lade `rules.md` nicht** — sie enthält nichts, was für diesen Fall gebraucht wird, und kostet nur Kontext.
- **Mit Tiefenprüfung:** Lies `rules.md` im Ordner dieses Skills vollständig und arbeite sie ab. **Die Reihenfolge ist festgelegt: erst die Tiefenprüfung samt der Korrekturen, die aus ihr erwachsen — der Datei-Abgleich unten kommt zuletzt.** Andernfalls überträgst du einen Stand, den du gleich danach korrigierst, und der Release-Zweig trägt zwei Commits, wo einer gereicht hätte.

## Was in jedem Fall gilt

- **Jeder Befund wird einzeln vorgelegt**, nicht selbständig ausgeführt. Das gilt auch dann, wenn der Auftrag allgemein erteilt war: Der Durchgang findet regelmäßig mehr, als der Nutzer erwartet hat.
- **Nicht voraussetzen, dass die dem Befund gegenüberstehende Stelle recht hat.** Mehrfach lag der Fehler auf der anderen Seite. Bevor etwas als Verstoß gemeldet wird, ist nachzusehen, ob es nicht ausdrücklich so festgelegt wurde.
- **Ein Checkpoint-Commit je Etappe**, nicht einer am Ende. Was auffällt, fällt oft erst zwei Etappen später auf.
- **Mit ausdrücklichen Pfaden committen, nie mit `git add -A`.** Läuft die Bash-Sandbox, hängt sie Attrappen in den Arbeitsbaum, die wie unversionierte Dateien aussehen und nicht lesbar sind; `files/find-sandbox-masks.sh` listet sie. Aus demselben Grund ist ein rekursives Prüfwerkzeug, das mit „Permission denied" abbricht, nicht zwangsläufig kaputt.
- **Vor jedem Commit, der Markdown einschließt**, die Tabellenprüfung des Skills `correct-zaaack-md-editor-mistakes` laufen lassen.
- **Nicht pushen.** Der Push ist Sache des Nutzers, auch am Ende eines gelungenen Durchgangs.

---

# Der Datei-Abgleich

Ziel: Der Release-Zweig trägt jede Datei des Entwicklungszweigs, ausgenommen das, was dort bewusst fehlen soll. Kein Merge — die Zweige haben absichtlich getrennte Historien, übertragen wird Datei für Datei.

Die Namen der Zweige und die Liste der zentralen Dateien stehen in `.claude/git-worktree-model.json` (`integration_branch`, `release_branch`, `infra_files`). Im Folgenden `dev` und `master` genannt.

## Was im Release-Zweig fehlen soll

Zwei Klassen, und sie sind keine Nachlässigkeit:

1. **Skills mit Baustellenschild im Ordnernamen** (`skills/🚧_…`, `skills/🚷_…`). Sie sind unfertig und bleiben es dort, wo sie stehen.
2. **Der Ordner `.research/`.** Untersuchungsmaterial, das den Release-Zweig nicht erreicht.

`files/branch-diff.py` kennt beide Klassen als Vorgabe. Erkannt werden sie nicht an einer Namensliste, sondern daran, dass der Ordnername unter `skills/` nicht mit einem alphanumerischen Zeichen beginnt — ein künftiges Schild fällt damit von selbst darunter.

## Schritt 1 — Infra verteilen, auf beide Zweige

**Zentrale Dateien kommen nie aus `dev`, sondern immer aus dem Infra-Zweig.** Sonst wandert eine Fassung weiter, die dort nie beschlossen wurde.

```bash
# auf dev, dann ebenso auf master:
git restore --source=infra -- .claude/CLAUDE.md .claude/settings.json .vscode/ .gitignore .markdownlint.jsonc
git add <dieselben Pfade> && git commit
```

Die maßgebliche Pfadliste ist `infra_files` aus der Modelldatei, nicht die obige Zeile. Ändert sich dort etwas, gilt die Datei.

Gegenprobe je Zweig: `git diff --stat infra <zweig> -- <infra_files>` muss leer sein.

## Schritt 2 — Den Vollvergleich erheben

```bash
python3 .claude/skills/repo-cleanup-pass/files/branch-diff.py --from dev --to master
```

Das Skript gibt vier Listen aus: zu übernehmen, im Release-Zweig zu löschen, bewusst ausgeschlossen, und die Infra-Dateien (die aus Schritt 1 kommen). Die beiden Arbeitslisten schreibt es NUL-getrennt in ein eigenes Verzeichnis, dessen Pfad es in der letzten Zeile als `LISTEN=…` nennt — NUL-getrennt, damit Pfade mit Leerzeichen und Emoji-Ordnernamen unbeschädigt bleiben. **Nicht `$TMPDIR` verwenden:** Die Variable existiert nur, solange die Sandbox läuft.

**Diese Liste wird gelesen, nicht überflogen.** Ein Bereich, der im Release-Zweig vollständig fehlt, sieht darin genauso aus wie eine geänderte Einzeldatei — und genau das ist der Fund, für den der Vollvergleich existiert. Was auffällt, wird dem Nutzer vorgelegt, bevor übertragen wird.

## Schritt 3 — Übertragen

```bash
LISTEN=<Pfad aus Schritt 2>
git checkout master
xargs -0 -r -a "$LISTEN/take.z" git checkout dev --
xargs -0 -r -a "$LISTEN/dele.z" git rm -q --
git diff --cached --stat        # ansehen, dann committen
git commit
```

Eine Löschung im Release-Zweig ist Teil des Abgleichs, kein Sonderfall: Was in `dev` bewusst entfallen ist, hat dort ebenfalls nichts mehr zu suchen. Sie wird aber **benannt**, nicht nebenbei ausgeführt.

**`-r` ist kein Beiwerk:** Ohne es ruft `xargs` den Befehl auch bei leerer Liste einmal ohne Argumente auf, und `git rm --` ohne Pfad bricht mit `fatal: No pathspec given` ab. Eine leere Löschliste ist der Regelfall, nicht die Ausnahme.

**Eine Umbenennung ist im Abgleich zwei Vorgänge**, kein eigener dritter. `branch-diff.py` erhebt den Vergleich deshalb mit `--no-renames`: Der alte Name steht dann in der Löschliste, der neue in der Übernahmeliste. Wer die Listen mit einer unabhängigen Messung vergleicht, muss das wissen — `git diff --name-only` mit Umbenennungserkennung nennt **nur** den neuen Namen, zählt also einen Pfad weniger. Beide Zahlen sind richtig; sie beantworten verschiedene Fragen.

**Bekannte Bedingung: `.claude/skills/` ist unter aktiver Sandbox nur lesbar.** Enthält die Übertragungsliste Dateien von dort — etwa diesen Skill selbst —, bricht `git checkout` sie mit „Das Dateisystem ist nur lesbar" ab. Der Index bekommt den richtigen Inhalt trotzdem; nur der Arbeitsbaum lässt sich nicht schreiben. Zwei Wege:

- **Sauber:** die Sandbox für den Übertrag abschalten, dann greift nichts ein.
- **Wenn sie an bleibt:** vor dem Commit ausdrücklich prüfen, dass Index und Arbeitsbaum übereinstimmen und der Index den Stand des Quellzweigs trägt — `git diff --name-only` (unversionierte Abweichungen, muss leer sein) und je Pfad `git show dev:<pfad>` gegen `git show :<pfad>`. Stimmt beides, ist der Commit vollständig; das war beim ersten Lauf so, **weil** dort dieselben Dateien schon auf der Platte lagen. Verlangte der Übertrag an dieser Stelle einen *anderen* Inhalt, bliebe er unvollständig — dann hilft nur der erste Weg.

## Schritt 4 — Gegenprobe, und zwar zweifach

```bash
# 1. Es darf nur noch das Ausgeschlossene übrig sein:
git -c core.quotepath=false diff --name-only master dev | grep -v -E '^skills/[^A-Za-z0-9]|^\.research/'
#    -> keine Ausgabe

# 2. Jede übertragene Datei byteweise vergleichen:
xargs -0 -r -a "$LISTEN/take.z" -I{} sh -c \
  'a=$(git show dev:"{}" | sha256sum); b=$(git show master:"{}" | sha256sum); [ "$a" = "$b" ] || echo "ABWEICHUNG: {}"'
#    -> keine Ausgabe
```

Die erste Probe fängt Vergessenes, die zweite einen misslungenen Übertrag. Beide gehören dazu; die erste allein sagt nur, dass ein Pfad existiert, nicht dass er stimmt.

**`core.quotepath=false` ist in der ersten Probe nicht Kosmetik.** Ohne diese Angabe setzt Git Pfade mit Nicht-ASCII-Zeichen in Anführungszeichen — die Zeile beginnt dann mit `"` statt mit `skills/`, der Ausschlussfilter greift nicht, und die Probe meldet **alle** Baustellen-Skills als unerwartet. Beim ersten Lauf dieses Skills ist genau das passiert: 25 Fehlalarme, die wie ein misslungener Abgleich aussahen.

## Schritt 5 — Zurück auf den Entwicklungszweig

`git checkout dev`, damit die nächste Sitzung nicht versehentlich im Release-Zweig arbeitet. Dann dem Nutzer den Stand melden: welche Zweige wie viele Commits vor ihrem Remote liegen, und dass nichts gepusht ist.
