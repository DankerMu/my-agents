# Hooks Catalog

> This file is generated. Run `npm run build`.

| Name | Version | Maturity | Events | Platforms | Categories | Description |
| --- | --- | --- | --- | --- | --- | --- |
| [instruction-guard](../../hooks/instruction-guard/HOOK.md) | 0.1.0 | experimental | PreToolUse | claude-code, codex, omp | security, workflow | PreToolUse hook that requires the user's approval before AGENTS.md or CLAUDE.md is modified (any directory, file tools and write-capable shell commands). Claude Code shows its native approval prompt; omp asks through its confirm dialog; Codex, whose hooks cannot ask, denies until the user runs a one-shot approval command. |
| [large-file-guard](../../hooks/large-file-guard/HOOK.md) | 0.3.0 | experimental | PreToolUse | claude-code, codex, omp | workflow, review | PreToolUse hook that blocks `git commit` and `git merge --continue` when the commit would include text files over a line-count threshold (default 1000). Incremental ratchet: only files touched by the commit are checked (merge conclusions count only content that differs from every parent); legacy large files do not block until modified. Resolves the tool-call cwd to its git top level; configurable via .large-file-guard.json there. |
| [review-gate](../../hooks/review-gate/HOOK.md) | 0.4.0 | experimental | PreToolUse | claude-code, codex, omp | workflow, review | PreToolUse hook that denies implementer/reviewer subagent spawns once subagent-workflow has used its two fix passes on a PR. No-op until the project has a .review-gate.json state file (maintained by the skill's fix_gate.py CLI), so it is safe to install everywhere. |
| [worktree-guard](../../hooks/worktree-guard/HOOK.md) | 0.2.2 | experimental | PreToolUse | claude-code, codex, omp | security, workflow | PreToolUse hook that blocks file writes outside declared worktree roots. No-op until the project declares .worktree-guard.json, so it is safe to install everywhere. |
