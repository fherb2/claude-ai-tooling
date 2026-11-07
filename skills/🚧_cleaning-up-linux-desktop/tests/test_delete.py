"""Simulated real run of delete.py: deletes for real, but only in a throwaway tree under /tmp.

Builds a fake home and a fake /var, redirects the system paths of delete.py
into it, replaces program commands (apt-get, journalctl, pip, docker) and
the process check by recorders, runs every rule and a list order without
--dry-run, and then checks file by file what is gone and what is kept.
Needs no root. Prints PASSED or the list of deviations.

Usage: python3 -I tests/test_delete.py
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DAY = 86400


def load_delete():
    spec = importlib.util.spec_from_file_location("delete", os.path.join(HERE, "..", "delete.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Fixture:
    """The throwaway tree and the expectation for every path in it."""

    def __init__(self, base, later):
        self.base, self.later = base, later
        self.home = os.path.join(base, "home", "user")
        self.var = os.path.join(base, "var")
        self.expect = {}          # path -> "gone" or "kept"

    def file(self, rel, expect, size=10, young=False, root=None, content=None):
        path = os.path.join(root or self.home, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(content if content is not None else b"\0" * size)
        if young:
            # one day old at the simulated time; the status change time cannot be set, so
            # the modification time is moved into the future relative to the real clock
            os.utime(path, (self.later - DAY, self.later - DAY))
        self.expect[path] = expect
        return path

    def folder(self, rel, expect, root=None):
        path = os.path.join(root or self.home, rel)
        os.makedirs(path, exist_ok=True)
        self.expect[path] = expect
        return path


def build(fx):
    h = fx.home
    # 4.2 Firefox (running): old entry gone, young kept, index kept, folders kept, stale remnant gone
    fx.file(".cache/mozilla/firefox/p.default/cache2/entries/OLD", "gone")
    fx.file(".cache/mozilla/firefox/p.default/cache2/entries/YOUNG", "kept", young=True)
    fx.file(".cache/mozilla/firefox/p.default/cache2/index", "kept")
    fx.folder(".cache/mozilla/firefox/p.default/cache2/entries", "kept")
    fx.folder(".cache/mozilla/firefox/p.default/cache2/doomed", "kept")
    fx.file(".cache/mozilla/firefox/p.default/startupCache/x", "kept")
    fx.file(".mozilla/firefox/p.default/startupCache/s", "gone")
    fx.file(".mozilla/firefox/p.default/cache2/c", "kept", young=True)
    fx.file(".mozilla/firefox/p.default/places.sqlite", "kept")
    # 4.3 Chrome (not running): old entries gone, young kept, index gone, other files kept
    fx.file(".cache/google-chrome/Default/Cache/Cache_Data/0123456789abcdef_0", "gone")
    fx.file(".cache/google-chrome/Default/Cache/Cache_Data/fedcba9876543210_0", "kept", young=True)
    fx.file(".cache/google-chrome/Default/Cache/Cache_Data/index", "gone")
    fx.file(".cache/google-chrome/Default/Cache/Cache_Data/index-dir/the-real-index", "gone")
    fx.file(".cache/google-chrome/Default/Cache/Cache_Data/notanentry", "kept")
    fx.file(".cache/google-chrome/Default/Code Cache/js/0123456789abcdef_0", "gone")
    fx.file(".cache/google-chrome/Default/Code Cache/wasm/0123456789abcdef_0", "kept")
    fx.folder(".cache/google-chrome/Default/Cache/Cache_Data", "kept")
    # 4.4 VS Code (running): old entry gone, index kept, old foreign CachedData gone, VSIX rules
    fx.file(".config/Code/Cache/Cache_Data/0123456789abcdef_0", "gone")
    fx.file(".config/Code/Cache/Cache_Data/index", "kept")
    fx.file(".config/Code/CachedData/installedcommit/f", "kept")
    fx.file(".config/Code/CachedData/oldcommit/f", "gone")
    fx.file(".config/Code/CachedData/youngcommit/f", "kept", young=True)
    fx.file(".config/Code/CachedExtensionVSIXs/.broken", "gone")
    fx.file(".config/Code/CachedExtensionVSIXs/.validzip", "kept", content=b"PK\x03\x04rest")
    fx.file(".config/Code/CachedExtensionVSIXs/.youngbroken", "kept", young=True)
    fx.file(".config/Code/CachedExtensionVSIXs/publisher.ext-1.0.0", "kept")
    fx.file(".config/Code/WebStorage/5/CacheStorage/data", "kept")
    fx.file(os.path.join(fx.base, "product.json"), "kept", content=b'{"commit": "installedcommit"}')
    # 4.5 logs: rotated and old gone; active, young, journal and unrelated files kept
    fx.file("syslog", "kept", root=fx.var + "/log")
    fx.file("syslog.1", "gone", root=fx.var + "/log")
    fx.file("syslog.2.gz", "gone", root=fx.var + "/log")
    fx.file("apt/history.log.3.gz", "gone", root=fx.var + "/log")
    fx.file("kern.log.1", "kept", young=True, root=fx.var + "/log")
    fx.file("journal/abc/system@x.journal~", "kept", root=fx.var + "/log")
    fx.file(".config/app/logs/app.log", "kept")
    fx.file(".config/app/logs/app.log.1", "gone")
    fx.file(".local/share/tool/run.log.old", "gone")
    fx.file(".config/app/settings.1", "kept")
    fx.file("Dokumente/report.log.1", "kept")
    # 4.12 __pycache__: every one in the home goes, with its folder; sources stay
    fx.file("proj/__pycache__/a.cpython-312.pyc", "gone")
    fx.folder("proj/__pycache__", "gone")
    fx.file("proj/.venv/lib/site/__pycache__/b.pyc", "gone")
    fx.file("proj/a.py", "kept")
    # 4.14 trash: old entry and info gone, young kept, orphan kept, link gone but its target kept
    trash = ".local/share/Trash"
    old_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(fx.later - 20 * DAY))
    young_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(fx.later - 2 * DAY))
    fx.file(f"{trash}/files/old.txt", "gone")
    fx.file(f"{trash}/info/old.txt.trashinfo", "gone",
            content=f"[Trash Info]\nPath=/x/old.txt\nDeletionDate={old_date}\n".encode())
    fx.file(f"{trash}/files/olddir/inner", "gone")
    fx.file(f"{trash}/info/olddir.trashinfo", "gone",
            content=f"[Trash Info]\nPath=/x/olddir\nDeletionDate={old_date}\n".encode())
    fx.file(f"{trash}/files/young.txt", "kept")
    fx.file(f"{trash}/info/young.txt.trashinfo", "kept",
            content=f"[Trash Info]\nPath=/x/young.txt\nDeletionDate={young_date}\n".encode())
    fx.file(f"{trash}/files/orphan", "kept")
    target = fx.file("Bilder/target.jpg", "kept")
    link = os.path.join(h, trash, "files/link")
    os.symlink(target, link)
    fx.expect[link] = "gone"
    fx.file(f"{trash}/info/link.trashinfo", "gone",
            content=f"[Trash Info]\nPath=/x/link\nDeletionDate={old_date}\n".encode())
    fx.file(f"{trash}/directorysizes", "kept", content=b"5 1 olddir\n7 2 keepme\n")
    # 4.9 list order: selected entries gone; ban, link and mount point keep theirs
    fx.file("Downloads/old.iso", "gone")
    fx.file("Downloads/folder/a", "gone")
    fx.file("Downloads/keep.txt", "kept")
    fx.file("Downloads/cleaning-up-linux-desktop-backup-x.tar", "kept")
    fx.file(".cleaning-up-linux-desktop-snapshots/snap/proj/__pycache__/x.pyc", "kept")
    os.symlink(os.path.join(h, "Downloads/keep.txt"), os.path.join(h, "Downloads/link"))
    fx.expect[os.path.join(h, "Downloads/link")] = "kept"
    fx.file("Downloads/mounted/data", "kept")
    fx.folder("Dokumente", "kept")


def check_trash_sizes(fx):
    with open(os.path.join(fx.home, ".local/share/Trash/directorysizes"), encoding="utf-8") as fh:
        return fh.read() == "7 2 keepme\n"


def main():
    d = load_delete()
    base = tempfile.mkdtemp(prefix="cleanup-test-", dir="/tmp")
    later = time.time() + 40 * DAY
    fx = Fixture(base, later)
    build(fx)
    home = fx.home

    # redirect the system paths and replace commands and the process check
    d.WALKED_ROOTS = [fx.var]
    d.APT_ARCHIVES = os.path.join(fx.var, "cache/apt/archives")
    d.LOG_DIR = os.path.join(fx.var, "log")
    d.JOURNAL_DIR = os.path.join(fx.var, "log/journal")
    d.VSCODE_PRODUCT = os.path.join(base, "product.json")
    d.running = lambda program: program in ("firefox", "code")
    d.owner = lambda path: "user"
    commands = []
    d.Deleter.command = lambda self, cmd, user=None: commands.append(((["runuser", "-u", user, "--"] if user else []) + cmd))
    d.docker_lines = lambda cmd: ({"in:use"} if "ps" in cmd else {"in:use", "keep:me", "drop:me", "<none>:<none>"})

    results, problems = {}, []
    for area, rule, params in [("4.2", d.rule_firefox, {}), ("4.3", d.rule_chrome, {}), ("4.4", d.rule_vscode, {}),
                               ("4.5", d.rule_logs, {"days": 14}), ("4.12", d.rule_pycache, {}),
                               ("4.14", d.rule_trash, {"days": 14}), ("4.1", d.rule_apt, {}),
                               ("4.6", d.rule_pip, {}),
                               ("4.13", d.rule_docker, {"containers": ["old_one"], "keep_images": ["keep:me"],
                                                        "builder_until_hours": 48})]:
        report = d.Report(area, False)
        deleter = d.Deleter(home, False, report)
        rule(deleter, home, params, later)
        results[area] = report.data

    report = d.Report("4.9", False)
    deleter = d.Deleter(home, False, report)
    deleter.guard.mounts.add(os.path.join(home, "Downloads/mounted"))
    for path in ["Downloads/old.iso", "Downloads/folder", "Downloads/link", "Downloads/mounted", "Dokumente", "",
                 "Downloads/cleaning-up-linux-desktop-backup-x.tar"]:
        deleter.remove(os.path.join(home, path) if path else home)
    for path in ["/boot/vmlinuz", "/etc/passwd"]:
        deleter.remove(path)
    results["4.9"] = report.data

    for path, expect in sorted(fx.expect.items()):
        present = os.path.lexists(path)
        if (expect == "gone") == present:
            problems.append(f"{'still there' if present else 'deleted'}: {os.path.relpath(path, base)} (expected {expect})")
    if not check_trash_sizes(fx):
        problems.append("trash directorysizes: line of the deleted entry not removed")
    expected_commands = [
        ["journalctl", "--vacuum-time=14d"], ["apt-get", "clean"],
        ["runuser", "-u", "user", "--", "python3", "-m", "pip", "cache", "purge"],
        ["docker", "rm", "-v", "old_one"], ["docker", "rmi", "drop:me"],
        ["docker", "builder", "prune", "--all", "--force", "--filter", "until=48h"]]
    for cmd in expected_commands:
        if cmd not in commands:
            problems.append(f"command not issued: {' '.join(cmd)}")
    for cmd in commands:
        if cmd not in expected_commands:
            problems.append(f"unexpected command: {' '.join(cmd)}")
    reasons = {s["path"]: s["reason"] for s in results["4.9"]["skipped"]}
    own = os.path.join(home, "Downloads/cleaning-up-linux-desktop-backup-x.tar")
    if reasons.get(own) != "own snapshot or archive (prefix)":
        problems.append(f"own archive not protected: {reasons.get(own)!r}")
    os.makedirs(os.path.join(home, "probe/__pycache__"))
    with open(os.path.join(home, "probe/__pycache__/a.pyc"), "w") as fh:
        fh.write("x")
    probe = d.Report("4.12", True, with_paths=True)
    d.rule_pycache(d.Deleter(home, True, probe), home, {}, later)
    wanted = {os.path.join(home, "probe/__pycache__")}
    if not wanted <= set(probe.data["candidates"]) or any(".cleaning-up-linux-desktop-snapshots" in c for c in probe.data["candidates"]):
        problems.append("with_paths: candidates missing or inside the own snapshot folder")
    if "candidates" in d.Report("4.12", True).data:
        problems.append("with_paths: candidates listed although not requested")
    for path, reason in [(os.path.join(home, "Downloads/link"), "symbolic link"),
                         (os.path.join(home, "Downloads/mounted"), "is or contains a mount point"),
                         (os.path.join(home, "Dokumente"), "folder directly under home"),
                         (home, "root or home itself or directly under /"),
                         ("/boot/vmlinuz", "under /boot"), ("/etc/passwd", "outside the analysed roots")]:
        if reasons.get(path) != reason:
            problems.append(f"ban: {path} -> {reasons.get(path)!r}, expected {reason!r}")
    orphan = os.path.join(home, ".local/share/Trash/files/orphan")
    if not any(s["path"] == orphan for s in results["4.14"]["skipped"]):
        problems.append("trash orphan was not reported")

    shutil.rmtree(base)
    if problems:
        print(f"FAILED ({len(problems)} deviations, {len(fx.expect)} paths checked):")
        for line in problems:
            print("  " + line)
        return 1
    print(f"PASSED: {len(fx.expect)} paths, {len(expected_commands)} commands, 6 bans, own-prefix protection and candidate paths checked.")
    for area, data in results.items():
        print(f"  {area:5} removed {data['removed_count']:3}  skipped {len(data['skipped'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
