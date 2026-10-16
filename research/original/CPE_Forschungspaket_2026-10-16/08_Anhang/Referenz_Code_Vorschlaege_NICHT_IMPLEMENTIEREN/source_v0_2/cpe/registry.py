"""Forecast registry (v0.2): every forecast carries as-of, known-at, an exact
resolution criterion, an expiry and an objective grading rule, committed to the
ledger BEFORE the outcome can be known.

"10x potential" is not a forecast. A forecast is: "P(event E resolves YES by T)
where E := <machine-checkable predicate over a named data source>".
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from .ledger import AppendOnlyLedger


def _aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.utcoffset() is not None


class ForecastStatus(str, Enum):
    COMMITTED = 'committed'
    RESOLVED_YES = 'resolved_yes'
    RESOLVED_NO = 'resolved_no'
    EXPIRED_NO = 'expired_no'        # expiry passed, criterion not met -> graded NO
    VOID = 'void'                     # resolution source disappeared; graded as abstain, counted in void-rate


class Forecaster(str, Enum):
    CLAUDE = 'claude'
    OPENAI = 'openai'
    GEMINI = 'gemini'
    JEV = 'jev'
    FUSION = 'fusion'
    BASELINE_BASE_RATE = 'baseline_base_rate'
    BASELINE_MARKET = 'baseline_market_implied'
    HUMAN = 'human'


@dataclass(frozen=True)
class EventSpec:
    event_id: str
    statement: str                      # human-readable
    resolution_source: str              # named source (e.g. 'SEC EDGAR 10-K item 7', 'FDA approvals DB')
    resolution_predicate: str           # machine-checkable rule text, versioned
    resolves_not_before: datetime       # earliest time outcome can be known
    expires_at: datetime                # if not YES by then -> NO
    grading_rule_version: str

    def validate(self) -> None:
        for dt in (self.resolves_not_before, self.expires_at):
            if not _aware(dt):
                raise ValueError('timezone-aware timestamps required')
        if self.expires_at <= self.resolves_not_before:
            raise ValueError('expiry must follow earliest resolution')
        if not (self.statement and self.resolution_source and self.resolution_predicate):
            raise ValueError('statement, resolution_source and resolution_predicate required')
        banned = ('potential', 'could', 'might', 'significant', 'strong')
        low = self.resolution_predicate.lower()
        if any(f' {b} ' in f' {low} ' for b in banned):
            raise ValueError(f'resolution_predicate contains vague wording: {banned}')


@dataclass(frozen=True)
class Forecast:
    forecast_id: str
    event_id: str
    forecaster: Forecaster
    forecaster_version: str
    p_low: float
    p_high: float
    as_of: datetime                     # information cutoff used by the forecaster
    known_at: datetime                  # wall-clock when the forecast was produced
    evidence_ids: tuple[str, ...]
    reasoning_digest: str               # sha256 of the archived reasoning text
    abstained: bool = False

    def validate(self, spec: EventSpec) -> None:
        if self.event_id != spec.event_id:
            raise ValueError('forecast/event mismatch')
        if not (_aware(self.as_of) and _aware(self.known_at)):
            raise ValueError('timezone-aware timestamps required')
        if self.as_of > self.known_at:
            raise ValueError('as_of cannot be after known_at')
        if self.known_at >= spec.resolves_not_before:
            raise ValueError('forecast produced inside the resolution window: not prospective')
        if not self.abstained and not (0 <= self.p_low <= self.p_high <= 1):
            raise ValueError('incoherent probability interval')
        if not self.abstained and (self.p_high - self.p_low) > 0.5:
            raise ValueError('interval wider than 0.5 must be recorded as abstention')
        if len(self.reasoning_digest) != 64:
            raise ValueError('reasoning_digest must be sha256 hex')


class ForecastRegistry:
    """Ledger-backed registry. All writes are append-only ledger events."""

    def __init__(self, ledger: AppendOnlyLedger):
        self.ledger = ledger
        self._events: dict[str, EventSpec] = {}
        self._forecasts: dict[str, Forecast] = {}
        self._status: dict[str, ForecastStatus] = {}

    def register_event(self, spec: EventSpec) -> str:
        spec.validate()
        if spec.event_id in self._events:
            raise ValueError('event already registered; specs are immutable')
        self._events[spec.event_id] = spec
        self._status[spec.event_id] = ForecastStatus.COMMITTED
        payload = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in asdict(spec).items()}
        return self.ledger.append('event_registered', payload)

    def commit_forecast(self, f: Forecast) -> str:
        spec = self._events.get(f.event_id)
        if spec is None:
            raise ValueError('unknown event')
        f.validate(spec)
        if f.forecast_id in self._forecasts:
            raise ValueError('forecast ids are immutable; submit a new forecast_id for an update')
        if self._status[f.event_id] != ForecastStatus.COMMITTED:
            raise ValueError('event already resolved: late forecast rejected')
        self._forecasts[f.forecast_id] = f
        payload = {k: (v.isoformat() if isinstance(v, datetime) else (v.value if isinstance(v, Enum) else v))
                   for k, v in asdict(f).items()}
        payload['commit_digest'] = sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return self.ledger.append('forecast_committed', payload)

    def resolve(self, event_id: str, outcome: bool | None, resolved_at: datetime, resolver: str, evidence_id: str) -> str:
        spec = self._events[event_id]
        if not _aware(resolved_at) or resolved_at < spec.resolves_not_before:
            raise ValueError('resolution before window')
        if self._status[event_id] != ForecastStatus.COMMITTED:
            raise ValueError('already resolved')
        if outcome is None:
            status = ForecastStatus.VOID
        elif outcome:
            status = ForecastStatus.RESOLVED_YES
        elif resolved_at >= spec.expires_at:
            status = ForecastStatus.EXPIRED_NO
        else:
            status = ForecastStatus.RESOLVED_NO
        self._status[event_id] = status
        return self.ledger.append('event_resolved', {
            'event_id': event_id, 'status': status.value, 'resolved_at': resolved_at.isoformat(),
            'resolver': resolver, 'evidence_id': evidence_id})

    def status(self, event_id: str) -> ForecastStatus:
        return self._status[event_id]

    def forecasts_for(self, event_id: str) -> list[Forecast]:
        return [f for f in self._forecasts.values() if f.event_id == event_id]
