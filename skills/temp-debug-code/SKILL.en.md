---
name: temp-debug-code
description: Marking rules for temporary debug code — inserted debug and print output, as well as original code disabled for testing, are given fixed, searchable marks so that they can later be removed without a trace and the original state restored in full. Use before inserting a debug output for the first time in a session or commenting out existing code for testing, or when the user calls /temp-debug-code.
license: CC0-1.0
---

# Temporary debug code and temporarily disabled original code

## What these rules apply to — and what they do not

These rules apply exclusively to **temporary** debug code: to lines that come into being only for tracking down a fault and that are meant to disappear again once the cause is found. That includes the original code you disable for the duration of the search.

Not the subject of these rules is debug code meant to stay in the source permanently — output behind a debug flag, behind a log level or behind a configuration variable. Such code is regular program code, is not marked, and follows the usual rules of the project.

## What the marks are for

Every mark defined here begins with the same character sequence ` # DEBUG`. A single search run therefore finds, without exception, every change that came into being for debugging:

```
grep -rn " # DEBUG" .
```

The entire purpose rests on that: at the end of the search the original state must be fully restorable — without memory, by someone who was not there, and by script if need be. An unmarked debug line is therefore not a blemish but a leftover nobody will ever find again.

**Self-test, mandatory.** Run the search as soon as you have written your debug changes, and compare the number of hits with what you changed: every block marking counts as two hits (start and end), every other marked line as one. If the numbers do not match, a mark is missing — look for it before you carry on.

## The marks

Keep to the following four marks character by character. **Each mark has a leading and a trailing space** — exactly one at the front and one at the back, without exception. Without them the search run no longer works reliably.

| Mark | Where it goes | When |
| --- | --- | --- |
| `# DEBUG #` | at the end of the line, behind the comment marker | on every individually inserted debug line |
| `# DEBUG: ORIGINAL #` | at the start of the line, between comment marker and code | on every original line you have disabled |
| `# DEBUG: START ------------ #` | its own comment line before the first debug line | with five or more debug lines in a row |
| `# DEBUG: END ------------ #` | its own comment line after the last debug line | for the same block |

The enclosing spaces are not visible in the table; what counts is the sentence above it and the examples below.

### The `#` is part of the mark

The `#` at the beginning and the end of every mark is part of the mark and **not** the comment marker of the programming language. In Python it therefore meets a second `#`, and the line carries two hashes in a row. That looks like a mistake but is intentional: only this way does the mark read identically in every language and get found by a single search pattern. Do not remove this apparent duplication and do not simplify it.

Python:

```python
value = fallback()  # # DEBUG # bypass cache on purpose
# # DEBUG: ORIGINAL # value = cache.get(key)
```

C, C++, Java, JavaScript, Rust and relatives:

```c
int n = 0;  // # DEBUG #
// # DEBUG: ORIGINAL # int n = compute_size(buf);
```

Shell:

```bash
path="/tmp/probe"  # # DEBUG #
# # DEBUG: ORIGINAL # path="$(resolve_path "$1")"
```

If a language has no line comment, put the mark inside a block comment: `/* # DEBUG # */`.

### The dashes in the block marks

The chain of dashes is pure optics — it makes the start and the end of the block stand out in the source. It does not count for finding anything; the search is for ` # DEBUG`. Write twelve dashes; if you come across a different number in existing code, that is not an error and nothing to correct.

## The three cases when inserting

### Case 1: changing a single statement line for debugging

- Copy the line in question below the original.
- Disable the original: comment marker at the start of the line, behind it ` # DEBUG: ORIGINAL # `, behind that the unchanged code.
- Change the copy below it and append ` # DEBUG # ` to it, as described in case 2.

### Case 2: up to four inserted debug lines

- Append a comment to every inserted line that begins with ` # DEBUG # ` behind the comment marker.
- Behind the mark you may comment the line additionally.
- Original lines standing immediately before, after or between the debug lines that have to be disabled get ` # DEBUG: ORIGINAL # ` between comment marker and code.

"In a row" means: separated by at most one line not belonging to the debugging. If the debug lines lie further apart, they are separate cases, and every group is counted for itself.

### Case 3: five or more debug lines in a row

- Put a comment line of its own before the first debug line, beginning with ` # DEBUG: START ------------ # ` behind the comment marker.
- Put a matching comment line with ` # DEBUG: END ------------ # ` after the last debug line.
- On the lines in between, the mark ` # DEBUG # ` is dropped.
- **Disabled original lines keep their mark ` # DEBUG: ORIGINAL # ` inside a block as well.** Only ` # DEBUG # ` is dropped. Without the ORIGINAL mark it is no longer recognizable inside the block which lines are to be reactivated — and that is exactly what matters when cleaning up.

If you are unsure whether a case crosses the limit of four lines, take the block form.

## Original code is never deleted

Original code that has to give way for the search is **only commented out — never deleted and never overwritten.** That holds even when it is short and you could easily remember it. The disabled line is the only reliable source for the way back: it stands in the search run, it stands in the diff, and it still stands there when somebody else cleans up.

## What else you watch out for when changing

- At decision points — branches, case distinctions — and inside loops the marks matter especially, so that the original state stays restorable with minimal effort and in a way the user can follow.
- Take over the indentation you find, or that of the programming language in use, unchanged.

## Removing debug code again

Before you insert new debug code, check whether existing code has served its purpose and can be removed. What decides is not when it came into being, but **which problem-solving task it belongs to**:

- Does it belong to the task you are working on right now, and has it done its job, you remove it on your own and reactivate the code areas disabled along with it.
- Does it belong to an earlier, already finished task, you do not decide for yourself: put the place to the user and let them decide. If they decide against removal, you propose the same place again only once a new day or a new chat has begun, or once the user explicitly asks you to find and remove debug code.

When you remove debug code, check very carefully whether disabled original code has to be reactivated in the process. From a line with ` # DEBUG: ORIGINAL # ` both the mark **and** the leading comment marker disappear; afterwards the line stands there exactly as it did before the debugging. Run the search at the end: whatever it still finds has not been cleaned up.

## Places that do not follow these rules

If you find lines in the source that do not keep to these rules exactly, inform the user and propose the correction to them. Show them the result of the correction in the chat by way of example, so they can decide more easily. No such correction without the user's prior agreement.

## Example

Starting state:

```python
def load_config(path):
    raw = read_file(path)
    config = parse(raw)
    validate(config)
    return config
```

Case 1 and case 2 — one changed statement line, one inserted output, one disabled original line:

```python
def load_config(path):
    # # DEBUG: ORIGINAL # raw = read_file(path)
    raw = '{"mode": "test"}'  # # DEBUG # fixed input instead of file
    config = parse(raw)
    print(f"config={config}")  # # DEBUG #
    # # DEBUG: ORIGINAL # validate(config)
    return config
```

The search run finds four hits here, matching four changed or inserted lines.

Case 3 — the same starting state, but five debug lines in a row, one disabled original line among them:

```python
def load_config(path):
    raw = read_file(path)
    config = parse(raw)
    # # DEBUG: START ------------ #
    print(f"path={path}")
    print(f"raw bytes={len(raw)}")
    print(f"keys={sorted(config)}")
    print(f"mode={config.get('mode')}")
    # # DEBUG: ORIGINAL # validate(config)
    print("validate() skipped")
    # # DEBUG: END ------------ #
    return config
```

The search run finds three hits here: two for the block, one for the disabled original line inside it.
