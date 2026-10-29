"""Whole-codebase audit, pass 5 (issue #37), at ``b34c7212ca688d72611c3fd09b4eba170f94b44b``: typed refusals (P3).

The read interfaces looked an identifier up in a dictionary without validating it, so an identifier that is not a
string (a list, here) raised ``TypeError: unhashable type`` from ``AdjudicationRegistry.adjudicate`` and from
``RegistrationRegistry.arm_version``, ``event``, ``forecasts_of``, ``slot_states``, ``claim_status`` and
``seed_of``; ``AsOfReader.series`` returned an empty series for it, a result rather than a refusal. Each now refuses
it as ``invalid_identifier``. Unknown identifiers keep their own reasons (``unknown_event`` and the others).

Every case failed on the pass-5 commit, and on ``main`` at ``00168e7``."""
from __future__ import annotations

from collections.abc import Callable

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.errors import Refusal
from cpe.ledger import Ledger
from cpe.pointintime import PointInTimeStore
from cpe.registration import RegistrationRegistry
from tests.test_registration import clock, ledger, registry  # noqa: F401

BAD: object = ["E-1"]

CALLS: dict[str, Callable[[RegistrationRegistry, Ledger], object]] = {
    "adjudicate": lambda r, l: AdjudicationRegistry(l).adjudicate(BAD),  # type: ignore[arg-type]
    "arm_version": lambda r, l: r.arm_version(BAD),  # type: ignore[arg-type]
    "event": lambda r, l: r.event(BAD),  # type: ignore[arg-type]
    "forecasts_of": lambda r, l: r.forecasts_of(BAD),  # type: ignore[arg-type]
    "slot_states": lambda r, l: r.slot_states(BAD),  # type: ignore[arg-type]
    "claim_status": lambda r, l: r.claim_status(BAD),  # type: ignore[arg-type]
    "seed_of": lambda r, l: r.seed_of(BAD),  # type: ignore[arg-type]
    "series": lambda r, l: PointInTimeStore(l).reader(l.now()).series(BAD, "f"),  # type: ignore[arg-type]
    "row": lambda r, l: PointInTimeStore(l).reader(l.now()).row("e", "f", BAD),  # type: ignore[arg-type]
}


@pytest.mark.parametrize("call", sorted(CALLS))
def test_an_identifier_that_is_not_a_string_is_refused_typed(registry: RegistrationRegistry,  # noqa: F811
                                                              ledger: Ledger, call: str) -> None:  # noqa: F811
    with pytest.raises(Refusal) as refused:
        CALLS[call](registry, ledger)
    assert refused.value.reason == "invalid_identifier"


def test_an_unknown_identifier_keeps_its_reason(registry: RegistrationRegistry) -> None:  # noqa: F811
    with pytest.raises(Refusal) as refused:
        registry.event("E-9")
    assert refused.value.reason == "unknown_event"
