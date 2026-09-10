#!/usr/bin/env bash
# Replaces the README inside one download package and repacks the archive.
#
# Why this exists: the README of a skill travels into its packages under the
# name README.md. Changing the README therefore makes every package of that
# language stale -- and a package that no longer matches its source is worse
# than no package, because nobody can see it from the outside.
#
# The archive is rebuilt from its own contents, not from a file list: whatever
# was in it stays in it, and only README.md is exchanged. That way the step
# cannot silently add or drop an entry. Afterwards every entry is compared
# against the state before, and the README against its source.
#
# Usage:  repack-package-readme.sh <ordner-mit-downloads> <paketname.zip>
# Example: repack-package-readme.sh skills/chat-export chat-export_de_local.zip
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

DIR=${1:?Ordner fehlt}
ZIPNAME=${2:?Paketname fehlt}
ZIP="$PWD/$DIR/downloads/$ZIPNAME"
[ -f "$ZIP" ] || { echo "Kein Paket: $ZIP" >&2; exit 1; }

# The language of the package decides which source README goes in.
case "$ZIPNAME" in
    *_de_*) SRC="$PWD/$DIR/README.md" ;;
    *_en_*) SRC="$PWD/$DIR/README.en.md" ;;
    *) echo "Kein Sprachkuerzel im Paketnamen: $ZIPNAME" >&2; exit 1 ;;
esac
[ -f "$SRC" ] || { echo "Keine Quell-README: $SRC" >&2; exit 1; }

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/before" "$WORK/after"

unzip -qq -o "$ZIP" -d "$WORK/before"
( cd "$WORK/before" && find . -type f | LC_ALL=C sort | xargs sha256sum ) > "$WORK/before.txt"

# The single directory inside the archive is the target name.
TOP=$(cd "$WORK/before" && find . -mindepth 1 -maxdepth 1 -type d -printf '%f\n')
[ -n "$TOP" ] || { echo "Archiv ohne Ordner: $ZIPNAME" >&2; exit 1; }
[ -f "$WORK/before/$TOP/README.md" ] || { echo "Paket enthaelt keine README.md" >&2; exit 1; }

cp -p "$SRC" "$WORK/before/$TOP/README.md"
rm -f "$ZIP"
( cd "$WORK/before" && find "$TOP" -type f | LC_ALL=C sort | zip -9 -o -X -q "$ZIP" -@ )

unzip -qq -o "$ZIP" -d "$WORK/after"
( cd "$WORK/after" && find . -type f | LC_ALL=C sort | xargs sha256sum ) > "$WORK/after.txt"

if diff <(grep -v 'README.md$' "$WORK/before.txt") \
        <(grep -v 'README.md$' "$WORK/after.txt") > /dev/null; then
    rest='unveraendert'
else
    rest='ABWEICHUNG'
fi
if [ "$(sha256sum < "$SRC")" = "$(sha256sum < "$WORK/after/$TOP/README.md")" ]; then
    same='ja'
else
    same='NEIN'
fi

printf '%s  uebrige Eintraege: %s | README == Quelle: %s | %s Bytes\n' \
    "$ZIPNAME" "$rest" "$same" "$(stat -c%s "$ZIP")"

[ "$rest" = 'unveraendert' ] && [ "$same" = 'ja' ]
