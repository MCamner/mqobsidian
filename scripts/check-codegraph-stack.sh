#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   check-codegraph-stack.sh              human-readable status report (default)
#   check-codegraph-stack.sh --coverage   public-safe stack-coverage JSON on stdout
#
# The --coverage mode reports, per MQ repo, what CodeGraph actually indexed and
# which command surfaces (shell / PowerShell) it does NOT support — so a green
# index status cannot silently hide unsupported command surfaces. Output is
# public-safe: repo basenames only, no machine paths and no `.codegraph/` DB
# paths. See docs/integrations/codegraph.md and Roadmap "CodeGraph MQ
# Integration → Delivery A".

repos=(
  "$HOME/mqobsidian"
  "$HOME/mq-agent"
  "$HOME/mq-mcp"
  "$HOME/mq-hal"
  "$HOME/repo-signal"
  "$HOME/mq-ums"
  "$HOME/mq-image-analyze"
  "$HOME/macos-scripts"
)

if ! command -v codegraph >/dev/null 2>&1; then
  echo "FAIL: codegraph not found on PATH" >&2
  exit 1
fi

coverage_json() {
  # Assemble the public-safe coverage view in python3 (guaranteed on macOS/Linux
  # here and already a dependency of the other check scripts). Bash builds the
  # repo list; python runs `codegraph status --json`, counts unsupported command
  # files on disk, and emits sanitized JSON.
  CODEGRAPH_VERSION="$(codegraph version 2>/dev/null | head -1 | tr -d '[:space:]')" \
  MQ_REPOS="${repos[*]}" \
  python3 - <<'PY'
import json
import os
import subprocess

# CodeGraph 1.0.x extracts these; everything else on disk is an unsupported
# surface. Shell and PowerShell are the MQ-relevant command surfaces missing
# upstream (see docs/integrations/codegraph.md → "Coverage and unsupported
# surfaces").
UNSUPPORTED = {
    "shell": {".sh", ".bash", ".zsh", ".fish"},
    "powershell": {".ps1", ".psm1", ".psd1"},
}
SKIP_DIRS = {".git", "node_modules", ".codegraph", ".venv", "__pycache__"}


def count_by_ext(root):
    counts = {kind: 0 for kind in UNSUPPORTED}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            for kind, exts in UNSUPPORTED.items():
                if ext in exts:
                    counts[kind] += 1
    return counts


def status_json(path):
    try:
        out = subprocess.run(
            ["codegraph", "status", "--json"],
            cwd=path, capture_output=True, text=True, timeout=60,
        )
    except Exception:
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


repos = [p for p in os.environ.get("MQ_REPOS", "").split() if p]
entries = []
for path in repos:
    name = os.path.basename(path.rstrip("/"))
    if not os.path.isdir(os.path.join(path, ".git")):
        entries.append({"repo": name, "indexed": False, "reason": "repo not present locally"})
        continue

    st = status_json(path)
    surface_counts = count_by_ext(path)
    unsupported = [
        {"kind": kind, "files_on_disk": surface_counts[kind], "indexed": False}
        for kind in UNSUPPORTED
    ]

    if st is None:
        entries.append({
            "repo": name,
            "indexed": False,
            "reason": ".codegraph/ missing or status unavailable",
            "unsupported_source": unsupported,
        })
        continue

    idx = st.get("index", {}) or {}
    has_unsupported = any(u["files_on_disk"] > 0 for u in unsupported)
    if has_unsupported:
        parts = [f"{u['files_on_disk']} {u['kind']}" for u in unsupported if u["files_on_disk"]]
        note = "green index omits unsupported command surfaces: " + ", ".join(parts)
        coverage = "partial"
    else:
        note = "no unsupported command surfaces detected on disk"
        coverage = "full"

    entries.append({
        "repo": name,
        "indexed": bool(st.get("initialized", True)),
        "last_indexed": st.get("lastIndexed"),
        "index_up_to_date": not idx.get("reindexRecommended", False),
        "counts": {
            "files": st.get("fileCount"),
            "nodes": st.get("nodeCount"),
            "edges": st.get("edgeCount"),
        },
        "indexed_languages": st.get("languages", []),
        "unsupported_source": unsupported,
        "coverage_status": coverage,
        "coverage_note": note,
    })

doc = {
    "schema": "codegraph-stack-coverage.v1",
    "generated_by": "scripts/check-codegraph-stack.sh --coverage",
    "codegraph_version": os.environ.get("CODEGRAPH_VERSION") or None,
    "note": (
        "Public-safe coverage view. CodeGraph indexes only supported source "
        "languages; shell and PowerShell command surfaces are unsupported "
        "upstream and reported here so a green index cannot hide them."
    ),
    "repos": entries,
}
print(json.dumps(doc, indent=2))
PY
}

if [ "${1:-}" = "--coverage" ]; then
  coverage_json
  exit 0
fi

echo "CodeGraph version:"
codegraph version

for repo in "${repos[@]}"; do
  if [ -d "$repo/.git" ]; then
    echo
    echo "==> Checking $repo"
    cd "$repo"

    if [ ! -d ".codegraph" ]; then
      echo "WARN: .codegraph/ missing"
      continue
    fi

    if ! grep -qxF ".codegraph/" .gitignore 2>/dev/null; then
      echo "WARN: .codegraph/ missing from .gitignore"
    fi

    codegraph status || echo "WARN: codegraph status failed in $repo"
  else
    echo "Skipping missing repo: $repo"
  fi
done
