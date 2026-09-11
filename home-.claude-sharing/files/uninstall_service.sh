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
    printf 'Aborting: systemctl not found.\n' >&2
    exit 1
fi

printf 'Unregistering %s …\n' "$UNIT_NAME"

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
        printf 'Aborting: the service is not provably stopped.\n' >&2
        printf 'State according to systemctl: %s\n' "$state" >&2
        if [ "$disable_failed" -eq 1 ]; then
            printf 'Disabling reported: %s\n' "$disable_output" >&2
        fi
        printf '\nThe unit is left in place on purpose: without it a watcher\n' >&2
        printf 'that is still running would be harder to stop. Please look,\n' >&2
        printf 'then call this script again:\n' >&2
        printf '    systemctl --user status %s\n' "$UNIT_NAME" >&2
        printf '    systemctl --user stop %s\n' "$UNIT_NAME" >&2
        exit 1
        ;;
esac

if [ "$disable_failed" -eq 1 ]; then
    # Harmless here -- the service is provably not running -- but not swallowed
    # either: a message thrown away is worse than one nobody needed (2.6).
    printf 'Note from unregistering: %s\n' "$disable_output"
fi

if [ -f "$UNIT_TARGET_DIR/$UNIT_NAME" ]; then
    rm -f "$UNIT_TARGET_DIR/$UNIT_NAME"
    printf 'Unit removed: %s\n' "$UNIT_TARGET_DIR/$UNIT_NAME"
else
    printf 'No installed unit found — nothing to remove.\n'
fi

systemctl --user daemon-reload

printf '\nThe service is unregistered.\n'
printf 'Folder, state file and working instruction stay untouched:\n'
printf '    %s\n' "$HOME/.claude-sync-watch"
printf 'To get rid of everything, delete this folder by hand.\n'
