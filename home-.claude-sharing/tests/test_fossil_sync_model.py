#!/usr/bin/env python3
"""test_fossil_sync_model.py -- validates the plain "one strand, stay in
step with the remote" sync model against real Fossil behaviour.

Usage:
    python3 test_fossil_sync_model.py

Runs entirely inside tests/test_data/ against throwaway repositories. No
network is used: the "server" is a local .fossil file that both machines
clone from over a filesystem path, which gives the same three-repository
topology as the real setup (server + one clone per machine, each clone
with its own check-out).

The model under test, stated in Git terms:
    fetch  -> are we behind? -> pull
           -> are we ahead?  -> commit (Fossil auto-syncs the push)
Repeat every few minutes on both machines.

Fossil equivalents:
    `fossil pull`   == git fetch  (writes only into the local repository
                                   file, never into the check-out)
    `fossil update` == git merge  (moves the check-out, and merges any
                                   uncommitted local edits while doing so)

Questions this probe answers:
    Q1  Does `fossil pull` really leave the check-out untouched?
    Q2  How can "am I behind?" be answered locally, after the pull?
    Q3  Does `fossil update -n` (dry run) predict merge conflicts WITHOUT
        writing conflict markers to disk? If it does, no shadow check-out
        is needed to detect them at all.
    Q4  If the locally modified files and the remotely changed files are
        disjoint sets, is the update guaranteed to be conflict-free?
    Q5  If they overlap, does the conflict actually materialise?

Transcript: tests/test_data/sync_model_probe.log
"""

import shutil
import subprocess
from pathlib import Path

TEST_DATA = Path(__file__).parent / "test_data"
WORK_ROOT = TEST_DATA / "sync_model"
LOG_PATH = TEST_DATA / "sync_model_probe.log"

BASE_LINES = ["line 1", "line 2", "line 3 -- BASE", "line 4", "line 5"]

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


def info_field(cwd: Path, field: str, args: list[str] | None = None) -> str:
    result = run(["fossil", "info", *(args or [])], cwd=cwd)
    for line in result.stdout.splitlines():
        if line.startswith(f"{field}:"):
            return line.split()[1]
    return ""


def checkout_version(cwd: Path) -> str:
    return info_field(cwd, "checkout")


def tip_version(cwd: Path) -> str:
    """The newest check-in known to the LOCAL repository (post-pull)."""
    result = run(["fossil", "timeline", "-n", "1", "-t", "ci", "-W", "0"], cwd=cwd)
    for line in result.stdout.splitlines():
        if "[" in line and "]" in line:
            return line.split("[", 1)[1].split("]", 1)[0]
    return ""


def changed_files(cwd: Path) -> set[str]:
    """Locally modified files (uncommitted)."""
    result = run(["fossil", "changes"], cwd=cwd)
    return {line.split()[-1] for line in result.stdout.splitlines() if line.strip()}


def incoming_files(cwd: Path, frm: str, to: str) -> set[str]:
    """Files that changed in the repository between two versions."""
    result = run(["fossil", "diff", "--brief", "--from", frm, "--to", to], cwd=cwd)
    names = set()
    for line in result.stdout.splitlines():
        if line.strip():
            names.add(line.split()[-1].lstrip("+-* "))
    return names


def has_markers(path: Path) -> bool:
    if not path.is_file():
        return False
    return "BEGIN MERGE CONFLICT" in path.read_text(encoding="utf-8", errors="ignore")


def build_topology(name: str) -> tuple[Path, Path]:
    """server.fossil + two clones, each with its own check-out.

    Returns (checkout_a, checkout_b), both holding the same base check-in.
    """
    log("\n" + "=" * 70)
    log(f"BUILDING TOPOLOGY: {name}  (server + 2 machine clones)")
    log("=" * 70)

    root = WORK_ROOT / name
    root.mkdir(parents=True)
    server = root / "server.fossil"
    run(["fossil", "init", str(server)], cwd=root)

    checkouts = {}
    for machine in ("a", "b"):
        repo = root / f"{machine}.fossil"
        co = root / f"co_{machine}"
        co.mkdir()
        run(["fossil", "clone", str(server), str(repo)], cwd=root)
        run(["fossil", "open", str(repo)], cwd=co)
        checkouts[machine] = co

    co_a, co_b = checkouts["a"], checkouts["b"]

    # Machine A creates the initial content and pushes it.
    for filename in ("shared.txt", "other.txt", "untouched.txt"):
        write_lines(co_a / filename, BASE_LINES)
    run(["fossil", "add", "."], cwd=co_a)
    run(["fossil", "commit", "-m", "base", "--no-warnings"], cwd=co_a)
    run(["fossil", "push"], cwd=co_a)

    # Machine B fetches and moves onto it.
    run(["fossil", "pull"], cwd=co_b)
    run(["fossil", "update", "--nosync"], cwd=co_b)

    return co_a, co_b


def probe(name: str, local_file: str, remote_file: str) -> dict:
    """Machine A commits a change to remote_file; machine B has an
    uncommitted change to local_file. Then B runs the sync decision."""
    log("\n" + "=" * 70)
    log(f"PROBE {name}: A changes {remote_file}, B has uncommitted {local_file}")
    log("=" * 70)
    co_a, co_b = build_topology(name)

    # --- machine A advances the strand --------------------------------
    edit_line3(co_a / remote_file, "INCOMING")
    run(["fossil", "commit", "-m", f"change {remote_file}", "--no-warnings"], cwd=co_a)
    run(["fossil", "push"], cwd=co_a)

    # --- machine B has an uncommitted local edit ----------------------
    edit_line3(co_b / local_file, "LOCAL uncommitted")

    before_version = checkout_version(co_b)
    before_content = (co_b / remote_file).read_text(encoding="utf-8")

    # --- Q1: fetch only ------------------------------------------------
    log("\n--- Q1: does `fossil pull` touch the check-out? ---")
    run(["fossil", "pull"], cwd=co_b)
    after_version = checkout_version(co_b)
    after_content = (co_b / remote_file).read_text(encoding="utf-8")
    pull_is_safe = (before_version == after_version) and (before_content == after_content)
    log(f"  check-out version unchanged: {before_version == after_version}")
    log(f"  file content on disk unchanged: {before_content == after_content}")
    log(f"  => pull left the check-out alone: {pull_is_safe}")

    # --- Q2: are we behind? --------------------------------------------
    log("\n--- Q2: are we behind, judged locally after the pull? ---")
    tip = tip_version(co_b)
    behind = tip[:10] != after_version[:10]
    log(f"  check-out = {after_version[:10]}, local tip = {tip[:10]}")
    log(f"  => behind: {behind}")

    # --- Q4: overlap of local and incoming file sets --------------------
    log("\n--- Q4: do the local and incoming change sets overlap? ---")
    local_set = changed_files(co_b)
    incoming_set = incoming_files(co_b, after_version, tip)
    overlap = local_set & incoming_set
    log(f"  locally modified : {sorted(local_set)}")
    log(f"  incoming changes : {sorted(incoming_set)}")
    log(f"  overlap          : {sorted(overlap)}")

    # --- Q3: does the dry run predict the conflict without writing? -----
    log("\n--- Q3: `fossil update -n` (dry run) ---")
    dry = run(["fossil", "update", "-n", "--nosync", "--verbose"], cwd=co_b, expect_fail=True)
    dry_text = dry.stdout + dry.stderr
    dry_predicts_conflict = "conflict" in dry_text.lower()
    markers_after_dry = [
        p.name for p in co_b.rglob("*") if p.is_file() and has_markers(p)
    ]
    log(f"  dry run mentions a conflict : {dry_predicts_conflict}")
    log(f"  files with markers on disk  : {markers_after_dry}")
    dry_is_clean = not markers_after_dry

    # --- Q5: what really happens -----------------------------------------
    log("\n--- Q5: the real update ---")
    real = run(["fossil", "update", "--nosync", "--verbose"], cwd=co_b, expect_fail=True)
    real_text = real.stdout + real.stderr
    real_conflict = "conflict" in real_text.lower()
    markers_after_real = [
        p.name for p in co_b.rglob("*") if p.is_file() and has_markers(p)
    ]
    run(["fossil", "changes", "--conflict"], cwd=co_b)
    log(f"  real update reports conflict : {real_conflict}")
    log(f"  files with markers on disk   : {markers_after_real}")

    return {
        "probe": name,
        "pull_safe": pull_is_safe,
        "behind_detected": behind,
        "overlap": sorted(overlap),
        "dryrun_predicts": dry_predicts_conflict,
        "dryrun_left_disk_clean": dry_is_clean,
        "real_conflict": bool(markers_after_real),
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

        results = [
            # same file touched on both sides -> conflict expected
            probe("overlapping", local_file="shared.txt", remote_file="shared.txt"),
            # different files touched -> no conflict expected
            probe("disjoint", local_file="other.txt", remote_file="shared.txt"),
        ]

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
