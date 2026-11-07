"""Archive backups of files before they are deleted (concept.md, sections 3.2, 3.9, 3.10).

Commands: create, list, restore, remove. One backup step becomes one archive
file (tar, tar.gz or zip) in a folder per run:
    <target>/cleaning-up-linux-desktop-backup-<date>-<time>/NN-<step>.tar|.tar.gz|.zip
Before writing, the free space at the target is checked against the total size
plus a reserve. After writing, the archive is verified: by default compared with
the files (a second read), on request only a quick check. If anything fails,
nothing is left behind and the caller must not delete. Restoring copies back
only what is missing and overwrites nothing. Result as JSON, summary on stderr.

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


def mount_points():
    points = set()
    try:
        with open("/proc/self/mountinfo", encoding="utf-8") as fh:
            for line in fh:
                fields = line.split()
                if len(fields) > 4:
                    points.add(re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), fields[4]))
    except OSError:
        pass
    return points


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
        elif not os.path.lexists(p):
            errors.append({"path": p, "reason": "does not exist"})
        elif any(is_own(part) for part in p.split(os.sep) if part):
            errors.append({"path": p, "reason": "own snapshot or archive (prefix)"})
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


def walk_entries(paths, mounts):
    """(path, kind, size) of everything below the paths; kind file, dir, link or special. Skipped: [(path, why)]."""
    entries, skipped = [], []

    def one(path, top_dev):
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
        one(top, st.st_dev)
        if not stat.S_ISDIR(st.st_mode):
            continue
        for folder, dirs, files in os.walk(top, followlinks=False,
                                           onerror=lambda e: skipped.append((e.filename, "unreadable"))):
            keep = []
            for d in sorted(dirs):
                path = os.path.join(folder, d)
                if is_own(d):
                    continue
                if os.path.islink(path):
                    entries.append((path, "link", 0))
                elif path in mounts or os.lstat(path).st_dev != st.st_dev:
                    skipped.append((path, "mount point or other file system"))
                else:
                    entries.append((path, "dir", 0))
                    keep.append(d)
            dirs[:] = keep
            for f in sorted(files):
                if not is_own(f):
                    one(os.path.join(folder, f), st.st_dev)
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


def write_tar(part, paths, gz):
    with tempfile.NamedTemporaryFile("wb", delete=False) as fh:
        fh.write(b"\0".join(p.lstrip("/").encode() for p in paths) + b"\0")
        listing = fh.name
    try:
        cmd = tar_base() + ["--create", "--sparse", "--one-file-system", "-C", "/", "--null", "--files-from=" + listing,
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
    entries, skipped = walk_entries(clean, mount_points())
    unreadable = [p for p, why in skipped if why == "unreadable"]
    if unreadable:
        return {"ok": False, "error": "unreadable folders; nothing would be backed up there", "unreadable": unreadable[:20]}
    plan = summarize(entries, skipped)
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
            ok, err = write_tar(part, clean, args.format == "tar.gz")
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
    missing = [m for m in wanted if not os.path.lexists("/" + m.rstrip("/"))]
    result["missing"] = {"items": len(missing), "examples": missing[:10]}
    if args.dry_run or not missing:
        return result
    cmd = tar_base() + ["--extract", "--skip-old-files", "-C", "/", "-f", archive] + \
          (["--gzip"] if gz else []) + ([only.lstrip("/")] if only else [])
    code, out, err = run(cmd)
    result["command"] = " ".join(cmd)
    if code != 0:
        result.update({"ok": False, "error": f"tar failed: {err.strip()}"})
        return result
    left = [m for m in wanted if not os.path.lexists("/" + m.rstrip("/"))]
    result["still_missing"] = len(left)
    result["ok"] = not left
    return result


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
        missing = [(i, o) for i, o in items if not os.path.lexists(o)]
        result["missing"] = {"items": len(missing), "examples": [o for _, o in missing[:10]]}
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
