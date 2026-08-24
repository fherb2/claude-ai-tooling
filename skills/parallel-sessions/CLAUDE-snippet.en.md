*Last updated: 2026-08-24*

*This file is not part of the skill. It holds the silent trigger that activates the skill. When installing: copy everything below the separator line into the `CLAUDE.md` of the target location; this file stays there, only the `CLAUDE.md` is effective. Without the trigger, the skill only runs when `/parallel-sessions` is called explicitly.*

*The wording names the signs as events and additionally binds the check to an action — the first writing Git command of the session. When adapting, the anchor may be moved but not dropped. More important still than this text is the skill's `description`: it decides first whether anything triggers at all.*

---

## Parallel sessions and the worktree working model

If the user mentions a second open chat, a second Claude instance or
simultaneous work on this repository, consult the skill
`parallel-sessions` immediately. Likewise when changes appear in the
working tree that do not come from this session.

And before you execute a writing Git command for the first time in a
session (`commit`, `add`, `push`, `checkout`, `restore`, `reset`,
`merge`), check: does one of these cases apply, is this session working
inside a Git worktree, or does the file `.claude/git-worktree-model.json`
exist in the project? Then consult the skill `parallel-sessions` first.
