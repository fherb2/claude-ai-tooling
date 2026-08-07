#!/usr/bin/env python3
"""Self-test for chat_read_store: unit checks plus an end-to-end CLI run.

Runnable from anywhere; the script under test is located relative to this
file, not to the working directory:

    python tests/test_read_store.py
    python -O tests/test_read_store.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(os.path.dirname(_HERE), "source")
sys.path.insert(0, SOURCE_DIR)

import chat_read_store as crs

SCRIPT = os.path.join(SOURCE_DIR, "chat_read_store.py")
FAILURES = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record and print one assertion result."""
    status = "ok  " if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# Fixtures modelled on the format observed on claude.ai in August 2026
# ---------------------------------------------------------------------------

UUID = "d64eea15-1547-40e6-9d04-ce58e9544874"


def page(uuid=UUID, total=6, first=0, last=1, next_token="t2", prev_token="",
         title="Flattening angled parts", turns=None):
    """Build one <chat> page in the observed read_conversation format."""
    attrs = [f'url="https://claude.ai/chat/{uuid}"',
             'updated_at="2025-11-13T22:07:44.559082+00:00"',
             f'total_turns="{total}"', f'turns="{first}-{last}"']
    if next_token:
        attrs.append(f'next_page_token="{next_token}"')
    if prev_token:
        attrs.append(f'prev_page_token="{prev_token}"')
    if turns is None:
        turns = [(index, "Human" if index % 2 == 0 else "Assistant",
                  f"Inhalt von Turn {index}, ausreichend lang zum Vergleichen.")
                 for index in range(first, last + 1)]
    body = [f"<title>{title}</title>", ""]
    for index, label, text in turns:
        body.append(f'<turn n="{index}">{label}: {text}</turn>')
        body.append("")
    return f"<chat {' '.join(attrs)}>" + "\n".join(body) + "</chat>\n"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

pages = crs.parse_pages(page())
check("one page parses to one record", len(pages) == 1, str(len(pages)))
first_page = pages[0]
check("uuid comes from the url", first_page["uuid"] == UUID, first_page["uuid"])
check("total_turns is read as an integer", first_page["total_turns"] == 6)
check("turn range is kept verbatim", first_page["range"] == "0-1")
check("next page token is read", first_page["next_page_token"] == "t2")
check("title is extracted", first_page["title"] == "Flattening angled parts")
check("both turns parse", len(first_page["turns"]) == 2)
check("Human maps to user", first_page["turns"][0]["role"] == "user")
check("Assistant maps to assistant", first_page["turns"][1]["role"] == "assistant")
check("the label is stripped from the text",
      first_page["turns"][0]["text"].startswith("Inhalt von Turn 0"),
      first_page["turns"][0]["text"][:40])
check("no warnings on a clean page", first_page["warnings"] == [],
      str(first_page["warnings"]))

# Attribute order must not matter, and unknown attributes must be ignored.
reordered = ('<chat total_turns="2" something_new="x" '
             f'url="https://claude.ai/chat/{UUID}" turns="0-0">'
             '<title>T</title><turn n="0">Human: hallo</turn></chat>')
odd = crs.parse_pages(reordered)[0]
check("attribute order and unknown attributes do not matter",
      odd["uuid"] == UUID and odd["total_turns"] == 2 and len(odd["turns"]) == 1)

# Short labels of the search tools are accepted too.
short = crs.parse_pages(page(turns=[(0, "H", "frage"), (1, "A", "antwort")]))[0]
check("short H/A labels are accepted",
      [turn["role"] for turn in short["turns"]] == ["user", "assistant"])

# A turn without a label keeps its text but is flagged.
unlabelled = crs.parse_pages(
    f'<chat url="https://claude.ai/chat/{UUID}" total_turns="1" turns="0-0">'
    '<turn n="0">ohne jedes Label</turn></chat>')[0]
check("an unlabelled turn keeps its text",
      unlabelled["turns"][0]["text"] == "ohne jedes Label")
check("an unlabelled turn is recorded as role unknown",
      unlabelled["turns"][0]["role"] == "unknown")
check("an unlabelled turn warns",
      any("no speaker label" in message for message in unlabelled["warnings"]),
      str(unlabelled["warnings"]))

# HTML entities are unescaped; the asymmetry is documented in the source.
escaped = crs.parse_pages(
    f'<chat url="https://claude.ai/chat/{UUID}" total_turns="1" turns="0-0">'
    '<turn n="0">Human: if a &gt; b &amp;&amp; c</turn></chat>')[0]
check("html entities are unescaped",
      escaped["turns"][0]["text"] == "if a > b && c",
      escaped["turns"][0]["text"])

# A missing closing tag is tolerated but reported.
truncated = crs.parse_pages(
    f'<chat url="https://claude.ai/chat/{UUID}" total_turns="1" turns="0-0">'
    '<turn n="0">Human: abgeschnitten</turn>')[0]
check("a block without </chat> still parses", len(truncated["turns"]) == 1)
check("a block without </chat> warns",
      any("</chat>" in message for message in truncated["warnings"]),
      str(truncated["warnings"]))

# Several pages, and pages of different chats, in one dump.
multi = crs.parse_pages(page(first=0, last=1, next_token="t2")
                        + page(uuid="other-uuid", first=0, last=1, total=2,
                               next_token=""))
check("several blocks in one dump parse separately", len(multi) == 2)
check("the second block keeps its own uuid", multi[1]["uuid"] == "other-uuid")
check("a page without a next token reports an empty one",
      multi[1]["next_page_token"] == "")

# A zero-width character in the title must not survive.
zero_width = crs.parse_pages(
    f'<chat url="https://claude.ai/chat/{UUID}" total_turns="1" turns="0-0">'
    '<title>Rein​es Titelchen</title>'
    '<turn n="0">Human: x</turn></chat>')[0]
check("zero-width characters are stripped from the title",
      zero_width["title"] == "Reines Titelchen", repr(zero_width["title"]))


# ---------------------------------------------------------------------------
# Ranges and completeness
# ---------------------------------------------------------------------------

check("empty ranges render as an empty string", crs.format_ranges([]) == "")
check("single numbers render alone", crs.format_ranges([4]) == "4")
check("runs collapse", crs.format_ranges([9, 10, 11]) == "9-11")
check("mixed runs and singles render in order",
      crs.format_ranges([3, 9, 10, 11, 40]) == "3, 9-11, 40",
      crs.format_ranges([3, 9, 10, 11, 40]))
check("a pair does not collapse into a range",
      crs.format_ranges([7, 8]) == "7-8")


# ---------------------------------------------------------------------------
# Merging
# ---------------------------------------------------------------------------

store = crs.new_store(UUID)
outcome = crs.merge_page(store, crs.parse_pages(page(first=0, last=1))[0])
check("merging a first page adds its turns", outcome["added"] == [0, 1])
check("the total is taken from the envelope", store["total_turns"] == 6)
check("missing turns are the difference to the total",
      crs.missing_turns(store) == [2, 3, 4, 5], str(crs.missing_turns(store)))
check("an incomplete chat is not complete", not crs.is_complete(store))
check("the forward token is the one of the furthest page",
      crs.next_token(store) == "t2", crs.next_token(store))

# Re-ingesting the same page must be a no-op in content.
before = json.dumps(store["turns"], sort_keys=True)
outcome = crs.merge_page(store, crs.parse_pages(page(first=0, last=1))[0])
check("re-ingesting a page changes no turn",
      json.dumps(store["turns"], sort_keys=True) == before)
check("re-ingesting reports the turns as already held",
      outcome["repeated"] == [0, 1] and outcome["added"] == [])
check("re-ingesting records no conflict",
      store["stats"]["turns_conflicting"] == 0)

# Pages arriving out of order: the forward token follows the furthest page.
crs.merge_page(store, crs.parse_pages(
    page(first=4, last=5, next_token="", prev_token="t4"))[0])
crs.merge_page(store, crs.parse_pages(
    page(first=2, last=3, next_token="t4", prev_token="t2"))[0])
check("out-of-order pages fill the gaps",
      crs.held_turns(store) == [0, 1, 2, 3, 4, 5], str(crs.held_turns(store)))
check("a chat with every turn is complete", crs.is_complete(store))
check("the forward token is empty once the furthest page had none",
      crs.next_token(store) == "", crs.next_token(store))
check("no backward token once the earliest page starts at turn 0",
      crs.prev_token(store) == "", crs.prev_token(store))
check("a complete chat has no gap token", crs.gap_token(store) == "")

# Entering a chat in the middle -- as a search result's page_token allows --
# is the case where the backward token matters.
midway = crs.new_store(UUID)
crs.merge_page(midway, crs.parse_pages(
    page(first=2, last=3, next_token="t4", prev_token="t0"))[0])
check("the backward token is reported when the start is not held",
      crs.prev_token(midway) == "t0", crs.prev_token(midway))
check("turns before the entry point count as missing",
      crs.missing_turns(midway) == [0, 1, 4, 5],
      str(crs.missing_turns(midway)))

# A gap left by out-of-order fetching must name the token that reopens it.
gapped = crs.new_store(UUID)
crs.merge_page(gapped, crs.parse_pages(page(first=0, last=1, next_token="t2"))[0])
crs.merge_page(gapped, crs.parse_pages(
    page(first=4, last=5, next_token="", prev_token="t4"))[0])
check("a gap is reported while the frontier is already reached",
      crs.missing_turns(gapped) == [2, 3] and crs.next_token(gapped) == "",
      str(crs.missing_turns(gapped)))
check("the gap token comes from the page ending just before it",
      crs.gap_token(gapped) == "t2", crs.gap_token(gapped))

# No page reaching the gap: the caller must be told, not handed a wrong token.
orphan = crs.new_store(UUID)
crs.merge_page(orphan, crs.parse_pages(
    page(first=4, last=5, next_token="", prev_token="t4"))[0])
check("an unreachable gap yields no token", crs.gap_token(orphan) == "",
      crs.gap_token(orphan))

# The same index with different text is the one case worth a warning.
conflict = crs.new_store(UUID)
crs.merge_page(conflict, crs.parse_pages(
    page(total=1, first=0, last=0, next_token="",
         turns=[(0, "Human", "die echte Fassung")]))[0])
outcome = crs.merge_page(conflict, crs.parse_pages(
    page(total=1, first=0, last=0, next_token="",
         turns=[(0, "Human", "eine umformulierte Fassung")]))[0])
check("a differing repeat of one turn is reported",
      outcome["conflicting"] == [0], str(outcome))
check("the newer text wins",
      conflict["turns"]["0"]["text"] == "eine umformulierte Fassung")
check("the conflict is recorded as a warning",
      any("different text" in entry["message"] for entry in conflict["warnings"]),
      str(conflict["warnings"]))

# A changed total_turns means the chat moved under us.
grown = crs.new_store(UUID)
crs.merge_page(grown, crs.parse_pages(page(total=6, first=0, last=1))[0])
crs.merge_page(grown, crs.parse_pages(page(total=8, first=2, last=3))[0])
check("a changed total_turns is taken over", grown["total_turns"] == 8)
check("a changed total_turns warns",
      any("total_turns changed" in entry["message"] for entry in grown["warnings"]),
      str(grown["warnings"]))

# An unknown total must not read as 'nothing missing'.
unknown_total = crs.new_store(UUID)
crs.merge_page(unknown_total, crs.parse_pages(
    f'<chat url="https://claude.ai/chat/{UUID}" turns="0-0">'
    '<turn n="0">Human: x</turn></chat>')[0])
check("an unknown total yields no missing list",
      crs.missing_turns(unknown_total) == [])
check("an unknown total is never complete", not crs.is_complete(unknown_total))


# ---------------------------------------------------------------------------
# recent_chats mapping
# ---------------------------------------------------------------------------

LISTING = (
    "<chat url='https://claude.ai/chat/aaa-1' updated_at='2026-01-05T08:00:00Z'>"
    "Content:\nTitle: Erster Chat\n</chat>\n"
    "<chat url='https://claude.ai/chat/bbb-2' updated_at='2026-02-11T08:00:00Z'>"
    "</chat>\n")
listed = crs.parse_chat_list(LISTING)
check("a listing yields one record per chat", len(listed) == 2)
check("a title in the listing is taken", listed[0]["title"] == "Erster Chat")
check("a chat without a title is still recorded",
      listed[1]["uuid"] == "bbb-2" and listed[1]["title"] == "")
check("the timestamp is taken", listed[1]["updated_at"] == "2026-02-11T08:00:00Z")


# ---------------------------------------------------------------------------
# End-to-end CLI
# ---------------------------------------------------------------------------

WORK = tempfile.mkdtemp(prefix="read-e2e-")
STORE_DIR = os.path.join(WORK, "store")


def run(*args):
    """Invoke the CLI against the test store directory."""
    return subprocess.run(
        [sys.executable, SCRIPT, "--store-dir", STORE_DIR, *args],
        capture_output=True, text=True)


def write(name, text):
    """Write a raw dump and return its path."""
    path = os.path.join(WORK, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def read_state():
    """Read the state file the CLI wrote."""
    with open(os.path.join(STORE_DIR, crs.STATE_FILENAME),
              "r", encoding="utf-8") as handle:
        return json.load(handle)


result = run("map", "--raw", write("listing.txt", LISTING))
check("CLI map exits 0", result.returncode == 0, result.stderr)
check("CLI map records both chats", len(read_state()["chats"]) == 2)
check("CLI map says how many lack a title", "without a title" in result.stdout,
      result.stdout)
check("mapped chats start as listed",
      all(entry["status"] == "listed"
          for entry in read_state()["chats"].values()))

result = run("ingest", "--raw", write("p1.txt", page(first=0, last=1)))
check("CLI ingest exits 0", result.returncode == 0, result.stderr)
check("CLI ingest reports held against the total", "2/6 held" in result.stdout,
      result.stdout)
check("CLI ingest names the missing turns", "missing: 2-5" in result.stdout,
      result.stdout)
check("CLI ingest names the next token", "next token: t2" in result.stdout,
      result.stdout)
check("ingesting a page registers the chat in the state",
      UUID in read_state()["chats"], str(read_state()["chats"].keys()))
check("the title from the page reaches the state",
      read_state()["chats"][UUID]["title"] == "Flattening angled parts")

result = run("status", "--chat", UUID)
check("CLI status runs", result.returncode == 0, result.stderr)
check("CLI status shows held against total", "2 of 6 held" in result.stdout,
      result.stdout)
check("CLI status lists what is missing", "Missing: 2-5" in result.stdout,
      result.stdout)
check("unread turns beyond the frontier read as a continuation, not a gap",
      "continue with page_token 't2'" in result.stdout
      and "gap below" not in result.stdout, result.stdout)

run("ingest", "--raw", write("p2.txt", page(first=2, last=3, next_token="t4")))
result = run("ingest", "--raw", write("p3.txt", page(first=4, last=5,
                                                     next_token="")))
check("the last page completes the chat", "COMPLETE" in result.stdout,
      result.stdout)
result = run("status", "--chat", UUID)
check("a complete chat says so in status", "COMPLETE" in result.stdout,
      result.stdout)
check("a complete chat has no Missing line", "Missing:" not in result.stdout,
      result.stdout)

# Idempotence over the real CLI, not just in memory.
before = json.dumps(crs.load_store(crs.store_path(STORE_DIR, UUID))["turns"],
                    sort_keys=True)
run("ingest", "--raw", write("p1again.txt", page(first=0, last=1)))
after = json.dumps(crs.load_store(crs.store_path(STORE_DIR, UUID))["turns"],
                   sort_keys=True)
check("re-ingesting through the CLI changes nothing", before == after)

# A foreign JSON file in the store directory must not break a scan.
with open(os.path.join(STORE_DIR, "export-something.json"), "w",
          encoding="utf-8") as handle:
    json.dump({"metadata": {}, "segments": []}, handle)
result = run("status")
check("a foreign JSON file is skipped, not fatal",
      result.returncode == 0 and "Skipping foreign JSON" in result.stderr,
      result.stdout + result.stderr)

# The other script's state file must be called out.
with open(os.path.join(STORE_DIR, crs.FOREIGN_STATE), "w",
          encoding="utf-8") as handle:
    json.dump({"chats": {}}, handle)
result = run("status", "--chat", UUID)
check("the other script's state file is called out",
      "chat_crawl_store.py" in result.stderr, result.stderr)

check("CLI ingest on an empty dump exits 1",
      run("ingest", "--raw", write("empty.txt", "")).returncode == 1)
check("CLI map on an empty dump exits 1",
      run("map", "--raw", write("empty2.txt", "")).returncode == 1)

os.remove(os.path.join(STORE_DIR, crs.FOREIGN_STATE))
os.remove(os.path.join(STORE_DIR, "export-something.json"))


# ---------------------------------------------------------------------------
# Status transitions and export
# ---------------------------------------------------------------------------

check("ingesting a page marks the chat started",
      read_state()["chats"][UUID]["status"] == "started",
      str(read_state()["chats"][UUID]))

export_path = os.path.join(WORK, "export.json")
result = run("export", "--chat", UUID, "--out", export_path)
check("CLI export runs", result.returncode == 0, result.stderr)
with open(export_path, "r", encoding="utf-8") as handle:
    exported = json.load(handle)
check("the export carries every turn in order",
      [message["n"] for message in exported["messages"]] == [0, 1, 2, 3, 4, 5],
      str([message["n"] for message in exported["messages"]]))
check("the export states completeness with its evidence",
      exported["metadata"]["complete"] is True
      and exported["metadata"]["turns"] == 6
      and exported["metadata"]["total_turns"] == 6
      and exported["metadata"]["turns_missing"] == [],
      str(exported["metadata"]))
check("the export names the source tool",
      exported["metadata"]["source"] == "read_conversation")
check("roles survive into the export",
      exported["messages"][0]["role"] == "user"
      and exported["messages"][1]["role"] == "assistant")
check("exporting a complete chat sets exported",
      read_state()["chats"][UUID]["status"] == "exported",
      str(read_state()["chats"][UUID]))
check("export says the chat is complete", "is complete" in result.stdout,
      result.stdout)
check("the protocol records the written file and the source state",
      read_state()["chats"][UUID]["file"] == "export.json"
      and read_state()["chats"][UUID]["exported_updated_at"] != ""
      and read_state()["chats"][UUID]["total_turns"] == 6,
      str(read_state()["chats"][UUID]))

# A partial chat must export as partial and keep its status.
PARTIAL = "partial-uuid"
run("ingest", "--raw", write("partial.txt",
                             page(uuid=PARTIAL, total=10, first=0, last=1,
                                  next_token="t2")))
partial_path = os.path.join(WORK, "partial-export.json")
result = run("export", "--chat", PARTIAL, "--out", partial_path)
check("exporting a partial chat succeeds", result.returncode == 0, result.stderr)
with open(partial_path, "r", encoding="utf-8") as handle:
    partial_doc = json.load(handle)
check("a partial export says so in the document",
      partial_doc["metadata"]["complete"] is False
      and partial_doc["metadata"]["turns_missing"] == [2, 3, 4, 5, 6, 7, 8, 9],
      str(partial_doc["metadata"]))
check("a partial export keeps the chat started",
      read_state()["chats"][PARTIAL]["status"] == "started")
check("export warns that the chat is partial", "PARTIAL" in result.stdout,
      result.stdout)
check("CLI export on a missing chat exits 1",
      run("export", "--chat", "nope").returncode == 1)


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

def section(report, name):
    """Return one section of an overview report, header line excluded."""
    import re as _re
    header = _re.search(rf"^{name}.*$", report, _re.M)
    if header is None:
        return ""
    return report[header.end():].split("\n\n")[0]


EMPTY_DIR = os.path.join(WORK, "empty-store")
result = subprocess.run(
    [sys.executable, SCRIPT, "--store-dir", EMPTY_DIR, "overview"],
    capture_output=True, text=True)
check("overview on an empty directory exits 0", result.returncode == 0,
      result.stderr)
check("overview without a state file asks the user to decide",
      "NO CRAWL STATE" in result.stdout and "fresh export" in result.stdout
      and "continuing earlier work" in result.stdout, result.stdout)

result = run("overview")
check("overview counts the statuses",
      "1 started, 1 exported" in result.stdout, result.stdout)
check("overview lists the partial chat as in progress",
      PARTIAL in section(result.stdout, "IN PROGRESS"), result.stdout)
check("overview names the token to continue with",
      "'t2'" in section(result.stdout, "IN PROGRESS"), result.stdout)
check("overview reports turns held against the total",
      "2/10 turns" in result.stdout, result.stdout)
check("overview names the missing turns",
      "missing 2-9" in result.stdout, result.stdout)
check("overview lists the exported chat for filing away",
      UUID in section(result.stdout, r"EXPORTED \(1\)"), result.stdout)
check("the handover names the state file and the started store",
      crs.STATE_FILENAME in section(result.stdout, "HANDOVER")
      and f"{PARTIAL}.json" in section(result.stdout, "HANDOVER")
      and "2 file(s) in total" in result.stdout, result.stdout)
check("a done chat does not travel to the next conversation",
      f"{UUID}.json" not in section(result.stdout, "HANDOVER"), result.stdout)

# An untouched chat with no turns must be told to start at turn 0.
run("map", "--raw", write("more.txt",
                          "<chat url='https://claude.ai/chat/fresh-1' "
                          "updated_at='2026-03-01T08:00:00Z'>Content:\n"
                          "Title: Noch ungelesen\n</chat>\n"))
result = run("overview")
check("an unread chat is told to start without a token",
      "without a page_token" in section(result.stdout, "NEXT UP"),
      section(result.stdout, "NEXT UP"))

# Working order steers the nomination and stays changeable.
run("state", "--order", "newest-first")
result = run("overview")
check("the order is reported once set",
      "Order : newest-first" in result.stdout and "never set" not in result.stdout,
      result.stdout)
result = run("state", "--chat", "fresh-1", "--status", "exported")
check("state --status corrects a status by hand",
      result.returncode == 0
      and read_state()["chats"]["fresh-1"]["status"] == "exported")
result = run("state")
check("state without an argument explains itself and exits 1",
      result.returncode == 1 and "--order" in result.stderr, result.stderr)

# ---------------------------------------------------------------------------
# Protocol convergence: stale detection and the shared schema
# ---------------------------------------------------------------------------

check("the state file is the shared protokoll.json",
      crs.STATE_FILENAME == "protokoll.json", crs.STATE_FILENAME)
check("the protocol carries the shared top-level fields",
      set(read_state()) >= {"protocol_version", "project", "order", "chats"},
      str(sorted(read_state())))
check("an entry carries every field of Vorgabe 2.4",
      set(read_state()["chats"][UUID]) == set(crs.blank_entry()),
      str(sorted(read_state()["chats"][UUID])))

# A newer timestamp in a fresh chat list marks an exported chat stale.
NEWER = ("<chat url='https://claude.ai/chat/" + UUID + "' "
         "updated_at='2026-09-01T00:00:00.000000Z'>Content:\n"
         "Title: Flattening angled parts\n</chat>\n")
newer_map = os.path.join(WORK, "neuere-liste.txt")
with open(newer_map, "w", encoding="utf-8") as handle:
    handle.write(NEWER)
run("map", "--raw", newer_map)
check("a newer listing marks the exported chat stale",
      read_state()["chats"][UUID]["status"] == "stale",
      read_state()["chats"][UUID]["status"])

# An older or equal listing must not un-stale or otherwise disturb it.
run("map", "--raw", newer_map)
check("mapping the same listing again keeps it stale",
      read_state()["chats"][UUID]["status"] == "stale")

# Reading a page of a stale chat takes it back into work.
run("ingest", "--raw", write("p1-again.txt", page(first=0, last=1)))
check("ingest takes a stale chat back to started",
      read_state()["chats"][UUID]["status"] == "started",
      read_state()["chats"][UUID]["status"])

# Export without --out names the file per Vorgabe 2.3 -- date unknown here.
run("ingest", "--raw", write("p2-again.txt", page(first=2, last=3,
                                                  next_token="t4")))
run("ingest", "--raw", write("p3-again.txt", page(first=4, last=5,
                                                  next_token="")))
AUTO_DIR = os.path.join(WORK, "autoname")
os.makedirs(AUTO_DIR, exist_ok=True)
result = subprocess.run(
    [sys.executable, SCRIPT, "--store-dir", STORE_DIR, "export",
     "--chat", UUID, "--now", "2026-09-02T00:00:00+00:00"],
    capture_output=True, text=True, cwd=AUTO_DIR)
check("export without --out writes the 2.3 name with 'ohne-datum'",
      os.path.exists(os.path.join(
          AUTO_DIR, f"ohne-datum_flattening-angled-parts_{UUID[:8]}.json")),
      str(os.listdir(AUTO_DIR)) + result.stderr)
check("the protocol notes the auto name",
      read_state()["chats"][UUID]["file"]
      == f"ohne-datum_flattening-angled-parts_{UUID[:8]}.json",
      read_state()["chats"][UUID]["file"])
check("the export records the fresh source state, clearing the stale verdict",
      read_state()["chats"][UUID]["status"] == "exported")


# A missing store file for a started chat must be asked for by name.
os.remove(crs.store_path(STORE_DIR, PARTIAL))
result = run("overview")
check("overview asks for the store file of a started chat that is absent",
      PARTIAL in section(result.stdout, "MISSING STORE FILES"), result.stdout)

shutil.rmtree(WORK, ignore_errors=True)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All checks passed.")
