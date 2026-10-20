"""Field validators shared by the schemas."""
from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from cpe.canonical import JsonValue, require_hex_digest
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


def require_probability(value: object, field: str) -> float:
    """A finite number in [0, 1]; booleans are not numbers here (T-26: NaN and out-of-range inputs are refused)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Refusal("invalid_probability", f"{field} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise Refusal("invalid_probability", f"{field} must be finite")
    if not 0.0 <= number <= 1.0:
        raise Refusal("invalid_probability", f"{field} must lie in [0, 1]")
    return number


def require_non_negative_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or value < 0:
        raise Refusal("invalid_number", f"{field} must be a finite non-negative number")
    return float(value)


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
