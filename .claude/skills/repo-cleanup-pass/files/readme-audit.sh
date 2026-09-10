#!/usr/bin/env bash
# Audits every versioned README of the repository: does it carry a date line,
# and does it carry the cross-link to its other language version?
#
# Skill folders with a construction sign are skipped -- they are unfinished on
# purpose. A missing cross-link is only a finding where a second language
# version actually exists; that is why the check looks for the partner file.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

printf '%-56s %-12s %-14s %s\n' DATEI DATUM QUERVERWEIS PARTNER

# -z is not a nicety: without it git quotes paths that contain non-ASCII
# characters, and the filter for the construction-sign folders would then look
# at a line starting with a quotation mark and let them all through.
git ls-files -z '*README*.md' | LC_ALL=C sort -z | while IFS= read -r -d '' f; do
    case "$f" in
        skills/[A-Za-z0-9]*) : ;;      # regular skill, gets checked
        skills/*) continue ;;          # construction sign in the folder name
    esac
    date=$(grep -m1 -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' "$f" 2>/dev/null || true)
    [ -n "$date" ] || date='KEINS'

    case "$f" in
        *README.en.md) partner="${f%README.en.md}README.md" ;;
        *README.de.md) partner="${f%README.de.md}README.md" ;;
        *README.md)
            # In the project root the English version is README.md; below it the
            # German one is. Whichever partner exists is the right one.
            if [ -f "${f%README.md}README.en.md" ]; then
                partner="${f%README.md}README.en.md"
            else
                partner="${f%README.md}README.de.md"
            fi ;;
        *) partner='' ;;
    esac

    if grep -qE '\[(English version|Deutsche Fassung)\]' "$f"; then
        link='vorhanden'
    else
        link='FEHLT'
    fi

    if [ -n "$partner" ] && [ -f "$partner" ]; then
        state="$(basename "$partner")"
    else
        state='keine zweite Fassung'
        [ "$link" = 'FEHLT' ] && link='entfaellt'
    fi

    printf '%-56s %-12s %-14s %s\n' "$f" "$date" "$link" "$state"
done

echo
echo 'Zu lesen: FEHLT ist ein Befund, entfaellt nicht. KEINS beim Datum ist immer ein Befund.'
