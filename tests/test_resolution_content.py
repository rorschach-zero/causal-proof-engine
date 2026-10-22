"""Resolution-content archive and predicate evaluation (hand-off section 3.1, decided 2026-10-21; PR #18 round-3
finding 4329664953): content-addressed source bytes on the ledger, the registered predicate evaluated over them, and
the claim derived from the evaluation rather than taken from the caller."""
from __future__ import annotations

import base64
from dataclasses import replace
from pathlib import Path

import pytest

from cpe.adjudication import (
    MEDIA_TYPE_JSON,
    AdjudicationRegistry,
    ArchivedContent,
    ResolutionRecord,
    adjudicate,
    evaluate,
)
from cpe.adjudication.registry import KIND_CONTENT, replay_state
from cpe.adjudication.rules import ReceivedRecord
from cpe.canonical import JsonValue, canonical_bytes, sha256_hex
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger, Record
from cpe.ledger.store import records_from_jsonl
from cpe.schemas.event import ResolutionPredicate
from tests.test_adjudication import archived, day, record, rule, spec, submit


def content_of(document: JsonValue, *, media_type: str = MEDIA_TYPE_JSON, source: str = "src",
               available: float = 0) -> ArchivedContent:
    data = canonical_bytes(document)
    return ArchivedContent(data, sha256_hex(data), media_type, source, day(available))


def predicate(comparator: str, value: JsonValue) -> ResolutionPredicate:
    return ResolutionPredicate.from_payload({**spec().predicate.to_payload(), "comparator": comparator, "value": value})


def stated(claim: str, content: ArchivedContent, record_id: str = "r", published: float = 105) -> ReceivedRecord:
    rec = ResolutionRecord(record_id, "E", "src", claim, day(published), content.sha256,  # type: ignore[arg-type]
                           occurrence_time=day(95) if claim == "occurred" else None,
                           evidenced_publication_time=day(published))
    return ReceivedRecord(rec, day(published), content)


def registry_at(tmp_path: Path, at: float) -> tuple[AdjudicationRegistry, ManualClock, Ledger]:
    clock = ManualClock(day(1))
    ledger = Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore())
    registry = AdjudicationRegistry(ledger)
    registry.register_rule(rule())
    registry.register_event(spec())
    clock.set(day(at))
    return registry, clock, ledger


# Tampered bytes

def test_bytes_that_do_not_have_the_declared_digest_are_refused() -> None:
    data = canonical_bytes({"sel": {"f": True}})
    with pytest.raises(Refusal) as refused:
        ArchivedContent(data, sha256_hex(b"other bytes"), MEDIA_TYPE_JSON, "src", day(0))
    assert refused.value.reason == "digest_mismatch"
    payload = content_of({"sel": {"f": True}}).to_payload()
    with pytest.raises(Refusal) as from_payload:
        ArchivedContent.from_payload({**payload, "sha256": sha256_hex(b"other bytes")})
    assert from_payload.value.reason == "digest_mismatch"


def test_tampered_archive_bytes_are_refused_on_replay(tmp_path: Path) -> None:
    registry, _, ledger = registry_at(tmp_path, 106)
    submit(registry, stated("occurred", content_of({"sel": {"f": True}})))
    forged_bytes = canonical_bytes({"sel": {"f": False}})
    forged_text = base64.b64encode(forged_bytes).decode("ascii")
    forged = tuple(replace(r, payload={**r.payload, "content_base64": forged_text})
                   if r.kind == KIND_CONTENT and isinstance(r.payload, dict) else r for r in ledger.records())
    with pytest.raises(Refusal) as refused:
        replay_state(forged)
    assert refused.value.reason == "digest_mismatch"


def test_a_record_with_other_content_than_it_names_is_refused() -> None:
    named, given = content_of({"sel": {"f": True}}), content_of({"sel": {"f": True, "g": 1}})
    received = stated("occurred", named)
    with pytest.raises(Refusal) as refused:
        adjudicate(spec(), rule(), [replace(received, content=given)], [], [], day(106))
    assert refused.value.reason == "content_mismatch"


# The claim is derived from the evaluation (4329664953)

def test_4329664953_a_stated_claim_that_the_content_contradicts_is_refused(tmp_path: Path) -> None:
    """A caller's 'occurred' over content whose registered field does not hold resolves nothing."""
    contradicted = stated("occurred", content_of({"sel": {"f": False}}))
    with pytest.raises(Refusal) as pure:
        adjudicate(spec(), rule(), [contradicted], [], [], day(106))
    assert pure.value.reason == "claim_disagrees"
    registry, clock, ledger = registry_at(tmp_path, 106)
    registry.archive_content(contradicted.content)
    with pytest.raises(Refusal) as refused:
        registry.submit_record(contradicted.record)
    assert refused.value.reason == "claim_disagrees"
    assert [r.kind for r in ledger.records()].count("resolution_record") == 0
    assert registry.adjudicate("E").disposition == "OPEN"


def test_the_disposition_follows_the_evaluated_content(tmp_path: Path) -> None:
    registry, _, _ = registry_at(tmp_path, 106)
    submit(registry, stated("occurred", content_of({"sel": {"f": True}, "other": {"f": False}})))
    decided = registry.adjudicate("E")
    assert decided.disposition == "RESOLVED_YES" and decided.deciding_record_id == "r"


# No evidence is not a NO

@pytest.mark.parametrize("document", [{"other": {"f": True}}, {"sel": {"g": True}}, {}])
def test_a_selector_or_field_without_a_match_is_no_evidence_not_a_no(tmp_path: Path, document: JsonValue) -> None:
    content = content_of(document)
    assert evaluate(spec().predicate, content) is None
    for claim in ("occurred", "not-occurred"):
        with pytest.raises(Refusal) as refused:
            adjudicate(spec(), rule(), [stated(claim, content)], [], [], day(120))
        assert refused.value.reason == "no_evidence"
    registry, _, _ = registry_at(tmp_path, 120)
    registry.archive_content(content)
    with pytest.raises(Refusal) as at_registry:
        registry.submit_record(stated("not-occurred", content, published=106).record)
    assert at_registry.value.reason == "no_evidence"
    assert registry.adjudicate("E").disposition == "OPEN"  # after finality, with no evidence of absence


# Each comparator

@pytest.mark.parametrize("comparator, registered, observed, expected", [
    ("eq", True, True, "occurred"),
    ("eq", True, False, "not-occurred"),
    ("eq", 1, True, "not-occurred"),           # a boolean is not the number 1
    ("eq", True, 1, "not-occurred"),
    ("eq", 1, 1.0, "occurred"),                # numbers compare by value
    ("eq", "approved", "approved", "occurred"),
    ("eq", "approved", "Approved", "not-occurred"),
    ("eq", None, None, "occurred"),
    ("eq", 0, None, "not-occurred"),
    ("eq", "x", ["x"], "not-occurred"),
    ("ne", "approved", "pending", "occurred"),
    ("ne", "approved", "approved", "not-occurred"),
    ("ne", 1, True, "occurred"),
    ("lt", 10, 9.5, "occurred"),
    ("lt", 10, 10, "not-occurred"),
    ("le", 10, 10, "occurred"),
    ("le", 10, 10.01, "not-occurred"),
    ("gt", 10, 11, "occurred"),
    ("gt", 10, 10, "not-occurred"),
    ("ge", 10, 10.0, "occurred"),
    ("ge", 10, -3, "not-occurred"),
    ("in", ["approved", "granted"], "granted", "occurred"),
    ("in", ["approved", "granted"], "denied", "not-occurred"),
    ("in", [1, 2], True, "not-occurred"),
    ("in", [[1, 2], {"a": 1}], {"a": 1}, "occurred"),
])
def test_each_comparator_against_its_fixtures(comparator: str, registered: JsonValue, observed: JsonValue,
                                              expected: str) -> None:
    assert evaluate(predicate(comparator, registered), content_of({"sel": {"f": observed}})) == expected


@pytest.mark.parametrize("comparator, registered, observed", [
    ("lt", 10, "9"), ("le", "a", "b"), ("gt", 10, True), ("ge", True, 1), ("gt", 10, None), ("lt", 10, [1]),
])
def test_an_order_comparison_of_anything_but_two_numbers_is_refused(comparator: str, registered: JsonValue,
                                                                     observed: JsonValue) -> None:
    # A registered value that is not a number is refused by the schema since issue #37 (pass 3 A4); it is set here
    # past the schema, so that evaluation's own guard is still the one exercised.
    unchecked = predicate(comparator, 0)
    object.__setattr__(unchecked, "value", registered)
    with pytest.raises(Refusal) as refused:
        evaluate(unchecked, content_of({"sel": {"f": observed}}))
    assert refused.value.reason == "incomparable_values"


def test_an_unsupported_comparator_is_refused() -> None:
    unsupported = predicate("eq", True)
    object.__setattr__(unsupported, "comparator", "matches")  # past the schema, which admits none such
    with pytest.raises(Refusal) as refused:
        evaluate(unsupported, content_of({"sel": {"f": True}}))
    assert refused.value.reason == "unsupported_comparator"


# Media type and byte form

@pytest.mark.parametrize("media_type", ["text/html", "application/xml", "application/json; charset=utf-8"])
def test_an_unsupported_media_type_is_refused(media_type: str) -> None:
    with pytest.raises(Refusal) as refused:
        evaluate(spec().predicate, content_of({"sel": {"f": True}}, media_type=media_type))
    assert refused.value.reason == "unsupported_media_type"


@pytest.mark.parametrize("data", [
    b'{"sel": {"f": true}}',                   # insignificant whitespace
    b'{"sel":{"f":true},"sel":{"f":false}}',   # a repeated key
    b'{"sel":{"f":NaN}}',
    b'{"sel":{"f":"\xc3\xa9"}}',               # not the ASCII escape of the canonical form
    b'not json',
])
def test_bytes_not_in_the_canonical_json_form_are_refused(data: bytes) -> None:
    content = ArchivedContent(data, sha256_hex(data), MEDIA_TYPE_JSON, "src", day(0))
    with pytest.raises(Refusal) as refused:
        evaluate(spec().predicate, content)
    assert refused.value.reason == "non_canonical_content"


@pytest.mark.parametrize("document", [["sel"], {"sel": ["f"]}, {"sel": True}])
def test_content_that_is_not_keyed_records_is_refused(document: JsonValue) -> None:
    with pytest.raises(Refusal) as refused:
        evaluate(spec().predicate, content_of(document))
    assert refused.value.reason == "invalid_content_structure"


# The archive on the ledger

def test_the_archive_keeps_bytes_digest_media_type_source_and_times(tmp_path: Path) -> None:
    registry, clock, _ = registry_at(tmp_path, 50)
    content = content_of({"sel": {"f": True}}, available=40)
    written = registry.archive_content(content)
    assert written.kind == KIND_CONTENT and written.receipt_time == "2026-02-20T00:00:00.000000Z"
    held, receipt = registry.state().contents[content.sha256]
    assert held == content and receipt == day(50)
    clock.set(day(60))
    assert registry.archive_content(content) == written  # one digest, archived once
    with pytest.raises(Refusal) as conflict:
        registry.archive_content(replace(content, available_at=day(41)))
    assert conflict.value.reason == "content_conflict"


def test_the_archive_refuses_content_available_after_its_receipt_and_of_an_unknown_source(tmp_path: Path) -> None:
    registry, _, ledger = registry_at(tmp_path, 50)
    with pytest.raises(Refusal) as future:
        registry.archive_content(content_of({"sel": {"f": True}}, available=51))
    assert future.value.reason == "evidence_after_receipt"
    with pytest.raises(Refusal) as unknown:
        registry.archive_content(content_of({"sel": {"f": True}}, source="other"))
    assert unknown.value.reason == "unknown_source"
    assert [r.kind for r in ledger.records()].count(KIND_CONTENT) == 0


def test_a_record_naming_content_not_archived_is_refused(tmp_path: Path) -> None:
    registry, _, _ = registry_at(tmp_path, 106)
    with pytest.raises(Refusal) as refused:
        registry.submit_record(stated("occurred", content_of({"sel": {"f": True}})).record)
    assert refused.value.reason == "unknown_content"


def test_content_of_another_source_is_refused() -> None:
    other = content_of({"sel": {"f": True}}, source="other")
    with pytest.raises(Refusal) as refused:
        evaluate(spec().predicate, other)
    assert refused.value.reason == "wrong_source"


def test_the_record_payload_names_its_content_digest() -> None:
    received = record("r", occurrence=95, published=105)
    payload = received.record.to_payload()
    assert payload["content_digest"] == archived().sha256
    assert ResolutionRecord.from_payload(payload) == received.record
    with pytest.raises(Refusal) as missing:
        ResolutionRecord.from_payload({k: v for k, v in payload.items() if k != "content_digest"})
    assert missing.value.reason == "missing_field"
    with pytest.raises(Refusal) as invalid:
        ResolutionRecord.from_payload({**payload, "content_digest": "z" * 64})
    assert invalid.value.reason == "invalid_digest"


# Replay

def test_replay_of_the_export_is_identical(tmp_path: Path) -> None:
    registry, clock, ledger = registry_at(tmp_path, 106)
    submit(registry, stated("occurred", content_of({"sel": {"f": True}})))
    clock.set(day(107))
    online = registry.adjudicate("E")
    store = HarnessAnchorStore()
    restored_ledger, _ = Ledger.restore(tmp_path / "restored.sqlite", ManualClock(day(107)),
                                        records_from_jsonl(ledger.export_jsonl()), store)
    restored = AdjudicationRegistry(restored_ledger)
    assert restored_ledger.state_digest() == ledger.state_digest()
    assert restored.state() == registry.state()
    assert restored.adjudicate("E") == online
    assert restored_ledger.export_jsonl() == ledger.export_jsonl()


def test_replay_refuses_a_record_whose_content_is_not_before_it(tmp_path: Path) -> None:
    registry, _, ledger = registry_at(tmp_path, 106)
    submit(registry, stated("occurred", content_of({"sel": {"f": True}})))
    reordered: list[Record] = [r for r in ledger.records() if r.kind != KIND_CONTENT]
    with pytest.raises(Refusal) as refused:
        replay_state(tuple(reordered))
    assert refused.value.reason == "unknown_content"
