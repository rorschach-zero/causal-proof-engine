"""Whole-codebase audit, pass 1 (issue #37, findings C3 to C6): the reproduced P2 and P3 defects. Each test failed
on the audit commit 04fee70."""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpe.adjudication import AdjudicationRegistry
from cpe.canonical import canonical_bytes
from cpe.capability import CapabilityGate, HarnessVerifier, HostTimeSource
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.ledger import HarnessAnchorStore, Ledger
from cpe.ledger.store import records_from_jsonl
from cpe.pointintime import detect_leak
from cpe.registration import CalibrationRecord
from tests import test_adjudication as adj

REPOSITORY = Path(__file__).resolve().parent.parent
HUGE = 10 ** 5000  # beyond Python's default limit of 4300 decimal digits and beyond the float range


# P2: one fallback boot id per process ----------------------------------------------------------------------------

def test_the_fallback_boot_id_is_one_per_process(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(HostTimeSource, "_BOOT_ID_PATH", tmp_path / "no-boot-id")
    assert HostTimeSource().boot_id() == HostTimeSource().boot_id()


def test_two_gates_in_one_process_without_a_kernel_boot_id_see_no_reboot(monkeypatch: pytest.MonkeyPatch,
                                                                         tmp_path: Path) -> None:
    monkeypatch.setattr(HostTimeSource, "_BOOT_ID_PATH", tmp_path / "no-boot-id")
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(datetime(2026, 1, 1, tzinfo=timezone.utc)), HarnessAnchorStore())
    first = CapabilityGate(ledger, HarnessVerifier("owner"), HostTimeSource(), "env", "ab" * 32, 60.0)
    CapabilityGate(ledger, HarnessVerifier("owner"), HostTimeSource(), "env", "ab" * 32, 60.0)
    assert first.perform("research").kind == "gate_check"  # no clock_discontinuity


# P2: a stored disposition is judged by itself --------------------------------------------------------------------

def test_a_late_report_is_judged_against_the_stored_disposition(tmp_path: Path) -> None:
    clock = ManualClock(adj.day(3))
    registry = AdjudicationRegistry(Ledger(tmp_path / "l.sqlite", clock, HarnessAnchorStore()))
    registry.register_rule(adj.rule())
    registry.register_event(adj.spec())
    clock.set(adj.day(110))
    registry.submit_observation(adj.observation(110))
    assert registry.adjudicate("E").disposition == "RESOLVED_NO"
    clock.set(adj.day(120))
    # a record published inside the window, missed by the read at finality: a fresh adjudication would decide YES
    adj.submit(registry, adj.record("r-timely", occurrence=95, published=105, observed=119))
    # a late report of a timely occurrence: it contradicts the stored NO, not the fresh YES
    adj.submit(registry, adj.record("r-late", occurrence=96, published=118, observed=119))
    after = registry.adjudicate("E")
    assert after.disposition == "RESOLVED_NO"
    assert {d.record_id for d in after.defects} == {"r-late"}
    assert {d.record_id for d in registry.state().event("E").disposition.defects} == {"r-late"}  # type: ignore[union-attr]


# P2: a lemma closed by sorry is not verified ---------------------------------------------------------------------

def _lean_stub(tmp_path: Path, build_output: str) -> Path:
    """Stub ``elan`` and ``lake`` so that ``tools/lean_check.sh`` runs offline: the build prints ``build_output``
    and exits 0, as Lean does for a lemma closed by ``sorry``; the known-false lemma fails with ``linarith``."""
    stub = tmp_path / "bin"
    stub.mkdir()
    (stub / "elan").write_text("#!/bin/sh\nexit 0\n", encoding="ascii")
    (stub / "lake").write_text(
        "#!/bin/sh\ncase \"$1\" in\n"
        f"  build) printf '%s\\n' \"{build_output}\"; exit 0;;\n"
        "  env) echo 'error: linarith failed'; exit 1;;\n"
        "  *) exit 0;;\nesac\n", encoding="ascii")
    for name in ("elan", "lake"):
        (stub / name).chmod(0o755)
    return stub


@pytest.mark.parametrize("output, verified", [
    ("warning: declaration uses 'sorry'", False),
    ("'CPE.implication_prob_le' depends on axioms: [sorryAx]", False),
    ("'CPE.implication_prob_le' depends on axioms: [propext, Classical.choice, Quot.sound]", True),
])
def test_the_lean_job_never_verifies_a_lemma_that_uses_sorry(tmp_path: Path, output: str, verified: bool) -> None:
    stub = _lean_stub(tmp_path, output)
    env = {**os.environ, "PATH": f"{stub}{os.pathsep}{os.environ['PATH']}", "ELAN_HOME": str(tmp_path)}
    run = subprocess.run(["sh", "tools/lean_check.sh"], cwd=REPOSITORY, env=env, capture_output=True, text=True)
    assert (run.returncode == 0) is verified, run.stdout
    assert ("LEAN: VERIFIED" in run.stdout) is verified


# P3: an integer beyond the limits is a typed refusal -------------------------------------------------------------

def test_a_huge_integer_is_refused_by_the_canonical_form() -> None:
    with pytest.raises(Refusal) as refused:
        canonical_bytes({"value": HUGE})
    assert refused.value.reason == "integer_too_large"


def test_an_export_line_with_a_huge_integer_is_an_invalid_export() -> None:
    with pytest.raises(Refusal) as refused:
        records_from_jsonl('{"seq": ' + "1" * 5000 + "}\n")
    assert refused.value.reason == "invalid_export"


def test_a_huge_calibration_budget_is_refused() -> None:
    payload = CalibrationRecord("c", "k", "a", 1, 0.5, "b", "r").to_payload()
    with pytest.raises(Refusal) as refused:
        CalibrationRecord.from_payload({**payload, "budget": 10 ** 400})
    assert refused.value.reason == "invalid_calibration"


def test_a_huge_leak_bound_is_refused() -> None:
    with pytest.raises(Refusal) as refused:
        detect_leak([0.5], [1], bound=10 ** 400, permutations=1, seed=1)
    assert refused.value.reason == "invalid_bound"


def test_a_huge_slew_tolerance_is_refused(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.sqlite", ManualClock(datetime(2026, 1, 1, tzinfo=timezone.utc)), HarnessAnchorStore())
    with pytest.raises(Refusal) as refused:
        CapabilityGate(ledger, HarnessVerifier("owner"), HostTimeSource(), "env", "ab" * 32, 10 ** 400)
    assert refused.value.reason == "invalid_tolerance"
