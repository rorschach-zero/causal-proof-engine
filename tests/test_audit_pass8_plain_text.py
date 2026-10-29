"""Whole-codebase audit, pass 8 (issue #37), at ``c37d04899c3f0c821825f7aee09ff79c900eb02a``: every input decided as its
plain text, bare arguments included.

Pass 7 (reading P7-R3) read every schema object back through the canonical form, so that a ``str`` subclass whose text
is one value and which compares equal to, and hashes as, another is decided as its text. An identifier given as a bare
argument went through ``require_identifier``, which returned the caller's object, and was decided as the other value:

- P8-1: ``CapabilityGate.perform`` admitted a look-alike ``sim_execution`` at ``RESEARCH_ONLY`` and persisted the check
  as ``action:sim_execution`` admitted (T-33, ``17`` item 5);
- P8-2: ``check_issuance`` was issuable for one event with every output and the Jev record of another, for one slot
  with outputs of another, and for a provider set the outputs do not name (T-28, RC-17, RC-75);
- P8-3: ``AdjudicationRegistry.adjudicate`` wrote one event's disposition under another's identifier, and every later
  read refused the ledger;
- P8-4: the registration and point-in-time reads answered for the record the argument compares equal to (``seed_of``
  gave a seed to a record whose round was never supplied, RC-187);
- P8-5: a gate configured with a look-alike environment acknowledged a capability signed for another environment.

``require_identifier``, ``require_text``, ``require_hex_digest`` and the choice validators now return the plain text
(``cpe.canonical.plain_text``), ``perform`` reads its action as plain text and the gate validates its environment.
Every test failed at the pass-8 pin."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.capability import CapabilityGate
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.pointintime import FeatureRow, PointInTimeStore
from cpe.registration import BeaconOutput, CalibrationRecord, ClaimPreregistration, RegistrationRegistry
from cpe.validation import check_issuance
from tests.test_adjudication import day as aday
from tests.test_adjudication import observation, rule, spec as aspec
from tests.test_audit_pass7_plain_inputs import LooksLike
from tests.test_capability import ENV, EVIDENCE, OWNER, RELEASE, TOLERANCE, Rig, issue
from tests.test_input_validation import VERSIONS, jev, output
from tests.test_point_in_time import day as pday
from tests.test_registration import clock as clock, ledger as ledger, registry as registry  # noqa: F401 (fixtures)
from tests.test_registration import day


def test_p8_1_an_action_is_decided_as_the_check_persists_it(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    assert rig.gate.anchor_epoch()
    with pytest.raises(Refusal) as refused:
        rig.gate.perform(LooksLike("sim_execution", "research"))  # at c37d048: admitted at RESEARCH_ONLY
    assert refused.value.reason == "level_insufficient"
    check = rig.ledger.records()[-1].payload
    assert isinstance(check, dict) and (check["subject"], check["verdict"]) == ("action:sim_execution", "refused")


@pytest.mark.parametrize("case", ["event", "slot", "provider"])
def test_p8_2_an_issuance_is_decided_on_the_text_of_its_arguments(case: str) -> None:
    if case == "event":  # every output and the Jev record of E-2, issued as E-1
        decision = check_issuance(LooksLike("E-1", "E-2"), VERSIONS, [output(p, "E-2") for p in VERSIONS],
                                  jev("E-2"), slot_id="primary")
    elif case == "slot":  # outputs for slot "other", issued for "primary"
        decision = check_issuance("E-1", VERSIONS, [output(p, slot_id="other") for p in VERSIONS], jev(),
                                  slot_id=LooksLike("primary", "other"))
    else:  # a registered provider "P-X" that P-A's output stands in for
        versions = {LooksLike("P-X", "P-A") if p == "P-A" else p: v for p, v in VERSIONS.items()}
        decision = check_issuance("E-1", versions, [output(p) for p in VERSIONS], jev(), slot_id="primary")
    assert decision.status == "rejected"  # at c37d048: issuable


def test_p8_3_an_adjudication_is_written_for_the_event_its_argument_names(tmp_path: Path) -> None:
    clock = ManualClock(aday(3))
    registry = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    registry.register_rule(rule())
    registry.register_event(aspec(event_id="G"))
    registry.register_event(aspec(event_id="H"))
    clock.set(aday(111))
    registry.submit_observation(observation(110, event_id="H"))
    result = registry.adjudicate(LooksLike("G", "H"))  # at c37d048: H's disposition under G's identifier
    assert (result.event_id, result.disposition) == ("G", "OPEN")
    assert registry.state().event("H").disposition is None  # and the ledger stays readable


def test_p8_4_a_read_answers_for_the_record_its_argument_names(registry: RegistrationRegistry, ledger: Ledger,
                                                             clock: ManualClock, tmp_path: Path) -> None:
    for n in (1, 2):
        registry.register_claim(ClaimPreregistration(f"claim-{n}", "fixed_question_set", "Q-1", "holder", day(1),
                                                     day(60), day(400), "period-balanced", ("DESIGN_C",), ("L-1",),
                                                     f"cal-{n}"))
        registry.record_calibration(CalibrationRecord(f"cal-{n}", f"claim-{n}", "t", 1000, 0.01, "beacon", f"r-{n}"))
    clock.set(day(11))
    ledger.anchor()
    clock.set(day(12))
    registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "r-1", "ab" * 32, day(12)))
    with pytest.raises(Refusal) as refused:
        registry.seed_of(LooksLike("cal-2", "cal-1"))  # at c37d048: cal-1's seed, for a record with no round
    assert refused.value.reason == "no_seed"
    with pytest.raises(Refusal) as unknown:
        registry.claim_status(LooksLike("claim-3", "claim-1"))  # at c37d048: claim-1's status
    assert unknown.value.reason == "unknown_claim"
    store = PointInTimeStore(Ledger(tmp_path / "pit.sqlite", ManualClock(pday(10)), HarnessAnchorStore()))
    store.ingest(FeatureRow("X", "f", 1.0, pday(1), pday(2), "v1"))
    reader = store.reader(pday(9))
    assert reader.series(LooksLike("Z", "X"), "f").empty  # at c37d048: X's observations, labelled Z
    with pytest.raises(Refusal) as missing:
        reader.row("X", "f", LooksLike("v9", "v1"))  # at c37d048: vintage v1
    assert missing.value.reason == "not_available"


def test_p8_5_a_gate_is_configured_with_the_text_of_its_environment(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    gate = CapabilityGate(rig.ledger, OWNER, rig.time, LooksLike(ENV, "env-2"), RELEASE, TOLERANCE)
    rig.time.advance(timedelta(seconds=1))
    elsewhere = issue(gate.state().epoch, "elsewhere", environment="env-2")  # signed for another environment
    with pytest.raises(Refusal) as refused:
        gate.promote(elsewhere, EVIDENCE)  # at c37d048: acknowledged at SIM_READ_ONLY
    assert refused.value.reason == "wrong_environment"
    with pytest.raises(Refusal) as invalid:
        CapabilityGate(rig.ledger, OWNER, rig.time, ["not", "text"], RELEASE, TOLERANCE)  # type: ignore[arg-type]
    assert invalid.value.reason == "invalid_identifier"


def test_p8_a_ledger_row_holds_the_text_of_its_kind_and_identifier(tmp_path: Path) -> None:
    """The same root at the ledger's own append: the acknowledged record held the caller's objects, so two kinds that
    compare equal were counted as one (found while fixing P8-1 to P8-5)."""
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(day(1)), HarnessAnchorStore())
    first = ledger.append(LooksLike("kind-a", "kind-b"), LooksLike("row-1", "row-2"), {})
    ledger.append("kind-b", "row-2", {})
    assert (type(first.kind), type(first.record_id)) == (str, str)  # at c37d048: the look-alike objects
    assert ledger.state.kinds == {"kind-a": 1, "kind-b": 1}  # at c37d048: {"kind-a": 2}
