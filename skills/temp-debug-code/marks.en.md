# The marks

This file describes the marking alone. It holds word for word whether you write the lines yourself or hand them to the user to enter — what differs is only who sets them and who runs the search. That is covered by the rules file that sent you here.

## What the marks are for

Every mark and every separator line begins with the same character sequence `@@~`. The number of tildes behind it is free and irrelevant to the search — used as a separator rule, however, it is sensibly repeated often, in proportion to the surrounding text, before the closing `~@@` follows.

**The marks are an aid, not an automatism.** They serve to recognize the changes for the way back and to find forgotten fragments. What actually happens during that way back is not decided by them.

Two search runs with separate jobs:

```
grep -rn '@@~DEBUG' .   # self-test: finds the marks
grep -rn '@@~' .        # cleaning up: additionally finds the separator lines
```

The entire purpose rests on that: at the end of the search the original state must be fully restorable — without memory, and by someone who was not there. An unmarked debug line is therefore not a blemish but a leftover nobody will ever find again.

For counting: every block marking counts as two hits (start and end), every other marked line as one.

## The five marks

Keep to the following five marks character by character.

| Mark | Where it goes | When |
| --- | --- | --- |
| `@@~DEBUG >>label<< ~@@` | at the end of the line, behind the comment marker | on every individually inserted debug line |
| `@@~DEBUG: ORIGINAL >>label<< ~@@` | at the start of the line, between comment marker and code | on every original line that was disabled |
| `@@~DEBUG: START >>label<< ~~~~~~~~~~~~@@` | its own comment line before the first debug line | with five or more debug lines in a row |
| `@@~DEBUG: END >>label<< ~~~~~~~~~~~~@@` | its own comment line after the last debug line | for the same block |
| `@@~~~~~~~~~~~~~~~~~~~~~~~~@@` | its own comment line | before every START and after every END |

Four things hold without exception:

- **Before every mark stands the comment marker of the language**, followed by a space. The mark itself begins with `@@~` and ends with one or more tildes and `@@`.
- **A space stands on either side of the label**, and one behind the closing `~@@` as well, before code or comment follows.
- **A mark without a label is incomplete.** The separator line is the only exception; it belongs to no effort.
- **Behind ` @@~DEBUG >>label<< ~@@ ` the line may be commented additionally.** Behind ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` it may not: there the disabled code follows unchanged.

This is what it looks like in the widespread languages when a single statement is swapped for another — the block marks and the separator line follow the same pattern.

Python:

```python
value = fallback()  # @@~DEBUG >>cache-bypass<< ~@@ bypass cache on purpose
# @@~DEBUG: ORIGINAL >>cache-bypass<< ~@@ value = cache.get(key)
```

C, C++, Java, JavaScript, Rust and relatives:

```c
int n = 0;  // @@~DEBUG >>size-probe<< ~@@
// @@~DEBUG: ORIGINAL >>size-probe<< ~@@ int n = compute_size(buf);
```

Shell:

```bash
path="/tmp/probe"  # @@~DEBUG >>path-probe<< ~@@
# @@~DEBUG: ORIGINAL >>path-probe<< ~@@ path="$(resolve_path "$1")"
```

If a language has no line comment, the mark goes into a block comment: `/* @@~DEBUG >>label<< ~@@ */`.

### The tildes in the marks

The chain of tildes is pure optics — it makes the mark stand out in the source. It does not count for finding anything; the search is for `@@~`.

When writing: at least one tilde in the line marks, at least twelve in the block marks, at least twenty-four in the separator line. Use more when that makes the delimitation stand out more clearly in relation to the surrounding code.

**Exactly two tildes are forbidden.** `~~` is strikethrough in Markdown, and comments and docstrings could contain Markdown. One tilde, or three and more, is allowed.

Three or more tildes at the **start of a line** open a code block in Markdown. Because the comment marker of the language stands before every mark, that cannot happen — one more reason not to leave it out.

## Labels

Every debugging effort gets a label: short, lower case, with hyphens. It stands in every mark of that effort between `>>` and `<<`.

**What it is for.** It says, on every single line, which effort that line belongs to. Only through it is it decidable, when cleaning up, what belongs together — even when two efforts lie inside one another and their lines alternate in the code. `grep -rn '>>label<<' .` pulls out one effort in full, no matter where its lines stand.

**What it names: the question you are pursuing — not the place in the code.** Two efforts in the same function would otherwise get the same label, and exactly the distinction it exists for would be lost. Only when the place is the shortest true description of the question does the label name it.

**Who chooses it: you.** You read the context of the program code and of the task and choose a sensible label from it, without asking. It is to be settled with the user only in visibly undecidable situations — above all in this one: when you cannot tell whether a new marking belongs to an effort already under way or is one of its own. That question is worth asking, because a wrong assignment reactivates someone else's code when cleaning up. Explain briefly to the user why you are asking in this case instead of deciding yourself.

**Two rules that hold together.** A label belongs to exactly one effort, and an effort has exactly one label. If you come across existing debug code whose effort you are continuing, you take over its label instead of inventing a new one.

## The three cases when inserting

Which case applies is decided by the number of inserted debug lines in a row. **"In a row" means: separated by at most one line not belonging to the debugging.** If the debug lines lie further apart, they are separate cases, and every group is counted for itself. If you are unsure whether a group crosses the limit of four lines, take the block form.

### Case 1: changing a single statement line for debugging

- The line in question is copied below the original.
- The original is disabled: comment marker at the start of the line, behind it ` @@~DEBUG: ORIGINAL >>label<< ~@@ `, behind that the unchanged code.
- The copy below it is changed and gets ` @@~DEBUG >>label<< ~@@ ` appended, as described in case 2.

### Case 2: up to four inserted debug lines

- Every inserted line gets a comment that begins with ` @@~DEBUG >>label<< ~@@ ` behind the comment marker.
- Original lines standing immediately before, after or between the debug lines that have to be disabled get ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` between comment marker and code.

### Case 3: five or more debug lines in a row

- Before the first debug line stands a comment line of its own, beginning with ` @@~DEBUG: START >>label<< ~~~~~~~~~~~~@@ ` behind the comment marker.
- After the last debug line stands a matching comment line with ` @@~DEBUG: END >>label<< ~~~~~~~~~~~~@@ `.
- Before the START line and after the END line comes a separator line ` @@~~~~~~~~~~~~~~~~~~~~~~~~@@ ` each.
- On the lines in between, the mark ` @@~DEBUG >>label<< ~@@ ` is dropped — with the exception described in the next section.
- **Disabled original lines keep their mark ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` inside a block as well.** Only ` @@~DEBUG >>label<< ~@@ ` is dropped. Without the ORIGINAL mark it is no longer recognizable inside the block which lines are to be reactivated — and that is exactly what matters when cleaning up.

### Nesting

A debugging effort may come into being inside another one; when debugging, that is the normal case and not the exception. Each carries its own label, and **the assignment follows from it alone, never from the position in the code.** A disabled line can sit physically inside the block of a foreign effort and still belong to the enclosing one.

From that follows the exception to case 3: **an inserted line belonging to a different effort than the block it stands in carries ` @@~DEBUG >>its-label<< ~@@ `** — inside a block as well, where the mark is otherwise dropped.

Where the END of one block and the START of the next meet, one separator line is enough.

## Original code is never deleted

Original code that has to give way for the search is **only commented out — never deleted and never overwritten.** That holds even when it is short and could easily be remembered. The disabled line is the only reliable source for the way back: it stands in the search run, it stands in the diff, and it still stands there when somebody else cleans up.

## What else to watch out for when changing

- At decision points — branches, case distinctions — and inside loops the marks matter especially, so that the original state stays restorable with minimal effort and in a way that can be followed.
- The indentation found, or that of the programming language in use, stays unchanged. Block marks and separator lines follow it too — **not** the nesting depth of the debugging efforts, and not the order in which they were inserted.

## Restoring a marked line

From a line with ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` both the mark **and** the leading comment marker disappear; afterwards the line stands there exactly as it did before the debugging. Inserted debug lines are removed entirely, and the separator lines of a block go with it.

## Example

Starting state:

```python
def load_config(path):
    raw = read_file(path)
    config = parse(raw)
    validate(config)
    return config
```

Case 1 and case 2 — one changed statement line, one inserted output, two disabled original lines:

```python
def load_config(path):
    # @@~DEBUG: ORIGINAL >>fixed-input<< ~@@ raw = read_file(path)
    raw = '{"mode": "test"}'  # @@~DEBUG >>fixed-input<< ~@@ fixed input instead of file
    config = parse(raw)
    print(f"config={config}")  # @@~DEBUG >>fixed-input<< ~@@
    # @@~DEBUG: ORIGINAL >>fixed-input<< ~@@ validate(config)
    return config
```

The self-test finds four hits here, matching four changed or inserted lines.

Case 3 — the same starting state, but five debug lines in a row, one disabled original line among them:

```python
def load_config(path):
    raw = read_file(path)
    config = parse(raw)
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    # @@~DEBUG: START >>config-shape<< ~~~~~~~~~~~~@@
    print(f"path={path}")
    print(f"raw bytes={len(raw)}")
    print(f"keys={sorted(config)}")
    print(f"mode={config.get('mode')}")
    # @@~DEBUG: ORIGINAL >>config-shape<< ~@@ validate(config)
    print("validate() skipped")
    # @@~DEBUG: END >>config-shape<< ~~~~~~~~~~~~@@
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    return config
```

The self-test finds three hits here: two for the block, one for the disabled original line inside it. The cleaning-up search finds five, because the two separator lines come on top.

Nesting — a second effort comes into being inside the first:

```python
def load_config(path):
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    # @@~DEBUG: START >>read-path<< ~~~~~~~~~~~~@@
    print(f"path={path}")
    # @@~DEBUG: ORIGINAL >>read-path<< ~@@ raw = read_file(path)
    raw = '{"mode": "test"}'
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    # @@~DEBUG: START >>parse-strict<< ~~~~~~~~~~~~@@
    print(f"raw head={raw[:40]!r}")
    print(f"raw bytes={len(raw)}")  # @@~DEBUG >>read-path<< ~@@
    # @@~DEBUG: ORIGINAL >>parse-strict<< ~@@ config = parse(raw)
    config = parse(raw, strict=False)
    print(f"keys={sorted(config)}")
    # @@~DEBUG: END >>parse-strict<< ~~~~~~~~~~~~@@
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    # @@~DEBUG: ORIGINAL >>read-path<< ~@@ validate(config)
    print("validate() skipped")
    # @@~DEBUG: END >>read-path<< ~~~~~~~~~~~~@@
    # @@~~~~~~~~~~~~~~~~~~~~~~~~@@
    return config
```

Two places show what the label is for. The line with `raw bytes` stands inside the block of `parse-strict` but belongs to `read-path` — which is why it carries a mark although no other line in the block does. And the disabled `validate(config)` stands behind the block of `parse-strict`, likewise belongs to `read-path`, and stays put when `parse-strict` is cleaned up.

The self-test finds eight hits here: four for the two blocks, three for the disabled original lines, one for the marked individual line.
