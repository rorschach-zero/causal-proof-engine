"""Synthetic, network-free checks for the privileged review-dispatch workflow.

Run: python -m unittest discover -s tests -p test_review_dispatch.py
"""
from __future__ import annotations

import io
import json
import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

REPOSITORY = "rorschach-zero/causal-proof-engine"
COMMIT = "a" * 40
WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/claude-on-codex-review.yml"


def dispatcher_code() -> str:
    contents = WORKFLOW.read_text(encoding="utf-8")
    assert "  issue_comment:\n    types: [edited]" in contents
    assert "  pull_request_review:" not in contents
    marker = "          python - <<'PY'\n"
    return textwrap.dedent(contents.split(marker, 1)[1].split("\n          PY", 1)[0])


class MockResponse(io.BytesIO):
    status = 200

    def __enter__(self) -> "MockResponse":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class ReviewDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = compile(dispatcher_code(), str(WORKFLOW), "exec")

    def invoke(
        self, *, status: str = "completed", findings: bool = True,
        branch: str = "claude/fix", reviewed_sha: str = COMMIT,
        token: str = "synthetic-token"
    ) -> tuple[list[str], int]:
        state = {
            "code_review": {"commit_sha": reviewed_sha,
                            "status": status,
                            "has_unresolved_findings": findings}
        }
        event = {
            "issue": {"number": 4},
            "comment": {
                "id": 123,
                "body": "<!-- codex-pull-request-review-summary -->\n"
                        "<!-- codex-review-state:v1 "
                        + json.dumps(state, separators=(",", ":")) + " -->",
            },
        }
        pr = {"state": "open", "head": {
            "repo": {"full_name": REPOSITORY}, "ref": branch, "sha": COMMIT}}
        urls: list[str] = []

        def fake_urlopen(request: object, timeout: int) -> MockResponse:
            url = request.full_url  # type: ignore[attr-defined]
            urls.append(url)
            return MockResponse(json.dumps(pr if "api.github.com" in url else
                                           {"type": "routine_fire"}).encode())

        with tempfile.TemporaryDirectory() as root:
            event_path = Path(root) / "event.json"
            event_path.write_text(json.dumps(event))
            environment = {
                "GITHUB_EVENT_PATH": str(event_path),
                "GITHUB_REPOSITORY": REPOSITORY,
                "GH_TOKEN": "synthetic-github",
                "ROUTINE_URL": "https://api.anthropic.com/v1/claude_code/routines/trig_TEST/fire",
                "ROUTINE_TOKEN": token,
            }
            with patch.dict(os.environ, environment), patch("urllib.request.urlopen", fake_urlopen):
                try:
                    exec(self.code, {})
                except SystemExit as exc:
                    return urls, exc.code if isinstance(exc.code, int) else 1
        return urls, 0

    def test_valid_review_dispatches(self) -> None:
        urls, code = self.invoke()
        self.assertEqual(code, 0)
        self.assertEqual(len(urls), 2)
        self.assertTrue(urls[1].startswith("https://api.anthropic.com/"))

    def test_in_progress_review_not_dispatched(self) -> None:
        urls, code = self.invoke(status="running")
        self.assertEqual((urls, code), ([], 0))

    def test_review_without_findings_not_dispatched(self) -> None:
        urls, code = self.invoke(findings=False)
        self.assertEqual((urls, code), ([], 0))

    def test_stale_review_not_dispatched(self) -> None:
        urls, code = self.invoke(reviewed_sha="b" * 40)
        self.assertEqual((len(urls), code), (1, 0))

    def test_unrelated_branch_not_dispatched(self) -> None:
        urls, code = self.invoke(branch="automation/change")
        self.assertEqual((len(urls), code), (1, 0))

    def test_absent_routine_token_fails_closed(self) -> None:
        urls, code = self.invoke(token="")
        self.assertEqual(len(urls), 1)
        self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
