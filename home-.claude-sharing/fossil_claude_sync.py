#!/usr/bin/env python3
"""fossil_claude_sync.py -- periodic Fossil-based sync for ~/.claude.

Usage:
    fossil_claude_sync.py                  Run one sync cycle (default action).
    fossil_claude_sync.py --silent         Same, but suppress line-by-line
                                            progress output (for systemd).
    fossil_claude_sync.py --set-interval N Rewrite the background schedule to
                                            run every N minutes and reload it.

What one sync cycle does:
    1. Acquire a lock so overlapping runs (e.g. a slow previous run plus a
       freshly triggered one) never touch the checkout at the same time.
    2. Preview the merge in a disposable shadow checkout of the same Fossil
       repository file, WITHOUT touching the real ~/.claude checkout.
    3. If the preview is clean: perform the real `fossil update`, `add`,
       and (if there is anything to commit) `commit` in ~/.claude, then show
       a short, self-dismissing success notice.
    4. If the preview shows a merge conflict: leave the real checkout
       untouched, and escalate to the user via a dialog that offers to open
       a Claude Code session pointed at the conflict. The dialog re-appears
       at most every 30 minutes while the conflict remains unresolved, and
       stays silent again once a later cycle comes back clean.

Platform notes:
    Designed to run on Linux and Windows. The state handling, locking, and
    Fossil calls are platform-independent (pathlib / subprocess). The
    interactive pieces (dialogs, terminal launch, background scheduling)
    are isolated behind small platform-dispatch functions; only the Linux
    side is implemented for now (Zenity, xdg-terminal-exec/well-known
    terminal emulators, systemd --user). The Windows side is a planned
    follow-up (see implementierungs_doku.md, chapter 2.7) and currently
    raises NotImplementedError with a pointer to that chapter.

Configuration constants below (paths, cooldowns) are the ones agreed in
implementierungs_doku.md and are intentionally not exposed as CLI flags
beyond --set-interval, to keep the tool small.
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterator, Optional

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

CLAUDE_DIR = Path.home() / ".claude"
REPO_FILE = Path.home() / "fossil-repos" / "claude-config.fossil"
STATE_DIR = Path.home() / ".local" / "state" / "claude-fossil-sync"
STATE_FILE = STATE_DIR / "state.json"

# This single file serves two purposes at once: while a cycle is running,
# every line Fossil produces is appended to it (that's the "liveness" log);
# its mtime is therefore always fresh as long as something is actually
# happening. It is deleted again in a `finally` block once the cycle ends,
# whatever the outcome. See implementierungs_doku.md, 1.12/1.13.
LOCK_FILE = STATE_DIR / "sync.lock"

CONFLICT_MARKER = "BEGIN MERGE CONFLICT"
DIALOG_COOLDOWN = datetime.timedelta(minutes=30)
# How long the lock/log file may go without a new line before a running
# transfer is assumed dead rather than merely slow. Long total runtimes are
# fine as long as new lines keep arriving well within this window.
STALE_LOG_AFTER = datetime.timedelta(minutes=5)

TRANSFER_SUMMARY_RE = re.compile(
    r"finished with (\d+) bytes sent,\s*(\d+) bytes received", re.IGNORECASE
)

SYSTEMD_UNIT_DIR = Path.home() / ".config" / "systemd" / "user"
SYSTEMD_TIMER_NAME = "fossil-claude-sync.timer"

# Fallback terminal candidates, in priority order, with their "run a
# command" argument. xdg-terminal-exec is tried first and does not need an
# entry here; this list only matters if it is not installed.
TERMINAL_CANDIDATES: list[tuple[str, str]] = [
    ("x-terminal-emulator", "-e"),
    ("gnome-terminal", "--"),
    ("konsole", "-e"),
    ("xfce4-terminal", "-e"),
    ("alacritty", "-e"),
    ("kitty", "-e"),
    ("xterm", "-e"),
]

# Set from main() based on --silent. Governs whether run_fossil_streaming()
# echoes lines to stdout as they arrive (manual run) or stays quiet (systemd
# run, where stdout/stderr normally end up in the journal).
SILENT = False


# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------

@dataclasses.dataclass
class SyncState:
    conflict_active: bool = False
    dialog_last_shown: Optional[str] = None  # ISO 8601 timestamp
    terminal_cmd: Optional[list[str]] = None

    def dialog_due(self) -> bool:
        if self.dialog_last_shown is None:
            return True
        last = datetime.datetime.fromisoformat(self.dialog_last_shown)
        return datetime.datetime.now() - last >= DIALOG_COOLDOWN


@dataclasses.dataclass
class SyncResult:
    success: bool
    committed: bool
    changed_files: int
    message: str


def load_state() -> SyncState:
    if not STATE_FILE.exists():
        return SyncState()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return SyncState(**data)
    except (json.JSONDecodeError, TypeError):
        # Corrupt state file: start clean rather than crash the sync cycle.
        return SyncState()


def save_state(state: SyncState) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(dataclasses.asdict(state), indent=2), encoding="utf-8"
    )


# --------------------------------------------------------------------------
# Locking + live progress log (combined in one file, see LOCK_FILE above)
# --------------------------------------------------------------------------

@contextlib.contextmanager
def acquire_lock(lock_path: Path) -> Iterator[None]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    if lock_path.exists():
        age = datetime.datetime.now() - datetime.datetime.fromtimestamp(
            lock_path.stat().st_mtime
        )
        if age < STALE_LOG_AFTER:
            # A previous run is still actively writing to the log -> this is
            # a live, still-working process, not a stuck one. Skip quietly.
            raise RuntimeError(
                f"Previous sync run still active (last log line {age} ago); skipping this cycle."
            )
        # No new line for STALE_LOG_AFTER: treat as a crashed previous run.
        lock_path.unlink()

    lock_path.write_text(f"[{datetime.datetime.now().isoformat()}] pid {os.getpid()} started\n", encoding="utf-8")
    try:
        yield
    finally:
        lock_path.unlink(missing_ok=True)


def _log_line(text: str) -> None:
    """Append one line to the live log (updates its mtime) and, unless
    running with --silent, echo it to stdout immediately."""
    with LOCK_FILE.open("a", encoding="utf-8") as fh:
        fh.write(text.rstrip("\n") + "\n")
    if not SILENT:
        print(text.rstrip("\n"))


# --------------------------------------------------------------------------
# Fossil operations
# --------------------------------------------------------------------------

def run_fossil(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Blocking call for fast, local-only commands (add, changes, open)."""
    return subprocess.run(
        ["fossil", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def run_fossil_streaming(args: list[str], cwd: Path) -> tuple[int, str]:
    """For commands that may trigger a network transfer (update, commit).

    Reads Fossil's output line by line as it is produced -- not just after
    the process finishes -- and feeds every line into _log_line(). This is
    what keeps the live log (and therefore the staleness check in
    acquire_lock) accurate even during a very long, but still progressing,
    transfer. `--verbose` is expected to already be part of `args` by the
    caller so that Fossil actually emits per-round-trip progress lines
    instead of staying silent until the end (see implementierungs_doku.md,
    1.12 -- default Fossil output is deliberately terse since some 2.x
    release, --verbose restores the older, chattier behaviour).
    """
    proc = subprocess.Popen(
        ["fossil", *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        lines.append(line.rstrip("\n"))
        _log_line(line)
    proc.wait()
    return proc.returncode, "\n".join(lines)


def _extract_transfer_summary(text: str) -> Optional[tuple[int, int, str]]:
    """Look for Fossil's own "... finished with N bytes sent, M bytes
    received" line and return (sent, received, full_line) if found."""
    for line in text.splitlines():
        match = TRANSFER_SUMMARY_RE.search(line)
        if match:
            return int(match.group(1)), int(match.group(2)), line.strip()
    return None


def _find_conflict_markers(root: Path) -> list[Path]:
    hits: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if CONFLICT_MARKER in content:
            hits.append(path.relative_to(root))
    return hits


def preview_conflicts(repo_file: Path) -> list[Path]:
    """Try the update in a disposable shadow checkout; never touch ~/.claude.

    Returns the list of files (relative paths) that would end up with
    unresolved merge-conflict markers if the real checkout were updated now.
    An empty list means the real update can proceed safely.
    """
    shadow_dir = Path(tempfile.mkdtemp(prefix="claude-merge-preview-"))
    try:
        open_result = run_fossil(["open", str(repo_file), "-k"], cwd=shadow_dir)
        if open_result.returncode != 0:
            raise RuntimeError(f"Could not open shadow checkout: {open_result.stderr}")

        # --verbose so this contributes real progress lines to the live log
        # while a large preview transfer is still running; the transfer
        # summary itself is not reported to the user here -- this is a
        # discarded preview, not the actual sync (see 1.13).
        run_fossil_streaming(["update", "--verbose"], cwd=shadow_dir)
        return _find_conflict_markers(shadow_dir)
    finally:
        shutil.rmtree(shadow_dir, ignore_errors=True)


def perform_sync(claude_dir: Path) -> SyncResult:
    """Real update + add + commit in ~/.claude. Only call after a clean preview."""
    update_rc, update_out = run_fossil_streaming(["update", "--verbose"], cwd=claude_dir)
    run_fossil(["add", "."], cwd=claude_dir)

    changes = run_fossil(["changes"], cwd=claude_dir)
    changed_lines = [line for line in changes.stdout.splitlines() if line.strip()]
    if not changed_lines:
        summary = _extract_transfer_summary(update_out)
        message = summary[2] if summary and (summary[0] or summary[1]) else "Nothing to commit."
        return SyncResult(success=True, committed=False, changed_files=0, message=message)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_rc, commit_out = run_fossil_streaming(
        ["commit", "-m", f"Auto-sync {timestamp}", "--verbose", "--no-warnings"],
        cwd=claude_dir,
    )
    if commit_rc != 0:
        return SyncResult(
            success=False, committed=False, changed_files=len(changed_lines),
            message=f"Commit failed (see live log for details).",
        )

    summary = _extract_transfer_summary(commit_out) or _extract_transfer_summary(update_out)
    message = summary[2] if summary and (summary[0] or summary[1]) else f"Synced {len(changed_lines)} changed file(s), no network transfer."
    return SyncResult(
        success=True, committed=True, changed_files=len(changed_lines),
        message=message,
    )


# --------------------------------------------------------------------------
# Platform dispatch: dialogs, terminal launch, success notice
# --------------------------------------------------------------------------

def _is_windows() -> bool:
    return sys.platform.startswith("win")


def detect_terminal(state: SyncState) -> list[str]:
    """Return an argv prefix that, when a command is appended, opens a
    terminal running that command. Cached in state once found/chosen."""
    if _is_windows():
        raise NotImplementedError(
            "Windows terminal detection is planned (implementierungs_doku.md, 2.7)."
        )

    if state.terminal_cmd and shutil.which(state.terminal_cmd[0]):
        return state.terminal_cmd

    if shutil.which("xdg-terminal-exec"):
        chosen = ["xdg-terminal-exec", "--"]
        state.terminal_cmd = chosen
        save_state(state)
        return chosen

    found = [(binary, arg) for binary, arg in TERMINAL_CANDIDATES if shutil.which(binary)]

    if len(found) == 1:
        binary, arg = found[0]
        chosen = [binary, arg]
    elif len(found) > 1:
        options = "|".join(binary for binary, _ in found)
        pick = subprocess.run(
            ["zenity", "--list", "--title=Terminal wählen",
             "--text=Mehrere Terminal-Emulatoren gefunden, welcher soll verwendet werden?",
             "--column=Terminal", *[b for b, _ in found]],
            capture_output=True, text=True,
        )
        selected = pick.stdout.strip() or found[0][0]
        arg = dict(found)[selected]
        chosen = [selected, arg]
    else:
        entry = subprocess.run(
            ["zenity", "--entry", "--title=Terminal-Emulator",
             "--text=Kein bekannter Terminal-Emulator gefunden. Bitte Befehl angeben:"],
            capture_output=True, text=True,
        )
        binary = entry.stdout.strip() or "xterm"
        chosen = [binary, "-e"]

    state.terminal_cmd = chosen
    save_state(state)
    return chosen


def show_success_message(message: str) -> None:
    if _is_windows():
        raise NotImplementedError(
            "Windows success notice is planned (implementierungs_doku.md, 2.7)."
        )
    try:
        subprocess.run(
            ["zenity", "--info", "--text", message, "--timeout=3"],
            capture_output=True,
        )
    except FileNotFoundError:
        print(message)


def launch_claude_session(terminal_cmd: list[str], conflicted_files: list[Path], claude_dir: Path) -> None:
    file_list = ", ".join(str(f) for f in conflicted_files) or "(unbekannt, bitte selbst suchen)"
    prompt = (
        "A fossil update produced an unresolved merge conflict in this "
        f"directory. Reported file(s): {file_list}. Please locate the "
        "conflicted file(s) yourself (search for 'BEGIN MERGE CONFLICT' "
        "markers), explain the conflict to me in plain terms, and propose "
        "a resolution. Do not commit anything without my explicit approval."
    )
    subprocess.Popen(
        [*terminal_cmd, "claude", prompt],
        cwd=claude_dir,
        start_new_session=True,
    )


def handle_conflict(conflicted_files: list[Path], state: SyncState) -> None:
    state.conflict_active = True

    if not state.dialog_due():
        save_state(state)
        return

    if _is_windows():
        raise NotImplementedError(
            "Windows conflict dialog is planned (implementierungs_doku.md, 2.7)."
        )

    file_list = "\n".join(str(f) for f in conflicted_files)
    result = subprocess.run(
        ["zenity", "--question",
         "--title=Claude-Sync: Merge-Konflikt",
         f"--text=Konflikt in:\n{file_list}\n\nJetzt mit Claude lösen?",
         "--ok-label=Jetzt lösen", "--cancel-label=Später"],
    )
    state.dialog_last_shown = datetime.datetime.now().isoformat()
    save_state(state)

    if result.returncode == 0:
        terminal_cmd = detect_terminal(state)
        launch_claude_session(terminal_cmd, conflicted_files, CLAUDE_DIR)


# --------------------------------------------------------------------------
# Self-configuration of the background schedule (Linux: systemd --user)
# --------------------------------------------------------------------------

def set_sync_interval(minutes: int) -> None:
    if _is_windows():
        raise NotImplementedError(
            "Windows Task Scheduler reconfiguration is planned "
            "(implementierungs_doku.md, 2.7)."
        )

    timer_path = SYSTEMD_UNIT_DIR / SYSTEMD_TIMER_NAME
    if not timer_path.exists():
        raise FileNotFoundError(
            f"{timer_path} does not exist yet; install the systemd unit first "
            "(implementierungs_doku.md, 2.5) before changing its interval."
        )

    lines = timer_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    replaced = False
    for line in lines:
        if line.strip().startswith("OnUnitActiveSec="):
            new_lines.append(f"OnUnitActiveSec={minutes}min")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        raise RuntimeError(
            f"No OnUnitActiveSec= line found in {timer_path}; not touching the file."
        )

    timer_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "restart", SYSTEMD_TIMER_NAME], check=True)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def _run_sync_cycle() -> int:
    with acquire_lock(LOCK_FILE):
        conflicted = preview_conflicts(REPO_FILE)
        state = load_state()

        if conflicted:
            handle_conflict(conflicted, state)
            return 1

        if state.conflict_active:
            state.conflict_active = False
            state.dialog_last_shown = None
            save_state(state)

        result = perform_sync(CLAUDE_DIR)
        if result.committed:
            show_success_message(result.message)
            if SILENT:
                # Journal/stdout stays quiet during the run; report the
                # outcome once at the end, but only if something was
                # actually transferred (see implementierungs_doku.md, 1.13).
                summary = _extract_transfer_summary(result.message)
                if summary is None and result.message != "Nothing to commit.":
                    print(result.message)
        return 0 if result.success else 1


def main(argv: Optional[list[str]] = None) -> int:
    global SILENT

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--set-interval", type=int, metavar="MINUTES",
        help="Rewrite the background schedule to run every MINUTES minutes.",
    )
    parser.add_argument(
        "--silent", action="store_true",
        help=(
            "Suppress line-by-line progress output (still written to the "
            "live log). Intended for the systemd/Task-Scheduler ExecStart "
            "line, not for manual runs. Errors are always printed regardless "
            "of this flag."
        ),
    )
    args = parser.parse_args(argv)
    SILENT = args.silent

    if args.set_interval is not None:
        set_sync_interval(args.set_interval)
        print(f"Sync interval set to {args.set_interval} minute(s).")
        return 0

    try:
        return _run_sync_cycle()
    except RuntimeError as exc:
        # Always printed, even with --silent: errors must remain visible
        # in the journal.
        print(f"Sync cycle skipped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
