# Rules of pedantic text editing

These rules hold from now on for the whole session and exclusively for the files that belong under section 2.

**A round** is one pass from presenting the findings through approval to the executed change including the counter-check — one findings file, one pair of commits. It is **not** a turn in the chat: a round may stretch over many messages and over several sessions, and not every finding has to be walked through together.

## 1 What is settled before the first step

1. **Which file or files** are being worked on (section 2).
2. **Which spelling rules and which variety** apply — say British or American English, or an official ruleset for another language. With several texts this may differ per text; record what holds for which.
3. **Whether and with what the course of work is versioned.** If the text lives in a Git repository, section 11 applies. If the user names another method, check whether you can operate it and then use that one. If there is none, point out **once per session** that tracking opens the way back in case of error, and work by the paragraph "Without version control" in section 11.
4. **Whether the starting state is clean** — no uncommitted changes to the text file. If it is not, no round begins: without a fixed starting point, both the record and the way back are worthless.
5. **How large a round may be.** Without another figure from the user: at most 30 places of change.

The answers hold for the session.

## 2 Which files belong

Only the files explicitly named apply. One exception: if it is recognizable that a text is spread over several files, or gets spread over them in the course of the work, those belong too — ask before you assign them. If it is not yet clear whether a new file is part of the same text, keep it in mind and watch it; until that is settled it is excluded.

If the user creates a file that does not fall under this exception, you do **not** ask. They must name it to you themselves. Since files are always added in coordination with you, they know at any time which ones belong and which they would have to name — which is why the procedure is safe even when you do not ask, and why you only need to act as described here.

## 3 Three classes of finding, three treatments

- **Rule violation** — unambiguously wrong by the agreed ruleset: spelling, grammar, punctuation, a missing word that makes the sentence ungrammatical. Goes into the correction list as a correction.
- **Matter of fact** — a number, date, name, cross-reference, a contradiction in the text, a doubtful claim. Is **never** corrected but presented as a question, separately from the correction list. Even when you believe you are sure.
- **Matter of taste** — phrasing, word choice, sentence rhythm, tightening, a word that would only make the sentence rounder. Only if the user has explicitly asked for it. Then in a category of its own, and the passage's statement must survive unchanged.

**Matters of fact come in two sorts, and only the first belongs to the mandate unasked.** *Formal* ones concern how a value is written — decimal mark, thousands separator, date format, the target of a cross-reference (section 5). They go into the correction list like any other finding. *Substantive* ones go beyond that: contradictions in the text, unclear statements, doubtful claims. Whether those are covered by the current mandate you ask first, unless it follows from the context — a substantive examination is usually given as a mandate of its own.

One row of the correction list belongs to exactly one class. Never bundle a change of taste with a correction in the same row — otherwise the user approves the rewritten half-sentence along with the comma, say.

## 4 Fidelity to detail: what never changes

**Outside the approved places, not a single character changes.** That is the purpose of this skill, and it stops at nothing that looks like an improvement.

None of this happens in passing:

- Re-wrapping paragraphs, evening out line lengths, normalizing whitespace, adding or removing blank lines, changing the end of the file.
- Converting quotation marks, apostrophes, hyphens and dashes, or ellipses — not even "merely typographically".
- Deleting hedges, intensifiers and modal particles. They carry meaning even where they look like filler.
- Merging or splitting sentences under the label of grammar.
- Aligning terms across the text. Unification is a separate, explicitly decided pass, not the side effect of a correction.
- Touching headings, numbering, list markers and formatting as long as they are not themselves the subject of an approved row.

Two rules about authority over the wording:

- **The convention recognizably kept up within the text takes precedence** over any outside preference. Someone who consistently uses an older or idiosyncratic spelling does not get silently modernized; ask once whether it should stay.
- **Where the ruleset permits both forms, no correction is due.** A permitted variant is not an error.

**Untouchable** — such places are reported when they catch your eye, never corrected: verbatim quotations, proper names, titles of works, bibliographic references, passages in another language, deliberately archaic or dialectal spots, code spans and links. What the user has decided here once stands afterwards in the glossary of the decisions file and is not put up for decision again (section 9).

## 5 Numbers, factual data and cross-references

Affected are values in tables, captions and examples, cross-references inside the text ("see section 4", "table 3", "p. 42"), bibliographic references, URLs and DOIs, values from outside sources, as well as equations together with their insertion points and captions.

- **The value itself is always a matter of fact** (section 3) — never change it, present it. Even when it looks obviously wrong.
- **The way a value is written** — decimal mark, thousands separator, space before the unit, date format — follows the convention kept up in the text. Deviations from it are a rule violation, but they go into the correction list as a category of their own and never share a row with a prose correction.
- **You do not check outside values against your memory.** Either the source is at hand, or it stays a question. A question settled once stands in the decisions file and is not asked again (section 9).
- **If an approved change shifts a numbering, a cross-reference or a page or line figure**, the consequent place is not changed along automatically. Report it and present it as a row of its own.
- **With figures**, the link, the caption and the description fall under these rules; the image itself does not. **With equations**, the content is a matter of fact, their captions and the references to them are prose.

## 6 How findings are presented in the chat

Structure the output by **place and category** — as intermediate headings, not as table columns. The table itself stays narrow, otherwise approving becomes an imposition:

| ID | Line |  | Change |
| --- | --- | --- | --- |
| 1 | 42 | Bef | `the the same day` |
|  |  | Aft | `the same day` |

**A finding gets as many table rows as it needs.** The first carries the ID, the line number and the before-fragment; the following ones leave ID and line number empty and carry the after-fragment and, where needed, the reason. The label sits in a **narrow column of its own** and abbreviated — `Bef`, `Aft`, `Rsn` — so that the text beside it starts at the same place throughout and the differences can be taken in at a glance. That column carries no header. **No `<br>` and no real newline inside a cell:** a real newline takes the table apart, and `<br>` is not rendered everywhere — in the Claude Code frontend it shows up as visible text (observed on the running system, 25 August 2026). Markdown has no cells spanning several rows; the empty cells are therefore the only form that looks the same everywhere.

- **The ID** runs consecutively within a round and is not reassigned. It is how the user addresses the rows.
- **The line number** is permitted and helpful, because the file stays unchanged until approval. Where one line holds a whole paragraph, the user finds the spot with their editor's search function — the before-fragment suffices for that.
- **`Bef` and `Aft`** appear like that in the label column, always in this order and with these abbreviations.
- **A reason** only where it is not obvious — then as a further row with `Rsn` in the label column.
- **For longer passages, no table.** There the label column falls away and the words are written out, because without columns nothing can be aligned. An itemized list serves better there: start every entry with `<ID> – <LINE NUMBER>`, then a line break, then "Before: ", and "After:" after a line break as well. Where many short passages are mixed with the occasional long one, interrupt the table for the long passage and resume it afterwards; the IDs run on across the interruption.
- **Show only as much text as the decision needs** — not the whole paragraph when three words will do.
- **At most 30 places of change per round**, unless the user has named another figure. Beyond that, split the work and say beforehand how you split it. Where the section you are in already implies the split, follow that.

**The length of the before-fragment follows the decision, not the file.** Two things the user must be able to do with it: find the spot in their text quickly, and rule on the change without having to gather the surrounding context themselves. The two together set the measure. Where the context on the spot does not suffice — or stretches over a longer stretch — add a reason instead of inflating the excerpt. The **stored** excerpt follows a different rule: it must be unique within the file (section 8). The two may differ in length.

Matters of fact (section 3) stand in a **list of their own** below the correction list, never inside it, always carry a reason, and are not presented as a table.

## 7 The approval

- The user approves by ID — individually, "all", or "all except 7 and 12". What is not approved is not carried out.
- **A rejected proposal moves into the decisions file and is not proposed again** as long as the passage is unchanged in its wording (section 9). This holds beyond the session. Only the user brings it back.
- If the user offers **wider latitude**, it holds only for the category named with it and the file named with it, holds for the session, and never covers a matter of fact or a change of taste. If the user limits the span of that latitude in their own words — say to a single task or a group of tasks — then the shortest span resulting from their words and from this rule together is the measure: never beyond the session, for instance, even when the task is not finished within it. The correction list does not fall away with it — it becomes the report **after** execution, and findings file and record under section 11 stay complete.

## 8 The findings file of a round

It sits **next to the text file** and is called `editing-findings_<basename of the text file>_<YYYY-MM-DD_hh-mm>.md`. If two rounds begin in the same minute, count the minute up. **The stem `editing-findings_` does not change with the language of this skill** — otherwise a later installed version would not find the earlier one's rounds. The same holds for the markers in the commit messages (section 11); free in their language are only the labels inside the file.

**The head stands above a `---` separator and carries the mandate** the findings came out of: which file was examined, which ruleset and variety applied, which classes were included — and explicitly **what was not examined**, such as substantive matters of fact under section 3. Below that, date and time. Only below the separator do the findings stand. The head is the part that later answers the question why a place did not catch anyone's eye back then; without it, that cannot be reconstructed.

One **block** per finding, not a table row. Reason: the text fragments must be exact to the character, and editors realign Markdown table rows on saving and eat whitespace doing it — a record that gets falsified unnoticed is no record. "Before" and "After" therefore sit in code blocks of their own, which preserve whitespace:

```markdown
### 1 — line 42 — spelling — approved

Before:

    the the same day

After:

    the same day

Reason: word doubled.
```

- **The before-fragment is verbatim and unique within the file.** If it is not, extend it until it is.
- The file holds the **approved** state, including the rejected entries with their decision.
- **It is not deleted by itself.** It may go once its durable parts stand in the decisions file (section 9). If the user orders it deleted, check that first and enter what is missing, rather than deleting and losing it.

## 9 The decisions file

It is called `editing-data_<basename of the text file>.md`, sits next to the text file, grows with the work, and is **never** deleted. It is the counterpart to the findings file: the findings file is one round, the decisions file is the memory. Four sections:

- **Untouchable** — the glossary: the wording, its class (quotation, proper name, title of a work, bibliographic reference, passage in another language or in dialect) and the decision.
- **Settled matters of fact** — the place in its wording, the question, the user's answer.
- **Rejected proposals** — the before-fragment and what was proposed and rejected.
- **Log** — one line per round: the head of the findings file, the time of the examination, and the byte size of the examined file at that time. Binding for the state of the text are the round's commits (section 11); the byte size is a reading aid for a human, not proof.

**It is written at the end of every round**, not first at cleanup time. Otherwise a cleanup at the wrong moment deletes findings that were never digested.

Three rules carry the procedure:

- **The key is the wording** — never the line number, never the ID. If the passage changes later, the entry no longer applies, and the same question may be asked again: it is then a different place. That is why the IDs stay local to their round and need no memory beyond it.
- **An entry changes the default, not the reporting.** A glossary hit still goes into the correction list, but in a category of its own and with "do not change" as the default. The user thereby decides only where the glossary is wrong.
- **The most recent entry holds.** If a passage was declared untouchable in an earlier round and revised later, only the order says so. Search backwards from the newest.

**Which decisions files are consulted must be laid open.** Consulted are **all** `editing-data_*` files in the folder the text file sits in — whether two files really belong to one text or merely lie side by side cannot be told for certain from outside, and too narrow a cut would let the glossary fall apart. Tell the user which files you use; they can explicitly include or exclude individual ones.

**At the start of a round**, and sparingly: search **specifically for the wording** of each individual finding instead of reading the files in full — otherwise the effort grows with every round. If findings files of earlier rounds lie in the folder, say so and propose clearing them away.

## 10 Carrying it out

- Only the approved places are changed, each as an exact replacement of the before-fragment by the after-fragment. If the before-fragment is not found verbatim, change nothing and report it.
- **Prose is written with the file tools, never through a script using a heredoc, `sed` or `awk`.** Quotation marks and dashes in the text end the script's strings early, and the run breaks off in the middle of the file.
- No formatter, no linter, no tool that re-wraps or normalizes the file in passing.

## 11 The record and the counter-check

Two commits per round, in this order, each with the affected paths only (`git add -- <text file> <findings file> <decisions file>`) and never with the whole tree:

1. **The approved findings file**, the text file still unchanged in it. The subject carries the marker `Findings:` and the file name.
2. **The executed text change together with the continued decisions file.** The subject carries the marker `Text correction:`.

The markers make the rounds findable via `git log --grep`; the rest of the commit message follows the project's conventions. From the pair both things follow: the findings sit in the first commit, and the difference between the two is exactly what was carried out.

**The counter-check before the second commit is mandatory.** Look at `git diff -- <text file>` and hold the changed places against the approved IDs. If the count does not match, or if the diff shows something belonging to no approved ID: commit nothing, take the surplus change back, report it to the user. This is the only point at which an unnoticed change shows up at all — it is never skipped, not even for a single correction.

**Without version control:** make a copy of the text file in a working directory outside the project before the round and run the counter-check with `diff` against that copy. The record is then missing, the counter-check is not.

**After an executed change: propose a verification round** if the log of the decisions file shows several rounds since the last one. A verification round is no mode of its own but an ordinary round over an already edited text — the same classes, the same list, the same approval. Its own worth lies in finding what earlier corrections first brought in. If the user asks for substantially the same examination again, that **is** the verification round; a second one is then not needed. If you forget to propose it, nothing breaks — it is a reminder, not a condition.

## 12 Looking up earlier rounds

Never from memory. The first look goes into the folder, because that is where the findings files sit as long as they have not been cleared away — sorted by name they stand in chronological order, and **the newest holds**. If they have been cleared away, the history keeps them:

```bash
ls editing-findings_<basename>_*.md                     # rounds still present
git log --oneline --grep=Findings -- <text file>        # all rounds
git log --oneline --diff-filter=D -- <findings file>   # a round cleared away
git show <commit>^:<findings file>                     # its findings
git diff <commit>^ <commit> -- <text file>             # what it changed
```

If you need several states side by side, write them with `git show <commit>:<path>` into files of a working directory outside the project and compare them there. The project stays untouched by it.

## 13 Suspected mistakes of your own

If you notice a place that may have come out wrong from an earlier editing step, do not correct it silently. Look up first (section 12) what was approved back then — that round's findings say it more precisely than any recollection, and its head says what was examined at all. Then present the place for approval like any other finding.

## 14 Limits

- The skill presupposes files that can be read and written as text (`.md`, `.txt`, `.tex`, `.rst`, `.html` and the like). With `.docx`, `.odt` or PDF, say so: without lossless writing back there is neither fidelity to detail nor a record. Two ways remain — the user exports into a text format, or the correction list stays in the chat and they transfer it themselves. Which one is their decision.
- If the text exists only in the chat and in no file, the classes (3), the fidelity to detail (4) and the form of presentation (6) apply. Findings file, decisions file, commits and counter-check fall away, because there is no file. Say that once.
