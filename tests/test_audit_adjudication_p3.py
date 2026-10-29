"""Whole-codebase audit (issue #37): the P3 findings in ``cpe/adjudication``, from pass 3 (comment 6348183848) and
pass 4 (comment 6349971614).

- Pass 3: ``archive_content`` refused content a second registry on the same ledger archived first
  (``duplicate_record_id``) instead of reading it back (the D2 class).
- Pass 3: a malformed side row (``source_latency_defect``, ``knowable_correction``, ``integrity_incident``) raised
  ``KeyError`` on replay instead of a typed refusal.
- Pass 4: a naive datetime in ``submit_record`` or ``register_event`` raised ``TypeError``.
- Pass 4: a ``late_publication`` incident was persisted against a stored VOID its record never decided.
- PR #54 review ``4353163782``: a ``str`` subclass that compares and hashes like an archived digest while its text
  names another passed the content lookup, and the record written with its text made every later replay refuse.
- PR #54 review ``4353163787``: on a ledger an earlier version wrote, a status declared with a non-UTC offset kept an
  identifier formed from the offset, so the same instant declared again in UTC landed a conflicting status.

The pass-3 and pass-4 tests failed on the pass-4 commit ``c3d6233dbaeb71eb71cb128394099b23cef285b5``, except the
naive-time tests, which PR #54 already makes pass; the two review tests failed on the head of PR #54,
``fa7ac8630e3a67875de5108ab00e96a7df277b61``."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from cpe.adjudication import AdjudicationRegistry, SourceRule, SourceStatus
from cpe.adjudication.registry import KIND_DEFECT, KIND_INCIDENT, KIND_KNOWABLE, KIND_STATUS, _ledger_id, replay_state
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.schemas import EventSpec
from tests.test_adjudication import archived, day, record, rule, spec, submit


def _registry(tmp_path: Path, source_rule: SourceRule | None = None) -> tuple[AdjudicationRegistry, ManualClock, Ledger]:
    clock = ManualClock(day(3))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(source_rule or rule())
    return registry, clock, ledger


def test_archive_content_reads_back_content_another_registry_landed_first(tmp_path: Path) -> None:
    reg_a, clock, ledger = _registry(tmp_path)
    reg_b = AdjudicationRegistry(ledger)
    content = archived("occurred")
    snapshot = reg_b.state()

    def stale_state() -> Any:  # B's snapshot is taken before A's append lands
        reg_a.archive_content(content)
        reg_b.state = original  # type: ignore[method-assign]
        return snapshot

    original = reg_b.state
    reg_b.state = stale_state  # type: ignore[method-assign]
    landed = reg_b.archive_content(content)  # at c3d6233: Refusal('duplicate_record_id')
    assert landed.kind == "resolution_content"
    assert [r.kind for r in ledger.records()].count("resolution_content") == 1


@pytest.mark.parametrize("kind, payload", [
    (KIND_DEFECT, {"event_id": "E"}),
    (KIND_DEFECT, {"event_id": "E", "record_id": "r", "detail": 3}),
    (KIND_KNOWABLE, {"event_id": "E"}),
    (KIND_INCIDENT, {"kind": "receipt_lag", "reference_id": "r", "detail": "x"}),
])
def test_a_malformed_side_row_is_a_typed_refusal_on_replay(tmp_path: Path, kind: str, payload: dict[str, Any]) -> None:
    _, _, ledger = _registry(tmp_path)
    ledger.append(kind, "side-row", payload)
    with pytest.raises(Refusal):
        replay_state(ledger.records())  # at c3d6233: KeyError, or a detail coerced


def _naive_record(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    reg.register_event(spec())
    clock.set(day(101))
    r = record("r", occurrence=95, published=100)
    reg.archive_content(r.content)
    reg.submit_record(replace(r.record, first_observed_at=day(100).replace(tzinfo=None)))


def _naive_event(reg: AdjudicationRegistry, clock: ManualClock) -> None:
    s: EventSpec = spec()

    def naive(t: datetime) -> datetime:
        return t.replace(tzinfo=None)

    reg.register_event(replace(s, predicate=replace(s.predicate, not_before=naive(s.predicate.not_before),
                                                    not_after=naive(s.predicate.not_after)),
                               issuance_open=naive(s.issuance_open), issuance_close=naive(s.issuance_close),
                               evidence_cutoff=naive(s.evidence_cutoff)))


@pytest.mark.parametrize("call", [_naive_record, _naive_event])
def test_a_naive_time_is_a_typed_refusal(tmp_path: Path, call: Callable[[AdjudicationRegistry, ManualClock], None]) -> None:
    reg, clock, _ = _registry(tmp_path)
    with pytest.raises(Refusal):
        call(reg, clock)  # at c3d6233: TypeError


def test_no_late_publication_incident_claims_a_decision_that_was_not_made(tmp_path: Path) -> None:
    reg, clock, _ = _registry(tmp_path, rule(evidenced=False))
    reg.register_event(spec())
    clock.set(day(111))
    assert reg.adjudicate("E").disposition == "VOID"
    clock.set(day(115))
    submit(reg, record("late", occurrence=103, observed=115))  # expiry evidenced after the stored VOID
    after = reg.adjudicate("E")
    assert after.disposition == "VOID"
    assert [i.kind for i in after.incidents] == []  # at c3d6233: ['late_publication']


def test_a_receipt_lag_found_after_the_disposition_is_still_recorded(tmp_path: Path) -> None:
    reg, clock, _ = _registry(tmp_path)
    reg.register_event(spec())
    clock.set(day(100))
    submit(reg, record("r-1", occurrence=90, published=95, observed=100))
    assert reg.adjudicate("E").disposition == "RESOLVED_YES"
    clock.set(day(120))
    submit(reg, record("r-2", occurrence=90, published=96, observed=120))
    assert ("receipt_lag", "r-2") in {(i.kind, i.reference_id) for i in reg.adjudicate("E").incidents}


def test_4353163782_a_digest_that_only_compares_like_an_archived_one_writes_nothing_unreadable(tmp_path: Path) -> None:
    reg, clock, ledger = _registry(tmp_path)
    reg.register_event(spec())
    clock.set(day(101))
    r = record("r", occurrence=95, published=100)
    reg.archive_content(r.content)
    real = r.content.sha256

    class Mimic(str):
        def __eq__(self, other: object) -> bool:
            return other == real or str.__eq__(self, other)

        def __ne__(self, other: object) -> bool:
            return not self.__eq__(other)

        def __hash__(self) -> int:
            return hash(real)

    try:
        reg.submit_record(replace(r.record, content_digest=Mimic("ab" * 32)))
    except Refusal:
        pass  # refused at the write: the required behaviour
    reg.state()  # at fa7ac86: unknown_content, for this and every later reader


def test_4353163787_a_legacy_offset_identifier_is_still_one_status(tmp_path: Path) -> None:
    reg, clock, ledger = _registry(tmp_path)
    reg.register_event(spec())
    clock.set(day(101))
    declared = day(100).astimezone(timezone(timedelta(hours=1)))
    legacy = SourceStatus("src", False, declared)  # as an earlier version wrote it: the identifier keeps the offset
    ledger.append(KIND_STATUS, _ledger_id("status", "src", declared.isoformat()), legacy.to_payload())
    with pytest.raises(Refusal) as refused:
        reg.declare_source_status(SourceStatus("src", True, day(100)))  # at fa7ac86: lands beside it
    assert refused.value.reason == "duplicate_status"
