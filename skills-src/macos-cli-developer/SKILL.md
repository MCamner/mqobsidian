---
name: macos-cli-developer
description: Use when designing, reviewing, simplifying, or improving macOS shell CLI tools, launchers, menu scripts, terminal workflows, Bash, Zsh, help output, flags, exit codes, and terminal UX.
---

# macOS CLI Developer

Use this skill when the task involves macOS-focused shell tools, launchers, menu scripts, terminal workflows, or automation scripts.

## Principle

Keep scripts safe, predictable, readable, and easy to verify. Do not over-engineer simple command-line tools.

## Best use cases

- Bash or Zsh scripts
- macOS terminal tooling
- launcher scripts such as `mqlaunch`, `gitlaunch`, or `netlaunch`
- menu/TUI scripts
- CLI flags and argument parsing
- `--help` output
- ShellCheck findings
- stdout/stderr separation
- exit codes
- `--json`, `--quiet`, `--dry-run`, `--no-color`
- safe destructive command handling
- terminal UX cleanup

## Operating rules

1. Identify the script's purpose.
2. Decide whether it is interactive, automation-friendly, or both.
3. Preserve existing behavior unless the user asks for a breaking change.
4. Prefer the smallest safe improvement.
5. Ask for script content only when it is unavailable.
6. Do not invent repository structure, flags, or file contents.

## Shell rules

For Bash:

- Prefer `#!/usr/bin/env bash`.
- Remember macOS may ship older Bash.
- Avoid newer Bash-only features unless Homebrew Bash is explicitly required.
- Quote variables unless word splitting is intentional.
- Avoid unsafe `eval`.
- Use arrays for argument lists where possible.

For Zsh:

- Use Zsh-specific features only when the script declares Zsh.
- Do not mix Bash assumptions into Zsh scripts.

For POSIX shell:

- Avoid Bash/Zsh-only syntax.
- Keep portability intentional.

## CLI UX standards

A good CLI command handles:

- `--help`
- invalid arguments
- missing required arguments
- non-interactive execution
- missing dependencies
- bad paths
- interrupted execution
- readable error messages

Suggest common flags only when they solve a real use case:

- `--version`
- `--verbose`
- `--quiet`
- `--dry-run`
- `--json`
- `--no-color`

## Output rules

- stdout is for primary output.
- stderr is for diagnostics, warnings, progress, and errors.
- JSON mode writes valid JSON to stdout only.
- Progress indicators must not pollute JSON output.
- `--quiet` suppresses non-essential human text.
- `--verbose` explains actions without exposing secrets.

## Color rules

Color must be optional.

Respect:

- `NO_COLOR`
- `--no-color`
- non-TTY output

Do not rely on Nerd Fonts, icons, or glyphs for meaning.

## Exit codes

Prefer:

- `0` success
- `1` general failure
- `2` usage or argument error

Never hide real failures behind exit code `0`.

## Safety rules

For commands that delete, overwrite, format, kill processes, change system or network state, or require sudo:

- recommend `--dry-run`
- require explicit confirmation for interactive use
- never prompt when stdin is not a TTY
- validate paths before destructive actions
- avoid broad globs
- print what will change before changing it
- do not run or suggest privileged commands unless explicitly requested

## Verification

Recommend practical checks when relevant:

```bash
shellcheck path/to/script.sh
bash -n path/to/script.sh
zsh -n path/to/script.zsh
./script --help
./script --dry-run
./script --json | jq .
```

Also test invalid flags, missing arguments, missing dependencies, non-existent paths, menu quit paths, and non-TTY behavior when relevant.

## Output format

Use this shape when it helps:

```md
## Goal
<what the script or change should achieve>

## Key findings
<important issues or design points>

## Recommended change
<exact patch, command, or replacement text when possible>

## Verification
<commands to run>

## Risks / notes
<what is unverified or could break>

## Next step
<one concrete next action>
```
