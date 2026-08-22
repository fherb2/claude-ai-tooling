#!/usr/bin/env python3
"""Guard against docstring drift: every CLI symbol, and every hand-picked
concept, has to be mentioned in the module docstring of its own script.

Vorgabe 2.9 keeps the uploadable scripts self-contained -- the docstring IS
the operating manual, nothing else travels with the file. Twice already a
feature shipped (attachments/creations/window, then the protocol timestamp
fields) while the docstring kept describing an earlier version. This test is
the guard against a third time: it does not check that the explanation is
*good*, only that the symbol is not silently missing.

Two layers, because they catch different kinds of drift:

1.  Mechanical -- every ``sub.add_parser("...")`` name and every
    ``add_argument("--...")`` flag, pulled straight from the source, must
    appear as a substring of the docstring.  No judgement call: if a command
    exists, its name has to be typed somewhere in the manual.
2.  Hand-maintained -- a per-script word list of concepts no parser
    introspection can find, because they are not CLI symbols (field names,
    file suffixes, named functions).  This list has to be extended by hand
    whenever a feature adds one of these; that manual step is deliberate,
    not an oversight -- there is no way to derive "important concept" from
    source code alone.

    python3 tests/test_docstrings.py
    python3 -O tests/test_docstrings.py

The two scripts it covers live in two places, by what each one is for, and the
``SCRIPTS`` mapping below records which is where: the converter with the skill
it ships in, and ``inspect_export.py`` in the project root as a maintenance
tool. Moving a script therefore means editing that mapping, and this test
failing to find a file is the reminder.

``tests/wegegleichheit_referenz.py`` is deliberately *not* covered: it is a
comparison yardstick, not a tool anyone operates, and it has no command line
whose symbols could drift out of a manual.
"""

import ast
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = _HERE
PROJECT_DIR = os.path.dirname(_HERE)
SKILL_DIR = os.path.join(os.path.dirname(_HERE), "skills", "chat-export")

FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record and print one assertion result."""
    status = "ok  " if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


def load_docstring(path: str) -> str:
    """Return the module-level docstring, or '' if there is none."""
    with open(path, "r", encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    return ast.get_docstring(tree) or ""


def parser_symbols(path: str) -> tuple[list[str], list[str]]:
    """Pull every subcommand name and every ``--flag`` straight from source.

    Regex over source text, not AST-argument introspection: the CLI symbols
    are string literals passed to argparse calls, and a regex over those two
    call shapes is simpler and just as exact as walking the AST for them.
    """
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    commands = sorted(set(re.findall(r'sub\.add_parser\(\s*"([a-z_]+)"', text)))
    flags = sorted(set(re.findall(r'add_argument\(\s*"(--[a-z-]+)"', text)))
    return commands, flags


# ---------------------------------------------------------------------------
# Layer 2: concepts no parser introspection can find (doku 2.9)
# ---------------------------------------------------------------------------

REQUIRED_CONCEPTS = {
    "chat_export_convert.py": [
        "attachments", "creations", "thinking", "protokoll.json",
        "window_start", "MAPPING_PROMPT", "INSTRUCTION_BLOCKS",
        "VANISHED_NOTE",
        "load_bundle", "bundle_records", "bundle_conversations",
        "SOURCE_WEB",
    ],
    "inspect_export.py": [
        "created_at", "project",
    ],
}


# ---------------------------------------------------------------------------
# Run both layers over every script this guard covers
# ---------------------------------------------------------------------------

# Script name -> the directory it lives in. Two homes, by what each script is
# for: the converter ships with the skill; inspect_export is a maintenance tool
# of this project and sits in its root.
SCRIPTS = {
    "chat_export_convert.py":  SKILL_DIR,
    "inspect_export.py":       PROJECT_DIR,
}

for name, directory in SCRIPTS.items():
    path = os.path.join(directory, name)
    doc = load_docstring(path)
    check(f"{name} has a non-trivial module docstring", len(doc) > 200)

    commands, flags = parser_symbols(path)
    for command in commands:
        check(f"{name}: command '{command}' is mentioned in its docstring",
              command in doc)
    for flag in flags:
        check(f"{name}: flag '{flag}' is mentioned in its docstring",
              flag in doc)

    for concept in REQUIRED_CONCEPTS.get(name, []):
        check(f"{name}: concept '{concept}' is mentioned in its docstring",
              concept in doc)


print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All checks passed.")
