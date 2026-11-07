"""Read-only statistics of the systemd journal: entries per log level over time.

Bins widen with age (today, yesterday+day before, rest of the last 7 days,
week before, two weeks, four weeks, twelve weeks, rest of 365 days, older).
Every entry is counted in exactly one bin. Only timestamp and priority are
read from journalctl; message texts are never requested or printed.

Usage: python3 -I /tmp/journal_histogram.py
"""

import re
import subprocess
import sys
from datetime import datetime, timedelta

TS_PATTERN = re.compile(r'"__REALTIME_TIMESTAMP":"(\d+)"')
PRIO_PATTERN = re.compile(r'"PRIORITY":"(\d+)"')
LEVELS = ["0 emerg", "1 alert", "2 crit", "3 err", "4 warning", "5 notice", "6 info", "7 debug", "ohne"]
BAR_WIDTH = 40


def build_bins(midnight):
    """Return (label, start, end) with start/end as datetimes; end exclusive. None = open."""
    day = timedelta(days=1)
    spec = [
        ("heute", midnight, None),
        ("gestern + vorgestern", midnight - 2 * day, midnight),
        ("Rest der letzten 7 Tage", midnight - 6 * day, midnight - 2 * day),
        ("Woche davor", midnight - 13 * day, midnight - 6 * day),
        ("2 Wochen davor", midnight - 27 * day, midnight - 13 * day),
        ("4 Wochen davor", midnight - 55 * day, midnight - 27 * day),
        ("12 Wochen davor", midnight - 139 * day, midnight - 55 * day),
        ("Rest bis 365 Tage", midnight - 364 * day, midnight - 139 * day),
        ("aelter", None, midnight - 364 * day),
    ]
    return spec


def bin_index(ts, bounds):
    """Index of the bin containing timestamp ts (seconds); bounds are (start, end) seconds."""
    for i, (start, end) in enumerate(bounds):
        if (start is None or ts >= start) and (end is None or ts < end):
            return i
    return len(bounds) - 1


def main():
    now = datetime.now().astimezone()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    spec = build_bins(midnight)
    bounds = [(s.timestamp() if s else None, e.timestamp() if e else None) for _, s, e in spec]

    usage = subprocess.run(["journalctl", "--disk-usage"], capture_output=True, text=True)
    print(usage.stdout.strip() or usage.stderr.strip())

    counts = [[0] * len(LEVELS) for _ in spec]
    oldest = None
    total = 0
    proc = subprocess.Popen(
        ["journalctl", "-o", "json", "--output-fields=PRIORITY", "--no-pager", "-q"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1 << 20)
    for line in proc.stdout:
        # Regex instead of json.loads: the journal holds millions of entries.
        ts_match = TS_PATTERN.search(line)
        if ts_match is None:
            continue
        ts = int(ts_match.group(1)) / 1_000_000
        prio_match = PRIO_PATTERN.search(line)
        level = int(prio_match.group(1)) if prio_match and int(prio_match.group(1)) <= 7 else 8
        counts[bin_index(ts, bounds)][level] += 1
        oldest = ts if oldest is None or ts < oldest else oldest
        total += 1
        if total % 1_000_000 == 0:
            print(f"  ... {total:,} Eintraege gelesen", file=sys.stderr)
    error = proc.stderr.read().strip()
    if proc.wait() != 0:
        print("journalctl fehlgeschlagen:", error)
        return 1

    now_ts = now.timestamp()
    print(f"\nEintraege gesamt: {total:,}   aeltester Eintrag: "
          f"{datetime.fromtimestamp(oldest).astimezone():%Y-%m-%d %H:%M}   Stand: {now:%Y-%m-%d %H:%M}")

    # Effective covered days per bin (a bin only counts where the journal reaches back).
    spans = []
    for start, end in bounds:
        lo = max(start if start is not None else oldest, oldest)
        hi = min(end if end is not None else now_ts, now_ts)
        spans.append(max(0.0, hi - lo) / 86400)

    print("\nAnzahl Eintraege je Zeitraum und Stufe:")
    head = f"{'Zeitraum':<26}{'Tage':>6}" + "".join(f"{name.split()[-1]:>11}" for name in LEVELS) + f"{'gesamt':>10}"
    print(head)
    for (label, start, end), row, span in zip(spec, counts, spans):
        shown = f"{span:.1f}" if span else "-"
        print(f"{label:<26}{shown:>6}" + "".join(f"{n:>11,}" for n in row) + f"{sum(row):>10,}")
    print(f"{'gesamt':<32}" + "".join(f"{sum(r[i] for r in counts):>11,}" for i in range(len(LEVELS)))
          + f"{total:>10,}")

    print("\nEintraege pro Tag (Flaeche je Zeitraum vergleichbar; Balken je Stufe auf deren Maximum skaliert):")
    for i, name in enumerate(LEVELS):
        rates = [(row[i] / span if span else 0.0) for row, span in zip(counts, spans)]
        peak = max(rates)
        if peak == 0:
            continue
        print(f"\n  Stufe {name}   (Maximum {peak:,.0f} pro Tag)")
        for (label, _, _), rate in zip(spec, rates):
            bar = "#" * max(1, round(rate / peak * BAR_WIDTH)) if rate else ""
            print(f"    {label:<26}|{bar:<{BAR_WIDTH}}| {rate:>12,.0f}/Tag")
    return 0


if __name__ == "__main__":
    sys.exit(main())
