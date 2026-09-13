#!/usr/bin/env python3
"""Which files changed since <ref> carry a date line, and is that line current?

The point is the second state: a file that was changed but whose date line
still names a day older than that change. The comparison is against the last
commit that touched the file within the range -- not against today. A pass run
against the release branch usually spans many days, and every correctly dated
file would otherwise be reported as outstanding.

Only committed work is visible here: the range is <ref>..HEAD. Uncommitted
changes in the working tree do not show up at all, so this tool is meaningful
after the checkpoint commit of a stage, not before it.

Files without any date line are listed separately, because most of them are
supposed to have none -- code, development files, archives.

Usage:  datelines-since.py <ref> [<heutiges-datum>]
Example: datelines-since.py master 2026-09-10
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from unfinished import is_unfinished  # noqa: E402

DATE_LINE = re.compile(r"^\*(?:Stand|Last updated): (\d{4}-\d{2}-\d{2})\*")


def git(root, *args):
    return subprocess.run(
        ["git", "-C", root, *args], capture_output=True, text=True, check=True
    ).stdout


def repo_root():
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def changed_paths(root, ref):
    """Paths changed since <ref>, NUL-separated.

    -z is not a nicety: without it git quotes paths holding non-ASCII
    characters, and every such file would silently drop out of both lists.
    """
    out = git(root, "diff", "--name-only", "-z", f"{ref}..HEAD")
    return [p for p in out.split("\0") if p]


def date_line_of(path):
    """The date a file's date line names, or None if it carries none."""
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                found = DATE_LINE.match(line)
                if found:
                    return found.group(1)
    except OSError:
        return None
    return None


def last_change_of(root, ref, rel_path):
    """Commit date of the newest commit in <ref>..HEAD that touched the file."""
    out = git(root, "log", "-1", "--format=%cs", f"{ref}..HEAD", "--", rel_path)
    return out.strip() or None


def main(argv):
    if len(argv) < 2:
        print("Referenz fehlt, z. B. ein Commit oder ein Zweigname", file=sys.stderr)
        return 1
    ref = argv[1]
    today = argv[2] if len(argv) > 2 else date.today().isoformat()

    root_text = repo_root()
    root = Path(root_text)

    with_line = []
    without_line = []
    for rel in changed_paths(root_text, ref):
        if is_unfinished(rel):
            continue
        path = root / rel
        if not path.is_file():
            continue
        dated = date_line_of(path)
        if dated is None:
            without_line.append(rel)
            continue
        changed = last_change_of(root_text, ref, rel)
        if changed is None:
            # The file differs between the branches without a commit on this
            # side having touched it -- it was changed or removed on the other
            # side. There is nothing to pull forward here, and no date to
            # compare against; inventing one would produce a false alarm.
            state, changed = "unberuehrt", "-"
        elif dated > today:
            state = "ZUKUNFT"
        elif dated < changed:
            state = "NACHZIEHEN"
        else:
            state = "ok"
        with_line.append((state, rel, dated, changed))

    print(f"Geaendert seit {ref}, mit Datumszeile:")
    for state, rel, dated, changed in with_line:
        print(f"  {state:<11}{rel:<52} Datumszeile {dated}  letzte Aenderung {changed}")

    print()
    print(f"Geaendert seit {ref}, ohne Datumszeile (meist richtig so):")
    for rel in without_line:
        print(f"  {rel}")

    print()
    print("Zu lesen:")
    print("  ok          Datumszeile ist nicht aelter als die letzte Aenderung der Datei.")
    print("  NACHZIEHEN  Datei wurde nach dem Datum ihrer Datumszeile geaendert.")
    print("  ZUKUNFT     Datumszeile liegt hinter dem heutigen Tag -- Zahlendreher?")
    print("  unberuehrt  Seit <ref> hat kein Commit dieses Zweiges die Datei angefasst;")
    print("              der Unterschied stammt von der Gegenseite. Nichts nachzuziehen.")
    print("  Nur Committetes ist sichtbar: der Lauf gilt nach dem Checkpoint-Commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
