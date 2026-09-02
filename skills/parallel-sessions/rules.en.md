# Rules of the worktree working model

These rules hold from now on for the whole session. Reasons and finer points live in the README of this skill folder (`${CLAUDE_SKILL_DIR}`) — consult it when the user asks follow-up questions, instead of reconstructing. The file name is not reliable for this: it may have been renamed during installation. Look inside the folder; if you do not find it, answer without it.

<!-- TEMP ISSUE-80278 ANFANG -->

## Known collision: Bash sandbox and worktrees

Before the session's first `git worktree` command runs (session start or continuing on another machine), check in two steps:

1. **Is the Bash sandbox running in this session?** Detectable from context alone, without a tool call: a system reminder describing an active sandbox policy (mentioning, among other things, "Bash tool commands run in a sandbox"), or a notice that the sandbox was just disabled ("has been disabled"), means "on"; the absence of any such notice means "off". Undocumented behavior, observed in this form on 2 September 2026 — not a `settings.json` check, which is spread across several scopes and could therefore mislead. If it is not running: skip the rest of this section, continue as normal.
2. **Only if it is running:** fetch [issue #80278](https://github.com/anthropics/claude-code/issues/80278) via WebFetch. Reason: the sandbox masks `.git/config.worktree` as soon as `git worktree` sets `extensions.worktreeConfig=true` — after that every Git command fails, including `git status`.
   - Still "open": point the user to the collision and ask whether the sandbox can be turned off now or whether worktree mode is dispensable at the moment. Depending on the answer, continue with the worktree model or agree with the user how collisions will be ruled out.
   - No longer "open": report to the user that the fix in the issue needs analyzing and this section needs revising — and that the revised version also needs reinstalling on other machines, because the skill sits there only as a copy. Then continue as normal.

<!-- TEMP ISSUE-80278 ENDE -->

## The working model

Four branch roles, whose concrete names `.claude/git-worktree-model.json` defines (fields: `integration_branch`, `release_branch`, `workbench_prefix`, `worktree_dir`, `infra_branch`, `infra_files`):

- **Release branch** (say, `master`): finished work only. Not a place to work in.
- **Integration branch** (say, `dev`): carries everything under development. The user's main checkout sits on it; it is **their** working area — Claude writes no files there and commits there only the approved squash (see completion).
- **Workbenches** (say, `claude-wb/<topic>`): one per simultaneous session, derived from the integration branch, each in its own worktree. Short-lived: after the squash merge it is discarded.
- **Infra branch** (say, `infra`): an orphan branch carrying exclusively the central files (`infra_files`: the project's CLAUDE.md, editor and tool configuration, `.gitignore` …). It is **never merged**; distribution happens via `git restore --source=<infra> -- <infra-files>`, which every session runs itself in its own worktree.

### Session start: create your own workbench

```bash
git fetch origin
# Integration branch up to date? Otherwise fast-forward first:
git rev-list --count <integration>..origin/<integration>
# Any orphaned workbenches lying around? (see below)
git worktree list
# Create workbench plus worktree (location from git-worktree-model.json):
git worktree add <worktree-dir>/<topic> -b <workbench-prefix><topic> <integration>
```

Propose the `<topic>` from the task — in English and short; the user confirms it (approval tiers below). From now on **all** file and Git work of this session happens in its own worktree — even when the session was started in the main checkout, then via absolute paths into it.

Immediately after creating it — and equally at the start of every later session on an already existing workbench — the **infra sync**:

```bash
git -C <worktree> restore --source=<infra> -- <infra-files>
```

If it changes anything, report that to the user in one sentence; the changes ride along with the next checkpoint commit. After the sync, heed the session's then-valid CLAUDE.md.

### Report orphaned workbenches

A session ends, its worktree stays behind — nobody clears it away. Claude Code's own sweep touches only worktrees of subagents and background sessions and never the ones created with `--worktree` or by hand. So at session start check what `git worktree list` shows besides the main checkout and your own workbench, and **report every find** instead of passing over it. Two questions belong to each:

```bash
git -C <worktree> status --short          # unversioned or changed work?
git log --oneline <integration>..<branch> # unmerged commits?
```

A clean working tree does **not** mean there is nothing to save: the work then sits in the branch. If anything there is unmerged, it comes before your own work — otherwise a later workbench touches the same files and the old work goes under in the squash. The user decides; remove worktree and branch only after their consent.

### Working in the worktree — or from the main checkout

Two ways lead into your own workbench, and they differ in what Claude Code enforces itself:

- **Via absolute paths**, while the session stays in the main checkout. Nothing is enforced; only this skill's rules apply.
- **With `EnterWorktree`** the session really moves in. The chat continues, only the transcript's storage follows the working directory. From then on Claude Code blocks every write into the main checkout, every redirect of Git into it (`git -C`, `--git-dir`, `GIT_DIR`, a preceding `cd`), and every command whose target it cannot verify — including heredocs with unquoted delimiters.

The second way is the safer one, the first the more mobile. Whoever works isolated leaves the worktree with `ExitWorktree` before the squash merge: the merge happens in the main checkout and would otherwise be blocked.

### Continuing a workbench on another machine

Git synchronizes branches, never worktree directories. Across machine boundaries therefore:

- **Before switching machines**, on the user's word: push the workbench — the first time with `git push -u origin <workbench>`, so that the upstream link exists and `git status` can report unpublished work.
- **On the other machine**: `git fetch origin`, then bind a worktree to the existing branch:

```bash
# Branch does not exist locally yet:
git worktree add --track -b <workbench> <worktree-dir>/<topic> origin/<workbench>
# Branch exists locally (earlier session on this machine) — bind, then fast-forward:
git worktree add <worktree-dir>/<topic> <workbench>
```

- Then as at every session start: infra sync, continue working.

### Working on the workbench

- After every completed work step a **checkpoint commit** in the own worktree, without asking. It covers the whole tree of the worktree — which contains only the session's own work.
- No command that changes foreign worktrees, foreign branches or the main checkout.
- **Command chains never rely on a lingering `cd`.** Every Git command addresses its target itself — `git -C <worktree>` for the workbench, `git -C <main-checkout>` for the squash. And no command runs with its working directory inside a worktree that is removed in the same go.
- `push` of the workbench only after consent in the individual case.

### Changing central files (infra)

Durable changes to infra files happen **exclusively on the infra branch** — never as a workbench commit. Procedure, each time with the user's consent:

```bash
git worktree add <worktree-dir>/_infra <infra>   # temporary worktree
# make the change there, commit
git worktree remove <worktree-dir>/_infra
git -C <worktree> restore --source=<infra> -- <infra-files>
```

Then report to the user: other **running** sessions pick the change up only at their next infra sync — whoever needs it immediately triggers the sync there.

### Trying out infra changes (experiments)

If a central change is to be tried out first, before it goes onto the infra branch — a new rule paragraph in the CLAUDE.md, a hook in the settings, a changed linter configuration —, the workbench may change its copy of the infra file for that. Conditions:

- The changed block is enclosed in the marks `<!-- INFRA-EXPERIMENT ANFANG <workbench> <date> -->` and `<!-- INFRA-EXPERIMENT ENDE -->`.
- The experiment always ends through the infra sync (one command, see above) — never by editing back by hand, and the experimental version is **never** merged.
- If the rule proves itself, it is entered anew, without marks, on the infra branch (previous section).
- If an infra sync in between brings new central changes, re-insert the marked block afterwards.

### Completing a task

Fixed checklist, in this order:

1. **Infra sync**: `git diff <infra> -- <infra-files>` must be empty; otherwise `restore` — which also ends every experiment.
2. **Experiment search**: `grep -rn "INFRA-EXPERIMENT" <worktree>` must be empty.
3. **Fetch the integration state**: `git fetch`; if the integration branch has moved on, merge it into the workbench and resolve conflicts here — not only at squash time.
4. **Propose the squash merge**; the user determines the commit text. If the session sits isolated in the worktree, `ExitWorktree` first — otherwise the main checkout is blocked. Execution in the main checkout on the integration branch, **explicitly addressed there** (`git -C <main-checkout>`), never via the working directory of a running chain — a `cd` from an earlier link lingers, and a squash inside the workbench's own worktree merges the branch into itself: "nothing to commit", the chain breaks mid-procedure (observed four times in one day, 26 August 2026). So: `git -C <main-checkout> merge --squash <workbench>`, then there `git commit` **without `-a`** — committed is only what the squash put into the index, the user's unversioned hand work remains untouched. Show `git status` beforehand.
5. **Clean up** after consent: remove the worktree (`git worktree remove`), delete the workbench branch. For a follow-up task, derive freshly from the integration branch.

### Initial setup of the model

Only at the user's explicit request, as a presented plan. Steps: settle the names (integration, release and infra branch, workbench prefix, storage location — as the storage location, absent any other instruction, `.claude/worktrees/` **inside** the repository is proposed: that is where Claude Code creates its own worktrees, moving there with `EnterWorktree` needs no separate approval, the path derives from the repo path on every machine, and above all the worktree then lies inside the folder the user's editor has open — outside it they cannot see the work. The folder belongs in the `.gitignore`, otherwise its content shows up as unversioned in the main checkout) and fix the infra file list; create the integration branch if it does not exist; create the infra branch as an orphan (`git worktree add --orphan -b <infra> <tmp>`, requires Git >= 2.42) and take the infra files over via `git checkout <integration> -- <file…>`; write `.claude/git-worktree-model.json` with the fields above; check this skill's silent trigger in the project CLAUDE.md — which afterwards lives on the infra branch itself.

## Approval tiers

These tiers apply to the actions named here even where something else has been agreed elsewhere for comparable activities. Only an explicit individual instruction of the user in the chat takes precedence.

| Tier | Actions |
| --- | --- |
| **Automatic, with a report** | Reading Git commands; infra sync in the own worktree (session start and completion step 1); checkpoint commits on the own workbench; experiment search |
| **Once per session** | Creating the own workbench plus worktree (`<topic>` is proposed) |
| **Once per project** | Initial setup of the model; storage location of the worktrees; the infra file list and every later change to it |
| **Every time** | `push`; every commit on the infra branch; squash merge into the integration branch; deleting branches or worktrees; every action touching foreign worktrees or the main checkout |

## Rules that are never simplified

- No durable change to infra files outside the infra branch. Workbench changes to them are experiments: marked, mortal, never merged.
- The infra branch is never merged and derived from no other branch. Distribution exclusively via `restore --source`.
- Every session writes only into its own worktree. The main checkout belongs to the user; the single exception is the approved squash commit.
- Workbench work reaches the integration branch only by squash, never as a merge commit.
