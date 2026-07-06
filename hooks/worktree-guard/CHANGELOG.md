# Changelog

## [0.1.0] - 2026-07-06

- 首个版本：PreToolUse 路径护栏，基于项目根 `.worktree-guard.json` 声明的 allowedRoots 拦截越界文件写入。
- 双平台支持：Claude Code（`Edit|Write|MultiEdit|NotebookEdit`）与 Codex（`apply_patch`），共用同一脚本。
- 无清单时为 no-op，可安全全量安装；卸载按 deep-equal 摘除托管条目，不影响用户手写 hooks。
