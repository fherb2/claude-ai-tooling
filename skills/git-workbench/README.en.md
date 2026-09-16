# git-workbench — how a Claude session commits: directly, on a workbench, or isolated in its own worktree

*Last updated: 2026-09-16*

*[Deutsche Fassung](https://github.com/fherb2/claude-ai-tooling/blob/master/skills/git-workbench/README.md)*

**✅☑ Finished and usable.** Instructions complete, frontmatter set, silent trigger present; German and English versions available. — Usable with Claude Code.

**Determines in which granularity and how isolated a Claude session commits in a Git repository — and thereby solves two problems at once: that a machine's safety commits shred the history into unreadable small steps, and that two sessions in the same working tree overwrite each other silently.** Three modes: `direct` commits every approved step durably on the current branch; `workbench` secures intermediate states on a short-lived branch and brings them onto the development branch at the end, by squash, as one commit in human granularity; `worktree` does the same in its own Git worktree, so that several sessions can work at the same time without touching each other. Without a setting the skill asks once per session (`ask`). Plus a push rule that asks before every push about unpublished commits on all local branches, so that nothing is stranded when switching machines.

**Scope:** The skill applies only to Claude Code working locally on a Git repository, not to claude.ai. It governs how a session commits, not the branches of the project — which branch is the development branch, how transfers to the release happen, how central files are distributed. If the project keeps a file `.claude/git-branch-model.json` for that, the skill reads the name of the development branch from it; otherwise it asks. It needs nothing more.

## Installation

1. **Download the package.** `downloads/git-workbench_en_local.zip`

2. **Unpack.** The archive contains a folder `git-workbench/` with all files. Unpack it into `~/.claude/skills/` — then the skill applies to all projects — or into `.claude/skills/` in the project, then only there. An existing folder of the same name is replaced; nothing old is left behind.

3. **Adopt the silent trigger.** You have to do this by hand. Claude then recognizes more easily from the context whether the skill should be loaded. To do so: from `CLAUDE-snippet.md`, **everything below the separator line** goes into the `CLAUDE.md` of the chosen location. The italic text above it stays behind; the file itself remains in the skill folder and shows, by its date line, which state the adopted trigger is from.

   Without this step the skill only works when called explicitly with `/git-workbench`.

4. **Set up per project — optional.** Without a configuration file the skill asks once in every session for the mode. Whoever does not want that creates `.claude/git-workbench.json` — in the chat, on request; the skill guides through the steps and explains along the way what happens automatically from then on. For `worktree` the worktree folder additionally belongs in the `.gitignore`.

The `README.md` comes with the package, and for good reason: the `SKILL.md` refers to it for all reasoning, and Claude names it as the reference when the skill first takes effect and quotes from it when asked. Whoever just installs the skill and watches what happens thus gets the explanation when they need it. If the README is missing, the skill still works — answers to why-questions just come out thinner.

## Details

**Three parts: thin `SKILL.md`, core rules, worktree rules.** The `SKILL.md` only determines the mode and loads `rules.en.md` (or `rules.de.md`) with the rules that hold in every mode. Only in `worktree` does `rules-worktree.en.md` come in addition — creating, orphaned workbenches, switching machines, the collision with the sandbox. Thus the machinery for parallel sessions costs no context in the other modes (split according to chapter 5.2 of the guidelines).

**Why the workbench exists: granularity, not parallelism.** A Claude session wants a point of return after every partial step — a misunderstanding that surfaces only three steps later should be correctable by a reset. Those points of return are machine granularity; nobody wants to read them in the history of the development branch. The workbench translates: intermediate states on a branch of its own, at the end a squash to the one commit a human would have made. From that follows the one rule that makes the squash right here and wrong elsewhere: **commits a human has made keep their granularity; safety commits of a machine are brought to human granularity.** A topic branch of the user is therefore merged, a workbench squashed.

**Why `direct` is a mode and not carelessness.** If the user waits for the session and nobody works in parallel, every approved step is a commit in human granularity anyway — the workbench would have nothing to translate. Then the direct commit is the simpler and more honest form. The skill knows it explicitly, so that the instance does not call such a decision of the user into question session after session, but executes it as a valid variant.

**Why the skill asks instead of guessing.** Without a configuration file `ask` applies: at the first writing Git command the session names its branch and its situation and proposes a mode. That is deliberately an action as anchor and not "session start" — an instance cannot detect that state reliably, the first writing command occurs in every relevant session. Likewise for the development branch: the currently checked-out branch is a proposal, not an assumption. Git has no signal for "this is the development branch", and the remote's default branch is often precisely the release branch.

**Why the skill stores the development branch nowhere.** It needs exactly one value from outside. If the project keeps a branching model, the value is in that model's file — one fact, one home. If the skill stored it additionally, there would be two versions drifting apart. If the project keeps no branching model, the question once per session is cheaper than a second truth. For the same reason there is no state file: which workbenches and worktrees exist, Git knows (`git worktree list`, the branch list); a file beside it goes stale.

**The push rule.** Git synchronizes branches individually. Whoever pushes `dev` in the evening and continues on the other machine in the morning finds there no workbench and no other branch that was not pushed as well. That is why the skill checks all local branches for unpublished commits before every push and asks per find whether it should be pushed too — with yes as the proposal. The rule does not hang on the term "workbench": in `direct` too there are branches that can be left behind. A branch without an upstream link is the most treacherous case, because `git status` stays silent about it; that is why it is linked with `-u` at its first push. Exactly that is how, in the first project using this skill, a whole working session on one machine was left behind unnoticed while work continued on the other.

**Why the workbenches lie inside the repository and not beside it.** A sibling folder beside the repository would be just as deterministically derivable from the repo path — but it would lie outside the folder the editor has open: the user then does not see what is being worked on, and if they switch there, the directory counts as a different project. `.claude/worktrees/` is at the same time the place where Claude Code creates its own worktrees; moving there with `EnterWorktree` therefore needs no separate approval. The folder must be in the `.gitignore`, otherwise its content shows up as unversioned in the main checkout — worktrees are working copies of the repository, not project files.

**What moving into the worktree costs and brings.** If the session stays in the main checkout and works via absolute paths, nobody enforces anything — only the skill's rules apply. If it moves in with `EnterWorktree`, the chat continues (only the transcript's storage follows), and from then on Claude Code itself blocks every write access to the main checkout, every redirect of Git into it, and every command whose target it cannot verify — including heredocs with unquoted delimiters, with which multi-line commit messages are written. The squash happens in the main checkout and therefore demands `ExitWorktree` beforehand. Documented: [Worktrees](https://code.claude.com/docs/en/worktrees).

**Nothing is cleaned up by itself.** Claude Code's automatic sweep removes only worktrees of subagents and background sessions; the ones created with `--worktree` or by hand it never touches (ibid.). A finished session thus leaves its workbench behind, branch included, and a clean working tree does not mean there is nothing to save — the work then sits in the branch. Exactly that happened on 25 August 2026: a workbench with one unmerged commit across 17 files, found only when a new session wanted to touch the same files. That is why the check with `git worktree list` stands at the beginning of the worktree rules.

**Work across several machines.** Git synchronizes branches, never worktree directories — the evening push takes the workbench along, but the other machine has to re-bind the worktree locally. That is why the storage location is derived deterministically from the repo path: every session finds the same place on every machine, without anything having to be negotiated. The worktree rules file carries the continuation procedure.

**The fallback without isolation: settle write authority.** If a second session works in the same working tree and `worktree` is not the mode, the skill first asks which session may execute writing Git commands, and offers the isolation. That is the oldest rule of this skill; it stays, because not every project wants worktrees.

**Known limitation: collision with the Bash sandbox.** If the sandbox is active, it masks `.git/config.worktree` as soon as `git worktree` runs — after that every Git command fails, including `git status` ([issue #80278](https://github.com/anthropics/claude-code/issues/80278), open, reproduced by maintainers). The worktree rules file detects from the session context whether the sandbox is active and then warns at runtime instead of silently running into the collision (section "Known collision", marked with `TEMP ISSUE-80278` and meant to be removed once the issue is fixed). Only the `worktree` mode is affected; `direct` and `workbench` need no `git worktree`.

**The skill's approval tiers** (table in the rules file) settle conclusively what happens automatically, what is confirmed once per session or per project, and what every time — explicitly also where something else has been agreed elsewhere for comparable activities. They are the point where the skill takes work off the user's hands without taking decisions off them: everything with effect beyond the own workbench remains subject to consent.

**Rules whose simplification destroys the function:**

- Workbench work reaches the development branch only by squash. A "quick merge commit" in between makes the safety history part of the main line and the later squash discipline void.
- The squash commit is executed without `-a`. With `-a`, the user's unversioned hand work rides into the squash.
- The squash is explicitly addressed to the main checkout. A squash inside the workbench's worktree merges the branch into itself; the chain breaks (observed four times in one day, 26 August 2026).
- Orphaned worktrees are reported, not passed over.

**Technical prerequisite:** Git with worktree support for the `worktree` mode; `direct` and `workbench` get by with any Git.

**Extending.** The project-specific values belong in the project's `.claude/git-workbench.json` (fields: `mode` with `direct`, `workbench`, `worktree` or `ask`; `workbench_prefix`; `worktree_dir`), not in the skill text — otherwise one project's scheme suddenly applies to all projects. The `git-` prefix in the file name lowers the risk of a collision with future engine files in `.claude/` and is honest about the content: without Git nothing of the method would remain.

## Status and open points

**Status:** New version of 15 September 2026 as the successor of the skill `parallel-sessions`, which mixed branching model and workbench. The branching model — development, release and management branch including the distribution of the central files — has been extracted and is a capability of its own; this skill now carries only how a session commits. New compared to the predecessor: the modes `direct` and `workbench` without a worktree, `ask` as the default, the push rule for all branches instead of only the open workbench, and the worktree rules as a file of their own, loaded only when needed. Taken over from the predecessor and unchanged: the workbench scheme `claude-wb/<topic>` with slash and English `<topic>`; the worktree location `.claude/worktrees/` inside the repository; the approval tiers.

**Measured (16 September 2026, procedure per chapter 4.2 of the guidelines, 34 runs with Sonnet, Opus and Fable):** The trigger fires with all three models on a plain commit request, with and without the configuration file; the negative control (a Git question without any writing intent) stays silent. The skill is thus reliable at the anchor "first writing Git command" — more reliable than its neighbour at the same anchor, whose description does not match the commit case (see that skill's README).

**Deliberately left open.** Mode, workbench prefix and storage location are decisions of the respective project and live in its `.claude/git-workbench.json` — the skill carries only the procedure. Which branch is the development branch the skill does not determine either: it reads it from the project's branching model if there is one, and asks otherwise.
