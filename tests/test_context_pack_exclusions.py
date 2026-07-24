"""Focused tests for the structured exclusions layer of generate-context-pack.py.

Remaining work A (v0.3.0): the generator must emit the same structured
`## Exclusions` proof (kind `forbidden|fallback|irrelevant` + reason) that the
schema, template, example, and the mq-agent mirror already use — not just a flat
`## Do not read first` list. Stdlib unittest only, so it runs in public-safe CI
with `python3 -m unittest`.
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


class MergeExclusions(unittest.TestCase):
    def test_structured_entry_keeps_kind_and_reason(self):
        merged = gcp.merge_exclusions(
            [{"item": "mq-ums", "kind": "forbidden", "reason": "unrelated repo"}]
        )
        self.assertEqual(
            merged, [{"item": "mq-ums", "kind": "forbidden", "reason": "unrelated repo"}]
        )

    def test_severity_ordering(self):
        merged = gcp.merge_exclusions(
            [
                {"item": "c", "kind": "irrelevant", "reason": ""},
                {"item": "b", "kind": "fallback", "reason": ""},
                {"item": "a", "kind": "forbidden", "reason": ""},
            ]
        )
        self.assertEqual([e["kind"] for e in merged], ["forbidden", "fallback", "irrelevant"])

    def test_legacy_string_folds_in_as_irrelevant(self):
        merged = gcp.merge_exclusions(["full README"])
        self.assertEqual(merged, [{"item": "full README", "kind": "irrelevant", "reason": ""}])

    def test_unknown_kind_degrades_to_irrelevant(self):
        merged = gcp.merge_exclusions([{"item": "x", "kind": "bogus"}])
        self.assertEqual(merged[0]["kind"], "irrelevant")

    def test_dedupe_by_kind_and_item_first_reason_wins(self):
        merged = gcp.merge_exclusions(
            [
                {"item": "x", "kind": "forbidden", "reason": "first"},
                {"item": "x", "kind": "forbidden", "reason": "second"},
            ]
        )
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["reason"], "first")

    def test_empty_or_blank_dropped(self):
        self.assertEqual(gcp.merge_exclusions(["", "   ", {"item": ""}]), [])


class ParseExcludeArg(unittest.TestCase):
    def test_kind_item_reason(self):
        self.assertEqual(
            gcp.parse_exclude_arg("forbidden:mq-ums:unrelated repo"),
            {"kind": "forbidden", "item": "mq-ums", "reason": "unrelated repo"},
        )

    def test_kind_item_without_reason(self):
        self.assertEqual(
            gcp.parse_exclude_arg("fallback:old notes"),
            {"kind": "fallback", "item": "old notes", "reason": ""},
        )

    def test_bare_string_is_item(self):
        # No leading known kind -> treat the whole value as a bare item.
        self.assertEqual(gcp.parse_exclude_arg("full README"), "full README")

    def test_colon_in_non_kind_head_stays_bare(self):
        self.assertEqual(gcp.parse_exclude_arg("note: keep it"), "note: keep it")


class RenderExclusions(unittest.TestCase):
    def _render(self, **kw):
        base = dict(
            task="t",
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
        base.update(kw)
        return gcp.render_pack(**base)

    def test_emits_exclusions_heading_not_do_not_read(self):
        content = self._render(exclusions=[{"item": "mq-ums", "kind": "forbidden", "reason": "unrelated"}])
        self.assertIn("## Exclusions", content)
        self.assertNotIn("## Do not read first", content)
        self.assertIn("* `forbidden` — mq-ums: unrelated", content)

    def test_legacy_do_not_read_renders_as_irrelevant(self):
        content = self._render(do_not_read=["full README"])
        self.assertIn("* `irrelevant` — full README", content)

    def test_empty_shows_fallback_line(self):
        content = self._render()
        self.assertIn("## Exclusions", content)
        self.assertIn("Broad repo scans unless the pack proves insufficient", content)


if __name__ == "__main__":
    unittest.main()
