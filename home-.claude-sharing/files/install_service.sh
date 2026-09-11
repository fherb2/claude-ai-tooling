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
# (implementation-doc.md, 2.7 and 3.5).
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

# Absolute on purpose -- a service starts with a sparse PATH and would not find
# "claude" (doku 3.3). It is a variable rather than a literal so that the login
# check below can be exercised against a stand-in; the checks themselves are
# the one thing here that must not go untested (doku 3.5).
CLAUDE_BIN="/usr/bin/claude"

# How long the answer probe may take. A variable for the same reason as
# the path above: the timeout case is one of the four the test covers, and
# waiting two minutes for it would be waiting for nothing (doku 3.5).
LOGIN_PROBE_TIMEOUT=120

# Syncthing's documented default GUI address ("The default listening address is
# 127.0.0.1:8384", docs.syncthing.net FAQ). Used in exactly one place: the hint
# after the exclusion list was copied. Only the base address, no deep link into
# the folder settings -- the addresses inside the interface are not documented,
# and a guessed link would be a claim (doku 3.5).
SYNCTHING_GUI="http://127.0.0.1:8384"

fail() {
    printf 'Aborting: %s\n' "$1" >&2
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

# True when at least one file matches the pattern. Needed because the working
# instruction and the message catalogue carry a language code in their name and
# a package holds exactly one of each (doku 2.7): there is no fixed name to
# test for. Without nullglob an unmatched pattern stays literal, and the -f
# test then fails as it should.
one_of() {
    local pattern="$1" candidate
    for candidate in $pattern; do
        if [ -f "$candidate" ]; then
            return 0
        fi
    done
    return 1
}

# --- Question: begin (doku 3.5) ---------------------------------------------
# Cut out and run by the test script as it stands. Do not restructure without
# looking there.
#
# Ask a yes/no question and answer through the exit status. Arguments: the
# question, then the default -- "y" or "n" -- which an empty answer selects and
# which the prompt shows in capitals.
#
# One reader for both questions: the packages default to NO, because installing
# something is the larger step, and the exclusion list defaults to YES, because
# leaving it diverging is (doku 2.8). Two nearly identical readers side by side
# would be the duplication 2.4 rules out.
#
# The answer is read from /dev/tty, not from standard input, so a redirection
# cannot swallow the question; sudo reads the password from the same place,
# which is why a password prompt does not disturb this script (measured,
# doku 3.5). The order of the redirections matters: bash applies them left to
# right, so 2>/dev/null has to come first to swallow the failure message of the
# one after it. Reversed, the shell reports the missing terminal itself.
#
# Belt and braces: the terminal check at the top already rules a failing read
# out, so a failure here means the terminal vanished mid-run. It selects the
# default -- and quietly, because the shell's own error would say nothing the
# user could act on.
ask_yes_no() {
    local question="$1" default="$2" answer=""
    if [ "$default" = "y" ]; then
        printf '%s [Y/n] ' "$question" >&2
    else
        printf '%s [y/N] ' "$question" >&2
    fi
    read -r answer 2>/dev/null < /dev/tty || answer=""
    [ -n "$answer" ] || answer="$default"
    # The German answers stay accepted although the script asks in English: a
    # German package is installed by the same script, and "j" is what that
    # user reaches for. Accepting one keystroke more costs nothing; reading it
    # as a no would be the wrong answer to a clear intention.
    case "$answer" in
        y|Y|yes|Yes|j|J|ja|Ja|JA) return 0 ;;
    esac
    return 1
}
# --- Question: end ----------------------------------------------------------

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
    printf '\n%s is missing — %s\n' "$package" "$consequence" >&2
    printf 'Install it now? The script would run\n' >&2
    printf '    sudo apt install %s\n' "$package" >&2
    if ask_yes_no "and the system will ask for your password." "n"; then
        local apt_log=""
        printf 'Installing %s …\n' "$package"
        # apt's output is captured and shown only on failure: this whole
        # change exists because the run was too talkative to be read. The
        # "unstable CLI interface" notice apt emits without a tty lands in
        # the same capture and stays invisible unless something breaks.
        if apt_log="$(sudo apt install -y "$package" 2>&1)" \
                && "$@" >/dev/null 2>&1; then
            printf '%s is installed.\n\n' "$package"
            return 0
        fi
        printf 'Installing %s failed:\n' "$package" >&2
        printf '%s\n' "$apt_log" >&2
    fi
    if [ -n "$abort_text" ]; then
        fail "$package is missing — $consequence" "$abort_text"
    fi
    warn "Carrying on without $package."
}

# --- 0. Terminal ----------------------------------------------------------
# Checked before anything else: every step below may ask a question, and sudo
# needs a terminal to read a password from. Opening /dev/tty is the only valid
# test -- the device file exists even without a controlling terminal, so a file
# test would always succeed (measured). A failing redirection inside an `if`
# condition is exempt from `set -e`, so this cannot abort the script by itself.
if ! ( : < /dev/tty ) 2>/dev/null; then
    fail "No terminal — this script asks questions and needs an answer." \
"An installation without feedback to the user is deliberately not
supported: you could neither answer a question nor see what is happening.
Please start this script in a terminal."
fi

# --- 1. Location ----------------------------------------------------------
# Checked first: everything below assumes the prescribed path.

if [ "$SCRIPT_DIR" != "$REQUIRED_DIR" ]; then
    fail "This folder is in the wrong place." \
"Found:     $SCRIPT_DIR
Expected:  $REQUIRED_DIR

The location is prescribed, not suggested: the service definition points
at ~/.claude-sync-watch and nowhere else. Please move the whole folder
there and start this script again:

    mv \"$SCRIPT_DIR\" \"$REQUIRED_DIR\"
    \"$REQUIRED_DIR/install_service.sh\""
fi

# --- 2. Own files ---------------------------------------------------------

MISSING_FILES_HINT="Every file of this project has to be in this folder. Please copy the
folder 'files/' from the repository here in full."

for file in claude_sync_watchd.py "$UNIT_NAME" messages.py .stignore; do
    [ -f "$SCRIPT_DIR/$file" ] || fail \
        "The file '$file' is missing from $SCRIPT_DIR." \
        "$MISSING_FILES_HINT"
done

for pattern in "conflict-resolution.*.md" "messages_*.py"; do
    one_of "$SCRIPT_DIR/$pattern" || fail \
        "No file matching '$pattern' in $SCRIPT_DIR." \
        "$MISSING_FILES_HINT"
done

[ -d "$SCRIPT_DIR/tools" ] || mkdir -p "$SCRIPT_DIR/tools"

# The folder was called 'werkzeuge' until 15 August 2026. Copying the new
# files/ over an existing installation leaves the old one behind, so it is
# named here rather than removed: deleting on someone's machine is the user's
# call (doku 3.5), and the folder may hold scripts nobody else knows about.
if [ -d "$SCRIPT_DIR/werkzeuge" ]; then
    warn "Note: $SCRIPT_DIR/werkzeuge/ is the former name of the folder
'tools' and is no longer used. It stays where it is until you remove it —
look whether anything is in there, then:
    rm -r $SCRIPT_DIR/werkzeuge"
fi

# --- 3. Prerequisites -----------------------------------------------------

[ -x "$CLAUDE_BIN" ] || fail \
    "$CLAUDE_BIN does not exist or is not executable." \
"Without Claude Code no conflict session can start. Please install Claude
Code and make sure it can be reached at $CLAUDE_BIN."

# Present is not enough: the conflict session is worthless if the terminal
# installation is not logged in. Without this check the service installs
# itself, dutifully shows dialogs and opens terminals in which nothing
# useful happens -- a silent failure.
#
# --- Login check: begin (doku 3.5) ------------------------------------------
# Everything between these markers is run by the test script as it stands, with
# fail/warn and CLAUDE_BIN supplied. Do not restructure without looking there.
#
# The deciding test is documented: 'claude auth status' exits 0 when logged in
# and 1 when not. The exit code alone must NOT carry the decision, though -- an
# unknown subcommand exits 1 as well (measured), so an older Claude Code would
# look exactly like a missing login. Decided on the CONTENT, with the spaces
# removed so a change of formatting cannot break it.
printf 'Checking whether Claude Code is logged in …\n'
auth_report="$("$CLAUDE_BIN" auth status 2>&1 || true)"
auth_flat="$(printf '%s' "$auth_report" | tr -d ' \t\n\r')"

case "$auth_flat" in
    *'"loggedIn":true'*)
        printf 'Logged in.\n'
        ;;
    *'"loggedIn":false'*)
        fail "Claude Code is not logged in for this terminal environment." \
"The conflict session would be unable to do anything. Please log in once by
hand:

    claude

Walk through the first-start conversation there (pick a theme; 'auto'
adapts to the terminal) and run '/login'. Then start this script again."
        ;;
    *)
        # Not an abort: an older Claude Code without this subcommand is no
        # evidence of a missing login, and the same principle already governs
        # the hanging line below (doku 3.5). The answer is shown rather than
        # silently classified.
        warn "Note: the login state could not be determined.
Answer of '$CLAUDE_BIN auth status':

$auth_report

The service is being installed. Please start 'claude' by hand once and make
sure it answers without asking you to log in."
        ;;
esac

# Second test, WARN ONLY: does it actually answer? This is a different question
# from being logged in -- an expired subscription, an exhausted allowance, no
# connection. Since it can no longer abort anything, its inevitably vague
# classification can no longer do harm either.
#
# The call costs a fraction of a cent in tokens and one network access.
# NOT with --bare: that reports an existing login as missing (observed,
# doku 3.8).
printf 'Checking whether Claude Code answers (one short call) …\n'
if login_probe="$(timeout "$LOGIN_PROBE_TIMEOUT" "$CLAUDE_BIN" -p "ok" 2>&1)"; then
    probe_status=0
else
    probe_status=$?
fi

# 124 is timeout's own return value, and it comes even when the call had
# already produced output -- which is why the old '|| true' let a hanging line
# pass for a confirmed login (doku 3.5).
if [ "$probe_status" -eq 124 ]; then
    warn "Note: Claude Code did not answer within $LOGIN_PROBE_TIMEOUT
seconds. The service is being installed all the same; a hanging line is no
evidence of a missing login. Please check once by hand."
else
    case "$login_probe" in
        *"Not logged in"*|*"run /login"*)
            warn "Note: the answer looks like a login problem although the
login was confirmed. The answer verbatim:

$login_probe"
            ;;
        "")
            warn 'Note: the answer was empty.
The service is being installed all the same; please start
"claude" by hand once and make sure it answers.'
            ;;
    esac
fi
# --- Login check: end -------------------------------------------------------

# Checked is exactly the interpreter the unit starts -- NOT the "python3" of
# this shell. On a machine whose shell carries a virtualenv in PATH those are
# two different interpreters, and only one of them sees the distribution
# packages: the check reported "watchdog missing" there while the service was
# perfectly able to run, and sent the user down a dead end (observed, 3.8).
SERVICE_PYTHON=/usr/bin/python3

[ -x "$SERVICE_PYTHON" ] || fail \
    "$SERVICE_PYTHON does not exist or is not executable." \
"The service starts exactly this interpreter. Please install Python 3
through the distribution, for example:

    sudo apt install python3"

printf 'Checking the watch library in %s …\n' "$SERVICE_PYTHON"
ensure_package python3-watchdog \
    "without it the watcher cannot notice any file change" \
"A 'pip install' in a virtualenv does not help here: the service starts
$SERVICE_PYTHON, not the python3 of this shell. Please install the
distribution package:

    sudo apt install python3-watchdog

Then start this script again." \
    "$SERVICE_PYTHON" -c 'import watchdog'

ensure_package zenity \
    "without it no dialog can appear" \
"The watcher escalates through Zenity dialogs and nothing else (doku 2.9);
without them a conflict would lie there unnoticed. Please install it through
the distribution:

    sudo apt install zenity" \
    command -v zenity

# Optional, and deliberately so: without it only the hourly notice is missing
# while conflict detection and escalation work in full (doku 1.8). It must be
# noticed all the same -- this very gap went unnoticed on one machine for two
# days, because nothing checked for it here (doku 3.8).
ensure_package libnotify-bin \
    "without this package notify-send is missing, and the hourly notice cannot appear on screen. The watcher reports that once per run in the journal, but only at the first pass that is due, within the hour at the latest. Conflict detection and escalation are unaffected" \
    "" \
    command -v notify-send

command -v systemctl >/dev/null 2>&1 || fail \
    "'systemctl' not found — this script installs a systemd user service." \
"On a system without systemd the service has to be set up by hand; the
template is $UNIT_NAME."

[ -d "$WATCH_DIR" ] || fail \
    "The directory to watch, $WATCH_DIR, does not exist." \
"Expected is ~/.claude, the directory Syncthing synchronises."

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
#
# The line the watcher answers with is in the WATCHER's language, not this
# script's: setup speaks English by exception, the tool speaks the language of
# the catalogue installed with it (doku 2.5). In a German package this is
# therefore the one German line in an English run, and translating it here
# would mean a second wording to keep in step.
printf 'Checking whether Syncthing synchronises %s …\n' "$WATCH_DIR"
folder_check="$("$SERVICE_PYTHON" "$SCRIPT_DIR/claude_sync_watchd.py" \
    --check-folder --watch-dir "$WATCH_DIR" 2>&1)" && folder_state=0 \
    || folder_state=$?
case "$folder_state" in
    0) printf '%s\n' "$folder_check" ;;
    1) warn "WARNING: $folder_check
The watcher is being installed and will run, but it will never find a
conflict, because this folder does not take part in the synchronisation.
Please share it in Syncthing — the README says how." ;;
    *) warn "Note: $folder_check
Whether the folder is synchronised is therefore open. The service is being
installed; please look in Syncthing's interface." ;;
esac

# --- Exclusion list: begin (doku 3.5) ---------------------------------------
# Everything between these markers is run by the test script as it stands, with
# warn, ask_yes_no, the two paths and the GUI address supplied. Do not
# restructure without looking there.
#
# The exclusion list does not travel with the sync (doku 2.8): differences
# between the machines would otherwise NEVER surface by themselves. The copy in
# this folder is therefore the authoritative one, and this is where it is
# compared -- and offered, because merely naming the command left the last step
# to the hand that forgets it: on 14 August 2026 the same list had to be copied
# by hand on two machines in one day (doku 2.8).
#
# Offered, never done silently. This is the one place where the installer
# writes into the synced folder, and the user has to say so first. A refusal is
# survivable and never aborts: a diverging exclusion list is a defect, but no
# reason to leave the watcher uninstalled.
stignore_copied=0
if [ ! -f "$WATCH_DIR/.stignore" ]; then
    # The weaker case gets the same default as the other one on purpose: here
    # NOTHING is excluded, not even the credentials, so leaving it as it is is
    # the worse of the two answers.
    printf '\nWARNING: %s/.stignore is missing — nothing is excluded,\n' \
        "$WATCH_DIR" >&2
    printf 'not even the credentials.\n' >&2
    if ask_yes_no "Take the authoritative version now?" "y"; then
        cp "$SCRIPT_DIR/.stignore" "$WATCH_DIR/.stignore"
        stignore_copied=1
    else
        warn "Carrying on without an exclusion list. Take it with:
    cp $SCRIPT_DIR/.stignore $WATCH_DIR/.stignore"
    fi
elif cmp -s "$SCRIPT_DIR/.stignore" "$WATCH_DIR/.stignore"; then
    printf 'The exclusion list matches the authoritative version.\n'
else
    # The differences are listed in full BEFORE the question: the answer is
    # about them, and an offer to overwrite something unseen would be no offer.
    stignore_diff="$(diff -u "$WATCH_DIR/.stignore" "$SCRIPT_DIR/.stignore" || true)"
    printf '\nWARNING: %s/.stignore differs from the version in this\n' \
        "$WATCH_DIR" >&2
    printf 'folder. The file does not travel with the synchronisation, so\n' >&2
    printf 'differences between machines never surface by themselves. Diff:\n\n' >&2
    printf '%s\n\n' "$stignore_diff" >&2
    if ask_yes_no "The version here is authoritative. Take it now?" "y"; then
        cp "$SCRIPT_DIR/.stignore" "$WATCH_DIR/.stignore"
        stignore_copied=1
    else
        warn "The difference stays as it is. Take the version here with:
    cp $SCRIPT_DIR/.stignore $WATCH_DIR/.stignore"
    fi
fi

# Only after a copy really happened. Whether Syncthing picks a changed
# .stignore up by itself is stated NOWHERE in its documentation -- neither on
# the page about ignoring files nor in the REST description (checked 22 August
# 2026). The recommendation is therefore the only defensible statement, and it
# is a warn() so that it survives the blocks that follow (doku 3.5).
if [ "$stignore_copied" -eq 1 ]; then
    printf 'Exclusion list taken over.\n'
    warn "Please have Syncthing re-read the folder once:
    $SYNCTHING_GUI
Whether a changed .stignore takes effect by itself is stated nowhere in
Syncthing's documentation — hence the recommendation."
fi
# --- Exclusion list: end ----------------------------------------------------

if command -v pgrep >/dev/null 2>&1 && ! pgrep -x syncthing >/dev/null 2>&1; then
    warn 'Note: Syncthing does not seem to be running right now.
The service is being installed all the same; without a running Syncthing
no conflict copies arise and the hourly notice stays away.'
fi

# --- 4. Install -----------------------------------------------------------

printf 'Installing %s …\n' "$UNIT_NAME"

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

printf '\nDone, service restarted. Status:\n\n'
systemctl --user --no-pager status "$UNIT_NAME" || true

printf '\nFollow the running output with:\n'
printf '    journalctl --user -u %s -f\n' "$UNIT_NAME"
printf 'Unregister again with:\n'
printf '    %s/uninstall_service.sh\n' "$SCRIPT_DIR"
