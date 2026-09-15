# Rules of the branching model

These rules hold from now on for the whole session. Reasons and finer points live in the README of this skill folder (`${CLAUDE_SKILL_DIR}`) — consult it when the user asks follow-up questions instead of reconstructing, and name it to them as the reference when the skill first takes effect. The file name is not reliable for this: it may have been renamed during installation. Look inside the folder; if you do not find it, answer without it.

## The four roles

Concrete names are defined by `.claude/git-branch-model.json` (fields: `integration_branch`, `release_branch`, `release_transfer`, `management_branch`, `management_files`).

| Role | Field | What happens there |
| --- | --- | --- |
| **Development branch** (say, `dev`) | `integration_branch` | The main line of development. Carries everything in progress; every commit is kept. |
| **Release branch** (say, `master`) | `release_branch` | The published state. Not a place to work: nothing is changed there, things are only transferred there. |
| **Topic branches** (named freely) | — | One per task, branched off the development branch and merged back into it. Their commits are kept. |
| **Management branch** (say, `repo-management`) | `management_branch`, `management_files` | An orphan branch with no common ancestry with the others. Carries exclusively the management files: what must be identical on every branch. Never merged — its files are laid over every other branch. |

**The boundary between human and machine granularity.** Commits a human has made keep their granularity: a topic branch is merged, its history stays. Safety commits of a machine — intermediate states of a session that exist only to allow going back — do not belong in this history; they are brought to the granularity a human would have chosen before they reach the development branch. How a session does that is its own business; this model only demands that it does.

## The development branch and its topic branches

- The development branch is the place of work. The user's main checkout normally sits on it.
- A delimited task — an issue, a topic — may get its own branch. It branches off the development branch and returns by merge (`git merge`, without `--squash`); whether with a merge commit or as fast-forward is the user's decision. Before the merge, fetch the state of the development branch and resolve conflicts on the topic branch.
- Whoever creates a topic branch names it after the task, in English and short. This model prescribes no prefix.

## Release transfer

When something is transferred to the release branch is the user's decision; the transfer itself requires approval every time. How it happens is defined by `release_transfer` — and the two values exclude each other:

**`merge` — one product.** The development branch is merged into the release branch, without `--squash`; the history stays continuous. Beforehand: sync of the management files (below) on the development branch, `git fetch`, and no unpublished state the merge would pass over.

**`file-sync` — several products.** If only part of the development state is published at a time, a merge is impossible: it takes all or nothing, and after a first partial transfer every later merge would reckon with a merge base that never described the state. Therefore:

- The two branches have **separate histories**. Transfer happens file by file; "every commit is kept" holds within the development branch, not across the boundary to the release branch.
- The release branch is **never checked out**. Its tree can be advanced at the object level (`read-tree`/`update-index`/`write-tree`/`commit-tree`/`update-ref` with an alternative index file) without touching the working tree.
- **Management files never come from the development branch** but always from the management branch — onto both branches alike.
- What is meant to be absent from the release branch (unfinished work, development tooling) is a decision of the project. The worked-out transfer recipe with its exclusion list and cross-check therefore belongs to the project, not to this skill; this skill names only the invariants.

## The management branch

### What belongs on it

Everything that must be identical on **every** branch — and only that. The criterion is not "is it configuration" but "must it be the same everywhere":

- **Configuration**: the project CLAUDE.md, editor and linter settings, `.gitignore`, the configuration files of this and related models.
- **Tooling with logic of its own**, provided it is branch-independent: a project skill needed alike on every branch, a CI configuration.
- **Not**: a tool needed only on the development branch. Distribution would put it onto the release branch too.

The list is in `management_files`; it changes only with the user's consent.

### Distribution: overlaying instead of merging

The management branch is **never** merged and derived from **no** other branch. Its files are fetched:

```bash
git restore --source=<management> -- <management-files>
```

This writes the management branch's version into the working tree the session works in; the change rides along with the next commit on that branch. For every management file there is exactly one valid version — the one on the management branch — and overwriting is always the right resolution. **Under one condition:** the local version is outdated, not new. That is exactly what the sync checks.

### The sync with direction check

**When:** before the first writing Git command of a session, and before every release transfer. The sync runs in the working tree the session works in.

**Step 1 — Does anything differ?**

```bash
git diff --name-only <management> -- <management-files>
```

Empty: nothing to do. Otherwise step 2 for every file named.

**Step 2 — In which direction?** The local version is either an earlier state of the management branch (then it is **outdated**) or it contains something that never was there (then it is **new**):

```bash
BLOB=$(git hash-object <file>)                        # version in the working tree
git log --oneline --find-object=$BLOB <management>    # did this content ever exist on the management branch?
```

- **Output not empty → outdated.** Run `git restore --source=<management> -- <file>` and report to the user in one sentence. Likewise for a file that is missing locally but exists on the management branch.
- **Output empty → new.** Stop and do not overwrite: someone changed the file outside the management branch, and `restore` would destroy that work. Show the user the difference (`git diff <management> -- <file>`) and propose the way to bring the change onto the management branch (next section). Likewise for a file that is in the list locally but missing on the management branch.
- **A marked experiment** (below) is an intended deviation in the "new" direction: do not overwrite, do not report — except before the release transfer, where it ends.

`--find-object` needs Git ≥ 2.16.

### Changing management files

Durable changes to management files happen **exclusively on the management branch**. Because it is orphan and carries only a few files, it is not checked out in the main checkout — that would empty the working tree — but in a temporary worktree. Every commit there requires approval.

**Small change:**

```bash
git worktree add <tmp> <management>        # temporary worktree
# make the change there, commit
git worktree remove <tmp>
git restore --source=<management> -- <management-files>   # in your own working tree
```

**Larger or iterative work** — a skill, a hook, anything needing several attempts — on a **working branch that branches off the management branch** and returns into it by squash. That does not violate the invariant: "derived from no other branch, never merged" means the traffic with development and release branch. A branch that comes from the management branch contains only management files, and its return by squash keeps the management branch's history clean. How a session runs its working branches is its own business.

Afterwards report to the user: other **running** sessions and other branches pick the change up only at their next sync.

<!-- TEMP ISSUE-80278 ANFANG -->
If a Bash sandbox is running in the session, `git worktree add` can fail on a known collision after which even `git status` fails ([issue #80278](https://github.com/anthropics/claude-code/issues/80278)). Whether the sandbox is running is shown by the context alone: a system reminder describing an active sandbox policy means "on". Then, before the first `git worktree` command, ask the user whether the sandbox can be switched off briefly, or leave the change on the management branch to them.
<!-- TEMP ISSUE-80278 ENDE -->

### Experiments

If a central change is to be tried out first, before it goes onto the management branch — a new rule paragraph in the CLAUDE.md, a hook in the settings —, its copy in your own working tree may be changed for that. Conditions:

- The changed block is enclosed in `<!-- MANAGEMENT-EXPERIMENT ANFANG <branch> <date> -->` and `<!-- MANAGEMENT-EXPERIMENT ENDE -->`.
- The experiment ends through the sync, never by editing back by hand — and the experimental version is **never** merged and **never** transferred to the release. Before every release transfer, `grep -rn "MANAGEMENT-EXPERIMENT"` must be empty.
- If the rule proves itself, it is entered anew, without marks, on the management branch.
- If a sync in between brings new central changes, re-insert the marked block afterwards.

## Initial setup of the model

Only at the user's explicit request, as a presented plan. Steps:

1. **Settle names and kind**: development branch, release branch, management branch, `release_transfer` (one product → `merge`, several → `file-sync`), the list of management files. For the management branch choose a name that says what lies on it — not `infra`: in IT that word is taken for deployment.
2. **Create the development branch** if it does not exist; the main checkout moves there.
3. **Create the management branch as an orphan** (`git worktree add --orphan -b <management> <tmp>`, Git ≥ 2.42), take the management files over from the development branch (`git checkout <integration> -- <file…>` in the orphan worktree), commit, remove the worktree, push with `-u`.
4. **Write `.claude/git-branch-model.json`** — and include it in `management_files` itself: it must be identical on every branch.
5. **Check the silent trigger** in the CLAUDE.md of the target location. If the project CLAUDE.md lives on the management branch, the change happens there.
6. **Explain**: tell the user what happens automatically from now on (the sync in the "outdated" direction) and what is asked every time, and name the README as the reference.

## Approval tiers

These tiers apply to the actions named here even where something else has been agreed elsewhere for comparable activities. Only an explicit individual instruction of the user in the chat takes precedence.

| Tier | Actions |
| --- | --- |
| **Automatic, with a report** | Reading Git commands; sync in the "outdated" direction; experiment search |
| **After asking** | Sync in the "new" direction — the way is proposed, not executed |
| **Once per project** | Initial setup; the list of management files and every later change to it |
| **Every time** | `push`; every commit on the management branch; every release transfer; creating and deleting branches; merging a topic branch |

## Rules that are never simplified

- No durable change to management files outside the management branch. Local changes to them are experiments: marked, mortal, never merged.
- The management branch is never merged into another branch and derived from no other branch. Distribution exclusively via `restore --source`.
- The sync overwrites only what is outdated. What is new is reported.
- The release branch is not a place to work. In the `file-sync` mode it is never checked out and never merged.
- Safety commits of a machine reach the development branch only in human granularity.
