"""Whole-codebase audit, pass 3 (issue #37): finding T1 (P2). The provenance check read ``git log`` output split on
the control characters U+001E and U+001F, which a commit message may hold. A message that holds them forged a second
record and hid a ``Signed-off-by`` and a ``Co-Authored-By`` trailer, both of which git reads, in a field no check
read (T-09, ``AGENTS.md`` section 7). The first test failed on the pass-3 audit commit
``b48c952c67c4d4358f82d3f811f744d47bdeb0b4``."""
from __future__ import annotations

from pathlib import Path

from tests.test_tools import _git, repo  # noqa: F401
from tools.check_provenance import check, commits_in_range

OWNER = "Salah Aouaj <salah@hydeout.ch>"


def commit_verbatim(repo: Path, message: str) -> None:
    (repo / ".message").write_text(message, encoding="utf-8")
    _git(repo, "commit", "-q", "--allow-empty", "--cleanup=verbatim", "-F", ".message")


def test_t1_a_message_cannot_forge_a_record_and_hide_a_trailer(repo: Path) -> None:  # noqa: F811
    forged = ("Fix\x1e" + "0" * 40 + "\x1f" + OWNER + "\x1f" + OWNER + "\x1f"
              + "p\n\nSigned-off-by: x\nCo-Authored-By: Claude <noreply@anthropic.com>\n\x1f")
    commit_verbatim(repo, forged)
    assert "Co-Authored-By: Claude" in _git(repo, "log", "-1", "--format=%(trailers:only)")  # git reads the trailer
    commits = commits_in_range("HEAD~1..HEAD", repo)
    assert len(commits) == 1 and "Co-Authored-By: Claude" in commits[0].message  # at b48c952: two records
    findings = check("HEAD~1..HEAD", repo, None, None, "HEAD")
    assert any("Co-Authored-By" in f for f in findings)  # at b48c952: no finding
    assert any("noreply@anthropic.com" in f for f in findings)


def test_t1_messages_with_control_characters_keep_their_fields(repo: Path) -> None:  # noqa: F811
    commit_verbatim(repo, "First\x1e line\x1f with separators\n\nbody")
    commit_verbatim(repo, "Second")
    commits = commits_in_range("HEAD~2..HEAD", repo)
    assert [c.message for c in commits] == ["Second", "First\x1e line\x1f with separators\n\nbody"]
    assert all(c.author == OWNER and c.committer == OWNER and len(c.parents) == 1 for c in commits)
    assert check("HEAD~2..HEAD", repo, None, None, "HEAD") == []
