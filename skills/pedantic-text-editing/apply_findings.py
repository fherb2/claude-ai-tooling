#!/usr/bin/env python3
"""Apply the approved corrections of one round in a single run.

    apply_findings.py --findings FILE --text FILE --approved FILE [--check]
    apply_findings.py --selftest

WHY THIS EXISTS
---------------
Without it the instance replaces every approved place one at a time. A round of
up to 30 places then takes very long, although the operation is mechanical: at
that moment the before-fragment, the after-fragment and the line number are all
already written down in the findings file, and that file is committed before a
single character of the text changes.

WHAT IT REFUSES TO DO
---------------------
It never guesses. Four situations end the run with nothing written:

* the before-fragment occurs more than once in its line,
* it occurs nowhere,
* two approved findings would change the same characters,
* a findings block cannot be parsed.

Sharing context is not a conflict: neighbouring findings regularly carry the
same word, one at the end of its fragment and one at the start of the next.
Only the trimmed cores are held against each other (see core_of).

The run has two phases and is all-or-nothing: every approved finding is located
first, and only when all of them are unambiguous does the file get written. A
half-changed file would be the worst outcome, because from that point on the
line numbers in the findings file describe a state that no longer exists.

THE TWO INPUTS AND WHY THERE ARE TWO
------------------------------------
The **findings file** is the authority for the text: it is what the first commit
of the round records, so replacing from anywhere else would make that commit a
false witness.

The **approved file** is a JSON list the instance writes, one object per finding
the user has approved. It carries the same data the instance showed in the chat:

    [{"id": 3, "line": 17, "before": "...", "after": "..."}, ...]

Its purpose is the cross-check. Comparing it against the findings file catches a
slipped selection -- an id list shifted by one turns a plausible-looking but
wrong replacement into a mismatch that stops the run. Ids and line numbers must
match exactly; the texts only have to be contained in their stored counterparts,
because the chat excerpt is deliberately shorter than the stored one (rules,
section 6).

Both files come from the same instance, so this is not a four-eyes check. It
catches slipping and mixing up, not a mistake already made while writing the
findings file. That is what the counter-check on the diff is for, and it stays.

WRITE THE APPROVED FILE WITH A FILE TOOL, never through a heredoc: German prose
carries quotation marks and dashes that end a shell string early.

HOW A PLACE IS FOUND
--------------------
The before-fragment is searched in the whole file first. Exactly one hit ends
the search and the line number merely confirms it. Several hits narrow the
search to the given line. Only an ambiguity that survives that ends the run.

Found with the full fragment, replaced only in its core: the context that makes
a fragment findable is not part of the change.

Replacements are applied to the original text back to front, so no earlier
replacement can move a later one -- not even when it adds or removes newlines.

OUTPUT
------
JSON on stdout: "applied" with one entry per replacement, "problems" with one
entry per refusal, "written" telling whether the file was touched. Exit code 0
when every approved finding was applied, 1 otherwise. With --check nothing is
ever written and the exit code reports what a real run would do.
"""

import argparse
import json
import re
import sys

# The heading of a findings block: "### 1 - Zeile 42 - ..." The two leading
# numbers are the id and the line number. Reading them positionally keeps the
# parser independent of the language the labels are written in -- section 8 of
# the rules leaves those free.
HEADING = re.compile(r"^###\s+(\d+)\D+?(\d+)")

# A block of the findings file is indented by four spaces; the fragments live
# there so that no editor can eat their whitespace.
INDENT = "    "


def parse_findings(text):
    """Return {id: {"line": int, "before": str, "after": str}} plus parse errors.

    Structure carries the meaning, not the labels: within one block the first
    indented passage is the before-fragment and the second the after-fragment
    (rules, section 6: always in this order). Anything further down -- a reason,
    a note -- is ignored.
    """
    findings, problems = {}, []
    blocks = re.split(r"^(?=###\s)", text, flags=re.MULTILINE)

    for block in blocks:
        heading = HEADING.match(block)
        if not heading:
            continue
        ident, line = int(heading.group(1)), int(heading.group(2))

        passages = collect_indented(block)
        if len(passages) < 2:
            problems.append({
                "id": ident,
                "reason": "unreadable-block",
                "detail": f"{len(passages)} indented passage(s), expected at least 2",
            })
            continue
        if ident in findings:
            problems.append({"id": ident, "reason": "duplicate-id"})
            continue

        findings[ident] = {"line": line, "before": passages[0], "after": passages[1]}

    return findings, problems


def collect_indented(block):
    """Return the indented passages of one block, in order, without the indent."""
    passages, current = [], []

    for raw in block.splitlines():
        if raw.startswith(INDENT):
            current.append(raw[len(INDENT):])
        elif raw.strip() == "" and current:
            # A blank line inside a passage is kept; only a non-indented,
            # non-blank line ends it.
            current.append("")
        elif current:
            passages.append("\n".join(current).strip("\n"))
            current = []

    if current:
        passages.append("\n".join(current).strip("\n"))
    return passages


def cross_check(approved, findings):
    """Compare the instance's records against the findings file."""
    problems = []

    for record in approved:
        ident = record.get("id")
        stored = findings.get(ident)
        if stored is None:
            problems.append({"id": ident, "reason": "unknown-id"})
            continue
        if record.get("line") != stored["line"]:
            problems.append({
                "id": ident,
                "reason": "line-mismatch",
                "detail": f"approved says {record.get('line')}, findings file says {stored['line']}",
            })
        # The chat excerpt may be shorter than the stored one, so containment is
        # the correct test -- equality would fail on a correct pair.
        if record.get("before", "") not in stored["before"]:
            problems.append({"id": ident, "reason": "before-mismatch"})
        if record.get("after", "") not in stored["after"]:
            problems.append({"id": ident, "reason": "after-mismatch"})

    return problems


def locate(source, line_starts, ident, line, fragment):
    """Return (offset, problem). Exactly one of the two is None."""
    hits = [m.start() for m in re.finditer(re.escape(fragment), source)]

    if len(hits) == 1:
        return hits[0], None
    if not hits:
        return None, {"id": ident, "reason": "not-found", "detail": f"line {line}"}

    # Ambiguous in the file: the line number decides.
    if not 1 <= line <= len(line_starts):
        return None, {"id": ident, "reason": "line-out-of-range", "detail": f"line {line}"}

    start = line_starts[line - 1]
    end = line_starts[line] if line < len(line_starts) else len(source)
    in_line = [hit for hit in hits if start <= hit < end]

    if len(in_line) == 1:
        return in_line[0], None
    if not in_line:
        return None, {
            "id": ident,
            "reason": "not-in-line",
            "detail": f"{len(hits)} hit(s) elsewhere, none in line {line}",
        }
    return None, {
        "id": ident,
        "reason": "ambiguous-in-line",
        "detail": f"{len(in_line)} occurrences in line {line} -- lengthen the before-fragment",
    }


def line_offsets(source):
    """Return the offset at which every line starts."""
    starts = [0]
    for match in re.finditer("\n", source):
        starts.append(match.end())
    return starts


def core_of(before, after):
    """Return (skip, core_before, core_after): the characters that really change.

    A before-fragment carries context on both sides so that it can be found and
    so that the user can judge it. The change itself is usually a few characters
    in the middle. Trimming the shared prefix and suffix leaves exactly those.

    This matters for neighbouring findings: two of them regularly share a word,
    because one ends where the other begins ("... Streuungsanteils von" and
    "von zurückreflektiertem ..."). Their fragments overlap, their changes do
    not. Comparing the trimmed cores tells the two cases apart -- observed on
    real rounds, 27 August 2026, where three of four rounds carried such a pair.
    """
    skip = 0
    while skip < len(before) and skip < len(after) and before[skip] == after[skip]:
        skip += 1

    tail = 0
    while (tail < len(before) - skip and tail < len(after) - skip
           and before[len(before) - 1 - tail] == after[len(after) - 1 - tail]):
        tail += 1

    return skip, before[skip:len(before) - tail], after[skip:len(after) - tail]


def plan(approved, findings, source):
    """Locate every approved finding. Returns (edits, problems)."""
    line_starts = line_offsets(source)
    edits, problems = [], []

    for record in approved:
        ident = record["id"]
        stored = findings[ident]

        skip, core_before, core_after = core_of(stored["before"], stored["after"])
        if not core_before and not core_after:
            problems.append({"id": ident, "reason": "no-change",
                             "detail": "before and after are identical"})
            continue

        # Searched with the full fragment, because that is what carries the
        # uniqueness; replaced only in the trimmed core.
        offset, problem = locate(source, line_starts, ident, stored["line"], stored["before"])
        if problem:
            problems.append(problem)
            continue

        edits.append({
            "id": ident,
            "line": stored["line"],
            "start": offset + skip,
            "end": offset + skip + len(core_before),
            "after": core_after,
        })

    return edits, problems


def find_overlaps(edits):
    """Return a problem per pair of edits that would change the same characters."""
    problems = []
    ordered = sorted(edits, key=lambda edit: (edit["start"], edit["end"]))

    for earlier, later in zip(ordered, ordered[1:]):
        if later["start"] < earlier["end"]:
            problems.append({
                "id": later["id"],
                "reason": "overlap",
                "detail": f"changes the same characters as id {earlier['id']} in line {earlier['line']}",
            })

    return problems


def apply_edits(source, edits):
    """Apply the edits back to front, so no edit can move another."""
    result = source
    for edit in sorted(edits, key=lambda edit: edit["start"], reverse=True):
        result = result[:edit["start"]] + edit["after"] + result[edit["end"]:]
    return result


def run(findings_text, source, approved, write):
    """Do the whole job on strings. Returns (report, new_source_or_None)."""
    findings, problems = parse_findings(findings_text)
    problems += cross_check(approved, findings)

    if problems:
        return {"applied": [], "problems": problems, "written": False}, None

    edits, problems = plan(approved, findings, source)
    problems += find_overlaps(edits)

    applied = [{"id": edit["id"], "line": edit["line"]} for edit in sorted(edits, key=lambda e: e["id"])]

    if problems:
        return {"applied": [], "problems": problems, "written": False}, None
    if not write:
        return {"applied": applied, "problems": [], "written": False}, None

    return {"applied": applied, "problems": [], "written": True}, apply_edits(source, edits)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def main(argv):
    parser = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    parser.add_argument("--findings", help="the findings file of this round")
    parser.add_argument("--text", help="the text file to change")
    parser.add_argument("--approved", help="JSON list of the approved findings")
    parser.add_argument("--check", action="store_true", help="locate everything, write nothing")
    parser.add_argument("--selftest", action="store_true", help="run the built-in checks")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    missing = [name for name in ("findings", "text", "approved") if not getattr(args, name)]
    if missing:
        parser.error("missing: " + ", ".join("--" + name for name in missing))

    approved = json.loads(read(args.approved))
    if not isinstance(approved, list) or not approved:
        print(json.dumps({"applied": [], "problems": [{"reason": "empty-approval"}],
                          "written": False}, ensure_ascii=False, indent=2))
        return 1

    source = read(args.text)
    report, changed = run(read(args.findings), source, approved, write=not args.check)

    if changed is not None:
        with open(args.text, "w", encoding="utf-8") as handle:
            handle.write(changed)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if len(report["applied"]) == len(approved) and not report["problems"] else 1


# --------------------------------------------------------------------------
# Self-test. Synthetic material only -- no real text of anyone's document.
# --------------------------------------------------------------------------

FINDINGS = """Auftrag: Rechtschreibkontrolle der Datei probe.tex.

---

### 1 — Zeile 1 — Rechtschreibung — freigegeben

Vorher:

    dass er dass sagte

Nachher:

    dass er das sagte

Begründung: Konjunktion und Artikel verwechselt.

### 2 — Zeile 3 — Zeichensetzung — freigegeben

Vorher:

    weil, er kam

Nachher:

    weil er kam

### 3 — Zeile 3 — Rechtschreibung — freigegeben

Vorher:

    Die Fälle konsequent

Nachher:

    die Fälle konsequent
"""

SOURCE = "dass er dass sagte\nunveraendert\nweil, er kam und Die Fälle konsequent\n"


def check(condition, label):
    if not condition:
        raise AssertionError(label)


def selftest():
    findings, problems = parse_findings(FINDINGS)
    check(not problems, "clean findings file must parse without problems")
    check(set(findings) == {1, 2, 3}, "all three findings must be recognized")
    check(findings[1]["before"] == "dass er dass sagte", "before-fragment verbatim")
    check(findings[2]["line"] == 3, "line number taken from the heading")

    # The straight case: everything applies, back to front, in one file.
    approved = [{"id": 1, "line": 1, "before": "dass dass", "after": "dass das"},
                {"id": 2, "line": 3, "before": "weil,", "after": "weil"},
                {"id": 3, "line": 3, "before": "Die Fälle", "after": "die Fälle"}]
    approved[0]["before"] = "er dass sagte"  # shorter than stored, as in the chat
    approved[0]["after"] = "er das sagte"
    report, changed = run(FINDINGS, SOURCE, approved, write=True)
    check(report["written"], "a clean run writes")
    check(len(report["applied"]) == 3, "three replacements")
    check(changed == "dass er das sagte\nunveraendert\nweil er kam und die Fälle konsequent\n",
          "all three places replaced, nothing else touched")

    # A slipped id: the line number no longer matches its record.
    slipped = [{"id": 2, "line": 1, "before": "weil,", "after": "weil"}]
    report, changed = run(FINDINGS, SOURCE, slipped, write=True)
    check(changed is None and not report["written"], "mismatch writes nothing")
    check(report["problems"][0]["reason"] == "line-mismatch", "line mismatch is reported")

    # An excerpt the instance changed on the way: caught by containment.
    tampered = [{"id": 1, "line": 1, "before": "dass er DAS sagte", "after": "dass er das sagte"}]
    report, _ = run(FINDINGS, SOURCE, tampered, write=True)
    check(report["problems"][0]["reason"] == "before-mismatch", "altered excerpt is reported")

    # Ambiguity inside the line: the fragment stands twice in the named line,
    # so the line number cannot decide either.
    twice_findings = """### 1 — Zeile 1 — Rechtschreibung — freigegeben

Vorher:

    und

Nachher:

    sowie
"""
    report, changed = run(twice_findings, "er kam und ging und blieb\n",
                          [{"id": 1, "line": 1, "before": "und", "after": "sowie"}], write=True)
    check(changed is None, "ambiguity writes nothing")
    check(report["problems"][0]["reason"] == "ambiguous-in-line", "ambiguity is named as such")

    # The same fragment twice in the file but only once in the line: the line
    # number resolves it, and the other occurrence stays untouched.
    report, changed = run(twice_findings.replace("Zeile 1", "Zeile 2"), "und ging\ner kam und blieb\n",
                          [{"id": 1, "line": 2, "before": "und", "after": "sowie"}], write=True)
    check(changed == "und ging\ner kam sowie blieb\n", "the line number resolves a file-wide ambiguity")

    # Nothing to find at all.
    report, _ = run(FINDINGS, "ein ganz anderer Text\n",
                    [{"id": 1, "line": 1, "before": "dass er dass sagte",
                      "after": "dass er das sagte"}], write=True)
    check(report["problems"][0]["reason"] == "not-found", "a missing fragment is reported")

    # Two approved fragments that would touch the same characters.
    overlap_findings = FINDINGS + """
### 4 — Zeile 1 — Rechtschreibung — freigegeben

Vorher:

    er dass

Nachher:

    er das
"""
    report, changed = run(overlap_findings, SOURCE,
                          [{"id": 1, "line": 1, "before": "dass er dass sagte", "after": "dass er das sagte"},
                           {"id": 4, "line": 1, "before": "er dass", "after": "er das"}], write=True)
    check(changed is None, "overlap writes nothing")
    check(any(problem["reason"] == "overlap" for problem in report["problems"]),
          "the overlap is named")

    # Two findings sharing a context word: their fragments overlap, their
    # changes do not. Taken from a real round of 27 August 2026, where the pair
    # "... beider" / "beider ..." stood in one line.
    shared_findings = """### 1 — Zeile 1 — Rechtschreibung — freigegeben

Vorher:

    Transmissionskoffeizienten beider

Nachher:

    Transmissionskoeffizienten beider

### 2 — Zeile 1 — Rechtschreibung — freigegeben

Vorher:

    beider Polarisationseben gleichermaßem.

Nachher:

    beider Polarisationsebenen gleichermaßen.
"""
    shared_source = "Die Transmissionskoffeizienten beider Polarisationseben gleichermaßem.\n"
    report, changed = run(shared_findings, shared_source,
                          [{"id": 1, "line": 1, "before": "Transmissionskoffeizienten",
                            "after": "Transmissionskoeffizienten"},
                           {"id": 2, "line": 1, "before": "Polarisationseben gleichermaßem.",
                            "after": "Polarisationsebenen gleichermaßen."}], write=True)
    check(not report["problems"], "shared context is not a conflict")
    check(changed == "Die Transmissionskoeffizienten beider Polarisationsebenen gleichermaßen.\n",
          "both changes applied, the shared word untouched")

    # A finding that changes nothing is a defect in the findings file.
    idle = """### 1 — Zeile 1 — Rechtschreibung — freigegeben

Vorher:

    dass er dass sagte

Nachher:

    dass er dass sagte
"""
    report, changed = run(idle, SOURCE, [{"id": 1, "line": 1, "before": "dass", "after": "dass"}],
                          write=True)
    check(changed is None and report["problems"][0]["reason"] == "no-change",
          "a finding without a change is reported")

    # An unreadable block must be reported, not skipped.
    broken = FINDINGS + "\n### 9 — Zeile 5 — Rechtschreibung — freigegeben\n\nkein Block\n"
    _, problems = parse_findings(broken)
    check(problems and problems[0]["reason"] == "unreadable-block", "broken block is reported")

    # --check locates everything and still writes nothing.
    report, changed = run(FINDINGS, SOURCE, approved, write=False)
    check(changed is None and len(report["applied"]) == 3, "--check locates without writing")

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
