---
name: chat-export
description: Fetches chats from claude.ai projects as searchable JSON files into the current repository, either via the logged-in Chrome browser or from an account export ZIP. Use as soon as the user wants to import, catch up on, back up, or archive chats from a claude.ai project — e.g. "get the new chats from project X", "I want to bring my Claude projects into the repo", "which chats are still missing here?", or "do an export of project Y". Requires attached browser tools and a running Chrome logged into claude.ai.
license: CC0-1.0
---

# Fetching chats from claude.ai

You fetch chats from claude.ai projects and store them as searchable JSON files. They are meant for finding earlier context again, not for continuing a conversation.

The work splits strictly: **you interpret and match, the script counts and compares.** Mapping a mistyped project name onto the real list, reacting sensibly to "just show me everything" — that is your strength. Summing entries from a JSON file is not; measured against this tool, it once said ten where there were nine. **So never do the arithmetic yourself.** Every number you state comes from a script run.

The script sits next to this file: `${CLAUDE_SKILL_DIR}/chat_export_convert.py`.

**On tone toward the user:** terse at the intermediate steps, not tight-lipped about the result. A run that only prints commands and numbers and then falls silent leaves the user unsure whether anything else is coming — that is unpleasant, not a sign of efficiency. Every section gets a short, friendly sentence about what is happening and why; after the last step there is always an explicit statement that this is now done (see the "Wrap-up" section).

## Exactly two checkpoints

There are no more questions than this. Whoever adds a third makes the process unusable.

1. **Before the first fetch.** Briefly explain what is about to happen and ask whether you should start. A yes covers **everything that only reads**: account lookup, project list, chat lists, reconciliation.
2. **After the statistics.** The user picks the route per project. After that comes **one** notice of what happens next — no further checkpoint.

## Procedure

### Check the prerequisites

**Without attached browser tools you stop and do not improvise.** They are only attached to a message the user begins with `@browser`. If they are missing, say exactly that:

> The browser tools are not attached to this message. Call me with `@browser /chat-export`, or start Claude Code with `claude --chrome`.

If the first call reports "Browser extension is not connected" or "Claude in Chrome is turned off in your settings", it is one of these conditions, and the user has to fix it — not you:

- Chrome is running and logged into claude.ai.
- On claude.ai, under Settings → Connectors, "Claude in Chrome" is turned on for this account. Does not act retroactively on already-open tabs.
- In Chrome, under Settings → Downloads, "Ask where to save each file before downloading" is **off**. Otherwise the first download opens a file dialog, and a dialog blocks the connection entirely.

If all three are met and it still does not work, or the connection breaks off in the middle of a run, then read `${CLAUDE_SKILL_DIR}/bridge-diagnosis.en.md`. It says which message belongs to which layer and what is explicitly **not** a cause — in particular that different accounts in Chrome and Claude Code are not one. Do not read it beforehand: as a rule the file is not needed.

### Name the account

Open your own tab. You only ever see your own tabs, never the user's — a claude.ai tab opened beforehand is neither necessary nor reachable.

Fetch `/api/organizations` **with the full object, not just `uuid`/`name`** — the `capabilities` field filters automatically. An organization without `"chat"` in `capabilities` is a pure API/Console organization (typically named something like `"Frank's Individual Org"`); Anthropic deliberately splits chat subscription and API access into separate organizations (documented, [9876003](https://support.claude.com/en/articles/9876003-i-have-a-paid-claude-subscription-pro-max-team-or-enterprise-plans-why-do-i-have-to-pay-separately-to-use-the-claude-api-and-console)) — **that is normal, not a malfunction.** Drop it from the selection without asking.

If more than one organization with chat capability remains, check **yourself first** which one holds the named or desired projects (`/projects` per candidate) before asking — that costs only one extra call and spares the user a question you can answer on your own. Only ask if the result stays ambiguous (a match in more than one, or in none).

State the recognized result **unprompted**:

> Chrome is logged into claude.ai as: *organization name*. That's where I'll look for the projects.

This replaces any earlier instruction to log in. It is more reliable than a claim: the same project name can exist in a second account. The account in Chrome does **not** have to match the one Claude Code itself is working with — that has been checked and is fine.

### Determine the projects

Here you do the work, not the script. Three cases:

- **The user has named the projects.** Match them and move on. If a name only roughly fits, ask once ("*Modelbahn Fahrpult*" doesn't match literally — do you mean *Modellbahn-Fahrpult*?").
- **The user wants to see what's there first.** Show the projects as a menu, sorted by last change, together with what is already stored here.
- **Only one archive is present and the user says nothing further.** Take that one and say that you are taking it.

### Fetch the statistics

For each chosen project, fetch the chat list across **all** pages, then run `list --web --project "<project name>"` and `diff`. **Always** pass `--project` — otherwise the field stays empty in the protocol even though the folder name has long carried the project name. With several projects, show **one** table with one row per project, so the checkpoints stay at two:

```
Project                 Archive Source   new  grown  vanished  Recommendation
Modellbahn-Fahrpult         34      39     5      2         1  Web
```

**No column for message volume.** The chat list does not carry it, and the protocol only knows `turns` after conversion -- any such number would be an estimate, which is exactly what is forbidden. The route recommendation rests on the number of chats, not on their size.

**A chat the fresh list no longer carries is reported and never removed automatically.** Its files stay put. From here, deletion at the source cannot be told apart from a move to another project, and neither can be told apart from a list that was not paged to the end. Any automatic removal would be data loss from a usage mistake in the third case.

### Let the route be chosen

Lay out both routes with their cost and **recommend**, don't decide:

- **Web route** — fetched via the web interface, throttled to a 4–12 s gap. Immediate, no waiting. Loads the web interface, hence the brake. Good for a few chats with small attachments.
- **Export route** — an account export that has to reach back to a computed date. Request, email, download; the wait time is set by claude.ai. Carries everything in one go, with no load per chat. Good for many chats or large attachments.

**Not every account has an export.** In Team and Enterprise accounts, an ordinary member has no self-serve export; there the web route is the **only** option, not just the more convenient one. Whether an export is available cannot be read off the data reliably — state that as a caveat and ask if in doubt.

One answer suffices for all projects; it may also split them ("export for Modellbahn, web for FreeCAD").

### The notice before the run

Not a checkpoint, just the announcement. It **states the replacement with numbers**, because files get removed in the process:

> I'll fetch 9 chats via the web route, gap 4–12 s at random, roughly 2 minutes. Everything arrives as one file in the download folder. During conversion, 2 chats get replaced; I'll remove their 3 existing files first and name them individually.

### Run the web route

One `fetch` per chat from the open page, **everything into one object**, and exactly **one** download at the end. Several downloads from the same page trigger a prompt, and every prompt is an opportunity for a blocking dialog.

Between chat fetches you wait **4 to 12 seconds, drawn uniformly at random** — not on a fixed cadence, so no regular pattern emerges. The purpose is not to burden the server and not to stand out as a bulk fetch.

Show progress per chat. Afterwards, confirm locally that the file has arrived, and run `convert --bundle`.

### Run the export route

State the window boundary from the script run **with a reason** — the date filter applies to the creation date, not the last update; too short a window would leave a chat that has grown out entirely, and nothing would report it. Offer to fill in the request in the browser and present the submit button.

**No deep link reaches the export page.** Navigating directly to `claude.ai/settings/data-privacy-controls` (or similar settings URLs) lands on the ordinary chat interface, not the settings dialog — the page renders settings client-side, only an actual click opens it. Go through the interface: open the account/settings menu, click "Privacy", scroll within it to "Export data". An element-finder tool for "Privacy" or "Export data" reliably finds both buttons.

Then the chain breaks, and you say so plainly: the link arrives by email and is valid for 24 hours. **You do not go into the inbox.** As soon as the user gives the word, you find the ZIP in the download folder and run `convert --zip`.

### Wrap-up

Report what was written, replaced, and cleaned up — the removed files **named individually**; silent deletion would be the next source of error.

If the target project's `CLAUDE.md` does not yet reference the archive, say so as a **remark, not a question** — otherwise a third checkpoint appears:

> Note: This project's CLAUDE.md doesn't yet reference the archive. Without it, the archive sits here and is never read. Let me know if I should add the block.

**Always close out explicitly.** The last sentence states clearly that every announced step is done and nothing further is pending on your side — not just a list of what happened. A user who hears nothing more from you after the last tool output otherwise has no way of knowing whether you're still working or done; having to ask is unpleasant for them. For example:

> That's it — all four projects checked, FreeCAD-Bedienung updated, nothing else open. Let me know if anything more should be added.

## The endpoints

All reachable, with the same origin, from an open claude.ai page via `fetch`. `<org>` is the UUID from `/api/organizations`.

```
GET /api/organizations
GET /api/organizations/<org>/projects
GET /api/organizations/<org>/projects/<project>/conversations_v2?limit=100&offset=0
GET /api/organizations/<org>/chat_conversations/<chat>?tree=True&rendering_mode=messages&render_all_tools=true
```

The list endpoint returns `data` and `pagination` with `has_more`, `limit`, `offset`, `total` — paging is deterministic, nothing has to be guessed. Per chat come `uuid`, `name`, `created_at`, `updated_at`, `project_uuid`, and `model`.

The conversation endpoint returns the **complete message tree** in a single response, without pagination — even at over 180 messages and around 600 KB. The fields carry the same names as in the account export, which is why the converter treats both sources alike.

## The bundle

A JSON file with two parts, filled depending on the step. The download is produced from the page via a blob and a clicked link with a `download` attribute.

```json
{"fetched_at": "...", "organization": "...",
 "conversations": [{"uuid": "...", "name": "...", "created_at": "...", "updated_at": "..."}],
 "chats": [ ... full conversations ... ]}
```

`conversations` feeds `list --web`, `chats` feeds `convert --bundle`.

## The script calls

```
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py list    --web <bundle> --out <directory> [--project <name>]
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py convert --bundle <bundle> --out <directory> [--target repo|knowledge|home]
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py convert --zip <export.zip> --out <directory>
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py diff    --out <directory>
python3 ${CLAUDE_SKILL_DIR}/chat_export_convert.py report  --out <directory>
```

`list` always comes first — it builds the protocol, and only from that follows what needs fetching. A project with no chats is not an error: an empty, valid protocol results. The script's full docstring is its operating manual; read it if a command reacts differently than expected.

The target directory is `<project>/.claude/imported_chats/<source-project>/`, a flat directory per source project. **If the current repo bundles several independent undertakings** (recognizable by its own `CLAUDE.md`) and none of them fits the chosen claude.ai project, ask once about the target folder before creating it — that does not count against the two checkpoints, because it is not a reading or routing decision, but a precondition set by the repo's structure, not by the skill.

## What you never do

- **Never decide which route is taken.** Present both with their cost.
- **Never count yourself.** Every number comes from a script run.
- **Never remove anything that appears to have vanished.** Report it and leave it in place.
- **Never summarize.** Chat text is copied, never retold — the bundle passes as a file, bypassing the model.
- **Never fetch unthrottled.** 4 to 12 seconds, drawn uniformly at random.
- **Never go into the email inbox.**
- **Never demand a claim you can verify yourself.** The account gets stated, not asked for.
