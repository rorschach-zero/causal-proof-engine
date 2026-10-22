"""Field validators shared by the schemas."""
from __future__ import annotations

import json
import math
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any, cast

from cpe.canonical import JsonValue, canonical_bytes, require_hex_digest
from cpe.clock import format_timestamp, parse_timestamp
from cpe.errors import Refusal

Payload = dict[str, JsonValue]

MAX_IDENTIFIER_LENGTH = 256


def require_mapping(value: object, schema: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise Refusal("not_a_mapping", f"{schema} must be given as a mapping, not {type(value).__name__}")
    return value


def require_keys(payload: Mapping[str, Any], schema: str, required: frozenset[str], optional: frozenset[str]) -> None:
    """Refuse a missing required key and any key the schema does not define (RC-112, T-31 added field)."""
    keys = set(payload)
    if any(not isinstance(key, str) for key in keys):
        raise Refusal("invalid_field_name", f"{schema} has a field name that is not a string")
    missing = sorted(required - keys)
    if missing:
        raise Refusal("missing_field", f"{schema} lacks {', '.join(missing)}")
    unknown = sorted(keys - required - optional)
    if unknown:
        raise Refusal("unknown_field", f"{schema} does not define {', '.join(unknown)}")


def require_identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_IDENTIFIER_LENGTH or value.strip() != value:
        raise Refusal("invalid_identifier", f"{field} must be a non-empty trimmed string of at most "
                      f"{MAX_IDENTIFIER_LENGTH} characters")
    return value


def require_identifier_tuple(value: object, field: str, *, allow_empty: bool) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise Refusal("invalid_list", f"{field} must be a list of identifiers")
    items = tuple(require_identifier(item, f"{field}[{i}]") for i, item in enumerate(value))
    if not items and not allow_empty:
        raise Refusal("empty_list", f"{field} must not be empty")
    if len(set(items)) != len(items):
        raise Refusal("duplicate_identifier", f"{field} repeats an identifier")
    return items


def identifier_list(value: object, field: str) -> list[JsonValue]:
    """A tuple field as its payload writes it: a string is refused, never split into its characters (issue #37,
    pass 3). The items are checked when the payload is read back."""
    if not isinstance(value, (list, tuple)):
        raise Refusal("invalid_list", f"{field} must be a list of identifiers")
    return list(value)


def require_text(value: object, field: str) -> str:
    """Free text, refused rather than coerced when it is not a string (issue #37, pass 3)."""
    if not isinstance(value, str):
        raise Refusal("invalid_text", f"{field} must be a string")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise Refusal("invalid_text", f"{field} holds a surrogate code point") from None
    return value


def payload_of(value: object) -> Payload:
    """The payload a schema object would persist; an object whose fields cannot be serialised is refused, typed,
    rather than raising whatever its fields raise (issue #37)."""
    try:
        payload = value.to_payload()  # type: ignore[attr-defined]
    except Refusal:
        raise
    except Exception as error:
        raise Refusal("invalid_object", f"{type(value).__name__} cannot be serialised: {error!r}") from None
    return payload  # type: ignore[no-any-return]


def require_probability(value: object, field: str) -> float:
    """A finite number in [0, 1]; booleans are not numbers here (T-26: NaN and out-of-range inputs are refused)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Refusal("invalid_probability", f"{field} must be a number")
    try:
        number = float(value)
    except OverflowError:
        raise Refusal("invalid_probability", f"{field} is outside the finite range") from None
    if not math.isfinite(number):
        raise Refusal("invalid_probability", f"{field} must be finite")
    if not 0.0 <= number <= 1.0:
        raise Refusal("invalid_probability", f"{field} must lie in [0, 1]")
    return number


def require_non_negative_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Refusal("invalid_number", f"{field} must be a number")
    try:
        number = float(value)
    except OverflowError:
        raise Refusal("invalid_number", f"{field} is outside the finite range") from None
    if not math.isfinite(number) or number < 0:
        raise Refusal("invalid_number", f"{field} must be a finite non-negative number")
    return number


def require_json(value: object, field: str) -> JsonValue:
    """Accept only finite, plain JSON data (no tuples, objects or NaN), so that the value can be stored and digested.

    The accepted value is a fresh copy built from its canonical bytes, never the caller's object: a later change
    to the caller's list or mapping does not reach the schema."""
    return cast(JsonValue, json.loads(canonical_bytes(cast(JsonValue, value))))


def require_non_negative_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Refusal("invalid_integer", f"{field} must be a non-negative integer")
    return value


def require_timestamp(value: object, field: str) -> datetime:
    return parse_timestamp(value, field)


def optional_timestamp(value: object, field: str) -> datetime | None:
    return None if value is None else parse_timestamp(value, field)


def timestamp_payload(moment: datetime | None) -> str | None:
    return None if moment is None else format_timestamp(moment)


def require_date(value: object, field: str) -> date:
    if not isinstance(value, str):
        raise Refusal("invalid_date", f"{field} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise Refusal("invalid_date", f"{field}: {error}") from None


def require_digest(value: object, field: str) -> str:
    return require_hex_digest(value, field)
