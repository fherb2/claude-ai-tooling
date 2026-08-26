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
    claude_sync_watchd.py --check-folder  report whether Syncthing has the
                                          watched directory as a folder and
                                          exit: 0 configured, 1 not
                                          configured, 2 could not tell.
                                          Read-only -- no lock, no state
                                          file (doku 3.5)

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
    ``conflict-resolution.md`` -- that file, not this one, governs what you do.

    If you are asked to change this script: the determinations it implements
    live in ``implementation-doc.md`` chapters 3.1 (behaviour), 3.2 (state
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
import shlex
import shutil
import subprocess
import sys
import time
import traceback
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
INSTRUCTION_FILE = TOOL_DIR / "conflict-resolution.md"
TOOLS_DIR = TOOL_DIR / "tools"


def set_tool_dir(directory: Path) -> None:
    """Point the daemon's own files at another directory (tests only)."""
    global TOOL_DIR, STATE_FILE, LOCK_FILE, INSTRUCTION_FILE, TOOLS_DIR
    TOOL_DIR = directory
    STATE_FILE = TOOL_DIR / "zustand.json"
    LOCK_FILE = TOOL_DIR / ".lauf.lock"
    INSTRUCTION_FILE = TOOL_DIR / "conflict-resolution.md"
    TOOLS_DIR = TOOL_DIR / "tools"

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

# How far a process's start time may differ from the session start we recorded
# and still count as the same process. Generous on purpose: the two clocks are
# coarse (boot time to the second, process start to a hundredth), and the point
# is not precision but telling our terminal from a stranger who got its number
# minutes or hours later (doku 3.1, step 3).
PID_START_TOLERANCE = datetime.timedelta(seconds=60)

NOTICE_INTERVAL = datetime.timedelta(hours=1)

# How long the hourly notice stays on screen. Good news may be brief -- it is
# a sign of life, and "everything fine" is read at a glance. Anything asking
# for attention must stay long enough to be read (doku 1.8). Both are wishes:
# whether `notify-send -t` is honoured is up to the notification daemon (Plasma
# does, GNOME Shell ignores it).
NOTICE_SECONDS_QUIET = 5
NOTICE_SECONDS_ATTENTION = 12

# Every notice is a leading statement plus up to two appended clauses. What
# separates them is a line break, not "; ": on one line the daemon wraps the
# second clause mid-phrase, and the eye has to jump back to the end of the
# first line to make sense of it (observed in service, doku 1.8).
#
# Measured against Plasma 5.27.12 with a control probe (doku 3.8): a real
# newline is honoured, and so is <br/>. The newline wins on how each FAILS
# elsewhere -- a daemon that ignores it falls back to today's single line,
# while one without `body-markup` would show the tag itself as text. The
# specification defines neither.
CLAUSE_BREAK = "\n"

# The pause wording, in one place because it appears in two notices (doku 3.1,
# point 4). Two deliberate forms, and they are laid out side by side so that
# changing one and forgetting the other shows up in the diff: an appended
# half-sentence where a conflict already carries the message, and a full
# sentence where the pause IS the message. Constants, not a function like
# `_backlog_clause`: that one carries a decision (empty at zero), the pause
# carries none -- the branch has already tested it. Function where something is
# decided, constant where there is only text.
PAUSE_CLAUSE_SHORT = CLAUSE_BREAK + "Abgleich angehalten"
PAUSE_SENTENCE = ("Abgleich für diesen Ordner angehalten — Änderungen und "
                  "Konfliktkopien bleiben liegen")
SAFETY_SCAN_INTERVAL = datetime.timedelta(minutes=15)

# Fallback only, for a lock whose holder cannot be read. The holder's pid
# decides (doku 3.2) -- a live holder keeps the lock however old it is. That
# matters because a pass legitimately outlives any short limit: its dialogs
# close themselves after fifteen minutes each, and the run lock is held for the
# whole stretch. The old five-minute limit called anything older "a crashed
# predecessor" and let the next pass steal the lock mid-dialog.
LOCK_STALE_AFTER = datetime.timedelta(minutes=60)

# Platform-neutral: Syncthing listens on this address on every system. The
# location of its configuration is not, and therefore lives in the platform
# section below (doku 2.4).
SYNCTHING_API = "http://127.0.0.1:8384"

# EX_CONFIG from sysexits.h: a precondition that no restart can heal. The unit
# pairs it with RestartPreventExitStatus, so the service stops visibly after
# the first attempt instead of looping (doku 3.5). Structural failures use it;
# a transient one -- the watched directory not being there yet -- keeps exit 1
# and its restart, because Claude Code creates that directory itself.
EXIT_PRECONDITION = 78

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
            "(implementation-doc.md, 3.7)."
        )


# Reported once per service run, not once per notice. The marker's purpose is
# "not hourly" (doku 2.6), not "never again": one line per run keeps the defect
# findable if the package is removed later, and needs no state field.
_notify_missing_reported = False


def syncthing_config_candidates() -> list[Path]:
    """Where Syncthing keeps its configuration, most likely first (doku 2.4).

    A platform-dependent *location*, so it belongs here and not in the
    configuration block at the top. The rule in 2.4 covers not only actions
    but data -- paths, program names, candidate lists -- because its whole
    justification for listing nothing is that the capsule is the directory:
    what depends on the platform is found at its calls. A path pair sitting
    among the constants is found at no call at all.

    Windows keeps it under %LOCALAPPDATA% (doku 3.7).
    """
    _require_linux("Syncthing configuration location")
    return [Path.home() / ".local" / "state" / "syncthing" / "config.xml",
            Path.home() / ".config" / "syncthing" / "config.xml"]


def terminal_candidates() -> list[tuple[str, str]]:
    """Known terminal emulators and the flag that runs a command in them.

    In priority order; the caller takes the first that exists. X11 names, so
    platform-dependent data -- the Windows counterpart is wt.exe/PowerShell
    (doku 3.7). Mirrored deliberately in tests/test_detect_terminal.py, which
    reimplements the cascade without importing this file.
    """
    _require_linux("Terminal candidate list")
    return [
        ("x-terminal-emulator", "-e"),
        ("gnome-terminal", "--"),
        ("konsole", "-e"),
        ("xfce4-terminal", "-e"),
        ("alacritty", "-e"),
        ("kitty", "-e"),
        ("xterm", "-e"),
    ]


def terminal_run_flags() -> tuple[str, ...]:
    """The flags that make a terminal run a command, most common first.

    Platform-dependent data, so it belongs in the capsule rather than sitting
    as a literal in the detection (doku 2.4, finding 5). Two uses: the fallback
    for a candidate whose flag is unknown, and the check whether a hand-typed
    command already carries one.
    """
    _require_linux("Terminal run flags")
    return ("-e", "--")


def claude_binary() -> str:
    """Absolute path of the Claude Code program (doku 3.3, 3.5).

    Absolute and not resolved through the search path: a systemd user service
    starts with a sparse environment and would not find it. That makes it a
    platform-dependent location like the two above, and it is capsuled rather
    than kept as a named exception -- an exception in 2.4 would reintroduce
    through the back door the enumeration that 2.4 rejects.
    """
    _require_linux("Claude Code location")
    return "/usr/bin/claude"


def notify(summary: str, body: str,
           seconds: int = NOTICE_SECONDS_QUIET) -> None:
    """Show a passive desktop notification. Never raises (doku 1.8).

    *seconds* is a request, not a guarantee: honouring `-t` is the
    notification daemon's decision (doku 1.8).
    """
    global _notify_missing_reported
    if DRY_RUN:
        print(f"[dry-run] Meldung ({seconds}s): {summary} -- {body}")
        return
    _require_linux("Desktop notification")
    try:
        result = subprocess.run(["notify-send", "-t", str(seconds * 1000),
                                 summary, body], capture_output=True,
                                check=False)
        if result.returncode != 0:
            # Present but unsuccessful: no notification daemon on the bus, no
            # DBUS_SESSION_BUS_ADDRESS, a timeout. Without this line the hourly
            # proof that the watcher lives could fail without a trace, and the
            # user would read the silence as a dead service (doku 2.6).
            # Deliberately WITHOUT the notice text: hourly it would be the
            # chatter 2.6 rules out, and in the journal it would quietly become
            # a third channel where 2.6 promises exactly two.
            detail = (result.stderr or b"").decode("utf-8", "replace").strip()
            print(f"'notify-send' endete mit Rückgabewert "
                  f"{result.returncode}: {detail or 'ohne Meldung'}",
                  file=sys.stderr, flush=True)
    except FileNotFoundError:
        # A missing notify-send must not break conflict detection (doku 1.8).
        # The notice text itself does NOT go to the journal: hourly it would be
        # the chatter doku 2.6 rules out, and it would quietly become a third
        # channel where 2.6 promises exactly two. Reported once per run instead.
        if not _notify_missing_reported:
            _notify_missing_reported = True
            print("'notify-send' fehlt — die stündliche Betriebsmeldung kann "
                  "nicht am Bildschirm erscheinen. Bitte 'libnotify-bin' "
                  "installieren: sudo apt install libnotify-bin. "
                  "Konflikterkennung und Eskalation sind unberührt.",
                  file=sys.stderr, flush=True)


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
    return zenity_outcome(result)


def zenity_outcome(result: subprocess.CompletedProcess,
                   expects_answer: bool = True) -> Answer:
    """Classify a finished zenity call and journal whatever it said.

    Kept in ONE place on purpose. The rule below used to live inside the
    question dialog alone, and the other two windows of the escalation chain
    drifted away from it: they read every non-zero return code as "cancelled"
    and threw the error output away, so a display that broke mid-chain looked
    exactly like a user postponing (doku 3.3).

    *expects_answer* is False for a window that only informs. Its self-closing
    is then the normal course and not worth a line.
    """
    stderr = result.stderr or b""
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", "replace")
    detail = stderr.strip()
    if detail:
        # Unconditionally, whatever the classification below decides: a case
        # this misjudges is then at least visible instead of silent (doku 3.3).
        print(f"zenity meldete (Rückgabewert {result.returncode}): {detail}",
              file=sys.stderr, flush=True)

    if result.returncode == 0:
        return Answer.YES
    if result.returncode == 5:
        # Closed itself unanswered: nobody is sitting there. Treated like a
        # deferral, not like a defect -- the regular waiting time applies.
        if expects_answer:
            print("Dialog lief ohne Antwort ab.", file=sys.stderr, flush=True)
        return Answer.NO

    lowered = detail.lower()
    if (result.returncode != 1
            or any(marker in lowered for marker in DISPLAY_FAILURE_MARKERS)):
        print("Dialog konnte nicht gezeigt werden -- das gilt nicht als "
              "vertagt.", file=sys.stderr, flush=True)
        return Answer.FAILED
    return Answer.NO


def show_message(title: str, text: str,
                 timeout_seconds: Optional[int] = DIALOG_TIMEOUT_SECONDS) -> None:
    """Tell the user something that needs doing. No answer is evaluated.

    A window rather than a desktop notification, because 2.9 draws the line not
    at the tool but at the question "is a reaction needed" -- and here one is.
    Failure to show it is not silent: every non-empty stderr reaches the journal,
    as with every other dialog (doku 3.3).
    """
    _require_linux("Message dialog")
    command = ["zenity", "--error", f"--title={title}", f"--text={text}"]
    if timeout_seconds is not None:
        command.append(f"--timeout={timeout_seconds}")
    try:
        result = subprocess.run(command, capture_output=True, check=False)
    except FileNotFoundError:
        print("Meldung nicht möglich: 'zenity' ist nicht installiert.",
              file=sys.stderr, flush=True)
        return
    zenity_outcome(result, expects_answer=False)


def pick_from_list(title: str, text: str, column: str, options: list[str],
                   timeout_seconds: Optional[int] = None
                   ) -> tuple[Answer, Optional[str]]:
    """Let the user pick one option. Returns the outcome and the choice.

    Proven behaviour (doku 3.8, tests/test_zenity_list.py): the choice comes
    back as plain text with a trailing newline; cancelling yields empty
    output and return code one.

    The outcome is returned alongside the value, not folded into "None",
    because the caller has to tell a cancelling user from a display that
    cannot be reached: only the second one keeps the short retry interval
    instead of the half hour (doku 3.3).

    The timeout matters as much here as for the question dialog: this runs
    inside a pass, so an unanswered window would hold the run lock -- and a
    held lock makes the watcher deaf to everything else (doku 3.3).
    """
    _require_linux("Selection dialog")
    command = ["zenity", "--list", f"--title={title}", f"--text={text}",
               f"--column={column}", *options]
    if timeout_seconds is not None:
        command.append(f"--timeout={timeout_seconds}")
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                check=False)
    except FileNotFoundError:
        print("Auswahl nicht möglich: 'zenity' ist nicht installiert.",
              file=sys.stderr, flush=True)
        return Answer.FAILED, None
    outcome = zenity_outcome(result)
    if outcome is not Answer.YES:
        return outcome, None
    return outcome, (result.stdout.strip() or None)


def ask_text(title: str, text: str,
             timeout_seconds: Optional[int] = None
             ) -> tuple[Answer, Optional[str]]:
    """Ask for free text. Returns the outcome and the entered text.

    Same reasoning as for the selection dialog: the outcome is separate from
    the value, and a timeout counts as a deferral because the pass holds the
    run lock while this window waits (doku 3.3).
    """
    _require_linux("Text entry dialog")
    command = ["zenity", "--entry", f"--title={title}", f"--text={text}"]
    if timeout_seconds is not None:
        command.append(f"--timeout={timeout_seconds}")
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                check=False)
    except FileNotFoundError:
        print("Eingabe nicht möglich: 'zenity' ist nicht installiert.",
              file=sys.stderr, flush=True)
        return Answer.FAILED, None
    outcome = zenity_outcome(result)
    if outcome is not Answer.YES:
        return outcome, None
    return outcome, (result.stdout.strip() or None)


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


# The terminal stays a child of this process, so somebody has to collect its
# exit status -- otherwise it lingers in the process table as a zombie. Keeping
# the object is the whole mechanism: dropping it left the reaping to CPython's
# housekeeping on the next Popen call anywhere in the daemon, which made it
# depend on unrelated activity. Only one session runs at a time, and every pass
# is serialised by the run lock, so a single slot needs no locking of its own.
_session_process: Optional[subprocess.Popen] = None


def spawn_detached(argv: list[str], cwd: Path) -> Optional[int]:
    """Start a process decoupled from this one; return its pid."""
    global _session_process
    _require_linux("Terminal launch")
    try:
        process = subprocess.Popen(argv, cwd=str(cwd), start_new_session=True,
                                   env=child_environment())
    except OSError as error:
        # An unusable terminal command reached Popen and the exception rose all
        # the way up, killing the pass and with it the observer thread. Reported
        # and turned into "no pid" instead: the caller then leaves the episode
        # open, and it reports itself again later (doku 3.3, 2.6).
        print(f"Terminalstart fehlgeschlagen ({argv[0]!r}): {error}",
              file=sys.stderr, flush=True)
        return None
    _session_process = process
    return process.pid


def reap_finished_session() -> None:
    """Collect the terminal's exit status once it has ended (doku 3.1, step 3).

    Hygiene, not a fix: a zombie is recognised as such by its process state
    anyway. This keeps the process table clean and makes the collection happen
    at a defined moment instead of as a side effect of the next subprocess call.
    """
    global _session_process
    if _session_process is not None and _session_process.poll() is not None:
        _session_process = None


def process_running_since(pid: int) -> Optional[datetime.datetime]:
    """When *pid* started, or None if it is not a running process any more.

    Exists because "does this pid exist" is the wrong question for deciding
    whether our conflict session is still open (doku 3.1, step 3). It answers
    yes in two cases where the session is over, and neither is visible to
    ``os.kill(pid, 0)``:

    * The terminal ended but nobody collected its status -- it lingers as a
      zombie, and signal zero reaches it.
    * The number was recycled and now belongs to a stranger. Linux hands pids
      out cyclically, so this is a matter of uptime, not of luck.

    None means the same thing in every case it can occur -- gone, zombie, or
    ``/proc`` unreadable because the number belongs to another user, which
    equally means it is not our session. The start time lets the caller tell
    our own terminal from a stranger holding its old number.

    Linux-specific and therefore in this section (doku 2.4): it reads the
    process state and start time from ``/proc/<pid>/stat``. Windows gets its
    own implementation here when 3.7 is built.
    """
    _require_linux("Process start time")
    try:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        # The second field is the executable name in brackets and may itself
        # contain spaces and brackets, so fields are counted from the LAST
        # closing bracket -- splitting the whole line would miscount.
        fields = raw[raw.rindex(")") + 2:].split()
        if fields[0] == "Z":
            return None
        ticks = int(fields[19])
    except (OSError, ValueError, IndexError):
        return None
    boot = _boot_time()
    if boot is None:
        return None
    return boot + datetime.timedelta(seconds=ticks / os.sysconf("SC_CLK_TCK"))


def _boot_time() -> Optional[datetime.datetime]:
    """Wall-clock time the system booted, from ``/proc/stat`` (doku 2.4).

    Refuses explicitly rather than relying on its only caller being
    guarded: a location under /proc is as platform-dependent as any
    other, and the next caller might not be guarded.
    """
    _require_linux("Boot time")
    try:
        for line in Path("/proc/stat").read_text(encoding="utf-8").splitlines():
            if line.startswith("btime "):
                return datetime.datetime.fromtimestamp(int(line.split()[1]))
    except (OSError, ValueError, IndexError):
        return None
    return None


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
    # When the current episode began -- a second clock, because the two spans
    # the notice can name are opposites: the quiet form counts from the last
    # sighting, the conflict hint from the start of the episode (doku 1.8, 3.2).
    # One field for both could only ever say "0 hours".
    conflict_since: Optional[str] = None
    session_pid: Optional[int] = None
    session_started: Optional[str] = None
    # True when the last attempt could not be shown at all (doku 3.3).
    dialog_failed: bool = False
    # True while the last search could not cover the whole directory (doku
    # 3.1, step 1). Kept in the state only to report the CHANGE: a line per
    # pass would arrive at the pace of file events, and the situation persists
    # until someone fixes the permissions or the mount.
    scan_incomplete: bool = False
    # Last time at least one device was connected -- the reference point for
    # "no connection since ..." in the notice (doku 1.8). Absent in state
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
        if self.session_started is None:
            return False
        if _age(self.session_started) < SESSION_QUIET_TIME:
            return True
        if self.session_pid is None:
            return False
        # Past the quiet time only the pid can still speak for the session, and
        # only if it is demonstrably the process we started: same number AND a
        # start time matching what we recorded. That is what protects a session
        # lasting longer than half an hour -- the case the quiet time cannot
        # cover -- while a zombie, a recycled number or a stranger's process all
        # answer "not running" (doku 3.1, step 3).
        started = process_running_since(self.session_pid)
        if started is None:
            return False
        try:
            recorded = datetime.datetime.fromisoformat(self.session_started)
        except (ValueError, TypeError):
            return False
        return abs(started - recorded) <= PID_START_TOLERANCE


def _now() -> str:
    """Current local time as an ISO 8601 string, WITH its zone offset.

    The offset is what makes a difference between two stamps exact across a
    daylight-saving change: without it, a stamp written at 02:50 CEST and read
    at 02:10 CET -- twenty real minutes -- computes as MINUS forty (doku 3.2).

    Local time rather than UTC on purpose: the state file is also a diagnostic
    surface a person reads, and "02:50:00+02:00" says something at a glance
    where "00:50:00+00:00" needs arithmetic first. Both are equally exact.
    """
    return datetime.datetime.now().astimezone().isoformat()


def _age(timestamp: str) -> datetime.timedelta:
    """How long ago an ISO 8601 timestamp was. Unparsable counts as ancient.

    Reads BOTH forms, and that is not a courtesy: subtracting a naive datetime
    from an aware one raises TypeError, which the branch below would turn into
    "ancient" -- and then every waiting period in an existing state file would
    be due at once, on the first pass after the change (doku 3.2). A stamp
    without an offset is therefore read as local time, which resolves winter
    and summer correctly by date. Its one residual: a naive stamp from the
    SECOND pass through an ambiguous hour is read an hour off, once.
    """
    try:
        moment = datetime.datetime.fromisoformat(timestamp)
    except (ValueError, TypeError):
        return datetime.timedelta.max
    if moment.tzinfo is None:
        moment = moment.astimezone()
    return datetime.datetime.now().astimezone() - moment


def _hours_since(timestamp: str) -> int:
    """Full hours since a timestamp, never negative (doku 1.8).

    One place for the rule, because three notices ask for it. The clamp holds
    even where the zone offset cannot help: a corrected system clock moves
    wall-clock time in both directions, and "kein Konflikt seit -1 Stunde(n)"
    is the kind of sentence nobody can explain from the outside.
    """
    return max(0, int(_age(timestamp).total_seconds() // 3600))


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
                # Clamped at zero, and precisely about the journal line
                # below: after the clock moves back, a lock file looks as if it
                # came from the future, and "Alter -3540 s" is a sentence
                # nobody can act on. The DECISION is unaffected -- a negative
                # age is below the limit just as zero is, and the age only
                # decides at all when the holder cannot be read. A forward jump
                # cannot be caught here and need not be: the holder's pid
                # decides, and that check hangs on no clock (doku 3.2).
                age = max(
                    datetime.timedelta(0),
                    datetime.datetime.now() - datetime.datetime.fromtimestamp(
                        LOCK_FILE.stat().st_mtime))
            except FileNotFoundError:
                # Released between the failed create and the stat: try again.
                continue
            holder = lock_holder()
            if holder is not None and process_alive(holder):
                return False
            if holder is None and age < LOCK_STALE_AFTER:
                return False
            if attempt == 1:
                whose = (f"von PID {holder}" if holder is not None
                         else "ohne lesbare PID")
                print(f"Laufsperre {whose} war ein Überrest (Alter "
                      f"{int(age.total_seconds())} s) und wurde entfernt.",
                      file=sys.stderr, flush=True)
                LOCK_FILE.unlink(missing_ok=True)
                continue
            return False
        else:
            with os.fdopen(handle, "w", encoding="utf-8") as file:
                file.write(f"pid {os.getpid()} {_now()}\n")
            return True
    return False


def lock_holder() -> Optional[int]:
    """The pid recorded in the lock file, or None if it cannot be read.

    None is the honest answer for "unreadable", not a guess: the caller then
    falls back to the age limit instead of treating the lock as free.
    """
    try:
        first = LOCK_FILE.read_text(encoding="utf-8").split()
    except OSError:
        return None
    if len(first) >= 2 and first[0] == "pid":
        try:
            return int(first[1])
        except ValueError:
            return None
    return None


def release_lock() -> None:
    """Drop the pass lock -- but only our own.

    Releasing indiscriminately turns one overlap into a cascade: the finishing
    pass deletes the lock of the pass that overtook it, and a third one walks
    straight in (doku 3.2).
    """
    holder = lock_holder()
    if holder is not None and holder != os.getpid():
        print(f"Laufsperre gehört PID {holder}, nicht diesem Durchgang — "
              "nicht entfernt.", file=sys.stderr, flush=True)
        return
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


def find_conflicts(watch_dir: Path) -> tuple[list[Path], list[str]]:
    """Search the watched directory for conflict copies.

    Returns the findings **and** whatever kept the search from being complete.
    That second list is the whole point: "found nothing" and "could not look"
    used to be the same empty answer, and the second one is the worst outcome
    for a tool that exists only to escalate -- it reports calm for ever while
    seeing nothing, and calm is the normal state (doku 3.1 step 1, 1.5, F7).
    Two ways it happens: the watched directory is gone or unreadable (moved,
    a mount point away, permissions changed), and a subdirectory that
    ``os.walk`` silently skips because it cannot be entered.

    Keys on the fixed literal only -- date, time and device format are not
    guaranteed. Skips archived versions, Syncthing's own directory, and files
    still being received: a copy in transit carries the marker inside a
    temporary name and would otherwise be reported as a pair whose original
    never existed.
    """
    found: list[Path] = []
    problems: list[str] = []
    if not watch_dir.is_dir():
        return found, [f"{watch_dir}: nicht vorhanden oder kein Verzeichnis"]

    def note(error: OSError) -> None:
        problems.append(f"{error.filename}: {error.strerror}")

    for root, dirs, files in os.walk(watch_dir, onerror=note):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if CONFLICT_MARKER in name and not is_transfer_temporary(name):
                found.append(Path(root) / name)
    return sorted(found), problems


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

def _terminal_from_text(entered: str) -> Optional[list[str]]:
    """Turn a hand-typed terminal command into an argv prefix, or None.

    Taken apart with shlex instead of used as one word: "urxvt -hold" is what a
    user naturally types, and as argv[0] that is a program name containing a
    space -- one that can never exist. EVERY multi-word entry was therefore
    broken, not just a typo (doku 3.3).

    The user's words are kept and the run flag is APPENDED, unless they already
    typed one: the flag has to end up last, directly before the command, and
    doubling it would break the launch just as surely as leaving it out.
    """
    try:
        words = shlex.split(entered)
    except ValueError:
        return None                      # unbalanced quotes, for instance
    if not words or not shutil.which(words[0]):
        return None
    flags = terminal_run_flags()
    if any(word in flags for word in words):
        return words
    return [*words, flags[0]]


def _distinct_terminals(
        candidates: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """The candidates that exist, one entry per actual program (doku 3.3).

    ``x-terminal-emulator`` is not an emulator but Debian's alternatives link
    to one of the others, so the plain list offers the same program twice --
    three lines for two programs, measured on this machine.

    Which of the two survives is not a matter of taste: every candidate carries
    ITS OWN launch flag, and six of the seven use ``-e`` while gnome-terminal
    needs ``--``. Where the link points at gnome-terminal, picking the link
    would launch it with the flag this very table calls wrong for it. The entry
    whose own name matches the resolved program therefore wins. If none
    matches, the link points at something unknown to us and is kept -- there it
    is the best guess available.
    """
    seen: dict[Path, tuple[str, str]] = {}
    for binary, arg in candidates:
        path = shutil.which(binary)
        if not path:
            continue
        try:
            target = Path(path).resolve()
        except OSError:
            target = Path(path)
        if target not in seen or target.name == binary:
            seen[target] = (binary, arg)
    return list(seen.values())


def detect_terminal(state: WatchState) -> tuple[Answer, Optional[list[str]]]:
    """Find an argv prefix that opens a terminal running an appended command.

    Returns the outcome next to the result: a command with ``Answer.YES``, a
    cancelled choice with ``Answer.NO``, and a dialog that could not be shown
    at all with ``Answer.FAILED``. The last one has to reach the caller,
    because only it keeps the short retry interval instead of the half hour
    (doku 3.3) -- folded into a bare "None" it looked like a user postponing.

    The result is cached in the state file and reused as long as the command
    still exists.
    """
    if state.terminal_cmd and shutil.which(state.terminal_cmd[0]):
        return Answer.YES, state.terminal_cmd

    # freedesktop's own solution first; it does its own caching.
    if shutil.which("xdg-terminal-exec"):
        chosen = ["xdg-terminal-exec", "--"]
        state.terminal_cmd = chosen
        return Answer.YES, chosen

    found = _distinct_terminals(terminal_candidates())

    if len(found) == 1:
        chosen = [found[0][0], found[0][1]]
    elif len(found) > 1:
        outcome, selected = pick_from_list(
            "Claude-Sync: Terminal wählen",
            "Mehrere Terminal-Emulatoren gefunden. Welcher soll für die "
            "Konfliktsitzung verwendet werden?",
            "Terminal", [binary for binary, _ in found],
            DIALOG_TIMEOUT_SECONDS)
        if selected is None:
            return outcome, None
        chosen = [selected, dict(found).get(selected, terminal_run_flags()[0])]
    else:
        outcome, entered = ask_text(
            "Claude-Sync: Terminal-Emulator",
            "Kein bekannter Terminal-Emulator gefunden. Bitte Befehl angeben:",
            DIALOG_TIMEOUT_SECONDS)
        if entered is None:
            return outcome, None
        candidate = _terminal_from_text(entered)
        if candidate is None:
            # Not silently accepted: the launch would fail deep inside Popen,
            # where the exception used to kill the whole pass. Reported here,
            # and the answer NO lands in the retry question escalate already
            # asks -- one loop, not a second one (doku 3.3).
            print(f"Eingegebener Terminal-Befehl nicht verwendbar: {entered!r}",
                  file=sys.stderr, flush=True)
            show_message(
                "Claude-Sync: Terminal-Befehl unbrauchbar",
                f"Der eingegebene Befehl „{entered}“ lässt sich nicht "
                "verwenden — das erste Wort muss ein vorhandenes Programm "
                "sein. Beispiele: „konsole“ oder „urxvt -hold“.")
            return Answer.NO, None
        chosen = candidate

    state.terminal_cmd = chosen
    return Answer.YES, chosen


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
    # Without the instruction file Claude Code refuses to start at all: it
    # answers "Append system prompt file not found" and exits, so the terminal
    # flashes up and is gone (doku 3.3). Unchecked, the daemon would record a
    # pid and treat the episode as in progress -- the escalation would burn,
    # silently, and the next question came half an hour later. The installer
    # covers this at setup time only, and --tool-dir bypasses it entirely.
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    if not INSTRUCTION_FILE.is_file():
        print(f"Arbeitsanweisung fehlt: {INSTRUCTION_FILE} — keine Sitzung "
              "gestartet.", file=sys.stderr, flush=True)
        show_message(
            "Claude-Sync: Konfliktlösung nicht möglich",
            f"Die Arbeitsanweisung {INSTRUCTION_FILE} fehlt. Ohne sie kann "
            "keine Konfliktsitzung starten. Bitte den Inhalt des "
            "files/-Ordner aus der Repo-Quelle von claude-sync-watch "
            "vollständig nach ~/.claude-sync-watch kopieren. Dort ist auch "
            "das fehlende File 'conflict-resolution.md' enthalten.")
        return None
    # Argument order is load-bearing, not cosmetic: ``--add-dir`` is variadic
    # (``--add-dir <directories...>``), so it swallows every following argument
    # as another directory. With the prompt placed after it, the session
    # started with no prompt at all -- observed, and the reason this ordering
    # is fixed here. ``--append-system-prompt-file`` takes exactly one value,
    # so the prompt is safe behind it.
    argv = [
        *terminal_cmd,
        claude_binary(),
        "--add-dir", str(TOOLS_DIR),
        "--append-system-prompt-file", str(INSTRUCTION_FILE),
        build_handover(pairs, watch_dir),
    ]
    if DRY_RUN:
        print("[dry-run] würde starten:", " ".join(repr(a) for a in argv))
        return None
    pid = spawn_detached(argv, cwd=watch_dir)
    if pid is None:
        # Same treatment as a missing instruction file: tell the user, record
        # no pid, let the episode report itself again (doku 3.3).
        show_message(
            "Claude-Sync: Terminal konnte nicht starten",
            f"Der Terminalbefehl „{' '.join(terminal_cmd)}“ ließ sich nicht "
            "ausführen. Die Konfliktkopien bleiben liegen; der Wächter meldet "
            "sich wieder. Einzelheiten stehen im Journal: "
            "journalctl --user -u claude-sync-watch")
    return pid


def defer(state: WatchState) -> None:
    """Note that the user had the opportunity and did not take it (doku 2.9).

    The waiting time is counted from the deferral, not from the moment the
    dialog appeared. That matters because a dialog closes itself after fifteen
    minutes: stamped at the appearance, half the promised half hour was already
    gone when the deferral happened, and the next dialog could arrive twice as
    early as 2.9 assures. Called at every exit of the chain that is a deferral,
    not only after the first question -- the chain can take three quarters of an
    hour before the last one.

    The early stamp in `escalate` stays: it protects against a crash mid-chain,
    it makes an overlapping pass see the episode rule, and after a dialog that
    could not be shown at all it is exactly right -- there the short retry runs
    from the attempt, because nobody deferred anything.
    """
    state.dialog_last_shown = _now()


def escalate(pairs: list[ConflictPair], state: WatchState,
             watch_dir: Path) -> None:
    """Run the dialog chain and, on approval, start the session (doku 3.3).

    Cancelling the terminal choice does not silently pick one: it asks whether
    to try again, and cancelling that ends the chain -- the episode reports
    itself again later anyway.

    Choosing to retry starts another round, and the number of rounds is
    deliberately not capped (doku 3.3). A cap would lock out the very user who
    is sitting there trying: the chain would end and 2.9 would then hold the
    next dialog back for half an hour. Leaving costs one click instead. The run
    lock is held throughout, but every round requires a deliberate click, so
    the deafness from finding 25 -- which is about a lock nobody is watching --
    does not apply here. What bounds the unattended case is the self-close
    time: a timed-out retry question ends the chain after at most three windows.
    """
    # The list is labelled, as it is in the handover text: what follows are the
    # ORIGINALS, not the copies whose number the line above states. Without the
    # label the names read as the copies' names, which they are not -- they
    # carry neither the date nor the device suffix (doku 1.8, 3.3).
    listing = "\n".join(f"  {pair.describe()}" for pair in pairs)
    text = (
        f"Syncthing hat {len(pairs)} Konfliktkopie(n) angelegt.\n\n"
        f"Betroffene Originale:\n{listing}\n\n"
        "Zur Bearbeitung öffnet sich eine Claude-Code-Sitzung in einem "
        "Terminal. Gegebenenfalls ist dafür ein Terminal-Programm auszuwählen.\n\n"
        "Jetzt lösen?"
    )
    if DRY_RUN:
        print(f"[dry-run] würde nach {len(pairs)} Konflikt(en) fragen:\n{listing}")
        return

    # Saved before the dialog opens, not with the rest of the pass at the end:
    # the dialog stays on screen for up to fifteen minutes, and a pass that
    # overlaps despite the run lock would otherwise read a state in which no
    # dialog had been shown -- and put a second window next to this one
    # (doku 3.2, 3.3).
    state.dialog_last_shown = _now()
    save_state(state)
    answer = ask_question("Claude-Sync: Konflikt", text, "Jetzt lösen",
                          "Später", DIALOG_TIMEOUT_SECONDS)
    if answer is Answer.FAILED:
        # Nothing was shown, so nothing was deferred: the stamp above stands,
        # and the short retry interval runs from the ATTEMPT (doku 3.3).
        state.dialog_failed = True
        return
    if answer is not Answer.YES:
        state.dialog_failed = False
        defer(state)
        return
    state.dialog_failed = False

    while True:
        outcome, terminal_cmd = detect_terminal(state)
        if terminal_cmd is not None:
            break
        # An outage of the display is not a deferral, wherever in the chain it
        # happens: nobody saw anything, so the short retry interval applies
        # (doku 3.3). Without this the half hour from 2.9 took hold, because
        # dialog_failed had already been cleared above.
        if outcome is Answer.FAILED:
            state.dialog_failed = True
            return
        retry = ask_question(
            "Claude-Sync: Terminal nötig",
            "Zur Bearbeitung des Konflikts wird ein Terminal für die "
            "Claude-Sitzung benötigt. Auswahl erneut versuchen?",
            "Erneut versuchen", "Abbrechen", DIALOG_TIMEOUT_SECONDS)
        if retry is Answer.FAILED:
            state.dialog_failed = True
            return
        if retry is not Answer.YES:
            # Also a deferral, and it can arrive up to three quarters of an
            # hour after the first question -- counted from here, not from then.
            defer(state)
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
    for candidate in syncthing_config_candidates():
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


def _backlog_clause(count: int) -> str:
    """The backlog wording, in one place.

    It appears in three notices -- next to open conflicts, next to a pause, and
    in the quiet form. Two copies of the same sentence are the kind of
    duplication that drifts apart (doku 2.4).

    What it counts is the incoming direction only: `needFiles` is what THIS
    machine lacks against the cluster's latest version. What we hold and the
    other side lacks would need a completion call per device, which 3.1 point 5
    turns down on purpose. Named here because the pause sentence speaks of both
    directions while this number can only vouch for one (doku 1.8).
    """
    return f"{CLAUSE_BREAK}Rückstand: {count} Datei(en)" if count else ""


def build_notice(state: WatchState, open_conflicts: int,
                 watch_dir: Path) -> Optional[tuple[str, int]]:
    """Assemble the hourly notice as text plus display time, or None.

    Four cases ask for attention and get the long display time: open conflicts,
    a hand-set pause, no connection at all, and a backlog. Everything else is
    the sign of life and may be brief (doku 1.8).
    """
    api_key = read_api_key()
    figures = _sync_figures(state, api_key, watch_dir) if api_key else None

    # Deliberately before the figures are needed: with conflicts open, a clear
    # pointer replaces the statistics so a postponed resolution does not fade
    # from view -- and it must appear even when the interface says nothing.
    if open_conflicts:
        # From the START of the episode, not from the last sighting: the
        # sighting is refreshed by every pass while the conflict is open, and
        # passes run at least every fifteen minutes -- the span could therefore
        # only ever read "0 Stunde(n)", which turns a reminder into the report
        # of a fresh find (doku 1.8). Without the field, no span at all: an
        # older state file must not be made to claim zero.
        since = ""
        if state.conflict_since:
            hours = _hours_since(state.conflict_since)
            since = f" seit {hours} Stunde(n)"
        # Both a pause and a backlog change what the user has to do, so both
        # are named alongside the conflict instead of waiting for a quiet hour
        # that may not come while conflicts are open (doku 1.8).
        extra = ""
        if figures and figures["paused"]:
            extra += PAUSE_CLAUSE_SHORT
        if figures:
            extra += _backlog_clause(figures["backlog"])
        return (f"{open_conflicts} Konflikt(e){since} ungelöst{extra}",
                NOTICE_SECONDS_ATTENTION)

    if figures is None:
        return None

    if figures["paused"]:
        # Before the connection check on purpose: a hand-set pause explains the
        # silence better than its symptom, and it is the user's own doing.
        # The backlog comes along, as it does next to a conflict: a pause does
        # not make the number less relevant, and a backlog DURING a pause is
        # the expected case (doku 1.8).
        return (PAUSE_SENTENCE + _backlog_clause(figures["backlog"]),
                NOTICE_SECONDS_ATTENTION)

    if not figures["connected"]:
        since = ""
        if state.last_connected:
            hours = _hours_since(state.last_connected)
            since = f" seit {hours} Stunde(n)"
        return (f"keine Verbindung zum Abgleich{since}",
                NOTICE_SECONDS_ATTENTION)

    # Without a reference point, naming a span would be a lie. One sentence
    # covers both ways of lacking it -- a discarded state file (3.2) and a
    # fresh installation that has never seen a conflict. From the outside the
    # two are indistinguishable, and it is true of both.
    if state.last_conflict_seen:
        hours = _hours_since(state.last_conflict_seen)
        quiet = f"{CLAUSE_BREAK}kein Konflikt seit {hours} Stunde(n)"
    else:
        quiet = CLAUSE_BREAK + "Zählung neu begonnen"

    if figures["comparable"]:
        text = (f"abgeglichen: {_human_bytes(figures['outgoing'])} hoch, "
                f"{_human_bytes(figures['incoming'])} herunter{quiet}")
    else:
        # A sentence instead of zeroes. "0 B hoch, 0 B herunter" would stand for
        # three different situations at once -- a quiet hour, a lost reference
        # point, and a sync that has really stalled -- and the third is the one
        # this notice exists for (doku 1.8). The wording holds for both ways of
        # losing the reference: a reconnect and a first pass. The prefix stays
        # on purpose; it is what makes the hourly notice recognisable.
        text = ("abgeglichen: Zähler neu gesetzt — Bytes erst in der nächsten "
                f"Meldung{quiet}")
    if figures["backlog"]:
        return (text + _backlog_clause(figures["backlog"]),
                NOTICE_SECONDS_ATTENTION)
    return (text, NOTICE_SECONDS_QUIET)


def _human_bytes(count: float) -> str:
    """Byte count in a form a notice can show.

    Switches one tenth into the next unit instead of at its full value
    (doku 1.8): more than 0.1 kB reads as kB, more than 0.1 MB as MB. The
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
    the notice needs `paused` from the same answer (doku 1.8). Compares
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
    # All or nothing: the sum is only trustworthy if EVERY known device
    # contributed a delta. One device without a reference point makes the sum
    # incomplete, and an incomplete number that looks plausible is worse than a
    # sentence naming the situation (doku 1.8). A disconnected device does not
    # spoil this: its startedAt is empty now as it was then, so it matches.
    comparable = True
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
        else:
            # Either the connection was re-established -- every reconnect
            # restarts Syncthing's counters at zero -- or this is the first pass
            # ever. Either way this device's traffic is missing from the sum.
            comparable = False
    state.transfer_baseline = baseline
    if connected:
        state.last_connected = _now()

    backlog = 0
    paused = False
    folder = folder_config_for(watch_dir, api_key)
    if folder:
        # A pause the user set by hand stops the sync without anything looking
        # broken -- exactly the case the notice exists for (doku 1.8). Read,
        # never written: the watcher does not steer Syncthing (2.1).
        paused = bool(folder.get("paused"))
        status = rest_get(f"/rest/db/status?folder={folder.get('id')}", api_key)
        if isinstance(status, dict):
            backlog = int(status.get("needFiles") or 0)

    return {"connected": connected, "incoming": incoming, "outgoing": outgoing,
            "backlog": backlog, "paused": paused, "comparable": comparable}


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
    # Stamped for the ATTEMPT, not for the success -- and before anything can
    # go wrong. Two reasons, both learned the hard way (doku 2.6): a line in
    # the except branch below would otherwise appear at the pace of file
    # events, because an unstamped notice stays due for ever. And build_notice
    # legitimately returns None when no conflict is open and no API key can be
    # read, so on a machine whose Syncthing configuration sits elsewhere the
    # hourly rhythm would never establish itself.
    state.notice_last_shown = _now()
    try:
        notice = build_notice(state, open_conflicts, watch_dir)
    except NotImplementedError as unsupported:
        # The documented refusal of the platform capsule (doku 2.4), not a
        # defect. Caught before the branch below on purpose: reported as a
        # programming error with a traceback it would be a lie -- and an
        # hourly one -- at the very place this pass made truthful.
        print(f"Betriebsmeldung auf dieser Plattform nicht bedient "
              f"({unsupported}); siehe 3.7.", file=sys.stderr, flush=True)
        return
    except Exception:
        # Everything the suppliers handle themselves -- unreachable interface,
        # missing key, oddly shaped answer -- already returns None (doku 3.1,
        # point 3). What arrives here is a programming error, and 2.6 has no
        # exception for those. With the traceback, because a report nobody can
        # locate is not a report.
        print("Betriebsmeldung fehlgeschlagen:\n"
              + traceback.format_exc().rstrip(), file=sys.stderr, flush=True)
        return
    if notice is None:
        return
    text, seconds = notice
    notify("Claude-Sync", text, seconds)


# ---------------------------------------------------------------------------
# One pass (doku 3.1, "Ablauf")
# ---------------------------------------------------------------------------

def run_pass(watch_dir: Path, reason: str) -> int:
    """Search, attribute, escalate if due, notify if due. Returns conflict count."""
    if not acquire_lock():
        return -1
    try:
        reap_finished_session()
        state = load_state()
        copies, problems = find_conflicts(watch_dir)
        pairs = pair_conflicts(copies)

        # Reported on the CHANGE, in both directions -- see the state field.
        if problems and not state.scan_incomplete:
            print(f"Suchlauf unvollständig, {len(problems)} Stelle(n) nicht "
                  f"lesbar: {problems[0]}", file=sys.stderr, flush=True)
        elif not problems and state.scan_incomplete:
            print("Suchlauf wieder vollständig.", file=sys.stderr, flush=True)
        state.scan_incomplete = bool(problems)

        if not state.session_running():
            # The state gets a way back. Without it the last pid stayed in the
            # file for ever and every pass kept asking the system about a number
            # that had long stopped meaning anything (doku 3.2).
            state.session_pid = None
            state.session_started = None

        # Three cases, not two: "found something", "found nothing", and "could
        # not look properly". The third one must leave the episode untouched --
        # ending it would make a blind watcher look like a resolved conflict,
        # and starting one would escalate a finding that does not exist.
        if pairs:
            state.last_conflict_seen = _now()
            was_active = state.conflict_active
            state.conflict_active = True
            if not was_active:
                # The episode's own clock, separate from the last sighting: the
                # notice says how long the conflict has been OPEN, and the
                # sighting is refreshed on every pass while it is (doku 1.8,
                # 3.2). Set on the transition only, so a restart during an open
                # episode does not put the clock back -- and so a state file
                # from an older version keeps it empty, which drops the span
                # instead of claiming zero.
                state.conflict_since = _now()
            if state.session_running():
                # The user is working on it right now -- no dialog (step 3).
                pass
            elif state.dialog_due() or not was_active:
                escalate(pairs, state, watch_dir)
        elif problems:
            pass
        else:
            # No finding on a complete search: the episode ends by itself. That
            # is the normal case when the conflict was resolved on another
            # machine and the resolution has arrived here (doku 1.6, 3.1 step 4).
            state.conflict_active = False
            state.conflict_since = None

        maybe_notify(state, len(pairs), watch_dir)
        # The only place a dry pass would write: the two other save_state calls
        # sit behind DRY_RUN exits that return earlier. One guard is therefore
        # enough, and adding more elsewhere would only suggest otherwise.
        # Without it a dry run against a real installation moved the live
        # service's state -- it would take away its next notice and shift the
        # episode -- while 3.8 worked around that by hand (doku 3.1, 3.2).
        if DRY_RUN:
            print("[dry-run] Zustand nicht geschrieben.", flush=True)
        else:
            save_state(state)
        # One line per pass that found something -- as a service this is the
        # only trace in the journal (doku 3.5). Silence on an empty finding is
        # deliberate: the safety scan runs every 15 minutes and would otherwise
        # fill the journal with "nothing".
        if pairs or DRY_RUN:
            print(f"[{reason}] {len(pairs)} Konflikt(e) in {watch_dir}",
                  flush=True)
        return len(pairs)
    finally:
        release_lock()


# ---------------------------------------------------------------------------
# Event-driven observation with a safety net (doku 3.1)
# ---------------------------------------------------------------------------

def guarded_pass(watch_dir: Path, reason: str) -> None:
    """Run a pass so its failure cannot take the observation with it.

    The event handlers run in the watchdog observer's thread. An exception
    escaping one of them kills that thread: the watcher then survives on the
    safety scan alone, every event goes unnoticed, and nobody learns of it
    except through a traceback nobody reads (doku 3.1). The same holds for the
    start-up scan and the safety scan, which run in the service's main thread
    -- an exception there ends the service and, with RestartSec=30, restarts it
    every thirty seconds (doku 3.5).

    Swallowed silently would be worse than the crash, so the traceback goes to
    the journal (doku 2.6). ``--once`` deliberately does NOT use this: a hand
    run has to fail loudly, with a traceback and a return code.
    """
    try:
        run_pass(watch_dir, reason)
    except Exception:
        print(f"Durchgang '{reason}' mit einem Fehler abgebrochen; "
              "der Waechter laeuft weiter:", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.stderr.flush()


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
        print("Die Python-Beobachtungsbibliothek 'watchdog' fehlt.\n"
              "Bitte über die Distribution installieren (zum Beispiel: "
              "sudo apt install python3-watchdog) und den Dienst erneut "
              "starten.", file=sys.stderr)
        # Not exit 1: a missing library is structural. With RestartSec=30 the
        # start-rate limit never triggers (five starts in ten seconds is the
        # default), so exit 1 looped every thirty seconds forever and the unit
        # never reached "failed" (doku 3.5).
        return EXIT_PRECONDITION

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
                guarded_pass(watch_dir, "Ereignis: angelegt")

        def on_moved(self, event: Any) -> None:
            if self._relevant(event):
                guarded_pass(watch_dir, "Ereignis: verschoben")

        def on_deleted(self, event: Any) -> None:
            # A copy that disappears ends the episode. Without this the state
            # would keep saying "unresolved" until the next safety scan -- up
            # to fifteen minutes -- and with a watcher on both machines the
            # copy vanishing because it was resolved elsewhere is the normal
            # case, not an edge one (doku 3.1, step 1).
            if self._relevant(event):
                guarded_pass(watch_dir, "Ereignis: gelöscht")

    guarded_pass(watch_dir, "Startlauf")

    observer = Observer()
    observer.schedule(ConflictHandler(), str(watch_dir), recursive=True)
    observer.start()
    try:
        # The monotonic clock, not the wall clock: this interval outlives no
        # process, so it is the ONE place where a full fix is possible. It is
        # immune to every clock jump -- a daylight-saving change, an NTP
        # correction -- where a persisted timestamp can only be made exact
        # against the first of those (doku 3.1, 3.2).
        last_safety = time.monotonic()
        while True:
            time.sleep(30)
            if time.monotonic() - last_safety >= SAFETY_SCAN_INTERVAL.total_seconds():
                guarded_pass(watch_dir, "Sicherheitslauf")
                last_safety = time.monotonic()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def check_folder(watch_dir: Path) -> int:
    """Report whether Syncthing has *watch_dir* as a folder. Three outcomes.

    Exists because `install_service.sh` promised more than it checked: it
    tested that a directory is there, while 3.5 assured that the directory is
    *configured*. The difference is the silent failure the whole checklist is
    meant to prevent -- a watcher on a machine whose ~/.claude is not synced
    runs flawlessly, finds nothing ever, and reports no backlog precisely
    because it finds no folder.

    Deliberately here and not reimplemented in the shell script: the check
    needs the platform-dependent configuration location, the key, the REST
    call and the path comparison that tolerates "~/.claude" instead of an
    absolute path -- all of it already present. A second implementation would
    violate 2.4, and the Windows counterpart (3.7) would need a third.

    **Read-only by contract** (doku 3.5): no run lock, no state file, no tool
    directory. A refused lock would be read as "not configured" by the caller,
    which would be a wrong verdict drawn from a coincidence of timing; and a
    state write would overwrite the state of a pass running at the same moment.

    Returns 0 when the folder is configured, 1 when it is not, and 2 when that
    could not be determined -- the caller must keep those apart, because only
    the middle one is a finding.
    """
    api_key = read_api_key()
    if not api_key:
        print("Freigabe nicht prüfbar: Syncthings API-Schlüssel ist nicht "
              "lesbar.", file=sys.stderr)
        return 2
    folder = folder_config_for(watch_dir, api_key)
    if folder is None:
        if rest_get("/rest/system/config", api_key) is None:
            print("Freigabe nicht prüfbar: Syncthings Schnittstelle antwortet "
                  "nicht.", file=sys.stderr)
            return 2
        print(f"Syncthing kennt keine Freigabe für {watch_dir} — der Ordner "
              "wird nicht abgeglichen.", file=sys.stderr)
        return 1
    paused = " (angehalten)" if folder.get("paused") else ""
    print(f"Freigabe gefunden: {folder.get('id')}{paused}.")
    return 0


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
    parser.add_argument("--check-folder", action="store_true",
                        help="report whether Syncthing has the watched "
                             "directory as a folder, then exit")
    args = parser.parse_args(argv)

    DRY_RUN = args.dry_run
    if args.tool_dir:
        set_tool_dir(Path(args.tool_dir).expanduser())
    watch_dir = Path(args.watch_dir).expanduser()

    # Answered before the directory check below and before anything that
    # writes: this switch is read-only by contract (doku 3.5).
    if args.check_folder:
        return check_folder(watch_dir)

    if not watch_dir.is_dir():
        print(f"Überwachungsordner existiert nicht: {watch_dir}", file=sys.stderr)
        return 1

    if args.once:
        count = run_pass(watch_dir, "Einzellauf")
        if count < 0:
            print("Ein anderer Durchgang läuft gerade; nichts getan.",
                  file=sys.stderr)
            return 1
        return 0

    return watch_forever(watch_dir)


if __name__ == "__main__":
    sys.exit(main())
