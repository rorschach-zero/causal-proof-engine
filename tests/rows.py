"""Rows the ledger cannot hold, for the replay rules that refuse them (issue #37, pass 8).

The ledger refuses a second record under an identifier it already holds. A replay rule that refuses a second row of
one key (one disposition per event, one criteria record per event, one rule per source, one register, one intent per
nonce) therefore cannot be reached through ``Ledger``: a forged row under another identifier is refused by the
identifier check before the rule runs, and a test of the rule passes without it. ``extended`` appends a row under any
identifier, the one the registry gives included, as a consistent hash chain, for replay alone."""
from __future__ import annotations

from cpe.canonical import JsonValue
from cpe.ledger import Record
from cpe.ledger.record import entry_digest


def extended(records: tuple[Record, ...], kind: str, record_id: str, payload: JsonValue,
             receipt: str | None = None) -> tuple[Record, ...]:
    """``records`` and one more row after them, received at ``receipt`` (by default with the last row)."""
    head = records[-1].entry_hash
    seq = len(records) + 1
    stamp = receipt if receipt is not None else records[-1].receipt_time
    row = Record(seq, record_id, kind, stamp, payload, head, entry_digest(seq, record_id, kind, stamp, payload, head))
    return (*records, row)
