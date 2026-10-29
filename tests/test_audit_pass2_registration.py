"""Whole-codebase audit, pass 2 (issue #37): the registration findings of the Codex auditor (issue #37 comment
``6346290601``, findings 5, 6 and 7). Each test failed on the audit commit ``2998824d0330ef028a8cc2cb7682a40f6fc23763``."""
from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from cpe.adjudication import classify_breaches
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.registration import BaseRate, CandidateEntry, ClusterRegistration, RegistrationRegistry
from cpe.schemas.forecast import ArmVersion
from tests.test_registration import arm, day, registration, spec

PLUS_TWO = timezone(timedelta(hours=2))


# 5 (P2): every registration write is validated as replay will read it ---------------------------------------------

def test_codex_5_an_invalid_arm_version_is_refused_before_it_is_written(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(day(1)), HarnessAnchorStore())
    registry = RegistrationRegistry(ledger)
    with pytest.raises(Refusal) as refused:
        registry.register_arm_version(ArmVersion("A-1", "", "provider", "v1", date(2025, 1, 1), "ev", ()))
    assert refused.value.reason == "invalid_identifier"
    assert ledger.state.count == 0  # at 2998824 the row was written and every later replay refused it
    registry.register_arm_version(arm("A-1", "2026-01-05"))


def test_codex_5_an_unserialisable_object_is_a_typed_refusal(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(day(1)), HarnessAnchorStore())
    broken = ArmVersion("A-1", "A", "provider", "v1", "2025-01-01", "ev", ())  # type: ignore[arg-type]
    with pytest.raises(Refusal) as refused:
        RegistrationRegistry(ledger).register_arm_version(broken)
    assert refused.value.reason == "invalid_object"
    assert ledger.state.count == 0


# 6 (P2): the cutoff rule compares e_i in UTC, as it is persisted ---------------------------------------------------

def test_codex_6_the_cutoff_rule_compares_the_utc_date_of_e_i(tmp_path: Path) -> None:
    clock = ManualClock(day(1))
    registry = RegistrationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    registry.register_arm_version(arm("A-1", "2025-12-01"))
    registry.register_arm_version(arm("DESIGN_C-1", "2025-12-01"))
    registry.register_arm_version(arm("FULL-1", "2026-01-05", ["A-1"]))
    registry.commit_base_rate(BaseRate("RC-1", 0.2))
    registry.log_candidate(CandidateEntry("cand-E", "E-1", "src", day(1), "registered", "match"))
    base = spec("E-1", issuance=(1.5, 3))
    local = datetime(2026, 1, 6, tzinfo=PLUS_TWO)  # 2026-01-05T22:00Z, on FULL's cutoff date
    event = replace(base, predicate=replace(base.predicate, not_before=local))
    with pytest.raises(Refusal) as refused:
        registry.register_cluster(registration([event]))
    assert refused.value.reason == "cutoff_after_e_i"  # at 2998824: admitted


def test_codex_6_an_early_knowability_breach_compares_the_utc_date() -> None:
    knowable = datetime(2026, 1, 6, tzinfo=PLUS_TWO)  # 2026-01-05T22:00Z
    report = classify_breaches("E", knowable, datetime(2025, 1, 1, tzinfo=timezone.utc), {"FULL": date(2026, 1, 5)}, [])
    assert report.early_knowability_arms == ("FULL",)


# 7 (P2): FULL is never the baseline arm ----------------------------------------------------------------------------

def test_codex_7_full_cannot_be_the_baseline_arm() -> None:
    base = registration([spec("E-1")])
    with pytest.raises(Refusal) as refused:
        ClusterRegistration(base.cluster, base.events, base.arm_versions, "FULL")
    assert refused.value.reason == "invalid_cluster"
    with pytest.raises(Refusal):
        ClusterRegistration.from_payload({**base.to_payload(), "baseline_arm_id": "FULL"})
