#!/usr/bin/env python3
"""Make sure git-branch-model is consulted before the first writing Git command.

PreToolUse hook, matcher "Bash", if "Bash(git *)". Reads the hook input JSON
from stdin. It acts only if tool_input.command names a writing Git
subcommand (commit, add, push, checkout, restore, reset, merge -- the same
list the CLAUDE.md trigger anchors on) AND the project, found by walking up
from cwd, keeps .claude/git-branch-model.json. Then:

* If the session transcript (hook input field transcript_path) shows that
  the skill git-branch-model has already been loaded in this session --
  either via the Skill tool or via the slash command -- the hook stays
  silent and the command runs.
* Otherwise it DENIES this one command (permissionDecision "deny") with the
  reason that git-branch-model is to be consulted first. Once the skill is
  loaded, the transcript shows it, and the next attempt passes. So the
  block happens at most once per session, and the sync of the management
  files that the skill prescribes runs BEFORE the first write, not after it.
* If the transcript cannot be read, it falls back to a plain notice
  (additionalContext) instead of blocking: never block on missing evidence.

Why a hook at all: measured on 16 September 2026, Sonnet loads at the anchor
"first writing Git command" only the skill whose description literally
matches the request and skips the second trigger condition. A PreToolUse
hook is deterministic where a CLAUDE.md trigger is not. Why deny instead of
notice: additionalContext does not stop the command, so the skill would be
consulted only after the first write.

The hook never runs the sync itself and never blocks a read-only command.
On any error or non-match it stays silent (no stdout) and exits 0.
"""

import json
import os
import re
import sys

# "git" must stand at a command position -- start of the line, or after a
# separator such as &&, ||, ;, | or $( -- optionally preceded by variable
# assignments or "env"/"command", and the subcommand must be the first bare
# word after git's own options (-C <path>, -c <k=v>, --git-dir=...). A "git"
# inside a quoted string or a name like git-branch-model does not count:
# the first live version matched those and blocked a command that merely
# mentioned the skill (16 September 2026).
WRITE_SUBCOMMANDS = re.compile(
    r"(?:^|[;&|(]|\$\()\s*"
    r"(?:\S+=\S*\s+)*(?:env\s+|command\s+)?"
    r"git\s+"
    r"(?:(?:-C|-c|--git-dir|--work-tree)\s+\S+\s+|--?[\w-]+(?:=\S+)?\s+)*"
    r"(commit|add|push|checkout|restore|reset|merge)\b",
    re.M,
)
SKILL = "git-branch-model"


def find_project_root(start):
    """Walk upward from start looking for the folder holding .claude/git-branch-model.json."""
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, ".claude", SKILL + ".json")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def skill_already_loaded(transcript_path):
    """True if the transcript shows the skill loaded in this session.

    Two traces count: a Skill tool_use with this skill's name (the instance
    loaded it), or a message carrying the skill body header with this skill's
    folder (the user called it via slash command). Sidechain entries of
    subagents are ignored. Raises OSError if the file cannot be read.
    """
    marker = f"Base directory for this skill: "
    with open(transcript_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if SKILL not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("isSidechain"):
                continue
            message = entry.get("message") or {}
            for block in message.get("content") or []:
                if not isinstance(block, dict):
                    continue
                if (
                    block.get("type") == "tool_use"
                    and block.get("name") == "Skill"
                    and (block.get("input") or {}).get("skill") == SKILL
                ):
                    return True
                text = block.get("text") if block.get("type") == "text" else None
                if text and marker in text and text.split(marker, 1)[1].split("\n", 1)[0].rstrip("/").endswith("/" + SKILL):
                    return True
    return False


def emit(decision=None, reason=None, context=None):
    out = {"hookEventName": "PreToolUse"}
    if decision:
        out["permissionDecision"] = decision
        out["permissionDecisionReason"] = reason
    if context:
        out["additionalContext"] = context
    print(json.dumps({"hookSpecificOutput": out}))


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

    if find_project_root(hook_input.get("cwd") or ".") is None:
        return 0

    notice = (
        f"[{SKILL}] This project keeps .claude/{SKILL}.json. "
        f"Consult the skill {SKILL} before running writing Git commands."
    )

    transcript_path = hook_input.get("transcript_path")
    if not transcript_path:
        emit(context=notice)
        return 0
    try:
        loaded = skill_already_loaded(transcript_path)
    except OSError as err:
        print(f"{SKILL} hook: cannot read transcript: {err}", file=sys.stderr)
        emit(context=notice)
        return 0

    if loaded:
        return 0

    emit(
        decision="deny",
        reason=(
            f"[{SKILL}] This project keeps .claude/{SKILL}.json, and the skill "
            f"{SKILL} has not been consulted in this session yet. Consult it first "
            f"(Skill tool: {SKILL}), then run this command again. This block "
            f"happens once per session."
        ),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
