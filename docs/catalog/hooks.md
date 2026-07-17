# Hooks Catalog

> This file is generated. Run `npm run build`.

| Name | Version | Maturity | Events | Platforms | Categories | Description |
| --- | --- | --- | --- | --- | --- | --- |
| [large-file-guard](../../hooks/large-file-guard/HOOK.md) | 0.1.0 | experimental | PreToolUse | claude-code, codex | workflow, review | PreToolUse hook that blocks `git commit` when the commit includes text files over a line-count threshold (default 1000). Incremental ratchet: only files touched by the commit are checked; legacy large files do not block until modified. Configurable via .large-file-guard.json. |
| [review-gate](../../hooks/review-gate/HOOK.md) | 0.2.0 | experimental | PreToolUse | claude-code, codex | workflow, review | PreToolUse hook that denies implementer/reviewer subagent spawns while the subagent-workflow three-round hard gate is locked. No-op until the project has a .review-gate.json state file (maintained by the skill's review_gate.py CLI), so it is safe to install everywhere. |
| [worktree-guard](../../hooks/worktree-guard/HOOK.md) | 0.1.0 | experimental | PreToolUse | claude-code, codex | security, workflow | PreToolUse hook that blocks file writes outside declared worktree roots. No-op until the project declares .worktree-guard.json, so it is safe to install everywhere. |
