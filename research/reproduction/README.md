# Reproduction scripts of the reconciliation matrix

One committed file per appendix of `research/16-reconciliation-matrix.md`, byte-identical to the fenced block
between that appendix's `<!-- <key>-script:start -->` and `<!-- <key>-script:end -->` markers. These are evidence
scripts for the research documents, not project code: nothing under `cpe/` (when it exists) may import them.

| File | Appendix | Needs |
|---|---|---|
| `reconciliation_probes.py` | A (output in B) | a scratch copy of the archived v0.2 reference code, passed as the first argument; httpx and pytest beside the pinned packages |
| `round2_checks.py` to `round11_checks.py` | C to L | nothing beyond the pinned packages |
| `check_appendix_scripts.py` | — | nothing; verifies every file above against its appendix block |

Run from the repository root, in an isolated virtual environment:

```sh
python -m venv /path/to/venv && /path/to/venv/bin/pip install -r research/reproduction/requirements.txt
/path/to/venv/bin/python -I research/reproduction/check_appendix_scripts.py
/path/to/venv/bin/python -I research/reproduction/round11_checks.py
```

Every script prints JSON; the committed output follows the script in its appendix, and two consecutive runs are
byte-identical at the pinned versions (Python 3.11.17, numpy 2.4.6, scipy 1.17.1). No script reads the network or any
credential.
