"""Read-only probe: which system-wide statistics are worth showing in table 3.

One single walk over the start directories collects S1-S4 and S6 at once;
S5 asks df and btrfs. The areas already covered by tables 1 and 2
(concept.md, section 4) are skipped and only listed. Nothing is written or
deleted. Sizes are file sizes (st_size), not allocated disk space; hard
links are counted once per link.

Progress goes to stderr (terminal only), results to stdout (for tee).

Usage (as the desktop user, the script itself runs as root):
    sudo nice -n 19 ionice -c3 python3 -I table3_probe.py \
        --home "$HOME" --downloads "$(xdg-user-dir DOWNLOAD)" \
        | tee /tmp/table3_probe.log
"""

import argparse
import os
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime

SYSTEM_ROOTS = ["/var", "/opt", "/usr/local", "/srv"]
LARGE_FILE = 150 * 1024**2
STALE_DAYS = 365
TOP_DIRS = 30
DAY = 86400

GROUPS = {
    "video": "mp4 mkv avi mov wmv flv webm m4v mpg mpeg ts mts m2ts 3gp",
    "audio": "mp3 flac wav ogg oga opus m4a aac wma aiff",
    "image": "jpg jpeg png gif bmp tif tiff webp heic heif raw cr2 nef arw dng svg psd xcf",
    "archive": "zip tar gz tgz xz bz2 7z rar zst lz4",
    "disk image": "img iso qcow2 vdi vmdk vhd vhdx",
    "package": "deb rpm snap flatpak appimage whl",
    "code": "py c h cpp hpp js ts java rs go sh rb php html css json yaml yml toml xml md ipynb",
    "document": "pdf doc docx odt xls xlsx ods ppt pptx odp txt rtf epub",
}
EXT_GROUP = {ext: group for group, exts in GROUPS.items() for ext in exts.split()}


def known_areas(home, downloads):
    """Fixed paths of concept.md section 4 that tables 1 and 2 already cover."""
    return {
        os.path.join(home, ".cache/mozilla/firefox"),
        os.path.join(home, ".cache/google-chrome"),
        os.path.join(home, ".cache/pip"),
        os.path.join(home, ".config/Code/Cache"),
        os.path.join(home, ".config/Code/CachedData"),
        os.path.join(home, ".config/Code/CachedExtensionVSIXs"),
        os.path.realpath(downloads),
        "/var/cache/apt/archives",
        "/var/log",
    }


def is_known_dir(path, name, home, areas):
    """True for a directory covered by section 4 (fixed paths and name patterns)."""
    if path in areas:
        return True
    if name in ("cache2", "startupCache") and path.startswith(os.path.join(home, ".mozilla/firefox/")):
        return True
    if name == "CacheStorage" and path.startswith(os.path.join(home, ".config/Code/WebStorage/")):
        return True
    return name in ("log", "logs") and path.startswith(home + "/")


def file_group(name):
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    return EXT_GROUP.get(ext, "other")


def human(size):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:,.0f} {unit}" if unit == "B" else f"{size:,.1f} {unit}"
        size /= 1024


class Stats:
    def __init__(self, now):
        self.now = now
        self.dir_size = defaultdict(int)       # S1: (root, rel parts up to depth 3) -> bytes
        self.large = []                        # S2: (size, mtime, group, path)
        self.growth = defaultdict(lambda: [0, 0])  # S3: top dir -> [7 days, 30 days]
        self.stale = defaultdict(int)          # S4: top dir -> bytes
        self.types = defaultdict(lambda: [0, 0])   # S6: group -> [files, bytes]
        self.skipped_known = []
        self.skipped_mounts = []
        self.errors = 0
        self.files = 0


def walk_tree(root, home, areas, stats, progress):
    """Single pass over one start directory, staying on its device."""
    try:
        device = os.stat(root).st_dev
    except OSError:
        return
    stack = [root]
    while stack:
        current = stack.pop()
        rel = os.path.relpath(current, root)
        parts = () if rel == "." else tuple(rel.split(os.sep))
        top = os.path.join(root, parts[0]) if parts else root
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
                        path = entry.path
                        if is_known_dir(path, entry.name, home, areas):
                            stats.skipped_known.append(path)
                        elif entry.stat(follow_symlinks=False).st_dev != device:
                            stats.skipped_mounts.append(path)
                        else:
                            stack.append(path)
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        continue
                    if root == home and ".log" in entry.name:
                        continue  # log files in the home: section 4.5
                    st = entry.stat(follow_symlinks=False)
                except OSError:
                    stats.errors += 1
                    continue
                size, mtime = st.st_size, st.st_mtime
                stats.files += 1
                for depth in range(1, min(len(parts), 3) + 1):
                    stats.dir_size[(root, parts[:depth])] += size
                if not parts:
                    stats.dir_size[(root, ())] += size
                group = file_group(entry.name)
                if size >= LARGE_FILE:
                    stats.large.append((size, mtime, group, entry.path))
                age = stats.now - mtime
                file_top = top if parts else entry.path
                if age <= 7 * DAY:
                    stats.growth[file_top][0] += size
                if age <= 30 * DAY:
                    stats.growth[file_top][1] += size
                if age > STALE_DAYS * DAY:
                    stats.stale[file_top] += size
                stats.types[group][0] += 1
                stats.types[group][1] += size
        progress(current, stats.files)


def mark(path, home):
    return path + ("   [git]" if path.startswith(os.path.join(home, "git")) else "")


def report_sizes(stats, roots, home):
    print("\n== S1  Groesse je Verzeichnis (ohne Bereiche aus Abschnitt 4) ==")
    for root in roots:
        total = sum(s for (r, p), s in stats.dir_size.items() if r == root and len(p) <= 1)
        print(f"\n{root}   gesamt {human(total)}")
        level1 = sorted(((s, p) for (r, p), s in stats.dir_size.items() if r == root and len(p) == 1),
                        reverse=True)
        for size, parts in level1[:TOP_DIRS]:
            print(f"  {human(size):>12}  {mark(os.path.join(root, *parts), home)}")
    deeper = sorted(((s, r, p) for (r, p), s in stats.dir_size.items() if len(p) in (2, 3)), reverse=True)
    print(f"\nGroesste {TOP_DIRS} Verzeichnisse der Tiefe 2 und 3:")
    for size, root, parts in deeper[:TOP_DIRS]:
        print(f"  {human(size):>12}  T{len(parts)}  {mark(os.path.join(root, *parts), home)}")


def report_large_files(stats, home):
    print(f"\n== S2  Einzeldateien ab {human(LARGE_FILE)} ==")
    for size, mtime, group, path in sorted(stats.large, reverse=True):
        print(f"  {human(size):>12}  {datetime.fromtimestamp(mtime):%Y-%m-%d}  {group:<11} {mark(path, home)}")
    print(f"  ({len(stats.large)} Dateien, zusammen {human(sum(e[0] for e in stats.large))})")


def report_growth(stats, home):
    print("\n== S3  Zuwachs: geaendert in den letzten 7 / 30 Tagen, je Verzeichnis der obersten Ebene ==")
    rows = sorted(stats.growth.items(), key=lambda item: item[1][1], reverse=True)
    for path, (week, month) in rows[:TOP_DIRS]:
        print(f"  {human(week):>12}  {human(month):>12}  {mark(path, home)}")


def report_stale(stats, home):
    print(f"\n== S4  Seit ueber {STALE_DAYS} Tagen unveraendert, je Verzeichnis der obersten Ebene ==")
    rows = sorted(stats.stale.items(), key=lambda item: item[1], reverse=True)
    for path, size in rows[:TOP_DIRS]:
        print(f"  {human(size):>12}  {mark(path, home)}")


def report_types(stats):
    print("\n== S6  Datenmenge je Dateiart ==")
    for group, (count, size) in sorted(stats.types.items(), key=lambda item: item[1][1], reverse=True):
        print(f"  {group:<11} {count:>10,} Dateien  {human(size):>12}")


def run(cmd):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return done.stdout if done.returncode == 0 else None


def report_filesystems():
    print("\n== S5  Belegung je Dateisystem und btrfs-Snapshots ==")
    out = run(["df", "-B1", "--output=source,fstype,size,used,target",
               "-x", "tmpfs", "-x", "devtmpfs", "-x", "squashfs", "-x", "overlay", "-x", "efivarfs"])
    btrfs_mounts = {}
    for line in (out or "").splitlines()[1:]:
        source, fstype, size, used, target = line.split(None, 4)
        print(f"  {fstype:<6} {human(int(used)):>12} von {human(int(size)):>12}  {target}  ({source})")
        if fstype == "btrfs":
            btrfs_mounts.setdefault(source, target)
    for source, target in btrfs_mounts.items():
        listing = run(["btrfs", "subvolume", "list", "-s", target])
        if listing is None:
            print(f"  {target}: Snapshots nicht ermittelbar (btrfs-Werkzeug fehlt oder keine Rechte)")
            continue
        ids = {line.split()[1] for line in listing.splitlines() if line.startswith("ID ")}
        qgroups = run(["btrfs", "qgroup", "show", "--raw", target])
        if qgroups is None:
            print(f"  {target}: {len(ids)} Snapshots, Belegung nicht ermittelbar (Quotas nicht aktiv)")
            continue
        exclusive = 0
        for line in qgroups.splitlines():
            fields = line.split()
            if len(fields) >= 3 and fields[0].startswith("0/") and fields[0][2:] in ids:
                exclusive += int(fields[2])
        print(f"  {target}: {len(ids)} Snapshots, exklusiv belegt {human(exclusive)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--home", required=True)
    parser.add_argument("--downloads", required=True)
    args = parser.parse_args()
    home = os.path.realpath(args.home)
    for path in (home, args.downloads):
        if not os.path.isdir(path):
            print(f"Kein Verzeichnis: {path}", file=sys.stderr)
            return 2

    areas = known_areas(home, args.downloads)
    stats = Stats(time.time())
    last = [0.0]

    def progress(current, files):
        if time.monotonic() - last[0] >= 2:
            last[0] = time.monotonic()
            print(f"\r  {files:>10,} Dateien  {current[:100]:<100}", end="", file=sys.stderr, flush=True)

    roots = [home] + [r for r in SYSTEM_ROOTS if os.path.isdir(r)]
    started = time.monotonic()
    for root in roots:
        print(f"\nDurchlaufe {root} ...", file=sys.stderr)
        walk_tree(root, home, areas, stats, progress)
    print(file=sys.stderr)

    print(f"Stand {datetime.now():%Y-%m-%d %H:%M}, {stats.files:,} Dateien in "
          f"{time.monotonic() - started:,.0f} s, {stats.errors} Lesefehler")
    report_sizes(stats, roots, home)
    report_large_files(stats, home)
    report_growth(stats, home)
    report_stale(stats, home)
    report_filesystems()
    report_types(stats)
    print("\n== Uebersprungen: Bereiche aus Abschnitt 4 ==")
    for path in sorted(stats.skipped_known):
        print(f"  {path}")
    print("\n== Uebersprungen: andere Dateisysteme oder Subvolumes ==")
    for path in sorted(stats.skipped_mounts):
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
