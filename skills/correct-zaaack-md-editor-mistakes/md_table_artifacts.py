"""Editor artifacts in Markdown tables: what counts as one, and how to repair it.

Some WYSIWYG Markdown editors damage table rows when saving. Two artifacts are
known: a space swallowed in front of an inline-code or bold delimiter, and a
no-break space (U+00A0) put in place of an ordinary one. The second is the
worse of the two, because it is invisible and defeats any search over the
wording.

This module is the single place where those rules live. Both command line tools
import it, so a change here cannot leave one of them reporting what the other
will not touch.
"""

import pathlib
import re

CODE = re.compile(r'`[^`\n]+`')
BOLD = re.compile(r'\*\*[^*\n]+\*\*')

# Characters a delimiter may legitimately touch on its left resp. right.
OK_BEFORE = set(' \t|([-–—*_"\'„“·/>')
OK_AFTER = set(' \t|)]-–—*_.,;:!?"\'“”·/<')

NBSP = ' '

# Project scope: a path holding one of these is never looked at. The one
# setting to review before using these tools in another project.
#
# '/.git/' used to sit here and is gone on purpose: every hidden entry is
# skipped now, which covers it. Do not put it back -- it would only suggest
# that the other dot folders are still being searched.
SKIP = ('bisherige Arbeitsanweisungen',)

# Artifact kinds repair_row acts on. Everything else is reported for a human
# to look at once and must stay out of any work list: a check that keeps
# listing what nothing will ever repair can never come out clean.
REPAIRABLE = ('nbsp', 'before')


def is_table_row(line):
    """True for a line that opens a Markdown table row."""
    return line.lstrip().startswith('|')


def is_repairable(kind):
    """True for an artifact kind that repair_row will actually act on."""
    return kind in REPAIRABLE


def find_artifacts(line):
    """Artifacts in one table row, as (kind, context) pairs.

    Kinds are 'nbsp', 'before' and 'after'. Only the first two are repairable;
    see repair_row for why 'after' is reported but left alone.
    """
    found = []
    if NBSP in line:
        found.append(('nbsp', line.replace(NBSP, '<NBSP>')[:120]))
    for pattern in (CODE, BOLD):
        for match in pattern.finditer(line):
            before = line[match.start() - 1] if match.start() else '|'
            after = line[match.end()] if match.end() < len(line) else '|'
            if before not in OK_BEFORE:
                found.append(('before', before + match.group()[:24]))
            if after not in OK_AFTER:
                found.append(('after', match.group()[-24:] + after))
    return found


def repair_row(line):
    """One table row with its repairable artifacts repaired.

    A space is restored in front of an opening delimiter, and a no-break space
    becomes an ordinary one. Nothing is ever inserted *after* a closing
    delimiter: a suffix glued to a code span is regular prose (`uuid`s) and
    would be broken by that. Single-asterisk emphasis is left alone as well,
    because it cannot be told apart from a list marker or a multiplication
    sign with any confidence.
    """
    line = line.replace(NBSP, ' ')
    for pattern in (CODE, BOLD):
        while True:
            for match in pattern.finditer(line):
                if match.start() and line[match.start() - 1] not in OK_BEFORE:
                    line = line[:match.start()] + ' ' + line[match.start():]
                    break
            else:
                break
    return line


def scan_text(text):
    """Artifacts in a whole file, as (line number, kind, context) triples."""
    return [
        (number, kind, context)
        for number, line in enumerate(text.splitlines(), 1)
        if is_table_row(line)
        for kind, context in find_artifacts(line)
    ]


def repair_text(text):
    """The text with every table row repaired, and the number of rows changed."""
    repaired = ''.join(
        repair_row(line) if is_table_row(line) else line
        for line in text.splitlines(keepends=True)
    )
    changed = sum(
        1 for before, after in zip(text.splitlines(), repaired.splitlines())
        if before != after
    )
    return repaired, changed


def markdown_files(root):
    """Every in-scope Markdown file below root, in a stable order.

    Three filters, and the first one is the reason this function exists at all:

    * **Regular files only.** A sandbox masks the paths it must not expose by
      mounting a device over them -- a name that looks like a Markdown file but
      is a character device, unreadable, and invisible from outside the sandbox.
      Reading one raises PermissionError, and an aborted run leaves no result at
      all: "nothing found" and "never ran" then look the same. The criterion is
      deliberately the **file type** and not the shape of the mount, because the
      shape is not ours and may change.
    * **No hidden entries.** A path is dropped when one of its segments starts
      with a dot -- counted **relative to root**, so that pointing the tool at a
      dot folder on purpose still works.
    * **SKIP** for folders excluded by name in this project.
    """
    base = pathlib.Path(root)
    for path in sorted(base.rglob('*.md')):
        try:
            relative = path.relative_to(base)
        except ValueError:                      # pragma: no cover - defensive
            relative = path
        if any(part.startswith('.') for part in relative.parts):
            continue
        if any(skip in f'/{path.as_posix()}' for skip in SKIP):
            continue
        if not path.is_file():
            continue
        yield path
