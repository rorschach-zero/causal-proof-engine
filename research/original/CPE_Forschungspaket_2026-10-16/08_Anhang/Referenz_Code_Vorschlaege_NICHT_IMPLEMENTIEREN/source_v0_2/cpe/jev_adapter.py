"""Typed TypeSafe Jev adapter (v0.2). Schema verified against the live OpenAPI
document at https://api.typesafe.ai/openapi.json (title 'TypeSafe', version
0.2.0, fetched 2026-10-16): POST /v1/systemone with {model, state, questions};
response {model, answers{name -> {type, noul|choice|score...}}, usage}.
GET /v1/models lists model names with release_date.

Design rules:
  * Jev never sees broker credentials, account data or order drafts.
  * Every call is recorded with origin timestamps and the model name RETURNED
    (the alias 'jev-latest' can silently change; the response's `model` is
    the version of record).
  * Every noul question is asked in both polarities; the complement gap
    |p + q - 1| is recorded. Published independent evaluation (arXiv:2609.33209)
    reports a mean gap of 0.064 on complement pairs; items with a large gap are
    treated as unreliable rather than averaged.
  * Jev probabilities are triage/classification signals. They become inputs to
    calibration only after prospective outcome data exists (see SCIENTIFIC_EXPERIMENTS.md).
  * Transport is injectable so tests run without network or API key.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Protocol
import json
import os
import time

JEV_URL = 'https://api.typesafe.ai/v1/systemone'
JEV_MODELS_URL = 'https://api.typesafe.ai/v1/models'


class Transport(Protocol):
    def __call__(self, url: str, headers: dict, body: dict, timeout: float) -> tuple[int, dict]: ...


def httpx_transport(url: str, headers: dict, body: dict, timeout: float) -> tuple[int, dict]:
    import httpx  # imported lazily so tests do not need network
    with httpx.Client(timeout=timeout) as client:
        r = client.post(url, headers=headers, json=body)
        try:
            return r.status_code, r.json()
        except ValueError:
            return r.status_code, {'_raw': r.text[:2000]}


class JevMalformed(ValueError):
    pass


@dataclass(frozen=True)
class JevNoulResult:
    question: str
    p_yes: float
    p_not: float            # from the negated question
    complement_gap: float   # |p_yes + p_not - 1|
    model_returned: str
    requested_at: datetime
    received_at: datetime
    latency_ms: float
    input_tokens: int
    raw_digest: str


def _check_prob(x: Any, name: str) -> float:
    if not isinstance(x, (int, float)) or isinstance(x, bool):
        raise JevMalformed(f'{name}: probability not numeric: {x!r}')
    if not (0.0 <= float(x) <= 1.0):
        raise JevMalformed(f'{name}: probability out of range: {x}')
    return float(x)


def parse_noul_response(resp: dict, names: tuple[str, str]) -> tuple[float, float, str, int]:
    if not isinstance(resp, dict) or 'answers' not in resp or 'model' not in resp:
        raise JevMalformed('response missing answers/model')
    ans = resp['answers']
    out = []
    for n in names:
        a = ans.get(n)
        if not isinstance(a, dict) or a.get('type') != 'noul':
            raise JevMalformed(f'answer {n} missing or wrong type')
        out.append(_check_prob(a.get('noul'), n))
    usage = resp.get('usage', {})
    toks = usage.get('input_tokens', 0) if isinstance(usage, dict) else 0
    return out[0], out[1], str(resp['model']), int(toks)


class JevClient:
    def __init__(self, api_key: str | None = None, transport: Transport | None = None,
                 model: str = 'jev-latest', timeout: float = 10.0, max_retries: int = 2,
                 cost_ceiling_tokens: int = 50_000_000, clock: Callable[[], datetime] | None = None):
        self.api_key = api_key or os.environ.get('TYPESAFE_API_KEY')
        self.transport = transport or httpx_transport
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.cost_ceiling_tokens = cost_ceiling_tokens
        self.tokens_used = 0
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        if transport is None and not self.api_key:
            raise ValueError('TYPESAFE_API_KEY required for live transport')

    def ask_noul_pair(self, state: str | dict, question: str, negated_question: str,
                      criteria_true: str | None = None, criteria_false: str | None = None) -> JevNoulResult:
        if self.tokens_used >= self.cost_ceiling_tokens:
            raise RuntimeError('Jev cost ceiling reached; research degraded, no further Jev calls')
        if any(k in json.dumps(state).lower() for k in ('accountkey', 'bearer ', 'refresh_token', 'access_token')):
            raise ValueError('refusing to send credential-like content to Jev')
        q: dict[str, Any] = {'type': 'noul', 'instructions': question}
        if criteria_true or criteria_false:
            q['criteria'] = {'true': criteria_true, 'false': criteria_false}
        body = {'model': self.model, 'state': state,
                'questions': {'q': q, 'q_not': {'type': 'noul', 'instructions': negated_question}}}
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        requested_at = self._clock()
        t0 = time.perf_counter()
        last_err: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                status, resp = self.transport(JEV_URL, headers, body, self.timeout)
            except Exception as ex:  # network-level
                last_err = ex
                time.sleep(min(2 ** attempt * 0.2, 2.0))
                continue
            if status == 429 or 500 <= status < 600:
                last_err = RuntimeError(f'Jev HTTP {status}')
                time.sleep(min(2 ** attempt * 0.2, 2.0))
                continue
            if status != 200:
                raise RuntimeError(f'Jev HTTP {status}: {str(resp)[:200]}')
            p, pn, model_ret, toks = parse_noul_response(resp, ('q', 'q_not'))
            received_at = self._clock()
            self.tokens_used += toks
            import hashlib
            return JevNoulResult(question, p, pn, abs(p + pn - 1.0), model_ret, requested_at, received_at,
                                 (time.perf_counter() - t0) * 1000, toks,
                                 hashlib.sha256(json.dumps(resp, sort_keys=True).encode()).hexdigest())
        raise RuntimeError(f'Jev unavailable after retries: {last_err}')
