#!/usr/bin/env bash
# Release readiness check for mqobsidian. Read-only.
#
# Human mode (no flags / --dry-run): prints [PASS]/[FAIL] per check, exits 1 on
#   any failure.
# Contract mode (--json): emits a repo_release_check.v1 object on stdout and
#   exits 0 (the `status` field carries the verdict). Consumed by mq-agent's
#   `stack release --all --preflight`.
#
# These mirror the Public Safe Check CI gate — mqobsidian's releasability
# assertions — minus the context-export staleness step, which regenerates files
# and so is not read-only. CI enforces staleness on every push.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1

DRY_RUN=0
JSON=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --json) JSON=1 ;;
    *) echo "usage: ./release-check.sh [--dry-run] [--json]" >&2; exit 2 ;;
  esac
done
# --dry-run is accepted for contract compatibility; this check is already
# read-only, so it is a no-op.
: "$DRY_RUN"

FAILED=0
BLOCKERS=()
VERSION="$(cat VERSION)"

step() { [[ "$JSON" -eq 1 ]] || printf "\033[1;34m[----]\033[0m %s\n" "$*"; }
pass() { [[ "$JSON" -eq 1 ]] || printf "\033[1;32m[PASS]\033[0m %s\n" "$*"; }
fail() { FAILED=1; BLOCKERS+=("$1"); [[ "$JSON" -eq 1 ]] || printf "\033[1;31m[FAIL]\033[0m %s\n" "$*" >&2; }

# run LABEL CMD...  — record a blocker on failure; keep stdout clean by routing
# captured output to stderr (human mode) only on failure.
run() {
  local label="$1"; shift
  local out
  if out="$("$@" 2>&1)"; then
    pass "$label"
  else
    fail "$label"
    [[ "$JSON" -eq 1 ]] || printf '%s\n' "$out" >&2
  fi
}

step "Version surface"
if grep -q "\[${VERSION}\]" CHANGELOG.md; then
  pass "CHANGELOG references [$VERSION]"
else
  fail "CHANGELOG does not reference [$VERSION]"
fi

step "Public-safe — no sensitive content"
run "check-sensitive-content.py" python3 scripts/check-sensitive-content.py

step "Export scaffolding valid"
run "validate-export.py" python3 scripts/validate-export.py

step "Token budget"
run "check-token-budget.py" python3 scripts/check-token-budget.py

step "Agent entrypoints canonical"
run "check-agent-entrypoints.py" python3 scripts/check-agent-entrypoints.py

step "Unit tests"
run "unittest" python3 -m unittest discover -s tests -q

if [[ "$JSON" -eq 1 ]]; then
  status=READY
  [[ "$FAILED" -ne 0 ]] && status=BLOCKED
  python3 - "$status" "$VERSION" ${BLOCKERS[@]+"${BLOCKERS[@]}"} <<'PY'
import json
import sys

status, version, *blockers = sys.argv[1:]
print(json.dumps({
    "schema": "repo_release_check.v1",
    "repo": "mqobsidian",
    "status": status,
    "blockers": blockers,
    "warnings": [],
    "evidence": {"version": version},
}))
PY
  exit 0
fi

printf '\n'
if [[ "$FAILED" -eq 0 ]]; then
  printf "\033[1;32m=== release-check passed — v%s checks are green ===\033[0m\n" "$VERSION"
else
  printf "\033[1;31m=== release-check FAILED — fix issues before releasing ===\033[0m\n"
  exit 1
fi
