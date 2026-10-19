# Reproduction scripts of the reconciliation matrix

One committed file per appendix of `research/16-reconciliation-matrix.md`, byte-identical to the fenced block
between that appendix's `<!-- <key>-script:start -->` and `<!-- <key>-script:end -->` markers. These are evidence
scripts for the research documents, not project code: nothing under `cpe/` (when it exists) may import them.

| File | Appendix | Needs |
|---|---|---|
| `reconciliation_probes.py` | A (output in B) | a scratch copy of the archived v0.2 reference code, passed as the first argument; the pinned packages, httpx and its dependencies included (the archived `cpe.saxo_sim` imports httpx) |
| `round2_checks.py` to `round21_checks.py`, `round23_checks.py` to `round47_checks.py` (round 22 had none) | C to V, W to Z, AA to AU | numpy and scipy of the pinned packages (`round42_checks.py` needs neither); `round38_checks.py`, `round39_checks.py`, `round40_checks.py` and `round42_checks.py` also read committed fixtures (below), and none reads Git history (RC-236: until round 39 two of them ran `git show` on commits that a squash merge leaves unreachable, and `round38_checks.py` ran the working checker) |
| `fixtures/` | AL, AM, AN, AP | historical inputs, each pinned by its SHA-256 in the script that reads it: the checkers of `98b03fc` and `784183f` byte for byte (Git blob ids `8ca4817f` and `c2b2c453`), the checker of round 40 (`check_appendix_scripts.round40.py.txt`, identical to `check_appendix_scripts.py` of the round-40 and round-41 commits), the checker of round 42 (`check_appendix_scripts.round42.py.txt`, identical to `check_appendix_scripts.py` of the round-42 commit), and for `3fe4b06` and `98b03fc` the lines of the matrix, the specification and `research/README.md` that the version-label check reads, the line of each first match of its four patterns, on which it returns what it returns on the full documents (RC-236) |
| `inventory.txt` | — | the committed list of the scripts above with their appendix keys (RC-230); a round with a script appends its line |
| `check_appendix_scripts.py` | — | the pinned packages, since it runs every script; verifies every file above against its appendix block, and fails on an appendix block without its file, a file without its block, any other `*.py` file here (RC-196), and a key without exactly one start and one end marker line (RC-217); then runs every script and fails unless its output is byte-identical to the committed output block, of which each appendix must hold exactly one (RC-224, RC-240); the probe's output is compared only with `--reference-code`, and is otherwise reported as not compared; `--reference-code` without exactly one existing directory, or any other argument, exits with status 2 before anything is checked (RC-226); the scripts it requires are those of `inventory.txt`, and an inventory entry without its file or block, a file or block outside the inventory, or a missing or malformed inventory fails (RC-230: an inventory derived from the appendix keys and the files present passed when a script and its block were deleted together); finally the version labels of the matrix, the specification and the reading order of `research/README.md` must agree (RC-231), and each must occur exactly once in its document (RC-249) |

Run from the repository root, in an isolated virtual environment:

```sh
python -m venv /path/to/venv && /path/to/venv/bin/pip install --require-hashes --no-deps -r research/reproduction/requirements.txt
cp -r research/original/CPE_Forschungspaket_2026-10-16/08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/source_v0_2 /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/check_appendix_scripts.py --reference-code /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/round47_checks.py
```

Every script prints JSON; the committed output follows the script in its appendix, and two consecutive runs are
byte-identical at the pinned versions (Python 3.11.17 and `requirements.txt`). The lock lists the SHA-256 of every
artifact PyPI serves for each pinned version, so pip refuses any other artifact (RC-206). No script reads the network or any
credential.
