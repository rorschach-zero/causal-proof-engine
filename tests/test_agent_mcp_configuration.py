"""Offline checks for safe, vendor-neutral Graphify MCP onboarding."""
from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path
from typing import Any

from scripts.check_mcp_config import credential_paths, scan_file

ROOT = Path(__file__).resolve().parents[1]
GRAPHIFY_URL = "https://api.graphify.com/mcp"
ALLOWED = {
    "list_repositories", "list_workspaces", "graph_stats", "query_graph",
    "graphify_find", "graphify_node", "graphify_rank_files",
    "graphify_callers", "graphify_callees", "graphify_trace",
    "shortest_path", "graphify_impact", "impact_and_risk",
    "graphify_tests_for", "graphify_file_neighbors",
    "graphify_imports_exports", "graphify_references",
    "graphify_expand", "graphify_render_subgraph",
    "search", "fetch", "recall", "memories_about",
}


class AgentMcpConfigurationTests(unittest.TestCase):
    claude: dict[str, Any]
    codex: dict[str, Any]
    gemini: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.claude = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
        cls.codex = tomllib.loads((ROOT / ".codex/config.toml").read_text(encoding="utf-8"))
        cls.gemini = json.loads((ROOT / ".gemini/settings.json").read_text(encoding="utf-8"))

    def test_claude_project_mcp_endpoint(self) -> None:
        server = self.claude["mcpServers"]["graphify"]
        self.assertEqual(server, {"type": "http", "url": GRAPHIFY_URL})

    def test_codex_project_mcp_endpoint(self) -> None:
        server = self.codex["mcp_servers"]["graphify"]
        self.assertEqual(server["url"], GRAPHIFY_URL)
        self.assertTrue(server["enabled"])
        self.assertFalse(server["required"])
        self.assertEqual(server["default_tools_approval_mode"], "writes")

    def test_gemini_project_mcp_endpoint(self) -> None:
        server = self.gemini["mcpServers"]["graphify"]
        self.assertEqual(server["httpUrl"], GRAPHIFY_URL)
        self.assertFalse(server["trust"])

    def test_read_oriented_tools_only_in_codex_gemini(self) -> None:
        codex = set(self.codex["mcp_servers"]["graphify"]["enabled_tools"])
        gemini = set(self.gemini["mcpServers"]["graphify"]["includeTools"])
        self.assertEqual(codex, ALLOWED)
        self.assertEqual(gemini, ALLOWED)
        self.assertNotIn("remember", codex)
        self.assertNotIn("set_workspace", codex)

    def test_no_embedded_secret_or_broker_endpoint(self) -> None:
        for relative in (".mcp.json", ".codex/config.toml", ".gemini/settings.json"):
            with self.subTest(config=relative):
                ok, findings = scan_file(ROOT / relative)
                self.assertTrue(ok, findings)

    def test_parsed_credential_keys_rejected(self) -> None:
        for example in (
            {"headers": {"X-Api-Key": "test-value"}},
            {"headers": {"Authorization": "Basic dummy"}},
            {"mcp": {"access_token": "test-value"}},
            {"mcp": {"clientSecret": "test-value"}},
            {"mcp": {"PASSWORD": "test-value"}},
            {"mcp": [{"RefreshToken": "test-value"}]},
            {"mcp": {"key": "test-value"}},
        ):
            with self.subTest(example=list(example)):
                self.assertTrue(credential_paths(example))

    def test_embedded_auth_header_values_rejected_without_leaking(self) -> None:
        literal = "Bearer test-secret-do-not-print"
        findings = credential_paths({"custom": literal})
        self.assertEqual(findings, ["$.custom"])
        self.assertNotIn(literal, str(findings))

    def test_benign_configuration_fields_are_allowed(self) -> None:
        example = {
            "mcpServers": {
                "graphify": {
                    "type": "http",
                    "url": GRAPHIFY_URL,
                    "enabled_tools": ["graph_stats", "query_graph"],
                }
            }
        }
        self.assertEqual(credential_paths(example), [])

    def test_malformed_config_fails_closed(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text("{", encoding="utf-8")
            ok, findings = scan_file(path)
            self.assertFalse(ok)
            self.assertTrue(findings)

    def test_all_agent_entrypoints_preserve_canonical_policy(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        gemini = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
        self.assertIn("## 13. Graphify", agents)
        self.assertIn("AGENTS.md", claude)
        self.assertIn("AGENTS.md", gemini)
        self.assertIn("docs/runbooks/agent-mcp-onboarding.md", agents)


if __name__ == "__main__":
    unittest.main()
