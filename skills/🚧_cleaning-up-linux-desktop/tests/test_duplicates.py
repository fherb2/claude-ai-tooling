"""The duplicate search of analyze.py (Table 3), hashed by a pool of workers.

The result of find_duplicates must equal two references: an independent one (group by size and the
full SHA-256) for the groups, and the former sequential algorithm for order and read errors, ties
included. Cases: identical files, equal start but different end, equal size but different start,
exactly one MiB, one byte more than a MiB, a file that vanished since the walk, ties, many groups
and a file on a simulated mount point (never hashed). Runs with the real core count, with one
worker and with more workers than tasks. Needs no root. Prints PASSED or the deviations.

Usage: python3 -I tests/test_duplicates.py [--analyze <analyze.py>]
    --analyze: test another version of analyze.py (negative control with a deliberately broken copy)
"""

import argparse
import hashlib
import importlib.util
import os
import random
import shutil
import sys
import tempfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MiB = 1024 * 1024


def load(path):
    spec = importlib.util.spec_from_file_location("analyze", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze"] = module          # the pool pickles hash_task by its module name
    spec.loader.exec_module(module)
    return module


def content(seed, size, tail=None, head=None):
    data = bytearray(random.Random(seed).randbytes(size))
    if tail is not None:
        data[-1] = tail
    if head is not None:
        data[0] = head
    return bytes(data)


def build(base):
    """Candidates as the walk would have collected them: {size: [paths]}; also the mount point."""
    home = os.path.join(base, "home", "user")
    by_size = defaultdict(list)

    def put(rel, data):
        path = os.path.join(home, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
        by_size[len(data)].append(path)
        return path

    for i in range(3):                                   # A: three identical files
        put(f"a/{i}/same.bin", content(1, 2 * MiB + 5))
    put("b/one", content(2, 3 * MiB, tail=1))            # B: equal start, different end
    put("b/two", content(2, 3 * MiB, tail=2))
    put("c/one", content(3, 3 * MiB + 7, head=1))        # C: different start
    put("c/two", content(3, 3 * MiB + 7, head=2))
    put("d/one", content(4, MiB))                        # D: exactly one MiB, identical
    put("d/two", content(4, MiB))
    put("e/one", content(5, MiB, head=1))                # E: exactly one MiB, different
    put("e/two", content(5, MiB, head=2))
    put("g/one", content(6, MiB + 1, tail=1))            # G: one byte more than a MiB, different end
    put("g/two", content(6, MiB + 1, tail=2))
    put("f/one", content(7, 2 * MiB))                    # F: identical pair and a file that vanished
    put("f/two", content(7, 2 * MiB))
    by_size[2 * MiB].append(os.path.join(home, "f", "vanished"))
    for i in range(4):                                   # I: two pairs of one size: a tie in the order
        put(f"i/{i}", content(8 + i // 2, 2 * MiB + 11))
    for k in range(40):                                  # many groups for the chunked first round
        put(f"many/{k}/x", content(100 + k, MiB + 100 + k))
        put(f"many/{k}/y", content(100 + k, MiB + 100 + k))
    mount = os.path.join(home, "mnt")                    # H: one copy lies on a (simulated) mount point
    put("h/real", content(50, 2 * MiB + 99))
    put("mnt/copy", content(50, 2 * MiB + 99))
    return home, mount, by_size


def reference_sequential(a, by_size, mount, stats):
    """The former algorithm of analyze.py, one file after the other (copied; the mount filter added)."""
    groups = []
    sizes = []
    for s, paths in by_size.items():
        paths = [p for p in paths if not (p == mount or p.startswith(mount + os.sep))]
        if len(paths) > 1:
            sizes.append((s, paths))
    for size, paths in sorted(sizes, reverse=True):
        by_start = defaultdict(list)
        for path in paths:
            try:
                by_start[a.file_hash(path, a.PARTIAL)].append(path)
            except OSError:
                stats["read_errors"] += 1
        for same_start in by_start.values():
            if len(same_start) < 2:
                continue
            by_content = defaultdict(list)
            for path in same_start:
                try:
                    by_content[a.file_hash(path) if size > a.PARTIAL else ""].append(path)
                except OSError:
                    stats["read_errors"] += 1
            groups.extend({"size": size, "paths": sorted(g)} for g in by_content.values() if len(g) > 1)
    return sorted(groups, key=lambda g: g["size"] * (len(g["paths"]) - 1), reverse=True)


def independent(by_size, mount):
    """Groups by size and the full SHA-256 only."""
    found = defaultdict(list)
    for size, paths in by_size.items():
        for p in paths:
            if p == mount or p.startswith(mount + os.sep) or not os.path.exists(p):
                continue
            with open(p, "rb") as fh:
                found[(size, hashlib.sha256(fh.read()).hexdigest())].append(p)
    return {(size, tuple(sorted(ps))) for (size, _), ps in found.items() if len(ps) > 1}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", default=os.path.join(HERE, "..", "analyze.py"))
    args = parser.parse_args()
    a = load(args.analyze)
    base = tempfile.mkdtemp(prefix="cleanup-duplicates-", dir="/tmp")
    problems = []
    try:
        home, mount, by_size = build(base)
        real_points = a.mount_points
        a.mount_points = lambda: real_points() | {mount}
        a.WALK.home = home
        a.WALK.read_at = None
        expected = independent(by_size, mount)
        ref_stats = {"read_errors": 0, "files": 0}
        ref = reference_sequential(a, by_size, mount, ref_stats)
        if {(g["size"], tuple(g["paths"])) for g in ref} != expected:
            problems.append("the sequential reference and the independent one disagree (test fixture broken)")
        if ref_stats["read_errors"] != 1:
            problems.append(f"fixture: expected one read error in the reference, got {ref_stats['read_errors']}")
        real_cores = a.physical_cores
        for label, cores in (("real core count", real_cores), ("one worker", lambda: 1),
                             ("more workers than tasks", lambda: 4000)):
            a.physical_cores = cores
            candidate = a.DuplicateCandidates()
            candidate.by_size.update({s: list(p) for s, p in by_size.items()})
            stats = {"read_errors": 0, "files": 0}
            seen = []
            try:
                got = a.find_duplicates(candidate, stats, lambda text, files: seen.append(text))
            except Exception as exc:  # noqa: BLE001 - a crash is a finding of this test
                problems.append(f"{label}: find_duplicates raised {exc!r}")
                continue
            if {(g["size"], tuple(g["paths"])) for g in got} != expected:
                problems.append(f"{label}: groups differ from the independent reference")
            if got != ref:
                problems.append(f"{label}: result or order differs from the sequential version")
            if stats["read_errors"] != 1:
                problems.append(f"{label}: read errors {stats['read_errors']}, expected 1")
            keys = [g["size"] * (len(g["paths"]) - 1) for g in got]
            if keys != sorted(keys, reverse=True):
                problems.append(f"{label}: not sorted by the surplus")
            if not any(t.startswith("hashing first MiB") for t in seen) or \
                    not any(t.startswith("hashing content") for t in seen):
                problems.append(f"{label}: progress lines of both rounds missing: {seen[:3]}")
        a.physical_cores = real_cores
        # nothing to do: no pool, empty result
        empty = a.DuplicateCandidates()
        if a.find_duplicates(empty, {"read_errors": 0, "files": 0}, lambda *x: None) != []:
            problems.append("empty candidates: expected []")
    finally:
        shutil.rmtree(base)
    if problems:
        print(f"FAILED ({len(problems)} deviations):")
        for line in problems:
            print("  " + line)
        return 1
    print("PASSED: groups equal the independent reference, result and order equal the sequential version "
          "(3 worker counts), read error counted, mount point never hashed, progress of both rounds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
