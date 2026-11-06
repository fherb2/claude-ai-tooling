"""Read-only analysis for the linux-desktop-clean-up skill.

One walk over the home directory and the system directories collects the
data for the fill level and the tables of the skill; the instance reads the
JSON result and builds the tables. Nothing is written except the result
file, nothing is deleted. Progress goes to stderr.

Deliveries: 15a fill level and table 3, 15b table 1, 15c software inventory (table 2).

Usage (paths resolved by the instance beforehand):
    sudo nice -n 19 ionice -c3 python3 -I analyze.py --home /home/<user> \
        --downloads <download dir> --media-dir <dir> [--media-dir <dir> ...] \
        --desktop "$XDG_CURRENT_DESKTOP" --threshold 150 [--archives] \
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
            os.path.join(home, ".local/share/Trash"): "4.14",
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

    def project(self, path, names, is_project=True):
        if path in self.projects:
            return
        has_deps = bool(names & DEPENDENCY_LISTS) or any(n.startswith("requirements") and n.endswith(".txt")
                                                         for n in names)
        self.projects[path] = {"artifacts": defaultdict(int), "dependency_list": has_deps, "last_source": 0,
                               "is_project": is_project}

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
                rows.append({"project": path, "is_project": info["is_project"],
                             "size": sum(info["artifacts"].values()),
                             "artifacts": dict(sorted(info["artifacts"].items(), key=lambda i: -i[1])),
                             "dependency_list": info["dependency_list"],
                             "last_source": info["last_source"] or None})
        return sorted(rows, key=lambda r: r["size"], reverse=True)


# --- table 1: the areas of concept.md section 4 -------------------------------------------------

CACHE_AGE = 3 * DAY
STALE_PROFILE_AGE = 30 * DAY
PIP_BIG = 50 * MiB
DEB_DEPTH = 5
ENTRY_NAME = re.compile(r"^[0-9a-f]{16}_")
PARTIAL_DOWNLOAD = (".crdownload", ".part")
COMPOSE_NAMES = {"compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"}


def below(path, base):
    """Path components of path below base, or None if path is not inside base."""
    if not path.startswith(base + os.sep):
        return None
    return path[len(base) + 1:].split(os.sep)


def age(st, now):
    """Seconds since the later of modification and status change."""
    return now - max(st.st_mtime, st.st_ctime)


class Bucket:
    """Count and size of a group of files."""

    def __init__(self):
        self.count = 0
        self.size = 0

    def add(self, size):
        self.count += 1
        self.size += size

    def out(self):
        return {"count": self.count, "size": self.size}


class AptArchives:
    """4.1: downloaded packages in the apt cache."""

    def __init__(self):
        self.packages = Bucket()

    def file(self, ctx, path, name, st, area):
        if area == "4.1" and name.endswith(".deb"):
            self.packages.add(st.st_size)

    def result(self):
        return self.packages.out()


class BrowserCache:
    """4.2 and 4.3: old entries and index files per profile."""

    def __init__(self, home, now):
        self.now = now
        self.ff_cache = os.path.join(home, ".cache/mozilla/firefox")
        self.ff_profiles = os.path.join(home, ".mozilla/firefox")
        self.chrome = os.path.join(home, ".cache/google-chrome")
        self.firefox = defaultdict(lambda: {"old_entries": Bucket(), "all_entries": Bucket(), "index": False})
        self.remnants = defaultdict(lambda: {"size": 0, "newest": 0})
        self.chrome_profiles = defaultdict(lambda: defaultdict(lambda: {"old_entries": Bucket(),
                                                                         "all_entries": Bucket(), "index": False}))

    def file(self, ctx, path, name, st, area):
        if area != "4.2" and area != "4.3":
            return
        parts = below(path, self.ff_cache)
        if parts and len(parts) >= 3 and parts[1] == "cache2":
            profile = self.firefox[parts[0]]
            if parts[2] == "entries" and len(parts) == 4:
                profile["all_entries"].add(st.st_size)
                if age(st, self.now) > CACHE_AGE:
                    profile["old_entries"].add(st.st_size)
            elif parts[2] == "index" and len(parts) == 3:
                profile["index"] = True
            return
        parts = below(path, self.ff_profiles)
        if parts and len(parts) >= 3 and parts[1] in ("cache2", "startupCache"):
            remnant = self.remnants[os.path.join(self.ff_profiles, parts[0], parts[1])]
            remnant["size"] += st.st_size
            remnant["newest"] = max(remnant["newest"], st.st_mtime)
            return
        parts = below(path, self.chrome)
        if not parts or len(parts) < 3:
            return
        if parts[1:3] == ["Cache", "Cache_Data"]:
            kind, rest = "cache_data", parts[3:]
        elif parts[1:3] == ["Code Cache", "js"]:
            kind, rest = "code_cache_js", parts[3:]
        else:
            return
        slot = self.chrome_profiles[parts[0]][kind]
        if len(rest) == 1 and ENTRY_NAME.match(rest[0]):
            slot["all_entries"].add(st.st_size)
            if age(st, self.now) > CACHE_AGE:
                slot["old_entries"].add(st.st_size)
        elif rest and (rest[0] == "index" or rest[0] == "index-dir"):
            slot["index"] = True

    @staticmethod
    def _slot(slot):
        return {"old_entries": slot["old_entries"].out(), "all_entries": slot["all_entries"].out(),
                "index": slot["index"]}

    def result(self):
        remnants = [{"path": p, "size": r["size"], "newest": int(r["newest"]),
                     "stale": self.now - r["newest"] > STALE_PROFILE_AGE} for p, r in sorted(self.remnants.items())]
        return {
            "firefox": {"profiles": {p: self._slot(s) for p, s in sorted(self.firefox.items())},
                        "profile_remnants": remnants},
            "chrome": {"profiles": {p: {k: self._slot(s) for k, s in kinds.items()}
                                    for p, kinds in sorted(self.chrome_profiles.items())}},
        }


class VSCodeCache:
    """4.4: Cache_Data entries, old CachedData folders, broken VSIX downloads, CacheStorage size."""

    def __init__(self, home, now):
        self.now = now
        self.base = os.path.join(home, ".config/Code")
        self.cache_data = {"old_entries": Bucket(), "all_entries": Bucket(), "index": False}
        self.cached_data = defaultdict(lambda: {"size": 0, "newest": 0})
        self.vsix_broken = []
        self.cache_storage = Bucket()

    def file(self, ctx, path, name, st, area):
        if area != "4.4":
            return
        parts = below(path, self.base)
        if not parts:
            return
        if parts[:2] == ["Cache", "Cache_Data"] and len(parts) >= 3:
            if len(parts) == 3 and ENTRY_NAME.match(parts[2]):
                self.cache_data["all_entries"].add(st.st_size)
                if age(st, self.now) > CACHE_AGE:
                    self.cache_data["old_entries"].add(st.st_size)
            elif parts[2] in ("index", "index-dir"):
                self.cache_data["index"] = True
        elif parts[0] == "CachedData" and len(parts) >= 3:
            folder = self.cached_data[parts[1]]
            folder["size"] += st.st_size
            folder["newest"] = max(folder["newest"], st.st_mtime)
        elif parts[0] == "CachedExtensionVSIXs" and len(parts) == 2 and name.startswith("."):
            if age(st, self.now) > CACHE_AGE and not is_zip(path):
                self.vsix_broken.append({"path": path, "size": st.st_size, "mtime": int(st.st_mtime)})
        elif parts[0] == "WebStorage" and "CacheStorage" in parts:
            self.cache_storage.add(st.st_size)

    def result(self):
        commit = installed_vscode_commit()
        old = [{"folder": os.path.join(self.base, "CachedData", n), "size": f["size"], "newest": int(f["newest"])}
               for n, f in sorted(self.cached_data.items())
               if n != commit and self.now - f["newest"] > CACHE_AGE]
        return {"installed_commit": commit,
                "cache_data": {"old_entries": self.cache_data["old_entries"].out(),
                               "all_entries": self.cache_data["all_entries"].out(),
                               "index": self.cache_data["index"]},
                "cached_data_old": old, "vsix_broken": self.vsix_broken,
                "cache_storage": self.cache_storage.out()}


def is_zip(path):
    try:
        with open(path, "rb") as fh:
            return fh.read(4) == b"PK\x03\x04"
    except OSError:
        return False


def installed_vscode_commit():
    try:
        with open("/usr/share/code/resources/app/product.json", encoding="utf-8") as fh:
            return json.load(fh).get("commit")
    except (OSError, ValueError):
        return None


class LogSizes:
    """4.5 in the first analysis: two sums only, log files and the journal."""

    JOURNAL = ("/var/log/journal" + os.sep, "/run/log/journal" + os.sep)

    def __init__(self):
        self.logs = Bucket()
        self.journal = Bucket()

    def file(self, ctx, path, name, st, area):
        if area != "4.5":
            return
        (self.journal if path.startswith(self.JOURNAL) else self.logs).add(st.st_size)

    def result(self):
        volatile = "/run/log/journal"
        for folder, _, files in os.walk(volatile):
            for name in files:
                try:
                    self.journal.add(os.lstat(os.path.join(folder, name)).st_size)
                except OSError:
                    pass
        return {"log_files": self.logs.out(), "journal": self.journal.out()}


class TrashSizes:
    """4.14: size and number of entries per trash directory, no content."""

    def __init__(self, home):
        self.home_trash = os.path.join(home, ".local/share/Trash")
        self.size = 0

    def file(self, ctx, path, name, st, area):
        if area == "4.14" and path.startswith(os.path.join(self.home_trash, "files") + os.sep):
            self.size += st.st_size

    @staticmethod
    def entries(trash):
        try:
            return sum(1 for n in os.listdir(os.path.join(trash, "info")) if n.endswith(".trashinfo"))
        except OSError:
            return 0

    def result(self, mounts, uid):
        rows = [{"path": self.home_trash, "entries": self.entries(self.home_trash), "size": self.size}]
        for mount in mounts:
            for trash in (os.path.join(mount, ".Trash", str(uid)), os.path.join(mount, f".Trash-{uid}")):
                if not os.path.isdir(trash) or trash == self.home_trash:
                    continue
                size = 0
                for folder, _, files in os.walk(os.path.join(trash, "files")):
                    for name in files:
                        try:
                            size += os.lstat(os.path.join(folder, name)).st_size
                        except OSError:
                            pass
                rows.append({"path": trash, "entries": self.entries(trash), "size": size})
        return rows


class PipCache:
    """4.6: size of the pip cache and its entries from 50 MiB on (no names)."""

    def __init__(self):
        self.total = Bucket()
        self.big = []

    def file(self, ctx, path, name, st, area):
        if area == "4.6":
            self.total.add(st.st_size)
            if st.st_size >= PIP_BIG:
                self.big.append({"size": st.st_size, "mtime": int(st.st_mtime)})

    def result(self):
        return {"total": self.total.out(), "big_entries": sorted(self.big, key=lambda r: -r["size"])}


class UserFiles:
    """4.7 to 4.10: .deb files, images and archives, the download folder, stray media."""

    def __init__(self, home, downloads, media_dirs, threshold, archives, now):
        self.home, self.downloads, self.now = home, downloads, now
        self.media_dirs = media_dirs
        self.threshold, self.archives = threshold, archives
        self.excluded = [os.path.join(home, d) for d in (".config", ".local", ".cache")]
        self.trash = os.path.join(home, ".local/share/Trash")
        self.debs, self.images, self.media = [], [], []
        self.download_entries = defaultdict(lambda: {"size": 0, "youngest_age": None, "is_dir": False})

    def _inside(self, path, bases):
        return any(path == b or path.startswith(b + os.sep) for b in bases)

    def file(self, ctx, path, name, st, area):
        if not ctx.is_home:
            return
        group = file_group(name)
        in_downloads = area == "4.9"
        if in_downloads:
            parts = below(path, self.downloads)
            entry = self.download_entries[os.path.join(self.downloads, parts[0])]
            entry["size"] += st.st_size
            entry["is_dir"] = len(parts) > 1
            file_age = age(st, self.now)
            if entry["youngest_age"] is None or file_age < entry["youngest_age"]:
                entry["youngest_age"] = file_age
        if group == "deb" and (in_downloads or (len(ctx.parts) < DEB_DEPTH and not area
                                                and not self._inside(path, [self.trash, os.path.join(self.home, ".cache")]))):
            self.debs.append({"path": path, "size": st.st_size})
            return
        if in_downloads or area or st.st_size < self.threshold or self._inside(path, self.excluded):
            return
        if group == "disk image" or (group == "archive" and self.archives):
            self.images.append({"path": path, "size": st.st_size, "mtime": int(st.st_mtime), "group": group})
        elif group in MEDIA_GROUPS and not ctx.dot_top and not self._inside(path, self.media_dirs):
            self.media.append({"path": path, "size": st.st_size, "mtime": int(st.st_mtime), "group": group,
                               "in_git": ctx.in_git, "project": ctx.project})

    def result(self):
        for deb in self.debs:
            deb.update(deb_status(deb["path"]))
        folders = {}
        for row in self.media:
            folder = os.path.dirname(row["path"])
            if folder not in folders:
                folders[folder] = neighbour_groups(folder)
        downloads = []
        for path, e in sorted(self.download_entries.items(), key=lambda i: -i[1]["size"]):
            days = int(e["youngest_age"] // DAY) if e["youngest_age"] is not None else None
            downloads.append({"path": path, "is_dir": e["is_dir"], "size": e["size"], "age_days": days,
                              "partial": not e["is_dir"] and path.endswith(PARTIAL_DOWNLOAD)})
        return {"deb_files": self.debs,
                "images_archives": sorted(self.images, key=lambda r: -r["size"]),
                "downloads": downloads,
                "stray_media": {"files": sorted(self.media, key=lambda r: -r["size"]), "folders": folders}}


def deb_status(path):
    """Package and version of a .deb file compared with the installed version."""
    fields = run(["dpkg-deb", "-f", path, "Package", "Version"])
    if not fields:
        return {"package": None, "status": "unreadable"}
    info = dict(line.split(": ", 1) for line in fields.splitlines() if ": " in line)
    package, version = info.get("Package"), info.get("Version")
    if not package or not version:
        return {"package": package, "status": "unreadable"}
    installed = run(["dpkg-query", "-W", "-f=${Status}|${Version}", package])
    if not installed or not installed.startswith("install ok installed"):
        return {"package": package, "version": version, "installed": None, "status": "not_installed"}
    inst_version = installed.split("|", 1)[1]
    newer = subprocess.run(["dpkg", "--compare-versions", inst_version, "ge", version]).returncode == 0
    return {"package": package, "version": version, "installed": inst_version,
            "status": "same_or_newer_installed" if newer else "older_installed"}


def neighbour_groups(folder):
    """File groups of the files in a folder, for the instance's judgement of the folder."""
    counts = defaultdict(int)
    try:
        with os.scandir(folder) as it:
            for entry in it:
                if entry.is_file(follow_symlinks=False):
                    counts[file_group(entry.name)] += 1
    except OSError:
        pass
    return dict(counts)


class PyCache:
    """4.12: __pycache__ folders in the home."""

    def __init__(self):
        self.dirs = set()
        self.total = Bucket()

    def file(self, ctx, path, name, st, area):
        if area == "4.12" and ctx.is_home:
            parts = ctx.parts
            self.dirs.add(parts[:parts.index("__pycache__") + 1] if "__pycache__" in parts else parts)
            self.total.add(st.st_size)

    def result(self):
        return {"folders": len(self.dirs), "files": self.total.count, "size": self.total.size}


class ComposeFiles:
    """Compose files in the home, for 4.13."""

    def __init__(self):
        self.paths = []

    def file(self, ctx, path, name, st, area):
        if ctx.is_home and name in COMPOSE_NAMES and not ctx.artifact:
            self.paths.append(path)


def json_lines(cmd):
    out = run(cmd)
    if out is None:
        return None
    rows = []
    for line in out.splitlines():
        try:
            item = json.loads(line)
        except ValueError:
            continue
        # some commands print one JSON object per line, others a single array
        rows.extend(item if isinstance(item, list) else [item])
    return [r for r in rows if isinstance(r, dict)]


def docker_state(compose_paths):
    """4.13: state of Docker read through its own commands; nothing is changed."""
    state = {"podman_present": bool(run(["sh", "-c", "command -v podman"]))}
    containers = json_lines(["docker", "ps", "-a", "--format", "json"])
    if containers is None:
        state["available"] = False
        return state
    state["available"] = True
    state["stopped_containers"] = [{"name": c.get("Names"), "image": c.get("Image"), "status": c.get("Status"),
                                    "size": c.get("Size"), "created": c.get("CreatedAt")}
                                   for c in containers if c.get("State") != "running"]
    state["running_images"] = sorted({c.get("Image") for c in containers if c.get("State") == "running"})
    state["used_images"] = sorted({c.get("Image") for c in containers})
    state["images"] = [{"name": f"{i.get('Repository')}:{i.get('Tag')}", "id": i.get("ID"),
                        "created": i.get("CreatedSince"), "size": i.get("Size")}
                       for i in json_lines(["docker", "images", "--format", "json"]) or []]
    volumes = [v.get("Name", "") for v in json_lines(["docker", "volume", "ls", "--format", "json"]) or []]
    state["named_volumes"] = [v for v in volumes if not re.fullmatch(r"[0-9a-f]{64}", v)]
    state["anonymous_volumes"] = [v for v in volumes if re.fullmatch(r"[0-9a-f]{64}", v)]
    state["disk_usage"] = json_lines(["docker", "system", "df", "--format", "json"])
    listed = {}
    for project in json_lines(["docker", "compose", "ls", "-a", "--format", "json"]) or []:
        for cfg in str(project.get("ConfigFiles", "")).split(","):
            listed[cfg.strip()] = project.get("Status")
    compose = []
    for path in sorted(compose_paths):
        try:
            mtime = int(os.stat(path).st_mtime)
        except OSError:
            mtime = None
        config = run(["docker", "compose", "-f", path, "config", "--format", "json"])
        images = run(["docker", "compose", "-f", path, "config", "--images"])
        name = None
        if config:
            try:
                name = json.loads(config).get("name")
            except ValueError:
                pass
        compose.append({"path": path, "mtime": mtime, "project": name,
                        "images": [i if ":" in i else i + ":latest" for i in images.split()] if images else None,
                        "state": listed.get(path, "down")})
    state["compose"] = compose
    return state


# --- software inventory: data for table 2 and for leftovers of uninstalled programs (4.11) ------

MAIN_CATEGORIES = {"AudioVideo", "Audio", "Video", "Development", "Education", "Game", "Graphics",
                   "Network", "Office", "Science", "Settings", "System", "Utility"}


def desktop_dirs(home):
    """Starter entry locations of concept.md 4.11 with their origin; the user's own come first."""
    return [(os.path.join(home, ".local/share/applications"), "local"),
            (os.path.join(home, ".local/share/flatpak/exports/share/applications"), "flatpak"),
            ("/usr/local/share/applications", "local"),
            ("/var/lib/flatpak/exports/share/applications", "flatpak"),
            ("/var/lib/snapd/desktop/applications", "snap"),
            ("/usr/share/applications", "system")]


def read_desktop_entry(path):
    """Keys of the [Desktop Entry] group (unlocalised)."""
    keys, in_group = {}, False
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("["):
                    in_group = line == "[Desktop Entry]"
                elif in_group and "=" in line:
                    key, value = line.split("=", 1)
                    keys.setdefault(key.strip(), value.strip())
    except OSError:
        return None
    return keys


def exclusion_reason(keys, desktops):
    """Rules 1-4 of concept.md 4.11; None if the entry counts as user software."""
    split = lambda key: [v for v in keys.get(key, "").split(";") if v]
    if keys.get("Type") != "Application":
        return "type"
    if keys.get("NoDisplay", "").lower() == "true" or keys.get("Hidden", "").lower() == "true":
        return "hidden"
    only, never = split("OnlyShowIn"), split("NotShowIn")
    if (only and not set(only) & desktops) or set(never) & desktops:
        return "desktop"
    if keys.get("Terminal", "").lower() == "true":
        return "terminal"
    main = set(split("Categories")) & MAIN_CATEGORIES
    if not main:
        return "no_main_category"
    if not main - {"Settings", "System"}:
        return "system_or_settings"
    return None


def desktop_entries(home, current_desktop):
    """User software from the starter entries, plus the excluded entries with their reason."""
    desktops = {d for d in current_desktop.split(":") if d}
    seen, included, excluded = set(), [], []
    for folder, origin in desktop_dirs(home):
        for base, _, files in os.walk(folder):
            for fname in sorted(files):
                if not fname.endswith(".desktop"):
                    continue
                path = os.path.join(base, fname)
                entry_id = os.path.relpath(path, folder).replace(os.sep, "-")
                if entry_id in seen:
                    continue          # an earlier location overrides this entry
                seen.add(entry_id)
                keys = read_desktop_entry(path)
                if keys is None:
                    continue
                reason = exclusion_reason(keys, desktops)
                row = {"id": entry_id, "name": keys.get("Name"), "path": path, "origin": origin}
                if reason:
                    excluded.append({**row, "reason": reason})
                    continue
                command = keys.get("Exec", "").split()
                included.append({**row, "exec": os.path.basename(command[0]) if command else None,
                                 "categories": [c for c in keys.get("Categories", "").split(";") if c],
                                 "wm_class": keys.get("StartupWMClass")})
    package_of(included)
    return {"current_desktop": current_desktop, "included": included, "excluded": excluded}


def package_of(entries):
    """Debian package and version of system starter entries, with one dpkg -S for all."""
    paths = [e["path"] for e in entries if e["origin"] in ("system", "local")]
    if not paths:
        return
    try:
        out = subprocess.run(["dpkg", "-S", *paths], capture_output=True, text=True).stdout
    except FileNotFoundError:
        return
    owner = {}
    for line in out.splitlines():
        package, _, path = line.partition(": ")
        owner[path.strip()] = package.split(":")[0].split(",")[0].strip()
    versions = {}
    if owner:
        listing = run(["dpkg-query", "-W", "-f=${Package} ${Version}\n", *sorted(set(owner.values()))]) or ""
        versions = dict(line.split(" ", 1) for line in listing.splitlines() if " " in line)
    for e in entries:
        package = owner.get(e["path"])
        e["package"] = package
        e["version"] = versions.get(package)
        if e["origin"] == "system" and package:
            e["origin"] = "deb"


def other_installs(home):
    """Installed Flatpaks (system and user) and Snaps."""
    flatpaks = []
    for line in (run(["flatpak", "list", "--app", "--system", "--columns=application,name,version"]) or "").splitlines():
        cols = line.split("\t")
        flatpaks.append({"id": cols[0], "name": cols[1] if len(cols) > 1 else None,
                         "version": cols[2] if len(cols) > 2 else None, "scope": "system"})
    try:
        for app in sorted(os.listdir(os.path.join(home, ".local/share/flatpak/app"))):
            flatpaks.append({"id": app, "name": None, "version": None, "scope": "user"})
    except OSError:
        pass
    snaps = [{"name": cols[0], "version": cols[1] if len(cols) > 1 else None}
             for cols in (line.split() for line in (run(["snap", "list"]) or "").splitlines()[1:]) if cols]
    return {"flatpak": flatpaks, "snap": snaps}


class AppFolders:
    """Application folders in the home with size and newest change, without section 4 areas."""

    def __init__(self, home):
        self.home = home
        self.size = defaultdict(int)
        self.newest = defaultdict(float)

    def folder(self, parts):
        if not parts or not parts[0].startswith("."):
            return None
        if parts[0] in (".config", ".cache"):
            return parts[:2] if len(parts) >= 2 else None
        if parts[0] in (".local", ".var"):
            inner = "share" if parts[0] == ".local" else "app"
            return parts[:3] if len(parts) >= 3 and parts[1] == inner else None
        return parts[:1]

    def file(self, ctx, path, name, st, area):
        if area or not ctx.is_home:
            return
        key = self.folder(ctx.parts)
        if key:
            self.size[key] += st.st_size
            self.newest[key] = max(self.newest[key], st.st_mtime)

    def result(self, tokens):
        rows = []
        for key, size in sorted(self.size.items(), key=lambda i: -i[1]):
            rows.append({"path": os.path.join(self.home, *key), "size": size, "newest": int(self.newest[key]),
                         "prefilter_match": match_installed(key[-1], tokens)})
        return rows


def norm(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def installed_tokens(desktop, installs):
    """Normalised names of installed software; used only for the prefilter, not written out."""
    tokens = set()
    for e in desktop["included"] + desktop["excluded"]:
        tokens.update(norm(p) for p in e["id"][:-8].split("."))
        tokens.update(norm(e.get(k)) for k in ("name", "exec", "wm_class", "package"))
    # only packages actually installed; dpkg also lists removed ones whose records remain
    listing = run(["dpkg-query", "-W", "-f=${db:Status-Abbrev} ${Package}\n"]) or ""
    tokens.update(norm(f[1]) for f in (line.split() for line in listing.splitlines())
                  if len(f) == 2 and f[0].startswith("ii"))
    for f in installs["flatpak"]:
        tokens.update(norm(p) for p in f["id"].split("."))
    tokens.update(norm(s["name"]) for s in installs["snap"])
    tokens.discard("")
    return tokens


def match_installed(name, tokens):
    """Best matching installed name for a folder name, or None (prefilter only)."""
    key = norm(name)
    if not key:
        return None
    if key in tokens:
        return key
    if len(key) >= 4:
        for token in sorted(tokens):
            if len(token) >= 4 and (token in key or key in token):
                return token
    return None


def software(home, current_desktop, app_folders):
    desktop = desktop_entries(home, current_desktop)
    installs = other_installs(home)
    return {"desktop": desktop, **installs, "app_folders": app_folders.result(installed_tokens(desktop, installs))}


def safe(func, *args):
    """Run a step after the walk; a failure is recorded instead of losing the whole analysis."""
    try:
        return func(*args)
    except Exception as exc:  # noqa: BLE001 - any failure here must not discard the walk
        print(f"\nWarning: {func.__name__} failed: {exc!r}", file=sys.stderr)
        return {"error": repr(exc)}


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
                    artifact, owner = ctx.artifact, project
                    if not artifact and not in_git and not area:
                        if project and entry.name in ARTIFACT_NAMES:
                            artifact = entry.path
                        elif ctx.is_home and not ctx.dot_top and os.path.exists(os.path.join(entry.path, "pyvenv.cfg")):
                            artifact = entry.path
                            if not owner:
                                # a Python environment outside a project counts on its own
                                owner = current
                                artifacts.project(current, names, is_project=False)
                    stack.append((entry.path, ctx.child(entry.name, area, in_git, artifact, owner)))
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
    parser.add_argument("--desktop", default="", help="value of XDG_CURRENT_DESKTOP (lost under sudo)")
    parser.add_argument("--media-dir", action="append", default=[],
                        help="user folder for videos, music, pictures or documents (repeatable)")
    parser.add_argument("--output", default="/tmp/cleanup-analysis.json")
    args = parser.parse_args()
    home = os.path.realpath(args.home)
    downloads = os.path.realpath(args.downloads)
    media_dirs = [os.path.realpath(d) for d in args.media_dir]
    for path in [home, downloads] + media_dirs:
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
    apt, browsers, vscode = AptArchives(), BrowserCache(home, started), VSCodeCache(home, started)
    pip, pycache, compose, logs = PipCache(), PyCache(), ComposeFiles(), LogSizes()
    trash, app_folders = TrashSizes(home), AppFolders(home)
    user_files = UserFiles(home, downloads, media_dirs, args.threshold * MiB, args.archives, started)
    sinks = [dir_sizes, large, dup_candidates, git_left, crashes, artifacts,
             apt, browsers, vscode, pip, pycache, compose, user_files, logs, trash, app_folders]

    print("Step 1/4: file system usage", file=sys.stderr)
    fill = filesystems()
    for root in [home] + [r for r in SYSTEM_ROOTS if os.path.isdir(r)]:
        print(f"\nStep 2/4: walking {root}", file=sys.stderr)
        walk(root, home, areas, sinks, artifacts, stats, progress)
    print("\nStep 3/4: comparing files of equal size", file=sys.stderr)
    duplicates = find_duplicates(dup_candidates, stats, progress)
    print("\nStep 4/4: package versions, media folders, Docker, installed software", file=sys.stderr)
    table1 = {"4.1_apt": apt.result(), **{f"4.{n}_{k}": v for n, (k, v) in
                                         zip((2, 3), browsers.result().items())},
              "4.4_vscode": vscode.result(), "4.5_logs": logs.result(), "4.6_pip": pip.result()}
    files = user_files.result()
    table1.update({"4.7_deb_files": files["deb_files"], "4.8_images_archives": files["images_archives"],
                   "4.9_downloads": files["downloads"], "4.10_stray_media": files["stray_media"],
                   "4.12_pycache": pycache.result(), "4.13_docker": safe(docker_state, compose.paths),
                   "4.14_trash": trash.result([m["mount"] for m in fill["mounts"]], os.stat(home).st_uid)})

    data = {
        "meta": {"tool": "analyze.py", "delivery": "15c",
                 "started": datetime.fromtimestamp(started, timezone.utc).isoformat(timespec="seconds"),
                 "duration_s": round(time.time() - started, 1), "files": stats["files"],
                 "read_errors": stats["read_errors"], "other_filesystems": sorted(stats["other_filesystems"]),
                 "params": {"home": home, "downloads": downloads, "threshold_mib": args.threshold,
                            "archives": args.archives, "media_dirs": media_dirs,
                            "desktop": args.desktop}},
        "fill_level": fill,
        "table1": table1,
        "software": safe(software, home, args.desktop, app_folders),
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
