# temp-debug-code — Marking of temporary debug code

*Last updated: 2026-08-30*

*[Deutsche Fassung](README.md)*

**✅☑ Finished and usable.** Instructions complete, frontmatter set, silent triggers for both environments present, German and English version available. — With differences in content between the version for claude.ai / Claude Desktop (Chat + Cowork) and Claude Code.

**Gives every line that comes into being purely for tracking down a fault a fixed, searchable mark** — inserted debug and `print` output as well as original code disabled for the duration of the search. All marks begin with the same character sequence, so a single search run finds, without exception, every change that came into being for debugging. The entire purpose rests on that: the original state stays fully restorable — without memory and by someone who was not there.

The second part of the skill is the cleaning up: before a cause found is reported or the actual correction written, Claude checks whether debug code is still standing in the source — including code from an earlier task — and either removes it or puts it to the user.

**Where Claude does not reach the files itself** — on claude.ai and in Claude Desktop (Chat + Cowork) — a second subject comes in: which probe runs where, and how it is handed to the user. There it is also **their** decision whether anything is marked at all, because they enter the lines and take them out again.

**Not** meant is debug code intended to stay in the source permanently: output behind a debug flag, behind a log level or behind a configuration variable. That is regular program code, is not marked, and follows the usual rules of the project.

**The rules bind Claude, not the user.** They apply to debug code that Claude writes or proposes. Markings found in existing code are not measured against them: the user marks as they like and gets no remark about a deviating notation. Claude searches for foreign leftovers only when asked to — and then every place found is settled with the user individually before anything changes.

## Structure

The skill is split so that a session only carries the instructions that apply to the situation at hand:

| File | Content | When loaded |
| --- | --- | --- |
| `SKILL.md` | Scope · the project's rules come first · the environment question · the branch | always |
| `rules-local.en.md` | Claude does everything itself: marking duty, self-test, cleaning up, the way back | with direct file access |
| `user-choice.en.md` | Short version with an example, so the user can decide | when Claude works through the user |
| `rules-handover.en.md` | Where the probe has to run, how it stays small, how it is handed over | likewise, in every case |
| `marks.en.md` | The marks themselves: five marks, three cases, nesting, labels | from either rules file, once marking happens |

The marks stand **once per language**. They are character-identical in both environments; what differs is only who sets them and who runs the search.

## Installation

This skill has **two silent triggers** — one for each environment. Which one is the right one is taken off your hands by the package: it already contains the matching one, under the name `CLAUDE-snippet.md`.

### Claude Code

1. **Download the package.** `downloads/temp-debug-code_en_local.zip`

2. **Unpack it.** The archive contains a folder `temp-debug-code/` with all the files. Unpack it into `~/.claude/skills/` — then the skill applies to all projects — or into `.claude/skills/` in the project, then only there. An existing folder of the same name is replaced; nothing old is left behind.

3. **Adopt the silent trigger.** You have to do this by hand. Claude then recognizes more easily from the context whether the skill should be loaded. To do it: from `CLAUDE-snippet.md`, **everything below the separator line** goes into the `CLAUDE.md` of the chosen location. The italic text above it stays behind; the file itself stays in the skill folder and shows by its date line which state the adopted trigger is from.

   Without this step the skill only takes effect when called explicitly with `/temp-debug-code`.

### claude.ai and Claude Desktop (Chat + Cowork)

1. **Download the package.** `downloads/temp-debug-code_en_web.zip`

2. **Upload it.** Upload the archive in the application's management area for skills. The skill then applies to your account — not to your organization, and not at the same time in Claude Code.

3. **Adopt the silent trigger.** You have to do this by hand. Claude then recognizes more easily from the context whether the skill should be loaded. To do it: from `CLAUDE-snippet.md` in the archive, **everything below the separator line** goes into the instruction field — globally for the account or for the single project.

   Without this step the skill only takes effect when called explicitly with `/temp-debug-code`.

**Why the trigger matters especially here:** the cause is Claude's own action, or its proposal — the user asks "why does this come out as 3?", and the decision to add a `print` line is Claude's. There is no request the `description` could be matched against.

## Details

**The marks.** Five of them, to be kept character by character: ` @@~DEBUG >>label<< ~@@ ` on every individually inserted debug line, ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` on every disabled original line, ` @@~DEBUG: START >>label<< ~~~~~~~~~~~~@@ ` and ` @@~DEBUG: END >>label<< ~~~~~~~~~~~~@@ ` around blocks of five debug lines or more, plus the separator line ` @@~~~~~~~~~~~~~~~~~~~~~~~~@@ ` before every START and after every END. The exact cases and examples for Python, C-like languages and shell are in `marks.en.md`.

**Why `@@~` is the frame.** The frame character must not collide with the comment marker of any language, must not be a regex metacharacter, must have no special meaning in the shell, and must practically never occur in source code — what is searched for is `@@~`, not `@@` on its own. Checked and rejected: `%%`, because `%%~` is common syntax in Windows batch files (`%%~dp0`); `!!`, because an interactive Bash resolves `!!` as history expansion even inside double quotes, so the self-test command would silently do something else; `||`, because `|` is a metacharacter and would force escaping; and `§`, because it does not exist on US keyboards. The two collisions of `@@` — Ruby's class variables and the hunk headers in diffs — do not hit the search pattern, because no tilde ever follows there. Whoever adapts the skill should therefore not swap the frame for a more convenient character.

**Why the tildes never come in pairs.** Two tildes are strikethrough in Markdown, and comments and docstrings could contain Markdown. One tilde, or three and more, is therefore allowed; the number itself is pure optics and irrelevant to the search.

**The marks are the same in both language versions.** They are markers, not prose, and were deliberately not translated: otherwise a project in which both versions had been in circulation would no longer find its debug code with a single search run.

**Labels and nesting.** Every mark carries the label of its debugging effort between `>>` and `<<`. It is needed because debugging efforts come into being inside one another: a second begins in the middle of the first, and when the inner one is cleaned up it must stay recognizable which disabled line belongs to the outer one. Without a label that could only be guessed from the position in the code — and a wrong assignment reactivates original code that the still running effort had disabled. The damage then looks like a program fault, not like a cleanup fault. The label therefore names the question being pursued, not the place in the code: two efforts in the same function would otherwise get the same one.

**The self-test.** After the debug changes have been written, `grep -rn '@@~DEBUG' .` is run and the number of hits held against the number of changes: every block marking counts as two hits, every other marked line as one. If the numbers do not match, a mark is missing. For cleaning up, `grep -rn '@@~' .` is run instead — that pattern additionally finds the separator lines, which would otherwise be left behind. **Where Claude has no file access, the user runs these**; Claude gives them the pattern and the expected number of hits.

**Why the user decides when Claude cannot reach the files.** There every mark costs them work — they enter it and they take it out. So Claude puts the choice to them once, briefly and with an example, and keeps to their answer. If they decline, they are asked whether they would like a simpler marking; their proposal then holds unchanged and is not judged. Claude keeps no separate list of what to undo — the chat already carries it.

**Why the method steps appear only in the handover case.** With direct file access Claude decides for itself how to debug, how to start it and how to read the result; that is craft and needs no rule. Only once the user sits in between does the choice of probe become a question — because every step costs them work, and because Claude's own execution environment is not theirs.

**Original code is never deleted,** only commented out. The disabled line is the only reliable source for the way back — it stands in the search run, in the diff, and still stands there when somebody else cleans up.

**Cleaning up goes by task, not by age.** Debug code from the running task Claude removes on its own; debug code from a finished task it puts to the user. If the user declines, the same place comes up again only on a new day, in a new chat, or on an explicit request. **Nothing is decided by script:** the search run finds the marks; what happens at a place, Claude checks at that place itself — markings may be set completely differently from what the rules foresee.

**The anchors in the triggers.** Both snippets bind to Claude's own action, not to a request from the user — in one case to the insertion, in the other to the proposal. The sentence "even when the user has not spoken of debugging" is the part that does the work in each. The handover snippet additionally has the job of raising the marking question in time — namely before the user enters the first line by hand.

## Status and open points

**Status:** instructions complete, frontmatter set, two silent triggers, description in the third person. On 29 August 2026 the marks were recast completely — the frame `@@~` instead of the old double hash, a label per debugging effort, nesting, separator lines — and on 30 August the skill was split into a common part and two environment branches. Both language versions came into being together.

**Open:** the new form of the marks and the split have never been in use. That does not make the skill unusable — its first use is at the same time its trial. Untested in particular is whether an uploaded skill on claude.ai actually pulls the files it refers to.

**Deliberately left open:** whether the skill is installed on claude.ai at all is a question of use, not a technical one. Its description costs permanent space in the skill listing there, whether it fires or not.
