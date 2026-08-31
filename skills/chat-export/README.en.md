# chat-export — Bring chats from claude.ai into your project

*Last updated: 2026-08-31*

*Usable with Claude Code.*

**This skill fetches chats from your claude.ai projects and stores them as searchable JSON files in the project Claude Code is currently running in.** They are meant for finding earlier context again: what was once discussed in a chat is afterward findable in the project, instead of sitting only in the account.

Chats that keep growing, as well as new chats, can be updated or added later on.

What results from this are archive files, not chats you can continue. An imported chat can be read and searched, but not continued from here.

## Installation

1. **Download the package.** `downloads/chat-export_en_local.zip`

2. **Unpack it.** The archive contains a folder `chat-export/` with all the files. Unpack it into `~/.claude/skills/` — then the skill applies to all your projects — or into `.claude/skills/` in the project, then only there. An existing folder of the same name is replaced; nothing old is left behind.

This skill needs no silent trigger: it fires through its `description` or is called with `/chat-export`. And renaming the instruction file falls away — inside the package it is already called `SKILL.md`, in the language the package name states.

Besides the instruction file the folder holds three more files: the helper script `chat_export_convert.py`, without which the skill does not work; this README as documentation for you; and `bridge-diagnosis.en.md`, a failure diagnosis for the Chrome connection that Claude reads only when it actually goes wrong.

## Usage

### Prerequisites

> A note on the Claude Chrome extension:
>
> As of 08/2026, the procedure with the extension described here has been tested against the beta version, and getting the bridge (see below) to actually come up can sometimes be a bit of a hassle. Hopefully Anthropic will make this friendlier for users going forward.

**Set up once:**

Points 1 and 3 correspond to a full install of the Claude Chrome extension and are a prerequisite you may already have set up for other purposes.

1. **Install the Claude extension in Chrome** and establish the connection to Claude Code once: run `claude --chrome` in the terminal. This creates the file through which Claude Code talks to the extension. **Fully restart Chrome afterward** — the file is only read at startup.
2. **Turn off the download prompt in Chrome:** *Settings → Downloads → "Ask where to save each file before downloading"* off. If it stays on, the first download opens a file dialog, and that cripples the connection to the browser ([why](#why-a-browser-is-needed)).
3. **Turn on the connector on claude.ai:** *Settings → Connectors → "Claude in Chrome"*. This applies per account and does not act retroactively on already-open tabs.

**For every run:**

4. **Chrome is running.** One window is enough; claude.ai itself does not need to be open, the skill opens its own tab.
5. **Claude Code is running in the project you want to import into.** The target is always the project you're currently working in — the skill fetches the chats to wherever the session is. You can also use the VS Code Claude Code extension for this.
6. You first have to **establish the bridge between Claude Code and the Chrome Claude extension**. The simplest route is to use the same account in Chrome as in Claude Code — **but it is not required.** The bridge follows only the claude.ai session currently open in the tab; checked twice, once of them after a full machine restart with different accounts from the start. Anthropic's own error message claims the accounts must match anyway — take that as one possible cause among several, not as a condition. Then open the Claude chat window of the Claude Chrome extension: if it starts up and does not say that a login is still needed, you're fine. If it does need a login, log in. At that point at the latest, the Claude Chrome extension is genuinely connected to the account. If the bridge still does not come up, or breaks off later, tell Claude: the skill brings its own failure diagnosis along and assigns the messages to their cause. The full test path with all logged failure patterns lives in this skill's repository.
7. **Now establish the bridge from Claude Code** by passing `@browser` at the prompt. (You can dismiss the autocomplete suggestion that usually pops up by adding a space after @browser.)
8. **Finally, ask Claude Code** whether it can open a tab in Chrome. Only once that works does the bridge actually stand.
9. If you want **to import chats from a different Claude account**, you can now log out of Claude.ai in a new tab in Chrome and log in with the other account. An email turn is probably required here. This does not break the bridge.

   ---

   **Once you've reached this point, Claude Code — wherever you want to import the chats to — can work with whichever claude.ai account Chrome happens to be logged into at that moment, in order to export the chats from there.**

   ---
10. You now switch to **Claude Code in the project you want to import into.** The skill fetches the chats here, to wherever the session is, and uses the access via Chrome to reach the source data.

### The first prompt for export and import

As mentioned: you're in the Claude instance in the target project. The skill has to be known there.

In the steps above you already passed `@browser` on this prompt, which keeps showing above the prompt from here on. If you think this bridge is broken, you can ask the instance directly via the prompt, or it will report so on its own. Without this bridge, the skill has no access to Chrome and thus to the source. **Now you can begin:**

```
I'd like to export chats from a project and import them here. You're already
connected to the source via Chrome. Please first give me a list of all
projects there, then I'll tell you more precisely which project it is.
```

You have fairly free rein in how you phrase the request. You can also name the project right away, or even list several projects. Let Claude guide you through the rest of the session.

If the source is not a Team account, you have the option of doing the export via a download. Claude will advise you on this. In Team accounts this option does not exist, and Claude is then left with only the export via the browser, which it operates in Chrome.

### The procedure

Claude guides you through the export via the skill and asks wherever it needs a decision or write access. Everything in between runs through on its own, because it's only reading.

**Claude names the account.** Unprompted, as soon as it knows it:

```
Chrome is logged into claude.ai as: maxebaumann@gmx.de's Organization
That's where I'll look for the projects.
```

If that's not the account you wanted to import from, switch it in Chrome now at the latest and let it start over ([why it states this](#why-the-skill-states-the-account-instead-of-asking-for-it)).

**Claude clarifies which projects are meant.** Three cases, depending on what you said:

- You **named** the projects — it matches them against the real list and moves on. If a name only roughly fits, it asks once briefly ("*Project ABC* doesn't match literally — do you mean *Project A-B-C*?").
- You want **to see what's there first** — then it presents the account's projects, sorted by last change, noting what's already stored in the target project. You choose.
- Only **a single archive** is present in the project and you say nothing further — then it takes that one and says that it's taking it.

**Claude fetches the statistics and presents them.** One line per project:

```
Project                 Archive Source   new  grown  vanished  Recommendation
Project A-B-C              34      39     5      2         1  Web
Some Other Project         22      23     1      0         0  Web
```

*Archive* is the state in the project, *Source* the one in the account. *New* are chats that were never fetched before, *grown* are ones that have been continued since last time, *vanished* are ones the account no longer carries ([what happens with those](#why-a-vanished-chat-stays-in-place)). Up to this point, nothing has been fetched and nothing written ([why counting comes first](#why-only-counting-happens-first)).

**You choose the route.** This is the second and last checkpoint. The skill presents both routes (export via archive and a download link by email, or export directly via the web interface in Chrome) with their cost and **recommends** one, but doesn't decide ([why not](#why-you-choose-the-route-not-the-skill)). One answer suffices for all projects; you may also split it up ("export for A-B-C, web for all the others").

**Claude announces what happens next** — with numbers, because files also get replaced and removed in the process. This is no longer a checkpoint, just the final announcement before the run.

**Claude runs and reports.** With the web route, you see progress chat by chat. At the end stands what was written and what was replaced — replaced files named individually — and an explicit closing sentence that it's done ([what ends up in the folder](#what-ends-up-in-the-folder-in-the-end)).

### The two routes

Both deliver **the same result**: the same files, the same content — including the same gaps ([what fundamentally doesn't come along](#what-doesnt-come-along)). They differ only in how the chats come out of the account.

**Web route** — the skill reads the chats directly via your logged-in Chrome browser. No waiting, it starts right away. In exchange, it fetches throttled, with a four-to-twelve-second gap per chat; with many chats that adds up. The right choice for **a handful of chats**, say when you're catching up regularly.

**Export route** — you request a data export of your account from claude.ai. The skill fills in the request in the browser and presents you the submit button; it states the date the export has to reach back to, and gives the reason. After that, **the chain breaks**: the download link arrives by email and is valid for 24 hours. The skill does not go into your inbox — you download the file and say so, and it finds the rest by itself. The right choice for **many chats or large attachments**, because everything arrives in one go, with no load per chat.

> **In Team and Enterprise accounts, this export route doesn't exist** — there, only the organization's Primary Owner can export. For an ordinary member, the web route is thus not the more convenient option, but the **only** one.

### If something snags

**"The browser tools are not attached to this message."** The `@browser` at the start of the message is missing.

**"Browser extension is not connected."** Sounds like a broken setup, but usually just means Chrome isn't running right now — or the extension itself isn't logged in. That's separate from being logged into the claude.ai page: you can check it by opening a chat in the extension itself.

**"Claude in Chrome is turned off in your settings."** The connector isn't turned on for this account (prerequisite 3). After turning it on, you have to reload the affected tab — the setting doesn't act on tabs already open.

**A file dialog opens and nothing moves on.** Then the download prompt was still on after all (prerequisite 2). Click the dialog away, turn off the setting, and let the skill start over.

**A security check from claude.ai.** The skill does not bypass it and shouldn't. It stops, you click it away, it continues where it was — chats it already fetched are not fetched again.

### The target folder — using the imported chats

Claude will suggest a target folder within the project. Pay attention to whether you want to push this folder to a remote repo.

If you want to point Claude Code, within the project, toward searching earlier chats for something, just tell it where the chats are. The chats are formatted in a way Claude can navigate very well.

What unfortunately doesn't work: continuing these chats in Claude Code. But just tell Claude what to read and that you want to pick that chat back up here. That way Claude knows the context of the old chat and you can build on it right away.

### If you want to top up with more chats later

The skill can add to an archive at any time: fetch new chats and replace ones that have grown. For that to still work half a year from now, there are four things to get right the first time. None of them costs anything, and none can be repaired afterwards without editing by hand.

**One folder per claude.ai project.** Do not put the chats of several projects into the same folder. The `protocol.json` there tracks the state of **one** project; a second project overwrites its start date, and after that a requested export no longer reaches far enough back. The chats already in the folder stay complete — what goes wrong is only the calculation of what is still missing. And that calculation is then unusable.

**Keep the folder, `protocol.json` included.** That is the state the skill reads to know what it already has. If you additionally upload the chats into the project knowledge of a claude.ai instance, that is a **copy** — topping up always happens from the local folder. Delete it and the skill starts over and fetches everything again.

**Do not put the archive under `~/.claude/projects/` if it is meant to last.** Claude Code cleans up there after a retention period (30 days by default), and `claude project purge` takes the folder with it. If you want that location anyway — it makes sense for chats that must not go into a shared repo — raise the retention period first.

**A single chat file does not say which project it came from.** That lives in the folder name and in the protocol, not in the file. If you pass one file on by itself, say where it came from.

### One note that has nothing to do with this skill

The skill cannot read your **Claude Code sessions** — it fetches chats from claude.ai, not from Claude Code. Those local sessions are cleaned up after `cleanupPeriodDays`, by default after 30 days.

If you can imagine ever wanting the context of an old Claude Code session: **raise that period now**, in `~/.claude/settings.json`. Later it has no effect — what is gone is gone. The period costs nothing but disk space, and you never know in time which chat you will need.

## Background

This part explains why the skill asks for what, and what it does with your answers. You don't need it to use the skill.

### Why a browser is needed

Your chats live in your claude.ai account, not on your hard drive. Claude Code alone cannot reach them: it has no access to your account and cannot get any either. What it does have is the route via **your** browser — you're already logged in there, and the skill uses exactly this existing login to read the chats. It never logs in anywhere itself and knows no password of yours.

Everything else follows from that: Chrome has to be running, because there's no connection to a closed browser. And a file dialog in the browser blocks everything, because the browser stops accepting commands while it's open — hence the setting about the download prompt, ahead of the very first download.

### Why the skill states the account instead of asking for it

Nobody double-checks assurances. If the skill asked you "are you logged into the right account?", your answer would at best be a guess — and the most common mistake would be exactly the one neither of you would notice: **the same project name can exist in a second account.** A match based only on the name would silently keep writing to the wrong archive.

That's why the skill states what it actually finds, as soon as it knows it. That also catches the case where no login exists at all.

That Chrome and Claude Code are allowed to be on different accounts is not an oversight here, but something that has been verified: the skill always sees whichever session is currently active in the browser. For you, that means you determine the source account by switching accounts in Chrome — not by which account you use Claude Code with.

### Why only counting happens first

Before any chat is fetched, the skill compares the account's chat list with what's already stored in the project. That costs nothing and answers the question you need for your decision: **how much** is missing in the first place. Five chats to catch up on is a matter of minutes, two hundred is a very different matter — and only with this number can the route be chosen sensibly.

The second reason is reliability. Everything that gets counted and compared is computed by a script that actually reads the files — not by the Claude instance from memory. When summing things up, a language model gets it wrong, silently: in one trial it stated ten entries where there were nine. Every number you see therefore comes from a script run.

### Why you choose the route, not the skill

The two routes differ in a trade-off nobody can make for you: **wait time against load.** The web route starts right away, but fetches chat after chat via the ordinary web interface — with many chats, that's a noticeable sustained load on a service you share with others. Hence the brake of four to twelve seconds, scattered at random: it keeps the load low and avoids the regular pattern a bulk fetch would otherwise show.

The export route places no load at all, because it produces a single package — but when it's ready is up to claude.ai, not you, and the link expires after 24 hours.

Which one fits better depends on your situation: how urgent it is, how many chats are missing, how big their attachments are. The skill computes this for you and recommends; you're the one who decides.

### Why a vanished chat stays in place

If the account no longer carries a chat the project knows about, the skill reports it — and **removes nothing**. The reason: from the outside, three entirely different causes cannot be told apart.

The chat may have been **deleted** at the source. It may have been **moved to another project** and be living on there unchanged. Or the list simply **wasn't paged all the way to the end**. In the third case, an automatic deletion would be data loss from a usage mistake — and the silent kind at that, the one nobody notices.

That's why the decision stays with you. The skill tells you which chat is affected; whether its files should disappear is for you to decide, and nobody else.

### What ends up in the folder, in the end

The chats land under `<project>/.claude/imported_chats/<source-project>/` — a flat folder per claude.ai project, with no subfolders. If you want them somewhere else, say so when calling the skill; it then uses that location instead.

Each chat produces a **conversation file** with the exchanged messages, named after the chat's date, title, and ID — so it can be found by its filename alone, before it's even opened. Alongside it, whenever the chat provides them, sit up to three extra files: one with the **reasoning** that led to the answers, one with the **content of uploaded files**, and one with what **the AI produced** — artifacts, generated files, code changes.

They sit apart because otherwise they would multiply the volume: the reasoning alone is nearly as long as the conversation itself. Whoever reads a chat back generally wants the conversation — the extra files are there when you need them, and don't get in the way when you don't.

On top of that comes a `protocol.json`. It keeps track of which chats were fetched and what state they were in. Only because of that can a later run tell what's new and what has grown — without it, every import would be starting from scratch.

If a chat that has grown is fetched again, its new version **replaces** the old one completely; the old files are removed beforehand, and named individually as that happens. There is no silent deletion here.

### What doesn't come along

Not everything that was visible in a chat ends up in the archive afterward — partly because Anthropic doesn't hand it out, partly because it would bloat the archive to the point of being unusable.

**Images and other non-text attachments** come only as a filename. Their content simply isn't included in what the account hands out. Text files, on the other hand, come along in full.

**Tool calls and their results** are counted but not stored. This is by far the largest item and consists mostly of material that's already available elsewhere anyway — file contents, search results, intermediate steps.

**The reasoning may be missing.** This isn't a quirk of this skill: Claude sometimes writes it out and sometimes doesn't, within the very same source — measured, it switched from one day to the next inside a single chat. What it depends on is not known. In practice this means an archive without reasoning is a sample, not a defect of the tool, and nobody can fetch more than is there. Attachments and creations are unaffected.

**Deleted chats** still appear in the export as an empty shell, with no text. The skill recognizes and marks them; nobody can bring them back.
