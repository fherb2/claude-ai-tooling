*Last updated: 2026-09-15*

*This file is not part of the skill. It holds the silent trigger that activates the skill. When installing: copy everything below the separator line into the `CLAUDE.md` of the target location; this file stays there, only the `CLAUDE.md` is effective. Without the trigger, the skill only runs when `/git-workbench` is called explicitly.*

*The wording names the signs as events and additionally binds the check to an action — the first writing Git command of the session. When adapting, the anchor may be moved but not dropped. More important still than this text is the skill's `description`: it decides first whether anything triggers at all.*

---

## Commits of this session: direct, workbench or worktree

If the user mentions a second open chat, a second Claude instance or
simultaneous work on this repository, consult the skill `git-workbench`
immediately. Likewise when changes appear in the working tree that do
not come from this session, or the session starts inside a Git worktree.

And before you execute a writing Git command for the first time in a
session (`commit`, `add`, `push`, `checkout`, `restore`, `reset`,
`merge`), consult the skill `git-workbench` first: it establishes in
which mode this session commits.
