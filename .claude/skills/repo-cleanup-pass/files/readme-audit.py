#!/usr/bin/env python3
"""Audits every versioned README of the repository: does it carry a date line,
and does it carry the cross-link to its other language version?

Both lines are looked for in a restricted zone only: everything before the
first level-1 heading, plus everything between that heading and the next
level-1 or level-2 heading. A date somewhere down in the body text is
therefore no longer mistaken for a date line.

Three states per check instead of two. A README may have been written by hand
without knowing the exact conventions, and such a file must still be readable
by this tool: a deviating date form or an unusual cross-link is reported as
found-but-deviating, not as missing. Those cases are for the agent to inspect
before they are put to the developer as a finding.

Skill folders with a construction sign are skipped -- they are unfinished on
purpose. A missing cross-link is only a finding where a second language
version actually exists; that is why the check looks for the partner file.
"""

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from unfinished import is_unfinished  # noqa: E402

try:
    from dateutil import parser as dateparser
except ImportError:
    dateparser = None

HEADING_1_OR_2 = re.compile(r"^#{1,2}\s")
HEADING_1 = re.compile(r"^#\s")
DATE_CANONICAL = re.compile(r"^\*(?:Stand|Last updated):\s*(\d{4}-\d{2}-\d{2})\*\s*$")
LINK_CANONICAL = re.compile(r"^\*\[(?:English version|Deutsche Fassung)\]\(([^)]+)\)\*\s*$")
LINK_ANY = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
LANGUAGE_WORD = re.compile(r"english|deutsch|version|fassung", re.IGNORECASE)
# A four-digit year is required before the fuzzy parser is let near a line.
# Without that guard it reads chapter numbers and version numbers as dates.
YEAR = re.compile(r"(?:19|20)\d{2}")


def repo_root():
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def readme_paths(root):
    """Every versioned README, C-sorted, without the unfinished skills."""
    out = subprocess.run(
        ["git", "-C", root, "ls-files", "-z", "*README*.md"],
        capture_output=True, text=True, check=True,
    ).stdout
    paths = [p for p in out.split("\0") if p]
    paths.sort()
    return [p for p in paths if not is_unfinished(p)]


def zone(lines):
    """The lines a date line or cross-link may legally appear in.

    Returns the zone as (index, text) pairs plus the index of the first level-1
    heading, which is what the canonical position is measured against.
    """
    first_h1 = next((i for i, ln in enumerate(lines) if HEADING_1.match(ln)), None)
    if first_h1 is None:
        return [(i, ln) for i, ln in enumerate(lines)], None
    end = next(
        (i for i in range(first_h1 + 1, len(lines)) if HEADING_1_OR_2.match(lines[i])),
        len(lines),
    )
    picked = [(i, lines[i]) for i in range(0, first_h1)]
    picked += [(i, lines[i]) for i in range(first_h1 + 1, end)]
    return picked, first_h1


def first_content_index(lines, after):
    """Index of the first non-empty line after `after`, or None."""
    for i in range(after + 1, len(lines)):
        if lines[i].strip():
            return i
    return None


def find_date(lines, picked, first_h1):
    """(state, value, raw, line number) -- state is ok / andere Form / KEINS.

    'andere Form' covers a deviating notation as well as a deviating position:
    the rules put the date line immediately below the main heading, and a date
    further down the zone is found but not blessed.
    """
    canonical_at = first_content_index(lines, first_h1) if first_h1 is not None else None
    for i, text in picked:
        m = DATE_CANONICAL.match(text)
        if m:
            state = "ok" if i == canonical_at else "andere Form"
            return state, m.group(1), text.strip(), i + 1
    if dateparser is None:
        return "KEINS", "", "", 0
    for i, text in picked:
        if not YEAR.search(text):
            continue
        try:
            parsed = dateparser.parse(text, fuzzy=True, dayfirst=True)
        except (ValueError, OverflowError):
            continue
        return "andere Form", parsed.date().isoformat(), text.strip(), i + 1
    return "KEINS", "", "", 0


def find_language_link(lines, picked, first_h1, date_line):
    """(state, target, raw, line number) -- state is ok / UNSICHER / FEHLT.

    UNSICHER means: something link-shaped is there, but not in the agreed form.
    That is not a finding by itself -- the agent looks at the place first.
    """
    canonical_at = first_content_index(lines, date_line - 1) if date_line else None
    for i, text in picked:
        m = LINK_CANONICAL.match(text)
        if m:
            state = "ok" if i == canonical_at else "UNSICHER"
            return state, m.group(1), text.strip(), i + 1
    # No canonical line: look for anything link-shaped, preferring a link whose
    # text names a language over a bare link to some other .md file.
    fallback = None
    for i, text in picked:
        for label, target in LINK_ANY.findall(text):
            if LANGUAGE_WORD.search(label):
                return "UNSICHER", target, text.strip(), i + 1
            if fallback is None and target.lower().endswith(".md"):
                fallback = ("UNSICHER", target, text.strip(), i + 1)
    return fallback if fallback else ("FEHLT", "", "", 0)


def partner_of(path, root):
    """The other language version of this README, or '' if the name says none."""
    if path.endswith("README.en.md"):
        return path[: -len("README.en.md")] + "README.md"
    if path.endswith("README.de.md"):
        return path[: -len("README.de.md")] + "README.md"
    if path.endswith("README.md"):
        # In the project root the English version is README.md; below it the
        # German one is. Whichever partner exists is the right one.
        stem = path[: -len("README.md")]
        for candidate in (stem + "README.en.md", stem + "README.de.md"):
            if (root / candidate).is_file():
                return candidate
        return stem + "README.en.md"
    return ""


def target_kind(target):
    if not target:
        return "-"
    return "abs" if target.lower().startswith(("http://", "https://")) else "rel"


def main():
    root_text = repo_root()
    root = Path(root_text)

    if dateparser is None:
        print("HINWEIS: Das Modul python-dateutil fehlt. Die flexible Datumserkennung")
        print("         ist damit abgeschaltet -- eine Datumszeile in ungewohnter Form")
        print("         wird als KEINS gemeldet, obwohl sie da ist.")
        print("         Empfehlung an den Entwickler: pip install python-dateutil")
        print()

    print(f"{'DATEI':<56} {'DATUM':<12} {'FORM':<12} {'QUERVERWEIS':<12} {'ZIEL':<5} PARTNER")

    for path in readme_paths(root_text):
        lines = (root / path).read_text(encoding="utf-8", errors="replace").splitlines()
        picked, first_h1 = zone(lines)

        date_state, date_value, date_raw, date_line = find_date(lines, picked, first_h1)
        link_state, target, link_raw, link_line = find_language_link(
            lines, picked, first_h1, date_line
        )

        partner = partner_of(path, root)
        if partner and (root / partner).is_file():
            partner_state = partner.rsplit("/", 1)[-1]
        else:
            partner_state = "keine zweite Fassung"
            if link_state == "FEHLT":
                link_state = "entfaellt"

        print(
            f"{path:<56} {date_value or 'KEINS':<12} {date_state:<12} "
            f"{link_state:<12} {target_kind(target):<5} {partner_state}"
        )
        if date_state == "andere Form":
            print(f'{"":>4}Datum roh (Zeile {date_line}): {date_raw}')
        if link_state == "UNSICHER":
            print(f'{"":>4}Link  roh (Zeile {link_line}): {link_raw}')
            print(f'{"":>4}Link  Ziel: {target}')

    print()
    print("Zu lesen:")
    print("  DATUM/FORM  ok = Standardform an der vorgeschriebenen Stelle.")
    print("              andere Form = Datum gefunden, aber abweichend geschrieben")
    print("              oder nicht unmittelbar unter der Hauptueberschrift. Der")
    print("              erkannte Wert kann bei unvollstaendiger Angabe geraten sein")
    print("              -- gegen den Rohtext pruefen. KEINS ist immer ein Befund.")
    print("  QUERVERWEIS ok = Standardform an der vorgeschriebenen Stelle.")
    print("              UNSICHER = etwas Linkfoermiges gefunden, aber nicht in der")
    print("              vereinbarten Form. Das ist noch kein Befund: erst die Stelle")
    print("              ansehen, dann entscheiden. FEHLT ist ein Befund, entfaellt nicht.")
    print("  ZIEL        abs = absolute Repo-URL, rel = relativer Pfad. Welche Form")
    print("              richtig ist, sagt skill-dev-doc.md, Kapitel 5.1.")
    if dateparser is None:
        print()
        print("HINWEIS: python-dateutil fehlt -- flexible Datumserkennung war abgeschaltet.")


if __name__ == "__main__":
    sys.exit(main())
