"""Golden ledger identifiers (issue #37, test gap G1).

The ledger identifier format is a contract: owner decision, delegated to the coordinator on 2026-10-22 (PR #35 finding
4347648529, ``research/19`` section 10). Identifiers are persisted, cross-referenced, covered by the anchored hashes and
reproduced byte for byte by replay and restore, so a change of format needs a schema version and a migration. Each test
writes every record kind of one component through its public operations and checks every record's identifier
against the format computed here, independently of the code: ``<prefix>:<SHA-256 of the canonical JSON list of the
identifying parts>``; two literal values pin the encoding itself."""
from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from cpe.adjudication import AdjudicationRegistry, SourceStatus
from cpe.capability import CapabilityGate
from cpe.clock import ManualClock, parse_timestamp
from cpe.ledger import HarnessAnchorStore, Ledger, Record
from cpe.pointintime import FeatureRow, PointInTimeStore
from cpe.registration import (
    BaseRate,
    BeaconOutput,
    CalibrationRecord,
    CandidateEntry,
    ClaimPreregistration,
    ConfirmatoryRegister,
    CutoffCorrection,
    RegistrationRegistry,
    VoidRequest,
)
from tests import test_adjudication as adj
from tests import test_registration as reg
from tests.test_capability import ENV, OTHER, OWNER, RELEASE, TOLERANCE, Rig, issue
from tests.test_review_round2_pr25 import PausingTimeSource


def identifier(prefix: str, *parts: str) -> str:
    canonical = json.dumps(list(parts), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return f"{prefix}:{hashlib.sha256(canonical.encode('ascii')).hexdigest()}"


def payload(record: Record) -> dict[str, Any]:
    assert isinstance(record.payload, dict)
    return record.payload


def test_the_encoding_itself_is_pinned() -> None:
    assert identifier("candidate", "cand-E-1") == \
        "candidate:2ab52ac67e16a90a11db667b96d3f2446fa94014b09a96ca0e327e8fe28e294d"
    assert identifier("register") == "register:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"


def registration_identifier(record: Record, earlier: list[Record]) -> str:
    p = payload(record)
    if record.kind == "forecast":
        key = (p["event_id"], p["arm_id"], p["slot_id"])
        number = 1 + sum(1 for r in earlier if r.kind == "forecast"
                         and (payload(r)["event_id"], payload(r)["arm_id"], payload(r)["slot_id"]) == key)
        return identifier("forecast", *key, str(number))
    return {
        "arm_version": lambda: identifier("arm-version", p["arm_version_id"]),
        "cutoff_correction": lambda: identifier("cutoff-correction", p["arm_version_id"], p["evidence_id"]),
        "candidate": lambda: identifier("candidate", p["candidate_id"]),
        "base_rate": lambda: identifier("base-rate", p["reference_class_id"]),
        "cluster_registration": lambda: identifier("cluster", p["cluster"]["cluster_id"]),
        "void_request": lambda: identifier("void-request", p["request_id"]),
        "claim_preregistration": lambda: identifier("claim", p["claim_id"]),
        "confirmatory_register": lambda: identifier("register"),
        "calibration_record": lambda: identifier("calibration", p["calibration_record_id"]),
        "beacon_output": lambda: identifier("beacon", p["output"]["calibration_record_id"]),
    }[record.kind]()


def test_every_registration_record_has_its_golden_identifier(tmp_path: Path) -> None:
    clock = ManualClock(reg.day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = RegistrationRegistry(ledger)
    for version in (reg.arm("A-1", "2026-01-05"), reg.arm("DESIGN_C-1", "2026-01-01"),
                    reg.arm("FULL-1", "2026-01-03", ["A-1"]), reg.arm("B-1", "2026-01-02")):
        registry.register_arm_version(version)
    registry.correct_cutoff(CutoffCorrection("B-1", date(2026, 1, 4), "provider-notice"))
    registry.commit_base_rate(BaseRate("RC-1", 0.2))
    registry.log_candidate(CandidateEntry("cand-E-1", "E-1", "src", reg.day(1), "registered", "match"))
    clock.set(reg.day(10))
    registry.register_cluster(reg.registration([reg.spec("E-1")]))
    registry.request_void(VoidRequest("vr-1", "E-1", "please"))
    for hour in (1, 2):  # two submissions before the window: kept, numbered 1 and 2
        clock.set(reg.day(10) + timedelta(hours=hour))
        registry.submit_forecast(reg.forecast("E-1"))
    clock.set(reg.day(21))
    registry.submit_forecast(reg.forecast("E-1"))  # in the window: number 3, fills the slot
    registry.register_claim(ClaimPreregistration("claim-1", "fixed_question_set", "Q-1", "holder", reg.day(1), reg.day(60),
                                                 reg.day(400), "period-balanced", ("DESIGN_C",), ("L-1",), "cal-1"))
    registry.record_calibration(CalibrationRecord("cal-1", "claim-1", "block-t", 1000, 0.01, "beacon", "round-7"))
    registry.anchor_confirmatory_register(ConfirmatoryRegister("reg-1", 1, ("claim-1",)))
    ledger.anchor()
    clock.set(reg.day(23))
    registry.supply_beacon_output(BeaconOutput("cal-1", "beacon", "round-7", "ab" * 32, reg.day(22)))

    records = list(ledger.records())
    kinds = {r.kind for r in records}
    assert kinds == {"arm_version", "cutoff_correction", "candidate", "base_rate", "cluster_registration",
                     "void_request", "forecast", "claim_preregistration", "confirmatory_register",
                     "calibration_record", "beacon_output"}
    for index, record in enumerate(records):
        assert record.record_id == registration_identifier(record, records[:index]), record.kind


def adjudication_identifier(record: Record) -> str:
    p = payload(record)
    return {
        "source_rule": lambda: identifier("rule", p["source_id"]),
        "event_spec": lambda: identifier("event", p["event_id"]),
        "resolution_content": lambda: identifier("content", p["sha256"]),
        "resolution_record": lambda: identifier("record", p["record_id"]),
        "absence_observation": lambda: identifier("observation", p["observation_id"]),
        "source_status": lambda: identifier("status", p["source_id"],
                                            parse_timestamp(p["declared_at"]).isoformat()),
        "disposition": lambda: identifier("disposition", p["event_id"]),
        "source_latency_defect": lambda: identifier("defect", p["event_id"], p["record_id"]),
        "knowable_correction": lambda: identifier("knowable", p["event_id"], p["record_id"]),
        "integrity_incident": lambda: identifier("incident", p["event_id"], p["kind"], p["reference_id"]),
    }[record.kind]()


def test_every_adjudication_record_has_its_golden_identifier(tmp_path: Path) -> None:
    clock = ManualClock(adj.day(3))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(adj.rule(public_act=True))
    registry.register_event(adj.spec())
    registry.declare_source_status(SourceStatus("src", False, adj.day(3)))
    clock.set(adj.day(110))
    registry.submit_observation(adj.observation(110))
    assert registry.adjudicate("E").disposition == "RESOLVED_NO"
    clock.set(adj.day(120))
    # a late report of a timely public occurrence: a source-latency defect and a knowable-time correction
    adj.submit(registry, adj.record("r-late", occurrence=96, published=118, observed=119))
    registry.adjudicate("E")
    # a record published inside the window and received after it: a receipt-lag incident
    adj.submit(registry, adj.record("r-timely", occurrence=97, published=105, observed=119))
    registry.adjudicate("E")

    records = list(ledger.records())
    kinds = {r.kind for r in records}
    assert kinds == {"source_rule", "event_spec", "source_status", "absence_observation", "disposition",
                     "resolution_content", "resolution_record", "source_latency_defect", "knowable_correction",
                     "integrity_incident"}
    for record in records:
        assert record.record_id == adjudication_identifier(record), record.kind


def test_every_gate_record_has_its_golden_identifier(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    time = PausingTimeSource(rig.clock)
    rig.time = time
    rig.gate = CapabilityGate(rig.ledger, OWNER, time, ENV, RELEASE, TOLERANCE)
    rig.tick()
    rig.gate.perform("research")  # an action-boundary check
    at_decision = issue(rig.epoch(), "at-decision", expiry=rig.clock.now())
    assert rig.refused(at_decision) == "expired"  # refused by the decision itself, named by the chain head
    rig.store.mode = "lost"
    assert rig.refused(issue(rig.epoch(), "unanchored")) == "anchor_failed"  # the abort of an intent left unanchored
    rig.tick()
    assert rig.refused(issue(rig.epoch(), "forged", verifier=OTHER)) == "invalid_signature"  # a refused presentation
    edge = issue(rig.epoch(), "edge", expiry=rig.clock.now() + timedelta(seconds=0.5))
    time.pause = timedelta(seconds=0.5)  # decided before the expiry, received at it: the refusal written at the receipt
    assert rig.refused(edge) == "expired"
    rig.tick()
    def demote() -> None:
        rig.gate.demote("between steps 2 and 3")

    rig.gate.hooks["after_intent_anchor"] = demote
    assert rig.refused(issue(rig.epoch(), "aborted")) == "superseded"  # intent, epoch rotation, abort at step 3
    rig.tick()
    assert rig.promote(issue(rig.epoch(), "promoted")).status == "acknowledged"  # intent, commit, acknowledgement

    records = list(rig.ledger.records())
    assert {r.kind for r in records} == {"gate_epoch", "gate_check", "gate_intent", "gate_abort", "gate_commit"}
    reasons = [payload(r)["reason"] for r in records if r.kind == "gate_abort"]
    assert reasons == ["anchor of the intent failed", "epoch rotated since the intent (RC-197)"]
    edge_intent = identifier("gate-intent", str(edge.epoch), edge.nonce)
    expired_at_receipt = 0
    for record in records:
        p = payload(record)
        if record.kind == "gate_epoch":
            expected = identifier("gate-epoch", str(p["index"]), str(p["epoch"]))
        elif record.kind == "gate_intent":
            capability = p["capability"]
            expected = identifier("gate-intent", str(capability["epoch"]), capability["nonce"])
            assert p["intent_id"] == expected
        elif record.kind == "gate_abort":
            expected = identifier("gate-abort", p["intent_id"])
        elif record.kind == "gate_commit":
            expected = identifier("gate-commit", p["intent_id"])
        elif p["subject"] == "presentation:edge":  # written by the admission check, at the receipt that showed it
            expected = identifier("gate-check", edge_intent, record.receipt_time)
            expired_at_receipt += 1
        else:  # every other check is named by the chain head it was decided on
            expected = identifier("gate-check", record.prev_hash)
        assert record.record_id == expected, (record.kind, p.get("subject"))
    assert expired_at_receipt == 1


def test_a_feature_row_has_its_golden_identifier(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(adj.day(10)), HarnessAnchorStore())
    record = PointInTimeStore(ledger).ingest(FeatureRow("entity", "feature", 1, adj.day(9), adj.day(9), "v1"))
    assert record.record_id == identifier("pit", "entity", "feature", "v1")
