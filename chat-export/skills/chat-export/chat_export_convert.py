#!/usr/bin/env python3
"""Read a claude.ai account data export and make sense of its conversations.

Doku 2.9 binds it: this docstring is the whole operating manual, because
Claude Code reads it and not necessarily the implementation doc, and
``tests/test_docstrings.py`` guards that.  Chapter 3.1
of ``implementation_doku.md`` holds the determinations this implements, chapter
2 the repo-wide ones; the numbers quoted below come from there.

    python3 chat_export_convert.py list    --map <dump> | --web <bundle> --out <dir> \
                                            [--project N] [--project-created DATE]
    python3 chat_export_convert.py convert --zip <export.zip> | --bundle <file> --out <dir>
    python3 chat_export_convert.py diff    --out <dir>
    python3 chat_export_convert.py report  --out <dir>
    python3 chat_export_convert.py analyse --zip <export.zip> [--map <dump>]

**Two sources, one converter.** Chats reach this script either from an account
export archive (``--zip``) or from a *web bundle* (``--bundle``): the file a
browser step writes after reading claude.ai's own endpoints. Both carry the
same conversation fields, so only the container differs -- ``load_bundle``,
``bundle_records`` and ``bundle_conversations`` unwrap it, and from
``conversation_record`` on the code is shared. The bundle's chat list also
brings ``created_at`` per chat, which ``--map`` never had; that is why
``list --web`` needs no sounding export to bound its window. What differs in
the *output* is one field: the chat file declares its provenance as
``SOURCE_WEB`` instead of ``SOURCE_EXPORT``, which vorgabe 2.5 lists among the
five metadata fields allowed to differ. Everything else matches file for file,
and ``tests/test_export_convert.py`` compares the two ways to make sure.

Getting the ``--map`` input is the one step this file cannot do for you: the
chat list only exists inside a claude.ai chat, in the *source* project, via
the built-in ``recent_chats`` tool -- no script, no upload, nothing to run
there. Ask for it **in a chat created for that purpose, and delete that chat
afterwards**: ``recent_chats`` never lists the chat it is called from, so the
asking chat is absent from its own listing -- and therefore from the protocol
and the archive, with nothing reporting the gap. A throwaway chat makes that
harmless; a working chat would silently drop out. Ask for it verbatim, with
the literal prompt kept as ``MAPPING_PROMPT``
below (module-level, printable): only a codeblock survives the markdown
renderer, the ``<chat ...>`` tags outside one are silently swallowed as HTML
(observed). Save the reply as a file and pass it as ``--map``.

``list`` comes first, always: it builds the protocol from a chat list, which is
the only place the project a chat belongs to can be learned. ``convert`` then
writes the chats the protocol is waiting for. ``diff`` reports the standing from
the protocol alone -- no archive, no chat file, not one character of chat text
-- including how far back the next export has to reach.

``list`` also looks the other way round: a chat the protocol knows and the
fresh list no longer offers is counted, named and explained by
``VANISHED_NOTE`` -- deleted at the source, moved to another project, or a
list that was not paged to the end. The three cannot be told apart from here,
so **nothing is removed**; the protocol keeps the chat and its files. The same
sentence stands in the comparison yardstick
``tests/wegegleichheit_referenz.py`` and is guarded against drift by
``tests/test_wegegleichheit.py``.
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
archive with internal deliberation. Three cases, not two: text blocks make up
the conversation; a ``tool_use`` whose input carries a work goes into the
creations file (below); everything else in ``tool_use`` and all of
``tool_result`` is counted but never stored -- 28.6 million characters of
mostly foreign or duplicated material, which would be ballast (doku 3.1.3).

**Thinking goes into a file of its own.** It is not redundant -- only 9 % of its
vocabulary reappears in the answer -- so it is kept, but separately: inline, it
would add 84 % on top of the conversation itself, so every read of a chat would
carry close to twice the text. Selection is structural and never by content:
empty ``thinking_hidden`` blocks and blocks under 200 characters go, which is a
third of the entries and 0.8 % of the content. Trigger words would break at the
first change of language.

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
chat's own ``created_at`` once known, and ``window_lines()`` puts it in words
for both ``list`` and ``diff`` -- one wording, because two commands phrasing
the same calculation is how a report and its preview drift apart. The result
is the earliest date an account export needs to cover everything still
pending.

**Timestamps are compared through ``is_newer``, never as plain strings.** The
sources disagree on notation for the same instant -- a chat list ends on
``+00:00``, an archive on ``Z`` -- and they differ in fractional precision. A
raw string comparison happens to work for the identical instant only because
``+`` sorts before ``Z``, and it gets the order wrong as soon as the fractions
differ. ``is_newer`` and the sort key ``utc_key`` behind it are the single
place that decides this, so no caller can write the comparison the wrong way
round; ``window_start`` sorts its bounds through the same key.

**A source older than the chat list does not settle a chat.** ``convert``
writes the file either way -- it is what that source holds -- but leaves the
entry ``stale`` and says so, because otherwise converting a stale-marked chat
from an outdated archive would reset ``exported_updated_at`` and make ``diff``
report nothing pending: a reconciliation claimed but never done. The realistic
mishap is several export ZIPs in one download folder.

**``convert`` ends by printing an instruction block** -- a ready-made German
paragraph the user pastes into the *target* project, telling that project's
instance an archive exists and where, so it looks before asking.
``MAPPING_PROMPT`` above is its counterpart for the *source* side.

``INSTRUCTION_BLOCKS`` holds one wording per target and ``--target`` picks it:
``repo`` for a Claude Code repository (the default), ``knowledge`` for
claude.ai project knowledge, ``home`` for ``~/.claude/projects/...``. They
differ in the two things the block exists to say -- where the archive is and
how the instance reaches it (Grep and Read on paths, versus project knowledge)
-- and the ``home`` one adds that the directory sits outside the working
directory and has to be made accessible to the session first. The files
written are the same for all three; doku 2.10 is about those, not about this
console output. The flag changes nothing but the wording. Path and file kinds
are filled in from the run itself, so the block never announces an
``.attachments.json`` that was not written.

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
import textwrap
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

# What both routes say when the protocol knows a chat the fresh list no longer
# offers. Held word for word in tests/wegegleichheit_referenz.py too and
# guarded by tests/test_wegegleichheit.py: the yardstick must not import from
# this file (vorgabe 2.5), and this project has twice watched one side of such
# a pair grow while the other stood still.
VANISHED_NOTE = """\
NOTE: {count} chat(s) in the protocol are not in this list.
  Deleted at the source, moved out of the project -- or the list was not paged
  to the end. Check before concluding anything; nothing is removed automatically."""


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

def utc_key(value: str) -> str:
    """Return a timestamp in one comparable form, whatever shape it arrived in.

    The sources disagree on notation for the same instant: a chat list ends its
    timestamps with ``+00:00``, an export archive with ``Z``, and a project
    start typed in by hand is a bare date. Comparing those as plain strings
    happens to work today only because ``+`` sorts before ``Z`` in ASCII -- for
    the *same* instant. It breaks as soon as the fractional precision differs:
    ``…00.5+00:00`` sorts before ``…00Z`` although it is later.

    Anything unparseable is returned unchanged rather than guessed at, and an
    empty value stays empty -- callers rely on the falsiness.
    """
    if not value:
        return ""
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        moment = datetime.datetime.fromisoformat(text)
    except ValueError:
        return text
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=datetime.timezone.utc)
    return moment.astimezone(datetime.timezone.utc).isoformat(
        timespec="microseconds")


def is_newer(candidate: str, reference: str) -> bool:
    """True if ``candidate`` is strictly later than ``reference``.

    The one place the comparison lives, so no caller can write it the wrong way
    round or forget the normalisation. An empty candidate is never newer.
    """
    if not candidate:
        return False
    return utc_key(candidate) > utc_key(reference)


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
# The web bundle -- the second way in
# ---------------------------------------------------------------------------

BUNDLE_CONVERSATIONS = "conversations"
BUNDLE_CHATS = "chats"

# What a chat file declares as its provenance (vorgabe 2.2). The value has to
# follow the container it came out of: a chat fetched from the web endpoints is
# not an export, and an archive that claimed otherwise would misstate where its
# content is from.
SOURCE_EXPORT = "account-export"
SOURCE_WEB = "web-api"


def load_bundle(path: str) -> dict[str, Any]:
    """Read a web bundle: the file the browser step writes.

    Layout -- both payload keys optional, so one fetch writes one file::

        {"fetched_at": "...", "organization": "...",
         "conversations": [{"uuid": ..., "name": ..., "created_at": ...,
                            "updated_at": ...}, ...],
         "chats":         [<conversation carrying chat_messages>, ...]}

    ``conversations`` feeds ``list --web``, ``chats`` feeds
    ``convert --bundle``.  The chat objects carry the same field names as the
    archive's, so everything below ``conversation_record`` is shared with the
    zip way: the two ways are equal *by construction* here, not merely by test
    (vorgabe 2.5).
    """
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} does not hold a JSON object")
    return payload


def bundle_records(bundle: dict[str, Any]) -> list[dict[str, str]]:
    """Turn a bundle's chat list into the records ``update_from_list`` takes.

    Unlike a ``recent_chats`` dump this list carries ``created_at`` per chat --
    the one bound the older way never had, and the reason this route needs no
    project start date from outside (doku 1.5).
    """
    entries = bundle.get(BUNDLE_CONVERSATIONS)
    if not isinstance(entries, list):
        raise ValueError(f"the bundle carries no {BUNDLE_CONVERSATIONS!r} list")
    records = []
    for entry in entries:
        uuid = (entry.get("uuid") or "").strip()
        if not uuid:
            continue
        records.append({
            "uuid":       uuid,
            "title":      clean_title(entry.get("name") or ""),
            "updated_at": entry.get("updated_at") or "",
            "created_at": entry.get("created_at") or "",
        })
    return records


def bundle_conversations(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a bundle's full conversations, shaped like the archive's."""
    chats = bundle.get(BUNDLE_CHATS)
    if not isinstance(chats, list):
        raise ValueError(f"the bundle carries no {BUNDLE_CHATS!r} list")
    return chats


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
    """Return the names of files this message mentions but does not carry.

    ``files`` entries hold ``file_uuid`` and ``file_name`` and nothing else, so
    they look like a loss -- but the two arrays are **not disjoint**. A text
    upload is recorded twice: once under ``files`` as the file object, once
    under ``attachments`` with its extracted text. Measured on a three-month
    export, 319 of 524 ``files`` entries have their content sitting in the same
    message, so reporting all of them as lost overstates the loss by more than
    double.

    A name is therefore only returned when no attachment of this message
    carries content under it. The join is by name because that is the only key
    the two arrays share: ``files`` has a ``file_uuid``, ``attachments`` has
    none. Where the name is missing on the attachment side -- 22 in that export
    -- the join cannot see the pair and the file is reported anyway; doku 1.6
    carries that residue rather than letting the code guess.
    """
    covered = {entry.get("file_name")
               for entry in (message.get("attachments") or [])
               if entry.get("extracted_content") and entry.get("file_name")}
    return [attachment_label(entry) for entry in (message.get("files") or [])
            if (entry.get("file_name") or "") not in covered]


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
    own file.  Inline it would add 84 % on top of the conversation itself, so
    every read of a chat would carry close to twice the text.
    """
    rendered, dropped, without, thinking = [], collections.Counter(), [], []
    attachments, creations, dropped_thinking = [], [], 0
    for index, message in enumerate(messages):
        text, blocks = message_text(message)
        dropped.update(blocks)
        carried, nameless = attachment_records(message)
        # One entry per name and message: a file that shows up as a
        # content-less attachment *and* as a files entry is one loss, not two.
        # Deduplicated per message, not across the chat -- the same name in two
        # messages is two references and stays two.
        without.extend(dict.fromkeys(file_references(message) + nameless))
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
    then and did not contain this chat, so it was created later. For a
    ``recent_chats`` dump that is the only lower bound to be had, because such
    a list carries no ``created_at`` (doku 2.4). A record that *does* carry one
    -- the web list does (``bundle_records``) -- sets it outright, and an entry
    still missing it gets it filled in on a later pass; ``created_after`` then
    only remains as the weaker fallback it always was.
    """
    previous_listed = protocol.get("listed_at", "")
    counts = collections.Counter()
    for record in records:
        entry = protocol["chats"].get(record["uuid"])
        if entry is None:
            protocol["chats"][record["uuid"]] = {
                "title":       record.get("title", ""),
                "created_at":  record.get("created_at", ""),
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
        if record.get("created_at") and not entry.get("created_at"):
            entry["created_at"] = record["created_at"]
        exported = entry.get("exported_updated_at") or ""
        listed = entry.get("listed_updated_at") or ""
        if entry["status"] == STATUS_EXPORTED and is_newer(listed, exported):
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
    start = min((value for value, _ in bounds.values()), key=utc_key)
    source = next(kind for value, kind in bounds.values() if value == start)
    return {"start": start, "source": source,
            "chats": sorted(u for u, (v, _) in bounds.items() if v == start),
            "unbounded": []}


def window_lines(protocol: dict[str, Any]) -> list[str]:
    """State the window in words, for every command that has a protocol.

    One wording for all callers on purpose. ``list`` reports it right after a
    listing run, ``diff`` when looking at the standing without fetching a fresh
    list -- and two commands phrasing the same calculation in their own words
    is exactly how a report and its preview drift apart.
    """
    window = window_start(protocol)
    if window["source"] == "unbounded":
        return [f"{len(window['unbounded'])} pending chat(s) have no date bound "
                "at all -- give the project's start date with --project-created "
                "(read it off a probe export, doku 1.5), or export everything."]
    if window["start"]:
        return [f"An export has to reach back to {window['start'][:10]} to "
                f"cover everything pending (from {window['source']})."]
    return []


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


# One text per target, because the three differ in exactly the two things the
# block exists to say: where the archive is and how the instance reaches it
# (doku 1.3). The files themselves stay identical everywhere -- vorgabe 2.10 is
# about those, not about this console output. ``{where}`` takes the real output
# path, ``{files}`` the kinds actually written; both are filled in by
# ``instruction_block`` so the block never promises a file that is not there.
INSTRUCTION_BLOCKS = {
    "repo": """\
--- ab hier in die CLAUDE.md des Zielprojekts einfügen ---

Unter `{where}` liegt ein Archiv früherer Chats dieses Projekts: {files}

Bevor du zu etwas nachfragst, das früher schon besprochen worden sein könnte,
sieh mit `Grep` im Archiv nach und lies den Treffer mit `Read`. Ein Treffer
nennt Datum und Titel des Chats -- benutze das in deiner Antwort, damit
nachvollziehbar bleibt, woher die Auskunft kommt. Findest du nichts, sag das
ausdrücklich, statt zu vermuten.

--- Ende des Einschubs ---
""",
    "knowledge": """\
--- ab hier in die Projektanweisungen einfügen ---

Im Projektwissen liegt ein Archiv früherer Chats dieses Projekts: {files}

Bevor du zu etwas nachfragst, das früher schon besprochen worden sein könnte,
sieh im Archiv nach. Ein Treffer nennt Datum und Titel des Chats -- benutze das
in deiner Antwort, damit nachvollziehbar bleibt, woher die Auskunft kommt.
Findest du nichts, sag das ausdrücklich, statt zu vermuten.

--- Ende des Einschubs ---
""",
    "home": """\
--- ab hier in die CLAUDE.md des Zielprojekts einfügen ---

Unter `{where}` liegt ein Archiv früherer Chats dieses Projekts: {files}

Der Ordner liegt außerhalb des Arbeitsverzeichnisses. Die Sitzung erreicht ihn
nur, wenn er ihr als zusätzliches Verzeichnis freigegeben ist -- ist er das
nicht, sag es, statt das Archiv für leer zu halten.

Bevor du zu etwas nachfragst, das früher schon besprochen worden sein könnte,
sieh mit `Grep` im Archiv nach und lies den Treffer mit `Read`. Ein Treffer
nennt Datum und Titel des Chats -- benutze das in deiner Antwort, damit
nachvollziehbar bleibt, woher die Auskunft kommt. Findest du nichts, sag das
ausdrücklich, statt zu vermuten.

--- Ende des Einschubs ---
""",
}


# What each file kind is called in the block, in reading order.
FILE_KIND_WORDS = [
    (THINKING_SUFFIX,   "je eine `.thinking.json` mit den Überlegungen, die zu "
                        "einer Antwort führten"),
    (ATTACHMENT_SUFFIX, "je eine `.attachments.json` mit dem Inhalt "
                        "hochgeladener Dateien"),
    (CREATION_SUFFIX,   "je eine `.creations.json` mit dem, was die KI erzeugt "
                        "hat -- Artefakte, Dateien, Änderungen"),
]


def instruction_block(target: str, out_dir: str, protocol: dict[str, Any]) -> str:
    """Build the paragraph the user pastes into the target project.

    The file kinds come from the protocol rather than from a fixed list: a run
    that produced no attachments must not announce an ``.attachments.json``,
    or the instance goes looking for something that is not there.
    """
    present = {suffix for entry in protocol["chats"].values()
               for name in entry.get("side_files") or []
               for suffix, _ in FILE_KIND_WORDS if name.endswith(suffix)}
    parts = ["eine JSON-Datei je Chat mit den Redebeiträgen"]
    parts += [words for suffix, words in FILE_KIND_WORDS if suffix in present]
    files = ", ".join(parts) + (". Die Datei `protokoll.json` sagt, welche "
                                "Chats vorliegen und auf welchem Stand.")
    text = INSTRUCTION_BLOCKS[target].format(where=out_dir, files=files)
    # Rewrapped paragraph by paragraph, because the substitutions make the
    # first one arbitrarily long and the block is pasted into a CLAUDE.md or
    # into project instructions, where one endless line reads badly. Long
    # words stay whole so a path is never broken across lines.
    return "\n\n".join(
        textwrap.fill(paragraph, width=78, break_long_words=False,
                      break_on_hyphens=False)
        for paragraph in text.split("\n\n"))


def cmd_list(args: argparse.Namespace) -> int:
    """Create or update the protocol from one or more chat lists."""
    if not args.map and not args.web:
        print("Give a chat list: --map <recent_chats dump> or --web <bundle>.",
              file=sys.stderr)
        return 1
    records: list[dict[str, str]] = []
    for path in args.map:
        with open(path, "r", encoding="utf-8") as handle:
            records.extend(parse_chat_list(handle.read()))
    for path in args.web:
        records.extend(bundle_records(load_bundle(path)))
    # An empty result here is not an error: a project can genuinely hold no
    # chats yet, and that has to write a protocol too, not abort -- the
    # source being unreachable or misspelled would already have failed above,
    # in open() or in bundle_records()/load_bundle().

    protocol = load_protocol(args.out)
    if args.project:
        protocol["project"] = args.project
    if args.project_created:
        protocol["project_created_at"] = args.project_created
    previous_listed = protocol.get("listed_at", "")
    now = args.now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    counts = update_from_list(protocol, records, now)
    save_protocol(args.out, protocol)

    # The comparison in the other direction: chats the protocol knows and this
    # list no longer offers. Reported, never removed -- vorgabe 2.4.
    listed_now = {record["uuid"] for record in records}
    vanished = [uuid for uuid in protocol["chats"] if uuid not in listed_now]

    print(f"{len(records)} chat(s) listed: {counts.get('new', 0)} new, "
          f"{counts.get('stale', 0)} now stale, "
          f"{counts.get('unchanged', 0)} unchanged"
          + (f", {len(vanished)} no longer listed." if vanished else "."))
    print(f"{len(protocol['chats'])} chat(s) in {protocol_path(args.out)}")
    if vanished:
        print()
        print(VANISHED_NOTE.format(count=len(vanished)))
        for uuid in vanished:
            entry = protocol["chats"][uuid]
            print(f"  {uuid}  {entry.get('title', '')[:44]!r}"
                  f"  [{entry.get('status', '')}]")
    pending = [uuid for uuid, entry in protocol["chats"].items()
               if entry["status"] in (STATUS_LISTED, STATUS_STALE)]
    print(f"{len(pending)} chat(s) waiting to be converted." if pending
          else "Nothing waiting -- every listed chat is already exported.")
    for line in project_start_warnings(protocol):
        print(line, file=sys.stderr)
    for line in window_lines(protocol):
        print(line)
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

    if bool(args.zip) == bool(args.bundle):
        print("Give exactly one source: --zip <export.zip> or --bundle <file>.",
              file=sys.stderr)
        return 1
    if args.zip:
        source, declared = "archive", SOURCE_EXPORT
        found = load_conversations(zipfile.ZipFile(args.zip))
    else:
        source, declared = "bundle", SOURCE_WEB
        found = bundle_conversations(load_bundle(args.bundle))
    conversations = {c.get("uuid"): c for c in found}
    now = args.now or datetime.datetime.now(datetime.timezone.utc).isoformat()

    wanted = [uuid for uuid, entry in protocol["chats"].items()
              if entry["status"] in (STATUS_LISTED, STATUS_STALE)]
    missing = [uuid for uuid in wanted if uuid not in conversations]
    behind_names: list[str] = []
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
        write_json(chat_document(record, now, declared),
                   os.path.join(args.out, chat_name))
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

        # A source older than what the list already reported does not settle
        # the chat: converting the wrong archive -- an earlier export still
        # sitting in the download folder -- would otherwise claim a
        # reconciliation that never happened, and 'diff' would report nothing
        # pending. The entry stays stale so the next run fetches it again.
        behind = is_newer(entry.get("listed_updated_at") or "",
                          record["updated_at"])
        if record["deleted"]:
            settled = STATUS_DELETED
        elif behind:
            settled = STATUS_STALE
        else:
            settled = STATUS_EXPORTED

        entry.update({
            "title":       record["title"],
            "created_at":  record["created_at"],
            "exported_updated_at": record["updated_at"],
            "turns":       record["turns"],
            "file":        chat_name,
            "side_files":  side_files,
            "status":      settled,
            "exported_at": now,
        })
        written += 1
        if behind and not record["deleted"]:
            behind_names.append(record["uuid"])
        marks = []
        if record["deleted"]:
            marks.append("hollow, deleted at the source")
        if behind and not record["deleted"]:
            marks.append("STILL STALE -- this source is older than the list")
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
    if behind_names:
        print(f"{len(behind_names)} chat(s) came from a source OLDER than the "
              "chat list and stay stale:")
        for uuid in behind_names:
            entry = protocol["chats"][uuid]
            print(f"  {uuid}  {entry.get('title', '')!r}")
            print(f"      list says {entry.get('listed_updated_at', '')}, "
                  f"this source {entry.get('exported_updated_at', '')}")
        print("  The file was written -- it is what this source holds -- but "
              "the chat is not settled. Fetch the current state, most likely "
              "from a newer export than the one just used.")
    if missing:
        print(f"{len(missing)} chat(s) are listed but not in this {source}:")
        for uuid in missing:
            print(f"  {uuid}  {protocol['chats'][uuid].get('title', '')!r}")
        print("  Either this source does not reach them -- an export predating "
              "them, a fetch that left them out -- or a uuid was mistyped. They "
              "stay pending; do not guess.")
    if written:
        print()
        print(instruction_block(args.target, args.out, protocol))
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

    # The same window statement 'list' makes, available without fetching a
    # fresh chat list: 'what is still missing' and 'how far back must the next
    # export reach' are one question asked twice.
    lines = window_lines(protocol)
    if lines:
        print()
        for line in lines:
            print(line)
    for line in project_start_warnings(protocol):
        print(line, file=sys.stderr)

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

    # The kept thinking blocks are counted from the side files, not from the
    # conversation metadata: that carries only ``dropped_thinking``, and adding
    # a "kept" field would change the file format for both routes (vorgabe 2.2,
    # 2.5) for the sake of one report line.
    for name in sorted(os.listdir(args.out)):
        if not name.endswith(THINKING_SUFFIX):
            continue
        with open(os.path.join(args.out, name), "r", encoding="utf-8") as handle:
            document = json.load(handle)
        totals["thinking_kept"] += sum(len(entry.get("blocks") or [])
                                       for entry in document.get("thinking") or [])

    print(f"Losses and peculiarities in {args.out}")
    print()
    print("\n".join(lines) if lines else "  nothing to report")
    print()
    print(f"Hollow chats (content gone for good): {totals['deleted']}")
    print(f"Resends skipped: {totals['duplicates']}")
    print(f"Thinking blocks carried over: {totals['thinking_kept']}")
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
        totals["creations"] += sum(len(e["works"]) for e in record["creations"])
        totals["thinking_kept"] += sum(len(e["blocks"]) for e in record["thinking"])
        totals["thinking_dropped"] += record["dropped_thinking"]
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
    print(f"  thinking blocks carried: {totals['thinking_kept']}, "
          f"dropped as empty or too short: {totals['thinking_dropped']}")
    print(f"  creations carried (artifacts, created files, edits): "
          f"{totals['creations']}")
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
    p_list.add_argument("--web", action="append", default=[],
                        help="web bundle carrying a chat list; alternative to "
                             "--map, and it brings created_at per chat")
    p_list.add_argument("--map", action="append", default=[],
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
    p_convert.add_argument("--zip", default="", help="export archive")
    p_convert.add_argument("--bundle", default="",
                           help="web bundle carrying full chats; alternative "
                                "to --zip")
    p_convert.add_argument("--out", required=True, help="output directory")
    p_convert.add_argument("--target", default="repo",
                           choices=sorted(INSTRUCTION_BLOCKS),
                           help="where the archive will be read: 'repo' (a "
                                "Claude Code repository, the default), "
                                "'knowledge' (claude.ai project knowledge) or "
                                "'home' (~/.claude/projects/...). Picks the "
                                "wording of the closing instruction block and "
                                "nothing else")
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
