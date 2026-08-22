# Chrome Access — Systematic Test of the Bridge

This file carries the complete, systematic test path for Claude Code's Chrome connection (VS Code extension) — how it actually comes about and what it depends on. It was created for the `chat-export` skill (web route), but reads independently of that skill's other docs.

**Machine:** the same one throughout (Chrome, VS Code extension, `@browser` mechanism).

## Stage 0 (the previous day, 20/21 August): prior findings

Summarized briefly:

- A message without `@browser` provides no browser context — the tools are listed, but respond "Browser extension is not connected".
- The connector switch on claude.ai (Settings → Connectors → "Claude in Chrome") must be turned on for whichever account is active, otherwise "Claude in Chrome is turned off in your settings" comes back. Does not act retroactively on already-open tabs.
- Logging out of claude.ai in the tab: the bridge itself stayed reachable (navigation, script execution), only the claude.ai API call failed with `account_session_invalid`. Also tested on unrelated domains (gmx.de, example.com) — the bridge works there just the same, so it is not limited to claude.ai.

## Stage 1 (today, 22 August): starting point "same account everywhere"

**Starting point, per the user:** before today's test, the same Pro account had been in use everywhere — Chrome, this Claude Code session, the Claude Code CLI.

**1a — Chrome closed, `@browser` announced in the first message but not yet sent.** No access attempt needed, a plain announcement.

**1b — Chrome running (empty tab), the message arrived without a `<browser>` context block despite the `@browser` mention.** `tabs_context_mcp` → "Browser extension is not connected". Notable: per the system message the MCP server had reconnected, but that alone was not enough — no usable browser context came with it.

**1c — Chrome running, still no access.** The user opened the extension icon in Chrome: the extension itself showed as **not logged in** (separate from the claude.ai website login in the tab — this is about the extension's own login, visible via "Open Claude"). Two possible causes left open: the login lapses when Chrome closes, after some time span, or on a machine restart. Not distinguished.

**1d — The user logs back into the extension** (a full login turn via email link). Afterward, `tabs_context_mcp` → **success**, a tab was provided.

**1e — The first navigation after the re-login reported success but had not really happened.** `navigate` to `gmx.de` returned a success response with the title "www.gmx.de", but a repeated `tabs_context_mcp` query still showed the tab as an empty `chrome://newtab/`. A second navigation to the same target then actually worked (confirmed by the user in the tab). **Lesson: right after a re-login, the tool's report cannot be trusted without a visual check by the user — there appears to be a short delay before the extension actually responds.**

**Interim conclusion, stage 1:** neither Chrome running nor the `@browser` text alone is enough. What mattered was **the Chrome extension's own login**.

## Stage 2 (today): switching the claude.ai website account, extension stays logged in

**2a — The user logs out of claude.ai in the tab** (Pro account). The extension itself stays logged in — clicking the extension icon still brings up a chat with an active connection.

**2b — Access checked:** `tabs_create_mcp` failed at first, because the old tab group had become invalid when the tabs were closed ("This session's tab group no longer exists"); `tabs_context_mcp --createIfEmpty` immediately created a new tab. **The bridge keeps working despite being logged out of claude.ai.**

**2c — `gmx.de` opened and confirmed loaded by the user.** Works.

**2d — The user logs into claude.ai in the same tab with a *different* account** — the **Team account** ("work account"), not the original Pro account.

**2e — Access checked again:** a new tab created, `gmx.de` loaded (confirmed by the user), then `https://claude.ai/api/organizations` called:

```json
[{"name": "HZDR - FWF", "uuid": "4efe0308…"}]
```

That is the **Team account**, not the original Pro account (`e2cea7f9…`, "herbrand@gmx.de's Organization").

**Stage 2 result, preliminary:** the bridge apparently just follows the **current claude.ai web session in the tab** — it reads whatever session cookie is currently valid, regardless of which account Claude Code or the Chrome extension were originally connected with. There seems to be **no fixed account binding of the bridge itself**; switching accounts in the tab is enough to make the API responses reflect the new account.

**An important limit to this finding:** the starting point in stage 1 was "same account everywhere" — the bridge was therefore originally built with the Pro account, and the account switch happened only *afterward*, on an already-existing connection. Whether a bridge can also be built **from the very start** with a mismatched account — if Chrome/the extension works with a different account than Claude Code itself from the outset — is thus **not yet** tested. That is the subject of the next stage.

## Stage 3: machine restart, Chrome on the Team account from the start — carried out, inconclusive result

Starting point: the user rebooted the machine and logged into Chrome with the **Team account** from the start — not as a later switch as in stage 2, but as the initial state before any connection attempt.

**Prior finding, unrelated to the actual test:** the Chrome login itself survives a machine restart. After the restart, an account was still logged into Chrome without the user having to actively log in again — this is apparently set server-side by Anthropic (session duration), not tied to the machine restart.

**Procedure, each step checked with `tabs_context_mcp`:**

1. Team account logged into Chrome, empty tab open, `@browser` set → **"Browser extension is not connected."** (Checked twice, same result.)
2. Extension icon clicked — a separate prompt window opens, still logged in there → **still "not connected"**.
3. Extension options opened (the same path that had led to a breakthrough earlier in stage 1) → **still "not connected"**.
4. The user logs in again with the **Pro account**, full email turn (the identical step as in 1d, which had worked there) → **still "not connected"**, even on a second attempt shortly after.
5. The user runs a real chat turn **inside the extension itself** (in the extension's own small chat window) — the extension is thereby demonstrably talking to claude.ai successfully → **still "not connected"** for the bridge to this Claude Code session.
6. The user sends `@browser` again — this time the VS Code interface itself reports an error: **"no Files"**, a third failure mode not seen before. No further test carried out, the user announces a session restart.

**Tentative interpretation.** Unlike in stages 1/2, neither an account switch, nor logging in again, nor a demonstrably working turn inside the extension itself helped here. That argues against the account constellation alone being the cause — it points more strongly toward the bridge connection of this particular Claude Code session having gotten into a state it could no longer resolve on its own, and toward the accumulation of failed attempts with the Team account possibly having become the trigger itself, rather than being a neutral test step. The final "no Files" error on the VS Code side (not from the bridge, but from the interface itself) supports this: it occurred *before* any new bridge attempt had even taken place.

**Stage 3 is therefore not cleanly decidable.** Neither confirmed nor refuted: whether a first-time bridge build with an account differing from Claude Code's fails on principle. The test would have to be repeated with a fresh, demonstrably working session in which a mismatched account is active in Chrome from the very start — without the history from steps 1–5, which may have contaminated the current session's state.

**Next step:** the user announces a session restart. Continuation after the restart, with a clean starting point.

**Interim step (still with the Pro account):** a session restart alone had not helped yet. After that: Chrome restart, log out, log back in with the **Pro account** (this time without an email turn) → access works again.

## Stage 3, clean repeat attempt: Team account from the start — passed, unambiguous

The user then restarted the **entire machine** (not just Chrome). In Chrome, right after the restart, logged into claude.ai **anew** — this time with the **Team account**, full email turn. This Claude Code session itself stayed connected with the **Pro account** the whole time — the accounts were thus deliberately mismatched from the start, no alignment.

**First `@browser` attempt after the machine restart, `tabs_context_mcp`:** immediate success, tab provided. No failure, no retry needed.

**Result, now unambiguous — unlike the earlier, probably premature stage-3 attempt above:** the bridge build succeeds **even when** the account logged into claude.ai in Chrome (Team) differs from the start from the account this Claude Code session itself works with (Pro). **The question of matching accounts is thus settled: a match is not required.**

What actually matters, summarized from the whole of today's test:

1. Chrome must be running and logged into claude.ai (any account, with a working connector switch, see stage 0).
2. The extension itself must be working — verifiable by a working chat turn inside the extension as the test criterion.
3. If both hold, `@browser` works reliably in this Claude Code session, regardless of the account.

**The earlier stage-3 failure (above) remains unresolved in its cause**, but can no longer be read as evidence against the account-independent build — most likely a different, now unreconstructable session or extension state was present there (see the interpretation given there: accumulated failed attempts, the "no Files" error on the VS Code side).

## Stage 4: access to existing tabs — its own, isolated tab group, no access to tabs the user opened

The user's question: can this session find and reuse a Chrome tab the user has already opened manually (here: claude.ai, opened by hand), or must a new tab always be created?

**Test.** `tabs_context_mcp` **without** `createIfEmpty` first reported: "No tab group exists for this session." — not an empty list, but the complete absence of any visibility into existing tabs. Then `tabs_context_mcp` **with** `createIfEmpty: true`: a **new, empty** tab was created (`chrome://newtab/`) — not the claude.ai tab the user had already opened.

**Result: there is no access to tabs the user opened manually.** Every Claude Code session works in its own, isolated "MCP tab group", separate from the user's regular Chrome tabs. To work with claude.ai, it must always navigate there **itself** — but it relies on the same Chrome-wide login/session that the manually opened tab also uses (see stages 0–3: the login is Chrome-wide, not tab-bound).

**Consequence for the skill:** it can and must create its own tab at the start (`tabs_create_mcp`, or implicitly via `tabs_context_mcp --createIfEmpty`) and needs no preparation from the user beyond an existing Chrome login — a claude.ai tab the user opened in advance is neither necessary nor usable.

**Addendum, own error clarified.** Right afterward, the created tab seemingly could not be controlled — but that was not the bridge's fault, it was because only `tabs_context_mcp` had been loaded, not `navigate`. With `navigate` (tool loaded afterward), controlling the same tab worked immediately and flawlessly (`navigate` to `claude.ai` succeeded). No new finding about the bridge, just a reminder: for a created tab, the actual action tools (`navigate`, `computer`, `javascript_tool`, `find`, …) must be loaded in addition to `tabs_context_mcp`.

## Stage 5: visibility mix-up confirmed, and a new chat is written via the interface and then read back in structured form

**Direct confirmation of the tab isolation from stage 4.** In addition to the tab I had created myself, the user had a further, manually opened tab "New Chat - Claude" open in Chrome and asked me to find and use exactly that one. `tabs_context_mcp`, however, listed **only** my own tab (the same `tabId` as before), which had been automatically redirected to `/new` by the earlier navigation to `claude.ai` and happened to carry the same visible title. On the first attempt to type, the user was watching the wrong tab (their own, manually opened one) and saw no "Hello!" appear there; only after switching to my actual tab was the entered text visible. **This confirms, rather than merely suspects: there is no way, accidental or deliberate, to end up in a tab the user opened manually — the MCP tab group's isolation is complete.**

**A chat was written entirely through the interface** (click into the input field via `find` + `computer left_click`, `computer type` for "Hello!", `computer key Return` to submit) — not via the API. The user watched the screen and confirmed each step before the next one happened. Response received: "Hello! Great to have you here. What can I help you with today?"

**Then read back as structured JSON**, without any further text recognition from the visible page: the chat UUID was right there in the tab URL after submitting (`https://claude.ai/chat/028964c2-…`), and the same conversation endpoint the web route uses returned the full turn — `sender: "human"` with "Hello!", `sender: "assistant"` with the exact reply text, both with full `content` blocks, status 200, 2 messages.

**A secondary finding on the account question, confirmed on a third, independent case:** the call ran under the **Team account** (`HZDR - FWF`) then active in Chrome — even though the chat had been created through the ordinary user interface, not via a targeted API call. So the bridge consistently reads whichever claude.ai session is currently active, regardless of this Claude Code session's own account.

**Consequence for the skill, beyond what has been described so far:** it is not only able to read existing chats — in principle it could also create a new chat itself (via the interface or directly via the API endpoint) and then export it in structured form. That is not planned for this project, but is technically shown to be possible.

## Stage 6: navigation via the left sidebar — "Home" works, "Code" leads nowhere useful

Checked at the user's request: the left sidebar of the claude.ai interface, with its two tabs "Home" and "</> Code".

**"Home" → "Projects" menu item:** click by coordinate succeeded, title/URL changed to "Projects - Claude" (`/cowork/projects`). The same five projects of the Team account were visible there, with the same full metadata (`name`, `uuid`, `created_at`, `updated_at`, `is_private`) that the direct API call (`/api/organizations/<org>/projects`) also returned — the on-screen view and the JSON data matched exactly.

**"Code" tab:** click succeeded (`/code/family`), but shows **no** list of code projects, only a generic promotional page with three tiles — Terminal, IDE extension, Web. No "Projects" menu item like on the home tab.

- **Terminal tile:** shows only an install command (`curl -fsSL …`) for installing Claude Code locally; no way to start a terminal in the browser. Below it, "Sessions you start will show up here" — empty.
- **Web tile ("Start Claude Code Web"):** leads to an onboarding page (`/code/onboarding`) with a repository picker and an input field, but with the notice: *"Claude Code on the web requires GitHub access. Please contact an organization owner."* Locked for this account, then; not submitted.
- **IDE extension:** not checked further (an install link into an IDE, no browser access to be expected).

**Result: no locally created Claude Code projects from Claude Desktop can be reached via the Chrome tab.** The "Code" view in claude.ai is built for *starting* new sessions (terminal install, web with GitHub connection, IDE extension), not for *listing* existing local projects. For the web route, that means: **the only part of the Chrome tab that is usefully applicable is the "Home" area** — chats and projects in the ordinary claude.ai sense. Whether that changes in the future (e.g. a later list of connected local projects) is speculation and is not claimed here.

## Stage 7: first real test run of the skill flow — Team account with no self-serve export, aborted on a code gap

**Starting point.** At the user's request, the planned skill flow was run for real for the first time — not merely simulated —, with `chat_export_convert.py` as the executing tool, against the Team account (`HZDR - FWF`) that was actively logged into Chrome.

**An important secondary finding, not stated anywhere before:** the Team account has **no self-serve export** — unlike what the rule of thumb "web route for small top-ups, otherwise the account export" suggests, the web route here is **the only option at all**, not just the more convenient one. This matches the already-documented account-type restriction (doku 1.2/1.6: Team/Enterprise members without Primary Owner rights have no export). **Consequence for the skill:** it has to be able to recognize (or be told) that no export exists for an account, and must then not even offer the export route as an alternative.

**Procedure, step by step:**

1. First checkpoint presented and confirmed.
2. Account named (`HZDR - FWF`, the only organization) and the project list fetched: 5 projects via `/api/organizations/<org>/projects`.
3. The user chose two projects for the test: "Chats-Export, Test 1" and "Dresdyn-Kamerasystem-Überarbeitung".
4. Chat lists of both projects fetched (`conversations_v2`): **"Chats-Export, Test 1" → 3 chats**, **"Dresdyn-Kamerasystem-Überarbeitung" → 0 chats** (`pagination.total: 0`, genuinely empty, not a fetch problem).
5. Second checkpoint: the web route named as the **only** option (no export available), the user confirmed, **and** explicitly asked that a — then empty — report/protocol be created for the empty project too, instead of skipping it.
6. Output folders created: `tests/test_results/dresdyn-kamerasystem/`, `tests/test_results/chats-export-test-1/` (both gitignored, stayed empty).
7. For Dresdyn, a web bundle with an empty `conversations` list generated and downloaded (`~/Downloads/web-bundle_dresdyn-kamerasystem_list.json`, 127 bytes, arrived).
8. `list --web <bundle> --out tests/test_results/dresdyn-kamerasystem` run.

**Result of step 8: abort.** `chat_export_convert.py` refuses to create a protocol for an empty chat list — message *"No chats found in the given list(s)."*, exit code 1. That is existing, deliberately written code behavior (the check `if not records: … return 1`), not a mistake in the test run.

**The gap:** the code currently does not distinguish between "no source given" (a genuine usage mistake, aborting is correct) and "source given, but it genuinely yields zero chats" (the legitimate state of an empty project, which should be allowed to produce an — empty — report, as the user wanted). For the second project, "Chats-Export, Test 1" (3 chats), the test was not continued at all, so as not to proceed with a half-inconsistent procedure.

**Aborted here at the user's request, no decision made yet and no code change made** — the right fix (distinguishing the two cases in `cmd_list`/the `records` check) is still open and has to be discussed with the user before it is implemented, as with any script change.

**Cleanup state:** both output folders empty, no file written. The bundle download `~/Downloads/web-bundle_dresdyn-kamerasystem_list.json` sits outside the project root and was left untouched — it contains only metadata (timestamp, organization UUID, empty list), no chat content.

**Added later, 21 August (after a machine restart, without the browser):** the gap is fixed. `cmd_list` in `chat_export_convert.py` no longer refuses an empty chat list — the check `if not records: ... return 1` has been removed outright; only a missing source (both `--map`/`--web` empty) remains an error. Tested against a genuinely empty bundle: exit code 0, a valid, empty `protokoll.json` is written. The counter-check for the unchanged error case passed. A regression test added to `tests/test_export_convert.py` (two new checks) and confirmed via a blank test — with the old check written back, exactly this test fails. All six suites green, including under `-O`. This means the second part of stage 7 (project "Chats-Export, Test 1" with 3 chats) can be caught up on the next browser access, without getting stuck at this point again.

## Stage 8 (22 August): switching accounts on an already-standing bridge, not the trigger for the drop

The finding from stage 2 — switching accounts in the tab does not break an already-existing bridge — independently reproduced today, triggered by a suspicion that dissolved in the process.

**The suspicion:** over the course of the afternoon, the connection dropped and came back several times — sometimes with "Browser extension is not connected" on `tabs_context_mcp`, sometimes the MCP server `claude-in-chrome` disappeared from the tool list entirely, regardless of any account change. When the connection happened to come back shortly after logging Chrome into the **Pro** account (Chrome had been on the Team account until then), the suspicion arose that the bridge did after all need the same account as the Claude Code session — contradicting the restart finding from stage 3.

**The counter-test:** with the bridge still standing (Chrome on Pro, `/api/organizations` confirmed), the user switched Chrome to the **Team account** — deliberately going back to a mismatch against the Pro session of Claude Code. `tabs_context_mcp` immediately returned the existing tab, `/api/organizations` in the same tab promptly returned `HZDR - FWF` — no new login of the bridge needed, no drop.

**Result: the suspicion is dispelled.** The bridge continues to follow only the current claude.ai web session in the tab, regardless of the Claude Code session's account — as shown in stage 2, now a second time and with the roles swapped (there Pro→Team, here Pro→Team after an intervening Team→Pro). The instability of the afternoon was the beta's MCP server flapping, not an account issue. Nothing about the statements from stages 2/3 changes; this is just the second reproduction.

## Distinction: not every connection drop is a bridge finding

During the big import on 21 August — four real projects, 171 chats via the export route (implementation doc, 3.1.7) — one `API Error: Connection lost mid-response` occurred mid-conversation. That is the **model connection** of this Claude Code session, not `claude-in-chrome` — the bridge itself was unaffected, the run continued afterward without any further loss of access. Per the user, their internet connection has occasional multi-minute outages; that is the more plausible explanation than a bridge fault. Recorded here so that a future occurrence of this message is not too quickly lumped in with the MCP server dropouts from stage 8 — the two look similar but are different layers.
