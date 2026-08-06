#!/usr/bin/env python3
"""Self-test for chat_crawl_store: unit checks plus an end-to-end CLI run.

Run from the directory holding chat_crawl_store.py:

    python test_crawl_store.py
    python -O test_crawl_store.py     # verifies the __debug__ guards compile out
"""

import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

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

check("unknown query is accounted to nothing",
      ccs.account_query(store7, "never suggested", {1}) == "")

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
# End-to-end CLI
# ---------------------------------------------------------------------------

WORK = tempfile.mkdtemp(prefix="crawl-e2e-")
SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "chat_crawl_store.py")
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

shutil.rmtree(WORK, ignore_errors=True)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All checks passed.")
