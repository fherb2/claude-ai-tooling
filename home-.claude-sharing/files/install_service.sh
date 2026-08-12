#!/usr/bin/env bash
#
# Install the Claude sync conflict watcher as a systemd user service.
#
# Usage:
#     ~/.claude-sync-watch/install_service.sh
#
# May be called from any working directory -- what counts is the directory
# this script itself sits in. That directory must be ~/.claude-sync-watch:
# the unit file hardcodes %h/.claude-sync-watch, so any other location would
# require editing it, and keeping the unit a static file is deliberate
# (implementierungs_doku.md, 2.7 and 3.5).
#
# This script installs nothing on your behalf. If a prerequisite is missing
# it names the command to fix it and stops -- installing packages requires
# your consent, and an installer is no place to work around that (doku 3.5).

set -euo pipefail

# Resolve the directory this script lives in, following symlinks.
SCRIPT_PATH="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT_PATH" ]; do
    SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH")"
done
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

REQUIRED_DIR="$HOME/.claude-sync-watch"
UNIT_NAME="claude-sync-watch.service"
UNIT_TARGET_DIR="$HOME/.config/systemd/user"
WATCH_DIR="$HOME/.claude"

fail() {
    printf 'Abbruch: %s\n' "$1" >&2
    if [ $# -gt 1 ]; then
        printf '\n%s\n' "$2" >&2
    fi
    exit 1
}

# --- 1. Location ----------------------------------------------------------
# Checked first: everything below assumes the prescribed path.

if [ "$SCRIPT_DIR" != "$REQUIRED_DIR" ]; then
    fail "Dieser Ordner liegt an der falschen Stelle." \
"Gefunden:  $SCRIPT_DIR
Erwartet:  $REQUIRED_DIR

Der Ort ist Vorschrift, keine Empfehlung: Die Dienstdefinition verweist
fest auf ~/.claude-sync-watch. Bitte den gesamten Ordner dorthin
verschieben und dieses Skript erneut starten:

    mv \"$SCRIPT_DIR\" \"$REQUIRED_DIR\"
    \"$REQUIRED_DIR/install_service.sh\""
fi

# --- 2. Own files ---------------------------------------------------------

for file in claude_sync_watchd.py "$UNIT_NAME" konfliktloesung.md .stignore; do
    [ -f "$SCRIPT_DIR/$file" ] || fail \
        "Die Datei '$file' fehlt in $SCRIPT_DIR." \
"Alle Dateien des Vorhabens müssen in diesem Ordner liegen. Bitte den
Ordner 'files/' aus dem Repo vollständig hierher kopieren."
done

[ -d "$SCRIPT_DIR/werkzeuge" ] || mkdir -p "$SCRIPT_DIR/werkzeuge"

# --- 3. Prerequisites -----------------------------------------------------

[ -x /usr/bin/claude ] || fail \
    "/usr/bin/claude ist nicht vorhanden oder nicht ausführbar." \
"Ohne Claude Code kann keine Konfliktsitzung starten. Bitte Claude Code
installieren und sicherstellen, dass es unter /usr/bin/claude erreichbar
ist."

# Vorhanden genügt nicht: die Konfliktsitzung ist wertlos, wenn die
# Terminal-Fassung nicht angemeldet ist. Ohne diese Pruefung richtet sich der
# Dienst ein, zeigt brav Dialoge und oeffnet Terminals, in denen nichts
# Sinnvolles passiert -- ein stiller Ausfall.
#
# Der Aufruf kostet einen Bruchteil eines Cent an Tokens und einen
# Netzzugriff. NICHT mit --bare: das meldet eine vorhandene Anmeldung
# faelschlich als fehlend (beobachtet, Doku 3.8).
printf 'Prüfe die Anmeldung von Claude Code (ein kurzer Aufruf) …\n'
login_probe="$(timeout 120 /usr/bin/claude -p "ok" 2>&1 || true)"
case "$login_probe" in
    *"Not logged in"*|*"/login"*)
        fail "Claude Code ist in dieser Terminal-Umgebung nicht angemeldet." \
"Die Konfliktsitzung koennte nichts tun. Bitte einmal von Hand anmelden:

    claude

Dort das Erst-Start-Gespraech durchlaufen (Theme waehlen; 'auto' passt sich
dem Terminal an) und '/login' ausfuehren. Danach dieses Skript erneut starten."
        ;;
    "")
        printf 'Hinweis: Die Anmeldeprüfung lieferte keine Antwort.\n' >&2
        printf 'Der Dienst wird trotzdem eingerichtet; bitte einmal von Hand\n' >&2
        printf '"claude" starten und sicherstellen, dass es antwortet.\n\n' >&2
        ;;
esac

# Geprueft wird genau der Interpreter, den die Unit startet -- NICHT das
# "python3" dieser Shell. Auf einem Rechner, dessen Shell ein Virtualenv im
# PATH fuehrt, sind das zwei verschiedene Interpreter, und nur einer sieht die
# Distributionspakete: Die Pruefung meldete dort "watchdog fehlt", waehrend der
# Dienst lauffaehig war, und schickte in eine Sackgasse (beobachtet, Doku 3.8).
SERVICE_PYTHON=/usr/bin/python3

[ -x "$SERVICE_PYTHON" ] || fail \
    "$SERVICE_PYTHON ist nicht vorhanden oder nicht ausführbar." \
"Der Dienst startet genau diesen Interpreter. Bitte Python 3 über die
Distribution installieren, zum Beispiel:

    sudo apt install python3"

printf 'Prüfe die Beobachtungsbibliothek in %s …\n' "$SERVICE_PYTHON"
"$SERVICE_PYTHON" -c 'import watchdog' 2>/dev/null || fail \
    "Die Python-Beobachtungsbibliothek 'watchdog' fehlt in $SERVICE_PYTHON." \
"Bitte über die Distribution installieren, zum Beispiel:

    sudo apt install python3-watchdog

Ein 'pip install' in einer Virtualenv hilft hier nicht: Der Dienst startet
$SERVICE_PYTHON, nicht das python3 dieser Shell. Danach dieses Skript erneut
starten."

command -v zenity >/dev/null 2>&1 || fail \
    "'zenity' fehlt — ohne es kann kein Dialog erscheinen." \
"Bitte über die Distribution installieren, zum Beispiel:

    sudo apt install zenity"

command -v systemctl >/dev/null 2>&1 || fail \
    "'systemctl' nicht gefunden — dieses Skript richtet einen systemd-Benutzerdienst ein." \
"Auf Systemen ohne systemd ist der Dienst von Hand einzurichten; die
Vorlage steht in $UNIT_NAME."

[ -d "$WATCH_DIR" ] || fail \
    "Der zu überwachende Ordner $WATCH_DIR existiert nicht." \
"Erwartet wird das von Syncthing abgeglichene ~/.claude."

# Die Ausschlussliste wandert nicht mit dem Abgleich (Doku 2.8): Abweichungen
# zwischen den Rechnern fallen sonst NIE von selbst auf. Deshalb ist die
# Fassung in diesem Ordner die maßgebliche, und hier wird verglichen. Nur eine
# Warnung, kein Abbruch: Eine abweichende Ausschlussliste ist ein Mangel, aber
# kein Grund, den Waechter nicht einzurichten.
if [ -f "$WATCH_DIR/.stignore" ]; then
    if cmp -s "$SCRIPT_DIR/.stignore" "$WATCH_DIR/.stignore"; then
        printf 'Ausschlussliste stimmt mit der maßgeblichen Fassung überein.\n'
    else
        printf 'WARNUNG: %s/.stignore weicht von der Fassung in diesem\n' "$WATCH_DIR" >&2
        printf 'Ordner ab. Die Datei wandert nicht mit dem Abgleich, Abweichungen\n' >&2
        printf 'zwischen den Rechnern fallen also nie von selbst auf. Unterschiede:\n\n' >&2
        diff -u "$WATCH_DIR/.stignore" "$SCRIPT_DIR/.stignore" >&2 || true
        printf '\nMaßgeblich ist die Fassung hier. Uebernehmen mit:\n' >&2
        printf '    cp %s/.stignore %s/.stignore\n' "$SCRIPT_DIR" "$WATCH_DIR" >&2
        printf 'Danach in Syncthing die Ordnereinstellungen neu einlesen lassen.\n\n' >&2
    fi
else
    printf 'WARNUNG: %s/.stignore fehlt — nichts ist ausgeschlossen,\n' "$WATCH_DIR" >&2
    printf 'auch nicht die Zugangsdaten. Bitte die Fassung aus diesem Ordner\n' >&2
    printf 'kopieren, bevor weiter abgeglichen wird:\n' >&2
    printf '    cp %s/.stignore %s/.stignore\n\n' "$SCRIPT_DIR" "$WATCH_DIR" >&2
fi

if command -v pgrep >/dev/null 2>&1 && ! pgrep -x syncthing >/dev/null 2>&1; then
    printf 'Hinweis: Syncthing scheint gerade nicht zu laufen.\n' >&2
    printf 'Der Dienst wird trotzdem eingerichtet; ohne laufendes Syncthing\n' >&2
    printf 'entstehen aber keine Konfliktkopien und die Betriebsmeldung entfällt.\n\n' >&2
fi

# --- 4. Install -----------------------------------------------------------

printf 'Richte %s ein …\n' "$UNIT_NAME"

mkdir -p "$UNIT_TARGET_DIR"
cp "$SCRIPT_DIR/$UNIT_NAME" "$UNIT_TARGET_DIR/$UNIT_NAME"

systemctl --user daemon-reload
systemctl --user enable --now "$UNIT_NAME"

printf '\nFertig. Status:\n\n'
systemctl --user --no-pager status "$UNIT_NAME" || true

printf '\nLaufende Ausgabe mitlesen:\n'
printf '    journalctl --user -u %s -f\n' "$UNIT_NAME"
printf 'Wieder abmelden:\n'
printf '    %s/uninstall_service.sh\n' "$SCRIPT_DIR"
