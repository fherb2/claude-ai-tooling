#!/usr/bin/env python3
"""test_conflict_terminal_loop.py -- manual, interactive probe of the
intended retry loop between the conflict question dialog and the terminal
disambiguation dialog.

Usage:
    python3 test_conflict_terminal_loop.py

Background: currently, if the user cancels the zenity --list terminal
disambiguation in detect_terminal(), the real fossil_claude_sync.py
silently falls back to the first found candidate. The intended behavior
instead: on cancel, re-show the conflict question dialog with adjusted
wording, asking whether to retry the terminal selection or abandon
resolving the conflict for this run. Abandoning is NOT caught by a further
confirmation -- it simply ends this run's conflict handling; the next
cycle that still finds a conflict will show the initial dialog again on
its own (existing dialog_due() cooldown in the real script).

This script prototypes exactly that control flow with zenity, against a
dummy candidate list (same ones already validated in test_zenity_list.py).
It does not import fossil_claude_sync and does not touch its real state
file -- purely a standalone control-flow probe.
"""

import subprocess

FOUND = [
    ("gnome-terminal", "--"),
    ("konsole", "-e"),
    ("xterm", "-e"),
]

DUMMY_FILES = ["CLAUDE.md"]


def ask_resolve_now(retry_wording: bool) -> bool:
    """Show the conflict question dialog. Returns True for 'resolve now'."""
    if retry_wording:
        text = (
            "Zur Bearbeitung des Konflikts wird ein Terminal für die "
            "Claude-Sitzung benötigt.\n\nAuswahl erneut versuchen?"
        )
        ok_label, cancel_label = "Erneut versuchen", "Abbrechen"
    else:
        file_list = "\n".join(DUMMY_FILES)
        text = (
            f"Konflikt in:\n{file_list}\n\nZur Bearbeitung öffnet sich eine "
            "Claude-Code-Sitzung in einem Terminal; dafür muss ggf. ein "
            "Terminal-Programm ausgewählt werden.\n\nJetzt lösen?"
        )
        ok_label, cancel_label = "Jetzt lösen", "Später"

    result = subprocess.run(
        ["zenity", "--question", "--title=Claude-Sync: Merge-Konflikt",
         f"--text={text}", f"--ok-label={ok_label}", f"--cancel-label={cancel_label}"],
    )
    return result.returncode == 0


def pick_terminal():
    """Show the terminal disambiguation dialog. Returns the chosen binary
    name, or None if cancelled."""
    pick = subprocess.run(
        ["zenity", "--list", "--title=Terminal wählen",
         "--text=Mehrere Terminal-Emulatoren gefunden, welcher soll verwendet werden?",
         "--column=Terminal", *[b for b, _ in FOUND]],
        capture_output=True, text=True,
    )
    selected = pick.stdout.strip()
    return selected or None


def main() -> int:
    retry_wording = False
    while True:
        if not ask_resolve_now(retry_wording):
            print(
                "User chose 'Später'/'Abbrechen' -> ending this run's "
                "conflict handling. No further dialog now; the next cycle "
                "that still sees a conflict will show the initial dialog "
                "again on its own."
            )
            return 0

        selected = pick_terminal()
        if selected is not None:
            print(f"Terminal selected: {selected!r} -> would launch Claude session now.")
            return 0

        print(
            "Terminal selection cancelled -> looping back to the conflict "
            "question dialog with retry wording."
        )
        retry_wording = True


if __name__ == "__main__":
    raise SystemExit(main())
