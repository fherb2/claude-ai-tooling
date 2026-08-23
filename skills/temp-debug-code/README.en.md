# temp-debug-code — Marking of temporary debug code

**✅☑ Finished and usable.** Instructions complete, frontmatter set, silent trigger present, German and English version available.

**Gives every line that comes into being purely for tracking down a fault a fixed, searchable mark** — inserted debug and `print` output as well as original code disabled for the duration of the search. All marks begin with the same character sequence, so a single search run finds, without exception, every change that came into being for debugging. The entire purpose rests on that: the original state stays fully restorable — without memory, by someone who was not there, and by script if need be.

The second part of the skill is the cleaning up: before a cause found is reported or the actual correction written, Claude checks whether debug code is still standing in the source — including code from an earlier task — and either removes it or puts it to the user.

**Not** meant is debug code intended to stay in the source permanently: output behind a debug flag, behind a log level or behind a configuration variable. That is regular program code, is not marked, and follows the usual rules of the project.

## Installation

1. **Choose the target location.** The skill applies either to all of the user's projects or to a single one:

   | Location | Path                                 | Applies to                 |
   | -------- | ------------------------------------ | -------------------------- |
   | Personal | `~/.claude/skills/temp-debug-code/`  | all of the user's projects |
   | Project  | `.claude/skills/temp-debug-code/`    | this project only          |

2. **Copy the folder `temp-debug-code/` under its unchanged name and choose the language version.** `SKILL.md` and `CLAUDE-snippet.md` each exist in two versions — `SKILL.de.md`/`SKILL.en.md`, `CLAUDE-snippet.de.md`/`CLAUDE-snippet.en.md`. Only the desired one comes along, and its language marker is dropped in the process: `SKILL.en.md` becomes `SKILL.md` at the target location. If the marker stays, Claude Code will not find the skill. The German `README.md` already carries no marker; only those who want the English version rename `README.en.md` to `README.md` at the target location.

3. **Adopt the silent trigger.** The content of the `CLAUDE-snippet.md` — the one matching the chosen language version — goes **below the separator line** into the `CLAUDE.md` of the target location: for a personal installation into `~/.claude/CLAUDE.md`, for a project installation into the project's `CLAUDE.md`. The italic text above the separator line is not copied along. The snippet file is then deleted at the target location, so that the trigger does not exist twice.

   Without this step the skill only takes effect when called explicitly with `/temp-debug-code`. That matters especially here: the cause is Claude's own action — the user asks "why does this come out as 3?", and the decision to add a `print` line is Claude's. There is no request the `description` could be matched against.

## Details

**The marks.** Four of them, to be kept character by character, each with a leading and a trailing space: ` # DEBUG # ` on every individually inserted debug line, ` # DEBUG: ORIGINAL # ` on every disabled original line, ` # DEBUG: START ------------ # ` and ` # DEBUG: END ------------ # ` around blocks of five debug lines or more. The exact cases and examples for Python, C-like languages and shell are in the `SKILL.md`.

**Why two hashes stand in a row.** The `#` at the beginning and the end of a mark is part of the mark, not the comment marker of the language. In Python it therefore meets a second `#`. That looks like a mistake but is the reason why the mark reads identically in every language and a single search pattern suffices. Whoever adapts the skill should not simplify this apparent duplication away — that is what would cost the language independence.

**The marks are the same in both language versions.** They are markers, not prose, and were deliberately not translated: otherwise a project in which both versions had been in circulation would no longer find its debug code with a single search run.

**The self-test.** After the debug changes have been written, `grep -rn " # DEBUG" .` is run and the number of hits held against the number of changes: every block marking counts as two hits, every other marked line as one. If the numbers do not match, a mark is missing.

**Original code is never deleted,** only commented out. The disabled line is the only reliable source for the way back — it stands in the search run, in the diff, and still stands there when somebody else cleans up.

**Cleaning up goes by task, not by age.** Debug code from the running task Claude removes on its own; debug code from a finished task it puts to the user. If the user declines, the same place comes up again only on a new day, in a new chat, or on an explicit request.

**The anchor in the trigger.** The paragraph in the `CLAUDE.md` is bound to Claude's own action, and the sentence "even when the user has not spoken of debugging" is the part that does the work. Its second paragraph is the anchor for the cleaning up; without it the skill fires only on insertion and never on removal. When adapting it to a project both may be moved, but not left out.

## Status and open points

**Status:** instructions complete, frontmatter set, wording revised, silent trigger present, description in the third person. The English version was created on 17 August 2026 as a translation of the German one. Testing at the target location will happen when the skill is needed there.

**Open:** nothing at present.
