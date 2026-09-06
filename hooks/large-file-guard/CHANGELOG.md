# Changelog

All notable changes to this hook will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-05

移植自 NWM 仓库的 `.claude/hooks/large-file-guard/` 分叉（NWM 提交 `7af4b6f8`、`a9af21db`、`67017eaf`），脚本与分叉逐字节一致；测试套件同源，仅去掉 NWM 专属 fixture 名。

### Added

- `git merge --continue` 视同 commit 触发检查；结束合并（含 `git commit --no-edit`）时只统计**与每个 parent 都不同**的暂存内容，从对侧合入的既有大文件不再被拦（NWM 2026-08-09 一次合并被误拦 20 个文件的根因）。
- 工具调用 JSON 里的 `cwd` 解析到其 git 顶层作为根：配置文件、`git -C`、工作区读取、`MERGE_HEAD` 查找全部以该根为准；`CLAUDE_PROJECT_DIR` 只作无 `cwd` 或 `cwd` 不在 git 仓库时的回退。修复 linked worktree / 嵌套目录里提交读错主 checkout 配置的问题。omp 的 `omp.ts` 本就传 `cwd: process.cwd()`，三个平台接线不变。
- 路径类 git 输出按字节处理（只剥协议换行，`os.fsdecode`），尾随空格 / CR / LF 的工作区路径不再被截断。
- 打包测试 `tests/test-large-file-guard.sh`（46 条断言：普通提交、合并结束、linked worktree 配置解析、回退根、路径字节保真、精确豁免 vs 同目录 glob），由 `scripts/tests/large-file-guard.test.js` 接入 `npm test`；`tests/` 不随安装拷贝到项目。

### Changed

- 文档：安装/卸载说明改为 hook 命令级 merge 语义（同 `matcher` 块内按 `command` 增删，见 `scripts/lib/settings-merge.js`），删除"跨目录提交可能漏检"的限制。

- 文档：metric 口径引用改指 `repo-entropy-audit` 的 `metric-definitions.md`（原 `control-plane-auditor` 已退役），存量治理搭档改为 `repo-entropy-audit` / `eng-init`。行为不变。

## [0.2.0] - 2026-07-18

- 新增 omp 平台支持：`omp.ts` 扩展工厂安装到 `.omp/hooks/pre/large-file-guard.ts`，匹配 `bash` 工具，调用同一份 shell 脚本；退出码 2 翻译为 `{ block, reason }`，其余退出码放行。

## [0.1.0] - 2026-07-06

- Initial release: PreToolUse guard that intercepts `git commit` (Claude Code `Bash` matcher / Codex `exec_command` matcher) and denies the commit when a staged text file — or, with `-a`/`--all`, a tracked modified file — exceeds the line threshold (default 1000), feeding the offender list back to the model.
- Incremental ratchet semantics: only files the commit touches are checked; legacy large files do not block until modified.
- Per-project config via `.large-file-guard.json` (`enabled`, `maxLines`, `exclude` globs) on top of built-in excludes for lockfiles, minified assets, source maps, snapshots, and `dist`/`build`/`vendor`/`node_modules`.
