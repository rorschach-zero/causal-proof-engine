"""Whole-codebase audit, pass 6 (issue #37), at ``1dca8d75ab6f49a82397cd493714d8602131538b``: adjudication replay.

- Y1 (P1): replay took ``event_spec`` and ``source_rule`` rows as written. A second ``event_spec`` row, appended through
  ``Ledger.append``, replaced the registered resolution criteria (a timely YES at day 95 became ``EXPIRED_NO`` under a
  forged deadline of day 90); an event's first row was read even when it was received after its issuance window
  opened; a second ``source_rule`` row replaced the source's rule (``knowable_at`` day 96 became day 95).
  ``register_event`` and ``register_rule`` refuse all three (``event_immutable``, ``late_registration``,
  ``rule_immutable``). Replay now admits every adjudication row only under the identifier its write path gives it and
  by the rule that path applies, criteria, rule, content, records, observations and statuses included (class W of
  pass 4, reading P5-R1 extended).

Every ``test_y1_*`` test failed on the pass-6 commit; the parametrised test checks every other row kind the same way,
and the last test that the ledger the API writes still replays."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry, SourceStatus
from cpe.adjudication.registry import KIND_CONTENT, KIND_EVENT, KIND_OBSERVATION, KIND_RECORD, KIND_RULE, KIND_STATUS
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from tests.test_adjudication import archived, day, observation, record, rule, spec, submit



def timely_yes(tmp_path: Path) -> tuple[Ledger, ManualClock, AdjudicationRegistry]:
    """Event E (deadline 100, finality 110) registered at day 1; a timely YES, occurrence 95, published 96."""
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    registry.register_event(spec())
    clock.set(day(97))
    submit(registry, record("yes", occurrence=95, published=96))
    return ledger, clock, registry


def refuses(ledger: Ledger) -> None:
    with pytest.raises(Refusal) as refused:
        AdjudicationRegistry(ledger).adjudicate("E")
    assert refused.value.reason == "invalid_record"


def test_y1_a_second_event_spec_row_does_not_replace_the_criteria(tmp_path: Path) -> None:
    ledger, _, registry = timely_yes(tmp_path)
    with pytest.raises(Refusal) as immutable:
        registry.register_event(spec(deadline=90))
    assert immutable.value.reason == "event_immutable"  # the API refuses the rewrite
    ledger.append(KIND_EVENT, "event:forged", spec(deadline=90).to_payload())
    refuses(ledger)  # at 1dca8d7: EXPIRED_NO, the occurrence at 95 judged against a deadline of 90


def test_y1_an_event_spec_row_received_after_its_issuance_opened_is_not_criteria(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    clock.set(day(30))  # the issuance window of spec() opens at day 20
    with pytest.raises(Refusal) as late:
        registry.register_event(spec())
    assert late.value.reason == "late_registration"
    ledger.append(KIND_EVENT, "event:late", spec().to_payload())
    refuses(ledger)  # at 1dca8d7: the criteria recorded inside the issuance window are read as registered


def test_y1_a_second_source_rule_row_does_not_replace_the_rule(tmp_path: Path) -> None:
    ledger, _, registry = timely_yes(tmp_path)
    with pytest.raises(Refusal) as immutable:
        registry.register_rule(rule(public_act=True))
    assert immutable.value.reason == "rule_immutable"
    ledger.append(KIND_RULE, "rule:forged", rule(public_act=True).to_payload())
    refuses(ledger)  # at 1dca8d7: knowable_at day 95 (the occurrence as a public act), not day 96


def forged_rows() -> dict[str, tuple[str, str, object]]:
    """Rows the registry would refuse, each under the kind it names and an identifier of the writer's choosing."""
    content = archived()
    wrong_claim = record("wrong", claim="not-occurred", published=96)  # its content evaluates to "occurred"
    return {
        "content of an unregistered source": (KIND_CONTENT, "content:forged", archived(source="other").to_payload()),
        "content under another identifier": (KIND_CONTENT, "content:other-id", content.to_payload()),
        "record under another identifier": (KIND_RECORD, "record:other-id", record("other", published=96).record.to_payload()),
        "record whose content disagrees": (KIND_RECORD, "record:wrong",
                                           {**wrong_claim.record.to_payload(), "content_digest": content.sha256}),
        "observation made after its receipt": (KIND_OBSERVATION, "observation:late", observation(200).to_payload()),
        "observation of another source": (KIND_OBSERVATION, "observation:other",
                                          {**observation(97).to_payload(), "source_id": "other"}),
        "status declared after its receipt": (KIND_STATUS, "status:late", SourceStatus("src", True, day(200)).to_payload()),
        "status of an unregistered source": (KIND_STATUS, "status:other", SourceStatus("other", True, day(50)).to_payload()),
    }


@pytest.mark.parametrize("case", sorted(forged_rows()))
def test_every_row_the_registry_would_refuse_refuses_the_ledger(tmp_path: Path, case: str) -> None:
    ledger, _, _ = timely_yes(tmp_path)
    kind, record_id, payload = forged_rows()[case]
    ledger.append(kind, record_id, payload)  # type: ignore[arg-type]
    with pytest.raises(Refusal) as refused:
        AdjudicationRegistry(ledger).state()
    assert refused.value.reason == "invalid_record"


def test_the_adjudication_ledger_the_api_writes_still_replays(tmp_path: Path) -> None:
    ledger, _, registry = timely_yes(tmp_path)
    registry.register_rule(rule())  # the same rule and the same criteria again add nothing
    registry.register_event(spec())
    registry.declare_source_status(SourceStatus("src", False, day(50)))
    registry.submit_observation(observation(97))
    stored = registry.adjudicate("E")
    assert (stored.disposition, stored.knowable_at) == ("RESOLVED_YES", day(96))
    assert AdjudicationRegistry(ledger).adjudicate("E") == stored
