*Last updated: 2026-08-30*

*This file is not part of the skill. It carries the silent trigger for
environments with direct access to the file tree — Claude Code. For
claude.ai and Claude Desktop (Chat + Cowork) a different trigger applies; it
sits in the package for those environments. Only ever one is adopted. When
installing: copy everything below the separator line into the `CLAUDE.md` of
the target location; this file stays there, only the `CLAUDE.md` takes
effect. Without the trigger the skill runs only on an explicit
`/temp-debug-code` call.*

*This trigger depends on a cause the user never says out loud: they ask "why
does this come out as 3?", and the decision to add a `print` line is
Claude's own. There is no request the `description` could be matched
against — the wording therefore binds to Claude's own action, and the
sentence "even when the user has not spoken of debugging" is the part that
does the work. When adapting it to a project it may be moved, but not left
out. The second paragraph is the anchor for the other half of the skill,
the cleaning up; without it the skill fires only on insertion and never on
removal.*

---

## Temporary debug code

As soon as you insert a line into the source code that serves only to track
down a fault — a `print` or log output, a fixed test value, a skipped check
— or as soon as you comment out existing code for testing, consult the skill
`temp-debug-code` first and keep to its marking rules. This holds even when
the user has not spoken of debugging: the cause is your own action, not
their request.

And before you report a cause you have found or write the actual
correction, check whether temporary debug code is still standing in the
source — including code from an earlier task. The skill settles which of it
you remove yourself and which you put to the user to decide.
