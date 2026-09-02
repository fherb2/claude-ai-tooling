# recall-skills-after-compact — recall the loaded skills after a compaction

*Last updated: 2026-09-02*

*[Deutsche Fassung](README.md)*

**✅ Finished and usable.** Tested against real transcripts and error cases, and proven in the field on a real compaction on 2 September 2026.

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

3. **Wire the hook.** You have to do this by hand. Everything about it is in `settings-json-snippet.md`: the ready-made entry below the separator line, and above it where it belongs, how it is merged into an existing `settings.json`, and — if you did not unpack into `~/.claude/skills/` — how to adjust the path. It also carries a check that verifies the entry right away, without waiting for a compaction; run it, because a wrong path shows up nowhere else. The file stays in the skill folder afterwards; its date line shows which state the adopted entry is from.

   Without this step only the slash invocation `/recall-skills-after-compact` works; the guaranteed trigger on compaction is missing. In this repository the `settings.json` lives on the infra branch — that is where it is changed.

4. **Verify it works:** run `/compact` in a session with at least one skill invocation — the list must then appear as a context note and be presented by the instance.

## Limits

- Only real `Skill` tool invocations are counted. A skill whose rules entered the context another way (say, a rules file loaded directly via Read without a skill invocation) is missing from the list.
- The transcript format is, per Anthropic's documentation, internal and may change between Claude Code versions. If it breaks, the hook goes silent (stderr message, exit 0) instead of disruptive — but the reminder then stays away until the script is updated.
- Prerequisite: `python3` on the PATH. Deliberately no `jq` dependency: on a machine without `jq` the hook would fail silently, and a silent failure is especially treacherous for a reminder hook.
- What can go wrong while wiring it — an unadjusted path, broken JSON, renaming the folder later — is documented where it belongs, in `settings-json-snippet.md`.

## State and open points

**Status:** Built and tested on 2 September 2026 — against three real transcripts (among them a 15 MB session with three skills across six invocations; count identical to an independent manual tally) and three error cases (empty input, missing path, no JSON — all silent on stdout, exit 0).

**Field test passed on 2 September 2026.** In a real compaction the hook fired, the engine recorded it as `hook_success`, and the list then stood in the instance's context, which presented it to the user. That also proves the shell resolves `$HOME` in the hook command — until then it was only an inference from the docs.

**What the test additionally brought to light, and why the capability matters more than expected.** The instance found that after the compaction only three of eleven installed skills were available to it. That is not a defect but documented behavior: "The skill listing does not reload", or "Skill descriptions don't reload" ([Explore the context window](https://code.claude.com/docs/en/context-window)). After a compaction the instance is therefore missing the description listing — **no silent trigger can fire any more**. The reminder list is thus not a convenience but, after a compaction, the only way to learn that anything is missing at all.

**Why the output is this terse and this explicit.** In the same test the instance did more than asked: it checked whether the named skills were still loadable and analyzed the entire skill installation for that. The original wording had invited this by explaining the cap mechanism along the way. Since then the output carries no explanation, only the list and the explicit boundary: report, verify nothing, investigate nothing — "an informational notice, not a task".

**Why the entry uses `$HOME` instead of a placeholder.** The first field test on 2 September 2026 failed, and precisely here: the settings entry still carried the literal placeholder from the snippet, `python3` did not find the file, and because a hook's errors only go to the debug log the failure stayed invisible — the compaction ran, the list did not come. A placeholder that looks like a finished path gets pasted and overlooked. Since then the block carries `$HOME` (the shell resolves it, since hooks are shell commands per the docs), so nothing needs adjusting for the standard location, and the snippet carries a check that verifies the entry without a compaction.

**Open:** Nothing. The capability has been proven in the field.

**License:** CC0-1.0, like the other skills of this repository.
