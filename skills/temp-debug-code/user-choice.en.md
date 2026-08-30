# The user's decision about marking

You work through the user: every debug line that comes into being is entered by **them**, and they take it out again later. Whether marks are used is therefore their decision.

## Look first, then ask

If the answer is already in your context — as a rule of the project, or because the user said so in this chat — it holds. **Then do not ask.**

Otherwise put the choice to them once. Keep it short while you do: they should be able to decide, not have to learn the rules.

## What you show them

One sentence on the purpose and a short example:

> I can give the debug lines a mark. Then you find them again later with a single search, and disabled original code sits right beside its replacement, ready to be restored — without either of us having to remember.

```python
    # @@~DEBUG: ORIGINAL >>parse-fail<< ~@@ config = parse(raw)
    config = parse(raw, strict=False)  # @@~DEBUG >>parse-fail<< ~@@
```

No more than that. No full overview of the marks, no case distinctions — those come only once they agree.

## The three outcomes

- **They agree.** This skill's marking holds.
- **They decline.** Then ask whether they would like a simpler marking, and what it should look like. Whatever they propose holds — unchanged and unexamined. You do not judge their proposal and you do not come back to it.
- **They want no marking at all.** Then nothing is marked.

The answer holds for the current chat. If they want to settle it for good, it belongs in the project's own rules; the question then no longer arises.

## Afterwards

In every case, read `rules-handover.en.md` from this skill's folder and work by it. It covers how you choose a probe and hand it to the user — which holds regardless of how they decided. The marking itself is loaded there only if they agreed to it.

Should the user reverse that decision later on, or lay down a different way of marking debug places, you go by what the user has settled and adopt it without asking back and without proposals of your own.
