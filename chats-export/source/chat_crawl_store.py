#!/usr/bin/env python3
"""Incremental store for reconstructing chat transcripts from search snippets.

===========================================================================
@Claude: OPERATING INSTRUCTIONS -- read this part, then start working.
===========================================================================

This script is your bookkeeping tool for exporting past chats.  The chat
search tools (``conversation_search`` / ``recent_chats``) never return a
complete transcript, only overlapping *snippets*.  This script stitches
those snippets back together across many search calls and, once nothing
more can be found, writes a JSON export file.

You cannot delegate the searching itself: the search tools live in your
runtime, not in the container.  Every snippet must pass through your
context.  The script's job is to remember everything so you do not have to.

THE STORE DIRECTORY
-------------------
``--store-dir`` holds one file per chat plus one state file:

*   ``<uuid>.json`` -- the reconstruction of one chat: its segments, which
    edges are still worth querying, which queries were already spent.
*   ``crawl-state.json`` -- every chat UUID ever seen in any dump, with its
    title, timestamp and working status, plus the direction in which the
    chats are being worked through.

``crawl-state.json`` is only partly regenerable.  With every ``<uuid>.json``
still in place, ``overview`` recovers those chats' titles and progress from
the store files themselves.  What is gone for good without the state file:
every ``done`` mark, the working order, and the titles of all chats that
never got a store file -- exactly the seed vocabulary the bootstrap step
paid searches for.  So treat it as precious anyway.

Keep the directory clean: only store files and the state file belong there.
In particular, never write an export (``--out``) into ``--store-dir`` --
foreign JSON files are skipped with a warning, but they do not belong there.
A directory from an older schema is upgraded automatically on first contact,
including a legacy ``index.json``, which is folded into the state file and
renamed to ``index.json.migrated``.

SESSION START -- do this before anything else
---------------------------------------------
A big export does not fit into one conversation, so most sessions are a
continuation of an earlier one.  Find out which case you are in first::

    python chat_crawl_store.py --store-dir ./store overview

The report names the case and the next action.  Three situations need a
question put to the user, and you must not guess your way past them:

*   **Nothing there at all.**  Ask: a fresh export, or continuing earlier
    work?  On a fresh export also ask whether to work through the chats
    oldest-first or newest-first, and record the answer with
    ``state --order <choice>``.  On a continuation ask for the upload of
    ``crawl-state.json`` plus the ``<uuid>.json`` of every started chat.
*   **A state file is there.**  Continue; do not ask.  The one exception is
    a store *you* built earlier in this same conversation and that was merely
    interrupted -- then ask whether to continue or to start over empty,
    because only you know that no upload happened.
*   **Chats marked ``started`` whose ``<uuid>.json`` is absent.**  Ask for
    exactly those files by name.  Their crawl progress is otherwise gone.

UPLOAD PROBE -- once per continuation, before trusting anything uploaded
    Whether files the user uploads into the conversation are readable by
    this script in the container is *not* documented anywhere.  So check,
    the same way the format probe checks the snippet format: list the
    directory the user uploaded into and confirm the files are really there
    and really parse.  Report the result.

    Never point ``--store-dir`` at the upload directory and never work in
    place: COPY the uploaded files into your working store directory
    (e.g. ``./store``) first, then run ``overview`` there to confirm the
    copies parse.  The upload location is reported to be read-only, so
    working in it would fail at the first write -- in the best case
    immediately, in the worst case mid-round.

    Where that location is, is NOT documented by Anthropic.  Community
    reverse-engineering reports ``/mnt/user-data/uploads`` on claude.ai, and
    that is the first place worth looking, but treat it as a guess: if the
    files are not there, search rather than conclude they were never
    uploaded.  Copying instead of working in place is the right move either
    way, whatever the path turns out to be.

    They may well arrive under a different name -- ``.txt`` appended,
    because a chat upload of a ``.json`` file is not always accepted.
    Renaming while copying is fine; changing the content is not.
    If the files are nowhere in the filesystem, stop and report it.  Do not
    improvise: the documented alternative is to keep the store in the
    project knowledge of a claude.ai project, at the price of the files
    permanently occupying context.

    One asymmetry decides how far you may go.  Writing ``crawl-state.json``
    out again from what you can see in the conversation is acceptable: it is
    small and machine-generated.  Doing that with a ``<uuid>.json`` is not --
    those hold reconstructed chat text, and retyping snippets is exactly what
    this script exists to prevent.  Rather stop and say so.

WORKFLOW
--------
1.  Run the format probe below before the first real ingest.  Then list the
    chats: call ``recent_chats``.  Write the raw tool output verbatim into a
    file and run ``ingest``.  Never retype or reformat a snippet -- copy it
    exactly, otherwise the reconstruction silently degrades.  Use a quoted
    heredoc so nothing is expanded:

        cat > dump.txt <<'RAWEOF'
        <chat url='...' updated_at='...'>Title: ...
        ...
        RAWEOF
        python chat_crawl_store.py --store-dir ./store ingest \
            --raw dump.txt --query "the query you used"

    For ``recent_chats`` output pass ``--query ""``.

1a. BOOTSTRAP DISCOVERY -- finding titles/UUIDs you have no search terms for yet.

    ``recent_chats`` lists every chat's UUID and timestamp, but for most
    chats older than the first few it returns an empty content block --
    no title, no snippet.  You cannot search for a chat by a term you do
    not yet know occurs in it, and the UUID itself is not a search term
    (it never appears in the chat text).

    The fix is indirection: query ``conversation_search`` with broad
    *topic-cluster* words drawn from the project's domain (skim any
    project knowledge, file names, or already-known chat titles for
    vocabulary) rather than anything specific to one chat.  Each such
    query, with a generous ``max_results``, tends to surface several
    chats at once, each carrying its real title in the result header.
    Two or three broad queries from unrelated topic angles typically
    reveal many previously-"empty" UUIDs at once.

    Record every (uuid, title) pair you see this way, even from chats
    you are not ready to ingest yet -- title words are exactly the seed
    vocabulary for a targeted query on that chat later (see step 3).
    Ingest the dump immediately with ``--query`` set to the cluster term
    used, same as any other search result; do not discard the parts of
    the dump belonging to chats you were not looking for.

    This step is expensive in tokens relative to what it stores (a wide
    net returns much you will not keep), so budget it deliberately: a
    handful of cluster queries to map the whole project's titles, not
    one per chat.  Prefer breadth here (many titles, shallow) and leave
    depth (full reconstruction) to the targeted loop in steps 3-4.

2.  Pick the chats to work on -- at most ``ACTIVE_LIMIT`` (three) at a time.
    ``overview`` names them under ACTIVE and nominates the next candidates
    under NEXT UP, neighbours first in the chosen order.  Read it at the
    start of every round instead of remembering: the state on disk is the
    truth, your recollection of it is not.

    Three is an upper bound, not a quota.  With very long chats, start one
    and see what it costs before opening a second.

    Two reasons for the cap, and both matter:
      * Context.  Every snippet of every chat passes through you.
      * Handover.  Only started chats have to travel to the next
        conversation, and a chat upload is documented to take at most 20
        files.  Three active chats keep the handover at four files.

    A dump fetched for one chat regularly contains others.  Ingest all of it
    -- the script files each chat separately and keeps the titles.  But a
    chat that merely grew that way is *not* one you started: it stays
    ``untouched`` and does not occupy a slot.

3.  For each active chat, ask what to search next:

        python chat_crawl_store.py --store-dir ./store queries \
            --chat <uuid> -n 5

    Take one suggestion, pass it to ``conversation_search`` unchanged, dump
    the result, ingest it with ``--query`` set to that exact suggestion.
    The exact string matters: it is how the script credits the right edge.

    ``queries`` is also what marks the chat ``started``.  Do not run it on a
    chat you are not actually taking up.

4.  Repeat step 3.  Watch ``status``.  An edge marked ``~`` has produced
    nothing new several times in a row; stop querying it.  When a chat has
    no open edge left, ``overview`` moves it to READY TO EXPORT and the slot
    is free.

5.  Export every chat that is ready:

        python chat_crawl_store.py --store-dir ./store export \
            --chat <uuid> --out chat_<uuid>.json

    The export is what turns a chat into ``done``, and only an exhausted
    crawl earns that.  Exporting earlier is allowed -- then the chat keeps
    its status and you say plainly that it is unfinished.

6.  Round over.  Hand the files to the user, report the standing, and ask
    whether to continue.  See ROUNDS AND HANDOVER below.

===========================================================================
FORMAT PROBE -- do this once per environment, before trusting the parser.
===========================================================================

Everything this script knows about snippet packaging was observed in one
environment at one point in time.  Anthropic changes these details, and
claude.ai, Claude Desktop and Claude Code do not have to agree.  A wrong
assumption here does not crash anything -- it silently produces a damaged
transcript, which is far worse.  So spend two searches on checking.

Probe 1 -- a snippet from the MIDDLE of a chat:
    Call ``conversation_search`` with any topic term.  Look at the raw
    result and answer:
      * How does the block header look?  A ``Content:`` line?  One ``Title:``
        line or a repeated title?
      * What marks a speaker turn -- ``H: `` / ``A: `` or ``Human: `` /
        ``Assistant: ``?  Is there a blank after the colon?
      * Does the passage jump somewhere else mid-text?  If so, what marks
        the jump: three ASCII dots or the single character U+2026?
      * Are ``<``, ``>`` and ``&`` written literally or as HTML entities?

Probe 2 -- a snippet from the START of a chat:
    Call ``recent_chats`` with ``n=1``.  Its header format usually differs
    from probe 1.  Confirm that the first turn carries a speaker label and
    that nothing precedes it.

If any answer contradicts the OBSERVED FORMATS section below, stop and tell
the user before ingesting anything.  Naming the exact difference is far more
useful than a half-correct export.

If the probes pass, do not throw their dumps away: they are valid search
results.  Ingest them like any other dump (probe 1 with ``--query`` set to
the term used, probe 2 with ``--query ""``) -- otherwise the two searches
they cost are wasted.

ROUNDS AND HANDOVER
-------------------
The container filesystem is wiped between sessions, so the store has to
travel through the user by hand.  Work in *rounds* and hand over at the end
of each one; a round is at most the three active chats.

Do NOT wait for the context to run out.  You cannot see it run out.  On
claude.ai a long conversation does not stop at the limit, it summarises its
earlier parts and continues -- so the moment you would be waiting for may
never arrive, and what degrades instead is your grip on these instructions.
That is why the round, not a context signal, drives the handover.  It also
makes the summarising harmless: everything that matters is on disk, so a
fresh ``overview`` restores the full picture, and this file can simply be
read again.

At the start, tell the user they may interrupt at any time; otherwise you
work on until the round ends or nothing is left to crawl.  If they do
interrupt, run this handover procedure -- do not just stop.

The handover itself:

*   Export what is ready and offer every export file for download.  Name the
    files that are ``done``: the user can move those out of the way for good.
*   Hand back ``crawl-state.json`` **always**, together with the
    ``<uuid>.json`` of every chat still ``started``.  ``overview`` lists
    exactly these under HANDOVER.  Without the state file the titles, the
    working order and every ``done`` mark are gone and the next session
    starts from zero -- with all the ``<uuid>.json`` files still present.
*   Say how many chats are done, how many are started, how many are still
    untouched.  Mention that these are JSON files and ask whether the user
    needs them with a ``.txt`` extension to get them back in next time.
*   Store files of ``untouched`` chats stay behind **by design**, even when
    they already carry text picked up as by-catch in other chats' dumps.
    Only started chats travel; that is what keeps the handover at four
    files.  The price is real and you should name it once at the handover
    when it applies: whatever those chats accumulated is discarded with the
    container, and taking one of them up later re-searches that text.  The
    state file keeps their titles, so nothing but search effort is lost.
*   Then ask whether to continue.

HOW TO REPORT TO THE USER
-------------------------
``report`` prints every warning in full.  That output is for *you*, not for
the user.  Read it, judge it, and tell the user only what matters:

*   Say nothing about warnings when they are routine (an unlabelled leading
    fragment, an ambiguous overlap that resolved later, a prose ellipsis
    flagged as a possible gap).
*   Speak up when something needs a human eye: a header form the parser did
    not recognise, a segment with no speaker labels at all, a gap split that
    looks wrong, an odd fence count, or a chat that stayed in many segments.
*   Group by cause and name the affected chat and segment.  Then advise --
    for example, that a gap is probably unrecoverable and worth patching by
    hand, or that a different search term might still close it.
*   Never dump the raw warning list and never ask the user to acknowledge
    warnings one by one.  Warnings also travel into the export file, so the
    later import step can consider them again.

Keep a running note of the work itself, separately from the warnings:

*   Say at the outset that the user may interrupt whenever they like.
*   One short line on every status change -- which chat you have just taken
    up, which one is finished.  A line, not a paragraph, and no repetition
    of the whole standing; that comes at the handover.
*   Never report a chat as finished that you have not exported.  ``done``
    means the file is written, not that the chat looked complete.

WHAT NOT TO DO
--------------
*   Do not edit store files by hand.
*   Do not "clean up" snippets before ingesting them.
*   Do not claim a chat is complete.  The end of a chat cannot be detected
    from snippets; only its beginning can.  Segment order is unknown except
    for the segment carrying ``chat_start``.
*   Do not take search tokens from more than three chats at a time, however
    tempting the fourth title looks.
*   Do not hand the store back without ``crawl-state.json``.  The
    ``<uuid>.json`` files alone are not a resumable crawl.
*   Do not report a chat as ``done`` that was never exported.
*   Do not wait for a signal that the context is running out.  There is
    none; work in rounds instead.

===========================================================================
DESIGN NOTES -- for the developer maintaining this script.
===========================================================================

OBSERVED FORMATS
----------------
Everything below was seen in claude.ai in August 2026 and is an assumption,
not a guarantee.  Where a cheap tolerance existed it was implemented rather
than relying on the observation.

*   ``conversation_search`` blocks start with ``Title: <full title>`` and
    repeat the title on the next line.
*   ``recent_chats`` blocks start with a ``Content:`` line, then
    ``Title: <emoji> <truncated title>`` (truncation uses U+2026) and no
    repetition.
*   Speaker labels appeared as ``H: `` and ``A: `` (the latter sometimes
    with two blanks).  Other environments are reported to use ``Human: ``
    and ``Assistant: ``; both spellings are accepted.
*   ``<``, ``>`` and ``&`` arrived HTML-escaped (``&gt;``, ``&amp;``) and are
    unescaped on ingest.  This is a *verified* observation, not a guess: the
    same passages contained ``>`` literally in the original chat.  The cost
    of being wrong is asymmetric -- without unescaping every code sample
    containing ``>`` or ``&`` would be corrupted permanently, whereas a chat
    that literally discusses ``&amp;`` merely loses that escaping.
*   A block body may contain several *non-adjacent* passages joined by a gap
    marker.  Only one instance was ever observed, and its exact character
    could not be determined from the rendering, so both three-or-more ASCII
    dots and U+2026 are treated as markers.  Each passage becomes its own
    fragment; the marker itself is discarded and the split is logged.
*   Only a block whose content begins directly with a user label starts at
    the beginning of the chat.

MERGING
-------
Stored text is always the text as delivered, minus the search tool's own
packaging (block header, gap markers, HTML entities).  Whitespace collapsing
is applied only transiently during comparison, never when writing to disk,
because the search backend normalises whitespace inconsistently between
calls.

Fragments shorter than ``--min-overlap`` can never be joined by overlap:
they are either recognised as ``contained`` or start an isolated segment.
That is intentional -- a false join corrupts the reconstruction permanently,
whereas an isolated segment can still be absorbed later.

An ambiguous overlap (boundary text occurring more than once) never discards
a fragment.  Every segment is checked in both directions and the longest
*unique* overlap wins; if none exists the fragment is kept as a new segment.

Consolidation can remove a segment, so ``merge_fragment`` returns a ``remap``
mapping from removed ids to their survivor.  Callers tracking segment ids
across several merges must apply it.

EDGE BOOKKEEPING
----------------
``queries`` records each suggestion in ``pending_queries`` together with the
edge it came from.  ``ingest --query`` credits that edge only when *the
segment owning it* actually grew -- growth elsewhere in the same dump does
not count, or a dead edge would never be recognised as such.  All blocks of
one chat in a dump are merged before the edge is settled, so a dump split
across several blocks is accounted once.  An edge is *exhausted* at
``BARREN_LIMIT`` fruitless queries.

``chat_start`` is a segment field of its own and is never inferred from
``edges.head.closed``: closing an edge by hand means "stop querying here",
which is not the same claim as "this is where the chat begins".

STATUS MECHANICS
----------------
``crawl-state.json`` carries one status per chat: ``untouched``, ``started``
or ``done``.

``queries`` is what sets ``started``, never ``ingest``.  A dump fetched for
one chat routinely grows two or three others, and those must stay
``untouched``: asking for search tokens is the act of working on a chat,
receiving text by accident is not.  Without that distinction the
``ACTIVE_LIMIT`` cap would be gone after two searches.

``export`` sets ``done`` only when ``crawl_finished`` holds.  Exporting an
unfinished chat is legitimate -- context runs out -- and has to stay visible
as unfinished, so the status remains ``started``.

``done`` is a different claim from the ``CRAWL FINISHED`` line in ``status``.
The latter means "no edge is worth querying any more"; ``done`` means
"exported, and the file may leave the store directory".  That is why the
status lives in the state file rather than in the per-chat store: a finished
chat whose ``<uuid>.json`` has been filed away must not look untouched the
next time around.

``state --status`` is the manual override for what no script can judge: a
chat the user calls good enough, a status that drifted, a file that came
back under another name.  ``state --order`` may be changed at any time; it
only steers which ``untouched`` chat is nominated next.

``overview`` derives everything and changes no crawl decision.  Where it
cannot know, it says so instead of guessing: an idle round looks exactly the
same whether a round just ran dry or none has begun, and only the reader can
tell the two apart.  A store file with no entry in the state file is reported
as *recovered* and counted as ``started`` without being written out; the next
command touching that chat persists the record anyway.

The one thing ``overview`` does write is the one-off schema migration every
command shares through ``load_state``: a legacy ``index.json`` is folded into
the state file and renamed.  That is repair, not bookkeeping -- it is
idempotent, it decides nothing, and running it from a read-only report is
better than leaving the directory in a state where the next scan mistakes
the legacy file for a chat store.

Usage
-----
    python chat_crawl_store.py overview
    python chat_crawl_store.py state   [--order oldest-first|newest-first] \
                                       [--chat <uuid> --status STATUS]
    python chat_crawl_store.py ingest  --raw dump.txt [--query Q]
    python chat_crawl_store.py status  [--chat <uuid>]
    python chat_crawl_store.py queries --chat <uuid> [-n 5]
    python chat_crawl_store.py close   --chat <uuid> --segment <id> \
                                       --side tail [--reopen]
    python chat_crawl_store.py report  [--chat <uuid>]
    python chat_crawl_store.py export  --chat <uuid> [--out file] \
                                       [--predecessor UUID] [--successor UUID]
"""

from __future__ import annotations

import argparse
import functools
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

SCHEMA_VERSION       = 4
DEFAULT_MIN_OVERLAP  = 60       # minimum overlap length in normalised chars
EDGE_WINDOW          = 400      # chars inspected at a segment edge for tokens
STATE_FILENAME       = "crawl-state.json"
STATE_SCHEMA_VERSION = 1
ACTIVE_LIMIT         = 3        # chats queried at the same time (upper bound)
BARREN_LIMIT         = 3        # fruitless queries before an edge is exhausted
TITLE_MATCH_CHARS    = 15       # chars compared to detect a repeated title
HEADER_SEARCH_LINES  = 6        # how far to look for the 'Title:' line
NEAR_GAP_EXAMPLES    = 2        # near-miss examples kept per parsed block
PENDING_QUERY_LIMIT  = 50       # cap on remembered but unused suggestions
GAP_CONTEXT_CHARS    = 40       # context shown around a gap in warnings

# Opening tag of a chat block; attributes are parsed order-independently.
CHAT_OPEN_PATTERN = re.compile(r"<chat\b([^>]*)>")
CHAT_CLOSE_TAG    = "</chat>"
ATTR_PATTERN      = re.compile(r"(\w+)\s*=\s*['\"]([^'\"]*)['\"]")

# Header line carrying the chat title.
TITLE_LINE_PATTERN = re.compile(r"^\s*Title:\s*(.*)$")

# Speaker labels.  Both the short and the long spelling are accepted because
# they differ between environments.  The trailing blank is mandatory: "H:"
# without it is ordinary text, not a label.  Longest alternatives come first
# so that "Human:" is never matched as "H" plus a stray "uman:".
LABEL_PATTERN = re.compile(r"^(Human|Assistant|H|A):[ \t]")
LABEL_ROLES   = {"H": "user", "Human": "user",
                 "A": "assistant", "Assistant": "assistant"}

# Gap marker: three or more ASCII dots, or one or more U+2026, glued between
# non-space characters.  A standalone ellipsis surrounded by whitespace is
# ordinary prose or a code ellipsis.
_ELLIPSIS        = r"(?:\.{3,}|\u2026+)"
GAP_PATTERN      = re.compile(rf"(?<=\S){_ELLIPSIS}(?=\S)")
NEAR_GAP_PATTERN = re.compile(rf"(?:(?<=\S){_ELLIPSIS}(?=\s)|"
                              rf"(?<=\s){_ELLIPSIS}(?=\S))")

FENCE_PREFIX = "```"

# Tokens: a word optionally continued by dotted parts (identifiers such as
# ``os.path`` or ``store.json``).  A dot is only kept *between* word
# characters, so sentence-final punctuation never sticks to a token.
TOKEN_PATTERN = re.compile(r"[A-Za-z_\u00c0-\u024f]\w*(?:\.\w+)*")

STOPWORDS = {
    # English
    "the", "and", "for", "that", "this", "with", "from", "have", "has", "not",
    "are", "was", "were", "you", "your", "but", "can", "will", "would", "there",
    "then", "than", "which", "when", "what", "into", "also", "only", "more",
    "been", "they", "them", "these", "those", "such", "here", "does", "did",
    # German
    "und", "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen",
    "einem", "einer", "eines", "ist", "sind", "war", "waren", "nicht", "auch",
    "aber", "oder", "wenn", "dann", "als", "wie", "von", "vom", "mit", "auf",
    "aus", "bei", "nach", "vor", "durch", "fuer", "für", "sich", "man", "wir",
    "sie", "ich", "dass", "noch", "schon", "sehr", "kann", "koennen", "können",
    "soll", "sollte", "wird", "werden", "wurde", "hier", "dort", "diese",
    "dieser", "dieses", "einfach", "immer", "mal", "ganz", "also", "wobei",
}


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Collapse every whitespace run to a single space and strip the ends.

    Used exclusively for comparison; never applied to stored content.
    """
    return re.sub(r"\s+", " ", text).strip()


@functools.lru_cache(maxsize=512)
def normalize_with_map(text: str) -> tuple[str, tuple[int, ...]]:
    """Normalise *text* and return the mapping normalised index -> original index.

    Results are cached (strings are immutable), which makes the repeated
    normalisation inside merging and consolidation cheap.
    """
    out_chars: list[str] = []
    out_map: list[int] = []
    in_ws = False
    for idx, char in enumerate(text):
        if char.isspace():
            if not in_ws:
                out_chars.append(" ")
                out_map.append(idx)
                in_ws = True
            continue
        in_ws = False
        out_chars.append(char)
        out_map.append(idx)

    start = 0
    end = len(out_chars)
    while start < end and out_chars[start] == " ":
        start += 1
    while end > start and out_chars[end - 1] == " ":
        end -= 1
    return "".join(out_chars[start:end]), tuple(out_map[start:end])


def norm_of(text: str) -> str:
    """Shorthand returning only the normalised form of *text*."""
    return normalize_with_map(text)[0]


_KMP_SENTINEL = "\x00"


def find_overlap(left: str, right: str, min_len: int = DEFAULT_MIN_OVERLAP) -> int:
    """Return the length of the longest suffix of *left* that prefixes *right*.

    Both arguments are expected to be already normalised.  Returns 0 when no
    overlap of at least *min_len* characters exists.

    Implemented via the KMP prefix function over ``right[:m] + SEP + left[-m:]``
    which is O(n) instead of the quadratic endswith scan.
    """
    m = min(len(left), len(right))
    if m < min_len or min_len <= 0:
        return 0
    pattern = right[:m]
    tail = left[-m:]
    if _KMP_SENTINEL in pattern or _KMP_SENTINEL in tail:
        for length in range(m, min_len - 1, -1):
            if left.endswith(right[:length]):
                return length
        return 0

    combined = pattern + _KMP_SENTINEL + tail
    prefix = [0] * len(combined)
    k = 0
    for i in range(1, len(combined)):
        while k and combined[i] != combined[k]:
            k = prefix[k - 1]
        if combined[i] == combined[k]:
            k += 1
        prefix[i] = k
    return k if k >= min_len else 0


def _is_unique(haystack: str, needle: str) -> bool:
    """True when *needle* occurs exactly once inside *haystack*."""
    if not needle:
        return False
    first = haystack.find(needle)
    if first < 0:
        return False
    return haystack.find(needle, first + 1) < 0


# ---------------------------------------------------------------------------
# Code fence handling
# ---------------------------------------------------------------------------

def fence_spans(text: str) -> list[tuple[int, int]]:
    """Return character ranges of *text* that lie inside triple-backtick fences.

    Fence delimiter lines count as inside, so that a marker sitting on the
    delimiter itself is never treated as ordinary content.
    """
    spans: list[tuple[int, int]] = []
    offset = 0
    inside = False
    span_start = 0
    for line in text.splitlines(keepends=True):
        is_delim = line.strip().startswith(FENCE_PREFIX)
        if is_delim and not inside:
            inside = True
            span_start = offset
        elif is_delim and inside:
            inside = False
            spans.append((span_start, offset + len(line)))
        offset += len(line)
    if inside:
        spans.append((span_start, offset))
    return spans


def count_fence_delimiters(text: str) -> int:
    """Count triple-backtick delimiter lines in *text*.

    An odd count means the snippet was cut inside a code block, in which case
    inside and outside are swapped for everything that follows.
    """
    return sum(1 for line in text.splitlines()
               if line.strip().startswith(FENCE_PREFIX))


def in_spans(position: int, spans: list[tuple[int, int]]) -> bool:
    """True when *position* falls inside one of the *spans*."""
    return any(start <= position < end for start, end in spans)


# ---------------------------------------------------------------------------
# Snippet header and gap handling
# ---------------------------------------------------------------------------

def _title_key(text: str) -> str:
    """Comparison key for a title: leading non-word chars dropped, collapsed."""
    stripped = re.sub(r"^[^\w]+", "", normalize_text(text))
    return stripped[:TITLE_MATCH_CHARS]


def strip_tool_header(body: str, **kwargs) -> tuple[str, bool, str, list[str]]:
    """Remove the search tool's block header from *body*.

    Rules
    -----
    1.  Everything up to and including the ``Title:`` line is header.
    2.  The line following it is a repetition of the title when its first
        ``TITLE_MATCH_CHARS`` characters match the title and it does not
        start with a speaker label.  Dropping it is logged, because a format
        change could otherwise silently swallow real content.
    3.  The content starts at the chat's beginning exactly when the first
        non-blank line after the header carries a user label at the very
        start of the line.

    Returns
    -------
    tuple
        ``(content, starts_at_chat_begin, title, warnings)``.
    """
    warnings: list[str] = []
    lines = body.splitlines()

    title = ""
    title_index = -1
    for index, line in enumerate(lines[:HEADER_SEARCH_LINES]):
        match = TITLE_LINE_PATTERN.match(line)
        if match:
            title = match.group(1).strip()
            title_index = index
            break

    if title_index < 0:
        warnings.append("no 'Title:' line found in the block header; the block "
                        "was kept unchanged -- the snippet format may have changed")
        cursor = 0
    else:
        cursor = title_index + 1

    # Rule 2: drop a repeated title line.
    if title_index >= 0 and cursor < len(lines):
        candidate = lines[cursor]
        if candidate.strip() and not LABEL_PATTERN.match(candidate):
            key = _title_key(candidate)
            if key and key == _title_key(title):
                warnings.append(f"dropped a line repeating the title: "
                                f"{normalize_text(candidate)[:60]!r}")
                cursor += 1

    # Rule 3: chat start detection on the first non-blank line.
    probe = cursor
    while probe < len(lines) and not lines[probe].strip():
        probe += 1
    starts_at_begin = False
    if probe < len(lines):
        match = LABEL_PATTERN.match(lines[probe])
        starts_at_begin = bool(match) and LABEL_ROLES[match.group(1)] == "user"

    content = "\n".join(lines[cursor:])
    if not any(LABEL_PATTERN.match(line) for line in lines[cursor:]):
        warnings.append("no speaker label found in the block; roles cannot be "
                        "derived for this fragment")

    if __debug__ and "debug" in kwargs:
        print(f"[header] title={title!r} start={starts_at_begin} "
              f"dropped_lines={cursor}", file=sys.stderr)

    return content, starts_at_begin, title, warnings


def _context_of(text: str, start: int, end: int) -> str:
    """Return a short normalised context window around a text position."""
    left = max(0, start - GAP_CONTEXT_CHARS)
    return normalize_text(text[left:end + GAP_CONTEXT_CHARS])


def split_gap_markers(text: str, **kwargs) -> tuple[list[str], list[str]]:
    """Split *text* at gap markers and report both splits and near-misses.

    A gap marker is an ellipsis glued between two non-space characters and
    located outside a code fence.  The marker itself is discarded; the
    surrounding passages are returned as separate pieces because they are not
    adjacent in the original chat.

    Every split is logged: a wrong split destroys adjacency permanently and
    would otherwise be invisible.  Near-misses are logged too, but capped at
    ``NEAR_GAP_EXAMPLES`` examples plus a count, because prose ellipses are
    common and would otherwise flood the store.

    Returns
    -------
    tuple
        ``(pieces, warnings)`` -- *pieces* never contains blank strings.
    """
    warnings: list[str] = []
    spans = fence_spans(text)

    if count_fence_delimiters(text) % 2:
        warnings.append("odd number of code fence delimiters; the snippet was "
                        "probably cut inside a code block, so gap and label "
                        "detection may be inverted after that point")

    cut_points = [match.span() for match in GAP_PATTERN.finditer(text)
                  if not in_spans(match.start(), spans)]

    near_misses = [match for match in NEAR_GAP_PATTERN.finditer(text)
                   if not in_spans(match.start(), spans)]
    for match in near_misses[:NEAR_GAP_EXAMPLES]:
        warnings.append("possible gap marker not split (whitespace on one "
                        f"side): {_context_of(text, match.start(), match.end())}")
    if len(near_misses) > NEAR_GAP_EXAMPLES:
        warnings.append(f"{len(near_misses) - NEAR_GAP_EXAMPLES} further "
                        "asymmetric ellipses in this block were not logged")

    if not cut_points:
        return ([text] if text.strip() else []), warnings

    for start, end in cut_points:
        warnings.append("split at a gap marker: "
                        f"{_context_of(text, start, end)}")

    pieces = []
    previous = 0
    for start, end in cut_points:
        pieces.append(text[previous:start])
        previous = end
    pieces.append(text[previous:])

    if __debug__ and "debug" in kwargs:
        print(f"[gap] split into {len(pieces)} piece(s)", file=sys.stderr)

    return [piece for piece in pieces if piece.strip()], warnings


# ---------------------------------------------------------------------------
# Raw tool output parsing
# ---------------------------------------------------------------------------

def uuid_from_url(url: str) -> str:
    """Extract the chat UUID from a chat URL."""
    return url.rstrip("/").rsplit("/", 1)[-1]


def parse_tool_output(raw_text: str, **kwargs) -> list[dict[str, Any]]:
    """Parse a raw dump of conversation_search / recent_chats output.

    Each ``<chat ...>`` block yields one entry whose ``fragments`` list holds
    the block's contiguous passages.  HTML entities are resolved, the block
    header is removed and gap markers are used as passage separators.  A dump
    may well contain several blocks of the same chat; callers should group by
    ``uuid`` before settling any edge bookkeeping.

    Returns
    -------
    list of dict
        Entries with ``url``, ``uuid``, ``updated_at``, ``kind``, ``title``,
        ``fragments`` (list of ``{"text", "is_chat_start"}``) and ``warnings``.
    """
    results: list[dict[str, Any]] = []
    cursor = 0
    for match in CHAT_OPEN_PATTERN.finditer(raw_text):
        if match.start() < cursor:
            continue
        attrs = dict(ATTR_PATTERN.findall(match.group(1)))
        warnings: list[str] = []

        if "url" not in attrs:
            print(f"Warning: <chat> block without url attribute at offset "
                  f"{match.start()} skipped.", file=sys.stderr)
            cursor = match.end()
            continue

        close_at = raw_text.find(CHAT_CLOSE_TAG, match.end())
        if close_at < 0:
            body = raw_text[match.end():]
            cursor = len(raw_text)
            warnings.append("unterminated <chat> block; the remaining text was "
                            "taken as body")
        else:
            body = raw_text[match.end():close_at]
            cursor = close_at + len(CHAT_CLOSE_TAG)

        if "<chat" in body:
            warnings.append("body contains a nested '<chat' marker; the block "
                            "split may be wrong")

        body = html.unescape(body)
        content, starts_at_begin, title, header_warnings = strip_tool_header(
            body, **kwargs)
        warnings.extend(header_warnings)

        pieces, gap_warnings = split_gap_markers(content, **kwargs)
        warnings.extend(gap_warnings)

        fragments = [
            {"text": piece, "is_chat_start": starts_at_begin and index == 0}
            for index, piece in enumerate(pieces)
        ]

        results.append({
            "url":        attrs["url"],
            "uuid":       uuid_from_url(attrs["url"]),
            "updated_at": attrs.get("updated_at", ""),
            "kind":       attrs.get("kind") or "conversation",
            "title":      title,
            "fragments":  fragments,
            "warnings":   warnings,
        })
    return results


# ---------------------------------------------------------------------------
# Store handling
# ---------------------------------------------------------------------------

def _empty_stats() -> dict[str, int]:
    """Return a fresh statistics block."""
    return {
        "fragments_seen":       0,
        "empty_fragments":      0,
        "merge_events":         0,
        "new_segment_events":   0,
        "contained_events":     0,
        "ambiguous_rejections": 0,
        "segment_joins":        0,
    }


def _new_edge(closed: bool = False) -> dict[str, Any]:
    """Return a fresh edge record."""
    return {"closed": closed, "attempts": 0, "barren": 0}


def _new_segment(seg_id: int, text: str, query: str,
                 is_chat_start: bool = False) -> dict[str, Any]:
    """Return a fresh segment record."""
    return {
        "id":             seg_id,
        "text":           text,
        "chat_start":     is_chat_start,
        "edges":          {"head": _new_edge(is_chat_start), "tail": _new_edge()},
        "origin_queries": [query] if query else [],
    }


def new_store(uuid: str, url: str, title: str = "",
              updated_at: str = "") -> dict[str, Any]:
    """Create an empty store dictionary for one chat."""
    return {
        "schema_version":  SCHEMA_VERSION,
        "chat_uuid":       uuid,
        "url":             url,
        "title":           title,
        "updated_at":      updated_at,
        "segments":        [],
        "queries_used":    [],
        "pending_queries": [],
        "warnings":        [],
        "stats":           _empty_stats(),
    }


def upgrade_store(store: dict[str, Any]) -> dict[str, Any]:
    """Fill in keys that older store files (schema v1 to v3) do not have."""
    stats = store.setdefault("stats", _empty_stats())
    for key, value in _empty_stats().items():
        stats.setdefault(key, value)

    for segment in store.setdefault("segments", []):
        if "edges" not in segment:
            segment["edges"] = {
                "head": _new_edge(bool(segment.pop("head_closed", False))),
                "tail": _new_edge(bool(segment.pop("tail_closed", False))),
            }
        segment.pop("stale", None)
        segment.setdefault("origin_queries", [])
        # Before v4 the chat start was inferred from the head edge; that is
        # the best guess available for an already existing store.
        segment.setdefault("chat_start", bool(segment["edges"]["head"]["closed"]))

    store.setdefault("queries_used", [])
    store.setdefault("pending_queries", [])
    store.setdefault("warnings", [])
    store["schema_version"] = SCHEMA_VERSION
    return store


def store_path(store_dir: str, uuid: str) -> str:
    """Return the file path of the store belonging to *uuid*."""
    return os.path.join(store_dir, f"{uuid}.json")


def load_store(path: str) -> dict[str, Any]:
    """Load a store from *path*, upgrading older schemas in place."""
    with open(path, "r", encoding="utf-8") as handle:
        return upgrade_store(json.load(handle))


def is_store_payload(payload: Any) -> bool:
    """True when *payload* looks like a chat store of any schema version.

    Export documents, the legacy ``index.json`` and other foreign JSON files
    fail this test; directory scans use it so that a stray file never crashes
    ``status`` or pollutes ``overview`` with a phantom chat.
    """
    return (isinstance(payload, dict)
            and isinstance(payload.get("chat_uuid"), str)
            and isinstance(payload.get("segments"), list))


def try_load_store(path: str) -> dict[str, Any] | None:
    """Load a store file, or return None when it is not a chat store.

    Used by directory scans, where a foreign JSON file (an export written
    into the store directory, a leftover ``index.json``) must be skipped
    instead of crashing the command.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    if not is_store_payload(payload):
        return None
    return upgrade_store(payload)


def _write_json_atomic(payload: Any, path: str, prefix: str) -> None:
    """Write *payload* as JSON to *path* via a temp file and os.replace."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=prefix, suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def save_store(store: dict[str, Any], path: str) -> None:
    """Write *store* to *path* atomically."""
    _write_json_atomic(store, path, ".store-")


def add_warning(store: dict[str, Any], source: str, message: str) -> None:
    """Record a warning in the store, avoiding exact duplicates."""
    entry = {"source": source, "message": message}
    if entry not in store["warnings"]:
        store["warnings"].append(entry)


def _next_segment_id(store: dict[str, Any]) -> int:
    """Return an unused segment id."""
    if not store["segments"]:
        return 1
    return max(segment["id"] for segment in store["segments"]) + 1


def _find_segment(store: dict[str, Any], segment_id: int) -> dict[str, Any] | None:
    """Return the segment with *segment_id*, or None."""
    for segment in store["segments"]:
        if segment["id"] == segment_id:
            return segment
    return None


# ---------------------------------------------------------------------------
# Merging
# ---------------------------------------------------------------------------

def merge_fragment(store: dict[str, Any],
                   fragment: str,
                   query: str = "",
                   min_overlap: int = DEFAULT_MIN_OVERLAP,
                   is_chat_start: bool = False,
                   **kwargs) -> dict[str, Any]:
    """Merge *fragment* into *store*, growing or creating a segment.

    Every segment is checked in both directions; the longest *unique* overlap
    wins.  Ambiguous overlaps are counted but never discard the fragment: if
    nothing joins uniquely, the fragment becomes a new isolated segment.

    Parameters
    ----------
    store : dict
        Store dictionary, modified in place.
    fragment : str
        Fragment text with tool packaging already removed.
    query : str
        The query that produced this fragment (recorded for bookkeeping).
    min_overlap : int
        Minimum normalised overlap length accepted as a genuine join.
    is_chat_start : bool
        True when this fragment begins at the very start of the chat.

    Returns
    -------
    dict
        Outcome record with ``action`` (``empty``, ``contained``, ``extended``,
        ``superseded`` or ``new``), ``segment_id``, ``grew``, ``remap`` (ids
        removed by consolidation mapped to their survivor) and, for ``new``,
        ``had_ambiguous``.
    """
    stats = store["stats"]
    frag_norm = norm_of(fragment)
    if not frag_norm:
        stats["empty_fragments"] += 1
        return {"action": "empty", "segment_id": None, "grew": False, "remap": {}}

    stats["fragments_seen"] += 1
    if query and query not in store["queries_used"]:
        store["queries_used"].append(query)

    if __debug__ and "debug" in kwargs:
        print(f"[merge] fragment norm len={len(frag_norm)} "
              f"segments={len(store['segments'])} start={is_chat_start}",
              file=sys.stderr)

    # Pass 1: containment in either direction.
    for segment in store["segments"]:
        seg_norm = norm_of(segment["text"])

        if frag_norm in seg_norm:
            stats["contained_events"] += 1
            _record_query(segment, query)
            if is_chat_start:
                if seg_norm.startswith(frag_norm):
                    segment["chat_start"] = True
                    segment["edges"]["head"]["closed"] = True
                else:
                    add_warning(store, f"segment {segment['id']}",
                                "a fragment flagged as chat start lies inside "
                                "this segment but not at its head; the start "
                                "detection or an earlier merge is wrong")
            return {"action": "contained", "segment_id": segment["id"],
                    "grew": False, "remap": {}}

        if seg_norm in frag_norm:
            head_kept = frag_norm.startswith(seg_norm)
            tail_kept = frag_norm.endswith(seg_norm)
            if segment["chat_start"] and not head_kept:
                add_warning(store, f"segment {segment['id']}",
                            "text was found before a segment marked as chat "
                            "start; the mark was dropped -- the start "
                            "detection or this merge is wrong")
            segment["text"] = fragment
            if is_chat_start:
                segment["chat_start"] = True
            elif not head_kept:
                segment["chat_start"] = False
            # An edge whose text was replaced is new territory: its counters
            # describe queries against text that is no longer there.
            if not head_kept:
                segment["edges"]["head"] = _new_edge(segment["chat_start"])
            elif is_chat_start:
                segment["edges"]["head"]["closed"] = True
            if not tail_kept:
                segment["edges"]["tail"] = _new_edge()
            _record_query(segment, query)
            stats["merge_events"] += 1
            remap = _consolidate(store, min_overlap)
            return {"action": "superseded",
                    "segment_id": remap.get(segment["id"], segment["id"]),
                    "grew": True, "remap": remap}

    # Pass 2: best unique overlap over all segments and both directions.
    best_len = 0
    best_segment: dict[str, Any] | None = None
    best_direction = ""
    had_ambiguous = False

    for segment in store["segments"]:
        seg_norm = norm_of(segment["text"])

        overlap = find_overlap(seg_norm, frag_norm, min_overlap)
        if overlap:
            if _is_unique(seg_norm, frag_norm[:overlap]):
                if overlap > best_len:
                    best_len, best_segment, best_direction = overlap, segment, "append"
            else:
                had_ambiguous = True

        overlap = find_overlap(frag_norm, seg_norm, min_overlap)
        if overlap:
            if _is_unique(frag_norm, seg_norm[:overlap]):
                if overlap > best_len:
                    best_len, best_segment, best_direction = overlap, segment, "prepend"
            else:
                had_ambiguous = True

    if best_segment is not None:
        if best_direction == "append":
            if is_chat_start:
                add_warning(store, f"segment {best_segment['id']}",
                            "a fragment flagged as chat start was appended at "
                            "the tail of this segment; the flag was ignored -- "
                            "the start detection or this merge is wrong")
            cut = _original_cut(fragment, best_len)
            best_segment["text"] = best_segment["text"] + fragment[cut:]
            best_segment["edges"]["tail"] = _new_edge()
        else:
            if best_segment["chat_start"] and not is_chat_start:
                add_warning(store, f"segment {best_segment['id']}",
                            "text was prepended before a segment marked as "
                            "chat start; the mark was dropped -- the start "
                            "detection or this merge is wrong")
            cut = _original_cut(best_segment["text"], best_len)
            best_segment["text"] = fragment + best_segment["text"][cut:]
            best_segment["chat_start"] = is_chat_start
            best_segment["edges"]["head"] = _new_edge(is_chat_start)
        _record_query(best_segment, query)
        stats["merge_events"] += 1
        remap = _consolidate(store, min_overlap)
        return {"action": "extended",
                "segment_id": remap.get(best_segment["id"], best_segment["id"]),
                "grew": True, "remap": remap}

    if had_ambiguous:
        stats["ambiguous_rejections"] += 1

    segment = _new_segment(_next_segment_id(store), fragment, query, is_chat_start)
    store["segments"].append(segment)
    stats["new_segment_events"] += 1
    return {"action": "new", "segment_id": segment["id"], "grew": True,
            "remap": {}, "had_ambiguous": had_ambiguous}


def _record_query(segment: dict[str, Any], query: str) -> None:
    """Append *query* to the segment's origin list if new."""
    if query and query not in segment["origin_queries"]:
        segment["origin_queries"].append(query)


def _original_cut(text: str, norm_overlap: int) -> int:
    """Translate a normalised overlap length into an index into *text*."""
    _, index_map = normalize_with_map(text)
    if norm_overlap >= len(index_map):
        return len(text)
    return index_map[norm_overlap]


def _consolidate(store: dict[str, Any], min_overlap: int) -> dict[int, int]:
    """Repeatedly join segments that have grown into each other.

    Edge records travel only when they still describe an actual edge of the
    surviving segment: a segment absorbed in the *middle* of another must not
    close the absorber's head or tail.

    Returns
    -------
    dict
        Mapping of removed segment ids to the id of the segment that absorbed
        them, kept transitive so that a single lookup suffices.
    """
    remap: dict[int, int] = {}
    changed = True
    while changed:
        changed = False
        segments = store["segments"]
        for i in range(len(segments)):
            for j in range(len(segments)):
                if i == j:
                    continue
                left, right = segments[i], segments[j]
                left_norm = norm_of(left["text"])
                right_norm = norm_of(right["text"])

                if right_norm in left_norm:
                    if left_norm.startswith(right_norm):
                        if right["edges"]["head"]["closed"]:
                            left["edges"]["head"]["closed"] = True
                        left["chat_start"] = left["chat_start"] or right["chat_start"]
                    if left_norm.endswith(right_norm) and right["edges"]["tail"]["closed"]:
                        left["edges"]["tail"]["closed"] = True
                    _absorb_segment(store, left, right, remap)
                    segments.pop(j)
                    store["stats"]["segment_joins"] += 1
                    changed = True
                    break

                overlap = find_overlap(left_norm, right_norm, min_overlap)
                if overlap and _is_unique(left_norm, right_norm[:overlap]):
                    cut = _original_cut(right["text"], overlap)
                    left["text"] = left["text"] + right["text"][cut:]
                    left["edges"]["tail"] = right["edges"]["tail"]
                    _absorb_segment(store, left, right, remap)
                    segments.pop(j)
                    store["stats"]["segment_joins"] += 1
                    changed = True
                    break
            if changed:
                break
    return remap


def _absorb_segment(store: dict[str, Any],
                    survivor: dict[str, Any],
                    removed: dict[str, Any],
                    remap: dict[int, int]) -> None:
    """Move queries and pending entries from *removed* onto *survivor*."""
    for query in removed["origin_queries"]:
        _record_query(survivor, query)
    for entry in store["pending_queries"]:
        if entry["segment_id"] == removed["id"]:
            entry["segment_id"] = survivor["id"]
    for key, value in remap.items():
        if value == removed["id"]:
            remap[key] = survivor["id"]
    remap[removed["id"]] = survivor["id"]


# ---------------------------------------------------------------------------
# Edge bookkeeping
# ---------------------------------------------------------------------------

def account_query(store: dict[str, Any], query: str,
                  grown_segment_ids: set[int]) -> str:
    """Credit or debit the edge that *query* came from.

    The edge is credited only when the segment owning it is among the ones
    that actually grew.  Growth elsewhere in the same dump must not reset the
    counter, or an edge that keeps returning unrelated material would never
    be recognised as exhausted.

    Returns
    -------
    str
        A short note for the caller, empty when the query had no known edge.
    """
    if not query:
        return ""
    entry = None
    for candidate in store["pending_queries"]:
        if candidate["query"] == query:
            entry = candidate
            break
    if entry is None:
        return ""

    store["pending_queries"].remove(entry)
    segment = _find_segment(store, entry["segment_id"])
    if segment is None:
        return ""

    edge = segment["edges"][entry["side"]]
    edge["attempts"] += 1
    if segment["id"] in grown_segment_ids:
        edge["barren"] = 0
        return f"edge {entry['side']} of seg {segment['id']} advanced"
    edge["barren"] += 1
    if edge["barren"] >= BARREN_LIMIT:
        return (f"edge {entry['side']} of seg {segment['id']} exhausted "
                f"({edge['barren']} fruitless queries)")
    return f"edge {entry['side']} of seg {segment['id']} barren {edge['barren']}"


def edge_exhausted(edge: dict[str, Any]) -> bool:
    """True when an edge is closed or has stopped producing new text."""
    return edge["closed"] or edge["barren"] >= BARREN_LIMIT


def segment_exhausted(segment: dict[str, Any]) -> bool:
    """True when both edges of *segment* are closed or exhausted."""
    return all(edge_exhausted(edge) for edge in segment["edges"].values())


def crawl_finished(store: dict[str, Any]) -> bool:
    """True when no edge of any segment is worth querying any more."""
    return bool(store["segments"]) and all(
        segment_exhausted(segment) for segment in store["segments"]
    )


# ---------------------------------------------------------------------------
# Open edges and query suggestion
# ---------------------------------------------------------------------------

def open_edges(store: dict[str, Any]) -> list[dict[str, Any]]:
    """List all segment edges still worth querying."""
    edges: list[dict[str, Any]] = []
    for segment in store["segments"]:
        if not edge_exhausted(segment["edges"]["head"]):
            edges.append({
                "segment_id": segment["id"],
                "side":       "head",
                "window":     segment["text"][:EDGE_WINDOW],
            })
        if not edge_exhausted(segment["edges"]["tail"]):
            edges.append({
                "segment_id": segment["id"],
                "side":       "tail",
                "window":     segment["text"][-EDGE_WINDOW:],
            })
    return edges


def _token_score(token: str) -> int:
    """Rate how distinctive *token* is likely to be as a search term."""
    lowered = token.lower()
    if lowered in STOPWORDS or len(token) < 4:
        return 0
    score = 0
    if "_" in token or "." in token:
        score += 3
    if re.search(r"[a-z][A-Z]", token):
        score += 3
    if re.search(r"\d", token):
        score += 1
    if len(token) >= 9:
        score += 2
    elif len(token) >= 7:
        score += 1
    return score


def _corpus_counts(store: dict[str, Any]) -> dict[str, int]:
    """Count token occurrences across all known text of this chat."""
    counts: dict[str, int] = {}
    for segment in store["segments"]:
        for token in TOKEN_PATTERN.findall(segment["text"]):
            counts[token] = counts.get(token, 0) + 1
    return counts


def suggest_queries(store: dict[str, Any], count: int = 5,
                    **kwargs) -> list[dict[str, Any]]:
    """Propose search queries built from the open edges of known segments.

    Each query is a short phrase of two to three distinctive tokens, because
    the search backend behaves like a bag-of-words matcher: extra tokens
    dilute rather than restrict the result.

    Returns
    -------
    list of dict
        Entries with ``query``, ``segment_id``, ``side`` and ``score``.
    """
    counts = _corpus_counts(store)
    used = {normalize_text(query).lower() for query in store["queries_used"]}
    candidates: list[dict[str, Any]] = []
    edges = open_edges(store)

    for edge in edges:
        tokens = TOKEN_PATTERN.findall(edge["window"])
        scored = []
        for position, token in enumerate(tokens):
            score = _token_score(token)
            if score <= 0:
                continue
            occurrences = counts.get(token, 1)
            if occurrences == 1:
                score += 2
            elif occurrences <= 3:
                score += 1
            scored.append((position, token, score))

        scored.sort(key=lambda item: item[2], reverse=True)
        for position, token, score in scored[:4]:
            phrase = _build_phrase(tokens, position)
            key = normalize_text(phrase).lower()
            if key in used:
                continue
            used.add(key)
            candidates.append({
                "query":      phrase,
                "segment_id": edge["segment_id"],
                "side":       edge["side"],
                "score":      score,
            })

    candidates.sort(key=lambda item: item["score"], reverse=True)

    if __debug__ and "debug" in kwargs:
        print(f"[suggest] edges={len(edges)} candidates={len(candidates)}",
              file=sys.stderr)

    return candidates[:count]


def _build_phrase(tokens: list[str], position: int, width: int = 2) -> str:
    """Build a short phrase around *position*, keeping distinctive neighbours."""
    picked = [tokens[position]]
    offset = 1
    while len(picked) < width + 1 and offset < 6:
        for candidate_pos in (position + offset, position - offset):
            if 0 <= candidate_pos < len(tokens) and len(picked) < width + 1:
                candidate = tokens[candidate_pos]
                if _token_score(candidate) > 0 and candidate not in picked:
                    if candidate_pos > position:
                        picked.append(candidate)
                    else:
                        picked.insert(0, candidate)
        offset += 1
    return " ".join(picked)


def remember_suggestions(store: dict[str, Any],
                         suggestions: list[dict[str, Any]]) -> None:
    """Record suggested queries so that ingest can credit the right edge.

    The list is capped: suggestions that are never used would otherwise
    accumulate for the lifetime of the store.
    """
    known = {entry["query"] for entry in store["pending_queries"]}
    for item in suggestions:
        if item["query"] not in known:
            store["pending_queries"].append({
                "query":      item["query"],
                "segment_id": item["segment_id"],
                "side":       item["side"],
            })
    excess = len(store["pending_queries"]) - PENDING_QUERY_LIMIT
    if excess > 0:
        del store["pending_queries"][:excess]


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def split_messages(text: str, **kwargs) -> tuple[list[dict[str, str]], list[str]]:
    """Split segment *text* into role-tagged messages.

    Labels are recognised only at the very start of a line and outside code
    fences.  Leading text without a label is a truncated message; its role is
    derived from the label that follows it.

    Returns
    -------
    tuple
        ``(messages, warnings)`` with each message ``{"role", "content"}``.
    """
    warnings: list[str] = []
    spans = fence_spans(text)

    if count_fence_delimiters(text) % 2:
        warnings.append("odd number of code fence delimiters in this segment; "
                        "speaker labels after the unmatched fence may have been "
                        "missed")

    boundaries: list[tuple[int, str]] = []
    offset = 0
    for line in text.splitlines(keepends=True):
        match = LABEL_PATTERN.match(line)
        if match and not in_spans(offset, spans):
            boundaries.append((offset, LABEL_ROLES[match.group(1)]))
        offset += len(line)

    if not boundaries:
        content = text.strip()
        if not content:
            return [], warnings
        warnings.append("segment without any speaker label; role unknown")
        return [{"role": "unknown", "content": content}], warnings

    messages: list[dict[str, str]] = []
    lead = text[:boundaries[0][0]].strip()
    if lead:
        lead_role = "assistant" if boundaries[0][1] == "user" else "user"
        messages.append({"role": lead_role, "content": lead})

    for index, (start, role) in enumerate(boundaries):
        end = boundaries[index + 1][0] if index + 1 < len(boundaries) else len(text)
        body = LABEL_PATTERN.sub("", text[start:end], count=1).strip()
        if body:
            messages.append({"role": role, "content": body})

    if __debug__ and "debug" in kwargs:
        print(f"[messages] {len(messages)} message(s), lead={bool(lead)}",
              file=sys.stderr)

    return messages, warnings


def build_export(store: dict[str, Any],
                 predecessor: str | None = None,
                 successor: str | None = None,
                 **kwargs) -> dict[str, Any]:
    """Assemble the export document for one chat.

    Segment order is the store's insertion order and carries no chronological
    meaning; only the segment flagged ``chat_start`` is known to come first.
    ``chat_date`` is derived from the chat's ``updated_at`` and therefore
    denotes the last activity, not the creation date.
    """
    warnings = [dict(entry) for entry in store["warnings"]]
    segments_out: list[dict[str, Any]] = []

    for segment in store["segments"]:
        messages, message_warnings = split_messages(segment["text"], **kwargs)
        for message in message_warnings:
            warnings.append({"source": f"segment {segment['id']}",
                             "message": message})
        segments_out.append({
            "segment_id":      segment["id"],
            "chat_start":      segment["chat_start"],
            "edges_exhausted": segment_exhausted(segment),
            "messages":        messages,
        })

    return {
        "metadata": {
            "title":         store["title"],
            "chat_date":     (store["updated_at"] or "")[:10] or "unknown",
            "chat_uuid":     store["chat_uuid"],
            "source_url":    store["url"],
            "predecessor":   predecessor,
            "successor":     successor,
            "segment_order": "unknown_except_chat_start",
        },
        "segments": segments_out,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _edge_mark(edge: dict[str, Any], side: str) -> str:
    """Return a one-character marker describing an edge state."""
    if edge["closed"]:
        return "[" if side == "head" else "]"
    if edge["barren"] >= BARREN_LIMIT:
        return "~"
    return "<" if side == "head" else ">"


def _health_hint(stats: dict[str, int]) -> str:
    """Derive a consistency hint from the merge statistics."""
    productive = stats["merge_events"] + stats["segment_joins"]
    isolated = stats["new_segment_events"]
    if stats["fragments_seen"] < 5:
        return ""
    if isolated > 0 and productive < isolated:
        return ("mostly isolated fragments - either the crawl is still early or "
                "the incoming data does not fit the store")
    if stats["ambiguous_rejections"] > productive:
        return "many ambiguous overlaps - consider raising --min-overlap"
    return ""


def status_report(store: dict[str, Any]) -> str:
    """Render a human readable status summary for one chat store."""
    lines: list[str] = []
    total_chars = sum(len(segment["text"]) for segment in store["segments"])
    edges = open_edges(store)
    stats = store["stats"]

    lines.append(f"Chat  : {store['title'] or '(untitled)'}")
    lines.append(f"UUID  : {store['chat_uuid']}")
    lines.append(f"URL   : {store['url']}")
    lines.append(f"Chars : {total_chars} in {len(store['segments'])} segment(s)")
    lines.append(f"Edges : {len(edges)} still worth querying"
                 f"{'  -- CRAWL FINISHED' if crawl_finished(store) else ''}")
    lines.append(f"Stats : fragments={stats['fragments_seen']} "
                 f"merges={stats['merge_events']} "
                 f"joins={stats['segment_joins']} "
                 f"new={stats['new_segment_events']} "
                 f"contained={stats['contained_events']} "
                 f"ambiguous={stats['ambiguous_rejections']} "
                 f"empty={stats['empty_fragments']}")
    lines.append(f"Warn  : {len(store['warnings'])} warning(s) -- see 'report'")

    hint = _health_hint(stats)
    if hint:
        lines.append(f"Hint  : {hint}")

    for segment in store["segments"]:
        head, tail = segment["edges"]["head"], segment["edges"]["tail"]
        marks = _edge_mark(head, "head") + _edge_mark(tail, "tail")
        start_mark = " START" if segment["chat_start"] else ""
        lines.append(f"  seg {segment['id']:>3} {marks} {len(segment['text']):>7} chars "
                     f"| head a{head['attempts']}/b{head['barren']} "
                     f"tail a{tail['attempts']}/b{tail['barren']}{start_mark}")
        lines.append(f"          {normalize_text(segment['text'])[:66]!r}")
    return "\n".join(lines)


def warning_report(store: dict[str, Any]) -> str:
    """Render every recorded warning of one store, grouped by source."""
    if not store["warnings"]:
        return f"{store['chat_uuid']}: no warnings."

    grouped: dict[str, list[str]] = {}
    for entry in store["warnings"]:
        grouped.setdefault(entry["source"], []).append(entry["message"])

    lines = [f"{store['chat_uuid']}  ({store['title'] or 'untitled'})"]
    for source, messages in grouped.items():
        lines.append(f"  {source}:")
        for message in messages:
            lines.append(f"    - {message}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Crawl state
# ---------------------------------------------------------------------------

CHAT_STATUSES = ("untouched", "started", "done")
ORDER_VALUES  = ("oldest-first", "newest-first")


def state_path(store_dir: str) -> str:
    """Return the path of the crawl state file."""
    return os.path.join(store_dir, STATE_FILENAME)


def state_exists(store_dir: str) -> bool:
    """True when a crawl state file is present."""
    return os.path.exists(state_path(store_dir))


def new_state() -> dict[str, Any]:
    """Return an empty crawl state."""
    return {"schema_version": STATE_SCHEMA_VERSION, "order": "", "chats": {}}


LEGACY_INDEX_FILENAME = "index.json"


def _migrate_legacy_index(store_dir: str) -> None:
    """Fold a schema-v3 ``index.json`` into the crawl state, once.

    v3 kept titles and timestamps in ``index.json``; v4 keeps them in the
    state file.  The legacy file is merged (existing state entries win) and
    renamed to ``index.json.migrated`` so that directory scans never mistake
    it for a chat store again.  An unreadable legacy file is left in place
    with a warning -- it is skipped by the scans either way.
    """
    legacy = os.path.join(store_dir, LEGACY_INDEX_FILENAME)
    if not os.path.exists(legacy):
        return
    try:
        with open(legacy, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        print(f"Warning: {legacy} exists but is unreadable; leaving it alone.",
              file=sys.stderr)
        return
    chats = payload.get("chats", {}) if isinstance(payload, dict) else {}

    path = state_path(store_dir)
    state = new_state()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            state = json.load(handle)
        state.setdefault("order", "")
        state.setdefault("chats", {})

    for uuid, legacy_record in chats.items():
        if not isinstance(legacy_record, dict):
            continue
        record = state["chats"].setdefault(uuid, {"status": "untouched"})
        record.setdefault("status", "untouched")
        for key in ("url", "title", "updated_at"):
            if legacy_record.get(key) and not record.get(key):
                record[key] = legacy_record[key]

    state["schema_version"] = STATE_SCHEMA_VERSION
    _write_json_atomic(state, path, ".state-")
    os.replace(legacy, legacy + ".migrated")
    print(f"Migrated legacy {LEGACY_INDEX_FILENAME} into {STATE_FILENAME} "
          f"({len(chats)} chat record(s)); the old file was renamed to "
          f"{LEGACY_INDEX_FILENAME}.migrated.", file=sys.stderr)


def load_state(store_dir: str) -> dict[str, Any]:
    """Load the crawl state, or return an empty one when there is none.

    A missing state file is never an error here.  It is the signal that the
    user still has to decide between a fresh export and a continuation, and
    only the caller knows how to ask that.  A legacy v3 ``index.json`` is
    migrated into the state file on first contact.
    """
    _migrate_legacy_index(store_dir)
    path = state_path(store_dir)
    if not os.path.exists(path):
        return new_state()
    with open(path, "r", encoding="utf-8") as handle:
        state = json.load(handle)
    state.setdefault("schema_version", STATE_SCHEMA_VERSION)
    state.setdefault("order", "")
    state.setdefault("chats", {})
    for record in state["chats"].values():
        record.setdefault("status", "untouched")
    return state


def save_state(store_dir: str, state: dict[str, Any]) -> None:
    """Write the crawl state atomically."""
    state["schema_version"] = STATE_SCHEMA_VERSION
    os.makedirs(store_dir, exist_ok=True)
    _write_json_atomic(state, state_path(store_dir), ".state-")


def update_state(store_dir: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge *entries* into the crawl state and return it.

    Every chat occurring in any dump is recorded, including chats nobody was
    looking for: their titles are the seed vocabulary for a targeted query
    later.  Such a chat starts as ``untouched`` -- growing by accident inside
    someone else's dump is not the same as being worked on, and keeping the
    two apart is what makes the ``ACTIVE_LIMIT`` cap hold.
    """
    state = load_state(store_dir)
    for entry in entries:
        record = state["chats"].setdefault(entry["uuid"], {"status": "untouched"})
        record["url"] = entry["url"]
        record.setdefault("status", "untouched")
        if entry["updated_at"]:
            record["updated_at"] = entry["updated_at"]
        if entry["title"]:
            record["title"] = entry["title"]
    save_state(store_dir, state)
    return state


def set_chat_status(store_dir: str, uuid: str, status: str,
                    only_from: str = "") -> str | None:
    """Set the status of one chat and return the status it had before.

    With *only_from* the change happens only when the current status matches,
    and ``None`` is returned when nothing changed.  That is what keeps
    ``queries`` from dragging an already finished chat back into work.
    """
    state = load_state(store_dir)
    record = state["chats"].setdefault(uuid, {"status": "untouched"})
    previous = record.get("status", "untouched")
    if only_from and previous != only_from:
        return None
    record["status"] = status
    save_state(store_dir, state)
    return previous


def set_order(store_dir: str, order: str) -> None:
    """Record the direction in which the chats are worked through.

    Changing this later is harmless: it only steers which ``untouched`` chat
    is nominated next and never touches what is already done.
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
    """Derive the working picture from the crawl state and the store files.

    This records no decision of its own.  A store file the state does not know
    about is reported as *recovered* and counted as ``started`` without being
    written out; the next command that touches that chat persists the record
    anyway, so nothing is lost by leaving it alone here.

    Not entirely free of side effects, though: ``load_state`` performs the
    one-off legacy ``index.json`` migration, so a first call on an old store
    directory does write the state file and rename that file.
    """
    state = load_state(store_dir)
    order = state.get("order") or "oldest-first"

    known = {uuid: dict(entry) for uuid, entry in state["chats"].items()}
    stores: dict[str, dict[str, Any]] = {}
    recovered: set[str] = set()
    if os.path.isdir(store_dir):
        for name in sorted(os.listdir(store_dir)):
            if not name.endswith(".json") or name == STATE_FILENAME:
                continue
            path = os.path.join(store_dir, name)
            store = try_load_store(path)
            if store is None:
                # Exports or other foreign JSON: not a chat, not an error.
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
            "status":     entry.get("status", "untouched"),
            "has_store":  uuid in stores,
            "recovered":  uuid in recovered,
            "open_edges": 0,
            "segments":   0,
            "chars":      0,
        }
        if record["has_store"]:
            store = stores[uuid]
            record["title"] = record["title"] or store.get("title", "")
            record["updated_at"] = (record["updated_at"]
                                    or store.get("updated_at", ""))
            record["open_edges"] = len(open_edges(store))
            record["segments"] = len(store["segments"])
            record["chars"] = sum(len(seg["text"]) for seg in store["segments"])
        records.append(record)

    records = sort_chats(records, order)

    active = [r for r in records if r["status"] == "started"
              and r["has_store"] and r["open_edges"]]
    # Anything worth exporting: a started chat that ran dry, but also a chat
    # that was completed by accident inside other chats' dumps.
    ready = [r for r in records if r["status"] != "done"
             and r["has_store"] and r["segments"] and not r["open_edges"]]
    # 'done' without a store file is normal -- the user filed it away.
    missing = [r for r in records if r["status"] == "started"
               and not r["has_store"]]
    done = [r for r in records if r["status"] == "done"]
    untouched = [r for r in records if r["status"] == "untouched"]
    candidates = [r for r in untouched if r not in ready]
    free_slots = max(0, ACTIVE_LIMIT - len(active))

    # Whether a round just ran or has not begun yet is indistinguishable from
    # the state alone -- only the reader knows.  So the script reports the
    # fact ("nothing is active") and never claims which of the two it is.
    if active:
        round_state = "in progress"
    elif candidates or ready or missing:
        round_state = "idle"
    else:
        round_state = "all done"

    return {
        "store_dir":   store_dir,
        "state_file":  state_exists(store_dir),
        "order":       order,
        "order_set":   bool(state.get("order")),
        "records":     records,
        "active":      active,
        "ready":       ready,
        "missing":     missing,
        "done":        done,
        "untouched":   untouched,
        "candidates":  candidates,
        "free_slots":  free_slots,
        "next_up":     candidates[:free_slots],
        "round_state": round_state,
    }


def _overview_chat_line(record: dict[str, Any], hint: str = "") -> list[str]:
    """Render one chat as one or two lines of the overview."""
    lines = [f"  {record['uuid']}  {record['title'] or '(title unknown)'}"]
    facts = []
    if record["segments"]:
        facts.append(f"{record['segments']} segment(s)")
        facts.append(f"{record['chars']} chars")
    if record["open_edges"]:
        facts.append(f"{record['open_edges']} open edge(s)")
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
        "Neither a crawl state file nor a single chat store is here.",
        "Ask the user which case applies; do not guess:",
        "  * a fresh export -- ask whether to work through the chats",
        "    oldest-first or newest-first, then run 'state --order <choice>'.",
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
    lines = [f"CRAWL STATE  {picture['store_dir']}"]

    if not picture["state_file"]:
        lines += [
            f"  !! no {STATE_FILENAME} here -- the chats below were recovered",
            "     from their store files, titles and progress included.  What",
            "     is lost with the state file: every 'done' mark, the working",
            "     order, and the titles of chats that had no store file.  Ask",
            "     the user whether the state file can still be uploaded before",
            "     you crawl anything again.",
        ]

    lines.append(f"Order : {picture['order']}"
                 + ("" if picture["order_set"] else "   (default, never set)"))
    lines.append(f"Chats : {len(picture['records'])} known -- "
                 f"{len(picture['untouched'])} untouched, "
                 f"{len(started)} started, {len(picture['done'])} done")

    if picture["round_state"] == "in progress":
        lines.append(f"Round : IN PROGRESS -- {len(picture['active'])} of at most "
                     f"{ACTIVE_LIMIT} slot(s) in use, {picture['free_slots']} free")
    elif picture["round_state"] == "idle":
        lines.append("Round : IDLE -- no chat is active.  Which of the two this is,")
        lines.append("        only you know:")
        lines.append("        * you just finished a round -> export what is ready,")
        lines.append("          hand the files over, ask whether to continue.")
        lines.append("        * you are starting out -> begin up to "
                     f"{ACTIVE_LIMIT} chats from NEXT UP.")
    else:
        lines.append("Round : ALL DONE -- nothing left to crawl. Hand over and "
                     "say so.")

    if picture["active"]:
        lines.append("")
        lines.append("ACTIVE -- take search tokens from these and from no others")
        for record in picture["active"]:
            lines += _overview_chat_line(
                record, f"queries --chat {record['uuid']}")

    if picture["ready"]:
        lines.append("")
        lines.append("READY TO EXPORT -- no edge worth querying; the export is "
                     "what sets 'done'")
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
        lines.append("  Ask the user to upload exactly these.  Without them the "
                     "crawl progress")
        lines.append("  of those chats is lost and would have to start over.")

    lines.append("")
    if picture["free_slots"] and picture["next_up"]:
        lines.append(f"NEXT UP -- {picture['free_slots']} free slot(s), "
                     f"{picture['order']}")
        for record in picture["next_up"]:
            hint = (f"queries --chat {record['uuid']}" if record["has_store"]
                    else "search its title words first, then ingest the dump")
            lines += _overview_chat_line(record, hint)
    elif not picture["free_slots"]:
        lines.append(f"NEXT UP -- no free slot ({ACTIVE_LIMIT} in use). Finish or "
                     f"export an active")
        lines.append("          chat first.  Fewer than three at a time is fine "
                     "when the chats")
        lines.append("          turn out to be long.")
    else:
        lines.append("NEXT UP -- nothing untouched left.")

    if picture["done"]:
        lines.append("")
        lines.append(f"DONE ({len(picture['done'])}) -- name these when you hand "
                     f"over; the user may file them away")
        for record in picture["done"]:
            lines.append(f"  {record['uuid']}  "
                         f"{record['title'] or '(title unknown)'}")

    travellers = [r for r in started if r["has_store"]]
    leftovers = [r for r in picture["records"]
                 if r["status"] == "untouched" and r["has_store"]
                 and r["segments"]]
    lines.append("")
    lines.append("HANDOVER -- what has to reach the next conversation")
    lines.append(f"  {STATE_FILENAME}  -- always, no exception")
    if travellers:
        lines.append(f"  plus {len(travellers)} store file(s) of started chats:")
        for record in travellers:
            lines.append(f"    {record['uuid']}.json")
    lines.append(f"  {1 + len(travellers)} file(s) in total.")
    lines.append(f"  Without {STATE_FILENAME} every 'done' mark, the working "
                 "order and the")
    lines.append("  titles of chats without a store file are gone.")
    if leftovers:
        lines.append(f"  {len(leftovers)} store file(s) of untouched chats stay "
                     "behind BY DESIGN (by-catch")
        lines.append("  text; re-searched if those chats are taken up later).  "
                     "Name this to the")
        lines.append("  user once when handing over.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def group_entries_by_uuid(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Merge parser entries belonging to the same chat into one record.

    A single search result may contain several blocks of one conversation.
    Merging them before any edge bookkeeping happens keeps the query from
    being settled on the first block alone.
    """
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        record = grouped.get(entry["uuid"])
        if record is None:
            grouped[entry["uuid"]] = {
                "uuid":       entry["uuid"],
                "url":        entry["url"],
                "updated_at": entry["updated_at"],
                "title":      entry["title"],
                "fragments":  list(entry["fragments"]),
                "warnings":   list(entry["warnings"]),
            }
            continue
        record["fragments"].extend(entry["fragments"])
        record["warnings"].extend(entry["warnings"])
        if entry["title"]:
            record["title"] = entry["title"]
        if entry["updated_at"]:
            record["updated_at"] = entry["updated_at"]
    return grouped


def cmd_ingest(args: argparse.Namespace) -> int:
    """Read a raw tool dump and merge every fragment it contains."""
    with open(args.raw, "r", encoding="utf-8") as handle:
        raw_text = handle.read()

    debug_kwargs = {"debug": {}} if args.debug else {}
    entries = parse_tool_output(raw_text, **debug_kwargs)
    if not entries:
        print("No <chat ...> blocks found in the raw dump.", file=sys.stderr)
        return 1

    update_state(args.store_dir, entries)

    for record in group_entries_by_uuid(entries).values():
        path = store_path(args.store_dir, record["uuid"])
        if os.path.exists(path):
            store = load_store(path)
        else:
            store = new_store(record["uuid"], record["url"],
                              record["title"], record["updated_at"])
        if record["title"]:
            store["title"] = record["title"]
        if record["updated_at"]:
            store["updated_at"] = record["updated_at"]

        source = f"query {args.query!r}" if args.query else "ingest"
        for message in record["warnings"]:
            add_warning(store, source, message)

        grown: set[int] = set()
        actions: list[str] = []
        for fragment in record["fragments"]:
            outcome = merge_fragment(store, fragment["text"], args.query,
                                     args.min_overlap, fragment["is_chat_start"],
                                     **debug_kwargs)
            actions.append(outcome["action"])
            if outcome["remap"]:
                grown = {outcome["remap"].get(seg_id, seg_id) for seg_id in grown}
            if outcome["grew"] and outcome["segment_id"] is not None:
                grown.add(outcome["segment_id"])
            if outcome.get("had_ambiguous"):
                add_warning(store, f"segment {outcome['segment_id']}",
                            "only ambiguous overlaps found; kept as a new segment")

        note = account_query(store, args.query, grown)
        save_store(store, path)
        print(f"{record['uuid'][:8]}  {len(record['fragments'])} fragment(s): "
              f"{', '.join(actions) or 'none'}"
              f"{'  | ' + note if note else ''}")
    return 0


def cmd_overview(args: argparse.Namespace) -> int:
    """Print the working picture: where the crawl stands and what comes next.

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


def _resolve_paths(args: argparse.Namespace) -> list[str] | None:
    """Return the store paths selected by --chat, or None on error.

    Foreign JSON files in the store directory (exports, a leftover legacy
    ``index.json``) are skipped with a warning instead of being mistaken for
    chat stores.
    """
    if getattr(args, "chat", ""):
        path = store_path(args.store_dir, args.chat)
        if not os.path.exists(path):
            print(f"Missing store: {path}", file=sys.stderr)
            return None
        if try_load_store(path) is None:
            print(f"Not a chat store: {path}", file=sys.stderr)
            return None
        return [path]

    if not os.path.isdir(args.store_dir):
        print(f"Store directory does not exist: {args.store_dir}", file=sys.stderr)
        return None
    paths = []
    for name in sorted(os.listdir(args.store_dir)):
        if not name.endswith(".json") or name == STATE_FILENAME:
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
    """Print a status report for one or all stores."""
    paths = _resolve_paths(args)
    if paths is None:
        return 1
    for path in paths:
        print(status_report(load_store(path)))
        print()
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Print every recorded warning in full."""
    paths = _resolve_paths(args)
    if paths is None:
        return 1
    for path in paths:
        print(warning_report(load_store(path)))
        print()
    return 0


def cmd_queries(args: argparse.Namespace) -> int:
    """Suggest the next search queries and remember their edges."""
    path = store_path(args.store_dir, args.chat)
    if not os.path.exists(path):
        print(f"Missing store: {path}", file=sys.stderr)
        return 1

    store = load_store(path)
    debug_kwargs = {"debug": {}} if args.debug else {}
    suggestions = suggest_queries(store, args.count, **debug_kwargs)
    if not suggestions:
        print("No open edges left, or no distinctive tokens available.")
        return 0

    remember_suggestions(store, suggestions)
    save_store(store, path)

    # Asking for search tokens IS the act of starting a chat -- see the
    # status mechanics in the design notes.
    if set_chat_status(args.store_dir, args.chat, "started",
                       only_from="untouched") is not None:
        print(f"chat {args.chat[:8]} is now started.", file=sys.stderr)

    for item in suggestions:
        print(f"[seg {item['segment_id']} {item['side']:<4} score {item['score']:>2}]  "
              f"{item['query']}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    """Manually close (or reopen) a segment edge.

    Closing an edge only stops further queries there; it never asserts that
    the segment starts the chat.
    """
    path = store_path(args.store_dir, args.chat)
    if not os.path.exists(path):
        print(f"Missing store: {path}", file=sys.stderr)
        return 1

    store = load_store(path)
    segment = _find_segment(store, args.segment)
    if segment is None:
        print(f"No segment with id {args.segment} in store {args.chat}.",
              file=sys.stderr)
        return 1

    edge = segment["edges"][args.side]
    edge["closed"] = not args.reopen
    if args.reopen:
        edge["barren"] = 0
    save_store(store, path)
    print(f"seg {segment['id']} {args.side} "
          f"{'reopened' if args.reopen else 'closed'}.")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Write the export document for one chat."""
    path = store_path(args.store_dir, args.chat)
    if not os.path.exists(path):
        print(f"Missing store: {path}", file=sys.stderr)
        return 1

    store = load_store(path)
    if not store["segments"]:
        print("Store contains no segments yet.", file=sys.stderr)
        return 1

    debug_kwargs = {"debug": {}} if args.debug else {}
    document = build_export(store, args.predecessor or None,
                            args.successor or None, **debug_kwargs)

    if args.out:
        _write_json_atomic(document, args.out, ".export-")
        print(f"Wrote {len(document['segments'])} segment(s) and "
              f"{len(document['warnings'])} warning(s) to {args.out}")
    else:
        json.dump(document, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    # Only an exhausted crawl earns 'done'.  Exporting early is allowed and
    # must stay visible as unfinished, so the chat keeps its status.
    channel = sys.stdout if args.out else sys.stderr
    if crawl_finished(store):
        set_chat_status(args.store_dir, args.chat, "done")
        print(f"chat {args.chat[:8]} is now done -- the user may file it away.",
              file=channel)
    else:
        print(f"chat {args.chat[:8]} stays unfinished; status unchanged. "
              f"Say so when presenting the file.", file=channel)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Assemble the command line interface."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--store-dir", default="./store",
                        help="directory holding the per-chat JSON stores")
    parser.add_argument("--debug", action="store_true",
                        help="emit diagnostic output on stderr")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="merge a raw tool dump into the stores")
    p_ingest.add_argument("--raw", required=True, help="file holding the raw tool output")
    p_ingest.add_argument("--query", default="", help="the query that produced the dump")
    p_ingest.add_argument("--min-overlap", type=int, default=DEFAULT_MIN_OVERLAP,
                          help="minimum normalised overlap length")
    p_ingest.set_defaults(func=cmd_ingest)

    p_overview = sub.add_parser("overview",
                                help="where the crawl stands and what comes next")
    p_overview.set_defaults(func=cmd_overview)

    p_state = sub.add_parser("state", help="set the working order or a chat status")
    p_state.add_argument("--order", default="", choices=("", *ORDER_VALUES),
                         help="direction in which the chats are worked through")
    p_state.add_argument("--chat", default="", help="chat UUID for --status")
    p_state.add_argument("--status", default="", choices=("", *CHAT_STATUSES),
                         help="set the status of one chat by hand")
    p_state.set_defaults(func=cmd_state)

    p_status = sub.add_parser("status", help="report coverage and open edges")
    p_status.add_argument("--chat", default="", help="restrict to one chat UUID")
    p_status.set_defaults(func=cmd_status)

    p_report = sub.add_parser("report", help="print all recorded warnings")
    p_report.add_argument("--chat", default="", help="restrict to one chat UUID")
    p_report.set_defaults(func=cmd_report)

    p_queries = sub.add_parser("queries", help="suggest the next search queries")
    p_queries.add_argument("--chat", required=True, help="chat UUID")
    p_queries.add_argument("-n", "--count", type=int, default=5,
                           help="number of suggestions")
    p_queries.set_defaults(func=cmd_queries)

    p_close = sub.add_parser("close", help="manually close or reopen a segment edge")
    p_close.add_argument("--chat", required=True, help="chat UUID")
    p_close.add_argument("--segment", required=True, type=int, help="segment id")
    p_close.add_argument("--side", required=True, choices=("head", "tail"),
                         help="which edge to change")
    p_close.add_argument("--reopen", action="store_true",
                         help="reopen the edge instead of closing it")
    p_close.set_defaults(func=cmd_close)

    p_export = sub.add_parser("export", help="write the export document")
    p_export.add_argument("--chat", required=True, help="chat UUID")
    p_export.add_argument("--out", default="", help="output file (default: stdout)")
    p_export.add_argument("--predecessor", default="",
                          help="chat UUID of the preceding chat")
    p_export.add_argument("--successor", default="",
                          help="chat UUID of the following chat")
    p_export.set_defaults(func=cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
