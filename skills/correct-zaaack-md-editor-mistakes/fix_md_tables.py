#!/usr/bin/env python3
"""Repair the Markdown files that scan_md_tables.py listed.

Usage: scan_md_tables.py PROJECT_PATH | fix_md_tables.py

Reads the scanner's JSON from stdin and repairs every file it names, in place.
Only whitespace inside table rows is ever touched.

Each file is re-read and its repairs are derived from the current content, so
a file that changed between the two runs cannot be edited at the wrong place.
Paths are resolved against the working directory, which therefore has to be
the one the scanner ran in.
"""

import json
import pathlib
import sys

import md_table_artifacts as rules


def main():
    listing = json.load(sys.stdin)
    total = 0
    for entry in listing.get('files', []):
        path = pathlib.Path(entry['path'])
        text = path.read_text(encoding='utf-8')
        repaired, rows = rules.repair_text(text)
        if repaired != text:
            path.write_text(repaired, encoding='utf-8')
            total += rows
            print(f'{rows:3} row(s)  {path}')
    print(f'\n{total} row(s) repaired')


if __name__ == '__main__':
    main()
