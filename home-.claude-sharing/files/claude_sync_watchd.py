#!/usr/bin/env python3
"""Watch a Syncthing-synchronised directory for conflict copies and escalate.

Usage
-----
    claude_sync_watchd.py                 run as a daemon (this is how the
                                          systemd unit starts it)
    claude_sync_watchd.py --once          run one pass and exit (for testing)
    claude_sync_watchd.py --dry-run       never show dialogs, never launch a
                                          session; print what would happen
    claude_sync_watchd.py --watch-dir DIR override the watched directory
                                          (default: ~/.claude)
    claude_sync_watchd.py --tool-dir DIR  override where state, instruction
                                          file and tools live (default:
                                          ~/.claude-sync-watch) -- for tests,
                                          so a trial run never touches the
                                          real installation

Long-running user service. The operating system notifies it of file changes;
it does not poll. On every pass it searches the watched directory for
Syncthing conflict copies (name part ``.sync-conflict-``), and if it finds
any it escalates to the user: a question dialog, and on approval a Claude
Code session in a terminal that resolves them together with the user.

What it never does (doku 2.1): it does not merge anything, does not write to
Syncthing's REST interface, does not pause or unpause the sync, and does not
modify any file in the watched directory. It observes, reports and escalates.

@Claude:
    This file is the daemon, not the conflict session. If you are reading it
    because a conflict session was started, the instructions you need are in
    ``konfliktloesung.md`` -- that file, not this one, governs what you do.

    If you are asked to change this script: the determinations it implements
    live in ``implementierungs_doku.md`` chapters 3.1 (behaviour), 3.2 (state
    file) and 3.3 (dialogs and terminal launch); the repo-wide rules are in
    chapter 2. Read the relevant chapter before editing, and propose a doc
    change together with any code change that alters behaviour.

    Two things are load-bearing and must not be "simplified" away: the
    fifteen-minute safety scan (file events do get lost -- see 3.1) and the
    rule that a failing operational notice must never break conflict
    detection (3.1, point 3).
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import enum
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Configuration (doku 2.7: everything this project brings lives in one folder)
# ---------------------------------------------------------------------------

# The installation directory is prescribed, not suggested: the systemd unit
# hardcodes %h/.claude-sync-watch, and install_service.sh refuses to run
# anywhere else (doku 2.7, 3.5). It is a module-level variable rather than a
# constant only so that a trial run can point it elsewhere via --tool-dir and
# never touch a real installation.
TOOL_DIR = Path.home() / ".claude-sync-watch"
STATE_FILE = TOOL_DIR / "zustand.json"
LOCK_FILE = TOOL_DIR / ".lauf.lock"
INSTRUCTION_FILE = TOOL_DIR / "konfliktloesung.md"
TOOLS_DIR = TOOL_DIR / "werkzeuge"


def set_tool_dir(directory: Path) -> None:
    """Point the daemon's own files at another directory (tests only)."""
    global TOOL_DIR, STATE_FILE, LOCK_FILE, INSTRUCTION_FILE, TOOLS_DIR
    TOOL_DIR = directory
    STATE_FILE = TOOL_DIR / "zustand.json"
    LOCK_FILE = TOOL_DIR / ".lauf.lock"
    INSTRUCTION_FILE = TOOL_DIR / "konfliktloesung.md"
    TOOLS_DIR = TOOL_DIR / "werkzeuge"

DEFAULT_WATCH_DIR = Path.home() / ".claude"

# The only part of the conflict-copy name that is documented and fixed. Date,
# time and device id follow, but their exact format is not guaranteed -- so
# the pattern deliberately keys on the literal alone (doku 3.1, step 1).
CONFLICT_MARKER = ".sync-conflict-"

# Directories never searched: archived old versions and Syncthing's own
# bookkeeping (doku 3.1, step 1).
SKIP_DIRS = {".stversions", ".stfolder"}

# Syncthing writes an incoming file to a temporary name and moves it into
# place only once it is complete. That name embeds the target name, so a
# conflict copy IN TRANSIT carries the conflict marker inside a temporary
# name -- and copies do travel to every device, which makes this the normal
# case, not an exotic one (doku 3.1, step 1). Such a file is not a finding:
# it is half of one, arriving. Recognised by name and skipped.
TEMP_PREFIXES = (".syncthing.", "~syncthing~")   # the second is Windows'
TEMP_SUFFIX = ".tmp"


def is_transfer_temporary(name: str) -> bool:
    """Whether *name* is a file Syncthing is still receiving."""
    return name.endswith(TEMP_SUFFIX) and name.startswith(TEMP_PREFIXES)

# A conflict copy is named <stem>.sync-conflict-<date>-<time>-<modifiedBy><suffix>.
# Used only to read the device id out; the search itself never relies on it.
# The id belongs to ONE of the two devices involved, in no dependable role: the
# copy travels to every device under the name it was given once, so the local
# device's own id can appear in it (doku 3.1, step 2). Never attribute a version
# to a machine by this id.
CONFLICT_NAME_RE = re.compile(
    r"^(?P<stem>.*)\.sync-conflict-(?P<date>\d{8})-(?P<time>\d{6})-"
    r"(?P<device>[^.]*)(?P<suffix>\..*)?$"
)

DIALOG_COOLDOWN = datetime.timedelta(minutes=30)
# Applies only after a dialog that could not be shown at all (doku 3.3).
DIALOG_RETRY_AFTER = datetime.timedelta(minutes=5)

# How long a dialog waits before closing itself. In SECONDS -- measured, and
# not a matter of taste: zenity rejects "15m" with exit code 255, which the
# classification below would read as a failure (doku 3.3).
DIALOG_TIMEOUT_SECONDS = 900

# Substrings that mark a zenity failure as "no usable display" rather than a
# cancelled dialog. Both exit with 1, so only the message separates them
# (measured, doku 3.3). Kept lowercase and short on purpose: the wording of
# the toolkit message is not a guaranteed interface.
DISPLAY_FAILURE_MARKERS = ("open display", "cannot open display", "no display")
SESSION_QUIET_TIME = datetime.timedelta(minutes=30)
NOTICE_INTERVAL = datetime.timedelta(hours=1)

# How long the hourly notice stays on screen. Good news may be brief -- it is
# a sign of life, and "everything fine" is read at a glance. Anything asking
# for attention must stay long enough to be read (doku 1.7). Both are wishes:
# whether `notify-send -t` is honoured is up to the notification daemon (Plasma
# does, GNOME Shell ignores it).
NOTICE_SECONDS_QUIET = 5
NOTICE_SECONDS_ATTENTION = 12
SAFETY_SCAN_INTERVAL = datetime.timedelta(minutes=15)
LOCK_STALE_AFTER = datetime.timedelta(minutes=5)

CLAUDE_BINARY = "/usr/bin/claude"

SYNCTHING_API = "http://127.0.0.1:8384"
SYNCTHING_CONFIG_CANDIDATES = [
    Path.home() / ".local" / "state" / "syncthing" / "config.xml",
    Path.home() / ".config" / "syncthing" / "config.xml",
]

TERMINAL_CANDIDATES: list[tuple[str, str]] = [
    ("x-terminal-emulator", "-e"),
    ("gnome-terminal", "--"),
    ("konsole", "-e"),
    ("xfce4-terminal", "-e"),
    ("alacritty", "-e"),
    ("kitty", "-e"),
    ("xterm", "-e"),
]

DRY_RUN = False


# ---------------------------------------------------------------------------
# Platform encapsulation (doku 2.4)
#
# Every OS-specific decision goes through this section. Adding Windows
# support (doku 3.7) means filling in these functions, not scattering
# platform checks through the logic below.
# ---------------------------------------------------------------------------

def _is_windows() -> bool:
    """The single place the platform is queried (doku 2.4)."""
    return os.name == "nt"


def _require_linux(what: str) -> None:
    """Refuse a platform-specific action rather than guessing at it."""
    if _is_windows():
        raise NotImplementedError(
            f"{what} is not implemented for Windows yet "
            "(implementierungs_doku.md, 3.7)."
        )


def notify(summary: str, body: str,
           seconds: int = NOTICE_SECONDS_QUIET) -> None:
    """Show a passive desktop notification. Never raises (doku 1.7).

    *seconds* is a request, not a guarantee: honouring `-t` is the
    notification daemon's decision (doku 1.7).
    """
    if DRY_RUN:
        print(f"[dry-run] notify ({seconds}s): {summary} -- {body}")
        return
    _require_linux("Desktop notification")
    try:
        subprocess.run(["notify-send", "-t", str(seconds * 1000),
                        summary, body], capture_output=True, check=False)
    except FileNotFoundError:
        # A missing notify-send must not break conflict detection.
        print(f"{summary}: {body}", file=sys.stderr)


class Answer(enum.Enum):
    """The three outcomes a question dialog really has.

    Two would be a trap: zenity that cannot reach a display exits non-zero,
    exactly like a cancelled dialog. A watcher whose only purpose is to
    escalate must not read "could not ask" as "user postponed" -- that turns a
    broken desktop into silence (doku 3.3).
    """

    YES = "yes"
    NO = "no"
    FAILED = "failed"


def ask_question(title: str, text: str, ok_label: str, cancel_label: str,
                 timeout_seconds: Optional[int] = None) -> Answer:
    """Ask a yes/no question; FAILED when the dialog could not be shown.

    The return code alone cannot tell cancel and failure apart -- measured,
    not assumed: zenity without a reachable display exits with 1, exactly like
    a cancelled dialog, and says "Failed to open display" on stderr. So the
    classification reads the message, and every non-empty message reaches the
    journal regardless of how it was classified: a case this misjudges is then
    at least visible instead of silent (doku 3.3).

    A message on stderr is emphatically NOT a failure signal by itself -- on
    the machine this was built on, a perfectly successful dialog warns about a
    stray key in its own GTK configuration every single time.

    With *timeout_seconds* the dialog closes itself; that counts as "no
    answer", handled like a deferral (doku 3.3).
    """
    _require_linux("Question dialog")
    command = ["zenity", "--question", f"--title={title}", f"--text={text}",
               f"--ok-label={ok_label}", f"--cancel-label={cancel_label}"]
    if timeout_seconds is not None:
        command.append(f"--timeout={timeout_seconds}")
    try:
        result = subprocess.run(command, capture_output=True, check=False)
    except FileNotFoundError:
        print("Dialog nicht möglich: 'zenity' ist nicht installiert.",
              file=sys.stderr, flush=True)
        return Answer.FAILED

    detail = (result.stderr or b"").decode("utf-8", "replace").strip()
    if detail:
        print(f"zenity meldete (Rückgabewert {result.returncode}): {detail}",
              file=sys.stderr, flush=True)

    if result.returncode == 0:
        return Answer.YES
    if result.returncode == 5:
        # Closed itself unanswered: nobody is sitting there. Treated like a
        # deferral, not like a defect -- the regular waiting time applies.
        print("Dialog lief ohne Antwort ab.", file=sys.stderr, flush=True)
        return Answer.NO

    lowered = detail.lower()
    if (result.returncode != 1
            or any(marker in lowered for marker in DISPLAY_FAILURE_MARKERS)):
        print("Dialog konnte nicht gezeigt werden -- das gilt nicht als "
              "vertagt.", file=sys.stderr, flush=True)
        return Answer.FAILED
    return Answer.NO


def pick_from_list(title: str, text: str, column: str,
                   options: list[str]) -> Optional[str]:
    """Let the user pick one option. None means cancelled.

    Proven behaviour (doku 3.8, tests/test_zenity_list.py): the choice comes
    back as plain text with a trailing newline; cancelling yields empty
    output and return code one.
    """
    _require_linux("Selection dialog")
    result = subprocess.run(
        ["zenity", "--list", f"--title={title}", f"--text={text}",
         f"--column={column}", *options],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def ask_text(title: str, text: str) -> Optional[str]:
    """Ask for free text. None means cancelled or empty."""
    _require_linux("Text entry dialog")
    result = subprocess.run(
        ["zenity", "--entry", f"--title={title}", f"--text={text}"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def child_environment() -> dict[str, str]:
    """Build the environment for the launched session, deliberately.

    Inheriting this process's environment wholesale is wrong in both
    directions, and a trial run proved the second one:

    * Too little -- a systemd user service starts sparse, which is why the
      Claude binary is called by absolute path (doku 3.3).
    * Too much -- if the watcher is itself started from inside a Claude Code
      session (as happens while testing), the child inherits that session's
      identity variables and goes through first-run onboarding instead of
      using the existing login. Observed: theme prompt, then an
      authentication prompt, in a session that had valid credentials on disk.

    ``TERM`` is dropped rather than set to a value: the terminal emulator is
    the authority on what its own child should see, and an inherited
    ``TERM=dumb`` made the session unreadable.
    """
    parent_prefixes = ("CLAUDE_CODE_",)
    parent_names = {"CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT",
                    "CLAUDE_AGENT_SDK_VERSION"}
    environment = {
        key: value for key, value in os.environ.items()
        if not key.startswith(parent_prefixes) and key not in parent_names
    }
    environment.pop("TERM", None)
    return environment


def spawn_detached(argv: list[str], cwd: Path) -> Optional[int]:
    """Start a process decoupled from this one; return its pid."""
    _require_linux("Terminal launch")
    process = subprocess.Popen(argv, cwd=str(cwd), start_new_session=True,
                               env=child_environment())
    return process.pid


def process_alive(pid: int) -> bool:
    """Whether a process with this pid still exists.

    ``os.kill(pid, 0)`` is POSIX; the Windows equivalent goes here too when
    3.7 is built. Signal zero asks the kernel about the process without
    sending anything to it.
    """
    _require_linux("Process check")
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Exists, owned by someone else -- for our purpose it exists.
        return True
    return True


# ---------------------------------------------------------------------------
# State (doku 3.2)
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class WatchState:
    """The small amount this daemon needs to remember between passes.

    Everything essential lives in the watched directory itself (the conflict
    copies); this file only holds what cannot be re-derived. An unreadable
    state file counts as empty and must never crash the daemon (doku 3.2) --
    the only visible cost is that the notice counters restart.
    """

    conflict_active: bool = False
    dialog_last_shown: Optional[str] = None
    terminal_cmd: Optional[list[str]] = None
    notice_last_shown: Optional[str] = None
    # Per device: {"in": int, "out": int, "startedAt": str} -- the comparison
    # values for the hourly byte delta (doku 3.1, point 1).
    transfer_baseline: dict[str, Any] = dataclasses.field(default_factory=dict)
    last_conflict_seen: Optional[str] = None
    session_pid: Optional[int] = None
    session_started: Optional[str] = None
    # True when the last attempt could not be shown at all (doku 3.3).
    dialog_failed: bool = False
    # Last time at least one device was connected -- the reference point for
    # "no connection since ..." in the notice (doku 1.7). Absent in state
    # files written by older versions, which stay readable.
    last_connected: Optional[str] = None

    def dialog_due(self) -> bool:
        """Whether the conflict dialog may be shown again (doku 2.9).

        After a failed attempt the short retry interval applies instead of the
        cooldown: nobody has seen anything yet, so there is nothing to spare
        the user from -- but the wait keeps a broken desktop from filling the
        journal at the pace of file events.
        """
        if self.dialog_last_shown is None:
            return True
        wait = DIALOG_RETRY_AFTER if self.dialog_failed else DIALOG_COOLDOWN
        return _age(self.dialog_last_shown) >= wait

    def notice_due(self) -> bool:
        """Whether the hourly operational notice is due (doku 3.1)."""
        if self.notice_last_shown is None:
            return True
        return _age(self.notice_last_shown) >= NOTICE_INTERVAL

    def session_running(self) -> bool:
        """Whether a conflict session is presumably still in progress.

        Two signals, because one is not reliable everywhere (doku 3.1,
        step 3): the pid, which is exact where the terminal keeps the process
        (konsole), and a thirty-minute quiet time, which covers the
        terminals that hand the job to a server and exit at once
        (gnome-terminal). Where the pid holds, detection is exact; where it
        does not, the daemon behaves as if there were none -- a dialog may
        return earlier, but the escalation is never lost.
        """
        if self.session_pid is not None and process_alive(self.session_pid):
            return True
        if self.session_started is not None:
            return _age(self.session_started) < SESSION_QUIET_TIME
        return False


def _now() -> str:
    """Current local time as an ISO 8601 string."""
    return datetime.datetime.now().isoformat()


def _age(timestamp: str) -> datetime.timedelta:
    """How long ago an ISO 8601 timestamp was. Unparsable counts as ancient."""
    try:
        return datetime.datetime.now() - datetime.datetime.fromisoformat(timestamp)
    except (ValueError, TypeError):
        return datetime.timedelta.max


def load_state() -> WatchState:
    """Read the state file; an unreadable one counts as empty (doku 3.2)."""
    if not STATE_FILE.exists():
        return WatchState()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        known = {field.name for field in dataclasses.fields(WatchState)}
        return WatchState(**{k: v for k, v in data.items() if k in known})
    except (OSError, json.JSONDecodeError, TypeError):
        return WatchState()


def save_state(state: WatchState) -> None:
    """Write the state file atomically."""
    TOOL_DIR.mkdir(parents=True, exist_ok=True)
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(dataclasses.asdict(state), indent=2),
                         encoding="utf-8")
    temporary.replace(STATE_FILE)


def acquire_lock() -> bool:
    """Guard against overlapping passes. False means another pass is running.

    A pass is short, so a lock file with an age limit is enough (doku 3.2).
    The running conflict *session* is deliberately not tracked here -- that is
    what session_pid and session_started are for.

    Created with O_CREAT|O_EXCL, which asks the kernel to create the file only
    if it does not exist and to fail otherwise -- one indivisible step. A
    check-then-write would leave a window between the two in which a second
    caller could also find the file absent, and that window is real here: the
    watchdog observer calls a pass from its own thread while the safety loop
    calls one from the main thread.
    """
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    for attempt in (1, 2):
        try:
            handle = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                             0o644)
        except FileExistsError:
            try:
                age = datetime.datetime.now() - datetime.datetime.fromtimestamp(
                    LOCK_FILE.stat().st_mtime)
            except FileNotFoundError:
                # Released between the failed create and the stat: try again.
                continue
            if age < LOCK_STALE_AFTER:
                return False
            if attempt == 1:
                # Older than any real pass could be: a crashed predecessor.
                LOCK_FILE.unlink(missing_ok=True)
                continue
            return False
        else:
            with os.fdopen(handle, "w", encoding="utf-8") as file:
                file.write(f"pid {os.getpid()} {_now()}\n")
            return True
    return False


def release_lock() -> None:
    """Drop the pass lock."""
    LOCK_FILE.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Finding and attributing conflict copies (doku 3.1, steps 1 and 2)
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class ConflictPair:
    """One conflict copy and the original it belongs to."""

    copy: Path
    original: Path
    device: str

    def describe(self) -> str:
        """One line for a dialog or a handover text.

        Names the device id, never a direction: "from" would claim an origin
        the name cannot carry (doku 3.1, step 2).
        """
        marked = f" (Gerätekennung {self.device})" if self.device else ""
        return f"{self.original.name}{marked}"


def find_conflicts(watch_dir: Path) -> list[Path]:
    """Search the watched directory for conflict copies.

    Keys on the fixed literal only -- date, time and device format are not
    guaranteed (doku 3.1, step 1). Skips archived versions, Syncthing's own
    directory, and files still being received: a copy in transit carries the
    marker inside a temporary name and would otherwise be reported as a pair
    whose original never existed.
    """
    found: list[Path] = []
    if not watch_dir.is_dir():
        return found
    for root, dirs, files in os.walk(watch_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if CONFLICT_MARKER in name and not is_transfer_temporary(name):
                found.append(Path(root) / name)
    return sorted(found)


def pair_conflicts(copies: list[Path]) -> list[ConflictPair]:
    """Map every copy to its original and read the device out of the name.

    One original may have several copies (maxConflicts is 10 per file, doku
    3.1 step 2). A copy whose name does not parse still gets paired -- the
    marker is stripped and the device left empty, because failing to report
    a conflict would be worse than reporting it without provenance.
    """
    pairs: list[ConflictPair] = []
    for copy in copies:
        match = CONFLICT_NAME_RE.match(copy.name)
        if match:
            original_name = match.group("stem") + (match.group("suffix") or "")
            device = match.group("device")
        else:
            original_name = copy.name.split(CONFLICT_MARKER)[0]
            device = ""
        pairs.append(ConflictPair(copy=copy,
                                  original=copy.parent / original_name,
                                  device=device))
    return pairs


# ---------------------------------------------------------------------------
# Terminal detection and session launch (doku 3.3)
#
# Taken over unchanged in behaviour from the proven pre-study
# (tests/test_detect_terminal.py, tests/test_zenity_list.py).
# ---------------------------------------------------------------------------

def detect_terminal(state: WatchState) -> Optional[list[str]]:
    """Return an argv prefix that opens a terminal running an appended command.

    Cached in the state file and reused as long as the command still exists
    (doku 3.3). None means the user cancelled the choice.
    """
    if state.terminal_cmd and shutil.which(state.terminal_cmd[0]):
        return state.terminal_cmd

    # freedesktop's own solution first; it does its own caching.
    if shutil.which("xdg-terminal-exec"):
        chosen = ["xdg-terminal-exec", "--"]
        state.terminal_cmd = chosen
        return chosen

    found = [(binary, arg) for binary, arg in TERMINAL_CANDIDATES
             if shutil.which(binary)]

    if len(found) == 1:
        chosen = [found[0][0], found[0][1]]
    elif len(found) > 1:
        selected = pick_from_list(
            "Claude-Sync: Terminal wählen",
            "Mehrere Terminal-Emulatoren gefunden. Welcher soll für die "
            "Konfliktsitzung verwendet werden?",
            "Terminal", [binary for binary, _ in found])
        if selected is None:
            return None
        chosen = [selected, dict(found).get(selected, "-e")]
    else:
        entered = ask_text(
            "Claude-Sync: Terminal-Emulator",
            "Kein bekannter Terminal-Emulator gefunden. Bitte Befehl angeben:")
        if entered is None:
            return None
        chosen = [entered, "-e"]

    state.terminal_cmd = chosen
    return chosen


def build_handover(pairs: list[ConflictPair], watch_dir: Path) -> str:
    """The text the conflict session is started with.

    Names the watched directory and the pairs with their origin device. The
    directory has to be *in the text*: the working instruction must not
    hardcode it, or the two would drift apart -- observed, when a session
    searched the production directory during a test run in another folder.
    The session is told to search for itself anyway (doku 3.4, step 1), so
    this list orients it rather than binding it.
    """
    lines = [f"  - {pair.describe()}" for pair in pairs]
    return (
        f"Syncthing hat Konfliktkopien angelegt, im Ordner {watch_dir} — "
        "genau dort und nirgends sonst ist zu suchen.\n"
        "Betroffene Originale:\n"
        + "\n".join(lines)
        + "\n\nBitte suche selbst nach *.sync-conflict-* und arbeite nach der "
          "Arbeitsanweisung, die dir als System-Prompt mitgegeben wurde."
    )


def launch_session(terminal_cmd: list[str], pairs: list[ConflictPair],
                   watch_dir: Path) -> Optional[int]:
    """Open a terminal with a Claude Code session for these conflicts.

    The absolute binary path matters: a systemd user service starts with a
    sparse environment and would not find ``claude`` on the search path
    (doku 3.3). The working directory is the watched directory, which is the
    only way to set it -- Claude Code takes it from the calling process.
    """
    # Argument order is load-bearing, not cosmetic: ``--add-dir`` is variadic
    # (``--add-dir <directories...>``), so it swallows every following argument
    # as another directory. With the prompt placed after it, the session
    # started with no prompt at all -- observed, and the reason this ordering
    # is fixed here. ``--append-system-prompt-file`` takes exactly one value,
    # so the prompt is safe behind it.
    argv = [
        *terminal_cmd,
        CLAUDE_BINARY,
        "--add-dir", str(TOOLS_DIR),
        "--append-system-prompt-file", str(INSTRUCTION_FILE),
        build_handover(pairs, watch_dir),
    ]
    if DRY_RUN:
        print("[dry-run] would launch:", " ".join(repr(a) for a in argv))
        return None
    return spawn_detached(argv, cwd=watch_dir)


def escalate(pairs: list[ConflictPair], state: WatchState,
             watch_dir: Path) -> None:
    """Run the dialog chain and, on approval, start the session (doku 3.3).

    Cancelling the terminal choice does not silently pick one: it asks once
    whether to try again, and a second cancel ends the chain without further
    questions -- the episode reports itself again later anyway.
    """
    listing = "\n".join(f"  {pair.describe()}" for pair in pairs)
    text = (
        f"Syncthing hat {len(pairs)} Konfliktkopie(n) angelegt:\n\n{listing}\n\n"
        "Zur Bearbeitung öffnet sich eine Claude-Code-Sitzung in einem "
        "Terminal. Gegebenenfalls ist dafür ein Terminal-Programm auszuwählen.\n\n"
        "Jetzt lösen?"
    )
    if DRY_RUN:
        print(f"[dry-run] would ask about {len(pairs)} conflict(s):\n{listing}")
        return

    state.dialog_last_shown = _now()
    answer = ask_question("Claude-Sync: Konflikt", text, "Jetzt lösen",
                          "Später", DIALOG_TIMEOUT_SECONDS)
    if answer is not Answer.YES:
        # A failed dialog is not a deferral: it keeps the short retry interval
        # so the next pass tries again instead of falling silent for half an
        # hour (doku 3.3).
        state.dialog_failed = answer is Answer.FAILED
        return
    state.dialog_failed = False

    while True:
        terminal_cmd = detect_terminal(state)
        if terminal_cmd is not None:
            break
        if ask_question(
                "Claude-Sync: Terminal nötig",
                "Zur Bearbeitung des Konflikts wird ein Terminal für die "
                "Claude-Sitzung benötigt. Auswahl erneut versuchen?",
                "Erneut versuchen", "Abbrechen",
                DIALOG_TIMEOUT_SECONDS) is not Answer.YES:
            return

    pid = launch_session(terminal_cmd, pairs, watch_dir)
    if pid is not None:
        state.session_pid = pid
        state.session_started = _now()


# ---------------------------------------------------------------------------
# Operational notice (doku 3.1) -- strictly optional decoration
# ---------------------------------------------------------------------------

def read_api_key() -> Optional[str]:
    """Read Syncthing's API key from its configuration.

    The key grants full control over Syncthing: it is read at runtime, never
    logged, never written into a notice, and lives outside the synchronised
    directory (doku 3.1, point 2).
    """
    for candidate in SYNCTHING_CONFIG_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        match = re.search(r"<apikey>([^<]+)</apikey>", text)
        if match:
            return match.group(1)
    return None


def rest_get(path: str, api_key: str) -> Optional[Any]:
    """Read one REST endpoint. None on any problem -- the notice is decoration.

    Read-only by construction: this is the only REST access in the daemon and
    it never writes (doku 2.1).
    """
    import urllib.error
    import urllib.request

    request = urllib.request.Request(f"{SYNCTHING_API}{path}",
                                     headers={"X-API-Key": api_key})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
        return None


def build_notice(state: WatchState, open_conflicts: int,
                 watch_dir: Path) -> Optional[tuple[str, int]]:
    """Assemble the hourly notice as text plus display time, or None.

    Three cases ask for attention and get the long display time: open
    conflicts, no connection at all, and a backlog. Everything else is the
    sign of life and may be brief (doku 1.7).
    """
    api_key = read_api_key()
    figures = _sync_figures(state, api_key, watch_dir) if api_key else None

    # Deliberately before the figures are needed: with conflicts open, a clear
    # pointer replaces the statistics so a postponed resolution does not fade
    # from view -- and it must appear even when the interface says nothing.
    if open_conflicts:
        since = ""
        if state.last_conflict_seen:
            hours = int(_age(state.last_conflict_seen).total_seconds() // 3600)
            since = f" seit {hours} Stunde(n)"
        # A pause changes what the user has to do -- the resolution would stay
        # local -- so it is named alongside, not instead.
        halted = "; Abgleich angehalten" if figures and figures["paused"] else ""
        return (f"{open_conflicts} Konflikt(e){since} ungelöst{halted}",
                NOTICE_SECONDS_ATTENTION)

    if figures is None:
        return None

    if figures["paused"]:
        # Before the connection check on purpose: a hand-set pause explains the
        # silence better than its symptom, and it is the user's own doing.
        return ("Abgleich für diesen Ordner angehalten — Änderungen und "
                "Konfliktkopien bleiben liegen", NOTICE_SECONDS_ATTENTION)

    if not figures["connected"]:
        since = ""
        if state.last_connected:
            hours = int(_age(state.last_connected).total_seconds() // 3600)
            since = f" seit {hours} Stunde(n)"
        return (f"keine Verbindung zum Abgleich{since}",
                NOTICE_SECONDS_ATTENTION)

    # Without a reference point, naming a span would be a lie. One sentence
    # covers both ways of lacking it -- a discarded state file (3.2) and a
    # fresh installation that has never seen a conflict. From the outside the
    # two are indistinguishable, and it is true of both.
    if state.last_conflict_seen:
        hours = int(_age(state.last_conflict_seen).total_seconds() // 3600)
        quiet = f"; kein Konflikt seit {hours} Stunde(n)"
    else:
        quiet = "; Zählung neu begonnen"

    text = (f"abgeglichen: {_human_bytes(figures['outgoing'])} hoch, "
            f"{_human_bytes(figures['incoming'])} herunter{quiet}")
    if figures["backlog"]:
        return (f"{text}; Rückstand: {figures['backlog']} Datei(en)",
                NOTICE_SECONDS_ATTENTION)
    return (text, NOTICE_SECONDS_QUIET)


def _human_bytes(count: float) -> str:
    """Byte count in a form a notice can show.

    Switches one tenth into the next unit instead of at its full value
    (doku 1.7): more than 0.1 kB reads as kB, more than 0.1 MB as MB. The
    deliberate consequence is that 500 kB shows as "0.5 MB" -- the point is a
    short number at a glance, not an exact magnitude.
    """
    step = 1024.0
    if count < 0.1 * step:
        return f"{count:.0f} B"
    for unit in ("kB", "MB"):
        count /= step
        if count < 0.1 * step:
            return f"{count:.1f} {unit}"
    return f"{count / step:.1f} GB"


def folder_config_for(watch_dir: Path,
                      api_key: str) -> Optional[dict[str, Any]]:
    """Syncthing's configuration entry for the watched directory, or None.

    Returns the whole entry, not just the id: the backlog needs the id, and
    the notice needs `paused` from the same answer (doku 1.7). Compares
    resolved paths, since the configuration may hold "~/.claude" rather than
    an absolute path.
    """
    config = rest_get("/rest/system/config", api_key)
    if not isinstance(config, dict):
        return None
    try:
        target = watch_dir.expanduser().resolve()
    except OSError:
        return None
    for folder in config.get("folders") or []:
        if not isinstance(folder, dict):
            continue
        try:
            if Path(str(folder.get("path") or "")).expanduser().resolve() == target:
                return folder
        except OSError:
            continue
    return None


def _sync_figures(state: WatchState, api_key: str,
                  watch_dir: Path) -> Optional[dict[str, Any]]:
    """Read the figures for the notice and refresh the comparison values.

    None means the interface said nothing usable -- the notice is decoration
    and then simply does not appear (doku 3.1, point 3).
    """
    connections = rest_get("/rest/system/connections", api_key)
    if not isinstance(connections, dict):
        return None

    # The byte counters are cumulative since the connection was established
    # and reset to zero on every reconnect. A delta is only meaningful while
    # startedAt is unchanged (doku 3.1, point 1).
    incoming = outgoing = 0
    connected = False
    baseline: dict[str, Any] = {}
    for device, info in (connections.get("connections") or {}).items():
        if not isinstance(info, dict):
            continue
        if info.get("connected"):
            connected = True
        started = info.get("startedAt") or ""
        current_in = int(info.get("inBytesTotal") or 0)
        current_out = int(info.get("outBytesTotal") or 0)
        baseline[device] = {"in": current_in, "out": current_out,
                            "startedAt": started}
        previous = state.transfer_baseline.get(device)
        if isinstance(previous, dict) and previous.get("startedAt") == started:
            incoming += max(0, current_in - int(previous.get("in") or 0))
            outgoing += max(0, current_out - int(previous.get("out") or 0))
    state.transfer_baseline = baseline
    if connected:
        state.last_connected = _now()

    backlog = 0
    paused = False
    folder = folder_config_for(watch_dir, api_key)
    if folder:
        # A pause the user set by hand stops the sync without anything looking
        # broken -- exactly the case the notice exists for (doku 1.7). Read,
        # never written: the watcher does not steer Syncthing (2.1).
        paused = bool(folder.get("paused"))
        status = rest_get(f"/rest/db/status?folder={folder.get('id')}", api_key)
        if isinstance(status, dict):
            backlog = int(status.get("needFiles") or 0)

    return {"connected": connected, "incoming": incoming, "outgoing": outgoing,
            "backlog": backlog, "paused": paused}


def maybe_notify(state: WatchState, open_conflicts: int,
                 watch_dir: Path) -> None:
    """Show the hourly notice if due. Never lets a failure propagate.

    The notice is decoration: if the interface is unreachable, the key
    missing or an answer oddly shaped, it silently does not appear -- conflict
    detection, the actual job, must never fail because of it (doku 3.1,
    point 3).
    """
    if not state.notice_due():
        return
    try:
        notice = build_notice(state, open_conflicts, watch_dir)
    except Exception:
        notice = None
    if notice is None:
        return
    text, seconds = notice
    state.notice_last_shown = _now()
    notify("Claude-Sync", text, seconds)


# ---------------------------------------------------------------------------
# One pass (doku 3.1, "Ablauf")
# ---------------------------------------------------------------------------

def run_pass(watch_dir: Path, reason: str) -> int:
    """Search, attribute, escalate if due, notify if due. Returns conflict count."""
    if not acquire_lock():
        return -1
    try:
        state = load_state()
        copies = find_conflicts(watch_dir)
        pairs = pair_conflicts(copies)

        if not pairs:
            # No finding: the episode ends by itself. That is the normal case
            # when the conflict was resolved on another machine and the
            # resolution has arrived here (doku 1.6, 3.1 step 4).
            state.conflict_active = False
        else:
            state.last_conflict_seen = _now()
            was_active = state.conflict_active
            state.conflict_active = True
            if state.session_running():
                # The user is working on it right now -- no dialog (step 3).
                pass
            elif state.dialog_due() or not was_active:
                escalate(pairs, state, watch_dir)

        maybe_notify(state, len(pairs), watch_dir)
        save_state(state)
        # One line per pass that found something -- as a service this is the
        # only trace in the journal (doku 3.5). Silence on an empty finding is
        # deliberate: the safety scan runs every 15 minutes and would otherwise
        # fill the journal with "nothing".
        if pairs or DRY_RUN:
            print(f"[{reason}] {len(pairs)} conflict(s) in {watch_dir}",
                  flush=True)
        return len(pairs)
    finally:
        release_lock()


# ---------------------------------------------------------------------------
# Event-driven observation with a safety net (doku 3.1)
# ---------------------------------------------------------------------------

def watch_forever(watch_dir: Path) -> int:
    """Observe the directory and run a pass on every relevant event.

    Two additions are mandatory because events alone are not enough
    (doku 3.1): a scan at startup, because copies created while the service
    was down raise no event any more; and a safety scan every fifteen
    minutes, because events do get lost (bounded queue, and a short race
    until a newly created directory is watched). Syncthing itself keeps its
    full scan for the same reason.
    """
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print("The Python package 'watchdog' is required but not installed.\n"
              "Install it through your distribution (for example: "
              "sudo apt install python3-watchdog) and start the service "
              "again.", file=sys.stderr)
        return 1

    # A conflict name is always a finished finding, never an intermediate
    # state: incoming transfers are written to .syncthing.<name>.tmp and
    # moved into place afterwards, whereas .sync-conflict- comes into being
    # by renaming the losing version once the conflict is settled. Hence no
    # debounce -- and both routes must be caught: locally the copy appears by
    # *renaming*, on the other devices by being *moved* in (doku 3.1).
    class ConflictHandler(FileSystemEventHandler):
        """Trigger a pass when something that looks like a copy shows up."""

        def _relevant(self, event: Any) -> bool:
            paths = [getattr(event, "src_path", ""),
                     getattr(event, "dest_path", "")]
            return any(CONFLICT_MARKER in str(p) for p in paths)

        def on_created(self, event: Any) -> None:
            if self._relevant(event):
                run_pass(watch_dir, "event:created")

        def on_moved(self, event: Any) -> None:
            if self._relevant(event):
                run_pass(watch_dir, "event:moved")

        def on_deleted(self, event: Any) -> None:
            # A copy that disappears ends the episode. Without this the state
            # would keep saying "unresolved" until the next safety scan -- up
            # to fifteen minutes -- and with a watcher on both machines the
            # copy vanishing because it was resolved elsewhere is the normal
            # case, not an edge one (doku 3.1, step 1).
            if self._relevant(event):
                run_pass(watch_dir, "event:deleted")

    run_pass(watch_dir, "startup scan")

    observer = Observer()
    observer.schedule(ConflictHandler(), str(watch_dir), recursive=True)
    observer.start()
    try:
        last_safety = datetime.datetime.now()
        while True:
            time.sleep(30)
            if datetime.datetime.now() - last_safety >= SAFETY_SCAN_INTERVAL:
                run_pass(watch_dir, "safety scan")
                last_safety = datetime.datetime.now()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    """Parse arguments and either run one pass or watch indefinitely."""
    global DRY_RUN

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--once", action="store_true",
                        help="run a single pass and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="show no dialogs and launch nothing; print instead")
    parser.add_argument("--watch-dir", default=str(DEFAULT_WATCH_DIR),
                        help="directory to watch (default: ~/.claude)")
    parser.add_argument("--tool-dir", default="",
                        help="where this daemon's own files live "
                             "(default: ~/.claude-sync-watch; for tests)")
    args = parser.parse_args(argv)

    DRY_RUN = args.dry_run
    if args.tool_dir:
        set_tool_dir(Path(args.tool_dir).expanduser())
    watch_dir = Path(args.watch_dir).expanduser()

    if not watch_dir.is_dir():
        print(f"Watched directory does not exist: {watch_dir}", file=sys.stderr)
        return 1

    if args.once:
        count = run_pass(watch_dir, "single pass")
        if count < 0:
            print("Another pass is currently running; did nothing.",
                  file=sys.stderr)
            return 1
        return 0

    return watch_forever(watch_dir)


if __name__ == "__main__":
    sys.exit(main())
