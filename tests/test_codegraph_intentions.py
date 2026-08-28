"""The task pack states CodeGraph *intentions*, never MCP tool names.

The pack already claims to carry "tool intentions, not shell commands", but it
named concrete MCP tools: `codegraph_callers`, `codegraph_impact` and
`codegraph_node`. The MCP surface varies by installed CodeGraph version -- 1.5.0
exposes a single tool, `codegraph_explore`, while the CLI still offers `callers`,
`callees`, `impact` and `node` as separate commands. So a pack naming MCP tools
can steer an agent toward calls it cannot make, and which names are "current"
depends on what the reader has installed.

Naming the intention and leaving transport to the consumer removes that class of
error rather than the three instances of it.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate-context-pack.py"

sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("generate_context_pack", GENERATOR)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

# Names of the generator's own symbols, which legitimately share the prefix.
OWN_SYMBOLS = {"codegraph_queries", "codegraph_section", "codegraph_symbols"}
TOOL_NAME = re.compile(r"codegraph_[a-z_]+")


def _tool_names(text: str) -> set[str]:
    return {m for m in TOOL_NAME.findall(text) if m not in OWN_SYMBOLS}


class CodegraphIntentionTests(unittest.TestCase):
    def _queries(self, task: str, **kwargs) -> list[str]:
        params = {
            "repo": "mq-agent",
            "relevant_repos": ["mq-agent"],
            "relevant_files": ["mq-agent/mq_agent/tools/context_pack.py"],
            "symbols": ["build_task_pack"],
            "mode": "on",
        }
        params.update(kwargs)
        return MODULE.build_codegraph_queries(task, **params)

    def test_emitted_guidance_names_no_mcp_tool(self) -> None:
        queries = self._queries("trace callers of build_task_pack")
        self.assertTrue(queries, "expected guidance for a source-heavy task")
        found = _tool_names("\n".join(queries))
        self.assertEqual(
            found,
            set(),
            f"guidance names MCP tools {sorted(found)}; the MCP surface varies by "
            "installed CodeGraph version, so state the intention instead",
        )

    def test_rendered_section_names_no_mcp_tool(self) -> None:
        section = MODULE.codegraph_section(self._queries("trace callers of build_task_pack"))
        found = _tool_names(section)
        self.assertEqual(found, set(), f"section names MCP tools {sorted(found)}")

    def test_intentions_are_still_distinct(self) -> None:
        # Dropping tool names must not flatten the guidance into one line.
        queries = self._queries("trace callers of build_task_pack")
        self.assertGreater(len(queries), 1)
        self.assertEqual(len(queries), len(set(queries)), "guidance repeated itself")

    def test_doc_intent_table_states_the_surface_is_version_dependent(self) -> None:
        doc = (ROOT / "docs" / "integrations" / "codegraph.md").read_text(encoding="utf-8")
        self.assertIn(
            "varies by installed version",
            doc,
            "the intent/tool table must say the MCP surface is version-dependent, "
            "or a reader will treat a stale row as a contract",
        )


if __name__ == "__main__":
    unittest.main()
