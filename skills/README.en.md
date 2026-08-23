# Skills for Claude Code

*[Deutsche Fassung](README.md)*

Reusable skills for Claude Code, together with the triggers that fire them. This directory is the source — the skills are developed and maintained here. They only take effect once they have been copied to their target location (chapter 3).

## 1 The skills one by one


| Skill                                                                            | Purpose                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`common-code-generation/`](common-code-generation/README.en.md)<br>✅☑ | **General rules for the cooperation on, and the carrying out of, writing and changing code, apart from code style rules**: e.g. no unrequested extension of the functional scope, careful use of processing time and memory |
| [`parallel-sessions/`](parallel-sessions/README.md) (in German)<br>✅ | **Several Claude instances working in the same repository at once**: working with or without a worktree. Settles the cooperation when several Claude Code instances are working in the same repository at the same time. |
| [`🚧_software-dev-doc-fh/`](🚧_software-dev-doc-fh/README.md) (in German)<br>🚧 | **A documentation standard for planning before coding and for the running record of what was implemented** — what is being built, which decisions were taken and why this way and not another. Documentation accompanying a software project, as the basis for coding, for debugging and for the later closing and user documentation. |
| [`🚧_softwareaufgabe-erkennen/`](🚧_softwareaufgabe-erkennen/README.md) (in German)<br>🚧 | **Recognizing that a request amounts to software to be written or changed** — even when it never uses words like "code" or "programming". So far an idea on record along with its measurements, not yet a skill.                                    |
| [`temp-debug-code/`](temp-debug-code/README.en.md)<br>✅☑ | **Unambiguous marking of code added or changed for an ongoing debugging session only** — not for debug code meant to stay in the source permanently.                                                                                               |
| [`tiefen-recherche/`](tiefen-recherche/README.en.md)<br>✅☑ | **Thorough source and literature research that does not give up too early** — systematic variation of search terms, channels and search levels, mandatory verification of every search summary, and instead of "nothing found" a report on the search paths still open. |
| [`🚧_translation-task/`](🚧_translation-task/README.md) (in German)<br>🚧 | **Translation of documents whose content is close to software development** — README files, concept and implementation documents, guides. Not tied to one direction of translation. |
| [`🚧_web-code-artefacts/`](🚧_web-code-artefacts/README.md) (in German)<br>🚧 | **Handling code artifacts in the web frontend**: when code becomes an artifact and when a change instruction in the chat, and in what form changes to already adopted code are communicated.                                                        |
| [`🚧_zotero-use/`](🚧_zotero-use/README.md) (in German)<br>🚧 | **Connecting Claude directly to one's own Zotero library** — creating new entries with a PDF, searching metadata and full text in a targeted way, managing collections. So far an idea on record along with its researched architecture, not yet a skill. |

(✅ German version finished and usable · ☑ English version finished and usable · 🚧 in progress · ⚠️ with reservations)

## 2 Purpose

This project develops and maintains skills for general use with Claude (web and local, and on every level from user to project).

It introduces and implements a concept of "silent triggers" that allows even weaker models to start a skill very early out of the context.

The rules for this area, `skills/`, and the findings from the accompanying test series are in `implementation_doku.md`. This README describes only the result: what there is and how to use it. On top of that, every skill has a README file of its own carrying its particular notes and its current state of development.

## 3 Obtaining and installing skills

What skills are, how they are structured and how Claude Code loads them is described in the official documentation: **[Extend Claude with skills](https://code.claude.com/docs/en/skills)**. This README takes that as known.

**What is added here are silent triggers:**

The technique Anthropic provides fires a skill via its `description`: if it matches the request, the skill is loaded. That works well when the user asks for something the skill obviously covers. It does not work, or works poorly, when the trigger is an observation nobody in the chat puts into words — for instance that a second Claude instance, or the user, is working in the same repository while the chat holds the authority over commits. For such cases a skill comes with an additional paragraph for the `CLAUDE.md` of the target location, naming the condition and pointing to the skill. In this project it is called a **silent trigger**, because usually nobody invokes it explicitly for a task and nobody sees it: it works from the background, inside the AI's reasoning, without the user noticing anything. Its job is to make sure the skill takes effect as early as possible in cases where, without it, the AI would still treat the skill as too faint a match against its description and the task at hand.

Skills that need such a trigger carry a `CLAUDE-snippet.md` in their folder for it. The snippet inside is to be added by hand to the `CLAUDE.md` of the same level.

**Which languages a skill is available in differs from case to case.** Most of them exist here in German only; their files are then simply called `SKILL.md`, `README.md` and `CLAUDE-snippet.md` and are copied unchanged. Only where there are several versions do `SKILL.md` and `CLAUDE-snippet.md` carry a language marker in front of the extension — `SKILL.de.md`/`SKILL.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Exactly **one** version then gets installed, and in doing so its marker is dropped: Claude Code recognizes the name `SKILL.md` and nothing else. `README.md` is the exception: with several versions it carries **no** marker for the German version, only the English one is called `README.en.md` — GitHub and GitLab, when browsing a folder, automatically display only a file named exactly `README.md`; a language marker would prevent that (see `implementation_doku.md`, chapter 5.1, for details). Which language version to pick follows from the language used in the chat, whereby the English version should as such be compatible with every chat language.

The folder name is the same in all versions and never carries a marker; the same holds for the skill name in the frontmatter and hence for the `/<skill-name>` invocation.

### Installation

1. **Choose the target location (level of effect).** A skill applies either to all of the user's projects or to a single one:


   | Location | Path                                     | Applies to                |
   | -------- | ---------------------------------------- | ------------------------- |
   | Personal | `~/.claude/skills/<skill-name>/SKILL.md` | all of the user's projects |
   | Project  | `.claude/skills/<skill-name>/SKILL.md`   | this project only         |
2. **Copy the skill folder, choose the language version where there is one.** The folder here already has exactly the structure it will have at the target location. It is copied under its unchanged name. Where a file exists in several language versions, only the desired one comes along, and its language marker is dropped in the process: `SKILL.de.md` becomes `SKILL.md` at the target location, so that Claude accepts it for what it is. If the marker stays, Claude Code may well not find the skill, since the file name `SKILL.md` is what Anthropic defined for skills.
3. **Adopt the silent trigger, if there is one.** If the folder contains a `CLAUDE-snippet.md`, its content **below the separator line** is taken over into the `CLAUDE.md` of the target location — for a personal skill into `~/.claude/CLAUDE.md`, for a project skill into that project's `CLAUDE.md`. The text above the separator line is the instruction for doing so and is not copied along. The `CLAUDE-snippet.md` is then deleted at the target location: were it left lying around, the trigger would exist twice, and the two versions would drift apart at the next adjustment.

The skill's `README.md` may stay at the target location — it is at the same time its user documentation, and just as useful there as here.

Without step 3 the skill still works — but only if it is invoked explicitly with `/<skill-name>`, or if the AI has become sufficiently aware of the skill through its description.

### When adjusting a trigger

Three rules — two of them from measurements rather than taste, the third from Anthropic's own guidance:

**The skill's `description` decides first.** It begins with the main use case and uses the words a user would say unprompted. Putting a classification in front of it ("Test skill…", "Internal version…") or using project-internal jargon that appears in no request can render the trigger ineffective — measured: the very same trigger text fired with a good description and did not with a weak one.

**A trigger should be bound to an event or an action,** not merely to a property of the task. "Keep an eye on whether this task is complex" does not carry itself; "before you change a file for the first time, check …" or "if a file turns up that you have not touched, then …" fire reliably. The test series behind this are in `implementation_doku.md`, chapter 3.

**The `description` is written in the third person.** It describes the skill — "Translates documents …", "Use as soon as …" — and addresses nobody, neither Claude nor the user. This is not a matter of style: the description is injected into the system prompt, and a shifting point of view disturbs the selection among many skills there. Anthropic says so explicitly — *"Always write in third person […] inconsistent point-of-view can cause discovery problems"* ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## 4 Open points of the project

What is open on an individual skill is stated in that skill's own `README.md` in its folder.

Open across the project as a whole is:

- Reorganizing the working instructions into skill homes (working model: `implementation_doku.md`, chapter 8).

**Next step (plan, not yet executed):** The items of the instruction inventory (T1–T27; kept in a temporary working folder that will be removed once this is done) are assigned one by one. Claude hands them over pre-sorted — bundled by proposed skill home, each item with its origin, its variants, and a scope proposal per chapter 8.3 of `implementation_doku.md` (coding only / all kinds of work / other) — and the developer decides or confirms each assignment. The yardstick for the distribution is the working model in chapter 8.2. The confirmed list of homes is then written into `implementation_doku.md`; only after that does the writing of the individual skills begin.

## License

All skills in this directory are under **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — the waiver of all rights as far as legally possible. That means:

- **Use without any condition** — private, commercial, in closed as well as in open projects.
- **No attribution needed.** Whoever wants to may name the source; nobody has to.
- **Freely modifiable and redistributable**, in modified form and under another name as well.
- **No obligation to disclose changes** or to give them back.
- **No license text has to be passed on** — unlike MIT or Apache-2.0, both of which demand attribution and the passing on of the license text.
- **No warranty and no liability.** Whatever these skills bring about is the responsibility of whoever employs them.

Anthropic makes no stipulations about the licensing of skills you write yourself, and the skill format is an open standard without conditions of its own. Anthropic's own skills repository uses Apache-2.0 for the open-source skills. CC0 is therefore a deliberate choice here, not a requirement — and the more far-reaching one: Apache-2.0 demands attribution and the passing on of the license text, CC0 does not.
