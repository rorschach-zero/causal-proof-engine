"""The mandatory-input check of an issuance (``17`` section 3 item 4; T-22, T-26, T-28; RC-05, RC-15, RC-17).

Every issued forecast needs one valid research output from each of the three registered providers and a valid Jev
record for the same event. The check never repairs, drops or merges an input and never falls back to fewer
providers or to equal weights over what remains:

- an input that is invalid (non-finite, reversed, out of range, an interval without a point, a point outside its
  interval, a malformed digest, an object that cannot be serialised, another event, an unregistered provider, an
  arm version other than the one registered for its provider, a provider given twice) **rejects** the issuance,
  with one typed reason per problem;
- an input that is absent (a registered provider without an output, no Jev record) **holds** it;
- otherwise the issuance is **issuable**, with the validated outputs in the registered provider order.

A rejection outranks a hold, and every problem found is reported, not only the first. Inputs are taken as payloads
and validated in full as they would be replayed, so a directly constructed object cannot pass a value its payload
would refuse. The provider of an output is its ``arm_id``; the three providers and the arm version each is
registered under for the event are the owner's (RC-17, OD8) and the registry's (RC-96), and are passed in.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from cpe.errors import Refusal
from cpe.schemas import ResearchOutput
from cpe.schemas.common import require_identifier
from cpe.schemas.forecast import JevRecord

IssuanceStatus = Literal["issuable", "held", "rejected"]
PROVIDER_COUNT = 3  # three independently reasoning frontier models, plus Jev (AGENTS.md section 2 item 1)

_HOLD_REASONS = frozenset({"missing_provider", "missing_jev"})


@dataclass(frozen=True)
class Problem:
    """One typed reason: what is wrong, and with which input."""

    reason: str
    subject: str
    detail: str = ""

    @property
    def holds(self) -> bool:
        return self.reason in _HOLD_REASONS


@dataclass(frozen=True)
class IssuanceDecision:
    event_id: str
    status: IssuanceStatus
    problems: tuple[Problem, ...]
    outputs: tuple[ResearchOutput, ...]  # the validated outputs, in provider order; empty unless issuable
    jev: JevRecord | None  # the validated Jev record; None unless issuable


def _payload(value: object) -> object:
    """A payload as it would be replayed: a schema object goes through its own payload first. An object whose
    fields cannot be serialised (a directly constructed object with a value of the wrong type) is refused, never
    allowed to crash the check."""
    to_payload = getattr(value, "to_payload", None)
    if not callable(to_payload):
        return value
    try:
        return to_payload()
    except Refusal:
        raise
    except Exception as error:
        raise Refusal("invalid_object", f"{type(value).__name__} cannot be serialised: {error!r}") from None


def check_issuance(event_id: str, arm_versions: Mapping[str, str], outputs: Sequence[object],
                   jev: object | None) -> IssuanceDecision:
    """Decide whether an issuance on ``event_id`` has every mandatory input, each valid. ``arm_versions`` maps each
    of the three registered providers to the arm version the event is registered under for it."""
    event_id = require_identifier(event_id, "event_id")
    versions = {require_identifier(provider, "provider"): require_identifier(version, f"arm_versions[{provider}]")
                for provider, version in arm_versions.items()}
    if len(versions) != PROVIDER_COUNT:
        raise Refusal("invalid_provider_set", f"exactly {PROVIDER_COUNT} distinct providers are registered (RC-17)")
    registered = tuple(versions)

    problems: list[Problem] = []
    by_provider: dict[str, list[ResearchOutput]] = {}
    for index, raw in enumerate(outputs):
        subject = f"outputs[{index}]"
        try:
            output = ResearchOutput.from_payload(_payload(raw))
        except Refusal as refusal:
            problems.append(Problem(refusal.reason, subject, refusal.detail))
            continue
        if output.event_id != event_id:
            problems.append(Problem("wrong_event", subject, f"names {output.event_id}"))
        elif output.arm_id not in versions:
            problems.append(Problem("unknown_provider", subject, f"{output.arm_id} is not a registered provider"))
        elif output.forecast.arm_version_id != versions[output.arm_id]:
            problems.append(Problem("wrong_arm_version", subject, f"{output.arm_id} is registered as "
                                    f"{versions[output.arm_id]}, not {output.forecast.arm_version_id} (RC-96)"))
        else:
            by_provider.setdefault(output.arm_id, []).append(output)

    for provider in registered:
        given = by_provider.get(provider, [])
        if len(given) > 1:  # never overwritten, never one of them chosen
            problems.append(Problem("duplicate_provider", provider, f"{len(given)} outputs"))
        elif not given:
            problems.append(Problem("missing_provider", provider, "issuance is held, no fallback to fewer providers"))

    record: JevRecord | None = None
    if jev is None:
        problems.append(Problem("missing_jev", "jev", "issuance is held without the Jev record"))
    else:
        try:
            record = JevRecord.from_payload(_payload(jev))
        except Refusal as refusal:
            problems.append(Problem(refusal.reason, "jev", refusal.detail))
        else:
            if record.event_id != event_id:
                problems.append(Problem("wrong_event", "jev", f"names {record.event_id}"))

    if any(not problem.holds for problem in problems):
        return IssuanceDecision(event_id, "rejected", tuple(problems), (), None)
    if problems:
        return IssuanceDecision(event_id, "held", tuple(problems), (), None)
    return IssuanceDecision(event_id, "issuable", (), tuple(by_provider[p][0] for p in registered), record)
