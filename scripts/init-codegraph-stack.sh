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
  echo "codegraph not found on PATH"
  echo "Install with:"
  echo "curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh"
  exit 1
fi

for repo in "${repos[@]}"; do
  if [ -d "$repo/.git" ]; then
    echo "==> CodeGraph init: $repo"
    cd "$repo"
    codegraph init

    if [ -f ".gitignore" ]; then
      grep -qxF ".codegraph/" .gitignore || echo ".codegraph/" >> .gitignore
    else
      echo ".codegraph/" > .gitignore
    fi
  else
    echo "Skipping missing repo: $repo"
  fi
done

echo "Done. Verify with: codegraph status"
