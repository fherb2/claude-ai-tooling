#!/usr/bin/env python3
"""test_detect_terminal.py -- manual, interactive probe of the terminal
detection and launch logic used in claude_sync_watchd.py's
detect_terminal() / launch_claude_session().

Usage:
    python3 test_detect_terminal.py

Reimplements the detection cascade (xdg-terminal-exec check, then the
TERMINAL_CANDIDATES fallback list via shutil.which, then the zenity --list
disambiguation for multiple matches) standalone, WITHOUT importing
claude_sync_watchd or touching its real state file under
~/.claude-sync-watch/ -- this probe must stay side-effect-free
outside of this tests/ directory.

Once a terminal command is chosen, it launches
    [*terminal_cmd, str(HELPER_SCRIPT), TEST_PROMPT]
which mirrors the real argv shape from launch_claude_session()
(`[*terminal_cmd, CLAUDE_BINARY, "--append-system-prompt-file", ..., prompt]`), but with the "claude" program
replaced by the harmless echo_test_helper.sh shipped alongside this
script, so the actual `claude` CLI is never invoked by this test. Confirm
by eye whether a terminal window opens and displays TEST_PROMPT unchanged,
including its spaces and quote characters.
"""

import shutil
import subprocess
from pathlib import Path

# Mirrors claude_sync_watchd.py's TERMINAL_CANDIDATES exactly.
TERMINAL_CANDIDATES: list[tuple[str, str]] = [
    ("x-terminal-emulator", "-e"),
    ("gnome-terminal", "--"),
    ("konsole", "-e"),
    ("xfce4-terminal", "-e"),
    ("alacritty", "-e"),
    ("kitty", "-e"),
    ("xterm", "-e"),
]

HELPER_SCRIPT = Path(__file__).parent / "echo_test_helper.sh"

TEST_PROMPT = (
    'Syncthing left a conflict copy of "CLAUDE.md" behind -- '
    "please check: spaces, \"double quotes\", and it's apostrophes all survive?"
)


def detect() -> list[str]:
    if shutil.which("xdg-terminal-exec"):
        print("xdg-terminal-exec found -> would be used directly.")
        return ["xdg-terminal-exec", "--"]

    print("xdg-terminal-exec NOT found -> falling back to candidate list.")
    found = [(b, a) for b, a in TERMINAL_CANDIDATES if shutil.which(b)]
    print(f"Candidates found on this machine: {[b for b, _ in found]}")

    if len(found) == 1:
        binary, arg = found[0]
        print(f"Exactly one match -> using it directly: {binary}")
        return [binary, arg]

    if len(found) > 1:
        print("Multiple matches -> asking via zenity --list (same as detect_terminal()).")
        pick = subprocess.run(
            ["zenity", "--list", "--title=Terminal wählen",
             "--text=Mehrere Terminal-Emulatoren gefunden, welcher soll verwendet werden?",
             "--column=Terminal", *[b for b, _ in found]],
            capture_output=True, text=True,
        )
        selected = pick.stdout.strip() or found[0][0]
        arg = dict(found)[selected]
        print(f"zenity returned: {pick.stdout!r} -> chosen = [{selected!r}, {arg!r}]")
        return [selected, arg]

    print("No known terminal emulator found -> would fall back to a zenity --entry prompt.")
    entry = subprocess.run(
        ["zenity", "--entry", "--title=Terminal-Emulator",
         "--text=Kein bekannter Terminal-Emulator gefunden. Bitte Befehl angeben:"],
        capture_output=True, text=True,
    )
    binary = entry.stdout.strip() or "xterm"
    return [binary, "-e"]


def main() -> int:
    terminal_cmd = detect()
    argv = [*terminal_cmd, str(HELPER_SCRIPT), TEST_PROMPT]
    print(f"Launching: {argv}")

    proc = subprocess.Popen(argv, start_new_session=True)
    print(
        f"Popen started (pid {proc.pid}). A terminal window should now open "
        "showing the test prompt between two '---' lines, then stay open "
        "8 seconds. Please confirm by eye whether the text matches exactly."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
