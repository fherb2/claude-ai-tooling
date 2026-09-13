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
- **Mit Tiefenprüfung:** Lies `rules.md` im Ordner dieses Skills vollständig und arbeite sie ab. **Erst die Tiefenprüfung samt der Korrekturen, die aus ihr erwachsen — der Datei-Abgleich unten kommt zuletzt** (der allgemeine Fall davon steht im nächsten Abschnitt).

## Was in jedem Fall gilt

- **Befunde werden nach der Regel „Befundlisten abarbeiten" der Projekt-`CLAUDE.md` behandelt** — einzeln vorgelegt, nicht selbständig ausgeführt. Bevor etwas als Verstoß gemeldet wird, ist zusätzlich nachzusehen, ob es nicht ausdrücklich so festgelegt wurde.
- **Ein Checkpoint-Commit je Etappe**, nicht einer am Ende. Was auffällt, fällt oft erst zwei Etappen später auf.
- **Mit ausdrücklichen Pfaden committen, nie mit `git add -A`.** Läuft die Bash-Sandbox, hängt sie Attrappen in den Arbeitsbaum, die wie unversionierte Dateien aussehen und nicht lesbar sind; `files/find-sandbox-masks.sh` listet sie. Aus demselben Grund ist ein rekursives Prüfwerkzeug, das mit „Permission denied" abbricht, nicht zwangsläufig kaputt.
- **Vor jedem Commit, der Markdown einschließt**, die Tabellenprüfung des Skills `correct-zaaack-md-editor-mistakes` laufen lassen.
- **Blockiert die Bash-Sandbox einen Schritt, nicht versuchen, das zu umgehen.** Dem Entwickler melden, welche Operation ohne Sandbox nötig ist, und ihn bitten, sie kurzzeitig abzuschalten. Nach der Operation Bescheid geben, dass er sie wieder einschalten kann.
- **Der Datei-Abgleich ist der letzte Schritt einer Arbeitssitzung**, nicht einer von mehreren. Steht noch etwas offen, das den Entwicklungszweig ändert — eine Korrektur aus der Tiefenprüfung, ein offener Punkt aus dem Gespräch —, wird erst das erledigt. Sonst trägt der Release-Zweig zwei Commits, wo einer gereicht hätte. **Am 11. September 2026 genau so passiert:** Der Abgleich lief, danach wurden drei offene Punkte abgearbeitet, und sechs Dateien mussten hinterher nachgezogen werden. Gefunden hat das die zweifache Gegenprobe aus Schritt 4 — die ist deshalb keine Formalität.
- **Nicht pushen.** Der Push ist Sache des Nutzers, auch am Ende eines gelungenen Durchgangs.

---

# Der Datei-Abgleich

Ziel: Der Release-Zweig trägt jede Datei des Entwicklungszweigs, ausgenommen das, was dort bewusst fehlen soll. Kein Merge — die Zweige haben absichtlich getrennte Historien, übertragen wird Datei für Datei.

Die Namen der Zweige und die Liste der zentralen Dateien stehen in `.claude/git-worktree-model.json` (`integration_branch`, `release_branch`, `infra_files`). Im Folgenden `dev` und `master` genannt.

**Der Haupt-Checkout bleibt dabei durchgehend auf `dev`.** Das Worktree-Modell (Projekt-`CLAUDE.md`, Skill `parallel-sessions`) verbietet dem Skill, dort den Zweig zu wechseln oder zu committen — und das muss er auch nicht: `master` wird nie ausgecheckt, sondern per Git-Plumbing direkt auf Ebene der Objekte fortgeschrieben (`read-tree`/`update-index`/`write-tree`/`commit-tree`/`update-ref`, mit einer alternativen Index-Datei statt des Arbeitsbaums). Das ist kein Umweg, sondern die robustere Lösung: Sie berührt `.claude/skills/` nie und scheitert deshalb auch nicht an dessen Sandbox-Sperre.

**Vorher prüfen: `git worktree list`.** Anders als `git checkout` verweigert `git update-ref` nicht, wenn der Ziel-Branch gerade in einem anderen Worktree ausgecheckt ist — es bewegt den Ref trotzdem, und diese andere Sitzung säße danach auf einem veralteten Stand. Zeigt `master` dort auf, den Nutzer fragen, statt fortzufahren.

## Was im Release-Zweig fehlen soll

Drei Klassen, und sie sind keine Nachlässigkeit:

1. **Skills mit Baustellenschild im Ordnernamen** (`skills/🚧_…`, `skills/🚷_…`). Sie sind unfertig und bleiben es dort, wo sie stehen.
2. **Der Ordner `.research/`.** Untersuchungsmaterial, das den Release-Zweig nicht erreicht.
3. **Die Projekt-Skills unter `.claude/skills/`** — und damit dieser Skill selbst. Sie sind Arbeitsgerät des Entwicklungszweigs: Ein Werkzeug, das den Release-Zweig herstellt, hat in ihm nichts zu suchen. In `infra` ebenso nicht, dort liegen nur die fünf zentralen Dateien (Festlegung des Entwicklers vom 11. September 2026; Anweisung in der Projekt-CLAUDE.md).

**Alle drei Klassen stehen in `files/unfinished.py`** — dem einen Ort, aus dem sich jedes Werkzeug dieses Skills und der Filter der Gegenprobe bedienen. Die Baustellen werden nicht an einer Namensliste erkannt, sondern daran, dass der Ordnername unter `skills/` nicht mit einem alphanumerischen Zeichen beginnt — ein künftiges Schild fällt damit von selbst darunter. Bewusst breiter als „beginnt mit einem Emoji": Zu viel auszuschließen fällt auf, zu wenig auszuschließen bringt einen unfertigen Skill still in den Release. Beginnt ein ausgeschlossener Ordner mit einem Zeichen, das gar kein Schild ist (etwa `_alt-kram/`), sagt das Werkzeug das ausdrücklich, statt ihn stillschweigend zu schlucken. Die dritte Klasse hängt am Präfix `.claude/skills/` und nicht am Namen dieses Skills, damit ein künftiger zweiter Projekt-Skill ebenso von selbst darunterfällt.

**Eine neue Klasse ist zweiteilig.** Der Ausschluss selbst verhindert nur künftige Übertragungen — was von der neuen Klasse bereits auf `master` liegt, muss einmalig von Hand entfernt werden. Weder `branch-diff.py` noch die Gegenprobe melden das, weil beide genau diesen Pfad ausfiltern. Genau das ist am 11. September 2026 passiert, als diese dritte Klasse eingeführt wurde: Die acht Dateien dieses Skills lagen aus dem ersten Lauf schon auf `master` und mussten von Hand entfernt werden (Commit `373b142`).

## Schritt 1 — Infra verteilen, auf beide Zweige

**Zentrale Dateien kommen nie aus `dev`, sondern immer aus dem Infra-Zweig.** Sonst wandert eine Fassung weiter, die dort nie beschlossen wurde. Die maßgebliche Pfadliste ist `infra_files` aus der Modelldatei.

**Auf `dev`** — echter Dateizugriff auf den aktiven Arbeitsbaum:

```bash
git restore --source=infra -- .claude/CLAUDE.md .claude/settings.json .vscode/ .gitignore .markdownlint.jsonc
git add <dieselben Pfade> && git commit
```

Trifft das auf eine tatsächliche Abweichung bei einer sandbox-gesperrten Datei (`.claude/settings.json`), greift die allgemeine Sandbox-Regel oben.

**Auf `master`, ohne Checkout** — der Release-Zweig wird nie ausgecheckt, sein Tree stattdessen per Plumbing fortgeschrieben:

```bash
IDX=$(mktemp)
GIT_INDEX_FILE="$IDX" git read-tree master
git ls-tree -r infra -- .claude/CLAUDE.md .claude/settings.json .vscode/ .gitignore .markdownlint.jsonc \
  | GIT_INDEX_FILE="$IDX" git update-index --index-info
TREE=$(GIT_INDEX_FILE="$IDX" git write-tree)
COMMIT=$(git commit-tree "$TREE" -p master -m "Infra verteilen")
git update-ref refs/heads/master "$COMMIT"
rm -f "$IDX"
```

Gegenprobe je Zweig, ohne Checkout: `git diff --stat infra <zweig> -- <infra_files>` muss für beide leer sein.

## Schritt 2 — Den Vollvergleich erheben

```bash
python3 .claude/skills/repo-cleanup-pass/files/branch-diff.py --from dev --to master
```

Das Skript gibt vier Listen aus: zu übernehmen, im Release-Zweig zu löschen, bewusst ausgeschlossen, und die Infra-Dateien (die aus Schritt 1 kommen). Die beiden Arbeitslisten schreibt es NUL-getrennt in ein eigenes Verzeichnis, dessen Pfad es in der letzten Zeile als `LISTEN=…` nennt — NUL-getrennt, damit Pfade mit Leerzeichen und Emoji-Ordnernamen unbeschädigt bleiben. `--out` ist optional. Ohne Angabe landet dieses Verzeichnis unter dem System-Temp-Pfad (unter aktiver Sandbox also `$TMPDIR`) — der ausgegebene `LISTEN=`-Pfad ist in jedem Fall absolut und eindeutig.

**Diese Liste wird gelesen, nicht überflogen.** Ein Bereich, der im Release-Zweig vollständig fehlt, sieht darin genauso aus wie eine geänderte Einzeldatei — und genau das ist der Fund, für den der Vollvergleich existiert. Was auffällt, wird dem Nutzer vorgelegt, bevor übertragen wird.

## Schritt 3 — Übertragen

Auch dies ohne Checkout, direkt auf dem aktuellen Stand von `master` (nach Schritt 1 also inklusive Infra):

**Vorher: Arbeitsverzeichnis ist die Repo-Wurzel.** Die Listen aus Schritt 2 sind wurzelrelativ; von woanders aus laufen `git ls-tree`/`update-index` an den falschen Pfaden vorbei.

```bash
LISTEN=<Pfad aus Schritt 2>
IDX=$(mktemp)
GIT_INDEX_FILE="$IDX" git read-tree master
xargs -0 -r -a "$LISTEN/take.z" git ls-tree dev -- \
  | GIT_INDEX_FILE="$IDX" git update-index --index-info
xargs -0 -r -a "$LISTEN/dele.z" env GIT_INDEX_FILE="$IDX" git update-index --remove --force-remove --
TREE=$(GIT_INDEX_FILE="$IDX" git write-tree)
COMMIT=$(git commit-tree "$TREE" -p master -m "Datei-Abgleich")
git diff --stat master "$COMMIT"   # ansehen, dann erst den Ref bewegen
git update-ref refs/heads/master "$COMMIT"
rm -f "$IDX"
```

Eine Löschung im Release-Zweig ist Teil des Abgleichs, kein Sonderfall: Was in `dev` bewusst entfallen ist, hat dort ebenfalls nichts mehr zu suchen. Sie wird aber **benannt**, nicht nebenbei ausgeführt.

**`-r` ist kein Beiwerk:** Ohne es ruft `xargs` den Befehl auch bei leerer Liste einmal ohne Argumente auf — `git ls-tree dev --` ohne Pfad läse dann den ganzen Baum, `update-index --remove --force-remove --` ohne Pfad wäre dagegen harmlos, aber beides unbeabsichtigt. Eine leere Löschliste ist der Regelfall, nicht die Ausnahme.

**Eine Umbenennung ist im Abgleich zwei Vorgänge**, kein eigener dritter. `branch-diff.py` erhebt den Vergleich deshalb mit `--no-renames`: Der alte Name steht dann in der Löschliste, der neue in der Übernahmeliste. Wer die Listen mit einer unabhängigen Messung vergleicht, muss das wissen — `git diff --name-only` mit Umbenennungserkennung nennt **nur** den neuen Namen, zählt also einen Pfad weniger. Beide Zahlen sind richtig; sie beantworten verschiedene Fragen.

**Warum Plumbing statt Checkout:** `.claude/skills/` existiert nur auf `dev`. Ein `git checkout master` im Haupt-Checkout müsste die Skill-Dateien deshalb aus dem Arbeitsbaum entfernen — unter aktiver Bash-Sandbox ist genau das gesperrt („Das Dateisystem ist nur lesbar", beobachtet). Die Plumbing-Route arbeitet nur auf Ebene der Git-Objekte und einer alternativen Index-Datei, berührt `.claude/skills/` nie und bleibt deshalb auch mit aktiver Sandbox möglich. Sie verlässt nebenbei `dev` kein einziges Mal — die frühere Rückkehr auf den Entwicklungszweig (vormals Schritt 5) entfällt damit.

## Schritt 4 — Gegenprobe, und zwar zweifach

```bash
# 1. Es darf nur noch das Ausgeschlossene übrig sein -- alle DREI Klassen:
git -c core.quotepath=false diff --name-only master dev \
  | grep -v -E "$(python3 .claude/skills/repo-cleanup-pass/files/unfinished.py --release-regex)"
#    -> keine Ausgabe

# 2. Jede übertragene Datei byteweise vergleichen:
xargs -0 -r -n1 -a "$LISTEN/take.z" sh -c \
  'a=$(git show dev:"$1" | sha256sum); b=$(git show master:"$1" | sha256sum); [ "$a" = "$b" ] || echo "ABWEICHUNG: $1"' _
#    -> keine Ausgabe
```

Die erste Probe fängt Vergessenes, die zweite einen misslungenen Übertrag. Beide gehören dazu; die erste allein sagt nur, dass ein Pfad existiert, nicht dass er stimmt.

**Der Pfad wandert in der zweiten Probe als Positionsparameter (`$1`) in die Shell, nicht als Text (`{}`) in den Befehl.** Enthält ein Pfad ein `"` oder ein `$`, setzt `-I{}` das roh in den Shell-Code ein — geprüft: Ein Anführungszeichen im Dateinamen bricht die Probe mit einem Syntaxfehler ab, statt den Pfad zu melden.

**Der Filter der ersten Probe bezieht sein Muster aus `files/unfinished.py`**, dem einen Ort, an dem sämtliche Ausschlussklassen dieses Skills stehen — die Werkzeuge lesen es dort ebenfalls. **Wer eine Klasse ergänzt, ergänzt genau diese eine Stelle** (und die Aufzählung oben, die sie für den Leser erklärt). Früher stand dasselbe Muster dreifach im Ordner; blieb eine Kopie zurück, meldete die Probe die neu ausgeschlossenen Dateien als Vergessenes — ein Fehlalarm, der wie ein misslungener Abgleich aussieht.

**`core.quotepath=false` ist in der ersten Probe nicht Kosmetik.** Ohne diese Angabe setzt Git Pfade mit Nicht-ASCII-Zeichen in Anführungszeichen — die Zeile beginnt dann mit `"` statt mit `skills/`, der Ausschlussfilter greift nicht, und die Probe meldet **alle** Baustellen-Skills als unerwartet. Beim ersten Lauf dieses Skills ist genau das passiert: 25 Fehlalarme, die wie ein misslungener Abgleich aussahen.

## Abschluss

Der Haupt-Checkout stand während des ganzen Durchgangs auf `dev` und bleibt dort — ein Zurückwechseln entfällt. Dem Nutzer den Stand melden: welche Zweige wie viele Commits vor ihrem Remote liegen, und dass nichts gepusht ist.
