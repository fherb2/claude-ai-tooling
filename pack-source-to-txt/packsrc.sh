#!/usr/bin/env bash
# ==============================================================================
# packsrc.sh
#
# Collects source files from one or more directories into a single
# project_source.txt.  Each file is wrapped in metadata lines (prefix #!PKSRC)
# that carry:
#   pksrc_ts   — timestamp of this script run, identical for every file block
#   file_mtime — last modification time of the individual source file
#
# The #!PKSRC prefix does not appear in normal Python or CUDA source code,
# so these lines are unambiguous metadata even when embedded in a search index.
#
# The file opens with a header between #!PKSRC:HEADER:BEGIN and
# #!PKSRC:HEADER:END, made up of three separately marked sections:
#   #!PKSRC:HEADER:NOTE_TO_READER      what the following sections are for
#   #!PKSRC:HEADER:FORMAT_DESCRIPTION  structure of the file and its fields
#   #!PKSRC:HEADER:DATE_TIME_CHECK     how to spot outdated retrieval results
# Each of these is searchable on its own, so a retrieval system that returns
# only a fragment of the file still returns something self-describing.
#
# The header describes; it does not command. Several AI agents deliberately
# treat the content of an uploaded document as data and may ignore directives
# found inside it. The actual instructions therefore live in a companion
# document, project_source.instructions.md (option -i), meant to be pasted
# into whatever standing-instructions field the agent offers. Both outputs
# draw the shared texts from emit_format_description and emit_date_time_check,
# so they cannot drift apart.
#
# USAGE
#   ./packsrc.sh [-h] [-md] [-txt] [-i]
#
# OPTIONS
#   -h    Print this help and exit. No output file is written.
#   -md   Also include .md files for this run (temporary, not saved to config).
#   -txt  Also include .txt files for this run (temporary, not saved to config).
#   -i    Also write project_source.instructions.md (see above).
#
# OUTPUT
#   ./project_source.txt              — created or overwritten on each run.
#   ./project_source.instructions.md  — with -i only.
#
# CONFIGURATION
#   Edit SOURCE_DIRS, BASE_EXTENSIONS, EXCLUDE_DIRS and EXPLICIT_FILES below.
# ==============================================================================


# ==============================================================================
# CONFIGURATION — edit this section as needed
# ==============================================================================

# SOURCE_DIRS
#   Directories to scan for source files, relative to this script's location.
#   Write without a leading './', one entry per array element.
#   The full relative path (e.g. ./shared/applogger.py) appears in the output
#   so files from different directories are clearly distinguishable.
#   Special entry "./" scans the entire project root recursively (all
#   subdirectories), instead of a single named subdirectory.
#   Default: ("source") — keeps the original single-directory behaviour and
#   is compatible with all existing projects that use this layout.
#   Example for multiple directories:
#     SOURCE_DIRS=("source" "shared" "tools" "tests")
#   Example for the whole project tree:
#     SOURCE_DIRS=("./")
SOURCE_DIRS=("source")

# BASE_EXTENSIONS
#   File extensions included in EVERY run.
#   Write without the leading dot, one entry per array element.
#   To add C headers for example: BASE_EXTENSIONS=("py" "cu" "h")
#   Special entry "" (empty string) matches files that have NO dot at all in
#   their name (e.g. "Dockerfile", "Makefile") — not files ending in a
#   literal dot.
BASE_EXTENSIONS=("py" "cu")

# EXCLUDE_DIRS
#   Directory *names* (not full paths) to skip at any depth inside the
#   scanned directories.  The match is on the bare name, so "backup" prunes
#   every directory called "backup" no matter where it appears in the tree.
#   To also skip a custom cache dir:  EXCLUDE_DIRS=("backup" "__pycache__" "cache")
#   Note: files and directories whose name starts with "." are already
#   excluded by default everywhere (see DOT-EXCLUSION note below) — you do
#   not need to list them here.
EXCLUDE_DIRS=("backup" "__pycache__")

# EXPLICIT_FILES
#   Extra individual files to include, matched by exact name/path instead of
#   by extension. Useful for extension-less files (so unrelated files that
#   happen to share the same extension aren't dragged in too), or for single
#   files that live outside SOURCE_DIRS entirely. Three forms are supported
#   per entry:
#
#     bare name, no leading path/slash          -> searched for by exact
#       e.g. "Dockerfile.watchdog"                  filename anywhere inside
#                                                    SOURCE_DIRS (EXCLUDE_DIRS
#                                                    still applies, but the
#                                                    default dot-exclusion is
#                                                    bypassed for this entry)
#     "./relative/path/from/project/root"       -> exact single file,
#       e.g. "./docker-compose.yml"                 relative to the project
#                                                    root
#     "/absolute/path"                          -> exact single file,
#       e.g. "/etc/hosts"                           absolute machine path
#     "~/path/from/home"                        -> exact single file,
#       e.g. "~/.config/foo.conf"                   relative to the user's
#                                                    home directory
#
#   All three path-prefixed forms (./, /, ~/) always bypass the default
#   dot-exclusion rule, since they name one specific file explicitly.
EXPLICIT_FILES=()

# DOT-EXCLUSION (not configurable, always active)
#   Any file or directory whose bare name starts with "." (e.g. .git,
#   .vscode, .env, .gitignore) is skipped everywhere in SOURCE_DIRS scans,
#   at any depth. The only way to include such a file is to list it
#   explicitly in EXPLICIT_FILES using the "./", "/" or "~/" form.


# ==============================================================================
# DO NOT EDIT BELOW THIS LINE
# ==============================================================================

usage() {
    cat <<'EOF'
USAGE
  ./packsrc.sh [-h] [-md] [-txt] [-i]

OPTIONS
  -h    Print this help and exit. No output file is written.
  -md   Also include .md  files for this run (not saved to BASE_EXTENSIONS).
  -txt  Also include .txt files for this run (not saved to BASE_EXTENSIONS).
  -i    Also write ./project_source.instructions.md, the companion document
        that carries the instructions for an AI agent. Paste its content into
        wherever your assistant takes its standing instructions (Claude
        project instructions, a Gemini Gem, AGENTS.md, ...). Its content does
        not depend on the run, so re-running just rewrites an identical file.

OUTPUT
  ./project_source.txt              — created or overwritten on each run.
  ./project_source.instructions.md  — with -i only, created or overwritten.

HEADER OF project_source.txt
  The generated file opens with a header bracketed by #!PKSRC:HEADER:BEGIN and
  #!PKSRC:HEADER:END that holds three separately marked sections:
    #!PKSRC:HEADER:NOTE_TO_READER      what the following sections are for
    #!PKSRC:HEADER:FORMAT_DESCRIPTION  structure of the file and its fields
    #!PKSRC:HEADER:DATE_TIME_CHECK     how to spot outdated retrieval results
  Every marker is searchable on its own, so a retrieval system that hands out
  a mere fragment of the file still hands out something self-describing. The
  body of the last two sections comes from emit_format_description and
  emit_date_time_check and is shared with project_source.instructions.md.

CONFIGURATION
  Edit SOURCE_DIRS, BASE_EXTENSIONS, EXCLUDE_DIRS and EXPLICIT_FILES near the
  top of this script.
  SOURCE_DIRS     : directories to scan (relative paths, without leading ./);
                    "./" scans the whole project root recursively.
  BASE_EXTENSIONS : always included file suffixes (without dot); "" matches
                    files with no dot in their name at all.
  EXCLUDE_DIRS    : directory names pruned at any depth inside the scanned trees.
  EXPLICIT_FILES  : individual files matched by exact name/path instead of
                    extension; see comments in the CONFIGURATION section.
  Files/directories starting with "." are always excluded unless listed
  explicitly in EXPLICIT_FILES via "./", "/" or "~/".
EOF
}

# --------------------------------------------------------------------------
# Shared header texts
#
# emit_format_description and emit_date_time_check are the SINGLE source for
# these two texts. They are used twice: once as the FORMAT_DESCRIPTION and
# DATE_TIME_CHECK sections of the project_source.txt header (piped through
# as_comment_lines), and once in project_source.instructions.md (verbatim,
# inside code fences). Edit them here and both outputs follow.
#
# The texts are stored WITHOUT a leading "# ": a "#" at the start of a line
# is a heading in Markdown, so the comment form has to be added by the
# consumer that needs it, not baked into the text.
#
# For the same reason the texts never say "this file" — they must read
# correctly both inside project_source.txt and in a separate instructions
# document, so they name project_source.txt explicitly.
# --------------------------------------------------------------------------

emit_format_description() {
    cat <<'EOF'
project_source.txt is a concatenation of source files, produced in a single
run. Every metadata line starts with the prefix '#!PKSRC:', which does not
occur in ordinary source code.

Each source file is enclosed in:

    #!PKSRC:FILE:BEGIN | <path> | pksrc_ts: <ts> | file_mtime: <ts>
    ... verbatim file content ...
    #!PKSRC:FILE:END | <path>

Fields:

    <path>       path of the source file, relative to the project root
    pksrc_ts     timestamp of the generating run, identical in every block
                 of the file, including its header
    file_mtime   last modification time of that individual source file
EOF
}

emit_date_time_check() {
    cat <<'EOF'
Every block repeats the pksrc_ts of the run that produced it. Content served
from an earlier, cached retrieval therefore carries an older pksrc_ts than the
#!PKSRC:HEADER:BEGIN line of the uploaded project_source.txt, and may no longer
match the current source code. Where the two differ, please retrieve the
#!PKSRC:HEADER:BEGIN line again and compare the values before relying on the
older content.

file_mtime distinguishes source files that were touched in a given work step
from those that were not.
EOF
}

# as_comment_lines — reads text on stdin and prefixes every line with "# ",
# so it can be embedded in the project_source.txt header. Empty lines become
# a bare "#" rather than "# " to avoid trailing whitespace.
as_comment_lines() {
    sed -e 's/^/# /' -e 's/^# $/#/'
}

# write_instructions_file — writes project_source.instructions.md, the
# companion document that carries the actual instructions for an AI agent.
# Instructions live here rather than in project_source.txt because several
# agents deliberately treat the content of an uploaded document as data and
# may ignore directives found inside it; a standing-instructions field is the
# channel where every agent honours them.
# The two shared texts are embedded verbatim inside code fences — they contain
# lines starting with "#", which Markdown would otherwise render as headings.
write_instructions_file() {
    {
        cat <<'EOF'
# project_source.txt — notes for AI agents and assistants

`project_source.txt` is a generated snapshot of a project's source code: every
source file concatenated into a single text file and wrapped in `#!PKSRC:`
metadata lines. It is meant to be uploaded as project knowledge or context, so
that an assistant has the whole codebase available in one place.

This document holds the instructions that belong *with* that snapshot. Paste it
wherever your assistant takes its standing instructions — Claude project
instructions, the instructions field of a Gemini Gem, `AGENTS.md`, `CLAUDE.md`,
or the system prompt of your own tooling. The snapshot itself is data, and
instructions placed inside a data file are not honoured reliably by every
agent.

## File format

```text
EOF
        emit_format_description
        cat <<'EOF'
```

## Recognising outdated content

```text
EOF
        emit_date_time_check
        cat <<'EOF'
```

## What to do with it

- When you quote or summarise content taken from `project_source.txt`, name the
  `pksrc_ts` of the block you took it from.
- If that `pksrc_ts` differs from the one in the `#!PKSRC:HEADER:BEGIN` line of
  the uploaded file, retrieve that header line again and compare the two values
  before relying on the older content. Say explicitly that the result came from
  a superseded version of the file.
- Use `file_mtime` to tell which source files were actually changed in a given
  work step and which were left untouched.

---

Generated by `packsrc.sh`. Do not edit by hand — run `./packsrc.sh -i` and
commit the result, so this document cannot drift away from the header that
`packsrc.sh` writes into `project_source.txt`.
EOF
    } > project_source.instructions.md
}

# --------------------------------------------------------------------------
# Argument parsing
# --------------------------------------------------------------------------
EXTRA_EXTENSIONS=()
WRITE_INSTRUCTIONS=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h)
            usage
            exit 0
            ;;
        -md)
            EXTRA_EXTENSIONS+=("md")
            ;;
        -txt)
            EXTRA_EXTENSIONS+=("txt")
            ;;
        -i)
            WRITE_INSTRUCTIONS=1
            ;;
        *)
            echo "Error: unknown option '$1'" >&2
            echo "" >&2
            usage >&2
            exit 1
            ;;
    esac
    shift
done

# Merge base extensions with any extras requested on the command line
ACTIVE_EXTENSIONS=("${BASE_EXTENSIONS[@]}" "${EXTRA_EXTENSIONS[@]}")

# --------------------------------------------------------------------------
# Build find(1) argument arrays dynamically
# --------------------------------------------------------------------------

# Prune conditions from EXCLUDE_DIRS only (used for EXPLICIT_FILES bare-name
# search, which must bypass the dot-exclusion rule):
#   yields:  ( -name "backup" -o -name "__pycache__" )  -prune  -o
EXCLUDE_PRUNE_CONDS=()
for dir in "${EXCLUDE_DIRS[@]}"; do
    [[ ${#EXCLUDE_PRUNE_CONDS[@]} -gt 0 ]] && EXCLUDE_PRUNE_CONDS+=(-o)
    EXCLUDE_PRUNE_CONDS+=(-name "$dir")
done

# Prune conditions from EXCLUDE_DIRS PLUS the default dot-exclusion rule
# (used for the regular BASE_EXTENSIONS scan):
#   yields:  ( -name "backup" -o -name "__pycache__" -o -name ".*" ) -prune -o
DOT_PRUNE_CONDS=("${EXCLUDE_PRUNE_CONDS[@]}")
[[ ${#DOT_PRUNE_CONDS[@]} -gt 0 ]] && DOT_PRUNE_CONDS+=(-o)
DOT_PRUNE_CONDS+=(-name ".*")

# Name conditions from ACTIVE_EXTENSIONS:
#   yields:  ( -name "*.py" -o -name "*.cu" )
# The special empty-string extension matches files with no dot at all in
# their name (e.g. "Dockerfile"), NOT files ending in a literal dot.
NAME_CONDS=()
for ext in "${ACTIVE_EXTENSIONS[@]}"; do
    [[ ${#NAME_CONDS[@]} -gt 0 ]] && NAME_CONDS+=(-o)
    if [[ -z "$ext" ]]; then
        NAME_CONDS+=(-not -name "*.*")
    else
        NAME_CONDS+=(-name "*.${ext}")
    fi
done

# resolve_dir_path — maps a SOURCE_DIRS entry to an actual find(1) start path.
# "./" (or ".") means "the whole project root, recursively"; anything else
# is prefixed with "./" as before.
resolve_dir_path() {
    local dir="$1"
    if [[ "$dir" == "./" || "$dir" == "." ]]; then
        echo "."
    else
        echo "./${dir}"
    fi
}

# run_find — iterates over SOURCE_DIRS and runs find in each existing directory,
# applying BASE_EXTENSIONS/EXTRA_EXTENSIONS filtering and the default
# dot-exclusion rule (in addition to EXCLUDE_DIRS).
# -mindepth 1 is essential here: without it, a SOURCE_DIRS entry of "./"
# would have its own start path (".") tested against the dot-exclusion
# pattern ".*" — which matches "." itself and would prune away the entire
# recursive scan before it even starts.
# Directories listed in SOURCE_DIRS that do not exist are skipped with a
# warning on stderr so the rest of the output is still produced cleanly.
# Output: one relative file path per line (e.g. ./shared/applogger.py), unsorted.
# Sorting across all directories happens in the caller pipeline.
run_find() {
    local args_tail=()
    args_tail+=(-mindepth 1)
    if [[ ${#DOT_PRUNE_CONDS[@]} -gt 0 ]]; then
        args_tail+=('(' "${DOT_PRUNE_CONDS[@]}" ')' -prune -o)
    fi
    args_tail+=(-type f '(' "${NAME_CONDS[@]}" ')' -print)

    for dir in "${SOURCE_DIRS[@]}"; do
        local dir_path
        dir_path=$(resolve_dir_path "$dir")
        if [[ ! -d "$dir_path" ]]; then
            echo "Warning: SOURCE_DIRS entry '${dir_path}' not found — skipping." >&2
            continue
        fi
        find "$dir_path" "${args_tail[@]}"
    done
}

# run_find_explicit_bare — searches all SOURCE_DIRS for one exact filename
# (used for EXPLICIT_FILES entries without a path prefix). EXCLUDE_DIRS
# still applies, but the default dot-exclusion rule is bypassed, since an
# explicitly named file is always wanted even if it lives in a hidden
# directory or has a name starting with ".".
# Output: one relative file path per line, unsorted (may be empty).
run_find_explicit_bare() {
    local filename="$1"
    local args_tail=()
    args_tail+=(-mindepth 1)
    if [[ ${#EXCLUDE_PRUNE_CONDS[@]} -gt 0 ]]; then
        args_tail+=('(' "${EXCLUDE_PRUNE_CONDS[@]}" ')' -prune -o)
    fi
    args_tail+=(-type f -name "$filename" -print)

    for dir in "${SOURCE_DIRS[@]}"; do
        local dir_path
        dir_path=$(resolve_dir_path "$dir")
        [[ -d "$dir_path" ]] || continue
        find "$dir_path" "${args_tail[@]}"
    done
}

# resolve_explicit_path — resolves a single "./", "/" or "~/" prefixed
# EXPLICIT_FILES entry to an actual filesystem path. No find(1) involved
# here, since these forms always name exactly one specific file.
resolve_explicit_path() {
    local entry="$1"
    case "$entry" in
        ~/*)
            echo "${HOME}/${entry#\~/}"
            ;;
        *)
            echo "$entry"
            ;;
    esac
}

# collect_explicit_files — resolves every EXPLICIT_FILES entry to zero or
# more concrete file paths, warning on stderr for entries that don't match
# anything. Output: one relative/absolute file path per line, unsorted.
collect_explicit_files() {
    for entry in "${EXPLICIT_FILES[@]}"; do
        case "$entry" in
            ./*|/*|~/*)
                local resolved
                resolved=$(resolve_explicit_path "$entry")
                if [[ -f "$resolved" ]]; then
                    echo "$resolved"
                else
                    echo "Warning: EXPLICIT_FILES entry '${entry}' not found at '${resolved}' — skipping." >&2
                fi
                ;;
            *)
                local found
                found=$(run_find_explicit_bare "$entry")
                if [[ -n "$found" ]]; then
                    echo "$found"
                else
                    echo "Warning: EXPLICIT_FILES entry '${entry}' not found in any SOURCE_DIRS — skipping." >&2
                fi
                ;;
        esac
    done
}

# --------------------------------------------------------------------------
# Generation timestamp — single value used throughout the output file
# --------------------------------------------------------------------------
PKSRC_TS=$(date +"%Y-%m-%d_%H-%M-%S")
echo "# project_source.txt generation started: ${PKSRC_TS}"

# --------------------------------------------------------------------------
# Write project_source.txt
# --------------------------------------------------------------------------
{
    # Global header. Each section carries its own #!PKSRC marker so that a
    # retrieval system handing out only a fragment of this file still hands
    # out something self-describing. The FORMAT_DESCRIPTION and
    # DATE_TIME_CHECK bodies come from the shared emitters above.
    echo "#!PKSRC:HEADER:BEGIN | project_source.txt | pksrc_ts: ${PKSRC_TS}"
    echo "#"
    echo "#!PKSRC:HEADER:NOTE_TO_READER"
    echo "# For AI agents, assistants, and anyone writing scripts against this"
    echo "# file: the FORMAT_DESCRIPTION and DATE_TIME_CHECK sections below"
    echo "# describe how this file is structured, how to read it automatically,"
    echo "# and how to recognise results that come from an outdated version of it."
    echo "#"
    echo "#!PKSRC:HEADER:FORMAT_DESCRIPTION"
    emit_format_description | as_comment_lines
    echo "#"
    echo "#!PKSRC:HEADER:DATE_TIME_CHECK"
    emit_date_time_check | as_comment_lines
    echo "#"
    echo "#!PKSRC:HEADER:END"

    # One block per source file: BASE_EXTENSIONS matches plus EXPLICIT_FILES,
    # sorted by path across all SOURCE_DIRS. Files with identical names in
    # different directories are NOT deduplicated — each is a distinct file,
    # and its containing path is visible in its #!PKSRC:FILE:BEGIN line.
    { run_find; collect_explicit_files; } | sort | while read -r f; do
        FILE_MTIME=$(date -d "$(stat -c "%y" "$f")" +"%Y-%m-%d_%H-%M-%S")
        echo ""
        echo "#!PKSRC:FILE:BEGIN | ${f} | pksrc_ts: ${PKSRC_TS} | file_mtime: ${FILE_MTIME}"
        cat "$f"
        echo ""
        echo "#!PKSRC:FILE:END | ${f}"
    done

} > project_source.txt

echo "# project_source.txt written successfully. Timestamp: ${PKSRC_TS}"

# -i writes the companion instructions document in addition to the packed
# source. Its content does not depend on this run's timestamp, so re-running
# simply overwrites it with an identical file.
if [[ ${WRITE_INSTRUCTIONS} -eq 1 ]]; then
    write_instructions_file
    echo "# project_source.instructions.md written successfully."
fi
