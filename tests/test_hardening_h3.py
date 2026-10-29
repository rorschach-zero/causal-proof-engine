"""Hardening pass H3 (CI tools): the findings of Codex's review of PR #22 that the owner's delegate decided to fix on
2026-10-21. Each test fails at 2122567 and passes after the fix."""
from __future__ import annotations

from pathlib import Path

from tools import check_import_boundary
from tools.check_provenance import text_findings, trailer_findings


def package_with(tmp_path: Path, files: dict[str, str]) -> Path:
    package = tmp_path / "cpe"
    package.mkdir()
    (package / "__init__.py").write_text("")
    for name, source in files.items():
        (package / name).write_text(source)
    return package


def test_4330035947_an_unaliased_dotted_import_of_os_binds_os(tmp_path: Path) -> None:
    package = package_with(tmp_path, {"dotted.py": "import os.path\nos.system('x')\n",
                                      "aliased.py": "import os.path as p\np.join('a')\n"})
    findings = check_import_boundary.check_package(package)
    assert any("dotted.py" in f and "os.system" in f for f in findings)
    assert not any("aliased.py" in f for f in findings)


def test_4330035940_only_an_absolute_star_import_of_os_itself_is_a_finding(tmp_path: Path) -> None:
    package = package_with(tmp_path, {"os.py": "", "path_star.py": "from os.path import *\n",
                                      "relative_star.py": "from .os import *\n", "os_star.py": "from os import *\n"})
    findings = check_import_boundary.check_package(package)
    assert not any("path_star.py" in f or "relative_star.py" in f for f in findings)
    assert any("os_star.py" in f for f in findings)


def test_4330035931_every_git_trailer_but_reviewed_by_is_a_finding() -> None:
    for message in ("Fix\n\nTested: Bob", "Fix\n\nAcked: Carol <c@example.org>", "Fix\n\nRefs: #3\nTested: Bob"):
        assert trailer_findings(message, "commit") != []
    assert trailer_findings("Fix\n\nReviewed-by: Salah Aouaj <salah@hydeout.ch>", "commit") == []
    assert trailer_findings("Fix\n\nThe body explains: why the change is needed.\nIt has prose lines.", "commit") == []
    assert text_findings("Fix\n\nReviewed-by: Salah Aouaj <salah@hydeout.ch>", "commit") == []
