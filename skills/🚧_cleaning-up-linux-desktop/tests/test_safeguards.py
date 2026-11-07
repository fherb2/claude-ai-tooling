"""Test of the safeguard detection in analyze.py against reproduced command outputs.

No real btrfs, ZFS or LVM is needed: the commands are replaced by canned
outputs. This checks the parsing and the structure of the result, not the
real systems. ZFS and LVM are marked tested: false in the result for that reason.

Usage: python3 -I tests/test_safeguards.py
"""

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PREFIX = "cleaning-up-linux-desktop-"


def load():
    spec = importlib.util.spec_from_file_location("analyze", os.path.join(HERE, "..", "analyze.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mount(path, source, fstype, avail=1000):
    return {"mount": path, "source": source, "fstype": fstype, "size": 5000, "used": 4000, "avail": avail}


class Fake:
    """Replaces run() with canned outputs keyed by the command tuple; a missing key means 'command failed'."""

    def __init__(self, outputs):
        self.outputs, self.calls = outputs, []

    def __call__(self, cmd, timeout=30):
        self.calls.append(tuple(cmd))
        return self.outputs.get(tuple(cmd))


def main():
    a = load()
    problems = []

    def check(label, condition):
        if not condition:
            problems.append(label)

    # 1 btrfs: two devices, snapshots incl. own and foreign ones, subvolume at the mount point
    show = ("@home\n\tName: \t\t\t@home\n\tUUID: \t\t\tabc\n\tSubvolume ID: \t\t257\n\tFlags: \t\t\t-\n")
    fake = Fake({
        ("btrfs", "subvolume", "list", "-s", "/"): (
            "ID 300 gen 9 cgen 9 top level 5 otime 2026-11-01 10:00:00 path @snapshots/timeshift-x\n"
            f"ID 301 gen 9 cgen 9 top level 5 otime 2026-11-02 10:00:00 path @snapshots/{PREFIX}20261102-1000-root\n"),
        ("btrfs", "subvolume", "list", "-s", "/home"): "",
        ("btrfs", "subvolume", "show", "/home"): show,
    })
    a.run = fake
    mounts = [mount("/", "/dev/nvme0n1p8", "btrfs"), mount("/swap", "/dev/nvme0n1p8", "btrfs"),
              mount("/home", "/dev/nvme0n1p9", "btrfs"), mount("/boot/efi", "/dev/nvme0n1p1", "vfat")]
    found = a.detect_btrfs(mounts)
    check("btrfs: one entry per device", len(found) == 2)
    root = next(f for f in found if f["device"] == "/dev/nvme0n1p8")
    home = next(f for f in found if f["device"] == "/dev/nvme0n1p9")
    check("btrfs: both mounts of one device", [m["mount"] for m in root["mounts"]] == ["/", "/swap"])
    check("btrfs: two snapshots counted, one own", root["snapshots"]["count"] == 2
          and root["snapshots"]["ours"] == [f"@snapshots/{PREFIX}20261102-1000-root"])
    check("btrfs: no snapshots listed as empty", home["snapshots"] == {"listed": True, "count": 0, "ours": []})
    check("btrfs: subvolume parsed", home["mounts"][0]["subvolume"] == {"name": "@home", "id": "257"})
    check("btrfs: subvolume missing -> None", root["mounts"][0]["subvolume"] is None)
    check("btrfs: tested flag", root["tested"] is True)

    # 2 btrfs without root: the commands fail
    a.run = Fake({})
    found = a.detect_btrfs(mounts)
    check("btrfs without root: listed false", all(f["snapshots"]["listed"] is False for f in found))

    # 3 ZFS
    a.run = Fake({("zfs", "list", "-H", "-t", "snapshot", "-o", "name"):
                  f"rpool/ROOT/ubuntu@old\nrpool/ROOT/ubuntu@{PREFIX}20261102\nrpool/USERDATA/u@x\n"})
    found = a.detect_zfs([mount("/", "rpool/ROOT/ubuntu", "zfs"), mount("/home", "rpool/USERDATA/u", "zfs")])
    root = next(f for f in found if f["device"] == "rpool/ROOT/ubuntu")
    check("zfs: snapshots of the dataset only", root["snapshots"]["count"] == 2
          and root["snapshots"]["ours"] == [f"rpool/ROOT/ubuntu@{PREFIX}20261102"])
    check("zfs: tested false", all(f["tested"] is False for f in found))
    check("zfs: none without zfs mounts", a.detect_zfs([mount("/", "/dev/sda1", "ext4")]) == [])

    # 4 LVM
    lvs_cmd = ("lvs", "--noheadings", "--separator", "|", "--units", "b", "--nosuffix", "-o",
               "lv_name,vg_name,lv_attr,origin,lv_size,vg_free,lv_path")
    a.run = Fake({lvs_cmd: ("  root|vg0|owi-aos---||50000|7000|/dev/vg0/root\n"
                            f"  {PREFIX}x|vg0|swi-a-s---|root|1000|7000|/dev/vg0/{PREFIX}x\n"
                            "  other|vg0|swi-a-s---|root|1000|7000|/dev/vg0/other\n"
                            "  data|vg0|-wi-ao----||9000|7000|/dev/vg0/data\n")})
    real = a.os.path.realpath
    a.os.path.realpath = lambda p: "/dev/dm-0" if p in ("/dev/mapper/vg0-root", "/dev/vg0/root") else real(p)
    a.shutil.which = lambda name: "/usr/sbin/" + name
    found = a.detect_lvm([mount("/", "/dev/mapper/vg0-root", "ext4"), mount("/boot", "/dev/sda1", "ext4")])
    a.os.path.realpath = real
    check("lvm: only the mount below a logical volume", len(found) == 1 and found[0]["mounts"][0]["volume"] == "root")
    check("lvm: snapshot volumes by origin", found[0]["snapshots"]["count"] == 2
          and found[0]["snapshots"]["ours"] == [f"{PREFIX}x"])
    check("lvm: free space of the group", found[0]["mounts"][0]["vg_free"] == 7000)
    check("lvm: tested false", found[0]["tested"] is False)
    a.run = Fake({})
    check("lvm: failing lvs -> nothing", a.detect_lvm([mount("/", "/dev/mapper/vg0-root", "ext4")]) == [])

    # 5 tools
    a.shutil.which = lambda name: "/usr/bin/" + name if name == "timeshift" else None
    exists, isdir, listdir = a.os.path.exists, a.os.path.isdir, a.os.listdir
    a.os.path.exists = lambda p: True if p == "/etc/timeshift/timeshift.json" else exists(p)
    a.os.path.isdir = lambda p: False if p == "/etc/timeshift/timeshift.json" else isdir(p)
    tools = a.detect_tools()
    a.os.path.exists, a.os.path.isdir, a.os.listdir = exists, isdir, listdir
    check("tools: timeshift installed and configured", tools["timeshift"] == {"installed": True, "configured": True})
    check("tools: snapper missing", tools["snapper"] == {"installed": False, "configured": False})

    # 6 nothing to offer, and the whole result is JSON
    a.run = Fake({})
    a.shutil.which = lambda name: None
    result = a.safeguards([mount("/", "/dev/sda1", "ext4")])
    check("nothing: no file system offered", result["filesystems"] == [])
    check("prefix in the result", result["prefix"] == PREFIX)
    json.dumps(result)

    # 7 timeout of a hanging command
    check("run: timeout returns None", load().run(["sleep", "5"], timeout=1) is None)
    check("run: missing command returns None", load().run(["no-such-command-xyz"]) is None)

    # 8 filesystems(): avail is added
    b = load()
    b.run = Fake({("df", "-B1", "--output=source,fstype,size,used,target", "-x", "tmpfs", "-x", "devtmpfs",
                   "-x", "squashfs", "-x", "overlay", "-x", "efivarfs"):
                  "Filesystem Type 1B-blocks Used Mounted on\n/dev/sda1 ext4 1000 400 /\n"})
    rows = b.filesystems()["mounts"]
    check("filesystems: avail added", rows and isinstance(rows[0]["avail"], int))

    if problems:
        print(f"FAILED ({len(problems)}):")
        for p in problems:
            print("  " + p)
        return 1
    print("PASSED: btrfs, ZFS, LVM, tools, nothing-to-offer, timeout and avail checked on reproduced outputs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
