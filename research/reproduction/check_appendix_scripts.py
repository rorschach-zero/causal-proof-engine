"""Verify that every script in this directory is byte-identical to the fenced block of the appendix of
`research/16-reconciliation-matrix.md` that records it.

The appendices are the record of what was run in each reconciliation round; the files here are the executables
the reproduction commands of `16` section 2 name. This check is what keeps the two from diverging: it exits
non-zero and names every script that differs, every appendix block whose script is missing, and every script
without an appendix block (RC-136: a check over the files that happen to exist passes when one is deleted). Every
`*.py` file here except this checker is enumerated, so a script whose name has no marker fails too (RC-196: a check
over the files whose names are in MARKERS passes an unregistered or misspelled evidence script). Every key must
have exactly one start and one end marker line, in that order (RC-217: with the last start marker read and the keys
collected into a set, a second, stale block under the same key was never compared). Every script whose source
matches is then run, and its stdout must be byte-identical to the committed output, the one ```json block after its
end marker and before the next script's start marker (RC-224: comparing the source alone passed a stale or
hand-edited output block; RC-240: with only the first of several blocks compared, a second, stale block passed).
The probe needs a scratch copy of the archived reference code; without `--reference-code` its output is reported as
not compared, never as passed, and `--reference-code` without exactly one existing directory, or any other argument,
exits with status 2 before anything is checked (RC-226). The scripts that must exist are read from `inventory.txt`,
a committed list kept apart from the matrix and the directory (RC-230: an inventory derived from the appendix keys and
the files present passed when a script and its appendix block were deleted together); every inventory entry must have
its file and its block, every file and block must be in the inventory, and a missing or malformed inventory fails.
Finally the version labels of the matrix, the specification and the reading order of `research/README.md` must agree
(RC-231: the reading order was left behind three times, RC-137, RC-167, RC-231), and each must occur exactly once
(RC-249: a second, stale label of the same form passed). The OD10 range of the matrix header's Awaiting sentence and
of its section 6 OD10 row must end at the specification version too (RC-277: the header named versions 5 to 41 from
round 45 to round 50, unseen because no check read it), and that OD10 row must hold exactly one entry, citing a
matrix ID, for every specification version from 23, the first it names by number, to the specification version
(RC-280: with the endpoint alone checked, the row asked for approval through version 48 while its record stopped at
version 46 and had never named version 41). Run from the repository root, in the environment of README.md:

    python -I research/reproduction/check_appendix_scripts.py [--reference-code /path/to/scratch/v02]
"""
import re
import subprocess
import sys
from pathlib import Path

MATRIX = Path('research/16-reconciliation-matrix.md')
SPEC = Path('research/17-phase1-amended-specification.md')
README = Path('research/README.md')
HERE = Path(__file__).resolve().parent
MARKERS = {'reconciliation_probes.py': 'probe', 'reassessment_sims.py': 'reassessment'}
MARKERS.update({f'round{n}_checks.py': f'round{n}' for n in range(2, 100)})
INVENTORY = HERE / 'inventory.txt'


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


def output_blocks(text: str, key: str) -> list:
    """Every ```json block after the end marker and before the next script's start marker."""
    end, = marker_lines(text, key, 'end')
    rest = re.split(r'^<!-- \w+-script:start -->$', text[end:], maxsplit=1, flags=re.MULTILINE)[0]
    return [block.split('```', 1)[0] for block in rest.split('```json\n')[1:]]


def output_failure(text: str, key: str, path: Path, args: list) -> str:
    blocks = output_blocks(text, key)
    if len(blocks) != 1:
        return (f'{path.name}: {len(blocks)} committed output blocks after its appendix block, '
                'exactly one is required')
    expected, = blocks
    run = subprocess.run([sys.executable, '-I', str(path), *args], capture_output=True, text=True)
    if run.returncode != 0:
        return f'{path.name}: RUN FAILED with exit code {run.returncode}'
    if run.stdout != expected:
        return f'{path.name}: OUTPUT DIFFERS from the committed output block'
    return ''


def read_inventory() -> dict:
    """File name -> appendix key, one `<file> <key>` pair per line of `inventory.txt`, `#` starting a comment."""
    inventory = {}
    for number, line in enumerate(INVENTORY.read_text(encoding='utf-8').splitlines(), 1):
        fields = line.split('#', 1)[0].split()
        if not fields:
            continue
        if len(fields) != 2 or fields[0] in inventory or MARKERS.get(fields[0]) != fields[1]:
            raise ValueError(f'{INVENTORY.name} line {number}: {line.strip()!r} is not a new `<file> <key>` pair '
                             'with the key defined for that file name')
        inventory[fields[0]] = fields[1]
    return inventory


FIRST_NUMBERED_OD10_VERSION = 23


def od10_record_failures(matrix: str, spec_version: int) -> list:
    """Every specification version from the first the section 6 OD10 row names by number to the current one must
    have exactly one entry there ("and version N ..." or ", version N ..."), and the entry must cite a matrix ID before
    the next entry starts (RC-280: an endpoint check passed a record that named neither version 47 nor 48). An entry
    for any other version is a failure too (RC-314: an entry for a version beyond the specification passed)."""
    row = re.search(r'^\| OD10 \|.*$', matrix, flags=re.MULTILINE)
    if row is None:
        return ['OD10 record: no section 6 OD10 row']
    starts = list(re.finditer(r'(?:\band |, )version (\d+) ', row.group(0)))
    entries = {}
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(row.group(0))
        entries.setdefault(int(match.group(1)), []).append(row.group(0)[match.end():end])
    failures = []
    for version in range(FIRST_NUMBERED_OD10_VERSION, spec_version + 1):
        found = entries.get(version, [])
        if len(found) != 1:
            failures.append(f'OD10 record, version {version}: {len(found)} entries found, exactly one is required')
        elif not re.search(r'RC-\d+', found[0]):
            failures.append(f'OD10 record, version {version}: the entry cites no matrix ID')
    for version in sorted(set(entries) - set(range(FIRST_NUMBERED_OD10_VERSION, spec_version + 1))):
        failures.append(f'OD10 record, version {version}: an entry outside versions '
                        f'{FIRST_NUMBERED_OD10_VERSION} to {spec_version}')
    return failures


def version_failures(matrix: str, spec: str, readme: str) -> list:
    """The matrix version and round, the specification version and round, the two reading-order entries and the
    two OD10 ranges of the matrix must agree, and the OD10 record must reach the specification version. Each label must occur exactly once in its document, so a label that
    cannot be found, and a second label of the same form, are failures too (RC-249: with the first match read, a
    later, stale label passed)."""
    patterns = {
        'matrix': (r'^\*\*Version:\*\* v(\d+), [-\d]+\. \*\*Round:\*\* (\d+) ', matrix, re.MULTILINE),
        'specification': (r'^version (\d+) \(round (\d+):', spec, re.MULTILINE),
        'reading order, matrix': (r'`16-reconciliation-matrix\.md`: [^(]*\(v(\d+), round (\d+):', readme, 0),
        'reading order, specification': (
            r'`17-phase1-amended-specification\.md`: [^(]*\(version (\d+); versions 5 to (\d+) ', readme, 0),
        'matrix Awaiting OD10 range': (
            r'\*\*Awaiting:\*\* [^(]*\(now: approve or revert the version-5 to version-(\d+) diffs', matrix, 0),
        'matrix section 6 OD10 range': (
            r'^\| OD10 \| \*\*Approve or revert the version-5 to version-(\d+) diffs of `17`\*\*', matrix,
            re.MULTILINE),
    }
    labels, failures = {}, []
    for name, (pattern, text, flags) in patterns.items():
        found = list(re.finditer(pattern, text, flags=flags))
        if len(found) != 1:
            failures.append(f'version label {name}: {len(found)} found, exactly one is required')
        else:
            labels[name] = tuple(int(g) for g in found[0].groups())
    if failures:
        return failures
    (mv, mr), (sv, sr), (rv, rr), (rs, rs5), (ma,), (m6,) = (labels[n] for n in patterns)
    stated = {'matrix version / reading order': (mv, rv), 'matrix round / reading order': (mr, rr),
              'matrix round / specification round': (mr, sr), 'specification version / reading order': (sv, rs),
              'specification version / reading-order OD10 range': (sv, rs5),
              'specification version / matrix Awaiting OD10 range': (sv, ma),
              'specification version / matrix section 6 OD10 range': (sv, m6)}
    return ([f'version labels disagree, {name}: {a} and {b}' for name, (a, b) in stated.items() if a != b]
            + od10_record_failures(matrix, sv))


def parse_reference(argv: list) -> list:
    """[] without arguments, [path] for exactly `--reference-code <existing directory>`; anything else is an error
    (RC-226: a valueless option was read as no option, so the probe output went uncompared with exit status 0)."""
    if not argv:
        return []
    if len(argv) != 2 or argv[0] != '--reference-code' or argv[1].startswith('--'):
        raise ValueError(f'invalid arguments {argv}; usage: [--reference-code /path/to/scratch/v02]')
    if not Path(argv[1]).is_dir():
        raise ValueError(f'--reference-code {argv[1]}: not a directory')
    return argv[1:]


def main(argv: list) -> int:
    try:
        reference = parse_reference(argv)
    except ValueError as error:
        print(error)
        return 2
    text = MATRIX.read_text(encoding='utf-8')
    keys = set(re.findall(r'^<!-- (\w+)-script:start -->$', text, flags=re.MULTILINE))
    files = {p.name for p in HERE.glob('*.py') if p.name != Path(__file__).name}
    failures = unrun = 0
    try:
        inventory = read_inventory()
    except FileNotFoundError:
        print(f'{INVENTORY.name}: MISSING, so no script is known to be required')
        failures += 1
        inventory = {}
    except (OSError, UnicodeDecodeError, ValueError) as error:
        print(error if isinstance(error, ValueError) else f'{INVENTORY.name}: unreadable ({type(error).__name__})')
        failures += 1
        inventory = {}
    present = {name for name, key in MARKERS.items() if key in keys} | (files & set(MARKERS))
    for name in sorted(present - set(inventory)):
        print(f'{name}: not in {INVENTORY.name}')
        failures += 1
    expected = present | set(inventory)
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
    for name in sorted(expected):
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
        elif fenced_block(text, key) != path.read_text(encoding='utf-8'):
            print(f'{name}: DIFFERS from the appendix block')
            failures += 1
        elif key == 'probe' and not reference:
            print(f'{name}: identical to the appendix block; output NOT compared (needs --reference-code)')
            unrun += 1
        elif failure := output_failure(text, key, path, reference if key == 'probe' else []):
            print(failure)
            failures += 1
        else:
            print(f'{name}: identical to the appendix block, output identical to the committed output')
    for line in version_failures(text, SPEC.read_text(encoding='utf-8'), README.read_text(encoding='utf-8')):
        print(line)
        failures += 1
    print(f'{len(inventory)} inventory entries, {len(keys)} appendix blocks, {len(files)} scripts checked, '
          f'{unrun} outputs not compared, {failures} failures')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
