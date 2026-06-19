"""Single source of truth for `.mq/context` line budgets.

Both the per-repo context export generator and the token-budget checker read
these values, so each budget is defined in exactly one place. Changing a budget
here updates the rendered `token-budget.md` table and the checker together.
"""

from __future__ import annotations


# Line budget per generated `.mq/context` file.
CONTEXT_BUDGETS = {
    "repo-card.md": 60,
    "active-contract.md": 80,
    "current-blockers.md": 80,
    "integration-map.md": 120,
    "token-budget.md": 80,
    "task-pack.md": 200,
}

# Rows rendered into each repo's `token-budget.md`, in order. Excludes
# `token-budget.md` itself, which documents the others.
RENDERED_BUDGET_ORDER = [
    "repo-card.md",
    "active-contract.md",
    "current-blockers.md",
    "integration-map.md",
    "task-pack.md",
]

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
