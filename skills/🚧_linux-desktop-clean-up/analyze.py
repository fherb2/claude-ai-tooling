"""Read-only analysis for the linux-desktop-clean-up skill.

One walk over the home directory and the system directories collects the
data for the fill level and the tables of the skill; the instance reads the
JSON result and builds the tables. Nothing is written except the result
file, nothing is deleted. Progress goes to stderr.

Delivery 15a: fill level and table 3. Tables 1 and 2 follow (15b, 15c).

Usage (paths resolved by the instance beforehand):
    sudo nice -n 19 ionice -c3 python3 -I analyze.py --home /home/<user> \
        --downloads <download dir> --threshold 150 [--archives] \
        [--output /tmp/cleanup-analysis.json]
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

SYSTEM_ROOTS = ["/var", "/opt", "/usr/local", "/srv"]
APP_CONTAINERS = [".config", ".local/share", ".cache", ".var"]
DAY = 86400
STALE_DAYS = 365
TOP_DIRS = 30
REPEAT_SHARE = 0.9          # a subfolder this large relative to its parent only repeats it
DUP_MIN = 1024**2
PARTIAL = 1024**2
CHUNK = 4 * 1024**2
MiB = 1024**2

GROUPS = {
    "video": "mp4 mkv avi mov wmv flv webm m4v mpg mpeg ts mts m2ts 3gp vob",
    "audio": "mp3 flac wav ogg oga opus m4a aac wma aiff",
    "image": "jpg jpeg png gif bmp tif tiff webp heic heif raw cr2 nef arw dng svg psd xcf",
    "archive": "zip tar gz tgz xz bz2 7z rar zst lz4",
    "disk image": "img iso qcow2 vdi vmdk vhd vhdx",
    "deb": "deb",
}
EXT_GROUP = {ext: group for group, exts in GROUPS.items() for ext in exts.split()}
MEDIA_GROUPS = {"video", "audio", "image"}

GIT_TMP = re.compile(r"^tmp_(pack|idx|obj)_")
CRASH_DIRS = ("/var/crash", "/var/lib/systemd/coredump")
PROJECT_MARKERS = {".git", "pyproject.toml", "package.json", "Cargo.toml", "setup.py",
                   "CMakeLists.txt", "go.mod", "pom.xml", "build.gradle"}
DEPENDENCY_LISTS = {"pyproject.toml", "Pipfile", "poetry.lock", "uv.lock", "package.json",
                    "package-lock.json", "Cargo.toml", "Cargo.lock", "go.mod", "environment.yml",
                    "setup.py"}
ARTIFACT_NAMES = {".venv", "venv", "node_modules", "build", "dist", "target", ".tox",
                  ".mypy_cache", ".pytest_cache", ".gradle"}


def file_group(name):
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    return EXT_GROUP.get(ext, "other")


class Areas:
    """Areas of concept.md section 4, defined at this one place."""

    def __init__(self, home, downloads):
        self.home = home
        self.containers = [os.path.join(home, c) for c in APP_CONTAINERS]
        self.paths = {
            os.path.join(home, ".cache/mozilla/firefox"): "4.2",
            os.path.join(home, ".cache/google-chrome"): "4.3",
            os.path.join(home, ".config/Code/Cache"): "4.4",
            os.path.join(home, ".config/Code/CachedData"): "4.4",
            os.path.join(home, ".config/Code/CachedExtensionVSIXs"): "4.4",
            os.path.join(home, ".cache/pip"): "4.6",
            downloads: "4.9",
            "/var/cache/apt/archives": "4.1",
            "/var/log": "4.5",
            "/var/lib/docker": "4.13",
            "/var/lib/containerd": "4.13",
        }

    def in_container(self, path):
        return any(path.startswith(c + os.sep) for c in self.containers)

    def of_dir(self, path, name):
        if path in self.paths:
            return self.paths[path]
        home = self.home
        if name in ("cache2", "startupCache") and path.startswith(os.path.join(home, ".mozilla/firefox/")):
            return "4.2"
        if name == "CacheStorage" and path.startswith(os.path.join(home, ".config/Code/WebStorage/")):
            return "4.4"
        if name in ("log", "logs") and self.in_container(path):
            return "4.5"
        if name == "__pycache__" and path.startswith(home + os.sep):
            return "4.12"
        return None

    def of_file(self, path, name):
        return "4.5" if ".log" in name and self.in_container(path) else None


class Ctx:
    """What a directory belongs to; handed down the walk."""
    __slots__ = ("root", "parts", "is_home", "dot_top", "area", "in_git", "artifact", "project")

    def __init__(self, root, parts, is_home, dot_top, area, in_git, artifact, project):
        self.root, self.parts, self.is_home, self.dot_top = root, parts, is_home, dot_top
        self.area, self.in_git, self.artifact, self.project = area, in_git, artifact, project

    def child(self, name, area, in_git, artifact, project):
        dot_top = self.dot_top or (self.is_home and not self.parts and name.startswith("."))
        return Ctx(self.root, self.parts + (name,), self.is_home, dot_top, area, in_git, artifact, project)


class DirSizes:
    """Size per directory up to depth 3, with the share unchanged for over a year (home only)."""

    def __init__(self, now):
        self.now = now
        self.size = defaultdict(int)
        self.stale = defaultdict(int)

    def file(self, ctx, path, name, st, area):
        if area:
            return
        stale = ctx.is_home and self.now - st.st_mtime > STALE_DAYS * DAY
        for depth in range(0, min(len(ctx.parts), 3) + 1):
            key = (ctx.root, ctx.parts[:depth])
            self.size[key] += st.st_size
            if stale:
                self.stale[key] += st.st_size

    def result(self, home):
        out = {}
        for root in sorted({r for r, _ in self.size}):
            total = self.size.get((root, ()), 0)

            def row(parts):
                key = (root, parts)
                return {"path": os.path.join(root, *parts), "depth": len(parts), "size": self.size[key],
                        "stale_share": round(self.stale[key] / self.size[key], 3)
                        if root == home and self.size[key] else None}

            level1 = sorted((p for r, p in self.size if r == root and len(p) == 1),
                            key=lambda p: self.size[(root, p)], reverse=True)
            deeper = [p for r, p in self.size if r == root and len(p) in (2, 3)
                      and self.size[(root, p)] < REPEAT_SHARE * self.size[(root, p[:-1])]]
            deeper.sort(key=lambda p: self.size[(root, p)], reverse=True)
            out[root] = {"total": total, "level1": [row(p) for p in level1],
                         "deeper": [row(p) for p in deeper[:TOP_DIRS]]}
        return out


class LargeFiles:
    """Single files from the threshold on, unless 4.7, 4.8 or 4.10 cover their type."""

    def __init__(self, threshold, archives):
        self.threshold = threshold
        self.covered = MEDIA_GROUPS | {"deb", "disk image"} | ({"archive"} if archives else set())
        self.rows = []

    def file(self, ctx, path, name, st, area):
        if area or st.st_size < self.threshold:
            return
        group = file_group(name)
        if ctx.is_home and group in self.covered:
            return
        self.rows.append({"path": path, "size": st.st_size, "mtime": int(st.st_mtime), "group": group})


class DuplicateCandidates:
    """User data in the home from 1 MiB on, grouped by size for the later comparison."""

    def __init__(self):
        self.by_size = defaultdict(list)
        self.inodes = set()

    def file(self, ctx, path, name, st, area):
        if (area or not ctx.is_home or ctx.dot_top or ctx.in_git or ctx.artifact
                or st.st_size < DUP_MIN or (st.st_dev, st.st_ino) in self.inodes):
            return
        self.inodes.add((st.st_dev, st.st_ino))
        self.by_size[st.st_size].append(path)


class GitLeftovers:
    def __init__(self):
        self.rows = []

    def file(self, ctx, path, name, st, area):
        if ctx.in_git and GIT_TMP.match(name):
            self.rows.append({"path": path, "size": st.st_size, "mtime": int(st.st_mtime)})


class CrashDumps:
    def __init__(self):
        self.rows = []

    def file(self, ctx, path, name, st, area):
        if path.startswith(CRASH_DIRS):
            self.rows.append({"path": path, "size": st.st_size, "mtime": int(st.st_mtime)})


class DevArtifacts:
    """Artifacts in projects in the home, one entry per project."""

    def __init__(self):
        self.projects = {}

    def project(self, path, names):
        has_deps = bool(names & DEPENDENCY_LISTS) or any(n.startswith("requirements") and n.endswith(".txt")
                                                         for n in names)
        self.projects[path] = {"artifacts": defaultdict(int), "dependency_list": has_deps, "last_source": 0}

    def file(self, ctx, path, name, st, area):
        if not ctx.project:
            return
        info = self.projects[ctx.project]
        if ctx.artifact:
            info["artifacts"][ctx.artifact] += st.st_size
        elif not ctx.in_git and not area:
            info["last_source"] = max(info["last_source"], int(st.st_mtime))

    def result(self):
        rows = []
        for path, info in self.projects.items():
            if info["artifacts"]:
                rows.append({"project": path, "size": sum(info["artifacts"].values()),
                             "artifacts": dict(sorted(info["artifacts"].items(), key=lambda i: -i[1])),
                             "dependency_list": info["dependency_list"],
                             "last_source": info["last_source"] or None})
        return sorted(rows, key=lambda r: r["size"], reverse=True)


def walk(root, home, areas, sinks, artifacts, stats, progress):
    """Single pass over one start directory, staying on its device."""
    try:
        device = os.stat(root).st_dev
    except OSError:
        return
    stack = [(root, Ctx(root, (), root == home, False, areas.of_dir(root, ""), False, None, None))]
    while stack:
        current, ctx = stack.pop()
        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError:
            stats["read_errors"] += 1
            continue
        names = {e.name for e in entries}
        project = ctx.project
        if ctx.is_home and not ctx.dot_top and not ctx.area and not ctx.in_git and not ctx.artifact \
                and current != home and names & PROJECT_MARKERS:
            project = current
            artifacts.project(current, names)
        ctx.project = project
        for entry in entries:
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    st = entry.stat(follow_symlinks=False)
                    if st.st_dev != device:
                        stats["other_filesystems"].append(entry.path)
                        continue
                    area = ctx.area or areas.of_dir(entry.path, entry.name)
                    in_git = ctx.in_git or entry.name == ".git"
                    artifact = ctx.artifact
                    if project and not artifact and not in_git and not area and (
                            entry.name in ARTIFACT_NAMES or os.path.exists(os.path.join(entry.path, "pyvenv.cfg"))):
                        artifact = entry.path
                    stack.append((entry.path, ctx.child(entry.name, area, in_git, artifact, project)))
                    continue
                if not entry.is_file(follow_symlinks=False):
                    continue
                st = entry.stat(follow_symlinks=False)
            except OSError:
                stats["read_errors"] += 1
                continue
            stats["files"] += 1
            area = ctx.area or areas.of_file(entry.path, entry.name)
            for sink in sinks:
                sink.file(ctx, entry.path, entry.name, st, area)
        progress(current, stats["files"])


def file_hash(path, limit=None):
    digest = hashlib.blake2b(digest_size=16)
    read = 0
    with open(path, "rb") as fh:
        while limit is None or read < limit:
            block = fh.read(CHUNK if limit is None else min(CHUNK, limit - read))
            if not block:
                break
            digest.update(block)
            read += len(block)
    return digest.hexdigest()


def find_duplicates(candidates, stats, progress):
    """Groups of identical files: equal size, then equal first MiB, then equal content."""
    groups = []
    sizes = [(s, p) for s, p in candidates.by_size.items() if len(p) > 1]
    for index, (size, paths) in enumerate(sorted(sizes, reverse=True)):
        progress(f"comparing size group {index + 1}/{len(sizes)}", stats["files"])
        by_start = defaultdict(list)
        for path in paths:
            try:
                by_start[file_hash(path, PARTIAL)].append(path)
            except OSError:
                stats["read_errors"] += 1
        for same_start in by_start.values():
            if len(same_start) < 2:
                continue
            by_content = defaultdict(list)
            for path in same_start:
                try:
                    by_content[file_hash(path) if size > PARTIAL else ""].append(path)
                except OSError:
                    stats["read_errors"] += 1
            groups.extend({"size": size, "paths": sorted(g)} for g in by_content.values() if len(g) > 1)
    return sorted(groups, key=lambda g: g["size"] * (len(g["paths"]) - 1), reverse=True)


def run(cmd):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return done.stdout if done.returncode == 0 else None


def filesystems():
    """Fill level per mounted file system and btrfs snapshots."""
    out = run(["df", "-B1", "--output=source,fstype,size,used,target", "-x", "tmpfs", "-x", "devtmpfs",
               "-x", "squashfs", "-x", "overlay", "-x", "efivarfs"]) or ""
    mounts, btrfs = [], {}
    for line in out.splitlines()[1:]:
        source, fstype, size, used, target = line.split(None, 4)
        mounts.append({"mount": target, "source": source, "fstype": fstype, "size": int(size), "used": int(used)})
        if fstype == "btrfs":
            btrfs.setdefault(source, target)
    snapshots = []
    for target in btrfs.values():
        listing = run(["btrfs", "subvolume", "list", "-s", target])
        if listing is None:
            snapshots.append({"mount": target, "count": None, "exclusive": None})
            continue
        ids = {line.split()[1] for line in listing.splitlines() if line.startswith("ID ")}
        if not ids:
            continue
        exclusive = None
        qgroups = run(["btrfs", "qgroup", "show", "--raw", target])
        if qgroups is not None:
            exclusive = sum(int(f[2]) for f in (line.split() for line in qgroups.splitlines())
                            if len(f) >= 3 and f[0].startswith("0/") and f[0][2:] in ids)
        snapshots.append({"mount": target, "count": len(ids), "exclusive": exclusive})
    return {"mounts": mounts, "snapshots": snapshots}


def write_result(path, data):
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--home", required=True)
    parser.add_argument("--downloads", required=True)
    parser.add_argument("--threshold", type=int, default=150, help="size threshold in MiB")
    parser.add_argument("--archives", action="store_true", help="section 4.8 covers general archives")
    parser.add_argument("--output", default="/tmp/cleanup-analysis.json")
    args = parser.parse_args()
    home = os.path.realpath(args.home)
    downloads = os.path.realpath(args.downloads)
    for path in (home, downloads):
        if not os.path.isdir(path):
            print(f"Not a directory: {path}", file=sys.stderr)
            return 2
    if os.geteuid() != 0:
        print("Warning: not running as root; system directories will be incomplete.", file=sys.stderr)

    started = time.time()
    last = [0.0]

    def progress(current, files):
        if time.monotonic() - last[0] >= 2:
            last[0] = time.monotonic()
            print(f"\r  {files:>10,} files  {current[:100]:<100}", end="", file=sys.stderr, flush=True)

    areas = Areas(home, downloads)
    stats = {"files": 0, "read_errors": 0, "other_filesystems": []}
    dir_sizes, large = DirSizes(started), LargeFiles(args.threshold * MiB, args.archives)
    dup_candidates, git_left, crashes = DuplicateCandidates(), GitLeftovers(), CrashDumps()
    artifacts = DevArtifacts()
    sinks = [dir_sizes, large, dup_candidates, git_left, crashes, artifacts]

    print("Step 1/3: file system usage", file=sys.stderr)
    fill = filesystems()
    for root in [home] + [r for r in SYSTEM_ROOTS if os.path.isdir(r)]:
        print(f"\nStep 2/3: walking {root}", file=sys.stderr)
        walk(root, home, areas, sinks, artifacts, stats, progress)
    print("\nStep 3/3: comparing files of equal size", file=sys.stderr)
    duplicates = find_duplicates(dup_candidates, stats, progress)
    print(file=sys.stderr)

    data = {
        "meta": {"tool": "analyze.py", "delivery": "15a",
                 "started": datetime.fromtimestamp(started, timezone.utc).isoformat(timespec="seconds"),
                 "duration_s": round(time.time() - started, 1), "files": stats["files"],
                 "read_errors": stats["read_errors"], "other_filesystems": sorted(stats["other_filesystems"]),
                 "params": {"home": home, "downloads": downloads, "threshold_mib": args.threshold,
                            "archives": args.archives}},
        "fill_level": fill,
        "table1": {},
        "software": {},
        "table3": {
            "dir_sizes": dir_sizes.result(home),
            "large_files": sorted(large.rows, key=lambda r: r["size"], reverse=True),
            "duplicates": duplicates,
            "git_leftovers": git_left.rows,
            "crash_dumps": crashes.rows,
            "dev_artifacts": artifacts.result(),
        },
    }
    write_result(args.output, data)
    print(f"Done: {stats['files']:,} files in {data['meta']['duration_s']} s, "
          f"{stats['read_errors']} read errors. Result: {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
