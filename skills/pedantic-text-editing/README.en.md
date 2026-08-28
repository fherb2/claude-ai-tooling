# pedantic-text-editing — text editing with fidelity to detail

*Last updated: 2026-08-28*

**✅☑ Finished and usable.** Instructions complete, frontmatter set, German and English version present. A silent trigger is not needed: the skill fires reliably through its `description` — confirmed in practice with Sonnet as well (25 August 2026) — or is called with `/pedantic-text-editing`.

**The skill confines the intervention in a text to exactly the places the user has approved — and afterwards proves that nothing else changed.** It applies to texts whose wording is itself the product: essays, applications, talks, letters, book chapters, expert opinions. The emphasis is not on finding errors — Claude can do that without a skill — but on bounding the intervention: that while a comma is corrected, no half-sentence gets rewritten in passing, no "presumably" deleted, no two sentences merged, no quotation marks unified across the whole text.

To that end it separates three kinds of finding — rule violation, matter of fact, matter of taste — and treats them differently, presents every change individually for approval, keeps the approved findings in a file, and after execution checks the diff against those findings. What the user has decided once is remembered durably by a second file, so that the same question does not come up again in every round.

**What it does not apply to:** source code, and texts that follow a piece of software and document it. There it takes effect only when the user explicitly asks for it. What decides is not the subject of the text, and not the folder it sits in, but its role. And it never takes effect on its own: after loading it asks once whether it should be applied, and a refusal holds for the whole session.

## Installation

1. **Choose the target location.** The skill applies either to all of the user's projects or to one only:

   | Location | Path                                      | Applies to                 |
   | -------- | ----------------------------------------- | -------------------------- |
   | Personal | `~/.claude/skills/pedantic-text-editing/` | all of the user's projects |
   | Project  | `.claude/skills/pedantic-text-editing/`   | this project only          |

2. **Copy one language version.** The folder name stays unchanged. One complete language version is copied:

   | German         | English        |
   | -------------- | -------------- |
   | `SKILL.de.md`  | `SKILL.en.md`  |
   | `rules.de.md`  | `rules.en.md`  |
   | `README.md`    | `README.en.md` |

   Plus **`apply_findings.py`** — the script is language-independent and belongs to both versions. Without it Claude would have to carry out every approved change one at a time, which makes a full round take very long.

   **Mandatory in this is only that the chosen SKILL version is called `SKILL.md` at the target location** — Claude Code recognizes no other name. Whether it is renamed for that or additionally placed makes no difference. Rules file and script keep their names: the `SKILL.md` points to the rules, those point to the script, and these pointers are the only way either gets loaded at all. Whoever renames carries the pointers along.

## Details

**Why the skill is split in two.** The `SKILL.md` carries only the scope, the settling step and the load instruction; the rules sit in the rules file. The reason is the context budget: a loaded skill stays in context for the rest of the session, and this one fires on a situation in which it often does not come into play after all. Without the split, every such session would drag the full rules text along. The extra file, by contrast, costs nothing as long as nobody points at it. Whoever merges the two files makes the skill expensive without making it better.

**The three classes are the actual protection against content drift.** A rule violation goes into the list as a correction. A matter of fact is never corrected but asked about, even when it looks obviously wrong — and it is split once more: how a number or a cross-reference is written belongs to the mandate, whereas a contradiction in the content first needs consent that it should be covered at all. Changes of taste come only on explicit instruction. Whoever softens this separation and throws "phrasing" together with "spelling" into one list has devalued the skill: the user then approves the rewritten half-sentence along with the comma.

**The counter-check is the point at which the skill takes effect at all.** Everything else is a request; only the diff against the approved findings turns it into a check. Hence two commits per round: first the approved findings with the text file still unchanged, then the executed change. The difference between the two is exactly what was carried out and can be held against the findings row by row. Without Git, a copy of the starting state takes the place of the first commit — the record is then missing, the counter-check is not.

**Two files with different lifetimes.** `editing-findings_<file>_<timestamp>.md` holds **one round**: in its head the mandate together with what was explicitly not examined, below that the findings. It may go later. `editing-data_<file>.md` is the **memory** and stays: the glossary of untouchable places, the settled matters of fact, the rejected proposals, and one log line per round. It is written at the end of every round and not first at cleanup time — otherwise a cleanup at the wrong moment deletes findings that were never evaluated. The key everywhere is the **wording**, never the line number and never the ID; if the passage changes, the entry no longer applies, and that is as it should be.

**That is why the IDs stay local to their round.** A numbering unique across a session would be error-prone for a language model and would need a counter surviving days and several sessions. The bar on re-proposing hangs on the wording in the decisions file instead — and thereby holds even longer than a session.

**The verification round** is no mode of its own but an ordinary round over an already edited text. Its own worth lies in finding what earlier corrections first brought in. It is proposed after an executed change, when the log shows several rounds since the last one — not at "the end of a round", because that is no observable moment: it comes about only once the user is done.

**Head and log are not decoration.** The head states what was **not** examined. That later answers the question why a place did not catch anyone's eye back then — without it, that cannot be reconstructed.

**The script `apply_findings.py` carries out the round, and it never guesses.** It reads the findings file — which is written and committed before any change anyway — and receives from Claude the list of approved IDs together with the text fragments that stood in the chat. The two are held against each other: a slipped selection shows up there instead of passing as a plausible-looking wrong change. The search uses the full before-fragment, the replacement only the part that actually changes — otherwise two findings sharing a context word would wrongly count as a conflict. If a place cannot be located unambiguously, the script writes **nothing at all**, not even the undisputed places: a half-changed file would be the worst outcome, because from then on the line numbers in the findings file describe a state that no longer exists.

**Measured against real rounds** (28 August 2026): four completed rounds from a running text project, 90 approved changes, replayed against their respective starting states — in all four cases the result was **byte-identical** with what had previously been made by hand. Three of the four rounds contained a pair of findings sharing a word; that is where the first version of the conflict check failed, and it is the origin of the split between search fragment and change core.

**The file holds blocks, not table rows.** The text fragments must be exact to the character, and some editors realign Markdown table rows on saving and eat whitespace doing it. In the chat the presentation is tabular, because that is easier to survey — and there a finding gets as many table rows as it needs, the follow-up rows leave ID and line number empty, and the label (`Bef`, `Aft`, `Rsn`) sits in a narrow column of its own so that the text beside it starts at the same place throughout. A `<br>` inside the cell would be the obvious way but is not rendered everywhere: in the Claude Code frontend it shows up as visible text (observed 25 August 2026, on the skill's first use).

**Displayed and stored excerpt are two things.** The displayed one follows the decision: the user must be able to find the spot and rule on it without gathering the context themselves. The stored one follows uniqueness within the file, because it is the template for an exact replacement. The two may differ in length; whoever collapses them gets either unclear proposals or replacements that slip.

**File names and commit markers are language-independent.** `editing-findings_`, `editing-data_`, `Findings:` and `Text correction:` appear verbatim like that in both versions. If they changed with the language, a later installed version would no longer find the earlier one's rounds. Free in their language are only the labels inside the files.

## State

**Status: complete.** Both language versions of `SKILL` and rules file are finished, as are both READMEs; the rules text has been talked through with the developer and approved. Trying it out in practice is concluded: round size, splitting, excerpt lengths and the form of presentation held up on a real text, and the operational findings (table format of the review list, handling of deferred substantive findings, cleanup reminder) have been worked into the rules text (25 August 2026). Since 28 August 2026 the script `apply_findings.py` carries out the changes, cross-checked against four real rounds (see “Details”). There are no open points.

**Deliberately left open:**

- **Spelling ruleset and variety** the skill does not fix but settles per text with the user. They belong to the text, not to the tool, and may differ across several texts.
- **The tracking method** is spelled out for Git only. If the user names another, the skill checks whether it can operate it. Deciding this in the target project is intentional.
- **The round size of 30 places of change** is a default the user may override — not a property of the procedure.
- **The cut of the decisions files.** All `editing-data_*` files of a folder are consulted, because it cannot be told for certain from outside whether two files belong to one text or merely lie side by side. A narrower cut would let the glossary fall apart. The user is told which files are used and can include or exclude individual ones.
- **A check script for the counter-check** is deliberately absent. An extra file in the skill folder costs no context, but a script would have to parse the findings file's format, and that is not yet tried out. Should the count comparison by eye prove too soft, it will come.
