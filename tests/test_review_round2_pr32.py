"""Regression tests for Codex's review of PR #32 at ed4b80f (round 2). Each fails at ed4b80f and passes after the
fix."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.adjudication import MEDIA_TYPE_JSON, AdjudicationRegistry, ArchivedContent, adjudicate, evaluate
from cpe.canonical import JsonValue, canonical_bytes, sha256_hex
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.schemas.event import ResolutionPredicate
from tests.test_adjudication import day, observation, record, rule, spec, submit


def test_4335130169_a_public_occurrence_after_a_milestone_deadline_sets_knowable_at(tmp_path: Path) -> None:
    """Deadline 100, finality 110: absence observed at 110, then a record published at 112 of a public occurrence at
    105, which evidences the expiry. The NO stands; it was publicly determinable at 105."""
    late_expiry = record("late", occurrence=105, published=112)
    pure = adjudicate(spec(), rule(public_act=True), [late_expiry], [observation(110)], [], day(113))
    assert pure.disposition == "RESOLVED_NO" and pure.knowable_at == day(105)
    clock = ManualClock(day(1))
    reg = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    reg.register_rule(rule(public_act=True))
    reg.register_event(spec())
    clock.set(day(111))
    reg.submit_observation(observation(110))
    assert reg.adjudicate("E").knowable_at == day(110)
    clock.set(day(113))
    submit(reg, late_expiry)
    assert reg.adjudicate("E").knowable_at == day(105)
    falsifier = adjudicate(spec("terminal-falsifier"), rule(public_act=True), [record("f", occurrence=105, published=106)],
                           [observation(110)], [], day(111))
    assert falsifier.knowable_at == day(110)  # 4334622008 stays fixed: a late falsifier sets nothing


def nested(depth: int) -> JsonValue:
    value: JsonValue = 1
    for _ in range(depth):
        value = [value]
    return value


def test_4335130178_deep_values_in_a_comparison_are_a_typed_refusal() -> None:
    deep = nested(900)
    predicate = ResolutionPredicate.from_payload({**spec().predicate.to_payload(), "comparator": "in", "value": [deep]})
    data = canonical_bytes({"sel": {"f": deep}})
    content = ArchivedContent(data, sha256_hex(data), MEDIA_TYPE_JSON, "src", day(0))
    with pytest.raises(Refusal) as refused:
        evaluate(predicate, content)
    assert refused.value.reason == "nesting_too_deep"
