---
name: cleaning-up-linux-desktop
description: Cleans up a Linux desktop or laptop (Ubuntu, Kubuntu and similar) without putting work data at risk — caches, package and log leftovers, trash, Docker leftovers, old downloads and installation files. Measures first, shows fill level and three tables, deletes caches by fixed rules and user data only as the user selects. Backs up beforehand on request (snapshot or archive) and keeps a short protocol that allows rolling back an interrupted run and cleaning up the backups later. Never removes installed software. Applied only when explicitly invoked with /cleaning-up-linux-desktop.
license: CC0-1.0
disable-model-invocation: true
---

# Cleaning up a Linux desktop

This skill runs long and in many steps; all of its rules are therefore in this one file so that they survive a compaction of the context. Reasons and measurements are in the README in this skill's folder — look there when the user asks why; its file name is not reliable, look in the folder.

## Principles

1. Nothing is blanket. Every area has its own treatment: **delete without asking**, **ask before deleting** or **only report**.
2. Without a decision by the user, only a program's own intermediate files are deleted that the program no longer needs or recreates fully automatically at any time (example: HTTP cache). What comes out of a work step of its own is work data, not cache (example: proxy files of a video editor). State, settings, databases and user data stay; user data (4.7 to 4.10) is deleted only after the user decides.
3. A cleanup command of a program is used only when it is established what it removes. Sweeping commands such as `docker system prune` or `docker image prune -a` are excluded.
4. Installed software is never removed, not even when it is probably no longer needed; such findings are reported.
5. What to keep and what to delete is put into words by the user alone. You translate the user's statements into an order for the script and show the translation before it runs.
6. You never insert folder names such as Downloads, Videos, Music, Pictures, Documents yourself. You determine them through the XDG user directories and pass the resolved paths.
7. What is mounted (network share, another drive, bind mount) is never deleted, never walked and never touched, not even read or counted; links are never followed. The scripts enforce this themselves, by name and before any access, because already a query of an unresponsive network share blocks the process. Mounted data is only covered by starting at its real location, and only if that lies within the analysis. Two exceptions: the target of an archive backup, chosen by the user, is only written to. And for the starter entries of Table 2, the analysis script reads a link target after checking its path by name.
8. Every run ends with a result report: what was deleted, how large the removed amount of data was (not the space freed), what was only reported. For Docker without sizes.
9. The skill's own snapshots and archives carry the name prefix `cleaning-up-linux-desktop-`. The scripts touch nothing without this prefix and exclude files with the prefix from every deletion run. You deviate from this only at the user's explicit request.

## Where you run and how the scripts are run

As a rule you start no scripts and no commands on the user's system. You give the user command blocks; the user runs them, including everything with `sudo`. The results end up as files in `/tmp`.

**Claude Code:** The scripts are in `${CLAUDE_SKILL_DIR}`. Ask whether the session runs on the computer to be cleaned up; if not, end the skill with that remark. You read the result files from `/tmp`. In the console the user can run `/add-dir /tmp` so that you read them without approving each access. The VS Code extension has no `/add-dir`; there reading works without asking in the permission mode "auto", otherwise the user approves every access — tell the user at the start so the questions do not come as a surprise. You write orders for the deletion script and path lists for the archive script yourself as files in `/tmp/cleanup-orders/`.

At the user's explicit request you run scripts without `sudo` yourself; offer this only if the session runs in the console and the user has moved it there with `/cd /tmp` beforehand. Everything with `sudo` stays with the user.

**claude.ai and Claude Desktop (Chat + Cowork):** The placeholder for the skill folder is not replaced here. Find this skill's folder in your execution environment (`ls` under `/mnt`), copy `analyze.py`, `delete.py`, `journal_stats.py`, `snapshots.py` and `backup.py` unchanged to `/mnt/user-data/outputs` and offer them as downloads — **never as an artifact**, because an artifact is a transcription by you and can differ from the original. The user puts them into a folder of their choice; in the commands that folder replaces `${CLAUDE_SKILL_DIR}`. After every command block you name the file the user should upload to you. Orders, path lists and the protocol you also hand over as downloads.

If the skill was not invoked explicitly with `/cleaning-up-linux-desktop` — for instance because it was loaded by itself on claude.ai —, first ask whether it should be applied now. If not, you stop.

## When a script runs too long

Every script that walks folders writes a line to `stderr` when it stays in the same folder for longer than 5 seconds: `<script>: still in "<folder>" after <n> s, no progress`. It repeats, and when the walk moves on, `moved on after <n> s in "<folder>"` follows. Tell the user at the start that these lines appear in the terminal and that they should pass them on to you. The stalls are also in the report (list `stalls`).

If the user reports that a run takes long, you never brush it off as "it just takes time". First ask for these lines; they name the folder. If there are none, give the block below (read-only; `pgrep` finds the process number). State `D` with hardly any CPU and no disk access means: the process waits for a device, mostly a network share. Such a process cannot be ended right away even with `kill -KILL`; do not advise force, ask what is mounted at the named folder (`findmnt -R <folder>`).

```bash
{ for p in $(pgrep -f '^python3 -I .*cleaning-up-linux-desktop'); do ps -o pid,etime,stat,pcpu,cmd -p "$p"; echo "wchan: $(sudo cat /proc/$p/wchan)"; done; } 2>&1 | tee /tmp/cleanup-hang.txt
```

## Modes

The skill knows three: **cleaning up** (the normal run, described from "Start" on), **cleaning up the backups** of an earlier run, and **resuming** after an interrupted run (both at the end of this file). First look for the protocol (section "Protocol"): in Claude Code you read `~/cleaning-up-linux-desktop-protocol.md`, on claude.ai you ask the user to upload it. If there is none, ask whether it is under another name or in another place, and offer this search command. It runs without `sudo`, searches the home only and touches no mount point; if the protocol is on a mount point, the user names the path:

```bash
python3 -I "${CLAUDE_SKILL_DIR}/analyze.py" --home "$HOME" --find-protocol
```

It writes the paths found to `/tmp/cleanup-protocol-search.txt`.

Only then: no protocol. Then propose: no protocol means cleaning up; an open step (started without done, or run not finished) means resuming; a finished run with backups still present means cleaning up the backups. The user decides. "Start" applies to all three modes, step 5 only to cleaning up.

## Start

1. State the purpose: delete useless accumulations of data, point out large amounts of data the user has to take care of personally; remove no software. For Linux desktops and laptops, not for servers.
2. Explain how you work (previous section).
3. Tell the user: the procedure takes a while, can involve extensive internet research and uses many tokens; for good research results you recommend the Opus model. Also say clearly: no warranty is given for the skill's function, and deleted files come back only from a backup. Recommend creating at least one full backup or snapshot before the first deletion and checking that it can be restored. You do this together with the user at the right point (section "Backup"); whoever wants to can do it beforehand. Also say: the backups can be cleaned up later with this skill once the user is convinced that everything works.
4. Have the user confirm this way of working before you go on.
5. Only when cleaning up: ask for everything the analysis needs before it starts: the **size threshold** (one number for large single files, images, archives and media; default 150 MiB) and whether **general archives** (`.zip`, `.tar.*`, `.7z`, `.rar`) should be included with the images. After that the analysis runs without questions.

## Determining the environment

Give the user this block; it writes to `/tmp/cleanup-env.txt`:

```bash
{ echo "DESKTOP=$XDG_CURRENT_DESKTOP"; echo "HOME=$HOME"; for d in DOWNLOAD VIDEOS MUSIC PICTURES DOCUMENTS; do echo "$d=$(xdg-user-dir $d)"; done; grep -h '"browser.download.dir"' ~/.mozilla/firefox/*/prefs.js 2>/dev/null | sed 's/^/FIREFOX /'; for p in ~/.config/google-chrome/*/Preferences; do [ -f "$p" ] && python3 -c 'import json,sys; print("CHROME", json.load(open(sys.argv[1])).get("download", {}).get("default_directory", ""))' "$p"; done; } | tee /tmp/cleanup-env.txt
```

Download targets that differ from the default in Firefox or Chrome (lines `FIREFOX`, `CHROME`) are further download folders; each goes into the analysis as its own `--downloads`. Only what lies in the home is covered. For a folder that is not set up, `xdg-user-dir` returns the home itself. Such an entry counts as not present: you report a download folder without an entry, and you leave media folders without an entry out of the call — with the home as media folder the whole home would drop out of 4.10.

## Analysis

```bash
sudo nice -n 19 ionice -c3 python3 -I "${CLAUDE_SKILL_DIR}/analyze.py" --home "$HOME" --downloads "<download folder>" [--downloads "<browser target>" …] --media-dir "<Videos>" --media-dir "<Music>" --media-dir "<Pictures>" --media-dir "<Documents>" --desktop "$XDG_CURRENT_DESKTOP" --threshold <MiB> [--archives]
```

The script shows its progress and writes `/tmp/cleanup-analysis.json`. If a download or media folder passed in lies on a mount point, it is not analysed; the script reports it, and `meta.params.not_read` names it. Tell the user to clean up that folder at its real location personally. `meta.other_filesystems` names the mount points left out below the home. Contents: `fill_level`, `table1` (areas 4.1 to 4.14 except 4.11), `software` (starter entries, Flatpak, Snap, application folders with prefilter), `table3`, `safeguards` (btrfs, ZFS, LVM, Timeshift, Snapper: what the system offers for backups). It only reads. Tell the user beforehand that you also check which software brings cache and download folders, and that you research the programs on the internet.

Then you research the programs found (4.11) before showing tables. At the end of the analysis you briefly name the software for which you will make suggestions during the cleanup; Firefox, Chrome and VS Code belong to it if they are installed.

## Presentation

First the **fill level** per local file system (used, total size, percent); network shares and other non-local file systems are left out on purpose; if there are btrfs snapshots, their number and, where known, their usage; plus which backup variants the system offers (`safeguards`). The fill level shows where cleaning up pays off.

Then three tables, **one row per area**. Detail lists, histograms and selection lists come only when the area is processed — never everything right after the analysis.

- **Table 1 — backed by tests** (sections 4.1 to 4.14 except 4.11). Columns: area, location, size, treatment (without asking / with asking / only report), needs root, program must be closed, backup note. For 4.5 two rows: log files total, journal total. The rows 4.5, 4.7 to 4.10 and 4.14 carry the note that deleted data only comes back from a backup or snapshot.
- **Table 2 — backed by research** (4.11). Columns: program, folder, size, evidence level with source, program must be closed, backup comment (the measure is not tested).
- **Table 3 — statistics**, without the areas of Tables 1 and 2:
  - Size per directory: top level below the home and the system directories, deeper levels only where the script delivers them; in the home also the share unchanged for more than a year. Mark hits that correspond to one of the open areas: search index Baloo, Git repositories, thumbnails, Claude Desktop caches and sandbox image, Flatpak/Snap/AppImage/Wine, Python environments, toolchains, Syncthing versions, duplicates, migration leftovers.
  - Large single files: one row per open area with count and total, the rest as "other".
  - Leftovers of uninstalled programs: application folders you cannot assign to any installed software, any desktop or system component or any tool without a starter entry, each with a reason. The script's prefilter (`prefilter_match`) is only a hint; the judgement is yours.
  - Duplicate files: number of groups and surplus amount.
  - Leftovers of aborted Git fetches, caches without an assigned program, crash dumps (only if present), development artifacts (per project: size, last change of the sources, dependency list yes/no).

## Backup

The analysis only reads. Backups are made **before the first deletion** and a second time **before the follow-up** to Tables 2 and 3, because untested things happen there. Whether to back up before every cleanup step instead is the user's decision; the default is once per point in time. If the user has already backed up, you enter that in the protocol.

After the analysis offer all variants that `safeguards` provides and let the user choose. The choice, the target and all names go into the protocol:

1. **Own backup:** The user confirms that a current backup exists that can be restored. You then back up nothing yourself.
2. **Snapshot (btrfs):** only for file systems with `kind: btrfs`. You name ZFS and LVM (`tested: false`) but offer no snapshot for them: they are untested, and the skill contains no snapshot command for them.
3. **Timeshift or Snapper**, if `safeguards.tools` shows them as installed and set up: give their commands as a block; you enter the name or ID in the protocol. The scripts do not touch them.
4. **Archive of the files to be deleted (tar or zip):** for user data (4.7 to 4.10, download folder, trash) and for application folders for which it is not established that they are pure caches (follow-up). You never back up established caches (Table 1). Before every archive backup ask whether the user really wants it.

**Snapshot.** Ask whether the location `<mount point>/.cleaning-up-linux-desktop-snapshots/` suits the user; another location below the mount point can be chosen (`--base-dir`). Back up every file system on which something is deleted (from the fill level, mostly `/` and `/home`):

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/snapshots.py" create --mount <mount point> --label <label> [--base-dir <folder>] [--dry-run]
```

Dry run first, then for real. Give every file system **its own label** naming the mount point (for instance `root-before-delete`, `home-before-delete`): with the same label, snapshots created in the same second carry the same name, and `remove --name` then stops with "ambiguous". Also give every call its own report file (`--report /tmp/cleanup-snapshots-create-<label>.json`), otherwise the next call overwrites the report of the previous one; the report names the snapshot. Say with it: a snapshot holds on to deleted data, space is freed only once it is removed.

**Archive.** Ask about:
- **Format:** `tar` (default) keeps owners, ACLs, extended attributes, hard links and links; uncompressed for a fast target (internal SSD), as `tar.gz` for a slow one (USB stick, network). `zip` packs file by file (media only stored, the rest compressed) but does **not keep owners, ACLs, extended attributes or hard links**. With zip, point this out explicitly, for example the origin URL of downloads and tags and ratings from Dolphin (from knowledge, not checked).
- **Target:** default `~/`. Ask whether the user prefers an external device (stick, network share). With a network share say that the transfer usually takes much longer than to a directly attached, reasonably modern storage device. If the target is on the same file system as the data, the cleanup frees no space as long as the archive exists.
- **Reserve:** the default is the larger of 10 % of the target file system and 10 GiB. The user may lower it; the script raises it to the larger of 5 % and 5 GiB.
- **Verification:** the default is the comparison with the files (a second read); only on request the quick check.

Per backup step: (1) dry run of `delete.py` with `--with-paths` — the report lists the paths under `candidates` (for `list` orders they are the selected paths); (2) `backup.py create --dry-run` shows amount and space; (3) for real; (4) **only with `ok: true`** the real deletion. If the backup fails, you delete nothing.

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/backup.py" create --list <list or report of delete.py> --target "<target folder>" --step <step> --format tar|tar.gz|zip [--run <folder name of the run>] [--reserve-percent P] [--reserve-gib G] [--verify quick] [--dry-run]
```

The first report (`/tmp/cleanup-backup-create.json`) names the run (`run`); pass it with `--run` for all further steps of the same run. Every step becomes a file of its own, `NN-<step>.tar|.tar.gz|.zip`.

**Restoring** is selective: only what is missing, nothing is overwritten. From a snapshot: `snapshots.py restore --snapshot <name> --path <folder relative to the mount point> [--dry-run]`; from an archive: `backup.py restore --target <target> --run <run> --step <step> [--path <absolute original path>] [--dry-run]`. You roll back a whole subvolume only at the user's explicit request and with a warning: the protocol in the home would be reset to the state of the snapshot. Restored from a zip, new files get the owner of their parent folder. Targets at or below a mount point are left out by both scripts and reported (`not_restored`); tell the user that such data has to be restored at its location personally.

## Protocol

The protocol is short and only serves to make a rollback possible in a new session. Default: `~/cleaning-up-linux-desktop-protocol.md`; the user can change name and location. In Claude Code you write the file yourself, on claude.ai you hand it over as a download and ask for the upload at the next start.

- **First line exactly:** `# cleaning-up-linux-desktop Protocol`; the rest of the text is in the user's language unless the user wants otherwise.
- **Structure:** a head with the key facts (chosen backup variant, target, backup cadence, format), then the protocol per session with date, then a section "Special arrangements" without protocol character.
- **Entries:** one line per step with area and what was done. Write "started" **before** handing over the command block, afterwards "done" or "aborted", so an abort in the middle of a step stays visible. Per deletion step the affected folders (not every file) and which backup covers it, because the reports under `/tmp` do not survive a reboot. Skipped steps (with the user) and particularities. Every backup and every removal of a backup as a step of its own with name and location.
- **Special arrangements:** Ask whether a special arrangement with the user should be recorded for reuse. At the next run you ask whether they should apply again.

## Order of processing

Propose to work through Table 1 step by step; before that you back up according to the section "Backup" and create the protocol. Order: 4.1 to 4.6, 4.12, 4.13, then 4.9 → 4.7 → 4.8 → 4.10, finally 4.14 (so that everything an earlier step moved to the trash is included). Then the result report; it ends the actual run. Then offer the follow-up, first to Table 2, then to Table 3, with a new backup before it (section "Backup"); the user can stop after every part.

Per area: show the details, get the user's decision where one is needed, write the order, "started" in the protocol, **dry run**, show the result, run an archive backup if chosen, after confirmation the **real run**, "done" in the protocol:

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/delete.py" --home "$HOME" --order /tmp/cleanup-orders/<area>.json --dry-run
sudo python3 -I "${CLAUDE_SKILL_DIR}/delete.py" --home "$HOME" --order /tmp/cleanup-orders/<area>.json
```

Every run writes `/tmp/cleanup-report-<area>.json` (removed count and amount, groups, skipped paths with reason, commands run). You show skipped items to the user with the reason. Regardless of the order, the script refuses: `/`, the home, folders directly below `/` or the home, `/boot`, everything outside the home, `/var`, `/opt`, `/usr/local`, `/srv`, mount points and everything that contains one or lies below one, links (except in the trash).

Order forms: `{"area": "<area>", "kind": "rule", "params": {...}}` for rules, `{"area": "<area>", "kind": "list", "paths": [...]}` for selected paths (only 4.7, 4.8 and 4.10).

## The areas

**4.1 apt** — without asking, root. Order `rule`, no parameters; runs `apt-get clean`. `/var/lib/apt/lists` is not part of it.

**4.2 Firefox** — without asking, even while Firefox runs. Rule: files in `cache2/entries` of every profile, older than 3 days; `cache2/index` only when no Firefox runs; folders never. Old leftovers `cache2`/`startupCache` in the profile folder under `~/.mozilla/firefox`, unchanged for more than 30 days, delete completely and report. The remaining content stays. Order `rule`, no parameters.

**4.3 Chrome** — without asking. Rule: in every profile under `~/.cache/google-chrome`, entries in `Cache/Cache_Data` and `Code Cache/js` older than 3 days; `index` and `index-dir` only when Chrome does not run; `Code Cache/wasm` and all folders stay. Folders under `~/.config/google-chrome` are not touched.

**4.4 VS Code** — without asking. Rule: entries in `Cache/Cache_Data` older than 3 days, index only when VS Code does not run; folders in `CachedData` except the installed version, older than 3 days; hidden non-archives in `CachedExtensionVSIXs`, older than 3 days. Only report `WebStorage/*/CacheStorage`: large amounts of data, whether deleting is advisable is not settled.

Rules 4.2 to 4.4 apply only to the classic paths. If one of these programs runs as Snap, Flatpak or installed otherwise, treat it like user software according to 4.11 (Table 2).

**4.5 Log files and journal** — with asking. First start the evaluation:

```bash
sudo nice -n 19 ionice -c3 python3 -I "${CLAUDE_SKILL_DIR}/journal_stats.py" --home "$HOME"
```

It writes `/tmp/cleanup-journal.json`. Show: total size of the journal, the histogram (periods × levels, only as far as the journal reaches), the strongest sources, the **spikes** (source, day, count, median — descending by excess) as a hint to examine the logging configuration or function of these programs, and the **conspicuous log groups**. Fixing the cause is not part of the skill; if the user wants to do it right away, that is allowed, and you continue afterwards. Offer: delete everything except the last x days (default 14) — order `rule` with `{"days": x}`; the script runs `journalctl --vacuum-time` and deletes only archived, rotated log files, never the active one. You do not offer deleting by log level. You mention `MaxLevelStore` only as information: it limits future entries for all programs together, does not act on existing ones, changes the configuration.

**4.6 pip cache** — always with asking. Show the size and the entries from 50 MiB on (size, date, without names). Note: future installations download packages again or build them again. On approval order `rule`; runs `pip cache purge` as the owner of the home.

**4.12 `__pycache__`** — without asking. Order `rule`; deletes every `__pycache__` in the home including the folder. Consequence: the first program start is somewhat slower.

**4.13 Docker** — only Docker with a root daemon; Podman and rootless Docker only report. In this order, all in one order `rule`:
1. Build cache that is not younger than 2 days (the user can change the limit): `"builder_until_hours": 48`. Say with it: a freshly used build step holds on to its whole chain.
2. Present stopped containers numbered (name, image, stopped since, size); the user chooses: `"containers": [...]`. They are deleted together with anonymous volumes; named volumes stay.
3. Present Compose projects numbered (path and date of the file, project name, images, state). The images of all projects the user wants to keep form the keep list `"keep_images": [...]`. Report projects whose images Compose could not determine (`images` is empty) — then **all** images without a container are kept: run the area without image deletion by putting all existing images into `keep_images`.
4. The script then deletes all images that are no longer assigned to a container and are not on the keep list. Named volumes only report.
No size in the report.

**4.9 Download folder** — by age, not by size: in the download folder, overview is what matters. Ask for the age limit x in days (default 14) and for exceptions. Everything directly in the download folder whose age is greater than x days is deleted, regardless of size: a file by its own age; a folder by its youngest element at any depth (files, links and subfolders) — one single younger element protects the whole folder with everything in it; an empty folder by its own date. Incomplete downloads (`.crdownload`, `.part`) fall under the same limit, links directly in the folder are only reported. Order `rule` with `{"days": x, "folders": [...], "exclude": [...]}`: `folders` are the download folders from `meta.params.downloads` of the analysis, `exclude` the user's exceptions, translated by you with the help of `table1.4.9_downloads` into absolute paths directly below the download folder. The script computes the age during the run; the ages in the analysis count only files for folders and can differ. Therefore do the dry run first and show the overview from its report (`removed`, `skipped`): count and total size, every folder individually, files counted by type, the few largest, skipped items with reason; you put the complete list into a file. The user confirms, then the real run. Note: recoverable only if the folder is backed up.

**4.7 .deb files** — with selection. Numbered list of the files whose package is installed in the same or a newer version (`status: same_or_newer_installed`); the user chooses numbers or "all". The rest only report. Note: an older version can often not be downloaded again. Order `list`.

**4.8 Images and archives** — with selection. Hits by size descending, numbered. The user names numbers you should look at more closely — by extension, name, folder and date, not by content; then the list again with your assessment, the user decides. Order `list`.

**4.10 Stray media** — with selection. The script delivers media files from the threshold on outside the media folders, per folder found the extensions of the neighbouring files and whether it is a project or `.git`. You assess the nature of every folder (name, project folder, neighbouring extensions as a hint at an editing project, deliberate storage) and show only what looks forgotten. Presentation and selection as in 4.8. Order `list`.

**4.14 Trash** — last. Ask for x days (default 14, 0 = everything). Order `rule` with `{"days": x}`. Only the trash in the home is processed; the skill does not touch trash folders on other drives (`.Trash-<uid>` at a mount point), the user empties them at their location personally — tell the user. What counts is the date the item was moved to the trash; entries without a valid `.trashinfo` are only reported. Note: gone for good, a backup only helps if the trash is backed up.

## Result report

After Table 1, before the follow-up, you compile an overall report from the reports of the individual runs: per area what was deleted (count, removed amount of data; for Docker the deleted containers and images without size), what was skipped and why, what was only reported. Below it the total removed amount of data and the backups created (name, location, size). Say explicitly that this is not the space freed: snapshots and archives on the same file system, compression and files still open can make it smaller. Mention that the backups can be cleaned up later with this skill, and enter the run as finished in the protocol.

## Table 2: user software (4.11) and follow-up

The basis are the programs found in `software.desktop.included` (the script applies the rules for this) and the folders under `~/.cache` that you can assign to an owner without a starter entry (extension, command-line tool, library). You do not research Firefox, Chrome and VS Code on their classic paths.

Per program you look for exactly two things in the documentation:
1. **Cache and download folders.** A folder counts as cache only if the documentation establishes that the program restores its data fully automatically at any time and that their absence changes nothing except time — what the documentation calls it does not count; looking at the file system alone is not enough. If it does not follow that the program tolerates the loss while running, you delete only once it is closed, and you ask the user to close it.
2. **Folders with input data** of data-processing programs. You silently exclude hits in them from the searches 4.8, 4.10 and from the large single files and duplicates in Table 3 — without a report. No silent exclusion for 4.7, 4.9 and the size per directory.

**Evidence level** per row: **high** — the official documentation says so explicitly; **medium** — only developer forum, issue tracker or distribution wiki. Only third-party sources or inference count as **no clear finding**: then you name the program's data nowhere and exclude it from every deletion proposal (the size per directory still counts it). Folders under `~/.cache` without an assignable owner go to Table 3. **Follow-up to Table 2** (after the result report): repeat the items of Table 2 and tell the user that you have no tested and established experience for these items. Offer to clarify all or part of them further together — research in the documentation, developing and carrying out cleanup strategies together. Proceed carefully and before every deletion remind the user what is actually established and what is assumption, so that the user can judge whether to really delete. The deletion script accepts no order for Table 2; deleting is done with the fixed block from "Deleting in the follow-up".

## Follow-up to Table 3

After the follow-up to Table 2, or if the user skips it, offer to explore the findings together: look at contents more closely, internet research. Say with it: there are no ready-made solutions for this; they are worked out first, should be well established and are untested — a full backup or a snapshot is strongly recommended. Before that you clean up nothing there.

If the user additionally asks for a search for further files, none of the rules of this skill apply; you negotiate the conditions with the user. The silent exclusion does not apply to such searches either.

## Deleting in the follow-up

`delete.py` refuses folders directly below the home, and there is no rule for the items of Tables 2 and 3. What goes there after the user's decision you therefore delete with this fixed block and you do not write one of your own. You may change only the five lines at the top: `WHOLE` (folders or files that go completely) and `CONTENT` (folders that are emptied and stay themselves) with absolute paths without a trailing slash, `PROG` (pattern of running programs that must be closed beforehand), the running number in `OUT`, and `DRY`: first `1` for the dry run, after the user's confirmation `0`. "Started" is in the protocol before the real run. The block runs without `sudo`. Per path it checks by name before touching it: below the home, no own prefix, no other mount point (from `/proc/self/mountinfo`) and none below it; then no link and `realpath` equal. It reports apparent and allocated size; show the user both, because with image files (sparse) the allocated size can be far smaller.

```bash
DRY=1                                   # 1 = dry run, 0 = for real
WHOLE=( )                               # folders or files that go completely
CONTENT=( )                             # folders whose content goes; the folder itself stays
PROG=''                                 # pattern of running programs that must be closed first; empty = none
OUT=/tmp/cleanup-followup-1.txt
{
mounts() { awk '{ t = $5; gsub(/\\040/, " ", t); gsub(/\\011/, "\t", t); gsub(/\\012/, "\n", t); gsub(/\\134/, "\\", t); print t }' /proc/self/mountinfo; }
mnt_of() { mounts | X="$1/" awk '{ t = ($0 == "/" ? "" : $0) "/" } index(ENVIRON["X"], t) == 1 && length($0) > length(m) { m = $0 } END { print m }'; }
HM="$(mnt_of "$HOME")"
if [ -n "$PROG" ] && pgrep -a -f "$PROG"; then echo "ABORT: program running (see above)"; exit 1; fi
SUM=0; SUMB=0
for P in "${WHOLE[@]}" "${CONTENT[@]}"; do
  echo "## $P"
  case "$P" in "$HOME"/?*) ;; *) echo "skipped: not below the home"; continue ;; esac
  case "$P" in *cleaning-up-linux-desktop-*) echo "skipped: own backup (prefix)"; continue ;; esac
  if [ "$(mnt_of "$P")" != "$HM" ]; then echo "skipped: lies on another mount point"; continue; fi
  if [ -n "$(mounts | X="$P/" awk 'index($0 "/", ENVIRON["X"]) == 1')" ]; then echo "skipped: mount point below"; continue; fi
  if [ -L "$P" ] || [ ! -e "$P" ]; then echo "skipped: link or not present"; continue; fi
  if [ "$(realpath -e -- "$P")" != "$P" ]; then echo "skipped: realpath differs"; continue; fi
  B="$(du -sb --one-file-system -- "$P" | cut -f1)"; A="$(du -sB1 --one-file-system -- "$P" | cut -f1)"
  echo "size (bytes, apparent): $B  allocated: $A  entries: $(find "$P" -xdev | wc -l)"
  KEEP=0; for I in "${CONTENT[@]}"; do [ "$I" = "$P" ] && KEEP=1; done
  if [ "$DRY" = 1 ]; then echo "dry run: would remove $([ $KEEP = 1 ] && echo 'the content' || echo 'everything')"; SUM=$((SUM+B)); SUMB=$((SUMB+A)); continue; fi
  if [ $KEEP = 1 ]; then
    [ -d "$P" ] || { echo "skipped: not a folder"; continue; }
    find "$P" -mindepth 1 -xdev -delete; echo "find return code: $?"
  else
    rm -rf --one-file-system -- "$P"; echo "rm return code: $?"
  fi
  R=0; RB=0; [ -e "$P" ] && { R="$(du -sb --one-file-system -- "$P" | cut -f1)"; RB="$(du -sB1 --one-file-system -- "$P" | cut -f1)"; }
  echo "afterwards (bytes): $R"; SUM=$((SUM+B-R)); SUMB=$((SUMB+A-RB))
done
echo "## total (bytes, apparent): $SUM  allocated: $SUMB"
} 2>&1 | tee "$OUT"
```

## Mode: cleaning up the backups

Only if the protocol shows the last run as finished; otherwise go to resuming. Cleaning up can be at a later point when the user has been able to convince themselves that everything works. Establish which of the names in the protocol still exist and what they hold on to (`snapshots.py list`, `backup.py list --target <target>`; the reports are `/tmp/cleanup-snapshots-list.json` and `/tmp/cleanup-backup-list.json`). The user decides what goes. Only what carries the prefix is removed, every step with a dry run first:

```bash
sudo python3 -I "${CLAUDE_SKILL_DIR}/snapshots.py" remove --name <name or full path> --report /tmp/cleanup-snapshots-remove-<n>.json [--dry-run]
sudo python3 -I "${CLAUDE_SKILL_DIR}/backup.py" remove --target "<target folder>" --run <run> [--dry-run]
```

If snapshots on several file systems carry the same name (runs before the rule "one label per file system"), give the full path from `snapshots.py list`; `<n>` counts the calls so that each keeps its own report. Every removal is a step in the protocol. You clean up Timeshift and Snapper with their commands as a block. Afterwards you ask whether the protocol should be deleted; you delete it only if the user wants. If it contains special arrangements, tell the user. The user can also have only the protocol part of this and earlier sessions removed and keep the file with the special arrangements.

## Mode: resuming after an abort

Applies when the protocol shows an open step or a run not finished, for instance after a reboot that lost the session. Read the protocol and present the state: what is done, what was started without being finished. Check whether the backups named are still present (`snapshots.py list`, `backup.py list`). Then propose restoring one or all steps (selectively, section "Backup") or continuing; the user decides. Each step is restored from the backup the protocol names. If there is none, point to the user's own backup, which the user restores personally.
