"""Mount points and links are never touched (concept.md, Grundsatz 8), and stalls are reported.

Simulates mount points inside a throwaway home by adding their paths to the mount
list the scripts read, and records every file system call of the scripts. A call
on a path at or below a simulated mount point, or one that follows a link into it,
is a violation: on an unresponsive network mount, already this call blocks.
Needs no root. Prints PASSED or the list of deviations.

Usage: python3 -I tests/test_mounts.py [--delete F] [--analyze F] [--journal F] [--backup F] [--snapshots F]
    one option: test another version of that script only (negative control against an old version)
"""

import argparse
import builtins
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
DAY = 86400


def load(name, path=None):
    spec = importlib.util.spec_from_file_location(name, path or os.path.join(SKILL, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recorder:
    """Wraps the os functions the scripts use and records calls on forbidden paths."""

    NAMES = ["scandir", "listdir", "stat", "lstat", "open", "access", "readlink"]

    def __init__(self, mounts, links):
        self.mounts = [m.rstrip(os.sep) for m in mounts]
        self.links = [l.rstrip(os.sep) for l in links]
        self.hits = []
        self.saved = {}

    def forbidden(self, name, path):
        if not isinstance(path, str):
            return False
        path = os.path.normpath(path)
        for m in self.mounts:
            if path == m or path.startswith(m + os.sep):
                return True
        for link in self.links:
            if path.startswith(link + os.sep):
                return True              # anything through the link follows it
            if path == link and name not in ("lstat", "readlink"):
                return True              # stat, scandir, open of the link itself follow it
        return False

    def entry(self, e):
        """A DirEntry whose methods record like the os functions (DirEntry.stat does not call os.lstat)."""
        rec = self

        class Entry:
            name, path = e.name, e.path

            def _check(self, name, follow):
                effective = name if follow else "lstat"
                if rec.forbidden(effective, e.path):
                    rec.hits.append(f"DirEntry.{name}({e.path})")

            def is_dir(self, follow_symlinks=True):
                self._check("is_dir", follow_symlinks)
                return e.is_dir(follow_symlinks=follow_symlinks)

            def is_file(self, follow_symlinks=True):
                self._check("is_file", follow_symlinks)
                return e.is_file(follow_symlinks=follow_symlinks)

            def is_symlink(self):
                self._check("is_symlink", False)
                return e.is_symlink()

            def stat(self, follow_symlinks=True):
                self._check("stat", follow_symlinks)
                return e.stat(follow_symlinks=follow_symlinks)

            def inode(self):
                return e.inode()

            def __fspath__(self):
                return e.path

            def __lt__(self, other):
                return self.name < other.name
        return Entry()

    def wrap_scandir(self, func):
        rec = self

        class Scan:
            def __init__(self, *args, **kwargs):
                self.it = func(*args, **kwargs)

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                self.it.close()
                return False

            def __iter__(self):
                return self

            def __next__(self):
                return rec.entry(next(self.it))

            def close(self):
                self.it.close()
        return Scan

    def wrap(self, name, func):
        def call(*args, **kwargs):
            path = args[0] if args else kwargs.get("path")
            follow = kwargs.get("follow_symlinks", True)
            effective = "lstat" if name == "stat" and not follow else name
            if self.forbidden(effective, path):
                self.hits.append(f"{name}({path})")
            return func(*args, **kwargs)
        return call

    def __enter__(self):
        for name in self.NAMES:
            self.saved[name] = getattr(os, name)
            setattr(os, name, self.wrap(name, self.saved[name]))
        scan = self.wrap("scandir", self.saved["scandir"])
        os.scandir = self.wrap_scandir(scan)
        self.saved["builtin_open"] = builtins.open
        builtins.open = self.wrap("open", self.saved["builtin_open"])
        return self

    def __exit__(self, *exc):
        for name in self.NAMES:
            setattr(os, name, self.saved[name])
        builtins.open = self.saved["builtin_open"]
        return False


def write(path, data=b"x", age_days=0):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)
    if age_days:
        then = time.time() - age_days * DAY
        os.utime(path, (then, then))


def build_home(base):
    """A home with three simulated mount points and two links that point into them."""
    home = os.path.join(base, "home", "user")
    nas = os.path.join(home, "NAS711", "home")
    umlaut = os.path.join(home, "Bücher alt")
    cache_mount = os.path.join(home, ".cache", "mnt")
    for m in (nas, umlaut, cache_mount):
        write(os.path.join(m, "proj", "__pycache__", "x.pyc"))
        write(os.path.join(m, "app", "logs", "app.log.1"), age_days=60)
        write(os.path.join(m, ".Trash-1000", "info", "a.trashinfo"), b"[Trash Info]\nDeletionDate=2020-01-01T00:00:00\n")
        write(os.path.join(m, ".Trash-1000", "files", "a"))
    write(os.path.join(home, "proj", "__pycache__", "y.pyc"))
    write(os.path.join(home, ".config", "app", "logs", "app.log.1"), age_days=60)
    os.makedirs(os.path.join(home, ".mozilla", "firefox", "p.default"))
    links = [os.path.join(home, "proj", "naslink"), os.path.join(home, ".mozilla", "firefox", "p.default", "cache2")]
    os.symlink(nas, links[0])
    os.symlink(os.path.join(nas, "proj"), links[1])
    write(os.path.join(home, "Downloads", "withmount", "a"))
    write(os.path.join(home, "Downloads", "box", "cleaning-up-linux-desktop-backup-x", "01-a.tar"))
    write(os.path.join(home, "Downloads", "box", "b"))
    mounts = [nas, umlaut, cache_mount, os.path.join(home, "Downloads", "withmount", "inner")]
    os.makedirs(mounts[-1])
    return home, mounts, links


def check_delete(module_path, problems):
    d = load("delete", module_path)
    base = tempfile.mkdtemp(prefix="cleanup-mounts-", dir="/tmp")
    try:
        home, mounts, links = build_home(base)
        d.WALKED_ROOTS = [os.path.join(base, "var")]
        d.LOG_DIR = os.path.join(base, "var", "log")
        d.JOURNAL_DIR = os.path.join(base, "var", "log", "journal")
        os.makedirs(d.LOG_DIR)
        real_points = d.mount_points
        d.mount_points = lambda: real_points() | set(mounts)
        if hasattr(d, "WALK"):
            d.WALK.home = home
        d.running = lambda program: False
        d.owner = lambda path: "user"
        d.Deleter.command = lambda self, cmd, user=None: None
        reports = {}
        with Recorder(mounts, links) as rec:
            for area, rule, params in [("4.12", d.rule_pycache, {}), ("4.5", d.rule_logs, {"days": 14}),
                                       ("4.2", d.rule_firefox, {}),
                                       ("4.14", d.rule_trash, {"days": 0, "other_trashes": [
                                           os.path.join(m, ".Trash-1000") for m in mounts]})]:
                report = d.Report(area, True, with_paths=True)
                rule(d.Deleter(home, True, report), home, params, time.time())
                reports[area] = report.data
            report = d.Report("4.9", True)
            deleter = d.Deleter(home, True, report)
            for rel in ["NAS711/home/proj", "Bücher alt/proj/__pycache__", "Downloads/withmount", "Downloads/box"]:
                deleter.remove(os.path.join(home, rel))
            reports["4.9"] = report.data
        for hit in sorted(set(rec.hits)):
            problems.append(f"delete.py touched {os.path.relpath(hit, base) if hit.startswith('/') else hit}")
        found = [c for data in reports.values() for c in data.get("candidates", [])]
        for c in found:
            if any(c == m or c.startswith(m + os.sep) for m in mounts):
                problems.append(f"delete.py candidate on a mount point: {c}")
        if os.path.join(home, "proj", "__pycache__") not in reports["4.12"].get("candidates", []):
            problems.append("delete.py: __pycache__ outside the mounts not found (walk broken)")
        if os.path.join(home, ".config", "app", "logs", "app.log.1") not in reports["4.5"].get("candidates", []):
            problems.append("delete.py: rotated log outside the mounts not found (walk broken)")
        reasons = {s["path"]: s["reason"] for s in reports["4.9"]["skipped"]}
        expected = {"NAS711/home/proj": "lies on a mount point",
                    "Bücher alt/proj/__pycache__": "lies on a mount point",
                    "Downloads/withmount": "is or contains a mount point",
                    "Downloads/box": "contains own snapshot or archive (prefix): "
                                     + os.path.join(home, "Downloads/box/cleaning-up-linux-desktop-backup-x")}
        for rel, reason in expected.items():
            got = reasons.get(os.path.join(home, rel))
            if got != reason:
                problems.append(f"delete.py ban: {rel} -> {got!r}, expected {reason!r}")
    finally:
        shutil.rmtree(base)


def check_analyze(module_path, problems):
    a = load("analyze", module_path)
    base = tempfile.mkdtemp(prefix="cleanup-mounts-", dir="/tmp")
    try:
        home, mounts, links = build_home(base)
        flatpak = os.path.join(home, ".local", "share", "flatpak")
        write(os.path.join(flatpak, "app", "org.example.App", "x"))
        mounts.append(flatpak)
        nas = mounts[0]
        apps = os.path.join(home, ".local", "share", "applications")
        entry = b"[Desktop Entry]\nType=Application\nName=Good\nExec=good\nCategories=Utility;\n"
        write(os.path.join(apps, "good.desktop"), entry)
        write(os.path.join(home, "apps", "real.desktop"), entry.replace(b"Good", b"Linked"))
        write(os.path.join(nas, "nas.desktop"), entry.replace(b"Good", b"OnNas"))
        os.symlink(os.path.join(home, "apps", "real.desktop"), os.path.join(apps, "linked.desktop"))
        os.symlink(os.path.join(nas, "nas.desktop"), os.path.join(apps, "naslink.desktop"))
        links.append(os.path.join(apps, "naslink.desktop"))
        heading = b"# cleaning-up-linux-desktop Protocol\n\n- x\n"
        write(os.path.join(home, "notes", "protocol.md"), heading)
        write(os.path.join(nas, "old-protocol.md"), heading)
        os.symlink(os.path.join(nas, "old-protocol.md"), os.path.join(home, "notes", "plink.md"))
        links.append(os.path.join(home, "notes", "plink.md"))
        os.makedirs(os.path.join(home, "Downloads"), exist_ok=True)
        os.makedirs(os.path.join(nas, "Videos"))
        real_points = a.mount_points
        a.mount_points = lambda: real_points() | set(mounts)
        a.SYSTEM_ROOTS = []
        a.run = lambda cmd, timeout=None: None
        a.docker_state = lambda paths: {}
        a.desktop_dirs = lambda h: [(apps, "user")]
        out = os.path.join(base, "analysis.json")
        found = os.path.join(base, "found.txt")
        argv = sys.argv
        err = io.StringIO()
        with Recorder(mounts, links) as rec, contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            sys.argv = ["analyze.py", "--home", home, "--downloads", os.path.join(home, "Downloads"),
                        "--media-dir", os.path.join(nas, "Videos"), "--media-dir", mounts[1],
                        "--threshold", "1", "--output", out]
            code = a.main()
            if hasattr(a, "find_protocol"):
                sys.argv = ["analyze.py", "--home", home, "--find-protocol", "--output", found]
                a.main()
        sys.argv = argv
        for hit in sorted(set(rec.hits)):
            problems.append(f"analyze.py touched {hit}")
        if code != 0:
            problems.append(f"analyze.py exit {code}: {err.getvalue()[-300:]}")
            return
        with open(out, encoding="utf-8") as fh:
            data = json.load(fh)
        other = set(data["meta"]["other_filesystems"])
        for m in mounts:
            if m not in other:
                problems.append(f"analyze.py: mount point not listed in other_filesystems: {m}")
        not_read = data["meta"]["params"].get("not_read")
        if not_read != [os.path.join(nas, "Videos"), mounts[1]]:
            problems.append(f"analyze.py: not_read {not_read}")
        if len(data["table1"]["4.14_trash"]) != 1:
            problems.append(f"analyze.py: trash rows {data['table1']['4.14_trash']}")
        desktop = data["software"]["desktop"]
        names = {e["name"] for e in desktop["included"]}
        if names != {"Good", "Linked"}:
            problems.append(f"analyze.py: included starter entries {names}")
        if not any(e["path"].endswith("naslink.desktop") and e["reason"] == "link_not_followed"
                   for e in desktop["excluded"]):
            problems.append("analyze.py: link into the mount not reported as link_not_followed")
        for row in data["fill_level"]["mounts"]:
            if row["fstype"].startswith(("cifs", "smb", "nfs", "fuse", "9p", "ceph")) or row["fstype"] in a.EXCLUDED_FS:
                problems.append(f"analyze.py fill level shows {row['fstype']} at {row['mount']}")
        if hasattr(a, "find_protocol"):
            with open(found, encoding="utf-8") as fh:
                hits = fh.read().splitlines()
            if hits != [os.path.join(home, "notes", "protocol.md")]:
                problems.append(f"analyze.py --find-protocol: {hits}")
    finally:
        shutil.rmtree(base)


def check_journal(module_path, problems):
    j = load("journal_stats", module_path)
    base = tempfile.mkdtemp(prefix="cleanup-mounts-", dir="/tmp")
    try:
        home, mounts, links = build_home(base)
        var_log = os.path.join(base, "var", "log")
        write(os.path.join(var_log, "syslog.1"))
        write(os.path.join(var_log, "journal", "abc", "system.journal"))
        write(os.path.join(home, ".config", "app", "logs", "good.log.1"))
        j.LOG_DIR = var_log
        j.JOURNAL_DIRS = [os.path.join(var_log, "journal")]
        if hasattr(j, "mount_points"):                 # the old version does not know mount points at all
            real_points = j.mount_points
            j.mount_points = lambda: real_points() | set(mounts)
            j.WALK.home = home
        with Recorder(mounts, links) as rec:
            journals = j.journal_files()
            candidates = list(j.log_candidates(home))
            j.log_files(home)
        for hit in sorted(set(rec.hits)):
            problems.append(f"journal_stats.py touched {hit}")
        if journals != [os.path.join(var_log, "journal", "abc", "system.journal")]:
            problems.append(f"journal_stats.py: journal files {journals}")
        for want in (os.path.join(var_log, "syslog.1"), os.path.join(home, ".config", "app", "logs", "good.log.1")):
            if want not in candidates:
                problems.append(f"journal_stats.py: candidate missing (walk broken): {want}")
        if any(c.startswith(m + os.sep) for c in candidates for m in mounts):
            problems.append("journal_stats.py: candidate on a mount point")
    finally:
        shutil.rmtree(base)


class FakeKinds:
    """mount_kinds() of backup.py with simulated mounts: {path: (fstype, source)}."""

    def __init__(self, module, extra):
        self.real = module.mount_kinds
        self.extra = extra

    def __call__(self):
        return {**self.real(), **self.extra}


def check_backup(module_path, problems):
    b = load("backup", module_path)
    base = tempfile.mkdtemp(prefix="cleanup-mounts-", dir="/tmp")
    try:
        home, mounts, links = build_home(base)
        nas, umlaut, cache_mount = mounts[:3]
        usb = os.path.join(home, "usb")
        write(os.path.join(usb, "u.txt"))
        write(os.path.join(home, "keep", "k.txt"))
        os.makedirs(os.path.join(home, "keep", "mnt", "inner"))
        write(os.path.join(home, "keep", "mnt", "inner", "was-there.txt"))
        kinds = {nas: ("cifs", "//10.0.0.2/home"), umlaut: ("fuse.sshfs", "u@h:/x"), usb: ("ext4", "/dev/sdb1")}
        real_points = b.mount_points
        b.mount_points = lambda: real_points() | set(mounts) | {usb}
        if hasattr(b, "mount_kinds"):
            b.mount_kinds = FakeKinds(b, kinds)
        if hasattr(b, "WALK"):
            b.WALK.home = None
        target = os.path.join(base, "target")
        os.makedirs(target)
        # 1 validate: mount point and network mount refused, local mount allowed
        if hasattr(b, "mount_problem"):
            clean, errors = b.validate([nas, os.path.join(umlaut, "proj"), usb, os.path.join(home, "keep")], target)
            reasons = {e["path"]: e["reason"] for e in errors}
            if reasons.get(nas) != "is a mount point" or \
                    reasons.get(os.path.join(umlaut, "proj")) != "lies on a mount that is not a local file system" or \
                    reasons.get(usb) != "is a mount point" or clean != [os.path.join(home, "keep")]:
                problems.append(f"backup.py validate: {reasons} / {clean}")
        # 2 walk: the mount point inside the path is left out and not touched
        keep_mount = os.path.join(home, "keep", "mnt")
        b.mount_points = lambda: real_points() | set(mounts) | {usb, keep_mount}
        if hasattr(b, "WALK"):
            b.WALK.read_at = None
        with Recorder([keep_mount], links) as rec:
            entries, skipped = b.walk_entries([os.path.join(home, "keep")]) if hasattr(b, "WALK") else \
                b.walk_entries([os.path.join(home, "keep")], b.mount_points())
        for hit in sorted(set(rec.hits)):
            if not hit.startswith(("lstat(", "stat(", "DirEntry.stat(", "DirEntry.is_dir(", "DirEntry.is_symlink(")) \
                    or not hit.endswith(f"{keep_mount})"):
                problems.append(f"backup.py walk touched {hit}")
        names = {os.path.relpath(p, home) for p, _, _ in entries}
        if "keep/k.txt" not in names or any(n.startswith("keep/mnt/") for n in names):
            problems.append(f"backup.py walk entries: {sorted(names)}")
        # 3 create: tar is given the entries, so the content of the mount point is not in the archive
        listing = os.path.join(base, "list.json")
        with open(listing, "w", encoding="utf-8") as fh:
            json.dump({"paths": [os.path.join(home, "keep")]}, fh)
        import argparse as ap
        for fmt in ("tar", "zip"):
            args = ap.Namespace(target=target, step=f"s-{fmt}", list=listing, format=fmt, run=None, dry_run=False,
                                reserve_percent=None, reserve_gib=None, verify="full")
            args.run = b.RUN_PREFIX + "test-" + fmt
            result = b.do_create(args)
            if not result.get("ok"):
                problems.append(f"backup.py create {fmt}: {result.get('error')}")
                continue
            archive = result["archive"]
            if fmt == "tar":
                members = subprocess.run(["tar", "--list", "-f", archive], capture_output=True, text=True).stdout
            else:
                import zipfile
                members = "\n".join(zipfile.ZipFile(archive).namelist())
            if "was-there.txt" in members or "keep/k.txt" not in members:
                problems.append(f"backup.py create {fmt}: content of the mount point in the archive or data missing")
        # 4 restore: archives made while keep/mnt was a plain folder; later a network share is mounted on it
        if hasattr(b, "split_mounted"):
            b.mount_points = lambda: real_points() | set(mounts) | {usb}
            b.mount_kinds = FakeKinds(b, kinds)
            b.WALK.read_at = None                 # the walker keeps the mount list for a second
            for fmt in ("tar", "zip"):
                args = ap.Namespace(target=target, step=f"r-{fmt}", list=listing, format=fmt,
                                    run=b.RUN_PREFIX + "restore-" + fmt, dry_run=False,
                                    reserve_percent=None, reserve_gib=None, verify="full")
                if not b.do_create(args).get("ok"):
                    problems.append(f"backup.py create {fmt} for the restore test failed")
            b.mount_points = lambda: real_points() | set(mounts) | {usb, keep_mount}
            b.mount_kinds = FakeKinds(b, {**kinds, keep_mount: ("cifs", "//10.0.0.2/x")})
            b.WALK.read_at = None
            for fmt in ("tar", "zip"):
                os.unlink(os.path.join(home, "keep", "k.txt"))
                restore_args = ap.Namespace(target=target, run=b.RUN_PREFIX + "restore-" + fmt, step=f"r-{fmt}",
                                            path=None, dry_run=False)
                with Recorder([keep_mount], links) as rec:
                    result = b.do_restore(restore_args)
                for hit in sorted(set(rec.hits)):
                    problems.append(f"backup.py restore {fmt} touched {hit}")
                shown = {x["path"] for x in result.get("not_restored", [])}
                if keep_mount not in shown or not os.path.exists(os.path.join(home, "keep", "k.txt")):
                    problems.append(f"backup.py restore {fmt}: {result}")
    finally:
        shutil.rmtree(base)


def check_snapshots(module_path, problems):
    sn = load("snapshots", module_path)
    base = tempfile.mkdtemp(prefix="cleanup-mounts-", dir="/tmp")
    try:
        live = os.path.join(base, "live")
        snap = os.path.join(base, "snap")
        write(os.path.join(snap, "dir", "a.txt"), b"a")
        write(os.path.join(snap, "dir", "mnt", "b.txt"), b"b")
        write(os.path.join(snap, "dir", "sub", "c.txt"), b"c")
        write(os.path.join(live, "dir", "mnt", "live.txt"), b"live")
        mnt = os.path.join(live, "dir", "mnt")
        real_points = sn.mount_points if hasattr(sn, "mount_points") else None
        if real_points:
            sn.mount_points = lambda: real_points() | {mnt}
        entry = {"name": sn.PREFIX + "x", "path": snap, "mount": live}
        with Recorder([mnt], []) as rec:
            result = sn.do_restore(entry, "dir", False)
        for hit in sorted(set(rec.hits)):
            problems.append(f"snapshots.py restore touched {hit}")
        if not os.path.exists(os.path.join(live, "dir", "a.txt")) or not os.path.exists(os.path.join(live, "dir", "sub", "c.txt")):
            problems.append(f"snapshots.py restore: missing items not restored: {result}")
        if os.path.exists(os.path.join(mnt, "b.txt")):
            problems.append("snapshots.py restore: copied into the mount point")
        if real_points and "not_restored" not in result.get("still_missing", result.get("missing", {})) \
                and "not_restored" not in result.get("missing", {}):
            problems.append(f"snapshots.py restore: mount point not reported: {result}")
    finally:
        shutil.rmtree(base)


def check_fill_level(problems):
    """Each fill level row as df reports it for that mount point; no network, FUSE or memory file system."""
    a = load("analyze")
    rows = a.local_filesystems()
    if not rows:
        problems.append("fill level: no local file system found")
    for source, fstype, target in rows:
        done = subprocess.run(["df", "-B1", "--output=source,fstype,size,target", target],
                              capture_output=True, text=True, timeout=10)
        cols = done.stdout.splitlines()[-1].split(None, 3) if done.returncode == 0 else []
        st = os.statvfs(target)
        if cols[:2] != [source, fstype] or cols[3:] != [target] or int(cols[2]) != st.f_blocks * st.f_frsize:
            problems.append(f"fill level: {source} {fstype} {target} vs df {cols}")


def check_decoding(problems):
    d = load("delete")
    raw = "/home/u/Bücher\\040alt"
    if d.unescape_mount(raw) != "/home/u/Bücher alt":
        problems.append(f"mountinfo decoding: {d.unescape_mount(raw)!r}")
    points = d.mount_points()
    if "/" not in points or "/proc" not in points:
        problems.append("mount_points: / or /proc missing in the real mount list")


def check_stall(problems):
    d = load("delete")
    base = tempfile.mkdtemp(prefix="cleanup-stall-", dir="/tmp")
    slow = os.path.join(base, "a", "slow")
    write(os.path.join(slow, "f"))
    write(os.path.join(base, "b", "f"))
    d.WALK.stall_seconds = 0.2
    real_scandir = os.scandir

    def scandir(path):
        if path == slow:
            time.sleep(0.75)
        return real_scandir(path)
    err = io.StringIO()
    os.scandir = scandir
    try:
        with contextlib.redirect_stderr(err):
            d.tree_size(base)
            time.sleep(0.5)                 # no line may follow once the walk has finished
    finally:
        os.scandir = real_scandir
        shutil.rmtree(base)
    lines = err.getvalue().splitlines()
    still = [l for l in lines if l.startswith(f'delete.py: still in "{slow}" after ')]
    moved = [l for l in lines if l.startswith('delete.py: moved on after ')
             and (f'in "{slow}", now in "' in l or l.endswith(f'in "{slow}", walk finished'))]
    if len(still) < 2:
        problems.append(f"stall: expected at least two 'still in' lines, got {lines}")
    elif not still[0].endswith("(huge folder or unresponsive mount?)") or still[1].endswith("?)"):
        problems.append(f"stall: hint expected in the first line only: {still}")
    if len(moved) != 1 or lines[-1] != moved[0]:
        problems.append(f"stall: expected one 'moved on' line at the end, got {lines}")
    if len(d.WALK.stalls) != 1 or d.WALK.stalls[0]["folder"] != slow:
        problems.append(f"stall: report list {d.WALK.stalls}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete")
    parser.add_argument("--analyze")
    parser.add_argument("--journal")
    parser.add_argument("--backup")
    parser.add_argument("--snapshots")
    args = parser.parse_args()
    problems = []
    only = args.delete or args.analyze or args.journal or args.backup or args.snapshots
    if args.delete or not only:
        check_delete(args.delete, problems)
    if args.analyze or not only:
        check_analyze(args.analyze, problems)
    if args.journal or not only:
        check_journal(args.journal, problems)
    if args.backup or not only:
        check_backup(args.backup, problems)
    if args.snapshots or not only:
        check_snapshots(args.snapshots, problems)
    if not only:
        check_fill_level(problems)
        check_decoding(problems)
        check_stall(problems)
    if problems:
        print(f"FAILED ({len(problems)} deviations):")
        for line in problems:
            print("  " + line)
        return 1
    print("PASSED: no script touches simulated mount points or follows links; "
          "fill level against df; decoding; stall lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
