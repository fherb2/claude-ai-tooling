# Rules of the `worktree` mode

This file supplements `rules.en.md` with the isolation: every session gets its workbench in its own worktree under `<worktree-dir>`, and the main checkout stays with the user. Everything from `rules.en.md` continues to hold; here is only what is added.

<!-- TEMP ISSUE-80278 ANFANG -->

## Known collision: Bash sandbox and worktrees

Before the session's first `git worktree` command runs (session start or continuing on another machine), check in two steps:

1. **Is the Bash sandbox running in this session?** Detectable from context alone, without a tool call: a system reminder describing an active sandbox policy (mentioning, among other things, "Bash tool commands run in a sandbox"), or a notice that the sandbox was just disabled ("has been disabled"), means "on"; the absence of any such notice means "off". Undocumented behavior, observed in this form on 2 September 2026 — not a `settings.json` check, which is spread across several scopes and could therefore mislead. If it is not running: skip the rest of this section, continue as normal.
2. **Only if it is running:** fetch [issue #80278](https://github.com/anthropics/claude-code/issues/80278) via WebFetch. Reason: the sandbox masks `.git/config.worktree` as soon as `git worktree` sets `extensions.worktreeConfig=true` — after that every Git command fails, including `git status`.
   - Still "open": point the user to the collision and ask whether the sandbox can be turned off now or whether the `worktree` mode is dispensable at the moment (then `workbench` or `direct`). Depending on the answer, continue or agree with the user how collisions will be ruled out.
   - No longer "open": report to the user that the fix in the issue needs analyzing and this section needs revising — and that the revised version also needs reinstalling on other machines, because the skill sits there only as a copy. Then continue as normal.

<!-- TEMP ISSUE-80278 ENDE -->

## Session start: create your own workbench

```bash
git fetch origin
# Development branch up to date? Otherwise fast-forward first:
git rev-list --count <integration>..origin/<integration>
# Any orphaned workbenches lying around? (see below)
git worktree list
# Create workbench plus worktree (location from git-workbench.json):
git worktree add <worktree-dir>/<topic> -b <workbench-prefix><topic> <integration>
```

From now on **all** file and Git work of this session happens in its own worktree — even when the session was started in the main checkout, then via absolute paths into it. After creating it, heed the worktree's then-valid CLAUDE.md.

## Report orphaned workbenches

A session ends, its worktree stays behind — nobody clears it away. Claude Code's own sweep touches only worktrees of subagents and background sessions and never the ones created with `--worktree` or by hand. So at session start check what `git worktree list` shows besides the main checkout and your own workbench, and **report every find** instead of passing over it. Two questions belong to each:

```bash
git -C <worktree> status --short          # unversioned or changed work?
git log --oneline <integration>..<branch> # unmerged commits?
```

A clean working tree does **not** mean there is nothing to save: the work then sits in the branch. If anything there is unmerged, it comes before your own work — otherwise a later workbench touches the same files, and the old work goes under in the squash. The user decides; remove worktree and branch only after their consent.

## Working in the worktree — or from the main checkout

Two ways lead into your own workbench, and they differ in what Claude Code enforces itself:

- **Via absolute paths**, while the session stays in the main checkout. Nothing is enforced; only this skill's rules apply.
- **With `EnterWorktree`** the session really moves in. The chat continues, only the transcript's storage follows the working directory. From then on Claude Code blocks every write into the main checkout, every redirect of Git into it (`git -C`, `--git-dir`, `GIT_DIR`, a preceding `cd`), and every command whose target it cannot verify — including heredocs with unquoted delimiters.

The second way is the safer one, the first the more mobile. Whoever works isolated leaves the worktree with `ExitWorktree` before the squash: the squash happens in the main checkout and would otherwise be blocked.

- No command that changes foreign worktrees, foreign branches or the main checkout.
- The safety commit covers the whole tree of the own worktree — which contains only the session's own work.

## Continuing a workbench on another machine

Git synchronizes branches, never worktree directories. Across machine boundaries therefore:

- **Before switching machines**, on the user's word: push the workbench — the first time with `git push -u origin <workbench>`, so that the upstream link exists and `git status` can report unpublished work. The push rule from `rules.en.md` applies.
- **On the other machine**: `git fetch origin`, then bind a worktree to the existing branch:

```bash
# Branch does not exist locally yet:
git worktree add --track -b <workbench> <worktree-dir>/<topic> origin/<workbench>
# Branch exists locally (earlier session on this machine) -- bind, then fast-forward:
git worktree add <worktree-dir>/<topic> <workbench>
```

## Additions to the completion

To the checklist in `rules.en.md`:

- **`ExitWorktree` before the squash** if the session sits isolated in the worktree — otherwise the main checkout is blocked.
- **The squash is explicitly addressed to the main checkout** (`git -C <main-checkout> merge --squash <workbench>`), never via the working directory of a running chain: a `cd` from an earlier link lingers, and a squash inside the workbench's own worktree merges the branch into itself — "nothing to commit", the chain breaks mid-procedure (observed four times in one day, 26 August 2026).
- **Clean up** after consent: first `git worktree remove <worktree-dir>/<topic>`, then delete the branch. No command runs with its working directory inside the worktree being removed.

## Rules that are never simplified

- Every session writes only into its own worktree. The main checkout belongs to the user; the single exception is the approved squash commit.
- Orphaned worktrees are reported, never removed silently — and never passed over silently.
