#!/usr/bin/env python3
"""The second implementation of the chat file format -- the yardstick for Vorgabe 2.5.

``test_wegegleichheit.py`` measures the converter against this module: same
chat in, same document out. Without a second implementation the converter
would be the only yardstick of itself, and every format change would pass by
definition. That is the whole reason this file exists.

**It is not a route and never will be.** It descends from the abandoned read
route (``implementation_doku.md`` 1.7), which fetched a chat page by page from
a tool the platform withdrew on 18 August 2026. What survived here is only
what the comparison needs: parsing a handed-over page into turns, building the
chat document, and keeping the protocol. The command line, the fetch loop and
the operating instructions for an instance are gone -- they described a way
nobody can walk.

**Deliberately independent.** This module imports nothing from
``chat_export_convert.py`` and holds its own copies of the small helpers, down
to the slug rules and the window table. Sharing code would make the two sides
agree by construction and the test worthless. The duplication is the point,
not an oversight -- and ``VANISHED_NOTE`` below is checked for equality
against the converter's copy for exactly that reason.

    python3 tests/test_wegegleichheit.py

WHAT IT PROVIDES
----------------
* ``parse_pages`` / ``merge_page`` / ``new_store`` -- turn a rendered
  transcript into an ordered store of turns, the shape the withdrawn tool
  handed over.
* ``build_export`` -- the chat document per Vorgabe 2.2, with the metadata
  fields the comparison walks field by field.
* ``new_state`` / ``blank_entry`` / ``update_state`` / ``set_chat_status`` --
  the protocol per Vorgabe 2.4, so the comparison covers the protocol too and
  not just the chat file.
* ``record_export`` -- write the document and note it in the protocol, the
  counterpart of what the converter does at the end of a run.
* ``window_start`` / ``project_start_warnings`` -- the window calculation of
  Vorgabe 2.4, held twice on purpose: the test runs one shared table of cases
  through both implementations so they cannot drift apart on it.
* ``file_stem`` -- the naming rule of Vorgabe 2.3. This side cannot know a
  chat's creation date, so its stem falls back to ``ohne-datum``; that is one
  of the documented differences, not a defect.

Fields this side cannot know carry ``null`` rather than a guess, and
``source`` says ``read_conversation`` -- the provenance of the shape it
reproduces. Both are among the five metadata fields Vorgabe 2.5 allows to
differ.
"""

from __future__ import annotations

import datetime
import html
import json
import os
import re
import tempfile
from typing import Any

SCHEMA_VERSION       = 1

STATE_FILENAME       = "protokoll.json"

PROTOCOL_VERSION     = 1

# What both routes say when the protocol knows a chat the fresh list no longer
# offers. Held word for word in chat_export_convert.py too and guarded by
# tests/test_wegegleichheit.py: this module must not import from the converter
# (vorgabe 2.5), or it would stop being a yardstick -- and this project has
# twice watched one side of such a pair grow while the other stood still.
VANISHED_NOTE = """\
NOTE: {count} chat(s) in the protocol are not in this list.
  Deleted at the source, moved out of the project -- or the list was not paged
  to the end. Check before concluding anything; nothing is removed automatically."""

# The shared vocabulary of Vorgabe 2.4. 'started' is this route's own --
# partially read; the zip route always writes a chat whole. 'stale' is set by
# 'map' when the source moved on; 'deleted' only ever by hand, because this
# route cannot tell a deleted chat from an inaccessible one.
CHAT_STATUSES = ("listed", "started", "exported", "stale", "deleted")

# Opening tag of a page; attributes are parsed order-independently so that an
# added attribute cannot break the parser.
CHAT_OPEN_PATTERN = re.compile(r"<chat\b([^>]*)>")

CHAT_CLOSE_TAG    = "</chat>"

ATTR_PATTERN      = re.compile(r"([\w-]+)\s*=\s*['\"]([^'\"]*)['\"]")

TITLE_PATTERN     = re.compile(r"<title>(.*?)</title>", re.S)

TURN_PATTERN      = re.compile(r"<turn\b([^>]*)>(.*?)</turn>", re.S)

# Speaker label at the start of a turn.  Both spellings are accepted: the
# read tool was seen to write them out, the search tools abbreviate.
LABEL_PATTERN = re.compile(r"^(Human|Assistant|H|A):[ \t]*")

LABEL_ROLES   = {"H": "user", "Human": "user",
                 "A": "assistant", "Assistant": "assistant"}

# Zero-width characters observed in reported output; harmless but they must
# not end up inside a stored title.
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍﻿"))

UMLAUTS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "ae",
                         "Ö": "oe", "Ü": "ue", "ß": "ss"})

SLUG_STRIP = re.compile(r"[^a-z0-9]+")

SLUG_MAX = 50

def slug(title: str) -> str:
    """Turn a chat title into a filename part (doku 2.3).

    Deliberately duplicated from chat_export_convert.py: this module must not
    import from the converter (vorgabe 2.5), and the equality of the two
    implementations is guarded by tests/test_wegegleichheit.py.
    """
    lowered = title.translate(UMLAUTS).lower()
    cleaned = SLUG_STRIP.sub("-", lowered).strip("-")
    return cleaned[:SLUG_MAX].strip("-") or "ohne-titel"

def file_stem(store: dict[str, Any]) -> str:
    """Return the file stem per doku 2.3.

    This route never knows a chat's creation date -- read_conversation does
    not supply one -- so the date segment is honestly 'ohne-datum' rather
    than a guess from updated_at, which moves with every later message.
    """
    return f"ohne-datum_{slug(store.get('title') or '')}_{store['chat_uuid'][:8]}"

def uuid_from_url(url: str) -> str:
    """Return the trailing path segment of a chat URL."""
    return url.rstrip("/").rsplit("/", 1)[-1]

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

def _write_json_atomic(payload: Any, path: str, prefix: str) -> None:
    """Write *payload* as JSON via a temporary file in the same directory."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    handle_fd, temporary = tempfile.mkstemp(prefix=prefix, dir=directory)
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise

def split_chat_blocks(raw_text: str) -> list[tuple[dict[str, str], str, list[str]]]:
    """Split a dump into ``(attributes, body, warnings)`` per ``<chat>`` block.

    A dump may hold several pages, and may hold pages of different chats; the
    caller sorts that out.  A missing closing tag is tolerated -- the block
    then runs to the next opening tag or to the end -- because a truncated
    paste is far more likely than a malformed tool output, and refusing the
    whole file would lose the good blocks with it.
    """
    blocks: list[tuple[dict[str, str], str, list[str]]] = []
    matches = list(CHAT_OPEN_PATTERN.finditer(raw_text))
    for index, match in enumerate(matches):
        attributes = dict(ATTR_PATTERN.findall(match.group(1)))
        limit = matches[index + 1].start() if index + 1 < len(matches) else len(raw_text)
        body = raw_text[match.end():limit]
        warnings: list[str] = []
        closing = body.find(CHAT_CLOSE_TAG)
        if closing >= 0:
            body = body[:closing]
        else:
            warnings.append("block has no </chat>; it was read up to the next "
                            "block or the end of the file")
        blocks.append((attributes, body, warnings))
    return blocks

def parse_turn(attributes: str, body: str) -> tuple[int | None, str, str, list[str]]:
    """Parse one ``<turn>`` into ``(index, role, text, warnings)``."""
    warnings: list[str] = []
    fields = dict(ATTR_PATTERN.findall(attributes))
    raw_index = fields.get("n", "")
    if not raw_index.isdigit():
        return None, "", "", [f"turn without a usable n attribute: {raw_index!r}"]
    index = int(raw_index)

    text = body
    role = "unknown"
    label = LABEL_PATTERN.match(text)
    if label:
        role = LABEL_ROLES[label.group(1)]
        text = text[label.end():]
    else:
        warnings.append(f"turn {index} carries no speaker label; its role is "
                        "recorded as unknown and needs a human eye")
    return index, role, text, warnings

def parse_pages(raw_text: str) -> list[dict[str, Any]]:
    """Parse a ``read_conversation`` dump into one record per page.

    HTML entities are unescaped because the search tools were seen to encode
    them.  This tool was seen not to, and unescaping text that contains none
    is a no-op -- while failing to unescape would corrupt every code sample
    containing ``>`` or ``&`` permanently.  The asymmetry decides it.
    """
    pages: list[dict[str, Any]] = []
    for attributes, body, warnings in split_chat_blocks(raw_text):
        url = attributes.get("url", "")
        uuid = attributes.get("conversation_id", "") or uuid_from_url(url)
        if not uuid:
            warnings.append("block without a url or conversation_id was skipped")
            continue

        total = attributes.get("total_turns", "")
        title_match = TITLE_PATTERN.search(body)

        turns: list[dict[str, Any]] = []
        for turn_match in TURN_PATTERN.finditer(body):
            index, role, text, turn_warnings = parse_turn(
                turn_match.group(1), turn_match.group(2))
            warnings.extend(turn_warnings)
            if index is None:
                continue
            text = html.unescape(text)
            if not text.strip():
                warnings.append(f"turn {index} is empty")
            turns.append({"n": index, "role": role, "text": text})

        if not turns:
            warnings.append("page carries no <turn> elements at all; check the "
                            "format probe before ingesting more")

        pages.append({
            "uuid":            uuid,
            "url":             url,
            "updated_at":      attributes.get("updated_at", ""),
            "total_turns":     int(total) if total.isdigit() else 0,
            "range":           attributes.get("turns", ""),
            "next_page_token": attributes.get("next_page_token", ""),
            "prev_page_token": attributes.get("prev_page_token", ""),
            "title":           clean_title(title_match.group(1)) if title_match else "",
            "turns":           turns,
            "warnings":        warnings,
        })
    return pages

def _empty_stats() -> dict[str, int]:
    """Return a fresh statistics block."""
    return {"pages_ingested": 0, "turns_stored": 0,
            "turns_repeated": 0, "turns_conflicting": 0}

def new_store(uuid: str, url: str = "", title: str = "",
              updated_at: str = "") -> dict[str, Any]:
    """Create an empty store for one chat."""
    return {
        "schema_version": SCHEMA_VERSION,
        "chat_uuid":      uuid,
        "url":            url,
        "title":          title,
        "updated_at":     updated_at,
        "total_turns":    0,
        "turns":          {},
        "pages":          [],
        "warnings":       [],
        "stats":          _empty_stats(),
    }

def add_warning(store: dict[str, Any], source: str, message: str) -> None:
    """Record a warning together with where it came from."""
    store["warnings"].append({"source": source, "message": message})

def held_turns(store: dict[str, Any]) -> list[int]:
    """Return the indices held, as sorted integers."""
    return sorted(int(key) for key in store["turns"])

def missing_turns(store: dict[str, Any]) -> list[int]:
    """Return the turn indices still missing, or [] when the total is unknown.

    An unknown total is not the same as nothing missing; callers must check
    ``total_turns`` themselves before reading anything into an empty list.
    """
    total = store["total_turns"]
    if not total:
        return []
    held = set(held_turns(store))
    return [index for index in range(total) if index not in held]

def is_complete(store: dict[str, Any]) -> bool:
    """True when the total is known and every turn up to it is held."""
    return bool(store["total_turns"]) and not missing_turns(store)

def merge_page(store: dict[str, Any], page: dict[str, Any]) -> dict[str, Any]:
    """Merge one parsed page into *store* and report what happened.

    Re-ingesting a page is harmless by construction: a turn overwrites itself
    with identical content.  The single case worth reporting is the same index
    arriving with *different* text, which the tool alone cannot produce -- it
    means the chat was edited between calls, or the transcription went wrong.
    The newer text wins and the event is recorded either way.
    """
    stats = store["stats"]
    stats["pages_ingested"] += 1

    if page["title"]:
        store["title"] = page["title"]
    if page["updated_at"]:
        store["updated_at"] = page["updated_at"]
    if page["url"]:
        store["url"] = page["url"]

    if page["total_turns"]:
        if store["total_turns"] and store["total_turns"] != page["total_turns"]:
            add_warning(store, "envelope",
                        f"total_turns changed from {store['total_turns']} to "
                        f"{page['total_turns']}; the chat grew or was edited "
                        "between calls, so held turns may be stale")
        store["total_turns"] = page["total_turns"]

    added, repeated, conflicting = [], [], []
    for turn in page["turns"]:
        key = str(turn["n"])
        existing = store["turns"].get(key)
        if existing is None:
            added.append(turn["n"])
        elif existing["text"] == turn["text"]:
            repeated.append(turn["n"])
        else:
            conflicting.append(turn["n"])
            add_warning(store, f"turn {turn['n']}",
                        "arrived a second time with different text; the newer "
                        "version was kept. Either the chat was edited, or a "
                        "transcription was not verbatim")
        store["turns"][key] = {"role": turn["role"], "text": turn["text"]}

    stats["turns_stored"] = len(store["turns"])
    stats["turns_repeated"] += len(repeated)
    stats["turns_conflicting"] += len(conflicting)

    indices = [turn["n"] for turn in page["turns"]]
    if indices:
        store["pages"].append({
            "first": min(indices),
            "last":  max(indices),
            "next":  page["next_page_token"],
            "prev":  page["prev_page_token"],
        })

    for message in page["warnings"]:
        add_warning(store, "page", message)

    return {"added": added, "repeated": repeated, "conflicting": conflicting}

def state_path(store_dir: str) -> str:
    """Return the path of the state file."""
    return os.path.join(store_dir, STATE_FILENAME)

def new_state() -> dict[str, Any]:
    """Return an empty protocol, shaped exactly as chat_export_convert writes it."""
    return {"protocol_version": PROTOCOL_VERSION, "project": "",
            "project_created_at": "", "order": "", "listed_at": "",
            "chats": {}}

def blank_entry() -> dict[str, Any]:
    """Return a fresh protocol entry with every field of Vorgabe 2.4."""
    return {"title": "", "created_at": "", "created_after": "",
            "listed_updated_at": "",
            "exported_updated_at": "", "turns": 0, "total_turns": None,
            "end_token": "", "file": "", "side_files": [],
            "status": "listed", "exported_at": ""}

def load_state(store_dir: str) -> dict[str, Any]:
    """Load the state, or return an empty one when there is none.

    A missing state file is never an error here: it is the signal that the
    user still has to decide between a fresh export and a continuation, and
    only the caller knows how to ask that.
    """
    path = state_path(store_dir)
    if not os.path.exists(path):
        return new_state()
    with open(path, "r", encoding="utf-8") as handle:
        state = json.load(handle)
    state.setdefault("protocol_version", PROTOCOL_VERSION)
    state.setdefault("project", "")
    # When this project was last listed -- the reference point for the
    # created_after bound in update_state.
    state.setdefault("listed_at", "")
    # The project's own start date, read off a probe export by hand (doku 1.5).
    state.setdefault("project_created_at", "")
    state.setdefault("order", "")
    state.setdefault("chats", {})
    # A protocol written by chat_export_convert is read as-is; whichever
    # fields a route never touched are filled with their blanks.
    for record in state["chats"].values():
        for key, value in blank_entry().items():
            record.setdefault(key, value)
    return state

def save_state(store_dir: str, state: dict[str, Any]) -> None:
    """Write the protocol atomically."""
    state["protocol_version"] = PROTOCOL_VERSION
    os.makedirs(store_dir, exist_ok=True)
    _write_json_atomic(state, state_path(store_dir), ".state-")

def update_state(store_dir: str, records: list[dict[str, str]],
                 now: str = "") -> dict[str, Any]:
    """Merge identity records into the state and return it.

    A newly seen chat starts as ``listed``.  An exported chat whose source
    moved on -- the list carries a newer ``updated_at`` than the export rests
    on -- becomes ``stale``; that comparison is the whole growth detection
    (Vorgabe 2.4).  An existing title is only replaced by a non-empty one, so
    a listing without a title cannot erase one a read page already supplied.

    *now* stamps the reconciliation.  A chat seen here for the first time gets
    the **previous** reconciliation as ``created_after``: the project was
    listed then and did not contain this chat, so it was created later.  This
    route never learns a real ``created_at`` -- ``read_conversation`` does not
    supply one -- so that bound is all it can offer (Vorgabe 2.4).
    """
    state = load_state(store_dir)
    previous_listed = state.get("listed_at", "")
    for record in records:
        fresh = record["uuid"] not in state["chats"]
        entry = state["chats"].setdefault(record["uuid"], blank_entry())
        for key, value in blank_entry().items():
            entry.setdefault(key, value)
        if fresh:
            entry["created_after"] = previous_listed
        if record.get("updated_at"):
            entry["listed_updated_at"] = record["updated_at"]
        if record.get("title"):
            entry["title"] = record["title"]
        if (entry["status"] == "exported"
                and is_newer(entry["listed_updated_at"],
                             entry["exported_updated_at"] or "")):
            entry["status"] = "stale"
    if now:
        state["listed_at"] = now
    save_state(store_dir, state)
    return state

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
               if entry.get("status") in ("listed", "stale")}
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

def set_chat_status(store_dir: str, uuid: str, status: str,
                    only_from: tuple[str, ...] = ()) -> str | None:
    """Set one chat's status and return the previous value.

    With *only_from* the change happens only when the current status is one
    of the named ones, and ``None`` is returned when nothing changed.  That
    keeps an automatic transition from pulling an exported chat back into
    work.
    """
    state = load_state(store_dir)
    entry = state["chats"].setdefault(uuid, blank_entry())
    previous = entry.get("status", "listed")
    if only_from and previous not in only_from:
        return None
    entry["status"] = status
    save_state(store_dir, state)
    return previous

def build_export(store: dict[str, Any], now: str = "") -> dict[str, Any]:
    """Build the export document for one chat.

    Turns go out in index order as a flat list of messages -- there is nothing
    to segment, because the order is known.  Completeness is stated as a fact
    with the evidence beside it: the held count, the total from the envelope
    and the missing indices, so a reader of the file alone can tell whether it
    is a whole chat or a partial one.

    The shape is the one ``chat_export_convert.py`` writes as well, field for
    field and in the same order, so that a chat fetched either way ends up in
    the same file.  Where a path cannot know something, the value is ``None``
    rather than a guess: this path has no ``created_at`` because
    ``read_conversation`` does not supply one, and it can never report dropped
    blocks because it never sees any.
    """
    missing = missing_turns(store)
    messages = [{"n": index,
                 "role": store["turns"][str(index)]["role"],
                 "content": store["turns"][str(index)]["text"]}
                for index in held_turns(store)]
    return {
        "metadata": {
            "created_at":    "unknown",
            "imported_at":   now,
            "chat_uuid":     store["chat_uuid"],
            "url":           store["url"] or
                             f"https://claude.ai/chat/{store['chat_uuid']}",
            "title":         store["title"],
            "source":        "read_conversation",
            "last_updated_at": store["updated_at"],
            "turns":         len(messages),
            "total_turns":   store["total_turns"] or None,
            "complete":      is_complete(store),
            "turns_missing": missing,
            "deleted":       False,
            "dropped_duplicates": 0,
            "dropped_blocks":     {},
            "dropped_thinking":   0,
            "attachments_with_content":    0,
            "creations":    0,
            "attachments_without_content": [],
        },
        "messages": messages,
        "warnings": list(store["warnings"]),
    }


def record_export(store_dir: str, store: dict[str, Any], out_path: str,
                  now: str) -> dict[str, Any]:
    """Write the export document and note it in the protocol (Vorgabe 2.4).

    The counterpart of what the converter does at the end of a run, kept here
    so the comparison covers the protocol and not only the chat file. Only a
    provably complete chat earns ``exported`` -- a partial one stays visible
    as partial, which is the one thing this side can assert and the converter
    cannot (Vorgabe 2.5).
    """
    document = build_export(store, now=now)
    _write_json_atomic(document, out_path, ".export-")
    if not is_complete(store):
        return document
    state = load_state(store_dir)
    entry = state["chats"].setdefault(store["chat_uuid"], blank_entry())
    for key, value in blank_entry().items():
        entry.setdefault(key, value)
    entry.update({
        "title":       store["title"] or entry.get("title", ""),
        "exported_updated_at": store["updated_at"],
        "turns":       len(store["turns"]),
        "total_turns": store["total_turns"] or None,
        "end_token":   "",
        "file":        os.path.basename(out_path),
        "side_files":  [],
        "status":      "exported",
        "exported_at": now,
    })
    save_state(store_dir, state)
    return document
