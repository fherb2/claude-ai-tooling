---
name: temp-debug-code
description: Rules for temporary debug code — inserted debug and print output, as well as original code disabled for testing, are given fixed, searchable marks so that they can later be removed without a trace and the original state restored in full. Where Claude cannot reach the user's files itself, it adds which probe runs where and how it is handed over. Use before inserting a debug output for the first time in a session, commenting out existing code for testing, or proposing such a change to the user, or when the user calls /temp-debug-code.
license: CC0-1.0
---

# Temporary debug code and temporarily disabled original code

## What these rules apply to — and what they do not

These rules apply exclusively to **temporary** debug code: to lines that come into being only for tracking down a fault and that are meant to disappear again once the cause is found. That includes the original code you disable for the duration of the search.

Not the subject of these rules is debug code meant to stay in the source permanently — output behind a debug flag, behind a log level or behind a configuration variable. Such code is regular program code, is not marked, and follows the usual rules of the project.

**These rules bind you, not the user.** They apply to debug code that you write or propose. What you find in existing code you do not measure against them: the user marks their debug code as they like, and may do it differently at any time. A deviating notation gives rise to no remark and no proposed correction.

## The project's own rules come first

If the project has settled how debug code is handled, that holds and not this skill — including where the skill otherwise leaves no choice. Where to look:

- **The project's instruction file** — its own `CLAUDE.md`, or the project's instruction field — is in your context anyway. Nothing more to do there.
- **If you work through the user** and the answer is not already in your context, look in the project knowledge. That is one flat place; one look is enough.
- **If you reach the file tree yourself**, rely on the instruction file. Where accompanying project documentation exists, it usually says so. Do not comb through subfolders.

If you find such a rule only later, it holds **from then on** and overrides what is written here.

## Which environment are you working in?

Everything that follows hangs on a single distinction:

**Do you reach the project's file tree directly — with tools that read and write its files?** In Claude Code you do. On claude.ai and in Claude Desktop you do not: there you work through the user, and their hand is the one on the source.

> **Project knowledge is not the file tree.** If you find files under `/mnt/project/` or at a comparable place, those are **copies**. Changing something there changes nothing in the user's project. Finding something there proves no direct access.

- **You reach the file tree yourself** → read `${CLAUDE_SKILL_DIR}/rules-local.en.md` and work by it.
- **You work through the user** → read `user-choice.en.md` from this skill's folder and work by it.

## Why this skill is split

The two cases are not two wordings of the same thing but two mechanisms: in one you act, in the other the user does. And whether anything is marked at all is, in the second case, their decision — because they do the work. Rules that do not apply to the situation at hand would only cost context here and blur the decision. This file therefore carries only what holds in both cases; everything else is loaded once it is clear what is needed.
