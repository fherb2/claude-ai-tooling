#!/usr/bin/env bash
# Which files changed since <ref> carry a date line, and what does it say?
#
# The point is the second list: files that were changed but whose date line
# still names an older day. Files without a date line at all are printed
# separately, because most of them are supposed to have none -- code,
# development files, archives.
#
# Usage:  datelines-since.sh <ref> [<heutiges-datum>]
# Example: datelines-since.sh master 2026-09-10
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

REF=${1:?Referenz fehlt, z. B. ein Commit oder ein Zweigname}
TODAY=${2:-$(date +%F)}

echo "Geaendert seit $REF, mit Datumszeile:"
git diff --name-only "$REF"..HEAD | while read -r f; do
    [ -f "$f" ] || continue
    line=$(grep -m1 -E '^\*(Stand|Last updated): 20[0-9]{2}-[0-9]{2}-[0-9]{2}\*' "$f" 2>/dev/null || true)
    [ -n "$line" ] || continue
    date=$(printf '%s' "$line" | grep -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}')
    if [ "$date" = "$TODAY" ]; then
        printf '  ok        %-52s %s\n' "$f" "$date"
    else
        printf '  NACHZIEHEN %-51s %s\n' "$f" "$date"
    fi
done

echo
echo "Geaendert seit $REF, ohne Datumszeile (meist richtig so):"
git diff --name-only "$REF"..HEAD | while read -r f; do
    [ -f "$f" ] || continue
    grep -qE '^\*(Stand|Last updated): 20[0-9]{2}' "$f" 2>/dev/null || printf '  %s\n' "$f"
done
