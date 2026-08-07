#!/usr/bin/env python3
"""test_fossil_fork_close.py -- non-interactive probe of how Fossil closes
(or fails to close) a fork, comparing the two candidate mechanisms from
implementierungs_doku.md chapter 1.15.

Usage:
    python3 test_fossil_fork_close.py

Everything happens inside tests/test_data/ against throwaway repositories
created from scratch; neither ~/.claude nor the real claude-config
repository is touched, and no network access is involved.

Each scenario gets its OWN repository, because a commit made by one
scenario would otherwise change the starting state of the next one.

Scenario layout (identical starting point for all three):
    base check-in  ->  shared.txt, keep_local.txt, untouched.txt
    check-in VA    ->  edits line 3 of shared.txt and keep_local.txt,
                       adds only_incoming.txt          ("the other machine")
    check-in VB    ->  edits the same two lines differently, forced with
                       --allow-fork                    ("this machine")
    => two open leaves on trunk == a fork, both editing the same lines

Scenarios:
    A  file-restricted update: `fossil update VA <files without
       keep_local.txt>`, resolve, commit. Does the fork close?
    B  full update, resolve every conflict in the check-out (incoming for
       one file, local content restored for the other), commit. Does the
       fork close?
    C  full update, then commit straight away WITHOUT resolving, to see
       whether Fossil 2.23 really refuses a check-in containing conflict
       markers (open question in doku chapter 1.3).

A full transcript of every command and its output is written to
tests/test_data/fork_close_probe.log; the summary is printed to stdout.
"""

import shutil
import subprocess
import sys
from pathlib import Path

TEST_DATA = Path(__file__).parent / "test_data"
WORK_ROOT = TEST_DATA / "fork_probe"
LOG_PATH = TEST_DATA / "fork_close_probe.log"

BASE_LINES = ["line 1", "line 2", "line 3 -- BASE", "line 4", "line 5"]

_log_handle = None


def log(text: str) -> None:
    _log_handle.write(text + "\n")
    _log_handle.flush()


def run(args: list[str], cwd: Path, expect_fail: bool = False) -> subprocess.CompletedProcess:
    """Run a command, log it verbatim together with its full output."""
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


def current_checkout_hash(cwd: Path) -> str:
    info = run(["fossil", "info"], cwd=cwd)
    for line in info.stdout.splitlines():
        if line.startswith("checkout:"):
            return line.split()[1]
    raise RuntimeError("could not determine checkout hash")


def open_leaves(cwd: Path) -> list[str]:
    """Return the open leaves of the repository as raw text lines."""
    result = run(["fossil", "leaves"], cwd=cwd)
    return [line for line in result.stdout.splitlines() if line.strip()]


def build_forked_repo(name: str) -> tuple[Path, Path, str]:
    """Create a fresh repo containing a genuine two-leaf fork.

    Returns (repo_file, local_checkout, incoming_version_hash), where
    local_checkout sits on the 'this machine' leaf VB.
    """
    log("\n" + "=" * 70)
    log(f"BUILDING FORKED REPOSITORY: {name}")
    log("=" * 70)

    root = WORK_ROOT / name
    root.mkdir(parents=True)
    repo_file = root / "probe.fossil"
    co_incoming = root / "co_incoming"
    co_local = root / "co_local"
    co_incoming.mkdir()
    co_local.mkdir()

    run(["fossil", "init", str(repo_file)], cwd=root)

    # --- base check-in, made from the "incoming" check-out ---------------
    run(["fossil", "open", str(repo_file)], cwd=co_incoming)
    for filename in ("shared.txt", "keep_local.txt", "untouched.txt"):
        write_lines(co_incoming / filename, BASE_LINES)
    run(["fossil", "add", "."], cwd=co_incoming)
    run(["fossil", "commit", "-m", "base", "--no-warnings"], cwd=co_incoming)

    # --- second check-out, still sitting on the base version -------------
    run(["fossil", "open", str(repo_file)], cwd=co_local)

    # --- VA: the other machine's commit ----------------------------------
    edit_line3(co_incoming / "shared.txt", "INCOMING")
    edit_line3(co_incoming / "keep_local.txt", "INCOMING")
    write_lines(co_incoming / "only_incoming.txt", ["a file only the other machine has"])
    run(["fossil", "add", "."], cwd=co_incoming)
    run(["fossil", "commit", "-m", "incoming change", "--no-warnings"], cwd=co_incoming)
    incoming_hash = current_checkout_hash(co_incoming)
    log(f"\n  => incoming version VA = {incoming_hash}")

    # --- VB: this machine's commit, deliberately forking -----------------
    edit_line3(co_local / "shared.txt", "LOCAL")
    edit_line3(co_local / "keep_local.txt", "LOCAL")
    log("\n  -- first WITHOUT --allow-fork, to record how Fossil reacts --")
    run(["fossil", "commit", "-m", "local change", "--no-warnings"],
        cwd=co_local, expect_fail=True)
    log("\n  -- now WITH --allow-fork, to construct the fork on purpose --")
    run(["fossil", "commit", "-m", "local change", "--no-warnings", "--allow-fork"],
        cwd=co_local)

    leaves = open_leaves(co_local)
    log(f"\n  => open leaves after building the fork: {len(leaves)}")
    return repo_file, co_local, incoming_hash


def report_fork_state(cwd: Path, label: str) -> int:
    log(f"\n--- fork state {label} ---")
    leaves = open_leaves(cwd)
    run(["fossil", "leaves", "-m"], cwd=cwd)
    run(["fossil", "timeline", "-n", "6"], cwd=cwd)
    log(f"  => {len(leaves)} open leaf/leaves")
    return len(leaves)


def resolve_take_incoming(path: Path) -> None:
    """Keep the incoming side of every conflict block in the file."""
    out, mode = [], "normal"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("<<<<<<<"):
            mode = "ours"
        elif line.startswith("======="):
            mode = "theirs"
        elif line.startswith(">>>>>>>"):
            mode = "normal"
        elif mode in ("normal", "theirs"):
            out.append(line)
    write_lines(path, out)


def scenario_a() -> dict:
    """File-restricted update, excluding the 'keep local' file."""
    log("\n" + "=" * 70)
    log("SCENARIO A -- file-restricted update (candidate A in doku 1.15)")
    log("=" * 70)
    _, co, incoming_hash = build_forked_repo("scenario_a")

    run(["fossil", "update", incoming_hash, "shared.txt", "untouched.txt",
         "only_incoming.txt", "--verbose"], cwd=co, expect_fail=True)
    run(["fossil", "status"], cwd=co)
    run(["fossil", "changes", "--conflict"], cwd=co)

    log("\n  keep_local.txt content after the restricted update:")
    for line in (co / "keep_local.txt").read_text(encoding="utf-8").splitlines():
        log(f"    | {line}")

    resolve_take_incoming(co / "shared.txt")
    commit = run(["fossil", "commit", "-m", "resolved via restricted update",
                  "--no-warnings"], cwd=co, expect_fail=True)

    leaves = report_fork_state(co, "after scenario A")
    return {
        "name": "A (file-restricted update)",
        "commit_rc": commit.returncode,
        "leaves": leaves,
    }


def scenario_b() -> dict:
    """Full update, resolve everything in the check-out, then commit."""
    log("\n" + "=" * 70)
    log("SCENARIO B -- full update + resolve + commit (candidate B in doku 1.15)")
    log("=" * 70)
    _, co, _ = build_forked_repo("scenario_b")

    local_keep = (co / "keep_local.txt").read_text(encoding="utf-8")

    run(["fossil", "update", "--verbose"], cwd=co, expect_fail=True)
    run(["fossil", "status"], cwd=co)
    run(["fossil", "changes", "--conflict"], cwd=co)

    # shared.txt -> take what comes in; keep_local.txt -> keep local content.
    resolve_take_incoming(co / "shared.txt")
    (co / "keep_local.txt").write_text(local_keep, encoding="utf-8")

    run(["fossil", "changes", "--conflict"], cwd=co)
    commit = run(["fossil", "commit", "-m", "resolved in worksite",
                  "--no-warnings"], cwd=co, expect_fail=True)

    log("\n  keep_local.txt content after resolution:")
    for line in (co / "keep_local.txt").read_text(encoding="utf-8").splitlines():
        log(f"    | {line}")

    leaves = report_fork_state(co, "after scenario B")
    return {
        "name": "B (full update, resolve, commit)",
        "commit_rc": commit.returncode,
        "leaves": leaves,
    }


def scenario_c() -> dict:
    """Commit with unresolved conflict markers still in place."""
    log("\n" + "=" * 70)
    log("SCENARIO C -- commit WITHOUT resolving (doku 1.3 open question)")
    log("=" * 70)
    _, co, _ = build_forked_repo("scenario_c")

    run(["fossil", "update", "--verbose"], cwd=co, expect_fail=True)
    commit = run(["fossil", "commit", "-m", "deliberately unresolved",
                  "--no-warnings"], cwd=co, expect_fail=True)

    refused = commit.returncode != 0
    log(f"\n  => Fossil {'REFUSED' if refused else 'ACCEPTED'} the check-in "
        "containing conflict markers.")
    return {
        "name": "C (commit with unresolved markers)",
        "commit_rc": commit.returncode,
        "refused": refused,
    }


def main() -> int:
    global _log_handle

    if WORK_ROOT.exists():
        shutil.rmtree(WORK_ROOT)
    WORK_ROOT.mkdir(parents=True)

    with LOG_PATH.open("w", encoding="utf-8") as handle:
        _log_handle = handle
        version = subprocess.run(["fossil", "version"], capture_output=True, text=True)
        log(f"fossil version: {version.stdout.strip()}")

        results = [scenario_a(), scenario_b(), scenario_c()]

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
