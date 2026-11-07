"""Own btrfs snapshots of the cleaning-up-linux-desktop skill (concept.md, sections 3.2, 3.9, 3.10).

Commands: list, create, remove, restore. Only btrfs. Every snapshot this
script creates is read-only and carries the name prefix of the skill; the
script refuses to remove or restore from anything without that prefix.
Restoring copies back only what is missing and overwrites nothing; it copies each missing item
on its own and never looks at a target that lies at or below a mount point other than the one
restored (Grundsatz 8), because cp would descend into existing folders and a mount point inside
the live tree may be unresponsive.
With --dry-run nothing is changed; the report shows what would happen.
The result is written as JSON, a short summary goes to stderr.

Usage (run as root):
    snapshots.py list [--base-dir DIR ...]
    snapshots.py create --mount MOUNTPOINT --label LABEL [--base-dir DIR] [--dry-run]
    snapshots.py remove --name NAME_OR_PATH [--base-dir DIR ...] [--dry-run]
    snapshots.py restore --snapshot NAME_OR_PATH --path RELATIVE_PATH [--base-dir DIR ...] [--dry-run]
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
from datetime import datetime

PREFIX = "cleaning-up-linux-desktop-"
BASE_NAME = ".cleaning-up-linux-desktop-snapshots"     # default container folder below each mount point
LABEL = re.compile(r"[a-z0-9][a-z0-9-]{0,39}")
TIMEOUT = 120


def run(cmd, timeout=TIMEOUT):
    """Run a command; (returncode, stdout, stderr), returncode None if it could not run."""
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return None, "", str(exc)
    return done.returncode, done.stdout, done.stderr


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


WALK = Walker("snapshots.py")


def blocked(path, base):
    """True if path is or lies below a mount point other than base, decided by name."""
    return any(m != base and m.startswith(base.rstrip(os.sep) + os.sep)
               and (path == m or path.startswith(m.rstrip(os.sep) + os.sep)) for m in WALK.mounts(fresh=True))


def unescape(text):
    return re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), text)


def parse_mountinfo(lines):
    """btrfs mounts from /proc/self/mountinfo: mount point, device, subvolume path of the mount."""
    mounts = []
    for line in lines:
        left, sep, right = line.partition(" - ")
        fields, rest = left.split(), right.split()
        if not sep or len(fields) < 5 or len(rest) < 2 or rest[0] != "btrfs":
            continue
        mounts.append({"mount": unescape(fields[4]), "device": rest[1], "subvolume": unescape(fields[3])})
    return mounts


def btrfs_mounts():
    try:
        with open("/proc/self/mountinfo", encoding="utf-8") as fh:
            return parse_mountinfo(fh)
    except OSError:
        return []


def parse_show(text):
    """Fields of 'btrfs subvolume show'."""
    fields = {}
    for line in text.splitlines():
        key, _, value = line.strip().partition(":")
        fields.setdefault(key, value.strip())
    return {"id": fields.get("Subvolume ID"), "created": fields.get("Creation time"),
            "readonly": "readonly" in (fields.get("Flags") or "")}


def parse_qgroups(text):
    """Exclusive bytes per subvolume id from 'btrfs qgroup show --raw'."""
    excl = {}
    for line in text.splitlines():
        cols = line.split()
        if len(cols) >= 3 and cols[0].startswith("0/") and cols[2].isdigit():
            excl[cols[0][2:]] = int(cols[2])
    return excl


def inside(path, base):
    return path == base or path.startswith(base.rstrip(os.sep) + os.sep)


def mount_of(path, mounts):
    """The btrfs mount point the path lies below (the deepest one)."""
    best = None
    for m in mounts:
        if inside(path, m["mount"]) and (best is None or len(m["mount"]) > len(best["mount"])):
            best = m
    return best


def default_dirs(mounts, extra):
    dirs = []
    for m in mounts:
        dirs.append((m, os.path.join(m["mount"], BASE_NAME)))
    for d in extra:
        m = mount_of(os.path.realpath(d), mounts)
        if m:
            dirs.append((m, os.path.realpath(d)))
    return dirs


def list_snapshots(mounts, extra_dirs=()):
    """Own snapshots (prefix) found in the default container folders and the extra folders."""
    found, seen = [], set()
    excl_by_mount = {}
    for m, folder in default_dirs(mounts, extra_dirs):
        try:
            entries = sorted(os.scandir(folder), key=lambda e: e.name)
        except OSError:
            continue
        for e in entries:
            if not e.name.startswith(PREFIX) or not e.is_dir(follow_symlinks=False) or e.path in seen:
                continue
            code, out, _ = run(["btrfs", "subvolume", "show", e.path])
            if code != 0:
                continue
            info = parse_show(out)
            if m["mount"] not in excl_by_mount:
                code, out, _ = run(["btrfs", "qgroup", "show", "--raw", m["mount"]])
                excl_by_mount[m["mount"]] = parse_qgroups(out) if code == 0 else None
            excl = excl_by_mount[m["mount"]]
            seen.add(e.path)
            found.append({"name": e.name, "path": e.path, "mount": m["mount"], "device": m["device"],
                          "subvolume_id": info["id"], "created": info["created"], "readonly": info["readonly"],
                          "exclusive_bytes": None if excl is None else excl.get(info["id"])})
    return found


def find_snapshot(arg, mounts, extra_dirs):
    """Resolve a name or path to one of the own snapshots; (entry, error)."""
    extra = list(extra_dirs)
    if os.sep in arg:
        arg = os.path.realpath(arg)
        extra.append(os.path.dirname(arg))
    name = os.path.basename(arg)
    if not name.startswith(PREFIX):
        return None, f"refused: '{name}' does not carry the prefix {PREFIX}"
    hits = [s for s in list_snapshots(mounts, extra) if s["name"] == name
            and (os.sep not in arg or s["path"] == arg)]
    if not hits:
        return None, f"not found among the own snapshots: {name}"
    if len(hits) > 1:
        return None, f"ambiguous: {name} exists in several places, give the full path"
    return hits[0], None


def make_name(label, now=None):
    if not LABEL.fullmatch(label):
        raise ValueError("label: lowercase letters, digits and '-', 1 to 40 characters, not starting with '-'")
    return f"{PREFIX}{(now or datetime.now()):%Y%m%d-%H%M%S}-{label}"


def do_create(mounts, mount, label, base_dir, dry_run, now=None):
    mount = os.path.realpath(mount)
    m = next((x for x in mounts if x["mount"] == mount), None)
    if m is None:
        return {"ok": False, "error": f"not a btrfs mount point: {mount}"}
    code, out, err = run(["btrfs", "subvolume", "show", mount])
    if code != 0:
        return {"ok": False, "error": f"no subvolume at {mount}: {err.strip() or 'btrfs failed'}"}
    try:
        name = make_name(label, now)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    base = os.path.realpath(base_dir) if base_dir else os.path.join(mount, BASE_NAME)
    if not inside(base, mount):
        return {"ok": False, "error": f"the folder for the snapshots must lie below {mount}"}
    dest = os.path.join(base, name)
    if os.path.lexists(dest):
        return {"ok": False, "error": f"exists already: {dest}"}
    cmd = ["btrfs", "subvolume", "snapshot", "-r", mount, dest]
    result = {"ok": True, "dry_run": dry_run, "name": name, "path": dest, "mount": mount,
              "device": m["device"], "command": " ".join(cmd)}
    if dry_run:
        return result
    os.makedirs(base, mode=0o700, exist_ok=True)
    code, out, err = run(cmd)
    if code != 0:
        return {"ok": False, "error": f"btrfs failed: {err.strip()}", "command": result["command"]}
    code, out, _ = run(["btrfs", "subvolume", "show", dest])
    info = parse_show(out) if code == 0 else {}
    result.update({"readonly": info.get("readonly"), "subvolume_id": info.get("id"), "created": info.get("created")})
    result["ok"] = bool(info) and bool(info.get("readonly"))
    if not result["ok"]:
        result["error"] = "the snapshot was created but could not be verified as a read-only subvolume"
    return result


def do_remove(mounts, arg, extra_dirs, dry_run):
    entry, error = find_snapshot(arg, mounts, extra_dirs)
    if error:
        return {"ok": False, "error": error}
    cmd = ["btrfs", "subvolume", "delete", "--commit-after", entry["path"]]
    container = os.path.dirname(entry["path"])
    own_container = os.path.basename(container) == BASE_NAME
    result = {"ok": True, "dry_run": dry_run, "name": entry["name"], "path": entry["path"],
              "mount": entry["mount"], "command": " ".join(cmd)}
    if dry_run:
        if own_container:
            result["container_removed"] = not [n for n in os.listdir(container) if n != entry["name"]]
        return result
    code, out, err = run(cmd)
    if code != 0:
        return {"ok": False, "error": f"btrfs failed: {err.strip()}", "command": result["command"]}
    result["removed"] = not os.path.lexists(entry["path"])
    result["ok"] = result["removed"]
    # the container folder belongs to the skill: it goes with its last snapshot
    result["container_removed"] = False
    if result["removed"] and own_container:
        try:
            os.rmdir(container)
            result["container_removed"] = True
        except OSError:
            pass
    return result


def clean_relative(path):
    """A relative path inside the snapshot, or None if it is empty, absolute or climbs out."""
    norm = os.path.normpath(path)
    if not path or os.path.isabs(path) or norm in (".", "") or norm == ".." or norm.startswith(".." + os.sep):
        return None
    return norm


def missing_items(src, dst, base):
    """What of src is missing in dst: ([(relative path, bytes)], [(relative path, reason)]). A missing folder
    counts as one item. Targets at or below a mount point other than base are left out, by name, unseen."""
    def size_of(path):
        total = 0
        for folder, _, files in WALK.walk(path):
            for f in files:
                try:
                    total += os.lstat(os.path.join(folder, f)).st_size
                except OSError:
                    pass
        return total
    if blocked(dst, base):
        return [], [(".", "target lies on another mount")]
    if not os.path.isdir(src) or os.path.islink(src):
        return ([(".", os.lstat(src).st_size)] if not os.path.lexists(dst) else []), []
    items, left_out = [], []
    for folder, dirs, files in WALK.walk(src):
        rel = os.path.relpath(folder, src)
        target = dst if rel == "." else os.path.join(dst, rel)
        if blocked(target, base):
            left_out.append((rel, "target lies on another mount"))
            dirs[:] = []
            continue
        if not os.path.lexists(target):
            items.append((rel, size_of(folder)))
            dirs[:] = []
            continue
        for f in files:
            name = os.path.normpath(os.path.join(rel, f))
            if blocked(os.path.join(target, f), base):
                left_out.append((name, "target lies on another mount"))
            elif not os.path.lexists(os.path.join(target, f)):
                items.append((name, os.lstat(os.path.join(folder, f)).st_size))
        kept = []
        for d in dirs:
            if blocked(os.path.join(target, d), base):
                left_out.append((os.path.normpath(os.path.join(rel, d)), "target lies on another mount"))
            else:
                kept.append(d)
        dirs[:] = kept
    return items, left_out


def ensure_folder(src_root, dst_root, rel):
    """Create missing folders of rel below dst_root with owner, mode and times of their counterparts in src_root."""
    current_src, current_dst = src_root, dst_root
    for part in rel.split(os.sep):
        current_src = os.path.join(current_src, part)
        current_dst = os.path.join(current_dst, part)
        if os.path.lexists(current_dst):
            continue
        os.mkdir(current_dst)
        st = os.lstat(current_src)
        os.chown(current_dst, st.st_uid, st.st_gid)
        shutil.copystat(current_src, current_dst)


def restore_plan(items, left_out):
    plan = {"items": len(items), "bytes": sum(b for _, b in items), "examples": [r for r, _ in items[:10]]}
    if left_out:
        plan["not_restored"] = [{"path": p, "reason": why} for p, why in left_out[:50]]
    return plan


def do_restore(entry, rel, dry_run):
    """Copy back what is missing from the snapshot into the live tree; nothing is overwritten."""
    clean = clean_relative(rel)
    if clean is None:
        return {"ok": False, "error": "give a folder or file relative to the snapshot, not an empty path, '.' or '..'"}
    if any(part.startswith(PREFIX) or part == BASE_NAME for part in clean.split(os.sep)):
        return {"ok": False, "error": "refused: never restore from or into the skill's own snapshot folders"}
    src = os.path.join(entry["path"], clean)
    dst = os.path.join(entry["mount"], clean)
    if not os.path.lexists(src) or not inside(os.path.realpath(os.path.dirname(src)), entry["path"]):
        return {"ok": False, "error": f"not in the snapshot: {clean}"}
    items, left_out = missing_items(src, dst, entry["mount"])
    result = {"ok": True, "dry_run": dry_run, "snapshot": entry["name"], "path": clean, "source": src, "target": dst,
              "missing": restore_plan(items, left_out)}
    if dry_run or not items:
        return result
    commands = []
    try:
        for item, _ in items:           # each missing item on its own: cp never descends into an existing folder
            item_src = src if item == "." else os.path.join(src, item)
            item_dst = dst if item == "." else os.path.join(dst, item)
            parent = os.path.dirname(os.path.join(clean, item) if item != "." else clean)
            if parent:
                ensure_folder(entry["path"], entry["mount"], parent)
            cmd = ["cp", "-a", "--update=none", "--", item_src, item_dst]
            code, out, err = run(cmd)
            commands.append(" ".join(cmd))
            if code != 0:
                result.update({"ok": False, "error": f"cp failed: {err.strip()}", "command": commands[-1]})
                return result
    except OSError as exc:
        return {"ok": False, "error": f"could not prepare the target: {exc.strerror}"}
    result["command"] = commands[0] if len(commands) == 1 else f"{commands[0]} (and {len(commands) - 1} more)"
    result["items_copied"] = len(commands)
    left_items, left_blocked = missing_items(src, dst, entry["mount"])
    result["still_missing"] = restore_plan(left_items, left_blocked)
    result["ok"] = not left_items
    return result


def emit(command, data, report):
    target = report or f"/tmp/cleanup-snapshots-{command}.json"
    tmp = target + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o644)
    os.replace(tmp, target)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("list", "create", "remove", "restore"):
        p = sub.add_parser(name)
        p.add_argument("--report")
        if name != "create":
            p.add_argument("--base-dir", action="append", default=[], help="extra folder with own snapshots")
        if name != "list":
            p.add_argument("--dry-run", action="store_true")
    sub.choices["create"].add_argument("--mount", required=True)
    sub.choices["create"].add_argument("--label", required=True)
    sub.choices["create"].add_argument("--base-dir")
    sub.choices["remove"].add_argument("--name", required=True)
    sub.choices["restore"].add_argument("--snapshot", required=True)
    sub.choices["restore"].add_argument("--path", required=True)
    args = parser.parse_args(argv)

    if os.geteuid() != 0:
        print("Warning: not running as root; btrfs commands will fail.", file=sys.stderr)
    mounts = btrfs_mounts()
    if args.command == "list":
        data = {"ok": True, "prefix": PREFIX, "btrfs_mounts": mounts, "snapshots": list_snapshots(mounts, args.base_dir)}
    elif args.command == "create":
        data = do_create(mounts, args.mount, args.label, args.base_dir, args.dry_run)
    elif args.command == "remove":
        data = do_remove(mounts, args.name, args.base_dir, args.dry_run)
    else:
        entry, error = find_snapshot(args.snapshot, mounts, args.base_dir)
        data = {"ok": False, "error": error} if error else do_restore(entry, args.path, args.dry_run)
    target = emit(args.command, data, args.report)
    summary = data.get("error") or (f"{len(data['snapshots'])} own snapshots" if args.command == "list" else "ok")
    print(f"{args.command}: {'ok' if data.get('ok') else 'FAILED'} - {summary}. Report: {target}", file=sys.stderr)
    return 0 if data.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
