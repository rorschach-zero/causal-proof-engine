"""Offline checks for safe, vendor-neutral Graphify MCP onboarding."""
from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path

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
        configs = [
            ROOT / ".mcp.json",
            ROOT / ".codex/config.toml",
            ROOT / ".gemini/settings.json",
        ]
        for path in configs:
            data = path.read_text(encoding="utf-8").lower()
            for forbidden in ["api_key", "client_secret", "bearer ", "saxobank.com", "gateway.saxobank", "token ="]:
                with self.subTest(path=path, forbidden=forbidden):
                    self.assertNotIn(forbidden, data)

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
