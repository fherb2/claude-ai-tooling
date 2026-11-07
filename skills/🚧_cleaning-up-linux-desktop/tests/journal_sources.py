"""Read-only: which sources produce the priority "info" entries of the journal, per day.

Only the source names (syslog identifier, command) and the timestamp are read;
message texts are never requested or printed.

Usage: python3 -I /tmp/journal_sources.py
"""

import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime

TS_PATTERN = re.compile(r'"__REALTIME_TIMESTAMP":"(\d+)"')
IDENT_PATTERN = re.compile(r'"SYSLOG_IDENTIFIER":"([^"]*)"')
COMM_PATTERN = re.compile(r'"_COMM":"([^"]*)"')
UNIT_PATTERN = re.compile(r'"_SYSTEMD_UNIT":"([^"]*)"')
TOP_PER_DAY = 3
TOP_OVERALL = 12


def main():
    per_day = defaultdict(Counter)
    units = Counter()
    total = 0
    proc = subprocess.Popen(
        ["journalctl", "-p", "6..6", "-o", "json",
         "--output-fields=SYSLOG_IDENTIFIER,_COMM,_SYSTEMD_UNIT", "--no-pager", "-q"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1 << 20)
    for line in proc.stdout:
        ts_match = TS_PATTERN.search(line)
        if ts_match is None:
            continue
        day = datetime.fromtimestamp(int(ts_match.group(1)) / 1_000_000).strftime("%m-%d")
        source = IDENT_PATTERN.search(line) or COMM_PATTERN.search(line)
        name = source.group(1) if source else "(ohne Name)"
        per_day[day][name] += 1
        unit = UNIT_PATTERN.search(line)
        units[unit.group(1) if unit else "(ohne Unit)"] += 1
        total += 1
        if total % 1_000_000 == 0:
            print(f"  ... {total:,} Eintraege gelesen", file=sys.stderr)
    error = proc.stderr.read().strip()
    if proc.wait() != 0:
        print("journalctl fehlgeschlagen:", error)
        return 1

    print(f"Info-Eintraege gesamt: {total:,}\n")
    print("Je Tag: Summe und die staerksten Quellen (Name: Anzahl)")
    for day in sorted(per_day):
        counter = per_day[day]
        top = ", ".join(f"{n}: {c:,}" for n, c in counter.most_common(TOP_PER_DAY))
        print(f"  {day}  {sum(counter.values()):>10,}   {top}")

    overall = Counter()
    for counter in per_day.values():
        overall.update(counter)
    print(f"\nStaerkste Quellen ueber alle Tage (Name, Anzahl, Anteil):")
    for name, count in overall.most_common(TOP_OVERALL):
        print(f"  {name:<30}{count:>12,}  {100 * count / total:5.1f} %")

    print(f"\nStaerkste Units ueber alle Tage:")
    for name, count in units.most_common(8):
        print(f"  {name:<40}{count:>12,}  {100 * count / total:5.1f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
