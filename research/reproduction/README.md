# Reproduction scripts of the reconciliation matrix

One committed file per appendix of `research/16-reconciliation-matrix.md`, byte-identical to the fenced block
between that appendix's `<!-- <key>-script:start -->` and `<!-- <key>-script:end -->` markers. These are evidence
scripts for the research documents, not project code: nothing under `cpe/` (when it exists) may import them.

| File | Appendix | Needs |
|---|---|---|
| `reconciliation_probes.py` | A (output in B) | a scratch copy of the archived v0.2 reference code, passed as the first argument; the pinned packages, httpx and its dependencies included (the archived `cpe.saxo_sim` imports httpx) |
| `round2_checks.py` to `round21_checks.py`, `round23_checks.py` to `round37_checks.py` (round 22 had none) | C to V, W to Z, AA to AK | numpy and scipy of the pinned packages |
| `check_appendix_scripts.py` | — | the pinned packages, since it runs every script; verifies every file above against its appendix block, and fails on an appendix block without its file, a file without its block, any other `*.py` file here (RC-196), and a key without exactly one start and one end marker line (RC-217); then runs every script and fails unless its output is byte-identical to the committed output block (RC-224); the probe's output is compared only with `--reference-code`, and is otherwise reported as not compared; `--reference-code` without exactly one existing directory, or any other argument, exits with status 2 before anything is checked (RC-226) |

Run from the repository root, in an isolated virtual environment:

```sh
python -m venv /path/to/venv && /path/to/venv/bin/pip install --require-hashes --no-deps -r research/reproduction/requirements.txt
cp -r research/original/CPE_Forschungspaket_2026-10-16/08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/source_v0_2 /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/check_appendix_scripts.py --reference-code /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/round37_checks.py
```

Every script prints JSON; the committed output follows the script in its appendix, and two consecutive runs are
byte-identical at the pinned versions (Python 3.11.17 and `requirements.txt`). The lock lists the SHA-256 of every
artifact PyPI serves for each pinned version, so pip refuses any other artifact (RC-206). No script reads the network or any
credential.
