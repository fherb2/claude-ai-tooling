# temp-debug-code — Marking of temporary debug code

*Last updated: 2026-08-29*

**✅☑ Finished and usable.** Instructions complete, frontmatter set, silent trigger present, German and English version available.

**Gives every line that comes into being purely for tracking down a fault a fixed, searchable mark** — inserted debug and `print` output as well as original code disabled for the duration of the search. All marks begin with the same character sequence, so a single search run finds, without exception, every change that came into being for debugging. The entire purpose rests on that: the original state stays fully restorable — without memory and by someone who was not there.

The second part of the skill is the cleaning up: before a cause found is reported or the actual correction written, Claude checks whether debug code is still standing in the source — including code from an earlier task — and either removes it or puts it to the user.

**Not** meant is debug code intended to stay in the source permanently: output behind a debug flag, behind a log level or behind a configuration variable. That is regular program code, is not marked, and follows the usual rules of the project.

**The rules bind Claude, not the user.** They apply to debug code that Claude writes. Markings found in existing code are not measured against them: the user marks as they like and gets no remark about a deviating notation. Claude searches for foreign leftovers only when asked to — and then every place found is settled with the user individually before anything changes.

## Installation

1. **Choose the target location.** The skill applies either to all of the user's projects or to a single one:

   | Location | Path                                 | Applies to                 |
   | -------- | ------------------------------------ | -------------------------- |
   | Personal | `~/.claude/skills/temp-debug-code/`  | all of the user's projects |
   | Project  | `.claude/skills/temp-debug-code/`    | this project only          |

2. **Copy one language version of the folder `temp-debug-code/`.** `SKILL` and `CLAUDE-snippet` each exist in two versions — `SKILL.de.md`/`SKILL.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. All files of the chosen language come along, README included. The chosen SKILL version is called `SKILL.md` at the target location — whether renamed or additionally placed makes no difference; Claude Code recognizes that name and no other. The date lines later show which state the installation is from.

3. **Adopt the silent trigger.** The content of the `CLAUDE-snippet.md` — the one matching the chosen language version — goes **below the separator line** into the `CLAUDE.md` of the target location: for a personal installation into `~/.claude/CLAUDE.md`, for a project installation into the project's `CLAUDE.md`. The italic text above the separator line is not copied along. The snippet files stay at the target location; only the `CLAUDE.md` is effective, their date lines show the state of the adopted trigger.

   Without this step the skill only takes effect when called explicitly with `/temp-debug-code`. That matters especially here: the cause is Claude's own action — the user asks "why does this come out as 3?", and the decision to add a `print` line is Claude's. There is no request the `description` could be matched against.

## Details

**The marks.** Five of them, to be kept character by character: ` @@~DEBUG >>label<< ~@@ ` on every individually inserted debug line, ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` on every disabled original line, ` @@~DEBUG: START >>label<< ~~~~~~~~~~~~@@ ` and ` @@~DEBUG: END >>label<< ~~~~~~~~~~~~@@ ` around blocks of five debug lines or more, plus the separator line ` @@~~~~~~~~~~~~~~~~~~~~~~~~@@ ` before every START and after every END. The exact cases and examples for Python, C-like languages and shell are in the `SKILL.md`.

**Why `@@~` is the frame.** The frame character must not collide with the comment marker of any language, must not be a regex metacharacter, must have no special meaning in the shell, and must practically never occur in source code — what is searched for is `@@~`, not `@@` on its own. Checked and rejected: `%%`, because `%%~` is common syntax in Windows batch files (`%%~dp0`); `!!`, because an interactive Bash resolves `!!` as history expansion even inside double quotes, so the self-test command would silently do something else; `||`, because `|` is a metacharacter and would force escaping; and `§`, because it does not exist on US keyboards. The two collisions of `@@` — Ruby's class variables and the hunk headers in diffs — do not hit the search pattern, because no tilde ever follows there. Whoever adapts the skill should therefore not swap the frame for a more convenient character.

**Why the tildes never come in pairs.** Two tildes are strikethrough in Markdown, and comments and docstrings could contain Markdown. One tilde, or three and more, is therefore allowed; the number itself is pure optics and irrelevant to the search.

**The marks are the same in both language versions.** They are markers, not prose, and were deliberately not translated: otherwise a project in which both versions had been in circulation would no longer find its debug code with a single search run.

**Labels and nesting.** Every mark carries the label of its debugging effort between `>>` and `<<`. It is needed because debugging efforts come into being inside one another: a second begins in the middle of the first, and when the inner one is cleaned up it must stay recognizable which disabled line belongs to the outer one. Without a label that could only be guessed from the position in the code — and a wrong assignment reactivates original code that the still running effort had disabled. The damage then looks like a program fault, not like a cleanup fault. The label therefore names the question being pursued, not the place in the code: two efforts in the same function would otherwise get the same one.

**The self-test.** After the debug changes have been written, `grep -rn '@@~DEBUG' .` is run and the number of hits held against the number of changes: every block marking counts as two hits, every other marked line as one. If the numbers do not match, a mark is missing. For cleaning up, `grep -rn '@@~' .` is run instead — that pattern additionally finds the separator lines, which would otherwise be left behind.

**Original code is never deleted,** only commented out. The disabled line is the only reliable source for the way back — it stands in the search run, in the diff, and still stands there when somebody else cleans up.

**Cleaning up goes by task, not by age.** Debug code from the running task Claude removes on its own; debug code from a finished task it puts to the user. If the user declines, the same place comes up again only on a new day, in a new chat, or on an explicit request. **Nothing is decided by script:** the search run finds the marks; what happens at a place, Claude checks at that place itself — markings may be set completely differently from what the rules foresee.

**The anchor in the trigger.** The paragraph in the `CLAUDE.md` is bound to Claude's own action, and the sentence "even when the user has not spoken of debugging" is the part that does the work. Its second paragraph is the anchor for the cleaning up; without it the skill fires only on insertion and never on removal. When adapting it to a project both may be moved, but not left out.

## Status and open points

**Status:** instructions complete, frontmatter set, wording revised, silent trigger present, description in the third person. On 29 August 2026 the marks were recast completely — the frame `@@~` instead of the old double hash, a label per debugging effort, nesting, separator lines — and both language versions were carried along together. Testing at the target location will happen when the skill is needed there.

**Open:** the new form of the marks has never been in use. That does not make the skill unusable — its first use is at the same time its trial.
