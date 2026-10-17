"""Network-free provenance checks for optional Graphify development tooling."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.check_graphify_snapshot import assess

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_graphify_snapshot.py"
SHA = "a" * 40
OTHER_SHA = "b" * 40
REPO_ID = "fd5eb8a0-cc46-48ff-8f82-cba4898857d1"


class GraphifySnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.response = {
            "repositoryId": REPO_ID,
            "commitSha": SHA,
            "result": {"freshness": {"commit": SHA[:8]}},
        }

    def test_matching_commit_is_provenance_only(self) -> None:
        self.assertEqual(assess(self.response, SHA, REPO_ID), (True, "EXACT_INDEX_SHA_MATCH"))

    def test_stale_index_fails_closed(self) -> None:
        self.assertEqual(assess(self.response, OTHER_SHA, REPO_ID), (False, "STALE_INDEX"))

    def test_wrong_repository_fails_closed(self) -> None:
        self.assertEqual(assess(self.response, SHA, "another-workspace-repo"), (False, "REPOSITORY_MISMATCH"))

    def test_truncated_index_sha_fails_closed(self) -> None:
        self.response["commitSha"] = SHA[:8]
        self.assertEqual(assess(self.response, SHA, REPO_ID), (False, "MISSING_OR_INVALID_INDEX_SHA"))

    def test_missing_index_sha_fails_closed(self) -> None:
        del self.response["commitSha"]
        self.assertEqual(assess(self.response, SHA, REPO_ID), (False, "MISSING_OR_INVALID_INDEX_SHA"))

    def test_invalid_expected_sha_fails_closed(self) -> None:
        self.assertEqual(assess(self.response, SHA[:8], REPO_ID), (False, "INVALID_EXPECTED_SHA"))

    def test_invalid_response_fails_closed(self) -> None:
        self.assertEqual(assess([], SHA, REPO_ID), (False, "INVALID_RESPONSE"))

    def test_cli_success_and_stale_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "graphify.json"
            file.write_text(json.dumps(self.response), encoding="utf-8")
            base = [sys.executable, str(SCRIPT), "--response", str(file), "--repository-id", REPO_ID, "--expected-sha"]
            good = subprocess.run([*base, SHA], capture_output=True, text=True, check=False)
            stale = subprocess.run([*base, OTHER_SHA], capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("GRAPHIFY_EXACT_INDEX_SHA_MATCH", good.stdout)
            self.assertEqual(stale.returncode, 2, stale.stderr)
            self.assertIn("GRAPHIFY_STALE_INDEX", stale.stdout)

    def test_invalid_json_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "bad.json"
            file.write_text("{", encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--response", str(file), "--repository-id", REPO_ID, "--expected-sha", SHA],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(run.returncode, 2)


if __name__ == "__main__":
    unittest.main()
