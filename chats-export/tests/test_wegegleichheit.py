#!/usr/bin/env python3
"""Both ways must produce the same file for the same chat.

The promise of ``implementation_doku.md`` Vorgabe 2.5: a chat fetched out of an account
export and the same chat fetched through ``read_conversation`` end up as the
same document.  Otherwise the content of the archive depends on which route a
chat came in by, and "do I have this chat?" stops being a sharp question.

Nothing enforces that at runtime -- the two scripts are deliberately separate,
because ``chat_read_store.py`` has to stay uploadable as a single file.  This
test is the only thing standing between the two shapes and silent drift.

    python3 tests/test_wegegleichheit.py
    python3 -O tests/test_wegegleichheit.py
"""

import json
import os
import sys
import zipfile

_HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(os.path.dirname(_HERE), "source")
sys.path.insert(0, SOURCE_DIR)

import chat_export_convert as cec
import chat_read_store as crs

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

for field in ("chat_uuid", "url", "title", "turns", "deleted",
              "predecessor", "successor", "imported_at"):
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

# read_conversation supplies no created_at, so chat_date cannot agree. That is
# a documented asymmetry, not drift -- but it must stay visible.
check("the export path knows the chat date, the read path admits it does not",
      from_export["metadata"]["chat_date"].startswith("2026-05-01")
      and from_read["metadata"]["chat_date"] == "unknown",
      f"{from_export['metadata']['chat_date']!r} vs "
      f"{from_read['metadata']['chat_date']!r}")

# Everything else that only one path can observe must be empty on the other,
# never absent -- otherwise a comparison of two files would trip over shape.
for field, empty in (("dropped_duplicates", 0), ("dropped_blocks", {}),
                     ("dropped_thinking", 0),
                     ("attachments_without_content", [])):
    check(f"the read path reports an empty {field} rather than omitting it",
          from_read["metadata"][field] == empty,
          repr(from_read["metadata"][field]))


# ---------------------------------------------------------------------------
# The same through both command lines, on files
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

page_file = os.path.join(WORK, "seite.txt")
with open(page_file, "w", encoding="utf-8") as handle:
    handle.write(page)

out_export = os.path.join(WORK, "aus-zip")
out_read = os.path.join(WORK, "aus-read")
convert = os.path.join(SOURCE_DIR, "chat_export_convert.py")
read = os.path.join(SOURCE_DIR, "chat_read_store.py")


def run(*args):
    """Invoke one of the two scripts."""
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


run(convert, "list", "--map", listing, "--out", out_export)
result = run(convert, "convert", "--zip", archive_path, "--out", out_export,
             "--now", NOW)
check("the zip route writes its file", result.returncode == 0, result.stderr)

run(read, "--store-dir", out_read, "ingest", "--raw", page_file)
# No --out: the file name has to follow doku 2.3 on this route as well, so
# that the protocol can carry a name a later run will recognise.
result = subprocess.run(
    [sys.executable, read, "--store-dir", out_read, "export", "--chat", UUID,
     "--now", NOW], capture_output=True, text=True, cwd=WORK)
read_file = os.path.join(WORK, f"ohne-datum_wegegleichheit_{UUID[:8]}.json")
check("the read route writes its file under the 2.3 name",
      result.returncode == 0 and os.path.exists(read_file),
      result.stderr + str(os.listdir(WORK)))

written = [name for name in os.listdir(out_export)
           if name.endswith(".json") and name != cec.PROTOCOL_FILENAME]
with open(os.path.join(out_export, written[0]), "r", encoding="utf-8") as handle:
    file_export = json.load(handle)
with open(read_file, "r", encoding="utf-8") as handle:
    file_read = json.load(handle)

check("the files agree on the transcript",
      file_export["messages"] == file_read["messages"],
      f"{file_export['messages']}\n  vs {file_read['messages']}")
check("the files agree on the metadata keys",
      list(file_export["metadata"]) == list(file_read["metadata"]),
      f"{list(file_export['metadata'])}\n  vs {list(file_read['metadata'])}")

# The one difference a reader may rely on: the fields whose value depends on
# what the route can observe. Everything else must be equal.
differing = {key for key in file_export["metadata"]
             if file_export["metadata"][key] != file_read["metadata"][key]}
check("only the fields that depend on the route differ",
      differing == {"source", "chat_date", "total_turns", "complete",
                    "turns_missing"},
      str(sorted(differing)))

# ---------------------------------------------------------------------------
# The protocol has to converge as well -- this was the gap of Fahrplan 12
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

# Exactly the fields a route cannot know may differ -- mirroring 2.5.
differing = {key for key in entry_zip if entry_zip[key] != entry_read[key]}
check("only the route-dependent protocol fields differ",
      differing == {"created_at", "total_turns", "file"},
      str(sorted(differing)))
check("the zip route knows created_at, the read route does not",
      entry_zip["created_at"] != "" and entry_read["created_at"] == "")
check("the read route proves total_turns, the zip route does not claim it",
      entry_read["total_turns"] == len(TURNS)
      and entry_zip["total_turns"] is None,
      f"{entry_read['total_turns']} vs {entry_zip['total_turns']}")
check("the file names differ only in the date segment",
      entry_zip["file"].split("_", 1)[1] == entry_read["file"].split("_", 1)[1],
      f"{entry_zip['file']} vs {entry_read['file']}")

shutil.rmtree(WORK, ignore_errors=True)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All checks passed.")
