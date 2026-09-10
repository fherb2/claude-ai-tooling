#!/usr/bin/env bash
# Lists the placeholder devices that the Bash sandbox mounts into the working
# tree to mask paths it must not expose.
#
# Why this matters during a cleanup pass: those entries look like untracked
# files in `git status`, they cannot be read, and they make any recursive tool
# abort with "Permission denied" -- a markdown checker, for instance. Outside
# the sandbox they do not exist at all, so the developer does not see them.
#
# Two consequences, both worth knowing before committing:
#   * stage with explicit paths; `git add -A` would stumble over them,
#   * a recursive check that aborts is not necessarily a broken tool.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

found=$(find . -path ./.git -prune -o \( -type c -o -type b \) -print 2>/dev/null | LC_ALL=C sort)

if [ -z "$found" ]; then
    echo 'Keine Attrappen im Arbeitsbaum. Entweder laeuft keine Sandbox, oder sie maskiert hier nichts.'
    exit 0
fi

echo 'Maskierte Attrappen im Arbeitsbaum (kein Repo-Inhalt):'
printf '%s\n' "$found" | sed 's|^\./|  |'
echo
printf 'Anzahl: %s\n' "$(printf '%s\n' "$found" | grep -c .)"
echo 'Folge: mit ausdruecklichen Pfaden committen, nicht mit git add -A.'
