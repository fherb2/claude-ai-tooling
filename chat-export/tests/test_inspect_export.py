#!/usr/bin/env python3
"""Self-test for inspect_export: the schema watchdog, run against a fixture.

The fixture archive is synthetic (Vorgabe 2.11). Its texts carry marker
strings that must NEVER appear in the tool's output -- that guarantee is what
makes the output safe to paste into a conversation, and it is the most
important check here.

The script under test lives in ``chat-export/`` itself, not with the skill: it
is a maintenance tool of this project, run by hand when there is reason to
think Anthropic changed the export format. No user ever needs it.

    python3 tests/test_inspect_export.py
    python3 -O tests/test_inspect_export.py

WHAT IS COVERED
---------------
* **No chat content in the output** -- the marker strings planted in the
  fixture must never appear. This is the most important check: it is what
  makes the tool's output safe to paste into a conversation. Titles do appear,
  deliberately, because they identify the chats.
* **Archive contents and the member list** -- and that a growing member list is
  not an alarm while a missing ``conversations.json`` is.
* **Projects by creation date** -- the tool reports them because they are the
  supplier for ``--project-created``. Project files are exempt from the export
  window, which is what made a short "sounding" export useful; the web
  endpoint has since made that step unnecessary, but the report stays because
  the schema watch needs it.
* **Counts, span and size of the conversations**, hollow (deleted) chats, forks
  per chat, block types and truth flags.
* **The flat ``text`` discrepancy** -- the tool reports it, because that field
  carries the thinking and using it would flood an archive with internal
  deliberation.
* **``attachments`` with content, reported separately from name-only ``files``
  references** -- the distinction that decides how much an archive can keep.
* **The union of all conversation, message and block keys** -- this is the
  schema watch proper, to be held against ``implementation_doku.md`` 3.1.1. A
  *missing* name is the warning sign; a new one is usually just an extension.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

_HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.dirname(_HERE)
sys.path.insert(0, SOURCE_DIR)

import inspect_export as ie

SCRIPT = os.path.join(SOURCE_DIR, "inspect_export.py")
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record and print one assertion result."""
    status = "ok  " if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# Fixture: marker strings stand in for content that must stay invisible
# ---------------------------------------------------------------------------

GEHEIM = "GEHEIMNIS-DARF-NIE-ERSCHEINEN"
ROOT = "00000000-0000-4000-8000-000000000000"


def msg(uuid, parent, sender, text, when, blocks=None, files=None,
        attachments=None):
    """Build one message the way the export writes them."""
    content = blocks if blocks is not None else (
        [{"type": "text", "text": text}] if text else [])
    return {"uuid": uuid, "parent_message_uuid": parent, "sender": sender,
            "text": text, "content": content, "created_at": when,
            "updated_at": when, "files": files or [],
            "attachments": attachments or []}


CONVERSATIONS = [
    {"uuid": "aaa-1", "name": "Gewoehnlich", "summary": "",
     "created_at": "2026-05-01T10:00:00.000000Z",
     "updated_at": "2026-05-01T12:00:00.000000Z",
     "account": {"uuid": "acc"},
     "chat_messages": [
         msg("m0", ROOT, "human", GEHEIM + " Frage", "2026-05-01T10:00:00Z",
             attachments=[{"file_name": "code.py", "file_type": "text/x-python",
                           "file_size": 30,
                           "extracted_content": GEHEIM + " print()"}],
             files=[{"file_uuid": "f1", "file_name": "nur-name.bin"}]),
         msg("m1", "m0", "assistant", "MISLEADING " + GEHEIM,
             "2026-05-01T10:01:00Z", blocks=[
                 {"type": "thinking", "thinking": GEHEIM + " Abwaegung",
                  "thinking_hidden": False, "truncated": False,
                  "cut_off": False, "hidden": False},
                 {"type": "text", "text": GEHEIM + " Antwort"},
             ]),
         # a fork: two children under m1
         msg("m2", "m1", "human", "Weg eins", "2026-05-01T10:02:00Z"),
         msg("m3", "m1", "human", "Weg zwei", "2026-05-01T10:03:00Z"),
     ]},
    {"uuid": "bbb-2", "name": "", "summary": "",
     "created_at": "2026-05-02T10:00:00.000000Z",
     "updated_at": "2026-05-02T17:31:40.000000Z",
     "account": {"uuid": "acc"},
     "chat_messages": [
         msg("h0", ROOT, "human", "", "2026-05-02T10:00:00Z", blocks=[]),
         msg("h1", "h0", "assistant", "", "2026-05-02T10:01:00Z", blocks=[]),
     ]},
]

WORK = tempfile.mkdtemp(prefix="inspect-test-")
ARCHIVE = os.path.join(WORK, "export.zip")
with zipfile.ZipFile(ARCHIVE, "w") as archive:
    archive.writestr("users.json", json.dumps(
        [{"uuid": "u", "full_name": GEHEIM, "email_address": GEHEIM}]))
    archive.writestr("memories.json", json.dumps([]))
    archive.writestr("projects/p-1.json", json.dumps(
        {"uuid": "p-1", "name": "Projekt", "prompt_template": GEHEIM,
         "created_at": "2026-01-05T08:00:00.000000Z",
         "docs": [{"content": GEHEIM * 3}]}))
    archive.writestr("conversations.json", json.dumps(CONVERSATIONS))


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------

check("message chars prefer the larger of text and blocks",
      ie.message_chars({"text": "12345", "content": [
          {"type": "text", "text": "1234567890"}]}) == 10)
check("a hollowed conversation is recognised",
      ie.is_shell(CONVERSATIONS[1]) is True)
check("a conversation with text is no shell",
      ie.is_shell(CONVERSATIONS[0]) is False)
check("the fork is counted as one branch point",
      ie.branch_count(CONVERSATIONS[0]) == 1)


# ---------------------------------------------------------------------------
# End to end: the report says the right things and NEVER leaks content
# ---------------------------------------------------------------------------

result = subprocess.run([sys.executable, SCRIPT, ARCHIVE],
                        capture_output=True, text=True)
out = result.stdout

check("the tool exits 0", result.returncode == 0, result.stderr)
check("it counts the conversations", "conversations: 2, 6 messages" in out, out)
check("it names the hollowed chat as deleted at the source",
      "hollowed conversations (messages present, no text): 1" in out
      and "DELETED at the source" in out, out)
check("it counts the fork", "1 branch(es)" in out, out)
check("it separates carried attachments from name-only references",
      "attachments WITH extracted_content: 1" in out
      and "name only" in out, out)
check("it reports the text/blocks divergence",
      "'text' != the text blocks" in out, out)
check("the schema watch lists all three key sets",
      "conversation keys:" in out and "message keys" in out
      and "block keys" in out, out)
check("it says there is no project reference",
      "NONE -- a conversation does not say" in out, out)

check("it lists the projects by creation date",
      "projects by creation date" in out and "2026-01-05" in out, out)
check("with the project name, which identifies it",
      "Projekt" in out, out)
check("and points at the flag that consumes the date",
      "--project-created" in out, out)

# The one check this tool exists to pass: nothing of the content leaks.
check("no chat content appears in the output -- Vorgabe 2.11",
      GEHEIM not in out and "MISLEADING" not in out
      and "Abwaegung" not in out and "Antwort" not in out, out[:400])
check("titles may appear (they are needed to identify chats)",
      "Gewoehnlich" in out)

# Robustness: an archive without conversations must not crash the watchdog.
EMPTY = os.path.join(WORK, "leer.zip")
with zipfile.ZipFile(EMPTY, "w") as archive:
    archive.writestr("users.json", "[]")
result = subprocess.run([sys.executable, SCRIPT, EMPTY],
                        capture_output=True, text=True)
check("an archive without conversations.json is reported, not a crash",
      result.returncode == 0 and "no conversations.json" in result.stdout,
      result.stdout + result.stderr)

check("wrong usage exits with a message",
      subprocess.run([sys.executable, SCRIPT],
                     capture_output=True, text=True).returncode != 0)

shutil.rmtree(WORK, ignore_errors=True)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All checks passed.")
