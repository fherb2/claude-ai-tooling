# CLAUDE.md-Snippets

*Last updated: 2026-08-25*

*[Deutsche Fassung](README.md)*

Ready-made blocks of text for the instructions Claude carries with it permanently — for the `CLAUDE.md` of a local Claude Code installation (`~/.claude/CLAUDE.md`), where applicable in projects worked on with Claude Code (`<projekt>/.claude/CLAUDE.md`), and for the places where claude.ai takes instructions (in the account under General as well as in projects). Every block stands on its own: no order, no overall document, no claim to completeness. Whoever needs one copies it out; the rest stays where it is. Instruction areas in common-snippets.*.md may also be present in the other two files: there, the instructions are to be mixed under the corresponding heading.

## Not to be confused with `skills/`

In the component [`skills/`](../skills/README.en.md), some skill folders contain a file `CLAUDE-snippet.md` that looks like the same thing at first glance. It is something else: the **silent trigger** of one particular skill — a reference that has no effect without that skill, and which is therefore installed into `CLAUDE.md` together with it.

What is kept here is the opposite of that: instructions that take effect on their own and have no skill behind them. What belongs to a skill does not belong here — and the other way round.

## The three files

What separates them is the **place they take effect**, not the topic:

| File | Applies to | Because |
| ---- | ---------- | ------- |
| [`common-snippets.de.md`](common-snippets.de.md) · [`.en.md`](common-snippets.en.md) | claude.ai **and** a local Claude Code installation | The block is usable word for word in both environments. |
| [`claude.ai-snippets.de.md`](claude.ai-snippets.de.md) · [`.en.md`](claude.ai-snippets.en.md) | claude.ai only | The block names things that exist only there. |
| [`home-.claude-snippets.de.md`](home-.claude-snippets.de.md) · [`.en.md`](home-.claude-snippets.en.md) | local only, `~/.claude/CLAUDE.md` | The block names locations and paths on your own machine. |

Every file comes in two language versions — `.de.md` German, `.en.md` English. Both say the same thing; which one you take follows the language the user usually works in, so that Claude does not get its languages mixed up when answering.

**One topic can appear in several files**, and that is not an oversight. Memory is the example: `common-snippets` holds the question of **whether** knowledge about the user may go into memory at all — that one applies everywhere alike. The two environment-specific files hold the question of **where** — and the possible places do differ. Whoever needs both takes both.

## Use

Nothing here loads itself. A block takes effect only once its text sits at the target place.

**One block is always worth taking: "Precedence of the instruction levels" from `common-snippets`.** It settles which level holds when two instructions contradict each other — and that case arrives sooner than one expects. Without it, one of the two rules is otherwise picked arbitrarily, which shows up as a needless question or as surprising behavior. It is four lines long, costs hardly any context, and nothing can go wrong with it: it only orders what would have to be settled anyway.

1. **Choose the language version.** Exactly **one** gets inserted. Two would be a duplicate that drifts apart at the next change.
2. **Copy the block out along with its heading.** At the target place, the heading names the topic and keeps it findable later on.
3. **Adjust the heading level.** Here every block carries a first-order heading, because the file belongs to it alone. In a `CLAUDE.md` that has grown over time, it belongs at the level that fits the structure there.
4. **Merge identical topics.** If you take both the common *and* the environment-specific block on one topic, both belong under **one** heading at the target place — otherwise the same heading stands there twice.

## Status

The content of the files in this folder keeps growing every now and then. The project's main branch should always carry complete instructions, so that they are always released for use.

The user decides what to take from them:

## License

All blocks in this folder are under **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — the waiver of all rights as far as legally possible. That means:

- **Use without any condition** — private, commercial, in closed as well as in open projects.
- **No attribution needed.** Whoever wants to may name the source; nobody has to.
- **Freely modifiable and redistributable**, in modified form and under another name as well.
- **No obligation to disclose changes** or to give them back.
- **No license text has to be passed on** — unlike MIT or Apache-2.0, both of which demand attribution and the passing on of the license text.
- **No warranty and no liability.** Whatever these blocks bring about is the responsibility of whoever employs them.

The same choice as in the component [`skills/`](../skills/README.en.md) and for the same reason: a block of text that ends up in somebody else's `CLAUDE.md` should not leave any licensing obligations behind there.
