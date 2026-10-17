"""Verify that every script in this directory is byte-identical to the fenced block of the appendix of
`research/16-reconciliation-matrix.md` that records it.

The appendices are the record of what was run in each reconciliation round; the files here are the executables
the reproduction commands of `16` section 2 name. This check is what keeps the two from diverging: it exits
non-zero and names the first script that differs. Run from the repository root:

    python -I research/reproduction/check_appendix_scripts.py
"""
import sys
from pathlib import Path

MATRIX = Path('research/16-reconciliation-matrix.md')
HERE = Path(__file__).resolve().parent
MARKERS = {'reconciliation_probes.py': 'probe'}
MARKERS.update({f'round{n}_checks.py': f'round{n}' for n in range(2, 100)})


def fenced_block(text: str, key: str) -> str:
    start = text.rindex(f'<!-- {key}-script:start -->')
    end = text.index(f'<!-- {key}-script:end -->', start)
    return text[start:end].split('```python\n', 1)[1].rsplit('```', 1)[0]


def main() -> int:
    text = MATRIX.read_text(encoding='utf-8')
    scripts = sorted(p for p in HERE.glob('*.py') if p.name in MARKERS)
    failures = 0
    for path in scripts:
        key = MARKERS[path.name]
        if f'<!-- {key}-script:start -->' not in text:
            print(f'{path.name}: no appendix block with marker {key}-script')
            failures += 1
            continue
        if fenced_block(text, key) == path.read_text(encoding='utf-8'):
            print(f'{path.name}: identical to the appendix block')
        else:
            print(f'{path.name}: DIFFERS from the appendix block')
            failures += 1
    print(f'{len(scripts)} scripts checked, {failures} differ')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
