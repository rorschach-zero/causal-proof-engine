"""Whole-codebase audit (issue #37): the P3 findings in registration, the point-in-time store, the issuance check and
the schemas, from pass 3 (comment 6348183848) and pass 4 (comment 6349971614). Each raised an untyped error, or
coerced a value, where ``AGENTS.md`` section 6 requires a typed refusal; a tuple field given as a string was split into
its characters and persisted. Every test failed on the pass-4 commit
``c3d6233dbaeb71eb71cb128394099b23cef285b5``."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.pointintime import FeatureRow, PointInTimeStore
from cpe.registration import CandidateEntry, ClaimPreregistration, ConfirmatoryRegister, RegistrationRegistry, VoidRequest
from cpe.schemas import Forecast
from cpe.validation.issuance import check_issuance
from tests.test_registration import clock, day, forecast, ledger, registry  # noqa: F401
from tests.test_schemas import HEX

HUGE = 10 ** 5000


def _claim(claim_id: str = "claim-1", cal: str = "cal-1") -> ClaimPreregistration:
    return ClaimPreregistration(claim_id, "fixed_question_set", "Q-1", "holder", day(1), day(60), day(400),
                                "period-balanced", ("DESIGN_C",), ("L-1",), cal)


def _candidate_payload(**over: Any) -> dict[str, Any]:
    base = {"candidate_id": "c", "event_id": "E", "source_id": "s", "listed_at": "2026-01-01T00:00:00.000000Z",
            "decision": "registered", "reason": "r"}
    base.update(over)
    return base


# Pass 3: reason fields are coerced with str(): any JSON value is accepted, and a huge integer escapes untyped ----------

def test_f1_candidate_reason_that_is_not_a_string_is_refused() -> None:
    with pytest.raises(Refusal):
        CandidateEntry.from_payload(_candidate_payload(reason=None))  # accepted and stored as the text "None"


def test_f1_candidate_reason_huge_integer_is_a_typed_refusal() -> None:
    with pytest.raises(Refusal):
        CandidateEntry.from_payload(_candidate_payload(reason=HUGE))  # plain ValueError from int->str digit limit


def test_f1_a_void_request_reason_that_is_not_text_is_refused(registry: RegistrationRegistry) -> None:
    with pytest.raises(Refusal):
        registry.request_void(VoidRequest("vr-1", "E-1", None))  # type: ignore[arg-type]


# Pass 3: log_candidate / submit_forecast / register_claim / PIT ingest bypass _payload_of: untyped crashes -------------

def test_f2_log_candidate_with_unserialisable_time_is_typed(registry: RegistrationRegistry) -> None:
    bad = CandidateEntry("cand-X", "X-1", "src", "2026-01-02T00:00:00.000000Z", "registered", "r")  # type: ignore[arg-type]
    with pytest.raises(Refusal):
        registry.log_candidate(bad)  # AttributeError


def test_f2_log_candidate_with_out_of_range_aware_time_is_typed(registry: RegistrationRegistry) -> None:
    early = datetime(1, 1, 1, tzinfo=timezone(timedelta(hours=1)))
    with pytest.raises(Refusal):
        registry.log_candidate(CandidateEntry("cand-X", "X-1", "src", early, "registered", "r"))  # OverflowError


def test_f2_submit_forecast_with_unserialisable_claim_time_is_typed(registry: RegistrationRegistry, clock: ManualClock) -> None:
    clock.set(day(21))
    good = forecast("E-1")
    bad = Forecast(good.event_id, good.arm_id, good.slot_id, good.arm_version_id, 0.3, 0.3, 0.3, HEX, HEX, (),
                   "2026-01-21")  # type: ignore[arg-type]
    with pytest.raises(Refusal):
        registry.submit_forecast(bad)  # AttributeError


def test_f2_register_claim_with_unserialisable_times_is_typed(registry: RegistrationRegistry) -> None:
    bad = ClaimPreregistration("claim-s", "fixed_question_set", "Q", "h", "2026-01-01",  # type: ignore[arg-type]
                               "2026-03-01", "2027-01-01",  # type: ignore[arg-type]
                               "period-balanced", ("DESIGN_C",), ("L-1",), "cal-s")
    with pytest.raises(Refusal):
        registry.register_claim(bad)  # AttributeError


def test_f2_pit_ingest_with_unserialisable_time_is_typed(ledger: Ledger) -> None:
    row = FeatureRow("E1", "f", 1.0, "2026-01-01", day(1), "v1")  # type: ignore[arg-type]
    with pytest.raises(Refusal):
        PointInTimeStore(ledger).ingest(row)  # AttributeError


def test_f2_pit_reader_with_string_as_of_is_typed(ledger: Ledger) -> None:
    reader = PointInTimeStore(ledger).reader(day(10))
    with pytest.raises(Refusal):
        reader.series("E1", "f", as_of="2026-01-05T00:00:00.000000Z")  # type: ignore[arg-type]


# Pass 3: a tuple field given as a string is split into characters and persisted -------------------------------------

def test_f3_forecast_evidence_ids_string_is_refused_not_split(registry: RegistrationRegistry, clock: ManualClock) -> None:
    clock.set(day(21))
    good = forecast("E-1")
    bad = Forecast(good.event_id, good.arm_id, good.slot_id, good.arm_version_id, 0.3, 0.3, 0.3, HEX, HEX,
                   "ev1")  # type: ignore[arg-type]
    try:
        record = registry.submit_forecast(bad)
    except Refusal:
        return
    pytest.fail(f"persisted evidence_ids={record.payload['evidence_ids']!r}")  # type: ignore[index, call-overload]


def test_f3_claim_family_order_string_is_refused_not_split(registry: RegistrationRegistry) -> None:
    bad = ClaimPreregistration("claim-s", "fixed_question_set", "Q", "h", day(1), day(60), day(400),
                               "period-balanced", "AB", "LM", "cal-s")  # type: ignore[arg-type]
    try:
        record = registry.register_claim(bad)
    except Refusal:
        return
    pytest.fail(f"persisted family_order={record.payload['family_order']!r}")  # type: ignore[index, call-overload]


# Pass 3: the issuance check crashes untyped on a provider map that is not a mapping ------------------------------------

def test_f6_issuance_with_a_non_mapping_provider_set_is_typed() -> None:
    with pytest.raises(Refusal):
        check_issuance("E-1", [("A", "A-1")], [], None, slot_id="primary")  # type: ignore[arg-type]


# Pass 3: register / calibration constructors crash untyped on a non-integer -------------------------------------------

def test_f7_register_with_non_integer_s_max_is_typed() -> None:
    with pytest.raises(Refusal):
        ConfirmatoryRegister("reg-1", "1", ())  # type: ignore[arg-type]


def test_p4_issuance_with_outputs_that_are_not_a_sequence_is_typed() -> None:
    with pytest.raises(Refusal) as refused:
        check_issuance("E-1", {"A": "A-1", "B": "B-1", "C": "C-1"}, None, None, slot_id="primary")  # type: ignore[arg-type]
    assert refused.value.reason == "invalid_outputs"
