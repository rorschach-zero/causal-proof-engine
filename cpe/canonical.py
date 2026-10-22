"""Canonical serialisation and digests.

Every digest in the system is taken over one canonical byte form of a JSON-compatible value: keys sorted, no
insignificant whitespace, ASCII escapes, no NaN or infinity. The same tuple serialised with another key order or
other whitespace therefore has the same digest, and an added field changes it (``17`` T-31, RC-62).
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Union

from cpe.errors import Refusal

JsonValue = Union[None, bool, int, float, str, list["JsonValue"], dict[str, "JsonValue"]]

SHA256_HEX_LENGTH = 64
ZERO_DIGEST = "0" * SHA256_HEX_LENGTH


def _check_json(value: object, path: str, active: frozenset[int] = frozenset()) -> None:
    """Refuse anything that is not plain, finite, acyclic JSON data; ``active`` holds the containers on the current
    path, so a value that contains itself is a typed refusal rather than a RecursionError."""
    if value is None or isinstance(value, (bool, str)):
        return
    if isinstance(value, int):
        try:
            # json writes int.__repr__ whatever a subclass defines, and Python refuses the decimal form of an integer
            # beyond its digit limit (issue #37; the subclass case is PR #39 review 4348066271)
            int.__repr__(value)
        except ValueError:
            raise Refusal("integer_too_large", f"{path} has more digits than a JSON integer may carry here") from None
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Refusal("non_finite_number", f"{path} is {value!r}")
        return
    if isinstance(value, (list, dict)):
        if id(value) in active:
            raise Refusal("cyclic_value", f"{path} contains itself")
        inner = active | {id(value)}
        if isinstance(value, list):
            for i, item in enumerate(value):
                _check_json(item, f"{path}[{i}]", inner)
            return
        for key, item in value.items():
            if not isinstance(key, str):
                raise Refusal("non_string_key", f"{path} has key {key!r}")
            _check_json(item, f"{path}.{key}", inner)
        return
    raise Refusal("not_json", f"{path} is of type {type(value).__name__}")


def canonical_bytes(value: JsonValue) -> bytes:
    """Return the one canonical UTF-8 byte form of ``value``.

    Refuses anything that is not plain JSON data, so that no object can carry hidden state into a digest.
    """
    _check_json(value, "$")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_of(value: JsonValue) -> str:
    """SHA-256 of the canonical bytes of ``value``, as 64 lowercase hex characters."""
    return sha256_hex(canonical_bytes(value))


def require_hex_digest(value: object, field: str) -> str:
    """Accept exactly 64 lowercase hex characters (fixture F-04: ``'z' * 64`` is refused)."""
    if not isinstance(value, str) or len(value) != SHA256_HEX_LENGTH or any(c not in "0123456789abcdef" for c in value):
        raise Refusal("invalid_digest", f"{field} must be {SHA256_HEX_LENGTH} lowercase hex characters")
    return value
