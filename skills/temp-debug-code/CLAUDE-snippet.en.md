*Last updated: 2026-08-24*

*This file is not part of the skill. It holds the silent trigger that
activates the skill. When installing: copy everything below the separator
line into the `CLAUDE.md` of the target location; this file
stays there, only the `CLAUDE.md` is effective.
Without the trigger, the skill only runs when `/temp-debug-code` is called
explicitly.*

*This trigger depends on a cause the user never puts into words: they ask
"why does this come out as 3?", and the decision to add a `print` line is
Claude's own. There is no request the `description` could be matched
against — the wording is therefore bound to Claude's own action, and the
sentence "even when the user has not spoken of debugging" is the part that
does the work. When adapting it to a project it may be moved, but not left
out. The second paragraph is the anchor for the other half of the skill,
the cleaning up; without it the skill fires only on insertion and never on
removal.*

---

## Temporary debug code

As soon as you insert a line that serves nothing but tracking down a fault
— a `print` or log output, a fixed test value, a skipped check —, or as
soon as you comment out existing code for testing, consult the skill
`temp-debug-code` beforehand and keep to its marking rules. That holds even
when the user has not spoken of debugging: the trigger is your own action,
not their request.

And before you report a cause you have found or write the actual
correction, check whether temporary debug code is still standing in the
source — including code from an earlier task. The skill settles which of it
you remove yourself and which you put to the user for a decision.
