"""Single source of truth for `.mq/context` line budgets.

The budgets and their rendered order live in the published, cross-repo contract
`.mq/context-budgets.json` (owned by mqobsidian, also consumed by mq-agent). This
module loads that contract so the generator and the checker derive each budget
from exactly one place. See `docs/context-export-contract.md`.
"""

from __future__ import annotations

import json
from pathlib import Path


_CONTRACT = Path(__file__).resolve().parents[1] / ".mq" / "context-budgets.json"
_DATA = json.loads(_CONTRACT.read_text(encoding="utf-8"))

# Line budget per generated `.mq/context` file.
CONTEXT_BUDGETS = _DATA["budgets"]

# Rows rendered into each repo's `token-budget.md`, in order. Excludes
# `token-budget.md` itself, which documents the others.
RENDERED_BUDGET_ORDER = _DATA["rendered_order"]

# Files present in a live repo's `.mq/context` (task-pack is generated per task,
# token-budget.md is not separately budget-checked there).
LOCAL_CONTEXT_FILES = [
    "repo-card.md",
    "active-contract.md",
    "current-blockers.md",
    "integration-map.md",
    "task-pack.md",
]

# Files written by generate-repo-context-export.py into examples/.
EXPORTED_CONTEXT_FILES = [
    "repo-card.md",
    "active-contract.md",
    "current-blockers.md",
    "integration-map.md",
    "token-budget.md",
]
