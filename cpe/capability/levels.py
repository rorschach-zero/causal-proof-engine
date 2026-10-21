"""Gate levels and the actions each permits.

The gate floor is ``RESEARCH_ONLY``; every process start begins there (RC-123). ``LIVE_EXECUTION`` is named so
that a capability asking for it is refused by name: live promotion stays blocked in code until a separately
reviewed and expressly authorised release (``AGENTS.md`` section 3). The action table is the Phase 1 minimum:
each protected action names the lowest level that permits it (T-33: ``SHADOW_LIVE_QUOTES`` alone denies SIM
execution).
"""
from __future__ import annotations

from types import MappingProxyType

from cpe.errors import Refusal

LEVELS: tuple[str, ...] = ("RESEARCH_ONLY", "SHADOW_LIVE_QUOTES", "SIM_READ_ONLY", "SIM_EXECUTION", "LIVE_EXECUTION")
FLOOR = LEVELS[0]
LIVE = LEVELS[-1]
PROMOTE_PREFIX = "promote:"

# A read-only view: the one table the gate trusts cannot be rewritten by an in-process caller (RC-46).
ACTIONS: MappingProxyType[str, str] = MappingProxyType({
    "research": FLOOR,
    "shadow_quotes": "SHADOW_LIVE_QUOTES",
    "sim_read": "SIM_READ_ONLY",
    "sim_execution": "SIM_EXECUTION",
})


def rank(level: str) -> int:
    if level not in LEVELS:
        raise Refusal("unknown_level", level)
    return LEVELS.index(level)


def permits(level: str, action: str) -> bool:
    required = ACTIONS.get(action)
    if required is None:
        raise Refusal("unknown_action", action)
    return rank(level) >= rank(required)


def promotion_target(capability_action: str) -> str:
    """The level a promotion capability names; live is refused by name, before any signature is looked at."""
    if not capability_action.startswith(PROMOTE_PREFIX):
        raise Refusal("unknown_action", f"{capability_action} is not a gate promotion")
    level = capability_action[len(PROMOTE_PREFIX):]
    if level == LIVE:
        raise Refusal("live_blocked", "live promotion is blocked in code (AGENTS.md section 3)")
    rank(level)
    return level
