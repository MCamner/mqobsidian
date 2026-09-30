---
type: learn
system: repo-signal
status: verified
date: 2026-08-17
tags: [repo-signal, uv, packaging, cli, mq-stack]
---

# repo-signal — uv tool installation

## Lesson

`repo-signal` works correctly as an isolated `uv tool`. For the full feature surface, install the `ai` and `vector` extras together.

Canonical install while PyPI is behind the GitHub release:

```bash
uv tool install \
  'repo-signal[ai,vector] @ git+https://github.com/MCamner/repo-signal.git@v1.4.2'
```

## Verified state

- `repo-signal --version` -> `repo-signal 1.4.2`
- `repoaware --help` works.
- `uv tool list` exposes both `repo-signal` and `repoaware`.
- CLI path is `/Users/mansys/.local/bin/repo-signal`.
- uv tool root is `/Users/mansys/.local/share/uv/tools`.
- Imports inside the installed tool environment succeed for `openai`, `dotenv`, and `chromadb`.
- Direct verification returned `ai+vector OK`.

## Packaging conclusion

The core CLI is installable without a repo checkout. `pyproject.toml` declares the console entry points and package list, and the packaging check builds a wheel, installs it into a clean environment, and smoke-tests core commands.

The repo-level `bin/`, `scripts/`, `tools/`, `skills/`, `docs/`, and `examples/` directories are development/repository assets rather than required runtime files for the installed CLI.

## CI guard

`repo-signal` packaging CI now includes a `uv tool install .` smoke test that verifies the recommended installation model and exercises both installed executables plus core commands.

## Operational rule

For MQ CLI tools that are packaged as Python console applications, prefer `uv tool` over `pipx` when the package contract supports it. Install required extras explicitly, and add a CI smoke test for the canonical install path before treating a migration as complete.

## Caveat

At verification time, PyPI resolved `repo-signal==1.0.0` while GitHub tag `v1.4.2` existed. Until the current release is published to PyPI, install from the GitHub tag rather than plain `uv tool install repo-signal`.
