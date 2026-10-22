"""Mutation-testing report: survivor evidence, classification and scores (``research/19`` section 10).

Two steps, both reproducible:

1. ``collect`` reads mutmut's working copy (``mutants/``, written by ``mutmut run``) and the output of
   ``mutmut results --all true``, and writes every mutant that was not killed as evidence: its status and the
   source lines it changes against the original function, with each original function once. Run it in the
   directory where ``mutmut run`` ran.
2. ``classify`` reads that evidence, the results and the hand classification (``manual.tsv``), classifies every
   surviving mutant, writes the per-mutant table and prints the totals and the per-module scores. It needs no
   mutmut and no ``mutants/`` directory: every input is a committed file.

Categories of a survivor: ``text`` (it changes only a message, a field label used in messages, or record text no
code reads), ``equivalent`` (no input the system can receive tells it from the original), ``tool-limit`` (mutmut
cannot run it or the test that kills it), ``accepted`` (a real difference judged not worth a test, with the reason),
and ``unclassified`` (no rule applies and the hand table names no reason). Rules are
structural, over the Python syntax trees of the original and the mutated function; the hand table gives one reason
per mutant. The raw score is killed over all mutants. The adjusted score is derived from this classification:
detected (killed or timed out) over all mutants minus the text, equivalent and tool-limit survivors; accepted and
unclassified survivors count against it.

Usage::

    python tools/mutation_report.py collect --results R --mutants mutants --out E
    python tools/mutation_report.py classify --results R --evidence E --manual M --table T [--check]
"""
from __future__ import annotations

import argparse
import ast
import csv
import difflib
import json
import re
import sys
from collections import Counter
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

RESULT_LINE = re.compile(r"^\s*(?P<name>\S+): (?P<status>\S.*?)\s*$")
MUTANT_NAME = re.compile(r"^(?P<module>[\w.]+?)\.(?P<function>x(?:_|ǁ).*)__mutmut_(?P<number>\d+)$")
DETECTED = ("killed", "timeout")
CATEGORIES = ("text", "equivalent", "tool-limit", "accepted", "unclassified")


@dataclass(frozen=True)
class Mutant:
    name: str
    module: str
    function: str
    status: str


def parse_name(name: str) -> tuple[str, str]:
    match = MUTANT_NAME.match(name)
    if match is None:
        raise ValueError(f"not a mutmut mutant name: {name}")
    return match["module"], match["function"]


def read_results(path: Path) -> list[Mutant]:
    mutants = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = RESULT_LINE.match(line)
        if match is None:
            continue
        module, function = parse_name(match["name"])
        mutants.append(Mutant(match["name"], module, function, match["status"]))
    if not mutants:
        raise ValueError(f"{path} holds no mutmut result line")
    return mutants


# collect ---------------------------------------------------------------------------------------------------------

def _functions(source: str) -> dict[str, str]:
    """Every function of a mutated module by name, as its source text (decorators excluded)."""
    tree = ast.parse(source)
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            segment = ast.get_source_segment(source, node)
            if segment is not None:
                found[node.name] = segment
    return found


def _rename(source: str, old: str, new: str) -> str:
    return source.replace(f"def {old}(", f"def {new}(", 1)


def _changes(original: str, mutated: str) -> list[list[object]]:
    """The line changes that turn ``original`` into ``mutated``: [first line, last line (exclusive), new lines]."""
    a, b = original.splitlines(), mutated.splitlines()
    return [[i1, i2, b[j1:j2]] for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()
            if tag != "equal"]


def apply_changes(original: str, changes: Sequence[Sequence[object]]) -> str:
    lines = original.splitlines()
    for first, last, new in sorted(changes, key=lambda change: -int(str(change[0]))):
        assert isinstance(first, int) and isinstance(last, int) and isinstance(new, list)
        lines[first:last] = [str(line) for line in new]
    return "\n".join(lines)


def collect(results: Path, mutants_dir: Path, out: Path) -> int:
    survivors = [m for m in read_results(results) if m.status not in DETECTED]
    sources: dict[str, dict[str, str]] = {}
    originals: dict[str, str] = {}
    entries = []
    for mutant in survivors:
        if mutant.module not in sources:
            path = mutants_dir.joinpath(*mutant.module.split(".")).with_suffix(".py")
            if not path.exists():
                path = mutants_dir.joinpath(*mutant.module.split("."), "__init__.py")
            sources[mutant.module] = _functions(path.read_text(encoding="utf-8"))
        functions = sources[mutant.module]
        key = f"{mutant.module}.{mutant.function}"
        number = mutant.name.rsplit("__mutmut_", 1)[1]
        original = _rename(functions[f"{mutant.function}__mutmut_orig"], f"{mutant.function}__mutmut_orig", "f")
        mutated = _rename(functions[f"{mutant.function}__mutmut_{number}"], f"{mutant.function}__mutmut_{number}", "f")
        originals[key] = original
        entries.append({"name": mutant.name, "status": mutant.status, "function": key,
                        "changes": _changes(original, mutated)})
    out.write_text(json.dumps({"functions": dict(sorted(originals.items())), "mutants": entries}, indent=1,
                              ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"collect: {len(entries)} mutants not detected, {len(originals)} functions, written to {out}")
    return 0


# classification rules --------------------------------------------------------------------------------------------

Step = tuple[ast.AST, str, int | None]  # parent node, field, index in the field's list


@dataclass(frozen=True)
class Difference:
    trail: tuple[Step, ...]
    original: object
    mutated: object


def differences(a: object, b: object, trail: tuple[Step, ...] = ()) -> list[Difference]:
    """The minimal differing positions of two syntax trees."""
    if isinstance(a, ast.AST) and isinstance(b, ast.AST):
        if type(a) is not type(b):
            return [Difference(trail, a, b)]
        if isinstance(a, ast.Constant) and isinstance(b, ast.Constant):
            same = type(a.value) is type(b.value) and a.value == b.value
            return [] if same else [Difference(trail, a, b)]
        found: list[Difference] = []
        for name in a._fields:
            left, right = getattr(a, name, None), getattr(b, name, None)
            if isinstance(left, list) and isinstance(right, list):
                if len(left) != len(right):
                    found.append(Difference(trail + ((a, name, None),), left, right))
                    continue
                for index, (x, y) in enumerate(zip(left, right)):
                    found += differences(x, y, trail + ((a, name, index),))
            else:
                found += differences(left, right, trail + ((a, name, None),))
        return found
    return [] if a == b else [Difference(trail, a, b)]


def _callee(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        owner = func.value.id if isinstance(func.value, ast.Name) else ""
        return f"{owner}.{func.attr}" if owner else func.attr
    return ""


# Calls whose argument at the given position is a label used in refusal messages only.
LABEL_ARGUMENT: dict[str, int] = {
    "require_identifier": 1, "require_identifier_tuple": 1, "require_probability": 1, "require_non_negative_number": 1,
    "require_json": 1, "require_non_negative_int": 1, "require_timestamp": 1, "optional_timestamp": 1,
    "require_date": 1, "require_digest": 1, "require_hex_digest": 1, "parse_timestamp": 1, "_require_bool": 1,
    "_choice": 1, "_require_choice": 1, "require_predicate_kind": 1, "require_comparator": 1, "require_mapping": 1,
    "require_keys": 1, "_check_json": 1,
}
# Calls whose argument at or after the given position is human-readable text that no code reads.
TEXT_ARGUMENT: dict[str, int] = {
    "Refusal": 1, "log.warning": 0, "log.info": 0, "log.error": 0, "log.debug": 0, "Defect": 1, "Incident": 2,
    "AbortRecord": 1, "Problem": 2, "_not_after": 1, "self._rotate": 0, "self._abort": 1, "AssertionError": 0,
    "_DuplicateKey": 0, "VerificationReport": 4,
}
TEXT_KEYWORDS = frozenset({"detail"})
LABEL_PARAMETERS = frozenset({"field", "path", "schema", "what"})
TEXT_NAMES = frozenset({"basis", "absence_basis", "detail", "aborted"})
DISPOSITIONS = frozenset({"OPEN", "RESOLVED_YES", "RESOLVED_NO", "EXPIRED_NO", "VOID"})
CODEC_NAMES = frozenset({"ascii", "utf-8"})
SQL_START = re.compile(r"^\s*(SELECT|INSERT|DELETE|CREATE|BEGIN|COMMIT|ROLLBACK)\b", re.IGNORECASE)


def _sink(step: Step, outer: Step | None) -> str | None:
    """The rule under which the expression at ``step`` is a message, a label or record text, or None."""
    parent, field, index = step
    if isinstance(parent, ast.Call) and field == "args" and index is not None:
        callee = _callee(parent)
        short = callee.rsplit(".", 1)[-1]
        if short in LABEL_ARGUMENT and index == LABEL_ARGUMENT[short]:
            return f"field label of {short}"
        if callee in TEXT_ARGUMENT and index >= TEXT_ARGUMENT[callee]:
            return f"text argument of {callee}"
    if isinstance(parent, ast.keyword) and parent.arg in TEXT_KEYWORDS:
        return f"keyword {parent.arg}"
    if isinstance(parent, ast.arguments) and field == "defaults" and index is not None:
        positional = [*parent.posonlyargs, *parent.args]
        name = positional[len(positional) - len(parent.defaults) + index].arg
        if name in LABEL_PARAMETERS:
            return f"default label {name}"
    if isinstance(parent, ast.Assign) and field == "value":
        targets = [t.id for t in parent.targets if isinstance(t, ast.Name)]
        if targets and all(t in TEXT_NAMES for t in targets):
            return f"assigned to {targets[0]}"
    if (isinstance(parent, ast.Tuple) and field == "elts" and index is not None and outer is not None
            and isinstance(outer[0], ast.Assign) and outer[1] == "value" and isinstance(outer[0].targets[0], ast.Tuple)):
        names = [e.id if isinstance(e, ast.Name) else "" for e in outer[0].targets[0].elts]
        if len(names) > index and names[index] in TEXT_NAMES:
            return f"assigned to {names[index]}"
    if isinstance(parent, ast.Tuple) and field == "elts" and index == 2 and parent.elts:
        head = parent.elts[0]
        if isinstance(head, ast.Constant) and head.value in DISPOSITIONS:
            return "adjudication basis"
        if outer is not None and isinstance(outer[0], ast.Assign) and isinstance(outer[0].targets[0], ast.Tuple):
            names = [e.id for e in outer[0].targets[0].elts if isinstance(e, ast.Name)]
            if len(names) > index and names[index] in TEXT_NAMES:
                return "adjudication basis"
    return None


def _text_context(trail: tuple[Step, ...]) -> str | None:
    """The rule under which a change at the end of ``trail`` only changes text: some enclosing expression is a
    message argument, a label, or record text that no code reads."""
    for position in range(len(trail) - 1, -1, -1):
        found = _sink(trail[position], trail[position - 1] if position else None)
        if found is not None:
            return found
    return None


def _removed_text_argument(difference: Difference) -> str | None:
    """A call that lost one argument, where the lost argument is a message or a label."""
    if not difference.trail or not isinstance(difference.original, list) or not isinstance(difference.mutated, list):
        return None
    parent, field, _ = difference.trail[-1]
    if not isinstance(parent, ast.Call) or field != "args" or len(difference.original) != len(difference.mutated) + 1:
        return None
    dumps_a = [ast.dump(x) for x in difference.original]
    dumps_b = [ast.dump(x) for x in difference.mutated]
    removed = next((i for i in range(len(dumps_b)) if dumps_a[i] != dumps_b[i]), len(dumps_b))
    if dumps_a[:removed] + dumps_a[removed + 1:] != dumps_b:
        return None
    return _sink((parent, "args", removed), None)


def _is_cast_type(trail: tuple[Step, ...]) -> bool:
    return any(isinstance(node, ast.Call) and _callee(node) == "cast" and field == "args" and index == 0
               for node, field, index in trail)


def rule_for(original_source: str, mutated_source: str) -> tuple[str, str] | None:
    """(category, rule) when a structural rule classifies the mutant; None otherwise."""
    a, b = ast.parse(original_source).body[0], ast.parse(mutated_source).body[0]
    found = differences(a, b)
    if not found:
        return "equivalent", "identical syntax tree"
    rules: list[tuple[str, str]] = []
    for difference in found:
        left, right = difference.original, difference.mutated
        removed = _removed_text_argument(difference)
        if removed is not None:
            rules.append(("text", removed))
            continue
        if _is_cast_type(difference.trail):
            rules.append(("equivalent", "type argument of typing.cast, no runtime effect"))
            continue
        if (isinstance(left, ast.Constant) and isinstance(right, ast.Constant) and isinstance(left.value, str)
                and isinstance(right.value, str) and left.value.lower() == right.value.lower()):
            if left.value.lower() in CODEC_NAMES:
                rules.append(("equivalent", "codec name case; Python codec lookup ignores case"))
                continue
            if SQL_START.match(left.value):
                rules.append(("equivalent", "SQL keyword case; SQL keywords ignore case"))
                continue
        context = _text_context(difference.trail)
        if context is None:
            return None
        rules.append(("text", context))
    categories = {category for category, _ in rules}
    category = "equivalent" if categories == {"equivalent"} else "text"
    return category, "; ".join(sorted({rule for _, rule in rules}))


# classify --------------------------------------------------------------------------------------------------------

def read_manual(path: Path) -> dict[str, tuple[str, str]]:
    table: dict[str, tuple[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader((line for line in handle if not line.startswith("#")), delimiter="\t"):
            category = row["category"]
            if category not in CATEGORIES[:-1]:
                raise ValueError(f"{row['name']}: unknown category {category!r}")
            if not row["reason"].strip():
                raise ValueError(f"{row['name']}: a hand classification states its reason")
            table[row["name"]] = (category, row["reason"].strip())
    return table


def classify_all(evidence: dict[str, object], manual: dict[str, tuple[str, str]]) -> list[tuple[str, str, str, str]]:
    functions = evidence["functions"]
    entries = evidence["mutants"]
    assert isinstance(functions, dict) and isinstance(entries, list)
    rows = []
    for entry in entries:
        if entry["status"] != "survived":
            continue
        name = entry["name"]
        original = functions[entry["function"]]
        mutated = apply_changes(original, entry["changes"])
        if name in manual:
            category, reason = manual[name]
            rows.append((name, category, "hand", reason))
            continue
        ruled = rule_for(original, mutated)
        if ruled is None:
            rows.append((name, "unclassified", "", ""))
        else:
            rows.append((name, ruled[0], "rule", ruled[1]))
    return rows


def _iter_table(rows: Sequence[tuple[str, str, str, str]]) -> Iterator[str]:
    yield "name\tcategory\tsource\treason"
    for row in sorted(rows):
        yield "\t".join(row)


def classify(results: Path, evidence_path: Path, manual_path: Path, table: Path, check: bool) -> int:
    mutants = read_results(results)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    manual = read_manual(manual_path)
    rows = classify_all(evidence, manual)
    unknown = set(manual) - {row[0] for row in rows}
    if unknown:
        raise ValueError(f"the hand table names mutants that did not survive: {sorted(unknown)[:5]}")
    text = "\n".join(_iter_table(rows)) + "\n"
    if check:
        if table.read_text(encoding="utf-8") != text:
            print(f"classify: {table} differs from the classification of the committed evidence")
            return 1
    else:
        table.write_text(text, encoding="utf-8")
    category_of = {row[0]: row[1] for row in rows}
    status = Counter(m.status for m in mutants)
    print(f"mutants: {len(mutants)}; " + ", ".join(f"{k}: {v}" for k, v in sorted(status.items())))
    survived = Counter(category_of.values())
    print("survivors by category: " + ", ".join(f"{c}: {survived.get(c, 0)}" for c in CATEGORIES))
    print("module\tmutants\tkilled\ttimeout\tsurvived\tother\traw\texcluded\tadjusted")
    modules = sorted({m.module for m in mutants})
    for module in [*modules, "total"]:
        group = [m for m in mutants if module in ("total", m.module)]
        killed = sum(m.status == "killed" for m in group)
        timeout = sum(m.status == "timeout" for m in group)
        survived_here = sum(m.status == "survived" for m in group)
        other = len(group) - killed - timeout - survived_here
        excluded = sum(category_of.get(m.name) in ("text", "equivalent", "tool-limit") for m in group)
        raw = killed / len(group)
        denominator = len(group) - excluded
        adjusted = (killed + timeout) / denominator if denominator else 1.0
        print(f"{module.removeprefix('cpe.')}\t{len(group)}\t{killed}\t{timeout}\t{survived_here}\t{other}\t"
              f"{raw:.2%}\t{excluded}\t{adjusted:.2%}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    commands = parser.add_subparsers(dest="command", required=True)
    collect_parser = commands.add_parser("collect")
    collect_parser.add_argument("--results", type=Path, required=True)
    collect_parser.add_argument("--mutants", type=Path, default=Path("mutants"))
    collect_parser.add_argument("--out", type=Path, required=True)
    classify_parser = commands.add_parser("classify")
    classify_parser.add_argument("--results", type=Path, required=True)
    classify_parser.add_argument("--evidence", type=Path, required=True)
    classify_parser.add_argument("--manual", type=Path, required=True)
    classify_parser.add_argument("--table", type=Path, required=True)
    classify_parser.add_argument("--check", action="store_true", help="compare with the committed table, write nothing")
    args = parser.parse_args(argv)
    if args.command == "collect":
        return collect(args.results, args.mutants, args.out)
    return classify(args.results, args.evidence, args.manual, args.table, args.check)


if __name__ == "__main__":
    sys.exit(main())
