---
name: correct-zaaack-md-editor-mistakes
description: Finds and repairs damaged whitespace in Markdown tables — spaces swallowed in front of an inline-code or bold delimiter, and no-break spaces (U+00A0) that defeat any search over the wording without being visible in the text. Some WYSIWYG Markdown editors cause this on save. Use as soon as a Markdown file is read or changed for the first time in a session, and before every commit that includes Markdown files, or when the user calls /correct-zaaack-md-editor-mistakes.
license: CC0-1.0
---

# Artifacts of the zaaack Markdown editor in tables

This skill's folder holds a `README.md`. It explains the editor, how the tools are built, how to set up the hook, and where the limits are. Read it when you need one of those — not beforehand.

## What this applies to

These rules apply to **every** Markdown file. They are not confined to software projects and presuppose no work on code.

Only table rows get damaged, in two ways: a space swallowed in front of inline code or bold text, and a no-break space (U+00A0) put in place of an ordinary one. The second is invisible and defeats any search over the wording — which is why it is not allowed, even where it would be harmless in substance. Which file is affected is not for you to establish; that is what the tools do.

## The procedure

If it has not been settled yet whether this project is affected, then check at the first opportunity: as soon as you read or change a Markdown file in a session.

**If you find artifacts:** repair them across the whole project, not only in the file that caught your eye. Report to the user the number of files and rows — not the individual places — and that you will be doing this on your own from now on, at every find and before every commit. Then put the finding on record.

**If you find none:** ask the user whether they use this editor as a matter of course, and whether you should check and repair without asking in future. Put their answer on record — **the refusal as well**. Without that you will ask again next time.

**If no hook is set up** — look in `.claude/settings.json` —, say so when you first report, and describe the setup to the user. The section "Verlässlichkeit: der Hook" of the `README.md` in this folder carries it, ready-made entry included. Only a hook makes the check before every commit reliable; this skill on its own merely gets loaded with some probability.

## Standing authorization

Once the user has agreed, or once you have found artifacts and reported the repair, you need no further consent for this repair — not even where you would otherwise put every file change up for a decision first. Report it instead of putting it up for a decision.

The authorization covers **whitespace inside table rows** and nothing else. No word, no punctuation, no rewording. Touching more means acting without authorization.

Two of the limits are enforced by the tools themselves. The third one nobody catches for you: **single-asterisk `*italic*` is not detected.** If such a place catches your eye, put it to the user instead of changing it yourself.

## The tools

Three Python files in this skill's folder. `md_table_artifacts.py` carries the rules and is only ever imported; the other two are the commands. Use them instead of searching yourself.

Always the same sequence, three separate calls. The only variable is the project path — give it as an **absolute** path, then the working directory does not matter:

```bash
# 1 findings
python3 "${CLAUDE_SKILL_DIR}/scan_md_tables.py" PATH

# 2 repair
python3 "${CLAUDE_SKILL_DIR}/scan_md_tables.py" PATH | python3 "${CLAUDE_SKILL_DIR}/fix_md_tables.py"

# 3 blank test
python3 "${CLAUDE_SKILL_DIR}/scan_md_tables.py" PATH
```

The scanner descends from `PATH` into every subdirectory by itself — one call, not one per folder.

Its output holds two lists. **`files`** is the work list, and it alone determines the exit code: 1 while there is something to do, 0 when there is not. **`notes`** holds what is reported but deliberately never repaired, and is **not** outstanding work. Look the notes over and put to the user whatever looks wrong among them.

**Step 3 must yield `"files": []` and exit code 0.** If it does not, the repair tool is broken: do not repeat the run, report it to the user.

If `SKIP` in `md_table_artifacts.py` does not fit this project, say so. If the tools fail to recognize something as an artifact that is one, report it and do not change it yourself.

## What you put on record

Record in the project memory whether this project is affected and the repair authorized — or that the user does not use the editor and wants no automatic repair. Word it as a finding about the project, not as a claim about the user.

The memory holds for this project only. If the user works with that editor everywhere, propose that they take the finding into their `~/.claude/CLAUDE.md`. Writing it there yourself is not allowed.
