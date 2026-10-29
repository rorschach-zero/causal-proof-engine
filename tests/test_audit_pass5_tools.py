"""Whole-codebase audit, pass 5 (issue #37), at ``b34c7212ca688d72611c3fd09b4eba170f94b44b``: the tools.

- T3 (P2): the pull request title check matched ``Token: value`` with a leading letter and a non-empty value, while
  git also reads ``Fix:`` and ``1Fix: y`` as trailers of the merge commit GitHub writes from the title. Such a
  title passed the pull request text check and failed T-09 on ``main`` after the merge (the incident of issue #37
  comment 6500990530). The title is now read by git itself, as the post-merge check reads the merge commit.
- B1 (P2): the import boundary did not name ``posix``, the module beneath ``os``: ``posix.system`` spawned a process
  with no finding. The modules beneath ``os``, ``subprocess`` and ``socket`` are now forbidden too.

Every test but the two "stays clean" tests failed on the pass-5 commit."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import check_import_boundary, check_provenance

OWNER = ("-c", "user.name=Salah Aouaj", "-c", "user.email=salah@hydeout.ch")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, *OWNER, "commit", "-q", "--allow-empty", "-m", "Base")
    return tmp_path


@pytest.mark.parametrize("title", ["Fix:", "1Fix: y"])
def test_t3_a_title_git_reads_as_a_trailer_is_refused_before_the_merge(repo: Path, title: str) -> None:
    _git(repo, *OWNER, "commit", "-q", "--allow-empty", "-m", f"Merge pull request #1 from a/b\n\n{title}")
    assert check_provenance.check("HEAD~1..HEAD", repo, None, None, "HEAD"), "refused after the merge"
    assert check_provenance.check("HEAD~1..HEAD~1", repo, title, "", "HEAD"), "so refused before it"


@pytest.mark.parametrize("title", ["Refuse a pull request title that becomes a Git trailer in the merge commit",
                                   "Audit pass 4, #63 review finding 4414429445: a larger anchor settles"])
def test_t3_a_title_git_reads_as_no_trailer_stays_clean(repo: Path, title: str) -> None:
    assert check_provenance.check("HEAD..HEAD", repo, title, "", "HEAD") == []


def _package(tmp_path: Path, source: str) -> Path:
    package = tmp_path / "cpe"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "m.py").write_text(source)
    return package


@pytest.mark.parametrize("source", ["import posix\nposix.system('true')\n", "from posix import fork\n",
                                    "import _posixsubprocess\n", "import _socket\n", "import nt\n"])
def test_b1_the_modules_beneath_os_subprocess_and_socket_are_forbidden(tmp_path: Path, source: str) -> None:
    assert check_import_boundary.check_package(_package(tmp_path, source))


def test_b1_the_package_itself_stays_clean() -> None:
    package = Path(__file__).resolve().parent.parent / "cpe"  # whatever the working directory (issue #37, pass 7)
    assert list(package.glob("*.py")) and check_import_boundary.check_package(package) == []
