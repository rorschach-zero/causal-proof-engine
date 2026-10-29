"""Whole-codebase audit, pass 8 (issue #37), at ``c37d04899c3f0c821825f7aee09ff79c900eb02a``: two row fields replay read
as written, found by the raw-row invariant (invariant 3 of PR #88).

- P8-6 (P3): a source-latency defect's ``detail`` was read as written, so a row with any text was admitted and the
  stored disposition showed it; the registry writes one text (``late_contradictions``).
- P8-7 (P3): a refused round's ``reason`` was read as written. For a round published before its calibration
  record's anchor the registry writes ``round_before_anchor``; a row saying ``register_not_anchored`` was admitted.
  The check is one-directional: a covering anchor only settles earlier, so a round that followed the record's anchor
  when it was written still does, while the other reason may have been written while an attempt was pending.

The first two tests failed at the pass-8 pin; the third is a guard."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.adjudication.registry import KIND_DEFECT, _ledger_id as adjudication_id
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.registration import BeaconOutput, CalibrationRecord, ClaimPreregistration, ConfirmatoryRegister, RegistrationRegistry
from cpe.registration.registry import KIND_ROUND_REFUSED, _ledger_id as registration_id
from tests.test_adjudication import day as aday
from tests.test_adjudication import observation, record, rule, spec, submit
from tests.test_registration import clock as clock, ledger as ledger, registry as registry  # noqa: F401 (fixtures)
from tests.test_registration import day


def test_p8_6_a_defect_carries_the_text_its_registry_writes(tmp_path: Path) -> None:
    clock = ManualClock(aday(3))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    registry.register_event(spec())
    clock.set(aday(111))
    registry.submit_observation(observation(110))
    registry.adjudicate("E")
    clock.set(aday(113))
    submit(registry, record("late", occurrence=95, published=112, observed=113))
    ledger.append(KIND_DEFECT, adjudication_id("defect", "E", "late"),
                  {"event_id": "E", "record_id": "late", "detail": "the source was right after all"})
    with pytest.raises(Refusal) as refused:
        registry.state()  # at c37d048: read, and the stored disposition carried the text
    assert refused.value.reason == "invalid_record"


def test_p8_7_a_refused_round_names_the_anchor_it_preceded(registry: RegistrationRegistry, ledger: Ledger,
                                                         clock: ManualClock) -> None:
    registry.register_claim(ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60),
                                                 day(400), "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1"))
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(11.5))
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(13))
    output = BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(10.5))  # before the record's anchor
    ledger.append(KIND_ROUND_REFUSED, registration_id("round-refused", "cal-1"),
                  {"output": output.to_payload(), "reason": "register_not_anchored"})
    with pytest.raises(Refusal) as refused:
        registry.claim_status("claim-1")  # at c37d048: read; the registry writes round_before_anchor
    assert refused.value.reason == "invalid_record"


def test_p8_7_the_registry_writes_the_reason_its_replay_reads(registry: RegistrationRegistry, ledger: Ledger,
                                                            clock: ManualClock) -> None:
    """A guard, passing before and after the fix: the row the registry writes is one its replay reads."""
    registry.register_claim(ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60),
                                                 day(400), "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1"))
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(11.5))
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(13))
    with pytest.raises(Refusal) as refused:  # before both anchors: the record's is named, and the round binds
        registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, day(10.5)))
    assert refused.value.reason == "round_before_anchor"
    row = ledger.records()[-1].payload
    assert isinstance(row, dict) and row["reason"] == "round_before_anchor"
    assert registry.claim_status("claim-1") == "exploratory"
