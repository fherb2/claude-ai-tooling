# recall-skills-after-compact — recall the loaded skills after a compaction

*Last updated: 2026-09-02*

*[Deutsche Fassung](README.md)*

**✅ Finished and usable.** Script tested against real transcripts and error cases; the field test on a real compaction is still pending (see "State and open points").

**After every context compaction this capability presents the instance — and through it the user — with the list of skills already loaded in the session.** The decision whether and which of them to reload stays with the user; nothing is reloaded on its own. This is the repository's first **guaranteed capability**: it is triggered not by a silent trigger but by a **hook** — an event handler of the Claude Code engine that always runs on its event. In addition it can be invoked by hand at any time: `/recall-skills-after-compact` answers, mid-session, the question "which skills have been loaded here so far?" — the same script, second ignition path.

**Why it is needed.** A compaction replaces the conversation history with a summary. Claude Code does re-inject the `SKILL.md` texts of invoked skills automatically afterwards — but capped (5,000 tokens per skill, 25,000 in total, oldest dropped first) and **without** the lazily loaded rules files, which in two-part skills carry the actual rules. The silent triggers only fire again on the next matching occasion. In between, nobody knows what is missing — missing content leaves no hole in the context. The reminder list closes that gap.

## How it works

- **Anchor:** a `SessionStart` hook with matcher `compact`. Fires on automatic compaction and on a manual `/compact`; deliberately **not** on `/clear` — a fresh start is meant to be empty.
- **Path:** the script reads the hook's stdin JSON, takes `transcript_path` from it (a documented input field), walks the session transcript line by line, and collects all `Skill` tool invocations of the main conversation (subagent sidechains deliberately excluded) — deduplicated, with count and last timestamp.
- **Output:** the list goes to stdout, and stdout of a `SessionStart` hook is documented to be added to the instance's context ("adds plain-text stdout as context that Claude can see and act on"). The text is English only — it is machine input; the instance presents the list to the user in the chat language.
- **On demand:** when invoked via `/recall-skills-after-compact`, the instance passes the transcript path as an argument; the script then prints only the list. The `SKILL.md` carries `disable-model-invocation: true` — it costs no permanent context (per the docs its description is then not in the listing) and can only be started by the user.
- **Error behavior:** an empty result or any error (broken input JSON, missing or unreadable transcript path) produces, in hook mode, **no** stdout output — only a stderr message — and exit 0. The session is never disturbed.

## Installation

##### Claude Code

1. **Download the package.** `downloads/recall-skills-after-compact_en_local.zip`

2. **Unpack it.** The archive contains a folder `recall-skills-after-compact/` with all the files. Unpack it into `~/.claude/skills/` — then the capability applies to all projects — or into `.claude/skills/` in the project, then only there. An existing folder of the same name is replaced; nothing old is left behind.

3. **Wire the hook.** You have to do this by hand. Everything about it is in `settings-json-snippet.md`: the ready-made entry below the separator line, and above it where it belongs, how it is merged into an existing `settings.json`, and which path to adjust. The file stays in the skill folder afterwards; its date line shows which state the adopted entry is from.

   Without this step only the slash invocation `/recall-skills-after-compact` works; the guaranteed trigger on compaction is missing. In this repository the `settings.json` lives on the infra branch — that is where it is changed.

4. **Verify it works:** run `/compact` in a session with at least one skill invocation — the list must then appear as a context note and be presented by the instance.

## Limits

- Only real `Skill` tool invocations are counted. A skill whose rules entered the context another way (say, a rules file loaded directly via Read without a skill invocation) is missing from the list.
- The transcript format is, per Anthropic's documentation, internal and may change between Claude Code versions. If it breaks, the hook goes silent (stderr message, exit 0) instead of disruptive — but the reminder then stays away until the script is updated.
- Prerequisite: `python3` on the PATH. Deliberately no `jq` dependency: on a machine without `jq` the hook would fail silently, and a silent failure is especially treacherous for a reminder hook.
- What can go wrong while wiring it — an unadjusted path, broken JSON, renaming the folder later — is documented where it belongs, in `settings-json-snippet.md`.

## State and open points

**Status:** Built and tested on 2 September 2026 — against three real transcripts (among them a 15 MB session with three skills across six invocations; count identical to an independent manual tally) and three error cases (empty input, missing path, no JSON — all silent on stdout, exit 0).

**Open:** The field test on a real compaction — the next long session due for one will run it.

**License:** CC0-1.0, like the other skills of this repository.
