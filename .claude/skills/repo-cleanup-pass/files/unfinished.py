#!/usr/bin/env python3
"""The path exclusions of this skill, in one place.

Two sets, because they answer different questions:

UNFINISHED   Skill folders marked as not ready. Every tool of this skill
             ignores them -- a finding about an unfinished skill is none.
RELEASE      The above plus the research material and the project's own
             skills: everything that must not reach the release branch.

A folder counts as marked when its name does not begin with an alphanumeric
character. That criterion is deliberately broader than "begins with an emoji":
it fails in the safe direction. Over-excluding is loud -- the folder is simply
absent and someone notices. Under-excluding is silent, and an unfinished skill
would travel into the release, which is the very thing these sets prevent.
Emoji cannot be caught reliably anyway: they are spread over a dozen Unicode
blocks that keep growing, and U+2139 INFORMATION SOURCE even reports as a
lowercase letter (measured 14 September 2026).

Precision is not lost, it is moved: describe() names a marked folder whose
first character is not a sign-like symbol, so a stray "_old-stuff/" is
reported instead of quietly vanishing.

Usage as a module:  from unfinished import is_unfinished, RELEASE_PATTERNS
Usage on the CLI:   unfinished.py --regex | --release-regex
"""

import re
import sys
import unicodedata

SKILLS_PREFIX = "skills/"

# Marked skill folder: directly under skills/, name not starting alphanumeric.
# Written as a character class, not as a negative lookahead: the same string
# has to work in Python and in `grep -E`, and POSIX ERE has no lookaheads.
# A lookahead version fails there with a syntax error -- and a failing grep in
# a pipe prints nothing, which reads exactly like a passed check. Equivalence
# of the two forms measured over all 203 versioned paths on 14 September 2026.
UNFINISHED_PATTERN = r"^skills/[^A-Za-z0-9]"

# Additionally out of the release: research material, and the project's own
# skills -- working equipment of the development branch, this skill included.
# The last pattern hangs on the prefix, not on a folder name, so a second
# project skill is covered without anyone having to remember it.
RELEASE_PATTERNS = [UNFINISHED_PATTERN, r"^\.research/", r"^\.claude/skills/"]

_UNFINISHED_RE = re.compile(UNFINISHED_PATTERN)


def is_unfinished(path):
    """True for a path inside a skill folder that is marked as not ready."""
    return bool(_UNFINISHED_RE.match(path))


def describe(path):
    """A note about a marked folder whose mark is not a sign-like symbol.

    Returns None when there is nothing to say. Sign-like means Unicode category
    So, which covers the signs in use as well as any further pictograph,
    without needing a package outside the standard library.
    """
    if not is_unfinished(path):
        return None
    first = path[len(SKILLS_PREFIX):][:1]
    if not first or unicodedata.category(first) == "So":
        return None
    return (f"ausgeschlossen, aber {first!r} ist kein Schild "
            f"(Unicode-Kategorie {unicodedata.category(first)})")


def main(argv):
    if len(argv) == 2 and argv[1] == "--regex":
        print(UNFINISHED_PATTERN)
        return 0
    if len(argv) == 2 and argv[1] == "--release-regex":
        print("|".join(RELEASE_PATTERNS))
        return 0
    print(__doc__.strip(), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
