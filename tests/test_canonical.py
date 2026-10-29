"""Canonical serialisation and digests (RC-62, T-31 serialisation cases, F-04)."""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cpe.canonical import JsonValue, canonical_bytes, digest_of, require_hex_digest
from cpe.errors import Refusal


def test_key_order_and_whitespace_do_not_change_the_digest() -> None:
    assert digest_of({"b": 1, "a": [1, 2]}) == digest_of({"a": [1, 2], "b": 1})
    assert canonical_bytes({"a": 1}) == b'{"a":1}'


def test_an_added_field_and_a_retyped_field_change_the_digest() -> None:
    base: JsonValue = {"epoch": 1, "nonce": "n"}
    extended: JsonValue = {"epoch": 1, "nonce": "n", "extra": True}
    retyped: JsonValue = {"epoch": "1", "nonce": "n"}
    assert digest_of(base) != digest_of(extended)
    assert digest_of(base) != digest_of(retyped)


def test_non_finite_numbers_and_non_json_values_are_refused() -> None:
    with pytest.raises(Refusal) as refusal:
        canonical_bytes({"x": float("nan")})
    assert refusal.value.reason == "non_finite_number"
    with pytest.raises(Refusal):
        canonical_bytes({"x": object()})  # type: ignore[dict-item]


def test_fixture_f04_non_hex_digest_is_refused() -> None:
    with pytest.raises(Refusal) as refusal:
        require_hex_digest("z" * 64, "reasoning_digest")
    assert refusal.value.reason == "invalid_digest"
    with pytest.raises(Refusal):
        require_hex_digest("ab" * 31, "reasoning_digest")
    assert require_hex_digest("ab" * 32, "reasoning_digest") == "ab" * 32


@given(st.dictionaries(st.text(), st.one_of(st.integers(), st.text(), st.booleans(), st.none())))
def test_canonical_bytes_are_deterministic_and_ascii(value: dict[str, object]) -> None:
    first = canonical_bytes(value)  # type: ignore[arg-type]
    assert first == canonical_bytes(dict(reversed(list(value.items()))))  # type: ignore[arg-type]
    first.decode("ascii")
