# Changelog

## [Unreleased]

### Added

- Added the first repo-local `.mq/context/` export generated through `mq-agent context export`.
- Published `.mq/context-budgets.json` as the cross-repo context-export budget contract, with `docs/context-export-contract.md` declaring mqobsidian as owner and mq-agent as the designated consumer.
- Added a CI drift guard that regenerates `.mq/context` exports and fails when the committed `examples/repo-context-exports` are stale.

### Changed

- Updated the Phase 4 roadmap with the verified nine-repo local rollout and safe managed-file cleanup contract.

### Fixed

## [0.2.1] - 2026-06-17

### Added

- Seeded mqobsidian, mq-agent, and mq-mcp context cards for the token reduction layer.
- Added tracked mqobsidian system hot/index surfaces for agent read-order grounding.
- Added VERSION and CHANGELOG release metadata.

### Changed

- Expanded token budget checks to cover system hot/index notes, context cards, and agent views.
- Expanded export validation to check context-pack frontmatter and required context-card sections.
- Documented Phase 2 context-card seed status in the token-reduction roadmap.
