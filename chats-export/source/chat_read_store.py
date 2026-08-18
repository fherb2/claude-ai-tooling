#!/usr/bin/env python3
"""Complete, ordered export of past chats via ``read_conversation``.

===========================================================================
@Claude: OPERATING INSTRUCTIONS -- read this part, then start working.
===========================================================================

This script collects whole chat transcripts and writes JSON export files.
It is deliberately dull: ``read_conversation`` hands you a chat by UUID,
paginated by turn, with every turn numbered and the total turn count stated
in the envelope.  So there is nothing to guess, nothing to stitch, and no
uncertainty about whether a chat is finished.

What it cannot do for you: the text still has to travel through your context
on its way into the container.  The search and read tools live in your
runtime, not in the container.  That is the expensive part of the job and
the only part where you can ruin the result -- see TRANSCRIBING below.

If you are looking for the older ``chat_crawl_store.py``: that one
reconstructs chats from overlapping *search snippets* and exists for
environments where ``read_conversation`` is unavailable.  Where this script
works, it supersedes it entirely.

WHAT THE ENVIRONMENT ALLOWS
---------------------------
Established by observation on claude.ai in August 2026, not by
documentation.  Re-check with the probe below before trusting any of it:

*   ``read_conversation(conversation_id, page_token, max_turns)`` returns the
    *full* text of each turn -- not an excerpt.  Turns carry their index, the
    envelope carries ``total_turns``, so completeness is a calculation.
*   Paging works in both directions (``next_page_token`` /
    ``prev_page_token``), and a ``page_token`` from a ``conversation_search``
    result can be used to open a chat at that position.
*   Page size is limited by a character budget, not only by ``max_turns``.
    Around eight turns per page was typical; expect it to vary.
*   It reads the live conversation store, so it is fresher than the search
    index.

Three hard limits, all worth telling the user about up front:

*   **Scope.**  Only chats within the current scope are readable.  From a
    conversation inside a project you reach that project's chats and no
    others -- the same UUID that reads fine inside the project fails outside
    it with "Conversation not found or not accessible".  One run therefore
    covers one project.  Several projects mean several runs, each started
    from inside its own project.
*   **Cowork conversations are unreachable.**  Their ids look like
    ``cse_01Mi...`` and are rejected on format: "Invalid conversation_id:
    expected a UUID".
*   **Enumeration is a subset of retrieval.**  ``recent_chats`` in a project
    lists chats you can also read there, so you never end up holding a UUID
    you are not allowed to fetch -- but the list is not complete: **the chat
    you are running in never appears in its own listing** (observed, twice
    and symmetrically).  Ask for the list from a chat created for that
    purpose and delete it afterwards; then the one chat missing from every
    listing is the one that holds nothing but the listing itself.  Ask from
    a working chat instead, and that chat drops out of the archive without
    anything reporting it.
*   **A chat can also leave the list.**  ``plan`` and ``overview`` report the
    ones the protocol knows and the list no longer offers, with the wording of
    ``VANISHED_NOTE`` -- deleted at the source, moved to another project, or a
    list that was not paged to the end.  Nothing is removed automatically; the
    three cases are indistinguishable from here.  ``chat_export_convert.py``
    says it word for word, guarded by ``tests/test_wegegleichheit.py``.

THE STORE DIRECTORY
-------------------
``--store-dir`` holds one file per chat plus one state file:

*   ``<uuid>.json`` -- one chat: its turns by index, its ``total_turns``, and
    which pages have been fetched.
*   ``protokoll.json`` -- every chat UUID known in this scope, with title,
    timestamps and working status, plus the direction of work.  It is the
    **same protocol file** the local zip converter writes, so both routes
    keep one shared ledger per source project.

``protokoll.json`` is what makes a run resumable across conversations.  It
must always travel with the store files; the titles and every ``exported``
mark live there and nowhere else.

A ``crawl-state.json`` in the directory means it belongs to the older
``chat_crawl_store.py``.  Do not mix the two: the data models are unrelated.

SESSION START -- do this before anything else
---------------------------------------------
A whole project does not fit into one conversation, so most sessions are a
continuation.  Find out which one you are in first::

    python chat_read_store.py --store-dir ./store overview

The report names the case.  Three situations need a question put to the user,
and you must not guess your way past them:

*   **Nothing there at all.**  Ask: a fresh export, or continuing earlier
    work?  On a fresh export also ask whether to work through the chats
    oldest-first or newest-first, record it with ``state --order <choice>``,
    and then map the scope.  On a continuation ask for the upload of
    ``protokoll.json`` plus the ``<uuid>.json`` of every started chat.

2a. ASK WHAT IS NEW, BEFORE READING ANYTHING

    When a ``protokoll.json`` was uploaded, the first thing to run is
    ``plan``: fetch a fresh chat list, hand it to ``plan --raw``, and show the
    user what it says.  It writes nothing and decides nothing -- it reports how
    many chats are new, grown, or still pending, and then names two ways
    forward: request an account export from a given date (everything, thinking
    and attachments included), or read the chats here and now (immediate, but
    permanently without thinking and attachments).

    Do not choose for the user.  The date ``plan`` names is the whole point of
    the exercise: it is computed from the best bound available for each chat,
    and a window that is too short loses content silently.  If ``plan`` says
    the window cannot be computed, ask the user for the project's start date
    (they read it off a probe export) and pass it to ``map --project-created``.

    Only when the user chooses to read here does the rest of this docstring
    apply.
*   **A state file is there.**  Continue; do not ask.  The one exception is a
    store *you* built earlier in this same conversation that was merely
    interrupted -- then ask whether to continue or start over empty, because
    only you know that no upload happened.
*   **Chats marked ``started`` whose ``<uuid>.json`` is absent.**  Ask for
    exactly those files by name; the turns already read are otherwise lost.

UPLOAD PROBE -- once per continuation, before trusting anything uploaded
    Whether files the user uploads into the conversation are readable by this
    script in the container is *not* documented anywhere.  So check: list the
    directory they landed in, confirm the files parse, and report the result.

    Never point ``--store-dir`` at the upload location and never work in
    place: COPY the files into your working store directory first, then run
    ``overview`` there.  The upload location is reported to be read-only, so
    working in it would fail at the first write.

    Where that location is, is NOT documented by Anthropic.  Community
    reverse-engineering reports ``/mnt/user-data/uploads`` on claude.ai, and
    that is the first place worth looking, but treat it as a guess: if the
    files are not there, search rather than conclude they were never
    uploaded.

    They may arrive under a different name -- ``.txt`` appended, because a
    chat upload of a ``.json`` file is not always accepted.  Renaming while
    copying is fine; changing the content is not.

    One asymmetry decides how far you may go if the files are unreachable.
    Writing ``protokoll.json`` out again from what you can see in the
    conversation is acceptable: it is small and machine-generated.  Doing that
    with a ``<uuid>.json`` is not -- those hold chat text, and retyping it is
    exactly what must not happen.  Rather stop and say so.

WORKFLOW
--------
1.  Map the scope.  Call ``recent_chats`` with ``sort_order='asc'`` and
    ``n=20``; page further with ``before``/``after`` until nothing new
    arrives.  Write each dump out verbatim and run::

        python chat_read_store.py --store-dir ./store map --raw recent.txt

    Only UUID, timestamp and title are taken from it -- bodies are ignored on
    purpose.  A chat whose listing block is empty still gets its title from
    the first page you read, so there is nothing to work around here.

2.  Pick the chats to work on -- at most ``ACTIVE_LIMIT`` (three) at a time.
    ``overview`` names them and nominates the next candidates in the chosen
    order.  Read it at the start of every round instead of remembering: the
    state on disk is the truth, your recollection of it is not.

    Three is an upper bound, not a quota, and with long chats one at a time is
    the better choice.  Two reasons for the cap, both real: every turn of
    every chat passes through your context, and only started chats have to
    travel to the next conversation -- a chat upload is documented to take at
    most 20 files, so three keeps the handover at four.

    ``total_turns`` lets you say what a chat will cost *before* you start it.
    Use that: a 200-turn chat is a whole round on its own.

3.  Read a page and ingest it::

        python chat_read_store.py --store-dir ./store ingest --raw page.txt

    Start a chat with ``read_conversation`` without a page token; continue
    with the token ``overview`` or ``status`` names.  ``ingest`` reports how
    many turns are held against the total and which are still missing.

    ALWAYS ASK FOR ``max_turns=50``, the documented maximum.  The default is
    20, and a character budget may hand you fewer turns than you asked for
    anyway -- but asking for fewer can only ever cost extra calls, never save
    any.  With the eight turns per page seen in practice, a 58-turn chat runs
    to roughly eight calls; every one of them is a page you have to write out
    by hand, so this is where the real cost of an export sits.

    If you entered a chat in the middle -- possible, because a ``page_token``
    from a ``conversation_search`` result opens the chat at that position --
    then turns *before* your entry point are missing too, and
    ``prev_page_token`` is how you walk backwards to them.  ``status`` reports
    it as ``prev=``.  Reading from turn 0 forwards avoids the whole question
    and is the normal path.

4.  Repeat step 3 until a chat is complete.  ``status`` names the gaps by
    number, so there is never a question about what is left.  Ingesting the
    same page twice is harmless -- if in doubt, fetch it again.

5.  Export every complete chat::

        python chat_read_store.py --store-dir ./store export \
            --chat <uuid> --out chat_<uuid>.json

    The export sets ``exported``, but only for a chat whose turns are all held.
    Exporting a partial chat is allowed -- then the document carries
    ``complete: false`` and the missing indices, and you say so plainly.

6.  Round over.  Hand the files to the user, report the standing, ask whether
    to continue.  See ROUNDS AND HANDOVER.

ROUNDS AND HANDOVER
-------------------
The container filesystem is wiped between sessions, so the store travels
through the user by hand.  Work in *rounds* and hand over at the end of each.

Do NOT wait for the context to run out.  You cannot see it run out.  On
claude.ai a long conversation does not stop at the limit, it summarises its
earlier parts and continues -- so the moment you would be waiting for may
never arrive, and what degrades instead is your grip on these instructions.
That is why the round drives the handover.  It also makes the summarising
harmless: everything that matters is on disk, so a fresh ``overview``
restores the full picture, and this file can be read again.

At the start, tell the user they may interrupt at any time; otherwise you
work on until the round ends or nothing is left.  If they do interrupt, run
the handover -- do not just stop.

Once the start decision is settled, do not ask for authorisation again.  A
round is the unit of work, and asking per chat or per page turns the export
into a conversation about the export.  Spanning several conversations *is* the
design; taking up a single chat is a normal round, not a concession.

The handover itself:

*   Export what is complete and offer every export file for download.  Name
    the chats that are ``exported``: the user can file those away for good.
*   Hand back ``protokoll.json`` **always**, with the ``<uuid>.json`` of
    every chat still ``started``.  ``overview`` lists exactly these.
*   Say how many chats are exported, how many started, how many still
    listed or stale.
    Mention that these are JSON files and ask whether the user needs them
    with a ``.txt`` extension to get them back in next time.
*   Then ask whether to continue.

HOW TO REPORT TO THE USER
-------------------------
Keep a running note of the work, and keep it short:

*   Say at the outset that the user may interrupt whenever they like.
*   One short line on every status change -- which chat you have taken up,
    which one is complete.  A line, not a paragraph; the full standing comes
    at the handover.
*   Never report a chat as finished that you have not exported, and never
    call one complete unless ``status`` says so against ``total_turns``.
    Unlike its predecessor, this script can prove completeness -- so there is
    no reason to claim it without the proof.
*   Warnings recorded in a store are for you, not for the user.  Read them,
    judge them, and pass on only what needs a human eye: a turn without a
    speaker label, a turn that arrived twice with different text, a
    ``total_turns`` that changed between calls.

WHAT NOT TO DO
--------------
*   Do not edit store files by hand.
*   Do not summarise, shorten by rewording, or "make handleable" a page on
    its way into a file.  Copy less of it rather than a version of it.
*   Do not skip a page because it looks like text you already have.
    Re-ingesting is free and provably harmless; guessing is not.
*   Do not take up more than three chats at a time.
*   Do not hand the store back without ``protokoll.json``.
*   Do not wait for a signal that the context is running out.  There is none.
*   Do not mix this store with a ``chat_crawl_store.py`` store.
*   Do not leave ``max_turns`` at its default.  Ask for 50 every time.

PROBE -- do this once per environment, before trusting the parser.
-----------------------------------------------------------------
Formats change and are not the same across claude.ai, Claude Desktop and
Claude Code.  A wrong assumption here does not crash anything, it quietly
produces a damaged transcript.  So spend one call on checking.

Call ``read_conversation`` on any chat, without a page token, and answer:

*   Does the envelope carry ``total_turns`` and a turn range, and are the
    attributes named as in OBSERVED FORMAT below?
*   Are turns wrapped as ``<turn n="0">`` and does the text begin with a
    speaker label -- ``Human: `` / ``Assistant: `` spelled out, or the short
    ``H: `` / ``A: `` used by the search tools?
*   Are ``<``, ``>`` and ``&`` written literally, or as HTML entities?  The
    search tools were seen to escape them; this tool was seen not to.
*   Does the title arrive as a ``<title>`` element, and is it clean, or does
    it carry stray zero-width characters?
*   Fetch the last page of a short chat: is a missing ``next_page_token`` how
    the end announces itself?

Report anything that differs from OBSERVED FORMAT before ingesting.  Naming
the difference is worth far more than a half-correct export.  Then ingest the
probe's dump like any other -- it is real data.

TRANSCRIBING -- the one place you must not economise.
-----------------------------------------------------
There is no pipe from the tool into the container: the text reaches the file
only because you write it out.  Use a quoted heredoc so nothing is expanded::

    cat > page.txt <<'RAWEOF'
    <chat url="..." total_turns="58" turns="0-7" next_page_token="t8">...
    RAWEOF
    python chat_read_store.py --store-dir ./store ingest --raw page.txt

Leaving text out and rewriting text are not two degrees of the same problem,
they are opposites:

*   **Leaving out** is recoverable.  A turn you did not copy is simply
    missing, ``status`` names it by number, and fetching that page again
    brings it back.
*   **Rewriting, summarising or paraphrasing** is not recoverable.  It lands
    in the store as if it were the real turn and reaches the export
    indistinguishable from it.  That is not a damaged record, it is an
    invented one.

So when a page is too large to write out in one go, split it across several
``ingest`` calls -- any number is fine, one file per turn if need be.  Never
condense, and never invent an ellipsis to mark an omission.

If you have already shortened something, say which chat and repair it rather
than discussing it: delete the affected turns from the store by fetching that
page again -- a re-ingested turn overwrites itself -- or, if in doubt about a
whole chat, delete its ``<uuid>.json``, set its status back to ``listed``
and read it again from the start.  Nothing in the store can detect a
paraphrase, so the doubt itself is reason enough.

===========================================================================
DESIGN NOTES -- for the developer maintaining this script.
===========================================================================

OBSERVED FORMAT
---------------
One page, as seen in August 2026.  Titles and turn texts below are invented;
every structural detail is reproduced exactly as observed -- the attribute
spelling, the ``><title>`` glued to the closing bracket, the blank lines and
the two spaces after ``Assistant:``.  Real chat text is kept out of this
script on purpose: it travels wherever the script is uploaded::

    <chat url="https://claude.ai/chat/<uuid>"
          updated_at="2026-08-01T12:00:00.000000+00:00"
          total_turns="58" turns="0-7" next_page_token="t8"
      ><title>Pruefstueck Lesepfad</title>

    <turn n="0">Human: Wie schneiden wir die Rollen ...</turn>

    <turn n="1">Assistant:  Der GUI-Prozess besitzt ...</turn>

Attributes are read order-independently and unknown ones are ignored, so an
added attribute does not break parsing.  ``prev_page_token`` was documented
but not seen in a first-page envelope, which is consistent with it being
absent at the start.

WHY TURNS AND NOT TEXT
----------------------
A turn has an identity: its index.  Ingesting the same page twice therefore
cannot corrupt anything -- each turn overwrites itself with the same content.
That is the whole reason this script is short where its predecessor is long:
no overlap detection, no ambiguity resolution, no edge bookkeeping, and no
guessing about order.

The one thing worth watching is a turn arriving *twice with different text*.
That cannot happen from the tool alone, so it means the chat was edited
between calls, or the transcription went wrong.  Both deserve a warning and
neither may be silently resolved: the newer text wins, but the event is
recorded.

COMPLETENESS
------------
``total_turns`` from the envelope is the target, the keys of ``turns`` are
what is held.  ``missing_turns`` is the difference, and it is the only
authority on whether a chat is finished.  This is the sharpest break from
``chat_crawl_store.py``, whose instructions had to forbid ever claiming a
chat was complete.

Turn indices are JSON object keys and therefore strings on disk.  Everything
in memory converts to ``int`` at the boundary; nothing else may assume one
or the other.

STATUS MECHANICS
----------------
``plan`` is read-only and exists to be run first: it answers "what is new?"
against a fresh chat list without touching a thing, so the user can decide
between the export route and this one while knowing the cost of each.

``protokoll.json`` carries one status per chat, shared with the zip route:
``listed`` (known from the chat list), ``started`` (partially read -- only
this route ever sets it), ``exported``, ``stale`` (the source moved on) and
``deleted`` (only ever set by hand here, because this route cannot tell a
deleted chat from an inaccessible one).

``ingest`` is what sets ``started``: reading a page *is* taking up a chat.
There is no equivalent of the predecessor's problem where a chat grew by
accident inside another chat's dump -- ``read_conversation`` returns one chat
per call, so intent and effect coincide.

``map`` is what sets ``stale``: a chat list whose ``updated_at`` is newer
than the export's means the source moved on.  A stale chat is read again
from the start and replaced whole.

``export`` sets ``exported`` only when every turn up to ``total_turns`` is
held, and records the written file in the protocol.  This is a proof, not a
judgement, which is the sharpest difference from ``chat_crawl_store.py``.

``exported`` means "written out, and the file may leave the store
directory".  That is why the status lives in the protocol and not in the
per-chat store: a finished chat whose ``<uuid>.json`` has been filed away
must not look untouched next time.

Three more fields ride alongside the status, all of them about *when*, none of
them written by hand:

``listed_at`` (top level) is the timestamp of the last ``map``.  ``plan`` and
``map`` both stamp it, and it is the reference point the next new chat gets
bounded against -- see ``created_after`` below.

``created_after`` (per chat) is set exactly once, the first time a chat is
seen, to whatever ``listed_at`` held *before* that.  The reasoning: the project
was listed then and this chat was not in it, so it was created afterwards.
This route never learns a chat's real ``created_at`` -- ``read_conversation``
does not supply one -- so this is the only lower bound it can ever offer.  It
is never overwritten once set; overwriting it on a later ``map`` would
quietly weaken a bound that was already as tight as it gets.

``project_created_at`` (top level) is the one field nothing here can derive:
the source project's own creation date, typed in by hand via
``map --project-created`` after reading it off a probe export
(``inspect_export.py``).  It bounds every chat that has neither of the two
fields above, because no chat of a project can predate the project itself.

All three feed ``window_start()``, which picks the best bound available per
chat and reports the earliest date an account export would have to reach to
cover everything pending -- see ``plan`` and doku Vorgabe 2.4.

Every command that stamps a timestamp accepts ``--now`` to record a fixed one
instead of the clock -- for reproducible test runs, not for daily use.

``state --status`` is the manual override for what no script can judge -- a
chat the user calls good enough, a status that drifted, a file that came back
under another name.  ``state --order`` may be changed at any time; it only
steers which ``listed`` or ``stale`` chat is nominated next.

``overview`` derives everything and decides nothing.  Where it cannot know,
it says so instead of guessing: an idle round looks the same whether a round
just ended or none has begun, and only the reader can tell those apart.

Usage
-----
    python chat_read_store.py overview
    python chat_read_store.py state    [--order oldest-first|newest-first] \
                                       [--chat <uuid> --status STATUS]
    python chat_read_store.py map      --raw recent.txt
    python chat_read_store.py ingest   --raw page.txt
    python chat_read_store.py status   [--chat <uuid>]
    python chat_read_store.py export   --chat <uuid> [--out file]
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import re
import sys
import tempfile
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION       = 1
STATE_FILENAME       = "protokoll.json"
PROTOCOL_VERSION     = 1
FOREIGN_STATE        = "crawl-state.json"   # belongs to chat_crawl_store.py
ACTIVE_LIMIT         = 3        # chats worked on at once (upper bound)

# What both routes say when the protocol knows a chat the fresh list no longer
# offers. Held word for word in chat_export_convert.py too and guarded by
# tests/test_wegegleichheit.py: the two scripts cannot import from each other
# (vorgabe 2.9), and this project has twice watched one side of such a pair
# grow while the other stood still.
VANISHED_NOTE = """\
NOTE: {count} chat(s) in the protocol are not in this list.
  Deleted at the source, moved out of the project -- or the list was not paged
  to the end. Check before concluding anything; nothing is removed automatically."""

# The shared vocabulary of Vorgabe 2.4. 'started' is this route's own --
# partially read; the zip route always writes a chat whole. 'stale' is set by
# 'map' when the source moved on; 'deleted' only ever by hand, because this
# route cannot tell a deleted chat from an inaccessible one.
CHAT_STATUSES = ("listed", "started", "exported", "stale", "deleted")
ORDER_VALUES  = ("oldest-first", "newest-first")

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

# 'Title:' line of a recent_chats block, used by 'map' only.
TITLE_LINE_PATTERN = re.compile(r"^\s*Title:\s*(.*)$", re.M)

# Zero-width characters observed in reported output; harmless but they must
# not end up inside a stored title.
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍﻿"))


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

UMLAUTS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "ae",
                         "Ö": "oe", "Ü": "ue", "ß": "ss"})
SLUG_STRIP = re.compile(r"[^a-z0-9]+")
SLUG_MAX = 50


def slug(title: str) -> str:
    """Turn a chat title into a filename part (doku 2.3).

    Deliberately duplicated from chat_export_convert.py: this script has to
    stay uploadable as a single file (doku 2.9), and the equality of the two
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


def format_ranges(numbers: list[int]) -> str:
    """Render sorted integers compactly: ``[3,9,10,11,40]`` -> ``3, 9-11, 40``."""
    if not numbers:
        return ""
    parts: list[str] = []
    start = previous = numbers[0]
    for number in numbers[1:]:
        if number == previous + 1:
            previous = number
            continue
        parts.append(f"{start}" if start == previous else f"{start}-{previous}")
        start = previous = number
    parts.append(f"{start}" if start == previous else f"{start}-{previous}")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

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


def parse_chat_list(raw_text: str) -> list[dict[str, str]]:
    """Parse a ``recent_chats`` dump into identity records.

    Only uuid, timestamp and title are taken.  Bodies are ignored on purpose:
    with ``read_conversation`` available there is no reason to reconstruct a
    chat from a listing, and a chat whose listing block is empty still gets
    its title from the first page that is read.
    """
    records: list[dict[str, str]] = []
    for attributes, body, _ in split_chat_blocks(raw_text):
        url = attributes.get("url", "")
        uuid = attributes.get("conversation_id", "") or uuid_from_url(url)
        if not uuid:
            continue
        title_match = TITLE_LINE_PATTERN.search(body)
        records.append({
            "uuid":       uuid,
            "url":        url,
            "updated_at": attributes.get("updated_at", ""),
            "title":      clean_title(title_match.group(1)) if title_match else "",
        })
    return records


# ---------------------------------------------------------------------------
# Per-chat store
# ---------------------------------------------------------------------------

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


def upgrade_store(store: dict[str, Any]) -> dict[str, Any]:
    """Fill in keys an older store file may lack."""
    store.setdefault("turns", {})
    store.setdefault("pages", [])
    store.setdefault("warnings", [])
    store.setdefault("total_turns", 0)
    stats = store.setdefault("stats", _empty_stats())
    for key, value in _empty_stats().items():
        stats.setdefault(key, value)
    store["schema_version"] = SCHEMA_VERSION
    return store


def store_path(store_dir: str, uuid: str) -> str:
    """Return the file path of the store belonging to *uuid*."""
    return os.path.join(store_dir, f"{uuid}.json")


def load_store(path: str) -> dict[str, Any]:
    """Load a store from *path*, filling in missing keys."""
    with open(path, "r", encoding="utf-8") as handle:
        return upgrade_store(json.load(handle))


def is_store_payload(payload: Any) -> bool:
    """True when *payload* looks like a chat store of this script."""
    return (isinstance(payload, dict)
            and isinstance(payload.get("chat_uuid"), str)
            and isinstance(payload.get("turns"), dict))


def try_load_store(path: str) -> dict[str, Any] | None:
    """Load a store, or return None when the file is not one.

    Directory scans use this so that an export written into the store
    directory, or a store of the other script, is skipped instead of
    crashing the command.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return upgrade_store(payload) if is_store_payload(payload) else None


def save_store(store: dict[str, Any], path: str) -> None:
    """Write a store atomically."""
    _write_json_atomic(store, path, ".store-")


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


def next_token(store: dict[str, Any]) -> str:
    """Return the token continuing past the furthest page held, or ''.

    Taken from whichever page reaches furthest into the chat -- not simply the
    last one ingested, because pages may arrive out of order.  Pages *without*
    a token take part in the comparison on purpose: if the furthest page had
    no ``next_page_token``, the end has been reached, and reporting the token
    of some earlier page instead would send the reader backwards.
    """
    if not store["pages"]:
        return ""
    return max(store["pages"], key=lambda page: page["last"])["next"]


def prev_token(store: dict[str, Any]) -> str:
    """Return the token continuing before the earliest page held, or ''."""
    if not store["pages"]:
        return ""
    return min(store["pages"], key=lambda page: page["first"])["prev"]


def gap_token(store: dict[str, Any]) -> str:
    """Return the token that reopens the first gap, or ''.

    A gap can only appear when pages were fetched out of order, and the page
    ending just before the first missing turn is the one whose
    ``next_page_token`` leads into it.  Without such a page the gap has to be
    reached some other way -- from a search result's token, or by reading the
    chat again from the start.
    """
    missing = missing_turns(store)
    if not missing:
        return ""
    boundary = missing[0] - 1
    for page in store["pages"]:
        if page["last"] == boundary and page["next"]:
            return page["next"]
    return ""


# ---------------------------------------------------------------------------
# Crawl state
# ---------------------------------------------------------------------------

def state_path(store_dir: str) -> str:
    """Return the path of the state file."""
    return os.path.join(store_dir, STATE_FILENAME)


def state_exists(store_dir: str) -> bool:
    """True when a state file is present."""
    return os.path.exists(state_path(store_dir))


def foreign_state_present(store_dir: str) -> bool:
    """True when the directory holds the other script's state file."""
    return os.path.exists(os.path.join(store_dir, FOREIGN_STATE))


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
        if (entry["status"] == "exported" and entry["listed_updated_at"]
                and entry["listed_updated_at"] > (entry["exported_updated_at"] or "")):
            entry["status"] = "stale"
    if now:
        state["listed_at"] = now
    save_state(store_dir, state)
    return state


def plan_report(state: dict[str, Any], records: list[dict[str, str]],
                now: str) -> dict[str, Any]:
    """Compare a fresh chat list against the protocol, without changing either.

    This is the "what is new?" question, answered as a pure computation so it
    can run before the user has decided anything -- the whole point is to hand
    them the choice, not to take it.  Nothing here writes; the caller may not
    save the state it was given.

    Four groups come out of the comparison.  *new* and *grown* are work to do;
    *pending* is work an earlier run left behind (listed, never fetched);
    *vanished* is a chat the protocol knows and the list no longer offers,
    which means deleted at the source or moved out of the project -- and,
    less alarmingly, a chat list that was not paged to the end.
    """
    listed = {record["uuid"]: record for record in records}
    known = state["chats"]
    groups: dict[str, list[str]] = {"new": [], "grown": [], "pending": [],
                                    "started": [], "unchanged": [],
                                    "deleted": [], "vanished": []}
    for uuid, record in listed.items():
        entry = known.get(uuid)
        if entry is None:
            groups["new"].append(uuid)
            continue
        status = entry.get("status", "listed")
        fresh = record.get("updated_at", "")
        if status == "deleted":
            groups["deleted"].append(uuid)
        elif status == "started":
            groups["started"].append(uuid)
        elif status in ("listed", "stale"):
            groups["pending"].append(uuid)
        elif fresh and fresh > (entry.get("exported_updated_at") or ""):
            groups["grown"].append(uuid)
        else:
            groups["unchanged"].append(uuid)
    groups["vanished"] = [uuid for uuid in known if uuid not in listed]

    # The window is computed on what the protocol WOULD look like after this
    # list is folded in -- new chats bounded by the previous reconciliation,
    # grown ones by their own created_at. Nothing is saved.
    hypothetical = {"project_created_at": state.get("project_created_at", ""),
                    "chats": {}}
    previous_listed = state.get("listed_at", "")
    for uuid in groups["new"]:
        hypothetical["chats"][uuid] = {"status": "listed", "created_at": "",
                                       "created_after": previous_listed}
    for uuid in groups["grown"] + groups["pending"] + groups["started"]:
        entry = known[uuid]
        hypothetical["chats"][uuid] = {
            "status": "stale",
            "created_at": entry.get("created_at", ""),
            "created_after": entry.get("created_after", "")}
    window = window_start(hypothetical)

    # What the reading route would cost instead: turns are known only for
    # chats an archive has already described. Guessing for the rest would be
    # invention, so they are counted, not estimated.
    known_turns = 0
    unknown_extent = len(groups["new"])
    for uuid in groups["grown"] + groups["pending"] + groups["started"]:
        extent = known[uuid].get("total_turns") or known[uuid].get("turns") or 0
        if extent:
            known_turns += extent
        else:
            # Listed but never fetched: the protocol knows of it and nothing
            # about its size. Counting it as zero turns would understate the
            # cost of option B for every chat an earlier run left behind.
            unknown_extent += 1
    titles = {uuid: record.get("title", "") for uuid, record in listed.items()}
    return {"groups": groups, "window": window, "known_turns": known_turns,
            "unknown_extent": unknown_extent, "titles": titles,
            "previous_listed": previous_listed, "now": now}


def format_plan(report: dict[str, Any], state: dict[str, Any]) -> list[str]:
    """Render the plan for a human to decide on."""
    groups, window = report["groups"], report["window"]
    lines = ["WHAT IS NEW"]
    if state.get("project"):
        lines.append(f"  project        : {state['project']}")
    lines.append(f"  last reconciled: {report['previous_listed'][:19] or 'never'}")
    for key, label in (("new", "new, never seen"),
                       ("grown", "grown since the export"),
                       ("pending", "pending from an earlier run"),
                       ("started", "partially read"),
                       ("unchanged", "unchanged"),
                       ("deleted", "deleted at the source"),
                       ("vanished", "gone from the list")):
        if groups[key]:
            lines.append(f"  {label:<27}: {len(groups[key])}")
    todo = len(groups["new"]) + len(groups["grown"]) + len(groups["pending"]) \
        + len(groups["started"])
    def vanished_note() -> list[str]:
        """The chats the protocol knows and the list no longer offers.

        Reported on both paths: with nothing left to fetch it is the *only*
        finding, and the most likely one to matter -- everything exported and
        some chats gone means they were deleted at the source.
        """
        if not groups["vanished"]:
            return []
        return [""] + VANISHED_NOTE.format(
            count=len(groups["vanished"])).splitlines()

    if not todo:
        lines += ["", "Nothing to fetch -- every listed chat is exported and "
                      "none has moved on."]
        lines += vanished_note()
        return lines

    lines += ["", f"TO FETCH: {todo} chat(s)"]
    for key, mark in (("new", "new"), ("grown", "grown"),
                      ("pending", "pending"), ("started", "partial")):
        for uuid in groups[key]:
            # A chat seen for the first time has no protocol entry yet, so its
            # title exists only in the fresh list.
            title = (report.get("titles", {}).get(uuid)
                     or (state["chats"].get(uuid) or {}).get("title", ""))
            lines.append(f"  {mark:<8} {uuid[:8]}  {title[:44]!r}")

    lines += ["", "OPTION A -- the account export: everything, thinking and "
                  "attachments included"]
    if window["source"] == "unbounded":
        lines += [f"  {len(window['unbounded'])} of them have no date bound at "
                  "all, so the window cannot be computed.",
                  "  Give the project's start date once (read it off a probe "
                  "export with", "  inspect_export.py, then 'map "
                  "--project-created <date>'), or export everything."]
    else:
        reason = {"created_at": "the creation date of the oldest chat to fetch",
                  "created_after": "the reconciliation before the oldest new "
                                   "chat appeared",
                  "project": "the project's own start date -- no chat can be "
                             "older"}[window["source"]]
        lines += [f"  Request an export from {window['start'][:10]} onwards.",
                  f"  That date is {reason}.",
                  "  A wider window costs only download size; a narrower one "
                  "loses content."]
    lines += ["  Then run chat_export_convert.py locally: list, convert.",
              "",
              "OPTION B -- read them here, now: no waiting, but permanently "
              "poorer"]
    if report["known_turns"]:
        pages = -(-report["known_turns"] // 8)
        lines.append(f"  {report['known_turns']} turn(s) of known extent, "
                     f"roughly {pages} page(s) of reading at ~8 turns a page.")
    if report["unknown_extent"]:
        lines.append(f"  {report['unknown_extent']} of the {todo} chat(s) have "
                     "no known extent -- no archive has described them, so "
                     "there is no honest estimate.")
    lines += ["  Everything fetched this way lacks thinking and attachments "
              "for good (3.2.1).", "  Only a later export can repair that, and "
              "only by replacing the chat."]
    lines += vanished_note()
    lines += ["", "Nothing was written. Whichever way you choose, the protocol "
                  "is updated only", "when the chats are actually fetched -- so "
                  "a window that turns out too short",
              "leaves the missing chats visible as pending, to fetch again."]
    return lines


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
    start = min(value for value, _ in bounds.values())
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


def set_order(store_dir: str, order: str) -> None:
    """Record the direction in which the chats are worked through.

    Changing this later is harmless: it only steers which ``listed`` or
    ``stale`` chat is nominated next and never touches what is exported.
    """
    state = load_state(store_dir)
    state["order"] = order
    save_state(store_dir, state)


def sort_chats(records: list[dict[str, Any]], order: str) -> list[dict[str, Any]]:
    """Order chat records by timestamp; entries without one always come last."""
    stamped = [record for record in records if record.get("updated_at")]
    unstamped = [record for record in records if not record.get("updated_at")]
    stamped.sort(key=lambda record: record["updated_at"],
                 reverse=(order == "newest-first"))
    return stamped + unstamped


def chat_overview(store_dir: str) -> dict[str, Any]:
    """Derive the working picture from the state and the store files.

    Nothing about the crawl is decided here.  A store file the state does not
    know about is reported as *recovered* and counted as ``started`` without
    being written out; the next command touching that chat persists the
    record anyway.
    """
    state = load_state(store_dir)
    order = state.get("order") or "oldest-first"

    known = {uuid: dict(entry) for uuid, entry in state["chats"].items()}
    stores: dict[str, dict[str, Any]] = {}
    recovered: set[str] = set()
    if os.path.isdir(store_dir):
        for name in sorted(os.listdir(store_dir)):
            if not name.endswith(".json") or name in (STATE_FILENAME, FOREIGN_STATE):
                continue
            store = try_load_store(os.path.join(store_dir, name))
            if store is None:
                continue
            uuid = name[:-len(".json")]
            stores[uuid] = store
            if uuid not in known:
                known[uuid] = {"status": "started"}
                recovered.add(uuid)

    records: list[dict[str, Any]] = []
    for uuid, entry in known.items():
        record = {
            "uuid":       uuid,
            "title":      entry.get("title", ""),
            "updated_at": entry.get("updated_at", ""),
            "status":     entry.get("status", "listed"),
            "has_store":  uuid in stores,
            "recovered":  uuid in recovered,
            "held":       0,
            "total":      0,
            "chars":      0,
            "missing":    [],
            "complete":   False,
            "token":      "",
        }
        if record["has_store"]:
            store = stores[uuid]
            record["title"] = record["title"] or store.get("title", "")
            record["updated_at"] = (record["updated_at"]
                                    or store.get("updated_at", ""))
            record["held"] = len(store["turns"])
            record["total"] = store["total_turns"]
            record["chars"] = sum(len(turn["text"])
                                  for turn in store["turns"].values())
            record["missing"] = missing_turns(store)
            record["complete"] = is_complete(store)
            record["token"] = gap_token(store) or next_token(store)
        records.append(record)

    records = sort_chats(records, order)

    active = [r for r in records if r["status"] == "started"
              and r["has_store"] and not r["complete"]]
    ready = [r for r in records if r["status"] != "exported" and r["complete"]]
    missing_files = [r for r in records if r["status"] == "started"
                     and not r["has_store"]]
    done = [r for r in records if r["status"] == "exported"]
    # 'stale' chats queue up again next to the never-started ones: the source
    # moved on, so there is fresh reading to do either way.
    queued = [r for r in records if r["status"] in ("listed", "stale")]
    candidates = [r for r in queued if not r["complete"]]
    free_slots = max(0, ACTIVE_LIMIT - len(active))

    if active:
        round_state = "in progress"
    elif candidates or ready or missing_files:
        round_state = "idle"
    else:
        round_state = "all done"

    return {
        "store_dir":   store_dir,
        "state_file":  state_exists(store_dir),
        "foreign":     foreign_state_present(store_dir),
        "order":       order,
        "order_set":   bool(state.get("order")),
        "records":     records,
        "active":      active,
        "ready":       ready,
        "missing":     missing_files,
        "done":        done,
        "queued":      queued,
        "candidates":  candidates,
        "free_slots":  free_slots,
        "next_up":     candidates[:free_slots],
        "round_state": round_state,
    }


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def _overview_chat_line(record: dict[str, Any], hint: str = "") -> list[str]:
    """Render one chat as one or two lines of the overview."""
    lines = [f"  {record['uuid']}  {record['title'] or '(title unknown)'}"]
    facts = []
    if record["total"]:
        facts.append(f"{record['held']}/{record['total']} turns")
        facts.append(f"{record['chars']} chars")
    elif record["held"]:
        facts.append(f"{record['held']} turns, total unknown")
    if record["missing"]:
        facts.append(f"missing {format_ranges(record['missing'])}")
    if not record["has_store"]:
        facts.append("no store file here")
    if record["recovered"]:
        facts.append("recovered from the store file")
    detail = ", ".join(facts)
    if detail or hint:
        lines.append(f"      {detail}{'  -> ' + hint if hint else ''}")
    return lines


def _no_state_report(store_dir: str) -> list[str]:
    """Render the start-up decision when there is nothing to continue from."""
    return [
        f"NO CRAWL STATE in {store_dir}",
        "-" * 66,
        "Neither a state file nor a single chat store is here.",
        "Ask the user which case applies; do not guess:",
        "  * a fresh export -- ask whether to work through the chats",
        "    oldest-first or newest-first, then run 'state --order <choice>',",
        "    then map the scope with 'map' from a recent_chats dump.",
        f"  * continuing earlier work -- ask them to upload {STATE_FILENAME}",
        "    plus the <uuid>.json of every chat marked 'started', then run the",
        "    upload probe from the operating instructions.",
        "If you created or emptied this directory yourself earlier in this same",
        "conversation, neither case applies: carry on where you left off.",
    ]


def overview_report(picture: dict[str, Any]) -> str:
    """Render the working picture as text that states the next action."""
    if not picture["state_file"] and not picture["records"]:
        return "\n".join(_no_state_report(picture["store_dir"]))

    started = [r for r in picture["records"] if r["status"] == "started"]
    lines = [f"READ STATE  {picture['store_dir']}"]

    if picture["foreign"]:
        lines.append(f"  !! {FOREIGN_STATE} is also here -- that directory "
                     "belongs to chat_crawl_store.py.")
        lines.append("     The two data models are unrelated; do not mix them.")
    if not picture["state_file"]:
        lines += [
            f"  !! no {STATE_FILENAME} here -- everything below was recovered",
            "     from the store files alone.  The titles of chats without a",
            "     store file, the working order and every 'exported' mark are lost.",
            "     Ask whether the state file can still be uploaded.",
        ]

    lines.append(f"Order : {picture['order']}"
                 + ("" if picture["order_set"] else "   (default, never set)"))
    stale_count = sum(1 for r in picture["records"] if r["status"] == "stale")
    deleted_count = sum(1 for r in picture["records"] if r["status"] == "deleted")
    lines.append(f"Chats : {len(picture['records'])} known -- "
                 f"{len(picture['queued']) - stale_count} listed, "
                 f"{len(started)} started, {len(picture['done'])} exported"
                 + (f", {stale_count} stale" if stale_count else "")
                 + (f", {deleted_count} deleted" if deleted_count else ""))

    if picture["round_state"] == "in progress":
        lines.append(f"Round : IN PROGRESS -- {len(picture['active'])} of at most "
                     f"{ACTIVE_LIMIT} slot(s) in use, {picture['free_slots']} free")
    elif picture["round_state"] == "idle":
        lines.append("Round : IDLE -- no chat is in progress.  Which of the two")
        lines.append("        this is, only you know:")
        lines.append("        * you just finished a round -> export what is ready,")
        lines.append("          hand the files over, ask whether to continue.")
        lines.append("        * you are starting out -> begin up to "
                     f"{ACTIVE_LIMIT} chats from NEXT UP.")
    else:
        lines.append("Round : ALL DONE -- every known chat is exported. Hand over "
                     "and say so.")

    if picture["active"]:
        lines.append("")
        lines.append("IN PROGRESS -- read the next page of these")
        for record in picture["active"]:
            hint = (f"read_conversation page_token {record['token']!r}"
                    if record["token"] else
                    "no token -- see 'status' for this chat")
            lines += _overview_chat_line(record, hint)

    if picture["ready"]:
        lines.append("")
        lines.append("READY TO EXPORT -- every turn held, checked against "
                     "total_turns")
        for record in picture["ready"]:
            lines += _overview_chat_line(
                record, f"export --chat {record['uuid']} "
                        f"--out chat_{record['uuid']}.json")

    if picture["missing"]:
        lines.append("")
        lines.append("MISSING STORE FILES -- marked started, but no <uuid>.json "
                     "is here")
        for record in picture["missing"]:
            lines += _overview_chat_line(record)
        lines.append("  Ask the user to upload exactly these; the turns already "
                     "read are")
        lines.append("  otherwise lost and would have to be fetched again.")

    lines.append("")
    if picture["free_slots"] and picture["next_up"]:
        lines.append(f"NEXT UP -- {picture['free_slots']} free slot(s), "
                     f"{picture['order']}")
        for record in picture["next_up"]:
            hint = ("read_conversation without a page_token, from turn 0"
                    if not record["held"] else
                    f"read_conversation page_token {record['token']!r}")
            lines += _overview_chat_line(record, hint)
    elif not picture["free_slots"]:
        lines.append(f"NEXT UP -- no free slot ({ACTIVE_LIMIT} in use). Finish or "
                     f"export one first.")
        lines.append("          Fewer than three at a time is fine, and with long "
                     "chats it is")
        lines.append("          the better choice.")
    else:
        lines.append("NEXT UP -- nothing listed or stale left.")

    if picture["done"]:
        lines.append("")
        lines.append(f"EXPORTED ({len(picture['done'])}) -- name these when you hand "
                     f"over; the user may file them away")
        for record in picture["done"]:
            lines.append(f"  {record['uuid']}  "
                         f"{record['title'] or '(title unknown)'}")

    travellers = [r for r in started if r["has_store"]]
    lines.append("")
    lines.append("HANDOVER -- what has to reach the next conversation")
    lines.append(f"  {STATE_FILENAME}  -- always, no exception")
    if travellers:
        lines.append(f"  plus {len(travellers)} store file(s) of started chats:")
        for record in travellers:
            lines.append(f"    {record['uuid']}.json")
    lines.append(f"  {1 + len(travellers)} file(s) in total.")
    lines.append(f"  Without {STATE_FILENAME} the working order, every 'exported' "
                 "mark and the")
    lines.append("  titles of chats without a store file are gone.")
    return "\n".join(lines)


def status_report(store: dict[str, Any]) -> str:
    """Render a status summary for one chat."""
    held = held_turns(store)
    total = store["total_turns"]
    missing = missing_turns(store)
    stats = store["stats"]
    chars = sum(len(turn["text"]) for turn in store["turns"].values())

    lines = [f"Chat  : {store['title'] or '(untitled)'}",
             f"UUID  : {store['chat_uuid']}",
             f"URL   : {store['url']}"]
    if total:
        lines.append(f"Turns : {len(held)} of {total} held, {chars} chars"
                     + ("  -- COMPLETE" if not missing else ""))
    else:
        lines.append(f"Turns : {len(held)} held, {chars} chars -- total unknown, "
                     "no page has been ingested yet")
    if missing:
        lines.append(f"Missing: {format_ranges(missing)}")
        # Missing turns beyond the furthest held one are simply unread; only
        # missing turns *below* it are a gap, which needs out-of-order
        # fetching to have happened at all.
        token = gap_token(store)
        if held and missing[0] > held[-1]:
            lines.append(f"  continue with page_token {token!r}" if token else
                         "  no continuation token, yet turns are missing -- the "
                         "furthest page announced an end that total_turns "
                         "contradicts; re-check the format probe")
        else:
            lines.append(f"  gap below the furthest turn held; reopen it with "
                         f"page_token {token!r}" if token else
                         "  gap below the furthest turn held, and no page "
                         "reaches it -- read the chat from the start, or enter "
                         "it at a search result's page_token")
    lines.append(f"Pages : {stats['pages_ingested']} ingested"
                 f"  next={next_token(store) or '- (end reached)'}"
                 f"  prev={prev_token(store) or '-'}")
    if stats["turns_conflicting"]:
        lines.append(f"Warn  : {stats['turns_conflicting']} turn(s) arrived "
                     "twice with different text -- see 'warnings' in the store")
    lines.append(f"Warn  : {len(store['warnings'])} warning(s) recorded")

    unknown = sorted(int(key) for key, turn in store["turns"].items()
                     if turn["role"] == "unknown")
    if unknown:
        lines.append(f"Roles : unknown for turn(s) {format_ranges(unknown)}")
    return "\n".join(lines)


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


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_overview(args: argparse.Namespace) -> int:
    """Print the working picture: where the export stands and what comes next.

    A missing store directory or state file is not an error here.  It is the
    documented start-up case, and the report says how to resolve it.
    """
    print(overview_report(chat_overview(args.store_dir)))
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    """Set the working order, or correct the status of one chat by hand."""
    if not args.order and not args.status:
        print("Nothing to change: pass --order or --chat with --status.",
              file=sys.stderr)
        return 1
    if args.order:
        set_order(args.store_dir, args.order)
        print(f"Working order is now {args.order}.")
    if args.status:
        if not args.chat:
            print("--status needs --chat.", file=sys.stderr)
            return 1
        previous = set_chat_status(args.store_dir, args.chat, args.status)
        print(f"chat {args.chat[:8]}: {previous} -> {args.status}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Write the export document for one chat."""
    path = store_path(args.store_dir, args.chat)
    if not os.path.exists(path):
        print(f"Missing store: {path}", file=sys.stderr)
        return 1
    store = load_store(path)
    if not store["turns"]:
        print("Store holds no turns yet.", file=sys.stderr)
        return 1

    now = args.now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    document = build_export(store, now=now)
    # Without --out the name follows doku 2.3, so the protocol can carry it.
    out_path = args.out or f"{file_stem(store)}.json"
    _write_json_atomic(document, out_path, ".export-")
    print(f"Wrote {len(document['messages'])} turn(s) and "
          f"{len(document['warnings'])} warning(s) to {out_path}")

    # Only a provably complete chat earns 'exported'.  Exporting a partial
    # chat is allowed and has to stay visible as partial.
    if is_complete(store):
        state = load_state(args.store_dir)
        entry = state["chats"].setdefault(args.chat, blank_entry())
        for key, value in blank_entry().items():
            entry.setdefault(key, value)
        entry.update({
            "title":       store["title"] or entry.get("title", ""),
            "exported_updated_at": store["updated_at"],
            "turns":       len(store["turns"]),
            "total_turns": store["total_turns"] or None,
            "end_token":   next_token(store),
            "file":        os.path.basename(out_path),
            "side_files":  [],
            "status":      "exported",
            "exported_at": now,
        })
        save_state(args.store_dir, state)
        print(f"chat {args.chat[:8]} is complete ({store['total_turns']} turns) "
              "and now exported -- the user may file it away.")
    else:
        held, total = len(store["turns"]), store["total_turns"]
        print(f"chat {args.chat[:8]} is PARTIAL: {held} of {total or '?'} turns, "
              f"missing {format_ranges(missing_turns(store)) or 'unknown'}. "
              "Status unchanged; say so when presenting the file.")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    """Answer "what is new?" from a fresh chat list -- read-only."""
    with open(args.raw, "r", encoding="utf-8") as handle:
        records = parse_chat_list(handle.read())
    if not records:
        print("No <chat ...> blocks found in the dump.", file=sys.stderr)
        return 1
    state = load_state(args.store_dir)
    now = args.now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    report = plan_report(state, records, now)
    print("\n".join(format_plan(report, state)))
    for line in project_start_warnings(state):
        print(line, file=sys.stderr)
    return 0


def cmd_map(args: argparse.Namespace) -> int:
    """Record the chats of this scope from a ``recent_chats`` dump."""
    with open(args.raw, "r", encoding="utf-8") as handle:
        records = parse_chat_list(handle.read())
    if not records:
        print("No <chat ...> blocks found in the dump.", file=sys.stderr)
        return 1

    previous_listed = load_state(args.store_dir).get("listed_at", "")
    now = args.now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    state = update_state(args.store_dir, records, now)
    if args.project_created:
        state["project_created_at"] = args.project_created
        save_state(args.store_dir, state)
    for line in project_start_warnings(state):
        print(line, file=sys.stderr)
    without_title = [record["uuid"] for record in records if not record["title"]]
    print(f"{len(records)} chat(s) recorded; {len(state['chats'])} known in total.")
    if previous_listed:
        print(f"Previous reconciliation: {previous_listed[:19]} -- chats new "
              "since then were created after it.")
    if without_title:
        print(f"{len(without_title)} of them without a title -- that is normal, "
              "the title arrives with the first page that is read.")
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    """Merge one or more ``read_conversation`` pages into the stores."""
    with open(args.raw, "r", encoding="utf-8") as handle:
        pages = parse_pages(handle.read())
    if not pages:
        print("No <chat ...> blocks found in the dump.", file=sys.stderr)
        return 1

    identities: list[dict[str, str]] = []
    started: set[str] = set()
    for page in pages:
        path = store_path(args.store_dir, page["uuid"])
        store = load_store(path) if os.path.exists(path) else new_store(page["uuid"])
        outcome = merge_page(store, page)
        os.makedirs(args.store_dir, exist_ok=True)
        save_store(store, path)

        identities.append({"uuid": page["uuid"], "url": page["url"],
                           "updated_at": page["updated_at"],
                           "title": page["title"]})
        started.add(page["uuid"])

        held = len(store["turns"])
        total = store["total_turns"]
        note = f"{len(outcome['added'])} new"
        if outcome["repeated"]:
            note += f", {len(outcome['repeated'])} already held"
        if outcome["conflicting"]:
            note += f", {len(outcome['conflicting'])} CONFLICTING"
        print(f"{page['uuid'][:8]}  turns {page['range'] or '?'}: {note}"
              f"  -> {held}/{total or '?'} held"
              + ("  COMPLETE" if is_complete(store) else ""))
        if is_complete(store):
            print(f"  every turn of {page['uuid'][:8]} is now held; export it.")
        elif total:
            missing = missing_turns(store)
            token = gap_token(store) or next_token(store)
            print(f"  missing: {format_ranges(missing)}"
                  f"  next token: {token or '(none - see status)'}")

    update_state(args.store_dir, identities)
    # Reading a page IS taking up a chat, so ingest is what marks it started.
    for uuid in sorted(started):
        if set_chat_status(args.store_dir, uuid, "started",
                           only_from=("listed", "stale")) is not None:
            print(f"chat {uuid[:8]} is now started.", file=sys.stderr)
    return 0


def _resolve_paths(args: argparse.Namespace) -> list[str] | None:
    """Return the store paths selected by --chat, or None on error."""
    if getattr(args, "chat", ""):
        path = store_path(args.store_dir, args.chat)
        if not os.path.exists(path):
            print(f"Missing store: {path}", file=sys.stderr)
            return None
        if try_load_store(path) is None:
            print(f"Not a chat store of this script: {path}", file=sys.stderr)
            return None
        return [path]

    if not os.path.isdir(args.store_dir):
        print(f"Store directory does not exist: {args.store_dir}", file=sys.stderr)
        return None
    paths = []
    for name in sorted(os.listdir(args.store_dir)):
        if not name.endswith(".json") or name in (STATE_FILENAME, FOREIGN_STATE):
            continue
        path = os.path.join(args.store_dir, name)
        if try_load_store(path) is None:
            print(f"Skipping foreign JSON file (not a chat store): {name}",
                  file=sys.stderr)
            continue
        paths.append(path)
    if not paths:
        print("No stores found.", file=sys.stderr)
        return None
    return paths


def cmd_status(args: argparse.Namespace) -> int:
    """Print a status report for one or all chats."""
    if foreign_state_present(args.store_dir):
        print(f"Warning: {FOREIGN_STATE} is present -- this directory belongs "
              "to chat_crawl_store.py. Do not mix the two.", file=sys.stderr)
    paths = _resolve_paths(args)
    if paths is None:
        return 1
    for path in paths:
        print(status_report(load_store(path)))
        print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Assemble the command line interface."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--store-dir", default="./store",
                        help="directory holding the per-chat JSON stores")
    sub = parser.add_subparsers(dest="command", required=True)

    p_overview = sub.add_parser("overview",
                                help="where the export stands and what comes next")
    p_overview.set_defaults(func=cmd_overview)

    p_state = sub.add_parser("state", help="set the working order or a chat status")
    p_state.add_argument("--order", default="", choices=("", *ORDER_VALUES),
                         help="direction in which the chats are worked through")
    p_state.add_argument("--chat", default="", help="chat UUID for --status")
    p_state.add_argument("--status", default="", choices=("", *CHAT_STATUSES),
                         help="set the status of one chat by hand")
    p_state.set_defaults(func=cmd_state)

    p_plan = sub.add_parser("plan", help="what is new, and how to fetch it "
                                        "(writes nothing)")
    p_plan.add_argument("--raw", required=True,
                        help="file holding a fresh recent_chats dump")
    p_plan.add_argument("--now", default="", help="timestamp instead of the clock")
    p_plan.set_defaults(func=cmd_plan)

    p_map = sub.add_parser("map", help="record this scope's chats from recent_chats")
    p_map.add_argument("--raw", required=True, help="file holding the raw dump")
    p_map.add_argument("--project-created", default="", dest="project_created",
                       help="the source project's own creation date, read off "
                            "a probe export")
    p_map.add_argument("--now", default="",
                       help="timestamp to record instead of the clock")
    p_map.set_defaults(func=cmd_map)

    p_ingest = sub.add_parser("ingest", help="merge read_conversation pages")
    p_ingest.add_argument("--raw", required=True, help="file holding the raw dump")
    p_ingest.set_defaults(func=cmd_ingest)

    p_status = sub.add_parser("status", help="report held turns and gaps")
    p_status.add_argument("--chat", default="", help="restrict to one chat UUID")
    p_status.set_defaults(func=cmd_status)

    p_export = sub.add_parser("export", help="write the export document")
    p_export.add_argument("--chat", required=True, help="chat UUID")
    p_export.add_argument("--out", default="", help="output file (default: stdout)")
    p_export.add_argument("--now", default="",
                          help="timestamp to record instead of the clock")
    p_export.set_defaults(func=cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
