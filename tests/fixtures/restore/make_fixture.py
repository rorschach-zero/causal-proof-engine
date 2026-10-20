"""Build the committed restore fixture deterministically (T-08).

Run from the repository root: ``python -I tests/fixtures/restore/make_fixture.py``. The test regenerates the fixture
in memory and compares it byte for byte with the committed files, so the fixture is reproducible from this code.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from cpe.canonical import JsonValue, canonical_bytes  # noqa: E402
from cpe.clock import ManualClock  # noqa: E402
from cpe.ledger import HarnessAnchorStore, Ledger  # noqa: E402

HERE = Path(__file__).resolve().parent


def build() -> dict[str, str]:
    clock = ManualClock(datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc))
    store = HarnessAnchorStore()
    ledger = Ledger(":memory:", clock, store)
    for i in range(6):
        clock.advance(timedelta(minutes=1))
        ledger.append("event", f"event-{i}", {"cluster_id": f"C-{i // 2}", "index": i})
    ledger.anchor()
    for i in range(3):
        clock.advance(timedelta(minutes=1))
        ledger.append("forecast", f"forecast-{i}", {"event_id": f"event-{i}", "point": 0.25 + i / 10})
    ledger.anchor()
    clock.advance(timedelta(minutes=1))
    ledger.append("resolution", "resolution-0", {"event_id": "event-0", "outcome": "YES"})
    report = ledger.verify(store)
    expected: JsonValue = {"state_digest": ledger.state_digest(), "anchored_prefix": report.anchored_prefix,
                           "unanchored_window": report.unanchored_window, "status": report.status}
    return {
        "ledger.jsonl": ledger.export_jsonl(),
        "anchors.json": canonical_bytes(store.export()).decode("ascii") + "\n",
        "expected.json": canonical_bytes(expected).decode("ascii") + "\n",
    }


if __name__ == "__main__":
    for name, text in build().items():
        (HERE / name).write_text(text, encoding="ascii")
        print(f"wrote {name}")
    print(json.dumps(json.loads((HERE / "expected.json").read_text()), indent=1))
