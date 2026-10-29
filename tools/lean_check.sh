#!/bin/sh
# T-40: build the retained Lean lemmas on the pinned toolchain and compile the known-false lemma, which must fail.
# Every infrastructure failure (toolchain download, Mathlib cache, build) is reported as NOT VERIFIED with a red
# exit status; the job never reports a pass it did not earn. Run from the repository root.
set -u
ELAN_VERSION="v4.2.4"
ELAN_SHA256="42b94d4244e8353142c456ec0e4ca6528fd898a6c604d4059f494e706e431f63"  # elan-x86_64-unknown-linux-gnu.tar.gz
ELAN_HOME="${ELAN_HOME:-$HOME/.elan}"
export ELAN_HOME
export PATH="$ELAN_HOME/bin:$PATH"
not_verified() { echo "LEAN: NOT VERIFIED: $1"; exit 1; }
# Every file of a run is under its own temporary directory, removed at exit: two runs on one host never share a log or
# a download (issue #37, pass 8 for the owner, fixed in pass 9 as P9-8).
work=$(mktemp -d) || not_verified "cannot create a temporary directory"
trap 'rm -rf "$work"' EXIT

if ! command -v elan >/dev/null 2>&1; then
  mkdir -p "$ELAN_HOME/bin" || not_verified "cannot create $ELAN_HOME"
  curl -sSfL --retry 2 -m 300 \
    "https://github.com/leanprover/elan/releases/download/$ELAN_VERSION/elan-x86_64-unknown-linux-gnu.tar.gz" \
    -o "$work/elan.tar.gz" || not_verified "elan $ELAN_VERSION download failed"
  echo "$ELAN_SHA256  $work/elan.tar.gz" | sha256sum -c --quiet || not_verified "elan archive digest mismatch"
  tar -xzf "$work/elan.tar.gz" -C "$ELAN_HOME/bin" elan-init || not_verified "elan archive unreadable"
  "$ELAN_HOME/bin/elan-init" -y --no-modify-path --default-toolchain none >/dev/null 2>&1 \
    || not_verified "elan-init failed"
fi
cd proofs || not_verified "proofs directory missing"
toolchain=$(cat lean-toolchain)
elan toolchain install "$toolchain" || not_verified "toolchain $toolchain download failed"
lake exe cache get || not_verified "Mathlib cache unreachable"
# A lemma closed by `sorry` builds with a warning and exit status 0, and `#print axioms` lists `sorryAx` for it; either
# in the build log means a retained lemma is not proved (issue #37).
lake build > "$work/lean_build.log" 2>&1
built=$?
cat "$work/lean_build.log"
[ "$built" -eq 0 ] || not_verified "the retained lemmas did not build"
if grep -q -e "declaration uses 'sorry'" -e "sorryAx" "$work/lean_build.log"; then
  not_verified "a retained lemma depends on sorry"
fi
echo "LEAN: retained lemmas built on $toolchain"
if lake env lean CpeProofs/Broken.lean > "$work/broken.log" 2>&1; then
  cat "$work/broken.log"
  not_verified "the known-false lemma compiled"
fi
grep -q "linarith failed" "$work/broken.log" || { cat "$work/broken.log"; not_verified "the known-false lemma failed for another reason"; }
echo "LEAN: the known-false lemma fails as required"
echo "LEAN: VERIFIED"
