*Last updated: 2026-08-24*

*This file is not part of the skill. It holds the silent trigger that
activates the skill. When installing: copy everything below the separator
line into the `CLAUDE.md` of the target location; this file
stays there, only the `CLAUDE.md` is effective.
Without the trigger, the skill only runs when
`/correct-zaaack-md-editor-mistakes` is called explicitly.*

*The cause is nothing the user puts into words: they ask for a change to a
file, and nobody knows beforehand that damaged whitespace is sitting in it —
it is barely visible anyway, and in the case of the no-break space not at
all. There is no request the `description` could be matched against; the
wording is therefore bound to two of Claude's own actions, the first reading
or changing of a Markdown file and the commit. When adapting it to a project
the anchors may be moved, but not left out. The sentence about the memory is
the part that does the work against repetition: without it the check starts
afresh in every session — and that in a skill meant to work unnoticed in the
background.*

*Do not write into it that the file has to contain a table. The condition
sounds thrifty but tempts Claude into searching for tables first — exactly
the work the skill's tool does in a single pass.*

*The third paragraph — the standing authorization — has to sit here and must
not be left out, even though the skill body says the same thing. Measured on
24 August 2026 with Sonnet 5 and Opus 5: with the authorization in the skill
body alone, both models present a plan and repair nothing; with it here as
well, both repair at once and report afterwards. The reason is precedence — a
duty to present a plan sits in the `CLAUDE.md` and holds unconditionally,
while an authorization in the skill body comes up against it and loses.
Without this paragraph the trigger does fire, but the automation does not
happen.*

---

## Markdown tables: artifacts of a WYSIWYG editor

Before you read or change a Markdown file for the first time in a session,
and before you commit Markdown files, consult the skill
`correct-zaaack-md-editor-mistakes`. Some WYSIWYG editors swallow spaces in
tables when saving and replace others with no-break spaces; neither shows up
when reading, and nobody asks to have them looked for.

This repair is authorized once and for all: carry it out without asking and
do not put it up as a plan. It concerns whitespace inside table rows and
nothing else — no word, no punctuation. Report afterwards what you changed.

If the memory of this project already says whether it is affected, follow
that and do not ask again.
