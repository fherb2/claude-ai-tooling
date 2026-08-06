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
    vocabulary for a targeted query on that chat later (see step 2).
    Ingest the dump immediately with ``--query`` set to the cluster term
    used, same as any other search result; do not discard the parts of
    the dump belonging to chats you were not looking for.

    This step is expensive in tokens relative to what it stores (a wide
    net returns much you will not keep), so budget it deliberately: a
    handful of cluster queries to map the whole project's titles, not
    one per chat.  Prefer breadth here (many titles, shallow) and leave
    depth (full reconstruction) to the targeted loop in step 2-3.

2.  Ask what to search next:

        python chat_crawl_store.py --store-dir ./store queries \
            --chat <uuid> -n 5

    Take one suggestion, pass it to ``conversation_search`` unchanged, dump
    the result, ingest it with ``--query`` set to that exact suggestion.
    The exact string matters: it is how the script credits the right edge.

3.  Repeat step 2.  Watch ``status``.  An edge marked ``~`` has produced
    nothing new several times in a row; stop querying it.

4.  Stop when ``status`` says CRAWL FINISHED, or when your context is
    filling up.  Then export.

5.  Export:

        python chat_crawl_store.py --store-dir ./store export \
            --chat <uuid> --out chat_<uuid>.json

    Present the file to the user.  If the crawl is unfinished, say so.

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

RUNNING OUT OF CONTEXT
----------------------
The container filesystem is wiped between sessions.  Before you run out of
room, present the whole ``store`` directory to the user and tell them to
re-upload it next time.  Say plainly how far the crawl got.

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

WHAT NOT TO DO
--------------
*   Do not edit store files by hand.
*   Do not "clean up" snippets before ingesting them.
*   Do not claim a chat is complete.  The end of a chat cannot be detected
    from snippets; only its beginning can.  Segment order is unknown except
    for the segment carrying ``chat_start``.

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

Usage
-----
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
INDEX_FILENAME       = "index.json"
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
            if is_chat_start and seg_norm.startswith(frag_norm):
                segment["chat_start"] = True
                segment["edges"]["head"]["closed"] = True
            return {"action": "contained", "segment_id": segment["id"],
                    "grew": False, "remap": {}}

        if seg_norm in frag_norm:
            head_kept = frag_norm.startswith(seg_norm)
            tail_kept = frag_norm.endswith(seg_norm)
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
            cut = _original_cut(fragment, best_len)
            best_segment["text"] = best_segment["text"] + fragment[cut:]
            best_segment["edges"]["tail"] = _new_edge()
        else:
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
# Index handling
# ---------------------------------------------------------------------------

def update_index(store_dir: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge *entries* into the chat index file and return the index."""
    path = os.path.join(store_dir, INDEX_FILENAME)
    index: dict[str, Any] = {"chats": {}}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            index = json.load(handle)
    index.setdefault("chats", {})

    for entry in entries:
        record = index["chats"].setdefault(entry["uuid"], {})
        record["url"] = entry["url"]
        if entry["updated_at"]:
            record["updated_at"] = entry["updated_at"]
        if entry["title"]:
            record["title"] = entry["title"]

    os.makedirs(store_dir, exist_ok=True)
    _write_json_atomic(index, path, ".index-")
    return index


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

    update_index(args.store_dir, entries)

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


def _resolve_paths(args: argparse.Namespace) -> list[str] | None:
    """Return the store paths selected by --chat, or None on error."""
    if getattr(args, "chat", ""):
        path = store_path(args.store_dir, args.chat)
        if not os.path.exists(path):
            print(f"Missing store: {path}", file=sys.stderr)
            return None
        return [path]

    if not os.path.isdir(args.store_dir):
        print(f"Store directory does not exist: {args.store_dir}", file=sys.stderr)
        return None
    paths = sorted(
        os.path.join(args.store_dir, name)
        for name in os.listdir(args.store_dir)
        if name.endswith(".json") and name != INDEX_FILENAME
    )
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
