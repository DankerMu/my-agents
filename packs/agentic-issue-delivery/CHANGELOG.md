# Changelog

All notable changes to this pack will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-14

- Replace the `codex-codeagent-workflow` member with its renamed successor `subagent-workflow`, which delegates implementation, review, and verification to native subagents instead of an external code-agent CLI.
- Bundle the worker subagents the workflow depends on: `implementer`, `reviewer`, and `verifier`, plus their declared `explorer` dependency (previously the pack installed no agents).
- Update the pack description and notes: the delivery path no longer requires `codeagent-wrapper`; it requires a subagent-capable orchestrator (Claude Code Task subagents or Codex subagents). The `codeagent` skill remains bundled as optional CLI documentation.

## [0.1.0] - 2026-05-25

- Initial agentic issue delivery workflow pack.
- Bundles `stage-change-pipeline`, `codex-codeagent-workflow`, `risk-adaptive-cross-review`, and local planning/review/documentation support skills.
- Includes `codeagent` and `gh-create-issue` as canonical local support skills while documenting the external CLI prerequisites.
