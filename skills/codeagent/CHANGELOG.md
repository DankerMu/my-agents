# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2026-08-08

### Fixed

- 纠正 0.2.0/0.2.1 的错误说法：`--reasoning-effort` **不会**被 omp backend 丢弃，wrapper 会把它翻译成 omp 的 `--thinking`（实测生成 `--thinking max`，session 记录确认生效）；`--parallel` 的 `reasoning_effort:` 头同样生效。
- OMP 小节与 CLI flag 表改为推荐用 `--reasoning-effort` 传强度，并说明为何不要写进 model 串：`provider/model:effort` 只对 omp 权威列出的 provider 有效，网关自定义 provider（如 `sub-gpt`/`sub-claude`）会直接 `Model not found`；裸 model 不带 effort 也不会继承 `modelRoles` 的配置，实测落到固定的 `high`。

## [0.2.1] - 2026-08-08

### Changed

- OMP 小节点明 `--no-skills` 与 `--no-rules` 的不对称：前者有 wrapper 的 `--skills` 顶上，后者没有任何补偿通道，也没有 omp 额外参数的透传口；写代码的任务必须在 prompt 里让它自己去读 `AGENTS.md`/`CLAUDE.md`。
- 补充 `--auto-approve` 默认开启的后果：委派的写任务没有审批闸，用 `workdir` 圈住作用范围。

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
