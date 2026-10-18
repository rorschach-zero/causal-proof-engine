"""Verify that every script in this directory is byte-identical to the fenced block of the appendix of
`research/16-reconciliation-matrix.md` that records it.

The appendices are the record of what was run in each reconciliation round; the files here are the executables
the reproduction commands of `16` section 2 name. This check is what keeps the two from diverging: it exits
non-zero and names every script that differs, every appendix block whose script is missing, and every script
without an appendix block (RC-136: a check over the files that happen to exist passes when one is deleted). Every
`*.py` file here except this checker is enumerated, so a script whose name has no marker fails too (RC-196: a check
over the files whose names are in MARKERS passes an unregistered or misspelled evidence script). Every key must
have exactly one start and one end marker line, in that order (RC-217: with the last start marker read and the keys
collected into a set, a second, stale block under the same key was never compared). Run from the repository
root:

    python -I research/reproduction/check_appendix_scripts.py
"""
import re
import sys
from pathlib import Path

MATRIX = Path('research/16-reconciliation-matrix.md')
HERE = Path(__file__).resolve().parent
MARKERS = {'reconciliation_probes.py': 'probe'}
MARKERS.update({f'round{n}_checks.py': f'round{n}' for n in range(2, 100)})


def marker_lines(text: str, key: str, kind: str) -> list:
    return [m.start() for m in re.finditer(rf'^<!-- {key}-script:{kind} -->$', text, flags=re.MULTILINE)]


def marker_failures(text: str) -> dict:
    keys = set(re.findall(r'^<!-- (\w+)-script:(?:start|end) -->$', text, flags=re.MULTILINE))
    failures = {}
    for key in sorted(keys):
        starts, ends = marker_lines(text, key, 'start'), marker_lines(text, key, 'end')
        if len(starts) != 1 or len(ends) != 1:
            failures[key] = (f'appendix block {key}-script: {len(starts)} start and {len(ends)} end markers, '
                             'exactly one of each is required')
        elif ends[0] < starts[0]:
            failures[key] = f'appendix block {key}-script: end marker precedes start marker'
    return failures


def fenced_block(text: str, key: str) -> str:
    start, = marker_lines(text, key, 'start')
    end, = marker_lines(text, key, 'end')
    return text[start:end].split('```python\n', 1)[1].rsplit('```', 1)[0]


def main() -> int:
    text = MATRIX.read_text(encoding='utf-8')
    keys = set(re.findall(r'^<!-- (\w+)-script:start -->$', text, flags=re.MULTILINE))
    files = {p.name for p in HERE.glob('*.py') if p.name != Path(__file__).name}
    expected = {name for name, key in MARKERS.items() if key in keys}
    failures = 0
    malformed = marker_failures(text)
    for line in malformed.values():
        print(line)
        failures += 1
    for name in sorted(files - set(MARKERS)):
        print(f'{name}: no appendix marker is defined for this file name')
        failures += 1
    for key in sorted(keys - set(MARKERS.values())):
        print(f'appendix block {key}-script: no script name is defined for this marker')
        failures += 1
    for name in sorted(expected | (files & set(MARKERS))):
        key = MARKERS[name]
        path = HERE / name
        if name not in files:
            print(f'{name}: MISSING, appendix block {key}-script has no committed file')
            failures += 1
        elif key not in keys:
            print(f'{name}: no appendix block with marker {key}-script')
            failures += 1
        elif key in malformed:
            print(f'{name}: not compared, its appendix markers are malformed')
        elif fenced_block(text, key) == path.read_text(encoding='utf-8'):
            print(f'{name}: identical to the appendix block')
        else:
            print(f'{name}: DIFFERS from the appendix block')
            failures += 1
    print(f'{len(keys)} appendix blocks, {len(files)} scripts checked, {failures} failures')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
