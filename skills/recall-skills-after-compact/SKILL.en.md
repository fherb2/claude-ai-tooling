---
name: recall-skills-after-compact
description: Lists on demand which skills have already been loaded via the Skill tool in the running session — the same script the accompanying SessionStart hook runs automatically after every context compaction. Invoked by the user with /recall-skills-after-compact.
disable-model-invocation: true
license: CC0-1.0
---

# List the skills loaded in this session

Run this folder's script with the transcript path of the running session and present the result to the user. Do not reload any skill on your own — the decision is the user's.

**Determine the transcript path like this** (layout documented in the sessions docs): `~/.claude/projects/<project>/<session-id>.jsonl`, where `<project>` is the working directory path with `-` in place of all non-alphanumeric characters. If you know your session ID — it shows up in the scratchpad path, for instance — take the file of that name. Otherwise take the most recently modified `.jsonl` in the folder: the running session grows with every turn, so its file is practically always the newest.

```bash
python3 "${CLAUDE_SKILL_DIR}/recall_skills_after_compact.py" <transcript-path>
```

If the script reports "No Skill tool invocations found", no skills have been invoked via the Skill tool in this session so far — say so, rather than interpreting it. Only real Skill tool invocations of the main conversation are counted; rules that entered the context another way (say, a file loaded directly via Read) are not covered by the list.
