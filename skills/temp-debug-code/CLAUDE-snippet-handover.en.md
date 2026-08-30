*Last updated: 2026-08-30*

*This file is not part of the skill. It carries the silent trigger for
environments without direct access to the file tree — claude.ai and Claude
Desktop (Chat + Cowork). For Claude Code, `CLAUDE-snippet-local.en.md`
applies instead; only ever one of the two is adopted. When installing: copy everything below the
separator line into the instruction field of the target location — globally
for the account or per project. Without the trigger the skill runs only on
an explicit `/temp-debug-code` call.*

*The cause here is a different one than in Claude Code: Claude inserts
nothing itself but proposes it to the user. The wording therefore binds to
the proposal, not to the execution. The sentence "even when the user has not
spoken of debugging" is the part that does the work here too — they ask "why
does this come out as 3?", and that a probe follows from it is Claude's
decision. The second paragraph makes sure the question about marking is
asked once, before the user enters the first line by hand; afterwards it is
too late.*

---

## Temporary debug code

As soon as you propose a code change to the user that serves only to track
down a fault — a `print` or log output, a fixed test value, a skipped check,
a line commented out for testing — consult the skill `temp-debug-code`
first. This
holds even when the user has not spoken of debugging: the cause is your
proposal, not their request.

The skill first settles whether such lines are to be marked at all — the
user decides that, because they enter them and take them out again. Settle
it before you give them the first change, not once several are already
standing in the source.
