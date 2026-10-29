"""The monotonic clock and the boot identifier beside the wall clock (``17`` section 3 item 2 "Clock", RC-73).

No rule that reads only the wall clock can measure time during which nothing was observed, so every
clock-dependent check persists a reading of (wall time, monotonic time, boot id). The wall time of a reading is
the ledger's server clock; the other two come from a ``TimeSource``. ``ManualTimeSource`` is the harness's,
driven by the tests; ``HostTimeSource`` reads the host.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol

from cpe.clock import ManualClock
from cpe.schemas.common import (
    Payload,
    require_identifier,
    require_keys,
    require_mapping,
    require_non_negative_number,
    require_timestamp,
    timestamp_payload,
)

_READING_KEYS = frozenset({"wall", "monotonic", "boot_id"})


@dataclass(frozen=True)
class ClockReading:
    """One persisted reading: the wall time, the monotonic time and the boot identifier at a check."""

    wall: datetime
    monotonic: float
    boot_id: str

    def offset(self) -> float:
        """Wall minus monotonic, in seconds; its drift from the epoch baseline measures the unobserved time."""
        return self.wall.timestamp() - self.monotonic

    @classmethod
    def from_payload(cls, payload: object) -> ClockReading:
        m = require_mapping(payload, "ClockReading")
        require_keys(m, "ClockReading", _READING_KEYS, frozenset())
        return cls(require_timestamp(m["wall"], "wall"), require_non_negative_number(m["monotonic"], "monotonic"),
                   require_identifier(m["boot_id"], "boot_id"))

    def to_payload(self) -> Payload:
        return {"wall": timestamp_payload(self.wall), "monotonic": self.monotonic, "boot_id": self.boot_id}


class TimeSource(Protocol):
    def monotonic(self) -> float: ...

    def boot_id(self) -> str: ...


class ManualTimeSource:
    """The harness's time source: a monotonic clock and a boot id the tests advance, slew, reset and reboot,
    beside the manual wall clock the ledger reads."""

    def __init__(self, clock: ManualClock, monotonic: float = 0.0, boot_id: str = "boot-1") -> None:
        self._clock = clock
        self._monotonic = monotonic
        self._boot_id = boot_id

    def monotonic(self) -> float:
        return self._monotonic

    def boot_id(self) -> str:
        return self._boot_id

    def advance(self, delta: timedelta, slew: timedelta = timedelta(0)) -> None:
        """Real time passes by ``delta``; the wall clock moves by ``delta`` plus ``slew``."""
        self._monotonic += delta.total_seconds()
        self._clock.advance(delta + slew)

    def reboot(self, boot_id: str, monotonic: float = 0.0) -> None:
        self._boot_id = boot_id
        self._monotonic = monotonic


# Drawn once at import: without a kernel boot id, a process start is the only discontinuity this source can name, so
# every source in one process must report the same id; one drawn per object made a second gate in the same process
# read a reboot (issue #37).
_PROCESS_BOOT_ID = str(uuid.uuid4())


class HostTimeSource:
    """The host's monotonic clock and boot id (Linux: the kernel's; elsewhere: one id per process)."""

    _BOOT_ID_PATH = Path("/proc/sys/kernel/random/boot_id")

    def __init__(self) -> None:
        try:
            self._boot_id = self._BOOT_ID_PATH.read_text(encoding="ascii").strip() or _PROCESS_BOOT_ID
        except OSError:
            self._boot_id = _PROCESS_BOOT_ID

    def monotonic(self) -> float:
        return time.monotonic()

    def boot_id(self) -> str:
        return self._boot_id
