#!/usr/bin/env python3
"""test_zenity_list.py -- manual, interactive probe of the zenity --list
invocation used in fossil_claude_sync.py's detect_terminal() (the branch
that runs when more than one terminal candidate is found).

Usage:
    python3 test_zenity_list.py

Reproduces the exact zenity command shape from detect_terminal() against a
fixed set of dummy terminal names -- NOT real shutil.which() results, since
this probe is only about zenity's behavior, not about terminal detection.
Prints the raw subprocess result and what the real selection logic in
fossil_claude_sync.py would derive from it, so the on-screen dialog
behavior can be compared against the parsed outcome by a human.

Each run shows a single dialog for a single interaction (pick an item,
cancel, close the window, ...); run it again to observe a different one.
"""

import subprocess

FOUND = [
    ("gnome-terminal", "--"),
    ("konsole", "-e"),
    ("xterm", "-e"),
]


def main() -> int:
    pick = subprocess.run(
        ["zenity", "--list", "--title=Terminal wählen",
         "--text=Mehrere Terminal-Emulatoren gefunden, welcher soll verwendet werden?",
         "--column=Terminal", *[b for b, _ in FOUND]],
        capture_output=True, text=True,
    )

    print(f"returncode: {pick.returncode}")
    print(f"stdout (repr): {pick.stdout!r}")
    print(f"stderr (repr): {pick.stderr!r}")

    selected = pick.stdout.strip() or FOUND[0][0]
    print(f"selected (as real script would derive it): {selected!r}")

    found_dict = dict(FOUND)
    if selected not in found_dict:
        print(
            "WARNING: selected value is not a key in dict(FOUND) -- the "
            "real script's dict(found)[selected] lookup would raise "
            "KeyError here."
        )
    else:
        arg = found_dict[selected]
        print(f"resulting chosen = [{selected!r}, {arg!r}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
