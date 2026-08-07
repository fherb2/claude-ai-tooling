#!/usr/bin/env python3
"""test_fossil_silent_merge.py -- checks whether Fossil silently merges two
independent, non-adjacent single-line edits within the SAME file without
ever reporting a conflict, and whether our existing file-set-overlap check
(already used for the dry-run plausibility check, see konzept.md 3.1/1.5)
would still flag that file as touched by both sides.

Usage:
    python3 test_fossil_silent_merge.py

Throwaway repository under tests/test_data/, no network, real topology
(server + one clone per machine). Neither ~/.claude nor claude-config is
touched.

Background: the user pointed out a distinction our design had not made --
a "Fossil conflict" (same line touched on both sides, needs markers) is
not the same thing as "a conflict WE should care about" (two different
lines of the same structured file changed independently; Fossil merges
this silently with no marker at all, but the combination was never seen
or reviewed by anyone -- for a JSONL transcript that is harmless, for
settings.json it may not be). Fossil's own forum confirms this is by
design: "It should never be assumed that an absence of merge conflict
means that the changes are compatible... the algorithm knows nothing of
higher level concepts such as coordinated changes in separate places."
(Larry Brasfield, https://fossil-scm.org/forum/forumpost/6629813f6f)

Scenario:
    base        -> a 7-line file
    other side  -> commits a change to line 2 only
    local side  -> has an UNCOMMITTED change to line 6 only (not adjacent,
                   no insertion/shift involved on either side)

Checked:
    1. Does `fossil update` report ANY conflict for this file? (expect: no)
    2. Does the merged file contain BOTH changes correctly?
    3. Does the file appear in BOTH the locally-changed-file-set (`fossil
       changes`) and the incoming-changed-file-set (`fossil diff --brief`
       between old and new checkout version) -- i.e. would our EXISTING
       file-overlap check (already used for the dry-run plausibility
       check) have flagged this file as touched by both sides, even
       though Fossil itself never raised anything?

Transcript: tests/test_data/silent_merge_probe.log
"""

import shutil
import subprocess
from pathlib import Path

TEST_DATA = Path(__file__).parent / "test_data"
WORK_ROOT = TEST_DATA / "silent_merge_probe"
LOG_PATH = TEST_DATA / "silent_merge_probe.log"

BASE_LINES = [f"line {i} -- BASE" for i in range(1, 8)]  # 7 lines

_log_handle = None


def log(text: str) -> None:
    _log_handle.write(text + "\n")
    _log_handle.flush()


def run(args, cwd, expect_fail: bool = False):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    log(f"\n$ (in {cwd.name}) {' '.join(args)}")
    log(f"  rc={result.returncode}")
    for stream, name in ((result.stdout, "out"), (result.stderr, "err")):
        for line in stream.splitlines():
            log(f"  {name}| {line}")
    if result.returncode != 0 and not expect_fail:
        log("  NOTE: non-zero exit was not expected here.")
    return result


def write_lines(path: Path, lines) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def edit_line(path: Path, line_no_1_based: int, marker: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[line_no_1_based - 1] = f"line {line_no_1_based} -- {marker}"
    write_lines(path, lines)


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


def has_markers(path: Path) -> bool:
    return "BEGIN MERGE CONFLICT" in path.read_text(encoding="utf-8", errors="ignore")


def build_topology():
    root = WORK_ROOT
    root.mkdir(parents=True)
    server = root / "server.fossil"
    run(["fossil", "init", str(server)], cwd=root)

    co = {}
    for machine in ("other", "local"):
        repo = root / f"{machine}.fossil"
        path = root / f"co_{machine}"
        path.mkdir()
        run(["fossil", "clone", str(server), str(repo)], cwd=root)
        run(["fossil", "open", str(repo)], cwd=path)
        co[machine] = path

    co_other, co_local = co["other"], co["local"]

    write_lines(co_other / "shared.txt", BASE_LINES)
    run(["fossil", "add", "."], cwd=co_other)
    run(["fossil", "commit", "-m", "base", "--no-warnings"], cwd=co_other)
    run(["fossil", "pull"], cwd=co_local)
    run(["fossil", "update", "--nosync"], cwd=co_local)
    return co_other, co_local


def main() -> int:
    global _log_handle

    if WORK_ROOT.exists():
        shutil.rmtree(WORK_ROOT)

    with LOG_PATH.open("w", encoding="utf-8") as handle:
        _log_handle = handle
        version = subprocess.run(["fossil", "version"], capture_output=True, text=True)
        log(f"fossil version: {version.stdout.strip()}")

        co_other, co_local = build_topology()

        # Other machine changes line 2 and commits.
        edit_line(co_other / "shared.txt", 2, "INCOMING")
        run(["fossil", "commit", "-m", "change line 2", "--no-warnings"], cwd=co_other)
        run(["fossil", "push"], cwd=co_other)

        # Local machine has an UNCOMMITTED change to line 6, not adjacent,
        # no insertion, no shift.
        before_version = checkout_version(co_local)
        edit_line(co_local / "shared.txt", 6, "LOCAL")

        run(["fossil", "pull"], cwd=co_local)
        tip = tip_version(co_local)

        # --- Q1: does our EXISTING file-overlap check see this file on
        # both sides, independent of whether Fossil itself will conflict? ---
        log("\n--- Q1: file-set overlap (our existing dry-run plausibility check) ---")
        local_changed = run(["fossil", "changes"], cwd=co_local)
        local_files = {l.split()[-1] for l in local_changed.stdout.splitlines() if l.strip()}
        incoming_diff = run(["fossil", "diff", "--brief", "--from", before_version,
                             "--to", tip], cwd=co_local)
        incoming_files = {l.split()[-1].lstrip("+-* ") for l in incoming_diff.stdout.splitlines()
                           if l.strip()}
        overlap = local_files & incoming_files
        log(f"  locally modified: {sorted(local_files)}")
        log(f"  incoming changed: {sorted(incoming_files)}")
        log(f"  overlap (both sides touched): {sorted(overlap)}")

        # --- Q2/Q3: does the real update conflict, and what's the result? ---
        log("\n--- Q2/Q3: real update -- conflict? merged content? ---")
        dry = run(["fossil", "update", "-n", "--nosync", "--verbose"], cwd=co_local,
                  expect_fail=True)
        dry_reports_conflict = "conflict" in (dry.stdout + dry.stderr).lower()
        log(f"  dry run mentions a conflict: {dry_reports_conflict}")

        real = run(["fossil", "update", "--nosync", "--verbose"], cwd=co_local,
                   expect_fail=True)
        real_reports_conflict = "conflict" in (real.stdout + real.stderr).lower()
        run(["fossil", "changes", "--conflict"], cwd=co_local)

        merged_lines = (co_local / "shared.txt").read_text(encoding="utf-8").splitlines()
        markers_present = has_markers(co_local / "shared.txt")
        line2_ok = merged_lines[1] == "line 2 -- INCOMING"
        line6_ok = merged_lines[5] == "line 6 -- LOCAL"

        log(f"  real update mentions a conflict: {real_reports_conflict}")
        log(f"  conflict markers present in file: {markers_present}")
        log(f"  line 2 correctly shows INCOMING: {line2_ok}")
        log(f"  line 6 correctly shows LOCAL:    {line6_ok}")
        log("\n  full merged file:")
        for line in merged_lines:
            log(f"    | {line}")

        result = {
            "file_flagged_by_our_overlap_check": bool(overlap),
            "fossil_dry_run_conflict": dry_reports_conflict,
            "fossil_real_update_conflict": real_reports_conflict,
            "markers_written": markers_present,
            "both_changes_present_correctly": line2_ok and line6_ok,
        }
        log("\n" + "=" * 70)
        log("SUMMARY")
        log("=" * 70)
        log(f"  {result}")

    print(f"Full transcript: {LOG_PATH}")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
