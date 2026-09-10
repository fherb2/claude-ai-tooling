"""English message catalogue for the conflict watcher.

Same keys as the German catalogue, same order, same placeholders -- the check
script pins both properties, so a half-translated catalogue is a failing test
rather than a surprise in operation.

What is translated here are the **decisions**, not the words. Three of them are
easy to lose:

* "Affected originals" has to say *originals*. The line above it counts the
  copies, and without the heading the names read as the copies' names, which
  they are not (doku 1.8, 3.3).
* The two pause wordings stay two entries: a short clause where a conflict
  already carries the message, a full sentence where the pause IS the message
  and its consequence has to be spelt out (doku 1.8).
* "synced:" is the fixed prefix that makes the hourly notice recognisable, in
  the same way "abgeglichen:" does in German (doku 1.8).

Plurals keep the house trick, "hour(s)" instead of a plural engine. Where an
English plural is irregular the noun is chosen so the trick still works:
"conflict file(s)" rather than "conflict copy(-ies)".
"""

TEXTS = {

    # ------------------------------------------------------------------
    # Handover to the Claude session
    # ------------------------------------------------------------------
    "handover.text": (
        "Syncthing has created conflict copies, in the folder {dir} — that is "
        "where to look and nowhere else.\n"
        "Affected originals:\n"
        "{listing}\n\n"
        "Please search for *.sync-conflict-* yourself and work through them "
        "following the working instruction you were given as a system prompt."
    ),

    # ------------------------------------------------------------------
    # Dialogs (zenity) -- everything that asks for a decision (doku 2.9)
    # ------------------------------------------------------------------
    "dialog.conflict.title": "Claude-Sync: conflict",
    "dialog.conflict.text": (
        "Syncthing has created {count} conflict file(s).\n\n"
        "Affected originals:\n{listing}\n\n"
        "A Claude Code session will open in a terminal to work through them. "
        "You may have to pick a terminal program for that.\n\n"
        "Resolve now?"
    ),
    "dialog.conflict.ok": "Resolve now",
    "dialog.conflict.later": "Later",

    "dialog.terminal_pick.title": "Claude-Sync: pick a terminal",
    "dialog.terminal_pick.text": (
        "Several terminal emulators found. Which one should the conflict "
        "session use?"
    ),
    "dialog.terminal_pick.column": "Terminal",

    "dialog.terminal_entry.title": "Claude-Sync: terminal emulator",
    "dialog.terminal_entry.text": (
        "No known terminal emulator found. Please enter a command:"
    ),

    "dialog.terminal_retry.title": "Claude-Sync: a terminal is needed",
    "dialog.terminal_retry.text": (
        "Working through the conflict needs a terminal for the Claude "
        "session. Try the selection again?"
    ),
    "dialog.terminal_retry.ok": "Try again",
    "dialog.terminal_retry.cancel": "Cancel",

    "dialog.terminal_unusable.title": "Claude-Sync: terminal command unusable",
    "dialog.terminal_unusable.text": (
        "The command you entered, “{entered}”, cannot be used — its first "
        "word has to be a program that exists. Examples: “konsole” or "
        "“urxvt -hold”."
    ),

    "dialog.no_instruction.title": "Claude-Sync: cannot resolve the conflict",
    "dialog.no_instruction.text": (
        "The working instruction {path} is missing. Without it no conflict "
        "session can start. Please copy the complete contents of the files/ "
        "folder from the claude-sync-watch repository source to "
        "~/.claude-sync-watch. The missing file '{name}' is in there as well."
    ),

    "dialog.terminal_failed.title": "Claude-Sync: the terminal did not start",
    "dialog.terminal_failed.text": (
        "The terminal command “{command}” could not be run. The conflict "
        "copies stay where they are; the watcher will report again. Details "
        "are in the journal: journalctl --user -u claude-sync-watch"
    ),

    # ------------------------------------------------------------------
    # Hourly notice (notify-send) -- doku 1.8
    # ------------------------------------------------------------------
    "notify.summary": "Claude-Sync",
    "notify.synced": "synced: {up} up, {down} down",
    "notify.counter_reset": (
        "synced: counters reset — byte figures from the next notice on"
    ),
    "notify.quiet_since": "no conflict for {hours} hour(s)",
    "notify.count_restarted": "counting started afresh",
    "notify.conflicts_open": "{count} conflict(s){since} unresolved{extra}",
    "notify.since_hours": " for {hours} hour(s)",
    "notify.no_connection": "no connection to the sync{since}",
    "notify.backlog": "backlog: {count} file(s)",

    "notify.paused_short": "sync paused",
    "notify.paused_sentence": (
        "Sync paused for this folder — changes and conflict copies stay where "
        "they are"
    ),

    # ------------------------------------------------------------------
    # Journal (doku 2.5, 2.6)
    # ------------------------------------------------------------------
    # "Event:" is the common prefix that makes the file events searchable, the
    # way "Ereignis:" does in German (doku 3.5).
    "journal.reason.created": "Event: created",
    "journal.reason.moved": "Event: moved",
    "journal.reason.deleted": "Event: deleted",
    "journal.reason.startup": "Startup pass",
    "journal.reason.safety": "Safety pass",
    "journal.reason.single": "Single pass",

    "journal.pass_conflicts": "[{reason}] {count} conflict(s) in {dir}",
    "journal.pass_failed": (
        "Pass '{reason}' ended with an error; the watcher keeps running:"
    ),
    "journal.pass_busy": "Another pass is running; nothing done.",

    "journal.scan_incomplete": (
        "Scan incomplete, {count} place(s) unreadable: {first}"
    ),
    "journal.scan_complete": "Scan complete again.",
    "journal.watch_dir_missing": "The watched directory does not exist: {dir}",
    "journal.watch_dir_unusable": "{dir}: missing or not a directory",

    "journal.lock_stale": (
        "Run lock {whose} was a leftover (age {seconds} s) and was removed."
    ),
    "journal.lock_holder_pid": "of PID {pid}",
    "journal.lock_holder_unknown": "without a readable PID",
    "journal.lock_foreign": (
        "The run lock belongs to PID {pid}, not to this pass — not removed."
    ),

    "journal.notify_failed": "'notify-send' exited with code {code}: {detail}",
    "journal.notify_no_detail": "without a message",
    "journal.zenity_reported": "zenity reported (exit code {code}): {detail}",
    "journal.dialog_timeout": "The dialog closed itself unanswered.",
    "journal.dialog_failed": (
        "The dialog could not be shown -- that does not count as deferred."
    ),
    "journal.terminal_launch_failed": (
        "Terminal launch failed ({command}): {error}"
    ),
    "journal.terminal_entry_unusable": (
        "The terminal command entered is not usable: {entered}"
    ),
    "journal.no_instruction": (
        "Working instruction missing: {path} — no session started."
    ),
    "journal.notice_unsupported": (
        "The hourly notice is not served on this platform ({detail}); "
        "see 3.7."
    ),
    "journal.notice_failed": "The hourly notice failed:",

    # ------------------------------------------------------------------
    # Missing tools and structural refusals
    # ------------------------------------------------------------------
    "error.zenity_question": "No dialog possible: 'zenity' is not installed.",
    "error.zenity_message": "No message possible: 'zenity' is not installed.",
    "error.zenity_pick": "No selection possible: 'zenity' is not installed.",
    "error.zenity_entry": "No entry possible: 'zenity' is not installed.",
    "error.notify_missing": (
        "'notify-send' is missing — the hourly notice cannot appear on "
        "screen. Please install 'libnotify-bin': sudo apt install "
        "libnotify-bin. Conflict detection and escalation are unaffected."
    ),
    "error.watchdog_missing": (
        "The Python watch library 'watchdog' is missing.\n"
        "Please install it through the distribution (for example: "
        "sudo apt install python3-watchdog) and start the service again."
    ),
    "error.platform_unsupported": (
        "{what} is not implemented for Windows yet "
        "(implementation-doc.md, 3.7)."
    ),

    # ------------------------------------------------------------------
    # --check-folder (doku 3.1, 3.5)
    # ------------------------------------------------------------------
    "check.no_api_key": (
        "Cannot check the folder: Syncthing's API key is not readable."
    ),
    "check.no_answer": (
        "Cannot check the folder: Syncthing's interface does not answer."
    ),
    "check.no_folder": (
        "Syncthing knows no folder for {dir} — it is not being synced."
    ),
    "check.found": "Folder found: {id}{paused}.",
    "check.paused_suffix": " (paused)",

    # ------------------------------------------------------------------
    # Dry run (doku 3.1, "Die Schalter der Kommandozeile")
    # ------------------------------------------------------------------
    "dryrun.notify": "[dry-run] notice ({seconds}s): {summary} -- {body}",
    "dryrun.would_start": "[dry-run] would start:",
    "dryrun.would_ask": (
        "[dry-run] would ask about {count} conflict(s):\n{listing}"
    ),
    "dryrun.state_unwritten": "[dry-run] state not written.",

    # ------------------------------------------------------------------
    # Conflict pair description
    # ------------------------------------------------------------------
    "conflict.device_marker": " (device id {device})",
}
