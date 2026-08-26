# Chats-Export

*Last updated: 2026-08-26*

**Fetches chats from claude.ai projects and stores them as searchable JSON files in a Claude Code project** — for finding earlier context again, not for continuing them at that point. (On claude.ai they can of course be continued, and then updated again in the Claude Code project.) Anthropic doesn't offer a way to do this itself: chats cannot be moved between accounts, nor between claude.ai, Claude Desktop, and Claude Code. This folder rebuilds the two routes that actually work — the account export and claude.ai's internal web endpoints — plus a script that treats both alike.

## The skill

This is used via the `chat-export` skill. Installation and usage are fully described in its own README:

- [`skills/chat-export/README.md`](skills/chat-export/README.md) (German)
- [`skills/chat-export/README.en.md`](skills/chat-export/README.en.md) (English)

Only the folder `skills/chat-export/` is meant to be copied — everything else here belongs to development.

## Status

**The skill is built, tested against real data across three independent sessions, and ready for use** — most recently in a large-scale run across four real claude.ai projects with 171 chats, whose result was verified against the actual export ZIP (171 of 171 chats found, no discrepancy). Both routes — the account export and the web endpoints — demonstrably yield the same result.

**On 22 August 2026 an independent instance reviewed the logic against the goals stated in the documentation; every finding has been fixed.**

What this version does **not** do is set out in [`implementation-doc.md`](implementation-doc.md), chapter 1.8 (German) — the practical consequences for day-to-day use are in the "If you want to top up with more chats later" section of the skill README. In short: one folder per source project, and that folder together with its protocol is the state.

What follows from that as the next stage is outlined in [`version2_fahrplan.md`](version2_fahrplan.md) (German) — two complexes, no steps yet.

Also noted for a future version (review of 25 August 2026): the skill's `SKILL.md` loads in full at 167 lines and aborts hard when the browser tools are not attached to the message — a frequent and therefore expensive outcome. A remedy following the split pattern from `skills/` (thin clarification, rules loaded on demand) requires checking **this** project's own guidelines first, instead of transferring that pattern unexamined.

All facts, evidence, and check points for this project are in [`implementation-doc.md`](implementation-doc.md) (German); the mechanics of the Chrome connection, including its pitfalls, are in [`chrome-access.de.md`](chrome-access.de.md) / [`chrome-access.en.md`](chrome-access.en.md).
