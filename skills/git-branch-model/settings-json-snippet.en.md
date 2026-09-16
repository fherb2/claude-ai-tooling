*Last updated: 2026-09-16*

*This file is the counterpart to the `CLAUDE-snippet.md` of the same skill — and it does not replace it but complements it: the silent trigger in the `CLAUDE.md` covers the occasions (release, creating or merging a branch, changing a central file); the hook here covers the one case in which the trigger does not fire with some models — the first writing Git command in a project with `.claude/git-branch-model.json`. **Everything below the separator line** is adopted, not into a `CLAUDE.md` but into a `settings.json`; this text above it stays behind. The file itself remains in the skill folder and shows, by its date line, which state the adopted entry is from.*

*What the hook does: before every `git commit`, `add`, `push`, `checkout`, `restore`, `reset` or `merge` Claude is about to run, it checks whether the project keeps the file `.claude/git-branch-model.json` and whether the skill `git-branch-model` has already been loaded in this session (it reads that from the session transcript Claude Code hands it). If the file is there and the skill not yet loaded, it **denies this one command** with the reason to consult the skill first — the instance then loads it and repeats the command, which passes. So the block hits at most once per session, and the sync of the management files the skill prescribes runs **before** the first write, not after it. If the skill is already loaded, the file is missing or the command is read-only, the hook stays silent. If it cannot read the transcript, it does not block but only places a notice into the context — never a block on uncertain grounds.*

*The block is built so that with the standard location `~/.claude/skills/` **nothing needs adapting**: `$HOME` is resolved by the shell that runs the hook command. If you unpacked elsewhere, replace the path with the absolute path of your script. It must stay stable afterwards — if the folder is renamed or moved, the hook breaks **silently**, because hook errors go only to the debug log.*

*Mind that `settings.json` is JSON, not prose: the block is not appended but **inserted**. If your file already has a `hooks` key, `PreToolUse` goes in as a sibling of the existing event names, not as a replacement of the whole object; if it already has a `PreToolUse` array, the entry goes in as a further element. A broken `settings.json` makes Claude Code ignore the hook silently.*

*The `if` field restricts the hook to Git commands so that it does not run on every Bash call. If your Claude Code version does not know the field, leave it out — the hook then runs on every Bash command but checks itself whether it is a writing Git command and stays silent otherwise. It then costs only one more script start per command.*

*Where: `~/.claude/settings.json` applies to all projects, `<project>/.claude/settings.json` only to that one. Without this entry the skill works only via the silent trigger and the call `/git-branch-model`; the guaranteed notice before the first writing Git command is then missing.*

*Check beforehand, without waiting for a real Git command — it catches exactly the error that otherwise stays silent. Run in the root folder of a project **with** `.claude/git-branch-model.json`; the empty transcript stands for "skill not loaded yet":*

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m probe"},"cwd":"'"$PWD"'","transcript_path":"/dev/null"}' \
  | python3 $HOME/.claude/skills/git-branch-model/notify_branch_model.py
```

*Expected: one JSON line with `"permissionDecision": "deny"` and the reason naming the skill. The same check in a folder **without** the file must print nothing. If you get "No such file or directory", the entry points into the void.*

*The real check afterwards: in a fresh session of a project with the file, have something committed. The first Git command must be refused with the hook's reason, the instance must load the skill `git-branch-model` and then repeat the command.*

---

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git *)",
            "command": "python3 $HOME/.claude/skills/git-branch-model/notify_branch_model.py"
          }
        ]
      }
    ]
  }
}
```
