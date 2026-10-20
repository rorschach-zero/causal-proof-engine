"""Clocks and timestamps.

The ledger assigns every record its receipt time from the server clock it is given; a caller's own time is stored
as an audited claim and never as the receipt time (``17`` T-01, RC-02). Tests inject a manual clock.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Protocol

from cpe.errors import Refusal

_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def format_timestamp(moment: datetime) -> str:
    """UTC, microsecond resolution, trailing ``Z``; the only timestamp text the ledger stores."""
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise Refusal("naive_timestamp", "timestamps must carry a time zone")
    return moment.astimezone(timezone.utc).strftime(_FORMAT)


def parse_timestamp(text: object, field: str = "timestamp") -> datetime:
    if not isinstance(text, str):
        raise Refusal("invalid_timestamp", f"{field} must be a string")
    try:
        parsed = datetime.strptime(text, _FORMAT).replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise Refusal("invalid_timestamp", f"{field}: {error}") from None
    if format_timestamp(parsed) != text:
        raise Refusal("invalid_timestamp", f"{field}: {text!r} is not in the canonical form {_FORMAT}")
    return parsed


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    """The host wall clock, in UTC."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class ManualClock:
    """A clock the test harness sets and advances; it can also be rolled back to exercise fail-closed paths."""

    def __init__(self, start: datetime) -> None:
        if start.tzinfo is None:
            raise Refusal("naive_timestamp", "the manual clock needs an aware start time")
        self._now = start.astimezone(timezone.utc)

    def now(self) -> datetime:
        return self._now

    def set(self, moment: datetime) -> None:
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise Refusal("naive_timestamp", "the manual clock is set with an aware time only")
        self._now = moment.astimezone(timezone.utc)

    def advance(self, delta: timedelta) -> None:
        self._now = self._now + delta
