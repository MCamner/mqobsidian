# Integration: CodeGraph source intelligence

CodeGraph is an optional **local source-code intelligence layer** for the MQ
stack. It indexes each repo's source into a local `.codegraph/` database and
answers structural questions — symbol lookup, callers/callees, code-flow, and
impact/blast-radius — without the agent grepping and reading many files.

This document covers what CodeGraph does, what `mqobsidian` keeps, how to
install and wire it, how to initialize each MQ repo, and how agents should use
it before broad source scans.

## What CodeGraph does

* indexes local source into `.codegraph/`
* answers symbol lookup ("where is this implemented?")
* answers callers/callees ("what calls this?")
* answers impact/blast-radius ("what breaks if this changes?")
* explores code flow ("how does this go from command to writer?")
* keeps its index current via auto-sync

## What mqobsidian does

`mqobsidian` stays the durable memory and context-contract layer. It owns:

* durable architecture memory
* context cards and context packs
* schemas, templates, and context/token-budget rules
* repo responsibility map
* public-safe exports

See `docs/CONTEXT_CONTRACT.md`. The smallest-useful-surface-first rule still
applies; source repos and tools own live truth.

## What CodeGraph must not replace

CodeGraph is **not** durable memory. Do not use it for:

* MQ durable architecture memory
* historical decisions
* repo boundaries / responsibility map
* runtime truth or behavior verification (use source tests and CLI)
* public-safe exports

```text
mqobsidian = what the agent should read first
CodeGraph  = what the agent should ask when it needs to understand the code
mq-agent   = exports/packs the right context
mq-mcp     = runtime and safety contracts
```

## Which MQ repos to index

Initial MQ-stack target repos:

* `mqobsidian`
* `mq-agent`
* `mq-mcp`
* `mq-hal`
* `repo-signal`
* `mq-ums`
* `mq-image-analyze`
* `macos-scripts` / `mqlaunch` if present locally

## Install

### macOS / Linux bundle install

```bash
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
```

Open a new terminal after install, then verify:

```bash
codegraph version
```

### npm install alternative

Use this when Node/npm is already preferred:

```bash
npm i -g @colbymchenry/codegraph
codegraph version
```

### Windows PowerShell reference

Not the main MQ-stack path, documented for cross-platform parity:

```powershell
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex
codegraph version
```

## Wire CodeGraph to coding agents

Connect CodeGraph to the supported coding agents:

```bash
codegraph install --target=claude,cursor,codex
```

Non-interactive setup:

```bash
codegraph install --target=claude,cursor,codex --yes
```

Optional privacy-first local setting:

```bash
codegraph telemetry off
```

`CODEGRAPH_TELEMETRY=0` and `DO_NOT_TRACK=1` are equivalent environment
toggles.

## Initialize each MQ repo

Run in each repo that should expose source intelligence to agents:

```bash
cd ~/mqobsidian && codegraph init
cd ~/mq-agent && codegraph init
cd ~/mq-mcp && codegraph init
cd ~/mq-hal && codegraph init
cd ~/repo-signal && codegraph init
cd ~/mq-ums && codegraph init
cd ~/mq-image-analyze && codegraph init
```

Optional if local:

```bash
cd ~/macos-scripts && codegraph init
```

Or use the stack helper:

```bash
bash scripts/init-codegraph-stack.sh
```

## Keep `.codegraph/` local

Each repo must ignore its local CodeGraph index:

```gitignore
.codegraph/
```

`.codegraph/` is a local index, never durable memory. Do not commit the
database and do not export it into `examples/`. The init helper appends the
ignore rule if it is missing.

## Verify status

```bash
codegraph status
bash scripts/check-codegraph-stack.sh
```

`scripts/check-codegraph-stack.sh` reports the installed version, flags repos
missing `.codegraph/` or the `.gitignore` entry, and runs `codegraph status`
where initialized. It does not modify files.

## Coverage and unsupported surfaces

A green `codegraph status` only covers **supported source languages**. CodeGraph
1.0.x indexes languages such as Python, JavaScript, YAML, and XML; it does **not**
parse shell (`.sh`, `.bash`, `.zsh`, `.fish`) or PowerShell (`.ps1`, `.psm1`,
`.psd1`). In the MQ stack those are real command surfaces — `macos-scripts` alone
is hundreds of shell files — so an "up to date" index can silently hide most of a
repo's actual behavior.

Get an honest, public-safe coverage view:

```bash
bash scripts/check-codegraph-stack.sh --coverage
```

For every MQ repo this emits JSON with the indexed languages and counts plus an
explicit `unsupported_source` list (shell / PowerShell files present on disk but
not indexed) and a `coverage_status` of `full` or `partial`. Output is
public-safe: repo basenames only, no machine paths and no `.codegraph/` database
paths. See `examples/codegraph/stack-coverage.example.json` for the shape.

Rule: a repo whose only unindexed source is shell/PowerShell is `partial`, never
"fully indexed". Do not treat a green index as complete coverage of a
command-surface repo.

### Upstream boundary

Shell and PowerShell parsing belong to **CodeGraph upstream**, not `mqobsidian`.
The vault does not implement shell/PowerShell parsing (see the roadmap non-goals);
it only reports the gap so agents fall back to source reads and tests for those
surfaces. If upstream adds shell/PowerShell extraction, these surfaces move from
`unsupported_source` into `indexed_languages` with no change to this contract.

## How agents should use CodeGraph

Prefer CodeGraph before broad grep/read loops. Use it when the task asks:

* where is this implemented?
* what calls this?
* what breaks if this changes?
* how does this flow from command to writer?
* which tests are likely affected?

Suggested query patterns for MQ tasks:

```bash
codegraph explore "how does context export work"
codegraph explore "how does brain_record_learning write memory"
codegraph query "generate_context_pack"
codegraph callers "generate_context_pack"
codegraph impact "context_pack"
codegraph node scripts/generate-context-pack.py
codegraph affected $(git diff --name-only)
```

## When to fall back to normal source reads

Fall back to plain reads/grep and source tests when:

* the repo is not initialized (no `.codegraph/`)
* the question is about durable architecture memory or historical decisions
* the question requires current test execution to verify behavior
* a CodeGraph result shows a staleness warning

For those, use `mqobsidian` context packs and cards for memory and boundaries,
and run source tests/CLI for behavior.

## Validation

Run after editing the docs/scripts/templates in this repo:

```bash
python3 scripts/check-token-budget.py
python3 scripts/validate-export.py
python3 scripts/check-sensitive-content.py
```
