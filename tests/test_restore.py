"""T-08 (fixture part) and A1: restore from a clean checkout reports the anchored prefix and the unanchored window,
and the replayed state digest equals the committed one in every environment."""
from __future__ import annotations

import json
from pathlib import Path

from cpe.clock import SystemClock
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from tests.fixtures.restore.make_fixture import build

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "restore"


def test_committed_fixture_is_reproducible_from_its_generator() -> None:
    for name, text in build().items():
        assert (FIXTURE / name).read_text(encoding="ascii") == text, name


def test_restore_from_clean_checkout_matches_the_committed_digest_and_window(tmp_path: Path) -> None:
    records = records_from_jsonl((FIXTURE / "ledger.jsonl").read_text(encoding="ascii"))
    store = HarnessAnchorStore.from_export(json.loads((FIXTURE / "anchors.json").read_text(encoding="ascii")))
    expected = json.loads((FIXTURE / "expected.json").read_text(encoding="ascii"))
    ledger, report = Ledger.restore(tmp_path / "restored.sqlite", SystemClock(), records, store)
    assert ledger.state_digest() == expected["state_digest"]
    assert report.status == expected["status"] == "continuous"
    assert report.attestation == "verified"
    assert report.anchored_prefix == expected["anchored_prefix"] == 9
    assert report.unanchored_window == expected["unanchored_window"] == 1


def test_4329652627_the_generator_writes_exactly_the_committed_file_set(tmp_path: Path) -> None:
    """A file the generator stops emitting would otherwise stay committed and keep passing a diff."""
    from tests.fixtures.restore import make_fixture

    committed = {p.name for p in FIXTURE.iterdir() if p.name not in ("make_fixture.py", "__pycache__")}
    assert committed == set(build())
    out = tmp_path / "fresh"
    assert make_fixture.main([str(out)]) == 0
    assert {p.name for p in out.iterdir()} == committed
    for name in committed:
        assert (out / name).read_bytes() == (FIXTURE / name).read_bytes(), name
