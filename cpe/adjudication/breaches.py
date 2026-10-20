"""Breach classes of a member's adjudicated ``knowable_at`` (RC-135, RC-139, RC-163).

Classification only: what a breach does in a comparison is the box rule of ``17`` section 3 item 3 and is not
built in Phase 1. A cutoff is a date; ``knowable_at`` is at or before it when it falls on that day or earlier.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime

from cpe.schemas.common import Payload, timestamp_payload


@dataclass(frozen=True)
class BreachReport:
    event_id: str
    knowable_at: datetime
    registration_breach: bool
    early_knowability_arms: tuple[str, ...]
    issuance_breach: bool

    @property
    def any_breach(self) -> bool:
        return self.registration_breach or bool(self.early_knowability_arms) or self.issuance_breach

    def to_payload(self) -> Payload:
        return {
            "event_id": self.event_id,
            "knowable_at": timestamp_payload(self.knowable_at),
            "registration_breach": self.registration_breach,
            "early_knowability_arms": list(self.early_knowability_arms),
            "issuance_breach": self.issuance_breach,
        }


def classify_breaches(event_id: str, knowable_at: datetime, scheduled_registration_time: datetime,
                      arm_effective_cutoffs: Mapping[str, date], cluster_issuance_closes: Sequence[datetime]) -> BreachReport:
    """Classify one adjudicated member.

    - registration breach: ``knowable_at`` at or before the cluster's scheduled registration time (RC-139, RC-200);
    - early-knowability breach of every arm whose effective cutoff is at or after ``knowable_at`` (RC-135, RC-156);
    - issuance breach: after the registration time and after every cutoff, but at or before the issuance close
      of a member of its cluster (RC-163).
    """
    registration = knowable_at <= scheduled_registration_time
    early = tuple(sorted(arm for arm, cutoff in arm_effective_cutoffs.items() if knowable_at.date() <= cutoff))
    issuance = (not registration and not early and bool(cluster_issuance_closes)
                and knowable_at <= max(cluster_issuance_closes))
    return BreachReport(event_id, knowable_at, registration, early, issuance)
