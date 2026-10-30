"""Whole-codebase audit, pass 9 (issue #37), at ``811ba9d6bd13996cec72da62c0179d1baf71c6f2``: coverage gaps (P9-10, P3).

The line-by-line reviewers of pass 9 removed or changed each rule below in a scratch copy and the whole suite still
passed: every rule is correct at the pin, and none had a test. Each test here kills its rule's mutant (stated in the
test's docstring; checked by applying the mutation, see the PR)."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.adjudication import registry as adjudication_module
from cpe.adjudication.rules import adjudicate
from cpe.capability.records import (
    KIND_ABORT,
    KIND_CHECK,
    KIND_INTENT,
    AbortRecord,
    CheckRecord,
    IntentRecord,
    gate_ledger_id,
    intent_ledger_id,
)
from cpe.capability.timesource import ClockReading
from cpe.clock import ManualClock, format_timestamp
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from cpe.pointintime import FeatureRow, PointInTimeStore
from cpe.registration import BeaconOutput, CalibrationRecord, ClaimPreregistration, ConfirmatoryRegister
from cpe.registration import RegistrationRegistry
from cpe.registration.registry import (
    KIND_BEACON,
    KIND_CALIBRATION,
    KIND_CLAIM,
    KIND_DISCLOSURE,
    KIND_REGISTER,
    _ledger_id,
    replay_state,
)
from cpe.registration.seeds import derive_seed
from tests.rows import extended
from tests.test_adjudication import day as aday
from tests.test_adjudication import observation, record, rule, spec as aspec, submit
from tests.test_audit_pass3_claim_status import calibrated, claim
from tests.test_capability import Rig, issue
from tests.test_registration import clock as clock, ledger as ledger, registry as registry  # noqa: F401 (fixtures)
from tests.test_registration import day, forecast
from tests.test_schemas import HEX
from tools.check_provenance import text_findings

CAL_1 = CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7")


def refusal_of(read: object) -> str:
    try:
        read()  # type: ignore[operator]
    except Refusal as refusal:
        return refusal.reason
    return "admitted"


def with_refused_round(registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock,
                       published: float = 12) -> BeaconOutput:
    """claim-1 and cal-1 anchored at day 11, the register at day 12 anchored at day 13, and round-7 published at
    ``published`` and supplied at day 14: recorded as refused when it was published at or before the register's
    anchor (RC-311)."""
    calibrated(registry, ledger, clock)
    clock.set(day(12))
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(13))
    ledger.anchor()
    clock.set(day(14))
    round_7 = BeaconOutput("cal-1", "beacon", "round-7", HEX, day(published))
    with pytest.raises(Refusal) as refused:
        registry.supply_beacon_output(round_7)
    assert refused.value.reason == "register_not_anchored"
    return round_7


# Registration --------------------------------------------------------------------------------------------------


def test_a_round_published_exactly_at_the_registers_anchor_makes_the_claim_exploratory(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    """``claim_status``: a recorded round published at or before the register's anchor (RC-311). Mutant: ``<``."""
    with_refused_round(registry, ledger, clock, published=13)  # the anchor's own time
    assert registry.claim_status("claim-1") == "exploratory"


def test_a_register_row_received_at_a_listed_claims_period_start_refuses_the_ledger(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    """Replay of a register received at or after the period start of a claim it lists (``_check_register``). Mutant:
    that clause removed."""
    calibrated(registry, ledger, clock)
    clock.set(day(60))  # claim-1's period starts at day 60
    ledger.append(KIND_REGISTER, _ledger_id("register"), ConfirmatoryRegister("reg-1", 1, ("claim-1",)).to_payload())
    assert refusal_of(lambda: registry.claim_status("claim-1")) == "invalid_record"


def test_claim_and_calibration_rows_received_exactly_at_the_period_start_refuse_the_ledger(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    """``_check_claim`` and ``_check_calibration`` refuse a receipt at the period start itself. Mutants: ``>``."""
    early = ClaimPreregistration("claim-2", "fixed_question_set", "Q-2", "holder", day(1), day(12), day(400),
                                 "period-balanced", ("DESIGN_C",), ("L-1",), "cal-2")
    clock.set(day(12))
    ledger.append(KIND_CLAIM, _ledger_id("claim", "claim-2"), early.to_payload())
    assert refusal_of(lambda: registry.event("E-1")) == "invalid_record"


def test_a_calibration_row_received_exactly_at_its_claims_period_start_refuses_the_ledger(
        registry: RegistrationRegistry, ledger: Ledger, clock: ManualClock) -> None:
    early = ClaimPreregistration("claim-2", "fixed_question_set", "Q-2", "holder", day(1), day(12), day(400),
                                 "period-balanced", ("DESIGN_C",), ("L-1",), "cal-2")
    clock.set(day(11))
    registry.register_claim(early)
    clock.set(day(12))
    ledger.append(KIND_CALIBRATION, _ledger_id("calibration", "cal-2"),
                  CalibrationRecord("cal-2", "claim-2", "block-t", 1000, 0.01, "beacon", "round-2").to_payload())
    assert refusal_of(lambda: registry.event("E-1")) == "invalid_record"


def test_a_beacon_row_after_its_refused_round_draws_no_seed(registry: RegistrationRegistry, ledger: Ledger,
                                                           clock: ManualClock) -> None:
    """``_check_round``: no row follows a round already refused for its record (PR #48 review 4352111655), even one
    claiming a publication after the register's anchor. Mutant: the refused-round clause removed."""
    with_refused_round(registry, ledger, clock)
    later = BeaconOutput("cal-1", "beacon", "round-7", HEX, day(13.5))  # after the register's anchor this time
    ledger.append(KIND_BEACON, _ledger_id("beacon", "cal-1"),
                  {"output": later.to_payload(), "seed": derive_seed(CAL_1.to_payload(), HEX)})
    assert refusal_of(lambda: registry.seed_of("cal-1")) == "invalid_record"


def test_a_register_row_under_another_identifier_confers_nothing(registry: RegistrationRegistry, ledger: Ledger,
                                                                 clock: ManualClock) -> None:
    """``_check_register``'s identifier clause, with no other register on the ledger. Mutant: that clause removed."""
    calibrated(registry, ledger, clock)
    clock.set(day(12))
    ledger.append(KIND_REGISTER, "register:other", ConfirmatoryRegister("reg-1", 1, ("claim-1",)).to_payload())
    clock.set(day(13))
    ledger.anchor()
    assert refusal_of(lambda: registry.claim_status("claim-1")) == "invalid_record"


def test_a_beacon_row_under_another_identifier_draws_no_seed(registry: RegistrationRegistry, ledger: Ledger,
                                                            clock: ManualClock) -> None:
    """``_check_round``'s identifier clause. Mutant: that clause removed."""
    calibrated(registry, ledger, clock)
    clock.set(day(12))
    output = BeaconOutput("cal-1", "beacon", "round-7", HEX, day(11.5))
    ledger.append(KIND_BEACON, "beacon:other", {"output": output.to_payload(),
                                                "seed": derive_seed(CAL_1.to_payload(), HEX)})
    assert refusal_of(lambda: registry.seed_of("cal-1")) == "invalid_record"


def test_a_second_register_is_refused_as_a_second_register_first(registry: RegistrationRegistry, ledger: Ledger,
                                                                 clock: ManualClock) -> None:
    """The decision refuses a second register before it looks at the claims it lists. Mutant: that check removed (the
    second register naming an unknown claim is then refused ``unknown_claim``)."""
    calibrated(registry, ledger, clock)
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    assert refusal_of(lambda: registry.anchor_confirmatory_register(
        ConfirmatoryRegister("reg-2", 1, ("ghost",)))) == "register_immutable"


def test_a_second_row_of_a_claim_refuses_replay(registry: RegistrationRegistry, ledger: Ledger,
                                                clock: ManualClock) -> None:
    """``_check_claim``'s one-record-per-claim clause, reachable by replay only (the ledger refuses the identifier
    twice). The second row names another calibration record, so that the reservation rule does not decide. Mutant:
    the clause removed."""
    registry.register_claim(claim())
    other = ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                 "period-balanced", ("DESIGN_C",), ("L-1",), "cal-9")
    rows = extended(ledger.records(), KIND_CLAIM, _ledger_id("claim", "claim-1"), other.to_payload())
    assert refusal_of(lambda: replay_state(rows)) == "invalid_record"


def test_a_second_disclosure_row_of_an_event_refuses_replay(registry: RegistrationRegistry, ledger: Ledger,
                                                            clock: ManualClock) -> None:
    """``admit_disclosure``'s one-release-per-event clause, reachable by replay only. Mutant: the clause removed."""
    clock.set(day(21))
    registry.submit_forecast(forecast("E-1"))
    clock.set(day(41))
    registry.forecasts_of("E-1")
    rows = extended(ledger.records(), KIND_DISCLOSURE, _ledger_id("disclosure", "E-1"), {"event_id": "E-1"})
    assert refusal_of(lambda: replay_state(rows)) == "invalid_record"


# Adjudication --------------------------------------------------------------------------------------------------


def adjudication_ledger(tmp_path: Path) -> tuple[Ledger, ManualClock, AdjudicationRegistry]:
    clock = ManualClock(aday(1))
    ledger = Ledger(tmp_path / "a.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    registry.register_event(aspec())
    return ledger, clock, registry


def test_a_disposition_adjudicated_after_its_receipt_refuses_replay(tmp_path: Path) -> None:
    """``_check_disposition``: the adjudication time is at or before the row's receipt (pass 6 A8). The row here is the
    adjudication of the records before it at day 112, received at day 111. Mutant: the receipt clause removed."""
    ledger, clock, registry = adjudication_ledger(tmp_path)
    clock.set(aday(111))
    registry.submit_observation(observation(110))
    state = adjudication_module.replay_state(ledger.records())
    event = state.event("E")
    assert event.spec is not None
    ahead = adjudicate(event.spec, state.rules["src"], event.records, event.observations, [], aday(112),
                       event.observation_receipts, {})
    ledger.append(adjudication_module.KIND_DISPOSITION, adjudication_module._ledger_id("disposition", "E"),
                  ahead.to_payload())  # received at day 111
    assert refusal_of(lambda: registry.adjudicate("E")) == "invalid_record"


def test_a_second_archive_of_one_digest_refuses_replay(tmp_path: Path) -> None:
    """``admit_content``'s one-read-per-digest clause, reachable by replay only. Mutant: the clause removed."""
    ledger, clock, registry = adjudication_ledger(tmp_path)
    received = record("r-1", occurrence=90, published=95)
    registry.archive_content(received.content)
    rows = extended(ledger.records(), adjudication_module.KIND_CONTENT,
                    adjudication_module._ledger_id("content", received.content.sha256), received.content.to_payload())
    assert refusal_of(lambda: adjudication_module.replay_state(rows)) == "invalid_record"


def test_a_knowable_correction_before_any_disposition_refuses_replay(tmp_path: Path) -> None:
    """``_check_correction``: a correction stands beside a stored disposition only. Mutant: that clause removed."""
    ledger, clock, registry = adjudication_ledger(tmp_path)
    clock.set(aday(100))
    submit(registry, record("r-1", occurrence=90, published=95, observed=100))
    rows = extended(ledger.records(), adjudication_module.KIND_KNOWABLE,
                    adjudication_module._ledger_id("knowable", "E", "r-1"),
                    {"event_id": "E", "knowable_at": format_timestamp(aday(95)), "record_id": "r-1"})
    assert refusal_of(lambda: adjudication_module.replay_state(rows)) == "invalid_record"


# The gate ------------------------------------------------------------------------------------------------------


def test_an_intent_received_exactly_at_its_capabilitys_expiry_refuses_replay(tmp_path: Path) -> None:
    """``_check_intent``: expired at or after the receipt (RC-37). Mutant: ``<``."""
    rig = Rig(tmp_path)
    rig.tick()
    capability = issue(rig.epoch(), "at-expiry", expiry=rig.clock.now())  # the receipt below is this instant
    reading = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())
    rig.ledger.append(KIND_INTENT, intent_ledger_id(capability),
                      IntentRecord(intent_ledger_id(capability), capability, "SIM_READ_ONLY", reading).to_payload())
    assert refusal_of(rig.gate.state) == "invalid_gate_ledger"


def test_a_drift_of_exactly_the_tolerance_is_continuous_live_and_on_replay(tmp_path: Path) -> None:
    """``discontinuity`` rotates on a drift beyond the tolerance, as the live gate does (``>``): a promotion read at a
    drift of exactly the tolerance replays. Mutant: ``>=`` in replay."""
    rig = Rig(tmp_path)
    rig.time.advance(timedelta(seconds=1), slew=timedelta(seconds=1))  # the drift is the tolerance, 1 s
    outcome = rig.promote(issue(rig.epoch(), "drift"))
    assert outcome.status == "acknowledged" and rig.gate.state().level == "SIM_READ_ONLY"


def test_a_check_row_with_another_verdict_refuses_replay(tmp_path: Path) -> None:
    """``_check_check``'s verdict clause. Mutant: the clause removed."""
    rig = Rig(tmp_path)
    rig.tick()
    head = rig.ledger.records()[-1].entry_hash
    reading = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())
    rig.ledger.append(KIND_CHECK, gate_ledger_id("gate-check", head),
                      CheckRecord("action:research", "other", "", reading).to_payload())
    assert refusal_of(rig.gate.state) == "invalid_gate_ledger"


def test_an_abort_row_under_another_identifier_refuses_replay(tmp_path: Path) -> None:
    """``replay_gate``'s abort identifier clause. Mutant: the clause removed."""
    rig = Rig(tmp_path)
    rig.tick()

    def killed() -> None:
        raise RuntimeError("the gate stops after its intent")

    rig.gate.hooks["after_intent"] = killed
    with pytest.raises(RuntimeError):
        rig.promote(issue(rig.epoch(), "a"))
    (intent_id,) = rig.gate.state().intents
    reading = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())
    rig.ledger.append(KIND_ABORT, "gate-abort:other", AbortRecord(intent_id, "chosen", reading).to_payload())
    assert refusal_of(rig.gate.state) == "invalid_gate_ledger"


# The ledger, the point-in-time store and the provenance check --------------------------------------------------


def test_a_restore_of_a_shorter_export_keeps_no_anchor_beyond_it(tmp_path: Path) -> None:
    """``Ledger.restore`` copies only the anchors of prefixes the export holds. Mutant: every anchor copied (the gate
    and the registration registry would count a later anchor as covering records the restored ledger lacks)."""
    clock = ManualClock(day(1))
    store = HarnessAnchorStore()
    source = Ledger(tmp_path / "source.sqlite", clock, store)
    for n in range(3):
        clock.advance(timedelta(seconds=1))
        source.append("candidate", f"c-{n}", {})
        source.anchor()
    restored, report = Ledger.restore(tmp_path / "restored.sqlite", clock,
                                      records_from_jsonl(source.export_jsonl())[:2], store)
    assert report.status == "truncated"
    assert [a.prefix_length for a in restored.local_anchors()] == [1, 2]


def test_two_vintages_available_at_one_time_are_ordered_by_vintage_id(tmp_path: Path) -> None:
    """``AsOfReader.series``: of two vintages of one observation with one ``available_at``, the greater vintage id is
    the latest (research/19 section 5, "Ties"). Mutant: ordered by ``available_at`` only (the first ingested wins)."""
    from datetime import datetime, timezone

    def at(n: int) -> datetime:
        return datetime(2026, 1, n, tzinfo=timezone.utc)

    store = PointInTimeStore(Ledger(tmp_path / "p.sqlite", ManualClock(at(10)), HarnessAnchorStore()))
    store.ingest(FeatureRow("X", "f", 1.0, at(1), at(2), "b"))
    store.ingest(FeatureRow("X", "f", 2.0, at(1), at(2), "a"))
    store.ingest(FeatureRow("Y", "f", 1.0, at(1), at(2), "a"))
    store.ingest(FeatureRow("Y", "f", 2.0, at(1), at(2), "b"))
    reader = store.reader(at(9))
    assert [v.vintage_id for v in reader.series("X", "f").observations.values()] == ["b"]
    assert [v.vintage_id for v in reader.series("Y", "f").observations.values()] == ["b"]


def test_an_assistant_named_after_generated_with_mid_line_is_a_promotional_footer() -> None:
    """The second promotional-footer pattern: an assistant named after "generated with/by" anywhere on a line, where
    the first pattern only reads a line that opens with it. Mutant: the second pattern removed."""
    findings = text_findings("Release notes, generated with Claude, follow.", "message")
    assert [f.split(":")[1].strip() for f in findings] == ["promotional footer at line 1"]
