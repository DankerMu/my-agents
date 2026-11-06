# Changelog

## [0.1.0] - 2026-11-06

- 首个版本：PreToolUse 审批点，拦截对任意目录 `AGENTS.md` / `CLAUDE.md` 的修改（文件编辑工具 + 有写入迹象的 shell 命令）。
- Claude Code：`permissionDecision: "ask"` 走原生权限确认；omp：有 UI 时用 `ctx.ui.confirm`，无 UI 时拦截；Codex：PreToolUse 不支持 `ask`，拦截后由用户运行一次性 `approve` 命令放行（每文件一张、15 分钟过期、存于项目外的 XDG state 目录）。
- 模型自行执行 `approve`，或经编辑工具 / shell 写令牌目录，会被拦下。
- Python 以 `-I` 隔离模式运行，工作目录里的同名模块无法让 guard 失效。
- Codex `apply_patch` 按实测 payload（`tool_input.command` 补丁文本）解析 `Add/Update/Delete File` 与 `Move to` 目标。
