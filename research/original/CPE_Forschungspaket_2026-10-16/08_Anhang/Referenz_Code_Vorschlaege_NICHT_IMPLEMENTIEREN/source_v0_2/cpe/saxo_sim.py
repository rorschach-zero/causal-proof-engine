"""Saxo OpenAPI: SIM-only order precheck with an explicit gate state machine (v0.2).

NO ORDER EXECUTION. There is still no function that calls POST /trade/v2/orders.

Verified against official docs on 2026-10-16:
  * Environments (SIM base URL https://gateway.saxobank.com/sim/openapi, LIVE
    https://gateway.saxobank.com/openapi, one-day Developer-Portal tokens are
    SIM-only, "market data ... not available in SIM"):
    https://www.developer.saxo/openapi/learn/environments
  * Precheck request fields (AccountKey, Amount, AssetType, BuySell, OrderType,
    OrderPrice, OrderDuration, Uic, ExternalReference(<=50 chars), FieldGroups;
    `ManualOrder` is NOT listed on the precheck page):
    https://www.developer.saxo/openapi/referencedocs/trade/v2/orders/post__trade__precheck
  * Order placement: duplicate protection via `x-request-id` header ("exactly
    the same order within 15 seconds without specifying a different x-request-id
    header will be rejected"); `ManualOrder` "Indicates if the order is
    originated by a manual or automatic action", automated = "generated and/or
    routed without human intervention"; FX Options not tradable via OpenAPI:
    https://www.developer.saxo/openapi/learn/order-placement
  * PKCE: /authorize + /token, code_challenge_method S256, example
    expires_in 1200 s, refresh_token_expires_in 2400 s:
    https://www.developer.saxo/openapi/learn/oauth-authorization-code-grant-pkce

Changes vs v0.1:
  - AssetType restricted to a pilot whitelist of fully paid, loss-bounded types.
  - `ManualOrder` removed from the PRECHECK payload (undocumented there); it is
    set to False on the (future, not implemented) placement payload only.
  - ExternalReference (certificate id) and x-request-id (uuid4) added.
  - Amount must be an integer number of units for Stock/Etf; price sanity checks.
  - Fail-closed GateState machine; promotion requires an owner authorization
    record, never a code path the research agents can call.
  - Token never logged; HTTP errors are re-raised without request headers.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import os
import uuid

import httpx

SIM_API = 'https://gateway.saxobank.com/sim/openapi'
LIVE_API = 'https://gateway.saxobank.com/openapi'  # never used by this module

PILOT_ASSET_TYPES = ('Stock', 'Etf', 'Bond', 'MutualFund')   # fully paid, loss bounded by premium/price
EXCLUDED_IN_PILOT = ('CfdOnStock', 'CfdOnIndex', 'FxSpot', 'FxForward', 'FxOption', 'FuturesOption',
                     'StockOption', 'StockIndexOption', 'FutureContracts', 'FutureStrategies', 'Cfd')


class GateState(str, Enum):
    RESEARCH_ONLY = 'RESEARCH_ONLY'
    SIM_READ_ONLY = 'SIM_READ_ONLY'
    SIM_PRECHECK = 'SIM_PRECHECK'
    SIM_EXECUTION = 'SIM_EXECUTION'
    SHADOW_LIVE_QUOTES = 'SHADOW_LIVE_QUOTES'
    LIVE_CAPPED_1000 = 'LIVE_CAPPED_1000'


_ORDER = list(GateState)


@dataclass(frozen=True)
class OwnerAuthorization:
    """Signed-off promotion record. The secret lives only with the owner."""
    from_state: GateState
    to_state: GateState
    evidence_bundle_sha256: str   # hash of the test report that justifies promotion
    owner_mac: str                # HMAC(owner_secret, from|to|evidence) hex


class Gate:
    def __init__(self, state: GateState = GateState.RESEARCH_ONLY):
        self.state = state

    @staticmethod
    def expected_mac(owner_secret: bytes, from_state: GateState, to_state: GateState, bundle: str) -> str:
        import hmac
        return hmac.new(owner_secret, f'{from_state.value}|{to_state.value}|{bundle}'.encode(), 'sha256').hexdigest()

    def promote(self, auth: OwnerAuthorization, owner_secret: bytes) -> GateState:
        import hmac
        if auth.from_state != self.state:
            raise PermissionError('authorization does not match current state')
        if _ORDER.index(auth.to_state) != _ORDER.index(self.state) + 1:
            raise PermissionError('gates can only be promoted one step at a time')
        if not hmac.compare_digest(self.expected_mac(owner_secret, auth.from_state, auth.to_state, auth.evidence_bundle_sha256), auth.owner_mac):
            raise PermissionError('owner authorization invalid')
        if auth.to_state == GateState.LIVE_CAPPED_1000:
            raise PermissionError('LIVE promotion is blocked in v0.2 code by design; requires independent risk-gate sign-off and a separate release')
        self.state = auth.to_state
        return self.state

    def demote(self, reason: str) -> GateState:
        """Anyone (including automation) may demote; this is the kill switch."""
        self.state = GateState.RESEARCH_ONLY
        return self.state

    def require(self, minimum: GateState) -> None:
        if _ORDER.index(self.state) < _ORDER.index(minimum):
            raise PermissionError(f'gate {self.state.value} below required {minimum.value}')


@dataclass(frozen=True)
class SaxoInstrument:
    uic: int
    asset_type: str
    account_key: str
    currency: str = 'USD'
    lot_size: float = 1.0
    tradable: bool = False   # must be set True from /ref/v1/instruments/details readback, never by hand


def build_precheck_payload(inst: SaxoInstrument, amount: float, *, limit_price: float,
                           buy_sell: str = 'Buy', certificate_id: str = '') -> tuple[dict, dict]:
    """Returns (json_body, headers_without_auth). Caller adds Authorization."""
    if inst.asset_type in EXCLUDED_IN_PILOT or inst.asset_type not in PILOT_ASSET_TYPES:
        raise ValueError(f'AssetType {inst.asset_type!r} not permitted in the pilot whitelist {PILOT_ASSET_TYPES}')
    if not inst.tradable:
        raise ValueError('Instrument tradability must be confirmed from Saxo reference data readback')
    if amount <= 0 or limit_price <= 0:
        raise ValueError('Positive quantity and limit required')
    if inst.asset_type in ('Stock', 'Etf') and (amount != int(amount) or amount < inst.lot_size):
        raise ValueError('Stock/Etf amount must be a whole number of units >= lot size')
    if buy_sell not in ('Buy', 'Sell'):
        raise ValueError('Bad direction')
    if not certificate_id or len(certificate_id) > 50:
        raise ValueError('certificate_id (ExternalReference) required, <= 50 chars per Saxo docs')
    body = {
        'AccountKey': inst.account_key,
        'Amount': amount,
        'AssetType': inst.asset_type,
        'Uic': inst.uic,
        'BuySell': buy_sell,
        'OrderType': 'Limit',
        'OrderPrice': limit_price,
        'OrderDuration': {'DurationType': 'DayOrder'},
        'ExternalReference': certificate_id,
        'FieldGroups': ['Costs', 'MarginImpactBuySell'],
    }
    headers = {'x-request-id': str(uuid.uuid4()), 'Content-Type': 'application/json'}
    return body, headers


class SaxoHttpError(RuntimeError):
    pass


def sim_precheck(gate: Gate, payload: dict, headers: dict, *, access_token: str | None = None) -> dict:
    """SIM precheck only. Raises unless gate >= SIM_PRECHECK. Never places an order."""
    gate.require(GateState.SIM_PRECHECK)
    token = access_token or os.environ.get('SAXO_SIM_ACCESS_TOKEN')
    if not token:
        raise ValueError('Set SAXO_SIM_ACCESS_TOKEN using Saxo SIM developer portal')
    url = SIM_API + '/trade/v2/orders/precheck'
    assert '/sim/' in url and 'precheck' in url  # fail closed
    h = dict(headers); h['Authorization'] = f'Bearer {token}'
    try:
        with httpx.Client(timeout=15) as client:
            response = client.post(url, headers=h, json=payload)
    except httpx.HTTPError as ex:  # do not propagate request objects (they carry the bearer header)
        raise SaxoHttpError(f'transport error: {type(ex).__name__}') from None
    if response.status_code != 200:
        raise SaxoHttpError(f'precheck HTTP {response.status_code}: {response.text[:300]}')
    data = response.json()
    data['_payload_digest'] = sha256(repr(sorted(payload.items())).encode()).hexdigest()
    return data
