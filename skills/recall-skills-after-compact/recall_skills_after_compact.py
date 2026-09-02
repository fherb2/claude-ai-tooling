#!/usr/bin/env python3
"""Recall which skills were invoked in a Claude Code session.

Two ways to run it:

* **Hook mode** (no arguments): as a SessionStart hook with matcher
  ``compact``. Reads the hook input JSON from stdin, opens the transcript
  named by its ``transcript_path`` field, and — if any skills were invoked —
  prints an English notice to stdout. Claude Code adds SessionStart stdout to
  the model's context, so the instance sees which skills had been loaded
  before the compaction and presents the list to the user. The hook never
  re-invokes anything itself.

* **On-demand mode** (transcript path as argument): invoked mid-session via
  the accompanying skill (``/recall-skills-after-compact``). Prints only the
  list; the instance is already handling the presentation.

Why this exists: after a compaction the harness re-injects invoked SKILL.md
bodies only within token caps, and lazily loaded rules files not at all. The
list closes that gap. On empty findings or any error the script stays silent
on stdout (errors go to stderr) and exits 0, so a session is never disturbed.
"""

import json
import sys


def collect_skill_calls(transcript_path):
    """Return {skill_name: (count, last_timestamp)} from the transcript."""
    calls = {}
    with open(transcript_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"Skill"' not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") != "assistant" or entry.get("isSidechain"):
                continue
            message = entry.get("message") or {}
            for block in message.get("content") or []:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "tool_use"
                    and block.get("name") == "Skill"
                ):
                    skill = (block.get("input") or {}).get("skill")
                    if not skill:
                        continue
                    count, _ = calls.get(skill, (0, ""))
                    calls[skill] = (count + 1, entry.get("timestamp") or "")
    return calls


def skill_lines(calls):
    """Format the deduplicated calls, oldest last invocation first."""
    lines = []
    for skill, (count, last) in sorted(calls.items(), key=lambda item: item[1][1]):
        when = f", last {last}" if last else ""
        lines.append(f"  - {skill} ({count}x{when})")
    return lines


def main():
    if len(sys.argv) > 1:
        transcript_path = sys.argv[1]
        on_demand = True
    else:
        on_demand = False
        try:
            hook_input = json.load(sys.stdin)
        except ValueError as err:
            print(f"recall-skills-after-compact: bad hook input: {err}", file=sys.stderr)
            return 0
        transcript_path = hook_input.get("transcript_path")
        if not transcript_path:
            print("recall-skills-after-compact: no transcript_path in hook input", file=sys.stderr)
            return 0

    try:
        calls = collect_skill_calls(transcript_path)
    except OSError as err:
        print(f"recall-skills-after-compact: cannot read transcript: {err}", file=sys.stderr)
        return 0

    if not calls:
        if on_demand:
            print("No Skill tool invocations found in this transcript.")
        return 0

    if on_demand:
        lines = ["Skills invoked in this session:"]
        lines.extend(skill_lines(calls))
    else:
        lines = [
            "[recall-skills-after-compact] A context compaction just occurred.",
            "Skills invoked earlier in this session:",
        ]
        lines.extend(skill_lines(calls))
        lines.append(
            "The harness re-injects invoked SKILL.md bodies only within token caps, "
            "and lazily loaded rules files are not re-injected at all."
        )
        lines.append(
            "Present this list to the user and let them decide which skills to "
            "re-invoke now. Do not re-invoke anything on your own."
        )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
