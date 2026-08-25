# Skills for Claude Code

*Last updated: 2026-08-25*

*[Deutsche Fassung](README.md)*

Reusable skills for Claude Code, together with the triggers that fire them. This directory is the source — the skills are developed and maintained here. They only take effect once they have been copied to their target location (chapter 3).

## 1 The skills one by one


| Skill                                                                            | Purpose                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`common-code-generation/`](common-code-generation/README.en.md)<br>✅☑ | **General rules for the cooperation on, and the carrying out of, writing and changing code, apart from code style rules**: e.g. no unrequested extension of the functional scope, careful use of processing time and memory |
| [`correct-zaaack-md-editor-mistakes/`](correct-zaaack-md-editor-mistakes/README.en.md)<br>✅☑ | **Finding and repairing damaged whitespace in Markdown tables** — spaces swallowed in front of inline code or bold text, and no-break spaces that defeat any search over the wording without being visible. Some WYSIWYG editors cause this on save. |
| [`parallel-sessions/`](parallel-sessions/README.en.md)<br>✅☑ | **Several Claude sessions at the same time in the same repository, separated via Git worktrees** — one workbench in its own worktree per session, central files via an infra branch, completion by squash merge; without an agreed model, settling Git write authority remains as the fallback. |
| [`pedantic-text-editing/`](pedantic-text-editing/README.en.md)<br>✅☑ | **Text editing with fidelity to detail** — every change presented individually for approval, not a character changed outside the approved spots, and afterwards the proof through the diff. For texts whose wording is itself the product; not for source code or documentation accompanying software. |
| [`temp-debug-code/`](temp-debug-code/README.en.md)<br>✅☑ | **Unambiguous marking of code added or changed for an ongoing debugging session only** — not for debug code meant to stay in the source permanently.                                                                                               |
| [`tiefen-recherche/`](tiefen-recherche/README.en.md)<br>✅☑ | **Thorough source and literature research that does not give up too early** — systematic variation of search terms, channels and search levels, mandatory verification of every search summary, and instead of "nothing found" a report on the search paths still open. |
| [`🚧_software-dev-doc-fh/`](🚧_software-dev-doc-fh/README.md) (in German) | **A documentation standard for planning before coding and for the running record of what was implemented** — what is being built, which decisions were taken and why this way and not another. Documentation accompanying a software project, as the basis for coding, for debugging and for the later closing and user documentation. |
| [`🚧_softwareaufgabe-erkennen/`](🚧_softwareaufgabe-erkennen/README.md) (in German) | **Recognizing that a request amounts to software to be written or changed** — even when it never uses words like "code" or "programming". So far an idea on record along with its measurements, not yet a skill.                                    |
| [`🚧_translation-task/`](🚧_translation-task/README.md) (in German) | **Translation of documents whose content is close to software development** — README files, concept and implementation documents, guides. Not tied to one direction of translation. |
| [`🚧_web-code-artefacts/`](🚧_web-code-artefacts/README.md) (in German) | **Handling code artifacts in the web frontend**: when code becomes an artifact and when a change instruction in the chat, and in what form changes to already adopted code are communicated.                                                        |
| [`🚧_zotero-use/`](🚧_zotero-use/README.md) (in German) | **Connecting Claude directly to one's own Zotero library** — creating new entries with a PDF, searching metadata and full text in a targeted way, managing collections. So far an idea on record along with its researched architecture, not yet a skill. |

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

**Which languages a skill is available in differs from case to case.** Most of them exist here in German only; their files are then simply called `SKILL.md`, `README.md` and `CLAUDE-snippet.md` and are copied unchanged. Only where there are several versions do `SKILL.md` and `CLAUDE-snippet.md` carry a language marker in front of the extension — `SKILL.de.md`/`SKILL.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Exactly one language version is installed then, and the chosen SKILL version is called `SKILL.md` at the target location — whether renamed or additionally placed makes no difference; Claude Code recognizes that name and nothing else. `README.md` is the exception: with several versions it carries **no** marker for the German version, only the English one is called `README.en.md` — GitHub and GitLab, when browsing a folder, automatically display only a file named exactly `README.md`; a language marker would prevent that (see `implementation_doku.md`, chapter 5.1, for details). Which language version to pick follows from the language used in the chat, whereby the English version should as such be compatible with every chat language.

The folder name is the same in all versions and never carries a marker; the same holds for the skill name in the frontmatter and hence for the `/<skill-name>` invocation.

### Installation

1. **Choose the target location (level of effect).** A skill applies either to all of the user's projects or to a single one:


   | Location | Path                                     | Applies to                |
   | -------- | ---------------------------------------- | ------------------------- |
   | Personal | `~/.claude/skills/<skill-name>/SKILL.md` | all of the user's projects |
   | Project  | `.claude/skills/<skill-name>/SKILL.md`   | this project only         |
2. **Copy one complete language version of the folder.** The folder here already has exactly the structure it will have at the target location and keeps its name. All files of the chosen language come along — README and `CLAUDE-snippet` included; their date lines later show which state the installation is from. **Mandatory is only the name `SKILL.md`:** Claude Code recognizes no other, a `SKILL.de.md` on its own is not a skill. Whether the chosen version is renamed for that or additionally placed under this name makes no difference; likewise a `README.en.md` may become `README.md` in an English installation.
3. **Adopt the silent trigger, if there is one.** If the folder contains a `CLAUDE-snippet` file, its content **below the separator line** is taken over into the `CLAUDE.md` of the target location — for a personal skill into `~/.claude/CLAUDE.md`, for a project skill into that project's `CLAUDE.md`. The text above the separator line is the instruction for doing so and is not copied along. The snippet file itself stays at the target location — in the language its content was adopted in: only the `CLAUDE.md` is effective, the file beside it is the reference copy from which one can later read off whether the adopted trigger still matches the state of the source.

The skill's `README` belongs at the target location too: it is the skill's user documentation, and the `SKILL.md` may point to it for reasoning when questions come up — without it, answers to why-questions come out thinner.

**None of this is dogma.** Installation is the user's business; Claude supports it but does not police it. Neither is it checked unasked whether an installation is complete or up to date, nor whether a `CLAUDE.md` matches the snippet shipped alongside. Checking and reporting happen only when the user explicitly asks for it.

Without step 3 the skill still works — but only if it is invoked explicitly with `/<skill-name>`, or if the AI has become sufficiently aware of the skill through its description.

### When adjusting a trigger

Three rules — two of them from measurements rather than taste, the third from Anthropic's own guidance:

**The skill's `description` decides first.** It begins with the main use case and uses the words a user would say unprompted. Putting a classification in front of it ("Test skill…", "Internal version…") or using project-internal jargon that appears in no request can render the trigger ineffective — measured: the very same trigger text fired with a good description and did not with a weak one.

**A trigger should be bound to an event or an action,** not merely to a property of the task. "Keep an eye on whether this task is complex" does not carry itself; "before you change a file for the first time, check …" or "if a file turns up that you have not touched, then …" fire reliably. The test series behind this are in `implementation_doku.md`, chapter 3.

**The `description` is written in the third person.** It describes the skill — "Translates documents …", "Use as soon as …" — and addresses nobody, neither Claude nor the user. This is not a matter of style: the description is injected into the system prompt, and a shifting point of view disturbs the selection among many skills there. Anthropic says so explicitly — *"Always write in third person […] inconsistent point-of-view can cause discovery problems"* ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## 4 Open points of the project

The upcoming steps and their order are kept in the **[roadmap](fahrplan.md)** (in German). What is finished on an individual skill — and what is planned there but not yet on the agenda — is stated in that skill's own `README.md` in its folder.

## License

All skills in this directory are under **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — the waiver of all rights as far as legally possible. That means:

- **Use without any condition** — private, commercial, in closed as well as in open projects.
- **No attribution needed.** Whoever wants to may name the source; nobody has to.
- **Freely modifiable and redistributable**, in modified form and under another name as well.
- **No obligation to disclose changes** or to give them back.
- **No license text has to be passed on** — unlike MIT or Apache-2.0, both of which demand attribution and the passing on of the license text.
- **No warranty and no liability.** Whatever these skills bring about is the responsibility of whoever employs them.

Anthropic makes no stipulations about the licensing of skills you write yourself, and the skill format is an open standard without conditions of its own. Anthropic's own skills repository uses Apache-2.0 for the open-source skills. CC0 is therefore a deliberate choice here, not a requirement — and the more far-reaching one: Apache-2.0 demands attribution and the passing on of the license text, CC0 does not.
