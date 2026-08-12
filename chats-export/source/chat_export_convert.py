#!/usr/bin/env python3
"""Read a claude.ai account data export and make sense of its conversations.

Runs locally, never uploaded -- unlike ``chat_read_store.py`` it does not have
to be self-contained for a chat upload (doku 2.9 is about those).  Chapter 3.1
of ``implementation_doku.md`` holds the determinations this implements, chapter
2 the repo-wide ones; the numbers quoted below come from there.

    python3 chat_export_convert.py list    --map <dump> --out <dir> \
                                            [--project N] [--project-created DATE]
    python3 chat_export_convert.py convert --zip <export.zip> --out <dir>
    python3 chat_export_convert.py diff    --out <dir>
    python3 chat_export_convert.py report  --out <dir>
    python3 chat_export_convert.py analyse --zip <export.zip> [--map <dump>]

Getting the ``--map`` input is the one step this file cannot do for you: the
chat list only exists inside a claude.ai chat, in the *source* project, via
the built-in ``recent_chats`` tool -- no script, no upload, nothing to run
there. Ask for it verbatim, with the literal prompt kept as ``MAPPING_PROMPT``
below (module-level, printable): only a codeblock survives the markdown
renderer, the ``<chat ...>`` tags outside one are silently swallowed as HTML
(observed). Save the reply as a file and pass it as ``--map``.

``list`` comes first, always: it builds the protocol from a chat list, which is
the only place the project a chat belongs to can be learned. ``convert`` then
writes the chats the protocol is waiting for. ``diff`` reports the standing from
the protocol alone -- no archive, no chat file, not one character of chat text.
``report`` says what could not be carried over. ``analyse`` describes what the
reader makes of an archive without writing anything, which is a different
question than ``inspect_export.py`` answers: that one describes the raw export,
this one the *interpretation*.

DESIGN NOTES
------------
**The message tree.** Messages form a tree via ``parent_message_uuid``, not a
chain (doku 3.1.2). At a fork the path to the newest message in the whole tree
is followed. That rule was checked against all 20 forks of a three-month
export: it decides every one of them, and it disagrees with "largest subtree"
in exactly one case, which is a genuine tie of one descendant each. The
tempting alternative, "youngest child at the fork", is *wrong* -- in one
conversation the older child carries 29 messages and the younger is a dead end.

**Side branches are kept, duplicates are not.** A sibling whose text is
identical to the chosen one and which has no descendants is a resend, not
content: one conversation has fourteen such children with exactly 440
characters each. Those are counted, not stored. A duplicate *with* descendants
is kept regardless, because its subtree is not a duplicate.

**Text comes from the content blocks, not from ``text``.** The flat ``text``
field *contains the thinking*: 20.8 million characters against 11.3 million in
the text blocks, the difference being the reasoning. Taking it would flood the
archive with internal deliberation. Only text blocks contribute; ``tool_use``
and ``tool_result`` are counted so the loss stays visible, and whether they
should travel is still open (doku 3.1.8).

**Thinking goes into a file of its own.** It is not redundant -- only 9 % of its
vocabulary reappears in the answer -- so it is kept, but separately: a reader of
the conversation would otherwise carry 84 % of the archive's volume. Selection
is structural and never by content: empty ``thinking_hidden`` blocks and blocks
under 200 characters go, which is a third of the entries and 0.8 % of the
content. Trigger words would break at the first change of language.

**Hollow chats are deleted chats.** Messages present, no text anywhere. Verified
in the browser: they no longer exist. Nothing recovers them, so they are marked
rather than silently emptied.

**Up to four files per chat, not just the conversation.** Alongside the chat
file itself, ``convert`` writes ``.thinking.json`` (kept thinking blocks),
``.attachments.json`` (uploaded files whose content came through, tracked
separately from bare name-only references) and ``.creations.json`` (things the
assistant produced -- artifacts, generated files, code edits) whenever a chat
has any. All three are linked back to the conversation file by message UUID,
never by position, because branches make positional linking wrong.

**``protokoll.json`` is the one file that survives between runs.** It carries,
per chat: status, timestamps, and the file names ``convert`` wrote for it, so a
second run knows what to replace instead of duplicating. Two fields exist only
to answer "how far back must the next export reach": ``created_after``, set the
first time a chat is *seen* (not converted) to the timestamp of the previous
``list``, and ``project_created_at``, typed in by hand via ``--project-created``
after reading a project's own creation date off a probe export
(``inspect_export.py`` lists them). ``window_start()`` combines both with each
chat's own ``created_at`` once known, and ``list`` prints the result: the
earliest date an account export needs to cover everything still pending.

**``convert`` ends by printing ``INSTRUCTION_BLOCK``** -- a ready-made German
paragraph for the *target* project's own instructions, telling that
project's instance an archive exists and where, so it looks before asking.
``MAPPING_PROMPT`` above is its counterpart for the *source* side.

Every command that stamps a timestamp accepts ``--now`` to record a fixed one
instead of the clock -- for reproducible test runs, not for daily use.
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import os
import re
import sys
import tempfile
import zipfile
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONVERSATIONS_MEMBER = "conversations.json"
PROJECTS_PREFIX      = "projects/"

# The export writes the speaker as 'sender'; §1.12 of the working instructions
# wants 'user'/'assistant'.
ROLE_BY_SENDER = {"human": "user", "assistant": "assistant"}

# Blocks that carry conversation text. Everything else is counted, not stored.
TEXT_BLOCK_TYPES = ("text",)

# A thinking block below this length is a progress note, not a consideration.
# Measured (doku 3.1.1): blocks under 200 characters are a third of all entries
# but 0.8 % of the content, and only 2 % of them weigh anything up. Blocks with
# ``thinking_hidden`` are empty outright.
THINKING_MIN_CHARS = 200

PROTOCOL_FILENAME  = "protokoll.json"
PROTOCOL_VERSION   = 1
THINKING_SUFFIX    = ".thinking.json"
ATTACHMENT_SUFFIX  = ".attachments.json"
CREATION_SUFFIX    = ".creations.json"

# Tool calls whose input carries a work the AI produced -- an artifact, a
# created file, an edit. Selection by tool name and field is structural
# (doku 2.7); the yardstick numbers live in doku 3.1.1. Everything else in
# tool_use, and all of tool_result, is counted but not stored: 28.6 million
# characters of mostly foreign or duplicated material.
CREATION_TOOLS = ("artifacts", "create_file", "str_replace")

# untouched -> listed by 'list', exported/deleted by 'convert', stale when the
# chat list shows a newer timestamp than the export rests on.
STATUS_LISTED   = "listed"
STATUS_EXPORTED = "exported"
STATUS_STALE    = "stale"
STATUS_DELETED  = "deleted"

UMLAUTS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "ae",
                         "Ö": "oe", "Ü": "ue", "ß": "ss"})
SLUG_STRIP = re.compile(r"[^a-z0-9]+")
SLUG_MAX = 50

# 'Title:' line of a recent_chats block; the chat list supplies the project
# mapping, which conversations.json does not contain at all.
TITLE_LINE_PATTERN = re.compile(r"^\s*Title:\s*(.*)$", re.M)
CHAT_OPEN_PATTERN  = re.compile(r"<chat\b([^>]*)>")
CHAT_CLOSE_TAG     = "</chat>"
ATTR_PATTERN       = re.compile(r"([\w-]+)\s*=\s*['\"]([^'\"]*)['\"]")

# Zero-width characters seen in reported output; never wanted in a title.
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍﻿"))


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def clean_title(text: str) -> str:
    """Strip zero-width noise and surrounding whitespace from a title."""
    return text.translate(ZERO_WIDTH).strip()


def uuid_from_url(url: str) -> str:
    """Return the trailing path segment of a chat URL."""
    return url.rstrip("/").rsplit("/", 1)[-1]


def sort_key(message: dict[str, Any]) -> tuple[str, str]:
    """Order messages reproducibly: by time, then by uuid to break ties."""
    return (message.get("created_at") or "", message.get("uuid") or "")


def slug(title: str) -> str:
    """Turn a chat title into a filename part (doku 2.3)."""
    lowered = title.translate(UMLAUTS).lower()
    cleaned = SLUG_STRIP.sub("-", lowered).strip("-")
    return cleaned[:SLUG_MAX].strip("-") or "ohne-titel"


def file_stem(record: dict[str, Any]) -> str:
    """Return the shared stem of a chat's two files.

    The uuid segment is always present, not only on collision (doku 2.3): two
    chats really do share a date and a title in a real export, and a name that
    depends on what else happens to be converted in the same run would not be
    reproducible.
    """
    return (f"{(record.get('created_at') or '')[:10] or 'ohne-datum'}"
            f"_{slug(record.get('title') or '')}"
            f"_{(record.get('uuid') or '')[:8]}")


# ---------------------------------------------------------------------------
# Reading the archive
# ---------------------------------------------------------------------------

def load_member(archive: zipfile.ZipFile, name: str) -> Any:
    """Read one JSON member without extracting the archive."""
    with archive.open(name) as handle:
        return json.load(handle)


def load_conversations(archive: zipfile.ZipFile) -> list[dict[str, Any]]:
    """Return the conversations of an export archive."""
    if CONVERSATIONS_MEMBER not in archive.namelist():
        raise ValueError(f"{CONVERSATIONS_MEMBER} is missing from the archive")
    payload = load_member(archive, CONVERSATIONS_MEMBER)
    if not isinstance(payload, list):
        raise ValueError(f"{CONVERSATIONS_MEMBER} does not hold a list")
    return payload


def load_projects(archive: zipfile.ZipFile) -> list[dict[str, Any]]:
    """Return the project records; they carry instructions and knowledge docs.

    They contain no conversations at all -- the chats live only in
    ``conversations.json`` -- but the names are the only place a project name
    can be read from, which matters when output directories get named.
    """
    return [load_member(archive, name) for name in sorted(archive.namelist())
            if name.startswith(PROJECTS_PREFIX) and name.endswith(".json")]


# ---------------------------------------------------------------------------
# Message content
# ---------------------------------------------------------------------------

def message_text(message: dict[str, Any]) -> tuple[str, dict[str, int]]:
    """Assemble a message's text and report which blocks were left out.

    The flat ``text`` field is only a fallback: it disagrees with the content
    blocks in a third of all messages.  A message with no blocks at all but a
    non-empty ``text`` is taken at face value, because dropping it would lose
    content over a formality.
    """
    blocks = message.get("content") or []
    dropped: dict[str, int] = collections.Counter()
    parts = []
    for block in blocks:
        kind = block.get("type")
        if kind in TEXT_BLOCK_TYPES:
            parts.append(block.get("text") or "")
        elif kind == "thinking":
            # Accounted for by message_thinking, which keeps most of them in a
            # file of their own. Counting them here as well would report a loss
            # that did not happen.
            continue
        elif kind == "tool_use" and block.get("name") in CREATION_TOOLS:
            # Extracted by message_creations into the fourth file -- same
            # reasoning as the thinking: what travels is no loss.
            continue
        else:
            dropped[kind or "?"] += 1
    if not blocks:
        return (message.get("text") or ""), dict(dropped)
    return "".join(parts), dict(dropped)


def message_role(message: dict[str, Any]) -> str:
    """Map the export's ``sender`` to the role used in the output files."""
    return ROLE_BY_SENDER.get(message.get("sender") or "", "unknown")


def message_creations(message: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the works the AI produced in this message's tool calls.

    The counterpart of ``attachment_records``: there the user uploads, here
    the AI creates. For chats without an accompanying repo these are the only
    copies. Edits (``update``, ``str_replace``) are deltas without their base
    and say so via ``delta: true`` -- pretending they were whole documents
    would be worse than admitting the gap.
    """
    works = []
    for block in message.get("content") or []:
        if block.get("type") != "tool_use" or block.get("name") not in CREATION_TOOLS:
            continue
        tool = block.get("name")
        payload = block.get("input") or {}
        if tool == "artifacts":
            content = payload.get("content") or payload.get("new_str") or ""
            if not content:
                continue
            works.append({"kind": "artifact",
                          "command": payload.get("command") or "",
                          "id": payload.get("id") or "",
                          "title": payload.get("title") or "",
                          "delta": (payload.get("command") or "") == "update",
                          "content": content})
        elif tool == "create_file":
            content = payload.get("file_text") or ""
            if not content:
                continue
            works.append({"kind": "file",
                          "path": payload.get("path") or "",
                          "title": payload.get("description") or "",
                          "delta": False,
                          "content": content})
        else:  # str_replace
            if not (payload.get("new_str") or payload.get("old_str")):
                continue
            works.append({"kind": "edit",
                          "path": payload.get("path") or "",
                          "delta": True,
                          "old": payload.get("old_str") or "",
                          "content": payload.get("new_str") or ""})
    return works


def message_thinking(message: dict[str, Any]) -> tuple[list[str], int]:
    """Return the thinking worth keeping and the number of blocks discarded.

    Structural selection only, never by content (doku 2.7): trigger words are
    language-dependent and break the moment a chat switches language. The
    threshold was validated against an independent signal -- blocks that weigh
    something up have a median length of 2,537 characters, the rest 176 -- but
    that signal is a yardstick, not a filter, and does not appear here.
    """
    kept, dropped = [], 0
    for block in message.get("content") or []:
        if block.get("type") != "thinking":
            continue
        text = block.get("thinking") or ""
        if block.get("thinking_hidden") or len(text) < THINKING_MIN_CHARS:
            dropped += 1
            continue
        kept.append(text)
    return kept, dropped


def attachment_label(entry: dict[str, Any]) -> str:
    """Name an attachment, falling back to its type when the name is empty.

    22 attachments in a real export carry no ``file_name`` but several kilobytes
    of content, so a bare "?" would hide something worth having.
    """
    name = entry.get("file_name") or entry.get("name") or ""
    if name:
        return name
    kind = entry.get("file_type") or "unbekannt"
    return f"(ohne Namen, {kind})"


def file_references(message: dict[str, Any]) -> list[str]:
    """Return the names of files the export mentions but does not carry.

    ``files`` entries hold ``file_uuid`` and ``file_name`` and nothing else --
    those really are a named loss.  Not to be confused with ``attachments``,
    which do carry their text; see ``attachment_records``.
    """
    return [attachment_label(entry) for entry in (message.get("files") or [])]


def attachment_records(message: dict[str, Any]) -> tuple[list[dict[str, Any]],
                                                         list[str]]:
    """Return the attachments that carry content, and those that do not.

    ``attachments`` come with ``extracted_content``: 341 of them in a
    three-month export, none empty, 9.6 million characters in total, mostly
    Python and Markdown the user had uploaded.  That is frequently the *subject*
    of a conversation, so it is kept -- in a file of its own, like the thinking.
    """
    kept, without = [], []
    for entry in message.get("attachments") or []:
        content = entry.get("extracted_content") or ""
        if not content:
            without.append(attachment_label(entry))
            continue
        kept.append({"name":    attachment_label(entry),
                     "type":    entry.get("file_type") or "",
                     "size":    entry.get("file_size"),
                     "content": content})
    return kept, without


# ---------------------------------------------------------------------------
# The message tree
# ---------------------------------------------------------------------------

def child_map(messages: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group messages by their parent uuid, children in reproducible order."""
    children: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for message in messages:
        children[message.get("parent_message_uuid")].append(message)
    for kids in children.values():
        kids.sort(key=sort_key)
    return dict(children)


def main_path(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the path from the tree root to the newest message.

    Walking *up* from the newest message rather than down from the root is what
    makes the rule total: every fork is decided, because exactly one of its
    children lies on this path.  Checked against 20 real forks (see the design
    notes).  A cycle would be a corrupt export; the loop is bounded so a
    corrupt file cannot hang the tool.
    """
    if not messages:
        return []
    by_uuid = {message["uuid"]: message for message in messages}
    current = max(messages, key=sort_key)
    path: list[dict[str, Any]] = []
    seen: set[str] = set()
    while current is not None and current["uuid"] not in seen:
        seen.add(current["uuid"])
        path.append(current)
        current = by_uuid.get(current.get("parent_message_uuid"))
    path.reverse()
    return path


def subtree(head: dict[str, Any],
            children: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Return *head* and everything below it, in reproducible order."""
    collected, front = [], [head]
    while front:
        node = front.pop()
        collected.append(node)
        front.extend(children.get(node["uuid"], []))
    collected.sort(key=sort_key)
    return collected


def split_branches(messages: list[dict[str, Any]], path: list[dict[str, Any]]
                   ) -> tuple[list[list[dict[str, Any]]], int, list[dict[str, Any]]]:
    """Separate the side branches from the chosen path.

    Returns ``(branches, duplicates_skipped, orphans)``.  A branch is a whole
    subtree hanging off the path.  A childless sibling whose text equals the
    chosen message's text is a resend and is skipped; one with children is kept
    even so, because its subtree is not a duplicate.
    """
    children = child_map(messages)
    path_uuids = {message["uuid"] for message in path}
    chosen_at: dict[str | None, dict[str, Any]] = {
        message.get("parent_message_uuid"): message for message in path}

    branches: list[list[dict[str, Any]]] = []
    duplicates = 0
    claimed = set(path_uuids)
    for message in sorted(messages, key=sort_key):
        if message["uuid"] in claimed:
            continue
        parent = message.get("parent_message_uuid")
        if parent not in path_uuids and parent in {m["uuid"] for m in messages}:
            continue    # belongs to a branch that is collected via its head
        head_children = children.get(message["uuid"], [])
        sibling = chosen_at.get(parent)
        if (not head_children and sibling is not None
                and message_text(message)[0] == message_text(sibling)[0]):
            duplicates += 1
            claimed.add(message["uuid"])
            continue
        branch = subtree(message, children)
        branches.append(branch)
        claimed.update(node["uuid"] for node in branch)

    orphans = [m for m in messages if m["uuid"] not in claimed]
    return branches, duplicates, orphans


# ---------------------------------------------------------------------------
# Normalising one conversation
# ---------------------------------------------------------------------------

def render(messages: list[dict[str, Any]],
           branch: int | None = None) -> dict[str, Any]:
    """Turn messages into role/content records and collect what came off.

    The thinking of a message is deliberately *not* put into the record: it is
    handed back separately, keyed by the message uuid, because it goes into its
    own file.  Otherwise 84 % of the archive's volume would sit in every read of
    a conversation.
    """
    rendered, dropped, without, thinking = [], collections.Counter(), [], []
    attachments, creations, dropped_thinking = [], [], 0
    for index, message in enumerate(messages):
        text, blocks = message_text(message)
        dropped.update(blocks)
        without.extend(file_references(message))
        carried, nameless = attachment_records(message)
        without.extend(nameless)
        kept, discarded = message_thinking(message)
        dropped_thinking += discarded
        record = {"n": index, "role": message_role(message), "content": text}
        if carried:
            record["attachments_ref"] = message.get("uuid", "")
            attachments.append({"ref": message.get("uuid", ""), "branch": branch,
                                "turn": index, "files": carried})
        works = message_creations(message)
        if works:
            record["creations_ref"] = message.get("uuid", "")
            creations.append({"ref": message.get("uuid", ""), "branch": branch,
                              "turn": index, "works": works})
        if kept:
            # The reference is the message uuid: unique account-wide already,
            # so no identifier of our own has to be invented.
            record["thinking_ref"] = message.get("uuid", "")
            # 'turn' counts within its own sequence, so it repeats between the
            # main path and a branch. Only the pair (branch, turn) is unique,
            # and a back-reference has to be exact to be worth anything.
            thinking.append({"ref": message.get("uuid", ""), "branch": branch,
                             "turn": index, "blocks": kept})
        rendered.append(record)
    return {"messages": rendered, "dropped_blocks": dict(dropped),
            "attachments": attachments, "without_content": without,
            "creations": creations, "thinking": thinking,
            "dropped_thinking": dropped_thinking}


def conversation_record(conversation: dict[str, Any]) -> dict[str, Any]:
    """Normalise one exported conversation into what step 2 needs to write."""
    messages = conversation.get("chat_messages") or []
    warnings: list[str] = []

    path = main_path(messages)
    branches, duplicates, orphans = split_branches(messages, path)
    if orphans:
        warnings.append(f"{len(orphans)} message(s) hang from a parent that is "
                        "not in this conversation and were not placed")

    main = render(path)
    rendered = main["messages"]
    dropped = dict(main["dropped_blocks"])
    without = list(main["without_content"])
    attachments = list(main["attachments"])
    creations = list(main["creations"])
    thinking = list(main["thinking"])
    dropped_thinking = main["dropped_thinking"]

    branch_records = []
    for number, branch in enumerate(branches):
        side = render(branch, branch=number)
        for kind, count in side["dropped_blocks"].items():
            dropped[kind] = dropped.get(kind, 0) + count
        without.extend(side["without_content"])
        attachments.extend(side["attachments"])
        creations.extend(side["creations"])
        thinking.extend(side["thinking"])
        dropped_thinking += side["dropped_thinking"]
        branch_records.append({"messages": side["messages"]})

    text_total = sum(len(item["content"]) for item in rendered)
    text_total += sum(len(item["content"]) for record in branch_records
                      for item in record["messages"])
    unknown_roles = sum(1 for item in rendered if item["role"] == "unknown")
    if unknown_roles:
        warnings.append(f"{unknown_roles} message(s) carry an unknown sender")

    return {
        "uuid":          conversation.get("uuid", ""),
        "title":         clean_title(conversation.get("name") or ""),
        "created_at":    conversation.get("created_at", ""),
        "updated_at":    conversation.get("updated_at", ""),
        "messages":      rendered,
        "branches":      branch_records,
        "turns":         len(rendered),
        "message_count": len(messages),
        "chars":         text_total,
        "empty":         not messages,
        "deleted":       bool(messages) and text_total == 0,
        "dropped_blocks":      dropped,
        "dropped_duplicates":  duplicates,
        "dropped_thinking":    dropped_thinking,
        "thinking":            thinking,
        "creations":           creations,
        "attachments":         attachments,
        "attachments_without_content": without,
        "warnings":      warnings,
    }


# ---------------------------------------------------------------------------
# Writing the files
# ---------------------------------------------------------------------------

def write_json(payload: Any, path: str) -> None:
    """Write JSON via a temporary file in the same directory."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    handle_fd, temporary = tempfile.mkstemp(prefix=".write-", dir=directory)
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def entry_files(entry: dict[str, Any]) -> list[str]:
    """Return every file an existing protocol entry claims."""
    names = [entry.get("file") or ""] + list(entry.get("side_files") or [])
    return [name for name in names if name]


def remove_previous(out_dir: str, entry: dict[str, Any]) -> list[str]:
    """Delete the files a previous conversion of this chat left behind.

    Doku 2.6. Without this a renamed chat leaves a whole second file stem in place --
    the name carries the title slug -- and a side file that the new version no
    longer needs stays findable.  Neither breaks anything; the archive merely
    stops being trustworthy, which is worse.
    """
    removed = []
    for name in entry_files(entry):
        path = os.path.join(out_dir, name)
        if os.path.exists(path):
            os.unlink(path)
            removed.append(name)
    return removed


def chat_document(record: dict[str, Any], now: str,
                  source: str = "account-export") -> dict[str, Any]:
    """Build the chat file for one conversation, following doku 2.2.

    A hollow chat gets a document without messages and ``deleted: true``: the
    fact that it existed survives, without a blank transcript pretending to be
    a record of anything.
    """
    metadata = {
        "created_at":     record["created_at"] or "unknown",
        "imported_at":    now,
        "chat_uuid":      record["uuid"],
        "url":            f"https://claude.ai/chat/{record['uuid']}",
        "title":          record["title"],
        "source":         source,
        "last_updated_at": record["updated_at"],
        "turns":        record["turns"],
        # This path has no independent yardstick: the archive is all there is,
        # so completeness cannot be proven and is not claimed.
        "total_turns":  None,
        "complete":     None,
        "turns_missing": None,
        "deleted":      record["deleted"],
        "dropped_duplicates": record["dropped_duplicates"],
        "dropped_blocks":     record["dropped_blocks"],
        "dropped_thinking":   record["dropped_thinking"],
        # Files, not messages: one message can bring several along, and a
        # count of messages would understate what was carried.
        "attachments_with_content":    sum(len(entry["files"])
                                           for entry in record["attachments"]),
        "creations":    sum(len(entry["works"]) for entry in record["creations"]),
        "attachments_without_content": record["attachments_without_content"],
    }
    document: dict[str, Any] = {"metadata": metadata}
    if record["deleted"] or record["empty"]:
        document["messages"] = []
    else:
        document["messages"] = record["messages"]
        if record["branches"]:
            document["branches"] = record["branches"]
    # Always present, even empty: a constant shape is what makes two files from
    # the two routes comparable at all. 'branches' stays optional, because only
    # this route can ever see one -- read_conversation hands over a flat turn
    # list, so an empty list there would claim a finding it cannot make.
    document["warnings"] = record["warnings"]
    return document


def attachment_document(record: dict[str, Any], chat_file: str) -> dict[str, Any]:
    """Build the attachment file: the text of what was uploaded into the chat.

    Kept out of the conversation file for the same reason as the thinking --
    9.6 million characters against 11.3 million of conversation, so a reader
    would otherwise carry nearly double. The way back is the same too: the
    message uuid in ``ref``, plus chat, branch and turn.
    """
    entries = []
    for entry in record["attachments"]:
        entries.append({
            "ref":       entry["ref"],
            "chat_uuid": record["uuid"],
            "chat_file": chat_file,
            "branch":    entry["branch"],
            "turn":      entry["turn"],
            "files":     entry["files"],
        })
    return {"metadata": {"chat_uuid": record["uuid"],
                         "title": record["title"],
                         "chat_file": chat_file,
                         "entries": len(entries),
                         "files": sum(len(e["files"]) for e in entries)},
            "attachments": entries}


def creations_document(record: dict[str, Any], chat_file: str) -> dict[str, Any]:
    """Build the creations file: what the AI produced in this chat.

    Same mechanics as thinking and attachments -- ``ref`` is the message uuid,
    ``(branch, turn)`` the exact place. Deltas keep their ``delta: true``.
    """
    entries = []
    for entry in record["creations"]:
        entries.append({"ref": entry["ref"], "chat_uuid": record["uuid"],
                        "chat_file": chat_file, "branch": entry["branch"],
                        "turn": entry["turn"], "works": entry["works"]})
    return {"metadata": {"chat_uuid": record["uuid"], "title": record["title"],
                         "chat_file": chat_file, "entries": len(entries),
                         "works": sum(len(e["works"]) for e in entries)},
            "creations": entries}


def thinking_document(record: dict[str, Any], chat_file: str) -> dict[str, Any]:
    """Build the thinking file, every entry carrying its way back.

    ``ref`` is the message uuid, the same value the chat file writes into
    ``thinking_ref``; ``chat_uuid``, ``chat_file`` and ``turn`` lead back. Both
    directions exist so that a find can start on either side.
    """
    entries = []
    for entry in record["thinking"]:
        entries.append({
            "ref":       entry["ref"],
            "chat_uuid": record["uuid"],
            "chat_file": chat_file,
            "branch":    entry["branch"],
            "turn":      entry["turn"],
            "blocks":    entry["blocks"],
        })
    return {"metadata": {"chat_uuid": record["uuid"],
                         "title": record["title"],
                         "chat_file": chat_file,
                         "entries": len(entries)},
            "thinking": entries}


# ---------------------------------------------------------------------------
# The protocol: the one file besides the chats
# ---------------------------------------------------------------------------

def protocol_path(out_dir: str) -> str:
    """Return the path of the protocol inside an output directory."""
    return os.path.join(out_dir, PROTOCOL_FILENAME)


def load_protocol(out_dir: str) -> dict[str, Any]:
    """Load the protocol, or return an empty one.

    A missing protocol is not an error: it is the state before ``list`` has
    ever run, and only the caller knows whether that is expected.
    """
    path = protocol_path(out_dir)
    if not os.path.exists(path):
        return {"protocol_version": PROTOCOL_VERSION, "project": "",
                "project_created_at": "", "order": "", "listed_at": "",
                "chats": {}}
    with open(path, "r", encoding="utf-8") as handle:
        protocol = json.load(handle)
    protocol.setdefault("protocol_version", PROTOCOL_VERSION)
    protocol.setdefault("project", "")
    # The reading route records the direction of work here; this route does
    # not use it but must not lose it either -- one protocol, one schema.
    protocol.setdefault("order", "")
    # When the source project was last listed -- the reference point for the
    # created_after bound below.
    protocol.setdefault("listed_at", "")
    # The project's own start date, read off a probe export by hand (doku 1.5)
    # -- nothing in an archive links a conversation to a project, so no tool
    # can derive it.
    protocol.setdefault("project_created_at", "")
    protocol.setdefault("chats", {})
    for entry in protocol["chats"].values():
        entry.setdefault("side_files", [])
        entry.setdefault("created_after", "")
    return protocol


def save_protocol(out_dir: str, protocol: dict[str, Any]) -> None:
    """Write the protocol atomically."""
    protocol["protocol_version"] = PROTOCOL_VERSION
    write_json(protocol, protocol_path(out_dir))


def update_from_list(protocol: dict[str, Any],
                     records: list[dict[str, str]],
                     now: str = "") -> dict[str, int]:
    """Fold a chat list into the protocol and report what changed.

    This is what makes growth detectable without touching a single chat file:
    the list's ``updated_at`` against the timestamp the export rests on. A chat
    whose source moved on becomes ``stale`` and is fetched again; everything
    else stays untouched.

    *now* stamps the reconciliation. A chat seen here for the first time gets
    the **previous** reconciliation as ``created_after``: the source was listed
    then and did not contain this chat, so it was created later. That is the
    only lower bound available for a chat that has never been in an archive --
    the chat list carries no ``created_at`` (doku 2.4).
    """
    previous_listed = protocol.get("listed_at", "")
    counts = collections.Counter()
    for record in records:
        entry = protocol["chats"].get(record["uuid"])
        if entry is None:
            protocol["chats"][record["uuid"]] = {
                "title":       record.get("title", ""),
                "created_at":  "",
                "created_after": previous_listed,
                "listed_updated_at": record.get("updated_at", ""),
                "exported_updated_at": "",
                "turns":       0,
                "total_turns": None,
                "end_token":   "",
                "file":        "",
                "side_files":  [],
                "status":      STATUS_LISTED,
                "exported_at": "",
            }
            counts["new"] += 1
            continue
        entry["listed_updated_at"] = (record.get("updated_at", "")
                                      or entry.get("listed_updated_at", ""))
        if record.get("title") and not entry.get("title"):
            entry["title"] = record["title"]
        exported = entry.get("exported_updated_at") or ""
        listed = entry.get("listed_updated_at") or ""
        if entry["status"] == STATUS_EXPORTED and listed and listed > exported:
            entry["status"] = STATUS_STALE
            counts["stale"] += 1
        else:
            counts["unchanged"] += 1
    if now:
        protocol["listed_at"] = now
    return dict(counts)


def project_start_warnings(protocol: dict[str, Any]) -> list[str]:
    """Check the hand-entered project start against what the protocol knows.

    A date typed for the wrong project would silently shorten every export
    window from here on, so it is checked against the earliest date the
    protocol already holds: no chat of a project can predate the project.
    """
    start = protocol.get("project_created_at", "")
    if not start:
        return []
    known = [(entry.get("created_at") or entry.get("created_after") or "", uuid)
             for uuid, entry in protocol["chats"].items()]
    known = [(value, uuid) for value, uuid in known if value]
    if not known:
        return []
    earliest, uuid = min(known)
    if earliest[:10] < start[:10]:
        return [f"!! project_created_at is {start[:10]}, but chat {uuid[:8]} is "
                f"dated {earliest[:10]} -- a chat cannot predate its project. "
                "Wrong project's date, or the wrong project's chat list."]
    return []


def window_start(protocol: dict[str, Any]) -> dict[str, Any]:
    """Compute how far back an export has to reach to cover what is pending.

    The table in doku 2.4, as code. Every chat an export must cover contributes
    a lower bound on its own creation, from the best source available:

    * its ``created_at`` -- exact, but only a route that saw an archive has it;
    * its ``created_after`` -- exact too: the project was listed then and this
      chat was not in it, so it came later;
    * the project's own ``created_at`` -- no chat of a project can predate the
      project, so this bounds anything the first two cannot.

    The window start is the earliest of those bounds. A chat with none of the
    three is genuinely unbounded and forces a full export -- reported rather
    than papered over, because a window that is too short loses content
    silently while one that is too generous only costs download size.
    """
    project_start = protocol.get("project_created_at", "")
    pending = {uuid: entry for uuid, entry in protocol["chats"].items()
               if entry.get("status") in (STATUS_LISTED, STATUS_STALE)}
    bounds: dict[str, tuple[str, str]] = {}
    unbounded = []
    for uuid, entry in pending.items():
        if entry.get("created_at"):
            bounds[uuid] = (entry["created_at"], "created_at")
        elif entry.get("created_after"):
            bounds[uuid] = (entry["created_after"], "created_after")
        elif project_start:
            bounds[uuid] = (project_start, "project")
        else:
            unbounded.append(uuid)
    if not pending:
        return {"start": "", "source": "nothing-pending", "chats": [],
                "unbounded": []}
    if unbounded:
        return {"start": "", "source": "unbounded", "chats": [],
                "unbounded": sorted(unbounded)}
    start = min(value for value, _ in bounds.values())
    source = next(kind for value, kind in bounds.values() if value == start)
    return {"start": start, "source": source,
            "chats": sorted(u for u, (v, _) in bounds.items() if v == start),
            "unbounded": []}


# ---------------------------------------------------------------------------
# The chat list: the project mapping the export lacks
# ---------------------------------------------------------------------------

def parse_chat_list(raw_text: str) -> list[dict[str, str]]:
    """Parse a raw ``recent_chats`` dump into identity records.

    Only uuid, timestamp and title are taken; bodies are ignored. The list is
    the only place the project a chat belongs to can be learned -- a
    conversation in the export carries no project reference whatsoever.
    """
    records: list[dict[str, str]] = []
    matches = list(CHAT_OPEN_PATTERN.finditer(raw_text))
    for index, match in enumerate(matches):
        attributes = dict(ATTR_PATTERN.findall(match.group(1)))
        limit = (matches[index + 1].start() if index + 1 < len(matches)
                 else len(raw_text))
        body = raw_text[match.end():limit]
        closing = body.find(CHAT_CLOSE_TAG)
        if closing >= 0:
            body = body[:closing]
        uuid = (attributes.get("conversation_id", "")
                or uuid_from_url(attributes.get("url", "")))
        if not uuid:
            continue
        title = TITLE_LINE_PATTERN.search(body)
        records.append({
            "uuid":       uuid,
            "url":        attributes.get("url", ""),
            "updated_at": attributes.get("updated_at", ""),
            "title":      clean_title(title.group(1)) if title else "",
        })
    return records


def check_mapping(records: list[dict[str, str]],
                  conversations: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Split mapped uuids into those the archive knows and those it does not.

    A uuid has to be written out by hand somewhere along the way, and a typo
    would silently file a chat under the wrong project. Reporting the unknown
    ones turns that into a visible error.
    """
    known = {conversation.get("uuid") for conversation in conversations}
    hits = [record["uuid"] for record in records if record["uuid"] in known]
    misses = [record["uuid"] for record in records if record["uuid"] not in known]
    return {"known": hits, "unknown": misses}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

# Handed to the user verbatim (print it, or quote it in chat) before the first
# ``list`` of a source project: the chat list has to come from a claude.ai
# chat, and nothing here can fetch it. A codeblock is required -- outside one,
# the '<chat ...>' tags are HTML to the markdown renderer and vanish silently.
MAPPING_PROMPT = """\
Gib mir die vollständige Liste aller Chats dieses Projekts als Rohausgabe,
in einem einzigen Codeblock (drei Backticks, Sprache "text"). Rufe dazu
recent_chats mit sort_order='asc' und n=20 auf und blättere mit after
weiter, bis nichts Neues mehr kommt. Gib innerhalb des Blocks die
<chat ...>-Blöcke wörtlich und unverändert aus, wie das Werkzeug sie
liefert -- mit url und updated_at im Tag und der Title-Zeile darunter.
Kein Kommentar, keine Tabelle, keine Nummerierung, kein Text vor oder nach
dem Block."""


INSTRUCTION_BLOCK = """\
--- ab hier in die Projektanweisungen einfügen ---

Im Projektwissen liegt ein Archiv früherer Chats dieses Projekts: eine
JSON-Datei je Chat mit den Redebeiträgen, dazu je eine `.thinking.json` mit den
Überlegungen, die zu einer Antwort führten. Die Datei `protokoll.json` sagt,
welche Chats vorliegen und auf welchem Stand.

Bevor du zu etwas nachfragst, das früher schon besprochen worden sein könnte,
sieh im Archiv nach. Ein Treffer nennt Datum und Titel des Chats -- benutze das
in deiner Antwort, damit nachvollziehbar bleibt, woher die Auskunft kommt.
Findest du nichts, sag das ausdrücklich, statt zu vermuten.

--- Ende des Einschubs ---
"""


def cmd_list(args: argparse.Namespace) -> int:
    """Create or update the protocol from one or more chat lists."""
    records: list[dict[str, str]] = []
    for path in args.map:
        with open(path, "r", encoding="utf-8") as handle:
            records.extend(parse_chat_list(handle.read()))
    if not records:
        print("No <chat ...> blocks found in the given dump(s).", file=sys.stderr)
        return 1

    protocol = load_protocol(args.out)
    if args.project:
        protocol["project"] = args.project
    if args.project_created:
        protocol["project_created_at"] = args.project_created
    previous_listed = protocol.get("listed_at", "")
    now = args.now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    counts = update_from_list(protocol, records, now)
    save_protocol(args.out, protocol)

    print(f"{len(records)} chat(s) listed: {counts.get('new', 0)} new, "
          f"{counts.get('stale', 0)} now stale, "
          f"{counts.get('unchanged', 0)} unchanged.")
    print(f"{len(protocol['chats'])} chat(s) in {protocol_path(args.out)}")
    pending = [uuid for uuid, entry in protocol["chats"].items()
               if entry["status"] in (STATUS_LISTED, STATUS_STALE)]
    print(f"{len(pending)} chat(s) waiting to be converted." if pending
          else "Nothing waiting -- every listed chat is already exported.")
    for line in project_start_warnings(protocol):
        print(line, file=sys.stderr)
    window = window_start(protocol)
    if window["source"] == "unbounded":
        print(f"{len(window['unbounded'])} pending chat(s) have no date bound at "
              "all -- give the project's start date with --project-created "
              "(read it off a probe export, doku 1.5), or export everything.")
    elif window["start"]:
        print(f"An export has to reach back to {window['start'][:10]} to cover "
              f"everything pending (from {window['source']}).")
    if counts.get("new") and previous_listed:
        print(f"The {counts['new']} new chat(s) were created after "
              f"{previous_listed[:19]} -- that is the earliest an export has "
              "to reach to cover them.")
    elif counts.get("new") and not protocol.get("project_created_at"):
        print("No earlier reconciliation to bound the new chats: an export has "
              "to reach back to the project's own start date (doku 3.1.1).")
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    """Convert the chats the protocol is waiting for out of an archive."""
    protocol = load_protocol(args.out)
    if not protocol["chats"]:
        print(f"No protocol in {args.out}. Run 'list' with a chat list first -- "
              "without it there is no way to know which chats belong to this "
              "project.", file=sys.stderr)
        return 1

    archive = zipfile.ZipFile(args.zip)
    conversations = {c.get("uuid"): c for c in load_conversations(archive)}
    now = args.now or datetime.datetime.now(datetime.timezone.utc).isoformat()

    wanted = [uuid for uuid, entry in protocol["chats"].items()
              if entry["status"] in (STATUS_LISTED, STATUS_STALE)]
    missing = [uuid for uuid in wanted if uuid not in conversations]
    written = 0
    for uuid in wanted:
        conversation = conversations.get(uuid)
        if conversation is None:
            continue
        record = conversation_record(conversation)
        entry = protocol["chats"][uuid]
        record["title"] = record["title"] or entry.get("title", "")
        stem = file_stem(record)
        chat_name = f"{stem}.json"

        # Aufraeumen vor dem Schreiben, nicht danach: der Stamm kann sich
        # geaendert haben (Titel im Slug), und eine Nebendatei kann wegfallen.
        removed = remove_previous(args.out, entry)

        side_files = []
        write_json(chat_document(record, now), os.path.join(args.out, chat_name))
        if record["thinking"]:
            side_files.append(stem + THINKING_SUFFIX)
            write_json(thinking_document(record, chat_name),
                       os.path.join(args.out, side_files[-1]))
        if record["attachments"]:
            side_files.append(stem + ATTACHMENT_SUFFIX)
            write_json(attachment_document(record, chat_name),
                       os.path.join(args.out, side_files[-1]))
        if record["creations"]:
            side_files.append(stem + CREATION_SUFFIX)
            write_json(creations_document(record, chat_name),
                       os.path.join(args.out, side_files[-1]))

        entry.update({
            "title":       record["title"],
            "created_at":  record["created_at"],
            "exported_updated_at": record["updated_at"],
            "turns":       record["turns"],
            "file":        chat_name,
            "side_files":  side_files,
            "status":      STATUS_DELETED if record["deleted"] else STATUS_EXPORTED,
            "exported_at": now,
        })
        written += 1
        marks = []
        if record["deleted"]:
            marks.append("hollow, deleted at the source")
        if record["thinking"]:
            marks.append(f"{len(record['thinking'])} thinking entr(ies)")
        if record["attachments"]:
            files = sum(len(e["files"]) for e in record["attachments"])
            marks.append(f"{files} attachment(s) with content")
        if record["creations"]:
            works = sum(len(e["works"]) for e in record["creations"])
            marks.append(f"{works} creation(s)")
        if record["branches"]:
            marks.append(f"{len(record['branches'])} branch(es)")
        stale_names = [name for name in removed if name != chat_name
                       and name not in side_files]
        if stale_names:
            marks.append("replaced, removed " + ", ".join(stale_names))
        print(f"  {chat_name}  {record['turns']} turn(s)"
              + ("  | " + "; ".join(marks) if marks else ""))

    save_protocol(args.out, protocol)
    print()
    print(f"{written} chat(s) written to {args.out}")
    if missing:
        print(f"{len(missing)} chat(s) are listed but not in this archive:")
        for uuid in missing:
            print(f"  {uuid}  {protocol['chats'][uuid].get('title', '')!r}")
        print("  Either the export predates them, or a uuid was mistyped. They "
              "stay pending; do not guess.")
    if written:
        print()
        print(INSTRUCTION_BLOCK)
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    """Report the standing from the protocol alone -- no archive, no chat files."""
    protocol = load_protocol(args.out)
    if not protocol["chats"]:
        print(f"No protocol in {args.out}. Nothing has been listed yet.")
        return 0

    groups = collections.defaultdict(list)
    for uuid, entry in protocol["chats"].items():
        groups[entry["status"]].append((uuid, entry))

    print(f"Protocol: {protocol_path(args.out)}")
    if protocol.get("project"):
        print(f"Project : {protocol['project']}")
    print(f"Chats   : {len(protocol['chats'])} known -- "
          + ", ".join(f"{len(v)} {k}" for k, v in sorted(groups.items())))
    for status, label in ((STATUS_STALE, "STALE -- the source moved on, fetch again"),
                          (STATUS_LISTED, "WAITING -- listed, not yet converted"),
                          (STATUS_DELETED, "DELETED at the source -- hollow, "
                                           "unrecoverable")):
        if not groups.get(status):
            continue
        print()
        print(label)
        for uuid, entry in sorted(groups[status],
                                  key=lambda item: item[1].get("created_at", "")):
            print(f"  {uuid}  {entry.get('title', '')[:44]!r}"
                  + (f"  listed {entry['listed_updated_at'][:19]} vs exported "
                     f"{entry['exported_updated_at'][:19]}"
                     if status == STATUS_STALE else ""))

    missing_files = []
    for uuid, entry in protocol["chats"].items():
        if entry["status"] != STATUS_EXPORTED:
            continue
        for name in entry_files(entry):
            if not os.path.exists(os.path.join(args.out, name)):
                missing_files.append((uuid, name))
    if missing_files:
        print()
        print("EXPORTED but the file is gone -- convert again or restore it")
        for uuid, name in missing_files:
            print(f"  {name}  {uuid}")

    # The other direction, and the only place it can be noticed: a file that no
    # entry claims. A renamed chat used to leave its whole old stem behind, and
    # nothing said so -- the archive just quietly held two versions.
    claimed = {PROTOCOL_FILENAME}
    for entry in protocol["chats"].values():
        claimed.update(entry_files(entry))
    orphans = sorted(name for name in os.listdir(args.out)
                     if name.endswith(".json") and name not in claimed) \
        if os.path.isdir(args.out) else []
    if orphans:
        print()
        print("ORPHANED -- no protocol entry claims these; a search would still "
              "find them")
        for name in orphans:
            print(f"  {name}")
        print("  Either they are left over from an earlier naming, or the "
              "protocol was lost.")
        print("  Check before deleting: the protocol is the authority, not the "
              "directory.")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Report what the conversion could not carry over."""
    if not os.path.isdir(args.out):
        print(f"No such directory: {args.out}", file=sys.stderr)
        return 1

    totals = collections.Counter()
    lines: list[str] = []
    for name in sorted(os.listdir(args.out)):
        if not name.endswith(".json") or name == PROTOCOL_FILENAME \
                or name.endswith(THINKING_SUFFIX) \
                or name.endswith(ATTACHMENT_SUFFIX) \
                or name.endswith(CREATION_SUFFIX):
            continue
        with open(os.path.join(args.out, name), "r", encoding="utf-8") as handle:
            document = json.load(handle)
        meta = document.get("metadata") or {}
        marks = []
        if meta.get("deleted"):
            totals["deleted"] += 1
            marks.append("hollow: deleted at the source, unrecoverable")
        if meta.get("dropped_duplicates"):
            totals["duplicates"] += meta["dropped_duplicates"]
            marks.append(f"{meta['dropped_duplicates']} resend(s) skipped")
        if meta.get("dropped_thinking"):
            totals["thinking"] += meta["dropped_thinking"]
            marks.append(f"{meta['dropped_thinking']} empty/short thinking "
                         "block(s) dropped")
        for kind, count in (meta.get("dropped_blocks") or {}).items():
            totals[f"block:{kind}"] += count
        if meta.get("attachments_with_content"):
            totals["carried"] += meta["attachments_with_content"]
        if meta.get("creations"):
            totals["creations"] += meta["creations"]
        if meta.get("attachments_without_content"):
            names = meta["attachments_without_content"]
            totals["attachments"] += len(names)
            marks.append(f"{len(names)} file(s) mentioned by name only: "
                         + ", ".join(names[:3])
                         + (" …" if len(names) > 3 else ""))
        for warning in document.get("warnings") or []:
            marks.append(warning)
        if document.get("branches"):
            side = sum(len(b["messages"]) for b in document["branches"])
            totals["branches"] += len(document["branches"])
            marks.append(f"{len(document['branches'])} side branch(es) kept, "
                         f"{side} message(s)")
        if marks:
            lines.append(f"  {name}")
            lines += [f"      {mark}" for mark in marks]

    print(f"Losses and peculiarities in {args.out}")
    print()
    print("\n".join(lines) if lines else "  nothing to report")
    print()
    print(f"Hollow chats (content gone for good): {totals['deleted']}")
    print(f"Resends skipped: {totals['duplicates']}")
    print(f"Thinking blocks dropped as empty or too short: {totals['thinking']}")
    print(f"Side branches kept: {totals['branches']}")
    print(f"Attachments carried over with their content: {totals['carried']}")
    print(f"Creations carried over (artifacts, created files, edits): "
          f"{totals['creations']}")
    print(f"Files mentioned by name only, never in the export: "
          f"{totals['attachments']}")
    blocks = {key[6:]: value for key, value in totals.items()
              if key.startswith("block:")}
    print(f"Block types left out of the text: {blocks or 'none'}")
    return 0


def cmd_analyse(args: argparse.Namespace) -> int:
    """Report what the reader made of an archive."""
    archive = zipfile.ZipFile(args.zip)
    conversations = load_conversations(archive)
    projects = load_projects(archive)

    selected = None
    if args.map:
        records: list[dict[str, str]] = []
        for path in args.map:
            with open(path, "r", encoding="utf-8") as handle:
                records.extend(parse_chat_list(handle.read()))
        mapping = check_mapping(records, conversations)
        selected = set(mapping["known"])
        print(f"Mapping: {len(records)} chat(s) listed, "
              f"{len(mapping['known'])} found in the archive, "
              f"{len(mapping['unknown'])} unknown")
        for uuid in mapping["unknown"]:
            print(f"  !! not in this archive: {uuid}")
        if mapping["unknown"]:
            print("     Either the export predates these chats, or a uuid was "
                  "mistyped. Do not guess -- check before converting.")
        print()

    print(f"Archive: {len(conversations)} conversation(s), "
          f"{len(projects)} project record(s)")
    print()

    totals = collections.Counter()
    for conversation in conversations:
        record = conversation_record(conversation)
        if selected is not None and record["uuid"] not in selected:
            continue
        totals["chats"] += 1
        totals["turns"] += record["turns"]
        totals["chars"] += record["chars"]
        totals["branches"] += len(record["branches"])
        totals["duplicates"] += record["dropped_duplicates"]
        totals["deleted"] += int(record["deleted"])
        totals["empty"] += int(record["empty"])
        totals["attachments"] += len(record["attachments_without_content"])
        totals["carried"] += sum(len(e["files"]) for e in record["attachments"])
        for kind, count in record["dropped_blocks"].items():
            totals[f"block:{kind}"] += count

        marks = []
        if record["deleted"]:
            marks.append("DELETED (hollow)")
        if record["empty"]:
            marks.append("no messages")
        if record["branches"]:
            side = sum(len(b["messages"]) for b in record["branches"])
            marks.append(f"{len(record['branches'])} branch(es), {side} msg")
        if record["dropped_duplicates"]:
            marks.append(f"{record['dropped_duplicates']} resend(s) skipped")
        for warning in record["warnings"]:
            marks.append(warning)
        print(f"  {record['created_at'][:10]}  {record['turns']:>4} turns  "
              f"{record['chars']:>8} ch  {record['uuid'][:8]}  "
              f"{record['title'][:40]!r}"
              + ("  | " + "; ".join(marks) if marks else ""))

    print()
    print(f"Totals: {totals['chats']} chat(s), {totals['turns']} turns on the "
          f"chosen paths, {totals['chars']} chars")
    print(f"  side branches: {totals['branches']}, "
          f"resends skipped: {totals['duplicates']}")
    print(f"  hollow (deleted): {totals['deleted']}, "
          f"without messages: {totals['empty']}")
    print(f"  attachments carried with content: {totals['carried']}, "
          f"mentioned by name only: {totals['attachments']}")
    blocks = {key[6:]: value for key, value in totals.items()
              if key.startswith("block:")}
    print(f"  block types left out: {blocks or 'none'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Assemble the command line interface."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="create or update the protocol from a "
                                         "chat list")
    p_list.add_argument("--map", action="append", required=True,
                        help="raw recent_chats dump; repeatable")
    p_list.add_argument("--out", required=True, help="output directory")
    p_list.add_argument("--project", default="", help="name of the source project")
    p_list.add_argument("--project-created", default="", dest="project_created",
                        help="the source project's own creation date, read off "
                             "a probe export (inspect_export.py)")
    p_list.add_argument("--now", default="",
                        help="timestamp to record instead of the clock")
    p_list.set_defaults(func=cmd_list)

    p_convert = sub.add_parser("convert", help="convert the pending chats")
    p_convert.add_argument("--zip", required=True, help="export archive")
    p_convert.add_argument("--out", required=True, help="output directory")
    p_convert.add_argument("--now", default="",
                           help="timestamp to record instead of the clock")
    p_convert.set_defaults(func=cmd_convert)

    p_diff = sub.add_parser("diff", help="report the standing from the protocol")
    p_diff.add_argument("--out", required=True, help="output directory")
    p_diff.set_defaults(func=cmd_diff)

    p_report = sub.add_parser("report", help="report what could not be carried "
                                            "over")
    p_report.add_argument("--out", required=True, help="output directory")
    p_report.set_defaults(func=cmd_report)

    p_analyse = sub.add_parser("analyse",
                               help="report what the reader makes of an archive")
    p_analyse.add_argument("--zip", required=True, help="export archive")
    p_analyse.add_argument("--map", action="append", default=[],
                           help="raw recent_chats dump; repeatable")
    p_analyse.set_defaults(func=cmd_analyse)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
