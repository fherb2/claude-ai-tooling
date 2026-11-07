"""Test of snapshots.py without btrfs: the btrfs commands are replaced by canned answers.

Checks parsing, the prefix and path rules, dry runs, the commands that would be
issued, and the selective restore on real throwaway folders (real cp, no btrfs).
It does not prove that btrfs accepts the commands; that is tried on a real
file system (work-plan.md, step 22). Needs no root.

Usage: python3 -I tests/test_snapshots.py
"""

import importlib.util
import json
import os
import shutil
import stat
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = ("@x\n\tName: \t\t\t@x\n\tSubvolume ID: \t\t{id}\n\tCreation time: \t\t2026-11-07 10:00:00 +0000\n"
        "\tFlags: \t\t\t{flags}\n")


def load():
    spec = importlib.util.spec_from_file_location("snapshots", os.path.join(HERE, "..", "snapshots.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Fake:
    """run() with canned answers: key = command tuple -> (code, out, err); a function value may have side effects."""

    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def __call__(self, cmd, timeout=120):
        self.calls.append(tuple(cmd))
        answer = self.answers.get(tuple(cmd), (1, "", "unknown command"))
        return answer() if callable(answer) else answer


def main():
    s = load()
    problems = []
    check = lambda label, cond: problems.append(label) if not cond else None
    base = tempfile.mkdtemp(prefix="cleanup-snaptest-", dir="/tmp")
    real_run = s.run
    P = s.PREFIX

    # 1 parsing
    lines = ["36 25 0:30 /@ / rw,relatime shared:1 - btrfs /dev/nvme0n1p8 rw,ssd,subvolid=256,subvol=/@",
             "40 25 0:31 / /home rw - btrfs /dev/nvme0n1p9 rw,subvolid=5,subvol=/",
             "41 25 8:1 / /boot ro - ext4 /dev/sda1 rw",
             "42 25 0:32 /@x /mnt/my\\040disk rw - btrfs /dev/sdb1 rw,subvol=/@x"]
    mounts = s.parse_mountinfo(lines)
    check("mountinfo: btrfs only", [m["mount"] for m in mounts] == ["/", "/home", "/mnt/my disk"])
    check("mountinfo: subvolume path", mounts[0]["subvolume"] == "/@" and mounts[1]["subvolume"] == "/")
    info = s.parse_show(SHOW.format(id=301, flags="readonly"))
    check("show: fields", info == {"id": "301", "created": "2026-11-07 10:00:00 +0000", "readonly": True})
    check("show: not read-only", s.parse_show(SHOW.format(id=1, flags="-"))["readonly"] is False)
    check("qgroup: exclusive per id", s.parse_qgroups("qgroupid rfer excl\n0/301 10 4096\n0/5 1 1\n1/0 3 3\n") == {"301": 4096, "5": 1})

    # 2 names and labels
    name = s.make_name("before-clean", datetime(2026, 11, 7, 10, 30, 5))
    check("name format", name == f"{P}20261107-103005-before-clean")
    for bad in ("Upper", "with space", "-lead", "", "x" * 41, "ä"):
        try:
            s.make_name(bad)
            problems.append(f"label accepted: {bad!r}")
        except ValueError:
            pass

    # 3 create
    mount = os.path.join(base, "mnt")
    os.makedirs(mount)
    mnt = [{"mount": mount, "device": "/dev/x", "subvolume": "/"}]
    now = datetime(2026, 11, 7, 10, 30, 5)
    dest = os.path.join(mount, s.BASE_NAME, f"{P}20261107-103005-t")
    answers = {("btrfs", "subvolume", "show", mount): (0, SHOW.format(id=5, flags="-"), ""),
               ("btrfs", "subvolume", "snapshot", "-r", mount, dest): (0, "", ""),
               ("btrfs", "subvolume", "show", dest): (0, SHOW.format(id=301, flags="readonly"), "")}
    s.run = Fake(answers)
    r = s.do_create(mnt, mount, "t", None, True, now)
    check("create dry run: ok, command named", r["ok"] and r["command"] == f"btrfs subvolume snapshot -r {mount} {dest}")
    check("create dry run: nothing made", not os.path.exists(os.path.join(mount, s.BASE_NAME)))
    check("create dry run: only the show call", s.run.calls == [("btrfs", "subvolume", "show", mount)])
    r = s.do_create(mnt, mount, "t", None, False, now)
    check("create: ok and read-only verified", r["ok"] and r["readonly"] is True and r["subvolume_id"] == "301")
    check("create: container folder is private", stat.S_IMODE(os.stat(os.path.join(mount, s.BASE_NAME)).st_mode) == 0o700)
    s.run = Fake(answers)
    os.makedirs(dest)
    check("create: refuses an existing snapshot", not s.do_create(mnt, mount, "t", None, False, now)["ok"])
    shutil.rmtree(os.path.join(mount, s.BASE_NAME))
    check("create: not a btrfs mount", not s.do_create(mnt, "/tmp", "t", None, True, now)["ok"])
    check("create: invalid label", not s.do_create(mnt, mount, "Bad Label", None, True, now)["ok"])
    check("create: folder outside the mount", not s.do_create(mnt, mount, "t", "/tmp/elsewhere", True, now)["ok"])
    answers[("btrfs", "subvolume", "show", dest)] = (0, SHOW.format(id=301, flags="-"), "")
    s.run = Fake(answers)
    r = s.do_create(mnt, mount, "t", None, False, now)
    check("create: not read-only is reported", r["ok"] is False and "read-only" in r["error"])
    shutil.rmtree(os.path.join(mount, s.BASE_NAME))
    s.run = Fake({("btrfs", "subvolume", "show", mount): (1, "", "not a subvolume")})
    check("create: no subvolume at the mount point", not s.do_create(mnt, mount, "t", None, True, now)["ok"])

    # 4 list
    folder = os.path.join(mount, s.BASE_NAME)
    one, two = os.path.join(folder, f"{P}a"), os.path.join(folder, f"{P}b")
    foreign = os.path.join(folder, "timeshift-x")
    for d in (one, two, foreign):
        os.makedirs(d)
    open(os.path.join(folder, f"{P}file"), "w").close()
    s.run = Fake({("btrfs", "subvolume", "show", one): (0, SHOW.format(id=301, flags="readonly"), ""),
                  ("btrfs", "subvolume", "show", two): (0, SHOW.format(id=302, flags="readonly"), ""),
                  ("btrfs", "qgroup", "show", "--raw", mount): (0, "qgroupid rfer excl\n0/301 10 4096\n", "")})
    snaps = s.list_snapshots(mnt)
    check("list: own prefixed subvolumes only", [x["name"] for x in snaps] == [f"{P}a", f"{P}b"])
    check("list: exclusive bytes when known", snaps[0]["exclusive_bytes"] == 4096 and snaps[1]["exclusive_bytes"] is None)
    s.run = Fake({("btrfs", "subvolume", "show", one): (0, SHOW.format(id=301, flags="readonly"), ""),
                  ("btrfs", "qgroup", "show", "--raw", mount): (1, "", "quotas not enabled")})
    check("list: quotas off -> None", s.list_snapshots(mnt)[0]["exclusive_bytes"] is None)

    # 5 remove
    delete = ("btrfs", "subvolume", "delete", "--commit-after", one)
    fake = Fake({("btrfs", "subvolume", "show", one): (0, SHOW.format(id=301, flags="readonly"), ""),
                 delete: lambda: (shutil.rmtree(one), (0, "", ""))[1]})
    s.run = fake
    check("remove: refuses a name without the prefix", "prefix" in s.do_remove(mnt, "timeshift-x", [], False)["error"])
    check("remove: refuses a foreign path", "prefix" in s.do_remove(mnt, foreign, [], False)["error"])
    check("remove: unknown name", not s.do_remove(mnt, f"{P}nothere", [], False)["ok"])
    r = s.do_remove(mnt, f"{P}a", [], True)
    check("remove dry run: nothing deleted", r["ok"] and delete not in fake.calls and os.path.isdir(one))
    r = s.do_remove(mnt, f"{P}a", [], False)
    check("remove: command and result", r["ok"] and r["removed"] and delete in fake.calls)
    check("remove: container stays while others remain", r["container_removed"] is False and os.path.isdir(folder))

    mount2 = os.path.join(base, "mnt2")
    folder2 = os.path.join(mount2, s.BASE_NAME)
    single = os.path.join(folder2, f"{P}only")
    os.makedirs(single)
    mnt2 = [{"mount": mount2, "device": "/dev/y", "subvolume": "/"}]
    delete2 = ("btrfs", "subvolume", "delete", "--commit-after", single)
    s.run = Fake({("btrfs", "subvolume", "show", single): (0, SHOW.format(id=9, flags="readonly"), ""),
                  delete2: lambda: (shutil.rmtree(single), (0, "", ""))[1]})
    r = s.do_remove(mnt2, f"{P}only", [], True)
    check("remove dry run: announces the container removal", r["ok"] and r["container_removed"] is True and os.path.isdir(folder2))
    r = s.do_remove(mnt2, f"{P}only", [], False)
    check("remove: empty container folder goes with its last snapshot", r["ok"] and r["container_removed"] and not os.path.exists(folder2))
    fake = Fake({("btrfs", "subvolume", "show", two): (0, SHOW.format(id=302, flags="readonly"), ""),
                 ("btrfs", "subvolume", "delete", "--commit-after", two): (1, "", "permission denied")})
    s.run = fake
    check("remove: failing btrfs", not s.do_remove(mnt, two, [], False)["ok"] and os.path.isdir(two))

    # 6 selective restore on real folders (real cp)
    s.run = real_run
    snap = os.path.join(base, "snap")
    live = os.path.join(base, "live")
    for root in (snap, live):
        os.makedirs(root)
    def put(root, rel, text, mode=None):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(text)
        if mode:
            os.chmod(path, mode)
    put(snap, "dirA/file1", "from snapshot")
    put(snap, "dirA/sub/file2", "deep", 0o640)
    put(snap, "dirB/deep/file3", "gone entirely")
    put(snap, "single.txt", "one file")
    os.symlink("single.txt", os.path.join(snap, "dirA/link"))
    os.utime(os.path.join(snap, "dirB/deep/file3"), (1_000_000_000, 1_000_000_000))
    put(live, "dirA/file1", "live version")
    entry = {"name": f"{P}x", "path": snap, "mount": live}

    for bad in ("", ".", "..", "../x", "/etc", f"dirA/{P}y", s.BASE_NAME):
        check(f"restore: refused path {bad!r}", s.do_restore(entry, bad, False)["ok"] is False)
    check("restore: not in the snapshot", s.do_restore(entry, "nothere", False)["ok"] is False)
    r = s.do_restore(entry, "dirA", True)
    check("restore dry run: counts what is missing", r["ok"] and r["missing"]["items"] == 2
          and not os.path.exists(os.path.join(live, "dirA/sub")))
    r = s.do_restore(entry, "dirA", False)
    check("restore: folder restored", r["ok"] and open(os.path.join(live, "dirA/sub/file2")).read() == "deep")
    check("restore: nothing overwritten", open(os.path.join(live, "dirA/file1")).read() == "live version")
    check("restore: mode kept", stat.S_IMODE(os.stat(os.path.join(live, "dirA/sub/file2")).st_mode) == 0o640)
    check("restore: link kept as link", os.path.islink(os.path.join(live, "dirA/link")))
    check("restore: second run finds nothing", s.do_restore(entry, "dirA", False)["missing"]["items"] == 0)
    r = s.do_restore(entry, "dirB/deep", False)
    check("restore: missing parents created", r["ok"] and open(os.path.join(live, "dirB/deep/file3")).read() == "gone entirely")
    check("restore: times kept", int(os.stat(os.path.join(live, "dirB/deep/file3")).st_mtime) == 1_000_000_000)
    r = s.do_restore(entry, "single.txt", False)
    check("restore: single file", r["ok"] and open(os.path.join(live, "single.txt")).read() == "one file")

    # 7 command line
    s.btrfs_mounts = lambda: mnt
    s.run = Fake({})
    report = os.path.join(base, "r.json")
    code = s.main(["remove", "--name", "timeshift-x", "--report", report])
    check("main: refusal gives exit 1 and a report", code == 1 and json.load(open(report))["ok"] is False)
    code = s.main(["list", "--report", report])
    check("main: list ok", code == 0 and json.load(open(report))["prefix"] == P)

    shutil.rmtree(base)
    if problems:
        print(f"FAILED ({len(problems)}):")
        for p in problems:
            print("  " + p)
        return 1
    print("PASSED: parsing, names, create, list, remove, selective restore and command line checked without btrfs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
