"""Whole-codebase audit, pass 5 (issue #37), at ``b34c7212ca688d72611c3fd09b4eba170f94b44b``: typed refusals (P3).

A value that is not a ``datetime`` where a time is bound raised ``AttributeError`` (``format_timestamp`` reads
``tzinfo``): a point-in-time reader built with a text cutoff, and a gate promotion presented with a directly constructed
capability whose expiry is text. The reader refuses it as ``invalid_timestamp``; the promotion refuses the capability
as ``invalid_object``, as every registry refuses an object whose fields cannot be serialised.

Every test failed on the pass-5 commit."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.pointintime import PointInTimeStore
from tests.test_capability import Rig, issue


def test_a_reader_bound_to_a_text_cutoff_is_refused(ledger: Ledger) -> None:
    with pytest.raises(Refusal) as refused:
        PointInTimeStore(ledger).reader("2026-01-01")  # type: ignore[arg-type]
    assert refused.value.reason == "invalid_timestamp"


def test_a_capability_with_a_text_expiry_is_refused(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.gate.anchor_epoch()
    capability = replace(issue(rig.gate.state().epoch, "n-1"), expiry="tomorrow")  # type: ignore[arg-type]
    count = len(rig.ledger.records())
    with pytest.raises(Refusal) as refused:
        rig.gate.promote(capability, {"evidence": 1})
    assert refused.value.reason == "invalid_object" and len(rig.ledger.records()) == count
