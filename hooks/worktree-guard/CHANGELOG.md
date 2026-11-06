# Changelog

## [0.2.2] - 2026-11-06

- 修复：Codex 上此前完全不拦截。Codex `apply_patch` 的 payload 没有路径字段，目标写在 `tool_input.command` 的补丁头里（codex-cli 0.158 实测），旧脚本只读 `file_path`/`path`/`notebook_path`，因此一律放行。现在解析 `*** Add File:` / `Update File:` / `Delete File:` / `Move to:`，补丁里任一目标越界即拒绝。
- 加固：内嵌 Python 以 `python3 -I` 运行，工具调用 cwd 下的同名模块（如 `json.py`）不再能让 guard 失效。
- 新增 `tests/test-worktree-guard.sh`（16 项，覆盖 Claude Code / Codex / omp 三种 payload），经 `scripts/tests/worktree-guard.test.js` 接入 `npm test`。

## [0.2.1] - 2026-09-05

- 文档：安装/卸载说明改为 hook 命令级 merge 语义（同 `matcher` 块内按 `command` 增删，`scripts/lib/settings-merge.js`）。脚本行为不变。

## [0.2.0] - 2026-07-18

- 新增 omp 平台支持：`omp.ts` 扩展工厂安装到 `.omp/hooks/pre/worktree-guard.ts`，匹配 `edit`/`write` 工具，调用同一份 shell 脚本；退出码 2 翻译为 `{ block, reason }`，其余退出码放行。

## [0.1.0] - 2026-07-06

- 首个版本：PreToolUse 路径护栏，基于项目根 `.worktree-guard.json` 声明的 allowedRoots 拦截越界文件写入。
- 双平台支持：Claude Code（`Edit|Write|MultiEdit|NotebookEdit`）与 Codex（`apply_patch`），共用同一脚本。
- 无清单时为 no-op，可安全全量安装；卸载按 deep-equal 摘除托管条目，不影响用户手写 hooks。
