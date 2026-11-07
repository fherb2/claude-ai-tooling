"""Test of backup.py on a throwaway tree under /tmp: real tar, gzip and zip, real restore.

Needs no root and no special file system. The free space of the target is
replaced by a fixed value, so the test does not depend on the disk it runs on.
Checks creation, naming, verification (including a deliberately broken file and
a truncated archive), the space rule, the refusals, selective restore without
overwriting, listing and removal.

Usage: python3 -I tests/test_backup.py
"""

import argparse
import importlib.util
import json
import os
import shutil
import stat
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
GIB = 1024**3


def load():
    spec = importlib.util.spec_from_file_location("backup", os.path.join(HERE, "..", "backup.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(text if isinstance(text, bytes) else text.encode())
    if mode:
        os.chmod(path, mode)


def read(path):
    with open(path, "rb") as fh:
        return fh.read()


def main():
    b = load()
    problems = []
    check = lambda label, cond: problems.append(label) if not cond else None
    base = tempfile.mkdtemp(prefix="cleanup-backuptest-", dir="/tmp")
    data, out = os.path.join(base, "data"), os.path.join(base, "out")
    os.makedirs(out)
    b.free_space = lambda target: (1000 * GIB, 900 * GIB)

    # the tree to back up
    write(f"{data}/a.txt", "alpha", 0o640)
    write(f"{data}/media/v.mp4", os.urandom(50_000))
    write(f"{data}/docs/b.txt", "bravo")
    write(f"{data}/docs/sub/c.txt", "charlie", 0o750)
    os.makedirs(f"{data}/empty")
    os.symlink("b.txt", f"{data}/docs/link")
    os.link(f"{data}/docs/b.txt", f"{data}/docs/hard")
    with open(f"{data}/sparse.img", "wb") as fh:
        fh.truncate(8_000_000)
        fh.seek(7_999_999)
        fh.write(b"x")
    os.utime(f"{data}/docs/sub/c.txt", (631_152_000, 631_152_000))          # 1990
    xattr_ok = True
    try:
        os.setxattr(f"{data}/a.txt", "user.test", b"value")
    except OSError:
        xattr_ok = False
    listing = os.path.join(base, "list.json")
    report_like = os.path.join(base, "report.json")
    json.dump({"paths": [f"{data}/docs", f"{data}/docs/sub", f"{data}/a.txt", f"{data}/media",
                         f"{data}/empty", f"{data}/sparse.img"]}, open(listing, "w"))

    def ns(**kw):
        values = dict(list=listing, target=out, step="test", format="tar", run=None, reserve_percent=None,
                      reserve_gib=None, verify="full", dry_run=False)
        values.update(kw)
        return argparse.Namespace(**values)

    json.dump({"candidates": [f"{data}/a.txt"], "removed_count": 1}, open(report_like, "w"))
    check("list file: the report of delete.py is accepted", b.load_paths(report_like) == [f"{data}/a.txt"])

    # 1 validation
    write(f"{data}/cleaning-up-linux-desktop-x", "own")
    clean, errors = b.validate([f"{data}/docs", f"{data}/docs/sub", f"{data}/a.txt", "relative/x", f"{base}/missing",
                                f"{data}/cleaning-up-linux-desktop-x", out, f"{out}/inside"], out)
    check("validate: nested path dropped, clean ones kept", clean == [f"{data}/a.txt", f"{data}/docs"])
    reasons = {e["path"]: e["reason"] for e in errors}
    check("validate: relative, missing, own prefix, target inside",
          reasons.get("relative/x") == "not a clean absolute path" and reasons.get(f"{base}/missing") == "does not exist"
          and "prefix" in reasons.get(f"{data}/cleaning-up-linux-desktop-x", "") and "target folder" in reasons.get(out, ""))

    # 2 the space rule
    ok = lambda size, avail, req, **kw: b.space_check(size * GIB, avail * GIB, req * GIB, **kw)
    check("space: default reserve 10 GiB on a small disk", ok(100, 30, 20)["ok"] and not ok(100, 30, 20.1)["ok"])
    check("space: default reserve 10 % on a big disk", ok(1000, 150, 50)["ok"] and not ok(1000, 150, 51)["ok"])
    low = ok(1000, 150, 101, percent=1, gib=1)
    check("space: user may lower it, never below 5 % / 5 GiB", low["clamped"] and low["reserve"] == 50 * GIB and not low["ok"]
          and ok(1000, 150, 100, percent=1, gib=1)["ok"])
    check("space: small floor is 5 GiB", ok(10, 8, 2, percent=0, gib=0)["reserve"] == 5 * GIB)

    # 3 create: tar, zip, tar.gz in one run
    r1 = b.do_create(ns())
    check("tar: ok and named 01-test.tar", r1["ok"] and r1["archive"].endswith("/01-test.tar") and os.path.isfile(r1["archive"]))
    check("tar: verified by comparison", r1["verify"]["mode"] == "full" and r1["verify"]["ok"])
    check("tar: private files and folder", stat.S_IMODE(os.stat(r1["archive"]).st_mode) == 0o600
          and stat.S_IMODE(os.stat(os.path.dirname(r1["archive"])).st_mode) == 0o700)
    check("plan: overhead estimate added to the required space", r1["plan"]["overhead_estimate"] >= 2048 * 6
          and r1["space"]["required"] == r1["plan"]["bytes"] + r1["plan"]["overhead_estimate"])
    check("tar: plan counted", r1["plan"]["files"] >= 6 and r1["plan"]["links"] == 1 and r1["plan"]["bytes"] > 50_000)
    run = r1["run"]
    r2 = b.do_create(ns(format="zip", step="z", run=run))
    check("zip: same run, number 02", r2["ok"] and r2["archive"].endswith("/02-z.zip") and r2["run"] == run)
    r3 = b.do_create(ns(format="tar.gz", step="g", run=run, verify="quick"))
    check("tar.gz: gzip data, quick check", r3["ok"] and read(r3["archive"])[:2] == b"\x1f\x8b" and r3["verify"]["mode"] == "quick")
    check("no .part files left", not [n for n in os.listdir(os.path.dirname(r1["archive"])) if n.endswith(".part")])
    with zipfile.ZipFile(r2["archive"]) as zf:
        by_name = {i.filename: i for i in zf.infolist()}
        mp4 = by_name[f"02-z{data}/media/v.mp4"]
        txt = by_name[f"02-z{data}/docs/b.txt"]
        link = by_name[f"02-z{data}/docs/link"]
        check("zip: media stored, text deflated", mp4.compress_type == zipfile.ZIP_STORED and txt.compress_type == zipfile.ZIP_DEFLATED)
        check("zip: link kept as link, empty folder kept", stat.S_ISLNK(link.external_attr >> 16)
              and f"02-z{data}/empty/" in by_name)

    # 4 a dry run writes nothing, a lack of space refuses
    before = sorted(os.listdir(os.path.dirname(r1["archive"])))
    dry = b.do_create(ns(dry_run=True, step="dry", run=run))
    check("dry run: plan and verdict, nothing written", dry["ok"] and sorted(os.listdir(os.path.dirname(r1["archive"]))) == before)
    b.free_space = lambda target: (100 * GIB, 8 * GIB)
    refused = b.do_create(ns(step="nospace", run=run))
    b.free_space = lambda target: (1000 * GIB, 900 * GIB)
    check("no space: refused and nothing written", not refused["ok"] and "free space" in refused["error"]
          and sorted(os.listdir(os.path.dirname(r1["archive"]))) == before)
    check("refused list entry: no backup", not b.do_create(ns(list=json.dump({"paths": ["relative"]}, open(listing + "2", "w")) or listing + "2"))["ok"])
    check("invalid step name", not b.do_create(ns(step="Bad Name"))["ok"])

    # 5 verification notices damage
    entries, skipped = b.walk_entries(b.validate(json.load(open(listing))["paths"], out)[0], b.mount_points())
    write(f"{data}/docs/b.txt", "BRAVO")
    check("tar: a changed file fails the comparison", not b.verify_tar(r1["archive"], entries, "full", False)["ok"])
    check("zip: a changed file fails the comparison", not b.verify_zip(r2["archive"], entries, "full", 2, "z")["ok"])
    check("zip: quick check does not compare content", b.verify_zip(r2["archive"], entries, "quick", 2, "z")["ok"])
    write(f"{data}/docs/b.txt", "bravo")
    cut = os.path.join(base, "cut.tar")
    shutil.copy(r1["archive"], cut)
    os.truncate(cut, os.path.getsize(cut) // 3)
    check("tar: a truncated archive fails the quick check", not b.verify_tar(cut, entries, "quick", False)["ok"])
    real_verify = b.verify_tar
    b.verify_tar = lambda *a, **k: {"mode": "full", "ok": False, "details": ["simulated"]}
    failed = b.do_create(ns(step="bad", run=run))
    b.verify_tar = real_verify
    check("failed verification: error and no archive", not failed["ok"] and not any("bad" in n for n in os.listdir(os.path.dirname(r1["archive"]))))

    # 6 selective restore from tar and from zip
    def damage():
        shutil.rmtree(f"{data}/docs/sub")
        os.unlink(f"{data}/a.txt")
        os.unlink(f"{data}/docs/link")
        write(f"{data}/docs/b.txt", "live version")

    for step, label in (("test", "tar"), ("z", "zip")):
        damage()
        args = argparse.Namespace(target=out, run=run, step=step, path=None, dry_run=True)
        dry = b.do_restore(args)
        check(f"{label} restore dry run: counts, restores nothing",
              dry["ok"] and dry["missing"]["items"] >= 3 and not os.path.exists(f"{data}/a.txt"))
        args.dry_run = False
        args.path = f"{data}/docs"
        part = b.do_restore(args)
        check(f"{label} restore --path: only that part", part["ok"] and os.path.exists(f"{data}/docs/sub/c.txt")
              and not os.path.exists(f"{data}/a.txt"))
        args.path = None
        full = b.do_restore(args)
        check(f"{label} restore: everything missing is back", full["ok"] and read(f"{data}/a.txt") == b"alpha")
        check(f"{label} restore: nothing overwritten", read(f"{data}/docs/b.txt") == b"live version")
        check(f"{label} restore: link back as link", os.path.islink(f"{data}/docs/link") and os.readlink(f"{data}/docs/link") == "b.txt")
        check(f"{label} restore: mode kept", stat.S_IMODE(os.stat(f"{data}/docs/sub/c.txt").st_mode) == 0o750
              and stat.S_IMODE(os.stat(f"{data}/a.txt").st_mode) == 0o640)
        check(f"{label} restore: time kept", int(os.stat(f"{data}/docs/sub/c.txt").st_mtime) == 631_152_000)
        check(f"{label} restore: second run finds nothing", b.do_restore(args)["missing"]["items"] == 0)
        if label == "tar" and xattr_ok:
            check("tar restore: extended attribute kept", os.getxattr(f"{data}/a.txt", "user.test") == b"value")
        write(f"{data}/docs/b.txt", "bravo")
    check("restore: unknown step", not b.do_restore(argparse.Namespace(target=out, run=run, step="nope", path=None, dry_run=True))["ok"])
    check("restore: refuses a bad --path", not b.do_restore(argparse.Namespace(target=out, run=run, step="test", path="/", dry_run=True))["ok"])
    check("restore: refuses a run without the prefix", not b.do_restore(argparse.Namespace(target=out, run="other", step="test", path=None, dry_run=True))["ok"])

    # 7 list and remove
    listed = b.do_list(argparse.Namespace(target=out))
    check("list: the run with its three steps", len(listed["runs"]) == 1 and [s["step"] for s in listed["runs"][0]["steps"]] == ["test", "z", "g"])
    rm = lambda name, dry=False: b.do_remove(argparse.Namespace(target=out, run=name, dry_run=dry))
    write(f"{out}/innocent/01-x.tar", "someone else's archive")
    check("remove: refuses a folder without the prefix", not rm("innocent")["ok"] and os.path.isfile(f"{out}/innocent/01-x.tar"))
    shutil.rmtree(f"{out}/innocent", ignore_errors=True)
    write(f"{out}/{run}/notes.txt", "x")
    check("remove: refuses unexpected content", not rm(run)["ok"] and os.path.isdir(f"{out}/{run}"))
    os.unlink(f"{out}/{run}/notes.txt")
    check("remove dry run: nothing removed", rm(run, True)["ok"] and os.path.isdir(f"{out}/{run}"))
    r = rm(run)
    check("remove: run folder gone", r["ok"] and not os.path.exists(f"{out}/{run}"))

    # 8 command line
    report = os.path.join(base, "r.json")
    code = b.main(["create", "--list", listing, "--target", out, "--step", "cli", "--dry-run", "--report", report])
    check("main: dry run ok and no folder", code == 0 and json.load(open(report))["ok"] and not os.listdir(out))
    code = b.main(["create", "--list", listing + "2", "--target", out, "--step", "cli", "--report", report])
    check("main: refusal gives exit 1", code == 1 and json.load(open(report))["ok"] is False)

    shutil.rmtree(base)
    if problems:
        print(f"FAILED ({len(problems)}):")
        for p in problems:
            print("  " + p)
        return 1
    print("PASSED: tar, tar.gz, zip, space rule, refusals, verification, selective restore, list and remove checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
