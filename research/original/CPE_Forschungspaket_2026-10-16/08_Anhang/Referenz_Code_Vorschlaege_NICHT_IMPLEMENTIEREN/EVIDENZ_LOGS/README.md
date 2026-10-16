# EVIDENCE

- `pytest_v01.log`: `11 passed` on the unmodified v0.1 tree (Python 3.13.16, scipy 1.18.1, httpx 2.13.0), 2026-10-16.
- `pytest_v02.log`: `31 passed` on `PATCH_PROPOSALS/source_v0_2`.
- `attack_v01_reproduction.py` + `attack_v01_output.log`: F1-F10 reproductions (ledger rewrite undetected, e-process hindsight/duplicate/absorbing zero, Kelly FOC check and cost units, coherence scaling and missing guard, arbitrary LP vertex, shallow evidence checks, unvalidated precheck payload). Run with `python -I attack_v01_reproduction.py <source_v0_1> <scratch dir>`.
- `lean_compile.log`: Lean `leanprover/lean4:v4.35.0`, Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`; `BetThreshold.lean` and `RiskBudget.lean` exit 0 with standard axioms; negative control fails (exit 1).
- `typesafe_openapi_2026-10-16.json`: the live OpenAPI document of https://api.typesafe.ai (title TypeSafe, version 0.2.0) used to verify the Jev adapter schema.

External documentation read on 2026-10-16 (URLs in CLAUDE_REVIEW.md §7 and §8) was not archived as bytes in this package; the owner should archive them in the ingest log at setup time.
