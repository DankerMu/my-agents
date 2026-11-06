# Hooks Catalog

> This file is generated. Run `npm run build`.

| Name | Version | Maturity | Events | Platforms | Categories | Description |
| --- | --- | --- | --- | --- | --- | --- |
| [instruction-guard](../../hooks/instruction-guard/HOOK.md) | 0.2.1 | experimental | PreToolUse | claude-code, codex, omp | security, workflow | PreToolUse size gate for AGENTS.md / CLAUDE.md in any directory: at most 32 KiB per file and 307 bytes per line, old content included. Violations are denied with a hint to slim the file with the eng-init skill; `check` scans existing files. File tools and patches are judged on the resulting file, shell writes on the current one. |
| [large-file-guard](../../hooks/large-file-guard/HOOK.md) | 0.3.0 | experimental | PreToolUse | claude-code, codex, omp | workflow, review | PreToolUse hook that blocks `git commit` and `git merge --continue` when the commit would include text files over a line-count threshold (default 1000). Incremental ratchet: only files touched by the commit are checked (merge conclusions count only content that differs from every parent); legacy large files do not block until modified. Resolves the tool-call cwd to its git top level; configurable via .large-file-guard.json there. |
| [review-gate](../../hooks/review-gate/HOOK.md) | 0.4.0 | experimental | PreToolUse | claude-code, codex, omp | workflow, review | PreToolUse hook that denies implementer/reviewer subagent spawns once subagent-workflow has used its two fix passes on a PR. No-op until the project has a .review-gate.json state file (maintained by the skill's fix_gate.py CLI), so it is safe to install everywhere. |
| [worktree-guard](../../hooks/worktree-guard/HOOK.md) | 0.2.2 | experimental | PreToolUse | claude-code, codex, omp | security, workflow | PreToolUse hook that blocks file writes outside declared worktree roots. No-op until the project declares .worktree-guard.json, so it is safe to install everywhere. |
