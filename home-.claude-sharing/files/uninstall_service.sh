#!/usr/bin/env bash
#
# Unregister the Claude sync conflict watcher.
#
# Usage:
#     ~/.claude-sync-watch/uninstall_service.sh
#
# Stops and disables the service and removes the unit file. It deliberately
# leaves the folder, the state file and the working instruction untouched:
# this unregisters the service, it does not uninstall the project. To get rid
# of everything, delete ~/.claude-sync-watch afterwards by hand
# (implementation-doc.md, 3.5).
#
# Nothing in the synchronised directory is touched either way.

set -euo pipefail

UNIT_NAME="claude-sync-watch.service"
UNIT_TARGET_DIR="$HOME/.config/systemd/user"

if ! command -v systemctl >/dev/null 2>&1; then
    printf 'Abbruch: systemctl nicht gefunden.\n' >&2
    exit 1
fi

printf 'Melde %s ab …\n' "$UNIT_NAME"

# Return value and message are kept instead of discarded. The old
# '|| true' with 2>/dev/null did cover the harmless cases -- never enabled,
# already gone -- but it covered the harmful ones just as well: a masked unit,
# a service refusing to stop, no user instance of systemd at all (doku 3.5).
if disable_output="$(systemctl --user disable --now "$UNIT_NAME" 2>&1)"; then
    disable_failed=0
else
    disable_failed=1
fi

# ONE rule for what follows: the unit is only removed when the service is
# provably not running. "Cannot tell" does not count as success.
#
# The decision hangs on the WORD, not on the return value, and that is the
# whole point: 'is-active' answers 4 plus "inactive" for an unknown unit, but 1
# plus "Failed to connect to bus" when there is no user instance. Read as a
# return value, the second would pass for "not running" -- precisely the case
# in which nothing may be removed. The status is therefore ignored on purpose.
state="$(systemctl --user is-active "$UNIT_NAME" 2>&1 | head -1)" || true

case "$state" in
    inactive|failed|unknown)
        ;;
    *)
        printf 'Abbruch: Der Dienst ist nicht nachweislich beendet.\n' >&2
        printf 'Zustand laut systemctl: %s\n' "$state" >&2
        if [ "$disable_failed" -eq 1 ]; then
            printf 'Das Abmelden meldete: %s\n' "$disable_output" >&2
        fi
        printf '\nDie Unit bleibt absichtlich liegen: Ohne sie wäre ein noch\n' >&2
        printf 'laufender Wächter schlechter zu beenden. Bitte nachsehen und\n' >&2
        printf 'dieses Skript danach erneut aufrufen:\n' >&2
        printf '    systemctl --user status %s\n' "$UNIT_NAME" >&2
        printf '    systemctl --user stop %s\n' "$UNIT_NAME" >&2
        exit 1
        ;;
esac

if [ "$disable_failed" -eq 1 ]; then
    # Harmless here -- the service is provably not running -- but not swallowed
    # either: a message thrown away is worse than one nobody needed (2.6).
    printf 'Hinweis vom Abmelden: %s\n' "$disable_output"
fi

if [ -f "$UNIT_TARGET_DIR/$UNIT_NAME" ]; then
    rm -f "$UNIT_TARGET_DIR/$UNIT_NAME"
    printf 'Unit entfernt: %s\n' "$UNIT_TARGET_DIR/$UNIT_NAME"
else
    printf 'Keine installierte Unit gefunden — nichts zu entfernen.\n'
fi

systemctl --user daemon-reload

printf '\nDer Dienst ist abgemeldet.\n'
printf 'Ordner, Zustandsdatei und Arbeitsanweisung bleiben unangetastet:\n'
printf '    %s\n' "$HOME/.claude-sync-watch"
printf 'Wer alles loswerden will, löscht diesen Ordner von Hand.\n'
