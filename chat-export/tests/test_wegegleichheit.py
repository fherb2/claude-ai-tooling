#!/usr/bin/env python3
"""The converter must produce the documented file, measured against a second implementation.

The promise of ``implementation_doku.md`` Vorgabe 2.5: the same chat ends up
as the same document, whichever way it came in. Otherwise the content of the
archive depends on the route, and "do I have this chat?" stops being a sharp
question.

The converter's two real routes -- account export and web bundle -- satisfy
that *by construction*, because both run through the same code and only the
unwrapping differs. That is exactly why it cannot be the measure here: a
yardstick that shares code with what it measures passes every format change by
definition. So the comparison runs against ``wegegleichheit_referenz.py``, an
independent second implementation of the file format that imports nothing from
the converter.

That module descends from the read route the platform withdrew on 18 August
2026 (doku 1.7). Its command line and fetch loop are gone with the route; what
remains is only the shape -- enough to build a document and a protocol and
hold them next to the converter's.

    python3 tests/test_wegegleichheit.py
    python3 -O tests/test_wegegleichheit.py

WHAT IS COVERED
---------------
The same conversation is described twice -- once the way the export writes it,
once the way the reference implementation builds it -- and then compared:

* **Same top-level keys**, with ``branches`` the single permitted exception:
  only the zip route can observe a branch at all, so an empty list on the read
  side would claim a finding it cannot make.
* **Same metadata keys in the same order**, and ``warnings`` present on both
  even when empty.
* **Identical transcripts.** Where the zip route sees material the read route
  cannot -- thinking, attachments, tool calls -- it adds a reference field.
  Those three references are the only additions allowed, and stripping them
  must leave two identical message lists.
* **Exactly five metadata fields may differ** (``source``, ``created_at``,
  ``total_turns``, ``complete``, ``turns_missing``) -- and no more. Where a
  route cannot know something it writes ``null`` rather than a guess.
* **The protocols too**, not just the chat files: same key sets, same core
  fields, and the window calculation run through one shared table of cases so
  the two implementations cannot drift apart on it.
* **``VANISHED_NOTE`` is identical on both sides** -- the same sentence about
  a chat the fresh list no longer offers, which they must not share as code
  and therefore hold twice.
"""

import json
import os
import sys
import zipfile

_HERE = os.path.dirname(os.path.abspath(__file__))
# Two homes: the converter ships with the skill, the reference implementation
# sits here beside the tests -- it is nobody's tool, only this test's yardstick
# for vorgabe 2.5.
SOURCE_DIR = _HERE
CONVERT_DIR = os.path.join(os.path.dirname(_HERE), "skills", "chat-export")
sys.path.insert(0, SOURCE_DIR)
sys.path.insert(0, CONVERT_DIR)

import chat_export_convert as cec
import wegegleichheit_referenz as crs

FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record and print one assertion result."""
    status = "ok  " if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# One chat, described twice: as the export writes it and as read_conversation
# hands it over.  Same conversation, same wording, different packaging.
# ---------------------------------------------------------------------------

UUID = "11111111-2222-4333-8444-555555555555"
TITLE = "Wegegleichheit"
UPDATED = "2026-05-01T12:00:00.000000Z"
NOW = "2026-05-02T08:00:00+00:00"

TURNS = [
    ("user", "Wie schneiden wir die Rollen zwischen den Prozessen?"),
    ("assistant", "Der GUI-Prozess besitzt die Queue, die uebrigen lesen."),
    ("user", "Und der Aufbau im Shared Memory?"),
    ("assistant", "Ein Kopf mit Sequenznummer und Zeitstempel, dann die Daten."),
]

# --- as the account export writes it ---------------------------------------

ROOT = "00000000-0000-4000-8000-000000000000"
export_messages = []
for index, (role, text) in enumerate(TURNS):
    export_messages.append({
        "uuid": f"m{index}",
        "parent_message_uuid": ROOT if index == 0 else f"m{index - 1}",
        "sender": "human" if role == "user" else "assistant",
        # The flat field deliberately disagrees: the export puts the thinking
        # in there, and taking it would be the mistake this guards against.
        "text": "IRREFUEHREND " + text,
        "content": [{"type": "text", "text": text}],
        "created_at": f"2026-05-01T10:0{index}:00Z",
        "updated_at": f"2026-05-01T10:0{index}:00Z",
        "files": [], "attachments": [],
    })

CONVERSATION = {"uuid": UUID, "name": TITLE, "summary": "",
                "created_at": "2026-05-01T10:00:00.000000Z",
                "updated_at": UPDATED,
                "account": {"uuid": "acc"}, "chat_messages": export_messages}

# --- as read_conversation hands it over ------------------------------------

LABEL = {"user": "Human", "assistant": "Assistant"}
page = (f'<chat url="https://claude.ai/chat/{UUID}" updated_at="{UPDATED}" '
        f'total_turns="{len(TURNS)}" turns="0-{len(TURNS) - 1}">'
        f"<title>{TITLE}</title>\n"
        + "\n".join(f'<turn n="{index}">{LABEL[role]}: {text}</turn>'
                    for index, (role, text) in enumerate(TURNS))
        + "</chat>\n")


# ---------------------------------------------------------------------------
# Both documents
# ---------------------------------------------------------------------------

record = cec.conversation_record(CONVERSATION)
from_export = cec.chat_document(record, NOW)

store = crs.new_store(UUID, f"https://claude.ai/chat/{UUID}", TITLE, UPDATED)
crs.merge_page(store, crs.parse_pages(page)[0])
from_read = crs.build_export(store, now=NOW)


# ---------------------------------------------------------------------------
# The shape has to match field for field
# ---------------------------------------------------------------------------

# 'branches' is the one permitted difference: only the zip route can observe a
# branch at all, so an empty list on the read side would claim a finding it
# cannot make. Everything else must match.
check("both documents carry the same top-level keys apart from branches",
      set(from_export) - {"branches"} == set(from_read) - {"branches"},
      f"{sorted(from_export)} vs {sorted(from_read)}")
check("warnings is present on both, even when empty",
      "warnings" in from_export and "warnings" in from_read)

check("both carry the same metadata keys, in the same order",
      list(from_export["metadata"]) == list(from_read["metadata"]),
      f"{list(from_export['metadata'])}\n  vs {list(from_read['metadata'])}")


# ---------------------------------------------------------------------------
# The transcript has to be identical -- this is the actual promise
# ---------------------------------------------------------------------------

check("the message lists are identical",
      from_export["messages"] == from_read["messages"],
      f"{json.dumps(from_export['messages'], ensure_ascii=False)[:200]}\n"
      f"  vs {json.dumps(from_read['messages'], ensure_ascii=False)[:200]}")

# The promise is about the transcript, and it has to survive the case where the
# zip route sees material the read route cannot: thinking and attachments both
# add a reference field to a message. Those references are the only difference
# allowed, and stripping them must leave two identical transcripts.
REFS = {"thinking_ref", "attachments_ref", "creations_ref"}
RICH = dict(CONVERSATION, uuid="rich-1", chat_messages=[
    dict(export_messages[0],
         attachments=[{"file_name": "k.py", "file_type": "text/x-python",
                       "file_size": 8, "extracted_content": "print(1)"}]),
    dict(export_messages[1], content=[
        {"type": "thinking", "thinking": "A" * 500, "thinking_hidden": False},
        {"type": "text", "text": TURNS[1][1]},
        {"type": "tool_use", "name": "artifacts",
         "input": {"command": "create", "id": "w", "title": "Werk",
                   "content": "WERKINHALT-NUR-NEBENDATEI"}}]),
])
rich_export = cec.chat_document(cec.conversation_record(RICH), NOW)
rich_page = (f'<chat url="https://claude.ai/chat/rich-1" updated_at="{UPDATED}" '
             f'total_turns="2" turns="0-1"><title>{TITLE}</title>\n'
             f'<turn n="0">Human: {TURNS[0][1]}</turn>\n'
             f'<turn n="1">Assistant: {TURNS[1][1]}</turn></chat>\n')
rich_store = crs.new_store("rich-1", "", TITLE, UPDATED)
crs.merge_page(rich_store, crs.parse_pages(rich_page)[0])
rich_read = crs.build_export(rich_store, now=NOW)

extra = {key for message in rich_export["messages"] for key in message} - {
    "n", "role", "content"}
check("the zip route adds only the two known reference fields",
      extra == REFS, str(sorted(extra)))
check("the read route adds no reference field at all",
      not any(set(m) & REFS for m in rich_read["messages"]),
      str(rich_read["messages"])[:120])


def strip_refs(messages):
    """Drop the fields only one route can produce."""
    return [{k: v for k, v in message.items() if k not in REFS}
            for message in messages]


check("the transcript is identical once the references are set aside",
      strip_refs(rich_export["messages"]) == strip_refs(rich_read["messages"]),
      f"{strip_refs(rich_export['messages'])}\n"
      f"  vs {strip_refs(rich_read['messages'])}")
check("the attachment text never reaches the conversation file",
      "print(1)" not in json.dumps(rich_export, ensure_ascii=False))
check("the thinking never reaches the conversation file",
      "A" * 500 not in json.dumps(rich_export, ensure_ascii=False))
check("the creation content never reaches the conversation file",
      "WERKINHALT" not in json.dumps(rich_export, ensure_ascii=False))
check("the zip route counts the work, the read route honestly reports none",
      rich_export["metadata"]["creations"] == 1
      and rich_read["metadata"]["creations"] == 0,
      f"{rich_export['metadata']['creations']} vs "
      f"{rich_read['metadata']['creations']}")

check("the text really is the wording, not the misleading flat field",
      all("IRREFUEHREND" not in message["content"]
          for message in from_export["messages"]),
      str(from_export["messages"])[:160])

for field in ("chat_uuid", "url", "title", "turns", "deleted", "imported_at"):
    check(f"metadata agrees on {field}",
          from_export["metadata"][field] == from_read["metadata"][field],
          f"{from_export['metadata'][field]!r} vs {from_read['metadata'][field]!r}")


# ---------------------------------------------------------------------------
# Where the two ways honestly differ, they say so with None
# ---------------------------------------------------------------------------

check("the export path cannot prove completeness and does not claim it",
      from_export["metadata"]["complete"] is None
      and from_export["metadata"]["total_turns"] is None
      and from_export["metadata"]["turns_missing"] is None,
      str({k: from_export["metadata"][k]
           for k in ("complete", "total_turns", "turns_missing")}))

check("the read path proves completeness against the envelope",
      from_read["metadata"]["complete"] is True
      and from_read["metadata"]["total_turns"] == len(TURNS)
      and from_read["metadata"]["turns_missing"] == [],
      str({k: from_read["metadata"][k]
           for k in ("complete", "total_turns", "turns_missing")}))

check("each path names itself in source",
      from_export["metadata"]["source"] == "account-export"
      and from_read["metadata"]["source"] == "read_conversation")

# read_conversation supplies no created_at, so it cannot agree. That is
# a documented asymmetry, not drift -- but it must stay visible.
check("the export path knows the chat's creation date, the read path admits "
      "it does not",
      from_export["metadata"]["created_at"].startswith("2026-05-01")
      and from_read["metadata"]["created_at"] == "unknown",
      f"{from_export['metadata']['created_at']!r} vs "
      f"{from_read['metadata']['created_at']!r}")

# Everything else that only one path can observe must be empty on the other,
# never absent -- otherwise a comparison of two files would trip over shape.
for field, empty in (("dropped_duplicates", 0), ("dropped_blocks", {}),
                     ("dropped_thinking", 0),
                     ("attachments_without_content", [])):
    check(f"the read path reports an empty {field} rather than omitting it",
          from_read["metadata"][field] == empty,
          repr(from_read["metadata"][field]))


# ---------------------------------------------------------------------------
# The same on files: the converter through its command line, the reference
# through its API. The read route had a command line once; it is gone with the
# route (doku 1.7), so what is compared here is the written result, not two
# invocations.
# ---------------------------------------------------------------------------

import shutil
import subprocess
import tempfile

WORK = tempfile.mkdtemp(prefix="wege-")
archive_path = os.path.join(WORK, "export.zip")
with zipfile.ZipFile(archive_path, "w") as archive:
    archive.writestr("conversations.json", json.dumps([CONVERSATION]))

listing = os.path.join(WORK, "liste.txt")
with open(listing, "w", encoding="utf-8") as handle:
    handle.write(f"<chat url='https://claude.ai/chat/{UUID}' "
                 f"updated_at='{UPDATED}'>Content:\nTitle: {TITLE}\n</chat>\n")

out_export = os.path.join(WORK, "aus-zip")
out_read = os.path.join(WORK, "aus-read")
os.makedirs(out_read, exist_ok=True)
convert = os.path.join(CONVERT_DIR, "chat_export_convert.py")


def run(*args):
    """Invoke the converter."""
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


# Both sides start from the same chat list, folded in at the same
# reconciliation time -- otherwise the bound below cannot be compared, and the
# real workflow starts that way (doku 1.5).
LISTED_AT = "2026-04-30T00:00:00+00:00"
run(convert, "list", "--map", listing, "--out", out_export, "--now", LISTED_AT)
result = run(convert, "convert", "--zip", archive_path, "--out", out_export,
             "--now", NOW)
check("the zip route writes its file", result.returncode == 0, result.stderr)

# The reference side: same list, same time, then the same document written out.
# No --out equivalent -- the name has to follow doku 2.3 on this side as well,
# so that the protocol can carry a name a later run would recognise.
crs.update_state(out_read, [{"uuid": UUID, "url": f"https://claude.ai/chat/{UUID}",
                             "title": TITLE, "updated_at": UPDATED}],
                 now=LISTED_AT)
read_file = os.path.join(out_read, f"{crs.file_stem(store)}.json")
crs.record_export(out_read, store, read_file, NOW)
check("the reference writes its file under the 2.3 name",
      os.path.exists(read_file)
      and os.path.basename(read_file)
      == f"ohne-datum_wegegleichheit_{UUID[:8]}.json",
      os.path.basename(read_file))

written = [name for name in os.listdir(out_export)
           if name.endswith(".json") and name != cec.PROTOCOL_FILENAME]
with open(os.path.join(out_export, written[0]), "r", encoding="utf-8") as handle:
    file_export = json.load(handle)
with open(read_file, "r", encoding="utf-8") as handle:
    file_read = json.load(handle)

check("the files agree on the transcript",
      file_export["messages"] == file_read["messages"],
      f"{file_export['messages']} vs {file_read['messages']}")
check("the files agree on the metadata keys",
      list(file_export["metadata"]) == list(file_read["metadata"]),
      f"{list(file_export['metadata'])} vs {list(file_read['metadata'])}")
# The one difference a reader may rely on: the fields whose value depends on
# what each side can observe. Everything else must be equal.
differing = {key for key in file_export["metadata"]
             if file_export["metadata"][key] != file_read["metadata"][key]}
check("only the fields that depend on the route differ",
      differing == {"source", "created_at", "total_turns", "complete",
                    "turns_missing"},
      str(sorted(differing)))

# ---------------------------------------------------------------------------
# The protocol has to converge as well, not just the chat files (doku 2.4)
# ---------------------------------------------------------------------------

def load_protocol(directory):
    """Read the protokoll.json a route wrote."""
    with open(os.path.join(directory, "protokoll.json"),
              "r", encoding="utf-8") as handle:
        return json.load(handle)


protocol_zip = load_protocol(out_export)
protocol_read = load_protocol(out_read)

check("both routes write a file named protokoll.json",
      os.path.exists(os.path.join(out_export, "protokoll.json"))
      and os.path.exists(os.path.join(out_read, "protokoll.json")))
check("the protocols carry the same top-level keys",
      set(protocol_zip) == set(protocol_read),
      f"{sorted(protocol_zip)} vs {sorted(protocol_read)}")

entry_zip = protocol_zip["chats"][UUID]
entry_read = protocol_read["chats"][UUID]
check("the chat entries carry the same keys",
      set(entry_zip) == set(entry_read),
      f"{sorted(entry_zip)} vs {sorted(entry_read)}")

for field in ("title", "turns", "status", "exported_updated_at",
              "exported_at", "side_files"):
    check(f"the protocols agree on {field}",
          entry_zip[field] == entry_read[field],
          f"{entry_zip[field]!r} vs {entry_read[field]!r}")
check("both routes count the chat as exported",
      entry_zip["status"] == "exported")

# The reconciliation bound must be identical: both routes fold the same list
# at the same time, so both must reach the same conclusion about how far back
# an export has to go.
check("both protocols stamp the same listed_at",
      protocol_zip["listed_at"] == protocol_read["listed_at"] == LISTED_AT,
      f"{protocol_zip['listed_at']!r} vs {protocol_read['listed_at']!r}")
check("both routes bound a first-seen chat the same way",
      entry_zip["created_after"] == entry_read["created_after"],
      f"{entry_zip['created_after']!r} vs {entry_read['created_after']!r}")

# Exactly the fields a route cannot know may differ -- mirroring 2.5.
differing = {key for key in entry_zip if entry_zip[key] != entry_read[key]}
check("only the route-dependent protocol fields differ",
      differing == {"created_at", "total_turns", "file"},
      str(sorted(differing)))
check("created_after is NOT among them -- both routes compute the same bound",
      "created_after" not in differing)
check("the zip route knows created_at, the read route does not",
      entry_zip["created_at"] != "" and entry_read["created_at"] == "")
check("the read route proves total_turns, the zip route does not claim it",
      entry_read["total_turns"] == len(TURNS)
      and entry_zip["total_turns"] is None,
      f"{entry_read['total_turns']} vs {entry_zip['total_turns']}")
check("the file names differ only in the date segment",
      entry_zip["file"].split("_", 1)[1] == entry_read["file"].split("_", 1)[1],
      f"{entry_zip['file']} vs {entry_read['file']}")

# ---------------------------------------------------------------------------
# The window computation: same table, both implementations (doku 2.4)
# ---------------------------------------------------------------------------

# Vorgabe 2.5 keeps the yardstick independent, so window_start exists twice.
# The table below is the guard against the two drifting apart -- a wrong window
# is the one error that loses content silently.
def prot(project_start, chats):
    """Build a protocol skeleton for the window table."""
    return {"project_created_at": project_start, "chats": chats}


def chat(status, created_at="", created_after=""):
    """One protocol entry, only the fields the window cares about."""
    return {"status": status, "created_at": created_at,
            "created_after": created_after}


WINDOW_CASES = [
    ("nothing pending at all",
     prot("2025-01-01", {"a": chat("exported", "2026-01-01")}),
     {"start": "", "source": "nothing-pending"}),
    ("exact created_at wins when present",
     prot("2025-01-01", {"a": chat("stale", "2026-03-01"),
                         "b": chat("exported", "2020-01-01")}),
     {"start": "2026-03-01", "source": "created_at"}),
    ("the earliest pending chat sets the window",
     prot("", {"a": chat("stale", "2026-03-01"),
               "b": chat("stale", "2026-02-01")}),
     {"start": "2026-02-01", "source": "created_at"}),
    # The sources write the same instant differently -- 'Z' from an archive,
    # '+00:00' from a chat list -- and they differ in fractional precision.
    # Compared as plain strings, the later of these two sorts first.
    ("mixed notations are ordered by instant, not by ASCII",
     prot("", {"a": chat("stale", "2026-02-01T10:00:00Z"),
               "b": chat("stale", "2026-02-01T10:00:00.500000+00:00")}),
     {"start": "2026-02-01T10:00:00Z", "source": "created_at"}),
    ("created_after is used when created_at is unknown",
     prot("2025-01-01", {"a": chat("listed", "", "2026-05-01")}),
     {"start": "2026-05-01", "source": "created_after"}),
    ("created_at beats created_after on the same chat",
     prot("", {"a": chat("listed", "2026-04-01", "2026-05-01")}),
     {"start": "2026-04-01", "source": "created_at"}),
    ("the project start bounds a chat with neither",
     prot("2025-11-10", {"a": chat("listed")}),
     {"start": "2025-11-10", "source": "project"}),
    ("no bound anywhere is reported, not guessed",
     prot("", {"a": chat("listed")}),
     {"start": "", "source": "unbounded"}),
    ("one unbounded chat outweighs any bounded ones",
     prot("", {"a": chat("stale", "2026-03-01"), "b": chat("listed")}),
     {"start": "", "source": "unbounded"}),
]

for label, protocol, expected in WINDOW_CASES:
    got_zip = cec.window_start(protocol)
    got_read = crs.window_start(protocol)
    check(f"window -- {label} (zip)",
          got_zip["start"] == expected["start"]
          and got_zip["source"] == expected["source"], str(got_zip))
    check(f"window -- {label}: both routes agree",
          got_zip == got_read, f"{got_zip} vs {got_read}")

# The implausible-date guard, likewise in both.
IMPLAUSIBLE = prot("2026-01-01", {"a": chat("listed", "2025-06-01")})
for name, module in (("zip", cec), ("read", crs)):
    warnings = module.project_start_warnings(IMPLAUSIBLE)
    check(f"a chat older than its project is flagged ({name})",
          len(warnings) == 1 and "cannot predate" in warnings[0], str(warnings))
    check(f"a plausible project date is not flagged ({name})",
          module.project_start_warnings(
              prot("2025-06-01", {"a": chat("listed", "2025-06-01")})) == [])
    check(f"no project date means nothing to check ({name})",
          module.project_start_warnings(
              prot("", {"a": chat("listed", "2025-06-01")})) == [])


# ---------------------------------------------------------------------------
# Wording both routes have to share
# ---------------------------------------------------------------------------
# The yardstick must not import from the converter -- it would stop being one
# (vorgabe 2.5) -- so a shared sentence exists twice and can drift. It
# has happened twice in this project already: analyse against report, and list
# against plan. Whatever both are meant to say word for word is guarded here.

check("both routes word the vanished note identically",
      cec.VANISHED_NOTE == crs.VANISHED_NOTE,
      f"export:\n{cec.VANISHED_NOTE}\n\nread:\n{crs.VANISHED_NOTE}")
check("the vanished note takes the count as a placeholder",
      "{count}" in cec.VANISHED_NOTE, cec.VANISHED_NOTE)
check("it says that nothing is removed automatically",
      "nothing is removed automatically" in cec.VANISHED_NOTE,
      cec.VANISHED_NOTE)


shutil.rmtree(WORK, ignore_errors=True)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All checks passed.")
