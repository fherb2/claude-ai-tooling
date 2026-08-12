#!/usr/bin/env python3
"""Self-test for chat_export_convert: unit checks plus an end-to-end CLI run.

The fixture archive is built here from scratch. **No real chat content**: every
conversation is synthetic and models one situation observed in a real export.

    python3 tests/test_export_convert.py
    python3 -O tests/test_export_convert.py
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

_HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(os.path.dirname(_HERE), "source")
sys.path.insert(0, SOURCE_DIR)

import chat_export_convert as cec

SCRIPT = os.path.join(SOURCE_DIR, "chat_export_convert.py")
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record and print one assertion result."""
    status = "ok  " if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# Fixture: one conversation per observed situation
# ---------------------------------------------------------------------------

ROOT = "00000000-0000-4000-8000-000000000000"


def msg(uuid, parent, sender, text, when, blocks=None, files=None):
    """Build one message the way the export writes them."""
    content = blocks if blocks is not None else (
        [{"type": "text", "text": text}] if text else [])
    return {"uuid": uuid, "parent_message_uuid": parent, "sender": sender,
            "text": text, "content": content,
            "created_at": when, "updated_at": when,
            "files": files or [], "attachments": []}


def conv(uuid, name, messages, created="2026-05-01T10:00:00.000000Z",
         updated="2026-05-01T12:00:00.000000Z"):
    """Build one conversation entry."""
    return {"uuid": uuid, "name": name, "summary": "",
            "created_at": created, "updated_at": updated,
            "account": {"uuid": "acc-1"}, "chat_messages": messages}


# linear: the ordinary case
LINEAR = conv("lin-1", "Linear", [
    msg("l0", ROOT, "human", "Frage eins", "2026-05-01T10:00:00Z"),
    msg("l1", "l0", "assistant", "Antwort eins", "2026-05-01T10:01:00Z"),
    msg("l2", "l1", "human", "Frage zwei", "2026-05-01T10:02:00Z"),
])

# fork where the OLDER child carries the conversation -- the case that
# disproved "youngest child at the fork"
OLD_WINS = conv("old-1", "Aelteres Kind traegt", [
    msg("o0", ROOT, "human", "Ausgangsfrage", "2026-05-02T09:00:00Z"),
    msg("o1", "o0", "assistant", "Antwort", "2026-05-02T09:01:00Z"),
    # older child: continues for three more messages
    msg("oA", "o1", "human", "der echte Weg", "2026-05-02T09:31:50Z"),
    msg("oB", "oA", "assistant", "weiter", "2026-05-02T09:40:00Z"),
    msg("oC", "oB", "human", "und weiter", "2026-05-02T09:50:00Z"),
    # younger child: a dead end with one reply
    msg("oX", "o1", "human", "verworfene Umformulierung", "2026-05-02T09:33:55Z"),
    msg("oY", "oX", "assistant", "Sackgasse", "2026-05-02T09:34:10Z"),
])

# resend storm: identical siblings without descendants
STORM = conv("sto-1", "Sendesturm", [
    msg("s0", ROOT, "human", "dieselbe Nachricht", "2026-05-03T14:30:50Z"),
    msg("s1", ROOT, "human", "dieselbe Nachricht", "2026-05-03T14:30:56Z"),
    msg("s2", ROOT, "human", "dieselbe Nachricht", "2026-05-03T14:31:05Z"),
    msg("s3", "s2", "assistant", "Antwort", "2026-05-03T14:32:00Z"),
])

# hollow: messages present, no text anywhere -- a deleted chat
HOLLOW = conv("hol-1", "", [
    msg("h0", ROOT, "human", "", "2026-05-04T13:05:00Z", blocks=[]),
    msg("h1", "h0", "assistant", "", "2026-05-04T13:06:00Z", blocks=[]),
], updated="2026-05-04T17:31:40Z")

# no messages at all
EMPTY = conv("emp-1", "Ohne Nachrichten", [])

# blocks: text plus thinking, tool_use, tool_result -- and a flat 'text' that
# does not match the text blocks
BLOCKS = conv("blk-1", "Bloecke", [
    msg("b0", ROOT, "human", "steht so nicht in den Bloecken",
        "2026-05-05T08:00:00Z",
        blocks=[{"type": "text", "text": "der echte Text"}],
        files=[{"file_uuid": "f-1", "file_name": "skript.py"}]),
    msg("b1", "b0", "assistant", "", "2026-05-05T08:01:00Z", blocks=[
        {"type": "thinking", "thinking": "…"},
        {"type": "text", "text": "sichtbare Antwort"},
        {"type": "tool_use", "name": "x"},
        {"type": "tool_result", "content": []},
    ]),
])

# unknown sender
STRANGE = conv("str-1", "Fremder Sender", [
    msg("x0", ROOT, "gast", "wer spricht hier", "2026-05-06T08:00:00Z"),
])

CONVERSATIONS = [LINEAR, OLD_WINS, STORM, HOLLOW, EMPTY, BLOCKS, STRANGE]

LISTING = (
    "<chat url='https://claude.ai/chat/lin-1' updated_at='2026-05-01T12:00:00Z'>"
    "Content:\nTitle: Linear\n</chat>\n"
    "<chat url='https://claude.ai/chat/old-1' updated_at='2026-05-02T12:00:00Z'>"
    "</chat>\n"
    "<chat url='https://claude.ai/chat/gibt-es-nicht' "
    "updated_at='2026-05-09T12:00:00Z'>Content:\nTitle: Vertippt\n</chat>\n")


def build_archive(path):
    """Write the fixture archive."""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("users.json", json.dumps(
            [{"uuid": "u-1", "full_name": "Test", "email_address": "t@example"}]))
        archive.writestr("memories.json", json.dumps([]))
        archive.writestr("projects/p-1.json", json.dumps(
            {"uuid": "p-1", "name": "Testprojekt", "docs": [],
             "prompt_template": ""}))
        archive.writestr("conversations.json", json.dumps(CONVERSATIONS))
    return path


WORK = tempfile.mkdtemp(prefix="convert-test-")
ARCHIVE = build_archive(os.path.join(WORK, "export.zip"))
MAP_FILE = os.path.join(WORK, "listing.txt")
with open(MAP_FILE, "w", encoding="utf-8") as handle:
    handle.write(LISTING)


def record(uuid):
    """Normalise one fixture conversation by uuid."""
    entry = next(c for c in CONVERSATIONS if c["uuid"] == uuid)
    return cec.conversation_record(entry)


# ---------------------------------------------------------------------------
# Reading the archive
# ---------------------------------------------------------------------------

archive = zipfile.ZipFile(ARCHIVE)
check("conversations are read from the archive",
      len(cec.load_conversations(archive)) == len(CONVERSATIONS))
check("project records are read", len(cec.load_projects(archive)) == 1)

empty_zip = os.path.join(WORK, "leer.zip")
with zipfile.ZipFile(empty_zip, "w") as handle:
    handle.writestr("users.json", "[]")
try:
    cec.load_conversations(zipfile.ZipFile(empty_zip))
    check("an archive without conversations.json raises", False)
except ValueError as error:
    check("an archive without conversations.json raises",
          "conversations.json" in str(error))


# ---------------------------------------------------------------------------
# Message content
# ---------------------------------------------------------------------------

text, dropped = cec.message_text(BLOCKS["chat_messages"][0])
check("text comes from the content blocks, not from 'text'",
      text == "der echte Text", text)
text, dropped = cec.message_text(BLOCKS["chat_messages"][1])
check("several text blocks are joined", text == "sichtbare Antwort", text)
check("non-text blocks are counted per type",
      dropped == {"tool_use": 1, "tool_result": 1}, str(dropped))
check("thinking is NOT counted as a lost block -- it lives in its own file",
      "thinking" not in dropped, str(dropped))

check("a message without blocks falls back to 'text'",
      cec.message_text({"content": [], "text": "nur flach"})[0] == "nur flach")

check("human maps to user", cec.message_role({"sender": "human"}) == "user")
check("assistant maps to assistant",
      cec.message_role({"sender": "assistant"}) == "assistant")
check("an unexpected sender becomes unknown",
      cec.message_role({"sender": "gast"}) == "unknown")
check("a files entry is a name-only reference",
      cec.file_references(BLOCKS["chat_messages"][0]) == ["skript.py"])
# attachments are the other thing entirely: they carry extracted_content.
mit_inhalt = {"attachments": [{"file_name": "kernel.py", "file_type": "text/x-python",
                              "file_size": 42, "extracted_content": "print(1)"}]}
carried, without = cec.attachment_records(mit_inhalt)
check("an attachment with content is carried over",
      carried == [{"name": "kernel.py", "type": "text/x-python", "size": 42,
                   "content": "print(1)"}], str(carried))
check("nothing is reported as missing then", without == [])
# 22 real attachments have no file_name but several kilobytes of content.
namenlos = {"attachments": [{"file_name": "", "file_type": "txt",
                             "extracted_content": "x" * 100}]}
carried, without = cec.attachment_records(namenlos)
check("a nameless attachment is labelled by its type, not with a question mark",
      carried[0]["name"] == "(ohne Namen, txt)", carried[0]["name"])
check("an attachment without content is reported as missing",
      cec.attachment_records({"attachments": [{"file_name": "leer.txt"}]})
      == ([], ["leer.txt"]))


# ---------------------------------------------------------------------------
# The tree: the decisive rule
# ---------------------------------------------------------------------------

path = cec.main_path(LINEAR["chat_messages"])
check("a linear chat yields its messages in order",
      [m["uuid"] for m in path] == ["l0", "l1", "l2"],
      str([m["uuid"] for m in path]))

path = cec.main_path(OLD_WINS["chat_messages"])
check("the path follows the OLDER child when it carries the conversation",
      [m["uuid"] for m in path] == ["o0", "o1", "oA", "oB", "oC"],
      str([m["uuid"] for m in path]))
check("the dead end is not on the path",
      "oX" not in [m["uuid"] for m in path])

# The rule this replaces would have chosen oX: it is the younger child.
younger = max([m for m in OLD_WINS["chat_messages"]
               if m["parent_message_uuid"] == "o1"], key=cec.sort_key)
check("the discarded rule 'youngest child' would indeed have picked the dead end",
      younger["uuid"] == "oX")

check("an empty conversation yields an empty path", cec.main_path([]) == [])

# A cycle must not hang the walk.
cyclic = [msg("c0", "c1", "human", "a", "2026-05-01T10:00:00Z"),
          msg("c1", "c0", "human", "b", "2026-05-01T10:01:00Z")]
check("a cyclic parent chain terminates", len(cec.main_path(cyclic)) <= 2)


# ---------------------------------------------------------------------------
# Branches and duplicates
# ---------------------------------------------------------------------------

result = record("old-1")
check("the chosen path has five turns", result["turns"] == 5, str(result["turns"]))
check("the dead end is kept as one branch", len(result["branches"]) == 1,
      str(result["branches"]))
check("the branch carries both of its messages",
      len(result["branches"][0]["messages"]) == 2,
      str(result["branches"][0]))
check("nothing was counted as a duplicate here",
      result["dropped_duplicates"] == 0)

result = record("sto-1")
check("a resend storm leaves one path", result["turns"] == 2, str(result["turns"]))
check("identical childless siblings are skipped, not stored",
      result["dropped_duplicates"] == 2, str(result["dropped_duplicates"]))
check("no branch is created for pure resends", result["branches"] == [],
      str(result["branches"]))

# A duplicate WITH descendants must survive: its subtree is not a duplicate.
DUP_WITH_KIDS = conv("dup-1", "Dublette mit Nachfahren", [
    msg("d0", ROOT, "human", "gleicher Text", "2026-05-07T10:00:00Z"),
    msg("d1", ROOT, "human", "gleicher Text", "2026-05-07T10:00:30Z"),
    msg("d2", "d1", "assistant", "der gewaehlte Weg", "2026-05-07T10:02:00Z"),
    msg("d3", "d0", "assistant", "haengt am Duplikat", "2026-05-07T10:01:00Z"),
])
result = cec.conversation_record(DUP_WITH_KIDS)
check("a duplicate with descendants is kept as a branch",
      len(result["branches"]) == 1 and result["dropped_duplicates"] == 0,
      f"branches={result['branches']} dups={result['dropped_duplicates']}")
check("the kept branch holds the duplicate and its child",
      len(result["branches"][0]["messages"]) == 2)


# ---------------------------------------------------------------------------
# Hollow, empty, losses
# ---------------------------------------------------------------------------

result = record("hol-1")
check("a hollow conversation is marked deleted", result["deleted"] is True)
check("a hollow conversation is not marked empty", result["empty"] is False)
check("a hollow conversation carries no text", result["chars"] == 0)

result = record("emp-1")
check("a conversation without messages is marked empty", result["empty"] is True)
check("a conversation without messages is not marked deleted",
      result["deleted"] is False)

result = record("blk-1")
check("dropped block types are reported per conversation",
      result["dropped_blocks"] == {"tool_use": 1, "tool_result": 1},
      str(result["dropped_blocks"]))
check("a name-only file reference is named as such",
      result["attachments_without_content"] == ["skript.py"])

result = record("str-1")
check("an unknown sender is warned about",
      any("unknown sender" in w for w in result["warnings"]),
      str(result["warnings"]))

# A message whose parent is missing entirely must be reported, not lost.
ORPHAN = conv("orp-1", "Waise", [
    msg("p0", ROOT, "human", "regulaer", "2026-05-08T10:00:00Z"),
    msg("p9", "gibt-es-nicht", "human", "haengt im Nichts",
        "2026-05-08T09:00:00Z"),
])
result = cec.conversation_record(ORPHAN)
check("an orphan is either placed or reported",
      result["turns"] + sum(len(b["messages"]) for b in result["branches"]) == 2
      or any("not in this conversation" in w for w in result["warnings"]),
      f"turns={result['turns']} branches={result['branches']} "
      f"warnings={result['warnings']}")


# ---------------------------------------------------------------------------
# The chat list and the uuid check
# ---------------------------------------------------------------------------

listed = cec.parse_chat_list(LISTING)
check("the listing yields one record per chat", len(listed) == 3, str(len(listed)))
check("a title in the listing is taken", listed[0]["title"] == "Linear")
check("a chat without a title is still listed",
      listed[1]["uuid"] == "old-1" and listed[1]["title"] == "")
check("the timestamp is taken", listed[1]["updated_at"] == "2026-05-02T12:00:00Z")

mapping = cec.check_mapping(listed, CONVERSATIONS)
check("uuids present in the archive are recognised",
      set(mapping["known"]) == {"lin-1", "old-1"}, str(mapping))
check("a uuid the archive does not know is reported",
      mapping["unknown"] == ["gibt-es-nicht"], str(mapping))


# ---------------------------------------------------------------------------
# End-to-end CLI
# ---------------------------------------------------------------------------

# The invariant that guarantees nothing is silently lost: every message of a
# conversation ends up either on the chosen path, in a branch, or counted as a
# skipped resend. Verified against the real three-month export, where
# 7338 + 26 + 29 came to exactly 7393.
for fixture in CONVERSATIONS + [DUP_WITH_KIDS, ORPHAN]:
    result = cec.conversation_record(fixture)
    placed = (result["turns"]
              + sum(len(b["messages"]) for b in result["branches"])
              + result["dropped_duplicates"])
    check(f"every message is accounted for in {fixture['uuid']}",
          placed == len(fixture["chat_messages"]),
          f"{placed} placed of {len(fixture['chat_messages'])}")


def run(*args):
    """Invoke the CLI."""
    return subprocess.run([sys.executable, SCRIPT, *args],
                          capture_output=True, text=True)


result = run("analyse", "--zip", ARCHIVE)
check("CLI analyse exits 0", result.returncode == 0, result.stderr)
check("CLI analyse counts the conversations",
      f"{len(CONVERSATIONS)} conversation(s)" in result.stdout, result.stdout)
check("CLI analyse marks the hollow chat as deleted",
      "DELETED (hollow)" in result.stdout, result.stdout)
check("CLI analyse marks the chat without messages",
      "no messages" in result.stdout, result.stdout)
check("CLI analyse reports the branch of the fork",
      "1 branch(es), 2 msg" in result.stdout, result.stdout)
check("CLI analyse reports the skipped resends",
      "2 resend(s) skipped" in result.stdout, result.stdout)
check("CLI analyse lists the left-out block types",
      "tool_use" in result.stdout and "tool_result" in result.stdout,
      result.stdout)
check("CLI analyse separates carried attachments from bare references",
      "mentioned by name only: 1" in result.stdout, result.stdout)

result = run("analyse", "--zip", ARCHIVE, "--map", MAP_FILE)
check("CLI analyse with a mapping reports the hits",
      "2 found in the archive" in result.stdout, result.stdout)
check("CLI analyse names the unknown uuid loudly",
      "not in this archive: gibt-es-nicht" in result.stdout, result.stdout)
check("CLI analyse warns against guessing",
      "Do not guess" in result.stdout, result.stdout)
check("a mapping restricts the listing to the mapped chats",
      "lin-1"[:8] in result.stdout and "hol-1"[:8] not in result.stdout,
      result.stdout)

check("CLI analyse on a missing archive fails",
      run("analyse", "--zip", os.path.join(WORK, "gibtsnicht.zip")).returncode != 0)


# ---------------------------------------------------------------------------
# Thinking blocks: structural selection, never by content
# ---------------------------------------------------------------------------

def thinking_block(text, hidden=False):
    """Build one thinking block."""
    return {"type": "thinking", "thinking": text, "thinking_hidden": hidden,
            "summaries": [{"summary": "kurzer Verlaufshinweis"}]}


LONG = "Abwaegung ueber mehrere Wege. " * 20          # ~600 chars
SHORT = "kurzer Hinweis"                              # far below the threshold

THINK = conv("thk-1", "Mit Denken", [
    msg("t0", ROOT, "human", "Frage", "2026-05-10T10:00:00Z"),
    msg("t1", "t0", "assistant", "", "2026-05-10T10:01:00Z", blocks=[
        thinking_block(LONG),
        {"type": "text", "text": "die Antwort"},
    ]),
    msg("t2", "t1", "human", "noch eine Frage", "2026-05-10T10:02:00Z"),
    msg("t3", "t2", "assistant", "", "2026-05-10T10:03:00Z", blocks=[
        thinking_block(SHORT),                        # too short -> dropped
        thinking_block("x" * 400, hidden=True),       # hidden -> dropped
        thinking_block(LONG + "zweiter Block"),       # kept
        {"type": "text", "text": "zweite Antwort"},
    ]),
])

kept, dropped = cec.message_thinking(THINK["chat_messages"][1])
check("a long thinking block is kept", kept == [LONG], str(kept)[:80])
check("nothing is dropped when the block is long enough", dropped == 0)

kept, dropped = cec.message_thinking(THINK["chat_messages"][3])
check("a short thinking block is dropped", len(kept) == 1, str(len(kept)))
check("a hidden thinking block is dropped too", dropped == 2, str(dropped))
check("the kept block is the long one",
      kept[0].endswith("zweiter Block"), kept[0][-40:])

check("a message without thinking yields nothing",
      cec.message_thinking(THINK["chat_messages"][0]) == ([], 0))

# An attachment with content lands in a file of its own, like the thinking.
ATTACH = conv("att-1", "Mit Anhang", [
    dict(msg("a0", ROOT, "human", "hier das Skript", "2026-05-13T10:00:00Z"),
         attachments=[{"file_name": "kernel.py", "file_type": "text/x-python",
                       "file_size": 8, "extracted_content": "print(1)"},
                      {"file_name": "", "file_type": "txt",
                       "extracted_content": "y" * 300}]),
    msg("a1", "a0", "assistant", "sieht gut aus", "2026-05-13T10:01:00Z"),
])
attach_result = cec.conversation_record(ATTACH)
check("the message with attachments carries a reference",
      attach_result["messages"][0].get("attachments_ref") == "a0",
      str(attach_result["messages"][0]))
check("both attachments are carried with their content",
      len(attach_result["attachments"][0]["files"]) == 2,
      str(attach_result["attachments"]))
check("attachment content is not put into the message text",
      "print(1)" not in attach_result["messages"][0]["content"])
check("a carried attachment is not reported as missing",
      attach_result["attachments_without_content"] == [],
      str(attach_result["attachments_without_content"]))

result = cec.conversation_record(THINK)
check("thinking is not put into the message records",
      all("content" in m and LONG not in m["content"] for m in result["messages"]),
      str(result["messages"])[:120])
check("the assistant message carries a reference to its thinking",
      result["messages"][1].get("thinking_ref") == "t1",
      str(result["messages"][1]))
check("a message whose thinking was all dropped carries no reference",
      "thinking_ref" not in result["messages"][0])
check("two thinking entries are collected",
      len(result["thinking"]) == 2, str(len(result["thinking"])))
check("a thinking entry knows its turn",
      [e["turn"] for e in result["thinking"]] == [1, 3],
      str([e["turn"] for e in result["thinking"]]))
check("dropped thinking blocks are counted",
      result["dropped_thinking"] == 2, str(result["dropped_thinking"]))
check("the visible answer survives",
      result["messages"][1]["content"] == "die Antwort",
      result["messages"][1]["content"])


# The AI's works: artifacts, created files, edits -- the fourth side file.
CREATIONS = conv("crt-1", "Mit Erzeugnissen", [
    msg("c0", ROOT, "human", "bau mir was", "2026-05-14T10:00:00Z"),
    msg("c1", "c0", "assistant", "", "2026-05-14T10:01:00Z", blocks=[
        {"type": "text", "text": "hier ist es"},
        {"type": "tool_use", "name": "artifacts",
         "input": {"command": "create", "id": "art-1", "title": "Mein Werk",
                   "content": "print('WERKINHALT')"}},
        {"type": "tool_use", "name": "artifacts",
         "input": {"command": "update", "id": "art-1",
                   "old_str": "x", "new_str": "WERK-DELTA"}},
        {"type": "tool_use", "name": "create_file",
         "input": {"path": "doku/plan.md", "description": "Der Plan",
                   "file_text": "# DATEIINHALT"}},
        {"type": "tool_use", "name": "str_replace",
         "input": {"path": "alt.py", "old_str": "ALT", "new_str": "NEU"}},
        {"type": "tool_use", "name": "web_search",
         "input": {"query": "bleibt draussen"}},
        {"type": "tool_result", "name": "web_search", "content": []},
    ]),
])
crt = cec.conversation_record(CREATIONS)
check("four works are extracted",
      sum(len(e["works"]) for e in crt["creations"]) == 4,
      str(crt["creations"]))
check("the message carries a creations reference",
      crt["messages"][1].get("creations_ref") == "c1")
kinds = [w["kind"] for e in crt["creations"] for w in e["works"]]
check("artifact, file and edit kinds are told apart",
      kinds == ["artifact", "artifact", "file", "edit"], str(kinds))
deltas = [w["delta"] for e in crt["creations"] for w in e["works"]]
check("updates and edits are marked as deltas, creations are not",
      deltas == [False, True, False, True], str(deltas))
check("extracted creation tools are not counted as dropped blocks",
      crt["dropped_blocks"] == {"tool_use": 1, "tool_result": 1},
      str(crt["dropped_blocks"]))
check("the creations count lands in the record",
      sum(len(e["works"]) for e in crt["creations"]) == 4)
check("creation content is not in the conversation messages",
      "WERKINHALT" not in json.dumps(crt["messages"], ensure_ascii=False))

# Through the CLI: fourth side file, protocol entry, orphan-free.
CRT_DIR = os.path.join(WORK, "erzeugnisse")
crt_zip = os.path.join(WORK, "crt.zip")
with zipfile.ZipFile(crt_zip, "w") as handle:
    handle.writestr("conversations.json", json.dumps([CREATIONS]))
crt_map = os.path.join(WORK, "crt-liste.txt")
with open(crt_map, "w", encoding="utf-8") as handle:
    handle.write("<chat url='https://claude.ai/chat/crt-1' "
                 "updated_at='2026-05-14T12:00:00Z'></chat>\n")
run("list", "--map", crt_map, "--out", CRT_DIR)
result = run("convert", "--zip", crt_zip, "--out", CRT_DIR, "--now", "T-CRT")
check("convert reports the creations", "4 creation(s)" in result.stdout,
      result.stdout)
crt_files = sorted(os.listdir(CRT_DIR))
check("the creations file exists with the shared stem",
      any(f.endswith(cec.CREATION_SUFFIX) for f in crt_files), str(crt_files))
with open(os.path.join(CRT_DIR, cec.PROTOCOL_FILENAME),
          encoding="utf-8") as handle:
    crt_protocol = json.load(handle)
check("the protocol claims the creations file as a side file",
      any(name.endswith(cec.CREATION_SUFFIX)
          for name in crt_protocol["chats"]["crt-1"]["side_files"]),
      str(crt_protocol["chats"]["crt-1"]["side_files"]))
crt_doc = json.load(open(os.path.join(
    CRT_DIR, crt_protocol["chats"]["crt-1"]["file"]), encoding="utf-8"))
check("the chat file counts the works in its metadata",
      crt_doc["metadata"]["creations"] == 4, str(crt_doc["metadata"]))
crt_side = json.load(open(os.path.join(
    CRT_DIR, [f for f in crt_files if f.endswith(cec.CREATION_SUFFIX)][0]),
    encoding="utf-8"))
check("the creations file leads back to chat, branch and turn",
      crt_side["creations"][0]["chat_uuid"] == "crt-1"
      and crt_side["creations"][0]["branch"] is None
      and crt_side["creations"][0]["turn"] == 1, str(crt_side["creations"])[:200])
check("the work content lives in the creations file",
      "WERKINHALT" in json.dumps(crt_side, ensure_ascii=False))
result = run("report", "--out", CRT_DIR)
check("report counts the carried creations",
      "Creations carried over (artifacts, created files, edits): 4"
      in result.stdout, result.stdout)


# ---------------------------------------------------------------------------
# File names
# ---------------------------------------------------------------------------

check("umlauts are transliterated in a slug",
      cec.slug("Dachlüken-Steuerung überprüfen") == "dachlueken-steuerung-ueberpruefen",
      cec.slug("Dachlüken-Steuerung überprüfen"))
check("a slug without usable characters gets a fallback",
      cec.slug("!!! ???") == "ohne-titel", cec.slug("!!! ???"))
check("a long title is cut", len(cec.slug("wort " * 40)) <= 50)

stem_a = cec.file_stem({"created_at": "2026-05-21T20:00:00Z",
                        "title": "Technische 2D-Zeichnung", "uuid": "aaaaaaaa-1"})
stem_b = cec.file_stem({"created_at": "2026-05-21T20:00:00Z",
                        "title": "Technische 2D-Zeichnung", "uuid": "bbbbbbbb-2"})
check("the stem carries date, slug and uuid",
      stem_a == "2026-05-21_technische-2d-zeichnung_aaaaaaaa", stem_a)
check("two chats with the same date AND title do not collide",
      stem_a != stem_b, f"{stem_a} vs {stem_b}")


# ---------------------------------------------------------------------------
# The protocol
# ---------------------------------------------------------------------------

PROT_DIR = os.path.join(WORK, "ziel")
FIXED_NOW = "2026-05-20T12:00:00+00:00"


def protocol():
    """Read the protocol the CLI wrote."""
    with open(os.path.join(PROT_DIR, cec.PROTOCOL_FILENAME),
              "r", encoding="utf-8") as handle:
        return json.load(handle)


result = run("convert", "--zip", ARCHIVE, "--out", PROT_DIR)
check("convert without a protocol refuses and says why",
      result.returncode == 1 and "Run 'list'" in result.stderr, result.stderr)

result = run("list", "--map", MAP_FILE, "--out", PROT_DIR,
             "--project", "Testprojekt")
check("CLI list exits 0", result.returncode == 0, result.stderr)
check("the protocol records every listed chat",
      len(protocol()["chats"]) == 3, str(protocol()["chats"].keys()))
check("a freshly listed chat waits to be converted",
      all(e["status"] == "listed" for e in protocol()["chats"].values()))
check("the project name is kept", protocol()["project"] == "Testprojekt")
check("list reports how many are waiting",
      "3 chat(s) waiting" in result.stdout, result.stdout)

result = run("convert", "--zip", ARCHIVE, "--out", PROT_DIR, "--now", FIXED_NOW)
check("CLI convert exits 0", result.returncode == 0, result.stderr)
check("convert writes the two mapped chats", "2 chat(s) written" in result.stdout,
      result.stdout)
check("convert names the listed chat that is not in the archive",
      "gibt-es-nicht" in result.stdout and "do not guess" in result.stdout,
      result.stdout)
check("convert prints the block for the project instructions",
      "in die Projektanweisungen einfügen" in result.stdout, result.stdout)

files = sorted(os.listdir(PROT_DIR))
check("a chat file was written per converted chat",
      sum(1 for f in files if f.endswith(".json")
          and f != cec.PROTOCOL_FILENAME
          and not f.endswith(cec.THINKING_SUFFIX)) == 2, str(files))
check("the file name follows date_slug_uuid",
      any(f.startswith("2026-05-01_linear_lin-1") for f in files), str(files))

with open(os.path.join(PROT_DIR, "2026-05-01_linear_lin-1.json"),
          "r", encoding="utf-8") as handle:
    document = json.load(handle)
check("the document follows §1.12: metadata plus messages",
      set(document) >= {"metadata", "messages"}, str(set(document)))
check("the §1.12 fields are present",
      set(document["metadata"]) >= {"created_at", "imported_at"},
      str(sorted(document["metadata"])))
check("roles are user and assistant",
      {m["role"] for m in document["messages"]} == {"user", "assistant"},
      str({m["role"] for m in document["messages"]}))
check("the source is recorded",
      document["metadata"]["source"] == "account-export")
check("imported_at is the timestamp that was handed in",
      document["metadata"]["imported_at"] == FIXED_NOW)
check("last_updated_at records the state the export rests on",
      document["metadata"]["last_updated_at"] == "2026-05-01T12:00:00.000000Z",
      document["metadata"]["last_updated_at"])

entry = protocol()["chats"]["lin-1"]
check("the protocol notes the file", entry["file"] == "2026-05-01_linear_lin-1.json")
check("the converted chat counts as exported", entry["status"] == "exported")
check("the protocol notes what the export rests on",
      entry["exported_updated_at"] == "2026-05-01T12:00:00.000000Z")
check("the chat that is not in the archive stays pending",
      protocol()["chats"]["gibt-es-nicht"]["status"] == "listed")


# ---------------------------------------------------------------------------
# Growth detection without touching a chat file
# ---------------------------------------------------------------------------

NEWER_LIST = (
    "<chat url='https://claude.ai/chat/lin-1' "
    "updated_at='2026-06-01T09:00:00.000000Z'>Content:\nTitle: Linear\n</chat>\n")
newer = os.path.join(WORK, "neuer.txt")
with open(newer, "w", encoding="utf-8") as handle:
    handle.write(NEWER_LIST)

result = run("list", "--map", newer, "--out", PROT_DIR)
check("a newer timestamp in the list marks the chat stale",
      protocol()["chats"]["lin-1"]["status"] == "stale",
      protocol()["chats"]["lin-1"]["status"])
check("list reports the stale chat", "1 now stale" in result.stdout, result.stdout)

result = run("diff", "--out", PROT_DIR)
check("CLI diff exits 0", result.returncode == 0, result.stderr)
check("diff names the stale chat and both timestamps",
      "STALE" in result.stdout and "lin-1" in result.stdout
      and "listed 2026-06-01" in result.stdout, result.stdout)
check("diff works without the archive and without reading a chat file",
      "1 stale" in result.stdout, result.stdout)

# An unchanged list must not disturb anything.
result = run("list", "--map", MAP_FILE, "--out", PROT_DIR)
check("an older timestamp does not un-stale a chat",
      protocol()["chats"]["lin-1"]["status"] == "stale")


# ---------------------------------------------------------------------------
# Thinking file, references and the losses report
# ---------------------------------------------------------------------------

THINK_DIR = os.path.join(WORK, "denken")
THINK_ARCHIVE = os.path.join(WORK, "denken.zip")
with zipfile.ZipFile(THINK_ARCHIVE, "w") as handle:
    handle.writestr("conversations.json", json.dumps([THINK, HOLLOW, BLOCKS]))
THINK_LIST = "".join(
    f"<chat url='https://claude.ai/chat/{uuid}' "
    f"updated_at='2026-05-10T12:00:00Z'></chat>\n"
    for uuid in ("thk-1", "hol-1", "blk-1"))
think_map = os.path.join(WORK, "denkliste.txt")
with open(think_map, "w", encoding="utf-8") as handle:
    handle.write(THINK_LIST)

run("list", "--map", think_map, "--out", THINK_DIR)
result = run("convert", "--zip", THINK_ARCHIVE, "--out", THINK_DIR,
             "--now", FIXED_NOW)
check("convert reports the thinking entries", "thinking entr" in result.stdout,
      result.stdout)

names = sorted(os.listdir(THINK_DIR))
think_file = next(n for n in names if n.endswith(cec.THINKING_SUFFIX))
chat_file = think_file[:-len(cec.THINKING_SUFFIX)] + ".json"
check("the thinking file shares the stem with its chat file",
      chat_file in names, f"{think_file} / {names}")

with open(os.path.join(THINK_DIR, think_file), "r", encoding="utf-8") as handle:
    thinking = json.load(handle)
with open(os.path.join(THINK_DIR, chat_file), "r", encoding="utf-8") as handle:
    chat = json.load(handle)

refs_in_chat = [m["thinking_ref"] for m in chat["messages"] if "thinking_ref" in m]
refs_in_file = [e["ref"] for e in thinking["thinking"]]
check("every reference in the chat file has an entry in the thinking file",
      set(refs_in_chat) == set(refs_in_file),
      f"{refs_in_chat} vs {refs_in_file}")
check("each thinking entry leads back to chat and turn",
      all(e["chat_uuid"] == "thk-1" and e["chat_file"] == chat_file
          and isinstance(e["turn"], int) for e in thinking["thinking"]),
      str(thinking["thinking"])[:150])
check("a main-path entry says it is not in a branch",
      all(e["branch"] is None for e in thinking["thinking"]),
      str([e["branch"] for e in thinking["thinking"]]))

# 'turn' restarts inside a branch, so only (branch, turn) identifies a place.
# Without the branch field a back-reference would be ambiguous -- found on real
# data, where one chat had turn 1 twice in its thinking file.
BRANCH_THINK = conv("bth-1", "Zweig mit Denken", [
    msg("g0", ROOT, "human", "Frage", "2026-05-12T10:00:00Z"),
    # main path: thinking sits at position 1 and 3
    msg("g1", "g0", "assistant", "", "2026-05-12T10:01:00Z", blocks=[
        thinking_block(LONG), {"type": "text", "text": "Hauptweg"}]),
    msg("g2", "g1", "human", "weiter", "2026-05-12T10:05:00Z"),
    msg("g3", "g2", "assistant", "", "2026-05-12T10:06:00Z", blocks=[
        thinking_block(LONG + "spaeter"), {"type": "text", "text": "und weiter"}]),
    # side branch off g1: its own thinking also lands at position 1
    msg("gA", "g1", "human", "verworfen", "2026-05-12T10:02:00Z"),
    msg("gB", "gA", "assistant", "", "2026-05-12T10:03:00Z", blocks=[
        thinking_block(LONG + "im Zweig"), {"type": "text", "text": "Nebenweg"}]),
])
branch_result = cec.conversation_record(BRANCH_THINK)
places = [(e["branch"], e["turn"]) for e in branch_result["thinking"]]
check("turn alone repeats between main path and branch",
      len({t for _, t in places}) < len(places), str(places))
check("branch plus turn is unique", len(set(places)) == len(places), str(places))
check("the branch entry names its branch number",
      any(b == 0 for b, _ in places), str(places))
check("the thinking text is in the thinking file, not in the chat file",
      LONG in json.dumps(thinking, ensure_ascii=False)
      and LONG not in json.dumps(chat, ensure_ascii=False))
check("a hollow chat gets no thinking file",
      not any("hol-1" in n and n.endswith(cec.THINKING_SUFFIX) for n in names),
      str(names))

hollow_file = next(n for n in names if "hol-1" in n
                   and not n.endswith(cec.THINKING_SUFFIX))
with open(os.path.join(THINK_DIR, hollow_file), "r", encoding="utf-8") as handle:
    hollow_doc = json.load(handle)
check("a hollow chat is written as deleted and without messages",
      hollow_doc["metadata"]["deleted"] is True and hollow_doc["messages"] == [],
      str(hollow_doc["metadata"])[:120])
check("a hollow chat is marked deleted in the protocol too",
      json.load(open(os.path.join(THINK_DIR, cec.PROTOCOL_FILENAME),
                     encoding="utf-8"))["chats"]["hol-1"]["status"] == "deleted")

# ---------------------------------------------------------------------------
# Replacing a chat has to clean up after itself
# ---------------------------------------------------------------------------

HYG_DIR = os.path.join(WORK, "hygiene")
HYG_UUID = "hyg-1"


def hygiene_archive(name, title, messages, updated):
    """Write a one-chat archive under a given title and timestamp."""
    path = os.path.join(WORK, name)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("conversations.json", json.dumps([
            conv(HYG_UUID, title, messages, updated=updated)]))
    return path


def hygiene_list(name, title, updated):
    """Write a chat list naming that title and timestamp."""
    path = os.path.join(WORK, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(f"<chat url='https://claude.ai/chat/{HYG_UUID}' "
                     f"updated_at='{updated}'>Content:\nTitle: {title}\n</chat>\n")
    return path


def hygiene_files():
    """Names in the hygiene directory, protocol excluded."""
    return sorted(n for n in os.listdir(HYG_DIR) if n != cec.PROTOCOL_FILENAME)


def hygiene_protocol():
    """The hygiene directory's protocol."""
    with open(os.path.join(HYG_DIR, cec.PROTOCOL_FILENAME),
              "r", encoding="utf-8") as handle:
        return json.load(handle)


# First version: a title, thinking and an attachment -- so all three files.
first = [
    dict(msg("y0", ROOT, "human", "Frage", "2026-06-01T10:00:00Z"),
         attachments=[{"file_name": "alt.py", "file_type": "text/x-python",
                       "file_size": 5, "extracted_content": "print(1)"}]),
    msg("y1", "y0", "assistant", "", "2026-06-01T10:01:00Z",
        blocks=[thinking_block(LONG), {"type": "text", "text": "Antwort"}]),
]
run("list", "--map", hygiene_list("hl1.txt", "Alter Titel",
                                  "2026-06-01T12:00:00Z"), "--out", HYG_DIR)
run("convert", "--zip", hygiene_archive("hv1.zip", "Alter Titel", first,
                                        "2026-06-01T12:00:00Z"),
    "--out", HYG_DIR, "--now", FIXED_NOW)
check("all three files exist after the first conversion",
      len(hygiene_files()) == 3, str(hygiene_files()))
check("the protocol records the side files",
      len(hygiene_protocol()["chats"][HYG_UUID]["side_files"]) == 2,
      str(hygiene_protocol()["chats"][HYG_UUID]))

# Second version: renamed, one turn longer, and WITHOUT thinking or attachment.
second = [
    msg("y0", ROOT, "human", "Frage", "2026-06-01T10:00:00Z"),
    msg("y1", "y0", "assistant", "Antwort", "2026-06-01T10:01:00Z"),
    msg("y2", "y1", "human", "Nachtrag", "2026-07-01T10:00:00Z"),
]
run("list", "--map", hygiene_list("hl2.txt", "Neuer Titel",
                                  "2026-07-01T12:00:00Z"), "--out", HYG_DIR)
result = run("convert", "--zip", hygiene_archive("hv2.zip", "Neuer Titel", second,
                                                 "2026-07-01T12:00:00Z"),
             "--out", HYG_DIR, "--now", FIXED_NOW)

# The name carries the title slug, so a rename changes the whole stem. Without
# cleanup the archive would hold two versions and a search would find both.
check("a renamed chat leaves exactly one file behind",
      hygiene_files() == ["2026-05-01_neuer-titel_hyg-1.json"],
      str(hygiene_files()))
check("convert says which files it removed",
      "replaced, removed" in result.stdout and "alter-titel" in result.stdout,
      result.stdout)
check("the vanished side files are gone from the protocol",
      hygiene_protocol()["chats"][HYG_UUID]["side_files"] == [],
      str(hygiene_protocol()["chats"][HYG_UUID]["side_files"]))
check("the new version really is the longer one",
      hygiene_protocol()["chats"][HYG_UUID]["turns"] == 3,
      str(hygiene_protocol()["chats"][HYG_UUID]["turns"]))

result = run("diff", "--out", HYG_DIR)
check("diff reports no orphan when the directory is clean",
      "ORPHANED" not in result.stdout, result.stdout)

# The other direction: a file nobody claims. Nothing else can notice this.
with open(os.path.join(HYG_DIR, "2020-01-01_fremd_deadbeef.json"), "w",
          encoding="utf-8") as handle:
    json.dump({"metadata": {}, "messages": []}, handle)
result = run("diff", "--out", HYG_DIR)
check("diff finds a file no protocol entry claims",
      "ORPHANED" in result.stdout and "fremd_deadbeef" in result.stdout,
      result.stdout)
check("diff warns against deleting an orphan blindly",
      "the protocol is the authority" in result.stdout, result.stdout)
check("the protocol itself is never reported as an orphan",
      cec.PROTOCOL_FILENAME not in result.stdout.split("ORPHANED")[1],
      result.stdout)

# A missing side file has to be reported as well, not just a missing chat file.
run("list", "--map", hygiene_list("hl3.txt", "Neuer Titel",
                                  "2026-08-01T12:00:00Z"), "--out", HYG_DIR)
run("convert", "--zip", hygiene_archive("hv3.zip", "Neuer Titel", first,
                                        "2026-08-01T12:00:00Z"),
    "--out", HYG_DIR, "--now", FIXED_NOW)
side = hygiene_protocol()["chats"][HYG_UUID]["side_files"][0]
os.unlink(os.path.join(HYG_DIR, side))
result = run("diff", "--out", HYG_DIR)
check("diff notices a missing side file, not only a missing chat file",
      "the file is gone" in result.stdout and side in result.stdout,
      result.stdout)

check("entry_files lists chat file and side files together",
      cec.entry_files({"file": "a.json", "side_files": ["b.json", "c.json"]})
      == ["a.json", "b.json", "c.json"])
check("entry_files copes with an entry that has neither",
      cec.entry_files({}) == [])


result = run("report", "--out", THINK_DIR)
check("CLI report exits 0", result.returncode == 0, result.stderr)
check("report names the hollow chat as unrecoverable",
      "unrecoverable" in result.stdout, result.stdout)
# Two from the fixture with thinking, one from the fixture with mixed blocks.
check("report counts the dropped thinking blocks",
      "Thinking blocks dropped as empty or too short: 3" in result.stdout,
      result.stdout)
check("report does not count kept thinking as a lost block type",
      "'thinking'" not in result.stdout, result.stdout)
check("report names the file that is mentioned by name only",
      "skript.py" in result.stdout and "name only" in result.stdout,
      result.stdout)
check("report lists the block types left out of the text",
      "tool_use" in result.stdout, result.stdout)

# ---------------------------------------------------------------------------
# The reconciliation bound: listed_at and created_after
# ---------------------------------------------------------------------------

# Two listing runs. The first knows one chat and has no earlier run to compare
# against; the second adds a chat, which can only have been created after the
# first run -- that is the only lower bound a chat list can ever supply.
BOUND_DIR = os.path.join(WORK, "schranke")
FIRST_RUN, SECOND_RUN = "2026-03-01T00:00:00+00:00", "2026-04-01T00:00:00+00:00"


def bound_list(name, uuids):
    """Write a chat list holding the given uuids."""
    path = os.path.join(WORK, name)
    with open(path, "w", encoding="utf-8") as handle:
        for uuid in uuids:
            handle.write(f"<chat url='https://claude.ai/chat/{uuid}' "
                         f"updated_at='2026-02-01T00:00:00Z'>Content:\n"
                         f"Title: Chat {uuid}\n</chat>\n")
    return path


def bound_protocol():
    """Read the protocol of the bound fixture."""
    with open(os.path.join(BOUND_DIR, cec.PROTOCOL_FILENAME),
              encoding="utf-8") as handle:
        return json.load(handle)


result = run("list", "--map", bound_list("schranke-1.txt", ["alt-1"]),
             "--out", BOUND_DIR, "--now", FIRST_RUN)
first = bound_protocol()
check("the first listing stamps listed_at",
      first["listed_at"] == FIRST_RUN, str(first.get("listed_at")))
check("a chat from the very first listing has no bound",
      first["chats"]["alt-1"]["created_after"] == "",
      repr(first["chats"]["alt-1"]["created_after"]))
check("the first run says an export must reach the project start",
      "project's own start date" in result.stdout, result.stdout)

result = run("list", "--map", bound_list("schranke-2.txt", ["alt-1", "neu-2"]),
             "--out", BOUND_DIR, "--now", SECOND_RUN)
second = bound_protocol()
check("the second listing moves listed_at forward",
      second["listed_at"] == SECOND_RUN, str(second.get("listed_at")))
check("the newly seen chat is bounded by the previous reconciliation",
      second["chats"]["neu-2"]["created_after"] == FIRST_RUN,
      repr(second["chats"]["neu-2"]["created_after"]))
check("the bound of an already known chat is NOT overwritten",
      second["chats"]["alt-1"]["created_after"] == "",
      repr(second["chats"]["alt-1"]["created_after"]))
check("the run names the date an export has to reach",
      FIRST_RUN[:19] in result.stdout and "earliest an export" in result.stdout,
      result.stdout)

# A third run that adds nothing must not disturb the bounds it already holds.
run("list", "--map", bound_list("schranke-3.txt", ["alt-1", "neu-2"]),
    "--out", BOUND_DIR, "--now", "2026-05-01T00:00:00+00:00")
third = bound_protocol()
check("a run without new chats leaves every bound alone",
      third["chats"]["neu-2"]["created_after"] == FIRST_RUN
      and third["chats"]["alt-1"]["created_after"] == "",
      str({u: e["created_after"] for u, e in third["chats"].items()}))
check("but it still moves listed_at forward",
      third["listed_at"] == "2026-05-01T00:00:00+00:00", third["listed_at"])

# convert fills the real created_at; the bound stays as the weaker fallback.
bound_zip = os.path.join(WORK, "schranke.zip")
with zipfile.ZipFile(bound_zip, "w") as handle:
    handle.writestr("conversations.json", json.dumps([conv("neu-2", "Chat neu-2", [
        msg("b0", ROOT, "human", "hallo", "2026-03-15T10:00:00Z")],
        created="2026-03-15T10:00:00.000000Z",
        updated="2026-03-15T11:00:00.000000Z")]))
run("convert", "--zip", bound_zip, "--out", BOUND_DIR, "--now", "T-BOUND")
fourth = bound_protocol()
check("convert supplies the real created_at",
      fourth["chats"]["neu-2"]["created_at"].startswith("2026-03-15"),
      fourth["chats"]["neu-2"]["created_at"])
check("and leaves created_after in place as the weaker fallback",
      fourth["chats"]["neu-2"]["created_after"] == FIRST_RUN,
      fourth["chats"]["neu-2"]["created_after"])
# The real date must sit inside the bound -- otherwise the bound was wrong.
check("the real created_at is consistent with the bound",
      fourth["chats"]["neu-2"]["created_at"] > FIRST_RUN)


# The project start comes in by hand and drives the reported window.
result = run("list", "--map", bound_list("schranke-4.txt", ["alt-1", "neu-2"]),
             "--out", BOUND_DIR, "--now", "2026-06-01T00:00:00+00:00",
             "--project-created", "2025-11-10")
fifth = bound_protocol()
check("list stores the hand-entered project start",
      fifth["project_created_at"] == "2025-11-10",
      str(fifth.get("project_created_at")))
check("and reports the date an export has to reach",
      "reach back to" in result.stdout, result.stdout)

# A project date later than a chat it supposedly contains must be flagged --
# typing the wrong project's date would silently shorten every window.
result = run("list", "--map", bound_list("schranke-5.txt", ["alt-1"]),
             "--out", BOUND_DIR, "--now", "2026-07-01T00:00:00+00:00",
             "--project-created", "2026-06-15")
check("an implausible project date is flagged on stderr",
      "cannot predate" in result.stderr, result.stderr or result.stdout)

# Without any bound at all, the run says so instead of guessing a window.
EMPTY_DIR = os.path.join(WORK, "ohne-schranke")
result = run("list", "--map", bound_list("schranke-6.txt", ["frisch-1"]),
             "--out", EMPTY_DIR, "--now", "2026-06-01T00:00:00+00:00")
check("with no bound at all the run asks for the project start",
      "no date bound at all" in result.stdout
      and "--project-created" in result.stdout, result.stdout)


# ---------------------------------------------------------------------------
# The prompt for step 2 of doku 1.5 -- getting the chat list at all
# ---------------------------------------------------------------------------

check("the mapping prompt exists and is non-empty",
      bool(cec.MAPPING_PROMPT.strip()))
check("it names the tool call, not just 'get me the chats'",
      "recent_chats" in cec.MAPPING_PROMPT
      and "sort_order" in cec.MAPPING_PROMPT, cec.MAPPING_PROMPT)
check("it insists on a codeblock -- the fix for the swallowed-tags incident",
      "codeblock" in cec.MAPPING_PROMPT.lower()
      or "Codeblock" in cec.MAPPING_PROMPT, cec.MAPPING_PROMPT)
check("it forbids reformatting into a table or numbered list",
      "keine Tabelle" in cec.MAPPING_PROMPT
      and "keine Nummerierung" in cec.MAPPING_PROMPT, cec.MAPPING_PROMPT)
check("the module docstring points at MAPPING_PROMPT by name",
      "MAPPING_PROMPT" in (cec.__doc__ or ""), cec.__doc__[:200])

# The prompt must actually produce input parse_chat_list accepts -- otherwise
# it is advice that does not match the parser it feeds.
SAMPLE_DUMP = ("<chat url='https://claude.ai/chat/aaaaaaaa-1111-2222-3333-"
              "444444444444' updated_at='2026-01-01T00:00:00Z'>\n"
              "Title: Testchat\n</chat>\n")
check("a dump shaped the way the prompt asks for parses correctly",
      len(cec.parse_chat_list(SAMPLE_DUMP)) == 1
      and cec.parse_chat_list(SAMPLE_DUMP)[0]["title"] == "Testchat")


shutil.rmtree(WORK, ignore_errors=True)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All checks passed.")
