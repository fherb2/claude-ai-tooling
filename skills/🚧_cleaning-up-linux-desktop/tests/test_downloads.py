"""Rule 4.9 of delete.py: everything directly in the download folders older than x days goes.

Builds a throwaway home with a download folder, simulates the clock (the rule runs 40 days
ahead; "young" items carry a modification time one day before that), runs the rule first as a
dry run and then for real, and checks entry by entry what is gone and what is kept. Mount
points are simulated through the mount list; every file system call on them is recorded.
Needs no root. Prints PASSED or the list of deviations.

Usage: python3 -I tests/test_downloads.py [--delete <delete.py>]
    --delete: test another version of delete.py (negative control with a deliberately broken copy)
"""

import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DAY = 86400


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make(path, data=b"x", age="old", later=None):
    """A file; age 'young' sets the modification time to one day before the simulated time."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)
    if age == "young":
        os.utime(path, (later - DAY, later - DAY))


def young_dir(path, later):
    os.makedirs(path, exist_ok=True)
    os.utime(path, (later - DAY, later - DAY))


def build(base, later):
    """The tree and the expectation 'gone' or 'kept' for every first-level entry."""
    home = os.path.join(base, "home", "user")
    dl, other = os.path.join(home, "Downloads"), os.path.join(home, "Browser")
    expect = {}

    def f(folder, name, want, age="old", data=b"x"):
        make(os.path.join(folder, name), data, age, later)
        expect[os.path.join(folder, name)] = want

    f(dl, "old-big.iso", "gone", data=b"\0" * 3_000_000)
    f(dl, "old-small.txt", "gone")
    f(dl, "young.pdf", "kept", "young")
    f(dl, "old.crdownload", "gone")
    f(dl, "young.crdownload", "kept", "young")
    f(dl, "excluded.iso", "kept")
    f(dl, "cleaning-up-linux-desktop-backup-x.tar", "kept")
    # folders: the youngest element at any depth decides
    make(os.path.join(dl, "olddir", "a.txt"))
    make(os.path.join(dl, "olddir", "sub", "b.txt"))
    expect[os.path.join(dl, "olddir")] = "gone"
    make(os.path.join(dl, "mixeddir", "old.txt"))
    make(os.path.join(dl, "mixeddir", "deep", "er", "est", "young.txt"), age="young", later=later)
    expect[os.path.join(dl, "mixeddir")] = "kept"
    make(os.path.join(dl, "subyoungdir", "old.txt"))
    young_dir(os.path.join(dl, "subyoungdir", "fresh"), later)          # a young subfolder counts
    expect[os.path.join(dl, "subyoungdir")] = "kept"
    # empty folders: their own date counts
    os.makedirs(os.path.join(dl, "emptyold"))
    expect[os.path.join(dl, "emptyold")] = "gone"
    young_dir(os.path.join(dl, "emptyyoung"), later)
    expect[os.path.join(dl, "emptyyoung")] = "kept"
    os.makedirs(os.path.join(dl, "onlyemptysubs", "x", "y"))
    expect[os.path.join(dl, "onlyemptysubs")] = "gone"
    # a link is only reported, its target stays
    make(os.path.join(home, "Bilder", "target.jpg"))
    os.symlink(os.path.join(home, "Bilder", "target.jpg"), os.path.join(dl, "link"))
    expect[os.path.join(dl, "link")] = "kept"
    expect[os.path.join(home, "Bilder", "target.jpg")] = "kept"
    # mount points (simulated): one directly in the folder, one inside an old folder
    make(os.path.join(dl, "mnt", "inner"))
    expect[os.path.join(dl, "mnt")] = "kept"
    make(os.path.join(dl, "hasmount", "data"))
    make(os.path.join(dl, "hasmount", "m", "inner"))
    expect[os.path.join(dl, "hasmount")] = "kept"
    mounts = [os.path.join(dl, "mnt"), os.path.join(dl, "hasmount", "m")]
    # a second download folder (a browser target)
    f(other, "old.bin", "gone")
    f(other, "young.bin", "kept", "young")
    return home, dl, other, expect, mounts


def removed_names(report, base):
    return sorted(os.path.relpath(r["path"], base) for r in report["removed"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete", default=os.path.join(HERE, "..", "delete.py"))
    args = parser.parse_args()
    d = load("delete", args.delete)
    mounts_test = load("test_mounts", os.path.join(HERE, "test_mounts.py"))
    base = tempfile.mkdtemp(prefix="cleanup-downloads-", dir="/tmp")
    problems = []
    try:
        later = time.time() + 40 * DAY
        home, dl, other, expect, mounts = build(base, later)
        real_points = d.mount_points
        d.mount_points = lambda: real_points() | set(mounts)
        d.WALK.home = home
        d.WALK.read_at = None
        exclude = [os.path.join(dl, "excluded.iso")]
        params = {"days": 14, "folders": [dl, other], "exclude": exclude}
        # dry run: nothing changes, the report names what would go
        with mounts_test.Recorder(mounts, []) as rec:
            dry = d.Report("4.9", True)
            d.rule_downloads(d.Deleter(home, True, dry), home, params, later)
        for path, want in expect.items():
            if not os.path.lexists(path):
                problems.append(f"dry run changed something: {os.path.relpath(path, base)} is gone")
        wanted_gone = sorted(os.path.relpath(p, base) for p, w in expect.items() if w == "gone")
        if removed_names(dry.data, base) != wanted_gone:
            problems.append(f"dry run lists {removed_names(dry.data, base)}, expected {wanted_gone}")
        # real run
        with mounts_test.Recorder(mounts, []) as rec2:
            real = d.Report("4.9", False)
            d.rule_downloads(d.Deleter(home, False, real), home, params, later)
        for hit in sorted(set(rec.hits + rec2.hits)):
            problems.append(f"touched a mount point: {hit}")
        for path, want in sorted(expect.items()):
            present = os.path.lexists(path)
            if (want == "gone") == present:
                problems.append(f"{'still there' if present else 'deleted'}: {os.path.relpath(path, base)} (expected {want})")
        if removed_names(real.data, base) != wanted_gone:
            problems.append(f"real run lists {removed_names(real.data, base)}, expected {wanted_gone}")
        reasons = {os.path.relpath(s["path"], base): s["reason"] for s in real.data["skipped"]}
        for rel, reason in {
                "home/user/Downloads/excluded.iso": "excluded by the user",
                "home/user/Downloads/link": "symbolic link",
                "home/user/Downloads/cleaning-up-linux-desktop-backup-x.tar": "own snapshot or archive (prefix)",
                "home/user/Downloads/hasmount": "is or contains a mount point"}.items():
            if reasons.get(rel) != reason:
                problems.append(f"skipped {rel}: {reasons.get(rel)!r}, expected {reason!r}")
        sizes = {os.path.relpath(r["path"], base): r["size"] for r in real.data["removed"]}
        if sizes.get("home/user/Downloads/old-big.iso") != 3_000_000:
            problems.append(f"size of the big file in the report: {sizes.get('home/user/Downloads/old-big.iso')}")
        # the wiring: order file, area table, the list kind is refused for 4.9
        order = os.path.join(base, "order.json")
        report = os.path.join(base, "report.json")
        make(os.path.join(dl, "wiring.txt"))
        for kind, body, code in (("rule", {"area": "4.9", "kind": "rule", "params": {**params, "days": 0,
                                                                                   "folders": [dl]}}, 0),
                                 ("list", {"area": "4.9", "kind": "list", "paths": [os.path.join(dl, "wiring.txt")]}, 2)):
            with open(order, "w", encoding="utf-8") as fh:
                json.dump(body, fh)
            argv, sys.argv = sys.argv, ["delete.py", "--home", home, "--order", order, "--dry-run", "--report", report]
            try:
                got = d.main()
            finally:
                sys.argv = argv
            if got != code:
                problems.append(f"order kind {kind} for 4.9: exit {got}, expected {code}")
        if not os.path.exists(os.path.join(dl, "wiring.txt")):
            problems.append("the dry run through main() deleted a file")
    finally:
        shutil.rmtree(base)
    if problems:
        print(f"FAILED ({len(problems)} deviations):")
        for line in problems:
            print("  " + line)
        return 1
    print("PASSED: 4.9 by age (files, folders by the youngest element at any depth, empty folders), "
          "exclusions, link, own prefix, mount points untouched, dry run equals real run, order wiring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
