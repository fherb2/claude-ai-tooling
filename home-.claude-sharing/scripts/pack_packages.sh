#!/usr/bin/env bash
#
# Rebuild both download packages of claude-sync-watch from files/ and prove
# that each entry matches its source.
#
# Usage:
#     home-.claude-sharing/scripts/pack_packages.sh
#
# May be called from any working directory; the script locates the project
# folder from its own position.
#
# Why this exists: determination 2.7 says a package is a COPY that goes stale
# with the next change in files/, so whoever changes something there repacks in
# the same go, and the result is checked by comparing checksums. Until the
# multilingual conversion that was a handful of files and could be done by
# hand. It no longer is: the file set per package is a rule with exceptions --
# exactly one catalogue, exactly one working instruction, the README renamed,
# tools/ and zustand.json left out. A rule with four exceptions, applied by
# hand, is the kind of work that goes wrong on the third repetition, and a
# package that no longer matches its source is worse than no package, because
# nobody can see it from the outside.
#
# This script is a development tool. It is NOT part of what gets delivered and
# never travels to a target machine -- which is why it sits in scripts/ and not
# in files/ (doku 2.7).
#
# @Claude:
#     How to use: run it after every change to a file in files/, and after
#     every change to README.md or README.en.md of this folder -- both travel
#     into the packages. It takes no arguments and needs no network. It
#     rebuilds both archives from scratch rather than exchanging single
#     entries, so a file removed from files/ cannot stay behind in an archive.
#
#     A file ADDED to files/ is a different matter: the set below is the
#     determination of what an installation consists of, so a new name is not
#     packed by itself. It is not swallowed either -- the third check refuses
#     the run and names it. Do not work around that: decide where the file
#     belongs.
#
#     What to ask the user: nothing while it only repacks. Ask before adding a
#     name to COMMON, PER_LANGUAGE or NOT_IN_PACKAGE below: that changes what
#     an installation consists of, and the required-file check in
#     install_service.sh plus chapter 2.7 have to follow in the same go.
#
#     What to report afterwards: the two archive names, and per package that
#     every entry matched its source and the file set was as determined. Report
#     any deviation verbatim -- a deviation is an error, not a variant (2.7).
#     Output is German like that of the check script (named exception in 2.5).
set -euo pipefail

# The project folder is the parent of this script's folder, following symlinks.
SCRIPT_PATH="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT_PATH" ]; do
    SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH")"
done
AREA="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"

SRC="$AREA/files"
OUT="$AREA/downloads"

# The single directory inside every archive. Unpacking with "-d ~" therefore
# creates the prescribed target folder in one go (doku 2.7).
TOP=".claude-sync-watch"

# The files every package carries under their own name.
COMMON=(claude_sync_watchd.py claude-sync-watch.service install_service.sh
        uninstall_service.sh messages.py .stignore)

# The files that exist once per language. Their name carries the code, and they
# keep it inside the archive: repository and target machine stay name-identical,
# which is what keeps the watcher checkable from the repository (doku 2.7, 3.8).
PER_LANGUAGE=(messages_%s.py conflict-resolution.%s.md)

LANGUAGES=(de en)

# What lies in files/ and deliberately does NOT go into a package. Named here
# rather than skipped silently, because the third check below treats every
# other unexpected name in files/ as an error: tools/ is created by the
# installation, zustand.json is a marker that comes into being at runtime
# (doku 2.7), __pycache__ is a leftover of any Python run, and .claude/ is one
# of the tooling: Claude Code puts a .cc-writes directory there. None of them
# is versioned, and none has anything to do with this project.
NOT_IN_PACKAGE=(tools __pycache__ zustand.json .claude)

[ -d "$SRC" ] || { printf 'Abbruch: kein Ordner %s\n' "$SRC" >&2; exit 1; }
[ -d "$OUT" ] || { printf 'Abbruch: kein Ordner %s\n' "$OUT" >&2; exit 1; }

# The README is the one file that IS renamed on the way in: every package
# carries its language version as README.md (doku 2.7).
readme_source() {
    case "$1" in
        de) printf '%s\n' "$AREA/README.md" ;;
        en) printf '%s\n' "$AREA/README.en.md" ;;
        *) return 1 ;;
    esac
}

# Where an entry of the archive comes from. One place for the question, so the
# build and the check below cannot disagree about it.
origin_of() {
    local language="$1" entry="$2"
    if [ "$entry" = "README.md" ]; then
        readme_source "$language"
    else
        printf '%s\n' "$SRC/$entry"
    fi
}

# The complete, sorted file set of one package.
entries_for() {
    local language="$1" pattern
    printf '%s\n' "${COMMON[@]}" README.md
    for pattern in "${PER_LANGUAGE[@]}"; do
        # shellcheck disable=SC2059  # the pattern IS the format string here
        printf "$pattern\n" "$language"
    done
}

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
FAILED=0

for language in "${LANGUAGES[@]}"; do
    zip_path="$OUT/claude-sync-watch_${language}_local.zip"
    stage="$WORK/$language/$TOP"
    mkdir -p "$stage"

    while IFS= read -r entry; do
        source_path=$(origin_of "$language" "$entry")
        [ -f "$source_path" ] || {
            printf 'Abbruch: Quelle fehlt: %s\n' "$source_path" >&2
            exit 1
        }
        cp -p "$source_path" "$stage/$entry"
    done < <(entries_for "$language")

    rm -f "$zip_path"
    # Sorted entries and -X: the archive then depends only on its content, so
    # an unchanged set of files produces an unchanged archive.
    ( cd "$WORK/$language" \
        && find "$TOP" -type f | LC_ALL=C sort | zip -9 -o -X -q "$zip_path" -@ )
    printf 'gepackt: %s\n' "$(basename "$zip_path")"
done

printf '\nPruefung gegen die Quellen:\n'

for language in "${LANGUAGES[@]}"; do
    zip_path="$OUT/claude-sync-watch_${language}_local.zip"
    check="$WORK/check-$language"
    mkdir -p "$check"
    unzip -qq -o "$zip_path" -d "$check"
    printf '  %s:\n' "$(basename "$zip_path")"

    # Direction one: is every entry byte-identical to its source?
    while IFS= read -r -d '' path; do
        entry=${path#"$check/$TOP/"}
        source_path=$(origin_of "$language" "$entry") || source_path=""
        if [ -z "$source_path" ] || [ ! -f "$source_path" ]; then
            printf '    KEINE QUELLE  %s\n' "$entry"
            FAILED=1
            continue
        fi
        if [ "$(sha256sum < "$path")" = "$(sha256sum < "$source_path")" ]; then
            printf '    gleich        %s\n' "$entry"
        else
            printf '    ABWEICHUNG    %s\n' "$entry"
            FAILED=1
        fi
    done < <(find "$check/$TOP" -type f -print0 | LC_ALL=C sort -z)

    # Direction two: is the file set the determined one -- nothing more and
    # nothing less? Without this a file dropped from files/ would simply
    # disappear from the package without anyone noticing.
    have=$(cd "$check/$TOP" && find . -type f -printf '%P\n' | LC_ALL=C sort)
    want=$(entries_for "$language" | LC_ALL=C sort)
    if [ "$have" = "$want" ]; then
        printf '    Dateisatz     wie festgelegt (%s Dateien)\n' \
            "$(printf '%s\n' "$want" | wc -l)"
    else
        printf '    DATEISATZ WEICHT AB:\n'
        diff <(printf '%s\n' "$want") <(printf '%s\n' "$have") \
            | sed 's/^/      /' || true
        FAILED=1
    fi
done

# Direction three: does files/ hold anything that no package carries? The two
# checks above compare the archives against the determination; this one compares
# the determination against reality. Without it a file added to files/ would
# simply never be packed, and nothing would say so -- the set here is a list and
# not a search, on purpose, because "exactly one catalogue, exactly one working
# instruction" is a determination and not whatever happens to lie there.
printf '  files/ gegen den Dateisatz:\n'
expected_in_files=$( { printf '%s\n' "${COMMON[@]}" "${NOT_IN_PACKAGE[@]}"
    for language in "${LANGUAGES[@]}"; do
        entries_for "$language" | grep -v '^README\.md$'
    done; } | LC_ALL=C sort -u )
present_in_files=$(cd "$SRC" && find . -mindepth 1 -maxdepth 1 -printf '%P\n' \
    | LC_ALL=C sort)
# Matched by line and not with comm: comm insists on ITS collation order, and
# the two lists are sorted in the C locale here (measured -- comm rejected them).
unexpected=$(printf '%s\n' "$present_in_files" \
    | grep -Fxv -f <(printf '%s\n' "$expected_in_files") || true)
if [ -z "$unexpected" ]; then
    printf '    keine unerwartete Datei in files/\n'
else
    printf '    UNERWARTET in files/, in keinem Paket enthalten:\n'
    printf '%s\n' "$unexpected" | sed 's/^/      /'
    FAILED=1
fi

printf '\n'
if [ "$FAILED" -eq 0 ]; then
    printf 'Alle Pruefungen bestanden.\n'
else
    printf 'ABWEICHUNGEN GEFUNDEN — die Pakete stimmen nicht mit files/ ueberein.\n' >&2
    exit 1
fi
