# Reproduction scripts of the reconciliation matrix

One committed file per appendix of `research/16-reconciliation-matrix.md`, byte-identical to the fenced block
between that appendix's `<!-- <key>-script:start -->` and `<!-- <key>-script:end -->` markers. These are evidence
scripts for the research documents, not project code: nothing under `cpe/` (when it exists) may import them.

| File | Appendix | Needs |
|---|---|---|
| `reconciliation_probes.py` | A (output in B) | a scratch copy of the archived v0.2 reference code, passed as the first argument; the pinned packages, httpx and its dependencies included (the archived `cpe.saxo_sim` imports httpx) |
| `round2_checks.py` to `round14_checks.py` | C to O | numpy and scipy of the pinned packages |
| `check_appendix_scripts.py` | — | nothing; verifies every file above against its appendix block, and fails on an appendix block without its file or a file without its block |

Run from the repository root, in an isolated virtual environment:

```sh
python -m venv /path/to/venv && /path/to/venv/bin/pip install -r research/reproduction/requirements.txt
/path/to/venv/bin/python -I research/reproduction/check_appendix_scripts.py
/path/to/venv/bin/python -I research/reproduction/round14_checks.py
cp -r research/original/CPE_Forschungspaket_2026-10-16/08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/source_v0_2 /path/to/scratch/v02
/path/to/venv/bin/python -I research/reproduction/reconciliation_probes.py /path/to/scratch/v02
```

Every script prints JSON; the committed output follows the script in its appendix, and two consecutive runs are
byte-identical at the pinned versions (Python 3.11.17 and `requirements.txt`). No script reads the network or any
credential.
