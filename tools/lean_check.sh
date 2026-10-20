#!/bin/sh
# T-40: build the retained Lean lemmas on the pinned toolchain and compile the known-false lemma, which must fail.
# Every infrastructure failure (toolchain download, Mathlib cache, build) is reported as NOT VERIFIED with a red
# exit status; the job never reports a pass it did not earn. Run from the repository root.
set -u
ELAN_VERSION="v4.2.4"
ELAN_HOME="${ELAN_HOME:-$HOME/.elan}"
export ELAN_HOME
export PATH="$ELAN_HOME/bin:$PATH"
not_verified() { echo "LEAN: NOT VERIFIED: $1"; exit 1; }

if ! command -v elan >/dev/null 2>&1; then
  mkdir -p "$ELAN_HOME/bin" || not_verified "cannot create $ELAN_HOME"
  curl -sSfL --retry 2 -m 300 \
    "https://github.com/leanprover/elan/releases/download/$ELAN_VERSION/elan-x86_64-unknown-linux-gnu.tar.gz" \
    -o /tmp/elan.tar.gz || not_verified "elan $ELAN_VERSION download failed"
  tar -xzf /tmp/elan.tar.gz -C "$ELAN_HOME/bin" elan-init || not_verified "elan archive unreadable"
  "$ELAN_HOME/bin/elan-init" -y --no-modify-path --default-toolchain none >/dev/null 2>&1 \
    || not_verified "elan-init failed"
fi
cd proofs || not_verified "proofs directory missing"
toolchain=$(cat lean-toolchain)
elan toolchain install "$toolchain" || not_verified "toolchain $toolchain download failed"
lake exe cache get || not_verified "Mathlib cache unreachable"
lake build || not_verified "the retained lemmas did not build"
echo "LEAN: retained lemmas built on $toolchain"
if lake env lean CpeProofs/Broken.lean > /tmp/broken.log 2>&1; then
  cat /tmp/broken.log
  not_verified "the known-false lemma compiled"
fi
grep -q "linarith failed" /tmp/broken.log || { cat /tmp/broken.log; not_verified "the known-false lemma failed for another reason"; }
echo "LEAN: the known-false lemma fails as required"
echo "LEAN: VERIFIED"
