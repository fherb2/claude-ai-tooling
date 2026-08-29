---
name: temp-debug-code
description: Marking rules for temporary debug code — inserted debug and print output, as well as original code disabled for testing, are given fixed, searchable marks so that they can later be removed without a trace and the original state restored in full. Use before inserting a debug output for the first time in a session or commenting out existing code for testing, or when the user calls /temp-debug-code.
license: CC0-1.0
---

# Temporary debug code and temporarily disabled original code

## What these rules apply to — and what they do not

These rules apply exclusively to **temporary** debug code: to lines that come into being only for tracking down a fault and that are meant to disappear again once the cause is found. That includes the original code you disable for the duration of the search.

Not the subject of these rules is debug code meant to stay in the source permanently — output behind a debug flag, behind a log level or behind a configuration variable. Such code is regular program code, is not marked, and follows the usual rules of the project.

**These rules bind you, not the user.** They apply to debug code that you write. What you find in existing code you do not measure against them: the user marks their debug code as they like, and may do it differently at any time. A deviating notation gives rise to no remark and no proposed correction.

Two consequences. You mark your own debug code by these rules even when the surroundings do it differently — two schemes side by side do no harm, and yours stays searchable. And: the search run finds only what follows these rules. Everything else you find by looking, or not at all.

## What the marks are for

Every mark and every separator line begins with the same character sequence `@@~`. The number of tildes behind it is free and irrelevant to the search — used as a separator rule, however, it is sensibly repeated often, in proportion to the surrounding text, before the closing `~@@` follows.

**The marks are an aid, not an automatism.** They serve to recognize the changes for the way back and to find forgotten fragments. What actually happens during that way back is not decided by them.

Two search runs with separate jobs:

```
grep -rn '@@~DEBUG' .   # self-test: finds the marks
grep -rn '@@~' .        # cleaning up: additionally finds the separator lines
```

The entire purpose rests on that: at the end of the search the original state must be fully restorable — without memory, and by someone who was not there. An unmarked debug line is therefore not a blemish but a leftover nobody will ever find again.

**Self-test, mandatory.** Run the first search as soon as you have written your debug changes, and compare the number of hits with what you changed: every block marking counts as two hits (start and end), every other marked line as one. If the numbers do not match, a mark is missing — look for it before you carry on.

## The marks

Keep to the following five marks character by character.

| Mark | Where it goes | When |
| --- | --- | --- |
| `@@~DEBUG >>label<< ~@@` | at the end of the line, behind the comment marker | on every individually inserted debug line |
| `@@~DEBUG: ORIGINAL >>label<< ~@@` | at the start of the line, between comment marker and code | on every original line you have disabled |
| `@@~DEBUG: START >>label<< ~~~~~~~~~~~~@@` | its own comment line before the first debug line | with five or more debug lines in a row |
| `@@~DEBUG: END >>label<< ~~~~~~~~~~~~@@` | its own comment line after the last debug line | for the same block |
| `@@~~~~~~~~~~~~~~~~~~~~~~~~@@` | its own comment line | before every START and after every END |

Four things hold without exception:

- **Before every mark stands the comment marker of the language**, followed by a space. The mark itself begins with `@@~` and ends with one or more tildes and `@@`.
- **A space stands on either side of the label**, and one behind the closing `~@@` as well, before code or comment follows.
- **A mark without a label is incomplete.** The separator line is the only exception; it belongs to no effort.
- **Behind ` @@~DEBUG >>label<< ~@@ ` you may comment the line additionally.** Behind ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` you may not: there the disabled code follows unchanged.

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

If a language has no line comment, put the mark inside a block comment: `/* @@~DEBUG >>label<< ~@@ */`.

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

- Copy the line in question below the original.
- Disable the original: comment marker at the start of the line, behind it ` @@~DEBUG: ORIGINAL >>label<< ~@@ `, behind that the unchanged code.
- Change the copy below it and append ` @@~DEBUG >>label<< ~@@ ` to it, as described in case 2.

### Case 2: up to four inserted debug lines

- Append a comment to every inserted line that begins with ` @@~DEBUG >>label<< ~@@ ` behind the comment marker.
- Original lines standing immediately before, after or between the debug lines that have to be disabled get ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` between comment marker and code.

### Case 3: five or more debug lines in a row

- Put a comment line of its own before the first debug line, beginning with ` @@~DEBUG: START >>label<< ~~~~~~~~~~~~@@ ` behind the comment marker.
- Put a matching comment line with ` @@~DEBUG: END >>label<< ~~~~~~~~~~~~@@ ` after the last debug line.
- Put a separator line ` @@~~~~~~~~~~~~~~~~~~~~~~~~@@ ` before the START line and after the END line.
- On the lines in between, the mark ` @@~DEBUG >>label<< ~@@ ` is dropped — with the exception described in the next section.
- **Disabled original lines keep their mark ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` inside a block as well.** Only ` @@~DEBUG >>label<< ~@@ ` is dropped. Without the ORIGINAL mark it is no longer recognizable inside the block which lines are to be reactivated — and that is exactly what matters when cleaning up.

### Nesting

A debugging effort may come into being inside another one; when debugging, that is the normal case and not the exception. Each carries its own label, and **the assignment follows from it alone, never from the position in the code.** A disabled line can sit physically inside the block of a foreign effort and still belong to the enclosing one.

From that follows the exception to case 3: **an inserted line belonging to a different effort than the block it stands in carries ` @@~DEBUG >>its-label<< ~@@ `** — inside a block as well, where the mark is otherwise dropped.

Where the END of one block and the START of the next meet, one separator line is enough.

## Original code is never deleted

Original code that has to give way for the search is **only commented out — never deleted and never overwritten.** That holds even when it is short and you could easily remember it. The disabled line is the only reliable source for the way back: it stands in the search run, it stands in the diff, and it still stands there when somebody else cleans up.

## What else you watch out for when changing

- At decision points — branches, case distinctions — and inside loops the marks matter especially, so that the original state stays restorable with minimal effort and in a way the user can follow.
- Take over the indentation you find, or that of the programming language in use, unchanged.

## Removing debug code again

**The way back is your decision, never that of a script.** The search run finds the marks; what happens at a place you check at that place itself — on the strength of everything you know about the code fragment or can find out about it. Reckon with markings set completely differently and unstructured, not as these rules foresee: the user edits too, and not by your scheme. Look closely before you remove a line or reactivate it.

Before you insert new debug code, check whether existing code has served its purpose and can be removed. What decides is not when it came into being, but **which problem-solving task it belongs to**:

- Does it belong to the task you are working on right now, and has it done its job, you remove it on your own and reactivate the code areas disabled along with it.
- Does it belong to an earlier, already finished task, you do not decide for yourself: put the place to the user and let them decide. If they decide against removal, you propose the same place again only once a new day or a new chat has begun, or once the user explicitly asks you to find and remove debug code.

When you remove debug code, check very carefully whether disabled original code has to be reactivated in the process. From a line with ` @@~DEBUG: ORIGINAL >>label<< ~@@ ` both the mark **and** the leading comment marker disappear; afterwards the line stands there exactly as it did before the debugging. The separator lines of a block go with it. Run the second search at the end: whatever it still finds has not been cleaned up.

### The commissioned search for leftovers

Of your own accord you do not bring up a foreign or forgotten marking; on that, "What these rules apply to" says what is needed. But if the user explicitly asks you to search for such leftovers and to clear them up together, the same order applies at every place found:

1. **Establish what is there** — together with the user, before anything happens. What you can find out yourself you find out beforehand and put forward with it.
2. **The user decides how the place is to be adjusted.** Remove, leave, rewrite — they choose. You may give a recommendation; you do not take the decision off them.
3. **Only then do you change the place.**

Every place found for itself: a decision at one does not carry over to the next, even when the two look alike.

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
