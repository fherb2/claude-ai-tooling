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
    """Auswahl- und Freitextdialog: Zeitablauf zaehlt wie Abbruch.

    Warum das hier steht: Beide laufen innerhalb eines Durchgangs. Ein
    unbeantwortetes Fenster hielte die Laufsperre, und eine gehaltene Sperre
    macht den Waechter fuer alles andere taub -- kein weiterer Durchgang, keine
    Meldung, kein Episodenende (doku 3.3). Der Fall trifft eine frische
    Installation, einen verschwundenen Emulator und jeden weiteren Rechner,
    denn nur der leere Zwischenspeicher fuehrt zu diesen Dialogen.
    """
    print("Terminal-Dialoge (Auswahl und Freitext):")
    original = w.subprocess.run
    gesehen = {}

    def attrappe(code, ausgabe=""):
        def lauf(command, *a, **k):
            gesehen["command"] = command
            return types.SimpleNamespace(returncode=code, stdout=ausgabe,
                                         stderr="")
        return lauf

    try:
        w.subprocess.run = attrappe(5)          # Zeitablauf
        check("Auswahl: Zeitablauf wie Abbruch",
              w.pick_from_list("T", "t", "S", ["konsole", "xterm"],
                               w.DIALOG_TIMEOUT_SECONDS), (w.Answer.NO, None))
        check("Auswahl: Zeitangabe uebergeben",
              f"--timeout={w.DIALOG_TIMEOUT_SECONDS}" in gesehen["command"], True)

        w.subprocess.run = attrappe(1)          # Abbruch
        check("Auswahl: Abbruch bleibt Abbruch",
              w.pick_from_list("T", "t", "S", ["konsole"],
                               w.DIALOG_TIMEOUT_SECONDS), (w.Answer.NO, None))

        w.subprocess.run = attrappe(0, "konsole\n")
        check("Auswahl: Wahl kommt durch",
              w.pick_from_list("T", "t", "S", ["konsole"],
                               w.DIALOG_TIMEOUT_SECONDS), (w.Answer.YES, "konsole"))

        w.subprocess.run = attrappe(5)
        check("Freitext: Zeitablauf wie Abbruch",
              w.ask_text("T", "t", w.DIALOG_TIMEOUT_SECONDS), (w.Answer.NO, None))
        check("Freitext: Zeitangabe uebergeben",
              f"--timeout={w.DIALOG_TIMEOUT_SECONDS}" in gesehen["command"], True)

        w.subprocess.run = attrappe(0, " urxvt \n")
        check("Freitext: Eingabe kommt bereinigt",
              w.ask_text("T", "t", w.DIALOG_TIMEOUT_SECONDS), (w.Answer.YES, "urxvt"))

        # Ohne Angabe darf kein --timeout mitgehen: die Vorversuchs-Skripte
        # rufen beide Funktionen ohne Zeitangabe auf.
        w.subprocess.run = attrappe(1)
        w.pick_from_list("T", "t", "S", ["konsole"])
        check("Auswahl: ohne Angabe kein --timeout",
              any(str(x).startswith("--timeout") for x in gesehen["command"]), False)
    finally:
        w.subprocess.run = original

    # Und die Eskalationsstrecke muss die Zeitangabe auch wirklich mitgeben.
    quelle = DAEMON.read_text(encoding="utf-8")
    abschnitt = quelle[quelle.index("def detect_terminal"):quelle.index("def build_handover")]
    check("detect_terminal gibt sie beim Auswahldialog mit",
          "DIALOG_TIMEOUT_SECONDS" in abschnitt.split("pick_from_list")[1][:400], True)
    check("detect_terminal gibt sie bei der Freitexteingabe mit",
          "DIALOG_TIMEOUT_SECONDS" in abschnitt.split("ask_text")[1][:400], True)


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
    gefunden, probleme = w.find_conflicts(folder)
    found = [p.name for p in gefunden]
    check("vollständiger Suchlauf meldet kein Problem", probleme, [])
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
             paused: bool = False) -> None:
        w.read_api_key = lambda: key

        def get(path: str, api_key: str) -> object:
            if path.startswith("/rest/system/connections"):
                return {"connections": {"DEV": {
                    "connected": connected, "startedAt": "t",
                    "inBytesTotal": 0, "outBytesTotal": 0}}}
            if path.startswith("/rest/system/config"):
                return {"folders": [{"id": "F", "path": str(folder),
                                     "paused": paused}]}
            if path.startswith("/rest/db/status"):
                return {"needFiles": need}
            return None

        w.rest_get = get

    def state(seen: object = "2026-08-01T00:00:00") -> object:
        return w.WatchState(last_conflict_seen=seen,
                            last_connected="2026-08-01T00:00:00")

    try:
        stub()
        text, seconds = w.build_notice(state(), 0, folder)
        check("Normalfall kurz", seconds, w.NOTICE_SECONDS_QUIET)
        check("Normalfall nennt die Frist", "kein Konflikt seit" in text, True)

        text, seconds = w.build_notice(state(seen=None), 0, folder)
        check("ohne Bezugspunkt keine Frist",
              "Zählung neu begonnen" in text and "seit" not in text, True)

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
              all(teil in text for teil in ("2 Konflikt(e)", "angehalten",
                                            "Rückstand: 4 Datei(en)")), True)

        # Same wording in both notices -- one source, no drift (doku 2.4).
        stub(need=4)
        ruhe, _ = w.build_notice(state(), 0, folder)
        mit_konflikt, _ = w.build_notice(state(), 2, folder)
        klausel = "; Rückstand: 4 Datei(en)"
        check("Rückstands-Wortlaut identisch",
              ruhe.endswith(klausel) and mit_konflikt.endswith(klausel), True)

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

    # --- Die Einordnung gilt für alle drei Fenster gleich ------------------
    faelle = [
        ("Zustimmung", 0, "", w.Answer.YES),
        ("Abbruch", 1, "", w.Answer.NO),
        ("Zeitablauf", 5, "", w.Answer.NO),
        ("keine Anzeige", 1, "cannot open display: :99", w.Answer.FAILED),
        ("sonstiger Fehler", 255, "boom", w.Answer.FAILED),
    ]
    for label, code, err, erwartet in faelle:
        w.subprocess.run = (lambda *a, _c=code, _e=err, **k:
                            types.SimpleNamespace(returncode=_c, stdout="x\n",
                                                  stderr=_e))
        try:
            check(f"Auswahl: {label}",
                  w.pick_from_list("T", "t", "S", ["konsole"])[0], erwartet)
            check(f"Freitext: {label}", w.ask_text("T", "t")[0], erwartet)
        finally:
            w.subprocess.run = original

    # Eine nicht-leere Fehlerausgabe geht ins Journal, egal wie eingeordnet.
    w.subprocess.run = (lambda *a, **k: types.SimpleNamespace(
        returncode=0, stdout="konsole\n", stderr="Gtk-WARNING: irgendwas"))
    try:
        geschrieben = capture(lambda: w.pick_from_list("T", "t", "S", ["k"]))
    finally:
        w.subprocess.run = original
    check("Auswahl: Fehlerausgabe landet im Journal",
          "Gtk-WARNING" in geschrieben, True)

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
        geschrieben = capture(w.notify, "Claude-Sync", "abgeglichen: 1 kB", 5)
    finally:
        w.subprocess.run = original
    check("notify-send: Rückgabewert wird gemeldet",
          "Rückgabewert 1" in geschrieben, True)
    check("notify-send: Fehlertext wird gemeldet",
          "Benachrichtigungsdienst" in geschrieben, True)
    check("notify-send: Meldungstext bleibt draußen",
          "abgeglichen" in geschrieben, False)

    # --- maybe_notify: Programmierfehler melden UND stempeln ---------------
    original_build = w.build_notice

    def kaputt(*args, **kwargs):
        raise KeyError("backlog")

    zustand = w.WatchState()
    w.build_notice = kaputt
    try:
        geschrieben = capture(w.maybe_notify, zustand, 0, tmp_root)
    finally:
        w.build_notice = original_build
    check("Ausnahme in der Meldung wird gemeldet",
          "Betriebsmeldung fehlgeschlagen" in geschrieben, True)
    check("mit Rückverfolgung", "KeyError" in geschrieben, True)
    # Ohne Stempel bliebe die Meldung fällig und die Zeile käme im Takt der
    # Dateiereignisse -- genau die Flut, die 2.6 ausschliesst.
    check("und trotzdem gestempelt", zustand.notice_last_shown is not None, True)

    ruhig = w.WatchState()
    w.build_notice = lambda *a, **k: None
    try:
        w.maybe_notify(ruhig, 0, tmp_root)
    finally:
        w.build_notice = original_build
    check("auch ein reguläres Nichts stempelt",
          ruhig.notice_last_shown is not None, True)

    # --- Der Ausgang muss bis zur Wartezeit durchkommen -------------------
    # Der Kern von Befund 3: Fällt die Anzeige erst NACH der ersten Frage aus,
    # stand dialog_failed schon auf False -- die halbe Stunde griff statt der
    # kurzen Wiederholung, und der Nutzer hatte nichts gesehen (doku 3.3).
    original_detect = w.detect_terminal
    original_dir = w.TOOL_DIR
    w.set_tool_dir(tmp_root / "eskalation")
    paar = w.ConflictPair(copy=tmp_root / "a.sync-conflict-x.txt",
                          original=tmp_root / "a.txt", device="DEV")
    try:
        w.subprocess.run = (lambda *a, **k: types.SimpleNamespace(
            returncode=0, stdout=b"", stderr=b""))          # erste Frage: ja
        w.detect_terminal = lambda state: (w.Answer.FAILED, None)
        zustand = w.WatchState()
        capture(w.escalate, [paar], zustand, tmp_root)
        check("Anzeigeausfall in der Strecke setzt dialog_failed",
              zustand.dialog_failed, True)
        check("und damit gilt die kurze Wiederholung",
              zustand.dialog_due(), False)   # 5 Minuten noch nicht um
    finally:
        w.detect_terminal = original_detect
        w.subprocess.run = original
        w.set_tool_dir(original_dir)

    # --- find_conflicts: nichts gesehen ist nicht nichts gefunden ---------
    check("fehlender Ordner wird gemeldet",
          bool(w.find_conflicts(tmp_root / "gibtsnicht")[1]), True)
    sperr = tmp_root / "gesperrt"
    (sperr / "innen").mkdir(parents=True, exist_ok=True)
    os.chmod(sperr / "innen", 0o000)
    try:
        _, probleme = w.find_conflicts(sperr)
        if os.geteuid() == 0:
            print("  übersprungen unlesbarer Unterordner (als root lesbar)")
        else:
            check("unlesbarer Unterordner wird gemeldet", bool(probleme), True)
    finally:
        os.chmod(sperr / "innen", 0o700)


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
