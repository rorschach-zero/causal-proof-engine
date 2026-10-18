# Reproduction scripts of the reconciliation matrix

One committed file per appendix of `research/16-reconciliation-matrix.md`, byte-identical to the fenced block
between that appendix's `<!-- <key>-script:start -->` and `<!-- <key>-script:end -->` markers. These are evidence
scripts for the research documents, not project code: nothing under `cpe/` (when it exists) may import them.

| File | Appendix | Needs |
|---|---|---|
| `reconciliation_probes.py` | A (output in B) | a scratch copy of the archived v0.2 reference code, passed as the first argument; the pinned packages, httpx and its dependencies included (the archived `cpe.saxo_sim` imports httpx) |
| `round2_checks.py` to `round21_checks.py`, `round23_checks.py` to `round39_checks.py` (round 22 had none) | C to V, W to Z, AA to AM | numpy and scipy of the pinned packages; `round38_checks.py` and `round39_checks.py` also run `git show` on this clone, to read the checkers of commits `98b03fc` and `784183f`; `round38_checks.py` also runs the working checker, so Appendix AL reproduces only while `check_appendix_scripts.py` is unchanged since `784183f` (RC-235) |
| `inventory.txt` | — | the committed list of the scripts above with their appendix keys (RC-230); a round with a script appends its line |
| `check_appendix_scripts.py` | — | the pinned packages, since it runs every script; verifies every file above against its appendix block, and fails on an appendix block without its file, a file without its block, any other `*.py` file here (RC-196), and a key without exactly one start and one end marker line (RC-217); then runs every script and fails unless its output is byte-identical to the committed output block (RC-224); the probe's output is compared only with `--reference-code`, and is otherwise reported as not compared; `--reference-code` without exactly one existing directory, or any other argument, exits with status 2 before anything is checked (RC-226); the scripts it requires are those of `inventory.txt`, and an inventory entry without its file or block, a file or block outside the inventory, or a missing or malformed inventory fails (RC-230: an inventory derived from the appendix keys and the files present passed when a script and its block were deleted together); finally the version labels of the matrix, the specification and the reading order of `research/README.md` must agree (RC-231) |

Run from the repository root, in an isolated virtual environment:

```sh
python -m venv /path/to/venv && /path/to/venv/bin/pip install --require-hashes --no-deps -r research/reproduction/requirements.txt
cp -r research/original/CPE_Forschungspaket_2026-10-16/08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/source_v0_2 /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/check_appendix_scripts.py --reference-code /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/round39_checks.py
```

Every script prints JSON; the committed output follows the script in its appendix, and two consecutive runs are
byte-identical at the pinned versions (Python 3.11.17 and `requirements.txt`). The lock lists the SHA-256 of every
artifact PyPI serves for each pinned version, so pip refuses any other artifact (RC-206). No script reads the network or any
credential.
