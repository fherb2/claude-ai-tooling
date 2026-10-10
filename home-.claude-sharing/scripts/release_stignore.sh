#!/usr/bin/env bash
#
# Take a new version of the shared ignore list into the repository and deliver
# it: copy it to files/.stignore, set the date line of both READMEs to today,
# and rebuild the download packages including the loose downloads/.stignore.
#
# Usage:
#     home-.claude-sharing/scripts/release_stignore.sh [--dry-run] [SOURCE]
#
#     SOURCE     the new list; default ~/.claude/.stignore, where it is usually
#                edited during a conflict session
#     --dry-run  only check the source and show the changed patterns; nothing
#                is written
#
# May be called from any working directory; the script locates the project
# folder from its own position.
#
# Why this exists: the ignore list does not travel with the sync, and most
# updates change nothing but this one file. Taking it over by hand means four
# steps in three places -- the copy, two date lines, the repack -- and the
# repack is the one that gets forgotten. Before anything is written, the source
# is checked for the three lines whose position carries the safety of the
# whole list (doku 2.3, 3.9): a list without them would be delivered to every
# machine.
#
# This script is a development tool. It is NOT part of what gets delivered and
# never travels to a target machine (doku 2.7).
#
# @Claude:
#     How to use: run it with --dry-run first and show the user the changed
#     patterns, then run it without. The project skill stignore-release
#     describes the whole procedure around it, commit and release included.
#
#     What to ask the user: whether the source is the right file, if it is not
#     the default. Nothing else -- the content of the list is the user's
#     decision and was made before the script runs.
#
#     What to report afterwards: the added and removed patterns, the new date
#     line, and the verdict of pack_packages.sh. Report a refusal of the safety
#     check verbatim; do not repair the source yourself, it belongs to the user.
#     Output is German like that of the other development scripts (doku 2.5).
set -euo pipefail

# The project folder is the parent of this script's folder, following symlinks.
SCRIPT_PATH="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT_PATH" ]; do
    SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH")"
done
AREA="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"

TARGET="$AREA/files/.stignore"

dry_run=0
source_path="$HOME/.claude/.stignore"
for arg in "$@"; do
    case "$arg" in
        --dry-run) dry_run=1 ;;
        -*) printf 'Abbruch: unbekannter Schalter %s\n' "$arg" >&2; exit 2 ;;
        *) source_path="$arg" ;;
    esac
done

[ -f "$source_path" ] || { printf 'Abbruch: keine Datei %s\n' "$source_path" >&2; exit 1; }
[ -f "$TARGET" ] || { printf 'Abbruch: keine Datei %s\n' "$TARGET" >&2; exit 1; }

# Pattern lines only: no blank lines, no "//" comments. Directives such as
# "#include" count, because their position matters just as much.
patterns_of() {
    grep -v -E '^[[:space:]]*(//|$)' "$1" || true
}

# Safety check. The credentials line must come first, and the two lines of the
# local list directly after it: the first matching pattern decides, so local
# patterns must not be able to reach above the credentials line (doku 3.9).
expected_head=$'.credentials.json\n#include .stignore-local\n/.stignore-local'
actual_head=$(patterns_of "$source_path" | head -n 3)
if [ "$actual_head" != "$expected_head" ]; then
    printf 'Abbruch: Die ersten drei Muster der Quelle sind nicht\n' >&2
    printf '%s\n' "$expected_head" | sed 's/^/    /' >&2
    printf 'sondern\n' >&2
    printf '%s\n' "$actual_head" | sed 's/^/    /' >&2
    printf 'Nichts wurde geschrieben.\n' >&2
    exit 1
fi
printf 'Schutzpruefung bestanden: %s\n' "$source_path"

if cmp -s "$source_path" "$TARGET"; then
    printf 'Unveraendert: Die Quelle gleicht files/.stignore, nichts zu tun.\n'
    exit 0
fi

# Matched by line and not with comm, for the reason given in pack_packages.sh.
new_patterns=$(patterns_of "$source_path")
old_patterns=$(patterns_of "$TARGET")
added=$(printf '%s\n' "$new_patterns" | grep -Fxv -f <(printf '%s\n' "$old_patterns") || true)
removed=$(printf '%s\n' "$old_patterns" | grep -Fxv -f <(printf '%s\n' "$new_patterns") || true)

if [ -z "$added" ] && [ -z "$removed" ]; then
    printf 'Muster unveraendert, nur Kommentare oder Reihenfolge geaendert.\n'
fi
if [ -n "$added" ]; then
    printf 'Hinzugekommen:\n'
    printf '%s\n' "$added" | sed 's/^/  + /'
fi
if [ -n "$removed" ]; then
    printf 'Entfallen:\n'
    printf '%s\n' "$removed" | sed 's/^/  - /'
fi

if [ "$dry_run" -eq 1 ]; then
    printf '\n[dry-run] Nichts geschrieben.\n'
    exit 0
fi

cp "$source_path" "$TARGET"
printf '\nuebernommen: files/.stignore\n'

# The date line sits directly under the main heading; only that one line is
# touched, and a README without it stops the run before anything is packed.
today=$(date +%F)
set_date_line() {
    local file="$1" label="$2" line_no
    line_no=$(grep -n -m1 -E "^\*${label}: [0-9]{4}-[0-9]{2}-[0-9]{2}\*\$" "$file" | cut -d: -f1 || true)
    if [ -z "$line_no" ] || [ "$line_no" -gt 5 ]; then
        printf 'Abbruch: keine Datumszeile "*%s: ...*" oben in %s\n' "$label" "$file" >&2
        exit 1
    fi
    sed -i "${line_no}s/^\*${label}: [0-9-]*\*\$/*${label}: ${today}*/" "$file"
    printf 'Datumszeile: %s -> %s\n' "$(basename "$file")" "$today"
}
set_date_line "$AREA/README.md" "Stand"
set_date_line "$AREA/README.en.md" "Last updated"

printf '\n'
"$AREA/scripts/pack_packages.sh"
