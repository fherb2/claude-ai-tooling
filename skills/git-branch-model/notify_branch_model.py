#!/usr/bin/env python3
"""Notify the instance about the git-branch-model skill before a writing Git command.

PreToolUse hook, matcher "Bash", if "Bash(git *)". Reads the hook input JSON
from stdin; if tool_input.command names a writing Git subcommand (commit, add,
push, checkout, restore, reset, merge -- the same list the CLAUDE.md trigger
anchors on) AND the project (found by walking up
from cwd) keeps .claude/git-branch-model.json, prints a PreToolUse JSON
output whose hookSpecificOutput.additionalContext names the skill. Plain
stdout is NOT added to Claude's context for PreToolUse (unlike SessionStart)
-- only additionalContext is, per https://code.claude.com/docs/en/hooks.

The hook never blocks and never runs the sync itself: it only guarantees the
notice arrives, the way an event-anchored CLAUDE.md trigger can fail to at
the Description-selection step (measured 16 September 2026: Sonnet loads
only the skill whose description literally matches the request and skips
the second trigger condition). The instance still decides whether and how
to consult the skill.

On any error or non-match it stays silent (no stdout) and exits 0, so a
session is never disturbed.
"""

import json
import os
import re
import sys

WRITE_SUBCOMMANDS = re.compile(
    r"\bgit\b[^&|;]*\b(commit|add|push|checkout|restore|reset|merge)\b"
)


def find_project_root(start):
    """Walk upward from start looking for .claude/git-branch-model.json's project root."""
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, ".claude", "git-branch-model.json")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def main():
    try:
        hook_input = json.load(sys.stdin)
    except ValueError:
        return 0

    if hook_input.get("tool_name") != "Bash":
        return 0

    command = (hook_input.get("tool_input") or {}).get("command") or ""
    if not WRITE_SUBCOMMANDS.search(command):
        return 0

    cwd = hook_input.get("cwd") or "."
    root = find_project_root(cwd)
    if root is None:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "[git-branch-model] This project keeps .claude/git-branch-model.json. "
                "Before running this writing Git command, consult the skill "
                "git-branch-model."
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
