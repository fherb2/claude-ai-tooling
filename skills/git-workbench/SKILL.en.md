---
name: git-workbench
description: Governs how a Claude session commits in a Git repository — directly on the current branch, on a workbench of its own with safety commits and a squash at the end, or isolated in its own Git worktree when several sessions work at the same time. Use before the first writing Git command of a session, as soon as the user mentions a second open chat or a second Claude instance, foreign changes appear in the working tree, or the session starts inside a Git worktree, or when the user calls /git-workbench.
license: CC0-1.0
---

# How this session commits

This file only establishes the mode; the procedures and rules live in rules files of the same folder and are loaded only once it is clear what is needed. The split is deliberate: the machinery for parallel sessions costs no context in the other modes.

## Determine the mode

Read `.claude/git-workbench.json`, field `mode`. If the file or the field is missing, `ask` applies.

| `mode` | Meaning |
| --- | --- |
| `direct` | Commits directly on the branch the session sits on; every approved step one durable commit. A valid mode, not a deviation — it is not called into question again. |
| `workbench` | A workbench of its own (a short-lived branch) with safety commits, at the end a squash into human granularity. |
| `worktree` | Like `workbench`, but in its own worktree — for several sessions at the same time. |
| `ask` | You ask — once per session, at the first writing Git command. |

**With `ask`:** Name the branch the session sits on and the situation: is the session inside a worktree (`git rev-parse --git-dir --git-common-dir` — two different paths mean yes)? Has a second session been mentioned, do foreign changes appear? From that, propose a mode and ask. The answer holds for the session. If the session already sits inside a worktree, the mode is `worktree`, without asking.

**A second session without isolation.** If a second session is involved and the mode is not `worktree`, the immediate rule applies first: ask the user **which session may execute writing Git commands on its own** (`commit`, `add`, `push`, `checkout`, `restore`, `reset`, `merge`). Until the answer arrives this session executes none of them; reading commands (`status`, `diff`, `log`, `fetch`) remain allowed. Authority once granted holds for the rest of the session. Offer `worktree` — briefly, without pushing —, because then nobody needs an authority any more: no two sessions share the same working tree then.

## Know the development branch

Workbench and squash need a target branch. If the project keeps the file `.claude/git-branch-model.json`, it is there in the field `integration_branch`. Otherwise ask the user once per session — with the currently checked-out branch as a proposal, not as an assumption. Store the value nowhere.

## Load the rules

- In every mode, as soon as a writing Git command is imminent: **read `${CLAUDE_SKILL_DIR}/rules.en.md` in full** and work by it from then on.
- In `worktree` additionally **`rules-worktree.en.md`** from the same folder — before the first `git worktree` command.

If no file of that name is there, look in the skill folder for whichever rules files exist — they may have been renamed during installation. Until you have read them, execute no writing Git command.

## Explain, do not presume

When this skill takes effect in a project for the first time — at the first question in `ask`, when creating the first workbench, at the initial setup — say in a few sentences what you are about to do and why. The user may simply have installed the skill and be watching what happens. For everything beyond that, the README lies in this skill's folder: name it as the reference and quote from it when asked, instead of reconstructing. Its file name is not reliable — look in the folder; if you do not find it, answer without it.
