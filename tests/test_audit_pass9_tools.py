"""Whole-codebase audit, pass 9 (issue #37), at ``811ba9d6bd13996cec72da62c0179d1baf71c6f2``: the tools.

- P9-6: two structural rules of ``tools/mutation_report.py`` classified behaviour as text: every argument of
  ``AbortRecord`` after its reason (the persisted reading) and of ``self._rotate`` (a baseline), and any value assigned
  to ``detail`` or ``aborted``, which the gate reads as conditions.
- P9-7: the import boundary passed ``antigravity`` (it opens a web browser on import) and, on Python 3.11, ``pipes``
  (``os.popen``) and ``mailcap`` (``os.system``), the class of B1 to B3. The closure: the boundary's own rules, run over
  the source of every module of the running interpreter's standard library, flag a module only if it is forbidden or
  is on the reviewed list below, with the reason it is not a facility of its own.
- P9-8: ``tools/lean_check.sh`` wrote fixed ``/tmp`` paths, so two runs on one host clobbered each other (pass 8, for
  the owner), and its "did not build", "the known-false lemma compiled" and "failed for another reason" paths were
  covered by no test.

Each test named p9 fails at the pin."""
from __future__ import annotations

import importlib.util
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from tools.check_import_boundary import FORBIDDEN_MODULES, findings_for_module
from tools.mutation_report import rule_for

READING = '''def f(self, state, now):
    reading = self._raw_reading(now)
    detail = ""
    if reading.boot_id != state.boot_id:
        detail = "boot id changed"
    if detail:
        raise Refusal("clock_discontinuity", detail)
    return reading'''
ABORT = '''def f(self, intent_id, reason, now):
    record = AbortRecord(intent_id, reason, self._raw_reading(now))
    return record.to_payload()'''
ROTATE = '''def f(self, reading):
    self._rotate("discontinuity", reading)'''


@pytest.mark.parametrize("original, mutated", [
    (READING, READING.replace('detail = ""', 'detail = "XXXX"')),
    (ABORT, ABORT.replace("self._raw_reading(now))", "None)")),
    (ROTATE, ROTATE.replace('"discontinuity", reading)', '"discontinuity", None)')),
], ids=["detail", "abort reading", "rotation baseline"])
def test_p9_6_behaviour_is_never_classified_as_text(original: str, mutated: str) -> None:
    assert rule_for(original, mutated) is None


@pytest.mark.parametrize("mutated", [
    ABORT.replace("reason, self", '"XXabortXX", self'),
    ROTATE.replace('"discontinuity"', '"XXdiscontinuityXX"'),
], ids=["abort reason", "rotation reason"])
def test_the_reason_of_an_abort_and_a_rotation_stays_text(mutated: str) -> None:
    original = ABORT if "AbortRecord" in mutated else ROTATE
    if "XXabortXX" in mutated:
        original = original.replace("reason, self", '"aborted", self')
    assert rule_for(original, mutated) == ("text", "text argument of " + ("AbortRecord" if "Abort" in original
                                                                         else "self._rotate"))


# Standard-library modules whose source the boundary's rules flag but that are no network or process facility of
# their own, each with the reason. A module the rules flag that is neither forbidden nor listed fails the test below.
REVIEWED_STANDARD_LIBRARY: dict[str, str] = {
    "encodings": "imports _winapi on Windows only, for the code page of the console",
    "mimetypes": "urllib.parse splits a URL's path, and _winapi reads the Windows registry",
    "nturl2path": "urllib.parse quotes a path; no request is made",
    "pathlib": "urllib.parse quotes a file URI (Path.as_uri, Python 3.11); no request is made",
    "cgi": "urllib.parse parses a query string (Python 3.11); no request is made",
    "mailbox": "socket.gethostname names a maildir file; nothing is opened on the network",
    "shutil": "posix, nt and _winapi are used for file operations (sendfile, copy), never to spawn",
    "sysconfig": "imports _winapi on Windows only, for the install paths",
    "types": "_socket's type is listed among the built-in types; no socket is opened",
    "pdb": "imports pydoc for its help text; the debugger itself serves nothing and spawns nothing",
    "cgitb": "imports pydoc to render a traceback as HTML (Python 3.11); it serves nothing",
    "platform": "the documented indirect limit of the static check (it may spawn a process for a few queries)",
    "uuid": "the documented indirect limit of the static check (getnode may spawn a process); cpe uses uuid4 only",
}


def _flagged_standard_library() -> list[str]:
    root = Path("/boundary/cpe")
    flagged = []
    for name in sorted(sys.stdlib_module_names):
        if name.startswith("_") or name.split(".")[0] in FORBIDDEN_MODULES:
            continue
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, ValueError):
            continue
        if spec is None or spec.origin is None or not spec.origin.endswith(".py"):
            continue
        try:
            source = Path(spec.origin).read_text(encoding="utf-8", errors="replace")
            if findings_for_module(root / "m.py", source, root):
                flagged.append(name)
        except SyntaxError:
            continue
    return flagged


def test_p9_7_every_standard_library_module_the_rules_flag_is_forbidden_or_reviewed() -> None:
    unreviewed = [name for name in _flagged_standard_library() if name not in REVIEWED_STANDARD_LIBRARY]
    assert unreviewed == [], f"standard-library facilities neither forbidden nor reviewed: {unreviewed}"


@pytest.mark.parametrize("module", ["antigravity", "pipes", "mailcap"])
def test_p9_7_a_module_whose_own_interface_spawns_or_browses_is_forbidden(module: str, tmp_path: Path) -> None:
    package = tmp_path / "cpe"
    package.mkdir()
    findings = findings_for_module(package / "m.py", f"import {module}\n", package)
    assert len(findings) == 1 and "network or process facility" in findings[0]


# lean_check.sh with stub toolchain executables, as test_audit_pass1_others runs it: each stub prints what it is told.

def _stub(directory: Path, name: str, body: str) -> None:
    path = directory / name
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def _lean_check(tmp_path: Path, build: str, broken: str) -> subprocess.CompletedProcess[str]:
    """``build`` is the stub ``lake build``'s shell body, ``broken`` that of ``lake env lean`` on the false lemma."""
    tools = tmp_path / "bin"
    tools.mkdir()
    _stub(tools, "elan", "exit 0\n")
    _stub(tools, "lake", f'case "$1" in\n  exe) exit 0 ;;\n  build) {build} ;;\n  env) {broken} ;;\nesac\n')
    proofs = tmp_path / "repo" / "proofs"
    proofs.mkdir(parents=True)
    (proofs / "lean-toolchain").write_text("leanprover/lean4:v4.0.0\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "tools" / "lean_check.sh"
    environment = {**os.environ, "PATH": f"{tools}:{os.environ['PATH']}", "ELAN_HOME": str(tmp_path / "elan"),
                   "TMPDIR": str(tmp_path / "tmp")}
    (tmp_path / "tmp").mkdir()
    return subprocess.run(["sh", str(script)], cwd=tmp_path / "repo", env=environment, capture_output=True, text=True,
                          timeout=60)


FAILS_AS_REQUIRED = 'echo "error: linarith failed"; exit 1'


@pytest.mark.parametrize("build, broken, reported", [
    ("echo 'error: unknown identifier'; exit 1", FAILS_AS_REQUIRED, "the retained lemmas did not build"),
    ("exit 0", "exit 0", "the known-false lemma compiled"),
    ("exit 0", 'echo "error: unknown package"; exit 1', "the known-false lemma failed for another reason"),
], ids=["no build", "false lemma compiles", "false lemma fails otherwise"])
def test_every_failure_of_the_lean_job_is_not_verified(tmp_path: Path, build: str, broken: str, reported: str) -> None:
    result = _lean_check(tmp_path, build, broken)
    assert result.returncode == 1
    assert f"LEAN: NOT VERIFIED: {reported}" in result.stdout
    assert "LEAN: VERIFIED" not in result.stdout


def test_p9_8_the_lean_job_writes_no_fixed_path(tmp_path: Path) -> None:
    """Two runs on one host never share a log: each writes under its own temporary directory, removed at exit."""
    fixed = [Path("/tmp/lean_build.log"), Path("/tmp/broken.log")]
    before = {path: path.stat().st_mtime_ns if path.exists() else None for path in fixed}
    result = _lean_check(tmp_path, "exit 0", FAILS_AS_REQUIRED)
    assert result.returncode == 0 and "LEAN: VERIFIED" in result.stdout
    assert {path: path.stat().st_mtime_ns if path.exists() else None for path in fixed} == before
    assert list((tmp_path / "tmp").iterdir()) == []  # its own directory is removed at exit
