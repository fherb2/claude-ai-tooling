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
   interface says nothing at all (doku 1.7).

This file deliberately does not test the escalation as a whole, the episode
rule or the terminal launch: those need a screen and a human, and the
manual probes next to this file cover them (doku 3.8).
"""

import datetime
import importlib.util
import sys
import tempfile
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
    found = [p.name for p in w.find_conflicts(folder)]
    check("nur die fertige Kopie gefunden", found,
          ["Notiz.sync-conflict-20260811-120000-DEV.txt"])
    for entry in folder.iterdir():
        entry.unlink()
    folder.rmdir()


def check_notice(w: types.ModuleType, tmp_root: Path) -> None:
    """Figures, wording and display time of the hourly notice (doku 1.7).

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
        # the very case the notice exists for (doku 1.7).
        stub(paused=True)
        text, seconds = w.build_notice(state(), 0, folder)
        check("Pause verlängert", seconds, w.NOTICE_SECONDS_ATTENTION)
        check("Pause wird genannt", text.startswith("Abgleich für diesen "
                                                    "Ordner angehalten"), True)

        # With conflicts open the pause is named alongside, not instead: it
        # changes what the user has to do, since the resolution stays local.
        text, seconds = w.build_notice(state(), 2, folder)
        check("Pause neben Konflikten",
              "2 Konflikt(e)" in text and "Abgleich angehalten" in text, True)

        # A paused DEVICE is a different case and needs no own wording: it
        # shows up as no connection (verified against the real configuration,
        # doku 1.7).
        stub(paused=False, connected=False)
        text, _ = w.build_notice(state(), 0, folder)
        check("angehaltenes Gerät heißt: keine Verbindung",
              text.startswith("keine Verbindung"), True)

        # The one case where the notice is not decoration: without the
        # interface there are no figures, but an open conflict must still be
        # reported (doku 1.7).
        stub(key=None)
        check("ohne REST keine Zahlenmeldung",
              w.build_notice(state(), 0, folder), None)
        notice = w.build_notice(state(), 2, folder)
        check("ohne REST trotzdem Konfliktmeldung",
              notice is not None and "2 Konflikt(e)" in notice[0], True)
    finally:
        w.read_api_key, w.rest_get = original_key, original_get
    folder.rmdir()


def main() -> int:
    if not DAEMON.exists():
        print(f"Nicht gefunden: {DAEMON}", file=sys.stderr)
        return 2
    w = load_daemon()
    check_dialog_answers(w)
    check_timeout_unit(w)
    check_dialog_timing(w)
    check_naming(w)
    with tempfile.TemporaryDirectory(prefix="claude-sync-probe-") as tmp:
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
