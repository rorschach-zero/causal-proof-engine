"""Whole-codebase audit, pass 5 (issue #37), at ``b34c7212ca688d72611c3fd09b4eba170f94b44b``: adjudication replay.

- X2 (P1): replay took disposition, knowable-time correction and source-latency defect rows as written. A second
  ``disposition`` row, appended through ``Ledger.append``, turned a stored ``RESOLVED_NO`` into ``RESOLVED_YES``
  (RC-88: the disposition at finality is immutable), and a ``knowable_correction`` row naming no record lowered
  ``knowable_at`` from day 110 to day 30 (RC-146). Replay now admits a disposition only as the one disposition of
  its event, equal to the adjudication of the records before it at the time it names; a correction only at a time
  the record it names evidences; a defect only for a record that contradicts the stored disposition (class W of
  pass 4 extended, reading P5-R1).

Every ``test_x2_*`` test failed on the pass-5 commit; the last test checks that the API's own ledger still replays,
corrections and defects included."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.adjudication.registry import KIND_DEFECT, KIND_DISPOSITION, KIND_KNOWABLE, _ledger_id
from cpe.adjudication.rules import adjudicate
from cpe.clock import ManualClock, format_timestamp
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from tests.test_adjudication import day, observation, record, rule, spec, submit


def stored_no(tmp_path: Path, public_act: bool = False) -> tuple[Ledger, ManualClock, AdjudicationRegistry]:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule(public_act=public_act))
    registry.register_event(spec())
    clock.set(day(111))
    registry.submit_observation(observation(110))
    assert registry.adjudicate("E").disposition == "RESOLVED_NO"
    return ledger, clock, registry


def refuses(ledger: Ledger) -> None:
    with pytest.raises(Refusal) as refused:
        AdjudicationRegistry(ledger).state()
    assert refused.value.reason == "invalid_record"


def test_x2_a_second_disposition_row_refuses_the_ledger(tmp_path: Path) -> None:
    ledger, _, registry = stored_no(tmp_path)
    forged = replace(registry.adjudicate("E"), disposition="RESOLVED_YES")
    ledger.append(KIND_DISPOSITION, "disposition:forged", forged.to_payload())
    refuses(ledger)  # at b34c721: RESOLVED_YES


def test_x2_a_disposition_row_the_records_do_not_give_refuses_the_ledger(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    registry.register_event(spec())
    clock.set(day(111))
    registry.submit_observation(observation(110))
    honest = registry.state()  # nothing stored yet: write the disposition the records do not give
    assert honest.event("E").disposition is None
    fresh = adjudicate(spec(), rule(), [], honest.event("E").observations, [], day(111),
                       honest.event("E").observation_receipts)
    ledger.append(KIND_DISPOSITION, _ledger_id("disposition", "E"),
                  replace(fresh, disposition="RESOLVED_YES").to_payload())
    refuses(ledger)  # at b34c721: RESOLVED_YES on an absence observation


def test_x2_a_correction_naming_no_record_refuses_the_ledger(tmp_path: Path) -> None:
    ledger, _, _ = stored_no(tmp_path)
    ledger.append(KIND_KNOWABLE, _ledger_id("knowable", "E", "nothing"),
                  {"event_id": "E", "knowable_at": format_timestamp(day(30)), "record_id": "nothing"})
    refuses(ledger)  # at b34c721: knowable_at day 30


def test_x2_a_correction_at_a_time_its_record_does_not_evidence_refuses_the_ledger(tmp_path: Path) -> None:
    ledger, clock, registry = stored_no(tmp_path, public_act=True)
    clock.set(day(113))
    submit(registry, record("late", occurrence=95, published=112))  # a late report of a public occurrence at 95
    ledger.append(KIND_KNOWABLE, _ledger_id("knowable", "E", "late"),
                  {"event_id": "E", "knowable_at": format_timestamp(day(30)), "record_id": "late"})
    refuses(ledger)  # the record evidences day 95, not day 30


def test_x2_a_defect_naming_no_contradicting_record_refuses_the_ledger(tmp_path: Path) -> None:
    ledger, _, _ = stored_no(tmp_path)
    ledger.append(KIND_DEFECT, _ledger_id("defect", "E", "nothing"),
                  {"event_id": "E", "record_id": "nothing", "detail": "forged"})
    refuses(ledger)  # at b34c721: a defect against the source with no record behind it


def test_the_ledger_the_api_writes_still_replays(tmp_path: Path) -> None:
    ledger, clock, registry = stored_no(tmp_path, public_act=True)
    clock.set(day(113))
    submit(registry, record("late", occurrence=95, published=112))
    stored = registry.adjudicate("E")  # writes a defect and a correction to day 95
    assert [d.record_id for d in stored.defects] == ["late"] and stored.knowable_at == day(95)
    kinds = [r.kind for r in ledger.records()]
    assert kinds.count(KIND_DEFECT) == 1 and kinds.count(KIND_KNOWABLE) == 1
    assert AdjudicationRegistry(ledger).adjudicate("E") == stored
