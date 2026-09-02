*Last updated: 2026-09-02*

*This file is the counterpart to the `CLAUDE-snippet.md` of other skills: it carries the block that is adopted at its place of effect during installation — here, though, not into a `CLAUDE.md` but into a `settings.json`. What gets adopted is **everything below the separator line**; this text above it stays behind. The file itself stays in the skill folder and shows by its date line which state the adopted entry is from.*

*The block is built so that **nothing needs adjusting** for the standard location `~/.claude/skills/`: `$HOME` is resolved by the shell that runs the hook command. If you unpacked somewhere else, replace the path with the absolute path of your script. It must stay stable afterwards — rename or move the folder and the hook breaks **silently**, because a hook's errors only reach the debug log.*

*Note, because `settings.json` is JSON and not prose: the block is not appended but **merged in**. If your file already has a `hooks` key, `SessionStart` goes in as a sibling of the existing event names, not as a replacement for the whole object; if it already has a `SessionStart` array, the entry goes in as another element. A broken `settings.json` makes Claude Code ignore the hook silently.*

*Where: `~/.claude/settings.json` applies to all projects, `<project>/.claude/settings.json` only to that one. Without this entry the capability stays available by hand via `/recall-skills-after-compact`; what is missing then is the guaranteed trigger on every compaction.*

*Check it up front, without waiting for a compaction — this catches exactly the failure that would otherwise stay silent:*

```bash
python3 $HOME/.claude/skills/recall-skills-after-compact/recall_skills_after_compact.py \
  "$(ls -t ~/.claude/projects/*/*.jsonl | head -1)"
```

*A list, or the message "No Skill tool invocations found", means path and script are right. "No such file or directory" means the entry points nowhere.*

*The real test afterwards: in a session where at least one skill has been loaded, run `/compact`. The list of previously loaded skills must appear and be presented by Claude.*

---

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/.claude/skills/recall-skills-after-compact/recall_skills_after_compact.py"
          }
        ]
      }
    ]
  }
}
```
