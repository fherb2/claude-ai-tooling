# Syncthing sync for `~/.claude`

*Last updated: 2026-09-15*

*[Deutsche Fassung](https://github.com/fherb2/claude-ai-tooling/blob/master/home-.claude-sharing/README.md)*

**Keeps the working state of Claude Code and Claude Desktop — configuration, session transcripts, project memory — automatically in sync across several machines, so the same context is available everywhere. And it reports the exceptional case a synchronisation cannot resolve by itself: the file that was changed on both sides.**

The sync has been running since 11 August 2026, tried and tested across three machines and more; the watcher runs there as a service and has handled real conflicts. The implementation is complete; the only open item is a counterpart for Windows (`work-plan.md`).

A note on language: the package you install decides it. The English package carries an English message catalogue and an English working instruction, so dialogs, notifications, journal lines and the conflict session itself speak English; the German package speaks German. There is nothing to configure. The two setup scripts are English in both packages — setting up runs once and is the first contact with the tool. The strings quoted below are the English ones, verbatim.

## Purpose

Claude Code, Claude Desktop and the VSCode extension keep their entire working state in the `~/.claude` directory of the respective machine. Anyone working on several machines therefore has several independent memories: what was worked out on the laptop does not exist on the office machine.

The synchronisation itself is done entirely by Syncthing, through an always-on node on a NAS of your own. The participating machines need neither to see each other nor to be switched on at the same time — each one knows only the node. That is why everything described here holds for **any number** of machines, not just for two.

The contribution of this project lies elsewhere: Syncthing deliberately does **not** merge files that were changed on two machines at once. It puts the losing version next to the original as a conflict copy — and tells nobody. That is where this tool comes in: a watcher discovers such copies, reports them, and guides the user through resolving them together with Claude.

## What travels — and what does not

Everything in `~/.claude` is synchronised, including the session transcripts and chats under `projects/` — they are the actual point of the exercise. Excluded is whatever the ignore list `.stignore` names; which pattern is there for what reason is set out in chapter 3.9 of the documentation. Next to it sits a second list for a single machine — see the next chapter.

Four points worth knowing beforehand:

- **Credentials never travel.** `.credentials.json` is excluded, and that line must be present in `~/.claude/.stignore` on **every** machine **before** the folder is first connected there. The file itself does not travel — Syncthing never synchronises it.
- **`/rewind` across machine boundaries is gone.** The snapshots under `file-history/` are excluded: they refer to absolute paths of the machine that created them, and their write pattern is the worst in the whole folder for a synchronisation. Whoever continues a session on the other machine has no checkpoints to roll back to there. That is what the project's version control is for.
- **MCP servers in user and local scope stay local.** They live in `~/.claude.json`, which is **outside** the synchronised folder. Whoever sets up an MCP server on one machine enters it again on the other. This does not apply to the project scope: `.mcp.json` belongs in the project's repository and travels with it.
- **Login and device state stay local** — likewise `~/.claude.json`. Switching accounts is therefore a purely local affair and produces no conflicts.

## Keeping single projects off one machine

Not every machine should get everything. A workplace machine can take the configuration, the skills and the `CLAUDE.md` in full, but of the session transcripts under `projects/` only selected projects — and none of the rest. That is what a **second exclusion list** is for, `~/.claude/.stignore-local`.

### Why there are two lists

`.stignore` has an authoritative version that is the same on every machine; `install_service.sh` compares it at every update and offers to take it over, defaulting to yes. Whoever writes their own lines in there loses them at the next update — silently, because pressing return is enough.

`.stignore-local`, by contrast, is only created when it is missing and is **never overwritten**. It ships empty and is pulled in by the authoritative list with `#include`, placed high up: **local patterns take precedence over the general ones.** That also lets you make an exception from a general exclusion here. Only the line for the credentials sits above it, out of reach from here.

The file excludes itself from the synchronisation — otherwise one machine's selection would travel to all the others.

### Four rules by which Syncthing reads the patterns

Everything else follows from these four ([Ignoring Files](https://docs.syncthing.net/users/ignoring.html)):

1. **The first matching line decides** a file's fate. Exceptions with `!` must therefore sit **above** the pattern they take out of.
2. **`*` does not match the path separator, `**` does.** `/projects/*` hits only the topmost level, `/projects/**` every path below it.
3. **Comments start with `//`, not with `#`.** The `#` is reserved for directives such as `#include`; a line `# my comment` is not a comment but is read as a pattern or as an unknown directive — and it does not announce itself.
4. **Leading and trailing spaces are trimmed**, blank lines are allowed.

### What a project folder is called

Under `projects/`, Claude Code creates one folder per **working directory**, not per project. The name is built from the path, with **every** special character turned into a hyphen, the dot included. A typical set:

    -home-mustermann                                  ← session straight in the home directory
    -home-mustermann--claude                          ← /home/mustermann/.claude, two hyphens
    -home-mustermann-Downloads
    -home-mustermann-Music
    -home-mustermann-git-image-pipeline
    -home-mustermann-git-image-pipeline-calibration   ← session in a subfolder
    -home-mustermann-git-sensor-firmware
    -home-mustermann-git-sensor-firmware-docs
    -tmp                                              ← session in /tmp
    -var-log-analysis                                 ← session in /var/log/analysis

Two things follow from this, and both are easily missed:

**One project is often several entries.** Start a session in a subfolder and you get a second folder whose name carries the first as its prefix. Allow only the first, and those sessions are missing on the other machines.

**Read the name off, do not construct it.** `ls ~/.claude/projects/` shows what it really is.

### Example A — take a single project

This machine is to receive `image-pipeline` and nothing else from the session transcripts:

    // this project only, including sessions from its subfolders
    !/projects/-home-mustermann-git-image-pipeline
    !/projects/-home-mustermann-git-image-pipeline/**
    !/projects/-home-mustermann-git-image-pipeline-*
    !/projects/-home-mustermann-git-image-pipeline-*/**

    // everything else under projects/
    /projects/**

From the set above, `-home-mustermann-git-image-pipeline` and `-home-mustermann-git-image-pipeline-calibration` remain; the other eight drop out.

**The two `-*` lines have a price:** a separate neighbouring project whose name happens to start the same way — `image-pipeline-old`, say — is caught as well. If one exists, list the subfolders individually instead.

### Example B — your own home directory and all git projects

    // own home directory and everything under ~/git
    !/projects/-home-mustermann
    !/projects/-home-mustermann/**
    !/projects/-home-mustermann-git-*
    !/projects/-home-mustermann-git-*/**

    // all other folders of the own home directory
    /projects/-home-mustermann-*
    /projects/-home-mustermann-*/**

Here **one** asterisk suffices for the subfolder projects, because they all carry the same prefix: `-home-mustermann-git-*` catches `…-image-pipeline-calibration` too.

**This version has a gap**, and it is the reason for the next example: it only blocks what begins with `-home-mustermann-`. `-tmp` and `-var-log-analysis` would come through — and such entries appear as soon as you start Claude Code once in `/tmp`, `/var/log/…` or anywhere else outside your home directory.

### Example C — the same selection, sealed

    // own home directory and everything under ~/git
    !/projects/-home-mustermann
    !/projects/-home-mustermann/**
    !/projects/-home-mustermann-git-*
    !/projects/-home-mustermann-git-*/**

    // everything else, whatever directory it came from
    /projects/**

The difference is the last line. `/projects/**` catches **every** entry, whatever its name — so you need not know the possible names at all. Only what is explicitly allowed above gets through.

That also makes the two `-home-mustermann` lines load-bearing, which they were not in example B: before, no pattern matched them; now the catch-all does, and only the exception brings them back.

**This is the form to prefer.** An allowlist errs in the harmless direction: a forgotten entry costs you a project missing on this machine. With a list of exclusions, a newly created project lands where it should not, unasked.

### Excluding means both at once

Whatever is excluded here is **neither received nor sent**. A one-way street — send from here but receive nothing — does not exist in Syncthing for individual subfolders: the direction setting ("Send Only", "Receive Only") always applies to the whole folder and cannot be varied per remote device either.

What you shut out here of course stays on the other machines. It just does not arrive here.

### Two things sit outside `projects/`

Project-related content is not only in the session transcripts:

| Location | what is in it |
| --- | --- |
| `history.jsonl` | every prompt you typed, with timestamp and project path |
| `paste-cache/` | the pasted text that went with them |

Neither can be **split by project** — the history is a single file across all projects, and the paste files carry only a hash in their name. For a machine with a selection it is all or nothing:

    /history.jsonl
    /paste-cache

The price affects this machine alone: up-arrow recall, `Ctrl+R` search and `!` shell-command completion then draw only on what was typed here.

### Checking that the patterns really bite

A badly formed pattern looks as though it works. The probe uses a harmless file rather than the real thing:

```bash
# on this machine
echo "probe 1" > ~/.claude/probe-pattern.txt
# → on another machine, wait for it to arrive

echo "/probe-pattern.txt" >> ~/.claude/.stignore-local
# → in Syncthing (http://127.0.0.1:8384), have the folder rescanned once

echo "probe 2" > ~/.claude/probe-pattern.txt
# → on the other machine the change must NOT arrive any more
```

Then remove the entry and delete the probe file everywhere. The rescan belongs to it: when Syncthing reads a changed ignore list by itself is stated nowhere in its documentation.

### Excluding after the fact — the order decides

If what you want excluded has already been synchronised, everything hangs on what happens first. Three cases:

1. **It keeps being recreated** (`backups/`, say): set the pattern first and let it take effect, **then** delete. The deletion then stays local, so it is needed on every machine separately.
2. **Deleting before the pattern**: the deletion travels to everyone — and whatever creates the file writes it again at once. That goes back and forth.
3. **A one-off file that nothing recreates**: just delete it. The deletion travels everywhere, which is exactly right here.

**A pattern deletes nothing.** Whatever is already on disk stays there — Syncthing merely stops maintaining it. If you want the space back, delete it yourself.

**Before every update**, check whether `~/.claude/.stignore` carries lines of your own — see "Updating an existing installation".

## Prerequisites

### A node that is always running

The sync needs a place that **all** participating machines can reach and that runs permanently — here a Synology NAS, but any permanently reachable machine will do. This is not a convenience but a condition: Syncthing's public relay servers **store nothing**, they only forward between two devices that are connected **at the same time**. Two machines that are never online together do not sync through them.

The node therefore runs a full Syncthing instance holding a **complete copy** of the folder. The data flow is machine A → node → machine B, without A and B ever meeting; the folder thus exists three times over, plus the space for versioning on the node.

What has to be set up there — the individual steps are in `syncthing-synology-setup-guide.md` (German), here only what matters:

- **Device pairing, mutual and star-shaped** (section 6): the node knows every machine, every machine knows only the node. The machines are **not** paired with each other.
- **"Introducer" stays off everywhere** (6). With that option set, a device passes the device IDs known to it on to its peers — the node would make the machines known to each other, and they would try to connect directly.
- **Port forwarding and firewall only at the node** (4, 5). Syncthing establishes connections in both directions; it is enough that the node is reachable. Workstations behind a NAT router need no forwarding of their own.
- **A fixed address for the node** (6): in the device entry on the machines, under *Advanced → Addresses*, use `tcp://your-domain.tld:22000` instead of `dynamic`.
- **File versioning "Staggered" at the node** (9). It receives from all machines and is thus the only place with a complete archive — the emergency fallback depends on it (see "When something is broken"). On the workstations, "Trash Can" or "Simple" is enough.
- **Folder type "Send & Receive" on all devices** (7). "Receive Only" at the node would be wrong: it has to pass one machine's changes on to the others.
- **The folder is created first on the machine that holds the content** (7) — not on the empty node, or the empty state gets distributed.

### If the machines can reach each other

Syncthing is a peer-to-peer tool at heart: pairing machines directly is permissible, and the watcher does not notice either way — it only looks at file names in the synchronised folder. The setup of the node is then replaced by the initial setup on the first machine (see below).

**Two properties are lost in the process**, and both carry weight here:

- **The sync then requires simultaneity.** Whoever works alternately on two machines and switches one off before the other is running never transfers anything.
- **The emergency fallback loses its source.** Syncthing archives only **incoming** foreign changes before overwriting, never your own. Without a device that receives from everyone, only the local `.stversions/` remains — and that is exactly what does not preserve your own botched write.

The always-on node is therefore the way described and recommended here.

### On every participating machine

The installation script checks them one by one and **in this order** — it aborts on the first hard failure, so you do not learn after ten messages that it cannot proceed at all.

**Abort if missing:**

| Prerequisite | why it is hard |
| --- | --- |
| a controlling terminal | Every step after it may ask, and `sudo` reads its password from there. Without a terminal a question could not be answered. Checked by **opening** `/dev/tty` |
| the tool folder sits in `~/.claude-sync-watch` | The service definition hardcodes that path. If it is elsewhere, the script names the move command |
| its own files are complete | Watcher, service definition, message catalogue, working instruction, exclusion list. Remedy: unpack the package again, in full |
| `/usr/bin/python3` is executable | That is the interpreter which starts the service — not the `python3` of your shell |
| Claude Code present, executable **and logged in** | **Where** it lives, the script finds out itself: the search path first, then `~/.local/bin`, `/usr/local/bin`, `/usr/bin`. The login is checked with `claude auth status`. Remedy: start `claude` by hand and run `/login` |
| `python3-watchdog` in the **service interpreter** | Without the watch library the service does not run. The script asks whether to install it; on "no" it aborts |
| `zenity` | Without Zenity the entire notification and escalation path fails — the watcher exists for nothing else. Same kind of question |
| `systemctl` | This script installs a systemd user service |
| `~/.claude` exists | Without the folder there is nothing to watch |

**Warning only, setup carries on:**

| Finding | Consequence |
| --- | --- |
| Claude Code does not answer a probe | Expired subscription, exhausted quota or no connection. A hanging line is no proof of a missing login |
| `libnotify-bin` missing | **An accessory, not a reason to abort.** Only the hourly status notification is lost; detection and escalation work fully |
| Syncthing does not sync `~/.claude` | The watcher gets installed but will never find anything. Exactly the silent failure this check warns about |
| Syncthing is not running right now | Without a running Syncthing no conflict copies arise — that does not make the service wrongly installed |

**The script installs nothing silently.** If a package is missing it names the consequence and asks; the default on an empty answer is **no**. The command it would run is printed first (`sudo apt install …`), and the system then asks for your password.

**A trap involving two interpreters:** what is checked is `watchdog` in `/usr/bin/python3`, not in the `python3` of your shell. On a machine with an active virtualenv those are two different programs — the check reported "watchdog missing" there while the service was running perfectly, and sent the user down a dead end. Since then the script checks the same interpreter the service definition starts.

## Installation

**The normal case is a machine that already has its own, grown `~/.claude`** — holding the chats of its local projects and those from Claude Desktop. Those contents must not be overwritten, and that is exactly why the path below looks the way it does and not like an ordinary "synchronise a folder": the initial sync **unites** two grown sets of files, and the merge step that comes with it is part of the plan.

1. **Back up what is there.** `cp -a ~/.claude ~/.claude.before-sync` — the only fallback line of this procedure. It is released only at the end.
2. **Unpack the tool package.** Download `downloads/claude-sync-watch_en_local.zip` from this folder, then `unzip claude-sync-watch_en_local.zip -d ~`. That creates `~/.claude-sync-watch/` with every file needed — including the English catalogue and the English working instruction, which is what makes the tool speak English. This location is **mandatory**, not a recommendation: the service definition refers to it verbatim, and the installation script refuses the service at any other location. The folder is hidden; check with `ls -d ~/.claude-sync-watch`. The service is **not** set up yet at this point.
3. **Create both exclusion lists — before sharing.**

        cp ~/.claude-sync-watch/.stignore ~/.claude/.stignore
        cp ~/.claude-sync-watch/.stignore-local ~/.claude/.stignore-local

   **The second line belongs here, not later:** the authoritative list pulls the local one in with `#include`, and a missing include file is an error to Syncthing — so until the service is set up the first sync would run with a list whose effect is open. The local file is empty; you only fill it once this machine is to make a selection. Why beforehand at all: Syncthing does not synchronise this file, it has to be present on every machine separately — and if it is missing at the first sync, the credentials set off travelling. What Syncthing later shows in the *Ignore Patterns* tab is exactly this file; before sharing, that tab does not exist yet.
4. **Share the folder in Syncthing.** The interface is at `http://127.0.0.1:8384`. There, **Add Folder**, and then four fields matter:

   - **Folder ID** — the same identifier as on the other devices, **character for character**. Where to find it: on an already connected machine, expand the folder in the overview, line "Folder ID". If it differs by even one character, Syncthing treats it as a different folder and nothing is ever synchronised — without an error message, because from its point of view all is well.
   - **Folder Path** — `~/.claude`.
   - **Sharing tab** — tick the node. **Not** the other workstations: the cluster is a star, each machine knows only the node.
   - **Ignore Patterns tab** — this now shows the content of the `.stignore` you created in step 3. A glance at it is the simplest confirmation that the file is in the right place.

   Save. At the node a prompt then appears asking whether to accept the offered folder; give it a subfolder of the Syncthing data directory as its path. All devices stay on **Send & Receive** — "Receive Only" at the node would be wrong, it has to pass changes on. The individual steps are in section 7 of the setup guide.
5. **Wait for the initial sync.** The interface shows "Syncing" with a progress figure meanwhile, and "Up to Date" on **both** sides at the end. How long it takes depends on the volume — for a grown `~/.claude` that is a few hundred megabytes, so minutes, not hours.

   What happens meanwhile: files present on one side only get distributed; files present on both sides with differing content produce conflict copies carrying `.sync-conflict-` in the name. How many there are depends on how far the two sets have diverged — **this is the planned merge step, not a fault.** You can count them with

        find ~/.claude -name '*.sync-conflict-*' | wc -l

   **If the display stays on "Out of Sync"**, expand the folder: Syncthing names the files it could not transfer there. The most common reason is permissions, the second most common a file that keeps changing while it is being transferred.
6. **Resolve the conflict copies, started by hand.** The watcher is not running yet, and that is deliberate: it should start out on a conflict-free state, and during an initial sync still in progress further copies would keep arriving. So do it once yourself:

        cd ~/.claude
        claude --append-system-prompt-file ~/.claude-sync-watch/conflict-resolution.en.md \
               "The folder to search is ~/.claude. Please resolve the conflict copies lying there."

   The working directory carries weight, it is not decoration: Claude Code takes it from the calling process. The working instruction passed along is the same one the watcher uses later — without it, the session pulls in the project methodology from `~/.claude/CLAUDE.md`, which does not apply here and leads it astray. The session goes through the pairs one by one with you and writes or deletes nothing without your consent. Check for yourself afterwards: `find ~/.claude -name '*.sync-conflict-*'` must come back empty.
7. **Set up the service.** Run `~/.claude-sync-watch/install_service.sh` — from any working directory, the script finds its own folder. It checks the prerequisites above, compares `~/.claude/.stignore` with the authoritative version in the tool folder and **offers to take it over** if they differ; here the default is **yes**. If something was actually copied, it recommends having Syncthing re-read the folder once through its web interface (`http://127.0.0.1:8384`). After that the watcher starts by itself with every login to the graphical session and ends with it. Follow along with `journalctl --user -u claude-sync-watch.service -f`.
8. **Release the backup** after a reasonable observation period — not on the same day.

### Is it running? Three checks

After step 7 a minute is enough to establish that everything is in place:

```bash
systemctl --user status claude-sync-watch.service   # must show "active (running)"
journalctl --user -u claude-sync-watch.service -n 20
find ~/.claude -name '*.sync-conflict-*'            # must stay empty
```

Plus a look at Syncthing's interface: the folder reads **"Up to Date"**, and the node is listed as **connected**.

**The journal stays silent in normal operation**, and that is deliberate: the safety scan runs every fifteen minutes and would otherwise fill it with "found nothing". A line appears only when a pass found something. The first real sign of life is therefore the **hourly status notification** — it should appear within the hour.

### The very first machine

Where the group of machines begins, there is neither a synchronised folder nor a node yet. So the node is set up first (`syncthing-synology-setup-guide.md`, sections 1 to 9), and the folder is created **from this machine** — it holds the content, the node is empty.

Steps 1 to 4 and 7 to 8 above apply unchanged. **Steps 5 and 6 do not apply:** there is no second set of files to unite anything with, so no conflict copies arise. Only the next machine goes through the full path.

### Updating an existing installation

**First of all, before unpacking: rescue your own lines.** If `~/.claude/.stignore` holds anything you put there yourself, the update overwrites it — the authoritative version wins, and the question defaults to yes. This makes it visible:

    diff ~/.claude/.stignore ~/.claude-sync-watch/.stignore

Everything in there that applies to this machine alone belongs in `~/.claude/.stignore-local` **beforehand** (see "Keeping single projects off one machine"). This is exactly how two exclusions once disappeared from one machine. Once you have moved to the second list there is normally nothing left to do here — the check costs one command and is the only chance to notice.

An existing installation is not set up again but overwritten: download the current package and run `unzip -o claude-sync-watch_en_local.zip -d ~`. **The `-o` belongs there** — without it `unzip` asks about every file that already exists, one by one. Then run `~/.claude-sync-watch/install_service.sh`: only that renews the service definition and starts the watcher with the new version. Unpacking alone leaves the new files on disk and the old watcher running. Untouched by all of this: `~/.claude` and the state file `zustand.json`.

**Unpacking deletes nothing.** An installation from before the split by language therefore keeps `conflict-resolution.md` — the working instruction without a language code. It is not read any more, because the watcher builds the name from its own language (`conflict-resolution.en.md`); it merely looks like the authoritative one. The setup script names whatever it finds of these and removes nothing by itself: deleting on someone else's machine is not its business. What is **not** a leftover is `__pycache__/` — Python creates it itself as soon as the watcher loads its message catalogue; deleted, it comes back on the next pass.

**One folder, one catalogue.** Where several `messages_*.py` sit side by side — because both packages were unpacked, or files were copied in from the repository — the package no longer decides the language; the `--lang` switch does. The service definition passes none, so German applies. The setup script points that out as well.

### Removing the service again

`~/.claude-sync-watch/uninstall_service.sh` removes the service — not the folder and not the sync. Whoever wants to get rid of the tool entirely deletes `~/.claude-sync-watch/` by hand afterwards; `~/.claude` and the Syncthing share are untouched by that.

## Day to day

**The sync needs no attention.** It runs on file events; a change is usually on the node within seconds, and a machine that was switched off catches up by itself on its next start.

**Two habits prevent conflicts rather than resolving them:** after switching on, let the sync arrive before working with Claude; and do not switch a machine off while the interface still shows "Syncing". With machines used alternately, the conflict window is not the transfer time but the gap between the last change here and the first catch-up there.

**Once an hour the watcher reports in** — briefly shown, not clickable. It is the sign of life of a service you otherwise cannot tell apart from one that has been stuck for days:

    synced: 0.8 MB up, 0.3 MB down
    no conflict for 74 hour(s)

Four forms of this notification call for attention and therefore stay on screen longer: `3 conflict(s) for 9 hour(s) unresolved`, so a postponed resolution is not forgotten; `backlog: 7 file(s)` — something is stuck, which you would otherwise never learn about; `Sync paused for this folder — changes and conflict copies stay where they are`, because a pause you set yourself and forgot would otherwise stop the sync unnoticed; and `no connection to the sync for …`. Where a number would be, `counters reset` or `counting started afresh` means the reference value is simply missing — after a reconnection, such as a change of WLAN.

**If the hourly notification stops appearing altogether, that is a finding in itself.** Then check whether the service is running at all (`systemctl --user status claude-sync-watch.service`) and what the journal says (`journalctl --user -u claude-sync-watch.service -n 50`). The most common cause is a login without a graphical session — the service hangs on it and ends with it.

**On a conflict**, a dialog asks whether to resolve it now (“Resolve now” / “Later”). On consent, a terminal opens with a Claude Code session that goes through all pending conflict pairs **one by one with the user**: it compares original and copy, explains the difference and obtains the decision — keep the original, take over the copy, or merge. **Nothing** is written or deleted without explicit consent for the specific file; at the end the session reports what it did.

Two things about that:

- **Resolution always happens on one machine only.** Deleting the copy and updating the original travel as ordinary file operations — whoever resolves here tidies up everywhere. If the same conflict is decided differently on two machines, a new one arises.
- **A dialog left unanswered closes itself after fifteen minutes** and asks again after thirty minutes at the earliest. The hourly notification is the quiet reminder in between.

## When something is broken

**Not an emergency:** a file whose conflict was resolved inelegantly — that is simply reworked. An emergency looks like this: Claude Code no longer starts, demands a new login, cannot find a project any more, or a setting has vanished. Even then the cause may be something other than the sync, and the order of steps separates the two:

1. **Close all Claude sessions properly** (`/exit`), in the terminal as well as in VSCode. Those on the **other** machine only if this here achieved nothing.
2. **Kill leftover processes:** `pkill -u $USER claude`. The watcher is unaffected; it only observes.
3. **Open a session again.** If it runs, stop here — it was not sync damage, and there is nothing to retrieve.
4. Only if it is still broken: **make a backup** (`cp -a ~/.claude ~/.claude.broken-<date>`), **then** pause the sync for that folder. The backup deliberately comes before pausing: pausing only stops further propagation.
5. **Retrieve individual files**, normally from the "Staggered" archive on the NAS — it receives from all machines and therefore archives every state that was transferred. The archived versions sit there in the `.stversions/` subfolder of the synchronised folder, named after the moment they were displaced; retrieving means plain copying back to the original place. The **local** `~/.claude/.stversions/` only helps if the damage came in from the other side: Syncthing archives **incoming** foreign changes before overwriting, never your own — and your own botched write is the more common case.
6. **Check on both machines**, log in again if needed, and only then switch the sync back on.
7. **Keep the backup** until it is clear what went wrong — it is the only source for that.

## Limits worth knowing

- **The watcher needs a graphical session**, because it shows dialogs. On a login without a screen — over SSH or a console — Syncthing runs but the watcher does not: conflict copies can arrive without anyone being asked. Nothing is lost; the scan at the next graphical login picks them up.
- **Reporting happens on the machine whose graphical session the watcher belongs to** — not where you happen to be working. Whoever works on another machine through VSCode Remote-SSH sees its notifications only when sitting at an actually synchronised machine with a screen again. It is enough that **any** participating machine reports.
- **A machine that does not take part in the sync itself never reports anything.**
- **The display duration of the hourly notification is a request, not a guarantee:** Plasma honours it, GNOME Shell ignores it.

## Further reading

The documents below are in German.

- `implementation-doc.md` — the complete description (context, project-wide rules, units), with the code review of 13 August 2026 and its processing in the appendix
- `work-plan.md` — the one remaining open step
- `syncthing-synology-setup-guide.md` — setting up the node and the clients
- `offener_fall_chatprotokolle.md` — an investigated but unfinished special case: conflicts in session transcripts
