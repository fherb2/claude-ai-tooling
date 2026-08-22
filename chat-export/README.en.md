# Chats-Export

**Fetches chats from claude.ai projects and stores them as searchable JSON files in a Claude Code project** — for finding earlier context again, not for continuing them. Anthropic doesn't offer a way to do this itself: chats cannot be moved between accounts, nor between claude.ai, Claude Desktop, and Claude Code. This folder rebuilds the two routes that actually work — the account export and claude.ai's internal web endpoints — plus a script that treats both alike.

## The skill

This is used via the `chat-export` skill. Installation and usage are fully described in its own README:

- [`skills/chat-export/README.de.md`](skills/chat-export/README.de.md) (German)
- [`skills/chat-export/README.en.md`](skills/chat-export/README.en.md) (English)

Only the folder `skills/chat-export/` is meant to be copied — everything else here belongs to development.

## Status

**The skill is built, tested against real data across three independent sessions, and ready for use** — most recently in a large-scale run across four real claude.ai projects with 171 chats, whose result was verified against the actual export ZIP (171 of 171 chats found, no discrepancy). Both routes — the account export and the web endpoints — demonstrably yield the same result.

**On 22 August 2026 an independent instance (Fable 5) reviewed the logic of this area against the goals stated in the documentation.** Result: 13 genuine findings and 2 side notes, **all resolved, none deferred**. The review was not a formality — it found real, silent defects: attachments that vanished with their content as an alleged resend; a hollow-chat test that took a chat made of one upload and one failed answer for a deleted one; timestamp comparisons that only worked by an accident of ASCII ordering. That is why "resolved" here is a statement about the code, not about the procedure. What was found and how each point was settled is in [`befunde_logikpruefung_2026-08-22.md`](befunde_logikpruefung_2026-08-22.md) and [`befund_pruefung_2026-08-22.md`](befund_pruefung_2026-08-22.md) (both German), the course of the work in [`fahrplan.md`](fahrplan.md).

All facts, evidence, and check points for this project are in [`implementation_doku.md`](implementation_doku.md) (German); the mechanics of the Chrome connection, including its pitfalls, are in [`chrome-zugriff.de.md`](chrome-zugriff.de.md) / [`chrome-access.en.md`](chrome-access.en.md).
