# parallel-sessions — several Claude sessions at the same time in the same repository, cleanly separated via Git worktrees

*Last updated: 2026-08-25*

*[Deutsche Fassung](README.md)*

**✅☑ Finished and usable.** Instructions complete, frontmatter set, silent trigger present; German and English versions available.

**Gives every simultaneously working Claude session its own Git worktree with its own workbench, and thereby makes the question of which session may commit obsolete.** Two sessions in the same working tree overwrite each other silently — the treacherous part is not the conflict, which Git would report, but the unnoticed riding-along of foreign intermediate states. The skill separates the sessions physically: one worktree per session, inside it a short-lived workbench derived from the integration branch, completion by squash merge. Central files that must be current everywhere (the project CLAUDE.md, editor configuration, `.gitignore`) live on a dedicated orphan **infra branch** and are not merged but fetched by every session into its own worktree via `git restore --source`. For projects without this model the skill contains the old immediate rule as a fallback: first settle Git write authority, then work.

**Scope:** The skill applies only to Claude Code working locally on a Git repository, not to claude.ai. It governs the collaboration of the sessions, not a project's release procedure (when something moves from the integration to the release branch); on that it says nothing.

## Installation

1. **Choose the target location.** The skill applies either to all of the user's projects or to a single one:

   | Location | Path                                  | Applies to                 |
   | -------- | -------------------------------------- | -------------------------- |
   | Personal | `~/.claude/skills/parallel-sessions/` | all of the user's projects |
   | Project  | `.claude/skills/parallel-sessions/`   | this project only          |

2. **Copy one language version of the folder `parallel-sessions/`.** It holds `SKILL.de.md`/`SKILL.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`, this `README.en.md` and the German `README.md`; all files of the chosen language come along. The chosen SKILL version is called `SKILL.md` at the target location — whether renamed or additionally placed makes no difference; Claude Code recognizes that name and no other. The date lines of README and snippet show at the target location which state the installation is from.

3. **Adopt the silent trigger.** The content of the `CLAUDE-snippet` file matching the chosen language, **below the separator line**, goes into the `CLAUDE.md` of the target location; the snippet files stay at the target location, only the `CLAUDE.md` is effective. Without this step the skill does not notice the situation: nobody says of their own accord "a second instance is working here right now".

4. **Set up per project.** The worktree model does not take effect through the installation but through the initial setup in the project (branches, infra file list, the file `.claude/git-worktree-model.json`). It happens in the chat, at the user's request; the skill leads through the steps. Without it only the fallback applies.

The `README.md` belongs at the target location too: the `SKILL.md` points to it for all reasoning, and Claude consults it when the user asks follow-up questions. If it is missing there, the skill still works — answers to why-questions just come out thinner. Its presence is not checked.

## Details

**Why an orphan infra branch with `restore` instead of a merge flow.** Completing a workbench is a squash merge, and squashes erase ancestry: were the central change distributed into the workbenches by merge and the workbench squashed afterwards, the integration branch would know nothing of the common origin — the next merge of the same infra state would reckon with an outdated merge base and produce conflicts in files that never held a real conflict. `git restore --source=<infra>` bypasses ancestry entirely: for every infra file there is exactly one valid version (the one on the infra branch), and overwriting is always the correct resolution. That is precisely why the rule "no durable change to infra files outside the infra branch" is not tidiness but the condition under which the procedure is conflict-free.

**Why distribution is pull-based.** The infra branch pushes nothing into the workbenches; every session fetches the state itself — automatically at session start and in the first step of the completion checklist. That turns temporary deviation into an intended state instead of an error: an experiment — a central change that one session is to try out first, before it holds for everyone, say a new trigger paragraph in the CLAUDE.md or a hook in the settings — is simply a sync not yet run plus a marked local change. It is ended by that same sync — one command, no editing back. All of this is possible in the first place only because of the worktrees: Claude loads the project CLAUDE.md from the worktree of the respective session; in a shared working tree all sessions would see every test rule.

**Why a dedicated file `git-worktree-model.json` instead of a block in a shared agreements file.** A shared file would need coexistence rules — whose key belongs to whom, who never touches what —, and those rules would have to stand as permanent text in every skill that co-uses the file: context costs in every turn, only to manage an avoidable problem. The dedicated file solves this by existence instead of by rules; its presence is at the same time the sign that the model has been agreed in the project. Side effect: the skill is portable, because in foreign projects it presupposes no existing agreements file. The `git-` prefix in the name lowers the risk of a collision with future engine files in `.claude/` and is honest about the content: without Git — worktrees, branches, `restore` — nothing of the method would remain.

**Work across several machines.** Git synchronizes branches, never worktree directories — the evening push takes the workbench along, but the other machine must bind the worktree locally anew. That is why the storage location is derived deterministically from the repo path (sibling folder `<repo>-worktrees/`): every session finds the same place on every machine without anything having to be negotiated. The continuation procedure (push with `-u` the first time, binding to the remote branch, infra sync) is carried by the `SKILL.md`.

**The skill's approval tiers** (table in the `SKILL.md`) settle conclusively what happens automatically, what is confirmed once per session or per project, and what every time — expressly even where something else has been agreed elsewhere for comparable activities. They are the point where the skill takes work off the user without taking decisions off them: everything with effect beyond the own worktree remains subject to consent.

**Rules whose simplification destroys the function:**

- The infra branch is never merged and never derived from another branch. Whoever branches it off `master` "for simplicity's sake" invites merging it — and thereby dumps an outdated overall state over the target branch.
- Workbench work reaches the integration branch only by squash. A "quick merge commit" in between makes the checkpoint history part of the integration branch and renders the later squash discipline ineffective.
- Experiments on infra files end through the sync, never through a merge and never through manual rollback. The marks (`INFRA-EXPERIMENT`) are not decoration: the completion checklist finds forgotten experiments through them — mechanically, not by memory.
- The squash commit in the main checkout is executed without `-a`. With `-a` the user's unversioned hand work rides into the squash.

**Technical prerequisite:** Git with worktree support; the initial setup uses `git worktree add --orphan` and needs Git >= 2.42 for it. Everyday use gets by with older versions.

**Extending.** The project-concrete names (branches, prefix, storage location, infra file list) belong into the project's `.claude/git-worktree-model.json` (fields: `integration_branch`, `release_branch`, `workbench_prefix`, `worktree_dir`, `infra_branch`, `infra_files`), not into the skill text — otherwise a project scheme suddenly holds for all projects.

## State and open points

**Status:** Complete rewrite, talked through with the developer and approved (24/25 August 2026); the earlier version (only settling write authority, worktrees merely explained) lives on as the fallback. Decided are: the approval tiers as in the `SKILL.md`; the workbench scheme `claude-wb/<topic>` with a slash and an English `<topic>`; the skill name without a personal suffix, because the model counts as generally usable; the worktree storage location as the sibling folder `<repo>-worktrees/` next to the repository (deterministically derivable from the repo path — the precondition for working across several machines by evening push and morning pull). Installed at the developer's (`~/.claude/skills/parallel-sessions/`, German SKILL version); this repository is at the same time the model's first deployment project.

**Deliberately left open.** The concrete branch names (integration, release, infra branch), the workbench prefix, the storage location and the infra file list are determinations of the respective project and live in its `.claude/git-worktree-model.json` — the skill carries only the procedure and the roles.
