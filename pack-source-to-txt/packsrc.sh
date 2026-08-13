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
# USAGE
#   ./packsrc.sh [-h] [-md] [-txt]
#
# OPTIONS
#   -h    Print this help and exit. No output file is written.
#   -md   Also include .md files for this run (temporary, not saved to config).
#   -txt  Also include .txt files for this run (temporary, not saved to config).
#
# OUTPUT
#   ./project_source.txt — created or overwritten on each run.
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
  ./packsrc.sh [-h] [-md] [-txt]

OPTIONS
  -h    Print this help and exit. No output file is written.
  -md   Also include .md  files for this run (not saved to BASE_EXTENSIONS).
  -txt  Also include .txt files for this run (not saved to BASE_EXTENSIONS).

OUTPUT
  ./project_source.txt — created or overwritten on each run.

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
# Argument parsing
# --------------------------------------------------------------------------
EXTRA_EXTENSIONS=()

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
    # Global header with instructions for Claude
    echo "#!PKSRC:HEADER:BEGIN | project_source.txt | pksrc_ts: ${PKSRC_TS}"
    echo "#"
    echo "# @Claude: Das File wurde mit dem Zeitstempel ${PKSRC_TS} erstellt."
    echo "# Gib diesen Zeitstempel bitte im Chat immer kurz als Referenz mit aus,"
    echo "# wenn Du in Deiner Antwort Ergebnisse einer Suche in diesem File hast."
    echo "# Jede enthaltene Quelldatei hat eine Einleitungszeile mit dem Token"
    echo "# 'pksrc_ts: ${PKSRC_TS}'. Falls ein Suchergebnis einen anderen pksrc_ts-Wert"
    echo "# zeigt, ist es ein veraltetes Ergebnis aus einem früheren Index-Stand —"
    echo "# weise bitte ausdrücklich darauf hin."
    echo "# Das Feld 'file_mtime' gibt den letzten Änderungszeitpunkt der Quelldatei an."
    echo "# Anhand von file_mtime erkennst Du, ob eine Datei bei einem bestimmten"
    echo "# Arbeitsschritt tatsächlich angefasst wurde oder nicht."
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
