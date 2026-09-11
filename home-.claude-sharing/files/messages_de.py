"""German message catalogue for the conflict watcher.

One dictionary, keys grouped by output channel -- the same order the
documentation uses (2.6 for output discipline, 2.9 for the graphical
interaction). A package carries exactly one catalogue; which one is installed
decides the language, so nothing has to be configured (doku 3.1).

Placeholders are named and resolved with ``str.format``. Plurals stay with the
house trick "Stunde(n)" instead of a plural engine: it keeps the number of keys
down, and the parenthesis is already the established style (doku 1.8).

The separator between a notice's main part and an appended clause is NOT in
here. It is a layout decision, not a language one, and lives as CLAUSE_BREAK in
the watcher (doku 1.8) -- the entries below carry the clause text alone.
"""

TEXTS = {

    # ------------------------------------------------------------------
    # Handover to the Claude session
    # ------------------------------------------------------------------
    # This text and the working instruction decide which language the session
    # speaks to the user. It is the reason the catalogue exists at all: a
    # German instruction makes the session ask a German question, whoever is
    # sitting there (doku 3.3, 3.4).
    "handover.text": (
        "Syncthing hat Konfliktkopien angelegt, im Ordner {dir} — genau dort "
        "und nirgends sonst ist zu suchen.\n"
        "Betroffene Originale:\n"
        "{listing}\n\n"
        "Bitte suche selbst nach *.sync-conflict-* und arbeite nach der "
        "Arbeitsanweisung, die dir als System-Prompt mitgegeben wurde."
    ),

    # ------------------------------------------------------------------
    # Dialogs (zenity) -- everything that asks for a decision (doku 2.9)
    # ------------------------------------------------------------------
    # "Betroffene Originale" is load-bearing: the line above names the number
    # of COPIES, and without the heading the names read as the copies' names,
    # which they are not (doku 1.8, 3.3).
    "dialog.conflict.title": "Claude-Sync: Konflikt",
    "dialog.conflict.text": (
        "Syncthing hat {count} Konfliktkopie(n) angelegt.\n\n"
        "Betroffene Originale:\n{listing}\n\n"
        "Zur Bearbeitung öffnet sich eine Claude-Code-Sitzung in einem "
        "Terminal. Gegebenenfalls ist dafür ein Terminal-Programm "
        "auszuwählen.\n\n"
        "Jetzt lösen?"
    ),
    "dialog.conflict.ok": "Jetzt lösen",
    "dialog.conflict.later": "Später",

    "dialog.terminal_pick.title": "Claude-Sync: Terminal wählen",
    "dialog.terminal_pick.text": (
        "Mehrere Terminal-Emulatoren gefunden. Welcher soll für die "
        "Konfliktsitzung verwendet werden?"
    ),
    "dialog.terminal_pick.column": "Terminal",

    "dialog.terminal_entry.title": "Claude-Sync: Terminal-Emulator",
    "dialog.terminal_entry.text": (
        "Kein bekannter Terminal-Emulator gefunden. Bitte Befehl angeben:"
    ),

    "dialog.terminal_retry.title": "Claude-Sync: Terminal nötig",
    "dialog.terminal_retry.text": (
        "Zur Bearbeitung des Konflikts wird ein Terminal für die "
        "Claude-Sitzung benötigt. Auswahl erneut versuchen?"
    ),
    "dialog.terminal_retry.ok": "Erneut versuchen",
    "dialog.terminal_retry.cancel": "Abbrechen",

    "dialog.terminal_unusable.title": "Claude-Sync: Terminal-Befehl unbrauchbar",
    "dialog.terminal_unusable.text": (
        "Der eingegebene Befehl „{entered}“ lässt sich nicht verwenden — das "
        "erste Wort muss ein vorhandenes Programm sein. Beispiele: „konsole“ "
        "oder „urxvt -hold“."
    ),

    # The file name is a placeholder and not written out: it carries a language
    # suffix, and a name in the text would have to be changed in two places.
    "dialog.no_instruction.title": "Claude-Sync: Konfliktlösung nicht möglich",
    "dialog.no_instruction.text": (
        "Die Arbeitsanweisung {path} fehlt. Ohne sie kann keine "
        "Konfliktsitzung starten. Bitte den Inhalt des files/-Ordner aus der "
        "Repo-Quelle von claude-sync-watch vollständig nach "
        "~/.claude-sync-watch kopieren. Dort ist auch das fehlende File "
        "'{name}' enthalten."
    ),

    "dialog.terminal_failed.title": "Claude-Sync: Terminal konnte nicht starten",
    "dialog.terminal_failed.text": (
        "Der Terminalbefehl „{command}“ ließ sich nicht ausführen. Die "
        "Konfliktkopien bleiben liegen; der Wächter meldet sich wieder. "
        "Einzelheiten stehen im Journal: "
        "journalctl --user -u claude-sync-watch"
    ),

    # ------------------------------------------------------------------
    # Hourly notice (notify-send) -- doku 1.8
    # ------------------------------------------------------------------
    "notify.summary": "Claude-Sync",
    # The prefix "abgeglichen:" stays even where it grates grammatically: it is
    # what makes the hourly notice recognisable (doku 1.8).
    "notify.synced": "abgeglichen: {up} hoch, {down} herunter",
    "notify.counter_reset": (
        "abgeglichen: Zähler neu gesetzt — Bytes erst in der nächsten Meldung"
    ),
    "notify.quiet_since": "kein Konflikt seit {hours} Stunde(n)",
    # No invented zero where the reference point is missing -- one sentence
    # covers a discarded state file and a fresh installation alike (doku 1.8).
    "notify.count_restarted": "Zählung neu begonnen",
    "notify.conflicts_open": "{count} Konflikt(e){since} ungelöst{extra}",
    "notify.since_hours": " seit {hours} Stunde(n)",
    "notify.no_connection": "keine Verbindung zum Abgleich{since}",
    "notify.backlog": "Rückstand: {count} Datei(en)",

    # Two wordings, and both are a decision about what the user is told, not a
    # formulation: the short clause where a conflict already carries the
    # message, the full sentence where the pause IS the message and its
    # consequence has to be named. They stay two entries side by side so that
    # changing one and forgetting the other shows up in the diff (doku 1.8).
    "notify.paused_short": "Abgleich angehalten",
    "notify.paused_sentence": (
        "Abgleich für diesen Ordner angehalten — Änderungen und "
        "Konfliktkopien bleiben liegen"
    ),

    # ------------------------------------------------------------------
    # Journal (doku 2.5, 2.6)
    # ------------------------------------------------------------------
    # The reasons are named so they can be searched for: everything with the
    # "Ereignis:" prefix is a file event. Translating the prefix keeps that
    # property only if it stays a common prefix (doku 3.5).
    "journal.reason.created": "Ereignis: angelegt",
    "journal.reason.moved": "Ereignis: verschoben",
    "journal.reason.deleted": "Ereignis: gelöscht",
    "journal.reason.startup": "Startlauf",
    "journal.reason.safety": "Sicherheitslauf",
    "journal.reason.single": "Einzellauf",

    "journal.pass_conflicts": "[{reason}] {count} Konflikt(e) in {dir}",
    "journal.pass_failed": (
        "Durchgang '{reason}' mit einem Fehler abgebrochen; der Wächter läuft "
        "weiter:"
    ),
    "journal.pass_busy": "Ein anderer Durchgang läuft gerade; nichts getan.",

    "journal.scan_incomplete": (
        "Suchlauf unvollständig, {count} Stelle(n) nicht lesbar: {first}"
    ),
    "journal.scan_complete": "Suchlauf wieder vollständig.",
    "journal.watch_dir_missing": "Überwachungsordner existiert nicht: {dir}",
    "journal.watch_dir_unusable": "{dir}: nicht vorhanden oder kein Verzeichnis",

    "journal.lock_stale": (
        "Laufsperre {whose} war ein Überrest (Alter {seconds} s) und wurde "
        "entfernt."
    ),
    "journal.lock_holder_pid": "von PID {pid}",
    "journal.lock_holder_unknown": "ohne lesbare PID",
    "journal.lock_foreign": (
        "Laufsperre gehört PID {pid}, nicht diesem Durchgang — nicht entfernt."
    ),

    "journal.notify_failed": (
        "'notify-send' endete mit Rückgabewert {code}: {detail}"
    ),
    "journal.notify_no_detail": "ohne Meldung",
    "journal.zenity_reported": "zenity meldete (Rückgabewert {code}): {detail}",
    "journal.dialog_timeout": "Dialog lief ohne Antwort ab.",
    "journal.dialog_failed": (
        "Dialog konnte nicht gezeigt werden -- das gilt nicht als vertagt."
    ),
    "journal.terminal_launch_failed": (
        "Terminalstart fehlgeschlagen ({command}): {error}"
    ),
    "journal.terminal_entry_unusable": (
        "Eingegebener Terminal-Befehl nicht verwendbar: {entered}"
    ),
    "journal.no_instruction": (
        "Arbeitsanweisung fehlt: {path} — keine Sitzung gestartet."
    ),
    "journal.notice_unsupported": (
        "Betriebsmeldung auf dieser Plattform nicht bedient ({detail}); "
        "siehe 3.7."
    ),
    "journal.notice_failed": "Betriebsmeldung fehlgeschlagen:",

    # ------------------------------------------------------------------
    # Missing tools and structural refusals
    # ------------------------------------------------------------------
    "error.zenity_question": "Dialog nicht möglich: 'zenity' ist nicht installiert.",
    "error.zenity_message": "Meldung nicht möglich: 'zenity' ist nicht installiert.",
    "error.zenity_pick": "Auswahl nicht möglich: 'zenity' ist nicht installiert.",
    "error.zenity_entry": "Eingabe nicht möglich: 'zenity' ist nicht installiert.",
    # Reported once per run, never hourly, and without the notice text itself:
    # that would quietly become a third channel where 2.6 promises two.
    "error.notify_missing": (
        "'notify-send' fehlt — die stündliche Betriebsmeldung kann nicht am "
        "Bildschirm erscheinen. Bitte 'libnotify-bin' installieren: "
        "sudo apt install libnotify-bin. Konflikterkennung und Eskalation "
        "sind unberührt."
    ),
    "error.watch_setup_failed": (
        "Die Verzeichnisbeobachtung lässt sich nicht einrichten: {detail}\n"
        "Häufigste Ursache ist das inotify-Kontingent "
        "(fs.inotify.max_user_watches); die rekursive Beobachtung belegt je "
        "Verzeichnis unterhalb des beobachteten Ordners einen Eintrag."
    ),
    "error.watchdog_missing": (
        "Die Python-Beobachtungsbibliothek 'watchdog' fehlt.\n"
        "Bitte über die Distribution installieren (zum Beispiel: "
        "sudo apt install python3-watchdog) und den Dienst erneut starten."
    ),
    # {what} is the name of the platform capsule and stays English: it names a
    # place in the code, not a thing for the user (doku 2.4).
    "error.platform_unsupported": (
        "{what} wird unter Windows noch nicht bedient "
        "(implementation-doc.md, 3.7)."
    ),

    # ------------------------------------------------------------------
    # --check-folder (doku 3.1, 3.5)
    # ------------------------------------------------------------------
    "check.no_api_key": (
        "Freigabe nicht prüfbar: Syncthings API-Schlüssel ist nicht lesbar."
    ),
    "check.no_answer": (
        "Freigabe nicht prüfbar: Syncthings Schnittstelle antwortet nicht."
    ),
    "check.no_folder": (
        "Syncthing kennt keine Freigabe für {dir} — der Ordner wird nicht "
        "abgeglichen."
    ),
    "check.found": "Freigabe gefunden: {id}{paused}.",
    "check.paused_suffix": " (angehalten)",

    # ------------------------------------------------------------------
    # Dry run (doku 3.1, "Die Schalter der Kommandozeile")
    # ------------------------------------------------------------------
    "dryrun.notify": "[dry-run] Meldung ({seconds}s): {summary} -- {body}",
    "dryrun.would_start": "[dry-run] würde starten:",
    "dryrun.would_ask": (
        "[dry-run] würde nach {count} Konflikt(en) fragen:\n{listing}"
    ),
    "dryrun.state_unwritten": "[dry-run] Zustand nicht geschrieben.",

    # ------------------------------------------------------------------
    # Conflict pair description
    # ------------------------------------------------------------------
    # Names the device id and never a direction: "from" would claim an origin
    # the name cannot carry (doku 3.1, step 2).
    "conflict.device_marker": " (Gerätekennung {device})",
}
