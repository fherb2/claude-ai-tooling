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

# The type is asked PER PATH and never taken from the directory listing. A mask
# is a mount, and the d_type that readdir hands out still describes the regular
# file underneath it -- GNU find uses exactly that d_type to avoid a stat call,
# so `find . -type c` misses every mask, while `find .bashrc -type c` on the
# same name in the same process finds it. Measured on 11 September 2026: the
# one-liner this loop replaces reported "no masks" while 20 of them lay in the
# working tree. `test -c` calls stat(2) on the path and is therefore reliable.
masks=()
while IFS= read -r -d '' path; do
    path=${path#./}
    if [ -c "$path" ] || [ -b "$path" ]; then
        masks+=("$path")
    fi
done < <(find . -path ./.git -prune -o -print0 2>/dev/null)

found=$(printf '%s\n' ${masks+"${masks[@]}"} | grep . | LC_ALL=C sort || true)

if [ -z "$found" ]; then
    echo 'Keine Attrappen im Arbeitsbaum. Entweder laeuft keine Sandbox, oder sie maskiert hier nichts.'
    exit 0
fi

echo 'Maskierte Attrappen im Arbeitsbaum (kein Repo-Inhalt):'
printf '%s\n' "$found" | sed 's|^\./|  |'
echo
printf 'Anzahl: %s\n' "$(printf '%s\n' "$found" | grep -c .)"
echo 'Folge: mit ausdruecklichen Pfaden committen, nicht mit git add -A.'
