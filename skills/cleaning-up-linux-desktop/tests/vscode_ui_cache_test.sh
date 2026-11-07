#!/usr/bin/env bash
# Test: delete the HTTP cache entries of the VS Code desktop UI (Cache/Cache_Data)
# and the CachedData folders of other VS Code versions while VS Code is running,
# and observe how VS Code reacts. WebStorage/CacheStorage is NOT touched.
# Also records processes and temp artifacts before, during and after to see
# whether anything is left behind. Run as normal user.

set -u

readonly LOG=/tmp/vscode_ui_cache_test.log
readonly STATE=/tmp/vscode_ui_cache_test_state
readonly WAIT=90
readonly CFG="$HOME/.config/Code"
readonly DATA="$CFG/Cache/Cache_Data"
readonly CACHED="$CFG/CachedData"
readonly WEBSTORAGE="$CFG/WebStorage"

log() { echo "$@" | tee -a "$LOG"; }

COMMIT=$(python3 -I -c "import json;print(json.load(open('/usr/share/code/resources/app/product.json'))['commit'])" 2>/dev/null)
readonly COMMIT
if [ -z "$COMMIT" ] || [ ! -d "$DATA" ] || [ ! -d "$CACHED" ]; then
    echo "Installierte VS-Code-Version oder Cache-Ordner nicht gefunden. Abbruch."
    exit 1
fi

# Entry files have names like 0123456789abcdef_0 or ..._s (16 hex characters).
entries_list() { /usr/bin/find "$DATA" -mindepth 1 -maxdepth 1 -type f -name '????????????????_*' -printf '%f\n' | sort; }

# VS Code related processes: pid, age, command, start of the arguments.
procs() {
    ps -eo pid=,etimes=,comm=,args= | awk '
        $3!="ps" && $3!="awk" && $3!="bash" && $3!="sh" && $3!="sort" && $3!="grep" && $3!="tee" &&
        ($3=="code" || $0 ~ /\/usr\/share\/code\/|vscode-server|\.vscode\//) {
            printf "%s %ss %s %s\n", $1, $2, $3, substr($0, index($0, $4), 90)
        }'
}

# Temp artifacts of VS Code outside the cache folders.
leftovers() {
    echo "/tmp:"; ls -1A /tmp | grep -i -E 'vscode|^code' | grep -v -E '^vscode_(ui_)?cache_test' | sed 's/^/  /'
    echo "/run/user/$(id -u):"; ls -1A "/run/user/$(id -u)" 2>/dev/null | grep -i -E 'vscode|^code' | sed 's/^/  /'
    echo "Singleton-/Lock-Dateien in ~/.config/Code:"; ls -1A "$CFG" | grep -i -E 'singleton|lock' | sed 's/^/  /'
}

artifacts() {
    local label="$1" file="$STATE/art_$1.txt"
    {
        echo "Prozesse:"; procs | sed 's/^/  /'
        leftovers
    } > "$file"
    {
        echo
        echo "--- Artefakte: $label ($(date '+%T')) ---"
        cat "$file"
    } | tee -a "$LOG"
    # Normalized copy without pid and age for comparison.
    { procs | cut -d' ' -f3-; leftovers; } | sort > "$STATE/artn_$label.txt"
}

compare_artifacts() {
    local label="$1" base="$2"
    echo "Unterschied zu '$base' ('<' vorher, '>' jetzt):" | tee -a "$LOG"
    if diff "$STATE/artn_$base.txt" "$STATE/artn_$label.txt" | tee -a "$LOG" | grep -q .; then :; else
        log "  (keine Unterschiede)"
    fi
}

snapshot() {
    local label="$1" list="$STATE/$1.list"
    entries_list > "$list"
    {
        echo
        echo "--- Zustand: $label ($(date '+%T')) ---"
        echo "Entry-Dateien in Cache_Data: $(wc -l < "$list"), Groesse: $(du -sh "$DATA" | cut -f1)"
        echo "index: $(stat -c '%s Bytes, geaendert %y' "$DATA/index" 2>/dev/null || echo fehlt)"
        echo "the-real-index: $(stat -c '%s Bytes, geaendert %y' "$DATA/index-dir/the-real-index" 2>/dev/null || echo fehlt)"
        echo "Weitere Dateien in Cache_Data (keine Entries): $(ls -1A "$DATA" | grep -v -E '^[0-9a-f]{16}_' | tr '\n' ' ')"
        echo "CachedData (Aktuelle Version: ${COMMIT:0:8}):"
        for d in "$CACHED"/*/; do echo "  $(basename "$d" | cut -c1-8)  $(du -sh "$d" | cut -f1)"; done
        echo "WebStorage gesamt (soll unveraendert bleiben): $(du -s "$WEBSTORAGE" | cut -f1) KiB"
        echo "VS Code laeuft: $(pgrep -x code >/dev/null && echo ja || echo nein)"
    } | tee -a "$LOG"
}

compare() {
    local label="$1" prev="$2" list="$STATE/$1.list"
    local new same
    new=$(comm -13 "$STATE/$prev.list" "$list" | wc -l)
    same=$(comm -12 "$STATE/before.list" "$list" | wc -l)
    {
        echo "Neu seit '$prev': $new Dateien"
        echo "Davon mit gleichem Namen wie eine der geloeschten Dateien (gleiche Ressource neu im Cache): $same"
    } | tee -a "$LOG"
}

observe() {
    local note
    read -r -p "Deine Beobachtung in VS Code (eine Zeile, Enter fuer keine): " note
    log "Beobachtung: ${note:-(keine)}"
}

countdown() {
    local i
    for ((i = ${1:-$WAIT}; i > 0; i--)); do
        printf '\r  warte %d s ...' "$i"
        sleep 1
    done
    printf '\r                \r'
}

if [ -e "$LOG" ] || [ -e "$STATE" ]; then
    echo "Reste eines frueheren Laufs vorhanden ($LOG, $STATE). Bitte vorher wegraeumen."
    exit 1
fi
mkdir -p "$STATE"

log "VS-Code-Cache-Test $(date '+%F %T')"
log "Installierte Version: $COMMIT"

echo
echo "=== Ausgangslage: VS Code sollte jetzt NICHT laufen ==="
artifacts baseline
if pgrep -x code >/dev/null; then
    echo "Achtung: VS Code laeuft bereits. Bitte beenden (Strg+Q), dann hier Enter."
    read -r -p "Enter, wenn VS Code beendet ist. "
    artifacts baseline-after-quit
    cp "$STATE/artn_baseline-after-quit.txt" "$STATE/artn_baseline.txt"
fi

echo
echo "=== Jetzt VS Code starten und einen Ordner oeffnen (zum Beispiel ein Projekt) ==="
read -r -p "Enter, wenn VS Code offen ist und alles geladen hat. "
if ! pgrep -x code >/dev/null; then
    echo "VS Code laeuft nicht. Abbruch."
    exit 1
fi
artifacts running
snapshot before

echo
echo "Gleich werden geloescht:"
echo "  - ALLE Entry-Dateien in $DATA (index und index-dir bleiben)"
echo "  - alle Ordner in $CACHED ausser der aktuellen Version ${COMMIT:0:8}"
echo "WebStorage (mit CacheStorage) wird nicht angefasst."
read -r -p "Enter zum Start, Strg+C zum Abbrechen. "

deleted=$(/usr/bin/find "$DATA" -mindepth 1 -maxdepth 1 -type f -name '????????????????_*' -print -delete | wc -l)
old=$(/usr/bin/find "$CACHED" -mindepth 1 -maxdepth 1 -type d ! -name "$COMMIT" | wc -l)
/usr/bin/find "$CACHED" -mindepth 1 -maxdepth 1 -type d ! -name "$COMMIT" -exec rm -rf {} +
log
log ">>> $(date '+%T'): $deleted Cache-Dateien und $old CachedData-Ordner geloescht."
snapshot after-delete

echo
echo "=== Schritt 1: Erweiterungsansicht (Strg+Shift+X) oeffnen, im Marketplace suchen, einen Eintrag oeffnen ==="
read -r -p "Enter druecken, dann in VS Code arbeiten. Danach wird $WAIT s gewartet. "
countdown
snapshot step1
compare step1 after-delete
observe

echo
echo "=== Schritt 2: eine Ansicht oeffnen, die vorher nicht offen war (zum Beispiel Einstellungen, Willkommensseite oder eine Markdown-Vorschau) ==="
read -r -p "Enter druecken, dann in VS Code arbeiten. Danach wird $WAIT s gewartet. "
countdown
snapshot step2
compare step2 step1
observe

echo
echo "=== Schritt 3: Fenster neu laden (Strg+Shift+P, 'Developer: Reload Window'), dann die Erweiterungsansicht aus Schritt 1 wieder oeffnen ==="
read -r -p "Enter druecken, dann in VS Code arbeiten. Danach wird $WAIT s gewartet. "
countdown
snapshot step3
compare step3 step2
observe
artifacts after-steps

echo
echo "=== Schritt 4: VS Code vollstaendig beenden (Strg+Q, alle Fenster) ==="
read -r -p "Enter druecken, dann beenden. Danach wird 20 s gewartet. "
countdown 20
artifacts after-quit
compare_artifacts after-quit baseline

echo
echo "=== Schritt 5: VS Code normal neu starten, Ordner oeffnen, danach wieder beenden ==="
read -r -p "Enter druecken, dann starten, kurz arbeiten, beenden. Danach wird 20 s gewartet. "
countdown 20
snapshot after-restart
artifacts after-restart
compare_artifacts after-restart baseline
observe

log
log "Ende $(date '+%T'). Protokoll: $LOG"
