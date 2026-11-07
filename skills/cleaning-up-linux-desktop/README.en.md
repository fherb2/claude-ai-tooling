# cleaning-up-linux-desktop — cleaning up a Linux desktop without putting work data at risk

*Last updated: 2026-11-08*

*[Deutsche Fassung](https://github.com/fherb2/claude-ai-tooling/blob/master/skills/cleaning-up-linux-desktop/README.md)*

**✅☑ Finished and usable.** Instructions and scripts complete, frontmatter set, German and English versions available, installation packages built; a complete run with real deletions has gone through on the development machine. No silent trigger: the skill is only applied when invoked explicitly. — For Claude Code and claude.ai.

---

## Overview

**The skill cleans up a Linux desktop or laptop and deletes only what is demonstrably useless.** It first measures what is on the machine, shows the fill level of the file systems and three tables, and then works through them together with the user: caches of Firefox, Chrome and VS Code, the apt package cache, log files and journal, the pip cache, Python bytecode, Docker leftovers, the download folder, installation files left lying around, images and archives, forgotten media files and finally the trash.

What is deleted without asking is narrowly limited: a program's own intermediate files that the program no longer needs or recreates fully automatically at any time. Everything that belongs to the user — downloads, installation files, media, the contents of the trash — is deleted only as the user selects. For the downloads folder an age rule applies that the user sets: everything older than x days (default 14) goes, regardless of size; a folder stays with everything in it as long as anything in it, however deeply nested, is younger. Before every deletion there is a dry run that shows what would actually go, and before the first deletion a backup that the skill creates together with the user (snapshot or archive). A short protocol records what was done: with it an interrupted run can be rolled back, and the backups can later be cleaned up with the skill.

**Scope:** The skill removes no installed software, not even software that probably nobody needs any more; it only reports it. It is meant for desktops and laptops (Ubuntu, Kubuntu and similar), not for servers. What is mounted — another file system or a bind mount — is never walked and never deleted.

The skill is only applied when invoked explicitly: `/cleaning-up-linux-desktop`. It does not load by itself.

## No warranty

**No warranty is given for the function of this skill.** It deletes files, and deleted files only come back from a backup. Its rules were developed and checked on a single machine; on another system, with other software or in a later version of a program they can act differently. **Create at least one full backup or snapshot before the first deletion** and check that it can be restored. The skill does this together with you at the right point; you can also do it beforehand. Whoever uses the skill is responsible for what it does.

## Installation

### Claude Code

1. **Download the package.** `downloads/cleaning-up-linux-desktop_en_local.zip`

2. **Unpack it.** The archive contains a folder `cleaning-up-linux-desktop/` with all the files. Unpack it into `~/.claude/skills/` — then the skill applies to all projects — or into `.claude/skills/` in the project, then only there. An existing folder of the same name is replaced; nothing old is left behind.

### claude.ai and Claude Desktop (Chat + Cowork)

1. **Download the package.** `downloads/cleaning-up-linux-desktop_en_web.zip`

2. **Upload it.** Upload the archive in the application's management area for skills. The skill then applies to your account — not to your organization, and not at the same time in Claude Code.

## Details

### How the skill works

The skill starts no commands on the machine itself. It gives the user command blocks; the user runs them, including everything that needs `sudo`. The results end up as files in `/tmp`, where the skill reads them. In Claude Code the five scripts are in the skill folder; on claude.ai the user gets them as downloads and uploads the result files again.

Sequence:

0. Choose the mode: the skill first looks for the protocol and proposes whether it cleans up, cleans up the backups of an earlier run, or resumes an interrupted run.
1. Explain purpose and way of working, get confirmation, ask for the size threshold for large files (default 150 MiB) and whether archives should be included.
2. Determine the environment: desktop, the user folders according to XDG and download targets of Firefox and Chrome that differ from the default — the skill never inserts folder names such as "Downloads" or "Pictures" itself, they are named differently depending on the language.
3. Analysis: a single walk through the home, `/var`, `/opt`, `/usr/local` and `/srv`, read-only.
4. Fill level and three tables: **Table 1** — areas backed by tests; **Table 2** — cache folders of further programs that the skill researches at runtime, with evidence level; **Table 3** — statistics for exploring together (size per directory, large files, leftovers of uninstalled programs, duplicates, development artifacts).
5. Back up and create the protocol (see below).
6. Area by area through Table 1: show the details, get a decision, dry run, after confirmation the real run.
7. Result report: what was deleted and how much, what was skipped and what was only reported. This ends the actual run.
8. Follow-up, on request and stoppable at any time, with a new backup before it: first Table 2, then Table 3. For these items the skill has no tested experience; it clarifies them together with the user, with research in the documentation and with the explicit note before every deletion of what is established and what is assumption. For Table 2 the research is already there from the analysis, for Table 3 it only begins. Deleting in the follow-up is done with a fixed command block that checks mount points, links and the prefix of the skill's own backups per path and runs as a dry run first.

### The scripts

| File | Task |
| --- | --- |
| `analyze.py` | the analysis; writes `/tmp/cleanup-analysis.json`; with `--find-protocol` only the search for the protocol of earlier runs |
| `journal_stats.py` | the evaluation of journal and log files when this area is processed; writes `/tmp/cleanup-journal.json` |
| `delete.py` | the deletion, one area per run, with dry run (`--dry-run`); writes `/tmp/cleanup-report-<area>.json` |
| `snapshots.py` | own btrfs snapshots: create, list, remove, restore selectively |
| `backup.py` | archives (tar, tar.gz, zip) of the files to be deleted: create and verify, list, restore selectively, remove |

All five need only Python 3 with the standard library (`backup.py` additionally calls GNU `tar` for tar). Their screen messages are in English; the skill talks to the user in the user's language.

### Backup and protocol

Before the first deletion and before the follow-up the skill offers what the system provides, and the user chooses: confirm an own backup, a **btrfs snapshot**, the commands of **Timeshift** or **Snapper** if one of them is set up, or an **archive** of the files to be deleted as `tar` or `zip`. Established caches are not backed up; user data and application folders without evidence are, after asking.

- **Own backups** carry the name prefix `cleaning-up-linux-desktop-`. The scripts touch nothing without this prefix, and analysis as well as deletion runs exclude files with the prefix.
- **Snapshots** are stored by default in `<mount point>/.cleaning-up-linux-desktop-snapshots/`; the user can choose another location below the mount point. They are read-only and hold on to deleted data until they are removed. Every file system gets its own label, so that the names stay unique.
- **Archives** are stored in one folder per run, one file per backup step. Before writing, the script checks the space at the target including a reserve (default the larger of 10 % and 10 GiB, never below the larger of 5 % and 5 GiB); afterwards it compares the archive with the files. If anything fails, nothing is deleted. `tar` keeps owners, ACLs and extended attributes; `zip` does **not** keep them (nor hard links), but packs faster file by file.
- **Restoring** is selective: only what is missing comes back, nothing is overwritten.
- **ZFS and LVM** are detected and reported by the skill, but it offers no snapshot for them. A test system was missing; these variants are untested. There the user backs up personally or chooses the archive.
- **The protocol** `~/cleaning-up-linux-desktop-protocol.md` begins with the line `# cleaning-up-linux-desktop Protocol` and is short: per step "started" and "done", the names of all backups as steps of their own, skipped steps and particularities, plus a section "Special arrangements" for reuse. The skill deletes it only if the user wants. It keeps it in the home; rolling back a whole home snapshot would reset it to the state of the snapshot, which is why selective restoring is the default.

### What the deletion script always refuses

Regardless of the order, `delete.py` never deletes: `/`, the home itself, a folder directly below `/` or directly below the home, anything below `/boot`, anything outside the home, `/var`, `/opt`, `/usr/local` and `/srv`, a mount point, a folder that contains one, and everything that lies on one, anything with the prefix of the skill's own backups, and a symbolic link — except in the trash, and there only the link, never its target. This ban catches a translation error before it does damage; it must not be dropped in a simplification.

### Mount points, links and hanging runs

What is mounted — a network share, another drive, a bind mount — the scripts do not touch: no deleting, no walking, not even reading or counting. The occasion was the first run of the installed skill: the dry run for `__pycache__` hung in an SMB share below the home whose server did not answer. The process sat in the kernel (state `D`) and could not be ended right away even with `kill -KILL`. Therefore the scripts decide about mount points by name, against `/proc/self/mountinfo`, before making any access to the path; the list is read again at most once per second. In the home nothing is touched that lies on another mount point than the home itself, not even a fixed path and not a link target. Symbolic links are not followed; the only exception are the starter entries for Table 2, whose link target is read only if it lies on no foreign mount point. The fill level shows only local file systems, and trash folders on other drives stay untouched: the user empties them at their location. The target of an archive backup chosen by the user, even a network share, is only written to.

If a walk stays in the same folder for longer than 5 seconds, the script writes a line naming the folder to `stderr` every 5 seconds, and one more right away when it moves on. A hang thus becomes visible at its location. Time limits do not help against the hang itself as long as the process waits in the kernel; this is why avoiding it comes first. The stalls are also in the reports as the list `stalls`. External commands are not monitored. The protocol search (`analyze.py --find-protocol`) follows the same rules and needs no `sudo`.

### What "cache" means here

A folder counts as a deletable cache only if it is established that the program restores its data fully automatically at any time and that their absence changes nothing except time. What a folder is called does not count. Proxy files of a video editor, for instance, are not a cache, even if they should sit in a folder of that name: they are produced in a work step of their own and do not come back by themselves.

### Evidence and origin of the rules

Application-specific rules have so far been worked out for:

- Firefox
- Chrome
- VS Code
- Docker

Keep in mind that the rules can also become outdated, and follow the agent's work attentively.

The decisions with reasons and measurements are in `plan/concept.md`; the tests on which the rules for the applications rest are under `tests/`. Both are development material, do not travel into the package and remain in the author's working language (German).

The scripts determine the age of a file from the later of modification and status change time; Python on Linux does not provide the creation date. A file thus appears at most younger than it is, and in case of doubt it is not deleted.

## Status and open items

**Status:** Finished: instructions, scripts, both language versions and the installation packages for Claude Code and claude.ai. On the development machine a complete run with real deletions has gone through, across three sessions with an abort and a resumption; the scripts are also checked in tests of their own (`tests/`), among them `tests/test_mounts.py`, which records every file access to simulated mount points. The analysis ran through without a hang with a network share mounted below the home.

**Open:** nothing.

**Deliberately left open:** For some areas no treatment has been settled yet — search index Baloo, Git repositories, thumbnails, Claude Desktop caches, Flatpak, Snap, AppImage and Wine, Python environments, toolchains, Syncthing versions, duplicates and migration leftovers. The skill shows them in Table 3 and explores them together with the user on request, but deletes nothing there by rules of its own.
