---
name: pedantic-text-editing
description: Edits texts whose exact wording is itself the product — essays, applications, talks, letters, book chapters: proofreading, copy-editing, spelling, grammar, punctuation, phrasing. Presents every change individually for approval, changes not a single character outside the approved spots, and keeps the approvals under version control. Does not apply to source code, nor to texts that document software. Use before a text of that kind is changed for the first time in a session, or when the user calls /pedantic-text-editing.
license: CC0-1.0
---

# Pedantic text editing

## What this skill is for

For texts whose **wording is itself the product** — essays, applications, talks, letters, book chapters, expert opinions. Not for source code, and not for texts that follow a piece of software and document it; there this skill applies only when the user explicitly asks for it. What decides is not the subject of the text, and not the folder it sits in, but its role.

## First settle whether it is applied

- **If the user calls `/pedantic-text-editing`**, that is the consent. Do not ask, go straight to the last section.
- **Otherwise ask once** whether the text at hand should be worked on according to this skill. Until the answer comes, change nothing in it.
- **A refusal holds for the whole session.** Do not ask again, do not mention the skill again, do not read any further file of this skill. It is done for this session.
- If no such text editing is recognizably going on — software work, source code, documentation accompanying software — do not ask in the first place.

## If it does apply, load the rules

**Read `${CLAUDE_SKILL_DIR}/rules.en.md` in full and work by it from then on.** If no file of that name is there, look in the skill folder for whichever rules file exists — it may have been renamed during installation. The rules are there, not here. Until you have read them, change nothing in the text — not even a trifle.

This split is deliberate and does not get merged: the skill is loaded often without coming into play, and what it costs then is exactly this page. In such sessions the rules text stays out.
