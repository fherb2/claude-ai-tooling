# parallel-sessions — several Claude sessions at the same time in the same repository, cleanly separated via Git worktrees

*Last updated: 2026-08-30*

*[Deutsche Fassung](README.md)*

**✅☑ Finished and usable.** Instructions complete, frontmatter set, silent trigger present; German and English versions available. — Usable with Claude Code.

**Gives every simultaneously working Claude session its own Git worktree with its own workbench, and thereby makes the question of which session may commit obsolete.** Two sessions in the same working tree overwrite each other silently — the treacherous part is not the conflict, which Git would report, but the unnoticed riding-along of foreign intermediate states. The skill separates the sessions physically: one worktree per session, inside it a short-lived workbench derived from the integration branch, completion by squash merge. Central files that must be current everywhere (the project CLAUDE.md, editor configuration, `.gitignore`) live on a dedicated orphan **infra branch** and are not merged but fetched by every session into its own worktree via `git restore --source`. For projects without this model the skill contains the old immediate rule as a fallback: first settle Git write authority, then work.

**Scope:** The skill applies only to Claude Code working locally on a Git repository, not to claude.ai. It governs the collaboration of the sessions, not a project's release procedure (when something moves from the integration to the release branch); on that it says nothing.

## Installation

1. **Choose the target location.** The skill applies either to all of the user's projects or to a single one:

   | Location | Path                                  | Applies to                 |
   | -------- | -------------------------------------- | -------------------------- |
   | Personal | `~/.claude/skills/parallel-sessions/` | all of the user's projects |
   | Project  | `.claude/skills/parallel-sessions/`   | this project only          |

2. **Copy one language version of the folder `parallel-sessions/`.** It holds `SKILL.de.md`/`SKILL.en.md`, `rules.de.md`/`rules.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`, this `README.en.md` and the German `README.md`; all files of the chosen language come along. The chosen SKILL version is called `SKILL.md` at the target location — whether renamed or additionally placed makes no difference; Claude Code recognizes that name and no other. The rules file keeps its name: the `SKILL.md` points to it, and that pointer is the only way the rules ever get loaded; whoever renames it carries the pointer along. The date lines of README and snippet show at the target location which state the installation is from.

3. **Adopt the silent trigger.** The content of the `CLAUDE-snippet` file matching the chosen language, **below the separator line**, goes into the `CLAUDE.md` of the target location; the snippet files stay at the target location, only the `CLAUDE.md` is effective. Without this step the skill does not notice the situation: nobody says of their own accord "a second instance is working here right now".

4. **Set up per project.** The worktree model does not take effect through the installation but through the initial setup in the project (branches, infra file list, the file `.claude/git-worktree-model.json`). It happens in the chat, at the user's request; the skill leads through the steps. Without it only the fallback applies.

The `README.md` belongs at the target location too: the `SKILL.md` points to it for all reasoning, and Claude consults it when the user asks follow-up questions. If it is missing there, the skill still works — answers to why-questions just come out thinner. Its presence is not checked.

## Details

**Split in two: thin `SKILL.md`, rules file loaded on demand.** The skill deliberately fires broadly — also in sessions where the worktree model has not been agreed at all. So that those sessions do not carry the full rules text in context, the `SKILL.md` only establishes the situation and loads the rules file (`rules.de.md`/`rules.en.md`) only when the model holds or is to be set up; the immediate rule for the model-free case stands completely in the `SKILL.md` itself (split per chapter 5.2 of the guidelines, 26 August 2026).

**Why an orphan infra branch with `restore` instead of a merge flow.** Completing a workbench is a squash merge, and squashes erase ancestry: were the central change distributed into the workbenches by merge and the workbench squashed afterwards, the integration branch would know nothing of the common origin — the next merge of the same infra state would reckon with an outdated merge base and produce conflicts in files that never held a real conflict. `git restore --source=<infra>` bypasses ancestry entirely: for every infra file there is exactly one valid version (the one on the infra branch), and overwriting is always the correct resolution. That is precisely why the rule "no durable change to infra files outside the infra branch" is not tidiness but the condition under which the procedure is conflict-free.

**Why distribution is pull-based.** The infra branch pushes nothing into the workbenches; every session fetches the state itself — automatically at session start and in the first step of the completion checklist. That turns temporary deviation into an intended state instead of an error: an experiment — a central change that one session is to try out first, before it holds for everyone, say a new trigger paragraph in the CLAUDE.md or a hook in the settings — is simply a sync not yet run plus a marked local change. It is ended by that same sync — one command, no editing back. All of this is possible in the first place only because of the worktrees: Claude loads the project CLAUDE.md from the worktree of the respective session; in a shared working tree all sessions would see every test rule.

**Why a dedicated file `git-worktree-model.json` instead of a block in a shared agreements file.** A shared file would need coexistence rules — whose key belongs to whom, who never touches what —, and those rules would have to stand as permanent text in every skill that co-uses the file: context costs in every turn, only to manage an avoidable problem. The dedicated file solves this by existence instead of by rules; its presence is at the same time the sign that the model has been agreed in the project. Side effect: the skill is portable, because in foreign projects it presupposes no existing agreements file. The `git-` prefix in the name lowers the risk of a collision with future engine files in `.claude/` and is honest about the content: without Git — worktrees, branches, `restore` — nothing of the method would remain.

**Work across several machines.** Git synchronizes branches, never worktree directories — the evening push takes the workbench along, but the other machine must bind the worktree locally anew. That is why the storage location is derived deterministically from the repo path (`.claude/worktrees/` inside the repository): every session finds the same place on every machine without anything having to be negotiated. The continuation procedure (push with `-u` the first time, binding to the remote branch, infra sync) is carried by the rules file.

**Why the workbenches live inside the repository and not beside it.** A sibling folder next to the repository satisfies the determinism condition just as well — but it has a drawback that weighs more in practice: it lies outside the folder the editor has open. The developer then cannot see what is being worked on, and moving there makes the directory count as a different project. `.claude/worktrees/` is also where Claude Code creates its own worktrees, so moving there with `EnterWorktree` needs no separate approval. The folder must go into the `.gitignore`, otherwise its content shows up as unversioned in the main checkout (decided 25 August 2026, after the first working session under the model).

**What moving into the worktree costs and yields.** If the session stays in the main checkout and works via absolute paths, nothing is enforced — only the skill's rules apply. If it moves in with `EnterWorktree`, the chat continues (only the transcript's storage follows), and from then on Claude Code itself blocks every write into the main checkout, every redirect of Git into it, and every command whose target it cannot verify — including heredocs with unquoted delimiters, which is how multi-line commit messages get written. The squash merge happens in the main checkout and therefore requires `ExitWorktree` first. Documented: [Worktrees](https://code.claude.com/docs/en/worktrees).

**Nothing tidies up by itself.** Claude Code's automatic sweep removes only worktrees of subagents and background sessions; the ones created with `--worktree` or by hand it never touches (ibid.). An ended session thus leaves its workbench and branch behind, and a clean working tree does not mean there is nothing to save — the work then sits in the branch. Exactly that happened on 25 August 2026: a workbench with one unmerged commit across 17 files, found only when a new session was about to touch the same files. Hence the `git worktree list` check now stands at session start.

**The skill's approval tiers** (table in the rules file) settle conclusively what happens automatically, what is confirmed once per session or per project, and what every time — expressly even where something else has been agreed elsewhere for comparable activities. They are the point where the skill takes work off the user without taking decisions off them: everything with effect beyond the own worktree remains subject to consent.

**Rules whose simplification destroys the function:**

- The infra branch is never merged and never derived from another branch. Whoever branches it off `master` "for simplicity's sake" invites merging it — and thereby dumps an outdated overall state over the target branch.
- Workbench work reaches the integration branch only by squash. A "quick merge commit" in between makes the checkpoint history part of the integration branch and renders the later squash discipline ineffective.
- Experiments on infra files end through the sync, never through a merge and never through manual rollback. The marks (`INFRA-EXPERIMENT`) are not decoration: the completion checklist finds forgotten experiments through them — mechanically, not by memory.
- The squash commit in the main checkout is executed without `-a`. With `-a` the user's unversioned hand work rides into the squash.

**Technical prerequisite:** Git with worktree support; the initial setup uses `git worktree add --orphan` and needs Git >= 2.42 for it. Everyday use gets by with older versions.

**Extending.** The project-concrete names (branches, prefix, storage location, infra file list) belong into the project's `.claude/git-worktree-model.json` (fields: `integration_branch`, `release_branch`, `workbench_prefix`, `worktree_dir`, `infra_branch`, `infra_files`), not into the skill text — otherwise a project scheme suddenly holds for all projects.

## State and open points

**Status:** Complete rewrite, talked through with the developer and approved (24/25 August 2026); the earlier version (only settling write authority, worktrees merely explained) lives on as the fallback. Decided are: the approval tiers as in the `SKILL.md`; the workbench scheme `claude-wb/<topic>` with a slash and an English `<topic>`; the skill name without a personal suffix, because the model counts as generally usable; the worktree storage location `.claude/worktrees/` inside the repository (deterministically derivable from the repo path — the precondition for working across several machines by evening push and morning pull — and within the editor's field of view; the earlier sibling folder next to the repository was not). Installed at the developer's (`~/.claude/skills/parallel-sessions/`, German SKILL version); this repository is at the same time the model's first deployment project. Since 26 August 2026 the skill is split in two: a thin `SKILL.md` establishing the situation, procedures and rules in `rules.de.md`/`rules.en.md` (see Details).

**Deliberately left open.** The concrete branch names (integration, release, infra branch), the workbench prefix, the storage location and the infra file list are determinations of the respective project and live in its `.claude/git-worktree-model.json` — the skill carries only the procedure and the roles.
