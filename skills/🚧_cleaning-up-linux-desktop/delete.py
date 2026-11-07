"""Deletion for the cleaning-up-linux-desktop skill: one area per run, as ordered by the instance.

An order is either a list (paths or containers the user selected) or a rule
(the area with its parameters; the rule of concept.md section 4 is applied
here). A fixed ban protects system and home roots regardless of the order.
With --dry-run nothing is deleted and no command is run; the report shows
what would happen. The report is written as JSON.

Usage:
    sudo python3 -I delete.py --home /home/<user> --order <order.json> [--dry-run] \
        [--report /tmp/cleanup-report-<area>.json]

Order examples:
    {"area": "4.9", "kind": "list", "paths": ["/home/u/Downloads/x.iso"]}
    {"area": "4.14", "kind": "rule", "params": {"days": 14}}
    {"area": "4.13", "kind": "rule", "params": {"containers": ["old_one"], "keep_images": ["a:latest"],
                                                 "builder_until_hours": 48}}
"""

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from urllib.parse import unquote

DAY = 86400
CACHE_AGE = 3 * DAY
STALE_PROFILE_AGE = 30 * DAY
WALKED_ROOTS = ["/var", "/opt", "/usr/local", "/srv"]
PREFIX = "cleaning-up-linux-desktop-"
BASE_NAME = ".cleaning-up-linux-desktop-snapshots"
APT_ARCHIVES = "/var/cache/apt/archives"
LOG_DIR = "/var/log"
JOURNAL_DIR = "/var/log/journal"
VSCODE_PRODUCT = "/usr/share/code/resources/app/product.json"
ENTRY_NAME = re.compile(r"^[0-9a-f]{16}_")
ROTATED = re.compile(r"(\.\d+(\.gz|\.xz|\.zst)?|-\d{8}(\.gz|\.xz|\.zst)?|\.gz|\.xz|\.zst|\.old)$")
PROGRAMS = {"firefox": ("firefox", "firefox-bin"), "chrome": ("chrome",), "code": ("code",)}


def is_own(name):
    """Names of the skill's own snapshots, archives and their container folders."""
    return name.lstrip(".").startswith(PREFIX)


STALL_SECONDS = 5
MOUNT_REFRESH = 1.0


def unescape_mount(field):
    """Undo the octal escapes of /proc/self/mountinfo (space, tab, newline, backslash); UTF-8 stays as it is."""
    return re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), field)


def mount_points():
    """All mount points, bind mounts on the same file system included (/proc/self/mountinfo)."""
    points = set()
    try:
        with open("/proc/self/mountinfo", encoding="utf-8", errors="surrogateescape") as fh:
            for line in fh:
                fields = line.split()
                if len(fields) > 4:
                    points.add(unescape_mount(fields[4]))
    except OSError:
        pass
    return points


class Walker:
    """Folder walks that never touch a mount point and never follow a link (concept.md, Grundsatz 8),
    with a line on stderr while a walk stays in one folder longer than STALL_SECONDS.

    Mount points are recognised by name against /proc/self/mountinfo before any system call on them,
    because already a stat of an unresponsive network mount blocks. In the home, nothing is touched that
    lies on another mount than the home itself (set home); other start points are the caller's choice."""

    def __init__(self, script, newline=False):
        self.script, self.newline = script, newline
        self.home = None
        self.stall_seconds = STALL_SECONDS
        self.points, self.read_at = set(), None
        self.lock = threading.Lock()
        self.thread = None
        self.active = []                    # folder each running walk is reading, innermost last
        self.folder = self.since = None
        self.stalled = None                 # folder named in the last stall line
        self.stalls = []                    # [{"folder", "seconds"}] for the report

    def mounts(self, fresh=False):
        """Mount points, read again when older than MOUNT_REFRESH seconds or when fresh is asked for."""
        now = time.monotonic()
        if fresh or self.read_at is None or now - self.read_at >= MOUNT_REFRESH:
            self.points, self.read_at = mount_points(), now
        return self.points

    def on_other_mount(self, path, base, fresh=False):
        """True if a mount point lies at path or between base and path: seen from base, path is mounted data."""
        prefix = base.rstrip(os.sep) + os.sep
        target = path.rstrip(os.sep) + os.sep
        return any(m.startswith(prefix) and target.startswith(m.rstrip(os.sep) + os.sep)
                   for m in self.mounts(fresh))

    def mount_of(self, path):
        """The mount point path lies on, by name: the longest mount point that is a prefix of path."""
        target = path.rstrip(os.sep) + os.sep
        return max((m for m in self.mounts() if target.startswith(m.rstrip(os.sep) + os.sep)), key=len, default="/")

    def contains_mount(self, path, fresh=False):
        """True if path is a mount point or one lies below it."""
        prefix = path.rstrip(os.sep) + os.sep
        return any(m == path or m.startswith(prefix) for m in self.mounts(fresh))

    def allowed(self, path):
        """False for a path in the home that is or lies below a mount point inside the home."""
        return not (self.home and path.startswith(self.home + os.sep) and self.on_other_mount(path, self.home))

    def listdir(self, path):
        """Sorted names in path without mount points; empty if path itself is not allowed or unreadable."""
        if not self.allowed(path):
            return []
        try:
            names = os.listdir(path)
        except OSError:
            return []
        points = self.mounts()
        return sorted(n for n in names if os.path.join(path, n) not in points)

    def walk(self, top, skipped=None):
        """Top-down walk like os.walk(top): yields (folder, dirs, files); dirs may be pruned in place.
        Never enters a mount point, a folder on another device, a link or a folder with the own prefix;
        they go to skipped as (path, reason) if a list is given. Links are listed in files."""
        if not self.allowed(top):
            if skipped is not None:
                skipped.append((top, "on another mount than the home"))
            return
        try:
            st = os.lstat(top)
        except OSError:
            return
        if stat.S_ISLNK(st.st_mode):           # scandir would follow it
            if skipped is not None:
                skipped.append((top, "link"))
            return
        device = st.st_dev
        self.begin()
        stack = [top]
        try:
            while stack:
                folder = stack.pop()
                self.enter(folder)
                try:
                    with os.scandir(folder) as it:
                        entries = list(it)
                except OSError:
                    continue
                points = self.mounts()
                dirs, files = [], []
                for entry in entries:
                    if entry.path in points:
                        reason = "mount point"
                    elif is_own(entry.name):
                        reason = "own snapshot or archive (prefix)"
                    else:
                        try:
                            if not entry.is_dir(follow_symlinks=False):
                                files.append(entry.name)
                                continue
                            if entry.stat(follow_symlinks=False).st_dev == device:
                                dirs.append(entry.name)
                                continue
                        except OSError:
                            continue
                        reason = "other file system"
                    if skipped is not None:
                        skipped.append((entry.path, reason))
                yield folder, dirs, files
                stack.extend(os.path.join(folder, d) for d in reversed(dirs))
        finally:
            self.leave()

    def begin(self):
        """Start of a walk; walks may nest (a size inside a walk), each ends with leave()."""
        self.active.append(None)

    def enter(self, folder):
        """The walk starts reading folder: progress for the stall check."""
        with self.lock:
            now = time.monotonic()
            if self.stalled is not None:
                self._moved_on(now, folder)
            self.active[-1] = folder
            self.folder, self.since = folder, now
        if self.thread is None:
            self.thread = threading.Thread(target=self._watch, daemon=True)
            self.thread.start()

    def leave(self):
        """End of a walk; an outer walk continues in its folder."""
        with self.lock:
            now = time.monotonic()
            self.active.pop()
            outer = self.active[-1] if self.active else None
            if self.stalled is not None:
                self._moved_on(now, outer)
            self.folder, self.since = outer, now

    def _moved_on(self, now, folder):
        seconds = round(now - self.since)
        self.stalls.append({"folder": self.stalled, "seconds": seconds})
        where = f', now in "{folder}"' if folder else ", walk finished"
        self._say(f'moved on after {seconds} s in "{self.stalled}"{where}')
        self.stalled = None

    def _watch(self):
        while True:
            time.sleep(self.stall_seconds)
            with self.lock:
                if self.folder is None:
                    continue
                seconds = time.monotonic() - self.since
                if seconds < self.stall_seconds:
                    continue
                hint = "" if self.stalled else " (huge folder or unresponsive mount?)"
                self.stalled = self.folder
                self._say(f'still in "{self.folder}" after {round(seconds)} s, no progress{hint}')

    def _say(self, text):
        print(("\n" if self.newline else "") + f"{self.script}: {text}", file=sys.stderr, flush=True)


WALK = Walker("delete.py")


class Report:
    def __init__(self, area, dry_run, with_paths=False):
        self.with_paths = with_paths
        self.data = {"area": area, "dry_run": dry_run, "removed_bytes": 0, "removed_count": 0,
                     "groups": {}, "removed": [], "skipped": [], "commands": []}
        if with_paths:
            self.data["candidates"] = []

    def removed(self, path, size, group=None):
        self.data["removed_bytes"] += size
        self.data["removed_count"] += 1
        if self.with_paths:
            self.data["candidates"].append(path)
        if group:
            g = self.data["groups"].setdefault(group, {"count": 0, "bytes": 0})
            g["count"] += 1
            g["bytes"] += size
        else:
            self.data["removed"].append({"path": path, "size": size})

    def skipped(self, path, reason):
        self.data["skipped"].append({"path": path, "reason": reason})

    def command(self, cmd, returncode, output=""):
        self.data["commands"].append({"command": cmd, "returncode": returncode, "output": output[-2000:]})


class Guard:
    """The fixed ban: independent of the order, these paths are never deleted."""

    def __init__(self, home):
        self.home = home
        self.roots = [home] + WALKED_ROOTS
        self.devices = {}
        for root in self.roots:
            try:
                self.devices[root] = os.stat(root).st_dev
            except OSError:
                pass

    def reason(self, path, allow_link=False):
        """Why path must not be deleted, or None. allow_link: the link itself may go (trash), never its target."""
        path = os.path.normpath(path)
        if not os.path.isabs(path):
            return "not an absolute path"
        if path in ("/", self.home) or os.path.dirname(path) == "/":
            return "root or home itself or directly under /"
        if path == "/boot" or path.startswith("/boot/"):
            return "under /boot"
        root = next((r for r in self.roots if path.startswith(r + os.sep)), None)
        if root is None:
            return "outside the analysed roots"
        if any(is_own(part) for part in path.split(os.sep) if part):
            return "own snapshot or archive (prefix)"
        # by name before any system call: a stat on an unresponsive mount already blocks
        if WALK.contains_mount(path):
            return "is or contains a mount point"
        if WALK.on_other_mount(path, root):
            return "lies on a mount point"
        try:
            st = os.lstat(path)
        except FileNotFoundError:
            return "does not exist"
        except OSError as exc:
            return f"not accessible: {exc.strerror}"
        if os.path.islink(path) and not allow_link:
            return "symbolic link"
        if os.path.dirname(path) == self.home and os.path.isdir(path):
            return "folder directly under home"
        if root in self.devices and st.st_dev != self.devices[root]:
            return "other file system"
        return None


class Deleter:
    def __init__(self, home, dry_run, report):
        self.guard = Guard(home)
        self.dry_run = dry_run
        self.report = report

    def remove(self, path, group=None, allow_link=False):
        """Delete one file or folder after the ban check; True if removed (or would be, in a dry run)."""
        reason = self.guard.reason(path, allow_link)
        if reason:
            self.report.skipped(path, reason)
            return False
        size, inside = tree_info(path)
        if inside:
            self.report.skipped(path, f"contains {inside[0][1]}: {inside[0][0]}")
            return False
        if not self.dry_run:
            if WALK.contains_mount(path, fresh=True):          # mounted since the check above
                self.report.skipped(path, "is or contains a mount point")
                return False
            try:
                if not os.path.islink(path) and os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
            except OSError as exc:
                self.report.skipped(path, f"delete failed: {exc.strerror}")
                return False
        self.report.removed(path, size, group)
        return True

    def command(self, cmd, user=None):
        """Run a cleanup command of a program (Grundsatz 3); in a dry run only report it."""
        full = (["runuser", "-u", user, "--"] if user else []) + cmd
        if self.dry_run:
            self.report.command(" ".join(full), None, "dry run, not executed")
            return None
        try:
            done = subprocess.run(full, capture_output=True, text=True)
        except FileNotFoundError:
            self.report.command(" ".join(full), None, "command not found")
            return None
        self.report.command(" ".join(full), done.returncode, done.stdout + done.stderr)
        return done


def tree_info(path):
    """Size of a file or folder, and what a walk of the folder had to leave out (mount points, other file
    systems, own folders) as [(path, reason)]; rmtree would not leave it out."""
    if not WALK.allowed(path):
        return 0, [(path, "on another mount than the home")]
    try:
        if os.path.islink(path) or not os.path.isdir(path):
            return os.lstat(path).st_size, []
    except OSError:
        return 0, []
    total, left_out = 0, []
    for folder, _, files in WALK.walk(path, left_out):
        for name in files:
            try:
                total += os.lstat(os.path.join(folder, name)).st_size
            except OSError:
                pass
    return total, left_out


def tree_size(path):
    return tree_info(path)[0]


def age(path, now):
    """Seconds since the later of modification and status change (concept.md, section 2)."""
    st = os.lstat(path)
    return now - max(st.st_mtime, st.st_ctime)


def listdir(path):
    return WALK.listdir(path)


def running(program):
    """True if a process of the program runs; read from /proc, not pgrep."""
    names = PROGRAMS[program]
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            exe = os.path.basename(os.readlink(f"/proc/{pid}/exe"))
        except OSError:
            continue
        if exe in names:
            return True
    return False


def old_entries(d, folder, now, group, pattern=None):
    """Delete entry files older than three days directly in folder; folders stay."""
    for name in listdir(folder):
        path = os.path.join(folder, name)
        if not os.path.islink(path) and os.path.isfile(path) and (pattern is None or pattern.match(name)):
            if age(path, now) > CACHE_AGE:
                d.remove(path, group)


def index_files(d, folder, names, program, group):
    """Index files and folders only while the program does not run."""
    for name in names:
        path = os.path.join(folder, name)
        if WALK.allowed(path) and os.path.lexists(path):
            if running(program):
                d.report.skipped(path, f"{program} is running")
            else:
                d.remove(path, group)


# --- rules per area ---------------------------------------------------------------------------

def rule_apt(d, home, params, now):
    """4.1: apt-get clean; the removed amount is measured beforehand."""
    archives = APT_ARCHIVES
    size = sum(tree_size(os.path.join(archives, n)) for n in listdir(archives) if n.endswith(".deb"))
    size += sum(tree_size(os.path.join(archives, "partial", n)) for n in listdir(os.path.join(archives, "partial")))
    done = d.command(["apt-get", "clean"])
    if d.dry_run or (done and done.returncode == 0):
        d.report.removed(archives, size, "apt archives")


def rule_firefox(d, home, params, now):
    """4.2: old entries per profile, index only when Firefox does not run, stale remnants in the profiles."""
    cache = os.path.join(home, ".cache/mozilla/firefox")
    for profile in listdir(cache):
        cache2 = os.path.join(cache, profile, "cache2")
        old_entries(d, os.path.join(cache2, "entries"), now, "entries")
        index_files(d, cache2, ["index"], "firefox", "index")
    profiles = os.path.join(home, ".mozilla/firefox")
    for profile in listdir(profiles):
        for name in ("cache2", "startupCache"):
            path = os.path.join(profiles, profile, name)
            if WALK.allowed(path) and not os.path.islink(path) and os.path.isdir(path) and newest_mtime(path) < now - STALE_PROFILE_AGE:
                d.remove(path, "profile remnants")


def newest_mtime(path):
    newest = 0
    for folder, _, files in WALK.walk(path):
        for name in files:
            try:
                newest = max(newest, os.lstat(os.path.join(folder, name)).st_mtime)
            except OSError:
                pass
    return newest


def rule_chrome(d, home, params, now):
    """4.3: old entries in Cache_Data and Code Cache/js per profile, index only when Chrome does not run."""
    cache = os.path.join(home, ".cache/google-chrome")
    for profile in listdir(cache):
        for parts in (("Cache", "Cache_Data"), ("Code Cache", "js")):
            folder = os.path.join(cache, profile, *parts)
            if WALK.allowed(folder) and not os.path.islink(folder) and os.path.isdir(folder):
                old_entries(d, folder, now, "entries", ENTRY_NAME)
                index_files(d, folder, ["index", "index-dir"], "chrome", "index")


def rule_vscode(d, home, params, now):
    """4.4: Cache_Data entries, old CachedData folders, broken VSIX downloads; CacheStorage is never touched."""
    base = os.path.join(home, ".config/Code")
    folder = os.path.join(base, "Cache/Cache_Data")
    old_entries(d, folder, now, "entries", ENTRY_NAME)
    index_files(d, folder, ["index", "index-dir"], "code", "index")
    commit = None
    try:
        with open(VSCODE_PRODUCT, encoding="utf-8") as fh:
            commit = json.load(fh).get("commit")
    except (OSError, ValueError):
        d.report.skipped("CachedData", "installed version unknown; CachedData left alone")
    if commit:
        cached = os.path.join(base, "CachedData")
        for name in listdir(cached):
            path = os.path.join(cached, name)
            if name != commit and not os.path.islink(path) and os.path.isdir(path) and newest_mtime(path) < now - CACHE_AGE:
                d.remove(path, "CachedData")
    vsix = os.path.join(base, "CachedExtensionVSIXs")
    for name in listdir(vsix):
        path = os.path.join(vsix, name)
        if name.startswith(".") and not os.path.islink(path) and os.path.isfile(path) and age(path, now) > CACHE_AGE and not is_zip(path):
            d.remove(path, "broken VSIX downloads")


def is_zip(path):
    try:
        with open(path, "rb") as fh:
            return fh.read(4) == b"PK\x03\x04"
    except OSError:
        return False


def rule_logs(d, home, params, now):
    """4.5: journal older than x days (journalctl), rotated archived log files older than x days."""
    days = int(params["days"])
    journal = JOURNAL_DIR
    before = tree_size(journal)
    done = d.command(["journalctl", f"--vacuum-time={days}d"])
    if not d.dry_run and done and done.returncode == 0:
        d.report.removed(journal, max(0, before - tree_size(journal)), "journal")
    limit = now - days * DAY
    candidates = [(LOG_DIR, True)] + [(os.path.join(home, c), False)
                                         for c in (".config", ".local/share", ".cache", ".var")]
    for base, everything in candidates:
        for folder, dirs, files in WALK.walk(base):
            dirs[:] = [x for x in dirs if os.path.join(folder, x) != JOURNAL_DIR]
            in_log_dir = everything or any(p in ("log", "logs") for p in folder.split(os.sep))
            for name in files:
                if not (in_log_dir or ".log" in name) or not ROTATED.search(name):
                    continue
                path = os.path.join(folder, name)
                try:
                    if os.lstat(path).st_mtime < limit:
                        d.remove(path, "rotated log files")
                except OSError:
                    pass


def rule_pip(d, home, params, now):
    """4.6: pip cache purge as the owner of the home; the amount is measured before and after."""
    cache = os.path.join(home, ".cache/pip")
    if not WALK.allowed(cache):
        d.report.skipped(cache, "on another mount than the home")
        return
    before = tree_size(cache)
    user = owner(home)
    done = d.command(["python3", "-m", "pip", "cache", "purge"], user=user)
    if d.dry_run:
        d.report.removed(cache, before, "pip cache")
    elif done and done.returncode == 0:
        d.report.removed(cache, max(0, before - tree_size(cache)), "pip cache")


def owner(path):
    import pwd
    return pwd.getpwuid(os.stat(path).st_uid).pw_name


def rule_pycache(d, home, params, now):
    """4.12: every __pycache__ folder in the home, including the folder."""
    for folder, dirs, _ in WALK.walk(home):
        if "__pycache__" in dirs:
            d.remove(os.path.join(folder, "__pycache__"), "__pycache__")
            dirs.remove("__pycache__")


def rule_docker(d, home, params, now):
    """4.13: selected stopped containers (with anonymous volumes), images without container
    except the keep list, build cache older than the limit. No sizes (concept.md 4.13)."""
    for name in params.get("containers", []):
        d.command(["docker", "rm", "-v", name])
    keep = set(params.get("keep_images", []))
    used = docker_lines(["docker", "ps", "-a", "--format", "{{.Image}}"])
    for image in docker_lines(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"]):
        if image in used or image in keep or image.endswith(":<none>"):
            continue
        d.command(["docker", "rmi", image])
    hours = params.get("builder_until_hours")
    if hours is not None:
        d.command(["docker", "builder", "prune", "--all", "--force", "--filter", f"until={int(hours)}h"])


def docker_lines(cmd):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return set()
    return {line.strip() for line in done.stdout.splitlines() if line.strip()}


def rule_trash(d, home, params, now):
    """4.14: entries longer than x days in the trash (DeletionDate); file and .trashinfo together."""
    days = int(params["days"])
    limit = now - days * DAY
    for trash in [os.path.join(home, ".local/share/Trash")]:      # trash on other file systems: never (4.14)
        if not WALK.allowed(trash):
            d.report.skipped(trash, "on another mount than the home")
            continue
        info, files = os.path.join(trash, "info"), os.path.join(trash, "files")
        deleted = set()
        for name in listdir(info):
            if not name.endswith(".trashinfo"):
                continue
            info_path = os.path.join(info, name)
            if os.path.islink(info_path):
                d.report.skipped(info_path, "symbolic link")
                continue
            trashed = deletion_date(info_path)
            if trashed is None:
                d.report.skipped(info_path, "no valid DeletionDate")
                continue
            if trashed >= limit:
                continue
            item = os.path.join(files, name[:-len(".trashinfo")])
            if not WALK.allowed(item):
                d.report.skipped(item, "on another mount than the home")
                continue
            if os.path.lexists(item) and not d.remove(item, "trash entries", allow_link=True):
                continue          # the .trashinfo stays with its entry
            d.remove(info_path, "trashinfo")
            deleted.add(name[:-len(".trashinfo")])
        known = {n[:-len(".trashinfo")] for n in listdir(info) if n.endswith(".trashinfo")} | deleted
        for name in listdir(files):
            if name not in known:
                d.report.skipped(os.path.join(files, name), "no .trashinfo; age unknown")
        if deleted and not d.dry_run:
            prune_directorysizes(trash, deleted)


def deletion_date(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("DeletionDate="):
                    value = line.split("=", 1)[1].strip()
                    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y%m%dT%H:%M:%S"):
                        try:
                            return time.mktime(time.strptime(value, fmt))
                        except ValueError:
                            pass
    except OSError:
        pass
    return None


def prune_directorysizes(trash, deleted):
    """Drop the size-cache lines of deleted entries; temporary file plus rename, as the spec demands."""
    path = os.path.join(trash, "directorysizes")
    if os.path.islink(path):
        return
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return
    kept = [l for l in lines if unquote(l.rstrip("\n").split(" ", 2)[-1]) not in deleted]
    if len(kept) != len(lines):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.writelines(kept)
        os.replace(tmp, path)


RULES = {"4.1": rule_apt, "4.2": rule_firefox, "4.3": rule_chrome, "4.4": rule_vscode, "4.5": rule_logs,
         "4.6": rule_pip, "4.12": rule_pycache, "4.13": rule_docker, "4.14": rule_trash}
LIST_AREAS = {"4.7", "4.8", "4.9", "4.10"}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--home", required=True)
    parser.add_argument("--order", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--with-paths", action="store_true",
                        help="the report names every candidate path (for a backup before deleting)")
    parser.add_argument("--report")
    args = parser.parse_args()
    home = os.path.realpath(args.home)
    WALK.home = home
    with open(args.order, encoding="utf-8") as fh:
        order = json.load(fh)
    area, kind = str(order.get("area")), order.get("kind")
    report = Report(area, args.dry_run, args.with_paths)
    d = Deleter(home, args.dry_run, report)
    now = time.time()
    if kind == "list" and area in LIST_AREAS:
        for path in order.get("paths", []):
            d.remove(path)
    elif kind == "rule" and area in RULES:
        RULES[area](d, home, order.get("params", {}), now)
    else:
        print(f"Unknown order: area {area}, kind {kind}", file=sys.stderr)
        return 2
    report.data["stalls"] = WALK.stalls
    report.data["finished"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    target = args.report or f"/tmp/cleanup-report-{area}.json"
    tmp = target + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(report.data, fh, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o644)
    os.replace(tmp, target)
    data = report.data
    verb = "would remove" if args.dry_run else "removed"
    print(f"Area {area}: {verb} {data['removed_count']} items, {data['removed_bytes'] / 1024**2:,.1f} MiB; "
          f"{len(data['skipped'])} skipped. Report: {target}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
