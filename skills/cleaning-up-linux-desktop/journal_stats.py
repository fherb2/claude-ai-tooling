"""Read-only evaluation of the system journal and the log files (concept.md, section 4.5).

Runs when the area is processed, not in the first analysis. Only time,
priority and source of the journal entries are read, never message texts;
of the log files only time and size. Result as JSON, progress on stderr.

Mount points and links are never followed (concept.md, Grundsatz 8): in the home, nothing on
another mount than the home itself is touched; the journal and /var/log are named system sources.

Usage:
    sudo nice -n 19 ionice -c3 python3 -I journal_stats.py --home /home/<user> \
        [--output /tmp/cleanup-journal.json]
"""

import argparse
import glob
import json
import multiprocessing
import os
import re
import statistics
import stat
import subprocess
import sys
import threading
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

JOURNAL_DIRS = ["/var/log/journal", "/run/log/journal"]
LOG_DIR = "/var/log"
PREFIX = "cleaning-up-linux-desktop-"      # name prefix of the skill's own snapshots and archives
APP_CONTAINERS = [".config", ".local/share", ".cache", ".var"]
LEVELS = ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug", "none"]
BINS = [(f"day {n + 1}", n, n) for n in range(14)] + [
    ("days 15-28", 14, 27), ("days 29-56", 28, 55), ("days 57-140", 56, 139),
    ("days 141-365", 140, 364), ("older", 365, None)]
SPIKE_MIN = 10000
SPIKE_FACTOR = 10
GROUP_MIN = 100 * 1024**2
GROUP_WINDOW = 2 * 86400
SINGLE_MIN = 50 * 1024**2
TS = re.compile(r'"__REALTIME_TIMESTAMP":"(\d+)"')
PRIO = re.compile(r'"PRIORITY":"(\d+)"')
IDENT = re.compile(r'"SYSLOG_IDENTIFIER":"((?:[^"\\]|\\.)*)"')
COMM = re.compile(r'"_COMM":"((?:[^"\\]|\\.)*)"')
ROTATED = re.compile(r"(\.\d+(\.gz|\.xz|\.zst)?|-\d{8}(\.gz|\.xz|\.zst)?|\.gz|\.xz|\.zst|\.old)$")


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


WALK = Walker("journal_stats.py", newline=True)


def physical_cores():
    """Number of physical cores available to this process; logical CPUs if the topology is unreadable."""
    cpus = os.sched_getaffinity(0)
    cores = set()
    for cpu in cpus:
        try:
            with open(f"/sys/devices/system/cpu/cpu{cpu}/topology/core_cpus_list", encoding="ascii") as fh:
                cores.add(fh.read().strip())
        except OSError:
            return len(cpus)
    return len(cores) or len(cpus)


def journal_files():
    files = []
    for folder in JOURNAL_DIRS:
        for base, _, names in WALK.walk(folder):
            files += [os.path.join(base, n) for n in names if n.endswith((".journal", ".journal~"))]
    return sorted(files)


def disk_usage():
    try:
        out = subprocess.run(["journalctl", "--disk-usage"], capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return None
    return out or None


def count_file(path):
    """Counts per (date, level) and per (date, source) of one journal file; no message texts."""
    levels = defaultdict(int)
    sources = defaultdict(int)
    oldest = newest = None
    proc = subprocess.Popen(["journalctl", "--file", path, "-o", "json", "--no-pager", "-q",
                             "--output-fields=PRIORITY,SYSLOG_IDENTIFIER,_COMM"],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1 << 20)
    for line in proc.stdout:
        ts_match = TS.search(line)
        if not ts_match:
            continue
        ts = int(ts_match.group(1)) / 1e6
        oldest = ts if oldest is None or ts < oldest else oldest
        newest = ts if newest is None or ts > newest else newest
        day = datetime.fromtimestamp(ts).date().isoformat()
        prio = PRIO.search(line)
        level = int(prio.group(1)) if prio and int(prio.group(1)) <= 7 else 8
        levels[(day, level)] += 1
        source = IDENT.search(line) or COMM.search(line)
        sources[(day, source.group(1) if source else "(unnamed)")] += 1
    proc.wait()
    return path, dict(levels), dict(sources), oldest, newest


def histogram(levels, oldest, now):
    """Entries per period and level; each period counted only as far as the journal reaches."""
    today = datetime.fromtimestamp(now).date()
    rows = [{"period": label, "days_covered": 0.0, "counts": [0] * len(LEVELS)} for label, _, _ in BINS]
    for (day, level), count in levels.items():
        age = (today - date.fromisoformat(day)).days
        for row, (_, lo, hi) in zip(rows, BINS):
            if age >= lo and (hi is None or age <= hi):
                row["counts"][level] += count
                break
    if oldest is not None:
        midnight = datetime.combine(today, datetime.min.time()).timestamp()
        for row, (_, lo, hi) in zip(rows, BINS):
            end = now if lo == 0 else midnight - (lo - 1) * 86400
            start = midnight - hi * 86400 if hi is not None else oldest
            row["days_covered"] = round(max(0.0, end - max(start, oldest)) / 86400, 2)
    return {"levels": LEVELS, "rows": rows}


def spikes(sources):
    """Days on which a source logs at least SPIKE_MIN entries and more than SPIKE_FACTOR times its median."""
    per_source = defaultdict(dict)
    for (day, source), count in sources.items():
        per_source[source][day] = count
    found = []
    for source, days in per_source.items():
        median = statistics.median(days.values())
        for day, count in days.items():
            if count >= SPIKE_MIN and count > SPIKE_FACTOR * median:
                found.append({"source": source, "date": day, "count": count, "median": median,
                              "excess": count - median})
    return sorted(found, key=lambda s: -s["excess"])


def top_sources(sources, limit=15):
    totals = defaultdict(int)
    for (_, source), count in sources.items():
        totals[source] += count
    total = sum(totals.values()) or 1
    return [{"source": s, "count": c, "share": round(c / total, 4)}
            for s, c in sorted(totals.items(), key=lambda i: -i[1])[:limit]]


def log_candidates(home):
    """Log files after the boundary of 4.5: /var/log without the journal, in the home only application folders."""
    journal = os.path.join(LOG_DIR, "journal")
    for folder, dirs, files in WALK.walk(LOG_DIR):
        dirs[:] = [d for d in dirs if os.path.join(folder, d) != journal]
        for name in files:
            yield os.path.join(folder, name)
    for container in APP_CONTAINERS:
        for folder, dirs, files in WALK.walk(os.path.join(home, container)):
            in_log_dir = any(p in ("log", "logs") for p in folder.split(os.sep))
            for name in files:
                if in_log_dir or ".log" in name:
                    yield os.path.join(folder, name)


def log_files(home):
    """Rotated files grouped per program; conspicuous groups and single files after the thresholds of 4.5."""
    groups = defaultdict(list)
    for path in log_candidates(home):
        try:
            st = os.lstat(path)
        except OSError:
            continue
        if not stat.S_ISREG(st.st_mode):          # from lstat: a link is not followed
            continue
        key = os.path.join(os.path.dirname(path), ROTATED.sub("", os.path.basename(path)))
        groups[key].append((st.st_mtime, st.st_size, path))
    rows, total = [], 0
    for key, members in groups.items():
        size = sum(m[1] for m in members)
        total += size
        reasons = []
        if size >= GROUP_MIN and burst(members, size):
            reasons.append("more than half within two days")
        big = [m for m in members if m[1] >= SINGLE_MIN]
        if big:
            reasons.append("single file from 50 MiB")
        if reasons:
            rows.append({"group": key, "files": len(members), "size": size, "reasons": reasons,
                         "newest": int(max(m[0] for m in members)),
                         "big_files": [{"path": m[2], "size": m[1]} for m in big]})
    return {"total_size": total, "groups": len(groups),
            "conspicuous": sorted(rows, key=lambda r: -r["size"])}


def burst(members, size):
    """True if more than half of the bytes have modification times within GROUP_WINDOW."""
    items = sorted(members)
    start, window = 0, 0
    for end in range(len(items)):
        window += items[end][1]
        while items[end][0] - items[start][0] > GROUP_WINDOW:
            window -= items[start][1]
            start += 1
        if window > size / 2:
            return True
    return False


def max_level_store():
    """Configured MaxLevelStore; the last setting read wins, default debug."""
    value, source = "debug", "default"
    paths = (["/usr/lib/systemd/journald.conf.d/" + n for n in sorted(os.listdir("/usr/lib/systemd/journald.conf.d"))]
             if os.path.isdir("/usr/lib/systemd/journald.conf.d") else [])
    paths += ["/etc/systemd/journald.conf"] + sorted(glob.glob("/etc/systemd/journald.conf.d/*.conf"))
    for path in paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("MaxLevelStore="):
                        value, source = line.split("=", 1)[1].strip(), path
        except OSError:
            pass
    return {"value": value, "source": source}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--home", required=True)
    parser.add_argument("--output", default="/tmp/cleanup-journal.json")
    args = parser.parse_args()
    home = os.path.realpath(args.home)
    WALK.home = home
    now = time.time()
    if os.geteuid() != 0:
        print("Warning: not running as root; the journal may be incomplete.", file=sys.stderr)

    files = journal_files()
    cores = physical_cores()
    workers = max(1, min(-(-cores // 2), len(files)))      # half the physical cores, rounded up
    print(f"Step 1/2: reading {len(files)} journal files with {workers} workers ({cores} cores)", file=sys.stderr)
    levels, sources = defaultdict(int), defaultdict(int)
    oldest = newest = None
    with multiprocessing.Pool(workers) as pool:
        for done, (_, lv, src, old, new) in enumerate(pool.imap_unordered(count_file, files), 1):
            for k, v in lv.items():
                levels[k] += v
            for k, v in src.items():
                sources[k] += v
            if old is not None:
                oldest = old if oldest is None or old < oldest else oldest
                newest = new if newest is None or new > newest else newest
            print(f"\r  {done}/{len(files)} files", end="", file=sys.stderr, flush=True)
    print("\nStep 2/2: log files", file=sys.stderr)

    data = {
        "meta": {"tool": "journal_stats.py",
                 "started": datetime.fromtimestamp(now, timezone.utc).isoformat(timespec="seconds"),
                 "duration_s": round(time.time() - now, 1), "journal_files": len(files),
                 "cores": cores, "workers": workers, "stalls": WALK.stalls,
                 "entries": sum(levels.values()),
                 "oldest": datetime.fromtimestamp(oldest).isoformat(timespec="minutes") if oldest else None},
        "journal_disk_usage": disk_usage(),
        "histogram": histogram(levels, oldest, now),
        "top_sources": top_sources(sources),
        "spikes": spikes(sources),
        "log_files": log_files(home),
        "max_level_store": max_level_store(),
    }
    data["meta"]["duration_s"] = round(time.time() - now, 1)
    tmp = args.output + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o644)
    os.replace(tmp, args.output)
    print(f"Done: {data['meta']['entries']:,} entries, {len(data['spikes'])} spikes, "
          f"{len(data['log_files']['conspicuous'])} conspicuous log groups. Result: {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
