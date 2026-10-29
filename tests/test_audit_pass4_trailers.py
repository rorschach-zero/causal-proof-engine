"""Whole-codebase audit, pass 4 (issue #37): finding T2 (P2). The provenance check recognised a trailer block only
when every line of the last paragraph was ``Key: value``. Git also reads a block that holds a ``#`` comment line,
and a mixed block led by a line git generates such as ``(cherry picked from commit ...)``. A trailer in either
passed with no finding (T-09, ``AGENTS.md`` section 7). The check now takes the trailers git reads. The three cases of
the first test failed on the pass-4 commit ``c3d6233dbaeb71eb71cb128394099b23cef285b5``."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_audit_pass3_provenance import commit_verbatim
from tests.test_tools import _git, repo  # noqa: F401
from tools.check_provenance import check


@pytest.mark.parametrize("message", [
    "Fix\n\nAssisted: Claude\n# a comment line, which git skips in a trailer block\n",
    "Fix\n\n(cherry picked from commit 0123456789abcdef0123456789abcdef01234567)\nsome free text\nAssisted: Claude\n",
    "Fix\n\nSigned-off-by: Salah Aouaj <salah@hydeout.ch>\nsome free text\nAssisted: Claude\n",
])
def test_t2_every_trailer_git_reads_is_found(repo: Path, message: str) -> None:  # noqa: F811
    commit_verbatim(repo, message)
    assert "Assisted: Claude" in _git(repo, "log", "-1", "--format=%(trailers:only,unfold)")  # git reads it
    findings = check("HEAD~1..HEAD", repo, None, None, "HEAD")
    assert any("'Assisted'" in f for f in findings)  # at c3d6233: no finding for 'Assisted'


@pytest.mark.parametrize("message", [
    "Fix\n\nReviewed-by: Salah Aouaj <salah@hydeout.ch>\n",
    "Fix\n\nsome free text\nAssisted: Claude\n",  # a mixed block without a git-generated line: git reads no trailer
    "Fix the parser\n\nThe parser reads Key: value lines.\n",
])
def test_t2_what_git_does_not_read_as_a_trailer_is_not_one(repo: Path, message: str) -> None:  # noqa: F811
    commit_verbatim(repo, message)
    assert _git(repo, "log", "-1", "--format=%(trailers:only,unfold)").strip() in ("", "Reviewed-by: Salah Aouaj <salah@hydeout.ch>")
    assert check("HEAD~1..HEAD", repo, None, None, "HEAD") == []
