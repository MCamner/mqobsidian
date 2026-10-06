---
schema: learn-record.v1
pattern_name: interactive-menu-exit-status-contract
created_at: 2026-10-06T17:16:25Z
summary: Interactive menu lifecycle exits must not be conflated with operational delegate failures; normalize bare menu EOF/no-TTY termination to success while preserving real operation status.
recommended_action: Split dispatcher branches by intent so bare interactive entrypoints return 0 on normal menu termination and explicit operations propagate the delegate's actual exit status.
type: learn
system: macos-scripts
status: verified
date: 2026-10-06
tags: [macos-scripts, mqlaunch, exit-status, interactive-menu, smoke-test, regression]
source_evidence_refs:
  - https://github.com/MCamner/macos-scripts/pull/272
  - https://github.com/MCamner/macos-scripts/commit/b4cc5dcd0a8bb26ec1cc651c8fe6954a70fec8aa
  - tests/menu-exit-contract-smoke.sh
  - tests/delegated-exit-code-smoke.sh
---

# Interactive menu lifecycle must be separate from operation status

## Lesson

A shell dispatcher must distinguish between an interactive surface ending normally and a real delegated operation failing.

For a bare interactive command such as:

```bash
mqlaunch git
```

EOF, `MQ_NO_TUI=1`, or an unavailable TTY can make the inner menu return non-zero as an internal control-flow signal. That status must not automatically become the public command result when the menu simply had no choice to read.

By contrast, an explicit operation such as:

```bash
mqlaunch git /some/repo
```

must preserve validation and runtime failures from its delegate.

## Failure mode

The Git dispatcher previously used one propagation rule for both paths:

```text
bare menu -> gitlaunch no-TTY status 1 -> mqlaunch returns 1
explicit repo failure -> gitlaunch status 1 -> mqlaunch returns 1
```

The second result was correct. The first was not.

This produced the end-to-end smoke failure:

```text
FAIL: a menu ending was reported as a failure: git=1
```

A stubbed delegate test remained green because it verified the intended contract without exercising the real `gitlaunch.sh` no-TTY path.

## Correct pattern

Split the dispatcher by intent:

```text
interactive lifecycle
  bare command / menu
  EOF or no TTY
        -> public exit 0

operational request
  explicit repo / real action
  validation or runtime failure
        -> propagate delegate status
```

Do not solve this by forcing the lower-level menu implementation to always return 0. Its non-zero no-TTY result is useful internal control flow. Normalize it only at the public interactive boundary.

## Evidence

The defect was exposed by `tests/menu-exit-contract-smoke.sh`, which runs the real `bin/mqlaunch` path end to end. The more precise stubbed contract in `tests/delegated-exit-code-smoke.sh` already showed that deliberate interactive endings are success while operational delegate failures must propagate.

The fix in `macos-scripts` PR #272 separates bare `git` / `git menu` lifecycle handling from explicit repo handling. Commit `b4cc5dcd0a8bb26ec1cc651c8fe6954a70fec8aa` contains the change.

Operator verification on 2026-10-06 confirmed that the previously failing self-check succeeds after applying the fix.

At the time this learning record was authored, PR #272 was still open; the evidence commit is therefore referenced directly rather than claiming a merge to `main`.

## Reuse

Apply this pattern to any CLI branch that combines:

- an interactive menu or picker,
- a headless/EOF termination path,
- and explicit subcommands or arguments that perform real work.

Test both layers:

1. a stubbed delegate test that pins status propagation precisely;
2. an end-to-end smoke test that executes the real launcher and catches control-flow statuses leaking across process boundaries.

## Operational rule

Do not use one unconditional `return $?` policy for a branch that mixes interactive lifecycle and operational work.

Classify the path first:

- **menu lifecycle** -> normalize a normal ending to success;
- **operation** -> preserve the delegate's exit status;
- **usage error** -> return the documented usage status.

This keeps automation trustworthy without treating normal menu termination as a failure.
