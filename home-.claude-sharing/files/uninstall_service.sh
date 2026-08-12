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
# (implementierungs_doku.md, 3.5).
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

# Both may fail harmlessly if the service was never enabled or already gone.
systemctl --user disable --now "$UNIT_NAME" 2>/dev/null || true

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
