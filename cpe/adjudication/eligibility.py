"""Forecast eligibility from recorded timestamps (RC-52, RC-76, RC-87, RC-92; T-02 retained parts).

t*_k is the earliest time over all members of a cluster at which any outcome information could exist: the minimum
over members of the outcome's registry receipt, its adjudicated ``knowable_at`` and a VOID's adjudication time. A
forecast received at or after t*_k is excluded from the increment and kept as a labelled late forecast; one
outside its event's issuance window is out of window; one received before the registration record is refused at
submission and classified here for replay.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Literal

from cpe.adjudication.rules import Adjudication
from cpe.schemas.event import EventSpec

ForecastStatus = Literal["eligible", "before_registration", "out_of_window", "late"]


def cluster_knowable_time(members: Iterable[Adjudication]) -> datetime | None:
    candidates: list[datetime] = []
    for member in members:
        if member.knowable_at is not None:
            candidates.append(member.knowable_at)
        if member.timestamps is not None:
            candidates.append(member.timestamps.receipt)
        if member.disposition == "VOID" and member.adjudicated_at is not None:
            candidates.append(member.adjudicated_at)
    return min(candidates) if candidates else None


def classify_forecast(receipt: datetime, spec: EventSpec, registration_time: datetime,
                      t_star: datetime | None) -> ForecastStatus:
    if receipt < registration_time:  # at the same server time the ledger's sequence put the registration first
        return "before_registration"
    if not spec.issuance_open <= receipt <= spec.issuance_close:
        return "out_of_window"
    if t_star is not None and receipt >= t_star:
        return "late"
    return "eligible"
