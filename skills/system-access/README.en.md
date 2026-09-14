# system-access — rules for working on a live system

*Last updated: 2026-09-15*

*[Deutsche Fassung](https://github.com/fherb2/claude-ai-tooling/blob/master/skills/system-access/README.md)*

**✅☑ Finished and usable.** Instructions complete, frontmatter set, silent trigger present, German and English versions available, installation packages built. — Claude Code only.

---

## Overview

**The skill governs what happens between the task and the first command on a live system — and what keeps the way back open afterwards.** It is built for maintenance work: looking after a server, updating software, tracking down a misconfiguration, finding a vulnerability. That is, for work whose mistakes take effect immediately and in public, rather than staying private and revertible as they do in software development.

It answers four questions, in this order. **Which system** is meant at all — one's own machine, a container on it, a connected or an entirely unconnected foreign one? **Which area** within it has been released, and where do its boundaries run, including the invisible ones formed by mounts, links and network destinations? **What is known about the effect** before intervening — from read-only exploration and from the documentation of the version actually installed, rather than from learned knowledge? And **how does one get back**, if the measure does something other than expected?

To this come three situations that do not occur in software development and are therefore easily overlooked: changes that can cut off one's own access; other people whose work depends on a service; and an access failing on a protection, which is not a defect and must not be circumvented.

**What it does not cover:** ordinary work inside the released project folder. The boundary "no changes outside the project root" belongs to the working instructions and stays there; this skill begins where the work leaves the project folder or intervenes in running programs, services and containers. It also applies to Claude Code only: on claude.ai there is no access to the user's machine, and the rules would have no subject matter there.

## Installation

1. **Download the package.** `downloads/system-access_en_local.zip`

2. **Unpack it.** The archive contains a folder `system-access/` with all the files. Unpack it into `~/.claude/skills/` — then the skill applies to all projects — or into `.claude/skills/` in the project, then only there. An existing folder of the same name is replaced; nothing old is left behind.

3. **Adopt the silent trigger.** You have to do this by hand. Claude then recognizes more easily from the context whether the skill should be loaded. To do it: from `CLAUDE-snippet.md`, **everything below the separator line** goes into the `CLAUDE.md` of the chosen location. The italic text above it stays behind; the file itself stays in the skill folder and shows by its date line which state the adopted trigger is from.

   Without this step the skill only takes effect when called explicitly with `/system-access`.

## Details

### The silent trigger carries a rule core of its own

Its final paragraph is not a summary of the skill but the rule that takes effect **while the skill is not loaded**: a task does not release the means, an environment without an obstacle has permitted nothing, ask before each access separately, change nothing without a way back you can state. This is why this trigger, at roughly 1200 characters, is the longest in the repository, while the others range between 540 and 800.

The reason is the time lag: between the moment a task arrives and the moment the skill is actually in context there is a stretch — after a compaction just as at the start of a session. Along that stretch the paragraph is the only thing protecting anything. **Anyone who takes it for a duplication while shortening and deletes it removes from the skill precisely the effect it was built for.** The header note of the snippet file says so again on the spot.

### Four triggers instead of one

The trigger names topics (server, machine, service, package, configuration, network), an incoming question, one's own action, and the rule core. The second is the earliest and the most important: when a mere question about a computer arrives there is as yet no access to weigh up — the trap is starting to investigate, and doing so on whichever machine happens to be reachable. An anchor tied to one's own action comes too late for that.

The same triggers also appear in the `description`. That is deliberate and not a duplication: the `description` is the route Anthropic provides and works without the user doing anything, while the silent trigger survives a compaction, which the skill listing does not. The two complement each other, and by the developer's measurements the silent trigger is the more important one on the less sensitive models.

### Rules whose simplification destroys the function

- **The area is named, not paraphrased.** "The configuration of service X and its logs" states an area; "I will have a look at what is going on" does not. Without a named boundary the user cannot see what they are agreeing to.
- **The way back belongs to the measure, not to the follow-up.** The sentence "If you cannot name the way back, the measure is not prepared" applies expressly **even against an approval already given**. A careful approval protects against overreach, not against unexpected effect — and the more thoroughly both sides have weighed it, the less anyone expects one.
- **When an access fails on a protection, there is no evasion.** Neither onto another technical route nor towards loosening it. Exactly one narrowing step is allowed on an ambiguous error message, and it must not touch the protected area.
- **The moment is part of the approval.** Consent to a restart is not consent to carrying it out now.

### Origin

The skill brings together two earlier drafts in this repository, which were dropped as a result: `safety_rules` (area boundaries, "automatic" permissions are not an approval, no implicit opening of a project) and `pc-configuration-maintaining` (read-only exploration before intervening, evidence instead of learned knowledge). Added to these are items T29 and T30 from the inventory of the earlier working instructions.

**One departure from `safety_rules` is deliberate:** there, processes running inside the project currently being worked on were exempt. The skill does not know that exemption. Instead the rule hangs on the kind of action — looking at a process does not trigger it, intervening does. The reason: whether a process "belongs to the project" is often not settled at the moment of action, and a project's own service can be the very one on a server that other people's work depends on.

## State and open points

**State.** Finished: instructions, both language versions, silent trigger, and the installation packages for Claude Code.

**Open.**

- Whether the skill needs a trial on a live system before counting as proven has not been decided. Its rules are derived from incidents and from two drafts, not measured in a maintenance session — and unlike the other skills in this repository, a mistake here does not land in a working tree but on a running system.

**Decisions deliberately left open.**

- **Where the intervention record is kept** is not fixed by the skill — it only requires that one be kept and that the location be settled with the user at the outset. On a system there is no obvious counterpart to the Git history, and the right place depends on who owns the system.
- **What exactly "the project folder" covers** in the trigger is for the target project to decide. The term was deliberately chosen to be concrete and thus observable, rather than precise-but-indeterminate ("the released area"): an instance that has not yet loaded the skill does not know what the area is, but it does know where it is working.
- **A hook as a guaranteed trigger** is not provided for. It would be the only construction that forces loading reliably, but it costs on every tool call. Whether that is worth it will only show in use.
