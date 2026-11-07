#!/usr/bin/env bash
# Test: delete all files in Firefox's cache2/entries while Firefox is running
# (index and directories are kept) and observe how Firefox reacts.
# Only cache files of the current user are touched. Run as normal user.

set -u

readonly LOG=/tmp/firefox_cache_test.log
readonly STATE=/tmp/firefox_cache_test_state
readonly WAIT=5

log() { echo "$@" | tee -a "$LOG"; }

# Pick the cache2 directory whose index was written most recently (active profile).
CACHE2=$(ls -1td "$HOME"/.cache/mozilla/firefox/*/cache2/index 2>/dev/null | head -1)
CACHE2=${CACHE2%/index}
if [ -z "$CACHE2" ] || [ ! -d "$CACHE2/entries" ]; then
    echo "Kein cache2 mit entries gefunden. Abbruch."
    exit 1
fi
readonly CACHE2
readonly ENTRIES="$CACHE2/entries"

snapshot() {
    local label="$1" list="$STATE/$1.list"
    ls -1 "$ENTRIES" | sort > "$list"
    {
        echo
        echo "--- Zustand: $label ($(date '+%T')) ---"
        echo "Dateien in entries: $(wc -l < "$list"), Groesse: $(du -sh "$ENTRIES" | cut -f1)"
        echo "index: $(stat -c '%s Bytes, geaendert %y' "$CACHE2/index")"
        echo "Inhalt cache2: $(ls -1A "$CACHE2" | tr '\n' ' ')"
        echo "Dateien in doomed: $(ls -1A "$CACHE2/doomed" 2>/dev/null | wc -l)"
        echo "Inhalt des Profil-Cacheordners: $(ls -1A "$(dirname "$CACHE2")" | grep -i -E 'cache2|trash' | tr '\n' ' ')"
        echo "Firefox laeuft: $(pgrep -x firefox >/dev/null && echo ja || echo nein)"
    } | tee -a "$LOG"
}

# Compare a snapshot with the list of files deleted at the start.
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
    read -r -p "Deine Beobachtung in Firefox (eine Zeile, Enter fuer keine): " note
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
if ! pgrep -x firefox >/dev/null; then
    echo "Firefox laeuft nicht. Der Test braucht einen laufenden Firefox mit einigen offenen Seiten."
    exit 1
fi
mkdir -p "$STATE"

log "Firefox-Cache-Test $(date '+%F %T')"
log "Cache-Ordner: $CACHE2"
snapshot before

echo
echo "Gleich werden ALLE Dateien in $ENTRIES geloescht."
echo "Ordner cache2, entries, doomed und die Datei index bleiben stehen."
read -r -p "Enter zum Start, Strg+C zum Abbrechen. "

deleted=$(/usr/bin/find "$ENTRIES" -mindepth 1 -maxdepth 1 -type f -print -delete | wc -l)
log
log ">>> $(date '+%T'): $deleted Dateien in entries geloescht."
snapshot after-delete

echo
echo "=== Schritt 1: eine bereits geoeffnete Seite mit F5 neu laden ==="
echo "    (nur F5, nicht Strg+F5: Strg+F5 umgeht den Cache)"
read -r -p "Enter druecken, dann sofort in Firefox F5. Danach wird $WAIT s gewartet. "
countdown
snapshot step1
compare step1 after-delete
observe

echo
echo "=== Schritt 2: eine Seite oeffnen, die heute noch nicht offen war ==="
echo "    (prueft, ob der Cache ueberhaupt noch neue Eintraege speichert)"
read -r -p "Enter druecken, dann sofort in Firefox die Seite oeffnen. "
countdown
snapshot step2
compare step2 step1
observe

echo
echo "=== Schritt 3: die Seite aus Schritt 1 noch einmal mit F5 neu laden ==="
echo "    (prueft, ob die neu geschriebenen Eintraege benutzt werden)"
read -r -p "Enter druecken, dann sofort in Firefox F5. "
countdown
snapshot step3
compare step3 step2
observe

log
log "Ende $(date '+%T'). Protokoll: $LOG"
log "Nach dem Test bitte noch: Firefox beenden, neu starten, eine Seite laden; dann melden."
