# Changelog

## [0.1.1] - 2026-07-11

- Tighten the description to a lean identity + explicit-invocation clause (slimming batch 2): this skill is reached by name — by the user or an orchestrating skill — so trigger vocabulary moves out of standing context. Body and behavior unchanged.

## [0.1.0]

- Initial issue-controller skill for Issue Agent OS.
- Thin concurrent dispatcher loop: pull queue → triage → dispatch → review loop → merge → repeat.
- Supports max 6 parallel workers with slot-based concurrency.
- Migrated from agent package to skill — runs at depth 0 in main session, avoiding sub-agent nesting limits.
