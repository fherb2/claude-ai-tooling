"""Read-only probe of five further analyses; which of them are worth keeping is decided afterwards.

A1  leftovers of uninstalled programs: application folders in the home
    whose name matches no installed software
A2  duplicate files (>= 1 MiB): grouped by size, then compared by hash
A3  leftovers of aborted git fetches (tmp_pack_*, tmp_idx_*, tmp_obj_*)
A4  crash dumps (/var/crash, systemd-coredump, files named core / core.<pid>)
A5  development artifacts (.venv, node_modules, build output, tool caches)

One walk collects A1, A3, A4 and A5 and the size groups for A2; only files
of equal size are read afterwards. Nothing is written or deleted. Progress
goes to stderr (terminal only), results to stdout (for tee).

Usage (as the desktop user, the script itself runs as root):
    sudo nice -n 19 ionice -c3 python3 -I extras_probe.py --home "$HOME" \
        | tee /tmp/extras_probe.log
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime

SYSTEM_ROOTS = ["/var", "/opt", "/usr/local", "/srv"]
APP_CONTAINERS = [".config", ".local/share", ".cache", ".var/app"]
DUP_MIN = 1024**2
PARTIAL = 1024**2
CHUNK = 4 * 1024**2
TOP = 40
GIT_TMP = re.compile(r"^tmp_(pack|idx|obj)_")
CORE = re.compile(r"^core(\.\d+)?$")
ARTIFACT_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".tox", ".mypy_cache",
                 ".pytest_cache", ".gradle", "target", "build", "dist"}
DESKTOP_DIRS = ["/usr/share/applications", "/usr/local/share/applications",
                "/var/lib/flatpak/exports/share/applications", "/var/lib/snapd/desktop/applications"]


def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def run(cmd):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return done.stdout if done.returncode == 0 else ""


def survey_installed(home):
    """Normalized name tokens of installed software (desktop entries, dpkg, flatpak, snap)."""
    tokens = set()
    dirs = DESKTOP_DIRS + [os.path.join(home, ".local/share/applications"),
                           os.path.join(home, ".local/share/flatpak/exports/share/applications")]
    for folder in dirs:
        try:
            names = os.listdir(folder)
        except OSError:
            continue
        for fname in names:
            if not fname.endswith(".desktop"):
                continue
            tokens.update(norm(part) for part in fname[:-8].split("."))
            try:
                with open(os.path.join(folder, fname), encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        key, _, value = line.partition("=")
                        if key in ("Name", "StartupWMClass"):
                            tokens.add(norm(value))
                        elif key == "Exec" and value.split():
                            tokens.add(norm(os.path.basename(value.split()[0])))
            except OSError:
                pass
    tokens.update(norm(p) for p in run(["dpkg-query", "-W", "-f=${Package}\n"]).split())
    for line in run(["flatpak", "list", "--app", "--columns=application"]).split():
        tokens.update(norm(part) for part in line.split("."))
    for line in run(["snap", "list"]).splitlines()[1:]:
        if line.split():
            tokens.add(norm(line.split()[0]))
    tokens.discard("")
    return tokens


def match_installed(name, tokens):
    """Best matching installed token for a folder name, or None."""
    key = norm(name)
    if not key:
        return None
    if key in tokens:
        return key
    if len(key) >= 4:
        for token in tokens:
            if len(token) >= 4 and (token in key or key in token):
                return token
    return None


class Stats:
    def __init__(self):
        self.app_size = defaultdict(int)       # A1: app folder -> bytes
        self.app_newest = defaultdict(float)   # A1: app folder -> newest mtime
        self.by_size = defaultdict(list)       # A2: size -> [path]
        self.seen_inodes = set()
        self.git_tmp = []                      # A3: (size, mtime, path)
        self.cores = []                        # A4: (size, mtime, path)
        self.artifacts = defaultdict(int)      # A5: artifact folder -> bytes
        self.files = 0
        self.errors = 0


def child_bucket(parent, name, home, containers):
    """App folder a directory belongs to (A1), or None."""
    if parent in containers:
        return os.path.join(parent, name)
    if parent == home and name.startswith(".") and os.path.join(home, name) not in containers \
            and name not in (".local", ".var"):
        return os.path.join(home, name)
    return None


def walk_tree(root, home, stats, progress):
    """Single pass over one start directory, staying on its device."""
    try:
        device = os.stat(root).st_dev
    except OSError:
        return
    containers = {os.path.join(home, c) for c in APP_CONTAINERS}
    stack = [(root, None, None)]   # (path, app folder, artifact folder)
    while stack:
        current, bucket, artifact = stack.pop()
        try:
            entries = os.scandir(current)
        except OSError:
            stats.errors += 1
            continue
        with entries:
            for entry in entries:
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        if entry.stat(follow_symlinks=False).st_dev != device:
                            continue
                        child_app = bucket or child_bucket(current, entry.name, home, containers)
                        child_art = artifact
                        if artifact is None and (entry.name in ARTIFACT_DIRS
                                                 or os.path.exists(os.path.join(entry.path, "pyvenv.cfg"))):
                            child_art = entry.path
                        stack.append((entry.path, child_app, child_art))
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        continue
                    st = entry.stat(follow_symlinks=False)
                except OSError:
                    stats.errors += 1
                    continue
                stats.files += 1
                size, mtime = st.st_size, st.st_mtime
                if bucket:
                    stats.app_size[bucket] += size
                    stats.app_newest[bucket] = max(stats.app_newest[bucket], mtime)
                if artifact:
                    stats.artifacts[artifact] += size
                if size >= DUP_MIN and (st.st_dev, st.st_ino) not in stats.seen_inodes:
                    stats.seen_inodes.add((st.st_dev, st.st_ino))
                    stats.by_size[size].append(entry.path)
                if GIT_TMP.match(entry.name) and f"{os.sep}.git{os.sep}" in entry.path:
                    stats.git_tmp.append((size, mtime, entry.path))
                if CORE.match(entry.name) or current.startswith(("/var/crash", "/var/lib/systemd/coredump")):
                    stats.cores.append((size, mtime, entry.path))
        progress(current, stats.files)


def human(size):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:,.0f} {unit}" if unit == "B" else f"{size:,.1f} {unit}"
        size /= 1024


def file_hash(path, limit=None):
    digest = hashlib.blake2b(digest_size=16)
    read = 0
    with open(path, "rb") as fh:
        while True:
            block = fh.read(CHUNK if limit is None else min(CHUNK, limit - read))
            if not block:
                break
            digest.update(block)
            read += len(block)
            if limit is not None and read >= limit:
                break
    return digest.digest()


def find_duplicates(stats, progress):
    """Groups of identical files: equal size, then equal first MiB, then equal full hash."""
    groups = []
    candidates = [(s, p) for s, p in stats.by_size.items() if len(p) > 1]
    for index, (size, paths) in enumerate(sorted(candidates, reverse=True)):
        progress(f"Duplikate: Groesse {index + 1}/{len(candidates)}", 0)
        partial = defaultdict(list)
        for path in paths:
            try:
                partial[file_hash(path, PARTIAL)].append(path)
            except OSError:
                stats.errors += 1
        for same_start in partial.values():
            if len(same_start) < 2:
                continue
            full = defaultdict(list)
            for path in same_start:
                try:
                    full[file_hash(path) if size > PARTIAL else b""].append(path)
                except OSError:
                    stats.errors += 1
            groups.extend((size, group) for group in full.values() if len(group) > 1)
    return groups


def report_orphans(stats, tokens):
    print("\n== A1  Anwendungsordner im Home ohne passende installierte Software ==")
    print("   (Abgleich nach Namen, grob; Treffer = vermutlich zugehoerige Software)")
    rows = sorted(stats.app_size.items(), key=lambda item: item[1], reverse=True)
    unmatched = [(p, s) for p, s in rows if match_installed(os.path.basename(p), tokens) is None]
    for path, size in unmatched[:TOP]:
        newest = datetime.fromtimestamp(stats.app_newest[path]) if stats.app_newest[path] else None
        print(f"  {human(size):>12}  zuletzt {newest:%Y-%m-%d}  {path}" if newest
              else f"  {human(size):>12}  (leer)       {path}")
    print(f"  ({len(unmatched)} ohne Treffer, zusammen {human(sum(s for _, s in unmatched))}; "
          f"{len(rows) - len(unmatched)} mit Treffer)")


def report_duplicates(groups):
    print(f"\n== A2  Doppelte Dateien ab {human(DUP_MIN)} (gleicher Inhalt) ==")
    groups.sort(key=lambda g: g[0] * (len(g[1]) - 1), reverse=True)
    for size, paths in groups[:TOP]:
        print(f"  {human(size):>12} x {len(paths)}  ueberzaehlig {human(size * (len(paths) - 1))}")
        for path in sorted(paths):
            print(f"      {path}")
    wasted = sum(size * (len(paths) - 1) for size, paths in groups)
    print(f"  ({len(groups)} Gruppen, ueberzaehlige Kopien zusammen {human(wasted)})")


def report_list(title, rows):
    print(f"\n== {title} ==")
    for size, mtime, path in sorted(rows, reverse=True)[:TOP]:
        print(f"  {human(size):>12}  {datetime.fromtimestamp(mtime):%Y-%m-%d}  {path}")
    print(f"  ({len(rows)} Dateien, zusammen {human(sum(r[0] for r in rows))})")


def report_artifacts(stats):
    print("\n== A5  Entwicklungsartefakte (je Ordner) ==")
    by_kind = defaultdict(lambda: [0, 0])
    for path, size in stats.artifacts.items():
        kind = os.path.basename(path) if os.path.basename(path) in ARTIFACT_DIRS else "venv (pyvenv.cfg)"
        by_kind[kind][0] += 1
        by_kind[kind][1] += size
    for kind, (count, size) in sorted(by_kind.items(), key=lambda item: item[1][1], reverse=True):
        print(f"  {kind:<20} {count:>6} Ordner  {human(size):>12}")
    print(f"\n  Groesste {TOP}:")
    for path, size in sorted(stats.artifacts.items(), key=lambda item: item[1], reverse=True)[:TOP]:
        print(f"  {human(size):>12}  {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--home", required=True)
    args = parser.parse_args()
    home = os.path.realpath(args.home)
    if not os.path.isdir(home):
        print(f"Kein Verzeichnis: {home}", file=sys.stderr)
        return 2

    stats = Stats()
    last = [0.0]

    def progress(current, files):
        if time.monotonic() - last[0] >= 2:
            last[0] = time.monotonic()
            print(f"\r  {files:>10,} Dateien  {current[:100]:<100}", end="", file=sys.stderr, flush=True)

    started = time.monotonic()
    tokens = survey_installed(home)
    for root in [home] + [r for r in SYSTEM_ROOTS if os.path.isdir(r)]:
        print(f"\nDurchlaufe {root} ...", file=sys.stderr)
        walk_tree(root, home, stats, progress)
    walked = time.monotonic() - started
    print("\nVergleiche Dateien gleicher Groesse ...", file=sys.stderr)
    groups = find_duplicates(stats, progress)
    print(file=sys.stderr)

    print(f"Stand {datetime.now():%Y-%m-%d %H:%M}, {stats.files:,} Dateien, Durchlauf {walked:,.0f} s, "
          f"gesamt {time.monotonic() - started:,.0f} s, {stats.errors} Lesefehler, "
          f"{len(tokens):,} Namen installierter Software")
    report_orphans(stats, tokens)
    report_duplicates(groups)
    report_list("A3  Reste abgebrochener Git-Abrufe", stats.git_tmp)
    report_list("A4  Absturzabbilder", stats.cores)
    report_artifacts(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
