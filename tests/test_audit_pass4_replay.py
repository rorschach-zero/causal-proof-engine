"""Whole-codebase audit, pass 4 (issue #37): class W. Replay trusted rows written through ``Ledger.append`` outside
the registry or gate API; it now re-validates every authority-bearing row as the write path did.

- W1: a gate intent with a capability the owner never signed, and its commit, gave the gate a level (17 item 5,
  RC-43, RC-46).
- W2: a second register row was read as the register (18 R9).
- W3: a register row after a seeded round was read as the register (18 section 6 M-1, RC-311).
- F5 (pass 3, re-rated P1): a beacon row's seed was taken as written, never derived (RC-187, RC-304).

The four ``test_w*``/``test_f5*`` tests failed on the pass-4 commit ``c3d6233dbaeb71eb71cb128394099b23cef285b5``.
The property tests check the other direction: every ledger the APIs write replays without a refusal, and replays to
the state the API holds."""
from __future__ import annotations

import random
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

import pytest

from cpe.capability.levels import LEVELS, LIVE
from cpe.canonical import digest_of
from cpe.capability.records import KIND_COMMIT, KIND_INTENT, CommitRecord, IntentRecord, gate_ledger_id
from cpe.capability.state import replay_gate
from cpe.capability.timesource import ClockReading
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.registration import BeaconOutput, CalibrationRecord, ClaimPreregistration, ConfirmatoryRegister
from cpe.registration import RegistrationRegistry
from cpe.registration.registry import (
    KIND_BEACON,
    KIND_CALIBRATION,
    KIND_CLAIM,
    KIND_REGISTER,
    KIND_ROUND_REFUSED,
    _ledger_id,
)
from cpe.registration.seeds import derive_seed
from cpe.schemas import Capability
from tests.test_audit_pass3_claim_status import calibrated, claim
from tests.test_capability import ENV, EVIDENCE, OTHER, OWNER, RELEASE, Rig, issue
from tests.test_registration import clock, day, ledger, registry  # noqa: F401
from tests.test_schemas import HEX

CAL_1 = CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7")


def intent_ledger_id(capability: Capability) -> str:
    """The identity the protected operation writes an intent under, spelled out so that this file runs on the
    pass-4 commit too (``cpe.capability.records.intent_ledger_id``)."""
    return f"gate-intent:{digest_of([str(capability.epoch), capability.nonce])}"


# W1: the gate --------------------------------------------------------------------------------------------------------

def forge_promotion(rig: Rig, intent: IntentRecord, record_id: str | None = None) -> None:
    """An intent and its commit, written through the generic append, then anchored: what the protected operation
    writes, minus its checks."""
    reading = ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())
    rig.ledger.append(KIND_INTENT, record_id or intent.intent_id, intent.to_payload())
    anchor = rig.ledger.anchor()
    rig.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent.intent_id),  # the gate's own identifier
                      CommitRecord(intent.intent_id, anchor.prefix_length, anchor.digest, reading).to_payload())
    rig.ledger.anchor()
    rig.tick()


def reading_of(rig: Rig) -> ClockReading:
    return ClockReading(rig.clock.now(), rig.time.monotonic(), rig.time.boot_id())


def test_w1_an_intent_the_owner_never_signed_confers_no_level(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    forged = issue(rig.epoch(), "forged", level="SIM_EXECUTION", verifier=OTHER)
    forge_promotion(rig, IntentRecord(intent_ledger_id(forged), forged, "SIM_EXECUTION", reading_of(rig)))
    with pytest.raises(Refusal) as refused:
        rig.gate.perform("sim_execution")  # at c3d6233: admitted
    assert refused.value.reason == "invalid_gate_ledger"


def forged_intents(rig: Rig) -> dict[str, tuple[IntentRecord, str | None]]:
    epoch, reading = rig.epoch(), reading_of(rig)

    def intent(nonce: str, **kwargs: object) -> IntentRecord:
        capability = issue(epoch, nonce, **kwargs)  # type: ignore[arg-type]
        return IntentRecord(intent_ledger_id(capability), capability, "SIM_READ_ONLY", reading)

    expired = intent("expired", expiry=rig.clock.now() - timedelta(seconds=1))
    other_target = intent("target")
    return {
        "another signer": (intent("signer", verifier=OTHER), None),
        "another environment": (intent("environment", environment="env-2"), None),
        "another release": (intent("release", release="cd" * 32), None),
        "another identity": (intent("identity"), "gate-intent:chosen"),
        "another target": (IntentRecord(other_target.intent_id, other_target.capability, "SIM_EXECUTION", reading), None),
        "expired at its receipt": (expired, None),
        "another epoch": (_with_epoch(intent("epoch"), epoch + 1), None),
    }


def _with_epoch(intent: IntentRecord, epoch: int) -> IntentRecord:
    capability = issue(epoch, intent.capability.nonce)
    return IntentRecord(intent_ledger_id(capability), capability, intent.target_level, intent.reading)


@pytest.mark.parametrize("case", ["another signer", "another environment", "another release", "another identity",
                                  "another target", "expired at its receipt", "another epoch"])
def test_w1_every_intent_the_protected_operation_would_refuse_refuses_the_ledger(tmp_path: Path, case: str) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    intent, record_id = forged_intents(rig)[case]
    forge_promotion(rig, intent, record_id)
    with pytest.raises(Refusal) as refused:
        rig.gate.state()
    assert refused.value.reason == "invalid_gate_ledger"


def test_w1_a_commit_step_3_would_abort_or_that_cites_no_covering_anchor_refuses_the_ledger(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    rig.gate.promote(issue(rig.epoch(), "first"), EVIDENCE)  # the gate is at SIM_READ_ONLY
    rig.tick()
    again = issue(rig.epoch(), "again")  # a second commit to the same level does not raise the gate
    forge_promotion(rig, IntentRecord(intent_ledger_id(again), again, "SIM_READ_ONLY", reading_of(rig)))
    with pytest.raises(Refusal) as refused:
        rig.gate.state()
    assert refused.value.reason == "invalid_gate_ledger"

    (tmp_path / "anchor").mkdir()
    other = Rig(tmp_path / "anchor")
    other.tick()
    capability = issue(other.epoch(), "unanchored", level="SIM_EXECUTION")
    intent = IntentRecord(intent_ledger_id(capability), capability, "SIM_EXECUTION", reading_of(other))
    other.ledger.append(KIND_INTENT, intent.intent_id, intent.to_payload())
    other.ledger.append(KIND_COMMIT, gate_ledger_id("gate-commit", intent.intent_id),
                        CommitRecord(intent.intent_id, 1, "ab" * 32, reading_of(other)).to_payload())
    with pytest.raises(Refusal) as refused:
        other.gate.state()
    assert refused.value.reason == "invalid_gate_ledger"


@pytest.mark.parametrize("seed", range(12))
def test_every_ledger_the_gate_writes_replays_to_its_state(tmp_path: Path, seed: int) -> None:
    """Property: for random sequences of the gate's API (promotions to every level below live, valid or not,
    demotions, actions, restarts and anchor-store outages), replay never refuses the ledger, and its level is the one
    the API's outcomes imply: the target of the last acknowledged promotion, the floor after a demotion or a restart
    (a commit left in doubt makes the level unknown until the next one). The gate's own state is this replay, so the
    level is checked against the outcomes rather than against ``state()`` (issue #37, pass 7)."""
    from cpe.capability.state import GateRules  # added with the fix; imported here so the file runs on c3d6233

    rules = GateRules(OWNER, ENV, RELEASE)
    rng = random.Random(seed)
    rig = Rig(tmp_path)
    targets = [level for level in LEVELS if level != LIVE and level != LEVELS[0]]
    expected: str | None = LEVELS[0]
    for step in range(30):
        rig.tick(rng.choice([0.2, 1, 5]))
        rig.store.available = rng.random() > 0.15
        choice = rng.random()
        try:
            if choice < 0.5:
                expiry = rig.clock.now() + timedelta(seconds=rng.choice([0.1, 60, 3600]))
                verifier = OTHER if rng.random() < 0.1 else OWNER
                target = rng.choice(targets)
                outcome = rig.gate.promote(issue(rig.epoch(), f"n-{step}", level=target, expiry=expiry,
                                                 verifier=verifier), EVIDENCE)
                expected = target if outcome.status == "acknowledged" else None
            elif choice < 0.65:
                expected = LEVELS[0]  # the demotion takes effect at once, anchored or not (RC-123)
                rig.gate.demote(f"step {step}")
            elif choice < 0.9:
                rig.gate.perform(rng.choice(["research", "sim_read", "sim_execution"]))
            else:
                rig.store.available = True
                expected = LEVELS[0]  # every start begins at the floor (RC-123)
                rig.restart()
        except Refusal as refusal:
            if refusal.reason == "commit_in_doubt":
                expected = None  # a commit record outside every anchor takes effect when an anchor covers it
        rig.store.available = True
        anchors = rig.ledger.local_anchors()
        prefix = max((a.prefix_length for a in anchors), default=0)
        replayed = replay_gate(rig.ledger.records(), prefix, rules, anchors)
        if expected is not None:
            assert replayed.level == expected


# W2, W3, F5: the registration registry -------------------------------------------------------------------------

def refusal_of(call: Callable[[], object]) -> str:
    with pytest.raises(Refusal) as refused:
        call()
    return refused.value.reason


def test_w2_a_second_register_row_confers_nothing(registry: RegistrationRegistry, ledger: Ledger,
                                                   clock: ManualClock) -> None:
    registry.register_claim(claim())
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    clock.set(day(11))
    ledger.anchor()
    assert registry.claim_status("claim-1") == "confirmatory"
    ledger.append(KIND_REGISTER, "register-amended", ConfirmatoryRegister("reg-2", 2, ()).to_payload())
    clock.set(day(12))
    ledger.anchor()
    assert refusal_of(lambda: registry.claim_status("claim-1")) == "invalid_record"  # at c3d6233: "exploratory"


def test_w3_a_register_row_after_a_seeded_round_confers_nothing(registry: RegistrationRegistry, ledger: Ledger,
                                                               clock: ManualClock) -> None:
    calibrated(registry, ledger, clock)
    clock.set(day(12))
    registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", HEX, day(11.5)))
    ledger.append(KIND_REGISTER, _ledger_id("register"), ConfirmatoryRegister("reg-1", 1, ("claim-1",)).to_payload())
    clock.set(day(13))
    ledger.anchor()
    assert refusal_of(lambda: registry.claim_status("claim-1")) == "invalid_record"  # at c3d6233: "confirmatory"


def test_f5_a_seed_not_derived_from_its_round_is_never_returned(registry: RegistrationRegistry, ledger: Ledger,
                                                                clock: ManualClock) -> None:
    calibrated(registry, ledger, clock)
    clock.set(day(12))
    output = BeaconOutput("cal-1", "beacon", "round-7", HEX, day(11.5))
    ledger.append(KIND_BEACON, _ledger_id("beacon", "cal-1"), {"output": output.to_payload(), "seed": "00" * 32})
    assert refusal_of(lambda: registry.seed_of("cal-1")) == "invalid_record"  # at c3d6233: "00" * 32


def forged_registration_rows() -> dict[str, tuple[str, str, object]]:
    """Rows the registry's API refuses to write, each after ``calibrated`` (claim-1 and cal-1, anchored at day 11),
    with the clock at day 12."""
    round_7 = BeaconOutput("cal-1", "beacon", "round-7", HEX, day(11.5))
    late = ClaimPreregistration("claim-2", "fixed_question_set", "Q-2", "holder", day(1), day(11), day(400),
                                "period-balanced", ("DESIGN_C",), ("L-1",), "cal-2")
    listing = ClaimPreregistration("claim-3", "source_listing", "Q-3", "holder", day(1), day(60), day(400),
                                   "period-balanced", ("DESIGN_C",), ("L-1",), "cal-3")
    reserved = ClaimPreregistration("claim-4", "fixed_question_set", "Q-4", "holder", day(1), day(60), day(400),
                                    "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1")
    return {
        "a seed not derived": (KIND_BEACON, _ledger_id("beacon", "cal-1"),
                               {"output": round_7.to_payload(), "seed": "00" * 32}),
        "a round other than the record's": (
            KIND_BEACON, _ledger_id("beacon", "cal-1"),
            {"output": BeaconOutput("cal-1", "beacon", "round-8", HEX, day(11.5)).to_payload(),
             "seed": derive_seed(CAL_1.to_payload(), HEX)}),
        "a round before the record's anchor": (
            KIND_BEACON, _ledger_id("beacon", "cal-1"),
            {"output": BeaconOutput("cal-1", "beacon", "round-7", HEX, day(10.5)).to_payload(),
             "seed": derive_seed(CAL_1.to_payload(), HEX)}),
        "a round received before its publication": (
            KIND_BEACON, _ledger_id("beacon", "cal-1"),
            {"output": BeaconOutput("cal-1", "beacon", "round-7", HEX, day(13)).to_payload(),
             "seed": derive_seed(CAL_1.to_payload(), HEX)}),
        "a refused round with no register": (KIND_ROUND_REFUSED, _ledger_id("round-refused", "cal-1"),
                                             {"output": round_7.to_payload(), "reason": "register_not_anchored"}),
        "a claim after its period started": (KIND_CLAIM, _ledger_id("claim", "claim-2"), late.to_payload()),
        "a source-listing claim": (KIND_CLAIM, _ledger_id("claim", "claim-3"), listing.to_payload()),
        "a claim reserving another's record": (KIND_CLAIM, _ledger_id("claim", "claim-4"), reserved.to_payload()),
        "a second calibration record": (
            KIND_CALIBRATION, _ledger_id("calibration", "cal-1b"),
            CalibrationRecord("cal-1b", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7").to_payload()),
        "a second register": (KIND_REGISTER, "register:other", ConfirmatoryRegister("reg-1", 1, ()).to_payload()),
    }


@pytest.mark.parametrize("case", list(forged_registration_rows()))
def test_every_row_the_registry_would_refuse_refuses_the_ledger(registry: RegistrationRegistry, ledger: Ledger,
                                                                clock: ManualClock, case: str) -> None:
    calibrated(registry, ledger, clock)
    clock.set(day(12))
    if case == "a second register":
        registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    kind, record_id, payload = forged_registration_rows()[case]
    ledger.append(kind, record_id, payload)  # type: ignore[arg-type]
    clock.set(day(13))
    ledger.anchor()
    assert refusal_of(lambda: registry.claim_status("claim-1")) == "invalid_record"


@pytest.mark.parametrize("seed", range(12))
def test_every_ledger_the_registry_writes_replays_without_a_refusal(registry: RegistrationRegistry, ledger: Ledger,
                                                                    clock: ManualClock, seed: int) -> None:
    """Property: for random sequences of the registry's API (claims, calibration records, the register, anchors,
    and rounds attested at random times, valid or not), replay never refuses the ledger, every seed is derived from
    its record and round, and every status is answered."""
    rng = random.Random(seed)
    now = 10.0
    for n in range(1, 4):
        registry.register_claim(ClaimPreregistration(
            f"claim-{n}", "fixed_question_set", f"Q-{n}", "holder", day(1), day(60), day(400), "period-balanced",
            ("DESIGN_C",), ("L-1",), f"cal-{n}"))
    for step in range(25):
        now += rng.choice([0.25, 0.5, 1])
        clock.set(day(now))
        n = rng.randint(1, 3)
        choice = rng.random()
        try:
            if choice < 0.2:
                registry.record_calibration(CalibrationRecord(f"cal-{n}", f"claim-{n}", "block-t", 1000, 0.01,
                                                              "beacon", f"round-{n}"))
            elif choice < 0.3:
                ids = tuple(f"claim-{i}" for i in range(1, 4) if rng.random() < 0.6)
                registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ids))
            elif choice < 0.55:
                ledger.anchor()
            else:
                published = now - rng.choice([0, 0.5, 1, 2, 4])
                registry.supply_beacon_output(BeaconOutput(f"cal-{n}", "beacon", f"round-{n}", HEX, day(published)))
        except Refusal:
            pass
        state = registry.state()  # never refuses on a ledger the API wrote
        for calibration_id, value in state.seeds.items():
            output = state.beacon_outputs[calibration_id]
            assert value == derive_seed(state.calibrations[calibration_id].to_payload(), output.value)
        for claim_id in state.claims:
            assert registry.claim_status(claim_id) in ("confirmatory", "exploratory")
