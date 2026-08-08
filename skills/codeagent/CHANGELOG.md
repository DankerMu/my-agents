# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-08-08

### Added

- OpenCode 与 OMP（oh-my-pi）两个 backend；OMP 单列一节说明四点差异：凭据来自 `~/.omp/agent/`、委派会话带 `--no-skills --no-rules`（不加载任何项目 skill / 规则 / agent 定义）、reasoning effort 必须写进 model 串、tools 为小写白名单。
- Agent presets（`~/.codeagent/models.json` 的 `agents.<name>` 或 `~/.codeagent/agents/<name>.md`）、skill 注入（自动探测表 + `--skills` 覆盖）、`--worktree` 隔离、tool control。
- 完整 CLI flag 表、exit code 表、`--output` 结构化 JSON 形态，以及并行 task DSL 的全部 header 字段（`agent`/`model`/`skills`/`dependencies`/`session_id`/`skip_permissions`/`worktree`）。
- `[codeagent-progress]` 帧的判读规则：还在刷帧就说明任务活着，不要当成"没有返回"而自己动手。

### Changed

- 默认后台执行、优先 `--parallel` 的使用取向写进 Overview 与 Invocation Pattern。
- Security 节重写：`--skip-permissions` 的适用边界、heredoc 定界符必须加引号（任务文本是数据不是指令）、tool control 的显式枚举约束。
- `When Not to Use` 增补 `orche-omp-workflow` 的嵌套委派禁令。

### Known limitations

- `--reasoning-effort` 对 omp backend 被静默丢弃。
- model 串的 `:effort` 后缀只对本地 omp 模型缓存中权威列出的模型可解析；discovery 缓存为空的 provider 需退回裸 pin，否则报 `Model "…" not found`。

## [0.1.2] - 2026-07-11

- Move session resume, parallel execution, and the backend selection guide to `references/advanced-usage.md` (slimming batch 5). Core usage, parameters, critical rules, and security notes stay in the body.
- Drop the Recent Updates section — this changelog owns release history.

## [0.1.1] - 2026-06-15
- Update stale cross-reference: `codex-codeagent-workflow` -> `subagent-workflow` (skill renamed).

## [0.1.0] - 2026-05-25
- Initial canonical package for `codeagent-wrapper` usage.
- Documents single-task, resume, and parallel execution patterns across Codex, Claude, and Gemini backends.
