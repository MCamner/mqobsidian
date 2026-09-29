#!/usr/bin/env bash
# Lint Python with the ruff version this repo pins, and refuse to lint with any
# other one. Read-only: ruff is run without --fix.
#
# The pin exists because ruff's rule set changes between releases, so a gate
# whose rules move on their own is not reproducible. Running whatever ruff
# happens to be on PATH defeats that: the local gate would report "ruff passed"
# against a different rule set than CI, which is a pass that means something
# else rather than the same pass.
#
# requirements-dev.txt is the single source of the pin. CI installs from it and
# runs this script; a developer installs from it too. Both install commands are
# printed on failure because this repo's own venv is uv-created and has no pip,
# so the pip line alone sends the reader into "No module named pip".

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

install_hint() {
  echo "      python3 -m pip install -r requirements-dev.txt" >&2
  echo "      uv pip install -r requirements-dev.txt   # venv without pip" >&2
}

PIN="$(sed -n 's/^ruff==\([0-9][0-9.]*\).*/\1/p' requirements-dev.txt | head -1)"
if [[ -z "$PIN" ]]; then
  echo "FAIL: no 'ruff==<version>' pin found in requirements-dev.txt" >&2
  exit 1
fi

if ! command -v ruff >/dev/null 2>&1; then
  echo "FAIL: ruff is not installed. Install the pin with one of:" >&2
  install_hint
  exit 1
fi

HAVE="$(ruff --version | awk '{print $2}')"
if [[ "$HAVE" != "$PIN" ]]; then
  echo "FAIL: ruff $HAVE is installed, but this repo pins $PIN." >&2
  echo "      A different rule set is a different gate. Run one of:" >&2
  install_hint
  exit 1
fi

echo "ruff $HAVE (pinned)"
ruff check .
