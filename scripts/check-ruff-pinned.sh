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
# runs this script; a developer installs from it too.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

PIN="$(sed -n 's/^ruff==\([0-9][0-9.]*\).*/\1/p' requirements-dev.txt | head -1)"
if [[ -z "$PIN" ]]; then
  echo "FAIL: no 'ruff==<version>' pin found in requirements-dev.txt" >&2
  exit 1
fi

if ! command -v ruff >/dev/null 2>&1; then
  echo "FAIL: ruff is not installed. Run: python3 -m pip install -r requirements-dev.txt" >&2
  exit 1
fi

HAVE="$(ruff --version | awk '{print $2}')"
if [[ "$HAVE" != "$PIN" ]]; then
  echo "FAIL: ruff $HAVE is installed, but this repo pins $PIN." >&2
  echo "      A different rule set is a different gate. Run:" >&2
  echo "      python3 -m pip install -r requirements-dev.txt" >&2
  exit 1
fi

echo "ruff $HAVE (pinned)"
ruff check .
