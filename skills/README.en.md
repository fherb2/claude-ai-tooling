# Skills for Claude Code

*Last updated: 2026-08-30*

*[Deutsche Fassung](README.md)*

Reusable skills for Claude Code, claude.ai and Claude Desktop (Chat + Cowork), together with the triggers that fire them. This directory is the source — the skills are developed and maintained here. They only take effect once they are installed at their target location (chapter 3).

## 1 The skills one by one


| Skill                                                                            | Purpose                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`common-code-generation/`](common-code-generation/README.en.md)<br>✅☑ | **General rules for the cooperation on, and the carrying out of, writing and changing code, apart from code style rules**: e.g. no unrequested extension of the functional scope, careful use of processing time and memory |
| [`correct-zaaack-md-editor-mistakes/`](correct-zaaack-md-editor-mistakes/README.en.md)<br>✅☑ | **Finding and repairing damaged whitespace in Markdown tables** — spaces swallowed in front of inline code or bold text, and no-break spaces that defeat any search over the wording without being visible. Some WYSIWYG editors cause this on save. |
| [`parallel-sessions/`](parallel-sessions/README.en.md)<br>✅☑ | **Several Claude sessions at the same time in the same repository, separated via Git worktrees** — one workbench in its own worktree per session, central files via an infra branch, completion by squash merge; without an agreed model, settling Git write authority remains as the fallback. |
| [`pedantic-text-editing/`](pedantic-text-editing/README.en.md)<br>✅☑ | **Text editing with fidelity to detail** — every change presented individually for approval, not a character changed outside the approved spots, and afterwards the proof through the diff. For texts whose wording is itself the product; not for source code or documentation accompanying software. |
| [`temp-debug-code/`](temp-debug-code/README.en.md)<br>✅☑ | **Unambiguous marking of code added or changed for an ongoing debugging session only** — not for debug code meant to stay in the source permanently.                                                                                               |
| [`in-depth-online-literature-research/`](in-depth-online-literature-research/README.en.md)<br>✅☑ | **Thorough source and literature research that does not give up too early** — systematic variation of search terms, channels and search levels, mandatory verification of every search summary, and instead of "nothing found" a report on the search paths still open. |
| [`🚧_software-dev-doc-fh/`](🚧_software-dev-doc-fh/README.md) (in German) | **A documentation standard for planning before coding and for the running record of what was implemented** — what is being built, which decisions were taken and why this way and not another. Documentation accompanying a software project, as the basis for coding, for debugging and for the later closing and user documentation. |
| [`🚧_software-task-detection/`](🚧_software-task-detection/README.md) (in German) | **Recognizing that a request amounts to software to be written or changed** — even when it never uses words like "code" or "programming". So far an idea on record along with its measurements, not yet a skill.                                    |
| [`🚧_translation-task/`](🚧_translation-task/README.md) (in German) | **Translation of documents whose content is close to software development** — README files, concept and implementation documents, guides. Not tied to one direction of translation. |
| [`web-code-editing/`](web-code-editing/README.en.md)<br>✅☑ | **Editing code on claude.ai**: secure the sources completely (project knowledge sits as files under `/mnt/project/`), return changed files mechanically as downloads instead of re-dictating them, small changes as a before/replace scheme in the chat. For claude.ai only.                                                        |
| [`🚧_zotero-use/`](🚧_zotero-use/README.md) (in German) | **Connecting Claude directly to one's own Zotero library** — creating new entries with a PDF, searching metadata and full text in a targeted way, managing collections. So far an idea on record along with its researched architecture, not yet a skill. |

(✅ German version finished and usable · ☑ English version finished and usable · 🚧 in progress · ⚠️ with reservations)

## 2 Purpose

This project develops and maintains skills for general use with Claude (web and local, and on every level from user to project).

It introduces and implements a concept of "silent triggers" that allows even weaker models to start a skill very early out of the context.

On top of that, some skills are **split in two**: the `SKILL.md` then only settles whether the skill is to be applied at all, and loads the actual rules from a second file in the same folder once that is agreed. A skill firing on a situation in which it often turns out not to be needed thus costs only its settling page instead of its whole text.

The rules for this area, `skills/`, and the findings from the accompanying test series are in `skill-dev-doc.md`. This README describes only the result: what there is and how to use it. On top of that, every skill has a README file of its own carrying its particular notes and its current state of development.

## 3 Obtaining and installing skills

What skills are, how they are structured and how Claude Code loads them is described in the official documentation: **[Extend Claude with skills](https://code.claude.com/docs/en/skills)**. This README takes that as known.

**What is added here are silent triggers:**

The technique Anthropic provides fires a skill via its `description`: if it matches the request, the skill is loaded. That works well when the user asks for something the skill obviously covers. It does not work, or works poorly, when the trigger is an observation nobody in the chat puts into words — for instance that a second Claude instance, or the user, is working in the same repository while the chat holds the authority over commits. For such cases a skill comes with an additional paragraph for the `CLAUDE.md` of the target location, naming the condition and pointing to the skill. In this project it is called a **silent trigger**, because usually nobody invokes it explicitly for a task and nobody sees it: it works from the background, inside the AI's reasoning, without the user noticing anything. Its job is to make sure the skill takes effect as early as possible in cases where, without it, the AI would still treat the skill as too faint a match against its description and the task at hand.

Skills that need such a trigger carry a `CLAUDE-snippet` file for it; in the installation package it is called `CLAUDE-snippet.md`. Its content is adopted by hand — the one installation step no package can take off your hands.

**Which languages a skill is available in differs from case to case.** Where there are several versions, the files here in the repository carry a language marker in front of the extension — `SKILL.de.md`/`SKILL.en.md`, `rules.de.md`/`rules.en.md`. Which of them comes along is decided by the package you pick; the rename to `SKILL.md` that Claude Code presupposes happens at packing time. `README.md` is the exception in the repository: with several versions only the English one carries a marker (`README.en.md`), the German one is called `README.md` with no marker at all — GitHub and GitLab, when browsing a folder, automatically display only a file named exactly `README.md`; a language marker would prevent that (see `skill-dev-doc.md`, chapter 5.1, for details). Which language version to pick follows from the language used in the chat, whereby the English version should as such be compatible with every chat language.

The folder name is the same in all versions and never carries a marker; the same holds for the skill name in the frontmatter and hence for the `/<skill-name>` invocation.

### Installation

**A finished skill is installed from an archive, not copied together as a folder.** The archives sit in the `downloads/` subfolder of the skill in question, one per language and target world:

| Name | For |
| --- | --- |
| `<skill>_de_local.zip` | Claude Code, German version |
| `<skill>_de_web.zip` | claude.ai and Claude Desktop (Chat + Cowork), German version |
| `<skill>_en_local.zip` | Claude Code, English version |
| `<skill>_en_web.zip` | claude.ai and Claude Desktop (Chat + Cowork), English version |

Which combinations exist for a given skill at all is stated by the note after its status line; **the exact steps are in its own README.** The archive holds a folder named after the skill, and in it all files of the chosen language — `SKILL.md`, `README.md`, and where applicable lazily loaded rules files, scripts and `CLAUDE-snippet.md`. The sorting out and renaming that used to be handwork is taken off your hands by the package.

**In Claude Code** the archive is unpacked into `~/.claude/skills/` — then the skill applies to all of the user's projects — or into `.claude/skills/` in the project, then only there. **In claude.ai and Claude Desktop (Chat + Cowork)** it is uploaded in the application's management area for skills and then applies to the account.

**The silent trigger stays handwork.** If the package holds a `CLAUDE-snippet.md`, **everything below the separator line** goes into the `CLAUDE.md` of the target location, or into the application's instruction field. The italic text above it is the instruction for doing so and stays behind; the file itself stays put and is the reference copy, from whose date line one can later read off whether the adopted trigger still matches the state of the source.

Without this step the skill still works — but only when it is called explicitly with `/<skill-name>` or the AI has become sufficiently aware of it through the `description`.

The skill's `README` is in the package and belongs at the target location: it is the skill's user documentation, and the `SKILL.md` may point to it for reasoning when questions come up — without it, answers to why-questions come out thinner.

**None of this is dogma.** Installation is the user's business; Claude supports it but does not police it. Neither is it checked unasked whether an installation is complete or up to date, nor whether a `CLAUDE.md` matches the snippet shipped alongside. Checking and reporting happen only when the user explicitly asks for it.

### When adjusting a trigger

Three rules — two of them from measurements rather than taste, the third from Anthropic's own guidance:

**The skill's `description` decides first.** It begins with the main use case and uses the words a user would say unprompted. Putting a classification in front of it ("Test skill…", "Internal version…") or using project-internal jargon that appears in no request can render the trigger ineffective — measured: the very same trigger text fired with a good description and did not with a weak one.

**A trigger should be bound to an event or an action,** not merely to a property of the task. "Keep an eye on whether this task is complex" does not carry itself; "before you change a file for the first time, check …" or "if a file turns up that you have not touched, then …" fire reliably. The test series behind this are in `skill-dev-doc.md`, chapter 3.

**The `description` is written in the third person.** It describes the skill — "Translates documents …", "Use as soon as …" — and addresses nobody, neither Claude nor the user. This is not a matter of style: the description is injected into the system prompt, and a shifting point of view disturbs the selection among many skills there. Anthropic says so explicitly — *"Always write in third person […] inconsistent point-of-view can cause discovery problems"* ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## 4 Open points of the project

The upcoming steps and their order are kept in the **[work plan](../work-plan.md)** (in German). What is finished on an individual skill — and what is planned there but not yet on the agenda — is stated in that skill's own `README.md` in its folder.

## License

All skills in this directory are under **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — the waiver of all rights as far as legally possible. That means:

- **Use without any condition** — private, commercial, in closed as well as in open projects.
- **No attribution needed.** Whoever wants to may name the source; nobody has to.
- **Freely modifiable and redistributable**, in modified form and under another name as well.
- **No obligation to disclose changes** or to give them back.
- **No license text has to be passed on** — unlike MIT or Apache-2.0, both of which demand attribution and the passing on of the license text.
- **No warranty and no liability.** Whatever these skills bring about is the responsibility of whoever employs them.

Anthropic makes no stipulations about the licensing of skills you write yourself, and the skill format is an open standard without conditions of its own. Anthropic's own skills repository uses Apache-2.0 for the open-source skills. CC0 is therefore a deliberate choice here, not a requirement — and the more far-reaching one: Apache-2.0 demands attribution and the passing on of the license text, CC0 does not.
