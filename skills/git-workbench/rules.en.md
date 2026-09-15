# Rules of the workbench

These rules hold from now on for the whole session, in every mode. Reasons and finer points live in the README of this skill folder (`${CLAUDE_SKILL_DIR}`) — consult it when the user asks follow-up questions instead of reconstructing, and name it to them as the reference when the skill first takes effect. The file name is not reliable for this: it may have been renamed during installation. Look inside the folder; if you do not find it, answer without it.

Concrete names are defined by `.claude/git-workbench.json` (fields: `mode`, `workbench_prefix`, `worktree_dir`). The session knows the development branch from `.claude/git-branch-model.json` (field `integration_branch`) or from the user's answer; below it is called `<integration>`.

## In every mode

- **Never commit on a release branch.** If the project keeps a branching model, its name is there; otherwise whatever the user calls the release branch applies.
- **`push` only after consent in the individual case** — and the push rule (below) beforehand.
- **Command chains never rely on a lingering `cd`.** Every Git command addresses its target itself (`git -C <path>`). No command runs with its working directory inside a folder that is removed in the same go.
- **A commit covers what belongs to the step** — documentation adjustment and the associated code change in the same commit; the commit body names the step or the plan it comes from.
- **Larger restructurings only from a clean state** (no uncommitted diff), so that they can be checked and taken back via diff.

## Mode `direct`

The session commits on the branch it sits on. After every approved and executed step one commit, without asking again; it is durable and is not summarized later. There is no workbench and nothing to complete. The precondition is that nobody works in parallel in the same working tree — the user has said so by choosing this mode; do not ask about it again.

## Mode `workbench`

**Creating.** A workbench is a short-lived branch `<workbench-prefix><topic>`, derived from `<integration>` — or from the branch the user has the session work on. Propose the `<topic>` from the task, in English and short; the user confirms it (once per session). Beforehand `git fetch` and check whether the base branch is behind its remote — if so, report and stop: the user cleans that up first.

The working tree is shared: when switching to the workbench it must be clean. If unversioned work of the user is lying around, ask whether it is to be committed or stashed — never run `checkout` or `reset` over it yourself.

**An existing workbench.** If a branch with the prefix already exists, check `git log --oneline <integration>..<workbench>`. If unmerged commits lie there, settling them comes before your own work — the user decides whether they are squashed, discarded or continued. If nothing is unmerged, the workbench may be reset to the current state of `<integration>` and reused.

**Working.** After every completed and approved work step a **safety commit** on the workbench, without asking. Purpose: make a misunderstanding that surfaces only steps later correctable by a simple reset. Going back to an earlier state is allowed exclusively on the workbench, never on another branch.

**Completion — fixed checklist, in this order:**

1. **Fetch the state of the target branch:** `git fetch`; if `<integration>` has moved on, merge it into the workbench and resolve conflicts here — not only at squash time.
2. **Propose the squash**; the user determines the commit text. Switch to `<integration>` — in `workbench` via `git checkout <integration>` in the shared working tree, in `worktree` in the main checkout, explicitly addressed with `git -C <main-checkout>` —, then `git merge --squash <workbench>` and `git commit` **without `-a`**: committed is only what the squash put into the index, the user's unversioned hand work remains untouched. Show `git status` beforehand.
3. **Clean up** after consent: delete the workbench branch. For a follow-up task, derive freshly.

## Mode `worktree`

Everything from `workbench`, plus the isolation: the workbench lives in its own worktree under `<worktree-dir>`, and the main checkout stays with the user. What is added for that — creating, orphaned workbenches, working in the worktree, switching machines, the additions to the completion — is in `rules-worktree.en.md` of the same folder.

## The push rule

A push publishes one branch — and leaves all others behind. Whoever pushes a branch in the evening and continues on the other machine in the morning finds there only what was pushed.

Therefore, **before every push** the user asks for or the session proposes:

```bash
git for-each-ref --format='%(refname:short) %(upstream:short) %(upstream:track)' refs/heads
```

Every local branch that is ahead of its upstream (`[ahead n]`) or has no upstream carries unpublished work. Ask per find: "On `<branch>` there are n unpublished commits — push them too?", with yes as the proposal unless the user says otherwise. Whether a branch is still needed cannot be judged reliably; so ask instead of guessing. A branch without upstream is linked with `-u` at its first push, so that `git status` can report unpublished work from then on.

## Initial setup

Only at the user's explicit request, as a presented plan:

1. **Settle the mode** (`direct`, `workbench`, `worktree` or `ask`), the workbench prefix (absent any other instruction `claude-wb/`) and, if `worktree` ever comes into question, the storage location — absent any other instruction `.claude/worktrees/` **inside** the repository: that is where Claude Code creates its own worktrees, moving there needs no separate approval, the path derives from the repo path on every machine, and the work lies within the editor's view.
2. **Write `.claude/git-workbench.json`.** If the project keeps a branching model with centrally managed files, this file belongs to them; how it is committed then follows that model's rules.
3. **`.gitignore`**: the worktree folder must be listed there, otherwise its content shows up as unversioned in the main checkout. How the `.gitignore` is committed follows the project's branch rules.
4. **Check the silent trigger** in the CLAUDE.md of the target location.
5. **Explain**: tell the user what happens automatically from now on and what is asked, and name the README as the reference.

## Approval tiers

These tiers apply to the actions named here even where something else has been agreed elsewhere for comparable activities. Only an explicit individual instruction of the user in the chat takes precedence.

| Tier | Actions |
| --- | --- |
| **Automatic, with a report** | Reading Git commands; safety commits on the own workbench; commits in `direct` after an approved step |
| **Once per session** | The mode in `ask`; creating the own workbench (`<topic>` is proposed); naming the development branch when the project does not define it |
| **Once per project** | Initial setup; prefix and storage location |
| **Every time** | `push`; squash into the development branch; deleting branches or worktrees; every action on foreign worktrees or on the main checkout in `worktree` |

## Rules that are never simplified

- Workbench work reaches the development branch only by squash, never as a merge commit. Otherwise the safety history becomes part of the main line, and the squash discipline is void.
- The squash commit is executed without `-a`. With `-a`, the user's unversioned hand work rides into the squash.
- Resets happen only on the workbench. On no other branch is history rewritten.
- `direct` is a decision of the user, not carelessness. It is executed, not debated.
