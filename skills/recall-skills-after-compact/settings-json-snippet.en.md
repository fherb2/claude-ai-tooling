*Last updated: 2026-09-02*

*This file is the counterpart to the `CLAUDE-snippet.md` of other skills: it carries the block that is adopted at its place of effect during installation — here, though, not into a `CLAUDE.md` but into a `settings.json`. What gets adopted is **everything below the separator line**; this text above it stays behind. The file itself stays in the skill folder and shows by its date line which state the adopted entry is from.*

*Two things set this block apart from a CLAUDE.md snippet, and you need to know both before using it:*

*1. **`settings.json` is JSON, not prose** — the block is not appended but **merged in**. If your file already has a `hooks` key, `SessionStart` goes in as a sibling of the existing event names, not as a replacement for the whole object. If it already has a `SessionStart` array, the entry goes in as another element. A broken `settings.json` makes Claude Code ignore the hook silently.*

*2. **The path must be adjusted** — it points to the script in the folder you unpacked the package into. With the package under `~/.claude/skills/`, the path below is correct except for `<user>`. The path must stay stable afterwards: rename the folder and the hook breaks **silently** — a hook's errors only reach the debug log.*

*Where: `~/.claude/settings.json` applies to all projects, `<project>/.claude/settings.json` only to that one. Without this entry the capability stays available by hand via `/recall-skills-after-compact`; what is missing then is the guaranteed trigger on every compaction.*

*To verify: in a session where at least one skill has been loaded, run `/compact`. The list of previously loaded skills must then appear and be presented by Claude.*

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
            "command": "python3 /home/<user>/.claude/skills/recall-skills-after-compact/recall_skills_after_compact.py"
          }
        ]
      }
    ]
  }
}
```
