#!/usr/bin/env python3
"""test_fossil_resolution_flow.py -- tests the script-driven conflict
resolution flow end to end, in two candidate orderings.

Usage:
    python3 test_fossil_resolution_flow.py

Throwaway repositories under tests/test_data/, no network, real topology
(server + one clone per machine, each with its own check-out).

The flow being validated (decided with the user):
    everything runs script-driven; a Claude session is started ONLY when
    `fossil update` would not be able to update every file because of real
    conflicts. The session then classifies each conflicted file as
        take    -- incoming wins, the local edit may be discarded
        keep    -- local wins, the incoming change must not be applied
        puzzle  -- neither wins, the file has to be merged by hand
    and afterwards the update runs, the hand-merged files are put in
    place, and a commit advances the remote head with the correction.

Two candidate orderings for the last part:
    FLOW A  revert the `take` files, then a FILE-RESTRICTED update that
            names only the files which may move, then write the puzzled
            content, then commit. Never writes a conflict marker to disk.
            Open question: `fossil help update` says a restricted update
            does NOT move the check-out version -- so does the final
            commit end up forking?
    FLOW B  revert the `take` files, stash the `keep`/`puzzle` content,
            run a FULL update (which does write markers for the still
            conflicting files), restore the stashed content over them,
            then commit. Moves the check-out version properly, but the
            check-out holds conflict markers for a moment.

Success for either flow means all of:
    - the commit succeeds
    - the repository has exactly ONE open leaf afterwards (no fork)
    - the push is accepted and the server head advances
    - every file holds the intended content and no conflict markers

Transcript: tests/test_data/resolution_flow_probe.log
"""

import shutil
import subprocess
from pathlib import Path

TEST_DATA = Path(__file__).parent / "test_data"
WORK_ROOT = TEST_DATA / "resolution_flow"
LOG_PATH = TEST_DATA / "resolution_flow_probe.log"

BASE_LINES = ["line 1", "line 2", "line 3 -- BASE", "line 4", "line 5"]

# f_clean is changed by the other machine only -> must update silently.
FILES = ["f_take.txt", "f_keep.txt", "f_puzzle.txt", "f_clean.txt"]

_log_handle = None


def log(text: str) -> None:
    _log_handle.write(text + "\n")
    _log_handle.flush()


def run(args: list[str], cwd: Path, expect_fail: bool = False) -> subprocess.CompletedProcess:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    log(f"\n$ (in {cwd.name}) {' '.join(args)}")
    log(f"  rc={result.returncode}")
    for stream, name in ((result.stdout, "out"), (result.stderr, "err")):
        for line in stream.splitlines():
            log(f"  {name}| {line}")
    if result.returncode != 0 and not expect_fail:
        log("  NOTE: non-zero exit was not expected here.")
    return result


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def edit_line3(path: Path, marker: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[2] = f"line 3 -- {marker}"
    write_lines(path, lines)


def has_markers(path: Path) -> bool:
    return path.is_file() and "BEGIN MERGE CONFLICT" in path.read_text(
        encoding="utf-8", errors="ignore")


def line3(path: Path) -> str:
    return path.read_text(encoding="utf-8").splitlines()[2]


def checkout_version(cwd: Path) -> str:
    result = run(["fossil", "info"], cwd=cwd)
    for line in result.stdout.splitlines():
        if line.startswith("checkout:"):
            return line.split()[1]
    return ""


def tip_version(cwd: Path) -> str:
    result = run(["fossil", "timeline", "-n", "1", "-t", "ci", "-W", "0"], cwd=cwd)
    for line in result.stdout.splitlines():
        if "[" in line and "]" in line:
            return line.split("[", 1)[1].split("]", 1)[0]
    return ""


def open_leaf_count(cwd: Path) -> int:
    result = run(["fossil", "leaves"], cwd=cwd)
    return len([line for line in result.stdout.splitlines() if line.strip()])


def build(name: str) -> tuple[Path, Path]:
    """Set up the conflict situation. Returns (co_a, co_b)."""
    log("\n" + "=" * 70)
    log(f"BUILDING: {name}")
    log("=" * 70)

    root = WORK_ROOT / name
    root.mkdir(parents=True)
    server = root / "server.fossil"
    run(["fossil", "init", str(server)], cwd=root)

    co = {}
    for machine in ("a", "b"):
        repo = root / f"{machine}.fossil"
        path = root / f"co_{machine}"
        path.mkdir()
        run(["fossil", "clone", str(server), str(repo)], cwd=root)
        run(["fossil", "open", str(repo)], cwd=path)
        co[machine] = path
    co_a, co_b = co["a"], co["b"]

    for filename in FILES:
        write_lines(co_a / filename, BASE_LINES)
    run(["fossil", "add", "."], cwd=co_a)
    run(["fossil", "commit", "-m", "base", "--no-warnings"], cwd=co_a)
    run(["fossil", "push"], cwd=co_a)

    run(["fossil", "pull"], cwd=co_b)
    run(["fossil", "update", "--nosync"], cwd=co_b)

    # The other machine advances every file.
    for filename in FILES:
        edit_line3(co_a / filename, "INCOMING")
    run(["fossil", "commit", "-m", "incoming changes", "--no-warnings"], cwd=co_a)
    run(["fossil", "push"], cwd=co_a)

    # This machine has uncommitted edits on three of them (f_clean is left
    # alone, so it must update without any fuss).
    for filename in ("f_take.txt", "f_keep.txt", "f_puzzle.txt"):
        edit_line3(co_b / filename, "LOCAL")

    run(["fossil", "pull"], cwd=co_b)
    run(["fossil", "update", "-n", "--nosync", "--verbose"], cwd=co_b)
    return co_a, co_b


PUZZLED = "line 3 -- HAND-MERGED by Claude and user"


def verify(co_b: Path, commit_rc: int, label: str) -> dict:
    log(f"\n--- verification for {label} ---")
    push = run(["fossil", "push"], cwd=co_b, expect_fail=True)
    leaves = open_leaf_count(co_b)
    contents = {name: line3(co_b / name) for name in FILES}
    markers = [name for name in FILES if has_markers(co_b / name)]
    for name, value in contents.items():
        log(f"  {name}: {value}")
    log(f"  files still holding markers: {markers}")
    log(f"  open leaves: {leaves}")

    expected = {
        "f_take.txt": "line 3 -- INCOMING",
        "f_keep.txt": "line 3 -- LOCAL",
        "f_puzzle.txt": PUZZLED,
        "f_clean.txt": "line 3 -- INCOMING",
    }
    content_ok = contents == expected
    log(f"  content as intended: {content_ok}")
    if not content_ok:
        for name in FILES:
            if contents[name] != expected[name]:
                log(f"    MISMATCH {name}: got {contents[name]!r}, "
                    f"want {expected[name]!r}")

    return {
        "flow": label,
        "commit_rc": commit_rc,
        "push_rc": push.returncode,
        "leaves": leaves,
        "content_ok": content_ok,
        "markers_left": markers,
        "ok": commit_rc == 0 and push.returncode == 0 and leaves == 1
        and content_ok and not markers,
    }


def flow_a() -> dict:
    log("\n" + "=" * 70)
    log("FLOW A -- revert 'take', file-restricted update, add puzzle, commit")
    log("=" * 70)
    _, co_b = build("flow_a")
    tip = tip_version(co_b)

    # 'take' files: discard the local edit so the update can bring in the
    # incoming version without a merge.
    run(["fossil", "revert", "f_take.txt"], cwd=co_b)

    # Restricted update: only the files that are allowed to move.
    run(["fossil", "update", tip, "f_take.txt", "f_clean.txt", "--verbose"],
        cwd=co_b, expect_fail=True)
    log(f"\n  check-out version after the restricted update: "
        f"{checkout_version(co_b)[:10]} (tip is {tip[:10]})")

    # The hand-merged file is written last.
    lines = (co_b / "f_puzzle.txt").read_text(encoding="utf-8").splitlines()
    lines[2] = PUZZLED
    write_lines(co_b / "f_puzzle.txt", lines)

    commit = run(["fossil", "commit", "-m", "conflict resolved", "--no-warnings"],
                 cwd=co_b, expect_fail=True)
    return verify(co_b, commit.returncode, "A (file-restricted update)")


def flow_b() -> dict:
    log("\n" + "=" * 70)
    log("FLOW B -- revert 'take', stash, full update, restore, commit")
    log("=" * 70)
    _, co_b = build("flow_b")

    run(["fossil", "revert", "f_take.txt"], cwd=co_b)

    # Stash the content that must survive the update untouched.
    stash = {
        name: (co_b / name).read_text(encoding="utf-8")
        for name in ("f_keep.txt", "f_puzzle.txt")
    }

    run(["fossil", "update", "--nosync", "--verbose"], cwd=co_b, expect_fail=True)
    log(f"\n  check-out version after the full update: "
        f"{checkout_version(co_b)[:10]}")
    log(f"  markers present mid-flow: "
        f"{[n for n in FILES if has_markers(co_b / n)]}")

    # Restore 'keep' verbatim, and write the hand-merged content.
    (co_b / "f_keep.txt").write_text(stash["f_keep.txt"], encoding="utf-8")
    lines = stash["f_puzzle.txt"].splitlines()
    lines[2] = PUZZLED
    write_lines(co_b / "f_puzzle.txt", lines)

    run(["fossil", "changes", "--conflict"], cwd=co_b)
    commit = run(["fossil", "commit", "-m", "conflict resolved", "--no-warnings"],
                 cwd=co_b, expect_fail=True)
    return verify(co_b, commit.returncode, "B (full update, restore)")


def flow_c() -> dict:
    """Like B, but every conflicted file is reverted BEFORE the update, so
    the update has nothing left to merge and never writes a marker."""
    log("\n" + "=" * 70)
    log("FLOW C -- stash, revert ALL conflicted files, full update, restore")
    log("=" * 70)
    _, co_b = build("flow_c")

    conflicted = ("f_take.txt", "f_keep.txt", "f_puzzle.txt")
    stash = {
        name: (co_b / name).read_text(encoding="utf-8")
        for name in ("f_keep.txt", "f_puzzle.txt")
    }

    # Drop the local edits on every conflicted file; what has to survive
    # is already held in `stash`.
    run(["fossil", "revert", *conflicted], cwd=co_b)

    run(["fossil", "update", "--nosync", "--verbose"], cwd=co_b, expect_fail=True)
    mid_markers = [n for n in FILES if has_markers(co_b / n)]
    log(f"\n  check-out version after the full update: "
        f"{checkout_version(co_b)[:10]}")
    log(f"  markers present mid-flow: {mid_markers}")
    log("  (the point of this flow: this list must be empty)")

    (co_b / "f_keep.txt").write_text(stash["f_keep.txt"], encoding="utf-8")
    lines = stash["f_puzzle.txt"].splitlines()
    lines[2] = PUZZLED
    write_lines(co_b / "f_puzzle.txt", lines)

    commit = run(["fossil", "commit", "-m", "conflict resolved", "--no-warnings"],
                 cwd=co_b, expect_fail=True)
    result = verify(co_b, commit.returncode, "C (revert all, full update, restore)")
    result["markers_during_flow"] = mid_markers
    result["ok"] = result["ok"] and not mid_markers
    return result


def main() -> int:
    global _log_handle

    if WORK_ROOT.exists():
        shutil.rmtree(WORK_ROOT)
    WORK_ROOT.mkdir(parents=True)

    with LOG_PATH.open("w", encoding="utf-8") as handle:
        _log_handle = handle
        version = subprocess.run(["fossil", "version"], capture_output=True, text=True)
        log(f"fossil version: {version.stdout.strip()}")

        results = [flow_a(), flow_b(), flow_c()]

        log("\n" + "=" * 70)
        log("SUMMARY")
        log("=" * 70)
        for entry in results:
            log(f"  {entry}")

    print(f"Full transcript: {LOG_PATH}")
    for entry in results:
        print(f"  {entry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
