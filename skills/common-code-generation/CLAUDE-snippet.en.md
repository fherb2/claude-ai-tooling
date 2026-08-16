*This file is not part of the skill. It holds the silent trigger that
activates the skill. When installing: copy everything below the separator
line into the `CLAUDE.md` of the target location, then delete this file.
Without the trigger, the skill only runs when `/common-code-generation` is
called explicitly.*

*The anchor ("before you write or change source code for the first time in a
session …") may be moved when adapting it to a project, but not left out. It
lies deliberately this early: the skill is a set of rules that applies from
the first line of code onward, and its body stays in the context for the rest
of the session once loaded — a late hit no longer rescues the decisions that
have already been made.*

---

## Rules for writing code

Before you write or change source code for the first time in a session,
consult the skill `common-code-generation`. This applies even when nobody
has mentioned code and the request sounds like a question — "why does the
script abort on large files?", "could you have a look at why the list stays
empty?" — because changed source code comes out of those too.
