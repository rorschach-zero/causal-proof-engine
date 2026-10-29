"""Append-only JSONL event ledger with external anchoring (v0.2).

Threat model (new in v0.2):
  T1  In-place edit of one line            -> detected by v0.1 hash chain.
  T2  Full rewrite + re-hash of the chain  -> NOT detected by v0.1 (reproduced in
      review, attack F1). Detected in v0.2 iff an anchor taken BEFORE the rewrite
      is stored somewhere the writer cannot modify (separate volume/account,
      signed commit, OpenTimestamps, printed hash, e-mail to self, ...).
  T3  Truncation (drop tail entries)       -> detected by anchor length + head.
  T4  Clock rollback / reordering          -> `written_at` must be monotone.
  T5  Writer process itself is malicious   -> out of scope for a file ledger;
      requires an append-only store owned by a different principal (see spec §9).

Anchors are tiny JSON records {n, head_hash, anchored_at} and MUST be kept
outside the writer's write permission to be meaningful.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import hmac
import json


def _canonical(entry: dict) -> bytes:
    return json.dumps(entry, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf8')


class AppendOnlyLedger:
    def __init__(self, file: str | Path):
        self.path = Path(file)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ write
    def append(self, event_type: str, payload: dict) -> str:
        if not event_type or not isinstance(payload, dict):
            raise ValueError('event_type and payload required')
        prev_hash, n, last_written = self._tail()
        now = datetime.now(timezone.utc)
        if last_written is not None and now < last_written:
            raise ValueError('Clock moved backwards relative to ledger tail; refusing to append')
        entry = {
            'seq': n,
            'event_type': event_type,
            'written_at': now.isoformat(),
            'payload': payload,
            'prev_hash': prev_hash,
        }
        entry['entry_hash'] = sha256(_canonical(entry)).hexdigest()
        with self.path.open('a', encoding='utf8') as out:
            out.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + '\n')
        return entry['entry_hash']

    # ------------------------------------------------------------------- read
    def _tail(self) -> tuple[str, int, datetime | None]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return 'GENESIS', 0, None
        with self.path.open('rb') as inp:
            lines = inp.read().splitlines()
        last = json.loads(lines[-1])
        return last['entry_hash'], len(lines), datetime.fromisoformat(last['written_at'])

    def tail_hash(self) -> str:
        return self._tail()[0]

    def __len__(self) -> int:
        return self._tail()[1]

    def verify_chain(self) -> bool:
        previous = 'GENESIS'
        if not self.path.exists():
            return True
        last_time: datetime | None = None
        for i, line in enumerate(self.path.read_text(encoding='utf8').splitlines()):
            entry = json.loads(line)
            reported = entry.pop('entry_hash')
            if entry.get('seq') != i:
                return False
            if sha256(_canonical(entry)).hexdigest() != reported or entry['prev_hash'] != previous:
                return False
            t = datetime.fromisoformat(entry['written_at'])
            if last_time is not None and t < last_time:
                return False
            last_time = t
            previous = reported
        return True

    # ---------------------------------------------------------------- anchors
    def anchor(self, secret: bytes | None = None) -> dict:
        """Snapshot {n, head_hash, anchored_at[, mac]}. Store it OUTSIDE the writer's reach."""
        head, n, _ = self._tail()
        rec = {'n': n, 'head_hash': head, 'anchored_at': datetime.now(timezone.utc).isoformat()}
        if secret is not None:
            rec['mac'] = hmac.new(secret, _canonical(rec), 'sha256').hexdigest()
        return rec

    def verify_against_anchor(self, anchor: dict, secret: bytes | None = None) -> bool:
        """True iff the first anchor['n'] entries of the chain still hash to anchor['head_hash']."""
        if secret is not None:
            rec = {k: v for k, v in anchor.items() if k != 'mac'}
            if not hmac.compare_digest(hmac.new(secret, _canonical(rec), 'sha256').hexdigest(), anchor.get('mac', '')):
                return False
        if not self.verify_chain():
            return False
        if not self.path.exists():
            return anchor['n'] == 0 and anchor['head_hash'] == 'GENESIS'
        lines = self.path.read_text(encoding='utf8').splitlines()
        if len(lines) < anchor['n']:
            return False  # truncated
        if anchor['n'] == 0:
            return anchor['head_hash'] == 'GENESIS'
        return json.loads(lines[anchor['n'] - 1])['entry_hash'] == anchor['head_hash']
