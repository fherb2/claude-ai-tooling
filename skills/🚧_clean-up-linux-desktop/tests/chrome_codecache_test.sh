#!/usr/bin/env bash
# Test: delete all entry files in Chrome's "Code Cache/js" while Chrome is
# running (index, index-dir and directories are kept) and observe how Chrome
# reacts. Only cache files of the current user are touched. Run as normal user.

set -u

readonly LOG=/tmp/chrome_codecache_test.log
readonly STATE=/tmp/chrome_codecache_test_state
readonly WAIT=90

log() { echo "$@" | tee -a "$LOG"; }

# Pick the js directory with the most entry files (the real profile, not "System Profile").
DATA=""
best=0
for dir in "$HOME"/.cache/google-chrome/*/"Code Cache"/js; do
    [ -f "$dir/index" ] || continue
    count=$(/usr/bin/find "$dir" -mindepth 1 -maxdepth 1 -type f -name '????????????????_*' | wc -l)
    if [ "$count" -gt "$best" ]; then
        best=$count
        DATA=$dir
    fi
done
if [ -z "$DATA" ] || [ ! -d "$DATA" ]; then
    echo "Kein 'Code Cache/js' mit index gefunden. Abbruch."
    exit 1
fi
readonly DATA
readonly WASM="$(dirname "$DATA")/wasm"

# Entry files have names like 0123456789abcdef_0 or ..._s (16 hex characters).
entries_list() { /usr/bin/find "$DATA" -mindepth 1 -maxdepth 1 -type f -name '????????????????_*' -printf '%f\n' | sort; }

snapshot() {
    local label="$1" list="$STATE/$1.list"
    entries_list > "$list"
    {
        echo
        echo "--- Zustand: $label ($(date '+%T')) ---"
        echo "Entry-Dateien in js: $(wc -l < "$list"), Groesse js: $(du -sh "$DATA" | cut -f1)"
        echo "index: $(stat -c '%s Bytes, geaendert %y' "$DATA/index" 2>/dev/null || echo fehlt)"
        echo "index-dir: $(ls -1A "$DATA/index-dir" 2>/dev/null | tr '\n' ' ')"
        echo "the-real-index: $(stat -c '%s Bytes, geaendert %y' "$DATA/index-dir/the-real-index" 2>/dev/null || echo fehlt)"
        echo "Weitere Dateien in js (keine Entries): $(ls -1A "$DATA" | grep -v -E '^[0-9a-f]{16}_' | tr '\n' ' ')"
        echo "Inhalt Code Cache/: $(ls -1A "$(dirname "$DATA")" | tr '\n' ' ')"
        echo "wasm (nicht angefasst): $(ls -1A "$WASM" 2>/dev/null | wc -l) Dateien"
        echo "Chrome laeuft: $(pgrep -x chrome >/dev/null && echo ja || echo nein)"
    } | tee -a "$LOG"
}

# Compare a snapshot with the previous one and with the files deleted at the start.
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
    read -r -p "Deine Beobachtung in Chrome (eine Zeile, Enter fuer keine): " note
    log "Beobachtung: ${note:-(keine)}"
}

countdown() {
    local i
    for ((i = WAIT; i > 0; i--)); do
        printf '\r  warte %d s ...' "$i"
        sleep 1
    done
    printf '\r                \r'
}

if [ -e "$LOG" ] || [ -e "$STATE" ]; then
    echo "Reste eines frueheren Laufs vorhanden ($LOG, $STATE). Bitte vorher wegraeumen."
    exit 1
fi
if ! pgrep -x chrome >/dev/null; then
    echo "Chrome laeuft nicht. Der Test braucht einen laufenden Chrome mit einigen offenen Seiten."
    exit 1
fi
mkdir -p "$STATE"

log "Chrome-Code-Cache-Test $(date '+%F %T')"
log "Cache-Ordner: $DATA"
snapshot before

echo
echo "Gleich werden ALLE Entry-Dateien in '$DATA' geloescht."
echo "Die Ordner, die Datei index und der Ordner index-dir bleiben stehen; wasm wird nicht angefasst."
read -r -p "Enter zum Start, Strg+C zum Abbrechen. "

deleted=$(/usr/bin/find "$DATA" -mindepth 1 -maxdepth 1 -type f -name '????????????????_*' -print -delete | wc -l)
log
log ">>> $(date '+%T'): $deleted Dateien in 'Code Cache/js' geloescht."
snapshot after-delete

echo
echo "=== Schritt 1: eine bereits geoeffnete JavaScript-lastige Seite (zum Beispiel das WordPress-Dashboard) mit F5 neu laden ==="
echo "    (nur F5, nicht Strg+F5: Strg+F5 umgeht den Cache)"
read -r -p "Enter druecken, dann in Chrome F5 und auf der Seite arbeiten (einloggen, Seiten wechseln). Danach wird $WAIT s gewartet. "
countdown
snapshot step1
compare step1 after-delete
observe

echo
echo "=== Schritt 2: eine Seite oeffnen, die heute noch nicht offen war (zum Beispiel den Beitrags-Editor oder die Plugin-Seite) ==="
echo "    (prueft, ob der Code Cache ueberhaupt noch neue Eintraege speichert)"
read -r -p "Enter druecken, dann in Chrome die Seite oeffnen und darauf arbeiten. Danach wird $WAIT s gewartet. "
countdown
snapshot step2
compare step2 step1
observe

echo
echo "=== Schritt 3: die Seite aus Schritt 1 noch einmal mit F5 neu laden ==="
echo "    (prueft, ob die neu geschriebenen Eintraege benutzt werden)"
read -r -p "Enter druecken, dann in Chrome F5 und auf der Seite arbeiten. Danach wird $WAIT s gewartet. "
countdown
snapshot step3
compare step3 step2
observe

log
log "Ende $(date '+%T'). Protokoll: $LOG"
log "Nach dem Test bitte noch: Chrome beenden, neu starten, eine Seite laden; dann melden."
