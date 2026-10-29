"""Whole-codebase audit, pass 8 (issue #37), at ``c37d04899c3f0c821825f7aee09ff79c900eb02a``: the idempotent read-back of
the adjudication registry compares persisted content.

Codex 8-4 (PR #87 review comment 4417203557, P2): ``register_event`` compared an existing specification by dataclass
equality, where ``True == 1``. Registering the predicate value ``1`` after ``true`` returned as idempotent instead of
``event_immutable``, although the two predicates evaluate the same archived content differently (``json_equal``), so
the caller was told criteria were registered that were not. The registry now compares the canonical payloads, as the
point-in-time store does (4335189789). Both tests failed at the pass-8 pin."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.schemas import EventSpec
from tests.test_adjudication import day, rule, spec


def registered(tmp_path: Path, predicate: dict[str, Any]) -> tuple[AdjudicationRegistry, dict[str, Any]]:
    """A registry holding spec() with ``predicate`` merged into its predicate; the payload registered."""
    registry = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", ManualClock(day(1)), HarnessAnchorStore()))
    registry.register_rule(rule())
    payload: dict[str, Any] = spec().to_payload()
    payload["predicate"] = {**payload["predicate"], **predicate}
    registry.register_event(EventSpec.from_payload(payload))
    return registry, payload


@pytest.mark.parametrize("held, given", [
    ({"comparator": "eq", "value": True}, {"value": 1}),
    ({"comparator": "in", "value": [True]}, {"value": [1]}),
])
def test_codex8_4_a_predicate_value_of_another_type_is_other_criteria(tmp_path: Path, held: dict[str, Any],
                                                                      given: dict[str, Any]) -> None:
    registry, payload = registered(tmp_path, held)
    other = {**payload, "predicate": {**payload["predicate"], **given}}
    with pytest.raises(Refusal) as refused:
        registry.register_event(EventSpec.from_payload(other))
    assert refused.value.reason == "event_immutable"  # at c37d048: returned as if registered
    registry.register_event(EventSpec.from_payload(payload))  # the same criteria again stay idempotent
