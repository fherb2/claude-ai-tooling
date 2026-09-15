*Last updated: 2026-09-15*

*This file is not part of the skill. It holds the silent trigger that activates the skill. When installing: copy everything below the separator line into the `CLAUDE.md` of the target location; this file stays there, only the `CLAUDE.md` is effective. Without the trigger, the skill only runs when `/git-branch-model` is called explicitly.*

*The wording names the occasions as events and additionally binds the check to an action — the first writing Git command of the session. When adapting, the anchor may be moved but not dropped. More important still than this text is the skill's `description`: it decides first whether anything triggers at all.*

---

## Branching model of the project

If the user wants to bring something into the release, create or merge a
branch, or change a central file of the project (the project CLAUDE.md,
editor or tool configuration, `.gitignore`), consult the skill
`git-branch-model` first.

And before you execute a writing Git command for the first time in a
session (`commit`, `add`, `push`, `checkout`, `restore`, `reset`,
`merge`), check: does the file `.claude/git-branch-model.json` exist in
the project? Then consult the skill `git-branch-model` first.
