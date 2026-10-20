#!/bin/sh
# T-41: the archived research package is unchanged, by manifest and by Git tree object.
# Run from the repository root. Exit 0 when both checks hold.
set -eu
ARCHIVE="research/original/CPE_Forschungspaket_2026-10-16"
EXPECTED_TREE="122a1619cdad4f1c7f577e26f86709c34ce86298"
(cd "$ARCHIVE" && sha256sum -c MANIFEST.sha256 --quiet) || { echo "T-41: manifest check failed"; exit 1; }
count=$(cd "$ARCHIVE" && sha256sum -c MANIFEST.sha256 | grep -c ': OK$')
tree=$(git rev-parse "HEAD:$ARCHIVE")
if [ "$tree" != "$EXPECTED_TREE" ]; then
  echo "T-41: tree object $tree differs from $EXPECTED_TREE (a file was added, renamed or changed)"; exit 1
fi
echo "T-41: manifest $count OK; tree $tree"
