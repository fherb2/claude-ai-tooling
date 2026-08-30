# Tracking down faults with direct access

You reach the project's file tree yourself. The whole search is therefore yours: you decide which probe is needed, how it is run, and how its result is to be read. **No rules for that are written here** — that is craft, not regulation.

Only one thing is regulated: **what you leave behind in the source while the search is running.**

## The marking is not negotiable

Every line you insert for debugging, and every original line you disable for it, is marked. Without asking, in every session.

There are two reasons, and both hold no matter how carefully you work:

- **The user sees where you are reaching in.** They do not read along with every change you make. The mark is where their eye catches.
- **You find your own way back.** At the end of the search the original state must be fully restorable — without memory, and by someone who was not there. An unmarked debug line is not a blemish but a leftover nobody will ever find again.

The only exception is a rule of the project that settles it differently.

**Now read `${CLAUDE_SKILL_DIR}/marks.en.md`.** It carries the marks and the cases in which they are set.

## The self-test, mandatory

Run the search as soon as you have written your debug changes, and compare the number of hits with what you changed:

```
grep -rn '@@~DEBUG' .
```

Every block marking counts as two hits (start and end), every other marked line as one. If the numbers do not match, a mark is missing — look for it before you carry on.

## Removing debug code again

**The way back is your decision, never that of a script.** The search run finds the marks; what happens at a place you check at that place itself — on the strength of everything you know about the code fragment or can find out about it. Reckon with markings set completely differently and unstructured, not as these rules foresee: the user edits too, and not by your scheme. Look closely before you remove a line or reactivate it.

Before you insert new debug code, check whether existing code has served its purpose and can be removed. What decides is not when it came into being, but **which problem-solving task it belongs to**:

- Does it belong to the task you are working on right now, and has it done its job, you remove it on your own and reactivate the code areas disabled along with it.
- Does it belong to an earlier, already finished task, you do not decide for yourself: put the place to the user and let them decide. If they decide against removal, you propose the same place again only once a new day or a new chat has begun, or once the user explicitly asks you to find and remove debug code.

When you remove debug code, check very carefully whether disabled original code has to be reactivated in the process. The separator lines of a block go with it. Run the second search at the end — it additionally finds the separator lines:

```
grep -rn '@@~' .
```

Whatever it still finds has not been cleaned up.

## The commissioned search for leftovers

Of your own accord you do not bring up a foreign or forgotten marking; on that, the `SKILL.md` says what is needed. But if the user explicitly asks you to search for such leftovers and to clear them up together, the same order applies at every place found:

1. **Establish what is there** — together with the user, before anything happens. What you can find out yourself you find out beforehand and put forward with it.
2. **The user decides how the place is to be adjusted.** Remove, leave, rewrite — they choose. You may give a recommendation; you do not take the decision off them.
3. **Only then do you change the place.**

Every place found for itself: a decision at one does not carry over to the next, even when the two look alike.
