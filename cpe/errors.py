"""Typed refusals.

Every input the system declines is refused with a stable reason code, never silently dropped or coerced
(``AGENTS.md`` section 6; ``17`` A4). A refusal is a finding about the input, not an internal error.
"""
from __future__ import annotations


class Refusal(ValueError):
    """An input or an action that the system declines, with a stable reason code and a human-readable detail."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail
