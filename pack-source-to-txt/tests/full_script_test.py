#!/usr/bin/env python3
"""
full_script_test.py
====================

Acceptance / regression test for packsrc.sh.

This script never modifies the real packsrc.sh. Instead it:

  1. Builds a small fixture file/directory tree under ./test_project/,
     which plays the role of a simulated project root.
  2. For each entry in SCENARIOS, writes a scenario-specific COPY of
     packsrc.sh into test_project/ with the
     CONFIGURATION block (SOURCE_DIRS, BASE_EXTENSIONS, EXCLUDE_DIRS,
     EXPLICIT_FILES) replaced by the scenario's values, then runs that copy
     with cwd=test_project/.
  3. Copies the resulting project_source.txt into ./test_results/ under a
     scenario-specific name.
  4. Parses the "#!PKSRC:FILE:BEGIN" lines of that output and compares the
     resulting file set against the expected set derived from FIXTURES.
  5. Prints a PASS/FAIL report per scenario plus an overall summary.

Cleanup behaviour:
  - At the START of every run, ./test_project/ and ./test_results/ are
    removed (if present) and rebuilt from scratch, so a previous failed run
    can never corrupt the next one.
  - At the END of a run: if ALL scenarios passed, both directories are
    removed again (only the console PASS/FAIL report remains). If ANY
    scenario failed, or an unexpected error occurred, BOTH directories are
    left in place so you can inspect test_project/ (the simulated project
    with the scenario script copies) and test_results/ (the raw
    project_source.txt outputs) by hand.

Requirements: Python 3.10+ (standard library only, no third-party
packages). Tested against the system Python 3.12 on Ubuntu 24.04 — no
virtual environment is required to run this script.

Command line options:
    -h, --help         Show usage help and exit.
    -c, --no-clean-up  Keep test_project/ and test_results/ after the run,
                        even if all scenarios passed (normally both are only
                        kept on failure). They are still wiped and rebuilt at
                        the start of every run regardless of this flag.
    -C, --clean-up     Only remove test_project/ and test_results/ if they
                        are still present from a previous run, then exit
                        immediately without running any scenarios. Mutually
                        exclusive with -c/--no-cleanup.

--------------------------------------------------------------------------
HOW TO ADD A NEW TEST CASE
--------------------------------------------------------------------------

To add a new FIXTURE FILE:
    Append a FixtureFile(...) entry to the FIXTURES list below.
      - path:      the file's path relative to test_project/ (i.e.
                    relative to the simulated project root). No leading
                    "./".
      - content:   the file's text content.
      - scenarios: a frozenset of scenario names (see SCENARIOS below) in
                    which this file is expected to appear in the generated
                    project_source.txt. Use an empty frozenset() for files
                    that must NEVER appear in any scenario's output (e.g.
                    files inside an excluded directory, or hidden files).

To add a new TEST SCENARIO:
    Add a new entry to the SCENARIOS dict below, with the same keys as the
    existing entries (SOURCE_DIRS, BASE_EXTENSIONS, EXCLUDE_DIRS,
    EXPLICIT_FILES, cli_args). Then go through FIXTURES and add the new
    scenario's name to the `scenarios` frozenset of every fixture that is
    expected to appear under that new scenario's configuration.
--------------------------------------------------------------------------
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ==============================================================================
# PATHS
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_SCRIPT = PROJECT_ROOT.parent / "packsrc.sh"
TEST_DIR = PROJECT_ROOT / "test_project"
RESULT_DIR = PROJECT_ROOT / "test_results"


# ==============================================================================
# FIXTURES — the simulated project tree
# ==============================================================================

@dataclass(frozen=True)
class FixtureFile:
    path: str                  # relative to test_project/ (simulated project root)
    content: str
    scenarios: frozenset[str]  # scenario names expecting this file in the output


FIXTURES: list[FixtureFile] = [
    # --- normal extension match, inside a SOURCE_DIRS entry ---
    FixtureFile(
        "services/aufsicht-links/watchdog.py",
        "print('watchdog')\n",
        frozenset({"named", "recursive", "md_flag"}),
    ),
    # --- EXPLICIT_FILES bare-name lookup (found by exact name, not extension) ---
    FixtureFile(
        "services/aufsicht-links/Dockerfile.watchdog",
        "FROM python:3.12-slim\n",
        frozenset({"named", "recursive", "md_flag"}),
    ),
    # --- EXCLUDE_DIRS pruning ---
    FixtureFile(
        "services/aufsicht-links/backup/old_watchdog.py",
        "print('old watchdog, must be excluded via EXCLUDE_DIRS')\n",
        frozenset(),
    ),
    FixtureFile(
        "services/aufsicht-links/__pycache__/watchdog.cpython-312.pyc",
        "placeholder bytecode, must be excluded via EXCLUDE_DIRS\n",
        frozenset(),
    ),
    # --- BASE_EXTENSIONS="" special case: files with no dot in their name ---
    FixtureFile(
        "services/containment-overview/Dockerfile",
        "FROM python:3.12-slim\n",
        frozenset({"named", "recursive", "md_flag"}),
    ),
    # --- -md CLI flag ---
    FixtureFile(
        "services/containment-overview/notes.md",
        "# Notes\nShould only appear when the script is run with -md.\n",
        frozenset({"md_flag"}),
    ),
    # --- default dot-exclusion: hidden directory ---
    FixtureFile(
        "services/.hidden_subdir/leftover.py",
        "print('must be excluded, lives in a hidden directory')\n",
        frozenset(),
    ),
    # --- default dot-exclusion: hidden file itself ---
    FixtureFile(
        "services/.hidden.py",
        "print('must be excluded, hidden file name')\n",
        frozenset(),
    ),
    # --- second SOURCE_DIRS entry ---
    FixtureFile(
        "watchdog-module/containerwatchdog/main.py",
        "print('containerwatchdog main')\n",
        frozenset({"named", "recursive", "md_flag"}),
    ),
    # --- directory NOT listed in SOURCE_DIRS for 'named'/'md_flag' ---
    FixtureFile(
        "not_included_dir/module.py",
        "print('only found when SOURCE_DIRS scans the whole project root')\n",
        frozenset({"recursive"}),
    ),
    # --- default dot-exclusion at project-root level (regression test for the
    #     -mindepth 1 fix: without it, a SOURCE_DIRS entry of './' would have
    #     its own start path pruned away by the ".*" dot pattern) ---
    FixtureFile(
        ".git/config",
        "[core]\n\trepositoryformatversion = 0\n",
        frozenset(),
    ),
    FixtureFile(
        ".hidden_root.py",
        "print('must be excluded even though .py matches BASE_EXTENSIONS')\n",
        frozenset(),
    ),
    # --- EXPLICIT_FILES with './' prefix: single file at project-root level ---
    FixtureFile(
        "docker-compose.yml",
        "version: '3'\nservices: {}\n",
        frozenset({"named", "recursive", "md_flag"}),
    ),
    # --- EXPLICIT_FILES './' bypasses the default dot-exclusion ---
    FixtureFile(
        ".hidden_root_config",
        "explicit_bypass=true\n",
        frozenset({"named", "recursive", "md_flag"}),
    ),
]


# ==============================================================================
# SCENARIOS — scenario name -> CONFIGURATION values for the scenario script copy
# ==============================================================================

_COMMON_EXCLUDE_DIRS = ["backup", "__pycache__"]
_COMMON_EXPLICIT_FILES = [
    "Dockerfile.watchdog",
    "./docker-compose.yml",
    "./.hidden_root_config",
]
_COMMON_BASE_EXTENSIONS = ["py", ""]

SCENARIOS: dict[str, dict] = {
    "named": {
        "SOURCE_DIRS": ["services", "watchdog-module"],
        "BASE_EXTENSIONS": _COMMON_BASE_EXTENSIONS,
        "EXCLUDE_DIRS": _COMMON_EXCLUDE_DIRS,
        "EXPLICIT_FILES": _COMMON_EXPLICIT_FILES,
        "cli_args": [],
    },
    "recursive": {
        "SOURCE_DIRS": ["./"],
        "BASE_EXTENSIONS": _COMMON_BASE_EXTENSIONS,
        "EXCLUDE_DIRS": _COMMON_EXCLUDE_DIRS,
        "EXPLICIT_FILES": _COMMON_EXPLICIT_FILES,
        "cli_args": [],
    },
    "md_flag": {
        "SOURCE_DIRS": ["services", "watchdog-module"],
        "BASE_EXTENSIONS": _COMMON_BASE_EXTENSIONS,
        "EXCLUDE_DIRS": _COMMON_EXCLUDE_DIRS,
        "EXPLICIT_FILES": _COMMON_EXPLICIT_FILES,
        "cli_args": ["-md"],
    },
}


# ==============================================================================
# RESULT TYPE
# ==============================================================================

@dataclass
class ScenarioResult:
    name: str
    passed: bool
    missing: set[str] = field(default_factory=set)
    unexpected: set[str] = field(default_factory=set)
    error: str | None = None


# ==============================================================================
# HELPERS
# ==============================================================================

def clean_test_dirs() -> None:
    """Remove test_project/ and test_results/ if present."""
    for d in (TEST_DIR, RESULT_DIR):
        if d.exists():
            shutil.rmtree(d)


def build_fixtures() -> None:
    """Create test_project/ and populate it with all FIXTURES."""
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    for fixture in FIXTURES:
        target = TEST_DIR / fixture.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(fixture.content)


def format_bash_array(name: str, values: list[str]) -> str:
    """Render e.g. SOURCE_DIRS=("services" "watchdog-module")."""
    quoted = " ".join(f'"{v}"' for v in values)
    return f"{name}=({quoted})"


def substitute_config(script_text: str, cfg: dict) -> str:
    """
    Replace the four top-level CONFIGURATION assignment lines
    (SOURCE_DIRS=..., BASE_EXTENSIONS=..., EXCLUDE_DIRS=..., EXPLICIT_FILES=...)
    in script_text with the scenario's values. The regex is anchored at the
    start of the line (no leading '#'), so commented-out example lines in
    the CONFIGURATION section's documentation are never touched.
    """
    result = script_text
    for var in ("SOURCE_DIRS", "BASE_EXTENSIONS", "EXCLUDE_DIRS", "EXPLICIT_FILES"):
        new_line = format_bash_array(var, cfg[var])
        pattern = re.compile(rf"^{var}=\([^\n]*\)", re.MULTILINE)
        result, count = pattern.subn(new_line, result, count=1)
        if count != 1:
            raise RuntimeError(
                f"Expected exactly one top-level assignment line for '{var}' "
                f"in {SOURCE_SCRIPT.name}, found {count}. The script's "
                f"CONFIGURATION section format may have changed."
            )
    return result


_FILE_BEGIN_RE = re.compile(r"^#!PKSRC:FILE:BEGIN \| (.+?) \| pksrc_ts:", re.MULTILINE)


def normalize_path(p: str) -> str:
    p = p.strip()
    if p.startswith("./"):
        p = p[2:]
    return p


def parse_output_paths(output_file: Path) -> set[str]:
    text = output_file.read_text()
    return {normalize_path(p) for p in _FILE_BEGIN_RE.findall(text)}


def expected_paths_for(scenario_name: str) -> set[str]:
    return {f.path for f in FIXTURES if scenario_name in f.scenarios}


# ==============================================================================
# SCENARIO EXECUTION
# ==============================================================================

def run_scenario(name: str, cfg: dict, original_script_text: str) -> ScenarioResult:
    print(f"\n--- Running scenario '{name}' ---")

    try:
        scenario_script_text = substitute_config(original_script_text, cfg)
    except RuntimeError as exc:
        return ScenarioResult(name, passed=False, error=str(exc))

    scenario_script_path = TEST_DIR / f"packsrc__{name}.sh"
    scenario_script_path.write_text(scenario_script_text)

    cli_args = cfg.get("cli_args", [])
    try:
        proc = subprocess.run(
            ["bash", scenario_script_path.name, *cli_args],
            cwd=TEST_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return ScenarioResult(name, passed=False, error=f"Failed to run scenario script: {exc}")

    if proc.returncode != 0:
        return ScenarioResult(
            name,
            passed=False,
            error=(
                f"Script exited with code {proc.returncode}.\n"
                f"--- stdout ---\n{proc.stdout}\n"
                f"--- stderr ---\n{proc.stderr}"
            ),
        )

    produced = TEST_DIR / "project_source.txt"
    if not produced.is_file():
        return ScenarioResult(name, passed=False, error="project_source.txt was not created.")

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    result_copy = RESULT_DIR / f"{name}_project_source.txt"
    shutil.copyfile(produced, result_copy)

    actual = parse_output_paths(result_copy)
    expected = expected_paths_for(name)
    missing = expected - actual
    unexpected = actual - expected
    passed = not missing and not unexpected

    return ScenarioResult(name, passed=passed, missing=missing, unexpected=unexpected)


def print_scenario_report(r: ScenarioResult) -> None:
    if r.error:
        print(f"  ERROR: {r.error}")
        return
    if r.passed:
        print("  PASS")
        return
    print("  FAIL")
    if r.missing:
        print("  Missing (expected but not found in output):")
        for p in sorted(r.missing):
            print(f"    - {p}")
    if r.unexpected:
        print("  Unexpected (found in output but not expected):")
        for p in sorted(r.unexpected):
            print(f"    - {p}")


# ==============================================================================
# MAIN
# ==============================================================================

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Acceptance/regression test for packsrc.sh. "
                     "Requirements: Python 3.10+ (standard library only, no third-"
                     "party packages)."
                     ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-c",
        "--no-clean-up",
        action="store_true",
        help=(
            "Keep test_project/ and test_results/ after the run, even if "
            "all scenarios passed. They are still wiped and rebuilt at the "
            "start of the next run regardless of this flag."
        ),
    )
    group.add_argument(
        "-C",
        "--clean-up",
        action="store_true",
        help=(
            "Only remove test_project/ and test_results/ if they are "
            "still present from a previous run, then exit immediately. "
            "No scenarios are executed."
        ),
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()

    print(f"=== full_script_test.py — testing {SOURCE_SCRIPT.name} ===")

    if args.clean_up:
        print("\n--clean-up: removing test_project/ and test_results/ if present, then exiting.")
        clean_test_dirs()
        return 0

    if shutil.which("bash") is None:
        print("FATAL: 'bash' was not found on PATH.", file=sys.stderr)
        return 1

    if not SOURCE_SCRIPT.is_file():
        print(f"FATAL: {SOURCE_SCRIPT} not found.", file=sys.stderr)
        return 1

    # Always start from a clean slate, in case a previous run failed and
    # left directories behind.
    clean_test_dirs()

    results: list[ScenarioResult] = []
    try:
        build_fixtures()
        original_script_text = SOURCE_SCRIPT.read_text()

        for name, cfg in SCENARIOS.items():
            result = run_scenario(name, cfg, original_script_text)
            results.append(result)
            print_scenario_report(result)

    except Exception as exc:  # noqa: BLE001 - top-level safety net, see docstring
        print("\nFATAL ERROR during test setup/execution:", file=sys.stderr)
        print(f"  {type(exc).__name__}: {exc}", file=sys.stderr)
        print("\ntest_project/ and test_results/ were left in place for inspection at:")
        print(f"  {TEST_DIR}")
        print(f"  {RESULT_DIR}")
        return 1

    all_passed = bool(results) and all(r.passed and r.error is None for r in results)

    print("\n=== SUMMARY ===")
    for r in results:
        status = "PASS" if (r.passed and r.error is None) else "FAIL"
        print(f"  [{status}] {r.name}")

    if all_passed:
        if args.no_clean_up:
            print("\nAll scenarios passed — leaving test_project/ and test_results/ in place (--no-cleanup).")
            print(f"  {TEST_DIR}")
            print(f"  {RESULT_DIR}")
        else:
            print("\nAll scenarios passed — cleaning up test_project/ and test_results/.")
            clean_test_dirs()
        return 0

    print("\nAt least one scenario FAILED.")
    print("test_project/ and test_results/ were left in place for inspection at:")
    print(f"  {TEST_DIR}")
    print(f"  {RESULT_DIR}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
