# Changelog

## [0.2.1] - 2026-11-06

### Fixed

- 拒绝信息里的瘦身指引原先写的是 eng-init 的“incremental 模式”，指错了。eng-init 处理臃肿指令文件的流程是 repair 模式的“AGENTS.md repair style”，配合 `references/agents-md-sections.md` 的 “Rendering strategy — concise hard kernel”、“Size budget”和 eng-init 3.8.0 新增的“Byte budget”，现在提示直接点名这几节。提示还写明了 eng-init 的硬约束：先挪走再压缩、规则一条不丢；决策、用户原话、用户自己写的段落只能原样移到链接文档。

## [0.2.0] - 2026-11-06

### Changed

- **不再拦截修改去审批**：hook 改成体积闸。`AGENTS.md` / `CLAUDE.md` 不得超过 32768 字节，单行不得超过 307 字节（UTF-8 字节）。超限直接拒绝，并提示按 `eng-init` skill（incremental 模式）瘦身；生成型项目改源片段再渲染。`approve` 子命令、审批令牌和 XDG 状态目录已移除。
- **旧内容也算**：能算出改后内容的调用（Claude Code `Edit` / `Write` / `MultiEdit`、Codex `apply_patch`、omp `write` 及 `edit` 的 replace / apply_patch 模式）检查改后的整份文件；文件已超限时，只放行减少超出量、且不引入新超长行的修复性改动。算不出改后内容的调用（shell 写入、omp hashline / patch 模式）在当前文件已超限时拒绝。
- 上限可用 `INSTRUCTION_GUARD_MAX_BYTES` / `INSTRUCTION_GUARD_MAX_LINE_BYTES` 调整。

### Added

- `check [路径…]` 子命令：扫描 AGENTS.md / CLAUDE.md 的超限情况，有超限时退出码为 1，可接入 CI。

### Fixed

- **只读 shell 命令不再被当成写入**：旧版在整条命令上跑正则，搜索词里出现 `install`、`patch`、`touch`、`cp`，或引号里有 `=>`，都会被判成写入，例如 `grep -n install AGENTS.md`。现在先按 shell 语法切分，再按命令名找写入目标。
- **补上旧版漏识别的写入方式**：glob（`rm *.md`）、`bash -c "…"`、`$(…)` / 反引号里的写入、`find -delete` / `-exec sed -i`、进程替换 `>(tee …)`、`cd` 之后的相对路径，以及 `cp x dir/` 落成 `dir/AGENTS.md` 的情况。
- **omp 默认编辑模式的目标此前识别不到**：默认的 hashline 模式把 `[AGENTS.md#…]` 文件头包在 `*** Begin Patch` 里，旧版当成 Codex 补丁解析，结果识别出零个目标；这是用 omp 18.13 实测发现的。现在会合并补丁头、hashline 文件头、`path` / `paths` 字段中的路径。shim 改为传完整的工具参数；没点名指令文件的 edit / write 不再启动 guard 进程。
- **guard 自身出错时不再放行**：解析异常等情况下，只要输入点名了指令文件就按拒绝处理，不再按非阻断错误放行。

## [0.1.0] - 2026-11-06

- 首个版本：PreToolUse 审批点，拦截对任意目录 `AGENTS.md` / `CLAUDE.md` 的修改（文件编辑工具 + 有写入迹象的 shell 命令）。
- Claude Code：`permissionDecision: "ask"` 走原生权限确认；omp：有 UI 时用 `ctx.ui.confirm`，无 UI 时拦截；Codex：PreToolUse 不支持 `ask`，拦截后由用户运行一次性 `approve` 命令放行（每文件一张、15 分钟过期、存于项目外的 XDG state 目录）。
- 模型自行执行 `approve`，或经编辑工具 / shell 写令牌目录，会被拦下。
- Python 以 `-I` 隔离模式运行，工作目录里的同名模块无法让 guard 失效。
- Codex `apply_patch` 按实测 payload（`tool_input.command` 补丁文本）解析 `Add/Update/Delete File` 与 `Move to` 目标。
