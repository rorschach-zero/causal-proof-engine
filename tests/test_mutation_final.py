"""Mutation testing, the last survivors with an observable effect (``research/19`` section 10): tests written after
the run on ``e69b0c8`` classified its survivors, so that the run reported in section 10 is the one on the final tree.
Each test names the mutant it kills; the classification of every other survivor is committed beside the run."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry, ArchivedContent, adjudicate
from cpe.capability import CapabilityGate, ManualTimeSource
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.pointintime import FeatureRow, PointInTimeStore
from cpe.registration import BaseRate, CandidateEntry, CutoffCorrection, RegistrationRegistry
from cpe.validation import check_issuance
from tests import test_adjudication as adj
from tests import test_registration as reg
from tests.test_capability import ENV, OWNER, RELEASE, TOLERANCE, Rig, issue


class SteppingClock(ManualClock):
    """A manual clock that moves on to ``then`` right after its next reading."""

    def __init__(self, start: datetime) -> None:
        super().__init__(start)
        self.then: datetime | None = None

    def now(self) -> datetime:
        value = super().now()
        if self.then is not None:
            self.set(self.then)
            self.then = None
        return value


class CountingTimeSource(ManualTimeSource):
    """A harness time source whose monotonic clock moves a microsecond at every reading, as a host clock does."""

    def monotonic(self) -> float:
        value = super().monotonic()
        self._monotonic += 1e-6
        return value


def test_two_versions_corrected_on_one_evidence_id(tmp_path: Path) -> None:  # correct_cutoff 26, 29
    registry = RegistrationRegistry(Ledger(tmp_path / "l.sqlite", ManualClock(reg.day(1)), HarnessAnchorStore()))
    registry.register_arm_version(reg.arm("A-1", "2026-01-05"))
    registry.register_arm_version(reg.arm("B-1", "2026-01-05"))
    registry.correct_cutoff(CutoffCorrection("A-1", date(2026, 1, 4), "provider-notice"))
    registry.correct_cutoff(CutoffCorrection("B-1", date(2026, 1, 4), "provider-notice"))
    assert registry.arm_version("B-1").declared_cutoff == date(2026, 1, 4)


def test_three_forecasts_before_the_window_are_kept(tmp_path: Path) -> None:  # replay_state 75
    clock = ManualClock(reg.day(1))
    registry = RegistrationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    registry.register_arm_version(reg.arm("A-1", "2026-01-05"))
    registry.register_arm_version(reg.arm("DESIGN_C-1", "2026-01-01"))
    registry.register_arm_version(reg.arm("FULL-1", "2026-01-03", ["A-1"]))
    registry.commit_base_rate(BaseRate("RC-1", 0.2))
    registry.log_candidate(CandidateEntry("cand-E-1", "E-1", "src", reg.day(1), "registered", "match"))
    clock.set(reg.day(10))
    registry.register_cluster(reg.registration([reg.spec("E-1")]))
    for hour in (1, 2, 3):  # before the window opens: kept, labelled by receipt, filling nothing
        clock.set(reg.day(10) + timedelta(hours=hour))
        registry.submit_forecast(reg.forecast("E-1"))
    # The replayed state, not the public snapshot, which seals the event's forecasts until its window closes (pass 6
    # Codex 6-2, reading P6-R2)
    assert len(registry._state().forecasts_by_event["E-1"]) == 3


def test_a_discontinuity_rotates_with_the_new_boot_as_its_baseline(tmp_path: Path) -> None:  # _rotate 2
    """The baseline is the rotation's own reading, taken after the one that showed the discontinuity (issue #37, pass
    9, PR #102 review 4418866225): the new boot identifier, and the monotonic time read again."""
    clock = ManualClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    time_source = CountingTimeSource(clock)
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    gate = CapabilityGate(ledger, OWNER, time_source, ENV, RELEASE, TOLERANCE)
    time_source.reboot("boot-2", monotonic=5.0)
    with pytest.raises(Refusal):
        gate.perform("research")
    baseline = gate.state().baseline
    assert baseline is not None and baseline.boot_id == "boot-2" and baseline.monotonic > 5.0


def test_two_step_3_aborts_on_one_ledger(tmp_path: Path) -> None:  # promote 165, 167
    rig = Rig(tmp_path)
    def demote() -> None:
        rig.gate.demote("between steps 2 and 3")

    for nonce in ("first", "second"):
        rig.tick()
        rig.gate.hooks["after_intent_anchor"] = demote
        assert rig.refused(issue(rig.epoch(), nonce)) == "superseded"
    assert len(rig.gate.state().aborted) == 2


def test_two_receipt_lags_on_one_stored_disposition(tmp_path: Path) -> None:  # AdjudicationRegistry.adjudicate 132, 136
    clock = ManualClock(adj.day(3))
    registry = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    registry.register_rule(adj.rule())
    registry.register_event(adj.spec())
    clock.set(adj.day(110))
    registry.submit_observation(adj.observation(110))
    assert registry.adjudicate("E").disposition == "RESOLVED_NO"
    clock.set(adj.day(120))
    adj.submit(registry, adj.record("r-105", occurrence=95, published=105, observed=119))
    registry.adjudicate("E")
    adj.submit(registry, adj.record("r-103", occurrence=95, published=103, observed=119))
    lags = {i.reference_id for i in registry.adjudicate("E").incidents if i.kind == "receipt_lag"}
    assert lags == {"r-105", "r-103"}


def test_a_row_refused_at_its_receipt_is_not_retried(tmp_path: Path) -> None:  # PointInTimeStore.ingest 43
    clock = SteppingClock(adj.day(10))
    store = PointInTimeStore(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    row = FeatureRow("entity", "feature", 1, adj.day(9), adj.day(10) + timedelta(seconds=1), "v1")
    clock.then = adj.day(11)  # a second append would be received after the row became available
    with pytest.raises(Refusal) as refused:
        store.ingest(row)
    assert refused.value.reason == "evidence_after_receipt"


def test_a_missing_jev_record_is_named_as_the_jev_input() -> None:  # check_issuance 127, 130, 134, 135
    decision = check_issuance("E-1", {"A": "A-1", "B": "B-1", "C": "C-1"}, [], None, slot_id="primary")
    assert ("missing_jev", "jev") in {(p.reason, p.subject) for p in decision.problems}


def test_base64_with_stray_bits_is_refused_as_invalid_content() -> None:  # ArchivedContent.from_payload 54 to 59
    payload = adj.archived().to_payload()
    payload["content_base64"] = "QR=="  # decodes strictly to b"A", whose one canonical encoding is "QQ=="
    with pytest.raises(Refusal) as refused:
        ArchivedContent.from_payload(payload)
    assert refused.value.reason == "invalid_content"


def test_a_record_published_at_finality_is_timely_not_evidence_of_absence() -> None:  # adjudicate 110
    at_finality = adj.record("r", claim="not-occurred", published=110, observed=111)
    out = adjudicate(adj.spec(), adj.rule(monotone=True), [at_finality], [], [], adj.day(112))
    assert out.disposition == "OPEN"
