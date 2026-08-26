---
name: parallel-sessions
description: Runs the collaboration of several Claude Code sessions working in the same repository at the same time — each session on its own workbench in its own Git worktree, central files such as the CLAUDE.md distributed via an infra branch, completion by squash merge. Use as soon as the user mentions a second open chat, a second Claude instance or simultaneous work, foreign changes appear in the working tree, a session starts inside a Git worktree, or the project has agreed on the worktree working model, or when the user calls /parallel-sessions.
license: CC0-1.0
---

# Parallel Claude sessions via Git worktrees

This file only establishes which case applies; the procedures and rules of the working model live in a rules file of the same folder and are loaded only once the model actually holds here. The split is deliberate: the skill also fires in sessions where the model has not been agreed, and then the context stays free.

## Establish the situation

First check which of the three cases applies:

1. **The project has agreed on the worktree working model** — recognizable by the file `.claude/git-worktree-model.json`; the names of branches, storage location and infra files are in that file, not in the skill. **Then read `${CLAUDE_SKILL_DIR}/rules.en.md` in full and work by it from then on.** If no file of that name is there, look in the skill folder for whichever rules file exists — it may have been renamed during installation. Until you have read it, execute no writing Git command.
2. **No model agreed, but a second session is working or has been announced.** Then the immediate rule (next section) applies, and the user is offered the initial setup of the model — briefly and without pushing, since it changes their way of working. If they want it, read the rules file as in case 1: the initial setup is in there.
3. **Neither** — a single session, no model: this skill then demands nothing, and the rules file is not loaded.

Whether the running session itself sits in a worktree is shown by `git rev-parse --git-dir --git-common-dir`: if the two paths differ, it is a worktree.

## Immediate rule without an agreed model: settle write authority

Ask the user **which session may execute writing Git commands on its own** (`commit`, `add`, `push`, `checkout`, `restore`, `reset`, `merge`). Until the answer arrives this session executes none of them; reading commands (`status`, `diff`, `log`, `fetch`) remain allowed. Authority once granted holds for the rest of the session; the user can redistribute it at any time and speaks up actively to do so.

This rule is the fallback. It is superseded by the worktree model as soon as that is set up: then nobody needs an authority any more, because no two sessions share the same working tree.
