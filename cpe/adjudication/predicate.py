"""Evaluation of a registered predicate (record selector, field, comparator, value) over archived content.

Phase 1 reading of the predicate (hand-off section 3.1; each point is listed for the owner in the PR):
- One media type, ``application/json``, in the canonical byte form of ``cpe.canonical``; other bytes or another
  media type are typed refusals, never parsed by guess.
- The content is a JSON object whose keys are the source's record keys; ``record_selector`` names one key and
  ``field`` one key of the record it selects. A selector or field that matches nothing is no evidence (``None``),
  never a NO.
- ``eq``, ``ne`` and ``in`` compare JSON values exactly: a boolean equals only a boolean, numbers compare by value,
  lists and objects element by element. ``lt``, ``le``, ``gt`` and ``ge`` compare numbers only; any other pair is
  a typed refusal.
- A predicate that holds yields the claim ``occurred``, one that does not hold ``not-occurred``.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from types import MappingProxyType

from cpe.adjudication.content import ArchivedContent
from cpe.adjudication.records import Claim
from cpe.canonical import JsonValue, canonical_bytes
from cpe.errors import Refusal
from cpe.schemas.event import ResolutionPredicate

MEDIA_TYPE_JSON = "application/json"
SUPPORTED_MEDIA_TYPES: tuple[str, ...] = (MEDIA_TYPE_JSON,)


def _number(value: JsonValue) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def json_equal(left: JsonValue, right: JsonValue) -> bool:
    """Equality of JSON values without Python's ``True == 1``."""
    if _number(left) and _number(right):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(json_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(json_equal(left[k], right[k]) for k in left)
    return left == right


def _order(test: Callable[[float, float], bool]) -> Callable[[JsonValue, JsonValue], bool]:
    def compare(observed: JsonValue, registered: JsonValue) -> bool:
        if not (_number(observed) and _number(registered)):
            raise Refusal("incomparable_values", f"an order comparison needs two numbers, not {observed!r} and "
                          f"{registered!r}")
        assert isinstance(observed, (int, float)) and isinstance(registered, (int, float))
        return test(observed, registered)
    return compare


def _member(observed: JsonValue, registered: JsonValue) -> bool:
    assert isinstance(registered, list)  # ResolutionPredicate refuses 'in' without a non-empty list
    return any(json_equal(observed, item) for item in registered)


COMPARATORS: Mapping[str, Callable[[JsonValue, JsonValue], bool]] = MappingProxyType({
    "eq": json_equal,
    "ne": lambda observed, registered: not json_equal(observed, registered),
    "lt": _order(lambda a, b: a < b),
    "le": _order(lambda a, b: a <= b),
    "gt": _order(lambda a, b: a > b),
    "ge": _order(lambda a, b: a >= b),
    "in": _member,
})


def _no_duplicate_keys(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    mapping: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in mapping:
            raise Refusal("non_canonical_content", f"the content repeats the key {key!r}")
        mapping[key] = value
    return mapping


def _refuse_constant(name: str) -> JsonValue:
    raise Refusal("non_canonical_content", f"the content holds {name}, which is not JSON")


def parse_content(content: ArchivedContent) -> dict[str, JsonValue]:
    """The JSON object the archived bytes encode, refused unless the bytes are its canonical form."""
    if content.media_type not in SUPPORTED_MEDIA_TYPES:
        raise Refusal("unsupported_media_type", f"{content.media_type!r} cannot be evaluated in Phase 1 (supported: "
                      f"{', '.join(SUPPORTED_MEDIA_TYPES)})")
    try:
        parsed: JsonValue = json.loads(content.content.decode("ascii"), object_pairs_hook=_no_duplicate_keys,
                                       parse_constant=_refuse_constant)
    except Refusal:
        raise
    except ValueError:  # UnicodeDecodeError and JSONDecodeError both
        raise Refusal("non_canonical_content", "the content is not ASCII JSON") from None
    if canonical_bytes(parsed) != content.content:
        raise Refusal("non_canonical_content", "the content is not in the canonical byte form of cpe.canonical")
    if not isinstance(parsed, dict):
        raise Refusal("invalid_content_structure", "the content is a JSON object keyed by record")
    return parsed


def evaluate(predicate: ResolutionPredicate, content: ArchivedContent) -> Claim | None:
    """The claim the archived content supports under the registered predicate, or None when it holds no evidence."""
    if content.source_id != predicate.source:
        raise Refusal("wrong_source", f"the content is from {content.source_id}, the predicate reads {predicate.source}")
    comparator = COMPARATORS.get(predicate.comparator)
    if comparator is None:
        raise Refusal("unsupported_comparator", f"{predicate.comparator!r} cannot be evaluated")
    records = parse_content(content)
    if predicate.record_selector not in records:
        return None
    selected = records[predicate.record_selector]
    if not isinstance(selected, dict):
        raise Refusal("invalid_content_structure", f"the record {predicate.record_selector!r} is not a JSON object")
    if predicate.field not in selected:
        return None
    return "occurred" if comparator(selected[predicate.field], predicate.value) else "not-occurred"
