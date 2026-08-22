#!/usr/bin/env python3
"""Inspect a claude.ai account data export (.zip) without extracting it.

The schema watchdog of this folder (implementation_doku.md 3.2, first building
block of 4.1): it answers whether an export still looks the way everything
here assumes -- before a conversion run quietly produces something wrong.
Where ``analyse`` in chat_export_convert.py describes the *interpretation* an
archive gets, this describes the raw export itself.

    python3 inspect_export.py <export.zip>

Diagnostic output only: structure and numbers, **never chat content**
(Vorgabe 2.11) -- so the output is safe to paste into a conversation.

Also lists every project in the archive by its ``created_at``: project files
are never filtered by the export's date range, so even a one-week probe
export names every project's true start date. That date bounds how far back
a real export has to reach (``chat_export_convert.py list --project-created``,
doku Vorgabe 2.4) -- no chat of a project can predate the project itself.
"""

from __future__ import annotations

import collections
import json
import sys
import zipfile
from typing import Any


def load(archive: zipfile.ZipFile, name: str) -> Any:
    """Read one JSON member of the archive."""
    with archive.open(name) as handle:
        return json.load(handle)


def message_chars(message: dict[str, Any]) -> int:
    """Characters a message carries, counting the structured blocks."""
    from_blocks = sum(len(block.get("text") or "")
                      for block in (message.get("content") or []))
    return max(len(message.get("text") or ""), from_blocks)


def conversation_chars(conversation: dict[str, Any]) -> int:
    """Characters of a whole conversation."""
    return sum(message_chars(m) for m in conversation["chat_messages"])


def is_shell(conversation: dict[str, Any]) -> bool:
    """True when messages exist but carry no text at all -- a hollowed chat."""
    return (bool(conversation["chat_messages"])
            and not any(message_chars(m) for m in conversation["chat_messages"]))


def branch_count(conversation: dict[str, Any]) -> int:
    """Number of parents with more than one child -- edited/resent messages."""
    children = collections.Counter(m.get("parent_message_uuid")
                                   for m in conversation["chat_messages"])
    return sum(1 for count in children.values() if count > 1)


def report(path: str) -> None:
    """Print the whole diagnosis for one export archive."""
    archive = zipfile.ZipFile(path)
    names = archive.namelist()
    projects = [n for n in names if n.startswith("projects/")]

    print(f"=== {path.rsplit('/', 1)[-1]}")
    print(f"    {len(names)} members: {len(projects)} project file(s), "
          f"plus {sorted(n for n in names if not n.startswith('projects/'))}")

    # ---- projects: instructions and knowledge documents ------------------
    doc_count = doc_chars = 0
    records = []
    for name in projects:
        project = load(archive, name)
        docs = project.get("docs") or []
        doc_count += len(docs)
        doc_chars += sum(len(d.get("content") or "") for d in docs)
        records.append(project)
    print(f"    projects: {len(projects)}, {doc_count} knowledge document(s), "
          f"{doc_chars} chars in them")

    # The project's created_at is the earliest any of its chats can be, so it
    # bounds every export window (doku 2.4). Project files are NOT filtered by
    # the export's date range, so even a one-week export lists them all --
    # which is what makes a cheap probe export worth running (doku 3.1.1).
    if records:
        print()
        print("=== projects by creation date -- the earliest an export must "
              "reach for each")
        for project in sorted(records, key=lambda p: p.get("created_at") or ""):
            docs = project.get("docs") or []
            print(f"    {(project.get('created_at') or '?')[:10]}  "
                  f"{len(docs):>3} doc(s)  {(project.get('name') or '')[:52]!r}")
        print("    Pass the date of the project you are migrating to "
              "chat_export_convert list --project-created.")

    if "conversations.json" not in names:
        print("    !! no conversations.json in this archive")
        return

    conversations = load(archive, "conversations.json")
    if not conversations:
        print("    !! conversations.json is empty")
        return

    messages = sum(len(c["chat_messages"]) for c in conversations)
    chars = sum(conversation_chars(c) for c in conversations)
    dates = sorted(c["created_at"][:10] for c in conversations)
    print()
    print(f"=== conversations: {len(conversations)}, {messages} messages, "
          f"{chars} chars")
    print(f"    created between {dates[0]} and {dates[-1]}")

    # ---- hollowed conversations: deleted at the source --------------------
    shells = [c for c in conversations if is_shell(c)]
    print()
    print(f"=== hollowed conversations (messages present, no text): {len(shells)}")
    for c in shells:
        files = sum(len(m.get("files") or []) for m in c["chat_messages"])
        print(f"    {c['uuid'][:8]}  created {c['created_at'][:19]}  "
              f"updated {c['updated_at'][:19]}  "
              f"{len(c['chat_messages'])} msg  {files} file ref(s)  "
              f"name={c['name']!r}")
    if shells:
        print("    A hollowed chat is a chat DELETED at the source -- verified")
        print("    in the browser, they no longer exist; nothing recovers them.")
        print("    Mass deletions share one updated_at to the second, single")
        print("    ones follow their own last message; the difference is")
        print("    unexplained and practically irrelevant (doku 3.1.3).")

    # ---- per conversation ------------------------------------------------
    print()
    print("=== per conversation (date, messages, chars, branches, name):")
    for c in sorted(conversations, key=lambda c: c["created_at"]):
        print(f"    {c['created_at'][:10]}  {len(c['chat_messages']):>4} msg  "
              f"{conversation_chars(c):>8} ch  "
              f"{branch_count(c)} branch(es)  {c['name'][:40]!r}")

    # ---- content blocks and the two kinds of uploads ----------------------
    types = collections.Counter()
    flags = collections.defaultdict(collections.Counter)
    divergent = truncated = 0
    attachments_with = attachment_chars = 0
    files_name_only = 0
    for c in conversations:
        for m in c["chat_messages"]:
            for block in (m.get("content") or []):
                types[block.get("type")] += 1
                for field in ("truncated", "cut_off", "hidden", "is_error"):
                    if field in block:
                        flags[field][repr(block[field])] += 1
                if block.get("truncated") or block.get("cut_off"):
                    truncated += 1
            joined = "".join(b.get("text") or ""
                             for b in (m.get("content") or [])
                             if b.get("type") == "text")
            if (m.get("text") or "").strip() != joined.strip():
                divergent += 1
            for entry in (m.get("attachments") or []):
                content = entry.get("extracted_content") or ""
                if content:
                    attachments_with += 1
                    attachment_chars += len(content)
                else:
                    files_name_only += 1
            files_name_only += len(m.get("files") or [])

    print()
    print("=== content blocks:", dict(types.most_common()))
    for field, values in sorted(flags.items()):
        print(f"    {field}: {dict(values)}")
    print(f"    blocks marked truncated/cut_off: {truncated}")
    print(f"    messages where 'text' != the text blocks: {divergent} of "
          f"{messages} -- 'text' alone is not a faithful rendering (it holds "
          f"the thinking)")
    print(f"    attachments WITH extracted_content: {attachments_with} "
          f"({attachment_chars} chars) -- these travel")
    print(f"    file references by name only (content NOT in the export): "
          f"{files_name_only}")

    # ---- schema watch ----------------------------------------------------
    conv_keys, msg_keys, block_keys = set(), set(), set()
    for c in conversations:
        conv_keys |= set(c.keys())
        for m in c["chat_messages"]:
            msg_keys |= set(m.keys())
            for block in (m.get("content") or []):
                block_keys |= set(block.keys())
    print()
    print("=== schema (compare against doku 3.1.1 -- a new or missing key is "
          "the early warning):")
    print("    conversation keys:", sorted(conv_keys))
    print("    message keys     :", sorted(msg_keys))
    print("    block keys       :", sorted(block_keys))
    project_fields = [k for k in conv_keys | msg_keys if "project" in k.lower()]
    print("    project reference:", project_fields or
          "NONE -- a conversation does not say which project it belongs to")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <export.zip>")
    report(sys.argv[1])
