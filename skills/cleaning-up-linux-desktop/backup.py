"""Archive backups of files before they are deleted (concept.md, sections 3.2, 3.9, 3.10).

Commands: create, list, restore, remove. One backup step becomes one archive
file (tar, tar.gz or zip) in a folder per run:
    <target>/cleaning-up-linux-desktop-backup-<date>-<time>/NN-<step>.tar|.tar.gz|.zip
Before writing, the free space at the target is checked against the total size
plus a reserve. After writing, the archive is verified: by default compared with
the files (a second read), on request only a quick check. If anything fails,
nothing is left behind and the caller must not delete. Restoring copies back
only what is missing and overwrites nothing. Result as JSON, summary on stderr.

Mount points and links are never followed (concept.md, Grundsatz 8): a mount point inside a path is
left out and reported, a listed path that is a mount point or lies on a network or FUSE mount is
refused, and tar is given the exact entries instead of folders to walk itself. Restoring skips
members at a mount point or on a network or FUSE mount, before any access to them.

Usage (as root, to read everything and keep owners):
    backup.py create --list FILE --target DIR --step NAME [--format tar|tar.gz|zip] [--run NAME]
                     [--reserve-percent P] [--reserve-gib G] [--verify full|quick] [--dry-run]
    backup.py list --target DIR
    backup.py restore --target DIR --run NAME --step NAME [--path ABSOLUTE_PATH] [--dry-run]
    backup.py remove --target DIR --run NAME [--dry-run]
"""

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
import zlib
from datetime import datetime

PREFIX = "cleaning-up-linux-desktop-"
RUN_PREFIX = PREFIX + "backup-"
GIB = 1024**3
STEP = re.compile(r"[a-z0-9][a-z0-9-]{0,39}")
ARCHIVE = re.compile(r"(\d{2,})-([a-z0-9][a-z0-9-]*)\.(tar\.gz|tar|zip)")
STORE_EXTENSIONS = set(
    "mp4 mkv avi mov wmv flv webm m4v mpg mpeg ts mts m2ts 3gp vob "
    "mp3 flac wav ogg oga opus m4a aac wma aiff "
    "jpg jpeg png gif bmp tif tiff webp heic heif raw cr2 nef arw dng "
    "zip tar gz tgz xz bz2 7z rar zst lz4 img iso qcow2 vdi vmdk vhd vhdx deb".split())
ZIP_LEVEL = 3
ENTRY_OVERHEAD = 2048      # per file, folder or link: tar blocks and headers (measured: 1.8 KiB), zip headers
TAR_GZIP = "gzip -1"
MODE_FILE, MODE_DIR = 0o600, 0o700


def run(cmd, timeout=None):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return None, "", str(exc)
    return done.returncode, done.stdout, done.stderr


def is_own(name):
    return name.lstrip(".").startswith(PREFIX)


def inside(path, base):
    return path == base or path.startswith(base.rstrip(os.sep) + os.sep)


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


WALK = Walker("backup.py")
SAFE_FS = {"zfs", "tmpfs", "ramfs", "devtmpfs", "overlay"}      # memory or local block devices cannot hang


def mount_kinds():
    """{mount point: (fstype, source)} from /proc/self/mountinfo."""
    kinds = {}
    try:
        with open("/proc/self/mountinfo", encoding="utf-8", errors="surrogateescape") as fh:
            for line in fh:
                left, sep, right = line.partition(" - ")
                fields, rest = left.split(), right.split()
                if sep and len(fields) > 4 and len(rest) > 1:
                    kinds[unescape_mount(fields[4])] = (rest[0], unescape_mount(rest[1]))
    except OSError:
        pass
    return kinds


def mount_problem(path):
    """Why path must not be touched because of mounts (decided by name, before any access), or None:
    it is a mount point, or lies on a mount that is neither a local block device nor memory."""
    if path != "/" and path in mount_kinds():
        return "is a mount point"
    kinds = mount_kinds()
    target = path.rstrip(os.sep) + os.sep
    point = max((m for m in kinds if target.startswith(m.rstrip(os.sep) + os.sep)), key=len, default=None)
    if point is not None:
        fstype, source = kinds[point]
        if not (source.startswith("/dev/") or fstype in SAFE_FS):
            return "lies on a mount that is not a local file system"
    return None


def adopt(path, target):
    """When running as root, give the new file the owner of the target folder."""
    if os.geteuid() == 0:
        st = os.stat(target)
        os.chown(path, st.st_uid, st.st_gid)


# --- the paths and the plan ----------------------------------------------------------------------

def load_paths(file):
    with open(file, encoding="utf-8") as fh:
        data = json.load(fh)
    # a plain list, {"paths": [...]}, or the report of delete.py --with-paths ("candidates")
    return data.get("paths", data.get("candidates")) if isinstance(data, dict) else data


def validate(paths, target):
    """Clean list of absolute paths and the reasons for refusals."""
    errors, clean = [], []
    target_real = os.path.realpath(target)
    for p in paths:
        if not isinstance(p, str) or not os.path.isabs(p) or os.path.normpath(p) != p or p == "/":
            errors.append({"path": p, "reason": "not a clean absolute path"})
        elif any(is_own(part) for part in p.split(os.sep) if part):
            errors.append({"path": p, "reason": "own snapshot or archive (prefix)"})
        elif mount_problem(p):
            errors.append({"path": p, "reason": mount_problem(p)})
        elif not os.path.lexists(p):
            errors.append({"path": p, "reason": "does not exist"})
        elif inside(target_real, os.path.join(os.path.realpath(os.path.dirname(p)), os.path.basename(p))):
            errors.append({"path": p, "reason": "the target folder lies inside this path"})
        else:
            clean.append(p)
    clean.sort()
    deduped = []
    for p in clean:
        if not any(inside(p, q) for q in deduped):
            deduped.append(p)
    return deduped, errors


def walk_entries(paths):
    """(path, kind, size) of everything below the paths; kind file, dir, link or special. Skipped: [(path, why)].
    Mount points and other file systems are left out (by name, before any access) and reported."""
    entries, skipped = [], []

    def one(path):
        st = os.lstat(path)
        if stat.S_ISLNK(st.st_mode):
            entries.append((path, "link", 0))
        elif stat.S_ISREG(st.st_mode):
            entries.append((path, "file", st.st_size))
        elif stat.S_ISDIR(st.st_mode):
            entries.append((path, "dir", 0))
        else:
            entries.append((path, "special", 0))
            skipped.append((path, "special file"))

    for top in paths:
        st = os.lstat(top)
        one(top)
        if not stat.S_ISDIR(st.st_mode):
            continue
        left_out = []
        for folder, dirs, files in WALK.walk(top, left_out):
            dirs[:] = sorted(dirs)
            for d in dirs:
                entries.append((os.path.join(folder, d), "dir", 0))
            for f in sorted(files):
                one(os.path.join(folder, f))
        skipped += [(p, "mount point or other file system") for p, why in left_out
                    if why in ("mount point", "other file system")]
    return entries, skipped


def summarize(entries, skipped):
    kinds = {k: sum(1 for _, kind, _ in entries if kind == k) for k in ("file", "dir", "link", "special")}
    return {"files": kinds["file"], "dirs": kinds["dir"], "links": kinds["link"], "bytes": sum(s for _, _, s in entries),
            "skipped": [{"path": p, "reason": r} for p, r in skipped[:50]], "skipped_count": len(skipped)}


def space_check(size, avail, required, percent=None, gib=None):
    """Reserve: default the larger of 10 % and 10 GiB; the user may lower it, never below the larger of 5 % and 5 GiB."""
    wanted = max((10 if percent is None else percent) / 100 * size, (10 if gib is None else gib) * GIB)
    floor = max(0.05 * size, 5 * GIB)
    reserve = max(wanted, floor)
    return {"size": size, "avail": avail, "required": required, "reserve": int(reserve), "floor": int(floor),
            "clamped": wanted < floor, "ok": avail - required >= reserve}


def free_space(target):
    st = os.statvfs(target)
    return st.f_blocks * st.f_frsize, st.f_bavail * st.f_frsize


# --- writing -------------------------------------------------------------------------------------

def next_number(run_dir):
    numbers = [int(m.group(1)) for n in (os.listdir(run_dir) if os.path.isdir(run_dir) else [])
               if (m := ARCHIVE.fullmatch(n))]
    return max(numbers, default=0) + 1


def tar_base():
    return ["tar", "--format=pax", "--acls", "--xattrs", "--numeric-owner"]


def write_tar(part, entries, gz):
    """tar gets every entry by name and does not walk: its own walk would stat the mount points."""
    with tempfile.NamedTemporaryFile("wb", delete=False) as fh:
        fh.write(b"\0".join(p.lstrip("/").encode(errors="surrogateescape") for p, _, _ in entries) + b"\0")
        listing = fh.name
    try:
        cmd = tar_base() + ["--create", "--sparse", "--no-recursion", "-C", "/", "--null", "--files-from=" + listing,
                            "-f", part] + ([f"--use-compress-program={TAR_GZIP}"] if gz else [])
        code, out, err = run(cmd)
    finally:
        os.unlink(listing)
    return code == 0, err.strip()


def store_it(path):
    return path.rsplit(".", 1)[-1].lower() in STORE_EXTENSIONS if "." in os.path.basename(path) else False


def write_zip(part, entries, number, step):
    root = f"{number:02d}-{step}"
    with zipfile.ZipFile(part, "w", allowZip64=True, strict_timestamps=False) as zf:
        for path, kind, _ in entries:
            arc = f"{root}/{path.lstrip('/')}"
            st = os.lstat(path)
            if kind == "dir":
                info = zipfile.ZipInfo.from_file(path, arc + "/", strict_timestamps=False)
                info.external_attr = (stat.S_IFDIR | stat.S_IMODE(st.st_mode)) << 16 | 0x10
                zf.writestr(info, b"")
            elif kind == "link":
                info = zipfile.ZipInfo(arc, date_time=datetime.fromtimestamp(max(st.st_mtime, 315532800)).timetuple()[:6])
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                zf.writestr(info, os.readlink(path), compress_type=zipfile.ZIP_STORED)
            elif kind == "file":
                zf.write(path, arc, compress_type=zipfile.ZIP_STORED if store_it(path) else zipfile.ZIP_DEFLATED,
                         compresslevel=ZIP_LEVEL)
    return True, ""


def file_crc(path):
    crc = 0
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            crc = zlib.crc32(block, crc)
    return crc & 0xFFFFFFFF


def verify_tar(archive, entries, mode, gz):
    flags = ["--gzip"] if gz else []
    if mode == "quick":
        code, out, err = run(["tar", "--list", "-f", archive] + flags)
        count = len(out.splitlines())
        needed = sum(1 for _, k, _ in entries if k in ("file", "link"))
        ok = code == 0 and count >= needed
        return {"mode": mode, "ok": ok, "entries": count, "details": [] if ok else [err.strip() or f"{count} entries, {needed} expected"]}
    code, out, err = run(["tar", "--diff", "--numeric-owner", "-f", archive, "-C", "/"] + flags)
    lines = (out + err).strip().splitlines()
    return {"mode": mode, "ok": code == 0, "details": lines[:20], "difference_lines": len(lines)}


def verify_zip(archive, entries, mode, number, step):
    problems = []
    root = f"{number:02d}-{step}"
    with zipfile.ZipFile(archive) as zf:
        bad = zf.testzip()
        if bad:
            problems.append(f"damaged member: {bad}")
        names = set(zf.namelist())
        for path, kind, size in entries:
            arc = f"{root}/{path.lstrip('/')}" + ("/" if kind == "dir" else "")
            if kind != "special" and arc not in names:
                problems.append(f"missing in the archive: {path}")
            elif mode == "full" and kind == "file":
                info = zf.getinfo(arc)
                try:
                    if info.file_size != os.lstat(path).st_size or info.CRC != file_crc(path):
                        problems.append(f"differs from the file: {path}")
                except OSError as exc:
                    problems.append(f"unreadable: {path} ({exc.strerror})")
            elif mode == "full" and kind == "link" and zf.read(arc).decode() != os.readlink(path):
                problems.append(f"link target differs: {path}")
            if len(problems) >= 20:
                break
    return {"mode": mode, "ok": not problems, "details": problems}


def do_create(args):
    target = os.path.realpath(args.target)
    if not os.path.isdir(target) or not os.access(target, os.W_OK | os.X_OK):
        return {"ok": False, "error": f"target is not a writable folder: {args.target}"}
    if not STEP.fullmatch(args.step):
        return {"ok": False, "error": "step: lowercase letters, digits and '-', 1 to 40 characters"}
    try:
        paths = load_paths(args.list)
    except (OSError, ValueError, KeyError) as exc:
        return {"ok": False, "error": f"cannot read the list: {exc}"}
    clean, errors = validate(paths, target)
    if errors:
        return {"ok": False, "error": "refused paths in the list", "refused": errors}
    entries, skipped = walk_entries(clean)
    unreadable = [p for p, why in skipped if why == "unreadable"]
    if unreadable:
        return {"ok": False, "error": "unreadable folders; nothing would be backed up there", "unreadable": unreadable[:20]}
    plan = summarize(entries, skipped)
    plan["stalls"] = WALK.stalls
    plan["overhead_estimate"] = ENTRY_OVERHEAD * (plan["files"] + plan["dirs"] + plan["links"])
    size, avail = free_space(target)
    space = space_check(size, avail, plan["bytes"] + plan["overhead_estimate"], args.reserve_percent, args.reserve_gib)
    run_name = args.run or f"{RUN_PREFIX}{datetime.now():%Y%m%d-%H%M%S}"
    if not run_name.startswith(RUN_PREFIX) or os.sep in run_name:
        return {"ok": False, "error": f"the run name must start with {RUN_PREFIX}"}
    run_dir = os.path.join(target, run_name)
    number = next_number(run_dir)
    ext = {"tar": ".tar", "tar.gz": ".tar.gz", "zip": ".zip"}[args.format]
    archive = os.path.join(run_dir, f"{number:02d}-{args.step}{ext}")
    result = {"ok": space["ok"], "dry_run": args.dry_run, "run": run_name, "step": args.step, "number": number,
              "archive": archive, "format": args.format, "plan": plan, "space": space}
    if not space["ok"]:
        result["error"] = "not enough free space at the target for the data plus the reserve"
        return result
    if args.dry_run:
        return result
    os.makedirs(run_dir, mode=MODE_DIR, exist_ok=True)
    adopt(run_dir, target)
    part = archive + ".part"
    try:
        if args.format == "zip":
            ok, err = write_zip(part, entries, number, args.step)
        else:
            ok, err = write_tar(part, entries, args.format == "tar.gz")
        if not ok:
            raise RuntimeError(err or "writing the archive failed")
        if args.format == "zip":
            verify = verify_zip(part, entries, args.verify, number, args.step)
        else:
            verify = verify_tar(part, entries, args.verify, args.format == "tar.gz")
        result["verify"] = verify
        if not verify["ok"]:
            raise RuntimeError("verification failed")
        os.chmod(part, MODE_FILE)
        adopt(part, target)
        os.replace(part, archive)
    except (RuntimeError, OSError, zipfile.BadZipFile) as exc:
        if os.path.exists(part):
            os.unlink(part)
        result.update({"ok": False, "error": str(exc) or type(exc).__name__})
        return result
    result["bytes_written"] = os.path.getsize(archive)
    return result


# --- list, restore, remove -----------------------------------------------------------------------

def find_archive(target, run, step):
    run_dir = os.path.join(os.path.realpath(target), run)
    if not run.startswith(RUN_PREFIX) or os.sep in run or not os.path.isdir(run_dir) or os.path.islink(run_dir):
        return None, f"not a run of the skill: {run}"
    hits = [n for n in os.listdir(run_dir) if (m := ARCHIVE.fullmatch(n)) and m.group(2) == step]
    if len(hits) != 1:
        return None, f"expected exactly one archive for the step '{step}', found {len(hits)}"
    return os.path.join(run_dir, hits[0]), None


def do_list(args):
    target = os.path.realpath(args.target)
    runs = []
    for name in sorted(os.listdir(target)) if os.path.isdir(target) else []:
        path = os.path.join(target, name)
        if not name.startswith(RUN_PREFIX) or not os.path.isdir(path) or os.path.islink(path):
            continue
        steps = []
        for n in sorted(os.listdir(path)):
            m = ARCHIVE.fullmatch(n)
            if m:
                st = os.stat(os.path.join(path, n))
                steps.append({"file": n, "step": m.group(2), "format": m.group(3), "bytes": st.st_size,
                              "created": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")})
        runs.append({"run": name, "steps": steps, "bytes": sum(s["bytes"] for s in steps)})
    return {"ok": True, "target": target, "runs": runs}


def tar_members(archive, gz):
    code, out, err = run(["tar", "--list", "-f", archive] + (["--gzip"] if gz else []))
    return (out.splitlines() if code == 0 else None), err.strip()


def do_restore(args):
    archive, error = find_archive(args.target, args.run, args.step)
    if error:
        return {"ok": False, "error": error}
    only = None
    if args.path:
        only = os.path.normpath(args.path)
        if not os.path.isabs(only) or only == "/" or any(is_own(p) for p in only.split(os.sep) if p):
            return {"ok": False, "error": "--path: an absolute path of the original, not '/' and not an own folder"}
    fmt = ARCHIVE.fullmatch(os.path.basename(archive)).group(3)
    result = {"ok": True, "dry_run": args.dry_run, "archive": archive, "path": only}
    if fmt == "zip":
        return restore_zip(archive, args.step, only, args.dry_run, args.target, result)
    gz = fmt == "tar.gz"
    members, err = tar_members(archive, gz)
    if members is None:
        return {"ok": False, "error": f"cannot read the archive: {err}"}
    wanted = [m for m in members if only is None or inside("/" + m.rstrip("/"), only)]
    wanted, excluded = split_mounted(wanted, lambda m: "/" + m.rstrip("/"))
    missing = [m for m in wanted if not os.path.lexists("/" + m.rstrip("/"))]
    result["missing"] = {"items": len(missing), "examples": missing[:10]}
    if excluded:
        result["not_restored"] = excluded
    if args.dry_run or not missing:
        return result
    with tempfile.NamedTemporaryFile("wb", delete=False) as fh:
        fh.write(b"\0".join(m.encode(errors="surrogateescape") for m in missing) + b"\0")
        listing = fh.name
    try:       # exactly the missing members: tar neither walks nor looks at anything else
        cmd = tar_base() + ["--extract", "--skip-old-files", "--no-recursion", "-C", "/", "-f", archive,
                            "--null", "--files-from=" + listing] + (["--gzip"] if gz else [])
        code, out, err = run(cmd)
    finally:
        os.unlink(listing)
    result["command"] = " ".join(cmd)
    if code != 0:
        result.update({"ok": False, "error": f"tar failed: {err.strip()}"})
        return result
    left = [m for m in wanted if not os.path.lexists("/" + m.rstrip("/"))]
    result["still_missing"] = len(left)
    result["ok"] = not left
    return result


def split_mounted(items, path_of):
    """(restorable items, [{"path", "reason"}]): items at a mount point or on a network or FUSE mount are
    decided by name and never looked at (a folder in the archive may be a mount point by now)."""
    keep, excluded = [], []
    for item in items:
        reason = mount_problem(path_of(item))
        if reason:
            excluded.append({"path": path_of(item), "reason": reason})
        else:
            keep.append(item)
    return keep, excluded


def restore_zip(archive, step, only, dry_run, target, result):
    try:
        zf = zipfile.ZipFile(archive)
    except (OSError, zipfile.BadZipFile) as exc:
        return {"ok": False, "error": f"cannot read the archive: {exc}"}
    with zf:
        root = ARCHIVE.fullmatch(os.path.basename(archive)).group(1) + "-" + step
        items = []
        for info in zf.infolist():
            if not info.filename.startswith(root + "/"):
                continue
            orig = "/" + info.filename[len(root) + 1:].rstrip("/")
            if only is None or inside(orig, only):
                items.append((info, orig))
        items, excluded = split_mounted(items, lambda item: item[1])
        missing = [(i, o) for i, o in items if not os.path.lexists(o)]
        result["missing"] = {"items": len(missing), "examples": [o for _, o in missing[:10]]}
        if excluded:
            result["not_restored"] = excluded
        if dry_run or not missing:
            return result
        for info, orig in missing:
            if os.path.lexists(orig):
                continue
            parent = os.path.dirname(orig)
            made = []
            while not os.path.lexists(parent):
                made.append(parent)
                parent = os.path.dirname(parent)
            owner = os.stat(parent)
            for d in reversed(made):
                os.mkdir(d)
                if os.geteuid() == 0:
                    os.chown(d, owner.st_uid, owner.st_gid)
            mode = (info.external_attr >> 16) & 0xFFFF
            if info.is_dir():
                os.mkdir(orig)
            elif stat.S_ISLNK(mode):
                os.symlink(zf.read(info).decode(), orig)
            else:
                fd = os.open(orig, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as out, zf.open(info) as src:
                    for block in iter(lambda: src.read(1 << 20), b""):
                        out.write(block)
            if not stat.S_ISLNK(mode):
                os.chmod(orig, stat.S_IMODE(mode) or 0o644)
                stamp = datetime(*info.date_time).timestamp()
                os.utime(orig, (stamp, stamp))
            if os.geteuid() == 0:
                os.lchown(orig, owner.st_uid, owner.st_gid)
        left = [o for _, o in missing if not os.path.lexists(o)]
        result["still_missing"] = len(left)
        result["ok"] = not left
        return result


def do_remove(args):
    target = os.path.realpath(args.target)
    run_dir = os.path.join(target, args.run)
    if not args.run.startswith(RUN_PREFIX) or os.sep in args.run or not os.path.isdir(run_dir) or os.path.islink(run_dir):
        return {"ok": False, "error": f"not a run of the skill: {args.run}"}
    names = os.listdir(run_dir)
    strange = [n for n in names if not ARCHIVE.fullmatch(n) and not n.endswith(".part")]
    if strange:
        return {"ok": False, "error": "unexpected content in the run folder, nothing removed", "unexpected": strange}
    total = sum(os.path.getsize(os.path.join(run_dir, n)) for n in names)
    result = {"ok": True, "dry_run": args.dry_run, "run": args.run, "files": len(names), "bytes": total}
    if not args.dry_run:
        for n in names:
            os.unlink(os.path.join(run_dir, n))
        os.rmdir(run_dir)
        result["removed"] = not os.path.exists(run_dir)
        result["ok"] = result["removed"]
    return result


def emit(command, data, report):
    target = report or f"/tmp/cleanup-backup-{command}.json"
    tmp = target + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o644)
    os.replace(tmp, target)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--target", required=True)
    common.add_argument("--report")
    p = sub.add_parser("create", parents=[common])
    p.add_argument("--list", required=True)
    p.add_argument("--step", required=True)
    p.add_argument("--format", choices=("tar", "tar.gz", "zip"), default="tar")
    p.add_argument("--run")
    p.add_argument("--reserve-percent", type=float)
    p.add_argument("--reserve-gib", type=float)
    p.add_argument("--verify", choices=("full", "quick"), default="full")
    p.add_argument("--dry-run", action="store_true")
    sub.add_parser("list", parents=[common])
    p = sub.add_parser("restore", parents=[common])
    p.add_argument("--run", required=True)
    p.add_argument("--step", required=True)
    p.add_argument("--path")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("remove", parents=[common])
    p.add_argument("--run", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if os.geteuid() != 0:
        print("Warning: not running as root; some files may be unreadable and owners are not kept.", file=sys.stderr)
    data = {"create": do_create, "list": do_list, "restore": do_restore, "remove": do_remove}[args.command](args)
    target = emit(args.command, data, args.report)
    summary = data.get("error") or ("ok" if args.command != "list" else f"{len(data['runs'])} runs")
    print(f"{args.command}: {'ok' if data.get('ok') else 'FAILED'} - {summary}. Report: {target}", file=sys.stderr)
    return 0 if data.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
