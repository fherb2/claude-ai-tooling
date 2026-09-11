# Syncthing sync for `~/.claude`

*Last updated: 2026-09-11*

*[Deutsche Fassung](https://github.com/fherb2/claude-ai-tooling/blob/master/home-.claude-sharing/README.md)*

**Keeps the working state of Claude Code and Claude Desktop — configuration, session transcripts, project memory — automatically in sync across several machines, so the same context is available everywhere. And it reports the exceptional case a synchronisation cannot resolve by itself: the file that was changed on both sides.**

The sync has been running since 11 August 2026, by now on three machines; the watcher runs as a service on all three and has handled real conflicts. The implementation is complete; the only open item is a counterpart for Windows (`work-plan.md`).

A note on language: the package you install decides it. The English package carries an English message catalogue and an English working instruction, so dialogs, notifications, journal lines and the conflict session itself speak English; the German package speaks German. There is nothing to configure. The two setup scripts are English in both packages — setting up runs once and is the first contact with the tool. The strings quoted below are the English ones, verbatim.

## Purpose

Claude Code, Claude Desktop and the VSCode extension keep their entire working state in the `~/.claude` directory of the respective machine. Anyone working on several machines therefore has several independent memories: what was worked out on the laptop does not exist on the office machine.

The synchronisation itself is done entirely by Syncthing, through an always-on node on a NAS of your own. The participating machines need neither to see each other nor to be switched on at the same time — each one knows only the node. That is why everything described here holds for **any number** of machines, not just for two.

The contribution of this project lies elsewhere: Syncthing deliberately does **not** merge files that were changed on two machines at once. It puts the losing version next to the original as a conflict copy — and tells nobody. That is where this tool comes in: a watcher discovers such copies, reports them, and guides the user through resolving them together with Claude.

## What travels — and what does not

Everything in `~/.claude` is synchronised, including the session transcripts and chats under `projects/` — they are the actual point of the exercise. Excluded is whatever the ignore list `.stignore` names; which pattern is there for what reason is set out in chapter 3.9 of the documentation.

Four points worth knowing beforehand:

- **Credentials never travel.** `.credentials.json` is excluded, and that line must be present in `~/.claude/.stignore` on **every** machine **before** the folder is first connected there. The file itself does not travel — Syncthing never synchronises it.
- **`/rewind` across machine boundaries is gone.** The snapshots under `file-history/` are excluded: they refer to absolute paths of the machine that created them, and their write pattern is the worst in the whole folder for a synchronisation. Whoever continues a session on the other machine has no checkpoints to roll back to there. That is what the project's version control is for.
- **MCP servers in user and local scope stay local.** They live in `~/.claude.json`, which is **outside** the synchronised folder. Whoever sets up an MCP server on one machine enters it again on the other. This does not apply to the project scope: `.mcp.json` belongs in the project's repository and travels with it.
- **Login and device state stay local** — likewise `~/.claude.json`. Switching accounts is therefore a purely local affair and produces no conflicts.

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

The installation script checks these prerequisites one by one:

| Prerequisite | If it is missing … |
| --- | --- |
| Syncthing is running and syncs `~/.claude` | Warning — the watcher gets installed but will never find anything |
| `/usr/bin/claude` present **and logged in** | Abort. Remedy: start `claude` by hand and run `/login` |
| `python3-watchdog`, `zenity`, `libnotify-bin` | One question per package, whether to install it |
| `systemctl` and a controlling terminal | Abort — without a terminal no question could be asked |

The script **installs nothing silently**: if a package is missing it names the consequence and asks; the default on an empty answer is **no**. Without `zenity` the entire notification path fails, without the watchdog library the service does — both are prerequisites. `libnotify-bin`, by contrast, is an accessory: without it only the hourly status notification is missing, while detection and escalation work fully.

## Installation

**The normal case is a machine that already has its own, grown `~/.claude`** — holding the chats of its local projects and those from Claude Desktop. Those contents must not be overwritten, and that is exactly why the path below looks the way it does and not like an ordinary "synchronise a folder": the initial sync **unites** two grown sets of files, and the merge step that comes with it is part of the plan.

1. **Back up what is there.** `cp -a ~/.claude ~/.claude.before-sync` — the only fallback line of this procedure. It is released only at the end.
2. **Unpack the tool package.** Download `downloads/claude-sync-watch_en_local.zip` from this folder, then `unzip claude-sync-watch_en_local.zip -d ~`. That creates `~/.claude-sync-watch/` with every file needed — including the English catalogue and the English working instruction, which is what makes the tool speak English. This location is **mandatory**, not a recommendation: the service definition refers to it verbatim, and the installation script refuses the service at any other location. The folder is hidden; check with `ls -d ~/.claude-sync-watch`. The service is **not** set up yet at this point.
3. **Create the ignore list — before sharing.** `cp ~/.claude-sync-watch/.stignore ~/.claude/.stignore`. Why beforehand: Syncthing does not synchronise this file, it has to be present on every machine separately — and if it is missing at the first sync, the credentials set off travelling. What Syncthing later shows in the *Ignore Patterns* tab is exactly this file; before sharing, that tab does not exist yet.
4. **Share the folder in Syncthing.** Four steps, details in section 7 of the setup guide: **Add Folder**; enter the same **Folder ID** as on the other devices — character for character, otherwise it counts as a different folder; set "Folder Path" to `~/.claude`; tick the node in the **Sharing** tab; save. At the node, a prompt appears asking whether to accept the folder. All devices stay on **Send & Receive**.
5. **Wait for the initial sync.** It is done when both sides show "Up to Date". What happens meanwhile: files present on one side only get distributed; files present on both sides with differing content produce conflict copies carrying `.sync-conflict-` in the name. How many there are depends on how far the two sets have diverged — **this is the planned merge step, not a fault.**
6. **Resolve the conflict copies, started by hand.** The watcher is not running yet, and that is deliberate: it should start out on a conflict-free state, and during an initial sync still in progress further copies would keep arriving. So do it once yourself:

        cd ~/.claude
        claude --append-system-prompt-file ~/.claude-sync-watch/conflict-resolution.en.md \
               "The folder to search is ~/.claude. Please resolve the conflict copies lying there."

   The working directory carries weight, it is not decoration: Claude Code takes it from the calling process. The working instruction passed along is the same one the watcher uses later — without it, the session pulls in the project methodology from `~/.claude/CLAUDE.md`, which does not apply here and leads it astray. The session goes through the pairs one by one with you and writes or deletes nothing without your consent. Check for yourself afterwards: `find ~/.claude -name '*.sync-conflict-*'` must come back empty.
7. **Set up the service.** Run `~/.claude-sync-watch/install_service.sh` — from any working directory, the script finds its own folder. It checks the prerequisites above, compares `~/.claude/.stignore` with the authoritative version in the tool folder and **offers to take it over** if they differ; here the default is **yes**. If something was actually copied, it recommends having Syncthing re-read the folder once through its web interface (`http://127.0.0.1:8384`). After that the watcher starts by itself with every login to the graphical session and ends with it. Follow along with `journalctl --user -u claude-sync-watch.service -f`.
8. **Release the backup** after a reasonable observation period — not on the same day.

### The very first machine

Where the group of machines begins, there is neither a synchronised folder nor a node yet. So the node is set up first (`syncthing-synology-setup-guide.md`, sections 1 to 9), and the folder is created **from this machine** — it holds the content, the node is empty.

Steps 1 to 4 and 7 to 8 above apply unchanged. **Steps 5 and 6 do not apply:** there is no second set of files to unite anything with, so no conflict copies arise. Only the next machine goes through the full path.

### Removing the service again

`~/.claude-sync-watch/uninstall_service.sh` removes the service — not the folder and not the sync. Whoever wants to get rid of the tool entirely deletes `~/.claude-sync-watch/` by hand afterwards; `~/.claude` and the Syncthing share are untouched by that.

## Day to day

**The sync needs no attention.** It runs on file events; a change is usually on the node within seconds, and a machine that was switched off catches up by itself on its next start.

**Two habits prevent conflicts rather than resolving them:** after switching on, let the sync arrive before working with Claude; and do not switch a machine off while the interface still shows "Syncing". With machines used alternately, the conflict window is not the transfer time but the gap between the last change here and the first catch-up there.

**Once an hour the watcher reports in** — briefly shown, not clickable. It is the sign of life of a service you otherwise cannot tell apart from one that has been stuck for days:

    abgeglichen: 0.8 MB hoch, 0.3 MB herunter
    kein Konflikt seit 74 Stunde(n)

(“synced: 0.8 MB up, 0.3 MB down / no conflict for 74 hour(s)”.)

Four forms of this notification call for attention and therefore stay on screen longer: `3 conflict(s) for 9 hour(s) unresolved`, so a postponed resolution is not forgotten; `backlog: 7 file(s)` — something is stuck, which you would otherwise never learn about; `Sync paused for this folder — changes and conflict copies stay where they are`, because a pause you set yourself and forgot would otherwise stop the sync unnoticed; and `no connection to the sync for …`. Where a number would be, `counters reset` or `counting started afresh` means the reference value is simply missing — after a reconnection, such as a change of WLAN.

**If the hourly notification stops appearing altogether, that is a finding in itself** and worth looking up in the journal.

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
5. **Retrieve individual files**, normally from the "Staggered" archive on the NAS — it receives from all machines and therefore archives every state that was transferred. The local `~/.claude/.stversions/` only helps if the damage came in from the other side; it does not archive your own botched write.
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
