#!/usr/bin/env python3
"""test_fossil_preview_model.py -- checks whether the shadow-checkout
conflict preview described in implementierungs_doku.md 1.15/2.2 can
actually reproduce the conflict it is supposed to predict.

Usage:
    python3 test_fossil_preview_model.py

Runs entirely inside tests/test_data/ against throwaway repositories; no
network access, and neither ~/.claude nor claude-config is touched.

Background: a previous probe (test_fossil_fork_close.py) showed that
`fossil update` does NOT pull in a sibling leaf of a fork -- it only
fast-forwards along the current line of descent. That makes the shape of
the real-world conflict worth pinning down precisely, because the whole
preview design rests on it.

In the real setup, each machine runs update -> add -> commit every few
minutes, so the two machines rarely produce a true two-leaf fork. The
realistic conflict is different: the local check-out carries UNCOMMITTED
edits (Claude Code is writing transcripts continuously) while a check-in
from the other machine arrives. `fossil update` then merges the incoming
check-in into those uncommitted edits, and that merge can conflict.

Three scenarios:
    R1  the real conflict: local uncommitted edit + incoming check-in,
        then `fossil update` in the real check-out. Does it conflict?
    R2  the preview as currently designed: a fresh `fossil open <repo> -k`
        in an empty throwaway directory, then `fossil update`. Does it
        see the conflict from R1?
    R3  a corrected preview: shadow check-out opened at the SAME version
        as the real check-out, the locally modified files copied in, then
        `fossil update`. Does it reproduce R1's conflict?

Transcript: tests/test_data/preview_model_probe.log
"""

import shutil
import subprocess
from pathlib import Path

TEST_DATA = Path(__file__).parent / "test_data"
WORK_ROOT = TEST_DATA / "preview_probe"
LOG_PATH = TEST_DATA / "preview_model_probe.log"

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


def has_markers(path: Path) -> bool:
    return "BEGIN MERGE CONFLICT" in path.read_text(encoding="utf-8", errors="ignore")


def checkout_version(cwd: Path) -> str:
    info = run(["fossil", "info"], cwd=cwd)
    for line in info.stdout.splitlines():
        if line.startswith("checkout:"):
            return line.split()[1]
    raise RuntimeError("no checkout hash")


def build_scenario(name: str) -> tuple[Path, Path, str]:
    """base check-in; other machine commits an edit; this machine has the
    same line edited but NOT committed.

    Returns (repo_file, local_checkout, version_of_local_checkout).
    """
    log("\n" + "=" * 70)
    log(f"BUILDING: {name}")
    log("=" * 70)

    root = WORK_ROOT / name
    root.mkdir(parents=True)
    repo_file = root / "probe.fossil"
    co_other = root / "co_other"
    co_local = root / "co_local"
    co_other.mkdir()
    co_local.mkdir()

    run(["fossil", "init", str(repo_file)], cwd=root)
    run(["fossil", "open", str(repo_file)], cwd=co_other)
    for filename in ("shared.txt", "untouched.txt"):
        write_lines(co_other / filename, BASE_LINES)
    run(["fossil", "add", "."], cwd=co_other)
    run(["fossil", "commit", "-m", "base", "--no-warnings"], cwd=co_other)

    # This machine opens at base and then edits WITHOUT committing.
    run(["fossil", "open", str(repo_file)], cwd=co_local)
    local_version = checkout_version(co_local)
    edit_line3(co_local / "shared.txt", "LOCAL uncommitted")

    # The other machine commits a conflicting change to the same line.
    edit_line3(co_other / "shared.txt", "INCOMING committed")
    write_lines(co_other / "only_incoming.txt", ["file only the other machine has"])
    run(["fossil", "add", "."], cwd=co_other)
    run(["fossil", "commit", "-m", "incoming change", "--no-warnings"], cwd=co_other)

    log(f"\n  => local check-out sits at {local_version} with an uncommitted edit")
    return repo_file, co_local, local_version


def scenario_r1() -> dict:
    log("\n" + "=" * 70)
    log("R1 -- the real conflict: uncommitted local edit + incoming check-in")
    log("=" * 70)
    _, co_local, _ = build_scenario("r1")

    run(["fossil", "update", "--verbose"], cwd=co_local, expect_fail=True)
    run(["fossil", "status"], cwd=co_local)
    run(["fossil", "changes", "--conflict"], cwd=co_local)

    conflicted = has_markers(co_local / "shared.txt")
    log("\n  shared.txt after update:")
    for line in (co_local / "shared.txt").read_text(encoding="utf-8").splitlines():
        log(f"    | {line}")
    log(f"\n  => conflict markers present: {conflicted}")
    return {"name": "R1 real check-out", "conflict": conflicted}


def scenario_r2() -> dict:
    log("\n" + "=" * 70)
    log("R2 -- preview as currently designed (fresh `open -k`, then update)")
    log("=" * 70)
    repo_file, co_local, _ = build_scenario("r2")

    shadow = WORK_ROOT / "r2" / "shadow"
    shadow.mkdir()
    run(["fossil", "open", str(repo_file), "-k"], cwd=shadow)
    log(f"\n  files present in the shadow directory after `open -k`: "
        f"{sorted(p.name for p in shadow.iterdir() if p.name != '.fslckout')}")
    run(["fossil", "update", "--verbose"], cwd=shadow, expect_fail=True)
    run(["fossil", "changes", "--conflict"], cwd=shadow)

    found = [p for p in shadow.rglob("*") if p.is_file() and has_markers(p)]
    log(f"\n  => files with conflict markers in the shadow check-out: {len(found)}")
    log("  (R1 proved the real check-out DOES conflict here, so anything "
        "other than a hit means the preview is blind to it.)")
    return {"name": "R2 preview as designed", "conflict": bool(found)}


def scenario_r3() -> dict:
    log("\n" + "=" * 70)
    log("R3 -- corrected preview (same version + local edits copied in)")
    log("=" * 70)
    repo_file, co_local, local_version = build_scenario("r3")

    shadow = WORK_ROOT / "r3" / "shadow"
    shadow.mkdir()
    # Open the shadow check-out at exactly the version the real check-out
    # sits on, not at the tip.
    run(["fossil", "open", str(repo_file), local_version], cwd=shadow)

    # Carry the uncommitted local edits over, so the shadow starts from
    # the same state the real check-out is in.
    changes = run(["fossil", "changes"], cwd=co_local)
    for line in changes.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            rel = parts[-1]
            source = co_local / rel
            if source.is_file():
                target = shadow / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                log(f"  copied local modification into shadow: {rel}")

    run(["fossil", "update", "--verbose"], cwd=shadow, expect_fail=True)
    run(["fossil", "changes", "--conflict"], cwd=shadow)

    found = [p for p in shadow.rglob("*") if p.is_file() and has_markers(p)]
    log(f"\n  => files with conflict markers in the shadow check-out: "
        f"{[p.name for p in found]}")
    if found:
        log("\n  shadow shared.txt after update:")
        for line in (shadow / "shared.txt").read_text(encoding="utf-8").splitlines():
            log(f"    | {line}")
    log("\n  real check-out must still be untouched -- verifying:")
    real_untouched = not has_markers(co_local / "shared.txt")
    log(f"  => real check-out free of markers: {real_untouched}")
    return {
        "name": "R3 corrected preview",
        "conflict": bool(found),
        "real_untouched": real_untouched,
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

        results = [scenario_r1(), scenario_r2(), scenario_r3()]

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
