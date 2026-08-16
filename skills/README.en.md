# Skills for Claude Code

*[Deutsche Fassung](README.md)*

Reusable skills for Claude Code, together with the triggers that fire them. This directory is the source — the skills are developed and maintained here. They only take effect once they have been copied to their target location (chapter 2).

## 1 Purpose

This project develops and maintains skills for general use with Claude (web and local, and on every level from user to project).

It introduces and implements a concept of "silent triggers" that allows even weaker models to start a skill very early out of the context.

The rules for this area, `skills/`, and the findings from the accompanying test series are in `skill_vorgaben.md`. This README describes only the result: what there is and how to use it. On top of that, every skill has a README file of its own carrying its particular notes and its current state of development.

## 2 Obtaining and installing skills

What skills are, how they are structured and how Claude Code loads them is described in the official documentation: **[Extend Claude with skills](https://code.claude.com/docs/en/skills)**. This README takes that as known.

**What is added here are silent triggers:**

The technique Anthropic provides fires a skill via its `description`: if it matches the request, the skill is loaded. That works well when the user asks for something the skill obviously covers. It does not work, or works poorly, when the trigger is an observation nobody in the chat puts into words — for instance that a second Claude instance, or the user, is working in the same repository while the chat holds the authority over commits. For such cases a skill comes with an additional paragraph for the `CLAUDE.md` of the target location, naming the condition and pointing to the skill. In this project it is called a **silent trigger**, because usually nobody invokes it explicitly for a task and nobody sees it: it works from the background, inside the AI's reasoning, without the user noticing anything. Its job is to make sure the skill takes effect as early as possible in cases where, without it, the AI would still treat the skill as too faint a match against its description and the task at hand.

Skills that need such a trigger carry a `CLAUDE-snippet.md` in their folder for it. The snippet inside is to be added by hand to the `CLAUDE.md` of the same level.

**Skills here are usually available in two language versions,** a German one and an English one. Both sit in the same folder and are distinguished by a language marker in front of the extension: `SKILL.de.md` and `SKILL.en.md`, likewise `README.de.md`/`README.en.md` and `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Exactly **one** of the two versions gets installed, and in doing so the marker is dropped — Claude Code recognizes the name `SKILL.md` and nothing else. Which language version to pick follows from the language used in the chat, whereby the English version should as such be compatible with every chat language.

The folder name is the same in both versions and never carries a marker; the same holds for the skill name in the frontmatter and hence for the `/<skill-name>` invocation.

### Installation

1. **Choose the target location (level of effect).** A skill applies either to all of the user's projects or to a single one:


   | Location | Path                                     | Applies to                |
   | -------- | ---------------------------------------- | ------------------------- |
   | Personal | `~/.claude/skills/<skill-name>/SKILL.md` | all of the user's projects |
   | Project  | `.claude/skills/<skill-name>/SKILL.md`   | this project only         |
2. **Copy the skill folder, choose the language version.** The folder here already has exactly the structure it will have at the target location. It is copied under its unchanged name; of each file only the desired language version comes along, and its language marker is dropped in the process: `SKILL.de.md` becomes `SKILL.md` at the target location, so that Claude accepts it for what it is. If the marker stays, Claude Code may well not find the skill, since the file name `SKILL.md` is what Anthropic defined for skills.
3. **Adopt the silent trigger, if there is one.** If the folder contains a `CLAUDE-snippet.md`, its content **below the separator line** is taken over into the `CLAUDE.md` of the target location — for a personal skill into `~/.claude/CLAUDE.md`, for a project skill into that project's `CLAUDE.md`. The text above the separator line is the instruction for doing so and is not copied along.
4. **Delete `CLAUDE-snippet.md` and `README.md` at the target location** or do not copy them there in the first place. For the snippet this is mandatory: were it left lying around, a second version of the trigger would exist, and the two would drift apart at the next adjustment.

Without steps 3 and 4 the skill still works — but only if it is invoked explicitly with `/<skill-name>`, or if the AI has become sufficiently aware of the skill through its description.

### When adjusting a trigger

Three rules — two of them from measurements rather than taste, the third from Anthropic's own guidance:

**The skill's `description` decides first.** It begins with the main use case and uses the words a user would say unprompted. Putting a classification in front of it ("Test skill…", "Internal version…") or using project-internal jargon that appears in no request can render the trigger ineffective — measured: the very same trigger text fired with a good description and did not with a weak one.

**A trigger should be bound to an event or an action,** not merely to a property of the task. "Keep an eye on whether this task is complex" does not carry itself; "before you change a file for the first time, check …" or "if a file turns up that you have not touched, then …" fire reliably. The test series behind this are in `skill_vorgaben.md`, chapter 3.

**The `description` is written in the third person.** It describes the skill — "Translates documents …", "Use as soon as …" — and addresses nobody, neither Claude nor the user. This is not a matter of style: the description is injected into the system prompt, and a shifting point of view disturbs the selection among many skills there. Anthropic says so explicitly — *"Always write in third person […] inconsistent point-of-view can cause discovery problems"* ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## 3 The skills one by one


| Skill                                                                            | Purpose                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ✅[`common-code-generation/`](common-code-generation/README.en.md)               | **General rules for writing and changing code**: English identifiers in the source, no unrequested extension of the functional scope, careful use of processing time and memory — names and optimizations are proposed, not decided.               |
| 🚧[`parallel-sessions/`](parallel-sessions/README.md) (in German)                | **Several Claude instances working in the same repository at once**: settle who may issue writing Git commands first, then offer the worktree model as a clean separation.                                                                          |
| 🚧[`software-dev-doc-fh/`](software-dev-doc-fh/README.md) (in German)            | **A documentation standard for planning before coding and for the running record of what was implemented** — what is being built, which decisions were taken and why this way and not another. Not meant: source comments and user documentation.   |
| 🚧[`softwareaufgabe-erkennen/`](softwareaufgabe-erkennen/README.md) (in German)  | **Recognizing that a request amounts to software to be written or changed** — even when it never uses words like "code" or "programming". So far an idea on record along with its measurements, not yet a skill.                                    |
| 🚧[`temp-debug-code/`](temp-debug-code/README.md) (in German)                    | **Unambiguous marking of code added or changed for an ongoing debugging session only** — not for debug code meant to stay in the source permanently.                                                                                               |
| 🚧[`translation-task/`](translation-task/README.md) (in German)                  | **Translation of documents close to software development** — technical terms, code blocks, file and product names each follow their own rules. Not tied to one direction of translation.                                                            |
| 🚧[`web-code-artefacts/`](web-code-artefacts/README.md) (in German)              | **Handling code artifacts in the web frontend**: when code becomes an artifact and when a change instruction in the chat, and in what form changes to already adopted code are communicated.                                                        |

(✅ ready to use · 🚧 in progress)

### 3.1 `translation-task`

**What for.** Translates documents whose content is close to software development — README files, concept and implementation documents, guides. Not tied to one direction of translation.

**What it actually does.** It settles the target language and the degree of technical jargon up front, submits a work sample before the full translation (at most a third of the document and at most around 1000 words), and afterwards handles three things by fixed rules: code blocks are translated only if they are recognizably illustrative and have no real source in the project; proper names, product names and literal markers such as `@Claude:` always stay untouched; decisions on terminology go into a glossary.

**Particularities.** The skill detects for itself whether it is running locally in Claude Code or in claude.ai, and keeps the glossary only locally — in claude.ai it does not even mention it, rather than promising a file nobody will find again.

**Extending it.** The glossary sits in the skill folder as `glossar.md` and is the place intended for your own decisions on terminology; it grows in use. Whoever changes the rules themselves should not simplify the detection of code blocks: the project-wide search for a real source is the reason why genuine tool output does not get translated by accident.

**Installation.** As in chapter 2, no silent trigger needed — the trigger comes from the user themselves.

### 3.2 `parallel-sessions`

**What for.** Settles the cooperation when several Claude Code instances are working in the same repository at the same time.

**What it actually does.** Two steps in a fixed order. First: it has it settled which instance may run writing Git commands on its own, and runs none itself until it gets an answer. Second: it offers the worktree model as a clean separation and explains both ways of setting it up — via the `EnterWorktree` tool and by hand via `git worktree add`, including the differences in storage location and base branch.

**Particularities.** The skill deliberately does not decide how a project's own branch naming scheme goes together with several simultaneous worktrees — that is a project decision. It names the conflict and leaves the decision to the user.

**Extending it.** Whoever adds a naming scheme of their own to the skill should anchor it in the project `CLAUDE.md` and merely refer to it here, instead of writing it into the skill — otherwise the scheme suddenly applies to all projects.

**Installation.** As in chapter 2, **with** a silent trigger (`CLAUDE-snippet.md`). Without it the skill does not notice the situation, because nobody says "there is a second instance working here" unprompted.

### 3.3 `software-dev-doc-fh`

**What for.** A documentation standard for planning before coding and for the running record of what was implemented: what is being built, which decisions were taken, and why this way and not another. **Not** meant are source code comments and user documentation.

**What it actually does.** It prescribes four phases (exploration, fixing, segmentation, implementation), a three-part document structure (interrelations, rules, units), the separation of roadmap and status, as well as the rule that concept documents contain no implementation code. Along with that the working loop by which documentation and code come into being in alternation, and the handling of review findings in the appendix of the documentation.

**Particularities.** The suffix `-fh` is deliberate: this is the way a particular developer works, not the only possible standard. Whoever works differently copies the skill and rewrites it, instead of bending this one. The skills `konzept-segmentierung` and `konsistenzpruefung` are tools within this standard.

**Extending it.** Two decisions carry the rest and should not fall when adjusting it: the prose-code boundary (otherwise you later check code against code) and the rule that every statement has exactly one normative home (otherwise two versions of the same decision come into being and drift apart). The admission test for segment 2 — "you must be able to point at a file and say, that violates this rule" — is the tool for deciding where a new statement belongs.

**Installation.** As in chapter 2, **with** a silent trigger (`CLAUDE-snippet.md`). Its wording is bound to an action ("before you … for the first time") — that anchor may be moved, but not left out, otherwise the trigger stops firing.

### 3.4 `common-code-generation`

**What for.** General rules for writing and changing code — the kind of decisions that would otherwise have to be repeated in every `CLAUDE.md`. **Not** its subject: the obligation to submit a plan before changing a file; that stays in the `CLAUDE.md`, because a skill only probably loads, whereas a protective rule has to take effect reliably.

**What it actually does.** It lays down that everything in the source code — identifiers, comments, docstrings — is in English, and that self-chosen names are submitted to the user for a decision. It forbids unrequested extensions of the functional scope. It prescribes a ranking of resources (processing time, main memory, mass storage) and requires every proposed optimization to be checked against reality beforehand: whether it pays off in the actual use case, and whether its effect is measurable at all across the application as a whole. Along with that a special case — the ordering of loop exit criteria according to prior knowledge about the data, including the note that the compiler changes the order in the machine code anyway.

**Particularities.** The trigger's anchor lies at the earliest possible moment of the session, not at the first naming or the first proposed optimization. The reason: the skill is not a procedure but a set of rules that applies from the first line of code onward — and because its body stays in the context once loaded and is not read again, a late hit no longer rescues the decisions that were taken before it.

**Extending it.** The anchor may be moved when adjusting the skill, but not left out. And the obligation to plan does not belong pulled into the skill, tempting as that looks: a trigger is probabilistic, a protective rule has to take effect reliably.

**Installation.** As in chapter 2, **with** a silent trigger (`CLAUDE-snippet.md`).

## 4 Open points of the project

What is open on an individual skill is stated in that skill's own `README.md` in its folder.

Open across the project as a whole is:

- nothing

## License

All skills in this directory are under **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — the waiver of all rights as far as legally possible. That means:

- **Use without any condition** — private, commercial, in closed as well as in open projects.
- **No attribution needed.** Whoever wants to may name the source; nobody has to.
- **Freely modifiable and redistributable**, in modified form and under another name as well.
- **No obligation to disclose changes** or to give them back.
- **No license text has to be passed on** — unlike MIT or Apache-2.0, both of which demand attribution and the passing on of the license text.
- **No warranty and no liability.** Whatever these skills bring about is the responsibility of whoever employs them.

Anthropic makes no stipulations about the licensing of skills you write yourself, and the skill format is an open standard without conditions of its own. Anthropic's own skills repository uses Apache-2.0 for the open-source skills. CC0 is therefore a deliberate choice here, not a requirement — and the more far-reaching one: Apache-2.0 demands attribution and the passing on of the license text, CC0 does not.
