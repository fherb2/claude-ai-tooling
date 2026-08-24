#!/usr/bin/env python3
"""Report the Markdown files whose tables carry editor artifacts.

Usage: scan_md_tables.py [PROJECT_PATH]

PROJECT_PATH is the project root and nothing else -- every subdirectory below
it is searched by this tool itself, so it is called once and not per folder.
Defaults to the working directory.

Writes JSON to stdout and never touches a file. Exits 1 while any file still
needs repair and 0 once none does, so a run doubles as a check.

Two lists come out, and the difference matters. "files" is the work list: the
files the repair tool will change, and the only thing the exit code depends
on. "notes" holds what is reported but deliberately never repaired -- a
suffix glued to a code span, for instance. Keeping those out of the work list
is what allows a second run to come out clean at all.

The work list carries paths and counts, never line numbers: the repair tool
re-reads each file anyway, and a stale line number would make it edit the
wrong place. The notes carry line numbers, because a person reads them. Paths
are given as found below PROJECT_PATH, so the repair tool has to run from the
same working directory.
"""

import json
import sys

import md_table_artifacts as rules


def main(root):
    files = []
    notes = []
    total = 0
    for path in rules.markdown_files(root):
        repairable = 0
        for number, kind, context in rules.scan_text(path.read_text(encoding='utf-8')):
            if rules.is_repairable(kind):
                repairable += 1
            else:
                notes.append({'path': str(path), 'line': number,
                              'kind': kind, 'context': context})
        if repairable:
            files.append({'path': str(path), 'findings': repairable})
            total += repairable
    json.dump({'root': root, 'files': files, 'total': total, 'notes': notes},
              sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write('\n')
    return 1 if files else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
