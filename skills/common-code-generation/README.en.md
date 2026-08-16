# common-code-generation — General rules for writing and changing code

English identifiers in the source code, no unrequested extension of the functional scope, careful use of processing time and memory, names and optimizations proposed rather than decided.

**Further notes:**

**Why the anchor lies this early.** The skill is not a procedure with a starting moment, but a set of rules that applies continuously from the first line of code onward. Because its body stays in the context for the rest of the session once loaded, only the earliest hit counts (Vorgaben, chapter 2.1). The moments named in the skill text itself — naming, proposing, deciding — would come too late.

Until 16 August 2026 the silent trigger carried a second condition: it was also meant to fire as soon as the application contained a frontend of its own or delivered data to an external one, "because additional rules then apply to the design of the operating concept". Those rules were dropped in the revision, which left the paragraph without a subject — it was deleted. As long as ergonomics remains outside the scope of this skill, the trigger has only one condition left: the anchor at the first contact with code.

**Status:**

Ready for use in principle. Keep an eye on whether further adjustments turn out to be necessary while using it.

Instructions complete, frontmatter set, silent trigger present. The text originates from a `CLAUDE.md` of the user and was carried over into a skill for this project. Revised on 16 August 2026: the previously separate role words "Entwickler" and "Anwender" were dropped — there is only the user now, the person in the chat (Vorgaben, chapter 7). The sections on operating ergonomics and tone went with them. The description has been in the third person since. Described in the overall README. The English version was created on 16 August 2026 as a translation of the German one.

**Trigger not measured.** The check described in chapter 4.2 of the Vorgaben has deliberately been deferred, not forgotten. What would need testing is the anchor against a request that sounds like a pure question and ends in a change to the code.

**Open:**

* Nothing at present. Testing at the target location will happen when the skill is needed there.
