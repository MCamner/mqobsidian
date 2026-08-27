# NotebookLM bridge boundary

## Status

The NotebookLM bridge is **experimental** and optional. It may synthesize an
explicitly approved source pack, but it is not canonical memory, repository
truth, or a required MQ dependency.

The adapter's authentication and tool surface are runtime facts. Verify the
installed adapter before use; do not encode assumed tool names as MQ contracts.

## Ownership

| Layer | Owns |
|-------|------|
| mqobsidian | durable knowledge, schemas, templates, policy, sanitized examples |
| mq-agent | selection, pack generation, hashing, export, routing, sync, fallback |
| CodeGraph | current code structure and call paths |
| NotebookLM | synthesis over an approved exported source set |
| macos-scripts | optional operator UX after the workflow is stable |

NotebookLM never writes directly to `decisions/`, `learn/`, `systems/`, or
other canonical memory. Provider output may later enter the normal inbox and
human-review flow as a provenance-bearing candidate only.

## Consumer profile

`.mq/notebooks.json` is configuration, not a new memory contract. It declares
NotebookLM as an experimental read-only consumer, names the existing MQ
contracts it consumes, and provides narrow include/exclude rules for each
logical notebook.

The first profile contains only `mq-stack-intelligence`, displayed as
**MQ Stack Intelligence**. Its allowlist targets reviewed, tracked Markdown
surfaces; it does not include entire `systems/`, `memory/`, or vault roots.
mq-agent may later consume the profile, but mqobsidian does not implement an
exporter.

The profile separates two source lanes. `reviewed` content comes from
mqobsidian and is active. `observed` content comes from CodeGraph, requires a
repository revision, and remains deferred until mq-agent can export it without
misclassifying graph output as a decision or memory observation.

## Data boundary

Selection is deny-by-default. A source must be explicitly allowlisted and carry
one of the classifications accepted by `notebook-pack.v1`:

- `public-safe` — already suitable for the public repository surface.
- `approved-external` — explicitly approved for this external provider and
  notebook; approval must exist outside the manifest.

Never export by default:

- credentials, secrets, tokens, `.env` content, or authentication material
- personal, patient, or otherwise regulated data
- raw sessions, inbox material, or unreviewed local-rich notes
- binaries, oversized artifacts, generated indexes, or `.codegraph/`
- paths outside the selected mqobsidian roots

A denylist is defense in depth, not permission. It cannot widen the allowlist.

### Gitignored durable memory never exports

The publication boundary is the export boundary. A source that git ignores does
not become eligible by being reviewed, well-written, or useful to a provider:

```text
tracked, public-safe truth surfaces   ->  export allowed
gitignored durable memory             ->  never exported
  learn/  reviews/  unpublished decisions/  memory/  systems/
```

Two independent reasons, either sufficient. **Provenance would be false:** the
exporter stamps every source with the vault's HEAD commit, and gitignored files
are invisible to `git status`, so they would be written as `dirty: false` and
read as commit-bound while not existing in the repository at all. **And the
boundary is deliberate:** this material is local by design, so exporting it
moves durable memory to an external provider.

Do not extend the exporter to provenance-mark ignored material in order to make
it exportable. Benchmark value is not a reason to move this boundary; if a
measurement needs the private surface to succeed, the correct outcome is that
the measurement fails.

## Pack contract

`schemas/notebook-pack.v1.json` describes the manifest. Every source has a
vault-relative path, kind, classification, SHA-256, and optional repository
revision. Absolute paths, parent traversal, and Windows path separators are
invalid.

A revision must declare `dirty`. The SHA-256 describes the working tree, so a
commit alone would imply the content is commit-bound even when it is not. When
`dirty` is true, the named commit does not explain the hash, and the source is
not reproducible from the repository at that revision. The flag is required
rather than optional: an omitted flag would read as clean.

`content_hash` is calculated from canonical source metadata and source content.
`generated_at` is excluded, so rebuilding unchanged inputs produces the same
content hash. mq-agent is the only allowed generator identity.

Generated packs and real notebook identifiers remain under local-only
`.notebooklm/`. Only the consumer profile, schema, template, policy, and
sanitized example are published from mqobsidian.

## Safe workflow

```text
explicit allowlist
  -> resolve inside approved vault roots
  -> reject unsafe type, size, path, or classification
  -> sensitive-content scan
  -> deterministic local pack and dry-run
  -> explicit operator approval
  -> remote source mutation
```

Local reads and local pack generation may be automated. Adding, updating, or
removing remote sources requires explicit operator approval.

## Agent routing

Use the smallest sufficient source:

```text
code location / impact       -> CodeGraph
decision / history / lesson  -> mqobsidian read order or memory query
live behavior                -> source repo, tests, or bounded runtime tool
cross-document synthesis     -> NotebookLM, when available and approved
```

Codex and Claude should receive a compact synthesis plus provenance, not a full
notebook transcript. If NotebookLM is unavailable, stale, unauthorized, or
unnecessary, mq-agent falls back to existing MQ retrieval.

## Activation gate

Do not upload real MQ content until all are true:

- adapter version and actual operations are recorded
- data classification and organizational approval are confirmed
- sensitive-content and path checks pass
- a dry-run shows every addition, change, and removal
- the operator explicitly approves the remote mutation

The first proof uses one `mq-stack-intelligence` notebook and the five fixed
questions in `docs/notebooklm-evaluation.md`. Measure its incremental value over
CodeGraph plus compact mqobsidian retrieval before building incremental sync or
automatic routing.
