#!/usr/bin/env python3
"""Full comparison of two branches, with the exclusion classes of this repo.

Prints one line per difference, grouped into what has to be transferred, what
has to be deleted in the target, and what stays out on purpose. Writes the two
work lists NUL-separated so they can be fed to `xargs -0`, which keeps paths
with spaces and non-ASCII folder names intact.

Infra files are never taken from the source branch: they are distributed from
the infra branch. Their list is read from .claude/git-worktree-model.json, so
it cannot drift away from the agreement.

The work lists are always written. Without --out they go into a fresh
temporary directory whose path is printed at the end -- relying on $TMPDIR
would break outside the sandbox, where that variable does not exist.

Usage:
    branch-diff.py [--from dev] [--to master] [--out DIR] [--exclude REGEX]...
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Three classes are deliberately absent from the release branch: skill folders
# whose name does not start with an alphanumeric character (they carry a
# construction sign), the research material, and the project's own skills under
# .claude/skills/ -- those are working equipment of the development branch, this
# skill included, and a tool that produces the release branch has no business
# inside it. The third pattern hangs on the prefix and not on a folder name, so
# a second project skill is covered without anyone having to remember it.
DEFAULT_EXCLUDES = [r"^skills/(?![A-Za-z0-9])", r"^\.research/",
                    r"^\.claude/skills/"]


def run(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def repo_root() -> Path:
    return Path(run("git", "rev-parse", "--show-toplevel").strip())


def infra_patterns(root: Path) -> list[str]:
    model = root / ".claude" / "git-worktree-model.json"
    if not model.is_file():
        return []
    entries = json.loads(model.read_text(encoding="utf-8")).get("infra_files", [])
    out = []
    for e in entries:
        e = e.rstrip("/")
        out.append(rf"^{re.escape(e)}(/|$)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default="dev")
    ap.add_argument("--to", dest="dst", default="master")
    ap.add_argument("--out", default=None,
                    help="Ablage der beiden Arbeitslisten; ohne Angabe ein neues Temporaerverzeichnis")
    ap.add_argument("--exclude", action="append", default=[])
    args = ap.parse_args()

    root = repo_root()
    excl = [re.compile(p) for p in DEFAULT_EXCLUDES + args.exclude]
    infra = [re.compile(p) for p in infra_patterns(root)]

    # --no-renames is load-bearing, not a preference: with rename detection a
    # renamed file arrives as ONE record of THREE fields (R100, old, new),
    # while every other record has two. The loop below pairs them two by two,
    # so a single rename shifts everything behind it by one field -- status
    # letters end up in the path slot and the old name lands in the take list
    # instead of the delete list. Measured on 11 September 2026: one R100 in
    # the comparison, 24 bogus entries behind it. Without rename detection git
    # reports the same change as "D old" plus "A new", which is exactly the
    # pair of lists this script keeps.
    raw = run("git", "diff", "--name-status", "--no-renames", "-z",
              args.dst, args.src)
    fields = raw.split("\0")
    take: list[str] = []
    dele: list[str] = []
    skipped_excl: list[str] = []
    skipped_infra: list[str] = []

    i = 0
    while i < len(fields) - 1 and fields[i]:
        status, path = fields[i], fields[i + 1]
        i += 2
        if any(r.match(path) for r in excl):
            skipped_excl.append(path)
        elif any(r.match(path) for r in infra):
            skipped_infra.append(path)
        elif status == "D":
            dele.append(path)
        else:
            take.append(path)

    print(f"Vergleich {args.dst} <- {args.src}\n")
    print(f"Zu uebernehmen: {len(take)}")
    for p in take:
        print(f"  + {p}")
    print(f"\nIn {args.dst} zu loeschen: {len(dele)}")
    for p in dele:
        print(f"  - {p}")
    print(f"\nBewusst ausgeschlossen: {len(skipped_excl)}")
    for p in skipped_excl:
        print(f"  . {p}")
    print(f"\nInfra-Dateien (kommen aus dem infra-Zweig): {len(skipped_infra)}")
    for p in skipped_infra:
        print(f"  i {p}")

    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="repo-cleanup-"))
    out.mkdir(parents=True, exist_ok=True)
    for name, items in (("take.z", take), ("dele.z", dele)):
        data = "\0".join(items) + ("\0" if items else "")
        (out / name).write_text(data, encoding="utf-8")
    print(f"\nArbeitslisten: {out}/take.z  und  {out}/dele.z")
    print(f"Diesen Pfad in den naechsten Schritten verwenden: LISTEN={out}")

    if not take and not dele:
        print("\nNichts zu tun: Die Zweige unterscheiden sich nur im Ausgeschlossenen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
