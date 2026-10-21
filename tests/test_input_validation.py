"""Input validation and the mandatory-input check: T-22, T-26, T-28 (``17`` section 5, A4; F-04 and F-13 on the
issuance path). T-29 is the schema test ``test_t29_*`` of ``tests/test_schemas.py``. Offline and synthetic."""
from __future__ import annotations

import math
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cpe.errors import Refusal
from cpe.schemas import Forecast, ResearchOutput
from cpe.validation import check_issuance
from tests.test_schemas import HEX

PROVIDERS = ("P-A", "P-B", "P-C")
VERSIONS = {p: f"{p}-1" for p in PROVIDERS}  # the arm version each provider is registered under


def output(provider: str, event_id: str = "E-1", **forecast: Any) -> dict[str, Any]:
    values: dict[str, Any] = {"event_id": event_id, "arm_id": provider, "slot_id": "primary",
                              "arm_version_id": f"{provider}-1", "point": 0.4, "low": 0.3, "high": 0.5,
                              "prompt_hash": HEX, "model_hash": HEX, "evidence_ids": []}
    values.update(forecast)
    return {"arm_id": provider, "event_id": event_id, "forecast": {k: v for k, v in values.items() if v is not ...},
            "reasoning_digest": HEX, "evidence_ids": []}


def jev(event_id: str = "E-1", **overrides: Any) -> dict[str, Any]:
    record = {"jev_record_id": "J-1", "event_id": event_id, "inputs_digest": HEX, "result_positive": {"route": "yes"},
              "result_negative": {"route": "no"}, "model_hash": HEX, "routing_result": "research", "cost": 0.01}
    record.update(overrides)
    return record


def complete(**changes: Any) -> list[dict[str, Any]]:
    return [output(p, **(changes if p == "P-B" else {})) for p in PROVIDERS]


def test_three_valid_outputs_and_a_jev_record_are_issuable_in_provider_order() -> None:
    decision = check_issuance("E-1", VERSIONS, list(reversed(complete())), jev())
    assert decision.status == "issuable" and decision.problems == ()
    assert [o.arm_id for o in decision.outputs] == list(PROVIDERS) and decision.jev is not None


@pytest.mark.parametrize("changes, reason", [
    ({"point": math.nan}, "invalid_probability"),                 # T-26, F-13: NaN
    ({"point": 0.5, "low": 0.8, "high": 0.2}, "interval_disorder"),  # T-26, F-13: reversed [0.8, 0.2]
    ({"point": 1.25, "low": 1.2, "high": 1.3}, "invalid_probability"),  # T-26, F-13: [1.2, 1.3], above 1
    ({"point": math.inf}, "invalid_probability"),
    ({"point": ...}, "missing_field"),                             # T-22: interval-only forecast
    ({"point": 0.9, "low": 0.3, "high": 0.5}, "interval_disorder"),  # T-22: point outside its interval
    ({"model_hash": "z" * 64}, "invalid_digest"),                  # F-04 on the issuance path
])
def test_t22_t26_an_invalid_output_rejects_the_issuance_with_a_typed_reason(changes: dict[str, Any], reason: str) -> None:
    decision = check_issuance("E-1", VERSIONS, complete(**changes), jev())
    assert decision.status == "rejected" and decision.outputs == () and decision.jev is None
    assert [(p.reason, p.subject) for p in decision.problems] == [(reason, "outputs[1]"), ("missing_provider", "P-B")]


def test_t26_a_duplicate_provider_rejects_and_never_overwrites() -> None:
    outputs = complete() + [output("P-B", point=0.9, low=0.9, high=0.9)]
    decision = check_issuance("E-1", VERSIONS, outputs, jev())
    assert decision.status == "rejected" and decision.outputs == ()
    assert [(p.reason, p.subject) for p in decision.problems] == [("duplicate_provider", "P-B")]


@pytest.mark.parametrize("provider_set", [{"P-A": "P-A-1", "P-B": "P-B-1"},
                                          {"P-A": "P-A-1", "P-B": "P-B-1", "P-C": "P-C-1", "P-D": "P-D-1"},
                                          {"P-A": "P-A-1", "P-B": " ", "P-C": "P-C-1"}])
def test_the_registered_provider_set_is_three_providers_each_with_its_arm_version(provider_set: dict[str, str]) -> None:
    with pytest.raises(Refusal):
        check_issuance("E-1", provider_set, complete(), jev())


def test_t26_unknown_provider_and_another_event_reject() -> None:
    outputs = complete() + [output("P-Z")]
    decision = check_issuance("E-1", VERSIONS, outputs, jev(event_id="E-2"))
    assert decision.status == "rejected"
    assert {(p.reason, p.subject) for p in decision.problems} == {("unknown_provider", "outputs[3]"), ("wrong_event", "jev")}
    other = complete()
    other[0] = output("P-A", event_id="E-2")
    assert {p.reason for p in check_issuance("E-1", VERSIONS, other, jev()).problems} == {"wrong_event", "missing_provider"}


def test_t28_two_providers_or_no_jev_record_hold_the_issuance_without_fallback() -> None:
    two = check_issuance("E-1", VERSIONS, complete()[:2], jev())
    assert two.status == "held" and two.outputs == ()
    assert [(p.reason, p.subject) for p in two.problems] == [("missing_provider", "P-C")]
    no_jev = check_issuance("E-1", VERSIONS, complete(), None)
    assert no_jev.status == "held" and [p.reason for p in no_jev.problems] == ["missing_jev"]
    nothing = check_issuance("E-1", VERSIONS, [], None)
    assert nothing.status == "held" and len(nothing.problems) == 4


def test_t26_an_invalid_jev_record_rejects_and_a_rejection_outranks_a_hold() -> None:
    decision = check_issuance("E-1", VERSIONS, complete()[:2], jev(cost=-1))
    assert decision.status == "rejected"
    assert [(p.reason, p.subject) for p in decision.problems] == [("missing_provider", "P-C"), ("invalid_number", "jev")]


def test_a_directly_constructed_output_is_validated_through_its_payload() -> None:
    good = ResearchOutput.from_payload(output("P-B"))
    bad = ResearchOutput("P-B", "E-1", Forecast("E-1", "P-B", "primary", "P-B-1", 0.4, 0.3, 0.5, "not-hex", HEX, ()),
                         HEX, ())
    outputs: list[object] = [output("P-A"), bad, output("P-C")]
    assert check_issuance("E-1", VERSIONS, outputs, jev()).status == "rejected"
    outputs[1] = good
    assert check_issuance("E-1", VERSIONS, outputs, jev()).status == "issuable"


_numbers = st.one_of(st.floats(allow_nan=True, allow_infinity=True), st.floats(min_value=0.0, max_value=1.0))


@given(st.lists(st.tuples(_numbers, _numbers, _numbers), min_size=0, max_size=4), st.booleans())
def test_a4_issuable_exactly_when_three_valid_ordered_outputs_and_the_jev_record_are_given(
        triples: list[tuple[float, float, float]], with_jev: bool) -> None:
    outputs = [output(PROVIDERS[i % 3], low=low, point=point, high=high) for i, (low, point, high) in enumerate(triples)]
    decision = check_issuance("E-1", VERSIONS, outputs, jev() if with_jev else None)

    def valid(t: tuple[float, float, float]) -> bool:
        return all(math.isfinite(x) and 0.0 <= x <= 1.0 for x in t) and t[0] <= t[1] <= t[2]

    expected_issuable = len(triples) == 3 and all(valid(t) for t in triples) and with_jev
    assert (decision.status == "issuable") == expected_issuable
    if any(not valid(t) for t in triples) or len(triples) == 4:
        assert decision.status == "rejected"  # never held, never issued on the remaining providers
    if decision.status != "issuable":
        assert decision.outputs == () and decision.jev is None and decision.problems
