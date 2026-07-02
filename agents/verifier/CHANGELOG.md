# Changelog

All notable changes to the **verifier** agent will be documented in this file.

## [0.1.2] - 2026-07-02

### Changed

- Codex definition: added the two constraint bullets present on the Claude Code surface but missing from Codex ("Do not fabricate scenarios or guards" and "One candidate, one verdict — keep the output to the structured block").
- Claude Code tools: `Bash` -> `Bash(readonly)` to match the read-only role.

## [0.1.1] - 2026-06-14

### Changed

- Codex definition: model `gpt-5.4` -> `gpt-5.5` and reasoning effort `high` -> `xhigh`.

## [0.1.0] - 2026-06-14

### Added

- Initial release: independent finding-verification gate that adjudicates a single candidate review finding as CONFIRMED, PLAUSIBLE, or REFUTED.
- Read-only posture on both surfaces: Claude Code definition with Read, Glob, Grep, Bash; Codex definition with `read-only` sandbox and `gpt-5.4` at `high` reasoning effort.
- Encodes the find/verify separation: a verifier must not be the reviewer that produced the candidate, must not search for new findings, and must default ambiguous-but-realistic runtime states to PLAUSIBLE.
- Pairs with the `subagent-workflow` skill's Phase 4.5 verification gate.
