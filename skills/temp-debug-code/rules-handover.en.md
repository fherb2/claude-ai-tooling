# Tracking down faults through the user

You do not reach the source yourself. Every probe that is to run is run by the user; every line that has to be inserted or disabled is entered by them. From that follows the guiding principle of this part: **ask for as little as possible — and for everything you do ask for, say exactly what to do.**

## Where the probe has to run

Before you design a probe, settle one question: **where does the fault live?**

- **If the logic settles it** — an arithmetic path, a string treatment, a sorting behaviour — then run the probe **yourself**, in your own execution environment. That costs the user nothing and happens at once.
- **If the fault hangs on their environment** — versions, installed dependencies, real data, hardware, the file system, timing — then your execution environment **proves nothing.** It is a different machine. The probe belongs on their computer.

If you are unsure which case applies, say so and ask. A probe that runs in the wrong place produces a result that means nothing — and that is worse than no probe.

## The smallest probe first

Ask only for what answers the question, in this order:

1. **Settle it without running anything.** Some things are answered by a look at the source, a question, or an error message that already exists. Then nothing runs.
2. **A probe from the outside** that does not touch the source. The form depends on the language:
   - **Interpreted languages:** a command-line call, often a one-liner — say `python -c "…"`.
   - **Compiled languages:** a command line that compiles and starts, or a small standalone program the user compiles and runs.
   - **Where both get too tight:** a short driver program they put beside the project and call.
3. **A script of its own**, when a single call no longer carries — several steps, setup and teardown, evaluation.
4. **Only then reach into the source.** When an intermediate value cannot be reached from outside, a line has to go in or one has to be disabled. That is not a last resort; it often belongs to step 2 already — the point is not to avoid it but to keep it **small**.

In every case touch as little as possible, and let the user decide after each step whether the next one is needed.

## How you hand over a change

If they are to enter something, they must be able to do it without asking back:

- **Describe the place by its content** — function name, surrounding lines — **never by line numbers.** Those shift with every change.
- **Give the indentation** as it applies at that place.
- **Say what happens to the original:** left alone, disabled, replaced.
- **One step at a time.** Not five interventions at once whose results overlap.

## How you get the result back

Say explicitly **what you want to see**: the whole output, the last lines, the error message with its traceback. And reckon with them returning something other than you expected — ask, rather than drawing conclusions from an unclear output.

## The marking

What holds now is what the user decided (see `user-choice.en.md`):

- **They agreed** → read `marks.en.md` from this skill's folder and hand the lines over ready-marked. **They run the search, not you.** So when it comes to cleaning up, give them the search pattern and, where you know it, the expected number of hits.
- **They proposed a marking of their own** → use theirs, unchanged. `marks.en.md` is then not loaded.
- **They want none** → do not mark.

## Cleaning up

The way back is the user's, and they decide when. Your job is not to leave them stranded:

- When a probe has served its purpose, say so — and say what undoes it.
- For disabled original lines: name the line that has to become active again.
- If they had things marked, name at the end the search pattern that finds the rest.

You do not have to keep a separate list of what to undo — the chat already carries it. If they ask for one, assemble it from the transcript.
