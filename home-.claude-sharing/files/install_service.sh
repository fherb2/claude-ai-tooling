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
# This script installs nothing behind your back. Where a package is missing it
# says what breaks, offers to install it, and acts only on an explicit "yes"
# (doku 3.5). What the older rule forbade was installing silently, not asking:
# a question obtains your consent instead of working around it.
#
# It therefore needs a terminal and refuses to run without one. An unattended
# install would leave you unable to answer and unable to see what happened.

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

# Every warning pauses afterwards. Without the pause the next block overruns
# it: the hint about a missing notification tool was printed exactly as
# intended and still went unnoticed, because five more blocks followed and a
# success message was the last thing on screen (doku 3.5).
WARN_PAUSE_SECONDS=3

warn() {
    printf '%s\n\n' "$1" >&2
    sleep "$WARN_PAUSE_SECONDS"
}

# Offer to install a missing package instead of only naming the command.
# Arguments: package, what doing without costs, the abort text -- empty makes
# the package optional and a refusal survivable -- then the command that tests
# whether it is there. The answer is read from /dev/tty, not from standard
# input, so a redirection cannot swallow the question; sudo reads the password
# from the same place, which is why a password prompt does not disturb this
# script (measured, doku 3.5).
ensure_package() {
    local package="$1" consequence="$2" abort_text="$3"
    shift 3
    if "$@" >/dev/null 2>&1; then
        return 0
    fi
    printf '\n%s fehlt — %s\n' "$package" "$consequence" >&2
    printf 'Jetzt nachinstallieren? Das Skript ruft dazu\n' >&2
    printf '    sudo apt install %s\n' "$package" >&2
    printf 'auf; das System fragt dabei nach dem Passwort. [j/N] ' >&2
    local answer=""
    # Belt and braces: the terminal check above already rules this out, so a
    # failure here means the terminal vanished mid-run. Treated as "no" -- and
    # quietly, because the shell's own redirection error would say nothing the
    # user could act on.
    # The order of the redirections matters: bash applies them left to right,
    # so 2>/dev/null has to come first to swallow the failure message of the
    # one after it. Reversed, the shell reports the missing terminal itself.
    read -r answer 2>/dev/null < /dev/tty || answer=""
    case "$answer" in
        j|J|ja|Ja|JA|y|Y|yes|Yes)
            local apt_log=""
            printf 'Installiere %s …\n' "$package"
            # apt's output is captured and shown only on failure: this whole
            # change exists because the run was too talkative to be read. The
            # "unstable CLI interface" notice apt emits without a tty lands in
            # the same capture and stays invisible unless something breaks.
            if apt_log="$(sudo apt install -y "$package" 2>&1)" \
                    && "$@" >/dev/null 2>&1; then
                printf '%s ist installiert.\n\n' "$package"
                return 0
            fi
            printf 'Die Installation von %s ist fehlgeschlagen:\n' "$package" >&2
            printf '%s\n' "$apt_log" >&2
            ;;
    esac
    if [ -n "$abort_text" ]; then
        fail "$package fehlt — $consequence" "$abort_text"
    fi
    warn "Weiter ohne $package."
}

# --- 0. Terminal ----------------------------------------------------------
# Checked before anything else: every step below may ask a question, and sudo
# needs a terminal to read a password from. Opening /dev/tty is the only valid
# test -- the device file exists even without a controlling terminal, so a file
# test would always succeed (measured). A failing redirection inside an `if`
# condition is exempt from `set -e`, so this cannot abort the script by itself.
if ! ( : < /dev/tty ) 2>/dev/null; then
    fail "Kein Terminal — dieses Skript fragt nach und braucht eine Antwort." \
"Eine Einrichtung ohne Rückmeldung an den Nutzer wird bewusst nicht
unterstützt: Sie könnten weder eine Rückfrage beantworten noch sehen, was
dabei geschieht. Bitte das Skript in einem Terminal starten."
fi

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

# Present is not enough: the conflict session is worthless if the terminal
# installation is not logged in. Without this check the service installs
# itself, dutifully shows dialogs and opens terminals in which nothing
# useful happens -- a silent failure.
#
# The call costs a fraction of a cent in tokens and one network access.
# NOT with --bare: that reports an existing login as missing (observed,
# doku 3.8).
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
        warn 'Hinweis: Die Anmeldeprüfung lieferte keine Antwort.
Der Dienst wird trotzdem eingerichtet; bitte einmal von Hand
"claude" starten und sicherstellen, dass es antwortet.'
        ;;
esac

# Checked is exactly the interpreter the unit starts -- NOT the "python3" of
# this shell. On a machine whose shell carries a virtualenv in PATH those are
# two different interpreters, and only one of them sees the distribution
# packages: the check reported "watchdog missing" there while the service was
# perfectly able to run, and sent the user down a dead end (observed, 3.8).
SERVICE_PYTHON=/usr/bin/python3

[ -x "$SERVICE_PYTHON" ] || fail \
    "$SERVICE_PYTHON ist nicht vorhanden oder nicht ausführbar." \
"Der Dienst startet genau diesen Interpreter. Bitte Python 3 über die
Distribution installieren, zum Beispiel:

    sudo apt install python3"

printf 'Prüfe die Beobachtungsbibliothek in %s …\n' "$SERVICE_PYTHON"
ensure_package python3-watchdog \
    "der Wächter kann ohne sie keine Dateiänderung bemerken" \
"Ein 'pip install' in einer Virtualenv hilft hier nicht: Der Dienst startet
$SERVICE_PYTHON, nicht das python3 dieser Shell. Bitte das Distributionspaket
installieren:

    sudo apt install python3-watchdog

Danach dieses Skript erneut starten." \
    "$SERVICE_PYTHON" -c 'import watchdog'

ensure_package zenity \
    "ohne es kann kein Dialog erscheinen" \
"Der Wächter eskaliert ausschließlich über Zenity-Dialoge (Doku 2.9); ohne sie
bliebe ein Konflikt unbemerkt liegen. Bitte über die Distribution installieren:

    sudo apt install zenity" \
    command -v zenity

# Optional, and deliberately so: without it only the hourly notice is missing
# while conflict detection and escalation work in full (doku 1.8). It must be
# noticed all the same -- this very gap went unnoticed on one machine for two
# days, because nothing checked for it here (doku 3.8).
ensure_package libnotify-bin \
    "ohne dieses Paket fehlt notify-send, und die stündliche Betriebsmeldung kann nicht am Bildschirm erscheinen. Der Wächter meldet das einmal je Lauf im Journal, aber erst beim ersten fälligen Durchgang, spätestens nach einer Stunde. Konflikterkennung und Eskalation sind unberührt" \
    "" \
    command -v notify-send

command -v systemctl >/dev/null 2>&1 || fail \
    "'systemctl' nicht gefunden — dieses Skript richtet einen systemd-Benutzerdienst ein." \
"Auf Systemen ohne systemd ist der Dienst von Hand einzurichten; die
Vorlage steht in $UNIT_NAME."

[ -d "$WATCH_DIR" ] || fail \
    "Der zu überwachende Ordner $WATCH_DIR existiert nicht." \
"Erwartet wird das von Syncthing abgeglichene ~/.claude."

# The directory being there says nothing about it being synchronised, and 3.5
# used to promise the second while checking the first -- exactly the silent
# failure the checklist exists for. The watcher answers this itself, because it
# already owns the configuration location, the key, the REST call and the path
# comparison; a second implementation here would violate 2.4 and the Windows
# counterpart would need a third. Read-only by contract: no lock, no state file.
#
# A warning, never an abort. Case 2 means the interface said nothing, and from
# that the script may conclude nothing; case 1 means the watcher would run
# flawlessly and find nothing for ever, which the user has to learn -- but a
# watcher without a synced folder is useless, not harmful.
printf 'Prüfe, ob %s von Syncthing abgeglichen wird …\n' "$WATCH_DIR"
folder_check="$("$SERVICE_PYTHON" "$SCRIPT_DIR/claude_sync_watchd.py" \
    --check-folder --watch-dir "$WATCH_DIR" 2>&1)" && folder_state=0 \
    || folder_state=$?
case "$folder_state" in
    0) printf '%s\n' "$folder_check" ;;
    1) warn "WARNUNG: $folder_check
Der Wächter wird eingerichtet und läuft, findet aber nie einen Konflikt,
weil dieser Ordner nicht am Abgleich teilnimmt. Bitte ihn in Syncthing
teilen — die Anleitung steht in der Konfigurationsanleitung." ;;
    *) warn "Hinweis: $folder_check
Ob der Ordner abgeglichen wird, ist damit offen. Der Dienst wird
eingerichtet; bitte in Syncthings Oberfläche nachsehen." ;;
esac

# The exclusion list does not travel with the sync (doku 2.8): differences
# between the machines would otherwise NEVER surface by themselves. The copy
# in this folder is therefore the authoritative one, and this is where it is
# compared. A warning only, not an abort: a diverging exclusion list is a
# defect, but no reason to leave the watcher uninstalled.
if [ -f "$WATCH_DIR/.stignore" ]; then
    if cmp -s "$SCRIPT_DIR/.stignore" "$WATCH_DIR/.stignore"; then
        printf 'Ausschlussliste stimmt mit der maßgeblichen Fassung überein.\n'
    else
        # The diff goes into the message instead of straight to the terminal,
        # so the whole warning is one block and the pause comes after all of it.
        stignore_diff="$(diff -u "$WATCH_DIR/.stignore" "$SCRIPT_DIR/.stignore" || true)"
        warn "WARNUNG: $WATCH_DIR/.stignore weicht von der Fassung in diesem
Ordner ab. Die Datei wandert nicht mit dem Abgleich, Abweichungen
zwischen den Rechnern fallen also nie von selbst auf. Unterschiede:

$stignore_diff

Maßgeblich ist die Fassung hier. Übernehmen mit:
    cp $SCRIPT_DIR/.stignore $WATCH_DIR/.stignore
Danach in Syncthing die Ordnereinstellungen neu einlesen lassen."
    fi
else
    warn "WARNUNG: $WATCH_DIR/.stignore fehlt — nichts ist ausgeschlossen,
auch nicht die Zugangsdaten. Bitte die Fassung aus diesem Ordner
kopieren, bevor weiter abgeglichen wird:
    cp $SCRIPT_DIR/.stignore $WATCH_DIR/.stignore"
fi

if command -v pgrep >/dev/null 2>&1 && ! pgrep -x syncthing >/dev/null 2>&1; then
    warn 'Hinweis: Syncthing scheint gerade nicht zu laufen.
Der Dienst wird trotzdem eingerichtet; ohne laufendes Syncthing
entstehen aber keine Konfliktkopien und die Betriebsmeldung entfällt.'
fi

# --- 4. Install -----------------------------------------------------------

printf 'Richte %s ein …\n' "$UNIT_NAME"

mkdir -p "$UNIT_TARGET_DIR"
cp "$SCRIPT_DIR/$UNIT_NAME" "$UNIT_TARGET_DIR/$UNIT_NAME"

systemctl --user daemon-reload
systemctl --user enable "$UNIT_NAME"

# restart, not "enable --now": the latter starts the service only if it is not
# already running, so re-installing a NEW version reported success while the OLD
# process kept running -- observed on 2026-08-14, file copied at 20:20, process
# from 10:21 (doku 3.5). This script exists to put THIS version into service.
# The restart costs nothing: the watcher keeps no state in memory that it does
# not restore from its file, and the scan on startup catches up on what it
# missed. A conflict session running at that moment is unaffected -- it is a
# detached process, the run lock is transient, and its pid is in the state file.
systemctl --user restart "$UNIT_NAME"

printf '\nFertig, Dienst neu gestartet. Status:\n\n'
systemctl --user --no-pager status "$UNIT_NAME" || true

printf '\nLaufende Ausgabe mitlesen:\n'
printf '    journalctl --user -u %s -f\n' "$UNIT_NAME"
printf 'Wieder abmelden:\n'
printf '    %s/uninstall_service.sh\n' "$SCRIPT_DIR"
