"""Codex's review of H1 (PR #27, 08:28 UTC on 5c0cbf6), the adjudication findings assigned to the resolution-content
PR by research/19 section 9.9. Each test fails at c5ba103 and passes after the fix."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry, SourceStatus, adjudicate
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from tests.test_adjudication import archived, day, observation, record, rule, spec, submit


class StepClock(ManualClock):
    """Hands out queued readings first: the submission's own sample, then the append's."""

    def __init__(self, start: datetime) -> None:
        super().__init__(start)
        self.queue: list[datetime] = []

    def now(self) -> datetime:
        if self.queue:
            self.set(self.queue.pop(0))
        return super().now()


def registry(tmp_path: Path, clock: ManualClock, public_act: bool = False) -> AdjudicationRegistry:
    reg = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    reg.register_rule(rule(public_act=public_act))
    reg.register_event(spec())
    return reg


def test_4334622008_a_public_occurrence_after_the_deadline_does_not_set_knowable_at() -> None:
    late_falsifier = record("late-falsifier", occurrence=105, published=106)
    result = adjudicate(spec("terminal-falsifier"), rule(public_act=True), [late_falsifier], [observation(110)], [],
                        day(111))
    assert result.disposition == "RESOLVED_YES" and result.knowable_at == day(110)


def test_4334622042_a_late_public_occurrence_corrects_the_stored_knowable_time(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    reg = registry(tmp_path, clock, public_act=True)
    clock.set(day(111))
    reg.submit_observation(observation(110))
    assert reg.adjudicate("E").knowable_at == day(110)
    clock.set(day(118))
    submit(reg, record("late", occurrence=90, published=118))
    corrected = reg.adjudicate("E")
    assert corrected.disposition == "RESOLVED_NO" and corrected.knowable_at == day(90)
    assert [d.record_id for d in corrected.defects] == ["late"]
    assert reg.adjudicate("E") == corrected
    clock.set(day(200))
    reopened = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    assert reopened.adjudicate("E") == corrected


@pytest.mark.parametrize("kind", ["observation", "status", "record"])
def test_4334622048_evidence_is_checked_against_the_appended_receipt(tmp_path: Path, kind: str) -> None:
    """The submission's own clock sample reads 111, the append's 109 (above the high-water mark): evidence at 110
    is refused at that receipt or admitted at a receipt not before it, never admitted at 109."""
    clock = StepClock(day(1))
    reg = registry(tmp_path, clock)
    clock.set(day(100))
    if kind == "record":
        reg.archive_content(archived())
    clock.queue = [day(111), day(109)]
    try:
        if kind == "observation":
            reg.submit_observation(observation(110))
        elif kind == "status":
            reg.declare_source_status(SourceStatus("src", True, day(110)))
        else:
            reg.submit_record(record("r", occurrence=95, published=110).record)
    except Refusal as refused:
        assert refused.reason == "evidence_after_receipt"
    clock.queue = []
    clock.set(day(112))
    reg.adjudicate("E")  # replay and adjudication accept every row the ledger holds
