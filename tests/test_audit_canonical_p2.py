"""Whole-codebase audit (issue #37): the P2 findings in the canonical form.

- Pass 4 K1: a string holding surrogate code points had the canonical form of another string:
  ``chr(0xD800) + chr(0xDC00)`` and ``chr(0x10000)`` gave the same bytes and the same digest.
- Pass 4 K2: as dictionary keys, the two merged into one key in the ledger, and one value was lost without a refusal
  (``AGENTS.md`` section 6).
- Pass 3 C-d: a ``list`` subclass whose ``__iter__`` shows nothing was digested as ``[]``, whatever it held.

Every test but the last failed on the pass-4 commit ``c3d6233dbaeb71eb71cb128394099b23cef285b5``; the
``OrderedDict`` case fails there because it states a reading, not a defect."""
from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpe.canonical import canonical_bytes, digest_of
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger

PAIR = chr(0xD800) + chr(0xDC00)  # two surrogate code points
ASTRAL = chr(0x10000)  # one code point, which JSON escapes as the same pair


@pytest.mark.parametrize("value", [PAIR, chr(0xD800), "a" + chr(0xDFFF), {PAIR: 1}, [ASTRAL, PAIR]])
def test_k1_a_surrogate_code_point_is_refused(value: object) -> None:
    with pytest.raises(Refusal) as refused:
        canonical_bytes(value)  # type: ignore[arg-type]  # at c3d6233: the canonical form of another string
    assert refused.value.reason == "surrogate_code_point"


def test_k1_two_different_strings_never_share_a_digest() -> None:
    assert PAIR != ASTRAL
    try:
        pair_digest = digest_of(PAIR)
    except Refusal:
        return
    assert pair_digest != digest_of(ASTRAL)  # at c3d6233: equal


def test_k2_append_never_merges_two_keys(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(datetime(2026, 1, 1, tzinfo=timezone.utc)))
    with pytest.raises(Refusal):
        ledger.append("note", "n-1", {PAIR: 1, ASTRAL: 2})  # at c3d6233: admitted as {ASTRAL: 2}
    assert ledger.records() == ()


class HiddenList(list):  # type: ignore[type-arg]
    def __iter__(self) -> Iterator[object]:
        return iter(())


class HiddenDict(dict):  # type: ignore[type-arg]
    def items(self):  # type: ignore[no-untyped-def]
        return iter(())


@pytest.mark.parametrize("value", [HiddenList([1, object(), float("nan")]), HiddenDict({"a": object()})])
def test_cd_a_container_subclass_is_refused(value: object) -> None:
    with pytest.raises(Refusal) as refused:
        canonical_bytes({"x": value})  # type: ignore[dict-item]  # at c3d6233: [] for the list, a TypeError for the dict
    assert refused.value.reason == "not_json"


def test_cd_every_container_subclass_is_refused_even_a_faithful_one() -> None:
    """A reading: the canonical form takes plain containers only, so a subclass that serialises as it iterates is
    refused too, rather than told apart from one that does not."""
    with pytest.raises(Refusal):
        canonical_bytes({"x": OrderedDict(a=1)})


def test_guard_astral_text_and_plain_containers_keep_their_form() -> None:
    assert canonical_bytes({"k": [ASTRAL, "é", 1]}) == b'{"k":["\\ud800\\udc00","\\u00e9",1]}'
