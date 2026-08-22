# Chats-Export

**Fetches chats from claude.ai projects and stores them as searchable JSON files in a Claude Code project** — for finding earlier context again, not for continuing them. Anthropic doesn't offer a way to do this itself: chats cannot be moved between accounts, nor between claude.ai, Claude Desktop, and Claude Code. This folder rebuilds the two routes that actually work — the account export and claude.ai's internal web endpoints — plus a script that treats both alike.

## The skill

This is used via the `chat-export` skill. Installation and usage are fully described in its own README:

- [`skills/chat-export/README.de.md`](skills/chat-export/README.de.md) (German)
- [`skills/chat-export/README.en.md`](skills/chat-export/README.en.md) (English)

Only the folder `skills/chat-export/` is meant to be copied — everything else here belongs to development.

## Status

**The skill is built, tested against real data across three independent sessions, and ready for use** — most recently in a large-scale run across four real claude.ai projects with 171 chats, whose result was verified against the actual export ZIP (171 of 171 chats found, no discrepancy). Both routes — the account export and the web endpoints — demonstrably yield the same result.

All facts, evidence, and check points for this project are in [`implementation_doku.md`](implementation_doku.md) (German); the mechanics of the Chrome connection, including its pitfalls, are in [`chrome-zugriff.de.md`](chrome-zugriff.de.md) / [`chrome-access.en.md`](chrome-access.en.md).
