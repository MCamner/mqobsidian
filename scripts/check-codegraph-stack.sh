#!/usr/bin/env bash
set -euo pipefail

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
  echo "FAIL: codegraph not found on PATH"
  exit 1
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
