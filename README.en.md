# Claude-AI-Tooling

*[Deutsche Fassung](README.md)*

Tools / components for the daily work with Claude — claude.ai, Claude Desktop and Claude Code. Self-contained components, each with its own documentation in its folder. This page is the overview only. Use the linked READMEs inside the components.

## What there is


| Component                                                                 | What it addresses                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`pack-source-to-txt/`](pack-source-to-txt/README.en.md)<br>✅ | **The whole project codebase as a single file**: precise, up-to-date project context for an AI without access to the machine.                                                                                                      |
| [`chat-export/`](chat-export/README.md) (in German)<br>🚧 | **Transferring chats from Claude.ai between different user accounts, or sorted by project, into local Claude instances** (Claude Code) — which Anthropic does not offer so far.                                                   |
| [`home-.claude-sharing/`](home-.claude-sharing/README.md) (in German)<br>⚠️ | **Working across several machines**: chat memory and working instructions / skills instead of many separate ones spread over the systems: `~/.claude` in sync on all machines, conflicts are reported and resolved under guidance. |
| [`skills/`](skills/README.en.md)<br>☑ | Instead of many CLAUDE.md instructions:**have the rules loaded automatically**. In the context first and only when actually needed: Claude Code **skills with a "silent" trigger**.                                                |

(✅ ready to use · 🚧 in progress · ⚠️ with reservations · ☑ depends on the skill)

### **Usage notes** further down in this README:

* **[Chat retention in Claude Code](#chat-retention-in-claude-code)**

## pack-source-to-txt (not limited to Claude)

**Purpose:** code analysis and further development on web-based agent instances; use in weakly secured areas: no direct system access.

**A single, self-contained shell script (`packsrc.sh`) that bundles a project's source files into one structured text file — ready for upload to the knowledge base of a web AI agent.** Every file sits inside unambiguous metadata blocks carrying a run-related timestamp and the date of its last change, and an AI-readable header explains to the agent how to interpret them. Source directories, file extensions, explicit individual files and directory exclusions are configurable; an acceptance test under `tests/` secures the behavior. Needs nothing but Bash and the GNU tools, no further dependencies.

**Note:** by default, Claude Code throws chats away after 30 days. That limit can be turned up as far as you like.

**Status:** in production use — more in the [component's README](pack-source-to-txt/README.en.md).

## chat-export

**Purpose:** **importing chats from Claude.ai between different user accounts, or sorted by project, into local Claude instances (Claude Code)** is something Anthropic does not support at present (08/2026). – With this tooling it works anyway.

The existing data export interface is not directly suited to this and is used by this tooling only indirectly. The tool supports importing project by project and also allows the "reloading" of chats that had already been begun at the time of the last import. Not a simple one-click solution. – Instead, a solution at all, for a start.

**Status:** in progress, not quite finished yet. — More in the [component's README](chat-export/README.md) (in German).

## home-.claude-sharing

**Purpose: keeps the working state of Claude Desktop and Claude Code — configuration, session logs, project memory — in sync between several machines via Syncthing. – Switching machines between home and office, or remote and local. Needs neither a VPN nor a local network for that.**

An always-on NAS node acts as the intermediary. The actual core is dealing with what Syncthing deliberately leaves unsolved: files changed at the same time are put aside as conflict copies, a watcher service discovers them, reports in and guides the user, together with Claude, through resolving them by content. Installation scripts, the service definition and a setup guide for the intermediary node are included.

**Status:** in operation at the developer's, not yet released for distribution — more in the [component's README](home-.claude-sharing/README.md) (in German).

## skills

**Purpose: get instructions out of CLAUDE.md and make task descriptions reusable.** Skills also start without a matching "trigger word".

Reusable skills for Claude Code: instructions that do not permanently cost context in `CLAUDE.md` files but are loaded only once they are needed.

Along with that, the concept of **silent triggers** developed here — triggers for situations nobody puts into words. The Anthropic standard has a skill either started by the user or fired automatically on trigger words given in the skill's `description:`; silent triggers extend that by a start out of the context of the chat. This is not an extension of Claude Code, but is achieved through particular rules of wording in CLAUDE.md. Details on reuse in this component.

**Status:** the status of the individual skills is stated separately in the [corresponding README](skills/README.en.md).

## Usage notes

### Chat retention in Claude Code

Claude Code stores chats, along with the data belonging to them and backup copies of the files it is about to change, under `~/.claude/`. **By default the retention period is a mere 30 days. Whoever wants to fall back on the knowledge in those chats later on has no chance.**

The retention period can be **reconfigured** in `~/.claude/settings.json` with the `cleanupPeriodDays` key.

**Example for 3 years:**

```json
{
  "cleanupPeriodDays": 1095
}
```

In principle the key is permitted at every settings level — `~/.claude/settings.json` (user), `<project>/.claude/settings.json`, `<project>/.claude/settings.local.json`.

**Some paths are exempt from this, though** — above all `history.jsonl` (every prompt ever typed, with timestamp and project path) and the auto memory under `projects/<project>/memory/`. Those stay on indefinitely. So whoever reads the retention period as a privacy control does not get far with `cleanupPeriodDays` alone; for that, the documentation additionally names `CLAUDE_CODE_SKIP_PROMPT_HISTORY` and `claude project purge`.

## License

This repository does not set a common license. Each component settles its license of use individually in its own README — which is also where it says what is released for distribution / use.
