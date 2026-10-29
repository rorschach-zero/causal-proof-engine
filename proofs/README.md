# Lean proofs

The retained lemmas of `research/04-formal-verification.md` section 1, carried verbatim from the archived reference
package, on the pinned toolchain `leanprover/lean4:v4.35.0` with Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`
(`lean-toolchain`, `lake-manifest.json`). `CpeProofs/Broken.lean` is the deliberately false proof of T-40: it is not
part of the library and must fail with `linarith failed`.

CI runs `tools/lean_check.sh`, which installs the pinned toolchain, fetches the Mathlib cache, builds the library,
prints the axioms of every theorem and compiles the negative control. Any download or cache failure is reported as
`NOT VERIFIED` and makes the job red; it is never reported as a pass.

A compiled theorem proves that conclusions follow from listed hypotheses. It never certifies a forecast, an edge,
an outcome or any property of the world (`AGENTS.md` section 8).
