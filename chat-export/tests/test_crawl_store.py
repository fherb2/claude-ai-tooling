#!/usr/bin/env python3
"""Self-test for chat_crawl_store: unit checks plus an end-to-end CLI run.

Runnable from anywhere; the script under test is located relative to this
file, not to the working directory:

    python tests/test_crawl_store.py
    python -O tests/test_crawl_store.py   # verifies the __debug__ guards compile out
"""

import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

# Locate the script under test: prefer the repo layout (../source next to a
# tests/ directory), fall back to the directory of this file.  SCRIPT is then
# derived from the *imported* module, so the unit tests and the CLI
# subprocesses are guaranteed to exercise the same file.
_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [_HERE]
for _candidate in _CANDIDATES:
    if os.path.exists(os.path.join(_candidate, "chat_crawl_store.py")):
        sys.path.insert(0, _candidate)
        break
else:
    sys.exit("chat_crawl_store.py not found next to this test file "
             f"or in {_CANDIDATES[0]}")

import chat_crawl_store as ccs

FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record and print one assertion result."""
    status = "ok  " if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# Overlap, normalisation and tokens
# ---------------------------------------------------------------------------

def naive_overlap(left, right, min_len):
    """Reference implementation used to validate the KMP version."""
    limit = min(len(left), len(right))
    for length in range(limit, min_len - 1, -1):
        if left.endswith(right[:length]):
            return length
    return 0


random.seed(42)
ok = True
for _ in range(500):
    a = "".join(random.choice("abc ") for _ in range(random.randint(0, 60)))
    b = "".join(random.choice("abc ") for _ in range(random.randint(0, 60)))
    for min_len in (1, 3, 7):
        if ccs.find_overlap(a, b, min_len) != naive_overlap(a, b, min_len):
            ok = False
check("find_overlap matches naive definition (500 random cases)", ok)
check("find_overlap identical strings",
      ccs.find_overlap("hello world", "hello world", 5) == 11)
check("find_overlap below min_len returns 0",
      ccs.find_overlap("abcdef", "defxyz", 4) == 0)

tokens = ccs.TOKEN_PATTERN.findall(
    "Wir speichern im Store. Danach os.path.join und store.json fertig.")
check("no sentence-final dot in tokens", "Store." not in tokens and "Store" in tokens)
check("dotted identifiers kept intact", "os.path.join" in tokens and "store.json" in tokens)
check("dotted identifier scores identifier bonus", ccs._token_score("store.json") >= 3)


# ---------------------------------------------------------------------------
# Speaker labels: both spellings, blank mandatory
# ---------------------------------------------------------------------------

check("short user label recognised",
      ccs.LABEL_PATTERN.match("H: text").group(1) == "H")
check("long user label recognised",
      ccs.LABEL_PATTERN.match("Human: text").group(1) == "Human")
check("long assistant label recognised",
      ccs.LABEL_PATTERN.match("Assistant: text").group(1) == "Assistant")
check("short assistant label with two blanks recognised",
      ccs.LABEL_PATTERN.match("A:  text").group(1) == "A")
check("label without trailing blank is not a label",
      ccs.LABEL_PATTERN.match("H:text") is None)
check("indented label is not a label",
      ccs.LABEL_PATTERN.match("  H: text") is None)
check("role mapping covers all spellings",
      {ccs.LABEL_ROLES[key] for key in ("H", "Human")} == {"user"}
      and {ccs.LABEL_ROLES[key] for key in ("A", "Assistant")} == {"assistant"})


# ---------------------------------------------------------------------------
# Code fences
# ---------------------------------------------------------------------------

FENCED = "prose line\n```python\ncode ... here\n```\nmore prose\n"
spans = ccs.fence_spans(FENCED)
check("fence span found", len(spans) == 1)
check("code inside fence detected",
      ccs.in_spans(FENCED.index("code ... here"), spans))
check("prose outside fence", not ccs.in_spans(FENCED.index("more prose"), spans))
check("unterminated fence extends to end",
      len(ccs.fence_spans("a\n```\nb\nc\n")) == 1)
check("fence delimiters counted", ccs.count_fence_delimiters(FENCED) == 2)
check("odd fence count detected", ccs.count_fence_delimiters("a\n```\nb\n") == 1)


# ---------------------------------------------------------------------------
# Header stripping: both observed real formats
# ---------------------------------------------------------------------------

BODY_SEARCH = (
    "Title: Regelparameter-Grenzwerte in Konfiguration auslagern\n"
    "Regelparameter-Grenzwerte in Konfiguration auslagern\n"
    "Ich brauche noch eine ganz andere Aenderung: der Startwert.\n"
    "\n"
    "A:  \n"
    "Die relevante Stelle ist in state_change().\n"
    "\n"
    "H: Nee. Anders, als ich geschrieben habe.\n"
)
content, is_start, title, warns = ccs.strip_tool_header(BODY_SEARCH)
check("format A: title captured",
      title == "Regelparameter-Grenzwerte in Konfiguration auslagern")
check("format A: header and repetition removed",
      content.lstrip().startswith("Ich brauche noch"))
check("format A: not a chat start (unlabelled lead text)", not is_start)
check("format A: dropping the repeated title is logged",
      any("repeating the title" in message for message in warns), str(warns))

BODY_RECENT = (
    "Content:\n"
    "Title: \U0001f4ac Meine Ausbildung in Regelungst\u2026\n"
    "\n"
    "H: Meine Ausbildung in Regelungstechnik ist lange her.\n"
    "\n"
    "A:  \n"
    "Das ist ein klassisches Problem.\n"
)
content_b, is_start_b, title_b, warns_b = ccs.strip_tool_header(BODY_RECENT)
check("format B: Content: line removed",
      not content_b.lstrip().startswith("Content:"))
check("format B: recognised as chat start", is_start_b)
check("format B: first user message survives",
      "H: Meine Ausbildung in Regelungstechnik ist lange her." in content_b)
check("format B: no warnings", warns_b == [], str(warns_b))

BODY_LONG_LABELS = (
    "Title: Ein Thema\n"
    "Ein Thema\n"
    "Human: erste frage\n"
    "Assistant: erste antwort\n"
)
_, is_start_long, _, _ = ccs.strip_tool_header(BODY_LONG_LABELS)
check("long labels also mark a chat start", is_start_long)

BODY_TRAP = (
    "Title: Meine Ausbildung in Regelungstechnik\n"
    "H: Meine Ausbildung in Regelungstechnik ist lange her.\n"
    "A:  antwort\n"
)
content_t, is_start_t, _, _ = ccs.strip_tool_header(BODY_TRAP)
check("title-repetition guard protects a labelled first message",
      "H: Meine Ausbildung in Regelungstechnik ist lange her." in content_t
      and is_start_t)

_, _, _, warns_missing = ccs.strip_tool_header("just some text\nwithout a header\n")
check("missing Title: line warns",
      any("Title:" in message for message in warns_missing), str(warns_missing))
_, _, _, warns_nolabel = ccs.strip_tool_header("Title: X\nplain text only\n")
check("missing speaker labels warn",
      any("speaker label" in message for message in warns_nolabel),
      str(warns_nolabel))

_, is_start_assistant, _, _ = ccs.strip_tool_header("Title: X\nA: antwort\nH: frage\n")
check("a block starting with the assistant is not a chat start",
      not is_start_assistant)


# ---------------------------------------------------------------------------
# Gap splitting
# ---------------------------------------------------------------------------

pieces, gap_warns = ccs.split_gap_markers(
    "H: erste haelfte des Relai...ze zweite haelfte folgt hier")
check("glued ASCII gap marker splits into two pieces", len(pieces) == 2, str(pieces))
check("gap marker itself is discarded",
      all("..." not in piece for piece in pieces), str(pieces))
check("a performed split is logged",
      any("split at a gap marker" in message for message in gap_warns),
      str(gap_warns))

pieces_uni, _ = ccs.split_gap_markers("erste haelfte des Relai\u2026ze zweite haelfte")
check("unicode ellipsis also splits", len(pieces_uni) == 2, str(pieces_uni))
check("unicode marker is discarded",
      all("\u2026" not in piece for piece in pieces_uni), str(pieces_uni))

pieces_four, _ = ccs.split_gap_markers("links....rechts")
check("four glued dots leave no stray dot",
      len(pieces_four) == 2 and pieces_four[1] == "rechts", str(pieces_four))

pieces_code, _ = ccs.split_gap_markers(
    "H: siehe code\n```python\ndef f():\n    a...b\n```\nweiter im text\n")
check("ellipsis inside a code fence does not split", len(pieces_code) == 1)

pieces_prose, warns_prose = ccs.split_gap_markers("ein Satz ... und weiter")
check("standalone ellipsis in prose does not split", len(pieces_prose) == 1)
check("symmetric prose ellipsis raises no near-miss warning",
      not any("possible gap" in message for message in warns_prose),
      str(warns_prose))

_, warns_near = ccs.split_gap_markers("abbruch... danach")
check("asymmetric ellipsis warns as possible gap",
      any("possible gap marker" in message for message in warns_near),
      str(warns_near))

noisy = " ".join(f"satz{index}... weiter" for index in range(10))
_, warns_noisy = ccs.split_gap_markers(noisy)
near_warnings = [message for message in warns_noisy if "possible gap" in message]
check("near-miss warnings are capped with a count",
      len(near_warnings) == ccs.NEAR_GAP_EXAMPLES
      and any("further asymmetric" in message for message in warns_noisy),
      str(warns_noisy))

_, warns_fence = ccs.split_gap_markers("text\n```\nnoch im code\n")
check("odd fence count warns",
      any("odd number of code fence" in message for message in warns_fence),
      str(warns_fence))


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

RAW = (
    "<chat updated_at='2026-01-01T00:00:00Z' "
    "url='https://claude.ai/chat/aaa-111' kind='conversation'>"
    "Title: Erster\nErster\nH: hallo &gt; welt &amp; mehr\nA: antwort</chat>\n"
    "<chat url=\"https://claude.ai/chat/bbb-222\" updated_at=\"2026-02-02\">"
    "Title: Zweiter\nH: vorher...nachher</chat>"
)
entries = ccs.parse_tool_output(RAW)
check("parser reads both blocks regardless of attribute order",
      len(entries) == 2 and entries[0]["uuid"] == "aaa-111"
      and entries[1]["uuid"] == "bbb-222")
check("parser defaults kind", entries[1]["kind"] == "conversation")
check("HTML entities resolved",
      "hallo > welt & mehr" in entries[0]["fragments"][0]["text"])
check("block starting with a user label is flagged as chat start",
      entries[0]["fragments"][0]["is_chat_start"])
check("gap marker splits a block into two fragments",
      len(entries[1]["fragments"]) == 2, str(entries[1]["fragments"]))
check("only the first fragment can be the chat start",
      not any(fragment["is_chat_start"] for fragment in entries[1]["fragments"][1:]))

MULTI = (
    "<chat url='https://claude.ai/chat/same-1' updated_at='2026-03-03'>"
    "Title: Doppelt\nDoppelt\nH: erster block</chat>"
    "<chat url='https://claude.ai/chat/same-1' updated_at='2026-03-03'>"
    "Title: Doppelt\nDoppelt\nA: zweiter block</chat>"
)
grouped = ccs.group_entries_by_uuid(ccs.parse_tool_output(MULTI))
check("blocks of the same chat are grouped",
      len(grouped) == 1 and len(grouped["same-1"]["fragments"]) == 2)


# ---------------------------------------------------------------------------
# Merging semantics
# ---------------------------------------------------------------------------

CHAT = ("H: Wir besprechen heute die Segmentierungslogik des Projekts "
        "Quenya mit der Datei chat_crawl_store.py und den Funktionen "
        "normalize_with_map sowie find_overlap im Detail.\n"
        "A: Die Overlap-Erkennung nutzt normalisierte Zeichenketten, "
        "damit Whitespace-Unterschiede der Suchmaschine keine Rolle spielen.\n"
        "H: Gut, dann erweitern wir den Store um ein close Kommando und "
        "eine Export Funktion fuer die rekonstruierten Transkripte.\n"
        "A: Einverstanden, das Export Kommando schreibt die Segmente "
        "mit sichtbaren Luecken-Markern in eine Datei oder nach stdout.")

store = ccs.new_store("uuid-x", "https://claude.ai/chat/uuid-x")
A, B, C, D = CHAT[:220], CHAT[150:420], CHAT[500:], CHAT[350:560]

result = ccs.merge_fragment(store, A, "q1", is_chat_start=True)
check("first fragment becomes a new segment", result["action"] == "new")
check("chat start sets its own flag and closes the head",
      store["segments"][0]["chat_start"]
      and store["segments"][0]["edges"]["head"]["closed"])
result = ccs.merge_fragment(store, B, "q2")
check("overlapping fragment extends", result["action"] == "extended"
      and len(store["segments"]) == 1 and result["grew"])
result = ccs.merge_fragment(store, C, "q3")
check("distant fragment becomes an isolated segment",
      result["action"] == "new" and len(store["segments"]) == 2)
result = ccs.merge_fragment(store, D, "q4")
check("bridge fragment consolidates into one segment",
      len(store["segments"]) == 1 and store["stats"]["segment_joins"] >= 1)
check("consolidation reports a remap", bool(result["remap"]))
check("the reported segment id still exists",
      ccs._find_segment(store, result["segment_id"]) is not None)
check("reconstruction equals the original (normalised)",
      ccs.norm_of(store["segments"][0]["text"]) == ccs.norm_of(CHAT))
check("chat_start survives consolidation", store["segments"][0]["chat_start"])
check("tail stays open (no end detection)",
      not store["segments"][0]["edges"]["tail"]["closed"])

result = ccs.merge_fragment(store, CHAT[100:200], "q5")
check("known fragment reported as contained without growth",
      result["action"] == "contained" and not result["grew"])

store2 = ccs.new_store("uuid-y", "u")
ccs.merge_fragment(store2, CHAT[200:500], "p1")
result = ccs.merge_fragment(store2, CHAT[:280], "p2", is_chat_start=True)
check("preceding fragment prepends and marks the chat start",
      result["action"] == "extended"
      and store2["segments"][0]["chat_start"]
      and ccs.norm_of(store2["segments"][0]["text"]) == ccs.norm_of(CHAT[:500]))

store3 = ccs.new_store("uuid-z", "u")
ccs.merge_fragment(store3, CHAT[100:300], "s1")
result = ccs.merge_fragment(store3, CHAT, "s2", is_chat_start=True)
check("containing fragment supersedes",
      result["action"] == "superseded"
      and ccs.norm_of(store3["segments"][0]["text"]) == ccs.norm_of(CHAT)
      and store3["segments"][0]["chat_start"])

# A superseded segment must not keep counters describing replaced edge text.
store3b = ccs.new_store("uuid-z2", "u")
ccs.merge_fragment(store3b, CHAT[100:300], "t1")
seg3b = store3b["segments"][0]
seg3b["edges"]["tail"]["barren"] = ccs.BARREN_LIMIT
seg3b["edges"]["head"]["barren"] = ccs.BARREN_LIMIT
ccs.merge_fragment(store3b, CHAT, "t2")
check("superseding resets counters of edges whose text changed",
      store3b["segments"][0]["edges"]["tail"]["barren"] == 0
      and store3b["segments"][0]["edges"]["head"]["barren"] == 0)

REPEAT = "wiederholter block der genau gleich ist hier steht er"
store4 = ccs.new_store("uuid-a", "u")
ccs.merge_fragment(store4, "anfang teil " + REPEAT + " mitte teil " + REPEAT,
                   "a1", min_overlap=20)
before = len(store4["segments"])
result = ccs.merge_fragment(store4, REPEAT + " voellig neuer anschlusstext hier",
                            "a2", min_overlap=20)
check("ambiguous overlap keeps the fragment as a new segment",
      result["action"] == "new" and result.get("had_ambiguous")
      and len(store4["segments"]) == before + 1
      and store4["stats"]["ambiguous_rejections"] == 1)

store5 = ccs.new_store("uuid-b", "u")
big = ccs._new_segment(1, CHAT[50:600], "")
small = ccs._new_segment(2, CHAT[200:400], "")
small["edges"]["head"]["closed"] = True
small["edges"]["tail"]["closed"] = True
small["chat_start"] = True
store5["segments"] = [big, small]
ccs._consolidate(store5, ccs.DEFAULT_MIN_OVERLAP)
check("mid-containment does not leak closed flags or chat_start",
      len(store5["segments"]) == 1
      and not store5["segments"][0]["edges"]["head"]["closed"]
      and not store5["segments"][0]["edges"]["tail"]["closed"]
      and not store5["segments"][0]["chat_start"])

store6 = ccs.new_store("uuid-c", "u")
ccs.merge_fragment(store6, CHAT[:300], "w1")
variant = re.sub(r" ", "\n  ", CHAT[200:520])
result = ccs.merge_fragment(store6, variant, "w2")
check("whitespace-mangled fragment still joins",
      result["action"] == "extended"
      and ccs.norm_of(store6["segments"][0]["text"]) == ccs.norm_of(CHAT[:520]))


# ---------------------------------------------------------------------------
# Edge bookkeeping
# ---------------------------------------------------------------------------

store7 = ccs.new_store("uuid-e", "u")
ccs.merge_fragment(store7, CHAT[:300], "")
suggestions = ccs.suggest_queries(store7, 2)
check("suggest_queries returns suggestions", len(suggestions) > 0)
ccs.remember_suggestions(store7, suggestions)
check("suggestions are remembered with their edge",
      len(store7["pending_queries"]) == len(suggestions)
      and store7["pending_queries"][0]["side"] in ("head", "tail"))

tracked = suggestions[0]
segment = ccs._find_segment(store7, tracked["segment_id"])
edge = segment["edges"][tracked["side"]]
ccs.account_query(store7, tracked["query"], set())
check("fruitless query increments barren and consumes the pending entry",
      edge["barren"] == 1 and edge["attempts"] == 1
      and not any(item["query"] == tracked["query"]
                  for item in store7["pending_queries"]))

# Growth in an unrelated segment must not credit this edge.
ccs.remember_suggestions(store7, [tracked])
ccs.account_query(store7, tracked["query"], {999})
check("growth elsewhere does not credit the queried edge", edge["barren"] == 2)

ccs.remember_suggestions(store7, [tracked])
ccs.account_query(store7, tracked["query"], set())
check("barren reaching the limit exhausts the edge", ccs.edge_exhausted(edge))
check("exhausted edges vanish from open_edges",
      not any(item["side"] == tracked["side"]
              and item["segment_id"] == tracked["segment_id"]
              for item in ccs.open_edges(store7)))

ccs.remember_suggestions(store7, [tracked])
ccs.account_query(store7, tracked["query"], {segment["id"]})
check("growth in the owning segment resets barren",
      edge["barren"] == 0 and edge["attempts"] == 4)

before = [(seg["id"], side, dict(edge))
          for seg in store7["segments"]
          for side, edge in seg["edges"].items()]
unknown_note = ccs.account_query(store7, "never suggested", {1})
after = [(seg["id"], side, dict(edge))
         for seg in store7["segments"]
         for side, edge in seg["edges"].items()]
check("unknown query changes no edge counter", before == after)
check("unknown query is called out exactly when suggestions were pending",
      ("not one of the suggestions" in unknown_note)
      == bool(store7["pending_queries"]), unknown_note)

flood = ccs.new_store("uuid-flood", "u")
ccs.merge_fragment(flood, CHAT[:300], "")
ccs.remember_suggestions(flood, [{"query": f"q{index}", "segment_id": 1,
                                  "side": "tail"}
                                 for index in range(ccs.PENDING_QUERY_LIMIT + 20)])
check("pending queries are capped",
      len(flood["pending_queries"]) == ccs.PENDING_QUERY_LIMIT)

store8 = ccs.new_store("uuid-f", "u")
ccs.merge_fragment(store8, CHAT[:300], "")
seg8 = store8["segments"][0]
seg8["edges"]["head"]["closed"] = True
seg8["edges"]["tail"]["barren"] = ccs.BARREN_LIMIT
check("crawl_finished when every edge is done", ccs.crawl_finished(store8))
check("empty store is not finished", not ccs.crawl_finished(ccs.new_store("u", "u")))

store["queries_used"].extend(item["query"] for item in ccs.suggest_queries(store))
check("used queries are not suggested again",
      all(item["query"] not in store["queries_used"]
          for item in ccs.suggest_queries(store)))


# ---------------------------------------------------------------------------
# Message splitting and export
# ---------------------------------------------------------------------------

messages, msg_warns = ccs.split_messages(CHAT)
check("messages split at speaker labels", len(messages) == 4, str(len(messages)))
check("roles alternate correctly",
      [message["role"] for message in messages]
      == ["user", "assistant", "user", "assistant"])
check("labels are stripped from the content",
      not messages[0]["content"].startswith("H:"))
check("clean split raises no warning", msg_warns == [], str(msg_warns))

long_messages, _ = ccs.split_messages("Human: frage\nAssistant: antwort\n")
check("long labels split into messages",
      [message["role"] for message in long_messages] == ["user", "assistant"])

lead_messages, _ = ccs.split_messages("rest einer antwort\nH: neue frage\n")
check("leading unlabelled text inherits the opposite role",
      lead_messages[0]["role"] == "assistant"
      and lead_messages[1]["role"] == "user")

fenced_messages, fenced_warns = ccs.split_messages(
    "H: schau her\n```\nH: das ist code\n```\nnoch text\n")
check("labels inside a code fence do not split messages",
      len(fenced_messages) == 1)
check("balanced fences raise no fence warning",
      not any("odd number" in message for message in fenced_warns))

_, odd_warns = ccs.split_messages("H: text\n```\ncode ohne ende\n")
check("odd fence count in a segment warns",
      any("odd number" in message for message in odd_warns), str(odd_warns))

unknown_messages, unknown_warns = ccs.split_messages("nur text ohne label")
check("segment without labels yields role unknown plus a warning",
      unknown_messages[0]["role"] == "unknown"
      and any("role unknown" in message for message in unknown_warns))

export_store = ccs.new_store("uuid-exp", "https://claude.ai/chat/uuid-exp",
                             "Titel", "2026-05-28T16:39:31.142718+00:00")
ccs.merge_fragment(export_store, CHAT, "", is_chat_start=True)
ccs.add_warning(export_store, "ingest", "something to carry over")
document = ccs.build_export(export_store, predecessor="prev-uuid")
check("export metadata complete",
      document["metadata"]["chat_date"] == "2026-05-28"
      and document["metadata"]["chat_uuid"] == "uuid-exp"
      and document["metadata"]["predecessor"] == "prev-uuid"
      and document["metadata"]["successor"] is None
      and document["metadata"]["segment_order"] == "unknown_except_chat_start")
check("export marks the chat start segment",
      document["segments"][0]["chat_start"] is True)
check("export carries store warnings",
      any(entry["message"] == "something to carry over"
          for entry in document["warnings"]))

# Closing a head edge by hand must not fake a chat start in the export.
manual = ccs.new_store("uuid-man", "u")
ccs.merge_fragment(manual, CHAT[200:500], "")
manual["segments"][0]["edges"]["head"]["closed"] = True
check("manually closed head does not claim a chat start",
      ccs.build_export(manual)["segments"][0]["chat_start"] is False)

no_date = ccs.new_store("uuid-nd", "u")
check("missing updated_at exports as 'unknown'",
      ccs.build_export(no_date)["metadata"]["chat_date"] == "unknown")


# ---------------------------------------------------------------------------
# Schema upgrade
# ---------------------------------------------------------------------------

V3 = {"schema_version": 3, "chat_uuid": "u", "url": "x", "title": "",
      "updated_at": "",
      "segments": [{"id": 1, "text": "H: abc",
                    "edges": {"head": {"closed": True, "attempts": 2, "barren": 0},
                              "tail": {"closed": False, "attempts": 0, "barren": 1}},
                    "origin_queries": []}],
      "queries_used": [], "pending_queries": [], "warnings": [],
      "stats": ccs._empty_stats()}
upgraded_v3 = ccs.upgrade_store(json.loads(json.dumps(V3)))
check("v3 store gains chat_start from the head edge",
      upgraded_v3["schema_version"] == ccs.SCHEMA_VERSION
      and upgraded_v3["segments"][0]["chat_start"] is True)

V2 = {"schema_version": 2, "chat_uuid": "u", "url": "x", "title": "", "updated_at": "",
      "segments": [{"id": 1, "text": "H: abc", "head_closed": False,
                    "tail_closed": False, "stale": 2, "origin_queries": []}],
      "queries_used": [],
      "stats": {"fragments_seen": 1, "merge_events": 0, "new_segment_events": 1,
                "contained_events": 0, "ambiguous_rejections": 0,
                "segment_joins": 0, "empty_fragments": 0}}
upgraded_v2 = ccs.upgrade_store(json.loads(json.dumps(V2)))
check("v2 store upgraded to the current schema",
      upgraded_v2["schema_version"] == ccs.SCHEMA_VERSION
      and upgraded_v2["segments"][0]["edges"]["head"]["closed"] is False
      and upgraded_v2["segments"][0]["chat_start"] is False
      and "stale" not in upgraded_v2["segments"][0]
      and upgraded_v2["pending_queries"] == []
      and upgraded_v2["warnings"] == [])


# ---------------------------------------------------------------------------
# Contradictory chat-start observations must be recorded, not swallowed
# ---------------------------------------------------------------------------

contra = ccs.new_store("uuid-contra", "u")
ccs.merge_fragment(contra, CHAT[:200], "")
result = ccs.merge_fragment(contra, CHAT[130:400], "", is_chat_start=True)
check("chat-start fragment joining at a tail leaves a warning",
      result["action"] == "extended"
      and any("appended at the tail" in entry["message"]
              for entry in contra["warnings"]),
      str(contra["warnings"]))

contra2 = ccs.new_store("uuid-contra2", "u")
ccs.merge_fragment(contra2, CHAT[100:300], "", is_chat_start=True)
result = ccs.merge_fragment(contra2, CHAT[:400], "")
check("superseding text before a chat-start segment warns and drops the mark",
      result["action"] == "superseded"
      and not contra2["segments"][0]["chat_start"]
      and any("mark was dropped" in entry["message"]
              for entry in contra2["warnings"]),
      str(contra2["warnings"]))

contra3 = ccs.new_store("uuid-contra3", "u")
ccs.merge_fragment(contra3, CHAT[100:400], "", is_chat_start=True)
result = ccs.merge_fragment(contra3, CHAT[:200], "")
check("prepending before a chat-start segment warns and drops the mark",
      result["action"] == "extended"
      and not contra3["segments"][0]["chat_start"]
      and any("prepended before" in entry["message"]
              for entry in contra3["warnings"]),
      str(contra3["warnings"]))

contra4 = ccs.new_store("uuid-contra4", "u")
ccs.merge_fragment(contra4, CHAT[:400], "")
result = ccs.merge_fragment(contra4, CHAT[100:300], "", is_chat_start=True)
check("contained chat-start fragment away from the head warns",
      result["action"] == "contained"
      and not contra4["segments"][0]["chat_start"]
      and any("not at its head" in entry["message"]
              for entry in contra4["warnings"]),
      str(contra4["warnings"]))


# ---------------------------------------------------------------------------
# End-to-end CLI
# ---------------------------------------------------------------------------

WORK = tempfile.mkdtemp(prefix="crawl-e2e-")
SCRIPT = os.path.abspath(ccs.__file__)
UUID = "e2e-uuid-1"
STORE_DIR = os.path.join(WORK, "store")


def dump(name, body, uuid=UUID):
    """Write a raw <chat> block to a file and return its path."""
    path = os.path.join(WORK, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(f"<chat url='https://claude.ai/chat/{uuid}' "
                     f"updated_at='2026-08-01T10:00:00Z' "
                     f"kind='conversation'>{body}</chat>\n")
    return path


def run(*args):
    """Invoke the CLI with the test store directory."""
    return subprocess.run(
        [sys.executable, SCRIPT, "--store-dir", STORE_DIR, *args],
        capture_output=True, text=True)


HEADER = "Title: E2E Chat\nE2E Chat\n"
first = dump("d1.txt", HEADER + CHAT[:260])
second = dump("d2.txt", HEADER + CHAT[180:520])

result = run("ingest", "--raw", first, "--query", "erste query")
check("CLI ingest 1 exits 0", result.returncode == 0, result.stderr)
check("CLI ingest 1 reports a new segment", "new" in result.stdout, result.stdout)
result = run("ingest", "--raw", second, "--query", "zweite query")
check("CLI ingest 2 extends", "extended" in result.stdout,
      result.stdout + result.stderr)

result = run("status")
check("CLI status runs", result.returncode == 0 and UUID in result.stdout)
check("CLI status shows edge counters", "head a" in result.stdout, result.stdout)
check("CLI status on a missing chat exits 1",
      run("status", "--chat", "does-not-exist").returncode == 1)

result = run("queries", "--chat", UUID, "-n", "3")
check("CLI queries runs", result.returncode == 0 and "seg" in result.stdout,
      result.stdout)
suggested = result.stdout.strip().splitlines()[0].split("]", 1)[1].strip()

result = run("ingest", "--raw", second, "--query", suggested)
check("CLI credits a remembered query to its edge",
      "edge" in result.stdout, result.stdout)

result = run("report", "--chat", UUID)
check("CLI report runs", result.returncode == 0)

result = run("close", "--chat", UUID, "--segment", "1", "--side", "tail")
check("CLI close runs", result.returncode == 0 and "closed" in result.stdout)
check("closed tail visible in status", "]" in run("status", "--chat", UUID).stdout)
result = run("close", "--chat", UUID, "--segment", "1", "--side", "tail", "--reopen")
check("CLI reopen runs", result.returncode == 0 and "reopened" in result.stdout)
check("CLI close on a missing segment exits 1",
      run("close", "--chat", UUID, "--segment", "99", "--side", "tail").returncode == 1)

out_path = os.path.join(WORK, "export.json")
result = run("export", "--chat", UUID, "--out", out_path,
             "--predecessor", "prev-1", "--successor", "next-1")
check("CLI export runs", result.returncode == 0, result.stderr)
with open(out_path, "r", encoding="utf-8") as handle:
    exported = json.load(handle)
check("exported file has the agreed shape",
      exported["metadata"]["chat_uuid"] == UUID
      and exported["metadata"]["predecessor"] == "prev-1"
      and exported["metadata"]["successor"] == "next-1"
      and exported["segments"][0]["messages"][0]["role"] in ("user", "assistant")
      and isinstance(exported["warnings"], list))

# Two blocks of one chat in a single dump must be settled together.
multi_path = os.path.join(WORK, "multi.txt")
with open(multi_path, "w", encoding="utf-8") as handle:
    for body in (HEADER + CHAT[:200], HEADER + CHAT[400:]):
        handle.write(f"<chat url='https://claude.ai/chat/multi-1' "
                     f"updated_at='2026-08-01T10:00:00Z'>{body}</chat>\n")
result = run("ingest", "--raw", multi_path, "--query", "")
check("CLI merges both blocks of one chat in a single pass",
      result.returncode == 0 and "2 fragment(s)" in result.stdout, result.stdout)

empty = os.path.join(WORK, "empty.txt")
open(empty, "w").close()
check("CLI ingest on an empty dump exits 1",
      run("ingest", "--raw", empty).returncode == 1)

# Foreign JSON files in the store directory are skipped, never mistaken for
# chat stores: an export written there by accident and a leftover v3 index.
foreign = os.path.join(STORE_DIR, "chat_foreign.json")
shutil.copy(out_path, foreign)
result = run("status")
check("status skips an export file lying in the store directory",
      result.returncode == 0 and "Skipping foreign JSON" in result.stderr
      and UUID in result.stdout,
      result.stdout + result.stderr)
result = run("status", "--chat", "chat_foreign")
check("status --chat on a foreign JSON file exits 1 with a clear message",
      result.returncode == 1 and "Not a chat store" in result.stderr,
      result.stderr)
os.remove(foreign)

# A legacy v3 index.json is folded into the crawl state on first contact.
MIG_DIR = os.path.join(WORK, "mig-store")
os.makedirs(MIG_DIR)
with open(os.path.join(MIG_DIR, "index.json"), "w", encoding="utf-8") as handle:
    json.dump({"chats": {"legacy-1": {
        "url": "https://claude.ai/chat/legacy-1",
        "title": "Alter Titel", "updated_at": "2026-01-01T00:00:00Z"}}}, handle)
result = subprocess.run(
    [sys.executable, SCRIPT, "--store-dir", MIG_DIR, "overview"],
    capture_output=True, text=True)
check("legacy index.json is migrated into the crawl state",
      result.returncode == 0
      and os.path.exists(os.path.join(MIG_DIR, "index.json.migrated"))
      and not os.path.exists(os.path.join(MIG_DIR, "index.json"))
      and os.path.exists(os.path.join(MIG_DIR, ccs.STATE_FILENAME)),
      result.stdout + result.stderr)
check("the migrated title is visible to the crawl",
      "Alter Titel" in result.stdout, result.stdout)
with open(os.path.join(MIG_DIR, ccs.STATE_FILENAME), encoding="utf-8") as handle:
    migrated_state = json.load(handle)
check("the migrated chat starts as untouched",
      migrated_state["chats"]["legacy-1"]["status"] == "untouched",
      str(migrated_state["chats"]))
result = subprocess.run(
    [sys.executable, SCRIPT, "--store-dir", MIG_DIR, "overview"],
    capture_output=True, text=True)
check("the migration runs only once",
      result.returncode == 0 and "Migrated legacy" not in result.stderr,
      result.stderr)

# ---------------------------------------------------------------------------
# Crawl state and chat status
# ---------------------------------------------------------------------------

STATE_DIR = os.path.join(WORK, "state-store")
TARGET = "state-target"
BYSTANDER = "state-bystander"


def run_state(*args):
    """Invoke the CLI against the status test store."""
    return subprocess.run(
        [sys.executable, SCRIPT, "--store-dir", STATE_DIR, *args],
        capture_output=True, text=True)


def read_state_of(store_dir):
    """Read the crawl state file the CLI wrote into *store_dir*."""
    with open(os.path.join(store_dir, ccs.STATE_FILENAME),
              "r", encoding="utf-8") as handle:
        return json.load(handle)


def status_of_dir(store_dir, uuid):
    """Return the recorded status of one chat, or None when unknown."""
    return read_state_of(store_dir)["chats"].get(uuid, {}).get("status")


def read_state():
    """Read the crawl state of the status test store."""
    return read_state_of(STATE_DIR)


def status_of(uuid):
    """Return the recorded status of one chat in the status test store."""
    return status_of_dir(STATE_DIR, uuid)


def write_blocks(name, blocks):
    """Write several <chat> blocks, possibly of different chats, to one file."""
    path = os.path.join(WORK, name)
    with open(path, "w", encoding="utf-8") as handle:
        for uuid, body in blocks:
            handle.write(f"<chat url='https://claude.ai/chat/{uuid}' "
                         f"updated_at='2026-08-02T10:00:00Z'>{body}</chat>\n")
    return path


# One dump carrying two chats: the one that was searched for and a bystander
# that merely turned up in the same result.
pair = write_blocks("pair.txt", [(TARGET, HEADER + CHAT[:260]),
                                 (BYSTANDER, HEADER + CHAT[:260])])
result = run_state("ingest", "--raw", pair, "--query", "cluster term")
check("ingest creates the crawl state file",
      result.returncode == 0
      and os.path.exists(os.path.join(STATE_DIR, ccs.STATE_FILENAME)),
      result.stderr)
check("a newly seen chat starts as untouched",
      status_of(TARGET) == "untouched" and status_of(BYSTANDER) == "untouched",
      str(read_state()["chats"]))
check("ingest records the title of a chat nobody searched for",
      read_state()["chats"][BYSTANDER].get("title") == "E2E Chat",
      str(read_state()["chats"][BYSTANDER]))
check("the state file is not mistaken for a chat store",
      run_state("status").returncode == 0)

result = run_state("queries", "--chat", TARGET, "-n", "3")
check("queries marks the chat as started",
      result.returncode == 0 and status_of(TARGET) == "started",
      result.stdout + result.stderr)
check("querying one chat leaves the bystander untouched",
      status_of(BYSTANDER) == "untouched")

# Growing inside a dump fetched for someone else is not the same as being
# worked on -- this is what keeps the ACTIVE_LIMIT cap meaningful.
grow = write_blocks("grow.txt", [(BYSTANDER, HEADER + CHAT[180:520])])
result = run_state("ingest", "--raw", grow, "--query", "cluster term")
check("a chat that grows in another chat's dump stays untouched",
      result.returncode == 0 and "extended" in result.stdout
      and status_of(BYSTANDER) == "untouched",
      result.stdout + result.stderr)

# Exporting early is legitimate and must stay visible as unfinished.
export_path = os.path.join(WORK, "state-export.json")
result = run_state("export", "--chat", TARGET, "--out", export_path)
check("export of an unfinished chat leaves the status alone",
      result.returncode == 0 and status_of(TARGET) == "started",
      result.stdout + result.stderr)
check("export says so when the chat stayed unfinished",
      "unfinished" in result.stdout, result.stdout)

for segment in ccs.load_store(ccs.store_path(STATE_DIR, TARGET))["segments"]:
    for side in ("head", "tail"):
        run_state("close", "--chat", TARGET,
                  "--segment", str(segment["id"]), "--side", side)
result = run_state("export", "--chat", TARGET, "--out", export_path)
check("export of an exhausted crawl sets done",
      result.returncode == 0 and status_of(TARGET) == "done",
      result.stdout + result.stderr)
check("export names the transition to done", "done" in result.stdout,
      result.stdout)

# A finished chat whose edge was reopened by hand must not fall back to
# 'started' just because it can be queried again.
run_state("close", "--chat", TARGET, "--segment", "1", "--side", "tail",
          "--reopen")
result = run_state("queries", "--chat", TARGET, "-n", "3")
check("queries does not drag a finished chat back into work",
      status_of(TARGET) == "done", result.stdout + result.stderr)

# ---------------------------------------------------------------------------
# Overview: the report that has to state the next action on its own
# ---------------------------------------------------------------------------

OVER_DIR = os.path.join(WORK, "overview-store")


def run_over(*args):
    """Invoke the CLI against the overview test store."""
    return subprocess.run(
        [sys.executable, SCRIPT, "--store-dir", OVER_DIR, *args],
        capture_output=True, text=True)


result = run_over("overview")
check("overview on an empty directory exits 0 instead of failing",
      result.returncode == 0, result.stderr)
check("overview without a state file asks the user to decide",
      "NO CRAWL STATE" in result.stdout
      and "fresh export" in result.stdout
      and "continuing earlier work" in result.stdout, result.stdout)

# Four chats, distinct timestamps, so the working order is observable.
STAMPS = {"ov-1": "2026-01-01T00:00:00Z", "ov-2": "2026-02-01T00:00:00Z",
          "ov-3": "2026-03-01T00:00:00Z", "ov-4": "2026-04-01T00:00:00Z"}
ov_path = os.path.join(WORK, "ov.txt")
with open(ov_path, "w", encoding="utf-8") as handle:
    for uuid, stamp in STAMPS.items():
        handle.write(f"<chat url='https://claude.ai/chat/{uuid}' "
                     f"updated_at='{stamp}'>Title: Chat {uuid}\nChat {uuid}\n"
                     f"{CHAT[:260]}</chat>\n")
run_over("ingest", "--raw", ov_path, "--query", "cluster term")

result = run_over("overview")
check("overview reports an idle round without claiming which case it is",
      "IDLE" in result.stdout and "only you know" in result.stdout,
      result.stdout)
check("overview counts the untouched chats", "4 untouched" in result.stdout,
      result.stdout)
check("overview offers all three slots when nothing is active",
      "3 free slot(s)" in result.stdout, result.stdout)

run_over("state", "--order", "oldest-first")
oldest_first = run_over("overview").stdout
run_over("state", "--order", "newest-first")
newest_first = run_over("overview").stdout


def section(report, name):
    """Return one section of an overview report, header line excluded.

    Anchored at the start of a line, because the section names also occur
    inside the guidance text further up.
    """
    header = re.search(rf"^{name}.*$", report, re.M)
    if header is None:
        return ""
    return report[header.end():].split("\n\n")[0]


def first_nominee(report):
    """Return the uuid named first under NEXT UP."""
    return re.search(r"(ov-\d)", section(report, "NEXT UP")).group(1)


check("oldest-first nominates the oldest chat first",
      first_nominee(oldest_first) == "ov-1", first_nominee(oldest_first))
check("newest-first nominates the newest chat first",
      first_nominee(newest_first) == "ov-4", first_nominee(newest_first))

run_over("state", "--order", "oldest-first")
for uuid in ("ov-1", "ov-2", "ov-3"):
    run_over("queries", "--chat", uuid, "-n", "2")
result = run_over("overview")
check("three started chats fill the round", "3 of at most 3" in result.stdout,
      result.stdout)
check("no fourth chat is nominated while the round is full",
      "no free slot" in result.stdout
      and "ov-4" not in section(result.stdout, "NEXT UP"), result.stdout)
check("the handover names the state file and the three store files",
      ccs.STATE_FILENAME in section(result.stdout, "HANDOVER")
      and "4 file(s) in total" in result.stdout, result.stdout)
check("the handover names by-catch stores that stay behind by design",
      "BY DESIGN" in section(result.stdout, "HANDOVER"), result.stdout)

# A chat that ran dry frees its slot again without being done yet.
for segment in ccs.load_store(ccs.store_path(OVER_DIR, "ov-1"))["segments"]:
    for side in ("head", "tail"):
        run_over("close", "--chat", "ov-1", "--segment", str(segment["id"]),
                 "--side", side)
result = run_over("overview")
check("a chat without open edges frees its slot",
      "2 of at most 3" in result.stdout and "1 free" in result.stdout,
      result.stdout)
check("the drained chat is offered for export",
      "ov-1" in section(result.stdout, "READY TO EXPORT"), result.stdout)
check("the freed slot nominates the next chat in order",
      first_nominee(result.stdout) == "ov-4", result.stdout)

# order stays changeable after work has begun; it must not touch what is done
run_over("export", "--chat", "ov-1", "--out", os.path.join(WORK, "ov1.json"))
result = run_over("state", "--order", "newest-first")
check("the working order can still be changed after work has begun",
      result.returncode == 0, result.stderr)
check("changing the order leaves a finished chat done",
      status_of_dir(OVER_DIR, "ov-1") == "done")

result = run_over("state")
check("state without an argument explains itself and exits 1",
      result.returncode == 1 and "--order" in result.stderr, result.stderr)
result = run_over("state", "--status", "done")
check("state --status without --chat exits 1", result.returncode == 1,
      result.stderr)
result = run_over("state", "--chat", "ov-2", "--status", "done")
check("state --status corrects a status by hand",
      result.returncode == 0 and status_of_dir(OVER_DIR, "ov-2") == "done",
      result.stdout + result.stderr)

# A started chat whose store file is gone must be asked for by name.
os.remove(ccs.store_path(OVER_DIR, "ov-3"))
result = run_over("overview")
check("overview asks for the store file of a started chat that is absent",
      "ov-3" in section(result.stdout, "MISSING STORE FILES"), result.stdout)

# Without the state file everything has to be recovered from the stores.
os.remove(os.path.join(OVER_DIR, ccs.STATE_FILENAME))
result = run_over("overview")
check("overview flags a missing state file as loss, not as a fresh start",
      result.returncode == 0 and f"no {ccs.STATE_FILENAME}" in result.stdout
      and "recovered" in result.stdout, result.stdout)
check("the loss banner is precise about what survives and what is gone",
      "titles and progress included" in result.stdout
      and "'done' mark" in result.stdout, result.stdout)

# ---------------------------------------------------------------------------
# Header-only bootstrap: building the title map without transcribing bodies
# ---------------------------------------------------------------------------

HDR_DIR = os.path.join(WORK, "header-store")


def run_hdr(*args):
    """Invoke the CLI against the header-bootstrap test store."""
    return subprocess.run(
        [sys.executable, SCRIPT, "--store-dir", HDR_DIR, *args],
        capture_output=True, text=True)


hdr_path = os.path.join(WORK, "titles.txt")
with open(hdr_path, "w", encoding="utf-8") as handle:
    handle.write("<chat url='https://claude.ai/chat/hdr-1' "
                 "updated_at='2026-03-01T10:00:00Z'>Title: Nur ein Titel\n"
                 "</chat>\n")

result = run_hdr("ingest", "--raw", hdr_path, "--query", "")
check("a header-only dump ingests without error",
      result.returncode == 0 and "0 fragment(s)" in result.stdout,
      result.stdout + result.stderr)
check("a header-only dump still records uuid, title and timestamp",
      read_state_of(HDR_DIR)["chats"]["hdr-1"].get("title") == "Nur ein Titel"
      and read_state_of(HDR_DIR)["chats"]["hdr-1"].get("updated_at")
      == "2026-03-01T10:00:00Z",
      str(read_state_of(HDR_DIR)["chats"].get("hdr-1")))

result = run_hdr("overview")
check("overview does not suggest 'queries' for a chat that has no text yet",
      "hdr-1" in section(result.stdout, "NEXT UP")
      and "no text yet" in section(result.stdout, "NEXT UP")
      and "queries --chat hdr-1" not in section(result.stdout, "NEXT UP"),
      section(result.stdout, "NEXT UP"))
check("a chat without text is not offered for export",
      "hdr-1" not in section(result.stdout, "READY TO EXPORT"), result.stdout)

# The measured ellipsis behaviour the instructions rely on.
check("a glued ellipsis splits a body into two fragments",
      len(ccs.split_gap_markers("H: abc...def weiter")[0]) == 2)
check("an ellipsis with blanks on both sides is absorbed without warning",
      ccs.split_gap_markers("H: abc ... def weiter") == (
          ["H: abc ... def weiter"], []))

# ---------------------------------------------------------------------------
# Query discipline: invented terms must be called out, not silently accepted
# ---------------------------------------------------------------------------

disc = ccs.new_store("disc-1", "https://claude.ai/chat/disc-1", "Disc")
ccs.merge_fragment(disc, CHAT[:300], "erste query", ccs.DEFAULT_MIN_OVERLAP)

check("an off-suggestion query is silent while nothing was suggested",
      ccs.account_query(disc, "selbst erfunden", set()) == "")

ccs.remember_suggestions(disc, ccs.suggest_queries(disc, 3))
check("suggestions were produced for the open edges",
      len(disc["pending_queries"]) > 0)
note = ccs.account_query(disc, "selbst erfunden", set())
check("an off-suggestion query is called out once suggestions are pending",
      "not one of the suggestions" in note, note)
check("calling it out consumes no suggestion",
      len(disc["pending_queries"]) > 0)

suggested_query = disc["pending_queries"][0]["query"]
note = ccs.account_query(disc, suggested_query, {1})
check("a suggested query still credits its edge",
      "advanced" in note, note)

ISLAND_STATS = {"fragments_seen": 26, "merge_events": 5, "segment_joins": 2,
                "new_segment_events": 14, "contained_events": 7,
                "ambiguous_rejections": 0, "empty_fragments": 0}


def island_store(probes, spent):
    """Build an island-heavy store: *probes* aimed queries out of *spent*."""
    store = ccs.new_store("hint-1", "u")
    ccs.merge_fragment(store, CHAT[:300], "")
    store["stats"] = dict(ISLAND_STATS)
    store["segments"][0]["edges"]["tail"]["attempts"] = probes
    store["queries_used"] = [f"q{index}" for index in range(spent)]
    return store


# The real case observed in the field: 2 of 5 queries aimed at an edge.
check("the hint points at query discipline when few queries were aimed",
      "verbatim" in ccs._health_hint(island_store(2, 5)),
      ccs._health_hint(island_store(2, 5)))
# Disciplined run: one broad bootstrap query, the rest from suggestions.
check("the hint points at probe 3 when the queries were aimed",
      "probe 3" in ccs._health_hint(island_store(4, 5)),
      ccs._health_hint(island_store(4, 5)))
check("both readings name the counts they are based on",
      "islands (14)" in ccs._health_hint(island_store(2, 5))
      and "joins (7)" in ccs._health_hint(island_store(2, 5)))
check("no hint while too few fragments have been seen",
      ccs._health_hint(ccs.new_store("hint-2", "u")) == "")

result = run_over("overview")
check("overview reports how often the edges were aimed at",
      "edge probe(s) so far" in result.stdout, result.stdout)

shutil.rmtree(WORK, ignore_errors=True)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All checks passed.")
