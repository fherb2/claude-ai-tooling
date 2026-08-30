# common-code-generation — General rules for writing and changing code

*Last updated: 2026-08-30*

**✅ Finished and usable.** Instructions complete, frontmatter set, silent trigger present, German and English version available. — No difference in content between the version for claude.ai / Claude Desktop (Chat + Cowork) and Claude Code.

**Collects the general rules of cooperation when code is written or changed** — the kind of decisions that would otherwise have to be repeated in every `CLAUDE.md`: English identifiers in the source, no unrequested extension of the functional scope, careful use of processing time and memory. Names and optimizations are **proposed, not decided**; the decision stays with the user.

The rules apply as soon as code comes into being or is changed in a session — and from then on continuously, not only for the step that triggered them.

**Not** its subject is the obligation to submit a plan before changing a file and to wait for approval. That stays in the project's `CLAUDE.md`, because a skill only probably loads whereas a protective rule has to take effect reliably. Also not its subject: the structure of concept and implementation documentation, and the handling of temporary debug code.

## Installation

### Claude Code

1. **Download the package.** `downloads/common-code-generation_en_local.zip`

2. **Unpack it.** The archive contains a folder `common-code-generation/` with all the files. Unpack it into `~/.claude/skills/` — then the skill applies to all projects — or into `.claude/skills/` in the project, then only there. An existing folder of the same name is replaced; nothing old is left behind.

3. **Adopt the silent trigger.** You have to do this by hand. Claude then recognizes more easily from the context whether the skill should be loaded. To do it: from `CLAUDE-snippet.md`, **everything below the separator line** goes into the `CLAUDE.md` of the chosen location. The italic text above it stays behind; the file itself stays in the skill folder and shows by its date line which state the adopted trigger is from.

   Without this step the skill only takes effect when called explicitly with `/common-code-generation`.

### claude.ai and Claude Desktop (Chat + Cowork)

1. **Download the package.** `downloads/common-code-generation_en_web.zip`

2. **Upload it.** Upload the archive in the application's management area for skills. The skill then applies to your account — not to your organization, and not at the same time in Claude Code.

3. **Adopt the silent trigger.** You have to do this by hand. Claude then recognizes more easily from the context whether the skill should be loaded. To do it: from `CLAUDE-snippet.md` in the archive, **everything below the separator line** goes into the instruction field — globally for the account or for the single project.

   Without this step the skill only takes effect when called explicitly with `/common-code-generation`.

Both packages carry the same content — the skill does not differ between the target worlds. They are separate only so that the name says where the archive belongs.

## Details

**Language and naming.** Everything in the source — identifiers, comments, docstrings — is written in English. Self-chosen names are put to the user for a decision in a clearly arranged form; short and apt beats long, and the project's code style rules take precedence. If the user wants to break them, they are told so — but they have the last word.

**No unrequested functional scope.** Only what the task strictly requires gets written. Nice-to-have functions and quality improvements are **proposed** early and added afterwards, not built in silently. The functional scope already realized is never extended without prior agreement.

**Ranking of resources.** Processing time (above all in loops, in frequently called functions and on I/O), then main memory, then mass storage. Where optimizations conflict, the user decides the priority.

**Check optimizations against reality.** Before a proposal is made, two questions have to be answered: does it pay off in the actual use case — measured also against the increased likelihood of building in undetected errors? And is its effect relevant at all across the application as a whole? Where knowledge about usage, hardware and the intended final state is missing, the answer is to ask, not to guess.

**Prior knowledge in loops.** Where several exit criteria occur in a loop, they are ordered by prior knowledge about the data so that on average the loop exits early. Part of that is telling the user that the compiler reorders the machine code anyway, and that this can only be ensured through directives or arguments.

**Why the anchor lies this early.** The skill is not a procedure with a starting moment, but a set of rules that applies continuously from the first line of code onward. Because its body stays in the context for the rest of the session once loaded, only the earliest hit counts (Vorgaben, chapter 2.1). The moments named in the skill text itself — naming, proposing, deciding — would come too late. When adapting it to a project the anchor may be moved, but not left out.

**And the obligation to plan stays outside,** tempting as it looks to pull it in here: a trigger is probabilistic, a protective rule has to take effect reliably.

**On its origin.** The text comes from a `CLAUDE.md` of the user. Revised on 16 August 2026: the previously separate role words "Entwickler" and "Anwender" were dropped — there is only the user now, the person in the chat (Vorgaben, chapter 7). The sections on operating ergonomics and tone went with them, and the silent trigger lost its second condition: it was also meant to fire as soon as the application contained a frontend of its own or delivered data to an external one. As long as ergonomics remains outside the scope of this skill, the trigger has only the anchor at the first contact with code. The English version was created the same day as a translation of the German one.

## Status and open points

**Status:** instructions complete, frontmatter set, silent trigger present, description in the third person. Keep an eye on whether adjustments turn out to be necessary while using it; testing at the target location will happen when the skill is needed there.

**Open:** nothing at present.
