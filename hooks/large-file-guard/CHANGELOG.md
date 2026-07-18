# Changelog

All notable changes to this hook will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-18

- 新增 omp 平台支持：`omp.ts` 扩展工厂安装到 `.omp/hooks/pre/large-file-guard.ts`，匹配 `bash` 工具，调用同一份 shell 脚本；退出码 2 翻译为 `{ block, reason }`，其余退出码放行。

## [0.1.0] - 2026-07-06

- Initial release: PreToolUse guard that intercepts `git commit` (Claude Code `Bash` matcher / Codex `exec_command` matcher) and denies the commit when a staged text file — or, with `-a`/`--all`, a tracked modified file — exceeds the line threshold (default 1000), feeding the offender list back to the model.
- Incremental ratchet semantics: only files the commit touches are checked; legacy large files do not block until modified.
- Per-project config via `.large-file-guard.json` (`enabled`, `maxLines`, `exclude` globs) on top of built-in excludes for lockfiles, minified assets, source maps, snapshots, and `dist`/`build`/`vendor`/`node_modules`.
