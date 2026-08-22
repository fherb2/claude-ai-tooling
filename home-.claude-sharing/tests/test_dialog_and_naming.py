#!/usr/bin/env python3
"""test_dialog_and_naming.py -- automatic regression check for the places in
claude_sync_watchd.py where a wrong assumption stays invisible: how a dialog
result is classified, how a conflict copy's name is taken apart, which files
are skipped while Syncthing is still receiving them, and what the hourly
notice says and for how long.

Usage:
    /usr/bin/python3 test_dialog_and_naming.py

Prints one line per case and exits with 1 on the first deviation, so it can
also be used as a gate before a commit. Needs no display, no zenity, no
Syncthing and no network: zenity and the REST interface are replaced by stubs,
and the names are fixed strings. Runs in well under a second.

The interpreter matters: use /usr/bin/python3, the one the service starts. A
virtualenv in the shell's PATH is a different interpreter and would check
something other than what runs (doku 3.8).

WHY THIS EXISTS -- every check guards against a specific, already-made error:

1. Dialog classification. Zenity exits with 1 both when the user cancels AND
   when it cannot open a display (measured, doku 3.3). A watcher that exists
   only to escalate must not read the second as "user postponed", or a broken
   desktop turns into silence. The distinction therefore rests on the error
   message, which is not a guaranteed interface -- exactly the kind of thing a
   later refactoring simplifies away in good faith. The case "cancelled, but
   the toolkit chattered on stderr anyway" is in here because that is how a
   naive "stderr means failure" rule breaks.

2. Name derivation. The device id in a conflict name belongs to one of the two
   devices in no dependable role, and the copy travels to every device under
   the name it was given once (doku 3.1, step 2). The check therefore pins the
   ONE real name observed so far, plus names with spaces and extra dots, and
   pins that describe() states the id without claiming a direction -- the very
   claim that had to be removed from three places.

3. Transfer temporaries. A copy in transit carries the marker inside a
   temporary name, and the watcher reported a pair whose original never
   existed. The doku had claimed the opposite, two paragraphs above its own
   refutation (doku 3.1, step 1).

4. The notice. Its display time now depends on what it says, and the wording
   must not claim a span it cannot know. Pinned here: the unit thresholds,
   which cases count as "asking for attention", and the one case where the
   notice is not decoration -- an open conflict is reported even when the REST
   interface says nothing at all (doku 1.8).

This file deliberately does not test the escalation as a whole, the episode
rule or the terminal launch: those need a screen and a human, and the
manual probes next to this file cover them (doku 3.8).
"""

import contextlib
import datetime
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

DAEMON = Path(__file__).resolve().parent.parent / "files" / "claude_sync_watchd.py"
UNIT = Path(__file__).resolve().parent.parent / "files" / "claude-sync-watch.service"
UNINSTALL = Path(__file__).resolve().parent.parent / "files" / "uninstall_service.sh"

failures = 0


def check(label: str, got: object, expected: object) -> None:
    """Report one case; remember deviations instead of aborting at the first."""
    global failures
    ok = got == expected
    if not ok:
        failures += 1
    print(f"  {'ok    ' if ok else 'FEHLER'} {label:34} -> {got!r}"
          + ("" if ok else f"   erwartet: {expected!r}"))


def load_daemon() -> types.ModuleType:
    """Import the daemon by path, without installing it anywhere.

    Registering it in sys.modules is not optional: dataclasses resolves type
    annotations through the module entry and fails with an AttributeError
    without it.
    """
    spec = importlib.util.spec_from_file_location("claude_sync_watchd", DAEMON)
    module = importlib.util.module_from_spec(spec)
    sys.modules["claude_sync_watchd"] = module
    spec.loader.exec_module(module)
    return module


def check_dialog_answers(w: types.ModuleType) -> None:
    """Classification of every zenity outcome the daemon can meet."""
    print("Dialog-Einordnung (zenity durch Attrappe ersetzt):")
    cases = [
        ("Zustimmung", 0, b"", w.Answer.YES),
        ("Abbruch oder Fenster zu", 1, b"", w.Answer.NO),
        ("Abbruch trotz GTK-Geschwätz", 1,
         b"Gtk-Message: Failed to load module 'canberra-gtk-module'",
         w.Answer.NO),
        ("keine Anzeige erreichbar", 1,
         b"(zenity:1): Gtk-WARNING **: Failed to open display", w.Answer.FAILED),
        ("keine Anzeige, andere Wortwahl", 1,
         b"cannot open display: :99", w.Answer.FAILED),
        # Self-closed after DIALOG_TIMEOUT_SECONDS: nobody was there, which is
        # a deferral, not a defect (measured exit code, doku 3.3).
        ("Zeitablauf ohne Antwort", 5, b"", w.Answer.NO),
        ("Zeitablauf mit GTK-Geschwätz", 5,
         b"Gtk-WARNING **: Unknown key gtk-modules", w.Answer.NO),
        ("sonstiger Fehler", 255, b"boom", w.Answer.FAILED),
    ]
    original = w.subprocess.run
    try:
        for label, code, stderr, expected in cases:
            w.subprocess.run = (
                lambda *a, _code=code, _err=stderr, **k:
                types.SimpleNamespace(returncode=_code, stderr=_err))
            check(label, w.ask_question("T", "t", "ja", "nein"), expected)
    finally:
        w.subprocess.run = original

    # A missing zenity must not look like a decision either.
    def absent(*args, **kwargs):
        raise FileNotFoundError("zenity")

    w.subprocess.run = absent
    try:
        check("zenity nicht installiert",
              w.ask_question("T", "t", "ja", "nein"), w.Answer.FAILED)
    finally:
        w.subprocess.run = original


def check_timeout_unit(w: types.ModuleType) -> None:
    """The timeout must be a plain number of seconds, not a duration string.

    Measured: zenity rejects "15m" with exit code 255, which the daemon reads
    as a failure -- every dialog would count as broken (doku 3.8).
    """
    print("Zeitangabe des Dialogs:")
    check("in Sekunden, als Zahl",
          isinstance(w.DIALOG_TIMEOUT_SECONDS, int), True)
    passed = {}
    original = w.subprocess.run

    def spy(command, *args, **kwargs):
        passed["command"] = command
        return types.SimpleNamespace(returncode=1, stderr=b"")

    w.subprocess.run = spy
    try:
        w.ask_question("T", "t", "ja", "nein", w.DIALOG_TIMEOUT_SECONDS)
    finally:
        w.subprocess.run = original
    check("wird als --timeout=<Zahl> übergeben",
          f"--timeout={w.DIALOG_TIMEOUT_SECONDS}" in passed.get("command", []),
          True)

    w.subprocess.run = spy
    try:
        w.ask_question("T", "t", "ja", "nein")
    finally:
        w.subprocess.run = original
    check("ohne Angabe kein --timeout",
          any(str(a).startswith("--timeout")
              for a in passed.get("command", [])), False)


def check_terminal_dialogs(w: types.ModuleType) -> None:
    """Selection and text dialog: a timeout counts as a cancellation.

    Why this is here: both run inside a pass. An unanswered window would hold
    the run lock, and a held lock makes the watcher deaf to everything else --
    no further pass, no notice, no end of episode (doku 3.3). The case hits a
    fresh installation, a vanished emulator and every additional machine,
    because only an empty cache leads to these dialogs at all.
    """
    print("Terminal-Dialoge (Auswahl und Freitext):")
    original = w.subprocess.run
    spied = {}

    def make_run(code, stdout_text=""):
        def fake_run(command, *a, **k):
            spied["command"] = command
            return types.SimpleNamespace(returncode=code, stdout=stdout_text,
                                         stderr="")
        return fake_run

    try:
        w.subprocess.run = make_run(5)          # timed out
        check("Auswahl: Zeitablauf wie Abbruch",
              w.pick_from_list("T", "t", "S", ["konsole", "xterm"],
                               w.DIALOG_TIMEOUT_SECONDS), (w.Answer.NO, None))
        check("Auswahl: Zeitangabe uebergeben",
              f"--timeout={w.DIALOG_TIMEOUT_SECONDS}" in spied["command"], True)

        w.subprocess.run = make_run(1)          # cancelled
        check("Auswahl: Abbruch bleibt Abbruch",
              w.pick_from_list("T", "t", "S", ["konsole"],
                               w.DIALOG_TIMEOUT_SECONDS), (w.Answer.NO, None))

        w.subprocess.run = make_run(0, "konsole\n")
        check("Auswahl: Wahl kommt durch",
              w.pick_from_list("T", "t", "S", ["konsole"],
                               w.DIALOG_TIMEOUT_SECONDS), (w.Answer.YES, "konsole"))

        w.subprocess.run = make_run(5)
        check("Freitext: Zeitablauf wie Abbruch",
              w.ask_text("T", "t", w.DIALOG_TIMEOUT_SECONDS), (w.Answer.NO, None))
        check("Freitext: Zeitangabe uebergeben",
              f"--timeout={w.DIALOG_TIMEOUT_SECONDS}" in spied["command"], True)

        w.subprocess.run = make_run(0, " urxvt \n")
        check("Freitext: Eingabe kommt bereinigt",
              w.ask_text("T", "t", w.DIALOG_TIMEOUT_SECONDS), (w.Answer.YES, "urxvt"))

        # Without a value no --timeout may be passed: the pre-study scripts
        # call both functions without one.
        w.subprocess.run = make_run(1)
        w.pick_from_list("T", "t", "S", ["konsole"])
        check("Auswahl: ohne Angabe kein --timeout",
              any(str(x).startswith("--timeout") for x in spied["command"]), False)
    finally:
        w.subprocess.run = original

    # And the escalation chain really has to pass the value on.
    daemon_source = DAEMON.read_text(encoding="utf-8")
    snippet = daemon_source[daemon_source.index("def detect_terminal"):daemon_source.index("def build_handover")]
    check("detect_terminal gibt sie beim Auswahldialog mit",
          "DIALOG_TIMEOUT_SECONDS" in snippet.split("pick_from_list")[1][:400], True)
    check("detect_terminal gibt sie bei der Freitexteingabe mit",
          "DIALOG_TIMEOUT_SECONDS" in snippet.split("ask_text")[1][:400], True)


def check_terminal_duplicates(w: types.ModuleType, tmp_root: Path) -> None:
    """One line per program, and the flag has to follow the program (doku 3.3).

    Real files and a real symlink instead of a patched resolve(): the whole
    point is that the link and its target are the same program on disk, and a
    stubbed resolver would only test the stub. Only ``which`` is stubbed, so
    the test does not depend on which emulators this machine happens to have.
    """
    print("Terminal-Entdoppelung:")
    binaries = tmp_root / "bin"
    binaries.mkdir(parents=True, exist_ok=True)
    (binaries / "konsole").write_text("#!/bin/sh\n", encoding="utf-8")
    (binaries / "gnome-terminal").write_text("#!/bin/sh\n", encoding="utf-8")
    (binaries / "xterm").write_text("#!/bin/sh\n", encoding="utf-8")
    link = binaries / "x-terminal-emulator"
    original_which = w.shutil.which

    def present(*names: str):
        """Let only these names exist, x-terminal-emulator via the link."""
        w.shutil.which = lambda binary: (str(binaries / binary)
                                         if binary in names else None)

    try:
        # Der Fall dieses Rechners: drei Funde, zwei Programme.
        link.unlink(missing_ok=True)
        link.symlink_to(binaries / "konsole")
        present("x-terminal-emulator", "konsole", "xterm")
        found = w._distinct_terminals(w.terminal_candidates())
        check("Doppeleintrag verschwindet", [b for b, _ in found],
              ["konsole", "xterm"])

        # Und die Regel, warum konsole gewinnt: der Schalter gehört zum
        # Programm. Zeigt der Link auf gnome-terminal, wäre -e falsch.
        link.unlink()
        link.symlink_to(binaries / "gnome-terminal")
        present("x-terminal-emulator", "gnome-terminal")
        found = w._distinct_terminals(w.terminal_candidates())
        check("der konkrete Name gewinnt samt seinem Schalter", found,
              [("gnome-terminal", "--")])
        check("und aus zwei Funden wird einer -- kein Dialog mehr",
              len(found), 1)

        # Zeigt der Link auf etwas, das wir nicht kennen, bleibt er stehen:
        # dort ist er der beste Griff, den wir haben.
        (binaries / "terminator").write_text("#!/bin/sh\n", encoding="utf-8")
        link.unlink()
        link.symlink_to(binaries / "terminator")
        present("x-terminal-emulator")
        check("unbekanntes Ziel: die Alternative bleibt",
              w._distinct_terminals(w.terminal_candidates()),
              [("x-terminal-emulator", "-e")])

        # Und der Beweis, dass die Kaskade die Entdoppelung wirklich benutzt.
        # Ohne ihn prüfen die Fälle oben nur eine Funktion, die niemand ruft --
        # eine Leerprobe an detect_terminal bliebe dann stumm (beobachtet).
        original_pick = w.pick_from_list
        angeboten: list[list[str]] = []
        try:
            link.unlink()
            link.symlink_to(binaries / "konsole")
            present("x-terminal-emulator", "konsole", "xterm")

            def spy(title, text, label, options, timeout=None):
                angeboten.append(list(options))
                return w.Answer.YES, "konsole"

            w.pick_from_list = spy
            outcome, cmd = w.detect_terminal(w.WatchState())
            check("der Auswahldialog bekommt die entdoppelte Liste",
                  angeboten, [["konsole", "xterm"]])
            check("und liefert den gewählten Befehl", cmd, ["konsole", "-e"])
        finally:
            w.pick_from_list = original_pick
    finally:
        w.shutil.which = original_which


def check_dialog_timing(w: types.ModuleType) -> None:
    """The two waiting times, and that a failure uses the shorter one."""
    print("Wartezeiten (2.9 und die Fehler-Ausnahme aus 3.3):")

    def ago(minutes):
        return (datetime.datetime.now()
                - datetime.timedelta(minutes=minutes)).isoformat()

    cases = [
        ("noch nie gezeigt", False, None, True),
        ("vertagt, 6 Minuten her", False, 6, False),
        ("vertagt, 31 Minuten her", False, 31, True),
        ("gescheitert, 2 Minuten her", True, 2, False),
        ("gescheitert, 6 Minuten her", True, 6, True),
        ("unlesbarer Zeitstempel", False, "kaputt", True),
    ]
    for label, failed, minutes, expected in cases:
        shown = (minutes if isinstance(minutes, str)
                 else None if minutes is None else ago(minutes))
        state = w.WatchState(dialog_failed=failed, dialog_last_shown=shown)
        check(label, state.dialog_due(), expected)


def check_naming(w: types.ModuleType) -> None:
    """Name derivation, pinned to the one real name observed so far."""
    print("Namensableitung:")
    cases = [
        # The single real Syncthing name seen to date (doku 3.8). If a future
        # Syncthing changes the format, this is where it shows.
        ("Konflikttest.sync-conflict-20260811-175245-3PDLNDG.txt",
         "Konflikttest.txt", "3PDLNDG"),
        # A space in the stem and a further dot in the suffix.
        ("mein notiz.v2.sync-conflict-20260811-120000-ABCDEFG.txt",
         "mein notiz.v2.txt", "ABCDEFG"),
        # No suffix at all.
        ("README.sync-conflict-20260811-120000-ABCDEFG",
         "README", "ABCDEFG"),
    ]
    for name, expected_original, expected_device in cases:
        pairs = w.pair_conflicts([Path("/nirgends") / name])
        if not pairs:
            check(f"{name[:28]}…", None, expected_original)
            continue
        check(f"Original aus {name[:20]}…", pairs[0].original.name,
              expected_original)
        check(f"Kennung aus {name[:20]}…", pairs[0].device, expected_device)

    # An unparsable name must still be reported, just without a device id.
    pairs = w.pair_conflicts([Path("/nirgends/kaputt.sync-conflict-xyz.txt")])
    check("unparsbarer Name gemeldet", len(pairs), 1)
    if pairs:
        check("unparsbarer Name ohne Kennung", pairs[0].device, "")

    # The line shown to the user must not claim a direction ("from", "von").
    line = w.ConflictPair(copy=Path("/x/a.sync-conflict-1-2-DEV.txt"),
                          original=Path("/x/a.txt"), device="DEV").describe()
    check("Anzeige nennt die Kennung", "DEV" in line, True)
    check("Anzeige behauptet keine Herkunft",
          any(word in line.lower() for word in (" from ", "(from", " von ")),
          False)


def check_transfer_temporaries(w: types.ModuleType, tmp_root: Path) -> None:
    """Files still being received must not be reported as findings.

    The trap this guards: Syncthing writes an incoming file under a temporary
    name that EMBEDS the target name, so a conflict copy in transit carries
    the marker inside it -- and since copies travel to every device, that is
    the normal case. Before the filter existed, the watcher reported a pair
    whose original had never existed (doku 3.1, step 1, and 3.8).
    """
    print("Zwischendateien beim Empfang:")
    check("Linux-Form erkannt", w.is_transfer_temporary(
        ".syncthing.a.sync-conflict-20260811-120000-DEV.txt.tmp"), True)
    check("Windows-Form erkannt", w.is_transfer_temporary(
        "~syncthing~a.sync-conflict-20260811-120000-DEV.txt.tmp"), True)
    check("fertige Kopie nicht erkannt", w.is_transfer_temporary(
        "a.sync-conflict-20260811-120000-DEV.txt"), False)
    # A .tmp of the user's own making is not Syncthing's -- and a name that
    # merely starts like one but has been moved into place is not either.
    check("eigene .tmp-Datei nicht erkannt", w.is_transfer_temporary(
        "a.sync-conflict-20260811-120000-DEV.tmp"), False)
    check("Vorsilbe ohne .tmp nicht erkannt", w.is_transfer_temporary(
        ".syncthing.a.sync-conflict-20260811-120000-DEV.txt"), False)

    folder = tmp_root / "empfang"
    folder.mkdir(parents=True, exist_ok=True)
    for name in (
            "Notiz.txt",
            "Notiz.sync-conflict-20260811-120000-DEV.txt",
            ".syncthing.Notiz.sync-conflict-20260811-120000-DEV.txt.tmp",
            "~syncthing~Andere.sync-conflict-20260811-120000-DEV.txt.tmp"):
        (folder / name).write_text("x", encoding="utf-8")
    found_paths, problems_found = w.find_conflicts(folder)
    found = [p.name for p in found_paths]
    check("vollständiger Suchlauf meldet kein Problem", problems_found, [])
    check("nur die fertige Kopie gefunden", found,
          ["Notiz.sync-conflict-20260811-120000-DEV.txt"])
    for entry in folder.iterdir():
        entry.unlink()
    folder.rmdir()


def check_notice(w: types.ModuleType, tmp_root: Path) -> None:
    """Figures, wording and display time of the hourly notice (doku 1.8).

    Syncthing is replaced by a stub, so this runs without a running daemon.
    What it pins: the unit thresholds, which cases count as "asking for
    attention", and that the conflict notice appears even when the interface
    says nothing at all -- the one case where the notice is not decoration.
    """
    print("Meldung: Zahlen, Wortlaut, Anzeigedauer:")
    for count, expected in ((0, "0 B"), (99, "99 B"), (150, "0.1 kB"),
                            (50 * 1024, "50.0 kB"), (150 * 1024, "0.1 MB"),
                            (5 * 1024 ** 2, "5.0 MB"), (2 * 1024 ** 3, "2.0 GB")):
        check(f"{count} B liest sich als", w._human_bytes(count), expected)

    folder = tmp_root / "freigabe"
    folder.mkdir(parents=True, exist_ok=True)
    original_key, original_get = w.read_api_key, w.rest_get

    def stub(connected: bool = True, need: int = 0, key: object = "k",
             paused: bool = False, started: str = "t",
             totals: tuple[int, int] = (0, 0)) -> None:
        w.read_api_key = lambda: key

        def get(path: str, api_key: str) -> object:
            if path.startswith("/rest/system/connections"):
                return {"connections": {"DEV": {
                    "connected": connected, "startedAt": started,
                    "inBytesTotal": totals[0], "outBytesTotal": totals[1]}}}
            if path.startswith("/rest/system/config"):
                return {"folders": [{"id": "F", "path": str(folder),
                                     "paused": paused}]}
            if path.startswith("/rest/db/status"):
                return {"needFiles": need}
            return None

        w.rest_get = get

    # The reference point is seeded by default and matches the stub's startedAt.
    # Without it every call would land in the "counters were reset" branch and
    # the checks below would quietly stop testing the normal case -- which is
    # exactly what happened before that branch existed: the figures were never
    # anything but zero, and no check noticed.
    def state(seen: object = "2026-08-01T00:00:00",
              baseline: object = None) -> object:
        if baseline is None:
            baseline = {"DEV": {"in": 0, "out": 0, "startedAt": "t"}}
        return w.WatchState(last_conflict_seen=seen,
                            last_connected="2026-08-01T00:00:00",
                            transfer_baseline=baseline)

    try:
        stub()
        text, seconds = w.build_notice(state(), 0, folder)
        check("Normalfall kurz", seconds, w.NOTICE_SECONDS_QUIET)
        check("Normalfall nennt die Frist", "kein Konflikt seit" in text, True)

        text, seconds = w.build_notice(state(seen=None), 0, folder)
        check("ohne Bezugspunkt keine Frist",
              "Zählung neu begonnen" in text and "seit" not in text, True)

        # The first check ever to look at the byte figures themselves. Until now
        # the stub returned constant totals, so the delta was always zero and
        # "0 B hoch, 0 B herunter" passed for a working computation.
        stub(totals=(2200, 1100))
        text, seconds = w.build_notice(state(), 0, folder)
        check("Bytes erscheinen bei gültigem Bezug",
              f"{w._human_bytes(1100)} hoch" in text
              and f"{w._human_bytes(2200)} herunter" in text, True)
        check("gültiger Bezug ohne Ersatzsatz",
              "Zähler neu gesetzt" in text, False)

        # Every reconnect restarts Syncthing's counters, so a delta across it
        # would be meaningless. The notice says that instead of showing zeroes,
        # which would look like a stalled sync (doku 1.8).
        stub(started="t2", totals=(2200, 1100))
        text, seconds = w.build_notice(state(), 0, folder)
        check("nach Neuverbindung ein Satz statt Nullen",
              "Zähler neu gesetzt" in text and "0 B" not in text, True)
        check("der Satz darf kurz stehen", seconds, w.NOTICE_SECONDS_QUIET)

        # First pass ever: no reference point at all. Same truth, same wording.
        stub(totals=(2200, 1100))
        text, _ = w.build_notice(state(baseline={}), 0, folder)
        check("frische Installation, derselbe Satz",
              "Zähler neu gesetzt" in text, True)

        # The backlog is a stock figure, not a delta -- untouched by a reconnect,
        # and it keeps its longer display time.
        stub(started="t2", need=3)
        text, seconds = w.build_notice(state(), 0, folder)
        check("Rückstand steht neben dem Satz",
              "Zähler neu gesetzt" in text
              and "Rückstand: 3 Datei(en)" in text, True)
        check("Rückstand verlängert auch hier", seconds,
              w.NOTICE_SECONDS_ATTENTION)

        stub(need=7)
        text, seconds = w.build_notice(state(), 0, folder)
        check("Rückstand verlängert", seconds, w.NOTICE_SECONDS_ATTENTION)
        check("Rückstand wird genannt", "Rückstand: 7 Datei(en)" in text, True)

        stub(connected=False)
        text, seconds = w.build_notice(state(), 0, folder)
        check("keine Verbindung verlängert", seconds,
              w.NOTICE_SECONDS_ATTENTION)
        check("keine Verbindung wird genannt",
              text.startswith("keine Verbindung zum Abgleich"), True)

        stub()
        text, seconds = w.build_notice(state(), 3, folder)
        check("Konflikte verlängern", seconds, w.NOTICE_SECONDS_ATTENTION)
        check("Konfliktzahl wird genannt", "3 Konflikt(e)" in text, True)
        check("ohne Pause kein Zusatz", "angehalten" in text, False)

        # A hand-set pause stops the sync without anything looking broken --
        # the very case the notice exists for (doku 1.8).
        stub(paused=True)
        text, seconds = w.build_notice(state(), 0, folder)
        check("Pause verlängert", seconds, w.NOTICE_SECONDS_ATTENTION)
        check("Pause wird genannt", text.startswith("Abgleich für diesen "
                                                    "Ordner angehalten"), True)
        check("Pausenform ohne Rückstand nennt keinen",
              "Rückstand" in text, False)

        # A pause does not make the backlog less relevant, and a backlog DURING
        # a pause is the expected case (doku 1.8). Without conflicts the pause
        # branch used to leave the function at once and drop the number.
        stub(need=5, paused=True)
        text, _ = w.build_notice(state(), 0, folder)
        check("Rückstand in der Pausenform",
              text.startswith("Abgleich für diesen Ordner angehalten")
              and text.endswith("; Rückstand: 5 Datei(en)"), True)

        # With conflicts open, pause and backlog are named alongside, not
        # instead: both change what the user has to do (doku 1.8).
        text, seconds = w.build_notice(state(), 2, folder)
        check("Pause neben Konflikten",
              "2 Konflikt(e)" in text and "Abgleich angehalten" in text, True)

        stub(need=4)
        text, _ = w.build_notice(state(), 2, folder)
        check("Rückstand neben Konflikten",
              "2 Konflikt(e)" in text and "Rückstand: 4 Datei(en)" in text, True)

        stub(need=4, paused=True)
        text, _ = w.build_notice(state(), 2, folder)
        check("Pause und Rückstand zugleich",
              all(chunk in text for chunk in ("2 Konflikt(e)", "angehalten",
                                            "Rückstand: 4 Datei(en)")), True)

        # Same wording in all three notices -- one source, no drift (doku 2.4).
        stub(need=4)
        quiet_text, _ = w.build_notice(state(), 0, folder)
        conflict_text, _ = w.build_notice(state(), 2, folder)
        stub(need=4, paused=True)
        paused_text, _ = w.build_notice(state(), 0, folder)
        clause_text = "; Rückstand: 4 Datei(en)"
        check("Rückstands-Wortlaut in drei Formen identisch",
              all(form.endswith(clause_text)
                  for form in (quiet_text, conflict_text, paused_text)), True)

        # Two deliberate forms, not one: an appended half-sentence where a
        # conflict already carries the message, a full sentence where the pause
        # IS the message (doku 3.1, point 4).
        check("zwei Pausenfassungen, nicht eine",
              w.PAUSE_CLAUSE_SHORT != w.PAUSE_SENTENCE
              and w.PAUSE_CLAUSE_SHORT.startswith("; ")
              and not w.PAUSE_SENTENCE.startswith(";"), True)

        # Both notices draw from the constants instead of carrying their own
        # literal: swapping the constants must swap the notices. Comparing the
        # text against the constant would not show that -- a branch with its own
        # copy of the same words would pass just as well.
        original_short = w.PAUSE_CLAUSE_SHORT
        original_sentence = w.PAUSE_SENTENCE
        w.PAUSE_CLAUSE_SHORT, w.PAUSE_SENTENCE = "; KURZ", "LANG"
        try:
            stub(paused=True)
            marked_quiet, _ = w.build_notice(state(), 0, folder)
            marked_conflict, _ = w.build_notice(state(), 2, folder)
        finally:
            w.PAUSE_CLAUSE_SHORT = original_short
            w.PAUSE_SENTENCE = original_sentence
        check("lange Pausenfassung kommt aus der Konstante",
              marked_quiet.startswith("LANG"), True)
        check("kurze Pausenfassung kommt aus der Konstante",
              marked_conflict.endswith("; KURZ"), True)

        # A paused DEVICE is a different case and needs no own wording: it
        # shows up as no connection (verified against the real configuration,
        # doku 1.8).
        stub(paused=False, connected=False)
        text, _ = w.build_notice(state(), 0, folder)
        check("angehaltenes Gerät heißt: keine Verbindung",
              text.startswith("keine Verbindung"), True)

        # The one case where the notice is not decoration: without the
        # interface there are no figures, but an open conflict must still be
        # reported (doku 1.8).
        stub(key=None)
        check("ohne REST keine Zahlenmeldung",
              w.build_notice(state(), 0, folder), None)
        notice = w.build_notice(state(), 2, folder)
        check("ohne REST trotzdem Konfliktmeldung",
              notice is not None and "2 Konflikt(e)" in notice[0], True)
    finally:
        w.read_api_key, w.rest_get = original_key, original_get
    folder.rmdir()


def check_swallowed_errors(w: types.ModuleType, tmp_root: Path) -> None:
    """Nothing that fails may fail quietly (doku 2.6).

    Four places had thrown their evidence away. Each of them is invisible when
    wrong -- that is the whole reason they stayed broken: a watcher whose
    reports vanish looks exactly like a watcher with nothing to report.
    """
    print("Verschluckte Fehler (2.6):")
    original = w.subprocess.run

    def capture(call, *args) -> str:
        """Run *call* and return what it wrote to the journal."""
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            call(*args)
        return buffer.getvalue()

    # --- The classification is the same for all three windows -------------
    outcome_cases = [
        ("Zustimmung", 0, "", w.Answer.YES),
        ("Abbruch", 1, "", w.Answer.NO),
        ("Zeitablauf", 5, "", w.Answer.NO),
        ("keine Anzeige", 1, "cannot open display: :99", w.Answer.FAILED),
        ("sonstiger Fehler", 255, "boom", w.Answer.FAILED),
    ]
    for label, code, err, want in outcome_cases:
        w.subprocess.run = (lambda *a, _c=code, _e=err, **k:
                            types.SimpleNamespace(returncode=_c, stdout="x\n",
                                                  stderr=_e))
        try:
            check(f"Auswahl: {label}",
                  w.pick_from_list("T", "t", "S", ["konsole"])[0], want)
            check(f"Freitext: {label}", w.ask_text("T", "t")[0], want)
        finally:
            w.subprocess.run = original

    # A non-empty error output reaches the journal, however it is classified.
    w.subprocess.run = (lambda *a, **k: types.SimpleNamespace(
        returncode=0, stdout="konsole\n", stderr="Gtk-WARNING: irgendwas"))
    try:
        journal_text = capture(lambda: w.pick_from_list("T", "t", "S", ["k"]))
    finally:
        w.subprocess.run = original
    check("Auswahl: Fehlerausgabe landet im Journal",
          "Gtk-WARNING" in journal_text, True)

    def fehlt(*args, **kwargs):
        raise FileNotFoundError("zenity")

    w.subprocess.run = fehlt
    try:
        check("Auswahl ohne zenity: nicht gezeigt, nicht abgebrochen",
              w.pick_from_list("T", "t", "S", ["k"])[0], w.Answer.FAILED)
        check("Freitext ohne zenity: nicht gezeigt, nicht abgebrochen",
              w.ask_text("T", "t")[0], w.Answer.FAILED)
    finally:
        w.subprocess.run = original

    # --- notify-send: Rückgabewert auswerten, Text draußen lassen ----------
    w.subprocess.run = (lambda *a, **k: types.SimpleNamespace(
        returncode=1, stdout=b"", stderr=b"kein Benachrichtigungsdienst"))
    try:
        journal_text = capture(w.notify, "Claude-Sync", "abgeglichen: 1 kB", 5)
    finally:
        w.subprocess.run = original
    check("notify-send: Rückgabewert wird gemeldet",
          "Rückgabewert 1" in journal_text, True)
    check("notify-send: Fehlertext wird gemeldet",
          "Benachrichtigungsdienst" in journal_text, True)
    check("notify-send: Meldungstext bleibt draußen",
          "abgeglichen" in journal_text, False)

    # --- maybe_notify: report the programming error AND stamp the time -----
    original_build = w.build_notice

    def kaputt(*args, **kwargs):
        raise KeyError("backlog")

    probe_state = w.WatchState()
    w.build_notice = kaputt
    try:
        journal_text = capture(w.maybe_notify, probe_state, 0, tmp_root)
    finally:
        w.build_notice = original_build
    check("Ausnahme in der Meldung wird gemeldet",
          "Betriebsmeldung fehlgeschlagen" in journal_text, True)
    check("mit Rückverfolgung", "KeyError" in journal_text, True)
    # Without the stamp the notice would stay due and the line would arrive
    # at the pace of file events -- the very flood 2.6 rules out.
    check("und trotzdem gestempelt", probe_state.notice_last_shown is not None, True)

    silent_state = w.WatchState()
    w.build_notice = lambda *a, **k: None
    try:
        w.maybe_notify(silent_state, 0, tmp_root)
    finally:
        w.build_notice = original_build
    check("auch ein reguläres Nichts stempelt",
          silent_state.notice_last_shown is not None, True)

    # --- The outcome has to reach the waiting time ------------------------
    # The heart of finding 3: if the display fails only AFTER the first
    # question, dialog_failed had already been cleared -- the half hour took
    # hold instead of the short retry, and the user had seen nothing (3.3).
    original_detect = w.detect_terminal
    original_dir = w.TOOL_DIR
    w.set_tool_dir(tmp_root / "eskalation")
    sample_pair = w.ConflictPair(copy=tmp_root / "a.sync-conflict-x.txt",
                          original=tmp_root / "a.txt", device="DEV")
    try:
        w.subprocess.run = (lambda *a, **k: types.SimpleNamespace(
            returncode=0, stdout=b"", stderr=b""))          # erste Frage: ja
        w.detect_terminal = lambda state: (w.Answer.FAILED, None)
        probe_state = w.WatchState()
        capture(w.escalate, [sample_pair], probe_state, tmp_root)
        check("Anzeigeausfall in der Strecke setzt dialog_failed",
              probe_state.dialog_failed, True)
        check("und damit gilt die kurze Wiederholung",
              probe_state.dialog_due(), False)   # the five minutes are not up
    finally:
        w.detect_terminal = original_detect
        w.subprocess.run = original
        w.set_tool_dir(original_dir)

    # --- The retry loop is unbounded on purpose (3.3) ----------------------
    # Every round takes a deliberate click, and a cap would lock out the very
    # user who is sitting there trying: the chain would end and 2.9 would hold
    # the next dialog back for half an hour. Pinned here so that capping the
    # loop later cannot slip through while the doku still calls it unbounded.
    original_ask = w.ask_question
    w.set_tool_dir(tmp_root / "runden")
    calls = {"detect": 0}
    answers = [w.Answer.YES,   # Jetzt lösen
               w.Answer.YES,   # Erneut versuchen
               w.Answer.YES,   # und noch einmal
               w.Answer.YES,   # und noch einmal
               w.Answer.NO]    # Abbrechen
    original_launch = w.launch_session
    try:
        def counting_detect(state: object) -> tuple[object, object]:
            calls["detect"] += 1
            return (w.Answer.NO, None)      # Auswahl abgebrochen, kein Ausfall

        w.detect_terminal = counting_detect
        # A guard, not decoration: the loop under test can only be left with a
        # command in hand, so this must never run. If someone ever caps the loop,
        # it falls out with terminal_cmd None -- and the real launch_session
        # would find no instruction file in this throwaway tool dir and put a
        # REAL zenity window on the screen for fifteen minutes. Observed while
        # running exactly that falsification.
        w.launch_session = lambda *a, **k: None
        w.ask_question = (lambda *a, **k:
                          answers.pop(0) if answers else w.Answer.NO)
        loop_state = w.WatchState()
        w.escalate([sample_pair], loop_state, tmp_root)
        check("jede Runde fragt erneut nach dem Terminal", calls["detect"], 4)
        check("Abbrechen beendet die Strecke", answers, [])
        check("die abgebrochene Runde gilt als Vertagung",
              loop_state.dialog_last_shown is not None, True)
    finally:
        w.ask_question = original_ask
        w.launch_session = original_launch
        w.detect_terminal = original_detect
        w.set_tool_dir(original_dir)

    # --- Platform-dependent data live inside the capsule (2.4) ------------
    # They have to be findable at the capsule's calls instead of sitting among
    # the constants at the top -- that is what 2.4's refusal to list them
    # rests on. Checked here: they refuse on an unsupported platform rather
    # than guessing.
    original_windows = w._is_windows
    w._is_windows = lambda: True
    try:
        for name in ("syncthing_config_candidates", "terminal_candidates",
                     "claude_binary", "_boot_time"):
            try:
                getattr(w, name)()
                did_refuse = False
            except NotImplementedError:
                did_refuse = True
            check(f"{name} verweigert auf fremder Plattform", did_refuse, True)
        # And the refusal must not look like a programming error: it would
        # otherwise reach the journal hourly, with a traceback.
        probe_state = w.WatchState()
        journal_text = capture(w.maybe_notify, probe_state, 0, tmp_root)
        check("nicht bediente Plattform ohne Rückverfolgung",
              "Traceback" in journal_text, False)
        check("und mit Verweis auf 3.7", "3.7" in journal_text, True)
    finally:
        w._is_windows = original_windows

    # --- find_conflicts: seeing nothing is not finding nothing ------------
    check("fehlender Ordner wird gemeldet",
          bool(w.find_conflicts(tmp_root / "gibtsnicht")[1]), True)
    blocked_dir = tmp_root / "gesperrt"
    (blocked_dir / "innen").mkdir(parents=True, exist_ok=True)
    os.chmod(blocked_dir / "innen", 0o000)
    try:
        _, problems_found = w.find_conflicts(blocked_dir)
        if os.geteuid() == 0:
            print("  übersprungen unlesbarer Unterordner (als root lesbar)")
        else:
            check("unlesbarer Unterordner wird gemeldet", bool(problems_found), True)
    finally:
        os.chmod(blocked_dir / "innen", 0o700)


def _dead_pid() -> int:
    """A pid that certainly no longer exists, and is fully reaped.

    Waited for on purpose: an abandoned child lingers as a zombie, and a zombie
    is exactly the case the daemon must NOT read as dead by number alone -- it
    would make this helper check something other than intended.
    """
    process = subprocess.Popen(["/bin/true"])
    process.wait()
    return process.pid


def _leave_a_zombie() -> int:
    """Start and abandon a child so it lingers unreaped, like the daemon's."""
    def spawn() -> int:
        process = subprocess.Popen(["/bin/true"], start_new_session=True)
        return process.pid          # object dropped on purpose, as in the daemon
    pid = spawn()
    time.sleep(0.3)
    return pid


def check_lock(w: types.ModuleType, tmp_root: Path) -> None:
    """The run lock belongs to its holder, not to a clock.

    The trap: a pass legitimately outlives any short age limit, because its
    dialogs stay open for fifteen minutes each and it holds the lock for the
    whole stretch. The old limit called anything older a crashed predecessor,
    so the next pass stole the lock mid-dialog, read the state from before the
    dialog and put a second window next to it (doku 3.2).
    """
    print("Laufsperre:")
    original_dir = w.TOOL_DIR
    w.set_tool_dir(tmp_root / "sperre")
    stranger = subprocess.Popen(["/bin/sleep", "30"])
    ancient = (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp()
    try:
        # A living holder keeps the lock however old the file is. The holder is
        # deliberately somebody else's pid: with our own, the release below
        # could not tell "mine" from "foreign" apart at all.
        w.LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        w.LOCK_FILE.write_text(f"pid {stranger.pid} 2000-01-01T00:00:00\n",
                               encoding="utf-8")
        os.utime(w.LOCK_FILE, (ancient, ancient))
        check("lebender Halter behält sie", w.acquire_lock(), False)
        check("fremde Sperre bleibt liegen",
              (w.release_lock(), w.LOCK_FILE.exists())[1], True)

        # A dead holder leaves a leftover, and that may go.
        w.LOCK_FILE.write_text(f"pid {_dead_pid()} 2000-01-01T00:00:00\n",
                               encoding="utf-8")
        os.utime(w.LOCK_FILE, (ancient, ancient))
        check("toter Halter gibt sie frei", w.acquire_lock(), True)
        check("eigene Sperre wird entfernt",
              (w.release_lock(), w.LOCK_FILE.exists())[1], False)

        # Unreadable holder: the age limit is the fallback, not a free pass.
        w.LOCK_FILE.write_text("ohne pid\n", encoding="utf-8")
        check("ohne PID entscheidet das Alter: frisch belegt",
              w.acquire_lock(), False)
        os.utime(w.LOCK_FILE, (ancient, ancient))
        check("ohne PID entscheidet das Alter: alt freigegeben",
              w.acquire_lock(), True)
        w.LOCK_FILE.unlink(missing_ok=True)
    finally:
        stranger.kill()
        stranger.wait()
        w.set_tool_dir(original_dir)


def check_session_detection(w: types.ModuleType) -> None:
    """A session counts as running only while it demonstrably is.

    Two lies the bare existence question cannot see, both measured: a terminal
    that ended without being collected lingers as a zombie and answers "yes",
    and a recycled number answers for a stranger. Past the quiet time the pid
    therefore has to prove itself by its start time -- which is what protects a
    session lasting longer than half an hour, the case the quiet time cannot
    cover (doku 3.1, step 3).
    """
    print("Sitzungserkennung:")
    now = datetime.datetime.now()
    long_ago = (now - datetime.timedelta(hours=3)).isoformat()
    recent = (now - datetime.timedelta(minutes=5)).isoformat()

    check("ohne Angaben nicht laufend", w.WatchState().session_running(), False)
    check("in der Ruhezeit laufend, ohne PID",
          w.WatchState(session_started=recent).session_running(), True)
    check("in der Ruhezeit laufend, PID tot",
          w.WatchState(session_pid=_dead_pid(),
                       session_started=recent).session_running(), True)
    check("nach der Ruhezeit ohne PID: beendet",
          w.WatchState(session_started=long_ago).session_running(), False)
    check("nach der Ruhezeit, PID tot: beendet",
          w.WatchState(session_pid=_dead_pid(),
                       session_started=long_ago).session_running(), False)
    # The reuse case: this process is alive, but it started long before the
    # session was recorded -- so the number does not belong to that session.
    check("nach der Ruhezeit, fremder Prozess: beendet",
          w.WatchState(session_pid=os.getpid(),
                       session_started=long_ago).session_running(), False)
    # The long session: alive, and started when we recorded it.
    own_start = w.process_running_since(os.getpid())
    check("Startzeit des eigenen Prozesses lesbar", own_start is not None, True)
    if own_start is not None:
        check("nach der Ruhezeit, passende Startzeit: laufend",
              w.WatchState(session_pid=os.getpid(),
                           session_started=own_start.isoformat()
                           ).session_running(), True)
    # A zombie answers os.kill with "exists"; the state letter gives it away.
    check("Zombie gilt als beendet",
          w.process_running_since(_leave_a_zombie()), None)


def check_episode_clock(w: types.ModuleType, tmp_root: Path) -> None:
    """The conflict hint counts from the start of the episode, not the sighting.

    One field served both spans, and they are opposites: the quiet form counts
    from the last sighting, which every pass refreshes while a conflict is open.
    Passes run at least every fifteen minutes, so the hint could only ever read
    "0 Stunde(n)" -- a reminder that reads like a fresh find and invites another
    deferral. The example in 1.8, "seit 9 Stunde(n) ungelöst", was unreachable
    (doku 1.8, 3.2).
    """
    print("Uhr der Episode:")
    now = datetime.datetime.now()
    long_open = (now - datetime.timedelta(hours=9, minutes=5)).isoformat()
    just_seen = (now - datetime.timedelta(minutes=3)).isoformat()
    original_key = w.read_api_key
    w.read_api_key = lambda: None            # keine echte Konfiguration lesen
    try:
        text, _ = w.build_notice(
            w.WatchState(conflict_since=long_open, last_conflict_seen=just_seen),
            3, tmp_root)
        check("Frist kommt aus dem Episodenbeginn", "seit 9 Stunde(n)" in text, True)
        # Der eigentliche Nachweis: die frische Sichtung darf sie nicht drücken.
        check("frische Sichtung ändert sie nicht", "0 Stunde(n)" in text, False)
        text, _ = w.build_notice(
            w.WatchState(last_conflict_seen=just_seen), 3, tmp_root)
        check("ohne Episodenbeginn keine Frist", "seit" in text, False)
    finally:
        w.read_api_key = original_key
    # Die Gegenrichtung: Die Ruheform zählt weiter ab der Sichtung und darf den
    # Episodenbeginn nicht heranziehen. Sie braucht Zahlen, also eine Attrappe.
    original_key, original_get = w.read_api_key, w.rest_get
    w.read_api_key = lambda: "k"
    w.rest_get = lambda path, api_key: (
        {"connections": {"DEV": {"connected": True, "startedAt": "t",
                                 "inBytesTotal": 0, "outBytesTotal": 0}}}
        if path.startswith("/rest/system/connections") else
        {"folders": [{"id": "F", "path": str(tmp_root), "paused": False}]}
        if path.startswith("/rest/system/config") else {"needBytes": 0})
    try:
        text, _ = w.build_notice(
            w.WatchState(last_conflict_seen=long_open,
                         conflict_since=just_seen), 0, tmp_root)
        check("Ruheform zählt ab der Sichtung", "seit 9 Stunde(n)" in text, True)
    finally:
        w.read_api_key, w.rest_get = original_key, original_get

    # Verhaltensprobe über zwei echte Durchgänge: Episode beginnt und endet.
    # Die Dialoge werden über eine Attrappe von `escalate` unterdrückt, NICHT
    # über DRY_RUN: Ein Trockendurchgang schreibt den Zustand nicht mehr
    # (doku 3.1), und dieser Fall prüft gerade, dass er geschrieben wird. Mit
    # DRY_RUN blieben zwei der drei Prüfungen grün, ohne etwas zu prüfen --
    # sie verglichen None mit None.
    original_dir, original_notify = w.TOOL_DIR, w.maybe_notify
    original_escalate = w.escalate
    w.set_tool_dir(tmp_root / "episode")
    w.maybe_notify = lambda *a, **k: None     # sonst liest der Durchgang REST
    w.escalate = lambda *a, **k: None         # kein Dialog, keine Sitzung
    watched = tmp_root / "beobachtet"
    watched.mkdir(parents=True, exist_ok=True)
    kopie = watched / "N.sync-conflict-20260814-120000-DEV.txt"
    try:
        (watched / "N.txt").write_text("x", encoding="utf-8")
        kopie.write_text("y", encoding="utf-8")
        w.run_pass(watched, "Prüfung")
        gesetzt = w.load_state().conflict_since
        check("Episodenbeginn beim ersten Fund gesetzt", gesetzt is not None, True)
        w.run_pass(watched, "Prüfung")
        check("zweiter Fund lässt ihn stehen",
              w.load_state().conflict_since, gesetzt)
        kopie.unlink()
        w.run_pass(watched, "Prüfung")
        check("Episodenende leert ihn",
              w.load_state().conflict_since, None)
    finally:
        w.escalate = original_escalate
        w.maybe_notify = original_notify
        w.set_tool_dir(original_dir)
        for entry in watched.iterdir():
            entry.unlink()
        watched.rmdir()


def check_dry_run(w: types.ModuleType, tmp_root: Path) -> None:
    """A dry pass leaves the state file alone (doku 3.1).

    It used to write it, so a dry run against a real installation took the live
    service's next notice away and could shift its episode. The counter-check
    matters as much as the check: without it this group would pass just as well
    if save_state had stopped working altogether.
    """
    print("Trockenmodus:")
    original_dir, original_notify = w.TOOL_DIR, w.maybe_notify
    original_escalate = w.escalate
    w.set_tool_dir(tmp_root / "trocken")
    w.maybe_notify = lambda *a, **k: None
    w.escalate = lambda *a, **k: None
    watched = tmp_root / "trocken-beobachtet"
    watched.mkdir(parents=True, exist_ok=True)
    kopie = watched / "T.sync-conflict-20260814-120000-DEV.txt"
    try:
        (watched / "T.txt").write_text("x", encoding="utf-8")
        kopie.write_text("y", encoding="utf-8")
        w.TOOL_DIR.mkdir(parents=True, exist_ok=True)
        w.save_state(w.WatchState())                  # ein Ausgangsstand
        vorher = w.STATE_FILE.read_bytes()

        w.DRY_RUN = True
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            w.run_pass(watched, "Trockenprobe")
        journal = buffer.getvalue()
        check("Trockenlauf lässt die Zustandsdatei unverändert",
              w.STATE_FILE.read_bytes() == vorher, True)
        check("und sagt es in der Ausgabe",
              "Zustand nicht geschrieben" in journal, True)
        w.DRY_RUN = False

        # Gegenprobe: Der reguläre Durchgang schreibt sehr wohl.
        w.run_pass(watched, "Vergleichslauf")
        check("der reguläre Durchgang schreibt",
              w.STATE_FILE.read_bytes() != vorher, True)
    finally:
        w.DRY_RUN = False
        w.escalate = original_escalate
        w.maybe_notify = original_notify
        w.set_tool_dir(original_dir)
        for entry in watched.iterdir():
            entry.unlink()
        watched.rmdir()


def check_precondition_exit(w: types.ModuleType, tmp_root: Path) -> None:
    """A structural precondition stops the service; a transient one retries.

    The pair only works if two files agree: the unit names an exit status, the
    daemon returns one. Nothing forces them together, so the invariant is
    pinned here -- it is exactly the kind that drifts in silence (doku 3.5).

    Why it matters: RestartSec=30 puts every restart far outside systemd's
    default start-rate limit of five starts in ten seconds, so a repeated
    exit 1 looped every thirty seconds and the unit never reached "failed".
    """
    print("Vorbedingungen und Neustart (3.5):")
    unit = UNIT.read_text(encoding="utf-8")
    named = [line.split("=", 1)[1].strip() for line in unit.splitlines()
             if line.startswith("RestartPreventExitStatus=")]
    check("die Unit nennt genau einen Ausstiegswert", len(named), 1)
    check("und er ist der des Waechters", named[0] if named else None,
          str(w.EXIT_PRECONDITION))
    check("RestartSec bleibt gesetzt -- der Grund fuer die Kopplung",
          any(line.strip() == "RestartSec=30" for line in unit.splitlines()),
          True)

    # Fehlende Bibliothek: strukturell, also 78 und kein Neustart.
    blocked = {"watchdog": None, "watchdog.events": None,
               "watchdog.observers": None}
    saved = {name: sys.modules.get(name) for name in blocked}
    watched = tmp_root / "vorbedingung"
    watched.mkdir(parents=True, exist_ok=True)
    try:
        sys.modules.update(blocked)
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            code = w.watch_forever(watched)
        check("fehlende Bibliothek liefert EX_CONFIG", code,
              w.EXIT_PRECONDITION)
        check("und sagt, was zu tun ist",
              "python3-watchdog" in buffer.getvalue(), True)
    finally:
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    # Gegenprobe: Der fehlende Ordner ist voruebergehend und behaelt seinen
    # Neustart -- Claude Code legt ihn beim ersten Lauf selbst an.
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        code = w.main(["--once", "--watch-dir", str(tmp_root / "gibtsnicht")])
    check("fehlender Ordner bleibt bei 1", code, 1)
    check("und ist damit vom Neustartverbot ausgenommen",
          code != w.EXIT_PRECONDITION, True)


def check_free_text_terminal(w: types.ModuleType, tmp_root: Path) -> None:
    """A hand-typed terminal command is checked before it is used (doku 3.3).

    It used to be taken as argv[0] unchanged, so "urxvt -hold" -- the entry a
    user naturally types -- became a program name with a space in it. Popen
    then raised, and the exception rose through the whole pass: in the observer
    thread it killed the observation, in the main thread the service.

    Only `which` is stubbed; the entries themselves are real strings, so the
    group does not depend on which emulators this machine has.
    """
    print("Freitext-Terminal (3.3):")
    binaries = tmp_root / "freitext-bin"
    binaries.mkdir(parents=True, exist_ok=True)
    (binaries / "konsole").write_text("#!/bin/sh\n", encoding="utf-8")
    original_which = w.shutil.which
    w.shutil.which = lambda binary: (str(binaries / binary)
                                     if binary == "konsole" else None)
    try:
        check("ein Wort bekommt den Schalter angehaengt",
              w._terminal_from_text("konsole"), ["konsole", "-e"])
        check("Mehrwort-Eingabe wird zerlegt, nicht verworfen",
              w._terminal_from_text("konsole -hold"),
              ["konsole", "-hold", "-e"])
        check("ein selbst getippter Schalter wird nicht verdoppelt",
              w._terminal_from_text("konsole -e"), ["konsole", "-e"])
        check("unbekanntes Programm wird abgelehnt",
              w._terminal_from_text("gibtsnicht"), None)
        check("unbalancierte Anfuehrungszeichen werfen nicht",
              w._terminal_from_text('kon"sole'), None)
        check("leere Eingabe wird abgelehnt", w._terminal_from_text("   "),
              None)

        # Und der Beweis, dass die Kaskade die Pruefung benutzt: kein Fund,
        # Freitext mit Tippfehler -> Antwort NO und keine Uebernahme.
        original_text, original_message = w.ask_text, w.show_message
        gemeldet: list[str] = []
        try:
            w.shutil.which = lambda binary: None      # gar kein Emulator
            w.ask_text = lambda *a, **k: (w.Answer.YES, "gibtsnicht")
            w.show_message = lambda title, text: gemeldet.append(title)
            state = w.WatchState()
            outcome, cmd = w.detect_terminal(state)
            check("Tippfehler wird nicht uebernommen", cmd, None)
            check("und gilt als Abbruch, nicht als Anzeigefehler",
                  outcome, w.Answer.NO)
            check("der Nutzer wird darauf hingewiesen", len(gemeldet), 1)
            check("und nichts wird zwischengespeichert",
                  state.terminal_cmd, None)
        finally:
            w.ask_text, w.show_message = original_text, original_message
    finally:
        w.shutil.which = original_which


def check_launch_failure(w: types.ModuleType, tmp_root: Path) -> None:
    """A terminal that cannot start is reported, not raised (doku 3.3, 2.6).

    The pass has to survive it, and the episode has to stay open so it reports
    itself again -- the same treatment a missing instruction file gets.
    """
    print("Fehlgeschlagener Terminalstart:")
    original_dir = w.TOOL_DIR
    original_popen = w.subprocess.Popen
    original_message = w.show_message
    w.set_tool_dir(tmp_root / "start")
    gemeldet: list[str] = []
    pair = w.ConflictPair(copy=tmp_root / "a.sync-conflict-x.txt",
                          original=tmp_root / "a.txt", device="DEV")
    try:
        w.TOOL_DIR.mkdir(parents=True, exist_ok=True)
        w.INSTRUCTION_FILE.write_text("egal", encoding="utf-8")

        def refusing(*args, **kwargs):
            raise OSError(2, "No such file or directory")

        w.subprocess.Popen = refusing
        w.show_message = lambda title, text: gemeldet.append(title)
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            pid = w.launch_session(["gibtsnicht", "-e"], [pair], tmp_root)
        check("kein Fehler nach oben, keine PID", pid, None)
        check("Journalzeile geschrieben",
              "Terminalstart fehlgeschlagen" in buffer.getvalue(), True)
        check("und der Nutzer erfaehrt es", len(gemeldet), 1)
    finally:
        w.subprocess.Popen = original_popen
        w.show_message = original_message
        w.set_tool_dir(original_dir)


def check_pass_guard(w: types.ModuleType, tmp_root: Path) -> None:
    """One failing pass must not take the observation with it (doku 3.1).

    Both halves are pinned: that the guard swallows and journals, and that the
    five places of continuous operation actually use it while --once does not.
    Without the second half the guard could sit there unused and every check
    above would still pass.
    """
    print("Durchgang mit Fehler:")
    original_run = w.run_pass
    try:
        def exploding(watch_dir, reason):
            raise RuntimeError("geplatzt")

        w.run_pass = exploding
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            w.guarded_pass(tmp_root, "Probe")
        journal = buffer.getvalue()
        check("der Traceback landet im Journal",
              "RuntimeError" in journal and "geplatzt" in journal, True)
        check("und der Anlass steht dabei", "Probe" in journal, True)
    finally:
        w.run_pass = original_run

    source = DAEMON.read_text(encoding="utf-8")
    gesichert = [reason for reason in
                 ("Ereignis: angelegt", "Ereignis: verschoben",
                  "Ereignis: gel\u00f6scht", "Startlauf", "Sicherheitslauf")
                 if f'guarded_pass(watch_dir, "{reason}")' in source]
    check("alle fuenf Stellen des Dauerbetriebs sind gesichert",
          len(gesichert), 5)
    check("der Einzellauf bleibt ungesichert",
          'run_pass(watch_dir, "Einzellauf")' in source, True)


def check_uninstall_guard(w: types.ModuleType, tmp_root: Path) -> None:
    """The uninstaller removes the unit only when the service is provably gone.

    It used to throw both the return value and the message away, so it claimed
    success while a watcher kept running -- and without its unit that watcher
    was harder to stop than before (doku 3.5).

    Run as a subprocess against a stubbed systemctl, so this needs no systemd
    and cannot touch the real installation. The bus case is the one that
    matters: there, is-active exits 1, which read as a return value looks like
    "not running".
    """
    print("Abmelden mit Nachweis (3.5):")
    stage = tmp_root / "abmelden"
    fake_bin = stage / "bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    unit_dir = stage / ".config" / "systemd" / "user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    unit_file = unit_dir / "claude-sync-watch.service"

    def systemctl_stub(disable_rc: int, is_active_word: str,
                       is_active_rc: int) -> None:
        (fake_bin / "systemctl").write_text(
            "#!/bin/sh\n"
            "case \"$*\" in\n"
            f'  *"disable"*) echo "disable sagte etwas" >&2; exit {disable_rc} ;;\n'
            f'  *"is-active"*) echo "{is_active_word}"; exit {is_active_rc} ;;\n'
            "  *) exit 0 ;;\n"
            "esac\n", encoding="utf-8")
        (fake_bin / "systemctl").chmod(0o755)

    def run() -> tuple[int, str]:
        unit_file.write_text("[Unit]\n", encoding="utf-8")
        environment = dict(os.environ)
        environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
        environment["HOME"] = str(stage)
        result = subprocess.run(["bash", str(UNINSTALL)], env=environment,
                                capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr

    # 1. Dienst laeuft weiter: Abbruch, und die Unit bleibt liegen.
    systemctl_stub(disable_rc=1, is_active_word="active", is_active_rc=0)
    code, output = run()
    check("laufender Dienst: Abbruch", code, 1)
    check("und die Unit bleibt liegen", unit_file.exists(), True)
    check("mit Hinweis, wie weiter", "systemctl --user stop" in output, True)

    # 2. Kein Benutzer-Bus: Rueckgabewert sieht wie "inaktiv" aus, ist es aber
    #    nicht -- entschieden wird am Wort.
    systemctl_stub(disable_rc=1, is_active_word="Failed to connect to bus",
                   is_active_rc=1)
    code, output = run()
    check("ohne Bus: trotzdem Abbruch", code, 1)
    check("und auch hier bleibt die Unit", unit_file.exists(), True)

    # 3. Dienst inaktiv: regulaerer Verlauf.
    systemctl_stub(disable_rc=0, is_active_word="inactive", is_active_rc=4)
    code, output = run()
    check("inaktiv: Abmelden laeuft durch", code, 0)
    check("Unit entfernt", unit_file.exists(), False)
    check("und die Schlusszeile erscheint",
          "Der Dienst ist abgemeldet" in output, True)

    # 4. Nie eingerichtet: kein Abbruch, aber die Meldung wird nicht
    #    verschluckt (2.6).
    systemctl_stub(disable_rc=1, is_active_word="inactive", is_active_rc=4)
    code, output = run()
    check("nie eingerichtet: kein Abbruch", code, 0)
    check("aber die Meldung erscheint",
          "Hinweis vom Abmelden" in output, True)


def check_folder_check(w: types.ModuleType, tmp_root: Path) -> None:
    """The folder check: three outcomes, and read-only by contract.

    The installer used to promise that the watched directory is *configured*
    while testing that a directory exists -- the silent failure the whole
    checklist exists for (doku 3.5). The three outcomes have to stay apart,
    because only the middle one is a finding: an unreachable interface permits
    no conclusion at all.

    The read-only property is pinned here rather than trusted: a run lock taken
    by this switch would be read as "not configured" whenever a pass happens to
    hold it, and a state write would overwrite that pass's state.
    """
    print("Freigabe-Prüfung:")
    original_key, original_get = w.read_api_key, w.rest_get
    shared = tmp_root / "geteilt"
    shared.mkdir(parents=True, exist_ok=True)
    try:
        w.read_api_key = lambda: "k"
        w.rest_get = lambda path, api_key: (
            {"folders": [{"id": "abcde-fghij", "path": str(shared),
                          "paused": False}]}
            if path.startswith("/rest/system/config") else None)
        check("Freigabe gefunden", w.check_folder(shared), 0)
        check("anderer Ordner: keine Freigabe",
              w.check_folder(tmp_root / "fremd"), 1)

        w.rest_get = lambda path, api_key: None          # Schnittstelle stumm
        check("Schnittstelle stumm: nicht prüfbar", w.check_folder(shared), 2)

        w.read_api_key = lambda: None                    # kein Schlüssel
        check("kein Schlüssel: nicht prüfbar", w.check_folder(shared), 2)
    finally:
        w.read_api_key, w.rest_get = original_key, original_get

    # Die zugesicherte Eigenschaft: keine Sperre, kein Schreiben.
    original_dir = w.TOOL_DIR
    w.set_tool_dir(tmp_root / "unberuehrt")
    try:
        w.TOOL_DIR.mkdir(parents=True, exist_ok=True)
        w.save_state(w.WatchState(conflict_active=True))
        before = w.STATE_FILE.read_bytes()
        w.read_api_key = lambda: "k"
        w.rest_get = lambda path, api_key: None
        w.check_folder(shared)
        check("keine Laufsperre entstanden", w.LOCK_FILE.exists(), False)
        check("Zustandsdatei unverändert", w.STATE_FILE.read_bytes(), before)
    finally:
        w.read_api_key, w.rest_get = original_key, original_get
        w.set_tool_dir(original_dir)


def check_deferral_stamp(w: types.ModuleType, tmp_root: Path) -> None:
    """The waiting time counts from the deferral, not from the appearance.

    A dialog closes itself after fifteen minutes. Stamped at the appearance,
    half of the promised half hour was gone by the time the deferral happened,
    and the next dialog could arrive twice as early as 2.9 assures. The check
    has to prove WHEN the stamp was taken, not merely that it is young -- both
    look the same to a "is it recent?" question. The zenity stub therefore
    records the moment it returns, and the stamp must lie after it.
    """
    print("Wartezeit ab der Vertagung:")
    original_dir, original_run = w.TOOL_DIR, w.subprocess.run
    w.set_tool_dir(tmp_root / "vertagung")
    sample_pair = w.ConflictPair(copy=tmp_root / "a.sync-conflict-x.txt",
                                original=tmp_root / "a.txt", device="DEV")
    returned_at = {}

    def answering(code: int, err: bytes = b""):
        def run(*args, **kwargs):
            returned_at["at"] = w._now()          # Zeitpunkt der Rückkehr
            return types.SimpleNamespace(returncode=code, stderr=err)
        return run

    try:
        # Zeitablauf (Rückgabewert 5) gilt als Vertagung.
        w.subprocess.run = answering(5)
        probe_state = w.WatchState()
        w.escalate([sample_pair], probe_state, tmp_root)
        check("Stempel liegt nach der Antwort",
              probe_state.dialog_last_shown >= returned_at["at"], True)
        check("und gilt nicht als gescheitert", probe_state.dialog_failed, False)

        # Abbruch durch den Nutzer: dasselbe.
        w.subprocess.run = answering(1)
        probe_state = w.WatchState()
        w.escalate([sample_pair], probe_state, tmp_root)
        check("auch bei Abbruch nach der Antwort",
              probe_state.dialog_last_shown >= returned_at["at"], True)

        # Gegenprobe: Ein nicht gezeigter Dialog ist KEINE Vertagung -- dort
        # muss der frühe Stempel stehen bleiben, damit die kurze Wiederholung
        # ab dem Versuch läuft.
        w.subprocess.run = answering(1, b"cannot open display: :99")
        probe_state = w.WatchState()
        w.escalate([sample_pair], probe_state, tmp_root)
        check("nicht gezeigt: gescheitert vermerkt",
              probe_state.dialog_failed, True)
        check("nicht gezeigt: Stempel nicht nachgezogen",
              probe_state.dialog_last_shown < returned_at["at"], True)
    finally:
        w.subprocess.run = original_run
        w.set_tool_dir(original_dir)


def check_missing_notify_send(w: types.ModuleType) -> None:
    """A missing notify-send is a fault report, never a substitute channel.

    Both halves stay invisible when wrong, and both were wrong: for two days on
    one machine the notice text went to the journal instead of the screen, which
    reads like a working watcher while nobody ever saw a notice (doku 2.6, 3.8).
    """
    print("Fehlendes notify-send:")
    original = w.subprocess.run

    def absent(command, *args, **kwargs):
        raise FileNotFoundError(command[0])

    def run_notices(*bodies: str) -> str:
        captured = io.StringIO()
        w.subprocess.run = absent
        w._notify_missing_reported = False
        try:
            with contextlib.redirect_stderr(captured):
                for body in bodies:
                    w.notify("Claude-Sync", body)
        finally:
            w.subprocess.run = original
            w._notify_missing_reported = False
        return captured.getvalue()

    written = run_notices("abgeglichen: 1.1 kB hoch", "abgeglichen: 2.2 kB hoch")
    check("Meldungsinhalt bleibt draußen", "abgeglichen" in written, False)
    check("Störung genau einmal je Lauf", written.count("notify-send"), 1)
    check("nennt das nachzuinstallierende Paket",
          "libnotify-bin" in written, True)
    # Once per run, not once for ever: a package removed later must show up
    # again. That is why the marker is a module variable and not a state field.
    check("nach Neustart wieder gemeldet",
          run_notices("abgeglichen: 3.3 kB hoch").count("notify-send"), 1)


def main() -> int:
    if not DAEMON.exists():
        print(f"Nicht gefunden: {DAEMON}", file=sys.stderr)
        return 2
    w = load_daemon()
    check_dialog_answers(w)
    check_timeout_unit(w)
    check_terminal_dialogs(w)
    check_dialog_timing(w)
    check_naming(w)
    check_session_detection(w)
    check_missing_notify_send(w)
    with tempfile.TemporaryDirectory(prefix="claude-sync-probe-") as tmp:
        check_lock(w, Path(tmp))
        check_swallowed_errors(w, Path(tmp))
        check_episode_clock(w, Path(tmp))
        check_terminal_duplicates(w, Path(tmp))
        check_precondition_exit(w, Path(tmp))
        check_free_text_terminal(w, Path(tmp))
        check_launch_failure(w, Path(tmp))
        check_pass_guard(w, Path(tmp))
        check_uninstall_guard(w, Path(tmp))
        check_dry_run(w, Path(tmp))
        check_folder_check(w, Path(tmp))
        check_deferral_stamp(w, Path(tmp))
        check_transfer_temporaries(w, Path(tmp))
        check_notice(w, Path(tmp))
    print()
    if failures:
        print(f"{failures} Abweichung(en).")
        return 1
    print("Alle Fälle wie festgelegt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
