"""Focused tests for the CodeGraph query layer of generate-context-pack.py.

Delivery C (CodeGraph MQ Integration): the generator must emit concrete,
bounded, copy-pasteable CodeGraph queries for source-heavy tasks and no
CodeGraph noise for documentation tasks. Stdlib unittest only — no pytest
dependency — so it runs in the public-safe CI with `python3 -m unittest`.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-context-pack.py"

_spec = importlib.util.spec_from_file_location("generate_context_pack", SCRIPT)
assert _spec and _spec.loader
gcp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gcp)


class BuildCodegraphQueries(unittest.TestCase):
    def test_source_heavy_task_emits_bounded_scoped_queries(self):
        queries = gcp.build_codegraph_queries(
            task="trace callers of store_learn_record",
            repo="mq-mcp",
            relevant_repos=[],
            relevant_files=["mq-mcp/runtime/memory/obsidian_writer.py"],
            symbols=["store_learn_record"],
            mode="auto",
        )
        self.assertTrue(queries)
        self.assertLessEqual(len(queries), gcp.MAX_CODEGRAPH_QUERIES)
        # every query passes an explicit project path
        self.assertTrue(all(" -p mq-mcp" in q for q in queries))
        self.assertTrue(queries[0].startswith('codegraph explore "trace callers of store_learn_record"'))
        self.assertIn("codegraph callers store_learn_record -p mq-mcp -l 20", queries)
        self.assertIn("codegraph impact store_learn_record -p mq-mcp -d 2", queries)
        # source file -> repo-relative node query (leading repo prefix stripped)
        self.assertIn("codegraph node runtime/memory/obsidian_writer.py -p mq-mcp", queries)

    def test_doc_task_emits_no_queries(self):
        queries = gcp.build_codegraph_queries(
            task="update mq-mcp README and changelog",
            repo="mq-mcp",
            relevant_repos=[],
            relevant_files=[],
            symbols=[],
            mode="auto",
        )
        self.assertEqual(queries, [])

    def test_off_mode_suppresses_queries(self):
        queries = gcp.build_codegraph_queries(
            task="trace callers of render_pack",
            repo="mqobsidian",
            relevant_repos=[],
            relevant_files=[],
            symbols=[],
            mode="off",
        )
        self.assertEqual(queries, [])

    def test_no_target_repo_emits_no_queries(self):
        queries = gcp.build_codegraph_queries(
            task="trace callers of something",
            repo=None,
            relevant_repos=[],
            relevant_files=[],
            symbols=[],
            mode="on",
        )
        self.assertEqual(queries, [])

    def test_query_count_is_capped(self):
        queries = gcp.build_codegraph_queries(
            task="refactor mq-mcp",
            repo="mq-mcp",
            relevant_repos=[],
            relevant_files=[f"mq-mcp/mod_{i}.py" for i in range(10)],
            symbols=[f"sym_{i}" for i in range(10)],
            mode="on",
        )
        self.assertEqual(len(queries), gcp.MAX_CODEGRAPH_QUERIES)


class RenderSection(unittest.TestCase):
    def test_section_present_for_source_task(self):
        content = gcp.render_pack(
            task="fix mq-mcp brain writer paths",
            target="both",
            repo="mq-mcp",
            summary="s",
            relevant_repos=["mq-mcp"],
            relevant_files=[],
            relevant_decisions=[],
            notes=[],
            do_not_read=[],
            codegraph_queries=["codegraph explore \"x\" -p mq-mcp --max-files 8"],
        )
        self.assertIn("## CodeGraph queries", content)
        self.assertIn("```bash", content)
        self.assertIn("CodeGraph never replaces source tests or CLI verification", content)

    def test_no_section_when_no_queries(self):
        content = gcp.render_pack(
            task="update README",
            target="both",
            repo="mq-mcp",
            summary="s",
            relevant_repos=["mq-mcp"],
            relevant_files=[],
            relevant_decisions=[],
            notes=[],
            do_not_read=[],
            codegraph_queries=[],
        )
        self.assertNotIn("## CodeGraph queries", content)
        self.assertNotIn("codegraph", content.lower())


if __name__ == "__main__":
    unittest.main()
