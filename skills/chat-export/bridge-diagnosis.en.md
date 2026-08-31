# The Chrome bridge: which message belongs to which layer

Read this file when the connection does not come up, or breaks off in the middle of a run. The preconditions themselves are in the `SKILL.md`; what stands here is what a failure means once they are met and it still does not work.

The purpose is delimitation. The most expensive diagnosis is the one that sends the user off to change something that has nothing to do with the cause — and that is exactly where the investigation of this bridge itself once got stuck for an afternoon.

## What is explicitly not a cause

**Different accounts in Chrome and in Claude Code are not an error.** The bridge follows only the claude.ai web session currently active in the tab — regardless of which account this Claude Code session hangs on. Reproduced twice independently, once after a full machine restart with different accounts from the start. So do not send the user off to align accounts.

There is a reason this misconception keeps coming back: **Anthropic's own error message claims the accounts must match** — "Please ensure the Claude browser extension is installed and running, and that you are logged into claude.ai with the same account as Claude Code." An error message lists possible causes; it does not establish a condition. Anyone who reads it without knowing the test path writes the requirement down again — which is exactly what happened in this skill's user documentation for nine days.

**Switching accounts in the tab does not break a standing bridge.** Also reproduced twice, the second time with the roles swapped. After the switch the tab promptly returns the new organization, without the bridge having to log in again.

**The bridge is not confined to claude.ai.** Navigation and script execution work on other domains too. A failure on the claude.ai call is therefore not yet a finding about the connection.

## Four messages and their layer

**`Claude in Chrome is turned off in your settings`** — the connector switch. One of the preconditions from the `SKILL.md` is not met, and the user is the one who meets it. The switch does not act retroactively on tabs that are already open.

**`Browser extension is not connected`** — two causes, and they need to be told apart. On the **first** call: `@browser` is missing from the message, or a precondition is open. **In the middle of a run** with the connection previously standing: the flapping of the beta, see below.

**`account_session_invalid`** — nobody is logged into claude.ai in the tab. The bridge itself is still standing: navigation and script execution work, only the claude.ai API call fails. What is affected is the web session, not the connection.

**`API Error: Connection lost mid-response`** — the model connection of this Claude Code session, not the bridge. Observed in the middle of the large run across 171 chats; the run continued afterwards without losing access again. This message does not belong among the bridge findings — it looks like the flapping but concerns a different layer.

## Flapping of the beta

If the MCP server `claude-in-chrome` disappears from the tool list entirely, or the connection breaks off repeatedly for no discernible reason and comes back, that is the instability of the beta — not a question of accounts and not a missing precondition. Observed several times over one afternoon. The right answer is to wait and try again; changing something about the account is not.

## What you see in the tab

You see only your own tabs, never the user's. A `tabs_context_mcp` without `createIfEmpty` reports "No tab group exists for this session" in a fresh session — that is not an empty list but the complete absence of any visibility into existing tabs. With `createIfEmpty: true` a **new, empty** tab comes into being, not the one the user opened. A claude.ai tab opened in advance is therefore neither needed nor reachable.

## Where these statements come from

From the systematic test path for the bridge, which lives in this skill's repository as `chrome-access.en.md` — stages 0 to 8, each attempt with date, starting situation and result, including the attempts whose outcome stayed inconclusive. That file belongs to development and is not part of the installation package. Anyone who doubts a statement here, or has to measure anew after a change to Anthropic's bridge, will find the procedure there.
