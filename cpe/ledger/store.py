"""The single transactional writer (SQLite, one process) with anchoring, export and restore."""
from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterable
from pathlib import Path

from cpe.canonical import JsonValue, canonical_bytes
from cpe.clock import Clock, format_timestamp
from cpe.errors import Refusal
from cpe.ledger.anchor import Anchor, AnchorStore
from cpe.ledger.record import Record, entry_digest
from cpe.ledger.replay import LedgerState, VerificationReport, replay, verify
from cpe.schemas.common import require_identifier

_SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    seq INTEGER PRIMARY KEY,
    record_id TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL,
    receipt_time TEXT NOT NULL,
    payload TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    entry_hash TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS anchors (
    prefix_length INTEGER PRIMARY KEY,
    digest TEXT NOT NULL,
    published_at TEXT NOT NULL
);
"""


class FaultInjector:
    """Arms one failure per named point of the append path; the failure fires once (fault-injection tests)."""

    def __init__(self) -> None:
        self._armed: dict[str, BaseException] = {}

    def arm(self, point: str, error: BaseException) -> None:
        self._armed[point] = error

    def hit(self, point: str) -> None:
        error = self._armed.pop(point, None)
        if error is not None:
            raise error


class Ledger:
    """Append-only ledger: one writer, one connection, one lock.

    An append is acknowledged by returning the record. Anything raised before the return is not an
    acknowledgement, and the caller must treat the record as not admitted until it reads the ledger back.
    """

    def __init__(self, path: str | Path, clock: Clock, anchor_store: AnchorStore | None = None,
                 faults: FaultInjector | None = None) -> None:
        self._clock = clock
        self._anchor_store = anchor_store
        self._faults = faults or FaultInjector()
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(path), isolation_level=None, check_same_thread=False)
        self._conn.executescript(_SCHEMA)
        self._state: LedgerState = replay(self.records())

    def close(self) -> None:
        self._conn.close()

    @property
    def state(self) -> LedgerState:
        return self._state

    def state_digest(self) -> str:
        return self._state.digest()

    def _records_locked(self) -> tuple[Record, ...]:
        rows = self._conn.execute(
            "SELECT seq, record_id, kind, receipt_time, payload, prev_hash, entry_hash FROM records ORDER BY seq"
        ).fetchall()
        return tuple(Record(row[0], row[1], row[2], row[3], json.loads(row[4]), row[5], row[6]) for row in rows)

    def records(self) -> tuple[Record, ...]:
        with self._lock:
            return self._records_locked()

    def _server_time(self) -> str:
        """The server clock as a canonical timestamp, refused when it is below the persisted high-water mark."""
        receipt_time = format_timestamp(self._clock.now())
        if receipt_time < self._state.high_water:
            raise Refusal("clock_rollback", f"server clock {receipt_time} is below the high-water mark "
                          f"{self._state.high_water}")
        return receipt_time

    def append(self, kind: str, record_id: str, payload: JsonValue) -> Record:
        require_identifier(kind, "kind")
        require_identifier(record_id, "record_id")
        with self._lock:
            receipt_time = self._server_time()
            seq = self._state.count + 1
            payload_text = canonical_bytes(payload).decode("ascii")
            canonical_payload: JsonValue = json.loads(payload_text)
            record = Record(seq, record_id, kind, receipt_time, canonical_payload, self._state.head,
                            entry_digest(seq, record_id, kind, receipt_time, canonical_payload, self._state.head))
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                self._faults.hit("before_insert")
                self._conn.execute(
                    "INSERT INTO records (seq, record_id, kind, receipt_time, payload, prev_hash, entry_hash) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (seq, record_id, kind, receipt_time, payload_text, record.prev_hash, record.entry_hash),
                )
                self._faults.hit("before_commit")
                self._conn.execute("COMMIT")
            except sqlite3.IntegrityError as error:
                self._conn.execute("ROLLBACK")
                raise Refusal("duplicate_record_id", f"{record_id} is already in the ledger") from error
            except BaseException:
                self._conn.execute("ROLLBACK")
                raise
            # The record is durable from here. The state change is the committed row; the in-memory state follows it.
            self._state.apply(record)
            self._faults.hit("after_commit")
            return record

    def export_jsonl(self) -> str:
        return "".join(canonical_bytes(record.to_payload()).decode("ascii") + "\n" for record in self.records())

    def write_export(self, path: str | Path) -> None:
        Path(path).write_text(self.export_jsonl(), encoding="ascii")

    def anchor(self) -> Anchor:
        """Anchor the whole committed prefix: publish externally first, then keep the local copy.

        Before publishing, the chain is verified against every anchor the external store already holds, so that a
        local history rewritten or truncated below an existing anchor can never pollute the store with a conflicting
        later anchor; and the clock is checked against the high-water mark, so that an anchor never carries a time
        before the records it covers.
        """
        if self._anchor_store is None:
            raise Refusal("no_anchor_store", "this ledger has no anchor store")
        with self._lock:
            if self._state.count == 0:
                raise Refusal("empty_ledger", "nothing to anchor")
            published_at = self._server_time()
            existing = self._anchor_store.anchors()
            if existing:
                report = verify(self._records_locked(), existing, external=True)
                if not report.intact:
                    raise Refusal("anchor_conflict", f"the ledger does not verify against the external store: {report.detail}")
            anchor = Anchor(self._state.count, self._state.head, published_at)
            self._anchor_store.publish(anchor)
            self._conn.execute(
                "INSERT OR REPLACE INTO anchors (prefix_length, digest, published_at) VALUES (?, ?, ?)",
                (anchor.prefix_length, anchor.digest, anchor.published_at),
            )
            return anchor

    def local_anchors(self) -> tuple[Anchor, ...]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT prefix_length, digest, published_at FROM anchors ORDER BY prefix_length").fetchall()
        return tuple(Anchor(row[0], row[1], row[2]) for row in rows)

    def verify(self, external: AnchorStore | None = None) -> VerificationReport:
        """Verify against the external store when given; against the local copy, self-attested, otherwise."""
        records = self.records()
        if external is not None:
            return verify(records, external.anchors(), external=True)
        return verify(records, self.local_anchors(), external=False)

    @classmethod
    def restore(cls, path: str | Path, clock: Clock, records: Iterable[Record], external: AnchorStore,
                faults: FaultInjector | None = None) -> tuple[Ledger, VerificationReport]:
        """Rebuild a ledger from exported records and verify it against the external anchor store.

        The restore refuses to run without an external store: a local anchor copy alone is self-attested, and a
        restore that trusts it could revive a rewritten history (T-18, RC-34).
        """
        ordered = tuple(records)
        replay(ordered)
        ledger = cls(path, clock, external, faults)
        if ledger.state.count != 0:
            raise Refusal("restore_target_not_empty", "restore needs an empty ledger")
        ledger._conn.execute("BEGIN IMMEDIATE")
        try:
            for record in ordered:
                ledger._conn.execute(
                    "INSERT INTO records (seq, record_id, kind, receipt_time, payload, prev_hash, entry_hash) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (record.seq, record.record_id, record.kind, record.receipt_time,
                     canonical_bytes(record.payload).decode("ascii"), record.prev_hash, record.entry_hash),
                )
            for anchor in external.anchors():
                if anchor.prefix_length <= len(ordered):
                    ledger._conn.execute(
                        "INSERT OR REPLACE INTO anchors (prefix_length, digest, published_at) VALUES (?, ?, ?)",
                        (anchor.prefix_length, anchor.digest, anchor.published_at),
                    )
            ledger._conn.execute("COMMIT")
        except BaseException:
            ledger._conn.execute("ROLLBACK")
            raise
        ledger._state = replay(ledger.records())
        return ledger, ledger.verify(external)


def records_from_jsonl(text: str) -> tuple[Record, ...]:
    records = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as error:
            raise Refusal("invalid_export", f"line {number}: {error}") from None
        records.append(Record.from_payload(payload))
    return tuple(records)
