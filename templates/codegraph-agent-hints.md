## Source intelligence

If `.codegraph/` exists, prefer CodeGraph for source-structure questions before
broad file scans.

Use CodeGraph for:

- symbol lookup
- callers/callees
- impact analysis
- code-flow exploration

Do not use CodeGraph as durable MQ memory. Use mqobsidian context packs and
cards for memory, repo boundaries, and prior verified work.
